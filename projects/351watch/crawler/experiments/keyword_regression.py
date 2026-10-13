#!/usr/bin/env python3
"""Keyword-change regression check on cached documents (no network).

    git show af1e10d:projects/351watch/crawler/watch351/keywords.py > /tmp/keywords_old.py
    python3 experiments/keyword_regression.py --old /tmp/keywords_old.py --cache-dir PATH/.cache \
        --out ../data/test/keyword_regression.json

For every document in the incremental index (data/state/docs/<ST>/*.jsonl: MA, NY, RI) whose
body is in the fetch cache, extract the text once (pdftotext; OCR text only if already cached,
never re-run) and match it with

* the old matcher (keywords.py before the MI/VA change),
* the new matcher exactly as production calls it (find_hits(text, state=<doc state>)),
* the new matcher with Michigan's / Virginia's extra patterns turned on (informational: what
  those patterns, incl. wind, would add if they were ever enabled for Massachusetts).

Reports hit counts by state and topic for each, and every document whose hits differ.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

CRAWLER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CRAWLER))

from watch351 import extract as X  # noqa: E402
from watch351 import keywords as NEW  # noqa: E402
from watch351.fetch import FetchError, PoliteFetcher  # noqa: E402

DATA = CRAWLER.parent / "data"


def load_old(path: Path):
    spec = importlib.util.spec_from_file_location("keywords_old", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["keywords_old"] = mod   # dataclasses look the module up while it executes
    spec.loader.exec_module(mod)
    return mod


def sig(hits) -> list[tuple]:
    return [(tuple(h.topics), h.snippet) for h in hits]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--old", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--states", default="MA,NY,RI")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    old = load_old(a.old)
    fetcher = PoliteFetcher(a.cache_dir, offline=True)   # read-only: offline mode never writes the cache
    ocr_dir = a.cache_dir / "ocr"

    def ocr_cached_only(data: bytes) -> str:
        import hashlib
        f = ocr_dir / f"{hashlib.sha256(data).hexdigest()[:32]}.txt"
        return f.read_text() if f.exists() else ""
    X.ocr_pdf = ocr_cached_only

    recs = []
    for st in a.states.split(","):
        for path in sorted((DATA / "state" / "docs" / st).glob("*.jsonl")):
            recs += [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    counts = {k: Counter() for k in ("old", "new", "new_mi", "new_va")}
    docs = Counter()
    diffs, extra_examples = [], []
    for rec in recs:
        if rec.get("status") != "ok":
            docs["skipped_not_ok"] += 1
            continue
        url = rec.get("source_url") or rec["url"]
        try:
            resp = fetcher.get(url)
        except FetchError:
            docs["not_cached"] += 1
            continue
        if not resp.ok:
            docs["cached_error_status"] += 1
            continue
        ex = X.extract(resp)
        docs["matched"] += 1
        docs[f"text_{'ocr' if ex.ocr else ex.kind}"] += 1
        st = rec["state"]
        o = sig(old.find_hits(ex.text))
        n = sig(NEW.find_hits(ex.text, state=st))
        mi = sig(NEW.find_hits(ex.text, state="MI"))
        va = sig(NEW.find_hits(ex.text, state="VA"))
        for name, hs in (("old", o), ("new", n), ("new_mi", mi), ("new_va", va)):
            counts[name][f"{st}:hits"] += len(hs)
            for topics, _ in hs:
                for t in topics:
                    counts[name][f"{st}:{t}"] += 1
        if o != n:
            diffs.append({"url": url, "state": st, "old": o, "new": n})
        if st == "MA" and mi != o and len(extra_examples) < 40:
            added = [h for h in mi if h not in o]
            if added:
                extra_examples.append({"url": url, "added_with_MI_patterns": added[:3]})
    report = {
        "documents": dict(docs), "records": len(recs),
        "hit_counts": {k: dict(sorted(v.items())) for k, v in counts.items()},
        "documents_with_changed_hits": len(diffs), "diffs": diffs[:50],
        "ma_examples_if_mi_patterns_were_enabled": extra_examples,
    }
    a.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in ("documents", "records", "documents_with_changed_hits")}, indent=1))
    for k in ("old", "new", "new_mi", "new_va"):
        print(k, {s: report["hit_counts"][k].get(f"{s}:hits") for s in a.states.split(",")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
