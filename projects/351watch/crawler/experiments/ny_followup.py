#!/usr/bin/env python3
"""New York follow-up without unblock letters (2026-11-03): places the wave-1 and wave-2 passes could not read
for reasons the crawler itself could remove. Everything here writes under data/test/ny_followup/ only; nothing
touches data/towns_ny.json, data/state/ or data/hits_current.json. The rows to change in data/towns_ny.json are
reported, not applied.

    cd projects/351watch/crawler
    python3 experiments/ny_followup.py discover [--places Huntington,Lansing,Cicero,Pound Ridge]
        # production (or wave) rows re-discovered with the 20 s crawl-delay cap -> data/test/ny_followup/config/towns_ny.json
    python3 experiments/ny_followup.py discover --counties [--places "Schenectady County,..."]
        # the county planning boards the wave-2 discovery filed as "no website found", with the sites found on 2026-11-03
    python3 experiments/ny_followup.py curate         # hand listings: Southampton (eSCRIBE HTML view), Perth / Spafford / Boston (Munibit)
    python3 experiments/ny_followup.py munibit        # the meeting lists the Munibit module gives (board, date, agenda address)
    python3 experiments/ny_followup.py crawl --label run1 [--places A,B]   # watch351.daily into data/test/ny_followup/ny
    python3 experiments/ny_followup.py report         # what read, per town -> data/test/ny_followup/report.md + report.json

The jobs behind it (research_notes/Expansion/ny_unblock_drafts.md, "Not letters: for the engineer"):

1. Crawl delays. fetch.CRAWL_DELAY_CAP is 20 s (was 10 s), with a per-run budget of fetch.SLOW_HOST_DOC_BUDGET
   documents for a host asking more than fetch.SLOW_HOST_DELAY. Huntington (15 s), Cicero (20 s) and Pound Ridge
   (15 s) can be read; Lansing's robots.txt asks 10 s since 2026-10-20.
2. The Munibit "agendasandminutes" module (Perth, Spafford, Boston): adapters/munibit.py reads the meeting list
   from the module's public JSON; the files themselves are served only to the site's own viewer, so the rows stay
   not automated until the town or Munibit allows the reader (listing key files_readable).
3. eSCRIBE (Southampton): the existing adapter reads the portal's HTML agenda view (format html); discovery now
   prefers that view and never requests the challenged PDF download.
4. County planning boards: Schenectady, Tompkins, Wayne, Schoharie and Steuben, discovered with the wave-2 county
   board patterns (GML 239-m referral agendas), websites in wave2_test.WEBSITES.

All requests go through watch351.fetch.PoliteFetcher.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAWLER = HERE.parent
sys.path.insert(0, str(CRAWLER))
sys.path.insert(0, str(HERE))

from watch351.fetch import FetchError, PoliteFetcher  # noqa: E402
from watch351.models import Window  # noqa: E402

DATA = CRAWLER.parent / "data"
OUT = DATA / "test" / "ny_followup"
CONFIG = OUT / "config"
CONFIG_FILE = CONFIG / "towns_ny.json"
CRAWL_OUT = OUT / "ny"
HITS_NAME = "hits_ny_followup.json"
PROD = DATA / "towns_ny.json"
W1_CONFIG = DATA / "test" / "wave1" / "config" / "towns_ny.json"
W2_CONFIG = DATA / "test" / "wave2" / "config" / "towns_ny.json"
W2_TARGETS = DATA / "test" / "wave2" / "targets_ny.json"
ALL3 = ["select_board", "planning_board", "zoning_board_of_appeals"]
TODAY = date.today().isoformat()

DEFAULT_PLACES = ["Huntington", "Lansing", "Cicero", "Pound Ridge"]
DEFAULT_COUNTIES = ["Schenectady County", "Tompkins County", "Wayne County", "Schoharie County", "Steuben County"]

ESCRIBE_SOUTHAMPTON = "https://pub-southamptonny.escribemeetings.com/"
# Hand listings. Southampton: the portal's meeting types as its filter lists them (2026-11-03); the HTML agenda
# view is read, the PDF download (a browser challenge) is never requested. Munibit towns: the page that embeds
# the module; files_readable stays false until the town or Munibit allows the reader to fetch the files.
CURATED: dict[str, dict] = {
    "Southampton": {
        "platform": "escribe",
        "listings": [
            {"board": "Town Board", "board_key": "select_board", "platform": "escribe", "url": ESCRIBE_SOUTHAMPTON,
             "meeting_type": r"^Town Board (Regular Meeting|Special Meeting|Work Session|Special Work Session|Organizational Meeting)$",
             "format": "html"},
            {"board": "Planning Board", "board_key": "planning_board", "platform": "escribe", "url": ESCRIBE_SOUTHAMPTON,
             "meeting_type": r"^Planning Board", "format": "html"},
            {"board": "Zoning Board of Appeals", "board_key": "zoning_board_of_appeals", "platform": "escribe",
             "url": ESCRIBE_SOUTHAMPTON, "meeting_type": r"^Zoning Board of Appeals$", "format": "html"},
            {"board": "Conservation Board", "board_key": "conservation_commission", "platform": "escribe",
             "url": ESCRIBE_SOUTHAMPTON, "meeting_type": r"^Conservation Board$", "format": "html"},
        ],
        "curation_note": "eSCRIBE portal, HTML agenda view (format html). Agendas appear on the portal a few days before "
                         "each meeting; past meetings load by POST and are not read. The PDF download (FileStream.ashx) "
                         "answers a browser challenge and is never requested. The Trustees and the Architectural Review "
                         "Board are not tracked boards.",
        "automated": True,
    },
    "Perth": {
        "platform": "munibit",
        "listings": [
            {"board": "Town Board", "board_key": "select_board", "platform": "munibit",
             "url": "https://www.perthny.gov/agendasandminutes", "files_readable": False},
            {"board": "Planning Board", "board_key": "planning_board", "platform": "munibit",
             "url": "https://www.perthny.gov/agendasandminutes", "files_readable": False},
        ],
        "curation_note": "Munibit document module: Town Board agendas (Agendas & Minutes / Town Board Agendas / <year>) and "
                         "Planning Board meeting notices and agendas; the files are served only to the site's own viewer.",
        "automated": True,
    },
    "Spafford": {
        "platform": "munibit",
        "listings": [
            {"board": "Town Board", "board_key": "select_board", "platform": "munibit",
             "url": "https://www.townofspaffordny.gov/agendasandminutes", "files_readable": False},
            {"board": "Planning Board", "board_key": "planning_board", "platform": "munibit",
             "url": "https://www.townofspaffordny.gov/agendasandminutes", "files_readable": False},
        ],
        "curation_note": "Munibit document module: Town Board agendas sit in one folder per meeting ('October 8, 2026 Agenda "
                         "& Documents', with the bills, reports and local-law texts); Planning Board agendas are named by date. "
                         "No ZBA documents are posted. The files are served only to the site's own viewer.",
        "automated": True,
    },
    "Boston": {
        "platform": "munibit",
        "listings": [
            {"board": "Town Board", "board_key": "select_board", "platform": "munibit",
             "url": "https://www.bostonny.gov/townboard", "files_readable": False},
            {"board": "Planning Board", "board_key": "planning_board", "platform": "munibit",
             "url": "https://www.bostonny.gov/planningboard", "files_readable": False},
            {"board": "Zoning Board of Appeals", "board_key": "zoning_board_of_appeals", "platform": "munibit",
             "url": "https://www.bostonny.gov/ZBA", "files_readable": False},
        ],
        "curation_note": "Munibit document module on each board's page (the site is bostonny.gov; townofboston.com redirects). "
                         "'TB 2026-10-21 Agenda Packet' and 'PB 2026-06-09 Agenda & Minutes' name the meeting day. The files "
                         "are served only to the site's own viewer.",
        "automated": True,
    },
}

# Schoharie County: discovery stopped short of the Planning Commission page (Revize site, "Planning and Community
# Development" > "Planning & Zoning" > "Planning Commission"); the page posts the commission's dated agendas
# ("November 2, 2026 Agenda.pdf") with the referral files (site plans, local laws) beside them. The commission meets
# the first Monday of each month and takes GML 239-m referrals.
CURATED["Schoharie County"] = {
    "platform": "agenda_page",
    "listings": [
        {"board": "Schoharie County Planning Commission", "board_key": "planning_board", "platform": "agenda_page",
         "url": "https://schohariecounty-ny.gov/departments/community_development/planning_zoning/planning_commission.php",
         "strip_doc_query": True},
    ],
    "county_body": "Schoharie County Planning Commission",
    "attribute_townships": True,
    "curation_note": "Planning Commission page on the county's Revize site: dated agendas (first Monday of the month) and the "
                     "referral documents of each meeting; the general agenda-page reader takes the agendas. Found by hand on "
                     "2026-11-03 after discovery read the department pages only.",
    "automated": True,
}

# Lansing: the AgendaCenter "agenda" files are one-line cover sheets ("Meeting Agenda", "Meeting Packet": two links
# to DocumentCenter files); the CivicPlus adapter's linked_agenda option reads the file the HTML view links as the
# agenda. Applied on top of the discovered listings (category ids stay as found).
CURATED["Lansing"] = {
    "listing_options": {"linked_agenda": True},
    "curation_note": "CivicPlus AgendaCenter whose agenda PDFs are cover sheets linking the real agenda and packet in the "
                     "DocumentCenter; listings carry linked_agenda so the linked agenda file is read (2026-11-03).",
}

# What was found by hand on 2026-11-03, kept with the generated report.
NOTES = {
    "Huntington": "The town site answers at its 15 s crawl delay, but every agenda is on huntingtonny.granicus.com, whose robots.txt "
                  "disallows all agents but Googlebot, Slurp, msnbot and the county's own search; the town's /meetings page lists no "
                  "documents. Needs the vendor letter, not a crawler change.",
    "Lansing": "lansingtownny.gov asks a 10 s crawl delay since 2026-10-20 (15 s in October). CivicPlus AgendaCenter with Town Board and "
               "Planning Board categories; the AgendaCenter agenda files are cover sheets, so the listings carry linked_agenda and the "
               "DocumentCenter agenda is read (four Town Board agendas Sept 23 to Nov 4, one Planning Board agenda Nov 9). The ZBA page "
               "lists no dated agendas; older documents sit in a Laserfiche WebLink repository (lfweb.tompkins-co.org), not read.",
    "Cicero": "ciceronewyork.net now redirects to cicerony.gov (Crawl-delay 20 s, honoured). Its /meetings/ page lists every board's "
              "agendas (ZBA Nov 2, Planning Board Nov 4, Town Board Oct 14, 16, 28) as PDFs under /wp-content/uploads/, which robots.txt "
              "disallows for all agents. The ask for the letter: Allow: /wp-content/uploads/ for User-agent: AgendaAheadBot. Hearing "
              "notices are also HTML posts (cicerony.gov/category/public-hearings/), readable if a notices listing is wanted.",
    "Pound Ridge": "Wave-2 row: townofpoundridge.gov asks 15 s, readable since the cap rose. Town Board agenda, backup packet and hearing "
                   "notice for Nov 4 read; the Planning Board and ZBA pages list no dated agendas in the window.",
    "Southampton": "eSCRIBE portal: the Conservation Board (Nov 4) and ZBA (Nov 5) HTML agenda views read with text_source html; the "
                   "Town Board (work session Nov 5, regular Nov 10) and Planning Board meetings are listed on the portal but their agendas "
                   "were not yet published. The PDF download was never requested.",
    "Perth": "Munibit module: the JSON lists the Town Board agenda of Nov 5 (with public hearing materials) and Oct 1, and the Planning "
             "Board's monthly meeting notices (September to November); the files are served only to the site's own viewer.",
    "Spafford": "Munibit module: Town Board agenda Oct 8 (the Nov 5 meeting folder holds budget documents, no agenda yet) and Planning "
                "Board agenda Oct 15; the Oct 8 folder also holds the Local Law C-2026 solar moratorium texts and GML referral. Files "
                "served only to the viewer.",
    "Boston": "Munibit module on each board page (bostonny.gov): Town Board agenda packets Sept 30 and Oct 21, agenda & minutes Sept 30; "
              "Planning Board and ZBA have no documents since June and August. Files served only to the viewer.",
    "Schoharie County": "Revize site; the Planning Commission page (first Monday of the month) posts dated agendas and each meeting's "
                        "referral files. The Nov 2 agenda lists referrals from Gilboa, Schoharie, Cobleskill, Richmondville, Jefferson "
                        "and Seward, in the 'Town of X:' form attribution.py reads.",
    "Schenectady County": "Drupal site; the Economic Development and Planning department pages (ag district, trails, aquifer, GIS) "
                          "name no planning board or commission and post no agendas. 239-m reviews appear to be a department function.",
    "Tompkins County": "The Legislature and its committees are on tompkinscountyny.iqm2.com (closed vendor; its robots.txt did not "
                       "answer, which RFC 9309 treats as disallow). The Planning and Sustainability department's pages list advisory "
                       "boards (tourism, transportation council) but no county planning board agendas; 239 reviews are staff work.",
    "Wayne County": "waynecountyny.gov (web.co.wayne.ny.us redirects there): CivicPlus AgendaCenter with a 'Wayne County Planning Board' "
                    "category. The Oct 28 agenda read (referrals as 'T. Ontario (Applicant)', 'V. Newark', which attribution.py reads); "
                    "the Sept 23 file is an 87 MB packet, over the 40 MB download cap.",
    "Steuben County": "steubencountyny.gov answered this time (CivicPlus). Its AgendaCenter holds the Legislature and its committees "
                      "only; the Planning department's Planning & Zoning Assistance page says 239-m referrals are reviewed by the "
                      "department on a referral form. There is no county planning board agenda to read.",
}

ABOUT = ("Agenda Ahead New York follow-up (2026-11-03): places re-read after crawler changes that needed no unblock letter "
         "(crawl-delay cap 20 s, Munibit meeting lists, the eSCRIBE HTML view, county sites found after the wave-2 run). "
         "Same row shape as towns_ny.json. Built by experiments/ny_followup.py; kept outside data/towns_*.json because New "
         "York is a published state. Nothing here is promoted by a script: the rows to change are in report.md.")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def config_doc(rows: list[dict]) -> dict:
    return {"_about": ABOUT, "generated": now_iso(), "state": "NY", "gated": True,
            "gate_note": "Follow-up test rows: not part of the production run or the site. Crawled only by "
                         "`python3 -m watch351.daily --data-dir ../data/test/ny_followup/config --states NY --output-dir "
                         "../data/test/ny_followup/ny --hits-name hits_ny_followup.json` (experiments/ny_followup.py crawl).",
            "boards_tracked": ALL3, "count": len(rows), "automated": sum(1 for r in rows if r.get("automated")),
            "towns": rows}


def source_rows() -> dict[str, tuple[str, dict]]:
    """Every known New York row by town name: production first, then the wave configs."""
    out: dict[str, tuple[str, dict]] = {}
    for label, path in (("data/towns_ny.json", PROD), ("data/test/wave2/config/towns_ny.json", W2_CONFIG),
                        ("data/test/wave1/config/towns_ny.json", W1_CONFIG)):
        for t in (load(path, {}) or {}).get("towns", []):
            out.setdefault(t["town"], (label, t))
    return out


def existing_rows() -> dict[str, dict]:
    return {t["town"]: t for t in (load(CONFIG_FILE, {}) or {}).get("towns", [])}


def write_config(rows_by_town: dict[str, dict]) -> None:
    order = list(dict.fromkeys(DEFAULT_PLACES + list(CURATED) + DEFAULT_COUNTIES))
    ordered = [rows_by_town[n] for n in order if n in rows_by_town] + \
        [r for n, r in rows_by_town.items() if n not in order]
    save(CONFIG_FILE, config_doc(ordered))


# ------------------------------------------------------------------------------------ discover
def cmd_discover(args) -> None:
    from watch351.discover_sites import discover_place
    from wave2_test import WEBSITES, county_label, patch_county_patterns
    wanted = [p.strip() for p in args.places.split(",")] if args.places else None
    rows = existing_rows()
    fetcher = PoliteFetcher()
    t0 = time.monotonic()
    todo = []
    if args.counties:
        patch_county_patterns()
        targets = {t["town"]: t for t in (load(W2_TARGETS, []) or []) if t.get("kind") == "county"}
        for name in wanted or DEFAULT_COUNTIES:
            county = name.replace(" County", "")
            t = targets.get(name) or {"town": name, "state": "NY", "county": county, "kind": "county",
                                      "selection_group": "county_planning",
                                      "selection_reason": "County planning board: GML 239-m referrals (follow-up 2026-11-03)"}
            sites = WEBSITES.get(name) or ([t["website"]] if t.get("website") else [])
            row = {k: v for k, v in t.items() if k not in ("website_candidates", "wikipedia", "domain_probe", "no_website_note")}
            row.update(website=sites[0] if sites else None, website_candidates=sites,
                       website_source=f"polite probe from the sandbox, 2026-11-03 (wave2_test.WEBSITES)" if sites else None,
                       followup_source="data/test/wave2/targets_ny.json")
            todo.append((row, ["planning_board"]))
    else:
        known = source_rows()
        for name in wanted or DEFAULT_PLACES:
            if name not in known:
                print(f"  {name}: no row in data/towns_ny.json or the wave configs; skipped")
                continue
            label, t = known[name]
            row = {k: v for k, v in t.items() if k not in ("listings", "board_evidence", "board_stale", "boards_found",
                                                             "boards_missing", "vendors", "robots_blocked", "notes",
                                                             "pages_fetched", "discovered_at", "platforms", "cms",
                                                             "warrants_found", "boards_by_platform", "_posted_rows")}
            sites = [u for u in (t.get("final_url"), t.get("website"), *(t.get("website_candidates") or [])) if u]
            row.update(website_candidates=list(dict.fromkeys(sites)), followup_source=label,
                       earlier_reason_code=t.get("reason_code"), earlier_reason=t.get("reason"))
            todo.append((row, list(ALL3)))

    def one(item):
        row, tracked = item
        best = None
        for site in row.get("website_candidates") or [row.get("website")]:
            r0 = {k: v for k, v in row.items() if k != "website_candidates"}
            r0["website"] = site
            r0["town"] = re.sub(r"\s+\(.*\)$", "", row["town"])
            try:
                r = discover_place(fetcher, r0, "NY", tracked)
                r["town"] = row["town"]
            except Exception as e:  # noqa: BLE001 - one site must not stop the run
                logging.exception("discovery crashed for %s", row["town"])
                r = {**r0, "status": "not_automated", "reason_code": "discovery_error", "automated": False,
                     "reason": f"{type(e).__name__}: {str(e)[:160]}", "listings": []}
            if best is None or r.get("automated") or best.get("reason_code") in ("unreachable", "website_mismatch", "http_error"):
                best = r
            if r.get("automated"):
                break
        best["website_candidates"] = row.get("website_candidates") or []
        best.pop("_posted_rows", None)
        if best.get("kind") == "county":
            best["attribute_townships"] = True
            pb = next((l for l in (best.get("listings") or []) if l.get("board_key") == "planning_board"), None)
            label = (pb or {}).get("board") or ""
            if not re.search(r"planning", label, re.I):
                label = county_label(best["county"])
            elif not re.search(re.escape(best["county"]), label, re.I):
                label = f"{best['county']} County {re.sub(r'^\\s*county\\s+', '', label, flags=re.I)}"
            best["county_body"] = label
        best["followup_discovered_at"] = now_iso()
        return best

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one, todo))
    for r in results:
        rows[r["town"]] = r
    write_config(rows)
    print(f"follow-up discovery: {len(results)} rows in {time.monotonic() - t0:.0f}s; fetcher {fetcher.stats}; "
          f"slow hosts {dict(fetcher.slow_host_docs)}")
    for r in results:
        print(f"  {r['town']:<20} {str(r.get('platform') or '-'):<13} {len(r.get('listings') or []):>2} "
              f"{'AUTO ' + ','.join(sorted(r.get('boards_found') or [])) if r.get('automated') else r.get('reason_code')}: "
              f"{'' if r.get('automated') else (r.get('reason') or '')[:140]}")
        for n in (r.get("notes") or [])[:6]:
            print(f"      note: {n[:150]}")


# ------------------------------------------------------------------------------------ curate
def cmd_curate(args) -> None:
    rows = existing_rows()
    known = source_rows()
    for name, cur in CURATED.items():
        base = rows.get(name) or {}
        if not base:
            label, t = known.get(name, ("", {"town": name, "state": "NY"}))
            base = {k: v for k, v in t.items() if k not in ("listings", "board_evidence", "board_stale", "boards_found",
                                                              "boards_missing", "vendors", "robots_blocked", "notes",
                                                              "pages_fetched", "discovered_at", "platforms", "cms",
                                                              "warrants_found", "boards_by_platform")}
            base.update(followup_source=label, earlier_reason_code=t.get("reason_code"), earlier_reason=t.get("reason"))
        opts = cur.get("listing_options")
        base.update({k: v for k, v in cur.items() if k != "listing_options"})
        if opts:   # options added to the listings discovery found (Lansing: linked_agenda)
            base["listings"] = [{**l, **opts} for l in base.get("listings") or []]
        base["status"] = "automated" if base.get("automated") else "not_automated"
        base["reason_code"] = base["reason"] = None
        base["boards_found"] = sorted({l["board_key"] for l in base.get("listings") or []})
        tracked = ["planning_board"] if base.get("kind") == "county" else ALL3
        base["boards_missing"] = [k for k in tracked if k not in base["boards_found"]]
        base["curated"] = True
        base["curated_at"] = now_iso()
        rows[name] = base
    write_config(rows)
    print("curated:", ", ".join(CURATED))


# ------------------------------------------------------------------------------------ munibit
def cmd_munibit(args) -> None:
    """The meeting lists the Munibit module gives, for the three towns, with the files' addresses; no document is
    fetched (the files are not served to the reader). -> data/test/ny_followup/munibit_meetings.json"""
    from watch351.adapters.munibit import MunibitAdapter
    f = PoliteFetcher()
    ad = MunibitAdapter(f)
    today = date.today()
    window = Window(today - timedelta(days=45), today + timedelta(days=120))
    out = {"generated": now_iso(), "window": {"start": window.start.isoformat(), "end": window.end.isoformat()},
           "note": "Meeting list from the Munibit module's JSON (adapters/munibit.py). viewer_url is the stable address "
                   "of each file; a plain GET of it returns the site's viewer page, not the file, and the download link "
                   "answers 'Access denied' to AgendaAheadBot, so no document text is read.", "towns": {}}
    for town, cur in CURATED.items():
        if cur.get("platform") != "munibit":
            continue
        pages = list(dict.fromkeys(l["url"] for l in cur["listings"]))
        try:
            with f.purpose("listing"):
                ms = ad.meetings(pages[0])
        except (FetchError, RuntimeError) as e:
            out["towns"][town] = {"error": str(e)[:200]}
            print(f"== {town}: {e}")
            continue
        inwin = [m for m in ms if m["date"] in window or
                 (m["date"] is None and m["month"] and window.start.strftime("%Y-%m") <= m["month"] <= window.end.strftime("%Y-%m"))]
        rec = {"library_files": len(ms), "in_window": len(inwin),
               "by_board": dict(Counter(m["board_key"] or "unclassified" for m in inwin)),
               "meetings": [{**m, "date": m["date"].isoformat() if m["date"] else None} for m in
                            sorted(inwin, key=lambda m: (str(m["date"] or m["month"]), m["title"]))]}
        out["towns"][town] = rec
        print(f"== {town}: {len(ms)} agenda / packet / notice files in the library, {len(inwin)} in the window {rec['by_board']}")
        for m in rec["meetings"]:
            print(f"   {str(m['date'] or m['month']):<10} {str(m['board_key']):<24} {m['kind']:<7} {m['title'][:48]:<48} {m['viewer_url'][:70]}")
    save(OUT / "munibit_meetings.json", out)
    print("wrote", OUT / "munibit_meetings.json", f"fetcher {f.stats}")


# ------------------------------------------------------------------------------------ crawl
def cmd_crawl(args) -> None:
    cmd = [sys.executable, "-m", "watch351.daily", "--data-dir", str(CONFIG), "--states", "NY", "--output-dir",
           str(CRAWL_OUT), "--hits-name", HITS_NAME, "--days-back", str(args.days_back), "--days-ahead", str(args.days_ahead),
           "--workers", str(args.workers), "--request-log", str(CRAWL_OUT / f"requests_{args.label}.tsv")]
    if args.places:
        cmd += ["--towns", args.places]
    CRAWL_OUT.mkdir(parents=True, exist_ok=True)
    print(" ".join(cmd))
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=CRAWLER)
    print(f"exit {proc.returncode}, wall {time.monotonic() - t0:.0f}s")
    runs = CRAWL_OUT / "state" / "runs"
    latest = max(runs.glob("*.json"), key=lambda p: p.stat().st_mtime, default=None)
    if latest:
        save(CRAWL_OUT / "runs" / f"run_{args.label}.json", load(latest))
        print(f"saved {CRAWL_OUT / 'runs' / f'run_{args.label}.json'}")


# ------------------------------------------------------------------------------------ report
def cmd_report(args) -> None:
    from watch351.state import DocIndex, load_health
    cfg = load(CONFIG_FILE, {}) or {}
    rows = cfg.get("towns", [])
    idx = DocIndex(CRAWL_OUT / "state" / "docs")
    by_town: dict[str, list[dict]] = defaultdict(list)
    for rec in idx.records():
        by_town[rec["town"]].append(rec)
    health = load_health(CRAWL_OUT / "state" / "town_health.json")
    runs = sorted((CRAWL_OUT / "state" / "runs").glob("*.json"))
    report = load(runs[-1]) if runs else {}
    hits = (load(CRAWL_OUT / HITS_NAME, {}) or {}).get("hits", [])
    munibit = load(OUT / "munibit_meetings.json", {}) or {}
    out_rows = []
    lines = [f"# New York follow-up: what reads now ({TODAY})", "",
             f"Built by `python3 experiments/ny_followup.py report` from data/test/ny_followup/ (config, crawl run "
             f"{report.get('date')}, index {idx.stats().get('documents', 0)} documents). Nothing here is in production.", "",
             "| Place | Platform | Status | Boards read | Documents (dated) | Meeting dates | Hits | Reason / errors |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        recs = by_town.get(r["town"], [])
        ok = [x for x in recs if x.get("status") == "ok"]
        dated = sorted(x["meeting_date"] for x in ok if x.get("meeting_date"))
        h = health.get(f"NY:{r['town']}") or {}
        errs = [e["error"] for e in report.get("errors", []) if e.get("town") == f"NY:{r['town']}"]
        n_hits = sum(1 for x in hits if x.get("town") == r["town"])
        if r.get("automated"):
            status = h.get("status") or "not run"
            reason = "; ".join(dict.fromkeys(e[:160] for e in errs)) if errs else ""
        else:
            status = "not automated"
            reason = f"{r.get('reason_code')}: {(r.get('reason') or '')[:200]}"
        if r.get("platform") == "munibit" and r["town"] in munibit.get("towns", {}):
            m = munibit["towns"][r["town"]]
            if "error" not in m:
                reason = (f"meeting list read: {m['in_window']} agenda files in the window {m['by_board']}; files not served "
                          f"to the reader (see munibit_meetings.json). " + reason)
        boards = sorted(h.get("boards_ok") or []) if r.get("automated") else []
        span = f"{dated[0]} to {dated[-1]}" if dated else ""
        out_rows.append({"town": r["town"], "kind": r.get("kind"), "county": r.get("county"), "platform": r.get("platform"),
                         "automated": bool(r.get("automated")), "status": status, "boards_ok": boards,
                         "boards_failed": sorted(h.get("boards_failed") or []), "documents_ok": len(ok),
                         "documents_dated": len(dated), "meeting_dates": dated, "hits": n_hits, "reason": reason,
                         "listings": r.get("listings") or [], "earlier_reason_code": r.get("earlier_reason_code"),
                         "website": r.get("final_url") or r.get("website")})
        lines.append(f"| {r['town']} | {r.get('platform') or '-'} | {status} | {', '.join(boards) or '-'} | "
                     f"{len(ok)} ({len(dated)}) | {span or '-'} | {n_hits} | {reason.replace('|', '/')[:300]} |")
    lines += ["", "## Notes (read by hand on 2026-11-03)", ""]
    for r in rows:
        if r["town"] in NOTES:
            lines.append(f"- **{r['town']}**: {NOTES[r['town']]}")
    lines += ["", "## Document records", ""]
    for r in rows:
        recs = sorted(by_town.get(r["town"], []), key=lambda x: (x.get("meeting_date") or "", x.get("board") or ""))
        if not recs:
            continue
        lines.append(f"### {r['town']}")
        lines.append("")
        for x in recs:
            lines.append(f"- {x.get('meeting_date') or 'undated'} · {x.get('board')} · {x.get('status')} · "
                         f"{(x.get('text_source') or '-')} · {len(x.get('hits') or [])} hits · {x['url']}"
                         + (f" · {x.get('error', '')[:120]}" if x.get("status") == "error" else ""))
        lines.append("")
    save(OUT / "report.json", {"generated": now_iso(), "run": report.get("date"), "rows": out_rows,
                               "network": report.get("network")})
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:4 + len(rows)]))
    print("wrote", OUT / "report.md", "and report.json")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["discover", "curate", "munibit", "crawl", "report"])
    p.add_argument("--places")
    p.add_argument("--counties", action="store_true", help="discover: the county planning boards instead of the places")
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--label", default="run1")
    p.add_argument("--days-back", type=int, default=45)
    p.add_argument("--days-ahead", type=int, default=120)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    globals()[f"cmd_{args.command}"](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
