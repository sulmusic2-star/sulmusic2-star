"""Attribute hits from a county body's agenda to the township the item is about.

Michigan county planning commissions review every township zoning amendment (MCL 125.3307:
30 days, after the township planning commission's hearing and before the township board
votes), so their agendas list township items ("Raisinville Township - Text Amendment -
Solar Energy Systems"). A township watcher should see those items under the township, so a
hit from a county row marked "attribute_townships": true is filed under the township named
in the agenda item (the nearest "<Name> Township" before the keyword, within the item), and
keeps the county body as `board` ("Monroe County Planning Commission"). A hit that names no
township stays with the county.
"""

from __future__ import annotations

import re

from .keywords import clean_text

_TWP = re.compile(r"\b(?:Charter\s+)?Township\s+of\s+((?:[A-Z][a-z]+\s+){0,2}[A-Z][A-Za-z']+)"
                  r"|\b((?:[A-Z][a-z]+\.?\s+){0,2}[A-Z][A-Za-z']+)\s+(?:Charter\s+)?(?:Township|Twp\.?)\b")
_STOP = {"county", "the", "this", "each", "said", "adjacent", "neighboring", "neighbouring", "charter", "township",
         "board", "planning", "zoning", "civil", "michigan", "public", "act", "rural", "agricultural", "general",
         "local", "any", "all", "other", "such", "a", "an", "of", "and", "for", "to", "in", "by", "with", "our",
         "your", "their", "its", "per", "from", "regular", "special", "joint", "city", "village", "state",
         "commission", "commissioners", "supervisor", "clerk", "treasurer", "trustee", "trustees", "member",
         "members", "staff", "applicant", "request", "requests", "case", "item", "re", "proposed", "amended",
         "amendment", "ordinance", "text", "map", "attached", "subject", "host", "participating", "respective",
         "various", "several", "both", "multiple", "affected", "unincorporated"}
_LEAD_STOP = re.compile(r"^(?:the|this|each|said|of|and|for|to|in|by|from|with|a|an)\s+", re.I)
WINDOW_BEFORE = 420          # an agenda item's heading sits shortly before its text
_ITEM_BREAK = re.compile(r"\b[A-Z]\.\s|\b\d{1,2}\.\s+[A-Z]|\bCase\s*(?:No\.?|#)", re.I)


def _name(m: re.Match) -> str | None:
    raw = (m.group(1) or m.group(2) or "").strip()
    raw = _LEAD_STOP.sub("", raw)
    words = [w for w in raw.split() if w.lower().strip(".'") not in _STOP]
    if not words:
        return None
    name = " ".join(words)
    return name if len(name) >= 3 and name[0].isupper() else None


def keyword_offset(snippet: str, state: str | None) -> int:
    """Offset of the first topic keyword in a snippet (the item the hit is about)."""
    from .keywords import _COMPILED, _state_matches
    offs = [m.start() for rxs in _COMPILED.values() for rx in rxs for m in rx.finditer(snippet)]
    offs += [s for s, _, _ in _state_matches(snippet, state)]
    return min(offs) if offs else min(90, len(snippet))


def township_named(text: str, anchor: int, end: int) -> str | None:
    """The township the item containing text[anchor] (the keyword) is about: the last township
    mention before the keyword within WINDOW_BEFORE characters, not crossing into the previous
    item where the text shows item numbering; else the first mention after it in the passage."""
    lo = max(0, anchor - WINDOW_BEFORE)
    breaks = list(_ITEM_BREAK.finditer(text, lo, anchor))
    if breaks:   # stay within the current item where item numbering is visible
        lo = breaks[-1].start()
    best = None
    for m in _TWP.finditer(text, lo, anchor):
        n = _name(m)
        if n:
            best = n
    if best:
        return best
    nxt = _ITEM_BREAK.search(text, anchor, end)   # not into the next item
    for m in _TWP.finditer(text, anchor, nxt.start() if nxt else end):
        n = _name(m)
        if n:
            return n
    return None


def canonical(name: str, known: dict[str, str]) -> str:
    """'Raisinville' -> the configured row name ('Raisinville Township') when we monitor it."""
    key = re.sub(r"[^a-z]", "", name.lower())
    return known.get(key) or f"{name} Township"


def attribute(hits: list[dict], raw_text: str, row: dict, known: dict[str, str]) -> None:
    """In place: county-body hits get town = the named township (county kept as board)."""
    county = row.get("county") or re.sub(r"\s+County$", "", row["town"])
    text = clean_text(raw_text)
    for h in hits:
        pos = text.find(h["snippet"][:120].rstrip("…"))
        if pos < 0:
            continue
        anchor = pos + keyword_offset(h["snippet"], row.get("state"))
        twp = township_named(text, anchor, pos + len(h["snippet"]))
        if twp:
            h["town"] = canonical(twp, known)
            h["county"] = county
            h["attributed_from"] = row["town"]


def known_townships(rows: list[dict], county: str) -> dict[str, str]:
    """normalized short name -> row name, for monitored townships in `county`."""
    out = {}
    for r in rows:
        if r.get("county") == county and r.get("kind") in ("township", "city"):
            short = re.sub(r"\b(?:charter\s+)?township\b|\bcity\s+of\b", "", r["town"], flags=re.I)
            out[re.sub(r"[^a-z]", "", short.lower())] = r["town"]
    return out
