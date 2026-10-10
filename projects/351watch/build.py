"""Render the static 351 Watch site from the data/ files.

Inputs: tracker.json, agenda_hits_ma_all.json (falls back to the 30-town agenda_hits.json),
towns_ma_all.json, ma_census_summary.json, leadtime_ma_all.json, ag_decisions.json.
Usage: python3 build.py   (writes site/index.html, site/proof.html, site/privacy.html,
site/robots.txt and site/manifest.txt, the list of files the deploy step fetches)
"""

import json
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

BOARD_LABELS = {
    "planning_board": "Planning",
    "zoning_board_of_appeals": "ZBA",
    "conservation_commission": "Conservation",
    "select_board": "Select Board / Council",
    "town_meeting": "Town Meeting",
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

STATIC_FILES = ["index.html", "proof.html", "privacy.html", "styles.css", "app.js", "robots.txt"]


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
    """Clean-energy items for meetings still ahead first (soonest first), then the most
    recent clean-energy items, then other land-use items; one card per document."""
    seen, upcoming, energy, other = set(), [], [], []
    for h in sorted(hits, key=lambda h: h.get("meeting_date") or "", reverse=True):
        if h["source_url"] in seen:
            continue
        seen.add(h["source_url"])
        if not ENERGY_TOPICS & set(h.get("topics", [])):
            other.append(h)
        elif h.get("days_before_meeting", -1) > 0:
            upcoming.append(h)
        else:
            energy.append(h)
    upcoming.sort(key=lambda h: h.get("meeting_date") or "")
    return (upcoming + energy + other)[:limit]


def lead_note(h):
    days = h.get("days_before_meeting", -1)
    if days >= 1:
        return f'<span class="leadtime">First seen {days:.0f} days before the meeting</span>'
    if days > 0:
        return '<span class="leadtime">First seen the day before the meeting</span>'
    return ""


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
  <div class="tags">{tags} {lead_note(h)} <a href="{escape(h['source_url'])}" rel="nofollow noopener" target="_blank">Agenda</a></div>
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
    <a href="/proof">Proof</a>
    <a class="cta" href="/#alerts">Get alerts</a>
  </nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>351 Watch compiles public records that Massachusetts towns post under the Open Meeting Law, plus state and legislative sources. It is informational only and not legal advice. Always confirm dates and terms with the town clerk or the cited source.</p>
  <p><a href="/proof">Coverage and method</a> · <a href="/privacy">Privacy</a> · <a href="/privacy#contact">Corrections and contact</a></p>
</div></footer>
<script src="/app.js" defer></script>
</body>
</html>
"""


def build_index(tracker, hits_doc, census, ag):
    items = tracker.get("items", [])
    hits = hits_doc.get("hits", [])
    hit_towns = len({h["town"] for h in hits})
    upcoming = sum(1 for h in hits if h.get("days_before_meeting", -1) > 0)
    monitored = census.get("automated", {}).get("towns", 0)
    struck = ag_moratorium_record(ag)
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
    <div class="stat" role="listitem"><b>{monitored} of 351</b><span>towns' agendas read automatically</span></div>
    <div class="stat" role="listitem"><b>{len(hits)}</b><span>agenda items flagged in {hit_towns} towns</span></div>
    <div class="stat" role="listitem"><b>{upcoming}</b><span>flagged for meetings still ahead</span></div>
    <div class="stat" role="listitem"><b>{struck['disapproved']} of {struck['total']}</b><span>town moratoria struck down by the Attorney General since 2024</span></div>
  </div>
  <p class="form-note">Every number links to its evidence on the <a href="/proof">coverage and method</a> page.</p>
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
  <p class="section-lead">Our crawler read {scanned:,} agendas from {automated} Massachusetts towns (scan of {fmt_date(scan_time) or 'today'}) and flagged items on battery storage, solar, moratoria, consolidated permits, 40B housing, wireless facilities and zoning amendments. Items for meetings still ahead are shown first, with when we first saw them. Subscribers will get these for the towns they choose, every day. <a href="/proof">How we measure this</a>.</p>
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


def ag_moratorium_record(ag, since="2024-01-01"):
    """Solar/BESS moratorium articles the Attorney General ruled on since `since`."""
    rows = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") == "moratorium"
            and (r.get("decision_date") or "") >= since and r.get("outcome") in ("approved", "disapproved")]
    articles = lambda r: max(1, r.get("article", "").count(" and ") + 1)  # "Articles 26 and 27" counts 2
    return {
        "rows": sorted(rows, key=lambda r: r["decision_date"], reverse=True),
        "total": sum(articles(r) for r in rows),
        "disapproved": sum(articles(r) for r in rows if r["outcome"] == "disapproved"),
        "towns": len({r["town"] for r in rows}),
    }


def pct(x):
    return f"{x * 100:.0f}%"


def coverage_rows(towns):
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
        pop = t.get("pop_2024_est") or t.get("pop_2020") or 0
        rows.append(f"""<tr data-group="{group}">
  <td class="town"><b>{escape(t['town'])}</b><small>{escape(t.get('county', ''))} County</small></td>
  <td class="num">{pop:,}</td>
  <td><span class="badge {cls}">{escape(status)}</span></td>
  <td><div class="pills">{pills}</div></td>
</tr>""")
    return "\n".join(rows)


def build_proof(census, leadtime, hits_doc, ag, towns_doc):
    auto = census.get("automated", {})
    boards = census.get("boards", {})
    first = leadtime.get("summary", {}).get("first_posting_only", {})
    by_board = leadtime.get("by_board_first_posting_only", {})
    window = leadtime.get("meeting_window", {})
    hits = hits_doc.get("hits", [])
    ahead = sorted(h["days_before_meeting"] for h in hits if h.get("days_before_meeting", -1) > 0)
    median_ahead = ahead[len(ahead) // 2] if ahead else 0
    record = ag_moratorium_record(ag)
    regulating = [r for r in ag if r.get("record_type") == "ag_decision" and r.get("bylaw_type") != "moratorium"
                  and r.get("outcome") in ("approved", "approved in part", "disapproved")]
    reg_ok = sum(1 for r in regulating if r["outcome"] in ("approved", "approved in part"))
    not_auto = census.get("not_automated", {})
    blocked = sorted(not_auto.items(), key=lambda kv: -kv[1]["towns"])

    board_rows = "".join(
        f"<tr><td>{BOARD_LABELS[k]}</td><td class='num'>{v['towns']} of {v['of']}</td><td class='num'>{pct(v['share'])}</td></tr>"
        for k, v in boards.items() if k in BOARD_LABELS)
    lead_rows = "".join(
        f"<tr><td>{BOARD_LABELS.get(k, k)}</td><td class='num'>{v['median_days']:.0f} days</td>"
        f"<td class='num'>{v['p10_days']:.0f} days</td><td class='num'>{pct(v['share_ge_48h_before_meeting_day'])}</td><td class='num'>{v['n']:,}</td></tr>"
        for k, v in by_board.items() if k in BOARD_LABELS)
    blocked_rows = "".join(
        f"<tr><td>{escape(REASON_LABELS.get(k, k))}</td><td class='num'>{v['towns']}</td><td>{escape(', '.join(v.get('examples', [])[:6]))}</td></tr>"
        for k, v in blocked)
    ag_rows = "".join(
        f"""<tr><td class="town"><b>{escape(r['town'])}</b><small>{escape(r.get('article', ''))}</small></td>
<td class="when">{fmt_date(r['decision_date'])}</td><td><span class="badge {'active' if r['outcome'] == 'disapproved' else 'cleared'}">{escape(r['outcome'].capitalize())}</span></td>
<td><a href="{escape(r['letter_url'])}" rel="nofollow noopener" target="_blank">Decision letter, case {escape(str(r.get('case_number', '')))}</a></td></tr>"""
        for r in record["rows"])

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
    <div class="stat" role="listitem"><b>{record['disapproved']} of {record['total']}</b><span>moratoria struck down by the AG since 2024</span></div>
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
  <p class="form-note">Our own timing: of the {len(hits):,} items flagged in the latest statewide scan, {len(ahead)} were for meetings still ahead, first seen a median {median_ahead:.0f} days before the meeting day. Each item records when we first fetched its agenda.</p>
</section>

<section aria-labelledby="ag-title">
  <h2 id="ag-title">Will a moratorium survive? The Attorney General's record</h2>
  <p class="section-lead">Town bylaws in Massachusetts take effect only after Attorney General review (cities are not reviewed). We read all 2,719 decision letters issued from January 2022 to October 10, 2026. Since 2024 she has ruled on {record['total']} solar or battery-storage moratorium articles in {record['towns']} towns and disapproved {record['disapproved']}, citing the state's zoning protection for solar and storage (G.L. c. 40A, §3). Bylaws that regulate rather than ban fared differently: {reg_ok} of {len(regulating)} were approved in whole or in part. Data-center moratoria have been approved, because data centers aren't a protected use.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Town and article</th><th scope="col">Decision</th><th scope="col">Outcome</th><th scope="col">Source</th></tr></thead><tbody>{ag_rows}</tbody></table></div>
</section>

<section aria-labelledby="gaps-title">
  <h2 id="gaps-title">Towns we can't read yet, and why</h2>
  <p class="section-lead">{351 - auto.get('towns', 0)} towns aren't monitored automatically yet. Most block automated visitors or ask crawlers not to visit; we respect that and don't work around it. We'll ask those towns and their vendors for access.</p>
  <div class="table-wrap"><table class="plain"><thead><tr><th scope="col">Reason</th><th scope="col">Towns</th><th scope="col">Examples</th></tr></thead><tbody>{blocked_rows}</tbody></table></div>
</section>

<section aria-labelledby="towns-title">
  <h2 id="towns-title">All 351 cities and towns</h2>
  <div class="filters">
    <label>Status<select id="c-status"><option value="">All</option><option value="monitored">Monitored</option><option value="not">Not yet</option></select></label>
    <label>Search<input id="c-search" type="search" placeholder="Town or county"></label>
    <span class="count" id="c-count" aria-live="polite"></span>
  </div>
  <div class="table-wrap">
    <table id="coverage-table" class="plain">
      <thead><tr><th scope="col">Town</th><th scope="col">Population</th><th scope="col">Status</th><th scope="col">Boards read</th></tr></thead>
      <tbody>
{coverage_rows(towns_doc.get('towns', []))}
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
        "Coverage and Method | 351 Watch",
        "How many Massachusetts towns 351 Watch reads, how far ahead agendas are posted, the Attorney General's record on clean-energy moratoria, and the evidence behind each number.",
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
    hits = load("agenda_hits_ma_all.json", None) or load("agenda_hits.json", {"hits": []})
    census = load("ma_census_summary.json", {})
    leadtime = load("leadtime_ma_all.json", {})
    ag = load("ag_decisions.json", [])
    towns = load("towns_ma_all.json", {"towns": []})
    (SITE / "index.html").write_text(build_index(tracker, hits, census, ag))
    (SITE / "proof.html").write_text(build_proof(census, leadtime, hits, ag, towns))
    (SITE / "manifest.txt").write_text("\n".join(STATIC_FILES) + "\n")
    (SITE / "privacy.html").write_text(build_privacy())
    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /api/\n")
    print(f"built: {len(tracker.get('items', []))} tracker rows, {len(hits.get('hits', []))} agenda hits")


if __name__ == "__main__":
    main()
