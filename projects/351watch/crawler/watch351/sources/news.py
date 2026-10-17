"""Regional news feeds -> which towns' siting fights are in the news.

Biggest stories ranks an agenda item higher when the town's fight over the same subject is in the news,
and the expansion list (tools/where_people_care.py) counts news about places we don't read yet. This
module reads the RSS feeds of regional newsrooms, keeps each article's headline, link, date and the
feed's short summary (never the article itself), and matches them to towns and subjects.

Politeness: the crawler's PoliteFetcher (AgendaAheadBot user agent, robots.txt on every host, one request
per second per host). A feed whose robots.txt disallows us is skipped, not worked around. Each feed is
read once a run; feeds carry only their latest items, so the archive (data/news/items.jsonl) builds up
day by day.

Matching. An article counts for a town when its headline or summary names the town and a siting subject
(data centers, battery storage, solar, wind, moratoriums, 40B housing, cell towers), and the state is
clear: the feed's home state is the town's, or the article names the town's state. Town names that are
also common words or people's names ("Washington", "Lincoln", "Clay") need the town's own context
("Town of Clay", "Clay Planning Board", "in Clay").

Usage (from projects/351watch/crawler):
    python3 -m watch351.sources.news            # read the feeds and two days of sitemaps, rewrite matches
    python3 -m watch351.sources.news --days 45  # fill the whole window from the sitemaps (first run)
    python3 -m watch351.sources.news --offline  # rewrite matches from the archive only

Outputs (data/news/):
    items.jsonl     one row per article that touches a subject: link, title, summary (<= 400 chars), published, source
    matches.json    {generated, window_days, towns: {"MA:Auburn": [article, ...]}, states: {"CT": {topic: n}}}
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from ..fetch import FetchError, PoliteFetcher

ROOT = Path(__file__).resolve().parents[3]          # projects/351watch
DATA = ROOT / "data"
OUT = DATA / "news"
WINDOW_DAYS = 45

# (name, feed URL, home states). Checked against robots.txt on every run by the fetcher.
FEEDS = [
    ("MassLive", "https://www.masslive.com/arc/outboundfeeds/rss-latest/?outputType=xml", ("MA",)),
    ("Boston Globe", "https://www.bostonglobe.com/arc/outboundfeeds/rss/?outputType=xml", ("MA",)),
    ("WBUR", "https://www.wbur.org/feed", ("MA",)),
    ("Western Mass News", "https://www.westernmassnews.com/arc/outboundfeeds/rss/?outputType=xml", ("MA",)),
    ("WWLP", "https://www.wwlp.com/feed/", ("MA",)),
    ("Boston 25 News", "https://www.boston25news.com/arc/outboundfeeds/rss/?outputType=xml", ("MA",)),
    ("Greenfield Recorder", "https://www.recorder.com/feed/", ("MA",)),
    ("Daily Hampshire Gazette", "https://www.gazettenet.com/feed/", ("MA",)),
    ("CommonWealth Beacon", "https://commonwealthbeacon.org/feed/", ("MA",)),
    ("New Bedford Light", "https://newbedfordlight.org/feed/", ("MA",)),
    ("Worcester Business Journal", "https://www.wbjournal.com/rss", ("MA",)),
    ("WAMC", "https://www.wamc.org/rss.xml", ("NY", "MA")),
    ("Syracuse.com", "https://www.syracuse.com/arc/outboundfeeds/rss-latest/?outputType=xml", ("NY",)),
    ("Spectrum News Central NY", "https://spectrumlocalnews.com/services/contentfeed.nys%7Ccentral-ny%7Cnews.landing.rss", ("NY",)),
    ("ecoRI News", "https://ecori.org/feed/", ("RI",)),
    ("Rhode Island Current", "https://rhodeislandcurrent.com/feed/", ("RI",)),
    ("CT Mirror", "https://ctmirror.org/feed/", ("CT",)),
    ("NHPR", "https://www.nhpr.org/rss.xml", ("NH",)),
]

# Day-by-day sitemaps (listed in each site's robots.txt): an article's address spells out its headline, so
# these fill in the days a feed's latest-items window has already dropped. (name, index URL, home states)
SITEMAPS = [
    ("MassLive", "https://www.masslive.com/arc/outboundfeeds/sitemap-index-by-day/", ("MA",)),
    ("Boston Globe", "https://www.bostonglobe.com/arc/outboundfeeds/sitemap-index-by-day/?outputType=xml", ("MA",)),
    ("Syracuse.com", "https://www.syracuse.com/arc/outboundfeeds/sitemap-index-by-day/", ("NY",)),
]

TOPICS = {
    "data_center": r"data[\s-]?cent(?:er|re)s?|hyperscale",
    "battery_storage": r"battery(?:[\s-]energy)?[\s-]storage|\bBESS\b|lithium[\s-]ion\s+batter",
    "solar": r"\bsolar\s+(?:farm|array|field|project|panels?|installation|facility|development|canopy|bylaw|ordinance)s?\b|\bsolar\b",
    "wind": r"\bwind\s+(?:turbines?|farm|project|energy)\b|offshore\s+wind",
    "moratorium": r"\bmoratori(?:um|ums|a)\b",
    "40b_comprehensive_permit": r"\b40B\b|comprehensive\s+permit",
    "wireless_telecom": r"cell(?:ular)?\s+towers?|\bmonopole\b|wireless\s+facilit",
}
TOPIC_RE = {k: re.compile(v, re.I) for k, v in TOPICS.items()}
# A solar or wind mention needs a siting word too, so "solar eclipse" and "wind chill" don't count.
SITING = re.compile(r"\b(?:zoning|bylaw|ordinance|permit|planning\s+board|select\s*board|town\s+meeting|council|"
                    r"hearing|vote|voters|proposal|proposed|project|residents|neighbors|abutters|moratorium|ban|"
                    r"conservation\s+commission|zba|appeals|lawsuit|acres|megawatt|MW)\b", re.I)

STATE_WORDS = {
    "MA": r"Massachusetts|\bMass\.|\bMA\b",
    "NY": r"New\s+York|\bN\.Y\.|\bNY\b|Upstate",
    "RI": r"Rhode\s+Island|\bR\.I\.|\bRI\b",
    "CT": r"Connecticut|\bConn\.|\bCT\b",
    "NH": r"New\s+Hampshire|\bN\.H\.|\bNH\b",
    "VT": r"Vermont|\bVt\.|\bVT\b",
}
STATE_RE = {k: re.compile(v) for k, v in STATE_WORDS.items()}
# Town names that are also common words, people's or other places' names: they need the town's own context.
COMMON = {
    # common words, people's names and places elsewhere
    "Washington", "Lincoln", "Clay", "Franklin", "Warren", "Union", "Hudson", "Clinton", "Monroe", "Orange",
    "Florida", "Holland", "Wales", "Berlin", "Lee", "Ware", "Salem", "Concord", "Athens", "Peru", "Mexico",
    "Paris", "Lima", "Victor", "Greece", "Sharon", "Douglas", "Adams", "Hancock", "Hamilton", "Jackson",
    "Madison", "Milton", "Newton", "Webster", "Lowell", "Everett", "Chester", "Dover", "Carlisle", "Princeton",
    "Burlington", "Cambridge", "Lexington", "Manchester", "Newport", "Bristol", "Plymouth", "Harvard",
    "Shirley", "Avon", "Richmond", "Sterling", "Oxford", "Hull", "Dennis", "Russell", "Montgomery",
    "Wellington", "Gill", "Otis", "Savoy", "Windsor", "Cheshire", "Norfolk", "Mansfield", "Easton", "Norton",
    "Palmer", "Granby", "Hampden", "Holden", "Sutton", "Dalton", "Becket", "Pompey", "Van Buren", "DeWitt",
    "Cicero", "Lysander", "Camillus", "Marcellus", "Tully", "Fabius", "LaFayette", "Charlestown",
    # the newsrooms' own cities, named in stories about everything
    "Boston", "Worcester", "Springfield", "Providence", "Syracuse", "Albany", "Hartford",
}
CONTEXT = r"(?:Town\s+of|City\s+of|in|of|for|near)\s+{n}\b|\b{n}(?:'s|’s)?\s+(?:Select\s*board|Planning|Zoning|Town|City|Conservation|Board|Council|residents|voters|officials|selectmen|selectboard|ZBA|Annual|Special)"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def text_of(el, *names) -> str:
    for n in names:
        found = el.find(n)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
    return ""


def plain(s: str) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def parse_feed(body: str, source: str) -> list[dict]:
    """RSS 2.0 or Atom items as {link, title, summary, published, source}."""
    body = re.sub(r"^﻿", "", body)
    try:
        root = ET.fromstring(body.encode("utf-8", "replace"))
    except ET.ParseError:
        return []
    out = []
    atom = "{http://www.w3.org/2005/Atom}"
    items = root.iter("item") if root.find(".//item") is not None else root.iter(f"{atom}entry")
    for it in items:
        title = plain(text_of(it, "title", f"{atom}title"))
        link = text_of(it, "link", "guid")
        if not link:
            le = it.find(f"{atom}link")
            link = le.get("href", "") if le is not None else ""
        summary = plain(text_of(it, "description", f"{atom}summary", f"{atom}content"))[:400]
        when = text_of(it, "pubDate", f"{atom}published", f"{atom}updated",
                       "{http://purl.org/dc/elements/1.1/}date")
        published = ""
        if when:
            try:
                published = parsedate_to_datetime(when).astimezone(timezone.utc).isoformat(timespec="seconds")
            except (TypeError, ValueError):
                try:
                    published = datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat(timespec="seconds")
                except ValueError:
                    published = ""
        if title and link.startswith("http"):
            out.append({"link": link.strip(), "title": title, "summary": summary, "published": published, "source": source})
    return out


def keep(r: dict) -> bool:
    """Only articles that touch a subject are kept (the rest of the news has no use here)."""
    return bool(topics_in(f"{r['title']} {r.get('summary') or ''} {SITING_HINT}"))


def load_items() -> dict[str, dict]:
    items = {}
    path = OUT / "items.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                items[r["link"]] = r
    return items


def read_feeds(fetcher: PoliteFetcher, items: dict[str, dict]) -> dict:
    """Append new articles to items.jsonl; returns a per-feed report."""
    report = {}
    new_rows = []
    for name, url, states in FEEDS:
        try:
            with fetcher.purpose("news"):
                resp = fetcher.get(url, max_age=3600)
        except FetchError as ex:  # robots.txt says no, or the feed is down: skip it today
            report[name] = f"skipped ({type(ex).__name__})"
            continue
        if not resp.ok:
            report[name] = f"HTTP {resp.status}"
            continue
        got = parse_feed(resp.text, name)
        fresh = [r for r in got if r["link"] not in items and keep(r)]
        for r in fresh:
            r["states"] = list(states)
            r["fetched_at"] = now_iso()
            items[r["link"]] = r
            new_rows.append(r)
        report[name] = f"{len(got)} items, {len(fresh)} new"
    if new_rows:
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "items.jsonl", "a", encoding="utf-8") as f:
            for r in new_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return report


def slug_title(url: str) -> str:
    """"westfield-planning-board-denies-...-project.html" -> "Westfield planning board denies ... project"."""
    seg = [x for x in url.split("?")[0].split("/") if x][-1]
    seg = re.sub(r"\.html?$", "", seg)
    seg = re.sub(r"(?:-|_)[A-Z0-9]{20,}$|-\d{6,}$", "", seg)
    words = seg.replace("_", "-").split("-")
    return (" ".join(w for w in words if w)).capitalize() if len(words) >= 4 else ""


def read_sitemaps(fetcher: PoliteFetcher, items: dict[str, dict], days: int) -> dict:
    """Articles from the last `days` days of each site's day-by-day sitemaps (a day already read is cached)."""
    report = {}
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    new_rows = []
    for name, index_url, states in SITEMAPS:
        try:
            with fetcher.purpose("news"):
                idx = fetcher.get(index_url, max_age=3600)
        except FetchError as ex:
            report[name + " sitemaps"] = f"skipped ({type(ex).__name__})"
            continue
        locs = re.findall(r"<loc>([^<]+)</loc>", idx.text if idx.ok else "")
        wanted = [u for u in locs if (m := re.search(r"(\d{4}-\d{2}-\d{2})", u)) and m.group(1) >= since]
        wanted += [u for u in locs if "latest" in u]
        n_new = 0
        for u in wanted:
            past_day = "latest" not in u
            try:
                with fetcher.purpose("news"):
                    resp = fetcher.get(html.unescape(u), max_age=None if past_day else 3600)
            except FetchError:
                continue
            if not resp.ok:
                continue
            for loc, lastmod in re.findall(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", resp.text):
                loc = html.unescape(loc)
                if loc in items:
                    continue
                title = slug_title(loc)
                if not title or not keep({"title": title}):
                    continue
                r = {"link": loc, "title": title, "summary": "", "published": lastmod[:19] + "+00:00" if lastmod else "",
                     "source": name, "states": list(states), "fetched_at": now_iso(), "from": "sitemap"}
                items[loc] = r
                new_rows.append(r)
                n_new += 1
        report[name + " sitemaps"] = f"{len(wanted)} days, {n_new} new"
    if new_rows:
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "items.jsonl", "a", encoding="utf-8") as f:
            for r in new_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return report


def read_descriptions(fetcher: PoliteFetcher, items: dict[str, dict], limit: int = 120) -> str:
    """An article that names a subject but whose headline is all we hold (a sitemap row): read the page's own
    title and short description (its og: tags), which usually name the town. Robots-checked, one page each."""
    todo = [r for r in items.values() if r.get("from") == "sitemap" and not r.get("summary") and not r.get("described")
            and topics_in(r["title"] + " " + SITING_HINT)]
    done = 0
    for r in todo[:limit]:
        r["described"] = True
        try:
            with fetcher.purpose("news"):
                resp = fetcher.get(r["link"], max_age=None)
        except FetchError:
            continue
        if not resp.ok:
            continue
        head = resp.text[:200000]
        t = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', head)
        d = re.search(r'<meta[^>]+(?:property=["\']og:description["\']|name=["\']description["\'])[^>]+content=["\']([^"\']+)', head)
        if t:
            r["title"] = plain(t.group(1))
        if d:
            r["summary"] = plain(d.group(1))[:400]
        done += 1
    if done:  # rewrite the archive with the new titles and descriptions
        tmp = OUT / "items.jsonl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in items.values():
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        tmp.replace(OUT / "items.jsonl")
    return f"{done} of {len(todo)} described"


# a subject word alone in a headline is enough to read the article's description
SITING_HINT = "zoning"


def load_towns() -> list[dict]:
    rows = []
    for path in sorted(DATA.glob("towns_*.json")):
        doc = json.loads(path.read_text())
        for t in (doc.get("towns", []) if isinstance(doc, dict) else doc):
            if isinstance(t, dict) and t.get("town"):
                rows.append({"state": (t.get("state") or "MA").upper(), "town": t["town"]})
    return rows


def topics_in(text: str) -> list[str]:
    found = [k for k, rx in TOPIC_RE.items() if rx.search(text)]
    if any(k in found for k in ("solar", "wind")) and not SITING.search(text):
        found = [k for k in found if k not in ("solar", "wind")]
    return found


def town_matcher(towns: list[dict]):
    """name -> compiled pattern; names shared by two states or in COMMON need the town's own context."""
    by_name: dict[str, list[str]] = {}
    for t in towns:
        by_name.setdefault(t["town"], []).append(t["state"])
    pats = {}
    for name, states in by_name.items():
        n = re.escape(name)
        # a name two states share is settled by the newsroom's home state (or the state the article names)
        strict = name in COMMON or len(name) <= 4
        pats[name] = (re.compile(CONTEXT.format(n=n), re.I) if strict else re.compile(rf"\b{n}\b", re.I), sorted(set(states)))
    return pats


def match(items: dict[str, dict], towns: list[dict], today: datetime) -> dict:
    since = today - timedelta(days=WINDOW_DAYS)
    pats = town_matcher(towns)
    by_town: dict[str, list[dict]] = {}
    by_state: dict[str, dict[str, int]] = {}
    for r in items.values():
        when = r.get("published") or r.get("fetched_at") or ""
        try:
            if datetime.fromisoformat(when) < since:
                continue
        except ValueError:
            continue
        text = f"{r['title']}. {r.get('summary') or ''}"
        topics = topics_in(text)
        if not topics:
            continue
        home = set(r.get("states") or [])
        named = {st for st, rx in STATE_RE.items() if rx.search(text)}
        for st in (named or home):
            for t in topics:
                by_state.setdefault(st, {}).setdefault(t, 0)
                by_state[st][t] += 1
        for name, (rx, states) in pats.items():
            if not rx.search(text):
                continue
            for st in states:
                # the state must be clear: the feed's home state, or named in the article
                if st not in home and st not in named:
                    continue
                if named and st not in named and len(states) > 1:
                    continue
                title = r["title"]
                if r.get("from") == "sitemap":  # a headline rebuilt from the address is lower case: capitalize the town
                    title = re.sub(rf"\b{re.escape(name)}\b", name, title, flags=re.I)
                by_town.setdefault(f"{st}:{name}", []).append({
                    "title": title, "link": r["link"], "source": r["source"],
                    "published": r.get("published") or r.get("fetched_at"), "topics": topics})
    for k in by_town:
        by_town[k].sort(key=lambda a: a["published"] or "", reverse=True)
    return {"generated": now_iso(), "window_days": WINDOW_DAYS, "towns": by_town, "states": by_state}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--offline", action="store_true", help="match from the archive only; read no feeds")
    p.add_argument("--cache-dir", default=str(ROOT / "crawler" / ".cache" / "news"))
    p.add_argument("--days", type=int, default=2, help="days of sitemaps to read (45 fills the whole window)")
    a = p.parse_args(argv)
    items = {k: r for k, r in load_items().items() if keep(r)}
    report = {}
    if not a.offline:
        fetcher = PoliteFetcher(Path(a.cache_dir))
        report = read_feeds(fetcher, items)
        report.update(read_sitemaps(fetcher, items, a.days))
        report["article descriptions"] = read_descriptions(fetcher, items)
    tmp_items = OUT / "items.jsonl.tmp"
    OUT.mkdir(parents=True, exist_ok=True)
    with open(tmp_items, "w", encoding="utf-8") as f:
        for r in sorted(items.values(), key=lambda r: r.get("published") or ""):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp_items.replace(OUT / "items.jsonl")
    result = match(items, load_towns(), datetime.now(timezone.utc))
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "matches.json.tmp"
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(OUT / "matches.json")
    for name, line in report.items():
        sys.stderr.write(f"news: {name}: {line}\n")
    n = sum(len(v) for v in result["towns"].values())
    sys.stderr.write(f"news: {len(items)} articles held; {n} town matches in {len(result['towns'])} towns "
                     f"over the last {WINDOW_DAYS} days\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
