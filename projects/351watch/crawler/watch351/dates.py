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
    return None
