#!/usr/bin/env python3
"""New York pilot for 351 Watch.

Glue code only: it imports the `watch351` package and reuses its PoliteFetcher
(351WatchBot UA, robots.txt on every hop, 1 req/s/host, crawl-delay cap, cache),
the census discovery engine (`discover_census.discover_municipality`), the
adapters, `crawl.scan_document` (PDF/OCR/HTML extraction) and the keyword
matcher (which includes `data_center`). Nothing in watch351/ is modified; the
New York differences are applied in this process only (see `ny_patches`).

    cd crawler
    python3 experiments/ny_pilot.py get URL [--grep REGEX] [--text N]
    python3 experiments/ny_pilot.py discover [--towns A,B]   # -> data/towns_ny.json
    python3 experiments/ny_pilot.py listings [--towns A,B]   # dry run, no documents
    python3 experiments/ny_pilot.py crawl [--towns A,B]      # -> data/agenda_hits_ny.json

Outputs (projects/351watch/data/):
    towns_ny.json          same row shape as towns_ma_all.json plus "state": "NY" and
                           why the town was chosen (selection_reason / selection_source_url)
    agenda_hits_ny.json    hits in the ARCHITECTURE.md hit shape + per-town status,
                           per-document records and posting lead times
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import statistics
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # crawler/
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from watch351 import boards as _boards  # noqa: E402
from watch351 import discover_census as dc  # noqa: E402
from watch351.adapters import REGISTRY  # noqa: E402
from watch351.adapters.civicplus import CivicPlusAdapter  # noqa: E402
from watch351.crawl import _dedupe, scan_document  # noqa: E402
from watch351.fetch import FetchError, PoliteFetcher  # noqa: E402
from watch351.models import Window  # noqa: E402

import northeast_probe as nep  # noqa: E402  (exploration helper + PDF-date proxy)

DATA = ROOT.parent / "data"
CONFIG = DATA / "towns_ny.json"
HITS = DATA / "agenda_hits_ny.json"
SCRATCH = ROOT / ".cache" / "ny_pilot"          # git-ignored: discovery lead-time rows
STATE = "NY"

log = logging.getLogger("ny_pilot")

CARINA = "https://carina.energy/bess-moratoriums/"

# --------------------------------------------------------------------------
# The towns. Chosen 2026-10-10 from Carina Energy's BESS Moratorium Monitor
# (128 NY rows; NY is ~65% of the national total), town hearing notices and
# news coverage of data-center fights. `why` is the reason, `src` the source.
T = lambda town, county, website, why, src, kind="town": dict(  # noqa: E731
    town=town, county=county, website=website, why=why, src=src, kind=kind)

NY_TOWNS: list[dict] = [
    # ---- Long Island (Suffolk / Nassau)
    T("Southold", "Suffolk", "https://www.southoldtownny.gov",
      "BESS moratorium ACTIVE, expires 2027-04-11 (Carina)", CARINA),
    T("Oyster Bay", "Nassau", "https://www.oysterbaytown.com",
      "BESS moratorium ACTIVE, expires 2027-04-30 (Carina)", CARINA),
    T("North Hempstead", "Nassau", "https://www.northhempsteadny.gov",
      "BESS moratorium ACTIVE, expires 2026-11-18 (Carina) - extension/replacement law due this fall", CARINA),
    T("Smithtown", "Suffolk", "https://www.smithtownny.gov",
      "BESS moratorium ACTIVE, expires 2026-10-20 (Carina) - extension or BESS code due now", CARINA),
    T("Islip", "Suffolk", "https://islipny.gov",
      "BESS moratorium ACTIVE, expired/extended 2026-09-30 (Carina)", CARINA),
    T("Hempstead", "Nassau", "https://hempsteadny.gov",
      "BESS moratorium ACTIVE through 2026-08-25 (Carina)", CARINA),
    T("Huntington", "Suffolk", "https://www.huntingtonny.gov",
      "BESS moratorium ACTIVE through 2026-06-30 (Carina)", CARINA),
    T("Southampton", "Suffolk", "https://www.southamptontownny.gov",
      "BESS moratorium ACTIVE through 2026-06-30 (Carina)", CARINA),
    T("Babylon", "Suffolk", "https://www.townofbabylonny.gov",
      "BESS moratorium ACTIVE through 2026-07-01 (Carina)", CARINA),
    T("Brookhaven", "Suffolk", "https://www.brookhavenny.gov",
      "Data-center moratorium: Introductory Local Law 11 of 2026 (new Chapter 17), hearing 2026-07-16",
      "https://www.brookhavenny.gov/CivicAlerts.aspx?AID=4859"),
    # ---- Westchester / Putnam / Rockland / Orange
    T("Cortlandt", "Westchester", "https://www.townofcortlandtny.gov",
      "BESS moratorium; 2026-07-21 hearing to extend it to 2026-12-31 (Carina: expires 2026-07-31)",
      "https://www.townofcortlandtny.gov/documents/PH-%20Battery%20Storage%20Moratorium%20for%207-21-2026.pdf"),
    T("Bedford", "Westchester", "https://www.bedfordny.gov",
      "BESS moratorium ACTIVE through 2026-08-17 (Carina)", CARINA),
    T("New Castle", "Westchester", "https://www.mynewcastle.org",
      "BESS moratorium ACTIVE through 2026-08-17 (Carina)", CARINA),
    T("Carmel", "Putnam", "https://www.carmelny.org",
      "BESS moratorium ACTIVE, no end date listed (Carina)", CARINA),
    T("Kent", "Putnam", "https://www.townofkentny.gov",
      "BESS moratorium ACTIVE through 2026-08-31 (Carina)", CARINA),
    T("Putnam Valley", "Putnam", "https://www.putnamvalley.com",
      "BESS moratorium ACTIVE through 2026-06-30 (Carina)", CARINA),
    T("Stony Point", "Rockland", "https://www.stonypointny.gov",
      "Eight-month BESS moratorium, public hearing 2026-06-23",
      "https://www.stonypointny.gov/userfiles/notice_of_public_hearing_61026_0282.pdf"),
    T("Chester", "Orange", "https://www.thetownofchester.org",
      "BESS moratorium ACTIVE through 2026-08-26 (Carina)", CARINA),
    # ---- Mid-Hudson / Catskills
    T("Gardiner", "Ulster", "https://www.townofgardiner.org",
      "BESS moratorium ACTIVE through 2026-07-13 (Carina)", CARINA),
    T("Hurley", "Ulster", "https://www.townofhurleyny.gov",
      "BESS moratorium ACTIVE through 2026-06-30 (Carina)", CARINA),
    T("Wawarsing", "Ulster", "https://www.townofwawarsing.net",
      "Temporary BESS moratorium approved late July 2026", "https://wjffradio.org/2026/07/27/"),
    T("Highland", "Sullivan", "https://townofhighlandny.gov",
      "12-month data-center moratorium enacted 2026 (extendable to 24 months)",
      "https://townofhighlandny.gov/?p=6403"),
    T("Stanford", "Dutchess", "https://www.stanfordny.gov",
      "BESS moratorium ACTIVE through 2026-07-01 (Carina)", CARINA),
    T("Beekman", "Dutchess", "https://townofbeekman.gov",
      "Proposed 2026 local law: temporary battery-storage moratorium",
      "https://townofbeekman.gov/wp-content/uploads/2026/01/2026-OBS-Local-Law-Battery-Storage-Moratorium.pdf"),
    T("East Fishkill", "Dutchess", "https://www.eastfishkillny.gov",
      "Three-year data-center freeze adopted June 2026 after Treetop Development's hyperscale proposal",
      "https://www.wamc.org/2026-06-26/east-fishkill-passes-3-year-data-center-freeze"),
    T("Dover", "Dutchess", "https://www.doverny.gov",
      "Northeast feasibility pilot town (CivicClerk); BESS/solar siting activity in eastern Dutchess",
      "research_notes/Meeting monitor deep dive/northeast_feasibility.md (CivicClerk tenant doverny)"),
    T("Claverack", "Columbia", "https://www.claverackny.gov",
      "BESS moratorium (Local Law 2 of 2025), ACTIVE through 2026-06-11 (Carina); solar tracker site plans",
      "https://www.claverackny.gov/DocumentCenter/View/276/75-TOC-LL2-of-2025-BESS-Moratorium-PDF"),
    T("Livingston", "Columbia", "https://www.livingstonny.us",
      "BESS moratorium ACTIVE through 2026-06-01 (Carina)", CARINA),
    # ---- Capital Region / Saratoga / Mohawk Valley
    T("Clifton Park", "Saratoga", "https://cliftonparkny.gov",
      "BESS moratorium (Carina, through 2026-07-19) and a 12-month data storage center moratorium, hearing 2026-07-07",
      "https://cliftonparkny.gov/notice-of-public-hearing-to-consider-a-local-law-establishing-12-month-moratorium-on-the-acceptance-review-and-approval-of-data-storage-center-applications-in-the-town-of-clifton-park"),
    T("Halfmoon", "Saratoga", "https://www.townofhalfmoon-ny.gov",
      "BESS moratorium ACTIVE through 2026-08-31 (Carina)", CARINA),
    T("Milton", "Saratoga", "https://www.townofmiltonny.org",
      "BESS moratorium ACTIVE through 2026-07-29 (Carina)", CARINA),
    T("Wilton", "Saratoga", "https://www.townofwilton.com",
      "BESS moratorium ACTIVE through 2027-06-15 (Carina)", CARINA),
    T("Corinth", "Saratoga", "https://townofcorinthny.gov",
      "One-year BESS moratorium, public hearing 2026-07-09",
      "https://townofcorinthny.gov/images/document/26230944/BESSNoticeofPublicHearing2026--gOfTXl_Tk2dv5-s2NVtEw.pdf"),
    T("Glenville", "Schenectady", "https://www.townofglenville.org",
      "BESS moratorium (Carina, ACTIVE, dated 2025-10-16)", CARINA),
    T("Duanesburg", "Schenectady", "https://www.duanesburg.net",
      "BESS moratorium ACTIVE, no end date listed (Carina)", CARINA),
    T("Berne", "Albany", "https://www.berneny.org",
      "BESS moratorium ACTIVE through 2026-11-06 (Carina)", CARINA),
    T("East Greenbush", "Rensselaer", "https://www.eastgreenbush.org",
      "Town board weighing a data-center moratorium (July 2026)",
      "https://spectrumlocalnews.com/nys/capital-region/business/2026/07/09/east-greenbush-exploring-moratorium-on-data-center-development"),
    T("Amsterdam", "Montgomery", "https://www.townofamsterdam.org",
      "BESS moratorium ACTIVE (Carina 'Amsterdam, Montgomery County'); town BESS hearing notice 2026",
      "https://www.townofamsterdam.org/?p=1590"),
    T("Perth", "Fulton", "https://www.townofperth.org",
      "BESS moratorium ACTIVE through 2027-01-21 (Carina)", CARINA),
    T("Horicon", "Warren", "https://www.horiconny.gov",
      "BESS moratorium public hearing 2026-05-21", "https://www.horiconny.gov/media/2546"),
    T("Winfield", "Herkimer", "https://townofwinfieldny.gov",
      "Local Law 2 of 2026: 12-month data-center moratorium (>=500 kW peak demand)",
      "https://townofwinfieldny.gov/wp-content/uploads/2026/06/Local-Law-No.-2-of-2026_-Data-Center-Moratorium-1.pdf"),
    T("Leyden", "Lewis", "https://townofleydenny.gov",
      "BESS law public hearing 2026-06-09; BESS moratorium ACTIVE through 2026-09-30 (Carina)",
      "https://townofleydenny.gov/application/files/3517/7931/3704/Public_Hearing_Battery_Energy_Storage_Law.pdf"),
    # ---- Central NY / Finger Lakes
    T("Clay", "Onondaga", "https://townofclayny.gov",
      "Local Law 4 of 2026 (BESS siting) hearing; ZBA setback variance for BESS (Micron host town)",
      "https://www.cnycentral.com/news/local/clay-to-hold-public-hearing-on-battery-storage-law"),
    T("Lysander", "Onondaga", "https://lysanderny.gov",
      "BESS moratorium ACTIVE through 2026-12-19 (Carina); data-center moratorium extension hearing 2026-11-05",
      CARINA),
    T("Cicero", "Onondaga", "https://ciceronewyork.net",
      "Local Law 2 of 2026: moratorium on large-scale data centers / AI computing / crypto mining, hearing 2026-07-22",
      "https://ciceronewyork.net/?p=28237"),
    T("Camillus", "Onondaga", "https://www.townofcamillus.com",
      "BESS moratorium ACTIVE through 2027-03-10 (Carina)", CARINA),
    T("Marcellus", "Onondaga", "https://townofmarcellusny.gov",
      "BESS moratorium through 2027-05-06 (Carina); proposed Local Law C-2026 BESS regulations, hearing 2026-10-07",
      "https://townofmarcellusny.gov/?p=9134"),
    T("Spafford", "Onondaga", "https://www.townofspafford.org",
      "BESS moratorium ACTIVE through 2027-06-09 (Carina)", CARINA),
    T("Lansing", "Tompkins", "https://www.lansingtownny.gov",
      "AI data center proposed at the former Cayuga coal plant; town-wide zoning moratorium debate",
      "https://www.wskg.org/regional-news/2025-10-15/lansing-town-board-to-discuss-zoning-moratorium-amid-controversy-over-data-center"),
    T("Geneva", "Ontario", "https://www.townofgeneva.com",
      "New BESS law, public hearing 2026-09-08",
      "https://www.fltimes.com/classifieds/community/announcements/legal/legal-notice-town-of-geneva-notice-of-public-hearing-please-take-notice/ad_8b62553a-333f-5736-93a2-456a9978e496.html"),
    T("Penfield", "Monroe", "https://www.penfield.org",
      "BESS moratorium ACTIVE through 2026-06-30 (Carina)", CARINA),
    T("York", "Livingston", "https://www.yorkny.gov",
      "Local Law 3 of 2026: 12-month data-center moratorium, hearing 2026-07-14",
      "https://www.yorkny.gov/_files/ugd/80e0ed_4d3d2702e62f4be6a44a538127f0dc2b.pdf"),
    # ---- Western NY
    T("Amherst", "Erie", "https://www.amherst.ny.us",
      "Zoning text amendment ZTA-2026-01 for battery energy storage systems, hearing 2026-07-06",
      "https://www.amherst.ny.us/pdf/planning/dev_proj_pending/other/ZTA-2026-01-report-3e4h2h2ke6.pdf"),
    T("Concord", "Erie", "https://www.townofconcordny.gov",
      "BESS moratorium (Carina, through 2026-06-12) and Proposed Local Law 4: one-year data-center moratorium, hearing 2026-07-15",
      "https://www.townofconcordny.gov/files/Public Hearing Data Center 2026.pdf"),
    T("Aurora", "Erie", "https://www.townofaurora.com",
      "BESS moratorium ACTIVE through 2026-06-09 (Carina)", CARINA),
    T("Boston", "Erie", "https://www.townofboston.com",
      "BESS moratorium ACTIVE through 2026-12-03 (Carina)", CARINA),
    T("Newfane", "Niagara", "https://www.townofnewfane.com",
      "BESS moratorium ACTIVE through 2026-08-31 (Carina)", CARINA),
]


# --------------------------------------------------------------------------
# New York patches, applied to this process only.
NY_EXTRA_BOARDS: list[tuple[str, str, str]] = [
    # NY Conservation Advisory Councils / Boards (GML §239-x/y) and environmental boards
    ("conservation_commission",
     r"conservation (advisory )?(council|board)|\bCAC\b|environmental (conservation )?(commission|board|council)|"
     r"conservation advisory|wetlands? (board|commission)",
     r"sub-?committee|district|soil|water|open space|trust|inactive|archive"),
    ("select_board",
     r"^(?:regular |special |agenda[s]?[ :-]*)?town board\b|\btown board (?:meeting|agenda|work session|workshop)s?\b|"
     r"^town council\b",
     r"committee|joint|room|chambers|housing|ethics"),
    ("planning_board", r"^(?:the )?planning board\b|planning (?:board|department) agenda", r"committee|regional|county"),
    ("zoning_board_of_appeals", r"zoning board|board of (?:zoning )?appeals|\bZBA\b", r"committee"),
]
_stock_classify = _boards.classify_board


def classify_ny(name: str) -> str | None:
    k = _stock_classify(name)
    if k:
        return k
    n = " ".join(name.split())
    if re.search(r"zzz|inactive|archive|minutes only", n, re.I):
        return None
    for key, inc, exc in NY_EXTRA_BOARDS:
        if re.search(inc, n, re.I) and not re.search(exc, n, re.I):
            return key
    return None


def _site_root(host: str) -> str:
    host = host.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if re.search(r"\.[a-z]{2}\.us$", host) and len(parts) >= 3:   # town.wawarsing.ny.us, amherst.ny.us
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def ny_patches() -> None:
    """Teach the census discovery engine NY board names and hosts."""
    dc.classify_board = classify_ny
    dc.site_root = _site_root
    hub = dict(dc.HUB_BOARD_RX)
    inc, exc = hub["select_board"]
    hub["select_board"] = (inc + r"|\btown board\b", exc + r"|town board (?:meeting )?(?:room|chambers)")
    inc, exc = hub["conservation_commission"]
    hub["conservation_commission"] = (inc + r"|\bCAC\b|environmental (?:conservation )?(?:commission|board|council)",
                                      exc + r"|soil|water")
    inc, exc = hub["planning_board"]
    hub["planning_board"] = (inc, exc)
    dc.HUB_BOARD_RX.clear()
    dc.HUB_BOARD_RX.update(hub)
    dc.SLUG_HINTS["select_board"] += r"|town[-_ ]?board"
    dc.SLUG_HINTS["conservation_commission"] += r"|conservation[-_ ]advisory|conservation[-_ ]board|/cac\b|environmental[-_ ]board"
    dc.SLUG_HINTS["zoning_board_of_appeals"] += r"|/zoning[-_ ]?board"
    dc.OTHER_BODY = re.compile(dc.OTHER_BODY.pattern + r"|town board (?:meeting )?(?:room|chambers)", re.I)


class NYFetcher(PoliteFetcher):
    """discover_census probes CivicClerk tenant '<town>ma'; for New York the
    tenant convention is '<town>ny' (e.g. doverny). Rewrite only that probe
    (the one request that carries params {'$top': '1'})."""

    def get(self, url, max_age=None, params=None):
        if params == {"$top": "1"}:
            m = re.match(r"https://([a-z]+)ma\.api\.civicclerk\.com/v1/Events$", url)
            if m:
                url = f"https://{m.group(1)}ny.api.civicclerk.com/v1/Events"
        return super().get(url, max_age=max_age, params=params)


# --------------------------------------------------------------------------
# Hand-curated facts from manual inspection with 351WatchBot. Applied on top of
# the automatic discovery result. `listings` are watch351 `generic` listings
# unless the platform says otherwise.
def _gl(board, key_, url, pattern, exclude=None, **kw):
    d = {"board": board, "board_key": key_, "url": url, "link_pattern": pattern}
    if exclude:
        d["exclude_pattern"] = exclude
    d.update(kw)
    return d


_CLAY = "https://townofclayny.gov/minutes-agendas?field_board_value="
CURATED: dict[str, dict] = {
    "Clay": {"platform": "generic", "agenda_platform": "Drupal", "automated": True,
             "note": "?field_board_value does not filter the 'recent agendas' block; each listing also matches "
                     "the board name in the file name.",
             "listings": [
                 _gl("Planning Board", "planning_board", _CLAY + "Planning%20Board", r"View Agenda.*Planning"),
                 _gl("Zoning Board of Appeals", "zoning_board_of_appeals", _CLAY + "Zoning%20Board%20of%20Appeals",
                     r"View Agenda.*(Zoning|ZBA)"),
                 _gl("Town Board", "select_board", _CLAY + "Town%20Board", r"View Agenda.*Town"),
             ]},
}


# --------------------------------------------------------------------------
def load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def select(rows: list[dict], names: str | None) -> list[dict]:
    if not names:
        return rows
    wanted = {n.strip().lower() for n in names.split(",")}
    return [r for r in rows if r["town"].lower() in wanted]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ discover
def apply_curated(rec: dict) -> dict:
    cur = CURATED.get(rec["town"], {})
    if not cur:
        return rec
    rec.update({k: v for k, v in cur.items() if k not in ("listings", "drop_listings", "add_listings")})
    if "listings" in cur:
        rec["listings"] = cur["listings"]
    if cur.get("add_listings"):
        have = {(l["board_key"], l["url"]) for l in rec.get("listings", [])}
        rec["listings"] = rec.get("listings", []) + [l for l in cur["add_listings"]
                                                      if (l["board_key"], l["url"]) not in have]
    if cur.get("drop_listings"):
        rec["listings"] = [l for l in rec.get("listings", []) if not re.search(cur["drop_listings"], l["board"], re.I)]
    if rec.get("automated"):
        rec["status"], rec["reason_code"], rec["reason"] = "automated", None, None
        rec["boards_found"] = sorted({l["board_key"] for l in rec.get("listings", [])})
        rec["boards_missing"] = [k for k in dc.TRACKED[:4] if k not in rec["boards_found"]]
    else:
        rec["status"] = "not_automated"
        rec["listings"] = []
    rec["curated"] = True
    return rec


def discover_one(fetcher: PoliteFetcher, t: dict) -> dict:
    muni = {"town": t["town"], "website": t["website"], "county": t["county"], "kind": t["kind"],
            "legislative_body": "Town Board" if t["kind"] == "town" else "Council",
            "pop_2020": None, "pop_2024_est": None}
    try:
        rec = dc.discover_municipality(fetcher, muni)
    except Exception as e:  # noqa: BLE001 - one bad site must not stop the census
        log.exception("%s: discovery crashed", t["town"])
        rec = {"town": t["town"], "website": t["website"], "county": t["county"], "kind": t["kind"],
               "status": "not_automated", "reason_code": "discovery_error", "reason": f"discovery error: {e}"[:200],
               "automated": False, "listings": [], "_leadtime_rows": []}
    lead = rec.pop("_leadtime_rows", [])
    rec = {"town": rec["town"], "state": STATE, **{k: v for k, v in rec.items() if k != "town"}}
    rec["selection_reason"] = t["why"]
    rec["selection_source_url"] = t["src"]
    rec = apply_curated(rec)
    return rec | {"_lead": lead}


def cmd_discover(args, fetcher: PoliteFetcher) -> None:
    ny_patches()
    conf = load(CONFIG, {"towns": []})
    by_town = {t["town"]: t for t in conf.get("towns", [])}
    todo = select(NY_TOWNS, args.towns)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        out = list(pool.map(lambda t: discover_one(fetcher, t), todo))
    lead_all = load(SCRATCH / "leadtime_rows.json", {})
    for rec in out:
        lead_all[rec["town"]] = rec.pop("_lead")
        by_town[rec["town"]] = rec
    save(SCRATCH / "leadtime_rows.json", lead_all)
    rows = [by_town[t["town"]] for t in NY_TOWNS if t["town"] in by_town]
    conf = {
        "_about": "351 Watch New York pilot: agenda platform and crawlable listing per tracked board (with "
                  "evidence: agendas dated within the last 120 / next 120 days), or the precise reason a town is "
                  "not automated. Same per-town schema as towns_ma_all.json plus state and why the town was "
                  "chosen. Built by `python3 experiments/ny_pilot.py discover` (watch351.discover_census with NY "
                  "board names: Town Board -> select_board, Conservation Advisory Council/Board -> "
                  "conservation_commission).",
        "generated": now_iso(),
        "state": STATE,
        "boards_tracked": dc.TRACKED[:4],
        "board_key_mapping": {"Town Board": "select_board", "Planning Board": "planning_board",
                              "Zoning Board of Appeals": "zoning_board_of_appeals",
                              "Conservation Advisory Council / Conservation Board": "conservation_commission"},
        "evidence_rule": "board automated only if its listing shows >=1 agenda dated in [today-120d, today+120d]",
        "count": len(rows),
        "automated": sum(1 for r in rows if r.get("automated")),
        "towns": rows,
    }
    save(CONFIG, conf)
    for r in out:
        print(f"{r['town']:<16} {str(r.get('platform')):<11} {'AUTO' if r.get('automated') else 'no  '} "
              f"boards={r.get('boards_found')} cms={r.get('cms')} vend={list((r.get('vendors') or {}).keys())} "
              f"{'' if r.get('automated') else (r.get('reason_code') or '') + ': ' + str(r.get('reason'))[:150]}")
    print(f"automated {conf['automated']}/{conf['count']}")


# ------------------------------------------------------------------ crawl
def civicplus_posted(fetcher: PoliteFetcher, cfg: dict, window: Window) -> dict[str, dict]:
    cp = CivicPlusAdapter(fetcher)
    website = cfg["website"].rstrip("/")
    cids = [l["category_id"] for l in cfg.get("listings", []) if l.get("category_id")]
    if not cids:
        return {}
    resp = cp.get_listing(f"{website}/AgendaCenter/Search/", params={
        "term": "", "CIDs": ",".join(cids) + ",",
        "startDate": window.start.strftime("%m/%d/%Y"), "endDate": window.end.strftime("%m/%d/%Y"),
        "dateRange": "", "dateSelector": ""})
    out = {}
    for r in dc.civicplus_rows(resp):
        if r.get("posted"):
            out[r["url"]] = {r["posted_kind"]: r["posted"]}
    return out


def civicclerk_published(fetcher: PoliteFetcher, cfg: dict, window: Window) -> dict[str, dict]:
    ad = REGISTRY["civicclerk"](fetcher)
    out = {}
    for ev in ad.events(cfg, window):
        for f in ev.get("publishedFiles", []):
            if (f.get("type") or "").lower() == "agenda" and f.get("publishOn"):
                url = f"{ad._api(cfg)}/Meetings/GetMeetingFileStream(fileId={f['fileId']},plainText=false)"
                out[url] = {"published": f["publishOn"].replace("Z", "")[:19],
                            "meeting_start": ev.get("startDateTime", "").replace("Z", "")[:19]}
    return out


def crawl_one(fetcher: PoliteFetcher, cfg: dict, window: Window) -> dict:
    res = {"town": cfg["town"], "county": cfg.get("county"), "platform": cfg.get("platform"),
           "automated": bool(cfg.get("automated")), "reason_code": cfg.get("reason_code"),
           "reason": cfg.get("reason"), "agendas_listed": 0, "documents_scanned": 0,
           "documents_without_text_layer": 0, "documents_ocr": 0, "errors": [], "docs": [], "hits": []}
    if not cfg.get("automated"):
        return res
    adapter = REGISTRY[cfg["platform"]](fetcher)
    try:
        docs = adapter.list_agendas(cfg, window)
    except (FetchError, RuntimeError, ValueError) as e:
        res["errors"].append(f"listing: {e}"[:300])
        return res
    res["agendas_listed"] = len(docs)
    stamps: dict[str, dict] = {}
    try:
        if cfg["platform"] == "civicplus":
            stamps = civicplus_posted(fetcher, cfg, window)
        elif cfg["platform"] == "civicclerk":
            stamps = civicclerk_published(fetcher, cfg, window)
    except (FetchError, RuntimeError, ValueError) as e:
        res["errors"].append(f"posted-times: {e}"[:200])
    for doc in docs:
        rec = {"board": doc.board, "board_key": doc.board_key,
               "meeting_date": doc.meeting_date.isoformat() if doc.meeting_date else None,
               "title": doc.title, "url": doc.url, "listing_url": doc.listing_url}
        rec.update(stamps.get(doc.url, {}))
        m = dc.REVIZE_TS.search(doc.url)
        if m:
            rec["uploaded"] = datetime.strptime(m.group(1), "%Y%m%d%H%M%S").isoformat()
        try:
            hits, ex = scan_document(fetcher, doc)
        except FetchError as e:
            res["errors"].append(str(e)[:200])
            rec["error"] = str(e)[:200]
            res["docs"].append(rec)
            continue
        ts = fetcher.cached_at(doc.url)
        rec["first_fetched"] = datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds") if ts else now_iso()
        if not any(k in rec for k in ("posted", "published", "uploaded")) and not doc.resolve_pdf:
            rec.update(nep.pdf_dates(fetcher, doc.url))
        rec.update(pages=ex.pages, scanned=ex.scanned, ocr=ex.ocr, hits=len(hits), text_chars=len(ex.text or ""))
        res["docs"].append(rec)
        res["documents_scanned"] += 1
        res["documents_without_text_layer"] += int(ex.scanned)
        res["documents_ocr"] += int(ex.ocr)
        for h in hits:
            h["_first_fetched"] = rec["first_fetched"]
            for k in ("posted", "published", "amended", "uploaded"):
                if k in rec:
                    h[f"_{k}"] = rec[k]
        res["hits"].extend(hits)
    log.info("%s: %d listed, %d scanned, %d hits", cfg["town"], res["agendas_listed"],
             res["documents_scanned"], len(res["hits"]))
    return res


def _days(meeting: str, stamp: str) -> float:
    """Lead time from a timestamp to the start (00:00) of the meeting day."""
    md = datetime.fromisoformat(meeting)
    st = datetime.fromisoformat(stamp[:19])
    return round((md - st).total_seconds() / 86400, 2)


def finalize_hit(h: dict, county: str | None) -> dict:
    first = h.pop("_first_fetched")
    out = {
        "id": hashlib.sha1(f"{h['source_url']}|{h['snippet']}".encode()).hexdigest()[:12],
        "state": STATE, "town": h["town"], "county": county, "board": h["board"], "board_key": h["board_key"],
        "meeting_date": h["meeting_date"], "topics": h["topics"], "snippet": h["snippet"],
        "source_url": h["source_url"], "listing_url": h["listing_url"], "document_title": h["document_title"],
        "text_source": h["text_source"], "first_seen": first, "days_before_meeting": None, "source": "agenda",
    }
    if h["meeting_date"]:
        seen = datetime.fromisoformat(first)
        meeting = datetime.fromisoformat(h["meeting_date"]).replace(tzinfo=timezone.utc)
        out["days_before_meeting"] = round((meeting - seen).total_seconds() / 86400, 1)
    for k in ("posted", "published", "amended", "uploaded"):
        if f"_{k}" in h:
            out[f"platform_{k}"] = h.pop(f"_{k}")
    return out


def dist(xs: list[float]) -> dict:
    if not xs:
        return {"n": 0}
    xs = sorted(xs)
    q = lambda p: xs[min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))]  # noqa: E731
    return {"n": len(xs), "median": round(statistics.median(xs), 2), "p10": q(0.10), "p25": q(0.25),
            "p75": q(0.75), "p90": q(0.90), "min": xs[0], "max": xs[-1],
            "share_ge_3d": round(sum(1 for x in xs if x >= 3) / len(xs), 3),
            "share_ge_7d": round(sum(1 for x in xs if x >= 7) / len(xs), 3),
            "share_lt_1d": round(sum(1 for x in xs if x < 1) / len(xs), 3)}


def cmd_crawl(args, fetcher: PoliteFetcher) -> None:
    conf = load(CONFIG, {"towns": []})
    towns = select(conf["towns"], args.towns)
    today = date.today()
    window = Window(today - timedelta(days=args.days_back), today + timedelta(days=args.days_ahead))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda c: crawl_one(fetcher, c, window), towns))
    county = {r["town"]: r.get("county") for r in towns}
    hits = _dedupe([h for r in results for h in r["hits"]])
    hits = [finalize_hit(h, county.get(h["town"])) for h in hits]
    hits.sort(key=lambda h: (h["meeting_date"] or "", h["town"], h["board"]), reverse=True)

    # posting lead times: platform stamps for documents in the crawl window ...
    lead_window = []
    for r in results:
        for d in r["docs"]:
            if not d.get("meeting_date"):
                continue
            for kind in ("posted", "published", "uploaded"):
                if d.get(kind):
                    lead_window.append({"town": r["town"], "platform": r["platform"], "board": d["board"],
                                        "meeting_date": d["meeting_date"], "stamp_kind": kind, "stamp": d[kind],
                                        "lead_days": _days(d["meeting_date"], d[kind]), "url": d["url"]})
                    break
    # ... the PDF-metadata proxy where no platform stamp exists ...
    proxy = []
    for r in results:
        for d in r["docs"]:
            st = d.get("pdf_modified") or d.get("pdf_created")
            if d.get("meeting_date") and st and not any(d.get(k) for k in ("posted", "published", "uploaded")):
                try:
                    proxy.append({"town": r["town"], "board": d["board"], "meeting_date": d["meeting_date"],
                                  "lead_days": _days(d["meeting_date"], st.replace("Z", "")[:19])})
                except ValueError:
                    pass
    # ... and a year of platform history gathered during discovery.
    history = []
    lead_rows = load(SCRATCH / "leadtime_rows.json", {})
    for town, rows in lead_rows.items():
        if args.towns and town.lower() not in {n.strip().lower() for n in args.towns.split(",")}:
            continue
        for row in rows:
            if row.get("posted") and row.get("meeting_date") and row.get("posted_kind") != "amended":
                try:
                    history.append({"town": town, "platform": row["platform"], "kind": row["posted_kind"],
                                    "meeting_date": row["meeting_date"], "posted": row["posted"],
                                    "lead_days": _days(row["meeting_date"], row["posted"]),
                                    "board_key": row.get("board_key")})
                except ValueError:
                    pass
    # first_seen lead (our own fetch) for upcoming meetings only
    upcoming = [h["days_before_meeting"] for h in hits if h["days_before_meeting"] is not None
                and h["meeting_date"] >= today.isoformat()]

    by_platform = defaultdict(lambda: {"automated": [], "not_automated": []})
    for r, cfg in zip(results, towns):
        by_platform[cfg.get("platform") or cfg.get("reason_code") or "unknown"][
            "automated" if r["automated"] else "not_automated"].append(r["town"])
    report = {
        "generated": now_iso(),
        "state": STATE,
        "window": {"start": window.start.isoformat(), "end": window.end.isoformat()},
        "towns_attempted": len(results),
        "towns_automated": sum(r["automated"] for r in results),
        "documents_scanned": sum(r["documents_scanned"] for r in results),
        "documents_without_text_layer": sum(r["documents_without_text_layer"] for r in results),
        "documents_ocr": sum(r["documents_ocr"] for r in results),
        "hits_by_topic": dict(Counter(t for h in hits for t in h["topics"]).most_common()),
        "hits_by_board": dict(Counter(h["board_key"] for h in hits).most_common()),
        "towns_by_platform": dict(by_platform),
        "lead_time": {
            "note": "days from a timestamp to 00:00 of the meeting day (an underestimate for evening meetings). "
                    "platform_window: CivicPlus 'Posted' / CivicClerk publishOn stamps for agendas in the crawl "
                    "window; platform_365d: same stamps for every agenda of the past year seen during discovery; "
                    "pdf_proxy: PDF ModDate/CreationDate (when the file was last saved, not posted); "
                    "first_seen_upcoming: our own first fetch vs. meeting day, upcoming meetings only.",
            "platform_window": dist([x["lead_days"] for x in lead_window]),
            "platform_365d": dist([x["lead_days"] for x in history]),
            "platform_365d_by_platform": {p: dist([x["lead_days"] for x in history if x["platform"] == p])
                                          for p in sorted({x["platform"] for x in history})},
            "platform_365d_by_town": {t: dist([x["lead_days"] for x in history if x["town"] == t])
                                      for t in sorted({x["town"] for x in history})},
            "pdf_proxy": dist([x["lead_days"] for x in proxy]),
            "first_seen_upcoming": dist(upcoming),
        },
        "towns": [{k: v for k, v in r.items() if k not in ("hits", "docs")}
                  | {"hits": sum(1 for h in hits if h["town"] == r["town"]), "errors": r["errors"][:10]}
                  for r in results],
        "hits": hits,
        "posting_lead_times": sorted(lead_window, key=lambda x: (x["town"], x["meeting_date"])),
        "documents": [{"town": r["town"], **d} for r in results for d in r["docs"]],
    }
    save(Path(args.out), report)
    print(f"towns {report['towns_attempted']} automated {report['towns_automated']} docs "
          f"{report['documents_scanned']} (no text {report['documents_without_text_layer']}, ocr "
          f"{report['documents_ocr']}) hits {len(hits)}")
    print("topics", report["hits_by_topic"])
    print("lead", json.dumps(report["lead_time"]["platform_window"]), json.dumps(report["lead_time"]["platform_365d"]))
    for r in report["towns"]:
        if r["automated"]:
            print(f"  {r['town']:<16} listed {r['agendas_listed']:>3} scanned {r['documents_scanned']:>3} "
                  f"hits {r['hits']:>3} err {len(r['errors'])} {r['errors'][:1]}")
    print(f"fetcher: {fetcher.stats}")


def cmd_listings(args, fetcher: PoliteFetcher) -> None:
    conf = load(CONFIG, {"towns": []})
    today = date.today()
    window = Window(today - timedelta(days=args.days_back), today + timedelta(days=args.days_ahead))
    for cfg in select(conf["towns"], args.towns):
        if not cfg.get("automated"):
            print(f"{cfg['town']}: NOT automated ({cfg.get('reason')})")
            continue
        try:
            docs = REGISTRY[cfg["platform"]](fetcher).list_agendas(cfg, window)
        except (FetchError, RuntimeError, ValueError) as e:
            print(f"{cfg['town']}: listing error {e}")
            continue
        print(f"{cfg['town']} [{cfg['platform']}]: {len(docs)} docs")
        for d in docs[: args.limit]:
            print(f"   {d.meeting_date} {d.board[:28]:<28} {d.title[:50]:<50} {d.url[:110]}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["get", "discover", "listings", "crawl"])
    p.add_argument("url", nargs="?")
    p.add_argument("--grep")
    p.add_argument("--limit", type=int, default=60)
    p.add_argument("--text", type=int, default=0)
    p.add_argument("--towns")
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=90)
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--out", default=str(HITS))
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    log.setLevel(logging.INFO)
    fetcher = NYFetcher()
    if args.command == "get":
        nep.cmd_get(args, fetcher)
    else:
        {"discover": cmd_discover, "listings": cmd_listings, "crawl": cmd_crawl}[args.command](args, fetcher)
    return 0


if __name__ == "__main__":
    sys.exit(main())
