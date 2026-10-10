#!/usr/bin/env python3
"""351 Watch prototype crawler.

    python3 run.py discover            # (re)build data/towns.json listings
    python3 run.py crawl               # fetch agendas, write data/agenda_hits.json
    python3 run.py crawl --towns Amherst,Sutton --days-back 45 --days-ahead 90
    python3 run.py crawl --offline     # re-run matching from the cache only
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from watch351.crawl import run_crawl
from watch351.discover import discover_town
from watch351.fetch import PoliteFetcher

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data"
TOWNS_FILE = DATA / "towns.json"
HITS_FILE = DATA / "agenda_hits.json"


def load_towns() -> dict:
    return json.loads(TOWNS_FILE.read_text())


def save_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def select(towns: list[dict], names: str | None) -> list[dict]:
    if not names:
        return towns
    wanted = {n.strip().lower() for n in names.split(",")}
    return [t for t in towns if t["town"].lower() in wanted]


def cmd_discover(args, fetcher: PoliteFetcher) -> None:
    doc = load_towns()
    chosen = {t["town"] for t in select(doc["towns"], args.towns)}
    todo = [t for t in doc["towns"] if t["town"] in chosen]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        updated = {c["town"]: c for c in pool.map(lambda c: discover_town(fetcher, c), todo)}
    doc["towns"] = [updated.get(t["town"], t) for t in doc["towns"]]
    save_json(TOWNS_FILE, doc)
    for t in doc["towns"]:
        if t["town"] in chosen:
            status = "automated" if t.get("automated") else f"NOT automated: {t.get('reason')}"
            print(f"{t['town']:<18} {t.get('platform') or '-':<11} "
                  f"{len(t.get('listings', [])):>2} listings  {status}")


def cmd_crawl(args, fetcher: PoliteFetcher) -> None:
    towns = select(load_towns()["towns"], args.towns)
    report = run_crawl(towns, fetcher, days_back=args.days_back,
                       days_ahead=args.days_ahead, workers=args.workers)
    save_json(Path(args.out), report)
    print(f"towns attempted {report['towns_attempted']}, automated {report['towns_automated']}, "
          f"documents scanned {report['documents_scanned']} "
          f"({report['documents_without_text_layer']} without text layer, "
          f"{report['documents_ocr']} recovered by OCR), hits {len(report['hits'])}")
    for topic, n in report["hits_by_topic"].items():
        print(f"  {topic:<26} {n}")
    print(f"fetcher: {fetcher.stats}")
    print(f"wrote {args.out}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["discover", "crawl"])
    p.add_argument("--towns", help="comma-separated subset of towns")
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=90)
    p.add_argument("--workers", type=int, default=8, help="towns crawled in parallel (each host stays at <=1 req/s)")
    p.add_argument("--offline", action="store_true", help="serve only from crawler/.cache")
    p.add_argument("--out", default=str(HITS_FILE))
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    fetcher = PoliteFetcher(offline=args.offline)
    {"discover": cmd_discover, "crawl": cmd_crawl}[args.command](args, fetcher)
    return 0


if __name__ == "__main__":
    sys.exit(main())
