"""Discovery: figure out each town's agenda platform and listing URLs, and
record the result (including failures and why) in data/towns.json.

Hand-curated facts in towns.json (website, platform overrides, generic
listing URLs, `automated: false` + `reason`) are preserved; discovery only
fills in what it can determine mechanically.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from .adapters import REGISTRY
from .boards import BOARD_PATTERNS
from .fetch import FetchError, PoliteFetcher

log = logging.getLogger(__name__)

_CF_MARKERS = ("challenges.cloudflare.com", "Attention Required! | Cloudflare", "cf-chl")


def fingerprint(fetcher: PoliteFetcher, website: str) -> dict:
    """Guess the agenda platform from the homepage (and /AgendaCenter)."""
    try:
        home = fetcher.get(website.rstrip("/") + "/", max_age=24 * 3600)
    except FetchError as e:
        return {"platform": None, "reason": f"homepage unreachable: {e}"}
    html = home.text
    if home.status == 403 and any(m in html for m in _CF_MARKERS):
        return {"platform": None, "reason": "Cloudflare bot challenge on every page (HTTP 403); not bypassed"}
    if not home.ok:
        return {"platform": None, "reason": f"homepage HTTP {home.status}"}
    info: dict = {"final_url": home.final_url}
    m = re.search(r"https?://([a-z0-9-]+)\.portal\.civicclerk\.com", html, re.I)
    if m:
        info.update(platform="civicclerk", tenant=m.group(1).lower())
    elif "/AgendaCenter" in html or "CivicPlus" in html:
        info["platform"] = "civicplus"
    else:
        info["platform"] = "generic"
    tm = re.search(r'href="([^"]+)"[^>]*>\s*(?:Annual |Special |Fall )?Town Meeting\s*<', html, re.I)
    if tm:
        info["town_meeting_page"] = urljoin(home.final_url, tm.group(1))
    return info


def discover_town(fetcher: PoliteFetcher, cfg: dict) -> dict:
    cfg = dict(cfg)
    if cfg.get("automated") is False and cfg.get("reason"):
        return cfg  # known-unautomatable; keep the curated explanation
    fp = fingerprint(fetcher, cfg["website"])
    if fp.get("platform") is None:
        cfg.update(automated=False, reason=fp["reason"], listings=[])
        return cfg
    cfg.setdefault("platform", fp["platform"])
    if "tenant" in fp:
        cfg.setdefault("tenant", fp["tenant"])
    if fp.get("town_meeting_page"):
        cfg.setdefault("town_meeting_page", fp["town_meeting_page"])
    adapter = REGISTRY[cfg["platform"]](fetcher)
    try:
        cfg["listings"] = adapter.discover(cfg)
    except (FetchError, RuntimeError) as e:
        cfg.update(automated=False, reason=f"discovery failed: {e}", listings=cfg.get("listings", []))
        return cfg
    keys = {l["board_key"] for l in cfg["listings"]}
    cfg["boards_found"] = sorted(keys)
    cfg["boards_missing"] = [k for k in BOARD_PATTERNS if k not in keys]
    if cfg["listings"]:
        cfg["automated"] = cfg.get("enabled", True)
        if cfg["automated"]:
            cfg.pop("reason", None)
    else:
        cfg.update(automated=False, reason=cfg.get("reason") or
                   f"{cfg['platform']} site found but no agenda listings for tracked boards")
    cfg["discovered_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return cfg
