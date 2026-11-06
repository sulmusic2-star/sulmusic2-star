"""Maryland PSC Certificate of Public Convenience and Necessity (CPCN) cases -> Agenda Ahead items (gated).

Every generating station over 2 MW (solar farms, battery storage, gas plants) and every high-voltage
transmission line in Maryland needs a CPCN from the Public Service Commission; the county is consulted and
the Commission holds a public comment hearing in the county. Three pages on psc.maryland.gov carry what we
need (robots.txt: allow all, Crawl-delay 10, which the fetcher honours):

  * the CPCN case list, by year: case number, applicant, size, county, and withdrawals
    https://psc.maryland.gov/online-services/file-a-public-comment/energy-generation-and-transmission-siting-cpcn-cases/
  * the upcoming public comment hearings: case, date and time, place, written-comment deadline
    https://psc.maryland.gov/news-events/upcoming-public-comment-hearings/
  * the proceedings dashboard: filing date and stage of each CPCN case
    https://psc.maryland.gov/proceedings-dashboard/

The case files themselves (webpsc.psc.state.md.us, "DMS") sit behind a Cloudflare challenge and are not read.

Item: case number, applicant, description, MW, county, year listed, filing date and stage (dashboard),
hearing date, time and place, comment deadline, withdrawal or decision note, topics.

Hit (source_kind "state_docket"): one per case with an event in the window, filed under the county row
("Caroline County"), board "Maryland Public Service Commission", meeting_date = hearing date (date_kind
hearing), else a withdrawal or decision date in the window (decision), else null for a case filed in the
window (filed).

    cd projects/351watch/crawler
    python3 -m watch351.sources.md_psc_cpcn --days 30
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from ..fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from .notice_feeds import (DEFAULT_OUT, check_out_dir, counties_named, county_named, county_rows, iso, load_ledger,
                           make_hit, network_report, norm, notice_topics, parse_date, snippet_of, window_start, write_outputs)
from .state_feeds import clean, first_seen, now_iso

log = logging.getLogger("md_psc_cpcn")

SOURCE = "md_psc_cpcn"
SOURCE_KIND = "state_docket"
STATE = "MD"
BOARD = "Maryland Public Service Commission"
LIST_URL = "https://psc.maryland.gov/online-services/file-a-public-comment/energy-generation-and-transmission-siting-cpcn-cases/"
HEARINGS_URL = "https://psc.maryland.gov/news-events/upcoming-public-comment-hearings/"
DASHBOARD_URL = "https://psc.maryland.gov/proceedings-dashboard/"
PAGE_MAX_AGE = 20 * 3600
YEARS_BACK = 2
_CASE = re.compile(r"Case\.?\s*(?:No\.?)?\s*(\d{4})\s*[–—-]+\s*", re.I)
_MW = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*[-\s]?\s*(?:megawatts?|MW)\b", re.I)
_NOTE = re.compile(r"(Application\s+withdrawn|Withdrawn|Dismissed|Denied|Granted|Approved|Final\s+Order|Order\s+No\.?\s*\d+)"
                   r"\s*:?\s*([^\n]{0,80})", re.I)


def _main_text(html: str):
    soup = BeautifulSoup(html, "lxml")
    main = soup.find("main") or soup.find("article") or soup
    for t in main(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    return main


def parse_list(html: str) -> list[dict]:
    """Cases by year from the CPCN list page."""
    main = _main_text(html)
    out = []
    year = None
    for el in main.find_all(["h2", "h3", "p", "li", "div"]):
        if el.name in ("h2", "h3") and re.fullmatch(r"20\d\d", clean(el.get_text(" "))):
            year = int(clean(el.get_text(" ")))
            continue
        if el.name in ("h2", "h3") or not year:
            continue
        if el.find(["p", "li", "div", "h2", "h3"]):
            continue        # a container; its children come on their own
        text = clean(el.get_text(" "))
        if not _CASE.search(text):
            continue
        parts = _CASE.split(text)
        # parts: [lead, case1, body1, case2, body2 ...]
        for k in range(1, len(parts) - 1, 2):
            case_no, body = parts[k], clean(parts[k + 1])
            if not body:
                continue
            note = None
            nm = _NOTE.search(body)
            if nm:
                note = clean(nm.group(0))
                body = clean(body[:nm.start()])
            counties = counties_named(body)
            county = counties[0] if counties else None
            mw = None
            mm = _MW.search(body)
            if mm:
                try:
                    mw = float(mm.group(1).replace(",", ""))
                except ValueError:
                    pass
            applicant = re.split(r"\s+\d[\d,.]*\s*[-\s]?\s*MW\b|\s+\(", body, maxsplit=1)[0].strip(" –-")
            out.append({"case_number": case_no, "year": year, "applicant": applicant, "description": body,
                        "county": county, "counties": counties, "mw": mw, "note": note})
    return out


def parse_hearings(html: str) -> list[dict]:
    """Public comment hearings: case number, title, hearing date, time, place, comment deadline, virtual."""
    main = _main_text(html)
    out = []
    for h3 in main.find_all("h3"):
        title = clean(h3.get_text(" "))
        cm = re.search(r"\b(\d{4})\b", title)
        if not cm:
            continue
        content = h3.find_next_sibling("div")
        lines = [clean(x) for x in (content.get_text("\n") if content else "").split("\n") if clean(x)]
        hearing_date, hearing_time, place, deadline, virtual = None, None, None, None, False
        for i, ln in enumerate(lines):
            low = ln.lower()
            if ("hearing" in low or "date and time" in low) and parse_date(ln) and not hearing_date:
                hearing_date = parse_date(ln)
                tm = re.search(r"\b(\d{1,2}(?::\d{2})?\s*[ap]\.?m\.?)", ln, re.I)
                hearing_time = clean(tm.group(1)) if tm else None
                virtual = "virtual" in low
            elif ("hearing" in low or "date and time" in low) and not hearing_date and i + 1 < len(lines) and parse_date(lines[i + 1]):
                hearing_date = parse_date(lines[i + 1])
                tm = re.search(r"\b(\d{1,2}(?::\d{2})?\s*[ap]\.?m\.?)", lines[i + 1], re.I)
                hearing_time = clean(tm.group(1)) if tm else None
                virtual = "virtual" in low
            if low.startswith("location"):
                place = clean(ln.split(":", 1)[1]) if ":" in ln and clean(ln.split(":", 1)[1]) else (lines[i + 1] if i + 1 < len(lines) else None)
                place = clean((place or "").lstrip(": ")) or None
            if "deadline" in low or "written comments due" in low:
                deadline = parse_date(ln) or (parse_date(lines[i + 1]) if i + 1 < len(lines) else None)
        if "virtual" in title.lower() or any("virtual" in ln.lower() for ln in lines[:4]):
            virtual = virtual or any("virtual" in ln.lower() and "hearing" in ln.lower() for ln in lines)
        out.append({"case_number": cm.group(1), "title": title, "hearing_date": iso(hearing_date), "hearing_time": hearing_time,
                    "place": place, "comment_deadline": iso(deadline), "virtual": virtual,
                    "county": county_named(title), "cpcn": "cpcn" in title.lower()})
    return out


def parse_dashboard(html: str) -> dict[str, dict]:
    """case number -> {filed_by, filed, stage} for the CPCN table of the proceedings dashboard."""
    main = _main_text(html)
    out = {}
    text_rows = []
    for tr in main.find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in tr.find_all(["td", "th"])]
        if len(cells) >= 4:
            text_rows.append(cells)
    section = None
    for cells in text_rows:
        if cells[0].lower().startswith("rate case") or cells[0].lower().startswith("cpcn"):
            section = cells[0]
            continue
        cm = re.search(r"\b(\d{4})\b", cells[0])
        if cm and parse_date(cells[2]):
            out[cm.group(1)] = {"filed_by": cells[1], "filed": iso(parse_date(cells[2])), "stage": cells[3], "table": section}
    return out


def run(fetcher: PoliteFetcher, out_dir: Path, days: int = 30, data_dir: Path | None = None,
        today: date | None = None) -> dict:
    check_out_dir(out_dir)
    started = now_iso()
    today = today or date.today()
    since = window_start(days, today)
    counties = county_rows(STATE, data_dir) if data_dir else county_rows(STATE)
    ledger = load_ledger(out_dir, SOURCE)
    errors: list[str] = []
    pages = {}
    for key, url in (("list", LIST_URL), ("hearings", HEARINGS_URL), ("dashboard", DASHBOARD_URL)):
        try:
            with fetcher.purpose("listing"):
                r = fetcher.get(url, max_age=PAGE_MAX_AGE)
            if not r.ok:
                raise FetchError(f"HTTP {r.status}")
            pages[key] = r.text
        except FetchError as e:
            errors.append(f"{key}: {e}"[:200])
    if "list" not in pages:
        raise FetchError("CPCN list page unreadable: " + "; ".join(errors))
    cases = {c["case_number"]: c for c in parse_list(pages["list"]) if c["year"] >= today.year - YEARS_BACK}
    hearings = parse_hearings(pages.get("hearings", "")) if "hearings" in pages else []
    dashboard = parse_dashboard(pages.get("dashboard", "")) if "dashboard" in pages else {}
    for h in hearings:
        c = cases.get(h["case_number"])
        if c is None and h["cpcn"]:
            c = cases[h["case_number"]] = {"case_number": h["case_number"], "year": None,
                                           "applicant": re.split(r"[’']s\b", h["title"].split("-", 1)[-1], maxsplit=1)[0].strip(),
                                           "description": h["title"].split("-", 1)[-1].strip(), "county": h["county"],
                                           "counties": [h["county"]] if h["county"] else [], "mw": None, "note": None}
        if c is not None:
            c.setdefault("hearings", []).append(h)
            if not c.get("county") and h.get("county"):
                c["county"], c["counties"] = h["county"], [h["county"]]
    # CPCN cases the dashboard tracks but the list page has not caught up with (filed this year)
    for no, d in dashboard.items():
        if (d.get("table") or "").lower().startswith("cpcn") and no not in cases and d.get("filed") \
                and date.fromisoformat(d["filed"]).year >= today.year - YEARS_BACK:
            cases[no] = {"case_number": no, "year": date.fromisoformat(d["filed"]).year, "applicant": d["filed_by"],
                         "description": d["filed_by"], "county": None, "counties": [], "mw": None, "note": None}
    items = []
    for no, c in cases.items():
        dash = dashboard.get(no, {})
        text = f"{c['applicant']} {c['description']}"
        topics = notice_topics(text, STATE) or ["clean_energy_siting"]
        note_date = parse_date(c["note"]) if c.get("note") else None
        items.append({**c, "hearings": c.get("hearings", []), "filed": dash.get("filed"), "stage": dash.get("stage"),
                      "filed_by": dash.get("filed_by"), "topics": topics, "note_date": iso(note_date),
                      "link": LIST_URL + f"#case-{no}", "first_seen": first_seen(ledger, no, started),
                      "siting_relevant": True})
    hits = [h for i in items for h in to_hits(i, since, counties)]
    report = {
        "source": SOURCE, "started": started, "finished": now_iso(), "since": since.isoformat(),
        "cases": len(items), "hearings_listed": len(hearings), "hearings_cpcn": sum(1 for h in hearings if h["cpcn"]),
        "dashboard_rows": len(dashboard), "hits": len(hits),
        "topics": dict(Counter(t for i in items for t in i["topics"]).most_common()),
        "counties_unresolved": sorted({i["county"] for i in items if i.get("county") and norm(i["county"]) not in counties}),
        "errors": errors, "network": network_report(fetcher),
    }
    write_outputs(SOURCE, out_dir, items, hits, LIST_URL, report, ledger)
    return report


def to_hits(item: dict, since: date, counties: dict[str, dict]) -> list[dict]:
    upcoming = sorted((h for h in item["hearings"] if h["hearing_date"] and date.fromisoformat(h["hearing_date"]) >= since),
                      key=lambda h: h["hearing_date"])
    place, deadline = None, None
    if upcoming:
        h = upcoming[0]
        when, date_kind = date.fromisoformat(h["hearing_date"]), "hearing"
        place = ("Virtual hearing" if h["virtual"] and not h["place"] else h["place"])
        deadline = date.fromisoformat(h["comment_deadline"]) if h.get("comment_deadline") else None
        what = f"Public comment hearing {h['hearing_date']}" + (f" at {h['hearing_time']}" if h.get("hearing_time") else "") \
            + (f", {place}" if place else "") + (f". Written comments by {h['comment_deadline']}" if h.get("comment_deadline") else "") + "."
        source_url = HEARINGS_URL + f"#case-{item['case_number']}"
    elif item.get("note_date") and date.fromisoformat(item["note_date"]) >= since:
        when, date_kind = date.fromisoformat(item["note_date"]), "decision"
        what = f"{item['note']}."
        source_url = item["link"]
    elif item.get("filed") and date.fromisoformat(item["filed"]) >= since:
        when, date_kind = None, "filed"
        what = f"Filed {item['filed']}" + (f"; stage: {item['stage']}" if item.get("stage") else "") + "."
        source_url = DASHBOARD_URL + f"#case-{item['case_number']}"
    else:
        return []
    names = item.get("counties") or ([item["county"]] if item.get("county") else [])
    out = []
    for county in names:
        county_row = counties.get(norm(county))
        town = county_row["town"] if county_row else (f"{county} County" if county != "Baltimore City" else county)
        size = f"{item['mw']:g} MW. " if item.get("mw") else ""
        snippet = snippet_of(f"PSC Case {item['case_number']}: {item['description']}. {size}{what}")
        out.append(make_hit(source=SOURCE, source_kind=SOURCE_KIND, state=STATE, town=town, county=county, board=BOARD,
                            meeting_date=when, date_kind=date_kind, topics=item["topics"], snippet=snippet, source_url=source_url,
                            listing_url=LIST_URL, document_title=f"PSC CPCN case {item['case_number']}: {item['applicant']}",
                            first_seen=item["first_seen"], headline_text=f"Case No. {item['case_number']} – {item['description']}",
                            place=place, comment_deadline=deadline,
                            extra={"stage": item.get("stage"), "mw": item.get("mw"), "filed": item.get("filed"),
                                   "configured": county_row is not None, "counties": names}))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--offline", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    rep = run(PoliteFetcher(a.cache_dir, offline=a.offline), a.out_dir, a.days)
    print(f"MD PSC: {rep['cases']} cases, {rep['hearings_cpcn']} CPCN hearings listed, {rep['hits']} hits; "
          f"errors {len(rep['errors'])}; network {rep['network']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
