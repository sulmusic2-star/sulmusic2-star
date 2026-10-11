# 351 Watch: Rhode Island via the Secretary of State Open Meetings portal

Run date: 2026-10-10 to 2026-10-11. Crawl window: meetings from 2026-08-26 to 2027-01-08 (45 days back, 90 days ahead).

**Question:** can one adapter on the RI Department of State's Open Meetings portal (`opengov.sos.ri.gov`) cover all 39 Rhode Island municipalities, with the portal's own "filed on" timestamps?

**Short answer:** yes.

- **Coverage.** All 39 municipalities are automated, with 151 portal public bodies:
  - every city and town council (`select_board`);
  - every planning board or commission;
  - every zoning board of review;
  - 29 conservation commissions.

  This includes Hopkinton and Exeter, whose own websites sit behind Cloudflare challenges, and Johnston and West Greenwich, whose sites lacked usable listings in the Northeast probe.
- **Signal.** The crawl scanned 398 agenda files (29 recovered by OCR) for 328 meetings and found **119 hits in 29 municipalities**, 17 of them for meetings not yet held.
  - The standout is a **wave of data-center prohibitions**: Hopkinton (moratorium, then a zoning ban), Burrillville, Exeter, South Kingstown, Cumberland, Bristol ("AI Data Centers") and North Kingstown.
  - Solar projects: Richmond (391 Church Street Solar; Charbert Solar 3, 4.5 MW AC), Hopkinton (Skunk Hill Road Solar) and Little Compton (Beacon Solar special use permit).
- **Lead time.** Agendas for tracked boards are filed a median **5.2 days** before the meeting starts. 97.8% are filed at least 48 business hours ahead (weekends and state holidays excluded, as the statute counts).
  - For the hit documents, the median is 5.1 days and the minimum 2.1 days. That is the warning a daily crawl of the portal would give.
- **One caveat.** The portal is behind Cloudflare, which rate-limits.
  - At 1 request per second, it answered HTTP 429 to 2 requests out of about 220.
  - The adapter spaces its own requests 2.5 s apart and backs off on 429.
  - The daily engine's shared fetcher should use 2.5 s for this host too (see Limitations).

## Terms of use and robots.txt

| Check | Finding |
|---|---|
| `https://opengov.sos.ri.gov/robots.txt` | **404**, so there is no robots file. Under RFC 9309 and `fetch.py`, everything is allowed. `https://www.sos.ri.gov/robots.txt` is also 404. |
| Terms of use on the portal | **None.** The portal footer links only About, Contact, News, Notary Public and the APRA request page. The login page (`/`) is for filers only, and no public page needs a login. |
| RI.gov statewide policies (these are what the state's sites point to) | **Disclaimer** (https://apps.ri.gov/policies/disclaimer/): "This site is intended to be used by the public for viewing and retrieving information only."<br>**Copyright** (https://www.ri.gov/policies/copyright/): "The compiled information presented on this WWW site is considered public information and may be distributed or copied. However, use of appropriate byline/photo/image credits is requested."<br>**Security** (https://www.ri.gov/policies/security/): this prohibits "unauthorized attempts to upload information or change information." Read-only GETs do neither. |
| The SOS's own invitation | The portal's Open Meetings page says: "Advanced users can even use RSS technology to stream real-time meeting information to their own website." The page is https://opengov.sos.ri.gov/OpenMeetings, linked from https://www.sos.ri.gov/divisions/open-government-center. |
| Verdict | **No clause prohibits automated read access.** Credit the source on alerts ("RI Department of State Open Meetings portal" plus a link), as the copyright policy requests. |
| Bot protection | Cloudflare sits in front (the `/cdn-cgi/` email obfuscation is visible). There was no JavaScript challenge on any page. HTTP 429 arrived only above about 0.7 requests per second sustained. |

## Endpoints used

All are plain GETs that the portal's own public pages issue, either as links or as the jQuery calls behind "click a meeting date". There are no logins, no form POSTs and no cookies. The public search form (`POST /OpenMeetings`) and the autocomplete endpoint (`POST /OpenMeetingsPublic/SuggestSearchPublicPostingEntity`) were not used.

| Purpose | GET |
|---|---|
| The 39 municipalities and their parent EntityIDs | `/GOVDirectoryPublic/OfficialSearch?topmenuId=105&page=IdxMuni`<br>(rows call `GOVDirectoryMeetingInfo(<EntityID>,4)`; "Narragansett Indian Tribe" is skipped) |
| Municipality website (discovery only) | `/GOVDirectoryPublic/GOVDirectoryMeetingDetails?EntityID=<town id>` ("Web:") |
| Every public body filed under a municipality | `/OpenMeetingsPublic/OpenMeetingDashboard?subtopmenuId=201&EntityID=<town id>&MeetingID=0` → `table#ParentEntitiesSummary` |
| A body's meetings: upcoming, past and cancelled | the same dashboard URL with the body's EntityID. `ViewMeetingDetails(<MeetingID>)` sits on each row, with a hidden `hdn*DateSeq` date and the time.<br>The past list holds **about the 100 most recent** meetings. |
| A meeting's notice and agenda files | `/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID=<id>` (the popup fragment). It gives "Filed on", the Emergency / Annual Calendar / Public Announcement flags, and one `DownloadMeetingFiles('\Notices\<n>\<yyyy>\<id>.pdf')` link per agenda file, each labelled "Agenda filed on <time> by <name>". |
| The agenda file | `/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C<n>%5C<yyyy>%5C<id>.pdf` |
| Human-readable meeting page (`listing_url`) | `/OpenMeetingsPublic/MeetingInformation?MeetingID=<id>` (RSS items link here too) |

Also found, but not used by the adapter:
- `GET /OpenMeetingsPublic/SearchPublicPosting?MDate=MM/DD/YYYY` lists every meeting statewide on a date.
- `GET /RSSFeed/Rss?feedType=1&entityID=0&…` is an RSS feed of all upcoming meetings statewide (367 items, with "Filed on"). It is the cheapest change detector for a future daily run.
- Per-entity RSS feeds exist with `feedType` 6 (today), 7 (upcoming), 9 (minutes) and 10 (subcommittees).

## What was built

- **`crawler/watch351/adapters/ri_sos.py`**, platform `ri_sos`, registered with one appended line in `adapters/__init__.py`.
  - **`discover(cfg)`** reads the municipality dashboard and keeps the bodies it classifies.
    - Classification strips the town prefix ("Hopkinton Planning Board" → "Planning Board"), applies RI rules, then falls back to `boards.classify_board`.
    - A body is listed only if it has filed a non-cancelled meeting in the last 730 days or has one upcoming. RI bodies must file every meeting, so a quiet board is still covered when it next meets.
  - **`list_agendas(cfg, window)`** returns one `AgendaDoc` per uploaded agenda file, earliest-filed first.
    - Each doc carries `meeting_id`, `meeting_time`, `meeting_start`, `notice_filed_at`, `agenda_filed_at`, `amended`, `emergency` and `public_announcement` in `extra`.
    - Annual-calendar postings and cancelled meetings are skipped.
  - **Caching.**
    - Dashboards follow `LISTING_MAX_AGE` (6 h).
    - A meeting-detail fragment is re-read every 6 h until a copy fetched after the meeting day is cached; that copy is final.
    - Agenda files are cached indefinitely through `scan_document`.
  - **Throttling.** Its own listing and detail requests pass through a module-level gate, at least `PORTAL_INTERVAL` = 2.5 s apart. An HTTP 429 gets one retry after 90 s.
  - **Helpers** for the 48-hour rule: `ri_holidays(year)` (R.I. Gen. Laws 25-1-1, plus Thanksgiving and the even-year general election day) and `business_hours_between()`.
- **`crawler/experiments/ri_sos_build.py`**: the driver.
  - `discover` writes `data/towns_ri.json`.
  - `crawl [--today D] [--offline]` writes `data/agenda_hits_ri.json`.
  - It uses `crawl.scan_document` and `crawl.town_configs` unchanged, with `PoliteFetcher(min_interval=2.5)`.
- **`data/ri_census_sub_est2024.csv`**: Census Vintage 2024 subcounty rows for RI, giving county, `pop_2020` (estimates base) and `pop_2024_est`.
  - The town rows sum exactly to every county total and the state total.
  - It was retrieved by hand, as for MA, because a strict parse of www2.census.gov's robots.txt groups `User-agent: *` with a `Disallow: /`.
- **Untouched:** `crawl.py`, `fetch.py`, `keywords.py`, `state.py`, `daily.py` and `boards.py`. The shared `data/first_seen.json` ledger was not written. Each hit's `first_seen` is our own first fetch time, from the cache timestamp.
- **`daily.py` compatibility.** `daily.py` reads every `data/towns_*.json` and calls `REGISTRY[platform](fetcher).list_agendas(cfg, window)`, so RI joins the next daily run without code changes.
- **Contract check.** All 119 hits pass `watch351.current.validate`, including the `sha1(source_url|snippet)[:12]` ids. That was run in-process; `hits_current.json` was not rewritten.

## Coverage: municipalities × boards

| | Bodies |
|---|---|
| Municipalities automated | **39 / 39** (1,097,354 people, 2020) |
| Town or city council → `select_board` | 39 municipalities (Providence: "City Council Meeting" and "City Council as a Whole") |
| Planning board or commission → `planning_board` | 39 (plus Central Falls' Combined Planning and Zoning Board, and Portsmouth's Prudence Island Planning Commission) |
| Zoning board of review → `zoning_board_of_appeals` | 39 (Pawtucket's is filed as "Board of Appeals", with an agenda header reading "Zoning Board of Appeals"; Glocester and Central Falls also file a zoning "Board of Appeals") |
| Conservation commission → `conservation_commission` | 29 (Exeter: "Conservation Committee"; Warwick: "Wildlife & Conservation Commission"; Narragansett: "Conservation Commission - Tree Board") |
| Town meeting → `town_meeting` | **0.** No municipality files a financial town meeting as a portal body. In RI, financial town meetings vote budgets only, and zoning is adopted by the council (R.I. Gen. Laws 45-24), so no siting signal is lost. |

- **No active conservation commission on the portal** in 10 municipalities: Central Falls, Cranston (last filed 2020-12-23), East Greenwich, Johnston, Newport, North Providence, Pawtucket, Providence, West Warwick and Woonsocket.
- **Dormant bodies kept out** (`board_stale` in `towns_ri.json`), 8 in all:
  - Narragansett Conservation Commission (last filed 2024-09);
  - North Kingstown Board of Appeals (2023);
  - Portsmouth Planning Board of Appeal (2022);
  - Warren Zoning Board of Appeals (2021);
  - Providence Zoning Commission (2005);
  - Warwick Airport Land Use Commission (2009);
  - and two more.
- **Land-use bodies outside the five contract board keys.** These are left out by the classifier and listed per town in `untracked_bodies`:
  - Technical Review Committees (most towns) and Cranston's Development Plan Review Committee;
  - Tiverton's Solar Ordinance Advisory Committee and Zoning Revision Committee;
  - energy committees in Barrington, Little Compton, Richmond, Westerly, Warren, Woonsocket, Jamestown and New Shoreham;
  - Newport's Energy and Environment Commission;
  - Middletown's Zoning Ordinance Review Committee.

  Adding any of them needs a new `board_key` in ARCHITECTURE.md first.

Per municipality (meetings, documents and hits are within the crawl window):

| Town | County | Pop 2020 | Council | Planning | Zoning | ConCom | Meetings | Docs | Hits |
|---|---|---|---|---|---|---|---|---|---|
| Barrington | Bristol | 17,154 | ✓ | ✓ | ✓ | ✓ | 9 | 13 | 6 |
| Bristol | Bristol | 22,484 | ✓ | ✓ | ✓ | ✓ | 9 | 9 | 2 |
| Burrillville | Providence | 16,141 | ✓ | ✓ | ✓ | ✓ | 11 | 14 | 2 |
| Central Falls | Providence | 22,583 | ✓ | ✓ | ✓ | – | 8 | 11 | 1 |
| Charlestown | Washington | 7,996 | ✓ | ✓ | ✓ | ✓ | 15 | 17 | 0 |
| Coventry | Kent | 35,704 | ✓ | ✓ | ✓ | ✓ | 10 | 10 | 3 |
| Cranston | Providence | 82,885 | ✓ | ✓ | ✓ | – | 8 | 12 | 2 |
| Cumberland | Providence | 36,404 | ✓ | ✓ | ✓ | ✓ | 6 | 6 | 1 |
| East Greenwich | Kent | 14,305 | ✓ | ✓ | ✓ | – | 7 | 11 | 1 |
| East Providence | Providence | 47,130 | ✓ | ✓ | ✓ | ✓ | 12 | 15 | 2 |
| Exeter | Washington | 6,461 | ✓ | ✓ | ✓ | ✓ | 8 | 9 | 5 |
| Foster | Providence | 4,469 | ✓ | ✓ | ✓ | ✓ | 5 | 7 | 0 |
| Glocester | Providence | 9,976 | ✓ | ✓ | ✓ | ✓ | 12 | 14 | 0 |
| Hopkinton | Washington | 8,398 | ✓ | ✓ | ✓ | ✓ | 10 | 13 | 12 |
| Jamestown | Newport | 5,554 | ✓ | ✓ | ✓ | ✓ | 9 | 10 | 3 |
| Johnston | Providence | 29,576 | ✓ | ✓ | ✓ | – | 4 | 6 | 1 |
| Lincoln | Providence | 22,519 | ✓ | ✓ | ✓ | ✓ | 9 | 9 | 4 |
| Little Compton | Newport | 3,616 | ✓ | ✓ | ✓ | ✓ | 9 | 10 | 5 |
| Middletown | Newport | 17,076 | ✓ | ✓ | ✓ | ✓ | 13 | 14 | 2 |
| Narragansett | Washington | 14,525 | ✓ | ✓ | ✓ | ✓ | 13 | 14 | 3 |
| New Shoreham | Washington | 1,407 | ✓ | ✓ | ✓ | ✓ | 16 | 17 | 8 |
| Newport | Newport | 25,169 | ✓ | ✓ | ✓ | – | 9 | 13 | 10 |
| North Kingstown | Washington | 27,742 | ✓ | ✓ | ✓ | ✓ | 6 | 6 | 1 |
| North Providence | Providence | 34,128 | ✓ | ✓ | ✓ | – | 5 | 10 | 2 |
| North Smithfield | Providence | 12,596 | ✓ | ✓ | ✓ | ✓ | 5 | 6 | 0 |
| Pawtucket | Providence | 75,611 | ✓ | ✓ | ✓ | – | 6 | 7 | 1 |
| Portsmouth | Newport | 17,867 | ✓ | ✓ | ✓ | ✓ | 6 | 6 | 0 |
| Providence | Providence | 190,978 | ✓ | ✓ | ✓ | – | 5 | 7 | 0 |
| Richmond | Washington | 8,023 | ✓ | ✓ | ✓ | ✓ | 10 | 10 | 4 |
| Scituate | Providence | 10,380 | ✓ | ✓ | ✓ | ✓ | 6 | 9 | 1 |
| Smithfield | Providence | 22,125 | ✓ | ✓ | ✓ | ✓ | 9 | 12 | 0 |
| South Kingstown | Washington | 31,932 | ✓ | ✓ | ✓ | ✓ | 9 | 10 | 12 |
| Tiverton | Newport | 16,359 | ✓ | ✓ | ✓ | ✓ | 9 | 12 | 13 |
| Warren | Bristol | 11,148 | ✓ | ✓ | ✓ | ✓ | 7 | 10 | 3 |
| Warwick | Kent | 82,831 | ✓ | ✓ | ✓ | ✓ | 8 | 10 | 5 |
| West Greenwich | Kent | 6,528 | ✓ | ✓ | ✓ | ✓ | 6 | 6 | 0 |
| West Warwick | Kent | 30,998 | ✓ | ✓ | ✓ | – | 6 | 6 | 0 |
| Westerly | Washington | 23,352 | ✓ | ✓ | ✓ | ✓ | 8 | 9 | 4 |
| Woonsocket | Providence | 43,224 | ✓ | ✓ | ✓ | – | 5 | 8 | 0 |

## Crawl results

| | |
|---|---|
| Portal bodies crawled | 151 |
| Meetings in window (non-cancelled, annual calendars excluded) | **328**: 278 already held, 50 upcoming and already filed |
| Meetings by board | council 139, planning 95, zoning 55, conservation 39 |
| Meetings without an agenda file | 0 (every notice carries at least one uploaded file) |
| Agenda files listed / scanned | 398 / **398**: 369 with a PDF text layer, 29 image-only scans recovered by tesseract OCR |
| Hits after dedupe | **119** (17 for meetings not yet held), in 29 municipalities |
| Hits by topic | zoning_amendment 64, 40b_comprehensive_permit 23 (RI's Low and Moderate Income Housing Act, R.I. Gen. Laws 45-53), solar 19, data_center 16, moratorium 3, wireless_telecom 2, **battery_storage 0** |
| Hits by board | planning 63, council 54, zoning 2 |
| Requests to the portal | about 230 (discovery) plus 735 (crawl) plus 129 (re-run for 4 PDFs that got 429), about 1,100 in all. Every one went through `PoliteFetcher` with the 351WatchBot UA and robots checked. |

**Battery storage: zero items in the window.**
- A full-text scan of all 398 documents for "battery", "BESS", "energy storage", "storage facility" and "MW" found only:
  - library UPS batteries;
  - police auto-parts invoices (Scituate's bills list);
  - self-storage facilities (Warren, Portsmouth, North Providence);
  - Richmond's 4.5 MW solar.
- The matcher's guards rejected all of these correctly.
- RI's storage siting is quieter than its data-center fights right now. OER's 2026 BESS model ordinance (below) means storage zoning amendments are likely to arrive on these same agendas.

**Precision.** About 30 of the energy and data-center hits are real siting items. Noise found:
- "Solar Salt" in a South Kingstown road-salt bid (2026-09-28). This needs an exclusion in `keywords.py`.
- Newport's green-building ordinance listing "solar panels" as a sustainability option.
- Tiverton's "PFAS moratorium". It is a real moratorium but not an energy one.
- An Exeter resident's correspondence titled "ChatGPT/Data Center Water Consumption". This is borderline: it is correspondence, but tied to Exeter's data-center zoning item.

Zoning-amendment hits are overwhelmingly real zoning items, such as short-term rentals, form-based code, cannabis, zone changes and comprehensive permits. A few are general ordinance amendments (Barrington's parks and salaries chapters), which is the matcher's intended behavior.

## Lead times (from the portal's own timestamps)

These cover the 278 tracked-board meetings already held in the window. Each figure runs from the portal timestamp to the meeting's scheduled start in Eastern Time. "Business hours" exclude Saturdays, Sundays and R.I. Gen. Laws 25-1-1 holidays, the way R.I. Gen. Laws 42-46-6(b) counts its 48 hours. In this window that removes Labor Day 9/7, Columbus Day 10/12, Election Day 11/3, Veterans Day 11/11, Thanksgiving and Christmas.

- **"Filed on" (the notice) equals the first "Agenda filed on" in every meeting.** Notice and agenda are filed together, so the portal's first timestamp is when the agenda became public.

| | median | p10 | p25 | p75 | p90 | min | max |
|---|---|---|---|---|---|---|---|
| First agenda filed, days before meeting | **5.21** | 2.31 | 4.15 | 6.87 | 14.54 | 0.0 | 90.3 |
| …in business hours | **76.8** | 50.7 | 53.7 | 105.2 | 245.3 | 0.1 | 1448 |
| Hit documents (n = 62), days before meeting | **5.12** | 4.04 | 4.15 | 6.09 | 7.10 | 2.13 | 20.1 |

- **≥ 48 business hours before the meeting start:** 97.8% (272 of 278).
- **Under the strict reading** (48 business hours before the meeting *date*, i.e. by the start of the meeting day): only **64.4%**.
  - Councils commonly file on Thursday or Friday for a Monday or Tuesday evening meeting, about 50 to 52 business hours ahead of the start.
- **≥ 5 calendar days:** 61.2%. **≥ 7 days:** 25.2%.
- **By board** (median days; share ≥ 48 business hours before the start / before the meeting day; share ≥ 7 days):

  | Board | Median days | ≥ 48 business h before start | ≥ 48 business h before day | ≥ 7 days |
  |---|---|---|---|---|
  | Zoning board of review | **11.3** | 100% | 95% | 74% (hearings must be advertised) |
  | Planning | 6.1 | 99% | 85% | 31% |
  | Conservation | 4.7 | 94% | 56% | 16% |
  | Councils | 4.3 | 97.5% | 41% | 7% |

- **Under 48 business hours at first filing:** 6 meetings.
  - Central Falls City Council 10/7 (filed minutes before; not flagged as an emergency);
  - Hopkinton Conservation Commission 9/8 (filed Saturday 9/5, 18.5 business hours) and Planning Board 9/8 at noon (filed Friday 9/4, 24.8 business hours); Labor Day fell in between;
  - Charlestown Conservation Commission 9/24 (filed the day before, 27.1 business hours);
  - two Cranston City Council notices for 9/22 (filed Friday 9/18 after 7 pm: 47.3 and 47.98 hours).
- **Later agenda versions.** 47 meetings had a later version (amended agenda or added attachments); in 7 of them it was filed inside 48 business hours.
- **Emergency meetings:** 0 in the window.
- **Town medians**, shortest: Cumberland 2.3 d, Central Falls 2.3 d, Little Compton 2.7 d. Longest: Johnston 12.8 d, Lincoln 9.3 d, Barrington 7.2 d.
- **Comparison.** These are true filing stamps, unlike the PDF-metadata proxy used for other states. RI's 5.2-day median is longer than the 3.3 days measured on NY CivicPlus "Posted" stamps, and in line with the 5.35 days seen on the few Northeast CivicPlus sites that show stamps.

`days_before_meeting` in the hit file follows the shared contract: our `first_seen` (this backfill, 2026-10-11 UTC) to the meeting day. It is negative for meetings already held. The RI-specific fields carry the real public-availability lead:
- `days_filed_before_meeting`
- `business_hours_filed_before_meeting`
- `agenda_filed_at`
- `notice_filed_at`
- `meeting_time` / `meeting_start`

## Notable real hits

Data centers, the dominant RI siting fight in this window:
- **Hopkinton Town Council, 2026-09-02:** "Discuss, consider and possibly vote to adopt a moratorium on data centers pursuant to Town Charter Section 3220." Filed 8/31 (2.1 d ahead).
  - Then on **9/21**: set a public hearing on a "Zoning Ordinance amendment that would define 'data centers' and prohibit that use in all zoning districts."
  - Planning Board advisory votes followed on 9/2, 9/10 and 10/7.
  - https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4512%5C2026%5C565050.pdf
  - https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4512%5C2026%5C566769.pdf
- **Burrillville Town Council, 2026-10-14 (upcoming):** an amendment to "Chapter 30 Zoning to prohibit data centers." Filed 10/9 11:04 (5.3 d ahead). https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4127%5C2026%5C568466.pdf (meeting page https://opengov.sos.ri.gov/OpenMeetingsPublic/MeetingInformation?MeetingID=1094516)
- **Exeter Town Council, 2026-09-28:** zoning text amendments adding "DATA CENTER" (§1.2.25 definition, use table §2.4.1.79), alongside incinerator/pyrolysis and asphalt plant uses. https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4390%5C2026%5C567225.pdf
- **South Kingstown:** the Planning Board on 9/10 took up a "ZONING TEXT AMENDMENT - Data Centers" referral, and the Town Council on 9/28 moved to "prohibit data centers in Industrial Zones."
  - https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C3946%5C2026%5C565608.pdf
  - https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C3943%5C2026%5C567329.pdf
- **Bristol Planning Board, 9/10 and 10/8:** zoning amendments "to regulate AI Data Centers" (re-review and possible action on 10/8). https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4497%5C2026%5C567962.pdf
- **Cumberland Town Council, 2026-09-16:** "#26-22 – An ordinance amending the Zoning Ordinance relating to Data Centers." https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C5060%5C2026%5C566244.pdf
- **North Kingstown Town Council, 2026-09-14:** item 38, "Discussion concerning Data Center(s)". This is the item the Northeast probe found on the town's own site, now from the portal. https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4122%5C2026%5C565967.pdf

Solar and telecom:
- **Richmond Planning Board, 9/24 and 10/13 (upcoming):**
  - "391 Church Street Solar – Major Change to an Approved Plan";
  - "Charbert Solar 3 – Pre-Application – Major Land Development Project", a "4.5 MW AC/5.625 MW DC solar energy facility" at 299 Church Street, Wood River Junction.
  - https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C3922%5C2026%5C568191.pdf
- **Hopkinton Planning Board, 9/2, 9/8 and 10/7:** Skunk Hill Road Solar, LLC, a major modification and extension, plus a variance from the town's 2019 Non-Residential Photovoltaic Solar Energy Systems Ordinance. https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4514%5C2026%5C567837.pdf
- **Little Compton Planning Board 9/1 and Zoning Board of Review 9/16:** Beacon Solar special use permit, "Solar Energy Systems in Historically Critical Areas", 14 Commons. https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C1494%5C2026%5C566120.pdf
- **Warren Town Council, 2026-10-13 (upcoming):** zoning use-table amendments, including telecommunication antennas on existing structures (2nd reading). https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C3928%5C2026%5C568391.pdf

## RI siting context (brief)

- **State vs. local.**
  - Under the Energy Facility Siting Act (R.I. Gen. Laws ch. 42-98), the Energy Facility Siting Board (EFSB) licenses "major energy facilities", including generating plants of **40 MW or more**.
  - For those, municipal boards (zoning, planning, council) issue *advisory opinions* to the EFSB instead of permits, and the EFSB license stands in for local approvals.
  - **Below 40 MW, siting is local:**
    - zoning use and special-use permits go to the zoning board of review;
    - land-development and subdivision review goes to the planning board under 45-23 (after the 2023 reforms, "unified development review" also lets planning boards decide variances and special-use permits tied to a project; the phrase appears in Warwick's 10/14 agenda);
    - zoning ordinance and map amendments go to the town or city council under 45-24.

    Councils and planning boards therefore carry nearly all of the RI signal (117 of 119 hits).
- **Battery storage** is generally a local zoning matter. The Office of Energy Resources published a **BESS model ordinance** in 2026, with zoning and fire-safety templates for municipalities (https://energy.ri.gov/energy-storage/bess-model-ordinance).
  - Whether a large standalone BESS is a "major energy facility" has been contested. The developer of a 180 MW South Kingstown proposal argued storage does not "generate" (it was withdrawn in 2022; https://ecori.org/2022-1-14-company-pulls-plug-on-proposed-battery-storage-facility-in-south-kingstown/).
  - A **208 MW** BESS in North Kingstown's Quonset Business Park is now before the EFSB as docket SB-2026-02 (https://ripuc.ri.gov/sites/g/files/xkgbur841/files/2026-03/Notice%20of%20Preliminary%20Hearing%20SB-2026-02.pdf).
  - Watch EFSB dockets alongside agendas for projects over 40 MW. Local boards' advisory opinions will still appear on these agendas.
- **Wetlands:** permits come from RIDEM (freshwater) and CRMC (coastal). Municipal conservation commissions are advisory, which fits their low hit count (0 here).
- **Open Meetings Act:** R.I. Gen. Laws 42-46-6(b) requires supplemental written notice "within a minimum of forty-eight (48) hours, excluding weekends and state holidays in the count of hours, before the date of the meeting." The notice must be filed electronically with the Secretary of State, which is why the portal is complete.

## Limitations

1. **Rate limiting.**
   - Cloudflare returned 429 at about 1 request per second (2 of about 220 discovery requests). At 2.5 s spacing it returned 429 five more times during the crawl: once on a gated detail call, which the back-off recovered, and on four agenda-file downloads.
   - The adapter gates its own listing and detail calls (2.5 s; one 90 s back-off and retry on 429).
   - **Agenda-file downloads go through the shared fetcher.** Four PDFs got 429 at 2.5 s, with no back-off, and were fetched on a re-run.
   - **Action for the daily-engine owner:** add a per-host minimum interval of 2.5 s for `opengov.sos.ri.gov` in `fetch.py`, or build the RI fetcher with `min_interval=RISOSAdapter.min_interval`. Daily incremental runs are small (new filings only), but the first 120-day daily backfill of RI will be about 2,000 requests.
2. **Dashboards list only about the 100 most recent past meetings** per body (Providence, Cranston, Pawtucket and Warwick bodies show exactly 100 or 101). That is ample for a 120-day window, but this adapter cannot do deep history.
3. **Only bodies filed under the municipality's parent entity.**
   - Regional bodies are excluded, such as the Pawtucket–Central Falls Joint Planning Commission.
   - So are committees outside the five board keys (see Coverage).
   - The classifier skips names containing committee, advisory, technical review, historic, housing, tax, sewer, water and similar words.
4. **Agenda files only.**
   - Backup packets usually live on town sites, so most hits are agenda-item text.
   - A few towns upload packets or bill lists (Scituate) or draft minutes (Newport Planning Board). This adds context and some noise.
5. **Matcher false positive:** "Solar Salt" (a road-salt product). Suggest an exclusion in `keywords.py`, which I left alone because it is read-only for this task.
6. **Classification calls to review:**
   - "Board of Appeals" bodies in Pawtucket, Glocester and Central Falls are mapped to `zoning_board_of_appeals`. Pawtucket's and Glocester's agendas confirm zoning appeals.
   - "Prudence Island Planning Commission" (Portsmouth) is mapped to `planning_board`.
   - Providence's "City Council as a Whole" is mapped to `select_board`.
7. **`first_seen` comes from the shared fetch cache's timestamp.**
   - This backfill's re-run re-downloaded about 108 portal items that the first pass had cached. The cause is unclear: `fetch.py` has no eviction, so possibly concurrent cache maintenance elsewhere.
   - Those hits' `first_seen` therefore reflects the re-fetch, at most about 35 minutes later.
   - The daily engine's own document index (`data/state/docs/`) should own `first_seen` for RI from here on.
8. **Public announcements** (hearing notices filed outside 42-46-7) are kept and flagged `public_announcement`. None produced a hit in this window.

## Files

- Adapter: `projects/351watch/crawler/watch351/adapters/ri_sos.py`, plus one line in `adapters/__init__.py`.
- Driver: `projects/351watch/crawler/experiments/ri_sos_build.py`.
  - Run with `cd crawler && python3 experiments/ri_sos_build.py discover|crawl [--towns A,B] [--today YYYY-MM-DD] [--offline]`.
- Town config: `projects/351watch/data/towns_ri.json`.
  - 39 rows in the `towns_ma_all.json` shape, plus `state`, `sos_entity_id`, `sos_entity_name`, `sos_dashboard_url` and `untracked_bodies`.
  - Each listing has `platform: "ri_sos"`, `entity_id` and `entity_name`.
- Hits and stats: `projects/351watch/data/agenda_hits_ri.json`.
  - Contains `hits` (ARCHITECTURE.md shape plus RI extras), `lead_time`, per-town status, and counts by topic and board.
- Census input: `projects/351watch/data/ri_census_sub_est2024.csv`.
