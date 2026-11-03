"""Polite HTTP fetching: User-Agent, robots.txt, per-host rate limit, disk cache.

Every network request the crawler makes goes through `PoliteFetcher.get`, so
the politeness rules live in exactly one place:

* identifies itself with a descriptive User-Agent
* obeys robots.txt (RFC 9309 semantics: 4xx on robots.txt = allow all,
  5xx / network failure = disallow the host for this run)
* waits at least `min_interval` seconds between requests to the same host
  (or the robots.txt Crawl-delay, whichever is larger); a host asking for more than
  CRAWL_DELAY_CAP (20 s; LISTING_CRAWL_DELAY_CAP for listing pages, the same value) is skipped
* a host asking for more than SLOW_HOST_DELAY (10 s) gets at most SLOW_HOST_DOC_BUDGET (20)
  document downloads per run, so one slow host cannot hold a worker for hours
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
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

from .botauth import signer_from_env

log = logging.getLogger(__name__)

USER_AGENT = "AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)"
ROBOTS_AGENT = "AgendaAheadBot"
# Earlier name of the same crawler; robots.txt rules written for it are still obeyed.
FORMER_ROBOTS_AGENTS = ("351WatchBot",)
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
# Hosts that rate-limit below our default 1 request/second (seconds between requests).
HOST_MIN_INTERVAL = {"opengov.sos.ri.gov": 2.5}
MAX_BYTES = 40 * 1024 * 1024  # skip anything bigger than 40 MB
# Longest robots.txt Crawl-delay we honour (seconds). A host asking for more is skipped. Raised from 10 s
# to 20 s on 2026-11-03 so that Huntington (15 s), Cicero (20 s) and Pound Ridge (15 s) can be read: a few
# files a day at one request every 15 to 20 s is harmless. Listing pages keep their own constant (the same
# value today; it was the higher of the two).
CRAWL_DELAY_CAP = 20.0
LISTING_CRAWL_DELAY_CAP = 20.0
LISTING_PURPOSES = frozenset({"listing"})
# A host whose Crawl-delay is above SLOW_HOST_DELAY is slow: one PoliteFetcher (one run) downloads at most
# SLOW_HOST_DOC_BUDGET documents from it (network requests made with purpose "document"; cached copies are
# free). The rest wait for the next run: daily.py defers them without recording an error. At 20 s a request,
# 20 documents are about seven minutes on one worker; a backlog of 100 would otherwise take half an hour.
SLOW_HOST_DELAY = 10.0
SLOW_HOST_DOC_BUDGET = 20


@dataclass
class Response:
    url: str            # URL requested
    final_url: str      # URL after redirects
    status: int
    content_type: str
    body: bytes
    from_cache: bool = False
    last_modified: str | None = None   # the server's Last-Modified header, when it sent one

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


class SlowHostBudget(FetchError):
    """This run's document budget for a slow host (Crawl-delay above SLOW_HOST_DELAY) is spent."""


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
        self._stats_lock = threading.Lock()
        self._ctx = threading.local()
        self.stats = {"network": 0, "cache": 0, "robots_blocked": 0, "errors": 0}
        # network document fetches per slow host this run (SLOW_HOST_DOC_BUDGET)
        self.slow_host_docs: Counter = Counter()
        # Network requests and bytes by purpose ("robots", "listing", "document", ...),
        # set per thread with `with fetcher.purpose("listing"): ...`.
        self.requests_by_purpose: Counter = Counter()
        self.bytes_by_purpose: Counter = Counter()
        self.request_log: list[tuple[str, str, int]] = []   # (purpose, url, status)

    # ---------------------------------------------------------------- accounting
    @contextmanager
    def purpose(self, kind: str):
        """Label the network requests made by this thread inside the block."""
        prev = getattr(self._ctx, "kind", None)
        self._ctx.kind = kind
        try:
            yield
        finally:
            self._ctx.kind = prev

    def _count(self, key: str, n: int = 1) -> None:
        with self._stats_lock:
            self.stats[key] += n

    def _record(self, url: str, status: int, size: int) -> None:
        kind = "robots" if url.endswith("/robots.txt") else (getattr(self._ctx, "kind", None) or "other")
        with self._stats_lock:
            self.stats["network"] += 1
            self.requests_by_purpose[kind] += 1
            self.bytes_by_purpose[kind] += size
            self.request_log.append((kind, url, status))

    # ------------------------------------------------------------------ cache
    def _cache_paths(self, url: str) -> tuple[Path, Path]:
        h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
        sub = self.cache_dir / h[:2]
        return sub / f"{h}.body", sub / f"{h}.json"

    def _read_cache(self, url: str, max_age: float | None) -> Response | None:
        body_p, meta_p = self._cache_paths(url)
        if not (body_p.exists() and meta_p.exists()):
            return None
        try:
            meta = json.loads(meta_p.read_text())
        except ValueError:
            # a meta file another process is writing this instant (two runs sharing the cache), or a
            # truncated one: treat the entry as not cached rather than crash the run
            return None
        if max_age is not None and not self.offline and time.time() - meta["fetched_at"] > max_age:
            return None
        return Response(url=url, final_url=meta["final_url"], status=meta["status"],
                        content_type=meta["content_type"], body=body_p.read_bytes(),
                        from_cache=True, last_modified=meta.get("last_modified"))

    def _write_cache(self, resp: Response) -> None:
        body_p, meta_p = self._cache_paths(resp.url)
        body_p.parent.mkdir(parents=True, exist_ok=True)
        body_p.write_bytes(resp.body)
        meta_p.write_text(json.dumps({
            "url": resp.url, "final_url": resp.final_url, "status": resp.status,
            "content_type": resp.content_type, "fetched_at": time.time(),
            **({"last_modified": resp.last_modified} if resp.last_modified else {}),
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
        return rp is not None and all(rp.can_fetch(a, url) for a in (ROBOTS_AGENT, *FORMER_ROBOTS_AGENTS))

    def host_delay(self, url: str) -> float:
        """The robots.txt Crawl-delay for the URL's host, in seconds (0 when there is none, or when
        robots.txt could not be read)."""
        rp = self._robots_for(url)
        if rp is None:
            return 0.0
        delays = [float(d) for d in (rp.crawl_delay(a) for a in (ROBOTS_AGENT, *FORMER_ROBOTS_AGENTS)) if d]
        return max(delays) if delays else 0.0

    def is_slow_host(self, url: str) -> bool:
        return self.host_delay(url) > SLOW_HOST_DELAY

    def slow_host_budget_left(self, url: str) -> int | None:
        """Documents this run may still download from the URL's host: None for an ordinary host, else
        SLOW_HOST_DOC_BUDGET minus the documents already fetched from it (0 when the budget is spent)."""
        if not self.is_slow_host(url):
            return None
        with self._stats_lock:
            return max(0, SLOW_HOST_DOC_BUDGET - self.slow_host_docs[urlsplit(url).netloc])

    def _charge_slow_host(self, url: str) -> None:
        """Count one network document fetch against a slow host's budget; raise when it is spent."""
        if getattr(self._ctx, "kind", None) != "document":
            return
        delay = self.host_delay(url)
        if delay <= SLOW_HOST_DELAY:
            return
        host = urlsplit(url).netloc
        with self._stats_lock:
            if self.slow_host_docs[host] >= SLOW_HOST_DOC_BUDGET:
                raise SlowHostBudget(f"{url}: {SLOW_HOST_DOC_BUDGET} documents already fetched from {host} this run "
                                     f"(Crawl-delay {delay:g} s); the rest wait for the next run")
            self.slow_host_docs[host] += 1

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
                # Web Bot Auth headers, signed per attempt (they expire after a minute).
                signer = signer_from_env()
                r = self.session.get(url, timeout=self.timeout, stream=True,
                                     allow_redirects=allow_redirects,
                                     headers=signer.headers(url) if signer else None)
                chunks, size = [], 0
                declared = r.headers.get("Content-Length", "")
                if declared.isdigit() and int(declared) > MAX_BYTES:
                    r.close()  # don't stream 40 MB of a packet we will discard anyway
                    self._record(url, r.status_code, 0)
                    raise FetchError(f"too large ({declared} > {MAX_BYTES} bytes): {url}")
                try:
                    for chunk in r.iter_content(64 * 1024):
                        size += len(chunk)
                        if size > MAX_BYTES:
                            r.close()
                            raise FetchError(f"too large (> {MAX_BYTES} bytes): {url}")
                        chunks.append(chunk)
                finally:
                    self._record(url, r.status_code, size)
                return r, b"".join(chunks)
            except (requests.ConnectionError, requests.Timeout) as e:
                last_err = e
                log.debug("transient error on %s (attempt %d): %s", url, attempt + 1, e)
                time.sleep(2 + 3 * attempt)
            except requests.RequestException as e:
                last_err = e
                break
        self._count("errors")
        raise FetchError(f"{url}: {last_err}") from last_err

    def _interval_for(self, url: str) -> float:
        """robots.txt check plus per-host interval; raises if the URL is off limits."""
        rp = self._robots_for(url)
        agents = (ROBOTS_AGENT, *FORMER_ROBOTS_AGENTS)
        if rp is None or not all(rp.can_fetch(a, url) for a in agents):
            self._count("robots_blocked")
            raise RobotsDisallowed(url)
        delays = [float(d) for d in (rp.crawl_delay(a) for a in agents) if d]
        delay = max(delays) if delays else None
        interval = max(self.min_interval, HOST_MIN_INTERVAL.get(urlsplit(url).netloc, 0.0),
                       float(delay) if delay else 0.0)
        # A site asking for more than the cap is skipped instead of hammered (listing pages have their own
        # cap). Hosts between SLOW_HOST_DELAY and the cap are honoured as asked, with a per-run document
        # budget (_charge_slow_host) so one of them cannot stall a worker.
        cap = LISTING_CRAWL_DELAY_CAP if getattr(self._ctx, "kind", None) in LISTING_PURPOSES else CRAWL_DELAY_CAP
        if interval > cap:
            raise RobotsDisallowed(f"{url} (crawl-delay {interval}s above the {cap:g} s cap)")
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

    def is_cached(self, url: str) -> bool:
        """True if a body for this URL is in the disk cache (any age)."""
        body_p, meta_p = self._cache_paths(url)
        return body_p.exists() and meta_p.exists()

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
            self._count("cache")
            return cached
        if self.offline:
            raise FetchError(f"offline mode and not cached: {url}")
        self._charge_slow_host(url)   # a document from a slow host: within this run's budget, or SlowHostBudget

        r, body, final_url = self._get_following_redirects(url)
        resp = Response(url, final_url, r.status_code, r.headers.get("Content-Type", ""), body,
                        last_modified=r.headers.get("Last-Modified"))
        if r.status_code in (200, 404, 410):
            self._write_cache(resp)  # cache successes and definitive misses
        if not resp.ok:
            self._count("errors")
        log.debug("GET %s -> %s (%d bytes)", url, r.status_code, len(body))
        return resp
