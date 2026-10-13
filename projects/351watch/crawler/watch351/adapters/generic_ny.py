"""Hand-curated town-website listings, with the extras New York town sites needed
(New York pilot, 2026-10). Everything the `generic` adapter accepts works here
too; these listing keys are added:

    "months": true            URL has {m} (or {mm}, {month} = "september") and {y}: expanded to every month the crawl
                              window touches (".../meeting-agendas?m={m}&y={y}")
    "skip_missing_months": true   with "months" or a {year} URL: a month or year page that does not exist
                              yet (HTTP error) is skipped, not fatal (the first page of the window must answer)
    "strip_query": true       drop the whole query string of document links
                              (per-page-load cache-busters: "?tmstv=1791675856", "?t=...")
    "compact_dates": true     when nothing else dates a link, read an 8-digit MMDDYYYY or
                              6-digit MMDDYY run in the file name ("a10082026pb_0.pdf",
                              "100526zbaagenda.pdf")
    "board_rules": [[regex, board, board_key], ...]
                              one listing page mixes several boards: the first rule whose
                              regex matches link text + href + row assigns the board;
                              links that match no rule are dropped; "board_rules_field": "href"
                              matches the rules against the href only (pages whose rows mix boards)
    "month_only": true        keep links dated only by "Month YYYY" ("September 2026.pdf")
                              when that month overlaps the window; meeting_date stays None
    "doc_href": regex         only links whose href matches (e.g. r"\\.pdf$")
    "scope": regex            only links inside the first <table>/<ul> that follows the first
                              heading-like element whose text matches (one page, one table per board)
    "assume_year": 2026       rows dated "January 12" with no year get this year; "url" = the year in the
                              listing page's URL (a {year} page); with month_only, a link named only by its
                              month ("September Agenda") is that month of this year
    "date_regex": regex       named groups y, m (number or month name), d: a site-specific date
                              format ("2026.10 October 13 Town Board Meeting Agenda.pdf")
    "posted_regex": regex     group 1 is a posted/document date shown in the row
                              ("document date 10-02-2026"); kept in AgendaDoc.extra["posted"]
    "follow_pages": true      each matching link is a notice or post page (WordPress public notices, posts):
                              the page is fetched (listing purpose, at most "follow_limit", default 8, per
                              listing); date_regex is tried on its text, then its heading is read for a date
                              (or, with month_only, a month); the page itself is the document, or with
                              "follow_doc": regex, the first link on the page whose href matches (a .docx or
                              .pdf attachment)
Revize "?t=YYYYMMDDhhmmss" upload stamps are kept in AgendaDoc.extra["uploaded"] before a
query string is stripped.

Meeting dates are parsed from link text, then href, then the surrounding row.
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import unquote

from ..dates import MONTHS, first_date
from ..models import AgendaDoc, Window
from .generic import _MORE, DEFAULT_EXCLUDE, GenericListingAdapter, _small_block

_COMPACT = re.compile(r"(?<!\d)(\d{2})(\d{2})(20\d{2}|\d{2})(?!\d)")
_MONTH_YEAR = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(20\d{2})\b", re.I)


def _compact_date(s: str) -> date | None:
    name = s.rsplit("/", 1)[-1]
    for m in _COMPACT.finditer(name):
        mm, dd, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yy < 100:
            yy += 2000
        try:
            d = date(yy, mm, dd)
        except ValueError:
            continue
        if 2020 <= d.year <= 2030:
            return d
    return None


def _month_overlaps(s: str, window: Window) -> bool:
    m = _MONTH_YEAR.search(s)
    if not m:
        return False
    y, mo = int(m.group(2)), MONTHS[m.group(1)[:3].lower()]
    first = date(y, mo, 1)
    last = date(y + (mo == 12), mo % 12 + 1, 1)
    return first <= window.end and last > window.start


_REVIZE_T = re.compile(r"[?&]t=(20\d{12})")
_MONTH_NAME = re.compile(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b", re.I)
_MONTH_DAY = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})\b", re.I)


def _regex_date(rx: re.Pattern, s: str) -> date | None:
    m = rx.search(s)
    if not m:
        return None
    g = m.groupdict()
    mon = g["m"]
    mon = int(mon) if mon.isdigit() else MONTHS.get(mon[:3].lower())
    try:
        return date(int(g["y"]) + (2000 if int(g["y"]) < 100 else 0), mon, int(g["d"]))
    except (TypeError, ValueError):
        return None


class GenericNYAdapter(GenericListingAdapter):
    platform = "generic_ny"

    @staticmethod
    def _expand_months(url: str, window: Window) -> list[str]:
        out, y, m = [], window.start.year, window.start.month
        while (y, m) <= (window.end.year, window.end.month):
            out.append(url.replace("{m}", str(m)).replace("{mm}", f"{m:02d}").replace("{y}", str(y))
                       .replace("{month}", date(y, m, 1).strftime("%B").lower()))   # "september_2026" folders
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        return out

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        docs: dict[str, AgendaDoc] = {}
        for listing in cfg.get("listings", []):
            urls = self._expand_months(listing["url"], window) if listing.get("months") else \
                self._expand(listing["url"], window)
            for i, url in enumerate(urls):
                try:
                    found = self._parse_ny(cfg, listing, url, window)
                except RuntimeError:
                    # "skip_missing_months": a month folder the site has not created yet (HTTP 4xx/5xx)
                    # is skipped instead of failing the listing; the first month must still answer
                    if listing.get("skip_missing_months") and i > 0:
                        continue
                    raise
                for doc in found:
                    docs.setdefault(doc.url, doc)
        return list(docs.values())

    def _parse_ny(self, cfg: dict, listing: dict, url: str, window: Window) -> list[AgendaDoc]:
        resp = self.get_listing(url)
        if not resp.ok:
            raise RuntimeError(f"listing {url} returned HTTP {resp.status}")
        include = re.compile(listing.get("link_pattern", "agenda"), re.I)
        exclude = re.compile(listing.get("exclude_pattern", DEFAULT_EXCLUDE), re.I)
        board_rx = re.compile(listing["board_pattern"], re.I) if listing.get("board_pattern") else None
        board_ex = re.compile(listing["board_exclude"], re.I) if listing.get("board_exclude") else None
        doc_href = re.compile(listing["doc_href"], re.I) if listing.get("doc_href") else None
        rules = [(re.compile(rx, re.I), b, k) for rx, b, k in listing.get("board_rules", [])]
        date_rx = re.compile(listing["date_regex"], re.I) if listing.get("date_regex") else None
        posted_rx = re.compile(listing["posted_regex"], re.I) if listing.get("posted_regex") else None
        year_hint = listing.get("assume_year")
        if year_hint == "url":
            ym = re.search(r"(?<!\d)(20\d\d)(?!\d)", url)
            year_hint = int(ym.group(1)) if ym else None
        soup = self.soup(resp)
        base_tag = soup.find("base", href=True)
        base = self.abs_url(resp.final_url, base_tag["href"]) if base_tag else resp.final_url
        root = soup
        if listing.get("scope"):
            scope_rx = re.compile(listing["scope"], re.I)
            head = next((el for el in soup.find_all(["h1", "h2", "h3", "h4", "h5", "strong", "b", "p", "span"])
                         if scope_rx.search(" ".join(el.get_text(" ", strip=True).split()))), None)
            root = head.find_next(["table", "ul"]) if head else None
            if root is None:
                return []
        out, followed = [], set()
        for a in root.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            text = " ".join(a.get_text(" ", strip=True).split()) or (a.get("title") or a.get("aria-label") or "")
            hay = f"{text} {href}"
            if not include.search(hay) or exclude.search(text) or _MORE.match(text):
                continue
            if doc_href and not doc_href.search(href):
                continue
            container = a.find_parent(["tr", "li"])
            if container is None and listing.get("context") == "block":
                container = _small_block(a)
            row_text = " ".join(container.get_text(" ", strip=True).split()) if container else ""
            if board_rx and not board_rx.search(f"{hay} {row_text}"):
                continue
            if board_ex and board_ex.search(f"{text} {row_text}"):
                continue
            board, board_key = listing["board"], listing["board_key"]
            if rules:
                target = href if listing.get("board_rules_field") == "href" else f"{hay} {row_text}"
                hit = next(((b, k) for rx, b, k in rules if rx.search(target)), None)
                if hit is None:
                    continue
                board, board_key = hit
            doc_url = self.abs_url(base, href)
            page_title = page_text = ""
            if listing.get("follow_pages"):
                # a link that dates itself outside the window is not followed
                pre = (_regex_date(date_rx, f"{text} {href}") if date_rx else None) or first_date(text, href)
                if pre is not None and pre not in window:
                    continue
                if doc_url in followed or len(followed) >= int(listing.get("follow_limit", 8)):
                    continue
                followed.add(doc_url)
                page = self._follow(listing, doc_url)
                if page is None:
                    continue
                doc_url, page_title, page_text = page
                if exclude.search(page_title):
                    continue
            when = _regex_date(date_rx, f"{text} {href}") if date_rx else None
            if when is None and date_rx and page_text:
                when = _regex_date(date_rx, page_text)
            when = when or first_date(text, href, row_text) or (first_date(page_title) if page_title else None)
            if when is None and year_hint:
                m = _MONTH_DAY.search(f"{text} {row_text}")
                if m:
                    try:
                        when = date(int(year_hint), MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
                    except ValueError:
                        when = None
            if when is None and listing.get("compact_dates"):
                when = _compact_date(href.split("?")[0])
            if when not in window:
                named = _MONTH_NAME.search(text) if year_hint else None
                if not (when is None and listing.get("month_only")
                        and (_month_overlaps(f"{text} {unquote(href)} {page_title}", window)
                             or (named and _month_overlaps(f"{named.group(0)} {year_hint}", window)))):
                    continue
            extra = {}
            m = _REVIZE_T.search(doc_url)
            if m:
                extra["uploaded"] = m.group(1)
            if posted_rx:
                pm = posted_rx.search(row_text)
                if pm:
                    extra["posted"] = pm.group(1)
            if listing.get("strip_query"):
                doc_url = doc_url.split("?")[0]
            out.append(AgendaDoc(
                town=cfg["town"], board=board, board_key=board_key, meeting_date=when,
                title=page_title or text or row_text[:120], url=doc_url, listing_url=url,
                resolve_pdf=bool(listing.get("resolve_pdf")), extra=extra,
            ))
        return out

    def _follow(self, listing: dict, url: str) -> tuple[str, str, str] | None:
        """"follow_pages": read one notice or post page -> (document url, heading, page text)."""
        resp = self.get_listing(url)
        if not resp.ok:
            return None
        soup = self.soup(resp)
        head = soup.find("h1") or soup.title
        title = " ".join(head.get_text(" ", strip=True).split())[:200] if head else ""
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ", strip=True).split())
        target = resp.final_url
        if listing.get("follow_doc"):
            rx = re.compile(listing["follow_doc"], re.I)
            a = next((a for a in soup.find_all("a", href=True) if rx.search(a["href"])), None)
            if a is None:
                return None
            target = self.abs_url(resp.final_url, a["href"])
        return target, title, text
