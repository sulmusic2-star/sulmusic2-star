"""Searchable document text, committed to git under data/search/.

The crawler's disk cache (crawler/.cache) holds raw bodies and disappears with the
container, and the document index (data/state/docs/) holds only metadata and hit
snippets. This module keeps the text that full-text search needs, in git:

    data/search/<ST>/<YYYY-MM>.jsonl   one row per agenda document, sharded like
                                       data/state/docs (state, meeting month;
                                       "undated.jsonl" without a meeting date)

Row (keys in this order; one JSON object per line):

    {"id": sha1(url)[:12], "url": the document's key in data/state/docs,
     "source_url": only when the text came from another URL (landing page -> PDF),
     "listing_url", "state", "town", "county", "board", "board_key",
     "meeting_date": "YYYY-MM-DD" | null, "first_seen", "title", "text_source",
     "topics": sorted topics of the document's hits, "chars": full normalized length,
     "text": whitespace-normalized text, the first TEXT_CAP characters, then
             " … " and each hit snippet that lies beyond the cap}

Only documents whose text was read (index status "ok") get a row. The folder is
append-only: a run adds rows for documents it has not seen, in (town, url) order at
the end of each shard, so a daily git delta is just the new lines. A row is
rewritten in place only when its document is processed again and something changed
(re-match after a keyword-rule update, OCR replacing a scan). Rows are never pruned
with the document index: search covers every document 351 Watch has read.

When a rewrite changes a document's text (a town re-posts an amended agenda, or OCR
replaces a scan), the earlier text is kept, append-only, in

    data/archive/<ST>/<YYYY-MM>.jsonl  {"id", "url", "first_seen", "superseded_at",
                                        "text_sha256", "text"}

so the record of what each agenda said before its meeting, and when we saw it, is
never overwritten.

The daily engine calls `FullText.add` for each document it extracts and
`FullText.save` once at the end. For documents already indexed, rebuild rows from
the local cache without any network request:

    python3 -m watch351.fulltext backfill [--cache-dir PATH] [--no-ocr]
    python3 -m watch351.fulltext stats
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

log = logging.getLogger("watch351.fulltext")

DATA = Path(__file__).resolve().parents[2] / "data"
SEARCH_DIR = DATA / "search"
TEXT_CAP = 20_000      # characters of normalized text kept per document (an agenda is ~2k)
FIELDS = ("id", "url", "source_url", "listing_url", "state", "town", "county", "board", "board_key",
          "meeting_date", "first_seen", "title", "text_source", "topics", "chars", "text")

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0e-\x1f\x7f�­​-‍﻿]")
_RUNS = re.compile(r"([._\-=*~#_·•…])\1{3,}")   # leader dots, rules, signature lines
_SPACE = re.compile(r"\s+")


def doc_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def normalize(text: str) -> str:
    """One line of plain text: control characters dropped, runs of leader dots /
    rules shortened, whitespace collapsed."""
    text = _CONTROL.sub(" ", text or "")
    text = _RUNS.sub(r"\1\1\1", text)
    return _SPACE.sub(" ", text).strip()


def capped(text: str, snippets: list[str], cap: int = TEXT_CAP) -> str:
    """The first `cap` characters (cut at a word boundary), then the hit snippets
    the cut left out, so every matched passage stays searchable."""
    if len(text) <= cap:
        return text
    head = text[:cap]
    if not text[cap].isspace() and " " in head[-80:]:
        head = head[: head.rindex(" ")]
    head = head.rstrip()
    extra = []
    for s in snippets:
        s = normalize(s)
        if s and s not in head and s not in extra:
            extra.append(s)
    return " … ".join([head] + extra)


def make_row(rec: dict, text: str, county: str | None = None) -> dict:
    """Search row for a data/state/docs record and its extracted text."""
    full = normalize(text)
    row = {
        "id": doc_id(rec["url"]),
        "url": rec["url"],
        "source_url": rec.get("source_url") if rec.get("source_url") not in (None, rec["url"]) else None,
        "listing_url": rec.get("listing_url"),
        "state": rec["state"],
        "town": rec.get("town"),
        "county": county,
        "board": rec.get("board"),
        "board_key": rec.get("board_key"),
        "meeting_date": rec.get("meeting_date"),
        "first_seen": rec.get("first_seen"),
        "title": rec.get("title") or None,
        "text_source": rec.get("text_source"),
        "topics": sorted({t for h in rec.get("hits") or [] for t in h.get("topics") or []}),
        "chars": len(full),
        "text": capped(full, [h.get("snippet") or "" for h in rec.get("hits") or []]),
    }
    if row["source_url"] is None:
        del row["source_url"]
    return row


def _dumps(row: dict) -> str:
    return json.dumps(row, ensure_ascii=False, separators=(",", ":"))


def shard_of(row: dict) -> str:
    md = row.get("meeting_date")
    return f"{row['state']}/{md[:7] if md else 'undated'}.jsonl"


def _counties(data_dir: Path) -> dict:
    try:
        from .current import county_lookup, load_towns
        return county_lookup(load_towns(data_dir))
    except Exception as e:  # noqa: BLE001 - county is optional
        log.warning("county lookup unavailable: %s", e)
        return {}


class FullText:
    """The data/search folder: rows by id, plus the changes waiting for save(). Thread-safe."""

    def __init__(self, root: Path = SEARCH_DIR, data_dir: Path | None = None):
        self.root = Path(root)
        self.counties = _counties(Path(data_dir) if data_dir else self.root.parent)
        self._rows: dict[str, dict] = {}       # id -> row (with "_shard")
        self._pending: dict[str, dict] = {}    # id -> new or changed row
        self._lock = threading.Lock()
        if self.root.exists():
            for path in sorted(self.root.rglob("*.jsonl")):
                shard = str(path.relative_to(self.root))
                for line in path.read_text().splitlines():
                    if line.strip():
                        row = json.loads(line)
                        self._rows.setdefault(row["id"], {**row, "_shard": shard})

    def __len__(self) -> int:
        return len(self._rows)

    def __contains__(self, url: str) -> bool:
        return doc_id(url) in self._rows

    def rows(self) -> list[dict]:
        with self._lock:
            return [{k: v for k, v in r.items() if k != "_shard"} for r in self._rows.values()]

    def add(self, rec: dict, text: str | None) -> bool:
        """Queue the row for a document the crawler just extracted. Returns True if the
        folder will change. Never raises: search must not stop a crawl."""
        try:
            if rec.get("status") != "ok" or not normalize(text or ""):
                return False
            county = self.counties.get((rec["state"], (rec.get("town") or "").lower()))
            row = make_row(rec, text or "", county)
            with self._lock:
                old = self._rows.get(row["id"])
                if old is not None and {k: v for k, v in old.items() if k != "_shard"} == row:
                    return False
                self._pending[row["id"]] = row
            return True
        except Exception as e:  # noqa: BLE001
            log.warning("search row for %s failed: %s", rec.get("url"), e)
            return False

    def redate(self, rec: dict) -> bool:
        """The crawler learned a document's meeting day after the fact (a warrant dated from its own text):
        move its row to that month, text untouched. Returns True if the folder will change."""
        rid = doc_id(rec["url"])
        with self._lock:
            old = self._rows.get(rid)
            if old is None or old.get("meeting_date") == rec.get("meeting_date"):
                return False
            row = {k: v for k, v in old.items() if k != "_shard"}
            row["meeting_date"] = rec.get("meeting_date")
            self._pending[rid] = row
        return True

    def save(self) -> list[Path]:
        """Append new rows to their shards (sorted by town, url) and rewrite only the
        lines of rows that changed. Returns the files touched."""
        with self._lock:
            pending, self._pending = self._pending, {}
            appends: dict[str, list[dict]] = {}
            rewrites: dict[str, dict[str, dict | None]] = {}   # shard -> id -> new row (None = moved away)
            archived: dict[str, list[dict]] = {}   # shard -> superseded text versions
            now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            for rid, row in pending.items():
                shard = shard_of(row)
                old = self._rows.get(rid)
                if old is not None and old.get("text") != row.get("text"):
                    archived.setdefault(old["_shard"], []).append({
                        "id": rid, "url": old.get("url"), "first_seen": old.get("first_seen"),
                        "superseded_at": now,
                        "text_sha256": hashlib.sha256((old.get("text") or "").encode("utf-8")).hexdigest(),
                        "text": old.get("text") or "",
                    })
                if old is None:
                    appends.setdefault(shard, []).append(row)
                elif old["_shard"] == shard:
                    rewrites.setdefault(shard, {})[rid] = row
                else:
                    rewrites.setdefault(old["_shard"], {})[rid] = None
                    appends.setdefault(shard, []).append(row)
                self._rows[rid] = {**row, "_shard": shard}
        touched = []
        try:
            for shard, versions in sorted(archived.items()):
                path = self.root.parent / "archive" / shard
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as fh:
                    fh.write("".join(_dumps(v) + "\n" for v in versions))
                touched.append(path)
            for shard, changes in sorted(rewrites.items()):
                path = self.root / shard
                lines = []
                for line in path.read_text().splitlines():
                    if not line.strip():
                        continue
                    rid = json.loads(line)["id"]
                    if rid in changes:
                        if changes[rid] is not None:
                            lines.append(_dumps(changes[rid]))
                    else:
                        lines.append(line)
                tmp = path.with_suffix(".jsonl.tmp")
                tmp.write_text("".join(l + "\n" for l in lines))
                tmp.replace(path)
                touched.append(path)
            for shard, rows in sorted(appends.items()):
                path = self.root / shard
                path.parent.mkdir(parents=True, exist_ok=True)
                rows.sort(key=lambda r: (r.get("town") or "", r["url"]))
                prefix = ""
                if path.exists() and path.stat().st_size:
                    with path.open("rb") as fh:
                        fh.seek(-1, 2)
                        prefix = "" if fh.read(1) == b"\n" else "\n"
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(prefix + "".join(_dumps(r) + "\n" for r in rows))
                touched.append(path)
        except OSError as e:
            log.error("writing data/search failed: %s", e)
        if pending:
            log.info("search: %d rows written (%d files)", len(pending), len(set(touched)))
        return touched

    def stats(self) -> dict:
        rows = self.rows()
        size = sum(p.stat().st_size for p in self.root.rglob("*.jsonl")) if self.root.exists() else 0
        return {
            "rows": len(rows),
            "bytes": size,
            "text_chars": sum(len(r["text"]) for r in rows),
            "truncated": sum(1 for r in rows if r.get("chars", 0) > TEXT_CAP),
            "by_state": dict(Counter(r["state"] for r in rows)),
            "by_text_source": dict(Counter(r.get("text_source") or "none" for r in rows)),
            "with_topics": sum(1 for r in rows if r.get("topics")),
            "shards": len(list(self.root.rglob("*.jsonl"))) if self.root.exists() else 0,
        }


# ------------------------------------------------------------------- backfill
def cached_text(fetcher, rec: dict) -> str | None:
    """Re-extract a document's text through the crawler's own fetch/extract path, from
    the cache only (the fetcher must be offline). None if the body is not cached."""
    from .crawl import scan_document_full
    from .fetch import FetchError
    from .models import AgendaDoc

    doc = AgendaDoc(town=rec.get("town") or "", board=rec.get("board") or "", board_key=rec.get("board_key") or "",
                    meeting_date=date.fromisoformat(rec["meeting_date"]) if rec.get("meeting_date") else None,
                    title=rec.get("title") or "", url=rec["url"], listing_url=rec.get("listing_url") or "",
                    resolve_pdf=bool(rec.get("source_url")))
    if not fetcher.is_cached(doc.url):
        return None
    try:
        _hits, ex, _source_url = scan_document_full(fetcher, doc)
    except FetchError as e:
        log.info("backfill: %s: %s", rec["url"], e)
        return None
    return ex.text


def backfill(cache_dir: Path, data_dir: Path = DATA, workers: int = 4, ocr: bool = True) -> dict:
    """Add a row for every indexed document (status ok) that has none, re-extracting its
    text from the local cache. Never touches the network."""
    from . import extract
    from .fetch import PoliteFetcher
    from .state import DocIndex

    cache_dir = Path(cache_dir)
    extract.OCR_CACHE = cache_dir / "ocr"   # OCR text is cached by content hash
    extract.OCR_MAX_PAGES = 6               # same as the daily engine
    if not ocr:                             # use cached OCR text only; never run tesseract
        def cached_ocr(data: bytes) -> str:
            path = extract.OCR_CACHE / f"{hashlib.sha256(data).hexdigest()[:32]}.txt"
            return path.read_text() if path.exists() else ""
        extract.ocr_pdf = cached_ocr
        extract.TESSERACT = extract.TESSERACT or "cached-only"
    fetcher = PoliteFetcher(cache_dir, offline=True)
    index = DocIndex(data_dir / "state" / "docs")
    ft = FullText(data_dir / "search", data_dir)
    recs = [r for r in index.records() if r.get("status") == "ok"]
    todo = [r for r in recs if r["url"] not in ft]
    counts: Counter = Counter(documents_ok=len(recs), already=len(recs) - len(todo))

    def one(rec: dict) -> None:
        text = cached_text(fetcher, rec)
        if text is None:
            counts["not_cached"] += 1
        elif ft.add(rec, text):
            counts["added"] += 1
        else:
            counts["no_text"] += 1

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, sorted(todo, key=lambda r: r["url"])))
    ft.save()
    return {**dict(counts), "network_requests": fetcher.stats["network"], "stats": ft.stats()}


def main(argv: list[str] | None = None) -> int:
    from .fetch import DEFAULT_CACHE_DIR
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["backfill", "stats"])
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--data-dir", type=Path, default=DATA)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--no-ocr", action="store_true", help="skip scans whose OCR text is not cached")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.command == "backfill":
        out = backfill(args.cache_dir, args.data_dir, args.workers, ocr=not args.no_ocr)
    else:
        out = FullText(args.data_dir / "search", args.data_dir).stats()
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
