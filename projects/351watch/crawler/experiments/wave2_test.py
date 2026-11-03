#!/usr/bin/env python3
"""Agenda Ahead New York wave 2 (2026-11): about 100 more New York places, the battery-storage moratorium
belt plus the data-center towns, promoted onto the live site as they prove readable. Everything here is
gated: nothing writes data/hits_current.json, data/state/ or data/sources/. Promotion is the one step that
touches production, and it touches only data/towns_ny.json.

    cd projects/351watch/crawler
    python3 experiments/wave2_test.py targets                      # -> data/test/wave2/targets_ny.json + targets_ny.md
    python3 experiments/wave2_test.py websites [--places A,B]      # official sites from Wikipedia infoboxes -> targets_ny.json
    python3 experiments/wave2_test.py probe [--places A,B]         # ...and from domain patterns (DNS first, homepage must name the place)
    python3 experiments/wave2_test.py discover [--places A,B] [--counties]   # -> data/test/wave2/config/towns_ny.json
    python3 experiments/wave2_test.py annotate                     # via-county coverage fields on the config rows
    python3 experiments/wave2_test.py crawl --label run1 [--subdir ny] [--days-back 45] [--days-ahead 120]
    python3 experiments/wave2_test.py sample --n 40 --seed 2031 [--subdir ny_extended]   # hand-check worksheet
    python3 experiments/wave2_test.py promote --wave 1|2 [--dry-run]   # rows that read cleanly -> data/towns_ny.json
    python3 experiments/wave2_test.py carry --wave 1|2 [--dry-run]     # their index records -> data/state/docs, first_seen
    python3 experiments/wave2_test.py drafts                       # research_notes/Expansion/ny_unblock_drafts.md (not sent)
    python3 experiments/wave2_test.py leadtime                     # CivicPlus "Posted" stamps of promoted towns -> leadtime_ny_wave2.json
    python3 experiments/wave2_test.py analyze                      # coverage, platforms, errors

Targets (data/test/wave2/targets_ny.json): every Carina BESS Moratorium Monitor row for New York that was
not already a site town or a wave-1 place (read 2026-11-02, 128 NY rows), the 2026 moratoria found in town
documents this session, the Capital Region and data-center towns the November notes name, the wave-1 places
that were not promoted (they come back for a second discovery pass and the county route), and the county
planning boards that see those places' zoning actions under General Municipal Law 239-m.

The config file (data/test/wave2/config/towns_ny.json) sits outside the data/towns_*.json glob because New
York is a published state (build.py renders every row of data/towns_ny.json), and is marked "gated":
watch351.daily crawls it only with --states NY and an --output-dir other than its own directory:

    python3 -m watch351.daily --data-dir ../data/test/wave2/config --states NY \\
        --output-dir ../data/test/wave2/ny --hits-name hits_ny_wave2.json

County rows carry "attribute_townships": true and "county_body" (the board's name): a hit from a county
agenda is filed under the town, village or city the item names (watch351/attribution.py, New York forms),
and a place we cannot read directly but whose county board we do read is marked coverage "via_county", as
data/towns_mi.json does for Michigan townships.

Promotion (`promote`): a place is moved into data/towns_ny.json when its last test run read its listings
without error, at least one of its documents is an agenda, packet or notice with a meeting date, and its
town_health entry is ok; the rest stay in the test config marked "automated": false with a one-line
"notes" reason in the pilot's vocabulary (bot wall, robots disallow, crawl delay over cap, JavaScript
only, no agenda page, agendas undated, vendor blocked, unreachable, no website).

All network access goes through watch351.fetch.PoliteFetcher (AgendaAheadBot UA, robots.txt on every hop,
<= 1 request/second/host, crawl-delay honoured up to the cap, no logins, no POSTs, no challenge solving).
Wikipedia is read at one page per 6 seconds (it answers 429 at one a second).
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
CRAWLER = HERE.parent
sys.path.insert(0, str(CRAWLER))

from bs4 import BeautifulSoup  # noqa: E402

from watch351 import attribution, current, fetch  # noqa: E402
from watch351.fetch import FetchError, PoliteFetcher  # noqa: E402

DATA = CRAWLER.parent / "data"
W2 = DATA / "test" / "wave2"
CONFIG = W2 / "config"
NY_OUT = W2 / "ny"
NY_HITS = "hits_ny_wave2.json"
PROD = DATA / "towns_ny.json"
W1_CONFIG = DATA / "test" / "wave1" / "config" / "towns_ny.json"
W1_OUT = DATA / "test" / "wave1" / "ny"
ALL3 = ["select_board", "planning_board", "zoning_board_of_appeals"]
TODAY = date.today().isoformat()

CARINA = "https://carina.energy/bess-moratoriums/"
NOTE_PAYS = "research_notes/Expansion/where_it_pays_2026.md"
NOTE_FIGHTS = "research_notes/Meeting monitor national expansion/data_center_and_other_fights.md"
NOTE_PILOT = "research_notes/Expansion/ny_pilot.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def load(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


# ------------------------------------------------------------------------------------ targets
# (town, county, kind, group, reason, source). Carina statuses and dates are the BESS Moratorium Monitor as
# read on 2026-11-02 (128 New York rows). Rows already in data/towns_ny.json or in wave 1 are not repeated;
# the three Carina rows whose moratoria ended in 2024 (Busti, Long Lake, Port Chester) are left out.
NY_TARGETS = [
    # --- Carina: active moratoria, extension or permanent law due
    ("Chester", "Orange", "town", "bess_moratorium",
     "BESS moratorium ACTIVE, listed end 2026-08-26: extension or law due. The pilot swapped Chester for Warwick "
     "when its guessed domain failed; the official site is chester-ny.gov (Wikipedia infobox)", CARINA),
    ("Freedom", "Cattaraugus", "town", "bess_moratorium", "BESS moratorium ACTIVE, no end date listed", CARINA),
    ("Mina", "Chautauqua", "town", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-06-30: extension or law due", CARINA),
    ("Cameron", "Steuben", "town", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due", CARINA),
    ("Gloversville", "Fulton", "city", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due", CARINA),
    ("Oswego", "Oswego", "city", "bess_moratorium", "BESS moratorium ACTIVE (Carina: 'Oswego City'), no end date listed", CARINA),
    ("Parishville", "St. Lawrence", "town", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due", CARINA),
    ("Jay", "Essex", "town", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-06-18: extension or law due", CARINA),
    ("Southport", "Chemung", "town", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due", CARINA),
    ("Poland", "Chautauqua", "town", "bess_moratorium", "BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due", CARINA),
    ("Willing", "Allegany", "town", "bess_moratorium",
     "BESS moratorium (all BESS) listed EXPIRED with end date 2027-06-01; Carina's status and date disagree", CARINA),
    # --- Carina: under review or pending in 2026
    ("Athens", "Greene", "town", "bess_review", "BESS moratorium (all BESS) UNDER_REVIEW, listed date 2026-03-01", CARINA),
    ("German Flatts", "Herkimer", "town", "bess_review", "BESS moratorium UNDER_REVIEW, listed date 2026-05-31", CARINA),
    ("Barker", "Broome", "town", "bess_review", "BESS moratorium UNDER_REVIEW, listed date 2026-04-22", CARINA),
    ("Victory", "Cayuga", "town", "bess_review", "BESS moratorium UNDER_REVIEW, listed date 2026-03-13", CARINA),
    ("Fort Ann", "Washington", "town", "bess_review", "BESS moratorium PENDING, listed date 2026-02-21", CARINA),
    ("Florence", "Oneida", "town", "bess_review", "BESS moratorium UNDER_REVIEW, listed date 2026-05-01", CARINA),
    ("Salem", "Washington", "town", "bess_review", "BESS moratorium UNDER_REVIEW, listed date 2026-04-28", CARINA),
    ("Naples", "Ontario", "town", "bess_review", "BESS moratorium UNDER_REVIEW, listed date 2026-02-28", CARINA),
    # --- Carina: lifted or expired since mid-2025 (a BESS law followed; applications and amendments next)
    ("Albion", "Orleans", "town", "bess_law", "BESS moratorium LIFTED: law adopted, applications next (Carina lists 'Albion'; taken as the town)", CARINA),
    ("Chautauqua", "Chautauqua", "town", "bess_law", "BESS moratorium EXPIRED 2025-09-03", CARINA),
    ("Harrison", "Westchester", "town", "bess_law", "BESS moratorium EXPIRED 2025-09-06", CARINA),
    ("Johnstown", "Fulton", "town", "bess_law", "BESS moratorium EXPIRED 2025-08-03 (Carina lists 'Johnstown'; taken as the town)", CARINA),
    ("Mamaroneck (village)", "Westchester", "village", "bess_law", "BESS moratorium LIFTED 2026-05-01", CARINA),
    ("Mount Kisco", "Westchester", "village", "bess_law", "BESS moratorium EXPIRED 2025-06-03", CARINA),
    ("Newstead", "Erie", "town", "bess_law", "BESS moratorium EXPIRED 2026-03-31", CARINA),
    ("Pound Ridge", "Westchester", "town", "bess_law", "BESS moratorium (all BESS) LIFTED 2026-02-28", CARINA),
    ("Ripley", "Chautauqua", "town", "bess_law", "BESS moratorium EXPIRED (no date listed)", CARINA),
    ("Rotterdam", "Schenectady", "town", "bess_law", "BESS moratorium EXPIRED 2025-05-03", CARINA),
    ("Royalton", "Niagara", "town", "bess_law", "BESS moratorium LIFTED 2026-03-31", CARINA),
    ("Walworth", "Wayne", "town", "bess_law", "BESS moratorium LIFTED 2026-05-30", CARINA),
    ("Wilson", "Niagara", "town", "bess_law", "BESS moratorium EXPIRED 2026-03-31", CARINA),
    ("Frankfort", "Herkimer", "town", "bess_law", "BESS moratorium LIFTED 2026-04-27", CARINA),
    ("Le Ray", "Jefferson", "town", "bess_law", "BESS moratorium EXPIRED 2025-08-18", CARINA),
    ("Turin", "Lewis", "town", "bess_law", "BESS moratorium EXPIRED 2025-12-06", CARINA),
    ("Pendleton", "Niagara", "town", "bess_law", "BESS moratorium EXPIRED 2025-12-27", CARINA),
    ("Carrollton", "Cattaraugus", "town", "bess_law", "BESS moratorium EXPIRED 2025-04-29", CARINA),
    ("Elba", "Genesee", "town", "bess_law", "BESS moratorium LIFTED 2025-10-31", CARINA),
    # --- 2026 moratoria found in town documents this session (not on Carina's monitor)
    ("North Elba", "Essex", "town", "bess_2026",
     "One-year BESS moratorium approved October 2026 (WCAX, 2026-10-16)",
     "https://www.wcax.com/2026/10/16/north-elba-approves-one-year-moratorium-battery-energy-storage-systems/"),
    ("Newcomb", "Essex", "town", "bess_2026",
     "12-month moratorium on permits for commercial and industrial BESS (news summary; adoption date to verify)",
     "https://www.thecooldown.com/?p=750647"),
    ("Ticonderoga", "Essex", "town", "bess_2026",
     "Town Board hearing 2026-05-14 on a temporary BESS moratorium (hearing notice read 2026-11-02)",
     "https://townofticonderoga.gov/wp-content/uploads/Notice-of-Public-Hearing-1.pdf"),
    ("St. Armand", "Essex", "town", "bess_2026",
     "One-year BESS moratorium passed March 2026 (Environment+Energy Leader summary of Carina's release; to verify)",
     "https://www.environmentenergyleader.com/stories/new-york-battery-storage-moratoriums-hit-98-municipalities,126655"),
    ("Lake George", "Warren", "town", "bess_2026",
     "Local Law 2 of 2026 establishing a BESS moratorium (law text read 2026-11-02)",
     "https://www.townoflakegeorge.gov/DocumentCenter/View/1246"),
    ("Chester (Warren County)", "Warren", "town", "bess_2026",
     "A BESS-moratorium document on the town site matched the search; the site answers HTTP 403 to the bot, so it is unread",
     "https://www.chesterwcny.gov/media/7606"),
    ("Walton", "Delaware", "town", "bess_2026",
     "Local Law 2 of 2026: a one-year BESS moratorium; the site asks a 30 s crawl delay, over the 10 s document cap",
     "https://townofwaltonny.gov/local-law-2-of-2026-a-local-law-establishing-a-one-1-year-moratorium-on-battery-energy-storage-systems-in-the-town-of-walton/"),
    ("Bergen", "Genesee", "town", "bess_2026",
     "Local Law 3 of 2026: a nine-month BESS moratorium, hearing 2026-05-19 (legal notice read 2026-11-02)",
     "https://www.townofbergenny.gov/documents/3-2026-legal-notice-for-moratorium-battery-storage-systems-may-2026.docx"),
    ("Webb", "Herkimer", "town", "bess_2026",
     "A public-hearing notice on the town site matched the BESS-moratorium search; the site answers HTTP 403 to the bot (to verify)",
     "https://www.townofwebbny.gov/media/2131"),
    ("Goshen", "Orange", "town", "bess_2026",
     "Residents and officials urged a BESS moratorium while the town studies safety and zoning (Citizen Portal summary; to verify)",
     "https://cpo.soar.com/articles/6447040/Goshen/Orange-County/New-York/Residents-and-officials-urge-moratorium-on-battery-storage-projects-while-town-studies-safety-and-zoning"),
    # --- Capital Region cities and towns named in where_it_pays_2026.md (Clifton Park is already a site town)
    ("Troy", "Rensselaer", "city", "capital_region",
     "City Council six-month BESS moratorium, 2026-02-06 (Spectrum News, cited in where_it_pays_2026.md [40])",
     "https://spectrumlocalnews.com/nys/capital-region/news/2026/02/06/troy-council-approves-moratorium-on-battery-energy-storage-systems-"),
    ("Moreau", "Saratoga", "town", "capital_region",
     "Capital Region town named in where_it_pays_2026.md; proposed Local Law 2 of 2026, a BESS moratorium (law text read 2026-11-02)",
     "https://www.townofmoreau.org/2026-LL2-Battery-Moratorium.pdf"),
    ("Waterford", "Saratoga", "town", "capital_region",
     "Capital Region town named in where_it_pays_2026.md; notice of adoption of Local Law 1 of 2026 (BESS moratorium); the notice "
     "answers HTTP 403 to the bot", "https://www.townofwaterfordny.gov/town-board/files/notice-adoption-local-law-no-1-2026"),
    # --- data-center and warehouse fights the notes name
    ("New Windsor", "Orange", "town", "data_center_fight",
     "Temporary moratorium on warehouses and self-storage, August 2026 (data_center_and_other_fights.md)",
     "https://citizenportal.ai/articles/10203240/new-york/orange-county/new-windsor/new-windsor-adopts-temporary-moratorium-on-warehouses-and-self-storage-excludes-airport-zone"),
    ("Alabama", "Genesee", "town", "data_center_fight",
     "STREAM US Data Centers' $19.5B proposal at STAMP: Planning Board site plan and SEQR findings through 2026 (ny_pilot.md next-50 #48)",
     "https://townofalabamany.gov/2026/04/"),
]
# County-level moratorium on Carina's monitor: the Board of Supervisors adopted it, and the county planning board
# sees the towns' 239-m referrals.
ESSEX_COUNTY = ("Essex County", "Essex", "county", "county_moratorium",
                "County-wide BESS moratorium ACTIVE on Carina's monitor (listed date 2026-03-16); five Essex towns are wave-2 targets", CARINA)

# Official websites known before discovery (Wikipedia infobox probes and the documents read 2026-11-02); the
# `websites` command fills the rest from Wikipedia. A list gives candidates tried in order.
WEBSITES: dict[str, list[str]] = {
    "Chester": ["http://chester-ny.gov/"],
    "Gloversville": ["https://cityofgloversvilleny.gov/"],
    "Oswego": ["https://www.oswegony.gov/"],
    "German Flatts": ["http://germanflatts.org"],
    "Harrison": ["http://www.harrison-ny.gov"],
    "Mamaroneck (village)": ["https://www.villageofmamaroneckny.gov/"],
    "Mount Kisco": ["http://www.mountkiscony.gov/"],
    "Ticonderoga": ["https://townofticonderoga.gov/"],
    "Lake George": ["https://www.townoflakegeorge.gov/", "https://lakegeorgetown.org/"],
    "Chester (Warren County)": ["https://www.chesterwcny.gov/"],
    "Walton": ["https://townofwaltonny.gov/"],
    "Bergen": ["https://www.townofbergenny.gov/"],
    "Webb": ["https://www.townofwebbny.gov/"],
    "Troy": ["http://troyny.gov"],
    "Moreau": ["https://www.townofmoreau.org/"],
    "Waterford": ["https://www.townofwaterfordny.gov/"],
    "New Windsor": ["http://newwindsor-ny.gov"],
    "Alabama": ["https://townofalabamany.gov/"],
    "Essex County": ["http://essexcountyny.gov"],
    "Suffolk County": ["http://www.suffolkcountyny.gov"],
}
# Wave-1 places kept out of wave 2 even though they were not promoted: none (every one comes back for a second
# look and the county route). Wave-1 towns with no website at all still get a county row.

LI_TOWNS = ["Babylon", "Brookhaven", "Hempstead", "Huntington", "Islip", "North Hempstead", "Oyster Bay",
            "Smithtown", "Southampton", "Southold", "Riverhead", "Glen Cove"]


def prod_rows() -> list[dict]:
    return [{**t, "state": "NY"} for t in (load(PROD, {}) or {}).get("towns", [])]


def w1_rows() -> list[dict]:
    return [{**t, "state": "NY"} for t in (load(W1_CONFIG, {}) or {}).get("towns", [])]


def county_label(county: str) -> str:
    return f"{county} County Planning Board"


def cmd_targets(args) -> None:
    prod = {t["town"] for t in prod_rows()}
    w1 = {t["town"]: t for t in w1_rows()}
    rows, skipped = [], []
    for town, county, kind, group, why, src in NY_TARGETS + [ESSEX_COUNTY]:
        if town in prod:
            skipped.append((town, county, "already in data/towns_ny.json"))
            continue
        if town in w1 and w1[town].get("automated"):
            skipped.append((town, county, "wave-1 place awaiting promotion"))
            continue
        sites = WEBSITES.get(town)
        rows.append({"town": town, "state": "NY", "county": county, "kind": kind,
                     "website": sites[0] if sites else None, "website_candidates": sites or [],
                     "website_source": "document or Wikipedia infobox, 2026-11-02" if sites else None,
                     "selection_group": group, "selection_reason": why, "selection_source": src})
    # wave-1 places that were not promoted: a second discovery pass, then the county route
    for town, r in w1.items():
        if town in prod or r.get("automated"):
            continue
        sites = [u for u in ([r.get("website")] + list(r.get("website_candidates") or [])) if u]
        sites = list(dict.fromkeys(sites))
        rows.append({"town": town, "state": "NY", "county": r["county"], "kind": r.get("kind") or "town",
                     "website": sites[0] if sites else None, "website_candidates": sites,
                     "website_source": r.get("website_source") if sites else None,
                     "no_website_note": None if sites else (r.get("no_website_note") or "no town website found"),
                     "selection_group": "wave1_retry",
                     "selection_reason": f"Wave 1, not promoted: {r.get('notes') or r.get('reason') or r.get('reason_code')}. "
                                         f"Originally: {r.get('selection_reason')}",
                     "selection_source": r.get("selection_source") or NOTE_PILOT,
                     "wave1_reason_code": r.get("reason_code"), "wave1_listings": r.get("listings") or [],
                     "wave1_curation_note": r.get("curation_note")})
    # county planning boards: every county with a wave-2 place or a site place we cannot read directly
    dark_prod = [t for t in prod_rows() if not t.get("automated") and t.get("kind") != "county"]
    by_county: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        if r["kind"] != "county":
            by_county[r["county"]].append(r["town"])
    for t in dark_prod:
        by_county[t["county"]].append(f"{t['town']} (site town, not read)")
    have_county_rows = {r["county"] for r in rows if r["kind"] == "county"} | {t["county"] for t in prod_rows() if t.get("kind") == "county"}
    for county in sorted(by_county):
        if county in have_county_rows:
            continue
        names = by_county[county]
        sites = WEBSITES.get(f"{county} County")
        rows.append({"town": f"{county} County", "state": "NY", "county": county, "kind": "county",
                     "website": sites[0] if sites else None, "website_candidates": sites or [],
                     "website_source": "document or Wikipedia infobox, 2026-11-02" if sites else None,
                     "selection_group": "county_planning",
                     "selection_reason": f"County planning board: GML 239-m referrals from {len(names)} target "
                                         f"place{'s' if len(names) != 1 else ''} we cannot read directly or have not read yet "
                                         f"({', '.join(sorted(names))})",
                     "selection_source": "research_notes/Expansion/cheap_township_coverage.md (county review route) and ny_pilot.md recommendation 6"})
    save(W2 / "targets_ny.json", rows)
    write_targets_md(rows, skipped)
    print(len(rows), "targets:", dict(Counter(r["selection_group"] for r in rows)),
          f"({sum(1 for r in rows if r['kind'] != 'county')} places, {sum(1 for r in rows if r['kind'] == 'county')} county boards);",
          len(skipped), "skipped as already covered")


def write_targets_md(rows: list[dict], skipped: list[tuple]) -> None:
    places = [r for r in rows if r["kind"] != "county"]
    counties = [r for r in rows if r["kind"] == "county"]
    groups = {"bess_moratorium": "Carina monitor: BESS moratorium active, a renewal or permanent law is due",
              "bess_review": "Carina monitor: BESS moratorium under review or pending in 2026",
              "bess_law": "Carina monitor: BESS moratorium lifted or expired since mid-2025 (a law followed)",
              "bess_2026": "2026 BESS moratoria found in town documents and news this session, not on Carina's monitor",
              "capital_region": "Capital Region cities and towns named in where_it_pays_2026.md",
              "data_center_fight": "Data-center and warehouse fights the notes name",
              "wave1_retry": "Wave-1 places not promoted (second discovery pass, then the county route)",
              "county_moratorium": "County with its own BESS moratorium"}
    out = [f"# New York wave 2: target list ({TODAY})", "",
           f"{len(places)} places and {len(counties)} county planning boards, built by `python3 experiments/wave2_test.py targets` "
           f"from `NY_TARGETS` in `crawler/experiments/wave2_test.py`. Sources: Carina Energy's BESS Moratorium Monitor "
           f"({CARINA}, 128 New York rows read 2026-11-02; the three rows whose moratoria ended in 2024, Busti, Long Lake and Port Chester, "
           f"are left out), the \"Next 50 towns to add\" list in ny_pilot.md (all 50 became wave 1; the ones not promoted come back here), "
           f"where_it_pays_2026.md (section 2, entry 5, and section 4, recommendation 1), data_center_and_other_fights.md, and the town "
           f"documents read this session. Anything already in data/towns_ny.json is skipped.", "",
           "The seven Long Island towns with moratoria (Babylon, Hempstead, Huntington, Islip, North Hempstead, Oyster Bay, Smithtown; "
           "Southampton and Southold too) are already site towns, so they are not repeated; Islip, Brookhaven and Huntington are read "
           "through Suffolk County's planning commission if that reads, and are on the unblock list. Clifton Park is a site town.", ""]
    for g, label in groups.items():
        rs = [r for r in places if r["selection_group"] == g]
        if not rs:
            continue
        out += [f"## {label} ({len(rs)})", "", "| Place (County) | Kind | Why | Source |", "|---|---|---|---|"]
        for r in rs:
            out.append(f"| {r['town']} ({r['county']}) | {r['kind']} | {r['selection_reason']} | {r['selection_source']} |")
        out.append("")
    out += [f"## County planning boards, the 239-m referral route ({len(counties)})", "",
            "Under General Municipal Law 239-m a town, village or city must refer zoning amendments, moratoria, site plans, special "
            "permits and variances within 500 feet of a county or state road, a municipal boundary or county land to the county planning "
            "board, which has 30 days to answer. The board's agenda therefore lists the municipal action before the local hearing. "
            "Where a place's own site cannot be read, its county board is discovered and, if it reads, the place is marked coverage "
            "\"via_county\" the way towns_mi.json does.", "", "| County board | Why |", "|---|---|"]
    for r in counties:
        out.append(f"| {r['town']} | {r['selection_reason']} |")
    out += ["", "## Skipped (already covered)", ""]
    for town, county, why in skipped:
        out.append(f"- {town} ({county}): {why}")
    out.append("")
    (W2 / "targets_ny.md").write_text("\n".join(out))


# ------------------------------------------------------------------------------------ websites (Wikipedia)
WIKI = "https://en.wikipedia.org/wiki/"


def wiki_titles(town: str, county: str, kind: str) -> list[str]:
    base = re.sub(r"\s+\(.*\)$", "", town)
    if kind == "county":
        return [f"{county} County, New York"]
    if kind == "village":
        return [f"{base} (village), New York", f"{base}, New York", f"{base} (village), {county} County, New York"]
    if kind == "city":
        return [f"{base}, New York", f"{base} (city), New York"]
    return [f"{base}, New York", f"{base} (town), New York", f"{base}, {county} County, New York",
            f"{base} (town), {county} County, New York"]


def wiki_page(f: PoliteFetcher, title: str) -> dict | None:
    url = WIKI + title.replace(" ", "_")
    for attempt in range(3):
        try:
            with f.purpose("listing"):
                r = f.get(url, max_age=30 * 86400)
        except FetchError as e:
            return {"error": str(e)[:120]}
        if r.status == 429:
            time.sleep(30 * (attempt + 1))
            continue
        break
    if not r.ok:
        return None
    s = BeautifulSoup(r.text, "lxml")
    h1 = s.find("h1").get_text(" ", strip=True) if s.find("h1") else ""
    body = s.find(id="mw-content-text")
    lead = ""
    if body:
        for p in body.find_all("p", recursive=True):
            t = " ".join(p.get_text(" ", strip=True).split())
            if len(t) > 60:
                lead = t[:400]
                break
    out = {"title": h1, "lead": lead, "website": None, "county": None,
           "disambiguation": bool(s.find(id="disambigbox")) or " may refer to" in lead[:120]}
    ib = s.find("table", class_=re.compile("infobox"))
    if ib:
        for tr in ib.find_all("tr"):
            th = tr.find("th")
            if not th:
                continue
            lab = th.get_text(" ", strip=True).lower()
            if "website" in lab:
                a = tr.find("a", href=True)
                out["website"] = a["href"] if a else None
            elif lab.startswith("county"):
                td = tr.find("td")
                out["county"] = td.get_text(" ", strip=True) if td else None
    return out


def cmd_websites(args) -> None:
    fetch.HOST_MIN_INTERVAL["en.wikipedia.org"] = float(args.interval or 12.0)   # Wikipedia answers 429 at one page a second
    targets = load(W2 / "targets_ny.json")
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    f = PoliteFetcher()
    n_found = 0
    for t in targets:
        if wanted and t["town"].lower() not in wanted:
            continue
        if t.get("website") and not args.force:
            continue
        kind = t["kind"]
        found = None
        tried = []
        for title in wiki_titles(t["town"], t["county"], kind):
            pg = wiki_page(f, title)
            tried.append(title)
            if not pg or pg.get("error") or pg.get("disambiguation"):
                continue
            lead = (pg.get("lead") or "").lower()
            county_ok = kind == "county" or (pg.get("county") or "").lower().startswith(t["county"].lower()) \
                or f"{t['county'].lower()} county" in lead
            kind_ok = kind == "county" or re.search(rf"\bis an? (?:{kind}|{kind} and village|village and town|coterminous)\b", lead) \
                or (kind == "village" and "village" in lead[:200]) or (kind == "city" and "city" in lead[:200])
            if county_ok and kind_ok:
                found = pg
                break
        t["wikipedia"] = {"tried": tried, "title": found.get("title") if found else None}
        if found and found.get("website"):
            site = found["website"]
            t["website"] = site
            t["website_candidates"] = list(dict.fromkeys([site] + list(t.get("website_candidates") or [])))
            t["website_source"] = f"Wikipedia infobox ({found['title']}), {TODAY}"
            t.pop("no_website_note", None)
            n_found += 1
        elif not t.get("website"):
            t["no_website_note"] = (f"no official website in the Wikipedia infobox ({found['title']})" if found
                                    else "no matching Wikipedia article found") + f", {TODAY}"
        print(f"  {t['town']:<26} {t['website'] or '-'}", flush=True)
        save(W2 / "targets_ny.json", targets)    # progress survives an interrupted run
    save(W2 / "targets_ny.json", targets)
    print(f"{n_found} websites found; {sum(1 for t in targets if t.get('website'))}/{len(targets)} targets have a site; fetcher {f.stats}")


# ------------------------------------------------------------------------------------ websites (domain patterns)
def domain_guesses(town: str, county: str, kind: str) -> list[str]:
    base = re.sub(r"\s+\(.*\)$", "", town).lower().replace("st. ", "st").replace(".", "")
    n = re.sub(r"[^a-z]", "", base)
    h = re.sub(r"[^a-z-]", "", base.replace(" ", "-"))
    names = [n] + ([h] if h != n else [])
    out = []
    for m in names:
        if kind == "county":
            out += [f"www.co.{m}.ny.us", f"co.{m}.ny.us", f"www.{m}countyny.gov", f"{m}countyny.gov", f"{m}county.ny.gov",
                    f"www.{m}countyny.com", f"www.{m}county.com", f"{m}co.org", f"www.{m}countyny.org", f"www.{m}gov.com", f"{m}gov.com"]
        elif kind == "city":
            out += [f"www.cityof{m}ny.gov", f"cityof{m}ny.gov", f"www.cityof{m}.org", f"cityof{m}.org", f"www.{m}ny.gov", f"{m}ny.gov",
                    f"www.{m}-ny.gov", f"{m}-ny.gov", f"www.cityof{m}ny.com", f"www.cityof{m}.com", f"www.{m}ny.org"]
        elif kind == "village":
            out += [f"www.villageof{m}ny.gov", f"villageof{m}ny.gov", f"www.villageof{m}.org", f"villageof{m}.org", f"www.{m}ny.gov",
                    f"{m}ny.gov", f"www.villageof{m}.com", f"www.{m}village.org", f"www.{m}ny.org"]
        else:
            out += [f"www.townof{m}ny.gov", f"townof{m}ny.gov", f"www.townof{m}.org", f"townof{m}.org", f"www.{m}ny.gov", f"{m}ny.gov",
                    f"www.townof{m}.com", f"townof{m}.com", f"www.townof{m}ny.org", f"townof{m}ny.org", f"www.townof{m}ny.com",
                    f"www.{m}ny.org", f"{m}ny.org", f"www.{m}-ny.gov", f"{m}-ny.gov", f"www.{m}ny.com", f"www.townof{m}-ny.gov",
                    f"www.{m}.ny.us", f"town.{m}.ny.us", f"www.town.{m}.ny.us", f"{m}ny.us", f"www.{m}ny.us"]
    return list(dict.fromkeys(out))


def _resolves(host: str) -> bool:
    import socket
    try:
        socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        return True
    except OSError:
        return False


def probe_place(f: PoliteFetcher, t: dict) -> list[dict]:
    """Homepages that answer and name the place: [{url, final_url, status, names_place}]."""
    base = re.sub(r"\s+\(.*\)$", "", t["town"]).lower()
    kind = t["kind"]
    word = {"county": "county", "city": "city", "village": "village"}.get(kind, "town")
    found = []
    for host in domain_guesses(t["town"], t["county"], kind):
        if not _resolves(host):
            continue
        url = f"https://{host}/"
        try:
            with f.purpose("listing"):
                r = f.get(url, max_age=7 * 86400)
        except FetchError as e:
            found.append({"url": url, "error": str(e)[:100]})
            continue
        text = " ".join(BeautifulSoup(r.text[:400000], "lxml").get_text(" ", strip=True).split()).lower() if r.ok else ""
        names = bool(text) and base in text and (" ny" in text or "new york" in text) and word in text
        found.append({"url": url, "final_url": r.final_url, "status": r.status, "names_place": names})
        if names:
            break
    return found


def cmd_probe(args) -> None:
    targets = load(W2 / "targets_ny.json")
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    todo = [t for t in targets if not t.get("website") and (wanted is None or t["town"].lower() in wanted)]
    f = PoliteFetcher()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda t: (t, probe_place(f, t)), todo))
    n = 0
    for t, found in results:
        t["domain_probe"] = found
        hit = next((x for x in found if x.get("names_place")), None)
        if hit:
            t["website"] = hit["final_url"]
            t["website_candidates"] = list(dict.fromkeys([hit["final_url"], hit["url"]] + list(t.get("website_candidates") or [])))
            t["website_source"] = f"domain pattern probe (homepage names the place), {TODAY}"
            t.pop("no_website_note", None)
            n += 1
        print(f"  {t['town']:<26} {t.get('website') or '-':<50} {[x.get('status') or x.get('error', '')[:30] for x in found]}", flush=True)
    save(W2 / "targets_ny.json", targets)
    print(f"{n} of {len(todo)} found by domain pattern; {sum(1 for t in targets if t.get('website'))}/{len(targets)} targets have a site; fetcher {f.stats}")


# ------------------------------------------------------------------------------------ peek (curation helper)
def cmd_peek(args) -> None:
    """Print a page's document-like links with the dates the crawler would read, to write a hand listing."""
    from watch351.dates import first_date
    from watch351.adapters.agenda_page import DOC_HREF, compact_date, filename_of
    f = PoliteFetcher()
    for url in args.places.split(","):
        url = url.strip()
        try:
            with f.purpose("listing"):
                r = f.get(url, max_age=0 if args.force else 6 * 3600)
        except FetchError as e:
            print(f"== {url}: {e}")
            continue
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        print(f"== {url} -> HTTP {r.status} {r.final_url} | {title[:100]} | {len(r.body)} bytes")
        if not r.ok:
            print(r.text[:300])
            continue
        n = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = " ".join(a.get_text(" ", strip=True).split())
            hay = f"{text} {href}"
            if not re.search(args.grep or r"agenda|minutes|meeting|notice|hearing|\.pdf|\.docx?|packet", hay, re.I):
                continue
            from urllib.parse import urljoin
            absu = urljoin(r.final_url, href)
            when = first_date(text) or first_date(filename_of(absu)) or compact_date(filename_of(absu))
            print(f"  {str(when or '-'):<10} {'DOC' if DOC_HREF.search(absu) else '   '} {text[:70]:<70} {absu[:110]}")
            n += 1
            if n >= (args.n or 60):
                print("  ...")
                break
        if args.text:
            body = " ".join(soup.get_text(" ", strip=True).split())
            print("  TEXT:", body[:args.text])


# ------------------------------------------------------------------------------------ discovery
# County planning boards: discover_sites' New York board patterns exclude "county planning" (a town site's link
# to the county is not the town's board), so a county row is discovered with these patterns instead. Patched
# into the running process only; the package is shared with the other waves.
COUNTY_BOARD_RX = {
    "planning_board": (r"county\s+planning\s+(?:board|commission|agency)|planning\s+(?:board|commission|agency)|"
                       r"\bPB\b|\b239(?:-|\s)?m\b|referral|planning\b",
                       r"regional|committee|comprehensive\s+plan|transportation|agricultural|\bMPO\b|environmental\s+management|"
                       r"soil\s+and\s+water|industrial\s+development|\bIDA\b"),
    "select_board": (r"board\s+of\s+supervisors|county\s+legislature|\bBOS\b|legislature|supervisors",
                     r"committee|school|library|ethics|\bIDA\b"),
}
COUNTY_BOARD_NAME = {"planning_board": r"planning\s+board|planning\s+commission|planning\s+agency|\bPB\b",
                     "select_board": r"board\s+of\s+supervisors|county\s+legislature|\bBOS\b"}


def patch_county_patterns() -> None:
    from watch351 import discover_sites as D
    D.BOARD_RX["NY"] = {**D.BOARD_RX["NY"], **COUNTY_BOARD_RX}
    D.BOARD_NAME["NY"] = {**D.BOARD_NAME["NY"], **COUNTY_BOARD_NAME}


# Hand corrections after reading the sites (2026-11-02), each with the reason. Applied on top of discovery.
_CMM_RULES = [["planning", "Planning Board", "planning_board"],
              ["zoning|ZBA|appeals", "Zoning Board of Appeals", "zoning_board_of_appeals"]]


def _cmm(site: int, note: str) -> dict:
    """A Weebly town whose Minutes & Agendas page is a Compass Web Development CMM iframe (the wave-1 adapter)."""
    return {"add_listings": [{"board": "Town Board", "board_key": "select_board", "platform": "cmm_compass",
                              "url": f"https://cmm.compassweb.dev/embeds/{site}/agendas", "board_rules": _CMM_RULES}],
            "curation_note": note}


_WALWORTH = "https://townofwalworthny.gov/government/minutes-agendas/"
CURATED_NY: dict[str, dict] = {
    # Weebly sites with the CMM agenda embed (iframe on minutes--agendas.html), as Clymer, Ellery and Angelica in wave 1
    "Poland": _cmm(46, "agendas in the CMM embed (iframe on minutes--agendas.html); one dated Town Board agenda in the window"),
    "Willing": _cmm(13, "agendas in the CMM embed (iframe on minutes--agendas.html)"),
    "Chautauqua": _cmm(48, "agendas in the CMM embed (iframe on town-clerk.html); the Legals & Notices page also posts local laws "
                           "and hearing notices as .doc files without dates"),
    "Ripley": _cmm(14, "agendas in the CMM embed (iframe on minutes.html)"),
    "Carrollton": _cmm(22, "agendas in the CMM embed (iframe on minutes--agendas.html)"),
    # WordPress Minutes & Agendas page with dated agenda and minutes PDFs per board; the homepage renders by script, so
    # discovery stopped there
    "Walworth": {"add_listings": [
        {"board": "Town Board", "board_key": "select_board", "platform": "agenda_page", "url": _WALWORTH,
         "board_pattern": r"town\s+board", "board_exclude": r"planning|zoning"},
        {"board": "Planning Board", "board_key": "planning_board", "platform": "agenda_page", "url": _WALWORTH,
         "board_pattern": r"planning\s+board", "board_exclude": r"town\s+board|zoning"},
        {"board": "Zoning Board", "board_key": "zoning_board_of_appeals", "platform": "agenda_page", "url": _WALWORTH,
         "board_pattern": r"zoning\s+board", "board_exclude": r"town\s+board|planning"}],
        "curation_note": "Minutes & Agendas page (WordPress, paginated) with dated agenda PDFs for the Town Board, Planning Board and "
                         "Zoning Board; the homepage is script-rendered, which is why discovery found nothing"},
}

NY_ABOUT = ("Agenda Ahead New York wave 2 (2026-11): {n} more New York towns, villages, cities and county planning "
            "boards (battery-storage moratoria per Carina's monitor and 2026 town documents, data-center and warehouse "
            "fights, the Capital Region, the wave-1 places not promoted, and the counties' 239-m referral boards). Same "
            "row shape as towns_ny.json plus kind, selection_group / selection_reason / selection_source; county rows "
            "carry attribute_townships and county_body; places read only through their county carry coverage "
            "\"via_county\". Built by `python3 experiments/wave2_test.py discover`. Kept outside data/towns_*.json "
            "because New York is a published state; promotion = `wave2_test.py promote --wave 2`, which moves rows "
            "into data/towns_ny.json.")


def _config_doc(rows: list[dict]) -> dict:
    return {
        "_about": NY_ABOUT.format(n=len(rows)),
        "generated": now_iso(), "state": "NY", "gated": True,
        "gate_note": "Wave 2 test rows: not part of the production daily run or site (this file is outside the "
                     "data/towns_*.json glob). Crawled only by `python3 -m watch351.daily --data-dir "
                     "../data/test/wave2/config --states NY --output-dir ../data/test/wave2/ny --hits-name "
                     "hits_ny_wave2.json` (experiments/wave2_test.py crawl).",
        "boards_tracked": ALL3,
        "board_key_mapping": {"Town Board, Village Board of Trustees, City / Common Council, County Board of Supervisors": "select_board",
                              "Planning Board (county planning board on county rows)": "planning_board",
                              "Zoning Board of Appeals": "zoning_board_of_appeals"},
        "evidence_rule": "a board is automated only if its listing shows >=1 agenda/packet/notice dated within "
                         "[today-120d, today+120d] and the first such document is fetchable under robots.txt",
        "count": len(rows), "automated": sum(1 for r in rows if r.get("automated")), "towns": rows,
    }


def cmd_discover(args) -> None:
    from watch351.discover_sites import discover_place
    targets = load(W2 / "targets_ny.json")
    path = CONFIG / "towns_ny.json"
    prev = {t["town"]: t for t in (load(path, {}) or {}).get("towns", [])}
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    if args.counties:
        todo = [t for t in targets if t["kind"] == "county" and (wanted is None or t["town"].lower() in wanted)]
        patch_county_patterns()
    else:
        todo = [t for t in targets if t["kind"] != "county" and (wanted is None or t["town"].lower() in wanted)]
    fetcher = PoliteFetcher()
    t0 = time.monotonic()

    def tracked_for(t: dict) -> list[str]:
        if t["kind"] == "county":
            return ["planning_board", "select_board"] if t["county"] == "Essex" else ["planning_board"]
        return list(ALL3)

    def one(t):
        best = None
        for site in t.get("website_candidates") or [t.get("website")] or [None]:
            row = {k: v for k, v in t.items() if k not in ("website_candidates", "wikipedia", "wave1_listings", "domain_probe")}
            row["website"] = site
            # "Mamaroneck (village)", "Chester (Warren County)": the site names the bare place
            row["town"] = re.sub(r"\s+\(.*\)$", "", t["town"])
            try:
                r = discover_place(fetcher, row, "NY", tracked_for(t))
                r["town"] = t["town"]
            except Exception as e:  # noqa: BLE001 - one site must not stop the run
                logging.exception("discovery crashed for %s", t["town"])
                r = {**row, "status": "not_automated", "reason_code": "discovery_error", "automated": False,
                     "reason": f"{type(e).__name__}: {str(e)[:160]}", "listings": []}
            if best is None or r.get("automated") or best.get("reason_code") in ("unreachable", "website_mismatch", "http_error"):
                best = r
            if r.get("automated"):
                break
        best["website_candidates"] = t.get("website_candidates") or []
        if t.get("wave1_listings"):
            best["wave1_listings"] = t["wave1_listings"]
        return best

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one, todo))
    for r in results:
        r.pop("_posted_rows", None)
        if r["kind"] == "county":
            r["attribute_townships"] = True
            pb = next((l for l in (r.get("listings") or []) if l.get("board_key") == "planning_board"), None)
            label = (pb or {}).get("board") or ""
            if not re.search(r"planning", label, re.I):
                label = county_label(r["county"])
            elif not re.search(re.escape(r["county"]), label, re.I):
                # the page says only "County Planning Board" (Lewis, Orleans): name the county
                label = re.sub(r"^\s*county\s+", "", label, flags=re.I)
                label = f"{r['county']} County {label}"
            r["county_body"] = label
        cur = CURATED_NY.get(r["town"])
        if cur:
            apply_curation(r, cur)
        prev[r["town"]] = r
    order = [t["town"] for t in targets]
    rows = [prev[n] for n in order if n in prev]
    save(path, _config_doc(rows))
    print(f"NY wave 2: {len(results)} discovered in {time.monotonic() - t0:.0f}s; fetcher {fetcher.stats}")
    for r in results:
        print(f"  {r['town']:<26} {str(r.get('platform') or '-'):<14} {len(r.get('listings') or []):>2} "
              f"{'AUTO ' + ','.join(sorted(r.get('boards_found') or [])) if r.get('automated') else r.get('reason_code')}: "
              f"{'' if r.get('automated') else (r.get('reason') or '')[:120]}")


def apply_curation(r: dict, cur: dict) -> None:
    cur = dict(cur)
    extra = cur.pop("add_listings", [])
    if cur.pop("replace_listings", False):      # the discovered listings were wrong: curated ones only
        r["listings"], r["platform"] = [], None
    r.update(cur)
    if extra:
        have = {(l["board_key"], l["url"]) for l in r.get("listings") or []}
        r["listings"] = (r.get("listings") or []) + [l for l in extra if (l["board_key"], l["url"]) not in have]
        r["automated"], r["status"] = True, "automated"
        r["reason_code"] = r["reason"] = None
        r["platforms"] = sorted({l.get("platform") or "agenda_page" for l in r["listings"]})
        r["platform"] = r.get("platform") or extra[0]["platform"]
        r["boards_found"] = sorted({l["board_key"] for l in r["listings"]})
        r["boards_missing"] = [k for k in (["planning_board"] if r.get("kind") == "county" else ALL3) if k not in r["boards_found"]]
    r["curated"] = True


def cmd_curate(args) -> None:
    """Apply CURATED_NY to the config without any request (after editing the table)."""
    path = CONFIG / "towns_ny.json"
    doc = load(path)
    for r in doc["towns"]:
        cur = CURATED_NY.get(r["town"])
        if cur:
            apply_curation(r, cur)
    save(path, _config_doc(doc["towns"]))
    print("curated:", [r["town"] for r in doc["towns"] if r.get("curated")])


def annotate_rows(config_rows: list[dict], production: list[dict]) -> Counter:
    """Coverage fields on config rows (and production NY rows) from the automated county boards in both files."""
    modes = attribution.coverage_modes(config_rows + production)
    c = Counter()
    for r in config_rows + production:
        m = modes.get(r["town"])
        if not m or r.get("kind") == "county":
            continue
        if r.get("automated"):
            r["coverage"] = "direct"
            r.pop("coverage_note", None)
            if m.get("coverage_county_body"):
                r["coverage_county_body"] = m["coverage_county_body"]
        else:
            r["coverage"] = m["coverage"]
            r["coverage_county_body"] = m["coverage_county_body"]
            r["coverage_note"] = m["coverage_note"]
        c[r["coverage"]] += 1
    return c


def cmd_annotate(args) -> None:
    path = CONFIG / "towns_ny.json"
    doc = load(path)
    c = annotate_rows(doc["towns"], prod_rows())
    save(path, _config_doc(doc["towns"]))
    print("coverage (config + production places):", dict(c))


# ------------------------------------------------------------------------------------ crawl
def cmd_crawl(args) -> None:
    out = W2 / args.subdir if args.subdir else NY_OUT
    cmd = [sys.executable, "-m", "watch351.daily", "--data-dir", str(CONFIG), "--states", "NY", "--output-dir",
           str(out), "--hits-name", NY_HITS, "--days-back", str(args.days_back), "--days-ahead", str(args.days_ahead),
           "--workers", str(args.workers), "--request-log", str(out / f"requests_{args.label}.tsv")]
    if args.places:
        cmd += ["--towns", args.places]
    out.mkdir(parents=True, exist_ok=True)
    print(" ".join(cmd))
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=CRAWLER)
    print(f"exit {proc.returncode}, wall {time.monotonic() - t0:.0f}s")
    runs = out / "state" / "runs"
    latest = max(runs.glob("*.json"), key=lambda p: p.stat().st_mtime)
    save(out / "runs" / f"run_{args.label}.json", load(latest))
    print(f"saved {out / 'runs' / f'run_{args.label}.json'}")


# ------------------------------------------------------------------------------------ sample
def _doc_text(url: str) -> str:
    from watch351 import extract as X
    from watch351.fetch import DEFAULT_CACHE_DIR
    from watch351.keywords import clean_text
    X.OCR_CACHE = DEFAULT_CACHE_DIR / "ocr"
    f = PoliteFetcher(DEFAULT_CACHE_DIR, offline=True)
    try:
        resp = f.get(url)
    except FetchError:
        return ""
    return clean_text(X.extract(resp).text)


def cmd_sample(args) -> None:
    from watch351.state import DocIndex
    rng = random.Random(args.seed)
    out_dir = W2 / args.subdir if args.subdir else NY_OUT
    idx = DocIndex(out_dir / "state" / "docs")
    rows = [{**t, "state": "NY"} for t in (load(CONFIG / "towns_ny.json", {}) or {}).get("towns", [])] + prod_rows()
    counties = current.county_lookup(rows)
    hits = list({n["id"]: n for n in (current.normalize(h, counties) for h in idx.current_hits())}.values())
    pool = sorted((h for h in hits if h["state"] == "NY"), key=lambda h: h["id"])
    exclude = set()
    for ex in (args.exclude or "").split(","):
        if ex:
            exclude |= {i["id"] for i in load(W2 / ex)["items"]}
    pool = [h for h in pool if h["id"] not in exclude]
    pick = sorted(rng.sample(pool, min(args.n, len(pool))), key=lambda h: (h["town"], h["id"]))
    items = []
    for h in pick:
        text = _doc_text(h["source_url"])
        pos = text.find(h["snippet"][:100].rstrip("…"))
        items.append({**{k: h.get(k) for k in ("id", "town", "county", "board", "meeting_date", "topics", "snippet",
                                               "source_url", "document_title", "text_source")},
                      "context": text[max(0, pos - 700): pos + 900] if pos >= 0 else ""})
    dest = W2 / (args.out or "worksheet_ny.json")
    save(dest, {"pool": len(pool), "seed": args.seed, "n": len(items), "source_dir": str(out_dir.relative_to(DATA.parent)),
                "items": items})
    print("wrote", dest, "pool", len(pool), "n", len(items), dict(Counter(i["town"] for i in items)))


# ------------------------------------------------------------------------------------ promotion
# Places whose test output reads but does not meet the bar, with the reason in the pilot's vocabulary.
JUDGE_W1 = {
    "Lewis": "agendas undated: Town Board agendas are posted as monthly public notices named only by month "
             "('Agenda for September 2026', a .docx), so no meeting date can be read",
    "Westfield": "agendas undated: Town Board agendas on the year page are named only by month ('September Agenda'); "
                 "no meeting date can be read",
    "Carlton": "no agenda page: the town posts hearing and meeting notices on its homepage only (one dated ZBA hearing "
               "notice in the window); kept in the test config for the county route",
    # not automated in wave 1; the precise reason, checked by hand on 2026-10-12 and re-read from the discovery record
    "Carlisle": "no agenda page: the county-hosted town page (www4.schohariecounty-ny.gov/government/town-of-carlisle/) answers HTTP 404",
    "Gainesville": "no website: no town website found (web search 2026-10-12); county-hosted notices at most",
    "Brasher": "no agenda page: townofbrasher.gov is reachable but lists no agendas for the Town Board, Planning Board or ZBA",
    "Sherman": "no agenda page: shermanny.gov carries Town Board minutes only; the Planning Board and ZBA agendas there are the Village of Sherman's",
    "Schroeppel": "unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2",
    "Northampton": "unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2",
    "Mayville": "no agenda page: mayvilleny.gov is reachable but lists no agendas for the tracked boards",
    "Benson": "no website: no town website found (townofbenson.com is Benson, North Carolina; web search 2026-10-12)",
    "Collins": "robots disallow: robots.txt on townofcollinsny.gov disallows the agenda documents",
    "Virgil": "unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2",
    "Oswegatchie": "agendas undated: monthly Town Board agendas (2026_<month>_agenda.pdf) are posted without a day, and the latest was August 2026, before the window",
    "Palatine": "no agenda page: the Town Council page links a Google Drive folder; no dated agenda listing on townofpalatine.org",
    "Pike": "no website: no town website found (web search 2026-10-12)",
    "Mentz": "robots disallow: robots.txt on townofmentz.com disallows AgendaAheadBot",
    "Allen": "no agenda page: the Wix site is reachable but lists no agendas for the tracked boards",
    "Root": "no agenda page: the county-hosted town pages (montgomerycountyny.gov/web/municipal/root/) show board pages but no agenda dated within 120 days of the run",
    "Greenwood": "unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2",
    "Prattsburgh": "no agenda page: the Town Board page lists monthly minutes only",
    "North Harmony": "no agenda page: board pages found (townofnorthharmony.gov/townboard) but no agenda dated within 120 days of the run",
    "Rose": "no agenda page: board pages found (roseny.gov/town-boards) but no agenda dated within 120 days of the run",
    "Stockport": "no agenda page: the Town Board page posts minutes; no agenda dated within 120 days of the run",
    "Yorktown": "bot wall: agendas are on calendar.yorktownny.gov, which answers HTTP 403 'blocked due to security reasons' to AgendaAheadBot (robots.txt too); not bypassed",
    "Montgomery": "JavaScript only: 'Agendas, Minutes, & Videos' is a DNN document library filled by script, with no static listing to read",
    "Somerset": "bot wall: Cloudflare-style bot challenge (HTTP 403) on www.somersetny.gov; not bypassed",
    "Sherburne": "no agenda page: the newest Town Board agenda document is from June 2024; nothing dated within 120 days of the run",
}
# Wave 2: the precise reason for each place checked by hand on 2026-11-02 (the wave-1 reasons carry over).
JUDGE_W2: dict[str, str] = {k: v for k, v in JUDGE_W1.items() if k not in ("Lewis", "Westfield", "Carlton")}
JUDGE_W2.update({
    "Lewis": JUDGE_W1["Lewis"],
    "Carlton": JUDGE_W1["Carlton"],
    "Chester": "no agenda page: the Minutes | Agendas page lists the boards but no documents (its lists are filled by script); the "
               "board pages carry forms and fee schedules only",
    "Freedom": "no agenda page: the Minutes page lists meeting audio recordings (.m4a) and a CMM minutes embed; no agendas are posted",
    "Mina": "no website: townofmina.info (the Wikipedia infobox site) answers HTTP 404 and no other town site was found",
    "Cameron": "no agenda page: townofcameron.us posts the meeting schedule and minutes only",
    "Gloversville": "vendor blocked: Common Council agendas and minutes are kept in a Dropbox folder, whose robots.txt disallows all "
                    "readers; the calendar's event pages carry no agenda",
    "Parishville": "no agenda page: the Town Council page links board minutes only",
    "Athens": "bot wall: the Town Board page answers a Cloudflare check ('One moment, please...') to AgendaAheadBot; not bypassed",
    "German Flatts": "no website: germanflatts.org (the Wikipedia infobox site) answers HTTP 404",
    "Barker": "no agenda page: the dated Town Board documents on the Meetings page are minutes; legal notices are page text",
    "Victory": "no website: no town website found (web search 2026-11-02; the county site lists the board schedule only)",
    "Naples": "vendor blocked: legal notices and minutes are Google Drive folders; Drive's download endpoint is disallowed by robots.txt "
              "and the folder view renders by script",
    "Mamaroneck (village)": "vendor blocked: agendas are on Destiny (public.destinyhosted.com), a closed vendor",
    "Newstead": "no agenda page: the county-hosted site posts legal notices (hearing notices, SEQR letters, a rezoning application) but no "
                "agendas",
    "Pound Ridge": "crawl delay over cap: the agenda documents on townofpoundridge.gov need a crawl delay above the 10 s document cap",
    "Rotterdam": "JavaScript only: the Meetings pages (Town Board, Planning Commission, ZBA) list no documents in server HTML",
    "Royalton": "JavaScript only: the Minutes & Agendas page renders its document list by script",
    "Wilson": "JavaScript only: the CivicPlus Document Center folder 'Minutes and Agendas' renders by script; the site has no AgendaCenter",
    "Turin": "JavaScript only: meeting archives load by script and the public-notices posts carry no agendas (the same CMS as Lewis)",
    "Newcomb": "vendor blocked: Town Board agendas are Google Drive files; Drive's download endpoint is disallowed by robots.txt and the "
               "file page is a script viewer",
    "New Windsor": "vendor blocked: agendas and minutes are kept in a Laserfiche Portal repository (portal.laserfiche.com), which renders "
                   "by script and has no static listing",
    "Alabama": "no agenda page: the Town Board and Planning Board pages post meeting notices (a cancellation, one data-center information "
               "post) but no agendas; the Board Meeting Minutes page lists nothing in server HTML",
    "Carlisle": "no website: the county-hosted town page answers HTTP 404 and the Wikipedia infobox lists no site",
    "Gainesville": "JavaScript only: townofgainesvilleny.gov (found this wave) is a Wix site whose Agendas & Minutes page renders by script",
    "Mayville": "no agenda page: the village posts notices through a CMM notices embed (nothing dated in the window) and minutes; Village "
                "Board agendas are not online",
    "Greenwood": "no agenda page: the Minutes and Agenda page's newest council agenda is October 2023",
    "Yorktown": "bot wall: agendas are on calendar.yorktownny.gov (HTTP 403 'blocked due to security reasons') and ecode360.com/documents "
                "(robots.txt disallows all agents); the public-notices page carries a few hearing notices; not bypassed",
    "Rose": "unreachable: robots.txt answered 5xx or timed out from this sandbox (RFC 9309: treated as disallow); reachable in the pilot",
    "Oswegatchie": "agendas undated: monthly Town Board agendas (2026_<month>_agenda.pdf) are posted without a day; the latest was August 2026",
})
AGENDA_PLATFORM = {"civicplus": "CivicPlus AgendaCenter", "civicclerk": "CivicClerk", "legistar": "Legistar",
                   "escribe": "eSCRIBE", "agenda_page": "town website (general agenda-page reader)",
                   "generic_ny": "town website (hand listing)", "generic": "town website (hand listing)",
                   "cmm_compass": "Compass Web Development CMM embed"}
REASON_VOCAB = {   # discovery reason codes -> the site's reason codes (build.py REASON_TAG) and the pilot's words
    "bot_challenge": ("bot_challenge", "bot wall"), "waf_block": ("waf_block", "bot wall"),
    "robots_disallow": ("robots_disallow_site", "robots disallow"), "documents_blocked": ("robots_disallow_site", "robots disallow"),
    "vendor_blocked": ("vendor_blocked", "vendor blocked"), "vendor_robots_disallow": ("vendor_robots_disallow", "vendor blocked"),
    "crawl_delay_exceeds_cap": ("crawl_delay_exceeds_cap", "crawl delay over cap"), "js_only": ("js_only", "JavaScript only"),
    "no_agendas_found": ("no_agenda_listing_found", "no agenda page"), "no_recent_agendas": ("agendas_stale_or_undated", "agendas undated"),
    "no_website": ("no_agenda_listing_found", "no website"), "unreachable": ("no_agenda_listing_found", "unreachable"),
    "http_error": ("no_agenda_listing_found", "no agenda page"), "website_mismatch": ("no_agenda_listing_found", "no website"),
    "tls_error": ("no_agenda_listing_found", "unreachable"), "document_store": ("no_adapter", "vendor blocked"),
    "discovery_error": ("no_agenda_listing_found", "unreachable"),
}


def judge(row: dict, recs: list[dict], health: dict, report: dict, overrides: dict) -> tuple[bool, str | None, dict]:
    """(promote?, notes reason when not, evidence) from the last test run's output."""
    town = row["town"]
    ok_dated = [r for r in recs if r.get("status") == "ok" and r.get("meeting_date")]
    ok_any = [r for r in recs if r.get("status") == "ok"]
    errs = [e["error"] for e in report.get("errors", []) if e.get("town") == f"NY:{town}"]
    listing_errs = [e for e in errs if e.startswith("listing")]
    h = health.get(f"NY:{town}") or {}
    ev = {"documents_ok": len(ok_any), "documents_ok_dated": len(ok_dated), "hits": sum(len(r.get("hits") or []) for r in recs),
          "health": h.get("status"), "boards_ok": h.get("boards_ok"), "boards_failed": h.get("boards_failed"),
          "listing_errors": listing_errs[:3], "document_errors": len(errs) - len(listing_errs),
          "boards_with_dated_docs": sorted({r.get("board_key") for r in ok_dated if r.get("board_key")})}
    if town in overrides:
        return False, overrides[town], ev
    if not row.get("automated"):
        code = row.get("reason_code") or ""
        word = REASON_VOCAB.get(code, (code, code))[1]
        return False, f"{word}: {row.get('reason') or code}", ev
    if listing_errs or h.get("status") == "failed" or h.get("boards_failed"):
        return False, f"listing error in the last run: {(listing_errs or [h.get('last_error') or 'boards failed'])[0][:160]}", ev
    if not ok_dated:
        if ok_any:
            return False, "agendas undated: documents read but none carries a meeting date", ev
        return False, "no agenda page: the listing read without error but listed no document in the window", ev
    return True, None, ev


def legislative_body(row: dict) -> str:
    kind = row.get("kind")
    sb = next((l for l in row.get("listings") or [] if l.get("board_key") == "select_board"), None)
    if kind == "county":
        return "Board of Supervisors / Legislature"
    if kind == "city":
        return (sb or {}).get("board") if sb and re.search(r"council", sb.get("board", ""), re.I) else "City Council"
    if kind == "village":
        return "Village Board of Trustees"
    return "Town Board"


def promoted_row(row: dict, wave: int) -> dict:
    r = {k: v for k, v in row.items() if k not in ("website_candidates", "no_website_note", "wikipedia", "wave1_listings",
                                                     "wave1_curation_note", "wave1_reason_code")}
    r["state"] = "NY"
    src = r.get("selection_source") or ""
    r["selection_source_url"] = src if src.startswith("http") else None
    r["agenda_platform"] = AGENDA_PLATFORM.get(r.get("platform") or "", r.get("platform") or "unknown")
    if len(r.get("platforms") or []) > 1:
        r["agenda_platform"] += " + " + ", ".join(AGENDA_PLATFORM.get(p, p) for p in r["platforms"] if p != r.get("platform"))
    r["legislative_body"] = legislative_body(r)
    r["has_town_meeting"] = False
    r.setdefault("pop_2020", None)
    r["coverage"] = "direct"
    r.pop("coverage_note", None)
    r["promoted_from"] = f"wave{wave}"
    r["promoted_at"] = TODAY
    return r


def cmd_promote(args) -> None:
    from watch351.state import DocIndex, load_health
    wave = args.wave
    cfg_path, out_dir, overrides = (W1_CONFIG, W1_OUT, JUDGE_W1) if wave == 1 else (CONFIG / "towns_ny.json", NY_OUT, JUDGE_W2)
    doc = load(cfg_path)
    idx = DocIndex(out_dir / "state" / "docs")
    by_town: dict[str, list[dict]] = defaultdict(list)
    for rec in idx.records():
        by_town[rec["town"]].append(rec)
    health = load_health(out_dir / "state" / "town_health.json")
    runs = sorted((out_dir / "state" / "runs").glob("*.json"))
    report = load(runs[-1]) if runs else {}
    prod = load(PROD)
    have = {t["town"] for t in prod["towns"]}
    promoted, kept, log_rows = [], [], []
    for row in doc["towns"]:
        ok, note, ev = judge(row, by_town.get(row["town"], []), health, report, overrides)
        log_rows.append({"town": row["town"], "county": row["county"], "kind": row.get("kind"), "promote": ok,
                         "notes": note, "platform": row.get("platform"), "evidence": ev})
        if ok and row["town"] not in have:
            promoted.append(promoted_row(row, wave))
        else:
            r = dict(row)
            if ok and row["town"] in have:
                note = f"already in data/towns_ny.json"
            if r.get("automated"):
                r["automated"] = False
                r["status"] = "not_promoted"
            if isinstance(r.get("notes"), list):
                r["discovery_notes"] = r.pop("notes")
            r["notes"] = note
            r["promotion_judged"] = TODAY
            r["promotion_run"] = report.get("date")
            kept.append(r)
    print(f"wave {wave}: {len(promoted)} promoted, {len(kept)} kept in the test config"
          f"{' (dry run, nothing written)' if args.dry_run else ''}")
    for lr in log_rows:
        print(f"  {'PROMOTE' if lr['promote'] else 'keep   '} {lr['town']:<24} {str(lr['platform'] or '-'):<13} "
              f"docs ok/dated {lr['evidence']['documents_ok']}/{lr['evidence']['documents_ok_dated']} hits {lr['evidence']['hits']}"
              f"{'' if lr['promote'] else ' | ' + (lr['notes'] or '')[:110]}")
    save(W2 / f"promotion_wave{wave}.json", {"judged": now_iso(), "config": str(cfg_path.relative_to(DATA.parent)),
                                            "run_report": report.get("date"), "rows": log_rows})
    if args.dry_run:
        return
    # production file: append the promoted rows, refresh counts and the about line
    prod["towns"].extend(promoted)
    if wave == 1 or wave == 2:
        prod_rows_now = [{**t, "state": "NY"} for t in prod["towns"]]
        annotate_rows([], prod_rows_now)   # via-county coverage for site places we cannot read directly
        for t, a in zip(prod["towns"], prod_rows_now):
            for k in ("coverage", "coverage_county_body", "coverage_note"):
                if k in a:
                    t[k] = a[k]
                elif k in t:
                    del t[k]
    prod["count"] = len(prod["towns"])
    prod["automated"] = sum(1 for t in prod["towns"] if t.get("automated"))
    prod["generated"] = now_iso()
    tag = f"Wave {wave} promotion ({TODAY}): {len(promoted)} place{'s' if len(promoted) != 1 else ''} moved in from "
    tag += f"{cfg_path.relative_to(DATA.parent)} by `python3 experiments/wave2_test.py promote --wave {wave}`"
    if wave == 2:
        tag += ("; county rows (kind county, attribute_townships, county_body) are county planning boards read for GML 239-m "
                "referrals, and places with coverage via_county are read only through them")
    prod["_about"] = re.sub(r"\s*Wave %d promotion \([^)]*\):[^.]*\.?" % wave, "", prod["_about"]).rstrip() + " " + tag + "."
    save(PROD, prod)
    # test config: the rest, marked not automated with the reason
    doc["towns"] = kept
    doc["count"] = len(kept)
    doc["automated"] = sum(1 for r in kept if r.get("automated"))
    doc["generated"] = now_iso()
    doc["_about"] = re.sub(r"\s*Promotion \([^)]*\):[^.]*\.?", "", doc["_about"]).rstrip() + \
        f" Promotion ({TODAY}): {len(promoted)} rows moved to data/towns_ny.json; the rows here were not promoted " \
        f"(\"notes\" says why) and are kept for the next pass."
    save(cfg_path, doc)
    print(f"data/towns_ny.json: {prod['count']} places, {prod['automated']} automated")


def cmd_carry(args) -> None:
    """After `promote`: copy the promoted places' document records from the test index into data/state/docs/
    and their first-seen stamps into data/first_seen.json, so the production daily run neither re-downloads
    documents it has already read nor loses their first-seen times (lead time). Nothing else in data/state/
    is touched; data/hits_current.json is rebuilt by the daily run, not here."""
    from watch351.state import DocIndex, update_ledger
    out_dir = W1_OUT if args.wave == 1 else NY_OUT
    promoted = {t["town"] for t in prod_rows() if t.get("promoted_from") == f"wave{args.wave}"}
    src = DocIndex(out_dir / "state" / "docs")
    dst = DocIndex(DATA / "state" / "docs")
    n_new = n_have = 0
    for rec in src.records():
        if rec["town"] not in promoted or rec.get("state") != "NY":
            continue
        if rec["url"] in dst:
            n_have += 1
            continue
        dst.put(rec)
        n_new += 1
    if args.dry_run:
        print(f"wave {args.wave}: would carry {n_new} records ({n_have} already in data/state/docs) for {len(promoted)} places")
        return
    dst.save()
    added = update_ledger(dst, DATA / "first_seen.json")
    print(f"wave {args.wave}: carried {n_new} document records for {len(promoted)} places into data/state/docs "
          f"({n_have} were already there); {added} first-seen entries added to data/first_seen.json")


# ------------------------------------------------------------------------------------ unblock drafts
BOT_PAGE = "https://agendaahead.vercel.app/bot"
KEY_DIR = "https://agendaahead.vercel.app/.well-known/http-message-signatures-directory"
DRAFT_KINDS = {   # reason code -> (kind of ask, the one-line explanation of what we saw)
    "bot_challenge": ("cloudflare", "answers a Cloudflare bot check (HTTP 403, 'Just a moment') to our reader"),
    "waf_block": ("firewall", "answers HTTP 403 from its firewall to our reader on every page"),
    "crawl_delay_exceeds_cap": ("crawl_delay", "asks in robots.txt for a crawl delay longer than the 10 seconds we honour for documents"),
    "robots_disallow": ("robots", "disallows our reader in robots.txt"),
    "documents_blocked": ("robots", "disallows the agenda documents in robots.txt"),
    "vendor_blocked": ("vendor", "keeps its agendas on a vendor host that turns automatic readers away"),
    "vendor_robots_disallow": ("vendor", "keeps its agendas on a vendor host whose robots.txt disallows every automatic reader"),
    "tls_error": ("tls", "serves a TLS certificate that does not match its host name, so we cannot read it over a verified connection"),
    "undecodable_response": ("firewall", "returns a body our reader cannot decode (Sucuri / Cloudflare front end)"),
}


def _draft(place: dict) -> str | None:
    code = place.get("reason_code") or ""
    if code not in DRAFT_KINDS:
        return None
    kind, saw = DRAFT_KINDS[code]
    name = place["town"] if place.get("kind") == "county" else \
        f"{'City' if place.get('kind') == 'city' else 'Village' if place.get('kind') == 'village' else 'Town'} of {re.sub(r' \(.*\)$', '', place['town'])}"
    site = place.get("final_url") or place.get("website") or ""
    host = re.sub(r"^https?://", "", site).split("/")[0]
    detail = (place.get("reason") or "").rstrip(".")
    ask = {
        "cloudflare": (f"add AgendaAheadBot to the allow list in your Cloudflare dashboard (Security, Bots: allow verified bots, or a "
                       f"WAF rule for the user agent AgendaAheadBot), or ask Cloudflare to pass it through"),
        "firewall": "allow the user agent AgendaAheadBot through the firewall rule that returns 403, for the agenda pages only",
        "crawl_delay": ("confirm that one request every 15 to 20 seconds is acceptable for the agenda pages, or lower the Crawl-delay "
                        "in robots.txt to 10 seconds for User-agent: AgendaAheadBot"),
        "robots": "add two lines to robots.txt: User-agent: AgendaAheadBot and Allow: / (or Allow: for the agenda folder only)",
        "vendor": ("ask your agenda vendor to allow the user agent AgendaAheadBot on the public agenda pages, or post the agenda "
                   "PDFs on your own site as well"),
        "tls": "renew or re-issue the site's TLS certificate so that it is valid for the host name people type",
    }[kind]
    lines = [
        f"### {name} ({place.get('county')} County): {host or 'site'}",
        "",
        f"**To:** the Town Clerk or website manager (address to be filled in). **Subject:** Reading {name}'s meeting agendas",
        "",
        f"Hello,",
        "",
        f"I run Agenda Ahead ({BOT_PAGE}), a small service that reads town board, planning board and zoning board agendas "
        f"the morning they are posted and tells residents, developers and lawyers when an item about battery storage, solar, "
        f"data centers, zoning or housing is coming up. Everything links back to your own agenda page; we publish no documents.",
        "",
        f"Our reader, AgendaAheadBot, cannot read {name}'s agendas today: {host or 'the site'} {saw}"
        f"{' (' + detail + ')' if detail and detail not in saw else ''}. We did not try to get around that.",
        "",
        f"How we read: one request per second at most per site, agendas and minutes only, no logins, no forms, robots.txt obeyed "
        f"on every page, and every request is signed (Web Bot Auth, key directory {KEY_DIR}) so you can verify it is us.",
        "",
        f"The ask: {ask}. If you would rather send agendas another way (an email list, an RSS feed, a calendar export), that works too.",
        "",
        f"We stop on request, and I can send a monthly log of our requests to your site if that helps. Thank you for considering it.",
        "",
        "[name], Agenda Ahead",
        "[email]",
        "",
    ]
    return "\n".join(lines)


def cmd_drafts(args) -> None:
    """research_notes/Expansion/ny_unblock_drafts.md: one short email per place that needs permission."""
    rows = prod_rows() + [{**t, "state": "NY"} for t in (load(CONFIG / "towns_ny.json", {}) or {}).get("towns", [])] \
        + w1_rows()
    seen, places = set(), []
    for r in rows:
        if r.get("automated") or r["town"] in seen:
            continue
        seen.add(r["town"])
        if (r.get("reason_code") or "") in DRAFT_KINDS:
            places.append(r)
    by_kind = defaultdict(list)
    for p in places:
        by_kind[DRAFT_KINDS[p["reason_code"]][0]].append(p)
    order = ["cloudflare", "firewall", "crawl_delay", "vendor", "robots", "tls"]
    labels = {"cloudflare": "Cloudflare bot checks", "firewall": "Firewall and front-end blocks", "crawl_delay": "Crawl delays over the cap",
              "vendor": "Vendor hosts that block readers", "robots": "robots.txt disallows", "tls": "TLS certificate problems"}
    out = [f"# New York: unblock requests to send ({TODAY})", "",
           f"Drafts, not sent. One short email per place whose site we cannot read without permission, in the vocabulary of "
           f"cheap_township_coverage.md section 8 (who we are, what we read, how much, why, the ask, the offer). Generated by "
           f"`python3 experiments/wave2_test.py drafts` from the reason codes in data/towns_ny.json and the wave configs; "
           f"{len(places)} places in all. Fill in the clerk's address (the town site's contact page) and your name before sending. "
           f"Places with no website, no agenda page or undated agendas are not here: there is nothing to unblock.", ""]
    out += ["## Summary", "", "| Ask | Places |", "|---|---|"]
    for k in order:
        if by_kind.get(k):
            out.append(f"| {labels[k]} | {', '.join(sorted(p['town'] for p in by_kind[k]))} |")
    out.append("")
    out += ["## One ask that covers several places", "",
            "- **Cloudflare, once for all of them:** submit AgendaAheadBot to Cloudflare's Verified Bots program (BotBase submission "
            "form; Web Bot Auth signing is already live, see OPERATIONS.md). Towns on the free plan's Bot Fight Mode cannot allow "
            "us themselves, so the program is the only route for them; the emails below ask the others to allow the agent directly.",
            "- **eCode360 (General Code):** New Castle's agendas sit under ecode360.com/documents/, disallowed for all agents; one "
            "request to General Code covers every town that posts agendas there.",
            "- **HeyGov:** api.heygov.com disallows all bots; one request to HeyGov covers Gardiner and any other HeyGov town.",
            "- **eSCRIBE:** Southampton's PDF downloads challenge the browser; one request to eSCRIBE (or the town) covers it.", ""]
    for k in order:
        if not by_kind.get(k):
            continue
        out += [f"## {labels[k]} ({len(by_kind[k])})", ""]
        for p in sorted(by_kind[k], key=lambda p: p["town"]):
            out.append(_draft(p))
    dest = DATA.parent.parent.parent / "research_notes" / "Expansion" / "ny_unblock_drafts.md"
    dest.write_text("\n".join(out))
    print("wrote", dest, f"({len(places)} drafts)", {k: len(v) for k, v in by_kind.items()})


# ------------------------------------------------------------------------------------ lead time
def cmd_leadtime(args) -> None:
    """Posting lead time for the New York places promoted from waves 1 and 2: CivicPlus AgendaCenter 'Posted'
    stamps (a true first-posting time, read from the AgendaCenter search page of each promoted CivicPlus town, past
    365 days) and our own first fetch for upcoming meetings in the wave-2 test index. Writes
    data/test/wave2/leadtime_ny_wave2.json."""
    from watch351.adapters.civicplus import CivicPlusAdapter
    from watch351.discover_census import civicplus_rows
    from watch351.models import Window
    from watch351.state import DocIndex
    from datetime import timedelta
    f = PoliteFetcher()
    cp = CivicPlusAdapter(f)
    today = date.today()
    window = Window(today - timedelta(days=365), today + timedelta(days=120))
    promoted = [t for t in prod_rows() if t.get("promoted_from") in ("wave1", "wave2") and t.get("automated")]
    stamps = []
    for t in promoted:
        cids = [l["category_id"] for l in t.get("listings", []) if l.get("category_id")]
        if not cids:
            continue
        site = (t.get("final_url") or t.get("website") or "").rstrip("/")
        from urllib.parse import urlsplit
        parts = urlsplit(site)
        site = f"{parts.scheme}://{parts.netloc}"
        try:
            with f.purpose("listing"):
                resp = cp.get_listing(f"{site}/AgendaCenter/Search/", params={
                    "term": "", "CIDs": ",".join(cids) + ",", "startDate": window.start.strftime("%m/%d/%Y"),
                    "endDate": window.end.strftime("%m/%d/%Y"), "dateRange": "", "dateSelector": ""})
        except FetchError as e:
            print(f"  {t['town']}: {str(e)[:100]}")
            continue
        for r in civicplus_rows(resp):
            if r.get("posted") and r.get("meeting_date") and r.get("posted_kind") == "posted":
                posted = datetime.fromisoformat(r["posted"])
                meeting = datetime.fromisoformat(r["meeting_date"])
                days = round((meeting - posted).total_seconds() / 86400, 2)
                stamps.append({"town": t["town"], "category": r["category"], "meeting_date": r["meeting_date"],
                               "posted": r["posted"], "days_before": days, "url": r["url"]})
        print(f"  {t['town']:<16} {sum(1 for s_ in stamps if s_['town'] == t['town'])} posted stamps", flush=True)
    pre = [s_["days_before"] for s_ in stamps if s_["days_before"] > 0]
    by_town = {}
    for town in sorted({s_["town"] for s_ in stamps}):
        ds = [s_["days_before"] for s_ in stamps if s_["town"] == town and s_["days_before"] > 0]
        after = sum(1 for s_ in stamps if s_["town"] == town and s_["days_before"] <= 0)
        by_town[town] = {"n": len(ds), "median_days": round(median(ds), 1) if ds else None,
                         "share_72h": round(100 * sum(1 for d in ds if d >= 2.21) / len(ds)) if ds else None,
                         "posted_after_meeting": after}
    # our own first fetch (wave-2 test index), meetings still ahead when first seen
    idx = DocIndex(NY_OUT / "state" / "docs")
    own = []
    for rec in idx.records():
        if rec.get("meeting_date") and rec.get("first_seen"):
            d = (datetime.fromisoformat(rec["meeting_date"]) - datetime.fromisoformat(rec["first_seen"]).replace(tzinfo=None)).total_seconds() / 86400
            if d > 0:
                own.append(round(d, 2))
    out = {"generated": now_iso(), "note": "days from the stamp to 00:00 of the meeting day (most boards meet 6 to 7:30 pm, so these "
                                           "understate the lead); share_72h = at least 2.21 days, i.e. 72 hours before a 7 pm meeting",
           "civicplus_posted": {"n": len(pre), "median_days": round(median(pre), 1) if pre else None,
                                "p10_days": round(sorted(pre)[max(0, len(pre) // 10 - 1)], 1) if pre else None,
                                "share_72h": round(100 * sum(1 for d in pre if d >= 2.21) / len(pre)) if pre else None,
                                "posted_after_meeting": sum(1 for s_ in stamps if s_["days_before"] <= 0), "by_town": by_town},
           "own_first_fetch_wave2": {"n": len(own), "median_days": round(median(own), 1) if own else None,
                                     "note": "bounded by the test run dates; a daily crawl would see agendas as soon as they post"},
           "stamps": sorted(stamps, key=lambda s_: (s_["town"], s_["meeting_date"]))}
    save(W2 / "leadtime_ny_wave2.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "stamps"}, indent=1))


# ------------------------------------------------------------------------------------ analyze
def cmd_analyze(args) -> None:
    from watch351.state import DocIndex
    cfg = load(CONFIG / "towns_ny.json", {}) or {}
    rows = cfg.get("towns", [])
    prod = prod_rows()
    runs = sorted((NY_OUT / "state" / "runs").glob("*.json"))
    report = load(runs[-1]) if runs else {}
    idx = DocIndex(NY_OUT / "state" / "docs")
    recs = idx.records()
    hits = (load(NY_OUT / NY_HITS, {}) or {}).get("hits", [])
    promoted = [t for t in prod if t.get("promoted_from") == "wave2"]
    out = {
        "generated": now_iso(),
        "config": {"rows": len(rows), "automated": sum(1 for r in rows if r.get("automated")),
                   "places": sum(1 for r in rows if r.get("kind") != "county"),
                   "county_boards": sum(1 for r in rows if r.get("kind") == "county"),
                   "by_reason": dict(Counter(r.get("reason_code") or "automated" for r in rows)),
                   "by_platform": dict(Counter(r.get("platform") for r in rows if r.get("automated"))),
                   "coverage": dict(Counter(r.get("coverage") or "none" for r in rows if r.get("kind") != "county"))},
        "promoted_wave2": {"n": len(promoted), "by_county": dict(Counter(t["county"] for t in promoted)),
                           "by_platform": dict(Counter(t.get("platform") for t in promoted)),
                           "by_kind": dict(Counter(t.get("kind") for t in promoted))},
        "production": {"places": len(prod), "automated": sum(1 for t in prod if t.get("automated")),
                       "via_county": sorted(t["town"] for t in prod if t.get("coverage") == "via_county")},
        "last_run": {k: report.get(k) for k in ("date", "towns_attempted", "towns_succeeded", "towns_failed", "towns_partial",
                                                "documents_listed", "new_documents", "document_errors", "errors_total", "hits_current")},
        "index": idx.stats(),
        "documents_by_town": {t: dict(Counter("dated" if r.get("meeting_date") else "undated" for r in rs))
                              for t, rs in sorted(((t, [r for r in recs if r["town"] == t]) for t in {r["town"] for r in recs}))},
        "hits_by_topic": dict(Counter(t for h in hits for t in h["topics"]).most_common()),
        "hits_by_town": dict(Counter(h["town"] for h in hits).most_common()),
        "attributed_hits": sum(1 for h in hits if h.get("board_key") == "planning_board" and "County" in (h.get("board") or "")),
    }
    # lead time: our own first sighting against the meeting day, for meetings still ahead at first sight
    ahead = [h["days_before_meeting"] for h in hits if isinstance(h.get("days_before_meeting"), (int, float)) and h["days_before_meeting"] > 0]
    out["lead_time_days_first_seen"] = {"n": len(ahead), "median": round(median(ahead), 1) if ahead else None,
                                        "share_72h": round(100 * sum(1 for d in ahead if d >= 2.21) / len(ahead)) if ahead else None,
                                        "note": "our own first fetch (bounded by the run dates), not the town's posting stamp"}
    save(W2 / "analysis_ny_wave2.json", out)
    print(json.dumps(out, indent=1)[:6000])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["targets", "websites", "discover", "curate", "annotate", "crawl", "sample", "promote",
                                       "carry", "drafts", "analyze", "probe", "leadtime", "peek"])
    p.add_argument("--grep", help="peek: regex for the links to show")
    p.add_argument("--text", type=int, help="peek: also print this many characters of the page text")
    p.add_argument("--interval", type=float, help="websites: seconds between Wikipedia pages (default 12)")
    p.add_argument("--places")
    p.add_argument("--counties", action="store_true", help="discover: the county planning boards instead of the places")
    p.add_argument("--force", action="store_true", help="websites: look up places that already have a site")
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--label", default="run1")
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=120)
    p.add_argument("--subdir", help="crawl / sample: output directory under data/test/wave2 (default ny)")
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--seed", type=int, default=2031)
    p.add_argument("--exclude", help="sample: comma-separated worksheets under data/test/wave2 already judged")
    p.add_argument("--out", help="sample: worksheet file name (default worksheet_ny.json)")
    p.add_argument("--wave", type=int, default=2, choices=[1, 2])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    globals()[f"cmd_{args.command}"](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
