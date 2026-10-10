"""Topic keyword groups and snippet extraction.

Each topic is a list of case-insensitive regexes. `find_hits(text)` returns
one entry per distinct passage: the snippet (<= 240 chars, whitespace
cleaned) plus every topic that matches inside that snippet.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

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
    # bond / contract boilerplate: "bankruptcy, insolvency, reorganization, moratorium"
    (re.compile(r"morator(?:ium|ia|iums)", re.I),
     lambda t, m: re.search(r"bankruptcy|insolvency|reorganization|creditors", _around(t, m, 60, 60), re.I)),
]

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


def topics_in(text: str) -> list[str]:
    found = []
    for topic, rxs in _COMPILED.items():
        if any(not _is_false_positive(text, m) for rx in rxs for m in rx.finditer(text)):
            found.append(topic)
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


def find_hits(raw_text: str, max_per_doc: int = 8) -> list[Hit]:
    text = clean_text(raw_text)
    matches: list[tuple[int, int, str]] = []
    for topic, rxs in _COMPILED.items():
        for rx in rxs:
            for m in rx.finditer(text):
                if not _is_false_positive(text, m):
                    matches.append((m.start(), m.end(), topic))
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
        topics = topics_in(snippet) or [topic]
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
