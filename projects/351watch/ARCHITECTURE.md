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
| Trending stories (ranked, with headlines) | `trending.py` → `data/trending.json` | Trending workstream (data side). Contract below; the page is the web app's. |
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
      "doc_url": "https://…/Agenda/_10062026-5421 (only when the town re-posted the agenda under a new file: the live link; source_url keeps the id stable)",
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
- `topics` keys: `battery_storage, solar, data_center, moratorium, clean_energy_siting, 40b_comprehensive_permit, wireless_telecom, zoning_amendment` (+ `wetlands_filing` for MassDEP-sourced items; + `extraction` (quarries, gravel and sand pits) and `large_development` (large commercial / industrial projects) for the gated Vermont Act 250 feed only, until the site has labels for them). New topics must be added here first.
- State-feed `source` values (gated, Wave 1): `vt_act250` (Vermont Act 250 district commissions), `ct_siting_council` (Connecticut Siting Council). Their `board` is the state body ("Act 250 District 5 Commission", "Connecticut Siting Council") with `board_key` `planning_board`; `town` is the host town.
- Window: meetings from 120 days back to 120 days ahead; older items move to `data/state/hits_archive/YYYY-MM.jsonl`.
- Town slug: lowercase, spaces → `-`, apostrophes dropped; URL path `/{state}/{slug}` e.g. `/ma/great-barrington`.

## `data/trending.json` (Trending page contract)

`python3 trending.py` (standard library only) reads `hits_current.json`, `data/search/` (agenda text), `data/state/hits_archive/`, `tracker.json` and `ag_decisions.json`, groups hits into stories, scores them and writes the top 100. `ops/daily.sh` runs it after the crawl and before `build.py`; a failure keeps yesterday's file. Tests: `python3 tools/test_trending.py`. Preview: `python3 trending.py --dry-run --print 40` (add `--towns MA:Carver --topics solar` to see the page's re-ranking).

```json
{
  "generated": "2026-10-12T21:07:34+00:00",
  "window": {"start": "2026-10-12", "end": "2027-02-09"},
  "personalize": {"in_my_towns": 2.0, "in_neighbor_towns": 1.0, "topic_match": 0.5},
  "stories": [
    {
      "id": "3f219af9840f",
      "score": 27.68,
      "headline": "Plymouth Town Meeting takes up a one-year data-center moratorium",
      "dek": "Plymouth's Town Meeting is Saturday, Oct 17. The warrant lists an article proposing a temporary moratorium on data centers.",
      "quote": "…\"Data Center\", and by creating a new section, §207-12, Temporary Moratorium on Data Centers, which would enact a one-year temporary moratorium from October 17, 2026…",
      "reasons": ["Moratorium vote", "2 town boards", "Town Meeting Oct 17"],
      "topics": ["data_center", "moratorium", "zoning_amendment"],
      "state": "MA", "town": "Plymouth", "county": "Plymouth", "towns": ["MA:Plymouth"],
      "board": "Town Meeting", "board_key": "town_meeting",
      "meeting_date": "2026-10-17", "meeting_date_source": "warrant", "days_until": 5,
      "first_seen": "2026-10-10T14:41:39+00:00", "is_new": true,
      "source_url": "https://www.plymouth-ma.gov/DocumentCenter/View/11128/…",
      "town_path": "/ma/plymouth",
      "action": "moratorium",
      "boards": [{"town": "Plymouth", "board": "Town Meeting", "board_key": "town_meeting", "meeting_date": "2026-10-17"}, "…"],
      "hit_ids": ["203c7e1a696a", "…"]
    }
  ]
}
```

- `stories` is sorted by `score`, highest first, at most 100. `window.start` is the day the file was built (Boston time); `window.end` is the hits window end.
- A story is one project or one local rule: hits share a story when they are the same agenda item, the same town + board + meeting + topic family (data centers; energy = solar, battery storage, clean energy siting, wind; zoning; 40B; wireless), the same named applicant (LLC names join across towns; utilities and carriers never do), the same site address in a town, or the same town's moratorium or bylaw on one energy or data-center subject (so the Planning Board hearing and the City Council referral are one story).
- Only stories with a live item are kept: a meeting today or later, an undated fall Town Meeting warrant, or a MassDEP filing from the last 14 days. Past meetings drop off; hits from the last 60 days still count as momentum. The lead hit (headline, dek, quote, `board`, `meeting_date`, `source_url`) is the story's highest-scoring live hit. Minutes of an earlier meeting printed in an agenda packet never lead a story and are never shown; they only help group hits.
- `headline` (≤ 84 characters, sentence case, present tense), `dek` (one or two sentences, ≤ 26 words) and `reasons` come from fixed templates filled only with words found in the agenda: board, date, applicant name, site address, sizes, durations. When a template's fact is missing, a plainer template is used, down to "Battery storage item on Holyoke Planning Board agenda" and "The agenda lists an item on battery storage." Nothing claims an outcome or a position, and no reader-facing text uses system words ("packet", "mentions", "hits", "matched", "flagged", "tracker"). `quote` is the shortest clean agenda sentence holding the subject or project name (≤ 200 characters, OCR noise removed, `…` where cut); render it in `<q>` or `<blockquote>`.
- `reasons` are short phrases a reader cares about, in this order: what is happening ("Moratorium vote", "Moratorium hearing", "Proposed ban", "Public hearing", "Continued public hearing", "Town Meeting vote", "Adoption vote", "Permit application", "Continuance requested"; none for a bare discussion or listing), "First time this has come up in Leyden" (only with 60+ days of that town's agendas and no earlier item on the topic), a stated size ("300 units", "4.9 MW"), momentum ("3 town boards", "2 city boards", "Neighboring towns too" or "Neighboring Plympton too" when `neighbors.json` says so, else "Also in Plympton"; "Also on the Sep 23 agenda"; "State wetlands filing Sep 30"), the date ("Hearing Oct 20", "Town Meeting Oct 17", "Meeting Oct 13"), and "Town has an earlier vote on this" or "AG disapproved Gill's battery storage bylaw on Sep 24" when the data show it. Reasons never say "today" or "tomorrow" or name a weekday; the page shows relative time from `meeting_date`.
- `towns` are site town ids (`MA:Carver`), every town involved; `town`/`state`/`county`/`town_path` are the lead's. `boards` lists each board once (next upcoming meeting, else latest past one).
- `meeting_date_source`: `agenda`, `warrant` (read from an undated Town Meeting warrant's first pages; `meeting_date` is null when the warrant gives none) or `filing` (MassDEP filing date). `days_until` is counted from `window.start`; the page should recompute it from `meeting_date` and hide stories whose meeting has passed.
- `is_new`: the story's earliest `first_seen` is within 72 hours of `generated`.
- `action` is one of `moratorium, ban, adopt, town_meeting, bylaw_hearing, project_hearing, rezoning, warrant_review, filing, bylaw_draft, project, deal, process, discussion, mention, continuance, minutes, withdrawn, cancelled` (`minutes` = narrative minutes of an earlier meeting printed in the packet).
- Publishing: the page needs the file at `/data/trending.json`; copy it in the deploy the way `hits_current.json` is copied.

### Score

`score = (topic points × action multiplier + bonuses × routine − vague) × timing`, rounded to 2 places. All weights are constants at the top of `trending.py`.

| Part | Values |
|---|---|
| Topic points | data center 10; battery storage 8; moratorium or ban on any siting subject at least 7; large solar (ground-mounted, large-scale, MW, acres, dual-use) 6; wind 5; clean energy siting 5; zoning change 4; 40B 3.5; other solar (carport, rooftop, municipal) 3.5; cell tower 3; wetlands filing 1.5; non-zoning bylaw or non-siting moratorium 1 |
| Action multiplier | moratorium or ban 1.6 (+0.1 for a vote, hearing or Town Meeting article; 1.2 when tentative, "moratorium?"); adoption vote 1.5; Town Meeting article 1.4; bylaw hearing 1.4; public hearing on a project 1.3; rezoning 1.2; warrant review 1.1; filing, draft bylaw, project application 1.0; lease or contract 0.8; consolidated-permit process 0.7; discussion 0.55; mention 0.5; continuance 0.35; minutes 0.35; withdrawn 0.25; canceled 0.15. Conservation Commission project items × 0.85 (wetlands review only) |
| Scale (largest one, project items only) | MW ≥50: 3, ≥10: 2.5, ≥2: 2, ≥0.5: 1; MWh ≥200: 3, ≥40: 2.5, ≥8: 2, ≥1: 1; units ≥200: 2.5, ≥100: 2, ≥40: 1.5, ≥10: 1; acres ≥50: 2, ≥20: 1.5, ≥5: 1; dollars ≥$10M: 2, ≥$1M: 1.5, ≥$100k: 0.5; sq ft ≥200k: 2.5, ≥50k: 1.5, ≥10k: 1 |
| First in town | +2 data center, battery storage, moratorium; +1.5 wind; +1 solar, clean energy, 40B, cell tower. Only when no earlier dated (or any undated) hit on that topic exists for the town and we hold 60+ days of its agendas before the story |
| Momentum | +2.5 per extra board, +3 per extra town (each capped at 3 extra); +1 per extra meeting (max 2) when the board count is 1. Boards seen only through printed minutes do not count |
| Other bonuses | +1 first seen in the last 72 hours (no reason line; `is_new` carries it); +1 `tracker.json` records a vote by the town on the subject (adopted, approved or disapproved by the AG, in effect, expired, pending at the Legislature); +1.5 the AG disapproved the town's bylaw on the subject in the last 365 days |
| Routine | bonuses × min(1, action multiplier ÷ 0.8), so momentum cannot lift a mention or minutes above a real hearing |
| Vague | −1.5 for a long snippet with no project name that is only a mention or discussion, or one that is mostly OCR noise |
| Timing | meeting in 0–1 days 1.5; 2–7 days 1.35; 8–14 days 1.2; 15–30 days 0.9; 31–60 days 0.7; later 0.5; undated fall warrant 0.75; MassDEP filing 0.8; past 0 |

### Personalization (the page, in the browser, no account)

The visitor picks towns (site ids such as `MA:Carver`) and optionally topics. The page loads `/data/trending.json` and `/data/neighbors.json` and re-ranks:

```
personal = score × (1 + 2·in_my_towns + 1·in_neighbor_towns) × (1 + 0.5·topic_match)
```

- `in_my_towns` = 1 if any of the story's `towns` is a chosen town, else 0.
- `in_neighbor_towns` = 1 if any of the story's `towns` is in `neighbors[t]` for a chosen town `t` and is not itself chosen, else 0. Both can be 1 (a story in my town and the next town over gets × 4).
- `topic_match` = 1 if the story's `topics` share a key with the chosen topics, else 0 (no topics chosen: always 0).
- Sort by `personal`, highest first; ties keep the file's order. The three constants are also in the file's `personalize` key; `trending.personalize()` is the reference implementation.

Worked example, from the Oct 12, 2026 file, for a visitor who picks Carver and the topic `solar` (Carver's neighbors are Kingston, Middleborough, Plymouth, Plympton and Wareham):

| Story | score | my town | neighbor | topic | personal |
|---|---|---|---|---|---|
| Plymouth Town Meeting takes up a one-year data-center moratorium | 27.68 | 0 | 1 | 0 | 27.68 × 2 × 1 = 55.36 |
| Harvard Town Meeting takes up solar and battery storage rules | 20.64 | 0 | 0 | 1 | 20.64 × 1 × 1.5 = 30.96 |
| Federal Pond Solar asks Carver planners for continuance to Oct 27 | 6.50 | 1 | 0 | 1 | 6.50 × 3 × 1.5 = 29.25 |
| Boxborough weighs a data-center moratorium | 27.00 | 0 | 0 | 0 | 27.00 |
| Wareham Town Meeting takes up zoning changes | 7.92 | 0 | 1 | 0 | 7.92 × 2 = 15.84 |

Sorted, the Carver visitor's list starts: Plymouth 55.36, Geneva 31.50 (its story also carries `solar`), Rochester 31.28, Harvard 30.96, the Carver continuance 29.25, then Boxborough 27.00. Their own town's routine item climbs from #70 to #5 but still does not outrank a neighbor's moratorium vote. `python3 trending.py --dry-run --print 10 --towns MA:Carver --topics solar` prints this list.

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

### Wave 1: Vermont and Connecticut state feeds, 50 more New York places (gated, Oct 13, 2026)

- **State feeds** live in `watch351/sources/`: `vt_act250.py` (the Act 250 "Agenda" list of the last three weeks, `anrweb.vt.gov/ANR/Act250/agenda.aspx`, plus each project's `Details.aspx?Num=` page) and `ct_siting.py` (the Siting Council's pending-matters page, its petition and docket lists, matter pages, the meeting agendas and docket Final Decision entries on `portal.ct.gov/csc`). Shared helpers (town lists, the item ledger, applicant clean-up: organizations kept, private persons shown as `[individual]`, contact names stripped) are in `sources/state_feeds.py`. Each writes `<source>_items.json` (every matter, with `siting_relevant`, `topics`, `flag_reason`) and `<source>_hits.json` (flagged items in this contract's shape) to `data/test/wave1/sources/` by default.
- **Gating.** `current.other_hits` merges every `data/sources/*_hits.json` into production, so the feeds refuse `--out-dir data` and `data/sources` (`state_feeds.check_out_dir`). `data/towns_vt.json` (256 towns and cities) and `data/towns_ct.json` (169 towns) are `"gated": true`, `"automated": false` and `"coverage": "state_feed"`: no town is crawled; they are the host-town lists the feeds file items under. Promotion = pointing the feeds at `data/sources/` from `ops/daily.sh` and removing `"gated"` once the site labels `extraction` and `large_development`.
- **Vermont PUC §248** is not read: its ePUC searches are POST forms and the PUC calendar is disallowed by robots.txt.
- **New York, 50 more places** (battery-storage moratorium towns and data-center fights): `data/test/wave1/config/towns_ny.json`, `"gated": true`, kept outside the `data/towns_*.json` glob because NY is a published state (its towns would otherwise appear on the site). Crawled only by `python3 -m watch351.daily --data-dir ../data/test/wave1/config --states NY --output-dir ../data/test/wave1/ny --hits-name hits_ny_wave1.json` (`experiments/wave1_test.py crawl`). Promotion = moving rows into `data/towns_ny.json`. `boards.STATE_BOARD_PATTERNS["NY"]` and the NY branches of `discover_sites` are used by discovery only (crawling never classifies boards), so production NY configs are unaffected.
- **Adapters added or extended** (all opt-in by listing key, so existing configs behave as before): `adapters/cmm_compass.py` (Compass Web Development "CMM" agenda embeds used by small NY Weebly sites); `generic_ny` keys `{month}` placeholder, `skip_missing_months` (also for `{year}` pages), `follow_pages` + `follow_doc` + `follow_limit` (notice or post pages and their .docx / .pdf attachments), `assume_year: "url"` (a month-named agenda on a year page); `agenda_page` key `"self_page": "force"` (read the page itself as the agenda, ignoring header, nav and footer).
- `experiments/gate_check.py` proves the gate (default selection MA 240 / NY 33 / RI 39, no VT / CT in a production build or in `data/sources/`, refusals before any request); `experiments/wave1_test.py` builds the town lists, discovers and curates the NY places, crawls, runs the feeds, draws the hand-check samples and validates `data/test/wave1/hits_wave1.json`. Results: `research_notes/Expansion/test_vt_ct_ny.md`.

## Crawler rules (non-negotiable)

Identify as AgendaAheadBot (robots.txt rules for the former name 351WatchBot are also obeyed); obey robots.txt on every host and redirect hop; ≤1 request/second/host; no logins; never solve or bypass bot challenges; respect crawl-delay (skip hosts asking >10 s; listing pages, a few requests per host per day, may wait up to 20 s: `fetch.LISTING_CRAWL_DELAY_CAP`).

## `data/briefs/` (written briefs contract)


A brief is a short written explanation of one flagged agenda item, keyed by the hit's `id` (the 12-hex id in `hits_current.json`). It replaces the item's rules-based sentence on town pages, topic pages, `/upcoming`, the meeting pages, `/w/<key>` and the Biggest stories page, but only after `tools/verify_briefs.py` has checked it against the agenda's own text and set `verified: true`. Nothing unverified renders; `build.py` runs the same check again when it loads them.

- `data/briefs/<ST>/<YYYY-MM>.jsonl` (the hit's meeting month; `undated.jsonl` without one): one JSON object per line, append-only. A later row for the same `id` replaces the earlier one (the latest `written_at` wins). `briefs.append_brief()` writes one; `briefs.load_briefs()` reads the latest per id.
- Fields, all optional except `id` and `written_at`: `what` (one plain sentence: what is proposed or being decided), `where` (address or location as the agenda gives it), `size` (MW, acres, units, dollars, as stated), `who` (applicant or sponsor as named), `action` (one of `hearing`, `vote`, `discussion`, `continued`, `adopted`, `withdrawn`, `other`), `next` (what happens next, if the agenda says), `history` (earlier meetings on the same item, from our own data), `can_speak` (true, false or null, from the agenda), `line` (the one-line version, at most 90 characters), `quote` (the exact agenda sentence or sentences the brief rests on), `source_url`, `written_at`, `writer` (e.g. `claude-fable-5-1`), `verified` (set only by the verifier).
- The verifier (`python3 tools/verify_briefs.py`, `--check` to write nothing): every proper noun, number and address fragment in `what`, `line`, `next`, `size` and `where`, and the whole `who` value, must appear in the document's text in `data/search` (case-insensitive, punctuation-tolerant); `quote` must appear verbatim (whitespace and curly quotes aside; `…` joins parts in order); `action` needs its cue near the quote ("continued" needs "continu"); `can_speak: true` needs "public hearing" or "public comment" nearby; dates in `history` must be meeting dates we hold for that town. It prints each failure with the reason, sets `verified` on the latest row for each id (the only field it changes), and exits 1 when any brief fails. `ops/daily.sh` runs it after `trending.py` and before `build.py`.
- Rendering: the brief's `line` is the item's headline with the stage word from `BRIEF_STAGE` by `action` beside it (a `continued` brief says "Postponed to Tue Oct 27" when its `next` names the day, or "Asks to postpone to …" when the applicant asked and the board hasn't decided, `brief_stage()`), then `what` as a sentence, `history` as "Before this:", then the facts line (`where` · `size` · `who`). On the `/m/` page only: `next`, the clerk line when `can_speak` is true, and the quote behind "Agenda wording". Straight quotes in the writers' fields become curly ones at build time (`smart_quotes()`); the quote stays as printed. `lines.json` and `trending.json` carry the briefs and the labels for `w.js` and `trending.js`. Without a brief, the rules-based line stays, in the same format.
- More fields: `how_to_speak` (the agenda's own rule: sign-up, time limit, where written comments go; leave it empty when the agenda gives none and the default rule prints), `when_time` and `when_place` (as the agenda prints them; the page uses them when the header gave none), `duplicate_of` (the id of the row this one repeats, when one item was flagged twice), `missing` (what the agenda doesn't say; for the records, never rendered).
- Writers' rules the verifier enforces (from the round-5 reviewers, Oct 2026): no asides about our records, our copy or how the agenda spells a name ("per our records", "cut off in our copy", "as the agenda spells it", "listed with a question mark" all fail; `missing` is the place for such notes); no "no rules stated" in `how_to_speak` (leave it empty instead); a quote starts where the agenda item starts, not mid-sentence ("Public Hearing Cont'd: 3. Federal Pond Solar, LLC, requesting …", not "located at 104 Tremont Street …"); "heard" only when the board heard the matter, "continued" when the agenda says it was continued; a Planning Board's vote on a zoning article is its recommendation, Town Meeting adopts.
- Hearings an earlier agenda moved to a later day with no agenda yet are listed on the town page under "Also ahead, from earlier agendas" (`continued_ahead()`, from the stage's date), with "if the board agrees" while the move is only the applicant's request, and Town Meeting days a write-up's `next` names ("Special Town Meeting October 26, 2026"); the list drops a line once that day's agenda or warrant is posted.
- A continuation printed at the end of a legal notice ("CONTINUED TO NOVEMBER 4, 2026.") counts even when it sits well past the sentence that named the project (`CONT_TAIL_RE` in trending.py, stopping at the next notice). A meeting whose listing title or first lines say it is cancelled renders as "Canceled, the town says" with every item's status Canceled (`MEETING_CANCELLED` in build.py and trending.py). A council's printed "Third Reading" or "Discussion & Action" is a vote.
- Re-posted agendas: when a town's listing drops a document and lists another for the same board and day, the daily crawl marks the old one `replaced` (`DocIndex.retire_replaced`); its items keep their ids with `doc_url` pointing at the new file, items the new file dropped go, and the new file's new items get their own ids. Tests: `python3 tools/test_replaced.py`.
- Spreadsheets: `/topics/<slug>.csv` (meetings still ahead on that topic, one row per item that says something, with county and status), `/attorney-general/rulings.csv` and `/attorney-general/town-actions.csv`, all written by `build.py`.

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
