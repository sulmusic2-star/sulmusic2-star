"""Adapter interface. One adapter per agenda-hosting platform.

An adapter knows two things about its platform:

* `discover(cfg)`  - given a town config with at least `website`, find the
  agenda listing(s) for the boards we track and return them as a list of
  listing dicts ({board, board_key, url, ...platform-specific fields}).
* `list_agendas(cfg, window)` - return AgendaDoc objects for meetings whose
  date falls in `window`, using the listings stored in the town config.

Fetching the agenda documents themselves, text extraction and keyword
matching are platform-independent and live in crawl.py.
"""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..fetch import PoliteFetcher, Response
from ..models import AgendaDoc, Window

LISTING_MAX_AGE = 6 * 3600  # re-fetch listing pages after 6h; documents are cached indefinitely


class Adapter:
    platform = "base"

    def __init__(self, fetcher: PoliteFetcher):
        self.fetcher = fetcher

    # -- helpers ---------------------------------------------------------
    def get_listing(self, url: str, **kw) -> Response:
        return self.fetcher.get(url, max_age=LISTING_MAX_AGE, **kw)

    @staticmethod
    def soup(resp: Response) -> BeautifulSoup:
        return BeautifulSoup(resp.text, "lxml")

    @staticmethod
    def abs_url(base: str, href: str) -> str:
        return urljoin(base, href.strip())

    # -- interface -------------------------------------------------------
    def discover(self, cfg: dict) -> list[dict]:
        raise NotImplementedError

    def list_agendas(self, cfg: dict, window: Window) -> list[AgendaDoc]:
        raise NotImplementedError
