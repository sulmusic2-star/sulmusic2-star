"""Render the static 351 Watch site from data/tracker.json and data/agenda_hits.json.

Usage: python3 build.py   (writes site/index.html, site/privacy.html, site/data/*.json)
"""

import json
import shutil
from datetime import date, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE = ROOT / "site"

STATUS_GROUPS = {
    "active": ({"Adopted", "Approved by AG", "Enacted", "In effect"}, "In effect or adopted"),
    "pending": ({"Proposed", "Hearing held", "On warrant", "Pending at Legislature"}, "Pending"),
    "cleared": ({"Rejected", "Withdrawn", "Expired", "Disapproved by AG", "Sent to study"}, "Not in effect"),
}

TOPIC_LABELS = {
    "battery_storage": "Battery storage",
    "solar": "Solar",
    "moratorium": "Moratorium",
    "clean_energy_siting": "Consolidated permit",
    "40b_comprehensive_permit": "40B housing",
    "wireless_telecom": "Wireless / cell tower",
    "zoning_amendment": "Zoning amendment",
}

ENERGY_TOPICS = {"battery_storage", "solar", "clean_energy_siting"}


def load(name, default):
    path = DATA / name
    return json.loads(path.read_text()) if path.exists() else default


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
        return datetime.strptime(value, "%Y-%m-%d").strftime("%b %-d, %Y")
    except ValueError:
        return escape(value)


def sources_html(sources):
    links = "".join(
        f'<li><a href="{escape(s["url"])}" rel="nofollow noopener" target="_blank">{escape(s["title"])}</a></li>'
        for s in sources
        if s.get("url")
    )
    return f'<ul class="sources">{links}</ul>' if links else ""


def tracker_rows(items):
    rows = []
    for item in sorted(items, key=lambda i: i.get("key_date") or "", reverse=True):
        group = status_group(item)
        topic = item.get("topic", "")
        rows.append(
            f"""<tr data-group="{group}" data-topic="{escape(topic.lower())}" data-county="{escape(item.get('county', ''))}">
  <td class="town"><b>{escape(item['town'])}</b><small>{escape(item.get('county', ''))} County</small></td>
  <td>{escape(item.get('action', ''))}<br><small>{escape(topic)}</small></td>
  <td><span class="badge {group}">{escape(item.get('status', ''))}</span></td>
  <td class="when">{fmt_date(item.get('key_date'))}<small>{escape(item.get('date_label', ''))}</small></td>
  <td class="col-summary"><p class="summary">{escape(item.get('summary', ''))}</p>{sources_html(item.get('sources', []))}</td>
</tr>"""
        )
    return "\n".join(rows)


def framework_cards(framework):
    cards = []
    for f in framework:
        date_html = f'<p class="date">{fmt_date(f.get("date"))}</p>' if f.get("date") else ""
        cards.append(
            f"""<article class="card"><h3>{escape(f['title'])}</h3>{date_html}<p>{escape(f.get('summary', ''))}</p>{sources_html(f.get('sources', []))}</article>"""
        )
    return "\n".join(cards)


def featured_hits(hits, limit):
    """Most recent clean-energy hits first, one per document, then other land-use hits."""
    seen, energy, other = set(), [], []
    for h in sorted(hits, key=lambda h: h.get("meeting_date") or "", reverse=True):
        if h["source_url"] in seen:
            continue
        seen.add(h["source_url"])
        (energy if ENERGY_TOPICS & set(h.get("topics", [])) else other).append(h)
    return (energy + other)[:limit]


def hit_cards(hits, limit=15):
    ordered = featured_hits(hits, limit)
    if not ordered:
        return '<p class="empty">The first automated scan is still running. Check back shortly.</p>'
    cards = []
    for h in ordered:
        tags = "".join(f'<span class="tag">{escape(TOPIC_LABELS.get(t, t))}</span>' for t in h.get("topics", []))
        when = fmt_date(h.get("meeting_date")) or "Date not listed"
        cards.append(
            f"""<article class="hit">
  <header><b>{escape(h['town'])}</b><span class="meta">{escape(h.get('board', ''))} · {when}</span></header>
  <p>“{escape(h.get('snippet', ''))}”</p>
  <div class="tags">{tags} <a href="{escape(h['source_url'])}" rel="nofollow noopener" target="_blank">Agenda</a></div>
</article>"""
        )
    return "\n".join(cards)


def page(title, description, body, path=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/styles.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5f4a'/%3E%3Ctext x='16' y='21' font-family='Arial' font-size='13' font-weight='700' fill='white' text-anchor='middle'%3E351%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="/">351<span>Watch</span></a>
  <nav class="top" aria-label="Main">
    <a href="/#tracker">Tracker</a>
    <a href="/#agendas">From town agendas</a>
    <a href="/#rules">State rules</a>
    <a class="cta" href="/#alerts">Get alerts</a>
  </nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>351 Watch compiles public records that Massachusetts towns post under the Open Meeting Law, plus state and legislative sources. It is informational only and not legal advice. Always confirm dates and terms with the town clerk or the cited source.</p>
  <p><a href="/data/tracker.json">Download the tracker data (JSON)</a> · <a href="/privacy">Privacy</a> · <a href="/privacy#contact">Corrections and contact</a></p>
</div></footer>
<script src="/app.js" defer></script>
</body>
</html>
"""


def build_index(tracker, hits_doc):
    items = tracker.get("items", [])
    hits = hits_doc.get("hits", [])
    groups = {g: sum(1 for i in items if status_group(i) == g) for g in ("active", "pending", "cleared")}
    towns = len({i["town"] for i in items})
    counties = sorted({i.get("county", "") for i in items if i.get("county")})
    county_opts = "".join(f'<option value="{escape(c)}">{escape(c)}</option>' for c in counties)
    verified = fmt_date(tracker.get("generated", date.today().isoformat()))
    scanned = hits_doc.get("documents_scanned", 0)
    automated = hits_doc.get("towns_automated", 0)
    attempted = hits_doc.get("towns_attempted", 0)
    scan_time = hits_doc.get("generated", "")[:10]

    body = f"""
<div class="wrap">
<section class="hero" aria-labelledby="hero-title">
  <p class="eyebrow">Massachusetts clean-energy siting</p>
  <h1 id="hero-title">Battery storage and solar moratoria, town by town</h1>
  <p class="lead">A free, source-linked tracker of local moratoria, special acts and new permit rules for battery storage and solar across Massachusetts — plus live items pulled from town board agendas.</p>
  <div class="actions"><a class="btn" href="#alerts">Get agenda alerts</a><a class="btn ghost" href="#tracker">Browse the tracker</a></div>
  <div class="stats" role="list">
    <div class="stat" role="listitem"><b>{towns}</b><span>towns with tracked actions</span></div>
    <div class="stat" role="listitem"><b>{groups['pending']}</b><span>pending actions</span></div>
    <div class="stat" role="listitem"><b>{groups['active']}</b><span>in effect or adopted</span></div>
    <div class="stat" role="listitem"><b>{len(hits)}</b><span>agenda items flagged in the latest scan</span></div>
  </div>
</section>

<section id="rules" aria-labelledby="rules-title">
  <h2 id="rules-title">The state rules changed on October 1</h2>
  <p class="section-lead">Every town must now offer a single consolidated permit for small clean-energy projects, with a 12-month decision clock. These are the rules everything below is measured against.</p>
  <div class="cards">{framework_cards(tracker.get('framework', []))}</div>
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
{tracker_rows(items)}
      </tbody>
    </table>
  </div>
</section>

<section id="agendas" aria-labelledby="agendas-title">
  <h2 id="agendas-title">From town agendas</h2>
  <p class="section-lead">Our crawler read {scanned} recent agendas from {automated} of {attempted} sample towns (scan of {fmt_date(scan_time) or 'today'}) and flagged items on battery storage, solar, moratoria, consolidated permits, 40B housing, wireless facilities and zoning amendments. Subscribers will get these for the towns they choose, every day.</p>
  <div class="hits">{hit_cards(hits)}</div>
</section>

<section id="alerts" aria-labelledby="alerts-title">
  <div class="signup-grid">
    <div>
      <h2 id="alerts-title">Know before the hearing</h2>
      <p class="section-lead">351 Watch will check planning boards, zoning boards of appeal, conservation commissions, select boards and town-meeting warrants in every Massachusetts town each day, and email you when your towns post something you track.</p>
      <ul class="ticks">
        <li>Alerts by town and topic: battery storage, solar, moratoria, consolidated permits, 40B, wireless, zoning</li>
        <li>Every alert links to the original agenda or warrant</li>
        <li>Weekly digest and spreadsheet export</li>
      </ul>
      <div class="plans" aria-label="Planned pricing">
        <div class="plan"><b>Town pack</b><span class="price">$79/mo</span><p>Up to 15 towns, one user.</p></div>
        <div class="plan"><b>Statewide</b><span class="price">$299/mo</span><p>All 351 towns, three users, exports.</p></div>
      </div>
      <p class="form-note">Planned pricing. Joining the waitlist is free and doesn't commit you to anything.</p>
    </div>
    <form id="signup-form" class="signup" novalidate>
      <label>Work email<input name="email" type="email" autocomplete="email" required></label>
      <label>Your role
        <select name="role">
          <option value="developer">Solar or storage developer</option>
          <option value="attorney">Land-use or energy attorney</option>
          <option value="consultant">Consultant or engineer</option>
          <option value="municipal">Town staff or board member</option>
          <option value="advocacy">Advocacy or community group</option>
          <option value="journalist">Journalist or researcher</option>
          <option value="other">Other</option>
        </select>
      </label>
      <label>Organization <small>(optional)</small><input name="organization" autocomplete="organization"></label>
      <label>Towns you care about <small>(optional)</small><input name="towns" placeholder="e.g. Sturbridge, Lee, Carver"></label>
      <label>What would you want alerts on? <small>(optional)</small><textarea name="wants"></textarea></label>
      <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
      <input type="hidden" name="source" value="tracker">
      <button class="btn" type="submit">Join the waitlist</button>
      <p class="form-status" role="status" aria-live="polite"></p>
      <p class="form-note">We'll only use your email to contact you about 351 Watch. See our <a href="/privacy">privacy note</a>.</p>
    </form>
  </div>
</section>
</div>
"""
    return page(
        "Massachusetts Battery Storage & Solar Moratorium Tracker | 351 Watch",
        "Free, source-linked tracker of battery storage and solar moratoria, special acts and consolidated permit rules in Massachusetts towns, plus items from town board agendas.",
        body,
    )


def build_privacy():
    body = """
<div class="wrap prose">
<h1>Privacy and contact</h1>
<p>351 Watch is a new service. This note explains what we collect and why.</p>
<h2>What we collect</h2>
<p>If you join the waitlist, we store the email address, role, organization, towns and notes you enter, and the time you signed up. If you send a correction or message, we store your email and message.</p>
<h2>How we use it</h2>
<p>Only to contact you about 351 Watch — mainly to tell you when alerts open for your towns — and to decide which towns and topics to cover first. We don't sell or share it, and we don't add you to anyone else's mailing list.</p>
<h2>Where it's kept</h2>
<p>Submissions are stored in private, access-controlled cloud storage at our hosting provider, Vercel. They are not publicly viewable.</p>
<h2>How long we keep it</h2>
<p>Until you ask us to delete it, or for 12 months if the paid service doesn't launch, whichever comes first.</p>
<h2>About the data on this site</h2>
<p>The tracker uses public records: agendas and warrants that towns must post under the Massachusetts Open Meeting Law, legislative records, and news reports. Our crawler reads only publicly posted pages, identifies itself, follows robots.txt and limits how often it visits each town's website.</p>
<h2 id="contact">Corrections, removal requests and contact</h2>
<form id="contact-form" class="signup" novalidate>
  <label>Your email<input name="email" type="email" autocomplete="email" required></label>
  <label>Type of request
    <select name="kind">
      <option value="correction">Correction to the tracker</option>
      <option value="removal">Delete my waitlist data</option>
      <option value="message">Other message</option>
    </select>
  </label>
  <label>Message<textarea name="message" required></textarea></label>
  <div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
  <button class="btn" type="submit">Send</button>
  <p class="form-status" role="status" aria-live="polite"></p>
</form>
</div>
"""
    return page("Privacy and contact | 351 Watch", "How 351 Watch handles waitlist information, and how to send corrections.", body)


def main():
    tracker = load("tracker.json", {"generated": date.today().isoformat(), "framework": [], "items": []})
    hits = load("agenda_hits.json", {"hits": []})
    (SITE / "data").mkdir(exist_ok=True)
    (SITE / "index.html").write_text(build_index(tracker, hits))
    (SITE / "privacy.html").write_text(build_privacy())
    if (DATA / "tracker.json").exists():
        shutil.copyfile(DATA / "tracker.json", SITE / "data" / "tracker.json")
    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /api/\n")
    print(f"built: {len(tracker.get('items', []))} tracker rows, {len(hits.get('hits', []))} agenda hits")


if __name__ == "__main__":
    main()
