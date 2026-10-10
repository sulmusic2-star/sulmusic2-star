"""Granicus Legistar (https://<client>.legistar.com), e.g. Boston City Council.

Legistar's public Web API serves the meeting calendar as JSON, no key needed:

* GET https://webapi.legistar.com/v1/<client>/events?$filter=EventDate ge datetime'YYYY-MM-DD' ...
  -> EventBodyName, EventDate, EventTime, EventAgendaFile, EventInSiteURL,
     EventAgendaLastPublishedUTC

The agenda PDFs sit on <client>.legistar1.com, whose robots.txt disallows all
bots, so the adapter reads each meeting's public detail page instead
(<client>.legistar.com/MeetingDetail.aspx), which lists every agenda item title.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from ..boards import classify_board
from ..models import AgendaDoc, Window
from .base import Adapter


class LegistarAdapter(Adapter):
    platform = "legistar"

    def _api(self, cfg: dict) -> str:
        return f"https://webapi.legistar.com/v1/{cfg['client']}"

    def events(self, cfg: dict, window: Window) -> list[dict]:
        resp = self.get_listing(f"{self._api(cfg)}/events", params={
            "$filter": f"EventDate ge datetime'{window.start.isoformat()}' and "
                       f"EventDate le datetime'{window.end.isoformat()}'",
            "$orderby": "EventDate"})
        if not resp.ok:
            raise RuntimeError(f"Legistar events HTTP {resp.status}")
        return json.loads(resp.text)

    def discover(self, cfg: dict) -> list[dict]:
        today = datetime.now().date()
        seen: dict[str, dict] = {}
        for ev in self.events(cfg, Window(today - timedelta(days=365), today + timedelta(days=120))):
            name = (ev.get("EventBodyName") or "").strip()
            key = classify_board(name)
            if key and name not in seen:
                seen[name] = {"board": name, "board_key": key,
                              "url": f"https://{cfg['client']}.legistar.com/Calendar.aspx"}
        return list(seen.values())

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        wanted = {l["board"]: l for l in cfg.get("listings", [])}
        docs = []
        for ev in self.events(cfg, window):
            listing = wanted.get((ev.get("EventBodyName") or "").strip())
            if listing is None or not ev.get("EventAgendaFile") or not ev.get("EventInSiteURL"):
                continue
            when = datetime.fromisoformat(ev["EventDate"][:19]).date()
            docs.append(AgendaDoc(
                town=cfg["town"], board=listing["board"], board_key=listing["board_key"],
                meeting_date=when, title=f"{listing['board']} {when.isoformat()} agenda items",
                url=ev["EventInSiteURL"], listing_url=listing["url"],
                extra={"agenda_pdf": ev["EventAgendaFile"]},
            ))
        return docs
