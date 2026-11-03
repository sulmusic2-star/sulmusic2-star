# Great Lakes wave: southeast Michigan townships and central Ohio, behind the gate

Written 2026-11-02 from the gated test crawl (`data/test/great_lakes/`). Nothing in this wave reaches the live site: `data/towns_mi.json` and `data/towns_oh.json` carry `"gated": true`, the production daily run skips them (`experiments/gate_check.py`: GATE OK with both files present), and the test crawl writes only under `data/test/great_lakes/`. Companion notes: `great_lakes_unblock_drafts.md` (letters, not sent), `test_mi_va.md` (the October Michigan test this builds on), `cheap_township_coverage.md` section 1 (the county route), `where_it_pays_2026.md` section 4 recommendation 3 (why these counties).

**In one screen.**

- **Michigan, the twelve southeast counties (208 townships):** 74 read directly (36%), 26 more only through a readable county planning commission (100, 48%, either way), 97 with nothing usable online (47%), 22 blocked by a bot wall, robots.txt or a vendor. 6 of the 24 county bodies in the file are readable (Livingston, Jackson, Genesee, Calhoun, Huron, Clinton); Washtenaw, Oakland, Monroe, Lapeer, Shiawassee and St. Clair post no county planning commission agendas, Macomb was unreachable, Ingham is robots-closed, Lenawee's listing is empty this half-year. Over all 283 Michigan township rows: 124 (44%) covered either way.
- **Ohio, the eight counties (130 townships):** 20 read directly (15%), 87 more through the county or regional planning commission (107, 82%, either way), 91 with nothing usable online (70%; 35 have no website at all), 6 blocked. Of the 88 county planning commissions (ORC 519.12 route): 8 readable, 3 automated with nothing in the window, 58 with no agendas found online, 13 unreachable this run, 7 blocked. Licking County, the data-center county, is the hole: 2 of 25 townships readable and the county's agenda files behind a robots-closed file bank.
- **Output:** 544 documents indexed, 426 hits (385 Michigan, 41 Ohio) with the final matcher; Michigan is a data center wave (206 hits), Ohio is zoning amendments on county packets (35 of 41).
- **Precision, hand-judged, two rounds:** Michigan 29 of 30 in both rounds (0.97, Wilson 0.83 to 0.99), with none of the round-6 false-positive classes back. Ohio 14 of 30 in round 1 (0.47): one county attaches whole adopted zoning resolutions to its packets, one township's fee schedule lists battery and solar permits. After the fixes, fresh and out of sample: Ohio 24 of 29 (0.83, 0.66 to 0.92), pooled 53 of 59 (0.90, 0.80 to 0.95). The shared matcher is unchanged for the published states (regression: MA 307, NY 10, RI 33 hits before and after).
- **Lead time:** Michigan posts about four days before the meeting (CivicPlus median 4.2 days, 81% at three days or more), Ohio about six (6.2 days, 74%); both are far beyond the 18 and 24 hour notice floors and short of the 15 and 10 day hearing notices, which run in the newspaper.
- **Not sent, drafted:** unblock requests to Diligent, BoardDocs, iCompass/CivicWeb, Revize, Licking County, two Ohio and one Michigan county behind Cloudflare, and the township clerks (`great_lakes_unblock_drafts.md`).
- **Needs the owner:** send the letters; choose a Licking County route; accept the hand-chosen websites; the 40 MB document cap; the Oakland County gap; the site work in section 10 before `"gated"` comes off.

## 1. How the places were chosen

- **Michigan: every township in the twelve southeast counties** named in the plan (Washtenaw, Livingston, Oakland, Macomb, Monroe, Lenawee, Jackson, Genesee, Lapeer, St. Clair, Shiawassee, Ingham): 208 township rows, 164 of them new (the October test already held 44 of them plus cities and county rows), from Wikipedia's list of Michigan townships (type and 2020 population kept). The October test's other rows (the Thumb, Calhoun, Hillsdale and the rest) stay in the file unchanged, so `towns_mi.json` has 312 rows. Five new county rows (Oakland, Macomb, Genesee, Lapeer, St. Clair) join the seven already there, so each of the twelve counties has a county body row; the county route therefore covers every county planning commission that reviews township zoning under MCL 125.3307 in the twelve, plus the October counties.
- **Ohio: every township in Licking, Union, Franklin, Delaware, Logan, Champaign, Clermont and Butler counties**: 130 rows (Lima Township in Licking and Marion Township in Franklin are defunct and left out), all 88 county rows (county planning commission tracked, ORC 519.12 route) and one regional body, the Logan-Union-Champaign Regional Planning Commission, which reviews township zoning for three of the eight counties: 219 rows. Same-named townships carry the county in parentheses ("Liberty Township (Delaware County)"), the convention the New York file uses.
- Every row carries `selection_group` (`se_michigan`, `central_ohio`, `cincinnati_exurbs`, `county_planning`, `regional_planning`), `selection_reason`, `selection_source` and, for townships, the Wikipedia article as `selection_source_url`. Targets and sources: `data/test/great_lakes/targets_mi.json` (164), `targets_oh.json` (219), `sources/` (township lists, county census rows, website lookups, and a README on how each website was found).

## 2. Websites: how they were found, and what got in the way

Discovery needs a website per row. Sources, in the order used (`data/test/great_lakes/sources/README.md`):

1. **Web search, one query per township** (about 190 queries; the search budget ran out during the county-body lookups): the official site was taken only when the search digest named it and tied it to the right county. Ambiguous domains (bloomfieldtwp.org is Oakland County, Michigan, not Logan County, Ohio; libertytwp.org is Delaware County; miamitownship.net is Greene County; wayne-township.org is Clermont) were checked by fetching the homepage and looking for the county's name. Twenty-nine Ohio townships and nineteen Michigan townships came back with no site; those rows are `no_website`.
2. **Licking County's own per-township pages** (`lickingcounty.gov/depts/planning/zoninginfo/<twp>.htm`), with a website link for 20 of 25 townships.
3. **County and regional pages that link their townships**: Livingston (16 of 16), Oakland (21 of 21), Franklin (17 of 17), Delaware (15 of 18; its "cities" page gave the City of Delaware for eight townships, which discovery's name check caught; five were replaced by hand with the township's own domain), Clermont's township zoning pages (13 of 14), Macomb's communities page, LUC Planning's member pages (23 townships of Logan, Union and Champaign).
4. **Wikipedia infoboxes**: one page. Wikimedia answered HTTP 429 to the bot after two requests at one a second and again at one every five seconds, so Wikipedia articles were not read further (the list pages had already been read).
5. **The Michigan Townships Association directory**: the first page gave a township's website; from the second request on, the site served a "verifying your request" interstitial. Not bypassed, not used.

The county census (`research_notes/Meeting monitor national expansion/coverage_county_census.csv`) supplied the 88 Ohio county sites and the five new Michigan ones. One quirk to fix later: discovery follows a board link off the township's own host (Licking Township's trustees link points at an unrelated personal site), so the `reason` text can name a page that is not the township's; a same-host rule for board candidates belongs in `discover_sites.py`.

## 3. What was built (all additive; the published states behave as before)

- `crawler/watch351/boards.py`: `STATE_BOARD_PATTERNS["OH"]`: board of trustees and county commissioners to `select_board`; zoning commission, planning commission, regional planning commission and rural zoning commission to `planning_board` (Ohio's "regional" bodies are county-level, so they are not excluded as they are elsewhere); board of zoning appeals to `zoning_board_of_appeals`.
- `crawler/watch351/discover_sites.py`: Ohio board patterns and strict names for shared pages (`BOARD_RX["OH"]`, `BOARD_NAME["OH"]`), per-state slug hints (`STATE_SLUG_HINTS`: Ohio's zoning-commission and regional-planning paths), Ohio CivicClerk tenant guesses (`<name>cooh`, `<name>twpoh`), and the "(X County)" suffix stripped before the website-name check and the tenant guess.
- `crawler/watch351/keywords.py`: `STATE_TOPICS["OH"]`: zoning resolution amendments and ORC 519.12 citations to `zoning_amendment`; SB 52 restricted areas, the Ohio Power Siting Board and qualified energy projects (ORC 5727.75) to `clean_energy_siting`, each with an energy or siting guard. New `STATE_FALSE_POSITIVE` guards, applied to MI, VA and OH only: before the crawl, the round-6 Michigan classes (operations reports, reference lists, plan-review scope, bylaws boilerplate), each requiring the class's own words and no concrete matter nearby; after the round-1 hand check (section 6), attached adopted zoning resolutions (`_reference_code`: the document's head names a zoning resolution or ordinance with an adoption, approval or effective-date marker and nothing that reads as an agenda, minutes, hearing, draft or new ordinance), permit fee tables (`_reference_table`, `_caption_list`: a run of Title Case entries with no sentences around the term), a variance worded as "to amend the Zoning Resolution" (`_variance_only`), "raising rates ... due to data center usage" in the utility-rates guard, and, after the round-2 check, fire code fee schedule footnotes and permit tallies (`_fire_code_footnote`, `_permit_tally`). Because the matcher works page by page for these states, `find_hits` decides once per document whether it is codified text and passes that down to the page-level guards (`_state_false_positive(..., codified=)`); the first version only saw the page the match was on and let 14 Medina hits through. The shared matcher is untouched: on the cached Massachusetts, New York and Rhode Island documents the old and new matchers give the same hits (MA 307, NY 10, RI 33; `data/test/great_lakes/keyword_regression.json` for the first change, `keyword_regression_r2.json` for the second). `MATCHER_VERSION` changed twice, so the next production run re-matches its cached documents once (no downloads).
- `crawler/watch351/attribution.py`: `covered_counties` and `body_name` (a county row may carry `covers_counties` and `county_body`), `county_of` on `attribute` and `split_items` so a township filed from a regional body keeps its own county, `known_townships` over several counties and the "(X County)" suffix, `township_counties`, `bare_township` for rows with `township_bare_names` (the Delaware County RPC's "07-25.1 / Estates at Berlin Sec 1 / Berlin / 25 lots" form), and `resolve_known` for rows with `attribute_known_only` (an item is filed under a township only when the name resolves to a monitored one; before this, county packets produced "Jack Reynolds Township" and "Kinnear Road Clinton Township").
- `crawler/watch351/daily.py`: a county row's `county_body` is the hit's `board`; attribution names and counties come from every county the body covers.
- `crawler/experiments/great_lakes_test.py` (`targets`, `discover`, `annotate`, `crawl`, `analyze`, `sample`) and `great_lakes_analysis.py` (coverage three ways by county and route; output, freshness and sampling reuse `mi_va_analysis`). `experiments/gate_check.py` also checks that Ohio is gated and that `--states MI,OH` selects only those two.
- Curated listings (each says why in `curation_note`): the Jackson and Lenawee county planning commissions on the Region 2 Planning Commission site, the Genesee County Metropolitan Planning Commission, Franklin County's EDP meetings page (Planning Commission and Rural Zoning Commission), Butler County's Planning Commission agendas page, the Delaware County RPC's monthly mailing page, the LUC RPC's "This Month at LUC" page (documents dated from their text), and Licking County marked `documents_blocked` (section 5).

## 4. Coverage by county and route

Coverage is recorded three ways, as `test_mi_va.md` did, from `data/test/great_lakes/analysis_great_lakes.json` (`great_lakes_test.py analyze`):

- **Read directly**: the township's own agenda listing is automated and produced a dated document in the window (45 days back, 120 ahead).
- **Via county only**: the township is not read directly, but the county or regional planning commission that reviews its zoning amendments (MCL 125.3307 in Michigan, ORC 519.12 in Ohio) is readable. The township row carries `coverage: "via_county"`, `coverage_county_body` and a `coverage_note` that says what this does and does not catch.
- **Nothing usable online**: neither; the reason is on the row (`no_website`, `no_agendas_found`, `no_recent_agendas`, `js_only`, `website_mismatch`). "Blocked" is counted separately: a bot wall, a robots.txt rule, a vendor whose robots.txt disallows us, documents on a host we may not read, or a crawl delay above our caps. We never bypassed any of these.

### Michigan, the twelve southeast counties (208 townships)

| County | Townships | Read directly | Via county only | Either | Nothing usable online | Blocked | County body |
|---|---|---|---|---|---|---|---|
| Washtenaw | 20 | 12 | 0 | 12 (60%) | 4 | 3 | Washtenaw County Planning Commission: no agendas online (site renders client-side) |
| Livingston | 16 | 10 | 6 | 16 (100%) | 2 | 4 | Livingston County Planning Commission: readable |
| Oakland | 21 | 8 | 0 | 8 (38%) | 9 | 4 | Oakland County: no county planning commission agendas found (the county has a Coordinating Zoning Committee, not a planning commission with posted agendas) |
| Macomb | 11 | 7 | 0 | 7 (64%) | 2 | 2 | Macomb County Planning Commission: unreachable (robots.txt timed out, treated as disallow for the run) |
| Monroe | 15 | 7 | 0 | 7 (47%) | 6 | 1 | Monroe County Planning Commission: no agenda listing found |
| Lenawee | 21 | 2 | 0 | 2 (10%) | 13 | 2 | Lenawee County Planning Commission: listing works (Region 2 Planning site), but it lists only January to June 2026 packets, nothing in the window |
| Jackson | 18 | 7 | 11 | 18 (100%) | 10 | 0 | Jackson County Planning Commission: readable (Region 2 Planning site) |
| Genesee | 17 | 8 | 9 | 17 (100%) | 7 | 2 | Genesee County Metropolitan Planning Commission: readable |
| Lapeer | 16 | 3 | 0 | 3 (19%) | 8 | 3 | Lapeer County Planning Commission: no agenda listing found |
| St. Clair | 21 | 5 | 0 | 5 (24%) | 13 | 1 | St. Clair County Metropolitan Planning Commission: board page found, no dated agenda |
| Shiawassee | 16 | 0 | 0 | 0 (0%) | 13 | 0 | Shiawassee County Planning Commission: no agenda listing found |
| Ingham | 16 | 5 | 0 | 5 (31%) | 10 | 0 | Ingham County Planning Commission: blocked (robots.txt disallows the bot) |
| **Total** | **208** | **74 (36%)** | **26** | **100 (48%)** | **97 (47%)** | **22** | **6 of 24 county bodies readable** |

"Nothing usable online", how: no recent agendas on a reachable site 48, no agenda listing found 22, no website 19, client-side site 4, wrong website 4 (two expired domains, one consultant's site, and the City of Richmond's site on the Richmond Township row). Blocked, how: Cloudflare-style challenge 10, robots.txt 6, documents on a disallowed or 403 host 3, firewall 403 2, iCompass/CivicWeb 1. Six townships are automated but had no document in the window. Direct platforms: plain agenda pages 60, CivicClerk 8, CivicPlus 6.

Over all 283 Michigan township rows (the twelve counties plus the October counties): 82 read directly, 124 (44%) directly or via county, 157 nothing usable; 6 of 24 county bodies readable (Livingston, Jackson, Genesee, Calhoun, Huron, Clinton), 5 blocked (Hillsdale and Saginaw on Diligent, Tuscola on CivicWeb, Montcalm behind Cloudflare, Ingham by robots.txt), 1 unreachable (Macomb), 1 listing without documents in the window (Lenawee), 11 with no agendas found online. The `coverage` field on the township rows reads direct 80, via_county 44, none 84 (the field counts a county body as covering when its listing is automated, so Lenawee's 18 townships are `via_county` on the rows but "via county only" in the table counts only bodies that produced documents).

### Ohio, the eight counties (130 townships)

| County | Townships | Read directly | Via county only | Either | Nothing usable online | Blocked | County body |
|---|---|---|---|---|---|---|---|
| Licking | 25 | 2 | 0 | 2 (8%) | 21 | 1 | Licking County Planning Commission: blocked (agenda files behind a robots-closed file bank) |
| Union | 14 | 1 | 13 | 14 (100%) | 12 | 1 | Logan-Union-Champaign Regional Planning Commission: readable |
| Franklin | 17 | 6 | 11 | 17 (100%) | 6 | 3 | Franklin County Planning Commission (and Rural Zoning Commission): readable |
| Delaware | 18 | 5 | 13 | 18 (100%) | 12 | 0 | Delaware County Regional Planning Commission: readable |
| Logan | 17 | 0 | 17 | 17 (100%) | 15 | 0 | Logan-Union-Champaign Regional Planning Commission: readable |
| Champaign | 12 | 0 | 12 | 12 (100%) | 11 | 0 | Logan-Union-Champaign Regional Planning Commission: readable |
| Clermont | 14 | 3 | 11 | 14 (100%) | 6 | 0 | Clermont County Planning Commission: readable |
| Butler | 13 | 3 | 10 | 13 (100%) | 8 | 1 | Butler County Planning Commission: readable |
| **Total** | **130** | **20 (15%)** | **87** | **107 (82%)** | **91 (70%)** | **6** | **5 bodies readable, covering 7 of the 8 counties** |

"Nothing usable online", how: no recent agendas on a reachable site 38, no website 35, no agenda listing found 15, client-side site 3. Blocked, how: Akamai 403 2 (West Chester, Jerome), documents on a disallowed host 2 (St. Albans, Plain), robots.txt 1 (Jefferson), crawl delay above the cap 1 (Mifflin). Direct platforms: plain agenda pages 14, CivicPlus 6.

**The 88 county planning commissions (ORC 519.12 route), all of Ohio:** 8 readable (Butler, Clark, Clermont, Delaware RPC, Franklin, Medina, Warren, and the LUC RPC for Logan, Union and Champaign), 3 automated with no document in the window (Ashtabula, Madison, Preble), 58 with no agendas found online (29 reachable sites with no agenda listing for a planning or regional planning commission, 20 with a board page but no dated agenda in the window, 5 client-side sites, 1 with no website at all (Adams), 1 whose listed domain has been re-registered by a spam site (Jackson County: the census row needs a new URL), plus others), 13 unreachable this run (11 whose robots.txt timed out or answered 5xx, treated as disallow for the run under RFC 9309 and worth a retry; Ross and Summit answer 404 at the census URL), 7 blocked (Crawford, Noble, Paulding and Putnam ask a 30 s crawl delay, above our 20 s listing cap; Montgomery and Portage sit behind Cloudflare; Licking's files are behind its robots-closed file bank). Ohio counties mostly do not post planning commission agendas as documents; the ones that do are the urban and exurban counties, which is where the fights are.

## 5. What reads and what does not, county by county

**Michigan.**

- *Washtenaw* (12 of 20 direct): the strongest direct county. Saline, Augusta, Pittsfield, Ypsilanti, Lyndon, Superior, Lima, Sylvan, Dexter, Freedom, Webster and York read; the data-center fights (Saline, Pittsfield, Ypsilanti) are all in. Scio is behind Akamai, Lodi needs a crawl delay above our 10 s document cap, Salem serves documents from a 403 host, the City of Saline's robots.txt disallows us. The county planning commission's site renders client-side, so there is no county route; Washtenaw townships are direct or nothing.
- *Livingston* (10 direct, 16 of 16 either): Howell, Marion, Brighton, Conway, Genoa, Hamburg, Handy, Hartland, Oceola and Tyrone read directly; the county planning commission is readable and covers the rest (Iosco and Cohoctah behind Cloudflare, Putnam's firewall, Green Oak and the City of Howell by robots.txt, Deerfield and Unadilla with board pages but no dated agenda).
- *Oakland* (8 of 21 direct): Commerce, Novi, Oxford, Rose, Royal Oak, Springfield, Waterford and White Lake read; Bloomfield and Orion sit behind bot walls, Lyon and West Bloomfield disallow us in robots.txt; nine townships post nothing we can date. Oakland County has no planning commission that posts agendas (its Coordinating Zoning Committee reviews township amendments, and its pages gave the crawler nothing), so there is no county route here; this is the largest gap in the wave by population.
- *Macomb* (7 of 11 direct): Armada, Clinton, Harrison, Lenox, Macomb, Shelby and Washington read. Richmond Township read for most of the test, but the county's member page had given it the City of Richmond's site (a separate municipality with the same name); the round-2 hand check caught a city council item filed under the township and the row now has no website. Bruce is behind Cloudflare and Chesterfield is on CivicWeb. The county's robots.txt timed out for the run, so the county planning commission is unreachable rather than unreadable; a retry may open it.
- *Monroe* (7 of 15 direct): Berlin, Frenchtown, Ida, LaSalle, Milan, Monroe Charter and Summerfield read; Bedford's robots.txt disallows us and the City of Monroe's iQM2 answers 429. The county site has no planning commission agenda category, so no county route.
- *Lenawee* (2 of 21 direct): Clinton and Macon read; Madison is behind Cloudflare, Riga's agendas are on Mailchimp (robots-closed), four sites' robots.txt timed out, thirteen post nothing we can date or have no site. The county planning commission's packets are on the Region 2 Planning site (curated listing), but only January to June 2026 are posted, so the county route exists and is empty this window.
- *Jackson* (7 direct, 18 of 18 either): Waterloo, Grass Lake, Blackman, Leoni, Napoleon, Summit and Tompkins read; the county planning commission (Region 2 Planning site) is readable and named Summit and Waterloo township items this window.
- *Genesee* (8 direct, 17 of 17 either): Davison, Flint, Flushing, Genesee, Grand Blanc, Montrose, Richfield and Thetford read; Fenton is behind Cloudflare and Mundy's robots.txt disallows us; the Genesee County Metropolitan Planning Commission is readable (curated listing with dates read from the agenda text).
- *Lapeer* (3 of 16 direct): Arcadia, Hadley and Marathon read; Almont, Attica and Rich are behind Cloudflare; eight post nothing; the county site has no planning commission agendas.
- *St. Clair* (5 of 21 direct): Burtchville, Casco, Clyde, East China and Port Huron read; St. Clair Township's robots.txt disallows us; five townships have no website; the county's Metropolitan Planning Commission has a page but no dated agenda.
- *Shiawassee* (0 of 16): nothing. Five townships have no website, five have sites with no agenda listing, two are automated with no document in the window; the county posts no planning commission agendas. The county route is the only hope here and it is closed by absence, not by a wall.
- *Ingham* (5 of 16 direct, plus Lansing): Meridian, Williamstown, Alaiedon, Delhi and Onondaga read; Ingham County's robots.txt disallows the bot, so the county route is closed; a letter is drafted.

**Ohio.**

- *Licking* (2 of 25 direct): Etna and Liberty read (Etna's zoning commission is hearing the Harvey Farms data center text amendment). St. Albans' robots.txt disallows its own PDF folder; 21 townships post nothing we can date (six reachable sites with no listing, three with no site, the rest with board pages and no dated agenda); Newark Township's robots.txt timed out. The county planning commission's listing is readable but every file is behind the robots-closed file bank, so the county route is closed too. The data-center county is the least covered county in the wave.
- *Union* (1 direct, 14 of 14 either): only Darby reads directly; Jerome (the Intel township) is behind Akamai; seven townships have no website. The LUC RPC covers all of them for zoning amendments.
- *Franklin* (6 direct, 17 of 17 either): Madison, Norwich, Perry, Prairie, Truro and Washington read; Jefferson's robots.txt disallows us, Mifflin asks a 30 s crawl delay, Plain's documents need a delay above our cap; two sites render client-side. The county's EDP page gives both the Planning Commission and the Rural Zoning Commission (curated), and named Clinton and Franklin township items this window.
- *Delaware* (5 direct, 18 of 18 either): Berlin (data center moratorium special meeting), Genoa, Harlem, Liberty and Orange read; six townships have no website. The county's "cities" page had pointed eight township rows at the City of Delaware; the name check caught it and five were fixed by hand. The Delaware County RPC's monthly mailing is readable and names townships in its bare form ("/ Berlin /"), handled by `township_bare_names`.
- *Logan* (0 direct, 17 of 17 via LUC) and *Champaign* (0 direct, 12 of 12 via LUC): nine and seven townships respectively have no website, the rest post nothing we can date. The LUC RPC's "This Month at LUC" page (curated, dates from text) is the only route, and it is the route the law gives: every township zoning amendment in the three counties goes to LUC under ORC 519.12.
- *Clermont* (3 direct, 14 of 14 either): Pierce (the extended moratorium), Tate and Union read; four township sites answer 404 at the address the county's zoning pages give (stale links), one robots.txt timed out. The county planning commission is readable and named Goshen and Union township items this window.
- *Butler* (3 direct, 13 of 13 either): Fairfield, Liberty and Wayne read; West Chester is behind Akamai; two townships have no website. The county planning commission's agendas page (curated) is readable; the county board of commissioners is on iQM2, which disallows us.

**What the county route catches and misses, seen in the data.** County items filed under townships this window: Michigan Emmett, Summit and Waterloo (plus Fredonia, Marengo and Rubicon from the October counties); Ohio Clinton Township and Franklin Township (Franklin County), Goshen and Union (Clermont). The Medina County Planning Commission produced 38 hits in run 2 (most of them from attached whole zoning resolutions, section 6) that stay under "Medina County" because its townships are not rows. Nothing from a county body is a special land use, a site plan or a moratorium vote: those stay with the township board, as the `coverage_note` says.

## 6. Output: what the crawl read and found

Six runs on 2026-11-02 (`data/test/great_lakes/runs/`, request logs `requests_run1..6.tsv`). Run 1 was the cold crawl: 135 places, 133 ok (Clinton County's robots.txt timed out, Lake Township's listing answered 403), 591 documents listed, 516 downloaded, 25 document errors (mostly packets above the 40 MB cap), 722 requests (547 documents, 124 listings, 51 robots files), 1.36 GB, 449 seconds, at most one request a second per host and every robots rule and crawl delay honoured. Runs 2 to 6 were incremental: 2 to 10 network requests each, 265 to 283 seconds, 485 to 492 documents re-matched from the cache each time the matcher changed. The hits file validates against the production contract (`current.validate`, 0 errors).

| | Michigan (102 automated rows) | Ohio (33 automated rows) |
|---|---|---|
| Documents indexed | 395 (371 read, 24 errors) | 149 (148 read, 1 error) |
| Text source | PDF 291, OCR 51, HTML 23, DOCX 6 | PDF 122, OCR 24, DOCX 2 |
| Hits (final matcher, run 6) | 385 | 41 |
| By topic | data center 206, zoning amendment 136, battery storage 59, moratorium 54, solar 33, energy siting 19, wireless 3 | zoning amendment 35, data center 3, solar 2, moratorium 1 |
| By board | planning commission 226, township board 152, ZBA 7 | planning / zoning commission 29, trustees 11, BZA 1 |
| Places with hits | 58 | 14 |
| Hits for meetings still ahead | 23 | 13 |

The pool went from 464 hits after run 2 to 426 after run 6: the round-1 and round-2 fixes removed 27 Medina County reference-text hits, 6 Norwich fee-table hits, Hartland's MSU checklist, Harlem's permit tally and the Liberty fence variance, and one Clinton County hit re-segmented. Two hits under "Richmond Township" are the City of Richmond's (section 5, Macomb); the row is corrected but the city's documents stay in the test index until they age out.

What the hits are about, in plain terms: Michigan is a data center wave. Of the 58 Michigan places with hits, most are townships drafting, hearing or extending a moratorium on a data center ordinance (Pittsfield, Oxford, White Lake, Springfield, Meridian, Marion, Augusta, Webster, Williamstown, Genesee, Conway, Dexter, Tyrone, Ypsilanti), with battery storage riding along inside those ordinances and a smaller solar set (Bedford's PA 233 ordinance work, Oxford's accessory solar amendment, Richmond city's solar collectors ordinance). Ohio is zoning amendments on county planning commission packets (Franklin, Medina, Clermont, Butler, Delaware RPC, LUC) plus a few township items: Berlin Township's data center moratorium special meeting, Etna's Harvey Farms data center text amendment, Pierce's data center discussions, Clark County's CEDA review of Springfield Township's data center text amendment.

The county route filed items under townships this window as section 5 lists; the attribution resolves a name only when it matches a monitored township (`attribute_known_only`), so a county item about a township that is not a row (Medina's, Clark's) stays under the county body.

## 7. Precision: two rounds of hand judging (`data/test/great_lakes/precision_judgments.json`)

Definition (stricter than the Massachusetts design, as in `test_mi_va.md`): a hit is a true positive when it is a real agenda item, ordinance text, or staff or public record about the topic in the land-use or siting sense, and the matched text belongs to that matter. Text in an adopted zoning resolution attached to a packet as reference (or in the unchanged part of a whole-resolution redline) is a false positive even when the packet also carries a real amendment; the staff report or agenda line carries that. General ordinance amendments, non-land-use moratoria, utility-rate items, permit tallies and fee tables are false positives. Intervals are Wilson 95%.

| Round | Sample | Michigan | Ohio | Pooled |
|---|---|---|---|---|
| 1 (matcher as crawled in run 2) | seeded random, 30 per state, from 386 MI and 78 OH hits (`precision_worksheet_r1.json`) | 29 of 30, **0.97** (0.83 to 0.99) | 14 of 30, **0.47** (0.30 to 0.64) | 43 of 60, 0.72 (0.59 to 0.82) |
| 2 (after the round-1 fixes, fresh and out of sample) | seeded random, 30 MI from the 354 unjudged; all 29 unjudged OH hits (`precision_worksheet_r2.json`) | 29 of 30, **0.97** (0.83 to 0.99) | 24 of 29, **0.83** (0.66 to 0.92) | 53 of 59, **0.90** (0.80 to 0.95) |

**Round 1.** Michigan held at the round-6 level and none of the round-6 classes (operations reports, reference lists, plan citations, bylaws boilerplate) appeared in the 30; the one false positive was a board minute about a statute forbidding electricity rate increases due to data center usage (utility rates, not land use). Ohio was bad for two reasons that are Ohio's, not the matcher's old faults: the Medina County Planning Commission attaches a township's whole adopted zoning resolution (or a whole-resolution redline) to each packet, so accessory solar rules, wind turbine definitions, overlay purpose clauses and inspector duties produced 11 of the 16 false positives (one source, three documents, 38 hits in the pool of 78); Norwich Township's fire department fee schedule listed "Energy Storage (Battery) System" and "Solar Photovoltaic System" as permit types (3). The rest: a fence variance worded "variance to amend the Zoning Resolution", and a department activity report's already decided rooftop solar conditional use. The reference-list class did come back, in two Ohio forms the Michigan words did not cover (a fee table, a resolution's table of contents), and a cousin of the operations report appeared as a department activity report.

**Fixes between the rounds** (all in `keywords.py`, MI/VA/OH only, section 3): adopted zoning text is judged on the whole document (`_codified_doc`, passed into the page-level guards, since the matcher works page by page and the first version of the guard only saw the page it was on); permit fee tables by cue words over a wider window and by a Title Case list test; the variance wording; the utility-rates words. Every judged true positive survived the fixes (checked by re-matching the judged documents); the Massachusetts, New York and Rhode Island hits did not change.

**Round 2.** Michigan 29 of 30; the false positive is a board goals tracker's line "consider amendments to the master plan and zoning ordinance to address issues of the day, such as short-term rentals and data centers" (a work plan, not a matter). One true positive was filed under the wrong place: the Macomb County member page gave Richmond Township the City of Richmond's site, and the city council's solar collectors ordinance went under the township; the row has been corrected (no website) and discovery's name check needs to treat a same-named city as a mismatch. Ohio 24 of 29: the five false positives are two fire code fee schedule footnotes ("systems over 20 KWH for non-liquid battery systems", Norwich again), a zoning report's permit tally ("seven swimming pools, four solar"), the BZA's rooftop solar conditional use on a church (small-scale accessory solar, the class the Virginia round counted as FP), and a subdivision staff report citing an adopted text amendment's effective date. Two further guards were added after round 2 for the footnotes and the tally (`_fire_code_footnote`, `_permit_tally`); they remove three of the five Ohio false positives in the sample and no true positive, but that effect is post hoc and is not counted in the table. After them the final crawl (run 6) carries 426 hits (385 Michigan, 41 Ohio).

What Ohio precision means in practice: Ohio's pool is small (44 hits after the fixes, 35 of them zoning amendments on county planning commission packets) because Ohio townships post little and the matter that reaches us through the county route is almost always a text or map amendment. The remaining Ohio false positives are small accessory items (rooftop panels, permit counts), not the siting mistakes a developer would act on.

Round 1 also recorded label faults that do not count against precision but matter for the site: a Butler Township (MI) planning commission agenda filed under `select_board` with no meeting date; Lima Township's hearing notice under the select board; the Conway Township listing title used as the board name.

## 8. Posting lead time against the two states' notice rules

What the law requires (from `cheap_township_coverage.md` section 1 and the statutes it cites; the Open Meetings Act figures should be checked against the current text before they are printed anywhere):

- **Michigan.** The Open Meetings Act (MCL 15.265) requires a posted notice of a special or rescheduled meeting at least 18 hours ahead; it does not require the agenda itself to be posted. A zoning hearing needs a newspaper notice at least 15 days ahead (MCL 125.3103). A township zoning amendment goes to the county planning commission after the township planning commission's hearing and before the township board votes; the county has 30 days (MCL 125.3307), so a county agenda shows the amendment in the weeks between the two township meetings.
- **Ohio.** The Open Meetings Act (ORC 121.22) requires 24 hours' notice of a special meeting to anyone who asked; regular meetings follow a published schedule. A township zoning commission's hearing on an amendment needs a newspaper notice at least 10 days ahead, and the trustees' hearing another 10 days (ORC 519.12); the county or regional planning commission's recommendation is due before the zoning commission's hearing, which falls 20 to 40 days after the amendment is initiated. So the county route in Ohio runs ahead of the first township hearing, where in Michigan it runs between the two.

What the documents show (lead time = meeting date minus the posting stamp; `analysis_great_lakes.json`, `freshness`):

| Source of the posting time | Michigan | Ohio |
|---|---|---|
| CivicPlus "posted" stamp | n 26, median 4.2 days, 81% at 3 days or more | n 31, median 6.2 days, 74% at 3 days or more |
| CivicClerk publishOn | n 52, median 3.6 days, 65% at 3 days or more | (no CivicClerk sites read) |
| PDF modification date | n 300, median 4.2 days, 70% at 3 days or more | n 141, median 6.3 days, 72% at 3 days or more |
| HTTP Last-Modified | n 209, median 3.5 days, 63% | n 107, median 6.3 days, 64% |
| Revize upload stamp | n 56, median 3.2 days, 57% | n 17, median 1.4 days, 41% |
| Our first fetch, upcoming meetings only | n 32, median 4.2 days | n 53, median 7.2 days |

Michigan posts about four days ahead, Ohio about six: both comfortably beyond the 18 and 24 hour notice floors, and both short of the 15 and 10 day hearing notices, which is expected (the newspaper notice runs before the agenda is written). Share of dated documents for meetings still ahead at the end of the crawl: Michigan 9% (34 of 366), Ohio 36% (53 of 148): Ohio's county packets and CivicPlus townships post further ahead, Michigan's townships post the agenda the week of the meeting and the minutes afterward. A daily crawl catches the Michigan agenda about four days out; a resident who wants the 15-day hearing notice needs the newspaper, not us.

## 9. Customers to approach first

From `where_it_pays_2026.md` section 4, recommendation 3, read against what this wave can actually show:

- **Michigan solar and storage developers choosing between a township permit under a CREO and the MPSC under PA 233** (Invenergy, Ranger Power, Apex, DTE's and Consumers' project teams). What they get now: the township planning commission and board agendas of 74 of 208 southeast townships read directly, and the county planning commission's 30-day review (MCL 125.3307) for the townships of Livingston, Jackson, Genesee, Calhoun, Huron and Clinton counties, which shows a zoning text amendment (a CREO, a solar or battery ordinance, a data center ordinance) between the township's two hearings. The Michigan hits this window are dominated by data center ordinances and moratoria (data centers in 206 of 385 hits, zoning amendments 136, battery storage 59, moratoria 54, solar 33), which is the same board calendar a solar developer watches.
- **Michigan land-use counsel who publish on PA 233** (Foster Swift, Varnum) and the **Michigan Townships Association** (its sample moratorium ordinance turned up in Brighton Township's packet). The pitch to them is the county route itself: one feed of every township zoning amendment a county planning commission reviews, labelled by township.
- **Ohio: the Licking County data-center developers and QTS, Bricker Graydon, Vorys, the Ohio Township Association, and Columbus-area solar developers facing SB 52 county votes.** Be honest about Licking County first: 2 of its 25 townships read directly (Etna, where the zoning commission is hearing the Harvey Farms data center text amendment, and Liberty), St. Albans' PDF folder is robots-closed, 21 townships post nothing we can date, and the county planning commission's agenda files sit behind a robots-closed file bank, so until Licking County answers the letter the Licking feed is two townships' agendas and nothing else. The strong Ohio coverage this window is Franklin, Delaware, Butler and Clermont counties (county planning commission packets plus the townships that post on CivicPlus), which is where the Columbus and Cincinnati exurb fights are, and the LUC RPC for Logan, Union and Champaign, where the bans came "en masse". SB 52 restricted-area votes are county commissioner items; the county rows track the commissioners' agendas only where the county site exposes them, so an SB 52 product needs the 88 county sites opened (section 5), not more townships.
- Order: the two Michigan groups first (coverage is tested twice and precision is high), then Franklin, Delaware, Butler and Clermont in Ohio, then Licking once its file bank is open.

## 10. Site support needed (a spec, not edits)

Nothing below is built. It is what the site needs before `"gated"` can come off `data/towns_mi.json` and `data/towns_oh.json`. `build.py`, `styles.css` and `site/` were not touched in this wave.

### State names

- `MI` = Michigan, `OH` = Ohio wherever the site spells a state out (town pages, topic pages, feeds, the state picker, email subjects). Both files carry `"state"` at the top and on every row.
- Ohio and Michigan rows are townships, cities and counties, not towns. The word "town" in page copy ("this town", "towns near you") should read from a per-state noun: `township` for `kind: township`, `city` for `kind: city`, and the county body's own name for `kind: county`.

### Board labels

The crawler keeps the shared keys (`select_board`, `planning_board`, `zoning_board_of_appeals`) so feeds and filters do not change. The labels shown should come from a per-state table instead of `BOARD_LABELS`:

| key | Michigan | Ohio |
|---|---|---|
| `select_board` | Township Board (or Board of Trustees); City Council / City Commission for cities | Board of Trustees; City / Village Council for cities and villages; Board of County Commissioners for counties |
| `planning_board` | Planning Commission | Zoning Commission (township); Planning Commission or Regional Planning Commission (county) |
| `zoning_board_of_appeals` | Zoning Board of Appeals | Board of Zoning Appeals |

The hit's own `board` field carries the real name as the listing printed it ("Delaware County Regional Planning Commission", "Zoning Commission"), so where the site shows `board` it is right already; where it shows the label for the key, it needs the table. Two label faults seen in the sample should be fixed in the crawler, not the site: a Butler Township (MI) planning commission agenda filed under `select_board` with no meeting date, and Lima Township's hearing notice filed under the select board.

### "Via county" coverage, shown honestly

Township rows carry `coverage` (`direct`, `via_county`, `none`), `coverage_county_body` and, for `via_county`, `coverage_note`. The site should:

- On a `via_county` township page, say in plain words that we do not read this township's own agendas, and that zoning text and map amendments reach us through the named county or regional body because state law routes them there (Michigan MCL 125.3307, Ohio ORC 519.12). The `coverage_note` field is that sentence. It must also say what we will not see: special land uses, site plans, conditional uses, moratorium votes taken by the township board itself, and anything the county body does not review.
- Never show a `via_county` township with the same badge as a `direct` one. Three states, three looks: read directly; zoning changes via county; not covered.
- On a `none` township page, say the township posts no agendas we can read, and name the county body if one exists but is not readable (the reason is in `reason` on the row: a vendor, a bot wall, a robots rule, or nothing posted).
- A hit filed under a township from a county agenda carries the county body in `board`. The hits contract has no field that names the county row it came from; add an optional `attributed_from` (the county row's `town`) to `current.validate` so the item line can say "at the Calhoun County Planning Commission" and a resident does not go to the township hall for a county meeting. Until then the site can detect these items by `board` naming a county or regional body while `town` is a township.
- The county body's own page should list the township items it reviewed and link each to the township page.

### Township versus county pages

- A county body row (`kind: county`) is a place of its own: its page lists its meetings and items, plus the townships it covers (`covers_counties` on a regional body; else its own county) with each township's `coverage`.
- A township page shows its own meetings (if `direct`), then "At the county" items attributed to it, in date order, each marked as a county meeting.
- Same-named townships carry the county in parentheses in `town` ("Liberty Township (Delaware County)", "Fairfield Township (Lenawee County)"). The page title should print the name without the parentheses and the county on the next line; the id stays as the row name.
- Cities inside a county (Lansing, Saline, Howell) are `kind: city` and never get a county-route badge; county review does not apply to them.

### The map

- Michigan and Ohio need county-subdivision shapes (US Census `cb_2024_26_cousub_500k` and `cb_2024_39_cousub_500k`, the same vintage as `data/neighbors.json`), not place shapes: townships are the units. Cities inside townships are separate subdivisions in the Census file and should take the city row where one exists.
- Fill by `coverage`: solid for `direct`, hatched or lighter for `via_county`, empty for `none`. The legend must say what hatched means in one line, the same words as the township page.
- The free-area rule (one town plus neighbors) needs `data/neighbors.json` rows for MI and OH; `tools/neighbors.py` takes the two state FIPS codes and the duplicate-name suffix convention above.

### Topics

- `clean_energy_siting` carries Michigan PA 233 / CREO items, Ohio SB 52 restricted-area votes and Ohio Power Siting Board references. The topic label on MI and OH pages should not read "Consolidated permit / 225 CMR 29": that is Massachusetts law. A per-state label: Michigan "Energy siting (PA 233, special land use)", Ohio "Energy siting (SB 52, OPSB)".
- `zoning_amendment` in Ohio includes "zoning resolution" amendments (townships zone by resolution); the label "Zoning / bylaw amendment" should read "Zoning amendment" outside New England.

## 11. Unblock requests (drafted, not sent)

`research_notes/Expansion/great_lakes_unblock_drafts.md`: letters for Diligent (Hillsdale and Saginaw county planning commissions, Camden Township), BoardDocs (Jackson County board), iCompass/CivicWeb (Tuscola County, Chesterfield Charter Township), a note on Granicus/iQM2 (Butler County OH board, City of Monroe), the Cloudflare-walled counties (Montgomery and Portage in Ohio, Montcalm in Michigan) and townships, Licking County's robots-closed file bank, the robots.txt disallow list (with a single ask to Revize for its default file), document hosts the listing does not control, and the counties and townships whose crawl delay is above our caps. The order to send is at the end of that file.

## 12. Files changed or created in this wave

Changed (all additive):
- `projects/351watch/crawler/watch351/boards.py` (Ohio board patterns)
- `projects/351watch/crawler/watch351/discover_sites.py` (Ohio board regexes and names, `STATE_SLUG_HINTS`, Ohio CivicClerk guesses, "(X County)" stripping)
- `projects/351watch/crawler/watch351/keywords.py` (`STATE_TOPICS["OH"]`, the round-6 and round-1 guards, `_UTILITY_RATES`)
- `projects/351watch/crawler/watch351/attribution.py` (`covered_counties`, `body_name`, `county_of`, `bare_township`, `resolve_known`, `township_counties`)
- `projects/351watch/crawler/watch351/daily.py` (`county_body` as the hit's board, attribution over covered counties)
- `projects/351watch/crawler/experiments/gate_check.py` (Ohio gate checks)
- `projects/351watch/data/towns_mi.json` (124 to 312 rows; `coverage`, `coverage_county_body`, `coverage_note`, `attribute_known_only` on county rows)
- `research_notes/Expansion/great_lakes_unblock_drafts.md`

Created:
- `projects/351watch/data/towns_oh.json` (219 rows, gated)
- `projects/351watch/crawler/experiments/great_lakes_test.py`, `great_lakes_analysis.py`
- `projects/351watch/data/test/great_lakes/`: `targets_mi.json`, `targets_oh.json`, `sources/` (README, township lists, county census rows, website lookups), `hits_great_lakes.json`, `first_seen.json`, `state/` (the test index and town health), `posted_stamps_mi.json`, `posted_stamps_oh.json`, `requests_run1..6.tsv`, `runs/run_run1..6.json` and `runs/hits_run2.json`, `analysis_great_lakes.json`, `keyword_regression.json`, `keyword_regression_r2.json`, `precision_worksheet_r1.json`, `precision_worksheet_r2.json`, `precision_judgments.json`
- `research_notes/Expansion/great_lakes_wave.md` (this note)

Not touched: `data/towns_ny.json`, `data/towns_va.json`, `data/towns_md.json`, `data/test/wave2/`, `data/test/va_md/`, `build.py`, `styles.css`, `site/`. No git commands, no deploy, no `ops/daily.sh`.

## 13. Notes, and what needs the owner's decision

Notes:
- `MATCHER_VERSION` changed (keywords.py was edited), so the next production run re-matches its cached Massachusetts, New York and Rhode Island documents once, without downloads. The regression says the result is identical (MA 307, NY 10, RI 33 hits before and after). The production daily run already ran once today with the first of these edits in place.
- The container's disk filled during the work (other sessions' worktrees and caches share the volume); `pip cache purge` and `uv cache clean` freed 391 MB, and space came back later. Between run 2 and run 3 the bodies of about 20 cached documents disappeared from `crawler/.cache` (not by this session); the daily run keeps those documents' run-2 hits and does not re-fetch them until their listing changes. Nothing was lost from the index.
- The web search budget (200 queries a turn) ran out during the county-body lookups; the remaining probing used the crawler itself on known URLs.
- Seven Michigan packets are above the 40 MB document cap (Brighton 166 MB, East China 81 MB, Delta 59 MB and others, `runs/run_run3.json`, `documents_too_large`); they are the full board packets of the townships most active on data centers.
- Rows carried over from the October test keep their October `reason` wording ("351WatchBot"); the current user agent is AgendaAheadBot.
- `coverage_county_census.csv` has a re-registered spam domain for Jackson County, Ohio (`jerukbet-fresh.com`); the row needs the county's real site.
- Discovery accepts a board link that leaves the township's host (Licking Township, Ohio); a same-host rule for board candidates is a small follow-up in `discover_sites.py`. Its website-name check also passed the City of Richmond's site for Richmond Township (Macomb) because the page names "Richmond"; a same-named city or village should count as a mismatch for a township row. Richmond Township's two solar hits in the test runs up to run 5 are the city council's, and the row was corrected before run 6.

Decisions needed:
1. **Send the unblock letters** in `great_lakes_unblock_drafts.md`, in the order given there (Diligent, Revize, Licking County, the Cloudflare counties, the township clerks). Nothing has been sent.
2. **Licking County's route.** With the file bank closed and 23 of 25 townships dark, the choices are: send the letter and wait; read the planning commission's agenda dates from the listing and show "meeting, items unknown"; or ask the planning department for an email copy of each agenda. The second is honest but thin; the third is manual.
3. **Hand-chosen domains.** Twenty Ohio and a handful of Michigan township websites came from a web search digest or were typed in by hand after the county's page gave the wrong one (Delaware County). Each is marked in `website_source`. Accepting them means trusting the digest's "official site" line; the name check caught the known mismatches.
4. **The 40 MB document cap.** Raising it to 200 MB would read the seven large Michigan packets (about 600 MB a crawl day at worst); keeping it means those boards are covered by their agenda PDFs only when the township posts one separately.
5. **The Oakland County gap.** No county route exists (the Coordinating Zoning Committee posts no agendas we can read) and 13 of 21 townships are dark or walled; the only ways in are the four letters (Bloomfield, Orion, Lyon, West Bloomfield) and the county's own site.
6. **Whether the `via_county` label is acceptable on the site** as specified in section 10 before any of this goes live; the crawler side is done, the site side is not.
