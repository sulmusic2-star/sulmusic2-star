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
    "select_board": "Select board or council",
    "town_meeting": "Town meeting",
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

# Topics featured in the home page's "Next on town agendas" list.
HERO_TOPICS = {"battery_storage", "solar", "clean_energy_siting", "data_center", "moratorium"}

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


# ---------------------------------------------------------------- shared markup

NAV = [
    ("/towns", "Towns"),
    ("/topics", "Topics"),
    ("/#tracker", "Tracker"),
    ("/attorney-general", "AG decisions"),
    ("/proof", "Coverage"),
]
FOOTER_LINKS = [
    ("/watch", "Create a watchlist"),
    ("/towns", "All towns"),
    ("/topics", "Topics"),
    ("/attorney-general", "Attorney General decisions"),
    ("/proof", "Coverage and method"),
    ("/pricing", "Free during the beta"),
    ("/privacy", "Privacy"),
    ("/privacy#contact", "Corrections and contact"),
]
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' "
           "height='32' rx='3' fill='%231b4f8a'/%3E%3Ctext x='16' y='21.5' font-family='Georgia,serif' font-size='12.5' "
           "font-weight='700' fill='white' text-anchor='middle'%3E351%3C/text%3E%3C/svg%3E")


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
<meta name="color-scheme" content="light dark">
<link rel="preload" href="/fonts/public-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/besley-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<link rel="icon" href="{FAVICON}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="/">351 Watch</a>
  <nav class="top" aria-label="Main">
    {nav}
    <a class="cta" href="/watch"{cta_current}>Create a watchlist</a>
  </nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>351 Watch compiles public records: agendas and warrants {law}, Attorney General decision letters, court rulings and legislative records. It is informational only and is not legal advice. Confirm dates and terms with the town clerk or the linked source before relying on them.</p>
  <ul class="foot-links">{footer_links}</ul>
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


def date_block(value):
    """The meeting date as a small calendar block. w.js builds the same markup for watchlists."""
    try:
        d = datetime.strptime((value or "")[:10], "%Y-%m-%d")
    except ValueError:
        return f'<p class="hit-date nodate">{e(value) if value else "No date listed"}</p>'
    return (f'<p class="hit-date"><time datetime="{d:%Y-%m-%d}"><span class="dow">{d:%a}</span> '
            f'<span class="mon">{d:%b}</span> <span class="day">{d.day}</span> <span class="yr">{d.year}</span></time></p>')


def hit_card(ctx, h, show_town=True, clip=None):
    """One agenda item: meeting date, town and board, the quoted agenda text, topics, lead time and source."""
    tags = "".join(f'<span class="tag">{e(TOPIC_LABELS.get(t, t))}</span>' for t in h.get("topics", []))
    when = fmt_date(h.get("meeting_date")) or "date not listed"
    board = e(h.get("board", ""))
    if show_town:
        state = f", {e(h['state'])}" if len(ctx.states) > 1 else ""
        where = f'<b>{ctx.town_link(h["state"], h["town"])}{state}</b> <span class="board">{board}</span>'
    else:
        where = f'<b>{board}</b>'
    snippet = h.get("snippet", "")
    if clip and len(snippet) > clip:
        snippet = snippet[:clip].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    upcoming = ctx.is_upcoming(h)
    return f"""<article class="hit{' is-upcoming' if upcoming else ''}">
  {date_block(h.get('meeting_date'))}
  <div class="hit-body">
    <p class="hit-where">{where}</p>
    <blockquote class="snippet" cite="{e(h['source_url'])}">{e(snippet)}</blockquote>
    <p class="hit-meta">{tags}{lead_note(h)}<a href="{e(h['source_url'])}" rel="nofollow noopener" target="_blank">Agenda<span class="sr-only"> for {e(h['town'])} {board}, {when}</span></a></p>
  </div>
</article>"""


def hit_list(ctx, hits, empty, show_town=True, limit=None, clip=None):
    if not hits:
        return f'<p class="empty">{empty}</p>'
    shown = hits[:limit] if limit else hits
    tail = (f'<p class="note">Showing {len(shown):,} of {len(hits):,}. Each town page lists all of its items.</p>'
            if len(hits) > len(shown) else "")
    return f'<div class="hits">{"".join(hit_card(ctx, h, show_town, clip) for h in shown)}</div>{tail}'


def figures(rows):
    """Headline numbers as a list of (number, what it counts, link to its evidence)."""
    items = []
    for num, label, href in rows:
        value = f'<a href="{href}">{num}</a>' if href else num
        items.append(f"<div><dt>{label}</dt><dd>{value}</dd></div>")
    return f'<dl class="figures">{"".join(items)}</dl>'


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
  <thead><tr><th scope="col">Town</th><th scope="col">Action</th><th scope="col">Status</th><th scope="col">Date</th><th scope="col" class="col-summary">What happened</th></tr></thead>
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


TOPIC_HEAD = ('<thead><tr><th scope="col">Topic</th><th scope="col" class="num">Items</th><th scope="col" class="num">Towns</th>'
              '<th scope="col" class="num">Meetings ahead</th></tr></thead>')


def topic_rows(ctx, state=None):
    rows = []
    for tp in TOPIC_PAGES:
        c = topic_counts(ctx, tp["key"], state)
        rows.append(f"""<tr><td><b><a href="/topics/{tp['slug']}">{e(tp['name'])}</a></b><small class="block">Mentions {e(tp['matches'])}</small></td>
<td class="num" data-label="Items">{c['items']:,}</td><td class="num" data-label="Towns">{c['towns']:,}</td><td class="num" data-label="Meetings ahead">{c['upcoming']:,}</td></tr>""")
    return "".join(rows)


def hero_hits(ctx, limit=5):
    """Soonest upcoming energy, data-center and moratorium items, one per agenda document."""
    up = sorted((h for h in ctx.hits if ctx.is_upcoming(h) and HERO_TOPICS & set(h.get("topics", []))),
                key=lambda h: (h["meeting_date"], h["state"] != "MA", h["town"]))
    return dedupe_docs(up)[:limit]


def build_index(ctx):
    items = ctx.tracker.get("items", [])
    hits = ctx.hits
    hit_towns = len({(h["state"], h["town"]) for h in hits})
    upcoming = sum(1 for h in hits if ctx.is_upcoming(h))
    monitored = sum(m for _, m, _ in ctx.coverage())
    struck = ag_moratorium_record(ctx.ag)
    first = ctx.leadtime.get("summary", {}).get("first_posting_only", {})
    counties = sorted({i.get("county", "") for i in items if i.get("county")})
    county_opts = "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in counties)
    verified = fmt_date(ctx.tracker.get("generated", date.today().isoformat()))
    scan_time = (ctx.hits_doc.get("generated") or "")[:10]
    soonest = hero_hits(ctx)
    shown = {h["source_url"] for h in soonest}
    featured = [h for h in featured_hits(ctx, hits, 40) if h["source_url"] not in shown][:12]
    more_up = [h for h in featured if ctx.is_upcoming(h)]
    more_past = [h for h in featured if not ctx.is_upcoming(h)]

    rows = [
        (f"{monitored:,}", f"towns whose agendas we read every day: {e(ctx.coverage_text())}", "/towns"),
        (f"{len(hits):,}", f"agenda items flagged in {plural(hit_towns, 'town')}, for {ctx.window_text()}", "/topics"),
        (f"{upcoming:,}", f"items for meetings still ahead, first seen a median {ctx.ahead_median():.0f} days before the meeting",
         "/proof#our-timing"),
    ]
    if first.get("n"):
        rows.append((f"{first.get('median_days', 0):.0f} days",
                     f"median time between a Massachusetts board posting its first agenda and the meeting "
                     f"({first['n']:,} agendas from {first.get('towns', 0)} towns)", "/proof#lead-title"))
    rows.append((f"{struck['disapproved']} of {struck['total']}", ag_stat_text(struck), "/proof#ag-title"))
    if soonest:
        next_title, next_sub = "Next on town agendas", (
            f"Battery storage, solar, data-center, consolidated-permit and moratorium items, soonest meeting first. "
            f"Agenda data as of {fmt_date(scan_time) or 'today'}.")
        next_list = hit_list(ctx, soonest, "", clip=150)
    else:
        next_title, next_sub = "Latest from town agendas", f"Agenda data as of {fmt_date(scan_time) or 'today'}."
        next_list = hit_list(ctx, featured[:5], "The first automated scan is still running.", clip=150)

    body = f"""
<div class="wrap">
<section class="hero home" aria-labelledby="hero-title">
  <div class="hero-text">
    <h1 id="hero-title">Siting items on town board agendas</h1>
    <p class="place">{e(ctx.region())}</p>
    <p class="lead">Every day 351 Watch reads the agendas that town planning boards, zoning boards, conservation commissions, select boards and councils post before they meet. It pulls out items on battery storage, solar, data centers, moratoria, 40B housing, cell towers and zoning changes, adds MassDEP wetlands filings, and links each item to the agenda it came from.</p>
    <p class="actions"><a class="btn" href="/watch">Create a watchlist</a> <a class="text-link" href="#tracker">Massachusetts moratorium tracker</a></p>
  </div>
  <div class="hero-figures">{figures(rows)}</div>
  <section class="next" aria-labelledby="next-title">
    <h2 id="next-title">{next_title}</h2>
    <p class="next-sub">{next_sub}</p>
    {next_list}
    <p class="next-more"><a href="#agendas">More agenda items</a> or <a href="/towns">find a town</a></p>
  </section>
</section>

<section id="agendas" aria-labelledby="agendas-title">
  <h2 id="agendas-title">More from town agendas</h2>
  <p class="section-lead">A selection, energy and data-center items first. Every item links to its agenda; <a href="/topics">browse by topic</a> or <a href="/towns">by town</a> for the rest.</p>
  {f'<h3 class="sub">Meetings still ahead</h3>{hit_list(ctx, more_up, "")}' if more_up else ''}
  {f'<h3 class="sub">Recent meetings</h3>{hit_list(ctx, more_past, "")}' if more_past else ''}
  {'' if featured else '<p class="empty">The first automated scan is still running.</p>'}
</section>

<section id="topics" aria-labelledby="topics-title">
  <h2 id="topics-title">Agenda items by topic</h2>
  <p class="section-lead">Counts for {ctx.window_text()}, across {e(ctx.region())}. One item can match more than one topic. 40B housing, cell towers, zoning amendments and wetlands filings are on the <a href="/topics">topics page</a>.</p>
  <div class="table-wrap"><table class="plain stack">{TOPIC_HEAD}<tbody>{topic_rows(ctx)}</tbody></table></div>
</section>

<section id="tracker" aria-labelledby="tracker-title">
  <h2 id="tracker-title">Massachusetts local actions tracker</h2>
  <p class="section-lead">{plural(len(items), 'local action')} on battery storage and solar: moratoria, special acts, zoning bylaws and permit rules, each linked to the town, legislative or news record it came from. Last checked {verified}. If an entry is missing or out of date, <a href="/privacy#contact">send a correction</a>.</p>
  <div class="filters">
    <label>Status<select id="f-status"><option value="">All</option><option value="pending">Pending</option><option value="active">In effect or adopted</option><option value="cleared">Not in effect</option><option value="info">Permit rules</option></select></label>
    <label>Topic<select id="f-topic"><option value="">All</option><option value="battery">Battery storage</option><option value="solar">Solar</option></select></label>
    <label>County<select id="f-county"><option value="">All</option>{county_opts}</select></label>
    <label>Search<input id="f-search" type="search" placeholder="Town, board, keyword"></label>
    <span class="count" id="f-count" aria-live="polite"></span>
  </div>
  <div class="table-wrap">
    <table id="tracker-table">
      <thead><tr><th scope="col">Town</th><th scope="col">Action</th><th scope="col">Status</th><th scope="col">Date</th><th scope="col" class="col-summary">What happened</th></tr></thead>
      <tbody>
{tracker_rows(ctx, items)}
      </tbody>
    </table>
  </div>
</section>

<section id="rules" aria-labelledby="rules-title">
  <h2 id="rules-title">State law, regulations and court rulings</h2>
  <p class="section-lead">Since October 1, 2026, every Massachusetts city and town has had to accept consolidated permit applications for small clean-energy projects and decide them within 12 months.</p>
  {framework_list(ctx.tracker.get('framework', []))}
</section>

<section id="alerts" aria-labelledby="alerts-title">
  <h2 id="alerts-title">Watchlists</h2>
  <div class="split">
    <div>
      <p class="section-lead">Pick towns and topics, and 351 Watch keeps a private page of the matching agenda items, updated each day after the agenda scan.</p>
      <ul class="plain-list">
        <li>RSS and JSON feeds, and a calendar feed with one entry per upcoming meeting that has matched items</li>
        <li>An optional daily message to a Slack, Microsoft Teams or Discord channel</li>
        <li>A link to the original agenda or warrant on every item</li>
      </ul>
      <p class="actions"><a class="btn" href="/watch">Create a watchlist</a></p>
    </div>
    <p class="aside">Watchlists are free during the founding beta, and you don't need an account or an email address: the watchlist's private link is its key. <a href="/pricing">About the beta</a>.</p>
  </div>
</section>
</div>
"""
    return page(
        ctx,
        f"Battery storage, solar and data-center items on {join_and(ctx.states)} town agendas | 351 Watch",
        f"351 Watch reads the agendas of {monitored:,} towns in {ctx.region()} every day and flags battery storage, "
        "solar, data-center, moratorium, 40B, cell tower and zoning items, with a Massachusetts tracker of local "
        "moratoria and permit rules. Every item links to its source.",
        body, "/",
    )


def framework_list(framework):
    """State rules and rulings as a dated list, oldest first; undated entries last."""
    entries = []
    for f in sorted(framework, key=lambda f: (not f.get("date"), f.get("date") or "")):
        when = (f'<time datetime="{e(f["date"])}">{fmt_date(f["date"])}</time>' if f.get("date")
                else '<span class="muted">No single date</span>')
        entries.append(f"""<li><p class="when">{when}</p><div><h3>{e(f['title'])}</h3><p>{e(f.get('summary', ''))}</p>{sources_html(f.get('sources', []))}</div></li>""")
    return f'<ol class="timeline">{"".join(entries)}</ol>'


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
    median_ahead = ctx.ahead_median()
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
        f"<tr><td class='town'><b>{BOARD_LABELS.get(k, k)}</b></td><td class='num' data-label='Median'>{v['median_days']:.0f} days</td>"
        f"<td class='num' data-label='10th percentile'>{v['p10_days']:.0f} days</td><td class='num' data-label='48 hours or more'>{pct(v['share_ge_48h_before_meeting_day'])}</td><td class='num' data-label='Agendas'>{v['n']:,}</td></tr>"
        for k, v in by_board.items() if k in BOARD_LABELS)
    blocked_rows = "".join(
        f"<tr><td class='town'><b>{e(REASON_LABELS.get(k, k))}</b></td><td class='num' data-label='Towns'>{v['towns']}</td><td data-label='Examples'>{e(', '.join(v.get('examples', [])[:6]))}</td></tr>"
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
        health_note = (f" The daily crawl last succeeded for {len(ok)} towns (most recent run {fmt_date(latest)}); "
                       + (f"{plural(failing, 'town')} failed" if failing else "none failed") + " three or more days in a row.")
    upcoming = sum(1 for h in hits if ctx.is_upcoming(h))
    rows = [
        (f"{auto.get('towns', 0)} of 351", f"Massachusetts cities and towns whose agendas we read automatically "
                                          f"({pct(auto.get('share', 0))})", "#boards-title"),
        (f"{auto.get('pop', 0) / 1e6:.2f}M", f"residents in those towns, {pct(auto.get('pop_share', 0))} of the state",
         "#towns-title"),
        (f"{first.get('median_days', 0):.0f} days", "median time between the first agenda posting and the meeting",
         "#lead-title"),
        (f"{median_ahead:.0f} days", f"median lead for the {upcoming:,} items we found for meetings still ahead",
         "#our-timing"),
        (f"{record['disapproved']} of {record['total']}", ag_stat_text(record), "#ag-title"),
    ]

    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="proof-title">
  <h1 id="proof-title">Coverage and method</h1>
  <p class="lead">Measured {fmt_date(census.get('generated', '')[:10])} across all 351 Massachusetts cities and towns. Each figure links to the table it comes from, and we list the reason for every town we can't read yet.</p>
  {figures(rows)}
</section>

<section aria-labelledby="boards-title">
  <h2 id="boards-title">Which boards we read</h2>
  <p class="section-lead">A town counts as monitored when at least one of its boards has an agenda listing dated within the last 120 days that our crawler can read. {census.get('all_four_meeting_boards', {}).get('towns', 0)} towns have all four meeting boards covered.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Board</th><th scope="col" class="num">Towns</th><th scope="col" class="num">Share</th></tr></thead><tbody>{board_rows}</tbody></table></div>
</section>

<section aria-labelledby="lead-title">
  <h2 id="lead-title">How far ahead agendas are posted</h2>
  <p class="section-lead">Massachusetts law requires notice 48 hours before a meeting, not counting weekends and holidays. We measured {first.get('n', 0):,} agendas from {first.get('towns', 0)} towns whose platforms publish a posting time, for meetings from {fmt_date(window.get('start'))} to {fmt_date(window.get('end'))}. The first posting went up a median {first.get('median_days', 0):.0f} days before the meeting. {pct(first.get('share_ge_48h_before_meeting_day', 0))} were online at least 48 hours before the meeting day, and {pct(first.get('share_ge_24h_before_meeting_day', 0))} at least 24 hours before.</p>
  <div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Board</th><th scope="col" class="num">Median lead</th><th scope="col" class="num">10th percentile</th><th scope="col" class="num">48 hours or more</th><th scope="col" class="num">Agendas</th></tr></thead><tbody>{lead_rows}</tbody></table></div>
  <p class="note" id="our-timing">Our own timing: of the {len(hits):,} items in the current data, {upcoming:,} are for meetings still ahead. Those with a known first-seen time were first seen a median {median_ahead:.0f} days before the meeting day. Each item records when we first fetched its agenda.</p>
</section>

<section aria-labelledby="ag-title">
  <h2 id="ag-title">The Attorney General's record on moratoria</h2>
  <p class="section-lead">A Massachusetts town bylaw takes effect only after the Attorney General reviews it; city ordinances are not reviewed. We read all 2,719 decision letters issued from January 2022 to October 10, 2026 and found {letters} on solar or battery storage. Since 2024 the Attorney General has ruled on {record['total']} solar or battery-storage moratorium articles in {record['towns']} towns and disapproved {record['disapproved']}, citing the zoning protection for solar and storage in G.L. c. 40A, §3. Bylaws that regulate rather than ban fared differently: {reg_ok} of {len(regulating)} were approved in whole or in part. Data-center moratoria have been approved, because data centers are not a protected use. <a href="/attorney-general">Full ledger of decisions</a>.</p>
  <div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Town and article</th><th scope="col">Decided</th><th scope="col">Outcome</th><th scope="col">Source</th></tr></thead><tbody>{ag_rows}</tbody></table></div>
</section>

<section aria-labelledby="gaps-title">
  <h2 id="gaps-title">Towns we can't read yet</h2>
  <p class="section-lead">{351 - auto.get('towns', 0)} Massachusetts towns aren't monitored automatically yet. Most of them block automated visitors or ask crawlers not to visit. We respect both and don't work around them; we'll ask those towns and their vendors for access instead.</p>
  <div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Reason</th><th scope="col">Towns</th><th scope="col">Examples</th></tr></thead><tbody>{blocked_rows}</tbody></table></div>
</section>

<section aria-labelledby="towns-title">
  <h2 id="towns-title">All 351 cities and towns</h2>
  <p class="section-lead">Each name links to the town's page, with the boards we read and its current items.{health_note}</p>
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
  <h2 id="method-title">Crawler rules</h2>
  <p class="section-lead">The crawler reads only publicly posted agenda pages and identifies itself as 351WatchBot. It follows each site's robots.txt, checking again on every redirect, makes at most one request per second to a site, never logs in and never gets around bot protection. Scanned agendas are read with OCR. Every item links to the original agenda so you can check it yourself.</p>
</section>
</div>
"""
    return page(
        ctx,
        "Coverage and method | 351 Watch",
        f"351 Watch reads {auto.get('towns', 0)} of 351 Massachusetts towns' agendas automatically. Agendas go up a median "
        f"{first.get('median_days', 0):.0f} days before the meeting. Board-by-board coverage, posting times, the Attorney "
        "General's record on moratoria, and the towns we can't read yet.",
        body, "/proof",
    )


# ---------------------------------------------------------------- privacy

def build_privacy(ctx):
    body = """
<div class="wrap"><div class="prose">
<h1>Privacy and contact</h1>
<p>351 Watch has no accounts or passwords, and it doesn't collect email addresses.</p>
<h2>Watchlists</h2>
<p>When you create a watchlist we store the towns and topics you chose, the optional name, the optional Slack, Teams or Discord webhook URL, when the watchlist was created and changed, and whether each daily message was delivered. It is stored privately at our hosting provider, Vercel, under a random identifier. That identifier is part of the watchlist's link and its feed links, and it is the only key: anyone who has the link can view, change or delete the watchlist. Deleting a watchlist from its page removes it from our storage.</p>
<p>We show webhook URLs only in shortened form, because anyone with the full URL can post to your channel. Messages go only to the URL you give us.</p>
<h2>In your browser</h2>
<p>We don't use cookies or analytics. The watchlist pages keep the links of watchlists made in this browser in its local storage so you can find them again. Clearing the site's data in your browser removes that list.</p>
<h2>Payments</h2>
<p>Everything is free during the founding beta. If paid plans open, Stripe will handle payment, and we would store only the Stripe customer and subscription IDs on the watchlist the plan applies to.</p>
<h2>Earlier waitlist signups</h2>
<p>Before watchlists existed, some people joined a waitlist. We keep those entries privately and delete each one on request or 12 months after signup, whichever comes first. We don't send email.</p>
<h2>Where the data comes from</h2>
<p>The site is built from public records: agendas and warrants that towns post under open meeting laws, Attorney General decision letters, court rulings, legislative records and news reports. Our crawler reads only publicly posted pages, identifies itself, follows robots.txt and limits how often it visits each town's website.</p>
<h2 id="contact">Corrections, removal requests and contact</h2>
<p>We read every message. The form doesn't collect contact details, so we can't reply; a correction shows up on the site once we've checked it.</p>
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
</div></div>
"""
    return page(ctx, "Privacy and contact | 351 Watch",
                "What 351 Watch stores for a watchlist (it has no accounts and collects no email addresses), and how to send a correction.",
                body, "/privacy")


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
            status = '<span class="mon">read daily</span>' if t["monitored"] else '<span class="notyet">not read yet</span>'
            details = [e(t["county"]) if t.get("county") else "", status, plural(n, "item") if n else ""]
            search = f"{t['town']} {t.get('county', '')} {STATE_NAMES.get(state, state)}".lower()
            items.append(
                f'<li data-search="{e(search)}" data-monitored="{1 if t["monitored"] else 0}">'
                f'<label><input type="checkbox" name="towns" value="{e(t["id"])}" data-label="{e(t["town"])}">'
                f'<span>{e(t["town"])} <small>{", ".join(d for d in details if d)}</small></span></label></li>')
        groups.append(f"""<fieldset class="state-group" data-state="{state}">
  <legend>{e(STATE_NAMES.get(state, state))} <small>{mon} of {len(towns)} read daily</small></legend>
  <ul>{''.join(items)}</ul>
</fieldset>""")

    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="watch-title">
  <h1 id="watch-title">Create a watchlist</h1>
  <p class="lead">Choose towns and topics. Each day after the agenda scan, new matching items appear on your watchlist's page and in its RSS, JSON and calendar feeds. You can also have them posted to a Slack, Microsoft Teams or Discord channel.</p>
  <p class="note">Free during the founding beta. You don't need an account or an email address: the watchlist's private link is its only key.</p>
</section>
<p class="notice" id="edit-banner" hidden>Editing <b id="edit-name">your watchlist</b>. Changes apply to its page and feeds right away. <a href="/watch">Start a new watchlist instead</a></p>
<p class="notice err" id="watch-error" role="alert" hidden></p>
<form id="watch-form" class="watch-form" novalidate>
  <fieldset class="panel" aria-describedby="town-count">
    <legend><span class="step">1</span> Towns</legend>
    <p class="form-note">Towns marked "read daily" are the ones whose agendas we read automatically. You can add towns we can't read yet; their items will appear once we can.</p>
    <div class="picker-tools">
      <label>Find towns<input id="town-search" type="search" placeholder="Town or county" autocomplete="off" aria-controls="town-list"></label>
      <label>Show<select id="town-show" aria-controls="town-list"><option value="">All towns</option><option value="monitored">Read daily</option><option value="selected">Selected</option></select></label>
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
    <p class="form-note" id="webhook-help">New items are posted once a day. Paste a Slack incoming webhook (hooks.slack.com), a Microsoft Teams webhook (*.webhook.office.com, outlook.office.com, or a Power Automate workflow on *.logic.azure.com) or a Discord webhook (discord.com/api/webhooks).</p>
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
  <p class="form-note">Anyone with your watchlist's private link can view, change or delete it, so share the link only with people you trust. The <a href="/privacy">privacy note</a> lists what we store.</p>
</form>

<section id="my-lists" aria-labelledby="my-lists-title" hidden>
  <h2 id="my-lists-title">Watchlists made in this browser</h2>
  <ul class="link-list" id="my-lists-items"></ul>
  <p class="form-note">This list lives only in this browser. Bookmark your watchlist links to keep them.</p>
</section>
</div>
"""
    return page(ctx, "Create a watchlist of town agenda items | 351 Watch",
                "Choose towns and topics and get new battery storage, solar, data-center and zoning items from their agendas "
                "by RSS, JSON, calendar feed or a daily Slack, Teams or Discord message. Free during the beta.",
                body, "/watch", scripts=("/watch.js",))


def build_viewer(ctx):
    topics = e(json.dumps(TOPIC_LABELS))
    body = f"""
<div class="wrap" id="wl-app" data-topics="{topics}">
<section class="hero compact" aria-labelledby="wl-title">
  <p class="crumbs">Watchlist</p>
  <h1 id="wl-title">Loading watchlist…</h1>
  <p class="lead" id="wl-summary"></p>
</section>
<div class="notice err" id="wl-error" role="alert" hidden></div>
<div id="wl-body" hidden>
  <p class="notice"><b>Bookmark this page.</b> Its link is the only key to this watchlist: anyone who has it can view, change or delete the watchlist, and we can't recover a lost link. <button type="button" class="btn small ghost" id="copy-page">Copy link</button></p>
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
    <p class="section-lead">Paste these into a feed reader, a spreadsheet or your own scripts. They update once a day, after the agenda scan.</p>
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
      <p><b>Delete this watchlist?</b> Its page and feeds stop working right away, and you can't undo it.</p>
      <div class="actions"><button type="button" class="btn danger" id="delete-yes">Delete watchlist</button><button type="button" class="btn ghost" id="delete-no">Keep it</button></div>
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
            status = '<span class="badge info">No agendas found online</span>'
        else:
            status = '<span class="badge pending">Not read yet</span>'
        latest = fmt_date(ev.get("latest")) if key in found else ""
        link = (f'<a href="{e(ev["url"])}" rel="nofollow noopener" target="_blank">Agenda listing<span class="sr-only"> for {e(name.lower())}</span></a>'
                if key in found and ev.get("url") else "")
        board_rows.append(f"<tr><td><b>{e(name)}</b></td><td>{status}</td>"
                          f"<td class='when'{' data-label=\"Latest agenda\"' if latest else ''}>{latest}</td><td>{link}</td></tr>")

    where = kind.lower()
    sources = []
    for p in t.get("platforms") or []:
        name = PLATFORM_NAMES.get(p, p).format(kind=where)
        if name not in sources:
            sources.append(name)
    if t["monitored"]:
        coverage = (f'<p><span class="badge cleared">Read daily</span> We read {plural(len(found), "board")} here automatically'
                    f'{" from " + e(join_and(sources)) if sources else ""}.</p>')
    else:
        coverage = (f'<p><span class="badge pending">Not read yet</span> {e(REASON_LABELS.get(t.get("reason_code"), "We can’t read this town’s agendas automatically yet"))}.'
                    f' We follow each site’s rules and don’t work around bot protection. <a href="/proof#gaps-title">All towns we can’t read yet</a>.</p>')
    if health:
        fails = health.get("consecutive_failures") or 0
        coverage += (f'<p class="note">Last successful crawl: {fmt_date(health.get("last_success")) or "none yet"}'
                     f'{f"; the last {fails} attempts failed" if fails else ""}.</p>')

    extra = []
    if tracked:
        extra.append(plural(len(tracked), "tracked local action"))
    if ag_rows:
        extra.append(plural(len(ag_rows), "Attorney General decision"))
    if t["monitored"]:
        ahead = (f"{len(upcoming)} of them for meetings still ahead" if upcoming else "none for meetings still ahead")
        lead = (f"We read {town}’s agendas every day. For {ctx.window_text()}, we flagged "
                f"{plural(len(hits), 'item')} on the topics we track" + (f", {ahead}." if hits else "."))
        if extra:
            lead += f" This page also lists {join_and(extra)}."
    else:
        lead = f"We can’t read {town}’s agendas automatically yet." + (
            f" This page lists {join_and(extra)} from state and legislative records." if extra else "")
        if hits:
            dep = sum(1 for h in hits if h.get("source") == "massdep_wetlands")
            lead += (f" It also lists {plural(dep, 'MassDEP wetlands filing')}." if dep == len(hits)
                     else f" It also lists {plural(len(hits), 'item')} on the topics we track.")

    sections = [f"""<section aria-labelledby="coverage-title">
  <h2 id="coverage-title">Boards we read</h2>
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
  <p class="section-lead">The Attorney General's rulings on {town}’s solar and battery-storage bylaws. <a href="/attorney-general">Statewide record by type of bylaw</a>.</p>
  {ag_table(ctx, ag_rows)}
</section>""")
    if t.get("county"):
        neighbors = [n for n in ctx.towns if n["state"] == state and n.get("county") == t["county"] and n["id"] != tid]
        if neighbors:
            links = "".join(f'<li><a href="{town_path(n["state"], n["town"])}">{e(n["town"])}</a></li>' for n in neighbors)
            sections.append(f"""<section aria-labelledby="county-title">
  <h2 id="county-title">Other towns in {e(t['county'])} County</h2>
  <ul class="town-links">{links}</ul>
</section>""")

    website = (f' <a class="text-link" href="{e(t["website"])}" rel="nofollow noopener" target="_blank">{kind} website</a>'
               if t.get("website") else "")
    body = f"""
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/towns">Towns</a> <span aria-hidden="true">›</span> <a href="/towns#{state.lower()}">{e(state_name)}</a> <span aria-hidden="true">›</span> <span aria-current="page">{e(town)}</span></nav>
<section class="hero compact" aria-labelledby="town-title">
  <h1 id="town-title">{e(town)}</h1>
  <p class="place">{kind} in {e(county)}{e(state_name)}</p>
  <p class="lead">{e(lead)}</p>
  <p class="actions"><a class="btn" href="{e(watch_url(tid))}">Watch {e(town)}</a>{website}</p>
</section>
{''.join(sections)}
</div>
"""
    title = f"{town}, {state}: battery storage, solar and zoning agenda items | 351 Watch"
    if hits:
        desc = (f"{town} ({county}{state_name}): {plural(len(hits), 'agenda item')} on battery storage, solar, data centers, "
                f"moratoria and zoning{f', {len(upcoming)} for upcoming meetings' if upcoming else ''}, each linked to its source.")
    elif t["monitored"]:
        desc = (f"{town} ({county}{state_name}): 351 Watch reads its agendas every day"
                + (f" and lists {join_and(extra)}" if extra else "") + ", with sources.")
    else:
        desc = (f"{town} ({county}{state_name}): 351 Watch can't read its agendas automatically yet"
                + (f"; this page lists {join_and(extra)}, with sources" if extra else "") + ".")
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
            badge = ('<span class="badge cleared">Read daily</span>' if t["monitored"]
                     else '<span class="badge pending">Not read yet</span>')
            rows.append(f"""<tr data-status="{'monitored' if t['monitored'] else 'not'}" data-items="{'yes' if hits else 'no'}">
  <td class="town"><b><a href="{town_path(state, t['town'])}">{e(t['town'])}</a></b><small>{e(t.get('county') or '')}{' County' if t.get('county') else ''}</small></td>
  <td>{badge}</td>
  <td class="num" data-label="Items">{len(hits)}</td>
  <td class="num" data-label="Meetings ahead">{up}</td>
  <td class="num" data-label="Tracked">{len(ctx.tracker_by_town.get(t['id'], []))}</td>
  <td class="num" data-label="AG">{len(ctx.ag_by_town.get(t['id'], [])) if state == 'MA' else 0}</td>
</tr>""")
        mon = sum(1 for t in towns if t["monitored"])
        sections.append(f"""<section aria-labelledby="{state.lower()}">
  <h2 id="{state.lower()}">{e(STATE_NAMES.get(state, state))} <small class="muted">{mon} of {len(towns)} read daily</small></h2>
  <div class="table-wrap"><table class="plain stack" data-filter-group="towns">
    <thead><tr><th scope="col">Town</th><th scope="col">Status</th><th scope="col" class="num">Items</th><th scope="col" class="num">Meetings ahead</th><th scope="col" class="num">Tracked actions</th><th scope="col" class="num">AG decisions</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</section>""")
    total = len(ctx.towns)
    mon = sum(1 for t in ctx.towns if t["monitored"])
    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="towns-title">
  <h1 id="towns-title">Towns</h1>
  <p class="lead">We read the agendas of {mon:,} of these {total:,} towns every day: {e(ctx.coverage_text())}. Item counts are for {ctx.window_text()}.</p>
  <div class="filters" data-filters="towns">
    <label>Status<select data-key="status"><option value="">All</option><option value="monitored">Read daily</option><option value="not">Not read yet</option></select></label>
    <label>Items<select data-key="items"><option value="">All towns</option><option value="yes">With agenda items</option></select></label>
    <label>Search<input type="search" data-search placeholder="Town or county"></label>
    <span class="count" data-count aria-live="polite"></span>
  </div>
</section>
{''.join(sections)}
</div>
"""
    return page(ctx, f"All {total} towns: agenda monitoring status and items | 351 Watch",
                f"The {total} towns 351 Watch covers in {ctx.region()}, whether we read their agendas every day, and their current agenda items, tracked actions and Attorney General decisions.",
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
<td class="num" data-label="Items">{len(hs)}</td><td class="num" data-label="Meetings ahead">{sum(1 for h in hs if ctx.is_upcoming(h))}</td>
<td class="when" data-label="Latest meeting">{fmt_date(max((h.get('meeting_date') or '' for h in hs), default='')) or '—'}</td></tr>"""
        for (s, town), hs in sorted(by_town.items(), key=lambda kv: (-len(kv[1]), kv[0][1])))
    tracked = [i for i in ctx.tracker.get("items", []) if tp["tracker"](i)]
    ag_rows = [r for r in ctx.ag if tp["ag"](r)]
    boards = Counter(h.get("board_key") for h in hits)
    top_boards = join_and(f"{BOARD_NAMES.get(k, k).lower()} ({n})" for k, n in boards.most_common(3) if k)

    lead = (f"For {ctx.window_text()}, {plural(c['items'], 'agenda item')} in {plural(c['towns'], 'town')} mention "
            f"{tp['matches']}. {plural(c['upcoming'], 'item is', 'items are')} for meetings still ahead."
            + (f" Most come from the {top_boards}." if top_boards else ""))
    if tracked or ag_rows:
        lead += " This page also lists " + join_and(
            [plural(len(tracked), "tracked local action") if tracked else "",
             plural(len(ag_rows), "Attorney General decision") if ag_rows else ""]) + "."

    ag_section = ""
    if tp["slug"] == "data-centers":
        gill = [r for r in ag_rows]
        ag_section = f"""<section aria-labelledby="ag-title">
  <h2 id="ag-title">Attorney General review</h2>
  <p class="section-lead">Data centers are not a use protected by G.L. c. 40A, §3, unlike solar and battery storage, so a town data-center moratorium can survive review. The Attorney General approved them in Shutesbury (case 12047, Jan. 20, 2026), Templeton (case 12294, Sept. 22, 2026) and Gill (Sept. 24, 2026, where the battery-storage half of the same article was struck).</p>
  {ag_table(ctx, gill) if gill else ''}
</section>"""
    elif ag_rows:
        out = Counter(r.get("outcome") for r in ag_rows if r.get("record_type") == "ag_decision")
        n = sum(out.values())
        summary = ", ".join(f"{v} {k}" for k, v in out.most_common())
        latest = sorted(ag_rows, key=lambda r: r.get("decision_date") or "", reverse=True)[:12]
        ag_section = f"""<section aria-labelledby="ag-title">
  <h2 id="ag-title">Attorney General decisions</h2>
  <p class="section-lead">Of {plural(n, 'decision')} on these bylaws since 2022: {e(summary)}. Here are the {len(latest)} most recent; <a href="/attorney-general">the full ledger</a> shows what survives review.</p>
  {ag_table(ctx, latest)}
</section>"""

    other = "".join(f'<li><a href="/topics/{o["slug"]}">{e(o["name"])}</a></li>' for o in TOPIC_PAGES if o is not tp)
    body = f"""
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/topics">Topics</a> <span aria-hidden="true">›</span> <span aria-current="page">{e(tp['name'])}</span></nav>
<section class="hero compact" aria-labelledby="topic-title">
  <h1 id="topic-title">{e(tp['h1'])}</h1>
  <p class="place">{e(ctx.region())}</p>
  <p class="lead">{e(lead)}</p>
  <p class="actions"><a class="btn" href="{e(watch_url(topic=tp['key']))}">Watch this topic</a> <a class="text-link" href="#by-town">Counts by town</a></p>
</section>
<section aria-labelledby="upcoming-title">
  <h2 id="upcoming-title">Upcoming meetings</h2>
  {hit_list(ctx, upcoming, 'No matching items for meetings still ahead right now.')}
</section>
<section id="by-town" aria-labelledby="bytown-title">
  <h2 id="bytown-title">Counts by town</h2>
  {'<div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Town</th><th scope="col" class="num">Items</th><th scope="col" class="num">Meetings ahead</th><th scope="col">Latest meeting</th></tr></thead><tbody>' + town_rows + '</tbody></table></div>' if town_rows else '<p class="empty">No items in the current window.</p>'}
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
  <ul class="town-links">{other}</ul>
</section>
</div>
"""
    return page(ctx, f"{tp['name']} on {ctx.region()} town agendas | 351 Watch",
                f"{c['items']} agenda items in {c['towns']} towns on {tp['name'].lower()}, {c['upcoming']} for upcoming meetings, with counts by town and links to every agenda.",
                body, f"/topics/{tp['slug']}")


def build_topics_index(ctx):
    others = Counter(t for h in ctx.hits for t in h.get("topics", []) if t not in {tp["key"] for tp in TOPIC_PAGES})
    other_rows = "".join(
        f"""<tr><td><b>{e(TOPIC_LABELS.get(k, k))}</b></td><td class="num" data-label="Items">{n:,}</td>
<td class="num" data-label="Towns">{len({(h['state'], h['town']) for h in ctx.hits if k in h.get('topics', [])}):,}</td>
<td class="num" data-label="Meetings ahead">{sum(1 for h in ctx.hits if k in h.get('topics', []) and ctx.is_upcoming(h)):,}</td></tr>"""
        for k, n in others.most_common())
    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="topics-title">
  <h1 id="topics-title">Topics</h1>
  <p class="lead">Agenda items by topic for {ctx.window_text()}, across {e(ctx.region())}. One item can match more than one topic.</p>
  <p class="actions"><a class="btn" href="/watch">Create a watchlist</a></p>
</section>
<section aria-labelledby="energy-title">
  <h2 id="energy-title">Energy and siting</h2>
  <div class="table-wrap"><table class="plain stack">{TOPIC_HEAD}<tbody>{topic_rows(ctx)}</tbody></table></div>
</section>
<section aria-labelledby="other-title">
  <h2 id="other-title">Other land-use topics</h2>
  <p class="section-lead">These have no topic page yet. You can add them to a watchlist, and town pages list them.</p>
  <div class="table-wrap"><table class="plain stack">{TOPIC_HEAD}<tbody>{other_rows}</tbody></table></div>
</section>
</div>
"""
    return page(ctx, "Topics: data centers, battery storage, solar, moratoria | 351 Watch",
                "Town agenda items on data centers, battery storage, solar, moratoria, consolidated permits, 40B housing, "
                "cell towers and zoning amendments, with counts by town and a link to every agenda.",
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

    def count_cells(a, p, d, n):
        cells = (("Approved", a), ("In part", p), ("Disapproved", d), ("Other", n - a - p - d), ("Total", n))
        return "".join(f"<td class='num' data-label='{label}'>{v}</td>" for label, v in cells)

    types = Counter(r.get("bylaw_type") for r in dec)
    type_rows = "".join(
        f"<tr><td class='town'><b>{e(t.capitalize())}</b></td>{count_cells(a, p, d, n)}</tr>"
        for t, _ in types.most_common()
        for a, p, d, n in [counts([r for r in dec if r.get("bylaw_type") == t])])
    year_rows = "".join(
        f"<tr><td class='town'><b>{y}</b></td>{count_cells(a, p, d, n)}</tr>"
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
    ag_figures = figures([
        (f"{since24['disapproved']} of {since24['total']}", ag_stat_text(since24), "#survives-title"),
        (f"{post_d} of {post_n}", "solar or battery-storage moratorium articles ruled on since the June 2022 Tracer Lane II "
                                  f"decision were disapproved ({plural(post_towns, 'town')})", "#survives-title"),
        (f"{reg_ok} of {len(reg)}", "bylaws that regulate solar or storage, rather than pause it, were approved in whole "
                                    "or in part", "#bytype-title"),
        (f"{ok_any} of {len(dec)}", "decisions in the ledger approved the bylaw in whole or in part", "#ledger-title"),
    ])

    body = f"""
<div class="wrap">
<section class="hero compact" aria-labelledby="ag-title">
  <h1 id="ag-title">Attorney General review of solar and battery-storage bylaws</h1>
  <p class="lead">A Massachusetts town bylaw takes effect only after the Attorney General's Municipal Law Unit reviews it; city ordinances are not reviewed. This ledger has {len(dec)} decisions on solar and battery-storage bylaws in {towns} towns from {fmt_date(dates[0]) if dates else ''} to {fmt_date(dates[-1]) if dates else ''}, plus {plural(rt.get('court_ruling', 0), 'court ruling')}, {plural(rt.get('city_ordinance', 0), 'city ordinance')} and {rt.get('pending_ag_review', 0)} pending review. Each one links to its source.</p>
  {ag_figures}
</section>

<section aria-labelledby="survives-title">
  <h2 id="survives-title">What survives review</h2>
  <p class="section-lead">Solar and battery-storage systems are protected uses under G.L. c. 40A, §3: a bylaw may not prohibit or unreasonably regulate them except to protect health, safety or welfare. Since the Supreme Judicial Court's Tracer Lane II decision, the Attorney General weighs a bylaw's purpose against its burden on the protected use. The counts come from the ledger on this page.</p>
  <div class="table-wrap"><table class="plain stack"><thead><tr><th scope="col">Bylaw pattern</th><th scope="col">Result</th><th scope="col">Count</th><th scope="col">Recent examples</th></tr></thead><tbody>{pattern_rows}</tbody></table></div>
  <p class="note">The data-center approvals for Shutesbury (case 12047, Jan. 20, 2026) and Templeton (case 12294, Sept. 22, 2026) come from our reading of those letters; the ledger itself covers solar and storage decisions only. Many approvals warn that applying a bylaw to deny a project "would run a serious risk of violating" §3.</p>
</section>

<section aria-labelledby="bytype-title">
  <h2 id="bytype-title">Outcomes by bylaw type and year</h2>
  <div class="cols">
    <div class="table-wrap"><table class="plain stack">{cnt_head.format('Bylaw type')}<tbody>{type_rows}</tbody></table></div>
    <div class="table-wrap"><table class="plain stack">{cnt_head.format('Year')}<tbody>{year_rows}</tbody></table></div>
  </div>
</section>

<section aria-labelledby="ledger-title">
  <h2 id="ledger-title">The full ledger</h2>
  <p class="section-lead">Each decision letter links to the Attorney General's public portal. Court rulings and city ordinances are included for context.</p>
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


# ---------------------------------------------------------------- beta (/pricing)
# The page states what is free and that a paid plan comes later, with no prices. Plan definitions and the
# (disabled) Stripe checkout live in site/api/checkout.js and site/pricing.js and are not rendered here.

def build_pricing(ctx):
    body = """
<div class="wrap"><div class="prose">
<section class="hero compact" aria-labelledby="pricing-title">
  <h1 id="pricing-title">Free during the beta</h1>
  <p class="lead">351 Watch is in its founding beta. Everything on the site is free, and you don't need an account or a card.</p>
</section>
<p class="notice" id="checkout-note" role="status" hidden></p>
<section aria-labelledby="free-title">
  <h2 id="free-title">Free now</h2>
  <ul class="plain-list">
    <li>Every public page: town pages, topic pages, the Massachusetts tracker and the Attorney General ledger.</li>
    <li>A watchlist for your area, with its own page, RSS, JSON and calendar feeds, and a daily Slack, Teams or Discord message.</li>
  </ul>
  <p class="actions"><a class="btn" href="/watch">Create a watchlist</a></p>
</section>
<section aria-labelledby="later-title">
  <h2 id="later-title">After the beta</h2>
  <p>Watching many places at once will become a paid plan. There is nothing to buy today.</p>
</section>
</div></div>
"""
    return page(ctx, "Free during the beta | 351 Watch",
                "351 Watch is free during its founding beta: every public page, and a watchlist for your area with feeds "
                "and daily messages. Watching many places at once will be a paid plan later.",
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
