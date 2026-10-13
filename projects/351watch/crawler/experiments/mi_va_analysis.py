"""Analysis for the Michigan / Virginia test (used by mi_va_test.py analyze | sample | rss).

Everything here reads local files (towns_*.json, data/test/, the fetch cache) except `rss`,
which fetches CivicPlus AgendaCenter RSS feeds (/RSSFeed.aspx, allowed by robots.txt) through
PoliteFetcher to get posting times.
"""

from __future__ import annotations

import json
import re
import statistics
import subprocess
import tempfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from watch351.adapters import REGISTRY
from watch351.adapters.civicclerk import CivicClerkAdapter
from watch351.crawl import town_configs
from watch351.fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from watch351.keywords import clean_text
from watch351.models import Window
from watch351 import extract as X

CRAWLER = Path(__file__).resolve().parent.parent
DATA = CRAWLER.parent / "data"
TEST = DATA / "test"
STATES = ("MI", "VA")
BLOCKED = {"robots_disallow": "robots.txt", "bot_challenge": "Cloudflare challenge", "waf_block": "WAF 403",
           "vendor_blocked": "vendor", "crawl_delay_exceeds_cap": "crawl-delay > 10 s",
           "documents_blocked": "documents robots/403"}
NO_AGENDAS = {"no_website", "no_agendas_found", "no_recent_agendas", "js_only", "document_store", "website_mismatch"}
ERRORS = {"unreachable", "http_error", "discovery_error"}


def load_rows(st: str) -> list[dict]:
    return json.loads((DATA / f"towns_{st.lower()}.json").read_text())["towns"]


def load_docs(st: str) -> list[dict]:
    out = []
    for p in sorted((TEST / "state" / "docs" / st).glob("*.jsonl")):
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out


def median(xs):
    return round(statistics.median(xs), 1) if xs else None


def dist(xs):
    if not xs:
        return {"n": 0}
    xs = sorted(xs)
    q = lambda f: xs[min(len(xs) - 1, int(f * (len(xs) - 1) + 0.5))]  # noqa: E731
    return {"n": len(xs), "median": round(statistics.median(xs), 1), "p10": round(q(0.1), 1),
            "p90": round(q(0.9), 1), "share_ge_3d": round(sum(x >= 3 for x in xs) / len(xs), 2),
            "share_negative": round(sum(x < 0 for x in xs) / len(xs), 2)}


def run_reports() -> dict:
    out = {}
    for p in sorted((TEST / "runs").glob("run_*.json")):
        out[p.stem.replace("run_", "")] = json.loads(p.read_text())
    return out


# ------------------------------------------------------------------ coverage
def coverage(st: str, rows: list[dict], docs: list[dict], health: dict, hits_doc: dict | None = None) -> dict:
    ok_by_town_board = defaultdict(set)
    for d in docs:
        if d.get("status") == "ok":
            ok_by_town_board[d["town"]].add(d.get("board_key"))
    per = []
    for r in rows:
        tracked = r.get("boards_tracked") or ["select_board", "planning_board", "zoning_board_of_appeals"]
        read_boards = sorted(ok_by_town_board.get(r["town"], set()) & set(tracked))
        h = health.get(f"{st}:{r['town']}", {})
        if r.get("automated") and read_boards:
            cls = "readable"
        elif r.get("automated") and h.get("status") == "failed":
            cls = "crawl_error"
        elif r.get("automated"):
            cls = "automated_no_docs_in_window"
        elif r.get("reason_code") in BLOCKED:
            cls = "blocked"
        elif r.get("reason_code") in ERRORS:
            cls = "error_unreachable"
        else:
            cls = "no_agendas_online"
        per.append({"town": r["town"], "kind": r.get("kind"), "group": r.get("selection_group"), "class": cls,
                    "reason_code": r.get("reason_code"), "platform": r.get("platform"),
                    "boards_tracked": tracked, "boards_read": read_boards,
                    "boards_automated": sorted({l["board_key"] for l in r.get("listings") or []}),
                    "reason": (r.get("reason") or "")[:200], "health": h.get("status")})
    by_kind = {}
    for kind in sorted({p["kind"] for p in per}):
        ps = [p for p in per if p["kind"] == kind]
        c = Counter(p["class"] for p in ps)
        bodies = sum(len(p["boards_tracked"]) for p in ps)
        bodies_read = sum(len(p["boards_read"]) for p in ps)
        by_kind[kind] = {"attempted": len(ps), **dict(c),
                         "readable_share": round(c["readable"] / len(ps), 3),
                         "bodies_targeted": bodies, "bodies_readable": bodies_read,
                         "bodies_readable_share": round(bodies_read / bodies, 3) if bodies else None,
                         "blocked_how": dict(Counter(f"{BLOCKED.get(p['reason_code'], p['reason_code'])}"
                                                     f"{': ' + p['platform'] if p['reason_code'] == 'vendor_blocked' else ''}"
                                                     for p in ps if p["class"] == "blocked")),
                         "no_agendas_how": dict(Counter(p["reason_code"] for p in ps if p["class"] == "no_agendas_online")),
                         "platforms_readable": dict(Counter(p["platform"] for p in ps if p["class"] == "readable"))}
    # Michigan: townships not readable themselves whose county planning commission is readable see
    # their zoning amendments through the county's MCL 125.3307 review (not moratoria / special land uses).
    county_ok = {p["town"].replace(" County", "") for p in per if p["kind"] == "county" and p["class"] == "readable"}
    county_of = {r["town"]: r.get("county") for r in rows}
    if county_ok and st == "MI":
        twp = [p for p in per if p["kind"] == "township"]
        via = [p["town"] for p in twp if p["class"] != "readable" and county_of.get(p["town"]) in county_ok]
        by_kind.setdefault("township", {})["indirect_via_county_planning_commission"] = len(via)
        by_kind["township"]["readable_or_county_reviewed_share"] = round(
            (sum(p["class"] == "readable" for p in twp) + len(via)) / len(twp), 3) if twp else None
        by_kind["township"]["counties_with_readable_planning_commission"] = sorted(county_ok)
    if st == "MI" and hits_doc:
        # townships reached through county items in this window: a county planning commission hit
        # filed under a target township (attribution.attribute / split_items)
        # rows, not names: four township names occur in two counties each (Brookfield, Bingham...)
        twp_rows = [p for p in per if p["kind"] == "township"]
        targets = {p["town"] for p in twp_rows}
        direct = {p["town"] for p in twp_rows if p["class"] == "readable"}
        named = {h["town"] for h in hits_doc["hits"]
                 if h["state"] == st and "county" in (h.get("board") or "").lower() and h["town"] in targets}
        tw = by_kind.setdefault("township", {})
        n = len(twp_rows) or 1
        n_direct = sum(p["class"] == "readable" for p in twp_rows)
        n_either = sum(p["class"] == "readable" or p["town"] in named for p in twp_rows)
        tw["direct_readable"] = n_direct
        tw["direct_readable_share"] = round(n_direct / n, 3)
        tw["via_county_items"] = len(named)
        tw["via_county_items_towns"] = sorted(named)
        tw["via_county_items_not_direct"] = sorted(named - direct)
        tw["direct_or_via_county_items"] = n_either
        tw["direct_or_via_county_items_share"] = round(n_either / n, 3)
        # the per-township coverage field the site shows (attribution.coverage_modes)
        modes = Counter(r.get("coverage") or "none" for r in rows if r.get("kind") == "township")
        tw["coverage_field"] = dict(modes)
        tw["coverage_field_direct_or_via_county_share"] = round(
            (modes.get("direct", 0) + modes.get("via_county", 0)) / n, 3)
    by_group = {}
    for g in sorted({p["group"] or "-" for p in per}):
        ps = [p for p in per if (p["group"] or "-") == g]
        by_group[g] = {"attempted": len(ps), "readable": sum(p["class"] == "readable" for p in ps),
                       "readable_share": round(sum(p["class"] == "readable" for p in ps) / len(ps), 3)}
    return {"by_kind": by_kind, "by_selection_group": by_group, "places": per}


# ------------------------------------------------------------------ freshness
def pdf_dates(body: bytes) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(body)
        tmp.flush()
        try:
            out = subprocess.run(["pdfinfo", "-isodates", tmp.name], capture_output=True, text=True, timeout=30).stdout
        except (subprocess.SubprocessError, OSError):
            return {}
    res = {}
    for k in ("CreationDate", "ModDate"):
        m = re.search(rf"^{k}:\s+(\S+)", out, re.M)
        if m:
            res[k] = m.group(1)
    return res


def _to_dt(s: str) -> datetime | None:
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _days(meeting: str, stamp: datetime) -> float:
    m = datetime.fromisoformat(meeting).replace(tzinfo=timezone.utc)
    return round((m - stamp.astimezone(timezone.utc)).total_seconds() / 86400, 1)


def relist_offline(st: str, rows: list[dict], window: Window) -> dict[str, dict]:
    """Re-run each automated listing from the cache (no network) to recover per-document extras
    (Revize upload stamps, WordPress upload months, 'Posted' text) and CivicClerk publishOn."""
    f = PoliteFetcher(DEFAULT_CACHE_DIR, offline=True)
    extras = {}
    for r in rows:
        if not r.get("automated"):
            continue
        for cfg in town_configs({**r, "state": st}):
            cls = REGISTRY.get(cfg["platform"])
            if cls is None:
                continue
            try:
                docs = cls(f).list_agendas(cfg, window)
            except Exception:  # noqa: BLE001 - offline: uncached listing pages are expected
                docs = []
            for d in docs:
                if d.extra:
                    extras[d.url] = dict(d.extra)
            if cfg["platform"] == "civicclerk":
                try:
                    evs = CivicClerkAdapter(f).events(cfg, window)
                except Exception:  # noqa: BLE001
                    evs = []
                api = f"https://{cfg['tenant']}.api.civicclerk.com/v1"
                for ev in evs:
                    for fl in ev.get("publishedFiles", []):
                        u = f"{api}/Meetings/GetMeetingFileStream(fileId={fl['fileId']},plainText=false)"
                        if fl.get("publishOn"):
                            extras.setdefault(u, {})["civicclerk_publishOn"] = fl["publishOn"]
    return extras


def freshness(st: str, rows: list[dict], docs: list[dict], crawl_day: date, window: Window) -> dict:
    f = PoliteFetcher(DEFAULT_CACHE_DIR, offline=True)
    ok = [d for d in docs if d.get("status") == "ok" and d.get("meeting_date")]
    ahead = [d for d in ok if d["meeting_date"] >= crawl_day.isoformat()]
    extras = relist_offline(st, rows, window)
    posted_rows = json.loads((TEST / f"posted_stamps_{st.lower()}.json").read_text()) \
        if (TEST / f"posted_stamps_{st.lower()}.json").exists() else []
    cp_posted = {p["url"]: p for p in posted_rows if p.get("posted") and p.get("posted_kind") == "posted"}
    rss = json.loads((TEST / "rss_pubdates.json").read_text()) if (TEST / "rss_pubdates.json").exists() else {}
    src = defaultdict(list)
    examples = defaultdict(list)
    for d in ok:
        url, md = d["url"], d["meeting_date"]
        e = extras.get(url, {})
        if url in cp_posted:
            src["civicplus_posted_stamp"].append(_days(md, _to_dt(cp_posted[url]["posted"]).replace(
                tzinfo=timezone(timedelta(hours=-4)))))
        m_cp = re.match(r"(https?://[^/]+)/AgendaCenter/ViewFile/Agenda/_\d{8}-(\d+)", url)
        if m_cp and f"{m_cp.group(1)}#{m_cp.group(2)}" in rss:
            src["civicplus_rss_pubdate"].append(_days(md, _to_dt(rss[f"{m_cp.group(1)}#{m_cp.group(2)}"])))
        if e.get("uploaded"):
            up = datetime.strptime(e["uploaded"], "%Y%m%d%H%M%S").replace(tzinfo=timezone(timedelta(hours=-4)))
            src["revize_upload_stamp"].append(_days(md, up))
        if e.get("posted"):
            pdt = None
            for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%m/%d/%y", "%B %d %Y", "%b. %d, %Y"):
                try:
                    pdt = datetime.strptime(re.sub(r"\s+\d{1,2}:\d{2}\s*[AP]M$", "", e["posted"]).strip(), fmt)
                    break
                except ValueError:
                    continue
            if pdt:
                src["posted_text_on_page"].append(_days(md, pdt.replace(tzinfo=timezone(timedelta(hours=-4)))))
        if e.get("uploaded_month"):
            y, m = map(int, e["uploaded_month"].split("-"))
            last = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1))
            src["wordpress_upload_month_lower_bound"].append(
                (date.fromisoformat(md) - last).days)
        if e.get("civicclerk_publishOn"):
            src["civicclerk_publishOn"].append(_days(md, _to_dt(e["civicclerk_publishOn"])))
        try:
            resp = f.get(d.get("source_url") or url)
        except FetchError:
            continue
        if resp.last_modified:
            try:
                src["http_last_modified"].append(_days(md, parsedate_to_datetime(resp.last_modified)))
            except (TypeError, ValueError):
                pass
        if resp.is_pdf:
            pdm = pdf_dates(resp.body)
            stamp = pdm.get("ModDate") or pdm.get("CreationDate")
            dt = _to_dt(stamp) if stamp else None
            if dt and 2020 <= dt.year <= 2030:
                src["pdf_moddate_or_creationdate"].append(_days(md, dt))
        if md >= crawl_day.isoformat() and d.get("first_seen"):
            src["our_first_fetch_upcoming_only"].append(_days(md, _to_dt(d["first_seen"])))
    return {
        "documents_read_with_meeting_date": len(ok),
        "documents_for_meetings_still_ahead": len(ahead),
        "share_still_ahead": round(len(ahead) / len(ok), 3) if ok else None,
        "lead_time_days_by_source": {k: dist(v) for k, v in src.items()},
    }


# ------------------------------------------------------------------ output
def output(st: str, docs: list[dict], hits_doc: dict, rep: dict) -> dict:
    hits = [h for h in hits_doc["hits"] if h["state"] == st]
    by_status = Counter(d.get("status") for d in docs)
    by_src = Counter(d.get("text_source") for d in docs if d.get("status") == "ok")
    topics = Counter(t for h in hits for t in h["topics"])
    return {
        "documents_listed_run1": (rep.get("by_state") or {}).get(st, {}),
        "documents_indexed": len(docs), "documents_by_status": dict(by_status),
        "documents_read_by_text_source": dict(by_src),
        "hits": len(hits), "hits_by_topic": dict(topics.most_common()),
        "hits_by_board": dict(Counter(h["board_key"] for h in hits)),
        "towns_with_hits": len({h["town"] for h in hits}),
        "hits_upcoming": sum(1 for h in hits if (h.get("meeting_date") or "") >= hits_doc["generated"][:10]),
    }


def analyze(args) -> None:
    from watch351.current import validate
    hits_doc = json.loads((TEST / "hits_mi_va.json").read_text())
    reps = run_reports()
    rep1 = reps.get(getattr(args, "base_run", None) or "run1", {})
    health = json.loads((TEST / "state" / "town_health.json").read_text())
    crawl_day = date.fromisoformat(rep1.get("date") or hits_doc["generated"][:10])
    w = rep1.get("window") or {"start": (crawl_day - timedelta(days=45)).isoformat(),
                               "end": (crawl_day + timedelta(days=120)).isoformat()}
    window = Window(date.fromisoformat(w["start"]), date.fromisoformat(w["end"]))
    res = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "crawl_day": crawl_day.isoformat(),
           "window": w, "contract_validation_errors": validate(hits_doc), "states": {}}
    for st in STATES:
        rows, docs = load_rows(st), load_docs(st)
        res["states"][st] = {
            "coverage": coverage(st, rows, docs, health, hits_doc),
            "output": output(st, docs, hits_doc, rep1),
            "freshness": freshness(st, rows, docs, crawl_day, window),
        }
    res["reliability"] = {k: {kk: v.get(kk) for kk in ("duration_seconds", "towns_attempted", "towns_succeeded",
                                                        "towns_failed", "towns_partial", "documents_listed",
                                                        "documents_already_indexed", "new_documents",
                                                        "documents_retried", "document_errors", "network",
                                                        "new_hits", "hits_current", "errors_total")}
                          for k, v in reps.items()}
    (TEST / "analysis_mi_va.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({st: {"coverage": res["states"][st]["coverage"]["by_kind"],
                           "output": res["states"][st]["output"],
                           "freshness": res["states"][st]["freshness"]} for st in STATES}, indent=1)[:12000])
    print("contract errors:", res["contract_validation_errors"][:5])


# ------------------------------------------------------------------ precision worksheet
def doc_text(url: str) -> str:
    f = PoliteFetcher(DEFAULT_CACHE_DIR, offline=True)
    try:
        resp = f.get(url)
    except FetchError:
        return ""
    return clean_text(X.extract(resp).text)


def _judged_keys(path: Path) -> tuple[set, set]:
    """Ids and (source_url, snippet head) of hits already judged in an earlier round, so a later round
    draws a fresh sample (hit ids can change when a meeting date or board name is corrected)."""
    doc = json.loads(path.read_text())
    items = [it for rnd in doc.get("rounds", []) for it in rnd.get("items", [])] if isinstance(doc, dict) else doc
    return ({it["id"] for it in items},
            {(it["source_url"], it["snippet"][:80]) for it in items})


def sample(args) -> None:
    """Every hit if a state has <= per_state, else a spread sample (round-robin over towns, then topics).
    --exclude FILE leaves out hits judged before (a worksheet or precision_judgments.json)."""
    hits_doc = json.loads((TEST / "hits_mi_va.json").read_text())
    ex_ids, ex_keys = _judged_keys(Path(args.exclude)) if getattr(args, "exclude", None) else (set(), set())
    # documents already in another test's index (the hand-checked pool): only hits from new documents
    seen_docs: set[str] = set()
    if getattr(args, "exclude_docs_from", None):   # a JSON list of document URLs
        seen_docs = set(json.loads(Path(args.exclude_docs_from).read_text()))
    out = []
    for st in STATES:
        hits = sorted((h for h in hits_doc["hits"] if h["state"] == st
                       and h["id"] not in ex_ids and (h["source_url"], h["snippet"][:80]) not in ex_keys
                       and h["source_url"] not in seen_docs),
                      key=lambda h: h["id"])
        if len(hits) > args.per_state and getattr(args, "random", None) is not None:
            # simple random sample of hits (every hit equally likely), seeded so it can be redrawn
            import random
            hits = sorted(random.Random(args.random).sample(hits, args.per_state), key=lambda h: (h["town"], h["id"]))
        elif len(hits) > args.per_state:
            by_town = defaultdict(list)
            for h in hits:
                by_town[h["town"]].append(h)
            picked, i = [], 0
            while len(picked) < args.per_state:
                added = False
                for t in sorted(by_town):
                    if i < len(by_town[t]) and len(picked) < args.per_state:
                        picked.append(by_town[t][i])
                        added = True
                if not added:
                    break
                i += 1
            hits = picked
        for h in hits:
            text = doc_text(h["source_url"])
            pos = text.find(h["snippet"][:100].rstrip("…"))
            ctx = text[max(0, pos - 600): pos + 900] if pos >= 0 else ""
            out.append({**{k: h[k] for k in ("id", "state", "town", "board", "meeting_date", "topics", "snippet",
                                            "source_url", "text_source")}, "context": ctx})
    dest = TEST / (getattr(args, "worksheet", None) or "precision_worksheet.json")
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)} hits to {dest}", Counter(h["state"] for h in out))


# ------------------------------------------------------------------ CivicPlus RSS posting times
def rss(args) -> None:
    """Fetch each CivicPlus site's AgendaCenter RSS (/RSSFeed.aspx?ModID=65&CID=All-0; robots.txt blocks
    only /RSS.aspx) and map agenda URLs to <pubDate> (when the agenda was posted)."""
    f = PoliteFetcher(DEFAULT_CACHE_DIR)
    out = {}
    for st in STATES:
        for r in load_rows(st):
            if not any("category_id" in l for l in r.get("listings") or []):
                continue
            origin = re.match(r"https?://[^/]+", r.get("final_url") or r["website"]).group(0)
            url = f"{origin}/RSSFeed.aspx?ModID=65&CID=All-0"
            try:
                resp = f.get(url, max_age=6 * 3600)
            except FetchError as e:
                print(r["town"], "RSS", e)
                continue
            n = 0
            # <link> is /AgendaCenter/PreviousVersions/<agenda id> (the id ends the ViewFile URL
            # "_MMDDYYYY-<id>"); an item whose description says "Update: Minutes added or updated" is a
            # later change, so only first postings (no "Update:") count as posting times.
            for item in re.findall(r"<item>(.*?)</item>", resp.text, re.S):
                link = re.search(r"<link>(.*?)</link>", item, re.S)
                pub = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
                desc = re.search(r"<description>(.*?)</description>", item, re.S)
                if not (link and pub) or (desc and "Update:" in desc.group(1)):
                    continue
                m = re.search(r"/AgendaCenter/(?:PreviousVersions/|ViewFile/Agenda/_\d{8}-)(\d+)", link.group(1))
                if not m:
                    continue
                try:
                    dt = parsedate_to_datetime(pub.group(1).strip())
                except (TypeError, ValueError):
                    continue
                out.setdefault(f"{origin}#{m.group(1)}", dt.isoformat())
                n += 1
            print(f"{r['town']}: RSS HTTP {resp.status}, {n} agenda items")
    (TEST / "rss_pubdates.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"{len(out)} agenda pubDates")
