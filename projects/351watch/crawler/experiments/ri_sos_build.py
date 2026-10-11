#!/usr/bin/env python3
"""Rhode Island via the Secretary of State Open Meetings portal (adapter: watch351/adapters/ri_sos.py).

Glue code only: it imports the watch351 package (PoliteFetcher: 351WatchBot UA,
robots.txt, 1 req/s/host, cache; crawl.scan_document; the keyword matcher) and
does not modify it.

    cd crawler
    python3 experiments/ri_sos_build.py discover        # -> data/towns_ri.json (all 39 municipalities)
    python3 experiments/ri_sos_build.py crawl           # -> data/agenda_hits_ri.json (45 days back, 90 ahead)
    python3 experiments/ri_sos_build.py crawl --towns Hopkinton,Exeter --days-back 30

Inputs: data/ri_census_sub_est2024.csv (Census Vintage 2024 subcounty estimates for
RI, county and population; hand-downloaded like the MA file because a strict parse
of www2.census.gov's robots.txt groups "User-agent: *" with "Disallow: /").

data/agenda_hits_ri.json carries hits in the ARCHITECTURE.md shape plus RI extras
(meeting_time, notice/agenda filed times, lead times) and a `lead_time` block
computed from the portal's filed timestamps.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from watch351.adapters.ri_sos import (ET, RISOSAdapter, business_hours_between,  # noqa: E402
                                      dashboard_url)
from watch351.crawl import scan_document, town_configs  # noqa: E402
from watch351.fetch import FetchError, PoliteFetcher  # noqa: E402
from watch351.models import Window  # noqa: E402

DATA = ROOT.parent / "data"
TOWNS_FILE = DATA / "towns_ri.json"
HITS_FILE = DATA / "agenda_hits_ri.json"
CENSUS_FILE = DATA / "ri_census_sub_est2024.csv"
BOARD_KEYS = ["planning_board", "zoning_board_of_appeals", "conservation_commission", "select_board", "town_meeting"]
log = logging.getLogger("ri_sos_build")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def census() -> dict[str, dict]:
    rows = list(csv.DictReader(CENSUS_FILE.open(encoding="latin-1")))
    counties = {r["COUNTY"]: r["NAME"].replace(" County", "") for r in rows if r["SUMLEV"] == "050"}
    out = {}
    for r in rows:
        if r["SUMLEV"] != "061":
            continue
        name = re.sub(r"\s+(town|city)$", "", r["NAME"])
        out[name.lower()] = {"county": counties[r["COUNTY"]], "pop_2020": int(r["ESTIMATESBASE2020"]),
                             "pop_2024_est": int(r["POPESTIMATE2024"]),
                             "census_kind": r["NAME"].rsplit(" ", 1)[-1]}
    return out


# --------------------------------------------------------------------------- discover
def _merge_evidence(evs: list[dict]) -> dict:
    """One board_evidence entry per board key (MA shape), listing every portal body."""
    evs = sorted(evs, key=lambda e: (-(e["n_recent"]), e["entity_id"]))
    latest = max((e["latest"] for e in evs if e["latest"]), default=None)
    return {"board": " + ".join(e["board"] for e in evs), "source": "ri_sos", "url": evs[0]["url"],
            "n_recent": sum(e["n_recent"] for e in evs), "latest": latest,
            "n_past_90": sum(e["n_past_90"] for e in evs),
            "bodies": [{k: e[k] for k in ("entity_id", "entity_name", "n_meetings_total", "n_recent", "latest")}
                       for e in evs]}


def cmd_discover(args, fetcher: PoliteFetcher) -> None:
    ad = RISOSAdapter(fetcher)
    pops = census()
    munis = ad.municipalities()
    wanted = {t.strip().lower() for t in args.towns.split(",")} if args.towns else None
    old = {t["town"]: t for t in json.loads(TOWNS_FILE.read_text())["towns"]} if TOWNS_FILE.exists() else {}
    rows = []
    for m in munis:
        if wanted and m["town"].lower() not in wanted:
            if m["town"] in old:
                rows.append(old[m["town"]])
            continue
        cfg = {"town": m["town"], "sos_entity_id": m["sos_entity_id"]}
        reason = None
        try:
            website = ad.website(m["sos_entity_id"])
            listings = ad.discover(cfg)
        except (FetchError, RuntimeError) as e:
            website, listings, reason = None, [], f"portal error: {e}"
            cfg["_discovery"] = {"evidence": {}, "stale": {}, "untracked_bodies": []}
        disc = cfg["_discovery"]
        found = sorted({l["board_key"] for l in listings})
        c = pops.get(m["town"].lower(), {})
        council = next((l["board"] for l in listings if l["board_key"] == "select_board"),
                       f"{m['kind'].title()} Council")
        ftm = [l["board"] for l in listings if l["board_key"] == "town_meeting"]
        rows.append({
            "town": m["town"], "state": "RI", "website": website, "county": c.get("county"),
            "kind": m["kind"], "pop_2020": c.get("pop_2020"), "pop_2024_est": c.get("pop_2024_est"),
            "legislative_body": council + (f" + {ftm[0]}" if ftm else ""),
            "has_town_meeting": bool(ftm), "final_url": website,
            "cms": [], "platforms": ["ri_sos"], "platform": "ri_sos", "warrants_found": False,
            "status": "automated" if listings else "not_automated",
            "reason_code": None if listings else ("portal_error" if reason else "no_tracked_bodies"),
            "reason": None if listings else (reason or "no tracked board has filed a meeting in two years"),
            "automated": bool(listings),
            "sos_entity_id": m["sos_entity_id"], "sos_entity_name": m["sos_entity_name"],
            "sos_dashboard_url": dashboard_url(m["sos_entity_id"]),
            "listings": listings,
            "boards_found": found,
            "boards_missing": [k for k in BOARD_KEYS if k not in found],
            "board_evidence": {k: _merge_evidence(v) for k, v in sorted(disc["evidence"].items())},
            "board_stale": {k: [{x: e[x] for x in ("entity_id", "entity_name", "latest", "note")} for e in v]
                            for k, v in sorted(disc["stale"].items())},
            "vendors": {}, "robots_blocked": [],
            "notes": [f"{len(disc['untracked_bodies'])} other public bodies filed under "
                      f"{m['sos_entity_name']} on the portal (not tracked)"],
            "untracked_bodies": disc["untracked_bodies"],
            "discovered_at": now_iso(),
        })
        log.info("%-18s %d listings %s", m["town"], len(listings), found)
    rows.sort(key=lambda r: r["town"])
    doc = {
        "_about": ("351 Watch Rhode Island: all 39 municipalities via the RI Secretary of State Open Meetings "
                   "portal (https://opengov.sos.ri.gov), where every public body must file notices and agendas "
                   "48 hours ahead (R.I. Gen. Laws 42-46-6). platform 'ri_sos' -> watch351/adapters/ri_sos.py. "
                   "Each listing is one portal public body (entity_id); board names are the portal's minus the town. "
                   "Built by `python3 experiments/ri_sos_build.py discover`."),
        "generated": now_iso(), "state": "RI",
        "source": "https://opengov.sos.ri.gov/GOVDirectoryPublic/OfficialSearch?topmenuId=105&page=IdxMuni",
        "boards_tracked": len(BOARD_KEYS),
        "board_key_mapping": {"Town Council / City Council": "select_board",
                              "Planning Board / Planning Commission / City Plan Commission": "planning_board",
                              "Zoning Board of Review": "zoning_board_of_appeals",
                              "Conservation Commission": "conservation_commission",
                              "Financial Town Meeting / Town Meeting": "town_meeting"},
        "evidence_rule": ("a portal body is listed if it has a non-cancelled meeting filed in the last 730 days or "
                          "upcoming (RI bodies must file every meeting on the portal, so a quiet body is still "
                          "covered when it next meets); n_recent counts meetings within 120 days either side"),
        "count": len(rows), "automated": sum(r["automated"] for r in rows),
        "towns": rows,
    }
    save(TOWNS_FILE, doc)
    print(f"wrote {TOWNS_FILE}: {doc['count']} municipalities, {doc['automated']} automated, "
          f"{sum(len(r['listings']) for r in rows)} listings")
    print(f"fetcher: {fetcher.stats}")


# --------------------------------------------------------------------------- crawl
def hit_id(source_url: str, snippet: str) -> str:
    return hashlib.sha1(f"{source_url}|{snippet}".encode("utf-8")).hexdigest()[:12]


def pct(xs: list[float], q: float) -> float | None:
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 2)


def dist(xs: list[float]) -> dict:
    return {"n": len(xs), "min": round(min(xs), 2) if xs else None, "p10": pct(xs, .1), "p25": pct(xs, .25),
            "median": pct(xs, .5), "p75": pct(xs, .75), "p90": pct(xs, .9),
            "max": round(max(xs), 2) if xs else None}


def lead_time_stats(meetings: list[dict], hits: list[dict], now: datetime) -> dict:
    """Lead times from the portal's own timestamps, for meetings already held (their
    filings are complete). notice = 'Filed on'; first/last agenda = earliest/latest
    'Agenda filed on'. Business hours exclude weekends and RI holidays (42-46-6(b))."""
    held = [m for m in meetings if m["meeting_start"] <= now and m["filed_on"]]
    rows = []
    for m in held:
        files = [f["filed_at"] for f in m["agendas"] if f["filed_at"]]
        first, last = (min(files), max(files)) if files else (None, None)
        rows.append({
            "board_key": m["board_key"], "town": m["town"], "board": m["board"],
            "meeting_date": m["meeting_date"].isoformat(), "meeting_url": m["listing_url"],
            "notice_days": (m["meeting_start"] - m["filed_on"]).total_seconds() / 86400,
            "notice_bh": business_hours_between(m["filed_on"], m["meeting_start"]),
            "first_days": (m["meeting_start"] - first).total_seconds() / 86400 if first else None,
            "first_bh": business_hours_between(first, m["meeting_start"]) if first else None,
            # strict reading of 42-46-6(b): 48 business hours "before the date of the meeting"
            "first_bh_day": business_hours_between(first, m["meeting_start"].replace(hour=0, minute=0)) if first else None,
            "notice_bh_day": business_hours_between(m["filed_on"], m["meeting_start"].replace(hour=0, minute=0)),
            "last_bh": business_hours_between(last, m["meeting_start"]) if last else None,
            "amended": bool(files and len(set(files)) > 1),
            "emergency": m["emergency"], "public_announcement": m["public_announcement"],
        })
    def summary(rs: list[dict]) -> dict:
        firsts = [r for r in rs if r["first_days"] is not None]
        return {
            "meetings": len(rs),
            "with_agenda_file": len(firsts),
            "notice_filed_days_before": dist([r["notice_days"] for r in rs]),
            "first_agenda_days_before": dist([r["first_days"] for r in firsts]),
            "first_agenda_business_hours_before": dist([r["first_bh"] for r in firsts]),
            "share_first_agenda_ge_48_business_hours": round(sum(r["first_bh"] >= 48 for r in firsts) / len(firsts), 3) if firsts else None,
            "share_first_agenda_ge_48_business_hours_before_meeting_day": round(sum(r["first_bh_day"] >= 48 for r in firsts) / len(firsts), 3) if firsts else None,
            "share_notice_ge_48_business_hours_before_meeting_day": round(sum(r["notice_bh_day"] >= 48 for r in rs) / len(rs), 3) if rs else None,
            "first_agenda_under_48_business_hours": sum(r["first_bh"] < 48 for r in firsts),
            "share_first_agenda_ge_5_days": round(sum(r["first_days"] >= 5 for r in firsts) / len(firsts), 3) if firsts else None,
            "share_first_agenda_ge_7_days": round(sum(r["first_days"] >= 7 for r in firsts) / len(firsts), 3) if firsts else None,
            "meetings_with_later_agenda_versions": sum(r["amended"] for r in firsts),
            "later_version_filed_inside_48_business_hours": sum(r["amended"] and r["last_bh"] < 48 for r in firsts),
            "emergency_meetings": sum(r["emergency"] for r in rs),
        }
    late = sorted((r for r in rows if r["first_bh"] is not None and r["first_bh"] < 48 and not r["emergency"]),
                  key=lambda r: r["first_bh"])
    hit_leads = {}
    for h in hits:
        if h.get("days_filed_before_meeting") is not None and datetime.fromisoformat(h["meeting_start"]) <= now:
            hit_leads.setdefault((h["source_url"]), h["days_filed_before_meeting"])
    return {
        "_about": ("Meetings of tracked RI boards already held in the crawl window. Days are measured from the "
                   "portal timestamp to the meeting's scheduled start (ET). Business hours exclude Saturdays, "
                   "Sundays and R.I. Gen. Laws 25-1-1 holidays, as the 48-hour rule in 42-46-6(b) does."),
        "all": summary(rows),
        "by_board_key": {k: summary([r for r in rows if r["board_key"] == k]) for k in BOARD_KEYS
                         if any(r["board_key"] == k for r in rows)},
        "hit_documents_agenda_filed_days_before": dist(list(hit_leads.values())),
        "first_agenda_under_48_business_hours_examples": [
            {k: (round(r[k], 1) if isinstance(r[k], float) else r[k])
             for k in ("town", "board", "meeting_date", "first_bh", "first_days", "meeting_url")} for r in late[:15]],
        "towns_median_first_agenda_days": {
            t: pct([r["first_days"] for r in rows if r["town"] == t and r["first_days"] is not None], .5)
            for t in sorted({r["town"] for r in rows})},
    }


def crawl_one(ad: RISOSAdapter, fetcher: PoliteFetcher, cfg: dict, window: Window) -> dict:
    res = {"town": cfg["town"], "meetings": [], "docs": 0, "scanned": 0, "no_text": 0, "ocr": 0,
           "hits": [], "errors": [], "doc_records": []}
    try:
        meetings = ad.meetings(cfg, window)
    except (FetchError, RuntimeError) as e:
        res["errors"].append(f"listing: {e}")
        return res
    res["errors"].extend(cfg.get("_errors", []))
    res["meetings"] = meetings
    docs = ad.agenda_docs(cfg, meetings)
    res["docs"] = len(docs)
    for doc in docs:
        try:
            hits, ex = scan_document(fetcher, doc)
        except FetchError as e:
            res["errors"].append(str(e)[:200])
            continue
        res["scanned"] += 1
        res["no_text"] += int(ex.scanned)
        res["ocr"] += int(ex.ocr)
        res["doc_records"].append({"url": doc.url, "kind": "ocr" if ex.ocr else ex.kind, "pages": ex.pages,
                                   "scanned": ex.scanned, "hits": len(hits)})
        for h in hits:
            h.update({k: doc.extra[k] for k in ("meeting_id", "meeting_time", "meeting_start", "notice_filed_at",
                                                "agenda_filed_at", "amended", "public_announcement")})
        res["hits"].extend(hits)
    log.info("%s: %d meetings, %d agenda files, %d scanned, %d raw hits", cfg["town"], len(meetings),
             len(docs), res["scanned"], len(res["hits"]))
    return res


def cmd_crawl(args, fetcher: PoliteFetcher) -> None:
    towns_doc = json.loads(TOWNS_FILE.read_text())
    towns = towns_doc["towns"]
    if args.towns:
        wanted = {t.strip().lower() for t in args.towns.split(",")}
        towns = [t for t in towns if t["town"].lower() in wanted]
    county = {t["town"]: t.get("county") for t in towns}
    today = date.fromisoformat(args.today) if args.today else date.today()
    window = Window(today - timedelta(days=args.days_back), today + timedelta(days=args.days_ahead))
    ad = RISOSAdapter(fetcher)
    cfgs = [c for t in towns for c in town_configs(t)]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:   # one host: the fetcher keeps it at 1 req/s
        results = list(pool.map(lambda c: crawl_one(ad, fetcher, c, window), cfgs))

    now = datetime.now(ET)
    seen, hits = set(), []
    for r in results:
        for h in r["hits"]:
            ctx = h.pop("_context")
            key = (h["town"], h["board"], h["meeting_date"], ctx)
            if key in seen:
                continue
            seen.add(key)
            ts = fetcher.cached_at(h["source_url"])
            first_seen = datetime.fromtimestamp(ts, timezone.utc) if ts else datetime.now(timezone.utc)
            meeting_day = datetime.fromisoformat(h["meeting_date"]).replace(tzinfo=timezone.utc)
            start = datetime.fromisoformat(h["meeting_start"])
            filed = datetime.fromisoformat(h["agenda_filed_at"]) if h["agenda_filed_at"] else None
            hits.append({
                "id": hit_id(h["source_url"], h["snippet"]), "state": "RI", "town": h["town"],
                "county": county.get(h["town"]), "board": h["board"], "board_key": h["board_key"],
                "meeting_date": h["meeting_date"], "topics": h["topics"], "snippet": h["snippet"],
                "source_url": h["source_url"], "listing_url": h["listing_url"],
                "document_title": h["document_title"], "text_source": h["text_source"],
                "first_seen": first_seen.isoformat(timespec="seconds"),
                # contract convention (as MA): first_seen -> start of the meeting day, UTC
                "days_before_meeting": round((meeting_day - first_seen).total_seconds() / 86400, 1),
                "source": "agenda",
                # RI extras from the portal's own timestamps
                "platform": "ri_sos", "meeting_id": h["meeting_id"], "meeting_time": h["meeting_time"],
                "meeting_start": h["meeting_start"],
                "notice_filed_at": h["notice_filed_at"], "agenda_filed_at": h["agenda_filed_at"],
                "days_filed_before_meeting": round((start - filed).total_seconds() / 86400, 2) if filed else None,
                "business_hours_filed_before_meeting": round(business_hours_between(filed, start), 1) if filed else None,
                "amended_agenda": h["amended"], "public_announcement": h["public_announcement"],
            })
    hits.sort(key=lambda h: (h["meeting_date"] or "", h["town"], h["board"], h["id"]), reverse=True)

    meetings = [m for r in results for m in r["meetings"]]
    topic_counts = Counter(t for h in hits for t in h["topics"])
    by_town = defaultdict(lambda: {"meetings": 0, "agenda_files": 0, "documents_scanned": 0,
                                   "documents_without_text_layer": 0, "documents_ocr": 0, "errors": []})
    for r in results:
        b = by_town[r["town"]]
        b["meetings"] += len(r["meetings"])
        b["agenda_files"] += r["docs"]
        b["documents_scanned"] += r["scanned"]
        b["documents_without_text_layer"] += r["no_text"]
        b["documents_ocr"] += r["ocr"]
        b["errors"].extend(r["errors"])
    town_rows = []
    for t in towns:
        b = by_town.get(t["town"], {"meetings": 0, "agenda_files": 0, "documents_scanned": 0,
                                    "documents_without_text_layer": 0, "documents_ocr": 0, "errors": []})
        town_rows.append({"town": t["town"], "platform": "ri_sos", "automated": t["automated"],
                          "boards": sorted({l["board_key"] for l in t["listings"]}),
                          "bodies": len(t["listings"]), **{k: v for k, v in b.items() if k != "errors"},
                          "hits": sum(1 for h in hits if h["town"] == t["town"]),
                          "hits_upcoming": sum(1 for h in hits if h["town"] == t["town"] and h["meeting_date"] >= today.isoformat()),
                          "errors": b["errors"][:10], "reason": t.get("reason")})
    report = {
        "generated": now_iso(),
        "source": "RI Secretary of State Open Meetings portal, https://opengov.sos.ri.gov (adapter ri_sos)",
        "state": "RI",
        "window": {"start": window.start.isoformat(), "end": window.end.isoformat()},
        "towns_attempted": len(towns),
        "towns_automated": sum(t["automated"] for t in towns),
        "bodies_crawled": sum(len(t["listings"]) for t in towns),
        "meetings_in_window": len(meetings),
        "meetings_held": sum(m["meeting_start"] <= now for m in meetings),
        "meetings_upcoming_filed": sum(m["meeting_start"] > now for m in meetings),
        "meetings_without_agenda_file": sum(not m["agendas"] for m in meetings),
        "meetings_by_board_key": dict(Counter(m["board_key"] for m in meetings).most_common()),
        "agenda_files_listed": sum(r["docs"] for r in results),
        "documents_scanned": sum(r["scanned"] for r in results),
        "documents_without_text_layer": sum(r["no_text"] for r in results),
        "documents_ocr": sum(r["ocr"] for r in results),
        "documents_by_kind": dict(Counter(d["kind"] for r in results for d in r["doc_records"])),
        "hits_total": len(hits),
        "hits_upcoming": sum(h["meeting_date"] >= today.isoformat() for h in hits),
        "hits_by_topic": dict(topic_counts.most_common()),
        "hits_by_board_key": dict(Counter(h["board_key"] for h in hits).most_common()),
        "towns_with_hits": len({h["town"] for h in hits}),
        "lead_time": lead_time_stats(meetings, hits, now),
        "fetcher": dict(fetcher.stats),
        "towns": town_rows,
        "hits": hits,
    }
    save(Path(args.out), report)
    print(f"towns {report['towns_attempted']} (automated {report['towns_automated']}), bodies {report['bodies_crawled']}, "
          f"meetings {report['meetings_in_window']} (held {report['meetings_held']}), agenda files {report['agenda_files_listed']}, "
          f"scanned {report['documents_scanned']} (no text {report['documents_without_text_layer']}, ocr {report['documents_ocr']}), "
          f"hits {len(hits)} (upcoming {report['hits_upcoming']})")
    for k, v in report["hits_by_topic"].items():
        print(f"  {k:<26} {v}")
    print(json.dumps(report["lead_time"]["all"], indent=1))
    print(f"fetcher: {fetcher.stats}\nwrote {args.out}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["discover", "crawl"])
    p.add_argument("--towns")
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=90)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--offline", action="store_true", help="serve only from crawler/.cache (re-match, recompute stats)")
    p.add_argument("--today", help="pin the window's reference date (YYYY-MM-DD), e.g. to re-run a crawl offline")
    p.add_argument("--out", default=str(HITS_FILE))
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    # opengov.sos.ri.gov rate-limits (Cloudflare 429 at ~1 req/s): space every request, agenda files included
    fetcher = PoliteFetcher(offline=args.offline, min_interval=RISOSAdapter.min_interval)
    {"discover": cmd_discover, "crawl": cmd_crawl}[args.command](args, fetcher)
    return 0


if __name__ == "__main__":
    sys.exit(main())
