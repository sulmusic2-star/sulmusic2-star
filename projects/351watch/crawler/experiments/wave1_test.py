#!/usr/bin/env python3
"""Agenda Ahead Wave 1 test (2026-10): Vermont Act 250, the Connecticut Siting Council, and 50 more
New York towns. Everything is gated: nothing here writes data/hits_current.json, data/state/ or
data/sources/.

    cd projects/351watch/crawler
    python3 experiments/wave1_test.py towns                 # data/towns_vt.json, data/towns_ct.json (gated)
    python3 experiments/wave1_test.py feeds                 # VT + CT sources -> data/test/wave1/sources/
    python3 experiments/wave1_test.py discover [--places A,B]   # NY targets -> data/test/wave1/config/towns_ny.json
    python3 experiments/wave1_test.py crawl --label run1    # NY towns -> data/test/wave1/ny/
    python3 experiments/wave1_test.py combine               # data/test/wave1/hits_wave1.json + validation
    python3 experiments/wave1_test.py sample --source ny --n 60 --seed 2028   # hand-check worksheet
    python3 experiments/wave1_test.py analyze               # coverage, errors, sample results

Town lists: Wikipedia's "List of municipalities in Vermont" and "List of towns in Connecticut" (towns,
counties, planning regions, villages / boroughs as aliases), read once through PoliteFetcher.

New York wave-1 towns live in data/test/wave1/config/towns_ny.json, outside the data/towns_*.json glob,
because New York is a published state: build.py renders every row of every data/towns_*.json for a
published state, so a gated NY file there would put 50 new town pages on the production site. The config
file is still marked "gated" (watch351.daily crawls it only with --states NY and an --output-dir other
than its own directory). Promotion = moving its rows into data/towns_ny.json.

All network access goes through watch351.fetch.PoliteFetcher (AgendaAheadBot UA, robots.txt on every
hop, <= 1 request/second/host, crawl-delay honoured up to the cap, no logins, no POSTs, no challenge
solving).
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

HERE = Path(__file__).resolve().parent
CRAWLER = HERE.parent
sys.path.insert(0, str(CRAWLER))

from bs4 import BeautifulSoup  # noqa: E402

from watch351 import current  # noqa: E402
from watch351.fetch import PoliteFetcher  # noqa: E402

DATA = CRAWLER.parent / "data"
W1 = DATA / "test" / "wave1"
CONFIG = W1 / "config"
NY_OUT = W1 / "ny"
SOURCES = W1 / "sources"
NY_HITS = "hits_ny_wave1.json"
ALL3 = ["select_board", "planning_board", "zoning_board_of_appeals"]


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


# ------------------------------------------------------------------------------------ towns
WP_VT = "https://en.wikipedia.org/wiki/List_of_municipalities_in_Vermont"
WP_CT = "https://en.wikipedia.org/wiki/List_of_towns_in_Connecticut"


def _cells(tr) -> list[str]:
    out = []
    for c in tr.find_all(["th", "td"]):
        for sup in c.find_all("sup"):
            sup.decompose()
        out.append(re.sub(r"\s+", " ", c.get_text(" ", strip=True)).strip())
    return out


def _int(s: str) -> int | None:
    s = re.sub(r"[^\d]", "", s or "")
    return int(s) if s else None


def cmd_towns(args) -> None:
    f = PoliteFetcher()
    with f.purpose("listing"):
        vt = BeautifulSoup(f.get(WP_VT, max_age=30 * 86400).text, "lxml")
        ct = BeautifulSoup(f.get(WP_CT, max_age=30 * 86400).text, "lxml")
    # ---------------- Vermont: municipalities (+ gores / unincorporated), villages as aliases
    rows: dict[str, dict] = {}
    tables = vt.find_all("table", class_="wikitable")
    raw = []
    for t in tables[:2]:
        for tr in t.find_all("tr")[1:]:
            c = _cells(tr)
            if len(c) < 4 or not c[0]:
                continue
            name = re.sub(r"\s*\(.*?\)\s*", "", c[0]).strip()
            county = re.sub(r"\s*\(.*?\)", "", c[2]).replace(" County", "").strip()
            kind = re.sub(r"\s*\(.*?\)", "", c[1]).strip().lower()
            raw.append((name, kind, county, _int(c[3])))
    names = Counter(n for n, *_ in raw)
    for name, kind, county, pop in raw:
        # a city and a town of the same name (Barre, Newport, Rutland, St. Albans): "Barre City", "Barre Town",
        # as Vermont itself names them
        full = f"{name} {kind.split()[-1].title()}" if names[name] > 1 else name
        rows[full] = {"town": full, "state": "VT", "county": county, "kind": kind, "pop_2020": pop,
                      "aliases": [full.replace("St. ", "Saint ")] if full.startswith("St. ") else []}
    for t in tables[2:4]:
        for tr in t.find_all("tr")[1:]:
            c = _cells(tr)
            if len(c) >= 2 and c[1] in rows and c[0] != c[1]:
                rows[c[1]]["aliases"].append(f"{c[0]} Village")
                rows[c[1]]["aliases"].append(c[0])
    # Act 250 / ePUC spellings
    extra = {"Essex": ["Essex, Town of"], "Essex Junction": ["Essex Junction, City of"],
             "Buels Gore": ["Buel's Gore"], "Averys Gore": ["Avery's Gore"], "Warners Grant": ["Warner's Grant"],
             "Warrens Gore": ["Warren's Gore"], "St. Albans City": ["Saint Albans City"],
             "St. Albans Town": ["Saint Albans Town"], "St. George": ["Saint George"],
             "St. Johnsbury": ["Saint Johnsbury"]}
    for k, al in extra.items():
        if k in rows:
            rows[k]["aliases"] += al
    note = ("Act 250 land-use permits for projects in this town reach us through the state's daily Act 250 "
            "agenda; the town's own agendas are not read.")
    vt_rows = []
    for r in sorted(rows.values(), key=lambda r: r["town"]):
        vt_rows.append({**r, "automated": False, "coverage": "state_feed", "coverage_sources": ["vt_act250"],
                        "coverage_note": note})
    save(DATA / "towns_vt.json", {
        "_about": "Agenda Ahead Wave 1 test (2026-10): every Vermont municipality (Wikipedia list, read "
                  f"{date.today().isoformat()}), for the Act 250 state feed (watch351/sources/vt_act250.py). No town "
                  "agendas are crawled (automated: false). Built by `python3 experiments/wave1_test.py towns`.",
        "generated": now_iso(), "state": "VT", "gated": True,
        "gate_note": "Test state: not part of the production daily run or site. Items are written only to "
                     "data/test/wave1/sources/ by `python3 -m watch351.sources.vt_act250`.",
        "source_url": WP_VT, "count": len(vt_rows), "towns": vt_rows})
    # ---------------- Connecticut: 169 towns, county and planning region, boroughs / cities as aliases
    rows = {}
    tables = ct.find_all("table", class_="wikitable")
    hdr = _cells(tables[0].find("tr"))
    ix = {h.split(" [")[0].strip(): i for i, h in enumerate(hdr)}
    for tr in tables[0].find_all("tr")[1:]:
        c = _cells(tr)
        if len(c) < len(hdr):
            continue
        name = c[ix["Name"]]
        rows[name] = {"town": name, "state": "CT", "county": c[ix["County"]].replace(" County", ""),
                      "planning_region": c[ix["Planning region"]], "kind": c[ix["Designation"]].lower(),
                      "pop_2020": _int(c[ix["Population (2020)"]]), "aliases": []}
    for t in tables[1:]:
        h = [x.split(" [")[0] for x in _cells(t.find("tr"))]
        if "Parent town" not in h:
            continue
        pi = h.index("Parent town")
        for tr in t.find_all("tr")[1:]:
            c = _cells(tr)
            if len(c) > pi and c[pi] in rows and c[0] != c[pi]:
                rows[c[pi]]["aliases"].append(c[0])
    note = ("Energy and telecommunications facilities here are decided by the Connecticut Siting Council; its "
            "petitions, dockets and hearings for this town reach us through the Council's listings. The town's own "
            "agendas are not read.")
    ct_rows = [{**r, "automated": False, "coverage": "state_feed", "coverage_sources": ["ct_siting_council"],
                "coverage_note": note} for r in sorted(rows.values(), key=lambda r: r["town"])]
    save(DATA / "towns_ct.json", {
        "_about": "Agenda Ahead Wave 1 test (2026-10): Connecticut's 169 towns (Wikipedia list, read "
                  f"{date.today().isoformat()}; county = historical county, planning_region = the Census county-"
                  "equivalent since 2022), for the Siting Council state feed (watch351/sources/ct_siting.py). No "
                  "town agendas are crawled (automated: false). Built by `python3 experiments/wave1_test.py towns`.",
        "generated": now_iso(), "state": "CT", "gated": True,
        "gate_note": "Test state: not part of the production daily run or site. Items are written only to "
                     "data/test/wave1/sources/ by `python3 -m watch351.sources.ct_siting`.",
        "source_url": WP_CT, "count": len(ct_rows), "towns": ct_rows})
    print(f"VT {len(vt_rows)} municipalities ({Counter(r['kind'] for r in vt_rows)}), "
          f"CT {len(ct_rows)} towns; fetcher {f.stats}")


# ------------------------------------------------------------------------------------ NY targets
CARINA = "https://carina.energy/bess-moratoriums/"
PILOT = "research_notes/Expansion/ny_pilot.md (Next 50 towns to add)"
FIGHTS = "research_notes/Meeting monitor national expansion/data_center_and_other_fights.md"
# (town, county, kind, group, reason, source). Status and end dates are Carina's BESS Moratorium Monitor as
# read on 2026-10-12 (88 NY rows in force or recent); the order follows the pilot's next-50 list: a renewal,
# extension or permanent BESS law is most likely on an agenda soon where a moratorium ends soonest.
NY_TARGETS = [
    ("Carlisle", "Schoharie", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2026-10-21", CARINA),
    ("Gainesville", "Wyoming", "town", "bess_moratorium", "BESS moratorium (all BESS) ACTIVE, ends 2026-10-20", CARINA),
    ("Brasher", "St. Lawrence", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2026-10-31", CARINA),
    ("Sherman", "Chautauqua", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2026-10-31", CARINA),
    ("Corning", "Steuben", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2026-11-20 (Carina: Corning, Steuben County)", CARINA),
    ("Campbell", "Steuben", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2026-11-30", CARINA),
    ("Clymer", "Chautauqua", "town", "bess_moratorium", "BESS moratorium (all BESS) ACTIVE, ends 2027-01-31", CARINA),
    ("Greig", "Lewis", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2027-01-14; Lewis County has 6 local restrictions (Sabin)", CARINA),
    ("Denmark", "Lewis", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2027-01-21", CARINA),
    ("Schroeppel", "Oswego", "town", "bess_moratorium", "Solar-plus-storage moratorium ACTIVE, ends 2027-02-10", CARINA),
    ("Lewis", "Lewis", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2027-03-16", CARINA),
    ("Northampton", "Fulton", "town", "bess_moratorium", "BESS moratorium (all BESS) ACTIVE, ends 2027-03-30", CARINA),
    ("Glen Cove", "Nassau", "city", "bess_moratorium", "BESS moratorium ACTIVE, ends 2027-05-13", CARINA),
    ("Mayville", "Chautauqua", "village", "bess_moratorium", "BESS moratorium ACTIVE, ends 2027-06-01", CARINA),
    ("Benson", "Hamilton", "town", "bess_moratorium", "BESS moratorium (all BESS) ACTIVE, ends 2027-06-09", CARINA),
    ("Arietta", "Hamilton", "town", "bess_moratorium", "BESS moratorium (all BESS) ACTIVE, ends 2027-06-22", CARINA),
    ("Eden", "Erie", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2026-12-29 (extended from 2026-09-30)", CARINA),
    ("Collins", "Erie", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Virgil", "Cortland", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Maine", "Broome", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Norfolk", "St. Lawrence", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Oswegatchie", "St. Lawrence", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Palatine", "Montgomery", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Pike", "Wyoming", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Mentz", "Cayuga", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Carlton", "Orleans", "town", "bess_moratorium", "BESS moratorium ACTIVE, ends 2027-04-14 (extended)", CARINA),
    ("Allen", "Allegany", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-30: extension or law due", CARINA),
    ("Angelica", "Allegany", "town", "bess_moratorium", "BESS moratorium EXPIRED 2026-04-30: law or renewal", CARINA),
    ("Dunkirk", "Chautauqua", "city", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-09-09: extension or law due", CARINA),
    ("Westfield", "Chautauqua", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-31: extension or law due", CARINA),
    ("Root", "Montgomery", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-31: extension or law due", CARINA),
    ("Greenwood", "Steuben", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-31: extension or law due", CARINA),
    ("Prattsburgh", "Steuben", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-31: extension or law due", CARINA),
    ("Ellery", "Chautauqua", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-31: extension or law due", CARINA),
    ("North Harmony", "Chautauqua", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-30: extension or law due", CARINA),
    ("West Bloomfield", "Ontario", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-08-13: extension or law due", CARINA),
    ("Rose", "Wayne", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-07-03: extension or law due", CARINA),
    ("Stockport", "Columbia", "town", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-06-01: extension or law due", CARINA),
    ("Peekskill", "Westchester", "city", "bess_moratorium", "BESS moratorium ACTIVE, ended 2026-05-31: extension or law due", CARINA),
    ("Yonkers", "Westchester", "city", "bess_moratorium", "BESS moratorium ACTIVE to 2026-03-31; large city", CARINA),
    ("Yorktown", "Westchester", "town", "bess_law", "BESS moratorium EXPIRED 2026-01-14: BESS law follow-up", CARINA),
    ("Riverhead", "Suffolk", "town", "bess_law", "Early Long Island BESS moratorium (expired 2024-02-03); BESS proposals since", CARINA),
    ("Montgomery", "Orange", "town", "bess_law", "BESS moratorium LIFTED 2026-03-31: law adopted, applications next", CARINA),
    ("Plattekill", "Ulster", "town", "bess_law", "BESS ban LIFTED 2026-03-31", CARINA),
    ("Mount Pleasant", "Westchester", "town", "bess_law", "BESS ban LIFTED 2026-03-31", CARINA),
    ("Somerset", "Niagara", "town", "bess_law", "BESS moratorium LIFTED 2026-03-31; former coal-plant site", CARINA),
    ("Sherburne", "Chenango", "town", "bess_fight", "January 2026 moratorium hearing tied to a Nexamp BESS proposal",
     "https://eticaag.com/sherburne-ny-approves-battery-storage-moratorium/"),
    ("Albany", "Albany", "city", "data_center_fight", "Data-center regulations advancing; South End opposition",
     "https://www.wamc.org/news/2026-06-03/albany-data-center-regulations-advance"),
    ("Massena", "St. Lawrence", "town", "data_center_fight", "Town board voted 3-2 against a data-center moratorium (2026)", FIGHTS),
    ("North Tonawanda", "Niagara", "city", "data_center_fight", "Extended its data-center moratorium a year (disputed mine-to-AI conversion)", FIGHTS),
]


# Official websites, found by web search on 2026-10-12 (Wikipedia infoboxes list few of them). A list gives
# candidates tried in order; None = no town website found (Gainesville's and Pike's pages are county-hosted
# notices at most). Carlisle and Root post through county-hosted town pages.
WEBSITES: dict[str, list[str] | None] = {
    "Carlisle": ["https://www4.schohariecounty-ny.gov/government/town-of-carlisle/",
                 "https://www2.schohariecounty-ny.gov/EdocWebApp/faces/TownCar/index.xhtml"],
    "Gainesville": None,
    "Brasher": ["https://townofbrasher.gov/"],
    "Sherman": ["https://www.shermanny.gov/", "https://townofsherman.net/"],
    "Corning": ["https://townofcorningny.gov/"],
    "Campbell": ["https://www.campbellny.gov/"],
    "Clymer": ["https://www.townofclymerny.gov/"],
    "Greig": ["https://townofgreig.gov/"],
    "Denmark": ["https://townofdenmarkny.gov/", "https://denmark.racog.org/"],
    "Schroeppel": ["https://schroeppelny.gov/"],
    "Lewis": ["https://townoflewislcny.gov/"],
    "Northampton": ["http://townofnorthampton.com/"],
    "Glen Cove": ["https://glencoveny.gov/"],
    "Mayville": ["https://www.mayvilleny.gov/"],
    "Benson": None,    # townofbenson.com is Benson, North Carolina (checked 2026-10-12)
    "Arietta": ["http://www.townofarietta.com/"],
    "Eden": ["https://edenny.gov/"],
    "Collins": ["https://www.townofcollins.com/"],
    "Virgil": ["https://virgilny.gov/"],
    "Maine": ["https://townofmaineny.gov/"],
    "Norfolk": ["https://norfolkny.com/"],
    "Oswegatchie": ["https://www.townofoswegatchie.gov/"],
    "Palatine": ["http://townofpalatine.org/"],
    "Pike": None,
    "Mentz": ["http://townofmentz.com/"],
    "Carlton": ["https://townofcarltonny.gov/", "https://townofcarlton.org/"],
    "Allen": ["https://townclerktownofall.wixsite.com/town-of-allen-ny"],
    "Angelica": ["https://www.angelicany.org/"],
    "Dunkirk": ["https://cityofdunkirk.com/"],
    "Westfield": ["http://www.townofwestfield.org/"],
    "Root": ["https://www.montgomerycountyny.gov/web/municipal/root/"],
    "Greenwood": ["https://greenwoodny.gov/"],
    "Prattsburgh": ["https://www.townofprattsburgh.org/"],
    "Ellery": ["http://elleryny.org/"],
    "North Harmony": ["https://townofnorthharmony.gov/"],
    "West Bloomfield": ["https://westbloomfieldny.gov/"],
    "Rose": ["https://roseny.gov/"],
    "Stockport": ["https://www.stockportny.gov/"],
    "Peekskill": ["https://www.cityofpeekskillny.gov/"],
    "Yonkers": ["https://www.yonkersny.gov/"],
    "Yorktown": ["https://www.yorktownny.gov/"],
    "Riverhead": ["https://www.townofriverheadny.gov/"],
    "Montgomery": ["https://townofmontgomery.com/"],
    "Plattekill": ["https://townofplattekill.gov/"],
    "Mount Pleasant": ["https://www.mtpleasantny.com/"],
    "Somerset": ["http://www.somersetny.org/"],
    "Sherburne": ["https://townofsherburne.gov/", "https://townofsherburne.net/"],
    "Albany": ["https://www.albanyny.gov/"],
    "Massena": ["https://www.massena.us/"],
    "North Tonawanda": ["https://www.northtonawanda.gov/"],
}


def cmd_targets(args) -> None:
    rows = []
    for town, county, kind, group, why, src in NY_TARGETS:
        sites = WEBSITES.get(town)
        rows.append({"town": town, "state": "NY", "county": county, "kind": kind,
                     "website": sites[0] if sites else None, "website_candidates": sites or [],
                     "website_source": "web search 2026-10-12" if sites else None,
                     "no_website_note": None if sites else "no town website found (web search 2026-10-12)",
                     "selection_group": group, "selection_reason": why, "selection_source": src})
    save(W1 / "targets_ny.json", rows)
    print(len(rows), "targets;", sum(1 for r in rows if r["website"]), "with a website;",
          dict(Counter(r["selection_group"] for r in rows)))


# ------------------------------------------------------------------------------------ NY discovery
# Hand corrections after reading the sites (2026-10-12), each with the reason. Applied on top of discovery.
_CMM_RULES = [["planning", "Planning Board", "planning_board"],
              ["zoning|ZBA|appeals", "Zoning Board of Appeals", "zoning_board_of_appeals"]]
CURATED_NY: dict[str, dict] = {
    # The agenda is the page itself ("FIRE COMMISSIONERS' and EDEN TOWN BOARD MEETING October 14, 2026 ..."),
    # and the page's navigation links a budget and a zoning map, so the general reader needs self_page: force.
    "Eden": {"add_listings": [{"board": "Town Board", "board_key": "select_board", "platform": "agenda_page",
                               "url": "https://edenny.gov/agendas-minutes/", "self_page": "force"}],
             "curation_note": "Town Board agenda posted as the page itself (HTML), read as one document per meeting"},
    # Town Board hearing notices posted on the homepage ("09212026_NOTICE OF PUBLIC HEARING ...").
    "Maine": {"add_listings": [{"board": "Town Board", "board_key": "select_board", "platform": "agenda_page",
                                "url": "https://townofmaineny.gov/",
                                "board_exclude": r"planning|zoning\s+board|\bZBA\b|fire\s+district"}],
              "curation_note": "Town Board public-hearing notices on the homepage"},
    # Agendas are in Compass Web Development "CMM" embeds (iframes on the Weebly sites).
    "Clymer": {"add_listings": [{"board": "Town Board", "board_key": "select_board", "platform": "cmm_compass",
                                 "url": "https://cmm.compassweb.dev/embeds/80/agendas", "board_rules": _CMM_RULES}],
               "curation_note": "agendas in the CMM embed (iframe on minutes--agendas.html)"},
    "Ellery": {"add_listings": [{"board": "Town Board", "board_key": "select_board", "platform": "cmm_compass",
                                 "url": "https://cmm.compassweb.dev/embeds/7/agendas", "board_rules": _CMM_RULES}],
               "curation_note": "agendas in the CMM embed (iframe on minutes--agendas.html)"},
    "Angelica": {"add_listings": [{"board": "Town Board", "board_key": "select_board", "platform": "cmm_compass",
                                   "url": "https://cmm.compassweb.dev/embeds/20/agendas", "board_rules": _CMM_RULES}],
                 "curation_note": "agendas and hearing notices in the CMM embed (iframe on minutes--agendas.html)"},
    # Legal notices page: Town Board meetings / hearings, Planning Board subdivision hearings, ZBA hearings.
    "West Bloomfield": {"add_listings": [{
        "board": "Town Board", "board_key": "select_board", "platform": "generic_ny",
        "url": "https://westbloomfieldny.gov/legal-notices",
        "link_pattern": r"\d{1,2}\.\d{1,2}\.20\d\d|^PH |^Meeting",
        "date_regex": r"(?P<m>\d{1,2})\.(?P<d>\d{1,2})\.(?P<y>20\d\d)",
        "board_rules": [[r"ZBA|Zoning Board", "Zoning Board of Appeals", "zoning_board_of_appeals"],
                        [r"Subdivision|Site Plan|Planning", "Planning Board", "planning_board"],
                        [r"Meeting|PH |Public Hearing|Local Law|Moratorium", "Town Board", "select_board"]]}],
        "curation_note": "Town Board / Planning Board / ZBA hearing and meeting notices on the legal-notices page "
                         "(minutes only on the board pages)"},
    # yonkersny.gov answers a Cloudflare challenge (not bypassed), but the City Council's meetings are on
    # Legistar, whose public Web API and meeting pages are open (robots.txt: none / allowed).
    "Yonkers": {"add_listings": [
        {"board": "City Council of Yonkers Stated Meeting", "board_key": "select_board", "platform": "legistar",
         "client": "yonkersny", "url": "https://yonkersny.legistar.com/Calendar.aspx"},
        {"board": "Public Hearing Notice", "board_key": "select_board", "platform": "legistar",
         "client": "yonkersny", "url": "https://yonkersny.legistar.com/Calendar.aspx"}],
        "client": "yonkersny",
        "curation_note": "City Council via Legistar (Web API + MeetingDetail pages); the city website itself is behind "
                         "a Cloudflare challenge; the Planning Board is not on Legistar"},
    # Common Council agendas in month folders of the file library ("september_2026").
    "North Tonawanda": {"add_listings": [{
        "board": "Common Council", "board_key": "select_board", "platform": "generic_ny",
        "url": "https://www.northtonawanda.gov/file-library/category/{month}_{y}", "months": True,
        "skip_missing_months": True, "link_pattern": "agenda", "compact_dates": True,
        "date_regex": r"/(?P<y>20\d\d)/(?P<m>\d{1,2})\.(?P<d>\d{2})\s*cc"}],
        "curation_note": "Common Council agendas in monthly file-library folders; no 2026 Planning or ZBA agendas posted"},
    # Monthly Town Board agendas posted as public notices ("Agenda for September 2026"), each a .docx attachment.
    "Lewis": {"add_listings": [{
        "board": "Town Board", "board_key": "select_board", "platform": "generic_ny",
        "url": "https://townoflewislcny.gov/resources/public-notices/", "link_pattern": "agenda-for",
        "follow_pages": True, "follow_doc": r"\.(?:docx?|pdf)(?:\?|$)", "month_only": True}],
        "curation_note": "Town Board monthly agendas as public notices with a .docx attachment (board pages and "
                         "meeting archives load by script)"},
    # Hearing notices posted as WordPress posts on the homepage ("Zoning Board Public Hearing").
    "Carlton": {"add_listings": [{
        "board": "Town Board", "board_key": "select_board", "platform": "generic_ny",
        "url": "https://townofcarltonny.gov/", "link_pattern": "hearing|notice-of-public|public-meeting|agenda",
        "exclude_pattern": "minutes|cancel", "follow_pages": True,
        "date_regex": r"(?:hold|held|have|having)\s+(?:a\s+|its\s+|their\s+)?(?:public\s+hearing|(?:public|regular|"
                      r"special)\s+meeting|meeting)\b.{0,160}?\bon\s+(?:[A-Za-z]+day,?\s+)?(?P<m>[A-Za-z]+)\.?\s+"
                      r"(?P<d>\d{1,2})\D{0,3}?,?\s*(?P<y>20\d\d)",
        "board_rules": [["zoning", "Zoning Board of Appeals", "zoning_board_of_appeals"],
                        ["planning", "Planning Board", "planning_board"], [".", "Town Board", "select_board"]]}],
        "curation_note": "public hearing and meeting notices posted on the homepage (no agenda listing)"},
    # Found after the NY precision sample (in-sample fixes): discovery had taken one document page as the Town
    # Board listing, so the sidebar's 2019 zoning-law PDF was read as a June 2026 meeting document.
    "Denmark": {"replace_listings": True, "add_listings": [{
        "board": "Town Board", "board_key": "select_board", "platform": "generic_ny",
        "url": "https://townofdenmarkny.gov/document-category/board_agendas/",
        "link_pattern": r"/documents/[a-z0-9-]+/?$", "exclude_pattern": "minutes|cancel",
        "follow_pages": True, "follow_doc": r"\.pdf(?:\?|$)",
        "date_regex": r"(?P<m>\d{1,2})[./](?P<d>\d{1,2})[./](?P<y>20\d\d)"}],
        "curation_note": "Town Board agenda packets as document pages in the 'Board Agendas' category, each with "
                         "its PDF"},
    # Discovery read the year page through the Planning Board page and labelled a Town Board agenda "Planning
    # Board"; the Town Board's monthly agendas are on the {year} page, named only by month ("September Agenda").
    "Westfield": {"replace_listings": True, "add_listings": [{
        "board": "Town Board", "board_key": "select_board", "platform": "generic_ny",
        "url": "https://westfieldny.com/town-westfield/{year}-town-agendas-and-minutes", "link_pattern": "agenda",
        "exclude_pattern": "minutes|cancel", "doc_href": r"\.pdf", "month_only": True, "assume_year": "url",
        "skip_missing_months": True}],
        "curation_note": "Town Board monthly agendas on the year page (month names only; meeting date left empty)"},
    # Checked by hand, not readable (recorded so the report says why):
    "Yorktown": {"reason_code": "documents_blocked",
                 "reason": "agendas are on calendar.yorktownny.gov, which answers HTTP 403 'blocked due to security "
                           "reasons' to AgendaAheadBot (robots.txt too); not bypassed",
                 "curation_note": "checked by hand 2026-10-12"},
    "Montgomery": {"curation_note": "checked by hand 2026-10-12: 'Agendas, Minutes, & Videos' is a DNN document "
                                    "library filled by script, with no static listing to read"},
    "Sherman": {"curation_note": "checked by hand 2026-10-12: shermanny.gov carries Town Board minutes only; the "
                                 "agendas there (planning board, ZBA) are the Village of Sherman's"},
    "Oswegatchie": {"curation_note": "checked by hand 2026-10-12: monthly Town Board agendas (2026_<month>_agenda.pdf) "
                                     "are posted, but the latest is August 2026, before the window"},
    "Prattsburgh": {"curation_note": "checked by hand 2026-10-12: Town Board page lists monthly minutes only"},
}
NY_ABOUT = ("Agenda Ahead Wave 1 test (2026-10): {n} more New York towns, cities and villages with battery-storage "
            "moratoria, local laws or active data-center fights (Carina BESS Moratorium Monitor, the NY pilot's "
            "next-50 list, research notes). Same row shape as towns_ny.json plus kind, selection_group / "
            "selection_reason / selection_source. Built by `python3 experiments/wave1_test.py discover`. Kept outside "
            "data/towns_*.json because New York is a published state; promotion = moving these rows into "
            "data/towns_ny.json.")


def cmd_discover(args) -> None:
    from watch351.discover_sites import discover_place
    targets = load(W1 / "targets_ny.json")
    path = CONFIG / "towns_ny.json"
    prev = {t["town"]: t for t in (load(path, {}) or {}).get("towns", [])}
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    todo = [t for t in targets if wanted is None or t["town"].lower() in wanted]
    fetcher = PoliteFetcher()
    t0 = time.monotonic()

    def one(t):
        best = None
        for site in t.get("website_candidates") or [None]:
            row = {k: v for k, v in t.items() if k != "website_candidates"}
            row["website"] = site
            try:
                r = discover_place(fetcher, row, "NY", list(ALL3))
            except Exception as e:  # noqa: BLE001 - one site must not stop the run
                logging.exception("discovery crashed for %s", t["town"])
                r = {**row, "status": "not_automated", "reason_code": "discovery_error", "automated": False,
                     "reason": f"{type(e).__name__}: {str(e)[:160]}", "listings": []}
            if best is None or r.get("automated") or best.get("reason_code") in ("unreachable", "website_mismatch",
                                                                                  "http_error"):
                best = r
            if r.get("automated"):
                break
        best["website_candidates"] = t.get("website_candidates") or []
        return best

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one, todo))
    for r in results:
        r.pop("_posted_rows", None)
        cur = CURATED_NY.get(r["town"])
        if cur:
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
                r["boards_missing"] = [k for k in ALL3 if k not in r["boards_found"]]
            r["curated"] = True
        prev[r["town"]] = r
    rows = [prev[t["town"]] for t in targets if t["town"] in prev]
    doc = {
        "_about": NY_ABOUT.format(n=len(rows)),
        "generated": now_iso(), "state": "NY", "gated": True,
        "gate_note": "Wave 1 test towns: not part of the production daily run or site (this file is outside the "
                     "data/towns_*.json glob). Crawled only by `python3 -m watch351.daily --data-dir "
                     "../data/test/wave1/config --states NY --output-dir ../data/test/wave1/ny --hits-name "
                     "hits_ny_wave1.json` (experiments/wave1_test.py crawl).",
        "boards_tracked": ALL3,
        "board_key_mapping": {"Town Board, Village Board of Trustees, City / Common Council": "select_board",
                              "Planning Board": "planning_board", "Zoning Board of Appeals": "zoning_board_of_appeals"},
        "evidence_rule": "a board is automated only if its listing shows >=1 agenda/packet/notice dated within "
                         "[today-120d, today+120d] and the first such document is fetchable under robots.txt",
        "count": len(rows), "automated": sum(1 for r in rows if r.get("automated")), "towns": rows,
    }
    save(path, doc)
    print(f"NY wave 1: {len(results)} discovered in {time.monotonic() - t0:.0f}s; fetcher {fetcher.stats}")
    for r in results:
        print(f"  {r['town']:<17} {str(r.get('platform') or '-'):<14} {len(r.get('listings') or []):>2} "
              f"{'AUTO ' + ','.join(sorted(r.get('boards_found') or [])) if r.get('automated') else r.get('reason_code')}: "
              f"{'' if r.get('automated') else (r.get('reason') or '')[:120]}")


def cmd_crawl(args) -> None:
    out = W1 / args.subdir if args.subdir else NY_OUT     # e.g. --subdir ny_extended --days-back 200
    cmd = [sys.executable, "-m", "watch351.daily", "--data-dir", str(CONFIG), "--states", "NY", "--output-dir",
           str(out), "--hits-name", NY_HITS, "--days-back", str(args.days_back), "--days-ahead", str(args.days_ahead),
           "--workers", str(args.workers), "--request-log", str(out / f"requests_{args.label}.tsv")]
    if args.cache_dir:
        cmd += ["--cache-dir", args.cache_dir]
    out.mkdir(parents=True, exist_ok=True)
    print(" ".join(cmd))
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=CRAWLER)
    print(f"exit {proc.returncode}, wall {time.monotonic() - t0:.0f}s")
    runs = out / "state" / "runs"
    latest = max(runs.glob("*.json"), key=lambda p: p.stat().st_mtime)
    save(out / "runs" / f"run_{args.label}.json", load(latest))
    print(f"saved {out / 'runs' / f'run_{args.label}.json'}")

# ------------------------------------------------------------------------------------ feeds
def cmd_feeds(args) -> None:
    for mod in ("watch351.sources.vt_act250", "watch351.sources.ct_siting"):
        if args.only and args.only not in mod:
            continue
        cmd = [sys.executable, "-m", mod, "--out-dir", str(SOURCES)] + (["--offline"] if args.offline else [])
        print(" ".join(cmd))
        t0 = time.monotonic()
        proc = subprocess.run(cmd, cwd=CRAWLER)
        print(f"exit {proc.returncode}, {time.monotonic() - t0:.0f}s")


# ------------------------------------------------------------------------------------ combine
def wave1_towns() -> list[dict]:
    rows = []
    for st in ("vt", "ct"):
        doc = load(DATA / f"towns_{st}.json", {}) or {}
        rows += [{**t, "state": st.upper()} for t in doc.get("towns", [])]
    rows += [{**t, "state": "NY"} for t in (load(CONFIG / "towns_ny.json", {}) or {}).get("towns", [])]
    return rows


def cmd_combine(args) -> None:
    """data/test/wave1/hits_wave1.json: VT + CT source hits and the NY wave-1 agenda hits, built and validated by
    watch351.current exactly as production builds data/hits_current.json (nothing archived)."""
    from watch351.state import DocIndex
    idx = DocIndex(NY_OUT / "state" / "docs")
    doc = current.build(W1, archive=False, agenda_hits=idx.current_hits(), indexed_urls=idx.urls(),
                        towns=wave1_towns())
    errs = current.validate(doc)
    save(W1 / "hits_wave1.json", doc)
    by = Counter((h["state"], h["source"]) for h in doc["hits"])
    rep = {"generated": now_iso(), "hits": len(doc["hits"]), "by_state_source": {f"{a}/{b}": n for (a, b), n in by.items()},
           "states": doc["states"], "towns_monitored": doc["towns_monitored"], "window": doc["window"],
           "validation_errors": errs[:50], "valid": not errs,
           "topics": dict(Counter(t for h in doc["hits"] for t in h["topics"]).most_common())}
    save(W1 / "validation.json", rep)
    print(json.dumps(rep, indent=1)[:2000])


# ------------------------------------------------------------------------------------ samples
def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(100 * (c - h), 1), round(100 * (c + h), 1))


def _doc_text(url: str) -> str:
    from watch351 import extract as X
    from watch351.fetch import DEFAULT_CACHE_DIR, FetchError
    from watch351.keywords import clean_text
    X.OCR_CACHE = DEFAULT_CACHE_DIR / "ocr"
    f = PoliteFetcher(DEFAULT_CACHE_DIR, offline=True)
    try:
        resp = f.get(url)
    except FetchError:
        return ""
    return clean_text(X.extract(resp).text)


# Vermont: today's agenda holds 40 projects, all read while the flag rules were written. The fresh check draws
# Act 250 projects the module never saw: base numbers just below the newest original application of each
# district series in today's feed, read from their detail pages through the same item builder.
VT_SERIES = {"1R": 1038, "4C": 1364, "5W": 1045, "7E": 1186, "9A": 374, "2W": 358}
VT_SPAN = 80


def vt_pool(n: int, seed: int) -> list[dict]:
    from watch351.sources import vt_act250 as V
    from watch351.sources.state_feeds import load_state_towns
    towns = V.town_index(load_state_towns("VT"))
    seen = {i["project_number"] for i in (load(SOURCES / "vt_act250_items.json", {}) or {}).get("items", [])}
    cands = [f"{p}{k:04d}" for p, top in VT_SERIES.items() for k in range(max(1, top - VT_SPAN), top)]
    cands = [c for c in cands if c not in seen]
    random.Random(seed).shuffle(cands)
    f = PoliteFetcher()
    out, tried = [], 0
    for num in cands:
        if len(out) >= n:
            break
        tried += 1
        try:
            it = V.item_from_detail(f, num, towns, now_iso())
        except Exception as e:  # noqa: BLE001
            print(num, "error", e)
            continue
        if it:
            out.append(it)
    print(f"VT fresh pool: {len(out)} projects from {tried} numbers tried; fetcher {f.stats}")
    return out


def cmd_sample(args) -> None:
    rng = random.Random(args.seed)
    if args.source == "ny":
        # every hit the crawl's document index holds (hits_current drops those older than 120 days), in the
        # contract's shape; none of the NY wave-1 hits had been read before this sample
        from watch351.state import DocIndex
        idx = DocIndex((W1 / args.subdir if args.subdir else NY_OUT) / "state" / "docs")
        counties = current.county_lookup(wave1_towns())
        hits = list({n["id"]: n for n in (current.normalize(h, counties) for h in idx.current_hits())}.values())
        pool = sorted((h for h in hits if h["state"] == "NY"), key=lambda h: h["id"])
        pick = sorted(rng.sample(pool, min(args.n, len(pool))), key=lambda h: (h["town"], h["id"]))
        rows = []
        for h in pick:
            text = _doc_text(h["source_url"])
            pos = text.find(h["snippet"][:100].rstrip("…"))
            rows.append({**{k: h[k] for k in ("id", "town", "board", "meeting_date", "topics", "snippet", "source_url",
                                             "text_source")},
                         "context": text[max(0, pos - 700): pos + 900] if pos >= 0 else ""})
        dest = W1 / "worksheet_ny.json"
        save(dest, {"pool": len(pool), "seed": args.seed, "n": len(rows), "items": rows})
    elif args.source == "ct":
        # fresh pool: decided petitions and dockets from 2022 on, outside the 2026 window the module was built on
        cur = {(i["number"], i["town"]) for i in (load(SOURCES / "ct_siting_items.json", {}) or {}).get("items", [])}
        for ex in (args.exclude or "").split(","):       # items judged in an earlier round
            if ex:
                cur |= {(i["number"], i["town"]) for i in load(W1 / ex)["items"]}
        back = W1 / ("sources_backfill" + (f"_r{args.round}" if args.round > 1 else ""))
        if not (back / "ct_siting_items.json").exists():
            subprocess.run([sys.executable, "-m", "watch351.sources.ct_siting", "--out-dir", str(back),
                            "--backfill-from", "2022-01-01", "--docket-from", "500"], cwd=CRAWLER, check=True)
        items = (load(back / "ct_siting_items.json", {}) or {}).get("items", [])
        pool = sorted((i for i in items if (i["number"], i["town"]) not in cur), key=lambda i: (i["number"], i["town"] or ""))
        pick = sorted(rng.sample(pool, min(args.n, len(pool))), key=lambda i: (i["kind"], i["number"]))
        dest = W1 / ("worksheet_ct.json" if args.round == 1 else f"worksheet_ct_r{args.round}.json")
        save(dest, {"pool": len(pool), "seed": args.seed, "n": len(pick), "items": pick})
    else:
        items = vt_pool(args.n, args.seed)
        dest = W1 / "worksheet_vt.json"
        save(dest, {"pool": "detail pages of Act 250 projects " + ", ".join(f"{p}{max(1, t - VT_SPAN):04d}-{p}{t - 1:04d}"
                                                                          for p, t in VT_SERIES.items()),
                    "seed": args.seed, "n": len(items), "items": items})
    print("wrote", dest)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["towns", "targets", "feeds", "discover", "crawl", "combine", "sample", "analyze"])
    p.add_argument("--only")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--places")
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--label", default="run1")
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=120)
    p.add_argument("--source", choices=["vt", "ct", "ny"])
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--seed", type=int, default=2028)
    p.add_argument("--round", type=int, default=1, help="sample: round number (a later round re-runs the source "
                                                         "into its own directory and excludes --exclude worksheets)")
    p.add_argument("--exclude", help="sample: comma-separated worksheets (under data/test/wave1) already judged")
    p.add_argument("--cache-dir")
    p.add_argument("--subdir", help="crawl / sample --source ny: output directory under data/test/wave1 "
                                    "(default ny; ny_extended for the wider window of the precision pool)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    globals()[f"cmd_{args.command}"](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
