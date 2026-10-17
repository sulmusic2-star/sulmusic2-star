"""Where people care about siting fights that we don't read yet: the next towns and states to add.

The same signals that rank Biggest stories, turned on the places outside our coverage:
  * regional news naming the town and a siting subject (data/news/matches.json, last 45 days)
  * neighbors we do read with siting items on their agendas in the last or next 60 days (a wave next door)
  * a data-center measure in the ledger (data/data_center_ledger.json) or a town action (data/tracker.json)
  * for states we don't cover, how many regional news stories name a siting subject there

Each town gets a score and what it would take to add it: an unblock request to the town or its agenda host
(a bot check or a robots.txt "no"), our own work (an agenda system we can't open yet, a page that needs a
browser), or adding it to the list (a New York town beside one we read).

    python3 tools/where_people_care.py            # writes data/expansion_targets.json and the research note
    python3 tools/where_people_care.py --print 25 # and prints the top 25
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import trending as TR  # noqa: E402

DATA = HERE / "data"
NOTE = HERE.parent.parent / "research_notes" / "Expansion" / "where_people_care.md"
SITING = {"data_center", "battery_storage", "solar", "wind", "moratorium", "clean_energy_siting", "40b_comprehensive_permit",
          "wireless_telecom"}
STATE_NAMES = {"MA": "Massachusetts", "NY": "New York", "RI": "Rhode Island", "CT": "Connecticut", "NH": "New Hampshire",
               "VT": "Vermont", "ME": "Maine", "NJ": "New Jersey", "PA": "Pennsylvania"}
# what it would take to read a town, by the reason we can't today
TAKES = {
    "bot_challenge": "unblock request", "waf_block": "unblock request", "robots_disallow_site": "unblock request",
    "vendor_blocked": "unblock request to the agenda host", "vendor_robots_disallow": "unblock request to the agenda host",
    "crawl_delay_exceeds_cap": "ask for a daily visit",
    "js_only": "our work: a reader for a browser-only page", "no_adapter": "our work: a reader for its agenda system",
    "no_agenda_listing_found": "find where it posts agendas", "agendas_stale_or_undated": "find dated agendas",
}
W_NEWS, W_WAVE, W_LEDGER, W_TRACKER = 3.0, 1.0, 4.0, 2.0
LABEL = {"data_center": "data centers", "battery_storage": "battery storage", "solar": "solar", "wind": "wind",
         "moratorium": "moratoriums", "clean_energy_siting": "clean-energy permits", "40b_comprehensive_permit": "40B housing",
         "wireless_telecom": "cell towers"}


def load(name, default):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


def site_towns():
    rows = {}
    for path in sorted(DATA.glob("towns_*.json")):
        doc = json.loads(path.read_text())
        for t in (doc.get("towns", []) if isinstance(doc, dict) else doc):
            if isinstance(t, dict) and t.get("town"):
                st = (t.get("state") or "MA").upper()
                rows.setdefault(f"{st}:{t['town']}", {"state": st, "town": t["town"], "county": t.get("county"),
                                                     "monitored": bool(t.get("automated")),
                                                     "reason_code": t.get("reason_code") or "",
                                                     "pop": t.get("pop_2024_est") or t.get("pop_2020") or 0})
    return rows


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--print", dest="show", type=int, default=0)
    p.add_argument("--today", default=None)
    a = p.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    towns = site_towns()
    shown_states = {"MA", "NY", "RI"}
    neighbors = {k: v for k, v in load("neighbors.json", {}).items() if not k.startswith("_")}
    news = load("news/matches.json", {})
    ledger = load("data_center_ledger.json", {})
    ledger_rows = ledger.get("rows", []) if isinstance(ledger, dict) else ledger
    tracker = load("tracker.json", {}).get("items", [])
    inputs = TR.load_inputs(str(DATA))

    # siting activity in towns we read, last or next 60 days
    lo, hi = today - timedelta(days=60), today + timedelta(days=60)
    active = defaultdict(set)
    for st, tw, t, d in inputs["history"]:
        if t in SITING and d and lo <= d <= hi:
            active[f"{st}:{tw}"].add(t)
    read = {k for k, t in towns.items() if t["monitored"] and t["state"] in shown_states}

    # candidates: towns on our lists we can't read, and New York towns beside ones we read
    cands = {k: t for k, t in towns.items() if not t["monitored"] and t["state"] in shown_states}
    for k in read:
        for n in neighbors.get(k, []):
            if n not in towns and n.split(":", 1)[0] == "NY":
                cands.setdefault(n, {"state": "NY", "town": n.split(":", 1)[1], "county": None, "monitored": False,
                                     "reason_code": "not_listed", "pop": 0})

    since = (today - timedelta(days=45)).isoformat()
    out = []
    for k, t in cands.items():
        arts = [x for x in (news.get("towns") or {}).get(k, []) if (x.get("published") or "")[:10] >= since]
        wave = sorted(n for n in neighbors.get(k, []) if n in read and active.get(n))
        led = [r for r in ledger_rows if f"{r.get('state', 'MA')}:{r.get('town')}" == k]
        trk = [i for i in tracker if f"{i.get('state', 'MA')}:{i.get('town')}" == k]
        score = W_NEWS * min(3, len(arts)) + W_WAVE * min(5, len(wave)) + W_LEDGER * bool(led) + W_TRACKER * bool(trk)
        if not score:
            continue
        why = []
        if arts:
            why.append(f"in the news ({len(arts)}): " + "; ".join(f"{x['source']}, {x['title']}" for x in arts[:2]))
        if led:
            why.append("data-center measure: " + ", ".join(f"{r.get('measure')} ({r.get('status')})" for r in led))
        if trk:
            why.append("town action on " + ", ".join(sorted({(i.get('topic') or '').lower() for i in trk})))
        if wave:
            subj = sorted({s for n in wave for s in active[n]})
            why.append(f"{len(wave)} neighbors we read have it on agendas ({', '.join(n.split(':', 1)[1] for n in wave[:4])}"
                       f"{' and more' if len(wave) > 4 else ''}): {', '.join(LABEL.get(x, x) for x in subj)}")
        out.append({"id": k, "state": t["state"], "town": t["town"], "county": t.get("county"), "score": round(score, 1),
                    "takes": "add to the New York list" if t["reason_code"] == "not_listed"
                    else TAKES.get(t["reason_code"], "look into it"),
                    "reason_code": t["reason_code"], "why": why})
    out.sort(key=lambda x: (-x["score"], x["state"], x["town"]))

    # states we don't cover: regional news naming a siting subject there
    states = []
    for st, topics in sorted((news.get("states") or {}).items()):
        if st in shown_states:
            continue
        states.append({"state": st, "stories": sum(topics.values()), "topics": topics})
    states.sort(key=lambda x: -x["stories"])

    result = {"generated": datetime.now().isoformat(timespec="seconds"), "today": today.isoformat(),
              "towns": out, "states": states,
              "weights": {"news": W_NEWS, "wave_per_neighbor": W_WAVE, "ledger": W_LEDGER, "tracker": W_TRACKER}}
    (DATA / "expansion_targets.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    write_note(result)
    if a.show:
        for i, x in enumerate(out[:a.show], 1):
            print(f"{i:>3}. [{x['score']:5.1f}] {x['town']}, {x['state']}  ({x['takes']})")
            for w in x["why"]:
                print(f"       {w}")
        for s in states:
            print(f"   {s['state']}: {s['stories']} stories {s['topics']}")
    print(f"where_people_care: {len(out)} towns, {len(states)} other states -> data/expansion_targets.json", file=sys.stderr)


def write_note(result):
    by_take = defaultdict(list)
    for x in result["towns"]:
        by_take[x["takes"]].append(x)
    lines = [
        "# Where people care that we don't read yet",
        "",
        f"Generated {result['today']} by `projects/351watch/tools/where_people_care.py` (rerun it any day). Signals: regional news "
        "naming the town and a siting subject in the last 45 days, neighbors we read with siting items on their agendas in the "
        "last or next 60 days, a data-center measure in the ledger, a town action in the tracker. Weights: news 3 per story "
        "(up to 3), 1 per active neighbor (up to 5), ledger 4, tracker 2.",
        "",
        "## Top 25",
        "",
        "| # | Town | Score | What it takes | Why |",
        "|---|---|---|---|---|",
    ]
    for i, x in enumerate(result["towns"][:25], 1):
        lines.append(f"| {i} | {x['town']}, {x['state']} | {x['score']} | {x['takes']} | {'; '.join(x['why'])} |")
    lines += ["", "## By what it takes", ""]
    for take, xs in sorted(by_take.items(), key=lambda kv: -sum(x["score"] for x in kv[1])):
        lines.append(f"- **{take}** ({len(xs)}): " + ", ".join(f"{x['town']}, {x['state']}" for x in xs[:15])
                     + (f" and {len(xs) - 15} more" if len(xs) > 15 else ""))
    lines += ["", "## States we don't cover", "",
              "Regional news stories naming a siting subject in the state (feeds we read: CT Mirror, NHPR and the "
              "Massachusetts, New York and Rhode Island newsrooms that cover their neighbors).", ""]
    for s in result["states"]:
        lines.append(f"- {STATE_NAMES.get(s['state'], s['state'])}: {s['stories']} ({', '.join(f'{LABEL.get(k, k)} {v}' for k, v in s['topics'].items())})")
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    NOTE.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
