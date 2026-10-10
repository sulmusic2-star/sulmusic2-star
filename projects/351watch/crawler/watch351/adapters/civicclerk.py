"""CivicClerk public portal (https://<tenant>.portal.civicclerk.com).

The portal is a JavaScript app, but it is backed by a public, unauthenticated
read-only OData API that serves the same published data:

* GET https://<tenant>.api.civicclerk.com/v1/Events?$filter=startDateTime ge ..
  -> events with categoryName and publishedFiles [{type: "Agenda", fileId}]
* GET .../v1/Meetings/GetMeetingFileStream(fileId=<id>,plainText=false)
  -> the published agenda PDF

No login, tokens or cookies are involved.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from ..boards import classify_board
from ..models import AgendaDoc, Window
from .base import Adapter


class CivicClerkAdapter(Adapter):
    platform = "civicclerk"

    def _api(self, cfg: dict) -> str:
        return f"https://{cfg['tenant']}.api.civicclerk.com/v1"

    def _portal(self, cfg: dict) -> str:
        return f"https://{cfg['tenant']}.portal.civicclerk.com"

    def events(self, cfg: dict, window: Window) -> list[dict]:
        url = f"{self._api(cfg)}/Events"
        params = {
            "$filter": f"startDateTime ge {window.start.isoformat()}T00:00:00Z and "
                       f"startDateTime le {window.end.isoformat()}T23:59:59Z",
            "$orderby": "startDateTime",
        }
        out: list[dict] = []
        for _ in range(20):  # hard page cap
            resp = self.get_listing(url, params=params)
            if not resp.ok:
                raise RuntimeError(f"CivicClerk events HTTP {resp.status}")
            data = json.loads(resp.text)
            out.extend(data.get("value", []))
            url, params = data.get("@odata.nextLink"), None
            if not url:
                break
        return out

    def discover(self, cfg: dict) -> list[dict]:
        today = datetime.now().date()
        seen: dict[str, dict] = {}
        for ev in self.events(cfg, Window(today - timedelta(days=365), today + timedelta(days=90))):
            name = (ev.get("categoryName") or ev.get("eventName") or "").strip()
            key = classify_board(name)
            if key and name not in seen:
                seen[name] = {"board": name, "board_key": key, "url": self._portal(cfg)}
        return list(seen.values())

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        wanted = {l["board"]: l for l in cfg.get("listings", [])}
        docs = []
        for ev in self.events(cfg, window):
            name = (ev.get("categoryName") or ev.get("eventName") or "").strip()
            listing = wanted.get(name)
            if listing is None:
                continue
            when = datetime.fromisoformat(ev["startDateTime"].replace("Z", "+00:00")).date()
            for f in ev.get("publishedFiles", []):
                if (f.get("type") or "").lower() != "agenda":
                    continue
                docs.append(AgendaDoc(
                    town=cfg["town"], board=name, board_key=listing["board_key"],
                    meeting_date=when, title=f.get("name") or ev.get("eventName", ""),
                    url=f"{self._api(cfg)}/Meetings/GetMeetingFileStream(fileId={f['fileId']},plainText=false)",
                    listing_url=f"{self._portal(cfg)}/event/{ev['id']}/files",
                ))
        return docs
