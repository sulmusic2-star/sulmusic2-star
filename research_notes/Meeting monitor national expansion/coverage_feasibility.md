# Coverage feasibility: how cheaply and completely an agenda reader can cover siting bodies in candidate US states

*Run 2026-10-11/12 by a research agent for 351 Watch. Companion CSVs in this folder:*
- *`coverage_county_census.csv`: all 1,982 county-level governments in 26 states, each probed (platform, block, agenda evidence).*
- *`coverage_sample_jurisdictions.csv`: 161 municipal/township sample (about 120 siting-relevant targets plus random townships).*
- *`coverage_mi_township_websites.csv`: 272 Michigan townships, with whether the Michigan Townships Association directory lists a website.*
- *`coverage_state_feeds.csv`: 44 state and national shortcut feeds, each tested once (reachable, blocked, machine-readable, current).*

**Labels.**
- **verified**: checked directly this session with a plain HTTP GET from the crawler's own `PoliteFetcher`:
  - 351WatchBot UA;
  - robots.txt checked on every hop;
  - at least 1.05 s between requests to a host;
  - crawl-delay cap of 10 s;
  - no logins, no POSTs, and no challenge ever solved.
- **secondary**: from a web-search summary or a third-party page that I did not test myself.
- **estimate**: my inference.

"Blocked" means a Cloudflare, Akamai, Imperva or CloudFront challenge or 403, a 429 on the first request, or a robots.txt disallow. A crawl delay over 10 s is counted separately as "slow-crawl only".

## Q1. Per-state table: who decides siting, how much is online, platforms, blocking, adapter readiness, shortcut feeds

### Takeaway
Our four stock adapters can read today:
- about 15% of reachable county governments directly (CivicPlus AgendaCenter, CivicClerk, Legistar, eSCRIBE);
- another 16% with hand-curated `generic` listings, for about 31% in all (verified, 1,737 reachable county sites).

Another 17% are bot-blocked, and 4% sit on agenda vendors that block polite bots outright (Granicus ViewPublisher, BoardDocs, PrimeGov, Diligent/iCompass, iQM2, Destiny). No candidate state reaches 60% of its siting bodies on today's adapters alone.

Three states, plus Vermont and Connecticut through their state siting dockets, can be covered cheaply through one statewide source:
- **Nevada** (all public bodies must post on notice.nv.gov);
- **Utah** (the Utah Public Notice Website);
- **Rhode Island** (already built).

### Method (summary)
1. **County census.** County websites came from Wikidata P856, via SPARQL by state. Each of the 1,982 counties in 26 states was probed: home page, up to 6 same-site agenda/meeting/governing-body pages, then a second pass of up to 8 more agenda links (verified).
   - **Classes:**
     - stock adapter;
     - generic (document links and an agenda date of Aug 2026 or later found);
     - open vendor needing a new adapter;
     - closed vendor;
     - agenda links with no recent date;
     - no agenda found;
     - blocked;
     - unreachable (a dead Wikidata URL: 245 counties, excluded from denominators).
   - **"No agenda found" is a lower-bound artifact, not proof of absence.** I re-probed 84 such counties at depth 2 with looser link rules, and 11 (13%) then showed agenda evidence.
2. **Vendor portals.** The examples the census found were each fetched once to test accessibility (verified, below and in Q3).
3. **Sample.** 161 municipalities and townships: siting-relevant targets in each state chosen from background knowledge of 2025–26 data-center, BESS and solar fights (selection not verified), plus a random draw of 12 townships per township state from Wikidata. For 22 random townships with no site found, websites were checked by web search.
4. **Michigan.** The MTA "Find a Township" directory (robots allows us) was read for 272 townships: the first 60 in Wikidata order plus a random 212.
5. **Shortcut feeds.** About 45 state and national feed URLs were tested once each.

### Cited Findings
**County census, all states:** 1,982 county governments, 1,737 reachable. Readable by stock adapters: 268 (15%). Readable by `generic` hand listings: 270 (16%). Blocked: 293 (17%): 95 Cloudflare challenges, 91 other 403s, 63 robots disallows, 42 Akamai 403s. Slow-crawl only: 50 (3%). Closed vendors: 72 (4%). Open vendors needing new adapters: 17 (1%). Stale listings: 139 (8%). No agenda found: 628 (36%). — [coverage_county_census.csv](coverage_county_census.csv) (verified)

**Census counts** (county / municipal / township) are from the 2022 Census of Governments, via [state_agenda_laws.md](../Meeting%20monitor%20deep%20dive/state_agenda_laws.md). Percentages in the county columns are shares of *reachable* county sites (verified probe). "Readable now" = stock adapter + `generic`. The cost column is an estimate.

| State | Who decides siting (bodies) | County agenda evidence online (lower bound) | Blocked | Readable now (+ open vendors / slow crawl) | Dominant platforms seen | New adapters / permissions needed | State-level shortcut feeds tested | Municipal / township notes | Cost to 60%+ |
|---|---|---|---|---|---|---|---|---|---|
| **PA** | 2,559 municipalities (1,546 townships, 1,013 boroughs and cities) under the MPC; counties rarely | 44% | 26% | 44% (46%) | Hand-built sites (18 of 57); CivicPlus 6 | Generic WordPress/FileBird/Revize listings; no vendor cluster | PA Bulletin and eFACTS: **robots disallow**. data.pa.gov: no permit-application dataset found. publicnoticepa.com reachable (ASP.NET search) | 12 sampled: 5 readable (Limerick CivicPlus; Falls, East Whiteland, Archbald `generic`), 2 stale, 5 none found. Random townships: 4 of 8 have a website | **High** |
| **OH** | 1,308 townships (zoning), 926 municipalities, 88 counties (SB 52 wind/solar veto); OPSB ≥50 MW | 29% | 8% | 25% (30%) | CivicPlus 10 | Generic | OPSB DIS docketing (dis.puc.state.oh.us) reachable. epa.ohio.gov answered 404 to our UA. publicnoticesohio.com reachable | 10 sampled: 5 readable (Liberty, Etna on CivicPlus; New Albany, Miami, Washington `generic`), 1 crawl-delay. Random townships: 2 of 8 have a website | **High** |
| **MI** | 1,240 townships (MZEA zoning), 533 municipalities, 83 counties; MPSC PA 233 option | 45% | 23% | 32% (36%) | CivicClerk 6; Diligent 2; CivicPlus 2 | Generic; Diligent (closed) | MiEnviro (EGLE permits and notices): **robots `Disallow: /`**. mpsc.michigan.gov: robots disallow. mipublicnotices.com reachable | 13 sampled: 4 readable (Frenchtown, Pittsfield CivicPlus; Ypsilanti `generic`), Gaines Granicus (closed), Lowell Diligent (closed), Lyon robots, 6 none found. 78% of townships list a website (MTA) | **High** |
| **IN** | 92 counties (plan commissions, BZAs, councils for abatements) and 567 municipalities. Townships do not zone (background, not verified) | 34% | 12% | 29% (**56%** if a 30–300 s crawl delay is accepted) | CivicPlus 7; CivicClerk 3; SuiteOne 2 | Accept long crawl delays: **19 counties share a robots.txt with Crawl-delay 30 s or 300 s**, e.g. wellscounty.org 30 s, co.hendricks.in.us 300 s | IURC portal reachable. indianapublicnotices.com: **Cloudflare challenge**. MISO queue API: Cloudflare | 8 sampled: 3 readable (Hobart, Valparaiso CivicPlus; Jeffersonville `generic`); Fort Wayne Cloudflare; Lebanon 403; Kokomo robots | **Medium** |
| **IL** | 102 counties (under the statewide wind/solar standards) and 1,295 municipalities; townships mostly advisory | 48% | 14% | 41% (42%) | CivicPlus 7; Legistar 2; iQM2 2 | Generic | ICC e-docket reachable. publicnoticeillinois.com reachable | 9 sampled: 6 readable (Yorkville, DeKalb, Aurora, Joliet and others: Legistar, CivicPlus, CivicClerk) | **Medium** |
| **WI** | PSC ≥100 MW. Data centers and smaller projects: 605 municipalities, 1,245 towns, 72 counties | 42% | **35%** | 33% (35%) | CivicPlus 6; CivicClerk 4. Towns: **HeyGov** (3 of 8 random towns) | HeyGov: API robots disallow. Granicus (closed) | PSC ERF: **Cloudflare challenge**. wisconsinpublicnotice.org reachable | 18 sampled, 2 readable. Mount Pleasant and DeForest on Granicus (closed); Port Washington, Kenosha, Janesville blocked | **High** |
| **MN** | PUC for solar ≥50 MW, wind ≥5 MW, storage ≥10 MW. Data centers: 854 cities, 1,779 townships, 87 counties as RGUs | 54% | 28% | 41% (44%) | CivicPlus 14; CivicClerk 10; PrimeGov 2 | Few | **EQB Monitor** (weekly environmental review notices statewide, HTML bulletins) **verified current** (Oct 6, 2026 issue). PUC eDockets: 403. mnpublicnotice.com reachable | 8 sampled: 3 readable. Random townships: 2 of 6 checked have a website | **Medium** (Low for data centers via the EQB Monitor) |
| **IA** | 99 county boards of supervisors and 940 cities | 45% | 22% | 21% | CivicPlus 6 | Generic | IUC EFS reachable. iowapublicnotices.com reachable | not sampled | **High** |
| **VA** | 95 counties, 38 cities, towns. SCC for utility-owned plants | 58% | 21% | **45%** (48%) | **CivicPlus 18; CivicClerk 11**; BoardDocs 3; Diligent 2 | BoardDocs and Granicus permissions | DEQ public notices: **Akamai 403**. SCC docket search: **robots disallow**. publicnoticevirginia.com reachable | 5 cities and towns: Manassas and Chesapeake on Granicus, Culpeper on BoardDocs (all closed); Warrenton on Municode Meetings (open); Leesburg Akamai | **Medium** (best county state) |
| **NC** | 100 counties and 552 municipalities | 51% | 21% | 35% (37%) | CivicPlus 12; CivicClerk 10; Granicus 3; Legistar 3 | Granicus permission | NCUC: **Cloudflare challenge**. ncnotices.com reachable | 4 sampled | **Medium** |
| **GA** | 152 consolidated and other counties, 537 cities. DRI regional review | 43% | 12% | 28% (32%) | CivicPlus 13; CivicClerk 10; Novus, Municode, Simbli | Novus (open); Simbli (Imperva) | DCA DRI system (apps.dca.ga.gov): **robots `Disallow: /`**. ARC DRI page reachable (WordPress). georgiapublicnotice.com reachable | 6 data-center cities: 1 readable (South Fulton CivicClerk); Fayetteville and Palmetto Cloudflare; Douglasville Diligent | **Medium-High** |
| **SC** | 46 counties and 271 municipalities | 40% | 33% | 26% | CivicPlus 2; Granicus 2 | — | PSC DMS: robots disallow. scpublicnotices.com reachable | 3 sampled | **High** |
| **TX** | 1,225 cities (zoning). 254 counties (abatements, road agreements; no zoning). PUCT/ERCOT | 48% | 7% | 30% (33%) | 55 of 252 counties on hand-built pages (many on a shared Texas county-hosting template). CivicClerk 10; CivicPlus 10; Granicus 6; Destiny 5 | Generic adapter for the shared template; Destiny and Granicus permissions | ERCOT GIS report: `/misdownload` and `/misapp` **robots disallow**. Comptroller JETI: robots disallow. TCEQ reachable. SPP queue CSV covers the Panhandle | 10 data-center cities: **6 readable** (Round Rock, San Marcos, Fort Worth on Legistar; Abilene, Taylor, Red Oak on CivicClerk). Temple and Amarillo on Granicus (closed); Hutto Cloudflare | **Medium** (cities Low-Medium) |
| **AZ** | 15 counties and 91 municipalities. ACC line siting | 33% | **47%** | 7% | **Destiny (4 of 15 counties)** | Destiny permission (robots disallow) | ACC eDocket reachable. arizonapublicnotices.com reachable | 10 cities: 1 readable | **High** (few bodies, so permission deals would fix it) |
| **NV** | 16 counties and 19 cities. PUCN UEPA | 87% | 7% | 53% | Granicus 5; CivicPlus 3; Legistar 2 | — | **notice.nv.gov: all public bodies must post agendas here by 9 a.m. on the 3rd working day before the meeting (NRS 241.020(4)(b))**. Home page lists upcoming meetings statewide with "Date Posted"; robots 404. Most entries link out to the body's own agenda page | 6 cities | **Low** |
| **NM** | 33 counties and 105 municipalities | 54% | 21% | 46% (50%) | CivicPlus 3; CivicClerk 2 | — | PRC eDocket: robots disallow. nmpublicnotices.com: robots disallow | 7 cities: 4 readable | **Medium** |
| **CO** | 64 counties (1041 powers) and 272 municipalities | 57% | 25% | 43% (51%) | CivicPlus 10; CivicClerk 6; eSCRIBE 2; Legistar 2 | — | 10 small counties hosted on `*.colorado.gov` return a **CloudFront 403**; PUC e-filings likewise. SPP queue CSV includes CO (Weld County rows) | 8 cities: 4 readable | **Medium** |
| **NJ** | 564 municipalities (MLUL) | 26% (21 counties, weak signal) | 37% | 26% | — | Generic; eCode360 `/documents` (robots) | NJDEP DataMiner: **robots disallow**. NJ DOS statewide legal-notice directory reachable (a list of each entity's notice page) | 10 sampled: 1 readable; most none found or eCode360 code links | **High** |
| **MD** | PSC CPCN for most solar. 23 counties and Baltimore City, 157 municipalities | 67% | 19% | 43% | CivicClerk 3; Granicus 3; CivicPlus 2 | Granicus | PSC DMS reachable. mddcpublicnotices.com reachable. Montgomery County sediment-control permits on Socrata | 4 sampled | **Medium-Low** (few bodies) |
| **DE** | 3 counties and 57 municipalities | — | 1 of 3 | 1 of 3 | — | — | publicmeetings.delaware.gov: Angular app whose `/assets/` config is **robots-disallowed**. **DNREC stormwater NOI dataset (Socrata API) works, but the newest record is 2024-04-17 (stale)** | 5 sampled: 0 readable | **Medium** |
| **CT** | Siting Council (>1 MW); 169 towns | n/a | NE probe: heavy | NE probe 2 of 6 | — | — | CT Siting Council "Pending Matters" page reachable (HTML) | see NE probe | **Low** (state docket) / High (towns) |
| **ME** | 461 towns, 23 cities (home rule); DEP Site Law | n/a | low | NE probe **5 of 6 on CivicPlus** | CivicPlus | — | mainepublicnotices.com: NXDOMAIN | — | **Low** |
| **NH** | 221 towns, 13 cities; SEC ≥30 MW | n/a | NE probe: Cloudflare 3 of 6 | NE probe 3 of 6 | CivicPlus | — | NHDES OneStop (wetlands, AoT): **Akamai 403**. nhpublicnotices.com: NXDOMAIN | — | **Medium** |
| **VT** | PUC §248; Act 250; 237 towns advisory | n/a | — | NE probe 3 of 6 | — | — | **Act 250 "Agenda"**: an aggregate daily list of every noticed or decided Act 250 project statewide, plain HTML, **verified current**. ePUC reachable. vtpublicnotices.com: robots disallow | — | **Low** |
| **UT** (added) | 29 counties and 254 municipalities | 58% | 8% | 42% | CivicPlus 3; CivicClerk 3 | — | **Utah Public Notice Website**: all 29 counties and 270 municipal entities listed. Plain GET JSON-free HTML lists, agenda files hosted at `/pmn/files/<id>.pdf`; robots allows | not sampled | **Low** |
| KY (added) | 120 counties, 417 cities. Siting Board for ≥10 MW merchant | 17% | 20% | 16% | CivicPlus 5 | Generic | PSC reachable. kypublicnotice.com: robots disallow | — | **High** |
| TN (added) | 95 counties, 345 cities | 43% | 14% | 22% | CivicPlus 3 | Generic | tnpublicnotice.com reachable | — | **High** |
| LA (added) | 64 parishes, 304 municipalities | 47% | 16% | 39% | CivicPlus 4; CivicClerk 3 | — | lapublicnotice.com: robots disallow | — | **Medium-High** |
| MO, OK (added) | counties and cities | 20% / 64% | 7% / 8% | 17% / 24% | CivicPlus | Generic | mopublicnotices.com and oklahomanotices.com reachable | — | **High** |

**Northeast figures** are from the earlier probe: CT, NJ, NY, PA, VT and ME each had 6 towns tried, and NH had 6 with 3 behind Cloudflare. — [northeast_feasibility.md](../Meeting%20monitor%20deep%20dive/northeast_feasibility.md) (our own prior verified run)

**Michigan townships:**
- 165 of 211 randomly drawn townships (78%) list a website in the Michigan Townships Association directory. By population:
  - under 1,000: 57%;
  - 1,000–2,500: 80%;
  - 2,500–10,000: 94%;
  - 10,000 and over: 100%.

  — [coverage_mi_township_websites.csv](coverage_mi_township_websites.csv); example record [MTA Rogers Township](https://michigantownships.org/find-a-township/?fips=69240), which shows "No Website Listed" (verified).
- This matches the Michigan Public Policy Survey (spring 2021): 76% of townships reported their own website, and 16% had neither a website nor a Facebook page. In fall 2012, 37% had no website. — [CLOSUP MPPS q27a](https://closup.umich.edu/data-table/michigan-public-policy-survey-mpps/spring-2021-data/q27a), [q27d](https://closup.umich.edu/data-table/michigan-public-policy-survey-mpps/spring-2021-data/q27d), [fall 2012 q26](https://closup.umich.edu/data-table/michigan-public-policy-survey-mpps/fall-2012-data/q26) (secondary: CLOSUP served a Cloudflare challenge to our bot, so the figures come from a search summary).

**Indiana crawl delays:** 19 county sites declare crawl delays of 30 s or more, e.g. `wellscounty.org` 30 s and `co.hendricks.in.us` 300 s. — [wellscounty robots](https://www.wellscounty.org/robots.txt), [Hendricks robots](https://www.co.hendricks.in.us/robots.txt) (verified)

**Colorado:** state-hosted county sites return a CloudFront "Request blocked" 403 even for robots.txt, e.g. [saguachecounty.colorado.gov](https://saguachecounty.colorado.gov/). — (verified)

### Inferences
- **The binding constraint is not platform count. It is two things:**
  1. Hand-built county and town sites: 16% `generic` plus most of the 36% "none found".
  2. Bot walls. Site walls block 17% of counties, and the major closed vendors block another 4%.
- **The NE probe's NY/NJ/PA problem generalizes.** About 1 county in 5 is behind a wall nationally, and a third or more in WI, SC, AZ and NJ.
- **County-zoning states in the South and Mid-Atlantic are easiest.** VA, NC, MN, CO and NM have the most CivicPlus and CivicClerk: 35–46% readable now.
- **Township states are hardest.** PA, OH, MI and WI need thousands of small-site listings.

### Gaps
- Per-state county figures exclude counties whose Wikidata URL was dead (245; worst in KY, IA, IL, IN). The true online share there is unknown.
- "Posts before meetings" was approximated by seeing a document link dated Aug 2026 or later on an agenda page. Posting lead time was not measured outside the NE, NY and RI work.
- The samples are small (4–18 per state) and selection-biased toward data-center fights.
- Facebook-only posting could not be measured: Facebook blocks bots, and I did not try.

## Q2. In township states, do townships post agendas online at all, or only on paper or Facebook?

### Takeaway
It depends sharply on size.
- **Michigan:** about 78% of townships have a website (verified census sample), but the smallest townships (under 1,000 people) are about 57%.
- **Pennsylvania and Wisconsin:** about half to most townships have a website.
- **Ohio and Minnesota:** most small rural townships appear to have **no website at all**. Notices go to the county newspaper or are posted at the hall.

Having a website is not the same as posting agendas. Of 17 random township sites we probed, only 4 showed a current agenda listing: Cummings PA, Denton MI, Green Lake WI, and Pepin WI (stale). Three Wisconsin towns use HeyGov, whose API forbids bots.

**Estimate of township agenda-online share:** MI about 35–50%, PA about 30–45%, WI about 30–40%, OH about 15–25%, MN about 10–20%. Siting-fight townships, which are larger and suburban, sit well above these averages.

### Cited Findings
**Random draw, verified** (12 townships per state drawn from Wikidata; the first 8 calibrated by pattern-matched domain plus web search):
- **PA:** 4 of 8 have a website: Cummings, Gulich, Pocono, and Taylor (Blair, which posts agendas through June 2026, [agendas](https://taylortownshipblaircounty.gov/agendas)).
  - No website found for Wells (Fulton), Montour (Columbia), Conneaut (Crawford) or Union (Lebanon), e.g. [Wells search result](https://www.openrecords.pa.gov/RTKL/AOROInfo.cfm?id=1356).
  - Upper Makefield (Bucks, outside the first 8) has a site with agendas: [uppermakefield.org](https://uppermakefield.org/government/).
  - (verified + secondary)
- **OH:** 2 of 8 have a website: Rootstown and Hanover (Butler, [hanovertownshipohio.org](https://hanovertownshipohio.org)). Lyme, outside the first 8, also has a site.
  - Grand Prairie (Marion), Starr (Hocking), Warren (Tuscarawas), Perry (Putnam), Roundhead (Hardin) and Oliver (Adams) turned up only Wikipedia, county or state-auditor pages, e.g. [Starr Township audit](https://ohioauditor.gov/AuditSearch/Reports/2017/Starr_Township_16_15-Hocking.pdf).
  - (verified + secondary)
- **MI:** 5 of 8 have a website: Norwood, James, Caseville, Belknap and [Burtchville](https://burtchville.org/wp-content/uploads/2026/03/Minutes-of-February-16-2026.pdf), the last posting minutes only. Lebanon (Clinton), Zilwaukee and Rogers have none; [MTA lists none for Rogers](https://michigantownships.org/find-a-township/?fips=69240). (verified + secondary)
- **WI:** 7 of 8 have a website, including Pierce ([per Wikipedia](https://en.wikipedia.org/wiki/Pierce,_Wisconsin)); Lena (Oconto) has only a county page ([Oconto County Town of Lena](https://www.ocontocountywi.gov/489/Town-of-Lena)). 3 of the 7 sites run HeyGov (`edge.heygov.com` / `files.heygov.com`). (verified)
- **MN:** 2 of 6 checked have a website: Nininger ([Wikipedia lists niningertownship.com](https://en.wikipedia.org/wiki/Nininger_Township,_Dakota_County,_Minnesota)) and Sargeant.
  - Pilot Mound publishes notices in the county newspaper ([Fillmore County Journal](https://fillmorecountyjournal.com/road-closure-notice-pilot-mound-township/)).
  - Elmwood, Park and Westside: no website found.
  - (secondary)

**Statewide context:**
- MI township website prevalence by size (MTA directory) is in Q1 (verified).
- **PA law:** Act 65 of 2021 requires an agenda posted online 24 hours ahead *if the agency has a website*. Townships without one are exempt. — [65 Pa.C.S. ch. 7](https://www.palegis.us/statutes/consolidated/view-statute?txtType=HTM&ttl=65&div=0&chapter=7) (from our prior notes)
- **Ohio and Michigan** open-meetings laws require no agenda at all. — [state_agenda_laws.md](../Meeting%20monitor%20deep%20dive/state_agenda_laws.md)
- **Ohio township zoning** is set by ORC Chapter 519. Many rural townships have none, and county zoning or none applies. — [ORC ch. 519 (Justia)](https://law.justia.com/codes/ohio/2018/title-5/chapter-519/) (secondary)

**Siting-fight townships** sit well above these averages (verified):
- **PA:** Limerick (CivicPlus), Falls, East Whiteland and Archbald (WordPress or hand-built, readable via `generic`) all had agendas dated Aug–Oct 2026. Hazle and Derry (Montour) had agenda links with no recent date.
- **OH:** Liberty and Etna (CivicPlus); New Albany, Miami (Greene) and Washington (Franklin) readable via `generic`.
- **MI:** Frenchtown and Pittsfield (CivicPlus) and Ypsilanti (`generic`). Gaines (Granicus) and Lowell (Diligent) are on closed vendors. Lyon Township's robots disallows us.

### Inferences
- **Facebook-only is a real but secondary channel.** MPPS says about 8% of MI townships have social media but no website (76% website; 16% neither).
- **The main gap in small townships is that agendas are not posted anywhere online.** The legal floor in OH, MI and MN requires none. Minutes and newspaper legal notices appear later.
- **For siting, the decisive event in these places** is usually a planning-commission hearing on a zoning amendment or moratorium. That hearing triggers a **newspaper legal notice** even when no online agenda exists. So the statewide press-association notice sites are the realistic catch-all for small townships, though not a cheap one (Q4).

### Gaps
- No PA, OH, WI or MN equivalent of the MTA directory was found or tested, so those shares rest on 6–8-township samples.
- Several township sites were probed but showed no agenda listing within 2 link levels. Some may post agendas under "Notices" or inside news posts.

## Q3. Which 3–5 platforms would unlock the most siting-relevant jurisdictions if adapters were built?

### Takeaway
The biggest unlocks are not new SaaS vendors:
1. A robust **generic document-listing adapter**: auto-discovered WordPress, Revize, CivicPlus Document/Archive Center, and the shared Texas county template. It covers about 16% of counties now, plus most of the 8% "stale" and part of the 36% "none found".
2. **Statewide portals:** Utah PMN and Nevada notice.nv.gov.
3. **Municode Meetings** (CivicPlus).
4. Small open vendors: **NovusAgenda, OnBase Agenda Online, AgendaSuite, SuiteOne, BoardBook**.

The big vendors the brief named, **Granicus ViewPublisher, BoardDocs, PrimeGov, Diligent/iCompass, iQM2 and Destiny**, all refuse our bot by robots.txt, WAF or 429. Writing adapters for them is pointless without vendor or customer permission.

### Cited Findings
**Platform counts among 1,737 reachable county sites:**
- Supported now: CivicPlus AgendaCenter 160, CivicClerk 88, Legistar 18, eSCRIBE 2.
- Closed: Granicus 30, iQM2 11, Diligent/iCompass 11, Destiny 10, BoardDocs 5, PrimeGov 3, Simbli 1.
- Open (new adapter needed): Municode Meetings 4, OnBase 3, AgendaSuite 3, SuiteOne 3, Novus 2, BoardBook 2.
- Hand-built `generic` pages: 270.

— [coverage_county_census.csv](coverage_county_census.csv) (verified)

**Vendor accessibility to 351WatchBot** (verified, 2026-10-11):
- **Granicus ViewPublisher** (`*.granicus.com`): robots allows Googlebot, Slurp and msnbot but ends with `User-agent: * Disallow: /`. — [dekalbcountyga.granicus.com/robots.txt](https://dekalbcountyga.granicus.com/robots.txt), [montrosecounty.granicus.com/robots.txt](https://montrosecounty.granicus.com/robots.txt)
- **PrimeGov:** `User-agent: * Disallow: /`. — [olmstedcounty.primegov.com/robots.txt](https://olmstedcounty.primegov.com/robots.txt), [dodgecountymn.primegov.com/robots.txt](https://dodgecountymn.primegov.com/robots.txt)
- **Diligent Community and iCompass (civicweb):** `User-agent: * Disallow: /`. — [kcmn.civicweb.net/robots.txt](https://kcmn.civicweb.net/robots.txt), [hillsdale.community.diligentoneplatform.com/robots.txt](https://hillsdale.community.diligentoneplatform.com/robots.txt)
- **BoardDocs:** CloudFront "Request blocked" 403, even on robots.txt. — [go.boarddocs.com/robots.txt](https://go.boarddocs.com/robots.txt), [boarddocs.com/robots.txt](https://www.boarddocs.com/robots.txt)
- **iQM2:** HTTP 429 on the very first request, robots.txt included, and still 429 on a retry after 20 s. — [chathamcountyga.iqm2.com/robots.txt](https://chathamcountyga.iqm2.com/robots.txt), [grundycountyil.iqm2.com/robots.txt](https://grundycountyil.iqm2.com/robots.txt)
- **Destiny Agenda:** `Disallow: /`. — [public.destinyhosted.com/robots.txt](https://public.destinyhosted.com/robots.txt)
- **Simbli:** Imperva challenge marker. — [simbli.eboardsolutions.com](https://simbli.eboardsolutions.com/SB_Meetings/SB_MeetingListing.aspx?S=36031032)
- **Swagit video:** `Disallow: /`. — [media.swagit.com/robots.txt](https://media.swagit.com/robots.txt)
- **eCode360:** Cloudflare challenge. — [ecode360.com/SU1223](https://ecode360.com/SU1223)

**Open to us** (verified):
- **Legistar:** Web API and calendar both answer, e.g. [webapi.legistar.com/v1/dupage/bodies](https://webapi.legistar.com/v1/dupage/bodies).
- **CivicClerk:** API answers, e.g. [maconbibbcoga.api.civicclerk.com/v1/Events](https://maconbibbcoga.api.civicclerk.com/v1/Events?$top=1).
- **eSCRIBE:** portal home answers ([pub-loudoun](https://pub-loudoun.escribemeetings.com/robots.txt) robots 404). The NY pilot found its PDF stream behind a challenge.
- **NovusAgenda:** [polkcounty.novusagenda.com/agendapublic](https://polkcounty.novusagenda.com/agendapublic/meetingsresponsive.aspx), robots 404.
- **OnBase Agenda Online:** [onbaseep22.mesacounty.us/OnBaseAgendaOnline](https://onbaseep22.mesacounty.us/OnBaseAgendaOnline).
- **AgendaSuite:** [agendasuite.org/iip/grayson](https://agendasuite.org/iip/grayson).
- **BoardBook:** [meetings.boardbook.org](https://meetings.boardbook.org/Public/Organization/1365).
- **SuiteOne:** [rushcoin.suiteonemedia.com](https://rushcoin.suiteonemedia.com/?embed=1).
- **Municode Meetings:** [meetings.municode.com/PublishPage](https://meetings.municode.com/PublishPage/index?cid=DOUGHERTY&ppid=8eef0464-395e-4aa7-8fda) answers, robots 404. But some tenant hosts declare `Crawl-delay: 15`, e.g. `huerfanocounty-co.municodemeetings.com` and `wallercounty-tx.municodemeetings.com`.

**Vendor consolidation** (secondary):
- **CivicPlus** acquired Municode (2021). The combined company serves over 7,000 customers, and Municode Meetings is now sold as CivicPlus "Essential Agenda and Meeting Management". — [CivicPlus news](https://www.civicplus.com/news/nn/civicplus-acquires-municode/), [GovTech](https://www.govtech.com/biz/civicplus-acquires-70-year-old-ordinance-compiler-municode), [Municode Meetings page](https://municode.com/meetings/page/take-your-public-meetings-new-level-transparency-efficiency-municode)
- **Granicus** bought Accela's legislative-management business (iQM2), with about 450 customers. — [K1](https://k1.com/granicus-purchases-legislative-management-business-from-accela/)
- **Granicus** acquired Rock Solid (PrimeGov's parent) in Oct 2022. — [PrivSource](https://www.privsource.com/acquisitions/deal/9zSrxD), [CB Insights](https://www.cbinsights.com/compare/granicus-vs-primegov)
- **Diligent** owns BoardDocs ("since 2016") and iCompass, and launched Diligent Community in 2022. — [Diligent BoardDocs page](https://www.diligent.com/lp/boarddocs), [Business Wire 2022](https://www.businesswire.com/news/home/20220331005921/en/)
- **BoardDocs** claims over 3,000 organizations; 6sense estimates about 5,500. — [6sense](https://6sense.com/tech/board-management/boarddocs-market-share)
- **Simbli** (GSBA subsidiary) claims over 1,200 boards in 25 states, mostly school boards. — [TechLearning](https://www.techlearning.com/ed-tech-ticker/11295)

### Inferences
**Ranked adapter investments for siting coverage:**
1. **A generic auto-discovering document-listing adapter**, with WordPress wp-json/FileBird, Revize, CivicPlus DocumentCenter/Archive.aspx and Texas county-template modes. Highest volume: about 270 counties now, plus most PA/OH/MI/WI townships and cities.
2. **Statewide portal adapters for UT and NV.** One adapter each covers every county and municipality.
3. **Municode Meetings.** It is open. Accept a 15 s crawl delay for low-volume daily checks.
4. **NovusAgenda + OnBase Agenda Online + AgendaSuite.** Open, ASP.NET-style, small clusters in GA, TX, CO and UT.
5. **Vendor partnerships instead of adapters:**
   - Granicus, which covers ViewPublisher, iQM2 and PrimeGov. Together these are about 44 counties in the census plus many large cities: Temple and Amarillo TX; Manassas and Chesapeake VA; Mount Pleasant and DeForest WI.
   - Diligent, which covers BoardDocs and iCompass.

   One allow-listing deal each would unlock more siting-relevant cities than any single adapter. HeyGov (Wisconsin towns) needs the same approach.

**Crawl-delay policy.** Raising the cap from 10 s to "honor any delay, at most N requests a day per host" would add about 50 counties (3%), mostly Indiana, without any politeness cost. A daily agenda check needs only 1–5 requests per host.

### Gaps
- BuiltWith-style vendor customer lists by state were not available. Platform shares come from the census, not vendor rosters.
- Granicus Legistar versus ViewPublisher could not be split for cities that use both.

## Q4. Which states have a statewide feed comparable to MassDEP wetlands filings or the RI Secretary of State portal?

### Takeaway
**Verified RI-class meeting portals:**
- **Nevada** (notice.nv.gov, mandatory for all public bodies);
- **Utah** (Utah Public Notice Website, all counties and municipalities).

**Verified MassDEP-class project feeds:**
- **Vermont Act 250 daily agenda**;
- **Minnesota EQB Monitor**, weekly; it carries data-center EAWs and AUARs;
- **NY DEC DART** on data.ny.gov, a current Socrata API;
- **SPP's active interconnection-queue CSV** (with county) and **EIA-860M** (monthly), both national or regional.

Most other promising state sources refuse bots:
- **robots disallow:** PA eFACTS and PA Bulletin, NJDEP DataMiner, MI MiEnviro, GA DCA DRI, VA SCC, SC PSC, NM PRC, TX Comptroller JETI, ERCOT downloads;
- **WAF or 403:** NH OneStop, VA DEQ notices, WI PSC ERF, NCUC, MN eDockets, CO PUC, MISO's queue API.

**Press-association public-notice sites** are reachable in about 20 states but are built on ASP.NET postback search. Robots allow them, but they are not feeds.

### Cited Findings
- **Nevada:** NRS 241.020(4)(b) makes "posting the notice on the official website of the State pursuant to NRS 232.2175 not later than 9 a.m. of the third working day before the meeting" part of *minimum public notice*. The notice must include an agenda (241.020(3)(d)). — [NRS 241](https://www.leg.state.nv.us/NRS/NRS-241.html) (verified)
  - notice.nv.gov's home page lists statewide upcoming meetings with "Date Posted". 162 of 182 rows link out to the body's own agenda page (Granicus, PrimeGov, CivicClerk, Revize and others). — [notice.nv.gov](https://notice.nv.gov/) (verified; robots.txt 404)
  - All public bodies must post per NRS 241.015(4). — [notice.nv.gov Help](https://notice.nv.gov/Home/Help) (secondary)
- **Utah:** the Public Notice Website lists 31 county entities (all 29 counties) and 270 municipalities, reached by plain GETs: `/pmn/list/entities.html?id=2`, `/pmn/list/publicBodies.html?id=…`, `/pmn/list/notices.html?id=…`.
  - Agenda files are hosted at `/pmn/files/<id>.pdf`. The Millard County Commission list showed agendas for Sept–Oct 2026 and a "Notch Peak Project" hearing notice.
  - robots.txt allows everything. — [utah.gov/pmn](https://www.utah.gov/pmn/), [Millard County Commission notices](https://www.utah.gov/pmn/list/notices.html?id=1846&page=0), [utah.gov robots](https://www.utah.gov/robots.txt) (verified)
  - The posting duty is in Utah Code 63A-16-601 and 52-4-202. — [Utah Archives](https://archives.utah.gov/Public-Notice-Website) (secondary)
- **Vermont:** the Act 250 Agenda is an "aggregate list of Act 250 projects that have been noticed or for which a decision or Jurisdictional Opinion (JO) has been issued… updated daily". It covers a 3-week window (61 projects on 2026-10-11) as an HTML table with applicant, town, hearing date and comment deadline. — [anrweb.vt.gov/ANR/Act250/agenda.aspx](https://anrweb.vt.gov/ANR/Act250/agenda.aspx) (verified)
  - ePUC is reachable. — [epuc.vermont.gov](https://epuc.vermont.gov/) (verified)
- **Minnesota:** the EQB Monitor is published every Tuesday as a GovDelivery bulletin. The Oct 6, 2026 issue (Vol. 50, No. 40) lists each project with location (city/township; county), process (EAW, AUAR…), step and comment deadline. — [EQB Monitor Oct 6, 2026](https://content.govdelivery.com/accounts/MNEQB/bulletins/42d3d41), [EQB Monitor page](https://www.eqb.state.mn.us/eqb-monitor) (verified)
  - EQB has a "Data centers FAQ" page and an ER projects database. — [ER data](https://www.eqb.state.mn.us/environmental-review/environmental-review-data) (verified)
  - The Hermantown hyperscale data-center EAW petition was noticed in the Monitor. — [Hermantown petition letter](https://hermantownmn.com/wp-content/uploads/2025/10/Complete-Petition-Transmittal-Letter-Petition-Hermantown-Data-Center.pdf) (secondary)
- **New York DEC DART** on Socrata is current: a 2026-09-21 Islip application was returned. Fields include town, applicant, permit type (including freshwater wetlands and excavation and fill), SEQR class and status. — [data.ny.gov mbk7-f2r2](https://data.ny.gov/resource/mbk7-f2r2.json?$limit=2&$order=:updated_at%20DESC) (verified)
- **Delaware:** the DNREC "Storm Water Notices of Intent" dataset answers the Socrata API and is stamped updated 2026-10-11. But the newest `datereceived` is **2024-04-17**, so the content is stale. — [data.delaware.gov 3s4n-3up9](https://data.delaware.gov/resource/3s4n-3up9.json?$limit=3&$where=datereceived%20IS%20NOT%20NULL&$order=datereceived%20DESC) (verified)
  - The Delaware public meeting calendar's config sits under `/assets/`, which its robots.txt disallows. — [publicmeetings.delaware.gov/robots.txt](https://publicmeetings.delaware.gov/robots.txt) (verified)
- **SPP active GI queue:** a CSV last updated 10/9/2026, 1,020 lines, with "Nearest Town or County" and state for CO, TX Panhandle, KS, OK and others. — [opsportal.spp.org/Studies/GenerateActiveCSV](https://opsportal.spp.org/Studies/GenerateActiveCSV) (verified)
- **EIA-860M:** monthly generator xlsx files, e.g. [august_generator2026.xlsx](https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx), 13.9 MB, fetched OK. — (verified)
- **Blocked feeds** (verified):
  - **robots.txt disallows:**
    - ERCOT: `Disallow: /misdownload` and `/misapp`, which covers the GIS report downloads ([ercot.com/robots.txt](https://www.ercot.com/robots.txt));
    - Georgia DRI ([apps.dca.ga.gov](https://apps.dca.ga.gov/DRI/Submissions.aspx) robots `Disallow: /`);
    - MI EGLE MiEnviro ([robots](https://mienviro.michigan.gov/robots.txt) "block all crawling");
    - [NJDEP DataMiner](https://njems.nj.gov/DataMiner/);
    - [PA eFACTS](https://www.ahs.dep.pa.gov/eFACTSWeb/);
    - [PA Code & Bulletin](https://www.pacodeandbulletin.gov/);
    - [VA SCC docket search](https://www.scc.virginia.gov/docketsearch);
    - [SC PSC DMS](https://dms.psc.sc.gov/);
    - [NM PRC eDocket](https://edocket.nmprc.state.nm.us/);
    - [TX Comptroller JETI](https://comptroller.texas.gov/economy/development/jeti/).
  - **Cloudflare challenges:** [MISO GI queue API](https://www.misoenergy.org/api/giqueue/getprojects), [WI PSC ERF](https://apps.psc.wi.gov/ERF/ERFsearch/default.aspx), [NCUC](https://starw1.ncuc.gov/NCUC/page/Dockets/portal.aspx), [indianapublicnotices.com](https://www.indianapublicnotices.com/).
  - **Akamai 403s:** [NHDES OneStop](https://www4.des.state.nh.us/DESOnestop/BasicSearch.aspx), [VA DEQ public notices](https://www.deq.virginia.gov/permits/public-notices).
  - **Plain 403s:** [MN eDockets](https://www.edockets.state.mn.us/), [CO PUC](https://puc.colorado.gov/e-filings).
- **Reachable dockets** (home page only; machine readability not tested; verified):
  - [OH PUCO/OPSB DIS](https://dis.puc.state.oh.us/)
  - [IL ICC](https://www.icc.illinois.gov/docket/)
  - [IN IURC](https://iurc.portal.in.gov/)
  - [IA EFS](https://efs.iowa.gov/)
  - [AZ ACC](https://edocket.azcc.gov/)
  - [GA PSC](https://psc.ga.gov/search/)
  - [KY PSC](https://psc.ky.gov/)
  - [MD PSC DMS](https://webpscxb.psc.state.md.us/DMS/)
  - [CT Siting Council pending matters](https://portal.ct.gov/csc/1_applications-and-other-pending-matters/pending-matters)
  - [Atlanta Regional Commission DRI page](https://atlantaregional.org/what-we-do/community-development/developments-of-regional-impact/)
- **Press-association notice sites:** reachable in PA, OH, MI, IL, WI, MN, IA, VA, NC, GA, SC, TX, AZ, NV, CO, NJ, MD/DC, TN, UT, MO and OK.
  - Most run one ASP.NET platform: cookieless `(S(...))/default.aspx` sessions, `Search.aspx`, `Details.aspx`.
  - Robots allow all except system folders. — [publicnoticepa.com/robots.txt](https://www.publicnoticepa.com/robots.txt), [publicnoticevirginia.com/robots.txt](https://www.publicnoticevirginia.com/robots.txt)
  - Blocked: Indiana (Cloudflare). robots disallow: NM, VT, KY and LA. No such domain found: ME and NH. — (verified)

### Inferences
- **NV and UT can each be covered with one adapter, as in RI.**
  - **Utah's portal hosts the agenda files itself.** It is closer to RI.
  - **Nevada's portal is mostly an index with posting dates.** Its links lead to vendor pages, some of them closed (PrimeGov, Granicus), so reading the agenda text still needs per-vendor access. As a "something was noticed" signal with posting dates, it is still complete.
- **For MassDEP-style early warning,** the best verified substitutes are:
  - VT Act 250 (daily);
  - MN EQB Monitor (weekly; data-center EAWs and AUARs);
  - NY DART (Socrata);
  - SPP's queue CSV and EIA-860M.

  Interconnection queues name the county and the MW, months before local filings.
- **The richest state permit systems** (PA, NJ, MI, GA DRI, NH) are robots- or WAF-closed. They would need a data request, a bulk export or written permission. The Georgia DRI is the single most valuable closed source for data centers. The secondary press reports Switch, Vantage, Butts, Spalding and Douglas DRIs, e.g. [AJC](https://feeds.ajc.com/business/2025/11/data-centers-to-get-regional-review-public-notice-on-key-georgia-website) and [DCD](https://www.datacenterdynamics.com/en/news/vantage-files-for-two-data-center-campuses-outside-atlanta-georgia/).
- **Press-association sites could be the catch-all for small townships' legal notices.** But they need POST searches, and their notice pages are reported to sit behind CAPTCHAs (not verified). Treat them as a partnership target (paid feed), not a crawl target.

### Gaps
- I did not POST to any search form, so Utah's search, the press sites and the CSC tables were not exercised.
- TCEQ, Ohio EPA, IDEM, IEPA, WDNR and GA EPD permit databases were not reached at a usable URL in the time available.
- Terms of use were not read for UT, NV or SPP. Read them before launch, as was done for RI.

## Q5. Cost to reach 60%+ coverage of siting bodies, and overall ranking

### Takeaway
**Cheapest and most complete:**
1. UT
2. NV
3. VT and CT (as state-docket states)
4. ME

**Next tier (Medium cost):**
5. VA
6. MN
7. TX cities
8. IL
9. NM, CO, MD, NC
10. IN, if long crawl delays are honored

**Expensive (High cost):** the township states (PA, OH, MI, WI) and NJ. They need the generic adapter plus per-town curation and still hit bot walls and towns with no agendas online. The same holds for KY, TN, MO, OK, SC, IA and AZ.

AZ is a special case: it has few bodies, so two vendor permissions (Destiny, Granicus) plus Cloudflare allow-listing would flip it.

### Cited Findings
| Rank | State | Cost to 60%+ | Why (evidence in Q1–Q4) |
|---|---|---|---|
| 1 | UT | Low | One portal holds all 29 counties and 270 municipalities, with hosted agenda files (verified) |
| 2 | NV | Low | Mandatory state portal (NRS 241.020(4)(b)). 87% county agenda evidence; 53% readable now (verified) |
| 3 | VT | Low | Siting is at the PUC (§248) and Act 250. The Act 250 daily agenda plus ePUC cover state decisions (verified) |
| 4 | CT | Low (state) / High (towns) | Siting Council decides over 1 MW. Its pending-matters page is reachable; towns are weak (NE probe) |
| 5 | ME | Low | NE probe: 5 of 6 towns on CivicPlus, stock board names work |
| 6 | VA | Medium | 45% of counties readable now (CivicPlus 18, CivicClerk 11). Closed BoardDocs/Granicus plus 21% WAF block the rest. Data-center counties are the priority market |
| 7 | MN | Medium | 41% of counties readable. The EQB Monitor covers data-center environmental review statewide. PUC eDockets 403 |
| 8 | TX | Medium | Data-center cities: 6 of 10 readable (Legistar, CivicClerk). Counties 30% readable, but only 7% blocked. A Texas county-template adapter would add many. ERCOT queue closed to bots |
| 9 | IL | Medium | 41% of counties readable, 14% blocked. Cities 6 of 9 readable |
| 10 | NM, CO, MD, NC | Medium | 35–46% of counties readable. CO and NC lose about 20–25% to walls (CloudFront `colorado.gov`, Cloudflare) |
| 11 | IN | Medium | 29% readable, rising to 56% if crawl delays of 30–300 s are honored (19 counties) |
| 12 | NH, DE, LA, GA | Medium-High | NH: Cloudflare on half the towns, and NHDES blocked. GA: 42% of counties "none found", and DRI robots-closed |
| 13 | PA, OH, MI, WI, NJ | High | Thousands of townships and municipalities. Township web presence: PA about 50%, OH about 25%, MI 78%, WI about 85%, but agenda posting is far lower. HeyGov and Granicus closed in WI; NJDEP, MiEnviro, PA eFACTS and PA Bulletin all robots-closed |
| 14 | IA, SC, KY, TN, MO, OK, AZ | High | 16–26% readable now. Heavy "none found" (KY 59%, MO 71%) or heavy blocking (SC 33%, AZ 47%) |

(Ranks are estimates built on the verified per-state data above.)

### Inferences
- **"Low" means** one adapter or source, a few days of work, and at least 60% of deciding bodies.
- **"Medium" means** about 60% only after:
  - the generic adapter;
  - about 1–2 weeks of curation per state (at 10–20 minutes per hand listing, per the NY pilot);
  - at least one vendor allow-listing.
- **"High" means** 60% is not reachable without vendor or WAF permissions, and without newspaper legal-notice data for townships that post nothing online.
- **The two cheapest national multipliers:**
  - Vendor allow-listing deals with Granicus (ViewPublisher, iQM2, PrimeGov) and Diligent (BoardDocs, iCompass, Community).
  - A paid or partnered feed from the state press associations' shared public-notice platform. Each would raise every High state at once.

### Gaps
- The cost bands are judgment calls, not costed engineering estimates.
- Coverage is measured on county governments plus small municipal samples, not on the full municipal universe of each state.
- Lead times outside RI, NY and the NE probe were not measured.
- The Michigan MTA scrape was limited to 272 of 1,241 townships to keep request volume polite; that server took about 10 s per page.
