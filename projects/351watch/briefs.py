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

FIELDS = ("id", "what", "where", "size", "who", "action", "next", "history", "can_speak", "line", "quote",
          "source_url", "written_at", "writer", "verified")
ACTIONS = ("hearing", "vote", "discussion", "continued", "adopted", "withdrawn", "other")
LINE_MAX = 90
# The cue each action needs within CUE_REACH characters of the quote (or anywhere, when there is no quote).
ACTION_CUES = {
    "hearing": r"\bhearing",
    "vote": r"\bvot(?:e|es|ed|ing)\b|to see if the (?:town|city) will|\bmotion\b|\bapprov|\bdecision\b",
    "discussion": r"\bdiscuss|\breview|\bupdate|\bpresentation|\bworkshop|\breport|\bconsider",
    "continued": r"continu",
    "adopted": r"\badopt|\benact|\bordain",
    "withdrawn": r"\bwithdr",
    "other": r"",
}
SPEAK_CUE = r"public\s+(?:hearing|comment|input|forum)|citizen(?:s'?|s’)?\s+(?:comment|forum|input)|open\s+forum"
CUE_REACH = 700
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
    "4.9MW," and "4.9 MW" read the same."""
    s = norm(s)
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
    if low in MONTH_ABBR:  # "Oct" in the brief, "October" in the agenda
        return has_phrase(MONTH_ABBR[low], loose_text)
    if low.endswith("'s") or low.endswith("’s"):
        return has_phrase(low[:-2], loose_text)
    return False


def checkable_tokens(value):
    """Tokens of a sentence that must be in the agenda: proper nouns (capitalized, not only sentence-initial,
    or all caps) and anything with a digit."""
    words = (value or "").translate(_TRANS).split()
    out = []
    start = True
    for i, w in enumerate(words):
        core = w.strip("\"'(),;:!?[]")
        if not core:
            continue
        nxt = words[i + 1].strip("\"'(),;:!?[]") if i + 1 < len(words) else ""
        if re.search(r"\d", core):
            out.append(core)
        elif core[:1].isupper():
            if len(core) >= 2 and core.isupper():
                out.append(core)
            elif not start or (nxt[:1].isupper() and nxt.lower() not in STOP):
                out.append(core)
        start = core.endswith((".", "!", "?", ":"))
    return out


def all_tokens(value):
    return [w.strip("\"'(),;:!?[].") for w in (value or "").translate(_TRANS).split()
            if w.strip("\"'(),;:!?[].").lower() not in STOP and len(w.strip("\"'(),;:!?[].")) >= 2]


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

def verify(brief, text, town_dates=None):
    """Reasons the brief fails against the agenda text; [] when every check passes. `town_dates` is the
    set of ISO meeting dates we hold for the brief's town (for `history`)."""
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
        missing = [t for t in tokens if not has_token(t, text_loose)]
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
    near = text_norm[max(0, qpos - CUE_REACH):qpos + len(norm(brief.get("quote") or "")) + CUE_REACH] if qpos >= 0 else text_norm
    cue = ACTION_CUES.get(brief.get("action") or "other", "")
    if cue and not re.search(cue, near, re.I):
        fails.append(f"action {brief['action']!r}: no sign of it near the quote")
    if brief.get("can_speak") is True:
        wide = text_norm[max(0, qpos - SPEAK_REACH):qpos + SPEAK_REACH] if qpos >= 0 else text_norm
        if not re.search(SPEAK_CUE, wide, re.I):
            fails.append("can_speak is true but the agenda doesn't say public hearing or public comment nearby")
    if brief.get("history") and town_dates is not None:
        held = {(int(d[:4]), int(d[5:7]), int(d[8:10])) for d in town_dates if re.match(r"\d{4}-\d\d-\d\d", d or "")}
        for y, m, d in history_dates(brief["history"]):
            if not any((y is None or y == hy) and m == hm and d == hd for hy, hm, hd in held):
                fails.append(f"history names {m}/{d}{'/' + str(y) if y else ''}, which isn't a meeting date we hold for this town")
    return fails


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
