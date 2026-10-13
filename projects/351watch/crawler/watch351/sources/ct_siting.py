"""Connecticut Siting Council petitions, dockets and hearings -> Agenda Ahead items (Wave 1 test, gated).

The Siting Council has exclusive jurisdiction over the location of electric generating and storage
facilities over 1 MW, transmission, and telecommunications towers (C.G.S. sec. 16-50x, 16-50i): projects
up to 65 MW come as petitions for a declaratory ruling, larger ones and new towers as applications
(dockets) with public hearings. Towns are notified but do not decide, so these listings are where a
Connecticut town's energy and tower siting shows up.

Pages read (plain GETs on portal.ct.gov; robots.txt allows /csc/; every request through
watch351.fetch.PoliteFetcher):
  * Pending Matters    portal.ct.gov/csc/1_applications-and-other-pending-matters/pending-matters
                       (applications, petitions, tower-share requests, sub-petitions, enforcement actions)
  * each pending petition's / docket's own page (received date; a docket's hearing dates)
  * Petition list 1500+ portal.ct.gov/csc/decisions/petition-lists/petition-list-1500-1999 (decisions:
                       Approved / Denied / Withdrawn with date), from BACKFILL_FROM on
  * Docket list 500+   portal.ct.gov/csc/decisions/docketlists/docket-list-nos500-999 (decided dockets
                       from DOCKET_FROM on; decision date and outcome from the docket's own page (FINAL
                       DECISION), else from the Decision and Order file name)
  * Meetings and Minutes: the current Council meeting agenda (PDF): matters for decision at that meeting
                       and the "Upcoming Calendar Events" (hearings)

Item (data/test/wave1/sources/ct_siting_items.json), one per matter and host town: kind (docket,
petition, tower_share, sub_petition, enforcement), number, applicant, facility (description, technology,
MW), host town(s) (the towns the Council's text marks, normalized to data/towns_ct.json), status
(pending / approved / denied / withdrawn ...), dates (received, hearing(s), Council meeting, decision),
link, and the siting flag with its topics and reason.

Siting-relevant (topics): solar; battery_storage; clean_energy_siting (fuel cells, other generation,
transmission lines and substations, including rebuilds the Council rules on); wireless_telecom (new
towers, tower extensions and modifications, small wireless facilities); data_center. Not flagged:
tower-share requests (co-location on an existing tower, no new structure), statewide maintenance
sub-petitions, and matters with no host town (the load forecast, EMF best practices).

Hits (data/test/wave1/sources/ct_siting_hits.json): one per flagged item and town, board "Connecticut
Siting Council", board_key planning_board, meeting_date = the next scheduled Council meeting or hearing
on the matter, else the decision date, else null (pending, not yet scheduled); source "ct_siting_council".

Site terms: portal.ct.gov's policies allow use of public information; the Council notes it "is not
required to maintain an online data base of Pending Matters" and that the pages may lag the official
file, which the items repeat (`caveat`).

    cd projects/351watch/crawler
    python3 -m watch351.sources.ct_siting [--offline]
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from ..fetch import DEFAULT_CACHE_DIR, FetchError, PoliteFetcher
from .state_feeds import (DEFAULT_OUT, check_out_dir, clean, first_seen, hit_id, iso, load_json,
                          load_state_towns, norm_key, now_iso, snippet_of, write_json)

log = logging.getLogger("ct_siting")

SOURCE = "ct_siting_council"
BASE = "https://portal.ct.gov"
PENDING_URL = BASE + "/csc/1_applications-and-other-pending-matters/pending-matters"
PETITIONS_URL = BASE + "/csc/decisions/petition-lists/petition-list-1500-1999"
DOCKETS_URL = BASE + "/csc/decisions/docketlists/docket-list-nos500-999"
MEETINGS_URL = BASE + "/csc/meetings-and-minutes/v4-template/council-activity"
BACKFILL_FROM = date(2026, 1, 1)     # decided petitions from this date (the first run's backfill)
DOCKET_FROM = 520                    # decided dockets from this number (decisions from 2024 on; date-filtered)
LISTING_MAX_AGE = 20 * 3600
BOARD = "Connecticut Siting Council"
BOARD_KEY = "planning_board"
CAVEAT = ("The Council's web pages are a convenience copy and may lag its official file "
          "(Pending Matters page notice).")

_NUM = re.compile(r"\b(DOCKET|PETITION)\s+NO\.?\s*(\d{3,4}[A-Z]?)\b|\b(TS-[A-Z0-9&-]+-\d{3}-\d{6})\b|"
                  r"\bSUB-PETITION\s+NO\.?\s*([\dA-Z-]+)", re.I)
_STATUS = re.compile(r"\b(Approved(?:\s+in\s+part)?|Denied|Withdrawn|Dismissed|Rejected|Not\s+Approved|"
                     r"Approved\s+with\s+conditions|Declaratory\s+Ruling\s+Surrendered)\b\s*:?\s*"
                     r"(\d{1,2}/\d{1,2}/\d{2,4})", re.I)
_APPLICANT_END = re.compile(r",?\s+(?:joint\s+)?(?:petition|application|request|notice\s+of\s+election|"
                            r"motion|declaratory\s+ruling)\b", re.I)


def parse_mdy(s: str | None) -> date | None:
    s = (s or "").strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%A, %B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


# ------------------------------------------------------------------------------------- towns
class Towns:
    def __init__(self, rows: list[dict]):
        self.idx: dict[str, str] = {}
        for r in rows:
            self.idx[norm_key(r["town"])] = r["town"]
            for a in r.get("aliases", []):
                self.idx.setdefault(norm_key(a), r["town"])
        self.county = {r["town"]: r.get("county") for r in rows}
        names = sorted(self.idx, key=len, reverse=True)
        self.rx = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b", re.I) if names else None

    def resolve(self, name: str) -> str | None:
        n = clean(name).strip(" ,.;")
        outer = re.sub(r"\s*\(.*?\)\s*", " ", n).strip()      # "Stonington (Mystic)", "Washington (New Preston)"
        town = self.idx.get(norm_key(outer))
        if town is None:                                       # "Storrs (Mansfield)": the village outside, town inside
            inner = re.search(r"\(([^)]+)\)", n)
            town = self.idx.get(norm_key(inner.group(1))) if inner else None
        return town

    def in_text(self, text: str) -> list[str]:
        """Known towns named right before ', Connecticut' (the Council's address form)."""
        out = []
        for m in re.finditer(r"([A-Z][A-Za-z .'()-]{2,60}?),?\s+Connecticut\b", text):
            frag = re.sub(r"\s*\(.*?\)", "", m.group(1))
            hits = list(self.rx.finditer(frag)) if self.rx else []
            if not hits and self.rx:                           # "Storrs (Mansfield), Connecticut"
                hits = [h for p in re.findall(r"\(([^)]+)\)", m.group(1)) for h in self.rx.finditer(p)]
            if hits:
                t = self.idx.get(norm_key(hits[-1].group(1)))
                if t and t not in out:
                    out.append(t)
        return out


# ------------------------------------------------------------------------------------ entries
_NUM_START = re.compile(r"^\s*(?:(?:DOCKET|PETITION)\s+NO\.?\s*\d{3,4}|TS-[A-Z0-9&-]+-\d{3}-\d{6}|SUB-PETITION\s+NO\.)",
                        re.I)


def _is_bold(el: NavigableString, stop: Tag) -> bool:
    for p in el.parents:
        if p is stop:
            return False
        if p.name in ("strong", "b") or (p.name == "span" and "bold" in (p.get("style") or "")):
            return True
    return False


def _struck(el: NavigableString, stop: Tag) -> bool:
    for p in el.parents:
        if p is stop:
            return False
        if p.name in ("s", "strike", "del"):
            return True
    return False


def segments(node: Tag) -> list[dict]:
    """Split one <p>/<li> into matters: the Council sometimes puts two petitions in one paragraph,
    separated by <br>. Each segment: text, bold runs (towns are bold), first link. Struck-through text
    (a superseded applicant name) is dropped."""
    segs: list[dict] = []
    cur = None
    bold_run: list[str] = []

    def flush_bold():
        if cur is not None and bold_run:
            t = clean("".join(bold_run))
            if t:
                cur["bold"].append(t)
        bold_run.clear()

    for el in node.descendants:
        if isinstance(el, Tag):
            if el.name in ("a", "strong", "b") and _NUM_START.match(clean(el.get_text(" "))):
                num = _NUM.search(clean(el.get_text(" ")))
                key = num.group(0).upper() if num else ""
                if cur is None or key != cur["key"]:
                    flush_bold()
                    cur = {"key": key, "text": [], "bold": [], "link": None}
                    segs.append(cur)
            if el.name == "a" and el.get("href") and cur is not None and cur["link"] is None:
                cur["link"] = el["href"]
            continue
        if cur is None or not isinstance(el, NavigableString) or isinstance(el, Comment) or _struck(el, node):
            continue
        s = str(el)
        cur["text"].append(s)
        if _is_bold(el, node):
            bold_run.append(s)
        else:
            flush_bold()
    flush_bold()
    for s in segs:
        s["text"] = clean("".join(s["text"]))
    return segs


def parse_entry(node: Tag, towns: Towns, page_url: str) -> dict | None:
    """The first matter in an <li> or <p> (parse_entries gives all of them)."""
    out = parse_entries(node, towns, page_url)
    return out[0] if out else None


def parse_entries(node: Tag, towns: Towns, page_url: str) -> list[dict]:
    out = []
    for seg in segments(node):
        e = _entry(seg, towns, page_url)
        if e:
            out.append(e)
    return out


def _entry(seg: dict, towns: Towns, page_url: str) -> dict | None:
    """One matter (a segment that starts with its number) -> raw entry."""
    text = seg["text"]
    m = _NUM.search(text[:80])
    if not m:
        return None
    if m.group(1):
        kind, num = m.group(1).lower(), m.group(2)
    elif m.group(3):
        kind, num = "tower_share", m.group(3).upper()
    else:
        kind, num = "sub_petition", m.group(4).upper()
    link = urljoin(page_url, seg["link"]) if seg["link"] else page_url
    rest = text[m.end():].lstrip(" –-:")
    rest = re.sub(r"^\(([^)]*)\)\s*[–-]?\s*", "", rest) if kind == "sub_petition" else rest
    am = _APPLICANT_END.search(rest)
    applicant = clean(rest[:am.start()]).strip(" ,") if am and am.start() < 220 else ""
    st = _STATUS.search(rest)
    desc = rest[:st.start()].strip() if st else rest
    desc = re.sub(r"\s*\(\s*Findings of Fact.*$", "", desc).strip()
    status, decided = ("pending", None)
    if st:
        status, decided = st.group(1).lower(), parse_mdy(st.group(2))
    elif re.search(r"\bWITHDRAWN\s+(\d{1,2}/\d{1,2}/\d{2,4})", rest, re.I):
        w = re.search(r"\bWITHDRAWN\s+(\d{1,2}/\d{1,2}/\d{2,4})", rest, re.I)
        status, decided = "withdrawn", parse_mdy(w.group(1))
    host: list[str] = []
    for b in seg["bold"]:
        if _NUM.search(b) or _STATUS.search(b) or re.match(r"(?:Approved|Withdrawn|Denied)\b", b, re.I):
            continue
        for part in re.split(r",|\band\b", b):
            t = towns.resolve(part)
            if t and t not in host:
                host.append(t)
    if not host:
        host = towns.in_text(desc)
    m2 = re.search(r"\(([^)]+)\)", text[m.start():m.end() + 40]) if kind == "sub_petition" else None
    if not host and m2:
        t = towns.resolve(m2.group(1))
        host = [t] if t else []
    return {"kind": kind, "number": num, "applicant": applicant, "description": desc, "towns": host,
            "status": status, "decision_date": iso(decided), "link": link}


def parse_listing(html: str, towns: Towns, page_url: str, section_kinds: bool = False) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    main = soup.find("main") or soup
    out, section = [], None
    for node in main.find_all(["h2", "h3", "h4", "li", "p"]):
        if node.name in ("h2", "h3", "h4"):
            section = clean(node.get_text(" ")).upper()
            continue
        for e in parse_entries(node, towns, page_url):
            if section_kinds and section and "ENFORCEMENT" in section and e["kind"] == "petition":
                e["kind"] = "enforcement"
            e["section"] = section
            out.append(e)
    # an <li> inside a <p> (or the reverse) yields the same matter twice: keep the first
    seen, uniq = set(), []
    for e in out:
        if (e["kind"], e["number"]) not in seen:
            seen.add((e["kind"], e["number"]))
            uniq.append(e)
    return uniq


# ------------------------------------------------------------------------------ classification
def technology(desc: str) -> tuple[list[str], str, float | None]:
    """(topics, technology label, MW) for a matter's description."""
    d = desc.lower()
    mw = None
    m = re.search(r"(\d+(?:\.\d+)?)[\s-]*(megawatt|mw)\b", d)
    if m:
        mw = float(m.group(1))
    else:
        k = re.search(r"(\d+(?:\.\d+)?)[\s-]*(kilowatt|kw)\b", d)
        if k:
            mw = round(float(k.group(1)) / 1000, 3)
    topics, label = [], []
    if re.search(r"\bsolar\b|photovoltaic", d):
        topics.append("solar"); label.append("solar")
    if re.search(r"batter(?:y|ies)\s+(?:energy\s+)?storage|energy\s+storage|\bbess\b", d):
        topics.append("battery_storage"); label.append("battery storage")
    if re.search(r"data\s+cent(?:er|re)|crypto", d):
        topics.append("data_center"); label.append("data center")
    if re.search(r"fuel\s+cell", d):
        topics.append("clean_energy_siting"); label.append("fuel cell")
    # a line or substation project (not a generating facility's interconnection to one)
    # (telecom antennas mounted on a transmission structure are a telecom matter, not a line project)
    if not label and re.search(r"transmission\s+line|substation|switching\s+station|\bkv\b|kilovolt", d) and \
            not re.search(r"antenna|telecommunications?|wireless", d):
        topics.append("clean_energy_siting")
        label.append("transmission / substation")
    if not label and re.search(r"generating\s+facility|power\s+(?:plant|station)|trash-to-energy|"
                               r"\bhydro|\bwind\s+(?:turbine|farm|energy|project|generat)|biomass|generating\s+station", d):
        topics.append("clean_energy_siting"); label.append("other generation")
    # (a transmission rebuild's "steel monopole structures" are not a telecommunications tower)
    if re.search(r"telecommunications?\s+facilit|wireless|antenna|cell(?:ular)?\s+tower", d) or \
            (re.search(r"tower|monopole", d) and not re.search(r"transmission|\bkv\b|kilovolt", d)):
        topics.append("wireless_telecom")
        label.append("small wireless facility" if "small wireless" in d else "telecommunications tower/facility")
    return topics, ", ".join(label) or "other", mw


def flag(entry: dict, topics: list[str]) -> tuple[bool, str]:
    if not entry["towns"]:
        return False, "no host town (statewide matter)"
    if entry["kind"] == "tower_share":
        return False, "tower share at an existing tower (no new structure)"
    if entry["kind"] == "sub_petition":
        return False, "statewide maintenance sub-petition"
    if not topics:
        return False, "no siting subject"
    return True, ", ".join(topics)


# ------------------------------------------------------------------------------- matter pages
def matter_page(fetcher: PoliteFetcher, url: str) -> dict:
    """Received date and hearing dates from a petition's or docket's own page."""
    with fetcher.purpose("listing"):
        r = fetcher.get(url, max_age=LISTING_MAX_AGE)
    if not r.ok:
        raise FetchError(f"HTTP {r.status}: {url}")
    text = clean((BeautifulSoup(r.text, "lxml").find("main") or BeautifulSoup(r.text, "lxml")).get_text(" "))
    rec = re.search(r"\((?:recd|received)\.?\s*(\d{1,2}/\d{1,2}/\d{2,4})\)", text, re.I)
    hearings = set()
    for m in re.finditer(r"Hearing\s+Program,?\s*(\d{1,2}/\d{1,2}/\d{2,4})", text, re.I):
        d = parse_mdy(m.group(1))
        if d:
            hearings.add(d)
    for m in re.finditer(r"([A-Z][a-z]+ \d{1,2}, 20\d\d)\s+(?:Continued\s+)?(?:Evidentiary\s+)?(?:Public\s+)?Hearing",
                         text):
        d = parse_mdy(m.group(1))
        if d:
            hearings.add(d)
    return {"received_date": iso(parse_mdy(rec.group(1))) if rec else None,
            "hearing_dates": sorted(iso(d) for d in hearings)}


def pdf_text(fetcher: PoliteFetcher, url: str) -> str:
    with fetcher.purpose("document"):
        r = fetcher.get(url)
    if not r.ok or not r.is_pdf:
        raise FetchError(f"not a PDF ({r.status}): {url}")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
        tf.write(r.body)
        tf.flush()
        out = subprocess.run(["pdftotext", "-layout", tf.name, "-"], capture_output=True, timeout=120)
    return out.stdout.decode("utf-8", "replace")


def meeting_agenda(fetcher: PoliteFetcher) -> tuple[dict, list[str]]:
    """{matter number: [(date, action, kind)]} from the current Council meeting agenda PDF."""
    errors: list[str] = []
    events: dict[str, list] = {}
    with fetcher.purpose("listing"):
        r = fetcher.get(MEETINGS_URL, max_age=LISTING_MAX_AGE)
    if not r.ok:
        return events, [f"meetings page HTTP {r.status}"]
    soup = BeautifulSoup(r.text, "lxml")
    for a in (soup.find("main") or soup).find_all("a", href=True):
        label = clean(a.get_text(" "))
        if not re.search(r"Meeting Agenda for", label, re.I):
            continue
        md = parse_mdy(re.sub(r"^.*Agenda for\s+", "", label))
        try:
            text = pdf_text(fetcher, urljoin(MEETINGS_URL, a["href"]))
        except FetchError as e:
            errors.append(str(e)[:200])
            continue
        flat = clean(text)
        main_part, _, upcoming = flat.partition("Upcoming Calendar Events")
        for m in re.finditer(r"\b\d{1,2}\.\s+((?:DOCKET|PETITION)\s+NO\.\s*\d{3,4}|TS-[A-Z0-9&-]+-\d{3}-\d{6}|"
                             r"SUB-PETITION\s+NO\.\s*[\dA-Z-]+)(.*?)(?=\s\d{1,2}\.\s+[A-Z(]|$)", main_part):
            key = _key(m.group(1))
            action = clean(m.group(2))[-80:]
            act = re.search(r"(Decision|Draft Findings of Fact|Findings of Fact|Annual Review|Motion[^.]*)\.?\s*$",
                            action)
            events.setdefault(key, []).append((iso(md), act.group(1) if act else "on agenda", "meeting"))
        for m in re.finditer(r"((?:Docket|Petition)\s+No\.\s*\d{3,4}),\s*(\w+day,\s+[A-Z][a-z]+ \d{1,2}, 20\d\d),"
                             r"([^•]*?)(?=•|$)", upcoming):
            d = parse_mdy(m.group(2).split(", ", 1)[1])
            what = clean(m.group(3))
            kind = "hearing" if re.search(r"hearing", what, re.I) else "meeting"
            events.setdefault(_key(m.group(1)), []).append((iso(d), what[:120], kind))
    return events, errors


def _key(s: str) -> str:
    s = clean(s).upper()
    m = re.search(r"(DOCKET|PETITION)\s+NO\.?\s*(\d{3,4}[A-Z]?)", s)
    if m:
        return f"{m.group(1).lower()}:{m.group(2)}"
    m = re.search(r"SUB-PETITION\s+NO\.?\s*([\dA-Z-]+)", s)
    if m:
        return f"sub_petition:{m.group(1)}"
    return f"tower_share:{s.strip()}"


def entry_key(e: dict) -> str:
    k = "petition" if e["kind"] in ("petition", "enforcement") else e["kind"]
    return f"{k}:{e['number']}"


def docket_decision(fetcher: PoliteFetcher, link: str, node_html: str) -> tuple[date | None, str, str | None]:
    """(decision date, status, source) of a decided docket. The docket's own page lists the decision under
    FINAL DECISION ("Council's Final Decision Documents, 08/19/22", "Council Decision Documents (Denial),
    02/06/26"): that date and outcome are used. Without it, the date in the Decision and Order's file name
    (do551_do_09_03_26, d546-do__04022026). The Decision and Order's text is not used: the only date it states
    is the service list's ("Service List, dated May 29, 2025"), not the decision's (round-1 hand check)."""
    try:
        with fetcher.purpose("listing"):
            r = fetcher.get(link, max_age=7 * 24 * 3600)
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            text = (soup.find("main") or soup).get_text("\n", strip=True)
            i = text.find("FINAL DECISION")
            if i >= 0:
                block = text[i:i + 600]
                m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", block)
                if m:
                    head = block[:m.end()]
                    status = "denied" if re.search(r"\bDenial\b|\bDenied\b|\bDeny\b", head, re.I) else "approved"
                    return parse_mdy(m.group(1)), status, "docket page"
    except FetchError:
        pass
    soup = BeautifulSoup(node_html, "lxml")
    for a in soup.find_all("a", href=True):
        if not re.search(r"decision\s+and\s+order", a.get_text(" "), re.I):
            continue
        name = a["href"].split("?")[0].rsplit("/", 1)[-1]
        for rx, fmt in ((r"(\d{2})_(\d{2})_(\d{2})(?!\d)", "%m%d%y"), (r"(?<!\d)(\d{2})(\d{2})(20\d{2})(?!\d)", "%m%d%Y"),
                        (r"(?<!\d)(\d{2})(\d{2})(\d{2})(?!\d)", "%m%d%y")):
            m = re.search(rx, name)
            if m:
                try:
                    return datetime.strptime("".join(m.groups()), fmt).date(), "decided", "decision file name"
                except ValueError:
                    pass
    return None, "decided", None

# --------------------------------------------------------------------------------------- build
def run(fetcher: PoliteFetcher, out_dir: Path, today: date | None = None, backfill_from: date = BACKFILL_FROM,
        docket_from: int = DOCKET_FROM) -> dict:
    check_out_dir(out_dir)
    started = now_iso()
    today = today or date.today()
    towns = Towns(load_state_towns("CT"))
    ledger_p = out_dir / "ct_siting_ledger.json"
    ledger = load_json(ledger_p, {})
    errors: list[str] = []
    entries: dict[str, dict] = {}

    # 1. pending matters
    with fetcher.purpose("listing"):
        r = fetcher.get(PENDING_URL, max_age=LISTING_MAX_AGE)
    if not r.ok:
        raise FetchError(f"pending matters HTTP {r.status}")
    for e in parse_listing(r.text, towns, PENDING_URL, section_kinds=True):
        e["listed_on"] = "pending"
        entries[entry_key(e)] = e
    # 2. decided petitions (1500+) from BACKFILL_FROM
    with fetcher.purpose("listing"):
        r = fetcher.get(PETITIONS_URL, max_age=LISTING_MAX_AGE)
    if r.ok:
        for e in parse_listing(r.text, towns, PETITIONS_URL):
            if e["kind"] != "petition" or not e["decision_date"] or e["decision_date"] < backfill_from.isoformat():
                continue
            k = entry_key(e)
            if k in entries:    # pending page wins for live matters; the decision list adds the outcome
                entries[k].update({x: e[x] for x in ("status", "decision_date") if e[x]})
            else:
                e["listed_on"] = "petition_list"
                entries[k] = e
    else:
        errors.append(f"petition list HTTP {r.status}")
    # 3. decided dockets (500+) from DOCKET_FROM
    with fetcher.purpose("listing"):
        r = fetcher.get(DOCKETS_URL, max_age=LISTING_MAX_AGE)
    if r.ok:
        soup = BeautifulSoup(r.text, "lxml")
        main = soup.find("main") or soup
        for node, e in ((n, e) for n in main.find_all(["p", "li"]) for e in parse_entries(n, towns, DOCKETS_URL)):
            if e["kind"] != "docket" or int(re.sub(r"\D", "", e["number"]) or 0) < docket_from:
                continue
            k = entry_key(e)
            if k in entries and entries[k].get("listed_on") == "pending":
                continue
            if e["status"] == "pending":       # decided: date and outcome from the docket's own page
                d, status, src = docket_decision(fetcher, e["link"], str(node))
                e["status"], e["decision_date"], e["decision_source"] = status, iso(d), src
            if e["decision_date"] and e["decision_date"] < backfill_from.isoformat():
                continue
            e["listed_on"] = "docket_list"
            entries.setdefault(k, e)
    else:
        errors.append(f"docket list HTTP {r.status}")
    # 4. pending matters' own pages: received date, docket hearings
    for k, e in entries.items():
        if e.get("listed_on") != "pending" or e["kind"] not in ("petition", "docket", "enforcement") \
                or not e["link"].startswith(BASE + "/csc/"):
            continue
        try:
            e.update(matter_page(fetcher, e["link"]))
        except FetchError as ex:
            errors.append(f"{k}: {ex}"[:200])
    for e in entries.values():
        if e["kind"] == "tower_share" and not e.get("received_date"):
            m = re.search(r"-(\d{6})$", e["number"])
            e["received_date"] = iso(datetime.strptime(m.group(1), "%y%m%d").date()) if m else None
    # 5. the current Council meeting agenda: matters for decision, upcoming hearings
    events, errs = meeting_agenda(fetcher)
    errors += errs
    for k, evs in events.items():
        if k in entries:
            entries[k].setdefault("events", []).extend(
                {"date": d, "what": w, "kind": kd} for d, w, kd in evs)

    items = []
    for k, e in entries.items():
        topics, tech, mw = technology(e["description"])
        relevant, reason = flag(e, topics)
        upcoming = sorted((ev for ev in e.get("events", []) if ev["date"] and ev["date"] >= today.isoformat()),
                          key=lambda ev: ev["date"])
        hearings_ahead = [h for h in e.get("hearing_dates", []) if h >= today.isoformat()]
        if e["status"] == "withdrawn":
            upcoming, hearings_ahead = [], []
        if upcoming:
            when, kind = upcoming[0]["date"], upcoming[0]["kind"]
        elif hearings_ahead:
            when, kind = hearings_ahead[0], "hearing"
        elif e.get("decision_date"):
            when, kind = e["decision_date"], "decision"
        else:
            when, kind = None, "pending"
        for town in e["towns"] or [None]:
            key = f"{k}|{town}|{e['status']}|{when}"
            items.append({
                "kind": e["kind"], "number": e["number"], "town": town,
                "county": towns.county.get(town) if town else None, "host_towns": e["towns"],
                "applicant": e["applicant"], "facility": e["description"], "technology": tech, "mw": mw,
                "status": e["status"], "received_date": e.get("received_date"),
                "hearing_dates": e.get("hearing_dates", []), "events": e.get("events", []),
                "decision_date": e.get("decision_date"), "date": when, "date_kind": kind,
                "link": e["link"], "listed_on": e.get("listed_on"),
                "siting_relevant": relevant and town is not None, "topics": topics if relevant else [],
                "flag_reason": reason, "first_seen": first_seen(ledger, key, started), "caveat": CAVEAT,
            })
    items.sort(key=lambda i: (i["date"] or "9999", i["number"], i["town"] or ""), reverse=True)
    hits = [to_hit(i) for i in items if i["siting_relevant"]]
    write_json(ledger_p, ledger)
    gen = now_iso()
    write_json(out_dir / "ct_siting_items.json", {"generated": gen, "source": SOURCE,
                                                  "listing_urls": [PENDING_URL, PETITIONS_URL, DOCKETS_URL, MEETINGS_URL],
                                                  "backfill_from": backfill_from.isoformat(), "items": items})
    write_json(out_dir / "ct_siting_hits.json", {"generated": gen, "source": SOURCE, "hits": hits})
    report = {
        "source": SOURCE, "started": started, "finished": now_iso(), "matters": len(entries),
        "by_listing": dict(Counter(e.get("listed_on") for e in entries.values())),
        "items": len(items), "flagged": sum(i["siting_relevant"] for i in items),
        "topics": dict(Counter(t for i in items for t in i["topics"]).most_common()),
        "no_town": sorted(f"{i['kind']} {i['number']}" for i in items if i["town"] is None),
        "errors": errors,
        "network": {"requests": fetcher.stats["network"], "cache_hits": fetcher.stats["cache"],
                    "errors": fetcher.stats["errors"], "robots_blocked": fetcher.stats["robots_blocked"]},
    }
    write_json(out_dir / "runs" / f"ct_siting_{started[:10]}.json", report)
    return report


def to_hit(item: dict) -> dict:
    label = {"docket": "Docket", "petition": "Petition", "enforcement": "Enforcement (petition)",
             "tower_share": "Tower share", "sub_petition": "Sub-petition"}[item["kind"]]
    when = {"hearing": "Hearing", "meeting": "Council meeting", "decision": item["status"].capitalize(),
            "pending": "Pending"}[item["date_kind"]]
    mw = f" ({item['mw']:g} MW)" if item.get("mw") else ""
    snippet = snippet_of(f"{label} {item['number']}, {item['town']}: {item['applicant'] or 'applicant'} -"
                         f" {item['technology']}{mw}.", f"{when} {item['date']}." if item["date"] else
                         "Pending; no Council date set yet.", item["facility"])
    return {
        "id": hit_id(item["link"], snippet),
        "state": "CT", "town": item["town"], "county": item.get("county"),
        "board": BOARD, "board_key": BOARD_KEY, "meeting_date": item["date"], "topics": item["topics"],
        "snippet": snippet, "source_url": item["link"],
        "listing_url": PENDING_URL if item["listed_on"] == "pending" else
        (PETITIONS_URL if item["listed_on"] == "petition_list" else DOCKETS_URL),
        "document_title": f"{label} No. {item['number']}" if item["kind"] in ("docket", "petition", "enforcement")
        else f"{label} {item['number']}",
        "text_source": "html", "first_seen": item["first_seen"], "source": SOURCE,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--backfill-from", type=date.fromisoformat, default=BACKFILL_FROM,
                   help="decided petitions / dockets from this date (YYYY-MM-DD)")
    p.add_argument("--docket-from", type=int, default=DOCKET_FROM, help="decided dockets from this number")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    rep = run(PoliteFetcher(a.cache_dir, offline=a.offline), a.out_dir, backfill_from=a.backfill_from,
              docket_from=a.docket_from)
    print(f"CT Siting Council: {rep['matters']} matters {rep['by_listing']}, {rep['items']} items, "
          f"{rep['flagged']} flagged {rep['topics']}; errors {len(rep['errors'])}; network {rep['network']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
