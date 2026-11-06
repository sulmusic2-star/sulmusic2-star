#!/usr/bin/env python3
"""Run the official notice and docket feeds (ny_enb, ny_ores, oh_opsb, md_psc_cpcn), count what they yield and
draw the hand-check samples. Everything is written under data/test/notices/.

    cd projects/351watch/crawler
    python3 experiments/notices_test.py run [--days 30] [--sources ny_enb,oh_opsb] [--offline]
    python3 experiments/notices_test.py stats          # items a week, hits on places we cannot read today
    python3 experiments/notices_test.py sample [--n 30] # precision_worksheet.json for the hand judgment
"""
from __future__ import annotations

import argparse
import collections
import importlib
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from watch351.fetch import DEFAULT_CACHE_DIR, PoliteFetcher  # noqa: E402
from watch351.sources.notice_feeds import DATA, DEFAULT_OUT  # noqa: E402

SOURCES = ("ny_enb", "ny_ores", "oh_opsb", "md_psc_cpcn")


def load(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def town_rows() -> dict[str, dict]:
    """'ST:Town' -> production row (gated files skipped: they are not places on the site)."""
    out = {}
    for p in sorted(DATA.glob("towns_*.json")):
        doc = load(p) or {}
        if doc.get("gated"):
            continue
        for r in doc.get("towns", []):
            out[f"{r.get('state', 'MA')}:{r['town']}"] = r
    return out


def cmd_run(a) -> int:
    fetcher = PoliteFetcher(a.cache_dir, offline=a.offline)
    for name in a.sources.split(","):
        mod = importlib.import_module(f"watch351.sources.{name}")
        rep = mod.run(fetcher, a.out_dir, a.days)
        print(json.dumps({k: v for k, v in rep.items() if k not in ("errors",)}, indent=1)[:3000])
        if rep.get("errors"):
            print(f"{name}: {len(rep['errors'])} errors, first: {rep['errors'][:5]}")
    return 0


def coverage_bucket(hit: dict, rows: dict[str, dict]) -> str:
    row = rows.get(f"{hit['state']}:{hit['town']}")
    if row is None:
        return "not_on_site"
    return "readable" if row.get("automated") else "not_readable"


def window_of(out_dir: Path, name: str, default_days: int) -> int:
    """Days the latest run of `name` covered (its run report's `since`), else the default."""
    reports = sorted(out_dir.glob(f"runs/{name}_*.json"))
    if reports:
        rep = load(reports[-1]) or {}
        try:
            return (date.fromisoformat(rep["finished"][:10]) - date.fromisoformat(rep["since"])).days or default_days
        except (KeyError, ValueError):
            pass
    return default_days


def cmd_stats(a) -> int:
    rows = town_rows()
    out = {"generated": date.today().isoformat(), "sources": {}}
    for name in SOURCES:
        doc = load(a.out_dir / f"{name}_hits.json")
        items = load(a.out_dir / f"{name}_items.json")
        if not doc:
            continue
        hits = doc["hits"]
        days = window_of(a.out_dir, name, a.days)
        buckets = collections.Counter(coverage_bucket(h, rows) for h in hits)
        dated = collections.Counter(h["date_kind"] for h in hits)
        topics = collections.Counter(t for h in hits for t in h["topics"])
        places = collections.Counter(f"{h['state']}:{h['town']}" for h in hits)
        not_readable = sorted({f"{h['state']}:{h['town']}" for h in hits if coverage_bucket(h, rows) == "not_readable"})
        not_on_site = sorted({f"{h['state']}:{h['town']}" for h in hits if coverage_bucket(h, rows) == "not_on_site"})
        n_items = len(items["items"]) if items else None
        out["sources"][name] = {
            "window_days": days, "items": n_items, "hits": len(hits), "hits_per_week": round(len(hits) * 7 / days, 1),
            "items_per_week": round(n_items * 7 / days, 1) if n_items is not None else None,
            "date_kinds": dict(dated), "topics": dict(topics.most_common()),
            "places": len(places), "coverage": dict(buckets),
            "places_not_readable_today": not_readable, "places_not_on_site": not_on_site[:60],
        }
    (a.out_dir / "stats.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


def cmd_sample(a) -> int:
    rows = town_rows()
    worksheet = {"drawn": date.today().isoformat(), "n_per_source": a.n, "sources": {}}
    for name in SOURCES:
        doc = load(a.out_dir / f"{name}_hits.json")
        if not doc:
            continue
        hits = sorted(doc["hits"], key=lambda h: (h["town"] or "", h["id"]))
        if len(hits) > a.n:
            step = len(hits) / a.n
            hits = [hits[int(i * step)] for i in range(a.n)]
        worksheet["sources"][name] = [{
            "n": i + 1, "id": h["id"], "state": h["state"], "town": h["town"], "county": h.get("county"),
            "coverage": coverage_bucket(h, rows), "meeting_date": h["meeting_date"], "date_kind": h["date_kind"],
            "topics": h["topics"], "headline": h["headline"], "snippet": h["snippet"], "source_url": h["source_url"],
            "verdict": None, "town_right": None, "reason": None,
        } for i, h in enumerate(hits)]
    (a.out_dir / "precision_worksheet.json").write_text(json.dumps(worksheet, indent=1, ensure_ascii=False) + "\n")
    print({k: len(v) for k, v in worksheet["sources"].items()})
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--days", type=int, default=30)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--sources", default=",".join(SOURCES))
    r.add_argument("--offline", action="store_true")
    sub.add_parser("stats")
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=30)
    a = p.parse_args(argv)
    return {"run": cmd_run, "stats": cmd_stats, "sample": cmd_sample}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
