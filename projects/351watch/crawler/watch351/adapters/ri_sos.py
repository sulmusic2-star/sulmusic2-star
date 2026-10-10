"""Rhode Island Secretary of State Open Meetings portal (https://opengov.sos.ri.gov).

Every RI public body must file its meeting notice and agenda on this portal at
least 48 hours before a meeting, not counting weekends and state holidays
(R.I. Gen. Laws 42-46-6(b)). One adapter therefore covers all 39 cities and
towns, including towns whose own websites sit behind bot walls, and every
meeting carries the portal's own "Filed on" timestamp.

Everything below is a plain GET that the portal's public pages issue themselves
(links, or the jQuery calls behind "click a meeting date"). No login, no form
POSTs, no cookies. robots.txt is a 404 (allow all). The RI.gov copyright policy
calls the compiled information public and free to distribute, and the SOS
invites "advanced users" to stream the data by RSS.

* GET /GOVDirectoryPublic/OfficialSearch?topmenuId=105&page=IdxMuni
      the 39 municipalities (plus the Narragansett Indian Tribe) and the
      EntityID of each "Hopkinton, Town of" parent entity
* GET /OpenMeetingsPublic/OpenMeetingDashboard?subtopmenuId=201&EntityID=<id>&MeetingID=0
      - for a municipality: table#ParentEntitiesSummary lists every public body
        filed under it (name + EntityID)                           -> discover()
      - for a public body: every upcoming and past meeting (MeetingID, date,
        time) plus a cancelled-meetings table                      -> list_agendas()
* GET /OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID=<id>
      the HTML fragment the dashboard's meeting popup loads: "Filed on"
      (notice time), Emergency / Annual Calendar / Public Announcement flags,
      and one "Agenda filed on <time> by <name>" link per uploaded agenda file
* GET /Common/DownloadMeetingFiles?FilePath=%5CNotices%5C<n>%5C<yyyy>%5C<id>.pdf
      the agenda file itself (PDF, sometimes Word)
* GET /OpenMeetingsPublic/MeetingInformation?MeetingID=<id>
      human-readable meeting page (the portal's RSS items link here), used as
      listing_url
* GET /GOVDirectoryPublic/GOVDirectoryMeetingDetails?EntityID=<id>
      RI Gov Directory page of a municipality (official website), discovery only

Town config fields read: `sos_entity_id` (the municipality's parent EntityID)
and `listings` [{board, board_key, entity_id, entity_name, url}].
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from urllib.parse import quote
from zoneinfo import ZoneInfo

from ..boards import classify_board
from ..fetch import FetchError
from ..models import AgendaDoc, Window
from .base import LISTING_MAX_AGE, Adapter

log = logging.getLogger(__name__)

BASE = "https://opengov.sos.ri.gov"
ET = ZoneInfo("America/New_York")
MUNICIPAL_INDEX_URL = f"{BASE}/GOVDirectoryPublic/OfficialSearch?topmenuId=105&page=IdxMuni"
ACTIVE_DAYS = 730   # a body with no meeting in two years (and none upcoming) is not listed


def dashboard_url(entity_id: int | str) -> str:
    return f"{BASE}/OpenMeetingsPublic/OpenMeetingDashboard?subtopmenuId=201&EntityID={entity_id}&MeetingID=0"


def detail_url(meeting_id: int | str) -> str:
    return f"{BASE}/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID={meeting_id}"


def meeting_page_url(meeting_id: int | str) -> str:
    return f"{BASE}/OpenMeetingsPublic/MeetingInformation?MeetingID={meeting_id}"


def directory_url(entity_id: int | str) -> str:
    return f"{BASE}/GOVDirectoryPublic/GOVDirectoryMeetingDetails?EntityID={entity_id}"


def file_url(path: str) -> str:
    """'\\Notices\\6739\\2026\\568140.pdf' -> download URL (backslashes as %5C)."""
    return f"{BASE}/Common/DownloadMeetingFiles?FilePath={quote(path, safe='.-_')}"


# ---------------------------------------------------------------------------
# Board names. Portal bodies are named "<Town> <Body>" ("Hopkinton Planning
# Board", "Providence City Plan Commission"); strip the town, then classify.
# ---------------------------------------------------------------------------

_RI_EXCLUDE = re.compile(
    r"sub-?committee|committee|advisory|task force|joint|regional|historic|housing|charter|school|"
    r"budget|canvass|licens|water|sewer|tax|personnel|library|harbor|building code|fire|"
    r"technical review|land trust|sitting as|acting as|board of finance|ad hoc",
    re.I)

_RI_BOARDS: list[tuple[str, re.Pattern]] = [
    ("planning_board", re.compile(
        r"^(?:city\s+)?plan(?:ning)?\s+(?:board|commission)\b|^planning\b", re.I)),
    ("zoning_board_of_appeals", re.compile(
        r"^zoning\s+(?:board|review|appeals?)\b|^(?:zoning\s+)?board\s+of\s+(?:zoning\s+)?(?:review|appeals)\b", re.I)),
    ("select_board", re.compile(r"^(?:town|city)\s+council\b", re.I)),
    ("conservation_commission", re.compile(r"^conservation\s+commission\b", re.I)),
    ("town_meeting", re.compile(r"^(?:annual\s+|special\s+)?(?:financial\s+)?town\s+meeting\b", re.I)),
]


def strip_town(name: str, town: str) -> str:
    """'Hopkinton Planning Board' -> 'Planning Board'; 'Town of X Planning Board' -> 'Planning Board'."""
    n = " ".join(name.split())
    for pat in (rf"^{re.escape(town)}\b[\s,\-–:]*", rf"^(?:the\s+)?(?:town|city)\s+of\s+{re.escape(town)}\b[\s,\-–:]*",
                rf"[\s,\-–]+(?:town|city)\s+of\s+{re.escape(town)}$", rf"[\s,\-–(]+{re.escape(town)}\)?$"):
        n = re.sub(pat, "", n, flags=re.I).strip()
    return n or name


def classify_ri_body(name: str, town: str) -> str | None:
    """Board key for a portal body name of `town`, or None if 351 Watch does not track it."""
    rest = strip_town(name, town)
    if _RI_EXCLUDE.search(rest):
        return None
    for key, rx in _RI_BOARDS:
        if rx.search(rest):
            return key
    if not rest.lower().startswith(town.lower()) and rest != name:
        return classify_board(rest)   # e.g. "Planning and Zoning Commission"
    return None


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

_MEETING_ID = re.compile(r"ViewMeetingDetails\((\d+)\)")
_ENTITY_ID = re.compile(r"EntityID=(\d+)")
_DOWNLOAD = re.compile(r"DownloadMeetingFiles\('([^']+)'\)")
_FILED = re.compile(r"(Agenda|Minutes)\s+filed\s+on\s+(.+?\d{1,2}:\d{2}\s*[AP]M)", re.I)


def parse_ts(s: str | None) -> datetime | None:
    """'Oct  6 2026, 03:17PM' -> aware datetime in America/New_York."""
    if not s:
        return None
    s = " ".join(s.replace(",", " ").split())
    for fmt in ("%b %d %Y %I:%M%p", "%b %d %Y %I:%M %p"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=ET)
        except ValueError:
            continue
    return None


def parse_time(s: str | None) -> str | None:
    """'9:30AM' / '5:30 PM' -> '09:30' (24h), else None."""
    m = re.search(r"(\d{1,2}):(\d{2})\s*([AP])\.?M", s or "", re.I)
    if not m:
        return None
    h = int(m.group(1)) % 12 + (12 if m.group(3).upper() == "P" else 0)
    return f"{h:02d}:{m.group(2)}"


def meeting_start(d: date, hhmm: str | None) -> datetime:
    h, m = (int(x) for x in (hhmm or "00:00").split(":"))
    return datetime(d.year, d.month, d.day, h, m, tzinfo=ET)


def parse_municipal_index(soup) -> list[dict]:
    """Directory 'Cities & Towns' table -> [{town, kind, sos_entity_id, sos_entity_name}]."""
    out = []
    for a in soup.select("table#SearchGovDirectoryOfficial a[onclick]"):
        m = re.search(r"GOVDirectoryMeetingInfo\((\d+)\s*,\s*(\d+)\)", a["onclick"])
        name = a.get_text(" ", strip=True)
        nm = re.match(r"^(.+?),\s*(Town|City) of$", name)
        if not (m and nm):
            continue  # e.g. "Narragansett Indian Tribe"
        out.append({"town": nm.group(1), "kind": nm.group(2).lower(),
                    "sos_entity_id": int(m.group(1)), "sos_entity_name": name})
    return out


def parse_child_bodies(soup) -> list[dict]:
    """Municipality dashboard -> [{entity_id, entity_name}] of every body filed under it."""
    out, seen = [], set()
    table = soup.find("table", id="ParentEntitiesSummary")
    for a in (table.find_all("a", href=True) if table else []):
        m = _ENTITY_ID.search(a["href"])
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append({"entity_id": int(m.group(1)), "entity_name": " ".join(a.get_text(" ", strip=True).split())})
    return out


_SKIP_TABLES = {"ParentEntitiesSummary", "RecentlyFiledMeetingMinutes", "UpcomingMeetingforSubCommittee"}


def parse_meeting_rows(soup) -> list[dict]:
    """Body dashboard -> [{meeting_id, date, time, cancelled}] (upcoming, today, past)."""
    cancelled: set[int] = set()
    rows: dict[int, dict] = {}
    for table in soup.find_all("table"):
        tid = table.get("id") or ""
        if tid in _SKIP_TABLES:
            continue
        for tr in table.find_all("tr"):
            ids = {int(x) for el in tr.find_all(onclick=True) for x in _MEETING_ID.findall(el["onclick"])}
            if len(ids) != 1:
                continue
            mid = ids.pop()
            if tid == "CancelledMeetingSummary":
                cancelled.add(mid)
                continue
            seq = tr.find("div", id=re.compile(r"^hdn\w*DateSeq$"))
            seq_text = seq.get_text(strip=True) if seq else ""
            try:
                d = datetime.strptime(seq_text[:8], "%Y%m%d").date()
            except ValueError:
                continue
            cells = tr.find_all("td")
            rows.setdefault(mid, {"meeting_id": mid, "date": d,
                                  "time": parse_time(cells[-1].get_text(" ", strip=True) if cells else "")})
    for mid, r in rows.items():
        r["cancelled"] = mid in cancelled
    return sorted(rows.values(), key=lambda r: (r["date"], r["time"] or "", r["meeting_id"]))


def parse_meeting_detail(soup) -> dict:
    """ViewMeetingDetailByID fragment -> notice fields and agenda files."""
    fields: dict[str, str] = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2 and tds[0].find("label"):
            label = tds[0].get_text(" ", strip=True).rstrip(":").strip().lower()
            fields.setdefault(label, " ".join(tds[1].get_text(" ", strip=True).split()))
    agendas, minutes = [], []
    for a in soup.find_all("a"):
        m = _DOWNLOAD.search(a.get("onclick") or "")
        text = " ".join(a.get_text(" ", strip=True).split())
        f = _FILED.search(text)
        if not m:
            continue
        item = {"path": m.group(1).replace("\\\\", "\\"), "text": text,
                "filed_at": parse_ts(f.group(2)) if f else None}
        (minutes if (f and f.group(1).lower() == "minutes") or text.lower().startswith("minutes") else agendas).append(item)
    yes = lambda k: fields.get(k, "").strip().lower().startswith("y")
    return {
        "body": fields.get("public body name"),
        "date": fields.get("date"),
        "time": parse_time(fields.get("time")),
        "address": fields.get("address"),
        "filed_on": parse_ts(fields.get("filed on")),
        "emergency": yes("emergency meeting"),
        "annual_calendar": yes("annual calendar"),
        "public_announcement": yes("public announcement"),
        "agendas": agendas,
        "minutes_files": len(minutes),
    }


# ---------------------------------------------------------------------------
# RI state holidays and the 48-hour rule (hours exclude weekends and holidays)
# ---------------------------------------------------------------------------

def _nth_weekday(y: int, month: int, weekday: int, n: int) -> date:
    d = date(y, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def _last_weekday(y: int, month: int, weekday: int) -> date:
    d = date(y, month + 1, 1) - timedelta(days=1) if month < 12 else date(y, 12, 31)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _observed(d: date) -> date:
    """R.I. Gen. Laws 25-1-1: a fixed-date holiday on a weekend moves to Monday."""
    return d + timedelta(days=(7 - d.weekday()) % 7) if d.weekday() >= 5 else d


def ri_holidays(y: int) -> set[date]:
    """Legal holidays under R.I. Gen. Laws 25-1-1 (plus Thanksgiving)."""
    days = {
        _observed(date(y, 1, 1)), _nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3),
        date(y, 5, 4), _last_weekday(y, 5, 0), _observed(date(y, 6, 19)), _observed(date(y, 7, 4)),
        _nth_weekday(y, 8, 0, 2), _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 10, 0, 2),
        _observed(date(y, 11, 11)), _nth_weekday(y, 11, 3, 4), _observed(date(y, 12, 25)),
    }
    if y % 2 == 0:   # general election for state officers: Tuesday after the first Monday in November
        days.add(_nth_weekday(y, 11, 0, 1) + timedelta(days=1))
    return days


def business_hours_between(start: datetime, end: datetime) -> float:
    """Hours from `start` to `end`, not counting Saturdays, Sundays or RI holidays
    (the way R.I. Gen. Laws 42-46-6(b) counts its 48 hours). Negative if end < start."""
    if end < start:
        return -business_hours_between(end, start)
    start, end = start.astimezone(ET), end.astimezone(ET)
    hol: dict[int, set[date]] = {}
    total, cur = 0.0, start
    while cur < end:
        nxt = min(end, datetime(cur.year, cur.month, cur.day, tzinfo=ET) + timedelta(days=1))
        d = cur.date()
        if d.weekday() < 5 and d not in hol.setdefault(d.year, ri_holidays(d.year)):
            total += (nxt - cur).total_seconds() / 3600
        cur = nxt
    return total


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class RISOSAdapter(Adapter):
    platform = "ri_sos"

    # -- discovery -------------------------------------------------------
    def municipalities(self) -> list[dict]:
        resp = self.get_listing(MUNICIPAL_INDEX_URL)
        if not resp.ok:
            raise RuntimeError(f"RI SOS municipal index HTTP {resp.status}")
        return parse_municipal_index(self.soup(resp))

    def website(self, entity_id: int) -> str | None:
        resp = self.fetcher.get(directory_url(entity_id), max_age=7 * 24 * 3600)
        if not resp.ok:
            return None
        soup = self.soup(resp)
        for td in soup.find_all(string=re.compile(r"^\s*Web:\s*$")):
            a = td.find_next("a", href=True)
            if a and a["href"].startswith("http"):
                return a["href"].strip()
        return None

    def child_bodies(self, entity_id: int) -> list[dict]:
        resp = self.get_listing(dashboard_url(entity_id))
        if not resp.ok:
            raise RuntimeError(f"RI SOS dashboard {entity_id} HTTP {resp.status}")
        return parse_child_bodies(self.soup(resp))

    def body_meetings(self, entity_id: int) -> list[dict]:
        resp = self.get_listing(dashboard_url(entity_id))
        if not resp.ok:
            raise FetchError(f"RI SOS dashboard {entity_id} HTTP {resp.status}")
        return parse_meeting_rows(self.soup(resp))

    def discover(self, cfg: dict) -> list[dict]:
        """Listings for every tracked board of one municipality that has met in the
        last ACTIVE_DAYS days or has a meeting scheduled. Sets cfg['_discovery'] with
        per-board evidence and the bodies left out."""
        town = cfg["town"]
        eid = cfg.get("sos_entity_id")
        if not eid:
            match = [m for m in self.municipalities() if m["town"].lower() == town.lower()]
            if not match:
                raise RuntimeError(f"{town}: not in the RI SOS municipal directory")
            eid = cfg["sos_entity_id"] = match[0]["sos_entity_id"]
        today = date.today()
        listings, evidence, stale, untracked = [], {}, {}, []
        for body in self.child_bodies(eid):
            key = classify_ri_body(body["entity_name"], town)
            if key is None:
                untracked.append(body["entity_name"])
                continue
            meetings = [m for m in self.body_meetings(body["entity_id"]) if not m["cancelled"]]
            dates = [m["date"] for m in meetings]
            recent = [d for d in dates if abs((d - today).days) <= 120]
            ev = {"board": strip_town(body["entity_name"], town), "entity_id": body["entity_id"],
                  "entity_name": body["entity_name"], "source": "ri_sos", "url": dashboard_url(body["entity_id"]),
                  "n_meetings_total": len(dates), "n_recent": len(recent),
                  "n_past_90": sum(1 for d in dates if 0 <= (today - d).days <= 90),
                  "latest": max(dates).isoformat() if dates else None,
                  "latest_past": max((d for d in dates if d <= today), default=None)}
            if ev["latest_past"]:
                ev["latest_past"] = ev["latest_past"].isoformat()
            active = any(d >= today - timedelta(days=ACTIVE_DAYS) for d in dates)
            if not active:
                ev["note"] = f"no meeting filed since {ev['latest'] or 'ever'}"
                stale.setdefault(key, []).append(ev)
                continue
            evidence.setdefault(key, []).append(ev)
            listings.append({"board": ev["board"], "board_key": key, "platform": self.platform,
                             "entity_id": body["entity_id"], "entity_name": body["entity_name"],
                             "url": ev["url"]})
        cfg["_discovery"] = {"evidence": evidence, "stale": stale, "untracked_bodies": untracked}
        return listings

    # -- listing -----------------------------------------------------------
    def meeting_detail(self, meeting_id: int, meeting_date: date) -> dict:
        """Detail fragment. Re-read every LISTING_MAX_AGE until a copy fetched after
        the meeting day is cached; that copy is final (agendas cannot change after)."""
        url = detail_url(meeting_id)
        ts = self.fetcher.cached_at(url)
        final = ts is not None and datetime.fromtimestamp(ts, ET).date() > meeting_date
        resp = self.fetcher.get(url, max_age=None if final else LISTING_MAX_AGE)
        if not resp.ok:
            raise FetchError(f"RI SOS meeting {meeting_id} HTTP {resp.status}")
        return parse_meeting_detail(self.soup(resp))

    def meetings(self, cfg: dict, window: Window) -> list[dict]:
        """Every non-cancelled meeting of the town's listed bodies in `window`, with
        its detail (filed times, flags, agenda files). Listings that fail are
        logged and skipped; if all fail, raises RuntimeError."""
        out, errors = [], []
        listings = cfg.get("listings", [])
        for listing in listings:
            try:
                rows = self.body_meetings(listing["entity_id"])
            except FetchError as e:
                errors.append(str(e))
                log.warning("%s %s: %s", cfg["town"], listing["board"], e)
                continue
            for r in rows:
                if r["cancelled"] or r["date"] not in window:
                    continue
                try:
                    det = self.meeting_detail(r["meeting_id"], r["date"])
                except FetchError as e:
                    errors.append(str(e))
                    continue
                if det["annual_calendar"]:
                    continue  # the year's schedule, not a meeting agenda
                hhmm = det["time"] or r["time"]
                out.append({**det, "town": cfg["town"], "board": listing["board"],
                            "board_key": listing["board_key"], "entity_id": listing["entity_id"],
                            "entity_name": listing.get("entity_name") or listing["board"],
                            "meeting_id": r["meeting_id"], "meeting_date": r["date"], "meeting_time": hhmm,
                            "meeting_start": meeting_start(r["date"], hhmm),
                            "listing_url": meeting_page_url(r["meeting_id"])})
        if listings and errors and not out and len(errors) >= len(listings):
            raise RuntimeError(f"all RI SOS listings failed: {errors[0]}")
        cfg.setdefault("_errors", []).extend(errors)
        return out

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        return self.agenda_docs(cfg, self.meetings(cfg, window))

    def agenda_docs(self, cfg: dict, meetings: list[dict]) -> list[AgendaDoc]:
        """One AgendaDoc per uploaded agenda file, earliest-filed first, so hit
        dedupe keeps the version that was public first."""
        docs = []
        for m in meetings:
            files = sorted(m["agendas"], key=lambda f: (f["filed_at"] or m["filed_on"] or m["meeting_start"]))
            first = files[0]["filed_at"] if files else None
            for i, f in enumerate(files):
                filed = f["filed_at"] or m["filed_on"]
                docs.append(AgendaDoc(
                    town=cfg["town"], board=m["board"], board_key=m["board_key"],
                    meeting_date=m["meeting_date"],
                    title=(f"{m['entity_name']} {m['meeting_date'].isoformat()} "
                           f"{'public announcement' if m['public_announcement'] else 'agenda'}"
                           + (f" (filed {filed:%Y-%m-%d %H:%M} ET)" if filed else "")),
                    url=file_url(f["path"]), listing_url=m["listing_url"],
                    extra={"meeting_id": m["meeting_id"], "entity_id": m["entity_id"],
                           "meeting_time": m["meeting_time"],
                           "meeting_start": m["meeting_start"].isoformat(),
                           "notice_filed_at": m["filed_on"].isoformat() if m["filed_on"] else None,
                           "agenda_filed_at": filed.isoformat() if filed else None,
                           "amended": bool(i and f["filed_at"] and first and f["filed_at"] > first),
                           "emergency": m["emergency"], "public_announcement": m["public_announcement"]},
                ))
        return docs
