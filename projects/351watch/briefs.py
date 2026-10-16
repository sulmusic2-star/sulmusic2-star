#!/usr/bin/env python3
"""Written briefs for agenda items: where they live, how they load, and how they are checked.

A brief is a short written explanation of one flagged agenda item, keyed by the hit's id (the 12-hex id
in data/hits_current.json). The site shows a brief in place of its rules-based sentence, but only after
tools/verify_briefs.py has checked every fact in it against the agenda's own text in data/search and set
`verified` to true. Nothing unverified renders.

Storage: data/briefs/<ST>/<YYYY-MM>.jsonl, one row per brief, in the month of the hit's meeting
(undated.jsonl when the hit has no date), like data/search. Files are append-only: a later row for the
same id replaces the earlier one (the latest `written_at` wins; file order breaks ties).

Fields, all optional except `id` and `written_at`:
  what        one plain sentence: what is proposed or being decided
  where       the address or location as the agenda gives it
  size        MW, acres, units, dollars, as stated
  who         the applicant or sponsor as named
  action      one of ACTIONS: hearing, vote, discussion, continued, adopted, withdrawn, other
  next        what happens next, if the agenda says
  history     earlier meetings on the same item, from our own data
  can_speak   true, false or null, from the agenda (public hearing, public comment)
  line        the one-line version, at most LINE_MAX characters
  quote       the exact agenda sentence or sentences the brief rests on
  source_url  the agenda document (the hit's source_url)
  written_at  ISO timestamp
  writer      who wrote it, e.g. "claude-fable-5-1"
  verified    true once the verifier passed; set by tools/verify_briefs.py, never by hand

Verification (verify()): every proper noun, number and address fragment in the brief, and the whole
`who` value, must appear in the document's text (case-insensitive, tolerant of punctuation); `quote`
must appear verbatim (whitespace and curly quotes aside); `action` must have its cue word near the
quote ("continued" needs "continu"); `can_speak: true` needs "public hearing" or "public comment"
nearby; dates in `history` must be meeting dates we hold for that town.
"""

import glob
import json
import os
import re
from datetime import date, datetime

FIELDS = ("id", "what", "where", "size", "who", "action", "next", "history", "can_speak", "how_to_speak", "line", "quote",
          "when_time", "when_place", "duplicate_of", "missing", "source_url", "written_at", "writer", "verified")
ACTIONS = ("hearing", "vote", "discussion", "continued", "adopted", "withdrawn", "extension", "other")
LINE_MAX = 90
# The cue each action needs within CUE_REACH characters of the quote (or anywhere, when there is no quote).
ACTION_CUES = {
    "hearing": r"\bhearing",
    "vote": r"\bvot(?:e|es|ed|ing)\b|to see if the (?:town|city)|\bmotion\b|\bapprov|\bdecision\b|\bresolution\b|"
            r"consider and act|\bact on\b|\bendorse|\bshall\b|second reading|final vote|\badopt|\bauthoriz|\border\b|"
            r"\brecommendation\b",
    "discussion": r"\bdiscuss|\breview|\bupdate|\bpresentation|\bworkshop|\breport|\bconsider|listening session|"
                  r"\binformational|\bstatus\b|\boverview|\bbriefing|\bforum\b|\b(?:old|new|unfinished|other) business\b|\binformal\b",
    "continued": r"continu",
    "adopted": r"\badopt|\benact|\bordain",
    "withdrawn": r"\bwithdr",
    "extension": r"\bextension|\bextend",
    "other": r"",
}
# A standing item anywhere on the agenda counts: residents can speak at the meeting.
SPEAK_CUE = (r"public\s+(?:hearing|comment|input|forum|participation)|citizen(?:s'?|s’)?\s+(?:comment|forum|input|time)|"
             r"open\s+forum|privilege of the floor|comments? from the public|public\s+to\s+be\s+heard|open\s+(?:mic|microphone)|"
             # a continued hearing, or the agenda itself saying who may speak ("non-members may speak", "wishing to speak")
             r"continuation\s+hearing|\bmay\s+speak\b|wish(?:ing|es)?\s+to\s+speak|opportunity\s+to\s+speak|speak\s+in\s+favor")
ABBREV = {  # the same place or body, written either way
    "st": "street", "rd": "road", "ave": "avenue", "hwy": "highway", "dr": "drive", "ln": "lane", "blvd": "boulevard",
    "ct": "court", "pl": "place", "rte": "route", "rt": "route", "tpke": "turnpike", "pkwy": "parkway", "cir": "circle",
    "ter": "terrace", "sq": "square", "mt": "mount", "ft": "foot",
    "zba": "zoning board of appeals", "bos": "board of selectmen", "concom": "conservation commission",
}
STAGE_WORDS = {"postponed", "hearing", "vote", "votes", "voted", "final", "discusses", "discussion", "decides", "withdrawn",
               "canceled", "cancelled", "continued", "mentions", "holds", "extension"}  # the site's own line vocabulary
ORDINARY = {"this", "it", "one", "nothing", "our", "town", "the", "a", "an", "if", "when", "no", "yes", "both", "each", "also",
            "its", "they", "there", "here", "that", "these", "those", "we", "he", "she", "but", "and", "or", "so", "not"}
# Bodies and processes a writer names from our own records, not the agenda's text.
BODY_NAMES = ("attorney general", "town meeting", "select board", "selectboard", "board of selectmen", "planning board",
              "zoning board", "board of appeals", "conservation commission", "city council", "town council", "town clerk",
              "secretary of state", "land court", "supreme judicial court", "zoning board of appeals")
STATE_WORDS = {"massachusetts", "new york", "rhode island", "connecticut", "new hampshire", "vermont", "maine"}
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
ASIDE = re.compile(r"our records|our copy|in our (?:copy|records|files)|per our|as the agenda spells|listed with a question mark|"
                   r"no rules stated|gives no rules|cut off in our", re.I)
CUE_REACH = 700
# A "Public Hearings" heading covers every item listed under it, so a hearing cue may sit further back.
HEARING_REACH = 1500
SPEAK_REACH = 1500
STOP = {"a", "an", "and", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with", "is", "are",
        "was", "were", "be", "will", "has", "have", "had", "its", "it", "this", "that", "as", "into", "near",
        "off", "up", "new", "no", "not", "per", "than", "then", "vs"}
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
MONTH_ABBR = {m[:3]: m for m in MONTHS} | {"sept": "september"}

_TRANS = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "„": '"', "–": "-", "—": "-", "−": "-",  # slop-lint: ignore
                        " ": " ", " ": " ", " ": " ", "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff",
                        "ﬃ": "ffi", "ﬄ": "ffl", "\xad": "", "​": "", "﻿": ""})  # slop-lint: ignore (characters, not copy)


# ---------------------------------------------------------------- storage

def brief_path(data_dir, state, meeting_date):
    """The file a brief belongs in: the hit's meeting month, or undated.jsonl."""
    month = (meeting_date or "")[:7] if re.match(r"\d{4}-\d{2}", meeting_date or "") else "undated"
    return os.path.join(data_dir, "briefs", state, f"{month}.jsonl")


def brief_files(data_dir):
    return sorted(glob.glob(os.path.join(data_dir, "briefs", "*", "*.jsonl")))


def read_rows(path):
    """The rows of one file, in order, with their line numbers. Lines that aren't JSON objects are skipped."""
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("id"):
                    rows.append((n, row))
    except OSError:
        pass
    return rows


def write_rows(path, rows):
    """Rewrite a file from its rows (used by the verifier to record `verified`); one JSON object per line."""
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_briefs(data_dir, verified_only=False):
    """{id: brief}, the latest row for each id across every file."""
    out = {}
    for path in brief_files(data_dir):
        for _, row in read_rows(path):
            prev = out.get(row["id"])
            if prev is None or (row.get("written_at") or "") >= (prev.get("written_at") or ""):
                out[row["id"]] = row
    if verified_only:
        out = {k: v for k, v in out.items() if v.get("verified") is True}
    return out


def append_brief(data_dir, brief, state, meeting_date=None):
    """Append one brief to its file. `verified` is cleared: only the verifier sets it."""
    row = {k: brief[k] for k in FIELDS if k in brief and k != "verified"}
    row.setdefault("written_at", datetime.now().astimezone().isoformat(timespec="seconds"))
    path = brief_path(data_dir, state, meeting_date)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    return path


# ---------------------------------------------------------------- text matching

def norm(s):
    """Lowercase, straight quotes, single spaces, no thousands separators; punctuation kept."""
    s = (s or "").translate(_TRANS)
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def loose(s):
    """norm() with punctuation gone, except the dot inside a number, and digits split from letters, so
    "4.9MW," and "4.9 MW" read the same. "U.S." is "us", "45'" and "45 ft" are "45 foot", "$1,660"
    is "1660", "Selectboard" is "select board"."""
    s = norm(s)
    s = re.sub(r"\bu\.s\.", "us", s)
    s = re.sub(r"(\d)\s*(?:'|′|-?\s*(?:ft\.?|feet|foot))(?![a-z])", r"\1 foot", s)
    s = re.sub(r"\bselect\s*board\b|\bselectboard\b", "select board", s)
    s = re.sub(r"'(\d\d)\b", r" yr\1 ", s)  # "'21": a two-digit year, kept apart from other numbers
    s = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", s)
    s = re.sub(r"[^a-z0-9.\s]+", " ", s)
    s = re.sub(r"(?<=\d)(?=[a-z])|(?<=[a-z])(?=\d)", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def has_phrase(phrase, loose_text):
    """Whole-token match of a loose() phrase in loose() text."""
    p = loose(phrase)
    if not p:
        return True
    return re.search(r"(?<![a-z0-9.])" + re.escape(p) + r"(?![a-z0-9])", loose_text) is not None


def has_token(tok, loose_text):
    if has_phrase(tok, loose_text):
        return True
    low = tok.lower().strip(".")
    if low.endswith("'s") or low.endswith("’s"):
        return has_token(tok[:-2], loose_text)
    year = re.fullmatch(r"(?:fy\s?)?(20(\d\d))", low)
    if year:  # "2021" also as "10/19/21" or "'21"; "FY2027" also as "FY27"
        yy = year.group(2)
        if low.startswith("fy") and has_phrase(f"fy {yy}", loose_text):
            return True
        if re.search(rf"(?<!\d)\d{{1,2}} \d{{1,2}} {yy}(?!\d)|\byr {yy}\b|\bfy {yy}\b", loose_text):
            return True
    if low in MONTH_ABBR:  # "Oct" in the brief, "October" in the agenda
        return has_phrase(MONTH_ABBR[low], loose_text)
    if low in ABBREV:  # "St" in the brief, "Street" in the agenda
        return has_phrase(ABBREV[low], loose_text)
    short = next((k for k, v in ABBREV.items() if v == low), None)
    if short:  # "Street" in the brief, "St." in the agenda
        return has_phrase(short, loose_text)
    if "-" in tok.strip("-"):  # "28.251-acre", "U.S.-made", "15-minute": the number or name is the fact
        parts = [x for x in tok.split("-") if x]
        facts = [x for x in parts if re.search(r"\d", x) or x[:1].isupper()]
        return all(has_token(x, loose_text) for x in facts) if facts else True
    return False


def weekday_tokens(value, year=None):
    """Weekday names in a date such as "Tue Oct 27" or "Tuesday, 10/27", when they are right for that date in
    `year` (or the next year): the agenda may print the date without its weekday."""
    out = set()
    years = [year] if year else [date.today().year, date.today().year + 1]
    for m in re.finditer(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\.?,?\s+(?:([A-Z][a-z]{2,8})\.?\s+(\d{1,2})|(\d{1,2})/(\d{1,2}))(?:,?\s+(20\d\d))?",
                         value or ""):
        name = m.group(1).lower()
        if m.group(2):
            mon = m.group(2).lower()
            month = MONTHS.index(mon) + 1 if mon in MONTHS else (MONTHS.index(MONTH_ABBR[mon]) + 1 if mon in MONTH_ABBR else None)
            day = int(m.group(3))
        else:
            month, day = int(m.group(4)), int(m.group(5))
        if not month:
            continue
        for y in ([int(m.group(6))] if m.group(6) else years + ([years[0] + 1] if month <= 3 else [])):  # January after a December meeting
            try:
                if WEEKDAYS[date(y, month, day).weekday()].startswith(name):
                    out.add(m.group(0).split()[0].strip(".,"))
                    break
            except ValueError:
                continue
    return out


def checkable_tokens(value):
    """Tokens of a sentence that must be in the agenda: proper nouns (capitalized, not only sentence-initial,
    or all caps) and anything with a digit."""
    words = (value or "").translate(_TRANS).split()
    out = []
    start = True
    for i, w in enumerate(words):
        core = w.strip("\"'(),;:!?[]").rstrip(".-").strip("\"'(),;:!?[]")
        if not core:
            continue
        nxt = words[i + 1].strip("\"'(),;:!?[].-") if i + 1 < len(words) else ""
        if re.search(r"\d", core):
            out.append(core)
        elif core[:1].isupper() and (core.rstrip(":").lower() in STAGE_WORDS or core.lower() in ORDINARY):
            pass  # "Postponed:", "Hearing", "This", "Our": the site's vocabulary or an ordinary word, not a fact
        elif core[:1].isupper():
            if len(core) >= 2 and core.isupper():
                out.append(core)
            elif not start:
                out.append(core)  # the first word of a sentence is capitalized whatever it is
        start = core.endswith((".", "!", "?", ":"))
    return out


def all_tokens(value):
    toks = [w.strip("\"'(),;:!?[].-") for w in (value or "").translate(_TRANS).split()]
    return [t for t in toks if t.lower() not in STOP and len(t) >= 2]


def find_quote(quote, text_norm):
    """Position of the quote in norm(text), or -1. "…" or "..." in the quote joins parts that must appear
    in order."""
    parts = [p.strip(" .") for p in re.split(r"…|\.\.\.", norm(quote)) if p.strip(" .")]
    if not parts:
        return -1
    pos = 0
    first = -1
    for part in parts:
        i = text_norm.find(part, pos)
        if i < 0:
            return -1
        if first < 0:
            first = i
        pos = i + len(part)
    return first


def history_dates(history):
    """Dates named in a history note: ISO, "October 6, 2026", "Oct 6", as [(year or None, month, day)]."""
    out = []
    for m in re.finditer(r"\b(20\d\d)-(\d\d)-(\d\d)\b", history or ""):
        out.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    for m in re.finditer(r"\b([A-Z][a-z]{2,8})\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(20\d\d))?", history or ""):
        name = m.group(1).lower()
        month = MONTHS.index(name) + 1 if name in MONTHS else (MONTHS.index(MONTH_ABBR[name]) + 1 if name in MONTH_ABBR else None)
        if month:
            out.append((int(m.group(3)) if m.group(3) else None, month, int(m.group(2))))
    return out


# ---------------------------------------------------------------- the check

def verify(brief, text, town_dates=None, year=None):
    """Reasons the brief fails against the agenda text; [] when every check passes. `town_dates` is the
    set of ISO meeting dates of every document we hold for the brief's town (for `history`); `year` is
    the meeting's year (for weekday names in dates)."""
    fails = []
    if not re.fullmatch(r"[0-9a-f]{12}", str(brief.get("id") or "")):
        fails.append("id is not a 12-hex hit id")
    try:
        datetime.fromisoformat(str(brief.get("written_at") or "").replace("Z", "+00:00"))
    except ValueError:
        fails.append("written_at is not an ISO timestamp")
    for k in brief:
        if k not in FIELDS:
            fails.append(f"unknown field {k}")
    if brief.get("action") is not None and brief.get("action") not in ACTIONS:
        fails.append(f"action {brief.get('action')!r} is not one of {', '.join(ACTIONS)}")
    if brief.get("can_speak") not in (True, False, None):
        fails.append("can_speak must be true, false or null")
    line = brief.get("line") or ""
    if len(line) > LINE_MAX:
        fails.append(f"line is {len(line)} characters, more than {LINE_MAX}")
    if not text:
        fails.append("no agenda text for this document in data/search")
        return fails
    text_norm = norm(text)
    text_loose = loose(text)

    def need(field, tokens):
        ok_days = weekday_tokens(brief.get(field), year)
        value_loose = loose(brief.get(field))
        spelled = set()  # words of a body's full name when the agenda uses its abbreviation ("ZBA")
        for short, full in ABBREV.items():
            if " " in full and full in value_loose and has_phrase(short, text_loose):
                spelled.update(full.split())
        for body in BODY_NAMES:  # bodies and processes a writer names from our own records
            if re.search(r"(?<![a-z])" + re.escape(body) + r"(?![a-z])", value_loose):
                spelled.update(body.split())
        if "state law" in value_loose or "state s" in value_loose:
            for st in STATE_WORDS:
                spelled.update(st.split())
        missing = [t for t in tokens if t.strip(".,") not in ok_days and t.lower() not in spelled and not has_token(t, text_loose)]
        if missing:
            fails.append(f"{field}: not in the agenda: {', '.join(dict.fromkeys(missing))}")

    for field in ("what", "line", "next", "size"):
        need(field, checkable_tokens(brief.get(field)))
    if brief.get("where"):
        need("where", all_tokens(brief["where"]))
    if brief.get("who"):
        if not has_phrase(brief["who"], text_loose):
            need("who", all_tokens(brief["who"]))
    qpos = -1
    if brief.get("quote"):
        qpos = find_quote(brief["quote"], text_norm)
        if qpos < 0:
            fails.append("quote is not in the agenda word for word")
    elif brief.get("what") or brief.get("line"):
        fails.append("no quote to rest on")
    reach = HEARING_REACH if brief.get("action") == "hearing" else CUE_REACH
    near = text_norm[max(0, qpos - reach):qpos + len(norm(brief.get("quote") or "")) + CUE_REACH] if qpos >= 0 else text_norm
    cue = ACTION_CUES.get(brief.get("action") or "other", "")
    if cue and not re.search(cue, near, re.I):
        fails.append(f"action {brief['action']!r}: no sign of it near the quote")
    if brief.get("can_speak") is True and not re.search(SPEAK_CUE, text_norm, re.I):
        fails.append("can_speak is true but the agenda has no public hearing or public comment item")
    # General knowledge is not the agenda: a vote threshold may be stated only when the document states it.
    for key in ("line", "what", "next"):
        if re.search(r"two.thirds", brief.get(key) or "", re.I) and not re.search(r"two.thirds|2/3", text_norm, re.I):
            fails.append(f"{key}: names a two-thirds vote the agenda doesn't mention")
    # The page is for the reader, not the newsroom: no asides about our records, our copy or how the agenda
    # spells a name, and no "no rules stated" (leave how_to_speak empty and the default rule applies).
    for key in ("line", "what", "history", "next", "how_to_speak", "where", "size", "who"):
        m = ASIDE.search(brief.get(key) or "")
        if m:
            fails.append(f"{key}: says {m.group(0)!r}; say what the agenda says, or leave it out")
    if brief.get("history") and town_dates is not None:
        held = {(int(d[:4]), int(d[5:7]), int(d[8:10])) for d in town_dates if re.match(r"\d{4}-\d\d-\d\d", d or "")}
        for y, m, d in history_dates(brief["history"]):
            if not any((y is None or y == hy) and m == hm and d == hd for hy, hm, hd in held):
                fails.append(f"history names {m}/{d}{'/' + str(y) if y else ''}, which isn't a meeting date we hold for this town")
    return fails


def search_dates(data_dir):
    """{"MA:Carver": {ISO meeting dates}} of every document in data/search: the dates a brief's `history`
    may name, whether or not that agenda had a flagged item."""
    out = {}
    for path in sorted(glob.glob(os.path.join(data_dir, "search", "*", "*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("town") and r.get("meeting_date"):
                    out.setdefault(f"{r.get('state', 'MA')}:{r['town']}", set()).add(r["meeting_date"][:10])
    return out


def doc_texts(data_dir, urls):
    """{url: text} from data/search for the urls given (a document's url or its source_url)."""
    want = {u for u in urls if u}
    out = {}
    for path in sorted(glob.glob(os.path.join(data_dir, "search", "*", "*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                for u in (r.get("url"), r.get("source_url")):
                    if u in want and u not in out and r.get("text"):
                        out[u] = r["text"]
    return out
