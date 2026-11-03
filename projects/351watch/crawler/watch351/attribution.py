"""Attribute hits from a county body's agenda to the township the item is about.

Michigan county planning commissions review every township zoning amendment (MCL 125.3307:
30 days, after the township planning commission's hearing and before the township board
votes), so their agendas list township items ("Raisinville Township - Text Amendment -
Solar Energy Systems"). A township watcher should see those items under the township, so a
hit from a county row marked "attribute_townships": true is filed under the township named
in the agenda item (the nearest "<Name> Township" before the keyword, within the item), and
keeps the county body as `board` ("Monroe County Planning Commission"). A hit that names no
township stays with the county.

New York (wave 2, 2026-11): county planning boards receive every town, village and city zoning
action within 500 feet of a county or state road, municipal line or county facility under
General Municipal Law 239-m, so their agendas list municipal items ("Town of Carlisle - Local
Law 2 of 2026 - Battery Energy Storage Moratorium", "T/Sherman - site plan"). For a row with
"state": "NY" the item's municipality is the "Town of / Village of / City of <Name>" (or
"T/ V/ C/ <Name>", "<Name> (T)") nearest the keyword, resolved against the state's town and
city names (data/neighbors.json) and the configured rows; a village or city that is not a
configured row is filed as "<Name> (village)" / "<Name> (city)", the site's own convention for
places that share a town's name.
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


# New York: "Town of New Windsor", "Village of Mayville", "City of Glen Cove", "T/Sherman", "V/ Mayville",
# "Carlisle (T)". Groups 1-2: kind and name ("of" form); 3-4: abbreviation form; 5-6: suffix form.
_NY_MUNI = re.compile(
    r"\b(Town|Village|City)\s+of\s+(?:the\s+)?((?:[A-Z][A-Za-z'.]+\s+){0,2}[A-Z][A-Za-z'.]+)"
    r"|\b(T|V|C)\s*[/.:]\s*(?!(?:Town|Village|City)\b)((?:[A-Z][A-Za-z'.]+\s+){0,2}[A-Z][A-Za-z'.]+)"
    r"|\b((?:[A-Z][A-Za-z'.]+\s+){0,2}[A-Z][A-Za-z'.]+)\s*\(\s*(T|V|C)\s*\)")
_NY_KIND = {"town": "town", "t": "town", "village": "village", "v": "village", "city": "city", "c": "city"}
_NY_STOP = {"town", "village", "law", "laws", "resolution", "moratorium", "site", "plan", "referral", "special",
            "use", "permit", "variance", "subdivision", "area", "comprehensive", "code", "chapter", "section",
            "district", "battery", "solar", "energy", "storage", "system", "systems", "data", "center", "centers",
            "introductory", "intro", "no", "zba", "pb", "tb", "planning", "zoning", "board", "appeals", "county"}
_NY_NAMES: set[str] | None = None


def _ny_names() -> set[str]:
    """Every New York town and city name (data/neighbors.json, the site's NY boundary list), lower-cased
    and without the ' (city)' / ' (<County> County)' suffixes; empty when the file is absent."""
    global _NY_NAMES
    if _NY_NAMES is None:
        import json
        from pathlib import Path
        names: set[str] = set()
        try:
            doc = json.loads((Path(__file__).resolve().parents[2] / "data" / "neighbors.json").read_text())
            for k in doc:
                if k.startswith("NY:"):
                    names.add(re.sub(r"\s+\((?:city|[A-Za-z. ]+ County)\)$", "", k[3:]).lower())
        except (OSError, ValueError):
            pass
        _NY_NAMES = names
    return _NY_NAMES


def _ny_name(raw: str, known: dict[str, str]) -> str | None:
    """The municipality in a captured run of capitalised words ("Carlisle Planning Board", "New Windsor
    Local Law"): the longest leading word run that is a known NY place; else the run with stop words
    dropped, as for Michigan."""
    words = raw.split()
    if words and re.fullmatch(r"[A-Z]\.|\d{1,2}\.", words[0]):   # an item letter or number glued to the name
        words = words[1:]
    for n in range(min(3, len(words)), 0, -1):
        cand = " ".join(words[:n]).strip(".,;:")
        key = re.sub(r"[^a-z]", "", cand.lower())
        if key in known or f"town:{key}" in known or cand.lower() in _ny_names():
            return cand
    kept = [w for w in words if w.lower().strip(".'") not in _STOP | _NY_STOP]
    name = " ".join(kept).strip(".,;:")
    return name if len(name) >= 3 and name[0].isupper() else None


def muni_mentions(text: str, state: str | None, known: dict[str, str] | None = None, lo: int = 0,
                  hi: int | None = None):
    """Yield (match_start, name, kind) for every municipality mention in text[lo:hi]: Michigan / Ohio
    townships (kind "township") or, for New York rows, towns, villages and cities."""
    hi = len(text) if hi is None else hi
    if (state or "").upper() == "NY":
        for m in _NY_MUNI.finditer(text, lo, hi):
            if m.group(1):
                kind, raw = m.group(1), m.group(2)
            elif m.group(3):
                kind, raw = m.group(3), m.group(4)
            else:
                kind, raw = m.group(6), m.group(5)
            name = _ny_name(raw, known or {})
            if name:
                yield m.start(), name, _NY_KIND[kind.lower()]
        return
    for m in _TWP.finditer(text, lo, hi):
        n = _name(m)
        if n:
            yield m.start(), n, "township"


def muni_named(text: str, anchor: int, end: int, state: str | None = None,
               known: dict[str, str] | None = None) -> tuple[str, str] | None:
    """The municipality the item containing text[anchor] (the keyword) is about, as (name, kind): the
    last mention before the keyword within WINDOW_BEFORE characters, not crossing into the previous
    item where the text shows item numbering; else the first mention after it in the passage."""
    lo = max(0, anchor - WINDOW_BEFORE)
    breaks = list(_ITEM_BREAK.finditer(text, lo, anchor))
    if breaks:   # stay within the current item where item numbering is visible
        lo = breaks[-1].start()
    best = None
    for _, n, k in muni_mentions(text, state, known, lo, anchor):
        best = (n, k)
    if best:
        return best
    nxt = _ITEM_BREAK.search(text, anchor, end)   # not into the next item
    for _, n, k in muni_mentions(text, state, known, anchor, nxt.start() if nxt else end):
        return (n, k)
    return None


def keyword_offset(snippet: str, state: str | None) -> int:
    """Offset of the first topic keyword in a snippet (the item the hit is about)."""
    from .keywords import _COMPILED, _state_matches
    offs = [m.start() for rxs in _COMPILED.values() for rx in rxs for m in rx.finditer(snippet)]
    offs += [s for s, _, _ in _state_matches(snippet, state)]
    return min(offs) if offs else min(90, len(snippet))


def township_named(text: str, anchor: int, end: int) -> str | None:
    """The township the item containing text[anchor] (the keyword) is about (Michigan / Ohio rows); see
    muni_named for the (name, kind) form that New York rows need."""
    found = muni_named(text, anchor, end)
    return found[0] if found else None


def canonical(name: str, known: dict[str, str], kind: str = "township") -> str:
    """'Raisinville' -> the configured row name ('Raisinville Township') when we monitor it. New York:
    the configured row of that kind ('Glen Cove' the city, 'Mayville' the village), else the bare name
    for a town and '<Name> (village)' / '<Name> (city)' otherwise (the site's convention)."""
    key = re.sub(r"[^a-z]", "", name.lower())
    if kind == "township":
        return known.get(key) or f"{name} Township"
    return known.get(f"{kind}:{key}") or known.get(key) or (name if kind == "town" else f"{name} ({kind})")


def resolve_known(name: str, known: dict[str, str]) -> str | None:
    """The monitored row a parsed township name refers to, or None. Tries the whole name, then its last
    two words and its last word ("777 Kinnear Road Clinton Township" -> Clinton Township; "Jack Reynolds
    Township", a clerk's name before the word, resolves to nothing). Rows that carry
    `attribute_known_only` (every township of the county is a row, as in the Great Lakes wave) file a
    county item only under a resolved row, never under an invented township."""
    words = name.split()
    for n in (len(words), 2, 1):
        if n > len(words):
            continue
        key = re.sub(r"[^a-z]", "", " ".join(words[-n:]).lower())
        if key in known:
            return known[key]
    return None


def covered_counties(row: dict) -> list[str]:
    """Counties a county body reviews townships for: `covers_counties` on the row (a regional planning
    commission serving several counties, e.g. Logan-Union-Champaign), else the row's own county."""
    return list(row.get("covers_counties") or [row.get("county") or re.sub(r"\s+County$", "", row["town"])])


def body_name(row: dict) -> str:
    """The reviewing body's name for `board` and the coverage fields: `county_body` on the row when set
    ("Delaware County Regional Planning Commission"), else "<County> County Planning Commission"."""
    county = row.get("county") or re.sub(r"\s+County$", "", row["town"])
    return row.get("county_body") or f"{county} County Planning Commission"


_BARE_DELIM = r"(?:^|[/|,;]\s*){name}(?=\s*(?:[/|,;]|$))"


def bare_township(text: str, known: dict[str, str]) -> str | None:
    """A township named by its bare name in a delimited field ("07-25.1 / Estates at Berlin Sec 1 /
    Berlin / 25 lots": the Delaware County Regional Planning Commission's monthly mailing lists items
    this way, with no "Township"). Only rows that opt in (`township_bare_names: true`) use it, and
    only a monitored township's name counts, delimited on both sides by / | , or ; so "Orange" or
    "Liberty" in running text never matches. Returns the row name."""
    best = None
    for row_name in known.values():
        short = re.sub(r"\s*\([^)]*\)|\b(?:Charter\s+)?Township\b", "", row_name).strip()
        if len(short) < 3:
            continue
        m = re.search(_BARE_DELIM.format(name=re.escape(short)), text, re.M)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), row_name)
    return best[1] if best else None


def attribute(hits: list[dict], raw_text: str, row: dict, known: dict[str, str],
              county_of: dict[str, str] | None = None) -> None:
    """In place: county-body hits get town = the named township (county kept as board). `county_of`
    (row name -> county) places a township in its own county when the body covers several; without it
    the row's county is used, as before."""
    county = row.get("county") or re.sub(r"\s+County$", "", row["town"])
    text = clean_text(raw_text)
    for h in hits:
        pos = text.find(h["snippet"][:120].rstrip("…"))
        if pos < 0:
            continue
        anchor = pos + keyword_offset(h["snippet"], row.get("state"))
        found = muni_named(text, anchor, pos + len(h["snippet"]), row.get("state"), known)
        if not found and row.get("township_bare_names"):
            bare = bare_township(text[max(0, anchor - WINDOW_BEFORE):pos + len(h["snippet"])], known)
            found = (bare, "row") if bare else None
        if found and row.get("attribute_known_only") and found[1] != "row":
            resolved = resolve_known(found[0], known)
            found = (resolved, "row") if resolved else None   # an unresolved name stays with the county body
        if found:
            h["town"] = found[0] if found[1] == "row" else canonical(found[0], known, found[1])
            h["county"] = (county_of or {}).get(h["town"]) or county
            h["attributed_from"] = row["town"]


MAX_ITEM_CHARS = 700        # an agenda item line, not a page of staff report


def norm_ctx_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def split_items(hits: list[dict], raw_text: str, row: dict, known: dict[str, str], base: dict,
                county_of: dict[str, str] | None = None) -> list[dict]:
    """Extra hits for a county body's document: one per agenda item (on agenda or minutes pages)
    that names a township and matches a topic, for every township the regular hits do not
    already file. A county planning commission's coordination list ("a. 08-26-01, Fredonia
    Township: Zoning Text Amendment b. 08-26-02, Marshall Township: Zoning Map Amendment") is
    one snippet to the matcher but one item per township to a watcher. `base` carries the
    document's fields (board, meeting date, source URL...). The board stays the county body."""
    from .keywords import SNIPPET_MAX, _page_spans, topics_in
    county = row.get("county") or re.sub(r"\s+County$", "", row["town"])
    counties_lower = {c.lower() for c in covered_counties(row)}
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
            first = next(muni_mentions(item, row.get("state"), known), None)
            twp, kind = (first[1], first[2]) if first else (None, "township")
            if not twp and row.get("township_bare_names"):
                bare = bare_township(item, known)
                twp, kind = (bare, "row") if bare else (None, "township")
            if not twp or twp.lower() in counties_lower:
                continue
            if row.get("attribute_known_only") and kind != "row":
                resolved = resolve_known(twp, known)
                if not resolved:
                    continue
                twp, kind = resolved, "row"
            topics = topics_in(item, row.get("state"))
            topics = [t for t in topics if t != "40b_comprehensive_permit"]
            if not topics:
                continue
            town = twp if kind == "row" else canonical(twp, known, kind)
            snippet = item if len(item) <= SNIPPET_MAX else item[:SNIPPET_MAX - 1].rstrip() + "…"
            key = (town, norm_ctx_text(item)[:120])
            if key in seen_items or (town, snippet[:80]) in have:
                continue
            # the regular hit for this township already covers this item
            if town in filed and any(h.get("town") == town and item[:60] in (h.get("snippet") or "") for h in hits):
                continue
            seen_items.add(key)
            out.append({**base, "town": town, "county": (county_of or {}).get(town) or county,
                        "attributed_from": row["town"],
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
    county_pc: dict[str, dict] = {}
    for r in rows:
        if r.get("kind") == "county" and r.get("attribute_townships") and r.get("automated"):
            for c in covered_counties(r):   # a regional commission covers several counties
                county_pc.setdefault(c, r)
    out = {}
    for r in rows:
        # Michigan / Ohio: townships; New York (state on the row): towns, villages and cities, all of
        # which the county planning board sees under GML 239-m
        kinds = NY_MEMBER_KINDS if (r.get("state") or "").upper() == "NY" else ("township",)
        if r.get("kind") not in kinds:
            continue
        cpc = county_pc.get(r.get("county"))
        body = body_name(cpc) if cpc else None
        mode = "direct" if r.get("automated") else ("via_county" if cpc else "none")
        out[r["town"]] = {"coverage": mode, "coverage_county_body": body,
                          "coverage_note": COUNTY_COVERAGE_NOTE.get(r.get("county"), COVERAGE_NOTE).format(body=body)
                          if mode == "via_county" else None}
    return out


NY_MEMBER_KINDS = ("town", "village", "city")


def known_townships(rows: list[dict], county: str | list[str]) -> dict[str, str]:
    """normalized short name -> row name, for monitored townships in `county` (one county or a list of
    counties a regional body covers; only townships: "Marshall Township" is not the City of Marshall).
    Two counties with a same-named township: the first in the list wins (the body says which county
    it means in its item, which `county_of` then carries)."""
    counties = [county] if isinstance(county, str) else list(county)
    out = {}
    for c in counties:
        for r in rows:
            if r.get("county") != c:
                continue
            if (r.get("state") or "").upper() == "NY":
                # New York rows: "<kind>:<name>" so "City of Corning" and "Town of Corning" resolve apart,
                # plus the bare name for towns (the default kind when an agenda says only the name)
                if r.get("kind") in NY_MEMBER_KINDS:
                    short = re.sub(r"\s+\((?:city|village|town|[A-Za-z. ]+ County)\)$", "", r["town"])
                    key = re.sub(r"[^a-z]", "", short.lower())
                    out.setdefault(f"{r['kind']}:{key}", r["town"])
                    if r["kind"] == "town":
                        out.setdefault(key, r["town"])
                continue
            if r.get("kind") == "township":
                # "Liberty Township (Delaware County)": Ohio rows disambiguate same-named townships this way
                short = re.sub(r"\s*\([^)]*\)|\b(?:charter\s+)?township\b|\bcity\s+of\b", "", r["town"], flags=re.I)
                out.setdefault(re.sub(r"[^a-z]", "", short.lower()), r["town"])
    return out


def township_counties(rows: list[dict], counties: list[str]) -> dict[str, str]:
    """row name -> county for monitored townships in `counties` (the `county_of` argument of
    attribute / split_items)."""
    return {r["town"]: r["county"] for r in rows if r.get("county") in counties
            and (r.get("kind") == "township"
                 or ((r.get("state") or "").upper() == "NY" and r.get("kind") in NY_MEMBER_KINDS))}
