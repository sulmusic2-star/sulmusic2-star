#!/usr/bin/env python3
"""Northeast feasibility probe for the 351 Watch agenda crawler.

Glue code only: it imports the (read-only) `watch351` package and reuses its
PoliteFetcher (351WatchBot UA, robots.txt, 1 req/s/host, cache), adapters,
extraction and keyword matcher. Nothing in watch351/ is modified.

    cd crawler
    python3 experiments/northeast_probe.py get URL [--grep REGEX]   # exploration helper
    python3 experiments/northeast_probe.py fingerprint [--towns A,B]
    python3 experiments/northeast_probe.py crawl [--towns A,B] [--days-back 30 --days-ahead 90]

Inputs / outputs (all in projects/351watch/data/, none of them shared with
the Massachusetts pipeline):
    northeast_sample.json         48 towns: state, website, why chosen, source URL
    northeast_towns.json          per-town config: platform, listings, automated / reason
                                  (curated keys are preserved across `fingerprint` runs)
    agenda_hits_northeast.json    crawl output: hits, per-town status, posting lead times
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent          # crawler/
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402

from watch351.adapters import REGISTRY  # noqa: E402
from watch351.adapters.civicplus import CivicPlusAdapter, _slug  # noqa: E402
from watch351.boards import classify_board  # noqa: E402
from watch351.crawl import _dedupe, scan_document  # noqa: E402
from watch351.dates import first_date  # noqa: E402
from watch351.keywords import clean_text  # noqa: E402
from watch351.fetch import FetchError, PoliteFetcher  # noqa: E402
from watch351.keywords import find_hits  # noqa: E402,F401  (used via scan_document)
from watch351.models import Window  # noqa: E402

DATA = ROOT.parent / "data"
SAMPLE = DATA / "northeast_sample.json"
CONFIG = DATA / "northeast_towns.json"
HITS = DATA / "agenda_hits_northeast.json"

log = logging.getLogger("northeast_probe")

# --------------------------------------------------------------------------
# Platform fingerprints (broader than watch351.discover, which only knows
# CivicPlus / CivicClerk / Cloudflare / "generic").
PLATFORM_MARKERS: list[tuple[str, str]] = [
    ("civicplus", r"/AgendaCenter|CivicPlus|civicplus\.com|/Archive\.aspx|CivicAlerts\.aspx"),
    ("civicclerk", r"portal\.civicclerk\.com"),
    ("granicus_govaccess", r"/sites/g/files/vyhlif"),
    ("granicus_viewpublisher", r"granicus\.com/(ViewPublisher|MediaPlayer)|\.granicus\.com"),
    ("legistar", r"legistar\.com"),
    ("boarddocs", r"boarddocs\.com"),
    ("ecode360", r"ecode360\.com"),
    ("municode_meetings", r"municodemeetings\.com|meetings\.municode"),
    ("civicweb_icompass", r"civicweb\.net"),
    ("diligent", r"diligent(oneplatform|\.community)"),
    ("escribe", r"escribemeetings\.com"),
    ("primegov", r"primegov\.com"),
    ("novusagenda", r"novusagenda\.com"),
    ("iqm2", r"iqm2\.com"),
    ("agendaquick_destiny", r"destinyhosted\.com|agendaquick"),
    ("onbase_agendaonline", r"OnBaseAgendaOnline|AgendaOnline"),
    ("laserfiche", r"WebLink/|laserfiche"),
    ("heygov", r"heygov\.com"),
    ("simbli", r"simbli\.eboardsolutions"),
    ("ri_sos_opengov", r"opengov\.sos\.ri\.gov"),
    ("revize", r"revize\.com|/revize/"),
    ("drupal", r'content="Drupal|/sites/default/files/|drupal-settings-json'),
    ("wordpress", r"/wp-content/|/wp-includes/"),
    ("govoffice", r"govoffice\.com|GovOffice"),
    ("squarespace", r"squarespace\.com|static1\.squarespace"),
    ("wix", r"wix\.com|wixstatic"),
    ("google_drive", r"drive\.google\.com|docs\.google\.com"),
    ("municipal_one", r"municipalone|catalis"),
    ("townweb", r"townweb|Town Web Design"),
    ("edmunds_clerkshq", r"clerkshq\.com"),
    ("sitewrench", r"sitewrench"),
]
_BLOCK_MARKERS = {
    "cloudflare": ("challenges.cloudflare.com", "Attention Required! | Cloudflare", "cf-chl", "Just a moment..."),
    "incapsula": ("_Incapsula_Resource", "Incapsula incident"),
    "sucuri": ("Sucuri WebSite Firewall", "sucuri.net/privacy-policy"),
    "akamai": ("Access Denied</H1>", "edgesuite.net"),
}

# Board names used outside Massachusetts. The stock watch351.boards
# classifier is tried first; this one is reported alongside it so the gap
# is measurable.
EXT_BOARDS: list[tuple[str, str, str]] = [
    ("conservation_commission",
     r"conservation commission|inland wetlands|wetlands? (and watercourses )?(commission|agency|board)|"
     r"environmental (commission|advisory|board)|conservation (advisory )?(council|board)|^conservation$|\bconcom\b",
     r"sub-?committee|district|open space committee|inactive|archive"),
    ("zoning_board_of_appeals",
     r"zoning board|board of (zoning )?appeals|\bZBA\b|zoning appeals|zoning hearing board|board of adjustment",
     r"sub-?committee|inactive|archive"),
    ("planning_board",
     r"planning (board|commission)|planning (and|&) zoning|zoning commission|land use (board|commission)|"
     r"plan commission|development review board|planning (and|&) development",
     r"sub-?committee|regional|housing|joint|comprehensive plan|steering|advisory|inactive|archive"),
    ("select_board",
     r"select ?board|board of selectmen|selectmen|(city|town|township|borough|village) council|common council|"
     r"town board|township committee|board of supervisors|board of (township )?commissioners|"
     r"board of (mayor and )?alder(men|s)|city commission|board of trustees",
     r"sub-?committee|(?<!township )committee|joint|ad hoc|housing|rules|youth|library|school|water|sewer|"
     r"cemetery|trust fund|parks|inactive|archive|zzz"),
    ("town_meeting", r"town meeting|warrant", r"advisory|handbook|committee|inactive"),
]


def classify_ext(name: str) -> str | None:
    name = " ".join(name.split())
    for key, inc, exc in EXT_BOARDS:
        if re.search(inc, name, re.I) and not re.search(exc, name, re.I):
            return key
    return None


# Supplemental patterns: NOT part of the watch351 keyword matcher; reported
# separately to measure what the MA-tuned topic list misses elsewhere.
SUPPLEMENTAL = {
    "data_center": re.compile(r"\bdata[\s-]+(?:cent(?:er|re)s?|storage facilit(?:y|ies))\b|\bhyperscale\b|"
                              r"\b(?:crypto(?:currency)?|bitcoin)\s+mining\b", re.I),
    "local_law_or_land_use_ordinance": re.compile(
        r"\b(?:local\s+law|ordinance)\b[^.;]{0,140}?\b(?:amend\w*|establish\w*|moratori\w*)\b[^.;]{0,100}?"
        r"\b(?:zoning|land\s+use|land\s+development|chapter\s+\d+)", re.I),
}


# --------------------------------------------------------------------------
def load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def select(rows: list[dict], names: str | None) -> list[dict]:
    if not names:
        return rows
    wanted = {n.strip().lower() for n in names.split(",")}
    return [r for r in rows if r["town"].lower() in wanted or f"{r['town']}, {r['state']}".lower() in wanted]


def key(t: dict) -> str:
    return f"{t['town']}, {t['state']}"


# ------------------------------------------------------------------ get (explore)
def cmd_get(args, fetcher: PoliteFetcher) -> None:
    try:
        r = fetcher.get(args.url, max_age=6 * 3600)
    except FetchError as e:
        print(f"FETCH ERROR {type(e).__name__}: {e}")
        return
    print(f"status={r.status} final={r.final_url} type={r.content_type} bytes={len(r.body)} cache={r.from_cache}")
    if r.is_pdf:
        return
    html = r.text
    blocked = [k for k, ms in _BLOCK_MARKERS.items() if any(m in html for m in ms)]
    plats = [p for p, rx in PLATFORM_MARKERS if re.search(rx, html, re.I)]
    print(f"platform markers: {plats}  block markers: {blocked}")
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    print(f"title: {title[:120]}")
    rx = re.compile(args.grep, re.I) if args.grep else None
    n = 0
    for a in soup.find_all("a", href=True):
        text = " ".join(a.get_text(" ", strip=True).split())
        href = urljoin(r.final_url, a["href"].strip())
        if rx and not rx.search(f"{text} {href}"):
            continue
        print(f"  [{text[:70]}] {href}")
        n += 1
        if n >= args.limit:
            print("  ...")
            break
    if args.text:
        body = soup.find("main") or soup.body or soup
        print(clean_text(body.get_text(" ", strip=True))[: args.text])


# ------------------------------------------------------------------ fingerprint
def fingerprint_town(fetcher: PoliteFetcher, sample: dict, cur: dict) -> dict:
    cfg = {**{k: sample[k] for k in ("town", "state", "website")}, **cur}
    cfg["website"] = cur.get("website") or sample["website"]
    fp: dict = {"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        home = fetcher.get(cfg["website"].rstrip("/") + "/", max_age=24 * 3600)
    except FetchError as e:
        fp["error"] = f"{type(e).__name__}: {e}"[:300]
        cfg["fingerprint"] = fp
        if not cur.get("reason"):
            cfg.update(automated=False, reason=f"homepage not fetchable: {fp['error']}")
        return cfg
    html = home.text
    fp.update(status=home.status, final_url=home.final_url)
    fp["block_markers"] = [k for k, ms in _BLOCK_MARKERS.items() if any(m in html for m in ms)]
    fp["platform_markers"] = [p for p, rx in PLATFORM_MARKERS if re.search(rx, html, re.I)]
    soup = BeautifulSoup(html, "lxml")
    site_host = urlsplit(home.final_url).netloc.lower()
    vendor_links = set()
    for a in soup.find_all("a", href=True):
        h = urlsplit(urljoin(home.final_url, a["href"])).netloc.lower()
        if h and h != site_host and any(re.search(rx, h, re.I) for _, rx in PLATFORM_MARKERS[:22]):
            vendor_links.add(h)
    fp["vendor_hosts_linked"] = sorted(vendor_links)
    cfg["fingerprint"] = fp

    if home.status in (401, 403, 429, 503) and fp["block_markers"]:
        if not cur.get("reason"):
            cfg.update(automated=False, platform=None,
                       reason=f"{'/'.join(fp['block_markers'])} bot challenge on homepage (HTTP {home.status}); not bypassed")
        return cfg
    if not home.ok:
        if not cur.get("reason"):
            cfg.update(automated=False, reason=f"homepage HTTP {home.status}")
        return cfg

    if "civicplus" in fp["platform_markers"] and cur.get("platform") in (None, "civicplus"):
        cp = CivicPlusAdapter(fetcher)
        base = f"{urlsplit(home.final_url).scheme}://{site_host}"
        try:
            cats = cp.categories(base)
        except FetchError as e:
            cats = []
            fp["agendacenter_error"] = str(e)[:200]
        fp["agendacenter_categories"] = len(cats)
        if cats:
            stock = {n: classify_board(n) for _, n in cats}
            ext = {n: classify_ext(n) for _, n in cats}
            fp["stock_classifier_boards"] = sorted({v for v in stock.values() if v})
            fp["extended_classifier_boards"] = sorted({v for v in ext.values() if v})
            fp["categories_missed_by_stock_classifier"] = sorted(n for n in ext if ext[n] and not stock[n])
            cfg["platform"] = "civicplus"
            cfg["website"] = base
            listings = []
            for cid, name in cats:
                k = stock[name] or ext[name]
                if k:
                    listings.append({"board": name, "board_key": k, "category_id": cid,
                                     "url": f"{base}/AgendaCenter/{_slug(name)}-{cid}",
                                     "classified_by": "stock" if stock[name] else "extended"})
            cfg["listings"] = listings
            cfg["boards_found"] = sorted({l["board_key"] for l in listings})
            if listings and "reason" not in cur:
                cfg["automated"] = True
    if fp["platform_markers"] and "civicclerk" in fp["platform_markers"]:
        m = re.search(r"https?://([a-z0-9-]+)\.portal\.civicclerk\.com", html, re.I)
        if m:
            fp["civicclerk_tenant"] = m.group(1).lower()
    return cfg


# --------------------------------------------------------------------------
# Hand-curated facts from manual inspection (2026-10-10), applied on top of
# the automatic fingerprint. `listings` here are watch351 "generic" adapter
# listings unless the platform says otherwise. Every reason below was
# observed with 351WatchBot through PoliteFetcher.
def _gl(board, key_, url, pattern, exclude=None, resolve=False):
    d = {"board": board, "board_key": key_, "url": url, "link_pattern": pattern}
    if exclude:
        d["exclude_pattern"] = exclude
    if resolve:
        d["resolve_pdf"] = True
    return d


_AS = "https://www.agendasuite.org/iip/groton"
_VG = "https://www.vergennes.org/government"
_EJ = "https://www.essexjunction.gov/meeting-calendar"
_CLAY = "https://townofclayny.gov/minutes-agendas?field_board_value="
_EW = "https://www.eastwhiteland.org/government/agenda_minutes/"
_UB = "https://upperburrelltwp.com/"
_NEP = "https://neptunetownship.org/agendas-minutes/"
_COV = "https://covingtontwp.org/document-category/2026-meeting-agendas/"

CURATED: dict[str, dict] = {
    # ---------------- CT
    "Groton, CT": {"platform": "generic", "agenda_platform": "AgendaSuite IIP (Provox Systems)", "automated": True,
                   "note": "Agendas live on agendasuite.org/iip/groton. Only the portal homepage links meetings with "
                           "dated link text (about one week either side of today); the full meeting list uses "
                           "'Details' links that the generic adapter deliberately skips. Documents are HTML "
                           "meeting pages with the agenda outline.",
                   "listings": [
                       _gl("Planning & Zoning Commission", "planning_board", _AS, r"for Planning & Zoning Commission"),
                       _gl("Zoning Board of Appeals", "zoning_board_of_appeals", _AS, r"for Zoning Board of Appeals"),
                       _gl("Inland Wetlands Agency", "conservation_commission", _AS, r"for Inland Wetlands Agency"),
                       _gl("Conservation Commission", "conservation_commission", _AS, r"for Conservation Commission"),
                       _gl("Town Council", "select_board", _AS, r"for Town Council(?! Committee)"),
                   ]},
    "New Milford, CT": {"automated": False, "agenda_platform": "QScend CMS (per robots.txt paths; site not fetched)",
                        "reason": "robots.txt sets Crawl-delay: 15 for all agents; watch351.fetch skips hosts asking "
                                  "for more than 10 s. Technically automatable at 1 request per 15 s if the cap is raised."},
    "Cornwall, CT": {"agenda_platform": "WordPress (behind Cloudflare)"},
    "New Haven, CT": {"agenda_platform": "Legistar (Board of Alders) + city site behind Akamai",
                      "reason": "newhavenct.gov returns HTTP 403 'Access Denied' (Akamai edge) to 351WatchBot; "
                                "newhavenct.legistar.com/Calendar.aspx returned a 19-byte empty body. Not bypassed."},
    "East Lyme, CT": {"agenda_platform": "WordPress (eltownhall.com)",
                      "reason": "robots.txt allows only named bots (Bingbot, Googlebot, ...) and ends with "
                                "'User-agent: * / Disallow: /'."},
    # ---------------- RI
    "Hopkinton, RI": {"agenda_platform": "unknown (Cloudflare); agendas are also filed on the RI SOS Open Meetings portal"},
    "Exeter, RI": {"agenda_platform": "unknown (Cloudflare); agendas are also filed on the RI SOS Open Meetings portal"},
    "Johnston, RI": {"platform": "clerkbase", "agenda_platform": "ClerkBase (clerkshq.com/johnston-ri)", "automated": False,
                     "reason": "Town site (CivicPlus CMS, no AgendaCenter) links Town Council, Planning Board and Zoning "
                               "Board agendas to ClerkBase, whose browse tree is loaded by JavaScript; no static listing "
                               "for the generic adapter. Needs a ClerkBase adapter (or the RI SOS portal)."},
    "West Greenwich, RI": {"note": "AgendaCenter has only a Town Council category (no agendas in the window); "
                                   "Planning Board / ZBA agendas are not on the town site (presumably only on the "
                                   "RI SOS Open Meetings portal; not verified)."},
    "North Kingstown, RI": {"drop_listings": r"Building Code"},
    # ---------------- NH
    "Concord, NH": {"platform": "generic", "agenda_platform": "Legistar (City Council) + CivicPlus CMS without AgendaCenter",
                    "automated": True,
                    "note": "Legistar Calendar.aspx lists every body on one page; the generic adapter cannot split "
                            "bodies, so all are labeled City Council. CivicPlus Archive Center (AMID=46) stopped in 2015.",
                    "listings": [_gl("City Council (Legistar calendar)", "select_board",
                                     "https://concordnh.legistar.com/Calendar.aspx", r"M=A&ID=")]},
    "Wakefield, NH": {"agenda_platform": "Granicus govAccess (vyhlif) behind Cloudflare"},
    # ---------------- VT
    "Vergennes, VT": {"platform": "generic_revize", "agenda_platform": "Revize", "automated": True,
        "note": "Revize: www host 302-redirects documents to cms*.revize.com, whose robots.txt allows only URLs ending in .pdf; Revize links carry a ?t= cache-buster, so the stock generic adapter is refused by robots (verified 2026-10-10 on Vergennes). Crawled with the probe shim generic_revize, which drops ?t=.", 
                      "listings": [
                          _gl("City Council", "select_board", f"{_VG}/city_council/city_council_agendas_and_minutes.php", r"^Agenda\b"),
                          _gl("Development Review Board", "planning_board",
                              f"{_VG}/development_review_board/development_review_board_agendas_and_minutes.php", r"agenda"),
                      ]},
    "Vernon, VT": {"platform": "heygov", "agenda_platform": "TownWeb site + HeyGov meetings widget", "automated": False,
                   "reason": "/meetings is rendered client-side from api.heygov.com, whose robots.txt is "
                             "'User-agent: * Disallow: /' (served as text/html, which watch351.fetch would wrongly "
                             "treat as allow-all; honored here)."},
    "Royalton, VT": {"platform": "generic", "agenda_platform": "Revize", "automated": False,
                     "reason": "No agendas online: Selectboard page says notices are posted on bulletin boards at the "
                               "Town Office, laundromat and Royalton Academy; Planning Commission page has only the Town Plan."},
    "Essex Junction, VT": {"platform": "generic", "agenda_platform": "TYPO3 CMS (fileadmin) meeting pages", "automated": True,
                           "note": "Meeting calendar shows upcoming meetings only; each meeting page links the agenda PDF.",
                           "listings": [
                               _gl("City Council", "select_board", _EJ, r"^City Council \d", resolve=True),
                               _gl("Planning Commission", "planning_board", _EJ, r"^Planning Commission \d", resolve=True),
                               _gl("Development Review Board", "planning_board", _EJ, r"^Development Review Board \d", resolve=True),
                           ]},
    "Northfield, VT": {"platform": "generic", "agenda_platform": "Wix", "automated": False,
                       "reason": "Wix site; 'Select Board Agendas & Minutes' page links dated PDFs but none from 2026 "
                                 "(latest 2025, and they are minutes); no current agenda listing in static HTML."},
    "South Burlington, VT": {},
    # ---------------- ME
    "Scarborough, ME": {"platform": "diligent", "agenda_platform": "Diligent Community (iCompass)", "automated": False,
                        "reason": "Agendas are on scarboroughmaine.community.diligentoneplatform.com, whose robots.txt "
                                  "disallows 351WatchBot."},
    # ---------------- NY
    "Clay, NY": {"platform": "generic", "agenda_platform": "Drupal", "automated": True,
                 "note": "The ?field_board_value filter does not filter the 'recent agendas' block, so each listing "
                         "also matches on the board name in the file name.",
                 "listings": [
                     _gl("Planning Board", "planning_board", _CLAY + "Planning%20Board", r"View Agenda.*Planning"),
                     _gl("Zoning Board of Appeals", "zoning_board_of_appeals", _CLAY + "Zoning%20Board%20of%20Appeals",
                         r"View Agenda.*(Zoning|ZBA)"),
                     _gl("Town Board", "select_board", _CLAY + "Town%20Board", r"View Agenda.*Town"),
                 ]},
    "Lysander, NY": {"platform": "generic", "agenda_platform": "Drupal", "automated": True,
                     "note": "One /board-meetings page mixes Town Board, Planning Board and ZBA agendas; several file "
                             "names carry no separators (a10082026pb_0.pdf, 100526zbaagenda.pdf) so their dates do not parse.",
                     "listings": [_gl("Board Meetings (Town Board / Planning / ZBA)", "mixed",
                                      "https://lysanderny.gov/board-meetings", r"agenda", r"minutes|materials")]},
    "Waterford, NY": {"agenda_platform": "Drupal (behind Cloudflare)"},
    "LaGrange, NY": {"platform": "generic", "agenda_platform": "WordPress", "automated": False,
                     "reason": "Board pages' 'Agendas' link is a HubSpot email-tracking redirect (hs-sales-engage.com) "
                               "to an external host, not an agenda listing; no agenda files on the town site."},
    "Dover, NY": {"platform": "civicclerk", "tenant": "doverny", "agenda_platform": "CivicClerk (+ CivicPlus CMS)"},
    # ---------------- NJ
    "Andover Township, NJ": {"platform": "ecode360", "agenda_platform": "eCode360 document hosting (General Code)",
                             "automated": False,
                             "reason": "Agendas are hosted under ecode360.com/documents/pub/AN2011/Agendas/, and ecode360.com "
                                       "robots.txt disallows /documents for all agents."},
    "Lopatcong Township, NJ": {"agenda_platform": "Vision / Granicus govAccess CMS (showpublisheddocument URLs) behind Akamai"},
    "Mansfield Township (Warren), NJ": {"platform": "generic", "agenda_platform": "Joomla", "automated": True,
                                        "listings": [
                                            _gl("Township Committee", "select_board",
                                                "https://www.mansfieldtownship-nj.gov/index.php/government/agendas-minutes-bill-list",
                                                r"^Agenda\b"),
                                            _gl("Land Use Board", "planning_board",
                                                "https://www.mansfieldtownship-nj.gov/index.php/boards-committees/land-use-board",
                                                r"agenda"),
                                        ]},
    "Neptune Township, NJ": {"platform": "generic", "agenda_platform": "Drupal", "automated": True,
                             "note": "Link text is month and day only ('January 28'); dates come from file names "
                                     "when they include a year. Some agendas are legacy .doc files (not extractable).",
                             "listings": [
                                 _gl("Planning Board", "planning_board", _NEP + "planning-board", r"agenda"),
                                 _gl("Zoning Board of Adjustment", "zoning_board_of_appeals", _NEP + "zoning-board-adjustment", r"agenda"),
                                 _gl("Township Committee", "select_board", _NEP + "township-committee", r"agenda"),
                                 _gl("Environmental and Shade Tree Commission", "conservation_commission",
                                     _NEP + "environmental-and-shade-tree-commission", r"agenda"),
                             ]},
    # ---------------- PA
    "Upper Burrell Township, PA": {"platform": "generic", "agenda_platform": "WordPress", "automated": True,
                                   "listings": [
                                       _gl("Board of Supervisors", "select_board", _UB + "supervisors/", r"agenda"),
                                       _gl("Planning Commission", "planning_board", _UB + "planning-commission/", r"agenda"),
                                       _gl("Zoning Hearing Board", "zoning_board_of_appeals", _UB + "zoning-hearing-board/", r"agenda"),
                                   ]},
    "East Whiteland Township, PA": {"platform": "generic_revize", "agenda_platform": "Revize", "automated": True,
        "note": "Revize: www host 302-redirects documents to cms*.revize.com, whose robots.txt allows only URLs ending in .pdf; Revize links carry a ?t= cache-buster, so the stock generic adapter is refused by robots (verified 2026-10-10 on Vergennes). Crawled with the probe shim generic_revize, which drops ?t=.", 
                                    "listings": [
                                        _gl("Board of Supervisors", "select_board", _EW + "board_of_supervisors.php", r"^Agenda\b"),
                                        _gl("Planning Commission", "planning_board", _EW + "planning_commission.php", r"^Agenda\b"),
                                        _gl("Zoning Hearing Board", "zoning_board_of_appeals", _EW + "zoning_hearing_board.php", r"agenda"),
                                        _gl("Environmental Advisory Council", "conservation_commission",
                                            _EW + "environmental_advisory_council.php", r"agenda"),
                                    ]},
    "East Vincent Township, PA": {"agenda_platform": "unknown (site not fetched)",
                                  "reason": "robots.txt: named search bots get narrow rules, then 'User-agent: * Disallow: /'."},
    "Granville Township (Mifflin), PA": {"platform": "generic", "agenda_platform": "WordPress + FileBird Document Library",
                                         "automated": False,
                                         "reason": "Minutes & Agendas page is an empty shell filled client-side by the "
                                                   "FileBird Document Library block (wp-json/filebird/v1); no links in "
                                                   "static HTML. Data-center ZHB appeal files are in a SharePoint folder."},
    "Watts Township (Perry), PA": {"platform": "generic", "agenda_platform": "WordPress + FileBird Document Library",
                                   "automated": False,
                                   "reason": "Meeting Agendas and Planning Commission Agendas pages are rendered "
                                             "client-side by the FileBird Document Library block; no links in static HTML."},
    "Covington Township (Lackawanna), PA": {"platform": "generic", "agenda_platform": "WordPress (document categories)",
                                            "automated": True,
                                            "listings": [
                                                _gl("Board of Supervisors", "select_board", _COV, r"BOS|Supervisors"),
                                                _gl("Planning Commission", "planning_board", _COV, r"Planning Commission"),
                                            ]},
}


class RevizeQueryStripAdapter(REGISTRY["generic"]):
    """PROBE SHIM, not part of watch351. Revize serves documents from
    cms*.revize.com, whose robots.txt allows only URLs ending in .pdf/.doc
    (`Allow: /*.pdf$` then `Disallow: /`). Revize page links append a
    `?t=<timestamp>` cache-buster, so the stock generic adapter's document
    requests are (correctly) refused by robots. Dropping the cache-buster
    yields the robots-allowed canonical URL."""
    platform = "generic_revize"

    def list_agendas(self, cfg, window):
        docs = super().list_agendas(cfg, window)
        for d in docs:
            d.url = re.sub(r"\?t=\d+$", "", d.url)
        return docs


REGISTRY.setdefault("generic_revize", RevizeQueryStripAdapter)


def apply_curated(fetcher: PoliteFetcher, cfg: dict) -> dict:
    cur = CURATED.get(key(cfg), {})
    drop = cur.get("drop_listings")
    cfg.update({k: v for k, v in cur.items() if k != "drop_listings"})
    if drop:
        cfg["listings"] = [l for l in cfg.get("listings", []) if not re.search(drop, l["board"], re.I)]
        cfg["dropped_listings_pattern"] = drop
    if cfg.get("reason") and "automated" not in cur:
        cfg["automated"] = False
    if cfg.get("platform") == "civicplus":
        cfg.setdefault("agenda_platform", "CivicPlus AgendaCenter")
        if not cfg.get("listings"):
            cfg.update(automated=False, reason=cfg.get("reason") or "CivicPlus site without AgendaCenter listings")
    if cfg.get("platform") == "civicclerk" and cfg.get("tenant"):
        from watch351.adapters.civicclerk import CivicClerkAdapter
        cc = CivicClerkAdapter(fetcher)
        today = date.today()
        try:
            evs = cc.events(cfg, Window(today - timedelta(days=365), today + timedelta(days=90)))
        except (FetchError, RuntimeError) as e:
            cfg.update(automated=False, reason=f"CivicClerk API error: {e}")
            return cfg
        names = sorted({(e.get("categoryName") or e.get("eventName") or "").strip() for e in evs})
        cfg.setdefault("fingerprint", {})["civicclerk_categories"] = names
        cfg["fingerprint"]["stock_classifier_boards"] = sorted({classify_board(n) for n in names if classify_board(n)})
        cfg["fingerprint"]["categories_missed_by_stock_classifier"] = [n for n in names if classify_ext(n) and not classify_board(n)]
        cfg["listings"] = [{"board": n, "board_key": classify_board(n) or classify_ext(n),
                            "url": f"https://{cfg['tenant']}.portal.civicclerk.com",
                            "classified_by": "stock" if classify_board(n) else "extended"}
                           for n in names if classify_board(n) or classify_ext(n)]
        cfg["automated"] = bool(cfg["listings"])
        cfg.pop("reason", None)
    if not cfg.get("agenda_platform"):
        fp = cfg.get("fingerprint", {})
        if fp.get("block_markers"):
            cfg["agenda_platform"] = "unknown (blocked)"
    return cfg


def cmd_fingerprint(args, fetcher: PoliteFetcher) -> None:
    sample = load(SAMPLE, {"towns": []})["towns"]
    conf = load(CONFIG, {"towns": []})
    by_key = {key(t): t for t in conf["towns"]}
    todo = select(sample, args.towns)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        out = list(pool.map(lambda s: fingerprint_town(fetcher, s, {}), todo))
    out = [apply_curated(fetcher, c) for c in out]
    for c in out:
        by_key[key(c)] = c
    order = [key(s) for s in sample]
    conf["towns"] = [by_key[k] for k in order if k in by_key]
    conf["generated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save(CONFIG, conf)
    for c in out:
        fp = c.get("fingerprint", {})
        print(f"{key(c):<28} {str(fp.get('status')):<4} {','.join(fp.get('platform_markers', []))[:60]:<60} "
              f"blk={fp.get('block_markers')} vend={fp.get('vendor_hosts_linked')} "
              f"cp_stock={fp.get('stock_classifier_boards')} cp_ext={fp.get('extended_classifier_boards')} "
              f"{'' if c.get('automated') else 'NOT: ' + str(c.get('reason'))}")


# ------------------------------------------------------------------ crawl
_POSTED = re.compile(r"Posted\s+([A-Za-z]{3,9}\.?\s+\d{1,2},\s+\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)", re.I)
_AMENDED = re.compile(r"Amended\s+([A-Za-z]{3,9}\.?\s+\d{1,2},\s+\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)", re.I)


def civicplus_posted_times(fetcher: PoliteFetcher, cfg: dict, window: Window) -> dict[str, dict]:
    """Re-read the AgendaCenter search page (served from the 6 h listing
    cache the adapter just filled) and map agenda href -> posted/amended time."""
    cp = CivicPlusAdapter(fetcher)
    website = cfg["website"].rstrip("/")
    cids = [l["category_id"] for l in cfg.get("listings", [])]
    resp = cp.get_listing(f"{website}/AgendaCenter/Search/", params={
        "term": "", "CIDs": ",".join(cids) + ",",
        "startDate": window.start.strftime("%m/%d/%Y"), "endDate": window.end.strftime("%m/%d/%Y"),
        "dateRange": "", "dateSelector": ""})
    out = {}
    for row in cp.soup(resp).select("tr.catAgendaRow"):
        link = row.select_one("a[href*='ViewFile/Agenda']")
        h3 = row.find("h3")
        if not link or not h3:
            continue
        txt = " ".join(h3.get_text(" ", strip=True).split())
        rec = {}
        for label, rx in (("posted", _POSTED), ("amended", _AMENDED)):
            m = rx.search(txt)
            if m:
                try:
                    rec[label] = datetime.strptime(f"{m.group(1).replace('.', '')} {m.group(2)}",
                                                   "%b %d, %Y %I:%M %p").isoformat()
                except ValueError:
                    try:
                        rec[label] = datetime.strptime(f"{m.group(1).replace('.', '')} {m.group(2)}",
                                                       "%B %d, %Y %I:%M %p").isoformat()
                    except ValueError:
                        pass
        out[cp.abs_url(website + "/", link["href"].split("?")[0])] = rec
    return out


def pdf_dates(fetcher: PoliteFetcher, url: str) -> dict:
    """CreationDate / ModDate from the cached PDF (a proxy for when the
    agenda was prepared, not when it was posted)."""
    try:
        r = fetcher.get(url)
    except FetchError:
        return {}
    if not r.is_pdf:
        return {}
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(r.body)
        tmp.flush()
        try:
            out = subprocess.run(["pdfinfo", "-isodates", tmp.name], capture_output=True, text=True, timeout=30).stdout
        except (subprocess.SubprocessError, OSError):
            return {}
    rec = {}
    for label, field in (("pdf_created", "CreationDate"), ("pdf_modified", "ModDate")):
        m = re.search(rf"^{field}:\s+(\S+)", out, re.M)
        if m:
            rec[label] = m.group(1)
    return rec


def supplemental_hits(text: str) -> list[dict]:
    t = clean_text(text)
    out = []
    for topic, rx in SUPPLEMENTAL.items():
        seen_until = -1
        n = 0
        for m in rx.finditer(t):
            if m.start() < seen_until:
                continue
            s = max(0, m.start() - 90)
            snip = t[s:s + 240]
            out.append({"topic": topic, "snippet": snip.strip()})
            seen_until = s + 240
            n += 1
            if n >= 3:
                break
    return out


def crawl_one(fetcher: PoliteFetcher, cfg: dict, window: Window) -> dict:
    res = {"town": cfg["town"], "state": cfg["state"], "platform": cfg.get("platform"),
           "automated": bool(cfg.get("automated")), "reason": cfg.get("reason"),
           "agendas_listed": 0, "documents_scanned": 0, "documents_without_text_layer": 0,
           "documents_ocr": 0, "errors": [], "docs": [], "hits": [], "supplemental": []}
    if not cfg.get("automated"):
        return res
    adapter = REGISTRY[cfg["platform"]](fetcher)
    try:
        docs = adapter.list_agendas(cfg, window)
    except (FetchError, RuntimeError, ValueError) as e:
        res["errors"].append(f"listing: {e}"[:300])
        return res
    res["agendas_listed"] = len(docs)
    posted = {}
    if cfg["platform"] == "civicplus":
        try:
            posted = civicplus_posted_times(fetcher, cfg, window)
        except (FetchError, RuntimeError) as e:
            res["errors"].append(f"posted-times: {e}"[:200])
    for doc in docs:
        rec = {"board": doc.board, "board_key": doc.board_key,
               "meeting_date": doc.meeting_date.isoformat() if doc.meeting_date else None,
               "title": doc.title, "url": doc.url, "listing_url": doc.listing_url}
        rec.update(posted.get(doc.url, {}))
        try:
            hits, ex = scan_document(fetcher, doc)
        except FetchError as e:
            res["errors"].append(str(e)[:200])
            rec["error"] = str(e)[:200]
            res["docs"].append(rec)
            continue
        if "posted" not in rec and not doc.resolve_pdf:
            rec.update(pdf_dates(fetcher, doc.url))
        rec.update(pages=ex.pages, scanned=ex.scanned, ocr=ex.ocr, hits=len(hits))
        res["docs"].append(rec)
        res["documents_scanned"] += 1
        res["documents_without_text_layer"] += int(ex.scanned)
        res["documents_ocr"] += int(ex.ocr)
        for h in hits:
            h["state"] = cfg["state"]
            h.update({k: rec[k] for k in ("posted", "amended") if k in rec})
        res["hits"].extend(hits)
        for s in supplemental_hits(ex.text):
            res["supplemental"].append({"town": cfg["town"], "state": cfg["state"], "board": doc.board,
                                        "meeting_date": rec["meeting_date"], **s, "source_url": doc.url})
    log.info("%s: %d listed, %d scanned, %d hits", key(cfg), res["agendas_listed"],
             res["documents_scanned"], len(res["hits"]))
    return res


def lead_days(rec: dict) -> float | None:
    if not rec.get("meeting_date"):
        return None
    md = datetime.fromisoformat(rec["meeting_date"])
    for k in ("posted",):
        if rec.get(k):
            return round((md - datetime.fromisoformat(rec[k][:19])).total_seconds() / 86400, 2)
    return None


def cmd_crawl(args, fetcher: PoliteFetcher) -> None:
    conf = load(CONFIG, {"towns": []})
    towns = select(conf["towns"], args.towns)
    today = date.today()
    window = Window(today - timedelta(days=args.days_back), today + timedelta(days=args.days_ahead))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda c: crawl_one(fetcher, c, window), towns))
    hits = _dedupe([h for r in results for h in r["hits"]])
    hits.sort(key=lambda h: (h["state"], h["town"], h["meeting_date"] or "", h["board"]))
    lead = []
    for r in results:
        for d in r["docs"]:
            ld = lead_days(d)
            if ld is not None:
                lead.append({"town": r["town"], "state": r["state"], "board": d["board"],
                             "meeting_date": d["meeting_date"], "posted": d["posted"],
                             "amended": d.get("amended"), "lead_days": ld, "url": d["url"]})
    by_state = defaultdict(lambda: Counter())
    for r in results:
        s = by_state[r["state"]]
        s["towns"] += 1
        s["automated"] += int(r["automated"])
        s["documents_scanned"] += r["documents_scanned"]
        s["documents_without_text_layer"] += r["documents_without_text_layer"]
    for h in hits:
        by_state[h["state"]]["hits"] += 1
    report = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window": {"start": window.start.isoformat(), "end": window.end.isoformat()},
        "towns_attempted": len(results),
        "towns_automated": sum(r["automated"] for r in results),
        "documents_scanned": sum(r["documents_scanned"] for r in results),
        "documents_without_text_layer": sum(r["documents_without_text_layer"] for r in results),
        "documents_ocr": sum(r["documents_ocr"] for r in results),
        "hits_by_topic": dict(Counter(t for h in hits for t in h["topics"]).most_common()),
        "by_state": {k: dict(v) for k, v in sorted(by_state.items())},
        "towns": [{k: v for k, v in r.items() if k not in ("hits", "docs", "supplemental")}
                  | {"hits": sum(1 for h in hits if h["town"] == r["town"] and h["state"] == r["state"]),
                     "errors": r["errors"][:10]} for r in results],
        "hits": hits,
        "posting_lead_times": sorted(lead, key=lambda x: (x["state"], x["town"], x["meeting_date"])),
        "supplemental_not_in_matcher": [s for r in results for s in r["supplemental"]],
        "documents": [{"town": r["town"], "state": r["state"], **d} for r in results for d in r["docs"]],
    }
    save(Path(args.out), report)
    print(f"towns {report['towns_attempted']} automated {report['towns_automated']} docs "
          f"{report['documents_scanned']} (no text {report['documents_without_text_layer']}, "
          f"ocr {report['documents_ocr']}) hits {len(hits)} lead-time records {len(lead)}")
    for st, c in report["by_state"].items():
        print(f"  {st}: {dict(c)}")
    for r in report["towns"]:
        print(f"  {r['town']}, {r['state']}: listed {r['agendas_listed']} scanned {r['documents_scanned']} "
              f"hits {r['hits']} err {len(r['errors'])} {r['errors'][:2]}")
    print(f"fetcher: {fetcher.stats}")


def cmd_listings(args, fetcher: PoliteFetcher) -> None:
    """Dry run: list the agenda documents each adapter finds in the window,
    without downloading them (one listing request per board)."""
    conf = load(CONFIG, {"towns": []})
    today = date.today()
    window = Window(today - timedelta(days=args.days_back), today + timedelta(days=args.days_ahead))
    for cfg in select(conf["towns"], args.towns):
        if not cfg.get("automated"):
            print(f"{key(cfg)}: NOT automated ({cfg.get('reason')})")
            continue
        try:
            docs = REGISTRY[cfg["platform"]](fetcher).list_agendas(cfg, window)
        except (FetchError, RuntimeError, ValueError) as e:
            print(f"{key(cfg)}: listing error {e}")
            continue
        print(f"{key(cfg)} [{cfg['platform']}]: {len(docs)} docs")
        for d in docs[: args.limit]:
            print(f"   {d.meeting_date} {d.board[:28]:<28} {d.title[:50]:<50} {d.url[:110]}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["get", "fingerprint", "listings", "crawl"])
    p.add_argument("url", nargs="?")
    p.add_argument("--grep")
    p.add_argument("--limit", type=int, default=60)
    p.add_argument("--text", type=int, default=0, help="get: print N chars of page text")
    p.add_argument("--towns")
    p.add_argument("--days-back", type=int, default=30)
    p.add_argument("--days-ahead", type=int, default=90)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--out", default=str(HITS))
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("northeast_probe").setLevel(logging.INFO)
    fetcher = PoliteFetcher()
    {"get": cmd_get, "fingerprint": cmd_fingerprint, "listings": cmd_listings,
     "crawl": cmd_crawl}[args.command](args, fetcher)
    return 0


if __name__ == "__main__":
    sys.exit(main())
