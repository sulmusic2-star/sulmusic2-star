"""Normalize the many ways Massachusetts towns name the same board."""

from __future__ import annotations

import re

# Order matters only for display. Each key has an include pattern and an
# exclude pattern (subcommittees, regional bodies, retired categories...).
BOARD_PATTERNS: dict[str, tuple[str, str]] = {
    "planning_board": (
        r"\bplanning board\b|community development board",
        r"sub-?committee|committee|regional|working group|housing|joint",
    ),
    "zoning_board_of_appeals": (
        r"zoning board|board of appeals|\bZBA\b|zoning appeals",
        r"sub-?committee|committee",
    ),
    "conservation_commission": (
        r"conservation commission|^conservation$|\bconcom\b",
        r"sub-?committee|committee|district",
    ),
    "select_board": (
        r"select ?board|board of selectmen|selectmen|^(city|town) council\b",
        r"committee|sub-?committee|joint|20\d\d to 20\d\d|housing|ad hoc|rules",
    ),
    "town_meeting": (
        r"town meeting|warrant",
        r"advisory|handbook|access to|committee|inactive",
    ),
}

BOARD_LABELS = {
    "planning_board": "Planning Board",
    "zoning_board_of_appeals": "Zoning Board of Appeals",
    "conservation_commission": "Conservation Commission",
    "select_board": "Select Board / Council",
    "town_meeting": "Town Meeting",
}

_INACTIVE = re.compile(r"zzz|inactive|archive", re.I)


def classify_board(name: str) -> str | None:
    """Return the board key for a category/board name, or None if it is not
    one of the boards 351 Watch tracks."""
    name = " ".join(name.split())
    if _INACTIVE.search(name):
        return None
    for key, (include, exclude) in BOARD_PATTERNS.items():
        if re.search(include, name, re.I) and not re.search(exclude, name, re.I):
            return key
    return None
