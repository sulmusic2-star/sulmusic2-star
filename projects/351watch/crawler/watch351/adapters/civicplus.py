"""CivicPlus "Agenda Center" (https://<town>/AgendaCenter).

The most common platform among Massachusetts towns. Layout:

* /AgendaCenter                       - every board ("category") with its id
* /AgendaCenter/<Board-Name>-<id>     - human-browsable listing for one board
* /AgendaCenter/Search/?CIDs=..&startDate=..&endDate=..
                                      - all agendas for chosen boards in a date
                                        range (one request per town)
* /AgendaCenter/ViewFile/Agenda/_MMDDYYYY-<agendaId>
                                      - the agenda itself (usually a PDF)

Listing option "linked_agenda": true (Lansing NY, 2026-11): the town's AgendaCenter "agenda" is a
one-line cover sheet whose only content is two links, "Meeting Agenda" and "Meeting Packet", to
DocumentCenter files. The adapter then reads the row's HTML view (?html=true, one listing request
per meeting, cached like a listing page) and takes the first link whose text says "agenda" (not
"packet") as the document; a row whose HTML view has no such link keeps the cover-sheet PDF.
"""

from __future__ import annotations

import re

from ..boards import classify_board
from ..dates import first_date
from ..models import AgendaDoc, Window
from .base import Adapter


def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")


class CivicPlusAdapter(Adapter):
    platform = "civicplus"

    def categories(self, website: str) -> list[tuple[str, str]]:
        resp = self.get_listing(website.rstrip("/") + "/AgendaCenter")
        if not resp.ok:
            return []
        soup = self.soup(resp)
        cats = []
        for h2 in soup.select("div.listing h2[aria-controls]"):
            cid = h2["aria-controls"].replace("category-panel-", "")
            cats.append((cid, " ".join(h2.get_text(" ", strip=True).split())))
        return cats

    def discover(self, cfg: dict) -> list[dict]:
        website = cfg["website"].rstrip("/")
        listings = []
        for cid, name in self.categories(website):
            key = classify_board(name)
            if key:
                listings.append({
                    "board": name,
                    "board_key": key,
                    "category_id": cid,
                    "url": f"{website}/AgendaCenter/{_slug(name)}-{cid}",
                })
        return listings

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        website = cfg["website"].rstrip("/")
        by_name = {l["board"].lower(): l for l in cfg.get("listings", [])}
        cids = [l["category_id"] for l in cfg.get("listings", [])]
        if not cids:
            return []
        resp = self.get_listing(
            f"{website}/AgendaCenter/Search/",
            params={
                "term": "", "CIDs": ",".join(cids) + ",",
                "startDate": window.start.strftime("%m/%d/%Y"),
                "endDate": window.end.strftime("%m/%d/%Y"),
                "dateRange": "", "dateSelector": "",
            },
        )
        if not resp.ok:
            raise RuntimeError(f"AgendaCenter search returned HTTP {resp.status}")
        docs: list[AgendaDoc] = []
        linked: dict[str, str | None] = {}
        for block in self.soup(resp).select("div.listing"):
            h2 = block.find("h2")
            if not h2:
                continue
            name = " ".join(h2.get_text(" ", strip=True).split())
            listing = by_name.get(name.lower())
            if listing is None:
                continue
            for row in block.select("tr.catAgendaRow"):
                link = row.select_one("p a[href*='ViewFile/Agenda']") or \
                    row.select_one("a[href*='ViewFile/Agenda']")
                if not link:
                    continue
                href = link["href"].split("?")[0]
                strong = row.find("strong")
                when = first_date(strong.get("aria-label") if strong else None,
                                  strong.get_text(" ", strip=True) if strong else None, href)
                if when not in window:
                    continue
                url = self.abs_url(website + "/", href)
                if listing.get("linked_agenda"):
                    if url not in linked:
                        linked[url] = self.linked_agenda(url)
                    url = linked[url] or url
                docs.append(AgendaDoc(
                    town=cfg["town"], board=name, board_key=listing["board_key"],
                    meeting_date=when, title=link.get_text(" ", strip=True),
                    url=url, listing_url=listing["url"],
                ))
        return docs

    def linked_agenda(self, agenda_url: str) -> str | None:
        """The document the agenda's HTML view links as the agenda ("Meeting Agenda" ->
        /DocumentCenter/View/712), when the AgendaCenter file itself is only a cover sheet."""
        resp = self.get_listing(agenda_url + "?html=true")
        if not resp.ok:
            return None
        best = None
        for a in self.soup(resp).find_all("a", href=True):
            text = " ".join(a.get_text(" ", strip=True).split())
            if re.search(r"agenda", text, re.I) and not re.search(r"packet|minutes", text, re.I):
                best = self.abs_url(resp.final_url, a["href"])
                break
        return best
