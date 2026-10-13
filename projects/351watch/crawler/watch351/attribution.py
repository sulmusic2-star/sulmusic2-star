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


MAX_ITEM_CHARS = 700        # an agenda item line, not a page of staff report


def norm_ctx_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def split_items(hits: list[dict], raw_text: str, row: dict, known: dict[str, str], base: dict) -> list[dict]:
    """Extra hits for a county body's document: one per agenda item (on agenda or minutes pages)
    that names a township and matches a topic, for every township the regular hits do not
    already file. A county planning commission's coordination list ("a. 08-26-01, Fredonia
    Township: Zoning Text Amendment b. 08-26-02, Marshall Township: Zoning Map Amendment") is
    one snippet to the matcher but one item per township to a watcher. `base` carries the
    document's fields (board, meeting date, source URL...). The board stays the county body."""
    from .keywords import SNIPPET_MAX, _page_spans, topics_in
    county = row.get("county") or re.sub(r"\s+County$", "", row["town"])
    text, spans = _page_spans(raw_text)
    have = {(h.get("town"), (h.get("snippet") or "")[:80]) for h in hits}
    filed = {h.get("town") for h in hits if h.get("attributed_from")}
    out: list[dict] = []
    seen_items: set[tuple[str, str]] = set()
    for s, e, cls in spans:
        if cls not in ("agenda", "minutes"):
            continue
        cuts = [m.start() for m in _ITEM_BREAK.finditer(text, s, e)] + [e]
        for a, b in zip([s] + cuts, cuts):
            item = text[a:b].strip()
            if not item or len(item) > MAX_ITEM_CHARS:
                continue
            twp = None
            for m in _TWP.finditer(item):
                twp = _name(m)
                if twp:
                    break
            if not twp or twp.lower() == county.lower():
                continue
            topics = topics_in(item, row.get("state"))
            topics = [t for t in topics if t != "40b_comprehensive_permit"]
            if not topics:
                continue
            town = canonical(twp, known)
            snippet = item if len(item) <= SNIPPET_MAX else item[:SNIPPET_MAX - 1].rstrip() + "…"
            key = (town, norm_ctx_text(item)[:120])
            if key in seen_items or (town, snippet[:80]) in have:
                continue
            # the regular hit for this township already covers this item
            if town in filed and any(h.get("town") == town and item[:60] in (h.get("snippet") or "") for h in hits):
                continue
            seen_items.add(key)
            out.append({**base, "town": town, "county": county, "attributed_from": row["town"],
                        "topics": topics, "snippet": snippet, "_context": norm_ctx_text(item)[:200]})
    return out


COVERAGE_NOTE = "Zoning changes reach us through the {body}; project permits may not."
# Counties where the county itself administers zoning for many townships: its planning commission
# also hears their special approvals (Huron County's Pinesap Solar SAP), so the line says so.
COUNTY_COVERAGE_NOTE = {
    "Huron": ("Zoning changes reach us through the {body}, and so do special approvals where the county "
              "administers zoning; other project permits may not."),
}


def coverage_modes(rows: list[dict]) -> dict[str, dict]:
    """How each Michigan township is covered, for its page on the site:

    direct      - we read the township's own agendas (its row is automated)
    via_county  - we do not, but we read its county planning commission, which reviews the
                  township's zoning amendments (MCL 125.3307): zoning changes reach us, project
                  permits (special land use, site plans) and other township business may not
    none        - neither

    Returns town -> {"coverage", "coverage_county_body", "coverage_note"}; the county body is
    named for direct townships too (both routes apply)."""
    county_pc = {r.get("county"): r for r in rows
                 if r.get("kind") == "county" and r.get("attribute_townships") and r.get("automated")}
    out = {}
    for r in rows:
        if r.get("kind") != "township":
            continue
        cpc = county_pc.get(r.get("county"))
        body = f"{r.get('county')} County Planning Commission" if cpc else None
        mode = "direct" if r.get("automated") else ("via_county" if cpc else "none")
        out[r["town"]] = {"coverage": mode, "coverage_county_body": body,
                          "coverage_note": COUNTY_COVERAGE_NOTE.get(r.get("county"), COVERAGE_NOTE).format(body=body)
                          if mode == "via_county" else None}
    return out


def known_townships(rows: list[dict], county: str) -> dict[str, str]:
    """normalized short name -> row name, for monitored townships in `county` (only townships:
    "Marshall Township" is not the City of Marshall)."""
    out = {}
    for r in rows:
        if r.get("county") == county and r.get("kind") == "township":
            short = re.sub(r"\b(?:charter\s+)?township\b|\bcity\s+of\b", "", r["town"], flags=re.I)
            out[re.sub(r"[^a-z]", "", short.lower())] = r["town"]
    return out
