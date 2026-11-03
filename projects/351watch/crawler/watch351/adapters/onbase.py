"""Hyland OnBase "Agenda Online" portals (VA/MD wave, 2026-11): Arlington County's
https://meetings.arlingtonva.us/CountyBoard and /Planning; Tucson's hylandcloud agendaonline is the same
product.

The portal page is server-rendered: one <tr class="meeting-row"> per meeting with the meeting type,
the start time (`data-sortable-label="1/24/2026"`) and two agenda links, the HTML view
(/Meetings/ViewMeeting?id=<id>&doctype=1) and the PDF
(/Documents/DownloadFile/<Name>_<id>_Agenda_<m>_<d>_<y>_...pdf). The PDF is read when it is linked, else the
HTML view; minutes (doctype=2) are left alone. Per listing in the town config:

    {"board": "County Board", "board_key": "select_board", "platform": "onbase_agenda",
     "url": "https://meetings.arlingtonva.us/CountyBoard",
     "meeting_type": "^County Board (Regular|Recessed)"}      # regex on the meeting type, optional

Every request goes through PoliteFetcher (`Adapter.get_listing`); the page lists upcoming meetings and the
current and recent years, so one request per portal per run is enough.
"""

from __future__ import annotations

import re

from ..dates import parse_date
from ..models import AgendaDoc, Window
from .base import Adapter


class OnBaseAgendaAdapter(Adapter):
    platform = "onbase_agenda"

    def meetings(self, portal: str) -> list[dict]:
        resp = self.get_listing(portal)
        if not resp.ok:
            raise RuntimeError(f"OnBase Agenda Online HTTP {resp.status}")
        out: dict[str, dict] = {}
        for tr in self.soup(resp).select("tr.meeting-row"):
            mid = tr.get("data-meeting-id") or ""
            cells = tr.find_all("td")
            mtype = next((" ".join(td.get_text(" ", strip=True).split()) for td in cells
                          if td.get("data-sortable-type") == "mtgType"), "")
            when_td = next((td for td in cells if td.get("data-sortable-type") == "mtgTime"), None)
            when = parse_date((when_td.get("data-sortable-label") or when_td.get_text(" ", strip=True))
                              if when_td is not None else "")
            if not mtype or when is None:
                continue
            pdf = tr.find("a", href=re.compile(r"/Documents/DownloadFile/[^\"']*_Agenda_", re.I))
            html = tr.find("a", href=re.compile(r"/Meetings/ViewMeeting\?id=\d+&(?:amp;)?doctype=1", re.I))
            packet = tr.find("a", href=re.compile(r"/Documents/DownloadFile/[^\"']*_Agenda_Packet_", re.I))
            url = None
            for a in (pdf, html):
                if a is not None and a is not packet:
                    url = self.abs_url(portal, a["href"])
                    break
            if url is None:
                continue
            out.setdefault(mid or url, {"id": mid, "type": mtype, "date": when, "url": url,
                                        "packet": self.abs_url(portal, packet["href"]) if packet is not None else None})
        return list(out.values())

    def discover(self, cfg: dict) -> list[dict]:
        return cfg.get("listings", [])

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        docs = []
        by_portal: dict[str, list[dict]] = {}
        for listing in cfg.get("listings", []):
            portal = listing["url"]
            if portal not in by_portal:
                by_portal[portal] = self.meetings(portal)
            rx = re.compile(listing.get("meeting_type") or ".", re.I)
            for mt in by_portal[portal]:
                if not rx.search(mt["type"]) or mt["date"] not in window:
                    continue
                docs.append(AgendaDoc(
                    town=cfg["town"], board=listing["board"], board_key=listing["board_key"],
                    meeting_date=mt["date"], title=f"{mt['type']} {mt['date'].isoformat()} agenda",
                    url=mt["url"], listing_url=portal,
                    extra={"meeting_type": mt["type"], "kind": "agenda", **({"packet": mt["packet"]} if mt["packet"] else {})},
                ))
        return docs
