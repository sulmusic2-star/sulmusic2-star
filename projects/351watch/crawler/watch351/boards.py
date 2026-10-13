"""Normalize the many ways towns name the same board (Massachusetts first, plus Northeast
names such as CT zoning commissions, NY town boards and NJ boards of adjustment)."""

from __future__ import annotations

import re

# Order matters only for display. Each key has an include pattern and an
# exclude pattern (subcommittees, regional bodies, retired categories...).
BOARD_PATTERNS: dict[str, tuple[str, str]] = {
    "planning_board": (
        r"\bplanning board\b|community development board|planning (and|&) zoning (commission|board)|"
        r"\bplanning commission\b|^zoning commission\b|land use (board|commission)|development review board",
        r"sub-?committee|committee|regional|working group|housing|joint|comprehensive plan|steering|advisory",
    ),
    "zoning_board_of_appeals": (
        r"zoning board|board of appeals|\bZBA\b|zoning appeals|board of (zoning )?adjustment|zoning hearing board",
        r"sub-?committee|committee|building code",
    ),
    "conservation_commission": (
        r"conservation commission|^conservation$|\bconcom\b|inland wetlands|"
        r"wetlands? (and watercourses )?(commission|agency|board)",
        r"sub-?committee|committee|district",
    ),
    "select_board": (
        r"select ?board|board of selectmen|selectmen|^(city|town|township|borough|village|common) council\b|"
        r"^town board\b|^township committee\b|^board of (township )?supervisors\b|"
        r"^board of (mayor and )?alder(men|s)\b",
        r"committee(?<!township committee)|sub-?committee|joint|20\d\d to 20\d\d|housing|ad hoc|rules",
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

# State-specific names, consulted first when classify_board() is given that state; a name
# they do not match falls through to BOARD_PATTERNS. Calls without a state (every
# Massachusetts, NY and RI caller) never see these, so those classifications are unchanged.
STATE_BOARD_PATTERNS: dict[str, dict[str, tuple[str, str]]] = {
    # Michigan: township boards (often "Board of Trustees"), city/village councils and city
    # commissions, county boards of commissioners; township, city and county planning
    # commissions (MZEA); ZBAs. "Board of Review" is the property-tax appeals board.
    "MI": {
        "select_board": (
            r"^(?:charter\s+)?township board\b|^(?:township\s+)?board of trustees\b|"
            r"^(?:regular\s+|special\s+)?township board|^city commission\b|^(?:city|village) council\b|"
            r"^(?:county\s+)?board of (?:county\s+)?commissioners\b",
            r"committee|sub-?committee|joint|school|library|housing|brownfield|downtown|ad hoc",
        ),
        "planning_board": (
            r"planning commission|planning board|planning\s*(?:&|and)\s*zoning commission",
            r"regional|district|sub-?committee|committee|advisory|emergency|historic|economic|steering",
        ),
        "zoning_board_of_appeals": (
            r"zoning board of appeals|\bZBA\b|board of zoning appeals|zoning appeals",
            r"building|construction|code|sub-?committee|review",
        ),
    },
    # Virginia: county boards of supervisors, town/city councils, planning commissions
    # (incl. joint county-town ones, e.g. "Joint Appomattox Planning Commission"), BZAs.
    "VA": {
        "select_board": (
            r"board of supervisors|^(?:town|city) council\b",
            r"committee|sub-?committee|school|electoral|social services",
        ),
        "planning_board": (
            r"planning commission",
            r"district|regional|sub-?committee|committee|emergency|advisory",
        ),
        "zoning_board_of_appeals": (
            r"board of zoning appeals|\bBZA\b|zoning appeals|\bZBA\b|^board of appeals\b",
            r"building|construction|code|fire|sub-?committee",
        ),
    },
    # New York (Wave 1 discovery only: production NY callers pass no state): town boards, village
    # boards of trustees, city / common councils; town, village and city planning boards; ZBAs.
    "NY": {
        "select_board": (
            r"^town board\b|^(?:regular\s+|special\s+)?town board|^(?:village\s+)?board of trustees\b|"
            r"^village board\b|^(?:city|common) council\b|^town council\b",
            r"committee|sub-?committee|joint|school|library|housing|ad hoc|ethics|assessment|review",
        ),
        "planning_board": (
            r"planning board|planning commission|planning\s*(?:&|and)\s*zoning board",
            r"county|regional|sub-?committee|committee|advisory|historic|economic|steering|comprehensive",
        ),
        "zoning_board_of_appeals": (
            r"zoning board of appeals|\bZBA\b|^board of (?:zoning )?appeals\b|zoning appeals",
            r"building|construction|code|sub-?committee|assessment",
        ),
    },
}


def classify_board(name: str, state: str | None = None) -> str | None:
    """Return the board key for a category/board name, or None if it is not
    one of the boards 351 Watch tracks. `state` adds that state's aliases
    (STATE_BOARD_PATTERNS) ahead of the shared patterns."""
    name = " ".join(name.split())
    if _INACTIVE.search(name):
        return None
    for key, (include, exclude) in STATE_BOARD_PATTERNS.get((state or "").upper(), {}).items():
        if re.search(include, name, re.I) and not re.search(exclude, name, re.I):
            return key
    for key, (include, exclude) in BOARD_PATTERNS.items():
        if re.search(include, name, re.I) and not re.search(exclude, name, re.I):
            return key
    return None
