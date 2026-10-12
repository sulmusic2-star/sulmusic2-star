# 351 Watch — architecture and shared contracts

Read this before changing anything. Several workstreams build in parallel; these contracts keep them compatible.

## Pieces

| Piece | Path | Owner |
|---|---|---|
| Crawler package (Python) | `crawler/watch351/` | Daily engine workstream owns `crawl.py`, `fetch.py`, `state.py`, `daily.py`, `keywords.py`. Others add **new files only** (adapters, sources) and may append one registration line to `adapters/__init__.py`. |
| Town configs | `data/towns_ma_all.json`, `data/towns_ny.json`, `data/towns_ri.json`, … | One file per state, same row shape as `towns_ma_all.json` plus a `"state"` field. |
| Incremental crawl state | `data/state/` | Daily engine. Committed to git so a fresh container can resume without re-downloading. |
| Current alert data | `data/hits_current.json` | Written by the daily engine; read by the site build and the web app. Schema below. |
| Second sources | `crawler/watch351/sources/` (e.g. `massdep.py`), outputs in `data/sources/` | Source workstreams. |
| Searchable document text | `data/search/` (written by `crawler/watch351/fulltext.py`) | Search workstream. Contract below. |
| Search index (Pagefind) + `/search` script | `search/build-index.mjs` → `/pagefind/` at deploy time; `site/search.js` | Search workstream. The `/search` page markup comes from `build.py`. |
| Site generator | `build.py` → `site/` | Web app workstream. |
| Web app API (Vercel functions) | `site/api/` | Web app workstream. |
| Daily runbook | `ops/daily.sh` | Daily engine. |

## `data/hits_current.json` (the contract)

```json
{
  "generated": "2026-10-11T11:05:00+00:00",
  "window": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "states": ["MA", "NY"],
  "towns_monitored": {"MA": 240, "NY": 41},
  "hits": [
    {
      "id": "12-hex sha1 of source_url + '|' + snippet",
      "state": "MA",
      "town": "Fitchburg",
      "county": "Worcester",
      "board": "City Council",
      "board_key": "select_board",
      "meeting_date": "2026-10-06",
      "topics": ["battery_storage", "moratorium"],
      "snippet": "≤240 chars",
      "source_url": "https://…/Agenda/_10062026-5418",
      "listing_url": "https://…",
      "document_title": "…",
      "text_source": "pdf|ocr|html|docx",
      "first_seen": "2026-10-10T15:11:10+00:00",
      "days_before_meeting": 3.2,
      "source": "agenda|massdep_wetlands|…"
    }
  ]
}
```

- `meeting_date` may be `null` (e.g., undated town-meeting warrants); then `days_before_meeting` is omitted.
- `board_key` ∈ `planning_board, zoning_board_of_appeals, conservation_commission, select_board, town_meeting` (outside MA, map local names onto these: NY Town Board → `select_board`, NJ Board of Adjustment → `zoning_board_of_appeals`, CT Zoning Commission → `planning_board`, CT Inland Wetlands → `conservation_commission`).
- `topics` keys: `battery_storage, solar, data_center, moratorium, clean_energy_siting, 40b_comprehensive_permit, wireless_telecom, zoning_amendment` (+ `wetlands_filing` for MassDEP-sourced items). New topics must be added here first.
- Window: meetings from 120 days back to 120 days ahead; older items move to `data/state/hits_archive/YYYY-MM.jsonl`.
- Town slug: lowercase, spaces → `-`, apostrophes dropped; URL path `/{state}/{slug}` e.g. `/ma/great-barrington`.

## `data/search/` (full-text search contract)

The crawler cache (`crawler/.cache`, raw bodies) is lost with the container and `data/state/docs/` keeps only metadata and hit snippets, so the text that search needs is committed here.

- `data/search/<ST>/<YYYY-MM>.jsonl` (meeting month; `undated.jsonl` without a date): one row per agenda document whose text was read (index status `ok`). Keys in this order:
  `id` (sha1(url)[:12]), `url` (the document's key in `data/state/docs`), `source_url` (only when the text came from another URL, e.g. a landing page's PDF), `listing_url`, `state`, `town`, `county`, `board`, `board_key`, `meeting_date` (or null), `first_seen`, `title`, `text_source`, `topics` (sorted topics of its hits), `chars` (full normalized length), `text`.
- `text`: whitespace collapsed, control characters dropped, leader-dot runs shortened, cut at 20,000 characters (`TEXT_CAP`; a median agenda is about 2,000), then ` … ` and any hit snippets that lie beyond the cut, so every matched passage stays searchable.
- Append-only: the daily engine (`DailyRun.process_doc` → `FullText.add`, `FullText.save` once per run) appends rows for new documents at the end of their shard; a row is rewritten in place only when its document is processed again and something changed (re-match after a keyword-rule change, OCR replacing a scan). Rows are not pruned with the document index: search covers every document read.
- Rebuild missing rows from the local cache, never the network: `python3 -m watch351.fulltext backfill` (`ops/daily.sh` runs it after each crawl; it does nothing when every row exists or the cache is empty). `python3 -m watch351.fulltext stats` prints sizes.
- Deploy: `site/vercel-build.sh` runs `search/build-index.mjs` (Pagefind, pinned by `search/package-lock.json`) over `data/search` into `/pagefind/`: one record per distinct document (identical text in one town is indexed once), filters `state` (`MA`), `town` (`MA:Carver`), `board` (board_key), `topic`, `date` (YYYY-MM-DD), sort key `date`, plus `/pagefind/words.txt` (spelling vocabulary). The browser fetches only the index chunks and fragments a query needs; there is no server work per query. The CSP allows `'wasm-unsafe-eval'` for Pagefind's WebAssembly.

## `/search` page contract (`build.py` writes the markup, `site/search.js` runs it)

- `<form id="search-form" action="/search" method="get">` with `<input name="q" id="search-q">`; optional `<select name="state">` (values `MA`…), `<select name="topic">` (topic keys), `<select name="board">` (board_keys), `<select name="town">` (`MA:Carver`), `<input type="checkbox" name="upcoming" value="1">` (upcoming meetings first, soonest first), `<select name="sort">` (`date` = newest meeting first; empty = best match). A select rendered with only an empty "Any" option is filled from the index.
- `<p id="search-status" aria-live="polite"></p>` and `<ol id="search-results"></ol>`; load `/search.js` (classic script, `defer`).
- Each result: `<li class="result" data-topics="solar,moratorium">` with `<a class="result-title" href=SOURCE>`, `<p class="result-meta">` (town, state · board · date, "(upcoming)" when today or later), `<p class="result-snippet">` (matches in `<mark>`) and `<a class="result-town" href="/ma/carver">`. A `<button class="search-more">` (10 more results) is inserted after the list.

## Agenda version archive

- `data/archive/<ST>/<YYYY-MM>.jsonl`: when a document's text changes after we first read it (an amended agenda, OCR replacing a scan), the earlier text is appended here with `first_seen`, `superseded_at` and `text_sha256` before `data/search` is rewritten. Append-only; never pruned. It is the dated record of what each agenda said before its meeting.

## Watchlists (web app; no email, no passwords)

- A watchlist is created on `/watch`: chosen towns (`"MA:Amherst"`), topics, optional name, optional Slack, Discord, Teams (Workflows: `*.logic.azure.com`, `*.api.powerplatform.com`) or generic webhook URL.
- Stored as a private Vercel Blob `watchlists/<id>.json`. Two keys, both 24+ random URL-safe chars: `id` is the private key that can edit or delete; `feed_id` is a read-only key used in feed, calendar and share links (`feeds/<feed_id>.json` points back to the watchlist). `GET /api/watchlists?id=<feed_id>` returns a read-only view (`readonly: true`, no id, no webhook); PATCH and DELETE need the private key. Feeds accept either key so older links keep working.
- Delivery: web view `/w/<id>`, RSS `/api/feed?id=…&format=rss`, JSON, and iCalendar (`format=ics`, upcoming meetings with matched items). Webhooks are posted by a Vercel Cron function (`/api/cron/dispatch`, `CRON_SECRET`) once a day after the data refresh, sending only items first seen since the last dispatch.
- Plans: free founding beta. Stripe Checkout code exists but is disabled unless `STRIPE_SECRET_KEY` and price env vars are set.

## Deploys

- Every deployment is built from git at one commit: the project's build command pipes `site/vercel-build.sh` from raw.githubusercontent.com at `<sha>` with `SITE_REF=<sha>`, which downloads that commit's tarball and writes a Build Output API v3 bundle (`.vercel/output`: static pages and data, the `/pagefind/` search index built from `data/search`, one Node function per `site/api/**/*.js`, routing headers, clean URLs and the daily cron). The deployment upload itself is a one-line `package.json`. Steps: `OPERATIONS.md`.
- Only the coordinator deploys to production.

## Crawler rules (non-negotiable)

Identify as 351WatchBot; obey robots.txt on every host and redirect hop; ≤1 request/second/host; no logins; never solve or bypass bot challenges; respect crawl-delay (skip hosts asking >10 s).
