"""Plain data types shared by adapters and the crawl pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Window:
    """Meeting-date window to crawl: [start, end] inclusive."""
    start: date
    end: date

    def __contains__(self, d: date | None) -> bool:
        return d is not None and self.start <= d <= self.end


@dataclass
class AgendaDoc:
    """One agenda (or warrant) document an adapter found on a listing page."""
    town: str
    board: str             # board name as the town labels it ("Select Board")
    board_key: str         # normalized key ("select_board")
    meeting_date: date | None
    title: str
    url: str               # the agenda PDF / page to fetch
    listing_url: str       # human-browsable page where the agenda is listed
    resolve_pdf: bool = False   # url is an HTML landing page that links to the real PDF
    extra: dict = field(default_factory=dict)
