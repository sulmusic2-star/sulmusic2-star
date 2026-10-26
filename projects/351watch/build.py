"""Render the static site from the data/ files (the product name is SITE_NAME below).

Inputs (data/): hits_current.json (the alert-data contract in ARCHITECTURE.md; falls back to
agenda_hits_ma_all.json), towns_*.json (one per state), tracker.json, ag_decisions.json,
ma_census_summary.json, leadtime_ma_all.json and, when present, state/town_health.json.
geo/town_points.json holds each town's Census centroid for the dot maps.

Usage: python3 build.py          (SITE_STATES=MA python3 build.py publishes only the listed states)
Writes site/: index, towns, <state>/<town-slug> for every town, topics, topics/<slug>, search,
watch (alert setup), w (alert list viewer), how-it-works, attorney-general, pricing, redirect pages
for the old /proof, /privacy and /bot URLs, maps/*.svg, sitemap.xml, robots.txt, data/towns.json
(the town index the API validates against) and data/lines.json (item lines for the alert pages). The deploy step copies these plus data/hits_current.json.

Site structure, built around what visitors come to do:
  /               what's coming up in your town: town box, the biggest stories this week, map
  /trending       the biggest stories coming up (data/trending.json), "For you" re-ranked in the browser
  /upcoming       every upcoming meeting about solar, batteries, data centers, zoning, housing or cell towers
  /<st>/<town>    one town: the next 7 days, what's coming up, earlier meetings, nearby towns, boards read
  /watch          residents' alerts: a town, the towns next to it, subjects, email; /w/<key> shows them
  /alerts-for-groups  the same, plus Slack, Teams or Discord webhooks, names and per-town choices
  /search         full-text search over every agenda (site/search.js fills the results)
  /how-it-works   coverage, timing, the Attorney General record, the crawler, privacy, contact
"""

import csv
import io
import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from html import escape
import sys
from pathlib import Path
from urllib.parse import quote, urlparse
from zoneinfo import ZoneInfo

import trending as TR  # the Trending page's classifier: one reading of each agenda item for every page
import briefs as BR  # written briefs: storage, loading and the verifier (tools/verify_briefs.py)

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE = ROOT / "site"
GEO = ROOT / "geo"
# Canonical base for links, sitemaps and canonical tags. Switches to https://agendaahead.com once the domain is live.
BASE_URL = "https://agendaahead.vercel.app"
# The product name, used everywhere it appears (titles, wordmark, copy). A new name is being chosen;
# change it here. The wordmark in styles.css (.brand) fits any short name.
SITE_NAME = "Agenda Ahead"
# Who runs the site (the owner's choice; still to come). While OWNER_NAME is the placeholder the line
# isn't shown anywhere. OWNER_TOWN is optional ("Carver").
OWNER_NAME = "OWNER_NAME_TBD"
OWNER_TOWN = ""
OWNER_LINE = ("" if OWNER_NAME.endswith("_TBD") else
              f"{SITE_NAME} is run by {OWNER_NAME}{' in ' + OWNER_TOWN if OWNER_TOWN else ''}, Massachusetts. "
              "It isn’t part of any town government, developer or advocacy group.")


def owner_html(cls="owner"):
    return f'<p class="{cls}">{escape(OWNER_LINE)}</p>' if OWNER_LINE else ""
# The crawler's name and the User-Agent it sends (shown on How it works, #crawler).
BOT_NAME = "AgendaAheadBot"
BOT_UA = "AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)"

STATE_NAMES = {
    "MA": "Massachusetts", "NY": "New York", "RI": "Rhode Island", "CT": "Connecticut", "NH": "New Hampshire",
    "VT": "Vermont", "ME": "Maine", "NJ": "New Jersey", "PA": "Pennsylvania",
}

STATUS_GROUPS = {
    "active": ({"Adopted", "Approved by AG", "Enacted", "In effect"}, "In effect or adopted"),
    "pending": ({"Proposed", "Hearing held", "On warrant", "Pending at Legislature"}, "Pending"),
    "cleared": ({"Rejected", "Withdrawn", "Expired", "Disapproved by AG", "Sent to study"}, "Not in effect"),
}

# Topic names as people say them. The keys are the data contract (ARCHITECTURE.md).
TOPIC_LABELS = {
    "solar": "Solar",
    "battery_storage": "Battery storage",
    "data_center": "Data centers",
    "moratorium": "Moratoriums",
    "clean_energy_siting": "Clean-energy permit rules",
    "zoning_amendment": "Zoning changes",
    "40b_comprehensive_permit": "Affordable housing (40B)",
    "wireless_telecom": "Cell towers",
    "wetlands_filing": "Wetlands permits",
    # Used by the gated Vermont feed so far; the forms list them once a state we show has items on them.
    "extraction": "Quarries and gravel pits",
    "large_development": "Large developments",
}
GATED_TOPICS = {"extraction", "large_development"}
# The same topics inside a sentence: (phrase, plural?)
TOPIC_PHRASES = {
    "solar": ("solar", False),
    "battery_storage": ("battery storage", False),
    "data_center": ("data centers", True),
    "moratorium": ("a moratorium", False),
    "clean_energy_siting": ("clean-energy permit rules", True),
    "zoning_amendment": ("a zoning change", False),
    "40b_comprehensive_permit": ("affordable housing", False),
    "wireless_telecom": ("cell towers", True),
    "wetlands_filing": ("a wetlands filing", False),
    "extraction": ("a quarry or gravel pit", False),
    "large_development": ("a large development", False),
}
TOPIC_ORDER = list(TOPIC_LABELS)
DEFAULT_TOPICS = ["solar", "battery_storage", "data_center", "moratorium", "clean_energy_siting"]
HERO_TOPICS = set(DEFAULT_TOPICS)

BOARD_NAMES = {
    "planning_board": "Planning board",
    "zoning_board_of_appeals": "Zoning board of appeals",
    "conservation_commission": "Conservation commission",
    "select_board": "Select board or city council",
    "town_meeting": "Town Meeting",
}

# Why we can't check a town's agendas, said plainly ({town} is filled in; "the town" when no town is named).
REASON_TEXT = {
    "bot_challenge": "{town}’s website shows a check meant to stop programs like ours, and we don’t get around it",
    "waf_block": "{town}’s website turns away programs like ours",
    "robots_disallow_site": "{town}’s website asks programs like ours to stay away, and we respect that",
    "vendor_blocked": "The company that hosts {town}’s agendas turns away programs like ours",
    "vendor_robots_disallow": "The company that hosts {town}’s agendas asks programs like ours to stay away, and we respect that",
    "js_only": "{town}’s agenda page only works in a full web browser, which our program can’t use yet",
    "no_adapter": "{town} posts agendas on a system our program can’t open yet",
    "no_agenda_listing_found": "We couldn’t find where {town} posts its agendas",
    "agendas_stale_or_undated": "{town}’s website has no recent agendas with dates on them",
    "crawl_delay_exceeds_cap": "{town}’s website asks programs like ours to visit less than once a day",
}
REASON_LABELS = {k: v.replace("{town}’s", "the town’s").replace("{town}", "the town") for k, v in REASON_TEXT.items()}
# The short form, for a list: "(can’t read yet: its site blocks programs)".
REASON_SHORT = {
    "bot_challenge": "its site runs a bot check",
    "waf_block": "its site turns away programs",
    "robots_disallow_site": "its site asks programs to stay away",
    "vendor_blocked": "its agenda host turns away programs",
    "vendor_robots_disallow": "its agenda host asks programs to stay away",
    "js_only": "its agenda page needs a full browser",
    "no_adapter": "a system we can’t open yet",
    "no_agenda_listing_found": "no agenda listing found",
    "agendas_stale_or_undated": "no dated agendas on its site",
    "crawl_delay_exceeds_cap": "its site allows fewer visits than one a day",
}


def reason_text(code, town):
    return REASON_TEXT.get(code, "Our program can’t read {town}’s agenda pages yet").replace("{town}", town)



# Agenda platforms as readers know them (town configs store the crawler's adapter names).
PLATFORM_NAMES = {
    "civicplus": "CivicPlus Agenda Center",
    "civicclerk": "CivicClerk",
    "legistar": "Legistar",
    "escribe": "eSCRIBE",
    "generic": "the {kind} website",
    "generic_ny": "the {kind} website",
    "ri_sos": "the Rhode Island Secretary of State's open meetings portal",
}

# Topic landing pages: slug to data topic key, plus how to pick related tracker and AG rows.
TOPIC_PAGES = [
    {"slug": "solar", "key": "solar", "name": "Solar",
     "matches": "solar or photovoltaic (PV) projects and bylaws",
     "tracker": lambda i: "solar" in i.get("topic", "").lower(),
     "ag": lambda r: r.get("technology") in ("solar", "both")},
    {"slug": "battery-storage", "key": "battery_storage", "name": "Battery storage",
     "matches": "battery energy storage (BESS)",
     "tracker": lambda i: "battery" in i.get("topic", "").lower(),
     "ag": lambda r: r.get("technology") in ("BESS", "both") or "BESS" in r.get("technology", "")},
    {"slug": "data-centers", "key": "data_center", "name": "Data centers",
     "matches": "data centers, hyperscale facilities or cryptocurrency mining",
     "tracker": lambda i: False,
     "ag": lambda r: "data cent" in (r.get("summary", "") + r.get("article", "")).lower()},
    {"slug": "moratoria", "key": "moratorium", "name": "Moratoriums",
     "matches": "a moratorium of any kind",
     "tracker": lambda i: "moratorium" in i.get("action", "").lower(),
     "ag": lambda r: r.get("bylaw_type") == "moratorium"},
    {"slug": "consolidated-permit", "key": "clean_energy_siting", "name": "Clean-energy permit rules",
     "matches": "the state's new consolidated local permit for small clean-energy projects (225 CMR 29.00)",
     "tracker": lambda i: i.get("action") == "Consolidated permit",
     "ag": lambda r: r.get("bylaw_type") == "consolidated permit bylaw"},
    {"slug": "zoning", "key": "zoning_amendment", "name": "Zoning changes",
     "matches": "changes to a town's zoning bylaw or zoning map",
     "tracker": lambda i: False,
     "ag": lambda r: r.get("bylaw_type") == "zoning regulation"},
    {"slug": "40b-housing", "key": "40b_comprehensive_permit", "name": "Affordable housing (40B)",
     "matches": "comprehensive permits under Chapter 40B, the state law that lets a housing project with affordable homes "
                "skip some local zoning rules",
     "tracker": lambda i: False, "ag": lambda r: False},
    {"slug": "cell-towers", "key": "wireless_telecom", "name": "Cell towers",
     "matches": "cell towers and other wireless antennas",
     "tracker": lambda i: False, "ag": lambda r: False},
    {"slug": "wetlands", "key": "wetlands_filing", "name": "Wetlands permits",
     "matches": "Conservation Commission hearings and state wetlands filings for energy and data-center projects",
     "tracker": lambda i: False, "ag": lambda r: False,
     # the Conservation Commission's hearings are the wetlands permits people go to, not only the state filings
     "hits": lambda h: "wetlands_filing" in h.get("topics", []) or (
         h.get("board_key") == "conservation_commission" and set(h.get("topics", [])) & {"solar", "battery_storage", "data_center"})},
]
TOPIC_PAGE_BY_KEY = {tp["key"]: tp for tp in TOPIC_PAGES}

TRACER_LANE = "2022-06-02"
# G.L. c. 40A, § 3 protects solar by statute. Battery storage has that protection only through Land Court
# (trial court) rulings, so it is not settled law for batteries. Used on /attorney-general and /how-it-works.
LAW_SOLAR = ("State zoning law (G.L. c. 40A, § 3, ninth paragraph) says no zoning bylaw or ordinance may prohibit or unreasonably "
             "regulate solar energy systems, or the structures that facilitate collecting solar energy, except where necessary to "
             "protect public health, safety or welfare. It binds cities as well as towns.")
LAW_BATTERY = ("Battery storage has that protection only through Land Court rulings that read a battery as a structure that "
               "facilitates collecting solar energy, and the Land Court is a trial court, so for batteries this isn’t settled law the "
               "way it is for solar. The rulings are NextSun Energy LLC v. Fernandes (Norton, May 9, 2023), Duxbury Energy Storage, LLC "
               "v. Town of Duxbury Zoning Board of Appeals (June 23, 2025) and Town of Wendell v. Campbell (March 12, 2026), which "
               "upheld the Attorney General’s disapproval of a licensing bylaw for battery storage; all three follow the Supreme Judicial "
               "Court’s reasoning in Tracer Lane II Realty, LLC v. City of Waltham (2022).")
e = escape


# ---------------------------------------------------------------- helpers

def load_clerks():
    """Town clerk phone numbers, {"MA:Hadley": "(413) 586-0221"}, from ref/ma_town_clerks.csv (town,phone) when
    someone has added it. The Secretary of the Commonwealth's clerk directory is the source to copy from."""
    path = ROOT / "ref" / "ma_town_clerks.csv"
    if not path.exists():
        return {}
    import csv
    with path.open() as f:
        return {f"MA:{r['town'].strip()}": r["phone"].strip() for r in csv.DictReader(f) if r.get("town") and r.get("phone")}


CLERKS = {}
CITIES = set()  # "MA:Pittsfield": a city, which adopts ordinances and has no Town Meeting
REP_TM = set()  # "MA:Dartmouth": a Representative Town Meeting, where elected members vote


# Hits about something else (a PFAS moratorium, a utility's pole petition, a general-ordinance amendment) are the
# engine's call, so the pages and hits_current.json agree: watch351.keywords.off_subject.
sys.path.insert(0, str(ROOT / "crawler"))
from watch351.keywords import off_subject  # noqa: E402


def load(name, default):
    path = DATA / name
    return json.loads(path.read_text()) if path.exists() else default


def slugify(name):
    return re.sub(r"\s+", "-", name.lower().replace("'", "").replace("’", ""))


def town_path(state, town):
    return f"/{state.lower()}/{slugify(town)}"


def alerts_url(town_id=None, topics=None):
    params = []
    if town_id:
        params.append("town=" + quote(town_id, safe=""))
    if topics:
        params.append("topic=" + quote(",".join(topics), safe=","))
    return "/watch" + ("?" + "&".join(params) if params else "")


def status_group(item):
    if item.get("action") == "Consolidated permit":
        return "info"
    for group, (statuses, _) in STATUS_GROUPS.items():
        if item.get("status") in statuses:
            return group
    return "pending"


def fmt_date(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").strftime("%b %-d, %Y")
    except ValueError:
        return escape(value)


def plural(n, word, many=None):
    return f"{n:,} {word if n == 1 else (many or word + 's')}"


def join_and(parts):
    parts = [p for p in parts if p]
    if len(parts) < 3:
        return " and ".join(parts)
    return f"{', '.join(parts[:-1])} and {parts[-1]}"


def median(values):
    values = sorted(values)
    return values[len(values) // 2] if values else 0


def pct(x):
    return f"{x * 100:.0f}%"


def today_et():
    return datetime.now(ZoneInfo("America/New_York")).date().isoformat()


def sources_html(sources):
    links = "".join(
        f'<li><a href="{e(s["url"])}" rel="nofollow noopener" target="_blank">{e(s["title"])}</a></li>'
        for s in sources
        if s.get("url")
    )
    return f'<ul class="sources">{links}</ul>' if links else ""


def outcome_class(outcome):
    o = (outcome or "").lower()
    if o.startswith("disapproved") or "upheld" in o:
        return "active"
    if o == "approved in part":
        return "pending"
    if o.startswith("approved") or "annulled" in o or "vacated" in o or "enforced" in o or "protected" in o:
        return "cleared"
    return "info"


PLAIN_AG = [
    (r"\s*\(latest found\)", ""),
    (r"\(Exact date not printed in the copy reviewed; it was reported ([^)]+?)\.?\)", r"(Reported \1.)"),
    (r"is not named in the AG's citation and was not verified here", "isn’t named in the Attorney General’s citation"),
    (r"locally regulated commercial battery energy storage systems \(LRC-BESS\)", "locally regulated commercial battery storage"),
    (r"\bLRC-BESS\b", "commercial battery storage"),
    (r"clean energy \(SCEI incl\. BESS\)", "small clean energy projects, including battery storage"),
    (r"\bSCEIF?\b", "small clean energy projects"),
    (r"\bBESS\b", "battery storage"),
    (r"\bAG's\b|\bAG’s\b", "Attorney General’s"),
    (r"\bAG\b", "Attorney General"),
    (r"\bDOER's\b|\bDOER’s\b", "the state energy department’s"),
    (r"\bDOER\b", "the state energy department"),
    (r"\bSJC\b", "Supreme Judicial Court"),
    (r"\bEFSB\b", "Siting Board"),
    (r"\bZBA\b", "Zoning Board of Appeals"),
    (r"constructively approved", "treated as approved"),
    (r"\bmoratoria\b", "moratoriums"),
    (r"\bMoratoria\b", "Moratoriums"),
    (r"(\d{4}) ATM\b", r"\1 Annual Town Meeting"),
    (r"(\d{4}) STM\b", r"\1 Special Town Meeting"),
    (r"\bATM\b", "Annual Town Meeting"),
    (r"\bSTM\b", "Special Town Meeting"),
    (r"\bs\. 3\b", "§ 3"),
    (r"Found by the (?:351 Watch|Agenda Ahead) agenda scan\.", "From the town’s posted agenda."),
    (r"\bSept\.?(?=\s\d)", "Sep"),
    (r"\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.(?=\s\d)", r"\1"),
    (r"Seen on the town’s posted agenda\.", "From the town’s posted agenda."),
]


def plain_ag(text):
    """Research notes in the rulings data, in plain words: no working notes, abbreviations spelled out."""
    t = text or ""
    for pat, sub in PLAIN_AG:
        t = re.sub(pat, sub, t)
    # A spelled-out name that replaced an abbreviation at the start of a sentence keeps the capital.
    return re.sub(r"(^|[.!?]\s+)the (state energy department|Attorney General)", lambda m: f"{m.group(1)}The {m.group(2)}", t)


def first_up(text):
    return text[:1].upper() + text[1:] if text else text


def ag_town(name):
    return re.sub(r"\s*\((city|town)\)$", "", name or "").strip()


def ag_articles(r):
    return max(1, r.get("article", "").count(" and ") + 1)  # "Articles 26 and 27" counts 2


class Ctx:
    """Everything the pages are rendered from."""

    def __init__(self):
        self.today = today_et()
        self.tracker = load("tracker.json", {"generated": date.today().isoformat(), "framework": [], "items": []})
        for item in self.tracker.get("items", []):  # summaries written under the old product name
            item["summary"] = plain_ag((item.get("summary") or "").replace("351 Watch", SITE_NAME))
            for k in ("action", "status", "topic", "date_label"):
                item[k] = plain_ag(item.get(k) or "")
        for f in self.tracker.get("framework", []):
            f["title"] = plain_ag(f.get("title") or "")
            f["summary"] = plain_ag(f.get("summary") or "")
        self.census = load("ma_census_summary.json", {})
        self.leadtime = load("leadtime_ma_all.json", {})
        self.ag = load("ag_decisions.json", [])
        for r in self.ag:
            for k in ("summary", "article", "outcome", "technology", "bylaw_type", "legal_basis"):
                if isinstance(r.get(k), str):
                    r[k] = plain_ag(r[k])
            if (r.get("town") or "").startswith("Not named"):
                r["town"] = "Town not named in the ruling"
        self.health = load_health()
        all_towns = load_towns()
        self.hits_doc = load_hits({t["id"]: t for t in all_towns})
        # A state is published (town pages, alert picker, API validation) once the daily
        # engine includes it in hits_current.json; town configs for pilot states stay private.
        published = set(self.hits_doc.get("states") or []) | {"MA"}
        if os.environ.get("SITE_STATES"):
            published &= {s.strip().upper() for s in os.environ["SITE_STATES"].split(",")} | {"MA"}
        self.states = sorted(published, key=lambda s: (s != "MA", s))
        self.towns = [t for t in all_towns if t["state"] in self.states]
        self.town_by_id = {t["id"]: t for t in self.towns}
        CITIES.update(t["id"] for t in self.towns if t.get("kind") == "city")
        REP_TM.update(t["id"] for t in self.towns if t.get("legislative_body") == "Representative Town Meeting")
        for item in self.tracker.get("items", []):
            if f"{item.get('state', 'MA')}:{item['town']}" in CITIES:
                item["action"] = re.sub(r"\b[Bb]ylaw\b", "ordinance", item["action"])
                item["summary"] = item["summary"].replace("From the town’s posted agenda.", "From the city’s posted agenda.")
        # Decision letters: when one case number has several letters (Carver 10941: battery storage on
        # Nov 10, 2023, solar on Nov 13), each letter is named by its subject.
        by_case = defaultdict(set)
        for r in self.ag:
            if r.get("case_number"):
                by_case[str(r["case_number"])].add(r.get("portal_document_name") or "")
        for r in self.ag:
            names = by_case.get(str(r.get("case_number") or ""), set())
            subject = (r.get("portal_document_name") or "").rsplit(" - ", 1)[-1].strip()
            # a note the data carries ("revised letter") stands when the case has one letter
            if len(names) > 1 and subject and not subject[0].isdigit() and subject.lower() not in ("letter", "decision") \
                    and ag_town(r.get("town") or "").lower() not in subject.lower():
                r["letter_note"] = f" ({subject.lower()} letter)"
            elif len(names) > 1 and r.get("decision_date"):
                r["letter_note"] = f" (letter dated {fmt_date(r['decision_date'])})"
            else:
                r["letter_note"] = r.get("letter_note") or ""
        self.hits = [h for h in self.hits_doc["hits"] if h.get("state", "MA") in self.states and not off_subject(h)]
        # A warrant read twice, once with its date and once without: the undated twin is dropped.
        dated = {(h["state"], h["town"], quote_key(h.get("snippet") or "")[:80]) for h in self.hits
                 if h.get("board_key") == "town_meeting" and h.get("meeting_date")}
        self.hits = [h for h in self.hits if not (h.get("board_key") == "town_meeting" and not h.get("meeting_date")
                                                  and (h["state"], h["town"], quote_key(h.get("snippet") or "")[:80]) in dated)]
        TODAY[0] = self.today
        self.tr_inputs = TR.load_inputs(str(DATA))
        TR_INPUTS[0] = self.tr_inputs
        for r in self.ag:
            AG_BY_TOWN.setdefault(f"MA:{ag_town(r.get('town'))}", []).append(r)
        today_d = date.fromisoformat(self.today)
        for h in self.hits:
            try:
                a = TR.analyze_hit(h, self.tr_inputs, today_d)
            except Exception:  # an item the classifier can't place keeps the rule-based sentence
                continue
            ANALYSIS[h["id"]] = a
            if not h.get("meeting_date") and a.get("date_source") == "warrant" and a.get("date"):
                h["meeting_date"] = a["date"].isoformat()  # read from the warrant, as Trending does
        # Minutes of an earlier meeting printed in an agenda packet aren't agenda items. A Town Meeting warrant is
        # never minutes, even when an article names the committee meeting before it (Auburn's Article 20).
        self.hits = [h for h in self.hits if (ANALYSIS.get(h["id"]) or {}).get("action") != "minutes"
                     or h.get("board_key") == "town_meeting"]
        # A warrant dated from its own text, older than the hits window, is an old warrant the town's site
        # still lists (Whately's 2012 to 2019 warrants), not an item for these pages.
        win_start = (self.hits_doc.get("window") or {}).get("start") or ""
        self.hits = [h for h in self.hits if not (win_start and (ANALYSIS.get(h["id"]) or {}).get("date_source") == "warrant"
                                                  and (h.get("meeting_date") or "") < win_start)]
        # Written briefs: only those the verifier passed, checked again here against the agenda text, so
        # nothing unverified renders.
        self.briefs_dropped = 0
        hit_by_id = {h["id"]: h for h in self.hits}
        town_dates = defaultdict(set)
        for st, town, _, d in self.tr_inputs.get("history") or []:
            if d:
                town_dates[f"{st}:{town}"].add(d.isoformat())
        for tid, held in BR.search_dates(str(DATA)).items():  # every agenda we hold, with or without items
            town_dates[tid].update(held)
        for bid, b in BR.load_briefs(str(DATA), verified_only=True).items():
            h = hit_by_id.get(bid)
            if not h:
                continue
            doc = (self.tr_inputs.get("docs") or {}).get(h["source_url"]) or {}
            wrong_doc = bool(b.get("source_url")) and b["source_url"] != h["source_url"]
            year = int(h["meeting_date"][:4]) if h.get("meeting_date") else None
            if wrong_doc or BR.verify(b, doc.get("text") or "", town_dates.get(f"{h['state']}:{h['town']}", set()), year):
                self.briefs_dropped += 1
                continue
            BRIEFS[bid] = moratorium_word(b)
        # A writer's "(not a solar item)" is honest, but a reader doesn't need the item at all: it goes with the
        # off-subject hits (the CSV and the copied week already left it out).
        self.hits = [h for h in self.hits if not OFF_ITEM.search((BRIEFS.get(h["id"]) or {}).get("line") or "")]
        for h in self.hits:  # a Town Meeting warrant a town posts under its Select Board listing is a Town Meeting
            if h.get("board_key") != "town_meeting" and TM_TITLE.search(h.get("document_title") or ""):
                h["board"], h["board_key"] = "Town Meeting", "town_meeting"
        for h in self.hits:
            h["topics"] = item_topics(h)
        # The meeting date of each document, also for warrants dated from their own text (as Trending does).
        self.doc_dates = {}
        for h in self.hits:
            if h.get("meeting_date"):
                self.doc_dates.setdefault(h["source_url"], h["meeting_date"][:10])
        self.hits_by_town = defaultdict(list)
        for h in self.hits:
            self.hits_by_town[f"{h['state']}:{h['town']}"].append(h)
        self.tracker_by_town = defaultdict(list)
        for i in self.tracker.get("items", []):
            self.tracker_by_town[f"{i.get('state', 'MA')}:{i['town']}"].append(i)
        self.ag_by_town = defaultdict(list)
        for r in self.ag:
            self.ag_by_town[f"MA:{ag_town(r.get('town'))}"].append(r)
        window = self.hits_doc.get("window") or {}
        self.window = (window.get("start"), window.get("end"))
        self.checked = fmt_date((self.hits_doc.get("generated") or self.today)[:10])
        self.checked_day = datetime.strptime((self.hits_doc.get("generated") or self.today)[:10], "%Y-%m-%d").strftime("%a %b %-d")
        generated = datetime.fromisoformat((self.hits_doc.get("generated") or f"{self.today}T12:00:00+00:00").replace("Z", "+00:00"))
        self.new_since = (generated - timedelta(hours=48)).astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S")
        self.first_sweep = {}
        self.older = {}  # (state, town) -> snippets of items seen before the "new" window, so a re-posted item isn't "New"
        for h in self.hits:
            if h.get("first_seen") and (h["state"] not in self.first_sweep or h["first_seen"] < self.first_sweep[h["state"]]):
                self.first_sweep[h["state"]] = h["first_seen"]
            if (h.get("first_seen") or "") < self.new_since:
                self.older.setdefault((h["state"], h["town"]), []).append(h.get("snippet") or "")
        # The top of each agenda (for the meeting's time and place) and every agenda we have, by town
        # (for which boards have posted their next agenda).
        self.headers = {}
        for path in sorted((DATA / "search").glob("*/*.jsonl")):
            for line in path.open():
                d = json.loads(line)
                if d.get("url"):
                    self.headers[d["url"]] = (d.get("text") or "")[:1500]
        self.docs_by_town = defaultdict(list)
        for path in sorted((DATA / "state" / "docs").glob("*/*.jsonl")):
            for line in path.open():
                d = json.loads(line)
                if d.get("town") and d.get("state"):
                    self.docs_by_town[f"{d['state']}:{d['town']}"].append(d)
        points = {}
        if (GEO / "town_points.json").exists():
            points = json.loads((GEO / "town_points.json").read_text()).get("points", {})
        self.points = {k: v for k, v in points.items() if k in self.town_by_id}
        # Towns with solar, battery, data-center, moratorium or permit-rule items on upcoming agendas.
        self.hot = {f"{h['state']}:{h['town']}" for h in self.hits if self.is_upcoming(h) and HERO_TOPICS & set(h.get("topics", []))}
        self.maps = {g: DotMap(self, g) for g in MAP_GROUPS if any(s in self.states for s in MAP_GROUPS[g])}
        # Towns that share a border, {"MA:Carver": ["MA:Plymouth", ...]}, when another step has built it.
        # Free alerts cover a town plus these neighbors; without the file, town pages list the nearest towns.
        self.neighbors = {}
        for path in (DATA / "neighbors.json", SITE / "data" / "neighbors.json"):
            if path.exists():
                doc = json.loads(path.read_text())
                self.neighbors = {k: [n for n in v if n in self.town_by_id] for k, v in doc.items() if isinstance(v, list)}
                break

    def is_upcoming(self, h):
        return bool(h.get("meeting_date")) and h["meeting_date"] >= self.today

    def known_posting(self, state, found, meeting_date):
        start = self.first_sweep.get(state)
        if not (found and start):
            return False
        after = datetime.fromisoformat(start.replace("Z", "+00:00")) + timedelta(hours=24)
        if datetime.fromisoformat(found.replace("Z", "+00:00")) <= after:
            return False
        return not meeting_date or found[:10] <= meeting_date[:10]

    def is_new(self, h):
        """First seen in the 48 hours before this data was generated, and not by a state's first sweep
        (a day after its first finding: everything the first sweep finds was already there)."""
        seen = h.get("first_seen") or ""
        start = self.first_sweep.get(h["state"])
        if not (seen and start) or seen < self.new_since:
            return False
        after = datetime.fromisoformat(start.replace("Z", "+00:00")) + timedelta(hours=24)
        if datetime.fromisoformat(seen.replace("Z", "+00:00")) <= after:
            return False
        # "New" means new to the town: a hearing continued from last month, or an agenda the town re-posted, is not
        return not overlaps(h.get("snippet") or "", self.older.get((h["state"], h["town"]), []))

    def town_link(self, state, town, cls=""):
        c = f' class="{cls}"' if cls else ""
        if f"{state}:{town}" in self.town_by_id:
            return f'<a{c} href="{town_path(state, town)}">{e(town)}</a>'
        return e(town)

    def region(self):
        names = [STATE_NAMES.get(s, s) for s in self.states]
        return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"

    def window_text(self):
        start, end = self.window
        return f"meetings from {fmt_date(start)} to {fmt_date(end)}" if start and end else "the current window"

    def coverage(self):
        """[(state, towns read daily, towns listed)] for each published state."""
        out = []
        for s in self.states:
            towns = [t for t in self.towns if t["state"] == s]
            listed = (self.hits_doc.get("towns_monitored") or {}).get(s) if s == "MA" else None
            out.append((s, listed or sum(1 for t in towns if t["monitored"]), len(towns)))
        return out

    def coverage_text(self):
        return join_and(f"{'all ' + str(n) if m == n else f'{m} of {n}'} in {STATE_NAMES.get(s, s)}"
                        for s, m, n in self.coverage())

    def ahead_median(self):
        """Median days between first sighting and the meeting, for items whose meeting is still ahead."""
        return median(h["days_before_meeting"] for h in self.hits
                      if self.is_upcoming(h) and isinstance(h.get("days_before_meeting"), (int, float)))


def load_towns():
    """Rows from every data/towns_*.json (state defaults to MA), normalized for the pages."""
    rows, seen = [], set()
    for path in sorted(DATA.glob("towns_*.json")):
        doc = json.loads(path.read_text())
        towns = doc.get("towns", []) if isinstance(doc, dict) else doc
        for t in towns:
            if not isinstance(t, dict) or not t.get("town"):
                continue
            state = (t.get("state") or "MA").upper()
            tid = f"{state}:{t['town']}"
            if tid in seen:
                continue
            seen.add(tid)
            rows.append({
                **t,
                "state": state,
                "id": tid,
                "slug": slugify(t["town"]),
                "monitored": bool(t.get("automated")),
                "pop": t.get("pop_2024_est") or t.get("pop_2020") or 0,
            })
    return sorted(rows, key=lambda t: (t["state"] != "MA", t["state"], t["town"]))


def load_hits(town_by_id):
    """data/hits_current.json, or the older MA snapshot normalized to the same contract."""
    doc = load("hits_current.json", None)
    if doc is None:
        old = load("agenda_hits_ma_all.json", None) or load("agenda_hits.json", {"hits": []})
        import hashlib
        hits = []
        for h in old.get("hits", []):
            town = town_by_id.get(f"MA:{h['town']}", {})
            hid = hashlib.sha1(f"{h['source_url']}|{h.get('snippet', '')}".encode()).hexdigest()[:12]
            hits.append({**h, "id": hid, "state": "MA", "county": town.get("county"), "source": "agenda"})
        doc = {"generated": old.get("generated"), "window": old.get("window"), "states": ["MA"],
               "towns_monitored": {"MA": old.get("towns_automated", 0)}, "hits": hits}
    doc.setdefault("hits", [])
    return doc


def load_health():
    """data/state/town_health.json: {"MA:Town": {"last_success": iso, "status": ..., ...}} (optional)."""
    doc = load("state/town_health.json", None)
    if not isinstance(doc, dict):
        return None
    return {k: v for k, v in doc.items() if isinstance(v, dict)}


# ---------------------------------------------------------------- dot maps
# One dot per town at its Census centroid. Massachusetts and Rhode Island share a map (they touch);
# New York has its own. Purple dots are towns with solar, battery, data-center, moratorium or
# permit-rule items on upcoming agendas.

MAP_GROUPS = {"ma-ri": ("MA", "RI"), "ny": ("NY",)}
MAP_WIDTH = 640
MAP_COLORS = {"light": {"land": "#eef1ed", "dot": "#a9b3ac", "hot": "#7a2c80"},
              "dark": {"land": "#1d2421", "dot": "#56625b", "hot": "#d59bdc"}}


def map_group(state):
    return next((g for g, states in MAP_GROUPS.items() if state in states), None)


class DotMap:
    def __init__(self, ctx, group):
        self.group = group
        self.states = [s for s in MAP_GROUPS[group] if s in ctx.states]
        pts = {k: v for k, v in ctx.points.items() if k.split(":", 1)[0] in self.states}
        self.ok = len(pts) > 2
        if not self.ok:
            self.xy, self.w, self.h, self.r = {}, MAP_WIDTH, 1, 1
            return
        lats = [v[0] for v in pts.values()]
        lons = [v[1] for v in pts.values()]
        k = math.cos(math.radians((min(lats) + max(lats)) / 2))
        pad = 14
        scale = (MAP_WIDTH - 2 * pad) / ((max(lons) - min(lons)) * k)
        self.w = MAP_WIDTH
        self.h = round((max(lats) - min(lats)) * scale + 2 * pad)
        self.xy = {tid: (round(pad + (lo - min(lons)) * k * scale, 1), round(pad + (max(lats) - la) * scale, 1))
                   for tid, (la, lo) in pts.items()}
        self.r = 4.4 if len(pts) > 150 else 6
        self.km_per_unit = 111.0 / scale  # degrees of latitude to km, per viewBox unit

    def name(self):
        return join_and(STATE_NAMES[s] for s in self.states)

    def svg(self, ctx, links="hot", cls="dotmap"):
        """Inline map. links: 'hot' links purple dots only, 'all' links every dot. The map is
        hidden from screen readers; the page lists the same towns as text."""
        parts = []
        for tid, (x, y) in sorted(self.xy.items(), key=lambda kv: kv[0] in ctx.hot):
            hot = tid in ctx.hot
            state, town = tid.split(":", 1)
            dot = f'<circle class="dot{" hot" if hot else ""}" cx="{x}" cy="{y}" r="{self.r}"><title>{e(town)}, {state}</title></circle>'
            if links == "all" or (links == "hot" and hot):
                dot = f'<a href="{town_path(state, town)}" tabindex="-1">{dot}</a>'
            parts.append(dot)
        return (f'<svg class="{cls}" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'aria-hidden="true" focusable="false">{"".join(parts)}</svg>')

    def file_svg(self, ctx, theme):
        """Standalone map image (presentation attributes only, so it renders under the CSP)."""
        c = MAP_COLORS[theme]
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="{self.r * 0.8:.1f}" fill="{c["hot"] if tid in ctx.hot else c["dot"]}"/>'
                       for tid, (x, y) in sorted(self.xy.items(), key=lambda kv: kv[0] in ctx.hot))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                f'<rect width="100%" height="100%" fill="{c["land"]}"/>{dots}</svg>\n')

    def nearby(self, ctx, tid, n=8):
        if tid not in self.xy:
            return []
        x0, y0 = self.xy[tid]
        dist = sorted(((math.hypot(x - x0, y - y0), other) for other, (x, y) in self.xy.items() if other != tid))
        return [(other, d * self.km_per_unit) for d, other in dist[:n]]


# ---------------------------------------------------------------- shared markup

NAV = [
    ("/upcoming", "Coming up"),
    ("/towns", "Towns"),
    ("/topics", "Topics"),
    ("/attorney-general", "Rulings"),
    ("/search", "Search"),
]
FOLLOW = ("/watch", "Follow a town")
FOOTER_EXPLORE = [("/upcoming", "Coming up"), ("/trending", "Biggest stories"), ("/towns", "Towns"), ("/topics", "Topics"),
                  ("/attorney-general", "Rulings"), ("/search", "Search")]
FOOTER_ABOUT = [("/how-it-works", "How it works"), ("/watch", "Follow a town"), ("/privacy", "Privacy"),
                ("/contact", "Contact"), ("/bot", "For website managers")]
# The mark: three agenda lines, the middle one longer and purple (the item coming up). The header draws it
# inline (BRAND_MARK), the favicon draws the same, and tools/og_image.py draws it on the share image.
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctitle%3E"
           + quote(SITE_NAME) + "%3C/title%3E"
           "%3Crect x='4' y='7' width='18' height='4' rx='1' fill='%231f2724'/%3E"
           "%3Crect x='4' y='14' width='24' height='4' rx='1' fill='%237a2c80'/%3E"
           "%3Crect x='4' y='21' width='18' height='4' rx='1' fill='%231f2724'/%3E%3C/svg%3E")
BRAND_MARK = ('<svg class="brand-mark" viewBox="0 0 26 20" aria-hidden="true" focusable="false">'
              '<rect x="0" y="1" width="19" height="4" rx="1"/><rect class="hi" x="0" y="8" width="26" height="4" rx="1"/>'
              '<rect x="0" y="15" width="19" height="4" rx="1"/></svg>')


def nav_section(path):
    """Which header section a page belongs to (it stays lit on every page below it)."""
    path = path or ""
    if path in ("/upcoming", "/trending"):
        return "/upcoming"
    if path == "/towns" or re.fullmatch(r"/[a-z]{2}/.+", path) or path.startswith("/m/"):
        return "/towns"
    if path in ("/watch", "/w", "/alerts-for-groups"):
        return "/watch"
    if path.startswith("/topics"):
        return "/topics"
    if path.startswith("/attorney-general"):
        return "/attorney-general"
    return path


def gloss_once(body):
    """Explain "moratorium" once per page: the first "(a moratorium)" stays, later ones go."""
    gloss = " (a moratorium)"
    first = body.find(gloss)
    if first < 0:
        return body
    cut = first + len(gloss)
    return body[:cut] + body[cut:].replace(gloss, "")


def page_end(path, source=""):
    """The strip at the end of every page: where the page's facts come from (when it has one source) and a way
    to report a problem with this page."""
    report = f'<a href="/contact?about={quote(path or "/")}">Report a problem with this page</a>'
    return f'<aside class="page-end wrap narrow" aria-label="About this page">{f"<p>{source}</p>" if source else ""}<p>{report}</p></aside>'


def page(ctx, title, description, body, path, scripts=(), noindex=False, head="", og_title=None, source=""):
    current = nav_section(path)
    nav = "".join(f'<li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>'
                  for href, label in NAV)
    follow = (f'<a class="nav-follow" href="{FOLLOW[0]}"{" aria-current=\"page\"" if current == FOLLOW[0] else ""}>'
              f'{FOLLOW[1]}</a>')
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    canonical = "" if noindex else f'<link rel="canonical" href="{BASE_URL}{"" if path == "/" else path}">\n'
    script_tags = "".join(f'<script src="{s}" defer></script>\n' for s in ("/app.js", *scripts))
    explore = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in FOOTER_EXPLORE)
    about = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in FOOTER_ABOUT)
    read = sum(m for _, m, _ in ctx.coverage())
    who = (OWNER_LINE if OWNER_LINE and e(OWNER_LINE) not in body else
           f"Every morning, {SITE_NAME} reads the agendas that {read} towns in {join_and(STATE_NAMES.get(x, x) for x in ctx.states)} "
           "post online. It isn’t a government website and isn’t part of any town.")
    body = gloss_once(body)
    end = page_end(path or "/", source)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{robots}{canonical}<meta property="og:title" content="{e(og_title or title.split(' | ')[0])}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE_NAME)}">
<meta property="og:url" content="{BASE_URL}{"" if path == "/" else path}">
<meta property="og:image" content="{BASE_URL}/og.png">
<meta property="og:image:alt" content="{e(SITE_NAME)}: what's coming up at your town meetings">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="light dark">
<link rel="preload" href="/fonts/barlow-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/barlow-semibold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/barlow-semicondensed-bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<link rel="icon" href="{FAVICON}">
{head}</head>
<body{' class="compact"' if 'data-view-switch' in body else ''}>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="/">{BRAND_MARK}<span>{e(SITE_NAME)}</span></a>
  <nav class="top" aria-label="Main"><ul>{nav}</ul></nav>
  {follow}
</div></header>
<main id="main">
{body}
</main>
{end}
<footer class="site"><div class="wrap">
  <div class="foot-who"><p class="foot-brand">{BRAND_MARK}<span>{e(SITE_NAME)}</span></p><p>{e(who)}</p></div>
  <nav class="foot-col" aria-label="Explore"><p class="foot-head">Explore</p><ul>{explore}</ul></nav>
  <nav class="foot-col" aria-label="About"><p class="foot-head">About</p><ul>{about}</ul></nav>
  <p class="foot-last">Not legal advice. Confirm dates with the town clerk.</p>
</div></footer>
{script_tags}</body>
</html>
"""


# ---------------------------------------------------------------- agenda items
# An "agenda" here is one agenda document for one meeting: every flagged passage from it is merged
# into one entry with one plain sentence, the quoted passages and one link to the agenda.

def board_label(h):
    key = h.get("board_key")
    if key == "town_meeting":
        return "Town Meeting"
    b = re.sub(r"\s*\([^)]*\)", "", h.get("board") or "")
    b = re.sub(r"\s+[-–]\s+.*$", "", b)
    b = re.sub(r"^The\s+", "", b)
    b = re.sub(r"\s+Meetings?$", "", b)
    b = re.sub(r"\s*/.*$", "", b)  # "Selectboard / Board of Health"
    b = re.sub(r"\s+(?:FY\s?\d{2,4}|Public Hearings?|(?:Meeting\s+)?Agendas?(?:\s*(?:&|and)\s*Minutes)?)$", "", b, flags=re.I)
    b = re.sub(r"['’]s\s+Office$", "", b)  # "Select Board's Office"
    b = re.sub(r"^[\s\-–:]+", "", b)
    b = re.sub(r"^(\w+), (.+ of)$", r"\2 \1", b)  # "Appeals, Zoning Board of"
    if b.isupper() or b.islower():
        b = b.title().replace(" Of ", " of ").replace(" And ", " and ")
    return b.strip() or BOARD_NAMES.get(key, "town board")


def ordered_topics(topics):
    return sorted(set(topics), key=lambda t: TOPIC_ORDER.index(t) if t in TOPIC_ORDER else 99)


def topic_phrase(topics, cap=True):
    ts = [t for t in ordered_topics(topics) if t != "wetlands_filing"] or ordered_topics(topics)
    phrases = [TOPIC_PHRASES.get(t, (t.replace("_", " "), False)) for t in ts]
    words = [p for p, _ in phrases]
    if len(words) > 3:
        words = words[:3] + ["more"]
    text = join_and(words)
    many = len(words) > 1 or phrases[0][1]
    return (text[:1].upper() + text[1:] if cap else text), many


# ---------------------------------------------------------------- agenda lines
# Each flagged passage becomes one plain line, built by rules from the agenda's own words (no
# paraphrase): who (an applicant or project name), what (the action), where (a street address).
# Without those, the line says which topics the agenda mentions. The cleaned quote sits behind
# "See the agenda wording".

KEYWORDS = re.compile(r"solar|photovoltaic|\bpv\b|batter|\bbess\b|energy storage|data cent|moratori|clean energy|"
                      r"consolidated|\b40b\b|comprehensive permit|wireless|cell tower|telecom|zoning|wetland", re.I)
ACTIONS = [  # (pattern, plain words), in the order they are named
    (r"\bmoratori(?:um|a)\b", "moratorium"),
    (r"\bspecial permit\b", "special permit"),
    (r"\bsite plan(?: review| approval)?\b|\bSPR\b", "site plan review"),
    (r"\bnotice of intent\b|\bNOI\b", "wetlands permit request"),
    (r"\brequest for determination\b|\bRDA\b", "wetlands review"),
    (r"\bvariance\b", "variance"),
    (r"\brezon(?:e|es|ing)\b|\bzoning map amendment\b", "rezoning"),
    (r"\bamend(?:s|ed|ing|ments?)?\b[^.]{0,40}\bby-?laws?\b|\bby-?laws? amendments?\b|\bzoning amendments?\b", "bylaw change"),
    (r"\bordinance\b", "ordinance"),
    (r"\bextension\b", "permit extension"),
    (r"\b(?:minor )?modification\b|\bmajor change\b", "change to an approved plan"),
    (r"\blease\b", "lease"),
    (r"\bagreement\b", "agreement"),
    (r"\bpermitting\b", "permitting"),
    (r"\bpublic hearing\b", "public hearing"),
]
CONTINUED = re.compile(r"\bcont(?:inued|['’]d|inuance)\b", re.I)
NAME_LLC = re.compile(r"((?:[A-Z0-9][\w&'’.-]*\s+){0,5}[A-Z0-9][\w&'’.-]*,?\s+(?:LLC|L\.L\.C\.|Inc\.?|LP|L\.P\.|Corp\.?|Corporation))(?=[\s,.;:)]|$)")
NAME_PROJECT = re.compile(r"((?:[A-Z][\w'’-]*\s+){1,3}(?:Solar|Data Center)"
                          r"(?:\s+(?:Farm|Project|Field|Array|Facility|Park))?(?:\s+\d+)?)\b")
GENERIC = {"large-scale", "large", "scale", "ground-mounted", "ground", "mounted", "small", "clean", "energy", "proposed",
           "the", "a", "commercial", "municipal", "and", "of", "for", "on", "battery", "storage", "solar", "data",
           "center", "photovoltaic", "dual-use", "rooftop", "community", "new", "accessory", "utility", "town",
           "regulations", "bylaw", "zoning", "review", "public", "hearing", "special", "permit", "site", "plan",
           "re", "request", "requesting", "discussion", "vote", "update", "facility", "facilities", "systems",
           "system", "installation", "construction", "operation", "amend", "amendment", "article", "residential",
           "non-residential", "bids", "code", "study", "zone", "change", "proposed", "temporary", "new", "city",
           "council", "board", "planning", "conservation", "commission", "select", "meeting", "agenda", "old",
           "business", "session", "consolidated", "statewide", "siting", "permitting", "process", "infrastructure"}
ADDRESS = re.compile(r"\b(\d{1,5}[A-Z]?(?:-\d+)?\s+(?:[A-Z][a-z]+\.?\s+){1,3}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|"
                     r"Drive|Dr|Way|Highway|Hwy|Boulevard|Blvd|Place|Pl|Turnpike|Tpke|Circle|Court|Ct|Pike|Parkway|Pkwy)\b\.?)")
LEAD_JUNK = re.compile(r"^(?:\d+[.)]\s*|[A-Z]\.\s+|re:\s*|request by\s+|applicant:\s*|public hearing(?: cont['’]d)?:\s*)+", re.I)


def short_topics(topics):
    ts = [t for t in ordered_topics(topics) if t not in ("wetlands_filing",)] or ordered_topics(topics)
    words = [{"moratorium": "moratorium", "data_center": "data centers"}.get(t, TOPIC_PHRASES.get(t, (t, False))[0])
             for t in ts]
    words = [w[2:] if w.startswith("a ") else w for w in words]
    return join_and(words[:3])


NAME_STOP = {"bylaw", "zoning", "amendment", "ordinance", "plan", "master", "regulations", "bids", "bid", "discussion",
             "position", "hr", "law", "minutes", "agenda", "update", "updates", "business", "session", "meeting", "hearing",
             "old", "other", "report", "reports", "committee", "subcommittee", "staff", "liaison", "vote", "warrant",
             "article", "policy", "use", "uses", "district", "overlay", "definition", "definitions", "section",
             "board", "regarding"}
LEAD_WORDS = re.compile(r"^(?:(?:public|hearing|continued|cont['’]d|discussion|regarding|board|update|re)\s+)+", re.I)


def find_name(text):
    """(name, is_company): an applicant such as "Federal Pond Solar, LLC", or a project such as "South St Solar Field"."""
    for m in NAME_LLC.finditer(text):
        name = LEAD_WORDS.sub("", LEAD_JUNK.sub("", m.group(1))).strip(" ,")
        words = re.findall(r"[A-Za-z][\w'’-]*", name)
        if words and not all(w.lower() in GENERIC | {"llc", "inc"} for w in words) and len(name) <= 60:
            return name, True
    for m in NAME_PROJECT.finditer(text):
        name = LEAD_JUNK.sub("", m.group(1)).strip(" ,")
        words = [re.sub(r"[^a-z0-9-]", "", w.lower()).strip("-") for w in name.split()]
        if any(w in NAME_STOP for w in words):  # agenda headings, not a project's name
            continue
        if sum(1 for w in words if w and w not in GENERIC and not w.isdigit()) >= 1 and len(name) <= 50:
            return name, False
    return "", False


def find_address(text):
    m = ADDRESS.search(text)
    if not m:
        return ""
    addr = m.group(1).rstrip(".")
    return re.sub(r"^0\s+", "", addr)  # "0 Wareham Street" is a parcel with no number


# The tags on each item use the same topic names as the alert form and search (without the glosses).
TOPIC_TAGS = {k: re.sub(r"\s*\(.*\)$", "", v) for k, v in TOPIC_LABELS.items()}
PROJECT_NOUN = {"solar": "solar", "battery_storage": "battery storage", "data_center": "data center",
                "wireless_telecom": "cell tower", "40b_comprehensive_permit": "affordable housing"}
PLURAL_NOUN = {"solar": "solar projects", "battery_storage": "battery storage", "data_center": "data centers",
               "wireless_telecom": "cell towers", "40b_comprehensive_permit": "affordable housing",
               "clean_energy_siting": "clean-energy projects"}
MENTION_NOUN = {**PLURAL_NOUN, "moratorium": "a temporary ban (moratorium)", "zoning_amendment": "a zoning change",
                "wetlands_filing": "a wetlands filing", "extraction": "a quarry or gravel pit",
                "large_development": "a large development"}
VOTE = re.compile(r"\bvot(?:e|es|ing)\b", re.I)
PRIMARY = ["special permit", "variance", "permit extension", "wetlands permit request", "wetlands review", "site plan review",
           "change to an approved plan", "moratorium", "bylaw change", "ordinance", "rezoning", "lease", "agreement",
           "permitting", "public hearing"]


def topic_tags(topics):
    return [TOPIC_TAGS.get(t, t.replace("_", " ")) for t in ordered_topics(topics)]


def who_label(h):
    """"The Planning Board", "Town meeting", or "" for a state filing."""
    if h.get("source") == "massdep_wetlands":
        return ""
    if h.get("board_key") == "town_meeting":
        return "Town Meeting"
    b = board_label(h)
    b = b[:1].upper() + b[1:]
    return b if b.lower().startswith("the ") else f"The {b}"


def project_phrase(topics, name, company, addr):
    nouns = [PROJECT_NOUN[t] for t in ordered_topics(topics) if t in PROJECT_NOUN]
    if name and not company:
        whole = re.search(r"(?:Project|Farm|Field|Array|Facility|Park)(?:\s+\d+)?$", name)
        obj = f"the {name}" + ("" if whole else " project")
    else:
        noun = join_and(nouns[:2])
        if not noun:
            obj = "a project"
        elif noun in ("data center", "cell tower"):
            obj = f"a {noun}"
        elif noun.startswith("affordable"):
            obj = f"an {noun} project"
        else:
            obj = f"a {noun} project"
        if name:
            obj += f" by {name}"
    return obj + (f" at {addr}" if addr else "")


def item_text(h):
    """One plain sentence for one agenda item: a verified written brief when there is one, else the shared
    reading (analysis_text), else the older rules."""
    a = ANALYSIS.get(h.get("id"))
    if a:
        t = analysis_text(h, a)
    else:
        t = item_text_rules(h)
        t.setdefault("key", "")
        t["quote"] = "" if junk_quote(clean_quote(h.get("snippet"), 600)) else clean_quote(h.get("snippet"), 600)
        t["no"] = ""
        t["rank"] = 30 if t["kind"] == "act" else 70
    t.setdefault("stage", "Hearing" if t.get("note") == HEARING_NOTE else "")
    t.setdefault("facts", [])
    b = BRIEFS.get(h.get("id"))
    return brief_text(t, b, h.get("board_key") == "town_meeting") if b else t


# Labels for a brief's facts, in the order they show. An empty label is a plain paragraph (the brief's
# one-sentence "what"). The content research can rename these here; w.js and trending.js read them
# from lines.json and trending.json.
BRIEF_LABELS = {"what": "", "where": "Where", "size": "Size", "who": "Who", "next": "Next", "history": "Earlier",
                "can_speak": "Can I speak?", "quote": "Agenda wording"}
BRIEF_SPEAK = {True: "Yes. This is a public hearing: anyone can attend and ask to speak, and you can send written "
                     "comments to the board through the town clerk before the meeting.",
               False: "The agenda doesn’t list public comment on this item. Ask the town clerk whether you can."}
BRIEF_RANK = {"vote": 10, "adopted": 10, "hearing": 20, "continued": 20, "extension": 30, "other": 40, "discussion": 40,
              "withdrawn": 50}
BRIEF_STAGE = {"vote": "Vote", "adopted": "Final vote", "hearing": "Hearing", "continued": "Postponed", "extension": "Extension",
               "other": "", "discussion": "Discussion", "withdrawn": "Withdrawn"}


def brief_stage(b):
    """The stage word for a brief. A postponement names the new day when the brief's "next" says where the
    hearing moves to ("asked to postpone to Tue Oct 27, 2026" becomes "Postponed to Tue Oct 27")."""
    stage = BRIEF_STAGE.get(b.get("action") or "other", "")
    # An applicant's request to continue is not a decision until the board agrees.
    asked = bool(re.search(r"\b(?:request|ask)(?:ed|s|ing)?\b[^.]{0,40}?\b(?:continu|postpon|move)",
                           f"{b.get('line') or ''}. {b.get('next') or ''}", re.I))
    if stage == "Postponed":
        m = re.search(r"(?:postpone[ds]? (?:it )?(?:to|until)|continued? (?:to|until)|continues|moves to|resumes|reopens|rescheduled (?:to|for)|new date)"
                      r"[^.;]{0,30}?\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2})\b",
                      b.get("next") or "", re.I)
        if m:
            stage = f"Postponed to {m.group(1).title()} {m.group(2).title()} {int(m.group(3))}"
        if asked:
            stage = stage.replace("Postponed", "Asks to postpone")
    elif stage == "Vote" and re.search(r"\b(?:may|might|could|possible|possibly|potential)\s+vote", f"{b.get('line') or ''} {b.get('what') or ''}", re.I):
        stage = "Possible vote"  # the agenda allows a vote without promising one
    return stage


def nice_case(v):
    """"PLANNING BOARD", as a warrant prints it, becomes "Planning Board"; mixed case is left alone."""
    v = str(v)
    if len(v) > 3 and v.isupper():
        small = {"of", "and", "the", "for", "on", "at", "to", "in", "by", "a", "an"}
        return " ".join(w if (i and w in small) else w[:1].upper() + w[1:] for i, w in enumerate(v.lower().split()))
    return v


SPONSOR_RE = re.compile(r"\b(board|committee|commission|council|selectmen|petition|department|trust|authority)\b", re.I)


def public_brief(b):
    """A brief as the alert pages get it: the writers' note that an item was flagged twice is for the records."""
    out = dict(b)
    out["what"] = re.sub(r"^(?:Same|This) (?:article|item)\b[^.]*\.\s*", "", (b.get("what") or "").strip())
    out.pop("missing", None)
    return out


def brief_text(base, b, town_meeting=False):
    """The item's line from a verified written brief: the brief's one-liner as the heading, its facts, and
    its own quote as the agenda wording. The shared reading still supplies the item key and number. A
    writer's note that the item was flagged twice is for the records, not the page; on a warrant, the
    sponsor reads "Planning Board article" so it isn't taken for the meeting's board."""
    b = dict(b)
    b["what"] = re.sub(r"^(?:Same|This) (?:article|item)\b[^.]*\.\s*", "", (b.get("what") or "").strip())
    for key in ("history", "next"):  # "Before this" is from our records by definition; the writers' hedge is noise on the page
        if b.get(key):
            b[key] = re.sub(r"\s*\((?:per|in|from)[^()]*our records\)|,? (?:per|in) our records\b", "", b[key]).strip()
            b[key] = b[key].replace("Related papers in our records:", "Related papers:")
    for key in ("line", "what", "history", "next", "how_to_speak", "where", "who"):  # the agenda's quote stays as printed
        if b.get(key):
            b[key] = smart_quotes(b[key])
    say = (b.get("line") or b.get("what") or base["say"]).strip()
    if b.get("line") and re.search(r"[a-z0-9)]\.$", say) and not re.search(r"\b(?:St|Rd|Ave|Dr|Ln|Blvd|Mt|No|Art|Sec)\.$", say):
        say = say[:-1]  # headlines carry no final period
    who = nice_case(b["who"]) if b.get("who") else ""
    if who and town_meeting and SPONSOR_RE.search(who) and not who.lower().endswith("article"):
        who += " article"
    return {**base, "say": say, "kind": "brief", "note": "", "quote": b.get("quote") or base.get("quote", ""), "brief": b,
            "stage": brief_stage(b),
            "facts": [v for v in (nice_case(b["where"]) if b.get("where") else "", b.get("size"), who) if v],
            "fact_pairs": [(k, v) for k, v in (("Where", nice_case(b["where"]) if b.get("where") else ""), ("Size", b.get("size")),
                                               ("Sponsor" if SPONSOR_RE.search(who) else "Applicant", who)) if v],
            "rank": BRIEF_RANK.get(b.get("action") or "other", 40) + SUBJECT_RANK.get(base.get("subj", ""), 8)}


def smart_quotes(text):
    """Straight quotes in a writer's text become the site's curly ones, apostrophes inside words included."""
    if not text or ('"' not in text and "'" not in text):
        return text
    t = re.sub(r"(\w)'(\w)", "\\1’\\2", text)
    t = re.sub(r"'(\d\ds)\b", "’\\1", t)
    t = re.sub(r"(^|[\s(\[“])'", "\\1‘", t)
    t = t.replace("'", "’")
    t = re.sub(r'(^|[\s(\[‘])"', "\\1“", t)
    return t.replace('"', "”")


def brief_facts_html(b, clerk="", skip_what=False):
    """The brief's facts that exist, labeled from BRIEF_LABELS: the "what" sentence as a paragraph (unless
    it repeats the line), then a <dl> of Where, Size, Who, Next, Earlier and "Can I speak?"."""
    parts = []
    rows = []
    same = quote_key(b.get("what") or "") == quote_key(b.get("line") or "")
    for key, label in BRIEF_LABELS.items():
        if key == "quote":
            continue
        v = b.get(key)
        extra = ""
        if key == "can_speak":
            v = f"Yes. {b['how_to_speak']}" if v is True and b.get("how_to_speak") else (BRIEF_SPEAK.get(v) if v in (True, False) else None)
            if b.get("can_speak") is True and clerk:
                extra = f" {clerk}"
        if v in (None, "", False):
            continue
        if not label:
            if not (key == "what" and (same or skip_what)):
                parts.append(f'<p class="brief-what">{e(str(v))}</p>')
            continue
        rows.append(f'<div class="fact"><dt>{e(label)}</dt><dd>{e(nice_case(v))}{extra}</dd></div>')
    if rows:
        parts.append(f'<dl class="brief-facts">{"".join(rows)}</dl>')
    return "".join(parts)


def item_text_rules(h):
    """One plain sentence for one agenda item: who will do what, about which project, where.
    Returns {"say", "note", "kind"}: kind is "act" (the agenda names an action), "list" (it names a
    project but no action) or "mention" (it only mentions a subject)."""
    text = " ".join((h.get("snippet") or "").split())
    topics = h.get("topics", [])
    found = [words for pattern, words in ACTIONS if re.search(pattern, text, re.I)]
    actions = [a for a in PRIMARY if a in found]
    if h.get("source") == "massdep_wetlands" and "wetlands permit request" not in actions:
        actions.insert(0, "wetlands permit request")
    hearing = "public hearing" in actions or bool(re.search(r"\bhearing\b", text, re.I))
    actions = [a for a in actions if a != "public hearing"] or (["public hearing"] if "public hearing" in actions else [])
    name, company = find_name(text)
    addr = find_address(text)
    cont = " (continued from an earlier meeting)" if CONTINUED.search(text) else ""
    who = who_label(h)
    town_meeting = h.get("board_key") == "town_meeting"
    vote = bool(VOTE.search(text)) or town_meeting
    talk = "vote on" if vote else "discuss"
    obj = project_phrase(topics, name, company, addr)
    subj = join_and([PLURAL_NOUN[t] for t in ordered_topics(topics) if t in PLURAL_NOUN][:3])
    note = HEARING_NOTE if hearing and who and not town_meeting else ""

    if not who:  # a filing with the state, not a meeting
        say = full_stop(f"A wetlands permit request for {obj} was filed with the state{cont}.")
        return {"say": say, "note": "", "kind": "act"}
    act = actions[0] if actions else ""
    if "moratorium" in actions and not (name or addr):  # a ban on a kind of project, not a review of one project
        act = "moratorium"
    if town_meeting and act in ("special permit", "variance", "permit extension", "wetlands permit request", "wetlands review",
                                "site plan review", "change to an approved plan", "lease", "agreement"):
        act = "article"
    verb = {
        "article": f"vote on an article about {obj if (name or addr) else (subj or 'this')}",
        "special permit": f"decide whether to allow {obj}" if obj != "a project" else "decide whether to allow a project that needs a special permit",
        "variance": f"decide whether to grant a variance for {obj}",
        "permit extension": f"decide whether to extend the permit for {obj}",
        "wetlands permit request": f"review a wetlands permit request for {obj}",
        "wetlands review": f"review whether {obj} needs a wetlands permit",
        "site plan review": f"review plans for {obj}",
        "change to an approved plan": f"review changes to the approved plans for {obj}",
        "moratorium": (f"{talk} a temporary ban on new {subj} (a moratorium)" if subj and "zoning" not in subj
                       else f"{talk} a temporary ban on new building permits (a moratorium)"),
        "bylaw change": f"{talk} a change to the zoning bylaw" + (f" for {subj}" if subj else ""),
        "ordinance": f"{talk} a change to the zoning ordinance" + (f" for {subj}" if subj else ""),
        "rezoning": f"{talk} rezoning " + (f"land at {addr}" if addr else "part of town"),
        "lease": f"{talk} a lease for {obj}",
        "agreement": f"{talk} an agreement for {obj}",
        "permitting": f"{talk} permit rules for {subj}" if subj else f"{talk} permit rules",
        "public hearing": f"hold a public hearing on {obj if (name or addr) else (subj or 'a zoning change')}",
    }.get(act)
    stage = "Hearing" if hearing else ("Vote" if vote else "Discussion")
    if verb:
        say = stage_verb(verb, hearing)
        return {"say": full_stop(f"{say}{cont}."), "note": note, "kind": "act", "stage": stage, "facts": [x for x in (addr,) if x],
                "fact_pairs": [("Where", addr)] if addr else []}
    if name or addr:
        return {"say": full_stop(f"Discusses {obj}{cont} (no vote listed)."), "note": note, "kind": "list", "stage": stage,
                "facts": [x for x in (addr,) if x], "fact_pairs": [("Where", addr)] if addr else []}
    about = join_and([("a 40R smart-growth district" if t == "40b_comprehensive_permit" and SMART_GROWTH.search(text) else MENTION_NOUN.get(t, t.replace("_", " ")))
                      for t in ordered_topics(topics)][:3]) or "these subjects"
    words = short_quote(text, 110)
    say = f"Mentions {about} in “{words}”" if quotable(words) else f"Mentions {about}."
    return {"say": say, "note": note, "kind": "mention", "stage": "", "facts": []}


def stage_verb(verb, hearing=False):
    """A rules-based verb phrase ("vote on a lease for X", "decide whether to allow X") as a line that starts
    with the stage: Votes on, Holds a hearing on, Discusses (no vote listed)."""
    for start, out in (("vote on ", "Votes on "), ("hold a public hearing on ", "Holds a hearing on "),
                       ("decide whether to allow ", "Decides on "), ("decide whether to grant ", "Decides on "),
                       ("decide whether to extend the permit for ", "Decides on extending the permit for ")):
        if verb.startswith(start):
            return out + verb[len(start):]
    for start in ("discuss ", "review "):
        if verb.startswith(start):
            rest = verb[len(start):]
            return (f"Holds a hearing on {rest}" if hearing else f"Discusses {rest} (no vote listed)")
    return verb[:1].upper() + verb[1:]


# ---------------------------------------------------------------- one reading of each item, shared with Trending
# trending.py's classifier reads every flagged passage once: which agenda item it sits in, what the
# board will do (hearing, vote, continuance, adoption, minutes of an earlier meeting...), the subject,
# names, address and sizes, and the date of an undated Town Meeting warrant. Town pages, topic pages,
# counts and the Trending page all use that one reading. ANALYSIS is filled by Ctx.

ANALYSIS = {}
BRIEFS = {}  # hit id -> verified written brief (briefs.py); filled by Ctx, shown instead of the rules-based line
SUBJECT_NOUN = {"data_center": "data centers", "battery_storage": "battery storage", "solar": "solar",
                "wind": "wind energy", "clean_energy_siting": "small clean-energy projects", "zoning_amendment": "zoning",
                "general_bylaw": "town rules", "40b_comprehensive_permit": "affordable housing",
                "wireless_telecom": "cell towers", "wetlands_filing": "wetlands", "other": "local rules"}
PERMIT_PLAIN = {"special permit": "a special permit", "site plan review": "site plans",
                "comprehensive permit": "an affordable housing permit (40B)", "variance": "a variance",
                "Notice of Intent": "a wetlands permit request", "planned development permit": "a planned development permit",
                "permit extension": "a request to extend a permit", "modification": "a change to an approved permit"}
# The same permits as a facts-line tag, next to the topic tag ("Affordable housing · 40B permit").
PERMIT_FACT = {"comprehensive permit": "40B permit", "Notice of Intent": "wetlands permit", "site plan review": "site plan",
               "permit extension": "permit extension", "modification": "change to an approved permit"}
HEARING_NOTE = "Public hearing."


def tr_keys(a):
    keys = []
    for t in a["subjects"] or [a["subject"]]:
        if t == "zoning_amendment":
            keys.append(TR.ZONING_KEY)
        elif t in TR.SUBJECT_RE:
            keys.append(TR.SUBJECT_RE[t])
    if a["action"] == "moratorium":
        keys.insert(0, TR.SUBJECT_RE["moratorium"])
    return keys


def tr_quote(a, limit):
    """The agenda's own words for this item: the sentence that holds the subject or the project name."""
    name = a["names"][0][0] if a["names"] else None
    prefer = {"moratorium": TR.SUBJECT_RE["moratorium"], "ban": TR.BAN_RE, "continuance": TR.CONTINUANCE_RE,
              "adopt": TR.ADOPT_RE, "rezoning": TR.REZONE_RE, "deal": TR.DEAL_RE}.get(a["action"])
    try:
        return TR.pick_quote(a["item"], tr_keys(a), prefer, a["snippet"], limit=limit, name=name)
    except Exception:
        return clean_quote(a["snippet"], limit)


def item_number(a):
    """"Article 12" or "item 3" when the agenda numbers the item."""
    m = re.search(r"\bArticle\s+(\d{1,3}[A-Z]?)\b(?![.\d])", a["item"][:400])  # not "Article 4.8.12", a bylaw section
    if m:
        return f"Article {m.group(1)}"
    m = re.match(r"\s*(\d{1,2}[a-z]?|[A-H])[.)]\s+[A-Z]", a["item"])
    return f"item {m.group(1)}" if m else ""


POSSIBLE_VOTE = re.compile(r"\b(?:possible|potential|may)\s+vote|discussion\s+and\s+(?:possible\s+)?vote", re.I)
SMART_GROWTH = re.compile(r"\b40\s?R\b|smart.growth", re.I)


def subject_noun(a):
    s = a["subject"]
    if s == "40b_comprehensive_permit" and SMART_GROWTH.search(a.get("item") or ""):
        return "a 40R smart-growth district"  # zoning for denser housing, not a 40B permit
    if s in ("data_center", "battery_storage") and TR.SUBJECT_RE["data_center"].search(a["item"]) \
            and TR.SUBJECT_RE["battery_storage"].search(a["item"]):
        return "battery storage and data centers"
    if s == "battery_storage" and "solar" in a["topics"] and TR.SUBJECT_RE["solar"].search(a["item"]):
        return "solar and battery storage"
    if s == "solar" and "battery_storage" in a["topics"] and TR.SUBJECT_RE["battery_storage"].search(a["item"]):
        return "solar and battery storage"
    return SUBJECT_NOUN.get(s, "local rules")


RANK = {"moratorium": 0, "ban": 0, "adopt": 1, "town_meeting": 1, "project_hearing": 2, "continuance": 2,
        "rezoning": 3, "bylaw_hearing": 3, "warrant_review": 3, "project": 4, "deal": 4, "filing": 4, "withdrawn": 5,
        "cancelled": 5, "process": 5, "bylaw_draft": 5, "discussion": 6, "mention": 7}
SUBJECT_RANK = {"data_center": 0, "battery_storage": 1, "solar": 2, "wind": 3, "clean_energy_siting": 4,
                "40b_comprehensive_permit": 5, "wireless_telecom": 6, "zoning_amendment": 7}
TR_INPUTS = [None]
DOC_TEXT = {}
AG_BY_TOWN = {}  # "MA:Gill": [rulings], filled by Ctx
TM_TITLE = re.compile(r"[\"“](?:Zoning\s+)?(?:By-?law|Ordinance)\s+Amendment\s*[–—-]\s*([^\"”]{4,80})[\"”]", re.I)


def doc_text(url):
    if url not in DOC_TEXT:
        d = ((TR_INPUTS[0] or {}).get("docs") or {}).get(url)
        DOC_TEXT[url] = TR.norm(d["text"]) if d and d.get("text") else ""
    return DOC_TEXT[url]


def whole_sentence(q, url, limit=420):
    """A quote cut at either end ("…the applicant has requested a…"), completed to the whole agenda
    sentence when the agenda text is at hand and that sentence isn't too long. Item edges (numbers,
    bullets, headers) count as sentence edges, so the quote never runs into the next item."""
    if not q or not (q.startswith("…") or q.endswith("…")):
        return q
    text = doc_text(url)
    core = q.strip("…").strip()
    if not text or len(core) < 12:
        return q
    pos = text.find(core)
    if pos >= 0:
        end = pos + len(core)
    else:
        pos = text.find(core[:40])
        if pos >= 0:
            end = pos + len(core)
        else:
            tail = text.find(core[-40:])
            if tail < 0:
                return q
            end = tail + 40
            pos = max(0, end - len(core))
    lo, hi = max(0, pos - 600), min(len(text), end + 600)
    cuts = {lo, hi}
    for x, y in TR.sentence_spans(text, lo, hi, semicolons=False):
        cuts.update((x, y))
    cuts.update(lo + x for x in TR.boundaries(text[lo:hi]))
    start = max((c for c in cuts if c <= pos), default=lo)
    stop = min((c for c in cuts if c >= end), default=hi)
    if (start == lo and lo > 0) or (stop == hi and hi < len(text)):
        return q  # no sentence edge in reach: keep the shorter quote
    out = TR.clean_quote_text(text[start:stop])
    if not out or len(out) > limit or TR.norm(core[:20]) not in out:
        return q
    if out[:1].islower():
        out = "…" + out  # the agenda's own sentence starts before the item
    if re.search(r"\b(?:within|and|or|of|for|to|the|a|an|in|on|at|by|with|from|that|is)$", out, re.I):
        out += "…"  # the agenda runs on into the next item here
    return out


BOILERPLATE = re.compile(r"2/3\s+(?:majority\s+)?vote\s+is\s+required|"
                         r"\[(?:Added|Amended)\b|complete\s+text\s+of\s+these\s+proposed|Page\s+\d+\s+of\s+\d+", re.I)
ANY_OTHER_ACTION = re.compile(r"or\s+take\s+any\s+other\s+action\s+relative", re.I)


def junk_quote(q):
    """Table cells, letterheads, page furniture and warrant boilerplate: not worth quoting."""
    t = (q or "").strip("…“” ")
    if len(t) < 15 or junk(t) or TR.junk_ratio(t) > 0.3 or BOILERPLATE.search(t):
        return True
    if len(t) < 140 and ANY_OTHER_ACTION.search(t):
        return True  # just the end of a warrant article
    toks = t.split()
    caps = sum(1 for w in toks if len(w) > 1 and w.isalpha() and w.isupper())
    return len(toks) >= 6 and caps / len(toks) > 0.35  # a letterhead: "CITY OF PITTSFIELD NOTICE OF ZONING AMENDMENT"


def ag_ruling(h, a):
    """An Attorney General ruling on this Town Meeting article, when one exists (Gill, Article 7)."""
    if h.get("board_key") != "town_meeting":
        return None
    no = item_number(a)
    if not no.startswith("Article "):
        return None
    n = no.split()[1]
    for r in AG_BY_TOWN.get(f"{h['state']}:{h['town']}", []):
        if r.get("record_type") == "ag_decision" and re.search(rf"\bArticles?\b[^()]*?\b{re.escape(n)}\b", r.get("article") or ""):
            if not h.get("meeting_date") or (r.get("decision_date") or "") >= h["meeting_date"]:
                return r
    return None


def city_words(say):
    """A city adopts ordinances: "bylaw" becomes "ordinance" outside the quoted agenda words."""
    parts = re.split(r"(“[^”]*”)", say)
    return "".join(x if x.startswith("“") else re.sub(r"\b[Bb]ylaw\b", "ordinance", x) for x in parts)


def analysis_text(h, a):
    """One line from the shared reading, in the site's item format: it starts with the stage (Votes on,
    Holds a hearing on, Discusses, Postponed, Final vote) and names the thing and the place; the board and
    day are on the meeting line above it. When the reading is unsure (a passing mention, a general
    discussion, a zoning change with no subject, an item with no project named) it quotes the agenda's
    own sentence instead of paraphrasing, and only whole sentences are quoted."""
    tm = h.get("board_key") == "town_meeting"
    act, f = a["action"], a["flags"]
    noun = subject_noun(a)
    _, adj, rules, proj = TR.words_for(a)
    proj = proj.replace("40B housing plan", "affordable housing project")
    rules = rules.replace("40B rules", "affordable housing rules").replace("clean energy siting rules", "clean-energy permit rules")
    name = a["names"][0][0] if a["names"] else None
    if name and re.fullmatch(r"(?i)(?:chapter|article|section|town|city|the town|the city)(?:\s+\w+)?", name):
        name = None  # "Chapter 40B", "Article 12": a citation, not an applicant
    addr = a["address"][0] if a["address"] and a["address"][1] else None
    at = f" at {addr}" if addr else ""
    full = whole_sentence(tr_quote(a, 600), h.get("source_url"))
    if junk_quote(full):
        full = ""
    q = full if full and len(full) <= 220 else ""
    hearing = bool(f.get("hearing")) and not tm
    cont = " (continued from an earlier meeting)" if f.get("continued") and act not in ("continuance",) else ""
    no = item_number(a)
    ik = a.get("item_key") or ("", h["id"])
    key = (name or addr or "").lower() or (f"{no.lower()}" if no else f"@{ik[0]}@{ik[1]}")
    ruling = ag_ruling(h, a)
    note = ""
    if ruling:
        note = (f"Already decided: the Attorney General ruled on this article ({ruling.get('outcome')}, letter dated "
                f"{fmt_date(ruling.get('decision_date'))}). {ruling.get('summary', '')}").strip()
    past_tm = tm and (ruling or not h.get("meeting_date") or h["meeting_date"] < TODAY[0])
    permits = TR.permit_list(a["item"]) if act in ("project_hearing", "project", "continuance") else []
    permit_words = join_and([PERMIT_FACT.get(x, re.sub(r"^an? ", "", PERMIT_PLAIN.get(x, x))) for x in permits]) if permits else ""
    facts = [x for x in (addr, permit_words) if x]
    fact_pairs = [(k, v) for k, v in (("Where", addr), ("Permits", permit_words)) if v]

    def done(say, kind="act", stage="Discussion", rank_act=None):
        say = full_stop(say[:1].upper() + say[1:])
        say = re.sub(r"\) \((?=[a-z])", "; ", say)  # "(a moratorium) (continued …) (no vote listed)" reads as one aside
        if stage == "Discussion" and POSSIBLE_VOTE.search(a.get("item") or ""):
            # "Discussion and possible vote": the agenda allows a vote without promising one
            stage = "Possible vote"
            say = say.replace(" (no vote listed)", "; a vote is possible").replace("; no vote listed)", "; a vote is possible)")
        if f"{h['state']}:{h['town']}" in CITIES:
            say = city_words(say)
        if past_tm:
            say = say.replace("Votes on ", "Voted on ")
            stage = "Decided" if ruling else ("Warrant" if not h.get("meeting_date") else "Vote")
        # Among sentences about the same item, the one that names the decision outranks a discussion
        decided = 0 if stage in ("Vote", "Final vote", "Hearing", "Decided") else 1 if stage.startswith(("Possible vote", "Postponed", "Asks")) else 3
        return {"say": say, "note": note, "kind": kind, "key": key, "quote": full, "no": no, "subj": a["subject"],
                "stage": stage, "facts": facts, "fact_pairs": fact_pairs,
                "rank": RANK.get(rank_act or act, 6) * 10 + SUBJECT_RANK.get(a["subject"], 8) + decided}

    def quoted(lead, plain):
        """lead: “quote” when the agenda's sentence is short enough to read inline; otherwise the plain words."""
        return f"{lead}: “{q}”" if q else f"{plain}."

    def with_stage(core, stage_vote=False):
        """The verb for a bylaw or ban: a hearing, a vote, or a discussion with no vote listed."""
        if hearing:
            return done(f"Holds a hearing on {core}{cont}.", stage="Hearing")
        if f.get("vote") or stage_vote:
            return done(f"Votes on {core}{cont}.", stage="Vote")
        return done(f"Discusses {core}{cont} (no vote listed).")

    if a["source"] != "agenda":
        mw = next((x[1] for x in a["scale"] if x[2] == "MW"), None)
        what = TR.with_article(f"{mw} {proj.replace(' project', '')}" if mw else proj)
        return done(f"Wetlands permit request for {what}{at}, filed with the state.", stage="Filing")
    if act == "moratorium":
        state = "a draft " if f["draft"] else "a possible " if f["tentative"] else "a proposed " if f["proposed"] else "a "
        # "a ban on new zoning" is not a thing; without a buildable subject the ban is on new building permits
        core = (f"{state}temporary ban on new {noun} (a moratorium)" if noun and noun not in ("zoning", "local rules", "town rules")
                else f"{state}temporary ban on new building permits (a moratorium)")
        if tm:
            return done(f"Votes on an article proposing {core}.", stage="Vote")
        if f["warrant"]:
            return done(f"Discusses a Town Meeting article proposing {core} (no vote listed).")
        return with_stage(core)
    if act == "ban":
        core = f"{'a petition' if f['petition'] else 'a proposal'} to prohibit {noun}"
        return with_stage(core)
    if act == "town_meeting":
        if a["subject"] in ("zoning_amendment", "general_bylaw", "other"):
            title = TM_TITLE.search(a["item"])
            change = "a zoning change" if a["subject"] == "zoning_amendment" else "a bylaw change"
            if title:
                return done(f"Votes on {change}: {title.group(1).strip()}.", stage="Vote")
            return done(quoted(f"Votes on an article about {noun}", f"Votes on {change}"), stage="Vote")
        return done(f"Votes on an article about {rules}.", stage="Vote")
    if act == "warrant_review":
        return done(f"Discusses a Town Meeting article about {rules} (no vote listed).")
    if act == "adopt":
        laws = re.search(r"\bLocal\s+Laws?\s+(?:No\.?\s*)?\d+(?:\s*(?:,|and|&)\s*(?:No\.?\s*)?\d+)*(?:\s+of\s+\d{4})?", a["item"], re.I)
        law = laws.group(0) if laws else TR.rule_phrase(a, adj, rules)
        return done(f"Final vote on {law}" + (f" ({rules})" if laws else "") + ".", stage="Final vote")
    if act in ("bylaw_hearing", "bylaw_draft"):
        if a["subject"] in ("zoning_amendment", "general_bylaw", "other"):
            what = "a zoning change" if a["subject"] == "zoning_amendment" else "a rule change"
            if act == "bylaw_hearing" and hearing:
                return done(quoted(f"Holds a hearing on {what}", f"Holds a hearing on {what}"), stage="Hearing")
            return done(quoted(f"Discusses {what} (no vote listed)", f"Discusses {what} (no vote listed)"))
        if act == "bylaw_hearing" and hearing:
            return done(f"Holds a hearing on {TR.rule_phrase(a, adj, rules)}{cont}.", stage="Hearing")
        if f["draft"]:
            return done(f"Discusses {TR.rule_phrase(a, adj, rules, draft=True) if TR.law_word(a) else 'draft ' + rules} (no vote listed).")
        return done(quoted(f"Discusses {rules} (no vote listed)", f"Discusses an item on {rules} (no vote listed)"))
    if act == "rezoning":
        target = addr or "land"
        return with_stage(f"a request to rezone {target}")
    if act in ("project_hearing", "project"):
        units = next((x for x in a["scale"] if x[2] == "units"), None)
        target = name or TR.with_article(proj)
        named = bool(name or addr or units)
        if a["subject"] == "40b_comprehensive_permit":
            target = (f"{TR.fmt_num(units[3])} units of housing" if units else ("a housing project" if permits else "an affordable housing project")) + (f" by {name}" if name else "")
        elif a["subject"] == "wireless_telecom":
            target = (f"a {a['height']} cell tower" if a.get("height") else "a cell tower") + (f" by {name}" if name else "")
        elif a["subject"] in ("zoning_amendment", "general_bylaw"):
            target = name or "a property"
        plain_permits = []
        for x in permits:
            words = PERMIT_PLAIN.get(x, x)
            if x == "variance":
                many = bool(re.search(r"\bvariances\b", a["item"], re.I))
                setback = "setback " if re.search(r"\bsetbacks?\b", a["item"], re.I) else ""
                words = f"{setback}variances" if many else f"a {setback}variance"
            plain_permits.append(words)
        kinds = join_and(plain_permits)
        asked = bool(re.search(r"\brequest|\bapplica|\bpetition|\bseek|\bapplicant", a["item"], re.I))
        if act == "project_hearing" and hearing:
            return done(f"Holds a hearing on {kinds + ' for ' if kinds else ''}{target}{at}{cont}.", stage="Hearing")
        if not (kinds and (named or asked)):
            # No permit named, or nothing asked for: the agenda's words, not a guess ("solar credits" isn't a project).
            return done(quoted("Mentions " + noun, f"Discusses {target}{at}{cont} (no vote listed)"), kind="mention", stage="",
                        rank_act="project" if named else "mention")
        if f.get("vote"):
            return done(f"Votes on {kinds} for {target}{at}{cont}.", kind="list", stage="Vote")
        return done(f"Discusses {kinds} for {target}{at}{cont} (no vote listed).", kind="list")
    if act == "continuance":
        d = date.fromisoformat(a["cont_date"]) if a.get("cont_date") else TR.continuance_date(a["item"], date.fromisoformat(TODAY[0]))
        when = f" to {d.strftime('%a %b %-d')}" if d else ""
        what = f"{name}’s hearing" if name else f"the hearing on {TR.with_article(proj)}"
        why = " (the applicant asked)" if a.get("cont_asked") else ""
        return done(f"Postponed: {what}{at} moves{when}{why}.", stage=f"Postponed{when}")
    if act == "deal":
        deal = TR.deal_kind(a["item"])
        what = "tax and benefits talks" if deal == "tax talks" else TR.with_article(deal)
        target = name or TR.with_article(proj)
        return done(f"Votes on {what} for {target}.", stage="Vote") if f.get("vote") else done(f"Discusses {what} for {target} (no vote listed).")
    if act == "process":
        core = "the state’s new permit process for small clean-energy projects"
        return done(f"Votes on {core}.", stage="Vote") if f.get("vote") else done(f"Discusses {core} (no vote listed).")
    if act == "cancelled":
        return done(f"Canceled: the hearing on {name or noun}.", kind="list", stage="Canceled")
    if act == "withdrawn":
        return done(f"Withdrawn: the application{' by ' + name if name else ''}.", kind="list", stage="Withdrawn")
    if act == "discussion":
        return done(quoted(f"Discusses {noun}", f"Discusses {noun} (no vote listed)"), kind="mention")
    words = short_quote(" ".join((a.get("item") or "").split()), 110)
    return done(quoted(f"Mentions {noun}", f"Mentions {noun} in “{words}”" if quotable(words) else f"Mentions {noun}"), kind="mention", stage="")


TODAY = [None]


def agenda_line(h):
    return item_text(h)["say"]


def full_stop(text):
    """One period at the end, also after a name such as "Corp." """
    return re.sub(r"\.\.$", ".", text)


def quotable(words):
    """Agenda words worth quoting on a page: whole words from the start, no file names or links."""
    return bool(words) and not junk(words) and bool(re.match(r"[A-Z][A-Za-z]", words)) and len(words.split()) >= 4 \
        and words.count(")") <= words.count("(") and not re.search(r"\.pdf\b|https?://|\.docx?\b", words, re.I)


def junk(part):
    letters = sum(c.isalpha() for c in part)
    words = part.split()
    if not words or letters < 0.6 * len(part):
        return True
    if sum(len(w) for w in words) / len(words) < 2.6:
        return True
    upper = sum(c.isupper() for c in part)
    return len(part) > 30 and upper > 0.6 * letters


def clean_quote(snippet, limit=200):
    """The sentence of the agenda that contains the match, without OCR junk, at most ~200 characters."""
    text = " ".join((snippet or "").split())
    text = re.sub(r"(?:^|\s)[e€o]?¢\s*", " ", text).strip()  # a bullet the OCR read as a cent sign
    parts = [p.strip() for p in re.split(r"(?<=[.;:])\s+(?=[A-Z0-9“\"(])|\s+(?=\d{1,2}[.)]\s+[A-Z])", text) if p.strip()]
    good = [p for p in parts if not junk(p)] or parts
    start = next((i for i, p in enumerate(good) if KEYWORDS.search(p)), 0)
    out = good[start]
    for p in good[start + 1:]:
        if len(out) >= 90 or len(out) + len(p) + 1 > limit:
            break
        out += " " + p
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return out


# ---------------------------------------------------------------- meeting time and place
# Read from the top of the agenda, where towns print the date, time and place of the meeting.
# Both are left out when the header doesn't say them plainly.

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s*m\b\.?", re.I)
STAMP_RE = re.compile(r"(?:received\s+)?by\s+[\w .]{2,40}?\s+at\s+\d{1,2}:\d{2}\s*[ap]m,?\s+[\w/]+(?:\s+\d{1,2},?\s+\d{4})?"
                      r"|\b\d{1,2}:\d{2}\s*[ap]m,\s+[A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4}", re.I)
PLACE_STOP = ("PM|AM|Received|Minutes|Draft|Revised|Amended|Posted|Of|The|In|At|On|To|For|And|Pm|Am|P|A|M|Agenda|Board|Meeting|Hybrid|Select|Selectmen|Selectboard|Planning|"
              "Choose|Elect|Hear|Reports|Fund|Article|Articles|"  # "Choose Town Officers" is a warrant article, not a room
              "Conservation|Commission|Massachusetts|Ma|Warrant|Public|Will|Held|Be|City|Town|Council|Flr|Floor|Notice|"
              "Zoning|Appeals|Committee|Remote|Zoom|Teams|Location|Place|Building|Room|Date|Time|Tuesday|Monday|"
              "Wednesday|Thursday|Friday|Saturday|Sunday|Special|Annual|Fall|Spring|Regular|Open|Session|Via")
PLACE_CORE = (r"(?:City|Town) Council Chambers?|Council Chambers?|Town Hall Auditorium|Town Hall|City Hall|Town Offices?|"
              r"Town Office Building|Municipal (?:Building|Offices|Center|Complex)|Senior Center|Community Center|"
              r"Public Library|Library|Police Station|Fire Station|Fire Headquarters|Middle School|High School|"
              r"Elementary School|School|Meeting Room|Hearing Room|Conference Room|Auditorium|Chambers")
WEAK_CORE = {"meeting room", "hearing room", "conference room", "auditorium", "chambers", "school", "library"}
PLACE_WORDS = re.compile(r"\b(?:Inn|Hotel|Center|Building|Hall|Room|Library|School|Church|Station|Headquarters|Park|Club|Barn)\b"
                         r"|^\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Way|Highway|Hwy)\b\.?$")
PLACE_RE = re.compile(r"((?:(?!(?:" + PLACE_STOP + r")\b)[A-Z][\w'’.-]*\s+){0,3}(?i:" + PLACE_CORE + r")"
                      r"(?:\s+(?:[A-Z][a-z]+\s+)?(?i:(?:meeting\s+|conference\s+|hearing\s+)?room)(?:\s*#?\s*\w{1,4}\b)?)?)")
NOT_THE_MEETING = re.compile(r"(inspection|business hours|available|copies|on file|office hours|clerk'?s office)\W+(?:\w+\W+){0,4}$", re.I)
LABEL_PLACE = re.compile(r"\b(?:meeting\s+)?(?:location|place|building)(?:\s+of\s+meeting)?\s*:\s*\|?\s*", re.I)
ONLINE_RE = re.compile(r"\b(?:zoom|microsoft teams|teams meeting|virtual(?:ly)?|remote meeting|meeting id|passcode|"
                       r"webinar|join online|watch online)\b", re.I)


def date_patterns(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    month = MONTHS[d.month - 1]
    return re.compile(
        rf"\b(?:{month}|{month[:3]}\.?)\s+{d.day}(?:st|nd|rd|th)?\b(?:,?\s*{d.year})?"
        rf"|\b0?{d.month}[/-]0?{d.day}[/-](?:{d.year}|{d.year % 100})\b", re.I)


def fmt_time(m):
    hour, minute, ap = int(m.group(1)), m.group(2), m.group(3).lower()
    if not 1 <= hour <= 12 or (minute and int(minute) > 59):
        return ""
    return f"{hour}{'' if not minute or minute == '00' else ':' + minute} {ap}m"


def header_text(header):
    """The top of the agenda with clerks' date stamps removed and ALL CAPS words capitalized."""
    text = STAMP_RE.sub(" ", (header or "")[:1500])
    return re.sub(r"\b[A-Z][A-Z'’.]+\b", lambda m: m.group(0).capitalize() if len(m.group(0)) > 2 else m.group(0), text)


def meeting_time(header, iso):
    """The start time printed next to the meeting date, or after "Time:"."""
    if not header or not iso:
        return ""
    text = STAMP_RE.sub(" ", header[:1500])
    # "5:00 p.m. Executive Session … 6:00 p.m. Return to Open Session": the public part starts at 6
    if re.search(r"\bexecutive\s+session\b", text, re.I):
        om = re.search(r"(\d{1,2}(?::\d{2})?\s*[ap]\.?\s?m\.?)\s*[-–:]?\s*(?:return\s+to\s+|reconvene\s+(?:in\s+)?)?open\s+session", text, re.I) \
            or re.search(r"open\s+session\s*(?:at|[-–:])?\s*(\d{1,2}(?::\d{2})?\s*[ap]\.?\s?m\.?)", text, re.I)
        if om:
            t = TIME_RE.match(om.group(1))
            if t and fmt_time(t):
                return fmt_time(t)
    m = re.search(r"\btime(?:\s+of\s+meeting)?\s*:\s*", text, re.I)
    if m:
        t = TIME_RE.match(text, m.end())
        if t and fmt_time(t):
            return fmt_time(t)
    for d in date_patterns(iso).finditer(text):
        t = TIME_RE.search(text, d.end(), d.end() + 90)
        if t and fmt_time(t):
            return fmt_time(t)
    return ""


def clean_place(v):
    v = " ".join(v.split()).strip(" ,.-–|:*(")
    v = re.sub(r"^(?:(?:[ap]\.?m\.?|at|in|the|of|in-?person|hybrid|department|office|copy|booklet|packet|agenda|location)\s+)+", "", v, flags=re.I)
    v = re.sub(r"^.*\bMayor\s+", "", v)  # "Dominick Pangallo Mayor City Hall": a name and title from the letterhead
    v = re.sub(r",?\s+in\s+[A-Z][\w .'’-]{2,30},\s*(?:MA|NY|RI|Massachusetts)\b\.?", "", v)  # "…in Plymouth, MA": the page already says where
    if re.match(r"(?i)bos\b", v):
        v = "Select Board meeting room" if re.search(r"(?i)room", v) else ""
    v = v[:1].upper() + v[1:] if v else v
    v = re.sub(r"\b(\w+)\s+\1\b", r"\1", v)
    return v if len(v) <= 60 else v[:60].rsplit(" ", 1)[0]


def meeting_place(header, iso=None):
    """Where the meeting is held: a named room or building (with "or online" for hybrid meetings), or "online"."""
    if not header:
        return ""
    text = header_text(header)
    place = ""
    m = LABEL_PLACE.search(text)
    if m:
        value = re.sub(r"^(?:hybrid\s*[–-]\s*)?(?:(?:zoom|microsoft teams|teams|remote)\s*(?:and|&)\s*)", "",
                       text[m.end():m.end() + 160].strip(" |"), flags=re.I)
        value = re.split(r",|\*|\(|\||\s\d{2,5}\s|\s[A-Z][a-z]+(?:\s+[a-z]+)*\s*:|https?://", value)[0]
        p = PLACE_RE.search(value)
        if p:
            place = p.group(1)
        elif 6 <= len(value.strip()) <= 50 and PLACE_WORDS.search(value.strip()) and not ONLINE_RE.search(value):
            place = value
    if not place:
        start = 0
        if iso:
            d = date_patterns(iso).search(text)
            start = max(0, d.start() - 250) if d else 0
        for p in PLACE_RE.finditer(text, start, min(len(text), start + 650 if start else 700)):
            if NOT_THE_MEETING.search(text[max(0, p.start() - 60):p.start()]):
                continue
            words = p.group(1).split()
            core_only = " ".join(words).lower() in WEAK_CORE
            if core_only:
                continue
            place = p.group(1)
            break
    place = clean_place(place) if place else ""
    online = bool(ONLINE_RE.search(text))
    if place:
        return place + (" or online" if online else "")
    return "online" if online else ""


def is_pdf(g):
    return g["source_url"].lower().split("?")[0].endswith(".pdf") or "(pdf)" in (g.get("document_title") or "").lower()


def day_label(iso, ctx):
    """"Tue Oct 13", with the year only when it isn't this year."""
    d = datetime.strptime(iso[:10], "%Y-%m-%d")
    return d.strftime("%a %b %-d") + ("" if iso[:4] == ctx.today[:4] else d.strftime(", %Y"))


def meeting_board(m):
    if m["source"] == "massdep_wetlands":
        return "Wetlands filing to the state"
    if m["board_key"] == "town_meeting":
        return "Town Meeting"
    return m["board"][:1].upper() + m["board"][1:]


def quote_key(q):
    return re.sub(r"[^a-z0-9]+", " ", (q or "").lower()).strip()[:80]


def overlaps(q, quotes):
    """True when q repeats one of quotes: the same passage, or two cuts of one passage."""
    a = re.sub(r"[^a-z0-9]+", " ", (q or "").lower()).strip()
    for other in quotes:
        b = re.sub(r"[^a-z0-9]+", " ", (other or "").lower()).strip()
        if a[:80] == b[:80] or (len(a) > 40 and a[6:66] in b) or (len(b) > 40 and b[6:66] in a):
            return True
    return False


CANCELLED_DOC = re.compile(r"\bcancel+ed\b", re.I)
MEETING_CANCELLED = re.compile(r"meeting\s+(?:is\s+|has\s+been\s+|was\s+)?cancel+ed|cancel+ed\s+meeting|\bcancel+ed\s*[-–—]\s*next\s+meeting", re.I)


def group_meetings(ctx, hits):
    """Hits grouped by meeting (town, board, date), in the order given. A meeting keeps one sentence per
    agenda item (repeats merged), most important first, its time and place from the agenda header, and
    its agenda documents."""
    out = {}
    for h in hits:
        date_ = (h.get("meeting_date") or "")[:10]
        key = (h["state"], h["town"], h.get("source") == "massdep_wetlands", h.get("board_key") or board_label(h), date_)
        m = out.get(key)
        if m is None:
            header = ctx.headers.get(h["source_url"], "")
            place = meeting_place(header, date_ or None)
            cancelled = bool(CANCELLED_DOC.search(h.get("document_title") or "") or MEETING_CANCELLED.search(header[:900]))
            if h.get("board_key") == "town_meeting" and place in ("online", ""):
                place = ""  # a Town Meeting is held in person; say nothing rather than guess
            m = out[key] = {"id": "m-" + slugify(f"{h['town']}-{board_label(h)}-{date_ or 'warrant'}"),
                            "state": h["state"], "town": h["town"], "board": board_label(h), "board_key": h.get("board_key"),
                            "date": date_, "source": h.get("source"), "lines": {}, "docs": [], "found": h.get("first_seen") or "",
                            "cancelled": cancelled,
                            "topics": [], "time": meeting_time(header, date_), "place": place}
        t = item_text(h)
        name, _ = find_name(" ".join((h.get("snippet") or "").split()))
        entry = m["lines"].setdefault(t["say"], {"quotes": [], "new": False, "topics": [], "note": t["note"], "kind": t["kind"],
                                                 "key": t.get("key") or (name or find_address(h.get("snippet") or "")).lower(),
                                                 "who": who_label(h), "no": t.get("no", ""), "hit": h["id"], "rank": t.get("rank", 60),
                                                 "subj": t.get("subj", ""), "brief": t.get("brief"),
                                                 "stage": t.get("stage", ""), "facts": list(t.get("facts") or []),
                                                 "fact_pairs": list(t.get("fact_pairs") or []),
                                                 "seen": h.get("first_seen") or "", "url": h["source_url"]})
        nb = t.get("brief")
        if nb and not nb.get("duplicate_of") and (entry.get("brief") or {}).get("duplicate_of"):
            entry.update({"brief": nb, "hit": h["id"], "stage": t.get("stage", ""), "facts": list(t.get("facts") or []),
                          "fact_pairs": list(t.get("fact_pairs") or [])})
        entry["topics"] += [x for x in item_topics(h) if x not in entry["topics"]]
        q = t.get("quote")
        if q and not overlaps(q, [x for v in m["lines"].values() for x in v["quotes"]]):
            entry["quotes"].append(q)
        entry["new"] = entry["new"] or ctx.is_new(h)
        entry["note"] = entry["note"] or t["note"]
        link = h.get("doc_url") or h["source_url"]  # the live file when the town re-posted the agenda
        if link not in [d["url"] for d in m["docs"]]:
            m["docs"].append({"url": link, "pdf": is_pdf(h), "title": h.get("document_title") or ""})
        if h.get("first_seen") and (not m["found"] or h["first_seen"] < m["found"]):
            m["found"] = h["first_seen"]
        m["topics"] += [x for x in item_topics(h) if x not in m["topics"]]
    for m in out.values():
        m["lines"] = tidy_lines(m["lines"], m["board_key"] == "town_meeting")
        # A time or place the agenda header didn't give up, from a written brief (the writers read the whole document).
        for v in m["lines"].values():
            b = v.get("brief") or {}
            if not m["time"] and b.get("when_time"):
                t = TIME_RE.search(b["when_time"])
                if t and fmt_time(t):
                    m["time"] = fmt_time(t)
            # Where to watch from home, when the agenda says: a cable channel or a YouTube stream (from the write-up
            # or the top of the agenda itself).
            head_text = " ".join(ctx.headers.get(d["url"], "") for d in m["docs"]) if hasattr(ctx, "headers") else ""
            if b.get("when_place") or b.get("quote") or head_text:
                for w in re.findall(r"(?:cable\s+)?channel\s*\d+|youtube|facebook\s+live|livestream", f"{b.get('when_place') or ''} {b.get('quote') or ''} {head_text}", re.I):
                    w = re.sub(r"^cable\s+", "", w, flags=re.I)
                    w = "YouTube" if w.lower() == "youtube" else w[0].upper() + w[1:]
                    if w not in m.setdefault("watch", []):
                        m["watch"].append(w)
            # No place, or "online" for what the writer read as a room plus a Zoom link (a hybrid meeting),
            # or a place with no room when the writer's names one ("Meeting Room #1, Carver Town Hall").
            room_in_place = re.search(ROOM_WORDS, m["place"] or "")
            addr_in_place = re.search(r"\d", m["place"] or "")
            if (b.get("when_place") and m["source"] != "massdep_wetlands"
                    and (m["place"] in ("", "online") or (not room_in_place and re.search(ROOM_WORDS, b["when_place"]))
                         or (not addr_in_place and re.search(r"\b\d{1,5}\s+[A-Z][a-z]+", b["when_place"])))):
                place = short_place(b["when_place"])
                # Only a real place (a hall, room, school, street or address), not a writer's description of the setup.
                named = re.search(r"\b(?:hall|room|cent(?:er|re)|school|street|st\.|road|rd\.|avenue|ave\.|drive|lane|way|"
                                  r"building|library|office|station|chambers|complex|house|annex|church|academy)\b|\b\d{1,5} [A-Z]", place, re.I)
                vague = re.search(r"not (?:stated|given|listed|named)|in[- ]person|\bTBD\b|to be announced", place, re.I)
                hybrid = bool(re.search(r"\b(?:zoom|online|remote|hybrid|virtual|webinar|teams)\b", b["when_place"], re.I))
                if place and named and not vague and not re.fullmatch(r"(?:zoom|online|remote|virtual)[^a-z]*", place, re.I):
                    # a Town Meeting's Zoom is for speaking by permission, not for attending; and the link is not ours to promise
                    online = ", or on Zoom" if re.search(r"\bzoom\b", b["when_place"], re.I) else ", or join online"
                    m["place"] = place + (online if hybrid and m["board_key"] != "town_meeting" else "")
                elif hybrid and re.search(r"in[- ]person", b["when_place"], re.I):
                    m["place"] = "In person and online (the agenda doesn’t say which room)"
    for m in out.values():
        # a town that posts a "Revised Agenda" beside the original: the revised one is the link
        m["docs"].sort(key=lambda d: not re.search(r"revis|amend|updat", d.get("title") or "", re.I))
    return list(out.values())


ROOM_WORDS = re.compile(r"\b(?:room|rm\.?|chambers?|auditorium|cafeteria|gym(?:nasium)?|suite|floor|hearing room|selectmen.s meeting room)\b", re.I)


def short_place(text):
    """The first clause of a written place, at most about 70 characters: "Plymouth North High School at 41 Obery
    Street in Plymouth" from a sentence that goes on to name the webcast."""
    place = re.split(r"\s*;\s*", text.strip())[0]
    place = re.sub(r",?\s+and (?:Zoom|online|remote|by video|via Zoom)\b.*$", "", place, flags=re.I)
    if len(place) > 70:
        place = place[:70].rsplit(",", 1)[0]
    if place.count("(") > place.count(")"):  # cut inside a parenthesis: "Town Hall (hybrid" -> "Town Hall"
        place = place[:place.rfind("(")]
    return place.strip(" ,")


def item_topics(h):
    """The hit's topics plus any other subject its agenda item names (a clean-energy zoning article that
    covers battery storage is a battery storage item too)."""
    topics = list(h.get("topics", []))
    a = ANALYSIS.get(h.get("id"))
    if a:
        for t in ("solar", "battery_storage", "data_center"):
            if t not in topics and t in TR.SUBJECT_RE and TR.SUBJECT_RE[t].search(a["item"]):
                topics.append(t)
        rule_acts = ("town_meeting", "warrant_review", "bylaw_hearing", "bylaw_draft", "adopt")
        if "clean_energy_siting" in topics and a["action"] in rule_acts and "battery_storage" not in topics:
            topics.append("battery_storage")
    return topics


def merge_entry(into, entry):
    for q in entry["quotes"]:
        if not overlaps(q, into["quotes"]):
            into["quotes"].append(q)
    if not into.get("facts"):
        into["facts"], into["fact_pairs"] = entry.get("facts") or [], entry.get("fact_pairs") or []
    into["stage"] = into.get("stage") or entry.get("stage") or ""
    if entry.get("stage") in ("Vote", "Final vote", "Hearing") and into["stage"] in ("", "Discussion"):
        into["stage"] = entry["stage"]  # a sentence that found the vote or hearing outranks one that didn't
    into["topics"] += [t for t in entry["topics"] if t not in into["topics"]]
    into["new"] = into["new"] or entry["new"]
    into["note"] = into["note"] or entry["note"]


def tidy_lines(lines, town_meeting=False):
    """One meeting's sentences without repeats, most important first. Sentences about the same agenda
    item (the same project, address, article number or item) keep the most important one; a sentence
    contained in a longer one joins it; a sentence that only quotes the agenda is dropped when another
    sentence already shows that quote."""
    def core(text):
        return (text.lower().replace(" (continued from an earlier meeting)", "").rstrip(".")
                .replace(" will vote on ", " will discuss ").replace("zoning ordinance", "zoning bylaw"))
    named = {}
    groups = defaultdict(list)
    for k in sorted(lines, key=lambda k: (lines[k]["rank"], lines[k]["kind"] != "brief", lines[k]["kind"] != "act", -len(k))):
        if lines[k]["key"]:
            groups[lines[k]["key"]].append(k)
        else:
            named[k] = lines[k]
    for keys in groups.values():
        best = lines[keys[0]]
        say = keys[0]
        # "...review a Town Meeting article about solar rules" and "...about clean-energy permit rules" for
        # one article: one line about both.
        lead = None if best["kind"] == "brief" else re.match(r"^(.* about )([^“:]+)\.$", say)
        if lead:
            subjects = [lead.group(2)]
            for k in keys[1:]:
                mm = re.match(r"^(.* about )([^“:]+)\.$", k)
                if mm and mm.group(1) == lead.group(1) and mm.group(2) not in subjects:
                    subjects.append(mm.group(2))
            say = f"{lead.group(1)}{join_and(subjects)}."
        for k in keys[1:]:
            merge_entry(best, lines[k])
        named[say] = best
    # The same subject as a moratorium or ban at this meeting: one article, one line.
    for k in sorted(named, key=lambda k: named[k]["rank"]):
        if k not in named or named[k]["rank"] >= 10:
            continue
        for other in [o for o in named if o != k and named[o]["rank"] >= 10 and named[o].get("subj") == named[k].get("subj")
                      and named[o]["kind"] not in ("list", "brief")]:
            merge_entry(named[k], named.pop(other))
    acts = [k for k in named if named[k]["kind"] not in ("mention", "brief")]
    for short in sorted(acts, key=lambda k: (len(core(k)), " will vote on " in k)):
        longer = next((k for k in acts if k != short and k in named and core(short) in core(k)), None)
        if longer and short in named:
            merge_entry(named[longer], named.pop(short))
    # One warrant article, one line: two write-ups of "Article 19" (from two windows of one warrant) print once.
    by_article = {}
    for k in sorted(named, key=lambda k: named[k]["rank"]):
        art = re.search(r"\bArticle (\d+)\b", k)
        if not art or named[k]["kind"] == "mention":
            continue
        if art.group(1) in by_article:
            merge_entry(named[by_article[art.group(1)]], named.pop(k))
        else:
            by_article[art.group(1)] = k
    shown = set()
    out = {}
    for k in sorted(named, key=lambda k: (named[k]["kind"] == "mention", named[k]["rank"])):
        v = named[k]
        qs = {quote_key(q) for q in v["quotes"]}
        if v["kind"] == "mention" and qs and qs <= shown:
            continue
        if v["kind"] == "mention" and not qs and len(named) > 1:
            continue  # a passing mention with nothing worth quoting, next to real items
        shown |= qs
        out[k] = v
    return dict(sorted(out.items(), key=lambda kv: kv[1]["rank"]))


def posted_text(ctx, m):
    """"Agenda posted by Oct 12" only when we know it: we check every day, so a document first seen after
    the state's first sweep went up within a day of that. Documents found by the first sweep, or first
    seen after the meeting, get no posting date."""
    if not m["found"] or not ctx.known_posting(m["state"], m["found"], m["date"]):
        return ""
    what = "Filed" if m["source"] == "massdep_wetlands" else "first seen"
    return f"{what} {datetime.strptime(m['found'][:10], '%Y-%m-%d').strftime('%b %-d')}"


def place_text(place):
    """"Online meeting", or "Carver Town Hall, or join online" for a hybrid meeting."""
    if place == "online":
        return "Online meeting"
    place = re.sub(r",?\s+in\s+[A-Z][\w .'’-]{2,30},\s*(?:MA|NY|RI|Massachusetts)\b\.?", "", place)  # the page already says which town
    return place[:-len(" or online")] + ", or join online" if place.endswith(" or online") else place


def when_text(ctx, m):
    return day_label(m["date"], ctx) + (f", {m['time']}" if m["time"] else "") if m["date"] else ""


def short_quote(q, limit=220):
    q = (q or "").strip()
    if len(q) <= limit:
        return q
    return q[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def citation(ctx, m, entry=None):
    """Town, board, document and date, the item number, a short quote, the date we read it and the link."""
    url = m["docs"][0]["url"] if m["docs"] else ""
    if m["source"] == "massdep_wetlands":
        doc = f"Wetlands filing with the state, {fmt_date(m['date'])}" if m["date"] else "Wetlands filing with the state"
    elif m["board_key"] == "town_meeting":
        doc = f"Town Meeting warrant for {fmt_date(m['date'])}" if m["date"] else "Town Meeting warrant"
    else:
        doc = f"{meeting_board(m)}. Agenda for the meeting of {fmt_date(m['date'])}" if m["date"] else f"{meeting_board(m)}. Agenda"
    text = f"{m['town']}, {m['state']}, {doc}"
    if entry:
        if entry.get("no"):
            text += f", {entry['no']}"
        if entry.get("quotes"):
            text += f": “{short_quote(entry['quotes'][0])}”"
        url = entry.get("url") or url
        if entry.get("seen"):  # the day we first read the document ("Checked" on the page is the town's latest check)
            return f"{text}. Read {fmt_date(entry['seen'][:10])}. {url}"
    return f"{text}. {url}"


def tag_text(topics):
    tags = topic_tags(topics)
    return ", ".join([tags[0]] + [t.lower() for t in tags[1:]]) if tags else ""


SPEAK_TEXT = "Public hearing: anyone can attend and ask to speak."
SPEAK_COMMENT = "The agenda has a public comment period: anyone can attend and ask to speak then. It prints no other rule."
SPEAK_TM = "Town Meeting: the town’s voters decide. Ask the town clerk how others may speak."
SPEAK_NO = "The agenda lists no public comment on this item; ask the town clerk."
# In a list the rule is one short line under the items; the meeting's own page prints the full wording in the ticket.
SPEAK_TM_REP = "Representative Town Meeting: elected members vote. Ask the town clerk how others may speak."
SPEAK_SHORT = {SPEAK_TEXT: "Public hearing: anyone can attend and ask to speak.",
               SPEAK_TM_REP: "Representative Town Meeting: elected members vote.",
               SPEAK_COMMENT: "Public comment period on the agenda: anyone can attend and speak then.",
               SPEAK_TM: "Town Meeting: the town’s voters decide."}


def for_town(text, state, town):
    """A city has a city clerk: the default wording says so when the municipality is one."""
    if text and f"{state}:{town}" in CITIES:
        return (text.replace("town clerk", "city clerk").replace("Town clerk", "City clerk").replace("Town Clerk", "City Clerk")
                .replace("town hall", "city hall").replace("Town Hall", "City Hall"))
    return text


def clerk_link(ctx, state, town):
    """How to reach the town clerk: a phone number when we have one, and the town's website."""
    t = ctx.town_by_id.get(f"{state}:{town}") or {}
    phone = clerk_phone(t) if t else ""
    parts = []
    if phone:
        parts.append(f"Town clerk: {e(phone)}.")
    if t.get("website"):
        parts.append(f'<a href="{e(t["website"])}" rel="nofollow noopener" target="_blank">{e(town)}’s website</a> lists the clerk’s office.')
    return " ".join(parts)


def report_link(m, text=""):
    about = f"{m['town']}, {meeting_board(m)}" + (f", {fmt_date(m['date'])}" if m["date"] else "") + (f": {text}" if text else "")
    return f'<a class="report-link" href="/contact?about={quote(about[:300], safe="")}">Report a problem</a>'


def speak_short(m, entry):
    """One short sentence on speaking for a shared line, when the item is a live hearing or a Town Meeting vote."""
    stage = str(entry.get("stage") or "")
    if m.get("cancelled") or stage.startswith(("Postponed", "Asks to postpone", "Canceled", "Withdrawn")):
        return ""
    if m.get("board_key") == "town_meeting":
        return ("Representative Town Meeting’s elected members decide." if f"{m['state']}:{m['town']}" in REP_TM
                else "Town Meeting’s voters decide.")
    b = entry.get("brief") or {}
    if b.get("can_speak") is True and b.get("how_to_speak") and len(b["how_to_speak"]) <= 140:
        return b["how_to_speak"]
    if b.get("can_speak") is True or stage == "Hearing":
        return "Anyone can attend and ask to speak."
    return ""


def share_text(ctx, m, first, entry=None, more=()):
    """Ready to paste into Facebook or a text: the meeting, its day, time and place, its items (the first
    line, then up to two more), and how to speak."""
    when = when_text(ctx, m)
    place = place_text(m["place"]) if m["place"] and m["source"] != "massdep_wetlands" else ""
    head = f"{m['town']} {meeting_board(m)}" + (f", {when}" if when else "") + (f", {place}" if place else "")
    text = f"{head}."
    for t in ([first] if first else []) + list(more)[:2]:
        text += f" {plain_say(t)}"
        if not text.endswith((".", "!", "?", "”")):
            text += "."  # a headline carries no final period; the sentence after it needs one
    rule = speak_short(m, entry) if entry is not None else ""
    return f"{text} {for_town(rule, m['state'], m['town'])}" if rule else text


def meeting_share_url(ctx, m):
    """Upcoming meetings have their own small page (/m/...) so a shared link shows that meeting in the preview."""
    if m["date"] and m["date"] >= ctx.today:
        return f"{BASE_URL}/m/{m['id'][2:]}"
    return f"{BASE_URL}{town_path(m['state'], m['town'])}#{m['id']}"


def fact_pairs(entry):
    """The item's facts, labelled: Topics, then Where, Size, Applicant or Sponsor."""
    pairs = [("Topics", tag_text(entry["topics"]))] if entry.get("topics") else []
    pairs += entry.get("fact_pairs") or [("Details", x) for x in (entry.get("facts") or []) if x]
    seen, out = set(), []
    for k, v in pairs:
        if v and str(v).lower() not in seen:
            seen.add(str(v).lower())
            out.append((k, str(v)))
    return out


def facts_text(entry):
    """The grey facts line under an item, in a fixed order: topics, then where, size, who or permit type."""
    parts = [tag_text(entry["topics"])] + [str(x) for x in (entry.get("facts") or []) if x]
    seen, out = set(), []
    for x in parts:
        if x and x.lower() not in seen:
            seen.add(x.lower())
            out.append(x)
    return out


def et_when(iso):
    """"Oct 16, 7:07 am" in Eastern time, from an ISO timestamp: when we read a town's listing."""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ZoneInfo("America/New_York"))
    except (ValueError, AttributeError):
        return ""
    return f"{dt.strftime('%b')} {dt.day}, {dt.strftime('%-I:%M %p').lower()}"


def headline(text):
    """A headline carries no final period (the written briefs already drop theirs); abbreviations keep it.
    The status word beside it says "Discussion", so "(no vote listed)" goes; a Town Meeting vote reads one way."""
    text = text.replace(" (no vote listed)", "").replace("; no vote listed)", ")")
    text = re.sub(r"\.\s+Vote \((Article \d+)\)$", r": vote (\1)", text)
    # Subject first, as the written briefs read: "Discusses a zoning change" -> "A zoning change: discussion",
    # "Holds a hearing on a solar farm at 5 Main St" -> "A solar farm at 5 Main St: hearing" (lines with a quote stay).
    if "“" not in text and ":" not in text:
        m = re.match(r"^(Discusses|Holds a hearing on|Votes on|Decides on) (.+?)\.?$", text)
        if m:
            what = m.group(2)
            what = what[0].upper() + what[1:]
            text = f"{what}: {'discussion' if m.group(1) == 'Discusses' else 'hearing' if m.group(1).startswith('Holds') else 'vote'}"
    if re.search(r"[a-z0-9)”\"]\.$", text) and not re.search(r"\b(?:St|Rd|Ave|Dr|Ln|Blvd|Mt|No|Art|Sec|Inc|Corp|LLC|Co)\.$", text):
        return text[:-1]
    return text


STATUS_SHOWN = [(re.compile(r"^Postponed to "), "Moved to "), (re.compile(r"^Postponed$"), "Moved"),
               (re.compile(r"^Asks to postpone"), "Asked to move")]


def stage_class(stage):
    """One status vocabulary: a filled dot when the board acts (vote, hearing), a hollow dark dot for a possible
    vote, an amber tag when the date moves, grey for canceled or withdrawn, a hollow grey dot otherwise."""
    if stage.startswith(("Postponed", "Asks to postpone", "Moved", "Asked to move")):
        return "stage moved"
    if stage.startswith(("Canceled", "Withdrawn")):
        return "stage off"
    if stage.startswith("Possible vote"):
        return "stage maybe"
    if stage.startswith(("Vote", "Hearing", "Final vote", "Decided")):
        return "stage act"
    return "stage"


def stage_word(stage):
    for rx, to in STATUS_SHOWN:
        stage = rx.sub(to, stage)
    return stage


def stage_html(entry, m, ctx):
    """The item's status in the one vocabulary (stage_class), as words a person uses ("Moved to Wed Nov 4")."""
    stage = entry.get("stage") or ""
    if not stage:
        return ""
    return f'<span class="{stage_class(stage)}">{e(stage_word(stage))}</span>'


def speak_line(m, short=False):
    """One line per meeting about speaking, only when an item is a hearing that isn't postponed, canceled
    or withdrawn. `short`: the list wording (SPEAK_SHORT) for the site's own sentences."""
    line = speak_line_full(m)
    if short and line:
        for full, brief_form in SPEAK_SHORT.items():
            if line == full or line == for_town(full, m["state"], m["town"]):
                return brief_form
    return line


def speak_rule(m):
    """The agenda's own words on speaking, from the write-ups (at most two rules, said once each); "" when it gives none.
    Lists print only this; the meeting's own page prints speak_line in its ticket."""
    if m.get("cancelled"):
        return ""
    rules = []
    for v in m["lines"].values():
        if str(v.get("stage") or "").startswith(("Postponed", "Asks to postpone", "Canceled", "Withdrawn")):
            continue
        b = v.get("brief") or {}
        rule = b.get("how_to_speak")
        if b.get("can_speak") is True and rule and quote_key(rule)[:40] not in {quote_key(r)[:40] for r in rules}:
            rules.append(rule)
    return for_town(" ".join(rules[:2]), m["state"], m["town"]) if rules else ""


def speak_line_full(m):
    entries = [v for v in m["lines"].values()
               if not str(v.get("stage") or "").startswith(("Postponed", "Asks to postpone", "Canceled", "Withdrawn"))]
    rules = []
    for v in entries:
        b = v.get("brief") or {}
        rule = b.get("how_to_speak")
        # two write-ups of one agenda give the same rule in slightly different words: print it once
        if b.get("can_speak") is True and rule and quote_key(rule)[:40] not in {quote_key(r)[:40] for r in rules}:
            rules.append(rule)
    if rules:
        return for_town(" ".join(rules[:2]), m["state"], m["town"])
    if m.get("board_key") == "town_meeting" and entries:
        return SPEAK_TM_REP if f"{m['state']}:{m['town']}" in REP_TM else SPEAK_TM
    if any(re.search(r"\bhearing\b", str(v.get("stage") or ""), re.I) and not (v.get("brief") or {}).get("can_speak") is False
           for v in entries):
        return for_town(SPEAK_TEXT, m["state"], m["town"])
    if any((v.get("brief") or {}).get("can_speak") is True for v in entries):
        return SPEAK_COMMENT  # a vote or discussion with a public comment item on the agenda, not a hearing
    if entries and m.get("board_key") != "town_meeting":
        return SPEAK_NONE
    return ""


SPEAK_NONE = "No public hearing on these items. The agenda doesn’t say whether the board takes comments on them."


def meeting_head(ctx, m, show_town=True, with_board=True, with_when=True, doc_link=""):
    """"Carver · Planning Board · Town Hall Room 1": the line above a meeting's items. In a list the day is
    printed once above the day's meetings and the time sits in its own column, so `with_when` is off there."""
    parts = []
    if show_town:
        st = f", {m['state']}" if m["state"] != "MA" else ""
        parts.append(f'<span class="meet-town">{ctx.town_link(m["state"], m["town"])}{e(st)}</span>')
    if with_board:
        parts.append(f"<span>{e(meeting_board(m))}</span>")
    when = when_text(ctx, m)
    if with_when and m["date"]:
        parts.append(f'<span class="meet-day"><time datetime="{m["date"]}">{e(when)}</time></span>')
    elif with_when and m["board_key"] == "town_meeting":
        parts.append('<span class="meet-day">Date not found on the warrant</span>')
    if m.get("cancelled"):
        parts.append('<span class="meet-canceled">Canceled by the town</span>')
    if m["place"] and m["source"] != "massdep_wetlands":
        parts.append(f'<span class="meet-place">{e(place_text(m["place"]))}</span>')
    if doc_link:  # the short list puts the agenda link on the meeting's top line (under the place on a phone)
        parts.append(f'<span class="meet-doc">{doc_link}</span>')
    return " ".join(parts)


# Plain words for the terms an agenda uses, printed on a meeting's own page when its items use them (the first four).
TERMS = [
    (re.compile(r"\bnotice of intent\b|\bNOI\b", re.I), "Notice of Intent",
     "the application for a wetlands permit, filed with the Conservation Commission"),
    (re.compile(r"\bcontinu(?:ed|ance)\b", re.I), "Continued", "put off to a later meeting; a continuance is the request to do that"),
    (re.compile(r"bordering vegetated wetland|\bBVW\b", re.I), "Bordering Vegetated Wetland",
     "a wet, plant-covered area along a stream, pond or marsh, protected by state law"),
    (re.compile(r"\bdual[\s-]use\b", re.I), "Dual-use", "solar panels raised high enough that farming goes on underneath"),
    (re.compile(r"\bground[\s-]mounted\b", re.I), "Ground-mounted", "panels on frames in a field, not on a roof"),
    (re.compile(r"\bassessors?.? map\b|\bmap \d+,? lots? \d+", re.I), "Assessors Map and Lot", "the town’s own number for the piece of land"),
    (re.compile(r"\bDEP file\b|\bMassDEP file\b", re.I), "DEP File #", "the state environmental agency’s number for the wetlands filing"),
    (re.compile(r"\border of conditions\b|\bOOC\b"), "Order of Conditions", "the wetlands permit, with the rules the work must follow"),
    (re.compile(r"\bbuffer zone\b", re.I), "Buffer Zone", "the land next to a wetland (the first 100 feet under state law; towns set their own lines inside it), where work needs the Conservation Commission’s review"),
    (re.compile(r"request for determination|determination of applicability|\bRDA\b", re.I), "Request for Determination",
     "asks the Conservation Commission whether the wetlands law applies to a piece of work"),
    (re.compile(r"\bcomprehensive permit\b|\b40B\b", re.I), "Comprehensive permit",
     "the state’s 40B permit: one permit from the Zoning Board of Appeals for housing with affordable units, which can override local zoning"),
    (re.compile(r"\b40R\b|smart growth", re.I), "40R district",
     "a smart-growth zoning district for denser housing with a share kept affordable, which the state pays the town to adopt"),
    (re.compile(r"\bspecial permit\b", re.I), "Special permit", "permission the zoning bylaw lets a board grant for a use it allows only with conditions"),
    (re.compile(r"\bsite plan\b", re.I), "Site plan review", "the board’s check of a project’s layout, parking, drainage and lighting"),
    (re.compile(r"\bvariance\b", re.I), "Variance", "permission to depart from a zoning rule because the lot’s shape, size or ground makes the rule a hardship"),
    (re.compile(r"\boverlay district\b", re.I), "Overlay district", "a zoning layer with extra rules on top of the zone underneath"),
    (re.compile(r"\bmoratori", re.I), "Moratorium", "a temporary ban"),
    (re.compile(r"\bdecommission", re.I), "Decommissioning", "taking a project down at the end of its life and restoring the land"),
    (re.compile(r"\bBESS\b"), "BESS", "large batteries that store electricity and feed it back to the grid (a battery energy storage system)"),
    (re.compile(r"battery energy storage", re.I), "Battery energy storage", "large batteries that store electricity and feed it back to the grid (a battery energy storage system)"),
    (re.compile(r"\binterconnection\b", re.I), "Interconnection", "connecting a project to the electric grid"),
    (re.compile(r"\bPILOT\b|payments? in lieu of tax", re.I), "PILOT",
     "a payment in lieu of taxes: a yearly payment the owner and the town agree on instead of property tax"),
    (re.compile(r"\b61A\b", re.I), "Chapter 61A", "the farmland tax break; when the land leaves farming, the town has a right of first refusal to buy it"),
    (re.compile(r"\bANR\b|approval not required", re.I), "ANR plan",
     "an “approval not required” plan: a lot division along an existing road that the Planning Board endorses because it is not a subdivision"),
    (re.compile(r"\bexecutive session\b", re.I), "Executive session", "a closed part of the meeting; the public leaves"),
    (re.compile(r"\bapplicant\b|\bpetitioner\b", re.I), "Applicant", "the person or company asking for the permit"),
]


def who_votes_text(m):
    """A Planning Board's hearing on a zoning change is not the vote: the board recommends, Town Meeting (or a
    city's council) adopts. One line in the meeting's ticket, when an item is such a hearing."""
    if m.get("cancelled") or m.get("board_key") != "planning_board":
        return ""
    zoning = {"zoning_amendment", "moratorium", "clean_energy_siting"}
    if not any(v.get("stage") == "Hearing" and zoning & set(v.get("topics") or []) for v in m["lines"].values()):
        return ""
    city = f"{m['state']}:{m['town']}" in CITIES
    who, what = ("the City Council", "ordinance") if city else ("Town Meeting", "bylaw")
    return f"After the hearing the Planning Board makes a recommendation; {who} votes on the {what}."


VTIMEZONE_NY = ["BEGIN:VTIMEZONE", "TZID:America/New_York",
                "BEGIN:DAYLIGHT", "TZOFFSETFROM:-0500", "TZOFFSETTO:-0400", "TZNAME:EDT", "DTSTART:19700308T020000",
                "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU", "END:DAYLIGHT",
                "BEGIN:STANDARD", "TZOFFSETFROM:-0400", "TZOFFSETTO:-0500", "TZNAME:EST", "DTSTART:19701101T020000",
                "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU", "END:STANDARD", "END:VTIMEZONE"]


def meeting_ics(ctx, m):
    """One calendar event for a meeting's own page: its hour in Eastern time when the agenda gives one (two hours
    long), else an all-day event; the room; the items as the description; cancelled when the town says so."""
    t = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m", m.get("time") or "", re.I)
    day = m["date"].replace("-", "")
    if t:
        hour = int(t.group(1)) % 12 + (12 if t.group(3).lower() == "p" else 0)
        minute = int(t.group(2) or 0)
        start = f"DTSTART;TZID=America/New_York:{day}T{hour:02d}{minute:02d}00"
        end = f"DTEND;TZID=America/New_York:{day}T{min(hour + 2, 23):02d}{minute:02d}00"
    else:
        nxt = (date.fromisoformat(m["date"]) + timedelta(days=1)).isoformat().replace("-", "")
        start, end = f"DTSTART;VALUE=DATE:{day}", f"DTEND;VALUE=DATE:{nxt}"
    place = place_text(m["place"]) if m["place"] and m["source"] != "massdep_wetlands" else ""
    lines = [plain_say(t_) for t_, _ in real_lines(m)][:4]
    page = meeting_share_url(ctx, m)
    doc = m["docs"][0]["url"] if m["docs"] else ""
    desc = ([("This meeting is canceled by the town.")] if m.get("cancelled") else []) + [f"• {x}" for x in lines] + \
        ["", f"Agenda: {doc}" if doc else "", f"Page: {page}", "Confirm the time and place with the town; agendas can change."]

    def ics_text(s):
        return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    def fold(line):
        out, cur = [], ""
        for ch in line:
            if len((cur + ch).encode("utf-8")) > (74 if out else 75):
                out.append(cur)
                cur = ""
            cur += ch
        out.append(cur)
        return "\r\n ".join(out)

    first_line = re.sub(r"^(?:Postponed|Canceled|Withdrawn|Asks to postpone|Moved|Asked to move)[^:]*:\s*", "", lines[0]) if lines else ""
    summary = f"{'CANCELED: ' if m.get('cancelled') else ''}{m['town']} {meeting_board(m)}" + (f": {first_line}" if first_line else "")
    ev = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{SITE_NAME}//Meeting//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
          *(VTIMEZONE_NY if t else []),
          "BEGIN:VEVENT", f"UID:{m['id']}@agendaahead", f"DTSTAMP:{ctx.today.replace('-', '')}T120000Z", start, end,
          f"SUMMARY:{ics_text(summary)}",
          f"LOCATION:{ics_text((place + ', ' if place else '') + m['town'] + ', ' + m['state'])}",
          f"DESCRIPTION:{ics_text(chr(10).join(x for x in desc if x is not None))}", f"URL:{page}"]
    if m.get("cancelled"):
        ev.append("STATUS:CANCELLED")
    ev += ["END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(fold(x) for x in ev) + "\r\n"


def terms_html(m, source):
    """The agenda's terms in plain words, from the items' quotes and write-ups."""
    parts = list(m["lines"])
    for en in m["lines"].values():
        parts += list(en.get("quotes") or [])
        b = en.get("brief") or {}
        parts += [b.get(k) or "" for k in ("what", "quote", "next", "how_to_speak")]
    text = " ".join(p for p in parts if p)
    found, plains = [], set()
    for rx, name, plain in TERMS:
        if not rx.search(text) or plain in plains:
            continue
        # a write-up that already explains the term in passing ("a wetlands permit (a Notice of Intent)") needs no second gloss
        if re.search(r"\((?:a |an |the )?" + re.escape(name) + r"\)|" + re.escape(name) + r"\s*\(", text, re.I):
            continue
        found.append((name, plain))
        plains.add(plain)
    found = found[:6]
    if not found:
        return ""
    return (f'<p class="terms"><b>Words on {e(source)}.</b> '
            + " ".join(f"<dfn>{e(name)}</dfn>: {e(plain)}." for name, plain in found) + "</p>")


def meeting_html(ctx, m, show_town=True, lines_shown=4, full=False):
    """One meeting in the site's one item format: a meeting line (town, board, day and time, place), then
    per item one line that starts with the stage, the brief's sentence when there is one, a grey facts
    line with the stage word, and at the end one source link. `full` (the meeting's own page) adds the
    agenda's wording behind a tap and the Attorney General note; lists carry none of that."""
    dep = m["source"] == "massdep_wetlands"
    source = "the state filing" if dep else ("the warrant" if m["board_key"] == "town_meeting" else "the agenda")

    notes_shown = []

    def line(text, entry, first=False):
        b = entry.get("brief")
        # "New" is for a project the town has not seen before, not every freshly posted agenda
        new = entry["new"] and not carried_over(entry) and not text.startswith("New ")
        what = ""
        if b and b.get("what") and quote_key(b["what"]) != quote_key(text):
            w = b["what"]
            mt_ = STAGE_DATE.match(str(entry.get("stage") or ""))
            if mt_:  # "Postponed to Wed Nov 4" is the status; the write-up needn't end by saying so again
                w = re.sub(rf"\s*[^.]*\b{mt_.group(3)}[a-z]*\.?\s+{int(mt_.group(4))}\b[^.]*\.$", "", w, flags=re.I) or w
            what = f'<p class="brief-what">{e(w)}</p>'
        if b and b.get("history"):  # what happened on this item before, from our own records
            what += f'<p class="line-before"><b>Before this:</b> {e(b["history"])}</p>'
        facts = ('<span class="is-new">New on an agenda</span>' if new else "") + "".join(f"<span>{e(x)}</span>" for x in facts_text(entry))
        stage = stage_html(entry, m, ctx)
        # a list keeps the headline, the write-up and "New"; the facts line (topics, address, applicant) is on the meeting's page
        pairs = fact_pairs(entry)
        facts_html = (((f'<p class="line-facts"><span class="is-new">New on an agenda</span></p>' if new else "")
                       + (f'<dl class="facts-list item-facts">{"".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in pairs)}</dl>' if pairs else ""))
                      if full else ('<p class="line-facts"><span class="is-new">New on an agenda</span></p>' if new else ""))
        extra = ""
        if str(entry.get("stage") or "").startswith("Asks to postpone") and m.get("date") and m["date"] >= ctx.today:
            # a request is not a decision: the board says yes or no at this meeting
            extra += '<p class="line-next">The board decides at this meeting whether to postpone; until it does, the hearing is still on.</p>'
        if full:
            mt = STAGE_DATE.match(str(entry.get("stage") or ""))
            # the stage already says "Postponed to Wed Nov 4": a next line that says it again is noise
            repeats = bool(mt and re.search(rf"\b{mt.group(3)}(?:[a-z]*\.?)\s+{int(mt.group(4))}\b", b.get("next") or "", re.I)) if b else False
            if b and b.get("next") and not repeats:
                extra += f'<p class="line-next">{e(b["next"])}</p>'
            if b and b.get("can_speak") is False:
                extra += f'<p class="line-next">{for_town(SPEAK_NO, m["state"], m["town"])}</p>'
            if entry["note"] and entry["note"] != HEARING_NOTE and entry["note"] not in notes_shown:
                notes_shown.append(entry["note"])  # the same note (a two-thirds vote, AG review) once per meeting
                extra += f'<p class="line-note">{e(entry["note"])}</p>'
            quotes = [b["quote"]] if b and b.get("quote") else [q for q in entry["quotes"][:3] if quote_key(q)[:60] not in quote_key(text)]
            if quotes:
                extra += (f'<details class="item-words"><summary>{e(BRIEF_LABELS["quote"]) if b else "Agenda wording"}</summary>'
                          f'<p class="item-from">Quoted from {source}:</p>'
                          + "".join(f'<blockquote class="item-quote">{e(q)}</blockquote>' for q in quotes) + "</details>")
        text = headline(text)
        if not full and not b and entry.get("kind") == "mention":
            # a list doesn't print a stray fragment of the agenda as a headline; the meeting's page keeps it
            text = re.sub(r"(?:\s+in|:)\s*“[^”]*”\.?$", "", text).rstrip(".")
        # In a list, the headline taps through to the meeting's own page (built for meetings still ahead).
        say = (f'<a class="line-link" href="/m/{m["id"][2:]}">{e(text)}</a>' if not full and m.get("date") and m["date"] >= ctx.today
               else e(text))
        kind = " brief" if b else (" mention" if entry.get("kind") == "mention" else "")
        # the one-line view prints the meeting's words ("Carver · Planning Board: ") ahead of the first item
        head_words = ""
        if first and not full:
            parts = []
            if show_town:
                parts.append(ctx.town_link(m["state"], m["town"]) + ("" if m["state"] == "MA" else e(f", {m['state']}")))
            if not text.lower().startswith(meeting_board(m).lower()):
                parts.append(e(meeting_board(m)))
            if parts:
                head_words = f'<span class="line-head" data-slop-ignore>{" · ".join(parts)}: </span>'
        return f'<li class="line{kind}"><p class="line-say"><span>{head_words}{say}</span>{stage}</p>{what}{facts_html}{extra}</li>'

    entries = list(m["lines"].items())
    if m.get("cancelled"):
        entries = [(t, {**en, "stage": "Canceled"}) for t, en in entries]
    lines = "".join(line(t, en, first=(i == 0)) for i, (t, en) in enumerate(entries[:lines_shown]))
    if entries[lines_shown:]:
        lines += (f'<li class="line-more"><details class="more"><summary>{plural(len(entries) - lines_shown, "more item")}</summary>'
                  f'<ul class="lines">{"".join(line(t, en) for t, en in entries[lines_shown:])}</ul></details></li>')
    what = "filing" if dep else ("warrant" if m["board_key"] == "town_meeting" else "agenda")
    where = f"{m['town']} {meeting_board(m)}, {day_label(m['date'], ctx) if m['date'] else 'no date'}"
    d = m["docs"][0] if m["docs"] else None
    link = (f'<a class="item-link" href="{e(d["url"])}" rel="nofollow noopener" target="_blank">{what.capitalize()}'
            f'{" (PDF)" if d["pdf"] else ""}<span class="sr-only">: {e(where)}</span></a>') if d else ""
    speak = "" if full else speak_rule(m)  # the meeting's own page says it in the ticket instead
    tail = "" if full else link
    county = county_key(ctx, m["state"], m["town"])
    when = ""
    if not full:
        # the time in its own column; the day is the heading above the day's meetings
        when = (f'<span class="meet-when"><time datetime="{m["date"]}">{e(m["time"])}</time></span>' if m["time"] and m["date"]
                else '<span class="meet-when none">No time listed</span>')
    head = "" if full else f'<p class="meet-head" data-slop-ignore>{meeting_head(ctx, m, show_town, with_when=False, doc_link=link)}</p>'
    speak_html = f'<p class="speak-line"><b>Speaking:</b> {e(speak)}</p>' if speak else ""
    terms = terms_html(m, source) if full and not m.get("cancelled") else ""
    return f"""<li class="meeting{' canceled' if m.get('cancelled') else ''}" id="{m['id']}" data-county="{e(county)}" data-state="{e(m['state'])}" data-town="{e(m['town'])}">
  {when}
  {head}
  {speak_html}
  <ul class="lines">{lines}</ul>
  {terms}
  {f'<p class="meet-src">{tail}</p>' if tail else ''}
</li>"""


def time_key(m):
    """Minutes past midnight for "6:30 pm", or a large number when the agenda lists no time."""
    mt = re.match(r"(\d{1,2})(?::(\d{2}))?\s*([ap])m", (m.get("time") or "").strip(), re.I)
    if not mt:
        return 10_000
    h = int(mt.group(1)) % 12 + (12 if mt.group(3).lower() == "p" else 0)
    return h * 60 + int(mt.group(2) or 0)


def day_groups(ctx, meetings, show_town=True, lines_shown=4):
    """Meetings under a heading per day, in the day order given; within a day in time order, no time last."""
    groups = []
    for m in meetings:
        key = m["date"] or ""
        if groups and groups[-1][0] == key:
            groups[-1][1].append(m)
        else:
            groups.append((key, [m]))
    out = []
    for key, ms in groups:
        ms = sorted(ms, key=time_key)
        if key:
            label = f'<time datetime="{key}">{e(day_label(key, ctx))}</time>'
        else:
            label = "Date not found on the warrant"
        out.append(f'<section class="day-group"><h3 class="day">{label}</h3><ol class="meetings">'
                   + "".join(meeting_html(ctx, m, show_town, lines_shown) for m in ms) + "</ol></section>")
    return f'<div class="days">{"".join(out)}</div>'


def meeting_list(ctx, meetings, show_town=True, shown=3, more="Show more", empty="", lines_shown=4):
    """The first few meetings, grouped by day, the rest behind one "Show more"."""
    if not meetings:
        return f'<p class="empty">{empty}</p>' if empty else ""
    html = day_groups(ctx, meetings[:shown], show_town, lines_shown)
    rest = meetings[shown:]
    if rest:
        html += (f'<details class="more"><summary>{more} ({len(rest)})</summary>'
                 + day_groups(ctx, rest, show_town, lines_shown) + '</details>')
    return html


def split_hits(ctx, hits):
    upcoming = sorted((h for h in hits if ctx.is_upcoming(h)), key=lambda h: (h["meeting_date"], h["state"] != "MA", h["town"]))
    past = sorted((h for h in hits if h.get("meeting_date") and not ctx.is_upcoming(h)),
                  key=lambda h: (h["meeting_date"], h["town"]), reverse=True)
    undated = sorted((h for h in hits if not h.get("meeting_date")), key=lambda h: (h["town"], h.get("first_seen", "")))
    return upcoming, past, undated


# ---------------------------------------------------------------- tracker and AG tables (reference pages)

def tracker_rows(ctx, items):
    rows = []
    for item in sorted(items, key=lambda i: i.get("key_date") or "", reverse=True):
        group = status_group(item)
        topic = item.get("topic", "")
        town = item["town"]
        body = (f'<p>{e(item.get("summary", ""))}</p>{sources_html(item.get("sources", []))}'
                f'<p class="rec-links"><a href="{town_path(item.get("state", "MA"), town)}">Everything about {e(town)}</a>'
                f'{" (" + e(item["county"]) + " County)" if item.get("county") else ""}</p>')
        rows.append(rec_li(e(town), f"{e(item.get('action', ''))}, {e(topic.lower())}",
                           f"<b>{e(item.get('status', ''))}</b>, {fmt_date(item.get('key_date'))}", body,
                           f' data-group="{group}" data-topic="{e(topic.lower())}" data-county="{e(item.get("county", ""))}"'))
    return "\n".join(rows)


TRACKER_HEAD = ('<thead><tr><th scope="col">Town</th><th scope="col">Action</th><th scope="col">Status</th>'
                '<th scope="col">Date</th><th scope="col" class="col-summary">What happened</th></tr></thead>')


def tracker_table(ctx, items, table_id=None):
    tid = f' id="{table_id}"' if table_id else ""
    return f'<div class="rec-list"{tid}><ul class="recs">{tracker_rows(ctx, items)}</ul></div>'


def ag_row(ctx, r, filters=False):
    year = (r.get("decision_date") or "")[:4]
    attrs = (f' data-outcome="{e(r.get("outcome", ""))}" data-bylaw="{e(r.get("bylaw_type", ""))}"'
             f' data-tech="{e(r.get("technology", ""))}" data-year="{year}" data-county="{e(r.get("county") or "")}"'
             + (f' data-csv="{r["_csv"]}"' if "_csv" in r else "")) if filters else ""
    case = f", case {e(str(r['case_number']))}{e(r.get('letter_note', ''))}" if r.get("case_number") else ""
    posted_copy = "copy of the letter the town posted" in (r.get("portal_document_name") or "")
    label = ("Town Clerk’s posting of the decision" if posted_copy else "Decision letter") if r.get("record_type") == "ag_decision" else "Source"
    letter = (f'<a href="{e(r["letter_url"])}" rel="nofollow noopener" target="_blank">{label}{case}</a>'
              if r.get("letter_url") else "")
    town = ag_town(r.get("town"))
    city = " (city)" if "(city)" in (r.get("town") or "") else ""
    what = "Court ruling" if r.get("record_type") == "court_ruling" else (r.get("bylaw_type") or "bylaw")
    src = abs_url(r.get("letter_url") or "")
    if r.get("record_type") == "court_ruling":
        citation = (f"{court_cite(r)}. {smart_quotes(r.get('summary') or '')}" + (f" Source: {src}." if src else "")
                    + f" Via Agenda Ahead, {BASE_URL}/attorney-general/rulings.")
    else:
        citation = (f"{town}, MA, {r.get('article') or what}: {r.get('outcome') or 'pending'}"
                    + (f" by the Massachusetts Attorney General, case {r['case_number']}{r.get('letter_note') or ''}" if r.get("case_number") else "")
                    + (f", {fmt_date(r['decision_date'])}" if len(r.get("decision_date") or "") == 10 else "")
                    + f". {smart_quotes(r.get('summary') or '')}"
                    + (f" Source: {src}." if src else "") + f" Via Agenda Ahead, {BASE_URL}/attorney-general/rulings.")
    if r.get("date_note"):  # "decided between Sep 14 and Sep 22": the caveat travels with the pasted citation
        citation = citation.replace(f", {fmt_date(r['decision_date'])}.", f", {fmt_date(r['decision_date'])} ({r['date_note']}).", 1)
    cite_btn = f' <button type="button" class="link-btn cite" data-copy="{e(citation)}" hidden>Copy citation</button>'
    kind = "Court ruling" if r.get("record_type") == "court_ruling" else first_up(r.get("bylaw_type") or "Bylaw")
    tech = r.get("technology") or ""
    d = r.get("decision_date") or ""
    when = (fmt_date(d) if len(d) == 10 else datetime.strptime(d, "%Y-%m").strftime("%b %Y") if len(d) == 7 else d) if d else "Awaiting a decision"
    dn = re.match(r"decided between (\w+ \d+) and (\w+ \d+), (\d{4})", r.get("date_note") or "")
    if dn:
        when = f"decided {dn.group(1)} to {dn.group(2)}, {dn.group(3)}"
    outcome = first_up(r.get("outcome") or "pending")
    meeting = " (meeting date)" if r.get("decision_date") and (r.get("outcome") or "").startswith(("proposed", "pending")) else ""
    sub = court_cite(r) if r.get("record_type") == "court_ruling" else r.get("article", "")
    body = (f'<p class="rec-sub">{e(sub)}</p>'
            + (f'<p class="form-note">Date: {e(r["date_note"])}.</p>' if r.get("date_note") else "") +
            f'<p>{e(smart_quotes(r.get("summary", "")))}</p>'
            f'<p class="rec-links">{letter}{cite_btn}</p>'
            + (f'<p class="rec-links"><a href="{town_path("MA", town)}">Everything about {e(town)}</a></p>' if f"MA:{town}" in ctx.town_by_id else ""))
    if r.get("record_type") == "pending_ag_review":
        attrs += ' data-nocount="1"'
    return rec_li(f"{e(town)}{e(city)}", f"{e(kind)}{', ' + e(tech) if tech else ''}",
                  f'<b class="tag {outcome_tag(r.get("outcome"))}">{e(outcome)}</b>, {when}{meeting}', body, attrs)


def outcome_tag(outcome):
    """One look per outcome: approved and wins for solar green, approved in part amber, disapproved red, the rest grey."""
    o = (outcome or "").lower()
    if o == "approved in part":
        return "tag-part"
    if o.startswith("disapproved") or "upheld" in o or o.startswith("expired"):
        return "tag-no"
    if o.startswith("approved") or "vacated" in o or "annulled" in o or "enforced" in o or "protected" in o or o.startswith("ruled for") or o.startswith("adopted") or o.startswith("in effect"):
        return "tag-ok"
    return "tag-wait"


def court_cite(r):
    """The case as a court cites it: "Tracer Lane II Realty, LLC v. City of Waltham, 489 Mass. 775 (2022)", or
    "Town of Wendell v. Campbell, No. 25 MISC 000014 (Mass. Land Ct. Mar. 2026)"."""
    art = (r.get("article") or "").strip()
    d = r.get("decision_date") or ""
    year = d[:4]
    m = re.match(r"(.+?),\s*(\d+ Mass\.(?: App\. Ct\.)? \d+)\s*\((?:SJC|AC|Supreme Judicial Court|Appeals Court)-\d+\)\s*$", art)
    if m:
        return f"{m.group(1)}, {m.group(2)} ({year})"
    m = re.match(r"(.+?),\s*Land Ct\.\s*(?:No\.\s*)?(\d+ MISC \d+)\s*(?:\([A-Z]+\))?\s*$", art)
    if m:
        when = fmt_date(d) if len(d) == 10 else (datetime.strptime(d, "%Y-%m").strftime("%b. %Y").replace("May.", "May") if len(d) == 7 else year)
        return f"{m.group(1)}, No. {m.group(2)} (Mass. Land Ct. {when})"
    return art + (f" ({year})" if year else "")


def ag_letter_links(ctx, towns, technology):
    """"Shutesbury (case 12047, Jan 20, 2026), Templeton (…) and Gill (…)", each linked to its decision letter."""
    out = []
    for town in towns:
        r = next((x for x in ctx.ag if ag_town(x.get("town")) == town and x.get("technology") == technology and x.get("letter_url")), None)
        if not r:
            out.append(e(town))
            continue
        out.append(f'<a href="{e(r["letter_url"])}" rel="nofollow noopener" target="_blank">{e(town)}</a> (case {e(str(r["case_number"]))}, {fmt_date(r["decision_date"])})')
    return join_and(out)


def ag_csv(rows):
    """Every ruling as a spreadsheet: one row per decision letter and subject."""
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["town", "county", "article", "bylaw_type", "technology", "decision_date", "outcome", "record_type",
                "case_number", "letter_url", "summary"])
    for r in sorted(rows, key=lambda r: r.get("decision_date") or "", reverse=True):
        url = r.get("letter_url") or ""
        w.writerow([ag_town(r.get("town")), r.get("county") or "", r.get("article") or "", r.get("bylaw_type") or "",
                    r.get("technology") or "", r.get("decision_date") or "", r.get("outcome") or "", r.get("record_type") or "",
                    r.get("case_number") or "", (BASE_URL + url) if url.startswith("/") else url, plain_ag(r.get("summary") or "")])
    return out.getvalue()


def actions_csv(items):
    """Town and city actions as a spreadsheet."""
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["town", "county", "topic", "action", "status", "key_date", "date_label", "body", "summary", "sources"])
    for i in items:
        srcs = " ".join(x.get("url") or "" for x in (i.get("sources") or []) if isinstance(x, dict))
        w.writerow([i.get("town") or "", i.get("county") or "", i.get("topic") or "", i.get("action") or "", i.get("status") or "",
                    i.get("key_date") or "", i.get("date_label") or "", i.get("body") or "", plain_ag(i.get("summary") or ""), srcs])
    return out.getvalue()


def rec_li(town, what, key, body, attrs="", rid=""):
    """One record as a box that opens: the town, what it is and its status in one line; the details inside."""
    idattr = f' id="{rid}"' if rid else ""
    return (f'<li class="rec"{idattr}{attrs}><details><summary><span class="rec-town">{town}</span>'
            f'<span class="rec-what">{what}</span><span class="rec-key">{key}</span></summary>'
            f'<div class="rec-body">{body}</div></details></li>')


def ag_table(ctx, rows, table_id=None, filters=False, group=None, by_year=False):
    """The Attorney General's rulings as records, newest first, under a heading per year when by_year."""
    tid = f' id="{table_id}"' if table_id else ""
    grp = f' data-filter-group="{group or table_id}"' if filters else ""
    ordered = sorted(rows, key=lambda r: r.get("decision_date") or "", reverse=True)
    if not by_year:
        return f'<div class="rec-list"{tid}{grp}><ul class="recs">{"".join(ag_row(ctx, r, filters) for r in ordered)}</ul></div>'
    years = []
    for r in ordered:
        y = (r.get("decision_date") or "")[:4] or "Awaiting a decision"
        if not years or years[-1][0] != y:
            years.append((y, []))
        years[-1][1].append(r)
    out = "".join(f'<section class="rec-group" data-year-group><h2 class="rec-head">{e(y)} <span class="sub-count">{plural(len(rs), "bylaw" if y == "Awaiting a decision" else "ruling")}</span></h2>'
                  f'<ul class="recs">{"".join(ag_row(ctx, r, filters) for r in rs)}</ul></section>' for y, rs in years)
    return f'<div class="rec-list"{tid}{grp}>{out}</div>'


def ag_moratorium_record(ag, since=None):
    """Solar and battery storage moratoriums the Attorney General ruled on (approved or disapproved)
    since the Tracer Lane II decision. Counted in decision letters; `articles` counts Town Meeting
    articles ("Articles 26 and 27" is two)."""
    since = since or TRACER_LANE
    rows = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") == "moratorium"
            and r.get("technology") != "data center"  # the record is about solar and battery storage
            and (r.get("decision_date") or "") >= since and r.get("outcome") in ("approved", "disapproved")]
    return {
        "rows": sorted(rows, key=lambda r: r["decision_date"], reverse=True),
        "total": len(rows),
        "disapproved": sum(1 for r in rows if r["outcome"] == "disapproved"),
        "articles": sum(ag_articles(r) for r in rows),
        "towns": len({r["town"] for r in rows}),
    }


def moratorium_lines(ag):
    """The headline numbers, all from the same rows as the "Outcomes by type" table."""
    rec = ag_moratorium_record(ag)
    n, d = rec["total"], rec["disapproved"]
    lead = (f"Since the Supreme Judicial Court’s Tracer Lane II decision (June 2, 2022), the Attorney General has ruled on "
            f"{n} town moratoriums on solar or battery storage and disapproved {'all ' + str(n) if d == n else f'{d} of them'}")
    detail = f" ({plural(rec['articles'], 'Town Meeting article')} in {plural(rec['towns'], 'town')})."
    ids = {id(r) for r in rec["rows"]}
    others = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") == "moratorium" and id(r) not in ids]
    notes = []
    for r in sorted(others, key=lambda r: r.get("decision_date") or ""):
        when = datetime.strptime(r["decision_date"], "%Y-%m-%d").strftime("%B %Y")
        if (r.get("outcome") or "").startswith("approved") and r["decision_date"] < TRACER_LANE:
            notes.append(f"{ag_town(r['town'])}’s, approved in {when} (before that decision)")
        else:
            notes.append(f"{ag_town(r['town'])}’s, which the Attorney General didn’t rule on because the town replaced it ({when})"
                         if "moot" in (r.get("outcome") or "") else f"{ag_town(r['town'])}’s ({r.get('outcome')}, {when})")
    both = notes[0] if len(notes) == 1 else ", ".join(notes[:-1]) + ", and " + notes[-1] if notes else ""
    extra = (f"The table above also counts {plural(len(notes), 'other moratorium ruling')}: {both}." if notes else "")
    return lead + detail, extra, rec


def topic_counts(ctx, key, state=None):
    tp = TOPIC_PAGE_BY_KEY.get(key) or {}
    match = tp.get("hits") or (lambda h: key in h.get("topics", []))
    hits = [h for h in ctx.hits if match(h) and (state is None or h["state"] == state)]
    return {
        "hits": hits,
        "items": len(hits),
        "towns": len({(h["state"], h["town"]) for h in hits}),
        "upcoming": sum(1 for h in hits if ctx.is_upcoming(h)),
    }


# ---------------------------------------------------------------- forms shared by pages

def town_options(ctx):
    """<datalist> of every town, each option carrying its page path for the town box."""
    multi = len(ctx.states) > 1
    opts = "".join(f'<option value="{e(t["town"])}{", " + t["state"] if multi else ""}" data-href="{town_path(t["state"], t["town"])}"'
                   f' data-up="{len(upcoming_meetings(ctx, t["id"]))}"></option>'
                   for t in ctx.towns)
    return f'<datalist id="town-names">{opts}</datalist>'


def town_box(ctx, label="Type your town", button="Find my town", examples=True):
    eg = ""
    if examples:
        picks = [t for t in ("MA:Carver", "MA:Amherst", "NY:Clay") if t in ctx.town_by_id][:3]
        links = [f'<a href="{town_path(*p.split(":", 1))}">{e(p.split(":", 1)[1])}{", " + p[:2] if p[:2] != "MA" else ""}</a>' for p in picks]
        eg = (f'<p class="eg">Or try {", ".join(links[:-1])} or {links[-1]}.</p>' if len(links) > 1
              else (f'<p class="eg">Or try {links[0]}.</p>' if links else ""))
    return f"""<form class="townbox" action="/towns" method="get" role="search" data-town-form>
  <label for="town-q">{label}</label>
  <div class="field-row"><div class="combo"><input id="town-q" name="q" type="text" list="town-names" autocomplete="off" autocapitalize="words" spellcheck="false" required>
  <ul class="suggest" id="town-q-list" role="listbox" aria-label="Matching towns" hidden></ul></div>
  <button class="btn" type="submit">{button}</button></div>
  <p class="field-error" id="town-q-error" role="alert" hidden></p>
  <p class="sr-only" id="town-q-status" aria-live="polite"></p>
  {eg}
</form>
{town_options(ctx)}"""


def upcoming_hits(ctx, keep=lambda h: True):
    return sorted((h for h in ctx.hits if ctx.is_upcoming(h) and keep(h)),
                  key=lambda h: (h["meeting_date"], h["state"] != "MA", h["town"], h.get("board") or ""))


def home_map(ctx):
    m = ctx.maps.get("ma-ri") or next((x for x in ctx.maps.values() if x.ok), None)
    if not m or not m.ok:
        return ""
    return f"""<figure class="home-map">
  <a href="/towns" class="map-link"><picture><source srcset="/maps/{m.group}-dark.svg" media="(prefers-color-scheme: dark)"><img src="/maps/{m.group}.svg" alt="Map of {e(m.name())} towns. Purple dots are towns with something coming up." width="{m.w}" height="{m.h}"></picture></a>
  <figcaption>Purple dots are towns with something coming up. <a href="/towns">All towns</a></figcaption>
</figure>"""


def build_index(ctx):
    states = join_and(STATE_NAMES.get(x, x) for x in ctx.states)
    stories, _ = trending_stories(ctx)
    week_end = (datetime.strptime(ctx.today, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    week = [st for st in stories if st["meeting_date"] and st["meeting_date"] <= week_end][:3]
    big_title = f"{len(week)} to watch this week" if week else "Biggest stories coming up"
    week = sorted(week, key=lambda st: st["meeting_date"]) or stories[:3]  # the biggest three, in the order they happen
    next_html = (f'<ol class="rows">{"".join(story_html(ctx, st) for st in week)}</ol>' if week
                 else '<p class="empty">Nothing big on the agendas posted so far.</p>')
    towns_read = sum(m for _, m, _ in ctx.coverage())
    abbr = join_and(ctx.states)
    ahead = upcoming_hits(ctx)
    ahead_towns = len({(h.get("state"), h.get("town")) for h in ahead})
    ahead_lines = sum(len(m["lines"]) for m in group_meetings(ctx, ahead))  # what /upcoming lists, not raw windows
    see_all = (f"See all {ahead_lines:,} items coming up in {ahead_towns} towns" if ahead else "See everything coming up")
    body = f"""
<div class="wrap narrow home">
<section class="home-hero" aria-labelledby="hero-title">
  <h1 id="hero-title">See what’s coming up at your town meetings</h1>
  <p class="lead">We read <a href="/how-it-works#coverage">{towns_read} towns’</a> agendas in {e(abbr)} every morning and tell you when solar, battery storage, a data center, a zoning change, affordable housing or a cell tower is on one. Free, with no account.</p>
  {site_checked(ctx)}
  {town_box(ctx)}
  {owner_html()}
</section>
<section class="next" aria-labelledby="next-title">
  <h2 id="next-title">{big_title}</h2>
  {next_html}
  <p class="more-link"><a href="/upcoming">{see_all}</a></p>
</section>
<section class="next" aria-labelledby="topics-title">
  <h2 id="topics-title">By topic</h2>
  <ul class="topic-links">{"".join(f'<li><a href="/topics/{tp["slug"]}">{e(tp["name"])}</a></li>' for tp in TOPIC_PAGES)}</ul>
</section>
</div>
"""
    return page(
        ctx,
        f"See what’s coming up at your town meetings | {SITE_NAME}",
        f"Find out when solar, battery storage or data centers are on your town board’s agenda in {join_and(ctx.states)}. "
        "Free, with no account.",
        body, "/", og_title="See what’s coming up at your town meetings",
    )


def build_404(ctx):
    """Our own page for a link that leads nowhere: a meeting page goes when its agenda is replaced or the
    meeting passes, so the page offers the town box and the lists instead of a platform's error."""
    body = f"""
<div class="wrap narrow">
<section class="page-head" aria-labelledby="nf-title">
  <h1 id="nf-title">That page isn’t here</h1>
  <p class="lead">The link may be old: a meeting’s page goes when the meeting has passed or its agenda was replaced. Type your town to see what’s coming up there.</p>
  {town_box(ctx)}
  <ul class="inline-links"><li><a href="/upcoming">Everything coming up</a></li><li><a href="/towns">All towns</a></li><li><a href="/search">Search the agendas</a></li></ul>
</section>
</div>
"""
    return page(ctx, f"Page not found | {SITE_NAME}", "That page isn’t here.", body, "/404", noindex=True)


# why we can't read a town, as a short tag after its name in a list of towns
REASON_TAG = {
    "bot_challenge": "website blocks automatic reading",
    "waf_block": "website blocks automatic reading",
    "robots_disallow_site": "website asks automatic readers to stay away",
    "vendor_blocked": "agenda host blocks automatic reading",
    "vendor_robots_disallow": "agenda host asks automatic readers to stay away",
    "js_only": "agenda page needs a full web browser",
    "no_adapter": "agenda system we can’t open yet",
    "no_agenda_listing_found": "no agenda page found",
    "agendas_stale_or_undated": "agendas posted without dates",
    "crawl_delay_exceeds_cap": "website allows fewer than one visit a day",
}


def county_key(ctx, state, town):
    """"MA:Worcester": a county is named within its state (there is a Bristol County in MA and in RI)."""
    c = (ctx.town_by_id.get(f"{state}:{town}") or {}).get("county") or ""
    return f"{state}:{c}" if c else ""


def county_keys(ctx, meetings):
    """The counties of these meetings, Massachusetts first."""
    keys = {county_key(ctx, m["state"], m["town"]) for m in meetings} - {""}
    return sorted(keys, key=lambda k: (k.split(":")[0] != "MA", k.split(":")[0], k.split(":", 1)[1]))


def county_label(key):
    st, name = key.split(":", 1)
    return f"{name} County" + ("" if st == "MA" else f", {st}")


def cant_read_by_county(ctx):
    """{"MA:Plymouth": "Duxbury, Hanover and Hanson (website blocks automatic reading); Kingston (...)"} for the
    towns we don't read, grouped by the reason."""
    by = defaultdict(lambda: defaultdict(list))
    for t in ctx.towns:
        if t.get("monitored") or not t.get("county"):
            continue
        by[f"{t['state']}:{t['county']}"][REASON_TAG.get(t.get("reason_code") or "", "not worked out yet")].append(t["town"])
    out = {}
    for county, reasons in by.items():
        parts = [f"{join_and(sorted(towns))} ({why})" for why, towns in sorted(reasons.items(), key=lambda kv: -len(kv[1]))]
        out[county] = "; ".join(parts)
    return out


def list_tools_html(counties, cant=None):
    """The row above a meeting list: county and town filters, the view switch, "only my towns" for people with
    alerts on this device, the count, Clear filters, and under a chosen county the towns there we can't read, with
    the reason. app.js (setupMeetingFilter, setupViewSwitch) runs it."""
    by_state = defaultdict(list)
    for c in counties:
        by_state[c.split(":")[0]].append(c)
    if len(by_state) > 1:  # several states: each state's counties under its name
        opts = "".join(f'<optgroup label="{e(STATE_NAMES.get(st, st))}">'
                       + "".join(f'<option value="{e(c)}">{e(c.split(":", 1)[1])}</option>' for c in cs) + "</optgroup>"
                       for st, cs in by_state.items())
    else:  # the box is labelled County, so the names stand alone ("Plymouth", not "Plymouth County")
        opts = "".join(f'<option value="{e(c)}">{e(c.split(":", 1)[1])}</option>' for c in counties)
    county = f'<label>County<select data-key="county"><option value="">All</option>{opts}</select></label>' if len(counties) > 1 else ""
    cant_html = "".join(
        f'<p class="form-note cant-list" data-cant-county="{e(c)}" hidden>We can’t read these {e(county_label(c))} towns yet: {e(v)}. <a href="/how-it-works#gaps">Why</a></p>'
        for c, v in sorted((cant or {}).items()) if c in counties)
    return f"""<div class="filterbar list-tools" data-meeting-filter>
    {county}
    <label>Town<input type="search" data-key="town" placeholder="Type a town" title="Several towns: put commas between them" autocomplete="off"></label>
    {view_switch_html()}
    <p class="count" data-count aria-live="polite"></p>
    <p class="form-note clear-row"><button type="button" class="link-btn" data-clear-filters hidden>Clear filters</button></p>
    <p class="form-note mine-row"><button type="button" class="link-btn" data-my-towns hidden>Only my towns</button></p>
    <p class="form-note cant-list" data-cant-mine hidden></p>
    {cant_html}
  </div>"""


SUBJECT_WORDS = ["solar", "battery storage", "data centers", "moratoriums", "clean-energy permit rules", "zoning changes",
                 "affordable housing", "cell towers", "wetlands permits"]
SUBJECTS = join_and(SUBJECT_WORDS)  # "solar, battery storage, ... and wetlands permits"
SUBJECTS_OR = ", ".join(SUBJECT_WORDS[:-1]) + " or " + SUBJECT_WORDS[-1]


def view_switch_html():
    """"Show: Titles only | With details". The page is built in the titles-only view (body.compact), so a reader
    without JavaScript sees what the pressed button says; app.js (setupViewSwitch) applies a remembered choice."""
    return ('<p class="view-switch" data-view-switch><span class="view-label">Show</span>'
            '<button type="button" class="link-btn" data-view="lines" aria-pressed="true">Titles only</button>'
            '<button type="button" class="link-btn" data-view="full" aria-pressed="false">With details</button></p>')


def week_folds(ctx, meetings):
    """Meetings beyond the next 7 days, one closed fold per week ("Week of Nov 2", its items and meetings), so the
    page is a screen of folds rather than a month-long scroll. app.js (setupMeetingFilter) recounts a fold under a
    filter and opens the ones with something left."""
    weeks = []
    for m in meetings:
        d = datetime.strptime(m["date"][:10], "%Y-%m-%d")
        monday = (d - timedelta(days=d.weekday())).strftime("%Y-%m-%d")
        if weeks and weeks[-1][0] == monday:
            weeks[-1][1].append(m)
        else:
            weeks.append((monday, [m]))
    out = []
    for monday, ms in weeks:
        n_items = sum(len(m["lines"]) for m in ms)
        label = datetime.strptime(monday, "%Y-%m-%d").strftime("%b %-d")
        out.append(f'<details class="week"><summary><span>Week of {label}</span>'
                   f'<span class="sub-count" data-week-count>{plural(n_items, "item")} at {plural(len(ms), "meeting")}</span></summary>'
                   + day_groups(ctx, ms) + "</details>")
    return "".join(out)


def build_upcoming(ctx):
    meetings = group_meetings(ctx, upcoming_hits(ctx))
    week_end = (datetime.strptime(ctx.today, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    soon = [m for m in meetings if m["date"] <= week_end]
    later = [m for m in meetings if m["date"] > week_end]
    counties = county_keys(ctx, meetings)
    n_items = sum(len(m["lines"]) for m in meetings)
    n_towns = len({(m["state"], m["town"]) for m in meetings})
    # The week as text to paste and the whole list as a spreadsheet, as on the topic pages.
    week_text = week_list_text(ctx, soon)
    copy_week = f'<button type="button" class="link-btn" data-copy="{e(week_text)}" hidden>Copy this week’s list</button>' if week_text else ""
    write("upcoming.csv", topic_csv(ctx, meetings))
    tools = f'<p class="action-row">{copy_week}<a href="/upcoming.csv" download>Download the list (CSV)</a></p>' if meetings else ""
    body = f"""
<div class="wrap narrow">
<section class="page-head" aria-labelledby="up-title">
  <h1 id="up-title">Coming up</h1>
  <p class="lead">{plural(n_items, 'item')} at {plural(len(meetings), 'meeting')} in {plural(n_towns, 'town')}: {SUBJECTS} on town agendas.</p>
  {site_checked(ctx)}
  {tabs(COMING_TABS, "/upcoming", "Coming up")}
  {list_tools_html(counties, cant_read_by_county(ctx))}
</section>
<section aria-labelledby="soon-title" data-meet-section>
  <h2 id="soon-title">Next 7 days</h2>
  {meeting_list(ctx, soon, shown=max(len(soon), 1), empty="Nothing in the next 7 days.")}
  {tools}
</section>
<section aria-labelledby="later-title" data-meet-section>
  <h2 id="later-title">Later, by week</h2>
  {week_folds(ctx, later) if later else '<p class="empty">Nothing later yet.</p>'}
</section>
<p class="more-link"><a href="/search?upcoming=1">Search these agendas</a></p>
</div>
"""
    return page(ctx, f"Coming up at town meetings | {SITE_NAME}",
                f"Town board meetings coming up in {join_and(ctx.states)} with solar, battery storage, data centers, zoning, "
                "housing or cell towers on the agenda, each with a link to the agenda.",
                body, "/upcoming")


# ---------------------------------------------------------------- biggest stories (/trending)
# trending.py ranks upcoming stories and writes data/trending.json (contract in ARCHITECTURE.md).
# The page shows the top 20 still ahead; trending.js re-ranks them toward the visitor's own towns.

def trending_stories(ctx):
    doc = load("trending.json", {"stories": []})
    hits_by_id = {h["id"]: h for h in ctx.hits}
    out = []
    seen_story = set()
    for st in doc.get("stories", []):
        d = st.get("meeting_date") or ""
        if d and d < ctx.today:
            continue
        if st.get("action") in ("withdrawn", "cancelled", "mention", "minutes") or \
                re.match(r"(?i)(?:withdrawn|mentions?|canceled|cancelled)\b", st.get("headline") or ""):
            continue  # not a story anyone acts on
        key = (st.get("state"), st.get("town"), d, re.sub(r"\W+", " ", (st.get("headline") or "").lower())[:50])
        if key in seen_story:
            continue
        seen_story.add(key)
        # The row describes the story's own meeting (its date and board), so the lead hit is one from that
        # meeting; the story's headline stands in when none of its hits is from that day.
        hits = [hits_by_id[i] for i in st.get("hit_ids", []) if i in hits_by_id]
        if st.get("hit_ids") and not hits:
            continue  # every item behind the story was dropped (off the subject): no story
        same_day = [h for h in hits if (h.get("meeting_date") or "")[:10] == d[:10]] if d else []
        lead = next((h for h in same_day if board_label(h) == st.get("board")), None) or (same_day[0] if same_day else None)
        board = board_label(lead) if lead else st.get("board", "")
        anchor = "#m-" + slugify(f"{st.get('town', '')}-{board}-{d[:10]}") if d and board else ""
        warrant = st.get("board_key") == "town_meeting"
        item = item_text(lead) if lead else {}
        b = BRIEFS.get(lead["id"]) if lead else None
        if b is None and same_day:
            b = next((BRIEFS[h["id"]] for h in same_day if h["id"] in BRIEFS), None)
        line = (b.get("line") or b.get("what")) if b else (plain_say(item.get("say", "")) or plain_story(st.get("headline", "")))
        href = (st.get("town_path") or town_path(st.get("state", "MA"), st.get("town", ""))) + anchor
        if lead and d and d[:10] >= ctx.today:
            href = f"/m/{slugify(f'{lead['town']}-{board}-{d[:10]}')}"
        out.append({
            "line": line, "board": board,
            "stage": brief_stage(b) if b else item.get("stage", ""),
            "id": st["id"], "score": st.get("score", 0), "headline": plain_story(st.get("headline", "")),
            "dek": plain_story(st.get("dek", "")).replace("The warrant lists ", "The warrant (the list of what voters will decide) lists "),
            "quote": st.get("quote", ""), "reasons": story_chips(st), "topics": st.get("topics", []), "warrant": warrant,
            "towns": st.get("towns", []), "town": st.get("town", ""), "state": st.get("state", ""),
            "href": href,
            "meeting_date": d, "source_url": st.get("source_url", ""),
            # "New on an agenda" only for a project with no earlier meeting in our records
            "new": (not (b and b.get("history")) and not any(w.startswith("Put off") for w in st.get("why", []))
                    and not str(st.get("stage") or "").startswith(("Postponed", "Asks", "Moved"))
                    and any(ctx.is_new(hits_by_id[i]) for i in st.get("hit_ids", []) if i in hits_by_id)),
            "brief": b,
            # why it ranks: at most two signs of what is at stake or how stirred up people are
            "why": [w for w in st.get("why", []) if not w.startswith("First time")][:2],
        })
    return out, doc.get("personalize") or {"in_my_towns": 2.0, "in_neighbor_towns": 1.0, "topic_match": 0.5}


def plain_story(text):
    return re.sub(r"\b(?:a|the) Notice of Intent\b", "a wetlands permit request", text).replace("Notice of Intent", "wetlands permit request")


def story_chips(st):
    """The story's reasons as short chips, without repeating the date shown above them."""
    day = ""
    if st.get("meeting_date"):
        d = datetime.strptime(st["meeting_date"][:10], "%Y-%m-%d")
        day = d.strftime("%b %-d")
    city = f"{st.get('state', 'MA')}:{st.get('town', '')}" in CITIES
    out = []
    for r in st.get("reasons", []):
        m = re.fullmatch(r"(Meeting|Hearing|Vote|Town Meeting) (\w{3} \d{1,2})", r)
        if m and m.group(2) == day:
            r = {"Meeting": "", "Hearing": "Public hearing", "Vote": "Vote", "Town Meeting": "Town Meeting vote"}[m.group(1)]
        if re.fullmatch(r"\d+ (?:town|city) boards", r):
            r = "Several boards are handling this" if not r.startswith("2 ") else "Two boards are handling this"
        also = re.fullmatch(r"Also on the (\w{3} \d{1,2}) agenda", r)
        if also:
            board = next((b.get("board") for b in st.get("boards", []) if b.get("meeting_date")
                          and datetime.strptime(b["meeting_date"][:10], "%Y-%m-%d").strftime("%b %-d") == also.group(1)), "")
            r = f"Also on the {board}’s {also.group(1)} agenda" if board else r
        if r == "Town has an earlier vote on this":
            r = "The city voted on this before" if city else "The town voted on this before"
        if r and r not in out:
            out.append(r)
    return out


def story_reasons(st):
    """The grey line under a story: up to two of its reasons, the neighbors' wave last."""
    chips = [c for c in (st.get("reasons") or []) if c and not c.startswith("Also next door")]
    wave = [c for c in (st.get("reasons") or []) if c.startswith("Also next door")]
    return (chips[:2] if len(chips) >= 2 else chips + wave[:1])[:2]


def story_html(ctx, st, level=3, rank=None):
    """One story as a compact row: its rank (or day), town · board · day, the item's line, and the stage word.
    The row links to the meeting's page, where the detail lives."""
    when = f'<time datetime="{st["meeting_date"]}">{e(day_label(st["meeting_date"], ctx))}</time>' if st["meeting_date"] else "Date not set"
    first = f'<span class="row-rank">{rank}</span>' if rank else f'<span class="row-day" data-slop-ignore>{when}</span>'
    day_meta = f'<span>{when}</span>' if rank else ""
    town = f'{e(st["town"])}{", " + e(st["state"]) if st["state"] != "MA" else ""}'
    # "New" rides the meta line, so every headline starts at the same edge
    new = '<span class="is-new">New on an agenda</span>' if st["new"] else ""
    board = f'<span>{e(st["board"])}</span>' if st.get("board") else ""
    stage = stage_html({"stage": st.get("stage")}, {"date": st.get("meeting_date")}, ctx)
    line = headline(st["line"])
    reasons = story_reasons(st)
    why = f'<span class="row-why">{"".join(f"<span>{e(r)}</span>" for r in reasons)}</span>' if reasons else ""
    return f"""<li class="row" data-id="{e(st['id'])}" data-date="{e(st.get('meeting_date') or '')}" data-topics="{e(' '.join(st.get('topics') or []))}">
  <a href="{e(st['href'])}">{first}<span class="row-when" data-slop-ignore><span class="row-town">{town}</span>{board}{day_meta}{new}</span>
  <span class="row-line">{e(line)}</span>{why}{stage}</a>
</li>"""


def trending_json(stories, weights):
    """site/data/trending.json: the stories still ahead, with only what the page needs."""
    return json.dumps({"personalize": weights, "brief_labels": BRIEF_LABELS,
                       "brief_speak": {"true": BRIEF_SPEAK[True], "false": BRIEF_SPEAK[False]}, "stories": stories},
                      separators=(",", ":"), ensure_ascii=False)


def build_trending(ctx):
    stories, _ = trending_stories(ctx)
    top = stories[:20]
    items = "".join(story_html(ctx, st, level=2, rank=i + 1) for i, st in enumerate(top)) if top else ""
    topic_boxes = "".join(f'<label><input type="checkbox" name="topic" value="{k}"> {e(v)}</label>'
                          for k, v in TOPIC_LABELS.items() if k not in GATED_TOPICS)
    body = f"""
<div class="wrap narrow">
<h1 id="trend-title">Biggest stories coming up</h1>
<p class="lead">Bans, moratoriums and large projects on town agendas, ranked by what’s at stake and how stirred up people are. Add your towns to see only theirs.</p>
<noscript><p class="notice">Adding your towns and the filters need JavaScript. Without it, every story shows, biggest first.</p></noscript>
{site_checked(ctx)}
{tabs(COMING_TABS, "/trending", "Coming up")}
<form class="panel story-towns" id="story-towns" aria-label="Your towns">
  <label for="story-town">Your towns</label>
  <div class="field-row"><input id="story-town" type="text" list="story-town-list" autocomplete="off" autocapitalize="words" spellcheck="false" placeholder="Type a town"><button class="btn" type="submit">Add</button></div>
  <datalist id="story-town-list"></datalist>
  <ul class="chips" id="story-chips" aria-label="Your towns"></ul>
  <label class="check" id="story-near-row" hidden><input type="checkbox" id="story-near" checked> Include the towns next to them</label>
  <p class="field-error" id="story-town-error" role="alert" hidden></p>
</form>
<details class="disclose" id="trend-filter-box"><summary>Filter by date or topic</summary>
<form class="trend-filters" id="trend-filters" aria-label="Narrow the list">
  <fieldset><legend>When</legend>
    <label><input type="radio" name="when" value="week"> This week</label>
    <label><input type="radio" name="when" value="month"> This month</label>
    <label><input type="radio" name="when" value="year" checked> This year</label>
  </fieldset>
  <fieldset><legend>Topics</legend>{topic_boxes}</fieldset>
</form>
</details>
<p class="results-head" id="trend-count" aria-live="polite"></p>
<ol class="rows" id="trend-all">{items}</ol>
<ol class="rows" id="trend-mine" hidden></ol>
{'' if top else '<p class="empty">Nothing big on the agendas posted so far.</p>'}
<p class="more-link"><a href="/upcoming">See everything coming up</a></p>
<details class="disclose"><summary>How we rank them</summary>
<div class="trend-foot">
  <p>Each story gets points for three things.</p>
  <ul class="plain-list">
    <li><b>What’s at stake.</b> What it is (a data center, battery storage, a ban or moratorium, large solar), how big it is (megawatts, acres, homes), whether it covers the whole town, and how final the step is: a vote or hearing counts more than a discussion.</li>
    <li><b>How stirred up people are.</b> How many boards and meetings it has been on, a delay from an earlier meeting, a citizen petition, letters from the public, an appeal or lawsuit, neighboring towns taking up the same subject, and regional news naming the town (headlines from newsrooms such as MassLive, WBUR, the Boston Globe, Syracuse.com and ecoRI News).</li>
    <li><b>How soon.</b> A meeting in the next week counts most.</li>
  </ul>
  <p>The grey line under a story says what lifted it.</p>
</div>
</details>
</div>
"""
    return page(ctx, f"Biggest stories coming up at town meetings | {SITE_NAME}",
                f"Bans, moratoriums and large solar, battery storage and data center projects coming up at town meetings in "
                f"{join_and(ctx.states)}, ranked.",
                body, "/trending", scripts=("/trending.js",), og_title="Biggest stories coming up at town meetings")


# ---------------------------------------------------------------- town pages

def rules_count(tracked, ag_rows):
    ruled = {r.get("decision_date") for r in ag_rows}
    return len([i for i in tracked if not (i.get("key_date") in ruled and "attorney general" in (i.get("status") or "").lower())]) + len(ag_rows)


def rules_html(ctx, tracked, ag_rows, town):
    parts = []
    ruled = {r.get("decision_date") for r in ag_rows}
    tracked = [i for i in tracked if not (i.get("key_date") in ruled and "attorney general" in (i.get("status") or "").lower())]
    for i in sorted(tracked, key=lambda i: i.get("key_date") or "", reverse=True):
        parts.append(f"""<li><p><b>{e(i.get('action', ''))}</b>, {e(i.get('topic', '').lower())}. {e(i.get('status', ''))}, {fmt_date(i.get('key_date'))}.</p>
<p class="small">{e(i.get('summary', ''))}</p>{sources_html(i.get('sources', []))}</li>""")
    for r in sorted(ag_rows, key=lambda r: r.get("decision_date") or "", reverse=True):
        case = f", case {e(str(r['case_number']))}{e(r.get('letter_note', ''))}" if r.get("case_number") else ""
        kind = r.get("record_type")
        who = {"ag_decision": "Attorney General", "court_ruling": "Court ruling", "city_ordinance": "City council",
               "pending_ag_review": "Attorney General review"}.get(kind, "Ruling")
        dated = "letter dated" if kind == "ag_decision" else ("meeting" if (r.get("outcome") or "").startswith("proposed") else "decided")
        letter = (f'<a href="{e(r["letter_url"])}" rel="nofollow noopener" target="_blank">'
                  f'{"Decision letter" if kind == "ag_decision" else "Source"}{case}</a>' if r.get("letter_url") else "")
        parts.append(f"""<li><p><b>{who}: {e((r.get('outcome') or '').lower())}</b> ({dated} {fmt_date(r.get('decision_date'))}). {e(r.get('article', ''))}, {e(r.get('bylaw_type', ''))}.</p>
<p class="small">{e(r.get('summary', ''))} {letter}</p></li>""")
    return f'<ul class="plain rules">{"".join(parts)}</ul>'


def short_day(iso):
    return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%b %-d")


def next_posted(ctx, t):
    """(date, board) of the soonest agenda already posted for a meeting still ahead, if any."""
    ahead = sorted(((d.get("meeting_date") or ctx.doc_dates.get(d.get("url")) or "")[:10], board_label(d))
                   for d in ctx.docs_by_town.get(t["id"], []))
    ahead = [x for x in ahead if x[0] >= ctx.today]
    return ahead[0] if ahead else None


def clerk_phone(t):
    return CLERKS.get(t["id"], "")


def upcoming_meetings(ctx, tid):
    """The town's upcoming meetings with items (cached: town pages also show the towns next door)."""
    cache = ctx.__dict__.setdefault("_upcoming", {})
    if tid not in cache:
        cache[tid] = group_meetings(ctx, sorted((h for h in ctx.hits_by_town.get(tid, []) if ctx.is_upcoming(h)),
                                                key=lambda h: (h.get("meeting_date") or "", h.get("board") or "")))
    return cache[tid]


def plain_say(say):
    """A sentence for a summary: the agenda quote left out (it is one click away)."""
    return re.sub(r":\s*“.*”$", ".", say)


def best_meeting(meetings):
    return min(meetings, key=lambda m: (min((v["rank"] for v in m["lines"].values()), default=99), m["date"]))


def near_ids(ctx, t):
    tid = t["id"]
    listed = ctx.neighbors.get(tid)
    if listed:
        return listed, True
    m = ctx.maps.get(map_group(t["state"]))
    return ([o for o, _ in m.nearby(ctx, tid)] if m and m.ok else []), False


def next_door_html(ctx, t):
    """"Next door: Plymouth (1, Sat Oct 17) · Wareham (0) · Middleborough (can’t read yet)": one line of links."""
    ids, listed = near_ids(ctx, t)
    parts = []
    for other in ids:
        o = ctx.town_by_id.get(other)
        if not o:
            continue
        ups = upcoming_meetings(ctx, other)
        st = f", {o['state']}" if o["state"] != t["state"] else ""
        if ups:
            first = min(ups, key=lambda m: m["date"])
            tops = ordered_topics({tp for en in first["lines"].values() for tp in (en.get("topics") or [])})
            about = join_and([TOPIC_LABELS.get(k, k).lower() for k in tops[:2]])
            note = f"{day_label(first['date'], ctx)}: {about}" if about else f"{plural(len(ups), 'meeting')}, next {day_label(first['date'], ctx)}"
        else:
            why = "" if o["monitored"] else REASON_TAG.get(o.get("reason_code") or "", "")
            note = "Nothing coming up" if o["monitored"] else (f"Can’t read yet ({why})" if why else "Can’t read yet")
        parts.append(f'<li><a href="{town_path(o["state"], o["town"])}">{e(o["town"])}{e(st)}</a> <span>{e(note)}</span></li>')
    if not parts:
        return ""
    return (f'<div class="next-door"><h2 class="next-door-head">{"Next door" if listed else "Nearby"}</h2>'
            f'<ul class="next-door-list">{"".join(parts)}</ul></div>')


def about_agendas_html(ctx, t):
    """One sentence on where the town's agendas come from, behind "About <town>'s agendas"."""
    town = t["town"]
    boards = []
    for listing in t.get("listings") or []:
        name = board_label({"board": listing.get("board"), "board_key": listing.get("board_key")})
        name = first_up(name)
        if name and name not in boards:
            boards.append(name)
    health = (ctx.health or {}).get(t["id"]) or {}
    last = et_when(health["last_success"]) if health.get("last_success") else ""
    ri = "ri_sos" in (t.get("platforms") or [])
    where = "the Rhode Island Secretary of State’s open meetings website" if ri else "its website"
    what = f"{e(town)}’s {e(join_and(boards))} agendas" if boards else f"{e(town)}’s agendas"
    sentence = f"We read {what} from {where}" + (f", most recently {e(last)}." if last else " every morning.")
    website = (f' <a href="{e(t["website"])}" rel="nofollow noopener" target="_blank">{e(town)}’s website</a>.'
               if t.get("website") else "")
    return f"""<details class="disclose"><summary>About {e(town)}’s agendas</summary>
<p>{sentence}{website} <a href="/how-it-works#gaps">Towns we can’t check yet</a>.</p></details>"""


def cant_check_html(ctx, t, up_m):
    """A town we can't read: the plain answer, the towns next door, one button, then the request."""
    tid, town, state = t["id"], t["town"], t["state"]
    reason = reason_text(t.get("reason_code"), town)
    phone = clerk_phone(t)
    host = re.sub(r"^https?://(www\.)?", "", (t.get("website") or "")).rstrip("/")
    site = (f' or check <a href="{e(t["website"])}" rel="nofollow noopener" target="_blank">{e(host)}</a>' if host else "")
    call = for_town(f"Call the {e(town)} Town Clerk", state, town) + (f" at {e(phone)}" if phone else "")
    ids, _ = near_ids(ctx, t)
    n_near = len([x for x in ids if x in ctx.town_by_id])
    filings = meeting_list(ctx, up_m, show_town=False, shown=3, more="More coming up")
    return f"""<section class="cant" aria-labelledby="town-title">
  <p class="lead cant-lead">We can’t read {e(town)}’s agendas yet. {e(for_town(reason, state, town))}. {call}{site}.</p>
  {next_door_html(ctx, t)}
  <p class="actions"><a class="btn" href="{e(alerts_url(tid))}">Follow the {n_near} towns next to {e(town)}</a></p>
  <div class="request" data-request-town="{e(tid)}" data-town-name="{e(town)}, {state}">
    <p>Want {e(town)} added? {for_town("We’ll ask the town hall to let us read its agendas.", state, town)}</p>
    <label class="field">Email, if you want to hear when {e(town)} is added<input type="email" name="request_email" autocomplete="email" spellcheck="false"></label>
    <button type="button" class="btn quiet">Ask us to add {e(town)}</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </div>
  {f'<h2 class="sub-title">Filed with the state</h2>{filings}' if up_m else ""}
</section>"""


STAGE_DATE = re.compile(r"^(Postponed|Asks to postpone) to (Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2})$")
LONG_DATE = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:,\s*(\d{4}))?\b")


def continued_ahead(ctx, meetings, up_m):
    """What earlier agendas say is coming on a day that has no agenda yet: hearings moved to a later day,
    and Town Meeting votes a write-up names with a date. [(day, meeting, item text, note)], soonest first.
    Once that day's agenda is posted the item shows under it and this list drops it."""
    today = date.fromisoformat(ctx.today)
    posted = {(m["board_key"], m["date"]) for m in up_m}
    out, seen = [], set()

    def add(board_key, d, m, text, note):
        key = (board_key, d, quote_key(text)[:40])
        if d < today or (board_key, d.isoformat()) in posted or key in seen:
            return
        seen.add(key)
        out.append((d, m, text, note))

    for m in meetings:
        if not m.get("date"):
            continue
        md = date.fromisoformat(m["date"])
        when = day_label(m["date"], ctx)
        for text, entry in m["lines"].items():
            mt = STAGE_DATE.match(str(entry.get("stage") or ""))
            if mt:
                try:
                    d = datetime.strptime(f"{mt.group(3)} {mt.group(4)} {md.year}", "%b %d %Y").date()
                except ValueError:
                    continue
                if d < md:
                    d = d.replace(year=md.year + 1)
                if mt.group(1) == "Asks to postpone":
                    note = (f"asked to move on {when}" if m["date"] < ctx.today
                            else f"if the board agrees at its {when} meeting")
                else:
                    note = f"moved from {when}"
                add(m["board_key"], d, m, text, note)
            # a write-up that names the Town Meeting day an article goes to
            b = entry.get("brief") or {}
            for sentence in re.split(r"(?<=[.;])\s+", b.get("next") or ""):
                if not re.search(r"town meeting", sentence, re.I):
                    continue
                ld = LONG_DATE.search(sentence)
                if not ld:
                    continue
                # the Town Meeting's own day, not a moratorium's end date in the same sentence ("until October 16, 2027")
                before = sentence[max(0, ld.start() - 14):ld.start()]
                if re.search(r"\b(?:until|through|thru|to|ending|expir\w*|before)\s*$", before, re.I):
                    continue
                if not re.search(r"town meeting", sentence[max(0, ld.start() - 80):ld.end() + 80], re.I):
                    continue
                try:
                    d = datetime.strptime(f"{ld.group(1)} {ld.group(2)} {ld.group(3) or md.year}", "%B %d %Y").date()
                except ValueError:
                    continue
                if not ld.group(3) and d < md:
                    d = d.replace(year=md.year + 1)
                if d > md + timedelta(days=120):
                    continue
                add("town_meeting", d, m, text, f"named on the {when} {meeting_board(m)} agenda; the warrant isn’t posted yet")
    return sorted(out, key=lambda x: x[0])


def continued_status(note):
    """The short status beside an "Also ahead" box: "moved from Tue Oct 13" -> "Moved from Oct 13"."""
    if note.startswith("named on"):
        return "Warrant not posted yet"
    if note.startswith(("asked to move", "if the board agrees")):
        return "Asked to move here"
    m = re.match(r"moved from \w{3} (\w{3} \d{1,2})", note)
    return f"Moved from {m.group(1)}" if m else first_up(note)


def continued_html(ctx, rows):
    if not rows:
        return ""
    items = []
    for d, m, text, note in rows:
        board = "Town Meeting" if note.startswith("named on") else meeting_board(m)
        items.append(f'<li class="row"><a href="{town_path(m["state"], m["town"])}#{m["id"]}">'
                     f'<span class="row-day"><time datetime="{d.isoformat()}">{e(day_label(d.isoformat(), ctx))}</time></span>'
                     f'<span class="row-when"><span>{e(board)}</span></span>'
                     f'<span class="row-line">{e(headline(plain_say(text)))}</span>'
                     f'<span class="{stage_class(continued_status(note))}">{e(continued_status(note))}</span></a></li>')
    return f"""<section class="continued" aria-labelledby="continued-title">
<h2 id="continued-title">Also coming up, dated from earlier agendas</h2>
<p class="form-note">The agenda for that day isn’t posted yet; the date comes from the earlier agenda.</p>
<ol class="rows continued-list">{"".join(items)}</ol>
</section>"""


def news_html(ctx, t):
    """"In the news": up to three regional headlines from the last 45 days naming the town and a siting subject
    (crawler/watch351/sources/news.py), each linking to the newsroom's story."""
    if "_news" not in ctx.__dict__:
        ctx._news = (load("news/matches.json", {}) or {}).get("towns", {})
    since = (datetime.strptime(ctx.today, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    arts, seen = [], set()
    for a in ctx._news.get(t["id"], []):
        if (a.get("published") or "")[:10] >= since and a["title"] not in seen:
            seen.add(a["title"])
            arts.append(a)
    if not arts:
        return ""
    items = "".join(f'<li><a href="{e(a["link"])}" rel="nofollow noopener" target="_blank">{e(a["title"])}</a> '
                    f'<span class="news-src">{e(a["source"])}, {e(short_day(a["published"]))}</span></li>' for a in arts[:3])
    return f'<section class="in-news" aria-labelledby="news-title"><h2 id="news-title">In the news</h2><ul class="news-list">{items}</ul></section>'


def town_summary(ctx, t, up_m, past_m=None):
    """The town page's opening: what is coming up, in one sentence with numbers and the next date, and when we
    last read the town's agendas."""
    if up_m:
        items = sum(len(staying_lines(m)) or len(m["lines"]) for m in up_m)
        topics = Counter(tp for m in up_m for en in m["lines"].values() for tp in ordered_topics(en.get("topics") or [])[:1])
        about = join_and([TOPIC_LABELS.get(k, k).lower() for k, _ in topics.most_common(2)])
        first = next((m for m in up_m if not m.get("cancelled")), up_m[0])
        lead = (f"{plural(items, 'item')} at {plural(len(up_m), 'meeting')} coming up"
                + ((f", mostly {about}" if items > 2 else f", on {about}") if about else "")
                + f". Next: the {meeting_board(first)}, {day_label(first['date'], ctx)}.")
    else:
        nxt = next_posted(ctx, t)
        last = next((m for m in (past_m or []) if real_lines(m)), None)
        recent = ""
        if last:
            text, _ = real_lines(last)[0]
            recent = f" Most recent: {day_label(last['date'], ctx)}, {meeting_board(last)}: {headline(plain_say(text))}."
        lead = (f"Nothing coming up on {SUBJECTS_OR}."
                + recent + (f" The next agenda we know of: {nxt[1]}, {day_label(nxt[0], ctx)}." if nxt else ""))
    health = (ctx.health or {}).get(t["id"]) or {}
    when = et_when(health["last_success"]) if health.get("last_success") else ""
    checked = f'<p class="checked">Checked {e(when)} from the agendas {e(t["town"])} posts online.</p>' if when else ""
    return f'<p class="lead">{e(lead)}</p>{checked}'


def build_town_page(ctx, t):
    tid, state, town = t["id"], t["state"], t["town"]
    hits = ctx.hits_by_town.get(tid, [])
    upcoming, past, undated = split_hits(ctx, hits)
    up_m, past_m, und_m = upcoming_meetings(ctx, tid), group_meetings(ctx, past), group_meetings(ctx, undated)
    tracked = ctx.tracker_by_town.get(tid, [])
    ag_rows = ctx.ag_by_town.get(tid, []) if state == "MA" else []
    thin = not (hits or tracked or ag_rows)
    state_name = STATE_NAMES.get(state, state)

    rail = ""
    if t["monitored"]:
        if up_m:
            first = next((m for m in up_m if not m.get("cancelled")), up_m[0])
            next_line = ""  # the list below prints the day once and the time beside each meeting
            listing = meeting_list(ctx, up_m, show_town=False, shown=3, more="More coming up")
        else:
            nxt = next_posted(ctx, t)
            next_line = ("Nothing on our topics in the agendas posted for upcoming meetings."
                         + (" A Town Meeting warrant with no date we could read is listed below." if und_m else "")
                         + (f" Next agenda posted: {e(nxt[1])}, {day_label(nxt[0], ctx)}." if nxt else ""))
            # The page still shows what the town did most recently, rather than an empty screen.
            listing = (f'<h2>Most recent</h2>{meeting_list(ctx, past_m[:2], show_town=False, shown=2)}' if past_m else "")
        coming = f"""<p class="actions"><a class="btn" href="{e(alerts_url(tid))}">Follow {e(town)}’s meetings</a></p>
<h2 class="sr-only">Coming up</h2>
{view_switch_html() if up_m else ''}
{listing}
{continued_html(ctx, continued_ahead(ctx, up_m + past_m, up_m))}
{news_html(ctx, t)}"""
        rail = f'<aside class="rail" aria-label="Nearby and about">{next_door_html(ctx, t)}{about_agendas_html(ctx, t)}</aside>'
    else:
        coming = cant_check_html(ctx, t, up_m)

    more = []
    earlier = past_m if (up_m or not t["monitored"]) else past_m[2:]  # the two shown above aren't repeated
    if earlier:
        more.append(f"""<details class="disclose"><summary>Earlier meetings ({len(earlier)})</summary>
{meeting_list(ctx, earlier, show_town=False, shown=5, more="Show older")}</details>""")
    if und_m:
        more.append(f"""<details class="disclose" id="warrants"><summary>Town Meeting warrants with no date we could read ({len(und_m)})</summary>
{meeting_list(ctx, und_m, show_town=False, shown=5)}</details>""")
    if tracked or ag_rows:
        more.append(f"""<details class="disclose"><summary>Bylaw rulings and town actions ({rules_count(tracked, ag_rows)})</summary>
{rules_html(ctx, tracked, ag_rows, town)}<p class="small"><a href="/attorney-general">Massachusetts Attorney General rulings</a></p></details>""")
    report = ""  # the page-end strip carries "Report a problem with this page"

    head_lines = town_summary(ctx, t, up_m, past_m) if t["monitored"] else ""
    body = f"""
<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/towns">Towns</a></li><li><a href="/towns#{state.lower()}">{e(state_name)}</a></li><li><span aria-current="page">{e(town)}</span></li></ol></nav>
<div class="page-grid with-head">
<div class="grid-head">
<h1 id="town-title">{e(town)}, {e(state)}</h1>
{head_lines}
</div>
<div class="page-main">
{coming}
<div class="disclosures">{''.join(more)}</div>
{report}
</div>
{rail}
</div>
</div>
"""
    title = f"{town}, {state} town agendas: solar and battery storage | {SITE_NAME}"
    if len(title) > 70:
        title = f"{town}, {state}: solar and battery storage on agendas | {SITE_NAME}"
    if len(title) > 70:
        title = f"{town}, {state}: solar and battery storage | {SITE_NAME}"
    if up_m:
        first = best_meeting(up_m)
        desc = f"{town}, {state}, {meeting_board(first)}, {when_text(ctx, first)}: {plain_say(next(iter(first['lines'])))}"
        if len(desc) < 90:
            desc += " See what else is coming up, with a link to each agenda."
        if len(desc) > 165:
            desc = desc[:160].rsplit(" ", 1)[0] + "…"
        og_title = f"{town}: {plural(len(up_m), 'meeting')} coming up"
    elif t["monitored"]:
        desc = (f"What {town}, {state_name} boards have coming up on solar, battery storage, data centers and zoning, "
                "with a link to each agenda.")
        og_title = f"{town}: town meetings coming up"
    else:
        desc = f"{town}, {state_name}: we can't read its agendas yet. How to find out what's coming up, and alerts for the towns next door."
        og_title = f"{town}: town meetings"
    return page(ctx, title, desc, body, town_path(state, town), noindex=thin, og_title=og_title), thin


def town_item_html(ctx, t):
    """One town in the directory: a link, a count badge when meetings are coming up, greyed when we can't read it."""
    n_up = len(upcoming_meetings(ctx, t["id"]))
    county = f"{t['county']} County" if t.get("county") else ""  # so "Worcester County" finds every town in it
    search = f"{t['town']} {county} {STATE_NAMES.get(t['state'], t['state'])} {t['state']}".lower()
    status = "up" if n_up else ("monitored" if t["monitored"] else "not")
    note_html = f' <span class="n">{plural(n_up, "meeting")}</span>' if n_up else ""
    why = REASON_SHORT.get(t.get("reason_code") or "")
    title = "" if t["monitored"] else f' title="We can’t read this town’s agendas yet{": " + why if why else ""}"'
    return (f'<li data-search="{e(search)}" data-status="{status}">'
            f'<a href="{town_path(t["state"], t["town"])}"{title}>{e(t["town"])}</a>{note_html}</li>')


def build_towns_index(ctx):
    """Search first; underneath, a browse list folded by state and county so the page is a few lines
    long until someone opens a group or types a name (typing opens every group with a match)."""
    sections = []
    for state in ctx.states:
        towns = [t for t in ctx.towns if t["state"] == state]
        if not towns:
            continue
        by_county = {}
        for t in towns:
            by_county.setdefault(t.get("county") or "", []).append(t)
        groups = []
        for county in sorted(by_county, key=lambda c: (c == "", c)):
            items = "".join(town_item_html(ctx, t) for t in by_county[county])
            if len(by_county) == 1:
                groups.append(f'<ul class="town-cols" data-filter-list>{items}</ul>')
            else:
                label = f"{county} County" if county else "Other towns"
                unread = sum(1 for t in by_county[county] if not t["monitored"])
                count = f"{plural(len(by_county[county]), 'town')}" + (f", {unread} we can’t read yet" if unread else "")
                groups.append(f'<details class="county"><summary>{e(label)} <span class="sub-count">{count}</span></summary>'
                              f'<ul class="town-cols" data-filter-list>{items}</ul></details>')
        mon = sum(1 for t in towns if t["monitored"])
        sections.append(f"""<details class="state-towns" id="{state.lower()}">
  <summary>{e(STATE_NAMES.get(state, state))} <span class="sub-count">{len(towns)} towns, {mon} checked every morning</span></summary>
  <div class="counties">{''.join(groups)}</div>
</details>""")
    body = f"""
<div class="wrap narrow towns">
<section class="page-head" aria-labelledby="towns-title">
  <h1 id="towns-title">Find your town</h1>
  <p class="lead">Pick your town to see what its boards have coming up.</p>
  {site_checked(ctx)}
  <noscript><p class="notice">The town box needs JavaScript. Every town is listed below, by state and county.</p></noscript>
  <form class="filterbar" data-list-filter role="search" action="/towns" method="get">
    <label>Town or county<input type="search" name="q" data-search autocomplete="off" autocapitalize="words" spellcheck="false"></label>
    <p class="count" data-count aria-live="polite"></p>
  </form>
  <p class="empty" data-empty hidden>No towns match. Check the spelling, or search by county.</p>
</section>
{''.join(sections)}
</div>
"""
    return page(ctx, f"Find your town in {join_and(ctx.states)} | {SITE_NAME}",
                f"Find your town in {join_and(ctx.states)} and see what its boards have coming up on solar, battery storage, "
                "data centers and zoning.",
                body, "/towns")


# ---------------------------------------------------------------- topics

def build_topic_page(ctx, tp):
    c = topic_counts(ctx, tp["key"])
    hits = c["hits"]
    upcoming, past, undated = split_hits(ctx, hits)
    by_town = defaultdict(list)
    for h in hits:
        by_town[(h["state"], h["town"])].append(h)
    ranked = sorted(by_town.items(), key=lambda kv: (-sum(1 for h in kv[1] if ctx.is_upcoming(h)), -len(kv[1]), kv[0][1]))
    town_rows = "".join(
        f"""<tr><th scope="row">{ctx.town_link(s, town)}{", " + s if s != "MA" else ""}</th>
<td class="num" data-label="Coming up">{sum(1 for h in hs if ctx.is_upcoming(h))}</td><td class="num" data-label="In all">{len(hs)}</td></tr>"""
        for (s, town), hs in ranked[:25])
    ag_rows = [r for r in ctx.ag if tp["ag"](r)]

    more = [f"""<details class="disclose"><summary>Towns where this comes up most</summary>
<div class="table-wrap"><table class="stack counts"><thead><tr><th scope="col">Town</th><th scope="col" class="num">Coming up</th><th scope="col" class="num">In all</th></tr></thead><tbody>{town_rows}</tbody></table></div></details>"""] if town_rows else []
    if past:
        g = group_meetings(ctx, past)[:60]
        more.append(f"""<details class="disclose"><summary>Earlier meetings ({len(g)})</summary>{meeting_list(ctx, g, shown=5, more="Show older")}</details>""")
    if undated:
        g = group_meetings(ctx, undated)[:40]
        more.append(f"""<details class="disclose"><summary>Town Meeting warrants with no date we could read ({len(g)})</summary>{meeting_list(ctx, g, shown=5)}</details>""")
    if tp["slug"] == "data-centers":
        more.append(f"""<details class="disclose"><summary>Can a town pause data centers?</summary>
<p>Yes, in Massachusetts. State law protects solar and battery storage, not data centers.</p>
<p>The Attorney General approved data-center moratoriums in {ag_letter_links(ctx, ("Shutesbury", "Templeton", "Gill"), "data center")}.</p>
{'<p><a href="/attorney-general/data-centers">Every data-center moratorium and ban, town by town</a>, with the dates each was proposed, adopted, approved and took effect.</p>' if ledger_rows(ctx) else ''}
<p><a href="/attorney-general">All Massachusetts Attorney General rulings</a></p></details>""")
    elif ag_rows:
        out = Counter(r.get("outcome") for r in ag_rows if r.get("record_type") == "ag_decision")
        n = sum(out.values())
        more.append(f"""<details class="disclose"><summary>State rulings on these bylaws ({n})</summary>
<p>{"; ".join(f"{v} {k}" for k, v in out.most_common())}.</p><p><a href="/attorney-general">All Massachusetts Attorney General rulings</a></p></details>""")
    more.append(f'<p class="more-link"><a href="/search?topic={tp["key"]}&amp;upcoming=1">Search these agendas</a></p>')
    others = "".join(f'<li><a href="/topics/{o["slug"]}">{e(o["name"])}</a></li>' for o in TOPIC_PAGES if o is not tp)

    # Everything in the next 7 days is in view (a Thursday hearing shouldn't hide behind "More coming up");
    # the same week is one tap to copy as text, and the whole list downloads as a spreadsheet.
    up_m = group_meetings(ctx, upcoming)
    week_end = (datetime.strptime(ctx.today, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    week = [m for m in up_m if m["date"] <= week_end]
    week_text = week_list_text(ctx, week)
    copy_week = (f'<button type="button" class="link-btn" data-copy="{e(week_text)}" hidden>Copy this week’s list</button>' if week else "")
    write(f"topics/{tp['slug']}.csv", topic_csv(ctx, up_m))
    tools = f"""<p class="action-row">{copy_week}<a href="/topics/{tp['slug']}.csv" download>Download the list (CSV)</a></p>""" if up_m else ""
    counties = county_keys(ctx, up_m)
    county_filter = list_tools_html(counties, cant_read_by_county(ctx)) if up_m else ""
    ledger_note = ""
    if tp["slug"] == "data-centers" and ledger_rows(ctx):
        n_rows = ledger_rows(ctx)
        ledger_note = (f'<p class="lead">Every data-center moratorium and ban, town by town, with the dates each was proposed, adopted, '
                       f'approved and took effect: <a href="/attorney-general/data-centers">the ledger</a> ({len(n_rows)} measures, with a CSV).</p>')
    read, total = (sum(m for _, m, _ in ctx.coverage()), sum(n for _, _, n in ctx.coverage()))
    coverage = (f'<p class="checked">From the agendas of {read} of {total} towns in {e(join_and(STATE_NAMES.get(x, x) for x in ctx.states))}. '
                f'<a href="/how-it-works#coverage">Towns we can’t read yet</a>.</p>')

    body = f"""
<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/topics">Topics</a></li><li><span aria-current="page">{e(tp['name'])}</span></li></ol></nav>
<h1 id="topic-title">{e(tp['name'])} on town agendas</h1>
<p class="lead">{topic_summary(ctx, up_m)}</p>
{site_checked(ctx)}
{ledger_note}
<section aria-labelledby="upcoming-title">
  <h2 id="upcoming-title">Coming up</h2>
  {county_filter}
  {meeting_list(ctx, up_m, shown=max(1, sum(1 for m in up_m if m["date"] <= (datetime.strptime(ctx.today, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d"))), more="Show meetings more than 30 days out", empty='Nothing on the agenda about this right now. We check every morning.')}
  {tools}
  {coverage}
</section>
<div class="disclosures">{''.join(more)}</div>
<nav class="others" aria-label="Other topics"><p class="small">Other topics:</p><ul class="inline-links">{others}</ul></nav>
</div>
"""
    title = f"{tp['name']} on town agendas in {join_and(ctx.states)} | {SITE_NAME}"
    return page(ctx, title if len(title) <= 70 else f"{tp['name']} on town agendas | {SITE_NAME}",
                f"{tp['name']} on town agendas in {c['towns']} towns, with the board, the date and a link to every agenda.",
                body, f"/topics/{tp['slug']}")


def topic_summary(ctx, up_m):
    """"12 items at 9 meetings coming up in 8 towns. Next: the Easthampton Conservation Commission, Mon Oct 19." """
    if not up_m:
        return "Nothing on town agendas about this right now. We check every morning."
    n_items = sum(len(m["lines"]) for m in up_m)
    n_towns = len({(m["state"], m["town"]) for m in up_m})
    dated = [m for m in up_m if m.get("date")]
    nxt = ""
    if dated:
        first = min(dated, key=lambda m: (m["date"], time_key(m)))
        day = datetime.strptime(first["date"][:10], "%Y-%m-%d").strftime("%a %b %-d")
        nxt = f" Next: the {e(first['town'])} {e(first['board'])}, {day}."
    return f"{plural(n_items, 'item')} at {plural(len(up_m), 'meeting')} coming up in {plural(n_towns, 'town')}.{nxt}"


def moratorium_word(b):
    """A headline says "ban" where the agenda says moratorium: a pause is not a ban, so it says moratorium."""
    src = f"{b.get('quote') or ''} {b.get('what') or ''}"
    line = b.get("line") or ""
    if (re.search(r"\bmoratori", src, re.I) and not re.search(r"\b(?:ban|prohibit\w*)\b", b.get("quote") or "", re.I)
            and re.search(r"\bban\b", line, re.I)):
        line = re.sub(r"\b(?:temporary )?ban\b", "moratorium", line, flags=re.I)
        line = re.sub(r"\bban\b", "moratorium", line, flags=re.I)
        b = {**b, "line": line[:1].upper() + line[1:]}
    return b


OFF_ITEM = re.compile(r"\(not an? [a-z0-9 -]+ item\)|\(attachment text\b|^(?:Existing|Standing notice)\b[^(]*\(not a project\)", re.I)
TM_TITLE = re.compile(r"\btown meeting\b[^|]{0,60}\bwarrant\b|\bwarrant\b[^|]{0,60}\btown meeting\b", re.I)  # a writer's note that the flagged words were incidental


def carried_over(entry):
    """An item continued, postponed or moved from an earlier meeting, or with a history in its write-up:
    not "New on an agenda", whatever day we first read this agenda."""
    b = entry.get("brief") or {}
    if b.get("history"):
        return True
    if str(entry.get("stage") or "").startswith(("Postponed", "Asks to postpone", "Moved", "Asked to move")):
        return True
    if ((ANALYSIS.get(entry.get("hit") or "") or {}).get("flags") or {}).get("continued"):
        return True  # "Continued Discussion – Data Centers": the reading found the continuation
    text = " ".join([str(entry.get("say") or ""), str(entry.get("quote") or "")] + [str(q) for q in (entry.get("quotes") or [])])
    return bool(CONTINUED.search(text))


def staying_lines(m):
    """real_lines without the items the agenda itself moves to a later meeting: they count on their new day."""
    return [(t, en) for t, en in real_lines(m) if not str(en.get("stage") or "").startswith(("Postponed", "Asks to postpone", "Moved"))]


def real_lines(m):
    """A meeting's items that say something (not a bare mention of a word, not an item a writer marked as
    off the subject), best first."""
    return [(t, en) for t, en in m["lines"].items() if en.get("kind") != "mention" and not OFF_ITEM.search(t)]


def week_list_text(ctx, meetings):
    """The week as text to paste: one line per meeting, grouped by state, mention-only meetings left out."""
    blocks = []
    for st in sorted({m["state"] for m in meetings}, key=lambda x: (x != "MA", x)):
        rows = []
        for m in meetings:
            if m["state"] != st or m.get("cancelled"):
                continue
            lines = real_lines(m)
            if not lines:
                continue
            rows.append(share_text(ctx, m, lines[0][0], lines[0][1]) + f" {meeting_share_url(ctx, m)}")
        if rows:
            blocks.append(f"{STATE_NAMES.get(st, st)}\n" + "\n".join(rows))
    return "\n\n".join(blocks)


def topic_csv(ctx, meetings):
    """One row per agenda item at a meeting still ahead: town, state, board, date, time, place, item, status,
    the agenda's URL and the meeting's page."""
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["town", "county", "state", "board", "date", "time", "place", "item", "status", "agenda_url", "page_url"])
    for m in meetings:
        doc = m["docs"][0]["url"] if m["docs"] else ""
        place = place_text(m["place"]) if m["place"] and m["source"] != "massdep_wetlands" else ""
        county = (ctx.town_by_id.get(f"{m['state']}:{m['town']}") or {}).get("county") or ""
        for text, entry in real_lines(m):
            w.writerow([m["town"], county, m["state"], meeting_board(m), m["date"] or "", m.get("time") or "", place,
                        plain_say(text), "Canceled" if m.get("cancelled") else (entry.get("stage") or ""), doc, meeting_share_url(ctx, m)])
    return out.getvalue()



def build_topics_index(ctx):
    rows = []
    first = min((h.get("first_seen") or "" for h in ctx.hits if h.get("first_seen")), default="")
    since = f"since {fmt_date(first[:10])}" if first else "since we started reading"
    keys = [tp["key"] for tp in TOPIC_PAGES] + [k for k in TOPIC_LABELS if k not in TOPIC_PAGE_BY_KEY]
    for k in keys:
        c = topic_counts(ctx, k)
        if not c["items"] and k not in TOPIC_PAGE_BY_KEY:
            continue
        tp = TOPIC_PAGE_BY_KEY.get(k)
        name = (f'<a href="/topics/{tp["slug"]}">{e(tp["name"])}</a>' if tp
                else f'<a href="/search?topic={e(k)}&amp;upcoming=1">{e(TOPIC_LABELS[k])}</a>')
        # Meetings, not items, so the number matches what the topic page lists.
        up_meetings = len(group_meetings(ctx, [h for h in c["hits"] if ctx.is_upcoming(h)]))
        rows.append(f"""<li><h2>{name}</h2><p class="topic-next">{plural(up_meetings, 'meeting')} coming up</p>
<p class="small">{plural(c['items'], 'item')} in {plural(c['towns'], 'town')} {since}</p></li>""")
    body = f"""
<div class="wrap narrow">
<section class="page-head" aria-labelledby="topics-title">
  <h1 id="topics-title">Topics</h1>
  <p class="lead">The {len(rows)} subjects we look for on every agenda, and how many meetings coming up touch each one.
  A meeting with two of them on its agenda counts under both.</p>
  {site_checked(ctx)}
</section>
<ul class="topic-boxes">{''.join(rows)}</ul>
<p class="more-link"><a href="/upcoming">Everything coming up, by date</a></p>
</div>
"""
    return page(ctx, f"Topics: solar, battery storage, data centers | {SITE_NAME}",
                "What town agendas say about solar, battery storage, data centers, moratoriums, clean-energy permit rules, "
                "zoning changes, affordable housing and cell towers.",
                body, "/topics")


# ---------------------------------------------------------------- search

def build_search(ctx):
    states = "".join(f'<option value="{s}">{e(STATE_NAMES.get(s, s))}</option>' for s in ctx.states)
    live = {t for h in ctx.hits for t in h.get("topics", [])}
    topics = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in TOPIC_LABELS.items() if k in live or k not in GATED_TOPICS)
    boards = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in BOARD_NAMES.items())
    multi = len(ctx.states) > 1
    towns = "".join(f'<option value="{e(t["town"])}{", " + t["state"] if multi else ""}" data-id="{e(t["id"])}"></option>' for t in ctx.towns)
    body = f"""
<div class="wrap narrow">
<h1 id="search-title">Search agendas</h1>
<p class="lead">The full text of every flagged item on {sum(m for _, m, _ in ctx.coverage())} towns’ agendas, past meetings and coming up.</p>
{site_checked(ctx)}
<form id="search-form" class="searchform" action="/search" method="get" role="search" data-towns="{sum(m for _, m, _ in ctx.coverage())}">
  <label for="search-q">Search for</label>
  <div class="field-row">
    <input name="q" id="search-q" type="search" autocomplete="off" placeholder="data center moratorium">
    <button class="btn" type="submit">Search</button>
  </div>
  <details class="filters" id="search-filters"><summary>Filters</summary>
  <div class="search-sort">
    <label>Sort<select name="sort"><option value="date">Newest meeting first</option><option value="">Best match</option></select></label>
    <label class="check"><input type="checkbox" name="upcoming" value="1" checked> Meetings still ahead first</label>
    <label class="check"><input type="checkbox" name="flagged" value="1"> Only meetings with a flagged item</label>
    <label class="check"><input type="checkbox" name="week" value="1"> Only the next 7 days</label>
  </div>
  <div class="search-filters">
    <label>State<select name="state"><option value="">All states</option>{states}</select></label>
    <label>Topic<select name="topic"><option value="">All topics</option>{topics}</select></label>
    <label>Board<select name="board"><option value="">All boards</option>{boards}</select></label>
    <div class="town-pick" id="town-pick">
      <label for="town-add">Towns</label>
      <div class="field-row"><input id="town-add" type="text" list="search-towns" autocomplete="off" autocapitalize="words" spellcheck="false" placeholder="All towns">
      <button type="button" class="btn quiet" id="town-add-btn">Add</button></div>
      <datalist id="search-towns">{towns}</datalist>
      <ul class="chips" id="town-chips" aria-label="Towns to search"></ul>
      <p class="form-note"><button type="button" class="link-btn" id="my-towns-btn" hidden>Search my towns</button></p>
      <p class="field-error" id="town-add-error" role="alert" hidden></p>
    </div>
  </div>
  </details>
</form>
<p id="search-status" aria-live="polite"></p>
<p class="form-note search-examples">Try <a href="/search?q=battery+storage&amp;upcoming=1">battery storage</a>, <a href="/search?q=data+center+moratorium">data center moratorium</a>, <a href="/search?q=cell+tower&amp;upcoming=1">cell tower</a> or <a href="/search?q=40B&amp;upcoming=1">40B</a>.</p>
<p class="notice" id="search-exact" hidden></p>
<ol id="search-results"></ol>
<noscript><p class="notice">Search needs JavaScript. You can still <a href="/towns">find a town</a>.</p></noscript>
</div>
"""
    return page(ctx, f"Search town agendas | {SITE_NAME}",
                f"Search the full text of town board agendas in {ctx.region()}. Filter by state, town, topic and board.",
                body, "/search", scripts=("/search.js",))


# ---------------------------------------------------------------- alerts (/watch) and the alert list view (/w)

def build_watch(ctx, groups=False):
    """Alert setup. /watch is for residents: a town, the towns next door, subjects, an email address.
    /alerts-for-groups adds chat webhooks, a name and per-town choices, for businesses and groups."""
    topic_count = Counter(t for h in ctx.hits for t in h.get("topics", []))
    topics = [k for k in TOPIC_LABELS if topic_count.get(k) or k not in GATED_TOPICS | {"wetlands_filing"}]
    topics += sorted(k for k in topic_count if k not in TOPIC_LABELS)
    preset = tuple(topics)  # every subject, unless the person narrows them: following for 40B or cell towers must not come up empty
    topic_boxes = "".join(
        f'<li><label class="check"><input type="checkbox" name="topics" value="{e(k)}"{" checked" if k in preset else ""}>'
        f'<span>{e(TOPIC_LABELS.get(k, k))}</span></label></li>'
        for k in topics)
    near_more = """<details class="disclose" id="near-details"><summary>Choose which towns</summary>
        <ul class="check-cols" id="near-list"></ul>
        <div id="extra-wrap" hidden>
          <p class="form-note">Also in these alerts:</p>
          <ul class="check-cols" id="extra-list"></ul>
        </div>
      </details>"""
    hook = """
    <fieldset class="group-box" id="hook-details">
      <legend>Post to Slack, Teams or Discord <small>(optional)</small></legend>
      <label class="field">Webhook URL<input name="webhook_url" id="webhook-url" type="url" inputmode="url" autocomplete="off" spellcheck="false" placeholder="https://hooks.slack.com/services/…" aria-describedby="webhook-help"></label>
      <p class="form-note" id="webhook-help">Your chat app gives you this link when you add an incoming webhook. For Teams, use a Workflows webhook. Before saving, we send one test message to check the link. After that we post once a day, only when something new is posted.</p>
      <label class="check" id="webhook-remove-row" hidden><input type="checkbox" id="webhook-remove"> Stop posting and remove the saved webhook</label>
      <label class="field">Message format
        <select name="webhook_format"><option value="auto">Made for your chat app</option><option value="json">Plain JSON, for your own tools</option></select>
      </label>
      <div class="actions"><button type="button" class="btn quiet" id="send-test">Send a test message</button></div>
      <p class="form-status" id="test-status" role="status" aria-live="polite"></p>
      <p class="field-error" id="webhook_url-error" hidden></p>
    </fieldset>
    <label class="field" id="name-details">Name for these alerts <small>(optional)</small><input name="name" maxlength="80" autocomplete="off" placeholder="Carver and neighbors"></label>""" if groups else ""
    if groups:
        title, lead = "Post to Slack, Teams or Discord", (
            "New agendas on your topics, posted to your team’s chat, at most once a day. Free for one town and the towns "
            "next to it.")
        more = '<p class="form-note">Watching many towns? <a href="/contact">Tell us what you need</a>.</p>'
        switch = ""
    else:
        title, lead, more = "Follow a town", "Free for your town and the towns next to it. No account needed.", ""
        switch = 'Want them in Slack, Teams or Discord? <a href="/alerts-for-groups">Post to a chat app</a>.'

    body = f"""
<div class="wrap narrow watch">
<p class="notice" id="edit-banner" hidden>Editing <b id="edit-name">your alerts</b>. <a href="{'/alerts-for-groups' if groups else '/watch'}">Set up new alerts instead</a></p>
<p class="notice err" id="watch-error" role="alert" hidden></p>
<h1 id="watch-title" tabindex="-1" data-start="{e(title)}">{e(title)}</h1>
{f'<p class="lead">{e(lead)}</p>' if lead else ""}
{site_checked(ctx)}
{more}
<noscript><p class="notice">Following a town needs JavaScript. You can still <a href="/towns">find your town</a> and read what’s coming up there.</p></noscript>
<form id="watch-form" class="watch-form" data-mode="{'groups' if groups else 'residents'}" novalidate>
  <div class="step" id="step-town">
    <label for="home-town" class="big-q">Which town?</label>
    <p class="form-note" id="town-help">You get a private page that updates every morning and a calendar feed for it and the towns next to it.</p>
    <div class="combo" data-town-box="pick">
      <input id="home-town" class="big-input" type="text" list="town-names" autocomplete="off" autocapitalize="words" spellcheck="false" aria-describedby="town-help home-read towns-error">
      <ul class="suggest" id="home-town-list" role="listbox" aria-label="Matching towns" hidden></ul>
    </div>
    <datalist id="town-names"></datalist>
    <p class="form-note" id="home-read" aria-live="polite">Pick it from the list as you type.</p>
    <div class="request" id="home-request" hidden>
      <p id="home-request-text"></p>
      <button type="button" class="btn quiet" id="home-request-btn">Ask us to add this town</button>
      <p class="form-status" id="home-request-status" role="status" aria-live="polite"></p>
    </div>
    <p class="field-error" id="towns-error" hidden></p>
    <div class="actions"><button type="button" class="btn" id="town-next">Continue</button></div>
    {f'<p class="form-note">{switch}</p>' if switch else ""}
  </div>

  <div class="step" id="step-send" hidden>
    <p class="back"><button type="button" class="link-btn" id="change-town">Change town</button></p>
    <div class="preview" id="preview" aria-live="polite"></div>
    <div id="email-option" hidden>
      <label class="field big-label">Your email address{' <small>(optional)</small>' if groups else ''}<input name="email" id="email" type="email" inputmode="email" autocomplete="email" spellcheck="false" aria-describedby="email-help"></label>
      <p class="form-note" id="email-help">At most one email a day, only when something new is posted. We email you a link to confirm the address first, and never sell or share it.</p>
      <label class="check" id="email-remove-row" hidden><input type="checkbox" id="email-remove"> Stop emails and remove the address</label>
      <p class="field-error" id="email-error" hidden></p>
    </div>
    <p class="form-note" id="no-email" hidden>The next page has your calendar feed and a private page for these towns.</p>
    {hook}
    <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <fieldset class="near" id="near-step">
      <legend class="sr-only">Towns</legend>
      <label class="check big" id="near-all-row"><input type="checkbox" id="near-all" checked> <span id="near-all-text">Also the towns next to <span id="home-name">your town</span></span></label>
      <p class="field-error" id="near-error" hidden></p>
      <p class="form-note" id="near-note" hidden></p>
      <p class="form-note cant-note" id="cant-note" hidden></p>
    </fieldset>
    <p class="topic-line" id="topic-line">Topics: <span id="topic-names">{e(join_and(TOPIC_LABELS.get(k, k)[0].lower() + TOPIC_LABELS.get(k, k)[1:] for k in topics))}</span>. <button type="button" class="link-btn" id="topics-change">Change topics</button></p>
    <details class="disclose" id="other-ways"><summary>Other ways: topics, towns, calendar, RSS</summary>
      <fieldset class="near" id="topics-step">
        <legend class="big-legend">Topics</legend>
        <ul class="check-cols topic-list" id="topics-details">{topic_boxes}</ul>
        <p class="field-error" id="topics-error" hidden></p>
      </fieldset>
      {near_more}
      <p class="form-note">After you save, the next page has a calendar link and an RSS feed for these alerts.</p>
    </details>
    <div class="submit-row">
      <button class="btn" type="submit" id="watch-submit">Send me these</button>
      <p class="form-status" id="watch-status" role="status" aria-live="polite"></p>
    </div>
  </div>
</form>
{owner_html()}

<section id="my-lists" aria-labelledby="my-lists-title" hidden>
  <h2 id="my-lists-title">Alerts you set up on this device</h2>
  <ul class="plain" id="my-lists-items"></ul>
</section>
</div>
"""
    if groups:
        return page(ctx, f"Post town agendas to Slack, Teams or Discord | {SITE_NAME}",
                    "Post new town agendas on solar, battery storage, data centers and zoning to Slack, Teams or "
                    "Discord, at most once a day.",
                    body, "/alerts-for-groups", scripts=("/watch.js",))
    return page(ctx, f"Follow a town | {SITE_NAME}",
                "Follow your town and the towns next to it: a private page and a calendar feed of meetings on solar, "
                "battery storage, data centers and zoning. Free, no account needed.",
                body, "/watch", scripts=("/watch.js",))


def build_viewer(ctx):
    topics = e(json.dumps({k: [v, TOPIC_PHRASES.get(k, (v.lower(), False))[0], TOPIC_PHRASES.get(k, ("", False))[1]]
                           for k, v in TOPIC_LABELS.items()}))
    body = f"""
<div class="wrap narrow" id="wl-app" data-topics="{topics}" data-order="{e(json.dumps(TOPIC_ORDER))}" data-tags="{e(json.dumps(TOPIC_TAGS))}" data-mention="{e(json.dumps(MENTION_NOUN))}" data-base="{BASE_URL}">
<p class="crumbs-plain">Your alerts</p>
<h1 id="wl-title">Loading your alerts…</h1>
<p id="wl-summary"></p>
<div class="notice err" id="wl-error" role="alert" hidden></div>

<div id="wl-created" hidden>
  <p id="created-lead"><span id="created-how"></span><span id="inbox-note" hidden> Check your inbox and click the link to confirm your address.</span></p>
  <p id="sample-lead">Here is what the first one will look like:</p>
  <div id="sample"></div>
  <p class="actions"><a class="btn" id="created-cal" href="#">Add these meetings to my calendar</a></p>
  <p class="keep">To change or stop these alerts later, keep this link.</p>
  <div class="copy-row" id="created-row"></div>
  <p class="more-link"><a id="see-all" href="#">See everything coming up in these towns</a></p>
</div>

<div id="wl-body" hidden>
  <p class="notice ok" id="created-banner" tabindex="-1" hidden></p>
  <p class="notice" id="readonly-banner" hidden>Someone shared these alerts with you. You can see them but not change them.</p>
  <div class="get-buttons">
    <a class="btn" id="webcal-link" href="#">Add to calendar</a>
    <a class="btn quiet" id="rss-link" href="#">RSS feed</a>
  </div>

  <section aria-labelledby="items-title">
    <h2 id="items-title">Coming up</h2>
    <p class="status" id="items-lead"></p>
    <div id="items-upcoming"></div>
    <details class="disclose" id="past-wrap"><summary id="past-summary">Earlier meetings</summary><div id="items-past"></div></details>
    <details class="disclose" id="undated-wrap" hidden><summary>Town Meeting warrants</summary><div id="items-undated"></div></details>
  </section>

  <details class="disclose" id="other-get"><summary>Other ways to get these</summary>
    <div class="feed-rows" id="feed-rows"></div>
    <p class="small"><a id="json-link" href="#">Data feed (JSON), for your own tools</a></p>
  </details>

  <details class="disclose settings" id="settings" hidden><summary>Change or delete these alerts</summary>
    <section id="links-section" aria-labelledby="links-title" hidden>
      <h2 id="links-title">Your links</h2>
      <p class="linkcard-title"><b>Private link</b>: changes or deletes these alerts. Keep it to yourself.</p>
      <div class="copy-row" id="private-row"></div>
      <p class="linkcard-title"><b>Share link</b>: shows these alerts to anyone, without letting them change anything.</p>
      <div class="copy-row" id="share-row"></div>
    </section>
    <section id="hook-section" aria-labelledby="hook-title" hidden>
      <h2 id="hook-title">Where alerts go</h2>
      <p id="email-status" hidden></p>
      <p id="hook-status"></p>
      <div class="actions"><button type="button" class="btn small quiet" id="hook-test" hidden>Send a test message</button></div>
      <p class="form-status" id="hook-test-status" role="status" aria-live="polite"></p>
    </section>
    <section id="manage-section" aria-labelledby="manage-title" hidden>
      <h2 id="manage-title">Change or delete</h2>
      <p id="plan-line"></p>
      <div class="actions">
        <a class="btn quiet" id="edit-link" href="/watch">Change towns, topics or email</a>
        <button type="button" class="btn quiet danger" id="delete-start">Delete alerts</button>
      </div>
      <div class="confirm" id="delete-confirm" hidden>
        <p><b>Delete these alerts?</b> Emails, posts and calendar updates stop, and this page goes away. You can’t undo this.</p>
        <div class="actions"><button type="button" class="btn danger" id="delete-yes">Delete alerts</button><button type="button" class="btn quiet" id="delete-no">Keep them</button></div>
      </div>
      <p class="form-status" id="manage-status" role="status" aria-live="polite"></p>
    </section>
  </details>
</div>
</div>
"""
    return page(ctx, f"Your alerts | {SITE_NAME}", f"Alerts from {SITE_NAME} for towns you follow.",
                body, "/w", scripts=("/w.js",), noindex=True)


# ---------------------------------------------------------------- how it works

def build_how(ctx):
    census, leadtime, ag = ctx.census, ctx.leadtime, ctx.ag
    auto = census.get("automated", {})
    boards = census.get("boards", {})
    first = leadtime.get("summary", {}).get("first_posting_only", {})
    window = leadtime.get("meeting_window", {})
    headline, _, record = moratorium_lines(ag)
    headline += ""
    ag_dates = sorted(r["decision_date"] for r in ag if r.get("record_type") == "ag_decision" and r.get("decision_date"))
    regulating = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") == "zoning regulation"
                  and r.get("outcome") in ("approved", "approved in part", "disapproved")]
    reg_ok = sum(1 for r in regulating if r["outcome"] in ("approved", "approved in part"))
    letters = sum(1 for r in ag if r.get("record_type") == "ag_decision")
    not_auto = census.get("not_automated", {})
    blocked = sorted(not_auto.items(), key=lambda kv: -kv[1]["towns"])
    upcoming = sum(1 for h in ctx.hits if ctx.is_upcoming(h))
    median_ahead = ctx.ahead_median()
    monitored = sum(m for _, m, _ in ctx.coverage())
    coverage_parts = [
        f'<a href="/towns#ma">{m} of the 351 cities and towns</a> in Massachusetts' if s == "MA" and n == 351
        else (f'<a href="/towns#ri">all {n} cities and towns</a> in Rhode Island' if s == "RI" and m == n
              else f'<a href="/towns#{s.lower()}">{m} towns</a> in {STATE_NAMES.get(s, s)}')
        for s, m, n in ctx.coverage()]
    board_rows = "".join(
        f"<tr><th scope='row'>{BOARD_NAMES[k]}</th><td class='num' data-label='Towns'>{v['towns']} of {v['of']}</td></tr>"
        for k, v in boards.items() if k in BOARD_NAMES)
    gap_rows = "".join(
        f"<li>{e(REASON_LABELS.get(k, k))}: {plural(v['towns'], 'town')}"
        f"{', such as ' + e(join_and(v.get('examples', [])[:3])) if v.get('examples') else ''}.</li>"
        for k, v in blocked)
    body = f"""
<div class="wrap narrow prose">
<h1 id="how-title">How it works</h1>
<p class="lead">Towns post their meeting agendas online. Every morning we check the new ones for solar, battery storage, data centers, zoning, affordable housing and cell towers, and write each one up in a plain sentence with a link to the town’s own agenda.</p>
<p>Everything here is for information only, not legal advice. Always check dates with the town clerk.</p>
{owner_html()}

<section aria-labelledby="coverage">
  <h2 id="coverage">Which towns we check</h2>
  <p>{join_and(coverage_parts)[:1].upper() + join_and(coverage_parts)[1:]}.</p>
  <details class="disclose"><summary>Which boards and topics</summary>
    <p>Planning boards, zoning boards of appeals, conservation commissions, select boards and city councils, and Town Meeting warrants, wherever the town posts them online. We also include wetlands permit requests for solar and battery projects filed with the state.</p>
    <p data-slop-ignore>Topics: {" · ".join(f'<a href="/topics/{tp["slug"]}">{e(tp["name"])}</a>' for tp in TOPIC_PAGES)} · <a href="/topics">all topics</a>.</p>
  </details>
</section>

<section aria-labelledby="timing">
  <h2 id="timing">How early you hear</h2>
  <p>Half of agendas go up {first.get('median_days', 0):.0f} or more days before the meeting. Massachusetts law requires at least 48 hours’ notice, not counting weekends and holidays.</p>
  <details class="disclose"><summary>How we know</summary>
    <p>We looked at {first.get('n', 0):,} agendas from {first.get('towns', 0)} towns, for meetings from {fmt_date(window.get('start'))} to {fmt_date(window.get('end'))}, and counted the days from when each was first posted to the meeting.</p>
  </details>
</section>

<section aria-labelledby="gaps">
  <h2 id="gaps">Towns we can’t check yet</h2>
  <p>Some town websites turn away programs like ours, and some don’t post agendas with dates. We don’t get around those limits. We ask the town hall instead, and you can ask us to add a town from its page.</p>
  <details class="disclose"><summary>Why, town by town</summary>
    <ul class="plain gaps">{gap_rows}</ul>
  </details>
</section>

<section aria-labelledby="attorney-general">
  <h2 id="attorney-general">Attorney General rulings</h2>
  <p>In Massachusetts, the Attorney General reviews every town bylaw before it can take effect. {headline} <a href="/attorney-general">Every ruling, with its letter</a>.</p>
</section>

<section aria-labelledby="crawler">
  <h2 id="crawler">How we collect agendas</h2>
  <p>Our program, {BOT_NAME}, visits town websites once a day and reads only public agenda pages. It follows each website’s rules for programs like ours. <a href="/bot">For website managers</a>.</p>
</section>

<section aria-labelledby="free">
  <h2 id="free">What it costs</h2>
  <p>Following a town and the towns next to it is free, with no account. There’s nothing to buy. If we ever charge businesses that watch many towns, we’ll say so here first.</p>
</section>

<section aria-labelledby="more-about">
  <h2 id="more-about">More</h2>
  <ul class="plain-list">
    <li><a href="/privacy">Privacy</a>: what we keep about you and why.</li>
    <li><a href="/contact">Contact</a>: corrections, town records, anything else.</li>
    <li><a href="/bot">For website managers</a>: how our program visits town websites.</li>
  </ul>
</section>
</div>
"""
    return page(ctx, f"How it works | {SITE_NAME}",
                f"How {SITE_NAME} checks town agendas every morning, which towns it includes, how early agendas go up, "
                "and what we keep about you.",
                body, "/how-it-works")


def build_privacy(ctx):
    body = f"""
<div class="wrap narrow prose">
<h1 id="privacy-title">Privacy</h1>
<p class="lead">We don’t use accounts, cookies or tracking. We keep only what your alerts need.</p>
  <h2 id="keep">What we keep</h2>
    <p>For your alerts we keep your towns and subjects, and, if you give them, your email address, a name for the alerts and a chat webhook link.</p>
    <p>Your alerts have two links. The private link can change or delete them. The share link can only show them.</p>
    <p>If you give us an email address, we email only the alerts you asked for: at most once a day, only when something new is posted, and only after you confirm the address.</p>
    <p>Our email provider, Resend, sends the emails. We never sell or share your email. We delete it when you unsubscribe or delete your alerts. Every email has a one-click unsubscribe link.</p>
    <p>This browser remembers the alerts you set up here. Clearing this site’s data removes them.</p>
    <p>Anything you sent through the contact form, we delete on request.</p>
</div>
"""
    return page(ctx, f"Privacy | {SITE_NAME}", "What {SITE_NAME} keeps about you and why: no accounts, cookies or tracking.",
                body, "/privacy")


def build_contact(ctx):
    body = f"""
<div class="wrap narrow prose">
<h1 id="contact-title">Contact</h1>
<p>We read every message. The form doesn’t ask who you are, so add your email address if you’d like an answer.</p>
  <p>Town officials: send us an adopted bylaw’s text or Town Meeting vote results, and we’ll add them to the town’s page.</p>
  <form id="contact-form" class="contact" novalidate>
    <label class="field">What is this about?
      <select name="kind">
        <option value="correction">A correction, a problem on a page, or town records</option>
        <option value="removal">Delete my alerts or my details</option>
        <option value="message">Something else</option>
      </select>
    </label>
    <label class="field">Message<textarea name="message" id="contact-message" required maxlength="2000"></textarea></label>
    <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <button class="btn" type="submit">Send message</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div>
"""
    return page(ctx, f"Contact | {SITE_NAME}", "Send {SITE_NAME} a correction, town records, or a question.", body, "/contact")


def build_bot(ctx):
    body = f"""
<div class="wrap narrow prose">
<h1 id="bot-title">For website managers</h1>
<p class="lead">Our program, {BOT_NAME}, visits town websites once a day and reads only public agenda pages. It follows each website’s robots.txt rules.</p>
<p>If you run a town website and want it to stay away, add this to your robots.txt:</p>
<pre><code>User-agent: {BOT_NAME}
Disallow: /</code></pre>
<p>It identifies itself on every visit as:</p>
<pre><code>{e(BOT_UA)}</code></pre>
<p>Visits are signed with <a href="https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/">Web Bot Auth</a>. The public key is at <a href="/.well-known/http-message-signatures-directory">/.well-known/http-message-signatures-directory</a>.</p>
<ul>
  <li>It checks robots.txt before every visit, including redirects.</li>
  <li>It asks a website for at most one page a second, or less often if the website says so.</li>
  <li>It opens each agenda page about once a day and each agenda once.</li>
  <li>It never logs in, fills in forms or gets past a bot check.</li>
  <li>It skips files larger than 40 MB.</li>
</ul>
<p>Want something different? <a href="/contact">Send us a note</a>.</p>
</div>
"""
    return page(ctx, f"For website managers | {SITE_NAME}",
                f"How {BOT_NAME} reads town agenda pages: once a day, public pages only, following robots.txt, "
                "signed with Web Bot Auth. How to keep it away.",
                body, "/bot")


# ---------------------------------------------------------------- Attorney General and local actions

def framework_list(framework):
    """State rules and rulings as a dated list, oldest first; undated entries last."""
    entries = []
    for f in sorted(framework, key=lambda f: (not f.get("date"), f.get("date") or "")):
        d = f.get("date") or ""
        shown = fmt_date(d) if len(d) == 10 else datetime.strptime(d, "%Y-%m").strftime("%b %Y") if len(d) == 7 else d
        when = (f'<time datetime="{e(d)}">{shown}</time>' if d else "No single date")
        entries.append(f"""<li><p class="when">{when}</p><div><h3>{e(f['title'])}</h3><p>{e(f.get('summary', ''))}</p>{sources_html(f.get('sources', []))}</div></li>""")
    return f'<ol class="timeline">{"".join(entries)}</ol>'


def ag_numbers(ctx):
    """The figures every Attorney General page states, all from the same rows."""
    ag = ctx.ag
    dec = [r for r in ag if r.get("record_type") == "ag_decision"]
    # One letter can rule on two things (Gill: battery storage struck, data centers allowed); it is one decision.
    letters = {(str(r.get("case_number") or ""), ag_town(r["town"])) for r in dec}
    dates = sorted(r["decision_date"] for r in dec if r.get("decision_date"))
    headline, also, rec = moratorium_lines(ag)
    ruled = [r for r in dec if r.get("bylaw_type") == "zoning regulation" and r["outcome"] in ("approved", "approved in part", "disapproved")]
    return {
        "ag": ag, "dec": dec, "letters": len(letters), "dates": dates, "towns": len({ag_town(r["town"]) for r in dec}),
        "rt": Counter(r.get("record_type") for r in ag), "headline": headline, "also": also, "rec": rec,
        "ruled": len(ruled), "ruled_ok": sum(1 for r in ruled if r["outcome"] in ("approved", "approved in part")),
        "ruled_full": sum(1 for r in ruled if r["outcome"] == "approved"), "ruled_part": sum(1 for r in ruled if r["outcome"] == "approved in part"),
        "ok_any": sum(1 for r in dec if r["outcome"] in ("approved", "approved in part")),
    }


def ag_summary_line(n):
    return (f'{n["rec"]["disapproved"]} of {n["rec"]["total"]} moratoriums disapproved since Tracer Lane II; '
            f'{n["ruled_ok"]} of {n["ruled"]} zoning bylaws approved in whole or in part; {n["letters"]} decisions in {n["towns"]} towns, '
            f'{fmt_date(n["dates"][0]) if n["dates"] else ""} to {fmt_date(n["dates"][-1]) if n["dates"] else ""}.')


AG_PAGES = [("/attorney-general", "What a town can do"), ("/attorney-general/rulings", "Every ruling"),
            ("/attorney-general/town-actions", "Town actions"), ("/attorney-general/data-centers", "Data-center ledger"),
            ("/attorney-general/law", "State law")]

# The data-center ledger: one row per town measure (moratorium or ban), with every date the record has.
# Rows come from data/data_center_ledger.json, compiled by hand from the towns' warrants, the Attorney General's
# decision letters and the towns' bylaws; each row lists its sources. Status order is the reading order.
LEDGER_STATUS = [("in effect", "In effect"), ("adopted", "Adopted"), ("proposed", "Proposed"), ("expired", "Expired"),
                 ("disapproved", "Disapproved"), ("withdrawn", "Withdrawn"), ("reported", "Reported in the press, not confirmed")]
LEDGER_COLS = ["state", "town", "county", "measure", "body", "proposed_date", "adopted_date", "ag_decision", "ag_decision_date",
               "ag_case_number", "ag_decision_date_note", "in_effect_from", "in_effect_to", "proposed_term_from", "proposed_term_to",
               "status", "summary", "sources", "confidence"]
LEDGER_BADGE = {"in effect": "active", "adopted": "pending", "proposed": "pending", "expired": "cleared",
                "disapproved": "cleared", "withdrawn": "cleared", "reported": "info"}


def ledger_rows(ctx):
    """Ledger rows in reading order: in effect, adopted, proposed, then ended. A row still marked in effect whose end
    date has passed reads as expired. Missing file or no rows: an empty list, and the page is not built."""
    path = DATA / "data_center_ledger.json"
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text()).get("rows", [])
    except (OSError, ValueError):
        return []
    today = date.today().isoformat()
    order = {k: i for i, (k, _) in enumerate(LEDGER_STATUS)}
    out = []
    for r in rows:
        r = dict(r)
        if r.get("status") == "in effect" and r.get("in_effect_to") and r["in_effect_to"] < today:
            r["status"] = "expired"
        if r.get("status") not in order:
            continue
        if r["status"] in ("proposed", "withdrawn", "disapproved", "reported"):
            # a measure not in effect has a proposed term, not in-effect dates
            r["proposed_term_from"], r["proposed_term_to"] = r.get("in_effect_from"), r.get("in_effect_to")
            r["in_effect_from"] = r["in_effect_to"] = None
        out.append(r)
    out.sort(key=lambda r: (order[r["status"]], r.get("state") or "", r.get("town") or ""))
    return out


def ledger_csv(rows):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(LEDGER_COLS)
    for r in rows:
        w.writerow([" | ".join(abs_url(u) for u in (r.get("sources") or [])) if c == "sources" else (r.get(c) or "") for c in LEDGER_COLS])
    return out.getvalue()


def ledger_date(value, missing="Not found"):
    return fmt_date(value) if value else missing


def ledger_source_name(url):
    """What a source is, from its address: the letter, the warrant, an agenda, a news report, or the site's name."""
    u = url.lower()
    if "massago.hylandcloud" in u or "/letters/" in u or "ago%20" in u or "ago " in u:
        return "Attorney General letter"
    if "warrant" in u:
        return "Warrant"
    if re.search(r"agenda|opengov\.sos\.ri\.gov|legistar|civicclerk|granicus|boarddocs|novusagenda|meeting", u):
        return "Agenda"
    if re.search(r"masslive|yahoo|news|gazette|telegram|globe|patch\.com|wbur|wwlp|reporter|chronicle|herald|times", u):
        return "News report"
    if re.search(r"documentcenter|civicalerts|bylaw|ordinance|ecode360", u):
        return "Town document"
    host = re.sub(r"^www\.", "", urlparse(url).netloc)
    return host or "Source"


def ledger_sources_html(urls):
    seen = Counter()
    out = []
    for u in urls:
        name = ledger_source_name(u)
        seen[name] += 1
        label = f"{name} {seen[name]}" if seen[name] > 1 else name
        out.append(f'<a href="{e(u)}" rel="nofollow noopener" target="_blank">{e(label)}</a>')
    return ", ".join(out)


def smart_quotes(text):
    """Curly quotes for display: "word" becomes “word” and it's becomes it’s."""
    if not text:
        return text or ""
    out = re.sub(r'(^|[\s(\[\u2014\u2013/-])"', "\\1\u201c", text)
    out = out.replace('"', "\u201d")
    out = re.sub(r"(^|[\s(\[\u2014\u2013/-])'", "\\1\u2018", out)
    return out.replace("'", "\u2019")


def abs_url(url):
    return BASE_URL + url if url and url.startswith("/") else (url or "")


def source_dates(ctx):
    """{document url: meeting date} from the agendas we hold and the Attorney General's letters, to label sources."""
    cache = ctx.__dict__.get("_source_dates")
    if cache is None:
        cache = {}
        for path in sorted((DATA / "search").glob("*/*.jsonl")):
            for line in path.open():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("meeting_date"):
                    for k in ("url", "source_url"):
                        if row.get(k):
                            cache.setdefault(row[k], row["meeting_date"][:10])
        for r in ctx.ag:
            if r.get("letter_url") and len(r.get("decision_date") or "") == 10:
                cache.setdefault(abs_url(r["letter_url"]), r["decision_date"])
        ctx.__dict__["_source_dates"] = cache
    return cache


def ledger_sources_html_dated(ctx, urls):
    """"Agenda, Oct 5, 2026; Warrant, Oct 17, 2026; News report": each source named, with its date when we hold it."""
    dates = source_dates(ctx)
    seen = Counter()
    out = []
    for u in urls:
        u = abs_url(u)
        name = ledger_source_name(u)
        day = dates.get(u)
        label = f"{name}, {fmt_date(day)}" if day else name
        seen[label] += 1
        if seen[label] > 1:
            label += f" ({seen[label]})"
        out.append(f'<li><a href="{e(u)}" rel="nofollow noopener" target="_blank">{e(label)}</a></li>')
    return f'<ul class="ledger-srcs" aria-label="Sources">{"".join(out)}</ul>' if out else ""


def term_text(start, end):
    return (fmt_date(start) if start else "From adoption") + (f" to {fmt_date(end)}" if end else "")


def build_data_center_ledger(ctx):
    rows = ledger_rows(ctx)
    if not rows:
        return None
    counts = Counter(r["status"] for r in rows)
    label = dict(LEDGER_STATUS)
    tally = "; ".join(f"{counts[k]} {label[k].lower()}" for k, _ in LEDGER_STATUS if counts.get(k))
    generated = fmt_date((json.loads((DATA / "data_center_ledger.json").read_text()).get("generated") or date.today().isoformat())[:10])
    status_opts = "".join(f'<option value="{e(k)}">{e(v)}</option>' for k, v in LEDGER_STATUS if counts.get(k))
    body_rows = []
    ids = Counter()
    for r in rows:
        town = r.get("town") or ""
        st = r.get("state") or "MA"
        rid = "dc-" + slugify(f"{st}-{town}-{r.get('measure') or 'measure'}")
        ids[rid] += 1
        if ids[rid] > 1:
            rid += f"-{ids[rid]}"
        ag = ""
        ag_plain = ""
        if r.get("ag_decision"):
            bits = ([fmt_date(r["ag_decision_date"]) + (f" ({r['ag_decision_date_note']})" if r.get("ag_decision_date_note") else "")]
                    if r.get("ag_decision_date") else []) + ([f"case {r['ag_case_number']}"] if r.get("ag_case_number") else [])
            ag_plain = first_up(r["ag_decision"]) + (f", {', '.join(bits)}" if bits else "")
            ag = e(ag_plain)
        elif st == "MA":
            ag = "None yet"
        else:
            ag = "No state review"
        # A measure still proposed prints the dates it has and stops; one that passed prints every step.
        pairs = []
        if r["status"] in ("proposed", "withdrawn", "reported"):
            pairs.append(("Proposed", ledger_date(r.get("proposed_date"), "Date not found")))
            if r.get("proposed_term_from") or r.get("proposed_term_to"):
                pairs.append(("Proposed term", term_text(r.get("proposed_term_from"), r.get("proposed_term_to"))))
        else:
            if r.get("proposed_date"):
                pairs.append(("Proposed", fmt_date(r["proposed_date"])))
            pairs.append(("Adopted", ledger_date(r.get("adopted_date"))))
            pairs.append(("Attorney General", ag))
            if r["status"] == "in effect":
                if r.get("in_effect_from"):
                    pairs.append(("In effect", term_text(r["in_effect_from"], r.get("in_effect_to"))
                                  + ("" if r.get("in_effect_to") else ", no end date in the record")))
                else:
                    pairs.append(("In effect", "Yes (start date not found)"))
                if r.get("proposed_term_to"):
                    pairs.append(("Proposed extension", f"to {fmt_date(r['proposed_term_to'])}"))
            elif r["status"] == "expired":
                pairs.append(("In effect", term_text(r.get("in_effect_from"), r.get("in_effect_to")) if r.get("in_effect_to")
                              else "Ended; dates not found"))
            elif r.get("proposed_term_from") or r.get("proposed_term_to"):
                pairs.append(("Proposed term", term_text(r.get("proposed_term_from"), r.get("proposed_term_to"))))
        level, _, note = (r.get("confidence") or "").partition(":")
        level = level.strip()
        if level:
            pairs.append(("How sure", e(first_up(level))))
        dates_html = "".join(f"<dt>{e(k)}</dt><dd>{v}</dd>" for k, v in pairs)
        srcs = ledger_sources_html_dated(ctx, r.get("sources") or [])
        why = (f'<details class="ledger-why"><summary>Why we rate it {e(level)}</summary><p>{e(smart_quotes(first_up(note.strip())))}</p></details>'
               if note.strip() else "")
        search = " ".join(filter(None, [town, r.get("county") or "", f"{r['county']} County" if r.get("county") else "",
                                        STATE_NAMES.get(st, st), st, r.get("measure") or "", r.get("body") or "",
                                        label[r["status"]], r.get("summary") or ""]))
        cite_dates = "; ".join(x for x in [
            f"proposed {fmt_date(r['proposed_date'])}" if r.get("proposed_date") else "",
            f"adopted {fmt_date(r['adopted_date'])}" if r.get("adopted_date") else "",
            f"Attorney General {ag_plain[:1].lower()}{ag_plain[1:]}" if ag_plain else "",
            f"in effect {term_text(r['in_effect_from'], r.get('in_effect_to'))}" if r.get("in_effect_from") else "",
            f"proposed term {term_text(r.get('proposed_term_from'), r.get('proposed_term_to'))}"
            if (r.get("proposed_term_from") or r.get("proposed_term_to")) and r["status"] != "in effect" else "",
            f"proposed extension to {fmt_date(r['proposed_term_to'])}" if r["status"] == "in effect" and r.get("proposed_term_to") else "",
        ] if x)
        citation = (f"{town}, {st}: {r.get('measure') or 'measure'} on data centers, {label[r['status']].lower()}"
                    + (f" ({cite_dates})" if cite_dates else "") + f". {smart_quotes(r.get('summary') or '')} "
                    f"Sources: {' | '.join(abs_url(u) for u in (r.get('sources') or []))}. "
                    f"Agenda Ahead data-center ledger, {BASE_URL}/attorney-general/data-centers#{rid}, checked {generated}.")
        cite_btn = f'<button type="button" class="link-btn cite" data-copy="{e(citation)}" hidden>Copy citation</button>'
        # the next meeting with a data-center item in this town, from the same agendas as Coming up
        nxt = next((m for m in upcoming_meetings(ctx, f"{st}:{town}")
                    if any("data_center" in (en.get("topics") or []) for en in m["lines"].values())), None)
        if nxt and r["status"] in ("proposed", "adopted", "reported", "in effect"):
            pairs.insert(0, ("Next on an agenda", f'<a href="/m/{nxt["id"][2:]}">{e(meeting_board(nxt))}, {e(day_label(nxt["date"], ctx))}</a>'))
        # the group heading names the status, so the row's key is the date that matters for it
        key = {"in effect": f"To {fmt_date(r['in_effect_to'])}" if r.get("in_effect_to") else "No end date",
               "expired": f"Ended {fmt_date(r['in_effect_to'])}" if r.get("in_effect_to") else "Ended",
               "adopted": fmt_date(r["adopted_date"]) if r.get("adopted_date") else "Date not found",
               "proposed": fmt_date(r["proposed_date"]) if r.get("proposed_date") else "Date not found",
               "reported": "In the press"}.get(r["status"], label[r["status"]])
        if nxt and r["status"] in ("proposed", "adopted", "reported"):
            key = f"On the agenda {short_day(nxt['date'])}"
        place = town + ("" if st == "MA" else f", {st}")
        where = (f"{r['county']} County" if r.get("county") else "") + (f", {STATE_NAMES.get(st, st)}" if st != "MA" else "")
        more = f' <a href="{town_path(st, town)}">Everything about {e(town)}</a>' if f"{st}:{town}" in ctx.town_by_id else ""
        lead_pairs = [(k, e(v)) for k, v in (("Where", where), ("Decided by", r.get("body") or "")) if v]
        dates_html = "".join(f"<dt>{e(k)}</dt><dd>{v}</dd>" for k, v in lead_pairs) + dates_html
        body = (f'<dl class="ledger-dates">{dates_html}</dl>{why}'
                f'<p>{e(smart_quotes(r.get("summary") or ""))}</p>'
                f'{srcs}<p class="rec-links">{cite_btn}{more}</p>')
        body_rows.append((r["status"], rec_li(e(place), e(first_up(r.get("measure") or "")), e(key), body,
                                              f' data-search="{e(search)}" data-status="{e(r["status"])}"', rid)))
    body = f"""
<div class="wrap">
{ag_nav("/attorney-general/data-centers")}
<h1 id="ledger-title">Data-center ledger</h1>
<p class="lead">Every town and city with a data-center moratorium or ban, proposed, in effect or ended: {plural(len(rows), 'measure')} in {len({(r.get('state'), r.get('town')) for r in rows})} places. Tap one for its dates and sources. Checked {generated}.</p>
{ag_checked(ctx)}
<form class="filterbar" data-list-filter data-noun="measures">
  <label>Status<select data-status><option value="">All</option>{status_opts}</select></label>
  <label>Town, county, state or words<input type="search" data-search autocomplete="off"></label>
  <p class="count" data-count aria-live="polite"></p>
</form>
<div class="rec-list" id="ledger">{"".join(
        f'<section class="rec-group" data-status-group="{e(k)}"><h2 class="rec-head">{e(v)} <span class="sub-count">{plural(counts[k], "measure")}</span></h2>'
        f'<ul class="recs" data-filter-list>{"".join(li for s, li in body_rows if s == k)}</ul></section>'
        for k, v in LEDGER_STATUS if counts.get(k))}</div>
<p class="muted" data-empty hidden>No measure matches.</p>
<p class="action-row"><a href="/attorney-general/data-centers.csv" download>Download the ledger (CSV)</a></p>
<p class="form-note">A Massachusetts town can pause data centers: state law protects solar and battery storage, not data centers. The Attorney General approved the moratoriums in {ag_letter_links(ctx, ("Shutesbury", "Templeton", "Gill"), "data center")}. Once the Attorney General approves a town’s moratorium and the town posts it, it counts from the Town Meeting vote (G.L. c. 40A, § 5); a city’s counts from the council vote. Each runs to the end date it names. Dates come from the warrant, the decision letter and the bylaw; a date we could not find in those reads “Not found”.</p>
</div>
"""
    write("attorney-general/data-centers.csv", ledger_csv(rows))
    return page(ctx, f"Data-center moratoriums and bans, town by town | {SITE_NAME}",
                f"{len(rows)} data-center moratoriums and bans in Massachusetts and nearby states, each with the date it was "
                "proposed, adopted, approved and took effect, and a link to every source. With a CSV.",
                body, "/attorney-general/data-centers")


COMING_TABS = [("/upcoming", "By date"), ("/trending", "Biggest stories")]


def tabs(items, current, label):
    """One row of tabs inside a page: the current one is plain text, underlined."""
    return (f'<nav class="tabs" aria-label="{e(label)}"><ul>' + "".join(
        f'<li><span aria-current="page">{e(t)}</span></li>' if href == current else f'<li><a href="{href}">{e(t)}</a></li>'
        for href, t in items) + "</ul></nav>")


def site_checked(ctx):
    """"Checked Oct 17, 9:15 am from the agendas towns post online": when the morning's reading finished."""
    when = et_when(ctx.hits_doc.get("generated") or "")
    return f'<p class="checked">Checked {e(when)} from the agendas towns post online.</p>' if when else ""


def ag_nav(current):
    ledger = (DATA / "data_center_ledger.json").exists()
    crumbs = "" if current == "/attorney-general" else (
        '<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/attorney-general">Rulings</a></li>'
        f'<li><span aria-current="page">{e(dict(AG_PAGES).get(current, ""))}</span></li></ol></nav>')
    return crumbs + '<nav class="tabs" aria-label="Rulings pages"><ul>' + "".join(
        f'<li>{"<span aria-current=\"page\">" + e(label) + "</span>" if href == current else f"<a href={chr(34)}{href}{chr(34)}>{e(label)}</a>"}</li>'
        for href, label in AG_PAGES if ledger or not href.endswith("/data-centers")) + "</ul></nav>"


def city_words_count(ag):
    """"1 city ordinance adopted and 2 proposed": city items by what happened to them."""
    rows = [r for r in ag if r.get("record_type") == "city_ordinance"]
    done = [r for r in rows if not (r.get("outcome") or "").startswith("proposed")]
    prop = len(rows) - len(done)
    return (f"{plural(len(done), 'city ordinance')} adopted" + (f" and {prop} proposed" if prop else "")) if done else f"{plural(prop, 'city ordinance')} proposed"


def ag_checked(ctx):
    """"Checked Oct 10 from the Attorney General’s decision letters": when the rulings data was last gone over."""
    when = ctx.tracker.get("generated") or ""
    return f'<p class="checked">Checked {fmt_date(when)} from the Attorney General’s decision letters and the towns’ postings.</p>' if when else ""


def build_ag(ctx):
    n = ag_numbers(ctx)
    ag, dec, rec = n["ag"], n["dec"], n["rec"]
    dates = n["dates"]

    def counts(rows):
        c = Counter(r["outcome"] for r in rows)
        return c.get("approved", 0), c.get("approved in part", 0), c.get("disapproved", 0), len(rows)

    def examples(rows, k=3):
        latest = sorted(rows, key=lambda r: r["decision_date"], reverse=True)
        seen, out = set(), []
        for r in latest:
            t = ag_town(r["town"])
            if t not in seen:
                seen.add(t)
                out.append(ctx.town_link("MA", t))
            if len(out) == k:
                break
        return ", ".join(out)

    zr = [r for r in dec if r.get("bylaw_type") == "zoning regulation"]
    zp = [r for r in dec if r.get("bylaw_type") == "zoning prohibition"]
    gl = [r for r in dec if (r.get("bylaw_type") or "").startswith("general bylaw")]
    # a ban on stand-alone or principal-use battery storage, whatever kind of article carried it
    sb = [r for r in dec if "stand-alone battery storage ban" in (r.get("provisions") or [])]
    sb_struck = [r for r in sb if r["outcome"] in ("disapproved", "approved in part")]
    sb_ok = [r for r in sb if r["outcome"] == "approved"]
    cp = [r for r in dec if r.get("bylaw_type") == "consolidated permit bylaw"]
    part = [r for r in dec if r["outcome"] == "approved in part"]
    herb = [r for r in part if re.search(r"herbicid|pesticid", r.get("summary", "") + " " + r.get("legal_basis", ""), re.I)]
    dc = [r for r in ag if "data cent" in r.get("summary", "").lower()]

    def ratio(rows):
        a, p, d, k = counts(rows)
        return f"{a} approved, {p} in part, {d} disapproved (of {k})"

    patterns = [
        ("Moratorium on solar or battery storage, of any length or area, since Tracer Lane II (June 2, 2022)",
         "Disapproved", f"{rec['disapproved']} of {rec['total']} ruled on, in {plural(rec['towns'], 'town')}", examples(rec["rows"])),
        ("Zoning that sets rules for solar or battery storage: size tiers, districts, special permits, site plan review, setbacks",
         "Approved, often with some parts struck", ratio(zr), examples(zr)),
        ("A ban on stand-alone or principal-use battery storage, in any kind of article",
         "Struck every time since March 2023", f"{len(sb_struck)} struck, {len(sb_ok)} approved (of {len(sb)})"
         + (f"; the approval was {', '.join(ag_town(r['town']) + ' on ' + fmt_date(r['decision_date']) for r in sb_ok)}" if sb_ok else ""),
         examples(sb_struck)),
        ("Licensing or another general (non-zoning) bylaw for battery storage",
         "Disapproved: it has to be adopted as zoning", ratio(gl), examples(gl)),
        ("Bans on weed killers or pesticides at solar or battery storage sites",
         "Struck: state pesticide law (G.L. c. 132B) overrides town rules", f"In {len(herb)} of {len(part)} partial approvals", examples(herb)),
        ("A bylaw for the state’s new clean-energy permit (225 CMR 29.00)", "Approved", ratio(cp), examples(cp)),
        ("Data-center moratorium", "Approved: data centers aren’t protected the way solar is",
         "Shutesbury, Templeton and Gill, all in 2026", examples(dc)),
    ]
    pattern_rows = "".join(
        f"<tr><th scope='row'>{e(p)}</th><td data-label='Result'><span class='badge'>{e(res)}</span></td><td data-label='Count'>{e(cnt)}</td><td data-label='Recent examples'>{ex}</td></tr>"
        for p, res, cnt, ex in patterns)
    all_n = rec["total"]
    body = f"""
<div class="wrap narrow">
{ag_nav("/attorney-general")}
<h1 id="ag-title">What a town can do</h1>
<p class="lead">A Massachusetts town can set rules for solar and battery storage, but pausing or banning them almost never gets past the state. It can pause or ban data centers. The state’s Attorney General reviews every town bylaw before it takes effect; here is how those reviews have gone.</p>
{ag_checked(ctx)}
<ul class="answers">
  <li class="answer"><b>A moratorium on solar or battery storage</b><span>Disapproved every time since June 2022: {rec['disapproved']} of {all_n}, in {plural(rec['towns'], 'town')}.</span><a href="/attorney-general/rulings?bylaw=moratorium">See them</a></li>
  <li class="answer"><b>Zoning rules for solar or battery storage</b><span>Approved {n['ruled_ok']} times out of {n['ruled']}: {n['ruled_full']} in full and {n['ruled_part']} with some parts struck.</span><a href="/attorney-general/rulings?bylaw=zoning+regulation">See them</a></li>
  <li class="answer"><b>A moratorium or ban on data centers</b><span>Approved: moratoriums in Shutesbury, Templeton and Gill (where the battery-storage half of the same article was struck), and Shutesbury’s ban in every district. State law doesn’t protect data centers.</span><a href="/attorney-general/data-centers">Data-center ledger</a></li>
  <li class="answer"><b>New in 2026</b><span>The state’s highest court ruled in Sunpin (Jul 14, 2026) that a town may deny a special permit for a protected solar project only when necessary to protect public health, safety or welfare. Since Oct 1, 2026, every town must take consolidated permit applications for small clean-energy projects and decide them within 12 months, or the project is approved.</span><a href="/attorney-general/law">State law</a></li>
</ul>
<p class="small">{plural(len(dec), 'ruling')} in {plural(n['letters'], 'case')} to {plural(n['towns'], 'town')}, letters dated {fmt_date(dates[0]) if dates else ''} to {fmt_date(dates[-1]) if dates else ''}; plus {plural(n['rt'].get('court_ruling', 0), 'court ruling')}, {city_words_count(ag)} and {plural(n['rt'].get('pending_ag_review', 0), 'bylaw')} awaiting a decision.</p>
<h2 id="survives-title">How the Attorney General has ruled, by kind of bylaw</h2>
<div class="table-wrap"><table class="stack"><thead><tr><th scope="col">Kind of bylaw</th><th scope="col">Result</th><th scope="col">Count</th><th scope="col">Recent examples</th></tr></thead><tbody>{pattern_rows}</tbody></table></div>
<p class="small">{e(n['also'])} The three data-center letters are in the rulings list too: Shutesbury’s (case 12047, Jan 20, 2026) and Templeton’s (case 12294, decided between Sep 14 and Sep 22, 2026) as the towns posted them, and Gill’s (case 12422, Sep 24, 2026), which struck the battery-storage half of the same article.</p>
<h2 id="why-title">Why</h2>
<p>The Attorney General reviews every town bylaw (G.L. c. 40, § 32); one the office doesn’t act on in time counts as approved. Once a zoning bylaw is approved and posted, it takes effect as of the Town Meeting vote (G.L. c. 40A, § 5). City ordinances don’t go to the Attorney General. {LAW_SOLAR} Since Tracer Lane II, the Attorney General judges what a bylaw is for against how much it burdens solar, and many approvals warn that using a bylaw to deny a project <q>would run a serious risk of violating</q> § 3.</p>
<p>{LAW_BATTERY}</p>
<p>The Attorney General approved data-center moratoriums in Shutesbury, Templeton and Gill, because state law doesn’t protect data centers the way it protects solar; the letters are in <a href="/attorney-general/rulings">the rulings list</a>. Missing or out of date? <a href="/contact">Send a correction</a>.</p>
<details class="disclose"><summary>Words on this page</summary>
<p class="terms"><dfn>Tracer Lane II</dfn>: the 2022 ruling by the state’s highest court that a town can’t use zoning to ban solar. <dfn>G.L. c. 40A, § 3</dfn>: the state zoning law’s solar clause; a town can’t prohibit solar or restrict it unreasonably. <dfn>225 CMR 29.00</dfn>: the state’s rules, final in February 2026, for permitting small clean-energy projects with one consolidated local permit. <dfn>Land Court</dfn>: a state trial court for land disputes; its rulings carry less weight than the highest court’s.</p>
</details>
</div>
"""
    return page(ctx, f"Massachusetts Attorney General rulings on bylaws | {SITE_NAME}",
                f"Since Tracer Lane II the Attorney General has disapproved {rec['disapproved']} of {all_n} town moratoriums on solar or "
                f"battery storage and approved {n['ruled_ok']} of {n['ruled']} zoning bylaws.",
                body, "/attorney-general")


def build_ag_rulings(ctx):
    n = ag_numbers(ctx)
    ag = n["ag"]

    def opts(values):
        return "".join(f'<option value="{e(v)}">{e(first_up(v))}</option>' for v in values)

    outcomes = [o for o, _ in Counter(r.get("outcome") for r in ag).most_common()]
    bylaws = [b for b, _ in Counter(r.get("bylaw_type") for r in ag).most_common()]
    techs = [t for t, _ in Counter(r.get("technology") for r in ag).most_common()]
    # the Attorney General's own decisions (and the bylaws awaiting one) in the table; court rulings and city
    # ordinances, which the Attorney General does not review, in their own table under it
    decisions = [r for r in ag if r.get("record_type") in ("ag_decision", "pending_ag_review")]
    context = [r for r in ag if r.get("record_type") not in ("ag_decision", "pending_ag_review")]
    outcomes = [o for o, _ in Counter(r.get("outcome") for r in decisions).most_common()]
    bylaws = [b for b, _ in Counter(r.get("bylaw_type") for r in decisions).most_common() if b]
    techs = [t for t, _ in Counter(r.get("technology") for r in decisions).most_common() if t]
    years = sorted({(r.get("decision_date") or "")[:4] for r in decisions if r.get("decision_date")}, reverse=True)
    counties = sorted({r.get("county") for r in decisions if r.get("county")})
    # each row's line in rulings.csv (same order as ag_csv), so the download can follow the filters
    for i, r in enumerate(sorted(ag, key=lambda r: r.get("decision_date") or "", reverse=True)):
        r["_csv"] = i
    body = f"""
<div class="wrap">
{ag_nav("/attorney-general/rulings")}
<h1 id="ag-title">Every ruling</h1>
<p class="lead">Every decision the Massachusetts Attorney General has made on a town’s solar, battery storage or data-center bylaw since 2022, newest first. Tap one for the letter.</p>
<p class="checked">{plural(len(n["dec"]), "ruling")} in {plural(n["letters"], "case")} to {plural(n["towns"], "town")}{f', {fmt_date(n["dates"][0])} to {fmt_date(n["dates"][-1])}' if n["dates"] else ""}. A case can have more than one letter, and Gill’s one letter rules on two bylaws. {plural(sum(1 for r in ag if r.get("record_type") == "pending_ag_review"), "bylaw")} awaiting a decision is listed at the end.</p>
{ag_checked(ctx)}
<details class="filter-box"><summary>Filter the rulings</summary>
<div class="filterbar" data-filters="ag-ledger">
  <label>Outcome<select data-key="outcome"><option value="">All</option>{opts(outcomes)}</select></label>
  <label>Kind of bylaw<select data-key="bylaw"><option value="">All</option>{opts(bylaws)}</select></label>
  <label>Technology<select data-key="tech"><option value="">All</option>{opts(techs)}</select></label>
  <label>County<select data-key="county"><option value="">All</option>{opts(counties)}</select></label>
  <label>Year<select data-key="year"><option value="">All</option>{opts(years)}</select></label>
  <label>Words<input type="search" data-search></label>
</div>
</details>
<p class="results-head" data-count-for="ag-ledger" aria-live="polite"></p>
{ag_table(ctx, decisions, table_id='ag-ledger', filters=True, by_year=True)}
<p class="action-row"><a href="/attorney-general/rulings.csv" download data-csv-for="ag-ledger">Download everything as a CSV ({len(ag)} rows: {len(n["dec"])} rulings, {n["rt"].get("court_ruling", 0)} court rulings, {n["rt"].get("city_ordinance", 0)} city items, {n["rt"].get("pending_ag_review", 0)} awaiting a decision)</a></p>
<h2 id="ag-context-title">Court rulings and city ordinances</h2>
<p>For context: the courts’ rulings on these bylaws, and what cities (which adopt ordinances without Attorney General review) have done.</p>
{ag_table(ctx, context, table_id='ag-context', filters=True, group='ag-ledger')}
</div>
"""
    write("attorney-general/rulings.csv", ag_csv(ag))
    return page(ctx, f"Every Attorney General ruling on solar and battery bylaws | {SITE_NAME}",
                f"All {n['letters']} Massachusetts Attorney General decisions on town solar, battery storage and data-center bylaws since 2022, "
                "with a link to each letter, plus the court rulings around them.",
                body, "/attorney-general/rulings")


def build_ag_actions(ctx):
    n = ag_numbers(ctx)
    items = ctx.tracker.get("items", [])
    counties = sorted({i.get("county", "") for i in items if i.get("county")})
    county_opts = "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in counties)
    verified = fmt_date(ctx.tracker.get("generated", date.today().isoformat()))
    body = f"""
<div class="wrap">
{ag_nav("/attorney-general/town-actions")}
<h1 id="ag-title">Town actions</h1>
<p class="lead">What towns and cities have done about battery storage and solar: moratoriums, special acts, zoning bylaws and permit rules. Tap one for its sources. Checked {verified}.</p>
{ag_checked(ctx)}
<details class="filter-box"><summary>Filter the actions</summary>
<div class="filterbar">
  <label>Status<select id="f-status"><option value="">All</option><option value="pending">Pending</option><option value="active">In effect or adopted</option><option value="cleared">Not in effect</option><option value="info">Permit rules</option></select></label>
  <label>Topic<select id="f-topic"><option value="">All</option><option value="battery">Battery storage</option><option value="solar">Solar</option></select></label>
  <label>County<select id="f-county"><option value="">All</option>{county_opts}</select></label>
  <label>Words<input id="f-search" type="search"></label>
</div>
</details>
<p class="results-head" id="f-count" aria-live="polite"></p>
{tracker_table(ctx, items, "tracker-table")}
<p class="action-row"><a href="/attorney-general/town-actions.csv" download>Download the table (CSV)</a></p>
</div>
"""
    write("attorney-general/town-actions.csv", actions_csv(items))
    return page(ctx, f"Town and city actions on battery storage and solar | {SITE_NAME}",
                f"{len(items)} Massachusetts town and city actions on battery storage and solar: moratoriums, special acts, "
                "zoning bylaws and permit rules, each with a link to its source.",
                body, "/attorney-general/town-actions")


def build_ag_law(ctx):
    n = ag_numbers(ctx)
    dec = n["dec"]

    def counts(rows):
        c = Counter(r["outcome"] for r in rows)
        return c.get("approved", 0), c.get("approved in part", 0), c.get("disapproved", 0), len(rows)

    def count_cells(a, p, d, k):
        cells = (("Approved", a), ("In part", p), ("Disapproved", d), ("Other", k - a - p - d), ("Total", k))
        return "".join(f"<td class='num' data-label='{label}'>{v}</td>" for label, v in cells)

    dec = [r for r in dec if r.get("technology") != "data center"]  # data-center moratoriums have their own page
    types = Counter(r.get("bylaw_type") for r in dec)
    type_rows = "".join(
        f"<tr><th scope='row'>{e(first_up(t))}</th>{count_cells(a, p, d, k)}</tr>"
        for t, _ in types.most_common()
        for a, p, d, k in [counts([r for r in dec if r.get("bylaw_type") == t])])
    year_rows = "".join(
        f"<tr><th scope='row'>{y}</th>{count_cells(a, p, d, k)}</tr>"
        for y in sorted({r["decision_date"][:4] for r in dec})
        for a, p, d, k in [counts([r for r in dec if r["decision_date"][:4] == y])])
    cnt_head = ('<thead><tr><th scope="col">{}</th><th scope="col" class="num">Approved</th><th scope="col" class="num">In part</th>'
                '<th scope="col" class="num">Disapproved</th><th scope="col" class="num">Other</th><th scope="col" class="num">Total</th></tr></thead>')
    body = f"""
<div class="wrap narrow">
{ag_nav("/attorney-general/law")}
<h1 id="ag-title">State law</h1>
<p class="lead">{LAW_SOLAR}</p>
{ag_checked(ctx)}
<p>{LAW_BATTERY}</p>
<h2 id="timeline-title">What the courts and the Legislature have said, in date order</h2>
<p class="section-lead">Since October 1, 2026, every Massachusetts city and town has had to accept consolidated permit applications for small clean-energy projects and decide them within 12 months.</p>
{framework_list(ctx.tracker.get('framework', []))}
<h2 id="bytype-title">Attorney General rulings on solar and battery-storage bylaws, by kind and by year</h2>
<p class="small">{plural(len(dec), 'ruling')}. Data-center moratoriums are counted on <a href="/attorney-general/data-centers">the data-center ledger</a>.</p>
<div class="cols">
  <div class="table-wrap" tabindex="0" role="region" aria-label="Outcomes by kind of bylaw"><table class="stack counts"><caption>By kind of bylaw</caption>{cnt_head.format('Kind of bylaw')}<tbody>{type_rows}</tbody></table></div>
  <div class="table-wrap" tabindex="0" role="region" aria-label="Outcomes by year"><table class="stack counts"><caption>By year</caption>{cnt_head.format('Year')}<tbody>{year_rows}</tbody></table></div>
</div>
</div>
"""
    return page(ctx, f"State law and court rulings on solar and battery storage | {SITE_NAME}",
                "Massachusetts law on solar and battery storage: G.L. c. 40A § 3, Tracer Lane II, the Land Court's battery "
                "rulings and the 2024 Climate Act permit.",
                body, "/attorney-general/law")


# ---------------------------------------------------------------- beta (/pricing)
# The page states what is free and that a paid plan comes later, with no prices. Plan definitions and the
# (disabled) Stripe checkout live in site/api/checkout.js and site/pricing.js and are not rendered here.

def build_pricing(ctx):
    body = f"""
<div class="wrap narrow prose">
<section class="page-head" aria-labelledby="pricing-title">
  <h1 id="pricing-title">It’s free</h1>
  <p class="lead">Alerts for your town and the towns next to it are free: every board we check, every topic, and no account. Today that is a calendar feed and a private page that updates as agendas post; email alerts are coming, at most one a day. Your private link lets you change or delete your alerts.</p>
  <p class="actions"><a class="btn" href="/watch">Get free alerts</a></p>
</section>
<p class="notice" id="checkout-note" role="status" hidden></p>
<section aria-labelledby="later-title">
  <h2 id="later-title">Later</h2>
  <p>If we start charging businesses that watch many towns, we’ll say so here first. There’s nothing to buy today. <a href="/contact">Tell us what you need</a>.</p>
</section>
</div>
"""
    return page(ctx, f"It’s free | {SITE_NAME}",
                "Alerts for your town and the towns next to it are free, with no account. If we start charging businesses "
                "that watch many towns, we'll say so here first.",
                body, "/pricing", scripts=("/pricing.js",))


# ---------------------------------------------------------------- old URLs

REDIRECTS = {
    # file: (target path, default fragment, {old fragment: new fragment}, title)
    "proof.html": ("/how-it-works", "#coverage", {
        "#our-timing": "#timing", "#lead-title": "#timing", "#ag-title": "#attorney-general", "#gaps-title": "#gaps",
        "#boards-title": "#coverage", "#towns-title": "/towns", "#method-title": "#crawler"}, "Coverage and method"),
    "pricing.html": ("/how-it-works", "#free", {}, "What it costs"),
}


def redirect_page(target, default, mapping, title):
    to = target + default
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} moved | {e(SITE_NAME)}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{BASE_URL}{target}">
<script src="/redirect.js" data-to="{e(target)}" data-default="{e(default)}" data-map="{e(json.dumps(mapping))}"></script>
<meta http-equiv="refresh" content="0; url={e(to)}">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<main id="main"><div class="wrap narrow"><p class="lead">This page moved to <a href="{e(to)}">How {SITE_NAME} works</a>.</p></div></main>
</body>
</html>
"""


# ---------------------------------------------------------------- sitemap, robots, town index

def build_sitemap(paths):
    today = today_et()
    urls = "".join(f"<url><loc>{BASE_URL}{'' if p == '/' else p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def build_robots():
    return f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /w/\nDisallow: /w?\n\nSitemap: {BASE_URL}/sitemap.xml\n"


def search_titles(ctx):
    """{agenda URL: {"title": its main item's headline, "more": other items written up on it, "page": the meeting's
    page here, "" when the meeting has passed}}: Search titles an agenda by what is on it, not by its file name, and
    sends the reader to the meeting's page (search/build-index.mjs reads this; a vote or hearing first)."""
    best = {}
    lines = defaultdict(set)
    order = {"vote": 0, "hearing": 1, "continued": 2, "adopted": 3}
    for h in ctx.hits:
        b = BRIEFS.get(h["id"])
        if not b or not b.get("line") or b.get("duplicate_of") or OFF_ITEM.search(b["line"]):
            continue
        rank = (order.get(b.get("action"), 9), item_text(h).get("rank", 60))  # a vote or hearing, then the bigger item
        url = h.get("source_url") or ""
        if not url:
            continue
        lines[url].add(headline(b["line"]))
        if url not in best or rank < best[url][0]:
            best[url] = (rank, headline(b["line"]))
    pages = {}
    for m in group_meetings(ctx, upcoming_hits(ctx)):
        for d in m["docs"]:
            pages.setdefault(d["url"], f"/m/{m['id'][2:]}")
    out = {u: {"title": t, "more": len(lines[u]) - 1, "page": pages.get(u, "")} for u, (_, t) in best.items()}
    for u, pg in pages.items():
        out.setdefault(u, {"title": "", "more": 0, "page": pg})
    return out


def search_pages(ctx):
    """{"MA|Lancaster|planning_board|2026-10-26": {"page": the meeting's page, "title": its main item's headline}}:
    a board's day posted as several documents (an agenda, two hearing notices) is one meeting on /search, under
    the headline we wrote, whichever document the words were found in (search/build-index.mjs reads this)."""
    out = {}
    for m in group_meetings(ctx, upcoming_hits(ctx)):
        if not m.get("date") or not m.get("board_key"):
            continue
        lines = real_lines(m)
        title = headline(plain_say(lines[0][0])) if lines else ""
        out.setdefault(f"{m['state']}|{m['town']}|{m['board_key']}|{m['date']}", {"page": f"/m/{m['id'][2:]}", "title": title})
    return out


def town_index_json(ctx):
    return json.dumps({
        "generated": ctx.hits_doc.get("generated"),
        "towns": [{"id": t["id"], "state": t["state"], "town": t["town"], "county": t.get("county"),
                   "slug": t["slug"], "monitored": t["monitored"],
                   **({} if t["monitored"] else {"why": REASON_TAG.get(t.get("reason_code") or "", "not worked out yet")})}
                  for t in ctx.towns],
    }, separators=(",", ":"))


def lines_json(ctx):
    """site/data/lines.json for the alert pages. lines: {id: [sentence, quote, note, kind, item key, board, rank,
    article or item number, subject, stage, facts]}; by_url: {agenda url: [hit ids]} (search rows); at: {agenda url: [time, place]}; new: ids first posted in the last 48 hours;
    recent: the items of the last 30 days and ahead by town (for the alert preview)."""
    since = (datetime.strptime(ctx.today, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
    recent = defaultdict(list)
    for h in sorted(ctx.hits, key=lambda h: h.get("meeting_date") or ""):
        d = (h.get("meeting_date") or "")[:10]
        if d >= since:
            recent[f"{h['state']}:{h['town']}"].append([d, board_label(h), h.get("topics", []), h["id"]])
    lines = {}
    for h in ctx.hits:
        t = item_text(h)
        lines[h["id"]] = [headline(t["say"]), t.get("quote") or "", t["note"], t["kind"],
                          t.get("key") or (find_name(" ".join((h.get("snippet") or "").split()))[0] or find_address(h.get("snippet") or "")).lower(),
                          who_label(h), t.get("rank", 60), t.get("no", ""), t.get("subj", ""), t.get("stage", ""), list(t.get("facts") or []),
                          list(h.get("topics") or [])]
    by_url = defaultdict(list)
    for h in ctx.hits:
        by_url[h["source_url"]].append(h["id"])
    # at: {agenda url: [time, place, cancelled]} from the grouped meetings, so the alert pages and the calendar
    # feed say the same room, the same hour and the same cancellation as the site.
    at = {}
    for m in group_meetings(ctx, ctx.hits):
        place = "" if (m["board_key"] == "town_meeting" and m.get("place") == "online") else (m.get("place") or "")
        when = [m.get("time") or "", place, bool(m.get("cancelled"))]
        if any(when):
            for d in m["docs"]:
                at[d["url"]] = when
    return json.dumps({
        "generated": ctx.hits_doc.get("generated"),
        "today": ctx.today,
        "since": since,
        "lines": lines,
        "at": at,
        "new": [h["id"] for h in ctx.hits if ctx.is_new(h)],
        "first_sweep": ctx.first_sweep,
        "briefs": {h["id"]: public_brief(BRIEFS[h["id"]]) for h in ctx.hits if h["id"] in BRIEFS},
        "by_url": by_url,
        "speak": SPEAK_TEXT,
        "brief_labels": BRIEF_LABELS,
        "brief_speak": {"true": BRIEF_SPEAK[True], "false": BRIEF_SPEAK[False]},
        "recent": recent,
    }, separators=(",", ":"), ensure_ascii=False)


def build_meeting_page(ctx, m):
    """/m/<id>: one upcoming meeting. The board as the heading, the day and place once, each item in full
    (with the agenda's wording behind a tap), where it came from, and the one action row on the site."""
    first = next(iter(m["lines"]), "")
    t = ctx.town_by_id.get(f"{m['state']}:{m['town']}") or {}
    title = f"{m['town']} {meeting_board(m)}"
    d = m["docs"][0] if m["docs"] else None
    what = "filing" if m["source"] == "massdep_wetlands" else ("warrant" if m["board_key"] == "town_meeting" else "agenda")
    label = "Open the Town Meeting warrant" if what == "warrant" else f"Open the {what}"
    link = f'<a class="item-link" href="{e(d["url"])}" rel="nofollow noopener" target="_blank">{label}{" (PDF)" if d["pdf"] else ""}</a>' if d else ""
    # When, where and whether you can speak sit in the ticket, where someone deciding whether to go looks first.
    speak_top = "" if m.get("cancelled") else speak_line(m)
    health = (ctx.health or {}).get(t.get("id")) or {}
    checked = et_when(health["last_success"]) if health.get("last_success") else ""
    host = re.sub(r"^www\.", "", (d["url"].split("/")[2] if d and "//" in d["url"] else ""))
    posted = posted_text(ctx, m).replace("Filed", "filed")
    entry = next(iter(m["lines"].values()), None)
    read = short_day(entry["seen"][:10]) if entry and entry.get("seen") else ""
    prov = (f"From the {meeting_board(m)} {what}{' ' + posted if posted else ''}{' on ' + e(host) if host else ''}."
            + (f" Last checked {e(checked)}." if checked else (f" Read {e(read)}." if read else "")))
    cite = citation(ctx, m, entry)
    share = (f'<button type="button" class="link-btn" data-share data-url="{e(meeting_share_url(ctx, m))}" data-title="{e(title + ", " + when_text(ctx, m))}" '
             f'data-text="{e(share_text(ctx, m, first, entry, [t for t, _ in real_lines(m)][1:3]))}" hidden>Share</button>')
    copy = f'<button type="button" class="link-btn" data-copy="{e(cite)}" hidden>Copy citation</button>'
    about = quote(f"{m['town']}, {meeting_board(m)}" + (f", {day_label(m['date'], ctx)}" if m["date"] else ""), safe="")
    place = place_text(m["place"]) if m["place"] and m["source"] != "massdep_wetlands" else ""
    when = (f'<time datetime="{m["date"]}">{e(when_text(ctx, m))}</time>' if m["date"] else "Date not found on the warrant")
    if m.get("cancelled"):
        when += ' <b class="ticket-canceled">Canceled by the town</b>'
    # The meeting's facts, labelled, where someone deciding whether to go looks first; the follow box after the items.
    facts = [("When", when), ("Where", e(place) if place else "Not on the agenda")]
    if m.get("watch"):
        facts.append(("Watch", e(" or ".join(m["watch"]))))
    speak = " ".join(x for x in (speak_top, who_votes_text(m)) if x)
    if speak:
        facts.append(("Public comment" if m["board_key"] != "town_meeting" else "Who votes", e(speak)))
    if link:
        facts.append(("Agenda" if what != "warrant" else "Warrant", link + (f' <span class="muted">({e(posted)})</span>' if posted else "")))
    ticket = ('<div class="ticket"><dl class="facts-list">'
              + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts) + "</dl></div>")
    follow = f"""<section class="ticket follow-box" aria-labelledby="follow-title">
  <h2 id="follow-title">Follow {e(m['town'])}</h2>
  <p>A private page and a calendar feed for {e(m['town'])} and the towns next to it, updated every morning.</p>
  <p class="actions"><a class="btn" href="{e(alerts_url(t.get('id')))}">Follow {e(m['town'])}</a></p>
  <p class="ticket-links">{share}<a class="link-btn" href="/m/{m['id'][2:]}.ics" download="{e(m['id'][2:])}.ics">Add this meeting to my calendar</a></p>
</section>"""
    body = f"""
<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/towns">Towns</a></li><li><a href="{town_path(m['state'], m['town'])}">{e(m['town'])}</a></li><li><span aria-current="page">{e(meeting_board(m))}</span></li></ol></nav>
<h1 id="meeting-title" data-slop-ignore>{e(title)}</h1>
{ticket}
<h2 class="sr-only">On the {e(what)}</h2>
<ol class="meetings one">{meeting_html(ctx, m, show_town=False, lines_shown=20, full=True)}</ol>
{follow}
<p class="more-link"><a href="{town_path(m['state'], m['town'])}">Everything coming up in {e(m['town'])}</a></p>
</div>
"""
    desc = share_text(ctx, m, plain_say(first))
    if len(desc) > 200:
        desc = desc[:196].rsplit(" ", 1)[0] + "…"
    full_title = title + (f", {when_text(ctx, m)}" if m["date"] else "")
    return page(ctx, f"{full_title} | {SITE_NAME}", desc, body, f"/m/{m['id'][2:]}", noindex=True, og_title=full_title,
                source=f"{prov} {copy}")


def write(rel, text):
    path = SITE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    CLERKS.update(load_clerks())
    ctx = Ctx()
    pages = {
        "index.html": (build_index(ctx), "/"),
        "404.html": (build_404(ctx), None),
        "upcoming.html": (build_upcoming(ctx), "/upcoming"),
        "trending.html": (build_trending(ctx), "/trending"),
        "how-it-works.html": (build_how(ctx), "/how-it-works"),
        "privacy.html": (build_privacy(ctx), "/privacy"),
        "contact.html": (build_contact(ctx), "/contact"),
        "search.html": (build_search(ctx), "/search"),
        "watch.html": (build_watch(ctx), "/watch"),
        "alerts-for-groups.html": (build_watch(ctx, groups=True), "/alerts-for-groups"),
        "w.html": (build_viewer(ctx), None),
        "towns.html": (build_towns_index(ctx), "/towns"),
        "topics.html": (build_topics_index(ctx), "/topics"),
        "attorney-general.html": (build_ag(ctx), "/attorney-general"),
        "attorney-general/rulings.html": (build_ag_rulings(ctx), "/attorney-general/rulings"),
        "attorney-general/town-actions.html": (build_ag_actions(ctx), "/attorney-general/town-actions"),
        "attorney-general/law.html": (build_ag_law(ctx), "/attorney-general/law"),
        "bot.html": (build_bot(ctx), "/bot"),
    }
    ledger = build_data_center_ledger(ctx)
    if ledger:
        pages["attorney-general/data-centers.html"] = (ledger, "/attorney-general/data-centers")
    for rel, (target, default, mapping, title) in REDIRECTS.items():
        pages[rel] = (redirect_page(target, default, mapping, title), None)
    for tp in TOPIC_PAGES:
        pages[f"topics/{tp['slug']}.html"] = (build_topic_page(ctx, tp), f"/topics/{tp['slug']}")

    # Town pages: clear old ones first so renamed or removed towns (or unpublished states) don't linger.
    for d in SITE.iterdir():
        if d.is_dir() and re.fullmatch(r"[a-z]{2}", d.name) and d.name.upper() in STATE_NAMES:
            for f in d.glob("*.html"):
                f.unlink()
            if not any(d.iterdir()):
                d.rmdir()
    meeting_dir = SITE / "m"
    if meeting_dir.is_dir():
        for f in list(meeting_dir.glob("*.html")) + list(meeting_dir.glob("*.ics")):
            f.unlink()
    for m in group_meetings(ctx, upcoming_hits(ctx)):
        pages[f"m/{m['id'][2:]}.html"] = (build_meeting_page(ctx, m), None)
        pages[f"m/{m['id'][2:]}.ics"] = (meeting_ics(ctx, m), None)  # "Add to my calendar" on the meeting's page
    thin = 0
    for t in ctx.towns:
        html, is_thin = build_town_page(ctx, t)
        thin += is_thin
        pages[f"{t['state'].lower()}/{t['slug']}.html"] = (html, None if is_thin else town_path(t["state"], t["town"]))

    for rel, (html, _) in pages.items():
        write(rel, html)
    for old in (SITE / "maps").glob("*.svg") if (SITE / "maps").is_dir() else []:
        old.unlink()  # the dot maps are gone from the pages
    write("sitemap.xml", build_sitemap([p for _, p in pages.values() if p]))
    write("robots.txt", build_robots())
    write("data/towns.json", town_index_json(ctx))
    (DATA / "search" / "titles.json").write_text(json.dumps(search_titles(ctx), ensure_ascii=False, sort_keys=True, indent=0) + "\n")
    (DATA / "search" / "pages.json").write_text(json.dumps(search_pages(ctx), ensure_ascii=False, sort_keys=True, indent=0) + "\n")
    write("data/lines.json", lines_json(ctx))
    write("data/trending.json", trending_json(*trending_stories(ctx)))
    stale = SITE / "manifest.txt"
    if stale.exists():
        stale.unlink()

    print(f"built {len(pages)} pages ({len(ctx.towns)} town pages, {thin} thin/noindex), "
          f"{len(ctx.tracker.get('items', []))} tracker rows, {len(ctx.hits)} agenda hits, "
          f"{len(ctx.ag)} AG rows, {len(ctx.points)} map points, town health {'present' if ctx.health is not None else 'absent'}, "
          f"{len(BRIEFS)} written briefs shown ({ctx.briefs_dropped} not verified)")


if __name__ == "__main__":
    main()
