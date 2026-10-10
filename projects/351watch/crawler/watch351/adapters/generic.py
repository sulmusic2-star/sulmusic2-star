"""Plain town-website agenda listings (Revize, WordPress, legacy ASP...).

Any page that lists agenda links can be handled with configuration alone.
Per listing in towns.json:

    {
      "board": "Planning Board", "board_key": "planning_board",
      "url": "https://town.example/planning/agendas?year={year}",
      "link_pattern":    "agenda",               # regex on link text OR href
      "exclude_pattern": "minutes|supporting",   # optional
      "resolve_pdf": false,                      # link goes to an HTML page that links the PDF
      "accept_undated_if": "warrant.*2026"       # optional: keep links with no parseable date
    }

`{year}` in the URL is expanded to each calendar year the crawl window touches.
The meeting date is parsed from the link text, then the href, then the
surrounding table row / list item.
"""

from __future__ import annotations

import re

from ..dates import first_date
from ..models import AgendaDoc, Window
from .base import Adapter

DEFAULT_EXCLUDE = r"minutes|supporting materials|summary|video|recording"
_MORE = re.compile(r"^(more|read more|view more|details?)\b", re.I)


class GenericListingAdapter(Adapter):
    platform = "generic"

    def discover(self, cfg: dict) -> list[dict]:
        # Generic sites have no machine-readable board index; listings are
        # curated by hand in towns.json and simply kept as-is.
        return cfg.get("listings", [])

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        docs: dict[str, AgendaDoc] = {}
        for listing in cfg.get("listings", []):
            for url in self._expand(listing["url"], window):
                for doc in self._parse_listing(cfg, listing, url, window):
                    docs.setdefault(doc.url, doc)
        return list(docs.values())

    @staticmethod
    def _expand(url: str, window: Window) -> list[str]:
        if "{year}" not in url:
            return [url]
        return [url.replace("{year}", str(y)) for y in range(window.start.year, window.end.year + 1)]

    def _parse_listing(self, cfg: dict, listing: dict, url: str, window: Window) -> list[AgendaDoc]:
        resp = self.get_listing(url)
        if not resp.ok:
            raise RuntimeError(f"listing {url} returned HTTP {resp.status}")
        include = re.compile(listing.get("link_pattern", "agenda"), re.I)
        exclude = re.compile(listing.get("exclude_pattern", DEFAULT_EXCLUDE), re.I)
        undated = listing.get("accept_undated_if")
        undated_rx = re.compile(undated, re.I) if undated else None
        soup = self.soup(resp)
        base_tag = soup.find("base", href=True)
        base = self.abs_url(resp.final_url, base_tag["href"]) if base_tag else resp.final_url
        out = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith(("#", "javascript:", "mailto:")):
                continue
            text = " ".join(a.get_text(" ", strip=True).split())
            hay = f"{text} {href}"
            if not include.search(hay) or exclude.search(text) or _MORE.match(text):
                continue
            container = a.find_parent(["tr", "li"])
            row_text = " ".join(container.get_text(" ", strip=True).split()) if container else ""
            when = first_date(text, href, row_text)
            if when not in window:
                if not (when is None and undated_rx and undated_rx.search(hay)):
                    continue
            out.append(AgendaDoc(
                town=cfg["town"], board=listing["board"], board_key=listing["board_key"],
                meeting_date=when, title=text or row_text[:120],
                url=self.abs_url(base, href), listing_url=url,
                resolve_pdf=bool(listing.get("resolve_pdf")),
            ))
        return out
