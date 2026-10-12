# 351 Watch: Michigan and Virginia test

- **Run date:** 2026-10-12. The first test ran, then a fix round, then a re-test on the same day.
- **Crawl window:** meetings from 2026-08-28 to 2027-02-09 (45 days back, 120 days ahead).
- **Places:** 185, in two test areas:
  - Michigan: southern Michigan townships plus the Thumb.
  - Virginia: Southside and Piedmont counties.

**Question.** Does the crawler work well enough in these two areas to expand into them?

**Short answer after the fix round:** Virginia passes every criterion. Michigan still fails two:

- **Precision on a fresh sample:** 88.3% in Michigan, against a 90% bar.
- **Township coverage:** 31.5% read directly, against a 35% bar.

Both states stay gated and off in production.

## Re-test after the fix round

### Pass/fail

| Criterion | Result | Verdict |
|---|---|---|
| Precision ≥90% in each state, out of sample | A fresh random sample of 60 hits per state, drawn before any further change, from documents never hand-checked before.<br>**MI 53/60 = 88.3%** (95% interval 78–94%)<br>**VA 56/60 = 93.3%** (84–97%)<br>Counting a hit right only if every topic tag is right: MI 83.3%, VA 90.0% | **MI FAIL, VA PASS** |
| Crawl errors <5% of attempted places | 1 of 185 places unreachable (0.5%): Shiawassee Township's robots.txt timed out.<br>0 of 80 crawled places failed in any of 3 re-test runs.<br>Document-level: 19 of 382 documents (5.0%), of which 17 are packets over the 40 MB cap. | **PASS** |
| VA ≥50% of target counties readable | 27/32 = **84.4%**<br>By body: 50 of 96 county boards = 52%, up from 49 | **PASS** |
| MI ≥35% of target townships readable | Direct: **39/124 = 31.5%**, up from 37.<br>Via county items: target townships named in a county planning commission item this window add Leroy, so direct or via county items is 40/124 = 32.3%.<br>Over a 105-day window, county items also reach Putnam, which blocks us directly, plus Brighton and Tyrone.<br>Counting every township whose county planning commission we read (the MCL 125.3307 review route): 60/124 = 48.4%. | **FAIL** on direct and on direct-or-county-items<br>**PASS** only if the county review route counts |
| Output validates against the contract | `current.validate` on `data/test/hits_mi_va.json`: 0 errors | **PASS** |
| MA hit counts unchanged | Final matcher against `keywords.py` at af1e10d on all 3,105 cached MA, NY and RI documents: MA 1,063, NY 28, RI 109 hits; **0 documents differ** | **PASS** |

### What the fix round changed

**0. Merge.** `claude/massachusetts-market-service-ead9ho` at 210d7a1 is merged into this branch. Its changes are all kept:

- Web Bot Auth signing (`botauth.py`, hooked into `fetch.py`);
- the AgendaAheadBot rename, with robots.txt rules for 351WatchBot still obeyed;
- full-text persistence (`fulltext.py`, the `daily.py` and `ops/daily.sh` hooks);
- `data/archive`.

The only conflict was in `OPERATIONS.md`, where both new sections were kept.

One small fix rides along. `PoliteFetcher.allowed()`, which discovery uses, now checks the 351WatchBot rules too, as fetching already did. Test crawls write their full-text rows to `data/test/**/search/`, which is git-ignored.

**1. Precision: sections before matching** (`keywords.py`; Michigan and Virginia only, so Massachusetts is unaffected).

- **Page classes.** Each page (pdftotext and tesseract separate pages with a form feed) is classified and matched on its own:
  - **agenda:** agenda markers, or a page right after an agenda page that still carries one;
  - **minutes:** motion, seconded, roll call vote, "stated that", "discussed";
  - **ordinance:** sections, definitions, "shall", whereas / be it resolved;
  - **noise:** newsletter, invoice or ledger, permit or inspection log, assessor card, audit, case-law digest, resume, or use table;
  - **attachment:** everything else.
- **Rules by class.**
  - Noise pages are skipped.
  - On attachment pages a match needs action or regulatory words, or a project name, nearby. It must also not be one entry in a comma list of unrelated topics, as in an administrator's report.
  - Agenda, minutes and ordinance pages are matched as before.
  - Guards now look only within the page, so a newsletter on the next page no longer cancels a real agenda item.
- **Gas-fired power plants** being sited map to `clean_energy_siting`. The pattern covers combined-cycle stations, gas-fired power plants, peaker plants and power-plant ordinances. Guards require siting words nearby and drop a utility's fleet descriptions. ARCHITECTURE requires site support before any new topic key.
- **In sample** (the 350 hits judged in rounds 1–4, on which these rules were designed):

  | | MI | VA |
  |---|---|---|
  | Precision | 98.0% | 95.3% |
  | True positives kept | 97.3% | 94.7% |

  These numbers overstate. The out-of-sample result in the pass/fail table is the one that counts.

**2. Michigan coverage**

- **County items split per township** (`attribution.split_items`). A county planning commission's item list ("a. 08-26-01, Fredonia Township: Zoning Text Amendment b. 08-26-02, Marshall Township: Zoning Map Amendment …") now gives one hit per named township. The county body stays as `board`.
  - In this window the Calhoun County agendas give hits for Fredonia, Marshall, Leroy, Emmett (two items) and Marengo townships.
  - Over the extended window, Livingston County's agendas add Brighton, Tyrone and Putnam rezonings and moratorium text amendments.
  - A township mention is now mapped only to a township row. "Marshall Township" was being filed under the City of Marshall.
- **Crawl-delay cap of 20 s for listing pages only** (`fetch.LISTING_CRAWL_DELAY_CAP`). This applies wherever the fetch purpose is "listing", including site discovery. Documents keep the 10 s cap: a listing that a slow host serves is used only when its documents live on another host, or on a host within 10 s. Of the 6 places blocked by crawl-delay:

  | Place | Crawl-delay | Result |
  |---|---|---|
  | Hartland Township | 15 s | Readable |
  | Hamburg Township (Municode Meetings) | 15 s | Readable |
  | Town of Warrenton (Municode Meetings) | 15 s | Readable |
  | Cato Township | 20 s | Still blocked: documents on the same host need more than 10 s |
  | Fluvanna County | 15 s | Still blocked: documents on the same host need more than 10 s |
  | Washtenaw County | 20 s | Homepage renders client-side; its CivicClerk portal has no planning commission |

  This cap is a production change too: an MA, NY or RI listing host asking for 10–20 s would now be read rather than skipped. All configured production listings already worked under 10 s.
- **A bug found and fixed.** Portland Township had been given the City of Portland's CivicClerk portal (`portlandmi`), whose files come back empty. Discovery no longer guesses `<name>mi` for a township, and it rejects a probed tenant whose events never say "township". Portland is now `no_recent_agendas`.
- **Not posting.** Monroe, Lenawee and Eaton counties keep CivicClerk portals with no planning commission, and Washtenaw's has none either. Their planning commission agendas are not published openly.

**3. Virginia Planning Commissions** in the 8 counties where only the Board of Supervisors was readable:

| County | Finding |
|---|---|
| Southampton | **Now read.** The planning commission posts one page per meeting under a page per year (`year_{year}.php`): staff reports, CUP applications, a draft data center ordinance. Added by hand. The reader now also skips a `{year}` page that does not exist yet, instead of failing. |
| Prince Edward | **Listing added.** The packets page sits under Community Development, which discovery's hub search did not reach. The latest packet is for August 18, just before the window. |
| Amelia | Listing works; no meeting since July 27. |
| Appomattox | Listing works (CivicClerk): the August 12 meeting falls before the window and September was cancelled. |
| Lunenburg | Last posted planning commission agenda is from May 2025. |
| Nottoway | Last posted is from March 2026. Planning commission minutes appear inside Board of Supervisors packets, which we read. |
| Sussex | Last posted is from December 2024. |
| Surry | No planning commission agendas on its CivicClerk portal or its AgendaCenter. |

The last four do not publish current planning commission agendas openly.

**4. Oversized packets** are skipped, not read in part. Each run report now lists them in `documents_too_large`, read from the index so they stay visible after the first attempt. There are 17 in this window, at Brighton, Delta, Hamburg, Hartland, Howell, Meridian, Pittsfield, Superior, Ypsilanti, Greensville and Halifax.

### Precision re-test (round 5)

**How the sample was drawn.**

- An extended crawl read meetings from 2026-06-29, 105 days back, into `data/test/extended/`.
- The sample came from hits in documents that were not in the rounds 1–4 index, excluding every hit judged before. That leaves 201 Michigan and 333 Virginia hits.
- It is a seeded simple random sample (seed 2026) of 60 per state, drawn before any change. Every hit was equally likely; rounds 1–4 had sampled round-robin over towns.
- Each hit was judged from about 1,500 characters of document context, under the same strict definition as before. The definition is in the precision section of the first test, below.
- Judgments and one-line reasons are in `data/test/precision_judgments.json` (round 5). The worksheet is `data/test/extended/precision_worksheet_r5.json`.

| | MI | VA |
|---|---|---|
| True positives / judged | 53 / 60 | 56 / 60 |
| Precision | **88.3%** | **93.3%** |
| All topic tags right | 50 / 60 = 83.3% | 54 / 60 = 90.0% |

**False positives in round 5, the next fix list:**

- **Michigan:**
  - two fiber right-of-way permits ("telecommunications facilities"; Lightpath), where no fiber word sits near the term;
  - a rezoning staff report's list of permitted uses;
  - a utility's map legend of existing substations;
  - a light-fixture spec sheet ("solar power battery available");
  - a job description ("legal notices for rezoning, ordinance amendments");
  - a hydro-operations note that ITC will rebuild an existing line. This note was also a false positive in round 2.
- **Virginia:**
  - a public comment where "data centers" is rhetorical;
  - a blank application form's questions;
  - a public-utility service yard SUP, where "transmission line" only describes the use;
  - a parks plan naming data-center proffers as a funding source.

**Recall of real items held.** The re-test still finds:

- **Michigan:**
  - the Huron County Pinesap Solar special approval;
  - the Genoa, Gilford, Brighton, Bedford, Lake and Milan moratoria;
  - the Marshall Solar special land use;
  - the BWL 37-acre solar site plan in Delta Township.
- **Virginia:**
  - Southampton's White Solar Plus Storage CUP (20 MWac with 8 MW / 32 MWh of storage) and its draft data center ordinance;
  - Cumberland's 3 GW gas plant CUP and 15.2-2232 finding, now under `clean_energy_siting`;
  - Hanover's proposed zoning amendment to allow data centers;
  - the Blunts Bridge Solar CUP;
  - Sussex's Blackwater Solar siting agreement;
  - the Warrenton substation-expansion SUP.

### Re-test output and reliability

| | Michigan | Virginia |
|---|---|---|
| Places crawled | 49 | 31 |
| Documents indexed | 205 (191 read: PDF 148, OCR 23, HTML 15, DOCX 5) | 177 (172 read: PDF 154, OCR 17, DOCX 1) |
| Hits | 219 in 30 places (48 for meetings ahead) | 252 in 26 places (62 for meetings ahead) |
| By topic | data_center 96, zoning_amendment 87, moratorium 34, battery_storage 28, solar 17, clean_energy_siting 16, wireless_telecom 4 | zoning_amendment 114, solar 74, clean_energy_siting 51, data_center 33, battery_storage 30, wireless_telecom 17, moratorium 1 |

| Run | What it was | Runtime | Requests | Bytes | Places ok |
|---|---|---|---|---|---|
| retest (first pass) | Index wiped and re-crawled with the fix-round code | 150 s | 143 (72 listing, 70 document) | 261 MB | 81/81 |
| retest1 | The same, after the Portland fix, from the warm cache | 134 s | 72 | 3 MB | 80/80 |
| retest2 | Immediately after: 380 of 382 already indexed, **0 new** | 77 s | 5 | 0.8 MB | 80/80 |
| retest_cold | Empty fetch cache, index kept: a fresh container the next day | 86 s | 241 (82 robots.txt, 156 listing, 3 document) | 33 MB | 80/80 |
| extended | Meetings from 2026-06-29, for the fresh precision sample | 312 s | 644 | 1.65 GB | 81/81 |

- Network errors: 0 in every run.
- The second run is incremental.
- Hosts on the 15–20 s listing delay did not lengthen the daily pass noticeably: the cold run takes 86 s.

**Freshness.** On first-publish sources, the median posting lead is:

| Source | MI | VA |
|---|---|---|
| CivicPlus "Posted" stamps | 3.5 days | 4.2 days |
| CivicClerk `publishOn` | 2.4 days | 4.5 days |

About 19–20% of dated documents were for meetings still ahead on the crawl day.

### What would fix what is left

1. **Michigan precision**, the four repeat classes from round 5:
   - fiber right-of-way agreements: require tower words for `wireless_telecom` in an attachment, not only the absence of fiber words;
   - job descriptions and blank forms: add a noise genre;
   - utility map legends and spec sheets: add a noise genre;
   - utility rebuild notes in operations reports: treat "rebuild" of an existing line as no siting.

   Then draw another fresh sample. The extended window still holds 141 unjudged Michigan hits from new documents, and the next month of meetings will add more.
2. **Michigan coverage** is now limited by what townships publish, not by the crawler.
   - The 72 townships with nothing usable online (21 no website, 30 minutes only or stale, 18 no agenda page, 2 domains gone, 1 JavaScript-only) need another source: statutory newspaper hearing notices (MCL 125.3103), or county planning commission review.
   - The county route already reaches 48% of target townships structurally.
   - Permission from Diligent (Hillsdale, Saginaw, Camden), BoardDocs (Jackson) and iCompass (Tuscola) would open 4 more county planning commissions. Those counties hold 33 target townships, 27 of which we cannot read directly today.
3. **The bar itself.** Strict direct readability (31.5%) and county-reviewed coverage (48.4%) measure different things. A Michigan launch could promise township zoning amendments through the county route and full agendas only where a township posts them.

## First test (before the fix round)

The sections below describe the first test as it ran, with the first matcher. Its pass/fail table and short answer follow. Coverage, output, freshness and reliability numbers in these sections are from the first test.

**Short answer (first test):** Virginia yes, Michigan only partly. Precision was close to the bar but not over it in either state.

- **Virginia reads well.**
  - 27 of 32 target counties are readable (84%), and so are 3 of 5 towns.
  - Most counties run on open platforms: CivicPlus (10), CivicClerk (9), and the new general agenda-page reader (8).
  - The crawl found the items that matter, including:
    - Halifax's 69 MW CEP Solar conditional use permit;
    - King George's Gibson Solar special exception;
    - Henry County's solar siting agreements and Data Center District ordinance;
    - Mecklenburg's BESS siting agreement;
    - Greensville's BESS zoning text amendment;
    - Caroline's rezoning to M-1 for a technology campus;
    - opposition to the Valley Link 765 kV line.
- **Michigan townships are mostly not online.**
  - 37 of 124 target townships (30%) have agendas we read in the window. That is below the 35% bar.
  - 71 townships post nothing usable:
    - 21 have no website;
    - 29 post only minutes, or nothing recent;
    - 18 have no agenda page;
    - 2 domains now belong to someone else;
    - 1 site is JavaScript-only.
  - Where the fights are, coverage is good: 13 of the 17 fight townships are readable (76%).
  - The four readable county planning commissions add 23 more townships indirectly, through the county's MCL 125.3307 review of township zoning amendments. That is how the 150 MW Pinesap Solar project in Rubicon Township surfaced.
- **Precision is just under the 90% bar in both states.** We hand-checked 350 hits over four rounds, each round a fresh sample drawn before that round's fixes:
  - After the first fixes, the pooled precision of the three held-out rounds is **85.4% in Michigan** and **88.5% in Virginia**.
  - Re-scored with the final matcher, all 350 judged hits come out at 94.9% and 93.7%. That figure is in-sample, because the fixes were tuned on these hits, so it overstates.
  - Most false positives that remain are packet attachments, not agenda items: newsletters, invoices, use tables, permit logs, and passing mentions in administrators' reports.
- **Production is untouched and Massachusetts is unchanged.**
  - The MI and VA towns files are gated, so the daily run cannot read them.
  - Output goes only to `data/test/`.
  - Keyword matching on the 3,105 cached MA, NY and RI documents is identical before and after the change: 0 documents differ.

### Pass/fail (first test)

| Criterion | Result | Verdict |
|---|---|---|
| Precision ≥90% in each state | Held-out, pooled rounds 2–4: MI 111/130 = **85.4%**, VA 115/130 = **88.5%**<br>Last round alone: MI 77.5%, VA 90.0%<br>In-sample with the final matcher: MI 94.9%, VA 93.7% | **FAIL** (both states) |
| Crawl errors <5% of attempted places | 1 of 185 places unreachable (0.5%): Shiawassee Township's robots.txt timed out.<br>0 of 78 crawled places failed in any of 5 runs.<br>Document-level: 19 of 338 documents (5.6%), of which 14 are packets over the 40 MB cap. | **PASS** |
| VA ≥50% of target counties readable | 27/32 = **84.4%**<br>Counted by body: 49 of 96 county boards = 51% | **PASS** |
| MI ≥35% of target townships readable | 37/124 = **29.8%** read in the window<br>42/124 = 33.9% have a working listing<br>With the county planning commission route: 48.4% | **FAIL** |
| Output validates against the contract | `current.validate` on `data/test/hits_mi_va.json`: 0 errors | **PASS** |
| MA hit counts unchanged | Old = new on every cached document: MA 1,063, NY 28, RI 109 hits; 0 documents differ | **PASS** |

## How the places were chosen

The targets, with a reason for each row, are in `data/test/targets_mi.json` and `data/test/targets_va.json`. Each row carries `selection_group`, `selection_reason` and `selection_source`. The same fields are copied into the gated `data/towns_mi.json` and `data/towns_va.json`.

**Michigan: 148 places**, from `energy_siting_hotspots.md` areas 1 (southern Michigan) and 4 (the Thumb). They span 19 counties.

| Group | Places | How they were chosen |
|---|---|---|
| fight | 17 townships | Places with live fights:<br>• Sabin Center restriction clusters (Monroe County: 10 restrictions)<br>• data-center fights: Saline (Stargate), Augusta (Thor), Ypsilanti (U-M / Los Alamos), Howell, Pittsfield<br>• the Iosco Solar cancellation<br>• Almer Township, lead appellant against the MPSC PA 233 order<br>• Meridian's BESS moratorium |
| mta_sample | 80 townships | Michigan Townships Association directory, limited to the 19 counties: 62 drawn at random (seed 7), plus 18 from the first pass |
| county_list | 27 townships | The rest of Livingston (data-center cluster) and Tuscola (Thumb, PA 233), from the county municipality pages, so two counties are complete |
| city | 5 | Lansing (data-center moratorium), Saline and Howell (next to fight townships), Monroe and Marshall (county seats; Marshall hosts the BlueOval battery plant) |
| county_planning | 19 county planning commissions | The 19 counties. A county planning commission reviews township zoning amendments (MCL 125.3307) and, in some counties, special approvals, so its agenda names township items. |

**Virginia: 37 places.**

| Group | Places | How they were chosen |
|---|---|---|
| southside | 21 counties | `energy_siting_hotspots.md` area 2: Pittsylvania, Halifax, Mecklenburg, Charlotte, Brunswick, Lunenburg, Nottoway, Prince Edward, Appomattox, Campbell, Henry, Greensville, Sussex, Southampton, Dinwiddie, Surry, Isle of Wight, Cumberland, Buckingham, Amelia, Powhatan |
| piedmont | 11 counties | Area 9: Culpeper, Fauquier, Orange, Louisa, Spotsylvania, Caroline, Hanover, Goochland, Fluvanna, King George, Madison |
| town | 5 | Culpeper and Warrenton (data-center fights); Farmville, South Hill and South Boston (Southside towns with their own planning and zoning) |

Every county is tracked for three bodies: Board of Supervisors, Planning Commission and BZA. Every township, city and town is tracked for its governing board, planning commission and ZBA. A Michigan county is tracked for its planning commission only.

## What was built

All code is in `projects/351watch/crawler/`. Every request goes through `fetch.PoliteFetcher`.

**Adapters and discovery**

- **`watch351/adapters/agenda_page.py`: the general agenda-page reader.** It works on any HTML page that links documents: WordPress, Revize, Wix, CivicPlus document pages, plain sites.
  - It classifies each document link as agenda, packet, notice, minutes or cancellation, and prefers agendas and packets.
  - It takes the meeting date from the link text, the file name (compact, glued and dashed forms), the row, or the nearest heading. It falls back to a month-only date ("October 2026 Agenda"). It can also read the date from the document itself.
  - It follows year folders and per-meeting pages, and treats a meeting page with the agenda inline as a document.
  - It filters boards on shared pages (`board_pattern` / `board_exclude`) and skips documents outside the window.
  - It keeps posting evidence where a site shows it: Revize upload stamps, WordPress upload months, "Posted" text.
- **`watch351/discover_sites.py`: site discovery outside Massachusetts.**
  - Homepage checks: robots.txt, crawl-delay, Cloudflare and WAF blocks, redirects, and domains that now belong to someone else.
  - CivicPlus AgendaCenter, with state board aliases.
  - CivicClerk tenants, linked or probed (`<county>cova`, `<county>comi`).
  - eSCRIBE.
  - Closed vendors are recorded as `vendor_blocked` with the platform name: Granicus, iQM2, PrimeGov, BoardDocs, iCompass/CivicWeb, Diligent Community, Destiny. Municode Meetings is recorded as a crawl-delay block, because its 15 s delay is over our cap.
  - Board pages, sub-pages and hub pages are scored by evidence quality.
  - Default rule: on a small township's shared page, documents that name no other body are filed under the governing body. These listings are flagged `board_default` so they can be audited. Any document that names planning or appeals is excluded.
- **No small platform adapters were needed.** The only open platforms we met were CivicPlus, CivicClerk, eSCRIBE (Livingston County: commissioners only), BoardBook and Laserfiche, and plain pages. We met no NovusAgenda or AgendaSuite.

**Michigan county planning commissions** (`watch351/attribution.py`)

- A hit on a county row (`attribute_townships: true`) is filed under the township its agenda item names. The county body is kept as `board`, for example "Huron County Planning Commission".
- The township chosen is the last "X Township" or "Township of X" before the keyword, within the same numbered item.

**Boards and keywords**

- **`watch351/boards.py`.** `classify_board(name, state)` adds MI and VA aliases:
  - township board, board of trustees, city commission and board of supervisors → `select_board`;
  - planning commission → `planning_board`;
  - ZBA and BZA → `zoning_board_of_appeals`.

  Without a state, the classifier behaves as before.
- **`watch351/keywords.py`.** `find_hits(text, state=...)` adds that state's patterns, mapped onto the existing topic keys. No new topic was added.

  | Scope | Patterns | Topic key |
  |---|---|---|
  | Both states | special land use, CUP/SUP or special exception, with energy context and not a data-center-only context | `clean_energy_siting` |
  | Both states | energy facility (not "Consumers Energy facility") | `clean_energy_siting` |
  | Both states | transmission lines and substations being sited, not used as landmarks; kV lines | `clean_energy_siting` |
  | Both states | PILOT and tax abatement, with energy context | `clean_energy_siting` |
  | Both states | wind: WECS, wind turbine / farm / energy facility / ordinance, meteorological tower | `clean_energy_siting` |
  | Both states | ZTA/ZOA | `zoning_amendment` |
  | Both states | rezoning to an industrial or energy district | `zoning_amendment` |
  | Both states | comprehensive or master plan amendment, with siting context | `zoning_amendment` |
  | Michigan | PA 233 / CREO, compatible renewable energy ordinance, MPSC siting, IFT / PA 198 for energy projects | `clean_energy_siting` |
  | Virginia | 15.2-2232 review / substantial accord, siting agreements, revenue share, renewable energy ordinances | `clean_energy_siting` |

  `STATE_FALSE_POSITIVE` holds the guards that came out of the hand checks (see Precision). They apply to MI and VA only. Without a state, matching is unchanged.
- **`watch351/crawl.py`, `daily.py`, `state.py`, `current.py`, `fetch.py`** (all additive):
  - the state is passed to the matcher;
  - `agenda_page` listings run one per config;
  - attribution is applied in `daily`;
  - `town` and `county` are carried on attributed hits;
  - Last-Modified is kept in the fetch cache.

**Gating**

- `data/towns_mi.json` and `data/towns_va.json` carry `"gated": true`. `current.load_towns` skips gated files unless they are named.
- `python3 -m watch351.daily` with no `--states` (what `ops/daily.sh` runs) selects MA 240, NY 33 and RI 39, exactly as before.
- `--states MI,VA` without `--output-dir` exits with code 2 before any request is made.
- `experiments/gate_check.py` checks all of this and prints "GATE OK".

**Test drivers** (`experiments/`)

- `mi_va_test.py`, with subcommands `discover`, `crawl`, `analyze`, `sample` and `rss`.
- `mi_va_analysis.py`.
- `keyword_regression.py`.

**Crawler rules held throughout**

- 351WatchBot user agent;
- robots.txt checked on every host and redirect hop;
- at most 1 request per second per host;
- crawl-delay honoured up to the 10 s cap, and hosts asking for more are skipped;
- no logins, no form POSTs, no bot-challenge solving.

The CivicPlus agenda RSS (`/RSSFeed.aspx?ModID=65&CID=All-0`) was read; robots.txt blocks only `/RSS.aspx`. Nothing was fetched from a host that refused us.

## Coverage

"Readable" means at least one agenda or packet for a tracked board was read in this window. A place with a working listing but no meeting in the window counts as "listing works, no document in window".

### Virginia

| Kind | Attempted | Readable | Blocked (how) | No agendas online | Errors |
|---|---|---|---|---|---|
| County | 32 | **27 (84%)** | 4:<br>• Charlotte: robots.txt (Revize)<br>• Culpeper: Cloudflare challenge<br>• Fauquier: Akamai 403<br>• Fluvanna: crawl-delay 15 s | 1 (Brunswick: only Zoom recordings and one image since spring) | 0 |
| Town | 5 | 3 (Farmville, South Hill, South Boston) | 2:<br>• Culpeper: BoardDocs 403<br>• Warrenton: Municode Meetings crawl-delay 15 s | 0 | 0 |

- **By group:** Southside 19 of 21 readable (90%); Piedmont 8 of 11 (73%).
- **By body,** across the 32 counties:
  - Board of Supervisors: 27 of 32;
  - Planning Commission: 19 of 32;
  - BZA: 3 of 32.

  That is 49 of 96 bodies (51%).

  In 8 counties only the Board of Supervisors is readable: Lunenburg, Nottoway, Prince Edward, Sussex, Southampton, Surry, Appomattox, Amelia. There, the Planning Commission either posts nothing separately or posts it where we could not find it.
- **Platforms of the readable counties:** CivicPlus 10, CivicClerk 9, `agenda_page` 8.

### Michigan

| Kind | Attempted | Readable | Listing works, no document in window | Blocked (how) | No agendas online | Errors |
|---|---|---|---|---|---|---|
| Township | 124 | **37 (29.8%)** | 5 (Bridgewater, Buel, Eaton Rapids, Portland, Sylvan) | 10:<br>• robots.txt: Bedford (Monroe), Newton, Green Oak<br>• Cloudflare: Iosco, Cohoctah<br>• crawl-delay 15–20 s: Cato, Hartland, Hamburg (Municode Meetings)<br>• Diligent: Camden<br>• WAF 403: Putnam | 71:<br>• 21 no website<br>• 29 no recent agendas<br>• 18 no agenda page<br>• 2 domain now someone else's<br>• 1 JavaScript-only | 1 (Shiawassee: robots.txt timed out) |
| City | 5 | 2 (Lansing, Marshall: CivicClerk) | 0 | 3:<br>• robots.txt: Saline, Howell<br>• Monroe: iQM2 answers 429 | 0 | 0 |
| County planning commission | 19 | 4 (Calhoun, Clinton, Huron, Livingston) | 0 | 7:<br>• Diligent: Hillsdale, Saginaw<br>• BoardDocs: Jackson<br>• iCompass/CivicWeb: Tuscola<br>• crawl-delay 20 s: Washtenaw<br>• robots.txt: Ingham<br>• Cloudflare: Montcalm | 8 (Monroe, Lenawee, Shiawassee, Ionia: none found; Branch, Eaton, Gratiot, Sanilac: none recent) | 0 |

- **By selection group:** fight townships 13 of 17 (76%); MTA random sample 17 of 80 (21%); full-county lists 7 of 27 (26%).

  The random sample is the honest estimate for Michigan townships in general: about one in five can be read directly. Small Thumb townships (Tuscola, Huron) post minutes or nothing.
- **By body,** across the 124 townships:
  - governing board: 34;
  - planning commission: 20;
  - ZBA: 10.

  That is 64 of 372 bodies (17%).
- **Through county planning commissions:**
  - **Coverage.** 23 more townships, otherwise unreadable, sit in the four counties whose planning commission we read. That brings "readable or county-reviewed" to 60 of 124 (48.4%).
  - **What the county route sees.** It covers only what the county reviews: township zoning amendments under MCL 125.3307, and special approvals where the county administers zoning (Huron County's Pinesap Solar). It does not see township moratoria or township board items.
  - **Attribution check.** All three township attributions in this run are correct:
    - Rubicon (Pinesap Solar, Huron);
    - Fredonia (Calhoun, zoning text amendment);
    - Marengo (Calhoun, two zoning map amendments).
  - **Limitation.** One snippet can hold several townships' items. Calhoun's 08/31 item list also names Marshall Township's map amendment, but the hit is filed under Fredonia only.
- **Platforms of the readable townships:** `agenda_page` 34 (WordPress, Revize, Wix, plain sites), CivicPlus 3. Two county planning commissions needed curated listings:
  - Livingston (not linked from its homepage);
  - Huron (undated notices, dated from the document itself).

**Gaps seen:**

- Koylton Township overwrites one undated agenda PDF each month.
- Easton Township posts its agenda as an image.
- Ida Township's planning commission posts minutes only.
- 14 packets of 45–266 MB went over the 40 MB download cap, at 9 places:
  - Halifax (2);
  - Pittsfield (3);
  - Ypsilanti (2);
  - Delta (2);
  - Brighton, Superior, Meridian, Howell and Greensville (1 each).

**Virginia ArcGIS land-application layers.** These are noted only; nothing was built, as instructed. Loudoun's layer is current. Similar county layers could flag rezonings and SUP or CUP filings before they reach an agenda. Checking our 32 Southside and Piedmont counties for such layers is the first step.

## Output

| | Michigan | Virginia |
|---|---|---|
| Places crawled | 48 | 30 |
| Documents indexed | 174 (160 read, 14 errors) | 166 (161 read, 5 errors) |
| Read as | PDF text 119, OCR 23, HTML 13, DOCX 5 | PDF text 145, OCR 15, DOCX 1 |
| Hits (final matcher) | **216** in 25 places | **213** in 24 places |
| Hits for meetings still ahead | 52 | 59 |
| By topic (a hit can carry several) | data_center 96, zoning_amendment 77, moratorium 34, battery_storage 28, clean_energy_siting 19, solar 18, wireless_telecom 5 | zoning_amendment 100, solar 62, clean_energy_siting 33, data_center 23, battery_storage 23, wireless_telecom 17, moratorium 1 |
| By board | governing board 94, planning 121, ZBA 1 | governing board 109, planning 104 |

The hits are in `data/test/hits_mi_va.json`, in the `hits_current.json` contract shape.

**Michigan examples:**

- **Huron County Planning Commission, 9/24, filed under Rubicon Township.** Ranger Power's 150 MW Pinesap Solar facility.
  https://www.co.huron.mi.us/_files/ugd/f69a3e_7729406e77c440e2b39f2abe2b5df9e8.pdf
- **Genoa Township Board of Trustees, 9/8.** Resolution extending the moratorium on data center and crypto-mining applications.
  https://www.genoa.org/dbfiles/download/boardmeetings/packet1/2669
- **Gilford Township Planning Commission, 9/14.** Resolution for a temporary moratorium on data centers and battery energy storage facilities.
  https://www.gilfordtownship.com/uploads/2/7/1/0/27106919/gilford_township_public_hearing_and_regular_planning_commission_meeting_9_14_26.pdf
- **Milan Township Board, 9/10.** Agenda item "Battery Storage Moratorium".
  https://milantownship.org/wp-content/uploads/2026/09/09102026-public-agenda.docx
- **City of Marshall Planning Commission, 10/14.** SLU 26-0004 public hearing and site plan for Marshall Solar.
  https://marshallmi.api.civicclerk.com/v1/Meetings/GetMeetingFileStream(fileId=1549,plainText=false)
- **Bedford Charter Township Board, 10/13.** Solar Energy Facility Exemption for Consumers Energy's 18 MW share of a 140 MW project.
  https://www.bedfordchartertwpmi.gov/OCT%20BOARD%20MEETING%20AGENDA.pdf
- **Calhoun County Planning Commission, 8/31, filed under Fredonia Township.** Township zoning text amendment.
  https://www.calhouncountymi.gov/CCPC%208.31.26%20Agenda.pdf

**Virginia examples:**

- **Halifax County Planning Commission, 9/15.** CUP hearing for CEP Solar's facility of up to 69 MW.
  https://www.halifaxcountyva.gov/AgendaCenter/ViewFile/Agenda/_09152026-783
- **King George County Planning Commission, 10/13.** Gibson Solar I / Hanwha special exception for a utility-scale solar facility.
  https://www.king-george.va.us/AgendaCenter/ViewFile/Agenda/_10132026-1552
- **Henry County Board of Supervisors, 9/22.** Siting-agreement hearings for Henry Solar 1 and 2, plus the Data Center District ordinance.
  https://www.henrycountyva.gov/AgendaCenter/ViewFile/Agenda/_09222026-397
- **Mecklenburg County Board of Supervisors, 10/13.** BESS siting agreement with Terraform Power (Mitchell Energy Center), and zoning ordinance amendments.
  https://www.mecklenburgva.com/AgendaCenter/ViewFile/Agenda/_10132026-238
- **Greensville County Board of Supervisors, 9/8.** Public hearing on ZTA-1-2026, Battery Energy Storage Systems.
  https://www.greensvillecountyva.gov/Documents%20Center/Agenda%20&%20Minutes/Board%20of%20Supervisors/2026/Agenda/Board%20of%20Supervisors%20Agenda%20-%2009082026.pdf
- **Caroline County Board of Supervisors, 9/22.** Luck Stone rezoning from RP to M-1.
  https://co.caroline.va.us/AgendaCenter/ViewFile/Agenda/_09222026-568
- **Buckingham County Board of Supervisors, 10/14.** Opposition to the Valley Link 765 kV line, and a technology overlay district allowing data centers by right.
  https://www.buckinghamcountyva.org/OCT%2014%202026%20BOS%20packet%20online%20version.pdf
- **Orange County Planning Commission, 10/15.** Grassland Solar SUP, with a 15.2-2232 substantial-accord determination.
  https://orangecova.api.civicclerk.com/v1/Meetings/GetMeetingFileStream(fileId=1131,plainText=false)

**A topic gap.** Cumberland County's planning commission adopted a 15.2-2232 substantial-accord finding and is reviewing a CUP for Dominion's 3 GW gas-fired Cumberland Energy Center. Milan Township has a "Gas Power Plant Ordinance". Neither has a topic of its own today: the first surfaces only as `clean_energy_siting` (2232) and via boilerplate. A gas or thermal power-plant topic belongs with the next topic batch.

## Precision

**Definition.** A hit is a true positive (TP) when it points to a real agenda item, ordinance text, or staff or public record about its topic in the land-use or siting sense.

- General (non-zoning) ordinance amendments count as false positives (FP), for example tax, traffic or stormwater-fee ordinances.
- Non-land-use moratoria count as FP, for example cemetery plots.
- This is stricter than the Massachusetts design, which counts general bylaw amendments.

We also recorded whether every topic tag on a hit was right (`tags_ok`).

**Method.**

- Each round drew a fresh sample of hits not judged before: round-robin over towns, 45 per state (40 in round 4).
- Each sample was drawn before that round's fixes.
- Every hit was judged from about 1,500 characters of document context, with a one-line reason. All 350 judgments and their reasons are in `data/test/precision_judgments.json`. The worksheets with context are `data/test/precision_worksheet_r1.json` to `_r4.json`.
- Because the sample is round-robin over towns, it weights towns equally. It is not a per-hit random sample.

| Round | Matcher | MI | VA |
|---|---|---|---|
| 1 | first MI/VA patterns | 38/45 = 84.4% | 35/45 = 77.8% |
| 2 | + round-1 fixes and the wind review | 39/45 = 86.7% | 39/45 = 86.7% |
| 3 | + round-2 fixes | 41/45 = 91.1% | 40/45 = 88.9% |
| 4 | + round-3 fixes | 31/40 = 77.5% | 36/40 = 90.0% |
| **Rounds 2–4 pooled (held-out)** | | **111/130 = 85.4%** | **115/130 = 88.5%** |
| All 350 re-scored with the final matcher (in-sample) | | 149/157 = 94.9% (18 FP dropped, 0 TP lost) | 149/159 = 93.7% (15 FP dropped, 1 TP lost) |

The one TP lost is South Boston's rezoning of 0.35 acres. It had matched only through a neighbouring yard-waste "ordinance amendment", and a generic residential rezoning is outside the MI/VA rezoning pattern.

**False-positive patterns, and the fixes made.** All fixes apply to MI and VA only.

| Pattern seen | Examples | Fix |
|---|---|---|
| Non-zoning ordinance amendments | South Hill traffic code, Amelia meals tax, Dinwiddie stormwater fees, South Boston yard waste | A bare "ordinance amendment" needs land-use words in the item itself: 60 characters before, 200 after |
| Use tables, numbered use lists, permit statistics, tables of contents | Bedford, Madison 5-1-x, King George, Clinton "26. Wind energy systems", Bedford TOC | Cell, number and dot-leader density rules |
| Data centers in flyers, webinars, calendars and invoices | Meridian MTA newsletter, Nottoway co-op training, Pittsfield invoice | Event and billing words; ≥6 dollar amounts or ≥2 hourly rates nearby |
| Non-land-use moratoria | Williamstown green burial | Cemetery, burial, hunting and similar words nearby |
| Lease accounting in audits | Genoa cell-tower lease | Lessor or GASB words |
| Glare boilerplate, rooftop solar, backup power | Clinton "no equipment such as solar panels", Cumberland rooftops | Guards |
| Solar-powered equipment | Meridian speed signs, Pittsfield solar tubes | Guards |
| Permit and inspection logs, assessor cards, check registers | Madison "SOLAR FINAL", Genoa property card | Log-word density |
| Special land use inside a data-center ordinance tagged as energy siting | Augusta | Drop when data-center context has no energy words |
| "Electric lines" on a site-plan legend, a distribution easement | Genoa, South Hill | Removed bare "electric lines" |
| Fiber broadband "telecommunications facilities" | Brightspeed | Fiber words without tower words |
| Public-hearing rules boilerplate | Hanover | Guard |
| Snippet-only re-tagging | Williamstown use table | Topics now come from the matches that survive in the full text |

**False positives that remain.** These need judgment rather than a pattern:

- newsletters and legal digests inside packets (MTA "Township Insights", county planning-trend summaries);
- consultant work logs without dollar amounts;
- passing mentions in administrators' reports;
- hypothetical public comments;
- a corporate boilerplate paragraph in a gas-plant application.

A section classifier that separates agenda pages from attachments would remove most of them. Packets concentrate the problem: 6 of the 19 Michigan false positives in rounds 2–4 came from two Meridian Township board packets. They carry an MTA newsletter, a speed-sign study and assessor records.

**Wind check, as requested.**

- **Before the guards, on real documents.** The wind patterns produced 11 hits. None was a wind siting item:
  - Williamstown use-table row;
  - Tyrone ×3: a data-center ordinance that copied a WECS "Facility Boundary" definition;
  - Clinton numbered use list;
  - Brighton ×2: legal digest of a wind-turbine noise case;
  - Ypsilanti height-exemption list;
  - Bedford height exemption;
  - Bedford table of contents;
  - Tyrone: data-center minutes comparing data centers with wind facilities. This hit is correct for `data_center` but wrong for the wind tag.
- **Guards added.** Weather words, "winding" roads (the patterns need "wind energy / turbine / farm..."), height-exemption lists, tables of contents, wind terms inside data-center ordinances, and legal digests.
- **After the guards.** No wind-tagged false positive is left. The two remaining hits that mention wind are correct for other topics:
  - Williamstown's energy-storage ordinance ("accessory to a solar or wind energy project");
  - Tyrone's data-center minutes.
- **Synthetic checks.** A WECS ordinance with a meteorological tower is matched. Storm wind damage and Winding Creek Road are not.
- **Recall is untested.** No real wind siting item fell in this window in the places we can read. Tuscola County's planning commission, where Thumb wind items would appear, is on iCompass/CivicWeb, which blocks us.

## Freshness

- **Documents for meetings still ahead on the crawl day** (2026-10-12):
  - Michigan 33 of 154 dated documents (21.4%);
  - Virginia 31 of 161 (19.3%).
- **Hits for meetings still ahead:** Michigan 52, Virginia 59.

Lead time is days from posting to meeting, assuming a 7 pm meeting. Each source measures something different:

| Source | How it is measured | MI n / median / ≥3 days | VA n / median / ≥3 days |
|---|---|---|---|
| CivicPlus "Posted" stamp | First-posting time printed on the AgendaCenter listing. **The best measure.** | 11 / **3.5 d** / 100% | 39 / **4.2 d** / 87% |
| CivicClerk `publishOn` | The portal API's publish time. **First publish.** | 13 / **2.4 d** / 38% | 52 / **4.5 d** / 83% |
| PDF CreationDate / ModDate | When the file was made or last saved. Approximate: it can predate posting. | 133 / 4.0 d / 71% | 140 / 4.3 d / 78% |
| HTTP Last-Modified | Last change on the server. Re-uploads after the meeting make it negative: 24% in MI. | 94 / 3.5 d / 61% | 49 / 3.5 d / 82% |
| Revize `?t=` upload stamp | Last upload. 44% negative in MI, from re-uploads. | 32 / 1.3 d / 41% | 45 / 4.2 d / 84% |
| CivicPlus RSS `pubDate` | Time of the latest version, not the first posting. 43% negative in VA. Not used as a posting measure. | 8 / 3.2 d | 21 / 0.4 d |
| Our first fetch | Every document was first fetched on the crawl day, so this measures our start date, not posting. | n/a | n/a |

**Reading.**

- On first-publish sources, Virginia counties post a median of about **4–4.5 days** before the meeting. Michigan posts about **2.5–3.5 days** before.
- In Virginia, both first-publish sources agree: 83–87% of agendas are up at least 3 days ahead.
- In Michigan the two sources disagree, and their samples are small: 100% of 11 CivicPlus postings were 3 or more days ahead, against 38% of 13 CivicClerk postings. File dates put the share at 60–70%.
- Small townships on plain sites often post one or two days before the meeting, judging by their upload stamps.
- WordPress upload months give only a bound weaker than a week, so they are not shown.

## Reliability

Runs used 16 workers, with the per-host limit of 1 request per second. Every run report is in `data/test/runs/` and every request log in `data/test/requests_*.tsv`.

| Run | What it was | Runtime | Requests | Bytes | Places ok | Documents |
|---|---|---|---|---|---|---|
| run1 | First crawl. Listing pages were warm from same-day discovery; documents were cold. | 194 s | 392 (50 listing, 342 document) | 1.03 GB | 77/77 | 338 listed, 319 read, 19 errors |
| rebuild | Index wiped and re-crawled with the fixed code: Howell added, date fixes | 103 s | 26 document | 53 MB | 78/78 | 319 read |
| run2 | Immediately after | 72 s | 3 | 0.2 MB | 78/78 | 333 already indexed, **0 new** |
| cold | Empty fetch cache, index kept: a fresh container the next day | 71 s | 237 (81 robots.txt, 148 listing, 8 document) | 33 MB | 78/78 | 2 new, 333 skipped as indexed |
| final | Matcher change: re-match from cache | 111 s | 0 | 0 | 78/78 | 319 re-matched |

- **Network errors:** 0 in every run.
- **The second run is incremental.** Indexed documents are never fetched again. A day's cost is the listing pages plus new documents: about 240 requests and 33 MB for 78 places.
- **Document errors (19), by cause:**
  - 14 packets over the 40 MB cap;
  - 3 Portland Township CivicClerk PDFs that `pdftotext` cannot read;
  - 2 Nottoway DOCX files, whose redirect to `cms8.revize.com` is disallowed by robots.txt.

  These are recorded in `town_health` and retried only when their listing changes.
- **Discovery:**
  - Michigan: 148 places in 430 s, about 2,500 page reads;
  - Virginia: 37 places in 160 s, about 770 page reads.

  Both final passes were mostly served from the same day's cache.
- **One bug, found and fixed.** A compact date glued to a month name ("botagendamarch122026") was read as Dec 20. Marion's March agenda therefore entered run 1's window. The rebuild dropped it.

## Massachusetts unchanged

`experiments/keyword_regression.py` matched every MA, NY and RI document in the production index whose body is in the fetch cache: 3,105 documents (PDF 2,211, OCR 732, HTML 146, DOCX 16). It read the cache offline and re-ran no OCR.

- It compared `keywords.py` at af1e10d with the matcher as it stands after the fix round, called as production calls it.
- Hits: MA 1,063 → 1,063, NY 28 → 28, RI 109 → 109. **0 documents differ.** The result is in `data/test/keyword_regression.json`.
- For information only: if the MI patterns and guards were ever switched on for Massachusetts, MA would drop to 880 hits. The guards are stricter than MA's rule that general bylaw amendments count.

`git status` shows no change to `data/hits_current.json`, `data/state/`, `site/` or `ops/`.

## What would raise coverage most (first test)

Items 2, 6 and 7 below, and the per-township split in item 3, were done in the fix round. The current list is under "What would fix what is left" at the top.


1. **Vendor permission, or vendor feeds, for closed platforms.** Diligent Community covers Hillsdale County, Saginaw County and Camden Township. BoardDocs covers Jackson County and the Town of Culpeper. iCompass/CivicWeb covers Tuscola County. iQM2 covers the City of Monroe.
   - That is 7 places, 4 of them county planning commissions.
   - Through the county route, each county planning commission covers every township zoning amendment in its county. Tuscola alone covers 18 target townships, 16 of which are not readable today, plus the Thumb's wind and PA 233 items.
2. **A crawl-delay cap of 20 s for listing-only daily runs.** This adds 6 places: Washtenaw County (20 s), Cato (20 s), Hartland, Fluvanna, and Hamburg and Warrenton on Municode Meetings (15 s each).
   - A daily pass makes 3–10 requests per host, so 20 s costs a few minutes per host, in parallel with the rest of the run.
   - Washtenaw's planning commission reviews zoning for 10 target townships, including the Saline, Augusta and Pittsfield data-center fights. 7 of the 10 are already readable directly.
3. **The county planning commission route in Michigan.** This takes direct-plus-indirect township coverage from 30% to 48% today. It goes further when:
   - counties that do not post agendas are asked to (Monroe, Lenawee, Branch, Eaton, Gratiot and Sanilac review the most townships in the Monroe and Thumb clusters);
   - one hit is split per township item, so that Calhoun's list files each township.
4. **Statutory hearing notices for townships with no website (21) or minutes only (29).** Michigan requires a newspaper notice before a zoning hearing (MCL 125.3103), so a public-notice source would reach the 57% of townships with no online agendas. Its terms of use need checking first. More crawling cannot reach these townships.
5. **Read large packets in part instead of skipping them.** 14 packets over 40 MB were skipped. Reading the first pages, or the separate agenda file, would help.
6. **Virginia Planning Commissions in the 8 counties where only the Board of Supervisors is readable.** Check CivicClerk categories and Document Center folders. This would take Virginia bodies from 51% toward 70%.
7. **Precision: separate attachments from agenda items** before matching, rather than adding regexes. This addresses the remaining newsletter, invoice and passing-mention false positives. Also add a gas or thermal power-plant topic: Cumberland Energy Center, Milan's ordinance.
8. **Virginia ArcGIS land-application layers** (noted only): a pre-agenda signal where a county keeps one current, as Loudoun does.

## Files

**Code** (`projects/351watch/crawler/`)

- New: `watch351/adapters/agenda_page.py`, `watch351/discover_sites.py`, `watch351/attribution.py`.
- Changed (additive): `watch351/boards.py`, `watch351/keywords.py`, `watch351/crawl.py`, `watch351/daily.py`, `watch351/state.py`, `watch351/current.py`, `watch351/fetch.py`, `watch351/adapters/__init__.py`.
- Experiments: `experiments/mi_va_test.py`, `experiments/mi_va_analysis.py`, `experiments/keyword_regression.py`, `experiments/gate_check.py`.

**Configs** (`projects/351watch/data/`)

- `towns_mi.json` and `towns_va.json` (gated).
- `test/targets_mi.json` and `test/targets_va.json`.

**Test output** (`projects/351watch/data/test/`)

- `hits_mi_va.json`
- `state/` (index, health, run reports)
- `first_seen.json`
- `runs/`
- `requests_*.tsv`
- `analysis_mi_va.json` (coverage per place, freshness, output, reliability; now for the re-test, `--base-run retest1`)
- `runs/run_run1.json` … `run_final.json` are the first test's runs; `run_retest1.json`, `run_retest2.json` and `run_retest_cold.json` are the re-test's.
- `round1_4_documents.json` lists the documents behind the hand-checked rounds 1–4, which round 5 excluded.
- `extended/` holds the extended crawl (meetings from 2026-06-29) used only for the fresh precision sample: `hits_mi_va.json`, `state/`, `runs/run_extended.json`, `requests_extended.tsv` and `precision_worksheet_r5.json`.
- Full-text rows from test crawls (`data/test/**/search/`, `archive/`) stay local and are git-ignored.
- `precision_judgments.json` (rounds 1–5, with reasons) and `precision_worksheet_r1.json` to `_r4.json`
- `keyword_regression.json`
- `posted_stamps_*.json`
- `rss_pubdates.json`

**Re-run:**

```bash
cd projects/351watch/crawler
python3 experiments/mi_va_test.py crawl
python3 experiments/mi_va_test.py analyze
```

Production is untouched by either command.
