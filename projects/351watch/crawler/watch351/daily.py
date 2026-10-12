"""Daily incremental crawl: every automated town in data/towns_*.json.

    python3 -m watch351.daily [--states MA,NY,RI] [--towns Amherst,...] [--no-network-docs]
                              [--cache-dir PATH] [--workers 16]
    python3 -m watch351.daily --states MI,VA --output-dir ../data/test --hits-name hits_mi_va.json

Gated states (a data/towns_<st>.json marked "gated": true, e.g. MI and VA under test) are
never part of the default run: they are crawled only when named in --states, and only with
an --output-dir other than data/ (their index, ledger, health, run report and hits file go
there), so data/hits_current.json and data/state/ are never touched by them.

For each automated town (rows default to state MA; the 30-town pilot
data/towns.json is not read):

1. refresh its agenda listings through the platform adapter registry
   (adapters/__init__.py REGISTRY; a new platform plugs in by registering an
   adapter under the `platform` name its town rows / listings use);
2. take documents for meetings from 30 days back to 120 days ahead;
3. skip every document already in the index (data/state/docs/), so a fresh
   container downloads only listing pages plus genuinely new documents;
4. fetch / extract / match new documents (OCR: first 6 pages, if tesseract is
   installed; otherwise the record is marked needs_ocr and retried on a later
   run that has tesseract), and retry earlier fetch errors up to 3 times;
5. save the index, data/first_seen.json, rebuild data/hits_current.json
   (archiving hits older than 120 days), prune index records older than 180 days;
6. write data/state/runs/YYYY-MM-DD.json and data/state/town_health.json.

All requests go through PoliteFetcher (robots.txt on every host and redirect hop,
<= 1 request/second/host, 351WatchBot user agent, crawl-delay > 10 s skipped).
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import attribution, current, extract
from .adapters import REGISTRY
from .crawl import scan_document_full, town_configs
from .fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from .fulltext import FullText
from .keywords import MATCHER_VERSION
from .models import AgendaDoc, Window
from .state import (DATA, MAX_ATTEMPTS, DocIndex, iso_from_epoch, load_health, make_record, now_iso,
                    update_ledger, write_health, write_json)

log = logging.getLogger("watch351.daily")

DAYS_BACK = 30
DAYS_AHEAD = 120
OCR_MAX_PAGES = 6
MAX_ERRORS_REPORTED = 300


@dataclass
class TownOutcome:
    key: str
    state: str
    town: str
    configs: int = 0
    configs_ok: int = 0
    boards_ok: set = field(default_factory=set)
    boards_failed: set = field(default_factory=set)
    listed: int = 0
    already_indexed: int = 0
    new_documents: int = 0
    retried: int = 0
    rematched: int = 0
    needs_ocr: int = 0
    doc_errors: int = 0
    deferred: int = 0
    new_hits: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.configs_ok == 0:
            return "failed"
        return "ok" if self.configs_ok == self.configs else "partial"


class DailyRun:
    def __init__(self, cache_dir: Path, data_dir: Path = DATA, today: date | None = None,
                 days_back: int = DAYS_BACK, days_ahead: int = DAYS_AHEAD, no_network_docs: bool = False,
                 workers: int = 16, towns_dir: Path | None = None, report_towns: list[dict] | None = None,
                 hits_name: str = "hits_current.json"):
        """`data_dir` receives the state index, ledger, run report, health and hits file;
        `towns_dir` (default: data_dir) holds the towns_*.json configs. `report_towns`, when
        given, are the town rows the hits file and health report cover (a gated test run);
        otherwise every non-gated row in towns_dir."""
        self.started = now_iso()
        self.t0 = time.monotonic()
        self.today = today or datetime.now(timezone.utc).date()
        self.window = Window(self.today - timedelta(days=days_back), self.today + timedelta(days=days_ahead))
        self.data_dir = Path(data_dir)
        self.towns_dir = Path(towns_dir) if towns_dir is not None else self.data_dir
        self.report_towns = report_towns
        self.hits_name = hits_name
        self.no_network_docs = no_network_docs
        self.workers = workers
        cache_dir = Path(cache_dir)
        extract.OCR_CACHE = cache_dir / "ocr"   # OCR text cache follows the fetch cache
        extract.OCR_MAX_PAGES = OCR_MAX_PAGES
        self.tesseract = bool(extract.TESSERACT)
        # Without poppler every PDF would fail to extract and burn its retry attempts:
        # defer all documents to a run that has pdftotext.
        self.can_extract = shutil.which("pdftotext") is not None and shutil.which("pdfinfo") is not None
        self.fetcher = PoliteFetcher(cache_dir)
        self.index = DocIndex(self.data_dir / "state" / "docs")
        self.fulltext = FullText(self.data_dir / "search", self.data_dir)   # data/search rows
        ledger_p = self.data_dir / "first_seen.json"
        self.ledger = json.loads(ledger_p.read_text()) if ledger_p.exists() else {}
        self._claimed: set[str] = set()
        self._claim_lock = threading.Lock()

    # ------------------------------------------------------------------ docs
    def _claim(self, url: str) -> bool:
        with self._claim_lock:
            if url in self._claimed:
                return False
            self._claimed.add(url)
            return True

    def _first_seen(self, url: str) -> str:
        if url in self.ledger:
            return self.ledger[url]
        ts = self.fetcher.cached_at(url)
        return iso_from_epoch(ts) if ts else now_iso()

    def _cached_for_rematch(self, rec: dict, doc: AgendaDoc) -> bool:
        if not self.fetcher.is_cached(doc.url):
            return False
        return not doc.resolve_pdf or self.fetcher.is_cached(rec.get("source_url") or doc.url)

    def _attribution_names(self, row: dict) -> dict[str, str]:
        rows = self.report_towns if self.report_towns is not None else current.load_towns(self.towns_dir)
        return attribution.known_townships(rows, row.get("county") or "")

    def process_doc(self, doc: AgendaDoc, state: str, out: TownOutcome, row: dict | None = None) -> None:
        if row is not None and row.get("attribute_townships") and "county" not in doc.board.lower():
            doc.board = f"{row.get('county')} County {doc.board}"   # "Monroe County Planning Commission"
        out.listed += 1
        if not self._claim(doc.url):
            out.already_indexed += 1
            return
        rec = self.index.get(doc.url)
        rematch = False
        if rec is not None:
            self.index.touch(doc.url, self.today, {
                "board": doc.board, "board_key": doc.board_key, "title": doc.title,
                "listing_url": doc.listing_url,
                "meeting_date": doc.meeting_date.isoformat() if doc.meeting_date else None})
            status, attempts = rec.get("status"), rec.get("attempts", 0)
            if status == "ok":
                # matching rules changed: re-match from the local cache only (never re-download)
                if rec.get("kw") != MATCHER_VERSION and self._cached_for_rematch(rec, doc):
                    rematch = True
                else:
                    out.already_indexed += 1
                    return
            elif status == "needs_ocr":
                if not (self.tesseract and attempts < MAX_ATTEMPTS):
                    out.already_indexed += 1
                    return
            elif rec.get("permanent") or attempts >= MAX_ATTEMPTS:
                out.already_indexed += 1
                return
        if not self.can_extract or (self.no_network_docs and not self.fetcher.is_cached(doc.url)):
            out.deferred += 1
            return
        prev_attempts = (rec or {}).get("attempts", 0)
        try:
            with self.fetcher.purpose("document"):
                hits, ex, source_url = scan_document_full(self.fetcher, doc, state)
            if row is not None and row.get("attribute_townships"):
                # county planning commission items -> the township they name (attribution.py)
                attribution.attribute(hits, ex.text, row, self._attribution_names(row))
        except Exception as e:  # noqa: BLE001 - one bad document must not stop the town
            msg = f"{type(e).__name__}: {e}" if not isinstance(e, FetchError) else str(e)
            if rematch:  # keep the good record; re-matching is best effort
                out.already_indexed += 1
                log.info("%s: re-match failed for %s: %s", out.key, doc.url, msg[:160])
                return
            self.index.put(make_record(doc, state, first_seen=(rec or {}).get("first_seen") or now_iso(),
                                       today=self.today, hits=[], status="error", error=msg,
                                       attempts=prev_attempts + 1))
            out.doc_errors += 1
            out.errors.append(f"document: {msg}"[:300])
            return
        needs_ocr = ex.scanned and not ex.ocr
        new = make_record(doc, state, first_seen=(rec or {}).get("first_seen") or self._first_seen(source_url),
                          today=self.today, hits=hits, ex=ex, source_url=source_url,
                          status="needs_ocr" if needs_ocr else "ok",
                          attempts=prev_attempts + 1 if needs_ocr else 0)
        if rec is not None:
            new["last_seen_in_listing"] = self.index.get(doc.url)["last_seen_in_listing"]
        self.index.put(new)
        self.fulltext.add(new, ex.text)
        if needs_ocr:
            out.needs_ocr += 1
        if rematch:
            out.rematched += 1
        elif rec is not None:
            out.retried += 1
        else:
            out.new_documents += 1
        if not rematch:
            out.new_hits.extend({"topics": h["topics"]} for h in hits)

    # ----------------------------------------------------------------- towns
    def run_town(self, row: dict) -> TownOutcome:
        state = row["state"]
        out = TownOutcome(f"{state}:{row['town']}", state, row["town"])
        for cfg in town_configs(row):
            out.configs += 1
            boards = {l.get("board_key") for l in cfg["listings"] if l.get("board_key")}
            cls = REGISTRY.get(cfg["platform"])
            if cls is None:
                out.errors.append(f"listing: no adapter registered for platform {cfg['platform']!r}")
                out.boards_failed |= boards
                continue
            try:
                with self.fetcher.purpose("listing"):
                    docs = cls(self.fetcher).list_agendas(cfg, self.window)
            except Exception as e:  # noqa: BLE001 - adapters raise FetchError/RuntimeError/ValueError/...
                out.errors.append(f"listing {cfg['platform']}: {e}"[:300])
                out.boards_failed |= boards
                log.info("%s: listing %s failed: %s", out.key, cfg["platform"], str(e)[:160])
                continue
            out.configs_ok += 1
            out.boards_ok |= boards
            for doc in docs:
                self.process_doc(doc, state, out, row)
        out.boards_failed -= out.boards_ok
        log.info("%s: %s, %d listed, %d new, %d hits", out.key, out.status, out.listed,
                 out.new_documents, len(out.new_hits))
        return out

    # ------------------------------------------------------------------- run
    def run(self, rows: list[dict]) -> dict:
        outcomes: list[TownOutcome] = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = [pool.submit(self.run_town, r) for r in rows]
            for f in as_completed(futures):
                outcomes.append(f.result())
        outcomes.sort(key=lambda o: o.key)

        self.index.save()
        self.fulltext.save()
        update_ledger(self.index, self.data_dir / "first_seen.json")
        prev = self._previous_ids()
        doc = current.rebuild(self.data_dir, today=self.today, agenda_hits=self.index.current_hits(),
                              indexed_urls=self.index.urls(), towns=self.report_towns, out_name=self.hits_name)
        pruned = self.index.prune(self.today)
        if pruned:
            self.index.save()
        new_ids = [h for h in doc["hits"] if h["id"] not in prev] if prev is not None else []
        self._update_health(outcomes)
        report = self._report(outcomes, doc, new_ids, len(pruned))
        path = self.data_dir / "state" / "runs" / f"{self.today.isoformat()}.json"
        try:  # a second run on the same day keeps the earlier runs' summaries
            earlier = json.loads(path.read_text())
            report["previous_runs_today"] = earlier.pop("previous_runs_today", []) + [
                {k: earlier.get(k) for k in ("started", "duration_seconds", "states", "towns_attempted",
                                              "towns_succeeded", "new_documents", "new_hits")}
                | {"requests": earlier.get("network", {}).get("requests")}]
        except (OSError, ValueError, AttributeError):
            pass
        write_json(path, report)
        return report

    def _previous_ids(self) -> set[str] | None:
        try:
            return {h["id"] for h in json.loads((self.data_dir / self.hits_name).read_text())["hits"]}
        except (OSError, ValueError, KeyError):
            return None

    def _update_health(self, outcomes: list[TownOutcome]) -> None:
        path = self.data_dir / "state" / "town_health.json"
        health = load_health(path)
        rows = self.report_towns if self.report_towns is not None else current.load_towns(self.towns_dir)
        automated = {f"{t['state']}:{t['town']}" for t in rows if t.get("automated")}
        health = {k: v for k, v in health.items() if k in automated}
        for o in outcomes:
            h = health.setdefault(o.key, {"last_success": None, "last_error": None,
                                          "consecutive_failures": 0, "boards_ok": []})
            h.pop("last_attempt", None)
            h["status"] = o.status
            if o.status != "failed":
                h["last_success"] = self.started
                h["consecutive_failures"] = 0
            else:
                h["consecutive_failures"] = h.get("consecutive_failures", 0) + 1
            listing_errors = [e for e in o.errors if e.startswith("listing")]
            if listing_errors:
                h["last_error"] = listing_errors[0]
                h["last_error_at"] = self.started
            h["boards_ok"] = sorted(o.boards_ok)
            h["boards_failed"] = sorted(o.boards_failed)
        write_health(path, health)

    def _report(self, outcomes: list[TownOutcome], doc: dict, new_ids: list[dict], pruned: int) -> dict:
        f = self.fetcher
        raw_topics = Counter(t for o in outcomes for h in o.new_hits for t in h["topics"])
        by_state: dict[str, Counter] = {}
        for o in outcomes:
            c = by_state.setdefault(o.state, Counter())
            c["towns_attempted"] += 1
            c["towns_succeeded"] += o.status != "failed"
            c["new_documents"] += o.new_documents
            c["new_hits"] += len(o.new_hits)
        errors = [{"town": o.key, "error": e} for o in outcomes for e in o.errors]
        return {
            "date": self.today.isoformat(),
            "started": self.started,
            "finished": now_iso(),
            "duration_seconds": round(time.monotonic() - self.t0, 1),
            "window": {"start": self.window.start.isoformat(), "end": self.window.end.isoformat()},
            "options": {"no_network_docs": self.no_network_docs, "tesseract": self.tesseract,
                        "pdftotext": self.can_extract,
                        "ocr_max_pages": OCR_MAX_PAGES, "workers": self.workers,
                        "matcher_version": MATCHER_VERSION},
            "states": sorted(by_state),
            "towns_attempted": len(outcomes),
            "towns_succeeded": sum(o.status != "failed" for o in outcomes),
            "towns_partial": sorted(o.key for o in outcomes if o.status == "partial"),
            "towns_failed": sorted(o.key for o in outcomes if o.status == "failed"),
            "documents_listed": sum(o.listed for o in outcomes),
            "documents_already_indexed": sum(o.already_indexed for o in outcomes),
            "new_documents": sum(o.new_documents for o in outcomes),
            "documents_retried": sum(o.retried for o in outcomes),
            "documents_rematched": sum(o.rematched for o in outcomes),
            "documents_needing_ocr": sum(o.needs_ocr for o in outcomes),
            "documents_deferred": sum(o.deferred for o in outcomes),
            "document_errors": sum(o.doc_errors for o in outcomes),
            "new_hits": sum(len(o.new_hits) for o in outcomes),
            "new_hits_by_topic": dict(raw_topics.most_common()),
            "new_alert_items": len(new_ids),
            "new_alert_items_by_topic": dict(Counter(t for h in new_ids for t in h["topics"]).most_common()),
            "by_state": {st: dict(c) for st, c in sorted(by_state.items())},
            "hits_current": len(doc["hits"]),
            "index": {**self.index.stats(), "pruned": pruned},
            "network": {
                "requests": f.stats["network"],
                "requests_by_purpose": dict(f.requests_by_purpose),
                "bytes_by_purpose": dict(f.bytes_by_purpose),
                "cache_hits": f.stats["cache"],
                "robots_blocked": f.stats["robots_blocked"],
                "errors": f.stats["errors"],
            },
            "errors_total": len(errors),
            "errors": errors[:MAX_ERRORS_REPORTED],
        }


def select_towns(data_dir: Path, states: set[str] | None, towns: set[str] | None) -> list[dict]:
    """Automated rows to crawl. Gated states are included only when named in `states`."""
    rows = [t for t in current.load_towns(data_dir, include_gated=states) if t.get("automated")]
    if states:
        rows = [t for t in rows if t["state"] in states]
    if towns:
        rows = [t for t in rows if t["town"].lower() in towns]
    seen, out = set(), []
    for t in rows:  # one row per (state, town)
        if (t["state"], t["town"]) not in seen:
            seen.add((t["state"], t["town"]))
            out.append(t)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--states", help="comma-separated state codes (default: every data/towns_*.json)")
    p.add_argument("--towns", help="comma-separated town names (testing)")
    p.add_argument("--no-network-docs", action="store_true",
                   help="refresh listings but download no documents (cached ones are still processed)")
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--data-dir", type=Path, default=DATA, help="where the towns_*.json configs are")
    p.add_argument("--output-dir", type=Path, default=None,
                   help="write the state index, ledger, run report, health and hits file here instead of "
                        "--data-dir (required for gated states such as MI and VA; e.g. ../data/test)")
    p.add_argument("--hits-name", default="hits_current.json",
                   help="file name of the hits file written in the output dir (e.g. hits_mi_va.json)")
    p.add_argument("--workers", type=int, default=16, help="towns in parallel (each host stays <= 1 req/s)")
    p.add_argument("--days-back", type=int, default=DAYS_BACK)
    p.add_argument("--days-ahead", type=int, default=DAYS_AHEAD)
    p.add_argument("--request-log", type=Path, help="write every network request (purpose, status, url) here")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    if not args.verbose:
        logging.getLogger("watch351.daily").setLevel(logging.WARNING)

    states = {s.strip().upper() for s in args.states.split(",")} if args.states else None
    towns = {t.strip().lower() for t in args.towns.split(",")} if args.towns else None
    rows = select_towns(args.data_dir, states, towns)
    if not rows:
        print("no automated towns selected", file=sys.stderr)
        return 2
    out_dir = args.output_dir or args.data_dir
    production_out = out_dir.resolve() == args.data_dir.resolve()
    gated = current.gated_states(args.data_dir) & {t["state"] for t in rows}
    if gated and production_out:
        print(f"gated state(s) {sorted(gated)} are not part of the production run: pass --output-dir "
              f"(e.g. ../data/test) so data/hits_current.json and data/state/ stay untouched", file=sys.stderr)
        return 2
    report_towns = None
    if not production_out:
        chosen = {t["state"] for t in rows}
        report_towns = [t for t in current.load_towns(args.data_dir, include_gated=states) if t["state"] in chosen]
    run = DailyRun(args.cache_dir, out_dir, days_back=args.days_back, days_ahead=args.days_ahead,
                   no_network_docs=args.no_network_docs, workers=args.workers, towns_dir=args.data_dir,
                   report_towns=report_towns, hits_name=args.hits_name)
    if not run.tesseract:
        print("tesseract not installed: image-only PDFs are recorded as needs_ocr and retried later",
              file=sys.stderr)
    if not run.can_extract:
        print("poppler-utils (pdftotext) not installed: listings only, documents deferred", file=sys.stderr)
    r = run.run(rows)
    if args.request_log:
        args.request_log.write_text("".join(f"{k}\t{s}\t{u}\n" for k, u, s in run.fetcher.request_log))
    print(f"daily {r['date']}: towns {r['towns_succeeded']}/{r['towns_attempted']} ok "
          f"({len(r['towns_partial'])} partial, {len(r['towns_failed'])} failed); "
          f"listed {r['documents_listed']}, already indexed {r['documents_already_indexed']}, "
          f"new {r['new_documents']}, retried {r['documents_retried']}, rematched {r['documents_rematched']}, "
          f"needs OCR {r['documents_needing_ocr']}, deferred {r['documents_deferred']}, "
          f"doc errors {r['document_errors']}")
    print(f"  new hits {r['new_hits']} {r['new_hits_by_topic']}; new alert items {r['new_alert_items']}; "
          f"hits_current {r['hits_current']}; index {r['index']['documents']} docs")
    print(f"  network {r['network']['requests']} requests {r['network']['requests_by_purpose']}, "
          f"{sum(r['network']['bytes_by_purpose'].values()) / 1e6:.1f} MB; "
          f"cache hits {r['network']['cache_hits']}; runtime {r['duration_seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
