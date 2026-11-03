#!/usr/bin/env python3
"""Great Lakes wave (2026-11), behind the gate: southeast Michigan townships plus the county planning
commission route (MCL 125.3307), then central Ohio and Cincinnati-exurb townships plus Ohio's county
and regional planning commissions (the ORC 519.12 review route, cheap_township_coverage.md section 1).

    cd projects/351watch/crawler
    python3 experiments/great_lakes_test.py targets --state MI      # data/test/great_lakes/targets_mi.json
    python3 experiments/great_lakes_test.py targets --state OH      # data/test/great_lakes/targets_oh.json
    python3 experiments/great_lakes_test.py discover --state MI     # new rows -> data/towns_mi.json (existing rows kept)
    python3 experiments/great_lakes_test.py discover --state OH     # -> data/towns_oh.json
    python3 experiments/great_lakes_test.py annotate --state OH     # coverage fields, no request
    python3 experiments/great_lakes_test.py crawl --label run1      # watch351.daily --states MI,OH -> data/test/great_lakes/
    python3 experiments/great_lakes_test.py analyze                 # coverage three ways, by county and route
    python3 experiments/great_lakes_test.py sample --per-state 30 --random 2028

Both towns files are "gated": the production daily run never reads them; watch351.daily crawls them
only with --states MI,OH and an --output-dir other than data/ (here data/test/great_lakes/).

Website sources for the new rows (data/test/great_lakes/sources/township_sites.json): the county
governments' own township-link pages, Wikipedia infoboxes where Wikimedia let the bot read them, and
web search for the rest; each row says which (`website_source`). All network access goes through
watch351.fetch.PoliteFetcher (AgendaAheadBot UA, robots.txt on every hop, <= 1 request/second/host,
crawl-delay honored up to the caps, no logins, no POSTs, no challenge solving).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAWLER = HERE.parent
sys.path.insert(0, str(CRAWLER))
sys.path.insert(0, str(HERE))

from watch351.discover_sites import discover_place  # noqa: E402
from watch351.fetch import PoliteFetcher  # noqa: E402

DATA = CRAWLER.parent / "data"
TEST = DATA / "test" / "great_lakes"
SOURCES = TEST / "sources"
HITS_NAME = "hits_great_lakes.json"
STATES = ("MI", "OH")
ALL3 = ["select_board", "planning_board", "zoning_board_of_appeals"]
SE_MI = ["Washtenaw", "Livingston", "Oakland", "Macomb", "Monroe", "Lenawee", "Jackson", "Genesee", "Lapeer",
         "St. Clair", "Shiawassee", "Ingham"]
OH8 = ["Licking", "Union", "Franklin", "Delaware", "Logan", "Champaign", "Clermont", "Butler"]
OH88 = ["Adams", "Allen", "Ashland", "Ashtabula", "Athens", "Auglaize", "Belmont", "Brown", "Butler", "Carroll",
        "Champaign", "Clark", "Clermont", "Clinton", "Columbiana", "Coshocton", "Crawford", "Cuyahoga", "Darke",
        "Defiance", "Delaware", "Erie", "Fairfield", "Fayette", "Franklin", "Fulton", "Gallia", "Geauga", "Greene",
        "Guernsey", "Hamilton", "Hancock", "Hardin", "Harrison", "Henry", "Highland", "Hocking", "Holmes", "Huron",
        "Jackson", "Jefferson", "Knox", "Lake", "Lawrence", "Licking", "Logan", "Lorain", "Lucas", "Madison",
        "Mahoning", "Marion", "Medina", "Meigs", "Mercer", "Miami", "Monroe", "Montgomery", "Morgan", "Morrow",
        "Muskingum", "Noble", "Ottawa", "Paulding", "Perry", "Pickaway", "Pike", "Portage", "Preble", "Putnam",
        "Richland", "Ross", "Sandusky", "Scioto", "Seneca", "Shelby", "Stark", "Summit", "Trumbull", "Tuscarawas",
        "Union", "Van Wert", "Vinton", "Warren", "Washington", "Wayne", "Williams", "Wood", "Wyandot"]
SELECTION_SOURCE = "research_notes/Expansion/where_it_pays_2026.md section 2 (areas 2 and 3), section 4 recommendation 3"
COUNTY_ROUTE = {
    "MI": "County planning commission: reviews every township zoning ordinance and amendment under MCL 125.3307 "
          "(30 days, after the township planning commission's hearing, before the township board votes), so its "
          "agenda names township items; a township with no site still gets its zoning amendments this way",
    "OH": "County or regional planning commission: every township zoning text or map amendment is transmitted to it "
          "under ORC 519.12 and its recommendation is read at the township zoning commission's hearing, so its agenda "
          "names township items; a township with no site still gets its zoning amendments this way",
}

# Hand corrections after reading the sites (each says why), applied on top of discovery.
CURATED: dict[str, dict[str, dict]] = {
    "MI": {
        # Jackson County's planning commission (JCPC) posts its packets on the Region 2 Planning Commission
        # site, not on the county's BoardDocs (which refuses the bot): region2planning.com/jcpc/ lists one
        # packet a month beside the transportation committees' packets (TAC, Policy, RTF2), hence the pattern.
        "Jackson County": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Jackson County Planning Commission", "board_key": "planning_board",
                          "platform": "agenda_page", "url": "https://www.region2planning.com/jcpc/",
                          "board_pattern": r"\bJCPC\b|planning\s+commission", "board_exclude": r"\bTAC\b|\bRTF|policy|minutes"}],
            "curation_note": "JCPC packets on the Region 2 Planning Commission site (the county's own agendas are on BoardDocs)",
        },
        # Lenawee County's planning commission (LCPC) also posts on Region 2's site: one packet a month
        # ("January Packet"), dated from the packet's first page.
        "Lenawee County": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Lenawee County Planning Commission", "board_key": "planning_board",
                          "platform": "agenda_page", "url": "https://www.region2planning.com/lenawee-county-planning-commission/",
                          "board_pattern": r"packet|\bLCPC\b", "board_exclude": r"worksheet|form|\bTAC\b|policy|R2PC"}],
            "curation_note": "LCPC packets on the Region 2 Planning Commission site (dated from the file name; the page listed "
                             "January to June 2026 on 2026-11-02, nothing later)",
        },
        # The Genesee County Metropolitan Planning Commission posts monthly agenda packets on gcmpc.org,
        # named by month only ("November Agenda Packet"); the meeting date is read from the packet.
        "Genesee County": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Genesee County Metropolitan Planning Commission", "board_key": "planning_board",
                          "platform": "agenda_page",
                          "url": "https://gcmpc.org/genesee-county-metropolitan-planning-commission/",
                          "board_pattern": r"agenda", "date_from_document": True}],
            "county_body": "Genesee County Metropolitan Planning Commission",
            "curation_note": "GCMPC agenda packets on gcmpc.org (the county site's robots.txt was unreachable), dated from the packet text",
        },
    },
    "OH": {
        # Licking County's planning commission agendas are on depts/planning/planning/agendas/, but every
        # document is a civicax/filebank/blobdload.aspx link, and the county's robots.txt disallows that path.
        "Licking County": {
            "automated": False, "status": "not_automated", "reason_code": "documents_blocked",
            "reason": "Licking County Planning Commission agendas are listed at lickingcounty.gov/depts/planning/planning/"
                      "agendas/default.htm, but the documents are civicax/filebank/blobdload.aspx links that the county's "
                      "robots.txt disallows; not fetched",
            "platform": None, "listings": [],
            "curation_note": "agenda page found by hand; documents robots-disallowed (CivicaSoft file bank)",
        },
        # Franklin County's Economic Development & Planning department posts its boards' agendas on one
        # page: Planning Commission (PC), Rural Zoning Commission (RZC, the county's own zoning for
        # unincorporated townships), BZA and the Board of Commissioners' zoning cases (BOC).
        "Franklin County": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Franklin County Planning Commission", "board_key": "planning_board", "platform": "agenda_page",
                          "url": "https://www.franklincountyohio.gov/Business-Development/Development-Planning/EDP-Meetings",
                          "board_pattern": r"-PC-|planning\s+commission", "board_exclude": r"-RZC-|-BZA-|-BOC-|minutes"},
                         {"board": "Franklin County Rural Zoning Commission", "board_key": "planning_board", "platform": "agenda_page",
                          "url": "https://www.franklincountyohio.gov/Business-Development/Development-Planning/EDP-Meetings",
                          "board_pattern": r"-RZC-|rural\s+zoning", "board_exclude": r"-PC-|-BZA-|-BOC-|minutes"}],
            "curation_note": "EDP meetings page (PC and RZC agendas, notices and packets), replacing the single meeting page discovery found",
        },
        # Butler County's Board of Commissioners is on iQM2 (closed), but the Planning Commission's monthly
        # agendas are PDFs on the Development department's agendas page.
        "Butler County": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Butler County Planning Commission", "board_key": "planning_board", "platform": "agenda_page",
                          "url": "https://bcohio.gov/board_of_commissioners/commissioner_departments/development/agendas.php",
                          "board_pattern": r"PC_Agenda|planning", "board_exclude": r"minutes|zoning\s+appeals|\bBZA\b"}],
            "curation_note": "Planning Commission agendas on the Development department page (the commissioners' iQM2 portal refuses the bot)",
        },
        # Logan-Union-Champaign RPC: the "This Month at LUC" Wix page lists each item's staff report and
        # supporting documents without dates or an "agenda" label; documents are dated from their text.
        "Logan-Union-Champaign Regional Planning Commission": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Logan-Union-Champaign Regional Planning Commission", "board_key": "planning_board",
                          "platform": "agenda_page", "url": "https://www.lucplanning.com/thismonthatluc",
                          "unlabeled": True, "date_from_document": True,
                          "board_exclude": r"minutes|assessment|budget|treasurer|committee\s+members|essential"}],
            "covers_counties": ["Logan", "Union", "Champaign"],
            "county_body": "Logan-Union-Champaign Regional Planning Commission",
            "curation_note": "regional body for Logan, Union and Champaign counties; This Month at LUC page, documents dated from their text",
        },
        # Delaware County's planning body is the Delaware County Regional Planning Commission, on its own site;
        # its monthly mailing page lists township items about 2.5 weeks ahead (cheap_township_coverage.md).
        "Delaware County": {
            "automated": True, "status": "automated", "reason_code": None, "reason": None,
            "platform": "agenda_page", "platforms": ["agenda_page"],
            "listings": [{"board": "Delaware County Regional Planning Commission", "board_key": "planning_board",
                          "platform": "agenda_page", "url": "https://regionalplanning.co.delaware.oh.us/current_events/mailing/",
                          "unlabeled": True, "board_exclude": r"minutes|financial|activity"}],
            "county_body": "Delaware County Regional Planning Commission",
            "township_bare_names": True,
            "curation_note": "the county's planning body is the Regional Planning Commission; its monthly mailing page lists each "
                             "item as its own document (\"07-25.1 / Estates at Berlin Sec 1 / Berlin / 25 lots\"), the township "
                             "by bare name (attribution.bare_township), about two and a half weeks before the meeting",
        },
    },
}


def tracked_for(row: dict) -> list[str]:
    if row.get("kind") == "county":
        return ["planning_board"]   # county / regional planning commissions only (the township-amendment review)
    return list(ALL3)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def load(path: Path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


# ------------------------------------------------------------------ targets
def _sites() -> dict:
    """'ST:County:Town' -> {"website", "source"} from data/test/great_lakes/sources/township_sites.json."""
    return load(SOURCES / "township_sites.json", {}) or {}


def _dedupe_names(rows: list[dict], taken: set[str]) -> None:
    """Same-named townships in one state get the county in parentheses ("Liberty Township (Delaware
    County)"), the way NY ids do in data/neighbors.json; names already in use stay as they are."""
    short = Counter(r["town"] for r in rows)
    for r in rows:
        if short[r["town"]] > 1 or r["town"] in taken:
            r["town"] = f"{r['town']} ({r['county']} County)"


def cmd_targets(args) -> None:
    st = args.state.upper()
    raw = load(SOURCES / "wikipedia_township_lists.json")   # from the two Wikipedia list pages (saved copies)
    census = {r["town"]: r for r in load(SOURCES / "county_census_rows.json", []) if r["state"] == st}
    sites = _sites()
    rows: list[dict] = []
    if st == "MI":
        existing = {r["town"]: r for r in load(DATA / "towns_mi.json")["towns"]}
        for t in raw["MI"]:
            if t["county"] not in SE_MI:
                continue
            name = f"{t['name']} Charter Township" if t["type"] == "Charter township" else f"{t['name']} Township"
            squeeze = lambda n: re.sub(r"\s+|\bcharter\b", "", n.lower())   # "La Salle" is the existing "LaSalle" row
            if any(squeeze(name) == squeeze(e) for e in existing):
                continue   # already a test row (fight / mta_sample / county_list), kept as it is
            site = sites.get(f"MI:{t['county']}:{name}") or {}
            rows.append({"town": name, "state": "MI", "county": t["county"], "kind": "township",
                         "website": site.get("website"), "website_source": site.get("source"),
                         "no_website_note": None if site.get("website") else site.get("note") or "no township website found",
                         "pop_2020": int(t["pop_2020"].replace(",", "")) if t.get("pop_2020", "").replace(",", "").isdigit() else None,
                         "selection_group": "se_michigan",
                         "selection_reason": f"southeast Michigan township, {t['county']} County (data-center and solar fights; "
                                             "county route MCL 125.3307)",
                         "selection_source": SELECTION_SOURCE, "selection_source_url": t.get("wp")})
        _dedupe_names(rows, set(existing))
        for c in SE_MI:
            if f"{c} County" in existing:
                continue
            cen = census.get(f"{c} County", {})
            site = sites.get(f"MI:{c}:{c} County") or {}
            rows.append({"town": f"{c} County", "state": "MI", "county": c, "kind": "county",
                         "website": site.get("website") or cen.get("website"),
                         "website_source": site.get("source") or ("county site (coverage_county_census.csv, wikidata P856)"
                                                                  if cen else None),
                         "selection_group": "county_planning", "selection_reason": COUNTY_ROUTE["MI"],
                         "selection_source": SELECTION_SOURCE})
    else:
        for t in raw["OH"]:
            if t["county"] not in OH8 or t.get("defunct", "").strip():
                continue
            name = f"{t['name']} Township"
            site = sites.get(f"OH:{t['county']}:{name}") or {}
            rows.append({"town": name, "state": "OH", "county": t["county"], "kind": "township",
                         "website": site.get("website"), "website_source": site.get("source"),
                         "no_website_note": None if site.get("website") else site.get("note") or "no township website found",
                         "selection_group": "central_ohio" if t["county"] not in ("Clermont", "Butler") else "cincinnati_exurbs",
                         "selection_reason": f"{t['county']} County township (138 Ohio data-center moratoria by Sept 2026, "
                                             "SB 52 county solar votes; county route ORC 519.12)",
                         "selection_source": SELECTION_SOURCE, "selection_source_url": t.get("wp")})
        _dedupe_names(rows, set())
        for c in OH88:
            cen = census.get(f"{c} County", {})
            site = sites.get(f"OH:{c}:{c} County") or {}
            rows.append({"town": f"{c} County", "state": "OH", "county": c, "kind": "county",
                         "website": site.get("website") or cen.get("website"),
                         "website_source": site.get("source") or ("county site (coverage_county_census.csv, wikidata P856)"
                                                                  if cen else "hand (Adams County is missing from the census)"),
                         "selection_group": "county_planning", "selection_reason": COUNTY_ROUTE["OH"],
                         "selection_source": SELECTION_SOURCE})
        rows.append({"town": "Logan-Union-Champaign Regional Planning Commission", "state": "OH", "county": "Logan",
                     "covers_counties": ["Logan", "Union", "Champaign"], "kind": "county",
                     "website": "https://www.lucplanning.com/",
                     "website_source": "research_notes/Expansion/cheap_township_coverage.md (sampled body)",
                     "selection_group": "regional_planning", "selection_reason": COUNTY_ROUTE["OH"],
                     "selection_source": SELECTION_SOURCE})
        for r in rows:
            if r["town"] == "Delaware County":
                r["website"] = "https://regionalplanning.co.delaware.oh.us/"
                r["website_source"] = "research_notes/Expansion/cheap_township_coverage.md (sampled body: DCRPC monthly mailing)"
    save(TEST / f"targets_{st.lower()}.json", rows)
    c = Counter(r["kind"] for r in rows)
    print(f"{st}: {len(rows)} targets {dict(c)}; with a website: {sum(1 for r in rows if r.get('website'))}")
    for county in sorted({r["county"] for r in rows if r["kind"] == "township"}):
        tw = [r for r in rows if r["kind"] == "township" and r["county"] == county]
        print(f"  {county:<12} townships {len(tw):>2}, with site {sum(1 for r in tw if r.get('website')):>2}")


# ------------------------------------------------------------------ discover
ABOUT = {
    "MI": ("Agenda Ahead Michigan test rows: the 2026-10 test places (southern Michigan and the Thumb) plus, from "
           "2026-11, every township in the twelve southeast Michigan counties (Washtenaw, Livingston, Oakland, Macomb, "
           "Monroe, Lenawee, Jackson, Genesee, Lapeer, St. Clair, Shiawassee, Ingham) and their county planning "
           "commissions (the MCL 125.3307 route). Same row shape as towns_ma_all.json plus state, kind, county, "
           "selection_group / selection_reason / selection_source, coverage fields. Built by "
           "`python3 experiments/mi_va_test.py discover --state MI` (2026-10) and "
           "`python3 experiments/great_lakes_test.py discover --state MI` (2026-11)."),
    "OH": ("Agenda Ahead Ohio test rows (2026-11): every township in Licking, Union, Franklin, Delaware, Logan, "
           "Champaign, Clermont and Butler counties, Ohio's 88 county planning commissions and the regional planning "
           "commissions that review township zoning under ORC 519.12. Same row shape as towns_mi.json. Built by "
           "`python3 experiments/great_lakes_test.py discover --state OH`."),
}
MAPPING = {
    "MI": {"Township Board / Board of Trustees, City Council / Commission": "select_board",
           "Planning Commission (township, city, county)": "planning_board",
           "Zoning Board of Appeals": "zoning_board_of_appeals"},
    "OH": {"Board of Trustees (township), City / Village Council, County Commissioners": "select_board",
           "Zoning Commission (township), Planning Commission / Regional Planning Commission (county)": "planning_board",
           "Board of Zoning Appeals": "zoning_board_of_appeals"},
}
GATE_NOTE = ("Test state: not part of the production daily run. Crawled only by `python3 -m watch351.daily --states MI,OH "
             "--output-dir ../data/test/great_lakes --hits-name hits_great_lakes.json` (Michigan also by the 2026-10 "
             "test command with --states MI,VA --output-dir ../data/test).")


def annotate_coverage(rows: list[dict]) -> None:
    """Township rows: `coverage` (direct / via_county / none), `coverage_county_body` and, for via_county,
    `coverage_note`, from attribution.coverage_modes (regional bodies cover several counties)."""
    from watch351.attribution import coverage_modes
    modes = coverage_modes(rows)
    for r in rows:
        if r["town"] in modes:
            r.update(modes[r["town"]])


def cmd_discover(args) -> None:
    st = args.state.upper()
    targets = load(TEST / f"targets_{st.lower()}.json")
    towns_file = DATA / f"towns_{st.lower()}.json"
    doc = load(towns_file) or {"towns": []}
    prev = {t["town"]: t for t in doc["towns"]}
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    todo = [t for t in targets if wanted is None or t["town"].lower() in wanted]
    if wanted:   # an existing row named with --places (e.g. a 2026-10 county row) is re-discovered from its own fields
        keep = {"town", "state", "county", "kind", "website", "website_source", "pop_2020", "selection_group",
                "selection_reason", "selection_source", "selection_source_url", "no_website_note", "covers_counties"}
        todo += [{k: v for k, v in prev[n].items() if k in keep} for n in prev
                 if n.lower() in wanted and n not in {t["town"] for t in todo}]
    if args.only_new:
        todo = [t for t in todo if t["town"] not in prev or not prev[t["town"]].get("discovered_at")]
    fetcher = PoliteFetcher()
    t0 = time.monotonic()

    def one(t):
        try:
            return discover_place(fetcher, t, st, tracked_for(t))
        except Exception as e:  # noqa: BLE001 - one site must not stop the census
            logging.exception("discovery crashed for %s", t["town"])
            return {**t, "status": "not_automated", "reason_code": "discovery_error", "automated": False,
                    "reason": f"{type(e).__name__}: {str(e)[:160]}", "listings": []}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one, todo))
    posted = []
    for r in results:
        posted += [dict(p, town=r["town"]) for p in r.pop("_posted_rows", [])]
        if r.get("kind") == "county":
            r["attribute_townships"] = True   # county-body items name townships: file hits under the township
            # every township of these counties is a row, so an unresolved township name is a parsing error
            # ("Jack Reynolds Township" from a clerk's name), not a township we do not monitor
            r["attribute_known_only"] = True
        cur = CURATED.get(st, {}).get(r["town"])
        if cur:
            cur = dict(cur)
            extra = cur.pop("add_listings", [])
            r.update(cur)
            if extra and r.get("automated"):
                have = {(l["board_key"], l["url"]) for l in r.get("listings") or []}
                r["listings"] = (r.get("listings") or []) + [l for l in extra if (l["board_key"], l["url"]) not in have]
            r["curated"] = True
        prev[r["town"]] = r
    # order: existing rows first (unchanged order), then the new targets in target order
    order = [t["town"] for t in doc["towns"]] + [t["town"] for t in targets if t["town"] not in {x["town"] for x in doc["towns"]}]
    rows = [prev[n] for n in order if n in prev]
    annotate_coverage(rows)
    out = {
        "_about": ABOUT[st], "generated": now_iso(), "state": st, "gated": True, "gate_note": GATE_NOTE,
        "boards_tracked": ALL3, "board_key_mapping": MAPPING[st],
        "evidence_rule": "a board is automated only if its listing shows >=1 agenda/packet/notice dated within "
                         "[today-120d, today+120d] and the first such document is fetchable under robots.txt",
        "count": len(rows), "automated": sum(1 for r in rows if r.get("automated")), "towns": rows,
    }
    save(towns_file, out)
    pp = TEST / f"posted_stamps_{st.lower()}.json"
    old = load(pp, [])
    keep = [p for p in old if p["town"] not in {r["town"] for r in results}]
    save(pp, keep + posted)
    print(f"{st}: {len(results)} discovered in {time.monotonic() - t0:.0f}s; fetcher {fetcher.stats}; "
          f"file now {len(rows)} rows, {out['automated']} automated")
    for r in results:
        print(f"  {r['town']:<44} {str(r.get('platform') or '-'):<18} {len(r.get('listings') or []):>2} "
              f"{'AUTO' if r.get('automated') else r.get('reason_code')}: "
              f"{'' if r.get('automated') else (r.get('reason') or '')[:100]}")


def cmd_annotate(args) -> None:
    st = args.state.upper()
    path = DATA / f"towns_{st.lower()}.json"
    doc = load(path)
    annotate_coverage(doc["towns"])
    doc["automated"] = sum(1 for r in doc["towns"] if r.get("automated"))
    doc["count"] = len(doc["towns"])
    save(path, doc)
    c = Counter(r.get("coverage") for r in doc["towns"] if r.get("kind") == "township")
    print(st, "township coverage:", dict(c))


# ------------------------------------------------------------------ crawl
def cmd_crawl(args) -> None:
    out = Path(args.test_dir) if args.test_dir else TEST
    cmd = [sys.executable, "-m", "watch351.daily", "--states", "MI,OH", "--output-dir", str(out),
           "--hits-name", HITS_NAME, "--days-back", str(args.days_back), "--days-ahead", str(args.days_ahead),
           "--workers", str(args.workers), "--request-log", str(out / f"requests_{args.label}.tsv")]
    if args.cache_dir:
        cmd += ["--cache-dir", args.cache_dir]
    print(" ".join(cmd))
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=CRAWLER)
    print(f"exit {proc.returncode}, wall {time.monotonic() - t0:.0f}s")
    runs = out / "state" / "runs"
    latest = max(runs.glob("*.json"), key=lambda p: p.stat().st_mtime)
    rep = json.loads(latest.read_text())
    snap = out / "runs" / f"run_{args.label}.json"
    save(snap, rep)
    print(f"saved {snap}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["targets", "discover", "annotate", "crawl", "analyze", "sample"])
    p.add_argument("--state", default="MI")
    p.add_argument("--places")
    p.add_argument("--only-new", action="store_true", help="discover: skip rows already discovered")
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=120)
    p.add_argument("--label", default="run1")
    p.add_argument("--per-state", type=int, default=30)
    p.add_argument("--exclude", help="sample: skip hits judged in this worksheet / precision_judgments.json")
    p.add_argument("--test-dir", help="crawl / sample / analyze: output directory (default data/test/great_lakes)")
    p.add_argument("--random", type=int, help="sample: simple random sample with this seed")
    p.add_argument("--base-run", default="run1", help="analyze: run label that fixes the crawl day and window")
    p.add_argument("--worksheet", help="sample: output file name under the test dir (default precision_worksheet.json)")
    p.add_argument("--cache-dir", help="crawl: fetch cache to use (default crawler/.cache)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    if args.command == "targets":
        cmd_targets(args)
    elif args.command == "discover":
        cmd_discover(args)
    elif args.command == "annotate":
        cmd_annotate(args)
    elif args.command == "crawl":
        cmd_crawl(args)
    elif args.command in ("analyze", "sample"):
        import great_lakes_analysis as GA  # noqa: E402
        if args.test_dir:
            GA.TEST = Path(args.test_dir)
        (GA.analyze if args.command == "analyze" else GA.sample)(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
