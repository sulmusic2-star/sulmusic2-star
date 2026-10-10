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
    url = url.strip()
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
    if not r.ok:
        res["result"] = f"http_{r.status}"
        return res
    name_rx = re.compile(r"\b" + re.escape(town).replace(r"\ ", r"[\s\-]+") + r"\b", re.I)
    head = title + " " + soup.get_text(" ", strip=True)[:20000]
    res["name_match"] = bool(name_rx.search(head))
    res["result"] = "ok" if res["name_match"] else "ok_name_not_found"
    return res


GUESS_PATTERNS = ["https://www.{s}ma.gov", "https://{s}ma.gov", "https://www.{s}-ma.gov",
                  "https://www.townof{s}.org", "https://www.{s}.ma.us", "https://www.town.{s}.ma.us",
                  "https://www.cityof{s}.org", "https://www.{s}ma.org"]


def build_municipalities(fetcher: PoliteFetcher, workers: int = 16) -> dict:
    mcds, counties = census_rows(fetcher)
    directory = mma_directory(fetcher)
    wd = {}
    if WIKIDATA_FILE.exists():
        for row in json.loads(WIKIDATA_FILE.read_text())["rows"]:
            wd.setdefault((norm_name(row["itemLabel"]), row["countyLabel"].replace(" County", "")), row)

    def one(r: dict) -> dict:
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
        checks = [dict(check_site(fetcher, u, name), source=src) for src, u in cands]
        chosen = next((c for c in checks if c["result"] == "ok"), None)
        if chosen is None:
            chosen = next((c for c in checks if c["result"] in ("bot_challenge", "ok_name_not_found",
                                                                 "robots_disallow_homepage")), None)
        if chosen is None:
            slug = re.sub(r"[^a-z]", "", name.lower())
            for pat in GUESS_PATTERNS:
                u = pat.format(s=slug)
                c = dict(check_site(fetcher, u, name), source="guess")
                if c["result"] == "dns_fail":
                    continue
                checks.append(c)
                if c["result"] in ("ok", "bot_challenge"):
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

    with ThreadPoolExecutor(max_workers=workers) as pool:
        munis = list(pool.map(one, mcds))
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
