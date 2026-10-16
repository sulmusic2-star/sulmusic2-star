"""Build data/hits_current.json, the shared alert-data contract (see ARCHITECTURE.md).

    python3 -m watch351.current            # rebuild from the crawl state, validate, write
    python3 -m watch351.current --check    # validate the existing file only

Inputs, merged and deduplicated by hit id:

* agenda hits: the incremental document index in data/state/docs/ when it exists
  (written by `watch351.daily`), otherwise the census snapshot
  data/agenda_hits_ma_all.json (+ data/first_seen.json);
* data/agenda_hits_<st>.json for any other two-letter state code;
* data/sources/*_hits.json from second-source workstreams (e.g. MassDEP).

Window: meetings from 120 days back to 120 days ahead of today. Hits for older
meetings are moved to data/state/hits_archive/YYYY-MM.jsonl (by meeting month);
undated hits are windowed on their first_seen date instead.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

log = logging.getLogger("watch351.current")

DATA = Path(__file__).resolve().parents[2] / "data"
WINDOW_DAYS = 120

BOARD_KEYS = {"planning_board", "zoning_board_of_appeals", "conservation_commission",
              "select_board", "town_meeting"}
TOPIC_KEYS = {"battery_storage", "solar", "data_center", "moratorium", "clean_energy_siting",
              "40b_comprehensive_permit", "wireless_telecom", "zoning_amendment", "wetlands_filing",
              # Wave 1 state feeds (Vermont Act 250): quarries / gravel pits, large commercial or industrial
              # projects. In the contract (ARCHITECTURE.md) but used only by gated sources until the site has
              # labels for them.
              "extraction", "large_development"}
# The contract names pdf|ocr|html; Word and plain-text agendas keep their true kind.
TEXT_SOURCES = {"pdf", "ocr", "html", "docx", "text"}
FIELDS = ["id", "state", "town", "county", "board", "board_key", "meeting_date", "topics", "snippet",
          "source_url", "doc_url", "listing_url", "document_title", "text_source", "first_seen",
          "days_before_meeting", "source"]
OPTIONAL_FIELDS = {"days_before_meeting", "county", "doc_url"}
_STATE_FILE = re.compile(r"^agenda_hits_([a-z]{2})\.json$")


def hit_id(source_url: str, snippet: str) -> str:
    return hashlib.sha1(f"{source_url}|{snippet}".encode("utf-8")).hexdigest()[:12]


def _load(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        log.warning("cannot read %s: %s", path, e)
        return None


def _hits_of(doc) -> list[dict]:
    if isinstance(doc, list):
        return [h for h in doc if isinstance(h, dict)]
    if isinstance(doc, dict) and isinstance(doc.get("hits"), list):
        return [h for h in doc["hits"] if isinstance(h, dict)]
    return []


# --------------------------------------------------------------------------- towns
def town_files(data_dir: Path = DATA) -> list[Path]:
    """Every per-state town config (data/towns_*.json). The 30-town pilot
    data/towns.json does not match the pattern and is never read."""
    return sorted(data_dir.glob("towns_*.json"))


def gated_state(doc, path: Path) -> str | None:
    """A towns file marked {"gated": true} (a state under test, e.g. MI or VA) returns its
    state code: such a state is crawled and published only when named explicitly."""
    if isinstance(doc, dict) and doc.get("gated"):
        return (doc.get("state") or path.stem.rsplit("_", 1)[-1]).upper()
    return None


def load_towns(data_dir: Path = DATA, include_gated: set[str] | None = None) -> list[dict]:
    """All town rows from data/towns_*.json; rows default to state MA. Files marked
    "gated" are skipped unless their state is in `include_gated` (daily.py passes the
    states named with --states), so the default production run never picks them up."""
    rows = []
    allowed = {s.upper() for s in (include_gated or ())}
    for p in town_files(data_dir):
        doc = _load(p)
        gated = gated_state(doc, p)
        if gated and gated not in allowed:
            continue
        towns = doc.get("towns", []) if isinstance(doc, dict) else (doc if isinstance(doc, list) else [])
        for t in towns:
            if isinstance(t, dict) and t.get("town"):
                rows.append({**t, "state": (t.get("state") or "MA").upper()})
    return rows


def gated_states(data_dir: Path = DATA) -> set[str]:
    """State codes whose towns file is gated (not part of the production run)."""
    return {st for p in town_files(data_dir) if (st := gated_state(_load(p), p))}


def county_lookup(towns: list[dict]) -> dict[tuple[str, str], str]:
    return {(t["state"], t["town"].lower()): t.get("county") for t in towns if t.get("county")}


def towns_monitored(towns: list[dict]) -> dict[str, int]:
    out: dict[str, set] = {}
    for t in towns:
        if t.get("automated"):
            out.setdefault(t["state"], set()).add(t["town"])
    return {st: len(v) for st, v in sorted(out.items())}


# ----------------------------------------------------------------------- sources
def legacy_agenda_hits(data_dir: Path = DATA) -> list[dict]:
    """Census snapshot hits (data/agenda_hits_ma_all.json) with first_seen from the ledger."""
    doc = _load(data_dir / "agenda_hits_ma_all.json") or {}
    ledger = _load(data_dir / "first_seen.json") or {}
    out = []
    for h in _hits_of(doc):
        h = {**h, "state": h.get("state") or "MA", "source": h.get("source") or "agenda"}
        if not h.get("first_seen") and h.get("source_url") in ledger:
            h["first_seen"] = ledger[h["source_url"]]
        out.append(h)
    return out


def index_agenda_hits(data_dir: Path = DATA) -> tuple[list[dict], set[str]] | None:
    """(hits, document URLs indexed) from the incremental document index, or None if there is none yet."""
    try:
        from .state import DocIndex
    except ImportError:
        return None
    root = data_dir / "state" / "docs"
    if not root.exists() or not any(root.rglob("*.jsonl")):
        return None
    index = DocIndex(root)
    return index.current_hits(), index.urls()


def other_hits(data_dir: Path = DATA, include_states: set[str] | None = None) -> list[dict]:
    """data/agenda_hits_<st>.json (other states) and data/sources/*_hits.json."""
    out = []
    for p in sorted(data_dir.glob("agenda_hits_*.json")):
        m = _STATE_FILE.match(p.name)
        if not m:
            continue  # agenda_hits_ma_all.json, agenda_hits_northeast.json (probe) ...
        st = m.group(1).upper()
        if include_states is not None and st not in include_states:
            continue
        for h in _hits_of(_load(p)):
            out.append({**h, "state": (h.get("state") or st).upper(), "source": h.get("source") or "agenda"})
    for p in sorted((data_dir / "sources").glob("*_hits.json")):
        default_source = p.name[: -len("_hits.json")]
        for h in _hits_of(_load(p)):
            out.append({**h, "state": (h.get("state") or "MA").upper(),
                        "source": h.get("source") or default_source})
    return out


# ----------------------------------------------------------------------- shaping
def _days_before(first_seen: str | None, meeting_date: str | None) -> float | None:
    if not (first_seen and meeting_date):
        return None
    try:
        seen = datetime.fromisoformat(first_seen)
        if seen.tzinfo is None:
            seen = seen.replace(tzinfo=timezone.utc)
        meeting = datetime.fromisoformat(meeting_date[:10]).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return round((meeting - seen).total_seconds() / 86400, 1)


def normalize(h: dict, counties: dict) -> dict:
    """One hit in exactly the contract's shape and key order."""
    state = (h.get("state") or "MA").upper()
    snippet = (h.get("snippet") or "")[:240]
    out = {
        "id": h.get("id") or hit_id(h.get("source_url") or "", snippet),
        "state": state,
        "town": h.get("town"),
        "county": h.get("county") or counties.get((state, (h.get("town") or "").lower())),
        "board": h.get("board"),
        "board_key": h.get("board_key"),
        "meeting_date": h.get("meeting_date"),
        "topics": list(h.get("topics") or []),
        "snippet": snippet,
        "source_url": h.get("source_url"),
        **({"doc_url": h["doc_url"]} if h.get("doc_url") else {}),  # the live file, when the town re-posted the agenda
        "listing_url": h.get("listing_url"),
        "document_title": h.get("document_title"),
        "text_source": h.get("text_source"),
        "first_seen": h.get("first_seen"),
        "days_before_meeting": h.get("days_before_meeting"),
        "source": h.get("source") or "agenda",
    }
    if out["days_before_meeting"] is None:
        out["days_before_meeting"] = _days_before(out["first_seen"], out["meeting_date"])
    if out["days_before_meeting"] is None:
        del out["days_before_meeting"]  # undated: omit rather than null (consumers compare it to 0)
    return out


def _window_date(h: dict) -> str | None:
    return (h.get("meeting_date") or (h.get("first_seen") or "")[:10]) or None


def _sort_key(h: dict):
    return (h.get("meeting_date") or "", h["state"], h.get("town") or "", h.get("board") or "", h["id"])


def archive_hits(hits: list[dict], archive_dir: Path) -> int:
    """Append hits (older than the window) to hits_archive/YYYY-MM.jsonl by meeting
    month, skipping ids already archived. Files stay sorted for small diffs."""
    by_month: dict[str, list[dict]] = {}
    for h in hits:
        by_month.setdefault((_window_date(h) or "undated")[:7], []).append(h)
    added = 0
    for month, new in sorted(by_month.items()):
        path = archive_dir / f"{month}.jsonl"
        existing = {}
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    rec = json.loads(line)
                    existing[rec["id"]] = rec
        before = len(existing)
        for h in new:
            existing.setdefault(h["id"], h)
        if len(existing) == before:
            continue
        added += len(existing) - before
        archive_dir.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r, ensure_ascii=False, separators=(",", ":"))
                 for r in sorted(existing.values(), key=_sort_key)]
        tmp = path.with_suffix(".jsonl.tmp")
        tmp.write_text("\n".join(lines) + "\n")
        tmp.replace(path)
    return added


def build(data_dir: Path = DATA, today: date | None = None, archive: bool = True,
          agenda_hits: list[dict] | None = None, indexed_urls: set[str] | None = None,
          towns: list[dict] | None = None) -> dict:
    """`towns`: the town rows to report (default: load_towns(data_dir), i.e. every
    non-gated state); a test run of gated states passes its own rows."""
    today = today or datetime.now(timezone.utc).date()
    start, end = today - timedelta(days=WINDOW_DAYS), today + timedelta(days=WINDOW_DAYS)
    towns = load_towns(data_dir) if towns is None else towns
    counties = county_lookup(towns)
    if agenda_hits is None:
        from_index = index_agenda_hits(data_dir)
        if from_index is not None:
            agenda_hits, indexed_urls = from_index
        else:
            agenda_hits = legacy_agenda_hits(data_dir)
    # The index is authoritative for every document it holds (its hits are re-matched
    # and deduplicated); per-state hit files from other workstreams contribute hits
    # only from documents the index does not hold (e.g. older than the daily window).
    indexed_urls = set(indexed_urls or ()) | {h.get("source_url") for h in agenda_hits}
    raw = agenda_hits + [h for h in other_hits(data_dir)
                         if not (h["source"] == "agenda" and h.get("source_url") in indexed_urls)]

    seen: dict[str, dict] = {}
    for h in raw:
        n = normalize(h, counties)
        if n["source_url"] and n["snippet"]:
            seen.setdefault(n["id"], n)
    current, old = [], []
    for h in seen.values():
        d = _window_date(h)
        if d is not None and d < start.isoformat():
            old.append(h)
        elif d is None or d <= end.isoformat():
            current.append(h)
    if archive and old:
        n = archive_hits(old, data_dir / "state" / "hits_archive")
        log.info("archived %d hits older than %s", n, start)
    current.sort(key=_sort_key, reverse=True)
    monitored = towns_monitored(towns)
    states = sorted(set(monitored) | {h["state"] for h in current})
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "states": states,
        "towns_monitored": monitored,
        "hits": current,
    }


# -------------------------------------------------------------------- validation
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(doc: dict) -> list[str]:
    """Return contract violations (empty list = valid)."""
    errs = []
    for k in ("generated", "window", "states", "towns_monitored", "hits"):
        if k not in doc:
            errs.append(f"missing top-level key {k}")
    if errs:
        return errs
    w = doc["window"]
    if not (_ISO_DATE.match(w.get("start", "")) and _ISO_DATE.match(w.get("end", ""))):
        errs.append("window start/end must be YYYY-MM-DD")
    ids = set()
    for i, h in enumerate(doc["hits"]):
        where = f"hits[{i}]"
        extra = set(h) - set(FIELDS)
        missing = set(FIELDS) - set(h) - OPTIONAL_FIELDS
        if extra:
            errs.append(f"{where}: unexpected keys {sorted(extra)}")
        if missing:
            errs.append(f"{where}: missing keys {sorted(missing)}")
        if not re.fullmatch(r"[0-9a-f]{12}", h.get("id") or ""):
            errs.append(f"{where}: bad id {h.get('id')!r}")
        elif h["id"] in ids:
            errs.append(f"{where}: duplicate id {h['id']}")
        ids.add(h.get("id"))
        if h.get("source") == "agenda" and h.get("id") != hit_id(h.get("source_url") or "", h.get("snippet") or ""):
            errs.append(f"{where}: id is not sha1(source_url|snippet)[:12]")
        if h.get("state") not in doc["states"]:
            errs.append(f"{where}: state {h.get('state')!r} not in states")
        if h.get("board_key") not in BOARD_KEYS and h.get("source") == "agenda":
            errs.append(f"{where}: board_key {h.get('board_key')!r}")
        bad_topics = set(h.get("topics") or []) - TOPIC_KEYS
        if bad_topics or not h.get("topics"):
            errs.append(f"{where}: topics {h.get('topics')}")
        if len(h.get("snippet") or "") > 240:
            errs.append(f"{where}: snippet longer than 240 chars")
        if h.get("meeting_date") is not None and not _ISO_DATE.match(h["meeting_date"]):
            errs.append(f"{where}: meeting_date {h['meeting_date']!r}")
        if h.get("source") == "agenda" and h.get("text_source") not in TEXT_SOURCES:
            errs.append(f"{where}: text_source {h.get('text_source')!r}")
        if not h.get("first_seen"):
            errs.append(f"{where}: no first_seen")
    return errs


def write(doc: dict, path: Path) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    tmp.replace(path)


def rebuild(data_dir: Path = DATA, today: date | None = None, archive: bool = True,
            agenda_hits: list[dict] | None = None, indexed_urls: set[str] | None = None,
            towns: list[dict] | None = None, out_name: str = "hits_current.json") -> dict:
    """Build, validate and write data/hits_current.json (or `out_name` in `data_dir`);
    returns the document."""
    doc = build(data_dir, today, archive, agenda_hits, indexed_urls, towns)
    errs = validate(doc)
    if errs:
        raise ValueError(f"{out_name} failed validation ({len(errs)}): " + "; ".join(errs[:10]))
    write(doc, data_dir / out_name)
    return doc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="only validate data/hits_current.json")
    p.add_argument("--legacy", action="store_true", help="ignore the state index; use agenda_hits_ma_all.json")
    p.add_argument("--no-archive", action="store_true")
    p.add_argument("--data-dir", type=Path, default=DATA)
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.check:
        errs = validate(json.loads((args.data_dir / "hits_current.json").read_text()))
        for e in errs[:50]:
            print(e)
        print("valid" if not errs else f"{len(errs)} problems")
        return 1 if errs else 0
    agenda = legacy_agenda_hits(args.data_dir) if args.legacy else None
    doc = rebuild(args.data_dir, archive=not args.no_archive, agenda_hits=agenda)
    by_state: dict[str, int] = {}
    for h in doc["hits"]:
        by_state[h["state"]] = by_state.get(h["state"], 0) + 1
    print(f"wrote {args.data_dir / 'hits_current.json'}: {len(doc['hits'])} hits {by_state}, "
          f"window {doc['window']['start']}..{doc['window']['end']}, towns {doc['towns_monitored']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
