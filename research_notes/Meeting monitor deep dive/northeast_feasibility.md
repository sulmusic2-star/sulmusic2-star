# 351 Watch crawler: Northeast feasibility test

Run date: 2026-10-10. Crawl window: meetings from 2026-09-10 to 2027-01-08 (30 days back plus everything already posted).

**Question:** does the Massachusetts agenda crawler (`projects/351watch/crawler`, package `watch351`) work in the other Northeast states without changes?

**Short answer:** partly.
- **Maine works now.** Its towns use CivicPlus AgendaCenter with New England board names, so the stock code finds the right boards.
- **New Hampshire and Rhode Island work where the town sites can be reached.**
- **Connecticut, New Jersey, New York, Pennsylvania and Vermont each need three things:**
  - board-name aliases in `boards.py`;
  - a data-center topic in `keywords.py`;
  - a few new listing adapters.

  Code alone will not fix one more problem: about 1 town in 5 is behind a bot wall (Cloudflare or Akamai).

## What was run

- **Glue script:** `projects/351watch/crawler/experiments/northeast_probe.py`. It imports `watch351` and leaves the package untouched.
  - It reuses `PoliteFetcher` (351WatchBot UA, robots.txt, 1 req/s/host, cache), the `civicplus`, `civicclerk` and `generic` adapters, `crawl.scan_document` (extraction plus OCR) and the existing keyword matcher.
  - Subcommands:
    - `get`: explore a page.
    - `fingerprint`: detect the platform, then classify CivicPlus/CivicClerk boards with both the stock `boards.py` classifier and a Northeast alias list.
    - `listings`: dry run.
    - `crawl`: the crawl itself.
- **Probe-only shim, used for 2 towns:** `generic_revize`. Revize sites redirect documents to `cms*.revize.com`, whose robots.txt allows only URLs that end in `.pdf`. Revize links append a `?t=<timestamp>` cache-buster, so the stock generic adapter is correctly refused by robots. The shim drops the cache-buster, which makes the URL robots-compliant. The two shim towns, Vergennes and East Whiteland, are flagged wherever they appear below.
- **Data files** (all new, in `projects/351watch/data/`):
  - `northeast_sample.json`: 48 towns, 6 per state, each with website, why it was chosen, and a source URL.
  - `northeast_towns.json`: per-town platform, listings, and whether it was automated or why not.
  - `agenda_hits_northeast.json`: hits, per-town status, per-document records, posting lead times, and a separate `supplemental_not_in_matcher` list.
- **Politeness:**
  - Every town request went through `PoliteFetcher`.
  - No logins, and no challenge was solved or bypassed.
  - Four town hosts were left alone: two whose robots.txt disallows all bots, one with a 15-second crawl delay, and one whose agenda API disallows bots.
  - 10 web searches were used to choose towns.
- **Town selection:** towns with 2025–2026 solar, BESS or data-center fights in the news, plus a few size controls (Augusta ME, Concord NH, Essex Junction VT, Northfield VT). Several RI fights in the sources date from 2022–2025.

## Headline numbers

| | |
|---|---|
| Towns tried | 48 (6 per state) |
| Automated with existing adapters | **27**: 15 CivicPlus AgendaCenter, 1 CivicClerk, 11 `generic` with hand-curated listings (2 of them via the Revize shim) |
| Not automated | **21**: 7 Cloudflare challenges, 2 Akamai 403s, 5 robots.txt disallows, 1 crawl-delay over the cap, 3 JavaScript-only listings, 3 with no agenda listing online |
| Agenda documents fetched and scanned | 153, of which 29 (19%) were image-only scans recovered by OCR |
| Keyword-matcher hits | **49 in 10 towns** |
| Hits that are energy or data-center siting items | about 24 |
| Hits that are other zoning or land-use items | about 9 |
| Noise | about 16: general (non-zoning) ordinance amendments, solar rebates mentioned in minutes |
| Data-center items the matcher missed | 6 documents in 3 towns (found by a supplemental regex, listed below) |

The bot-blocking rate is higher than in Massachusetts: 9 of 48 towns (19%) hit a Cloudflare or Akamai wall, against 3 of 30 MA pilot towns. Cloudflare alone blocked 3 of the 6 NH towns and 2 of the 6 RI towns.

## Per-state results

"Auto" means at least one tracked board was crawled through a watch351 adapter. "Hits" counts keyword-matcher hits.

Lead times are measured from the posting time to the meeting date, with the meeting counted from 00:00 on its day, so the figures are slight underestimates.

| State | Towns tried | Auto | Platforms seen | Blockers | Docs | Hits | Lead times observed |
|---|---|---|---|---|---|---|---|
| **CT** | Groton, New Milford, Cornwall, Harwinton, New Haven, East Lyme | 2 (Harwinton, Groton partial) | CivicPlus 1, AgendaSuite IIP (Provox) 1, WordPress 2, QScend 1, Legistar + Akamai 1 | Cloudflare (Cornwall); Akamai 403 (New Haven; its Legistar returned an empty body); robots allows only named bots (East Lyme); Crawl-delay 15 s, over the 10 s cap (New Milford) | 14 (10 OCR) | 5 | No posted stamps. PDF-metadata proxy median 5.0 d |
| **RI** | Hopkinton, West Greenwich, Johnston, North Kingstown, Portsmouth, Exeter | 3 (N. Kingstown, Portsmouth, W. Greenwich with Town Council only) | CivicPlus 3, ClerkBase 1, unknown behind Cloudflare 2 | Cloudflare (Hopkinton, Exeter); ClerkBase listing built by JavaScript (Johnston); W. Greenwich's town site has no agendas for its other boards (they are presumably filed only on the state portal) | 12 | 0 (1 data-center item missed, below) | Posted stamps: Portsmouth median 5.5 d (4.4–5.6), N. Kingstown median 5.5 d. RI SOS "Agenda filed on Oct 7 2026, 12:56PM" for the 10/13 Portsmouth Town Council (about 6 d) |
| **NH** | Bow, Nottingham, Rochester, Wakefield, Concord, Pembroke | 3 (Bow, Pembroke, Concord partial) | CivicPlus 2, Legistar 1, Granicus govAccess 1, unknown 2 | Cloudflare on Nottingham, Rochester and Wakefield, which are 2 of the 3 data-center fight towns plus the solar-and-BESS one | 23 (4 OCR) | 1 | Posted stamps: Bow median 9.0 d (0.5–20.5). Proxy median 6.5 d |
| **VT** | Vergennes, Vernon, South Burlington, Royalton, Essex Junction, Northfield | 3 (South Burlington, Essex Junction, Vergennes via shim) | CivicPlus 1, Revize 2, TYPO3 1, TownWeb + HeyGov 1, Wix 1 | HeyGov API robots `Disallow: /` (Vernon); no agendas online, only bulletin boards (Royalton); Wix page with no current agendas (Northfield) | 21 | 0 | Proxy median 2.9 d (Vergennes about 3 d) |
| **ME** | Brunswick, Scarborough, Bangor, Westbrook, Wiscasset, Augusta | **5** (all CivicPlus) | CivicPlus 5, Diligent Community 1 | Diligent robots disallows bots (Scarborough) | 32 (4 OCR) | **32** | Posted stamps: Westbrook median 2.3 d (1.5–17.5). Proxy median 2.6 d |
| **NY** | Clay, Lysander, Waterford, LaGrange, Dover, Claverack | 4 (Claverack, Dover, Clay, Lysander) | CivicPlus 1, CivicClerk 1, Drupal 3, WordPress 1 | Cloudflare (Waterford); LaGrange's "Agendas" link is a HubSpot tracking redirect, with no listing on the site | 18 (3 OCR) | 5 | Proxy median 5.4 d (range −0.7 to 19.4) |
| **NJ** | Andover Twp, Warren Twp, Lopatcong Twp, Mansfield Twp, Berkeley Heights, Neptune Twp | 4 (Warren, Berkeley Heights; Mansfield and Neptune thin) | CivicPlus 2, Drupal 1, Joomla 1, eCode360 1, Vision/Granicus 1 | eCode360 robots disallows `/documents` (Andover's agendas); Akamai 403 (Lopatcong) | 17 (5 OCR) | 0 | Proxy median 3.3 d |
| **PA** | Upper Burrell, East Whiteland, East Vincent, Granville, Watts, Covington | 3 (Upper Burrell, Covington, East Whiteland via shim), all `generic` | WordPress 4 (2 with FileBird), Revize 1, unknown 1 | robots `User-agent: * Disallow: /` (East Vincent); FileBird Document Library rendered by JavaScript (Granville, Watts; wp-json API not tried) | 16 (3 OCR) | 6 (3 data-center items missed, below) | Proxy median 0.4 d, unreliable because PA files are often re-saved after posting |

**The PDF-metadata proxy** is the PDF's ModDate, or its CreationDate when there is no ModDate, measured against the meeting date. It is not a posting time, only a rough bound: the agenda was prepared by then. Use it only as a rough indicator.

**Posting times are rarely visible.** Only 4 of the 15 CivicPlus sites (Bow, Westbrook, Portsmouth, North Kingstown) show the "Posted <date time>" stamp in AgendaCenter rows. That gives 27 directly observed lead times, with a median of 5.35 days and a range of −0.8 to 20.5 days. The negative values are agendas re-posted on the meeting day.

Eight towns show only "Amended" stamps (14 documents), almost all 0–5 days before the meeting. For RI, the state portal records an "Agenda filed on" timestamp for every meeting, which makes it the best lead-time source in the region.

## Notable real hits

Each is a real agenda item found by the existing matcher unless marked otherwise.

- **Harwinton CT Zoning Commission, 9/14, 9/28 and 10/13:** "Informal Discussion – draft moratoriums on data centers, battery storage facilities and solar."
  - Found only through the Northeast board aliases, because stock `boards.py` does not track "Zoning Commission".
  - The text came from OCR of a scanned PDF.
  - https://www.harwinton.gov/AgendaCenter/ViewFile/Agenda/_10132026-552
- **Bangor ME City Council, 9/14 and 9/28 (agenda packets):** "26-270 ORDINANCE Moratorium Extension Ordinance on Data Centers", an additional 180 days. The 10/14 packet records passage 8–0. https://www.bangormaine.gov/AgendaCenter/ViewFile/Agenda/_09282026-931
- **Westbrook ME Planning Board, 10/6:** "26-000777 – Land Use Ordinance Amendment … New Section §335-2.9.1 Data Centers … defines and prohibits". It was posted 2026-09-18 12:24, about 17.5 days ahead. https://www.westbrookmaine.gov/AgendaCenter/ViewFile/Agenda/_10062026-1030
- **Wiscasset ME Planning Board, 9/14 and 9/28:** site plan review and public hearing for a ground-mounted solar PV array (Map R-5, Lot 116-4). https://www.wiscasset.gov/AgendaCenter/ViewFile/Agenda/_09282026-793
- **Clay NY Zoning Board of Appeals, 10/12:** setback variance from 115 ft to 10.3 ft "for the development of BESS equipment", 4664 Wetzel Rd. https://townofclayny.gov/sites/default/files/2026-10/Zoning%20Board%20Agenda%20-%20October%2012%2C%202026.pdf
- **Clay NY Planning Board, 10/14:** Moyers Corners monopole cell tower site plan. https://townofclayny.gov/sites/default/files/2026-10/Planning%20Board%20Revised%20Agenda%2010-14-2026.pdf
- **Lysander NY Town Board, 10/1:** sets a 11/5 public hearing to extend the data-center moratorium to April 1, 2027. https://lysanderny.gov/sites/default/files/2026-10/10-1-2026_agenda.pdf
- **Claverack NY Planning Board, 10/5:** site plan and special exception for two ground-mounted solar trackers. https://www.claverackny.gov/AgendaCenter/ViewFile/Agenda/_10052026-136
- **Upper Burrell PA Board of Supervisors, 10/7:** public hearing on a Zoning Ordinance amendment "providing definitions and standards related to Data Centers". https://upperburrelltwp.com/wp-content/uploads/2026/10/UBT-BOS-Meeting-Agenda-10-7-2026-.pdf
- **Bow NH Planning Board, 10/1:** "Review of potential Zoning Amendments". The Bow data-center fight is not named in the one Selectboard agenda in the window (9/22, 1 page). https://www.bownh.gov/AgendaCenter/ViewFile/Agenda/_10012026-2778

**Missed by the existing matcher** (no data-center topic; found by the supplemental `data_center` regex):
- **East Whiteland PA Board of Supervisors, 9/24:** public hearing and enactment of "Ordinance #385-2026: Data Center Regulations (Curative Amendment)". The 9/10 agenda set the hearing date, and the Environmental Advisory Council (9/10, 10/15) carried "data center activity" updates. https://www.eastwhiteland.org/Documents/Agenda And Minutes/Board of Supervisors/2026/September 24 2026 Agenda crbk.pdf
- **North Kingstown RI Town Council, 9/14:** item 38, "Discussion concerning Data Center(s)". https://www.northkingstownri.gov/AgendaCenter/ViewFile/Agenda/_09142026-2958
- **Upper Burrell PA Planning Commission, 9/15:** "Updated Proposed Data Center Ordinance". https://upperburrelltwp.com/wp-content/uploads/2026/09/UBT-PC-Agenda-9152026-Updated.pdf

## Why the existing code underperforms outside MA

1. **Board names (`boards.py`).**
   - The stock classifier misses these names:
     - CT "Planning Commission", "Zoning Commission" and "Inland Wetlands & Watercourses Commission";
     - NY "Town Board";
     - NJ "Township Committee", "Township Council", "Board of Adjustment" and "Environmental Commission";
     - VT "Planning Commission" and "Development Review Board";
     - PA "Board of Supervisors", "Zoning Hearing Board" and "Planning Commission".
   - On the CivicPlus and CivicClerk sites tried, it missed 13 tracked boards in 7 towns, including governing bodies in Claverack, Dover, Warren Twp and Berkeley Heights. Those boards supplied 24 of the 153 documents and all 5 Harwinton hits.
   - It also misclassified "Building Code Board of Appeals" (North Kingstown) as a ZBA.
   - Fix: the alias list in `EXT_BOARDS` in the probe script can be moved into `boards.py`.
2. **Topics (`keywords.py`).**
   - Data centers are now the main Northeast siting fight, and every state in the sample has one. Without a `data_center` topic, items are caught only when they also say "moratorium" or "zoning amendment".
   - PA "curative amendment", NY "Local Law No. X amending Chapter NNN" and NJ "Ordinance … amending Chapter NN (Land Use)" phrasing is not covered by `zoning_amendment`.
   - The MA-specific topics (40B, 225 CMR 29) produced no hits here.
3. **Platforms.**
   - CivicPlus AgendaCenter dominates only in ME (5/6). It is common in NH and RI (2 or 3 of 6) and rare elsewhere (1 or 2 of 6 in CT, NJ, NY and VT; 0 in PA).
   - Most other automated towns are one-off WordPress, Drupal, Revize, Joomla or TYPO3 pages that need hand-written `generic` listings. That is about 10–20 minutes per town, and it breaks when a site changes.
   - The `generic` adapter falls short on several layouts:
     - Pages that mix boards on one listing: Lysander, Concord's Legistar calendar, and Clay's "recent" block.
     - Links named "Details": AgendaSuite list pages, which the adapter's `_MORE` filter skips.
     - Compact dates such as `a10082026pb_0.pdf` or `100526zbaagenda.pdf`.
     - Legacy `.doc` files: Neptune.
4. **Statewide portal (RI).**
   - Every RI public body files its notice and agenda on the Secretary of State's Open Meetings portal (`opengov.sos.ri.gov`).
   - Its robots.txt returns 404, so crawling is allowed.
   - Meeting pages are plain HTML with "Filed on" timestamps. Agenda PDFs come from a plain GET on `/Common/DownloadMeetingFiles?FilePath=…`.
   - The meeting index is a search form: a per-entity dashboard URL rendered empty for the ID tried, and the index endpoint was not found. One adapter for it would cover all 39 RI municipalities, including the Cloudflare-blocked Hopkinton and Exeter. This is the best single investment found.
5. **Bot walls and robots.txt.** These account for 15 of the 21 failures, and code will not fix them:
   - 7 Cloudflare challenges, 2 Akamai 403s, 5 robots disallows (East Lyme, East Vincent, the Diligent portal, eCode360 `/documents`, the HeyGov API) and 1 crawl delay.
   - eCode360 document hosting (General Code) is common in NJ, NY and PA. Its robots.txt disallows `/documents` for all agents.
   - Getting these needs the town's or vendor's permission. For New Milford, raising the 10-second crawl-delay cap would be enough.
6. **Politeness gaps in `fetch.py`.** These were found but not fixed, because the package is read-only for this task:
   - `_load_robots` treats any robots.txt served as `text/html` as allow-all. `api.heygov.com` serves `User-agent: * / Disallow: /` with an HTML content type, so the fetcher would crawl a site that forbids it. I honored the disallow by hand for Vernon.
   - Redirects are followed by `requests` before the target host's robots.txt is checked. For example, www.vergennes.org redirects to cms8.revize.com, so one disallowed request is sent and then discarded.

## Verdict by state

| State | Existing adapters | Why |
|---|---|---|
| **Maine** | **Handles well now** | 5/6 CivicPlus, stock board classifier correct, 32 hits including real data-center moratoria (Bangor, Westbrook) and solar site plans (Wiscasset). Only Scarborough's Diligent portal (robots) is out of reach. |
| **New Hampshire** | Good where reachable | CivicPlus towns (Bow, Pembroke) work unchanged, and NH's "Zoning Board of Adjustment" already classifies. But Cloudflare blocks half the sample, including two of the three data-center fight towns tried (Nottingham, Rochester). |
| **Rhode Island** | Fair now; best potential | CivicPlus towns work. Cloudflare and ClerkBase block the rest. A single RI SOS portal adapter would cover the whole state, with filed-on timestamps. |
| **New York** | Fair | CivicPlus and CivicClerk work once "Town Board" is aliased. Drupal towns need hand listings. Good real hits (Clay BESS and cell tower, Lysander data-center moratorium). |
| **Connecticut** | Weak | 2/6 automated. Heavy blocking (Cloudflare, Akamai, robots, crawl delay). The P&Z, Zoning Commission and Inland Wetlands names are missed by stock `boards.py`. Many scanned PDFs (Harwinton 10/10 OCR). |
| **New Jersey** | Weak | CivicPlus towns work only with the township aliases. eCode360 robots and Akamai block others. 0 matcher hits in the window. |
| **Pennsylvania** | Weak for current code, high signal | No CivicPlus in the sample, so every automated town is a hand listing. FileBird JavaScript and robots block 3/6. Data-center ordinances are everywhere but often missed without a `data_center` topic. |
| **Vermont** | Weak | Small towns post on bulletin boards, or on Wix and HeyGov pages. BESS siting is decided by the state PUC (Section 248), so local agendas carry less signal. |

**Recommended order of work:**
1. Add the Northeast aliases to `boards.py`. This is cheap and immediately fixes CivicPlus and CivicClerk coverage in CT, NJ, NY and VT.
2. Add a `data_center` topic, plus Local Law, chapter-ordinance and curative-amendment patterns.
3. Build the RI SOS Open Meetings adapter.
4. Have the Revize `?t=` handling in the generic adapter strip the cache-buster.
5. Fix the two `fetch.py` robots issues.
6. Build Legistar, ClerkBase and FileBird (wp-json) adapters only if those states are prioritized.
