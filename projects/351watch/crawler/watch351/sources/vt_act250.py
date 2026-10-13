"""Vermont Act 250 daily agenda -> Agenda Ahead items (Wave 1 test, gated).

Source: the Act 250 Agenda, "an aggregate list of Act 250 projects that have been noticed or for which
a decision or Jurisdictional Opinion (JO) has been issued", updated daily, covering this week, the prior
week and the week after: https://anrweb.vt.gov/ANR/Act250/agenda.aspx (plain HTML table). Each row is
enriched from the project's public detail page, Details.aspx?Num=<project number> (project type, dates
received / complete / noticed / hearing / response deadline / decision, status, participants), which
is also the item's link.

Only plain GETs are made. The agenda's date picker and the database search are ASP.NET form POSTs and
are not used, so one run sees the current three-week window only; the item ledger keeps what earlier
runs saw. anrweb.vt.gov has no robots.txt (404: everything allowed); every request goes through
watch351.fetch.PoliteFetcher (AgendaAheadBot, robots.txt on every hop, <= 1 request/second/host, cache).

Item (data/test/wave1/sources/vt_act250_items.json): project number, district, town (the agenda's
town, normalized to data/towns_vt.json), project (the description), applicant(s) (organizations; private
persons as "[individual]"), application type (Major / Minor / Administrative Amendment / JO ...), project
type (detail page), status, dates (agenda, hearing, decision, comment / petition deadline, notice), link,
and the siting flag with its topics and reason.

Siting-relevant (flag), by the project type and the description:
  solar                 solar arrays (ground-mounted or as part of a project)
  battery_storage       battery / energy storage
  data_center           data centers, server farms, crypto mining
  clean_energy_siting   other energy generation, substations, transmission (most energy siting in
                        Vermont is at the PUC under 30 V.S.A. sec. 248, not Act 250)
  wireless_telecom      telecommunications towers
  extraction            quarries, gravel / sand pits, earth extraction (new topic key, Wave 1)
  large_development     large commercial or industrial projects (project type commercial / industrial /
                        warehouse / ski resort): >= 20,000 sq ft of new floor area, >= 10 acres disturbed /
                        developed, >= 50 lodging rooms, >= 100 parking spaces, or a shopping center; sizes of
                        what exists already or of the land are not counted (new topic key, Wave 1)
Not flagged even when the subject fits: administrative amendments and JOs that only extend a
construction-completion date, transfer a permit, change a condition or make "insignificant changes"
without new construction, and records created in error or inactivated (kept as items, flagged false,
with the reason). Withdrawn and abandoned applications stay flagged: the withdrawal is the decision.

Hits (data/test/wave1/sources/vt_act250_hits.json): one per flagged item, board "Act 250 District N
Commission", board_key planning_board, meeting_date = hearing date, else decision date, else the
comment / petition deadline, else the agenda date; source "vt_act250".

    cd projects/351watch/crawler
    python3 -m watch351.sources.vt_act250                 # fetch + build (gated output dir)
    python3 -m watch351.sources.vt_act250 --offline       # rebuild from the fetch cache only
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

from ..fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from .state_feeds import (DEFAULT_OUT, INDIVIDUAL, check_out_dir, clean, first_seen, hit_id, iso, load_json,
                          load_state_towns, norm_key, now_iso, organizations, snippet_of, write_json)

log = logging.getLogger("vt_act250")

SOURCE = "vt_act250"
AGENDA_URL = "https://anrweb.vt.gov/ANR/Act250/agenda.aspx"
DETAIL_URL = "https://anrweb.vt.gov/ANR/Act250/Details.aspx?Num={num}"
LISTING_MAX_AGE = 20 * 3600
DETAIL_MAX_AGE = 20 * 3600
BOARD_KEY = "planning_board"
REFRESH_PER_RUN = 30     # earlier, still-pending items re-read from their detail page per run

APP_TYPES = {"adm. amend": "Administrative Amendment", "jo": "Jurisdictional Opinion", "major": "Major",
             "minor": "Minor", "": ""}


def parse_date(s: str | None) -> date | None:
    s = clean(s)
    for fmt in ("%m-%d-%Y", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


# ------------------------------------------------------------------------------------- parsing
def parse_agenda(html: str) -> list[dict]:
    """Rows of the agenda table (gvResults), keyed by the span ids' field names."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id=re.compile(r"gvResults$"))
    if table is None:
        raise ValueError("Act 250 agenda: results table not found (page layout changed?)")
    rows = []
    for tr in table.find_all("tr"):
        spans = tr.find_all("span", id=re.compile(r"_lbl\w+$"))
        if not spans:
            continue
        rec = {re.search(r"_lbl(\w+)$", s["id"]).group(1): clean(s.get_text(" ")) for s in spans}
        rows.append(rec)
    m = re.search(r"(\d+)\s+Projects", soup.get_text(" "))
    if m and int(m.group(1)) != len(rows):
        log.warning("agenda says %s projects, table has %d rows", m.group(1), len(rows))
    return rows


def parse_detail(html: str) -> dict:
    """Fields of a project's detail page: label/value pairs, the status timeline and participants."""
    soup = BeautifulSoup(html, "lxml")
    out: dict = {}
    labels = ["Project Number", "Project Name", "Project Address", "Project Town", "Description",
              "Application Type", "Project Type", "Latitude", "Longitude", "Date Application Received",
              "Date Deemed Complete", "Notice Issued", "Pre-Hearing Date", "Hearing Date", "Response Deadline",
              "Date Decision Issued", "Current Status"]
    text_nodes = [clean(t) for t in soup.get_text("\n").split("\n")]
    text_nodes = [t for t in text_nodes if t]
    for i, t in enumerate(text_nodes):
        if t in labels and t not in out:
            nxt = text_nodes[i + 1] if i + 1 < len(text_nodes) else ""
            out[t] = "" if nxt in labels or nxt in ("Project Status", "Project Participants",
                                                     "Status Definitions") else nxt
    parts = []
    table = soup.find("table", id=re.compile(r"gvParticipant$"))
    if table is not None:
        for tr in table.find_all("tr")[1:]:
            tds = [clean(td.get_text(" ")) for td in tr.find_all("td")]
            if len(tds) >= 2:
                parts.append({"role": tds[0], "name": tds[1]})
    out["participants"] = parts
    return out


# -------------------------------------------------------------------------------- classification
_SOLAR = re.compile(r"\bsolar\b|photovoltaic|\bPV\s+(?:array|system|facilit|project)", re.I)
_STORAGE = re.compile(r"batter(?:y|ies)\s+(?:energy\s+)?storage|\bBESS\b|energy\s+storage", re.I)
_DATA_CENTER = re.compile(r"data\s+cent(?:er|re)|server\s+farm|crypto(?:currency)?\s+mining|bitcoin", re.I)
_ENERGY = re.compile(r"\bsubstation|transmission\s+line|generating\s+(?:facility|station|plant)|"
                     r"power\s+plant|hydro(?:electric)?\s+(?:facility|project|station)|wind\s+(?:turbine|farm|"
                     r"energy\s+facilit)|biomass\s+(?:plant|facility)|anaerobic\s+digester", re.I)
_TOWER = re.compile(r"telecommunications?\s+(?:tower|facility)|cell(?:ular)?\s+tower|wireless\s+"
                    r"(?:communications?\s+)?(?:tower|facility)|\bmonopole\b|communications?\s+tower|"
                    r"(?:radio|broadcast|tr?ansmitter)\s+tower|\bantennas?\b", re.I)
_EXTRACTION = re.compile(r"\bquarr(?:y|ies|ying)\b|gravel\s+(?:pit|extraction|operation)|sand\s+(?:and\s+gravel\s+)?"
                         r"(?:pit|extraction|operation)|\bsand\s+pit\b|earth\s+(?:resource\s+)?extraction|"
                         r"\bextraction\b|\bborrow\s+pit\b|(?<!crypto )(?<!cryptocurrency )(?<!data )\bmining\b|\bcrusher|"
                         r"\bcrushing\b", re.I)
_INDUSTRIAL = re.compile(r"\bindustrial\b|manufactur|warehouse|distribution\s+(?:center|facility|building)|"
                         r"logistics|fulfillment|processing\s+(?:plant|facility)|\bfactory\b|manufacturing\s+plant", re.I)
_SHOPPING = re.compile(r"shopping\s+(?:center|plaza|mall)|big[\s-]box|supermarket|\bretail\s+(?:center|plaza)", re.I)
# changes that are not new siting: time extensions, transfers, condition edits, in-kind replacement
_ADMIN_ONLY = re.compile(r"extension\s+of\s+(?:the\s+)?(?:construction[\s-]+)?(?:completion|commencement)|"
                         r"extend(?:s|ing)?\s+the\s+(?:construction[\s-]+)?(?:completion|commencement)|"
                         r"\btransfer\s+of\s+(?:the\s+)?permit|change\s+(?:the\s+)?(?:permittee|ownership)|"
                         r"(?:revision|amendment|modification)\s+of\s+condition|replacement[\s-]in[\s-]kind|"
                         r"name\s+change|correct(?:ion)?\s+(?:of\s+)?(?:a\s+)?(?:scrivener|typographical|clerical)",
                         re.I)
_NEW_WORK = re.compile(r"\bconstruct(?:ion)?\s+(?:of\s+)?(?:a|an|two|three|four|\d)|\bnew\s+(?:building|structure|"
                       r"facility)|\bexpan(?:d|sion)\b|\baddition\b|\binstall(?:ation)?\s+of\s+(?:a|an)\s+"
                       r"(?:\d|new)", re.I)

_SQFT = re.compile(r"(\d{1,3}(?:,\d{3})+|\d{4,7})\s*(?:\+/-\s*|±\s*)?[\s-]*(?:sq\.?\s*(?:ft|feet)|square[\s-]+f(?:ee|oo)t|"
                   r"SF\b|s\.f\.)(?!\s+of\s+(?:land|property|lot))", re.I)
# acres of new development (disturbed, cleared, impervious, built), not the size of the parcel
_ACRES = re.compile(r"(\d{1,4}(?:\.\d+)?)\s*(?:\+/-\s*|±\s*)?[\s-]*acres?\s+(?:of\s+)?(?:new\s+)?(?:earth\s+)?"
                    r"(?:disturbance|disturbed|impervious|clearing|cleared|development|developed|building\s+area|"
                    r"solar|array|extraction)", re.I)
_UNITS = re.compile(r"(\d{2,4})\s*(?:-|\s)?(?:room|unit|key|bed)s?\b", re.I)
_PARKING = re.compile(r"(\d{2,4})\s*(?:new\s+)?(?:parking\s+)?(?:spaces|stalls)", re.I)
# sizes of what is already there or of the land, not of the project
_NOT_PROJECT_SIZE = re.compile(r"(?:existing|current(?:ly)?|former|approximately\s+\S+\s+of\s+land|parcel|lot|tract|"
                               r"property)\W+(?:\w+\W+){0,3}$", re.I)


def _max_num(rx: re.Pattern, text: str) -> float:
    vals = []
    for m in rx.finditer(text):
        if _NOT_PROJECT_SIZE.search(text[max(0, m.start() - 40):m.start()]):
            continue
        try:
            vals.append(float(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return max(vals) if vals else 0.0


def classify(desc: str, project_type: str, app_type: str, status: str) -> tuple[list[str], str]:
    """(topics, reason). Empty topics = not siting-relevant (the reason says why)."""
    text = f"{project_type} :: {desc}"
    topics: list[str] = []
    reasons: list[str] = []
    # solar on a roof or a building is equipment, not siting (the MI / VA rooftop rule); ground-mounted is
    if _SOLAR.search(text) and not (re.search(r"roof|building[\s-]mounted|canopy", text, re.I)
                                    and not re.search(r"ground[\s-]mount|solar\s+(?:farm|array|field|facility)", text, re.I)):
        topics.append("solar")
    if _STORAGE.search(text):
        topics.append("battery_storage")
    if _DATA_CENTER.search(text):
        topics.append("data_center")
    if _ENERGY.search(text) or re.search(r"^\s*energy|utilit(?:y|ies)\s*-\s*(?:electric|generat)", project_type, re.I):
        topics.append("clean_energy_siting")
    if _TOWER.search(text) or re.search(r"telecommunication", project_type, re.I):
        topics.append("wireless_telecom")
    pt = project_type.lower()
    if _EXTRACTION.search(text) or re.search(r"extraction|gravel|quarr|mining", pt):
        # closing a pit ("reclamation of a borrow pit") is not extraction, unless work continues or grows
        if not (re.search(r"reclamation\s+of\s+(?:an?\s+|the\s+)?(?:existing\s+)?(?:borrow|gravel|sand)\s+pit", desc, re.I)
                and not re.search(r"\bextract|\bexpan|\bcrush|continue[sd]?\s+(?:operation|extraction)", desc, re.I)):
            topics.append("extraction")
    sqft, acres = _max_num(_SQFT, desc), _max_num(_ACRES, desc)
    units, parking = _max_num(_UNITS, desc), _max_num(_PARKING, desc)
    industrial = bool(re.search(r"industrial|warehouse|manufactur|indust", pt) or _INDUSTRIAL.search(desc))
    commercial = bool(re.search(r"commercial|retail|hotel|motel|office|shopping|ski\s+resort", pt))
    large = []
    if commercial or industrial:
        if sqft >= 20000:
            large.append(f"{int(sqft):,} sq ft")
        if acres >= 10:
            large.append(f"{acres:g} acres developed")
        if units >= 50 and re.search(r"hotel|motel|lodg|room|resort", text, re.I):
            large.append(f"{int(units)} rooms")
        if parking >= 100:
            large.append(f"{int(parking)} parking spaces")
        # a new shopping center; an addition to one counts only by its own size (20,000 sq ft above)
        if _SHOPPING.search(desc) and not re.search(r"\baddition\b|\bexpan(?:d|sion)\b", desc, re.I):
            large.append("shopping center")
    # land divided for industry: "subdivide a 66 acre parcel into a 6 lot commercial/industrial subdivision"
    parcel = re.search(r"(\d{2,4}(?:\.\d+)?)\s*(?:\+/-\s*|±\s*)?[\s-]*acre\s+(?:parcel|tract)", desc, re.I)
    if re.search(r"industrial\s+(?:subdivision|park|lots?)\b", desc, re.I) and parcel and float(parcel.group(1)) >= 10:
        industrial = True
        large.append(f"industrial subdivision of {float(parcel.group(1)):g} acres")
    if large and "large_development" not in topics:
        topics.append("large_development")
        reasons.append(("large industrial" if industrial else "large commercial") + " (" + ", ".join(large) + ")")
    if not topics:
        return [], "no siting subject"
    if re.search(r"record created in error|inactivated", f"{status} {desc}", re.I):
        return [], f"{status.lower() or 'inactive'} (" + ", ".join(topics) + ")"
    if app_type in ("Administrative Amendment", "Jurisdictional Opinion", ""):
        # the permit being amended is often described ("..., authorizing construction of four warehouse
        # buildings"): that is not new work
        rest = re.sub(r"authoriz(?:ing|ed|es)\s+(?:the\s+)?construction\s+of[^.]*", " ", desc, flags=re.I)
        if (_ADMIN_ONLY.search(desc) or re.search(r"insignificant\s+changes", project_type, re.I)) \
                and not _NEW_WORK.search(_ADMIN_ONLY.sub(" ", rest)):
            return [], "administrative change only (" + ", ".join(topics) + ")"
    return topics, "; ".join(reasons) or ", ".join(topics)


# ------------------------------------------------------------------------------------- towns
def town_index(rows: list[dict]) -> dict[str, dict]:
    idx = {}
    for r in rows:
        idx[norm_key(r["town"])] = r
        for a in r.get("aliases", []):
            idx.setdefault(norm_key(a), r)
    return idx


def resolve_town(name: str, idx: dict[str, dict]) -> tuple[str, str | None]:
    """(town, county) for an Act 250 town label ("Essex, Town of", "Alburgh Village", "Rutland City")."""
    raw = clean(name)
    for cand in (raw, re.sub(r"\s+(?:Town|Village)$", "", raw), re.sub(r",\s*(?:Town|City)\s+of$", "", raw)):
        r = idx.get(norm_key(cand))
        if r:
            return r["town"], r.get("county")
    return re.sub(r",\s*(?:Town|City)\s+of$", "", raw), None


# --------------------------------------------------------------------------------------- build
def district_of(num: str) -> str | None:
    m = re.match(r"(?:JO\s*)?(\d)", num.strip(), re.I)
    return m.group(1) if m else None


def build_item(row: dict, det: dict, towns: dict[str, dict], seen_ts: str) -> dict:
    num = row.get("ProjectNumber") or det.get("Project Number") or ""
    app_type = APP_TYPES.get((row.get("AppType") or "").lower(), row.get("AppType") or det.get("Application Type") or "")
    desc = row.get("Desc") or det.get("Description") or ""
    status = det.get("Current Status") or row.get("Status") or ""
    ptype = det.get("Project Type") or ""
    others = [row.get("LandOwner", "")] + [p["name"] for p in det.get("participants", [])]
    applicants = organizations(row.get("Applicants", ""), others)
    landowners = organizations(row.get("LandOwner", ""), [row.get("Applicants", "")] +
                               [p["name"] for p in det.get("participants", [])])
    town, county = resolve_town(row.get("Town") or det.get("Project Town") or "", towns)
    hearing = parse_date(row.get("HearingDate")) or parse_date(det.get("Hearing Date"))
    decision = parse_date(det.get("Date Decision Issued"))
    deadline = parse_date(row.get("ResponseDate")) or parse_date(det.get("Response Deadline"))
    agenda = parse_date(row.get("AgendaDate"))
    if hearing:
        when, kind = hearing, "hearing"
    elif decision:
        when, kind = decision, "decision"
    elif deadline:
        when, kind = deadline, "comment_deadline"
    else:
        when, kind = agenda, "agenda"
    topics, reason = classify(desc, ptype, app_type, status)
    return {
        "project_number": num,
        "district": district_of(num),
        "town": town,
        "town_as_listed": row.get("Town") or "",
        "county": county,
        "project": desc,
        "project_name": det.get("Project Name") or "",
        "address": row.get("Address") or det.get("Project Address") or "",
        "applicants": applicants,
        "landowners": landowners,
        "application_type": app_type,
        "project_type": ptype,
        "status": status,
        "decision_issued": row.get("Decision") == "Yes" or bool(decision),
        "agenda_date": iso(agenda),
        "hearing_date": iso(hearing),
        "decision_date": iso(decision),
        "comment_deadline": iso(deadline),
        "notice_date": iso(parse_date(det.get("Notice Issued"))),
        "received_date": iso(parse_date(det.get("Date Application Received"))),
        "date": iso(when),
        "date_kind": kind,
        "link": DETAIL_URL.format(num=quote(num)),
        "siting_relevant": bool(topics),
        "topics": topics,
        "flag_reason": reason,
        "first_seen": seen_ts,
        "detail_ok": bool(det),
    }


def row_from_detail(det: dict) -> dict:
    """An agenda-row-shaped record from a detail page alone (a project that has left the three-week agenda,
    re-checked for its decision)."""
    by_role: dict[str, list[str]] = {}
    for p in det.get("participants", []):
        by_role.setdefault(p["role"].lower(), []).append(p["name"])
    app = det.get("Application Type") or ""
    app = {"administrative amendment": "Adm. Amend", "jurisdictional opinion": "JO"}.get(app.lower(), app)
    fmt = lambda s: (parse_date(s).strftime("%m-%d-%Y") if parse_date(s) else "")  # noqa: E731
    return {"ProjectNumber": det.get("Project Number", ""), "AppType": app,
            "Applicants": "; ".join(by_role.get("applicant", []) or by_role.get("co-applicant", [])),
            "LandOwner": "; ".join(by_role.get("land owner", [])), "Address": det.get("Project Address", ""),
            "Desc": det.get("Description", ""), "Status": det.get("Current Status", ""),
            "Town": det.get("Project Town", ""), "HearingDate": fmt(det.get("Hearing Date")),
            "Decision": "Yes" if det.get("Date Decision Issued") else "", "AgendaDate": "",
            "ResponseDate": fmt(det.get("Response Deadline"))}


def item_from_detail(fetcher: PoliteFetcher, num: str, towns: dict[str, dict], seen_ts: str) -> dict | None:
    with fetcher.purpose("document"):
        d = fetcher.get(DETAIL_URL.format(num=quote(num)), max_age=DETAIL_MAX_AGE)
    if not d.ok:
        return None
    det = parse_detail(d.text)
    if not det.get("Project Number"):
        return None
    it = build_item(row_from_detail(det), det, towns, seen_ts)
    it["agenda_date"] = None
    it["from_detail_only"] = True
    return it


def to_hit(item: dict) -> dict:
    kind = {"hearing": "Hearing", "decision": "Decision", "comment_deadline": "Comment/petition deadline",
            "agenda": "Listed"}[item["date_kind"]]
    who = ", ".join(a for a in item["applicants"] if a != INDIVIDUAL)
    if not who and not item["applicants"]:
        who = ", ".join(a for a in item.get("landowners", []) if a != INDIVIDUAL)
        who = f"landowner {who}" if who else ""
    who = who or "private applicant"
    head = f"Act 250 {item['project_number']}"
    if item["application_type"]:
        head += f" ({item['application_type']})"
    snippet = snippet_of(f"{head}, {item['town']}: {who}.", f"{kind} {item['date']}." if item["date"] else "",
                         f"Status: {item['status']}." if item["status"] else "", item["project"])
    return {
        "id": hit_id(item["link"], snippet),
        "state": "VT",
        "town": item["town"],
        "county": item.get("county"),
        "board": f"Act 250 District {item['district']} Commission" if item.get("district") else "Act 250 District Commission",
        "board_key": BOARD_KEY,
        "meeting_date": item["date"],
        "topics": item["topics"],
        "snippet": snippet,
        "source_url": item["link"],
        "listing_url": AGENDA_URL,
        "document_title": f"Act 250 project {item['project_number']}",
        "text_source": "html",
        "first_seen": item["first_seen"],
        "source": SOURCE,
    }


def run(fetcher: PoliteFetcher, out_dir: Path, data_dir: Path | None = None) -> dict:
    check_out_dir(out_dir)
    started = now_iso()
    towns = town_index(load_state_towns("VT", data_dir) if data_dir else load_state_towns("VT"))
    ledger_p = out_dir / "vt_act250_ledger.json"
    ledger = load_json(ledger_p, {})
    errors: list[str] = []
    with fetcher.purpose("listing"):
        resp = fetcher.get(AGENDA_URL, max_age=LISTING_MAX_AGE)
    if not resp.ok:
        raise FetchError(f"Act 250 agenda HTTP {resp.status}")
    rows = parse_agenda(resp.text)
    items = []
    for row in rows:
        num = row.get("ProjectNumber") or ""
        det: dict = {}
        try:
            with fetcher.purpose("document"):
                d = fetcher.get(DETAIL_URL.format(num=quote(num)), max_age=DETAIL_MAX_AGE)
            if d.ok:
                det = parse_detail(d.text)
            else:
                errors.append(f"{num}: detail HTTP {d.status}")
        except FetchError as e:
            errors.append(f"{num}: {e}"[:200])
        key = f"{num}|{row.get('AgendaDate')}|{row.get('Status')}"
        items.append(build_item(row, det, towns, first_seen(ledger, key, started)))
    # items seen on earlier runs (the agenda shows three weeks only) stay in the items file; those still
    # pending are re-read from their detail page (at most REFRESH_PER_RUN a day) so a later decision or
    # hearing date reaches the item after the project has left the agenda
    prev = {(i["project_number"], i.get("agenda_date")): i for i in load_json(out_dir / "vt_act250_items.json", {}).get("items", [])}
    today_nums = {it["project_number"] for it in items}
    stale = [k for k, i in prev.items() if i["project_number"] not in today_nums
             and re.search(r"pending|hearing|recess", i.get("status") or "", re.I)][:REFRESH_PER_RUN]
    for k in stale:
        try:
            it = item_from_detail(fetcher, k[0], towns, prev[k]["first_seen"])
        except FetchError as e:
            errors.append(f"{k[0]}: refresh {e}"[:200])
            continue
        if it:
            it["agenda_date"] = prev[k].get("agenda_date")
            prev[k] = it
    for it in items:
        prev[(it["project_number"], it.get("agenda_date"))] = it
    all_items = sorted(prev.values(), key=lambda i: (i.get("date") or "", i["project_number"]), reverse=True)
    hits = [to_hit(i) for i in all_items if i["siting_relevant"]]
    write_json(ledger_p, ledger)
    doc = {"generated": now_iso(), "source": SOURCE, "listing_url": AGENDA_URL,
           "items_on_agenda_today": len(items), "items": all_items}
    write_json(out_dir / "vt_act250_items.json", doc)
    write_json(out_dir / "vt_act250_hits.json", {"generated": doc["generated"], "source": SOURCE, "hits": hits})
    report = {
        "source": SOURCE, "started": started, "finished": now_iso(),
        "rows_on_agenda": len(rows), "items_total": len(all_items), "details_ok": sum(i["detail_ok"] for i in items),
        "flagged": sum(i["siting_relevant"] for i in items),
        "topics": dict(Counter(t for i in items for t in i["topics"]).most_common()),
        "towns_unmatched": sorted({i["town_as_listed"] for i in items if i["county"] is None and towns}),
        "errors": errors,
        "network": {"requests": fetcher.stats["network"], "cache_hits": fetcher.stats["cache"],
                    "errors": fetcher.stats["errors"], "robots_blocked": fetcher.stats["robots_blocked"]},
    }
    write_json(out_dir / "runs" / f"vt_act250_{started[:10]}.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--offline", action="store_true", help="read the fetch cache only")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    rep = run(PoliteFetcher(a.cache_dir, offline=a.offline), a.out_dir)
    print(f"Act 250: {rep['rows_on_agenda']} on the agenda, {rep['details_ok']} detail pages, "
          f"{rep['flagged']} flagged {rep['topics']}; errors {len(rep['errors'])}; network {rep['network']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
