"""Shared helpers for the official notice and docket feeds (Nov 2026, "coverage without letters").

These sources are state bulletins and dockets that already carry the hearings our blocked places hold:

  ny_enb        NYS DEC Environmental Notice Bulletin (weekly notices, filed under the town in the title)
  ny_ores       NYS Office of Renewable Energy Siting permit applications (large solar, wind, storage)
  oh_opsb       Ohio Power Siting Board cases, read from the PUCO Docketing Information System
  md_psc_cpcn   Maryland PSC CPCN cases (solar, storage, transmission) and their public comment hearings

Each feed writes `<source>_items.json` (every matter read, with its topics and relevance), `<source>_hits.json`
(the relevant ones in the shape of data/hits_current.json plus a few extra fields) and `runs/<source>_<date>.json`
under data/test/notices/ (the default). The hits carry:

  source        the feed id (ny_enb, ...), as the other state feeds do
  source_kind   "public_notice" (a notice of a hearing or comment period) or "state_docket" (a case before a
                state body), the label the site will show
  headline      the notice's own first line, verbatim, cut at a word to about 90 characters
  place         where the hearing is, when the notice says
  date_kind     what meeting_date is: hearing, comment_deadline, decision, filed or listed (meeting_date is
                null for listed and for filed items without a date)

Gating. The outputs never go to data/ or data/sources/ (current.other_hits merges data/sources/*_hits.json into
production): `check_out_dir` refuses those directories while GATED is true. ops/daily.sh does not run them.

Every request goes through watch351.fetch.PoliteFetcher (AgendaAheadBot, robots.txt on every hop, at most
one request a second per host, crawl-delay honoured). No logins, no form posts.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from pathlib import Path

from ..keywords import clean_text, topics_in
from .state_feeds import DATA, clean, hit_id, load_json, load_state_towns, now_iso, write_json

ROOT = DATA.parent
DEFAULT_OUT = DATA / "test" / "notices"
GATED = True
BOARD_KEY = "planning_board"
HEADLINE_MAX = 90
SNIPPET_MAX = 240
# Topics the contract lists for gated feeds only (ARCHITECTURE.md): kept here so a quarry or a large
# industrial project is an item with a topic, not a silent drop, until the site has labels for them.
GATED_TOPICS = ("extraction", "large_development")


def check_out_dir(out_dir: Path) -> None:
    """Refuse to write where production reads (data/, data/sources/)."""
    out = Path(out_dir).resolve()
    sources = (DATA / "sources").resolve()
    if GATED and (out == DATA.resolve() or out == sources or sources in out.parents):
        raise SystemExit(f"{out}: the notice feeds are gated. Write to data/test/notices (the default); "
                         f"data/sources/*_hits.json is merged into production.")


# ------------------------------------------------------------------------------------------ dates
_MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
_MON_ABBR = "jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec"
LONG_DATE = re.compile(rf"(?:(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s+)?"
                       rf"((?:{_MONTHS}|{_MON_ABBR})\.?)\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})", re.I)
NUM_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
TIME_RX = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s*m\.?\b", re.I)


def parse_date(s: str | None) -> date | None:
    """The first date in `s`, as written in notices: 'Friday, November 20, 2026', 'Nov. 9, 2026', '11/04/2026'."""
    s = clean(s)
    if not s:
        return None
    m = LONG_DATE.search(s)
    if m:
        mon = m.group(1).rstrip(".").lower()[:3]
        try:
            return date(int(m.group(3)), datetime.strptime(mon, "%b").month, int(m.group(2)))
        except ValueError:
            return None
    m = NUM_DATE.search(s)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            return None
    return None


def parse_dates(s: str) -> list[date]:
    """Every date in `s`, in order."""
    out = []
    for m in LONG_DATE.finditer(s or ""):
        d = parse_date(m.group(0))
        if d:
            out.append(d)
    for m in NUM_DATE.finditer(s or ""):
        d = parse_date(m.group(0))
        if d:
            out.append(d)
    return out


def iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def window_start(days: int, today: date | None = None) -> date:
    return (today or date.today()) - timedelta(days=days)


# ---------------------------------------------------------------------------------------- text
def headline(text: str, limit: int = HEADLINE_MAX) -> str:
    """The notice's own line, verbatim, cut at a word boundary to about `limit` characters."""
    t = clean(text)
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-(")
    return cut + "…"


def snippet_of(*parts: str, limit: int = SNIPPET_MAX) -> str:
    s = clean(" ".join(p for p in parts if p))
    if len(s) > limit:
        s = s[:limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:-") + "…"
    return s


def sentences(text: str, n: int = 2) -> str:
    """The first `n` sentences of a description."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", clean(text))
    return " ".join(parts[:n])


# ---------------------------------------------------------------------------------------- topics
# Words the shared matcher does not carry but a state docket or bulletin needs: wind, transmission and
# substations (clean_energy_siting, as the MI/VA/OH patterns map them), gas plants (clean_energy_siting until
# the site has a topic), mines and quarries (extraction, gated), zoning laws under other names.
_WIND = re.compile(r"\bwind\s+(?:energy|turbines?|farm|power|project|facilit|repower)|\bwind-powered|\bWECS\b", re.I)
_LINE = re.compile(r"\btransmission\s+(?:line|project|facilit)|\bsubstation|\b\d{2,3}\s*kV\b|\bkilovolt", re.I)
_GAS_PLANT = re.compile(r"(?:natural\s+gas|gas[\s-]+fired|combustion\s+turbine|combined[\s-]+cycle)[^.]{0,60}"
                        r"(?:generat|power\s+plant|electric)|electric\s+generat(?:ing|ion)\s+(?:facility|station|plant)|"
                        r"\bpower\s+plant\b|\bpeaker\b|\benergy\s+center\b", re.I)
_STORAGE = re.compile(r"batter(?:y|ies)|\bBESS\b|energy\s+storage", re.I)
_SOLAR = re.compile(r"\bsolar\b|photovoltaic", re.I)
_DATA_CENTER = re.compile(r"data\s+cent(?:er|re)|crypto(?:currency)?\s+min|bitcoin", re.I)
_MINE = re.compile(r"\bmine[sd]?\b|\bmining\b|\bquarr(?:y|ies)\b|gravel\s+(?:pit|mine|extraction)|sand\s+(?:and\s+gravel\s+)?"
                   r"(?:pit|mine)|mined\s+land", re.I)
_TOWER = re.compile(r"telecommunications?\s+(?:tower|facilit)|cell(?:ular)?\s+tower|wireless\s+(?:communications?\s+)?"
                    r"(?:tower|facilit)|\bmonopole\b|communications?\s+tower", re.I)
_ZONING_LAW = re.compile(r"(?:amend|updat|adopt|revis|repeal|rewrit|chang)\w*[^.;]{0,80}\bzoning\s+(?:law|code|ordinance|"
                         r"map|text|regulations?|local\s+law|district|chapter|bylaw)|\bzoning\s+(?:law|code|ordinance|map|text|"
                         r"regulations?)\s+(?:amendment|update|change|revision)|\bzoning\s+(?:law|code|ordinance|map|regulations?)"
                         r"[^.;]{0,40}\b(?:amend|updat|adopt|revis|repeal|rewrit)|\brezon|\bzone\s+change|comprehensive\s+plan"
                         r"[^.;]{0,30}(?:amend|updat|adopt)|planned\s+development\s+district|\bPDD\b|overlay\s+district|"
                         r"(?:amend|updat|chang|revis)\w*[^.;]{0,60}\b(?:dimensional|setback|accessory\s+(?:building|dwelling|"
                         r"structure)|use\s+table|permitted\s+uses|special\s+use|special\s+permit)|"
                         r"\bmoratorium\b[^.;]{0,60}(?:solar|batter|data\s+cent|wind|"
                         r"warehouse|zoning|develop|subdivision)|(?:solar|batter|data\s+cent|wind|warehouse|develop|subdivision)"
                         r"[^.;]{0,60}\bmoratorium\b", re.I)
_LARGE_DEV = re.compile(r"\bwarehouse|distribution\s+(?:center|facility)|logistics|fulfillment|industrial\s+park|"
                        r"manufacturing\s+(?:plant|facility)|\bfactory\b|chip\s+fab|semiconductor", re.I)
# a solar panel on a roof, a backup battery, a cell phone: equipment, not siting
_NOT_SITING = re.compile(r"roof(?:top)?[\s-]+(?:mounted\s+)?solar|solar[\s-]+(?:powered|hot\s+water|thermal\s+panel)|"
                         r"battery[\s-]+(?:backup|powered|recycling|charger)", re.I)


def notice_topics(text: str, state: str | None = None) -> list[str]:
    """Topics of a notice or docket entry: the shared matcher (with the state's patterns where it has them)
    plus the docket words above. Order follows keywords.TOPICS, gated topics last."""
    text = clean_text(text or "")
    found = set(topics_in(text, state if state in ("MI", "OH", "VA", "MD") else None))
    if _SOLAR.search(text) and not _NOT_SITING.search(text):
        found.add("solar")
    if _STORAGE.search(text) and not re.search(r"battery[\s-]+(?:backup|recycl|charger)|electric\s+vehicle", text, re.I):
        found.add("battery_storage")
    if _DATA_CENTER.search(text):
        found.add("data_center")
    if _WIND.search(text) or _LINE.search(text) or _GAS_PLANT.search(text):
        found.add("clean_energy_siting")
    if _TOWER.search(text):
        found.add("wireless_telecom")
    if _ZONING_LAW.search(text):
        found.add("zoning_amendment")
        if re.search(r"\bmoratori", text, re.I):
            found.add("moratorium")
    if _MINE.search(text):
        found.add("extraction")
    if _LARGE_DEV.search(text) and re.search(r"\d{2,3},\d{3}\s*(?:sq|square)|\d{2,4}\s*acres?", text, re.I):
        found.add("large_development")
    order = ["battery_storage", "solar", "moratorium", "clean_energy_siting", "40b_comprehensive_permit",
             "wireless_telecom", "data_center", "zoning_amendment", *GATED_TOPICS]
    return [t for t in order if t in found]


# ---------------------------------------------------------------------------------------- places
def norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", (s or "").lower())


def titlecase_place(s: str) -> str:
    """'ALTONA' -> 'Altona', 'ST. LAWRENCE' -> 'St. Lawrence', keeps 'McDonough'-style names when mixed case."""
    s = clean(s)
    if s.isupper():
        return " ".join(w[:1].upper() + w[1:].lower() if w.lower() not in ("of", "the", "and", "on") else w.lower()
                        for w in s.split())
    return s


class NYPlaces:
    """Resolve a New York municipality name to the site's name for it: the configured row of that kind
    (data/towns_ny.json), else the bare town name, else '<Name> (village)' / '<Name> (city)' (the site's
    convention, attribution.canonical). `known_town` says whether the name is a New York town or city at all
    (data/neighbors.json), so a typo or a hamlet is not filed as a town."""

    def __init__(self, data_dir: Path = DATA):
        from ..attribution import _ny_names
        self.rows = load_state_towns("NY", data_dir)
        self.known: dict[str, str] = {}
        self.row_county: dict[str, str] = {}
        for r in self.rows:
            kind = r.get("kind")
            if kind not in ("town", "village", "city"):
                continue
            short = re.sub(r"\s+\((?:city|village|town|[A-Za-z. ]+ County)\)$", "", r["town"])
            key = norm(short)
            self.known.setdefault(f"{kind}:{key}", r["town"])
            if kind == "town":
                self.known.setdefault(key, r["town"])
            self.row_county[r["town"]] = r.get("county")
        self.names = _ny_names()
        self.boroughs = {"bronx": "Bronx", "brooklyn": "Brooklyn", "queens": "Queens", "manhattan": "Manhattan",
                         "statenisland": "Staten Island", "newyork": "Manhattan"}

    def resolve(self, name: str, kind: str = "town") -> tuple[str | None, bool]:
        """(site name, configured) for a municipality; (None, False) when the name is not a New York place."""
        from ..attribution import canonical
        name = titlecase_place(name).strip(" ,.;")
        if not name:
            return None, False
        key = norm(name)
        if key in self.boroughs:
            return self.boroughs[key], False
        row = self.known.get(f"{kind}:{key}") or (self.known.get(key) if kind == "town" else None)
        if row:
            return row, True
        if kind == "town" and name.lower() not in self.names:
            # not a town we know: perhaps a village or hamlet filed as a town, or a misspelling
            return None, False
        return canonical(name, self.known, kind), False

    def configured(self, site_name: str) -> dict | None:
        for r in self.rows:
            if r["town"] == site_name:
                return r
        return None


def plain(s: str) -> str:
    """Straight quotes for curly ones ("Queen Anne’s" -> "Queen Anne's"), so names compare."""
    return (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


# "Town of Halfmoon", "City of Albany", "Village of Mayville", "Towns of Altona, Clinton, Ellenburg, and Mooers",
# "Towns of LANSING AND GROTON, TOMPKINS COUNTY"
_NAME_WORD = r"(?!Count(?:y|ies)\b)(?!COUNT(?:Y|IES)\b)[A-Z][A-Za-z'.\-]+"
_MUNI = re.compile(r"\b(Towns?|Cit(?:y|ies)|Villages?)\s+of\s+((?:" + _NAME_WORD + r"(?:\s+(?:" + _NAME_WORD + r"|AND|and))*)"
                   r"(?:\s*,\s*(?:(?:and|AND)\s+)?" + _NAME_WORD + r"(?:\s+(?:" + _NAME_WORD + r"|AND|and))*)*)")
_KIND = {"town": "town", "towns": "town", "city": "city", "cities": "city", "village": "village", "villages": "village"}
_KIND_WORDS = {"town", "towns", "city", "cities", "village", "villages", "county", "counties", "the", "and", "new york",
               "state", "hamlet", "hamlets"}


def municipalities(text: str) -> list[tuple[str, str]]:
    """(name, kind) for every 'Town of X' / 'Towns of X, Y and Z' / 'City of X' / 'Village of X' in `text`
    (names may be in capitals). A trailing county ('Mooers, Clinton County') is not a town, and the words
    Town / Village / County themselves are never names ('Village of Bainbridge and Town of Bainbridge')."""
    text = plain(text or "")
    out: list[tuple[str, str]] = []
    for m in _MUNI.finditer(text):
        kind = _KIND[m.group(1).lower()]
        run = m.group(2)
        # what follows the run says whether its last element is a county
        tail = text[m.end():m.end() + 12]
        pieces = [p for p in re.split(r"\s*,\s*|\s+(?:and|AND)\s+", run) if p]
        if re.match(r"\s*Count(?:y|ies)\b", tail, re.I) and len(pieces) > 1:
            pieces = pieces[:-1]
        elif re.match(r"\s*Count(?:y|ies)\b", tail, re.I):
            continue
        for p in pieces:
            words = [w for w in p.split() if w.lower() not in _KIND_WORDS]
            n = titlecase_place(" ".join(words)).strip(" ,.;")
            if n and n.lower() not in _KIND_WORDS and (n, kind) not in out:
                out.append((n, kind))
    return out


# the one or two words before "County": "Madison", "St. Lawrence", "Prince George's", "Anne Arundel", "New York"
_COUNTY = re.compile(r"(?:\b((?:St\.?|Saint|Prince|Queen|Anne|New|Van|Le|La|Du|De|Fond|Lake|Grand|Big|Little|Mount|Mt\.?)"
                     r"\s+[A-Z][A-Za-z'.]+)|\b([A-Z][A-Za-z'.]{2,}))\s+Count(?:y|ies)\b", re.I)
_NOT_COUNTY = {"the", "and", "in", "of", "for", "this", "each", "said", "any", "a", "an", "county", "counties", "ohio", "maryland",
               "york", "state", "new", "all", "both", "several", "various", "other", "other", "neighboring", "adjacent", "two",
               "three", "four", "adjoining", "surrounding", "respective", "same", "that", "which", "within", "located", "its"}


def counties_named(text: str) -> list[str]:
    """Every county named in `text`, in order: 'in Madison County, Ohio' -> ['Madison']; '(Harford, Baltimore, Howard
    counties)' -> ['Harford', 'Baltimore', 'Howard']; 'COEYMANS, ALBANY COUNTY' -> ['Albany']."""
    text = plain(text or "")
    if text.isupper():
        text = titlecase_place(text)
    out: list[str] = []
    for m in _COUNTY.finditer(text):
        name = (m.group(1) or m.group(2)).strip()
        if name.lower() in _NOT_COUNTY or name[0].islower():
            continue
        names = [name]
        if re.search(r"Counties\b", m.group(0), re.I):
            # "Harford, Baltimore, Howard counties": the comma list before the last name
            before = text[max(0, m.start() - 80):m.start()].rstrip()
            lm = re.search(r"((?:[A-Z][A-Za-z'.]+(?:\s+[A-Z][A-Za-z'.]+)?\s*,\s*)+(?:and\s+)?)$", before)
            if lm:
                names = [p.strip() for p in re.split(r"\s*,\s*", lm.group(1).rstrip(", ")) if p.strip() and p.strip().lower() != "and"] + names
                names = [re.sub(r"^and\s+", "", n) for n in names]
        for n in names:
            n = titlecase_place(n) if n.isupper() else n
            if n and n not in out and n.lower() not in _NOT_COUNTY:
                out.append(n)
    return out


def county_named(text: str) -> str | None:
    """The last county named in `text` (see counties_named), or None."""
    found = counties_named(text)
    return found[-1] if found else None


def county_rows(state: str, data_dir: Path = DATA) -> dict[str, dict]:
    """norm(county name) -> the state's county row ('Madison' -> {'town': 'Madison County', ...})."""
    out = {}
    for r in load_state_towns(state, data_dir):
        if r.get("kind") == "county":
            out[norm(re.sub(r"\s+County$", "", r["town"]))] = r
    return out


# ---------------------------------------------------------------------------------------- hits
def make_hit(*, source: str, source_kind: str, state: str, town: str | None, county: str | None, board: str,
             meeting_date: date | None, date_kind: str, topics: list[str], snippet: str, source_url: str,
             listing_url: str, document_title: str, first_seen: str, headline_text: str, place: str | None = None,
             comment_deadline: date | None = None, extra: dict | None = None) -> dict:
    """One hit in the contract's shape (data/hits_current.json) plus the notice fields the site will label."""
    snippet = snippet_of(snippet)
    hit = {
        "id": hit_id(source_url, snippet),
        "state": state,
        "town": town,
        "county": county,
        "board": board,
        "board_key": BOARD_KEY,
        "meeting_date": iso(meeting_date),
        "topics": list(topics),
        "snippet": snippet,
        "source_url": source_url,
        "listing_url": listing_url,
        "document_title": document_title,
        "text_source": "html",
        "first_seen": first_seen,
        "source": source,
        "source_kind": source_kind,
        "headline": headline(headline_text),
        "date_kind": date_kind,
        "place": clean(place) or None,
        "comment_deadline": iso(comment_deadline),
    }
    if extra:
        hit.update(extra)
    return hit


def write_outputs(source: str, out_dir: Path, items: list[dict], hits: list[dict], listing_url: str,
                  report: dict, ledger: dict | None = None) -> None:
    out_dir = Path(out_dir)
    check_out_dir(out_dir)
    generated = now_iso()
    write_json(out_dir / f"{source}_items.json", {"generated": generated, "source": source, "listing_url": listing_url,
                                                  "items": items})
    write_json(out_dir / f"{source}_hits.json", {"generated": generated, "source": source, "hits": hits})
    if ledger is not None:
        write_json(out_dir / f"{source}_ledger.json", ledger)
    write_json(out_dir / "runs" / f"{source}_{report.get('started', generated)[:10]}.json", report)


def network_report(fetcher) -> dict:
    return {"requests": fetcher.stats["network"], "cache_hits": fetcher.stats["cache"], "errors": fetcher.stats["errors"],
            "robots_blocked": fetcher.stats["robots_blocked"]}


def load_ledger(out_dir: Path, source: str) -> dict:
    return load_json(Path(out_dir) / f"{source}_ledger.json", {})
