"""General agenda-page reader for ordinary municipal sites: WordPress, Revize, CivicPlus
document pages (DocumentCenter / Archive Center), Municode Meetings, Drupal and plain
"Agendas & Minutes" pages. Unlike `generic`, it needs no per-site link regex: it reads
every document-like link on the page and decides for each one

* what it is: agenda, packet, notice, minutes, media (from the link text, the file name,
  the table column header, the nearest heading, then the page title), keeping agendas,
  packets and hearing notices and dropping minutes, recordings and cancellations;
* its meeting date: link text, then file name (incl. compact 10142026 / 101426 forms),
  then the surrounding row / list item / small block, then the nearest date heading;
  a year-less "October 14" takes the year from the heading, URL or folder;
* its board: a single-board page owns all its links (links naming another tracked board
  are dropped via `board_exclude`); on a shared page `board_pattern` must match the
  link, its row or its heading.

Documents dated outside the crawl window are skipped. Year folders ("2026 Agendas") are
followed one level. Every request goes through PoliteFetcher (`Adapter.get_listing`).

Listing keys (towns_*.json), all optional except board / board_key / url:

    {"board": "Planning Commission", "board_key": "planning_board", "platform": "agenda_page",
     "url": "https://twp.example/planning-commission/",   # {year} expands to window years
     "board_pattern": "planning",          # shared page: keep links whose text/row/heading match
     "board_exclude": "zoning board|ZBA",  # drop links whose text/row/heading match
     "unlabeled": true,                    # keep dated documents with no agenda/minutes label
                                           #   (a page that holds agendas only)
     "follow": true,                       # follow year-folder links one level (default true)
     "resolve_pdf": false}

Extras recorded on each AgendaDoc for lead-time analysis: kind, uploaded (Revize ?t=
stamp), uploaded_month (WordPress /uploads/YYYY/MM/), posted (a "Posted ..." date in the row).
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from urllib.parse import unquote, urljoin, urlsplit

from ..dates import MONTHS, first_date, parse_date
from ..models import AgendaDoc, Window
from .base import Adapter
from .generic import strip_doc_query

# links that point at a document (or an HTML agenda view) rather than a page of the site
DOC_HREF = re.compile(
    r"\.(?:pdf|docx?|rtf|txt)(?:$|[?#])|/DocumentCenter/View/|Archive\.aspx\?ADID=|ViewFile/|/download|"
    r"[?&/]download\b|/getfile|/viewfile|/fileviewer|FileStream\.ashx|/showdocument|/showpublisheddocument|"
    r"/dbfiles/|contentfiledata|/boardmeetingagenda/|/wp-content/uploads/|/sites/default/files/|"
    r"/files/[^/]+\.\w{2,4}$|/uploads/|/Document(?:s)?/\d|/media/\d|/d/\d+/|cms\d+\.revize\.com|"
    r"/AgendaCenter/ViewFile|/Archive/|/assets/\d+|/fs/resource-manager/view/|/ArchiveCenter/ViewFile|"
    r"/files/[a-z0-9_-]+/?$", re.I)
MEDIA = re.compile(r"\.(?:mp3|mp4|m4a|wav|mov|wmv|jpg|jpeg|png|gif)(?:$|\?)|youtube\.|youtu\.be|vimeo\.|zoom\.us|"
                   r"swagit|granicus\.com/MediaPlayer|facebook\.com|/video|/audio|livestream", re.I)
NOT_DOC = re.compile(r"^(?:mailto|tel|javascript):|/calendar|/event|/news|/blog|/search|login|signin|/security/|"
                     r"/subscribe|"
                     r"/form|/ical|\.ics\b|google\.com/calendar|/rss|/feed\b|translate\.", re.I)

MINUTES = re.compile(r"\bminutes?\b|\bmins\b|\bminu?tes\b|synopsis|summary of (?:actions?|proceedings)|"
                     r"action summary|actions? taken|\brecap\b|\bjournal\b|approved\s+minutes", re.I)
PACKET = re.compile(r"packet|board\s*book|agenda\s*book|full\s+agenda|supporting\s+(?:docs?|documents?|materials?)|"
                    r"back-?up|attachments?|staff\s+reports?|meeting\s+materials|info(?:rmation)?\s+packet|"
                    r"\bpkt\b", re.I)
AGENDA = re.compile(r"agenda|\bagnd\b", re.I)
NOTICE = re.compile(r"public\s+hearing|hearing\s+notice|notice\s+of\s+(?:public\s+)?(?:hearing|meeting)|"
                    r"legal\s+(?:ad|notice)|meeting\s+notice|notice\b", re.I)
CANCEL = re.compile(r"cancel+(?:ed|ation)|postpone", re.I)
OTHER_DOC = re.compile(r"\b(?:schedule|calendar|by-?laws|rules\s+of\s+procedure|application|form|fee|budget|"
                       r"annual\s+report|roster|members?hip|map|plan\s+document|ordinance\s+book|newsletter|"
                       r"audit|policy)\b", re.I)
_MEETINGISH = re.compile(r"meeting|session|hearing|regular|special|workshop|work\s+session", re.I)
_YEAR = re.compile(r"\b(20\d\d)\b")
_MONTH_DAY = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b",
                        re.I)
_COMPACT8 = re.compile(r"(?<!\d)(\d{2})(\d{2})(20\d{2})(?!\d)")          # 10142026
_COMPACT8_YMD = re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)")      # 20261014
_COMPACT6 = re.compile(r"(?<!\d)(\d{2})(\d{2})(2[4-8])(?!\d)")           # 101426
_POSTED = re.compile(r"(?:posted|uploaded|published|added)(?:\s+on)?\s*:?\s*"
                     r"((?:[A-Za-z]{3,9}\.?\s+\d{1,2},?\s+20\d\d|\d{1,2}/\d{1,2}/(?:20)?\d\d)(?:\s+\d{1,2}:\d{2}\s*[AP]M)?)",
                     re.I)
_REVIZE_T = re.compile(r"[?&]t=(20\d{12})")
_WP_UPLOAD = re.compile(r"/(?:wp-content/)?uploads/(20\d\d)/(\d\d)/", re.I)
_HEADINGS = ["h1", "h2", "h3", "h4", "h5", "h6", "summary", "dt", "caption", "legend"]
_ACCORDION = re.compile(r"accordion|toggle|collapse|panel-heading|tab-title|card-header|fl-accordion-button", re.I)
MAX_DOCS_PER_PAGE = 60
MAX_MEETING_PAGES = 8
MAX_DOC_DATING = 6          # undated documents fetched per page to read their meeting date
# link text that starts with a date: "October 14, 2026 - Regular Meeting", "Tue, 10/14/26"
_DATE_FIRST = re.compile(r"\W*(?:[A-Za-z]+day,?\s+)?(?:[A-Za-z]{3,9}\.?\s+\d|\d{1,2}[/.-]\d)")


def _norm(s: str | None) -> str:
    return " ".join((s or "").split())


def filename_of(href: str) -> str:
    parts = urlsplit(href)
    dn = re.search(r"(?:^|&)dn=([^&]+)", parts.query)   # Wix file links: ...docx?dn=Agenda%201.26.26.docx
    name = unquote(dn.group(1)) if dn else unquote(parts.path.rstrip("/").rsplit("/", 1)[-1])
    return re.sub(r"[_+]", " ", name)


_GLUED = re.compile(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?[\s_-]*(\d{1,2})(?:st|nd|rd|th)?"
                    r"[\s_,-]*(20\d\d)(?!\d)", re.I)
_MONTH_WORD = re.compile(r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*", re.I)


def compact_date(s: str) -> date | None:
    """'botagendamarch122026' (month name glued to day and year), else 10142026, 20261014 or 101426.
    A six-digit run is not read when the name has a month word ('march122026' is not Dec 20)."""
    m = _GLUED.search(s)
    if m:
        try:
            return date(int(m.group(3)), MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
        except ValueError:
            pass
    rxs = ((_COMPACT8, "mdy"), (_COMPACT8_YMD, "ymd")) + (() if _MONTH_WORD.search(s) else ((_COMPACT6, "mdy"),))
    for rx, order in rxs:
        for m in rx.finditer(s):
            a, b, c = (int(x) for x in m.groups())
            y, mo, d = (a, b, c) if order == "ymd" else (c + (2000 if c < 100 else 0), a, b)
            try:
                dt = date(y, mo, d)
            except ValueError:
                continue
            if 2020 <= dt.year <= 2030:
                return dt
    return None


_MONTH_YEAR = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?[\s_\-]+"
                         r"(?:[A-Za-z]+[\s_\-]+){0,2}?(20\d\d)\b", re.I)


def _month_only(s: str, window: Window) -> str | None:
    """'YYYY-MM' when `s` names only a month and year inside the window's months."""
    m = _MONTH_YEAR.search(s)
    if not m:
        return None
    y, mo = int(m.group(2)), MONTHS[m.group(1)[:3].lower()]
    first = date(y, mo, 1)
    nxt = date(y + (mo == 12), mo % 12 + 1, 1)
    if first <= window.end and nxt > window.start:
        return f"{y}-{mo:02d}"
    return None


def _yearless(s: str, year_hint: int | None) -> date | None:
    if not year_hint:
        return None
    m = _MONTH_DAY.search(s)
    if not m:
        return None
    try:
        return date(year_hint, MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
    except ValueError:
        return None


def _small_container(a, limit: int = 320):
    """The link's row: <tr>/<li>, else the largest small block around it."""
    c = a.find_parent(["tr", "li"])
    if c is not None and len(c.get_text(" ", strip=True)) <= 600:
        return c
    best = None
    for parent in a.parents:
        if parent.name in ("body", "html"):
            break
        if len(parent.get_text(" ", strip=True)) > limit:
            break
        if parent.name in ("div", "p", "td", "article", "section", "dd", "span", "figure"):
            best = parent
    return best


def _column_header(a) -> str:
    td = a.find_parent(["td", "th"])
    if td is None or td.parent is None:
        return ""
    cells = td.parent.find_all(["td", "th"], recursive=False)
    try:
        idx = cells.index(td)
    except ValueError:
        return ""
    table = td.find_parent("table")
    if table is None:
        return ""
    head = table.find("thead")
    hrow = head.find("tr") if head else table.find("tr")
    if hrow is None or hrow is td.parent:
        return ""
    hcells = hrow.find_all(["th", "td"], recursive=False)
    return _norm(hcells[idx].get_text(" ", strip=True))[:60] if idx < len(hcells) else ""


class _Headings:
    """Nearest preceding heading-like element for any tag on a page (h1-h6, summary, dt,
    caption, or an accordion/tab title), via one pass over the document."""

    def __init__(self, soup):
        els = soup.find_all(True)
        self.pos = {id(e): i for i, e in enumerate(els)}
        self.heads: list[tuple[int, str]] = []
        for i, e in enumerate(els):
            if e.name in _HEADINGS or (e.name in ("button", "div", "a", "span", "p", "strong", "b")
                                       and _ACCORDION.search(" ".join(e.get("class", []) or []) + " " + (e.get("id") or ""))):
                t = _norm(e.get_text(" ", strip=True))
                if t and len(t) < 160:
                    self.heads.append((i, t))
        self._keys = [i for i, _ in self.heads]

    def before(self, tag) -> str:
        import bisect
        i = self.pos.get(id(tag))
        if i is None:
            return ""
        k = bisect.bisect_left(self._keys, i) - 1
        return self.heads[k][1] if k >= 0 else ""


def doc_kind(*labels: str) -> str:
    """First decisive label wins: minutes / packet / agenda / notice / cancel."""
    for lab in labels:
        if not lab:
            continue
        if CANCEL.search(lab) and not AGENDA.search(lab):
            return "cancel"
        if MINUTES.search(lab) and not AGENDA.search(lab):
            return "minutes"
        if PACKET.search(lab):
            return "packet"
        if AGENDA.search(lab):
            return "agenda"
        if MINUTES.search(lab):
            return "minutes"
        if NOTICE.search(lab):
            return "notice"
    return "unknown"


class AgendaPageAdapter(Adapter):
    platform = "agenda_page"

    def discover(self, cfg: dict) -> list[dict]:
        # Listings are found by watch351.discover_sites (site-level probing); kept as-is here.
        return cfg.get("listings", [])

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        docs: dict[str, AgendaDoc] = {}
        for listing in cfg.get("listings", []):
            for url in self.expand(listing["url"], window):
                for doc in self.page_docs(cfg, listing, url, window):
                    docs.setdefault(doc.url, doc)
        return list(docs.values())

    def date_in_document(self, url: str) -> date | None:
        """Meeting date read from an undated agenda / hearing notice itself (listing option
        `date_from_document`): a date introduced by meeting / hearing / held words, else the first
        date in the opening text. The document is fetched once and cached like any agenda."""
        from ..extract import extract
        from ..fetch import FetchError
        try:
            resp = self.fetcher.get(url)
        except FetchError:
            return None
        if not resp.ok:
            return None
        text = _norm(extract(resp).text)[:3000]
        rx = r"[A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d\d|\d{1,2}/\d{1,2}/20\d\d"
        for m in re.finditer(r"(?:meeting|hearing|held|scheduled|convene|session)\D{0,60}?(" + rx + ")", text, re.I):
            d = parse_date(m.group(1))
            if d:
                return d
        m = re.search(rx, text)
        return parse_date(m.group(0)) if m else None

    @staticmethod
    def expand(url: str, window: Window) -> list[str]:
        if "{year}" not in url:
            return [url]
        return [url.replace("{year}", str(y)) for y in range(window.start.year, window.end.year + 1)]

    # ------------------------------------------------------------------ pages
    def page_docs(self, cfg: dict, listing: dict, url: str, window: Window, depth: int = 0,
                  seen_pages: set | None = None, date_hint: date | None = None,
                  skip_urls: set | None = None) -> list[AgendaDoc]:
        """Documents on one listing page. `date_hint`: the page is one meeting's page (reached from a
        dated link on the listing); its documents take that meeting date."""
        seen_pages = seen_pages if seen_pages is not None else set()
        if url in seen_pages:
            return []
        seen_pages.add(url)
        if date_hint is not None and date_hint < date.today() - timedelta(days=7):
            resp = self.fetcher.get(url, max_age=7 * 24 * 3600)   # a past meeting's page rarely changes
        else:
            resp = self.get_listing(url)
        if not resp.ok:
            raise RuntimeError(f"listing {url} returned HTTP {resp.status}")
        if resp.is_pdf:
            return []
        soup = self.soup(resp)
        refresh = soup.find("meta", attrs={"http-equiv": re.compile("refresh", re.I)})
        if refresh and depth < 2:
            m = re.search(r"url\s*=\s*['\"]?([^'\";]+)", refresh.get("content", ""), re.I)
            if m:
                return self.page_docs(cfg, listing, urljoin(resp.final_url, m.group(1).strip()), window,
                                      depth + 1, seen_pages)
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        base_tag = soup.find("base", href=True)
        base = urljoin(resp.final_url, base_tag["href"]) if base_tag else resp.final_url
        title = _norm(soup.title.get_text(" ", strip=True) if soup.title else "")
        h1 = soup.find("h1")
        page_label = f"{title} {_norm(h1.get_text(' ', strip=True)) if h1 else ''}"
        page_kind = doc_kind(page_label) if not re.search(r"agenda.{0,20}minutes|minutes.{0,20}agenda",
                                                          page_label, re.I) else "unknown"
        page_year = None
        ym = _YEAR.search(f"{page_label} {url}")
        if ym:
            page_year = int(ym.group(1))
        board_rx = re.compile(listing["board_pattern"], re.I) if listing.get("board_pattern") else None
        board_ex = re.compile(listing["board_exclude"], re.I) if listing.get("board_exclude") else None
        unlabeled_ok = bool(listing.get("unlabeled")) or page_kind == "agenda" or date_hint is not None
        if date_hint is not None:
            board_rx = board_ex = None   # the link to this meeting page was already matched to the board
        headings = _Headings(soup)

        out: list[AgendaDoc] = []
        year_links = []
        meeting_links: list[tuple[str, date]] = []
        page_urls: set[str] = set()
        n_doc_links = 0
        n_doc_dated = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#") or NOT_DOC.search(href):
                continue
            abs_url = urljoin(base, href)
            if not abs_url.startswith("http"):
                continue
            page_urls.add(abs_url)
            text = _norm(a.get_text(" ", strip=True)) or _norm(a.get("title") or a.get("aria-label") or "")
            fname = filename_of(abs_url)
            fwords = fname.replace("-", " ")   # "REGULAR-BOARD-MEETING-AGENDA-September-21-2026" -> words
            is_doc = bool(DOC_HREF.search(abs_url))
            n_doc_links += is_doc
            if not is_doc:
                # a dated "Agenda"/"Packet" link to an HTML page is the agenda itself (Genoa, Drupal nodes)
                if re.fullmatch(r"(?:view\s+)?(?:agenda|packet|agenda\s+packet)(?:\s*\(html\))?", text, re.I):
                    is_doc = True
                else:
                    if (depth == 0 and listing.get("follow", True) and _YEAR.search(text) and len(text) < 60
                            and urlsplit(abs_url).netloc == urlsplit(resp.final_url).netloc
                            and not MINUTES.search(text) and not _MONTH_DAY.search(text)):
                        y = int(_YEAR.search(text).group(1))
                        if window.start.year <= y <= window.end.year and \
                                re.search(r"agenda|meeting|packet|^\s*20\d\d\s*$|archive|documents", text, re.I):
                            year_links.append(abs_url)
                    # a dated link to a page of the same site: one meeting's page (Revize, CivicLive)
                    elif (depth <= 1 and date_hint is None and listing.get("follow", True) and len(text) <= 80
                          and urlsplit(abs_url).netloc == urlsplit(resp.final_url).netloc
                          and not MINUTES.search(text) and not MEDIA.search(abs_url)):
                        d = parse_date(text)
                        if d is not None and d in window and _DATE_FIRST.match(text):
                            mrow = _small_container(a)
                            mctx = (f"{text} {_norm(mrow.get_text(' ', strip=True)) if mrow is not None else ''} "
                                    f"{headings.before(a)}")
                            if (not board_rx or board_rx.search(mctx)) and not (board_ex and board_ex.search(text)):
                                meeting_links.append((abs_url, d))
                    continue
            if MEDIA.search(abs_url) or re.search(r"\b(?:video|audio|recording|youtube|listen|watch)\b", text, re.I):
                continue
            container = _small_container(a)
            row = _norm(container.get_text(" ", strip=True)) if container is not None else ""
            col = _column_header(a)
            head = headings.before(a)
            kind = doc_kind(text, fname, col)
            if kind == "unknown" and row and len(row) <= 200:
                kind = doc_kind(row) if not re.search(r"agenda.{0,40}minutes|minutes.{0,40}agenda", row, re.I) \
                    else "unknown"
            if kind == "unknown":
                kind = doc_kind(head) if head and not re.search(r"agenda.{0,30}minutes|minutes.{0,30}agenda",
                                                                 head, re.I) else "unknown"
            if kind == "unknown" and page_kind in ("agenda", "minutes", "packet"):
                kind = page_kind
            if kind in ("minutes", "cancel", "media"):
                continue
            if date_hint is not None and abs_url in (skip_urls or ()):
                continue   # sidebar / navigation document also linked from the listing page
            if kind == "unknown":
                if not unlabeled_ok or OTHER_DOC.search(text):
                    continue
                if date_hint is None and not (parse_date(text) or _MEETINGISH.search(text) or compact_date(fname)
                                              or parse_date(fname)):
                    continue
            if kind == "notice" and OTHER_DOC.search(text) and not NOTICE.search(text):
                continue
            ctx = f"{text} {fwords} {row if len(row) <= 400 else ''} {head}"
            if board_rx and not board_rx.search(ctx):
                continue
            if board_ex and board_ex.search(f"{text} {fwords} {row if len(row) <= 250 else ''}"):
                continue
            raw_name = unquote(urlsplit(abs_url).path.rstrip("/").rsplit("/", 1)[-1])   # "Agenda_5_20_26.pdf"
            when = date_hint or (first_date(text) or first_date(fname) or first_date(raw_name)
                                 or first_date(fwords) or compact_date(fname)
                                 or (first_date(row) if len(row) <= 400 else None) or first_date(head))
            if when is None:
                hint = None
                for s in (text, fname, head, abs_url):
                    ym = _YEAR.search(s or "")
                    if ym:
                        hint = int(ym.group(1))
                        break
                hint = hint or page_year
                when = _yearless(text, hint) or _yearless(row, hint) or _yearless(head, hint)
            if when is None and listing.get("date_from_document") and kind in ("agenda", "packet", "notice") \
                    and n_doc_dated < MAX_DOC_DATING:
                n_doc_dated += 1
                when = self.date_in_document(abs_url)
            month = None
            if when is None and kind in ("agenda", "packet") and not listing.get("no_month_only"):
                # "October — Agenda" / "October-Agenda-2026.pdf": the month is all the site gives
                month = _month_only(f"{text} {fwords} {head}", window)
            if when not in window and month is None:
                continue
            extra = {"kind": kind}
            if month:
                extra["month"] = month
            m = _REVIZE_T.search(abs_url)
            if m:
                extra["uploaded"] = m.group(1)
            m = _WP_UPLOAD.search(abs_url)
            if m:
                extra["uploaded_month"] = f"{m.group(1)}-{m.group(2)}"
            m = _POSTED.search(row)
            if m:
                extra["posted"] = m.group(1)
            doc_url = strip_doc_query(abs_url) if "uploaded" in extra or "revize" in abs_url else abs_url
            title_txt = text if text and not re.fullmatch(r"(?:view|download|pdf|here|click here|open)", text, re.I) \
                else (fname or row[:120])
            out.append(AgendaDoc(
                town=cfg["town"], board=listing["board"], board_key=listing["board_key"], meeting_date=when,
                title=title_txt[:200], url=doc_url, listing_url=url,
                resolve_pdf=bool(listing.get("resolve_pdf")), extra=extra))
            if len(out) >= MAX_DOCS_PER_PAGE:
                break
        if depth == 0:
            for y_url in list(dict.fromkeys(year_links))[:3]:
                try:
                    out.extend(self.page_docs(cfg, listing, y_url, window, depth + 1, seen_pages))
                except RuntimeError:
                    continue
        # A page that is itself the agenda ("Upcoming Meeting Agenda" in HTML, no document links): read
        # the page, keyed by meeting date (#meeting-YYYY-MM-DD) so each new agenda is a new document.
        if (not out and not n_doc_links and page_kind == "agenda" and date_hint is None
                and listing.get("self_page", True)):
            main = soup.find("main") or soup.find(id=re.compile("content|main", re.I)) or soup.body or soup
            body_text = _norm(main.get_text(" ", strip=True))[:4000]
            d = next((d for d in (parse_date(m.group(0)) for m in re.finditer(
                r"[A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d\d|\d{1,2}/\d{1,2}/20\d\d", body_text))
                      if d is not None), None)
            if d is not None and d in window and re.search(r"\bagenda\b", body_text, re.I):
                out.append(AgendaDoc(
                    town=cfg["town"], board=listing["board"], board_key=listing["board_key"], meeting_date=d,
                    title=(title or "Agenda")[:200], url=f"{resp.final_url.split('#')[0]}#meeting-{d.isoformat()}",
                    listing_url=url, extra={"kind": "agenda", "self_page": True}))
        # meeting pages: the nearest meetings first (upcoming, then most recent), at most a few
        today = date.today()
        uniq = dict(meeting_links)
        for m_url, d in sorted(uniq.items(), key=lambda x: abs((x[1] - today).days))[:MAX_MEETING_PAGES]:
            try:
                out.extend(self.page_docs(cfg, listing, m_url, window, depth + 1, seen_pages, date_hint=d,
                                          skip_urls=page_urls))
            except (RuntimeError, ValueError):
                continue
        return out
