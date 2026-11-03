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
        # 40R smart-growth districts: the other state housing program towns vote on (Carver, fall 2026)
        r"\b40\s?R\b",
        r"\bsmart\s+growth\s+(?:overlay\s+)?(?:zoning\s+)?districts?\b",
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
        # Auburn's warrant calls them "Electronic Data Storage projects"; Milford's bylaw, "Electronic Data Storage Centers"
        r"\b(?:electronic\s+)?data\s+storage\s+(?:facilit(?:y|ies)|cent(?:er|re)s?|projects?|buildings?|uses?)\b",
        r"\bhyperscale\b",
        r"\b(?:crypto(?:currency)?|bitcoin)\s+mining\b",
    ],
    "zoning_amendment": [
        r"\bzoning\s+(?:by-?law\s+|ordinance\s+|map\s+)?amendments?\b",
        # an overlay district being created, changed or repealed ("repeal the Brant Rock Village Overlay District")
        r"\b(?:repeal|rescind|amend|establish|creat|adopt|delet|eliminat|remov)\w*\b[^.;:]{0,60}?\boverlay\s+districts?\b",
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
    # "General Ordinance Amendment" about e-bikes, salaries, parks or composting is not a zoning change
    (re.compile(r"(?:by-?law|ordinance)\s+amendments?", re.I),
     lambda t, m: not re.search(r"zoning\s*$", t[max(0, m.start() - 12):m.start()], re.I)
     and not _ZONING_CTX.search(_around(t, m, 300, 300))),
]
_ZONING_CTX = re.compile(r"zoning|\bzones?\b|rezon|land\s+use|\bdistricts?\b|overlay|site\s+plan|special\s+permit|dimensional|"
                         r"setback|use\s+(?:table|regulations)|subdivision|lot\s+(?:size|coverage|area)|building\s+height|"
                         r"accessory\s+dwelling|\bADUs?\b|frontage|\b40[ABR]\b|\bto\s+allow\b|by[\s-]right|permitted\s+uses?|"
                         r"nonconforming|mixed[\s-]use|multi-?family|dwelling\s+units?|wetlands?|"
                         r"conservation\s+commission\s+by-?law", re.I)

# ----------------------------------------------------------------------------
# Hits that passed the matcher but are not what the site tracks. The engine drops them when it writes
# hits_current.json; build.py asks the same question of older hits.
# ----------------------------------------------------------------------------
# A moratorium on its own is a hit only when it is about land use or energy: a PFAS moratorium, a winter
# shut-off moratorium or a street-opening moratorium is a real item for the town, but not one this site tracks.
LAND_USE_WORDS = re.compile(r"solar|battery|data.?cent|server|development|building|construction|subdivision|zoning|housing|"
                            r"permit|dwelling|short.term|rental|cannabis|marijuana|warehouse|crypto", re.I)
POLE_WORDS = re.compile(r"\b(?:mid.?span\s+)?poles?\b|pole\s+(?:location|petition|hearing)|conduit", re.I)
UTILITY_WORDS = re.compile(r"national\s*grid|eversource|verizon|unitil|comcast|massachusetts\s+electric", re.I)
_PROJECT_WORDS = re.compile(r"solar\s+(?:farm|array|project|facility)|battery\s+(?:energy\s+)?storage\s+(?:system|facility|project)", re.I)
_ORDINANCE_ONLY = re.compile(r"(?:by-?law|ordinance)\s+amendments?", re.I)


def off_subject(h: dict) -> bool:
    """True for a hit the site should not show: a moratorium on something other than land use, a utility's
    pole petition that says "solar", or a general-ordinance amendment (salaries, parks, e-bikes) with no
    zoning words in its window."""
    snippet = " ".join((h.get("snippet") or "").split())
    topics = list(h.get("topics") or [])
    if topics == ["moratorium"] and not LAND_USE_WORDS.search(snippet):
        return True
    # A Planning Board's or Zoning Board's "bylaw amendment" is a zoning one; any other body's needs zoning words.
    if (topics == ["zoning_amendment"] and h.get("board_key") not in ("planning_board", "zoning_board_of_appeals")
            and _ORDINANCE_ONLY.search(snippet) and not _ZONING_CTX.search(snippet)):
        return True
    return bool(POLE_WORDS.search(snippet) and UTILITY_WORDS.search(snippet) and not _PROJECT_WORDS.search(snippet))

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
    r"expansion", re.I)
# maintenance of lines that already exist (a rebuild, a utility's service yard), not a siting
_ROUTINE_LINE_WORK = re.compile(r"rebuild|reconductor|maintenance|maintain|repair|replac(?:e|ement)|upgrade|"
                                r"relocat|outage|service\s+(?:yard|center)", re.I)
_STRONG_LINE_SITING = re.compile(r"proposed\s+(?:new\s+)?(?:\d+\s*kV\s+)?(?:transmission|line|substation)|"
                                 r"new\s+(?:\d+\s*kV\s+)?(?:transmission|substation|line)|\broute|routing|"
                                 r"certificate|\bCPCN\b|special\s+(?:land\s+)?use|\bSUP\b|\bCUP\b|rezon|"
                                 r"site\s+plan|siting|expansion|2232|substantial\s+accord", re.I)
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
    # gas-fired power plants being sited (no topic key of their own yet: clean_energy_siting until the
    # site supports a new topic). Needs siting words nearby; a utility's fleet description is not a siting.
    ("clean_energy_siting", r"\b(?:natural\s+)?gas[\s-]+(?:fired\s+)?(?:power|generat\w*|electric\w*)\s+"
                            r"(?:plants?|stations?|facilit(?:y|ies)|projects?)\b|\bcombined[\s-]+cycle\b|"
                            r"\bpeak(?:er|ing)\s+(?:power\s+)?plants?\b|\bpower\s+plant\s+ordinances?\b",
     lambda t, m: not _SITING_CTX.search(_around(t, m, 250, 250))
     or bool(re.search(r"portfolio|fleet|our\s+customers|headquartered", _around(t, m, 200, 200), re.I))),
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
    "OH": _STATE_SHARED + [
        # Ohio townships zone by resolution (ORC 519), so their amendments are "zoning resolution
        # amendments" / "amendments to the zoning resolution"; county and regional planning commissions
        # review every one of them under ORC 519.12 before the township zoning commission's hearing
        ("zoning_amendment", r"\bzoning\s+resolution\s+(?:text\s+|map\s+)?amendments?\b|"
                             r"\bamend(?:ing|ment|ments)?\s+(?:to\s+)?(?:the\s+)?(?:\w+\s+){0,3}zoning\s+resolutions?\b|"
                             r"\b(?:text|map)\s+amendments?\s+to\s+the\s+(?:\w+\s+){0,3}zoning\s+resolution\b|"
                             r"\b(?:ORC|R\.?C\.?|section)\s*519\.12\b", None),
        # SB 52 (2021): county commissioners may designate restricted areas for large solar and wind
        # facilities, and the Ohio Power Siting Board certifies them (not a county's "restricted parking")
        ("clean_energy_siting", r"\b(?:Senate\s+Bill|S\.?\s?B\.?)\s*52\b",
         _near(re.compile(r"solar|wind|energy|utility|siting|restricted|facilit", re.I), 200, 200)),
        ("clean_energy_siting", r"\brestricted\s+areas?\b",
         _near(re.compile(r"solar|wind\s+(?:farm|energy|turbine)|\bSB\s*52\b|utility[\s-]+scale|economically\s+"
                          r"significant|large\s+(?:solar|wind)|power\s+siting", re.I), 200, 200)),
        ("clean_energy_siting", r"\bOhio\s+Power\s+Siting\s+Board\b|\bOPSB\b",
         lambda t, m: not (_ENERGY_CTX.search(_around(t, m, 250, 250)) or _DC_CTX.search(_around(t, m, 250, 250)))),
        ("clean_energy_siting", _RENEWABLE_ORD, None),
        # payment in lieu of taxes for a qualified energy project (ORC 5727.75)
        ("clean_energy_siting", r"\bqualified\s+energy\s+projects?\b|\b5727\.75\b", None),
    ],
    "VA": _STATE_SHARED + [
        # Code of Virginia 15.2-2232 review ("substantial accord") of an energy facility
        ("clean_energy_siting", r"(?:§+\s*|section\s+|sec\.\s*|15\.2-)2232\b|\b2232\s+(?:review|determination|"
                                r"application|public\s+facilit)|\bsubstantial\s+accord\b", _near(_ENERGY_CTX, 250, 250)),
        ("clean_energy_siting", r"\bsiting\s+agreements?\b", None),
        ("clean_energy_siting", r"\brevenue\s+share\b", _near(_ENERGY_CTX, 200, 200)),
        ("clean_energy_siting", _RENEWABLE_ORD, None),
    ],
    # Maryland (VA/MD wave, 2026-11): the PSC's Certificate of Public Convenience and Necessity (PUA 7-207)
    # for a generating station or line, which counties comment on; the Renewable Energy Certainty Act (2025)
    # solar siting standards; Montgomery / Prince George's zoning map amendments (sectional, local,
    # countywide) when they rezone for industry, energy or data centers. Shared MI/VA guards apply.
    "MD": _STATE_SHARED + [
        ("clean_energy_siting", r"\bCPCN\b|certificate\s+of\s+public\s+convenience\s+and\s+necessity",
         _near(_ENERGY_CTX, 250, 250)),
        ("clean_energy_siting", r"\brenewable\s+energy\s+certainty\s+act\b|\bRECA\b|"
                                r"\b(?:PUA|public\s+utilit(?:y|ies)\s+article)\s*(?:§|section|sec\.)?\s*7-207\b",
         _near(_ENERGY_CTX, 250, 250)),
        ("clean_energy_siting", _RENEWABLE_ORD, None),
        ("zoning_amendment", r"\bsectional\s+map\s+amendments?\b|\b(?:local|countywide|zoning)\s+map\s+amendments?\b|"
                             r"\b(?:SMA|CMA|ZMA|LMA)[\s#-]*\d",
         lambda t, m: not (_INDUSTRIAL_TARGET.search(_around(t, m, 100, 250))
                           or _ENERGY_CTX.search(_around(t, m, 100, 250)))),
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
# ledgers, public-hearing-rules boilerplate, fiber broadband and right-of-way "telecommunications
# facilities", map legends, routine work on existing lines, and Massachusetts-only 40B.
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
_BROADBAND = re.compile(r"fib(?:er|re)|broadband|\bFTTH\b|\bVATI\b|right[\s-]+of[\s-]+ways?|\bROW\b|"
                        r"franchise|METRO\s+Act|conduit|cable\s+(?:television|operator)|lightpath", re.I)
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


# Round-6 false-positive classes from the Michigan hand check (research_notes/Expansion/test_mi_va.md):
# a fire chief's emergency-preparedness report on a solar facility under construction (operations, not
# land use); a list of reference checklists ("Adoption of a Zoning Ordinance Amendment"); a master plan
# five-year review whose scope cites "zoning amendments since adoption"; planning commission bylaws
# boilerplate on hearing notices. Each guard needs the class's own words and no siting words nearby.
_OPERATIONS_REPORT = re.compile(r"fire\s+chief|chief'?s\s+report|emergency\s+(?:preparedness|response\s+plan|"
                                r"management)|pre-?incident\s+plan|\bdrill\b|training\s+exercise|mutual\s+aid|"
                                r"first\s+responders?|\bEMS\b|fire\s+department\s+report", re.I)
_SITING_ACTION = re.compile(r"special\s+(?:land\s+)?use|conditional\s+use|site\s+plan|rezon|public\s+hearing|"
                            r"applica(?:nt|tion)|permit\s+(?:request|application)|variance|ordinance\s+amendment|"
                            r"text\s+amendment|proposed\s+(?:solar|wind|battery|project|facility)|\bcase\s*(?:no|#)",
                            re.I)
_REFERENCE_LIST = re.compile(r"checklists?|sample\s+(?:ordinance|resolution|form)|templates?|publications?|"
                             r"handbook|guidebook|fact\s+sheets?|\bMSU\s+Extension\b|Michigan\s+Townships\s+Association|"
                             r"\bMTA\b|\bOTA\b|resource\s+(?:list|library|center)|reference\s+(?:list|materials?)|"
                             r"available\s+(?:at|from|online)|\bwebsite\s+links?\b|"
                             # Great Lakes round 1: a fire department's permit fee table ("Energy Storage (Battery)
                             # System", "Solar Photovoltaic System" as permit types) and a zoning resolution's table
                             # of contents ("Overlay District removed 7/2025")
                             r"operational\s+permits?|construction\s+permits?|permit\s+fees?|fee\s+schedule|"
                             r"\btable\s+[A-H]\b|prevention\s+bureau|fire\s+marshal|table\s+of\s+contents", re.I)
_PLAN_REVIEW_SCOPE = re.compile(r"(?:five|5)[\s-]+year\s+(?:review|update)|master\s+plan\s+(?:review|update|"
                                r"progress)|comprehensive\s+plan\s+(?:review|update|progress)|since\s+(?:its\s+|the\s+)?"
                                r"adoption|review\s+of\s+the\s+(?:master|comprehensive)\s+plan|"
                                r"(?:MCL|section)\s*125\.3845", re.I)
_BYLAWS_BOILERPLATE = re.compile(r"by-?laws\s+(?:of|for)\s+the\s+(?:planning|zoning)|rules\s+of\s+procedure|"
                                 r"notice\s+(?:of\s+(?:the\s+|a\s+)?(?:public\s+)?hearing\s+)?shall\s+be\s+"
                                 r"(?:published|given|mailed|sent|posted)|not\s+less\s+than\s+(?:fifteen|15|ten|10)\s+days|"
                                 r"article\s+[IVX]+\s*[.:-]|quorum\s+shall", re.I)


def _beside(t: str, m: re.Match, before: int, after: int) -> str:
    """The text around a match without the match itself (so "zoning ordinance amendment" does not count
    as its own siting action)."""
    return t[max(0, m.start() - before):m.start()] + " | " + t[m.end():m.end() + after]


def _operations_report(t: str, m: re.Match) -> bool:
    w = _around(t, m, 250, 250)
    return len(_OPERATIONS_REPORT.findall(w)) >= 2 and not _SITING_ACTION.search(_beside(t, m, 250, 250))


def _reference_list(t: str, m: re.Match) -> bool:
    w = _around(t, m, 250, 250)
    return len(_REFERENCE_LIST.findall(w)) >= 2 and not _SITING_ACTION.search(_beside(t, m, 120, 120))


def _plan_review_scope(t: str, m: re.Match) -> bool:
    w = _around(t, m, 200, 200)
    return bool(_PLAN_REVIEW_SCOPE.search(w)) and not _SITING_ACTION.search(_beside(t, m, 120, 160))


# a bylaws page says "public hearing" and "ordinance amendment" as a matter of course, so only a concrete
# matter (an applicant, a case, a parcel, a named project) counts against the bylaws guard
_CONCRETE_MATTER = re.compile(r"special\s+(?:land\s+)?use|conditional\s+use|site\s+plan|rezon|applica(?:nt|tion)|"
                              r"\bcase\s*(?:no|#)|variance|parcel|\bMW\b|megawatt|acres?\b|\bLLC\b|petition", re.I)


def _bylaws_boilerplate(t: str, m: re.Match) -> bool:
    w = _around(t, m, 250, 250)
    cues = len(_BYLAWS_BOILERPLATE.findall(w))
    return (cues >= 2 or (cues >= 1 and bool(re.search(r"\barticle\s+[IVX\d]+\b|\bsection\s+\d+\.\d", w, re.I)))) \
        and bool(re.search(r"\bshall\b", w)) and not _CONCRETE_MATTER.search(_beside(t, m, 150, 150))


# Great Lakes round 1 (research_notes/Expansion/great_lakes_wave.md): Ohio county planning commissions attach a
# township's whole adopted zoning resolution to the packet (or a whole-resolution redline) when they review one
# text amendment under ORC 519.12. Accessory solar rules, wind turbine definitions, overlay purpose clauses and
# the zoning inspector's duties in that attachment are reference text, not the matter; the staff report is.
# A document is codified text when its head names a zoning resolution / ordinance with an adoption, approval,
# certification or effective-date marker and nothing that reads as an agenda, minutes, hearing notice, staff
# report, draft or new ordinance. Hits near "proposed", "draft" or redline words are kept.
_CODIFIED_NAME = re.compile(r"zoning\s+(?:resolution|ordinance|regulations|code)\b", re.I)
_CODIFIED_MARK = re.compile(r"\b(?:adopted|approved\s+by|certif(?:y|ication)|effective|revised|re-?codified|"
                            r"eff\.)\b|table\s+of\s+contents|\barticle\s+(?:I|1|II|2)\b\s*[-–:]?\s*(?:title|definitions|general)",
                            re.I)
_LIVE_MATTER_HEAD = re.compile(r"\bagenda\b|\bminutes\b|meeting\s+of|\bhearing\b|staff\s+report|memorandum|"
                               r"\bdraft\b|proposed\s+(?:amendments?|text|language|changes?)|redline|strike|underlin|"
                               r"ordinance\s+(?:no\.?|#)\s*\d|an\s+ordinance\s+to\s+amend|be\s+it\s+(?:ordained|resolved)|"
                               r"\bnotice\b|\bapplicant\b|\bcase\s*(?:no|#)", re.I)
# ordinance text says "the proposed structure" on every page, so only amendment words count as a live matter
# ("proposed amendments" is itself boilerplate: "to review all proposed amendments to this Zoning Resolution")
_PROPOSED_NEAR = re.compile(r"proposed\s+(?:text|language|changes?|revisions?)|"
                            r"\bdraft\b|redline|underlin|strike|new\s+(?:text|language|section)|"
                            r"\b(?:added|deleted)\s+(?:text|language|section)", re.I)


def _codified_doc(t: str) -> bool:
    head = t[:2500]
    return bool(_CODIFIED_NAME.search(head)) and bool(_CODIFIED_MARK.search(head)) \
        and not _LIVE_MATTER_HEAD.search(head)


def _reference_code(t: str, m: re.Match) -> bool:
    return _codified_doc(t) and not _PROPOSED_NEAR.search(_around(t, m, 300, 300))


# a variance "to amend the Zoning Resolution, Article 5" (a fence) is a variance, not an amendment
_VARIANCE = re.compile(r"\bvariances?\b", re.I)
_AMENDMENT_PROPER = re.compile(r"rezon|text\s+amendment|map\s+amendment|zoning\s+amendment\s+application|"
                               r"amendment\s+(?:no|#|application)|\bZTA\b|\bZOA\b|\bTA\b", re.I)


# Great Lakes round 2: a fire code fee schedule's footnotes ("systems over 20 KWH for non-liquid battery
# systems", "2025 OFC Table 5003.1.1") and a zoning report's permit tally ("seven swimming pools, four solar")
_FIRE_CODE = re.compile(r"\bOFC\b|fire\s+code|1301:7-7|administrative\s+code|operational\s+permits?|fee\s+schedule", re.I)
_TALLY_WORDS = re.compile(r"zoning\s+report|permits?\s+issued|total\s+this\s+year|year\s+to\s+date|\bYTD\b", re.I)
_COUNT_WORD = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d{1,3})"


def _fire_code_footnote(t: str, m: re.Match) -> bool:
    return len(_FIRE_CODE.findall(_around(t, m, 400, 400))) >= 2 and not _SITING_ACTION.search(_beside(t, m, 150, 150))


def _permit_tally(t: str, m: re.Match) -> bool:
    before = t[max(0, m.start() - 14):m.start()]
    return bool(re.search(_COUNT_WORD + r"\s*$", before, re.I)) and bool(_TALLY_WORDS.search(_around(t, m, 250, 100))) \
        and len(re.findall(_COUNT_WORD + r"\s+[a-z]+", _around(t, m, 200, 100), re.I)) >= 4


def _variance_only(t: str, m: re.Match) -> bool:
    w = _around(t, m, 150, 150)
    return bool(_VARIANCE.search(w)) and not _AMENDMENT_PROPER.search(_beside(t, m, 150, 150))


# a permit fee table runs for pages ("Table C - Operational Permits ... Energy Storage (Battery) System ...
# Solar Photovoltaic System ..."), so its cues sit farther from the term than a reference list's
def _reference_table(t: str, m: re.Match) -> bool:
    w = _around(t, m, 600, 600)
    return len(_REFERENCE_LIST.findall(w)) >= 3 and not _SITING_ACTION.search(_beside(t, m, 150, 150)) \
        and _distinct_actions(_around(t, m, 300, 300)) <= 2   # an agenda sheet ("adopt ... draft ... motion") is not a table


# a run of Title Case entries with no sentences around the term (a permit type list, an index, a legend):
# 50+ words, at most two sentence marks, seven in ten words capitalized, no action or siting words
_WORD = re.compile(r"[A-Za-z][A-Za-z'&/-]*")


def _distinct_actions(w: str) -> int:
    return len({x.lower()[:6] for x in _ACTION_WORDS.findall(w)})


def _caption_list(t: str, m: re.Match) -> bool:
    w = _around(t, m, 300, 300)
    words = _WORD.findall(w)
    if len(words) < 50 or len(re.findall(r"[.;:?!]", w)) > 3 or _ITEM_BOUNDARY.search(w) or _SITING_ACTION.search(w):
        return False   # sentences or agenda numbering around the term: not a bare list
    caps = sum(1 for x in words if x[0].isupper() or x.lower() in ("of", "and", "or", "the", "for", "a", "an", "&"))
    ratio, actions = caps / len(words), _distinct_actions(w)
    return (ratio >= 0.7 and actions == 0) or (ratio >= 0.9 and actions <= 1)


# VA/MD wave hand check (research_notes/Expansion/va_md_wave.md): "PV" as a pavement elevation on an engineering
# drawing ("EP 9.49 PV 8.71 FFE 10.00"), a finance policy's definition of proffers ("at the time of a rezoning"), a
# utility-rate or shut-off resolution that names data centers, and a homeowner's solar carport or panel-roof variance.
_DRAWING_WORDS = re.compile(r"\bFFE\b|\bEP\b|\bTC\b|\bBC\b|\bINV\b|\bRIM\b|contour|swale|\bSWM\b|easement", re.I)
_FINANCE_POLICY = re.compile(r"capital\s+assets?|depreciat|useful\s+life|\bGASB\b|capitalization\s+threshold|"
                             r"financial\s+reporting", re.I)
_UTILITY_RATES = re.compile(r"shut-?offs?|disconnect|utility\s+(?:rates?|bills?|increases?)|ratepayers?|"
                            r"rais(?:e|ing)\s+(?:\w+\s+){0,2}rates\b|electric(?:ity)?\s+(?:compan(?:y|ies)|rates?|bills?)|"
                            r"public\s+service\s+commission\b", re.I)
_RESIDENTIAL_SOLAR = re.compile(r"carport|panel[\s-]+roof|driveway|dwelling|single[\s-]+family|homeowner|"
                                r"accessory\s+structure|side[\s-]+yard|setback\s+applicable\s+to\s+a\s+corner\s+lot", re.I)
_UTILITY_SCALE = re.compile(r"\bMW\b|megawatt|acres?|utility[\s-]+scale|solar\s+(?:farm|facility|facilities|project|"
                            r"energy\s+system|ordinance)|ground[\s-]+mounted|special\s+exception|conditional\s+use|"
                            r"\bCUP\b|\bSUP\b|zoning\s+text", re.I)


def _pavement_pv(t: str, m: re.Match) -> bool:
    if m.group(0).upper() != "PV":
        return False
    w = _around(t, m, 120, 120)
    return len(re.findall(r"\b\d{1,3}\.\d\d?\b", w)) >= 4 and bool(_DRAWING_WORDS.search(w))


STATE_FALSE_POSITIVE: list[tuple] = [   # (topic or None for every topic, test(text, match) -> True = drop)
    (None, _tabular),
    ("solar", _pavement_pv),
    ("zoning_amendment", lambda t, m: bool(re.search(r"rezon", m.group(0), re.I))
     and bool(_FINANCE_POLICY.search(_around(t, m, 300, 300)))),
    ("data_center", lambda t, m: bool(_UTILITY_RATES.search(_around(t, m, 250, 250)))
     and not re.search(r"zoning|rezon|site\s+plan|special\s+(?:use|exception)|conditional\s+use|overlay|"
                       r"moratorium\s+on\s+(?:new\s+)?data|by[\s-]+right|text\s+amendment",
                       _around(t, m, 250, 250), re.I)),
    ("solar", lambda t, m: bool(_RESIDENTIAL_SOLAR.search(_around(t, m, 200, 200)))
     and len(_RESIDENTIAL_SOLAR.findall(_around(t, m, 300, 300))) >= 2
     and not _UTILITY_SCALE.search(_around(t, m, 300, 300))),
    # round-6 classes (above): operations reports, reference lists, plan-review scope, bylaws boilerplate
    ("solar", _operations_report),
    ("battery_storage", _operations_report),
    ("clean_energy_siting", _operations_report),
    ("zoning_amendment", _reference_list),
    ("zoning_amendment", _plan_review_scope),
    ("zoning_amendment", _bylaws_boilerplate),
    ("moratorium", _reference_list),
    # Great Lakes round 1 (above): permit fee tables (the energy topics take the wider table guard, not the
    # reference-list guard: "An MTA sample ordinance is attached" is a live agenda item), attached adopted zoning
    # resolutions, a variance worded as an amendment
    ("solar", _reference_table),
    ("battery_storage", _reference_table),
    ("clean_energy_siting", _reference_table),
    ("data_center", _reference_table),
    ("solar", _fire_code_footnote),
    ("battery_storage", _fire_code_footnote),
    ("solar", _permit_tally),
    ("battery_storage", _permit_tally),
    ("solar", _caption_list),
    ("battery_storage", _caption_list),
    ("clean_energy_siting", _caption_list),
    ("data_center", _caption_list),
    (None, _reference_code),
    ("zoning_amendment", _variance_only),
    (None, _billing),
    (None, _record_log),
    # a general (non-zoning) ordinance amendment: land-use words must be in the item itself, not in the
    # previous item ("...the rezoning request was approved. 2. YARD WASTE ORDINANCE AMENDMENT")
    ("zoning_amendment", lambda t, m: bool(re.fullmatch(r"(?:by-?law|ordinance)\s+amendments?", m.group(0), re.I))
     and not _LANDUSE_CTX.search(_around(t, m, 60, 200))),
    ("zoning_amendment", lambda t, m: bool(_HEARING_RULES.search(_around(t, m, 250, 250)))),
    ("wireless_telecom", lambda t, m: bool(_BROADBAND.search(_around(t, m, 250, 250)))
     and not _TOWER_WORDS.search(_around(t, m, 150, 150))),
    # 3. a map legend (existing lines and substations drawn on a utility's map)
    ("clean_energy_siting", lambda t, m: bool(re.search(r"transmission|substation|kV|kilovolt|voltage", m.group(0), re.I))
     and bool(re.search(r"\blegend\b", _around(t, m, 300, 300), re.I))),
    # 4. routine work on an existing line or a utility's service yard
    ("clean_energy_siting", lambda t, m: bool(re.search(r"transmission|substation|kV|kilovolt|voltage", m.group(0), re.I))
     and bool(_ROUTINE_LINE_WORK.search(_around(t, m, 150, 150)))
     and not _STRONG_LINE_SITING.search(_around(t, m, 150, 150))
     and not re.search(r"\bshall\b", _around(t, m, 150, 150), re.I)),   # not ordinance text
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


def _state_false_positive(text: str, m: re.Match, topic: str, state: str | None, codified: bool = False) -> bool:
    """`codified`: the whole document is adopted zoning text (_codified_doc on the full text); the page-level
    guards only see one page, so find_hits works it out once per document and passes it down."""
    if (state or "").upper() not in STATE_TOPICS:
        return False
    if codified and not _PROPOSED_NEAR.search(_around(text, m, 300, 300)):
        return True
    return any((tp is None or tp == topic) and test(text, m) for tp, test in STATE_FALSE_POSITIVE)


# ----------------------------------------------------------------------------
# Sections (MI / VA): an agenda packet is an agenda, then minutes of earlier meetings, then
# attachments (staff reports, draft ordinances, applications) and, often, things that are not
# about any item at all (newsletters, invoices, permit logs, assessor cards, audits, case-law
# digests, consultants' resumes). Each page (pdftotext and tesseract separate pages with a form
# feed) is classified on its own text:
#   agenda   - agenda markers (call to order, public hearing, new business, adjourn...), or a
#              page right after an agenda page that still carries one marker
#   minutes  - a record of a meeting (motion, seconded, carried, roll call vote, "stated that",
#              "discussed"), or a page after a minutes page that still carries one marker
#   noise    - one of the genres above, a ledger (8+ dollar amounts) or a use table (40+ P/S/A
#              cells): every match on the page is dropped (checked after agenda, before minutes)
#   ordinance - regulatory text (sections, definitions, "shall", whereas / be it resolved): as agenda
#   attachment - anything else: a match must carry stronger evidence nearby (action / regulatory
#              words or a project name) and must not be one entry in a list of unrelated topics
# Agenda and minutes pages are matched as before. Single-page HTML / DOCX documents are classified
# the same way.
# ----------------------------------------------------------------------------
_AGENDA_MARKERS = re.compile(
    r"call\s+to\s+order|roll\s+call|pledge\s+of\s+allegiance|(?:approval|adoption)\s+of\s+(?:the\s+)?agenda|"
    r"public\s+comments?|call\s+to\s+the\s+public|citizens?'?\s+comments?|old\s+business|unfinished\s+business|"
    r"new\s+business|adjourn|consent\s+(?:agenda|items)|public\s+hearings?|invocation|announcements|"
    r"board\s+(?:member\s+)?comments|closed\s+session|items?\s+for\s+(?:discussion|action)|"
    r"(?:approval|adoption)\s+of\s+(?:the\s+)?minutes", re.I)
_MINUTES_MARKERS = re.compile(
    r"\bminutes\b|motion\s+(?:by|made|carried|passed|failed|to\s+\w+)|seconded|supported\s+by|roll\s+call\s+vote|"
    r"\bayes?\b|\bnays?\b|\bpresent:|\babsent:|voice\s+vote|motion\s+carried|vote\s+\d-\d|\(\d-\d\)|"
    r"unanimous(?:ly)?|stated\s+that|\basked\s+(?:whether|about|if|that)|\bdiscussed\b|explained\s+that|"
    r"\bcommented\b|\breported\s+(?:that|on)", re.I)
_NOISE_GENRES = {
    "newsletter": (re.compile(r"newsletter|webinar|register\s+(?:now|today|here|online|at)|\be-?news\b|"
                              r"township\s+(?:focus|insights)|michigan\s+townships\s+association|subscribe|"
                              r"save\s+the\s+date|upcoming\s+(?:events|workshops)|virginia\s+association\s+of\s+"
                              r"counties|\bVACo\b|member\s+(?:benefits|services)|\bMTA\b|e-?blast|"
                              r"members?[\s-]+only|\bFAQs?\b|frequently\s+asked", re.I), 3),
    "invoice": (re.compile(r"invoice|amount\s+due|balance\s+due|remit|statement\s+of\s+account|billing|"
                           r"\bexpenses\b|\d{1,2}/\d{1,2}\s*-\s*\d{1,2}/\d{1,2}|"
                           r"\bhours?\b\s+@|@\s*\$?\d+(?:\.\d\d)?\s*/\s*hr|\brate\b|professional\s+services\s+rendered|"
                           r"check\s+(?:register|number|no\.?)|\bvendor\b|accounts\s+payable|\bwarrants?\b\s+list",
                           re.I), 3),
    "permit_log": (re.compile(r"\b(?:FINAL|ROUGH[\s-]?IN|FOOTING|FRAMING|INSULATION|PERM\s+SERVICE|TEMP\s+SERVICE|"
                              r"NEW\s+SFD|LOT\s+CLEARING)\b|permits?\s+issued|inspections?\s+(?:performed|completed)|"
                              r"est(?:imated)?\.?\s+value", re.I), 6),
    "assessor": (re.compile(r"not\s+available|extra\s+(?:toilet|sink)|double\s+hung|horiz\.?\s+slide|"
                            r"(?:vinyl|metal)\s+sash|treated\s+wood|below\s+grade|assessed\s+value|taxable\s+value|"
                            r"\bSEV\b|property\s+class|school\s+district:|year\s+built", re.I), 4),
    "audit": (re.compile(r"\bGASB\b|statement\s+of\s+net\s+position|fund\s+balance|independent\s+auditor|"
                         r"management'?s\s+discussion|deferred\s+(?:inflows?|outflows?)|net\s+pension|"
                         r"notes\s+to\s+(?:the\s+)?financial\s+statements", re.I), 3),
    "case_digest": (re.compile(r"court\s+of\s+appeals|supreme\s+court|circuit\s+court|plaintiffs?|defendants?|"
                               r"appellants?|appellees?|lacked\s+standing|\bv\.\s+[A-Z]", re.I), 4),
    "resume": (re.compile(r"years\s+of\s+experience|education\b|certifications?|project\s+role|qualifications|"
                          r"\bresumes?\b|relevant\s+experience|professional\s+(?:affiliations|registrations?)", re.I), 3),
    "job_description": (re.compile(r"job\s+description|essential\s+(?:duties|functions)|minimum\s+qualifications|"
                                   r"reports\s+to\b|\bsalary|\bFLSA\b|knowledge,?\s+skills|physical\s+(?:demands|"
                                   r"requirements)|position\s+(?:summary|title|purpose)|duties\s+and\s+responsibilities|"
                                   r"work\s+environment|pay\s+(?:grade|range)|job\s+(?:title|summary)", re.I), 3),
    # a consultant's services proposal ("Our proposal includes ... Retainer ... we will provide")
    "services_proposal": (re.compile(r"\bretainer\b|scope\s+of\s+(?:services|work)|our\s+proposal|"
                                     r"we\s+(?:will|would)\s+provide|fee\s+schedule|not\s+to\s+exceed|"
                                     r"hourly\s+rates?|proposed\s+fees?|statement\s+of\s+qualifications", re.I), 3),
    "spec_sheet": (re.compile(r"spec(?:ification)?s?\s+sheet|data\s*sheet|\bUL\s+listed|lumens?|\bLED\b|\bvac\b|"
                              r"\bIP\s?6[5-8]\b|die-?cast|powder\s+coat|warranty|catalog\s+(?:no|number|#)|"
                              r"model\s+(?:no|number|#)|wattage|\bCCT\b|kelvin|junction\s+box", re.I), 4),
}
# regulatory text (draft or adopted ordinance, resolution, siting agreement): matched as before
_ORDINANCE_MARKERS = re.compile(
    r"\bsec(?:tion|\.)\s*\d|\barticle\s+(?:[IVX]+|\d+)\b|\bdefinitions?\b|intent\s+and\s+purpose|\bpurpose\b|"
    r"\bsubsection|\bwhereas\b|be\s+it\s+(?:further\s+)?(?:resolved|ordained)|\bordinance\s+no\.|"
    r"\bagreement\b|\bthe\s+parties\b|applicability", re.I)
_ACTION_WORDS = re.compile(
    r"public\s+hearing|\bhearing\b|application|applicant|petition|request(?:ed|s|ing)?\b|propos(?:ed|al|es)|"
    r"ordinance|amend|rezon|special\s+(?:land\s+)?use|special\s+exception|conditional\s+use|\b(?:SUP|CUP|SLU|SAP|PUD)\b|"
    r"site\s+plan|siting\s+agreement|resolution|moratori|whereas|be\s+it\s+(?:further\s+)?resolved|approv|adopt|"
    r"\bden(?:y|ied|ial)\b|recommend|\bmotion\b|\bvote\b|tabled?\b|postpone|draft|setbacks?|\bdistricts?\b|overlay|"
    r"zoning|\bshall\b|decommission|substantial\s+accord|2232|staff\s+report|planning\s+commission|"
    r"board\s+of\s+(?:supervisors|trustees|zoning\s+appeals)|township\s+board|notice\s+is\s+hereby|permit\b|"
    r"\bcase\b|consider(?:ation)?", re.I)
_PROJECT_NAME = re.compile(
    r"\b(?!Dominion\b|Consumers\b|DTE\b|Appalachian\b)[A-Z][\w&'-]+(?:\s+[A-Z][\w&'-]+){0,3}\s+"
    r"(?:Solar|Energy|Storage|Wind|Power|Renewables|Data\s+Centers?|Campus)\b|"
    r"\b(?:SLU|SUP|CUP|ZTA|ZOA|REZ|RZ|SE|PC|SP|SAP|Z)[-#\s]?\d{2,}")


def _page_spans(raw_text: str) -> tuple[str, list[tuple[int, int, str]]]:
    """Clean text (as clean_text, pages joined by a space) and [(start, end, class)] per page."""
    pages = [clean_text(p) for p in raw_text.split("\f")]
    pages = [p for p in pages if p]
    text, spans, pos, prev = [], [], 0, None
    for i, p in enumerate(pages):
        n_ag = len({m.group(0).lower()[:12] for m in _AGENDA_MARKERS.finditer(p)})
        n_min = len({m.group(0).lower()[:10] for m in _MINUTES_MARKERS.finditer(p)})
        has_agenda_word = bool(re.search(r"\bagenda\b", p, re.I))
        n_ord = len({m.group(0).lower()[:10] for m in _ORDINANCE_MARKERS.finditer(p)})
        n_shall = len(re.findall(r"\bshall\b", p, re.I))
        noise = None
        for genre, (rx, need) in _NOISE_GENRES.items():
            if len({m.group(0).lower()[:14] for m in rx.finditer(p)}) >= need:
                noise = genre
                break
        if noise is None and len(re.findall(r"\$\s?\d[\d,]*\.\d\d", p)) >= 8:
            noise = "ledger"
        if noise is None and len(re.findall(r"(?<![\w.-])[PSCXA](?![\w.-])", p)) >= 40:
            noise = "use_table"
        if (has_agenda_word and n_ag >= 2) or n_ag >= 4 or (prev == "agenda" and n_ag >= 1):
            cls = "agenda"
        elif noise:
            cls = "noise:" + noise
        elif n_min >= 3 or (prev == "minutes" and n_min + n_ag >= 1):
            cls = "minutes"
        elif n_ord >= 3 or n_shall >= 4:
            cls = "ordinance"
        else:
            cls = "attachment"
        spans.append((pos, pos + len(p), cls))
        text.append(p)
        pos += len(p) + 1
        prev = cls
    return " ".join(text), spans


def _page_class(spans: list[tuple[int, int, str]], offset: int) -> str:
    for s, e, cls in spans:
        if s <= offset <= e:
            return cls
    return "attachment"


def _passing_list(t: str, start: int, end: int) -> bool:
    """The term is one entry in a comma list of short unrelated entries (a report's topic list)."""
    w = t[max(0, start - 160): end + 160]
    parts = [x.strip() for x in w.split(",")]
    if len(parts) < 6:
        return False
    short = [x for x in parts[1:-1] if len(x) <= 40]
    return len(short) >= 4 and not _ACTION_WORDS.search(t[max(0, start - 60): end + 60])


_FORM_MARKERS = re.compile(r"circle\s*:|check\s+(?:one|all)|if\s+(?:yes|so)\b|please\s+(?:describe|explain|attach|"
                           r"provide|list|print)|yes\s*/\s*no|_{6,}|for\s+office\s+use|applicant'?s?\s+signature|"
                           r"signature\s+of\s+applicant", re.I)


def _form_question(t: str, start: int, end: int, page: str) -> bool:
    """The term sits in a question of a form ("Is this a proposal for a ... telecommunication tower?")
    on a page that reads like a blank form."""
    nxt = re.search(r"[.?!]", t[end:end + 200])
    if not nxt or nxt.group(0) != "?":
        return False
    markers = len({m.group(0).lower()[:10] for m in _FORM_MARKERS.finditer(page)})
    return markers + (1 if page.count("?") >= 4 else 0) >= 2   # a page of questions


def _section_reject(t: str, start: int, end: int, spans) -> bool:
    """True when a match should be dropped because of the section it sits in (MI / VA)."""
    if spans is None:
        return False
    cls = _page_class(spans, start)
    if cls.startswith("noise:"):
        return True
    ps, pe = next(((a, b) for a, b, _ in spans if a <= start <= b), (0, len(t)))
    if cls in ("attachment", "ordinance") and _form_question(t, start, end, t[ps:pe]):
        return True
    if cls != "attachment":
        return False
    if _passing_list(t, start, end):
        return True
    w = t[max(0, start - 200): end + 200]
    return not (_ACTION_WORDS.search(w) or _PROJECT_NAME.search(w))

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


def _state_matches(text: str, state: str | None, spans=None, full: tuple[str, int] | None = None,
                   codified: bool = False):
    """(start, end, topic) for the state-specific patterns that survive their guards (and, with
    `spans` from _page_spans, the section rules). `full` = (whole document text, offset of `text`
    in it): the section rules' evidence window may reach into the neighbouring page."""
    for topic, rx, guard in _STATE_COMPILED.get((state or "").upper(), ()):
        for m in rx.finditer(text):
            if (guard is None or not guard(text, m)) and not _state_false_positive(text, m, topic, state, codified):
                if full is not None:
                    rejected = _section_reject(full[0], full[1] + m.start(), full[1] + m.end(), spans)
                else:
                    rejected = _section_reject(text, m.start(), m.end(), spans)
                if not rejected:
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


def find_hits(raw_text: str, max_per_doc: int = 12, state: str | None = None) -> list[Hit]:
    """Hits in one document. `state` adds that state's patterns (STATE_TOPICS); without
    it the result is exactly the shared matcher's."""
    matches: list[tuple[int, int, str]] = []
    if (state or "").upper() in STATE_TOPICS:
        # MI / VA: each page is classified (agenda, minutes, ordinance, attachment, noise) and matched
        # on its own, so a guard's look-around never reaches into the next page
        text, spans = _page_spans(raw_text)
        codified = _codified_doc(text)   # an attached adopted zoning resolution: judged on the document, not the page
        for s, e, cls in spans:
            if cls.startswith("noise:"):
                continue
            page = text[s:e]
            # guards see the page only; the section evidence window (action words, project names)
            # may reach into the neighbouring page (a resolution's WHEREAS on the next page)
            for topic, rxs in _COMPILED.items():
                for rx in rxs:
                    for m in rx.finditer(page):
                        if (not _is_false_positive(page, m)
                                and not _state_false_positive(page, m, topic, state, codified)
                                and not _section_reject(text, s + m.start(), s + m.end(), spans)):
                            matches.append((s + m.start(), s + m.end(), topic))
            matches.extend((s + a, s + b, t) for a, b, t in _state_matches(page, state, spans, (text, s), codified))
    else:
        text = clean_text(raw_text)
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
        if per_topic.get(topic, 0) >= 5:
            continue  # long packets: keep the first few mentions per topic (a warrant can carry five zoning articles)
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
