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
  /               what's coming up in your town: town box, the next 3 meetings, map
  /upcoming       every upcoming meeting with items on our topics
  /<st>/<town>    one town: the next 7 days, what's coming up, earlier meetings, nearby towns, boards read
  /watch          set up alerts (an "alert list"), one question per screen; /w/<key> shows one
  /search         full-text search over every agenda (site/search.js fills the results)
  /how-it-works   coverage, timing, the Attorney General record, the crawler, privacy, contact
"""

import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE = ROOT / "site"
GEO = ROOT / "geo"
# Canonical base for links, sitemaps and canonical tags. Switches to https://agendaahead.com once the domain is live.
BASE_URL = "https://351watch-sulmusic2-4637s-projects.vercel.app"
# The product name, used everywhere it appears (titles, wordmark, copy). A new name is being chosen;
# change it here. The wordmark in styles.css (.brand) fits any short name.
SITE_NAME = "Agenda Ahead"
# The crawler's name and the User-Agent it sends (shown on How it works, #crawler).
BOT_NAME = "AgendaAheadBot"
BOT_UA = "AgendaAheadBot/0.1 (+https://agendaahead.com/bot)"

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
    "40b_comprehensive_permit": "Affordable housing",
    "wireless_telecom": "Cell towers",
    "wetlands_filing": "Wetlands filings",
}
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
}
TOPIC_ORDER = list(TOPIC_LABELS)
DEFAULT_TOPICS = ["solar", "battery_storage", "data_center", "moratorium", "clean_energy_siting"]
HERO_TOPICS = set(DEFAULT_TOPICS)

BOARD_NAMES = {
    "planning_board": "Planning board",
    "zoning_board_of_appeals": "Zoning board of appeals",
    "conservation_commission": "Conservation commission",
    "select_board": "Select board or city council",
    "town_meeting": "Town meeting",
}

REASON_LABELS = {
    "bot_challenge": "The town’s website blocks programs like ours",
    "waf_block": "The town’s website blocks programs like ours",
    "agendas_stale_or_undated": "We found no current, dated agendas on the town’s website",
    "js_only": "Our reader can’t open the town’s agenda page yet",
    "robots_disallow_site": "The town’s website asks programs like ours not to visit",
    "no_adapter": "Our reader doesn’t work with the town’s agenda system yet",
    "no_agenda_listing_found": "We couldn’t find where the town posts agendas",
    "vendor_blocked": "The company that hosts the town’s agendas blocks programs like ours",
    "vendor_robots_disallow": "The company that hosts the town’s agendas asks programs like ours not to visit",
    "crawl_delay_exceeds_cap": "The town’s website asks us to wait longer between visits than we can yet",
}

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
]
TOPIC_PAGE_BY_KEY = {tp["key"]: tp for tp in TOPIC_PAGES}

TRACER_LANE = "2022-06-02"
e = escape


# ---------------------------------------------------------------- helpers

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
            item["summary"] = (item.get("summary") or "").replace("351 Watch", SITE_NAME)
        self.census = load("ma_census_summary.json", {})
        self.leadtime = load("leadtime_ma_all.json", {})
        self.ag = load("ag_decisions.json", [])
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
        self.hits = [h for h in self.hits_doc["hits"] if h.get("state", "MA") in self.states]
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
        for h in self.hits:
            if h.get("first_seen") and (h["state"] not in self.first_sweep or h["first_seen"] < self.first_sweep[h["state"]]):
                self.first_sweep[h["state"]] = h["first_seen"]
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

    def is_new(self, h):
        """First seen in the 48 hours before this data was generated, and not by a state's first sweep
        (a day after its first finding: everything the first sweep finds was already there)."""
        seen = h.get("first_seen") or ""
        start = self.first_sweep.get(h["state"])
        if not (seen and start) or seen < self.new_since:
            return False
        after = datetime.fromisoformat(start.replace("Z", "+00:00")) + timedelta(hours=24)
        return datetime.fromisoformat(seen.replace("Z", "+00:00")) > after

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
    ("/towns", "Towns"),
    ("/topics", "Topics"),
    ("/search", "Search"),
    ("/watch", "Get alerts"),
]
FOOTER_LINKS = [
    ("/how-it-works", "How it works"),
    ("/upcoming", "Everything coming up"),
    ("/attorney-general", "State rulings on moratoriums"),
    ("/pricing", "What’s free"),
    ("/how-it-works#privacy", "Privacy"),
    ("/how-it-works#crawler", "Our crawler"),
    ("/how-it-works#contact", "Send a correction"),
]
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctitle%3E"
           + quote(SITE_NAME) + "%3C/title%3E%3Crect width='32' height='32' rx='4' fill='%23eef1ed'/%3E%3Ccircle cx='9' cy='11' "
           "r='3' fill='%23a9b3ac'/%3E%3Ccircle cx='19' cy='9' r='3' fill='%23a9b3ac'/%3E%3Ccircle cx='14' cy='20' r='4.5' "
           "fill='%237a2c80'/%3E%3Ccircle cx='24' cy='22' r='3' fill='%23a9b3ac'/%3E%3C/svg%3E")


def nav_section(path):
    """Which nav item a path belongs to."""
    if path in ("/towns",) or re.fullmatch(r"/[a-z]{2}/.+", path or ""):
        return "/towns"
    if path in ("/watch", "/w"):
        return "/watch"
    if path.startswith("/topics"):
        return "/topics"
    return path


def page(ctx, title, description, body, path, scripts=(), noindex=False, head=""):
    current = nav_section(path)
    nav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>' for href, label in NAV
    )
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    canonical = "" if noindex else f'<link rel="canonical" href="{BASE_URL}{"" if path == "/" else path}">\n'
    script_tags = "".join(f'<script src="{s}" defer></script>\n' for s in ("/app.js", *scripts))
    footer_links = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in FOOTER_LINKS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{robots}{canonical}<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE_NAME)}">
<meta name="color-scheme" content="light dark">
<link rel="preload" href="/fonts/barlow-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/barlow-semicondensed-bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<link rel="icon" href="{FAVICON}">
{head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span>{e(SITE_NAME)}</a>
  <nav class="top" aria-label="Main"><ul>{nav}</ul></nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>{SITE_NAME} reads the agendas towns post online. It is not legal advice. Check dates with the town clerk.</p>
  <ul class="foot-links">{footer_links}</ul>
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
        return "town meeting"
    b = re.sub(r"\s*\([^)]*\)", "", h.get("board") or "")
    b = re.sub(r"\s+[-–]\s+.*$", "", b)
    b = re.sub(r"^The\s+", "", b)
    b = re.sub(r"\s+Meetings?$", "", b)
    if b.isupper():
        b = b.title()
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
    for m in NAME_LLC.finditer(text):
        name = LEAD_WORDS.sub("", LEAD_JUNK.sub("", m.group(1))).strip(" ,")
        words = re.findall(r"[A-Za-z][\w'’-]*", name)
        if words and not all(w.lower() in GENERIC | {"llc", "inc"} for w in words) and len(name) <= 60:
            return name
    for m in NAME_PROJECT.finditer(text):
        name = LEAD_JUNK.sub("", m.group(1)).strip(" ,")
        words = [re.sub(r"[^a-z0-9-]", "", w.lower()).strip("-") for w in name.split()]
        if any(w in NAME_STOP for w in words):  # agenda headings, not a project's name
            continue
        if sum(1 for w in words if w and w not in GENERIC and not w.isdigit()) >= 1 and len(name) <= 50:
            return name
    return ""


def find_address(text):
    m = ADDRESS.search(text)
    if not m:
        return ""
    addr = m.group(1).rstrip(".")
    return re.sub(r"^0\s+", "", addr)  # "0 Wareham Street" is a parcel with no number


def agenda_line(h):
    """One plain line for one flagged passage."""
    text = " ".join((h.get("snippet") or "").split())
    topics = short_topics(h.get("topics", []))
    actions = []
    for pattern, words in ACTIONS:
        if re.search(pattern, text, re.I) and words not in actions:
            actions.append(words)
    if h.get("source") == "massdep_wetlands" and "wetlands permit request" not in actions:
        actions.insert(0, "wetlands permit request")
    generic = ("bylaw change", "ordinance", "rezoning")
    if any(a not in generic + ("public hearing",) for a in actions):  # name the specific action, not the vehicle
        actions = [a for a in actions if a not in generic]
    if len(actions) > 1:
        actions = [a for a in actions if a != "permitting"]
    hearing = "public hearing" in actions and len(actions) > 1
    actions = [a for a in actions if a != "public hearing"] if hearing else actions
    if actions and actions[0] in ("bylaw change", "ordinance", "rezoning"):
        singular = {"data centers": "data center", "cell towers": "cell tower", "clean-energy permit rules": "clean-energy permit"}
        subjects = [singular.get(w, w) for w in re.split(r", | and ", topics) if w not in ("zoning change", "")]
        subject = join_and(subjects) or "zoning"
        actions = [f"{subject} {actions[0]}" if actions[0] != "rezoning" else "rezoning"] + actions[1:2]
        topics = ""
    action = join_and(actions[:2])
    if action == "moratorium":
        subjects = [w for w in re.split(r", | and ", topics) if w not in ("moratorium", "zoning change", "")]
        action = f"pause on {join_and(subjects)} (moratorium)" if subjects else "moratorium (a temporary pause)"
    if hearing:
        action = f"hearing on a {action}" if action.startswith(("pause", "moratorium")) else f"{action} hearing"
    name, addr = find_name(text), find_address(text)
    cont = " (continued)" if CONTINUED.search(text) else ""
    named_topic = re.search(r"solar|data center|battery|storage", name, re.I)
    if name and action:
        extra = (f" for {topics}" if topics and not named_topic and "moratorium" not in action
                 and topics.split()[0] not in action else "")
        line = f"{name}: {action}{extra}" + (f", {addr}" if addr else "")
    elif action and addr:
        line = f"{action} for {topics} at {addr}" if topics and "moratorium" not in action else f"{action}, {addr}"
    elif action:
        line = f"{action} for {topics}" if topics and "moratorium" not in action else action
    elif name:
        line = (name if named_topic else f"{name} ({topics})") + (f", {addr}" if addr else "")
    elif addr:
        line = f"{topics} at {addr}"
    else:
        line = f"mentions {topics}"
    line = line + cont
    return line[:1].upper() + line[1:]


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
        return "Town meeting warrant"
    return m["board"][:1].upper() + m["board"][1:]


def group_meetings(ctx, hits):
    """Hits grouped by meeting (town, board, date), in the order given. A meeting keeps one line per
    distinct agenda line (their quotes merged) and one link per agenda document."""
    out = {}
    for h in hits:
        date_ = (h.get("meeting_date") or "")[:10]
        key = (h["state"], h["town"], h.get("source") == "massdep_wetlands", h.get("board_key") or board_label(h), date_)
        m = out.get(key)
        if m is None:
            m = out[key] = {"id": "m-" + slugify(f"{h['town']}-{board_label(h)}-{date_ or 'warrant'}"),
                            "state": h["state"], "town": h["town"], "board": board_label(h), "board_key": h.get("board_key"),
                            "date": date_, "source": h.get("source"), "lines": {}, "docs": [], "found": h.get("first_seen") or "",
                            "topics": []}
        line = agenda_line(h)
        entry = m["lines"].setdefault(line, {"quotes": [], "new": False, "topics": []})
        entry["topics"] += [t for t in h.get("topics", []) if t not in entry["topics"]]
        q = clean_quote(h.get("snippet"))
        if q and q not in entry["quotes"]:
            entry["quotes"].append(q)
        entry["new"] = entry["new"] or ctx.is_new(h)
        if h["source_url"] not in [d["url"] for d in m["docs"]]:
            m["docs"].append({"url": h["source_url"], "pdf": is_pdf(h)})
        if h.get("first_seen") and (not m["found"] or h["first_seen"] < m["found"]):
            m["found"] = h["first_seen"]
        m["topics"] += [t for t in h.get("topics", []) if t not in m["topics"]]
    for m in out.values():
        m["lines"] = tidy_lines(m["lines"])
    return list(out.values())


def merge_entry(into, entry):
    into["quotes"] += [q for q in entry["quotes"] if q not in into["quotes"]]
    into["topics"] += [t for t in entry["topics"] if t not in into["topics"]]
    into["new"] = into["new"] or entry["new"]


def tidy_lines(lines):
    """One meeting's lines without repeats: a line contained in a longer one joins it, and the
    "Mentions …" lines become one line at the end, naming only topics no other line names."""
    def core(text):
        return text.lower().replace(" (continued)", "")
    named = {k: v for k, v in lines.items() if not k.startswith("Mentions ")}
    for short in sorted(named, key=len):
        longer = next((k for k in named if k != short and len(k) > len(short) and core(short) in core(k)), None)
        if longer:
            merge_entry(named[longer], named.pop(short))
    mentions = [v for k, v in lines.items() if k.startswith("Mentions ")]
    if not mentions:
        return named
    merged = {"quotes": [], "new": False, "topics": []}
    for v in mentions:
        merge_entry(merged, v)
    said = " ".join(core(k) for k in named)
    left = [t for t in ordered_topics(merged["topics"]) if short_topics([t]).lower().rstrip("s") not in said]
    if left:
        named[f"{'Also mentions' if named else 'Mentions'} {short_topics(left)}"] = merged
    return named


def found_text(ctx, m):
    """"We found it Oct 10, 3 days before the meeting." from the first time we saw the agenda."""
    if not m["found"]:
        return ""
    found = m["found"][:10]
    text = f"We found it {datetime.strptime(found, '%Y-%m-%d').strftime('%b %-d')}"
    if m["date"] and m["date"] > found:
        days = (datetime.strptime(m["date"], "%Y-%m-%d") - datetime.strptime(found, "%Y-%m-%d")).days
        text += f", {plural(days, 'day')} before the meeting"
    return text + "."


def meeting_html(ctx, m, show_town=True, lines_shown=4):
    """One meeting: town, board and day, then one plain line per item (agenda wording on request),
    then one link per agenda document and when we found it."""
    town = ""
    if show_town:
        st = f", {m['state']}" if m["state"] != "MA" else ""
        town = f'<span class="meet-town">{ctx.town_link(m["state"], m["town"])}{e(st)}</span>'
    day = (f'<span class="meet-day"><time datetime="{m["date"]}">{day_label(m["date"], ctx)}</time></span>'
           if m["date"] else "")
    dep = m["source"] == "massdep_wetlands"
    source = "the state filing" if dep else ("the warrant" if m["board_key"] == "town_meeting" else "the agenda")

    def line(text, entry):
        new = '<span class="badge-new">New</span> ' if entry["new"] else ""
        quotes = "".join(f'<blockquote class="item-quote">{e(q)}</blockquote>' for q in entry["quotes"][:3])
        words = (f'<details class="item-words"><summary>See the agenda wording</summary>'
                 f'<p class="item-from">Quoted from {source}:</p>{quotes}</details>') if quotes else ""
        return f'<li class="line"><p class="line-say">{new}{e(text)}</p>{words}</li>'

    entries = list(m["lines"].items())
    lines = "".join(line(t, en) for t, en in entries[:lines_shown])
    if entries[lines_shown:]:
        lines += (f'<li class="line-more"><details class="more"><summary>{plural(len(entries) - lines_shown, "more item")}</summary>'
                  f'<ul class="lines">{"".join(line(t, en) for t, en in entries[lines_shown:])}</ul></details></li>')
    what = "filing" if dep else ("warrant" if m["board_key"] == "town_meeting" else "agenda")
    where = f"{m['town']} {meeting_board(m)}, {fmt_date(m['date']) or 'no date'}"
    links = []
    for i, d in enumerate(m["docs"]):
        name = f"Open the {what}" if i == 0 else f"Another version of the {what}"
        links.append(f'<a class="item-link" href="{e(d["url"])}" rel="nofollow noopener" target="_blank">{name}'
                     f'{" (PDF)" if d["pdf"] else ""}<span class="sr-only">: {e(where)}</span></a>')
    found = found_text(ctx, m)
    return f"""<li class="meeting" id="{m['id']}">
  <h3 class="meet-head" data-slop-ignore>{town} <span class="meet-board">{e(meeting_board(m))}</span> {day}</h3>
  <ul class="lines">{lines}</ul>
  <p class="meet-src">{" ".join(links)}{f' <span class="meet-found">{found}</span>' if found else ""}</p>
</li>"""


def meeting_list(ctx, meetings, show_town=True, shown=3, more="Show more", empty=""):
    """The first few meetings, the rest behind one "Show more"."""
    if not meetings:
        return f'<p class="empty">{empty}</p>' if empty else ""
    html = f'<ol class="meetings">{"".join(meeting_html(ctx, m, show_town) for m in meetings[:shown])}</ol>'
    rest = meetings[shown:]
    if rest:
        html += (f'<details class="more"><summary>{more} ({len(rest)})</summary>'
                 f'<ol class="meetings">{"".join(meeting_html(ctx, m, show_town) for m in rest)}</ol></details>')
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
        rows.append(
            f"""<tr data-group="{group}" data-topic="{e(topic.lower())}" data-county="{e(item.get('county', ''))}">
  <td class="town"><b>{ctx.town_link(item.get('state', 'MA'), item['town'])}</b><small>{e(item.get('county', ''))} County</small></td>
  <td>{e(item.get('action', ''))}<br><small>{e(topic)}</small></td>
  <td><span class="badge {group}">{e(item.get('status', ''))}</span></td>
  <td class="when">{fmt_date(item.get('key_date'))}<small>{e(item.get('date_label', ''))}</small></td>
  <td class="col-summary"><p class="summary">{e(item.get('summary', ''))}</p>{sources_html(item.get('sources', []))}</td>
</tr>"""
        )
    return "\n".join(rows)


TRACKER_HEAD = ('<thead><tr><th scope="col">Town</th><th scope="col">Action</th><th scope="col">Status</th>'
                '<th scope="col">Date</th><th scope="col" class="col-summary">What happened</th></tr></thead>')


def tracker_table(ctx, items, table_id=None):
    tid = f' id="{table_id}"' if table_id else ""
    return f'<div class="table-wrap"><table class="stack"{tid}>{TRACKER_HEAD}<tbody>{tracker_rows(ctx, items)}</tbody></table></div>'


def ag_row(ctx, r, filters=False):
    year = (r.get("decision_date") or "")[:4]
    attrs = (f' data-outcome="{e(r.get("outcome", ""))}" data-bylaw="{e(r.get("bylaw_type", ""))}"'
             f' data-tech="{e(r.get("technology", ""))}" data-year="{year}"') if filters else ""
    case = f", case {e(str(r['case_number']))}" if r.get("case_number") else ""
    label = "Decision letter" if r.get("record_type") == "ag_decision" else "Source"
    letter = (f'<a href="{e(r["letter_url"])}" rel="nofollow noopener" target="_blank">{label}{case}</a>'
              if r.get("letter_url") else "")
    town = ag_town(r.get("town"))
    city = " (city)" if "(city)" in (r.get("town") or "") else ""
    return f"""<tr{attrs}>
  <td class="when">{fmt_date(r.get('decision_date'))}</td>
  <td class="town"><b>{ctx.town_link('MA', town)}{e(city)}</b><small>{e(r.get('article', ''))}</small></td>
  <td>{e(r.get('bylaw_type', '').capitalize())}<br><small>{e(r.get('technology', ''))}</small></td>
  <td><span class="badge {outcome_class(r.get('outcome'))}">{e((r.get('outcome') or '').capitalize())}</span></td>
  <td class="col-summary"><p class="summary">{e(r.get('summary', ''))}</p>{letter}</td>
</tr>"""


def ag_table(ctx, rows, table_id=None, filters=False):
    tid = f' id="{table_id}"' if table_id else ""
    group = f' data-filter-group="{table_id}"' if filters else ""
    body = "\n".join(ag_row(ctx, r, filters) for r in sorted(rows, key=lambda r: r.get("decision_date") or "", reverse=True))
    return f"""<div class="table-wrap"><table class="stack"{tid}{group}>
  <thead><tr><th scope="col">Decided</th><th scope="col">Town and article</th><th scope="col">Type</th><th scope="col">Outcome</th><th scope="col" class="col-summary">Summary and source</th></tr></thead>
  <tbody>
{body}
  </tbody></table></div>"""


def ag_moratorium_record(ag, since="2024-01-01"):
    """Solar/BESS moratorium articles the Attorney General ruled on since `since`."""
    rows = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") == "moratorium"
            and (r.get("decision_date") or "") >= since and r.get("outcome") in ("approved", "disapproved")]
    return {
        "rows": sorted(rows, key=lambda r: r["decision_date"], reverse=True),
        "total": sum(ag_articles(r) for r in rows),
        "disapproved": sum(ag_articles(r) for r in rows if r["outcome"] == "disapproved"),
        "towns": len({r["town"] for r in rows}),
    }


def topic_counts(ctx, key, state=None):
    hits = [h for h in ctx.hits if key in h.get("topics", []) and (state is None or h["state"] == state)]
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
    opts = "".join(f'<option value="{e(t["town"])}{", " + t["state"] if multi else ""}" data-href="{town_path(t["state"], t["town"])}"></option>'
                   for t in ctx.towns)
    return f'<datalist id="town-names">{opts}</datalist>'


def town_box(ctx, label="Type your town", button="Show me", examples=True):
    eg = ""
    if examples:
        picks = [t for t in ("MA:Carver", "MA:Amherst", "NY:Clay") if t in ctx.town_by_id][:3]
        links = [f'<a href="{town_path(*p.split(":", 1))}">{e(p.split(":", 1)[1])}{", " + p[:2] if p[:2] != "MA" else ""}</a>' for p in picks]
        eg = (f'<p class="eg">Or try {", ".join(links[:-1])} or {links[-1]}.</p>' if len(links) > 1
              else (f'<p class="eg">Or try {links[0]}.</p>' if links else ""))
    return f"""<form class="townbox" action="/towns" method="get" role="search" data-town-form>
  <label for="town-q">{label}</label>
  <div class="field-row"><input id="town-q" name="q" type="text" list="town-names" autocomplete="off" autocapitalize="words" spellcheck="false" required>
  <button class="btn" type="submit">{button}</button></div>
  <p class="field-error" id="town-q-error" role="alert" hidden></p>
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
  <a href="/towns" class="map-link"><picture><source srcset="/maps/{m.group}-dark.svg" media="(prefers-color-scheme: dark)"><img src="/maps/{m.group}.svg" alt="Map of {e(m.name())} towns. Purple dots are towns with items coming up." width="{m.w}" height="{m.h}"></picture></a>
  <figcaption>Purple dots: towns with items coming up. <a href="/towns">All towns</a></figcaption>
</figure>"""


def build_index(ctx):
    hero = upcoming_hits(ctx, lambda h: HERO_TOPICS & set(h.get("topics", [])))
    meetings = group_meetings(ctx, hero)
    n_all = len(group_meetings(ctx, upcoming_hits(ctx)))
    monitored = sum(m for _, m, _ in ctx.coverage())
    states = join_and(ctx.states)
    next_html = (f'<ol class="meetings">{"".join(meeting_html(ctx, m) for m in meetings[:3])}</ol>' if meetings
                 else '<p class="empty">Nothing on upcoming agendas right now. We check every morning.</p>')
    body = f"""
<div class="wrap home">
<section class="home-hero" aria-labelledby="hero-title">
  <h1 id="hero-title">See what your town is about to decide</h1>
  <p class="lead">We check {monitored:,} towns’ agendas in {e(states)} every morning for solar, battery storage and data centers.</p>
  {town_box(ctx)}
</section>
<section class="next" aria-labelledby="next-title">
  <h2 id="next-title">Coming up soon</h2>
  {next_html}
  <p class="more-link"><a href="/upcoming">See all upcoming ({n_all} meetings)</a></p>
</section>
{home_map(ctx)}
</div>
"""
    return page(
        ctx,
        f"See what your town is about to decide | {SITE_NAME}",
        f"Solar, battery storage and data center items on upcoming town agendas in {states}. {SITE_NAME} checks "
        f"{monitored:,} towns every morning. Free alerts.",
        body, "/",
    )


def build_upcoming(ctx):
    meetings = group_meetings(ctx, upcoming_hits(ctx))
    week_end = (datetime.strptime(ctx.today, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    soon = [m for m in meetings if m["date"] <= week_end]
    later = [m for m in meetings if m["date"] > week_end]
    towns = len({(m["state"], m["town"]) for m in meetings})
    body = f"""
<div class="wrap narrow">
<section class="page-head" aria-labelledby="up-title">
  <h1 id="up-title">Coming up</h1>
  <p class="lead">{plural(len(meetings), "meeting")} in {plural(towns, "town")} have items on our topics. Checked {ctx.checked}.</p>
  <p class="actions"><a class="btn" href="/watch">Get these by email</a></p>
</section>
<section aria-labelledby="soon-title">
  <h2 id="soon-title">Next 7 days</h2>
  {meeting_list(ctx, soon, shown=20, empty="Nothing in the next 7 days.")}
</section>
<section aria-labelledby="later-title">
  <h2 id="later-title">Later</h2>
  {meeting_list(ctx, later, shown=10, more="Show later meetings", empty="Nothing later yet.")}
</section>
<p class="more-link"><a href="/search?upcoming=1">Search these agendas</a></p>
</div>
"""
    return page(ctx, f"Coming up at town meetings | {SITE_NAME}",
                f"Every upcoming town meeting in {join_and(ctx.states)} with solar, battery storage, data center, zoning or "
                "housing items, and a link to each agenda.",
                body, "/upcoming")


# ---------------------------------------------------------------- town pages

def board_list(ctx, t):
    found = set(t.get("boards_found", []))
    evidence = t.get("board_evidence", {}) or {}
    rows = []
    for key, name in BOARD_NAMES.items():
        if key == "town_meeting" and not t.get("has_town_meeting") and key not in found:
            continue
        ev = evidence.get(key) or {}
        if key in found:
            latest = fmt_date(ev.get("latest"))
            status = "read daily" + (f", latest agenda {latest}" if latest else "")
            if ev.get("url"):
                status += f' (<a href="{e(ev["url"])}" rel="nofollow noopener" target="_blank">listing<span class="sr-only"> for {e(name.lower())}</span></a>)'
        elif t["monitored"]:
            status = "no agendas found online"
        else:
            status = "not read yet"
        rows.append(f"<li><b>{e(name)}</b>: {status}</li>")
    return f'<ul class="plain boards">{"".join(rows)}</ul>'


def rules_html(ctx, tracked, ag_rows, town):
    parts = []
    for i in sorted(tracked, key=lambda i: i.get("key_date") or "", reverse=True):
        parts.append(f"""<li><p><b>{e(i.get('action', ''))}</b>, {e(i.get('topic', '').lower())}. {e(i.get('status', ''))}, {fmt_date(i.get('key_date'))}.</p>
<p class="small">{e(i.get('summary', ''))}</p>{sources_html(i.get('sources', []))}</li>""")
    for r in sorted(ag_rows, key=lambda r: r.get("decision_date") or "", reverse=True):
        case = f", case {e(str(r['case_number']))}" if r.get("case_number") else ""
        letter = (f'<a href="{e(r["letter_url"])}" rel="nofollow noopener" target="_blank">'
                  f'{"Decision letter" if r.get("record_type") == "ag_decision" else "Source"}{case}</a>' if r.get("letter_url") else "")
        parts.append(f"""<li><p><b>Attorney General: {e((r.get('outcome') or '').lower())}</b>, {fmt_date(r.get('decision_date'))}. {e(r.get('article', ''))}, {e(r.get('bylaw_type', ''))}.</p>
<p class="small">{e(r.get('summary', ''))} {letter}</p></li>""")
    return f'<ul class="plain rules">{"".join(parts)}</ul>'


def next_meetings(ctx, t, meetings, days=6):
    """Meetings in the next `days` days: the ones with items, plus any other board whose next agenda
    is already posted (it has nothing on our topics). [(date, board, n items, anchor or None)]"""
    end = (datetime.strptime(ctx.today, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
    cols = {}
    for m in meetings:
        if m["date"] and m["date"] <= end:
            cols.setdefault((m["date"], m["board_key"]), (m["date"], meeting_board(m), len(m["lines"]), m["id"]))
    for key, ev in (t.get("board_evidence") or {}).items():
        latest = (ev or {}).get("latest") or "" if isinstance(ev, dict) else ""
        if ctx.today <= latest <= end and (latest, key) not in cols:
            cols[(latest, key)] = (latest, ev.get("board") or BOARD_NAMES.get(key) or "Town board", 0, None)
    return sorted(cols.values(), key=lambda c: (c[0], -c[2], c[1]))


def next_agenda(ctx, t):
    """(date, board) of the soonest posted agenda for a future meeting, if any."""
    found = [((ev or {}).get("latest"), (ev or {}).get("board") or BOARD_NAMES.get(k))
             for k, ev in (t.get("board_evidence") or {}).items() if isinstance(ev, dict)]
    found = sorted(f for f in found if f[0] and f[0] >= ctx.today and f[1])
    return found[0] if found else None


def week_strip(ctx, cols):
    if not cols:
        return ""
    cells = []
    for d, board, n, anchor in cols[:6]:
        inner = (f'<span class="wk-day">{day_label(d, ctx)}</span><span class="wk-board">{e(board)}</span>'
                 f'<span class="wk-n{" hot" if n else ""}">{plural(n, "item") if n else "Nothing on our topics"}</span>')
        cells.append(f'<li><a href="#{anchor}">{inner}</a></li>' if anchor else f"<li><div>{inner}</div></li>")
    return f'<div class="week" role="region" aria-label="Meetings in the next 7 days" tabindex="0"><p class="week-title">Next 7 days</p><ul class="week-days">{"".join(cells)}</ul></div>'


def build_town_page(ctx, t):
    tid, state, town = t["id"], t["state"], t["town"]
    hits = ctx.hits_by_town.get(tid, [])
    upcoming, past, undated = split_hits(ctx, hits)
    up_m, past_m, und_m = group_meetings(ctx, upcoming), group_meetings(ctx, past), group_meetings(ctx, undated)
    tracked = ctx.tracker_by_town.get(tid, [])
    ag_rows = ctx.ag_by_town.get(tid, []) if state == "MA" else []
    thin = not (hits or tracked or ag_rows)
    state_name = STATE_NAMES.get(state, state)
    kind = "City" if t.get("kind") == "city" else "Town"
    county = f"{t['county']} County, " if t.get("county") else ""
    health = (ctx.health or {}).get(tid)

    # What's coming up: the one job of the page. The alert button sits right above the list.
    alert_btn = f'<a class="btn" href="{e(alerts_url(tid))}">Get these by email</a>'
    request = ""
    if t["monitored"]:
        if up_m:
            lead = week_strip(ctx, next_meetings(ctx, t, up_m))
            listing = meeting_list(ctx, up_m, show_town=False, shown=3, more="More coming up")
        else:
            nxt = next_agenda(ctx, t)
            lead = ""
            listing = ('<p class="empty">Nothing on the agenda about these topics right now.'
                       + (f" Next {e(nxt[1])} meeting: {day_label(nxt[0], ctx)}." if nxt else "")
                       + " We check every morning.</p>")
        coming = f"""<section aria-labelledby="upcoming-title">
  <div class="sec-head"><h2 id="upcoming-title">Coming up in <span data-slop-ignore>{e(town)}</span></h2>{alert_btn}</div>
  {lead}
  {listing}
  <p class="checked">Checked {ctx.checked_day}.</p>
</section>"""
    else:
        reason = REASON_LABELS.get(t.get("reason_code"), "We can’t read this town’s agendas automatically yet")
        coming = f"""<section aria-labelledby="upcoming-title">
  <h2 id="upcoming-title">We can’t read {e(town)}’s agendas yet</h2>
  <p class="status">{e(reason)}.</p>
  {meeting_list(ctx, up_m, show_town=False, shown=3, more="More coming up")}
  <p class="actions"><a class="btn" href="{e(alerts_url(tid))}">Get alerts for the towns next to {e(town)}</a></p>
</section>"""
        request = (f'<div class="request" data-request-town="{e(tid)}" data-town-name="{e(town)}, {state}">'
                   f'<p>Want {e(town)} covered? We’ll ask the town for access.</p>'
                   f'<button type="button" class="btn quiet">Request {e(town)}</button>'
                   f'<p class="form-status" role="status" aria-live="polite"></p></div>')

    # Everything else, one click away.
    more = []
    if past_m:
        more.append(f"""<details class="disclose"><summary>Earlier meetings ({len(past_m)})</summary>
{meeting_list(ctx, past_m, show_town=False, shown=5, more="Show older")}</details>""")
    if und_m:
        more.append(f"""<details class="disclose"><summary>Town meeting warrants ({len(und_m)})</summary>
{meeting_list(ctx, und_m, show_town=False, shown=5)}</details>""")
    m = ctx.maps.get(map_group(state))
    if m and m.ok and tid in m.xy:
        x, y = m.xy[tid]
        listed = ctx.neighbors.get(tid)
        near_ids = [(n, None) for n in listed] if listed else m.nearby(ctx, tid)
        near = []
        for other, _ in near_ids:
            o = ctx.town_by_id[other]
            n_up = sum(1 for h in ctx.hits_by_town.get(other, []) if ctx.is_upcoming(h))
            note = (f"{n_up} coming up" if n_up else ("nothing coming up" if o["monitored"] else "not read yet"))
            st = f", {o['state']}" if o["state"] != state else ""
            near.append(f'<li><a href="{town_path(o["state"], o["town"])}">{e(o["town"])}{st}</a> <span class="{"n hot" if n_up else "n"}">{note}</span></li>')
        head = f"Towns next to {e(town)}" if listed else f"Towns near {e(town)}"
        more.append(f"""<details class="disclose"><summary>{head}</summary>
<div class="near-wrap"><ul class="plain near">{''.join(near)}</ul>
<figure class="locator"><div class="locator-map">
  <picture><source srcset="/maps/{m.group}-dark.svg" media="(prefers-color-scheme: dark)"><img src="/maps/{m.group}.svg" alt="" width="{m.w}" height="{m.h}" loading="lazy"></picture>
  <svg viewBox="0 0 {m.w} {m.h}" aria-hidden="true" focusable="false"><circle class="here" cx="{x}" cy="{y}" r="{m.r * 2.2:.1f}"/></svg>
</div><figcaption>{e(town)} is the ringed dot. Purple dots have items coming up.</figcaption></figure></div></details>""")
    sources = []
    for p in t.get("platforms") or []:
        name = PLATFORM_NAMES.get(p, p).format(kind=kind.lower())
        if name not in sources:
            sources.append(name)
    src = f"<p>{town} posts agendas on {e(join_and(sources))}.</p>" if sources and t["monitored"] else ""
    crawl = ""
    if health:
        fails = health.get("consecutive_failures") or 0
        crawl = (f'<p class="small">Last read: {fmt_date(health.get("last_success")) or "none yet"}'
                 f'{f"; the last {fails} tries failed" if fails else ""}.</p>')
    website = (f'<p><a href="{e(t["website"])}" rel="nofollow noopener" target="_blank">{kind} website</a></p>'
               if t.get("website") else "")
    more.append(f"""<details class="disclose"><summary>Where these agendas come from</summary>
{src}{board_list(ctx, t)}{crawl}{website}<p class="small"><a href="/how-it-works#gaps">Why some towns can’t be read</a></p></details>""")
    if tracked or ag_rows:
        more.append(f"""<details class="disclose"><summary>Bylaws and state rulings ({len(tracked) + len(ag_rows)})</summary>
{rules_html(ctx, tracked, ag_rows, town)}<p class="small"><a href="/attorney-general">All Massachusetts rulings</a></p></details>""")
    if t["monitored"]:
        more.append(f'<p class="more-link"><a href="/search?town={quote(tid, safe="")}">Search {e(town)}’s agendas</a></p>')

    body = f"""
<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/towns">Towns</a></li><li><a href="/towns#{state.lower()}">{e(state_name)}</a></li><li><span aria-current="page">{e(town)}</span></li></ol></nav>
<h1 id="town-title" class="town-title">{e(town)}</h1>
<p class="place">{kind} in {e(county)}{e(state_name)}</p>
{coming}
{request}
<div class="disclosures">{''.join(more)}</div>
</div>
"""
    title = f"{town}, {state} town agendas: solar and battery storage | {SITE_NAME}"
    if len(title) > 70:
        title = f"{town}, {state}: solar and battery storage on agendas | {SITE_NAME}"
    if len(title) > 70:
        title = f"{town}, {state}: solar and battery storage | {SITE_NAME}"
    if hits:
        desc = (f"What's coming up in {town}, {state_name}: {plural(len(upcoming), 'item')} for upcoming meetings on solar, "
                f"battery storage, data centers and zoning, with a link to each agenda.")
    elif t["monitored"]:
        desc = (f"{town}, {state_name}: {SITE_NAME} reads its town board agendas every day and lists solar, battery storage, "
                "data center and zoning items.")
    else:
        desc = f"{town}, {state_name}: {SITE_NAME} can't read its agendas automatically yet. See nearby towns and get alerts."
    return page(ctx, title, desc, body, town_path(state, town), noindex=thin), thin


def build_towns_index(ctx):
    sections, maps = [], []
    for state in ctx.states:
        towns = [t for t in ctx.towns if t["state"] == state]
        if not towns:
            continue
        items = []
        for t in towns:
            n_up = sum(1 for h in ctx.hits_by_town.get(t["id"], []) if ctx.is_upcoming(h))
            note = (f"{n_up} coming up" if n_up else ("" if t["monitored"] else "not read yet"))
            search = f"{t['town']} {t.get('county') or ''} {STATE_NAMES.get(state, state)} {state}".lower()
            status = "up" if n_up else ("monitored" if t["monitored"] else "not")
            note_html = f' <span class="n{" hot" if n_up else ""}">{note}</span>' if note else ""
            items.append(f'<li data-search="{e(search)}" data-status="{status}">'
                         f'<a href="{town_path(state, t["town"])}">{e(t["town"])}</a>{note_html}</li>')
        mon = sum(1 for t in towns if t["monitored"])
        sections.append(f"""<section class="state-towns" aria-labelledby="{state.lower()}">
  <h2 id="{state.lower()}">{e(STATE_NAMES.get(state, state))}</h2>
  <p class="sub">We read {mon} of these {len(towns)} towns' agendas every day.</p>
  <ul class="town-cols" data-filter-list>{''.join(items)}</ul>
</section>""")
    for g, m in ctx.maps.items():
        if m.ok:
            maps.append(f'<figure class="mapfig map-{g}">{m.svg(ctx, links="all")}<figcaption>{m.name()}. Purple: items coming up.</figcaption></figure>')
    total = len(ctx.towns)
    mon = sum(1 for t in ctx.towns if t["monitored"])
    body = f"""
<div class="wrap">
<section class="page-head" aria-labelledby="towns-title">
  <h1 id="towns-title">Find your town</h1>
  <p class="lead">We read {mon:,} of these {total:,} towns every day. The rest block automated readers or post no agendas.</p>
  <form class="filterbar" data-list-filter role="search" action="/towns" method="get">
    <label>Town or county<input type="search" name="q" data-search autocomplete="off"></label>
    <label>Show<select data-status><option value="">All towns</option><option value="up">With items coming up</option><option value="monitored">Read daily</option><option value="not">Not read yet</option></select></label>
    <p class="count" data-count aria-live="polite"></p>
  </form>
  <p class="empty" data-empty hidden>No towns match. Check the spelling, or search by county.</p>
</section>
<div class="maps-row">{''.join(maps)}</div>
{''.join(sections)}
</div>
"""
    return page(ctx, f"Find your town: {total} towns in {join_and(ctx.states)} | {SITE_NAME}",
                f"All {total} towns {SITE_NAME} covers in {join_and(ctx.states)}: which we read every day, and how many solar, "
                "battery storage and data center items each has coming up.",
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
<td class="num" data-label="Coming up">{sum(1 for h in hs if ctx.is_upcoming(h))}</td><td class="num" data-label="All items">{len(hs)}</td></tr>"""
        for (s, town), hs in ranked[:25])
    ag_rows = [r for r in ctx.ag if tp["ag"](r)]

    more = [f"""<details class="disclose"><summary>Towns with the most items</summary>
<div class="table-wrap"><table class="stack counts"><thead><tr><th scope="col">Town</th><th scope="col" class="num">Coming up</th><th scope="col" class="num">All items</th></tr></thead><tbody>{town_rows}</tbody></table></div></details>"""] if town_rows else []
    if past:
        g = group_meetings(ctx, past)[:60]
        more.append(f"""<details class="disclose"><summary>Earlier meetings ({len(g)})</summary>{meeting_list(ctx, g, shown=5, more="Show older")}</details>""")
    if undated:
        g = group_meetings(ctx, undated)[:40]
        more.append(f"""<details class="disclose"><summary>Town meeting warrants ({len(g)})</summary>{meeting_list(ctx, g, shown=5)}</details>""")
    if tp["slug"] == "data-centers":
        more.append("""<details class="disclose"><summary>Can a town pause data centers?</summary>
<p>Yes, in Massachusetts. State law protects solar and battery storage, not data centers.</p>
<p>The Attorney General approved data-center pauses in Shutesbury (case 12047, Jan. 20, 2026), Templeton (case 12294, Sept. 22, 2026) and Gill (Sept. 24, 2026).</p>
<p><a href="/attorney-general">All Massachusetts rulings</a></p></details>""")
    elif ag_rows:
        out = Counter(r.get("outcome") for r in ag_rows if r.get("record_type") == "ag_decision")
        n = sum(out.values())
        more.append(f"""<details class="disclose"><summary>State rulings on these bylaws ({n})</summary>
<p>{"; ".join(f"{v} {k}" for k, v in out.most_common())}.</p><p><a href="/attorney-general">All Massachusetts rulings</a></p></details>""")
    more.append(f'<p class="more-link"><a href="/search?topic={tp["key"]}&amp;upcoming=1">Search these agendas</a></p>')
    others = "".join(f'<li><a href="/topics/{o["slug"]}">{e(o["name"])}</a></li>' for o in TOPIC_PAGES if o is not tp)

    body = f"""
<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/topics">Topics</a></li><li><span aria-current="page">{e(tp['name'])}</span></li></ol></nav>
<h1 id="topic-title">{e(tp['name'])} on town agendas</h1>
<section aria-labelledby="upcoming-title">
  <div class="sec-head"><h2 id="upcoming-title">Coming up</h2><a class="btn" href="{e(alerts_url(topics=[tp['key']]))}">Get these by email</a></div>
  <p class="status">{plural(c['upcoming'], 'item')} in {plural(len({(h['state'], h['town']) for h in upcoming}), 'town')}. Checked {ctx.checked_day}.</p>
  {meeting_list(ctx, group_meetings(ctx, upcoming), shown=5, more="More coming up", empty='Nothing on the agenda about this right now. We check every morning.')}
</section>
<div class="disclosures">{''.join(more)}</div>
<nav class="others" aria-label="Other topics"><p class="small">Other topics:</p><ul class="inline-links">{others}</ul></nav>
</div>
"""
    title = f"{tp['name']} on town agendas in {join_and(ctx.states)} | {SITE_NAME}"
    return page(ctx, title if len(title) <= 70 else f"{tp['name']} on town agendas | {SITE_NAME}",
                f"{c['items']} town agenda items in {c['towns']} towns on {tp['name'].lower()}, {c['upcoming']} for upcoming "
                "meetings, with the board, the date and a link to every agenda.",
                body, f"/topics/{tp['slug']}")


TOPIC_HEAD = ('<thead><tr><th scope="col">Topic</th><th scope="col" class="num">Coming up</th>'
              '<th scope="col" class="num">All items</th><th scope="col" class="num">Towns</th></tr></thead>')


def build_topics_index(ctx):
    rows = []
    keys = [tp["key"] for tp in TOPIC_PAGES] + [k for k in TOPIC_LABELS if k not in TOPIC_PAGE_BY_KEY]
    for k in keys:
        c = topic_counts(ctx, k)
        if not c["items"] and k not in TOPIC_PAGE_BY_KEY:
            continue
        tp = TOPIC_PAGE_BY_KEY.get(k)
        name = f'<a href="/topics/{tp["slug"]}">{e(tp["name"])}</a>' if tp else e(TOPIC_LABELS[k])
        rows.append(f"""<tr><th scope="row">{name}</th><td class="num" data-label="Coming up">{c['upcoming']:,}</td>
<td class="num" data-label="All items">{c['items']:,}</td><td class="num" data-label="Towns">{c['towns']:,}</td></tr>""")
    body = f"""
<div class="wrap narrow">
<section class="page-head" aria-labelledby="topics-title">
  <h1 id="topics-title">Topics</h1>
  <p class="lead">Agenda items by topic. One item can match more than one topic.</p>
</section>
<div class="table-wrap"><table class="stack counts">{TOPIC_HEAD}<tbody>{''.join(rows)}</tbody></table></div>
<p class="actions"><a class="btn" href="/watch">Get alerts</a></p>
</div>
"""
    return page(ctx, f"Topics: solar, battery storage, data centers, moratoria | {SITE_NAME}",
                "Town agenda items on solar, battery storage, data centers, moratoria, clean-energy permits, zoning changes, "
                "affordable housing and cell towers.",
                body, "/topics")


# ---------------------------------------------------------------- search

def build_search(ctx):
    states = "".join(f'<option value="{s}">{e(STATE_NAMES.get(s, s))}</option>' for s in ctx.states)
    topics = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in TOPIC_LABELS.items())
    boards = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in BOARD_NAMES.items())
    towns = "".join(
        f'<optgroup label="{e(STATE_NAMES.get(s, s))}">'
        + "".join(f'<option value="{e(t["id"])}">{e(t["town"])}</option>' for t in ctx.towns if t["state"] == s)
        + "</optgroup>" for s in ctx.states)
    body = f"""
<div class="wrap narrow">
<h1 id="search-title">Search agendas</h1>
<form id="search-form" class="searchform" action="/search" method="get" role="search">
  <label for="search-q">Words to find</label>
  <div class="field-row">
    <input name="q" id="search-q" type="search" autocomplete="off" placeholder="data center moratorium">
    <button class="btn" type="submit">Search</button>
  </div>
  <details class="disclose filters" id="search-filters"><summary>Filters</summary>
  <div class="search-filters">
    <label>State<select name="state"><option value="">All states</option>{states}</select></label>
    <label>Town<select name="town"><option value="">All towns</option>{towns}</select></label>
    <label>Topic<select name="topic"><option value="">All topics</option>{topics}</select></label>
    <label>Board<select name="board"><option value="">All boards</option>{boards}</select></label>
    <label>Order<select name="sort"><option value="">Best match</option><option value="date">Newest meeting first</option></select></label>
    <label class="check"><input type="checkbox" name="upcoming" value="1"> Meetings ahead first</label>
  </div>
  </details>
</form>
<p id="search-status" aria-live="polite"></p>
<p class="search-alert" id="search-alert" hidden><a class="btn quiet" href="/watch">Get alerts for your town by email</a></p>
<ol id="search-results"></ol>
<noscript><p class="notice">Search needs JavaScript. You can still <a href="/towns">find a town</a>.</p></noscript>
</div>
"""
    return page(ctx, f"Search town agendas | {SITE_NAME}",
                f"Search the full text of town board agendas in {ctx.region()}. Filter by state, town, topic and board.",
                body, "/search", scripts=("/search.js",))


# ---------------------------------------------------------------- alerts (/watch) and the alert list view (/w)

def build_watch(ctx):
    topic_count = Counter(t for h in ctx.hits for t in h.get("topics", []))
    topics = [k for k in TOPIC_LABELS if topic_count.get(k) or k != "wetlands_filing"]
    topics += sorted(k for k in topic_count if k not in TOPIC_LABELS)
    topic_boxes = "".join(
        f'<li><label class="check"><input type="checkbox" name="topics" value="{e(k)}" checked>'
        f'<span>{e(TOPIC_LABELS.get(k, k))}</span></label></li>'
        for k in topics)

    body = f"""
<div class="wrap narrow watch">
<p class="notice" id="edit-banner" hidden>Editing <b id="edit-name">your alert list</b>. <a href="/watch">Start a new one instead</a></p>
<p class="notice err" id="watch-error" role="alert" hidden></p>
<h1 id="watch-title" tabindex="-1">Get free alerts</h1>
<form id="watch-form" class="watch-form" novalidate>
  <div class="step" id="step-town">
    <label for="home-town" class="big-q">Which town?</label>
    <p class="form-note" id="town-help">Alerts are free for your town and the towns next to it.</p>
    <input id="home-town" class="big-input" type="text" list="town-names" autocomplete="off" autocapitalize="words" spellcheck="false" aria-describedby="town-help home-read towns-error">
    <datalist id="town-names"></datalist>
    <p class="form-note" id="home-read" aria-live="polite">Pick it from the list as you type.</p>
    <div class="request" id="home-request" hidden>
      <p id="home-request-text"></p>
      <button type="button" class="btn quiet" id="home-request-btn">Request this town</button>
      <p class="form-status" id="home-request-status" role="status" aria-live="polite"></p>
    </div>
    <p class="field-error" id="towns-error" hidden></p>
    <div class="actions"><button type="button" class="btn" id="town-next">Continue</button></div>
  </div>

  <div class="step" id="step-send" hidden>
    <p class="back"><button type="button" class="link-btn" id="change-town">Change town</button></p>
    <div class="preview" id="preview" aria-live="polite"></div>
    <fieldset class="near" id="near-step">
      <legend class="sr-only">Towns</legend>
      <label class="check big" id="near-all-row"><input type="checkbox" id="near-all" checked> <span id="near-all-text">Also watch the towns next to <span id="home-name">your town</span></span></label>
      <p class="field-error" id="near-error" hidden></p>
      <details class="disclose" id="near-details"><summary>See or change the towns</summary>
        <p class="form-note" id="near-note"></p>
        <ul class="check-cols" id="near-list"></ul>
        <div id="extra-wrap" hidden>
          <p class="form-note">Also in this alert list:</p>
          <ul class="check-cols" id="extra-list"></ul>
        </div>
      </details>
      <details class="disclose" id="topics-details"><summary>Topics: all</summary>
        <ul class="check-cols topic-list">{topic_boxes}</ul>
      </details>
      <p class="field-error" id="topics-error" hidden></p>
    </fieldset>

    <div id="email-option" hidden>
      <label class="field big-label">Your email address<input name="email" id="email" type="email" inputmode="email" autocomplete="email" spellcheck="false" aria-describedby="email-help"></label>
      <p class="form-note" id="email-help">We email you a link to confirm it. After that, at most one email a day, only when something new comes up.</p>
      <label class="check" id="email-remove-row" hidden><input type="checkbox" id="email-remove"> Stop emails and remove the address</label>
      <p class="field-error" id="email-error" hidden></p>
    </div>
    <p class="form-note" id="no-email" hidden>Email alerts are starting soon. For now, the next page gives you a calendar link and an RSS feed.</p>

    <details class="disclose" id="hook-details">
      <summary>Other ways to get alerts</summary>
      <p>The next page has a calendar link and an RSS feed, with or without email. You can also post alerts to a chat channel.</p>
      <label class="field">Slack, Discord or Teams webhook URL <small>(optional)</small><input name="webhook_url" id="webhook-url" type="url" inputmode="url" autocomplete="off" spellcheck="false" placeholder="https://hooks.slack.com/services/…" aria-describedby="webhook-help"></label>
      <p class="form-note" id="webhook-help">For Teams, use a Workflows webhook URL. We post once a day.</p>
      <label class="check" id="webhook-remove-row" hidden><input type="checkbox" id="webhook-remove"> Remove the saved webhook</label>
      <label class="field">Message format
        <select name="webhook_format"><option value="auto">Match the service</option><option value="json">Plain JSON</option></select>
      </label>
      <div class="actions"><button type="button" class="btn quiet" id="send-test">Send a test message</button></div>
      <p class="form-status" id="test-status" role="status" aria-live="polite"></p>
      <p class="field-error" id="webhook_url-error" hidden></p>
    </details>
    <details class="disclose" id="name-details">
      <summary>Name this list</summary>
      <label class="field">Name <small>(optional)</small><input name="name" maxlength="80" autocomplete="off" placeholder="Carver and neighbors"></label>
    </details>

    <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <div class="submit-row">
      <button class="btn" type="submit" id="watch-submit">Get alerts</button>
      <p class="form-status" id="watch-status" role="status" aria-live="polite"></p>
    </div>
    <p class="form-note">No account. <a href="/how-it-works#privacy">What we store</a></p>
  </div>
</form>

<section id="my-lists" aria-labelledby="my-lists-title" hidden>
  <h2 id="my-lists-title">Your alert lists in this browser</h2>
  <ul class="plain" id="my-lists-items"></ul>
</section>
</div>
"""
    return page(ctx, f"Get alerts for your town's agendas | {SITE_NAME}",
                "Free alerts for your town and the towns next to it: solar, battery storage, data center and zoning items by "
                "calendar, RSS, email or chat. No account needed.",
                body, "/watch", scripts=("/watch.js",))


def build_viewer(ctx):
    topics = e(json.dumps({k: [v, TOPIC_PHRASES.get(k, (v.lower(), False))[0], TOPIC_PHRASES.get(k, ("", False))[1]]
                           for k, v in TOPIC_LABELS.items()}))
    body = f"""
<div class="wrap narrow" id="wl-app" data-topics="{topics}" data-order="{e(json.dumps(TOPIC_ORDER))}">
<p class="crumbs-plain">Alert list</p>
<h1 id="wl-title">Loading your alerts…</h1>
<p id="wl-summary"></p>
<div class="notice err" id="wl-error" role="alert" hidden></div>
<div id="wl-body" hidden>
  <p class="notice ok" id="created-banner" tabindex="-1" hidden><b>Alerts created.</b><span id="inbox-note" hidden> Check your inbox to confirm your email.</span> Save your private link below. It’s the only way to change these alerts.</p>
  <p class="notice" id="readonly-banner" hidden>This is a shared, read-only link.</p>

  <section aria-labelledby="get-title">
    <h2 id="get-title" class="sr-only">Get these alerts</h2>
    <div class="get-buttons">
      <a class="btn" id="webcal-link" href="#">Add to calendar</a>
      <a class="btn quiet" id="rss-link" href="#">RSS feed</a>
    </div>
    <details class="disclose"><summary>Show feed links</summary>
      <div class="feed-rows" id="feed-rows"></div>
      <p class="small"><a id="json-link" href="#">JSON feed</a></p>
    </details>
  </section>

  <section id="links-section" aria-labelledby="links-title" hidden>
    <h2 id="links-title">Your two links</h2>
    <div class="linkcard private">
      <p class="linkcard-title"><b>Private link: keep this to edit or delete</b></p>
      <div class="copy-row" id="private-row"></div>
    </div>
    <div class="linkcard share">
      <p class="linkcard-title"><b>Share link: safe to post</b></p>
      <div class="copy-row" id="share-row"></div>
    </div>
  </section>

  <section aria-labelledby="items-title">
    <h2 id="items-title">Coming up</h2>
    <p class="status" id="items-lead"></p>
    <div id="items-upcoming"></div>
    <details class="disclose" id="past-wrap"><summary id="past-summary">Earlier meetings</summary><div id="items-past"></div></details>
    <details class="disclose" id="undated-wrap" hidden><summary>Town meeting warrants</summary><div id="items-undated"></div></details>
  </section>

  <details class="disclose settings" id="settings" hidden><summary>Change or delete these alerts</summary>
    <section id="hook-section" aria-labelledby="hook-title" hidden>
      <h2 id="hook-title">Messages</h2>
      <p id="email-status" hidden></p>
      <p id="hook-status"></p>
      <div class="actions"><button type="button" class="btn small quiet" id="hook-test" hidden>Send a test message</button></div>
      <p class="form-status" id="hook-test-status" role="status" aria-live="polite"></p>
    </section>
    <section id="manage-section" aria-labelledby="manage-title" hidden>
      <h2 id="manage-title">Change or delete</h2>
      <p id="plan-line"></p>
      <div class="actions">
        <a class="btn quiet" id="edit-link" href="/watch">Edit towns, topics or messages</a>
        <button type="button" class="btn quiet danger" id="delete-start">Delete alerts</button>
      </div>
      <div class="confirm" id="delete-confirm" hidden>
        <p><b>Delete this alert list?</b> Its page, feeds and messages stop. You can’t undo this.</p>
        <div class="actions"><button type="button" class="btn danger" id="delete-yes">Delete alerts</button><button type="button" class="btn quiet" id="delete-no">Keep them</button></div>
      </div>
      <p class="form-status" id="manage-status" role="status" aria-live="polite"></p>
    </section>
  </details>
</div>
</div>
"""
    return page(ctx, f"Your alerts | {SITE_NAME}", f"A {SITE_NAME} alert list of town agenda items.",
                body, "/w", scripts=("/w.js",), noindex=True)


# ---------------------------------------------------------------- how it works

def build_how(ctx):
    census, leadtime, ag = ctx.census, ctx.leadtime, ctx.ag
    auto = census.get("automated", {})
    boards = census.get("boards", {})
    first = leadtime.get("summary", {}).get("first_posting_only", {})
    window = leadtime.get("meeting_window", {})
    record = ag_moratorium_record(ag)
    regulating = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") != "moratorium"
                  and r.get("outcome") in ("approved", "approved in part", "disapproved")]
    reg_ok = sum(1 for r in regulating if r["outcome"] in ("approved", "approved in part"))
    letters = sum(1 for r in ag if r.get("record_type") == "ag_decision")
    not_auto = census.get("not_automated", {})
    blocked = sorted(not_auto.items(), key=lambda kv: -kv[1]["towns"])
    upcoming = sum(1 for h in ctx.hits if ctx.is_upcoming(h))
    median_ahead = ctx.ahead_median()
    monitored = sum(m for _, m, _ in ctx.coverage())
    coverage_parts = [
        f"{m} of 351 Massachusetts cities and towns" if s == "MA" and n == 351
        else (f"all {n} Rhode Island towns" if s == "RI" and m == n
              else f"{m} of the {n} {STATE_NAMES.get(s, s)} towns we list")
        for s, m, n in ctx.coverage()]
    board_rows = "".join(
        f"<tr><th scope='row'>{BOARD_NAMES[k]}</th><td class='num' data-label='Towns'>{v['towns']} of {v['of']}</td></tr>"
        for k, v in boards.items() if k in BOARD_NAMES)
    gap_rows = "".join(
        f"<li>{e(REASON_LABELS.get(k, k))}: {plural(v['towns'], 'town')}"
        f"{', such as ' + e(join_and(v.get('examples', [])[:3])) if v.get('examples') else ''}.</li>"
        for k, v in blocked)
    health = ""
    if ctx.health is not None:
        ok = [h for k, h in ctx.health.items() if k.startswith("MA:") and h.get("last_success")]
        latest = max((h["last_success"] for h in ok), default="")
        failing = sum(1 for k, h in ctx.health.items() if k.startswith("MA:") and h.get("consecutive_failures", 0) >= 3)
        health = (f"<p>The last daily run, on {fmt_date(latest)}, read {len(ok)} Massachusetts towns. "
                  + (f"{plural(failing, 'town')} failed" if failing else "None failed") + " three days in a row.</p>")

    body = f"""
<div class="wrap narrow prose">
<h1 id="how-title">How it works</h1>
<p class="lead">Every morning we read the agendas towns post online. We flag solar, battery, data center and zoning items. Each one links to its agenda.</p>
<p>It’s informational only, not legal advice.</p>

<section aria-labelledby="coverage">
  <h2 id="coverage">What we read</h2>
  <p>We read {monitored:,} towns’ agendas every day.</p>
  <details class="disclose"><summary>Which towns and boards</summary>
    <ul>{"".join(f"<li>{e(c[:1].upper() + c[1:])}.</li>" for c in coverage_parts)}</ul>
    <p>The Massachusetts towns we read are home to {pct(auto.get('pop_share', 0))} of the state’s people.</p>
    <div class="table-wrap"><table class="stack counts"><caption>Massachusetts towns where we read each board</caption><thead><tr><th scope="col">Board</th><th scope="col" class="num">Towns</th></tr></thead><tbody>{board_rows}</tbody></table></div>
    <p>We also add state wetlands filings for solar and battery projects. <a href="/towns">Find your town</a></p>
  </details>
</section>

<section aria-labelledby="timing">
  <h2 id="timing">How early you hear</h2>
  <p>Agendas usually go up {first.get('median_days', 0):.0f} days before the meeting.</p>
  <details class="disclose"><summary>How we measured it</summary>
    <p>Massachusetts requires notice 48 hours ahead, not counting weekends and holidays.</p>
    <p>We timed {first.get('n', 0):,} agendas from {first.get('towns', 0)} towns. The meetings ran from {fmt_date(window.get('start'))} to {fmt_date(window.get('end'))}.</p>
    <p>The first version went up a median {first.get('median_days', 0):.0f} days ahead. {pct(first.get('share_ge_48h_before_meeting_day', 0))} were online 48 hours before the meeting day.</p>
    <p>{upcoming:,} of our {len(ctx.hits):,} current items are for meetings ahead. We saw those a median {median_ahead:.0f} days before the meeting.</p>
  </details>
</section>

<section aria-labelledby="gaps">
  <h2 id="gaps">Towns we can’t read yet</h2>
  <p>{351 - auto.get('towns', 0)} Massachusetts towns block automated readers or post no current agendas.</p>
  <details class="disclose"><summary>Why, town by town</summary>
    <p>We respect blocks and don’t get around them. We ask those towns for access instead.</p>
    <ul class="plain gaps">{gap_rows}</ul>
  </details>
</section>

<section aria-labelledby="attorney-general">
  <h2 id="attorney-general">State review of moratoriums</h2>
  <p>Since 2024, the Attorney General rejected {"all " + str(record['total']) if record['disapproved'] == record['total'] else f"{record['disapproved']} of {record['total']}"} solar and battery moratorium articles.</p>
  <details class="disclose"><summary>What that means</summary>
    <p>A Massachusetts town bylaw takes effect only after the Attorney General reviews it. City ordinances are not reviewed.</p>
    <p>State law (G.L. c. 40A, §3) protects solar and battery storage. Towns may regulate them but not ban them.</p>
    <p>We read all 2,719 decision letters from January 2022 to October 10, 2026. {letters} were about solar or batteries.</p>
    <p>The {record['total']} moratorium articles came from {record['towns']} towns. Bylaws that regulate did better: {reg_ok} of {len(regulating)} were approved in whole or in part.</p>
    <p>Data-center moratoriums have been approved, because state law doesn’t protect data centers.</p>
    <p><a href="/attorney-general">Every decision, with its letter</a></p>
  </details>
</section>

<section aria-labelledby="crawler">
  <h2 id="crawler">Our crawler, {BOT_NAME}</h2>
  <p>It reads public agenda pages only, and it follows each site’s robots.txt.</p>
  <p>To block it, add this to your robots.txt:</p>
  <pre><code>User-agent: {BOT_NAME}
Disallow: /</code></pre>
  <details class="disclose"><summary>How it behaves</summary>
    <p>It sends this User-Agent on every request:</p>
    <pre><code>{e(BOT_UA)}</code></pre>
    <p>Requests are signed with <a href="https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/">Web Bot Auth</a>. The public key is at <a href="/.well-known/http-message-signatures-directory">/.well-known/http-message-signatures-directory</a>.</p>
    <ul>
      <li>It checks robots.txt before every request, including redirects.</li>
      <li>It makes at most one request per second to a site, or follows <code>Crawl-delay</code>.</li>
      <li>It reads each listing about once a day and each agenda once.</li>
      <li>It never logs in, fills in forms or gets around a bot check.</li>
      <li>It skips files larger than 40 MB.</li>
    </ul>
    {health}
    <p>Run a town website and want something different? <a href="#contact">Send us a note</a>.</p>
  </details>
</section>

<section aria-labelledby="privacy">
  <h2 id="privacy">Privacy</h2>
  <p>We don’t use accounts, cookies or analytics. We store only what your alerts need.</p>
  <details class="disclose"><summary>What we store</summary>
    <p>For an alert list we store your towns, topics and list name. We also store a webhook URL or email address if you give one.</p>
    <p>Each list has two links. The private link can change or delete it. The share link can only view it.</p>
    <p>If you give an email address, we store it with your alert list. We send it only the alerts you asked for. That’s once a day, and only when there’s something new. First we ask you to confirm the address.</p>
    <p>We send email through our provider, Resend. We never share or sell your address. We delete it when you unsubscribe or delete the alert list. Every email has a one-click unsubscribe link.</p>
    <p>Your browser remembers the links of alert lists you made. Clearing this site’s data removes them.</p>
    <p>If paid plans open, Stripe will handle payment. We would store only the Stripe customer and subscription IDs.</p>
    <p>Some people joined an earlier waitlist. We delete each entry on request, or 12 months after signup.</p>
  </details>
</section>

<section aria-labelledby="contact">
  <h2 id="contact">Corrections and contact</h2>
  <p>We read every message. We can’t reply, because the form asks for no contact details.</p>
  <form id="contact-form" class="contact" novalidate>
    <label class="field">What is this about?
      <select name="kind">
        <option value="correction">A correction</option>
        <option value="removal">Delete an earlier waitlist signup</option>
        <option value="message">Something else</option>
      </select>
    </label>
    <label class="field">Message<textarea name="message" required maxlength="2000"></textarea></label>
    <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <button class="btn" type="submit">Send message</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</section>
</div>
"""
    return page(ctx, f"How it works: coverage, timing, crawler and privacy | {SITE_NAME}",
                f"{SITE_NAME} reads {monitored:,} towns' agendas every day. Coverage, how early agendas "
                "are posted, the Attorney General's record, our crawler and privacy.",
                body, "/how-it-works")


# ---------------------------------------------------------------- Attorney General and local actions

def framework_list(framework):
    """State rules and rulings as a dated list, oldest first; undated entries last."""
    entries = []
    for f in sorted(framework, key=lambda f: (not f.get("date"), f.get("date") or "")):
        when = (f'<time datetime="{e(f["date"])}">{fmt_date(f["date"])}</time>' if f.get("date") else "No single date")
        entries.append(f"""<li><p class="when">{when}</p><div><h3>{e(f['title'])}</h3><p>{e(f.get('summary', ''))}</p>{sources_html(f.get('sources', []))}</div></li>""")
    return f'<ol class="timeline">{"".join(entries)}</ol>'


def build_ag(ctx):
    ag = ctx.ag
    dec = [r for r in ag if r.get("record_type") == "ag_decision"]
    dates = sorted(r["decision_date"] for r in dec if r.get("decision_date"))
    towns = len({ag_town(r["town"]) for r in dec})
    rt = Counter(r.get("record_type") for r in ag)
    mor = [r for r in dec if r.get("bylaw_type") == "moratorium"]
    post = [r for r in mor if r["decision_date"] >= TRACER_LANE and r["outcome"] in ("approved", "disapproved")]
    post_n = sum(ag_articles(r) for r in post)
    post_d = sum(ag_articles(r) for r in post if r["outcome"] == "disapproved")
    post_towns = len({r["town"] for r in post})
    reg = [r for r in dec if r.get("bylaw_type") != "moratorium"]
    reg_ok = sum(1 for r in reg if r["outcome"] in ("approved", "approved in part"))
    ok_any = sum(1 for r in dec if r["outcome"] in ("approved", "approved in part"))
    since24 = ag_moratorium_record(ag)
    items = ctx.tracker.get("items", [])
    counties = sorted({i.get("county", "") for i in items if i.get("county")})
    county_opts = "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in counties)
    verified = fmt_date(ctx.tracker.get("generated", date.today().isoformat()))

    def counts(rows):
        c = Counter(r["outcome"] for r in rows)
        return c.get("approved", 0), c.get("approved in part", 0), c.get("disapproved", 0), len(rows)

    def examples(rows, n=3):
        latest = sorted(rows, key=lambda r: r["decision_date"], reverse=True)
        seen, out = set(), []
        for r in latest:
            t = ag_town(r["town"])
            if t not in seen:
                seen.add(t)
                out.append(ctx.town_link("MA", t))
            if len(out) == n:
                break
        return ", ".join(out)

    zr = [r for r in dec if r.get("bylaw_type") == "zoning regulation"]
    zp = [r for r in dec if r.get("bylaw_type") == "zoning prohibition"]
    gl = [r for r in dec if (r.get("bylaw_type") or "").startswith("general bylaw (licensing)")]
    cp = [r for r in dec if r.get("bylaw_type") == "consolidated permit bylaw"]
    part = [r for r in dec if r["outcome"] == "approved in part"]
    herb = [r for r in part if re.search(r"herbicid|pesticid", r.get("summary", "") + " " + r.get("legal_basis", ""), re.I)]
    dc = [r for r in ag if "data cent" in r.get("summary", "").lower()]

    def ratio(rows):
        a, p, d, n = counts(rows)
        return f"{a} approved, {p} in part, {d} disapproved (of {n})"

    patterns = [
        ("Solar or battery-storage moratorium, any length or area, since the SJC's Tracer Lane II ruling (June 2, 2022)",
         "active", "Disapproved", f"{post_d} of {post_n} articles disapproved, in {post_towns} towns", examples(post)),
        ("Zoning that regulates solar or storage: size tiers, districts, special permits, site plan review, setbacks",
         "cleared", "Approved, often with specific provisions struck", ratio(zr), examples(zr)),
        ("Town-wide or standalone battery-storage ban written into zoning",
         "pending", "Usually struck", ratio(zp), examples(zp)),
        ("Licensing or other general (non-zoning) bylaw for battery storage",
         "active", "Disapproved: it must be adopted as zoning", ratio(gl), examples(gl)),
        ("Herbicide or pesticide bans at solar or storage sites",
         "active", "Struck (preempted by G.L. c. 132B)", f"In {len(herb)} of {len(part)} partial approvals", examples(herb)),
        ("Consolidated local permit bylaw that tracks 225 CMR 29.00",
         "cleared", "Approved", ratio(cp), examples(cp)),
        ("Data-center moratorium",
         "cleared", "Approved (not a protected use)",
         "Shutesbury, Templeton and Gill in 2026" + (f"; {len(dc)} in this list" if dc else ""), examples(dc)),
    ]
    pattern_rows = "".join(
        f"<tr><th scope='row'>{e(p)}</th><td data-label='Result'><span class='badge {cls}'>{e(res)}</span></td><td data-label='Count'>{e(cnt)}</td><td data-label='Recent examples'>{ex}</td></tr>"
        for p, cls, res, cnt, ex in patterns)

    def count_cells(a, p, d, n):
        cells = (("Approved", a), ("In part", p), ("Disapproved", d), ("Other", n - a - p - d), ("Total", n))
        return "".join(f"<td class='num' data-label='{label}'>{v}</td>" for label, v in cells)

    types = Counter(r.get("bylaw_type") for r in dec)
    type_rows = "".join(
        f"<tr><th scope='row'>{e(t.capitalize())}</th>{count_cells(a, p, d, n)}</tr>"
        for t, _ in types.most_common()
        for a, p, d, n in [counts([r for r in dec if r.get("bylaw_type") == t])])
    year_rows = "".join(
        f"<tr><th scope='row'>{y}</th>{count_cells(a, p, d, n)}</tr>"
        for y in sorted({r["decision_date"][:4] for r in dec})
        for a, p, d, n in [counts([r for r in dec if r["decision_date"][:4] == y])])
    cnt_head = ('<thead><tr><th scope="col">{}</th><th scope="col" class="num">Approved</th><th scope="col" class="num">In part</th>'
                '<th scope="col" class="num">Disapproved</th><th scope="col" class="num">Other</th><th scope="col" class="num">Total</th></tr></thead>')

    def opts(values):
        return "".join(f'<option value="{e(v)}">{e(v.capitalize())}</option>' for v in values)

    outcomes = [o for o, _ in Counter(r.get("outcome") for r in ag).most_common()]
    bylaws = [b for b, _ in Counter(r.get("bylaw_type") for r in ag).most_common()]
    techs = [t for t, _ in Counter(r.get("technology") for r in ag).most_common()]
    years = sorted({(r.get("decision_date") or "")[:4] for r in ag if r.get("decision_date")}, reverse=True)

    body = f"""
<div class="wrap">
<section class="page-head narrow-text" aria-labelledby="ag-title">
  <h1 id="ag-title">Moratoria, bylaws and Attorney General rulings in Massachusetts</h1>
  <p class="lead">A Massachusetts town bylaw takes effect only after the Attorney General’s Municipal Law Unit reviews it; city ordinances are not reviewed. State law (G.L. c. 40A, §3) protects solar and battery storage: a town may regulate them to protect health, safety or welfare, but may not ban them.</p>
  <ul class="facts">
    <li>Since 2024, {since24['disapproved']} of {since24['total']} solar or battery-storage moratorium articles the Attorney General ruled on were disapproved ({plural(since24['towns'], 'town')}).</li>
    <li>Since the June 2022 Tracer Lane II decision, {post_d} of {post_n} such articles were disapproved ({plural(post_towns, 'town')}).</li>
    <li>{reg_ok} of {len(reg)} bylaws that regulate solar or storage, rather than pause it, were approved in whole or in part.</li>
    <li>This list has {len(dec)} decisions in {towns} towns from {fmt_date(dates[0]) if dates else ''} to {fmt_date(dates[-1]) if dates else ''} ({ok_any} approved in whole or in part), plus {plural(rt.get('court_ruling', 0), 'court ruling')}, {plural(rt.get('city_ordinance', 0), 'city ordinance')} and {rt.get('pending_ag_review', 0)} pending review.</li>
  </ul>
  <nav class="toc" aria-label="On this page"><ul><li><a href="#survives-title">What survives review</a></li><li><a href="#tracker">Local actions we track</a></li><li><a href="#ledger-title">Every decision</a></li><li><a href="#bytype-title">Outcomes by type and year</a></li><li><a href="#rules-title">State law and court rulings</a></li></ul></nav>
</section>

<section aria-labelledby="survives-title">
  <h2 id="survives-title">What survives review</h2>
  <p class="section-lead">Since the Supreme Judicial Court’s Tracer Lane II decision, the Attorney General weighs a bylaw’s purpose against its burden on the protected use. Many approvals warn that using a bylaw to deny a project <q>would run a serious risk of violating</q> §3.</p>
  <div class="table-wrap"><table class="stack"><thead><tr><th scope="col">Kind of bylaw</th><th scope="col">Result</th><th scope="col">Count</th><th scope="col">Recent examples</th></tr></thead><tbody>{pattern_rows}</tbody></table></div>
  <p class="small">The data-center approvals for Shutesbury (case 12047, Jan. 20, 2026) and Templeton (case 12294, Sept. 22, 2026) come from our reading of those letters; this list covers solar and storage decisions.</p>
</section>

<section id="tracker" aria-labelledby="tracker-title">
  <h2 id="tracker-title">Local actions we track</h2>
  <p class="section-lead">{plural(len(items), 'local action')} on battery storage and solar: moratoria, special acts, zoning bylaws and permit rules, each linked to its record. Last checked {verified}. Missing or out of date? <a href="/how-it-works#contact">Send a correction</a>.</p>
  <div class="filterbar">
    <label>Status<select id="f-status"><option value="">All</option><option value="pending">Pending</option><option value="active">In effect or adopted</option><option value="cleared">Not in effect</option><option value="info">Permit rules</option></select></label>
    <label>Topic<select id="f-topic"><option value="">All</option><option value="battery">Battery storage</option><option value="solar">Solar</option></select></label>
    <label>County<select id="f-county"><option value="">All</option>{county_opts}</select></label>
    <label>Words<input id="f-search" type="search"></label>
    <p class="count" id="f-count" aria-live="polite"></p>
  </div>
  {tracker_table(ctx, items, "tracker-table")}
</section>

<section aria-labelledby="ledger-title">
  <h2 id="ledger-title">Every decision</h2>
  <p class="section-lead">Each decision letter links to the Attorney General’s public portal. Court rulings and city ordinances are included for context.</p>
  <div class="filterbar" data-filters="ag-ledger">
    <label>Outcome<select data-key="outcome"><option value="">All</option>{opts(outcomes)}</select></label>
    <label>Kind of bylaw<select data-key="bylaw"><option value="">All</option>{opts(bylaws)}</select></label>
    <label>Technology<select data-key="tech"><option value="">All</option>{opts(techs)}</select></label>
    <label>Year<select data-key="year"><option value="">All</option>{opts(years)}</select></label>
    <label>Words<input type="search" data-search></label>
    <p class="count" data-count aria-live="polite"></p>
  </div>
  {ag_table(ctx, ag, table_id='ag-ledger', filters=True)}
</section>

<section aria-labelledby="bytype-title">
  <h2 id="bytype-title">Outcomes by type and year</h2>
  <div class="cols">
    <div class="table-wrap" tabindex="0" role="region" aria-label="Outcomes by kind of bylaw"><table class="stack counts">{cnt_head.format('Kind of bylaw')}<tbody>{type_rows}</tbody></table></div>
    <div class="table-wrap" tabindex="0" role="region" aria-label="Outcomes by year"><table class="stack counts">{cnt_head.format('Year')}<tbody>{year_rows}</tbody></table></div>
  </div>
</section>

<section aria-labelledby="rules-title">
  <h2 id="rules-title">State law and court rulings</h2>
  <p class="section-lead">Since October 1, 2026, every Massachusetts city and town has had to accept consolidated permit applications for small clean-energy projects and decide them within 12 months.</p>
  {framework_list(ctx.tracker.get('framework', []))}
</section>
</div>
"""
    return page(ctx, f"Massachusetts moratoriums and Attorney General rulings | {SITE_NAME}",
                f"All {len(dec)} Massachusetts Attorney General rulings on town solar and battery-storage bylaws since 2022, with "
                f"letters. Since 2024, {since24['disapproved']} of {since24['total']} moratoria were disapproved.",
                body, "/attorney-general")


# ---------------------------------------------------------------- beta (/pricing)
# The page states what is free and that a paid plan comes later, with no prices. Plan definitions and the
# (disabled) Stripe checkout live in site/api/checkout.js and site/pricing.js and are not rendered here.

def build_pricing(ctx):
    median_ahead = ctx.ahead_median()
    body = f"""
<div class="wrap narrow prose">
<section class="page-head" aria-labelledby="pricing-title">
  <h1 id="pricing-title">What’s free</h1>
  <p class="lead">Alerts for your town and the towns next to it are free. So is everything else on the site: town pages, topics and search.</p>
</section>
<p class="notice" id="checkout-note" role="status" hidden></p>
<section aria-labelledby="free-title">
  <h2 id="free-title">Free alerts include</h2>
  <ul>
    <li>One town plus the towns next to it.</li>
    <li>Every board we read in those towns.</li>
    <li>Every topic we track.</li>
    <li>Items before the meeting, usually {median_ahead:.0f} days ahead (<a href="/how-it-works#timing">how we measure</a>).</li>
    <li>Email<span data-email-soon> (starting soon)</span>, calendar, RSS, Slack, Teams or Discord.</li>
    <li>No account. A private link is the only key.</li>
  </ul>
  <p class="actions"><a class="btn" href="/watch">Get alerts</a></p>
</section>
<section aria-labelledby="later-title">
  <h2 id="later-title">Later</h2>
  <p>Watching more than one area will be a paid plan. There is nothing to buy today.</p>
</section>
</div>
"""
    return page(ctx, f"What’s free | {SITE_NAME}",
                "Free alerts for one town and its neighbors: every board, every topic, by email, calendar, RSS, Slack, Teams or "
                "Discord. More areas will be a paid plan later.",
                body, "/pricing", scripts=("/pricing.js",))


# ---------------------------------------------------------------- old URLs

REDIRECTS = {
    # file: (target path, default fragment, {old fragment: new fragment}, title)
    "proof.html": ("/how-it-works", "#coverage", {
        "#our-timing": "#timing", "#lead-title": "#timing", "#ag-title": "#attorney-general", "#gaps-title": "#gaps",
        "#boards-title": "#coverage", "#towns-title": "/towns", "#method-title": "#crawler"}, "Coverage and method"),
    "privacy.html": ("/how-it-works", "#privacy", {"#contact": "#contact"}, "Privacy and contact"),
    "bot.html": ("/how-it-works", "#crawler", {}, "Our crawler"),
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


def town_index_json(ctx):
    return json.dumps({
        "generated": ctx.hits_doc.get("generated"),
        "towns": [{"id": t["id"], "state": t["state"], "town": t["town"], "county": t.get("county"),
                   "slug": t["slug"], "monitored": t["monitored"]} for t in ctx.towns],
    }, separators=(",", ":"))


def lines_json(ctx):
    """site/data/lines.json for the alert pages: each item's plain line and cleaned quote, which items
    are new, and the items of the last 30 days and ahead by town (for the alert preview)."""
    since = (datetime.strptime(ctx.today, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
    recent = defaultdict(list)
    for h in sorted(ctx.hits, key=lambda h: h.get("meeting_date") or ""):
        d = (h.get("meeting_date") or "")[:10]
        if d >= since:
            recent[f"{h['state']}:{h['town']}"].append([d, board_label(h), h.get("topics", []), h["id"]])
    return json.dumps({
        "generated": ctx.hits_doc.get("generated"),
        "today": ctx.today,
        "since": since,
        "lines": {h["id"]: [agenda_line(h), clean_quote(h.get("snippet"))] for h in ctx.hits},
        "new": [h["id"] for h in ctx.hits if ctx.is_new(h)],
        "recent": recent,
    }, separators=(",", ":"), ensure_ascii=False)


def write(rel, text):
    path = SITE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    ctx = Ctx()
    pages = {
        "index.html": (build_index(ctx), "/"),
        "upcoming.html": (build_upcoming(ctx), "/upcoming"),
        "how-it-works.html": (build_how(ctx), "/how-it-works"),
        "search.html": (build_search(ctx), "/search"),
        "watch.html": (build_watch(ctx), "/watch"),
        "w.html": (build_viewer(ctx), None),
        "towns.html": (build_towns_index(ctx), "/towns"),
        "topics.html": (build_topics_index(ctx), "/topics"),
        "attorney-general.html": (build_ag(ctx), "/attorney-general"),
        "pricing.html": (build_pricing(ctx), "/pricing"),
    }
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
    thin = 0
    for t in ctx.towns:
        html, is_thin = build_town_page(ctx, t)
        thin += is_thin
        pages[f"{t['state'].lower()}/{t['slug']}.html"] = (html, None if is_thin else town_path(t["state"], t["town"]))

    for rel, (html, _) in pages.items():
        write(rel, html)
    for g, m in ctx.maps.items():
        if m.ok:
            write(f"maps/{g}.svg", m.file_svg(ctx, "light"))
            write(f"maps/{g}-dark.svg", m.file_svg(ctx, "dark"))
    write("sitemap.xml", build_sitemap([p for _, p in pages.values() if p]))
    write("robots.txt", build_robots())
    write("data/towns.json", town_index_json(ctx))
    write("data/lines.json", lines_json(ctx))
    stale = SITE / "manifest.txt"
    if stale.exists():
        stale.unlink()

    print(f"built {len(pages)} pages ({len(ctx.towns)} town pages, {thin} thin/noindex), "
          f"{len(ctx.tracker.get('items', []))} tracker rows, {len(ctx.hits)} agenda hits, "
          f"{len(ctx.ag)} AG rows, {len(ctx.points)} map points, town health {'present' if ctx.health is not None else 'absent'}")


if __name__ == "__main__":
    main()
