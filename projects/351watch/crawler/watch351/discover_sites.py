"""Site-level discovery for states outside Massachusetts (first used for the Michigan and
Virginia test, 2026-10): for one municipality, township or county, find a crawlable agenda
listing per tracked board, or the precise reason it cannot be read.

Order of probes (all through PoliteFetcher: robots.txt on every hop, <= 1 req/s/host):

1. the homepage (https first): robots disallow, crawl-delay over the cap, Cloudflare-style
   challenge, WAF 401/403/429, unreachable host -> not automated with that reason;
2. CivicPlus AgendaCenter categories, classified with the state's board aliases;
3. CivicClerk: a tenant linked from the pages read, else probed by name
   (VA counties "<name>cova", towns "<name>va"; MI counties "<name>comi", townships
   "<name>twpmi"/"<name>mi");
4. agenda vendors linked from the site. Closed ones (Granicus ViewPublisher, iQM2, PrimeGov,
   Diligent/iCompass civicweb, BoardDocs, Destiny) are recorded as vendor_blocked with the
   platform name and are never crawled; open ones (Municode Meetings, NovusAgenda,
   AgendaSuite, BoardBook) are read with the general agenda-page reader when it can;
5. the site's own pages: agenda hubs ("Agendas & Minutes", "Meetings") and each tracked
   board's page (and one level of "Agendas" sub-pages), read with
   adapters.agenda_page.AgendaPageAdapter.

Evidence rule: a board is automated only if a listing shows at least one agenda / packet /
notice dated within the last 120 or next 120 days, and the first such document is
fetchable under robots.txt.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .adapters.agenda_page import AgendaPageAdapter
from .adapters.civicplus import CivicPlusAdapter, _slug
from .boards import BOARD_LABELS, classify_board
from .discover_census import CF_MARKERS, civicplus_rows, cms_of
from .fetch import FetchError, PoliteFetcher, Response, RobotsDisallowed
from .models import Window

log = logging.getLogger(__name__)

EVIDENCE_BACK = 120
EVIDENCE_AHEAD = 120
LISTING_AGE = 24 * 3600
MAX_PAGES = 34

VENDOR_RX = [
    ("civicclerk", r"https?://([a-z0-9-]+)\.(?:portal|boardportal|v8)\.civicclerk\.com[^\s\"'<>]*"),
    ("civicclerk_legacy", r"https?://([a-z0-9-]+)\.civicclerk\.com/web/[^\s\"'<>]*"),
    ("granicus", r"https?://[a-z0-9-]+\.granicus\.com/(?:ViewPublisher|AgendaViewer|boards|GeneratedAgendaViewer)[^\s\"'<>]*"),
    ("iqm2", r"https?://[a-z0-9-]+\.iqm2\.com[^\s\"'<>]*"),
    ("primegov", r"https?://[a-z0-9-]+\.primegov\.com[^\s\"'<>]*"),
    ("legistar", r"https?://[a-z0-9-]+\.legistar\.com[^\s\"'<>]*"),
    ("boarddocs", r"https?://(?:go\.|www\.)?boarddocs\.com/[a-z]{2}/[^\s\"'<>]*"),
    ("icompass_civicweb", r"https?://[a-z0-9-]+\.civicweb\.net[^\s\"'<>]*"),
    ("diligent_community", r"https?://[a-z0-9-]+\.(?:community\.diligentoneplatform\.com|diligent\.community)[^\s\"'<>]*"),
    ("destiny", r"https?://public\.destinyhosted\.com[^\s\"'<>]*"),
    ("municode_meetings", r"https?://[a-z0-9-]+\.municodemeetings\.com[^\s\"'<>]*|https?://meetings\.municode\.com/[^\s\"'<>]*"),
    ("novusagenda", r"https?://[a-z0-9-]+\.novusagenda\.com[^\s\"'<>]*"),
    ("agendasuite", r"https?://(?:www\.)?agendasuite\.org/iip/[a-z0-9-]+[^\s\"'<>]*"),
    ("boardbook", r"https?://meetings\.boardbook\.org/[^\s\"'<>]*"),
    ("escribe", r"https?://pub-[a-z0-9-]+\.escribemeetings\.com[^\s\"'<>]*"),
    ("heygov", r"https?://(?:[a-z0-9-]+\.)?heygov\.com/[^\s\"'<>]*meeting[^\s\"'<>]*"),
    ("laserfiche", r"https?://[^\s\"'<>]*/WebLink/[^\s\"'<>]*"),
]
# Platforms whose robots.txt or firewall refuses AgendaAheadBot (coverage_feasibility.md Q3):
# never crawled, recorded as vendor_blocked with the platform name.
CLOSED = {"granicus", "iqm2", "primegov", "boarddocs", "icompass_civicweb", "diligent_community", "destiny"}
OPEN_READABLE = {"municode_meetings", "novusagenda", "agendasuite", "boardbook"}

HUB_TEXT = re.compile(r"\bagendas?\b|\bmeetings?\b|\bminutes\b|public\s+notices?|meeting\s+notices?|"
                      r"boards?\s*(?:&|and)\s*(?:commissions|committees)|^boards$|^government$|"
                      r"^planning|zoning|^documents$|document\s+center|^township\s+board|^board\s+of", re.I)
SUBPAGE_TEXT = re.compile(r"^(?:20\d\d\s+)?(?:meeting\s+)?agendas?\b|agendas?\s*(?:&|and|/|,)\s*(?:minutes|packets)|"
                          r"^meetings?$|^meeting\s+(?:agendas|notices|schedule|information|documents)|"
                          r"agenda\s*(?:&|and)\s*packets?|^documents$|^archives?$|meeting\s+center|"
                          r"^current\s+agendas?|^upcoming\s+meetings|^agendas?,\s*minutes", re.I)
AGENDAISH_PAGE = re.compile(r"agenda|meeting", re.I)
SKIP_LINK = re.compile(r"\.(?:pdf|docx?|xlsx?|jpe?g|png|mp[34])(?:$|\?)|/calendar|/event|mc-events|/events?/|"
                       r"/20\d\d/\d\d/\d\d/|/news|/blog|"
                       r"(?:facebook|twitter|youtube|instagram|x)\.com/|youtu\.be|mailto:|tel:|/login|/search", re.I)

# Board names on shared pages, by state: (include pattern, exclude words). The include pattern
# selects a board's links on a shared page; other boards' strict names (BOARD_NAME) are excluded.
# Exclude words name other bodies only: agenda subjects ("zoning", "planning") never exclude.
BOARD_RX = {
    "MI": {
        "select_board": (r"township\s+board|board\s+of\s+trustees|\btrustees\b|city\s+council|city\s+commission|"
                         r"village\s+council|\bTB\b|\bBOT\b|board\s+of\s+(?:county\s+)?commissioners|"
                         r"\bboard\s+(?:regular\s+|special\s+)?meeting|\bregular\s+board|\bboard\s+agenda|^\s*TB\b",
                         r"library\s+board|parks?\s+(?:and|&)\s+rec|recreation\s+(?:board|commission)|\bDDA\b|"
                         r"downtown\s+development|brownfield|cemetery|board\s+of\s+review|school\s+board|committee"),
        "planning_board": (r"planning\s+commission|planning\s+board|\bPC\b|planning\b",
                           r"planning\s+district|regional|emergency\s+planning|committee"),
        "zoning_board_of_appeals": (r"zoning\s+board\s+of\s+appeals|\bZBA\b|board\s+of\s+(?:zoning\s+)?appeals|"
                                    r"zoning\s+appeals",
                                    r"building|construction|code\s+appeals|board\s+of\s+review"),
    },
    "VA": {
        "select_board": (r"board\s+of\s+supervisors|\bBOS\b|supervisors|town\s+council|city\s+council|"
                         r"council\s+meeting",
                         r"school\s+board|social\s+services|electoral|committee|\bEDA\b|economic\s+development\s+"
                         r"authority|industrial\s+development\s+authority"),
        "planning_board": (r"planning\s+commission|\bPC\b",
                           r"planning\s+district|regional|emergency\s+planning|committee|\bPDC\b"),
        "zoning_board_of_appeals": (r"board\s+of\s+zoning\s+appeals|\bBZA\b|zoning\s+appeals|board\s+of\s+appeals",
                                    r"building|construction|fire|code\s+appeals"),
    },
}
BOARD_NAME = {  # strict names, used to drop another board's links
    "MI": {"select_board": r"township\s+board|board\s+of\s+trustees|city\s+council|city\s+commission|village\s+council|"
                           r"\bTB\b|\bBOT\b|board\s+of\s+(?:county\s+)?commissioners",
           "planning_board": r"planning\s+commission|planning\s+board|\bPC\b",
           "zoning_board_of_appeals": r"zoning\s+board\s+of\s+appeals|\bZBA\b|board\s+of\s+(?:zoning\s+)?appeals|"
                                      r"zoning\s+appeals"},
    "VA": {"select_board": r"board\s+of\s+supervisors|\bBOS\b|town\s+council|city\s+council",
           "planning_board": r"planning\s+commission|\bPC\b",
           "zoning_board_of_appeals": r"board\s+of\s+zoning\s+appeals|\bBZA\b|zoning\s+appeals|board\s+of\s+appeals"},
}
SLUG_HINTS = {
    "select_board": r"township[-_ ]?board|board[-_ ]of[-_ ]trustees|trustees|board[-_ ]of[-_ ]supervisors|supervisors|"
                    r"town[-_ ]council|city[-_ ]council|city[-_ ]commission|village[-_ ]council|/bos\b",
    "planning_board": r"planning[-_ ]?commission|planning[-_ ]?board|/planning/?$|/pc/?$",
    "zoning_board_of_appeals": r"zoning[-_ ]board[-_ ]of[-_ ]appeals|board[-_ ]of[-_ ]zoning[-_ ]appeals|/zba\b|/bza\b|"
                               r"zoning[-_ ]appeals|board[-_ ]of[-_ ]appeals",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_challenge(status: int, text: str) -> bool:
    return status in (403, 429, 503) and any(m in text[:30000] for m in CF_MARKERS)


def site_root(host: str) -> str:
    host = host.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if host.endswith((".mi.us", ".va.us")) and len(parts) >= 3:
        return ".".join(parts[-3:]) if len(parts) == 3 else ".".join(parts[-4:])
    return ".".join(parts[-2:])


@dataclass
class Link:
    url: str
    text: str
    row: str


@dataclass
class Page:
    url: str
    final_url: str
    html: str
    title: str
    h1: str
    links: list


@dataclass
class SiteState:
    row: dict
    state: str
    fetcher: PoliteFetcher
    today: date
    tracked: list
    pages_fetched: int = 0
    pages: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    robots_blocked: list = field(default_factory=list)
    vendors: dict = field(default_factory=dict)
    boards: dict = field(default_factory=dict)      # board_key -> evidence
    stale: dict = field(default_factory=dict)
    listings: list = field(default_factory=list)
    posted_rows: list = field(default_factory=list)  # CivicPlus "Posted" stamps (lead time)
    home_host: str = ""

    @property
    def window(self) -> Window:
        return Window(self.today - timedelta(days=EVIDENCE_BACK), self.today + timedelta(days=EVIDENCE_AHEAD))


def parse_page(resp: Response) -> Page:
    soup = BeautifulSoup(resp.text, "lxml")
    base_tag = soup.find("base", href=True)
    base = urljoin(resp.final_url, base_tag["href"]) if base_tag else resp.final_url
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        url = urljoin(base, href)
        if not url.startswith("http"):
            continue
        text = " ".join(a.get_text(" ", strip=True).split()) or (a.get("title") or a.get("aria-label") or "")
        row = a.find_parent(["li", "tr"])
        links.append(Link(url.split("#")[0], text[:160], " ".join(row.get_text(" ", strip=True).split())[:300]
                          if row is not None else ""))
    title = " ".join((soup.title.get_text(" ", strip=True) if soup.title else "").split())
    h1 = soup.find("h1")
    return Page(resp.url, resp.final_url, resp.text, title[:200],
                " ".join(h1.get_text(" ", strip=True).split())[:200] if h1 else "", links)


def get_page(st: SiteState, url: str, budget: bool = True) -> Page | None:
    url = url.split("#")[0]
    if url in st.pages:
        return st.pages[url]
    if budget and st.pages_fetched >= MAX_PAGES:
        return None
    st.pages_fetched += 1
    try:
        resp = st.fetcher.get(url, max_age=LISTING_AGE)
    except RobotsDisallowed as e:
        st.robots_blocked.append(str(e)[:200])
        st.pages[url] = None
        return None
    except FetchError as e:
        st.notes.append(f"fetch error {url}: {str(e)[:120]}")
        st.pages[url] = None
        return None
    if not resp.ok:
        st.notes.append(("bot challenge on " if is_challenge(resp.status, resp.text) else f"HTTP {resp.status} ") + url)
        st.pages[url] = None
        return None
    if resp.is_pdf or "html" not in (resp.content_type or "html").lower():
        st.pages[url] = None
        return None
    page = parse_page(resp)
    st.pages[url] = page
    return page


def same_site(st: SiteState, url: str) -> bool:
    host = urlsplit(url).netloc.lower()
    root = site_root(st.home_host)
    return site_root(host) == root or host.endswith("." + root)


def note_vendors(st: SiteState, page: Page) -> None:
    for key, rx in VENDOR_RX:
        for m in re.finditer(rx, page.html, re.I):
            url = m.group(0).rstrip(").,;&")
            if key == "laserfiche" and not any(l.url.startswith(url[:50]) and re.search(r"agenda|meeting|minutes", l.text, re.I)
                                               for l in page.links):
                continue
            v = st.vendors.setdefault(key, {"urls": []})
            if url not in v["urls"] and len(v["urls"]) < 4:
                v["urls"].append(url)
            if key.startswith("civicclerk"):
                v["tenant"] = m.group(1).lower()


def _quality(ev: dict) -> int:
    """Agenda platforms and pages with agendas / packets beat pages that only post meeting notices."""
    if ev["source"] in ("civicplus", "civicclerk", "escribe"):
        return 2
    return 2 if set(ev.get("kinds") or []) & {"agenda", "packet"} else 1


def record(st: SiteState, key: str, ev: dict) -> None:
    if ev["n_recent"] == 0:
        if key not in st.boards:
            st.stale.setdefault(key, ev)
        return
    cur = st.boards.get(key)
    if cur is None or (_quality(ev), ev["n_recent"], ev.get("latest") or "") > \
            (_quality(cur), cur["n_recent"], cur.get("latest") or ""):
        st.boards[key] = ev
    st.stale.pop(key, None)


# ------------------------------------------------------------------ CivicPlus
def do_civicplus(st: SiteState, origin: str) -> bool:
    ad = CivicPlusAdapter(st.fetcher)
    st.pages_fetched += 1
    try:
        cats = ad.categories(origin)
    except FetchError as e:
        st.notes.append(f"AgendaCenter: {str(e)[:120]}")
        return False
    if not cats:
        return False
    tracked = [(cid, name, classify_board(name, st.state)) for cid, name in cats]
    tracked = [t for t in tracked if t[2] in st.tracked]
    st.notes.append(f"AgendaCenter: {len(cats)} categories, {len(tracked)} tracked")
    if not tracked:
        return True
    w = st.window
    st.pages_fetched += 1
    try:
        resp = st.fetcher.get(f"{origin}/AgendaCenter/Search/", max_age=LISTING_AGE, params={
            "term": "", "CIDs": ",".join(t[0] for t in tracked) + ",",
            "startDate": (w.start - timedelta(days=245)).strftime("%m/%d/%Y"), "endDate": w.end.strftime("%m/%d/%Y"),
            "dateRange": "", "dateSelector": ""})
    except FetchError as e:
        st.notes.append(f"AgendaCenter search: {str(e)[:120]}")
        return True
    if not resp.ok:
        st.notes.append(f"AgendaCenter search HTTP {resp.status}")
        return True
    rows = civicplus_rows(resp)
    for cid, name, key in tracked:
        rs_all = [r for r in rows if r["category"].lower() == name.lower() and r["meeting_date"]]
        rs = [r for r in rs_all if date.fromisoformat(r["meeting_date"]) in w]
        listing = {"board": name, "board_key": key, "category_id": cid,
                   "url": f"{origin}/AgendaCenter/{_slug(name)}-{cid}"}
        if rs:
            st.listings.append(listing)
        record(st, key, {"board": name, "source": "civicplus", "url": listing["url"], "n_recent": len(rs),
                         "latest": max((r["meeting_date"] for r in rs_all), default=None)})
        for r in rs_all:
            if r.get("posted"):
                st.posted_rows.append(dict(r, board_key=key, platform="civicplus"))
    return True


# ------------------------------------------------------------------ CivicClerk
def civicclerk_events(st: SiteState, tenant: str) -> list[dict] | None:
    api = f"https://{tenant}.api.civicclerk.com/v1/Events"
    events, url = [], api
    params = {"$filter": f"startDateTime ge {st.window.start.isoformat()}T00:00:00Z and "
                         f"startDateTime le {st.window.end.isoformat()}T23:59:59Z",
              "$orderby": "startDateTime desc"}
    for _ in range(25):
        try:
            resp = st.fetcher.get(url, max_age=LISTING_AGE, params=params)
        except FetchError as e:
            st.notes.append(f"CivicClerk {tenant}: {str(e)[:100]}")
            return None if not events else events
        if not resp.ok:
            return None if not events else events
        try:
            data = json.loads(resp.text)
        except ValueError:
            return None
        events.extend(data.get("value", []))
        url, params = data.get("@odata.nextLink"), None
        if not url:
            break
    return events


def do_civicclerk(st: SiteState, tenant: str, found_by: str) -> bool:
    events = civicclerk_events(st, tenant)
    if events is None:
        return False
    if (found_by == "tenant probe" and st.row.get("kind") == "township" and events
            and not any("township" in json.dumps(ev).lower() for ev in events)):
        st.notes.append(f"CivicClerk tenant {tenant} never says 'township': another body's portal, not used")
        return False
    st.vendors.setdefault("civicclerk", {"urls": [f"https://{tenant}.portal.civicclerk.com"]})
    st.vendors["civicclerk"].update(tenant=tenant, found_by=found_by, status="supported")
    per: dict = {}
    for ev in events:
        name = (ev.get("categoryName") or ev.get("eventName") or "").strip()
        key = classify_board(name, st.state)
        if key not in st.tracked:
            continue
        files = [f for f in ev.get("publishedFiles", []) if (f.get("type") or "").lower() in ("agenda", "agenda packet")]
        per.setdefault((name, key), []).append((ev, files))
    found = False
    for (name, key), evs in per.items():
        with_files = [ev for ev, files in evs if files]
        dates = [ev["startDateTime"][:10] for ev in with_files]
        if with_files:
            st.listings.append({"board": name, "board_key": key, "url": f"https://{tenant}.portal.civicclerk.com"})
            found = True
        record(st, key, {"board": name, "source": "civicclerk", "url": f"https://{tenant}.portal.civicclerk.com",
                         "n_recent": len(with_files), "latest": max(dates) if dates else None})
    st.row["tenant"] = tenant
    return found


def civicclerk_guesses(row: dict, state: str) -> list[str]:
    name = re.sub(r"\b(?:charter\s+)?township\b|\bcounty\b|\bcity\s+of\b|\btown\s+of\b|\bcity\b|\btown\b", "",
                  row["town"], flags=re.I)
    n = re.sub(r"[^a-z]", "", name.lower())
    kind = row.get("kind")
    if state == "VA":
        return [f"{n}cova"] if kind == "county" else [f"{n}va", f"townof{n}va"]
    if state == "MI":
        if kind == "county":
            return [f"{n}comi", f"{n}countymi"]
        if kind == "city":
            return [f"{n}mi", f"cityof{n}mi"]
        # not "<name>mi": that is the city's tenant pattern (portlandmi is the City of Portland)
        return [f"{n}twpmi", f"{n}townshipmi", f"{n}chartertwpmi"]
    return []


# ------------------------------------------------------------------ eSCRIBE
def do_escribe(st: SiteState, url: str) -> bool:
    """eSCRIBE published-meetings portal: one listing per tracked meeting type with meetings in the
    window. PDFs (FileStream.ashx) behind a 'Verifying your browser' page are never fetched: the
    listing then reads the portal's own HTML agenda view (format: html)."""
    from .adapters.escribe import EscribeAdapter
    m = re.match(r"https?://pub-[a-z0-9-]+\.escribemeetings\.com", url, re.I)
    if not m:
        return False
    portal = m.group(0) + "/"
    try:
        meetings = EscribeAdapter(st.fetcher).meetings(portal)
    except (FetchError, RuntimeError) as e:
        st.notes.append(f"eSCRIBE {portal}: {str(e)[:100]}")
        return False
    st.pages_fetched += 1
    found = False
    by_type: dict = {}
    for mt in meetings:
        key = classify_board(mt["type"], st.state)
        if key in st.tracked:
            by_type.setdefault((mt["type"], key), []).append(mt)
    for (mtype, key), mts in by_type.items():
        recent = [x for x in mts if x["date"] in st.window]
        listing = {"board": mtype, "board_key": key, "platform": "escribe", "url": portal,
                   "meeting_type": "^" + re.escape(mtype) + "$"}
        pdf = next((x.get("Agenda") for x in recent if x.get("Agenda")), None)
        if pdf:
            try:
                r = st.fetcher.get(pdf)
                if not (r.ok and r.is_pdf):
                    listing["format"] = "html"
            except FetchError:
                listing["format"] = "html"
        elif any(x.get("HTML") for x in recent):
            listing["format"] = "html"
        if recent:
            st.listings.append(listing)
            found = True
        record(st, key, {"board": mtype, "source": "escribe", "url": portal, "n_recent": len(recent),
                         "latest": max(x["date"] for x in mts).isoformat(), "kinds": ["agenda"]})
    return found


# ------------------------------------------------------------------ vendors
def vendor_status(st: SiteState) -> None:
    for key, v in st.vendors.items():
        if v.get("status"):
            continue
        url = v["urls"][0]
        if key == "laserfiche":
            v["status"] = "document_store"
            continue
        try:
            allowed = st.fetcher.allowed(url)
        except Exception:  # noqa: BLE001
            allowed = False
        if not allowed:
            v["status"] = "vendor_blocked"
            v["detail"] = f"robots.txt on {urlsplit(url).netloc} disallows AgendaAheadBot"
            continue
        if key in CLOSED or key in OPEN_READABLE or key in ("escribe", "heygov", "legistar"):
            try:
                r = st.fetcher.get(url, max_age=LISTING_AGE)
            except RobotsDisallowed as e:
                if "crawl-delay" in str(e):
                    v["status"] = "crawl_delay_over_cap"
                    v["detail"] = (f"robots.txt on {urlsplit(url).netloc} asks for a crawl delay above the 20 s listing cap "
                                   f"({str(e).rsplit('crawl-delay', 1)[-1].strip(' )')[:20]})")
                else:
                    v["status"], v["detail"] = "vendor_blocked", f"robots.txt on {urlsplit(url).netloc} disallows AgendaAheadBot"
                continue
            except FetchError as e:
                v["status"], v["detail"] = "unreachable", str(e)[:120]
                continue
            if is_challenge(r.status, r.text):
                v["status"], v["detail"] = "vendor_blocked", f"{urlsplit(url).netloc} serves a bot challenge (HTTP {r.status})"
            elif r.status in (401, 403, 429):
                v["status"], v["detail"] = "vendor_blocked", f"{urlsplit(url).netloc} answers HTTP {r.status} to AgendaAheadBot"
            elif key in CLOSED:
                v["status"], v["detail"] = "vendor_closed", f"{key} pages answer, but the platform is on the closed list"
            else:
                v["status"] = "open"
        else:
            v["status"] = "open"


# ------------------------------------------------------------------ agenda pages
def board_rx(st: SiteState, key: str) -> tuple[str, str]:
    return BOARD_RX.get(st.state, BOARD_RX["MI"])[key]


# Other public bodies whose agendas share pages with the tracked boards.
OTHER_BODIES = (r"electoral\s+board|\bEB\b|school\s+board|social\s+services|economic\s+development|\bEDA\b|\bIDA\b|"
                r"industrial\s+development\s+authority|library\s+board|emergency\s+planning|\bLEPC\b|"
                r"board\s+of\s+equalization|board\s+of\s+review|building\s+code\s+appeals|wetlands\s+board|"
                r"recreation\s+(?:board|commission|advisory)|parks\s+(?:and|&)\s+rec|tourism|airport\s+(?:commission|"
                r"authority)|broadband|\bDDA\b|downtown\s+development|brownfield|cemetery|personnel\s+committee|"
                r"finance\s+committee|audit\s+committee|transportation\s+safety|historic\s+(?:district|commission)|"
                r"youth\s+council|beautification|community\s+policy|\bCPMT\b|\bFAPT\b")


# Under the default governing-body rule, a document naming planning or zoning appeals at all is not the
# governing body's.
DEFAULT_RULE_EXCLUDE = r"\bplanning\b|\bzoning\s+(?:board|appeals)|\bZBA\b|\bBZA\b|\bappeals\b"


def other_boards(st: SiteState, key: str) -> str:
    names = BOARD_NAME.get(st.state, BOARD_NAME["MI"])
    return "|".join([names[k] for k in ALL_BOARDS if k != key] + [OTHER_BODIES])


ALL_BOARDS = ["select_board", "planning_board", "zoning_board_of_appeals"]


def try_listing(st: SiteState, key: str, url: str, label: str, hub: bool, extra: dict | None = None,
                require_agenda: bool = False) -> bool:
    """Read `url` with the agenda-page reader for board `key`; keep it if it shows dated agendas."""
    inc, exc = board_rx(st, key)
    listing = {"board": label[:80], "board_key": key, "url": url, "platform": "agenda_page"}
    if hub:
        listing["board_pattern"] = inc
        listing["board_exclude"] = "|".join(x for x in (exc, other_boards(st, key)) if x)
    else:
        others = other_boards(st, key)
        if others:
            listing["board_exclude"] = others
    listing.update(extra or {})
    st.pages_fetched += 1
    try:
        docs = AgendaPageAdapter(st.fetcher).list_agendas({"town": st.row["town"], "listings": [listing]}, st.window)
    except RobotsDisallowed as e:
        st.robots_blocked.append(str(e)[:200])
        return False
    except (FetchError, RuntimeError) as e:
        st.notes.append(f"agenda page {url}: {str(e)[:100]}")
        return False
    if not docs:
        return False
    # the first document must be fetchable under robots.txt (Revize, Google Drive, eCode360...)
    blocked = None
    for d in docs[:2]:
        try:
            with st.fetcher.purpose("document"):
                r = st.fetcher.get(d.url)
            if r.ok:
                blocked = None
                break
            blocked = f"HTTP {r.status} {d.url}"
        except RobotsDisallowed as e:
            blocked = (f"documents on {urlsplit(d.url).netloc} need a crawl delay above the 10 s document cap"
                       if "crawl-delay" in str(e) else f"robots.txt disallows documents on {urlsplit(d.url).netloc}")
        except FetchError as e:
            blocked = f"document fetch error: {str(e)[:80]}"
    if blocked:
        st.notes.append(f"DOCS {blocked}")
        return False
    if require_agenda and not any(d.extra.get("kind") in ("agenda", "packet") for d in docs):
        return False
    day = lambda d: d.meeting_date.isoformat() if d.meeting_date else f"{d.extra.get('month', '0000-00')}-01"  # noqa: E731
    dates = sorted(day(d) for d in docs)
    kinds = sorted({d.extra.get("kind") for d in docs})
    if "board" not in (extra or {}):
        listing["board"] = BOARD_LABELS[key] if hub or not classify_board(label, st.state) == key else label[:80]
    ev = {"board": listing["board"], "source": "agenda_page", "url": url, "n_recent": len(docs),
          "latest": dates[-1], "kinds": kinds, "examples": [{"date": day(d), "url": d.url,
                                                             "title": d.title[:80]} for d in docs[:3]]}
    before = st.boards.get(key)
    record(st, key, ev)
    if st.boards.get(key) is ev:
        if before is not None:
            st.listings = [l for l in st.listings if not (l["board_key"] == key and l.get("url") == before.get("url"))]
        st.listings.append(listing)
    return True


def hub_links(st: SiteState, page: Page) -> list[Link]:
    out = []
    for l in page.links:
        if not same_site(st, l.url) or len(l.text) > 50 or SKIP_LINK.search(l.url):
            continue
        if re.search(r"AgendaCenter", l.url) and any(b["source"] == "civicplus" for b in st.boards.values()):
            continue
        if HUB_TEXT.search(l.text):
            out.append(l)

    def score(l: Link):
        t = l.text.lower()
        return (-6 * ("agenda" in t) - 2 * ("minutes" in t) - 2 * ("meeting" in t) - 2 * ("board" in t)
                + 3 * ("calendar" in t), len(t))
    out.sort(key=score)
    return list({l.url: l for l in out}.values())[:4]


def board_candidates(st: SiteState, pages: list[Page], key: str) -> list[Link]:
    cands = []
    for p in pages:
        for l in p.links:
            if not same_site(st, l.url) or SKIP_LINK.search(l.url) or len(l.text) > 70:
                continue
            k = classify_board(l.text, st.state)
            slug = re.search(SLUG_HINTS[key], urlsplit(l.url).path, re.I)
            if k == key or (slug and not re.search(r"minutes", l.text, re.I) and
                            (k is None or k == key)):
                cands.append(l)
    cands.sort(key=lambda l: (0 if re.search(r"agenda", l.text + l.url, re.I) else
                              1 if re.search(r"meeting", l.text + l.url, re.I) else 2, len(l.text)))
    return list({l.url: l for l in cands}.values())[:3]


def names_board(st: SiteState, key: str, page: Page) -> bool:
    """The page is this board's own page: its title / h1 names the board, or its URL has the board's slug."""
    inc = re.compile(board_rx(st, key)[0], re.I)
    return bool(inc.search(f"{page.title} {page.h1}") or re.search(SLUG_HINTS[key], urlsplit(page.final_url).path, re.I))


def try_board_page(st: SiteState, key: str, link: Link) -> bool:
    page = get_page(st, link.url)
    if page is None:
        return False
    note_vendors(st, page)
    if re.search(r"/AgendaCenter", page.final_url, re.I):
        return False
    if try_listing(st, key, page.final_url, link.text, hub=not names_board(st, key, page)):
        return True
    # one level down: "Agendas", "Agendas & Minutes", "Meetings" sub-pages of the board page
    here = page.final_url.rstrip("/")
    subs = [l for l in page.links if same_site(st, l.url) and SUBPAGE_TEXT.search(l.text)
            and l.url.rstrip("/") != here and not SKIP_LINK.search(l.url)]
    subs += [l for l in page.links if same_site(st, l.url) and classify_board(l.text, st.state) == key
             and re.search(r"agenda|meeting", l.url + l.text, re.I) and l.url.rstrip("/") != here
             and not SKIP_LINK.search(l.url)]
    for l in list({l.url: l for l in subs}.values())[:3]:
        if st.pages_fetched >= MAX_PAGES:
            break
        sub = get_page(st, l.url)
        if sub is None:
            continue
        note_vendors(st, sub)
        # a site-wide agendas page (it does not name this board) is read in shared-page mode
        if try_listing(st, key, sub.final_url, link.text, hub=not names_board(st, key, sub)):
            return True
    st.stale.setdefault(key, {"board": link.text[:80], "source": "agenda_page", "url": page.final_url,
                              "n_recent": 0, "latest": None, "note": "board page found, no dated agendas in window"})
    return False


# ------------------------------------------------------------------ driver
def _fetch_home(st: SiteState, website: str) -> tuple[Response | None, tuple | None]:
    variants = [re.sub(r"^http://", "https://", website)] + ([website] if website.startswith("http://") else [])
    err = None
    for v in variants:
        try:
            resp = st.fetcher.get(v, max_age=LISTING_AGE)
        except RobotsDisallowed as e:
            parts = urlsplit(v)
            origin = f"{parts.scheme}://{parts.netloc}"
            if "crawl-delay" in str(e):
                err = ("crawl_delay_exceeds_cap", f"robots.txt asks for a Crawl-delay above the 20 s listing cap "
                       f"({str(e)[-30:].strip('() ')}); host skipped")
            elif st.fetcher._robots.get(origin, "missing") is None:
                err = ("unreachable", "robots.txt answered 5xx / timed out (RFC 9309: treat as disallow for "
                       "this run); host skipped")
            else:
                err = ("robots_disallow", f"robots.txt on the site disallows AgendaAheadBot ({str(e)[:90]})")
            continue
        except FetchError as e:
            err = ("unreachable", f"homepage unreachable: {str(e)[:150]}")
            continue
        if resp.ok:
            soup = BeautifulSoup(resp.text[:5000], "lxml")
            refresh = soup.find("meta", attrs={"http-equiv": re.compile("refresh", re.I)})
            m = re.search(r"url\s*=\s*['\"]?([^'\";]+)", refresh.get("content", ""), re.I) if refresh else None
            if m and len(resp.text) < 3000:
                st.notes.append(f"meta refresh -> {m.group(1).strip()}")
                return _fetch_home(st, urljoin(resp.final_url, m.group(1).strip()))
            return resp, None
        if is_challenge(resp.status, resp.text):
            return None, ("bot_challenge", f"Cloudflare-style bot challenge (HTTP {resp.status}) on {resp.final_url}; "
                          "not bypassed")
        if resp.status in (401, 403, 429):
            akamai = re.search(r"edgesuite|AkamaiGHost|Reference\s*#\d", resp.text[:5000], re.I)
            who = "Akamai" if akamai else ("Cloudflare" if re.search(r"cloudflare", resp.text[:8000], re.I) else "the site's firewall")
            err = ("waf_block", f"HTTP {resp.status} from {who} to AgendaAheadBot; not bypassed")
            continue
        err = ("http_error", f"homepage HTTP {resp.status}")
    return None, err


def discover_place(fetcher: PoliteFetcher, row: dict, state: str, tracked: list[str],
                   today: date | None = None) -> dict:
    """Discovery record for one place, in the towns_*.json row shape. Pages are read as
    listing pages (crawl-delay cap 20 s); the probe of a listed document uses the document
    rules (cap 10 s), as the daily run does."""
    with fetcher.purpose("listing"):
        return _discover_place(fetcher, row, state, tracked, today)


def _discover_place(fetcher: PoliteFetcher, row: dict, state: str, tracked: list[str],
                    today: date | None = None) -> dict:
    today = today or date.today()
    st = SiteState(row=dict(row), state=state, fetcher=fetcher, today=today, tracked=tracked)
    rec = st.row

    def finish(status: str, code: str | None, reason: str | None) -> dict:
        rec.update(status=status, reason_code=code, reason=reason, automated=status == "automated")
        rec["listings"] = st.listings if rec["automated"] else []
        rec["boards_tracked"] = tracked
        rec["boards_found"] = sorted(k for k in st.boards if k in tracked)
        rec["boards_missing"] = [k for k in tracked if k not in st.boards]
        rec["board_evidence"] = {k: st.boards[k] for k in sorted(st.boards)}
        rec["board_stale"] = {k: v for k, v in st.stale.items() if k not in st.boards}
        rec["vendors"] = st.vendors
        rec["robots_blocked"] = st.robots_blocked[:5]
        rec["notes"] = st.notes[:14]
        rec["pages_fetched"] = st.pages_fetched
        rec["discovered_at"] = _now()
        rec["_posted_rows"] = st.posted_rows
        return rec

    website = (row.get("website") or "").strip()
    if not website:
        return finish("not_automated", "no_website", row.get("no_website_note") or "no official website found")
    if not website.startswith("http"):
        website = "http://" + website
    resp, err = _fetch_home(st, website.rstrip("/") + "/")
    if resp is None:
        # the place may still be readable through a CivicClerk tenant (its API is a separate host)
        for t in civicclerk_guesses(row, state):
            if do_civicclerk(st, t, "tenant probe"):
                rec["platform"] = "civicclerk"
                st.notes.append(f"homepage: {err[1]}")
                return finish("automated", None, None)
        return finish("not_automated", *err)
    home = parse_page(resp)
    st.pages[home.url] = home
    st.home_host = urlsplit(home.final_url).netloc.lower()
    # an expired or re-registered domain (the MTA directory still lists it): the page never names the place
    short = re.sub(r"\b(?:charter\s+)?township\b|\bcounty\b|\bcity\s+of\b|\btown\s+of\b", "", row["town"],
                   flags=re.I).strip().lower()
    if short and short not in BeautifulSoup(home.html, "lxml").get_text(" ", strip=True).lower() \
            and short.replace(" ", "") not in home.final_url.lower():
        rec["final_url"] = home.final_url
        return finish("not_automated", "website_mismatch",
                      f"the listed website ({home.final_url}) does not name {row['town']}: domain expired or "
                      "re-registered; no current township site found")
    rec["final_url"] = home.final_url
    rec["cms"] = cms_of(home.html)
    note_vendors(st, home)
    parts = urlsplit(home.final_url)
    origin = f"{parts.scheme}://{parts.netloc}"
    platforms = []
    if "civicplus" in rec["cms"] or "/AgendaCenter" in home.html:
        if do_civicplus(st, origin) and any(b["source"] == "civicplus" for b in st.boards.values()):
            platforms.append("civicplus")
    hubs = []
    for l in hub_links(st, home):
        p = get_page(st, l.url)
        if p is not None:
            note_vendors(st, p)
            hubs.append((l, p))
    # board pages (from the homepage and hub pages) first: they give single-board listings
    for key in tracked:
        if key in st.boards:
            continue
        for l in board_candidates(st, [home] + [p for _, p in hubs], key):
            if st.pages_fetched >= MAX_PAGES:
                break
            if try_board_page(st, key, l):
                break
    # board pages often link the vendor portal (CivicClerk "View agendas")
    cc = st.vendors.get("civicclerk") or st.vendors.get("civicclerk_legacy")
    if cc and cc.get("tenant") and any(k not in st.boards or _quality(st.boards[k]) < 2 for k in tracked):
        if do_civicclerk(st, cc["tenant"], "linked from site"):
            platforms.append("civicclerk")
    # all-boards hub pages for boards still missing; the homepage last (small sites link the next
    # meeting's agenda only from an "upcoming meetings" block there)
    hubs = hubs + [(Link(home.final_url, "Home", ""), home)]
    for l, p in hubs:
        for key in tracked:
            if key not in st.boards and st.pages_fetched < MAX_PAGES:
                try_listing(st, key, p.final_url, l.text, hub=True)
    # A town's / township's shared agendas page whose governing-body documents never name the body
    # ("Regular Meeting Agenda"): the governing body is the default owner of documents that name no
    # other board or body. Flagged on the listing (board_default) so it can be audited.
    if "select_board" in tracked and "select_board" not in st.boards and row.get("kind") != "county":
        for l, p in hubs:
            if st.pages_fetched < MAX_PAGES:
                # loose names too: "July 2026 Planning Agenda" belongs to the planning commission
                exclude = "|".join((other_boards(st, "select_board"), DEFAULT_RULE_EXCLUDE))
                if try_listing(st, "select_board", p.final_url, l.text, hub=False,
                               extra={"board": BOARD_LABELS["select_board"], "board_default": True,
                                      "board_exclude": exclude},
                               require_agenda=True):
                    st.notes.append(f"governing body assigned by default on {p.final_url}")
                    break
    if any(k not in st.boards or _quality(st.boards[k]) < 2 for k in tracked) and "civicclerk" not in platforms:
        for t in civicclerk_guesses(row, state):
            if t == (cc or {}).get("tenant"):
                continue
            if do_civicclerk(st, t, "tenant probe"):
                platforms.append("civicclerk")
                break
    # open vendor portals linked from the site: eSCRIBE has its own adapter; try the general reader on others
    vendor_status(st)
    esc = st.vendors.get("escribe")
    if esc and esc.get("status") == "open" and any(k not in st.boards for k in tracked):
        do_escribe(st, esc["urls"][0])
    for key in OPEN_READABLE:
        v = st.vendors.get(key)
        if not v or v.get("status") != "open":
            continue
        for bkey in tracked:
            if bkey not in st.boards:
                try_listing(st, bkey, v["urls"][0], key, hub=True, extra={"vendor": key})
    if any(b["source"] == "agenda_page" for b in st.boards.values()):
        platforms.append("agenda_page")
    if st.boards:
        def plat(l):
            if l.get("platform"):
                return l["platform"]
            if "category_id" in l:
                return "civicplus"
            if "civicclerk.com" in l.get("url", ""):
                return "civicclerk"
            return "agenda_page"
        src = {"civicplus": "civicplus", "civicclerk": "civicclerk", "agenda_page": "agenda_page", "escribe": "escribe"}
        # keep only the listing that backs each board's best evidence
        st.listings = [l for l in st.listings if l["board_key"] in st.boards and
                       plat(l) == src.get(st.boards[l["board_key"]]["source"]) and
                       (plat(l) != "agenda_page" or l["url"] == st.boards[l["board_key"]]["url"])]
        order = ["civicplus", "civicclerk", "escribe", "agenda_page"]
        rec["platforms"] = sorted({plat(l) for l in st.listings}, key=order.index)
        rec["platform"] = rec["platforms"][0]
        return finish("automated", None, None)
    rec["platform"] = None
    # not automated: the most specific reason
    blocked = {k: v for k, v in st.vendors.items() if v.get("status") in ("vendor_blocked", "vendor_closed")}
    if blocked:
        k, v = next(iter(blocked.items()))
        rec["platform"] = k
        return finish("not_automated", "vendor_blocked", f"agendas on {k}: {v.get('detail')}")
    slow = {k: v for k, v in st.vendors.items() if v.get("status") == "crawl_delay_over_cap"}
    if slow:
        k, v = next(iter(slow.items()))
        rec["platform"] = k
        return finish("not_automated", "crawl_delay_exceeds_cap", f"agendas on {k}: {v.get('detail')}")
    if any(n.startswith("bot challenge") for n in st.notes):
        return finish("not_automated", "bot_challenge", next(n for n in st.notes if n.startswith("bot challenge")))
    own = [u for u in st.robots_blocked if same_site(st, u.split(" ")[0])]
    if own:
        return finish("not_automated", "robots_disallow", f"robots.txt disallows agenda pages: {own[0][:140]}")
    docs_blocked = [n for n in st.notes if n.startswith("DOCS ")]
    if docs_blocked:
        return finish("not_automated", "documents_blocked", docs_blocked[0][5:200])
    if st.vendors.get("laserfiche"):
        return finish("not_automated", "document_store",
                      f"agendas kept in a Laserfiche WebLink repository ({st.vendors['laserfiche']['urls'][0][:90]}); "
                      "no listing with dates")
    if st.stale:
        k, v = next(iter(st.stale.items()))
        return finish("not_automated", "no_recent_agendas",
                      f"board pages found (e.g. {v.get('url')}) but no agenda dated within the last {EVIDENCE_BACK} "
                      f"or next {EVIDENCE_AHEAD} days could be read from them")
    if len(BeautifulSoup(home.html, "lxml").get_text(" ", strip=True)) < 300:
        return finish("not_automated", "js_only", "homepage renders client-side (no server HTML to read)")
    return finish("not_automated", "no_agendas_found",
                  "site reachable, but no agenda listing for the tracked boards was found (agendas may be posted "
                  "only on paper, only as minutes, or on pages the heuristics missed)")
