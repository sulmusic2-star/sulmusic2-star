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

## States under test (gated)

- A `data/towns_<st>.json` with `"gated": true` (Michigan and Virginia since Oct 12, 2026) is **not** part of the production run: `current.load_towns` skips it, so `ops/daily.sh` → `watch351.daily` (no `--states`) never crawls it and `data/hits_current.json` never lists it.
- It is crawled only when named explicitly, into a separate output directory: `python3 -m watch351.daily --states MI,VA --output-dir ../data/test --hits-name hits_mi_va.json`. Naming a gated state without `--output-dir` exits with an error before any request. Test output (index, ledger, health, run reports, hits file in this contract's shape) lives in `data/test/`.
- To promote a state: remove `"gated"` from its towns file (after site support for its board names exists).
- Board names outside New England: `boards.classify_board(name, state)` adds per-state aliases (MI township board / board of trustees / city commission → `select_board`, planning commission → `planning_board`, ZBA → `zoning_board_of_appeals`; VA board of supervisors → `select_board`, BZA → `zoning_board_of_appeals`). Without a state the classifier is unchanged.
- Keywords: `keywords.find_hits(text, state=...)` adds that state's patterns (`STATE_TOPICS`: PA 233 / CREO, special land use, 2232 review, siting agreements, wind / WECS, transmission and substations, rezoning to industrial, comprehensive-plan amendments), mapped onto the existing topic keys, plus false-positive rules for the shared topics (`STATE_FALSE_POSITIVE`: use tables and tables of contents, invoices and permit logs, non-zoning ordinance amendments, non-land-use moratoria, event flyers, rooftop / solar-powered equipment) from the hand check in `research_notes/Expansion/test_mi_va.md`. Without a state (MA, NY, RI) matching is unchanged; `experiments/keyword_regression.py` proves it on the cached MA/NY/RI documents.
- Michigan county planning commission rows carry `"attribute_townships": true`: a hit is filed under the township its agenda item names (`town`), with the county body kept as `board` ("Monroe County Planning Commission"); a county agenda's item list that names several townships gives one hit per named township (`attribution.split_items`), see `watch351/attribution.py`.
- Michigan township rows carry `coverage`: `direct` (we read the township's own agendas), `via_county` (we do not, but we read its county planning commission) or `none`, with `coverage_county_body` ("Calhoun County Planning Commission") and, for `via_county`, `coverage_note`, the line a township page shows ("Zoning changes reach us through the Calhoun County Planning Commission; project permits may not."). Derived by `attribution.coverage_modes`; `experiments/mi_va_test.py annotate --state MI` rewrites them without any request.
- Sections (MI / VA): `find_hits` classifies each page of a document (agenda, minutes, ordinance text, attachment, or noise: newsletter, invoice / ledger, permit log, assessor card, audit, case-law digest, resume, use table) and matches each page on its own. Noise pages are skipped; on attachment pages a match needs action or regulatory words or a project name nearby and must not be one entry in a list of unrelated topics. Gas-fired power plants being sited map to `clean_energy_siting` until the site supports a new topic.
- `adapters/agenda_page.py` is the general agenda-page reader (WordPress, Revize, CivicPlus document pages, Municode Meetings, plain pages); `watch351/discover_sites.py` finds its listings and records closed vendors (Granicus, iQM2, PrimeGov, iCompass/Diligent, BoardDocs, Destiny) as `vendor_blocked` with the platform name.

## Crawler rules (non-negotiable)

Identify as AgendaAheadBot (robots.txt rules for the former name 351WatchBot are also obeyed); obey robots.txt on every host and redirect hop; ≤1 request/second/host; no logins; never solve or bypass bot challenges; respect crawl-delay (skip hosts asking >10 s; listing pages, a few requests per host per day, may wait up to 20 s: `fetch.LISTING_CRAWL_DELAY_CAP`).
