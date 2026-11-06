"""NYS Office of Renewable Energy Siting (ORES) permit applications -> Agenda Ahead items (gated).

ORES (now part of the Department of Public Service) permits every renewable energy facility of 25 MW or
more and the large transmission lines; towns are consulted but do not decide. Its page
https://dps.ny.gov/ores-permit-applications lists every application by stage (notices of intent, pending
completeness, incomplete, complete under review, permitted, withdrawn, denied, declaratory rulings) with
the permit number, the project name and a description that names the towns and the county.

Read with one plain GET through watch351.fetch.PoliteFetcher (dps.ny.gov's robots.txt is the Drupal default
and allows the page). The matter pages in the Document and Matter Management system load their tables with
scripts, so they are not read; hearing dates are therefore not known here, only the stage.

Item: permit number, project name, stage, description, towns (as named and as the site names them), county,
MW, technology topics, decision date when the description gives one (withdrawn, relinquished, permitted),
link to the matter in DMM.

Hit (source_kind "state_docket"): one per town for every application in a pending stage or decided inside
the window, board "NYS Office of Renewable Energy Siting", meeting_date = the decision date for decided
applications, else null (date_kind "listed").

    cd projects/351watch/crawler
    python3 -m watch351.sources.ny_ores --days 30
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from ..fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from .notice_feeds import (DEFAULT_OUT, NYPlaces, check_out_dir, county_named, iso, load_ledger, make_hit,
                           municipalities, network_report, notice_topics, parse_dates, sentences, snippet_of,
                           window_start, write_outputs)
from .state_feeds import clean, first_seen, now_iso

log = logging.getLogger("ny_ores")

SOURCE = "ny_ores"
SOURCE_KIND = "state_docket"
STATE = "NY"
BOARD = "NYS Office of Renewable Energy Siting"
URL = "https://dps.ny.gov/ores-permit-applications"
PAGE_MAX_AGE = 20 * 3600
PENDING_STAGES = ("Notices of Intent", "Applications Pending Completeness Determination", "Incomplete Applications",
                  "Complete Applications Under Review", "Request for Declaratory Ruling")
DECIDED_STAGES = ("Permitted Applications", "Withdrawn Applications / Relinquished Permits", "Denied Applications")
_MW = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*[-\s]?\s*(?:Megawatts?|MW)\b", re.I)
_DECISION = re.compile(r"(?:Withdrawn|Relinquished|Denied|issued|granted|received a Permit)[^.]{0,80}?"
                       r"(?:effective|on|dated)\s+((?:January|February|March|April|May|June|July|August|September|"
                       r"October|November|December)\s+\d{1,2},\s+\d{4})", re.I)


def parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    main = soup.find("main") or soup
    out = []
    stage = None
    for el in main.find_all(["h2", "table"]):
        if el.name == "h2":
            stage = clean(el.get_text(" "))
            continue
        if not stage or stage == "On this page":
            continue
        rows = el.find_all("tr")
        for tr in rows[1:]:
            cells = [clean(td.get_text(" ")) for td in tr.find_all(["td", "th"])]
            if len(cells) < 3 or not cells[0]:
                continue
            link = next((a.get("href") for a in tr.find_all("a") if "MatterManagement" in (a.get("href") or "")), None)
            out.append({"permit_number": cells[0], "project_name": cells[1], "description": cells[2], "stage": stage,
                        "link": link or URL})
    return out


def enrich(row: dict, places: NYPlaces) -> dict:
    desc = row["description"]
    munis = municipalities(desc)
    towns = []
    for name, kind in munis:
        site, configured = places.resolve(name, kind)
        towns.append({"as_named": name, "kind": kind, "town": site, "configured": configured})
    county = county_named(desc)
    mw = None
    m = _MW.search(desc)
    if m:
        try:
            mw = float(m.group(1).replace(",", ""))
        except ValueError:
            mw = None
    topics = notice_topics(f"{row['project_name']} {desc}")
    if not topics:
        topics = ["clean_energy_siting"]        # every ORES matter is a renewable or transmission siting
    decided = None
    dm = _DECISION.search(desc)
    if dm:
        ds = parse_dates(dm.group(1))
        decided = ds[0] if ds else None
    if not decided and row["stage"] in DECIDED_STAGES:
        ds = parse_dates(desc)
        decided = ds[-1] if ds else None
    return {**row, "towns": towns, "county": county, "mw": mw, "topics": topics, "decision_date": iso(decided),
            "pending": row["stage"] in PENDING_STAGES, "siting_relevant": True}


def to_hits(item: dict, since: date) -> list[dict]:
    if not item["pending"]:
        if not item.get("decision_date") or date.fromisoformat(item["decision_date"]) < since:
            return []
        when, date_kind = date.fromisoformat(item["decision_date"]), "decision"
    else:
        when, date_kind = None, "listed"
    hits = []
    mw = f"{item['mw']:g} MW " if item.get("mw") else ""
    for t in item["towns"]:
        if not t["town"]:
            continue
        # the town is in the snippet so that each host town's hit has its own id (id = source_url + snippet)
        snippet = snippet_of(f"ORES {item['permit_number']} ({item['stage']}), {mw}{item['project_name']}, in {t['town']}.",
                             sentences(item["description"], 1))
        hits.append(make_hit(
            source=SOURCE, source_kind=SOURCE_KIND, state=STATE, town=t["town"], county=item.get("county"), board=BOARD,
            meeting_date=when, date_kind=date_kind, topics=item["topics"], snippet=snippet,
            source_url=item["link"] + ("" if item["link"] != URL else f"#{item['permit_number']}"), listing_url=URL,
            document_title=f"ORES permit application {item['permit_number']}: {item['project_name']}",
            first_seen=item["first_seen"], headline_text=f"{item['project_name']} ({item['permit_number']}): {item['stage']}",
            extra={"stage": item["stage"], "mw": item.get("mw"), "configured": t["configured"],
                   "host_towns": [x["town"] for x in item["towns"] if x["town"]]}))
    return hits


def run(fetcher: PoliteFetcher, out_dir: Path, days: int = 30, data_dir: Path | None = None,
        today: date | None = None) -> dict:
    check_out_dir(out_dir)
    started = now_iso()
    since = window_start(days, today)
    places = NYPlaces(data_dir) if data_dir else NYPlaces()
    ledger = load_ledger(out_dir, SOURCE)
    with fetcher.purpose("listing"):
        r = fetcher.get(URL, max_age=PAGE_MAX_AGE)
    if not r.ok:
        raise FetchError(f"ORES page HTTP {r.status}")
    rows = parse_page(r.text)
    items = []
    for row in rows:
        it = enrich(row, places)
        it["first_seen"] = first_seen(ledger, f"{it['permit_number']}|{it['stage']}", started)
        items.append(it)
    hits = [h for i in items for h in to_hits(i, since)]
    report = {
        "source": SOURCE, "started": started, "finished": now_iso(), "since": since.isoformat(),
        "applications": len(items), "pending": sum(i["pending"] for i in items), "hits": len(hits),
        "stages": dict(Counter(i["stage"] for i in items)),
        "topics": dict(Counter(t for i in items for t in i["topics"]).most_common()),
        "towns_unresolved": sorted({t["as_named"] for i in items for t in i["towns"] if not t["town"]}),
        "errors": [], "network": network_report(fetcher),
    }
    write_outputs(SOURCE, out_dir, items, hits, URL, report, ledger)
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--offline", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    rep = run(PoliteFetcher(a.cache_dir, offline=a.offline), a.out_dir, a.days)
    print(f"ORES: {rep['applications']} applications ({rep['pending']} pending), {rep['hits']} hits; "
          f"stages {rep['stages']}; unresolved towns {rep['towns_unresolved']}; network {rep['network']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
