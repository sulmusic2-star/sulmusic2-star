# Agenda Ahead: Virginia and the Maryland suburbs (wave 2 test)

- **Run date:** 2026-11-02. Discovery, one full crawl, two re-runs (incremental, then re-match after the hand check), all on the same day, all gated: nothing reached `data/hits_current.json`, `data/state/` or the site (`experiments/gate_check.py` passes before and after).
- **Crawl window:** meetings from 2026-09-18 to 2027-03-02 (45 days back, 120 days ahead).
- **Places:** 214. Virginia 174 (all 95 counties, the 38 independent cities, 41 towns where data-center, solar or battery fights are reported). Maryland 40 (the 23 counties, Baltimore City, and 16 municipalities in Montgomery, Prince George's, Frederick, Anne Arundel and Washington Counties).
- **Question.** Can the crawler read these two states well enough to promote them, and what does the site need before it can show them?
- **Short answer.** Coverage is good for counties and cities and poor for small towns; precision on a fresh sample is 82%, under the 90% bar, with the shortfall in passing mentions rather than wrong subjects. The states stay gated. The site needs state names, county pages and a county-aware vocabulary before promotion (section 9).

## 1. Coverage

"Readable" means at least one agenda or packet for a tracked body was read in this crawl. "Automated" means a listing was found and its first document fetched under robots.txt (one automated place per state had no meeting document inside the window).

### Virginia, 174 places

| Kind | Attempted | Readable | Blocked (how) | No agendas online | Unreachable from the sandbox |
|---|---|---|---|---|---|
| County | 95 | **62 (65%)** | 20: Akamai or site firewall 6 (Albemarle, Bedford, Clarke, Fauquier, Frederick, Nelson); Cloudflare challenge 3 (Culpeper, Highland, James City); BoardDocs 4 (Accomack, Northampton, Prince George, Pulaski); iCompass 1 (Lancaster); iQM2 1 (Washington); robots.txt 2 (Charlotte, Rappahannock); documents blocked 2 (Fluvanna crawl-delay 15 s, Richmond County robots); crawl-delay 60 s 1 (Alleghany) | 3: Dickenson (Agenda Center holds 2022 only), Grayson (no listing found), Montgomery (Laserfiche only) | 9: Bath, Buchanan, Giles, Lee, New Kent, Rockingham, Russell, Tazewell (egress 502 or timeout); Floyd (listed address answers 404) |
| Independent city | 38 | **26 (68%)** | 9: Granicus 2 (Fairfax, Manassas); iCompass 2 (Newport News, Williamsburg); Cloudflare 2 (Fredericksburg, Waynesboro); Akamai 2 (Lexington, Staunton); crawl-delay 20 s 1 (Portsmouth) | 2: Bristol (Laserfiche), Manassas Park (script-only site) | 0 |
| Town | 41 | **18 (44%)** | 9: Akamai or firewall 3 (Leesburg, Blacksburg, Chase City); Cloudflare 3 (Lovettsville, Strasburg, Chatham); BoardDocs 1 (Culpeper); Granicus 1 (Ashland); iQM2 1 (Haymarket) | 10: 7 with board pages but no dated agenda (Round Hill, Middleburg, Luray, Orange, Christiansburg, Abingdon, Vinton: empty Agenda Centers, agendas on undated Archive Center or video pages); 2 script-only (Dumfries, Clarksville); 1 none found (Blackstone) | 4: Hamilton, Woodstock, Stephens City, Gordonsville |

- **By body, counties:** Board of Supervisors 60 of 95, Planning Commission 42 of 95, BZA 11 of 95 (113 of 285 bodies, 40%). Cities: council 25 of 38, Planning Commission 15, BZA 5. Towns: council 17 of 41, Planning Commission 7, BZA 4.
- **By platform, readable places:** CivicPlus Agenda Center 35, CivicClerk 31, the general agenda-page reader 32 (Revize, WordPress, Drupal, CivicLive and plain pages), Legistar 5 (Richmond, Alexandria, Hampton, Harrisonburg, Vienna), eSCRIBE 2 (Loudoun's Board of Supervisors, Gloucester), OnBase Agenda Online 1 (Arlington).
- **Against the October test** (32 Southside and Piedmont counties, 84% readable): the statewide figure is lower because the northern and western counties sit behind Akamai and Cloudflare walls (Albemarle, Bedford, Clarke, Fauquier, Frederick, Culpeper, James City, Highland) and because eight southwestern county sites could not be reached from this sandbox at all.
- **Northern Virginia, the market that matters most:** Loudoun's Board of Supervisors reads (eSCRIBE, business meetings and public hearings; its Planning Commission is on OnBoard, which disallows us), Prince William's Planning Commission reads (its Board is on Granicus), Fairfax's Board reads from its own meeting pages (the Planning Commission posts only monthly calendars), Arlington's Board and Planning Commission read (OnBase), Stafford and Spotsylvania read (CivicClerk), Alexandria reads (Legistar). Fauquier, Culpeper County and the Town of Culpeper, Leesburg, Manassas and the City of Fairfax are blocked.

### Maryland, 40 places

| Kind | Attempted | Readable | Blocked (how) | Unreachable from the sandbox |
|---|---|---|---|---|
| County | 23 | **17 (74%)** | 6: Granicus 2 (Harford, Talbot); Akamai or firewall 2 (Charles, Baltimore County); robots.txt 2 (Carroll, Somerset) | 0 |
| City (incl. Baltimore City) | 12 | **10 (83%)** | 2: Granicus 1 (City of Frederick); Akamai 1 (Gaithersburg) | 0 |
| Town | 5 | **3** | 0 | 2: Laytonsville, Barnesville |

- **By body, counties:** council or commissioners 13 of 23, Planning Commission 11 of 23, Board of Appeals 9 of 23 (33 of 69 bodies, 48%).
- **By platform:** CivicPlus 10, CivicClerk 8 (Allegany, Anne Arundel, Cecil, Kent; Laurel, Bowie, Greenbelt, Hyattsville), agenda-page reader 9, Legistar 3 (Prince George's County Council, Baltimore City Council, Rockville Mayor and Council).
- **The two suburban counties:** Montgomery County's Council agendas are weekly PDFs behind a viewer link, read with a new listing key; the Montgomery Planning Board (M-NCPPC) is read from its per-meeting pages. Prince George's County Council reads through Legistar (its website is behind Akamai; the Planning Board's agendas load by script and were not found). Howard County's Board of Appeals cases read from OLIS; its council sessions appear there when posted.
- **Municipalities without zoning power** (Takoma Park, Bowie, College Park, Greenbelt, Hyattsville: the Montgomery and Prince George's District Councils zone for them) read, but what they carry is advisory. Their rows say `"zoning_power": "county"`.

### What cannot be read, by cause (both states)

| Cause | Places | Note |
|---|---|---|
| Akamai or a site firewall (HTTP 403) | 14 | Albemarle, Bedford, Clarke, Fauquier, Frederick VA, Nelson, Lexington, Staunton, Leesburg, Blacksburg, Chase City; Charles, Baltimore County, Gaithersburg. Prince George's County's homepage too, but its council reads through Legistar |
| Cloudflare challenge | 8 | Culpeper County, Highland, James City, Fredericksburg, Waynesboro, Lovettsville, Strasburg, Chatham |
| BoardDocs (403 to our bot) | 5 whole places, 2 bodies | Accomack, Northampton, Prince George VA, Pulaski, Town of Culpeper; Essex's Board, Northumberland's BZA |
| Granicus ViewPublisher (robots.txt) | 7 whole places, many bodies | Fairfax city, Manassas, Ashland; Harford, Talbot, Frederick city; plus the Boards of Prince William, Chesapeake, Roanoke County (iQM2) and the video hosts of Loudoun, Montgomery, Howard |
| iCompass / CivicWeb and iQM2 (robots.txt) | 5 | Lancaster, Newport News, Williamsburg; Washington VA, Haymarket |
| robots.txt on the locality's own site | 5 | Charlotte, Rappahannock, Richmond County (files), Carroll MD, Somerset MD; also Loudoun's OnBoard portal |
| Crawl-delay above our caps | 3 | Alleghany 60 s, Fluvanna 15 s (files), Portsmouth 20 s (files cannot be read at the 10 s document cap) |
| Laserfiche only, or a script-only site | 6 | Montgomery VA, Bristol, Virginia Beach's full agendas (its brief agenda reads); Manassas Park, Dumfries, Clarksville |
| No dated agenda on a reachable site | 10 | Dickenson, Grayson, Blackstone and seven small towns |
| Unreachable from this sandbox | 15 | Not a block: the egress proxy answered 502 to CONNECT or robots.txt timed out on three tries. Retry from the production host |

Draft unblock letters for every row above are in `va_md_unblock_drafts.md`.

## 2. Crawler changes (all additive)

- `watch351/boards.py`: `STATE_BOARD_PATTERNS["MD"]` (county councils, boards of county commissioners, the District Council, mayor and board of aldermen, planning boards, boards of appeals incl. Baltimore's BMZA). Virginia's entry unchanged.
- `watch351/discover_sites.py`: Maryland board patterns, Maryland CivicClerk tenant guesses (`<name>comd`, `<name>countymd`, `<name>md`), a Legistar branch (`do_legistar`: the public web API lists each body's meetings; the meeting detail page must answer under robots.txt; a `legistar_client` on the target row is used even when the homepage is walled, which is how Prince George's County, Alexandria and Hampton read), and state-aware default board labels (`STATE_BOARD_LABELS`: "Board of Supervisors", not "Select Board / Council").
- `watch351/adapters/agenda_page.py`, new listing keys: `date_from_url` (a page link whose address carries the meeting date, "/oct-13-2026-meeting", is a meeting page: Fairfax's Board, the Montgomery Planning Board), `meeting_page_self` (read the meeting page's own text as the agenda instead of its attachments: the Montgomery Planning Board), `doc_href_extra` (more link shapes that are documents, and a viewer link's `document=` parameter is unwrapped to the file itself: Montgomery County Council). Existing configs do not set these keys, so they behave as before.
- `watch351/adapters/onbase.py` (new, platform `onbase_agenda`): Hyland OnBase "Agenda Online" portals (Arlington County Board and Planning Commission; Tucson uses the same product).
- `watch351/keywords.py`: `STATE_TOPICS["MD"]` (Maryland's CPCN and Renewable Energy Certainty Act, sectional and local map amendments when they rezone for industry or energy, plus the MI/VA shared patterns) and four false-positive rules from the hand check (section 4). MA, NY and RI are untouched: `experiments/keyword_regression.py` re-matched the 973 production documents still in the shared cache with the old and new matcher, 0 differ (`data/test/va_md/keyword_regression.json`).
- `watch351/fetch.py`: a half-written cache meta file (two runs sharing the cache) is treated as not cached instead of crashing the run.
- `experiments/va_md_wave.py`: targets, discovery with a hand-curation table (Fairfax, Arlington, Virginia Beach, Portsmouth, Montgomery MD, Howard MD, the sandbox notes), relabeling, crawl, analysis, stratified sample.

## 3. Output

| | Virginia | Maryland |
|---|---|---|
| Places crawled | 108 | 30 |
| Documents read in run 1 | 538 (534 ok, 4 need OCR, 15 errors: 13 over the 40 MB cap, 2 Revize files behind robots) | 185 (all ok) |
| Read as | PDF 435, HTML 60, OCR 33, DOCX 6 | PDF 148, HTML 33, OCR 4 |
| Hits after the hand-check rules | **772** in 73 places | **80** in 15 places |
| Hits for meetings still ahead on the crawl day | 112 | 17 |
| By topic (a hit can carry several) | zoning_amendment 317, data_center 187, solar 174, clean_energy_siting 109, battery_storage 80, wireless_telecom 67, moratorium 21 | solar 40, zoning_amendment 23, data_center 15, clean_energy_siting 7, moratorium 3, battery_storage 3, wireless_telecom 1 (the rules removed 18 of Maryland's 98 run-1 hits, 10 of them the College Park carport) |
| By body | governing board 459, planning 309, BZA 4 | council 49, planning 30, board of appeals 1 |

Hits by platform: CivicPlus 523, agenda-page reader 204, CivicClerk 104, Legistar 32, eSCRIBE 9. The 13 packets over the 40 MB cap: Halifax (242 and 293 MB), Suffolk (90 and 46 MB), Botetourt (3, 48 to 63 MB), Franklin, Colonial Heights, Greensville, Southampton (the Cenergy solar application, 85 MB), Louisa town, Smithfield.

**Examples.**

- **Loudoun County Board of Supervisors, public hearing Nov 12.** A zoning ordinance amendment for three data center buildings (LEGI-2025-0053) and a ZMAP rezoning 22.68 acres from PD-MUB. https://pub-loudoun.escribemeetings.com/
- **Fairfax County Board of Supervisors, Oct 27.** Board matter requiring public disclosure of data center projects' incentives and resource demands; solar on county property.
- **Chesterfield County BZA, Oct 7.** TradePort 95's appeal of the determination that data center use now needs conditional use approval.
- **Charles City County Board of Supervisors, Oct 27.** Resolutions initiating comprehensive plan and zoning text amendments for battery storage and data centers; a Special Use Permit for BESS.
- **Shenandoah County Planning Commission, Nov 5.** Zoning text amendment 26-11-01 on Energy Facilities and Data Center Development articles.
- **Town of Front Royal Council, Oct 26.** Extension of the moratorium on data center land-use applications.
- **Cumberland County Planning Commission, Sep 21.** CUP 26-03, the Cumberland Energy Center dual-fuel combined-cycle plant (still filed under clean_energy_siting: a gas-plant topic is still missing).
- **King and Queen County Planning Commission, Nov 2.** CUP26-03, a utility-scale solar facility.
- **Anne Arundel County Council, Oct 5.** Bill 66-26: a temporary moratorium on data storage centers and a regulation work group.
- **Frederick County MD Planning Commission, Oct 14.** Quantum Frederick Bauxite II and III data center expansions (CDI overlay zone).
- **Wicomico County Council, Nov 3.** Public hearing on Bill 2026-13 regulating solar energy systems; the Planning and Zoning Commission's CPCN discussion.
- **Montgomery Planning Board, Nov 12.** Holsey Road Community Solar, mandatory referral MR2026028 (public hearing).

## 4. Precision

**Sample.** 60 hits drawn at random from the 872 hits of run 1 before any rule change, stratified 40 Virginia and 20 Maryland (seed 2026), each judged from about 1,500 characters of the document's text. Definition as in `test_mi_va.md`: a hit is right when it points to a real agenda item, ordinance text, or staff or public record about its topic in the land-use or siting sense; passing mentions, non-zoning policy text and non-land-use items are false positives. The worksheet is `data/test/va_md/precision_worksheet_r1.json`, the judgments with reasons `data/test/va_md/precision_judgments.json`.

| | Right | Precision | 95% interval (Wilson) | Every topic tag right |
|---|---|---|---|---|
| Virginia (40) | 34 | **85.0%** | 71 to 93% | 82.5% |
| Maryland (20) | 15 | **75.0%** | 53 to 89% | 70.0% |
| Both (60) | 49 | **81.7%** | 70 to 89% | 78.3% |

This is under the 90% bar, and the interval excludes 90%. The October Virginia test measured 93% on 32 counties whose agendas are mostly short CivicPlus and CivicClerk files; the statewide crawl reads many more 100-page packets with minutes, letters and reports, where passing mentions live.

**The 11 false positives.**

| Pattern | Hits | Examples |
|---|---|---|
| Passing mentions | 4 | an administrator's calendar line ("Laurel Branch Solar project kick-off"); paving timed around a solar easement; Henrico residents' comments about Goochland's data centers; a Warrenton comment on the mayor's past Amazon votes |
| Non-land-use text using the words | 2 | Prince George's utility shut-off moratorium resolution naming data centers; Warrenton's capital asset policy defining proffers "at the time of a rezoning" |
| Residential or building solar | 3 | a College Park homeowner's 12 by 12 ft solar carport variance (two passages); a Falls Church memo on community center solar |
| "PV" as a pavement elevation on a drawing | 1 | Worcester County site plan ("EP 9.49 PV 8.71 FFE 10.00") |
| A past amendment mentioned in a housing item | 1 | Worcester growth allocation, "when the zoning map amendment was approved in 2025" |

**Rules added** (MI, VA and MD matchers only): "PV" among elevation numbers on a drawing; "rezoning" inside capital asset or depreciation policy; data centers named in a utility rate or shut-off resolution with no zoning words; a residential solar carport or panel roof with no utility-scale words. In-sample they remove 5 of the 11 (the second carport passage, the shut-off resolution, the pavement PV, the proffer definition, the Warrenton comment) and lose no true positive: 54 of 60, 90.0% in-sample. That is not a held-out number. The six that remain are passing mentions and need a section classifier that separates minutes, letters and reports from the agenda's own items, the same gap the October test named.

**Also seen, counted right but low value:** Cumberland County's standing "no update on solar regulations" item appears in three sampled hits because the packets carry months of old minutes. Duplicate passages of one item (the carport, the Wicomico ZTA, the Shenandoah comments in two documents) make up 5 of the 60.

## 5. Posting lead time against the notice laws

Lead time is days from first posting to the meeting (7 pm assumed when no time is given). The best sources are the vendor's first-publish stamps.

| Source | Virginia n / median / share ≥ 3 days | Maryland n / median / share ≥ 3 days |
|---|---|---|
| CivicPlus "Posted" stamp | 101 / **4.0 d** / 70% | 49 / **4.2 d** / 82% (p10 1.0 d) |
| CivicClerk `publishOn` | 179 / **4.3 d** / 72% | 49 / **3.2 d** / 51% (24% negative: re-publication after the meeting) |
| PDF creation or modification date | 374 / 4.2 d / 72% | 117 / 3.3 d / 64% |
| Revize upload stamp | 78 / 3.2 d / 71% | |
| HTTP Last-Modified | 116 / 3.2 d / 53% | 17 / 5.4 d / 65% |
| Legistar `EventAgendaLastPublishedUTC` (8 clients, 169 events) | median 3.6 d; 54% ≥ 3 d; 34% under a day. "Last published", so re-publication after a meeting pulls it down (Alexandria's median is 0) | |

- **Virginia.** Va. Code § 2.2-3707 requires meeting notice posted at least three working days ahead and the agenda packet available when it goes to members. Observed: a median of about four days and 70 to 72% posted three or more calendar days ahead, against 83 to 87% in the October test's smaller county set. Roughly one agenda in four appears inside the three-day window, late or re-posted. Virginia also requires published newspaper notice of zoning hearings under § 15.2-2204 (check the current text before quoting it on the site).
- **Maryland.** The Open Meetings Act (General Provisions § 3-302, § 3-302.1) asks for reasonable advance notice and an agenda available at least 24 hours before the session. CivicPlus counties beat that comfortably (82% three or more days ahead, the tenth percentile a full day); CivicClerk places publish later and republish. Montgomery County posts its weekly agenda the Friday before; the Planning Board posts its page about a week ahead. Zoning hearing notices in Maryland are published in advance under the Land Use Article (two successive weeks for county zoning hearings in most counties; confirm per county before quoting).
- **What that means for alerts:** a daily morning crawl gives Virginia residents three to four days' warning on most county items and Maryland residents two to four; anything posted inside 24 hours is caught the next morning, which for an evening meeting is the day of.

## 6. Reliability

| Run | What | Runtime | Requests | Bytes | Places ok | Documents |
|---|---|---|---|---|---|---|
| run1 | First crawl, listings warm from discovery, documents cold | 370 s | 924 (155 listing, 769 document) | 1.56 GB | 138 of 138 | 743 listed, 723 new, 15 errors |
| run2 | Same day, after the matcher change | 95 s | 3 | 1.9 MB | 138 of 138 | 0 new, 599 re-matched from the cache, 138 skipped as indexed |
| run3 | Same day, after the board relabeling | 43 s | 2 | 0 | 138 of 138 | 0 new, 716 skipped as indexed (board labels in the index were then corrected offline and the hits file rebuilt) |

- Network errors: 0. Robots refusals during the crawl: 2 (Revize files for Nottoway and Carroll VA).
- Discovery: Virginia 174 places in 1,090 s (about 2,200 page reads), Maryland 40 in 432 s.
- **A shared-cache incident.** Between run1 and the hand check, 140 of 719 document bodies vanished from `crawler/.cache`, which three sessions were writing at once (the New York and Great Lakes crawls ran in parallel; the disk reached 90%). The sample's missing documents were re-fetched for the check (two Worcester items were judged from their snippets). The regression check also hit a half-written meta file; `fetch.py` now tolerates that. In production one run owns the cache, so this does not apply, but a cache lock or per-run cache directory would make parallel tests safe.

## 7. Customers to approach first (from `where_it_pays_2026.md`, recommendation 2)

- **Northern Virginia (Loudoun, Prince William, Fauquier, Culpeper, Stafford):** data-center developers and their land teams in Loudoun and Prince William; the site-selection desks at CBRE and JLL; Walsh Colucci and Hirschler-class zoning counsel; the Piedmont Environmental Council; Data Center Coalition staff; Loudoun Now and Prince William Times reporters on the free tier for distribution. What we can show them today: Loudoun's Board hearings, Prince William's Planning Commission, Fairfax's Board, Arlington, Stafford and Spotsylvania. Fauquier, Culpeper, Leesburg and Manassas need the unblock letters first.
- **Richmond and the Piedmont (Henrico, Chesterfield, Hanover, Goochland, Louisa, Powhatan, Charles City):** the same developer and counsel list plus Richmond's land-use bar; all seven counties read now, and the Chesterfield BZA data-center appeal and Charles City's BESS and data-center resolutions are the kind of item they pay for.
- **Southside (Pittsylvania, Mecklenburg, Halifax, Charlotte, Campbell):** solar developers and the siting-agreement and revenue-share items (Halifax's § 58.1-2636 revenue share, Mecklenburg's BESS siting agreement); Charlotte County is robots-blocked.
- **Maryland suburbs (Montgomery, Prince George's, Frederick, Howard, Anne Arundel):** the note names county planners who want to see neighbours' ordinances and the Maryland county pauses. Additions from this test, not from the note: the Quantum Frederick developers (site plans before Frederick's Planning Commission), the Montgomery and Prince George's land-use bar (Linowes and Blocher, Lerch Early, Miles and Stockbridge are the firms that appear on these dockets), the Sugarloaf Alliance and the Maryland chapter of the Sierra Club on the opposition side, and Maryland Matters for distribution. Howard's, Harford's and Baltimore County's councils need unblocking first.

## 8. Decisions needed

1. **Precision.** 82% held-out, 90% in-sample after rules. Promote with the known passing-mention noise, or hold the two states until a section classifier (agenda items versus minutes, letters and reports) is built and tested on a fresh sample.
2. **Unblock order.** The drafts cover 70-odd bodies. The highest-value ones: Fauquier, Culpeper County and town, Leesburg, Manassas, the Prince William Board, Fairfax city (Virginia); Howard, Harford, Charles, Baltimore County, Gaithersburg, Frederick city (Maryland).
3. **Maryland municipalities without zoning power.** Show Takoma Park, Bowie, College Park, Greenbelt and Hyattsville as places (their councils comment and their advisory boards hear variances) or fold them into the county page with a one-line note, as Michigan's `via_county` townships are.
4. **The 40 MB cap.** 13 packets of 46 to 293 MB were skipped. Raise the cap for a few hosts, or read a packet's first pages.
5. **Fixed-address agendas.** Virginia Beach's brief agenda (and Koylton, MI) overwrite one file. The index keys on the address, so a new agenda there is never re-read. A listing flag that re-reads when Last-Modified changes is a small crawler change; the site would then see one `#meeting-date` document per meeting.
6. **Sandbox-unreachable places.** 15 places need one discovery pass from the production host before anyone is written to.

## 9. Site support needed before promotion (a spec, not edits)

Everything below is in `build.py`, `site/` or the data contract; none of it is done. The crawler side (towns files, hits in the contract shape, `board_key` mapping) is ready.

**State names and codes.**
- `STATE_NAMES` in `build.py` lacks `VA` and `MD`; `stateName()` in `site/app.js` maps only ma, ny and ri; `trending.py`'s address regex lists state names for MA, RI and NY only (line about `Massachusetts|Rhode Island|New York`) and needs Virginia and Maryland. The AG tracker branches (`state == "MA"`) are already guarded.
- `REASON_TEXT` and `REASON_SHORT` know `robots_disallow_site`, `no_agenda_listing_found` and `agendas_stale_or_undated`; the discovery writes `robots_disallow`, `no_agendas_found`, `no_recent_agendas`, `documents_blocked`, `document_store`, `js_only`, `website_mismatch`, `unreachable`, `http_error`, `no_website` and `crawl_delay_exceeds_cap`. Map or add them, and let the sentence take "{town}'s website" for a county ("Loudoun County's website" reads fine).

**Kinds of place: county, independent city, town, municipality.**
- Rows carry `kind` (`county`, `city`, `town`), `county` (a county row's own name; `null` for independent cities), and for Maryland municipalities `zoning_power` (`own` or `county`). The site treats everything as a "town"; the pages, the town box ("Type your town"), the directory ("Towns"), counts ("N towns we read") and the alert copy all say town. Use "place" or "town or county" in shared copy and the kind on each page.
- `for_town()` swaps town clerk for city clerk when `kind == "city"`. Add a county branch: in Virginia "the Clerk to the Board of Supervisors" and "the County Administration Building"; in Maryland "the Council's office" or "the County Commissioners' office" (the row's governing-body listing says which) and the county government center. The MA phrase "the town clerk is the last word on dates" needs the same treatment.
- Names: rows are "Loudoun County", "City of Manassas", "Town of Culpeper" (so Culpeper County and the Town of Culpeper stay apart; same for Franklin, Richmond, Roanoke, Bedford, Fairfax, Orange, Louisa, Smithfield, Frederick). Page titles ("Town of Culpeper, Virginia") read fine; the town box should match "Culpeper" to both and ask which; slugs become `/va/town-of-culpeper`. Keep the ids as they are in the hits.
- Hits for a county row carry `county` equal to the row's name, so the line "Loudoun County (Loudoun County)" would print; suppress the county suffix when the place is the county. The county filter and `data-county` still work.
- A county page should list the towns and cities inside it (rows whose `county` matches) with their read status, and a town page should link up to its county ("Loudoun County decides zoning outside the town; its Board meets Nov 12"). Independent cities have no county and stand alone. A Maryland municipality with `zoning_power: "county"` needs the Michigan `via_county` treatment: one line saying the Montgomery or Prince George's District Council and the M-NCPPC Planning Board decide zoning for it, with a link to the county page.
- The directory (`/towns`) groups by county; a county row inside its own group is right, but the group's count should say places, and independent cities (no county) need their own heading rather than "Other towns".

**Boards and the speaking rules.**
- `BOARD_NAMES` labels `select_board` "Select board or city council"; the filter dropdown and the How-it-works table use it. Add state-aware labels: Virginia "Board of Supervisors or council", "Planning Commission", "Board of Zoning Appeals"; Maryland "County Council or Commissioners", "Planning Commission or Planning Board", "Board of Appeals". The hits already carry the real body names ("Board of Supervisors", "Montgomery Planning Board"); the crawler's discovery now writes state defaults instead of "Select Board / Council" for shared pages.
- `who_votes_text()` says the Planning Board recommends and Town Meeting (or a city council) votes on the bylaw. Virginia: the Planning Commission recommends; the Board of Supervisors, or the town or city council, adopts the ordinance. Maryland: the Planning Commission recommends; the County Council or the County Commissioners adopt; in Montgomery and Prince George's the Planning Board recommends and the Council sitting as the District Council decides, after a hearing examiner where one is required. No Town Meeting anywhere; "bylaw" is "ordinance" in both states.
- `SPEAK_TEXT` ("Public hearing: anyone can attend and ask to speak") holds for Virginia boards, which take speakers at the hearing with sign-up in the room, and Virginia boards also run a citizens' time at regular meetings. Maryland county councils and the M-NCPPC planning boards usually require advance sign-up to testify (Montgomery's Council and Planning Board take online sign-ups the day before; Prince George's Council pre-registers speakers; Baltimore City Council takes written testimony by form). The default line for Maryland should be "Public hearing: sign up with the Council's office to speak" until an agenda's own `how_to_speak` says otherwise; `SPEAK_NONE` and `SPEAK_NO` should not name a town clerk for counties.
- `TOPIC_LABELS["clean_energy_siting"]` reads "Consolidated permit / 225 CMR 29 / clean energy infrastructure", which is Massachusetts law. For Virginia the topic means Special Use and Conditional Use Permits for energy facilities, § 15.2-2232 reviews, siting agreements and revenue share; for Maryland CPCN comments, special exceptions and the Renewable Energy Certainty Act. One neutral label ("Energy facility permits and siting") or a per-state dict.
- `TERMS` (the "Words on the agenda" glossary) is New England: Notice of Intent, 40B, special permit, Chapter 61A. Add SUP and CUP, 2232 review (substantial accord), siting agreement, revenue share, proffers, by-right, ZTA and ZMAP, BZA; for Maryland special exception, conditional use, ZTA and sectional map amendment, CPCN, mandatory referral, growth allocation (Critical Area), District Council, Board of Appeals. Gas-fired plants (Cumberland Energy Center) still need a topic of their own.

**Map and town box.**
- `MAP_GROUPS` has `ma-ri` and `ny`; add `va-md` (the two states touch at the Potomac). `geo/match_points.py` reads county subdivisions for MA, RI and NY (FIPS 25, 44, 36). Virginia's and Maryland's county subdivisions are magisterial districts, not places: counties and independent cities come from the Census county Gazetteer (independent cities are county-equivalents, "Alexandria city"), towns and Maryland municipalities from the place Gazetteer, matched by name, state and kind. `geo/region_land.json` needs the Virginia and Maryland outlines (and the District, Delaware and West Virginia edges for context).
- A county is an area, not a point; a dot at the centroid works, but the caption "Each dot is a town" and the dot size need the kind: a larger or hollow marker for counties, towns as now. The home map and `region_map_svg()` captions say towns.
- The town box datalist should include counties and say "Type your town or county"; a name shared by two kinds ("Culpeper") asks which, as a name shared by two states does now.

**Free area and feeds.**
- `data/neighbors.json` has keys for MA, RI and NY only, so the API would allow no neighbours for any Virginia or Maryland place. Extend `tools/neighbors.py`: counties and independent cities from the county boundary file (`cb_2024_us_county_500k`), towns and municipalities from the place files (`cb_2024_51_place_500k`, `cb_2024_24_place_500k`); a county's area is the touching counties and cities plus the towns inside it, a town's area is its county plus the towns and cities it touches. The Potomac is Maryland's, so Virginia's shore counties touch Maryland's.
- Email, webhook, calendar and `w.js` copy say "town" and "towns next door"; "place" or the kind. Feed titles and ids are unaffected.
- Full-text search rows already carry the state; the search page's state filter needs the two names.

**Crawler follow-ups the site will see.**
- A fixed-address agenda (Virginia Beach) needs a re-read rule (decision 5) so each meeting becomes its own `#meeting-date` document.
- Board labels that were document titles ("09/14/2023 Board of Supervisors Worksession", "Town Council Meeting Agendas") were relabeled by hand in the towns files; discovery should refuse a label that carries a date or the words "agendas" or "minutes" and fall back to the state default.
- ARCHITECTURE.md ("States under test") and OPERATIONS.md ("Test states") still name only MI and VA; add MD and the `data/test/va_md` output directory. Not edited here because the New York and Great Lakes engineers are changing the same sections.

## 10. Files

**Code** (`projects/351watch/crawler/`): new `watch351/adapters/onbase.py`, `experiments/va_md_wave.py`; changed, additively, `watch351/boards.py`, `watch351/discover_sites.py`, `watch351/keywords.py`, `watch351/fetch.py`, `watch351/adapters/agenda_page.py`, `watch351/adapters/__init__.py`.

**Configs** (`projects/351watch/data/`): `towns_va.json` (174 rows, 108 automated, gated), `towns_md.json` (40 rows, 30 automated, gated).

**Test output** (`projects/351watch/data/test/va_md/`): `targets_va.json`, `targets_md.json`, `hits_va_md.json`, `state/` (index, health, run reports), `runs/run_run1.json` to `run_run3.json`, `requests_run*.tsv`, `analysis_va_md.json`, `precision_worksheet_r1.json`, `precision_judgments.json`, `keyword_regression.json`, `posted_stamps_*.json`, `legistar_probe.json`, the discovery and probe logs.

**Notes** (`research_notes/Expansion/`): this file; `va_md_unblock_drafts.md`.

**Re-run:**

```bash
cd projects/351watch/crawler
python3 experiments/va_md_wave.py discover --state VA    # or MD; --places "Loudoun County,City of Manassas"
python3 experiments/va_md_wave.py crawl --label run4
python3 experiments/va_md_wave.py analyze
python3 experiments/va_md_wave.py sample --state-n VA:40,MD:20 --seed 2027 --exclude ../data/test/va_md/precision_judgments.json
```

Production is untouched by every command (`experiments/gate_check.py`).
