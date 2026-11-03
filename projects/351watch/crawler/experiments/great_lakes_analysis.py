"""Analysis for the Great Lakes wave (great_lakes_test.py analyze | sample): coverage three ways
(direct readability, county-route coverage, nothing usable online), by county and route, for
Michigan and Ohio; output and freshness reuse mi_va_analysis. Everything reads local files
(towns_*.json, data/test/great_lakes/, the fetch cache); nothing is fetched."""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import mi_va_analysis as MVA
from watch351.attribution import body_name, covered_counties
from watch351.fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from watch351.keywords import clean_text
from watch351.models import Window
from watch351 import extract as X

CRAWLER = Path(__file__).resolve().parent.parent
DATA = CRAWLER.parent / "data"
TEST = DATA / "test" / "great_lakes"
HITS_NAME = "hits_great_lakes.json"
STATES = ("MI", "OH")
SE_MI = ["Washtenaw", "Livingston", "Oakland", "Macomb", "Monroe", "Lenawee", "Jackson", "Genesee", "Lapeer",
         "St. Clair", "Shiawassee", "Ingham"]
OH8 = ["Licking", "Union", "Franklin", "Delaware", "Logan", "Champaign", "Clermont", "Butler"]
BLOCKED, NO_AGENDAS, ERRORS = MVA.BLOCKED, MVA.NO_AGENDAS, MVA.ERRORS


def load_rows(st: str) -> list[dict]:
    return json.loads((DATA / f"towns_{st.lower()}.json").read_text())["towns"]


def load_docs(st: str) -> list[dict]:
    out = []
    for p in sorted((TEST / "state" / "docs" / st).glob("*.jsonl")):
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out


def place_class(r: dict, read_boards: list[str], h: dict) -> str:
    if r.get("automated") and read_boards:
        return "readable"
    if r.get("automated") and h.get("status") == "failed":
        return "crawl_error"
    if r.get("automated"):
        return "automated_no_docs_in_window"
    if r.get("reason_code") in BLOCKED:
        return "blocked"
    if r.get("reason_code") in ERRORS:
        return "error_unreachable"
    return "no_agendas_online"


def coverage(st: str, rows: list[dict], docs: list[dict], health: dict, hits_doc: dict, counties: list[str]) -> dict:
    """Per place class, then the three coverage measures per state and per county:
    direct (its own agendas read in the window), county route (direct, or its county / regional planning
    commission is readable), nothing usable online (no site, minutes only, no agenda page, stale)."""
    ok_by_town_board = defaultdict(set)
    for d in docs:
        if d.get("status") == "ok":
            ok_by_town_board[d["town"]].add(d.get("board_key"))
    per = []
    for r in rows:
        tracked = r.get("boards_tracked") or ["select_board", "planning_board", "zoning_board_of_appeals"]
        read_boards = sorted(ok_by_town_board.get(r["town"], set()) & set(tracked))
        h = health.get(f"{st}:{r['town']}", {})
        per.append({"town": r["town"], "county": r.get("county"), "kind": r.get("kind"), "group": r.get("selection_group"),
                    "class": place_class(r, read_boards, h), "reason_code": r.get("reason_code"),
                    "platform": r.get("platform"), "boards_tracked": tracked, "boards_read": read_boards,
                    "boards_automated": sorted({l["board_key"] for l in r.get("listings") or []}),
                    "reason": (r.get("reason") or "")[:200], "health": h.get("status"),
                    "coverage": r.get("coverage"), "coverage_county_body": r.get("coverage_county_body"),
                    "covers_counties": r.get("covers_counties"), "website": r.get("website")})
    by_place = {p["town"]: p for p in per}
    # county bodies: which county's townships each readable body covers (regional bodies: several)
    county_body_rows = [r for r in rows if r.get("kind") == "county"]
    body_for_county: dict[str, dict] = {}
    for r in county_body_rows:
        p = by_place[r["town"]]
        for c in covered_counties(r):
            cur = body_for_county.get(c)
            # prefer a readable body; else the first one
            if cur is None or (p["class"] == "readable" and cur["class"] != "readable"):
                body_for_county[c] = p
    # townships named in a county item this window (attributed hits)
    named = defaultdict(set)
    county_rows = {r["town"] for r in rows if r.get("kind") == "county"}
    township_rows = {r["town"] for r in rows if r.get("kind") == "township"}
    for h in hits_doc["hits"]:
        # the hits file carries no attributed_from: a county body's item is one whose board is the county
        # body's name and whose town is a township row (the body's own name is the row the item stays with)
        if h["state"] == st and h["town"] in township_rows and re.search(r"County|Regional", h.get("board") or "") \
                and h["town"] not in county_rows:
            named[h["town"]].add(h["board"])
    twp = [p for p in per if p["kind"] == "township"]
    by_county = {}
    for c in counties:
        tw = [p for p in twp if p["county"] == c]
        if not tw:
            continue
        body = body_for_county.get(c)
        body_ok = bool(body and body["class"] == "readable")
        direct = [p for p in tw if p["class"] == "readable"]
        via = [p for p in tw if p["class"] != "readable" and body_ok]
        nothing = [p for p in tw if p["class"] == "no_agendas_online"]
        blocked = [p for p in tw if p["class"] == "blocked"]
        by_county[c] = {
            "townships": len(tw),
            "direct_readable": len(direct),
            "listing_works_no_doc_in_window": sum(p["class"] == "automated_no_docs_in_window" for p in tw),
            "via_county_only": len(via),
            "direct_or_via_county": len(direct) + len(via),
            "direct_or_via_county_share": round((len(direct) + len(via)) / len(tw), 3),
            "direct_share": round(len(direct) / len(tw), 3),
            "blocked": len(blocked),
            "blocked_how": dict(Counter(f"{BLOCKED.get(p['reason_code'], p['reason_code'])}"
                                        f"{': ' + str(p['platform']) if p['reason_code'] == 'vendor_blocked' else ''}" for p in blocked)),
            "nothing_usable_online": len(nothing),
            "nothing_how": dict(Counter(p["reason_code"] for p in nothing)),
            "error_unreachable": sum(p["class"] == "error_unreachable" for p in tw),
            "county_body": body["town"] if body else None,
            "county_body_label": body_name({"town": body["town"], "county": c, "county_body":
                                            next((r.get("county_body") for r in county_body_rows if r["town"] == body["town"]), None)})
            if body else None,
            "county_body_class": body["class"] if body else "no county body row",
            "county_body_reason": (body["reason_code"] or body["platform"]) if body else None,
            "county_body_platform": body["platform"] if body else None,
            "townships_named_in_county_items": sorted(t for t in named if by_place.get(t, {}).get("county") == c),
            "direct_platforms": dict(Counter(p["platform"] for p in direct)),
        }
    n = len(twp) or 1
    n_direct = sum(p["class"] == "readable" for p in twp)
    n_either = sum(by_county[c]["direct_or_via_county"] for c in by_county)
    n_nothing = sum(p["class"] == "no_agendas_online" for p in twp)
    n_blocked = sum(p["class"] == "blocked" for p in twp)
    bodies = [p for p in per if p["kind"] == "county"]
    state_summary = {
        "townships": len(twp),
        "direct_readable": n_direct, "direct_readable_share": round(n_direct / n, 3),
        "listing_works_no_doc_in_window": sum(p["class"] == "automated_no_docs_in_window" for p in twp),
        "direct_or_via_county": n_either, "direct_or_via_county_share": round(n_either / n, 3),
        "via_county_only": n_either - n_direct,
        "blocked": n_blocked, "blocked_how": dict(Counter(
            f"{BLOCKED.get(p['reason_code'], p['reason_code'])}{': ' + str(p['platform']) if p['reason_code'] == 'vendor_blocked' else ''}"
            for p in twp if p["class"] == "blocked")),
        "nothing_usable_online": n_nothing, "nothing_usable_online_share": round(n_nothing / n, 3),
        "nothing_how": dict(Counter(p["reason_code"] for p in twp if p["class"] == "no_agendas_online")),
        "error_unreachable": sum(p["class"] == "error_unreachable" for p in twp),
        "coverage_field": dict(Counter(r.get("coverage") or "none" for r in rows if r.get("kind") == "township")),
        "county_bodies": len(bodies),
        "county_bodies_readable": sum(p["class"] == "readable" for p in bodies),
        "county_bodies_by_class": dict(Counter(p["class"] for p in bodies)),
        "county_bodies_blocked_how": dict(Counter(
            f"{BLOCKED.get(p['reason_code'], p['reason_code'])}{': ' + str(p['platform']) if p['reason_code'] == 'vendor_blocked' else ''}"
            for p in bodies if p["class"] == "blocked")),
        "county_bodies_readable_names": sorted(p["town"] for p in bodies if p["class"] == "readable"),
        "townships_named_in_county_items": sorted(named),
        "direct_platforms": dict(Counter(p["platform"] for p in twp if p["class"] == "readable")),
        "by_selection_group": {g: {"attempted": len(ps), "readable": sum(p["class"] == "readable" for p in ps)}
                               for g in sorted({p["group"] or "-" for p in per})
                               for ps in [[p for p in per if (p["group"] or "-") == g]]},
    }
    return {"state": state_summary, "by_county": by_county, "places": per}


def analyze(args) -> None:
    from watch351.current import validate
    hits_doc = json.loads((TEST / HITS_NAME).read_text())
    reps = {p.stem.replace("run_", ""): json.loads(p.read_text()) for p in sorted((TEST / "runs").glob("run_*.json"))}
    rep1 = reps.get(getattr(args, "base_run", None) or "run1", {})
    health = json.loads((TEST / "state" / "town_health.json").read_text())
    crawl_day = date.fromisoformat(rep1.get("date") or hits_doc["generated"][:10])
    w = rep1.get("window") or {"start": (crawl_day - timedelta(days=45)).isoformat(),
                               "end": (crawl_day + timedelta(days=120)).isoformat()}
    window = Window(date.fromisoformat(w["start"]), date.fromisoformat(w["end"]))
    MVA.TEST = TEST
    res = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "crawl_day": crawl_day.isoformat(),
           "window": w, "contract_validation_errors": validate(hits_doc), "states": {}}
    for st, counties in (("MI", SE_MI), ("OH", OH8)):
        rows, docs = load_rows(st), load_docs(st)
        if st == "MI":   # the twelve southeast counties are this wave's; the rest are the 2026-10 test's
            rows_wave = [r for r in rows if r.get("county") in counties or r.get("kind") == "county"]
        else:
            rows_wave = rows
        res["states"][st] = {
            "coverage": coverage(st, rows_wave, docs, health, hits_doc, counties),
            "coverage_all_rows": coverage(st, rows, docs, health, hits_doc,
                                          sorted({r.get("county") for r in rows if r.get("county")}))["state"]
            if st == "MI" else None,
            "output": MVA.output(st, docs, hits_doc, rep1),
            "freshness": MVA.freshness(st, rows, docs, crawl_day, window),
        }
    res["reliability"] = {k: {kk: v.get(kk) for kk in ("duration_seconds", "towns_attempted", "towns_succeeded",
                                                        "towns_failed", "towns_partial", "documents_listed",
                                                        "documents_already_indexed", "new_documents",
                                                        "documents_retried", "document_errors", "network",
                                                        "new_hits", "hits_current", "errors_total")}
                          for k, v in reps.items()}
    (TEST / "analysis_great_lakes.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    for st in STATES:
        c = res["states"][st]["coverage"]
        print(f"== {st} ==")
        print(json.dumps(c["state"], indent=1))
        print("by county:")
        for k, v in c["by_county"].items():
            print(f"  {k:<12} twp {v['townships']:>2}  direct {v['direct_readable']:>2}  via-county-only {v['via_county_only']:>2}  "
                  f"either {v['direct_or_via_county_share']:.0%}  nothing {v['nothing_usable_online']:>2}  blocked {v['blocked']:>2}  "
                  f"body: {v['county_body_class']} ({v['county_body_reason']})")
        print("output:", json.dumps(res["states"][st]["output"], indent=1)[:1500])
        print("freshness:", json.dumps(res["states"][st]["freshness"], indent=1)[:2500])
    print("contract errors:", res["contract_validation_errors"][:5])


# ------------------------------------------------------------------ precision worksheet
def doc_text(url: str) -> str:
    f = PoliteFetcher(DEFAULT_CACHE_DIR, offline=True)
    try:
        resp = f.get(url)
    except FetchError:
        return ""
    return clean_text(X.extract(resp).text)


def sample(args) -> None:
    """A seeded simple random sample of per_state hits per state (every hit equally likely), with about
    1,500 characters of document context each, for the hand check. --exclude FILE skips hits judged before."""
    hits_doc = json.loads((TEST / HITS_NAME).read_text())
    ex_ids, ex_keys = MVA._judged_keys(Path(args.exclude)) if getattr(args, "exclude", None) else (set(), set())
    out = []
    for st in STATES:
        hits = sorted((h for h in hits_doc["hits"] if h["state"] == st and h["id"] not in ex_ids
                       and (h["source_url"], h["snippet"][:80]) not in ex_keys), key=lambda h: h["id"])
        pool = len(hits)
        if len(hits) > args.per_state:
            seed = args.random if getattr(args, "random", None) is not None else 2028
            hits = sorted(random.Random(seed).sample(hits, args.per_state), key=lambda h: (h["town"], h["id"]))
        for h in hits:
            text = doc_text(h["source_url"])
            pos = text.find(h["snippet"][:100].rstrip("…"))
            ctx = text[max(0, pos - 600): pos + 900] if pos >= 0 else ""
            out.append({**{k: h.get(k) for k in ("id", "state", "town", "county", "board", "meeting_date", "topics", "snippet",
                                                "source_url", "text_source")}, "pool": pool, "context": ctx})
    dest = TEST / (getattr(args, "worksheet", None) or "precision_worksheet.json")
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)} hits to {dest}", Counter(h["state"] for h in out))
