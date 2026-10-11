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
    T("Warwick", "Orange", "https://townofwarwickny.gov",
      "Draft BESS local law (rev. 2026-06-30) after the 2025 BESS moratorium (Carina: expired 2025-06-03)",
      "https://townofwarwickny.gov/t-warwick-bess-law-rek-rev-06302026-draft-docx/"),
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
    T("Livingston", "Columbia", "https://townoflivingston.org",
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
    T("Perth", "Fulton", "https://www.perthny.gov",
      "BESS moratorium ACTIVE through 2027-01-21 (Carina); Fulton County Planning Board 239 review of the Perth renewable-energy/BESS moratorium, 2026-01-20",
      "https://www.fultoncountyny.gov/sites/default/files/_planning/PB-2026-01-20.pdf"),
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
    T("Spafford", "Onondaga", "https://www.townofspaffordny.gov",
      "BESS moratorium ACTIVE through 2027-06-09 (Carina)", CARINA),
    T("Lansing", "Tompkins", "https://www.lansingtownny.gov",
      "AI data center proposed at the former Cayuga coal plant; town-wide zoning moratorium debate",
      "https://www.wskg.org/regional-news/2025-10-15/lansing-town-board-to-discuss-zoning-moratorium-amid-controversy-over-data-center"),
    T("Geneva", "Ontario", "https://townofgenevany.gov",
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
_MDY = r"^(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.? \d{1,2}, 20\d\d\b"
_STAN = "https://stanfordny.gov/advisory-committees/town-laws/minsagenda/"
_WIL = "https://townofwilton.ny.gov/government/meeting-agendas/?board="
_AUR = "https://www.townofaurorany.gov/meetings-and-minutes/"
_ESC = "https://pub-southamptonny.escribemeetings.com/"
_PEN = "https://www.penfieldny.gov/online_documents/agendas,_minutes_and_notices/"
_JS_MW = ("the Agendas & Minutes page is a JavaScript-built document module (page sections are filled client-side "
          "from JSON; the server HTML has no agenda links or dates)")


def _ny(board, key_, url, pattern, **kw):
    """A generic_ny listing (see watch351/adapters/generic_ny.py)."""
    return _gl(board, key_, url, pattern, platform="generic_ny", **kw)


def _not(code, reason, platform=None, agenda_platform=None):
    d = {"automated": False, "reason_code": code, "reason": reason}
    if platform:
        d["platform"] = platform
    if agenda_platform:
        d["agenda_platform"] = agenda_platform
    return d


CF = "Cloudflare bot challenge ('Just a moment...', HTTP 403) on the town site for 351WatchBot; not bypassed"
CURATED: dict[str, dict] = {
    # ---------------- Long Island
    "Oyster Bay": {"automated": True, "agenda_platform": "WordPress (date-linked PDFs)",
                   "note": "No Planning Board: site plans and zoning go to the Town Board. Town Board rows also "
                           "link 'Adopted Resolutions' and 'Minutes'; only the date-named calendar PDF is taken.",
                   "listings": [
                       _ny("Town Board", "select_board", "https://oysterbaytown.com/calendars/town-board-meetings/", _MDY),
                       _ny("Zoning Board of Appeals", "zoning_board_of_appeals",
                           "https://oysterbaytown.com/calendars/zoning-board-of-appeals/", _MDY)]},
    "Hempstead": {"agenda_platform": "CivicPlus AgendaCenter (Town Board) + CivicPlus pages (BZA hearing calendars)",
                  "note": "Planning Board page lists members only (no agendas).",
                  "add_listings": [_ny("Board of Appeals", "zoning_board_of_appeals",
                                       "https://hempsteadny.gov/509/Board-of-Appeals", r"^Hearing - \d")]},
    "Southampton": {"automated": True, "platform": "escribe", "agenda_platform": "eSCRIBE (pub-southamptonny.escribemeetings.com)",
                    "note": "Agendas are on eSCRIBE (new adapter `escribe`, upcoming meetings only). eSCRIBE's PDF "
                            "downloads (FileStream.ashx) answer HTTP 403 with a 'Verifying your browser' challenge, "
                            "which is not solved; the portal's own HTML agenda view (Meeting.aspx?...&Agenda=Agenda) "
                            "is served without a challenge and is read instead (flagged for review). The older iQM2 "
                            "portal answers HTTP 429 to automated requests and is not used. The Zoning Board of "
                            "Appeals is not published on eSCRIBE.",
                    "listings": [
                        {"board": "Town Board", "board_key": "select_board", "url": _ESC, "platform": "escribe",
                         "meeting_type": r"^Town Board", "format": "html"},
                        {"board": "Planning Board", "board_key": "planning_board", "url": _ESC, "platform": "escribe",
                         "meeting_type": r"^Planning Board", "format": "html"},
                        {"board": "Conservation Board", "board_key": "conservation_commission", "url": _ESC,
                         "platform": "escribe", "meeting_type": r"^Conservation Board", "format": "html"}]},
    "Huntington": _not("crawl_delay_exceeds_cap", "huntingtonny.gov robots.txt sets Crawl-delay: 15 for all agents; "
                       "351WatchBot skips hosts asking for more than 10 s. Automatable at 1 request per 15 s if the cap "
                       "is raised.", agenda_platform="unknown (site not fetched)"),
    "Islip": _not("bot_challenge", CF, agenda_platform="unknown (behind Cloudflare)"),
    "Brookhaven": _not("bot_challenge", CF + ". Its data-center moratorium (Intro LL 11 of 2026) cannot be followed "
                       "from the town site.", agenda_platform="CivicPlus (behind Cloudflare)"),
    # ---------------- Westchester / Putnam / Rockland / Orange
    "New Castle": _not("vendor_robots_disallow",
                       "Agendas, minutes and packets are hosted on eCode360 (ecode360.com/documents/pub/NE0395/Agendas/), "
                       "whose robots.txt disallows /documents for all agents (verified with 351WatchBot 2026-10-10).",
                       platform="ecode360", agenda_platform="CivicPlus CMS + eCode360 document hosting (General Code)"),
    "Carmel": _not("tls_error",
                   "carmelny.org serves a TLS certificate that does not match the host (hostname mismatch), so "
                   "robots.txt cannot be read over a verified connection; host skipped (TLS verification is never disabled).",
                   agenda_platform="unknown (site not fetched)"),
    "Putnam Valley": {"automated": True, "platform": "generic_ny", "agenda_platform": "WordPress",
                      "note": "Town Board agenda packets ('with supporting documents') only; Planning Board and ZBA pages "
                              "post application files, not agendas.",
                      "listings": [
                          _ny("Town Board", "select_board", "https://www.putnamvalley.gov/agenda-documents/", r"Town Board"),
                          _ny("Town Board", "select_board", "https://www.putnamvalley.gov/town-board-pv/",
                              r"Town Board.*(?:Agenda|MEETING|WORK SESSION|Session)", doc_href=r"\.pdf")]},
    "Stony Point": {"automated": True, "platform": "generic_ny", "agenda_platform": "custom CMS (month-paged agenda list)",
                    "note": "Only Town Board packets are posted; Planning Board and ZBA appear only on the calendar.",
                    "listings": [_ny("Town Board", "select_board",
                                     "https://www.stonypointny.gov/meeting-agendas?m={m}&y={y}", _MDY,
                                     months=True, doc_href=r"/userfiles/")]},
    "Warwick": {"automated": True, "platform": "generic_ny", "agenda_platform": "WordPress (posts per agenda / legal notice)",
                "note": "Tentative Town Board agendas and ZBA legal notices are WordPress posts; the post page is read "
                        "(or its PDF, when it links one).",
                "listings": [
                    _ny("Town Board", "select_board", "https://townofwarwickny.gov/", r"agenda|ZBA LEGAL NOTICE",
                        resolve_pdf=True, board_rules=[[r"ZBA|zoning board", "Zoning Board of Appeals", "zoning_board_of_appeals"],
                                                       [r"planning board", "Planning Board", "planning_board"],
                                                       [r"agenda", "Town Board", "select_board"]],
                        doc_href=r"townofwarwickny\.gov/(?!events)"),
                    _ny("Town Board", "select_board", "https://townofwarwickny.gov/tb-agendas/", r"agenda",
                        resolve_pdf=True, doc_href=r"/tb-agendas/.+")]},
    # ---------------- Mid-Hudson
    "Gardiner": _not("vendor_robots_disallow",
                     "Agendas & Minutes (/agendas-minutes) is a HeyGov widget rendered client-side from api.heygov.com, "
                     "whose robots.txt disallows all bots.", platform="heygov",
                     agenda_platform="TownWeb site + HeyGov meetings"),
    "Hurley": _not("bot_challenge", CF), "Wawarsing": _not("bot_challenge", CF),
    "Highland": _not("no_agendas_online",
                     "Board pages (Town, Planning, Zoning) post no agendas: Town Board meetings appear only as "
                     "'hybrid meeting information' news posts and the site keeps minutes only.",
                     platform="generic", agenda_platform="WordPress"),
    "Stanford": {"automated": True, "platform": "generic_ny", "agenda_platform": "WordPress + Download Monitor",
                 "note": "Download links carry a per-page-load '?tmstv=' cache-buster, stripped so documents cache.",
                 "listings": [
                     _ny("Town Board", "select_board", _STAN + "agenda-archives/", r"^20\d\d-\d\d-\d\d", strip_query=True),
                     _ny("Planning Board", "planning_board", _STAN + "planning-board-agendas-archives/", r"^20\d\d-\d\d-\d\d",
                         strip_query=True),
                     _ny("Zoning Board of Appeals", "zoning_board_of_appeals", _STAN + "zba-agenda-archives/",
                         r"^20\d\d-\d\d-\d\d", strip_query=True),
                     _ny("Conservation Advisory Commission", "conservation_commission",
                         _STAN + "conservation-advisory-committee-archives/", r"^20\d\d-\d\d-\d\d", strip_query=True)]},
    "East Fishkill": {"note": "Town Board agendas on the town page stop in April 2026; later ones are on Granicus "
                              "(eastfishkillny.granicus.com), whose robots.txt disallows 351WatchBot. Only the ZBA is read."},
    "Livingston": _not("undecodable_response",
                       "townoflivingston.org (Sucuri + Cloudflare front end) returns a body that is not decodable HTML "
                       "to 351WatchBot; no agenda listing could be read. Not pursued.", agenda_platform="unknown"),
    # ---------------- Capital Region / Saratoga / Mohawk
    "Halfmoon": _not("bot_challenge", CF), "Duanesburg": _not("bot_challenge", CF), "Horicon": _not("bot_challenge", CF),
    "Milton": {"automated": True, "platform": "generic_ny", "agenda_platform": "Revize",
               "note": "Planning Board agendas only. Town Board folders hold minutes and resolutions, ZBA folders hold "
                       "project files, no agendas. Rows show a 'document date', kept as the posted date.",
               "listings": [_ny("Planning Board", "planning_board",
                                "https://www.miltonny.gov/supervisor___town_boards/planning_board/meeting_schedules_agenda___minutes.php",
                                r"Planning Board Agenda", strip_query=True,
                                posted_regex=r"document date (\d{2}-\d{2}-20\d\d)")]},
    "Wilton": {"automated": True, "platform": "generic_ny", "agenda_platform": "custom CMS (agenda attachment pages)",
               "listings": [
                   _ny("Town Board", "select_board", _WIL + "Town-Board", r"^(?:Agenda|Document|Public Hearing) ", resolve_pdf=True),
                   _ny("Planning Board", "planning_board", _WIL + "Planning-Board", r"^(?:Agenda|Document|Public Hearing) ",
                       resolve_pdf=True),
                   _ny("Zoning Board of Appeals", "zoning_board_of_appeals", _WIL + "Zoning-Board-of-Appeals",
                       r"^(?:Agenda|Document|Public Hearing) ", resolve_pdf=True)]},
    "Corinth": {"automated": True, "platform": "generic_ny", "agenda_platform": "custom CMS (homepage meeting list)",
                "note": "The bare homepage is a JavaScript language redirect to /en/; /en/ lists upcoming meetings with "
                        "their agenda PDFs.",
                "listings": [_ny("Town Board", "select_board", "https://townofcorinthny.gov/en/",
                                 r"Meeting|Agenda|Workshop|Hearing", doc_href=r"/images/document/",
                                 board_rules=[[r"planning", "Planning Board", "planning_board"],
                                              [r"zoning", "Zoning Board of Appeals", "zoning_board_of_appeals"],
                                              [r"town board", "Town Board", "select_board"]])]},
    "Berne": _not("no_agendas_online", "Town Board page posts resolutions and annual documents; Planning and Zoning "
                  "pages post minutes only. No agendas online.", platform="generic", agenda_platform="WordPress"),
    "Perth": _not("js_only", _JS_MW, agenda_platform="JavaScript CMS (agendasandminutes module)"),
    "Winfield": _not("no_agendas_online", "Only Town Board minutes are posted (no agendas); the data-center "
                     "moratorium appears as a public-hearing notice post.", platform="generic", agenda_platform="WordPress"),
    "Leyden": {"automated": True, "platform": "generic_ny", "agenda_platform": "custom CMS (meeting detail pages)",
               "note": "Each meeting has an HTML detail page; the page text is scanned.",
               "listings": [
                   _ny("Town Board", "select_board", "https://townofleydenny.gov/meetings/meetings/Town%20Board/{year}",
                       r"^[A-Z][a-z]+ \d{1,2}, 20\d\d:", exclude_pattern=r"minutes|assessment review"),
                   _ny("Planning Board", "planning_board",
                       "https://townofleydenny.gov/meetings/meetings/Planning%20Board/{year}", r"^[A-Z][a-z]+ \d{1,2}, 20\d\d:")]},
    # ---------------- Central NY / Finger Lakes
    "Clay": {"platform": "generic", "agenda_platform": "Drupal", "automated": True,
             "note": "?field_board_value does not filter the 'recent agendas' block; each listing also matches "
                     "the board name in the file name.",
             "listings": [
                 _gl("Planning Board", "planning_board", _CLAY + "Planning%20Board", r"View Agenda.*Planning"),
                 _gl("Zoning Board of Appeals", "zoning_board_of_appeals", _CLAY + "Zoning%20Board%20of%20Appeals",
                     r"View Agenda.*(Zoning|ZBA)"),
                 _gl("Town Board", "select_board", _CLAY + "Town%20Board", r"View Agenda.*Town"),
             ]},
    "Lysander": {"platform": "generic_ny", "agenda_platform": "Drupal", "automated": True,
                 "note": "One /board-meetings page mixes Town Board, Planning Board and ZBA agendas with no headings; "
                         "boards are told apart by file name (pb / zba, otherwise Town Board) and dates read from "
                         "compact names (a10082026pb_0.pdf). A file named only '91426agenda.pdf' cannot be assigned "
                         "reliably and is labeled Town Board.",
                 "listings": [_ny("Town Board", "select_board", "https://lysanderny.gov/board-meetings", r"agenda",
                                  exclude_pattern=r"minutes|materials", compact_dates=True, board_rules_field="href",
                                  board_rules=[[r"zba", "Zoning Board of Appeals", "zoning_board_of_appeals"],
                                               [r"pb", "Planning Board", "planning_board"],
                                               [r"agenda", "Town Board", "select_board"]])]},
    "Camillus": _not("no_agendas_online", "Town site calendar lists Town Board, Planning Board and ZBA meetings as "
                     "events with no agenda files; no agenda listing found on the pages reached.",
                     platform="generic", agenda_platform="custom ASP.NET CMS"),
    "Spafford": _not("js_only", _JS_MW, agenda_platform="JavaScript CMS (agendasandminutes module)"),
    "Geneva": {"automated": True, "platform": "generic_ny", "agenda_platform": "Revize",
               "listings": [_ny("Town Board", "select_board",
                                "https://townofgenevany.gov/departments_and_services/agendas_minutes.php", r"agenda",
                                exclude_pattern=r"minutes", strip_query=True, doc_href=r"\.pdf",
                                date_regex=r"(?P<y>20\d\d)\.\d\d (?P<m>[A-Za-z]+) (?P<d>\d{1,2})\b",
                                board_rules=[[r"planning", "Planning Board", "planning_board"],
                                             [r"zoning|ZBA", "Zoning Board of Appeals", "zoning_board_of_appeals"],
                                             [r"conservation", "Conservation Board", "conservation_commission"],
                                             [r"town board", "Town Board", "select_board"]])]},
    "Penfield": {"automated": True, "platform": "generic_ny", "agenda_platform": "Revize",
                 "listings": [
                     _ny("Town Board", "select_board",
                         _PEN + "town_board.php", r"agenda",
                         strip_query=True),
                     _ny("Planning Board", "planning_board",
                         _PEN + "planning_board.php", r"agenda",
                         strip_query=True),
                     _ny("Zoning Board of Appeals", "zoning_board_of_appeals",
                         _PEN + "zoning_board.php",
                         r"agenda", strip_query=True)]},
    "York": _not("no_agendas_online", "Wix site: Town Board, Planning Board and ZBA pages post annual meeting-date "
                 "schedules, forms and occasional hearing notices, but no agendas.", platform="generic",
                 agenda_platform="Wix"),
    "Cicero": _not("crawl_delay_exceeds_cap", "ciceronewyork.net robots.txt sets Crawl-delay: 20 for all agents; "
                   "351WatchBot skips hosts asking for more than 10 s.", agenda_platform="WordPress (site not fetched)"),
    "Lansing": _not("crawl_delay_exceeds_cap", "lansingtownny.gov robots.txt sets Crawl-delay: 15 for all agents; "
                    "351WatchBot skips hosts asking for more than 10 s. Automatable at 1 request per 15 s if the cap "
                    "is raised.", agenda_platform="unknown (site not fetched)"),
    # ---------------- Western NY
    "Concord": {"automated": True, "platform": "generic_ny", "agenda_platform": "custom PHP site",
                "note": "Most 2026 agenda files are named by month only ('September 2026.pdf'): those are kept with "
                        "no meeting date. ZBA page posts no documents.",
                "listings": [
                    _ny("Town Board", "select_board", "https://www.townofconcordny.gov/town_board_min.php", r"^Agenda",
                        month_only=True, doc_href=r"\.pdf"),
                    _ny("Planning Board", "planning_board", "https://www.townofconcordny.gov/planning_board_min.php",
                        r"^Agenda", month_only=True, doc_href=r"\.pdf")]},
    "Aurora": {"automated": True, "platform": "generic_ny", "agenda_platform": "Concrete CMS (download_file links in yearly tables)",
               "note": "One '2026 Meeting Schedule & Documents' page with a table per board; rows give month and day only.",
               "listings": [
                   _ny("Town Board", "select_board", _AUR, r"^AGENDA\b", scope=r"^Town Board Meetings & Work Sessions$",
                       assume_year=2026),
                   _ny("Planning and Conservation Board", "planning_board", _AUR, r"^AGENDA\b",
                       scope=r"^Planning Board Meetings$", assume_year=2026),
                   _ny("Zoning Board of Appeals", "zoning_board_of_appeals", _AUR, r"^AGENDA\b",
                       scope=r"^Zoning Board of Appeals Meetings$", assume_year=2026)]},
    "Boston": _not("js_only", _JS_MW, agenda_platform="JavaScript CMS (agendasandminutes module)"),
    "Newfane": _not("waf_block", "HTTP 403 'Forbidden' from the site's firewall on every request (bot/IP filtering); "
                    "not bypassed", agenda_platform="unknown"),
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
NY_LABELS = {"planning_board": "Planning Board", "zoning_board_of_appeals": "Zoning Board of Appeals",
             "conservation_commission": "Conservation Advisory Council", "select_board": "Town Board"}


def listing_platform(l: dict) -> str:
    if l.get("platform"):
        return l["platform"]
    if "category_id" in l:
        return "civicplus"
    if "civicclerk.com" in l.get("url", ""):
        return "civicclerk"
    if "client" in l:
        return "legistar"
    return "generic"


def apply_curated(raw: dict) -> dict:
    """Discovery result + hand-curated facts -> the towns_ny.json row."""
    rec = json.loads(json.dumps(raw))
    cur = CURATED.get(rec["town"], {})
    for k in ("agenda_platform", "note", "platform", "reason_code", "reason", "automated", "tenant"):
        if k in cur:
            rec[k] = cur[k]
    listings = rec.get("listings", []) + rec.pop("secondary_listings", [])
    if "listings" in cur:
        listings = list(cur["listings"])
    listings += cur.get("add_listings", [])
    if cur.get("drop_listings"):
        listings = [l for l in listings if not re.search(cur["drop_listings"], l["board"], re.I)]
    for l in listings:   # discovery labels generic listings with link text ("View Planning Board Meeting Minutes")
        if listing_platform(l) in ("generic", "generic_ny") and (
                re.search(r"minutes|view|click|full list|select board", l["board"], re.I) or len(l["board"]) > 40):
            l["board"] = NY_LABELS.get(l["board_key"], l["board"])
    if cur.get("automated") is False:
        rec.update(status="not_automated", automated=False, listings=[])
        rec.pop("boards_by_platform", None)
        if listings:
            rec["listings_found_not_crawled"] = listings
    elif listings and (cur.get("automated") or rec.get("automated")):
        rec.update(status="automated", automated=True, reason_code=None, reason=None)
        plats = []
        for l in listings:
            if listing_platform(l) not in plats:
                plats.append(listing_platform(l))
        primary = rec.get("platform") if rec.get("platform") in plats else plats[0]
        rec["platform"] = primary
        rec["platforms"] = [primary] + [p_ for p_ in plats if p_ != primary]
        rec["listings"] = [l for l in listings if listing_platform(l) == primary]
        sec = [l for l in listings if listing_platform(l) != primary]
        if sec:
            rec["secondary_listings"] = sec
        rec["boards_by_platform"] = {p_: sorted({l["board_key"] for l in listings if listing_platform(l) == p_})
                                     for p_ in rec["platforms"]}
        rec["boards_found"] = sorted({l["board_key"] for l in listings} |
                                     {k for l in listings for _, _, k in l.get("board_rules", [])})
        rec["boards_missing"] = [k for k in dc.TRACKED[:4] if k not in rec["boards_found"]]
    else:
        rec.update(status="not_automated", automated=False, listings=[])
    if not rec.get("agenda_platform"):
        plat = rec.get("platform")
        rec["agenda_platform"] = {"civicplus": "CivicPlus AgendaCenter", "civicclerk": "CivicClerk",
                                  "generic": "town website (" + (", ".join(rec.get("cms") or []) or "custom CMS") + ")",
                                  "legistar": "Legistar"}.get(plat, plat or "unknown")
    if cur:
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
    return rec | {"_lead": lead}


RAW = SCRATCH / "discovered_raw.json"


def write_config(raw_by_town: dict) -> dict:
    rows = []
    for t in NY_TOWNS:
        if t["town"] not in raw_by_town:
            continue
        rec = apply_curated(raw_by_town[t["town"]])
        rec["selection_reason"] = t["why"]
        rec["selection_source_url"] = t["src"]
        rows.append(rec)
    conf = {
        "_about": "351 Watch New York pilot: agenda platform and crawlable listing per tracked board, or the precise "
                  "reason a town is not automated. Same per-town schema as towns_ma_all.json plus state, "
                  "agenda_platform and why the town was chosen (selection_reason / selection_source_url). Built by "
                  "`python3 experiments/ny_pilot.py discover` (watch351.discover_census with NY board names) and "
                  "hand curation (CURATED in experiments/ny_pilot.py). Listings with \"platform\": \"generic_ny\" or "
                  "\"escribe\" use the adapters added for this pilot.",
        "generated": now_iso(),
        "state": STATE,
        "boards_tracked": dc.TRACKED[:4],
        "board_key_mapping": {"Town Board": "select_board", "Planning Board": "planning_board",
                              "Zoning Board of Appeals": "zoning_board_of_appeals",
                              "Conservation Advisory Council / Conservation Board": "conservation_commission"},
        "evidence_rule": "discovery: board automated only if its listing shows >=1 agenda dated in "
                         "[today-120d, today+120d]; curated listings were checked by hand",
        "count": len(rows),
        "automated": sum(1 for r in rows if r.get("automated")),
        "towns": rows,
    }
    save(CONFIG, conf)
    return conf


def cmd_discover(args, fetcher: PoliteFetcher) -> None:
    ny_patches()
    raw = load(RAW, {})
    todo = select(NY_TOWNS, args.towns)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        out = list(pool.map(lambda t: discover_one(fetcher, t), todo))
    lead_all = load(SCRATCH / "leadtime_rows.json", {})
    for rec in out:
        lead_all[rec["town"]] = rec.pop("_lead")
        raw[rec["town"]] = rec
    save(SCRATCH / "leadtime_rows.json", lead_all)
    save(RAW, raw)
    conf = write_config(raw)
    for r in conf["towns"]:
        if args.towns and r["town"] not in {t["town"] for t in todo}:
            continue
        print(f"{r['town']:<16} {str(r.get('platform')):<11} {'AUTO' if r.get('automated') else 'no  '} "
              f"boards={r.get('boards_found')} {'' if r.get('automated') else (r.get('reason_code') or '') + ': ' + str(r.get('reason'))[:150]}")
    print(f"automated {conf['automated']}/{conf['count']}")


def cmd_curate(args, fetcher: PoliteFetcher) -> None:
    conf = write_config(load(RAW, {}))
    for r in conf["towns"]:
        print(f"{r['town']:<16} {str(r.get('platform')):<11} {'AUTO' if r.get('automated') else 'no  '} "
              f"{r.get('agenda_platform')!s:<40.40} boards={r.get('boards_found')} "
              f"{'' if r.get('automated') else (r.get('reason_code') or '') + ': ' + str(r.get('reason'))[:90]}")
    print(f"automated {conf['automated']}/{conf['count']}")


def crawl_configs(towns: list[dict]) -> list[dict]:
    """One crawl config per (town, platform): each adapter reads its own listings."""
    cfgs = []
    for t in towns:
        if not t.get("automated"):
            cfgs.append(t)
            continue
        groups: dict[str, list] = {}
        for l in t.get("listings", []) + t.get("secondary_listings", []):
            groups.setdefault(listing_platform(l), []).append(l)
        for plat, ls in groups.items():
            cfg = {"town": t["town"], "county": t.get("county"), "website": t.get("final_url") or t["website"],
                   "platform": plat, "automated": True, "listings": ls}
            if plat == "civicplus":
                parts = urlsplit(cfg["website"])
                cfg["website"] = f"{parts.scheme}://{parts.netloc}"
            if plat == "civicclerk":
                cfg["tenant"] = t.get("tenant") or (t.get("vendors", {}).get("civicclerk", {}).get("tenant"))
            if plat == "legistar":
                cfg["client"] = ls[0]["client"]
            cfgs.append(cfg)
    return cfgs


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
               "title": doc.title, "url": doc.url, "listing_url": doc.listing_url, "platform": cfg["platform"]}
        rec.update(stamps.get(doc.url, {}))
        up = doc.extra.get("uploaded") or (dc.REVIZE_TS.search(doc.url).group(1) if dc.REVIZE_TS.search(doc.url) else None)
        if up:
            rec["uploaded"] = datetime.strptime(up[:14], "%Y%m%d%H%M%S").isoformat()
        if doc.extra.get("posted"):
            try:
                rec["posted"] = datetime.strptime(doc.extra["posted"], "%m-%d-%Y").isoformat()
                rec["posted_kind"] = "document_date"
            except ValueError:
                pass
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
        parts = list(pool.map(lambda c: crawl_one(fetcher, c, window), crawl_configs(towns)))
    results = []
    for t in towns:   # merge the per-platform results back into one row per town
        ps = [p_ for p_ in parts if p_["town"] == t["town"]]
        r = dict(ps[0])
        r["platform"] = t.get("platform")
        r["platforms"] = sorted({p_["platform"] for p_ in ps if p_["platform"]})
        r["reason_code"], r["reason"] = t.get("reason_code"), t.get("reason")
        for k in ("agendas_listed", "documents_scanned", "documents_without_text_layer", "documents_ocr"):
            r[k] = sum(p_[k] for p_ in ps)
        for k in ("errors", "docs", "hits"):
            r[k] = [x for p_ in ps for x in p_[k]]
        results.append(r)
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
    keep = {t["town"] for t in towns}
    for town, rows in lead_rows.items():
        if town not in keep:
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

    def stamp_stats(xs: list[float]) -> dict:
        """dist() plus the 72-hour check. Lead is measured to 00:00 of the meeting day; most NY town boards
        meet at 6-7:30 pm, so lead >= 2.21 d to midnight is >= 72 h before a 7 pm meeting."""
        out = dist(xs)
        if xs:
            out["share_after_meeting_day"] = round(sum(1 for x in xs if x < -1) / len(xs), 3)
            pre = [x for x in xs if x >= -1]
            out["share_ge_72h_before_7pm_meeting_of_preposted"] = (
                round(sum(1 for x in pre if x >= 2.21) / len(pre), 3) if pre else None)
            out["median_of_preposted"] = round(statistics.median(pre), 2) if pre else None
        return out

    first_post = [x for x in history if x["platform"] == "civicplus" and x["kind"] == "posted"]
    republish = [x for x in history if x not in first_post]
    by_platform = defaultdict(lambda: {"automated": [], "not_automated": []})
    for r, cfg in zip(results, towns):
        by_platform[cfg.get("platform") or "none (" + str(cfg.get("reason_code")) + ")"][
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
            "note": "Days from a timestamp to 00:00 of the meeting day (an underestimate: most NY town boards meet "
                    "6-7:30 pm). Only CivicPlus AgendaCenter 'Posted' stamps are first-posting times. CivicClerk "
                    "publishOn and Revize '?t=' upload stamps are LAST (re)publish times: many fall after the meeting "
                    "(agenda re-uploaded with resolutions/minutes), so they bound posting only when they precede it. "
                    "pdf_proxy is the PDF's ModDate/CreationDate (when the file was last saved). first_seen_upcoming "
                    "is our own first fetch, upcoming meetings only (bounded by when this pilot ran, not by the town).",
            "civicplus_first_posted_365d": stamp_stats([x["lead_days"] for x in first_post]),
            "civicplus_first_posted_365d_by_town": {t: stamp_stats([x["lead_days"] for x in first_post if x["town"] == t])
                                                    for t in sorted({x["town"] for x in first_post})},
            "republish_stamps_365d_by_platform": {
                p_: stamp_stats([x["lead_days"] for x in republish if x["platform"] == p_])
                for p_ in sorted({x["platform"] for x in republish})},
            "republish_stamps_365d_by_town": {
                f"{t} ({p_})": stamp_stats([x["lead_days"] for x in republish if x["town"] == t and x["platform"] == p_])
                for t, p_ in sorted({(x["town"], x["platform"]) for x in republish})},
            "window_platform_stamps": stamp_stats([x["lead_days"] for x in lead_window]),
            "pdf_proxy": stamp_stats([x["lead_days"] for x in proxy]),
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
    print("lead civicplus", json.dumps(report["lead_time"]["civicplus_first_posted_365d"]))
    for r in report["towns"]:
        if r["automated"]:
            print(f"  {r['town']:<16} listed {r['agendas_listed']:>3} scanned {r['documents_scanned']:>3} "
                  f"hits {r['hits']:>3} err {len(r['errors'])} {r['errors'][:1]}")
    print(f"fetcher: {fetcher.stats}")


def cmd_listings(args, fetcher: PoliteFetcher) -> None:
    conf = load(CONFIG, {"towns": []})
    today = date.today()
    window = Window(today - timedelta(days=args.days_back), today + timedelta(days=args.days_ahead))
    for cfg in crawl_configs(select(conf["towns"], args.towns)):
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
    p.add_argument("command", choices=["get", "discover", "curate", "listings", "crawl"])
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
        {"discover": cmd_discover, "curate": cmd_curate, "listings": cmd_listings,
         "crawl": cmd_crawl}[args.command](args, fetcher)
    return 0


if __name__ == "__main__":
    sys.exit(main())
