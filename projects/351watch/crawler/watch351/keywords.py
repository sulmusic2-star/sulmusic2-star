"""Topic keyword groups and snippet extraction.

Each topic is a list of case-insensitive regexes. `find_hits(text)` returns
one entry per distinct passage: the snippet (<= 240 chars, whitespace
cleaned) plus every topic that matches inside that snippet.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

# Fingerprint of the matching rules in this file. The daily engine stores it with each
# indexed document; when it changes, documents whose body is still in the local cache
# are re-matched (no network), so rule changes reach recent agendas.
MATCHER_VERSION = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:10]

TOPICS: dict[str, list[str]] = {
    "battery_storage": [
        r"\bbatter(?:y|ies)\b",
        r"\bBESS\b",
        r"\benergy[\s-]+storage\b",
    ],
    "solar": [
        r"\bsolar\b",
        r"\bphotovoltaics?\b",
        r"\bPV\b",
    ],
    "moratorium": [
        r"\bmorator(?:ium|ia|iums)\b",
    ],
    "clean_energy_siting": [
        r"\bconsolidated\s+(?:local\s+)?permit",
        r"\b225\s*CMR\s*29\b",
        r"\bclean\s+energy\s+infrastructure\b",
    ],
    "40b_comprehensive_permit": [
        r"\b40\s?B\b",
        r"\bcomprehensive\s+permits?\b",
    ],
    # Siting phrases only: bare "wireless"/"telecommunications" mostly hits
    # voter-ID boilerplate ("wireless telephone statement") and IT purchases.
    "wireless_telecom": [
        r"\b(?:personal\s+)?wireless\s+(?:communications?\s+|telecommunications?\s+|service\s+)*"
        r"(?:facilit(?:y|ies)|towers?|structures?|antennas?|installations?|by-?laws?|ordinances?)\b",
        r"\bsmall[\s-]+cells?\b",
        r"\bcell(?:ular)?\s+(?:phone\s+)?towers?\b",
        r"\bmonopoles?\b",
        r"\btelecommunications?\s+(?:towers?|facilit(?:y|ies)|structures?|antennas?|by-?laws?)\b",
    ],
    "data_center": [
        r"\bdata[\s-]+cent(?:er|re)s?\b",
        r"\bhyperscale\b",
        r"\b(?:crypto(?:currency)?|bitcoin)\s+mining\b",
    ],
    "zoning_amendment": [
        r"\bzoning\s+(?:by-?law\s+|ordinance\s+|map\s+)?amendments?\b",
        r"\b(?:by-?law|ordinance)\s+amendments?\b",
        r"\bamend(?:ing|ment|ments)?\s+(?:to\s+)?(?:the\s+)?(?:\w+\s+){0,2}zoning\s+(?:by-?laws?|ordinances?|maps?)\b",
    ],
}

TOPIC_LABELS = {
    "battery_storage": "Battery storage",
    "solar": "Solar",
    "moratorium": "Moratorium",
    "clean_energy_siting": "Consolidated permit / 225 CMR 29 / clean energy infrastructure",
    "40b_comprehensive_permit": "40B / comprehensive permit",
    "wireless_telecom": "Wireless / cell tower / telecom",
    "data_center": "Data center / crypto mining",
    "zoning_amendment": "Zoning / bylaw amendment",
}

_COMPILED = {t: [re.compile(p, re.I) for p in pats] for t, pats in TOPICS.items()}

# Matches that look like keywords but are not. Each rule: (keyword regex,
# test(text, match) -> True when the match is a false positive).
_STORAGE_CONTEXT = re.compile(r"storage|\bBESS\b|\bMWh?\b|kWh|megawatt|substation|interconnection|solar", re.I)
_NOT_STORAGE = re.compile(r"electric vehicle|\bBEVs?\b|recycl|collection|hazardous|voltage|smoke|drone|camera", re.I)


def _around(text: str, m: re.Match, before: int, after: int) -> str:
    return text[max(0, m.start() - before):m.end() + after]


_FALSE_POSITIVE = [
    # "Lot 40B", "Map 40B", "Route 40B"
    (re.compile(r"40\s?B", re.I),
     lambda t, m: re.search(r"(?:lot|map|parcel|unit|#|route|rte\.?|plat)\s*$", t[max(0, m.start() - 12):m.start()], re.I)),
    # bare "battery" without energy-storage context: EV fleets, battery recycling, drone checklists
    (re.compile(r"batter(?:y|ies)", re.I),
     lambda t, m: not _STORAGE_CONTEXT.search(_around(t, m, 80, 80)) or _NOT_STORAGE.search(_around(t, m, 40, 40))),
    # "PV" inside a list of zoning-district abbreviations: "(RR, SR, PV, WSP)"
    (re.compile(r"PV", re.I),
     lambda t, m: re.search(r"[,(&/]\s*PV\s*[,)&/]", _around(t, m, 3, 3), re.I)),
    # "Solar Salt" (road/water-softener salt bids)
    (re.compile(r"solar", re.I),
     lambda t, m: re.match(r"solar\s+salt\b", t[m.start():m.start() + 20], re.I)),
    # bond / contract boilerplate: "bankruptcy, insolvency, reorganization, moratorium"
    (re.compile(r"morator(?:ium|ia|iums)", re.I),
     lambda t, m: re.search(r"bankruptcy|insolvency|reorganization|creditors", _around(t, m, 60, 60), re.I)),
]

# ----------------------------------------------------------------------------
# State-specific patterns (Michigan, Virginia). They are matched only when find_hits /
# topics_in are given that state, so calls without a state (Massachusetts, NY, RI) keep
# exactly the matches above. They map onto the existing topic keys (ARCHITECTURE.md):
#
# * clean_energy_siting: the state siting route or permit for an energy facility, i.e. what
#   225 CMR 29 is in MA: MI PA 233 / compatible renewable energy ordinance (CREO) / renewable
#   energy ordinances, VA 2232 review (substantial accord) and siting agreements, special land
#   use / conditional or special use permits for energy facilities, wind energy (WECS, wind
#   turbine and wind farm ordinances, meteorological towers), transmission lines and
#   substations being sited, PILOT / tax-abatement deals for energy facilities.
# * zoning_amendment: zoning text amendments; rezonings to industrial (or for energy / data
#   centers); comprehensive / master plan amendments with a siting subject.
#
# Each entry: (topic, regex, guard). guard(text, match) -> True means "not a hit here".
# ----------------------------------------------------------------------------
_ENERGY_CTX = re.compile(
    r"\bsolar\b|photovoltaic|\bwind\s+(?:energy|turbine|farm|project|facilit|tower|ordinance|conversion|power)|"
    r"\bWECS\b|batter(?:y|ies)\s+(?:energy\s+)?storage|\bBESS\b|energy\s+storage|renewable|"
    r"energy\s+facilit|substation|transmission\s+line|utility[\s-]+scale\s+(?:solar|energy|wind)", re.I)
_DC_CTX = re.compile(r"data\s+cent|high\s+resource\s+demand|\bHRDF\b|crypto", re.I)
_SITING_CTX = re.compile(
    r"rezon|special\s+(?:land\s+)?use|conditional\s+use|\bCUP\b|\bSUP\b|site\s+plan|2232|substantial\s+accord|"
    r"public\s+hearing|applica|proposed|permit|ordinance|siting|route|construct|easement|\bkV\b|kilovolt", re.I)
_INDUSTRIAL_TARGET = re.compile(
    r"\b(?:M|I|LI|HI|GI|IP|PI)-?[1-3]\b|industrial|manufacturing|technology|data\s+cent|solar|batter|"
    r"energy|utility|wind", re.I)
_WEATHER = re.compile(r"wind\s*(?:storm|chill|speed|gust|damage|advisor|warning|event|shear|break|row|screen)|"
                      r"high\s+winds?|straight[\s-]+line\s+winds?|tornado|hurricane|derecho", re.I)
# a line or substation that is being proposed / sited, not one used as a landmark
_LINE_SITING_CTX = re.compile(
    r"proposed|\bnew\b|construct|\broute|\bkV\b|kilovolt|rezon|special\s+(?:land\s+)?use|conditional\s+use|"
    r"\bCUP\b|\bSUP\b|applica|\b2232\b|substantial\s+accord|siting|public\s+hearing|certificate|"
    r"expansion|upgrade|rebuild", re.I)
_LOCATION_ONLY = re.compile(r"\b(?:near|adjacent\s+to|along|across|under|beneath|crosses|crossing|existing|"
                            r"parallel\s+to|south\s+of|north\s+of|east\s+of|west\s+of|abuts?|bordered\s+by)\b"
                            r"[^.;]{0,40}$", re.I)
_UTILITY_NAME_BEFORE = re.compile(r"(?:consumers|dte|dominion|appalachian\s+power|aep|rappahannock|"
                                  r"cooperative|co-?op|electric)\s*$", re.I)


def _near(rx: re.Pattern, before: int, after: int):
    """guard: no match of `rx` within [start-before, end+after] -> not a hit."""
    return lambda t, m: not rx.search(_around(t, m, before, after))


_RENEWABLE_ORD = (r"\brenewable\s+energy\s+(?:ordinances?|facilit(?:y|ies)|systems?|projects?|overlay|zoning|"
                  r"siting|districts?|amendments?)\b")
_WIND = [
    ("clean_energy_siting", r"\bwind\s+energy\s+(?:conversion\s+systems?|facilit(?:y|ies)|systems?|projects?|"
                            r"ordinances?|overlay|farms?|developments?)\b", None),
    ("clean_energy_siting", r"\bWECS\b", None),
    ("clean_energy_siting", r"\b(?:utility[\s-]+scale\s+)?wind\s+(?:turbines?|farms?|parks?|projects?|"
                            r"generators?|developments?|ordinances?)\b",
     lambda t, m: bool(_WEATHER.search(_around(t, m, 60, 60)))),
    ("clean_energy_siting", r"\b(?:meteorological|met)\s+(?:test\s+)?towers?\b", None),
]
_STATE_SHARED = _WIND + [
    # special land use (MI) / conditional or special use permit (VA) for an energy facility (a data-center
    # permit is the data_center topic's, not clean-energy siting)
    ("clean_energy_siting", r"\bspecial\s+land\s+uses?\b|\b(?:conditional|special)\s+use\s+permits?\b|"
                            r"\bspecial\s+exceptions?\b",
     lambda t, m: not _ENERGY_CTX.search(_around(t, m, 150, 200))
     or (bool(_DC_CTX.search(_around(t, m, 150, 200))) and not re.search(
         r"\bsolar\b|\bwind\b|\bBESS\b|batter|energy\s+storage|renewable", _around(t, m, 150, 200), re.I))),
    ("clean_energy_siting", r"\b(?:solar|wind|storage|renewable|battery)?\s*energy\s+facilit(?:y|ies)\b",
     lambda t, m: bool(_UTILITY_NAME_BEFORE.search(t[max(0, m.start() - 30):m.start()]))),
    # transmission lines and substations being sited (not every passing mention)
    # (not bare "electric lines": site-plan legends and distribution easements)
    ("clean_energy_siting", r"\b(?:\d{2,3}\s*-?\s*kV|kilovolt|high[\s-]+voltage)\s+"
                            r"(?:transmission\s+)?lines?\b|\btransmission\s+lines?\b|\bsubstations?\b",
     lambda t, m: bool(_LOCATION_ONLY.search(t[max(0, m.start() - 45):m.start()]))
     or not _LINE_SITING_CTX.search(_around(t, m, 80, 120))),
    # PILOT / payment in lieu of taxes / tax abatement for an energy facility
    ("clean_energy_siting", r"(?-i:\bPILOT\b)|\bpayments?\s+in\s+lieu\s+of\s+taxes?\b|\btax\s+abatements?\b",
     _near(_ENERGY_CTX, 200, 200)),
    # zoning text amendments
    ("zoning_amendment", r"\bzoning\s+text\s+amendments?\b|\btext\s+amendments?\s+to\s+the\s+zoning\b|"
                         r"\b(?:ZTA|ZOA)[\s#-]*\d", None),
    # rezoning to industrial / for an energy or data-center use
    ("zoning_amendment", r"\brezon(?:e|es|ed|ing|ings)\b",
     lambda t, m: not _INDUSTRIAL_TARGET.search(t[m.start():m.end() + 220])),
    # comprehensive / master plan amendment with a siting subject
    ("zoning_amendment", r"\b(?:comprehensive|master)\s+plan\s+amendments?\b|"
                         r"\bamend(?:ing|ment\s+to)?\s+(?:the\s+)?(?:\w+\s+)?(?:comprehensive|master)\s+plan\b",
     lambda t, m: not (_ENERGY_CTX.search(_around(t, m, 150, 250)) or
                       re.search(r"data\s+cent|industrial|technology", _around(t, m, 150, 250), re.I))),
]
STATE_TOPICS: dict[str, list[tuple]] = {
    "MI": _STATE_SHARED + [
        ("clean_energy_siting", r"\b(?:Public\s+Act|P\.?\s?A\.?)\s*233\b",
         _near(re.compile(r"energy|renewable|solar|wind|storage|siting|CREO|MPSC|public\s+service", re.I), 200, 200)),
        ("clean_energy_siting", r"\bcompatible\s+renewable\s+energy\s+ordinances?\b|\bCREO\b", None),
        ("clean_energy_siting", _RENEWABLE_ORD, None),
        ("clean_energy_siting", r"\bMPSC\b(?=.{0,80}\b(?:siting|certificate|233|CREO))", None),
        # Industrial Facilities Exemption (PA 198) for an energy or data-center project
        ("clean_energy_siting", r"\bindustrial\s+facilit(?:y|ies)\s+(?:tax\s+)?exemption\b|\bIFT\b|\bP\.?\s?A\.?\s*198\b",
         _near(_ENERGY_CTX, 200, 200)),
    ],
    "VA": _STATE_SHARED + [
        # Code of Virginia 15.2-2232 review ("substantial accord") of an energy facility
        ("clean_energy_siting", r"(?:§+\s*|section\s+|sec\.\s*|15\.2-)2232\b|\b2232\s+(?:review|determination|"
                                r"application|public\s+facilit)|\bsubstantial\s+accord\b", _near(_ENERGY_CTX, 250, 250)),
        ("clean_energy_siting", r"\bsiting\s+agreements?\b", None),
        ("clean_energy_siting", r"\brevenue\s+share\b", _near(_ENERGY_CTX, 200, 200)),
        ("clean_energy_siting", _RENEWABLE_ORD, None),
    ],
}
_STATE_COMPILED = {st: [(topic, re.compile(rx, re.I), guard) for topic, rx, guard in entries]
                   for st, entries in STATE_TOPICS.items()}

# False-positive rules for the shared topics, applied only in the states above (MI, VA), from the
# hand check of the 2026-10 test (research_notes/Expansion/test_mi_va.md): use tables and permit
# statistics, non-zoning ordinance amendments (tax, traffic, stormwater fees), non-land-use moratoria
# (cemetery plots), data centers in event flyers / webinars / calendars / invoices, cell-tower leases in
# audit notes, "no equipment such as solar panels" glare boilerplate, tables of contents, height-exemption
# lists, solar on public roofs / backup power, wind terms inside data-center ordinances, invoices and
# ledgers, public-hearing-rules boilerplate, fiber broadband "telecommunications facilities", and
# Massachusetts-only 40B.
_LANDUSE_CTX = re.compile(r"zoning|\bzone[sd]?\b|rezon|land\s+use|subdivision|district|site\s+plan|setback|"
                          r"special\s+(?:land\s+)?use|conditional\s+use|planning\s+commission|comprehensive\s+plan|"
                          r"master\s+plan|\bZTA\b|\bZOA\b|overlay", re.I)
_NOT_LANDUSE_MORATORIUM = re.compile(r"cemeter|burial|grave|columbari|hunting|firework|burn(?:ing)?\s+ban|"
                                     r"shut-?offs?|disconnect|evict|\brent\b|hiring|tax\s+(?:sale|foreclos)", re.I)
_EVENT_OR_BILLING = re.compile(r"webinar|register\s+(?:today|now|here)|training\s+session|\bRSVP\b|eblast|"
                               r"newsletter|conference|invoice|/hr\b|\bPTO\b|holiday|trunk\s+or\s+treat", re.I)
_LEASE_ACCOUNTING = re.compile(r"lessor|lease\s+receivable|deferred\s+inflow|financial\s+statements|\bGASB\b", re.I)


# lists of things exempt from height limits ("solar panels, wind generators, television antenna...")
_HEIGHT_EXEMPT_LIST = re.compile(r"height\s+exemptions?|exempt(?:ed|ion)?\s+from\s+(?:the\s+)?(?:maximum\s+)?height|"
                                 r"antenna|chimney|flag\s*poles?|cupola|spire|steeple|air\s+condition", re.I)
# solar on public roofs / emergency backup power (energy savings, grants), not siting
_SOLAR_NOT_SITING = re.compile(r"roof(?:top)?s?\b|backup\s+power|transfer\s+switch|emergency\s+shelters?", re.I)
_SOLAR_SITING_WORDS = re.compile(r"ordinance|permit|zoning|special\s+(?:land\s+)?use|site\s+plan|facilit|farm|"
                                 r"\bMW\b|megawatt|acre|project|array", re.I)


def _tabular(t: str, m: re.Match) -> bool:
    """A zoning use table (P/S/A cells), a permit-statistics table, a numbered use list or a table of
    contents (dot leaders)."""
    w = _around(t, m, 120, 120)
    numbered = [int(n) for n in re.findall(r"(?<![\w.,/-])(\d{1,3})\.\s+[A-Z]", _around(t, m, 150, 150))]
    return (len(re.findall(r"(?<![\w.-])[PSCXA](?![\w.-])", _around(t, m, 200, 200))) >= 8
            or len(re.findall(r"(?<![\w.,/-])\d{1,4}(?![\w.,/-])", w)) >= 12
            or len(re.findall(r"\b\d+-\d+-\d+\.", w)) >= 3
            # a long numbered list of short entries (a use list), not an agenda's first items
            or (len(numbered) >= 6 and max(numbered) >= 15)
            or bool(re.search(r"\.{6,}|(?:\.\s){5,}|…{3,}", _around(t, m, 20, 100))))


_HEARING_RULES = re.compile(r"within\s+(?:its|their|the\s+\w+'s)\s+purview|public\s+hearing\s+rules|"
                            r"comments?\s+made\s+by\s+speakers", re.I)
_BROADBAND = re.compile(r"fib(?:er|re)|broadband|\bFTTH\b|\bVATI\b", re.I)
_TOWER_WORDS = re.compile(r"towers?|monopoles?|antenna|\bcell(?:ular)?\b|small\s+cell", re.I)


def _billing(t: str, m: re.Match) -> bool:
    """An invoice or ledger: many dollar amounts, or hourly rates, around the match."""
    w = _around(t, m, 250, 250)
    return (len(re.findall(r"\$\s?\d[\d,]*(?:\.\d\d)?", w)) >= 6
            or len(re.findall(r"\d\s*/\s*hr\b|\bper\s+hour\b", w, re.I)) >= 2)


# solar-powered equipment (speed signs, lights) and solar tubes (skylights)
_SOLAR_EQUIPMENT = re.compile(r"speed\s+(?:signs?|feedback|display|awareness|limit)|\bDSFS\b|radar\s+(?:signs?|speed)|"
                              r"skylights?", re.I)


# Building-permit and inspection logs ("SOLAR FINAL", "INSTALLING SOLAR PANELS ... NEW SFD"), assessor
# record cards and check registers: records of a house's rooftop panels or a vendor payment, not siting.
_INSPECTION_WORDS = re.compile(r"\b(?:FINAL|ROUGH[\s-]?IN|FOOTING|FRAMING|INSULATION|PERM\s+SERVICE|TEMP\s+SERVICE|"
                               r"NEW\s+SFD|LOT\s+CLEARING)\b")
_ASSESSOR_WORDS = re.compile(r"not\s+available|extra\s+(?:toilet|sink)|double\s+hung|horiz\.?\s+slide|"
                             r"(?:vinyl|metal)\s+sash|treated\s+wood|below\s+grade", re.I)
_REGISTER_WORDS = re.compile(r"REFUND\s+PERMIT\s+FEE|DEPT\s+PURCHASES|VEHICLE\s+MAINTENANCE|CONTRACTUAL\s+SERVICES|"
                             r"BLDG\s+MAINTENANCE|OPTICAL\s+EXPENSE")


def _record_log(t: str, m: re.Match) -> bool:
    w = _around(t, m, 200, 200)
    return (len(_INSPECTION_WORDS.findall(w)) >= 3 or len(_ASSESSOR_WORDS.findall(w)) >= 3
            or len(_REGISTER_WORDS.findall(_around(t, m, 300, 300))) >= 2)


STATE_FALSE_POSITIVE: list[tuple] = [   # (topic or None for every topic, test(text, match) -> True = drop)
    (None, _tabular),
    (None, _billing),
    (None, _record_log),
    # a general (non-zoning) ordinance amendment: land-use words must be in the item itself, not in the
    # previous item ("...the rezoning request was approved. 2. YARD WASTE ORDINANCE AMENDMENT")
    ("zoning_amendment", lambda t, m: bool(re.fullmatch(r"(?:by-?law|ordinance)\s+amendments?", m.group(0), re.I))
     and not _LANDUSE_CTX.search(_around(t, m, 60, 200))),
    ("zoning_amendment", lambda t, m: bool(_HEARING_RULES.search(_around(t, m, 250, 250)))),
    ("wireless_telecom", lambda t, m: bool(_BROADBAND.search(_around(t, m, 150, 150)))
     and not _TOWER_WORDS.search(_around(t, m, 150, 150))),
    ("moratorium", lambda t, m: bool(_NOT_LANDUSE_MORATORIUM.search(_around(t, m, 150, 200)))),
    ("data_center", lambda t, m: bool(_EVENT_OR_BILLING.search(_around(t, m, 150, 150)))),
    ("wireless_telecom", lambda t, m: bool(_LEASE_ACCOUNTING.search(_around(t, m, 150, 150)))),
    ("solar", lambda t, m: bool(re.search(r"\bno\s+(?:\w+\s+){0,3}such\s+as\s*$", t[max(0, m.start() - 40):m.start()],
                                          re.I))),
    ("solar", lambda t, m: bool(_SOLAR_NOT_SITING.search(_around(t, m, 100, 100)))
     and not _SOLAR_SITING_WORDS.search(_around(t, m, 100, 100))),
    ("solar", lambda t, m: bool(_HEIGHT_EXEMPT_LIST.search(_around(t, m, 100, 100)))),
    ("solar", lambda t, m: bool(re.match(r"[\s-]+(?:powered|tubes?|lights?|lighting|chargers?|water\s+heat)",
                                         t[m.end():m.end() + 20], re.I))
     or bool(_SOLAR_EQUIPMENT.search(_around(t, m, 200, 200)))),
    ("clean_energy_siting", lambda t, m: bool(_HEIGHT_EXEMPT_LIST.search(_around(t, m, 100, 100)))),
    # a wind term copied into a data-center ordinance (Tyrone's draft reuses the WECS "Facility Boundary")
    ("clean_energy_siting", lambda t, m: bool(re.match(r"(?:utility[\s-]+scale\s+)?wind|WECS|met", m.group(0), re.I))
     and bool(_DC_CTX.search(_around(t, m, 300, 300)))),
    # a legal digest of a wind case elsewhere ("objectors ... lacked standing")
    ("clean_energy_siting", lambda t, m: bool(re.match(r"(?:utility[\s-]+scale\s+)?wind|WECS|met", m.group(0), re.I))
     and bool(re.search(r"court\s+of\s+appeals|supreme\s+court|lacked\s+standing|appellants?|objectors",
                        _around(t, m, 300, 300), re.I))),
    ("40b_comprehensive_permit", lambda t, m: True),   # Massachusetts Chapter 40B: never a MI / VA topic
]


def _state_false_positive(text: str, m: re.Match, topic: str, state: str | None) -> bool:
    if (state or "").upper() not in STATE_TOPICS:
        return False
    return any((tp is None or tp == topic) and test(text, m) for tp, test in STATE_FALSE_POSITIVE)

SNIPPET_MAX = 240
CONTINUATION_GAP = 150  # chars after a snippet in which a same-topic match may be the same item
# Agenda item numbering ("161-26.", "7.", "b)", "IV.") marks the start of a new item.
_ITEM_BOUNDARY = re.compile(r"\b\d{1,4}-\d{2}\.\s|(?:^|\s)(?:\d{1,2}|[A-Za-z]|[IVX]{1,4})[.)]\s+[A-Z]")


# Typographic characters normalized before matching (by code point, so the
# table survives editors that mangle non-ASCII literals).
_PUNCT = str.maketrans({
    0x00AD: None,                                        # soft hyphen
    0xFFFD: " ",                                         # replacement char
    0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"',  # curly quotes
    0x2022: "-", 0x25CF: "-", 0x25AA: "-", 0x2212: "-",  # bullets, minus sign
    0xF0B7: "-", 0xF0A7: "-",                            # Wingdings bullets from Word
})


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(_PUNCT)).strip()


def _is_false_positive(text: str, m: re.Match) -> bool:
    return any(kw.fullmatch(m.group(0)) and test(text, m) for kw, test in _FALSE_POSITIVE)


def _state_matches(text: str, state: str | None):
    """(start, end, topic) for the state-specific patterns that survive their guards."""
    for topic, rx, guard in _STATE_COMPILED.get((state or "").upper(), ()):
        for m in rx.finditer(text):
            if (guard is None or not guard(text, m)) and not _state_false_positive(text, m, topic, state):
                yield m.start(), m.end(), topic


def topics_in(text: str, state: str | None = None) -> list[str]:
    found = []
    for topic, rxs in _COMPILED.items():
        if any(not _is_false_positive(text, m) and not _state_false_positive(text, m, topic, state)
               for rx in rxs for m in rx.finditer(text)):
            found.append(topic)
    if state:
        extra = {t for _, _, t in _state_matches(text, state)} | set(found)
        found = [t for t in TOPICS if t in extra]
    return found


def _snippet_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    """Choose a <= SNIPPET_MAX window around [start, end), preferring to begin
    at a sentence/agenda-item boundary shortly before the match."""
    lead = 90
    s = max(0, start - lead)
    # Snap forward to a natural boundary inside the lead-in if there is one.
    window = text[s:start]
    b = max(window.rfind(". "), window.rfind("; "), window.rfind(" - "), window.rfind(": "))
    if b != -1 and start - (s + b) > 15:
        s = s + b + 2
    elif s > 0:
        sp = text.find(" ", s)
        s = sp + 1 if 0 <= sp < start else s
    e = min(len(text), s + SNIPPET_MAX)
    if e < len(text):
        sp = text.rfind(" ", s, e)
        if sp > end:
            e = sp
    return s, max(e, min(len(text), end))


@dataclass
class Hit:
    topics: list[str]
    snippet: str
    offset: int
    context: str  # normalized text around the first keyword, used for dedupe


def find_hits(raw_text: str, max_per_doc: int = 8, state: str | None = None) -> list[Hit]:
    """Hits in one document. `state` adds that state's patterns (STATE_TOPICS); without
    it the result is exactly the shared matcher's."""
    text = clean_text(raw_text)
    matches: list[tuple[int, int, str]] = []
    for topic, rxs in _COMPILED.items():
        for rx in rxs:
            for m in rx.finditer(text):
                if not _is_false_positive(text, m) and not _state_false_positive(text, m, topic, state):
                    matches.append((m.start(), m.end(), topic))
    if state:
        matches.extend(_state_matches(text, state))
    matches.sort()
    hits: list[Hit] = []
    covered_until = -1
    last_match = 0
    per_topic: dict[str, int] = {}
    for start, end, topic in matches:
        if start < covered_until:
            continue  # already inside the previous snippet
        if (hits and topic in hits[-1].topics and start < covered_until + CONTINUATION_GAP
                and not _ITEM_BOUNDARY.search(text[last_match:start])):
            continue  # same item continuing ("...The moratorium will be in effect until...")
        if per_topic.get(topic, 0) >= 3:
            continue  # long packets: keep the first few mentions per topic
        s, e = _snippet_bounds(text, start, end)
        snippet = text[s:e].strip(" ,;:-")
        if len(snippet) > SNIPPET_MAX:
            snippet = snippet[:SNIPPET_MAX - 1].rstrip() + "…"
        if (state or "").upper() in STATE_TOPICS:
            # the matches that survived their guards in the full text (a guard needs more context
            # than the snippet holds: a use table's cells, an event flyer's wording)
            inside = {t for ms, me, t in matches if ms < e and me > s}
            topics = [t for t in TOPICS if t in inside] or [topic]
        else:
            topics = topics_in(snippet, state) or [topic]
        for t in topics:
            per_topic[t] = per_topic.get(t, 0) + 1
        # Forward-only context, so the same item reached via different lead-in
        # text (item number, section heading) still dedupes.
        context = re.sub(r"[^a-z0-9]+", " ", text[start:end + 80].lower()).strip()
        hits.append(Hit(topics, snippet, s, context))
        covered_until, last_match = e, start
        if len(hits) >= max_per_doc:
            break
    return hits
