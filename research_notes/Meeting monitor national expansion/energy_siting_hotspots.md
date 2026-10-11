# Energy siting hotspots below state level: where local bodies will decide the most clean-energy projects in 2026–2028

Prepared 2026-10-11 for 351 Watch expansion planning. This file extends `../Meeting monitor deep dive/expansion_markets.md` (state ranking, PA #1) and `../Meeting monitor deep dive/state_agenda_laws.md` (who decides siting in each state) down to county clusters. It does not redo the state work.

**Labels used on every claim**
- **[V]** verified: read this session in a primary source (a queue file, statute or bill page, a county or township document, or the Sabin database). For queue and Sabin numbers, "[V, my tabulation]" means I downloaded the primary file and counted it myself.
- **[S]** secondary: news, a law firm, an advocacy group, or a search-result summary of a page I did not open in full.
- **[E]** estimate or judgment.
- **[K]** background knowledge, not verified this session.

**Primary datasets downloaded and tabulated this session (all fetched 2026-10-11)**
- LBNL "Queued Up" 2026 edition, row-level file, data as of end of 2025 — [lbnl_ix_queue_data_file_thru2025.xlsx](https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx). I counted status = active projects whose type includes solar, battery or onshore wind, splitting multi-county projects equally between counties.
- PJM planning queue XML, live as of Oct 2026 — [PlanningQueues.xml](https://www.pjm.com/pub/planning/downloads/xml/PlanningQueues.xml). I counted these statuses: Active, Engineering & Procurement, Confirmed, Suspended, Under Construction and Partially in Service. I used incremental MW only (max of MWEnergy and MWCapacity); 0-MW rows were dropped. Capacity-increase (CIR) requests at existing sites remain, so PJM counts run higher than LBNL.
- ERCOT GIS Report, September 2026 (published 2026-10-01): [report list](https://www.ercot.com/misapp/GetReports.do?reportTypeId=15933) and [file](https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1281327706). I used the "Project Details – Large Gen" sheet, counting solar, wind and battery (OTH/BA) projects.
- Other ISO and federal files:
  - SPP active queue CSV, "Last Updated 10/9/2026": [GenerateActiveCSV](https://opsportal.spp.org/Studies/GenerateActiveCSV).
  - CAISO public queue report, run 10/11/2026: [PublicQueueReport.xlsx](http://www.caiso.com/PublishedDocuments/PublicQueueReport.xlsx).
  - NYISO queue: [NYISO-Interconnection-Queue.xlsx](https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx).
  - EIA-860M, August 2026: [august_generator2026.xlsx](https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx).
- Sabin Center "Opposition to Renewable Energy Facilities," 6th edition, live database: [oppositionreport.org/reports/current](https://oppositionreport.org/reports/current/). The page was modified 2026-10-01 and the data run through Dec 31, 2025. I parsed all 866 local restrictions (801 in effect, 65 expired) and 569 contested projects, and tagged each by county.
- Census of Governments 2022, individual unit file: [govt_units_2022.ZIP](https://www2.census.gov/programs-surveys/gus/datasets/2022/govt_units_2022.ZIP). I counted active counties, municipalities and townships per county.
- **Not obtained:** the MISO queue. Its API returned a Cloudflare 403. MISO-territory counties (most of IN outside AEP/NIPSCO, central and southern IL, MI, MN, WI, IA, AR, LA) are therefore covered only by LBNL's end-2025 snapshot.
- **Search budget:** the shared web-search budget ran out partway through. Later evidence comes from direct fetches of known URLs. Some items below are marked [S] from search-result summaries I could not open.

---

## Ranked list: which sub-state areas will see the most locally decided clean-energy siting, with the highest stakes, in 2026–2028

### Takeaway
Twenty-two areas across five regions qualify. The top tier sits where three things overlap: many locally decided queued projects, a dense and growing opposition record, and hundreds of small zoning bodies that national county-level tools do not reach.
- **Top tier:** southern Michigan townships, Southside Virginia, central Ohio, the Michigan Thumb, east-central Indiana and central Pennsylvania.
- **Regional coverage:** Midwest 11, Mid-Atlantic 5 (2 VA, 3 PA; PA is also Census Northeast), South 2, West 3, Northeast beyond MA/NY/RI 1 (Maine).

### Cited Findings

**How the rank was built [E].**
- Composite = 40% pipeline + 35% opposition + 15% number of zoning bodies + 10% 2024–2026 trend.
- **Pipeline:** LBNL active GW and project count, each multiplied by a state "local share" factor for how much of the queue local bodies decide. The factors are: PA, IN, KS, GA 1.0; VA, AZ, CO, NM, NE, ME, NC, SC 0.9; OH 0.8; IL 0.7; MI, NJ 0.6; IA, KY 0.5; TX, WI, MN, DE 0.3; MD 0.2.
  - In PJM states the count is the larger of the LBNL and PJM-XML counts.
- **Opposition:** Sabin in-effect local restrictions + 2 × canceled contested projects + 1 × other contested projects.
- Every factor is log-scaled to 0–10.
- **Judgment overrides:** I moved central PA from 15th to 6th and northeast PA from 16th to 13th. I moved Arizona from 4th to 8th. Reasons: Sabin under-catalogs PA township ordinances relative to how many exist; PA is fully local at any size with HB 502 still stalled; and Arizona's 89 bodies are county-grain, which national tools already cover (see `expansion_markets.md` §4.4).
- Without overrides, the composite's top 10 are: MI-south 82.8, VA-Southside 81.4, MI-Thumb 81.3, AZ 81.1, OH-central 79.9, IN-east-central 79.5, KS-central/east 78.2, VA-Piedmont/North 77.3, IL-central/south 75.9, OH-northwest 74.8 [E, my calculation from the [V] tabulations].

**Ranked table.**
- Columns:
  - Queue = LBNL end-2025 active solar, storage and wind: projects / GW / projects with storage.
  - PJM = live PJM XML requests / GW, Oct 2026.
  - Sabin = in-effect local restrictions / contested projects (of which canceled).
  - Bodies = counties / municipalities / townships (Census 2022).
- Queue, PJM, Sabin and Bodies are all [V, my tabulation] from the files listed above.

| # | Area (counties in cluster) | Region | Queue (LBNL) | PJM (Oct 2026) | Sabin | Bodies c/m/t | Who decides |
|---|---|---|---|---|---|---|---|
| 1 | **Southern Michigan townships**: Monroe, Lenawee, Hillsdale, Branch, Calhoun, Jackson, Washtenaw, St. Joseph, Cass, Van Buren, Berrien, Kalamazoo, Eaton, Ingham, Livingston, Shiawassee, Clinton, Allegan (18) | Midwest | 111 / 19.1 GW / 48 | 30 / 2.8 GW (SW MI only) | 35 / 10 (2) | 18 / 157 / 318 | Township boards and planning commissions. Below 50 MW is local; at 50 MW+ the township acts first, and the MPSC takes over if there is no CREO or a moratorium is in place (PA 233). |
| 2 | **Southside Virginia**: Mecklenburg, Halifax, Pittsylvania, Brunswick, Greensville, Charlotte, Lunenburg, Sussex, Southampton, Prince Edward, Nottoway, Dinwiddie, Surry, Isle of Wight, Henry, Campbell, Appomattox, Buckingham, Cumberland, Prince George, Amelia, Powhatan, Charles City (23) | Mid-Atlantic | 113 / 11.8 GW / 37 | 273 / 24.5 GW | 13 / 20 (13) | 23 / 47 / 0 | County boards of supervisors (conditional or special-use permits, comprehensive-plan review, siting agreements) and county planning commissions. |
| 3 | **Central Ohio solar belt**: Madison, Union, Logan, Champaign, Clark, Fayette, Pickaway, Licking, Marion, Morrow, Knox, Fairfield, Hardin, Delaware, Ross, Clinton, Greene, Highland (18) | Midwest | 66 / 7.1 GW / 13 | 202 / 18.2 GW | 11 / 14 (5) | 18 / 150 / 274 | County commissioners under SB 52 (restricted areas, and veto of OPSB-size wind and solar projects). Township trustees and zoning for projects under 50 MW, plus township referenda. The OPSB issues the 50 MW+ certificate. |
| 4 | **Michigan Thumb / Saginaw Bay**: Huron, Sanilac, Tuscola, Saginaw, Bay, Lapeer, Genesee, St. Clair, Gratiot, Montcalm, Isabella, Midland (12) | Midwest | 91 / 16.3 GW / 30 | — (MISO) | 31 / 13 (7) | 12 / 100 / 244 | Township boards. Huron County zones some townships [K]. The PA 233 MPSC route applies as in area 1. |
| 5 | **East-central / northeast Indiana**: Randolph, Jay, Blackford, Delaware, Grant, Huntington, Wells, Adams, Allen, Madison, Henry, Wayne, Howard, Tipton, Miami, Wabash, Rush, Decatur, Hamilton (19) | Midwest | 63 / 7.7 GW / 22 | 131 / 13.2 GW | 17 / 9 (6) | 19 / 136 / 214 (townships do not zone) | County commissioners, county councils, plan commissions and BZAs. Local at any size. |
| 6 | **Central Pennsylvania (Alleghenies)**: Clearfield, Centre, McKean, Elk, Cambria, Somerset, Jefferson, Indiana, Armstrong, Clinton, Blair, Huntingdon, Bedford, Fulton, Cameron, Potter (16) | Mid-Atlantic / NE | 74 / 5.6 GW / 21 | 164 / 7.9 GW | 12 / 0 | 16 / 197 / 340 | Township supervisors, borough councils, planning commissions and zoning hearing boards. Local at any size. |
| 7 | **Central and eastern Kansas**: Sedgwick, Sumner, Reno, McPherson, Harvey, Dickinson, Saline, Geary, Riley, Marion, Linn, Bourbon, Douglas, Shawnee, Leavenworth, Johnson, Franklin, Osage, Pottawatomie, Wabaunsee, Coffey, Butler, Cowley, Kingman, Harper (25) | Midwest / Plains | 49 / 11.3 GW / 19 | — (SPP) | 15 / 8 (4) | 25 / 217 / 417 (townships generally do not zone [K]) | County commissions and planning boards. No state siting board. |
| 8 | **Arizona Phoenix exurbs and western counties**: Maricopa, Pinal, Yuma, La Paz, Mohave, Yavapai, Navajo, Apache, Coconino, Cochise, Pima (11) | West | 185 / 81.9 GW / 163 | — | 5 / 6 (3) | 11 / 78 / 0 | County boards of supervisors and P&Z commissions, plus towns (Buckeye, Coolidge, Eloy and others). The state siting committee covers thermal plants only [K]. |
| 9 | **Virginia Piedmont / North**: Culpeper, Orange, Fauquier, Caroline, Spotsylvania, Louisa, King George, Prince William, Loudoun, Stafford, Hanover, Goochland, Fluvanna, Madison, Frederick, Warren, Page, Shenandoah, Rockingham, Augusta, Clarke, King William, King and Queen, Essex, Westmoreland, Amherst (26) | Mid-Atlantic | 83 / 6.4 GW / 44 | 186 / 13.6 GW | 16 / 13 (10) | 26 / 50 / 0 | County boards of supervisors and planning commissions. This is also the data-center belt. |
| 10 | **Northwest Indiana**: Pulaski, White, Jasper, Starke, Newton, LaPorte, St. Joseph, Marshall, Fulton, Cass, Benton, Carroll, Kosciusko, Porter, Lake, Elkhart (16) | Midwest | 81 / 14.8 GW / 33 | 69 / 8.7 GW | 9 / 3 (2) | 16 / 119 / 203 | County commissioners, plan commissions and BZAs. |
| 11 | **Northwest Ohio**: Hancock, Van Wert, Allen, Auglaize, Putnam, Paulding, Henry, Wood, Fulton, Seneca, Crawford, Wyandot, Defiance, Williams, Mercer, Sandusky, Huron, Richland, Erie, Ottawa, Shelby, Darke (22) | Midwest | 36 / 3.4 GW / 10 | 106 / 10.1 GW | 12 / 10 (6) | 22 / 216 / 312 | Same as area 3 (SB 52 counties plus townships). |
| 12 | **Central and southern Illinois (Ameren/MISO)**: McLean, Christian, Tazewell, Peoria, Logan, Sangamon, Fulton, Perry, Clark, Clay, Fayette, Piatt, Champaign, Macon, Moultrie, Montgomery, Vermilion, DeWitt, Woodford, Effingham, Bond, Randolph, Washington, Shelby, Coles (25) | Midwest | 158 / 29.3 GW / 55 | 50 / 6.4 GW | 11 / 8 (1) | 25 / 316 / 407 (townships do not zone) | County boards and ZBAs: a hearing is mandatory, but the state caps the standards (see Q3). |
| 13 | **Northeast / north-central Pennsylvania**: Luzerne, Lackawanna, Columbia, Montour, Northumberland, Schuylkill, Carbon, Monroe, Wayne, Pike, Lycoming, Union, Snyder, Wyoming, Susquehanna, Bradford, Sullivan, Tioga (18) | Mid-Atlantic / NE | 38 / 1.3 GW / 7 | 113 / 3.1 GW | 5 / 10 (6) | 18 / 204 / 395 | Township supervisors, borough councils and ZHBs. |
| 14 | **Northern Illinois (ComEd)**: Lee, Ogle, DeKalb, Kankakee, Iroquois, Livingston, McHenry, Will, Kendall, Grundy, LaSalle, Boone, Winnebago, Stephenson, Whiteside, Bureau, Ford, Carroll, Jo Daviess (19) | Midwest | 111 / 17.9 GW / 38 | 182 / 23.1 GW | 7 / 8 (5) | 19 / 273 / 377 | County boards and ZBAs under state standards; municipalities. Heavy community-solar activity (EIA small units in Will, McHenry, Kankakee and Kane). |
| 15 | **Colorado Eastern Plains / Front Range**: Pueblo, Weld, Kit Carson, Lincoln, Morgan, Adams, Elbert, El Paso, Cheyenne, Kiowa, Logan, Larimer, Arapahoe, Washington, Yuma, Crowley, Otero, Prowers, Bent, Phillips, Sedgwick (21) | West | 141 / 31.5 GW / 67 | — | 8 / 3 (2) | 21 / 118 / 0 | County commissioners (zoning and 1041 powers) and municipalities. No state siting board. |
| 16 | **Middle and south Georgia**: Laurens, Sumter, Jefferson, Hancock, McDuffie, Washington, Warren, Emanuel, Mitchell, Decatur, Thomas, Dougherty, Crisp, Dooly, Toombs, Bulloch, Baldwin, Greene, Oglethorpe and 22 more (41) | South | 82 / 15.6 GW / 38 | — | 10 / 3 (2) | 41 / 161 / 0 | County commissions and planning commissions. No state siting. |
| 17 | **South-central Pennsylvania farm belt**: Adams, York, Lancaster, Franklin, Cumberland, Lebanon, Dauphin, Perry, Berks, Chester, Juniata, Mifflin (12) | Mid-Atlantic / NE | 19 / 0.5 GW / 5 | 74 / 2.4 GW | 21 / 4 (2) | 12 / 174 / 319 | Township supervisors and ZHBs, with heavy agricultural-zoning conflict. |
| 18 | **Southwest Indiana coal country**: Sullivan, Vigo, Vermillion, Fountain, Greene, Knox, Gibson, Posey, Pike, Daviess, Dubois, Spencer, Warrick, Clay, Parke, Putnam, Owen, Martin (18) | Midwest | 83 / 15.4 GW / 34 | 28 / 5.8 GW | 4 / 4 (1) | 18 / 109 / 188 | County commissioners and plan commissions. |
| 19 | **Southeast Nebraska**: Lancaster, Gage, Saline, Otoe, Butler, Seward, Saunders, Cass, Johnson, Jefferson, Thayer, Fillmore, York, Polk, Nemaha, Richardson, Pawnee, Burt, Dodge, Colfax, Cuming (21) | Midwest / Plains | 29 / 5.2 GW / 9 | — (SPP) | 18 / 7 (1) | 21 / 188 / 115 | County boards and planning commissions. Some townships zone: Sabin lists 6 township restrictions in Butler County. |
| 20 | **Central and North Texas (ERCOT)**: Milam, Robertson, Navarro, Ellis, Hill, Limestone, Freestone, Johnson, Hood, Kaufman, Henderson, Fannin, Lamar, Hopkins, Falls, Bell, Williamson, Bastrop, Lee, Burleson, Brazos, Leon (22) | South | 258 / 50.7 GW / 177 | ERCOT GIS Sep 2026: 245 / 45.7 GW | 5 / 4 (1) | 22 / 189 / 0 | City councils (zoning inside city limits). Commissioners courts have no general zoning; their tools are tax abatements, resolutions, flood ordinances and Ch. 391 commissions. |
| 21 | **Central Maine towns**: Kennebec, Somerset, Waldo, Penobscot, Androscoggin, Oxford, Hancock, Franklin, Knox, Lincoln, Sagadahoc (11) | Northeast (beyond MA/NY/RI) | 12 / 0.8 GW / 1 | — (ISO-NE) | 25 / 12 (1) | 11 / 13 / 287 | Town select boards, planning boards and town meeting, plus a DEP permit. |
| 22 | **Central Oregon / Columbia Plateau**: Sherman, Crook, Deschutes, Wasco, Klamath, Morrow, Jefferson, Umatilla, Lake, Gilliam, Harney (11) | West | 205 / 78.7 GW / 133 | — | 1 / 7 (1) | 11 / 47 / 0 | County courts and commissions plus planning. Oregon's Energy Facility Siting Council takes larger sites by acreage and MW threshold [K]. This is the weakest-evidence entry. |

**Area notes: why each ranks, which fights, who gains and who loses** (developer and utility names are from the LBNL "developer" and "utility" fields and the Sabin project titles [V]; many queue rows have masked or blank developer names).

1. **Southern Michigan.**
   - Sabin's densest township restriction cluster in the US [V, my tabulation]:
     - Monroe County alone has 10 in-effect local restrictions (Bedford, Berlin, Frenchtown, Ida, LaSalle, Milan, Monroe Charter, Raisinville, Summerfield townships).
     - Livingston County has 7; Branch, Lenawee, Kalamazoo, Allegan and Ingham have several each.
   - Top queue counties: Calhoun 2.08 GW, Monroe 1.99 GW, Lenawee 1.95 GW, Van Buren 1.76 GW, Washtenaw 1.40 GW, Branch 1.38 GW [V, LBNL].
   - Contested projects: Mustang Mile (Lenawee), Thorn Lake and White Tail/Railsplitter (Washtenaw), Southwest Michigan Solar (Van Buren) are pending; Iosco Solar (Livingston) and Sandstone Creek (Eaton) were canceled [V, Sabin].
   - 2026 moratorium activity:
     - Baroda Township (Berrien Co.) adopted a utility-grade solar moratorium on Jan 19, 2026, and its definition explicitly includes "energy storage facilities" [V, [township PDF](https://barodatownship.org/wp-content/uploads/2026/01/ordinance43-moratorium-on-utility-grade-solar-energy-facilities-final.pdf)].
     - Oshtemo (Kalamazoo Co.) moved to extend its BESS moratorium [S, [WWMT](https://wwmt.com/news/arc/bess-oshtemo-battery-storage-energy-solar-project-township-board-planning-commission-protection-michigan-state-law-mpsc-wwmt)].
     - Meridian (Ingham Co.) passed a BESS moratorium in 2026, and Gun Plain (Allegan Co.) has one through Dec 2026 [V in prior notes: [Meridian notice](https://lansingcitypulse.com/charter-township-of-meridian-legal-notice-zoning-amendment-2026-04-battery-energy-storage-systems-moratorium/), [Gun Plain notice](https://www.gunplain.org/wp-content/uploads/Notice-of-Adoption-of-Ordinance-196-Temporary-Moratorium-on-Considering-Future-Applications-for-Battery-Energy-Storage-Systems.pdf)].
   - Gainers and losers:
     - Interconnecting utilities: METC/ITC (64 and 19 rows); DTE Electric is itself a queue developer (2 rows).
     - Developers: Decatur Storage LLC, Three Lakes Solar, Steelhead Solar, Bankson Solar [V, LBNL].
     - Landowners hold leases; township residents are the organized opposition.
2. **Southside Virginia.**
   - **Most canceled projects of any area:** 13 of 20 contested projects canceled [V, Sabin]. Examples: 7 Bridges, Lone Oak Agrisolar and New Hope Agrisolar (Mecklenburg); Monarch (Greensville); Blackwater (Sussex); Gabriel and Old Ridge Road (Prince Edward); Carver and Sycamore Cross (Isle of Wight / Surry).
   - **Largest live PJM request count of any area:** 273 requests / 24.5 GW. Sussex has 3.5 GW, Brunswick 2.9 GW, Mecklenburg 2.6 GW, Greensville 2.3 GW, Halifax 2.0 GW [V, PJM XML; county figures from the first-pass tabulation, which included facility totals].
   - **County caps:**
     - Mecklenburg capped solar at 2,325 acres (<1% of the county) in 2023, then voted unanimously on Apr 14, 2025 to drop utility-scale solar as a future allowed use. Three pending projects (Seven Bridges 80 MW, Antlers Road 90 MW, Finneywood 97 MW, ~500 acres each) compete for the remaining cap: "If any two of them get approved, that's the end of it" (county attorney) [S, [Cardinal News](https://cardinalnews.org/2025/04/15/mecklenburg-county-blocks-future-large-scale-solar-development/)].
     - The same article reports Pittsylvania and Henry adopted similar land caps, Halifax tightened its rules in late 2024 after a moratorium, and Greensville removed utility-scale solar as a use in June 2024 [S].
     - Pittsylvania's 2023 amendments set a 5-mile spacing rule and a 2% acreage cap per zoning district [S, 2023, [Chatham Star-Tribune](https://www.chathamstartribune.com/news/article_fd43026e-ce40-11ed-a14d-c7bed4d03718.html)].
   - Gainers: Dominion is the interconnecting utility on 101 of 113 rows and is itself a developer (15 rows); also Amelia Energy Facility LLC, Staunton Solar, Hillandale and Jarratt Energy Facility [V, LBNL].
3. **Central Ohio.**
   - Queue: Madison County is the single biggest Ohio county (LBNL 1.65 GW; PJM XML 22 requests). Union, Licking, Highland, Fairfield and Champaign follow [V].
   - SB 52 county restrictions in Clark, Clinton, Fairfield, Fayette, Greene, Knox, Licking, Logan, Madison, Marion and Union [V, Sabin].
   - Canceled projects: Chestnut (Marion), Chipmunk and Scioto Farms (Pickaway), Grange 500 MW (Logan), Richwood (Union) [V, Sabin].
   - Pending: Oak Run (Madison), Fountain Point (Logan), Frasier (Knox), Kingwood (Greene), Carnation and Eastern Cottontail (Fairfield), Circleville (Pickaway), Hillclimber (Champaign), Yellow Wood (Clinton) [V, Sabin].
   - 2026 actions [S, [OEC, updated Mar 30, 2026](https://theoec.org/campaign/ohio-utility-scale-solar-trends-2025/)]:
     - The OPSB denied Crossroads Solar (Morrow) in Feb 2026.
     - Staff recommended denial of Sloopy Solar (180 MW, Clark) and Carnation (142 MW, Fairfield).
     - Clark County banned all large solar and wind in Sept 2025; Morrow County banned it in five townships.
   - Gainers: utilities AEP (38 rows), ATSI (14), Dayton (13); developers Crossroads Solar I LLC, Riverlake Energy, Fountain Point Solar Energy LLC, Oak Run Solar Project LLC [V, LBNL].
4. **Michigan Thumb.**
   - Queue: Huron is the top Michigan county (3.85 GW, 17 projects); then Sanilac 2.36 GW, Saginaw 2.05 GW, Tuscola 1.43 GW [V, LBNL].
   - 31 in-effect restrictions [V, Sabin]: Bay, Tuscola, Montcalm, Sanilac and Genesee townships, plus Huron and St. Clair counties.
   - 7 cancellations [V, Sabin]: Filion, Meade and Huron Wind (Huron/Sanilac); Pegasus (Tuscola); Beaver Twp Wind (Bay); Goodland Twp Solar (Lapeer); Portside Solar (St. Clair).
   - Almer Township (Tuscola) is the lead appellant against the MPSC's PA 233 order [S, [Foster Swift, Jun 19, 2026](https://www.fosterswift.com/newsroom/news/michigan-supreme-court-zoning-control-renewable-energy-pa233-mpsc-appeal)].
   - Gainers: ITC (42 rows) and METC (35); Hackett Energy Storage LLC and DTE [V, LBNL].
5. **East-central Indiana.**
   - 17 in-effect county restrictions (Allen, Blackford, Decatur, Delaware, Hamilton ×2, Henry, Howard, Huntington, Madison ×2, Miami, Rush, Tipton, Wabash, Wayne, Wells) and 6 canceled projects (Big Blue Ribbon, Flat Rock, Hamilton Co. Wind, Harvest Wind, Prairie Breeze, West Fork) [V, Sabin].
   - Queue: Huntington 1.48 GW, Blackford 1.09 GW, Jay 11 projects [V, LBNL]; Randolph 20 requests and Jay 18 [V, PJM XML].
   - Jay County adopted one-year moratoria on commercial solar and on battery storage in April 2025 [S, [Commercial Review](https://thecr.com/news/2025/apr/28/moratoriums-put-in-place)].
   - Lone Oak Solar (Madison Co.) is a court case cited by Purdue Extension [S, [Purdue RSTEP deck](https://extension.purdue.edu/cdext/thematic-areas/community-planning/collaborative-projects/rstep/_docs/e-indiana-utility-preemption-declination.pdf)].
   - Gainers: AEP (50 rows) and Duke Energy Indiana (9); BR Solar Sheriff 2, Riverstart Solar Park VI, Leeward, Teays River Wind (f/k/a Blackford County Wind), Prairie Creek Wind, Tillman Storage, Muncie Solar 1 [V, LBNL].
6. **Central Pennsylvania.**
   - Queue:
     - Clearfield: 15 projects / 1.75 GW [V, LBNL]; 24 requests [V, PJM].
     - Centre: 14 projects, 8 with storage [V, LBNL]; 24 requests [V, PJM].
     - Cambria 11 projects, Somerset 9, McKean 0.95 GW [V, LBNL]. Somerset has 24 requests [V, PJM].
   - EIA-860M lists 6 planned units of 20 MW or less in Clearfield and 6 in Armstrong [V].
   - Restrictions: 12 in-effect township and borough restrictions (Benner, College, Halfmoon in Centre; Jackson and Upper Yoder in Cambria; and others) [V, Sabin]. Sabin lists no contested central-PA project, which likely reflects thin coverage rather than calm [E].
   - Gainers: utilities PENELEC (54 rows) and APS; developers CE-Black Moshannon OZ (3), RWE, Mineral Basin, Shallow Seam Energy Storage, Kimberlite, Moonlight Flats, CPV Maple Hill [V, LBNL].
7. **Central and eastern Kansas.**
   - 15 in-effect county restrictions (Douglas ×2, Franklin, Harvey, Johnson, Leavenworth, Linn, McPherson ×2, Osage, Pottawatomie, Reno, Sedgwick, Shawnee, Wabaunsee) and 4 canceled wind projects (Argyle Creek, Auburn Harvest, Eagle Rock, Leon) [V, Sabin].
   - Heatmap (Aug 24, 2026):
     - 21 counties nationally restrict solar, batteries and data centers at once; most were passed in 2026, and KS, IA and IN hold most of them.
     - Dickinson County, KS extended its moratorium to all energy development in spring 2026 [S, [Heatmap](https://heatmap.news/daily/data-centers-solar-batteries)].
   - 2026 county actions [S, search summaries; articles not opened]:
     - Saline: 4–0 vote, 3-year moratorium on data-center, nuclear and hydrogen facilities [[Yahoo](https://www.yahoo.com/news/articles/kansas-county-puts-moratorium-data-230922244.html)].
     - Geary: 1-year moratorium including wind, solar and BESS [[KSNT](https://www.ksnt.com/news/local-news/geary-co-approves-moratorium-on-data-center-development/amp/)].
     - Riley: 6-month data-center and BESS moratorium [[Manhattan Mercury](https://themercury.com/news/riley-county-still-not-ready-for-data-center-regulations/article_cfe37f3d-0ef7-4c3e-8d7d-250efe394df3.html)].
     - Reno: a petition sought a ban, with a June 9, 2026 decision date [[change.org](https://www.change.org/p/petition-for-moratorium-on-bess-and-data-centers-in-reno-county-kansas/u/34720965)].
     - Marion County area: commissioners leaned toward a battery moratorium despite the local co-op's pleas [[Peabody Gazette-Bulletin](https://www.peabodykansas.com/direct/county_ignores_plea_plans_battery_moratorium+5721county+436f756e74792069676e6f72657320706c65612c20706c616e732062617474657279206d6f7261746f7269756d)].
   - Queue: Linn 1.41 GW, Sedgwick 1.40 GW, Sumner 1.16 GW [V, LBNL]. Utility: Evergy/WERE (38 rows).
8. **Arizona.**
   - Largest locally permitted pipeline outside Texas: Maricopa 22.05 GW, La Paz 14.22 GW, Navajo 10.32 GW, Yuma 7.57 GW, Pinal 7.46 GW. 163 of 185 projects include storage [V, LBNL].
   - Arizona's Family (Oct 3, 2026) counts bans or restrictions on large solar and wind in Yavapai, Mohave and Navajo counties and in Chino Valley, Coolidge and Eloy. A Pinal supervisor said "Pinal County has just been solar fatigued" [S, [AZFamily](https://www.azfamily.com/2026/10/03/7-arizona-communities-restrict-solar-wind-projects-amid-growing-pushback/)].
   - Pinal P&Z recommended denial of NextEra's Valley Farms BESS while recommending approval of Copper Basin storage [S, [Pinal County document](https://intranet.pinal.gov/DocumentCenter/View/31732)].
   - Heatmap reports Pinal unanimously rejected an 8,122-acre solar farm [S, search summary of [Heatmap](https://heatmap.news/daily/data-centers-solar-batteries)].
   - Utilities: APS (94 rows), WAPA, SRP, TEP [V, LBNL]. Developer names are blank in LBNL for AZ.
9. **Virginia Piedmont / North.**
   - 10 cancellations [V, Sabin]: Almeda and Bealeton (Fauquier); Cape (Page); Cunningham Springs, Orange Road and Sunfish (Orange); Maroon and North Ridge (Culpeper); North Anna River (Hanover); Piney River (Amherst).
   - 16 county restrictions [V, Sabin].
   - BESS-heavy: 44 of 83 LBNL projects include storage, and Prince William has 12 storage projects [V].
   - Data-center overlap: Virginia has 287 planned data centers [S, Pew, cited in `expansion_markets.md`].
   - Gainers: Dominion (74 rows); Ameresco, Rockline Reliability Center, Meadow Brook Storage, Reid / Evergreen / Railroad Energy Centers [V, LBNL].
10. **Northwest Indiana.**
    - Queue: Pulaski 2.56 GW, White 2.53 GW, Jasper 1.86 GW, LaPorte 12 projects [V, LBNL].
    - Restrictions: Cass, Fulton ×2, Jasper, Kosciusko, Lake, Marshall, Pulaski, St. Joseph [V, Sabin].
    - Marshall County (Apr 2026) permanently banned data centers, advanced a 5-acre cap on solar (first reading, second vote two weeks later) and set a quarter-mile BESS setback [S, [WNDU](https://www.wndu.com/2026/04/20/marshall-county-commissioners-ban-data-centers-limit-solar-projects/)].
    - Starke County extended its commercial-solar moratorium on Feb 17, 2026 through Jul 25, 2026, citing a zoning "defect" [V, [county notice](https://starke.in.gov/wp-content/uploads/2026/02/NOTICE-OF-ADOPTION-OF-ORD-2026-02.pdf)].
    - Mammoth Solar (Pulaski/Starke) is in Sabin with unknown status [V].
    - Gainers: NIPSCO (44 rows, also a developer); RWE, Dumont Solar, Amberjack Solar, Black Prairie Solar/Storage, Starke Central Project LLC [V, LBNL].
11. **Northwest Ohio.**
    - 12 county restrictions (Allen, Auglaize, Crawford ×2, Erie, Hancock, Henry, Ottawa, Putnam, Richland, Seneca, Wyandot) [V, Sabin].
    - 6 cancellations [V, Sabin]: Birch 300 MW, the first OPSB solar denial (Allen/Auglaize); Cepheus (Defiance); Honey Creek Wind, killed by a Crawford County SB 52 resolution; One Energy (Hancock); Republic and Seneca Wind.
    - The Richland County ban was upheld at a May 5, 2026 referendum by about 1,300 votes [S, [Ohio Citizen Action](https://ohiocitizen.org/?p=312)].
    - Queue: PJM XML has 106 requests / 10.1 GW; Van Wert has 14 requests [V].
12. **Central and southern Illinois.**
    - Largest LBNL pipeline among the ranked areas outside the West and Texas: 158 projects / 29.3 GW. McLean 3.26 GW, Christian 2.59 GW, Peoria 2.15 GW, Tazewell 2.14 GW, Perry 1.85 GW [V].
    - 11 county restrictions (Christian, Moultrie ×2, Piatt, Sangamon, Tazewell, Vermilion, Woodford and others) [V, Sabin].
    - Washington County held a multi-night hearing (May 28 and June 2, 2026) on the Gatehouse Energy BESS special-use permit near Radom [S, [minutes](https://washingtonco.illinois.gov/wp-content/uploads/5_28_26-Minutes-GatehouseEnergy.pdf)].
    - Utilities: Ameren Illinois (97 rows) and ATXI (25) [V, LBNL].
13. **Northeast Pennsylvania.**
    - 6 cancellations [V, Sabin]: Electric City and Greenfield Twp (Lackawanna); Iberdrola Wind (Carbon); Susquehanna Solar's Lehman Twp (Pike) and Nanticoke (Luzerne); TotalEnergies' Palmyra Twp (Wayne).
    - 113 live PJM requests, but small sizes (3.1 GW) [V]. Many are distribution-scale: EIA-860M lists 5 planned small units each in Snyder and Columbia and 3 in Northumberland [V].
    - Carbon County examples [S, search summaries of Times News items]:
      - Towamensing Twp ZHB denied a commercial solar farm.
      - Penn Forest Twp faced an exclusionary-ordinance challenge, heard in June 2026.
      - Franklin Twp supervisors declared their 1972 zoning ordinance defective after a solar developer's curative challenge.
    - Utility: PPL (33 rows) [V].
14. **Northern Illinois.**
    - Queue: Lee 2.49 GW (LBNL); Kankakee 1.92 GW, Iroquois 1.78 GW, Livingston 1.71 GW, McHenry 1.57 GW [V].
    - PJM XML lists 182 requests / 23.1 GW (incremental MW) [V].
    - 5 cancellations [V, Sabin]: Bundleflower and Pleasant Ridge Wind (Livingston); Indigo (Winnebago); New Lenox Twp and Will County Solar (Will).
    - Iroquois ZBA took testimony on a Martinton solar permit on May 12, 2026 [S, [transcript](https://iroquoiscountyil.gov/wp-content/uploads/2026/05/Solar-Iroquois-Co.-CF-IL-Solar-N-2200-E.-Road-Martinton-LLC-5.12.2026-1.pdf)].
    - Gainers: ComEd (95 rows); Steward Creek Solar (6), Deriva Energy (4), Aurora Solar (3), Plano Skies, Blackstone Wind, Monarch Grid [V, LBNL].
15. **Colorado plains.**
    - Queue: Pueblo 27 projects / 4.25 GW, Kit Carson 3.87 GW, Weld 3.63 GW, Lincoln 3.15 GW, Morgan 2.61 GW [V, LBNL].
    - EIA small units: Weld 7 [V].
    - 8 county restrictions (Kiowa, Kit Carson, Larimer, Morgan, Phillips, Prowers, Weld ×2) [V, Sabin].
    - Canceled: Ivenergy and Pronghorn (Pueblo). Pending: Sundance Solar + Storage (Elbert) [V, Sabin].
    - Utilities: PSCo/Xcel (73 rows), Tri-State (41) [V, LBNL].
16. **Middle and south Georgia.**
    - Queue: Sumter 1.41 GW, Laurens 1.31 GW, Jefferson 1.28 GW, Hancock 1.22 GW (mostly storage), McDuffie 1.00 GW [V, LBNL]. Utilities: Southern Co / Georgia Power (48 rows) and Georgia Transmission (34) [V].
    - 10 county restrictions (Baldwin, Bulloch, Crisp, Dooly, Dougherty, Greene, Heard, Oglethorpe, Thomas, Toombs) [V, Sabin].
    - Moratorium activity:
      - Bacon County extended a solar moratorium on Jan 20, 2026 [S, AI summary, [Citizen Portal](https://citizenportal.ai/articles/7658022/Georgia/Bacon-County/Bacon-County-commissioners-extend-solar-moratorium-for-30-days)].
      - Dade County set a 90-day solar moratorium in late 2025 [S, [county doc](https://www.dadecounty-ga.gov/DocumentCenter/View/2937)].
      - Hart County voted 5–0 for a 180-day extension in 2025 [S, [Citizen Portal](https://cpo.soar.com/articles/6177246/Hart-County/Georgia/Hart-County-commissioners-extend-solar-moratorium-180-days)].
    - Competitor note: OrdinanceWatch already covers 13 Georgia counties and 40 municipalities (`expansion_markets.md` §4.4).
17. **South-central Pennsylvania.**
    - 21 in-effect restrictions, the most of any PA cluster: Berks, Chester, Dauphin, Perry and Mifflin townships [V, Sabin].
    - Canceled: Brookfield and Brookview (Lancaster). Pending: Dover Solar I (York), Lebanon Solar [V, Sabin].
    - Commonwealth Court (Jan 15, 2026) affirmed West Lampeter Twp's (Lancaster) denial of an agrivoltaic project as not "agriculture" [S, [Leagle](https://www.leagle.com/decision/inpaco20260115765)].
    - Reading Twp (Adams) set an Oct 19, 2026 hearing to strip its decommissioning rules because of Act 44 [S, [notice](https://reading.adamscountypa.gov/getmedia/02e4b711-4d88-4fe0-82a2-67bca42bb566/Public-Notice-ZO-Decom.doc)].
    - Queue is small in GW (74 PJM requests / 2.4 GW), but this is prime-farmland conflict country. Adams has 19 requests [V, PJM].
18. **Southwest Indiana.**
    - Sullivan is Indiana's top LBNL county (16 projects / 3.56 GW); then Vermillion, Vigo, Knox, Greene, Fountain [V].
    - Dubois County's solar moratorium is reported to expire Dec 2026, with Duff Solar Park Phase 2 and Shamrock Solar pending [S, letter to the editor, [Dubois County Free Press](https://duboiscountyfreepress.com/letter-dubois-county-commissioners-must-act-before-solar-moratorium-expires/)].
    - Contested: Crossvine (Dubois), Gibson Solar, Grandview (Spencer) pending; Cold Spring (Putnam) canceled [V, Sabin].
    - Utilities: Duke Energy Indiana (36 rows), Hoosier Energy, CenterPoint/Vectren [V, LBNL].
19. **Southeast Nebraska.**
    - 18 in-effect restrictions [V, Sabin]: Gage ×2, Otoe ×2, Saline, Jefferson, Thayer, Cuming, Dodge, Colfax, Burt and 6 Butler County townships (Franklin, Linwood, Oak Creek, Richardson, Savanah, Skull Creek).
    - Queue: Lancaster 14 projects / 2.04 GW, Burt 1.12 GW [V, LBNL].
20. **Central and North Texas.**
    - The largest raw pipeline in the ranking: 245 ERCOT projects / 45.7 GW in Sep 2026. Milam 7.2 GW, Navarro, Lamar, Ellis, Robertson, Hill [V, ERCOT GIS and LBNL].
    - Local leverage is weak. Sabin lists only city-level restrictions (Burleson, Grand Prairie, Midlothian, Ovilla, Nolanville) [V].
    - The 2025 legislature passed HB 3809 ("Relating to the removal of battery energy storage facilities"), effective 9/1/25 [V, [TLO](https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=HB3809)]. This is a decommissioning rule, not local zoning power.
    - The Hill Country BESS fight (Gillespie, Kendall) is the clearest county-court activity; see Q4. It sits outside this cluster's county list (TX-hill-country ranked 43rd on the composite) but is a live alert topic.
    - Gainers: Tempus Power (9 rows), Kickstart Infrastructure (6), RWE, Galaxy Solar, Enel Roseland [V, LBNL].
21. **Central Maine.**
    - 25 in-effect town restrictions [V, Sabin]: Augusta, Brewer, Albion, Athens, Belgrade, Dixmont ×2, Freedom, Glenburn, Greene, Moscow ×2, Palermo, Rome, Smithfield, Turner, Unity and others.
    - 12 contested projects, including the Aroostook Renewable Gateway transmission line (Kennebec/Waldo) [V, Sabin].
    - Pipeline is tiny: 12 LBNL projects / 0.8 GW. Net energy billing closed to new non-rooftop projects under LD 1777 [V in prior notes, see `state_agenda_laws.md`].
    - This is a town-meeting market that fits the 351 Watch format, but on volume it is a Northeast "beyond MA/NY/RI" pick, not a national top-10.
22. **Central Oregon.**
    - Queue: Sherman 17.5 GW, Crook 10.0 GW, Deschutes 9.5 GW, Wasco 8.4 GW, Klamath 7.2 GW, Morrow 6.2 GW (LBNL, 205 projects / 78.7 GW) [V].
    - Only 1 Sabin restriction, and 7 contested projects [V].
    - Placed last because how much of this pipeline counties decide versus the state's Energy Facility Siting Council could not be verified [K]. A candidate to swap with Eastern New Mexico (69 projects / 12.9 GW; 3 canceled Chaves County community-solar projects) [V, LBNL/Sabin].

**Near misses (ranked 23rd–44th on the composite)** [V numbers, E rank]:
- Southwest PA (Allegheny has 8 township restrictions; Washington and Westmoreland have 3 pending projects).
- Wisconsin central/south (Marathon County towns have 9 restrictions, but the PSC takes 100 MW+).
- Minnesota metro ring (the PUC takes solar 50 MW+, wind 5 MW+ and storage 10 MW+).
- Eastern NC (8 county restrictions; Duke and Dominion territory).
- Eastern NM, the SC Pee Dee, west NJ (Warren has 26 PJM requests; Sabin lists 0 NJ local restrictions).
- Iowa (state certificate at 25 MW+).
- Kentucky (state Siting Board above 10 MW).
- The Texas Gulf Coast BESS belt (Brazoria has 44 storage projects in LBNL and 34 in the ERCOT GIS, but counties have no zoning power).
- Maryland and Delaware (both moved authority to the state; see Q3).
- California (Kern 27 GW, Fresno 22.6 GW) is excluded because Hamlet is based there (`expansion_markets.md`).

### Inferences
- **Two product shapes** [E]:
  - **Township-grain markets** (MI, OH, PA, plus ME towns) have hundreds of bodies per cluster (MI-south 493, OH-central 442, PA-central 553, PA-northeast 617) and are where county-level national tools fit worst. They are the closest analog to the 351 Watch Massachusetts model.
  - **County-grain markets** (VA, IN, KS, IL, GA, AZ, CO) have 70–340 bodies per cluster, larger projects and higher stakes per hearing, but national county tools (Heatmap Pro, Learnewable, Paces) already fit them.
- **A multi-region launch set balancing both shapes** [E]: southern Michigan + the Thumb, central + northwest Ohio, central PA, Southside + Piedmont VA, east-central + northwest Indiana, Arizona's Maricopa/Pinal, and the Colorado plains.
- **2026–2028 decision timing:** LBNL proposed online years cluster in 2025–2028 in most ranked areas. Example: VA-Southside has 29 projects proposing 2025, 20 proposing 2024 and 19 proposing 2026; MI-south 29 in 2025 and 24 in 2028 [V, LBNL]. Many of those projects still need a local permit or a renewal in 2026–2028 [E].

### Gaps
- No MISO queue file (Cloudflare 403). Live counts for MISO counties (most of IN, IL-south, MI, MN, WI, IA, LA, AR) rely on LBNL end-2025 data.
- LBNL and PJM figures differ, sometimes by 2–3x in GW, because the PJM XML includes capacity-increase requests, E&P and suspended statuses, and 2026 changes. Both are shown; neither should be quoted alone without its date.
- Sabin counts are cumulative back to 2004, are wind-heavy, and under-catalog PA townships and BESS-only moratoria. Carina's March 2026 count was 150+ BESS moratoria, 65% in New York (secondary, from prior notes).
- No sourced lease-rate figures for landowners per area. I found no reliable per-county source in this session.
- Community-solar program pipelines by county (Illinois Shines, MD, NJ, NM, CO, MN, ME) were not obtained. Searches ran out, and EIA-860M captures few small units: IL 117, NY 96, PA 43, CO 20, MN 14, ME 10, NJ 10, NM 7, MD 7 units of 20 MW or less [V].

---

## Where are queued solar, BESS and wind projects concentrated by county?

### Takeaway
By raw volume, Texas, Arizona, Oregon and California counties dominate. But where local bodies actually decide, the densest concentrations are:
- **PJM:** Southside Virginia; northern and central Illinois; central Ohio's Madison/Union/Logan; Indiana's Pulaski/White/Randolph.
- **MISO:** Michigan's Huron/Sanilac/Calhoun/Monroe/Lenawee.
- **West:** Arizona's Maricopa/Pinal and Colorado's Pueblo/Weld/Kit Carson.

### Cited Findings
- **LBNL end-2025, active solar + storage + onshore wind, state totals** [V, my tabulation of the [LBNL file](https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx)]:
  - TX 1,786 projects / 384.5 GW; CA 432 / 168.3 GW; OR 248 / 87.5 GW; AZ 187 / 82.3 GW; IL 405 / 71.0 GW; WA 169 / 50.9 GW; MI 273 / 46.0 GW; NV 121 / 44.8 GW; IN 264 / 43.6 GW.
  - CO 169 / 34.5 GW; AR 151 / 33.3 GW; KS 129 / 28.2 GW; UT 115 / 27.3 GW; MN 134 / 26.3 GW; NM 134 / 25.8 GW; VA 261 / 23.6 GW; GA 126 / 22.2 GW; LA 118 / 21.3 GW; NY 182 / 21.3 GW.
  - OH 144 / 14.8 GW; PA 195 / 10.1 GW; NJ 55 / 4.4 GW; ME 16 / 1.0 GW.
- **Top LBNL counties in locally sited states** [V, same file]:
  - IN: Sullivan 3.56 GW, Pulaski 2.56, White 2.53, Jasper 1.86.
  - IL: McLean 3.26, Christian 2.59, Lee 2.49, Peoria 2.15, Tazewell 2.14.
  - MI: Huron 3.85, Sanilac 2.36, Calhoun 2.08, Saginaw 2.05, Monroe 1.99.
  - OH: Madison 1.65, Clermont 1.07.
  - PA: Clearfield 1.75, McKean 0.95, Cambria 0.83.
  - VA: Sussex 1.83, Brunswick 1.56, Pittsylvania 1.28, Halifax 1.12.
  - GA: Sumter 1.41, Laurens 1.31, Jefferson 1.28.
  - AZ: Maricopa 22.05, La Paz 14.22, Navajo 10.32.
  - CO: Pueblo 4.25, Kit Carson 3.87, Weld 3.63.
  - NM: Bernalillo 4.43, Lea 3.79, Roosevelt 3.02.
  - KS: Finney 2.28, Hodgeman 1.80, Ford 1.55, Linn 1.41, Sedgwick 1.40.
- **PJM live queue, Oct 2026: request counts by county** [V, my tabulation of [PJM XML](https://www.pjm.com/pub/planning/downloads/xml/PlanningQueues.xml); first-pass counts that include facility totals]:
  - VA: Mecklenburg 27, Halifax 23, Greensville 22, Caroline 22, Brunswick 21, Pittsylvania 20.
  - PA: Crawford 26, Clearfield 24, Centre 24, Somerset 24, Mercer 24, Erie 20, Adams 19.
  - OH: Madison 22, Union 20, Hardin 20, Champaign 18.
  - IN: Randolph 20, White 19, Jay 18, Pulaski 15.
  - IL: Lee 30, McLean 18, DeKalb 18, Kankakee 17, McHenry 16.
  - NJ: Warren 26, Gloucester 19.
  - State totals (first pass): VA 622 requests, PA 525, OH 420, IL 264, IN 249, KY 140, NJ 131, MD 112, WV 104, NC 65, MI 30, DE 25.
- **ERCOT GIS Sep 2026** [V, my tabulation of [GIS_Report_September2026](https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1281327706)]:
  - Totals: 1,614 large solar/wind/BESS projects; 149.6 GW solar, 157.0 GW BESS, 48.4 GW wind.
  - Top counties: Pecos 49 projects / 15.5 GW; Brazoria 50 / 10.6 GW (34 BESS); Wharton 37 / 7.2 GW; Mitchell 6.8 GW; Zapata 6.3 GW; Harris 6.3 GW (26 BESS); Milam 6.2 GW.
  - BESS counts: Brazoria 34, Harris 26, Hidalgo 19, Bexar 19, Wharton 18, Cameron 17, Robertson 16.
- **SPP active queue (updated 10/9/2026), non-operational solar/storage/wind MW** [V, my tabulation of [SPP CSV](https://opsportal.spp.org/Studies/GenerateActiveCSV)]:
  - By state: OK 28.4 GW, KS 23.0 GW, TX 13.8 GW, CO 11.4 GW, NE 7.7 GW, MO 6.0 GW, NM 5.4 GW.
  - Top counties: Roosevelt NM 2.15 GW, Texas County OK 2.10 GW, Kit Carson CO 1.6 GW, Weld CO 1.5 GW, Lancaster NE 1.5 GW, Sedgwick KS 1.0 GW.
- **CAISO active grid-queue sheet** [V, [CAISO report](http://www.caiso.com/PublishedDocuments/PublicQueueReport.xlsx)]: 254 solar/storage/wind projects / 73.2 GW; Kern 11.1 GW, Los Angeles 6.9 GW, Riverside 5.5 GW, Fresno 4.9 GW, Clark NV 4.7 GW, La Paz AZ 4.6 GW.
- **NYISO** (already a 351 Watch state) [V, [NYISO file](https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx)]: 180 solar/ES/wind projects excluding offshore wind / 23.6 GW; Suffolk 20 projects, Dutchess 1.3 GW, Ulster 10 projects.
- **EIA-860M (Aug 2026), planned units of 20 MW or less** (community-scale proxy) [V, [EIA file](https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx)]:
  - IL: Cook 14, DuPage 10, Will 5, McHenry 5, Kankakee 4.
  - PA: Clearfield 6, Armstrong 6, Snyder 5, Columbia 5.
  - CO: Weld 7.
  - ME: Androscoggin 3.

### Inferences
- Storage now dominates new requests where cities and BESS meet: Harris and Brazoria TX, Maricopa AZ (55 of 58 projects include storage), Prince William VA (12 of 12). Those are the places BESS hearings and moratoria will be most frequent in 2026–2028 [E].
- PA, OH-NW and NJ have many requests but small sizes. The opportunity there is many small township hearings, not GW [E].

### Gaps
- No live MISO data. Community-solar pipelines are missing (see above). Georgia Power and Duke queue rows arrive only through LBNL (end-2025).

---

## Where are local moratoria, bans and restrictive ordinances concentrated?

### Takeaway
- **Sabin's county-level map** concentrates in:
  - Michigan townships: Monroe 10, Livingston 7, Montcalm 7, then Tuscola, Bay and Sanilac.
  - Pennsylvania: Allegheny, Berks and Chester townships.
  - Upstate New York; Maine towns.
  - Whole-county restrictions in Ohio (32), Indiana (36), Iowa (52), Nebraska (46), Virginia (39), Minnesota (38) and Kansas (23).
- **The 2026 wave is different.** It consists of combined solar + BESS + data-center moratoria by rural counties in Kansas, Iowa and Indiana, and township BESS moratoria in Michigan and New York.

### Cited Findings
- **Sabin 6th-edition database:** 866 local restrictions (801 in effect), 23 state, 569 contested projects [V, my parse of [oppositionreport.org](https://oppositionreport.org/reports/current/)].
  - Top counties by local restrictions: MI Monroe 10, WI Marathon 9, PA Allegheny 8, MI Livingston 7, MI Montcalm 7, PA Berks 7, PA Chester 7, NE Butler 6, NY Lewis 6, ME Penobscot 6 [V].
- **Whole-county restrictions by state** [V, Sabin]:
  - OH: 31 counties plus Portage (expired), e.g., Adams, Allen, Auglaize, Brown, Butler, Clark, Clermont, Crawford ×2, Fairfield, Fayette, Greene, Hancock, Licking, Logan, Madison, Marion, Medina, Putnam, Richland, Seneca, Union, Wayne, Wyandot.
  - IN: 36, e.g., Allen, Blackford, Boone, Cass, Delaware, Fulton ×2, Hamilton ×2, Huntington, Jasper, LaGrange, Madison ×2, Marshall, Posey, Pulaski, Rush, St. Joseph, Tippecanoe, Tipton, Vermillion, Wells, Whitley.
  - VA: 39, e.g., Augusta, Brunswick, Culpeper, Fauquier, Greensville, Halifax, Henry, Isle of Wight, Louisa, Mecklenburg, Pittsylvania, Southampton.
  - KS: 23. IL: 21, including Iroquois ×2, Kankakee, Kendall, McHenry. GA: 16. NC: 24. CO: 17. AZ: 5. NM and NJ: 0.
- **Contested projects:** NY 52, VA 40 (27 canceled), MI 33, OH 31 (15 canceled), IN 25 (14 canceled), IL 20, PA 19 (9 canceled), TX 15 [V, Sabin].
- **Trend:** 22 projects totaling nearly 9.8 GW were canceled in 2025, a record. New restrictions were at least 70 in 2025, versus 112 in 2024 and 165 in 2023. Contested projects with BESS: 41 [S, [pv magazine, Sep 8, 2026](https://pv-magazine-usa.com/2026/09/08/the-u-s-saw-a-14-percent-increase-in-contested-renewable-projects-9-8-gw-in-cancellations-in-2025/); [Sabin blog, Sep 3, 2026](https://blogs.law.columbia.edu/climatechange/2026/09/03/widespread-local-opposition-often-driven-by-misinformation-continues-to-hamper-renewable-energy-development/)].
- **Ohio SB 52 count (conflicting definitions):**
  - "30 of 88 counties" with SB 52 bans [S, pv magazine summarizing Sabin, data end-2025].
  - "As of May 2026, 38 counties have passed a resolution creating a solar exclusion zone in at least 1 township" [S, advocacy, [Ohio Citizen Action](https://ohiocitizen.org/?p=312)].
  - 37 as of Sept 2025 [S, [OEC](https://theoec.org/campaign/ohio-utility-scale-solar-trends-2025/)].
- **Combined restrictions:** 21 counties restrict solar + batteries + data centers at once, and 10 more restrict data centers plus one of the two. These are "overwhelmingly in the rural Midwest and Great Plains"; KS, IA and IN hold most; most passed in 2026; more than 530 data-center restrictions exist nationally [S, [Heatmap, Aug 24, 2026](https://heatmap.news/daily/data-centers-solar-batteries)].
- **Indiana 2026 county actions:**
  - Dearborn: moratorium on solar, BESS and data-center rezonings, up to 1 year, effective Feb 25, 2026; a 1,700-signature petition preceded it [S, [WVXU](https://www.wvxu.org/environment/2026-02-25/dearborn-county-moratorium-solar-farms-data-center)].
  - Starke: extension through Jul 25, 2026 [V, county notice].
  - Marshall: data-center ban and solar cap [S, WNDU].
  - Dubois: moratorium to Dec 2026 [S, letter].
- **BESS moratoria:** 150+ local governments in 17 states; NY has 98 (65%); IN, MI, IA and ME are "rising" [S, commercial source, [Carina via GlobeNewswire, Mar 10, 2026](https://www.globenewswire.com/news-release/2026/03/10/3252888/0/en/150-Local-Governments-Have-Moved-to-Block-Battery-Storage-Development-New-Database-Reveals.html)].
- **Texas county BESS resistance:**
  - Gillespie County: resolution opposing all BESS (Feb 24, 2025); stop-work orders on the 145 MW Rogers Draw BESS (Harper) on Dec 10–11, 2025; agreed temporary injunction Jan 21, 2026; a second suit against AMPYR's 1,000-acre Marshall Springs solar + BESS [V, [county BESS page](https://gillespiecounty.gov/1372/Gillespie-County-BESS-Information)].
  - Kendall County: asked TCEQ to "deny all permits" for BESS (Oct 2024; older) [S, [Boerne Star](https://www.boernestar.com/article/9257,county-makes-move-to-help-in-fight-against-battery-storage-systems)].

### Inferences
- New flat-county restrictions are slowing (Sabin's count of new restrictions is falling). The 2026 growth is multi-technology moratoria and BESS-specific pauses. Neither is well captured by Sabin's wind/solar-centric categories, so agenda monitoring finds them earlier than any annual database [E].

### Gaps
- No county-level Heatmap list (paywalled). No 2026 statewide count of Indiana or Michigan moratoria. No Texas statewide county-resolution count.

---

## Which 2024–2026 state laws moved decisions toward or away from local governments, and which areas are newly hot or cold?

### Takeaway
- **Newly hot (local still decides, and fights are rising):** Indiana (no new preemption found), Kansas, Ohio (SB 52 is intact and the county count keeps rising), Pennsylvania (HB 502 stalled), and Michigan (PA 233 makes the township's moratorium or CREO vote decisive).
- **Cooled for local veto power:**
  - Illinois: statewide standards for wind/solar plus new 2026 standards for storage, and courts now order permits issued.
  - Virginia: 2026 HB 711 statewide solar criteria; SB 443 makes co-located storage a permitted accessory use.
  - Maryland: RECA 2025. Delaware: SB 159 (2025). Minnesota: 2024 permitting act.
  - Pennsylvania's decommissioning rules only (Act 44, from Jan 2027).

### Cited Findings
- **Pennsylvania:**
  - HB 502 (RESET Board, which would preempt local land use for 25 MW+ generation and 10 MW/4h+ storage) is still "Referred to Energy, April 23, 2025," with no committee report or votes; page generated 10/11/2026 [V, [palegis HB 502](https://www.palegis.us/legislation/bills/2025/hb502)].
  - Community-solar HB 1155 is still in committee (referred Apr 7, 2025) [V, [palegis HB 1155](https://www.palegis.us/legislation/bills/2025/hb1155)].
  - Act 44 of 2026 (SB 349), signed Jul 20, 2026, preempts and invalidates municipal solar decommissioning provisions for facilities over 2 MW from January 2027. PSATS opposed it [S, [PSATS](https://www.psats.org/governor-signs-act-that-will-invalidate-municipal-solar-decommissioning-ordinances/)].
- **Michigan:**
  - PA 233 is in force. The Court of Appeals (May 2026) largely upheld the MPSC's narrow CREO definition.
  - 79 townships and counties filed for Supreme Court leave on Jun 18, 2026, with 43 more supporting [S, [Foster Swift](https://www.fosterswift.com/newsroom/news/michigan-supreme-court-zoning-control-renewable-energy-pa233-mpsc-appeal); [Sabin blog, Jul 14, 2026](https://blogs.law.columbia.edu/climatechange/2026/07/14/michigan-court-of-appeals-decision-largely-upholds-michigan-pscs-renewable-energy-siting-process/)].
  - A local unit with a moratorium on energy facilities is treated as having no CREO, so the developer may file with the MPSC [S, search summary of the [Court of Appeals opinion](https://www.michbar.org/Portals/0/opinions/appeals/2026/050726/85698.pdf) and the [Fort Gratiot PA 233 outline](https://fortgratiot.us/wp-content/uploads/2024/10/Outline-Public-Act-233-of-2023.pdf)].
- **Illinois:**
  - *Equity Solar Illinois v. County of Grundy*, 2026 IL App (3d) 250289: counties must issue special-use permits to solar facilities that meet state standards. A writ of mandamus ordered approval [S, [ISACo, Mar 16, 2026](https://www.isacoil.org/News/30112/Illinois-Appellate-Court-Affirms-Limitations-of-County-Authority-Over-Solar-Projects/news-detail/)].
  - PA 104-0458 (signed Jan 8, 2026, effective Jun 1, 2026) adds statewide county standards for storage over 1 MW [S, Taft, cited in `state_agenda_laws.md`].
- **Virginia (2026 session, signed per B&D):**
  - HB 711: statewide siting criteria for certain utility-scale solar; "eliminates inconsistent local requirements"; new reporting on local decisions.
  - SB 443: certain BESS on parcels with approved solar special exceptions become permitted accessory uses "without requiring a separate local land-use approval."
  - SB 94: site assessment for high-energy-use facilities (data centers) before local approvals.
  - Source: [S, [Beveridge & Diamond, May 1, 2026](https://www.bdlaw.com/publications/environmental-highlights-from-virginias-2026-legislative-session/)]. Bill text and effective dates were not verified on LIS.
- **Ohio:** SB 52 is unchanged. HB 303 (community energy) passed the House and was pending in the Senate in spring 2026 [S, OEC]. Richland voters upheld the county ban on May 5, 2026; Portage residents blocked a proposed ban in April 2026 [S, Ohio Citizen Action].
- **Texas:** HB 3809 (BESS removal) is effective 9/1/25 [V, TLO]. Gillespie County backs bills to give counties BESS regulatory power and require PUC BESS permits; their outcome was not verified [V, county page].
- **Indiana:** a 2026 bill to set statewide zoning standards and override stricter local rules was reported moving in Feb 2026, but its number and outcome are unverified [S, [RTO Insider](https://www.rtoinsider.com/?p=20628), search summary]. SB 54 (solar overlay limits) is unverified [S].
- **Elsewhere:** Delaware SB 159 (2025) and Minnesota's Energy Infrastructure Permitting Act (2024) allow state override of local restrictions. Maryland RECA (2025), Arkansas's Wind Energy Development Act (2025) and Louisiana HB 459 (2025) added state-level restrictions [S, pv magazine summarizing Sabin].

### Inferences
- **Hottest for a local-agenda product:** MI townships (the moratorium vote decides the forum), OH counties and townships, IN counties, PA townships, KS counties [E].
- **Cooling in kind, not volume:** IL and VA hearings still happen and set conditions, but a denial is harder to sustain. The alert value shifts from "will it be blocked" to "what conditions, and when" [E].

### Gaps
- The text and status of Indiana's 2026 bill, Virginia HB 711 effective dates, and Texas county-BESS bill outcomes were not verified (search budget exhausted).

---

## In which areas is a single missed hearing most costly, and what is the evidence?

### Takeaway
A single missed hearing costs most where one vote can end or move a whole class of projects with little notice:
- **Ohio:** an SB 52 county resolution or township ban.
- **Michigan:** a township moratorium, which switches the forum to the MPSC.
- **Indiana:** a county moratorium that takes effect the next day.
- **Virginia:** county acreage caps and use removals that create first-come races.
- **Kansas:** 2026 combined moratoria.
- **Texas Hill Country:** county stop-work orders and lawsuits.

### Cited Findings
- **Ohio: one county vote kills projects.**
  - Crawford County commissioners adopted an SB 52 resolution on May 5, 2022 prohibiting large wind in all unincorporated areas, and Honey Creek Wind was canceled.
  - Mahoning commissioners approved Green Township's ban in Nov 2023, and Alpin Sun Solar was canceled [V, Sabin project records].
- **Ohio: residents who show up can prevent a ban.** Portage residents blocked a proposed ban in April 2026 after a late-March hearing where "all but one speaker opposed banning" [S, Ohio Citizen Action].
- **Michigan:** a township moratorium removes CREO status and opens the MPSC route, so the moratorium vote itself decides the forum [S, see Q3]. Baroda Township's Jan 19, 2026 moratorium was passed at a regular board meeting, with one member absent [V, township PDF].
- **Indiana:** Dearborn's moratorium took effect the day after the vote [S, WVXU]. Marshall County's solar cap passed first reading, with the decisive second vote two weeks later [S, WNDU].
- **Virginia:** Mecklenburg removed utility-scale solar as a future use by unanimous vote (Apr 14, 2025). Pending projects now compete for the remaining cap: "If any two of them get approved, that's the end of it" [S, Cardinal News]. Southside has the most canceled contested projects of any area (13) [V, Sabin].
- **Kansas:** Saline's 4–0 three-year moratorium and Geary's one-year moratorium covered BESS and data centers [S, search summaries]. Heatmap notes most combined restrictions were passed in 2026 [S].
- **Texas:** Gillespie County issued stop-work orders on the Rogers Draw BESS within weeks of filing to intervene in a suit [V, county page].
- **Illinois (lower cost):** after Grundy, a missed county hearing is less likely to cost a compliant solar project its permit [S, ISACo]. BESS hearings like Washington County's Gatehouse still run over multiple nights [S].

### Inferences
- **Ranking of "missed-hearing cost"** [E]: OH and MI (forum- or class-ending votes) > IN and KS (fast moratoria) > VA (caps and first-come allocation) > PA (pending-ordinance and curative-amendment timing [K]) > IL and TX (state standards, or no zoning).
- **Who loses most from a miss:**
  - Developers with interconnection positions they must hold (the PJM and ERCOT deposits and milestones listed in the queues).
  - Landowners with signed leases.
  - Residents, who need advance notice to organize.
- **Who wins:** whichever side shows up at the first reading.

### Gaps
- No systematic measure of notice lead time before moratorium votes across states. Agenda-posting rules are in `state_agenda_laws.md`: OH, MI and MN require no agenda; IN requires 48 hours; VA and TX require 3 days or 72 hours. No dataset links specific cancellations to specific missed hearings beyond the Sabin project narratives cited above.
