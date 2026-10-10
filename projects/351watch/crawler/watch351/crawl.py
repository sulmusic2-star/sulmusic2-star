"""Crawl pipeline: towns.json -> adapters -> agenda docs -> text -> topic hits."""

from __future__ import annotations

import json
import logging
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .adapters import REGISTRY
from .extract import Extracted, extract
from .fetch import FetchError, PoliteFetcher, Response
from .keywords import find_hits
from .models import AgendaDoc, Window

log = logging.getLogger(__name__)


@dataclass
class TownResult:
    town: str
    platform: str | None
    automated: bool
    agendas_listed: int = 0
    documents_scanned: int = 0
    documents_no_text: int = 0   # image-only PDFs
    documents_ocr: int = 0       # ...of which recovered with OCR
    hits: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    reason: str | None = None


def _resolve_pdf(fetcher: PoliteFetcher, resp: Response) -> Response:
    """For listings that link to an HTML landing page (e.g. WordPress
    attachment pages), follow the page's primary PDF link."""
    if resp.is_pdf:
        return resp
    soup = BeautifulSoup(resp.text, "lxml")
    links = [a for a in soup.find_all("a", href=True) if ".pdf" in a["href"].lower()]
    if not links:
        return resp
    best = next((a for a in links if re.search(r"download", a.get_text(), re.I)), links[0])
    return fetcher.get(urljoin(resp.final_url, best["href"]))


def scan_document(fetcher: PoliteFetcher, doc: AgendaDoc) -> tuple[list[dict], Extracted]:
    """Fetch + extract one agenda; return its keyword hits and the extraction."""
    resp = fetcher.get(doc.url)  # agenda documents are cached indefinitely
    if not resp.ok:
        raise FetchError(f"HTTP {resp.status}: {doc.url}")
    if doc.resolve_pdf:
        resp = _resolve_pdf(fetcher, resp)
    source_url = resp.final_url if doc.resolve_pdf else doc.url
    ex = extract(resp)
    if ex.error and not ex.text:
        raise FetchError(f"extract failed ({ex.error}): {doc.url}")
    hits = []
    for h in find_hits(ex.text):
        hits.append({
            "town": doc.town,
            "board": doc.board,
            "board_key": doc.board_key,
            "meeting_date": doc.meeting_date.isoformat() if doc.meeting_date else None,
            "topics": h.topics,
            "snippet": h.snippet,
            "source_url": source_url,
            "listing_url": doc.listing_url,
            "document_title": doc.title,
            "text_source": "ocr" if ex.ocr else ex.kind,
            "_context": h.context,
        })
    return hits, ex


def crawl_town(fetcher: PoliteFetcher, cfg: dict, window: Window) -> TownResult:
    res = TownResult(cfg["town"], cfg.get("platform"), bool(cfg.get("automated")))
    if not cfg.get("automated"):
        res.reason = cfg.get("reason")
        return res
    adapter = REGISTRY[cfg["platform"]](fetcher)
    try:
        docs = adapter.list_agendas(cfg, window)
    except (FetchError, RuntimeError, ValueError) as e:
        res.errors.append(f"listing: {e}")
        log.warning("%s: listing failed: %s", cfg["town"], e)
        return res
    res.agendas_listed = len(docs)
    for doc in docs:
        try:
            hits, ex = scan_document(fetcher, doc)
        except FetchError as e:
            res.errors.append(str(e)[:200])
            continue
        res.documents_scanned += 1
        res.documents_no_text += int(ex.scanned)
        res.documents_ocr += int(ex.ocr)
        res.hits.extend(hits)
    log.info("%s: %d agendas listed, %d scanned, %d hits", cfg["town"], res.agendas_listed,
             res.documents_scanned, len(res.hits))
    return res


def _dedupe(hits: list[dict]) -> list[dict]:
    """The same item often appears twice in one agenda (consent list + detail),
    in an agenda and its amended re-post, or in a packet and its revised
    packet. Key on the text right around the keyword and keep the first."""
    seen, out = set(), []
    for h in hits:
        ctx = h.pop("_context")
        key = (h["town"], h["board"], h["meeting_date"], ctx)
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


FIRST_SEEN_FILE = Path(__file__).resolve().parents[2] / "data" / "first_seen.json"


def stamp_first_seen(hits: list[dict], fetcher: PoliteFetcher, ledger_path: Path = FIRST_SEEN_FILE) -> None:
    """Record when each agenda document was first fetched, and how far ahead of the
    meeting day that was. The ledger survives cache wipes, so "flagged N days before"
    claims always rest on our own logged time. Meeting times are rarely published, so
    lead time is measured to the start of the meeting day (UTC), which understates it."""
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    now = time.time()
    for h in hits:
        url = h["source_url"]
        if url not in ledger:
            ts = fetcher.cached_at(url) or now
            ledger[url] = datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")
        h["first_seen"] = ledger[url]
        if h.get("meeting_date"):
            seen = datetime.fromisoformat(ledger[url])
            meeting = datetime.fromisoformat(h["meeting_date"]).replace(tzinfo=timezone.utc)
            h["days_before_meeting"] = round((meeting - seen).total_seconds() / 86400, 1)
    ledger_path.write_text(json.dumps(ledger, indent=0, sort_keys=True) + "\n")


def run_crawl(towns: list[dict], fetcher: PoliteFetcher, days_back: int = 45,
              days_ahead: int = 90, workers: int = 8, today: date | None = None) -> dict:
    today = today or date.today()
    window = Window(today - timedelta(days=days_back), today + timedelta(days=days_ahead))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda c: crawl_town(fetcher, c, window), towns))

    hits = _dedupe([h for r in results for h in r.hits])
    stamp_first_seen(hits, fetcher)
    hits.sort(key=lambda h: (h["meeting_date"] or "", h["town"], h["board"]), reverse=True)
    topic_counts = Counter(t for h in hits for t in h["topics"])
    by_platform: dict[str, dict[str, list[str]]] = {}
    for r, cfg in zip(results, towns):
        bucket = by_platform.setdefault(cfg.get("platform") or "unknown", {"automated": [], "not_automated": []})
        bucket["automated" if r.automated else "not_automated"].append(r.town)

    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window": {"start": window.start.isoformat(), "end": window.end.isoformat()},
        "towns_attempted": len(towns),
        "towns_automated": sum(r.automated for r in results),
        "documents_scanned": sum(r.documents_scanned for r in results),
        "documents_without_text_layer": sum(r.documents_no_text for r in results),
        "documents_ocr": sum(r.documents_ocr for r in results),
        "hits_by_topic": dict(topic_counts.most_common()),
        "towns_by_platform": by_platform,
        "towns": [{
            "town": r.town, "platform": r.platform, "automated": r.automated,
            "agendas_listed": r.agendas_listed, "documents_scanned": r.documents_scanned,
            "documents_without_text_layer": r.documents_no_text,
            "documents_ocr": r.documents_ocr,
            "hits": sum(1 for h in hits if h["town"] == r.town),
            "errors": r.errors[:10], "reason": r.reason,
        } for r in results],
        "hits": hits,
    }
