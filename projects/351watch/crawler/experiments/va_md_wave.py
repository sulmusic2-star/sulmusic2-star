#!/usr/bin/env python3
"""Agenda Ahead second expansion (2026-11): Virginia statewide (95 counties, the independent cities
and the towns with data-center, solar or battery fights) plus Maryland (23 counties, Baltimore City and
the Montgomery / Prince George's / Frederick municipalities). Everything is gated: nothing here writes
data/hits_current.json, data/state/ or data/sources/.

    cd projects/351watch/crawler
    python3 experiments/va_md_wave.py targets                   # data/test/va_md/targets_{va,md}.json
    python3 experiments/va_md_wave.py discover --state VA       # -> data/towns_va.json (gated)
    python3 experiments/va_md_wave.py discover --state MD       # -> data/towns_md.json (gated)
    python3 experiments/va_md_wave.py discover --state VA --places "Loudoun County,City of Manassas"
    python3 experiments/va_md_wave.py crawl --label run1        # watch351.daily --states VA,MD -> data/test/va_md/
    python3 experiments/va_md_wave.py analyze                   # coverage, output, freshness -> analysis_va_md.json
    python3 experiments/va_md_wave.py sample --n 60 --seed 2026 # precision worksheet (hit + source context)

Targets: the 95 Virginia counties and 23 Maryland counties come from the October county census
(research_notes/Meeting monitor national expansion/coverage_county_census.csv, Wikidata-sourced
websites), with the websites corrected by hand where the census URL was stale; the 37 places already in
data/towns_va.json keep their rows' websites and selection notes; cities, towns and Maryland
municipalities are hand lists (website_source "hand list, 2026-11; verified by discovery": discovery
rejects a site that does not name the place).

All network access goes through watch351.fetch.PoliteFetcher (AgendaAheadBot UA, robots.txt on every
hop, <= 1 request/second/host, crawl-delay honoured up to the cap, no logins, no POSTs, no challenge
solving).
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAWLER = HERE.parent
sys.path.insert(0, str(CRAWLER))
sys.path.insert(0, str(HERE))

from watch351.discover_sites import discover_place  # noqa: E402
from watch351.fetch import PoliteFetcher  # noqa: E402

DATA = CRAWLER.parent / "data"
TEST = DATA / "test" / "va_md"
HITS_NAME = "hits_va_md.json"
CENSUS_CSV = CRAWLER.parent.parent.parent / "research_notes" / "Meeting monitor national expansion" / "coverage_county_census.csv"
STATES = ("VA", "MD")
ALL3 = ["select_board", "planning_board", "zoning_board_of_appeals"]
FIGHTS = "research_notes/Meeting monitor national expansion/data_center_and_other_fights.md"
HOTSPOTS = "research_notes/Meeting monitor national expansion/energy_siting_hotspots.md"
PAYS = "research_notes/Expansion/where_it_pays_2026.md"
HAND = "hand list, 2026-11; verified by discovery (the site must name the place)"


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


# ------------------------------------------------------------------------------------ Virginia
# Census URLs that were stale or blank in October, replaced with the county's current site.
VA_COUNTY_SITES = {
    "Alleghany": "https://www.co.alleghany.va.us/", "Amherst": "https://www.countyofamherst.com/",
    "Bath": "https://www.bathcountyva.org/", "Buchanan": "https://www.buchanancountyonline.com/",
    "Clarke": "https://www.clarkecounty.gov/", "Fluvanna": "https://www.fluvannacounty.org/",
    "Giles": "https://www.gilescounty.org/", "Gloucester": "https://www.gloucesterva.gov/",
    "Greene": "https://www.greenecountyva.gov/", "Middlesex": "https://www.co.middlesex.va.us/",
    "New Kent": "https://www.co.new-kent.va.us/", "Page": "https://www.pagecounty.virginia.gov/",
    "Prince George": "https://www.princegeorgecountyva.gov/", "Prince William": "https://www.pwcva.gov/",
    "Fauquier": "https://www.fauquiercounty.gov/", "Culpeper": "https://web.culpepercounty.gov/",
    "Stafford": "https://staffordcountyva.gov/", "Frederick": "https://www.fcva.us/",
    "Albemarle": "https://www.albemarle.org/", "Augusta": "https://www.co.augusta.va.us/",
    "Bedford": "https://www.bedfordcountyva.gov/", "Lee": "https://www.leecova.org/",
    "Nelson": "https://www.nelsoncounty-va.gov/", "Smyth": "https://www.smythcounty.org/",
    "Rappahannock": "https://www.rappahannockcountyva.gov/", "Floyd": "https://www.floydcova.org/",
    "Highland": "https://www.highlandcova.org/", "James City": "https://www.jamescitycountyva.gov/",
    "Charlotte": "https://www.charlottecountyva.gov/", "Essex": "https://www.essexva.gov/",
    "Montgomery": "https://www.montva.com/", "Richmond": "https://co.richmond.va.us/",
    "Tazewell": "https://www.tazewellcounty.org/", "Russell": "https://www.russellcountyva.org/",
}
# Selection groups and the reported fights (data_center_and_other_fights.md, energy_siting_hotspots.md,
# where_it_pays_2026.md section 2). Counties not listed are "statewide" with no specific fight in our notes.
VA_COUNTY_NOTES = {
    "Loudoun": ("nova", "data-center capital: by-right data centers ended Mar 18, 2025; 23 grandfathered projects and a "
                        "12-month pause drafted Sep 15, 2026; opposes the Valley North 765 kV line", FIGHTS),
    "Prince William": ("nova", "Digital Gateway rezonings voided Aug 2025, affirmed Mar 31, 2026, QTS exit Jul 2, 2026 ($24.7B); "
                               "12 of 12 interconnection requests include storage", FIGHTS),
    "Fairfax": ("nova", "data-center zoning amendment (2024); $165M project delayed; agendas on iCompass/CivicWeb", FIGHTS),
    "Arlington": ("nova", "Northern Virginia data-center market; county board on Legistar", PAYS),
    "Stafford": ("nova", "I-95 data-center rezonings; Piedmont / North hotspot (area 9)", HOTSPOTS),
    "Frederick": ("shenandoah_valley", "Winchester-corridor data centers; Valley North 765 kV line", FIGHTS),
    "Clarke": ("shenandoah_valley", "Valley North 765 kV line; solar ordinance", FIGHTS),
    "Warren": ("shenandoah_valley", "Front Royal (Avtex site) data-center fight; Piedmont / North hotspot", HOTSPOTS),
    "Shenandoah": ("shenandoah_valley", "data-center ordinance (2025) and solar ordinance; hotspot area 9", HOTSPOTS),
    "Page": ("shenandoah_valley", "solar ordinance; hotspot area 9", HOTSPOTS),
    "Rockingham": ("shenandoah_valley", "solar and data-center rezonings; hotspot area 9", HOTSPOTS),
    "Augusta": ("shenandoah_valley", "solar ordinance; Weyers Cave data-center rezonings; hotspot area 9", HOTSPOTS),
    "Rappahannock": ("nova", "solar cap; Piedmont", HOTSPOTS),
    "Henrico": ("richmond_metro", "DC Blox $500M project withdrawn (2025); data-center overlay", FIGHTS),
    "Chesterfield": ("richmond_metro", "Old Bermuda data-center denial upheld Jun 3, 2026", FIGHTS),
    "New Kent": ("richmond_metro", "solar and data-center rezonings along I-64", HOTSPOTS),
    "Charles City": ("richmond_metro", "solar; Southside hotspot (area 2)", HOTSPOTS),
    "Prince George": ("richmond_metro", "solar; Southside hotspot (area 2)", HOTSPOTS),
    "Albemarle": ("central", "data-center and solar rezonings; Akamai-walled site", PAYS),
    "Botetourt": ("roanoke_valley", "Rocky Forge wind project; data-center rezoning", HOTSPOTS),
    "Roanoke": ("roanoke_valley", "Roanoke Valley; agendas on iQM2", PAYS),
    "Franklin": ("southwest", "solar ordinance", HOTSPOTS),
    "Bedford": ("southwest", "solar ordinance; Akamai-walled site", HOTSPOTS),
    "Pulaski": ("southwest", "New River Valley data-center and solar items; agendas on BoardDocs", PAYS),
    "Montgomery": ("southwest", "New River Valley (Blacksburg, Christiansburg)", PAYS),
    "Accomack": ("eastern_shore", "solar; offshore-wind staging; agendas on BoardDocs", PAYS),
    "Northampton": ("eastern_shore", "solar ordinance", HOTSPOTS),
    "Washington": ("southwest", "solar; agendas on iQM2", PAYS),
    "Wythe": ("southwest", "solar and industrial rezonings (Progress Park)", PAYS),
    "James City": ("hampton_roads", "solar; Cloudflare-walled site", PAYS),
    "York": ("hampton_roads", "Hampton Roads; CivicClerk", PAYS),
    "Gloucester": ("hampton_roads", "solar", HOTSPOTS),
    "Essex": ("northern_neck", "solar; Piedmont / North hotspot (area 9)", HOTSPOTS),
    "Westmoreland": ("northern_neck", "solar; hotspot area 9", HOTSPOTS),
    "King William": ("northern_neck", "solar; hotspot area 9", HOTSPOTS),
    "King and Queen": ("northern_neck", "solar; hotspot area 9", HOTSPOTS),
}
VA_REGION = {  # the rest, by region
    "southwest": ["Bland", "Buchanan", "Carroll", "Craig", "Dickenson", "Floyd", "Giles", "Grayson", "Lee", "Patrick",
                  "Russell", "Scott", "Smyth", "Tazewell", "Wise", "Amherst", "Nelson"],
    "shenandoah_valley": ["Alleghany", "Bath", "Highland", "Rockbridge"],
    "central": ["Greene"],
    "northern_neck": ["Lancaster", "Northumberland", "Richmond", "Mathews", "Middlesex"],
}

# (name, county, website, selection reason). Independent cities have no county.
VA_CITIES = [
    ("Alexandria", "https://www.alexandriava.gov/", "NoVa; council and planning commission on Legistar"),
    ("Bristol", "https://www.bristolva.org/", "statewide city list"),
    ("Buena Vista", "https://www.buenavistava.org/", "statewide city list"),
    ("Charlottesville", "https://www.charlottesville.gov/", "central Virginia; solar and zoning rewrite"),
    ("Chesapeake", "https://www.cityofchesapeake.net/", "data centers and solar; agendas on Granicus"),
    ("Colonial Heights", "https://www.colonialheightsva.gov/", "Richmond metro"),
    ("Covington", "https://www.covington.va.us/", "statewide city list"),
    ("Danville", "https://www.danvilleva.gov/", "Southside; data-center and industrial rezonings"),
    ("Emporia", "https://www.ci.emporia.va.us/", "Southside"),
    ("Fairfax", "https://www.fairfaxva.gov/", "NoVa"),
    ("Falls Church", "https://www.fallschurchva.gov/", "NoVa"),
    ("Franklin", "https://www.franklinva.com/", "Southside"),
    ("Fredericksburg", "https://www.fredericksburgva.gov/", "I-95 data-center corridor"),
    ("Galax", "https://www.galaxva.com/", "statewide city list"),
    ("Hampton", "https://hampton.gov/", "Hampton Roads"),
    ("Harrisonburg", "https://www.harrisonburgva.gov/", "Shenandoah Valley"),
    ("Hopewell", "https://www.hopewellva.gov/", "Richmond metro; industrial"),
    ("Lexington", "https://www.lexingtonva.gov/", "statewide city list"),
    ("Lynchburg", "https://www.lynchburgva.gov/", "central; data-center rezonings"),
    ("Manassas", "https://www.manassasva.gov/", "data centers (Digital Gateway neighbour); agendas on Granicus"),
    ("Manassas Park", "https://www.cityofmanassaspark.us/", "NoVa data-center corridor"),
    ("Martinsville", "https://www.martinsville-va.gov/", "Southside"),
    ("Newport News", "https://www.nnva.gov/", "Hampton Roads"),
    ("Norfolk", "https://www.norfolk.gov/", "Hampton Roads; Legistar"),
    ("Norton", "https://www.nortonva.gov/", "statewide city list"),
    ("Petersburg", "https://www.petersburgva.gov/", "Richmond metro; industrial"),
    ("Poquoson", "https://www.ci.poquoson.va.us/", "statewide city list"),
    ("Portsmouth", "https://www.portsmouthva.gov/", "Hampton Roads"),
    ("Radford", "https://www.radfordva.gov/", "New River Valley"),
    ("Richmond", "https://www.rva.gov/", "state capital; Legistar"),
    ("Roanoke", "https://www.roanokeva.gov/", "Roanoke Valley"),
    ("Salem", "https://www.salemva.gov/", "Roanoke Valley"),
    ("Staunton", "https://www.ci.staunton.va.us/", "Shenandoah Valley"),
    ("Suffolk", "https://www.suffolkva.us/", "Hampton Roads; solar and data-center rezonings"),
    ("Virginia Beach", "https://virginiabeach.gov/", "Hampton Roads; data centers and offshore-wind landing"),
    ("Waynesboro", "https://www.waynesboro.va.us/", "Shenandoah Valley"),
    ("Williamsburg", "https://www.williamsburgva.gov/", "Hampton Roads"),
    ("Winchester", "https://www.winchesterva.gov/", "Winchester-corridor data centers"),
]
# Legistar clients found with the public web API (data/test/va_md/legistar_probe.json, 2026-11-02): the city sites
# link only their Granicus video pages, or sit behind a bot wall, so discovery is told the client name.
VA_LEGISTAR = {"Alexandria": "alexandria", "Hampton": "hampton", "Richmond": "richmondva"}
VA_TOWNS = [  # (name, county, website, reason)
    ("Leesburg", "Loudoun", "https://www.leesburgva.gov/", "data centers (Loudoun); Akamai-walled in October"),
    ("Purcellville", "Loudoun", "https://www.purcellvilleva.gov/", "western Loudoun data-center fights"),
    ("Lovettsville", "Loudoun", "https://www.lovettsvilleva.gov/", "western Loudoun; Valley North line"),
    ("Round Hill", "Loudoun", "https://www.roundhillva.org/", "western Loudoun"),
    ("Hamilton", "Loudoun", "https://www.town.hamilton.va.us/", "western Loudoun"),
    ("Middleburg", "Loudoun", "https://www.middleburgva.gov/", "western Loudoun; Piedmont Environmental Council area"),
    ("Haymarket", "Prince William", "https://www.townofhaymarket.org/", "Digital Gateway neighbour"),
    ("Dumfries", "Prince William", "https://www.dumfriesva.gov/", "I-95 data-center corridor"),
    ("Herndon", "Fairfax", "https://www.herndon-va.gov/", "Dulles data-center corridor"),
    ("Vienna", "Fairfax", "https://www.viennava.gov/", "NoVa"),
    ("Front Royal", "Warren", "https://www.frontroyalva.com/", "Avtex-site data-center fight"),
    ("Strasburg", "Shenandoah", "https://www.strasburgva.com/", "data-center rezoning (2025)"),
    ("Woodstock", "Shenandoah", "https://www.townofwoodstockva.gov/", "Shenandoah County seat"),
    ("Berryville", "Clarke", "https://www.berryvilleva.gov/", "Clarke County seat; Valley North line"),
    ("Luray", "Page", "https://www.townofluray.com/", "Page County seat"),
    ("Stephens City", "Frederick", "https://www.stephenscity.us/", "Frederick County data-center corridor"),
    ("Orange", "Orange", "https://www.townoforangeva.org/", "solar (Grassland Solar SUP in the county)"),
    ("Louisa", "Louisa", "https://www.louisatown.org/", "Amazon data centers at Lake Anna (county)"),
    ("Ashland", "Hanover", "https://www.ashlandva.gov/", "Hanover data-center rezonings"),
    ("Bowling Green", "Caroline", "https://www.townofbowlinggreen.com/", "Caroline data-center and quarry rezonings"),
    ("Remington", "Fauquier", "https://www.remington-va.gov/", "Remington Technology Park gas fuel cells (Jul 10, 2026)"),
    ("Culpeper", "Culpeper", "https://www.culpeperva.gov/", "data centers ($12B Culpeper Acquisitions); BoardDocs"),
    ("Warrenton", "Fauquier", "https://www.warrentonva.gov/", "Amazon data-center fight; Municode Meetings"),
    ("Farmville", "Prince Edward", "https://www.farmvilleva.com/", "Southside town"),
    ("South Hill", "Mecklenburg", "https://www.southhillva.org/", "Microsoft Boydton neighbour"),
    ("South Boston", "Halifax", "https://www.southboston.com/", "Halifax's largest town (solar, industrial rezonings)"),
    ("Chase City", "Mecklenburg", "https://www.chasecity.org/", "Mecklenburg solar cap"),
    ("Clarksville", "Mecklenburg", "https://www.clarksvilleva.com/", "Microsoft Boydton neighbour"),
    ("Blackstone", "Nottoway", "https://www.blackstoneva.com/", "Southside; Fort Barfoot"),
    ("Blacksburg", "Montgomery", "https://www.blacksburg.gov/", "New River Valley"),
    ("Christiansburg", "Montgomery", "https://www.christiansburg.org/", "New River Valley data-center items"),
    ("Smithfield", "Isle of Wight", "https://www.smithfieldva.gov/", "Isle of Wight solar"),
    ("Windsor", "Isle of Wight", "https://www.windsor-va.gov/", "Isle of Wight solar"),
    ("Bedford", "Bedford", "https://www.bedfordva.gov/", "Bedford County solar"),
    ("Rocky Mount", "Franklin", "https://www.rockymountva.org/", "Franklin County solar"),
    ("Wytheville", "Wythe", "https://www.wytheville.org/", "Progress Park industrial"),
    ("Abingdon", "Washington", "https://www.abingdon-va.gov/", "southwest"),
    ("Altavista", "Campbell", "https://www.altavistava.gov/", "Campbell County solar"),
    ("Chatham", "Pittsylvania", "https://www.chatham-va.gov/", "Pittsylvania County seat"),
    ("Gordonsville", "Orange", "https://www.gordonsville.org/", "Orange County solar"),
    ("Vinton", "Roanoke", "https://www.vintonva.gov/", "Roanoke Valley"),
]

# ------------------------------------------------------------------------------------ Maryland
# (name, website, group, reason, extras)
MD_COUNTIES = [
    ("Allegany", "https://www.alleganygov.org/", "western", "statewide county list; CivicClerk", {}),
    ("Anne Arundel", "https://www.aacounty.org/", "baltimore_metro", "data-center zoning (2026); county council", {}),
    ("Baltimore", "https://www.baltimorecountymd.gov/", "baltimore_metro", "data-center moratorium Jun 16, 2026; MPRP 500 kV line", {}),
    ("Calvert", "https://www.calvertcountymd.gov/", "southern", "AWS withdrawal; data-center pause (2026); agendas on Granicus", {}),
    ("Caroline", "https://www.carolinemd.org/", "eastern_shore", "solar ordinance; CivicPlus", {}),
    ("Carroll", "https://www.carrollcountymd.gov/", "baltimore_metro", "MPRP 500 kV line; solar ordinance; robots.txt disallowed us in October", {}),
    ("Cecil", "https://www.cecilcountymd.gov/", "baltimore_metro", "Perryville data centers; solar; CivicClerk", {}),
    ("Charles", "https://www.charlescountymd.gov/", "southern", "Open Meetings Compliance Board ruling on data-center sessions Jun 4, 2026; Akamai-walled", {}),
    ("Dorchester", "https://dorchestercountymd.com/", "eastern_shore", "solar", {}),
    ("Frederick", "https://frederickcountymd.gov/", "frederick", "Quantum Frederick moratorium extended to Jul 1, 2027; MPRP and Valley North lines", {}),
    ("Garrett", "https://www.garrettcountymd.gov/", "western", "wind and solar", {}),
    ("Harford", "https://www.harfordcountymd.gov/", "baltimore_metro", "data-center ordinance / ban Jun 10, 2026", {}),
    ("Howard", "https://www.howardcountymd.gov/", "baltimore_metro", "data-center zoning; agendas on Granicus", {}),
    ("Kent", "https://www.kentcounty.com/", "eastern_shore", "solar; CivicClerk", {}),
    ("Montgomery", "https://www.montgomerycountymd.gov/", "dc_suburbs", "six-month data-center pause Aug 10, 2026; ZTA; Planning Board is M-NCPPC", {}),
    ("Prince George's", "https://www.princegeorgescountymd.gov/", "dc_suburbs", "two-year data-center moratorium Jul 6, 2026 (8-3); council on Legistar; Planning Board is M-NCPPC",
     {"legistar_client": "princegeorgescountymd"}),
    ("Queen Anne's", "https://www.qac.org/", "eastern_shore", "data-center moratorium Jun 4, 2026", {}),
    ("Somerset", "https://www.somersetmd.us/", "eastern_shore", "solar", {}),
    ("St. Mary's", "https://www.stmaryscountymd.gov/", "southern", "data centers and solar", {}),
    ("Talbot", "https://talbotcountymd.gov/", "eastern_shore", "solar; agendas on Granicus", {}),
    ("Washington", "https://www.washco-md.net/", "western", "data-center pause (2026); Hagerstown", {}),
    ("Wicomico", "https://www.wicomicocounty.org/", "eastern_shore", "solar; CivicPlus", {}),
    ("Worcester", "https://worcestermd.gov/", "eastern_shore", "solar; offshore-wind landing", {}),
]
MD_MUNIS = [  # (name, kind, county, website, zoning, reason, extras)
    ("Baltimore City", "city", None, "https://www.baltimorecity.gov/", "own",
     "independent city; council on Legistar; Planning Commission and BMZA", {"legistar_client": "baltimore"}),
    ("City of Frederick", "city", "Frederick", "https://www.cityoffrederickmd.gov/", "own", "Quantum Frederick area; Granicus", {}),
    ("City of Gaithersburg", "city", "Montgomery", "https://www.gaithersburgmd.gov/", "own", "own planning and zoning", {}),
    ("City of Rockville", "city", "Montgomery", "https://www.rockvillemd.gov/", "own", "own planning and zoning", {}),
    ("Town of Poolesville", "town", "Montgomery", "https://www.poolesvillemd.gov/", "own", "own zoning (Agricultural Reserve)", {}),
    ("Town of Laytonsville", "town", "Montgomery", "https://www.laytonsvillemd.gov/", "own", "own zoning; small town", {}),
    ("Town of Barnesville", "town", "Montgomery", "https://www.barnesvillemd.gov/", "own", "own zoning; small town", {}),
    ("Town of Brookeville", "town", "Montgomery", "https://www.townofbrookevillemd.org/", "own", "own zoning; small town", {}),
    ("Town of Washington Grove", "town", "Montgomery", "https://www.washingtongrovemd.org/", "own", "own zoning; small town", {}),
    ("City of Takoma Park", "city", "Montgomery", "https://takomaparkmd.gov/", "county",
     "zoning stays with the Montgomery District Council; council comments", {}),
    ("City of Laurel", "city", "Prince George's", "https://www.cityoflaurel.org/", "own",
     "the one Prince George's municipality with its own zoning; Municode Meetings", {}),
    ("City of Bowie", "city", "Prince George's", "https://www.cityofbowie.org/", "county",
     "zoning stays with the Prince George's District Council; council reviews", {}),
    ("City of College Park", "city", "Prince George's", "https://www.collegeparkmd.gov/", "county",
     "zoning stays with the District Council; council reviews", {}),
    ("City of Greenbelt", "city", "Prince George's", "https://www.greenbeltmd.gov/", "county",
     "zoning stays with the District Council; council reviews", {}),
    ("City of Hyattsville", "city", "Prince George's", "https://www.hyattsville.org/", "county",
     "zoning stays with the District Council; council reviews", {}),
    ("City of Annapolis", "city", "Anne Arundel", "https://www.annapolis.gov/", "own", "state capital; own zoning", {}),
    ("City of Hagerstown", "city", "Washington", "https://www.hagerstownmd.org/", "own", "data centers (Washington County)", {}),
]


def census_counties(st: str) -> list[dict]:
    with open(CENSUS_CSV, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["state"] == st and r["kind"] == "county"]


def cmd_targets(args) -> None:
    # Virginia
    prev = {t["town"]: t for t in (load(DATA / "towns_va.json") or {}).get("towns", [])}
    region_of = {c: g for g, cs in VA_REGION.items() for c in cs}
    va = []
    for r in census_counties("VA"):
        name = r["jurisdiction"]          # "Loudoun County"
        short = name[:-len(" County")]
        old = prev.get(name)
        site = VA_COUNTY_SITES.get(short) or (old or {}).get("website") or r["final_url"] or r["url_probed"]
        note = VA_COUNTY_NOTES.get(short)
        row = {"town": name, "state": "VA", "county": short, "kind": "county", "website": site}
        if old:   # keep the October test's selection notes and website unless corrected above
            row.update({k: old[k] for k in ("selection_group", "selection_reason", "selection_source") if k in old})
            row["website"] = VA_COUNTY_SITES.get(short) or old.get("website") or site
        elif note:
            row.update(selection_group=note[0], selection_reason=note[1], selection_source=note[2])
        else:
            row.update(selection_group=region_of.get(short, "statewide"),
                       selection_reason="statewide county list (all 95); no specific 2025-26 fight in our notes",
                       selection_source=PAYS)
        row["website_source"] = ("October county census (Wikidata) " + ("corrected by hand, 2026-11" if short in VA_COUNTY_SITES else "")).strip()
        row["census_oct_2026"] = {"bucket": r["coverage_bucket"], "platform_or_block": r["platform_or_block_reason"][:60],
                                  "vendors": r["agenda_vendors_seen"][:160]}
        va.append(row)
    assert len(va) == 95, len(va)
    for name, site, why in VA_CITIES:
        va.append({"town": f"City of {name}", "state": "VA", "county": None, "kind": "city", "website": site,
                   "selection_group": "city", "selection_reason": why, "selection_source": PAYS, "website_source": HAND,
                   **({"legistar_client": VA_LEGISTAR[name]} if name in VA_LEGISTAR else {})})
    for name, county, site, why in VA_TOWNS:
        old = prev.get(f"Town of {name}")
        va.append({"town": f"Town of {name}", "state": "VA", "county": county, "kind": "town",
                   "website": (old or {}).get("website") or site,
                   "selection_group": "town", "selection_reason": why,
                   "selection_source": (old or {}).get("selection_source") or PAYS, "website_source": HAND})
    save(TEST / "targets_va.json", va)
    # Maryland
    md = []
    for name, site, group, why, extra in MD_COUNTIES:
        md.append({"town": f"{name} County", "state": "MD", "county": name, "kind": "county", "website": site,
                   "selection_group": group, "selection_reason": why, "selection_source": PAYS,
                   "website_source": "October county census (Wikidata), checked by hand 2026-11", **extra})
    for name, kind, county, site, zoning, why, extra in MD_MUNIS:
        md.append({"town": name, "state": "MD", "county": county, "kind": kind, "website": site, "zoning_power": zoning,
                   "selection_group": "municipality", "selection_reason": why, "selection_source": PAYS,
                   "website_source": HAND, **extra})
    save(TEST / "targets_md.json", md)
    print(f"VA targets: {len(va)} ({Counter(r['kind'] for r in va)}); MD targets: {len(md)} ({Counter(r['kind'] for r in md)})")


# ------------------------------------------------------------------------------------ discover
# Hand corrections after reading the sites (each says why). Applied on top of discovery by `discover` and `curate`.
SANDBOX = ("unreachable from the test sandbox (the egress proxy answered 502 to CONNECT, or robots.txt timed out, on "
           "three tries, 2026-11-02); not a block by the site. Retry from the production host before treating it as down.")
_SANDBOX_VA = ["Bath County", "Buchanan County", "Giles County", "Lee County", "New Kent County", "Russell County",
               "Tazewell County", "Rockingham County", "Town of Hamilton", "Town of Woodstock", "Town of Stephens City",
               "Town of Gordonsville"]
_SANDBOX_MD = ["Town of Laytonsville", "Town of Barnesville"]
CURATED: dict[str, dict[str, dict]] = {
    "VA": {
        # Fairfax: the site's own meeting pages (/boardofsupervisors/oct-13-2026-meeting, the date in the address, the
        # link text "Board of Supervisors Meeting") carry the Final Board Package and the Board Matters PDF; the Granicus
        # video host discovery hit first is only the recordings. Packages can exceed the 40 MB cap (then recorded as too
        # large; the Board Matters PDF still reads). Planning Commission: only monthly calendar PDFs online, no agendas.
        "Fairfax County": {
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "add_listings": [{"board": "Board of Supervisors", "board_key": "select_board", "platform": "agenda_page",
                              "url": "https://www.fairfaxcounty.gov/boardofsupervisors/2026-board-meetings", "date_from_url": True,
                              "board_pattern": r"board\s+of\s+supervisors\s+meeting|\d-20\d\d-meeting$",
                              "board_exclude": r"committee|summary"}],
            "curation_note": "BOS meeting pages dated from their address (date_from_url); Planning Commission posts monthly "
                             "calendar PDFs only; Granicus (video.fairfaxcounty.gov) is the recordings host, robots-disallowed",
        },
        # Arlington: Hyland OnBase "Agenda Online" portal (meetings.arlingtonva.us), server-rendered meeting rows with
        # agenda PDFs; the county site itself links it as "View all Meetings and Agendas".
        "Arlington County": {
            "platform": "onbase_agenda", "platforms": ["onbase_agenda"],
            "add_listings": [{"board": "County Board", "board_key": "select_board", "platform": "onbase_agenda",
                              "url": "https://meetings.arlingtonva.us/CountyBoard", "meeting_type": r"^County Board (Regular|Recessed)"},
                             {"board": "Planning Commission", "board_key": "planning_board", "platform": "onbase_agenda",
                              "url": "https://meetings.arlingtonva.us/Planning"}],
            "curation_note": "OnBase Agenda Online portal (adapters/onbase.py); BZA hearings are on the same portal under "
                             "/Zoning if needed later",
        },
        # Virginia Beach: the City Clerk posts the "Current Brief Agenda" at a fixed address (overwritten each meeting); its
        # date is read from the PDF itself. The index keys documents by URL, so after the first read a new agenda at the
        # same address is not re-read until a refresh rule exists (see va_md_wave.md). Full agendas sit in Laserfiche.
        "City of Virginia Beach": {
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "add_listings": [{"board": "City Council", "board_key": "select_board", "platform": "agenda_page",
                              "url": "https://clerk.virginiabeach.gov/city-council", "date_from_document": True,
                              "board_pattern": "agenda", "unlabeled": True, "follow": False}],
            "curation_note": "fixed-address brief agenda dated from the document; re-read needs a refresh rule",
        },
        # Portsmouth: robots.txt Crawl-delay 20 s. Listing pages may wait 20 s (the listing cap) but the agenda files need
        # the 10 s document cap, so nothing can be read; discovery's "no recent agendas" was the wrong reason.
        "City of Portsmouth": {
            "status": "not_automated", "automated": False, "listings": [], "reason_code": "crawl_delay_exceeds_cap",
            "reason": "robots.txt on www.portsmouthva.gov asks for a Crawl-delay of 20 s: at the listing cap, above the 10 s "
                      "document cap, so agenda files cannot be fetched; CivicClerk V8 portal (portsmouthva.v8.civicclerk.com) "
                      "has no public API host",
            "curation_note": "reason corrected by hand",
        },
        # Loudoun: the Board's business meetings and public hearings are on eSCRIBE (readable). The Planning Commission's
        # agendas are on OnBoard (onboard.loudoun.gov, robots.txt disallows AgendaAheadBot) and in Laserfiche.
        "Loudoun County": {"curation_note": "Planning Commission agendas on onboard.loudoun.gov (robots.txt disallows us) and "
                                            "lfportal.loudoun.gov (Laserfiche); Granicus is the video host"},
        "Prince William County": {"curation_note": "Board of County Supervisors agendas only through pwcgov.granicus.com "
                                                   "(robots.txt disallows us); /board-meetings answers HTTP 403; Planning Commission readable"},
        **{n: {"sandbox_note": SANDBOX} for n in _SANDBOX_VA},
        "Floyd County": {"sandbox_note": "www.floydcova.org answers HTTP 404 for the homepage from the sandbox; check the current address"},
    },
    "MD": {
        # Montgomery County: the Council posts its weekly agendas as PDFs behind an /archival-document?document= viewer page
        # (file names carry the date: 102926 full comm.pdf); Granicus is the video host. The Planning Board (M-NCPPC) has one
        # page per meeting (/agenda-item/november-5-2026/) whose text lists the items; its PDFs are staff reports.
        "Montgomery County": {
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "add_listings": [{"board": "County Council", "board_key": "select_board", "platform": "agenda_page",
                              "url": "https://www.montgomerycountymd.gov/government/legislative-branch/county-council/council-meetings-agendas",
                              "doc_href_extra": r"archival-document\?document=", "unlabeled": True, "follow": False,
                              "board_exclude": r"summary|speakers?|confirmations"},
                             {"board": "Montgomery Planning Board", "board_key": "planning_board", "platform": "agenda_page",
                              "url": "https://montgomeryplanningboard.org/agendas/", "date_from_url": True, "meeting_page_self": True}],
            "curation_note": "council weekly agenda PDFs behind a viewer link (doc_href_extra); M-NCPPC Planning Board meeting "
                             "pages read as the agenda (date_from_url, meeting_page_self); Granicus is the video host",
        },
        # Howard County: discovery took the school system's Diligent portal (hcpss) for the county's. The Council's hearings
        # and the Board of Appeals cases are in OLIS (apps.howardcountymd.gov/Olis), a server-rendered table with agenda PDFs.
        "Howard County": {
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "add_listings": [{"board": "Board of Appeals", "board_key": "zoning_board_of_appeals", "platform": "agenda_page",
                              "url": "https://apps.howardcountymd.gov/Olis/UpcomingHearings", "unlabeled": True, "follow": False,
                              "board_pattern": r"\bBA\b|board\s+of\s+appeals"},
                             {"board": "County Council", "board_key": "select_board", "platform": "agenda_page",
                              "url": "https://apps.howardcountymd.gov/Olis/UpcomingHearings", "unlabeled": True, "follow": False,
                              "board_pattern": r"legislative|council|\bCB\b|\bCR\b|public\s+hearing", "board_exclude": r"\bBA\b"}],
            "curation_note": "OLIS upcoming hearings (Board of Appeals cases now; council sessions when listed); the Diligent "
                             "portal discovery found belongs to the school system; Granicus is the video host",
        },
        "Prince George's County": {"curation_note": "County Council (and District Council zoning sessions) on Legistar; the "
                                                    "M-NCPPC Planning Board's agendas load by script on pgplanningboard.org, "
                                                    "not found as documents; county homepage behind Akamai"},
        **{n: {"sandbox_note": SANDBOX} for n in _SANDBOX_MD},
    },
}

ABOUT = {
    "VA": ("Agenda Ahead Virginia (2026-11, gated): all 95 counties (Board of Supervisors, Planning Commission, BZA), the "
           "38 independent cities and {nt} towns where data-center, solar or battery fights are reported. Same row shape as "
           "towns_ma_all.json plus state, kind, selection_group / selection_reason / selection_source and the October "
           "county census bucket. Built by `python3 experiments/va_md_wave.py discover --state VA`; the 37 places of the "
           "October test (experiments/mi_va_test.py) keep their selection notes."),
    "MD": ("Agenda Ahead Maryland (2026-11, gated): the 23 counties and Baltimore City (council or county commissioners, "
           "planning commission or M-NCPPC planning board, board of appeals) plus {nt} Montgomery, Prince George's, "
           "Frederick, Anne Arundel and Washington County municipalities. Same row shape as towns_ma_all.json plus state, "
           "kind, zoning_power (own / county: Prince George's and Montgomery municipalities other than Laurel, Rockville, "
           "Gaithersburg, Poolesville and four small towns have no zoning power; the District Council zones), "
           "selection_group / selection_reason / selection_source. Built by `python3 experiments/va_md_wave.py discover "
           "--state MD`."),
}
MAPPING = {
    "VA": {"Board of Supervisors, Town / City Council": "select_board", "Planning Commission": "planning_board",
           "Board of Zoning Appeals (BZA)": "zoning_board_of_appeals"},
    "MD": {"County Council / Board of County Commissioners / District Council, City or Town Council, Mayor and Board of Aldermen":
           "select_board", "Planning Commission, Planning Board (M-NCPPC)": "planning_board",
           "Board of Appeals / Board of Zoning Appeals / Board of Municipal and Zoning Appeals": "zoning_board_of_appeals"},
}
GATE_NOTE = ("Test state: not part of the production daily run. Crawled only by `python3 -m watch351.daily --states VA,MD "
             "--output-dir ../data/test/va_md --hits-name hits_va_md.json` (experiments/va_md_wave.py crawl).")


def cmd_discover(args) -> None:
    st = args.state.upper()
    targets = load(TEST / f"targets_{st.lower()}.json")
    towns_file = DATA / f"towns_{st.lower()}.json"
    prev_doc = load(towns_file) or {}
    prev = {t["town"]: t for t in prev_doc.get("towns", [])}
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    todo = [t for t in targets if wanted is None or t["town"].lower() in wanted]
    fetcher = PoliteFetcher()
    t0 = time.monotonic()

    def one(t):
        try:
            return discover_place(fetcher, t, st, list(ALL3))
        except Exception as e:  # noqa: BLE001 - one site must not stop the census
            logging.exception("discovery crashed for %s", t["town"])
            return {**t, "status": "not_automated", "reason_code": "discovery_error", "automated": False,
                    "reason": f"{type(e).__name__}: {str(e)[:160]}", "listings": []}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one, todo))
    posted = []
    for r in results:
        posted += [dict(p, town=r["town"]) for p in r.pop("_posted_rows", [])]
        apply_curated(st, r)
        prev[r["town"]] = r
    order = [t["town"] for t in targets]
    rows = [prev[n] for n in order if n in prev]
    doc = {
        "_about": ABOUT[st].format(nt=sum(1 for r in rows if r.get("kind") in ("town", "city") and r["town"].startswith("Town"))
                                   if st == "VA" else sum(1 for r in rows if r.get("kind") != "county")),
        "generated": now_iso(), "state": st, "gated": True, "gate_note": GATE_NOTE,
        "boards_tracked": ALL3, "board_key_mapping": MAPPING[st],
        "evidence_rule": "a board is automated only if its listing shows >=1 agenda/packet/notice dated within "
                         "[today-120d, today+120d] and the first such document is fetchable under robots.txt",
        "count": len(rows), "automated": sum(1 for r in rows if r.get("automated")), "towns": rows,
    }
    save(towns_file, doc)
    pp = TEST / f"posted_stamps_{st.lower()}.json"
    old = load(pp) or []
    keep = [p for p in old if p["town"] not in {r["town"] for r in results}]
    save(pp, keep + posted)
    print(f"{st}: {len(results)} discovered in {time.monotonic() - t0:.0f}s; fetcher {fetcher.stats}")
    for r in results:
        print(f"  {r['town']:<30} {str(r.get('platform') or '-'):<18} {len(r.get('listings') or []):>2} "
              f"{'AUTO' if r.get('automated') else r.get('reason_code')}: "
              f"{'' if r.get('automated') else (r.get('reason') or '')[:110]}")


def apply_curated(st: str, r: dict) -> None:
    cur = CURATED.get(st, {}).get(r["town"])
    if not cur:
        return
    cur = dict(cur)
    extra = cur.pop("add_listings", [])
    r.update(cur)
    if extra:
        have = {(l["board_key"], l["url"]) for l in r.get("listings") or []}
        r["listings"] = (r.get("listings") or []) + [l for l in extra if (l["board_key"], l["url"]) not in have]
        r["automated"], r["status"], r["reason_code"], r["reason"] = True, "automated", None, None
        r["platforms"] = sorted({l.get("platform") or "agenda_page" for l in r["listings"]} | set(r.get("platforms") or []))
        r["platform"] = r.get("platform") or r["platforms"][0]
        for l in extra:
            r.setdefault("board_evidence", {})[l["board_key"]] = {"board": l["board"], "source": l.get("platform", "agenda_page"),
                                                                  "url": l["url"], "n_recent": None, "latest": None,
                                                                  "note": "curated listing (checked by hand)"}
        r["boards_found"] = sorted(set(r.get("boards_found") or []) | {l["board_key"] for l in extra})
        r["boards_missing"] = [k for k in ALL3 if k not in r["boards_found"]]
    r["curated"] = True


# Maryland code and commission counties govern through a Board of County Commissioners, not a council.
MD_COMMISSIONER_COUNTIES = {"Allegany", "Calvert", "Caroline", "Carroll", "Garrett", "Kent", "Queen Anne's", "Somerset",
                            "St. Mary's", "Washington", "Worcester"}
_BAD_LABEL = re.compile(r"^select board\s*/\s*council$|^planning board$|^zoning board of appeals$|"
                        r"\d{1,2}/\d{1,2}/\d{2,4}|agendas?\s*(?:&|and)\s*minutes|meeting\s+(?:agendas|packets)|\bagendas?\b|"
                        r"\bpackets?\b|\bpackages?\b|\bminutes\b|monthly\s+meetings|\bBOS\s+pack\b", re.I)
_DATED = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}")


def relabel(st: str, r: dict) -> int:
    """New England default labels ("Select Board / Council") and document titles used as board names
    ("09/14/2023 Board of Supervisors Worksession", "Town Council Meeting Agendas") become the state's
    label for the body (discover_sites.STATE_BOARD_LABELS). Returns how many listings changed."""
    from watch351.discover_sites import default_label
    n = 0
    for l in r.get("listings") or []:
        name = l.get("board") or ""
        if _BAD_LABEL.search(name) and (_DATED.search(name)
                                        or not re.search(r"public hearing|work ?session|business meeting", name, re.I)):
            new = default_label(st, r.get("kind"), l["board_key"])
            if st == "MD" and r.get("kind") == "county" and l["board_key"] == "select_board" and r.get("county") in MD_COMMISSIONER_COUNTIES:
                new = "Board of County Commissioners"
            if new != name:
                l["board_label_was"] = name
                l["board"] = new
                n += 1
    return n


def cmd_curate(args) -> None:
    """Re-apply CURATED to the saved towns files without any request, and relabel boards."""
    for st in STATES:
        path = DATA / f"towns_{st.lower()}.json"
        doc = load(path)
        if not doc:
            continue
        changed = 0
        for r in doc["towns"]:
            apply_curated(st, r)
            changed += relabel(st, r)
        print(st, "relabeled listings:", changed)
        doc["automated"] = sum(1 for r in doc["towns"] if r.get("automated"))
        save(path, doc)
        print(st, "automated", doc["automated"], "of", doc["count"])


# ------------------------------------------------------------------------------------ crawl
def cmd_crawl(args) -> None:
    out = TEST
    cmd = [sys.executable, "-m", "watch351.daily", "--states", "VA,MD", "--output-dir", str(out),
           "--hits-name", HITS_NAME, "--days-back", str(args.days_back), "--days-ahead", str(args.days_ahead),
           "--workers", str(args.workers), "--request-log", str(out / f"requests_{args.label}.tsv")]
    if args.places:
        cmd += ["--towns", args.places]
    print(" ".join(cmd))
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=CRAWLER)
    print(f"exit {proc.returncode}, wall {time.monotonic() - t0:.0f}s")
    runs = out / "state" / "runs"
    latest = max(runs.glob("*.json"), key=lambda p: p.stat().st_mtime)
    save(out / "runs" / f"run_{args.label}.json", load(latest))
    print(f"saved {out / 'runs' / f'run_{args.label}.json'}")


# ------------------------------------------------------------------------------------ analyze
def cmd_analyze(args) -> None:
    import mi_va_analysis as A
    from watch351.current import validate
    from watch351.models import Window
    A.TEST = TEST
    hits_doc = load(TEST / HITS_NAME)
    reps = {p.stem.replace("run_", ""): load(p) for p in sorted((TEST / "runs").glob("run_*.json"))}
    rep1 = reps.get(args.base_run) or next(iter(reps.values()))
    health = load(TEST / "state" / "town_health.json") or {}
    crawl_day = date.fromisoformat(rep1.get("date") or hits_doc["generated"][:10])
    w = rep1["window"]
    window = Window(date.fromisoformat(w["start"]), date.fromisoformat(w["end"]))
    res = {"generated": now_iso(), "crawl_day": crawl_day.isoformat(), "window": w,
           "contract_validation_errors": validate(hits_doc), "states": {}}
    for st in STATES:
        rows, docs = A.load_rows(st), A.load_docs(st)
        cov = A.coverage(st, rows, docs, health, hits_doc)
        # per kind and platform, and per body
        per = cov["places"]
        by_plat = defaultdict(Counter)
        for p in per:
            by_plat[p["platform"] or (p["reason_code"] or "-")][p["class"]] += 1
        bodies = Counter()
        for p in per:
            for k in p["boards_tracked"]:
                bodies[(p["kind"], k, "read" if k in p["boards_read"] else "not_read")] += 1
        cov["by_platform"] = {k: dict(v) for k, v in sorted(by_plat.items())}
        cov["bodies"] = {f"{kind}:{k}": {"read": bodies[(kind, k, "read")], "not_read": bodies[(kind, k, "not_read")]}
                         for kind in sorted({p["kind"] for p in per}) for k in ALL3}
        res["states"][st] = {"coverage": cov, "output": A.output(st, docs, hits_doc, rep1),
                             "freshness": A.freshness(st, rows, docs, crawl_day, window)}
    res["reliability"] = {k: {kk: v.get(kk) for kk in ("duration_seconds", "towns_attempted", "towns_succeeded", "towns_failed",
                                                        "towns_partial", "documents_listed", "documents_already_indexed",
                                                        "new_documents", "documents_retried", "document_errors", "network",
                                                        "new_hits", "hits_current", "errors_total")} for k, v in reps.items()}
    save(TEST / "analysis_va_md.json", res)
    for st in STATES:
        c = res["states"][st]["coverage"]
        print(st, json.dumps({"by_kind": c["by_kind"], "by_platform": c["by_platform"], "bodies": c["bodies"],
                              "output": res["states"][st]["output"],
                              "freshness": res["states"][st]["freshness"]}, indent=1)[:9000])
    print("contract errors:", res["contract_validation_errors"][:5])


# ------------------------------------------------------------------------------------ sample
def cmd_sample(args) -> None:
    """A simple random sample of n hits over both states (every hit equally likely), seeded; each with
    about 1,500 characters of the document's text around the snippet, for the hand check."""
    import mi_va_analysis as A
    A.TEST = TEST
    hits_doc = load(TEST / HITS_NAME)
    hits = sorted(hits_doc["hits"], key=lambda h: h["id"])
    ex = set()
    if args.exclude:
        prev = load(Path(args.exclude)) or []
        items = prev if isinstance(prev, list) else [it for rnd in prev.get("rounds", []) for it in rnd.get("items", [])]
        ex = {it["id"] for it in items}
    hits = [h for h in hits if h["id"] not in ex]
    rng = random.Random(args.seed)
    if args.state_n:   # stratified: "VA:40,MD:20" draws that many from each state, each hit in a state equally likely
        picked = []
        for part in args.state_n.split(","):
            st, n = part.split(":")
            pool = [h for h in hits if h["state"] == st.strip().upper()]
            picked += rng.sample(pool, min(int(n), len(pool)))
    else:
        picked = rng.sample(hits, min(args.n, len(hits)))
    picked = sorted(picked, key=lambda h: (h["state"], h["town"], h["id"]))
    out = []
    for h in picked:
        text = A.doc_text(h["source_url"])
        pos = text.find(h["snippet"][:100].rstrip("…"))
        ctx = text[max(0, pos - 600): pos + 900] if pos >= 0 else ""
        out.append({**{k: h.get(k) for k in ("id", "state", "town", "board", "meeting_date", "topics", "snippet",
                                             "source_url", "text_source")}, "context": ctx})
    dest = TEST / (args.worksheet or "precision_worksheet_r1.json")
    save(dest, out)
    print(f"wrote {len(out)} hits to {dest}", Counter(h["state"] for h in out), "of", len(hits), "hits")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["targets", "discover", "curate", "crawl", "analyze", "sample"])
    p.add_argument("--state", default="VA")
    p.add_argument("--places")
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=120)
    p.add_argument("--label", default="run1")
    p.add_argument("--base-run", default="run1")
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--exclude")
    p.add_argument("--state-n", help="sample: stratified draw, e.g. VA:40,MD:20")
    p.add_argument("--worksheet")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    {"targets": cmd_targets, "discover": cmd_discover, "curate": cmd_curate, "crawl": cmd_crawl,
     "analyze": cmd_analyze, "sample": cmd_sample}[args.command](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
