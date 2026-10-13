#!/usr/bin/env python3
"""Trending: rank upcoming local siting stories and give each a plain headline.

    python3 trending.py                        # writes data/trending.json
    python3 trending.py --today 2026-10-12     # fix "today" (default: today in Boston)
    python3 trending.py --print 40             # also print the top 40 as a reader would see them
    python3 trending.py --copy copy.txt        # headlines, deks and reasons, one per line, for slop_lint.py
    python3 trending.py --print 15 --towns MA:Carver --topics solar   # preview the page's re-ranking

Inputs (data/): hits_current.json (required), search/<ST>/*.jsonl (agenda text), state/hits_archive/
(older hits, for "first in this town"), tracker.json, ag_decisions.json, and neighbors.json for the
personalization preview. Standard library only. The output contract, the weights and the page's
re-ranking formula are in ARCHITECTURE.md under "data/trending.json".

Every headline, dek and reason is built from fixed templates filled with words found in the agenda
text (names, addresses, sizes, dates). Nothing is paraphrased by a model, and a template is only used
when the text holds the fact it states; otherwise a plainer template is used.
"""

import argparse
import glob
import hashlib
import json
import os
import re
from urllib.parse import unquote
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TZ = ZoneInfo("America/New_York")

# ============================================================================ weights
# score = (SUBJECT_POINTS x ACTION_MULT + bonuses x routine - vague) x timing, where
#   bonuses = scale + first + momentum + new + tracker + ag, and routine = min(1, ACTION_MULT / 0.8).
# Tuned by reading the ranked list; see research_notes/Design/trending_review.md. Documented in ARCHITECTURE.md.

SUBJECT_POINTS = {
    "data_center": 10.0,
    "battery_storage": 8.0,
    "moratorium": 7.0,          # floor for a moratorium or ban on any siting subject
    "solar_large": 6.0,         # ground-mounted, large-scale, MW, acres, dual-use
    "wind": 5.0,
    "clean_energy_siting": 5.0,  # consolidated permit, clean energy facility bylaws
    "zoning_amendment": 4.0,
    "40b_comprehensive_permit": 3.5,
    "solar": 3.5,               # rooftop, carport, municipal arrays, passing mentions
    "wireless_telecom": 3.0,
    "wetlands_filing": 1.5,
    "general_bylaw": 1.0,       # tagged zoning_amendment but no zoning in the text (snow removal, dogs)
    "other": 1.0,               # moratoria on PFAS, road openings, crypto kiosks
}

ACTION_MULT = {
    "moratorium": 1.6,       # +0.1 more when it is a vote, a hearing or a Town Meeting article; 1.2 when tentative
    "ban": 1.6,
    "adopt": 1.5,            # resolution adopting a bylaw, ordinance or local law
    "town_meeting": 1.4,     # article on a Town Meeting warrant ("To see if the Town will vote")
    "bylaw_hearing": 1.4,
    "project_hearing": 1.3,
    "rezoning": 1.2,
    "warrant_review": 1.1,   # a select board or council reviewing warrant articles
    "filing": 1.0,           # MassDEP wetlands filing
    "bylaw_draft": 1.0,
    "project": 1.0,          # application, extension or review without a hearing
    "deal": 0.8,             # lease, contract, easement or tax agreement
    "process": 0.7,          # consolidated permit administration
    "discussion": 0.55,
    "mention": 0.5,
    "continuance": 0.35,
    "minutes": 0.35,         # narrative minutes of an earlier meeting included in the packet
    "withdrawn": 0.25,
    "cancelled": 0.15,
}
STRONG_ACTION_BONUS = 0.1
TENTATIVE_MULT = 1.2         # "AI data center moratorium?" in a list of topics
CONSERVATION_PROJECT = 0.85  # a Conservation Commission project item is a wetlands review only
PROJECT_ACTIONS = ("project_hearing", "project", "filing", "deal", "continuance", "withdrawn", "rezoning")

# timing multiplier by days until the meeting; past meetings drop off
TIMING = [(1, 1.5), (7, 1.35), (14, 1.2), (30, 0.9), (60, 0.7)]
TIMING_FAR = 0.5
TIMING_UNDATED = 0.75      # upcoming Town Meeting warrant without a date we can read
TIMING_FILING = 0.8        # MassDEP filing in the last FILING_DAYS days
FILING_DAYS = 14
LOOKBACK_DAYS = 60         # past hits within this window still add momentum

FIRST_POINTS = {"data_center": 2.0, "battery_storage": 2.0, "moratorium": 2.0, "wind": 1.5,
                "clean_energy_siting": 1.0, "solar": 1.0, "40b_comprehensive_permit": 1.0,
                "wireless_telecom": 1.0}
FIRST_MIN_HISTORY_DAYS = 60   # claim "first time" only with this much earlier agenda history for the town
MOMENTUM_BOARD = 2.5          # per extra board (cap MOMENTUM_CAP)
MOMENTUM_TOWN = 3.0           # per extra town
MOMENTUM_MEETING = 1.0        # per extra meeting date when the board count does not grow
MOMENTUM_CAP = 3
NEW_POINTS = 1.0
NEW_HOURS = 72
TRACKER_POINTS = 1.0         # the town already voted on this subject (tracker.json)
AG_POINTS = 1.5
AG_DAYS = 365
VAGUE_PENALTY = 1.5
ROUTINE_BONUS_FLOOR = 0.8   # bonuses scale by ACTION_MULT / 0.8 when the lead's multiplier is below 0.8
TOP_N = 100

# The page re-ranks in the browser: score x (1 + 2*in_my_towns + 1*in_neighbor_towns) x (1 + 0.5*topic_match)
PERSONALIZE = {"in_my_towns": 2.0, "in_neighbor_towns": 1.0, "topic_match": 0.5}

# ============================================================================ text helpers

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NUM = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july",
                                              "august", "september", "october", "november", "december"])}
_TRANS = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "’": "'", "‘": "'",
                        "“": '"', "”": '"', " ": " ", "​": "", "﻿": "", " ": " ",
                        " ": " ", " ": " ", "‎": "", "\xad": ""})


def norm(s):
    s = re.sub(r"[-]", " • ", (s or "").translate(_TRANS))  # symbol-font bullets from PDFs
    return re.sub(r"\s+", " ", s).strip()


def short_date(d):
    return f"{MONTHS[d.month - 1]} {d.day}"


def long_date(d):
    return f"{d.strftime('%A')}, {short_date(d)}"


def slugify(name):
    return re.sub(r"\s+", "-", name.lower().replace("'", "").replace("’", ""))


def town_path(state, town):
    return f"/{state.lower()}/{slugify(town)}"


def parse_date(s):
    try:
        return date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


def parse_ts(s):
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None


def first_cap(s):
    return s[:1].upper() + s[1:] if s else s


def with_article(phrase):
    """'a one-year moratorium', 'an 87-unit plan', 'an 18-month moratorium', 'a 40B request'."""
    an = re.match(r"(?:[aeiAEI]|[oO](?!ne\b|ne-)|[uU](?!ni|s[aeu])|8|11\b|11-|18\b|18-)", phrase)
    return ("an " if an else "a ") + phrase


def tidy_caps(s):
    """'300 WELLESLEY ST' -> '300 Wellesley St'; leaves mixed case alone."""
    if s.upper() == s and re.search(r"[A-Z]{3}", s):
        return " ".join(w if re.search(r"\d", w) or w in ("LLC", "II", "III", "IV") else w.capitalize()
                        for w in s.split())
    return s


# ============================================================================ subjects and actions

SUBJECT_ORDER = ["data_center", "battery_storage", "solar", "wind", "clean_energy_siting", "zoning_amendment",
                 "40b_comprehensive_permit", "wireless_telecom", "wetlands_filing"]
SITING = {"data_center", "battery_storage", "solar", "solar_large", "wind", "clean_energy_siting"}

SUBJECT_RE = {
    "data_center": re.compile(r"\bdata[\s-]*(?:storage\s+|processing\s+)?cent(?:er|re)s?\b|\bdata\s+storage\s+facilit"
                              r"|\bcrypto(?:currency)?\s+mining\b|\bhyperscale", re.I),
    "battery_storage": re.compile(r"\bbatter(?:y|ies)\b|\bBESS\b|\bB\.E\.S\.S\b|\benergy\s+storage\b", re.I),
    "solar": re.compile(r"\bsolar\b|\bphotovoltaic\b|\bPV\b", re.I),
    "wind": re.compile(r"\bwind\s+(?:energy|turbines?|facilit|farm|power)", re.I),
    "clean_energy_siting": re.compile(r"\bconsolidated\s+(?:local\s+)?permit|\bclean\s+energy\s+(?:infrastructure|facilit|siting)"
                                      r"|\bSCEI\w*|\b225\s+CMR\s+29|\bsiting\s+and\s+permitting", re.I),
    "zoning_amendment": re.compile(r"\bzon(?:ing|e)\b|\brezon|\bby-?laws?\b|\bordinance", re.I),
    "40b_comprehensive_permit": re.compile(r"\b40\s?B\b|\bcomprehensive\s+permit", re.I),
    "wireless_telecom": re.compile(r"\bcell(?:ular)?\s+(?:tower|facilit|antenna)|\bwireless\s+(?:communication|telecom|facilit)"
                                   r"|\bmonopole|\btelecommunications?\s+(?:facility|tower|antenna)|\bantennas?\b|\bsmall\s+cell", re.I),
    "moratorium": re.compile(r"\bmoratori(?:um|a|ums)\b", re.I),
    "wetlands_filing": re.compile(r"\bnotice\s+of\s+intent|\bNOI\b|\bwetland", re.I),
}
NON_SITING_MORATORIUM = re.compile(r"PFAS|road|street|curb|trench|pavement|excavat|shutoff|shut-off|kiosk|crypto ATM"
                                   r"|marijuana|cannabis|water connection|sewer|residential development|growth", re.I)

LARGE_SOLAR = re.compile(r"large[\s-]*scale|ground[\s-]*mount|utility[\s-]*scale|solar\s+(?:farm|field|array)|\bMW\b|"
                         r"megawatt|\bacres?\b|dual[\s-]*use|agrivoltaic|photovoltaic\s+(?:installation|facilit|system)",
                         re.I)
SMALL_SOLAR = re.compile(r"carport|canopy|roof[\s-]*(?:top|mounted)|rooftop|residential\s+solar|space\s+solar|"
                         r"school|w-Solar|solar\s+(?:light|panel)s?\s+(?:for|on)\b", re.I)

CANCEL_RE = re.compile(r"\bcancel(?:l?ed|lation)\b", re.I)
WITHDRAWN_RE = re.compile(r"\bwithdr[ae]wn?\b|\bwithdrawal\b|\brequest(?:ed|s)?\s+to\s+withdraw", re.I)
CONTINUANCE_RE = re.compile(
    r"request(?:ed|s|ing)?\s+(?:a\s+|to\s+)?(?:continuance|continue)|continuance\s+(?:to|until)|"
    r"(?<!be )continued\s+(?:to|until)\s+(?:the\s+)?(?:\w+\s+)?\d|to\s+be\s+continued|\bpostpon", re.I)
CONTINUED_HEARING_RE = re.compile(r"continued\s+(?:public\s+)?hearing|hearing\s+cont(?:'d|inued)?|cont'd|"
                                  r"\(?continued\s+from\b", re.I)
HEARING_RE = re.compile(r"\bpublic\s+hearings?\b|\bhearings?\b|\bPH\b|\bnotice\s+of\s+(?:hybrid\s+|remote\s+)?public", re.I)
VOTE_RE = re.compile(r"\bvote\s+(?:on|to)\b|\bdiscuss(?:ion)?\s+and\s+(?:possible\s+)?vote|\bact\s+on\b|"
                     r"\bconsider\s+and\s+act|\bpossible\s+vote", re.I)
DRAFT_RE = re.compile(r"\bdraft\b", re.I)
TM_ARTICLE_RE = re.compile(r"to\s+see\s+if\s+the\s+(?:town|city)\s+will\s+vote|\bwarrant\s+articles?\b", re.I)
ADOPT_RE = re.compile(r"\badopt(?:ing|ion\s+of)\s+(?:a\s+|the\s+)?(?:local\s+law|(?:new\s+)?(?:zoning\s+)?(?:by-?law|ordinance))"
                      r"|\badopting\s+local\s+law|\brecommend\s+adoption", re.I)
BYLAW_RE = re.compile(r"\bby-?laws?\b|\bordinances?\b|\blocal\s+law\b|\bzoning\s+(?:amendment|code|text|map)|"
                      r"\bamend(?:ing|ment|ments|s)?\b[^.;]{0,60}\b(?:zoning|by-?law|ordinance|code)\b|"
                      r"\bregulations?\s+for\b|\bdefinitions?\b|\bTable\s+of\s+(?:Principal\s+)?Uses", re.I)
REZONE_RE = re.compile(r"\brezon(?:e|ing)\b|\bzone\s+change\b|\bzoning\s+map\b|\bchange\s+the\s+zoning\s+district", re.I)
DEAL_RE = re.compile(r"\blease\b|\bcontract\b|\baward\b|\beasement\b|\bPILOT\b|payment\s+in\s+lieu|host\s+community|"
                     r"community\s+benefits|\btaxation\b|\bpower\s+purchase|\bnet\s+metering", re.I)
DISCUSS_RE = re.compile(r"\bdiscuss(?:ion)?\b|\bupdate\b|\breview\b|\bpresentation\b|\bworkshop\b|\bbusiness\s+session\b", re.I)
BAN_RE = re.compile(r"\bprohibit(?:s|ed|ing|ion)?\b|\bban(?:s|ning|ned)?\b", re.I)
PETITION_RE = re.compile(r"\bpetition", re.I)

MINUTES_STRONG = re.compile(r"\bmoved\s+to\s+(?:approve|adjourn|accept|close|continue|recommend|table|grant|deny|amend|ordain|refer)\b|"
                            r"\bmade\s+a\s+motion\b|\bseconded\s+by\b|\bmotion\s+(?:carried|passed)|"
                            r"\bVOTE:\s*\d|\bunanimous(?:ly)?\b|\bso\s+voted\b|\bcarried\s+by\b|\bA\s+true\s+record\b|"
                            r"\bmotion\s+made\s+by\b", re.I)
MINUTES_NARR = re.compile(r"\b(?:said|stated|noted|explained|inquired|questioned|asked|reported|described|expressed|"
                          r"spoke|went\s+over|thinks?|believes?|suggested|indicated)\b", re.I)
PRONOUN = re.compile(r"\b(?:he|she|they|his|her|him)\b", re.I)
PLACE_WORDS = re.compile(r"Town\s+Hall|City\s+Hall|Senior\s+Center|Chambers|Municipal\s+(?:Complex|Building|Center)|"
                         r"Memorial\s+Hall|Library|Police\s+Department|Fire\s+(?:Station|Department)|\bRoom\b|Building\b|"
                         r"Inn\b|Suites?\b|School\b|Center\b|Office\b|P\.?O\.?\s+Box", re.I)


def topic_family(subject):
    if subject in SITING:
        return "data" if subject == "data_center" else "energy"
    if subject in ("zoning_amendment", "general_bylaw"):
        return "zoning"
    return subject


# ============================================================================ locating an agenda item

SECTION_PAT = (r"(?<!\S)(?:PUBLIC HEARINGS?|CONTINUED (?:PUBLIC )?HEARINGS?|PUBLIC MEETINGS?|NEW BUSINESS|"
               r"OLD BUSINESS|UNFINISHED BUSINESS|OTHER BUSINESS|GENERAL BUSINESS|BUSINESS SESSION|ADJOURN\w*|"
               r"MINUTES|APPROVAL OF MINUTES|CORRESPONDENCE|MODIFICATIONS|DISCUSSION(?: ITEMS)?|ACTION ITEMS|"
               r"STAFF UPDATES|REPORTS|CONSENT AGENDA|INFORMAL DISCUSSION|PLANNING BOARD DISCUSSION)\b")
BOUNDARY_RES = [
    re.compile(r"(?<!\S)\d{1,2}[.)]\s+(?=[A-Z(\"'])"),
    re.compile(r"(?<=[.:;)]\s)[A-Ha-h][.)]\s+(?=[A-Z(])|(?<=\d\s)[A-DF-MO-RT-VX-Z]\.\s+(?=[A-Z][a-z])"),
    re.compile(r"(?<!\S)[ivx]{1,4}\.\s+(?=[A-Z])"),
    re.compile(r"[•◼▪●○◦■□►➢✓]|(?<=\s)\u2212(?=\s)"),
    re.compile(r"(?<=\s)(?:e|o|e¢|¢|«)\s+(?=[A-Z])"),
    re.compile(r"(?<!\S)\d{1,2}:\d{2}\s*(?:[AaPp]\.?\s?[Mm]\.?)?(?=\s)"),
    re.compile(r"(?<!\S)(?:ARTICLE|Article)\s+\d+\b"),
    re.compile(r"(?<!\S)\d{2}-\d{3}(?=\s+[A-Z])"),
    re.compile(r"(?<!\S)(?:NB|OB|PH)-\d+\b"),
    re.compile(r"(?<!\S)(?:Ordinance|Resolution|Order|Measure)\s+(?:No\.\s*)?#?\d{2,4}-\d+"),
    re.compile(r"(?<!\S)Approval\s+of\s+(?:the\s+)?(?:meeting\s+)?minutes", re.I),
    re.compile(r"…"),  # data/search joins text cut at TEXT_CAP to later snippets with " … "
    re.compile(SECTION_PAT),
]
DOC_HEARING_RE = re.compile(r"will\s+hold\s+(?:a\s+)?(?:\w+\s+){0,2}public\s+hearings?|notice\s+of\s+(?:\w+\s+){0,2}public\s+hearing|"
                            r"following\s+(?:petitions|applications|matters)\s+will\s+be\s+heard|"
                            r"public\s+hearings?\s+on\s+the\s+following|\A.{0,150}?\bpublic\s+hearings?\b", re.I)
SECTION_RE = re.compile(SECTION_PAT + r"|(?<!\S)\d{1,2}\.\s+(?:Public\s+|Continued\s+)?Hearings?\b|(?<!\S)(?:Public Hearings?|Continued Public Hearings?|Public Hearing Cont'd|"
                        r"New Business|Old Business|Unfinished Business|Other Business|Discussion Items?|"
                        r"Business Session)\s*:")
HEARING_SECTIONS = re.compile(r"hearing", re.I)


def section_before(text, pos, reach=1500):
    """The last section header (PUBLIC HEARINGS, NEW BUSINESS...) before pos, or ''."""
    last = None
    for m in SECTION_RE.finditer(text, max(0, pos - reach), pos):
        last = m
    return last.group(0) if last else ""
HEADER_RE = re.compile(r"(public\s+hearings?(?:\s+cont\S*|\s+continued)?|continued\s+(?:public\s+)?hearings?|"
                       r"public\s+meetings?|new\s+business|old\s+business|unfinished\s+business|other\s+business|"
                       r"approval\s+of\s+minutes|minutes|discussion(?:\s+items)?|action\s+items|warrant\s+articles?|"
                       r"business\s+session)\s*:?\s*(?:\(?[^()]{0,40}\)?)?\s*$", re.I)
ABBREV = {"st", "rd", "ave", "no", "inc", "corp", "mr", "ms", "mrs", "dr", "sec", "art", "approx", "co", "ln", "blvd",
          "jr", "sr", "esq", "vs", "etc", "u.s", "m.g.l", "g.l", "c", "s", "p", "pp", "ch", "mass", "dept", "hwy",
          "rte", "mt", "ft", "sq", "lot", "map", "vol", "pg", "a.m", "p.m", "d/b/a", "o/b/o", "fl", "flr", "e.g", "i.e"}
FOLLOW_ON = re.compile(r"(?:The\s+(?:property|site|subject|applicant|proposed|project|parcel|owner|request)|This\b|It\b|"
                       r"Located|located|Construction|Applicant)")


NOT_ITEM_NUMBER = re.compile(r"(?:Lots?|Map|Parcel|Plat|Block|Unit|No\.?|#|Sections?|Sec\.|Article|Chapter|Route|Rte\.?|"
                             r"Page|Book|Ward|District|Phase|Building|Suite|Exhibit|of|[,&]|and)\s*$", re.I)


def boundaries(text):
    """Start positions of agenda items: numbering, bullets, times, section headers, article numbers."""
    out = set()
    for i, rx in enumerate(BOUNDARY_RES):
        for m in rx.finditer(text):
            if i == 0 and NOT_ITEM_NUMBER.search(text[max(0, m.start() - 12):m.start()]):
                continue  # "Map 14, Lot 17. The applicant..." is not item 17
            out.add(m.start())
    return sorted(out)


def sentence_spans(text, lo=0, hi=None, semicolons=True):
    """Spans of sentences in text[lo:hi]; a sentence ends at . ! ? (and ; when asked) or ': ' before a
    capital, except after common abbreviations and initials."""
    hi = len(text) if hi is None else hi
    spans, start = [], lo
    ends = r"[.!?;]" if semicolons else r"[.!?]"
    for m in re.finditer(ends + r"(?=\s+[A-Z0-9(\"'§])|:(?=\s+[A-Z])|\s…\s", text[lo:hi]):
        end = lo + m.end()
        prev = re.search(r"([\w./]+)$", text[start:end - 1])
        word = prev.group(1).lower() if prev else ""
        if text[end - 1] == "." and (word in ABBREV or re.fullmatch(r"[a-z]", word)):
            continue
        spans.append((start, end))
        start = end
        while start < hi and text[start] == " ":
            start += 1
    if start < hi:
        spans.append((start, hi))
    return spans


def locate(snippet, text):
    """(start, end) of the hit snippet in the document text, or None. Prefers a probe that occurs once,
    since agendas repeat stock phrases ("The applicant is proposing the installation...")."""
    s = norm(snippet).rstrip("…").strip()
    if not s or not text:
        return None
    mid = len(s) // 2
    probes = [s]
    for n in (160, 120, 80, 60, 40, 28):
        probes += [s[:n], s[-n:], s[max(0, mid - n // 2):mid + n // 2]]
    fallback = None
    for probe in probes:
        probe = probe.strip()
        if len(probe) < 18:
            continue
        i = text.find(probe)
        if i < 0:
            continue
        start = max(0, i - s.find(probe))
        if text.find(probe, i + 1) < 0:
            return start, min(len(text), start + len(s))
        if fallback is None:
            fallback = (start, min(len(text), start + len(s)))
    return fallback


def item_window(text, anchor):
    """The agenda item around position `anchor`: (start, end, header). Uses agenda numbering when the
    item is short; otherwise the sentence holding the anchor plus a follow-on sentence about the same site."""
    bs = boundaries(text)
    prev = max([b for b in bs if b <= anchor] or [0])
    nxt = min([b for b in bs if b > anchor + 5] or [len(text)])
    if nxt - prev <= 900 and anchor - prev <= 600:
        start, end, mode = max(prev, anchor - 450), min(nxt, anchor + 700), "item"
    else:
        lo = max(prev, anchor - 900)
        hi = min(nxt, anchor + 700)
        spans = sentence_spans(text, lo, hi, semicolons=False)
        idx = next((i for i, (a, b) in enumerate(spans) if a <= anchor < b), None)
        if idx is None:
            start, end = max(lo, anchor - 250), min(hi, anchor + 250)
        else:
            start, end = spans[idx]
            if idx + 1 < len(spans) and FOLLOW_ON.match(text[spans[idx + 1][0]:spans[idx + 1][0] + 30]):
                end = spans[idx + 1][1]
            if idx > 0 and FOLLOW_ON.match(text[start:start + 30]):
                start = spans[idx - 1][0]  # "The applicant is proposing..." belongs to the sentence naming it
        start, end, mode = max(start, anchor - 450), min(end, anchor + 350), "local"
    pre = text[max(0, start - 90):start]
    hm = HEADER_RE.search(pre)
    header = hm.group(1) if hm else ""
    return start, end, header, mode


# ============================================================================ names, addresses, sizes

ENTITY_SUFFIX = re.compile(r",?\s+(L\.?L\.?C\.?|Inc\.?|Incorporated|Corp\.?|Corporation|L\.?P\.?|Company|Trust)(?=[\s,.;:)]|$)")
NAME_STOP = {"by", "of", "from", "for", "the", "and", "applicant", "applicants", "owner", "owners", "petitioner",
             "request", "requested", "requests", "public", "hearing", "hearings", "continued", "notice", "noi",
             "intent", "map", "lot", "agenda", "item", "discussion", "business", "re", "mr", "ms",
             "mrs", "attorney", "atty", "esq", "representing", "represented", "behalf", "c/o", "trustee",
             "trustees", "with", "to", "a", "an", "is", "was", "that", "this", "application", "filed", "petition",
             "property", "owned", "between", "and/or", "regarding", "for:", "special", "permit", "site", "plan",
             "review", "modification", "comprehensive", "approval", "vote", "at", "in", "&"}
SINGLE_GENERIC = {"towers", "holdings", "properties", "realty", "partners", "development", "energy", "solar",
                  "storage", "trust", "company", "enterprises", "ventures", "investments", "management", "group"}
PRO_WORDS = re.compile(r"consult|engineer|survey|\blaw\b|legal|attorney|associates|architect|design\b|environmental|"
                       r"silverstein|bobrowski|land\s+consultants|partners\s+llp", re.I)
UTILITY = re.compile(r"new\s+england\s+power|national\s*grid|eversource|nstar|verizon|t-mobile|at&t|cellco|sba\b|"
                     r"crown\s+castle|american\s+tower|comcast|unitil|massachusetts\s+electric|town\s+of|city\s+of|"
                     r"commonwealth|holdings", re.I)
REP_BEFORE = re.compile(r"(?:represented\s+by|c/o|C/O|o/b/o|0/b/o|counsel|attorney|by\s+the\s+law\s+firm|owned\s+by|"
                        r"owner\s+is|representative\s+is|engineer)[\s,:]*$", re.I)
NAMED_PROJECT = re.compile(r"\b((?:[A-Z][\w'-]+\s+){1,3})(Solar(?:\s+(?:Project|Farm|Field|Array|Carport\s+Project))?|"
                           r"Cell\s+Tower|Data\s+Center|Energy\s+Storage)\b|\b((?:[A-Z][\w'-]+\s+){1,2})(40B)\b")
GENERIC_WORDS = {"large", "scale", "large-scale", "ground", "ground-mounted", "mounted", "proposed", "commercial",
                 "community", "residential", "municipal", "small", "medium", "accessory", "roof", "roof-mounted",
                 "rooftop", "dual-use", "dual", "use", "utility", "utility-scale", "battery", "energy", "clean",
                 "systems", "system", "the", "a", "of", "town", "city", "and", "public", "hearing", "special",
                 "permit", "site", "plan", "review", "bylaw", "zoning", "new", "solar", "photovoltaic",
                 "installation", "facility", "facilities", "space", "storage", "data", "center", "centers",
                 "temporary", "moratorium", "definition", "article", "section", "amend", "amendment", "smart", "ai",
                 "discussion", "update", "advancing", "landfill", "for", "on", "in", "at", "by", "agrivoltaics",
                 "agrivoltaic", "proposal", "regarding", "draft", "existing", "approved", "statewide", "state",
                 "local", "regional", "national", "massachusetts", "consolidated", "large-scale", "expedited",
                 "comprehensive", "permit/opengov", "continued", "cont'd", "pv", "via", "with", "to"}
STREET_TYPES = (r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Way|Boulevard|Blvd|Pike|Highway|Hwy|Turnpike|"
                r"Tpke|Parkway|Pkwy|Place|Pl|Court|Ct|Circle|Cir|Terrace|Ter|Path|Square|Sq|Trail|Extension)")
ADDR_RE = re.compile(r"\b(\d{1,5}(?:\s?(?:-|–|&|and)\s?\d{1,5})?[A-Z]?)\s+((?:[A-Z][A-Za-z'.-]*\s+){1,3}?)"
                     r"(?i:" + STREET_TYPES + r")\b\.?")
STREET_ONLY_RE = re.compile(r"\b(?:on|off|along)\s+((?:[A-Z][a-z'.-]+\s+){1,2}(?i:" + STREET_TYPES + r"))\b")
STREET_ABBR = {"st": "street", "rd": "road", "ave": "avenue", "ln": "lane", "dr": "drive", "blvd": "boulevard",
               "hwy": "highway", "tpke": "turnpike", "pkwy": "parkway", "pl": "place", "ct": "court",
               "cir": "circle", "ter": "terrace", "sq": "square"}


def name_key(name):
    """'Old Warren Rd Development II' and 'Old Warren Road Development' share a key."""
    k = re.sub(r"[^a-z0-9 ]", "", name.lower())
    k = re.sub(r"\b(rd|st|ave|ln|dr)\b", lambda m: {"rd": "road", "st": "street", "ave": "avenue", "ln": "lane",
                                                     "dr": "drive"}[m.group(1)], k)
    return re.sub(r"(?:\s+(?:\d+|i{1,3}|iv|v|40b))+$", "", k).strip()


def extract_names(item, town):
    """Applicant or project names in an agenda item, in order: [(display, key, is_llc)]."""
    out, seen = [], set()
    for m in ENTITY_SUFFIX.finditer(item):
        suffix = m.group(1)
        if suffix.replace(".", "").upper() in {"PLLC", "LLP", "PC"}:
            continue
        before = item[max(0, m.start() - 90):m.start()]
        toks = before.split()
        taken = []
        for i, tok in enumerate(reversed(toks)):
            if i and tok.endswith((",", ";", ":", ")")):
                break  # a comma or colon before the name ends it ("Lancaster (applicant/owner), 702, LLC")
            t = tok.strip(",;:")
            if "(" in t or ")" in t:
                break
            if "/" in t and not re.fullmatch(r"\d+/\d+", t):
                t = t.split("/")[-1]
                if t and t[0].isupper():
                    taken.append(t)
                break
            if not t or t.lower() in NAME_STOP or re.fullmatch(r"\d{1,2}\.|[a-z]\.|[A-Z]\.", tok):
                break
            if not (t[0].isupper() or t[0].isdigit()):
                break
            taken.append(t)
            if len(taken) >= 6:
                break
        name = " ".join(reversed(taken)).strip(" ,-–")
        name = re.sub(r"^(?:[A-Z]{2,}\s+)+(?=[A-Z][a-z])", lambda x: x.group(0) if len(x.group(0)) <= 4 else "", name)
        if len(name) < 5 or not re.search(r"[A-Za-z]{3}", name):
            continue
        if len(name.split()) == 1 and (len(name) < 6 or name.lower() in SINGLE_GENERIC or name.isupper()):
            continue
        rest = item[max(0, m.start() - 90):m.start()]
        if REP_BEFORE.search(rest[: len(rest) - len(name)].rstrip(" ,")) or PRO_WORDS.search(name):
            continue
        if re.match(r"\s*,?\s*(?:\(owner\)|\(property owner\))", item[m.end():m.end() + 20], re.I):
            continue
        if name.lower() == town.lower() or re.fullmatch(r"(?:Town|City)\s+of\s+.*", name):
            continue
        is_llc = suffix.upper().startswith(("L", "INC", "CORP"))
        display = re.sub(r"\s+\d{1,2}$", "", name)
        if re.match(r"\d", name):
            display = f"{name} {suffix.rstrip('.').replace('L.L.C', 'LLC')}"
        key = name_key(name)
        if key and key not in seen:
            seen.add(key)
            out.append((display, key, is_llc and not UTILITY.search(name)))
    for m in NAMED_PROJECT.finditer(item):
        words = (m.group(1) or m.group(3)).split()
        while words and words[0].lower() in GENERIC_WORDS | {town.lower()}:
            words = words[1:]
        if not words or any(w.lower() in GENERIC_WORDS for w in words) or (len(words) == 1 and len(words[0]) < 4):
            continue
        if words[0].isupper() and len(words[0]) > 3:
            continue
        if re.fullmatch(STREET_TYPES + r"\.?", words[-1], re.I):
            continue  # "23 Coyne Street 40B" names a place, not a project
        kind = m.group(2) or m.group(4)
        if kind == "40B":
            name = " ".join(words)          # "Woodland Ridge"; templates add "40B"
        elif kind.split()[0] == "Solar":
            name = " ".join(words + ["Solar"])
        else:
            name = " ".join(words + kind.split())
        key = name_key(name)
        if any(key in k or k in key for k in seen):
            continue
        seen.add(key)
        out.append((name, key, False))
    return out


ITEM_SEP = re.compile(r"(?i:\bApplicant\s*:|\bFiled\s*:|\bRE\s*:|\bPetitioner\s*:|\((?:continued|requested)\b)|"
                      r"\bA\s+(?:Special\s+Permit|Site\s+Plan|Notice\s+of\s+Intent)|\s[–—]\s+(?:Accept|Request)|"
                      r"\b(?:Request|Discussion)\s+(?:for|of|by)\b")


def pick_near(found, item, anchor, reach=400):
    """From [(position, value)], the value that belongs to the agenda item holding `anchor`: the closest
    one before it with no sentence end or 'Applicant:' in between, else the closest after it."""
    before = [(anchor - p, v) for p, v in found if p <= anchor and anchor - p <= reach
              and not ITEM_SEP.search(item[p:anchor])]
    if before:
        return min(before, key=lambda x: x[0])[1]
    after = [(p - anchor, v) for p, v in found if p > anchor and p - anchor <= 250]
    if after:
        return min(after, key=lambda x: x[0])[1]
    return None


def extract_address(item, town, anchor=None):
    """Site address in an item nearest `anchor` (not the applicant's office or the meeting room):
    (display, key), or (street, None) for 'on Shun Pike', or None."""
    found = []
    for m in ADDR_RE.finditer(item):
        got = _address_at(item, town, m)
        if got:
            found.append((m.start(), got))
    if found:
        if anchor is None:
            return found[0][1]
        best = pick_near(found, item, anchor)
        if best is not None:
            # "169 South St/0 Sawmill Brook Lane": one site with two parcels; show the first
            i = next(k for k, (_, v) in enumerate(found) if v is best)
            while i > 0 and re.fullmatch(r"\s*(?:/|&|and|,)\s*",
                                         item[found[i - 1][0] + len(found[i - 1][1][0]):found[i][0]]):
                i -= 1
            return found[i][1]
    m = STREET_ONLY_RE.search(item)
    if m:
        return tidy_caps(m.group(1)), None
    return None


def _address_at(item, town, m):
    """(display, key) for one ADDR_RE match, or None when it is an office, a meeting room or a route number."""
    num, street = m.group(1), m.group(2).strip()
    typ = m.group(0)[len(m.group(1)):].strip()[len(street):].strip().rstrip(".")
    if street.split()[0].lower() in {"and", "the", "of", "to", "on", "at", "map", "lot"}:
        return None
    if re.search(r"(?:Route|Rte\.?|Rt\.?|Highway|Hwy\.?|Box)\s*$", item[max(0, m.start() - 8):m.start()]):
        if not re.search(r"&|and", num):
            return None
        num = re.split(r"\s?(?:&|and)\s?", num)[-1]  # "Route 130 & 55 Pimlico Pond Road" -> 55
    after = item[m.end():m.end() + 45]
    before = item[max(0, m.start() - 45):m.start()]
    if re.match(r"\s*,?\s*(?:Suite|Ste\.?|Unit|Floor|Fl\.?|#)", after, re.I):
        return None
    tm = re.match(r"\s*,?\s*([A-Z][a-z]+(?:[\s-][A-Z][a-z]+)?),\s*(?:MA|RI|NY|CT|NH|VT|ME|NJ|PA|CA|FL|TX|"
                  r"Massachusetts|Rhode Island|New York)\b", after)
    if tm and tm.group(1).lower() != town.lower():
        return None
    if PLACE_WORDS.search(before[-30:]) or re.match(r"\s*,?\s*[^,.]{0,12}?(?:Town Hall|City Hall|Senior Center|"
                                                     r"Municipal|Library|Chambers|Room)", after):
        return None
    if re.search(r"(?:held at|located at the|meet(?:ing)? at|place:?)\s*$", before, re.I) and \
            PLACE_WORDS.search(re.split(r"[.;]", after, maxsplit=1)[0]):
        return None
    num = re.sub(r"\s?(?:-|–)\s?", "-", num)
    disp = tidy_caps(f"{num} {street} {typ}").strip()
    snum = re.split(r"[-&\s]", num)[-1] if re.search(r"&|and", num) else num.split("-")[0]
    styp = STREET_ABBR.get(typ.lower().rstrip("."), typ.lower())
    return disp, f"{snum} {street.lower()} {styp}"


def _num(s):
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def fmt_num(v):
    return f"{int(v):,}" if v == int(v) else f"{v:,.2f}".rstrip("0").rstrip(".")


SCALE_TIERS = {
    "MW": [(50, 3.0), (10, 2.5), (2, 2.0), (0.5, 1.0)],
    "MWh": [(200, 3.0), (40, 2.5), (8, 2.0), (1, 1.0)],
    "acres": [(50, 2.0), (20, 1.5), (5, 1.0)],
    "units": [(200, 2.5), (100, 2.0), (40, 1.5), (10, 1.0)],
    "dollars": [(10e6, 2.0), (1e6, 1.5), (1e5, 0.5)],
    "sqft": [(200e3, 2.5), (50e3, 1.5), (10e3, 1.0)],
}


def extract_scale(item):
    """Sizes stated in an item: list of (points, label, kind, value), best first."""
    found = []
    t = item
    for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)\s*(?:-\s*)?(MWh|MW|megawatt[\s-]hours?|megawatts?)(?:[\s-]?(?:AC|DC))?\b", t, re.I):
        v = _num(m.group(1))
        kind = "MWh" if "h" in m.group(2).lower() else "MW"
        if v:
            found.append((kind, v, f"{fmt_num(v)} {kind}"))
    for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)\s*(kWh|kW)\b", t):
        v = _num(m.group(1))
        if v and v >= 1000:
            kind = "MWh" if m.group(2) == "kWh" else "MW"
            found.append((kind, v / 1000, f"{fmt_num(v)} {m.group(2)}"))
    for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)[\s-]*(?:\+/-\s*)?acres?\b", t, re.I):
        v = _num(m.group(1))
        if v:
            found.append(("acres", v, f"{fmt_num(v)} acres"))
    for m in re.finditer(r"(?:\((\d[\d,]*)\)|\b(\d[\d,]*))\s+(?:[a-z-]+\s+){0,3}(?:dwelling\s+)?units\b", t, re.I):
        v = _num(m.group(1) or m.group(2))
        pre = t[max(0, m.start() - 12):m.start()].lower()
        if v and v >= 2 and not re.search(r"(?:of\s+which|%\s+of|of\s+the)\s*\(?$", pre):  # "(25% of which (75 units)"
            found.append(("units", v, f"{fmt_num(v)} units"))
    for m in re.finditer(r"\$\s?(\d[\d,]*(?:\.\d+)?)(\s*(?:million|billion|M)\b)?", t):
        v = _num(m.group(1))
        if v is None:
            continue
        mult = (m.group(2) or "").strip().lower()
        v = v * (1e9 if mult == "billion" else 1e6 if mult in ("million", "m") else 1)
        label = f"${fmt_num(round(v / 1e6, 1))} million" if v >= 1e6 else f"${fmt_num(v)}"
        found.append(("dollars", v, label))
    for m in re.finditer(r"(\d[\d,]*)\s*(?:sq\.?\s?ft\.?|square[\s-]+feet|s\.f\.|SF)\b", t):
        v = _num(m.group(1))
        if v:
            found.append(("sqft", v, f"{fmt_num(v)} sq ft"))
    out = []
    counts = defaultdict(int)
    for kind, v, _ in found:
        counts[(kind, v)] += 1
    for kind, v, label in found:
        if counts[(kind, v)] >= 3:  # repeated values are table cells, not a project's size
            continue
        pts = next((p for lim, p in SCALE_TIERS[kind] if v >= lim), 0.0)
        if pts:
            out.append((pts, label, kind, v))
    out.sort(key=lambda x: -x[0])
    return out


def extract_duration(item):
    """'365-day', 'one-year', '12-month' as the agenda words it (a number in parentheses wins)."""
    m = re.search(r"\b(\d{1,3}|one|two|six|nine|twelve|eighteen)(?:\s*\((\d+)\))?[\s-]+(day|month|year)s?\b", item, re.I)
    if not m:
        return None
    n = m.group(2) or m.group(1).lower()
    return f"{n}-{m.group(3).lower()}"


def extract_height(item):
    m = re.search(r"\b(\d{2,3})\s*(?:feet|foot|ft\.?|')\s*(?:in\s+height|tall|high)\b|monopole\s+(?:of\s+)?(\d{2,3})\s*(?:feet|ft)",
                  item, re.I)
    if m:
        return f"{m.group(1) or m.group(2)}-foot"
    return None


# ============================================================================ quotes

def clean_quote_text(s):
    s = norm(s)
    s = re.sub(r"\b(?:\d{2,3}\s){2,}(?=[A-Z])", "", s)            # minutes line numbers
    s = re.sub(r"(?:(?<=\s)|^)(?:e|o|e¢|¢|«|[•◼▪●○◦■□►➢✓])\s+(?=[A-Z])", "", s)
    toks = []
    for tok in s.split():
        if "~" in tok or re.search(r"[^\w.,;:()'\"&/$%§#@+*?!\-–—\[\]]", tok):
            if not re.fullmatch(r"[\"'(]?[\w.,;:()'\"&/$%§#@+*?!\-–—]+[\"').,;:]?", tok):
                continue
        if len(tok) >= 7 and len(re.findall(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", tok)) >= 3 \
                and not re.search(r"[-§.]", tok):
            continue  # OCR noise such as "oo006806d~CO0dU6lU(O"
        toks.append(tok)
    s = " ".join(toks)
    s = re.sub(r"^(?:[-–—:;,.)\s]|\d{1,2}[.)]\s|[A-Ha-h][.)]\s|[ivx]{1,4}\.\s|\d{1,2}:\d{2}\s*(?:[AaPp]\.?\s?[Mm]\.?)?\s)+", "", s)
    return s.strip(" -–—;,")


def junk_ratio(s):
    toks = s.split()
    if not toks:
        return 1.0
    good = sum(1 for t in toks if re.fullmatch(r"[\"'(§$]*(?:[A-Za-z][a-z']*|[A-Z][A-Z'&.-]*|[\d][\d,.:/-]*[a-zA-Z]?|"
                                               r"[A-Za-z]+(?:-[A-Za-z0-9]+)+|\d+(?:st|nd|rd|th)|[&\-–]|"
                                               r"[A-Z]?\d[\w.-]*)[\"'),.;:?]*", t))
    return 1 - good / len(toks)


def cut(s, limit, around=None):
    """Shorten s to about `limit` characters at word boundaries, keeping position `around` in view."""
    if len(s) <= limit:
        return s
    if around is None or around < limit - 40:
        out = s[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-–")
        return out + "…"
    start = max(0, around - limit // 3)
    piece = s[start:start + limit]
    if start > 0:
        piece = piece.split(" ", 1)[-1]
    if start + limit < len(s):
        piece = piece.rsplit(" ", 1)[0].rstrip(" ,;:-–") + "…"
    return ("…" if start > 0 else "") + piece


ZONING_KEY = re.compile(r"\bzon(?:ing|e)\b|\brezon", re.I)
TRAILING_ADDRESS = re.compile(r"\s+\d{1,5}\s+(?:[A-Z][\w'.-]*\s+){1,3}(?:St|Street|Rd|Road|Ave|Avenue|Lane|Ln|Drive|Dr|"
                              r"Way|Hwy|Highway|Pike)\.?$")
OUTCOME_START = re.compile(r"^(?:Does not|Do not|Recommends?|Approved|Denied|Passed|Failed|Voted)\b", re.I)


def pick_quote(item_text, keys, prefer, snippet, limit=200, name=None):
    """The shortest clean agenda sentence that supports the headline: it must hold the subject or the
    project name, and ranks higher the more of subject, name and action word it holds. Falls back to
    the snippet. Sentences that state a recommendation or outcome rank last."""
    cands = []
    dashes = {m.start() for m in re.finditer(r"\s[-–—−]\s+(?=[A-Z])", item_text)
              if item_text.count('"', 0, m.start()) % 2 == 0}  # " - " separates agenda items, not inside quotes
    coarse = {0, len(item_text)} | {b for _, b in sentence_spans(item_text, semicolons=False)} | \
        set(boundaries(item_text)) | dashes
    fine = coarse | {m.end() for m in re.finditer(r";\s", item_text)}  # also try clauses split at semicolons
    pieces = set()
    for cuts in (sorted(coarse), sorted(fine)):
        pieces.update(zip(cuts, cuts[1:]))
    name_rx = re.compile(re.escape(name), re.I) if name else None
    for a, b in sorted(pieces):
        sent = clean_quote_text(item_text[a:b])
        ta = TRAILING_ADDRESS.search(sent)  # the next item's address run on without a separator
        if ta and len(sent[:ta.start()]) >= 30 and not re.search(r"(?:\b(?:at|and|of|on|for|to)|[&,])$", sent[:ta.start()]):
            sent = sent[:ta.start()]
        sent = sent.rstrip(" ;,(-–")
        if re.search(r"\b(?:within|and|or|of|for|to|the|a|an|in|on|at|by|with|from)$", sent, re.I):
            sent += "…"  # the agenda runs on into the next item here
        if len(sent) < 12 or junk_ratio(sent) > 0.3 or not re.search(r"[a-z]{3}", sent):
            continue
        km = next((m for k in keys if k for m in [k.search(sent)] if m), None)
        nm = name_rx.search(sent) if name_rx else None
        if not (km or nm):
            continue
        pm = prefer.search(sent) if prefer else None
        cover = 2 * bool(km) + bool(nm) + bool(pm)
        pos = (pm or km or nm).start()
        mid = sent[:1].islower()  # starts mid-sentence (the item window began inside it)
        cands.append((bool(OUTCOME_START.search(sent)), -cover, mid, len(sent) < 40, len(sent) > limit, len(sent),
                      ("…" + sent) if mid else sent, pos + mid))
    if cands:
        cands.sort(key=lambda c: c[:6])
        return cut(cands[0][6], limit, cands[0][7])
    s = clean_quote_text(snippet)
    km = next((m for k in keys if k for m in [k.search(s)] if m), None)
    return cut(s, limit, km.start() if km else None)


# ============================================================================ loading

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def load_inputs(data_dir=DATA):
    hits_doc = load_json(os.path.join(data_dir, "hits_current.json"), None)
    if hits_doc is None:
        raise SystemExit(f"trending: {data_dir}/hits_current.json is missing or unreadable")
    docs = {}
    history = []   # (state, town, topic, date or None) for "first in this town"
    coverage = {}  # (state, town) -> earliest meeting date we hold text for
    for path in sorted(glob.glob(os.path.join(data_dir, "search", "*", "*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                for u in (r.get("url"), r.get("source_url")):
                    if u and u not in docs:
                        docs[u] = r
                d = parse_date(r.get("meeting_date"))
                key = (r.get("state"), r.get("town"))
                if d and (key not in coverage or d < coverage[key]):
                    coverage[key] = d
                for t in r.get("topics") or []:
                    history.append((r.get("state"), r.get("town"), t, d))
    for path in sorted(glob.glob(os.path.join(data_dir, "state", "hits_archive", "*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    h = json.loads(line)
                except ValueError:
                    continue
                for t in h.get("topics") or []:
                    history.append((h.get("state"), h.get("town"), t, parse_date(h.get("meeting_date"))))
    for h in hits_doc.get("hits", []):
        for t in h.get("topics") or []:
            history.append((h.get("state"), h.get("town"), t, parse_date(h.get("meeting_date"))))
    return {
        "hits_doc": hits_doc,
        "docs": docs,
        "history": history,
        "coverage": coverage,
        "tracker": load_json(os.path.join(data_dir, "tracker.json"), {}).get("items", []),
        "ag": load_json(os.path.join(data_dir, "ag_decisions.json"), []),
        "neighbors": load_json(os.path.join(data_dir, "neighbors.json"), {}),
    }


# ============================================================================ per-hit analysis

BOARD_CLEAN = [
    (r"\s*\(wetlands filing\)", ""), (r"^The\s+", ""), (r"(?<!Town)\s+Meetings?$", ""), (r"\s+FY\d+$", ""),
    (r"\s*-\s*TOWN CLERK'?S OFFICE$", ""), (r"\s*\(\w+\)$", ""), (r"\s+Public Hearing$", ""),
    (r"\s+Warrants?(?:\s*&\s*Minutes)?$", ""), (r"\s*/\s*(?:Board of Health|Council)$", ""),
    (r"^Appeals, Zoning Board of$", "Zoning Board of Appeals"),
]


def clean_board(name, key):
    s = (name or "").strip()
    for pat, rep in BOARD_CLEAN:
        s = re.sub(pat, rep, s, flags=re.I)
    s = s.strip()
    if s.isupper():
        s = s.title()
    if not s:
        s = {"planning_board": "Planning Board", "zoning_board_of_appeals": "Zoning Board of Appeals",
             "conservation_commission": "Conservation Commission", "select_board": "Select Board",
             "town_meeting": "Town Meeting"}.get(key, "Board")
    return s


def board_phrase(key, name):
    """How a headline names the board: (phrase, plural)."""
    if key == "planning_board" and "planning" in name.lower():
        return "planners", True
    if key == "zoning_board_of_appeals":
        return "zoning board", False
    if key == "town_meeting":
        return "Town Meeting", False
    return name, False


def verb(v, plural):
    if plural:
        return v
    head, _, tail = v.partition(" ")
    if head.endswith(("s", "sh", "ch", "x")):
        head += "es"
    else:
        head += "s"
    return (head + " " + tail).strip()


WARRANT_DATE = re.compile(r"(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+)?"
                          r"(January|February|March|April|May|June|July|August|September|October|November|December)"
                          r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)", re.I)  # warrants print "MONDAY, APRIL 27, 2026" too
HEADING_CHARS = 600  # a date this early in the document is the warrant's own heading


SEASON_MONTHS = {"spring": (3, 4, 5, 6), "fall": (9, 10, 11, 12), "autumn": (9, 10, 11, 12),
                 "winter": (1, 2, 12), "summer": (6, 7, 8)}
NOT_THE_MEETING = re.compile(r"fiscal\s+year|\bFY\s?\d|\bbeginning\b|\bending\b|\bthrough\b|\beffective\b|"
                             r"\bexpir|\buntil\b|\bcommencing\b|\bsigned\b|\bposted\b|\bdated\b|\bdeadline\b", re.I)


def warrant_date(text, title, window=None):
    """Meeting date of an undated Town Meeting warrant, read from its first pages.
    Returns (date or None, hint) where hint is 'fall' when only the title says the meeting is this fall.
    A date counts when it comes with a weekday or sits near "town meeting", "meet at", "assemble" or
    "convene". When the title (or the file name) names a month or season, a date in another month is
    not the meeting ("the fiscal year beginning July 1, 2026" in an October warrant). Among the rest,
    a date in the heading (the first HEADING_CHARS characters) comes first, then one in the title's
    year, then one inside `window` (a (start, end) pair of dates), then one not introduced as a
    fiscal-year or effective date, then the one nearest the top."""
    head = text[:4000]
    t = (title or "").lower()
    want_year = re.search(r"\b(20\d\d)\b", t)
    want_year = int(want_year.group(1)) if want_year else None
    want_months = next((set(v) for k, v in SEASON_MONTHS.items() if re.search(rf"\b{k}\b", t)), set())
    for i, name in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                              "september", "october", "november", "december"]):
        if re.search(rf"\b{name}\b", t):
            want_months = {i + 1}
            break
    cands = []
    for m in WARRANT_DATE.finditer(head):
        near = head[max(0, m.start() - 250):m.end() + 250]
        if not (m.group(1) or re.search(r"town\s+meeting|meet\s+at|assemble|convene", near, re.I)):
            continue
        try:
            d = date(int(m.group(4)), MONTH_NUM[m.group(2).lower()], int(m.group(3)))
        except ValueError:
            continue
        if want_months and d.month not in want_months:
            continue
        lead_in = head[max(0, m.start() - 40):m.start()]
        cands.append((
            0 if m.start() < HEADING_CHARS else 1,
            0 if want_year is None or d.year == want_year else 1,
            0 if window and window[0] and window[1] and window[0] <= d <= window[1] else 1,
            1 if NOT_THE_MEETING.search(lead_in) else 0,
            m.start(), d))
    if cands:
        return min(cands)[5], None
    if re.search(r"\b(fall|autumn|october|november|december|special)\b", t) and "2026" in t or \
            re.search(r"\b(fall|october|november)\b", t):
        return None, "fall"
    return None, None


def analyze_hit(h, inputs, today):
    """Everything trending needs from one hit: dates, the agenda item, subject, action, names, sizes."""
    doc = inputs["docs"].get(h.get("source_url"))
    text = norm(doc["text"]) if doc else ""
    snippet = norm(h.get("snippet", ""))
    topics = list(h.get("topics") or [])
    title = h.get("document_title") or (doc or {}).get("title") or ""
    source = h.get("source") or "agenda"
    a = {
        "hit": h, "id": h["id"], "state": h.get("state"), "town": h.get("town"), "county": h.get("county"),
        "board_raw": h.get("board") or "", "board_key": h.get("board_key") or "",
        "topics": topics, "source": source, "title": title,
    }
    a["board"] = clean_board(a["board_raw"], a["board_key"])
    d = parse_date(h.get("meeting_date"))
    a["date_source"] = "agenda"
    a["hint"] = None
    if source != "agenda":
        a["date_source"] = "filing"
    elif d is None and (a["board_key"] == "town_meeting" or "warrant" in title.lower()):
        win = (inputs.get("hits_doc") or {}).get("window") or {}
        # The file name often says what the title doesn't ("Fall-2026-ATM-Warrant" behind a "CLICK HERE" link).
        slug = unquote((h.get("source_url") or "").rsplit("/", 1)[-1]).replace("-", " ").replace("_", " ")
        d, a["hint"] = warrant_date(text, f"{title} {slug}", (parse_date(win.get("start")), parse_date(win.get("end"))))
        a["date_source"] = "warrant" if d else None
    a["date"] = d
    a["days"] = (d - today).days if d else None
    if a["date_source"] == "filing":
        a["status"] = "live" if d and -FILING_DAYS <= a["days"] <= 0 else ("past" if d else "stale")
    elif d is None:
        a["status"] = "live" if a["hint"] == "fall" else "stale"
    elif a["days"] >= 0:
        a["status"] = "live"
    elif a["days"] >= -LOOKBACK_DAYS:
        a["status"] = "past"
    else:
        a["status"] = "stale"
    a["first_seen"] = h.get("first_seen")

    a["snippet"] = snippet
    a["minutes_start"] = None
    span = locate(snippet, text) if text else None
    if span:
        s0, s1 = span
        anchor = find_anchor(text, s0, s1, topics)
        i0, i1, header, mode = item_window(text, anchor)
        a["item_key"] = (h.get("source_url"), i0)
        ms = MINUTES_START.search(text)
        a["minutes_start"] = ms.start() if ms else None
    else:
        text, anchor, i0, i1, header = snippet, find_anchor(snippet, 0, len(snippet), topics), 0, len(snippet), ""
        mode = "snippet"
        a["item_key"] = (h.get("source_url"), "snippet:" + h["id"])
    a["item"] = text[i0:i1]
    a["header"] = header
    a["mode"] = mode
    a["anchor_rel"] = anchor - i0
    classify(a, text, anchor, i0, i1)
    return a


def find_anchor(text, s0, s1, topics):
    """Position of the matched topic word inside the snippet span, highest-stakes topic first."""
    for t in sorted(topics, key=lambda t: SUBJECT_ORDER.index(t) if t in SUBJECT_ORDER else 99):
        rx = SUBJECT_RE.get(t)
        m = rx.search(text, s0, s1) if rx else None
        if m:
            return m.start()
    m = SUBJECT_RE["moratorium"].search(text, s0, s1)
    return m.start() if m else (s0 + s1) // 2


MINUTES_START = re.compile(r"called\s+(?:the\s+(?:meeting|session)\s+)?to\s+order\s+at|meeting\s+was\s+called\s+to\s+order|"
                           r"\bmembers\s+present\s*:|\bPRESENT\s*:|made\s+a\s+motion|seconded\s+by|"
                           r"\bmotion\s+(?:carried|passed)|\bmoved\s+to\s+(?:approve|adjourn|accept)", re.I)
BYLAW_NEAR = re.compile(r"\bby-?laws?\b|\bordinances?\b|\blocal\s+law\b|\bzoning\s+(?:amendments?|code|text|regulations?|"
                        r"changes?|definitions?)|\bamend(?:ing|ment|ments|s)?\s+(?:to\s+)?(?:the\s+)?(?:\w+\s+){0,4}"
                        r"(?:zoning|by-?law|ordinance|code)|\b(?:zoning|new|proposed|draft|amended)\s+(?:\w+\s+){0,2}"
                        r"regulations?\b|\bregulations?\s+for\b|\bdefinitions?\b|\bTable\s+of\s+(?:Principal\s+)?Uses|"
                        r"\buse\s+(?:table|regulations?)|\bSections?\s+[\d.]+(?:\(\d+\))?\s*:|\bprocedures?\s+for\b", re.I)
PROJECT_NEAR = re.compile(r"\bspecial\s+permit|\bsite\s+plan|\bcomprehensive\s+(?:permit|project)|\bvariances?\b|"
                          r"\bnotice\s+of\s+intent|\bNOI\b|\bL\.?L\.?C\b|\bInc\b|\bRealty\s+Trust|\bapplicant\s+(?:is|has)\b|"
                          r"\(applicant|\bapplication\s+(?:of|by|from|filed)|\bapplication\s+for\s+(?:a|an|the)\b|"
                          r"\bpetition\s+(?:of|by|from)\s+(?!the\s+(?:city|town)\b)|\bpermit\s+(?:extension|modification)|"
                          r"\bdefinitive\s+subdivision|\brequest\s+by\b|\bproperty\s+(?:located\s+)?at\b|"
                          r"\bplanned\s+development|\bpre-application|"
                          r"\bproposed\s+(?:[\w-]+\s+){0,5}(?:installation|tower|array|facility|carport|system|project)\b|"
                          r"\bat\s+\d{1,5}\s+(?:and\s+\d{1,5}\s+)?[A-Z][a-z]+\s+(?:St|Street|Road|Rd|Ave|Avenue|Lane|Drive|"
                          r"Way|Blvd|Highway|Pike)\b", re.I)
CITATION_RE = re.compile(r"(?:under|pursuant\s+to|per|of|in)\s+(?:the\s+)?(?:Sections?|§+|Article)\s*[\w.\-()]+"
                         r"(?:\s*(?:,|and|&)\s*[\w.\-()]+)*\s+(?:of\s+(?:the\s+)?(?:[A-Z][\w.']*\s+){0,4})?"
                         r"(?:Zoning\s+)?(?:By[\s-]?laws?|Ordinance|Code)\b", re.I)
CONSOLIDATED_RE = re.compile(r"consolidated\s+(?:local\s+)?permit|permitting\s+process|225\s+CMR|local\s+government\s+"
                             r"representative|DOER\b|statewide\s+siting", re.I)
ARTICLE_START = re.compile(r"\bARTICLE\s+\d+|\bArticle\s+\d+\s*[:.\-–]|To\s+see\s+if\s+the\s+(?:Town|City)\s+will\s+vote")
SOLAR_DISTRICT = re.compile(r"solar\s+(?:overlay\s+)?district|overlay(?:ed)?\s+by\s+the\s+solar", re.I)
UTILITY_WORK = re.compile(r"(?:national\s*grid|n\.\s?grid|eversource|nstar|verizon|unitil)[^.]{0,80}"
                          r"(?:poles?\b|conduit|grant\s+of\s+location|manhole|wires)|grant\s+of\s+location|mid\s+span\s+pole", re.I)
STARTER_RE = re.compile(r"\b(?:Discussion|Discuss|Request|Review|Update|Approval|Minutes|Correspondence|Vote\s+to|"
                        r"Accept|Appoint|Report)\b")


def nearest(rx, text, lo, hi, pos):
    """Distance from pos to the closest match of rx in text[lo:hi], or None."""
    best = None
    for m in rx.finditer(text, lo, hi):
        d = 0 if m.start() <= pos <= m.end() else (pos - m.end() if m.end() < pos else m.start() - pos)
        best = d if best is None else min(best, d)
    return best


def minutes_near(text, anchor, title, minutes_start):
    """True when the matched words sit in narrative minutes of an earlier meeting (included in a packet)."""
    low = title.lower()
    if re.search(r"\bminutes\b", low) and "agenda" not in low:
        return True
    if MINUTES_STRONG.search(text, max(0, anchor - 400), anchor + 400):
        return True
    narr = len(MINUTES_NARR.findall(text, max(0, anchor - 300), anchor + 300))
    if narr >= 2:
        return True
    tight = text[max(0, anchor - 200):anchor + 200]
    if narr and PRONOUN.search(tight):
        return True
    if re.search(r"(?<![\d.,:/$-])(\d{2,3}) (\d{2,3})(?![\d.,:/%-])", tight) and any(
            int(y) == int(x) + 1 for x, y in re.findall(r"(?<![\d.,:/$-])(\d{2,3}) (\d{2,3})(?![\d.,:/%-])", tight)):
        return True
    return minutes_start is not None and anchor > minutes_start and bool(
        MINUTES_NARR.search(text, max(0, anchor - 600), anchor + 600))


def classify(a, text, anchor, i0, i1):
    """Subject, action, flags, names, address, sizes and base points for one hit."""
    topics, title, source = a["topics"], a["title"], a["source"]
    item = text[i0:i1]
    rel = anchor - i0
    local_lo, local_hi = max(i0, anchor - 200), min(i1, anchor + 220)
    local = text[local_lo:local_hi]
    header = a["header"]
    section = header or (section_before(text, i0, 900) if i0 else "")
    if not section and i0:
        caps = [m.group(0) for m in re.finditer(SECTION_PAT, text[max(0, i0 - 2500):i0])]
        section = caps[-1] if caps else ""
    tm_doc = a["board_key"] == "town_meeting"

    # subject
    subs = [t for t in SUBJECT_ORDER if t in topics and t != "wetlands_filing"]
    mor = SUBJECT_RE["moratorium"].search(item)
    if not subs and "moratorium" in topics:
        near = item[max(0, mor.start() - 160):mor.end() + 160] if mor else item
        subs = [t for t in SUBJECT_ORDER[:5] if SUBJECT_RE[t].search(near)]
    if not subs and "wetlands_filing" in topics:
        subs = ["wetlands_filing"]
    subject = subs[0] if subs else "other"
    if subject == "zoning_amendment" and a["board_key"] != "planning_board" and \
            not re.search(r"\bzon(?:ing|e)\b|\brezon|\bland\s+use|\buse\s+table", item, re.I):
        subject = "general_bylaw"
    # "under Section 6.10 of the Zoning By-laws" cites the bylaw a permit is filed under; it is not a bylaw change
    masked = text[:i0] + CITATION_RE.sub(lambda m: " " * len(m.group(0)), item) + text[i1:]
    d_bylaw = nearest(BYLAW_NEAR, masked, i0, i1, anchor)
    d_project = nearest(PROJECT_NEAR, text, i0, i1, anchor)
    d_proc = nearest(CONSOLIDATED_RE, text, i0, i1, anchor)
    if "clean_energy_siting" in topics and not tm_doc and d_proc is not None and d_proc < 250 and \
            (d_bylaw is None or d_proc < d_bylaw) and (d_project is None or d_proc < d_project):
        subject = "clean_energy_siting"
    a["subjects"] = subs
    a["subject"] = subject
    a["solar_large"] = bool(LARGE_SOLAR.search(local)) and not SMALL_SOLAR.search(local)

    # flags: a hearing word just before the matched words (or in the item's section header), not one
    # belonging to the next item on a run-on agenda
    hearing_near = None
    for m in HEARING_RE.finditer(text, i0 if a["mode"] == "item" else max(i0, anchor - 220), min(i1, anchor + 40)):
        between = text[m.end():anchor]
        if m.start() > anchor or len(between) < 40 or not STARTER_RE.search(between):
            hearing_near = m  # no other agenda item ("Discussion of...", "Request for...") in between
    doc_hearing = bool(DOC_HEARING_RE.search(text[:1500])) or (re.search(r"hearing", title, re.I) and len(text) < 8000)
    flags = {
        "hearing": bool(hearing_near or HEARING_SECTIONS.search(section) or doc_hearing),
        "continued": bool(CONTINUED_HEARING_RE.search(item[:rel + 200] + " " + header)),
        "vote": bool(VOTE_RE.search(local)),
        "draft": bool(DRAFT_RE.search(local)),
        "proposed": bool(re.search(r"\bpropos", local, re.I)),
        "petition": bool(PETITION_RE.search(local)),
        "warrant": False,
        "temporary": bool(re.search(r"\btemporary\b", local, re.I)),
        "extension": bool(re.search(r"\bextension\b", local, re.I)),
        "tentative": False,
    }

    # Town Meeting article: the subject must be in the article's heading or "To see if" clause
    article_about = False
    if tm_doc or a["board_key"] == "select_board":
        last = None
        floor = text.rfind(" … ", 0, anchor)
        for m in ARTICLE_START.finditer(text, max(0, anchor - 4000, floor), anchor + 1):
            last = m
        if last:
            art_head = text[last.start():last.start() + 300]
            keys = [SUBJECT_RE[t] for t in (subs or [subject]) + (["clean_energy_siting"] if "clean_energy_siting"
                                                                    in topics else []) if t in SUBJECT_RE]
            article_about = any(k.search(art_head) for k in keys) or bool(mor and SUBJECT_RE["moratorium"].search(art_head))
            flags["warrant"] = tm_doc or bool(re.search(r"to\s+see\s+if|warrant|town\s+meeting",
                                                        text[last.start():anchor + 200], re.I))
    if not tm_doc and (TM_ARTICLE_RE.search(local) or (a["board_key"] == "select_board" and re.search(
            r"warrant\s+articles?|review\s+(?:of\s+)?(?:the\s+)?warrant", text[max(0, anchor - 1500):anchor], re.I))):
        flags["warrant"] = True

    near_mor = item[max(0, mor.start() - 160):mor.end() + 160] if mor else ""
    mor_siting = bool(mor) and any(SUBJECT_RE[t].search(near_mor) for t in ("data_center", "battery_storage", "solar",
                                                                             "wind", "clean_energy_siting")) \
        and not NON_SITING_MORATORIUM.search(item[max(0, mor.start() - 60):mor.end() + 60])
    ban = None
    for m in BAN_RE.finditer(item):
        if subject in SITING and SUBJECT_RE.get(subject, SUBJECT_RE["solar"]).search(
                item[max(0, m.start() - 120):m.end() + 120]):
            ban = m
            break
    minutes = minutes_near(text, anchor, title, a.get("minutes_start"))
    rezone = REZONE_RE.search(item) and re.search(r"\bfrom\s+[A-Z][\w-]*\s+to\b|\bPlat\b|\bLots?\b|\bparcel|\bacres?\b|"
                                                  r"\d+\s+[A-Z][a-z]+\s+(?:St|Street|Road|Rd|Ave|Avenue|Pike)", item)
    kind = None
    if d_bylaw is not None and (d_project is None or d_bylaw <= d_project):
        kind = "bylaw"
    elif d_project is not None:
        kind = "project"
    if subject == "40b_comprehensive_permit" and re.search(r"comprehensive\s+permit\s+(?:application|under|pursuant|per)|"
                                                           r"(?:application|request)\w*\s+(?:for\s+)?a\s+comprehensive\s+"
                                                           r"permit|waivers?\s+(?:of|from)", item, re.I):
        kind = "project"  # a 40B application lists bylaw waivers; it is still one project
    cont = CONTINUANCE_RE.search(item if a["mode"] == "item" else item[:rel + 400])
    cont_date = continuance_date(item, a["date"] or date.today()) if cont else None
    stale_cont = bool(cont and cont_date and a["date"] and cont_date < a["date"])

    if CANCEL_RE.search(item):
        action = "cancelled"
    elif minutes or stale_cont:
        action = "minutes"   # narrative minutes, or a continuance to a date before this meeting
    elif WITHDRAWN_RE.search(local):
        action = "withdrawn"
    elif cont and not mor_siting:
        action = "continuance"
    elif mor_siting:
        action = "moratorium"
        flags["vote"] = bool(re.search(r"vote\s+(?:on|to)[^.;]{0,60}moratori|moratori[^.;]{0,40}vote\s+(?:on|to)|"
                                       r"discuss\s+and\s+vote[^.;]{0,60}moratori|recommend\s+adoption", item, re.I))
        flags["draft"] = bool(re.search(r"draft[^.;]{0,40}moratori", item, re.I))
        flags["proposed"] = bool(re.search(r"propos\w+[^.;]{0,40}moratori|moratori[^.;]{0,20}propos", item, re.I))
        flags["tentative"] = bool(re.search(r"moratori\w*\s*\?|possible\s+moratori|potential\s+moratori", item, re.I))
    elif ban:
        action = "ban"
    elif source != "agenda":
        action = "filing"
    elif tm_doc:
        action = "town_meeting" if article_about and flags["warrant"] else "mention"
    elif flags["warrant"] and (kind == "bylaw" or article_about):
        action = "warrant_review" if article_about or kind == "bylaw" else "mention"
    elif subject == "clean_energy_siting" and kind != "project" and (d_bylaw is None or (d_proc or 999) < d_bylaw):
        action = "process"
    elif ADOPT_RE.search(local) and subject != "general_bylaw":
        action = "adopt"
    elif rezone and subject in ("zoning_amendment", "general_bylaw", "40b_comprehensive_permit"):
        action = "rezoning"
    elif kind == "bylaw":
        action = "bylaw_hearing" if flags["hearing"] else "bylaw_draft"
    elif kind == "project":
        action = "project_hearing" if flags["hearing"] else "project"
    elif DEAL_RE.search(local):
        action = "deal"
    elif DISCUSS_RE.search(local + " " + section):
        action = "discussion"
    else:
        action = "mention"
    if action in ("project_hearing", "project") and DEAL_RE.search(item) and not re.search(
            r"special\s+permit|site\s+plan|comprehensive\s+permit|variance|notice\s+of\s+intent", item, re.I):
        action = "deal"
    if subject == "solar" and SOLAR_DISTRICT.search(local) and not re.search(
            r"solar\s+(?:array|installation|facility|project|energy\s+system|field|farm)", item, re.I):
        action = "mention"  # the only solar word is the name of an overlay district
    if action in ("project", "project_hearing", "deal") and UTILITY_WORK.search(local):
        action = "mention"  # a utility's pole or conduit petition that only names the project it serves
    a["action"] = action
    a["flags"] = flags
    a["minutes"] = bool(minutes)

    # names (nearest the matched words first), address, sizes
    names = extract_names(item, a["town"]) if action != "minutes" else []
    if names:
        placed = [(item.find(n[0].split()[0]), n) for n in names]
        lead = pick_near([(p, n) for p, n in placed if p >= 0], item, rel)
        names = ([lead] if lead else []) + [n for _, n in placed if n is not lead]
        if lead is None:
            names = []  # names in the item belong to a neighboring agenda item
    a["names"] = names
    a["address"] = extract_address(item, a["town"], rel) if action in (
        "project_hearing", "project", "continuance", "filing", "rezoning", "deal", "withdrawn") else None
    a["scale"] = extract_scale(item) if action in ("project_hearing", "project", "filing", "rezoning", "deal") else []
    a["duration"] = extract_duration(near_mor or item) if action == "moratorium" else None
    a["height"] = extract_height(item) if subject == "wireless_telecom" else None

    # base points
    key = "solar_large" if subject == "solar" and a["solar_large"] and action in PROJECT_ACTIONS else subject
    pts = SUBJECT_POINTS.get(key, 1.0)
    if action in ("moratorium", "ban"):
        pts = max(pts, SUBJECT_POINTS["moratorium"])
    mult = ACTION_MULT[action]
    if action in ("moratorium", "ban") and (flags["vote"] or flags["hearing"] or flags["warrant"]):
        mult += STRONG_ACTION_BONUS
    if action == "moratorium" and flags["tentative"]:
        mult = TENTATIVE_MULT
    if action in ("project_hearing", "project") and a["board_key"] == "conservation_commission":
        mult *= CONSERVATION_PROJECT
    a["points_key"] = key
    a["base"] = pts * mult
    a["vague"] = (len(a["snippet"]) >= 220 and action in ("mention", "discussion") and not a["names"]) or \
        junk_ratio(a["snippet"]) > 0.3


def timing_factor(a):
    if a["status"] != "live":
        return 0.0
    if a["date_source"] == "filing":
        return TIMING_FILING
    if a["days"] is None:
        return TIMING_UNDATED
    for lim, f in TIMING:
        if a["days"] <= lim:
            return f
    return TIMING_FAR


# ============================================================================ grouping

class UnionFind:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, i, j):
        ri, rj = self.find(i), self.find(j)
        if ri != rj:
            self.p[max(ri, rj)] = min(ri, rj)


POLICY_SUBJECTS = {"data_center", "battery_storage", "solar", "wind", "clean_energy_siting"}
POLICY_ACTIONS = {"moratorium", "ban", "bylaw_hearing", "bylaw_draft", "adopt", "town_meeting", "warrant_review"}


def group_keys(a):
    """Keys that put two hits in one story: the same agenda item, the same town + topic + meeting,
    the same named applicant, the same site address, or the same town's bylaw or moratorium on a subject."""
    st, town = a["state"], a["town"]
    keys = [("item",) + tuple(a["item_key"])]
    meet = a["date"].isoformat() if a["date"] else a["hit"].get("source_url")
    keys.append(("meet", st, town, a["board_key"], meet, topic_family(a["subject"])))
    for disp, key, global_scope in a["names"]:
        if len(key) >= 5:
            keys.append(("name", "*" if global_scope else f"{st}:{town}", key))
    if a["address"] and a["address"][1] and a["action"] in ("project_hearing", "project", "continuance", "filing",
                                                              "rezoning", "withdrawn"):
        keys.append(("addr", st, town, a["address"][1]))
    policy_hint = SUBJECT_RE["moratorium"].search(a["item"]) or BYLAW_RE.search(a["item"])
    if a["subject"] in POLICY_SUBJECTS and (a["action"] in POLICY_ACTIONS or (
            policy_hint and a["action"] in ("minutes", "discussion", "mention", "continuance"))):
        mor = "moratorium" if (a["action"] in ("moratorium", "ban") or SUBJECT_RE["moratorium"].search(a["item"])) else "rules"
        keys.append(("policy", st, town, a["subject"], mor))
    return keys


def group_hits(analyses):
    uf = UnionFind(len(analyses))
    first = {}
    for i, a in enumerate(analyses):
        for k in group_keys(a):
            if k in first:
                uf.union(first[k], i)
            else:
                first[k] = i
    groups = defaultdict(list)
    for i, a in enumerate(analyses):
        groups[uf.find(i)].append(a)
    return list(groups.values())


# ============================================================================ wording

SUBJECT_WORDS = {
    # noun, adjective, rules, project
    "data_center": ("data centers", "data-center", "data-center rules", "data center"),
    "battery_storage": ("battery storage", "battery storage", "battery storage rules", "battery storage project"),
    "solar": ("solar", "solar", "solar rules", "solar project"),
    "wind": ("wind energy", "wind energy", "wind energy rules", "wind project"),
    "clean_energy_siting": ("clean energy siting", "clean energy", "clean energy siting rules", "clean energy project"),
    "zoning_amendment": ("zoning changes", "zoning", "zoning changes", "zoning request"),
    "general_bylaw": ("bylaw changes", "bylaw", "bylaw changes", "bylaw change"),
    "40b_comprehensive_permit": ("40B housing", "40B", "40B rules", "40B housing plan"),
    "wireless_telecom": ("a cell tower", "cell tower", "cell tower rules", "cell tower"),
    "wetlands_filing": ("a wetlands filing", "wetlands", "wetlands rules", "wetlands filing"),
    "other": ("a moratorium", "moratorium", "local rules", "local item"),
}


def words_for(a):
    """Subject words for the lead hit, joining solar and battery storage when the item covers both."""
    s = a["subject"]
    noun, adj, rules, proj = SUBJECT_WORDS.get(s, SUBJECT_WORDS["other"])
    if s == "battery_storage" and "solar" in a["topics"] and SUBJECT_RE["solar"].search(a["item"]):
        noun, adj, rules, proj = ("solar and battery storage", "solar and battery storage",
                                  "solar and battery storage rules", "solar and battery project")
    if s == "solar":
        item = a["item"]
        kind = next((k for rx, k in [(r"carport", "solar carport"), (r"canopy", "solar canopy"),
                                     (r"roof[\s-]*(?:top|mounted)|rooftop", "rooftop solar project"),
                                     (r"landfill", "landfill solar project"),
                                     (r"dual[\s-]*use|agrivoltaic", "dual-use solar array"),
                                     (r"ground[\s-]*mount", "ground-mounted solar array"),
                                     (r"large[\s-]*scale", "large-scale solar array")] if re.search(rx, item, re.I)), None)
        if kind:
            proj = kind
    return noun, adj, rules, proj


def law_word(a):
    """The word the agenda uses for the rule ('law', 'ordinance', 'bylaw'), or None when it uses none."""
    item = a["item"]
    if re.search(r"\blocal\s+law\b", item, re.I):
        return "law"
    if re.search(r"\bordinance\b", item, re.I):
        return "ordinance"
    if re.search(r"\bby-?law\b", item, re.I):
        return "bylaw"
    return None


PERMIT_KINDS = [(r"special\s+permit", "special permit"), (r"site\s+plan(?:\s+review)?", "site plan review"),
                (r"comprehensive\s+permit", "comprehensive permit"), (r"\bvariances?\b", "variance"),
                (r"notice\s+of\s+intent|\bNOI\b", "Notice of Intent"), (r"planned\s+development", "planned development permit"),
                (r"permit\s+extension", "permit extension"), (r"\bmodif(?:y|ication)\b", "modification")]


def permit_list(item):
    found = []
    for rx, label in PERMIT_KINDS:
        if re.search(rx, item, re.I) and label not in found:
            found.append(label)
    if "permit extension" in found:
        found = ["permit extension"]
    return found[:2]


def continuance_date(item, today):
    m = re.search(r"(?:continu\w*|postpon\w*)\s+(?:the\s+hearing\s+)?(?:to|until)\s+(?:\w+day,?\s+)?"
                  r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})",
                  item, re.I)
    if not m:
        return None
    try:
        d = date(today.year, MONTH_NUM[m.group(1).lower()], int(m.group(2)))
    except ValueError:
        return None
    if d < today - timedelta(days=60):
        d = date(today.year + 1, d.month, d.day)
    return d


def lead_name(story):
    a = story["lead"]
    for x in [a] + [b for b in story["hits"] if b is not a and b["item_key"] == a["item_key"]]:
        if x["names"]:
            return x["names"][0][0]
    return None


HEADLINE_MAX = 84
DEK_MAIN_WORDS = 22  # "The board meets ..." plus "The agenda lists ..."
DEK_MAX_WORDS = 26   # with the optional "It was on the ... agenda" sentence
DEAL_KINDS = [(r"lease\s+amendment", "lease amendment"), (r"\blease\b", "lease"), (r"contract|award", "contract"),
              (r"negotiat|taxation|community\s+benefits|\bPILOT\b|payment\s+in\s+lieu", "tax talks"),
              (r"easement", "easement")]


def deal_kind(item):
    return next((w for rx, w in DEAL_KINDS if re.search(rx, item, re.I)), "agreement")


def rule_phrase(a, adj, rules, article=True, draft=False):
    """'a battery storage bylaw' when the agenda names the bylaw, ordinance or law; else 'battery storage rules'."""
    law = law_word(a)
    if a["subject"] in ("zoning_amendment", "general_bylaw") or not law:
        return f"draft {rules}" if draft else rules
    phrase = f"{'draft ' if draft else ''}{adj} {law}"
    return with_article(phrase) if article else phrase


def make_headline(story):
    """Headline from fixed templates, chosen by action and subject. Each template states only what the
    agenda text shows; when one runs over HEADLINE_MAX characters the next, plainer one is used."""
    a = story["lead"]
    T = a["town"]
    B, pl = board_phrase(a["board_key"], a["board"])
    Bp = a["board"]
    noun, adj, rules, proj = words_for(a)
    act, f = a["action"], a["flags"]
    name = lead_name(story)
    addr = a["address"][0] if a["address"] else None
    scale = a["scale"]  # sizes in the lead item only; other hits' sizes appear in reasons
    options = []

    def v(w):
        return verb(w, pl)

    if act == "filing":
        mw = next((s[1] for s in scale if s[2] == "MW"), None)
        what = f"{mw} {proj.replace(' project', '')}" if mw else proj
        if name and re.search(r"\b(?:build|construct|install)", a["item"], re.I):
            options.append(f"{name} files to build {what} in {T}")
        options.append(f"{T} wetlands filing lists {with_article(what)}")
    elif act == "moratorium":
        dur = f"{a['duration']} " if a["duration"] else ""
        obj = with_article(f"{'draft ' if f['draft'] and not f['hearing'] else ''}{dur}{adj} moratorium")
        if f["tentative"]:
            options.append(f"{T} {B} {v('discuss')} a possible {adj} moratorium")
        elif a["board_key"] == "town_meeting":
            options.append(f"{T} Town Meeting takes up {obj}")
        elif f["hearing"]:
            options.append(f"{T} {B} {v('hold')} hearing on {obj}")
        elif f["vote"]:
            options.append(f"{T} {B} {v('vote')} on {obj}")
        elif f["warrant"]:
            options.append(f"{T} {B} {v('review')} Town Meeting article on {obj}")
        elif f["draft"]:
            options.append(f"{T} {B} {v('discuss')} {obj}")
        options.append(f"{T} weighs {obj}")
        options.append(f"{T} weighs {with_article(adj + ' moratorium')}")
    elif act == "ban":
        if f["petition"]:
            options.append(f"{T} {B} {v('take')} up petition to prohibit {noun}")
        if a["board_key"] == "town_meeting":
            options.append(f"{T} Town Meeting weighs prohibiting {noun}")
        if f["hearing"]:
            options.append(f"{T} {B} {v('hold')} hearing on prohibiting {noun}")
        options.append(f"{T} {B} {v('consider')} prohibiting {noun}")
        options.append(f"{T} weighs prohibiting {noun}")
    elif act == "town_meeting":
        options.append(f"{T} Town Meeting takes up {rules}")
    elif act == "warrant_review":
        options.append(f"{T} {B} {v('review')} Town Meeting article on {rules}")
        options.append(f"{T} {B} {v('review')} {rules} article")
    elif act == "adopt":
        options.append(f"{T} {B} {v('consider')} adopting {rule_phrase(a, adj, rules)}")
    elif act == "bylaw_hearing":
        options.append(f"{T} {B} {v('hold')} hearing on {rule_phrase(a, adj, rules)}")
        options.append(f"{T} {B} {v('hold')} hearing on {rules}")
    elif act == "bylaw_draft":
        if f["draft"] and a["subject"] not in ("zoning_amendment", "general_bylaw"):
            options.append(f"{T} {B} {v('review')} {rule_phrase(a, adj, rules, draft=True)}")
        options.append(f"{T} {B} {v('discuss')} {rules}")
    elif act == "rezoning":
        verb_ = v("hear") if f["hearing"] else v("take") + " up"
        if addr and a["address"][1]:
            options.append(f"{T} {B} {verb_} rezoning request for {addr}")
        elif addr:
            options.append(f"{T} {B} {verb_} rezoning of land on {addr}")
        options.append(f"{T} {B} {verb_} a rezoning request")
    elif act in ("project_hearing", "project"):
        hear = f["hearing"] and act == "project_hearing"
        verb_ = v("hear") if hear else v("review")
        units = next((s for s in scale if s[2] == "units"), None)
        if a["subject"] == "40b_comprehensive_permit":
            kind = "rental plan" if re.search(r"\brental", a["item"], re.I) else \
                "apartment plan" if re.search(r"apartment", a["item"], re.I) else "housing plan"
            if units:
                n = fmt_num(units[3])
                if addr:
                    options.append(f"{T} {B} {verb_} {n}-unit 40B {kind} for {addr}")
                options.append(f"{T} {B} {verb_} {n}-unit 40B {kind}")
            if name:
                options.append(f"{T} {B} {verb_} {name} 40B request")
            if addr:
                options.append(f"{T} {B} {verb_} 40B request for {addr}")
            options.append(f"{T} {B} {v('hold')} 40B hearing" if hear else f"{T} {B} {verb_} a 40B request")
        elif a["subject"] == "wireless_telecom":
            tower = f"{a['height']} cell tower" if a["height"] else "cell tower"
            if re.search(r"modif", a["item"], re.I) and not a["height"]:
                tower = "wireless facility change"
            if addr:
                options.append(f"{T} {B} {verb_} request for {tower} at {addr}")
            options.append(f"{T} {B} {verb_} request for {tower}")
        elif a["subject"] in ("zoning_amendment", "general_bylaw"):
            if name:
                options.append(f"{T} {B} {verb_} {name} zoning request")
            if addr:
                options.append(f"{T} {B} {verb_} zoning request for {addr}")
            options.append(f"{T} {B} {verb_} a zoning request")
        else:
            req = "permit extension" if f["extension"] else "petition" if f["petition"] else \
                "wetlands filing" if re.search(r"notice\s+of\s+intent|\bNOI\b", a["item"], re.I) else \
                "variance request" if re.search(r"\bvariance", a["item"], re.I) and not re.search(
                    r"special\s+permit|site\s+plan", a["item"], re.I) else "permit request"
            if name and f["extension"]:
                options.append(f"{T} {B} {v('take')} up {name} {adj} {req}")
            if name:
                options.append(f"{T} {B} {verb_} {name} {req}")
            if addr:
                options.append(f"{T} {B} {verb_} {req} for {proj} at {addr}")
            options.append(f"{T} {B} {verb_} {req} for {with_article(proj)}")
    elif act == "continuance":
        d = continuance_date(a["item"], story["today"])
        who = name or (f"{proj} at {addr}" if addr else None)
        if name and d and re.search(r"request", a["item"], re.I):
            options.append(f"{name} asks {T} {B} for continuance to {short_date(d)}")
        if who:
            options.append(f"{T} {Bp} agenda lists continuance of {who} hearing")
        options.append(f"{T} {Bp} agenda lists continuance of {with_article(proj)} hearing")
    elif act == "deal":
        deal = deal_kind(a["item"])
        obj = proj.replace(" project", "")
        money = next((s[1] for s in scale if s[2] == "dollars"), None)
        if deal == "tax talks":
            options.append(f"{T} {Bp} agenda lists {name or obj} tax talks")
        elif money and deal == "contract":
            options.append(f"{T} {Bp} {verb('take', False)} up {with_article(money + ' ' + obj + ' ' + deal)}")
        options.append(f"{T} {Bp} {verb('take', False)} up {with_article(obj + ' ' + deal)}")
    elif act == "process":
        what = "state clean energy permit process"
        if f["vote"]:
            options.append(f"{T} {Bp} {verb('vote', False)} on {what}")
        options.append(f"{T} {Bp} {verb('take', False)} up {what}")
    elif act == "discussion":
        options.append(f"{T} {B} {v('discuss')} {noun}")
    elif act == "cancelled":
        when = f"{short_date(a['date'])} " if a["date"] else ""
        options.append(f"{T} {B} {v('cancel')} {when}hearing on {rules}")
    elif act == "withdrawn":
        options.append(f"{T} {Bp} agenda lists withdrawal of {name or with_article(proj)}")
    # last resort: "Battery storage item on Holyoke Planning Board agenda"
    options.append(f"{first_cap(adj)} item on {T} {Bp} {'warrant' if a['board_key'] == 'town_meeting' else 'agenda'}")
    for o in options:
        o = re.sub(r"\s+", " ", o).strip()
        if len(o) <= HEADLINE_MAX:
            return first_cap(o)
    return first_cap(options[-1])


def make_dek(story):
    """One or two short sentences: when the board meets and what the agenda lists."""
    a = story["lead"]
    T = a["town"]
    noun, adj, rules, proj = words_for(a)
    act, f = a["action"], a["flags"]
    name = lead_name(story)
    addr = a["address"][0] if a["address"] and a["address"][1] else None
    tm = a["board_key"] == "town_meeting"
    src = "warrant" if tm or a["date_source"] == "warrant" else "agenda"

    if a["date_source"] == "filing":
        s1 = f"MassDEP lists the Notice of Intent as filed {short_date(a['date'])}." if a["date"] else \
            "MassDEP lists the Notice of Intent."
    elif a["date"] is None:
        s1 = f"The warrant for {T}'s {'fall ' if a['hint'] == 'fall' else ''}Town Meeting gives no date."
    elif tm or a["date_source"] == "warrant":
        s1 = f"{T}'s Town Meeting is {long_date(a['date'])}."
    else:
        s1 = f"The {a['board']} meets {long_date(a['date'])}."

    whats = []
    permits = permit_list(a["item"])
    if act == "moratorium":
        state = "a draft " if f["draft"] else "a possible " if f["tentative"] else "a proposed " if f["proposed"] else "a "
        core = f"{state}{'temporary ' if f['temporary'] else ''}moratorium on {noun}"
        if f["hearing"]:
            whats.append("a public hearing on " + core)
        elif f["vote"]:
            whats.append("a vote on " + core)
        elif tm or f["warrant"]:
            whats.append("an article proposing " + core.replace("a proposed ", "a "))
        whats.append(core)
    elif act == "ban":
        core = f"{'a petition' if f['petition'] else 'a proposal'} to prohibit {noun}"
        whats.append(("a public hearing on " if f["hearing"] else "") + core)
        whats.append(core)
    elif act in ("town_meeting", "warrant_review"):
        whats.append(f"an article on {rules}")
    elif act == "adopt":
        law = rule_phrase(a, adj, rules)
        whats.append(f"a resolution adopting {law}" if re.search(r"resolution", a["item"], re.I) else f"adoption of {law}")
    elif act == "bylaw_hearing":
        whats.append(f"a public hearing on {rule_phrase(a, adj, rules)}")
        whats.append(f"a public hearing on {rules}")
    elif act == "bylaw_draft":
        if f["draft"] and a["subject"] not in ("zoning_amendment", "general_bylaw"):
            whats.append(rule_phrase(a, adj, rules, draft=True) if law_word(a) else f"draft {rules}")
        whats.append(f"an item on {rules}")
    elif act == "rezoning":
        whats.append(("a public hearing on " if f["hearing"] else "") + "a rezoning request" +
                     (f" for {addr}" if addr else ""))
        whats.append("a rezoning request")
    elif act in ("project_hearing", "project"):
        who = name or with_article(proj)
        units = next((s for s in a["scale"] if s[2] == "units"), None)
        if a["subject"] == "40b_comprehensive_permit":
            who = (f"{fmt_num(units[3])} units" if units else "40B housing") + (f" by {name}" if name else "")
        elif a["subject"] == "wireless_telecom":
            who = f"a {a['height']} cell tower" if a["height"] else "a wireless facility"
        elif a["subject"] in ("zoning_amendment", "general_bylaw"):
            who = name or "a property"
        kinds = with_article(" and ".join(permits)) if permits else "an application"
        lead_in = "a public hearing on " if act == "project_hearing" and f["hearing"] else ""
        if addr:
            whats.append(f"{lead_in}{kinds} for {who} at {addr}")
        whats.append(f"{lead_in}{kinds} for {who}")
        whats.append(f"{kinds} for {who}")
    elif act == "filing":
        mw = next((s[1] for s in a["scale"] if s[2] == "MW"), None)
        what = with_article(f"{mw} {proj.replace(' project', '')}" if mw else proj)
        whats.append(f"{what} at {addr}" if addr else what)
        whats.append(what)
    elif act == "continuance":
        d = continuance_date(a["item"], story["today"])
        whats.append(f"a request to continue the {name + ' ' if name else ''}hearing" + (f" to {short_date(d)}" if d else ""))
        whats.append("a request to continue the hearing")
    elif act == "deal":
        deal = deal_kind(a["item"])
        if deal == "tax talks":
            whats.append(f"an item on tax and benefits talks for {name or with_article(proj)}")
        else:
            whats.append(f"{with_article(deal)} for {with_article(proj)}")
    elif act == "process":
        whats.append("a vote on the state's consolidated permit process" if f["vote"] else
                     "an item on the state's consolidated permit process")
    elif act == "discussion":
        whats.append(f"a discussion of {noun}")
    elif act == "cancelled":
        whats.append("a notice that the hearing is canceled")

    if act == "filing":
        s2 = next((f"The filing describes {w}." for w in whats
                   if len((s1 + " The filing describes " + w).split()) <= DEK_MAIN_WORDS), "")
    elif whats:
        s2 = next((f"The {src} lists {w}." for w in whats
                   if len((s1 + f" The {src} lists " + w).split()) <= DEK_MAIN_WORDS), f"The {src} lists {whats[-1]}.")
    else:
        s2 = f"The {src} lists an item on {noun}."
    dek = (s1 + " " + s2).strip()
    other = [b for b in story["boards"] if (b["town"], b["board"]) != (T, a["board"]) and not b["minutes_only"]]
    if other:
        b = other[0]
        where = f"the {b['town']} {b['board']}" if b["town"] != T else f"the {b['board']}"
        doc = "warrant" if b["board_key"] == "town_meeting" else "agenda"
        if b["board_key"] == "town_meeting":
            where = f"{b['town']}'s Town Meeting" if b["town"] != T else "the Town Meeting"
        if b["date"] and b["date"] >= story["today"]:
            extra = f"It is also on {where} {doc} for {short_date(b['date'])}."
        elif b["date"]:
            extra = f"It was on {where} {doc} {short_date(b['date'])}."
        else:
            extra = ""
        if extra and len((dek + " " + extra).split()) <= DEK_MAX_WORDS:
            dek = dek + " " + extra
    return dek


def make_quote(story):
    a = story["lead"]
    keys = []
    name = lead_name(story)
    for t in a["subjects"] or [a["subject"]]:
        if t == "zoning_amendment" and a["subject"] != "general_bylaw":
            keys.append(ZONING_KEY)  # "ordinance" alone also matches parking and dog bylaws
        elif t in SUBJECT_RE:
            keys.append(SUBJECT_RE[t])
    if a["action"] in ("moratorium",):
        keys.insert(0, SUBJECT_RE["moratorium"])
    prefer = {
        "moratorium": SUBJECT_RE["moratorium"], "ban": BAN_RE, "continuance": CONTINUANCE_RE,
        "project_hearing": re.compile(r"permit|site\s+plan|hearing|application|petition|request|notice\s+of\s+intent", re.I),
        "project": re.compile(r"permit|request|application|extension|notice\s+of\s+intent", re.I),
        "filing": re.compile(r"build|construct|install|propos", re.I),
        "bylaw_hearing": BYLAW_RE, "bylaw_draft": BYLAW_RE, "adopt": ADOPT_RE, "town_meeting": TM_ARTICLE_RE,
        "warrant_review": BYLAW_RE, "rezoning": REZONE_RE, "cancelled": CANCEL_RE, "process": CONSOLIDATED_RE,
        "deal": DEAL_RE,
    }.get(a["action"])
    return pick_quote(a["item"], keys, prefer, a["snippet"], name=name)


# ============================================================================ scoring

def history_index(history):
    idx = defaultdict(list)
    for st, town, topic, d in history:
        idx[(st, town, topic)].append(d)
    return idx


def is_first(story, inputs, hist):
    a = story["lead"]
    topic = "moratorium" if a["action"] in ("moratorium", "ban") and a["subject"] not in SITING else a["subject"]
    if topic not in FIRST_POINTS or a["action"] in ("mention", "minutes", "continuance", "cancelled", "withdrawn"):
        return None
    dates = [x["date"] for x in story["hits"] if x["date"]]
    if not dates:
        return None
    earliest = min(dates)
    cov = inputs["coverage"].get((a["state"], a["town"]))
    if not cov or (earliest - cov).days < FIRST_MIN_HISTORY_DAYS:
        return None
    own = {(x["state"], x["town"], x["date"]) for x in story["hits"]}
    for d in hist.get((a["state"], a["town"], topic), []):
        if d is None:
            return None
        if d < earliest and (a["state"], a["town"], d) not in own:
            return None
    return topic


TRACKER_VOTED = {"Adopted", "Approved by AG", "Disapproved by AG", "In effect", "Expired", "Pending at Legislature",
                 "Rejected", "Enacted"}
AG_TECH = {"BESS": {"battery_storage"}, "solar": {"solar"}, "both": {"battery_storage", "solar"}}


def tracker_reason(story, inputs):
    """'Town has an earlier vote on this' when tracker.json records a vote by the town on the same subject."""
    a = story["lead"]
    if a["state"] != "MA":
        return None
    for t in inputs["tracker"]:
        if t.get("town") != a["town"] or t.get("status") not in TRACKER_VOTED:
            continue
        topic = (t.get("topic") or "").lower()
        if any(SUBJECT_RE[s].search(topic) for s in (a["subjects"] or [a["subject"]]) if s in SUBJECT_RE):
            return "Town has an earlier vote on this"
    return None


def ag_reason(story, inputs, today):
    a = story["lead"]
    if a["state"] != "MA":
        return None
    for r in sorted(inputs["ag"], key=lambda r: r.get("decision_date") or "", reverse=True):
        town = re.sub(r"\s*\(city\)$", "", r.get("town") or "")
        if town != a["town"] or not str(r.get("outcome", "")).lower().startswith(("disapproved", "ag disapproval")):
            continue
        d = parse_date(r.get("decision_date"))
        if not d or (today - d).days > AG_DAYS or d > today:
            continue
        tech = AG_TECH.get(r.get("technology"), set())
        if not (tech & set(a["subjects"] or [a["subject"]])):
            continue
        what = {"BESS": "battery storage", "solar": "solar", "both": "solar and battery storage"}[r["technology"]]
        kind = "moratorium" if "moratorium" in (r.get("bylaw_type") or "") else "bylaw"
        return f"AG disapproved {a['town']}'s {what} {kind} on {short_date(d)}"
    return None


ACTION_REASON = {
    "town_meeting": "Town Meeting vote", "adopt": "Adoption vote", "bylaw_hearing": "Public hearing",
    "bylaw_draft": "Draft rules", "project_hearing": "Public hearing", "rezoning": "Rezoning request",
    "warrant_review": "Town Meeting article", "project": "Permit application", "filing": "State wetlands filing",
    "continuance": "Continuance requested", "cancelled": "Hearing canceled", "withdrawn": "Withdrawn",
}  # discussion, mention and process items get no action reason


def action_reason(a):
    """What is happening, in a reader's words ('Moratorium vote', 'Public hearing')."""
    act, f = a["action"], a["flags"]
    if act == "moratorium":
        if f["tentative"]:
            return "Possible moratorium"
        if f["vote"] or a["board_key"] == "town_meeting":
            return "Moratorium vote"
        return "Moratorium hearing" if f["hearing"] else "Proposed moratorium"
    if act == "ban":
        return "Public hearing on a ban" if f["hearing"] else "Proposed ban"
    if act == "project_hearing" and f["continued"]:
        return "Continued public hearing"
    if act == "deal":
        kind = deal_kind(a["item"])
        return {"lease": "Town lease", "lease amendment": "Town lease", "contract": "Town contract",
                "easement": "Easement"}.get(kind, "")
    return ACTION_REASON.get(act, "")


def timing_reason(a):
    """'Hearing Oct 20', 'Town Meeting Oct 17', 'Filed Sep 30': a date, never 'tomorrow' (the page adds that)."""
    if a["date_source"] == "filing":
        return f"Filed {short_date(a['date'])}" if a["date"] else None
    if a["date"] is None:
        return "Town Meeting date not in the warrant"
    act = a["action"]
    if a["board_key"] == "town_meeting":
        event = "Town Meeting"
    elif act == "adopt" or (act in ("moratorium", "ban", "process") and a["flags"]["vote"]):
        event = "Vote"
    elif a["flags"]["hearing"] and act in ("moratorium", "ban", "bylaw_hearing", "project_hearing", "rezoning"):
        event = "Hearing"
    else:
        event = "Meeting"
    return f"{event} {short_date(a['date'])}"


def momentum_reasons(story, lead, inputs):
    """'3 town boards', 'Neighboring towns too' or 'Also in Plympton', 'Also on the Sep 23 agenda'."""
    out = []
    towns = [t for t in story["towns"] if t != f"{lead['state']}:{lead['town']}"]
    if towns:
        near = set((inputs.get("neighbors") or {}).get(f"{lead['state']}:{lead['town']}", []))
        if all(t in near for t in towns):
            out.append("Neighboring towns too" if len(towns) > 1 else f"Neighboring {towns[0].split(':', 1)[1]} too")
        elif len(towns) == 1:
            out.append(f"Also in {towns[0].split(':', 1)[1]}")
        else:
            out.append(f"Also in {len(towns)} other towns")
    boards = [b for b in story["boards"] if b["town"] == lead["town"] and not b["minutes_only"]]
    if len(boards) > 1:
        city = any(re.search(r"\bcity\b", b["board"], re.I) for b in boards)
        out.append(f"{len(boards)} {'city' if city else 'town'} boards")
    elif not towns:
        other = sorted({x["date"] for x in story["hits"] if x["date"] and x["date"] != lead["date"]
                        and x["status"] != "stale" and x["action"] != "minutes" and x["source"] == "agenda"
                        and (x["town"], x["board_key"]) == (lead["town"], lead["board_key"])},
                       key=lambda d: abs((d - (lead["date"] or d)).days))
        if other:
            out.append(f"Also on the {short_date(other[0])} agenda")
    filings = sorted(x["date"] for x in story["hits"] if x["source"] != "agenda" and x["date"] and x is not lead
                     and x["status"] != "stale")
    if filings:
        out.append(f"State wetlands filing {short_date(filings[-1])}")
    return out


def build_story(hits, inputs, hist, today, now):
    live = [a for a in hits if a["status"] == "live"]
    if not live:
        return None
    if all(a["subject"] == "wetlands_filing" for a in live):
        return None
    for a in live:
        a["total"] = a["base"] * timing_factor(a)
    lead = max(live, key=lambda a: (a["total"], -(a["days"] if a["days"] is not None else 99), bool(a["names"])))
    same_meeting = [a for a in hits if a["date"] == lead["date"] and a["board_key"] == lead["board_key"]
                    and a["town"] == lead["town"]]
    if any(a["action"] == "cancelled" for a in same_meeting) and lead["action"] != "cancelled":
        cancelled = next(a for a in same_meeting if a["action"] == "cancelled")
        lead = dict(lead, action="cancelled", base=lead["base"] / ACTION_MULT[lead["action"]] * ACTION_MULT["cancelled"],
                    item=cancelled["item"], snippet=cancelled["snippet"])
    if lead["action"] == "minutes":
        return None  # minutes of an earlier meeting printed in a packet only count toward other stories
    story = {"lead": lead, "hits": hits, "today": today}

    # one entry per board: its next upcoming meeting, else its latest past one; minutes_only marks a board
    # that appears only through minutes printed in a packet
    boards = {}
    for a in sorted(hits, key=lambda a: (a["status"] != "live",
                                         (a["date"] or date.max).toordinal() * (1 if a["status"] == "live" else -1))):
        if a["status"] == "stale":
            continue
        k = (a["state"], a["town"], a["board_key"] or a["board"])
        if k not in boards:
            boards[k] = {"town": a["town"], "board": a["board"], "board_key": a["board_key"], "date": a["date"],
                         "minutes_only": True}
        if a["action"] != "minutes":
            boards[k]["minutes_only"] = False
    story["boards"] = list(boards.values())
    towns = sorted({f"{a['state']}:{a['town']}" for a in hits if a["status"] != "stale"})
    meetings = {(a["town"], a["board_key"], a["date"]) for a in hits
                if a["status"] != "stale" and a["action"] != "minutes" and a["source"] == "agenda"}
    story["n_boards"] = sum(1 for b in boards.values() if not b["minutes_only"])
    story["n_towns"] = len(towns)
    story["towns"] = towns

    scale = []
    for a in hits:
        if a["status"] != "stale" and (a["item_key"] == lead["item_key"] or a["names"] and lead["names"]
                                      and a["names"][0][1] == lead["names"][0][1]):
            scale.extend(a["scale"])
    scale.sort(key=lambda s: -s[0])
    story["scale"] = scale

    reasons, bonus = [], 0.0
    reasons.append(action_reason(lead))
    first = is_first(story, inputs, hist)
    if first:
        bonus += FIRST_POINTS[first]
        reasons.append(f"First time this has come up in {lead['town']}")
    if scale and lead["action"] not in ("continuance", "minutes", "cancelled", "withdrawn"):
        bonus += scale[0][0]
        reasons.append(first_cap(scale[0][1]))
    extra_b = min(MOMENTUM_CAP, story["n_boards"] - 1)
    extra_t = min(MOMENTUM_CAP, story["n_towns"] - 1)
    extra_m = min(2, len(meetings) - 1) if extra_b == 0 else 0
    bonus += extra_b * MOMENTUM_BOARD + extra_t * MOMENTUM_TOWN + extra_m * MOMENTUM_MEETING
    reasons.extend(momentum_reasons(story, lead, inputs))
    tr = timing_reason(lead)
    if tr:
        reasons.append(tr)
    seen = [parse_ts(a["first_seen"]) for a in hits if a["first_seen"]]
    seen = [s for s in seen if s]
    first_seen = min(seen) if seen else None
    is_new = bool(first_seen and (now - first_seen) <= timedelta(hours=NEW_HOURS))
    if is_new:
        bonus += NEW_POINTS  # no reason line: the page shows how new an item is
    trk = tracker_reason(story, inputs)
    if trk:
        bonus += TRACKER_POINTS
        reasons.append(trk)
    ag = ag_reason(story, inputs, today)
    if ag:
        bonus += AG_POINTS
        reasons.append(ag)
    # routine leads (mentions, minutes, continuances) keep only part of their bonuses, so momentum or a
    # tracker entry cannot lift a passing mention above a real hearing
    bonus *= min(1.0, ACTION_MULT[lead["action"]] / ROUTINE_BONUS_FLOOR)
    if lead["vague"]:
        bonus -= VAGUE_PENALTY
    score = max(0.05, (lead["base"] + bonus) * timing_factor(lead))

    story["score"] = score
    story["reasons"] = [r for r in reasons if r]
    story["first_seen"] = first_seen
    story["is_new"] = is_new
    return story


def story_id(story):
    hs = sorted(story["hits"], key=lambda a: (a["first_seen"] or "", a["id"]))
    a = story["lead"]
    return hashlib.sha1(f"{a['state']}|{a['town']}|{hs[0]['id']}".encode()).hexdigest()[:12]


def to_json(story):
    a = story["lead"]
    topics = sorted({t for x in story["hits"] if x["status"] != "stale" for t in x["topics"]})
    return {
        "id": story_id(story),
        "score": round(story["score"], 2),
        "headline": story["headline"],
        "dek": story["dek"],
        "quote": story["quote"],
        "reasons": story["reasons"],
        "topics": topics,
        "state": a["state"],
        "town": a["town"],
        "county": a["county"],
        "towns": story["towns"],
        "board": a["board_raw"],
        "board_key": a["board_key"],
        "meeting_date": a["date"].isoformat() if a["date"] else None,
        "meeting_date_source": a["date_source"],
        "days_until": a["days"],
        "first_seen": story["first_seen"].isoformat() if story["first_seen"] else None,
        "is_new": story["is_new"],
        "source_url": a["hit"].get("source_url"),
        "town_path": town_path(a["state"], a["town"]),
        "action": a["action"],
        "boards": [{"town": b["town"], "board": b["board"], "board_key": b["board_key"],
                    "meeting_date": b["date"].isoformat() if b["date"] else None} for b in story["boards"]],
        "hit_ids": sorted(x["id"] for x in story["hits"]),
    }


def build(inputs, today, now, limit=TOP_N):
    hits_doc = inputs["hits_doc"]
    analyses = [analyze_hit(h, inputs, today) for h in hits_doc.get("hits", [])]
    analyses = [a for a in analyses if a["status"] != "stale"]
    hist = history_index(inputs["history"])
    stories = []
    for group in group_hits(analyses):
        s = build_story(group, inputs, hist, today, now)
        if s:
            s["headline"] = make_headline(s)
            s["dek"] = make_dek(s)
            s["quote"] = make_quote(s)
            stories.append(s)
    stories.sort(key=lambda s: (-s["score"], s["lead"]["date"] or date.max, s["lead"]["town"]))
    stories = stories[:limit]
    ends = [s["lead"]["date"] for s in stories if s["lead"]["date"]]
    window_end = (hits_doc.get("window") or {}).get("end") or (max(ends).isoformat() if ends else today.isoformat())
    return {
        "generated": now.replace(microsecond=0).isoformat(),
        "window": {"start": today.isoformat(), "end": window_end},
        "personalize": PERSONALIZE,
        "stories": [to_json(s) for s in stories],
    }


# ============================================================================ personalization (reference)

def personalize(stories, my_towns, neighbors=None, my_topics=()):
    """The page's re-ranking, in Python for tests and previews. my_towns are site town ids ("MA:Carver").
    score x (1 + 2*in_my_towns + 1*in_neighbor_towns) x (1 + 0.5*topic_match)"""
    mine = set(my_towns or ())
    near = set()
    for t in mine:
        near.update((neighbors or {}).get(t, []))
    near -= mine
    topics = set(my_topics or ())
    out = []
    for s in stories:
        towns = set(s.get("towns") or [f"{s['state']}:{s['town']}"])
        in_mine = 1 if towns & mine else 0
        in_near = 1 if towns & near else 0
        match = 1 if topics & set(s.get("topics") or []) else 0
        k = (1 + PERSONALIZE["in_my_towns"] * in_mine + PERSONALIZE["in_neighbor_towns"] * in_near) * \
            (1 + PERSONALIZE["topic_match"] * match)
        out.append((s["score"] * k, s))
    out.sort(key=lambda x: -x[0])
    return [dict(s, personal_score=round(p, 2)) for p, s in out]


# ============================================================================ CLI

def copy_lines(result):
    lines = []
    for s in result["stories"]:
        lines.append(s["headline"])
        lines.append(s["dek"])
        lines.extend(s["reasons"])
        lines.append("")
    return "\n".join(lines) + "\n"


def print_stories(stories, n, out=sys.stdout):
    for i, s in enumerate(stories[:n], 1):
        score = s.get("personal_score", s["score"])
        out.write(f"{i:>3}. [{score:6.2f}] {s['headline']}\n")
        out.write(f"     {s['dek']}\n")
        out.write(f"     \"{s['quote']}\"\n")
        out.write(f"     {'; '.join(s['reasons'])}\n")
        out.write(f"     {s['state']} {s['town']} | {s['board']} | {s['meeting_date']} | {s['action']} | "
                  f"{len(s['hit_ids'])} hits | {s['source_url']}\n\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--data", default=DATA, help="data directory (default: next to this file)")
    p.add_argument("--out", default=None, help="output path (default: <data>/trending.json)")
    p.add_argument("--today", default=None, help="YYYY-MM-DD (default: today in America/New_York)")
    p.add_argument("--now", default=None, help="ISO timestamp for 'new in the last 72 hours' (default: now)")
    p.add_argument("--limit", type=int, default=TOP_N)
    p.add_argument("--print", dest="show", type=int, default=0, help="print the top N stories")
    p.add_argument("--copy", default=None, help="write headlines, deks and reasons to this text file")
    p.add_argument("--towns", default="", help="preview: comma-separated town ids, e.g. MA:Carver")
    p.add_argument("--topics", default="", help="preview: comma-separated topic keys")
    p.add_argument("--dry-run", action="store_true", help="do not write trending.json")
    args = p.parse_args(argv)

    now = parse_ts(args.now) if args.now else datetime.now(timezone.utc)
    today = date.fromisoformat(args.today) if args.today else now.astimezone(TZ).date()
    inputs = load_inputs(args.data)
    result = build(inputs, today, now, args.limit)
    out = args.out or os.path.join(args.data, "trending.json")
    if not args.dry_run:
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, out)
    if args.copy:
        with open(args.copy, "w", encoding="utf-8") as f:
            f.write(copy_lines(result))
    stories = result["stories"]
    if args.towns or args.topics:
        towns = [t.strip() for t in args.towns.split(",") if t.strip()]
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
        stories = personalize(stories, towns, inputs["neighbors"], topics)
    if args.show:
        print_stories(stories, args.show)
    sys.stderr.write(f"trending: {len(result['stories'])} stories"
                     f"{'' if args.dry_run else ' -> ' + os.path.relpath(out)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
