"""Draw a random sample of verified briefs with the agenda text they rest on, for an independent reader.

    python3 tools/brief_audit_sample.py OUT.json [--n 60] [--seed 7]

Each sample row carries the brief's fields a reader judges (line, what, where, size, who, action, next,
history, can_speak, how_to_speak, quote) and a window of the agenda text around the quote (about 2,500
characters each side), so the reader sees what the writer saw and can answer "does the agenda say this?".
The writer's own notes (`missing`, `duplicate_of`) are left out so the reader judges the page text only.
"""
import argparse
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import briefs as BR  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
JUDGED = ("line", "what", "where", "size", "who", "action", "next", "history", "can_speak", "how_to_speak", "quote")


def search_text():
    """url -> text for every row in data/search (the newest row per url wins)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(DATA, "search", "*", "*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    if row.get("url") and row.get("text"):
                        out[row["url"]] = row["text"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--window", type=int, default=2500)
    a = ap.parse_args()
    verified = BR.load_briefs(DATA, verified_only=True)
    texts = search_text()
    hits = {h["id"]: h for h in json.load(open(os.path.join(DATA, "hits_current.json"), encoding="utf-8")).get("hits", [])}
    rows = [b for b in verified.values() if b.get("source_url") in texts]
    random.Random(a.seed).shuffle(rows)
    sample = []
    for b in rows[: a.n]:
        text = texts[b["source_url"]]
        norm_text = BR.norm(text)
        pos = BR.find_quote(b.get("quote") or "", norm_text) if b.get("quote") else -1
        # The window is cut from the normalized text so the position lines up with the quote the checker found.
        start = max(0, pos - a.window) if pos >= 0 else 0
        window = norm_text[start: (pos + len(BR.norm(b.get("quote") or "")) + a.window) if pos >= 0 else a.window * 2]
        h = hits.get(b["id"], {})
        sample.append({"id": b["id"], "town": h.get("town"), "state": h.get("state"), "board": h.get("board_label") or h.get("board_key"),
                       "meeting_date": h.get("meeting_date"), "source_url": b["source_url"],
                       "brief": {k: b.get(k) for k in JUDGED}, "agenda_window": window,
                       "quote_found": pos >= 0})
    json.dump({"n": len(sample), "seed": a.seed, "rows": sample}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(sample)} briefs sampled from {len(rows)} verified with agenda text ({len(verified)} verified in all) -> {a.out}")


if __name__ == "__main__":
    main()
