"""Pull a meeting date out of the messy strings towns use.

Handles "October 13, 2026", "Tue, Oct 13, 2026", "10/13/2026", "10-13-26",
"10.13.26", CivicPlus ids like "_10132026-140", and "2026_Oct_13".
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import unquote

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

_MONTH_RE = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"

_PATTERNS = [
    # October 13, 2026 / Oct. 13 2026
    (re.compile(_MONTH_RE + r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", re.I), "mdy_name"),
    # 13 October 2026
    (re.compile(r"(\d{1,2})\s+" + _MONTH_RE + r",?\s+(\d{4})", re.I), "dmy_name"),
    # 2026_Oct_13 / 2026-Oct-13
    (re.compile(r"(\d{4})[\s_\-]+" + _MONTH_RE + r"[\s_\-]+(\d{1,2})\b", re.I), "ymd_name"),
    # 2026-10-13
    (re.compile(r"\b(20\d{2})[-_.](\d{1,2})[-_.](\d{1,2})\b"), "ymd"),
    # CivicPlus: _10132026-140
    (re.compile(r"_(\d{2})(\d{2})(20\d{2})-\d+"), "mdy"),
    # 10/13/2026, 10-13-26, 10.13.26, 1-12-2026
    (re.compile(r"(?<!\d)(\d{1,2})[/\-._](\d{1,2})[/\-._](20\d{2}|\d{2})(?!\d)"), "mdy"),
]


def _mk(y: int, m: int, d: int) -> date | None:
    if y < 100:
        y += 2000
    try:
        dt = date(y, m, d)
    except ValueError:
        return None
    return dt if 2000 <= dt.year <= 2100 else None


def parse_date(s: str | None) -> date | None:
    """Return the first plausible date found in `s`, else None."""
    if not s:
        return None
    s = unquote(s)
    for rx, kind in _PATTERNS:
        for m in rx.finditer(s):
            g = m.groups()
            if kind == "mdy_name":
                dt = _mk(int(g[2]), MONTHS[g[0][:3].lower()], int(g[1]))
            elif kind == "dmy_name":
                dt = _mk(int(g[2]), MONTHS[g[1][:3].lower()], int(g[0]))
            elif kind == "ymd_name":
                dt = _mk(int(g[0]), MONTHS[g[1][:3].lower()], int(g[2]))
            elif kind == "ymd":
                dt = _mk(int(g[0]), int(g[1]), int(g[2]))
            else:  # mdy
                dt = _mk(int(g[2]), int(g[0]), int(g[1]))
            if dt:
                return dt
    return None


def first_date(*candidates: str | None) -> date | None:
    for c in candidates:
        d = parse_date(c)
        if d:
            return d
    return None


# A warrant names its meeting day near the top: "Saturday, October 17, 2026" or "on Monday, the
# Nineteenth day of October, 2026". A bare "July 1, 2026" is the fiscal year, not the meeting.
_WEEKDAY = r"(?:Mon|Tues?|Wed(?:nes)?|Thu(?:rs)?|Fri|Sat(?:ur)?|Sun)(?:day)?\.?"
_MONTH_NAME = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
_ORDINAL = {w: i for i, w in enumerate(
    ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh",
     "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth",
     "twentieth", "twenty-first", "twenty-second", "twenty-third", "twenty-fourth", "twenty-fifth", "twenty-sixth",
     "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth", "thirty-first"], 1)}
_WARRANT_DAY = re.compile(
    r"\b" + _WEEKDAY + r",?\s+(?:the\s+)?(?:"
    + _MONTH_NAME + r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})"          # Saturday, October 17, 2026
    + r"|(\d{1,2})(?:st|nd|rd|th)\s+day\s+of\s+" + _MONTH_NAME + r",?\s+(\d{4})"   # Monday, the 19th day of October, 2026
    + r"|([a-z]+(?:-[a-z]+)?)\s+day\s+of\s+" + _MONTH_NAME + r",?\s+(\d{4})"       # Saturday, the Seventeenth day of October, 2026
    + r")", re.I)


# A warrant's running head: "OCTOBER 27, 2026 FALL ANNUAL TOWN MEETING WARRANT" or "October 27, 2026 Special Town
# Meeting Warrant". No weekday, but the date sits right against the words "Town Meeting", which a fiscal-year
# date or a "hold until October 13" never does.
_WARRANT_HEAD = re.compile(
    r"\b" + _MONTH_NAME + r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4}),?\s+"
    r"(?:(?:fall|spring|annual|special|adjourned|regular|semi-annual)\s+){0,3}town\s+meeting\b", re.I)

_WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def warrant_date(text: str | None, limit: int = 4000) -> date | None:
    """The meeting day a Town Meeting warrant prints near its top, else None. The weekday printed must be
    the date's own, so a scan error or a typo ("Monday, October 20, 2026") gives nothing rather than a wrong day."""
    if not text:
        return None
    for m in _WARRANT_DAY.finditer(text[:limit]):
        g = m.groups()
        if g[0]:
            dt = _mk(int(g[2]), MONTHS[g[0][:3].lower()], int(g[1]))
        elif g[3]:
            dt = _mk(int(g[5]), MONTHS[g[4][:3].lower()], int(g[3]))
        else:
            day = _ORDINAL.get(g[6].lower())
            dt = _mk(int(g[8]), MONTHS[g[7][:3].lower()], day) if day else None
        if dt and _WEEKDAYS[dt.weekday()] == m.group(0)[:3].lower():
            return dt
    # the running head repeats on every page, so it is read further in than the first page; a date that follows
    # "the", "at", "of" or "since" names an earlier meeting ("approved at the May 5, 2026 Annual Town Meeting")
    heads = list(_WARRANT_HEAD.finditer(text[:max(limit, 20000)]))
    for i, m in enumerate(heads):
        # two meeting dates back to back ("October 19, 2026 Special Town Meeting June 29, 2026 Special Town
        # Meeting") are a list of links to meetings, not this warrant's heading
        if (i and m.start() - heads[i - 1].end() < 60) or (i + 1 < len(heads) and heads[i + 1].start() - m.end() < 60):
            continue
        before = text[max(0, m.start() - 12):m.start()].lower()
        if re.search(r"\b(?:the|at|of|since|by|from|under|minutes)\s*$", before):
            continue
        dt = _mk(int(m.group(3)), MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
        if dt:
            return dt
    return None


def warrant_redate(listing_day: date | None, text: str | None) -> date | None:
    """The meeting day for a warrant whose listing gave a date: the warrant's own printed day when it is later
    than the listing's (a listing often dates a warrant by the day it was posted) and within four months of it.
    None when the listing's date stands."""
    day = warrant_date(text)
    if not day or not listing_day:
        return None
    gap = (day - listing_day).days
    return day if 0 < gap <= 120 else None
