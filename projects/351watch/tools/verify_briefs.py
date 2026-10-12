#!/usr/bin/env python3
"""Check every written brief against its agenda's text and record the result.

    python3 tools/verify_briefs.py              checks data/briefs/*/*.jsonl and writes `verified` back
    python3 tools/verify_briefs.py --check      reports only; writes nothing
    python3 tools/verify_briefs.py FILE...      only these files
    python3 tools/verify_briefs.py --data DIR   another data directory (tests)

For each brief: every proper noun, number, address fragment and the `who` value must appear in the
document's text in data/search; `quote` must appear verbatim; `action` must have its cue near the
quote; `can_speak: true` needs "public hearing" or "public comment" nearby; dates in `history` must be
meeting dates we hold for the town. Failures print with the reason. `verified` is set to true only when
every check passes, and to false otherwise, in place (the only field this tool changes). Only the
latest row for each id is checked; earlier rows for the same id are left as they are. Exit status is 1
when any brief fails. build.py renders only briefs marked verified, and checks them again.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
import briefs as B  # noqa: E402


def hits_by_id(data_dir):
    """{id: hit} from hits_current.json and the archive, for a brief's document and town."""
    out = {}
    path = os.path.join(data_dir, "hits_current.json")
    try:
        with open(path, encoding="utf-8") as f:
            for h in json.load(f).get("hits", []):
                out[h["id"]] = h
    except (OSError, ValueError):
        pass
    for p in sorted(B.glob.glob(os.path.join(data_dir, "state", "hits_archive", "*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    h = json.loads(line)
                except ValueError:
                    continue
                if h.get("id"):
                    out.setdefault(h["id"], h)
    return out


def town_dates(hits):
    out = {}
    for h in hits.values():
        if h.get("meeting_date"):
            out.setdefault(f"{h.get('state', 'MA')}:{h.get('town')}", set()).add(h["meeting_date"][:10])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--data", default=os.path.join(PROJECT, "data"))
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    ap.add_argument("--quiet", action="store_true", help="print failures only")
    args = ap.parse_args(argv)
    files = args.files or B.brief_files(args.data)
    hits = hits_by_id(args.data)
    dates = town_dates(hits)
    rows_by_file = {path: B.read_rows(path) for path in files}
    # Files are append-only: only the latest row for each id is checked; older rows are left as they are.
    latest = {}
    for path, rows in rows_by_file.items():
        for n, row in rows:
            prev = latest.get(row["id"])
            if prev is None or (row.get("written_at") or "") >= (prev[2].get("written_at") or ""):
                latest[row["id"]] = (path, n, row)
    current = {(path, n) for path, n, _ in latest.values()}
    urls = set()
    for _, _, row in latest.values():
        urls.add(row.get("source_url") or (hits.get(row["id"]) or {}).get("source_url"))
    texts = B.doc_texts(args.data, urls)
    failed = passed = superseded = 0
    for path, rows in rows_by_file.items():
        changed = False
        out = []
        for n, row in rows:
            if (path, n) not in current:
                superseded += 1
                out.append(row)
                continue
            hit = hits.get(row["id"]) or {}
            url = row.get("source_url") or hit.get("source_url")
            reasons = []
            if not hit:
                reasons.append("no hit with this id in hits_current.json or the archive")
            elif row.get("source_url") and hit.get("source_url") and row["source_url"] != hit["source_url"]:
                reasons.append("source_url is not the hit's document")
            town = f"{hit.get('state', 'MA')}:{hit.get('town')}" if hit else None
            reasons += B.verify(row, texts.get(url, ""), dates.get(town, set()) if town else None)
            ok = not reasons
            label = f"{row['id']} {hit.get('town', '?')} {hit.get('board', '')} {hit.get('meeting_date') or 'undated'}".strip()
            if ok:
                passed += 1
                if not args.quiet:
                    print(f"ok   {label}")
            else:
                failed += 1
                print(f"FAIL {label}: " + "; ".join(reasons))
            if row.get("verified") is not ok:
                row["verified"] = ok
                changed = True
            out.append(row)
        if changed and not args.check:
            B.write_rows(path, out)
    print(f"{passed} verified, {failed} failed, {superseded} superseded by a later row, {len(files)} file(s)"
          + (" (nothing written)" if args.check else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
