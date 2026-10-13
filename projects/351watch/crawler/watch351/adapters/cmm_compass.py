"""Compass Web Development "CMM" meeting-document embeds (cmm.compassweb.dev/embeds/<site>/agendas), the
agenda tables that small New York towns' Weebly sites show in an iframe (Wave 1, 2026-10: Clymer,
Ellery, Angelica). The embed is plain server HTML: one table row per document with its title, date
(MM/DD/YYYY) and a download link (/files/<uuid>/view). robots.txt allows everything.

Listing keys:

    {"platform": "cmm_compass", "url": "https://cmm.compassweb.dev/embeds/80/agendas",
     "board": "Town Board", "board_key": "select_board",
     "board_rules": [[regex, board, board_key], ...]   # optional: a row whose title matches is that board's
    }

The embed shows the current year; when the crawl window reaches into another year, that year's table
is read with the embed's own year selector (?year=YYYY, a GET form).
"""

from __future__ import annotations

import re
from datetime import datetime

from ..dates import parse_date
from ..models import AgendaDoc, Window
from .base import Adapter

_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b")
_TITLE_DATE = re.compile(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d\d\b|"
                         r"\b\d{1,2}/\d{1,2}/20\d\d\b", re.I)


class CMMCompassAdapter(Adapter):
    platform = "cmm_compass"

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        out: dict[str, AgendaDoc] = {}
        for listing in cfg.get("listings", []):
            years = sorted({window.start.year, window.end.year})
            base = listing["url"].split("?")[0]
            for i, y in enumerate(years):
                url = base if y == datetime.now().year else f"{base}?year={y}"
                resp = self.get_listing(url)
                if not resp.ok:
                    if i == 0 and y == datetime.now().year:
                        raise RuntimeError(f"listing {url} returned HTTP {resp.status}")
                    continue
                for doc in self._rows(cfg, listing, resp, window):
                    out.setdefault(doc.url, doc)
        return list(out.values())

    def _rows(self, cfg: dict, listing: dict, resp, window: Window) -> list[AgendaDoc]:
        rules = [(re.compile(rx, re.I), b, k) for rx, b, k in listing.get("board_rules", [])]
        docs = []
        for tr in self.soup(resp).find_all("tr"):
            a = tr.find("a", href=True)
            tds = tr.find_all("td")
            if a is None or len(tds) < 2:
                continue
            title = " ".join(tds[0].get_text(" ", strip=True).split())
            m = _DATE.search(tds[1].get_text(" ", strip=True)) or _DATE.search(title)
            if not m:
                continue
            try:
                posted = datetime(int(m.group(3)), int(m.group(1)), int(m.group(2))).date()
            except ValueError:
                continue
            # the table's date is the upload date; a full meeting date in the title wins
            # ("Proposed Agenda for October 12, 2026 Regular Town Board Meeting", posted 10/09/2026)
            t = _TITLE_DATE.search(title)
            d = parse_date(t.group(0)) if t else None
            d = d or posted
            if d not in window or re.search(r"\bminutes\b", title, re.I):
                continue
            board, key = listing["board"], listing["board_key"]
            for rx, b, k in rules:
                if rx.search(title):
                    board, key = b, k
                    break
            docs.append(AgendaDoc(town=cfg["town"], board=board, board_key=key, meeting_date=d,
                                  title=title[:200], url=self.abs_url(resp.final_url, a["href"]),
                                  listing_url=listing["url"], extra={"kind": "agenda", "posted": posted.isoformat()}))
        return docs
