#!/usr/bin/env python3
"""Give Town Meeting warrants in the document index the meeting day their text prints: undated ones, and ones
whose listing date is the day they were posted (earlier than the day the warrant prints).

    python3 tools/date_warrants.py            # update data/state/docs, data/search and hits_current.json
    python3 tools/date_warrants.py --check    # list what would change; write nothing

The daily crawl dates new warrants as it reads them (watch351.dates.warrant_date); this backfills the ones
read before that rule existed. A record moves from undated.jsonl to its meeting month, its search row with it,
and hits_current.json is rebuilt so the warrant's items carry the date.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "crawler"))
from watch351 import current  # noqa: E402
from datetime import date  # noqa: E402
from watch351.dates import warrant_date, warrant_redate  # noqa: E402
from watch351.fulltext import FullText, doc_id  # noqa: E402
from watch351.state import DocIndex  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)
    data = os.path.join(PROJECT, "data")
    index = DocIndex(os.path.join(data, "state", "docs"))
    fulltext = FullText(os.path.join(data, "search"), data)
    texts = {r["id"]: r["text"] for r in fulltext.rows()}
    changed = 0
    for rec in index.records():
        if rec.get("board_key") != "town_meeting" or rec.get("status") != "ok":
            continue
        text = texts.get(doc_id(rec["url"]))
        if rec.get("meeting_date"):
            # a listing date earlier than the day the warrant prints is the day it was posted
            day = warrant_redate(date.fromisoformat(rec["meeting_date"][:10]), text)
        else:
            day = warrant_date(text)
        if not day:
            continue
        changed += 1
        print(f"{rec['state']} {rec['town']}: {rec.get('title') or rec['url']} -> {day.isoformat()}")
        if not args.check:
            rec["meeting_date"] = day.isoformat()
            index.put(rec)
            fulltext.redate(rec)
    print(f"{changed} warrant(s) dated" + (" (nothing written)" if args.check else ""))
    if changed and not args.check:
        index.save()
        fulltext.save()
        doc = current.rebuild(current.Path(data), agenda_hits=index.current_hits(), indexed_urls=index.urls())
        print(f"hits_current.json rebuilt: {len(doc['hits'])} hits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
