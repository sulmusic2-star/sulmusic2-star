# New York wave 2: target list (2026-11-02)

81 places and 45 county planning boards, built by `python3 experiments/wave2_test.py targets` from `NY_TARGETS` in `crawler/experiments/wave2_test.py`. Sources: Carina Energy's BESS Moratorium Monitor (https://carina.energy/bess-moratoriums/, 128 New York rows read 2026-11-02; the three rows whose moratoria ended in 2024, Busti, Long Lake and Port Chester, are left out), the "Next 50 towns to add" list in ny_pilot.md (all 50 became wave 1; the ones not promoted come back here), where_it_pays_2026.md (section 2, entry 5, and section 4, recommendation 1), data_center_and_other_fights.md, and the town documents read this session. Anything already in data/towns_ny.json is skipped.

The seven Long Island towns with moratoria (Babylon, Hempstead, Huntington, Islip, North Hempstead, Oyster Bay, Smithtown; Southampton and Southold too) are already site towns, so they are not repeated; Islip, Brookhaven and Huntington are read through Suffolk County's planning commission if that reads, and are on the unblock list. Clifton Park is a site town.

## Carina monitor: BESS moratorium active, a renewal or permanent law is due (11)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| Chester (Orange) | town | BESS moratorium ACTIVE, listed end 2026-08-26: extension or law due. The pilot swapped Chester for Warwick when its guessed domain failed; the official site is chester-ny.gov (Wikipedia infobox) | https://carina.energy/bess-moratoriums/ |
| Freedom (Cattaraugus) | town | BESS moratorium ACTIVE, no end date listed | https://carina.energy/bess-moratoriums/ |
| Mina (Chautauqua) | town | BESS moratorium ACTIVE, listed end 2026-06-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Cameron (Steuben) | town | BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Gloversville (Fulton) | city | BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Oswego (Oswego) | city | BESS moratorium ACTIVE (Carina: 'Oswego City'), no end date listed | https://carina.energy/bess-moratoriums/ |
| Parishville (St. Lawrence) | town | BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Jay (Essex) | town | BESS moratorium ACTIVE, listed end 2026-06-18: extension or law due | https://carina.energy/bess-moratoriums/ |
| Southport (Chemung) | town | BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Poland (Chautauqua) | town | BESS moratorium ACTIVE, listed end 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Willing (Allegany) | town | BESS moratorium (all BESS) listed EXPIRED with end date 2027-06-01; Carina's status and date disagree | https://carina.energy/bess-moratoriums/ |

## Carina monitor: BESS moratorium under review or pending in 2026 (8)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| Athens (Greene) | town | BESS moratorium (all BESS) UNDER_REVIEW, listed date 2026-03-01 | https://carina.energy/bess-moratoriums/ |
| German Flatts (Herkimer) | town | BESS moratorium UNDER_REVIEW, listed date 2026-05-31 | https://carina.energy/bess-moratoriums/ |
| Barker (Broome) | town | BESS moratorium UNDER_REVIEW, listed date 2026-04-22 | https://carina.energy/bess-moratoriums/ |
| Victory (Cayuga) | town | BESS moratorium UNDER_REVIEW, listed date 2026-03-13 | https://carina.energy/bess-moratoriums/ |
| Fort Ann (Washington) | town | BESS moratorium PENDING, listed date 2026-02-21 | https://carina.energy/bess-moratoriums/ |
| Florence (Oneida) | town | BESS moratorium UNDER_REVIEW, listed date 2026-05-01 | https://carina.energy/bess-moratoriums/ |
| Salem (Washington) | town | BESS moratorium UNDER_REVIEW, listed date 2026-04-28 | https://carina.energy/bess-moratoriums/ |
| Naples (Ontario) | town | BESS moratorium UNDER_REVIEW, listed date 2026-02-28 | https://carina.energy/bess-moratoriums/ |

## Carina monitor: BESS moratorium lifted or expired since mid-2025 (a law followed) (19)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| Albion (Orleans) | town | BESS moratorium LIFTED: law adopted, applications next (Carina lists 'Albion'; taken as the town) | https://carina.energy/bess-moratoriums/ |
| Chautauqua (Chautauqua) | town | BESS moratorium EXPIRED 2025-09-03 | https://carina.energy/bess-moratoriums/ |
| Harrison (Westchester) | town | BESS moratorium EXPIRED 2025-09-06 | https://carina.energy/bess-moratoriums/ |
| Johnstown (Fulton) | town | BESS moratorium EXPIRED 2025-08-03 (Carina lists 'Johnstown'; taken as the town) | https://carina.energy/bess-moratoriums/ |
| Mamaroneck (village) (Westchester) | village | BESS moratorium LIFTED 2026-05-01 | https://carina.energy/bess-moratoriums/ |
| Mount Kisco (Westchester) | village | BESS moratorium EXPIRED 2025-06-03 | https://carina.energy/bess-moratoriums/ |
| Newstead (Erie) | town | BESS moratorium EXPIRED 2026-03-31 | https://carina.energy/bess-moratoriums/ |
| Pound Ridge (Westchester) | town | BESS moratorium (all BESS) LIFTED 2026-02-28 | https://carina.energy/bess-moratoriums/ |
| Ripley (Chautauqua) | town | BESS moratorium EXPIRED (no date listed) | https://carina.energy/bess-moratoriums/ |
| Rotterdam (Schenectady) | town | BESS moratorium EXPIRED 2025-05-03 | https://carina.energy/bess-moratoriums/ |
| Royalton (Niagara) | town | BESS moratorium LIFTED 2026-03-31 | https://carina.energy/bess-moratoriums/ |
| Walworth (Wayne) | town | BESS moratorium LIFTED 2026-05-30 | https://carina.energy/bess-moratoriums/ |
| Wilson (Niagara) | town | BESS moratorium EXPIRED 2026-03-31 | https://carina.energy/bess-moratoriums/ |
| Frankfort (Herkimer) | town | BESS moratorium LIFTED 2026-04-27 | https://carina.energy/bess-moratoriums/ |
| Le Ray (Jefferson) | town | BESS moratorium EXPIRED 2025-08-18 | https://carina.energy/bess-moratoriums/ |
| Turin (Lewis) | town | BESS moratorium EXPIRED 2025-12-06 | https://carina.energy/bess-moratoriums/ |
| Pendleton (Niagara) | town | BESS moratorium EXPIRED 2025-12-27 | https://carina.energy/bess-moratoriums/ |
| Carrollton (Cattaraugus) | town | BESS moratorium EXPIRED 2025-04-29 | https://carina.energy/bess-moratoriums/ |
| Elba (Genesee) | town | BESS moratorium LIFTED 2025-10-31 | https://carina.energy/bess-moratoriums/ |

## 2026 BESS moratoria found in town documents and news this session, not on Carina's monitor (10)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| North Elba (Essex) | town | One-year BESS moratorium approved October 2026 (WCAX, 2026-10-16) | https://www.wcax.com/2026/10/16/north-elba-approves-one-year-moratorium-battery-energy-storage-systems/ |
| Newcomb (Essex) | town | 12-month moratorium on permits for commercial and industrial BESS (news summary; adoption date to verify) | https://www.thecooldown.com/?p=750647 |
| Ticonderoga (Essex) | town | Town Board hearing 2026-05-14 on a temporary BESS moratorium (hearing notice read 2026-11-02) | https://townofticonderoga.gov/wp-content/uploads/Notice-of-Public-Hearing-1.pdf |
| St. Armand (Essex) | town | One-year BESS moratorium passed March 2026 (Environment+Energy Leader summary of Carina's release; to verify) | https://www.environmentenergyleader.com/stories/new-york-battery-storage-moratoriums-hit-98-municipalities,126655 |
| Lake George (Warren) | town | Local Law 2 of 2026 establishing a BESS moratorium (law text read 2026-11-02) | https://www.townoflakegeorge.gov/DocumentCenter/View/1246 |
| Chester (Warren County) (Warren) | town | A BESS-moratorium document on the town site matched the search; the site answers HTTP 403 to the bot, so it is unread | https://www.chesterwcny.gov/media/7606 |
| Walton (Delaware) | town | Local Law 2 of 2026: a one-year BESS moratorium; the site asks a 30 s crawl delay, over the 10 s document cap | https://townofwaltonny.gov/local-law-2-of-2026-a-local-law-establishing-a-one-1-year-moratorium-on-battery-energy-storage-systems-in-the-town-of-walton/ |
| Bergen (Genesee) | town | Local Law 3 of 2026: a nine-month BESS moratorium, hearing 2026-05-19 (legal notice read 2026-11-02) | https://www.townofbergenny.gov/documents/3-2026-legal-notice-for-moratorium-battery-storage-systems-may-2026.docx |
| Webb (Herkimer) | town | A public-hearing notice on the town site matched the BESS-moratorium search; the site answers HTTP 403 to the bot (to verify) | https://www.townofwebbny.gov/media/2131 |
| Goshen (Orange) | town | Residents and officials urged a BESS moratorium while the town studies safety and zoning (Citizen Portal summary; to verify) | https://cpo.soar.com/articles/6447040/Goshen/Orange-County/New-York/Residents-and-officials-urge-moratorium-on-battery-storage-projects-while-town-studies-safety-and-zoning |

## Capital Region cities and towns named in where_it_pays_2026.md (3)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| Troy (Rensselaer) | city | City Council six-month BESS moratorium, 2026-02-06 (Spectrum News, cited in where_it_pays_2026.md [40]) | https://spectrumlocalnews.com/nys/capital-region/news/2026/02/06/troy-council-approves-moratorium-on-battery-energy-storage-systems- |
| Moreau (Saratoga) | town | Capital Region town named in where_it_pays_2026.md; proposed Local Law 2 of 2026, a BESS moratorium (law text read 2026-11-02) | https://www.townofmoreau.org/2026-LL2-Battery-Moratorium.pdf |
| Waterford (Saratoga) | town | Capital Region town named in where_it_pays_2026.md; notice of adoption of Local Law 1 of 2026 (BESS moratorium); the notice answers HTTP 403 to the bot | https://www.townofwaterfordny.gov/town-board/files/notice-adoption-local-law-no-1-2026 |

## Data-center and warehouse fights the notes name (2)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| New Windsor (Orange) | town | Temporary moratorium on warehouses and self-storage, August 2026 (data_center_and_other_fights.md) | https://citizenportal.ai/articles/10203240/new-york/orange-county/new-windsor/new-windsor-adopts-temporary-moratorium-on-warehouses-and-self-storage-excludes-airport-zone |
| Alabama (Genesee) | town | STREAM US Data Centers' $19.5B proposal at STAMP: Planning Board site plan and SEQR findings through 2026 (ny_pilot.md next-50 #48) | https://townofalabamany.gov/2026/04/ |

## Wave-1 places not promoted (second discovery pass, then the county route) (28)

| Place (County) | Kind | Why | Source |
|---|---|---|---|
| Carlisle (Schoharie) | town | Wave 1, not promoted: no agenda page: the county-hosted town page (www4.schohariecounty-ny.gov/government/town-of-carlisle/) answers HTTP 404. Originally: BESS moratorium ACTIVE, ends 2026-10-21 | https://carina.energy/bess-moratoriums/ |
| Gainesville (Wyoming) | town | Wave 1, not promoted: no website: no town website found (web search 2026-10-12); county-hosted notices at most. Originally: BESS moratorium (all BESS) ACTIVE, ends 2026-10-20 | https://carina.energy/bess-moratoriums/ |
| Brasher (St. Lawrence) | town | Wave 1, not promoted: no agenda page: townofbrasher.gov is reachable but lists no agendas for the Town Board, Planning Board or ZBA. Originally: BESS moratorium ACTIVE, ends 2026-10-31 | https://carina.energy/bess-moratoriums/ |
| Sherman (Chautauqua) | town | Wave 1, not promoted: no agenda page: shermanny.gov carries Town Board minutes only; the Planning Board and ZBA agendas there are the Village of Sherman's. Originally: BESS moratorium ACTIVE, ends 2026-10-31 | https://carina.energy/bess-moratoriums/ |
| Schroeppel (Oswego) | town | Wave 1, not promoted: unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2. Originally: Solar-plus-storage moratorium ACTIVE, ends 2027-02-10 | https://carina.energy/bess-moratoriums/ |
| Lewis (Lewis) | town | Wave 1, not promoted: agendas undated: Town Board agendas are posted as monthly public notices named only by month ('Agenda for September 2026', a .docx), so no meeting date can be read. Originally: BESS moratorium ACTIVE, ends 2027-03-16 | https://carina.energy/bess-moratoriums/ |
| Northampton (Fulton) | town | Wave 1, not promoted: unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2. Originally: BESS moratorium (all BESS) ACTIVE, ends 2027-03-30 | https://carina.energy/bess-moratoriums/ |
| Mayville (Chautauqua) | village | Wave 1, not promoted: no agenda page: mayvilleny.gov is reachable but lists no agendas for the tracked boards. Originally: BESS moratorium ACTIVE, ends 2027-06-01 | https://carina.energy/bess-moratoriums/ |
| Benson (Hamilton) | town | Wave 1, not promoted: no website: no town website found (townofbenson.com is Benson, North Carolina; web search 2026-10-12). Originally: BESS moratorium (all BESS) ACTIVE, ends 2027-06-09 | https://carina.energy/bess-moratoriums/ |
| Collins (Erie) | town | Wave 1, not promoted: robots disallow: robots.txt on townofcollinsny.gov disallows the agenda documents. Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Virgil (Cortland) | town | Wave 1, not promoted: unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2. Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Oswegatchie (St. Lawrence) | town | Wave 1, not promoted: agendas undated: monthly Town Board agendas (2026_<month>_agenda.pdf) are posted without a day, and the latest was August 2026, before the window. Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Palatine (Montgomery) | town | Wave 1, not promoted: no agenda page: the Town Council page links a Google Drive folder; no dated agenda listing on townofpalatine.org. Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Pike (Wyoming) | town | Wave 1, not promoted: no website: no town website found (web search 2026-10-12). Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Mentz (Cayuga) | town | Wave 1, not promoted: robots disallow: robots.txt on townofmentz.com disallows AgendaAheadBot. Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Carlton (Orleans) | town | Wave 1, not promoted: no agenda page: the town posts hearing and meeting notices on its homepage only (one dated ZBA hearing notice in the window); kept in the test config for the county route. Originally: BESS moratorium ACTIVE, ends 2027-04-14 (extended) | https://carina.energy/bess-moratoriums/ |
| Allen (Allegany) | town | Wave 1, not promoted: no agenda page: the Wix site is reachable but lists no agendas for the tracked boards. Originally: BESS moratorium ACTIVE, ended 2026-09-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Westfield (Chautauqua) | town | Wave 1, not promoted: agendas undated: Town Board agendas on the year page are named only by month ('September Agenda'); no meeting date can be read. Originally: BESS moratorium ACTIVE, ended 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Root (Montgomery) | town | Wave 1, not promoted: no agenda page: the county-hosted town pages (montgomerycountyny.gov/web/municipal/root/) show board pages but no agenda dated within 120 days of the run. Originally: BESS moratorium ACTIVE, ended 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Greenwood (Steuben) | town | Wave 1, not promoted: unreachable: robots.txt answered 5xx or timed out from this sandbox on 2026-10-12 and 10-13 (RFC 9309: treated as disallow); retried in wave 2. Originally: BESS moratorium ACTIVE, ended 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| Prattsburgh (Steuben) | town | Wave 1, not promoted: no agenda page: the Town Board page lists monthly minutes only. Originally: BESS moratorium ACTIVE, ended 2026-08-31: extension or law due | https://carina.energy/bess-moratoriums/ |
| North Harmony (Chautauqua) | town | Wave 1, not promoted: no agenda page: board pages found (townofnorthharmony.gov/townboard) but no agenda dated within 120 days of the run. Originally: BESS moratorium ACTIVE, ended 2026-08-30: extension or law due | https://carina.energy/bess-moratoriums/ |
| Rose (Wayne) | town | Wave 1, not promoted: no agenda page: board pages found (roseny.gov/town-boards) but no agenda dated within 120 days of the run. Originally: BESS moratorium ACTIVE, ended 2026-07-03: extension or law due | https://carina.energy/bess-moratoriums/ |
| Stockport (Columbia) | town | Wave 1, not promoted: no agenda page: the Town Board page posts minutes; no agenda dated within 120 days of the run. Originally: BESS moratorium ACTIVE, ended 2026-06-01: extension or law due | https://carina.energy/bess-moratoriums/ |
| Yorktown (Westchester) | town | Wave 1, not promoted: bot wall: agendas are on calendar.yorktownny.gov, which answers HTTP 403 'blocked due to security reasons' to AgendaAheadBot (robots.txt too); not bypassed. Originally: BESS moratorium EXPIRED 2026-01-14: BESS law follow-up | https://carina.energy/bess-moratoriums/ |
| Montgomery (Orange) | town | Wave 1, not promoted: JavaScript only: 'Agendas, Minutes, & Videos' is a DNN document library filled by script, with no static listing to read. Originally: BESS moratorium LIFTED 2026-03-31: law adopted, applications next | https://carina.energy/bess-moratoriums/ |
| Somerset (Niagara) | town | Wave 1, not promoted: bot wall: Cloudflare-style bot challenge (HTTP 403) on www.somersetny.gov; not bypassed. Originally: BESS moratorium LIFTED 2026-03-31; former coal-plant site | https://carina.energy/bess-moratoriums/ |
| Sherburne (Chenango) | town | Wave 1, not promoted: no agenda page: the newest Town Board agenda document is from June 2024; nothing dated within 120 days of the run. Originally: January 2026 moratorium hearing tied to a Nexamp BESS proposal | https://eticaag.com/sherburne-ny-approves-battery-storage-moratorium/ |

## County planning boards, the 239-m referral route (45)

Under General Municipal Law 239-m a town, village or city must refer zoning amendments, moratoria, site plans, special permits and variances within 500 feet of a county or state road, a municipal boundary or county land to the county planning board, which has 30 days to answer. The board's agenda therefore lists the municipal action before the local hearing. Where a place's own site cannot be read, its county board is discovered and, if it reads, the place is marked coverage "via_county" the way towns_mi.json does.

| County board | Why |
|---|---|
| Essex County | County-wide BESS moratorium ACTIVE on Carina's monitor (listed date 2026-03-16); five Essex towns are wave-2 targets |
| Albany County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Berne (site town, not read)) |
| Allegany County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Allen, Willing) |
| Broome County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Barker) |
| Cattaraugus County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Carrollton, Freedom) |
| Cayuga County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Mentz, Victory) |
| Chautauqua County | County planning board: GML 239-m referrals from 8 target places we cannot read directly or have not read yet (Chautauqua, Mayville, Mina, North Harmony, Poland, Ripley, Sherman, Westfield) |
| Chemung County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Southport) |
| Chenango County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Sherburne) |
| Columbia County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Livingston (site town, not read), Stockport) |
| Cortland County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Virgil) |
| Delaware County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Walton) |
| Erie County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Boston (site town, not read), Collins, Newstead) |
| Fulton County | County planning board: GML 239-m referrals from 4 target places we cannot read directly or have not read yet (Gloversville, Johnstown, Northampton, Perth (site town, not read)) |
| Genesee County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Alabama, Bergen, Elba) |
| Greene County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Athens) |
| Hamilton County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Benson) |
| Herkimer County | County planning board: GML 239-m referrals from 4 target places we cannot read directly or have not read yet (Frankfort, German Flatts, Webb, Winfield (site town, not read)) |
| Jefferson County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Le Ray) |
| Lewis County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Lewis, Turin) |
| Livingston County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (York (site town, not read)) |
| Montgomery County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Palatine, Root) |
| Niagara County | County planning board: GML 239-m referrals from 5 target places we cannot read directly or have not read yet (Newfane (site town, not read), Pendleton, Royalton, Somerset, Wilson) |
| Oneida County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Florence) |
| Onondaga County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Camillus (site town, not read), Cicero (site town, not read), Spafford (site town, not read)) |
| Ontario County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Naples) |
| Orange County | County planning board: GML 239-m referrals from 4 target places we cannot read directly or have not read yet (Chester, Goshen, Montgomery, New Windsor) |
| Orleans County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Albion, Carlton) |
| Oswego County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Oswego, Schroeppel) |
| Putnam County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Carmel (site town, not read)) |
| Rensselaer County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Troy) |
| Saratoga County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Halfmoon (site town, not read), Moreau, Waterford) |
| Schenectady County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Duanesburg (site town, not read), Rotterdam) |
| Schoharie County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Carlisle) |
| St. Lawrence County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Brasher, Oswegatchie, Parishville) |
| Steuben County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Cameron, Greenwood, Prattsburgh) |
| Suffolk County | County planning board: GML 239-m referrals from 4 target places we cannot read directly or have not read yet (Brookhaven (site town, not read), Huntington (site town, not read), Islip (site town, not read), Southampton (site town, not read)) |
| Sullivan County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Highland (site town, not read)) |
| Tompkins County | County planning board: GML 239-m referrals from 1 target place we cannot read directly or have not read yet (Lansing (site town, not read)) |
| Ulster County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Gardiner (site town, not read), Hurley (site town, not read), Wawarsing (site town, not read)) |
| Warren County | County planning board: GML 239-m referrals from 3 target places we cannot read directly or have not read yet (Chester (Warren County), Horicon (site town, not read), Lake George) |
| Washington County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Fort Ann, Salem) |
| Wayne County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Rose, Walworth) |
| Westchester County | County planning board: GML 239-m referrals from 6 target places we cannot read directly or have not read yet (Harrison, Mamaroneck (village), Mount Kisco, New Castle (site town, not read), Pound Ridge, Yorktown) |
| Wyoming County | County planning board: GML 239-m referrals from 2 target places we cannot read directly or have not read yet (Gainesville, Pike) |

## Skipped (already covered)

