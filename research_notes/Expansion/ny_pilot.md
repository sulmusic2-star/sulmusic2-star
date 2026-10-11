# 351 Watch: New York pilot

Run dates: 2026-10-10 to 2026-10-11. Crawl window: meetings from 2026-08-27 to 2027-01-09 (45 days back, 90 days ahead).

**Question:** can 351 Watch read New York town agendas well enough to alert developers and land-use lawyers about battery storage (BESS), solar, data-center and land-use siting items before the meeting?

**Short answer:** yes, for about 60% of the towns that are actually fighting over BESS and data centers.

- **Coverage.** 34 of 57 targeted towns are automated.
  - 19 run on stock adapters: CivicPlus, CivicClerk, or stock `generic` listings.
  - 15 use the new `generic_ny` adapter: 14 as their main platform, plus Hempstead's ZBA.
  - Southampton uses the new `escribe` adapter.
- **Signal.** The crawl found 53 keyword hits in 18 towns. About 35 are real energy or data-center siting items. Among them:
  - BESS local laws (Geneva, Marcellus, Stanford);
  - a BESS moratorium extension (Bedford);
  - data-center moratoria (Marcellus, Lysander);
  - a BESS setback variance (Clay).
- **Blockers.**
  - Cloudflare challenges cost 7 towns, including Brookhaven and Islip, two of the largest Long Island towns.
  - Robots crawl delays over our 10-second cap cost 3 more: Huntington, Cicero and Lansing.
  - No agenda is posted online at all in 5 towns.
- **Lead time.** Where a platform shows a true first-posting stamp (CivicPlus "Posted"), agendas go up a median of **3.3 days** before the meeting day. About 91% are up at least 72 hours before a 7 pm meeting. That is consistent with NY's 72-hour meeting-notice rule, which governs the notice, not the agenda.

## What was run

- **Glue script:** `projects/351watch/crawler/experiments/ny_pilot.py`, with subcommands `get`, `discover`, `curate`, `listings` and `crawl`.
  - It reuses `watch351` unchanged: `PoliteFetcher`, `discover_census.discover_municipality`, the CivicPlus, CivicClerk and generic adapters, `crawl.scan_document` (PDF, DOCX, HTML and tesseract OCR) and the keyword matcher, which now includes `data_center`.
  - The New York differences are patched into the running process only, never into the package:
    - "Town Board" → `select_board`;
    - "Conservation Advisory Council/Board", "Environmental (Conservation) Commission" and "CAC" → `conservation_commission`;
    - `*.ny.us` host roots;
    - the CivicClerk tenant probe uses `<town>ny`, not `<town>ma`.
- **New adapters.** These are the only package changes: two new files, plus one appended registration line in `adapters/__init__.py`.
  - `crawler/watch351/adapters/generic_ny.py`: hand listings with features NY sites needed:
    - month-paged listings (`{m}`/`{y}`);
    - per-page-load cache-busters stripped (`?tmstv=`);
    - compact file-name dates (`a10082026pb_0.pdf`);
    - board rules for pages that mix boards;
    - section-scoped tables;
    - year-less row dates;
    - site-specific date regexes;
    - "document date" and Revize `?t=` upload stamps kept for lead time.
  - `crawler/watch351/adapters/escribe.py`: eSCRIBE published-meetings portals, read from the upcoming-meetings list on the portal home page.
- **Data files:**
  - `data/towns_ny.json`: 57 towns, in the same row shape as `towns_ma_all.json` plus `state`, `agenda_platform`, `selection_reason`, `selection_source_url` and curation notes.
  - `data/agenda_hits_ny.json`: hits in the ARCHITECTURE.md hit shape, plus per-town status, every document scanned, posting stamps and lead-time statistics.
- **Politeness.** Every request went through `PoliteFetcher`:
  - 351WatchBot UA;
  - robots.txt checked on every redirect hop;
  - at most 1 request per second per host;
  - hosts asking for a crawl delay over 10 s were skipped;
  - no logins;
  - no challenge was solved;
  - TLS verification was never disabled.

  One judgment call is flagged under Southampton below.

  `first_seen` is our own fetch time, taken from the fetch-cache timestamp. The shared `data/first_seen.json` ledger was not written.
- **Search budget:** 8 web searches; everything else was direct fetches.

## Town selection (57 towns)

- **Source 1: Carina Energy's BESS Moratorium Monitor** (https://carina.energy/bess-moratoriums/).
  - On 2026-10-10 it listed 128 NY jurisdictions. New York has about 65% of all US BESS moratoria; the March 2026 release counted 98.
  - Chosen from it: towns with ACTIVE moratoria, especially those expiring between October 2026 and 2027, where an extension or a permanent BESS law is likely on an upcoming agenda.
- **Source 2: 2026 town hearing notices and news.**
  - BESS laws: Clay LL4, Marcellus LL C, Geneva LL5, Amherst ZTA-2026-01, Leyden, Corinth, Stony Point, Horicon, Beekman and Warwick.
  - Data-center moratoria: Brookhaven Intro LL 11, Clifton Park, Concord LL4, Cicero LL2, York LL3, Winfield LL2, Highland, East Fishkill's three-year freeze, East Greenbush, and Lansing's Cayuga plant fight.
- **Carry-overs:** the 4 NY towns from the Northeast feasibility pilot (Clay, Lysander, Dover, Claverack).
- **By region:** Long Island 10, Westchester/Putnam/Rockland/Orange 8, Mid-Hudson 10, Capital Region/Mohawk/North Country 14, Central NY/Finger Lakes 10, Western NY 5.
- **Recorded per town:** the reason and source URL are in `towns_ny.json` (`selection_reason`, `selection_source_url`).
- **One substitution:** Chester (Orange County) was replaced by Warwick (Orange County, draft BESS law rev. 2026-06-30). Chester's guessed domain returns "Web Site not found", and `townofchesterny.org` redirects to Chester in Warren County.

## Results

| | |
|---|---|
| Towns tried | 57 |
| Automated | **34 (60%)**; 33 had at least one agenda dated in the window (Putnam Valley's newest was 8/19) |
| Boards with agendas in the window | Town Board 29 towns, Planning Board 25, ZBA 23, CAC/Conservation Board 4 |
| Agenda documents scanned | 215. Of these, 28 (13%) were image-only scans recovered by OCR |
| Keyword hits after dedupe | **53 in 18 towns**. 8 are for meetings not yet held at crawl time |
| Hits by topic | solar 22, battery_storage 16, moratorium 9, wireless_telecom 7, data_center 5, zoning_amendment 2 |
| Hits by board | Town Board 38, Planning Board 9, ZBA 5, CAC 1 |

**Precision (manual read of all 53 hits):**

| Category | Hits | Details |
|---|---|---|
| Energy or data-center siting | about 35 | BESS laws and moratoria, data-center moratoria, solar site plans, BESS variance. 3 of these are Babylon's EV-charging zoning text, which includes a BESS ban clause |
| Wireless siting | 7 | |
| Municipal solar procurement | 4 | Kent, Oyster Bay |
| Other land use | 3 | Stony Point housing moratorium, Cortlandt housing rezoning, Wilton lighting code |
| Noise | 4 | 3 are Wilton ZBA site-plan drawings where OCR'd "PV/PVC" labels matched `solar`; 1 is a fee schedule |

**Data-center hits:** 5 in 2 towns (Marcellus, Lysander). All 5 carry the new `data_center` topic. Before it existed, such items surfaced only when they also said "moratorium".

### Platforms (34 automated towns)

| Platform | Towns | Notes |
|---|---|---|
| Hand listings via `generic_ny` (new) | 15 | <ul><li>WordPress: Oyster Bay, Putnam Valley, Warwick, Stanford</li><li>Revize: Milton, Geneva, Penfield</li><li>custom CMS: Stony Point, Wilton, Corinth, Leyden, Concord</li><li>Concrete CMS: Aurora</li><li>Drupal: Lysander</li><li>Hempstead's ZBA hearing pages</li></ul> |
| Stock `generic` (discovered or hand) | 8 | Cortlandt, Beekman, East Fishkill, Clifton Park, East Greenbush, Amsterdam, Clay, Marcellus |
| CivicPlus AgendaCenter | 7 | Southold, Hempstead, Babylon, Bedford, Kent, Claverack, Glenville |
| CivicClerk (public API) | 5 | North Hempstead, Smithtown, Dover, Amherst, and Southold's Town Board |
| eSCRIBE (new `escribe` adapter) | 1 | Southampton |

CivicPlus and CivicClerk together are the primary platform in only 11 of 34 towns, against about 80% in Massachusetts. NY coverage depends on per-town hand listings: about 10 to 20 minutes per town, and they break when a site is redesigned. The two NY-specific blockers by count are Cloudflare and robots crawl delays.

### Not automated (23), with precise reasons

| Reason | Towns | Detail |
|---|---|---|
| Cloudflare bot challenge | 7 | Islip, Brookhaven, Hurley, Wawarsing, Halfmoon, Duanesburg, Horicon. "Just a moment..." (HTTP 403) on the town site. Not bypassed. Brookhaven's data-center moratorium is invisible to us |
| robots.txt Crawl-delay over the 10 s cap | 3 | Huntington (15 s), Lansing (15 s), Cicero (20 s). All three could be automated at 1 request per 15 to 20 s if the cap is raised |
| No agendas online | 5 | <ul><li>Highland: minutes and meeting-notice news posts only</li><li>Berne: resolutions and minutes</li><li>Winfield: minutes only</li><li>Camillus: calendar events carry no files</li><li>York: Wix pages with schedules and forms only</li></ul> |
| JavaScript-only document module | 3 | Perth, Spafford, Boston. All three share one JS-built "agendasandminutes" CMS module, with no links or dates in the server HTML. One adapter for that vendor's JSON would open all three |
| Vendor robots disallow | 2 | <ul><li>New Castle: agendas hosted on eCode360 `/documents/`, disallowed for all agents</li><li>Gardiner: HeyGov widget, and `api.heygov.com` robots disallows all</li></ul> |
| TLS certificate mismatch | 1 | Carmel: `carmelny.org` certificate is not valid for the host. Skipped; TLS verification is never disabled |
| Undecodable response | 1 | Livingston: Sucuri and Cloudflare front end returns a non-HTML body to 351WatchBot |
| WAF 403 | 1 | Newfane: HTTP 403 on every request |

**Partial coverage inside automated towns:**
- **East Fishkill:** Town Board agendas moved to Granicus, whose robots.txt disallows us. Only the ZBA is read.
- **Southampton:** ZBA is not on eSCRIBE.
- **Hempstead:** Planning Board page lists members only.
- **Milton:** Planning Board only; the Town Board folders hold minutes and resolutions.
- **Stony Point:** Town Board only.
- **Oyster Bay:** has no Planning Board; the Town Board decides site plans.
- **Files over the 40 MB cap were skipped:**
  - Kent Town Board 10/6 agenda;
  - Cortlandt Planning Board 10/6 packet;
  - Glenville P&Z 10/19.

**Flag for review: Southampton (eSCRIBE).**
- eSCRIBE's PDF downloads (`FileStream.ashx`) answer HTTP 403 with a "Verifying your browser" page. That challenge was not solved.
- The portal's own HTML agenda view (`Meeting.aspx?Id=…&Agenda=Agenda`) is linked on the portal as "Agenda (HTML)" and served normally. The adapter reads that view instead (listing option `"format": "html"`).
- This is the same host and the canonical agenda, not an alias. It is still a judgment call. To be strict, drop the three Southampton listings; the town then falls to "vendor challenge".

## Notable real hits

**Top 5:**

1. **Geneva (Ontario Co.) Town Board, 2026-10-13 (upcoming):** Resolution 68-2026, "Adopting Local Law No. 5 of 2026, Battery Energy Storage Systems". Resolution 70-2026 adopts Local Law 6 amending the solar code. The 9/8 agenda held the public hearings on both laws. We first saw the agenda 2.0 days before the meeting.
   https://townofgenevany.gov/Documents/Departments%20and%20Services/Agendas%20&%20Minutes/Town%20Board%20Meeting%20Agendas/2026.10.13%20Town%20Board%20Meeting%20Agenda.pdf
2. **Marcellus (Onondaga Co.) Town Board, 2026-10-07:** public hearings on Local Law C of 2026, "Battery Energy Storage Systems", and on Local Law E of 2026, a "Twelve (12) Month Moratorium on Commercial Cryptocurrency Mining Operations, Data Mining, Data Processing Centers, and Data Storage Facilities". The 9/2 agenda carried the introductory resolution and EAF, and the 9/16 agenda carried both laws.
   https://townofmarcellusny.gov/wp-content/uploads/2026-10-7-agenda.pdf
3. **Clay (Onondaga Co.) Zoning Board of Appeals, 2026-10-12 (upcoming at crawl):** a Highway Overlay setback variance "from 115 feet to 10.3 feet for the development of BESS equipment", I-1 district. First seen 1.3 days ahead.
   https://townofclayny.gov/sites/default/files/2026-10/Zoning%20Board%20Agenda%20-%20October%2012%2C%202026.pdf
4. **Lysander (Onondaga Co.) Town Board, 2026-10-01:** sets a 2026-11-05 public hearing "to extend the moratorium on data centers in the Town of Lysander". The 9/3 work session listed "Battery Energy Storage Code".
   https://lysanderny.gov/sites/default/files/2026-10/10-1-2026_agenda.pdf
5. **Bedford (Westchester Co.) Town Board, 2026-09-08:** "Public Hearing On A Local Law Extending The Moratorium On Large Scale Battery Energy Storage Systems In The Town Of Bedford For 6 Months".
   https://www.bedfordny.gov/AgendaCenter/ViewFile/Agenda/_09082026-398

**Also notable:**

- **Stanford (Dutchess Co.) Town Board:**
  - 9/9 and 9/10: "Battery Storage Moratorium Extension" resolution (https://stanfordny.gov/download/10934/).
  - 10/5 workshop: schedules the "Public Hearing on proposed Local Law #4 – Battery Energy Storage Systems" for the October meeting (https://stanfordny.gov/download/11000/).
- **Babylon (Suffolk Co.) Town Board, 9/9:** a proposed EV-charging-station zoning law includes "Battery energy storage systems shall be prohibited" (at EVCS sites). https://www.townofbabylonny.gov/AgendaCenter/ViewFile/Agenda/_09092026-907
- **East Greenbush Conservation Advisory Council, 9/28:** "Report on large-scale Grid-tied Battery Energy Storage Systems", with next steps for a report to the Town Board. This is the town that is weighing a data-center moratorium.
- **Solar site plans:**
  - Geneva Planning Board, 9/15: site plan extension for a 2.47 MW AC ground-mounted solar farm (Geneva PV, LLC).
  - Milton Planning Board, 9/9: "Milton Solar – Special Use Extension".
  - Penfield Town Board, 9/16: Green Spark Solar sidewalk waiver.
  - Claverack Planning Board, 10/5: ground-mounted solar trackers.
- **Wireless siting:**
  - Clay Planning Board, 10/14 (upcoming): Moyers Corners cell tower site plan.
  - Southold Planning Board, 10/5: Laurel Stone cell tower special-exception renewal.
  - Oyster Bay ZBA, 9/24: wireless facility special use permit.
  - Southampton Town Board, 10/13: small-wireless special-permit waiver notice.

**Known items missed:**
- **In window but unreadable** (blocked or not posted online):
  - Brookhaven's data-center moratorium (Cloudflare);
  - Huntington's and Islip's BESS moratoria (crawl delay, Cloudflare);
  - Cicero's and Lansing's data-center fights (crawl delay);
  - Winfield's and York's data-center moratoria (no agendas online);
  - Halfmoon's BESS moratorium (Cloudflare).
- **Before the window:** the July 2026 data-center hearings in Clifton Park and Concord.

## Posting lead time

Lead time is measured from a timestamp to 00:00 of the meeting day. Most NY town boards meet between 6 and 7:30 pm, so the figures are underestimates. "≥72 h" below means at least 2.21 days before midnight, which is at least 72 hours before a 7 pm meeting.

| Source | n | Median (days) | Share at least 72 h before a 7 pm meeting | Note |
|---|---|---|---|---|
| **CivicPlus "Posted" stamps** (first posting), past 365 days | 80 | **3.3** | **91%** of pre-posted | <ul><li>**Hempstead:** 18 of 18 posted 3.2 to 5.3 days ahead, median 3.3. The Thursday-or-Friday posting for a Tuesday meeting matches the 72-hour rule</li><li>**Southold:** median 2.6, with 91% at least 72 hours</li><li>**Bedford:** median 3.3; 26% of its stamps fall after the meeting day (uploads made after the fact)</li></ul> |
| Platform stamps on documents in the crawl window (mixed kinds) | 62 | 3.4 | 72% | Includes CivicClerk and Revize re-publish stamps, and Milton's "document date" (12 days ahead for 10/14) |
| CivicClerk `publishOn` | 206 | −0.7 | n/a | **Not a first-posting time.** 47% fall after the meeting day; Amherst's median is 54 days after, because files are re-published with minutes. Dover (median 5.3) and Smithtown use it closer to posting |
| Revize `?t=` upload stamps | 144 | 1.3 | 58% of pre-posted | Last upload. 22% fall after the meeting (Geneva re-uploads agendas with adopted resolutions) |
| PDF ModDate/CreationDate proxy | 99 | 4.4 | 63% | When the file was last saved, not posted |
| Our own first fetch, upcoming meetings | 8 | 2.0 | n/a | Bounded by when this pilot ran. A daily crawl would see agendas as soon as they post |

**Takeaways:**
- In NY towns that publish posting stamps, the alert window is roughly **3 days**. The 10th percentile is 0.6 days, and about 1 in 9 agendas are posted less than a day ahead.
- Daily crawling is the minimum. A twice-daily crawl on Thursday and Friday would catch most Monday-to-Wednesday meetings with 3 or more days of notice.
- The longer runway for developers and lawyers comes from the legislative sequence rather than the agenda (see below). Those steps show up as agenda items weeks before adoption:
  1. the introductory resolution;
  2. setting the public hearing;
  3. the county 239-m referral;
  4. the hearing;
  5. adoption.

  For example: Marcellus 9/2 → 9/16 → 10/7, Geneva 9/8 → 10/13, Lysander 10/1 → 11/5.

## New York legal context (brief)

- **Open Meetings Law notice.** Public Officers Law §104:
  - For a meeting scheduled at least a week ahead, notice of the time and place goes to the news media and is posted publicly at least 72 hours before.
  - Other meetings get notice "to the extent practicable" at a reasonable time beforehand.
  - Notice must also be posted on the body's website if it has one.
  - The OML does not require an agenda.

  Under §103(e), records scheduled to be discussed, such as proposed local laws and resolutions, must be available on request, and posted online if the agency keeps a regularly updated website, "to the extent practicable" at least 24 hours before the meeting. So the legal floor for agenda content online is 24 hours and best-efforts. Observed practice where stamps exist is about 3 days.
- **How towns adopt local laws, including moratoria and BESS or data-center laws.** Municipal Home Rule Law §20:
  1. The bill must be in final form on members' desks at least 7 calendar days, excluding Sundays, before passage (or mailed or emailed 10 days ahead). The chief executive can certify necessity to bypass this, with a two-thirds vote.
  2. A public hearing is required, on at least 3 days' notice if a local law sets it, otherwise 5 days.
  3. The adopted law is filed with the Secretary of State and takes effect on filing.

  Zoning amendments and most moratoria also go through:
  - Town Law §264/265: a hearing with notice published in the official newspaper at least 10 days ahead;
  - General Municipal Law §239-m referral to the county planning agency, which has 30 days to respond (a county disapproval forces a supermajority vote);
  - SEQRA review.

  Each step generates its own agenda item ("introductory resolution", "set public hearing", "SEQR determination", "adopt Local Law No. X of 2026"). This is why the Town Board is the highest-yield board in NY: 38 of 53 hits.
- **Who decides siting.**
  - Executive Law §94-c (ORES, now within DPS) sites **major renewable energy facilities of 25 MW or more**; projects of 20 to 25 MW may opt in.
  - ORES may waive local laws it finds unreasonably burdensome, so for large solar the local fight is mostly about the local-law record and host-community agreements.
  - Solar under 25 MW, which includes all community solar (about 5 MW AC or less), is sited **locally**: special use permit, site plan, ZBA variances.
  - **Standalone BESS is sited locally at any size** under local zoning and SEQRA, plus the State Fire Code. Storage co-located with an ORES-jurisdiction facility goes with that facility.
  - Standalone systems over 80 MW may also need PSC review under PSL §68 (per a Hodgson Russ CLE deck).
  - Bill S7834 (2023) proposed moving standalone storage over 5 MW to ORES; we did not confirm whether it was enacted.

  This local jurisdiction is why BESS moratoria cluster in NY (Carina: 128 NY rows), and why town agendas are the authoritative early-warning source for BESS and data centers. Data centers are ordinary local land uses with no state siting override.

## Gaps and recommendations

1. **Bot walls and crawl delays (10 of 23 failures).** Raising the crawl-delay cap from 10 s to 20 s for a nightly run would add Huntington, Lansing and Cicero at no politeness cost. Cloudflare towns need the town's permission or an allow-listed UA.
2. **Hand listings are fragile.** 22 of 34 automated towns depend mainly on hand-written or discovered page listings (`generic` or `generic_ny`), plus Hempstead's ZBA.
   - Add a weekly "listing still returns dated agendas" check.
   - Prioritize adapters for the clusters seen:
     - the JS "agendasandminutes" CMS: Perth, Spafford, Boston;
     - Revize document centers: Milton, Geneva, Penfield, East Greenbush;
     - WordPress Download Monitor: Stanford.
3. **The 40 MB cap** skipped three packets (Kent, Cortlandt, Glenville). NY towns post full packets as agendas. Consider streaming the first N pages instead of skipping.
4. **Precision.** `solar` matched "PV" on OCR'd site-plan drawings (Wilton). Requiring a word context for bare "PV" in OCR text would remove that noise.
5. **Board labels are town-defined:**
   - Dover files a Planning Board agenda under its ZBA category.
   - Southold's "Planning Board" AgendaCenter category also holds Land Preservation Committee agendas.
   - Lysander's file `91426agenda.pdf` cannot be assigned to a board and is labeled Town Board.
6. **Statewide sources worth testing next:**
   - county planning boards' 239-m referral agendas, which see every town zoning change and moratorium. Fulton County's January agenda had Perth's BESS and renewables moratorium (https://www.fultoncountyny.gov/sites/default/files/_planning/PB-2026-01-20.pdf).
   - the NYS Department of State local-law filings, which record adoption only, after the fact.

## Next 50 towns to add

Unless marked otherwise, each is an ACTIVE or recent BESS moratorium in Carina's monitor (https://carina.energy/bess-moratoriums/), with the listed end date. They are ordered by how soon a renewal or replacement law is likely to reach an agenda, with data-center towns added last.

| # | Town (County) | Why |
|---|---|---|
| 1 | Carlisle (Schoharie) | Moratorium ends 2026-10-21 |
| 2 | Gainesville (Wyoming) | Ends 2026-10-20 |
| 3 | Brasher (St. Lawrence) | Ends 2026-10-31 |
| 4 | Sherman (Chautauqua) | Ends 2026-10-31 |
| 5 | Corning (Steuben) | Ends 2026-11-20 |
| 6 | Campbell (Steuben) | Ends 2026-11-30 |
| 7 | Clymer (Chautauqua) | Ends 2027-01-31 |
| 8 | Greig (Lewis) | Ends 2027-01-14 |
| 9 | Denmark (Lewis) | Ends 2027-01-21 |
| 10 | Schroeppel (Oswego) | Ends 2027-02-10 |
| 11 | Lewis (Lewis) | Ends 2027-03-16 |
| 12 | Northampton (Fulton) | Ends 2027-03-30 |
| 13 | Glen Cove city (Nassau) | Ends 2027-05-13 |
| 14 | Mayville village (Chautauqua) | Ends 2027-06-01 |
| 15 | Benson (Hamilton) | Ends 2027-06-09 |
| 16 | Arietta (Hamilton) | Ends 2027-06-22 |
| 17 | Eden (Erie) | Ended 2026-09-30, so an extension or law is due |
| 18 | Collins (Erie) | Ended 2026-09-30 |
| 19 | Virgil (Cortland) | Ended 2026-09-30 |
| 20 | Maine (Broome) | Ended 2026-09-30 |
| 21 | Norfolk (St. Lawrence) | Ended 2026-09-30 |
| 22 | Oswegatchie (St. Lawrence) | Ended 2026-09-30 |
| 23 | Palatine (Montgomery) | Ended 2026-09-30 |
| 24 | Pike (Wyoming) | Ended 2026-09-30 |
| 25 | Mentz (Cayuga) | Ended 2026-09-30 |
| 26 | Carlton (Orleans) | Ended 2026-09-30 |
| 27 | Allen (Allegany) | Ended 2026-09-30 |
| 28 | Angelica (Allegany) | Ended 2026-09-30 |
| 29 | Dunkirk city (Chautauqua) | Ended 2026-09-09 |
| 30 | Westfield (Chautauqua) | Ended 2026-08-31 |
| 31 | Root (Montgomery) | Ended 2026-08-31 |
| 32 | Greenwood (Steuben) | Ended 2026-08-31 |
| 33 | Prattsburgh (Steuben) | Ended 2026-08-31 |
| 34 | Ellery (Chautauqua) | Ended 2026-08-31 |
| 35 | North Harmony (Chautauqua) | Ended 2026-08-30 |
| 36 | West Bloomfield (Ontario) | Ended 2026-08-13 |
| 37 | Rose (Wayne) | Ended 2026-07-03 |
| 38 | Stockport (Columbia) | Ended 2026-06-01 |
| 39 | Peekskill city (Westchester) | Ended 2026-05-31 |
| 40 | Yonkers city (Westchester) | Moratorium to 2026-03-31; large city with a Legistar-type platform likely |
| 41 | Yorktown (Westchester) | Moratorium expired 2026-01-14; BESS law follow-up |
| 42 | Riverhead (Suffolk) | Early Long Island moratorium; BESS proposals |
| 43 | Montgomery (Orange) | Moratorium lifted 2026-03-31, so a law was adopted; applications are next |
| 44 | Plattekill (Ulster) | Lifted 2026-03-31 |
| 45 | Mount Pleasant (Westchester) | Lifted 2026-03-31 |
| 46 | Sherburne (Chenango) | January 2026 moratorium hearing tied to a Nexamp BESS (https://eticaag.com/sherburne-ny-approves-battery-storage-moratorium/) |
| 47 | Albany city (Albany) | Data-center regulations advancing; South End data-center opposition (https://www.wamc.org/news/2026-06-03/albany-data-center-regulations-advance) |
| 48 | Alabama (Genesee) | STAMP data-center proposal. *Source to verify* |
| 49 | Somerset (Niagara) | BESS moratorium lifted 2026-03-31 (Carina); data-center and crypto load at the former coal-plant site. *Data-center source to verify* |
| 50 | Massena (St. Lawrence) | Crypto and data-center load history. *Source to verify* |

**Also queue the blocked towns** for a different route:
- for Huntington, Lansing and Cicero, a crawl-delay cap of 20 s or more;
- for Brookhaven, Islip and Halfmoon, permission or a county 239-m source.
