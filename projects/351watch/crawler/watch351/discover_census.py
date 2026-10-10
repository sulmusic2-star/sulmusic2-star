"""Census-scale discovery: for one municipality, find which agenda platform it
uses and a crawlable agenda listing per tracked board, with evidence (dated
agenda documents actually seen), or the precise reason it cannot be read.

Used by `python3 -m watch351.ma_census discover`. Output records follow the
data/towns.json schema (`town`, `website`, `platform`, `listings`,
`automated`, `reason`) so `crawl.run_crawl` can consume them unchanged, plus
census fields (`status`, `reason_code`, `board_evidence`, `cms`, `vendors`...).

Evidence rule: a board counts as automated only if its listing shows at least
one agenda whose meeting date falls within the last 120 days or the next 120
days (a listing whose newest agenda is older is treated as stale). A town counts
as automated if at least one meeting board (planning, ZBA, conservation, select
board / council) does; Town Meeting warrants alone do not count.
"""

from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .adapters.civicclerk import CivicClerkAdapter
from .adapters.civicplus import CivicPlusAdapter, _slug
from .boards import BOARD_LABELS, classify_board
from .dates import first_date, parse_date
from .fetch import FetchError, PoliteFetcher, Response, RobotsDisallowed
from .models import Window

log = logging.getLogger(__name__)

TRACKED = ["planning_board", "zoning_board_of_appeals", "conservation_commission",
           "select_board", "town_meeting"]
EVIDENCE_BACK = 120     # board is "active" only with an agenda dated in the last 120 days...
DATA_BACK = 365         # ...but platform timestamps are collected for a full year (lead time)
EVIDENCE_AHEAD = 120
LISTING_AGE = 24 * 3600
MAX_PAGES = 28          # network-page budget per town for discovery

CF_MARKERS = ("challenges.cloudflare.com", "Attention Required! | Cloudflare", "cf-chl",
              "Just a moment...", "cf_chl_opt", "/cdn-cgi/challenge-platform")

CMS_SIGS = [
    ("civicplus", r"/AgendaCenter|CivicPlus|civicplus\.com|/Archive\.aspx|/DocumentCenter/|/FormCenter|/CivicAlerts"),
    ("granicus_govaccess", r"vyhlif|govaccess|granicusideas|/egov/"),
    ("virtual_towns", r"vt-s\.net|Virtual Towns|virtualtownsandschools"),
    ("revize", r"revize"),
    ("municode_web", r"municodeweb|mcode-"),
    ("catalis_govoffice", r"govoffice|catalis"),
    ("wordpress", r"wp-content|wp-includes"),
    ("drupal", r"Drupal|/sites/default/files|drupal-settings-json"),
    ("wix", r"wixstatic|wix\.com"),
    ("civiclive", r"civiclive\.com"),
    ("squarespace", r"squarespace"),
    ("joomla", r"Joomla|/media/jui/"),
]

# Third-party agenda/meeting platforms, detected from links/iframes/scripts.
VENDOR_RX = [
    ("civicclerk", r"https?://([a-z0-9-]+)\.portal\.civicclerk\.com[^\s\"'<>]*"),
    ("granicus", r"https?://[a-z0-9-]+\.granicus\.com/(?:ViewPublisher|AgendaViewer|boards)[^\s\"'<>]*"),
    ("iqm2", r"https?://[a-z0-9-]+\.iqm2\.com[^\s\"'<>]*"),
    ("legistar", r"https?://[a-z0-9-]+\.legistar\.com[^\s\"'<>]*"),
    ("boarddocs", r"https?://go\.boarddocs\.com/ma/[^\s\"'<>]*"),
    ("heygov", r"https?://(?:app\.|api\.)?heygov\.com[^\s\"'<>]*"),
    ("municodemeetings", r"https?://[a-z0-9-]+\.municodemeetings\.com[^\s\"'<>]*"),
    ("civicweb", r"https?://[a-z0-9-]+\.civicweb\.net[^\s\"'<>]*"),
    ("novusagenda", r"https?://[a-z0-9-]+\.novusagenda\.com[^\s\"'<>]*"),
    ("primegov", r"https?://[a-z0-9-]+\.primegov\.com[^\s\"'<>]*"),
    ("escribe", r"https?://pub-[a-z0-9-]+\.escribemeetings\.com[^\s\"'<>]*"),
    ("diligent", r"https?://[a-z0-9-]+\.community\.diligentoneplatform\.com[^\s\"'<>]*"),
    ("agendasuite", r"https?://(?:www\.)?agendasuite\.org/iip/[a-z0-9-]+[^\s\"'<>]*"),
    ("meetingportal", r"https?://[a-z0-9-]+\.(?:meetingportal|onbaseonline)\.com[^\s\"'<>]*"),
    ("mytowngovernment", r"https?://(?:www\.)?mytowngovernment\.org/[0-9]{5}[^\s\"'<>]*"),
    ("laserfiche", r"https?://[^\s\"'<>]*/WebLink/[^\s\"'<>]*"),
    ("google_drive", r"https?://(?:drive|docs)\.google\.com/(?:drive/folders|document|file)/[^\s\"'<>]*"),
    ("sharepoint", r"https?://[a-z0-9-]+\.sharepoint\.com/[^\s\"'<>]*"),
    ("dropbox", r"https?://(?:www\.)?dropbox\.com/(?:sh|scl)/[^\s\"'<>]*"),
]
# vendors that are document stores, not meeting platforms: count only when the
# link text says agendas
DOC_STORE_VENDORS = {"laserfiche", "google_drive", "sharepoint", "dropbox"}

AGENDAISH = re.compile(r"agenda|meeting notice|posted meeting|meeting posting|notice of meeting", re.I)
MINUTESISH = re.compile(r"minutes|supporting materials|summary|video|recording", re.I)
DOCLIKE = re.compile(r"\.pdf\b|\.docx?\b|/DocumentCenter/View/|Archive\.aspx\?ADID=|ViewFile/Agenda|"
                     r"/agenda/|/agendas/|/files/|/uploads/|download|/node/\d+", re.I)
HUB_TEXT = re.compile(r"\bagendas?\b|\bmeetings?\b|\bminutes\b|posted meetings|public notices?|meeting notices?|"
                      r"\bcalendar\b", re.I)
BOARDS_HUB_TEXT = re.compile(r"boards?(?:\s*,)?\s*(?:&|and)?\s*(?:committees|commissions)|^boards$|"
                             r"government$|boards & committees|committees", re.I)
SUBPAGE_TEXT = re.compile(r"^(?:20\d\d\s+)?(?:meeting\s+)?agendas?\b|agendas?\s*(?:&|and|/)\s*minutes|^meetings?$|"
                          r"^agenda center|^meeting (?:agendas|notices|schedule)|^(?:posted|public) meetings|"
                          r"^documents$|^archives?$|^agendas?,", re.I)
WARRANT_TEXT = re.compile(r"warrant", re.I)
# link text that is just a meeting date ("October 14, 2026", "10/14/26 Regular Meeting")
DATE_ONLY = re.compile(r"^[\W_]*(?:(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?,?\s*)?"
                       r"(?:[A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}|\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4})"
                       r"[\W_]*(?:(?:agenda|meeting|regular|special|revised|amended|joint|pdf|docx?)[\W_]*)*$", re.I)
TOWN_MEETING_TEXT = re.compile(r"town meeting", re.I)
YEAR_RECENT = re.compile(r"20(?:25|26|27)|\b(?:25|26|27)\b")

# Board regexes for rows on an all-boards page (unanchored).
HUB_BOARD_RX = {
    "planning_board": (r"\bplanning board\b|community development board|\bplanning\s*(?:&|and)\s*zoning (?:board|commission)",
                       r"sub-?committee|committee|regional|working group|joint"),
    "zoning_board_of_appeals": (r"zoning board|board of appeals|\bZBA\b|zoning appeals",
                                r"sub-?committee|committee"),
    "conservation_commission": (r"conservation commission|\bconcom\b|\bconservation\b",
                                r"sub-?committee|committee|district|restriction|trust|agricultural"),
    "select_board": (r"select ?board|board of selectmen|selectmen|select men|(?:city|town) council",
                     r"sub-?committee|committee|joint|council on aging|youth council|cultural council|"
                     r"arts council|school council"),
    "town_meeting": (r"town meeting|warrant", r"advisory|handbook|committee|minutes"),
}
SLUG_HINTS = {
    "planning_board": r"planning[-_ ]?board|/planning/?$|/planning$",
    "zoning_board_of_appeals": r"zoning[-_ ]board|board[-_ ]of[-_ ]appeals|/zba\b|zoning[-_ ]appeals",
    "conservation_commission": r"conservation[-_ ]commission|/conservation/?$|/concom",
    "select_board": r"select[-_ ]?board|board[-_ ]of[-_ ]selectmen|selectmen|city[-_ ]council|town[-_ ]council",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def site_root(host: str) -> str:
    host = host.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if host.endswith(".ma.us") and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


@dataclass
class Link:
    url: str
    text: str
    row: str
    host: str


@dataclass
class Page:
    url: str
    final_url: str
    status: int
    html: str
    title: str
    h1: str
    links: list[Link]
    visible_chars: int


@dataclass
class TownState:
    muni: dict
    fetcher: PoliteFetcher
    today: date
    pages_fetched: int = 0
    notes: list[str] = field(default_factory=list)
    robots_blocked: list[str] = field(default_factory=list)
    vendors: dict = field(default_factory=dict)     # vendor -> {"urls": [...], "status": ...}
    boards: dict = field(default_factory=dict)      # board_key -> evidence dict (best)
    stale: dict = field(default_factory=dict)       # board_key -> evidence with no recent agendas
    listings: list[dict] = field(default_factory=list)
    leadtime_rows: list[dict] = field(default_factory=list)
    pages: dict = field(default_factory=dict)       # url -> Page | None

    @property
    def window(self) -> Window:
        return Window(self.today - timedelta(days=EVIDENCE_BACK), self.today + timedelta(days=EVIDENCE_AHEAD))

    @property
    def data_window(self) -> Window:
        return Window(self.today - timedelta(days=DATA_BACK), self.today + timedelta(days=EVIDENCE_AHEAD))


def _row_text(a) -> str:
    container = a.find_parent(["tr", "li"])
    if container is None:
        best = None
        for parent in a.parents:
            if parent.name in ("body", "html"):
                break
            if len(parent.get_text(" ", strip=True)) > 300:
                break
            if parent.name in ("div", "p", "td", "article", "section", "dd"):
                best = parent
        container = best
    if container is None:
        return ""
    t = " ".join(container.get_text(" ", strip=True).split())
    return t[:400]


def parse_page(resp: Response) -> Page:
    html = resp.text
    soup = BeautifulSoup(html, "lxml")
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
        links.append(Link(url=url, text=text[:200], row=_row_text(a), host=urlsplit(url).netloc.lower()))
    title = " ".join((soup.title.get_text(" ", strip=True) if soup.title else "").split())
    h1 = soup.find("h1")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    visible = len(soup.get_text(" ", strip=True))
    return Page(resp.url, resp.final_url, resp.status, html, title[:200],
                " ".join(h1.get_text(" ", strip=True).split())[:200] if h1 else "", links, visible)


def get_page(st: TownState, url: str, budget: bool = True) -> Page | None:
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
        if is_challenge(resp.status, resp.text):
            st.notes.append(f"bot challenge on {url}")
        else:
            st.notes.append(f"HTTP {resp.status} {url}")
        st.pages[url] = None
        return None
    if resp.is_pdf or "html" not in (resp.content_type or "html").lower():
        st.pages[url] = None
        return None
    page = parse_page(resp)
    st.pages[url] = page
    return page


def is_challenge(status: int, text: str) -> bool:
    return status in (403, 429, 503) and any(m in text[:30000] for m in CF_MARKERS)


def cms_of(html: str) -> list[str]:
    return [name for name, rx in CMS_SIGS if re.search(rx, html, re.I)]


def note_vendors(st: TownState, page: Page) -> None:
    hay = page.html
    for key, rx in VENDOR_RX:
        for m in re.finditer(rx, hay, re.I):
            url = m.group(0).rstrip(").,;")
            if key in DOC_STORE_VENDORS:
                # only if an anchor to it says agenda/meeting
                if not any(l.url.startswith(url[:60]) and re.search(r"agenda|meeting", l.text + " " + l.row, re.I)
                           for l in page.links):
                    continue
            v = st.vendors.setdefault(key, {"urls": []})
            if url not in v["urls"] and len(v["urls"]) < 5:
                v["urls"].append(url)
            if key == "civicclerk":
                v["tenant"] = m.group(1).lower()


def same_site(st: TownState, url: str) -> bool:
    root = site_root(urlsplit(st.muni["website"]).netloc)
    host = urlsplit(url).netloc.lower()
    return site_root(host) == root or host.endswith("." + root)


# --------------------------------------------------------------- evidence
def other_boards_rx(key: str) -> str:
    """Regex for the *other* tracked boards (to drop sidebar links to their agendas)."""
    return "|".join(HUB_BOARD_RX[k][0] for k in TRACKED if k not in (key, "town_meeting"))


def dated_agendas(page: Page, window: Window, page_is_agenda: bool,
                  board_key: str | None = None, exclude_rx: str | None = None) -> list[dict]:
    """Agenda-like links on a page with a meeting date inside `window`.
    `board_key` filters links on an all-boards page to one board; `exclude_rx`
    drops links naming other boards (used on single-board pages)."""
    out = []
    board_rx = None
    if board_key:
        inc, exc = HUB_BOARD_RX[board_key]
        board_rx = (re.compile(inc, re.I), re.compile(exc, re.I))
    ex = re.compile(exclude_rx, re.I) if exclude_rx else None
    seen = set()
    for l in page.links:
        hay = f"{l.text} {l.url}"
        named = AGENDAISH.search(hay)
        agendaish = named or (page_is_agenda and DOCLIKE.search(l.url)
                              and (DATE_ONLY.match(l.text) or re.search(r"meeting|hearing|session", l.text, re.I)))
        if board_key == "town_meeting":
            agendaish = WARRANT_TEXT.search(hay)
        if not agendaish or MINUTESISH.search(l.text):
            continue
        if not named and board_key != "town_meeting" and re.search(r"minutes", f"{l.row} {l.url}", re.I):
            continue
        if board_rx:
            ctx = f"{hay} {l.row}"
            if not board_rx[0].search(ctx) or board_rx[1].search(f"{l.text} {l.row}"):
                continue
        if ex and ex.search(f"{l.text} {l.row}"):
            continue
        when = first_date(l.text, l.url, l.row)
        if when is None and board_key == "town_meeting" and YEAR_RECENT.search(l.text + " " + l.url):
            m = re.search(r"20(2[5-7])", l.text + " " + l.url)
            if m:
                when = date(int("20" + m.group(1)), 6, 30)  # year-only warrant: mid-year placeholder
        if when is None or when not in window or l.url in seen:
            continue
        seen.add(l.url)
        item = {"url": l.url, "text": l.text[:120], "date": when.isoformat()}
        m = REVIZE_TS.search(l.url)
        if m:
            item["uploaded"] = m.group(1)
        out.append(item)
    return out


REVIZE_TS = re.compile(r"[?&]t=(20\d{12})\d*")


def revize_leadtime(st: TownState, page: Page, key: str, board: str, board_key_filter: str | None = None,
                    exclude_rx: str | None = None, page_is_agenda: bool = False) -> None:
    """Revize CMS stamps every document link with its upload time (?t=YYYYMMDDhhmmss).
    Record those as a (proxy) posted time for lead-time analysis."""
    if key == "town_meeting":
        return
    for f in dated_agendas(page, st.data_window, page_is_agenda, board_key_filter, exclude_rx):
        if not f.get("uploaded"):
            continue
        try:
            up = datetime.strptime(f["uploaded"], "%Y%m%d%H%M%S")
        except ValueError:
            continue
        st.leadtime_rows.append({"category": board, "board_key": key, "platform": "revize",
                                 "meeting_date": f["date"], "posted": up.isoformat(),
                                 "posted_kind": "uploaded", "url": f["url"], "title": f["text"]})


def page_is_agenda_page(page: Page) -> bool:
    label = f"{page.title} {page.h1} {page.final_url}"
    return bool(re.search(r"agenda|meeting", label, re.I)) and not re.search(r"minutes$", page.h1, re.I)


def record_board(st: TownState, key: str, ev: dict) -> None:
    """Keep the best evidence per board (most recent agendas)."""
    if ev["n_recent"] == 0:
        if key not in st.boards:
            st.stale.setdefault(key, ev)
        return
    cur = st.boards.get(key)
    if cur is None or (ev["n_recent"], ev.get("latest") or "") > (cur["n_recent"], cur.get("latest") or ""):
        st.boards[key] = ev
    st.stale.pop(key, None)


# --------------------------------------------------------------- CivicPlus
_POSTED_RX = re.compile(r"(Posted|Amended)\s+([A-Z][a-z]{2,9}\.?\s+\d{1,2},\s+\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)")


def civicplus_rows(resp: Response) -> list[dict]:
    soup = BeautifulSoup(resp.text, "lxml")
    rows = []
    for block in soup.select("div.listing"):
        h2 = block.find("h2")
        if not h2:
            continue
        name = " ".join(h2.get_text(" ", strip=True).split())
        for row in block.select("tr.catAgendaRow"):
            link = row.select_one("a[href*='ViewFile/Agenda']")
            if not link:
                continue
            strong = row.find("strong")
            when = first_date(strong.get("aria-label") if strong else None,
                              strong.get_text(" ", strip=True) if strong else None, link["href"])
            h3 = row.find(["h3", "h4"]) or row
            h3t = " ".join(h3.get_text(" ", strip=True).split())
            m = _POSTED_RX.search(h3t)
            posted = None
            if m:
                try:
                    posted = datetime.strptime(f"{m.group(2).replace('.', '')} {m.group(3).replace(' ', '')}",
                                               "%b %d, %Y %I:%M%p")
                except ValueError:
                    try:
                        posted = datetime.strptime(f"{m.group(2).replace('.', '')} {m.group(3).replace(' ', '')}",
                                                   "%B %d, %Y %I:%M%p")
                    except ValueError:
                        posted = None
            rows.append({"category": name, "meeting_date": when.isoformat() if when else None,
                         "posted": posted.isoformat() if posted else None,
                         "posted_kind": m.group(1).lower() if m else None,
                         "url": urljoin(resp.final_url, link["href"].split("?")[0]),
                         "title": link.get_text(" ", strip=True)[:120]})
    return rows


def do_civicplus(st: TownState, website: str) -> bool:
    ad = CivicPlusAdapter(st.fetcher)
    st.pages_fetched += 1
    try:
        cats = ad.categories(website)
    except RobotsDisallowed as e:
        st.robots_blocked.append(str(e)[:200])
        return False
    except FetchError as e:
        st.notes.append(f"AgendaCenter fetch error: {str(e)[:120]}")
        return False
    if not cats:
        return False
    st.notes.append(f"AgendaCenter: {len(cats)} categories")
    tracked = [(cid, name, classify_board(name)) for cid, name in cats]
    tracked = [t for t in tracked if t[2]]
    if not tracked:
        st.notes.append("AgendaCenter has no tracked-board categories")
        return True
    w = st.data_window
    st.pages_fetched += 1
    try:
        resp = st.fetcher.get(f"{website}/AgendaCenter/Search/", max_age=LISTING_AGE, params={
            "term": "", "CIDs": ",".join(t[0] for t in tracked) + ",",
            "startDate": w.start.strftime("%m/%d/%Y"), "endDate": w.end.strftime("%m/%d/%Y"),
            "dateRange": "", "dateSelector": ""})
    except FetchError as e:
        st.notes.append(f"AgendaCenter search error: {str(e)[:120]}")
        return True
    if not resp.ok:
        st.notes.append(f"AgendaCenter search HTTP {resp.status}")
        return True
    rows = civicplus_rows(resp)
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"].lower()].append(r)
    for cid, name, key in tracked:
        rs_all = [r for r in by_cat.get(name.lower(), []) if r["meeting_date"]]
        rs = [r for r in rs_all if date.fromisoformat(r["meeting_date"]) in st.window]
        listing = {"board": name, "board_key": key, "category_id": cid,
                   "url": f"{website}/AgendaCenter/{_slug(name)}-{cid}"}
        ev = {"board": name, "source": "civicplus", "url": listing["url"], "n_recent": len(rs),
              "latest": max((r["meeting_date"] for r in rs_all), default=None),
              "n_past_90": sum(1 for r in rs if 0 <= (st.today - date.fromisoformat(r["meeting_date"])).days <= 90)}
        if rs:
            st.listings.append(listing)
        record_board(st, key, ev)
        for r in rs_all:
            st.leadtime_rows.append(dict(r, board_key=key, platform="civicplus"))
    return True


# --------------------------------------------------------------- CivicClerk
def do_civicclerk(st: TownState, tenant: str) -> None:
    ad = CivicClerkAdapter(st.fetcher)
    cfg = {"tenant": tenant, "town": st.muni["town"]}
    try:
        events = ad.events(cfg, st.data_window)
    except (FetchError, RuntimeError, ValueError) as e:
        st.notes.append(f"CivicClerk API error: {str(e)[:120]}")
        return
    st.pages_fetched += 1
    per = defaultdict(list)
    for ev in events:
        name = (ev.get("categoryName") or ev.get("eventName") or "").strip()
        key = classify_board(name)
        if not key:
            continue
        files = [f for f in ev.get("publishedFiles", []) if (f.get("type") or "").lower() == "agenda"]
        if not files:
            continue
        per[(name, key)].append((ev, files))
    for (name, key), evs_all in per.items():
        evs = [(ev, f) for ev, f in evs_all if date.fromisoformat(ev["startDateTime"][:10]) in st.window]
        dates = [ev["startDateTime"][:10] for ev, _ in evs] or [None]
        if evs:
            st.listings.append({"board": name, "board_key": key, "url": f"https://{tenant}.portal.civicclerk.com"})
        record_board(st, key, {"board": name, "source": "civicclerk", "url": f"https://{tenant}.portal.civicclerk.com",
                               "n_recent": len(evs), "latest": max(d for d in dates) if evs else
                               max(ev["startDateTime"][:10] for ev, _ in evs_all),
                               "n_past_90": sum(1 for d in dates if d and 0 <= (st.today - date.fromisoformat(d)).days <= 90)})
        for ev, files in evs_all:
            pub = min((f.get("publishOn") for f in files if f.get("publishOn")), default=None)
            st.leadtime_rows.append({
                "category": name, "board_key": key, "platform": "civicclerk",
                "meeting_date": ev["startDateTime"][:10],
                "meeting_start": ev["startDateTime"].replace("Z", ""),
                "posted": pub.replace("Z", "")[:19] if pub else None, "posted_kind": "published",
                "url": f"https://{tenant}.portal.civicclerk.com/event/{ev['id']}/files",
                "title": (files[0].get("name") or "")[:120]})


# --------------------------------------------------------------- generic
EVENT_PAGE = re.compile(r"Calendar\.aspx\?EID=|/event/|/events?/\d|/calendar/event|eventid=|/node/\d+/?$", re.I)


def board_candidates(st: TownState, pages: list[Page], key: str) -> list[Link]:
    cands = []
    for p in pages:
        for l in p.links:
            if not same_site(st, l.url) or EVENT_PAGE.search(l.url) or DOCLIKE.search(l.url.split("?")[0][-6:]):
                continue
            if key == "town_meeting":
                ok = TOWN_MEETING_TEXT.search(l.text) and not re.search(r"advisory|committee|handbook", l.text, re.I)
            else:
                ok = classify_board(l.text) == key or (
                    re.search(SLUG_HINTS[key], urlsplit(l.url).path, re.I)
                    and len(l.text) < 60 and not re.search(r"minutes", l.text, re.I))
            if ok:
                cands.append(l)
    # prefer links to the board's agenda page, then shorter text; unique URLs
    cands.sort(key=lambda l: (0 if (AGENDAISH.search(l.text) or re.search(r"agenda", l.url, re.I)) else
                              1 if re.search(r"meeting", l.url, re.I) else 2, len(l.text)))
    out, seen = [], set()
    for l in cands:
        u = l.url.split("#")[0]
        if u not in seen:
            seen.add(u)
            out.append(l)
    return out[:3]


def try_board_page(st: TownState, key: str, url: str, label: str, depth: int = 0) -> bool:
    page = get_page(st, url)
    if page is None:
        return False
    note_vendors(st, page)
    agenda_page = page_is_agenda_page(page) or bool(AGENDAISH.search(label))
    others = None if key == "town_meeting" else other_boards_rx(key)
    found = dated_agendas(page, st.window, agenda_page, "town_meeting" if key == "town_meeting" else None,
                          exclude_rx=others)
    if found:
        dates = [f["date"] for f in found]
        board_name = label if classify_board(label) == key else BOARD_LABELS[key]
        listing = {"board": board_name[:80], "board_key": key, "url": page.final_url,
                   "link_pattern": "warrant" if key == "town_meeting" else "agenda|notice|posting",
                   "context": "block"}
        if agenda_page and key != "town_meeting":
            listing["date_only_docs"] = True
        if others:
            listing["board_exclude"] = others
        if key == "town_meeting":
            listing["accept_undated_if"] = r"warrant.*20(?:26|27)|20(?:26|27).*warrant"
            listing["exclude_pattern"] = r"minutes|results|vote|report|video|recording"
        ev = {"board": listing["board"], "source": "generic", "url": page.final_url, "n_recent": len(found),
              "latest": max(dates), "examples": found[:3],
              "n_past_90": sum(1 for d in dates if 0 <= (st.today - date.fromisoformat(d)).days <= 90)}
        before = st.boards.get(key)
        record_board(st, key, ev)
        if any(f.get("uploaded") for f in found):
            revize_leadtime(st, page, key, listing["board"], "town_meeting" if key == "town_meeting" else None,
                            others, agenda_page)
        if st.boards.get(key) is ev:
            if before is not None:
                st.listings = [l for l in st.listings if not (l["board_key"] == key and l.get("url") == before.get("url"))]
            st.listings.append(listing)
        return True
    # one level down: an "Agendas" / "Agendas & Minutes" sub-page of the board page
    if depth == 0:
        here = page.final_url.split("#")[0].rstrip("/")
        subs = [l for l in page.links if same_site(st, l.url) and SUBPAGE_TEXT.search(l.text)
                and l.url.split("#")[0].rstrip("/") != here and not EVENT_PAGE.search(l.url)
                and not re.search(r"\.(pdf|docx?|xlsx?)$", l.url.split("?")[0], re.I)]
        if key == "town_meeting":
            subs = [l for l in page.links if same_site(st, l.url) and WARRANT_TEXT.search(l.text)
                    and not re.search(r"\.(pdf|docx?)$", l.url.split("?")[0], re.I)] + subs
        # CivicPlus Archive Center modules ("Most Recent Agenda | View All" -> Archive.aspx?AMID=n)
        subs += [l for l in page.links if same_site(st, l.url) and re.search(r"Archive\.aspx\?AMID=\d+$", l.url, re.I)
                 and re.search(r"agenda", f"{l.text} {l.row}", re.I) and not re.search(r"minutes", l.text, re.I)]
        if key != "town_meeting":
            subs += [l for l in page.links if same_site(st, l.url) and classify_board(l.text) == key
                     and re.search(r"agenda|meeting", l.url, re.I) and not EVENT_PAGE.search(l.url)
                     and l.url.split("#")[0].rstrip("/") != here]
        # prefer this year's folder, then the board's own agenda page over a site-wide one
        slug_rx = re.compile(SLUG_HINTS.get(key, r"town[-_ ]?meeting|warrant"), re.I)
        yr = str(st.today.year)
        subs.sort(key=lambda l: (0 if l.text.startswith(yr) else (2 if re.match(r"20\d\d", l.text) else 1),
                                 0 if slug_rx.search(urlsplit(l.url).path.replace("%20", " ")) else 1))
        subs = list({l.url.split("#")[0].rstrip("/"): l for l in subs}.values())
        for l in subs[:3]:
            if try_board_page(st, key, l.url, l.text, depth=1):
                return True
    else:
        return False
    note = "board page found, no dated agenda links in window"
    if JS_LIST.search(page.html):
        note = "board page found; its document list is rendered client-side by JavaScript"
        st.notes.append(f"JS-rendered document list on {page.final_url}")
    elif any(re.search(r"DocumentCenter/Index/\d+", l.url) and re.search(r"agenda", l.text, re.I) for l in page.links):
        note = "agendas kept in a CivicPlus Document Center folder (folder contents load by JavaScript)"
        st.notes.append(f"JS-rendered document list (Document Center folder) linked from {page.final_url}")
    st.stale.setdefault(key, {"board": label[:80], "source": "generic", "url": page.final_url, "n_recent": 0,
                              "latest": None, "note": note})
    return False


JS_LIST = re.compile(r"ContentItemListData|reactPortletLoader|ng-app=|data-reactroot|__NEXT_DATA__", re.I)
NEWS_PAGE = re.compile(r"CivicAlerts\.aspx|/news/|/blog/|/post/|[?&]p=\d+|/\d{4}/\d{2}/\d{2}/", re.I)


def hub_links(st: TownState, page: Page) -> tuple[list[Link], list[Link]]:
    agendas, boards = [], []
    for l in page.links:
        if (not same_site(st, l.url) or len(l.text) > 45 or EVENT_PAGE.search(l.url)
                or NEWS_PAGE.search(l.url) or re.search(r"\.(pdf|docx?)$", l.url.split("?")[0], re.I)):
            continue
        if re.search(r"AgendaCenter", l.url) and st.boards:
            continue
        if HUB_TEXT.search(l.text) and not re.fullmatch(r"\W*(?:meeting\s+)?minutes\W*", l.text, re.I):
            agendas.append(l)
        elif BOARDS_HUB_TEXT.search(l.text):
            boards.append(l)

    def score(l: Link) -> tuple:
        t = l.text.lower()
        s = 0
        if "agenda" in t:
            s -= 6
        if "minutes" in t:
            s -= 2
        if "meeting" in t:
            s -= 2
        if "notice" in t or "posting" in t:
            s -= 1
        if "calendar" in t:
            s += 3
        return (s, len(t))
    agendas.sort(key=score)
    uniq = lambda ls: list({l.url.split("#")[0]: l for l in ls}.values())
    return uniq(agendas)[:3], uniq(boards)[:2]


def hub_agendas(st: TownState, page: Page) -> None:
    """An all-boards agenda page: classify its dated agenda links by board."""
    is_agenda = page_is_agenda_page(page)
    for key in TRACKED:
        if key in st.boards:
            continue
        found = dated_agendas(page, st.window, is_agenda, key)
        if not found:
            continue
        inc, exc = HUB_BOARD_RX[key]
        dates = [f["date"] for f in found]
        listing = {"board": BOARD_LABELS[key], "board_key": key, "url": page.final_url,
                   "link_pattern": "warrant" if key == "town_meeting" else "agenda|notice|posting",
                   "board_pattern": inc, "board_exclude": exc, "context": "block"}
        if is_agenda and key != "town_meeting":
            listing["date_only_docs"] = True
        if key == "town_meeting":
            listing["accept_undated_if"] = r"warrant.*20(?:26|27)|20(?:26|27).*warrant"
            listing["exclude_pattern"] = r"minutes|results|vote|report|video|recording"
        if any(f.get("uploaded") for f in found):
            revize_leadtime(st, page, key, BOARD_LABELS[key], key, None, is_agenda)
        record_board(st, key, {"board": BOARD_LABELS[key], "source": "generic_hub", "url": page.final_url,
                               "n_recent": len(found), "latest": max(dates), "examples": found[:3],
                               "n_past_90": sum(1 for d in dates if 0 <= (st.today - date.fromisoformat(d)).days <= 90)})
        if st.boards.get(key, {}).get("url") == page.final_url:
            st.listings.append(listing)


# --------------------------------------------------------------- vendors
def vendor_status(st: TownState) -> None:
    for key, v in st.vendors.items():
        if key == "civicclerk":
            v["status"] = "supported"
            continue
        url = v["urls"][0]
        try:
            allowed = st.fetcher.allowed(url)
        except Exception:  # noqa: BLE001
            allowed = False
        if allowed and key not in ("heygov", "boarddocs"):
            try:
                r = st.fetcher.get(url, max_age=LISTING_AGE)
                if is_challenge(r.status, r.text):
                    v["status"] = "vendor_challenge"
                    v["detail"] = f"{urlsplit(url).netloc} serves a Cloudflare-style bot challenge (HTTP {r.status}); not bypassed"
                    continue
                if r.status in (401, 403, 429):
                    v["status"] = "vendor_blocked"
                    v["detail"] = (f"{urlsplit(url).netloc} answers HTTP {r.status}"
                                   f"{' Too Many Requests' if r.status == 429 else ''} to automated requests")
                    continue
            except RobotsDisallowed:
                allowed = False
            except FetchError as e:
                v["status"] = "unreachable"
                v["detail"] = str(e)[:120]
                continue
        if key == "heygov":
            api_ok = st.fetcher.allowed("https://api.heygov.com/")
            v["status"] = "robots_disallow" if not api_ok else "js_only"
            v["detail"] = "agenda list is rendered client-side from api.heygov.com, whose robots.txt disallows all bots"
            continue
        if not allowed:
            v["status"] = "robots_disallow"
            v["detail"] = f"robots.txt on {urlsplit(url).netloc} disallows 351WatchBot"
            continue
        if key == "mytowngovernment":
            # the canonical host serves a Cloudflare challenge; some towns link an http://www. variant
            # that answers without one. Using it would sidestep the vendor's bot protection.
            zip_ = re.search(r"/(\d{5})", url)
            canon = f"https://mytowngovernment.org/{zip_.group(1)}" if zip_ else "https://mytowngovernment.org/"
            try:
                r = st.fetcher.get(canon, max_age=LISTING_AGE)
                chal = is_challenge(r.status, r.text)
            except FetchError:
                chal = True
            if chal:
                v["status"] = "vendor_challenge"
                v["detail"] = ("mytowngovernment.org serves a Cloudflare bot challenge (HTTP 403); not bypassed "
                               "(an http://www. alias some towns link answers without it, but using it would "
                               "sidestep the vendor's bot protection)")
                continue
        if key == "boarddocs":
            try:
                r = st.fetcher.get(url, max_age=LISTING_AGE)
                if r.status == 403:
                    v["status"] = "vendor_blocked"
                    v["detail"] = "BoardDocs (CloudFront) answers HTTP 403 'Request blocked' to automated requests"
                    continue
            except FetchError as e:
                v["status"] = "unreachable"
                v["detail"] = str(e)[:120]
                continue
            v["status"] = "js_only"
            v["detail"] = "BoardDocs public pages are built client-side"
            continue
        v["status"] = "no_adapter"
        v["detail"] = f"{key} pages are reachable; no 351 Watch adapter yet"


# --------------------------------------------------------------- driver
def discover_municipality(fetcher: PoliteFetcher, muni: dict, today: date | None = None) -> dict:
    today = today or date.today()
    st = TownState(muni=muni, fetcher=fetcher, today=today)
    rec = {"town": muni["town"], "website": muni.get("website"), "county": muni.get("county"),
           "kind": muni.get("kind"), "pop_2020": muni.get("pop_2020"), "pop_2024_est": muni.get("pop_2024_est"),
           "legislative_body": muni.get("legislative_body")}
    has_tm = bool(re.search(r"town meeting", muni.get("legislative_body") or "", re.I))
    rec["has_town_meeting"] = has_tm
    tracked = TRACKED if has_tm else TRACKED[:4]

    def finish(status: str, reason_code: str | None, reason: str | None) -> dict:
        rec.update(status=status, reason_code=reason_code, reason=reason)
        rec["automated"] = status == "automated"
        rec["platform"] = rec.get("platform")
        rec["listings"] = st.listings if rec["automated"] else []
        if not rec["automated"] and st.listings:
            rec["listings_found_not_crawled"] = st.listings
        rec["boards_found"] = sorted(k for k in st.boards if k in tracked)
        rec["boards_missing"] = [k for k in tracked if k not in st.boards]
        rec["board_evidence"] = {k: st.boards[k] for k in sorted(st.boards)}
        rec["board_stale"] = {k: v for k, v in st.stale.items() if k not in st.boards}
        rec["vendors"] = st.vendors
        rec["robots_blocked"] = st.robots_blocked[:5]
        rec["notes"] = st.notes[:12]
        rec["pages_fetched"] = st.pages_fetched
        rec["discovered_at"] = _now()
        rec["_leadtime_rows"] = st.leadtime_rows
        return rec

    website = muni.get("website")
    if not website:
        return finish("not_automated", "no_website", "no official website found in MMA directory or Wikidata")
    website = website.rstrip("/")
    rec["website"] = website
    st.pages_fetched += 1
    # https first: some hosts (Revize on AWS ELB) answer 403 to plain http but 200 over https
    variants = [re.sub(r"^http://", "https://", website)] + ([website] if website.startswith("http://") else [])
    home_resp, err = None, None
    for v in variants:
        try:
            home_resp = fetcher.get(v + "/", max_age=LISTING_AGE)
        except RobotsDisallowed as e:
            parts_ = urlsplit(v)
            origin_ = f"{parts_.scheme}://{parts_.netloc}"
            if "crawl-delay" in str(e):
                err = ("crawl_delay_exceeds_cap", "robots.txt asks for a Crawl-delay above the crawler's 10 s cap "
                       f"({str(e)[-40:].strip('() ')}); host skipped (a slower production schedule could honor it)")
            elif fetcher._robots.get(origin_, "missing") is None:
                err = ("robots_unavailable", "robots.txt answered 5xx / timed out, which RFC 9309 treats as "
                       "'disallow all' for this run; host skipped")
            else:
                err = ("robots_disallow_site", f"robots.txt on the town site disallows 351WatchBot ({str(e)[:100]})")
            home_resp = None
            continue
        except FetchError as e:
            err = ("unreachable", f"homepage unreachable: {str(e)[:160]}")
            home_resp = None
            continue
        if home_resp.ok:
            website = v
            break
    if home_resp is None:
        return finish("not_automated", *err)
    rec["website"] = website
    if is_challenge(home_resp.status, home_resp.text):
        return finish("not_automated", "bot_challenge",
                      f"bot challenge (HTTP {home_resp.status}, Cloudflare-style) on the homepage; not bypassed")
    if home_resp.status in (401, 403, 429):
        akamai = re.search(r"edgesuite|AkamaiGHost", home_resp.text[:5000], re.I)
        cf = re.search(r"cloudflare", home_resp.text[:8000], re.I)
        who = "Akamai" if akamai else ("Cloudflare" if cf else "the site's firewall")
        return finish("not_automated", "waf_block",
                      f"HTTP {home_resp.status} '{'Access Denied' if akamai else 'Forbidden'}' from {who} on every "
                      f"request (bot/IP filtering); not bypassed")
    if not home_resp.ok:
        return finish("not_automated", "http_error", f"homepage HTTP {home_resp.status}")
    home = parse_page(home_resp)
    st.pages[website + "/"] = home
    rec["final_url"] = home.final_url
    rec["cms"] = cms_of(home.html)
    note_vendors(st, home)
    if home.visible_chars < 300 and re.search(r"<div id=\"(?:root|app)\"", home.html):
        st.notes.append("homepage is a JavaScript app shell")
    # canonical base for CivicPlus probing: the final URL's origin
    parts = urlsplit(home.final_url)
    origin = f"{parts.scheme}://{parts.netloc}"

    platforms = []
    if "civicplus" in rec["cms"] or "/AgendaCenter" in home.html:
        if do_civicplus(st, origin):
            platforms.append("civicplus")
    # hubs: agendas/meetings pages and boards index
    agenda_hubs, board_hubs = hub_links(st, home)
    hub_pages = []
    for l in agenda_hubs[:2] + board_hubs[:1]:
        if "civicplus" in platforms and re.search(r"AgendaCenter", l.url, re.I):
            continue
        if re.search(r"DocumentCenter/Index/\d+", l.url) and re.search(r"agenda", l.text, re.I):
            st.notes.append(f"JS-rendered document list (Document Center folder) linked as '{l.text}' from homepage")
            continue
        p = get_page(st, l.url)
        if p:
            note_vendors(st, p)
            hub_pages.append(p)
    if "civicclerk" in st.vendors and st.vendors["civicclerk"].get("tenant"):
        do_civicclerk(st, st.vendors["civicclerk"]["tenant"])
        if any(b.get("source") == "civicclerk" for b in st.boards.values()):
            platforms.append("civicclerk")
    # all-boards hub pages
    for p in hub_pages:
        hub_agendas(st, p)
    # per-board pages for boards still missing
    for key in tracked:
        if key in st.boards:
            continue
        for l in board_candidates(st, [home] + hub_pages, key):
            if st.pages_fetched >= MAX_PAGES:
                break
            if try_board_page(st, key, l.url, l.text):
                break
    # CivicClerk tenants are not always linked from pages we read; probe "<town>ma"
    if "civicclerk" not in st.vendors and any(k not in st.boards for k in TRACKED[:4]):
        tenant = re.sub(r"[^a-z]", "", muni["town"].lower()) + "ma"
        try:
            r = fetcher.get(f"https://{tenant}.api.civicclerk.com/v1/Events", max_age=7 * 24 * 3600,
                            params={"$top": "1"})
            if r.ok and json.loads(r.text).get("value"):
                st.vendors["civicclerk"] = {"urls": [f"https://{tenant}.portal.civicclerk.com"], "tenant": tenant,
                                            "found_by": "tenant probe"}
                do_civicclerk(st, tenant)
                if any(b.get("source") == "civicclerk" for b in st.boards.values()) and "civicclerk" not in platforms:
                    platforms.append("civicclerk")
        except (FetchError, ValueError):
            pass
    if any(b["source"].startswith("generic") for b in st.boards.values()):
        platforms.append("generic")
    vendor_status(st)
    rec["platforms"] = platforms
    rec["platform"] = platforms[0] if platforms else None

    # a town counts as automated only through a meeting board (planning, ZBA,
    # ConCom, select board/council); warrants alone (1-3 a year) do not count
    tracked_found = [k for k in TRACKED[:4] if k in st.boards]
    rec["warrants_found"] = "town_meeting" in st.boards
    if tracked_found:
        # crawl.py dispatches one adapter per town; keep the listings of the primary platform
        # and record any secondary-platform listings separately.
        primary = rec["platform"]
        src_platform = {"civicplus": "civicplus", "civicclerk": "civicclerk", "generic": "generic",
                        "generic_hub": "generic"}

        def plat(l: dict) -> str:
            if "category_id" in l:
                return "civicplus"
            if "civicclerk.com" in l.get("url", ""):
                return "civicclerk"
            return "generic"

        # keep only listings that back a board's best evidence (no double-crawling a board)
        def backs_best(l: dict) -> bool:
            ev = st.boards.get(l["board_key"])
            if ev is None:
                return False
            if plat(l) != src_platform.get(ev["source"]):
                return False
            return plat(l) != "generic" or l["url"] == ev["url"]
        st.listings = [l for l in st.listings if backs_best(l)]
        platforms = [p_ for p_ in platforms if any(plat(l) == p_ for l in st.listings)]
        rec["platforms"] = platforms
        rec["platform"] = primary = platforms[0]
        if len(platforms) > 1:
            rec["secondary_listings"] = [l for l in st.listings if plat(l) != primary]
            st.listings = [l for l in st.listings if plat(l) == primary]
            rec["boards_by_platform"] = {
                p: sorted(k for k, b in st.boards.items() if src_platform.get(b["source"]) == p) for p in platforms}
        if primary == "civicclerk":
            rec["tenant"] = st.vendors["civicclerk"]["tenant"]
        return finish("automated", None, None)

    # not automated: most specific reason first
    blocked = {k: v for k, v in st.vendors.items()
               if v.get("status") in ("robots_disallow", "vendor_blocked", "vendor_challenge", "js_only")}
    if any("bot challenge" in n for n in st.notes):
        return finish("not_automated", "bot_challenge", "; ".join(n for n in st.notes if "bot challenge" in n)[:240])
    if blocked:
        k, v = next(iter(blocked.items()))
        code = {"robots_disallow": "vendor_robots_disallow", "vendor_blocked": "vendor_blocked",
                "vendor_challenge": "bot_challenge", "js_only": "js_only"}[v["status"]]
        rec["platform"] = k
        return finish("not_automated", code, f"agendas on {k}: {v.get('detail')}")
    unsupported = {k: v for k, v in st.vendors.items() if v.get("status") == "no_adapter"}
    if unsupported:
        k, v = next(iter(unsupported.items()))
        rec["platform"] = k
        return finish("not_automated", "no_adapter", f"agendas appear to be on {k} ({v['urls'][0][:100]}); no adapter yet")
    if st.robots_blocked:
        return finish("not_automated", "robots_disallow_site",
                      f"robots.txt disallows agenda pages on the town site: {st.robots_blocked[0][:140]}")
    if any("JS-rendered" in n for n in st.notes):
        return finish("not_automated", "js_only",
                      "agenda/document lists are rendered client-side by JavaScript (" +
                      next(n for n in st.notes if "JS-rendered" in n)[:160] + ")")
    if st.stale:
        k, v = next(iter(st.stale.items()))
        return finish("not_automated", "agendas_stale_or_undated",
                      f"agenda listing pages found (e.g. {v.get('url')}) but no agenda dated within the last "
                      f"{EVIDENCE_BACK} days or next {EVIDENCE_AHEAD} days could be read from them")
    if home.visible_chars < 300:
        return finish("not_automated", "js_only", "homepage renders client-side (no server HTML to read)")
    return finish("not_automated", "no_agenda_listing_found",
                  "site reachable, but discovery found no agenda listing for the tracked boards "
                  "(agendas may be posted only physically, only as minutes, or on pages the heuristics missed)")
