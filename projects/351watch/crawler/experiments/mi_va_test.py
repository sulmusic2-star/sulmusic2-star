#!/usr/bin/env python3
"""351 Watch test in two new areas (2026-10): southern Michigan townships + the Thumb, and
Virginia's Southside and Piedmont counties.

    cd projects/351watch/crawler
    python3 experiments/mi_va_test.py discover --state MI      # data/test/targets_mi.json -> data/towns_mi.json
    python3 experiments/mi_va_test.py discover --state VA [--places "Halifax County,Town of Culpeper"]
    python3 experiments/mi_va_test.py crawl                    # watch351.daily --states MI,VA -> data/test/
    python3 experiments/mi_va_test.py analyze                  # coverage, output, freshness, reliability
    python3 experiments/mi_va_test.py sample --per-state 45    # precision worksheet (hit + source context)

data/towns_mi.json and data/towns_va.json are marked "gated": the production daily run
(ops/daily.sh -> watch351.daily without --states) never reads them; watch351.daily crawls
them only with --states MI,VA and an --output-dir other than data/ (here data/test/), so
data/hits_current.json and data/state/ are never touched.

All network access goes through watch351.fetch.PoliteFetcher (351WatchBot UA, robots.txt on
every hop, <= 1 request/second/host, crawl-delay honored up to the 10 s cap, no logins, no
POSTs, no challenge solving).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAWLER = HERE.parent
sys.path.insert(0, str(CRAWLER))
sys.path.insert(0, str(HERE))   # mi_va_analysis, also under python3 -I

from watch351.discover_sites import discover_place  # noqa: E402
from watch351.fetch import PoliteFetcher  # noqa: E402

DATA = CRAWLER.parent / "data"
TEST = DATA / "test"
HITS_NAME = "hits_mi_va.json"
STATES = {"MI": "Michigan", "VA": "Virginia"}
ALL3 = ["select_board", "planning_board", "zoning_board_of_appeals"]

# Hand corrections after reading the sites (each says why). Applied on top of discovery.
CURATED: dict[str, dict] = {
    # Huron County administers zoning for most of its townships; its Building & Zoning office posts
    # Planning Commission hearing notices (special approval uses, zoning amendments) on the county
    # homepage as undated PDF links ("SAP 2026-03 Ranger Power Pinesap Solar Public Hearing Notice").
    # The meeting date is read from each notice itself (date_from_document).
    "Huron County": {
        "automated": True, "status": "automated", "reason_code": None, "reason": None,
        "platform": "agenda_page", "platforms": ["agenda_page"],
        "listings": [{"board": "Huron County Planning Commission", "board_key": "planning_board",
                      "platform": "agenda_page", "url": "https://www.co.huron.mi.us/",
                      "board_pattern": r"\bSAP\b|special\s+approval|\bZA\s*20|zoning|planning|public\s+hearing",
                      "date_from_document": True}],
        "curation_note": "hearing notices on the county homepage, dated from the notice text",
    },
    # Livingston County Planning Commission agendas and packets are on the Planning department's
    # commission page (milivcounty.gov/planning/commission/), linked only from /planning/, not from the
    # homepage or the meetings calendar that discovery reads; its eSCRIBE portal carries only the Board
    # of Commissioners and committees.
    "Livingston County": {
        "automated": True, "status": "automated", "reason_code": None, "reason": None,
        "platform": "agenda_page", "platforms": ["agenda_page"],
        "listings": [{"board": "Livingston County Planning Commission", "board_key": "planning_board",
                      "platform": "agenda_page", "url": "https://milivcounty.gov/planning/commission/"}],
        "curation_note": "Planning Commission page under the Planning department (2026 agendas and packets)",
    },
    # Virginia counties where discovery found only the Board of Supervisors (fix round, 2026-10-12).
    # Southampton's Planning Commission posts one page per meeting (staff reports, draft ordinances)
    # under a page per year; its links are relative to <base href>, which discovery's hub search
    # did not reach through the "archived" agendas page.
    "Southampton County": {
        "add_listings": [{"board": "Planning Commission", "board_key": "planning_board", "platform": "agenda_page",
                          "url": "https://www.southamptoncounty.org/departments/planning/year_{year}.php"}],
        "curation_note": "Planning Commission meeting pages (year_{year}.php), added by hand",
    },
    # Prince Edward's Planning Commission packets are on a Community Development page that discovery's
    # hub search did not reach.
    "Prince Edward County": {
        "add_listings": [{"board": "Planning Commission", "board_key": "planning_board", "platform": "agenda_page",
                          "url": "https://www.co.prince-edward.va.us/Departments/Community-Development/"
                                 "Planning-Zoning/Planning-Commission-Meetings"}],
        "curation_note": "Planning Commission packets page, added by hand",
    },
}


def tracked_for(row: dict) -> list[str]:
    if row["state"] == "MI" and row.get("kind") == "county":
        return ["planning_board"]   # county planning commissions only (MZEA township-amendment review)
    return list(ALL3)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


ABOUT = {
    "MI": ("351 Watch Michigan test (2026-10): {n} townships, cities and county planning commissions in "
           "southern Michigan and the Thumb (energy_siting_hotspots.md areas 1 and 4). Same row shape as "
           "towns_ma_all.json plus state, kind, selection_group / selection_reason / selection_source. "
           "Built by `python3 experiments/mi_va_test.py discover --state MI`."),
    "VA": ("351 Watch Virginia test (2026-10): {n} Southside and Piedmont counties (Board of Supervisors, "
           "Planning Commission, BZA) plus key towns (energy_siting_hotspots.md areas 2 and 9). Same row shape "
           "as towns_ma_all.json plus state, kind, selection_group / selection_reason / selection_source. "
           "Built by `python3 experiments/mi_va_test.py discover --state VA`."),
}
MAPPING = {
    "MI": {"Township Board / Board of Trustees, City Council / Commission": "select_board",
           "Planning Commission (township, city, county)": "planning_board",
           "Zoning Board of Appeals": "zoning_board_of_appeals"},
    "VA": {"Board of Supervisors, Town / City Council": "select_board", "Planning Commission": "planning_board",
           "Board of Zoning Appeals (BZA)": "zoning_board_of_appeals"},
}


# ------------------------------------------------------------------ discover
def cmd_discover(args) -> None:
    st = args.state.upper()
    targets = json.loads((TEST / f"targets_{st.lower()}.json").read_text())
    towns_file = DATA / f"towns_{st.lower()}.json"
    prev = {t["town"]: t for t in json.loads(towns_file.read_text())["towns"]} if towns_file.exists() else {}
    wanted = {p.strip().lower() for p in args.places.split(",")} if args.places else None
    todo = [t for t in targets if wanted is None or t["town"].lower() in wanted]
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
        if st == "MI" and r.get("kind") == "county":
            # county planning commission items name townships: file their hits under the township
            r["attribute_townships"] = True
        cur = CURATED.get(r["town"])
        if cur:
            cur = dict(cur)
            extra = cur.pop("add_listings", [])
            r.update(cur)
            if extra and r.get("automated"):   # add boards discovery missed; keep what it found
                have = {(l["board_key"], l["url"]) for l in r.get("listings") or []}
                r["listings"] = (r.get("listings") or []) + [l for l in extra if (l["board_key"], l["url"]) not in have]
            r["curated"] = True
        prev[r["town"]] = r
    order = [t["town"] for t in targets]
    rows = [prev[n] for n in order if n in prev]
    annotate_coverage(st, rows)
    doc = {
        "_about": ABOUT[st].format(n=len(rows)),
        "generated": now_iso(), "state": st, "gated": True,
        "gate_note": "Test state: not part of the production daily run. Crawled only by "
                     "`python3 -m watch351.daily --states MI,VA --output-dir ../data/test --hits-name hits_mi_va.json`.",
        "boards_tracked": ALL3, "board_key_mapping": MAPPING[st],
        "evidence_rule": "a board is automated only if its listing shows >=1 agenda/packet/notice dated within "
                         "[today-120d, today+120d] and the first such document is fetchable under robots.txt",
        "count": len(rows), "automated": sum(1 for r in rows if r.get("automated")), "towns": rows,
    }
    save(towns_file, doc)
    pp = TEST / f"posted_stamps_{st.lower()}.json"
    old = json.loads(pp.read_text()) if pp.exists() else []
    keep = [p for p in old if p["town"] not in {r["town"] for r in results}]
    save(pp, keep + posted)
    print(f"{st}: {len(results)} discovered in {time.monotonic() - t0:.0f}s; fetcher {fetcher.stats}")
    for r in results:
        print(f"  {r['town']:<34} {str(r.get('platform') or '-'):<18} {len(r.get('listings') or []):>2} "
              f"{'AUTO' if r.get('automated') else r.get('reason_code')}: "
              f"{'' if r.get('automated') else (r.get('reason') or '')[:110]}")


def annotate_coverage(st: str, rows: list[dict]) -> None:
    """Michigan townships: `coverage` (direct / via_county / none), `coverage_county_body` and, for
    via_county, `coverage_note` (the line a township page shows), from attribution.coverage_modes."""
    if st != "MI":
        return
    from watch351.attribution import coverage_modes
    modes = coverage_modes(rows)
    for r in rows:
        if r["town"] in modes:
            r.update(modes[r["town"]])


def cmd_annotate(args) -> None:
    """Re-derive the coverage fields in data/towns_mi.json without any discovery request."""
    st = args.state.upper()
    path = DATA / f"towns_{st.lower()}.json"
    doc = json.loads(path.read_text())
    annotate_coverage(st, doc["towns"])
    save(path, doc)
    c = Counter(r.get("coverage") for r in doc["towns"] if r.get("kind") == "township")
    print(st, "township coverage:", dict(c))


# ------------------------------------------------------------------ crawl
def cmd_crawl(args) -> None:
    out = Path(args.test_dir) if args.test_dir else TEST   # e.g. data/test/extended for a wider window
    cmd = [sys.executable, "-m", "watch351.daily", "--states", "MI,VA", "--output-dir", str(out),
           "--hits-name", HITS_NAME, "--days-back", str(args.days_back), "--days-ahead", str(args.days_ahead),
           "--workers", str(args.workers), "--request-log", str(out / f"requests_{args.label}.tsv")]
    if args.cache_dir:
        cmd += ["--cache-dir", args.cache_dir]   # e.g. an empty dir: a fresh container with only data/test/state
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
    p.add_argument("command", choices=["discover", "annotate", "crawl", "analyze", "sample", "rss"])
    p.add_argument("--state", default="MI")
    p.add_argument("--places")
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=120)
    p.add_argument("--label", default="run1")
    p.add_argument("--per-state", type=int, default=45)
    p.add_argument("--exclude", help="sample: skip hits judged in this worksheet / precision_judgments.json")
    p.add_argument("--test-dir", help="crawl / sample / analyze: output directory (default data/test)")
    p.add_argument("--random", type=int, help="sample: simple random sample with this seed (default: round-robin "
                                              "over towns)")
    p.add_argument("--base-run", default="run1", help="analyze: run label that fixes the crawl day and window")
    p.add_argument("--exclude-docs-from", help="sample: skip hits from the documents in this JSON list of URLs")
    p.add_argument("--worksheet", help="sample: output file name under data/test/ (default precision_worksheet.json)")
    p.add_argument("--cache-dir", help="crawl: fetch cache to use (default crawler/.cache)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    if args.command == "discover":
        cmd_discover(args)
    elif args.command == "annotate":
        cmd_annotate(args)
    elif args.command == "crawl":
        cmd_crawl(args)
    elif args.command == "analyze":
        import mi_va_analysis  # noqa: E402
        if args.test_dir:
            mi_va_analysis.TEST = Path(args.test_dir)
        mi_va_analysis.analyze(args)
    elif args.command == "rss":
        from mi_va_analysis import rss  # noqa: E402
        rss(args)
    elif args.command == "sample":
        import mi_va_analysis  # noqa: E402
        if args.test_dir:
            mi_va_analysis.TEST = Path(args.test_dir)
        mi_va_analysis.sample(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
