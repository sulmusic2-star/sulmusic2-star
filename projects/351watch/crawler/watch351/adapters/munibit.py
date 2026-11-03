"""Munibit municipal CMS: the "Agendas & Minutes" document module that small New York towns' sites fill
client-side (Perth, Spafford and Boston NY, found in the 2026-10 pilot as "JavaScript CMS, agendasandminutes
module"). The page's server HTML holds no documents; an inline script imports

    /api/public/mwjsResources?tn=<tenant>&et=<tenant id>&pi=<page>&eb=<block>&tg=<tag>&xtg=

which is a JavaScript module with the document library embedded. The same address with `&jd=t` answers
plain JSON (what the module's own refresh call uses): `files` (fileTitle, fileName, fileType,
fileDateCreated, dispDate, tags -> category ids, fileUrl) and `categories` (catId, name, parentId), the
whole tenant library whichever page was read. robots.txt is absent on the three sites (404: everything
allowed); the JSON needs no cookie or token.

What this adapter reads: the meeting list. A file's board is the nearest category in its folder path that
names a tracked board ("Town Board Agendas / 2026", "ZBA / Agendas & Minutes / 2026 ZBA", "Agendas &
Minutes / Planning Board / Agendas"); its kind comes from the title and file name (agenda, packet,
notice; minutes and cancellations are dropped), else from the folder when the title is only a date; its
meeting date from the title ("11.05.2026 TB Agenda", "TB 2026-10-21 Agenda Packet", "sep. 17, 2026"),
else from the meeting folder ("October 8, 2026 Agenda & Documents" holds "Agenda 10.8"), else a
month-day in the title with the folder's or the display date's year. A title naming only a month
("11-2026 Meeting Notice") gives no date; the month is kept in `extra["month"]`.

What it cannot read yet: the files. `fileUrl` (/api/blob/viewBlob?rf=t&i=...) answers a plain GET with
the site's HTML viewer page, not the file, and the download link the JSON gives (/api/blob/gb?gb=...)
answers HTTP 400 "Access denied: item not accessible" to AgendaAheadBot (checked 2026-11-03 on Perth).
The viewer page is the town's home page around an embedded reader, so scanning it would match the wrong
text. `list_agendas` therefore raises unless the listing says "files_readable": true, which is to be set
only once the town or Munibit lets the reader fetch the files; `meetings()` still gives the list for
reports and for the unblock request. Per listing in the town config:

    {"platform": "munibit", "board": "Town Board", "board_key": "select_board",
     "url": "https://www.perthny.gov/agendasandminutes",     # any page that embeds the module
     "board_rules": [[regex, board, board_key], ...],         # optional: overrides the folder-based board
     "files_readable": false}

Every request goes through PoliteFetcher (`Adapter.get_listing`): one page and one JSON request per host
per run.
"""

from __future__ import annotations

import json
import re
from datetime import date
from urllib.parse import urlsplit

from ..boards import classify_board
from ..dates import MONTHS, parse_date
from ..models import AgendaDoc, Window
from .agenda_page import AGENDA, MINUTES, OTHER_DOC, doc_kind
from .base import Adapter

_IMPORT = re.compile(r"""import\(\s*['"](/api/public/mwjsResources\?[^'"]+)['"]\s*\)""", re.I)
_MONTH_DOT = re.compile(r"\b([A-Za-z]{3,9})\.(\d)")                    # "oct.15, 2026" -> "oct. 15, 2026"
_MONTH_DAY_NUM = re.compile(r"(?<![\d.])(\d{1,2})[./-](\d{1,2})(?![\d./-]*\d{4})(?!\d)")   # "8.13", "5.14-2"
_MONTH_DAY_NAME = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b(?!,?\s*\d{4})", re.I)
_MONTH_YEAR = re.compile(r"(?<!\d)(\d{1,2})[-/](20\d\d)(?!\d)|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(20\d\d)\b", re.I)
_MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
# a title that is only a date: "oct.15, 2026", "February 12", "12 October 2024", "10.8.2026", "2026-10-21"
_DATE_ONLY = re.compile(r"^[\W_]*(?:" + _MON + r"\s*\d{1,2}(?:st|nd|rd|th)?,?\s*(?:\d{4})?|\d{1,2}\s+" + _MON + r"\s*\d{4}|"
                        r"\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?|20\d\d-\d\d-\d\d)[\W_]*(?:(?:agenda|meeting|regular|special|"
                        r"revised|amended|final|draft|tb|pb|zba)[\W_]*)*$", re.I)
# the library holds every town document; only folders about meetings are read (not "Bids and RFP's / Town Board")
_MEETING_FOLDER = re.compile(r"agenda|meeting|minutes|packet", re.I)
_SKIP_TYPES = {"jpg", "jpeg", "png", "gif", "mp3", "mp4", "m4a", "mov", "link"}


def _norm(s: str | None) -> str:
    return " ".join((s or "").split())


def _full_date(s: str) -> date | None:
    return parse_date(_MONTH_DOT.sub(r"\1. \2", s))


def _month_day(s: str, year: int | None) -> date | None:
    """'Agenda 8.13' / 'July 9 Budget' -> a date in `year`, when the title gives month and day without a year."""
    if not year:
        return None
    m = _MONTH_DAY_NAME.search(s)
    if m:
        try:
            return date(year, MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
        except (KeyError, ValueError):
            pass
    m = _MONTH_DAY_NUM.search(s)
    if m:
        try:
            return date(year, int(m.group(1)), int(m.group(2)))
        except ValueError:
            return None
    return None


def _month_only(s: str) -> str | None:
    m = _MONTH_YEAR.search(s)
    if not m:
        return None
    if m.group(1):
        mo, y = int(m.group(1)), int(m.group(2))
    else:
        mo, y = MONTHS[m.group(3)[:3].lower()], int(m.group(4))
    return f"{y}-{mo:02d}" if 1 <= mo <= 12 else None


def _disp_date(s: str | None) -> date | None:
    try:
        d = date.fromisoformat((s or "")[:10])
    except ValueError:
        return None
    return d if 2020 <= d.year <= 2031 else None   # 1974-01-23 and 2161-09-20 are placeholders


class MunibitAdapter(Adapter):
    platform = "munibit"

    def __init__(self, fetcher):
        super().__init__(fetcher)
        self._library: dict[str, dict] = {}   # host -> parsed JSON (the library is tenant-wide)

    # ---------------------------------------------------------------- library
    def library(self, page_url: str) -> dict:
        """The tenant's document library: the module page, then its JSON. Cached per host for this adapter."""
        host = urlsplit(page_url).netloc
        if host in self._library:
            return self._library[host]
        resp = self.get_listing(page_url)
        if not resp.ok:
            raise RuntimeError(f"Munibit page {page_url} returned HTTP {resp.status}")
        m = _IMPORT.search(resp.text)
        if not m:
            raise RuntimeError(f"Munibit page {page_url} embeds no mwjsResources module")
        parts = urlsplit(resp.final_url)
        json_url = f"{parts.scheme}://{parts.netloc}{m.group(1)}&jd=t"
        jr = self.get_listing(json_url)
        if not jr.ok:
            raise RuntimeError(f"Munibit resources JSON {json_url} returned HTTP {jr.status}")
        try:
            data = json.loads(jr.text)
        except ValueError as e:
            raise RuntimeError(f"Munibit resources JSON {json_url}: not JSON ({e})") from e
        if not isinstance(data, dict) or "files" not in data:
            raise RuntimeError(f"Munibit resources JSON {json_url}: no files key")
        data["_json_url"] = json_url
        data["_origin"] = f"{parts.scheme}://{parts.netloc}"
        self._library[host] = data
        return data

    @staticmethod
    def _paths(data: dict) -> dict[str, list[str]]:
        cats = {c.get("catId"): c for c in data.get("categories", []) if c.get("catId")}
        out: dict[str, list[str]] = {}
        for cid in cats:
            names, cur, seen = [], cid, set()
            while cur in cats and cur not in seen:
                seen.add(cur)
                names.append(_norm(cats[cur].get("name")))
                cur = cats[cur].get("parentId")
            out[cid] = list(reversed(names))
        return out

    def meetings(self, page_url: str, state: str = "NY") -> list[dict]:
        """Every agenda, packet or hearing notice in the library: board, board_key, date (or None), month,
        title, kind, posted, viewer_url, file_id, path."""
        data = self.library(page_url)
        paths = self._paths(data)
        origin = data["_origin"]
        out: list[dict] = []
        for f in data.get("files", []):
            if (f.get("fileType") or "").lower() in _SKIP_TYPES or f.get("hidden"):
                continue
            title = _norm(f.get("fileTitle")) or _norm(f.get("fileName"))
            fname = _norm(f.get("fileName"))
            path = next((paths[t.get("eItemId")] for t in f.get("tags", []) if t.get("eItemId") in paths), [])
            if not any(_MEETING_FOLDER.search(p) for p in path):
                continue
            if any(MINUTES.search(p) and not AGENDA.search(p) for p in path) and not AGENDA.search(f"{title} {fname}"):
                continue   # a "Minutes" folder: minutes, even "07-06-2026 DRAFT with attachments"
            folder = path[-1] if path else ""
            parent = path[-2] if len(path) > 1 else ""
            folder_date = next((d for d in (_full_date(p) for p in reversed(path)) if d), None)
            disp = _disp_date(f.get("dispDate"))
            year = (folder_date or disp).year if (folder_date or disp) else None
            # the title's own date first ("Agenda 10.8.2026", "7.9 Agenda", "February 12"), then the meeting folder's
            # ("October 8, 2026 Agenda & Documents" holds "AGENDA"), then the clerk's display date
            own = _full_date(title) or _full_date(fname) or _month_day(title, year) or _month_day(fname, year)
            kind = doc_kind(title, fname)
            if kind == "unknown" and _DATE_ONLY.match(title) and not OTHER_DOC.search(title):
                # a title that is only a date takes its folder's kind: "oct.15, 2026" under "Planning Board / Agendas",
                # "February 12" under "Agendas & Meeting Documents / 2026"; not when the folder is another meeting's
                # ("February 12", the minutes, filed under "March 12 2026 Agenda & Documents")
                if folder_date is None or own is None or own == folder_date:
                    kind = doc_kind(folder, parent, " / ".join(path))
            if kind not in ("agenda", "packet", "notice"):
                continue
            board_key = None
            board = ""
            for name in reversed(path):   # nearest folder naming a tracked board wins
                key = classify_board(name, state)
                if key:
                    board_key, board = key, name
                    break
            when = own or folder_date
            month = None
            if when is None:
                month = _month_only(title) or _month_only(fname)
                if month is None and disp is not None and kind in ("agenda", "packet", "notice") \
                        and not _month_only(" / ".join(path)):
                    when = disp   # the clerk's display date is the meeting date when nothing else is written
            out.append({
                "board": board, "board_key": board_key, "date": when, "month": month, "title": title,
                "kind": kind, "posted": (f.get("fileDateCreated") or "")[:10] or None,
                "viewer_url": f"{origin}/api/blob/viewBlob?rf=t&i={re.search(r'[?&]i=([^&]+)', f.get('fileUrl') or '').group(1)}"
                if re.search(r"[?&]i=([^&]+)", f.get("fileUrl") or "") else f.get("fileUrl"),
                "file_id": f.get("eFileId"), "path": path,
            })
        return out

    # --------------------------------------------------------------- adapter
    def discover(self, cfg: dict) -> list[dict]:
        return cfg.get("listings", [])

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        docs: dict[str, AgendaDoc] = {}
        for listing in cfg.get("listings", []):
            rules = [(re.compile(rx, re.I), b, k) for rx, b, k in listing.get("board_rules", [])]
            found = self.meetings(listing["url"], cfg.get("state") or "NY")
            if not listing.get("files_readable"):
                raise RuntimeError(
                    f"Munibit lists {sum(1 for m in found if m['date'] in window)} agenda files in the window on "
                    f"{listing['url']}, but serves the files only to its own page viewer (the download link answers "
                    f"'Access denied' to AgendaAheadBot); set files_readable once the town or Munibit allows it")
            for m in found:
                board, key = listing["board"], listing["board_key"]
                hit = next(((b, k) for rx, b, k in rules if rx.search(f"{m['title']} {' / '.join(m['path'])}")), None)
                if hit:
                    board, key = hit
                elif m["board_key"] != key:
                    continue
                if m["date"] not in window and not (m["date"] is None and m["month"]
                                                    and window.start.strftime("%Y-%m") <= m["month"] <= window.end.strftime("%Y-%m")):
                    continue
                extra = {"kind": m["kind"], "category": " / ".join(m["path"]), "file_id": m["file_id"]}
                if m["posted"]:
                    extra["posted"] = m["posted"]
                if m["month"]:
                    extra["month"] = m["month"]
                docs.setdefault(m["viewer_url"], AgendaDoc(
                    town=cfg["town"], board=board, board_key=key, meeting_date=m["date"], title=m["title"][:200],
                    url=m["viewer_url"], listing_url=listing["url"], extra=extra))
        return list(docs.values())
