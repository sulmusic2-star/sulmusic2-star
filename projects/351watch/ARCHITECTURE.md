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

## Watchlists (web app; no email, no passwords)

- A watchlist is created on `/watch`: chosen towns (`"MA:Amherst"`), topics, optional name, optional Slack/Teams/generic webhook URL.
- Stored as a private Vercel Blob `watchlists/<id>.json`; `<id>` is 24+ random URL-safe chars and is the credential (like a Google Alerts RSS link).
- Delivery: web view `/w/<id>`, RSS `/api/feed?id=…&format=rss`, JSON, and iCalendar (`format=ics`, upcoming meetings with matched items). Webhooks are posted by a Vercel Cron function (`/api/cron/dispatch`, `CRON_SECRET`) once a day after the data refresh, sending only items first seen since the last dispatch.
- Plans: free founding beta. Stripe Checkout code exists but is disabled unless `STRIPE_SECRET_KEY` and price env vars are set.

## Deploys

- Every deployment is built from git at one commit: the project's build command pipes `site/vercel-build.sh` from raw.githubusercontent.com at `<sha>` with `SITE_REF=<sha>`, which downloads that commit's tarball and writes a Build Output API v3 bundle (`.vercel/output`: static pages and data, one Node function per `site/api/**/*.js`, routing headers, clean URLs and the daily cron). The deployment upload itself is a one-line `package.json`. Steps: `OPERATIONS.md`.
- Only the coordinator deploys to production.

## States under test (gated)

- A `data/towns_<st>.json` with `"gated": true` (Michigan and Virginia since Oct 12, 2026) is **not** part of the production run: `current.load_towns` skips it, so `ops/daily.sh` → `watch351.daily` (no `--states`) never crawls it and `data/hits_current.json` never lists it.
- It is crawled only when named explicitly, into a separate output directory: `python3 -m watch351.daily --states MI,VA --output-dir ../data/test --hits-name hits_mi_va.json`. Naming a gated state without `--output-dir` exits with an error before any request. Test output (index, ledger, health, run reports, hits file in this contract's shape) lives in `data/test/`.
- To promote a state: remove `"gated"` from its towns file (after site support for its board names exists).
- Board names outside New England: `boards.classify_board(name, state)` adds per-state aliases (MI township board / board of trustees / city commission → `select_board`, planning commission → `planning_board`, ZBA → `zoning_board_of_appeals`; VA board of supervisors → `select_board`, BZA → `zoning_board_of_appeals`). Without a state the classifier is unchanged.
- Keywords: `keywords.find_hits(text, state=...)` adds that state's patterns (`STATE_TOPICS`: PA 233 / CREO, special land use, 2232 review, siting agreements, wind / WECS, transmission and substations, rezoning to industrial, comprehensive-plan amendments), mapped onto the existing topic keys, plus false-positive rules for the shared topics (`STATE_FALSE_POSITIVE`: use tables and tables of contents, invoices and permit logs, non-zoning ordinance amendments, non-land-use moratoria, event flyers, rooftop / solar-powered equipment) from the hand check in `research_notes/Expansion/test_mi_va.md`. Without a state (MA, NY, RI) matching is unchanged; `experiments/keyword_regression.py` proves it on the cached MA/NY/RI documents.
- Michigan county planning commission rows carry `"attribute_townships": true`: a hit is filed under the township its agenda item names (`town`), with the county body kept as `board` ("Monroe County Planning Commission"), see `watch351/attribution.py`.
- `adapters/agenda_page.py` is the general agenda-page reader (WordPress, Revize, CivicPlus document pages, Municode Meetings, plain pages); `watch351/discover_sites.py` finds its listings and records closed vendors (Granicus, iQM2, PrimeGov, iCompass/Diligent, BoardDocs, Destiny) as `vendor_blocked` with the platform name.

## Crawler rules (non-negotiable)

Identify as 351WatchBot; obey robots.txt on every host and redirect hop; ≤1 request/second/host; no logins; never solve or bypass bot challenges; respect crawl-delay (skip hosts asking >10 s).
