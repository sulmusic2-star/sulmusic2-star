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
| Town neighbors (free watchlist area) | `tools/neighbors.py` → `data/neighbors.json`, published at `/data/neighbors.json` | Web app workstream. Contract below. |
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

## Watchlists (web app; the link is the key, there are no accounts)

- A watchlist is created on `/watch`: a home town (`home_town`, `"MA:Carver"`), towns from its free area (`towns`), topics, optional name, optional Slack, Discord, Teams (Workflows: `*.logic.azure.com`, `*.api.powerplatform.com`) or generic webhook URL, and an optional email address.
- Stored as a private Vercel Blob `watchlists/<id>.json`. Two keys, both 24+ random URL-safe chars: `id` is the private key that can edit or delete; `feed_id` is a read-only key used in feed, calendar and share links (`feeds/<feed_id>.json` points back to the watchlist). `GET /api/watchlists?id=<feed_id>` returns a read-only view (`readonly: true`) without the private id, the webhook or any email details; PATCH and DELETE need the private key. Feeds accept either key so older links keep working. DELETE removes the watchlist, its `feeds/` entry and its entry in the email index.
- Delivery: web view `/w/<id>`, RSS `/api/feed?id=…&format=rss`, JSON, iCalendar (`format=ics`, upcoming meetings with matched items), webhooks and email. A Vercel Cron function (`/api/cron/dispatch`, `CRON_SECRET`, daily 13:30 UTC after the data refresh) posts webhooks first, then sends email digests; each channel keeps its own cursor and carries only items first seen since its last successful delivery.
- Product name: `SITE_NAME` in `site/api/_watch.js` (default "Agenda Ahead", or the `SITE_NAME` env var) is the only name used in webhook messages, feed titles, email subjects, senders and footers. Stable identifiers (`351watch-<id>` RSS guids, `@351watch` calendar UIDs, the `351WatchBot` user agent) stay as they are so feed readers and calendars don't duplicate items.
- Plans: free founding beta. Stripe Checkout code exists but is disabled unless `STRIPE_SECRET_KEY` and price env vars are set.

### The free area: one town plus its neighbors

All topics and all delivery channels are free; the limit is geographic. A watchlist covers one area: `home_town` plus any towns that touch it in `/data/neighbors.json`. Enforced in `validateConfig` (`site/api/_watch.js`) on create and update:

- Create: `home_town` is required and must be a known town; `towns` ⊆ {home_town} ∪ neighbors(home_town). The home town itself need not be in `towns`. `MAX_TOWNS` (200), unknown-town and topic checks still apply.
- Update, same home town: towns already on the list stay (so a later change to the neighbor data never blocks a save); added towns must be in the area.
- Update, new `home_town`: the whole list must fit the new area, so a list can't collect several areas.
- Watchlists made before the limit have no `home_town` (`grandfathered: true` in the private view). They keep working, and edits may remove towns. Adding a town requires the whole list to fit one area: the `home_town` sent, or else the first town on the list whose area holds the rest, which is then saved as `home_town`.
- Over the limit: HTTP 400, `code: "free_area"`, `fields.towns` and `error` both "Free alerts cover one town and the towns next to it. Need more places? Tell us at /privacy#contact." If the neighbor file can't be loaded: 503, `code: "area_unavailable"` (removing towns still works).

### `data/neighbors.json` (contract)

- Built by `python3 tools/neighbors.py` (needs `pip install shapely pyshp`) from US Census cartographic boundary files, county subdivisions, 1:500,000, vintage 2024 (`cb_2024_{25,44,36}_cousub_500k.zip`). Source URLs, vintage and method are in its `_meta` key. Published at `/data/neighbors.json` by `site/vercel-build.sh`; the API reads it from there like `towns.json`.
- Shape: `{"_meta": {...}, "MA:Carver": ["MA:Kingston", "MA:Middleborough", "MA:Plymouth", "MA:Plympton", "MA:Wareham"], ...}`. Keys containing `:` are town ids exactly as in `site/data/towns.json`; lists are sorted and symmetric.
- Coverage: every MA (351) and RI (39) town and all of NY (998: towns, cities, New York City's five boroughs; Indian reservations left out). NY names used by more than one place get ` (city)` or ` (<County> County)` (e.g. `NY:Amsterdam (city)`), except towns already on the site, which keep their ids. Neighbors across the MA, RI and NY lines are included; CT, NH, VT, NJ and PA towns are not.
- Rule: towns are neighbors when their boundaries come within 50 m of each other along at least 100 m (a corner-only contact measures about 25 to 55 m). Where the Census clips at the shoreline (ocean, Nantucket Sound, Narragansett Bay), towns across the water are not neighbors; Nantucket, Gosnold, Jamestown, New Shoreham and Staten Island have none. Rivers and unclipped bays (Long Island's Peconic Bay) count. Halifax is not a Carver neighbor: Plympton lies between them.
- Some neighbors are not on the site (most NY places). The UI offers neighbors ∩ `towns.json`; the API rejects others as unknown towns.

### Email alerts

- Provider: `site/api/_email.js` is the only module that sends mail (Resend's HTTP API, `POST https://api.resend.com/emails`, Bearer `RESEND_API_KEY`, sender `EMAIL_FROM`; a bare address gets `SITE_NAME` as display name). Email is on only when both env vars are set; otherwise the API rejects a non-empty `email` field (400, `fields.email`) and `/api/status` reports `email_alerts: false`. `EMAIL_TRANSPORT=file` (ignored on Vercel) writes messages to a local folder for tests.
- Opt-in: `email` on create or PATCH stores `wl.email = {address, confirmed: false, confirm_token, unsubscribe_token, requested_at, confirm_sends, confirm_sent_at, confirmed_at, last_emailed_at, last_email, failures}` and sends one confirmation email. Tokens are `<feed_id>.<24 random chars>`, never the private key. PATCH with an empty `email` removes the address; a different address starts over with new tokens; the same address in any case, or its masked form, changes nothing.
- Links never act on a GET, because mail scanners (Outlook Safe Links, gateways) open every link in an email. `GET /api/email?action=confirm&t=…` and `…action=unsubscribe&t=…` show a plain page with one button; the button POSTs a form (no script, so the site CSP allows it) to the same URL with the token, and only the POST changes anything. A confirm POST sets `confirmed: true` and redirects (303) to `/w/<private id>?email=confirmed`.
- Unconfirmed addresses get nothing else, apart from one more confirmation on request (`POST /api/email?action=resend&id=<private id>`): at once if the first send failed, otherwise 24 hours after it, then never again.
- Limits: 10 sign-ups per hour per network (per function instance); per address, 3 confirmation emails a day and 6 in 30 days, and at most 3 watchlists (confirmed ones, plus unconfirmed ones under a week old). Kept in `emails/<sha256 of the lowercased address>.json`: `{watchlists: {<id>: {confirmed, at}}, sends: [ISO times]}`. The index holds no address.
- Digest: after the webhooks, `/api/cron/dispatch` sends each confirmed address one email of the items first seen since `email.last_emailed_at` (at most 50, then "And N more"), only when there is something new, then moves the cursor to the data snapshot time. A failed send leaves the cursor so the items go out the next day. Sends are spaced `EMAIL_SEND_INTERVAL_MS` apart (default 550 ms, for Resend's 2 requests a second) two at a time, and stop starting after 50 s (`email_deferred` in the response; those go out the next day).
- Message: plain text and simple HTML. Each item gives town, board, meeting date, matched topics, a one-line agenda excerpt (quoted, never edited) and the agenda link. Footer: the share link, the private manage link, a one-click unsubscribe link. Headers `List-Unsubscribe: <…/api/email?action=unsubscribe&t=…>` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click`. Subject: `Agenda Ahead: 2 new items for Carver and neighbors` (the watchlist's name when it has one).
- Unsubscribe: a POST to `/api/email?action=unsubscribe&t=…` removes the address and its index entry at once. The form's POST answers a "You're unsubscribed" page linking to the watchlist page (where the address can be added again); the RFC 8058 one-click POST that mail providers send (body `List-Unsubscribe=One-Click`, urlencoded or multipart) answers 200 JSON.
- Privacy: the full address is stored only on the watchlist blob. The private view shows a masked address (`j***@example.com`) and its status; the read-only view, feeds and webhooks show nothing about email.

### `GET /api/status`

`{"ok": true, "email_alerts": true}`: whether this deployment has email configured, so pages can show or hide the email option. No caching.

## Deploys

- Every deployment is built from git at one commit: the project's build command pipes `site/vercel-build.sh` from raw.githubusercontent.com at `<sha>` with `SITE_REF=<sha>`, which downloads that commit's tarball and writes a Build Output API v3 bundle (`.vercel/output`: static pages and data, the `/pagefind/` search index built from `data/search`, one Node function per `site/api/**/*.js`, routing headers, clean URLs and the daily cron). The deployment upload itself is a one-line `package.json`. Steps: `OPERATIONS.md`.
- Only the coordinator deploys to production.

## Crawler rules (non-negotiable)

Identify as 351WatchBot; obey robots.txt on every host and redirect hop; ≤1 request/second/host; no logins; never solve or bypass bot challenges; respect crawl-delay (skip hosts asking >10 s).
