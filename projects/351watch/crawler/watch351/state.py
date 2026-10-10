"""Persistent incremental crawl state, committed to git under data/state/.

A fresh container (empty crawler/.cache) must never re-download an agenda
document the engine has already processed. The document index records every
agenda document ever scanned, with its extracted hits, so the daily run only
fetches listing pages plus documents it has never seen.

Layout (all deterministic: sorted keys, sorted lines, one JSON object per line):

    data/state/docs/<ST>/<YYYY-MM>.jsonl   one line per agenda document, sharded by state
                                           and meeting month ("undated.jsonl" for warrants
                                           etc. without a meeting date); lines sorted by
                                           (town, url)
    data/state/hits_archive/YYYY-MM.jsonl  hits for meetings older than the 120-day window
    data/state/runs/YYYY-MM-DD.json        daily run report
    data/state/town_health.json            per-town crawl health

Document record:

    {"url": ..., "state": "MA", "town": ..., "board": ..., "board_key": ...,
     "meeting_date": "YYYY-MM-DD" | null, "title": ..., "listing_url": ...,
     "first_seen": ISO time first fetched, "last_seen_in_listing": "YYYY-MM-DD",
     "status": "ok" | "needs_ocr" | "error", "text_source": "pdf|ocr|html|docx|text|...",
     "kw": matcher version, "hits": [{"topics": [...], "snippet": ..., "ctx": ...}],
     "source_url": only when the hits cite a different URL (resolved PDF),
     "attempts"/"error"/"permanent": only for needs_ocr / error records}

`last_seen_in_listing` is refreshed at most every LAST_SEEN_REFRESH_DAYS days, so
a daily run does not rewrite every in-window line just to bump a date.

    python3 -m watch351.state bootstrap   # build the index from the cache + hits files
    python3 -m watch351.state stats
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

log = logging.getLogger("watch351.state")

DATA = Path(__file__).resolve().parents[2] / "data"
STATE_DIR = DATA / "state"
DOCS_DIR = STATE_DIR / "docs"
ARCHIVE_DIR = STATE_DIR / "hits_archive"
RUNS_DIR = STATE_DIR / "runs"
HEALTH_FILE = STATE_DIR / "town_health.json"
LEDGER_FILE = DATA / "first_seen.json"

KEEP_DAYS = 180                 # drop records of meetings older than this (hits are archived first)
LAST_SEEN_REFRESH_DAYS = 7
MAX_ATTEMPTS = 3                # fetch errors / failed OCR are retried on this many runs
_PERMANENT = re.compile(r"too large|content-type|HTTP 40[04]|HTTP 410", re.I)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def iso_from_epoch(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")


def norm_ctx(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def is_permanent(error: str) -> bool:
    return bool(_PERMANENT.search(error or ""))


def _dumps(rec: dict) -> str:
    return json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, obj, indent: int | None = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=indent, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


# --------------------------------------------------------------------------- index
class DocIndex:
    """Every agenda document processed, keyed by URL. Thread-safe."""

    def __init__(self, root: Path = DOCS_DIR):
        self.root = Path(root)
        self._docs: dict[str, dict] = {}
        self._lock = threading.Lock()
        if self.root.exists():
            for path in sorted(self.root.rglob("*.jsonl")):
                for line in path.read_text().splitlines():
                    if line.strip():
                        rec = json.loads(line)
                        self._docs.setdefault(rec["url"], rec)

    # -- access ------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._docs)

    def __contains__(self, url: str) -> bool:
        return url in self._docs

    def get(self, url: str) -> dict | None:
        with self._lock:
            rec = self._docs.get(url)
            return dict(rec) if rec is not None else None

    def put(self, rec: dict) -> None:
        with self._lock:
            self._docs[rec["url"]] = rec

    def records(self) -> list[dict]:
        with self._lock:
            return list(self._docs.values())

    def states(self) -> set[str]:
        return {r["state"] for r in self.records()}

    def touch(self, url: str, today: date, meta: dict | None = None) -> None:
        """The document is on a listing again: refresh last_seen_in_listing (at most
        weekly) and fill metadata fields that were missing."""
        with self._lock:
            rec = self._docs.get(url)
            if rec is None:
                return
            last = rec.get("last_seen_in_listing")
            if not last or (today - date.fromisoformat(last)).days >= LAST_SEEN_REFRESH_DAYS:
                rec["last_seen_in_listing"] = today.isoformat()
            for k, v in (meta or {}).items():
                if v and not rec.get(k):
                    rec[k] = v

    # -- persistence ---------------------------------------------------------
    @staticmethod
    def shard_of(rec: dict) -> str:
        md = rec.get("meeting_date")
        return f"{rec['state']}/{md[:7] if md else 'undated'}.jsonl"

    def save(self) -> list[Path]:
        """Rewrite only shards whose content changed; delete emptied shards."""
        shards: dict[str, list[dict]] = {}
        for rec in self.records():
            shards.setdefault(self.shard_of(rec), []).append(rec)
        changed = []
        for name, recs in shards.items():
            recs.sort(key=lambda r: (r.get("town") or "", r["url"]))
            text = "\n".join(_dumps(r) for r in recs) + "\n"
            path = self.root / name
            if path.exists() and path.read_text() == text:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".jsonl.tmp")
            tmp.write_text(text)
            tmp.replace(path)
            changed.append(path)
        if self.root.exists():
            for path in self.root.rglob("*.jsonl"):
                if str(path.relative_to(self.root)) not in shards:
                    path.unlink()
                    changed.append(path)
        return changed

    def prune(self, today: date, keep_days: int = KEEP_DAYS) -> list[dict]:
        """Drop records for meetings older than keep_days (and undated records not
        listed for keep_days). The daily listing window starts 30 days back, so
        these can never be listed again; their hits go to the archive."""
        cutoff = (today - timedelta(days=keep_days)).isoformat()
        removed = []
        with self._lock:
            for url, rec in list(self._docs.items()):
                when = rec.get("meeting_date") or rec.get("last_seen_in_listing") or ""
                if when and when < cutoff:
                    removed.append(self._docs.pop(url))
        return removed

    # -- hits ----------------------------------------------------------------
    @staticmethod
    def hits_of(rec: dict) -> list[dict]:
        """A record's hits in the agenda-hit shape (before contract normalization)."""
        out = []
        for h in rec.get("hits") or []:
            out.append({
                "state": rec["state"], "town": rec["town"], "board": rec.get("board"),
                "board_key": rec.get("board_key"), "meeting_date": rec.get("meeting_date"),
                "topics": h["topics"], "snippet": h["snippet"],
                "source_url": rec.get("source_url") or rec["url"],
                "listing_url": rec.get("listing_url"), "document_title": rec.get("title"),
                "text_source": rec.get("text_source"), "first_seen": rec.get("first_seen"),
                "source": "agenda", "_ctx": h.get("ctx") or norm_ctx(h["snippet"]),
            })
        return out

    def current_hits(self) -> list[dict]:
        """All indexed hits, deduplicated across documents: the same item in an agenda
        and its amended re-post (or a packet) is kept once, from the document first
        seen, so its id and lead time never change once published."""
        recs = sorted((r for r in self.records() if r.get("hits") and r.get("board_key")),
                      key=lambda r: (r.get("first_seen") or "", r["url"]))
        seen, out = set(), []
        for rec in recs:
            for h in self.hits_of(rec):
                key = (h["state"], h["town"], h["board_key"], h["meeting_date"], h.pop("_ctx"))
                if key in seen:
                    continue
                seen.add(key)
                out.append(h)
        return out

    def stats(self) -> dict:
        recs = self.records()
        return {
            "documents": len(recs),
            "by_state": dict(Counter(r["state"] for r in recs)),
            "by_status": dict(Counter(r.get("status") for r in recs)),
            "by_text_source": dict(Counter(r.get("text_source") for r in recs)),
            "with_hits": sum(1 for r in recs if r.get("hits")),
            "hits": sum(len(r.get("hits") or []) for r in recs),
            "towns": len({(r["state"], r["town"]) for r in recs}),
        }


def make_record(doc, state: str, *, first_seen: str, today: date, hits: list[dict], ex=None,
                source_url: str | None = None, status: str = "ok", error: str | None = None,
                attempts: int = 0, matcher: str | None = None) -> dict:
    """Index record for an AgendaDoc. `hits` are crawl.scan_document hits (with _context)."""
    from .keywords import MATCHER_VERSION
    rec = {
        "url": doc.url, "state": state, "town": doc.town, "board": doc.board,
        "board_key": doc.board_key,
        "meeting_date": doc.meeting_date.isoformat() if doc.meeting_date else None,
        "title": (doc.title or "")[:200], "listing_url": doc.listing_url,
        "first_seen": first_seen, "last_seen_in_listing": today.isoformat(),
        "status": status,
        "text_source": ("ocr" if ex.ocr else ex.kind) if ex is not None else None,
        "kw": matcher or MATCHER_VERSION,
        "hits": [{"topics": h["topics"], "snippet": h["snippet"], "ctx": h.get("_context") or norm_ctx(h["snippet"])}
                 for h in hits],
    }
    if source_url and source_url != doc.url:
        rec["source_url"] = source_url
    if status != "ok":
        rec["attempts"] = attempts
        if error:
            rec["error"] = error[:200]
        if status == "error" and is_permanent(error or ""):
            rec["permanent"] = True
    return rec


# -------------------------------------------------------------------- ledgers
def update_ledger(index: DocIndex, path: Path = LEDGER_FILE) -> int:
    """data/first_seen.json: source_url -> first fetch time, for every document with
    hits. Existing entries are never changed."""
    ledger = json.loads(path.read_text()) if path.exists() else {}
    added = 0
    for rec in index.records():
        if rec.get("hits") and rec.get("first_seen"):
            url = rec.get("source_url") or rec["url"]
            if url not in ledger:
                ledger[url] = rec["first_seen"]
                added += 1
    if added or not path.exists():
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(ledger, indent=0, sort_keys=True) + "\n")
        tmp.replace(path)
    return added


def load_health(path: Path = HEALTH_FILE) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


# ------------------------------------------------------------------ bootstrap
def cache_metadata(cache_dir: Path) -> dict[str, dict]:
    """url -> cache metadata (fetched_at, final_url, status, content_type)."""
    out = {}
    for meta in Path(cache_dir).glob("*/*.json"):
        try:
            m = json.loads(meta.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(m, dict) and m.get("url"):
            out[m["url"]] = m
    return out


def _window_of(hits_file: Path):
    from .models import Window
    doc = json.loads(hits_file.read_text())
    w = doc["window"]
    return Window(date.fromisoformat(w["start"]), date.fromisoformat(w["end"])), doc


def bootstrap(cache_dir: Path, data_dir: Path = DATA, workers: int = 4, today: date | None = None) -> dict:
    """Build (or extend) the index from what earlier one-shot crawls left behind:

    1. re-list every automated town offline, with the exact windows of the census
       crawl (agenda_hits_ma_all.json) and the pilot crawl (agenda_hits.json), plus
       the daily window, from the cached listing pages;
    2. every listed document whose body is cached was scanned: re-extract it offline
       (OCR text is cached too) and re-match it, so even no-hit documents are recorded;
    3. any hit in agenda_hits_ma_all.json / agenda_hits.json whose document is still
       not indexed is added from the file itself.
    """
    from . import extract
    from .adapters import REGISTRY
    from .crawl import scan_document_full, town_configs
    from .current import load_towns
    from .fetch import FetchError, PoliteFetcher
    from .models import Window

    today = today or datetime.now(timezone.utc).date()
    cache_dir = Path(cache_dir)
    extract.OCR_CACHE = cache_dir / "ocr"
    extract.OCR_MAX_PAGES = 6
    fetcher = PoliteFetcher(cache_dir, offline=True)
    meta = cache_metadata(cache_dir)
    ledger = json.loads((data_dir / "first_seen.json").read_text()) if (data_dir / "first_seen.json").exists() else {}
    index = DocIndex(data_dir / "state" / "docs")
    before = len(index)
    report: dict = {"index_before": before, "cache_entries": len(meta)}

    census_file, pilot_file = data_dir / "agenda_hits_ma_all.json", data_dir / "agenda_hits.json"
    passes = []
    all_rows = load_towns(data_dir)
    if census_file.exists():
        w, doc = _window_of(census_file)
        passes.append(("census", all_rows, w, doc))
    if pilot_file.exists() and (data_dir / "towns.json").exists():
        w, doc = _window_of(pilot_file)
        pilot_rows = [{**t, "state": "MA"} for t in json.loads((data_dir / "towns.json").read_text())["towns"]]
        passes.append(("pilot", pilot_rows, w, doc))
    passes.append(("daily_window", all_rows, Window(today - timedelta(days=30), today + timedelta(days=120)), None))

    # 1. offline listings -> candidate documents (first listing wins, census first)
    listed: dict[str, tuple] = {}
    error_text: dict[str, str] = {}
    for name, rows, window, doc in passes:
        n0 = len(listed)
        seen_date = (doc or {}).get("generated", now_iso())[:10]
        if doc:
            for t in doc.get("towns", []):
                for e in t.get("errors", []):
                    for u in re.findall(r"https?://\S+", e):
                        error_text.setdefault(u.rstrip(":,"), e)
        for row in rows:
            for cfg in town_configs(row):
                cls = REGISTRY.get(cfg["platform"])
                if cls is None:
                    continue
                try:
                    docs = cls(fetcher).list_agendas(cfg, window)
                except Exception as e:  # noqa: BLE001 - uncached listing pages are expected
                    log.debug("%s %s: %s", row["town"], cfg["platform"], e)
                    continue
                for d in docs:
                    listed.setdefault(d.url, (d, row["state"], seen_date, name))
        report[f"listed_{name}"] = len(listed) - n0

    # 2. scan every cached, not-yet-indexed document offline
    todo = [v for url, v in listed.items() if url not in index]
    counts: Counter = Counter()

    def first_seen_for(url: str, source_url: str | None) -> str:
        for u in (source_url, url):
            if u and u in ledger:
                return ledger[u]
        m = meta.get(url)
        return iso_from_epoch(m["fetched_at"]) if m else now_iso()

    def one(item) -> None:
        d, state, seen_date, pass_name = item
        seen_day = date.fromisoformat(seen_date)
        if not fetcher.is_cached(d.url):
            err = error_text.get(d.url)
            if err:
                index.put(make_record(d, state, first_seen=now_iso(), today=seen_day, hits=[],
                                      status="error", error=err, attempts=1))
                counts["error_from_report"] += 1
            else:
                counts["listed_not_cached"] += 1
            return
        try:
            hits, ex, source_url = scan_document_full(fetcher, d)
        except FetchError as e:
            index.put(make_record(d, state, first_seen=first_seen_for(d.url, None), today=seen_day, hits=[],
                                  status="error", error=str(e), attempts=1))
            counts["error"] += 1
            return
        status = "needs_ocr" if (ex.scanned and not ex.ocr) else "ok"
        index.put(make_record(d, state, first_seen=first_seen_for(d.url, source_url), today=seen_day,
                              hits=hits, ex=ex, source_url=source_url, status=status,
                              attempts=1 if status != "ok" else 0))
        counts[f"scanned_{pass_name}"] += 1
        counts[status] += 1

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, todo))
    report.update(counts)

    # 3. hits from the one-shot crawl files whose document is still missing
    covered = set()
    for rec in index.records():
        covered.add(rec["url"])
        covered.add(rec.get("source_url") or rec["url"])
    added_from_files = 0
    for name, _rows, _w, doc in passes:
        if not doc:
            continue
        by_url: dict[str, list[dict]] = {}
        for h in doc.get("hits", []):
            if h["source_url"] not in covered:
                by_url.setdefault(h["source_url"], []).append(h)
        for url, hs in by_url.items():
            h0 = hs[0]
            index.put({
                "url": url, "state": h0.get("state") or "MA", "town": h0["town"], "board": h0.get("board"),
                "board_key": h0.get("board_key"), "meeting_date": h0.get("meeting_date"),
                "title": (h0.get("document_title") or "")[:200], "listing_url": h0.get("listing_url"),
                "first_seen": h0.get("first_seen") or ledger.get(url) or now_iso(),
                "last_seen_in_listing": doc["generated"][:10], "status": "ok",
                "text_source": h0.get("text_source"), "kw": "legacy",
                "hits": [{"topics": h["topics"], "snippet": h["snippet"], "ctx": norm_ctx(h["snippet"])} for h in hs],
            })
            covered.add(url)
            added_from_files += 1
    report["added_from_hits_files"] = added_from_files

    # coverage check against the census output
    if census_file.exists():
        cur = {(h["source_url"], h["snippet"]) for h in index.current_hits()}
        census_hits = json.loads(census_file.read_text())["hits"]
        report["census_hits"] = len(census_hits)
        report["census_hits_reproduced"] = sum(1 for h in census_hits if (h["source_url"], h["snippet"]) in cur)
        report["census_docs_scanned"] = json.loads(census_file.read_text()).get("documents_scanned")
    index.save()
    update_ledger(index, data_dir / "first_seen.json")
    report["index_after"] = len(index)
    report["stats"] = index.stats()
    return report


def main(argv: list[str] | None = None) -> int:
    from .fetch import DEFAULT_CACHE_DIR
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["bootstrap", "stats"])
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--data-dir", type=Path, default=DATA)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    if args.command == "bootstrap":
        print(json.dumps(bootstrap(args.cache_dir, args.data_dir, args.workers), indent=1))
    else:
        print(json.dumps(DocIndex(args.data_dir / "state" / "docs").stats(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
