"""Polite HTTP fetching: User-Agent, robots.txt, per-host rate limit, disk cache.

Every network request the crawler makes goes through `PoliteFetcher.get`, so
the politeness rules live in exactly one place:

* identifies itself with a descriptive User-Agent
* obeys robots.txt (RFC 9309 semantics: 4xx on robots.txt = allow all,
  5xx / network failure = disallow the host for this run)
* waits at least `min_interval` seconds between requests to the same host
  (or the robots.txt Crawl-delay, whichever is larger)
* caches every response body under crawler/.cache/ so re-runs are cheap
* never logs in, never sends cookies it was not given, never retries a
  403/429 aggressively
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
import urllib.robotparser
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

log = logging.getLogger(__name__)

USER_AGENT = "351WatchBot/0.1 (+contact: hello@351watch.example)"
ROBOTS_AGENT = "351WatchBot"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
MAX_BYTES = 40 * 1024 * 1024  # skip anything bigger than 40 MB


@dataclass
class Response:
    url: str            # URL requested
    final_url: str      # URL after redirects
    status: int
    content_type: str
    body: bytes
    from_cache: bool = False

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def text(self) -> str:
        # Most municipal pages are UTF-8; fall back gracefully.
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                return self.body.decode(enc)
            except UnicodeDecodeError:
                continue
        return self.body.decode("utf-8", errors="replace")

    @property
    def is_pdf(self) -> bool:
        return "pdf" in self.content_type.lower() or self.body[:5] == b"%PDF-"


class FetchError(Exception):
    pass


def _looks_like_robots(resp: "Response") -> bool:
    """Some servers send robots.txt as text/html. Trust the body, not the header:
    an HTML page (soft 404) is not a robots file, but plain directives are."""
    if "html" not in resp.content_type.lower():
        return True
    head = resp.text.lstrip()[:2000].lower()
    if head.startswith("<"):
        return False
    return any(line.strip().startswith(("user-agent:", "disallow:", "allow:"))
               for line in head.splitlines())


class RobotsDisallowed(FetchError):
    pass


class PoliteFetcher:
    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, min_interval: float = 1.0,
                 timeout: tuple[float, float] = (10, 45), offline: bool = False):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_interval = min_interval
        self.timeout = timeout
        self.offline = offline  # only serve from cache
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8",
        })
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._last_hit: dict[str, float] = {}
        self._host_locks: dict[str, threading.Lock] = {}
        self._origin_locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()
        self.stats = {"network": 0, "cache": 0, "robots_blocked": 0, "errors": 0}

    # ------------------------------------------------------------------ cache
    def _cache_paths(self, url: str) -> tuple[Path, Path]:
        h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
        sub = self.cache_dir / h[:2]
        return sub / f"{h}.body", sub / f"{h}.json"

    def _read_cache(self, url: str, max_age: float | None) -> Response | None:
        body_p, meta_p = self._cache_paths(url)
        if not (body_p.exists() and meta_p.exists()):
            return None
        meta = json.loads(meta_p.read_text())
        if max_age is not None and not self.offline and time.time() - meta["fetched_at"] > max_age:
            return None
        return Response(url=url, final_url=meta["final_url"], status=meta["status"],
                        content_type=meta["content_type"], body=body_p.read_bytes(),
                        from_cache=True)

    def _write_cache(self, resp: Response) -> None:
        body_p, meta_p = self._cache_paths(resp.url)
        body_p.parent.mkdir(parents=True, exist_ok=True)
        body_p.write_bytes(resp.body)
        meta_p.write_text(json.dumps({
            "url": resp.url, "final_url": resp.final_url, "status": resp.status,
            "content_type": resp.content_type, "fetched_at": time.time(),
        }))

    # ----------------------------------------------------------------- robots
    def _lock(self, table: dict[str, threading.Lock], key: str) -> threading.Lock:
        with self._locks_guard:
            return table.setdefault(key, threading.Lock())

    def _robots_for(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        """Return a parser, or None meaning 'host disallowed for this run'."""
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        with self._lock(self._origin_locks, origin):
            if origin not in self._robots:
                self._robots[origin] = self._load_robots(origin)
            return self._robots[origin]

    def _load_robots(self, origin: str) -> urllib.robotparser.RobotFileParser | None:
        parts = urlsplit(origin)
        robots_url = origin + "/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        cached = self._read_cache(robots_url, max_age=24 * 3600)
        try:
            if cached is not None:
                resp = cached
            else:
                r, body = self._get_with_retries(robots_url, parts.netloc, self.min_interval)
                resp = Response(robots_url, r.url, r.status_code,
                                r.headers.get("Content-Type", ""), body)
                if resp.status < 500:
                    self._write_cache(resp)
            if resp.status >= 500:
                log.warning("robots.txt %s -> %s; treating host as disallowed", robots_url, resp.status)
                return None
            if resp.status >= 400 or not _looks_like_robots(resp):
                rp.parse([])  # no usable robots.txt: everything allowed
            else:
                rp.parse(resp.text.splitlines())
        except FetchError as e:
            log.warning("robots.txt %s unreachable (%s); skipping host", robots_url, e)
            return None
        return rp

    def allowed(self, url: str) -> bool:
        rp = self._robots_for(url)
        return rp is not None and rp.can_fetch(ROBOTS_AGENT, url)

    # --------------------------------------------------------------- throttle
    def _throttle(self, host: str, interval: float) -> None:
        """Block until `interval` seconds have passed since the previous request
        to `host` started. Safe across threads: one lock per host."""
        with self._lock(self._host_locks, host):
            last = self._last_hit.get(host)
            if last is not None:
                wait = interval - (time.monotonic() - last)
                if wait > 0:
                    time.sleep(wait)
            self._last_hit[host] = time.monotonic()

    def _get_with_retries(self, url: str, host: str, interval: float, attempts: int = 3,
                          allow_redirects: bool = True):
        """Network GET with a small, bounded retry for transient connection
        failures (resets / TLS timeouts). HTTP error statuses are NOT retried."""
        last_err: Exception | None = None
        for attempt in range(attempts):
            self._throttle(host, interval)
            try:
                r = self.session.get(url, timeout=self.timeout, stream=True,
                                     allow_redirects=allow_redirects)
                self.stats["network"] += 1
                chunks, size = [], 0
                for chunk in r.iter_content(64 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        r.close()
                        raise FetchError(f"too large (> {MAX_BYTES} bytes): {url}")
                    chunks.append(chunk)
                return r, b"".join(chunks)
            except (requests.ConnectionError, requests.Timeout) as e:
                last_err = e
                log.debug("transient error on %s (attempt %d): %s", url, attempt + 1, e)
                time.sleep(2 + 3 * attempt)
            except requests.RequestException as e:
                last_err = e
                break
        self.stats["errors"] += 1
        raise FetchError(f"{url}: {last_err}") from last_err

    def _interval_for(self, url: str) -> float:
        """robots.txt check plus per-host interval; raises if the URL is off limits."""
        rp = self._robots_for(url)
        if rp is None or not rp.can_fetch(ROBOTS_AGENT, url):
            self.stats["robots_blocked"] += 1
            raise RobotsDisallowed(url)
        delay = rp.crawl_delay(ROBOTS_AGENT)
        interval = max(self.min_interval, float(delay) if delay else 0.0)
        # Cap absurd crawl-delays so one host cannot stall the whole run;
        # if a site asks for more than 10s we skip it instead of hammering.
        if interval > 10:
            raise RobotsDisallowed(f"{url} (crawl-delay {interval}s too long for prototype)")
        return interval

    def _get_following_redirects(self, url: str, max_hops: int = 5):
        """GET with redirects followed manually, so robots.txt and the rate limit
        are applied to every hop *before* it is requested."""
        current = url
        for _ in range(max_hops + 1):
            interval = self._interval_for(current)
            r, body = self._get_with_retries(current, urlsplit(current).netloc, interval,
                                             allow_redirects=False)
            location = r.headers.get("Location")
            if r.status_code in (301, 302, 303, 307, 308) and location:
                current = urljoin(current, location)
                continue
            return r, body, current
        raise FetchError(f"too many redirects: {url}")

    def cached_at(self, url: str) -> float | None:
        """When this URL was first stored in the cache (epoch seconds), if ever."""
        meta_p = self._cache_paths(url)[1]
        if not meta_p.exists():
            return None
        return json.loads(meta_p.read_text()).get("fetched_at")

    # -------------------------------------------------------------------- get
    def get(self, url: str, max_age: float | None = None, params: dict | None = None) -> Response:
        """GET a URL politely. `max_age` (seconds) bounds cache freshness;
        None means any cached copy is fine (good for immutable agenda PDFs)."""
        if params:
            url = requests.Request("GET", url, params=params).prepare().url
        cached = self._read_cache(url, max_age)
        if cached is not None:
            self.stats["cache"] += 1
            return cached
        if self.offline:
            raise FetchError(f"offline mode and not cached: {url}")

        r, body, final_url = self._get_following_redirects(url)
        resp = Response(url, final_url, r.status_code, r.headers.get("Content-Type", ""), body)
        if r.status_code in (200, 404, 410):
            self._write_cache(resp)  # cache successes and definitive misses
        if not resp.ok:
            self.stats["errors"] += 1
        log.debug("GET %s -> %s (%d bytes)", url, r.status_code, len(body))
        return resp
