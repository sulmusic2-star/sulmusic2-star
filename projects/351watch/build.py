"""Render the static 351 Watch site from the data/ files.

Inputs (data/): hits_current.json (the alert-data contract in ARCHITECTURE.md; falls back to
agenda_hits_ma_all.json), towns_*.json (one per state), tracker.json, ag_decisions.json,
ma_census_summary.json, leadtime_ma_all.json and, when present, state/town_health.json.

Usage: python3 build.py          (SITE_STATES=MA python3 build.py publishes only the listed states)
Writes site/: index, proof, privacy, watch, w (watchlist viewer), towns, topics, topics/<slug>,
<state>/<town-slug> for every town, attorney-general, pricing, sitemap.xml, robots.txt and
data/towns.json (the town index the API validates against). The deploy step (site/fetch-static.sh)
copies these plus data/hits_current.json into the deployment.
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE = ROOT / "site"
BASE_URL = "https://351watch-sulmusic2-4637s-projects.vercel.app"

STATE_NAMES = {
    "MA": "Massachusetts", "NY": "New York", "RI": "Rhode Island", "CT": "Connecticut", "NH": "New Hampshire",
    "VT": "Vermont", "ME": "Maine", "NJ": "New Jersey", "PA": "Pennsylvania",
}

STATUS_GROUPS = {
    "active": ({"Adopted", "Approved by AG", "Enacted", "In effect"}, "In effect or adopted"),
    "pending": ({"Proposed", "Hearing held", "On warrant", "Pending at Legislature"}, "Pending"),
    "cleared": ({"Rejected", "Withdrawn", "Expired", "Disapproved by AG", "Sent to study"}, "Not in effect"),
}

TOPIC_LABELS = {
    "battery_storage": "Battery storage",
    "solar": "Solar",
    "data_center": "Data centers",
    "moratorium": "Moratoria",
    "clean_energy_siting": "Consolidated permit",
    "40b_comprehensive_permit": "40B housing",
    "wireless_telecom": "Wireless / cell towers",
    "zoning_amendment": "Zoning amendments",
    "wetlands_filing": "Wetlands filings (MassDEP)",
}
DEFAULT_TOPICS = ["battery_storage", "solar", "data_center", "moratorium", "clean_energy_siting"]
ENERGY_TOPICS = {"battery_storage", "solar", "clean_energy_siting", "data_center"}

BOARD_LABELS = {
    "planning_board": "Planning",
    "zoning_board_of_appeals": "ZBA",
    "conservation_commission": "Conservation",
    "select_board": "Select Board / Council",
    "town_meeting": "Town Meeting",
}
BOARD_NAMES = {
    "planning_board": "Planning board",
    "zoning_board_of_appeals": "Zoning board of appeals",
    "conservation_commission": "Conservation commission",
    "select_board": "Select board or city council",
    "town_meeting": "Town meeting warrants",
}

REASON_LABELS = {
    "bot_challenge": "Site blocks automated visitors",
    "waf_block": "Site firewall blocks automated visitors",
    "agendas_stale_or_undated": "No current dated agendas found online",
    "js_only": "Agendas load only with JavaScript",
    "robots_disallow_site": "Site asks crawlers not to visit",
    "no_adapter": "Agenda platform not supported yet",
    "no_agenda_listing_found": "No agenda listing found",
    "vendor_blocked": "Agenda vendor blocks automated visitors",
    "vendor_robots_disallow": "Agenda vendor asks crawlers not to visit",
    "crawl_delay_exceeds_cap": "Site asks for slower crawling than we support yet",
}

# Topic landing pages: slug -> data topic key, plus how to pick related tracker and AG rows.
TOPIC_PAGES = [
    {"slug": "data-centers", "key": "data_center", "name": "Data centers",
     "h1": "Data centers on town agendas", "matches": "data centers, hyperscale facilities or cryptocurrency mining",
     "tracker": lambda i: False,
     "ag": lambda r: "data cent" in (r.get("summary", "") + r.get("article", "")).lower()},
    {"slug": "battery-storage", "key": "battery_storage", "name": "Battery storage",
     "h1": "Battery energy storage on town agendas", "matches": "battery energy storage (BESS)",
     "tracker": lambda i: "battery" in i.get("topic", "").lower(),
     "ag": lambda r: r.get("technology") in ("BESS", "both") or "BESS" in r.get("technology", "")},
    {"slug": "solar", "key": "solar", "name": "Solar",
     "h1": "Solar on town agendas", "matches": "solar or photovoltaic (PV) projects and bylaws",
     "tracker": lambda i: "solar" in i.get("topic", "").lower(),
     "ag": lambda r: r.get("technology") in ("solar", "both")},
    {"slug": "moratoria", "key": "moratorium", "name": "Moratoria",
     "h1": "Moratoria on town agendas", "matches": "a moratorium of any kind",
     "tracker": lambda i: "moratorium" in i.get("action", "").lower(),
     "ag": lambda r: r.get("bylaw_type") == "moratorium"},
    {"slug": "consolidated-permit", "key": "clean_energy_siting", "name": "Consolidated permit",
     "h1": "Consolidated clean-energy permits on town agendas",
     "matches": "the consolidated local permit, 225 CMR 29.00 or clean energy infrastructure",
     "tracker": lambda i: i.get("action") == "Consolidated permit",
     "ag": lambda r: r.get("bylaw_type") == "consolidated permit bylaw"},
]

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


def watch_url(town_id=None, topic=None):
    params = []
    if town_id:
        params.append("town=" + quote(town_id, safe=""))
    if topic:
        params.append("topic=" + quote(topic, safe=""))
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
        self.census = load("ma_census_summary.json", {})
        self.leadtime = load("leadtime_ma_all.json", {})
        self.ag = load("ag_decisions.json", [])
        self.health = load_health()
        all_towns = load_towns()
        self.hits_doc = load_hits({t["id"]: t for t in all_towns})
        # A state is published (town pages, watchlist picker, API validation) once the daily
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

    def is_upcoming(self, h):
        return bool(h.get("meeting_date")) and h["meeting_date"] >= self.today

    def town_link(self, state, town):
        if f"{state}:{town}" in self.town_by_id:
            return f'<a href="{town_path(state, town)}">{e(town)}</a>'
        return e(town)

    def region(self):
        names = [STATE_NAMES.get(s, s) for s in self.states]
        return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"

    def window_text(self):
        start, end = self.window
        return f"meetings from {fmt_date(start)} to {fmt_date(end)}" if start and end else "the current window"


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


# ---------------------------------------------------------------- shared markup

NAV = [
    ("/towns", "Towns"),
    ("/topics", "Topics"),
    ("/attorney-general", "AG rulings"),
    ("/#tracker", "Tracker"),
    ("/proof", "Proof"),
    ("/pricing", "Pricing"),
]


def page(ctx, title, description, body, path, scripts=(), noindex=False):
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == path else ""}>{label}</a>' for href, label in NAV
    )
    cta_current = ' aria-current="page"' if path == "/watch" else ""
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    canonical = "" if noindex else f'<link rel="canonical" href="{BASE_URL}{"" if path == "/" else path}">\n'
    script_tags = "".join(f'<script src="{s}" defer></script>\n' for s in ("/app.js", *scripts))
    law = ("that Massachusetts towns post under the Open Meeting Law" if ctx.states == ["MA"]
           else "that towns post under state open meeting laws")
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
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="/styles.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5f4a'/%3E%3Ctext x='16' y='21' font-family='Arial' font-size='13' font-weight='700' fill='white' text-anchor='middle'%3E351%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="/">351<span>Watch</span></a>
  <nav class="top" aria-label="Main">
    {nav}
    <a class="cta" href="/watch"{cta_current}>Watch towns</a>
  </nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>351 Watch compiles public records {law}, plus state and legislative sources. It is informational only and not legal advice. Always confirm dates and terms with the town clerk or the cited source.</p>
  <p><a href="/watch">Watch towns</a> · <a href="/towns">All towns</a> · <a href="/topics">Topics</a> · <a href="/attorney-general">Attorney General rulings</a> · <a href="/pricing">Pricing</a> · <a href="/proof">Coverage and method</a> · <a href="/privacy">Privacy</a> · <a href="/privacy#contact">Corrections and contact</a></p>
</div></footer>
{script_tags}</body>
</html>
"""


def lead_note(h):
    days = h.get("days_before_meeting")
    if not isinstance(days, (int, float)):
        return ""
    if days >= 1.5:
        return f'<span class="leadtime">First seen {days:.0f} days before the meeting</span>'
    if days > 0:
        return '<span class="leadtime">First seen the day before the meeting</span>'
    return ""


def hit_card(ctx, h, show_town=True):
    tags = "".join(f'<span class="tag">{e(TOPIC_LABELS.get(t, t))}</span>' for t in h.get("topics", []))
    when = fmt_date(h.get("meeting_date")) or "Date not listed"
    town = ""
    if show_town:
        state = f", {e(h['state'])}" if len(ctx.states) > 1 else ""
        town = f"<b>{ctx.town_link(h['state'], h['town'])}{state}</b>"
    upcoming = '<span class="badge pending">Upcoming</span>' if ctx.is_upcoming(h) else ""
    return f"""<article class="hit">
  <header>{town}<span class="meta">{e(h.get('board', ''))} · {when}</span>{upcoming}</header>
  <p>“{e(h.get('snippet', ''))}”</p>
  <div class="tags">{tags} {lead_note(h)} <a href="{e(h['source_url'])}" rel="nofollow noopener" target="_blank">Agenda<span class="sr-only"> for {e(h['town'])} {e(h.get('board', ''))}, {when}</span></a></div>
</article>"""


def hit_list(ctx, hits, empty, show_town=True, limit=None):
    if not hits:
        return f'<p class="empty">{empty}</p>'
    shown = hits[:limit] if limit else hits
    more = len(hits) - len(shown)
    tail = f'<p class="form-note">Plus {plural(more, "more item")}. Each town page lists all of its items.</p>' if more else ""
    return f'<div class="hits">{"".join(hit_card(ctx, h, show_town) for h in shown)}</div>{tail}'


def split_hits(ctx, hits):
    upcoming = sorted((h for h in hits if ctx.is_upcoming(h)), key=lambda h: (h["meeting_date"], h["town"]))
    past = sorted((h for h in hits if h.get("meeting_date") and not ctx.is_upcoming(h)),
                  key=lambda h: (h["meeting_date"], h["town"]), reverse=True)
    undated = sorted((h for h in hits if not h.get("meeting_date")), key=lambda h: (h["town"], h.get("first_seen", "")))
    return upcoming, past, undated


def dedupe_docs(hits):
    seen, out = set(), []
    for h in hits:
        if h["source_url"] in seen:
            continue
        seen.add(h["source_url"])
        out.append(h)
    return out


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


def tracker_table(ctx, items):
    return f"""<div class="table-wrap"><table class="stack">
  <thead><tr><th scope="col">Town</th><th scope="col">Action</th><th scope="col">Status</th><th scope="col">Key date</th><th scope="col" class="col-summary">What happened</th></tr></thead>
  <tbody>{tracker_rows(ctx, items)}</tbody></table></div>"""


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


def ag_stat_text(record):
    """Approved wording for the headline AG statistic (see research_notes/Product strategy)."""
    return (f"solar or battery-storage moratorium articles the Attorney General ruled on since 2024 were disapproved "
            f"({plural(record['towns'], 'town')})")


def topic_counts(ctx, key, state=None):
    hits = [h for h in ctx.hits if key in h.get("topics", []) and (state is None or h["state"] == state)]
    return {
        "hits": hits,
        "items": len(hits),
        "towns": len({(h["state"], h["town"]) for h in hits}),
        "upcoming": sum(1 for h in hits if ctx.is_upcoming(h)),
    }


# ---------------------------------------------------------------- home

def featured_hits(ctx, hits, limit):
    """Clean-energy items for meetings still ahead first (soonest first), then the most
    recent clean-energy items, then other land-use items; one card per document."""
    upcoming, energy, other = [], [], []
    dated = sorted((h for h in hits if h.get("meeting_date")), key=lambda h: h["meeting_date"], reverse=True)
    for h in dedupe_docs(dated):
        if not ENERGY_TOPICS & set(h.get("topics", [])):
            other.append(h)
        elif ctx.is_upcoming(h):
            upcoming.append(h)
        else:
            energy.append(h)
    upcoming.sort(key=lambda h: h["meeting_date"])
    return (upcoming + energy + other)[:limit]


def topic_cards(ctx, state="MA"):
    cards = []
    for tp in TOPIC_PAGES:
        c = topic_counts(ctx, tp["key"], state)
        cards.append(f"""<a class="card link-card" href="/topics/{tp['slug']}">
  <h3>{e(tp['name'])}</h3>
  <p><b>{c['items']:,}</b> agenda items in {plural(c['towns'], 'town')}; {c['upcoming']:,} for meetings still ahead.</p>
</a>""")
    return "\n".join(cards)


def build_index(ctx):
    items = ctx.tracker.get("items", [])
    hits = [h for h in ctx.hits if h["state"] == "MA"]
    ma_towns = [t for t in ctx.towns if t["state"] == "MA"]
    monitored = (ctx.hits_doc.get("towns_monitored") or {}).get("MA") or sum(1 for t in ma_towns if t["monitored"])
    hit_towns = len({(h["state"], h["town"]) for h in hits})
    upcoming = sum(1 for h in hits if ctx.is_upcoming(h))
    struck = ag_moratorium_record(ctx.ag)
    counties = sorted({i.get("county", "") for i in items if i.get("county")})
    county_opts = "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in counties)
    verified = fmt_date(ctx.tracker.get("generated", date.today().isoformat()))
    scan_time = (ctx.hits_doc.get("generated") or "")[:10]
    featured = featured_hits(ctx, hits, 15)

    body = f"""
<div class="wrap">
<section class="hero" aria-labelledby="hero-title">
  <p class="eyebrow">Massachusetts energy and data-center siting</p>
  <h1 id="hero-title">Battery storage and solar moratoria, town by town</h1>
  <p class="lead">A free, source-linked tracker of local moratoria, special acts and new permit rules for battery storage and solar across Massachusetts, plus items pulled from town board agendas every day, including data-center moratoria and bans. Pick your towns and get new items by feed, calendar or Slack and Teams messages.</p>
  <div class="actions"><a class="btn" href="/watch">Watch your towns</a><a class="btn ghost" href="#tracker">Browse the tracker</a></div>
  <div class="stats" role="list">
    <div class="stat" role="listitem"><b>{monitored} of {len(ma_towns) or 351}</b><span>towns' agendas read automatically</span></div>
    <div class="stat" role="listitem"><b>{len(hits):,}</b><span>agenda items flagged in {hit_towns} towns</span></div>
    <div class="stat" role="listitem"><b>{upcoming:,}</b><span>for meetings still ahead</span></div>
    <div class="stat" role="listitem"><b>{struck['disapproved']} of {struck['total']}</b><span>{ag_stat_text(struck)}</span></div>
  </div>
  <p class="form-note">Every number links to its evidence on the <a href="/proof">coverage and method</a> page. Agenda data as of {fmt_date(scan_time) or 'today'}.</p>
</section>

<section id="topics" aria-labelledby="topics-title">
  <h2 id="topics-title">Follow a topic</h2>
  <p class="section-lead">Massachusetts counts for {ctx.window_text()}. Topic pages cover every state we publish.</p>
  <div class="cards">{topic_cards(ctx)}</div>
</section>

<section id="rules" aria-labelledby="rules-title">
  <h2 id="rules-title">The state rules changed on October 1</h2>
  <p class="section-lead">Every town must now offer a single consolidated permit for small clean-energy projects, with a 12-month decision clock. These are the rules everything below is measured against.</p>
  <div class="cards">{framework_cards(ctx.tracker.get('framework', []))}</div>
</section>

<section id="tracker" aria-labelledby="tracker-title">
  <h2 id="tracker-title">Local actions tracker</h2>
  <p class="section-lead">Each row links to the town, legislative or news source it came from. Last verified {verified}. Spot something missing or out of date? <a href="/privacy#contact">Send a correction</a>.</p>
  <div class="filters">
    <label>Status<select id="f-status"><option value="">All</option><option value="pending">Pending</option><option value="active">In effect or adopted</option><option value="cleared">Not in effect</option><option value="info">Permit rules</option></select></label>
    <label>Topic<select id="f-topic"><option value="">All</option><option value="battery">Battery storage</option><option value="solar">Solar</option></select></label>
    <label>County<select id="f-county"><option value="">All</option>{county_opts}</select></label>
    <label>Search<input id="f-search" type="search" placeholder="Town, board, keyword"></label>
    <span class="count" id="f-count" aria-live="polite"></span>
  </div>
  <div class="table-wrap">
    <table id="tracker-table">
      <thead><tr><th scope="col">Town</th><th scope="col">Action</th><th scope="col">Status</th><th scope="col">Key date</th><th scope="col" class="col-summary">What happened</th></tr></thead>
      <tbody>
{tracker_rows(ctx, items)}
      </tbody>
    </table>
  </div>
</section>

<section id="agendas" aria-labelledby="agendas-title">
  <h2 id="agendas-title">From town agendas</h2>
  <p class="section-lead">Our crawler reads agendas from {monitored} Massachusetts towns every day and flags items on battery storage, solar, data centers, moratoria, consolidated permits, 40B housing, wireless facilities and zoning amendments. Items for meetings still ahead are shown first, with when we first saw them. <a href="/topics">Browse by topic</a> or <a href="/towns">by town</a>, and see <a href="/proof">how we measure this</a>.</p>
  {hit_list(ctx, featured, 'The first automated scan is still running. Check back shortly.')}
</section>

<section id="alerts" aria-labelledby="alerts-title">
  <div class="signup-grid">
    <div>
      <h2 id="alerts-title">Know before the hearing</h2>
      <p class="section-lead">Make a watchlist of towns and topics. Every day after the agenda scan, new matching items show up on your watchlist page and in its feeds. No account and no email: the watchlist's private link is your key.</p>
      <ul class="ticks">
        <li>Choose up to 200 towns and any of the topics above</li>
        <li>RSS and JSON feeds, plus a calendar feed of upcoming meetings</li>
        <li>Optional daily message to a Slack, Microsoft Teams or Discord channel</li>
        <li>Every item links to the original agenda or warrant</li>
      </ul>
      <div class="actions"><a class="btn" href="/watch">Create a watchlist</a><a class="btn ghost" href="/pricing">Pricing</a></div>
    </div>
    <div class="plans" aria-label="Plans">
      <div class="plan"><b>Founding beta</b><span class="price">Free</span><p>Everything on this site, while we build. No account or card.</p></div>
      <div class="plan"><b>Siting Desk</b><span class="price">$349/mo</span><p>Planned, for solar and storage developers. Billed annually.</p></div>
      <div class="plan"><b>Counsel</b><span class="price">$1,500/yr</span><p>Planned, for land-use and energy attorneys.</p></div>
      <div class="plan"><b>Data-Center Local Action Feed</b><span class="price">$499/mo</span><p>Planned.</p></div>
    </div>
  </div>
</section>
</div>
"""
    return page(
        ctx,
        "Massachusetts Battery Storage & Solar Moratorium Tracker | 351 Watch",
        "Free, source-linked tracker of battery storage and solar moratoria, special acts and consolidated permit rules in Massachusetts towns, plus daily items from town board agendas.",
        body, "/",
    )


def framework_cards(framework):
    cards = []
    for f in framework:
        date_html = f'<p class="date">{fmt_date(f.get("date"))}</p>' if f.get("date") else ""
        cards.append(
            f"""<article class="card"><h3>{e(f['title'])}</h3>{date_html}<p>{e(f.get('summary', ''))}</p>{sources_html(f.get('sources', []))}</article>"""
        )
    return "\n".join(cards)


# ---------------------------------------------------------------- proof

def coverage_rows(ctx, towns):
    rows = []
    for t in sorted(towns, key=lambda t: t["town"]):
        found = set(t.get("boards_found", []))
        if t.get("automated"):
            status, cls, group = "Monitored", "cleared", "monitored"
        else:
            status, cls, group = REASON_LABELS.get(t.get("reason_code"), "Not yet monitored"), "pending", "not"
        pills = "".join(
            f'<span class="pill{" on" if key in found else ""}" title="{label}">{label}</span>'
            for key, label in BOARD_LABELS.items()
            if key != "town_meeting" or t.get("has_town_meeting"))
        crawl = ""
        if ctx.health is not None:
            h = ctx.health.get(t["id"]) or {}
            crawl = f'<td class="when crawl">{fmt_date(h.get("last_success")) or "—"}</td>'
        rows.append(f"""<tr data-group="{group}">
  <td class="town"><b><a href="{town_path(t['state'], t['town'])}">{e(t['town'])}</a></b><small>{e(t.get('county', ''))} County</small></td>
  <td class="num">{t['pop']:,}</td>
  <td><span class="badge {cls}">{e(status)}</span></td>
  <td><div class="pills">{pills}</div></td>{crawl}
</tr>""")
    return "\n".join(rows)


def build_proof(ctx):
    census, leadtime, ag = ctx.census, ctx.leadtime, ctx.ag
    auto = census.get("automated", {})
    boards = census.get("boards", {})
    first = leadtime.get("summary", {}).get("first_posting_only", {})
    by_board = leadtime.get("by_board_first_posting_only", {})
    window = leadtime.get("meeting_window", {})
    hits = ctx.hits
    ahead = sorted(h["days_before_meeting"] for h in hits
                   if ctx.is_upcoming(h) and isinstance(h.get("days_before_meeting"), (int, float)))
    median_ahead = ahead[len(ahead) // 2] if ahead else 0
    record = ag_moratorium_record(ag)
    regulating = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") != "moratorium"
                  and r.get("outcome") in ("approved", "approved in part", "disapproved")]
    reg_ok = sum(1 for r in regulating if r["outcome"] in ("approved", "approved in part"))
    not_auto = census.get("not_automated", {})
    blocked = sorted(not_auto.items(), key=lambda kv: -kv[1]["towns"])
    ma_towns = [t for t in ctx.towns if t["state"] == "MA"]
    letters = sum(1 for r in ag if r.get("record_type") == "ag_decision")

    board_rows = "".join(
        f"<tr><td>{BOARD_LABELS[k]}</td><td class='num'>{v['towns']} of {v['of']}</td><td class='num'>{pct(v['share'])}</td></tr>"
        for k, v in boards.items() if k in BOARD_LABELS)
    lead_rows = "".join(
        f"<tr><td>{BOARD_LABELS.get(k, k)}</td><td class='num'>{v['median_days']:.0f} days</td>"
        f"<td class='num'>{v['p10_days']:.0f} days</td><td class='num'>{pct(v['share_ge_48h_before_meeting_day'])}</td><td class='num'>{v['n']:,}</td></tr>"
        for k, v in by_board.items() if k in BOARD_LABELS)
    blocked_rows = "".join(
        f"<tr><td>{e(REASON_LABELS.get(k, k))}</td><td class='num'>{v['towns']}</td><td>{e(', '.join(v.get('examples', [])[:6]))}</td></tr>"
        for k, v in blocked)
    ag_rows = "".join(
        f"""<tr><td class="town"><b>{ctx.town_link('MA', r['town'])}</b><small>{e(r.get('article', ''))}</small></td>
<td class="when">{fmt_date(r['decision_date'])}</td><td><span class="badge {'active' if r['outcome'] == 'disapproved' else 'cleared'}">{e(r['outcome'].capitalize())}</span></td>
<td><a href="{e(r['letter_url'])}" rel="nofollow noopener" target="_blank">Decision letter, case {e(str(r.get('case_number', '')))}</a></td></tr>"""
        for r in record["rows"])

    health_note, crawl_head = "", ""
    if ctx.health is not None:
        crawl_head = '<th scope="col">Last successful crawl</th>'
        ok = [h for k, h in ctx.health.items() if k.startswith("MA:") and h.get("last_success")]
        latest = max((h["last_success"] for h in ok), default="")
        failing = sum(1 for k, h in ctx.health.items() if k.startswith("MA:") and h.get("consecutive_failures", 0) >= 3)
        health_note = (f" The daily crawl last succeeded for {len(ok)} towns (most recent run {fmt_date(latest)});"
                       f" {plural(failing, 'town')} failed three or more days in a row.")

    body = f"""
<div class="wrap">
<section class="hero" aria-labelledby="proof-title">
  <p class="eyebrow">Coverage and method</p>
  <h1 id="proof-title">What we check, and the evidence behind every number</h1>
  <p class="lead">Measured on {fmt_date(census.get('generated', '')[:10])} across all 351 Massachusetts cities and towns. Where we can't read a town yet, we say so and why.</p>
  <div class="stats" role="list">
    <div class="stat" role="listitem"><b>{auto.get('towns', 0)} of 351</b><span>towns read automatically ({pct(auto.get('share', 0))})</span></div>
    <div class="stat" role="listitem"><b>{auto.get('pop', 0) / 1e6:.2f}M</b><span>residents covered ({pct(auto.get('pop_share', 0))} of the state)</span></div>
    <div class="stat" role="listitem"><b>{first.get('median_days', 0):.0f} days</b><span>median time agendas go up before the meeting</span></div>
    <div class="stat" role="listitem"><b>{record['disapproved']} of {record['total']}</b><span>{ag_stat_text(record)}</span></div>
  </div>
</section>

<section aria-labelledby="boards-title">
  <h2 id="boards-title">Which boards we read</h2>
  <p class="section-lead">A town counts as monitored when at least one of its boards has a current agenda listing (dated within 120 days) that our crawler can read. {census.get('all_four_meeting_boards', {}).get('towns', 0)} towns have all four boards covered.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Board</th><th scope="col" class="num">Towns</th><th scope="col" class="num">Share</th></tr></thead><tbody>{board_rows}</tbody></table></div>
</section>

<section aria-labelledby="lead-title">
  <h2 id="lead-title">How far ahead agendas are posted</h2>
  <p class="section-lead">Massachusetts law requires notice 48 hours before a meeting, not counting weekends and holidays. In practice, across {first.get('n', 0):,} agendas from {first.get('towns', 0)} towns whose platforms publish a posting time (meetings {fmt_date(window.get('start'))} to {fmt_date(window.get('end'))}), the first posting went up a median {first.get('median_days', 0):.0f} days before the meeting; {pct(first.get('share_ge_48h_before_meeting_day', 0))} were online at least 48 hours before the meeting day and {pct(first.get('share_ge_24h_before_meeting_day', 0))} at least 24 hours before. That window is when an alert is useful.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Board</th><th scope="col" class="num">Median lead</th><th scope="col" class="num">10th percentile</th><th scope="col" class="num">≥ 48 h before</th><th scope="col" class="num">Agendas</th></tr></thead><tbody>{lead_rows}</tbody></table></div>
  <p class="form-note">Our own timing: of the {len(hits):,} items in the current data, {sum(1 for h in hits if ctx.is_upcoming(h))} are for meetings still ahead; those with a known first-seen time were first seen a median {median_ahead:.0f} days before the meeting day. Each item records when we first fetched its agenda.</p>
</section>

<section aria-labelledby="ag-title">
  <h2 id="ag-title">Will a moratorium survive? The Attorney General's record</h2>
  <p class="section-lead">Town bylaws in Massachusetts take effect only after Attorney General review (cities are not reviewed). We read all 2,719 decision letters issued from January 2022 to October 10, 2026 and found {letters} on solar or battery storage. Since 2024 she has ruled on {record['total']} solar or battery-storage moratorium articles in {record['towns']} towns and disapproved {record['disapproved']}, citing the state's zoning protection for solar and storage (G.L. c. 40A, §3). Bylaws that regulate rather than ban fared differently: {reg_ok} of {len(regulating)} were approved in whole or in part. Data-center moratoria have been approved, because data centers aren't a protected use. <a href="/attorney-general">See the full ledger</a>.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Town and article</th><th scope="col">Decision</th><th scope="col">Outcome</th><th scope="col">Source</th></tr></thead><tbody>{ag_rows}</tbody></table></div>
</section>

<section aria-labelledby="gaps-title">
  <h2 id="gaps-title">Towns we can't read yet, and why</h2>
  <p class="section-lead">{351 - auto.get('towns', 0)} towns aren't monitored automatically yet. Most block automated visitors or ask crawlers not to visit; we respect that and don't work around it. We'll ask those towns and their vendors for access.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Reason</th><th scope="col">Towns</th><th scope="col">Examples</th></tr></thead><tbody>{blocked_rows}</tbody></table></div>
</section>

<section aria-labelledby="towns-title">
  <h2 id="towns-title">All 351 cities and towns</h2>
  <p class="section-lead">Each town links to its page with the boards we read and its current items.{health_note}</p>
  <div class="filters">
    <label>Status<select id="c-status"><option value="">All</option><option value="monitored">Monitored</option><option value="not">Not yet</option></select></label>
    <label>Search<input id="c-search" type="search" placeholder="Town or county"></label>
    <span class="count" id="c-count" aria-live="polite"></span>
  </div>
  <div class="table-wrap">
    <table id="coverage-table" class="plain">
      <thead><tr><th scope="col">Town</th><th scope="col">Population</th><th scope="col">Status</th><th scope="col">Boards read</th>{crawl_head}</tr></thead>
      <tbody>
{coverage_rows(ctx, ma_towns)}
      </tbody>
    </table>
  </div>
</section>

<section aria-labelledby="method-title">
  <h2 id="method-title">How the crawler behaves</h2>
  <p class="section-lead">It reads only publicly posted agenda pages, identifies itself as 351WatchBot, follows each site's robots.txt (checked again on every redirect), makes at most one request per second per site, never logs in, and never gets around bot protection. Scanned agendas are read with OCR. Every item links to the original agenda so you can check it yourself.</p>
</section>
</div>
"""
    return page(
        ctx,
        "Coverage and Method | 351 Watch",
        "How many Massachusetts towns 351 Watch reads, how far ahead agendas are posted, the Attorney General's record on clean-energy moratoria, and the evidence behind each number.",
        body, "/proof",
    )


# ---------------------------------------------------------------- privacy

def build_privacy(ctx):
    body = """
<div class="wrap prose">
<h1>Privacy and contact</h1>
<p>351 Watch has no accounts, no passwords and no email. This note explains what we store and why.</p>
<h2>Watchlists</h2>
<p>When you create a watchlist we store the towns and topics you chose, the optional name and the optional Slack, Teams or Discord webhook URL you enter, when it was created and changed, and whether our daily messages were delivered. It is stored privately at our hosting provider, Vercel, under a random identifier. That identifier is in your watchlist's link and feed links, and it is the only key: anyone who has the link can view, change or delete the watchlist. You can delete it at any time from its page, which removes it from our storage.</p>
<p>We show webhook URLs only in shortened form, because anyone with the full URL can post to your channel. Messages go only to the URL you give us.</p>
<h2>In your browser</h2>
<p>We don't use cookies or analytics. The watchlist pages remember the links of watchlists you made in this browser's local storage, so you can find them again; clearing your browser's site data removes that list.</p>
<h2>Payments</h2>
<p>Everything is free during the founding beta. If paid plans open, payment is handled by Stripe; we would store only the Stripe customer and subscription identifiers on the watchlist the plan applies to.</p>
<h2>Earlier waitlist signups</h2>
<p>Before watchlists existed, some people joined a waitlist. Those entries are kept privately and deleted on request, or 12 months after signup, whichever comes first. We don't send email.</p>
<h2>About the data on this site</h2>
<p>The tracker uses public records: agendas and warrants that towns must post under the Massachusetts Open Meeting Law, Attorney General decision letters, legislative records, and news reports. Our crawler reads only publicly posted pages, identifies itself, follows robots.txt and limits how often it visits each town's website.</p>
<h2 id="contact">Corrections, removal requests and contact</h2>
<p>We read every message. We can't reply, because we don't collect contact details; corrections show up on the site once checked.</p>
<form id="contact-form" class="signup" novalidate>
  <label>Type of request
    <select name="kind">
      <option value="correction">Correction to the data</option>
      <option value="removal">Delete an earlier waitlist signup</option>
      <option value="message">Other message</option>
    </select>
  </label>
  <label>Message <small>(for a removal request, include the address you signed up with)</small><textarea name="message" required maxlength="2000"></textarea></label>
  <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
  <button class="btn" type="submit">Send</button>
  <p class="form-status" role="status" aria-live="polite"></p>
</form>
</div>
"""
    return page(ctx, "Privacy and contact | 351 Watch",
                "What 351 Watch stores for watchlists (no accounts, no email), and how to send corrections.", body, "/privacy")


# ---------------------------------------------------------------- watch + viewer

def build_watch(ctx):
    topic_count = Counter(t for h in ctx.hits for t in h.get("topics", []))
    topics = [k for k in TOPIC_LABELS if topic_count.get(k) or k != "wetlands_filing"]
    topics += sorted(k for k in topic_count if k not in TOPIC_LABELS)
    topic_boxes = "".join(
        f'<label class="check"><input type="checkbox" name="topics" value="{e(k)}"{" checked" if k in DEFAULT_TOPICS else ""}>'
        f'<span>{e(TOPIC_LABELS.get(k, k))} <small>{topic_count.get(k, 0):,} current items</small></span></label>'
        for k in topics)
    groups = []
    for state in ctx.states:
        towns = [t for t in ctx.towns if t["state"] == state]
        if not towns:
            continue
        mon = sum(1 for t in towns if t["monitored"])
        items = []
        for t in towns:
            n = len(ctx.hits_by_town.get(t["id"], []))
            status = '<span class="mon">monitored</span>' if t["monitored"] else '<span class="notyet">not yet</span>'
            county = f"{e(t['county'])} · " if t.get("county") else ""
            search = f"{t['town']} {t.get('county', '')} {STATE_NAMES.get(state, state)}".lower()
            items.append(
                f'<li data-search="{e(search)}" data-monitored="{1 if t["monitored"] else 0}">'
                f'<label><input type="checkbox" name="towns" value="{e(t["id"])}" data-label="{e(t["town"])}">'
                f'<span>{e(t["town"])} <small>{county}{status}{f" · {plural(n, 'item')}" if n else ""}</small></span></label></li>')
        groups.append(f"""<fieldset class="state-group" data-state="{state}">
  <legend>{e(STATE_NAMES.get(state, state))} <small>{mon} of {len(towns)} monitored</small></legend>
  <ul>{''.join(items)}</ul>
</fieldset>""")

    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="watch-title">
  <p class="eyebrow">Free during the founding beta</p>
  <h1 id="watch-title">Watch towns for the agenda items you care about</h1>
  <p class="lead">Pick towns and topics. You get a private watchlist page, RSS and JSON feeds, a calendar of upcoming meetings, and an optional daily message to Slack, Teams or Discord. No account and no email.</p>
</section>
<p class="notice" id="edit-banner" hidden>Editing <b id="edit-name">your watchlist</b>. Changes apply to its page and feeds right away. <a href="/watch">Start a new watchlist instead</a></p>
<p class="notice err" id="watch-error" role="alert" hidden></p>
<form id="watch-form" class="watch-form" novalidate>
  <fieldset class="panel" aria-describedby="town-count">
    <legend><span class="step">1</span> Towns</legend>
    <p class="form-note">Monitored towns are read automatically every day. You can add towns we can't read yet; their items will appear once we can.</p>
    <div class="picker-tools">
      <label>Find towns<input id="town-search" type="search" placeholder="Town or county" autocomplete="off" aria-controls="town-list"></label>
      <label>Show<select id="town-show" aria-controls="town-list"><option value="">All towns</option><option value="monitored">Monitored only</option><option value="selected">Selected only</option></select></label>
      <div class="tool-buttons">
        <button type="button" class="btn small ghost" id="select-shown">Select all shown</button>
        <button type="button" class="btn small ghost" id="clear-towns">Clear</button>
      </div>
    </div>
    <p class="picker-count" id="town-count" aria-live="polite">No towns selected</p>
    <div class="chips" id="town-chips"></div>
    <div class="town-list" id="town-list">
{''.join(groups)}
      <p class="empty" id="town-empty" hidden>No towns match that search.</p>
    </div>
    <p class="field-error" id="towns-error" hidden></p>
  </fieldset>

  <fieldset class="panel">
    <legend><span class="step">2</span> Topics</legend>
    <div class="topic-grid">{topic_boxes}</div>
    <p class="field-error" id="topics-error" hidden></p>
  </fieldset>

  <fieldset class="panel">
    <legend><span class="step">3</span> Name and daily messages <small>(optional)</small></legend>
    <label class="field">Watchlist name<input name="name" maxlength="80" autocomplete="off" placeholder="e.g. Western Mass storage projects"></label>
    <label class="field">Slack, Teams or Discord webhook URL
      <input name="webhook_url" id="webhook-url" type="url" inputmode="url" autocomplete="off" spellcheck="false" placeholder="https://hooks.slack.com/services/…" aria-describedby="webhook-help">
    </label>
    <p class="form-note" id="webhook-help">We post new items once a day. Accepted: Slack incoming webhooks (hooks.slack.com), Microsoft Teams (*.webhook.office.com, outlook.office.com, or a Power Automate workflow on *.logic.azure.com) and Discord (discord.com/api/webhooks).</p>
    <label class="check" id="webhook-remove-row" hidden><input type="checkbox" id="webhook-remove"> Remove the saved webhook</label>
    <label class="field">Message format
      <select name="webhook_format"><option value="auto">Match the service (recommended)</option><option value="json">Plain JSON, for your own Power Automate flow</option></select>
    </label>
    <div class="actions"><button type="button" class="btn ghost" id="send-test">Send a test message</button></div>
    <p class="form-status" id="test-status" role="status" aria-live="polite"></p>
    <p class="field-error" id="webhook_url-error" hidden></p>
  </fieldset>

  <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
  <div class="submit-row">
    <button class="btn" type="submit" id="watch-submit">Create watchlist</button>
    <p class="form-status" id="watch-status" role="status" aria-live="polite"></p>
  </div>
  <p class="form-note">Your watchlist gets a private link. Anyone with the link can view, change or delete it, so share it only with people you trust. See the <a href="/privacy">privacy note</a>.</p>
</form>

<section id="my-lists" aria-labelledby="my-lists-title" hidden>
  <h2 id="my-lists-title">Watchlists made in this browser</h2>
  <ul class="link-list" id="my-lists-items"></ul>
  <p class="form-note">Remembered only in this browser. Bookmark your watchlist links to keep them.</p>
</section>
</div>
"""
    return page(ctx, "Watch towns for battery storage, solar and zoning agenda items | 351 Watch",
                "Create a free watchlist of towns and topics. Get new agenda items by RSS, JSON, calendar feed or daily Slack, Teams and Discord messages. No account or email.",
                body, "/watch", scripts=("/watch.js",))


def build_viewer(ctx):
    topics = e(json.dumps(TOPIC_LABELS))
    body = f"""
<div class="wrap" id="wl-app" data-topics="{topics}">
<section class="hero compact" aria-labelledby="wl-title">
  <p class="eyebrow">Watchlist</p>
  <h1 id="wl-title">Loading watchlist…</h1>
  <p class="lead" id="wl-summary"></p>
</section>
<div class="notice err" id="wl-error" role="alert" hidden></div>
<div id="wl-body" hidden>
  <p class="notice"><b>This page's link is the key to this watchlist.</b> Anyone with it can view, change or delete the watchlist, so share it only with people you trust, and bookmark it now: we can't recover lost links. <button type="button" class="btn small ghost" id="copy-page">Copy link</button></p>
  <p class="notice ok" id="checkout-banner" hidden></p>

  <section aria-labelledby="items-title">
    <h2 id="items-title">Matched agenda items</h2>
    <p class="section-lead" id="items-lead"></p>
    <div class="filters">
      <label>Town<select id="i-town"><option value="">All</option></select></label>
      <label>Topic<select id="i-topic"><option value="">All</option></select></label>
      <label>Search<input id="i-search" type="search" placeholder="Board, keyword"></label>
      <span class="count" id="i-count" aria-live="polite"></span>
    </div>
    <h3 class="sub">Upcoming meetings</h3>
    <div class="hits" id="items-upcoming"></div>
    <h3 class="sub">Recent meetings</h3>
    <div class="hits" id="items-past"></div>
    <div id="undated-wrap" hidden>
      <h3 class="sub">Date not listed (mostly town meeting warrants)</h3>
      <div class="hits" id="items-undated"></div>
    </div>
  </section>

  <section aria-labelledby="feeds-title">
    <h2 id="feeds-title">Feeds</h2>
    <p class="section-lead">Use these in a feed reader, a spreadsheet or your own tools. They update once a day after the agenda scan.</p>
    <div class="feed-rows" id="feed-rows"></div>
    <p><a class="btn ghost small" id="webcal-link" href="#">Subscribe in your calendar app</a></p>
  </section>

  <section aria-labelledby="hook-title">
    <h2 id="hook-title">Daily messages</h2>
    <p id="hook-status"></p>
    <div class="actions"><button type="button" class="btn small ghost" id="hook-test" hidden>Send a test message</button></div>
    <p class="form-status" id="hook-test-status" role="status" aria-live="polite"></p>
  </section>

  <section aria-labelledby="manage-title">
    <h2 id="manage-title">Manage</h2>
    <p id="plan-line"></p>
    <div class="actions">
      <a class="btn" id="edit-link" href="/watch">Edit towns, topics or webhook</a>
      <button type="button" class="btn ghost danger" id="delete-start">Delete watchlist</button>
    </div>
    <div class="confirm" id="delete-confirm" hidden>
      <p><b>Delete this watchlist?</b> Its page and feeds stop working right away. This can't be undone.</p>
      <div class="actions"><button type="button" class="btn danger" id="delete-yes">Delete permanently</button><button type="button" class="btn ghost" id="delete-no">Cancel</button></div>
    </div>
    <p class="form-status" id="manage-status" role="status" aria-live="polite"></p>
  </section>
</div>
</div>
"""
    return page(ctx, "Your watchlist | 351 Watch", "A private 351 Watch watchlist of town agenda items.",
                body, "/w", scripts=("/w.js",), noindex=True)


# ---------------------------------------------------------------- towns

def build_town_page(ctx, t):
    tid, state, town = t["id"], t["state"], t["town"]
    hits = ctx.hits_by_town.get(tid, [])
    upcoming, past, undated = split_hits(ctx, hits)
    tracked = ctx.tracker_by_town.get(tid, [])
    ag_rows = ctx.ag_by_town.get(tid, []) if state == "MA" else []
    thin = not (hits or tracked or ag_rows)
    state_name = STATE_NAMES.get(state, state)
    kind = "City" if t.get("kind") == "city" else "Town"
    county = f"{t['county']} County, " if t.get("county") else ""
    health = (ctx.health or {}).get(tid)

    found = set(t.get("boards_found", []))
    evidence = t.get("board_evidence", {}) or {}
    board_rows = []
    for key, name in BOARD_NAMES.items():
        if key == "town_meeting" and not t.get("has_town_meeting") and key not in found:
            continue
        ev = evidence.get(key) or {}
        if key in found:
            status = '<span class="badge cleared">Read daily</span>'
        elif t["monitored"]:
            status = '<span class="badge info">Not found online</span>'
        else:
            status = '<span class="badge pending">Not yet</span>'
        latest = fmt_date(ev.get("latest")) if key in found else ""
        link = (f'<a href="{e(ev["url"])}" rel="nofollow noopener" target="_blank">Agenda listing<span class="sr-only"> for {e(name.lower())}</span></a>'
                if key in found and ev.get("url") else "")
        board_rows.append(f"<tr><td><b>{e(name)}</b></td><td>{status}</td>"
                          f"<td class='when'{' data-label=\"Latest agenda\"' if latest else ''}>{latest}</td><td>{link}</td></tr>")

    if t["monitored"]:
        coverage = (f'<p><span class="badge cleared">Monitored</span> We read {plural(len(found), "board")} here automatically'
                    f'{" (" + ", ".join(sorted(t.get("platforms") or [])) + ")" if t.get("platforms") else ""}.</p>')
    else:
        coverage = (f'<p><span class="badge pending">Not yet monitored</span> {e(REASON_LABELS.get(t.get("reason_code"), "We can’t read this town’s agendas automatically yet"))}.'
                    f' We respect each site’s rules and don’t work around bot protection. <a href="/proof#gaps-title">Why some towns aren’t covered</a>.</p>')
    if health:
        fails = health.get("consecutive_failures") or 0
        coverage += (f'<p class="form-note">Last successful crawl: {fmt_date(health.get("last_success")) or "none yet"}'
                     f'{f"; the last {fails} attempts failed" if fails else ""}.</p>')

    if t["monitored"]:
        lead = (f"351 Watch reads {town}’s agendas every day. For {ctx.window_text()}, we flagged "
                f"{plural(len(hits), 'item')} on the topics we track, {len(upcoming)} for meetings still ahead.")
    else:
        extra = []
        if tracked:
            extra.append(plural(len(tracked), "tracked local action"))
        if ag_rows:
            extra.append(plural(len(ag_rows), "Attorney General decision"))
        lead = f"We can’t read {town}’s agendas automatically yet." + (
            f" This page lists {' and '.join(extra)} from state and legislative records." if extra else "")

    sections = [f"""<section aria-labelledby="coverage-title">
  <h2 id="coverage-title">Coverage</h2>
  {coverage}
  <div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Board</th><th scope="col">Status</th><th scope="col">Latest agenda seen</th><th scope="col">Source</th></tr></thead><tbody>{''.join(board_rows)}</tbody></table></div>
</section>"""]
    if t["monitored"] or upcoming:
        sections.append(f"""<section aria-labelledby="upcoming-title">
  <h2 id="upcoming-title">Upcoming agenda items</h2>
  {hit_list(ctx, upcoming, 'No matching items for meetings still ahead right now.', show_town=False)}
</section>""")
    if t["monitored"] or past:
        sections.append(f"""<section aria-labelledby="recent-title">
  <h2 id="recent-title">Recent agenda items</h2>
  {hit_list(ctx, past, 'No matching items from recent meetings.', show_town=False)}
</section>""")
    if undated:
        sections.append(f"""<section aria-labelledby="undated-title">
  <h2 id="undated-title">Town meeting warrants and other undated items</h2>
  {hit_list(ctx, undated, '', show_town=False)}
</section>""")
    if tracked:
        sections.append(f"""<section aria-labelledby="tracked-title">
  <h2 id="tracked-title">Tracked local actions</h2>
  {tracker_table(ctx, tracked)}
</section>""")
    if ag_rows:
        sections.append(f"""<section aria-labelledby="ag-title">
  <h2 id="ag-title">Attorney General decisions</h2>
  <p class="section-lead">Decisions on {town}’s solar and battery-storage bylaws. <a href="/attorney-general">What survives review statewide</a>.</p>
  {ag_table(ctx, ag_rows)}
</section>""")
    if t.get("county"):
        neighbors = [n for n in ctx.towns if n["state"] == state and n.get("county") == t["county"] and n["id"] != tid]
        if neighbors:
            links = " · ".join(f'<a href="{town_path(n["state"], n["town"])}">{e(n["town"])}</a>' for n in neighbors)
            sections.append(f"""<section aria-labelledby="county-title">
  <h2 id="county-title">Other {e(t['county'])} County towns</h2>
  <p class="town-links">{links}</p>
</section>""")

    stats = (f'<div class="stat" role="listitem"><b>{len(hits)}</b><span>agenda items flagged</span></div>'
             f'<div class="stat" role="listitem"><b>{len(upcoming)}</b><span>for meetings still ahead</span></div>'
             f'<div class="stat" role="listitem"><b>{len(tracked)}</b><span>tracked local actions</span></div>'
             f'<div class="stat" role="listitem"><b>{len(ag_rows)}</b><span>Attorney General decisions</span></div>')
    website = (f'<a class="btn ghost" href="{e(t["website"])}" rel="nofollow noopener" target="_blank">{kind} website</a>'
               if t.get("website") else "")
    body = f"""
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/towns">Towns</a> <span aria-hidden="true">›</span> <a href="/towns#{state.lower()}">{e(state_name)}</a> <span aria-hidden="true">›</span> <span aria-current="page">{e(town)}</span></nav>
<section class="hero compact" aria-labelledby="town-title">
  <p class="eyebrow">{kind} in {e(county)}{e(state_name)}</p>
  <h1 id="town-title">{e(town)}: energy and land-use items on {kind.lower()} agendas</h1>
  <p class="lead">{e(lead)}</p>
  <div class="actions"><a class="btn" href="{e(watch_url(tid))}">Watch this {kind.lower()}</a>{website}</div>
  <div class="stats" role="list">{stats}</div>
</section>
{''.join(sections)}
</div>
"""
    title = f"{town}, {state}: battery storage, solar and zoning agenda items | 351 Watch"
    desc = (f"{town} ({county}{state_name}): {plural(len(hits), 'agenda item')} on battery storage, solar, data centers, moratoria and zoning"
            f"{f', {len(upcoming)} for upcoming meetings' if upcoming else ''}; tracked local actions and Attorney General decisions, with sources.")
    return page(ctx, title, desc, body, town_path(state, town), noindex=thin), thin


def build_towns_index(ctx):
    sections = []
    for state in ctx.states:
        towns = [t for t in ctx.towns if t["state"] == state]
        if not towns:
            continue
        rows = []
        for t in towns:
            hits = ctx.hits_by_town.get(t["id"], [])
            up = sum(1 for h in hits if ctx.is_upcoming(h))
            badge = ('<span class="badge cleared">Monitored</span>' if t["monitored"]
                     else '<span class="badge pending">Not yet</span>')
            rows.append(f"""<tr data-status="{'monitored' if t['monitored'] else 'not'}" data-items="{'yes' if hits else 'no'}">
  <td class="town"><b><a href="{town_path(state, t['town'])}">{e(t['town'])}</a></b><small>{e(t.get('county') or '')}{' County' if t.get('county') else ''}</small></td>
  <td>{badge}</td>
  <td class="num" data-label="Items">{len(hits)}</td>
  <td class="num" data-label="Upcoming">{up}</td>
  <td class="num" data-label="Tracked">{len(ctx.tracker_by_town.get(t['id'], []))}</td>
  <td class="num" data-label="AG">{len(ctx.ag_by_town.get(t['id'], [])) if state == 'MA' else 0}</td>
</tr>""")
        mon = sum(1 for t in towns if t["monitored"])
        sections.append(f"""<section aria-labelledby="{state.lower()}">
  <h2 id="{state.lower()}">{e(STATE_NAMES.get(state, state))} <small class="muted">{mon} of {len(towns)} monitored</small></h2>
  <div class="table-wrap"><table class="plain stack" data-filter-group="towns">
    <thead><tr><th scope="col">Town</th><th scope="col">Status</th><th scope="col" class="num">Items</th><th scope="col" class="num">Upcoming</th><th scope="col" class="num">Tracked actions</th><th scope="col" class="num">AG decisions</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</section>""")
    total = len(ctx.towns)
    mon = sum(1 for t in ctx.towns if t["monitored"])
    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="towns-title">
  <p class="eyebrow">All towns</p>
  <h1 id="towns-title">Every town we cover, and what's on its agendas</h1>
  <p class="lead">{mon} of {total} towns are read automatically every day. Counts cover {ctx.window_text()}.</p>
  <div class="filters" data-filters="towns">
    <label>Status<select data-key="status"><option value="">All</option><option value="monitored">Monitored</option><option value="not">Not yet</option></select></label>
    <label>Items<select data-key="items"><option value="">All towns</option><option value="yes">With agenda items</option></select></label>
    <label>Search<input type="search" data-search placeholder="Town or county"></label>
    <span class="count" data-count aria-live="polite"></span>
  </div>
</section>
{''.join(sections)}
</div>
"""
    return page(ctx, f"All {total} towns: agenda monitoring status and items | 351 Watch",
                f"Every town 351 Watch covers, whether its agendas are read automatically, and counts of current agenda items, tracked actions and Attorney General decisions.",
                body, "/towns")


# ---------------------------------------------------------------- topics

def build_topic_page(ctx, tp):
    c = topic_counts(ctx, tp["key"])
    hits = c["hits"]
    upcoming, past, undated = split_hits(ctx, hits)
    by_town = defaultdict(list)
    for h in hits:
        by_town[(h["state"], h["town"])].append(h)
    town_rows = "".join(
        f"""<tr><td class="town"><b>{ctx.town_link(s, town)}</b><small>{e(hs[0].get('county') or '')}{' County' if hs[0].get('county') else ''}</small></td>
<td class="num" data-label="Items">{len(hs)}</td><td class="num" data-label="Upcoming">{sum(1 for h in hs if ctx.is_upcoming(h))}</td>
<td class="when" data-label="Latest meeting">{fmt_date(max((h.get('meeting_date') or '' for h in hs), default='')) or '—'}</td></tr>"""
        for (s, town), hs in sorted(by_town.items(), key=lambda kv: (-len(kv[1]), kv[0][1])))
    tracked = [i for i in ctx.tracker.get("items", []) if tp["tracker"](i)]
    ag_rows = [r for r in ctx.ag if tp["ag"](r)]
    boards = Counter(h.get("board_key") for h in hits)
    top_boards = ", ".join(f"{BOARD_NAMES.get(k, k).lower()} ({n})" for k, n in boards.most_common(3) if k)

    lead = (f"{plural(c['items'], 'agenda item')} in {plural(c['towns'], 'town')} mention {tp['matches']}, "
            f"for {ctx.window_text()}. {plural(c['upcoming'], 'item is', 'items are')} for meetings still ahead."
            + (f" Most come from {top_boards}." if top_boards else ""))

    ag_section = ""
    if tp["slug"] == "data-centers":
        gill = [r for r in ag_rows]
        ag_section = f"""<section aria-labelledby="ag-title">
  <h2 id="ag-title">Attorney General review</h2>
  <p class="section-lead">Unlike solar and battery storage, data centers are not a use protected by G.L. c. 40A, §3, so town data-center moratoria can survive review: the Attorney General approved them in Shutesbury (case 12047, Jan. 20, 2026), Templeton (case 12294, Sept. 22, 2026) and Gill (Sept. 24, 2026, where the battery-storage half of the same article was struck).</p>
  {ag_table(ctx, gill) if gill else ''}
</section>"""
    elif ag_rows:
        out = Counter(r.get("outcome") for r in ag_rows if r.get("record_type") == "ag_decision")
        n = sum(out.values())
        summary = ", ".join(f"{v} {k}" for k, v in out.most_common())
        latest = sorted(ag_rows, key=lambda r: r.get("decision_date") or "", reverse=True)[:12]
        ag_section = f"""<section aria-labelledby="ag-title">
  <h2 id="ag-title">Attorney General decisions</h2>
  <p class="section-lead">Of {plural(n, 'decision')} on these bylaws since 2022: {e(summary)}. The {len(latest)} most recent are below; <a href="/attorney-general">see the full ledger and what survives review</a>.</p>
  {ag_table(ctx, latest)}
</section>"""

    other = " · ".join(f'<a href="/topics/{o["slug"]}">{e(o["name"])}</a>' for o in TOPIC_PAGES if o is not tp)
    body = f"""
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/topics">Topics</a> <span aria-hidden="true">›</span> <span aria-current="page">{e(tp['name'])}</span></nav>
<section class="hero compact" aria-labelledby="topic-title">
  <p class="eyebrow">Topic · {e(ctx.region())}</p>
  <h1 id="topic-title">{e(tp['h1'])}</h1>
  <p class="lead">{e(lead)}</p>
  <div class="actions"><a class="btn" href="{e(watch_url(topic=tp['key']))}">Watch this topic</a><a class="btn ghost" href="#by-town">Counts by town</a></div>
  <div class="stats" role="list">
    <div class="stat" role="listitem"><b>{c['items']:,}</b><span>agenda items</span></div>
    <div class="stat" role="listitem"><b>{c['towns']:,}</b><span>towns</span></div>
    <div class="stat" role="listitem"><b>{c['upcoming']:,}</b><span>for meetings still ahead</span></div>
    <div class="stat" role="listitem"><b>{len(tracked) + len(ag_rows)}</b><span>tracked actions and AG decisions</span></div>
  </div>
</section>
<section aria-labelledby="upcoming-title">
  <h2 id="upcoming-title">Upcoming meetings</h2>
  {hit_list(ctx, upcoming, 'No matching items for meetings still ahead right now.')}
</section>
<section id="by-town" aria-labelledby="bytown-title">
  <h2 id="bytown-title">Counts by town</h2>
  {'<div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Town</th><th scope="col" class="num">Items</th><th scope="col" class="num">Upcoming</th><th scope="col">Latest meeting</th></tr></thead><tbody>' + town_rows + '</tbody></table></div>' if town_rows else '<p class="empty">No items in the current window.</p>'}
</section>
<section aria-labelledby="recent-title">
  <h2 id="recent-title">Recent meetings</h2>
  {hit_list(ctx, past, 'No matching items from recent meetings.', limit=60)}
</section>
{f'<section aria-labelledby="undated-title"><h2 id="undated-title">Town meeting warrants and other undated items</h2>{hit_list(ctx, undated, "", limit=30)}</section>' if undated else ''}
{f'<section aria-labelledby="tracked-title"><h2 id="tracked-title">Tracked local actions</h2>{tracker_table(ctx, tracked)}</section>' if tracked else ''}
{ag_section}
<section aria-labelledby="more-title">
  <h2 id="more-title">Other topics</h2>
  <p class="town-links">{other}</p>
</section>
</div>
"""
    return page(ctx, f"{tp['name']} on {ctx.region()} town agendas | 351 Watch",
                f"{c['items']} agenda items in {c['towns']} towns on {tp['name'].lower()}, {c['upcoming']} for upcoming meetings, with counts by town and links to every agenda.",
                body, f"/topics/{tp['slug']}")


def build_topics_index(ctx):
    rows = []
    for tp in TOPIC_PAGES:
        c = topic_counts(ctx, tp["key"])
        rows.append(f"""<tr><td><b><a href="/topics/{tp['slug']}">{e(tp['name'])}</a></b><small class="block">Mentions {e(tp['matches'])}</small></td>
<td class="num">{c['items']:,}</td><td class="num">{c['towns']:,}</td><td class="num">{c['upcoming']:,}</td></tr>""")
    others = Counter(t for h in ctx.hits for t in h.get("topics", []) if t not in {tp["key"] for tp in TOPIC_PAGES})
    other_rows = "".join(
        f"""<tr><td><b>{e(TOPIC_LABELS.get(k, k))}</b></td><td class="num">{n:,}</td>
<td class="num">{len({(h['state'], h['town']) for h in ctx.hits if k in h.get('topics', [])}):,}</td>
<td class="num">{sum(1 for h in ctx.hits if k in h.get('topics', []) and ctx.is_upcoming(h)):,}</td></tr>"""
        for k, n in others.most_common())
    head = '<thead><tr><th scope="col">Topic</th><th scope="col" class="num">Items</th><th scope="col" class="num">Towns</th><th scope="col" class="num">Upcoming</th></tr></thead>'
    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="topics-title">
  <p class="eyebrow">Topics</p>
  <h1 id="topics-title">What town boards are taking up</h1>
  <p class="lead">Agenda items by topic for {ctx.window_text()}. One item can match several topics.</p>
  <div class="actions"><a class="btn" href="/watch">Watch towns and topics</a></div>
</section>
<section aria-labelledby="energy-title">
  <h2 id="energy-title">Energy and siting</h2>
  <div class="table-wrap"><table class="plain">{head}<tbody>{''.join(rows)}</tbody></table></div>
</section>
<section aria-labelledby="other-title">
  <h2 id="other-title">Other land-use topics</h2>
  <p class="section-lead">Also available on watchlists and town pages.</p>
  <div class="table-wrap"><table class="plain">{head}<tbody>{other_rows}</tbody></table></div>
</section>
</div>
"""
    return page(ctx, "Topics: data centers, battery storage, solar, moratoria | 351 Watch",
                "Town agenda items on data centers, battery storage, solar, moratoria and consolidated permits, with counts and links.",
                body, "/topics")


# ---------------------------------------------------------------- attorney general

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
         "Shutesbury, Templeton and Gill in 2026" + (f"; {len(dc)} in this ledger" if dc else ""), examples(dc)),
    ]
    pattern_rows = "".join(
        f"<tr><td><b>{e(p)}</b></td><td><span class='badge {cls}'>{e(res)}</span></td><td data-label='Count'>{e(cnt)}</td><td data-label='Recent examples'>{ex}</td></tr>"
        for p, cls, res, cnt, ex in patterns)

    types = Counter(r.get("bylaw_type") for r in dec)
    type_rows = "".join(
        f"<tr><td>{e(t.capitalize())}</td><td class='num'>{a}</td><td class='num'>{p}</td><td class='num'>{d}</td><td class='num'>{n - a - p - d}</td><td class='num'>{n}</td></tr>"
        for t, _ in types.most_common()
        for a, p, d, n in [counts([r for r in dec if r.get("bylaw_type") == t])])
    year_rows = "".join(
        f"<tr><td>{y}</td><td class='num'>{a}</td><td class='num'>{p}</td><td class='num'>{d}</td><td class='num'>{n - a - p - d}</td><td class='num'>{n}</td></tr>"
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
<section class="hero compact" aria-labelledby="ag-title">
  <p class="eyebrow">Attorney General bylaw review</p>
  <h1 id="ag-title">What survives the Attorney General's review of solar and storage bylaws</h1>
  <p class="lead">Massachusetts town bylaws take effect only after the Attorney General's Municipal Law Unit reviews them; city ordinances are not reviewed. This ledger has {len(dec)} decisions on solar and battery-storage bylaws in {towns} towns from {fmt_date(dates[0]) if dates else ''} to {fmt_date(dates[-1]) if dates else ''}, plus {plural(rt.get('court_ruling', 0), 'court ruling')}, {plural(rt.get('city_ordinance', 0), 'city ordinance')} and {rt.get('pending_ag_review', 0)} pending review, each linked to its source.</p>
  <div class="stats" role="list">
    <div class="stat" role="listitem"><b>{since24['disapproved']} of {since24['total']}</b><span>{ag_stat_text(since24)}</span></div>
    <div class="stat" role="listitem"><b>{post_d} of {post_n}</b><span>solar or battery-storage moratorium articles ruled on since the June 2022 Tracer Lane II decision were disapproved ({plural(post_towns, 'town')})</span></div>
    <div class="stat" role="listitem"><b>{reg_ok} of {len(reg)}</b><span>regulating bylaws approved in whole or in part</span></div>
    <div class="stat" role="listitem"><b>{ok_any} of {len(dec)}</b><span>decisions approved in whole or in part</span></div>
  </div>
</section>

<section aria-labelledby="survives-title">
  <h2 id="survives-title">What survives review</h2>
  <p class="section-lead">Solar and battery-storage systems are protected uses under G.L. c. 40A, §3: a bylaw may not prohibit or unreasonably regulate them except to protect health, safety or welfare. Since the Supreme Judicial Court's Tracer Lane II decision, the Attorney General weighs a bylaw's purpose against its burden on the protected use. Counts are from the ledger below.</p>
  <div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Bylaw pattern</th><th scope="col">Result</th><th scope="col">Count</th><th scope="col">Recent examples</th></tr></thead><tbody>{pattern_rows}</tbody></table></div>
  <p class="form-note">Data-center approvals for Shutesbury (case 12047, Jan. 20, 2026) and Templeton (case 12294, Sept. 22, 2026) come from our reading of those letters; this ledger covers solar and storage decisions only. Many approvals warn that applying a bylaw to deny a project "would run a serious risk of violating" §3.</p>
</section>

<section aria-labelledby="bytype-title">
  <h2 id="bytype-title">Outcomes by bylaw type and year</h2>
  <div class="cols">
    <div class="table-wrap"><table class="plain">{cnt_head.format('Bylaw type')}<tbody>{type_rows}</tbody></table></div>
    <div class="table-wrap"><table class="plain">{cnt_head.format('Year')}<tbody>{year_rows}</tbody></table></div>
  </div>
</section>

<section aria-labelledby="ledger-title">
  <h2 id="ledger-title">The full ledger</h2>
  <p class="section-lead">Every decision letter links to the Attorney General's public portal. Court rulings and city ordinances are included for context.</p>
  <div class="filters" data-filters="ag-ledger">
    <label>Outcome<select data-key="outcome"><option value="">All</option>{opts(outcomes)}</select></label>
    <label>Bylaw type<select data-key="bylaw"><option value="">All</option>{opts(bylaws)}</select></label>
    <label>Technology<select data-key="tech"><option value="">All</option>{opts(techs)}</select></label>
    <label>Year<select data-key="year"><option value="">All</option>{opts(years)}</select></label>
    <label>Search<input type="search" data-search placeholder="Town, article, keyword"></label>
    <span class="count" data-count aria-live="polite"></span>
  </div>
  {ag_table(ctx, ag, table_id='ag-ledger', filters=True)}
</section>
</div>
"""
    return page(ctx, "Attorney General decisions on solar and battery storage bylaws | 351 Watch",
                f"All {len(dec)} Massachusetts Attorney General decisions on town solar and battery-storage bylaws since 2022, with letters. {since24['disapproved']} of {since24['total']} solar or battery-storage moratorium articles ruled on since 2024 were disapproved.",
                body, "/attorney-general")


# ---------------------------------------------------------------- pricing

PLANS = [
    {"key": "siting_desk", "name": "Siting Desk", "price": "$349", "per": "/month, billed annually",
     "who": "For solar and battery-storage developers",
     "features": ["5 seats", "Company and LLC watch: alerts when any of a developer's project companies appears",
                  "Consolidated-permit clock for each application", "MassDEP wetlands filings feed",
                  "Slack, Teams and calendar delivery"]},
    {"key": "counsel", "name": "Counsel", "price": "$1,500", "per": "/year",
     "who": "For land-use and energy attorneys",
     "features": ["3 seats", "Town meeting warrant articles on solar, storage, data centers and moratoria",
                  "Each article matched to the Attorney General's track record for that kind of bylaw"]},
    {"key": "datacenter", "name": "Data-Center Local Action Feed", "price": "$499", "per": "/month",
     "who": "For data-center developers, utilities and analysts",
     "features": ["Massachusetts town actions on data centers: definitions, use-table changes, moratoria, prohibitions",
                  "Status from proposal to vote and Attorney General review", "Webhook, JSON and calendar delivery"]},
]


def build_pricing(ctx):
    cards = "".join(f"""<article class="plan big">
      <h2>{e(p['name'])}</h2>
      <p class="who">{e(p['who'])}</p>
      <p class="price">{e(p['price'])}<small>{e(p['per'])}</small></p>
      <ul class="ticks">{''.join(f'<li>{e(f)}</li>' for f in p['features'])}</ul>
      <button class="btn ghost" type="button" data-plan="{p['key']}" disabled>Planned</button>
    </article>""" for p in PLANS)
    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="pricing-title">
  <p class="eyebrow">Pricing</p>
  <h1 id="pricing-title">Free during the founding beta</h1>
  <p class="lead">Everything on this site is free while we build it: no account, no card. The paid plans below are planned and not on sale yet; their extra features are still being built.</p>
</section>
<p class="notice" id="checkout-note" role="status" hidden></p>
<section aria-label="Plans">
  <div class="price-grid">
    <article class="plan big current">
      <h2>Founding beta</h2>
      <p class="who">Available now</p>
      <p class="price">Free</p>
      <ul class="ticks">
        <li>Up to 200 towns per watchlist, any topics</li>
        <li>Private watchlist page, RSS, JSON and calendar feeds</li>
        <li>Daily Slack, Teams or Discord messages</li>
        <li>Town pages, topic pages and the Attorney General ledger</li>
      </ul>
      <a class="btn" href="/watch">Create a watchlist</a>
    </article>
    {cards}
  </div>
  <p class="form-note" id="plan-help">Paid plans aren't open yet, so there is nothing to buy today. When they open, you'll upgrade a watchlist from its page and pay through Stripe.</p>
</section>
</div>
"""
    return page(ctx, "Pricing | 351 Watch",
                "351 Watch is free during the founding beta. Planned plans: Siting Desk $349/month billed annually, Counsel $1,500/year, Data-Center Local Action Feed $499/month.",
                body, "/pricing", scripts=("/pricing.js",))


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


def write(rel, text):
    path = SITE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    ctx = Ctx()
    pages = {
        "index.html": (build_index(ctx), "/"),
        "proof.html": (build_proof(ctx), "/proof"),
        "privacy.html": (build_privacy(ctx), "/privacy"),
        "watch.html": (build_watch(ctx), "/watch"),
        "w.html": (build_viewer(ctx), None),
        "towns.html": (build_towns_index(ctx), "/towns"),
        "topics.html": (build_topics_index(ctx), "/topics"),
        "attorney-general.html": (build_ag(ctx), "/attorney-general"),
        "pricing.html": (build_pricing(ctx), "/pricing"),
    }
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
    write("sitemap.xml", build_sitemap([p for _, p in pages.values() if p]))
    write("robots.txt", build_robots())
    write("data/towns.json", town_index_json(ctx))
    stale = SITE / "manifest.txt"
    if stale.exists():
        stale.unlink()

    print(f"built {len(pages)} pages ({len(ctx.towns)} town pages, {thin} thin/noindex), "
          f"{len(ctx.tracker.get('items', []))} tracker rows, {len(ctx.hits)} agenda hits, "
          f"{len(ctx.ag)} AG rows, town health {'present' if ctx.health is not None else 'absent'}")


if __name__ == "__main__":
    main()
