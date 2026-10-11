"""eSCRIBE published-meetings portal (https://pub-<client>.escribemeetings.com).

The portal home page is server-rendered and lists every upcoming meeting with
its type, date and published files. Each agenda file link carries an
aria-label such as

    "Agenda (PDF) for Town Board Regular Meeting 13 October 2026"
    -> /FileStream.ashx?DocumentId=10031          (the agenda PDF, plain GET)

Past meetings are loaded by a POST JSON call, which this adapter does not use:
it reads what is posted ahead of meetings, which is what alerts need. Per
listing in the town config:

    {"board": "Town Board", "board_key": "select_board",
     "url": "https://pub-southamptonny.escribemeetings.com/",
     "meeting_type": "^Town Board (Regular|Special)"}     # regex on the meeting type name

When a meeting has both "Agenda (PDF)" and "Agenda Full Package (PDF)", only the
agenda is taken (packages can run to hundreds of pages); a package is used when it
is the only agenda file.

Some eSCRIBE tenants put file downloads (FileStream.ashx) behind a "Verifying your
browser" challenge, which is never solved here. Set "format": "html" on the listing to
read the portal's own HTML agenda view instead (Meeting.aspx?Id=...&Agenda=Agenda, linked
on the portal as "Agenda ... (HTML)"); it is served without a challenge.
"""

from __future__ import annotations

import re
from datetime import datetime

from ..models import AgendaDoc, Window
from .base import Adapter

_LABEL = re.compile(r"^(Agenda(?: Full Package)?) \((PDF|HTML)\) for (.+?) (\d{1,2} [A-Z][a-z]+ 20\d\d)\s*$")


class EscribeAdapter(Adapter):
    platform = "escribe"

    def meetings(self, portal: str) -> list[dict]:
        resp = self.get_listing(portal)
        if not resp.ok:
            raise RuntimeError(f"eSCRIBE portal HTTP {resp.status}")
        found: dict[tuple[str, str], dict] = {}
        for a in self.soup(resp).select("a[href*='FileStream.ashx?DocumentId='], a[href*='Agenda=Agenda']"):
            m = _LABEL.match(" ".join((a.get("aria-label") or "").split()))
            if not m:
                continue
            kind, fmt, mtype, day = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
            when = datetime.strptime(day, "%d %B %Y").date()
            rec = found.setdefault((mtype, day), {"type": mtype, "date": when})
            rec.setdefault(kind if fmt == "PDF" else "HTML", self.abs_url(portal, a["href"]))
        return list(found.values())

    def discover(self, cfg: dict) -> list[dict]:
        return cfg.get("listings", [])

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        docs = []
        by_portal: dict[str, list[dict]] = {}
        for listing in cfg.get("listings", []):
            portal = listing["url"]
            if portal not in by_portal:
                by_portal[portal] = self.meetings(portal)
            rx = re.compile(listing.get("meeting_type") or re.escape(listing["board"]), re.I)
            for mt in by_portal[portal]:
                if not rx.search(mt["type"]) or mt["date"] not in window:
                    continue
                if listing.get("format") == "html":
                    url = mt.get("HTML")
                else:
                    url = mt.get("Agenda") or mt.get("Agenda Full Package")
                if not url:
                    continue
                docs.append(AgendaDoc(
                    town=cfg["town"], board=listing["board"], board_key=listing["board_key"],
                    meeting_date=mt["date"], title=f"{mt['type']} {mt['date'].isoformat()} agenda",
                    url=url, listing_url=portal, extra={"meeting_type": mt["type"]},
                ))
        return docs
