"""Massachusetts census: every one of the 351 cities and towns, not a sample.

Run from crawler/ (all network access goes through PoliteFetcher, so the
robots.txt / 1 req/s/host / 351WatchBot rules in fetch.py apply):

    python3 -m watch351.ma_census municipalities  # -> data/ma_municipalities.json
    python3 -m watch351.ma_census discover        # -> data/towns_ma_all.json
    python3 -m watch351.ma_census leadtime        # -> data/leadtime_ma_all.json
    python3 -m watch351.ma_census crawl           # -> data/agenda_hits_ma_all.json
    python3 -m watch351.ma_census report          # print the summary tables

Nothing here writes data/towns.json, data/sample_towns.json or
data/agenda_hits.json; the 30-town pilot files stay as they are.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import re
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from .fetch import FetchError, PoliteFetcher, RobotsDisallowed

log = logging.getLogger("watch351.ma_census")

CRAWLER = Path(__file__).resolve().parent.parent
DATA = CRAWLER.parent / "data"
MUNI_FILE = DATA / "ma_municipalities.json"
WIKIDATA_FILE = DATA / "ma_wikidata_snapshot.json"
TOWNS_ALL_FILE = DATA / "towns_ma_all.json"
LEADTIME_FILE = DATA / "leadtime_ma_all.json"
HITS_ALL_FILE = DATA / "agenda_hits_ma_all.json"
LEADTIME_RAW_FILE = DATA / "leadtime_rows_ma_all.json"
CENSUS_LOCAL = DATA / "ma_census_sub_est2024.csv"

CENSUS_CSV = ("https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/"
              "cities/totals/sub-est2024_25.csv")
MMA_SITEMAP = "https://www.mma.org/community-sitemap.xml"
MMA_DIRECTORY = "https://www.mma.org/all-directory-data/"

# Kept for reproducibility of data/ma_wikidata_snapshot.json (query.wikidata.org
# disallows /sparql in robots.txt, so the bot never calls it; the snapshot was
# taken once by hand and is used only to cross-check MMA's website field).
WIKIDATA_QUERY = """
SELECT ?item ?itemLabel ?countyLabel ?art
  (GROUP_CONCAT(DISTINCT STR(?website); separator="|") AS ?sites)
  (GROUP_CONCAT(DISTINCT STR(?type); separator="|") AS ?types) (SAMPLE(?fips) AS ?fips) WHERE {
  VALUES ?type { wd:Q2154459 wd:Q1093829 wd:Q15127012 }
  ?item wdt:P31 ?type ; wdt:P131 ?county .
  ?county wdt:P31 wd:Q13410485 .
  OPTIONAL { ?item wdt:P856 ?website }
  OPTIONAL { ?item wdt:P774 ?fips }
  OPTIONAL { ?art schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} GROUP BY ?item ?itemLabel ?countyLabel ?art
"""

CF_MARKERS = ("challenges.cloudflare.com", "Attention Required! | Cloudflare", "cf-chl",
              "Just a moment...", "cf_chl_opt", "/cdn-cgi/challenge-platform")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    tmp.replace(path)


def norm_name(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"\s+(town city|city|town)$", "", s.strip())
    return re.sub(r"[^a-z0-9]", "", s)


def is_challenge(status: int, text: str) -> bool:
    head = text[:20000]
    return status in (403, 503, 429) and any(m in head for m in CF_MARKERS)


# --------------------------------------------------------------------------
# 1. municipalities
# --------------------------------------------------------------------------

def census_rows(fetcher: PoliteFetcher) -> tuple[list[dict], dict[str, str]]:
    # www2.census.gov's robots.txt has a "User-agent: *" line that a strict
    # parser merges into a "Disallow: /" group, so the bot does not fetch it;
    # the CSV was downloaded once by hand and is read from data/.
    if CENSUS_LOCAL.exists():
        text = CENSUS_LOCAL.read_bytes().decode("latin-1")
    else:
        resp = fetcher.get(CENSUS_CSV)
        if not resp.ok:
            raise RuntimeError(f"Census CSV HTTP {resp.status}")
        text = resp.body.decode("latin-1")
    rows = list(csv.DictReader(io.StringIO(text)))
    counties = {r["COUNTY"]: r["NAME"].replace(" County", "") for r in rows if r["SUMLEV"] == "050"}
    mcds = [r for r in rows if r["SUMLEV"] == "061"]
    return mcds, counties


def mma_directory(fetcher: PoliteFetcher) -> dict[str, dict]:
    """MMA 'all directory data' table: governance + county for every community."""
    resp = fetcher.get(MMA_DIRECTORY, max_age=7 * 24 * 3600)
    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.find_all("table")[0]
    trs = table.find_all("tr")
    hdr = [c.get_text(" ", strip=True) for c in trs[1].find_all(["td", "th"])]
    out = {}
    for tr in trs[2:]:
        cells = tr.find_all(["td", "th"])
        if len(cells) != len(hdr):
            continue
        rec = {h: c.get_text(" ", strip=True) for h, c in zip(hdr, cells)}
        a = cells[0].find("a", href=True)
        rec["_mma_url"] = "https://www.mma.org" + a["href"] if a and a["href"].startswith("/") else (a["href"] if a else None)
        out[norm_name(rec["Community"])] = rec
    return out


def mma_community(fetcher: PoliteFetcher, url: str) -> dict:
    resp = fetcher.get(url, max_age=30 * 24 * 3600)
    if not resp.ok:
        return {"error": f"HTTP {resp.status}"}
    soup = BeautifulSoup(resp.text, "lxml")
    a = soup.select_one("a.comm-site-link[href]")
    title = soup.select_one("#comm-title-str")
    kind = soup.select_one("#cty-town-of")
    return {
        "name": title.get_text(" ", strip=True) if title else None,
        "style": kind.get_text(" ", strip=True) if kind else None,   # "Town of" / "City of"
        "website": a["href"].strip() if a else None,
    }


def normalize_site(url: str | None) -> str | None:
    if not url:
        return None
    url = re.sub(r"^(https?://)+(https?://)", r"\2", url.strip(), flags=re.I)  # "http://https://x"
    if not re.match(r"^https?://", url, re.I):
        url = "http://" + url
    parts = urlsplit(url)
    path = parts.path if parts.path not in ("", "/") else ""
    return f"{parts.scheme.lower()}://{parts.netloc.lower()}{path}".rstrip("/")


def dns_ok(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


def check_site(fetcher: PoliteFetcher, url: str, town: str) -> dict:
    """Does the domain resolve, answer, and look like this town's site?"""
    host = urlsplit(url).netloc
    res: dict = {"url": url, "dns": dns_ok(host)}
    if not res["dns"]:
        res["result"] = "dns_fail"
        return res
    try:
        r = fetcher.get(url + "/", max_age=24 * 3600)
    except RobotsDisallowed as e:
        res.update(result="robots_disallow_homepage", detail=str(e)[:200])
        return res
    except FetchError as e:
        res.update(result="unreachable", detail=str(e)[:200])
        return res
    text = r.text
    res.update(status=r.status, final_url=r.final_url)
    soup = BeautifulSoup(text[:400000], "lxml")
    title = " ".join((soup.title.get_text(" ", strip=True) if soup.title else "").split())
    res["title"] = title[:160]
    if is_challenge(r.status, text):
        res["result"] = "bot_challenge"
        return res
    if r.status in (401, 403, 429):
        res["result"] = "waf_block" if re.search(r"Access Denied|edgesuite|Request blocked|Forbidden",
                                                 text[:5000], re.I) else f"http_{r.status}"
        return res
    if not r.ok:
        res["result"] = f"http_{r.status}"
        return res
    name_rx = re.compile(r"\b" + re.escape(town).replace(r"\ ", r"[\s\-]+") + r"\b", re.I)
    body_text = soup.get_text(" ", strip=True)
    head = title + " " + body_text[:30000]
    res["name_match"] = bool(name_rx.search(head))
    res["ma_match"] = bool(re.search(r"Massachusetts|\bMA\b|\bMass\.?\b|, ?MA\s+0\d{4}", head))
    parked = (len(body_text) < 200 and re.search(r"location\.href|/lander|refresh", text[:3000], re.I)) or \
        re.search(r"domain (?:is )?for sale|buy this domain|parked free|hugedomains", head, re.I)
    tourism = re.search(r"\b(?:hotels?|lodging|vacation rentals?|things to do)\b", title, re.I)
    if parked:
        res["result"] = "parked_or_redirect_stub"
    elif tourism:
        res["result"] = "not_official_site"
    elif res["name_match"] and res["ma_match"]:
        res["result"] = "ok"
    elif res["name_match"]:
        res["result"] = "ok_name_only"
    else:
        res["result"] = "ok_name_not_found"
    return res


GUESS_PATTERNS = ["https://www.{s}ma.gov", "https://{s}ma.gov", "https://www.{s}-ma.gov",
                  "https://www.townof{s}.org", "https://www.{s}.ma.us", "https://www.town.{s}.ma.us",
                  "https://www.cityof{s}.org", "https://www.{s}ma.org"]


def load_sources(fetcher: PoliteFetcher):
    mcds, counties = census_rows(fetcher)
    directory = mma_directory(fetcher)
    wd = {}
    if WIKIDATA_FILE.exists():
        for row in json.loads(WIKIDATA_FILE.read_text())["rows"]:
            wd.setdefault((norm_name(row["itemLabel"]), row["countyLabel"].replace(" County", "")), row)
    return mcds, counties, directory, wd


def build_municipalities(fetcher: PoliteFetcher, workers: int = 16) -> dict:
    mcds, counties, directory, wd = load_sources(fetcher)
    one = lambda r: build_one(fetcher, r, counties, directory, wd)  # noqa: E731
    with ThreadPoolExecutor(max_workers=workers) as pool:
        munis = list(pool.map(one, mcds))
    return package_munis(munis)


def build_one(fetcher: PoliteFetcher, r: dict, counties: dict, directory: dict, wd: dict) -> dict:
    raw = r["NAME"]
    name = re.sub(r"\s+(Town city|city|town)$", "", raw)
    kind = "city" if raw.endswith(" city") else "town"
    county = counties.get(r["COUNTY"], r["COUNTY"])
    key = norm_name(name)
    mrec = directory.get(key, {})
    mma = mma_community(fetcher, mrec["_mma_url"]) if mrec.get("_mma_url") else {}
    w = wd.get((key, county)) or {}
    cands = []
    for src, u in (("mma", mma.get("website")), ("wikidata", (w.get("sites") or "").split("|")[0] or None)):
        nu = normalize_site(u)
        if nu and nu not in [c[1] for c in cands]:
            cands.append((src, nu))
    checks = []
    for src, u in cands:
        # many directory entries are http://; some hosts (Revize on AWS ELB) answer 403 to
        # plain http but 200 over https, so try https first and fall back to the listed URL
        variants = [re.sub(r"^http://", "https://", u)] + ([u] if u.startswith("http://") else [])
        for v in variants:
            c = dict(check_site(fetcher, v, name), source=src)
            checks.append(c)
            if c["result"] in ("ok", "ok_name_only", "bot_challenge"):
                break
    chosen = next((c for c in checks if c["result"] == "ok"), None)
    if chosen is None:
        # the directory's site exists but refuses us (challenge / WAF / robots): that is the
        # answer for this town; do not go guessing other domains
        chosen = next((c for c in checks if c["result"] in ("bot_challenge", "waf_block", "http_403", "http_401",
                                                             "http_429", "robots_disallow_homepage",
                                                             "ok_name_only")), None)
    if chosen is None:
        chosen = next((c for c in checks if c["result"] == "ok_name_not_found" and c["source"] == "mma"), None)
    if chosen is None:
        slug = re.sub(r"[^a-z]", "", name.lower())
        for pat in GUESS_PATTERNS:
            u = pat.format(s=slug)
            c = dict(check_site(fetcher, u, name), source="guess")
            if c["result"] == "dns_fail":
                continue
            checks.append(c)
            if c["result"] == "ok":
                chosen = c
                break
    website = None
    if chosen:
        website = normalize_site(chosen.get("final_url") or chosen["url"])
        # keep the scheme+host only when the final URL is a deep link (e.g. /index.php)
        parts = urlsplit(website)
        if parts.path and not re.search(r"/(town|city|ma|government)?$", parts.path, re.I):
            website = f"{parts.scheme}://{parts.netloc}"
    return {
        "town": name,
        "kind": kind,
        "county": county,
        "census_cousub": f"25{r['COUNTY']}{r['COUSUB']}",
        "pop_2020": int(r["ESTIMATESBASE2020"]),
        "pop_2024_est": int(r["POPESTIMATE2024"]),
        "legislative_body": mrec.get("Legislative Body"),
        "form_of_government": mrec.get("Form of Government"),
        "website": website,
        "website_verified": bool(chosen and chosen["result"] == "ok"),
        "website_status": chosen["result"] if chosen else (checks[-1]["result"] if checks else "no_candidate"),
        "website_sources": {"mma": normalize_site(mma.get("website")),
                            "wikidata": normalize_site((w.get("sites") or "").split("|")[0] or None)},
        "website_checks": checks,
        "mma_page": mrec.get("_mma_url"),
        "wikidata": w.get("item"),
    }



def package_munis(munis: list[dict]) -> dict:
    munis.sort(key=lambda m: m["town"])
    return {
        "_about": ("All 351 Massachusetts cities and towns (Census county subdivisions, state FIPS 25) "
                   "with official website. Website = MMA municipal directory (mma.org/community/<slug>), "
                   "cross-checked against Wikidata P856, each fetched once by 351WatchBot to verify it "
                   "answers and names the town. Population: Census Vintage 2024 sub-county estimates "
                   "(2020 estimates base and July 1, 2024 estimate)."),
        "generated": now_iso(),
        "sources": {"census": CENSUS_CSV, "mma_directory": MMA_DIRECTORY, "mma_community": "https://www.mma.org/community/<slug>/",
                    "wikidata_snapshot": "data/ma_wikidata_snapshot.json"},
        "count": len(munis),
        "population_2024_est_total": sum(m["pop_2024_est"] for m in munis),
        "municipalities": munis,
    }


def cmd_municipalities(args, fetcher: PoliteFetcher) -> None:
    doc = build_municipalities(fetcher, workers=args.workers)
    save_json(MUNI_FILE, doc)
    from collections import Counter
    c = Counter(m["website_status"] for m in doc["municipalities"])
    print(f"{doc['count']} municipalities, population {doc['population_2024_est_total']:,}")
    print("website status:", dict(c))
    print(f"wrote {MUNI_FILE}")


# --------------------------------------------------------------------------
# 2. discovery over all municipalities
# --------------------------------------------------------------------------

def load_munis(names: str | None = None) -> list[dict]:
    munis = json.loads(MUNI_FILE.read_text())["municipalities"]
    if names:
        wanted = {n.strip().lower() for n in names.split(",")}
        munis = [m for m in munis if m["town"].lower() in wanted]
    return munis


def cmd_discover(args, fetcher: PoliteFetcher) -> None:
    from collections import Counter
    from .discover_census import discover_municipality
    munis = load_munis(args.towns)

    def one(m: dict) -> dict:
        try:
            return discover_municipality(fetcher, m)
        except Exception as e:  # noqa: BLE001 - one bad site must not stop the census
            log.exception("%s: discovery crashed", m["town"])
            return {"town": m["town"], "website": m.get("website"), "automated": False,
                    "status": "not_automated", "reason_code": "discovery_error",
                    "reason": f"discovery crashed: {type(e).__name__}: {str(e)[:160]}", "listings": [],
                    "pop_2024_est": m.get("pop_2024_est"), "pop_2020": m.get("pop_2020"),
                    "county": m.get("county"), "kind": m.get("kind"),
                    "legislative_body": m.get("legislative_body"), "_leadtime_rows": []}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        recs = list(pool.map(one, munis))
    # merge into an existing census file when running a subset
    existing = {}
    if args.towns and TOWNS_ALL_FILE.exists():
        existing = {t["town"]: t for t in json.loads(TOWNS_ALL_FILE.read_text())["towns"]}
    raw_rows = {}
    if args.towns and LEADTIME_RAW_FILE.exists():
        raw_rows = json.loads(LEADTIME_RAW_FILE.read_text())["rows_by_town"]
    for r in recs:
        raw_rows[r["town"]] = r.pop("_leadtime_rows", [])
        existing[r["town"]] = r
    towns = sorted(existing.values(), key=lambda t: t["town"])
    doc = {
        "_about": ("351 Watch census of all 351 Massachusetts municipalities: agenda platform, crawlable "
                   "listing per tracked board (with evidence: agendas dated within the last 120 / next 120 days), "
                   "or the precise reason a town is not automated. Same per-town schema as data/towns.json; "
                   "built by `python3 -m watch351.ma_census discover`."),
        "generated": now_iso(),
        "boards_tracked": ["planning_board", "zoning_board_of_appeals", "conservation_commission",
                           "select_board", "town_meeting"],
        "evidence_rule": ("board automated only if its listing shows >=1 agenda dated in [today-120d, today+120d]; "
                          "town automated if >=1 meeting board is (warrants alone do not count)"),
        "count": len(towns),
        "automated": sum(1 for t in towns if t.get("automated")),
        "towns": towns,
    }
    save_json(TOWNS_ALL_FILE, doc)
    save_json(LEADTIME_RAW_FILE, {"_about": "Raw agenda rows with platform posted/published timestamps, "
                                  "collected during census discovery (CivicPlus AgendaCenter search, CivicClerk API).",
                                  "generated": now_iso(), "rows_by_town": raw_rows})
    c = Counter(t.get("reason_code") or "automated" for t in towns)
    print(f"{doc['automated']}/{len(towns)} automated; {dict(c.most_common())}")
    for r in recs:
        print(f"{r['town']:<22} {str(r.get('platform')):<11} {'AUTO' if r.get('automated') else '----'} "
              f"{','.join(r.get('boards_found', [])):<80} {(r.get('reason') or '')[:110]}")


# --------------------------------------------------------------------------
# 3. lead time: agenda posted vs meeting date
# --------------------------------------------------------------------------

def _pct(xs: list[float], q: float) -> float | None:
    """Linear-interpolated percentile (q in 0..100)."""
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * q / 100
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 2)


def _dist(rows: list[dict], field: str = "lead_days") -> dict:
    xs = [r[field] for r in rows]
    if not xs:
        return {"n": 0}
    hours = [r["lead_hours_to_day_start"] for r in rows]
    return {
        "n": len(xs),
        "towns": len({r["town"] for r in rows}),
        "p10_days": _pct(xs, 10), "p25_days": _pct(xs, 25), "median_days": _pct(xs, 50),
        "p75_days": _pct(xs, 75), "p90_days": _pct(xs, 90),
        "p10_hours_before_meeting_day": _pct(hours, 10), "median_hours_before_meeting_day": _pct(hours, 50),
        "share_posted_after_meeting_day_start": round(sum(1 for h in hours if h <= 0) / len(xs), 3),
        "share_ge_48h_before_meeting_day": round(sum(1 for h in hours if h >= 48) / len(xs), 3),
        "share_ge_24h_before_meeting_day": round(sum(1 for h in hours if h >= 24) / len(xs), 3),
        "share_ge_7_days": round(sum(1 for x in xs if x >= 7) / len(xs), 3),
    }


def leadtime_records(raw: dict, start, end) -> list[dict]:
    from datetime import date as _date
    out = []
    seen = set()
    for town, rows in raw.items():
        for r in rows:
            if not r.get("posted") or not r.get("meeting_date"):
                continue
            md = _date.fromisoformat(r["meeting_date"])
            if not (start <= md <= end):
                continue
            key = (town, r["url"])
            if key in seen:
                continue
            seen.add(key)
            posted = datetime.fromisoformat(r["posted"])
            day_start = datetime(md.year, md.month, md.day)
            rec = {"town": town, "board_key": r["board_key"], "category": r["category"],
                   "platform": r["platform"], "posted_kind": r.get("posted_kind"),
                   "meeting_date": r["meeting_date"], "posted": r["posted"], "url": r["url"],
                   "lead_days": (md - posted.date()).days,
                   "lead_hours_to_day_start": round((day_start - posted).total_seconds() / 3600, 1)}
            if r.get("meeting_start"):
                ms = datetime.fromisoformat(r["meeting_start"][:19])
                rec["lead_hours_to_start"] = round((ms - posted).total_seconds() / 3600, 1)
            out.append(rec)
    return out


def cmd_leadtime(args, fetcher: PoliteFetcher) -> None:
    from collections import defaultdict
    from datetime import date as _date, timedelta
    raw = json.loads(LEADTIME_RAW_FILE.read_text())["rows_by_town"]
    today = _date.today()
    start, end = today - timedelta(days=args.lead_days_back), today - timedelta(days=1)
    recs = leadtime_records(raw, start, end)
    posted_only = [r for r in recs if r["posted_kind"] in ("posted", "published")]
    summary = {"all_rows": _dist(recs), "first_posting_only": _dist(posted_only)}
    by_board, by_board_posted, by_platform = {}, {}, {}
    for key in ["planning_board", "zoning_board_of_appeals", "conservation_commission", "select_board", "town_meeting"]:
        by_board[key] = _dist([r for r in recs if r["board_key"] == key])
        by_board_posted[key] = _dist([r for r in posted_only if r["board_key"] == key])
    for plat in sorted({r["platform"] for r in recs}):
        by_platform[plat] = _dist([r for r in recs if r["platform"] == plat])
    # town-level: each town's median, so big posters do not dominate
    per_town = defaultdict(list)
    for r in posted_only:
        per_town[r["town"]].append(r["lead_days"])
    town_medians = [_pct(v, 50) for v in per_town.values() if len(v) >= 3]
    exact = [r for r in recs if "lead_hours_to_start" in r]
    doc = {
        "_about": ("Lead time between when an agenda appeared on the town's agenda platform and the meeting date, "
                   "for meetings already held. CivicPlus AgendaCenter shows 'Posted <timestamp>' (or 'Amended "
                   "<timestamp>' after an edit, which replaces the original time, so amended rows understate lead "
                   "time); CivicClerk's public API gives publishOn per agenda file and the meeting start time."),
        "generated": now_iso(),
        "meeting_window": {"start": start.isoformat(), "end": end.isoformat()},
        "method": {
            "lead_days": "meeting date minus the calendar date the agenda was posted",
            "lead_hours_to_day_start": ("hours from posting to 00:00 on the meeting day (a lower bound: most "
                                        "meetings start in the evening, adding ~17-19 h)"),
            "lead_hours_to_start": "CivicClerk only: hours from publishOn to the scheduled start time",
            "first_posting_only": "CivicPlus rows marked 'Posted' (not 'Amended') plus all CivicClerk rows",
        },
        "summary": summary,
        "by_board_all_rows": by_board,
        "by_board_first_posting_only": by_board_posted,
        "by_platform": by_platform,
        "town_medians": {"towns": len(town_medians), "p10_days": _pct(town_medians, 10),
                         "median_days": _pct(town_medians, 50), "p90_days": _pct(town_medians, 90)},
        "civicclerk_exact_hours_to_start": {"n": len(exact),
                                            "p10": _pct([r["lead_hours_to_start"] for r in exact], 10),
                                            "median": _pct([r["lead_hours_to_start"] for r in exact], 50)},
        "records": recs,
    }
    save_json(LEADTIME_FILE, doc)
    print(json.dumps({k: doc[k] for k in ("meeting_window", "summary", "by_board_first_posting_only",
                                          "by_platform", "town_medians", "civicclerk_exact_hours_to_start")},
                     indent=1))
    print(f"wrote {LEADTIME_FILE}")


# --------------------------------------------------------------------------
# 4. crawl every automated town
# --------------------------------------------------------------------------

def _listing_platform(l: dict) -> str:
    if "category_id" in l:
        return "civicplus"
    if "civicclerk.com" in l.get("url", ""):
        return "civicclerk"
    return "generic"


def crawl_configs(towns: list[dict]) -> list[dict]:
    """One crawl config per (town, platform): crawl.py runs one adapter per config."""
    cfgs = []
    for t in towns:
        if not t.get("automated"):
            continue
        groups: dict[str, list] = {}
        for l in t.get("listings", []) + t.get("secondary_listings", []):
            groups.setdefault(_listing_platform(l), []).append(l)
        for plat, ls in groups.items():
            cfg = {"town": t["town"], "website": t.get("final_url") or t["website"], "platform": plat,
                   "automated": True, "listings": ls}
            if plat == "civicplus":
                parts = urlsplit(cfg["website"])
                cfg["website"] = f"{parts.scheme}://{parts.netloc}"
            if plat == "civicclerk":
                cfg["tenant"] = t.get("tenant") or (t.get("vendors", {}).get("civicclerk", {}).get("tenant"))
            cfgs.append(cfg)
    return cfgs


def cmd_crawl(args, fetcher: PoliteFetcher) -> None:
    from collections import Counter, defaultdict
    from . import extract
    from .crawl import run_crawl
    extract.OCR_MAX_PAGES = 6     # census crawl: OCR only the first 6 pages of a scan
    towns = json.loads(TOWNS_ALL_FILE.read_text())["towns"]
    if args.towns:
        wanted = {n.strip().lower() for n in args.towns.split(",")}
        towns = [t for t in towns if t["town"].lower() in wanted]
    cfgs = crawl_configs(towns)
    report = run_crawl(cfgs, fetcher, days_back=args.days_back, days_ahead=args.days_ahead,
                       workers=args.workers)
    # merge per-(town, platform) entries back into one row per town
    merged: dict[str, dict] = {}
    for row in report["towns"]:
        m = merged.setdefault(row["town"], {"town": row["town"], "platforms": [], "agendas_listed": 0,
                                            "documents_scanned": 0, "documents_without_text_layer": 0,
                                            "documents_ocr": 0, "hits": row["hits"], "errors": []})
        m["platforms"].append(row["platform"])
        for k in ("agendas_listed", "documents_scanned", "documents_without_text_layer", "documents_ocr"):
            m[k] += row[k]
        m["errors"].extend(row["errors"])
    for m in merged.values():
        m["errors"] = m["errors"][:10]
    hits = report["hits"]
    by_town_topic: dict[str, Counter] = defaultdict(Counter)
    for h in hits:
        for tp in h["topics"]:
            by_town_topic[h["town"]][tp] += 1
    report.update({
        "_about": ("Census crawl of every automated Massachusetts municipality (data/towns_ma_all.json): "
                   "agendas for meetings in the window, text-extracted (OCR limited to the first 6 pages of "
                   "image-only PDFs) and matched against the 351 Watch topic keywords."),
        "towns_attempted": len(merged),
        "towns_automated": len(merged),
        "crawl_configs": len(cfgs),
        "towns": sorted(merged.values(), key=lambda m: m["town"]),
        "hits_by_town": {t: {"total": sum(c.values()), **dict(c.most_common())}
                         for t, c in sorted(by_town_topic.items(), key=lambda kv: -sum(kv[1].values()))},
        "towns_with_hits": len(by_town_topic),
        "hits_by_board": dict(Counter(h["board_key"] for h in hits).most_common()),
        "hits_text_source": dict(Counter(h.get("text_source") for h in hits).most_common()),
    })
    report.pop("towns_by_platform", None)
    report["towns_by_platform"] = dict(Counter(c["platform"] for c in cfgs))
    save_json(HITS_ALL_FILE, report)
    print(f"towns {len(merged)}, configs {len(cfgs)}, documents scanned {report['documents_scanned']} "
          f"({report['documents_without_text_layer']} without text layer, {report['documents_ocr']} OCR), "
          f"hits {len(hits)} in {len(by_town_topic)} towns")
    for topic, n in report["hits_by_topic"].items():
        print(f"  {topic:<26} {n}")
    print(f"fetcher: {fetcher.stats}")
    print(f"wrote {HITS_ALL_FILE}")


# --------------------------------------------------------------------------
# 5. summary tables
# --------------------------------------------------------------------------

SUMMARY_FILE = DATA / "ma_census_summary.json"
MEETING_BOARDS = ["planning_board", "zoning_board_of_appeals", "conservation_commission", "select_board"]


def _pct_of(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "-"


def cmd_report(args, fetcher: PoliteFetcher) -> None:
    from collections import Counter, defaultdict
    munis = json.loads(MUNI_FILE.read_text())["municipalities"]
    towns = json.loads(TOWNS_ALL_FILE.read_text())["towns"]
    state_pop = sum(m["pop_2024_est"] for m in munis)
    pop = {m["town"]: m["pop_2024_est"] for m in munis}
    auto = [t for t in towns if t.get("automated")]
    out: dict = {"generated": now_iso(), "municipalities": len(munis), "state_pop_2024": state_pop}
    out["websites"] = dict(Counter(m["website_status"] for m in munis))
    out["automated"] = {"towns": len(auto), "share": round(len(auto) / len(munis), 3),
                        "pop": sum(pop[t["town"]] for t in auto),
                        "pop_share": round(sum(pop[t["town"]] for t in auto) / state_pop, 3)}
    # platforms: every platform a town's automated boards come from
    plat = defaultdict(list)
    for t in auto:
        for p_ in t.get("platforms") or [t.get("platform")]:
            plat[p_].append(t["town"])
    primary = Counter(t.get("platform") for t in auto)
    out["automated_by_primary_platform"] = dict(primary.most_common())
    out["automated_towns_using_platform"] = {k: len(v) for k, v in sorted(plat.items(), key=lambda kv: -len(kv[1]))}
    cms = Counter()
    for t in towns:
        for c in (t.get("cms") or ["(none detected)"] if t.get("final_url") else ["(site not read)"]):
            cms[c] += 1
    out["cms_all_towns"] = dict(cms.most_common())
    # boards
    boards = {}
    tm_towns = [t for t in towns if t.get("has_town_meeting")]
    for key in MEETING_BOARDS + ["town_meeting"]:
        have = [t for t in towns if t.get("automated") and key in (t.get("boards_found") or [])]
        if key == "town_meeting":
            have = [t for t in tm_towns if "town_meeting" in (t.get("board_evidence") or {})]
        denom = len(tm_towns) if key == "town_meeting" else len(munis)
        boards[key] = {"towns": len(have), "of": denom, "share": round(len(have) / denom, 3) if denom else None,
                       "pop": sum(pop[t["town"]] for t in have)}
    out["boards"] = boards
    four = [t for t in auto if all(k in (t.get("boards_found") or []) for k in MEETING_BOARDS)]
    out["all_four_meeting_boards"] = {"towns": len(four), "pop": sum(pop[t["town"]] for t in four)}
    # reasons
    reasons = defaultdict(list)
    for t in towns:
        if not t.get("automated"):
            reasons[t.get("reason_code") or "unknown"].append(t["town"])
    out["not_automated"] = {k: {"towns": len(v), "pop": sum(pop[x] for x in v), "examples": v[:12]}
                            for k, v in sorted(reasons.items(), key=lambda kv: -len(kv[1]))}
    vend = defaultdict(list)
    for t in towns:
        if not t.get("automated") and t.get("reason_code") in ("vendor_robots_disallow", "vendor_blocked",
                                                              "bot_challenge", "js_only", "no_adapter"):
            vend[f"{t.get('reason_code')}:{t.get('platform') or 'town site'}"].append(t["town"])
    out["not_automated_by_vendor"] = {k: {"towns": len(v), "examples": v[:12]} for k, v in
                                      sorted(vend.items(), key=lambda kv: -len(kv[1]))}
    vendors_seen = Counter(k for t in towns for k in (t.get("vendors") or {}))
    out["vendor_links_seen_all_towns"] = dict(vendors_seen.most_common())
    if LEADTIME_FILE.exists():
        lt = json.loads(LEADTIME_FILE.read_text())
        out["leadtime"] = {k: lt[k] for k in ("meeting_window", "summary", "by_board_first_posting_only",
                                              "by_board_all_rows", "by_platform", "town_medians",
                                              "civicclerk_exact_hours_to_start") if k in lt}
    if HITS_ALL_FILE.exists():
        h = json.loads(HITS_ALL_FILE.read_text())
        out["crawl"] = {k: h.get(k) for k in ("window", "towns_attempted", "documents_scanned",
                                              "documents_without_text_layer", "documents_ocr",
                                              "hits_by_topic", "towns_with_hits", "hits_by_board",
                                              "hits_text_source")}
        out["crawl"]["hits"] = len(h["hits"])
        out["crawl"]["agendas_listed"] = sum(t["agendas_listed"] for t in h["towns"])
        out["crawl"]["towns_with_errors"] = sum(1 for t in h["towns"] if t["errors"])
        out["crawl"]["top_towns"] = dict(list(h["hits_by_town"].items())[:25])
    save_json(SUMMARY_FILE, out)
    print(json.dumps(out, indent=1)[:20000])
    print(f"wrote {SUMMARY_FILE}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["municipalities", "discover", "leadtime", "crawl", "report"])
    p.add_argument("--towns", help="comma-separated subset")
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--days-back", type=int, default=30)
    p.add_argument("--days-ahead", type=int, default=60)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--lead-days-back", type=int, default=180, help="leadtime: meetings held in the last N days")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    fetcher = PoliteFetcher(offline=args.offline)
    handlers = {"municipalities": cmd_municipalities}
    for name in ("discover", "leadtime", "crawl", "report"):
        fn = globals().get(f"cmd_{name}")
        if fn:
            handlers[name] = fn
    if args.command not in handlers:
        p.error(f"{args.command} not implemented yet")
    handlers[args.command](args, fetcher)
    return 0


if __name__ == "__main__":
    sys.exit(main())
