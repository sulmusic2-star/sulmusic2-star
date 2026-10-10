# 351 Watch: agenda crawler (prototype)

This prototype reads real Massachusetts town board agendas and flags clean-energy and
land-use items: battery storage, solar, moratoria, consolidated permits under 225 CMR 29,
40B, wireless facilities, and zoning or bylaw amendments. It proves the core technology
for 351 Watch and supplies the live examples on the public tracker.

```
data/sample_towns.json   30 pilot towns (input)
data/towns.json          town -> platform, agenda listing URL per board, or why not automated
data/agenda_hits.json    crawl output (hits + per-town status)
crawler/run.py           CLI
crawler/watch351/
  fetch.py               polite HTTP: UA, robots.txt, 1 req/s/host, retries, disk cache
  adapters/              one adapter per agenda platform
    civicplus.py           CivicPlus "Agenda Center" (/AgendaCenter)
    civicclerk.py          CivicClerk portal (public read-only OData API)
    generic.py             any plain HTML page that lists agenda links (Revize, WordPress, ASP...)
  discover.py            platform fingerprinting + listing discovery -> towns.json
  extract.py             PDF (pdftotext, tesseract OCR fallback) / HTML / DOCX -> text
  keywords.py            topic regexes, false-positive guards, snippet extraction
  dates.py               meeting-date parsing from link text / URLs
  crawl.py               pipeline: list -> fetch -> extract -> match -> dedupe -> JSON
```

## Running it

Requirements: Python 3.10+, `requests`, `beautifulsoup4`, `lxml`, and poppler-utils (`pdftotext`,
`pdfinfo`, `pdftoppm`). Optional: `tesseract-ocr` (`apt-get install tesseract-ocr`). When it is
installed, image-only PDFs from office copiers are OCR'd, up to the first 12 pages. OCR runs one
single-threaded process per core, and its text is cached in `.cache/ocr/`. Without tesseract, those
documents are counted in `documents_without_text_layer` and yield no hits. Hits from OCR text carry
`"text_source": "ocr"`.

```bash
cd crawler
python3 run.py discover                 # fingerprint sites, (re)build listings in data/towns.json
python3 run.py crawl                    # last 45 days + next 90 days -> data/agenda_hits.json
python3 run.py crawl --towns Amherst,Sudbury --days-back 30
python3 run.py crawl --offline          # re-match from crawler/.cache only (no network)
```

A full crawl of the 30 towns takes a few minutes on a cold cache. Most of that is the
1-second-per-host delay plus OCR. On a warm cache it takes seconds. Listing pages are re-fetched after
6 hours. Agenda documents are cached indefinitely under `crawler/.cache/`, which git ignores.

## Politeness rules (all in `fetch.py`)

- User-Agent: `351WatchBot/0.1 (+contact: hello@351watch.example)`. The contact is a placeholder; swap in a real address before any wider run.
- `robots.txt` is obeyed for every host, including hosts reached by redirect. A 4xx on robots.txt means "allow". A 5xx or unreachable robots.txt means skip the host for this run. A `Crawl-delay` is honored, and a host asking for more than 10 s is skipped.
- At most 1 request per second per host, enforced with a per-host lock, so parallel town workers cannot exceed it.
- Timeouts are 10 s to connect and 45 s to read. Connection errors get up to 2 retries with backoff. HTTP errors are never retried.
- Downloads are capped at 40 MB.
- No logins, no cookies beyond what a plain GET receives, and no bot-challenge solving. A site behind Cloudflare is recorded as not automated.

## Adding a town

1. Add an entry to `data/towns.json` with at least `town` and `website`:
   ```json
   {"town": "Holden", "website": "https://www.holdenma.gov"}
   ```
2. Run `python3 run.py discover --towns Holden`. Discovery fingerprints the homepage:
   - **CivicPlus**: if `/AgendaCenter` exists, every category is classified with `boards.py` and the tracked boards are written as listings. Nothing else to do.
   - **CivicClerk**: if the page links `<tenant>.portal.civicclerk.com`, it sets `platform: civicclerk` and `tenant`.
   - **Cloudflare challenge**: the town is marked `automated: false` with the reason.
   - **Anything else** becomes `platform: generic`. Add the listings by hand:
     ```json
     {"board": "Planning Board", "board_key": "planning_board",
      "url": "https://town.example/planning-board/agendas?year={year}",
      "link_pattern": "agenda", "exclude_pattern": "minutes", "resolve_pdf": false}
     ```
     `link_pattern` is matched against link text and href. `{year}` expands to each year the
     window touches. Set `resolve_pdf: true` when the link goes to an HTML landing page that links
     the PDF, as with WordPress attachment pages.
3. If the town can't be automated, set `"automated": false` and give a `"reason"`. Discovery keeps curated reasons.
4. Run `python3 run.py crawl --towns Holden` and check `data/agenda_hits.json`.

New platform? Subclass `adapters.base.Adapter`, implement `discover()` and `list_agendas()`, and
register it in `adapters/__init__.py`. Granicus ViewPublisher, Granicus govAccess ("vyhlif")
`/agendas` pages, and BoardDocs are the obvious next adapters. None of the 30 pilot towns needed
them, and Granicus's robots.txt currently disallows all non-search-engine bots.

## Output format (`data/agenda_hits.json`)

```json
{
  "generated": "2026-10-10T14:45:00+00:00",
  "towns_attempted": 30, "towns_automated": 24, "documents_scanned": 338,
  "hits": [{
    "town": "Sudbury", "board": "Planning Board", "meeting_date": "2026-10-14",
    "topics": ["battery_storage"],
    "snippet": "... Battery Energy Storage System Bylaw ...",
    "source_url": "https://cdn.sudbury.ma.us/.../PlanningBoard_2026_Oct_14_agenda.pdf",
    "listing_url": "https://sudbury.ma.us/planning/meetings/"
  }]
}
```

Extra keys: `window`, `documents_without_text_layer`, `hits_by_topic`, `towns_by_platform`, and
`towns` (per-town counts, errors and not-automated reasons). Each hit also carries `board_key` and
`document_title`.

Topic keys are `battery_storage`, `solar`, `moratorium`, `clean_energy_siting` (consolidated
permit / 225 CMR 29 / clean energy infrastructure), `40b_comprehensive_permit`, `wireless_telecom`
and `zoning_amendment`. Hits are deduplicated on town + board + meeting date + the text around the
keyword. That collapses an item listed twice in one agenda, or repeated in an amended re-post.
Every hit comes from a document that was actually fetched in the run.

## Results summary

First full run: 2026-10-10. The window covered meetings from 2026-08-26 through 2027-01-08,
that is, 45 days back plus everything already posted ahead.

| | |
|---|---|
| Towns attempted | 30 |
| Towns automated | **24**: 21 CivicPlus AgendaCenter, 1 CivicClerk (Bridgewater), 2 generic (Sudbury, Fall River) |
| Not automated | 6 (below) |
| Agenda documents fetched and scanned | **338** |
| Image-only scans (no text layer) | 93 (27%), all recovered with tesseract OCR |
| Hits after dedupe | **178**, of which 25 are for meetings not yet held |

Hits by topic (a hit can carry several topics):

| Topic | Hits |
|---|---|
| zoning_amendment | 66 |
| solar | 47 |
| battery_storage | 44 |
| 40b_comprehensive_permit | 25 |
| moratorium | 20 |
| clean_energy_siting | 15 |
| wireless_telecom | 4 |

**Notable real items:**
- **Fitchburg City Council, 2026-10-06:** temporary zoning moratorium on "Locally Regulated Commercial Battery Energy Storage Systems (LRC-BESS)". https://www.fitchburgma.gov/AgendaCenter/ViewFile/Agenda/_10062026-5418
- **Leominster City Council, 2026-09-28:** councilor's request to adopt a temporary moratorium on BESS. This agenda is a scanned PDF, found via OCR. https://www.leominster-ma.gov/AgendaCenter/ViewFile/Agenda/_09282026-2143
- **Pittsfield City Council, 2026-10-13:** the "Battery Energy Storage Systems" zoning amendment, which Ordinances & Rules recommended approving as amended, 5-0. https://www.pittsfieldma.gov/AgendaCenter/ViewFile/Agenda/_10132026-1026
- **Northampton Planning Board, 2026-10-08:** zoning package for consolidated local permitting of Small Clean Energy Infrastructure Facilities "in compliance with 225 CMR 29.00". https://www.northamptonma.gov/AgendaCenter/ViewFile/Agenda/_10082026-9442
- **Westford Select Board, 2026-10-13:** warrant article for the 10/26 Special Town Meeting creating zoning Section 6.6, Small Clean Energy Infrastructure Facilities. https://www.westfordma.gov/AgendaCenter/ViewFile/Agenda/_10132026-6982
- **Carver Planning Board, 2026-10-13:** special permit for ground-mounted and dual-use PV with coupled BESS (Federal Pond Solar). https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10132026-616

A recurring theme the keyword set wasn't designed for is **data centers**. Plymouth, Northampton,
Pittsfield, Fitchburg and Leominster have data-center moratoria. Amherst, Bridgewater, Charlton
and Wakefield have data-center zoning amendments. These surface through `moratorium` and
`zoning_amendment`, and data centers probably deserve their own topic.

**Not automated, and why** (details in `data/towns.json`):
- **Becket and Middleborough:** Cloudflare bot challenge (403) on every page. Not bypassed.
- **Barnstable:** barnstable.gov is behind a Cloudflare challenge. A legacy host,
  `tobweb.town.barnstable.ma.us`, serves the same pages without it, but crawling that would sidestep
  the town's bot protection. Its listings are configured and disabled pending the town's okay.
- **Framingham:** agendas are on Granicus, whose robots.txt disallows every bot except named search engines.
- **Medway:** the agenda page is rendered by JavaScript from `api.heygov.com`, and that API's robots.txt disallows everything.
- **Worthington:** no online agenda listing, only minutes in Google Drive folders.

**Technical obstacles and gaps:**
1. **Scanned PDFs.** 27% of agendas are image-only copier output (RICOH, Konica, Canon, Brother).
   Andover and Sutton post 100% scans, Leominster 15 of 19, Pittsfield 17 of 20. Without OCR
   those towns are invisible. OCR text is noisier ("Art;cle"), and hits from it are tagged
   `text_source: "ocr"`.
2. **Bot protection and robots.txt** account for 5 of the 6 non-automated towns. Getting them
   needs the town's permission, or a vendor relationship with Granicus or HeyGov, not more code.
3. **JS-only portals.** CivicClerk is fine because its public read API serves the same data.
   HeyGov is robots-blocked.
4. **Packets vs. agendas.** Some "agenda" files are full packets that include prior minutes and
   staff memos. Pittsfield's City Council packet runs 159 pages, and Great Barrington's 9/28 file
   exceeded the 40 MB cap and was skipped. Those packets give richer hits, but some snippets come
   from minutes or backup material rather than the agenda item itself.
5. **Town Meeting warrants.** 8 CivicPlus towns have a "Town Meeting" AgendaCenter category, but it
   holds only one-line posting notices; the warrant text lives in each town's Document Center. Select
   Board agendas that review warrant articles partly cover this (see Westford above). A
   Document Center adapter is the next step.
6. **Fall River** posts agendas online only for City Council: three 124-page scanned packets, of which
   the first 12 pages are OCR'd. Planning, ZBA and ConCom pages have forms but no agendas.
7. **Precision.** Bare "wireless/telecommunications" and "battery" were too noisy (voter-ID
   boilerplate, IT purchases, EV fleets, drone checklists), so those topics require siting or
   energy-storage context. Bylaw-amendment hits include general (non-zoning) bylaws on purpose.
   Expect a few percent false positives; spot-check before publishing.
