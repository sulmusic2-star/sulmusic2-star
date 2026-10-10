# 351 Watch census: how many Massachusetts towns can be monitored automatically

Run on 2026-10-10 against all 351 cities and towns, using the same polite crawler as the 30-town
pilot: identifies as `351WatchBot`, obeys robots.txt, at most 1 request per second per host, no
logins, no challenge solving. Every count here comes from pages the bot actually fetched that day.
Files are listed at the end.

## Headline numbers

| | Towns | % of 351 | Residents (Census 2024 est.) | % of 7.14 M |
|---|---:|---:|---:|---:|
| **Automated** (at least one meeting board with a current, dated agenda listing) | **240** | **68%** | **5.19 M** | **73%** |
| Same, strict (that board shows 2 or more dated agendas) | 233 | 66% | 4.99 M | 70% |
| All four meeting boards automated | 177 | 50% | 3.30 M | 46% |
| Not automated | 111 | 32% | 1.94 M | 27% |

"Current" means at least one agenda for a meeting dated between 120 days ago and 120 days ahead.
A listing whose newest agenda is older than that counts as stale. Town Meeting warrants on their
own do not make a town automated.

**Bot protection is the largest barrier, not missing technology.** 64 of the 111 non-automated
towns (58%, 1.10 M residents) block automated visitors, either on the town site or at their agenda
vendor. Getting them needs the town's or vendor's permission, not more code.

**How much notice do agendas give?** Across 4,116 first postings in 103 towns (Apr 13 to Oct 9,
2026), the median agenda went up **5 days** before the meeting. The 10th percentile was **2 days**,
or about 33 hours before the meeting day began. 94% were up at least 24 hours before the meeting
day began. A daily crawl therefore catches nearly every agenda before its meeting.

**Check against the pilot.** The fully automatic discovery reproduces the hand-built pilot
result: the same 24 of the 30 sample towns are automated. The same 6 are not (Becket, Middleborough
and Barnstable on Cloudflare, Framingham on its agenda vendor, Medway on HeyGov, Worthington with
no agendas online). The census reasons for the 6 are more specific than the pilot's. Framingham links three agenda
stores, and all three refuse the bot: iQM2 answers 429, and both Granicus and its Laserfiche
WebLink disallow bots in robots.txt.

## 1. The 351 municipalities

- The list comes from the Census Bureau's Vintage 2024 sub-county estimates: the 351 county
  subdivisions with state FIPS 25, which together sum exactly to the state's 7,136,171 people.
- Websites come from the Massachusetts Municipal Association directory (`mma.org/community/<town>`,
  all 351 entries). They were cross-checked against Wikidata P856. Wikidata lacked 23 towns and
  pointed somewhere else for 94 more. Most of those are older domain aliases; Amherst's points at a
  tourism site.
- Every site was fetched over https first, then http. A site was verified when it answered and its
  page named both the town and Massachusetts. Parked domains and tourism sites were rejected.
- Results: 295 sites verified. 36 serve a Cloudflare challenge. 12 return a firewall 403
  (Akamai or Cloudflare "Access Denied"). 7 disallow us in robots.txt or ask for a crawl-delay we
  don't honor. One site (Abington) answered without naming the town. 350 websites came from MMA,
  and one was found by a checked guess (Monroe, monroema.org).
- Output: `data/ma_municipalities.json`, which includes the 2020 base and 2024 estimate, county,
  form of government and the per-URL check log.

## 2. Coverage by platform

| Platform (automated towns) | Towns | Residents | How it is read |
|---|---:|---:|---|
| CivicPlus AgendaCenter | 187 | 3.40 M | AgendaCenter search page per town: every tracked category, dated, with "Posted" times |
| Plain listing pages (Revize, WordPress, RocketFusion, CivicPlus Archive Center, Drupal...) | 96 (44 as main platform) | 1.61 M | generic adapter on discovered per-board or all-boards pages |
| CivicClerk | 7 | 0.32 M | public read-only OData API (`<tenant>.api.civicclerk.com`), with publish times |
| Legistar (Boston, Somerville) | 2 | 0.76 M | public Web API for the calendar plus each meeting's detail page. The agenda PDFs are on a robots-disallowed host |

Town counts overlap because 52 towns use two platforms, for example AgendaCenter for most boards
and a plain page for one.

**CMS of the 297 sites that could be read:** CivicPlus 214, WordPress 25, Revize 23,
RocketFusion 11, Drupal 4, other or unidentified 24. A few sites match two signatures. CivicPlus dominates. 195 sites have an
AgendaCenter, and 187 of those have current agendas for tracked boards.

Two new pieces were needed to reach this coverage:

- A **Legistar adapter**, which adds Boston (673k residents) and Somerville.
- A **discovery engine** (`watch351/discover_census.py`). It probes AgendaCenter and CivicClerk,
  follows homepage links to "Agendas & Minutes" and board pages, and keeps a listing only when it
  shows dated agendas.

## 3. Coverage by board

| Board | Towns automated | % of applicable | Strict (2+ agendas) | Residents covered |
|---|---:|---:|---:|---:|
| Planning Board | 224 | 64% of 351 | 215 | 3.95 M |
| Zoning Board of Appeals | 194 | 55% | 177 | 4.35 M |
| Conservation Commission | 221 | 63% | 213 | 3.95 M |
| Select Board / City or Town Council | 225 | 64% | 220 | 4.83 M |
| Town Meeting warrant posted online and found | 92 | 32% of the 292 Town Meeting towns | - | 1.23 M |

The ZBA trails the other boards for two reasons. Small towns often post ZBA hearings as legal
notices rather than agendas. Some ZBAs also met less often than every 120 days, and those count as
stale here. Warrants are the weakest category: 92 of 292 were found, often as PDF links on a "Town
Meeting" page, with no posting time.

**By town size:** under 2,000 residents, 32 of 63 are automated (51%). From 10,000 to 50,000, 122
of 158 are (77%). Over 50,000, 17 of 27 are (63%). Several big cities sit behind vendor or
firewall blocks.

## 4. Not automated: 111 towns, 1.94 M residents

| Reason (precise reason per town in `towns_ma_all.json`) | Towns | Residents | Examples |
|---|---:|---:|---|
| Town website bot protection: Cloudflare challenge (36) or firewall 403 (11, Akamai on Newton, Arlington, Dedham, Westwood, Edgartown) | 47 | 761k | Brookline, New Bedford, Newton, Arlington, Chelsea, Danvers, Barnstable, Marblehead |
| Agenda vendor bot protection: MyTownGovernment (`mytowngovernment.org`, Cloudflare)* | 14 | 80k | Chatham, Athol, Orange, Dalton, Pelham, Norfolk, Templeton |
| robots.txt: town site disallows all but named search engines (Easton, Barre, Palmer, New Braintree, Westhampton), or disallows its meeting-calendar path (Cummington), crawl-delay 20 s above our 10 s cap (Harwich, Watertown), vendor disallows (Worcester on PrimeGov, Hopkinton on Granicus, Williamstown on SharePoint) | 11 | 337k | Worcester (211k), Watertown, Easton |
| Agenda vendor refuses automated requests: iQM2 / Granicus Meeting Portal answers HTTP 429 to the first request | 3 | 255k | Cambridge, Framingham, Revere |
| JavaScript-only listing: HeyGov, whose API robots.txt disallows all bots (4); CivicLive (Lynn); CivicPlus Document Center folders (Ashfield, North Reading, Westminster); Foxborough | 9 | 170k | Lynn (103k), Medway, Cheshire |
| Documents in a store with no adapter: Google Drive folders (Everett, West Springfield, Windsor, New Ashford); Laserfiche WebLink (North Andover, Reading) | 6 | 140k | Everett, West Springfield, North Andover |
| No current, dated agenda listing found: listing stale for over 120 days (Stoneham, Douglas, Georgetown), links undated, agendas posted only physically or as minutes (Worthington), or a heuristic miss | 21 | 199k | Peabody, Greenfield, Acton, Groton, Millis |

\* The MyTownGovernment towns link an `http://www.` alias that answers without the challenge. Using
it would sidestep the vendor's bot protection, the same call the pilot made for Barnstable's legacy
host, so it is not used.

Bot and firewall protection (the first two rows plus the iQM2 429s) accounts for **64 towns and
1.10 M residents**. The firewall and vendor blocks may key on our cloud egress IP rather than the
User-Agent, so a production crawler on a fixed, allow-listed address could fare better. That is
untested; the census did not change its UA or IP to find out.

## 5. Lead time: when agendas appear relative to the meeting

**Method.**

- **CivicPlus AgendaCenter** prints "Posted <date time>" on each agenda row. After an edit it prints
  "Amended <date time>" instead, which replaces the original time.
- **CivicClerk's** API gives `publishOn` per agenda file and the scheduled start time.
- **Revize** stamps every document link with its upload time (`?t=YYYYMMDDhhmmss`), a proxy that
  changes on re-upload.
- **Legistar** gives only the last republish time, usually after the meeting, so it is excluded.
- One request per town (CivicPlus) or a few (CivicClerk) collected a year of rows during discovery.
  The analysis uses meetings already held, Apr 13 to Oct 9, 2026, so future meetings whose agendas
  aren't posted yet don't bias the result.
- "Days" = meeting date minus posting date. "Hours" = posting time to 00:00 on the meeting day.
  That is a lower bound: most of these boards meet in the evening, which adds about 17 to 19 hours.

**First postings** (CivicPlus "Posted" rows plus CivicClerk). These are the clean measure:
4,116 agendas, 103 towns.

| Board | Agendas | Towns | 10th pct | Median | 90th pct | Up ≥48 h before meeting day | ≥24 h | Posted on/after meeting day |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Planning Board | 873 | 96 | 2 d (37 h) | 5 d | 13 d | 88% | 96% | 3% |
| Zoning Board of Appeals | 608 | 93 | 2 d (36 h) | 7 d | 21 d | 85% | 96% | 3% |
| Conservation Commission | 862 | 95 | 2 d (33 h) | 5 d | 8 d | 77% | 94% | 4% |
| Select Board / Council | 1,748 | 99 | 2 d (32 h) | 4 d | 7 d | 82% | 93% | 5% |
| **All boards** | **4,116** | **103** | **2 d (33 h)** | **5 d** | **13 d** | **82%** | **94%** | **4%** |

- **Per town:** the median of each town's median is 5 days. The 10th percentile town median is
  4 days.
- **Exact hours** (CivicClerk, 331 agendas in 10 towns, to the scheduled start): 10th percentile
  49 h, median 121 h.
- **All rows** (6,183 agendas in 197 towns, including Amended and Revize upload stamps): median
  4 days, 10th percentile 0 days, 72% up at least 48 h before the meeting day. Edits close to the
  meeting pull this down, so read it as a lower bound. CivicPlus towns that hide the original
  "Posted" time (about 45% of them) only appear here.
- **Town Meeting warrants:** only 25 timed postings. Median 12 days, but a quarter of the rows
  were posted or amended after the meeting began, because some towns re-post the final warrant.

**What it means for alerts.** Massachusetts Open Meeting Law requires notice 48 hours ahead,
excluding weekends and holidays. Boards are already posting on time, and usually days early. ZBA
agendas come earliest, a median of a week ahead, because hearings are noticed in advance. Select
board agendas come latest. A crawl every 24 hours alerts before about 94% of meetings. A crawl
every 6 hours would also catch most of the remaining 2-to-24-hour late postings. The roughly 4%
that first appear online on the meeting day or afterward were likely uploaded after the official
notice went up at town hall. The website can't give advance warning for those.

## 6. Crawl of every automated town: last 30 days and next 60 days

The run covered meetings dated Sep 10 to Dec 9, 2026, across all 240 automated towns. That is 292
crawl configs, because some towns use two platforms. OCR was limited to the first 6 pages of
image-only PDFs. The crawl took about 17 minutes. Most of that time went on OCR and the 1 request
per second per host limit.

| | |
|---|---:|
| Agenda documents listed / fetched and scanned | 2,535 / **2,524** |
| Image-only scans (no text layer) / recovered by OCR | 641 (25%) / 639 |
| Documents that failed | 11: 3 over the 40 MB cap, 4 in formats with no extractor (.doc, .pptx, .jpg), 2 HTTP errors (404/403), 2 others |
| Towns with zero agendas in the window | 5: Brockton, Haverhill, Needham, Richmond, and Oak Bluffs (connection reset) |
| **Topic hits** | **882 in 168 towns** (pilot: 178 hits in 24 towns) |
| Hits for meetings on or after Oct 10, i.e. still actionable | 135 in 67 towns |

| Topic | Hits | Towns |
|---|---:|---:|
| Zoning / bylaw amendment | 357 | 106 |
| Solar | 235 | 76 |
| Battery storage | 142 | 55 |
| 40B / comprehensive permit | 115 | 43 |
| Moratorium | 77 | 36 |
| Consolidated permit / 225 CMR 29 / clean energy infrastructure | 55 | 27 |
| Wireless / telecom siting | 36 | 26 |

- **By board:** Select Board/Council 340, Planning Board 263, Town Meeting warrants 164, ZBA 72,
  Conservation Commission 43.
- **By text source:** PDF text 674, OCR 174, HTML 26, DOCX 8.
- **Most hits:** Whately 43, Harvard 37, Pittsfield 32, Wellesley 30, Plymouth 29, Yarmouth 22,
  Westford 20, Milton 19, Leominster 18, Easthampton 18. Per-town counts by topic are in
  `hits_by_town`.

**Upcoming items the pilot could not see** (all from towns outside the 30-town sample unless
noted). Source links are in `agenda_hits_ma_all.json`.

- **Battery storage.**
  - Lakeville Planning Board, 10/22: new zoning section §270-12 for battery energy storage systems,
    with Tier 1 to 3 permitting and a noise study.
  - Somerset ZBA, 10/15: Somerset Energy Storage LLC petition for a commercial BESS at 1606
    Riverside Ave.
  - Egremont Planning Board, 10/16: BESS draft bylaw.
  - Westfield City Council, 10/15: petition for clean-energy and BESS zoning (pilot town).
  - Also on agendas: Middlefield ConCom and Swansea ConCom, plus Rochester, Carver, Wellesley and
    Leominster.
- **Data-center moratoria** spreading beyond the pilot:
  - Northfield Planning Board, 10/20 and 10/27: drafting a moratorium on data storage centers.
  - Boxborough Planning Board, 10/13: town counsel's feedback on a data-center moratorium.
  - Leyden Planning Board: "AI data center moratorium?"
  - Pittsfield and Northampton, already known from the pilot.
- **Clean-energy consolidated permitting (225 CMR 29).**
  - Middleton, Mattapoisett and Halifax select boards, 10/13: votes to adopt the DOER consolidated
    permit process and designate a local government representative.
  - Harvard's 10/20 Special Town Meeting warrant: a new solar and BESS siting bylaw with
    consolidated permitting.
  - Leyden Planning Board, 10/14.

Precision is the same as in the pilot. A few percent of hits are false positives, and bylaw-amendment
hits include general bylaws on purpose. Spot-check before publishing.

## 7. Honest gaps

1. **Discovery is heuristic.** It follows homepage links, board pages and one level of "Agendas"
   subpages, with a budget of 28 pages per town.
   - 21 towns land in "no current, dated listing found". Some of them do post agendas: Peabody,
     Greenfield and Acton are worth a manual look.
   - 7 automated towns rest on a single dated link.
   - Hand-curated listings would lift both numbers.
2. **Precision of plain-page listings.** The roughly 130 generic board listings were spot-checked by
   eye, and the false matches found were removed: other boards' agendas on shared pages, calendar
   exports, single-meeting pages. A few remaining listings may still pick up another board's agenda.
   CivicPlus, CivicClerk and Legistar listings are structured and reliable.
3. **"Automated" means a current listing was found.** It does not mean every document was parsed.
   Scanned PDFs need OCR, which is limited to 6 pages here. Some documents fail to download (see
   the crawl errors).
4. **Stale listings get no grace period.** A board that has not met in 120 days counts as not
   automated. That understates small-town ZBAs.
5. **Year-specific folders.** CivicPlus Archive Center and some Revize pages use year folders, for
   example "2026 Agendas". The listing will need refreshing in January. Re-running discovery
   monthly handles it.
6. **Blocks are point-in-time.** iQM2's 429s, Cloudflare challenges and robots 5xx responses
   (RFC 9309 says to treat them as disallow) can change. Roughly 64 towns need the vendor's or
   town's permission or an allow-list.
7. **Lead time covers platforms that publish a timestamp.** That is 103 towns for clean first
   postings, and those are mostly CivicPlus. Towns on plain pages have no posting time, and they
   may post later.
8. **Boston is partial.** Only the City Council and the ZBA are on Legistar. The BPDA and
   Conservation Commission agendas are on boston.gov and were not found.

## Files

- `projects/351watch/data/ma_municipalities.json`: 351 towns, population, website, verification log.
- `projects/351watch/data/towns_ma_all.json`: per town: platform(s), crawlable listings,
  board evidence (counts, latest agenda, examples), vendors seen, `reason_code` and `reason` when
  not automated. It uses the same schema as `towns.json`.
- `projects/351watch/data/leadtime_ma_all.json` (stats and per-agenda records) and
  `leadtime_rows_ma_all.json` (raw platform timestamps).
- `projects/351watch/data/agenda_hits_ma_all.json`: crawl output.
- `projects/351watch/data/ma_census_summary.json`: every table above as JSON.
- Sources kept for reproducibility: `ma_census_sub_est2024.csv` (Census) and
  `ma_wikidata_snapshot.json`. Both were downloaded once by hand: www2.census.gov's robots.txt
  parses as disallow-all under a strict reading, and query.wikidata.org disallows `/sparql`, so
  the bot does not fetch either.
- Code: `crawler/watch351/ma_census.py` (CLI: `python3 -m watch351.ma_census
  municipalities|discover|leadtime|crawl|report`), `discover_census.py`, `adapters/legistar.py`.
  The pilot CLI (`run.py`) and the 30-town files are unchanged.
