"""Ohio Power Siting Board cases, from the PUCO Docketing Information System (DIS) -> Agenda Ahead items (gated).

The Board certifies every solar or wind farm of 50 MW or more (and smaller ones that ask), gas plants,
battery storage over 50 MW, transmission lines and substations (R.C. 4906). Its own site (opsb.ohio.gov)
answered 404 to every page on 2026-11-06; the public docket, https://dis.puc.state.oh.us, is where the
cases, their filings, the local public hearing entries and the decisions are.

What is read (plain GETs through watch351.fetch.PoliteFetcher; dis.puc.state.oh.us's robots.txt disallows
only a list of named AI crawlers, so everyone else is allowed):
  * the DIS home page, once per run, because the daily report pages need the ASP.NET session it starts
  * the five most recent Docketing Division daily activity reports (DailyReport.aspx?Link=0..4): every new
    case and every entry, order or filing of the day, with case number, title and summary
  * the open-case lists for the Board's purpose codes (Browse by industry EL > purpose > status OPEN):
    BGN generating station certificate, BGA its amendment, BTX transmission line certificate, BTA its
    amendment, BSB substation certificate
  * the case record (CaseRecord.aspx?CaseNo=yy-nnnn) of every case opened in the last 18 months or named in a
    daily report, for its title, status, dates and latest 15 docket entries; the printable docket card
    (link=PDC) when the 15 do not reach back to the window start

Not read: the search forms (they are posts), documents themselves, letters of notification and construction
notices (BLN, BNR: small line work, items only when a daily report names them).

Item: case number, title, purpose, status, opened date, county and townships named in the title or docket
entries, MW, topics, hearing entries (date, place) and decisions found in the docket, link.

Hit (source_kind "state_docket"): one per case with an event in the window, filed under the county row
("Madison County"; the Board's cases name the county) and again under each configured township the docket
names, board "Ohio Power Siting Board", meeting_date = the hearing date (date_kind hearing), else the
decision date, else null for a case filed in the window (date_kind filed).

    cd projects/351watch/crawler
    python3 -m watch351.sources.oh_opsb --days 30
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from bs4 import BeautifulSoup

from ..attribution import known_townships, resolve_known
from ..fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from .notice_feeds import (DEFAULT_OUT, check_out_dir, county_named, county_rows, iso, load_ledger, make_hit,
                           network_report, norm, notice_topics, parse_date, parse_dates, snippet_of, window_start,
                           write_outputs)
from .state_feeds import clean, first_seen, load_state_towns, now_iso

log = logging.getLogger("oh_opsb")

SOURCE = "oh_opsb"
SOURCE_KIND = "state_docket"
STATE = "OH"
BOARD = "Ohio Power Siting Board"
DIS = "https://dis.puc.state.oh.us/"
LISTING_URL = DIS + "CasesByIndustryPurposeStatus.aspx?indcode=EL"
PURPOSES = {"BGN": "application for a certificate (generating station)",
            "BGA": "amendment to a generating station certificate",
            "BTX": "application for a certificate (transmission line)",
            "BTA": "amendment to a transmission line certificate",
            "BSB": "application for a certificate (substation)",
            "BLN": "letter of notification", "BNR": "construction notice"}
HIT_PURPOSES = ("BGN", "BGA", "BTX", "BTA", "BSB")
RECENT_DAYS = 540            # cases opened this recently get their record read every run
LIST_MAX_AGE = 20 * 3600
RECORD_MAX_AGE = 20 * 3600
DAILY_REPORTS = 5
MAX_RECORDS_PER_RUN = 150

_CASE_NO = re.compile(r"\b(\d{2}-\d{4})-([A-Z]{2})-([A-Z]{3})\b")
_SHORT_NO = re.compile(r"\b(\d{2}-\d{4})\b")
_HEARING = re.compile(r"(local\s+public\s+hearing|public\s+hearing|adjudicatory\s+hearing|evidentiary\s+hearing|"
                      r"public\s+informational\s+meeting)", re.I)
_SCHEDULING = re.compile(r"schedul|set(?:ting)?\s+(?:a|the)|notice\s+of\s+(?:local\s+)?public\s+hearing|reschedul|"
                         r"continu|be\s+held|will\s+be|to\s+commence", re.I)
_PLACE = re.compile(r"\b(?:held|located|take\s+place|commence|convene)\s+(?:at|in)\s+(?:the\s+)?([^.;]{5,160}?)"
                    r"(?:,?\s+(?:on|at|beginning|commencing|starting)\s+(?:\d|Monday|Tuesday|Wednesday|Thursday|Friday|"
                    r"Saturday|Sunday|January|February|March|April|May|June|July|August|September|October|November|"
                    r"December)|[.;]|\s+electronically\s+filed|$)", re.I)
_AFTER_DATE = re.compile(r"(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)"
                         r"\s+\d{1,2},?\s+\d{4}|\b\d{1,2}/\d{1,2}/\d{4}\b)", re.I)
# ", at 6:00 p.m., at the Pike County Fairgrounds, 609 Fairgrounds Road, Piketon, Ohio;" -> the place
_AT_PLACE = re.compile(r"(?:,?\s*(?:at|beginning\s+at|commencing\s+at|starting\s+at)\s+\d{1,2}(?::\d{2})?\s*[ap]\.?\s*m\.?)?"
                       r",?\s*(?:at|in)\s+(?:the\s+)?((?!\d{1,2}(?::\d{2})?\s*[ap]\.?\s*m)[A-Z0-9][^;.]{4,160}?)"
                       r"(?=[;.]|,?\s+(?:and|with|for|which)\s|$)", re.I)
# "... should be held at the Jackson Middle School Auditorium, 21 Tropic Street, Jackson, Ohio 45640, on October 27":
# the place named before the date
_PLACE_BEFORE = re.compile(r"(?:held|located|take\s+place|convene)\s+(?:at|in)\s+(?:the\s+)?"
                           r"([A-Z0-9](?:(?!\b(?:held|located)\s+(?:at|in)\b)[^;.]){4,160}?)"
                           r"(?=,?\s+(?:on|at)\s+(?:\d|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|January|February|"
                           r"March|April|May|June|July|August|September|October|November|December)|[;.]|$)", re.I)
_DECISION = re.compile(r"^(?:Opinion,?\s+Order,?\s+and\s+Certificate|Opinion\s+and\s+Order|Order\s+on\s+Rehearing|"
                       r"Entry\s+on\s+Rehearing|Finding\s+and\s+Order|Finding\s+&\s+Order|Second\s+Entry\s+on\s+Rehearing|"
                       r"Order\s+on\s+Remand|Certificate\s+of\s+Environmental\s+Compatibility)", re.I)
_TOWNSHIP = re.compile(r"\b((?:[A-Z][a-z]+\.?\s+){0,2}[A-Z][A-Za-z']+)\s+(?:Charter\s+)?Township\b")
_MW = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*[-\s]?\s*(?:megawatts?|MW)\b", re.I)
_TWP_STOP = {"the", "and", "of", "in", "each", "said", "county", "both", "a", "an", "adjacent", "township"}
# Ohio's county seats, for the one case where the docket never names the county but the local public hearing's
# venue is in the county seat ("at Southern State Community College, Lecture Hall, Hillsboro, Ohio"). Used only as a
# fallback, and recorded as such (county_source).
COUNTY_SEATS = {
    "West Union": "Adams", "Lima": "Allen", "Ashland": "Ashland", "Jefferson": "Ashtabula", "Athens": "Athens",
    "Wapakoneta": "Auglaize", "St. Clairsville": "Belmont", "Georgetown": "Brown", "Hamilton": "Butler",
    "Carrollton": "Carroll", "Urbana": "Champaign", "Springfield": "Clark", "Batavia": "Clermont", "Wilmington": "Clinton",
    "Lisbon": "Columbiana", "Coshocton": "Coshocton", "Bucyrus": "Crawford", "Cleveland": "Cuyahoga", "Greenville": "Darke",
    "Defiance": "Defiance", "Delaware": "Delaware", "Sandusky": "Erie", "Lancaster": "Fairfield",
    "Washington Court House": "Fayette", "Columbus": "Franklin", "Wauseon": "Fulton", "Gallipolis": "Gallia",
    "Chardon": "Geauga", "Xenia": "Greene", "Cambridge": "Guernsey", "Cincinnati": "Hamilton", "Findlay": "Hancock",
    "Kenton": "Hardin", "Cadiz": "Harrison", "Napoleon": "Henry", "Hillsboro": "Highland", "Logan": "Hocking",
    "Millersburg": "Holmes", "Norwalk": "Huron", "Jackson": "Jackson", "Steubenville": "Jefferson", "Mount Vernon": "Knox",
    "Painesville": "Lake", "Ironton": "Lawrence", "Newark": "Licking", "Bellefontaine": "Logan", "Elyria": "Lorain",
    "Toledo": "Lucas", "London": "Madison", "Youngstown": "Mahoning", "Marion": "Marion", "Medina": "Medina",
    "Pomeroy": "Meigs", "Celina": "Mercer", "Troy": "Miami", "Woodsfield": "Monroe", "Dayton": "Montgomery",
    "McConnelsville": "Morgan", "Mount Gilead": "Morrow", "Zanesville": "Muskingum", "Caldwell": "Noble",
    "Port Clinton": "Ottawa", "Paulding": "Paulding", "New Lexington": "Perry", "Circleville": "Pickaway", "Waverly": "Pike",
    "Ravenna": "Portage", "Eaton": "Preble", "Ottawa": "Putnam", "Mansfield": "Richland", "Chillicothe": "Ross",
    "Fremont": "Sandusky", "Portsmouth": "Scioto", "Tiffin": "Seneca", "Sidney": "Shelby", "Canton": "Stark", "Akron": "Summit",
    "Warren": "Trumbull", "New Philadelphia": "Tuscarawas", "Marysville": "Union", "Van Wert": "Van Wert",
    "McArthur": "Vinton", "Lebanon": "Warren", "Marietta": "Washington", "Wooster": "Wayne", "Bryan": "Williams",
    "Bowling Green": "Wood", "Upper Sandusky": "Wyandot",
}
_SEAT_RX = re.compile(r"\b(" + "|".join(re.escape(s) for s in sorted(COUNTY_SEATS, key=len, reverse=True)) + r")\s*,\s*(?:Ohio|OH)\b")


def county_from_place(text: str) -> str | None:
    m = _SEAT_RX.search(text or "")
    return COUNTY_SEATS[m.group(1)] if m else None


# ------------------------------------------------------------------------------------------ parsing
def parse_daily_report(html: str) -> tuple[str | None, list[dict]]:
    """(report date, rows): each row has case number, title, section (NEW CASES, ENTRIES AND ORDERS, ...),
    summary and document link."""
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("div", class_="bodyarea") or soup
    text = body.get_text(" ")
    m = re.search(r"REPORT FOR\s+(\d{1,2}/\d{1,2}/\d{4})", text)
    report_date = iso(parse_date(m.group(1))) if m else None
    rows: list[dict] = []
    section = None
    for el in body.find_all(["center", "tr"]):
        if el.name == "center":
            t = clean(el.get_text(" "))
            if t:
                section = t
            continue
        tds = el.find_all("td")
        if len(tds) == 2 and _CASE_NO.search(clean(tds[0].get_text(" "))) and el.find("b"):
            cm = _CASE_NO.search(clean(tds[0].get_text(" ")))
            rows.append({"case_number": cm.group(0), "short": cm.group(1), "industry": cm.group(2), "purpose": cm.group(3),
                         "title": clean(tds[1].get_text(" ")), "section": section, "summary": "", "document_url": None})
        elif len(tds) == 2 and rows and not rows[-1]["summary"] and el.find("a"):
            rows[-1]["summary"] = clean(tds[1].get_text(" "))
            doc = next((a.get("href") for a in el.find_all("a") if "DocumentRecord" in (a.get("href") or "")), None)
            rows[-1]["document_url"] = doc
    return report_date, rows


def parse_open_list(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for tr in soup.find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in tr.find_all("td")]
        if len(cells) >= 3 and _CASE_NO.fullmatch(cells[0]):
            cm = _CASE_NO.fullmatch(cells[0])
            out.append({"case_number": cells[0], "short": cm.group(1), "industry": cm.group(2), "purpose": cm.group(3),
                        "title": cells[1], "opened": iso(parse_date(cells[2])), "closed": iso(parse_date(cells[3])) if len(cells) > 3 else None})
    return out


def parse_case_record(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    def span(name: str) -> str:
        el = soup.find(id=f"ContentPlaceHolderMaster_{name}")
        return clean(el.get_text(" ")) if el else ""

    entries = []
    table = soup.find(id="ContentPlaceHolderMaster_gvDocketInformation")
    if table is not None:
        for tr in table.find_all("tr"):
            cells = [clean(td.get_text(" ")) for td in tr.find_all("td")]
            if len(cells) >= 2 and parse_date(cells[0]):
                entries.append({"date": iso(parse_date(cells[0])), "summary": cells[1]})
    rows_text = span("lblRows")
    m = re.search(r"of\s+(\d+)\s+documents", rows_text)
    return {"case_number": span("mlblCase"), "title": span("mlblCaseDesc"), "status": span("mlblStatus"),
            "industry": span("mlblIndustry"), "purpose": span("mlblPurpose"), "opened": iso(parse_date(span("mlblOpenedDate"))),
            "closed": iso(parse_date(span("mlblClosedDate"))), "entries": entries,
            "documents_total": int(m.group(1)) if m else len(entries)}


def parse_docket_card(html: str) -> list[dict]:
    """Every (date, summary) pair of a printable docket card."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    lines = [clean(x) for x in soup.get_text("\n").split("\n") if clean(x)]
    out = []
    i = 0
    while i < len(lines):
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", lines[i]) and i + 1 < len(lines):
            out.append({"date": iso(parse_date(lines[i])), "summary": lines[i + 1]})
            i += 2
        else:
            i += 1
    return out


# ------------------------------------------------------------------------------------------ meaning
def townships_named(text: str) -> list[str]:
    out = []
    for m in _TOWNSHIP.finditer(text or ""):
        words = [w for w in m.group(1).split() if w.lower().strip(".") not in _TWP_STOP]
        if words and words[-1][0].isupper():
            name = " ".join(words[-2:]) if len(words) >= 2 and words[-2][0].isupper() and len(words[-2]) > 2 else words[-1]
            if name not in out and name.lower() not in ("county", "ohio"):
                out.append(name)
    return out


def hearing_events(entries: list[dict]) -> list[dict]:
    """Docket entries that schedule a hearing: (filed date, hearing date, kind, place)."""
    out = []
    for e in entries:
        s = e["summary"]
        hm = _HEARING.search(s)
        if not hm or not _SCHEDULING.search(s):
            continue
        # a transcript of a hearing held, testimony or a brief for one: not the notice of one
        if re.match(r"\s*(?:transcript|testimony|(?:direct|rebuttal|supplemental)\s+testimony|exhibit|(?:initial|reply|post[\s-]hearing)"
                    r"\s+brief|brief|notice\s+of\s+appearance|public\s+comment|memorandum|motion|proof\s+of\s+(?:publication|service)|"
                    r"affidavit|certificate\s+of\s+service)", s, re.I):
            continue
        filed = date.fromisoformat(e["date"]) if e.get("date") else None
        found = None
        # the date that follows the word "hearing" ("the local public hearing be held on December 10, 2026, at
        # 6:00 p.m., at the Pike County Fairgrounds"), not the effective date earlier in the same entry
        for km in _HEARING.finditer(s):
            after = s[km.end():km.end() + 220]
            dm = _AFTER_DATE.search(after)
            if not dm:
                continue
            d = parse_date(dm.group(0))
            if not d or (filed and d < filed):
                continue
            rest = after[dm.end():]
            pm = _AT_PLACE.match(rest)
            if not pm:
                before = list(_PLACE_BEFORE.finditer(s[km.end():km.end() + dm.start()]))
                pm = before[-1] if before else None
            place = re.sub(r",?\s*(?:on|at|beginning|commencing|starting)$", "", clean(pm.group(1))).rstrip(",;") if pm else None
            found = {"filed": e.get("date"), "hearing_date": iso(d), "kind": km.group(1).lower(),
                     "place": place or None, "summary": s}
            break
        if found:
            out.append(found)
    # one event per hearing date: the newest entry (a rescheduling supersedes), with the newest place named
    by_date: dict[str, dict] = {}
    for h in sorted(out, key=lambda h: h["filed"] or ""):
        prev = by_date.get(h["hearing_date"])
        if prev and not h["place"]:
            h = {**h, "place": prev["place"]}
        by_date[h["hearing_date"]] = h
    return sorted(by_date.values(), key=lambda h: h["hearing_date"])


def decisions(entries: list[dict]) -> list[dict]:
    return [{"date": e["date"], "summary": e["summary"]} for e in entries if _DECISION.match(e["summary"])]


def classify(title: str, purpose: str, texts: list[str]) -> list[str]:
    topics = notice_topics(" ".join([title] + texts[:6]), STATE)
    if not topics:
        topics = ["clean_energy_siting"]   # a Board case is an energy facility by definition
    return topics


# ------------------------------------------------------------------------------------------ run
def _fetch(fetcher: PoliteFetcher, url: str, max_age, purpose: str):
    with fetcher.purpose(purpose):
        r = fetcher.get(url, max_age=max_age)
    if not r.ok:
        raise FetchError(f"{url}: HTTP {r.status}")
    return r


def run(fetcher: PoliteFetcher, out_dir: Path, days: int = 30, data_dir: Path | None = None,
        today: date | None = None) -> dict:
    check_out_dir(out_dir)
    started = now_iso()
    today = today or date.today()
    since = window_start(days, today)
    rows_oh = load_state_towns(STATE, data_dir) if data_dir else load_state_towns(STATE)
    counties = county_rows(STATE, data_dir) if data_dir else county_rows(STATE)
    ledger = load_ledger(out_dir, SOURCE)
    errors: list[str] = []
    # 1. the session
    _fetch(fetcher, DIS, 0, "listing")
    # 2. daily reports
    daily: dict[str, list[dict]] = {}
    for n in range(DAILY_REPORTS):
        try:
            r = _fetch(fetcher, DIS + f"DailyReport.aspx?Link={n}", 0, "listing")
            d, rows = parse_daily_report(r.text)
            if d:
                daily[d] = rows
        except FetchError as e:
            errors.append(f"daily report {n}: {e}"[:200])
    named_in_reports: dict[str, list[dict]] = {}
    for d, rows in daily.items():
        for row in rows:
            if row["industry"] in ("EL", "GA", "GE") and row["purpose"] in PURPOSES:
                named_in_reports.setdefault(row["case_number"], []).append({**row, "report_date": d})
    # 3. open lists
    open_cases: dict[str, dict] = {}
    for purp in HIT_PURPOSES:
        url = DIS + f"CasesByIndustryPurposeStatus.aspx?indcode=EL&purpcode={purp}&status=OPEN"
        try:
            r = _fetch(fetcher, url, LIST_MAX_AGE, "listing")
        except FetchError as e:
            errors.append(f"open list {purp}: {e}"[:200])
            continue
        for c in parse_open_list(r.text):
            open_cases[c["case_number"]] = c
    recent_cut = today - timedelta(days=RECENT_DAYS)
    wanted: dict[str, dict] = {}            # keyed by the short number: one record per case
    for no, c in open_cases.items():
        if c.get("opened") and date.fromisoformat(c["opened"]) >= recent_cut:
            wanted[c["short"]] = c
    for no, rows in named_in_reports.items():
        if rows[0]["purpose"] in HIT_PURPOSES:
            wanted.setdefault(rows[0]["short"], {"case_number": no, "short": rows[0]["short"], "industry": rows[0]["industry"],
                                                 "purpose": rows[0]["purpose"], "title": rows[0]["title"], "opened": None})
    # 4. case records
    items: list[dict] = []
    for short, c in sorted(wanted.items(), key=lambda kv: kv[1].get("opened") or "9", reverse=True)[:MAX_RECORDS_PER_RUN]:
        no = c["case_number"]
        try:
            r = _fetch(fetcher, DIS + f"CaseRecord.aspx?CaseNo={short}", RECORD_MAX_AGE, "document")
            rec = parse_case_record(r.text)
        except FetchError as e:
            errors.append(f"{no}: {e}"[:200])
            continue
        entries = rec["entries"]
        title = rec["title"] or c.get("title") or ""
        oldest = min((e["date"] for e in entries if e.get("date")), default=None)
        county = county_named(title) or next((county_named(t) for t in (e["summary"] for e in entries) if county_named(t)), None)
        need_card = bool(entries) and rec["documents_total"] > len(entries) and (
            (oldest and date.fromisoformat(oldest) > since)       # the window reaches past the 15 latest entries
            or not county)                                        # the county is usually in the application entry
        if need_card:
            try:
                r2 = _fetch(fetcher, DIS + f"CaseRecord.aspx?Caseno={short}&link=PDC", RECORD_MAX_AGE, "document")
                card = parse_docket_card(r2.text)
                if card:
                    entries = card
            except FetchError as e:
                errors.append(f"{no} docket card: {e}"[:200])
        texts = [e["summary"] for e in entries]
        county_source = "docket" if county else None
        if not county:
            county = next((county_named(t) for t in texts if county_named(t)), None)
            county_source = "docket" if county else None
        hearings = hearing_events(entries)
        if not county:
            for h in hearings:
                county = county_from_place(h["summary"])
                if county:
                    county_source = "hearing venue in the county seat"
                    break
        twps = townships_named(" ".join([title] + texts))
        pm = re.match(r"([A-Z]{3})", rec.get("purpose") or "")
        if pm:
            c = {**c, "purpose": pm.group(1)}      # the record's own purpose code (a report may show another suffix)
        no = rec["case_number"] or no
        mw = None
        for t in [title] + texts:
            mm = _MW.search(t)
            if mm:
                try:
                    mw = float(mm.group(1).replace(",", ""))
                except ValueError:
                    pass
                break
        decs = decisions(entries)
        purpose = c["purpose"]
        items.append({
            "case_number": no, "title": title, "purpose": purpose, "purpose_label": PURPOSES.get(purpose, purpose),
            "status": rec["status"], "opened": rec["opened"] or c.get("opened"), "closed": rec["closed"],
            "county": county, "county_source": county_source, "townships": twps, "mw": mw,
            "topics": classify(title, purpose, texts),
            "hearings": hearings, "decisions": decs, "latest_entries": entries[:5],
            "in_daily_reports": [{"date": x["report_date"], "section": x["section"], "summary": x["summary"]}
                                 for x in named_in_reports.get(no, []) + named_in_reports.get(c["case_number"], [])
                                 if True][:40],
            "link": DIS + f"CaseRecord.aspx?CaseNo={no}", "first_seen": first_seen(ledger, no, started),
            "siting_relevant": purpose in HIT_PURPOSES,
        })
    # letters of notification and construction notices named in the reports: items, not hits
    for no, rows in named_in_reports.items():
        if rows[0]["purpose"] not in HIT_PURPOSES and no not in {i["case_number"] for i in items}:
            items.append({"case_number": no, "title": rows[0]["title"], "purpose": rows[0]["purpose"],
                          "purpose_label": PURPOSES.get(rows[0]["purpose"]), "status": None, "opened": rows[0]["report_date"],
                          "county": county_named(rows[0]["title"] + " " + rows[0]["summary"]),
                          "townships": townships_named(rows[0]["title"] + " " + rows[0]["summary"]), "mw": None,
                          "topics": ["clean_energy_siting"], "hearings": [], "decisions": [],
                          "in_daily_reports": [{"date": x["report_date"], "section": x["section"], "summary": x["summary"]} for x in rows],
                          "link": DIS + f"CaseRecord.aspx?CaseNo={no}", "first_seen": first_seen(ledger, no, started),
                          "siting_relevant": False})
    hits = []
    for it in items:
        hits.extend(to_hits(it, since, today, rows_oh, counties))
    report = {
        "source": SOURCE, "started": started, "finished": now_iso(), "since": since.isoformat(),
        "daily_reports": sorted(daily), "cases_in_reports": len(named_in_reports), "open_cases": len(open_cases),
        "records_read": sum(1 for i in items if i.get("status") is not None), "items": len(items), "hits": len(hits),
        "hearings_found": sum(len(i["hearings"]) for i in items),
        "topics": dict(Counter(t for i in items for t in i["topics"]).most_common()),
        "counties_unresolved": sorted({i["county"] for i in items if i.get("county") and norm(i["county"]) not in counties}),
        "errors": errors, "network": network_report(fetcher),
    }
    write_outputs(SOURCE, out_dir, items, hits, LISTING_URL, report, ledger)
    return report


def to_hits(item: dict, since: date, today: date, rows_oh: list[dict], counties: dict[str, dict]) -> list[dict]:
    if not item["siting_relevant"]:
        return []
    upcoming = sorted((h for h in item["hearings"] if h["hearing_date"] and date.fromisoformat(h["hearing_date"]) >= since),
                      key=lambda h: h["hearing_date"])
    recent_dec = [d for d in item["decisions"] if d["date"] and date.fromisoformat(d["date"]) >= since]
    opened = date.fromisoformat(item["opened"]) if item.get("opened") else None
    if upcoming:
        h = upcoming[0]
        when, date_kind, place = date.fromisoformat(h["hearing_date"]), "hearing", h.get("place")
        what = f"{h['kind'].capitalize()} {h['hearing_date']}" + (f" at {place}" if place else "") + "."
        lead = h["summary"]
    elif recent_dec:
        d = recent_dec[-1]
        when, date_kind, place = date.fromisoformat(d["date"]), "decision", None
        what, lead = f"Decision {d['date']}.", d["summary"]
    elif opened and opened >= since:
        when, date_kind, place = None, "filed", None
        what = f"Filed {item['opened']}."
        lead = item["latest_entries"][-1]["summary"] if item.get("latest_entries") else ""
    else:
        return []
    county = item.get("county")
    county_row = counties.get(norm(county)) if county else None
    town = county_row["town"] if county_row else (f"{county} County" if county else None)
    if not town:
        return []
    mw = f"{item['mw']:g} MW. " if item.get("mw") else ""
    snippet = snippet_of(f"OPSB {item['case_number']} ({item['purpose_label']}): {item['title']}. {mw}{what}", lead)
    base = dict(source=SOURCE, source_kind=SOURCE_KIND, state=STATE, county=county, board=BOARD, meeting_date=when,
                date_kind=date_kind, topics=item["topics"], snippet=snippet, source_url=item["link"], listing_url=LISTING_URL,
                document_title=f"OPSB case {item['case_number']}: {item['title']}", first_seen=item["first_seen"],
                headline_text=f"{item['case_number']} {item['title']}", place=place,
                extra={"purpose": item["purpose"], "status": item.get("status"), "mw": item.get("mw"),
                       "townships_named": item["townships"], "configured": county_row is not None})
    out = [make_hit(town=town, **base)]
    if county_row:
        known = known_townships(rows_oh, county)
        for name in item["townships"]:
            row_name = resolve_known(name, known)
            if row_name and all(h["town"] != row_name for h in out):
                extra = {**base["extra"], "attributed_from": town, "configured": True}
                # the township is in the snippet so the hit has its own id (id = source_url + snippet)
                twp_snippet = snippet_of(f"{row_name}: {snippet}")
                out.append(make_hit(town=row_name, **{**base, "snippet": twp_snippet, "extra": extra}))
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
    print(f"OPSB: {rep['records_read']} case records, {rep['items']} items, {rep['hearings_found']} hearing entries, "
          f"{rep['hits']} hits; daily reports {rep['daily_reports']}; errors {len(rep['errors'])}; network {rep['network']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
