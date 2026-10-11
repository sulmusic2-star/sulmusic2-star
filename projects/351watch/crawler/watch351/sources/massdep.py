"""MassDEP wetlands filings -> 351 Watch second source.

Wetlands Protection Act filings (Notices of Intent, buffer-zone-only NOIs and ANRADs) name the
applicant behind a project and, in the fee-check note, who paid the state filing fee. For solar,
battery-storage (BESS), substation/transmission and data-center projects the applicant is often a
single-project LLC ("Golden Pond Solar 1, LLC") and the payor is the parent developer
("CK#5707 NEW LEAF ENERGY") or its engineering consultant. That makes this feed a leading
indicator for Conservation Commission hearings and a way to tie anonymous LLCs to developers.

Source: the EEA Data Portal's public Data Lake API, i.e. the same JSON endpoints that the public
search page https://eeaonline.eea.state.ma.us/portal#!/search/wire calls from a browser. No key,
no login, no cookies are needed or sent.

    GET {API}/wire?FromFilingDate=..&ToFilingDate=..&_start=0&_end=200&ColumnName=FilingDate&Direction=asc
        -> {"Items": [{NOIId, NOINum, FilingDate, ApplicantName, Company, OOCDate, TownName,
                       ProjectAddress}], "TotalCount": n}
    GET {API}/wire/{NOIId}
        -> {FilingType, ProjectType, ApplicantInformation, ProjectAddress, NOINum, FilingDate,
            OOCDate, SOCRequest, InlandResourceAreas, CoastalResourceAreas, Comments,
            TechnicalComments}

Politeness: identifies as 351WatchBot, obeys robots.txt on every host and redirect hop, at most one
request per second, backs off on 429/5xx, stops on 403. Raw API JSON is cached under
crawler/.cache/massdep/ (git-ignored) so outputs can be rebuilt offline.

Personal data: filings by private individuals (homeowners) are kept as minimal records but their
names are not stored; applicant/payor become "[individual]". Contact-person names on company
filings are reduced to a salted hash used only to link filings that share a contact.

Usage (from projects/351watch/crawler):
    python3 -m watch351.sources.massdep                     # incremental (cursor in massdep_state.json)
    python3 -m watch351.sources.massdep --since 2025-10-10  # backfill from a date
    python3 -m watch351.sources.massdep --offline           # rebuild outputs from cache, no network

Outputs (data/sources/):
    massdep_filings.jsonl   one minimal record per filing (all filings, energy or not)
    massdep_hits.json       energy / data-center filings in the hits_current.json hit shape
    massdep_entities.json   project LLC / applicant -> payor / parent developer links
    massdep_state.json      cursor, coverage and run statistics
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import logging
import os
import re
import sys
import time
import urllib.robotparser
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit

import requests

log = logging.getLogger("massdep")

# ----------------------------------------------------------------------------- paths / constants
ROOT = Path(__file__).resolve().parents[3]                 # projects/351watch
DATA = ROOT / "data"
OUT = DATA / "sources"
CACHE = ROOT / "crawler" / ".cache" / "massdep"            # raw API JSON (git-ignored)
TOWNS_FILE = DATA / "towns_ma_all.json"
TARGETS_CSV = ROOT.parents[1] / "research_notes" / "Meeting monitor deep dive" / "ma_target_companies.csv"

FILINGS_FILE = OUT / "massdep_filings.jsonl"
HITS_FILE = OUT / "massdep_hits.json"
ENTITIES_FILE = OUT / "massdep_entities.json"
STATE_FILE = OUT / "massdep_state.json"

HOST = "https://eeaonline.eea.state.ma.us"
API = HOST + "/EEA/DataLake/V1.0/DataLakeAPI/"
LIST_URL = API + "wire"
PORTAL = HOST + "/portal"
RECORD_PAGE = PORTAL + "#!/wire/{id}"                      # public detail page for one filing
RESULTS_PAGE = PORTAL + "#!/search/wire/results?{qs}"      # public results page (town + dates)

USER_AGENT = "351WatchBot/0.1 (+contact: hello@351watch.example)"
ROBOTS_AGENT = "351WatchBot"
MIN_INTERVAL = 1.05          # seconds between requests to the host (<= 1 request/second)
PAGE = 200                   # list page size
CHUNK_DAYS = 7               # list queries are split into week-long filing-date windows
LOOKBACK_DAYS = 45           # incremental runs re-list this many days before the cursor
DESCRIPTION_WAIT_DAYS = 30   # re-fetch details (every 2+ days) of recent filings still lacking a description
SOURCE = "massdep_wetlands"
BOARD = "Conservation Commission (wetlands filing)"
BOARD_KEY = "conservation_commission"
CONTACT_SALT = "351watch-massdep-contact-v1"
INDIVIDUAL = "[individual]"


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


# ============================================================================ HTTP (polite client)
class Blocked(Exception):
    """The server refused us (403, robots.txt, or repeated failures): stop the run, keep progress."""


class Client:
    def __init__(self, min_interval: float = MIN_INTERVAL, timeout: tuple[float, float] = (10, 60)):
        self.min_interval = min_interval
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.8",
        })
        self._last: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.stats: Counter = Counter()
        self.consecutive_failures = 0

    def _throttle(self, host: str, interval: float) -> None:
        last = self._last.get(host)
        if last is not None:
            wait = interval - (time.monotonic() - last)
            if wait > 0:
                time.sleep(wait)
        self._last[host] = time.monotonic()

    def _raw_get(self, url: str, **kw) -> requests.Response:
        self._throttle(urlsplit(url).netloc, self._interval(urlsplit(url)))
        self.stats["requests"] += 1
        return self.session.get(url, timeout=self.timeout, allow_redirects=False, **kw)

    def _interval(self, parts) -> float:
        rp = self._robots.get(f"{parts.scheme}://{parts.netloc}")
        delay = rp.crawl_delay(ROBOTS_AGENT) if rp else None
        return max(self.min_interval, float(delay or 0))

    def _robots_for(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin in self._robots:
            return self._robots[origin]
        rp = urllib.robotparser.RobotFileParser()
        target = origin + "/robots.txt"
        result: urllib.robotparser.RobotFileParser | None = rp
        try:
            for _ in range(6):                               # RFC 9309: follow up to 5 redirects
                r = self._raw_get(target)
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
                    target = urljoin(target, r.headers["Location"])
                    if urlsplit(target).netloc != parts.netloc:
                        break
                    continue
                break
            if r.status_code >= 500:
                result = None                                # server error: treat host as off limits
            elif r.status_code >= 400 or "html" in r.headers.get("Content-Type", "").lower():
                rp.parse([])                                 # no robots.txt: everything allowed
            else:
                rp.parse(r.text.splitlines())
        except requests.RequestException as e:
            log.warning("robots.txt for %s unreachable (%s); skipping host", origin, e)
            result = None
        self._robots[origin] = result
        log.info("robots.txt %s -> %s", origin, "unreachable/5xx" if result is None else "parsed")
        if result is not None:
            delay = result.crawl_delay(ROBOTS_AGENT)
            if delay and float(delay) > 10:
                raise Blocked(f"{origin} asks for crawl-delay {delay}s (> 10 s); not crawling")
        return result

    def get_json(self, url: str, params: dict | None = None):
        if params:
            url = url + ("&" if "?" in url else "?") + urlencode(params)
        current = url
        for _hop in range(6):
            rp = self._robots_for(current)
            if rp is None or not rp.can_fetch(ROBOTS_AGENT, current):
                raise Blocked(f"robots.txt disallows {current}")
            r = self._get_with_backoff(current)
            if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
                current = urljoin(current, r.headers["Location"])
                continue
            if r.status_code == 200:
                self.consecutive_failures = 0
                return r.json()
            self.stats[f"http_{r.status_code}"] += 1
            if r.status_code in (401, 403):
                raise Blocked(f"HTTP {r.status_code} for {current}; stopping (no login or bypass attempted)")
            self.consecutive_failures += 1
            if self.consecutive_failures >= 5:
                raise Blocked(f"{self.consecutive_failures} consecutive failures; last HTTP {r.status_code}")
            return None
        raise Blocked(f"too many redirects: {url}")

    def _get_with_backoff(self, url: str) -> requests.Response:
        for attempt in range(3):
            try:
                r = self._raw_get(url)
            except requests.RequestException as e:
                self.stats["network_errors"] += 1
                self.consecutive_failures += 1
                if self.consecutive_failures >= 5:
                    raise Blocked(f"network errors: {e}") from e
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code == 429 or r.status_code >= 500:
                retry_after = r.headers.get("Retry-After", "")
                wait = min(int(retry_after), 300) if retry_after.isdigit() else 30 * (attempt + 1)
                log.warning("HTTP %s on %s; waiting %ss", r.status_code, url, wait)
                self.stats[f"backoff_{r.status_code}"] += 1
                time.sleep(wait)
                continue
            return r
        return r  # last response (still 429/5xx); caller counts it as a failure


# ============================================================================ listing / details
def _iso(d: date) -> str:
    return d.isoformat() + "T00:00:00.000Z"


def _list_window(client: Client, a: date, b: date) -> list[dict]:
    """List rows with FilingDate in [a, b]. The browser sends To = last day + 1 (adjustDates);
    we do the same and also filter client-side, so either server semantics is safe."""
    params = {"FromFilingDate": _iso(a), "ToFilingDate": _iso(b + timedelta(days=1)),
              "_start": 0, "_end": PAGE, "ColumnName": "FilingDate", "Direction": "asc"}
    data = client.get_json(LIST_URL, params)
    if data is None:
        raise Blocked(f"list query failed for {a}..{b}")
    items, total = data.get("Items") or [], int(data.get("TotalCount") or 0)
    if total > len(items):
        if b > a:                                            # split the window instead of paging
            mid = a + timedelta(days=(b - a).days // 2)
            return _list_window(client, a, mid) + _list_window(client, mid + timedelta(days=1), b)
        start = len(items)
        while start < total:                                 # one very busy day: page through it
            params.update({"_start": start, "_end": start + PAGE})
            more = client.get_json(LIST_URL, params) or {}
            batch = more.get("Items") or []
            if not batch:
                break
            items += batch
            start += len(batch)
    return [it for it in items if a.isoformat() <= (it.get("FilingDate") or "")[:10] <= b.isoformat()]


def list_filings(client: Client, start: date, end: date) -> list[dict]:
    rows: dict[str, dict] = {}
    d = start
    while d <= end:
        e = min(d + timedelta(days=CHUNK_DAYS - 1), end)
        for it in _list_window(client, d, e):
            rows[str(it["NOIId"])] = it
        log.info("listed %s..%s: %d filings so far", d, e, len(rows))
        d = e + timedelta(days=1)
    return list(rows.values())


def cache_path(noi_id: str) -> Path:
    return CACHE / "raw" / f"{noi_id}.json"


def read_cache(noi_id: str) -> dict | None:
    p = cache_path(noi_id)
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def write_cache(noi_id: str, row: dict, detail: dict | None) -> None:
    p = cache_path(noi_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps({"noi_id": noi_id, "list": row, "detail": detail,
                               "fetched_at": utcnow().isoformat()}))
    tmp.replace(p)


# ============================================================================ reference data
def load_towns() -> dict[str, dict]:
    """API town name (upper case) -> {"town": proper name, "county": county}."""
    out: dict[str, dict] = {}
    try:
        towns = json.loads(TOWNS_FILE.read_text())["towns"]
    except (OSError, ValueError, KeyError):
        towns = []
    for t in towns:
        out[t["town"].upper()] = {"town": t["town"], "county": t.get("county")}
    if "MANCHESTER-BY-THE-SEA" in out:
        out["MANCHESTER"] = out["MANCHESTER-BY-THE-SEA"]
    return out


# Known companies. pattern = regex on the upper-cased name; kind: developer (solar/storage),
# datacenter, utility, wind, tower, consultant, attorney. "pure": the firm's MA wetlands filings
# are essentially all energy projects, so a name match alone marks the filing energy-related.
KNOWN: list[dict] = [
    # ---- solar / storage developers, IPPs, EPCs (ma_target_companies.csv)
    {"name": "Nexamp", "kind": "developer", "pure": True, "pattern": r"\bNEXAMP\b"},
    {"name": "NextGrid", "kind": "developer", "pure": True, "pattern": r"\bNEXT\s?GRID\b"},
    {"name": "BlueWave", "kind": "developer", "pure": True, "pattern": r"\bBLUE\s?WAVE\b|^BWC\s"},
    {"name": "Kearsarge Energy", "kind": "developer", "pure": True, "pattern": r"\bKEARSARGE\b"},
    {"name": "Syncarpha Capital", "kind": "developer", "pure": True, "pattern": r"\bSYNCARPHA\b"},
    {"name": "ZPT Energy Solutions / Zero-Point Development", "kind": "developer", "pure": True,
     "pattern": r"\bZPT\b|\bZERO[\s-]?POINT\b|^ZPB\b"},
    {"name": "ENGIE North America", "kind": "developer", "pure": False, "pattern": r"\bENGIE\b"},
    {"name": "Ameresco", "kind": "developer", "pure": False, "pattern": r"\bAMERESCO\b"},
    {"name": "New Leaf Energy", "kind": "developer", "pure": True, "pattern": r"\bNEW\s+LEAF\s+ENERGY\b"},
    {"name": "Standard Solar", "kind": "developer", "pure": True, "pattern": r"\bSTANDARD\s+SOLAR\b"},
    {"name": "Lodestar Energy", "kind": "developer", "pure": True, "pattern": r"\bLODESTAR\b"},
    {"name": "SunRaise Investments", "kind": "developer", "pure": True, "pattern": r"\bSUN\s?RAISE\b"},
    {"name": "EDF Renewables / PowerFlex", "kind": "developer", "pure": True,
     "pattern": r"\bEDF\s+RENEWABLE|\bPOWER\s?FLEX\b"},
    {"name": "Madison Energy Investments", "kind": "developer", "pure": True, "pattern": r"\bMADISON\s+ENERGY\b"},
    {"name": "AMP Solar Group", "kind": "developer", "pure": True, "pattern": r"\bAMP\s+SOLAR\b"},
    {"name": "Catalyze", "kind": "developer", "pure": True, "pattern": r"\bCATALYZE\b"},
    {"name": "Con Edison Clean Energy", "kind": "developer", "pure": False,
     "pattern": r"\bCON\s?ED(?:ISON)?\s+(?:CLEAN|SOLUTIONS|DEVELOPMENT)"},
    {"name": "Altus Power", "kind": "developer", "pure": True, "pattern": r"\bALTUS\s+POWER\b"},
    {"name": "Black Swan Dev Corp", "kind": "developer", "pure": False, "pattern": r"\bBLACK\s+SWAN\b"},
    {"name": "Borrego", "kind": "developer", "pure": True, "pattern": r"\bBORREGO\b"},
    {"name": "Grid Builders LLC", "kind": "developer", "pure": True, "pattern": r"\bGRID\s+BUILDERS\b"},
    {"name": "Clearway Energy Group", "kind": "developer", "pure": True, "pattern": r"\bCLEARWAY\b"},
    {"name": "American Renewables Construction", "kind": "developer", "pure": True,
     "pattern": r"\bAMERICAN\s+RENEWABLES\b"},
    {"name": "Parallel Products Solar Energy", "kind": "developer", "pure": False,
     "pattern": r"\bPARALLEL\s+PRODUCTS\b"},
    {"name": "Conti Solar", "kind": "developer", "pure": True, "pattern": r"\bCONTI\s+SOLAR\b"},
    {"name": "Navisun", "kind": "developer", "pure": True, "pattern": r"\bNAVISUN\b"},
    {"name": "CVE North America", "kind": "developer", "pure": True, "pattern": r"^CVE\b|\bCVE\s+(?:NORTH|NA\b|US)"},
    {"name": "ReWild Renewables", "kind": "developer", "pure": True, "pattern": r"\bRE\s?WILD\b"},
    {"name": "Dynamic Energy", "kind": "developer", "pure": True, "pattern": r"\bDYNAMIC\s+ENERGY\b"},
    {"name": "Citizens Enterprises Corporation", "kind": "developer", "pure": False,
     "pattern": r"\bCITIZENS\s+ENTERPRISES\b"},
    {"name": "Renewable Energy Development Partners (REDP)", "kind": "developer", "pure": True,
     "pattern": r"\bRENEWABLE\s+ENERGY\s+DEVELOPMENT\s+PARTNERS\b|\bREDP\b"},
    {"name": "Park Avenue Solar Solutions", "kind": "developer", "pure": True, "pattern": r"\bPARK\s+AVENUE\s+SOLAR\b"},
    {"name": "Greenbacker", "kind": "developer", "pure": True, "pattern": r"\bGREENBACKER\b"},
    {"name": "Solect Energy", "kind": "developer", "pure": True, "pattern": r"\bSOLECT\b"},
    {"name": "Allco Renewable Energy", "kind": "developer", "pure": True, "pattern": r"\bALLCO\b"},
    {"name": "Ecos Energy", "kind": "developer", "pure": True, "pattern": r"\bECOS\s+ENERGY\b"},
    {"name": "BerryHutton", "kind": "developer", "pure": True, "pattern": r"\bBERRY\s?HUTTON\b"},
    {"name": "Signal Energy", "kind": "developer", "pure": True, "pattern": r"\bSIGNAL\s+ENERGY\b"},
    {"name": "Cypress Creek Renewables", "kind": "developer", "pure": True, "pattern": r"\bCYPRESS\s+CREEK\b"},
    {"name": "ForeFront Power", "kind": "developer", "pure": True, "pattern": r"\bFORE\s?FRONT\s+POWER\b"},
    {"name": "Valta Solar", "kind": "developer", "pure": True, "pattern": r"\bVALTA\b"},
    {"name": "Greenskies Clean Energy", "kind": "developer", "pure": True, "pattern": r"\bGREEN\s?SKIES\b"},
    {"name": "Solar Collective", "kind": "developer", "pure": True, "pattern": r"\bSOLAR\s+COLLECTIVE\b"},
    {"name": "Pro-Tech Energy Solutions", "kind": "developer", "pure": True, "pattern": r"\bPRO[\s-]?TECH\s+ENERGY\b"},
    {"name": "SoCore Energy", "kind": "developer", "pure": True, "pattern": r"\bSOCORE\b"},
    {"name": "PureSky Energy", "kind": "developer", "pure": True, "pattern": r"\bPURE\s?SKY\b"},
    {"name": "DSD Renewables", "kind": "developer", "pure": True, "pattern": r"\bDSD\s+RENEWABLES\b"},
    {"name": "All Energy Solar", "kind": "developer", "pure": True, "pattern": r"\bALL\s+ENERGY\s+SOLAR\b"},
    {"name": "NextEra Energy", "kind": "developer", "pure": False, "pattern": r"\bNEXTERA\b"},
    {"name": "AES Clean Energy", "kind": "developer", "pure": False, "pattern": r"^AES\b|\bAES\s+(?:CLEAN|DISTRIBUTED|US)"},
    {"name": "Agilitas Energy", "kind": "developer", "pure": True, "pattern": r"\bAGILITAS\b"},
    {"name": "Stem Inc.", "kind": "developer", "pure": True, "pattern": r"^STEM\s+INC\b"},
    {"name": "Brookfield Renewable", "kind": "developer", "pure": False, "pattern": r"\bBROOKFIELD\s+RENEWABLE"},
    {"name": "SYSO Technologies", "kind": "developer", "pure": True, "pattern": r"\bSYSO\b"},
    {"name": "Enel X", "kind": "developer", "pure": False, "pattern": r"\bENEL\b"},
    {"name": "S&C Electric", "kind": "developer", "pure": False, "pattern": r"\bS\s?&\s?C\s+ELECTRIC\b"},
    {"name": "Hecate Energy", "kind": "developer", "pure": True, "pattern": r"\bHECATE\b"},
    {"name": "Cranberry Point Energy Storage LLC", "kind": "developer", "pure": True, "pattern": r"\bCRANBERRY\s+POINT\s+ENERGY"},
    {"name": "Medway Grid LLC", "kind": "developer", "pure": True, "pattern": r"\bMEDWAY\s+GRID\b"},
    {"name": "Moraga Storage LLC", "kind": "developer", "pure": True, "pattern": r"\bMORAGA\b"},
    {"name": "Hillman Energy Center LLC", "kind": "developer", "pure": True, "pattern": r"\bHILLMAN\s+ENERGY\b"},
    {"name": "Blue Sky Utility", "kind": "developer", "pure": True, "pattern": r"\bBLUE\s+SKY\s+UTILITY\b"},
    {"name": "East Point Energy", "kind": "developer", "pure": True, "pattern": r"\bEAST\s+POINT\s+ENERGY\b"},
    {"name": "SunPower / Sunrun / Tesla (residential installers)", "kind": "residential_installer", "pure": False,
     "pattern": r"\bSUNRUN\b|\bSUNPOWER\b|\bTESLA\b|\bVIVINT\s+SOLAR\b|\bREVOLUSUN\b|\bSUNNOVA\b|\bTRINITY\s+SOLAR\b|"
                r"\bSUNBUG\b|\bFREEDOM\s+FOREVER\b|\bION\s+SOLAR\b|\bPALMETTO\b|\bSOLARCITY\b|\bMOMENTUM\s+SOLAR\b|"
                r"\bPOWERHOME\b|\bBOSTON\s+SOLAR\b|\bSUNPRO\b|\bADT\s+SOLAR\b|\bSUNWORKS\b"},
    # ---- data-center operators / developers
    {"name": "Digital Realty", "kind": "datacenter", "pure": True, "pattern": r"\bDIGITAL\s+REALTY\b"},
    {"name": "Centersquare (incl. Cyxtera)", "kind": "datacenter", "pure": True, "pattern": r"\bCENTERSQUARE\b|\bCYXTERA\b"},
    {"name": "Markley Group", "kind": "datacenter", "pure": True, "pattern": r"\bMARKLEY\b"},
    {"name": "TierPoint", "kind": "datacenter", "pure": True, "pattern": r"\bTIER\s?POINT\b"},
    {"name": "ColoSpace", "kind": "datacenter", "pure": True, "pattern": r"\bCOLO\s?SPACE\b"},
    {"name": "Amazon Web Services", "kind": "datacenter", "pure": False, "pattern": r"\bAMAZON\b|\bAWS\b|\bVADATA\b"},
    {"name": "Equinix", "kind": "datacenter", "pure": True, "pattern": r"\bEQUINIX\b"},
    {"name": "CoreSite", "kind": "datacenter", "pure": True, "pattern": r"\bCORE\s?SITE\b"},
    {"name": "11:11 Systems", "kind": "datacenter", "pure": True, "pattern": r"\b11:11\s+SYSTEMS\b"},
    {"name": "EdgeConneX", "kind": "datacenter", "pure": True, "pattern": r"\bEDGE\s?CONNEX\b"},
    {"name": "Iron Mountain Data Centers", "kind": "datacenter", "pure": False, "pattern": r"\bIRON\s+MOUNTAIN\b"},
    {"name": "Servistar Realty LLC", "kind": "datacenter", "pure": False, "pattern": r"\bSERVISTAR\b"},
    {"name": "Chestnut River Power", "kind": "datacenter", "pure": False, "pattern": r"\bCHESTNUT\s+RIVER\s+POWER\b"},
    {"name": "The Davis Companies", "kind": "datacenter", "pure": False, "pattern": r"\bDAVIS\s+COMPANIES\b"},
    # ---- utilities, transmission, wind, towers
    {"name": "National Grid (New England Power / Mass. Electric)", "kind": "utility", "pure": False,
     "pattern": r"\bNATIONAL\s+GRID\b|\bNEW\s+ENGLAND\s+POWER\b|\bNEP\b|\bMECO\b|\bMASS(?:ACHUSETTS)?\.?\s+ELECTRIC\b|\bNANTUCKET\s+ELECTRIC\b|\bBOSTON\s+GAS\b|\bNGRID\b"},
    {"name": "Eversource (NSTAR Electric)", "kind": "utility", "pure": False,
     "pattern": r"\bEVERSOURCE\b|\bNSTAR\b|\bWESTERN\s+MASS(?:ACHUSETTS)?\.?\s+ELECTRIC\b|\bYANKEE\s+GAS\b"},
    {"name": "Unitil", "kind": "utility", "pure": False, "pattern": r"\bUNITIL\b|\bFITCHBURG\s+GAS\b"},
    {"name": "Municipal light plant", "kind": "utility", "pure": False,
     "pattern": r"\bLIGHT\s+(?:PLANT|DEPARTMENT|DEPT|BOARD)\b|\bMUNICIPAL\s+(?:LIGHT|ELECTRIC)\b|\bMMWEC\b"},
    {"name": "SouthCoast Wind", "kind": "wind", "pure": True, "pattern": r"\bSOUTH\s?COAST\s+WIND\b|\bMAYFLOWER\s+WIND\b"},
    {"name": "Commonwealth Wind LLC (Avangrid)", "kind": "wind", "pure": True, "pattern": r"\bCOMMONWEALTH\s+WIND\b|\bAVANGRID\b|\bVINEYARD\s+(?:WIND|OFFSHORE)\b|\bPARK\s+CITY\s+WIND\b"},
    {"name": "Vertex Towers, LLC", "kind": "tower", "pure": True, "pattern": r"\bVERTEX\s+TOWERS\b"},
    # ---- consultants / law firms that pay filing fees for clients
    {"name": "Beals and Thomas, Inc.", "kind": "consultant", "pure": False, "pattern": r"\bBEALS\s*(?:AND|&)\s*THOMAS\b"},
    {"name": "Farland Corp", "kind": "consultant", "pure": False, "pattern": r"\bFARLAND\b"},
    {"name": "Kimley-Horn", "kind": "consultant", "pure": False, "pattern": r"\bKIMLEY[\s-]?HORN\b"},
    {"name": "Weston & Sampson Engineers, Inc.", "kind": "consultant", "pure": False, "pattern": r"\bWESTON\s*(?:AND|&)\s*SAMPSON\b"},
    {"name": "Horsley Witten Group", "kind": "consultant", "pure": False, "pattern": r"\bHORSLEY\s+WITTEN\b"},
    {"name": "Industria Engineering", "kind": "consultant", "pure": False, "pattern": r"\bINDUSTRIA\b"},
    {"name": "Foley Hoag LLP", "kind": "attorney", "pure": False, "pattern": r"\bFOLEY\s+HOAG\b"},
    {"name": "Pierce Atwood LLP", "kind": "attorney", "pure": False, "pattern": r"\bPIERCE\s+ATWOOD\b"},
    {"name": "Nutter McClennen & Fish LLP", "kind": "attorney", "pure": False, "pattern": r"\bNUTTER\b"},
    {"name": "Bacon Wilson, P.C.", "kind": "attorney", "pure": False, "pattern": r"\bBACON\s+WILSON\b"},
]
_STORAGE_ONLY = {"Stem Inc.", "SYSO Technologies", "Hecate Energy", "Cranberry Point Energy Storage LLC",
                 "Medway Grid LLC", "Moraga Storage LLC", "Hillman Energy Center LLC", "Blue Sky Utility",
                 "East Point Energy", "Enel X", "S&C Electric"}
for _k in KNOWN:
    _k["rx"] = re.compile(_k["pattern"])
    _k["topic"] = {"datacenter": "data_center", "wind": "wetlands_filing", "utility": "wetlands_filing",
                   "tower": "wireless_telecom"}.get(_k["kind"],
                                                    "battery_storage" if _k["name"] in _STORAGE_ONLY else "solar")

# Generic markers for payors that are engineers / consultants / law firms (agents, not parents).
CONSULTANT_RX = re.compile(
    r"\bENGINEER|\bENG\b|\bENGRG?\b|\bCONSULT|\bSURVEY|\bSVY\b|\bASSOC\b|\bENV\b|\bENVIRO\b|\bENVIRONMENTAL\b|\bECOLOG|\bWETLAND|\bLAND\s+(?:DESIGN|PLANNING|SURVEY|USE)|"
    r"\bCIVIL\b|\bDESIGN\b|\bPLANNING\b|\bARCHITECT|\bASSOCIATES\b|\bGEOTECH|\bHYDRO(?:LOGIC|GEOLOGIC)|"
    r"\bBSC\s+GROUP\b|\bVHB\b|\bTIGHE\s*&\s*BOND\b|\bGZA\b|\bSTANTEC\b|\bTETRA\s+TECH\b|\bHALEY\b|\bNITSCH\b|"
    r"\bMERIDIAN\b|\bLEC\b|\bEBI\b|\bWSP\b|\bBOWMAN\b|\bEPSILON\b|\bESS\s+GROUP\b|\bGOULET\b|\bHANCOCK\s+ASSOC|"
    r"\bGODDARD\b|\bCOASTAL\s+ENGINEERING\b|\bBRACKEN\b|\bLUCAS\s+ENVIRONMENTAL\b|\bOXBOW\b|\bNORMANDEAU\b|"
    r"\bPOWER\s+ENGINEERS\b|\bTRC\b|\bAECOM\b|\bJACOBS\b|\bBURNS\s*&\s*MCDONNELL\b|\bDAVEY\b|\bVANASSE\b|"
    r"\bSITEC\b|\bOUTBACK\b|\bATLANTIC\s+DESIGN\b|\bSTERLING\b")
ATTORNEY_RX = re.compile(r"\bLLP\b|\bLAW\b|\bATTORNEY|\bESQ\b|\bP\.?\s?C\.?$|\bLEGAL\b")

ORG_RX = re.compile(
    r"\bL\.?\s?L\.?\s?C\b|\bINC\b|\bCORP|\bCO\b|\bCOMPANY\b|\bCOMPANIES\b|\bTRUST\b|\bTRUSTEES?\b|\bL\.?P\b|"
    r"\bLTD\b|\bPARTNERS|\bASSOC|\bASSN\b|\bTOWN\b|\bCITY\b|\bCOUNTY\b|\bCOMMONWEALTH\b|\bDEPARTMENT\b|\bDEPT\b|"
    r"\bDPW\b|\bAUTHORITY\b|\bCOMMISSION\b|\bBOARD\b|\bDISTRICT\b|\bUNIVERSITY\b|\bCOLLEGE\b|\bSCHOOL|\bACADEMY\b|"
    r"\bCHURCH\b|\bPARISH\b|\bDIOCESE\b|\bCLUB\b|\bSOCIETY\b|\bFOUNDATION\b|\bINSTITUTE\b|\bHOSPITAL\b|\bCENTER\b|"
    r"\bENERGY\b|\bSOLAR\b|\bPOWER\b|\bELECTRIC\b|\bGAS\b|\bWATER\b|\bUTILIT|\bGRID\b|\bRENEWABLE|\bSTORAGE\b|"
    r"\bDEVELOPMENT\b|\bDEV\b|\bREALTY\b|\bREAL\s+ESTATE\b|\bPROPERT|\bHOMES\b|\bHOUSING\b|\bBUILDERS?\b|"
    r"\bCONSTRUCTION\b|\bCONTRACT|\bENGINEER|\bCONSULT|\bSURVEY|\bENVIRONMENTAL\b|\bASSOCIATES\b|\bGROUP\b|"
    r"\bHOLDINGS?\b|\bMANAGEMENT\b|\bMGMT\b|\bENTERPRISES?\b|\bINDUSTR|\bSERVICES?\b|\bFARMS?\b|\bNOMINEE\b|"
    r"\bESTATES?\b|\bCONSERVATION\b|\bLAND\b|\bVENTURES?\b|\bCAPITAL\b|\bFUND\b|\bBANK\b|\bLLP\b|\bLAW\b|"
    r"\bMASSDOT\b|\bMBTA\b|\bDCR\b|\bDEP\b|\bU\.?S\.?\b|\bFEDERAL\b|\bNATIONAL\b|\bRAILROAD\b|\bRAILWAY\b|"
    r"\bASSOCIATION\b|\bCONDOMINIUM|\bCONDO\b|\bYACHT\b|\bMARINA\b|\bBEACH\b|\bCAMP\b|\bGOLF\b|\bCOUNTRY\b|"
    r"\bSYSTEMS?\b|\bTECHNOLOG|\bSOLUTIONS\b|\bPARTNERSHIP\b|\bORGANIZATION\b|\bCOOPERATIVE\b|\bCO-OP\b|"
    r"\bTOWERS?\b|\bWIRELESS\b|\bCOMMUNICATIONS?\b|\bVERIZON\b|\bAT&T\b|\bT-MOBILE\b|\bCELLCO\b|"
    r"\bSTORE\b|\bMARKET\b|\bRESTAURANT\b|\bHOTEL\b|\bINN\b|\bMALL\b|\bPLAZA\b|\bAIRPORT\b|\bPORT\b|"
    r"\bHARBOR\b|\bSHELLFISH\b|\bOYSTER|\bAQUACULTURE\b|\bSEA\s+FARM|\bORCHARD|\bNURSERY\b|\bCRANBERR|"
    r"\b(?:INC|LLC|CORP)\.?$")


def known_match(name: str | None, kinds: tuple[str, ...] | None = None) -> dict | None:
    if not name:
        return None
    u = name.upper()
    for k in KNOWN:
        if (kinds is None or k["kind"] in kinds) and k["rx"].search(u):
            return k
    return None


def looks_org(name: str | None) -> bool:
    if not name:
        return False
    u = name.upper()
    return bool(ORG_RX.search(u) or known_match(u) or CONSULTANT_RX.search(u))


_PERSON_LAST_FIRST = re.compile(r"^[A-Z][A-Z'\-]+,\s*[A-Z][A-Z'\-\.]*(?:\s+[A-Z][A-Z'\-\.]*){0,2}(?:\s*[/&]\s*[A-Z'\-\.\s]+)?$", re.I)


def org_only(name: str | None, lenient: bool = False) -> str:
    """Keep only the organization part of a name field; '' when it names a private person.
    Drops 'ATTN: <person>', 'c/o <person>' and the person in 'TYRRELL (NEP) MICHAEL'."""
    n = clean(name)
    if not n:
        return ""
    n = re.sub(r"\s*\bATTN\b:?.*$", "", n, flags=re.I).strip(" ,")
    m = re.match(r"^[A-Z'\-]+\s*\(([^)]+)\)\s*[A-Z'\-\.]+$", n, re.I)
    if m:
        return m.group(1).strip() if looks_org(m.group(1)) else ""
    co = re.search(r"\s*,?\s*\bC\s*/\s*O\b\s*(.+)$", n, re.I)
    if co and not looks_org(co.group(1)):
        n = n[:co.start()].strip(" ,")
    if looks_org(n):
        parts = [x.strip() for x in re.split(r"\s*[,;]\s*|\s+/\s+", n) if x.strip()]
        if len(parts) > 1 and not all(looks_org(x) or len(x) <= 4 for x in parts):
            kept = [x for x in parts if looks_org(x) or (len(x) <= 4 and x.upper() in {"INC", "LLC", "LP", "CO"})]
            return ", ".join(kept)
        return n
    if lenient and not _PERSON_LAST_FIRST.match(n) and len(n.split()) >= 3:
        return n                                             # company field without a marker ("MASS AUDUBON SOCIETY")
    return ""


def is_consultant(name: str | None) -> bool:
    if not name:
        return False
    k = known_match(name)
    if k:
        return k["kind"] in ("consultant", "attorney")
    u = name.upper()
    return bool(CONSULTANT_RX.search(u) or ATTORNEY_RX.search(u))


# ============================================================================ normalization
def clean(s: str | None) -> str:
    s = html.unescape(html.unescape(s or ""))                # descriptions sometimes carry "&AMP;"
    s = re.sub(r"&AMP;", "&", s, flags=re.I)
    return re.sub(r"\s+", " ", s.replace("\u00a0", " ").replace("\u00ad", "")).strip()


def clean_address(s: str | None) -> str:
    # The portal appends internal markers ("**", "**#", "*") to addresses.
    return clean(re.sub(r"[*#^]+\s*$", "", clean(s)))


def norm_name(s: str | None) -> str:
    """Comparison key for organization names."""
    u = clean(s).upper()
    u = re.sub(r"[.,'\"]", "", u)
    u = re.sub(r"\b(?:LLC|L L C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LP|LTD|LLP|THE)\b", " ", u)
    u = u.replace("&", " AND ")
    return re.sub(r"\s+", " ", u).strip()


# Fee-check note at the end of Comments: "// CK#5707 NEW LEAF ENERGY", "CK# 1234 & 1235 FOO LLC",
# "CHECK #12 FOO", "MO#123 FOO" (money order). Payor = the text after the check number(s).
CHECK_RX = re.compile(
    r"(?:^|[\s/;,(])(?:CK|CHK|CHECK|CHECKS|CKS|CK\.|M\.?O\.?|MONEY\s+ORDER|BANK\s+CHECK|CASHIERS?\s+CHECK|"
    r"CERTIFIED\s+CHECK|TREASURER'?S?\s+CHECK)\s*S?\s*(?:NO\.?|NUMBER)?\s*[#:]?\s*"
    r"(?P<nums>[A-Z]{0,3}[0-9][0-9A-Z\-]*(?:\s*(?:[,&+/]|AND)\s*#?\s*[A-Z]{0,3}[0-9][0-9A-Z\-]*)*|"
    r"(?:INFO\s+)?NOT\s+PROVIDED|N/?A|UNKNOWN)\s*"
    r"(?:[-:,]\s*)?(?:FROM\s+|BY\s+|PAID\s+BY\s+|PAYOR\s*:?\s*)?(?P<payor>.*)", re.I)
# Placeholder text DEP's system puts in the description field before staff fill it in.
PLACEHOLDER_RX = re.compile(r"^(?:SYSTEM\s+GENERATED\s+TASK|WAITING\s+FOR\s+(?:FEE|PAYMENT)\b.*|PAYMENT\s+NOT\s+RECEIVED\b.*|"
                            r"FEE\s+NOT\s+(?:YET\s+)?RECEIVED\b.*|N/?A|NONE|TBD)\.?$", re.I)
# "//"-separated note segments that are bookkeeping, not project description.
ADMIN_RX = re.compile(r"^(?:#\s*[A-Z0-9][A-Z0-9\-]*\b.*|[A-Z]{1,4}\d?[A-Z]?-\d+-\d+\b.*|APPROX\.?\s+LAT.*|[A-Z]{0,5}\s*DEP\s+TRANSACTION\s+ID\b.*|"
                      r"P(?:AI)?D\s+ON[\s-]?LINE.*|E[\s-]?PAY.*|FEE\s+(?:WAIVED|EXEMPT).*|(?:FEE\s+)?EXEMPT\b.*|"
                      r"NO\s+FEE\b.*|MUNICIPAL(?:LY)?\s+EXEMPT.*|(?:CK|CHECK)\s+INFO.*)$", re.I)


def split_comments(comments: str | None) -> tuple[str, str | None, list[str]]:
    """-> (project description, payor text or None, other admin segments)."""
    text = clean(comments)
    if not text:
        return "", None, []
    payor = None
    desc_parts, admin = [], []
    for seg in [s.strip() for s in re.split(r"\s*//+\s*", text) if s.strip()]:
        m = CHECK_RX.search(" " + seg)
        if m and payor is None:
            before = (" " + seg)[:m.start()].strip(" -;,")
            if before:
                desc_parts.append(before)
            p = clean(m.group("payor")).strip(" -;,.:")
            payor = p or None
        elif ADMIN_RX.match(seg):
            admin.append(seg)          # internal codes ("#WC-52-21"), eDEP transaction ids, online payment
        else:
            desc_parts.append(seg)
    desc = clean(" // ".join(p for p in desc_parts if not PLACEHOLDER_RX.match(p.strip())))
    return desc, payor, admin


def contact_key(person: str | None) -> str | None:
    p = re.sub(r"[^A-Z]", "", clean(person).upper())
    if len(p) < 4:
        return None
    return hashlib.sha256(f"{CONTACT_SALT}|{p}".encode()).hexdigest()[:12]


FILING_TYPES = {
    "NOI": "Notice of Intent",
    "BUFFER ZONE": "Notice of Intent (buffer zone only)",
    "ANRAD DELINEATION": "ANRAD (resource area delineation)",
    "ANRAD": "ANRAD (resource area delineation)",
}


def build_record(row: dict, detail: dict | None, towns: dict[str, dict]) -> dict:
    noi_id = str(row["NOIId"])
    detail = detail or {}
    t = towns.get(clean(row.get("TownName")).upper(), {})
    town = t.get("town") or clean(row.get("TownName")).title()
    company = org_only(clean(row.get("Company")), lenient=True)
    person = clean(row.get("ApplicantName"))
    info = clean(detail.get("ApplicantInformation"))
    applicant = company or org_only(info) or org_only(person)
    is_indiv = not applicant and bool(person or info or clean(row.get("Company")))
    description, payor_raw, admin = split_comments(detail.get("Comments"))
    payor = org_only(payor_raw) if payor_raw else None
    payor_indiv = False
    if payor_raw:
        if payor and norm_name(payor) and norm_name(payor) == norm_name(applicant):
            payor = applicant
        elif not payor:
            payor, payor_indiv = INDIVIDUAL, True
    ftype_raw = clean(detail.get("FilingType"))
    ptypes = []
    for p in clean(detail.get("ProjectType")).split(","):
        p = p.strip()
        if p and p not in ptypes:
            ptypes.append(p)
    areas = [clean(a.get("ResourceAreaName")).title() for a in
             (detail.get("InlandResourceAreas") or []) + (detail.get("CoastalResourceAreas") or [])
             if clean(a.get("ResourceAreaName"))]
    dep_no = clean(row.get("NOINum") or detail.get("NOINum")) or None
    issued = (row.get("OOCDate") or detail.get("OOCDate") or "")[:10] or None
    if re.search(r"\bWITHDRAWN\b", description or "", re.I):
        status = "withdrawn"
    elif issued:
        status = "decision_issued"
    elif dep_no:
        status = "file_number_issued"
    else:
        status = "received"
    rec = {
        "noi_id": noi_id,
        "dep_file_number": dep_no,
        "town": town,
        "county": t.get("county"),
        "filing_type": FILING_TYPES.get(ftype_raw.upper(), ftype_raw or None),
        "project_type": ", ".join(ptypes) or None,
        "received_date": (row.get("FilingDate") or "")[:10] or None,
        "issued_date": issued,
        "status": status,
        "soc_requested": clean(detail.get("SOCRequest")).upper() == "YES",
        "applicant": applicant or (INDIVIDUAL if is_indiv else None),
        "applicant_is_individual": is_indiv,
        "payor": payor,
        "payor_is_individual": payor_indiv,
        "project_address": clean_address(row.get("ProjectAddress") or detail.get("ProjectAddress")) or None,
        "description": description or None,
        "resource_areas": sorted(set(areas)),
        "dep_technical_comments": bool(clean(detail.get("TechnicalComments"))),
        "contact_key": contact_key(person) if applicant and person and not looks_org(person) else None,
        "source_url": RECORD_PAGE.format(id=noi_id),
        "api_url": f"{LIST_URL}/{noi_id}",
        "detail_ok": bool(detail),
        "list_sig": list_sig(row),
    }
    return rec


def list_sig(row: dict) -> str:
    keys = ("NOINum", "FilingDate", "ApplicantName", "Company", "OOCDate", "TownName", "ProjectAddress")
    return hashlib.sha1(json.dumps([row.get(k) for k in keys]).encode()).hexdigest()[:10]


# ============================================================================ classification
_SOLAR = re.compile(r"\bsolar\b|\bphoto\s?-?voltaics?\b|\bagri-?voltaics?\b|\bP\.?V\.?\s+(?:array|system|panels?|modules?|"
                    r"facility|installation|project|canopy|carport)s?\b", re.I)
_SOLAR_NOT = re.compile(r"\bsolar[\s-]+(?:powered|power(?:ed)?\s+(?:lights?|pumps?|gates?|signs?)|lights?|lighting|lamps?|"
                        r"pumps?|compactors?|bollards?|aerat\w*|fountains?|signs?|beacons?|gates?|cameras?|"
                        r"(?:weather|monitoring)\s+stations?|charg\w+|panel\s+(?:on|for)\s+(?:the\s+)?(?:pump|gate|sign|light)\w*)"
                        r"|\bsolar\s+(?:way|ave(?:nue)?|drive|dr|road|rd|street|st|lane|ln|circle|cir|terrace)\b", re.I)
_STORAGE_WORD = r"(?:storage|stroage|storgae|sotrage|strorage)"          # DEP data-entry typos seen in the data
_BESS = re.compile(rf"\bBESS\b|\bbattery\s+(?:energy\s+)?{_STORAGE_WORD}\b|\benergy\s+{_STORAGE_WORD}\b|\bbatter(?:y|ies)\b", re.I)
_BATTERY_CONTEXT = re.compile(r"storage|\bMWh?\b|\bkWh?\b|megawatt|substation|interconnect|solar|energy|"
                              r"containers?|enclosures?|inverters?", re.I)
_BATTERY_NOT = re.compile(r"battery\s+(?:st(?:reet)?|road|rd|wharf|march|lane|ln|park|point|hill|terrace|way|ave)\b|"
                          r"battery\s+(?:back[\s-]?up|backup)|back[\s-]?up\s+batter|batter(?:y|ies)\s+(?:for|at)\s+(?:the\s+)?"
                          r"(?:pump|lift|generator|telecom|cell|antenna|radio)|recycl|"
                          r"\b(?:antenna|monopole|cell(?:ular)?\s+tower|wireless|telecommunication|small\s+cell)\w*", re.I)
_DATACENTER = re.compile(r"\bdata[\s-]+cent(?:er|re)s?\b|\bhyperscale\b|\bserver\s+farm\b|"
                         r"\b(?:crypto(?:currency)?|bitcoin)\s+mining\b", re.I)
_SUBSTATION = re.compile(r"\bsub[\s-]?stations?\b|\bswitch(?:ing)?\s+stations?\b|\bswitch\s?yards?\b", re.I)
_SUBSTATION_NOT = re.compile(r"\b(?:fire|police|ems|ambulance|pump(?:ing)?|sewer|water|wastewater|lift|"
                             r"public\s+safety|highway|dpw)\s+sub[\s-]?stations?\b", re.I)
_TRANSMISSION = re.compile(r"\btransmission\s+(?:lines?|structures?|towers?|corridors?|right[\s-]of[\s-]ways?|"
                           r"ROW|system|project|upgrades?|rebuilds?|poles?|circuits?|facilit(?:y|ies)|cables?|"
                           r"infrastructure|structure\s+replacements?)\b|"
                           r"\breconductor\w*|\b(?:69|115|230|345)\s*-?\s*kV\b|\bkilovolt", re.I)
_TRANSMISSION_NOT = re.compile(r"\b(?:water|sewer|gas|force)\s+(?:transmission\s+)?mains?\b|\bwater\s+transmission\b|"
                               r"\btransmission\s+mains?\b|\bgas\s+transmission\b", re.I)
_KV = re.compile(r"\b(\d{1,3}(?:\.\d+)?)\s*-?\s*kV\b", re.I)
_UTILITY_ROUTINE = re.compile(r"\b(?:utility\s+)?poles?\b|\bvegetation\s+management\b|\bdistribution\s+lines?\b|"
                              r"\bunderground\s+(?:cable|conduit|electric)|\bmanholes?\b|\bgas\s+(?:main|service|line)s?\b|"
                              r"\bhazard\s+tree|\btree\s+(?:removal|trimming|pruning)", re.I)
_WIND = re.compile(r"\bwind\s+(?:turbines?|farm|energy\s+(?:facility|project|area)|project|power\s+project)\b|"
                   r"\boffshore\s+wind\b|\bexport\s+cables?\b|\bcable\s+landfall\b|"
                   r"\b(?:wave|tidal)\s+energy\b|\bhydrokinetic\b", re.I)
_EV = re.compile(r"\bEV\s+charg\w*|\belectric\s+vehicle\s+(?:charg\w*|supply)|\bcharging\s+stations?\b", re.I)
_SIZE = re.compile(r"\b(\d{1,4}(?:[.,]\d+)?)\s*-?\s*(MW|megawatts?|kW|kilowatts?)(?:\s*(?:AC|DC))?\b", re.I)
_COMMERCIAL_SOLAR = re.compile(
    r"\bsolar\s+(?:farm|facility|facilities|field|project|garden|canopy|canopies|carports?|park|plant|"
    r"generating|electric\s+generat\w+|energy\s+(?:facility|project|generat\w+))|"
    r"\bcommunity\s+solar\b|\butility[\s-]scale\b|\bagri-?voltaic|\bfloating\s+solar\b|\bdual[\s-]use\s+solar\b|"
    r"\bcanop(?:y|ies)\s+(?:solar|array|PV|over\s+(?:the\s+)?(?:existing\s+)?(?:parking|lot|canal))|"
    r"\bparking\s+(?:lot\s+|area\s+)?canop|\bcarports?\b|\b\d+(?:\.\d+)?\s*(?:\+/-\s*)?acres?\b|\bsolar\s+photovoltaic\s+facility\b|"
    r"\binterconnect\w*|\bmegawatt|\bmw\b", re.I)
_WEAK_COMMERCIAL_SOLAR = re.compile(r"\b(?:ground|pole)[\s-]+mounted\s+(?:solar|photovoltaic|PV)\b|"
                                    r"\b(?:solar|photovoltaic|PV)\s+(?:array|arrays|panels?|systems?|installation|"
                                    r"facility|energy\s+system)\b|\btransformers?\b", re.I)
_RESIDENTIAL = re.compile(r"\bsingle[\s-]family\b|\bSFH\b|\bSFD\b|\bdwelling\b|\bhouse\b|\bhome\b|\bresiden\w+|"
                          r"\bgarage\b|\bdeck\b|\bporch\b|\bshed\b|\bpool\b|\baddition\b|\bbackyard\b|"
                          r"\bseptic\b|\bcottage\b", re.I)
_ROOFTOP = re.compile(r"\broof\b|\broof[\s-]?(?:top|mounted)\b|\brooftop\b", re.I)
# Energy words in applicant/payor names. Bare "STORAGE" is excluded (self-storage LLCs are common).
_ENERGY_NAME = re.compile(r"\bSOLAR\b|\bPHOTOVOLTAIC\b|\bENERGY\s+STORAGE\b|\bBATTERY\b|\bBESS\b"
                          r"|\bRENEWABLES?\b|\bDATA\s+CENT(?:ER|RE)\b|\bWIND\s+(?:LLC|INC|ENERGY|POWER|FARM|PROJECT)\b")
# Utility work in a transmission right-of-way (structure replacements) is transmission, not distribution.
_UTILITY_TRANSMISSION = re.compile(r"\bROW\b|\bright[\s-]of[\s-]ways?\b|\bstructure\s+replacements?\b|"
                                   r"\btransmission\b|\bsub[\s-]?stations?\b", re.I)


def _hits(rx: re.Pattern, text: str, not_rx: re.Pattern | None = None, window: int = 0) -> list[str]:
    """Matches of rx in text that do not sit inside a not_rx match (searched +-window chars)."""
    out = []
    for m in rx.finditer(text):
        if not_rx is not None:
            ctx = text[max(0, m.start() - window):m.end() + window] if window else text
            bad = False
            for n in not_rx.finditer(ctx):
                if window:
                    bad = True
                    break
                if n.start() <= m.start() and m.end() <= n.end():
                    bad = True
                    break
            if bad:
                continue
        out.append(m.group(0))
    return out


def _size_kw(text: str) -> float | None:
    best = None
    for m in _SIZE.finditer(text):
        try:
            v = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        kw = v * 1000 if m.group(2).upper().startswith("M") else v
        best = kw if best is None else max(best, kw)
    return best


def classify(rec: dict) -> dict:
    """Energy / data-center classification of one filing. Returns
    {category, hit, topics, energy_topics, signals, confidence, note}."""
    desc = rec.get("description") or ""
    ptype = rec.get("project_type") or ""
    applicant = "" if rec.get("applicant_is_individual") else (rec.get("applicant") or "")
    payor = "" if rec.get("payor_is_individual") else (rec.get("payor") or "")
    text = f"{desc} . {ptype}"
    names = f"{applicant} | {payor}"
    signals: list[str] = []
    topics: list[str] = []

    k_app = known_match(applicant)
    k_pay = known_match(payor)
    dev = next((k for k in (k_app, k_pay) if k and k["kind"] in ("developer", "datacenter", "wind")), None)
    utility = next((k for k in (k_app, k_pay) if k and k["kind"] == "utility"), None)

    solar = _hits(_SOLAR, text, _SOLAR_NOT)
    battery = [h for h in _hits(_BESS, text) if not re.fullmatch(r"batter(?:y|ies)", h, re.I)]
    covered = [(m.start(), m.end()) for m in _BESS.finditer(text) if not re.fullmatch(r"batter(?:y|ies)", m.group(0), re.I)]
    for m in re.finditer(r"\bbatter(?:y|ies)\b", text, re.I):     # bare "battery" needs storage context
        if any(a <= m.start() < b for a, b in covered):
            continue
        ctx = text[max(0, m.start() - 80):m.end() + 80]
        if _BATTERY_CONTEXT.search(ctx) and not _BATTERY_NOT.search(text[max(0, m.start() - 60):m.end() + 60]):
            battery.append(m.group(0))
    datacenter = _hits(_DATACENTER, text)
    substation = _hits(_SUBSTATION, text, _SUBSTATION_NOT)
    transmission = _hits(_TRANSMISSION, text, _TRANSMISSION_NOT, window=0)
    kvs = [float(x) for x in _KV.findall(text)]
    if transmission and any(re.fullmatch(r"\d.*kV", t, re.I) for t in transmission) and not any(v >= 69 for v in kvs):
        transmission = [t for t in transmission if not re.search(r"kV", t, re.I)]
    wind = _hits(_WIND, text)
    ev = _hits(_EV, text)
    name_energy = _ENERGY_NAME.findall(names.upper())
    size_kw = _size_kw(text)

    category, hit, confidence, note = None, False, None, None

    if datacenter or (dev and dev["kind"] == "datacenter" and dev["pure"]):
        category, hit = "data_center", True
        topics.append("data_center")
        signals += [f"desc:{h}" for h in datacenter] or [f"name:{dev['name']}"]
        confidence = "high" if datacenter else "medium"

    if battery:
        topics.append("battery_storage")
        signals += [f"desc:{h}" for h in battery]
    if solar:
        topics.append("solar")
        signals += [f"desc:{h}" for h in solar]

    if solar or battery:
        # Scale decides whether this is a siting item. Precedence: stated size, then strong
        # commercial wording, then residential cues, then weaker commercial cues.
        strong = _COMMERCIAL_SOLAR.search(text)
        weak = _WEAK_COMMERCIAL_SOLAR.search(text)
        house = _RESIDENTIAL.search(text)
        roof = _ROOFTOP.search(text)
        installer = known_match(applicant, ("residential_installer",)) or known_match(payor, ("residential_installer",))
        named = bool(name_energy) or (dev is not None and dev["kind"] == "developer")
        if battery and not solar:
            base = "battery_storage"
        elif battery and solar:
            base = "solar_and_storage"
        else:
            base = "solar"
        if size_kw is not None and size_kw >= 250:
            scale, why = "commercial", f"stated size {size_kw:g} kW"
        elif size_kw is not None and size_kw < 50:
            scale, why = "residential", f"stated size {size_kw:g} kW"
        elif strong:
            scale, why = "commercial", f"'{strong.group(0)}'"
        elif house or rec.get("applicant_is_individual") or installer:
            scale, why = "residential", "house/roof wording, private applicant or residential installer"
        elif roof:
            scale, why = "rooftop", "roof-mounted on a non-residential building"
        elif named or weak or battery:
            scale, why = "commercial", "developer/energy name or ground-mount wording"
        else:
            scale, why = "unclear", "no scale cue"
        if scale == "residential":
            category = category or ("solar_residential" if not battery else "storage_residential")
            topics = [t for t in topics if t not in ("solar", "battery_storage")]
            note = f"residential scale ({why}); not a siting item"
        else:
            category = category or (base if scale != "rooftop" else "solar_rooftop_commercial")
            hit = True
            if scale == "commercial":
                confidence = "high" if (strong or named or (size_kw or 0) >= 250 or (battery and not solar)) else "medium"
            else:
                confidence = "low" if scale == "unclear" else "medium"
                note = f"{scale} ({why})"
        signals.append(f"scale:{scale}")
        if size_kw is not None:
            signals.append(f"size_kw:{size_kw:g}")

    line_work = re.search(r"structure|\blines?\b|maintenance|improvement|access\s+road|work\s+pad|refurbish|"
                          r"rebuild|upgrade|reconstruct", text, re.I)
    if utility and not (substation or transmission) and _UTILITY_TRANSMISSION.search(text) and line_work \
            and not _UTILITY_ROUTINE.search(text.replace("structure", "")):
        transmission = [m.group(0) for m in _UTILITY_TRANSMISSION.finditer(text)]
    elif utility and not (substation or transmission) and re.search(r"\bNEW\s+ENGLAND\s+POWER\b", applicant.upper()) \
            and _UTILITY_TRANSMISSION.search(text) and line_work:
        transmission = [m.group(0) for m in _UTILITY_TRANSMISSION.finditer(text)]      # NEP is National Grid's transmission company
    if not (substation or transmission):
        transmission = [m.group(0) for m in re.finditer(
            r"\belectric(?:al)?\s+(?:utility\s+|transmission\s+)?(?:ROW|right[\s-]of[\s-]ways?)\b", text, re.I)]
    if (substation or transmission) and not hit:
        category, hit, confidence = "transmission_substation", True, "high" if substation else "medium"
        signals += [f"desc:{h}" for h in substation + transmission]
    elif (substation or transmission) and hit:
        signals += [f"desc:{h}" for h in substation + transmission]

    if wind and not hit:
        category, hit, confidence = "wind_or_marine", True, "medium"
        signals += [f"desc:{h}" for h in wind]

    if not hit and not category and dev and dev["pure"] and dev["kind"] in ("developer", "wind"):
        category = "developer_other" if dev["kind"] == "developer" else "wind_or_marine"
        hit, confidence = True, "medium"
        topics.append(dev["topic"])
        signals.append(f"name:{dev['name']}")
        note = "known energy developer; description has no energy keyword"
    elif not hit and not category and name_energy:
        joined = " ".join(name_energy)
        strong_name = re.search(r"SOLAR|PHOTOVOLTAIC|STORAGE|BATTERY|BESS|DATA|WIND", joined)
        category, hit, confidence = "energy_name_only", True, "medium" if strong_name else "low"
        name_topic = ("battery_storage" if re.search(r"STORAGE|BATTERY|BESS", joined) else
                      "data_center" if "DATA" in joined else
                      "solar" if re.search(r"SOLAR|PHOTOVOLTAIC", joined) else None)
        if name_topic:
            topics.append(name_topic)
        signals += [f"name:{n}" for n in name_energy]
        note = "energy word in applicant/payor name only"

    if not hit and not category and utility and not re.search(r"\bGAS\b", applicant.upper()) \
            and rec.get("status") != "withdrawn" and not _UTILITY_ROUTINE.search(text):
        nep = re.search(r"NEW\s+ENGLAND\s+POWER|\bNEP\b", applicant.upper())
        anrad = (rec.get("filing_type") or "").startswith("ANRAD")
        if nep or anrad:
            category, hit, confidence = "transmission_substation", True, "low"
            signals.append("name:New England Power (transmission owner)" if nep else "utility ANRAD")
            note = ("filing by National Grid's transmission company; no line/substation keyword in the description yet"
                    if nep else "electric utility resource-area delineation (often ahead of a substation or line project)")
    if not category and ev:
        category = "ev_charging"
        note = "EV charging; not tracked as a siting topic"
    if not category and utility:
        category = "utility_routine"
        note = ("utility maintenance (poles, cables, vegetation, gas)" if _UTILITY_ROUTINE.search(text)
                else "utility filing without substation/transmission keywords")

    if dev and f"name:{dev['name']}" not in signals:
        signals.append(f"name:{dev['name']}")
    # de-duplicate, keep order
    topics = list(dict.fromkeys(topics))
    return {
        "category": category,
        "hit": hit,
        "topics": (["wetlands_filing"] + topics) if hit else [],
        "energy_topics": topics,
        "confidence": confidence if hit else None,
        "signals": list(dict.fromkeys(signals))[:12],
        "note": note,
    }


# ============================================================================ entity linking
def resolve_links(records: list[dict]) -> dict[str, dict]:
    """For each energy-related filing: who is the parent developer behind the applicant?
    Returns noi_id -> {parent, parent_kind, link, confidence, consultant, evidence}."""
    energy = [r for r in records if r["classification"]["hit"]]
    out: dict[str, dict] = {}
    # pass 1: direct evidence in the filing itself
    for r in energy:
        app = "" if r["applicant_is_individual"] else (r["applicant"] or "")
        pay = "" if r["payor_is_individual"] else (r["payor"] or "")
        link: dict = {"parent": None, "parent_kind": None, "link": None, "confidence": None,
                      "consultant": None, "evidence": None}
        k_app = known_match(app)
        k_pay = known_match(pay)
        co = re.search(r"\bC\s*/\s*O\s+(.+)$", app, re.I)
        if pay and is_consultant(pay):
            link["consultant"] = (k_pay or {}).get("name") or pay
        if k_app and k_app["kind"] not in ("consultant", "attorney", "residential_installer"):
            link.update(parent=k_app["name"], parent_kind=k_app["kind"], link="applicant_name", confidence="high",
                        evidence=f"applicant name '{app}' matches {k_app['name']}")
        elif co and not is_consultant(co.group(1)):
            k_co = known_match(co.group(1))
            link.update(parent=(k_co or {}).get("name") or clean(co.group(1)).strip(" ,."),
                        parent_kind=(k_co or {}).get("kind") or "company", link="care_of", confidence="high",
                        evidence=f"applicant listed as '{app}'")
        elif pay and k_pay and k_pay["kind"] not in ("consultant", "attorney", "residential_installer"):
            link.update(parent=k_pay["name"], parent_kind=k_pay["kind"],
                        link="self" if norm_name(pay) == norm_name(app) else "payor",
                        confidence="high", evidence=f"filing fee paid by '{pay}'")
        elif pay and norm_name(pay) != norm_name(app) and not is_consultant(pay):
            link.update(parent=pay, parent_kind="company", link="payor", confidence="medium",
                        evidence=f"filing fee paid by '{pay}' (not a known developer)")
        elif app and (pay == app or not pay or is_consultant(pay)):
            link.update(parent=None, link="unresolved")
        out[r["noi_id"]] = link

    # pass 2: shared contact person (hashed) or same site with a resolved filing (any filing type)
    by_contact: dict[str, list[dict]] = defaultdict(list)
    by_site: dict[tuple, list[dict]] = defaultdict(list)
    by_applicant: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        if r.get("contact_key"):
            by_contact[r["contact_key"]].append(r)
        if r.get("project_address"):
            by_site[(r["town"], _site_key(r["project_address"]))].append(r)
        if r.get("applicant") and not r["applicant_is_individual"]:
            by_applicant[norm_name(r["applicant"])].append(r)

    by_depno = {r["dep_file_number"]: r for r in records if r.get("dep_file_number")}
    by_family: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        if r.get("applicant") and not r["applicant_is_individual"]:
            by_family[_family_key(r["applicant"])].append(r)

    def resolved(r2: dict) -> tuple[str, str] | None:
        l2 = out.get(r2["noi_id"])
        if l2 and l2.get("parent") and l2["link"] in ("applicant_name", "care_of", "payor", "self"):
            return l2["parent"], l2["parent_kind"]
        k = known_match(r2.get("applicant") or "") or known_match(r2.get("payor") or "")
        if k and k["kind"] not in ("consultant", "attorney", "residential_installer"):
            return k["name"], k["kind"]
        return None

    for _ in range(2):
        for r in energy:
            link = out[r["noi_id"]]
            if link.get("parent"):
                continue
            for ref in re.findall(r"\b(\d{3}-\d{4})\b", r.get("description") or ""):
                r2 = by_depno.get(ref)
                if r2 and r2["noi_id"] != r["noi_id"] and resolved(r2):
                    p, kind = resolved(r2)
                    link.update(parent=p, parent_kind=kind, link="references_filing", confidence="high",
                                evidence=f"description cites DEP file {ref} ({r2['town']}, '{r2.get('applicant')}'), "
                                         f"which links to {p}")
                    break
            if link.get("parent"):
                continue
            fam = [x for x in by_family.get(_family_key(r.get("applicant") or ""), [])
                   if norm_name(x.get("applicant") or "") != norm_name(r.get("applicant") or "")]
            for r2 in by_applicant.get(norm_name(r.get("applicant") or ""), []) + fam:
                if r2["noi_id"] != r["noi_id"] and resolved(r2):
                    p, kind = resolved(r2)
                    link.update(parent=p, parent_kind=kind, link="same_applicant_other_filing", confidence="high",
                                evidence=f"same applicant's filing {r2.get('dep_file_number') or r2['noi_id']} "
                                         f"({r2['town']}) links to {p}")
                    break
            if link.get("parent"):
                continue
            for r2 in by_contact.get(r.get("contact_key") or "", []):
                if r2["noi_id"] != r["noi_id"] and resolved(r2):
                    p, kind = resolved(r2)
                    link.update(parent=p, parent_kind=kind, link="shared_contact", confidence="medium",
                                evidence=f"same applicant contact person as filing "
                                         f"{r2.get('dep_file_number') or r2['noi_id']} by "
                                         f"'{r2.get('applicant')}' ({r2['town']})")
                    break
            if link.get("parent"):
                continue
            k_desc = known_match(r.get("description") or "", ("developer", "utility", "datacenter", "wind"))
            if k_desc:
                link.update(parent=k_desc["name"], parent_kind=k_desc["kind"], link="description_mention",
                            confidence="medium", evidence=f"project description names {k_desc['name']}")
                continue
            for r2 in by_site.get((r["town"], _site_key(r.get("project_address") or "")), []):
                if r2["noi_id"] != r["noi_id"] and resolved(r2):
                    p, kind = resolved(r2)
                    link.update(parent=p, parent_kind=kind, link="same_site", confidence="low",
                                evidence=f"same site as filing {r2.get('dep_file_number') or r2['noi_id']} "
                                         f"by '{r2.get('applicant')}'")
                    break
    return out


def _family_key(name: str) -> str:
    """'OLD WARREN ROAD DEVELOPMENT II, LLC' and 'OLD WARREN ROAD DEVELOPMENT, LLC' -> same family."""
    n = norm_name(name)
    n = re.sub(r"(?:\s+(?:I{1,3}|IV|V|VI{0,3}|\d{1,2}))+$", "", n)
    return n if len(n) >= 8 else f"~{norm_name(name)}"


def _site_key(addr: str) -> str:
    a = addr.upper()
    a = re.sub(r"\(.*?\)", " ", a)
    a = re.sub(r"\b(?:STREET|ST)\b", "ST", a)
    a = re.sub(r"\b(?:ROAD|RD)\b", "RD", a)
    a = re.sub(r"\b(?:AVENUE|AVE)\b", "AVE", a)
    a = re.sub(r"\b(?:HIGHWAY|HWY)\b", "HWY", a)
    a = re.sub(r"\b0\s+", "", a)                              # "0 TREMONT STREET" = unnumbered parcel
    a = re.sub(r"[^A-Z0-9 ]", " ", a)
    return re.sub(r"\s+", " ", a).strip()


def canonical_parent(name: str) -> str:
    k = known_match(name)
    return k["name"] if k else name


def build_entities(records: list[dict], links: dict[str, dict], targets: dict[str, dict]) -> dict:
    energy = [r for r in records if r["classification"]["hit"]]
    applicants: dict[str, dict] = {}
    parents: dict[str, dict] = {}
    for r in energy:
        link = links.get(r["noi_id"], {})
        app = r["applicant"] or "(none)"
        key = norm_name(app) or app
        a = applicants.setdefault(key, {"applicant": app, "parent": None, "parent_kind": None, "link": None,
                                        "confidence": None, "filings": 0, "towns": set(), "payors": set(),
                                        "consultants": set(), "categories": Counter(), "evidence": []})
        a["filings"] += 1
        a["towns"].add(r["town"])
        a["categories"][r["classification"]["category"]] += 1
        if r.get("payor") and r["payor"] != app:
            a["payors"].add(r["payor"])
        if link.get("consultant"):
            a["consultants"].add(link["consultant"])
        rank = {"high": 3, "medium": 2, "low": 1, None: 0}
        if link.get("parent") and rank[link.get("confidence")] > rank[a["confidence"]]:
            a.update(parent=canonical_parent(link["parent"]), parent_kind=link.get("parent_kind"),
                     link=link.get("link"), confidence=link.get("confidence"))
        a["evidence"].append({
            "dep_file_number": r.get("dep_file_number"), "town": r["town"], "received_date": r["received_date"],
            "filing_type": r.get("filing_type"), "payor": r.get("payor"), "link": link.get("link"),
            "how": link.get("evidence"), "source_url": r["source_url"],
        })
        if link.get("parent"):
            pname = canonical_parent(link["parent"])
            p = parents.setdefault(pname, {"parent": pname, "kind": link.get("parent_kind"), "filings": 0,
                                           "project_applicants": set(), "sites": set(), "towns": set(),
                                           "categories": Counter(),
                                           "links": Counter(), "consultants": set(), "dep_files": []})
            p["filings"] += 1
            p["project_applicants"].add(app)
            p["sites"].add(f"{r['town']}: {_site_key(r.get('project_address') or '') or '?'}")
            p["towns"].add(r["town"])
            p["categories"][r["classification"]["category"]] += 1
            p["links"][link.get("link")] += 1
            if link.get("consultant"):
                p["consultants"].add(link["consultant"])
            p["dep_files"].append({"dep_file_number": r.get("dep_file_number"), "town": r["town"],
                                   "applicant": app, "received_date": r["received_date"],
                                   "source_url": r["source_url"], "evidence": link.get("evidence")})

    def finish(d: dict) -> dict:
        for k, v in list(d.items()):
            if isinstance(v, set):
                d[k] = sorted(v)
            elif isinstance(v, Counter):
                d[k] = dict(v.most_common())
        return d

    parent_rows = []
    for p in parents.values():
        finish(p)
        p["distinct_applicants"] = len(p["project_applicants"])
        p["distinct_sites"] = len(p["sites"])
        t = targets.get(p["parent"])
        p["in_target_list"] = bool(t)
        if t:
            p["target_segment"] = t.get("segment")
        parent_rows.append(p)
    parent_rows.sort(key=lambda p: (-p["filings"], p["parent"]))
    # applicants that share a (hashed) contact person: clusters of project LLCs run by the same people
    contact_apps: dict[str, set] = defaultdict(set)
    for r in records:
        if r.get("contact_key") and r.get("applicant") and not r["applicant_is_individual"]:
            contact_apps[r["contact_key"]].add(r["applicant"])
    for r in energy:
        a = applicants.get(norm_name(r["applicant"] or "(none)") or (r["applicant"] or "(none)"))
        if a is not None and r.get("contact_key"):
            others = {x for x in contact_apps[r["contact_key"]] if norm_name(x) != norm_name(a["applicant"])}
            a.setdefault("shares_contact_with", set()).update(others)
    app_rows = [finish(a) for a in applicants.values()]
    app_rows.sort(key=lambda a: (a["parent"] is None, -(a["filings"]), a["applicant"]))

    # payors across ALL filings (companies only): who pays wetlands fees most often
    payor_counts: Counter = Counter()
    payor_towns: dict[str, set] = defaultdict(set)
    for r in records:
        p = r.get("payor")
        if p and not r["payor_is_individual"] and norm_name(p) != norm_name(r.get("applicant") or ""):
            name = canonical_parent(p)
            payor_counts[name] += 1
            payor_towns[name].add(r["town"])
    top_payors = [{"payor": n, "filings": c, "towns": len(payor_towns[n]),
                   "kind": (known_match(n) or {}).get("kind") or ("consultant" if is_consultant(n) else "company")}
                  for n, c in payor_counts.most_common(60)]
    return {"parents": parent_rows, "applicants": app_rows, "top_third_party_payors_all_filings": top_payors}


def load_targets() -> dict[str, dict]:
    try:
        with TARGETS_CSV.open(newline="") as f:
            return {row["company"]: row for row in csv.DictReader(f)}
    except OSError:
        return {}


# ============================================================================ hits
def title_case(s: str | None) -> str:
    if not s:
        return ""
    keep = {"LLC", "LP", "LLP", "II", "III", "IV", "BESS", "MW", "KW", "MWH", "KWH", "PV", "DC", "AC",
            "NSTAR", "DPW", "MA", "USA", "US", "NOI", "ANRAD", "ROW", "EV", "AES", "EDF", "CVE", "ZPT", "BWC",
            "DCR", "MBTA", "KV", "BVW", "BLSF", "LUW", "LSCSF", "OOC", "RFA", "ZPB", "REDP", "SPV", "AKA"}
    out = []
    for w in re.split(r"(\s+)", s):
        core = re.sub(r"[^A-Za-z]", "", w).upper()
        if core in keep or (w.startswith("(") and w.endswith(")") and len(core) <= 5):
            out.append(w.upper().replace("KW", "kW").replace("KV", "kV") if core in ("KW", "KV", "MWH", "KWH")
                       else w.upper())
        elif re.match(r"^\d", w):
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:].lower() if w.isupper() or w.islower() else w)
    return re.sub(r"\bC/[Oo]\b", "c/o", "".join(out))


_UNITS = {"KW": "kW", "MW": "MW", "KWH": "kWh", "MWH": "MWh", "KV": "kV", "AC": "AC", "DC": "DC", "SF": "SF"}
_ACRONYMS = {"BESS", "PV", "BVW", "BLSF", "LSCSF", "LUW", "ROW", "RFA", "ACR", "NOI", "ANRAD", "ORAD", "OOC", "SFH",
             "SW", "DEP", "MA", "US", "EV", "HVAC", "LLC", "INC", "NHESP", "DPW", "MBTA", "MASSDOT", "DCR", "II", "III",
             "FEMA", "BFE", "NSTAR", "NECO", "CMR", "MGL", "PVC", "LED", "ADA", "UST", "HDD", "I/A", "IA", "WL", "NGRID"}


def sentence_case(s: str | None) -> str:
    """DEP descriptions are all caps; make them readable but keep units, acronyms and codes."""
    if not s:
        return ""
    out = []
    for tok in re.split(r"(\W+)", s):
        u = tok.upper()
        if not tok or not re.search(r"[A-Za-z]", tok):
            out.append(tok)
        elif u in _UNITS:
            out.append(_UNITS[u])
        elif u in _ACRONYMS or (re.search(r"\d", tok) and re.search(r"[A-Za-z]", tok)):
            out.append(u)
        else:
            out.append(tok.lower())
    text = "".join(out)
    return text[:1].upper() + text[1:]


def snippet_for(r: dict, link: dict) -> str:
    ftype = {"Notice of Intent": "NOI", "Notice of Intent (buffer zone only)": "Buffer-zone NOI",
             "ANRAD (resource area delineation)": "ANRAD"}.get(r.get("filing_type") or "", r.get("filing_type") or "Filing")
    who = title_case(r["applicant"]) if r.get("applicant") and not r["applicant_is_individual"] else "private applicant"
    if r.get("payor") and not r["payor_is_individual"] and norm_name(r["payor"]) != norm_name(r.get("applicant") or ""):
        who += f" (fee paid by {title_case(r['payor'])})"
    desc = sentence_case((r.get("description") or "").strip().rstrip(".")) or "no description"
    addr = title_case(r.get("project_address")) or "address not given"
    s = f"{ftype}, {who}: {desc}. {addr}."
    if len(s) > 240:
        room = 240 - len(f"{ftype}, {who}: . {addr}.") - 1
        s = f"{ftype}, {who}: {desc[:max(room, 40)].rstrip()}… {addr}."
    return s[:240]


def build_hits(records: list[dict], links: dict[str, dict]) -> list[dict]:
    hits = []
    for r in records:
        c = r["classification"]
        if not c["hit"]:
            continue
        link = links.get(r["noi_id"], {})
        snippet = snippet_for(r, link)
        meeting_date = r["received_date"]
        first_seen = r["first_seen"]
        try:
            fs = datetime.fromisoformat(first_seen)
            md = datetime.fromisoformat(meeting_date + "T00:00:00+00:00")
            days_before = round((md - fs).total_seconds() / 86400, 1)
        except (TypeError, ValueError):
            days_before = None
        hits.append({
            "id": hashlib.sha1(f"{r['source_url']}|{snippet}".encode()).hexdigest()[:12],
            "state": "MA",
            "town": r["town"],
            "county": r.get("county"),
            "board": BOARD,
            "board_key": BOARD_KEY,
            "meeting_date": meeting_date,
            "topics": c["topics"],
            "snippet": snippet,
            "source_url": r["source_url"],
            "listing_url": PORTAL + "#!/search/wire",
            "document_title": f"MassDEP wetlands filing {r.get('dep_file_number') or '(file number pending)'}"
                              f" — {r.get('filing_type') or 'filing'}, {r['town']}",
            "text_source": "api",
            "first_seen": first_seen,
            "days_before_meeting": days_before,
            "source": SOURCE,
            "details": {
                "noi_id": r["noi_id"],
                "dep_file_number": r.get("dep_file_number"),
                "filing_type": r.get("filing_type"),
                "project_type": r.get("project_type"),
                "received_date": r["received_date"],
                "issued_date": r.get("issued_date"),
                "status": r.get("status"),
                "soc_requested": r.get("soc_requested"),
                "meeting_date_basis": "filing_date",
                "applicant": r.get("applicant"),
                "payor": r.get("payor"),
                "parent": canonical_parent(link["parent"]) if link.get("parent") else None,
                "parent_link": link.get("link"),
                "parent_confidence": link.get("confidence"),
                "consultant": link.get("consultant"),
                "project_address": r.get("project_address"),
                "description": r.get("description"),
                "category": c["category"],
                "confidence": c["confidence"],
                "signals": c["signals"],
                "api_url": r["api_url"],
            },
        })
    hits.sort(key=lambda h: (h["meeting_date"], h["town"]), reverse=True)
    return hits


# ============================================================================ storage
def load_records() -> dict[str, dict]:
    recs: dict[str, dict] = {}
    try:
        with FILINGS_FILE.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    recs[r["noi_id"]] = r
    except OSError:
        pass
    return recs


def write_json_atomic(path: Path, obj, indent: int | None = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=indent, ensure_ascii=False) + "\n")
    tmp.replace(path)


def write_records(recs: dict[str, dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = FILINGS_FILE.with_suffix(".jsonl.tmp")
    with tmp.open("w") as f:
        for r in sorted(recs.values(), key=lambda r: (r.get("received_date") or "", int(r["noi_id"]))):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")
    tmp.replace(FILINGS_FILE)


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


# ============================================================================ pipeline
def merge(old: dict | None, new: dict, now: str) -> dict:
    new["first_seen"] = (old or {}).get("first_seen") or now
    if old and old.get("list_sig") != new["list_sig"]:
        new["last_changed"] = now
    elif old and old.get("last_changed"):
        new["last_changed"] = old["last_changed"]
    return new


def rebuild_from_cache(recs: dict[str, dict], towns: dict[str, dict], now: str) -> int:
    """Re-normalize every cached filing with the current parsers (no network)."""
    n = 0
    raw_dir = CACHE / "raw"
    if not raw_dir.exists():
        return 0
    for p in raw_dir.glob("*.json"):
        try:
            c = json.loads(p.read_text())
        except ValueError:
            continue
        if not c.get("list"):
            continue
        old = recs.get(c["noi_id"])
        new = build_record(c["list"], c.get("detail"), towns)
        new["detail_fetched_at"] = c.get("fetched_at")
        if old:
            new["first_seen"] = old.get("first_seen") or now
            if old.get("last_changed"):
                new["last_changed"] = old["last_changed"]
        else:
            new["first_seen"] = c.get("fetched_at") or now
        recs[c["noi_id"]] = new
        n += 1
    return n


def run(args: argparse.Namespace) -> dict:
    now = utcnow().isoformat()
    today = utcnow().date()
    towns = load_towns()
    targets = load_targets()
    state = load_state()
    recs = load_records()
    stats: Counter = Counter()
    blocked = None

    rebuilt = rebuild_from_cache(recs, towns, now)
    stats["rebuilt_from_cache"] = rebuilt

    if not args.offline:
        cursor = (state.get("cursor") or {}).get("max_filing_date")
        if args.since:
            since = date.fromisoformat(args.since)
        elif cursor:
            since = date.fromisoformat(cursor) - timedelta(days=LOOKBACK_DAYS)
        else:
            since = today - timedelta(days=365)
        until = date.fromisoformat(args.until) if args.until else today
        client = Client()
        try:
            rows = list_filings(client, since, until)
            stats["listed"] = len(rows)
            todo = []
            recent = (today - timedelta(days=DESCRIPTION_WAIT_DAYS)).isoformat()
            stale = (utcnow() - timedelta(days=2)).isoformat()
            for row in rows:
                nid = str(row["NOIId"])
                old = recs.get(nid)
                if old is None or old.get("list_sig") != list_sig(row) or not old.get("detail_ok"):
                    todo.append(row)
                elif args.refresh_pending and old.get("status") != "decision_issued":
                    todo.append(row)
                elif (not old.get("description") and (old.get("received_date") or "") >= recent
                      and (old.get("detail_fetched_at") or "") < stale):
                    todo.append(row)                         # DEP often adds the description days later
                    stats["refetch_no_description"] += 1
            todo.sort(key=lambda r: r.get("FilingDate") or "")
            stats["details_needed"] = len(todo)
            log.info("%d listed, %d need detail requests (~%.0f min)", len(rows), len(todo), len(todo) * MIN_INTERVAL / 60)
            for i, row in enumerate(todo[: args.max_details] if args.max_details else todo, 1):
                nid = str(row["NOIId"])
                detail = client.get_json(f"{LIST_URL}/{nid}")
                if detail is None:
                    stats["detail_errors"] += 1
                write_cache(nid, row, detail)
                old = recs.get(nid)
                if old is None:
                    stats["new"] += 1
                elif old.get("list_sig") != list_sig(row):
                    stats["changed"] += 1
                recs[nid] = merge(old, build_record(row, detail, towns), now)
                recs[nid]["detail_fetched_at"] = now
                stats["details_fetched"] += 1
                if i % 200 == 0:
                    log.info("details %d/%d", i, len(todo))
                    for r in recs.values():
                        r["classification"] = classify(r)
                    write_records(recs)
        except Blocked as e:
            blocked = str(e)
            log.error("stopped early: %s", e)
        stats.update({f"http_{k}": v for k, v in client.stats.items()})
        if not blocked:
            cov = state.get("coverage") or {}
            frm = min(filter(None, [cov.get("from"), since.isoformat()]))
            state["coverage"] = {"from": frm, "to": max(filter(None, [cov.get("to"), until.isoformat()]))}

    # classify, link, write
    for r in recs.values():
        r["classification"] = classify(r)
    records = sorted(recs.values(), key=lambda r: (r.get("received_date") or "", int(r["noi_id"])))
    links = resolve_links(records)
    for r in records:
        l = links.get(r["noi_id"])
        r["parent"] = canonical_parent(l["parent"]) if l and l.get("parent") else None
    write_records(recs)
    hits = build_hits(records, links)
    dates = [r["received_date"] for r in records if r.get("received_date")]
    cov = state.get("coverage") or {}
    write_json_atomic(HITS_FILE, {
        "generated": now,
        "source": SOURCE,
        "source_name": "MassDEP Wetlands Protection Act filings (EEA Data Portal, WIRe)",
        "window": {"start": cov.get("from") or (min(dates) if dates else None),
                   "end": cov.get("to") or (max(dates) if dates else None)},
        "states": ["MA"],
        "filings_total": len(records),
        "hits_count": len(hits),
        "notes": "meeting_date is the DEP filing date (the API has no hearing date); the Conservation "
                 "Commission must open its hearing within 21 days of filing (310 CMR 10.05(5)(b)). "
                 "Extra per-hit fields are under 'details'.",
        "hits": hits,
    })
    ent = build_entities(records, links, targets)
    write_json_atomic(ENTITIES_FILE, {
        "generated": now,
        "source": SOURCE,
        "scope": "energy and data-center related wetlands filings (same set as massdep_hits.json); "
                 "top_third_party_payors_all_filings covers every filing",
        "link_types": {
            "applicant_name": "applicant name contains a known developer's name",
            "care_of": "applicant listed 'c/o' a company",
            "payor": "fee check paid by a different company that is not an engineer, consultant or law firm",
            "self": "applicant is the known developer itself",
            "same_applicant_other_filing": "the same applicant (or a numbered sibling LLC such as 'X II, LLC') has a "
                                           "directly linked filing",
            "references_filing": "the description cites another DEP file number whose filing is linked",
            "shared_contact": "same applicant contact person (stored only as a hash) as a linked filing",
            "description_mention": "the project description names a known developer or utility (e.g. NEP, MECO)",
            "same_site": "same town and street address as a linked filing (weakest)",
        },
        **ent,
    })
    max_date = max(dates) if dates else None
    max_id = max((int(r["noi_id"]) for r in records), default=None)
    summary = summarize(records, hits, ent)
    state.update({
        "source": SOURCE,
        "api": LIST_URL,
        "cursor": {"max_filing_date": max_date, "max_noi_id": max_id},
        "lookback_days": LOOKBACK_DAYS,
        "last_run": {"at": now, "offline": bool(args.offline), "blocked": blocked, **dict(stats)},
        "summary": summary,
    })
    runs = (state.get("runs") or [])[-9:]
    runs.append({"at": now, "offline": bool(args.offline), "blocked": blocked,
                 "listed": stats.get("listed", 0), "new": stats.get("new", 0), "changed": stats.get("changed", 0),
                 "details_fetched": stats.get("details_fetched", 0), "hits": len(hits)})
    state["runs"] = runs
    write_json_atomic(STATE_FILE, state)
    return {"stats": dict(stats), "blocked": blocked, "summary": summary}


def summarize(records: list[dict], hits: list[dict], ent: dict) -> dict:
    energy = [r for r in records if r["classification"]["hit"]]
    cat = Counter(r["classification"]["category"] for r in records if r["classification"]["category"])
    return {
        "filings_total": len(records),
        "filings_by_type": dict(Counter(r.get("filing_type") or "unknown" for r in records).most_common()),
        "energy_hits": len(hits),
        "energy_by_category": dict(Counter(r["classification"]["category"] for r in energy).most_common()),
        "energy_by_topic": dict(Counter(t for r in energy for t in r["classification"]["energy_topics"]).most_common()),
        "energy_by_filing_type": dict(Counter(r.get("filing_type") or "unknown" for r in energy).most_common()),
        "energy_by_confidence": dict(Counter(r["classification"]["confidence"] for r in energy).most_common()),
        "energy_towns": len({r["town"] for r in energy}),
        "all_categories_incl_excluded": dict(cat.most_common()),
        "energy_with_parent": sum(1 for r in energy if r.get("parent")),
        "top_parents": [{"parent": p["parent"], "kind": p["kind"], "filings": p["filings"],
                         "sites": p["distinct_sites"], "towns": len(p["towns"])} for p in ent["parents"][:15]],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m watch351.sources.massdep",
                                 description="MassDEP wetlands filings -> data/sources/massdep_*.json")
    ap.add_argument("--since", help="re-list filings with filing date >= YYYY-MM-DD (default: cursor - "
                                    f"{LOOKBACK_DAYS} days, or 365 days back on the first run)")
    ap.add_argument("--until", help="last filing date to list (default: today)")
    ap.add_argument("--offline", action="store_true", help="no network: rebuild outputs from cache + jsonl")
    ap.add_argument("--max-details", type=int, default=0, help="cap detail requests this run (0 = no cap)")
    ap.add_argument("--refresh-pending", action="store_true",
                    help="also re-fetch details of listed filings that have no decision yet")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    res = run(args)
    print(json.dumps(res, indent=1))
    return 2 if res["blocked"] else 0


if __name__ == "__main__":
    sys.exit(main())
