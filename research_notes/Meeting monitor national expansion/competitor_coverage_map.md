# Competitor coverage map: who monitors US local siting decisions, where, how fresh, and at what price

Checked 2026-10-11 for 351 Watch (live coverage: MA 240 towns, NY 33, RI 39). This extends `../Meeting monitor deep dive/competitor_behind_login.md`, `../Product strategy/where_we_win.md` (the competitor matrix) and §4.4 of `../Meeting monitor deep dive/expansion_markets.md` with geographic detail, and does not repeat them. No accounts were created and no bot challenge was bypassed. Hamlet (Vercel checkpoint) and Citizen Portal (Cloudflare challenge, and its terms bar competitive use) were read only through search-index quotes of their own pages. Five other pages returned HTTP 403 to the fetcher and were not retried another way: energyzoning.org, documenters.org, fiscalnote.com/products/curate, and two civiciq.com pages. The session's web-search budget ran out before the last few state checks; those are listed under Gaps.

**Labels:**
- **[V]**: verified. I read it on the product's own page this session.
- **[V-idx]**: the product's own page text, but as quoted by the search index. I did not load the page.
- **[S]**: secondary. A third-party article, aggregator or search summary.
- **[E]**: estimate or my arithmetic.
- **[K]**: background knowledge, not checked this session.

A note on the brief: the Hamlet OpenAPI file is not at `research_notes/hamlet_openapi_2026-10-10.json`. It is at `research_notes/Meeting monitor deep dive/proof/hamlet_openapi_2026-10-10.json`, a copy of https://api.myhamlet.com/openapi.json.

---

## 1. Which places does each product cover, how many jurisdictions does it claim, and does it reach rural townships and counties or mostly cities?

### Takeaway
National claims range from about 550 cities (CivicSearch) to "100,000+ agencies" (Civic IQ). Only **Hamlet publishes a per-state breakdown**, and that breakdown shows where the holes are:
- Hamlet lists **30–60% of local governments in CA, FL, AZ, NV and RI** [E].
- It lists **under 5% in the township states (PA, OH, MI, WI, MN)**, and also in IL, IA, NE, NY, ME and VT [E].
- Its data model has **no TOWN or TOWNSHIP location type** [V].

The products that do reach rural townships and counties fall into two groups:
- **Post-meeting:** Citizen Portal, which writes recaps from video, and GatherGov.
- **County-grain siting tools:** Heatmap Pro, Spark, SitePath, Learnewable, Transect. None of them publishes a list of the townships or towns it covers.

### Cited Findings

**A. Product coverage table (geography, claimed count, finest level, rural reach)**

| Product | Geography and count claimed | Finest level | Rural/township reach (evidence) | Label · Source |
|---|---|---|---|---|
| **Hamlet** | Coverage page: "101,207+" transcripts across **2,011 cities and 453 counties**, "50+ states". Homepage: "6,600+ governing bodies", 94,000+ transcripts. Feb 2026 press: "3,000+" bodies. Each state row shows "Recent: Oct 6, 2026 / Upcoming: Oct 7–8, 2026" | City or county. The API's `Location.type` enum is only CITY, COUNTY, STATE. Body types are CITY_COUNCIL, PLANNING_COMMISSION, OTHER, BOARD_OF_SUPERVISORS, SCHOOL_BOARD | Small TX cities have pages (Glen Rose P&Z, Henderson). There is no township location type. Per-state shares are in table B | V-idx · [coverage](https://www.myhamlet.com/coverage), [home](https://www.myhamlet.com/), [Glen Rose P&Z](https://www.myhamlet.com/glen-rose-tx/planning-and-zoning-commission--1891); V · [API spec](https://api.myhamlet.com/openapi.json); S · [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/) |
| **Citizen Portal** (citizenportal.ai, also cp.soar.com) | No jurisdiction count found. The homepage lists per-state article counts, e.g. California 118,883 and Arizona 42,980; the unit is unclear. "600–700,000 hours" or "1.3 million hours" of meetings, depending on the profile | Individual body: township trustees, county commission, planning board | **The broadest rural reach seen.** OH township trustees (Williams Co.); PA Warriors Mark Twp solar conditional-use hearing; PA Cameron Co.; KS Butler Co.; NE Keith Co.; IA Des Moines Co.; OH Washington Co.; TX Dimmit, Kerr and Harrison Cos.; GA Coweta Co.; MI St. Clair Co. (sources in part C) | S · [cp.soar.com home (search summary)](https://cp.soar.com/), [Superpowers4Good](https://www.superpowers4good.com/p/citizen-portal-revolutionizes-civic) |
| **GatherGov** | "**9300+ jurisdictions including towns and counties**. We are live in over 94% of the US population." Elsewhere: "12,000+ jurisdictions — 7,394 cities, 2,332 counties, all 50 states" | City, town or county. Townships are not mentioned | Data-center tracker gives state counts (Q5). Customers include Prologis, Beale Infrastructure and Copenhagen Infrastructure Partners | V · [home](https://gathergov.com/), [DC tracker](https://gathergov.com/articles/data-center-moratorium-2026-tracker), [Curate comparison](https://gathergov.com/articles/gathergov-curate-alternative-in-2026) |
| **MyTownView** | "**22,946 municipalities in 50 states and DC**, covering 239.3M residents". The pricing page says "23,000+". Its per-state list is the largest of any product: PA 1,893, MI 1,368, IL 1,278, TX 1,217, MO 941, IA 939, OH 925, MN 853, KS 626, WI 599, NY 595 … VT 251, NH 240, CT 169, RI 39, NV 19 | Municipality | Listing counts look like a full directory. The site does not say how many places actually have meeting summaries. Founder is in Villa Park, IL | V · [coverage](https://mytownview.com/coverage), [home](https://mytownview.com/), [pricing](https://mytownview.com/pricing) |
| **Red Tape Recordings** | "7273 governments covered, 11946 meetings archived, 11335 with a real transcript". The state list (unit not stated) runs CA 1,513, UT 891, TX 781, NY 569, FL 559, MN 387, MA 355, NC 317, IL 316, MI 312, OH 289, PA 250 … NV 50, NE 26 | Government body, from crowd-submitted links | Mixed. Coverage depends on users pasting meeting links | V · [coverage](https://redtaperecordings.com/coverage) |
| **CivicSearch** | 547 cities and towns, US and Canada (civictech.guide); "over 650" (Cambridge 2024 agenda). Built on LocalView transcripts | City or town council | Mostly councils with video. The earlier MA check found 2 of 30 sample towns | S · [civictech.guide](https://civictech.guide/projects/civicsearch), [Cambridge ODRB agenda](https://cambridgema.gov/-/media/Files/informationtechnologydepartment/opendata/odrb/2024/odrb_agenda_20241203.pdf) |
| **Civic IQ** | "agendas, packets, and minutes of **100,000+ agencies**". The product page says 80,000+ agencies in 50 states | City council, county commission, school board | Procurement focus ("6 to 18 months before formal RFPs"). No township evidence | S (search summary of vendor pages; fetch blocked) · [MCP page](https://civiciq.com/mcp/public-meetings-mcp), [Signals](https://civiciq.com/products/signals) |
| **MultiState** (local) | "more than **4,850 jurisdictions** nationwide" | "municipalities, counties, **townships**, and special districts" | Townships claimed. No list published | V · [MultiState local page](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma) |
| **Quorum Local** | "all counties and cities of **3,000 or greater**"; "over 12,500 sources" | City or county above a population floor | By definition it excludes the smallest towns and townships | V · [Quorum Local](https://www.quorum.us/products/local/) |
| **FiscalNote PolicyNote / Curate** | "more than **12,000 US cities and counties**, 4,000+ school districts, 200+ state boards"; "400,000+ meeting minutes, agendas, and planning documents" a week | City or county | Townships are not mentioned | S · [FiscalNote press release, May 19, 2026](https://www.financialcontent.com/article/bizwire-2026-5-19-fiscalnote-expands-policynote-api-adding-local-government-intelligence-to-enterprise-and-ai-agent-workflows) |
| **Councilmatic** | Live: **Chicago** and **LA Metro** only, per its own home page. NYC and Philadelphia were earlier deployments | Big-city council legislation | None | V · [councilmatic.org](https://www.councilmatic.org/); S · [PPF](https://participatorypolitics.org/councilmatic/) |
| **BillTrack50** | Federal and state legislation; no local-ordinance category found | State | None | S · [ELGL interview](https://elgl.org/importance-legislative-tracking-karen-suhaka-founder-billtrack50) |
| **Ballotpedia** (local) | Elections in the **100 largest cities** and their overlapping counties, plus state capitals. Local ballot measures in those places and "throughout California and Virginia" | City or county (elections and ballot measures only) | Tracks 2026 data-center ballot measures: 38 in 8 states; Ohio has 20 in 17 jurisdictions | V-idx · [Texas cities page](https://ballotpedia.org/Texas_cities), [DC ballot measures 2026](https://news.ballotpedia.org/2026/09/21/ohio-leads-states-in-number-of-local-ballot-measures-on-data-centers-for-2026/) |
| **Heatmap Pro** | Local laws for "**every U.S. county and township**"; risk scores "for every U.S. county and zip code"; "regular phone calls to all 3,100+ U.S. counties" | County. Townships are claimed for laws only | Built by calling counties, so township data most likely comes from county contacts [E] | V · [Heatmap Pro](https://heatmap.news/pro) |
| **Spark** (sparkhq.ai) | "3,000+ counties"; all 50 states "down to county and **township levels**" where public online sources exist | County, and township where online | No township list. "Where public online sources exist" excludes townships with no website [E] | V · [sparkhq.ai](https://www.sparkhq.ai/) |
| **SitePath** | "Every U.S. county, researched and graded" | County | The example record cites "BoS minutes" (Mecklenburg) | V · [sitepathintel.com](https://www.sitepathintel.com/) |
| **Learnewable / Site Scout** | "more than 3,000 counties" | County | Transcribes meetings posted to **YouTube**. Rural bodies without video are missed [E] | S · [pv magazine](https://www.pv-magazine.com/2026/03/05/ai-platform-aims-to-transform-solar-site-assessment-2/) |
| **Transect** | Local Solar Regulations (beta) "usually captures most counties in a given state". As of June 2025, "80%+ county-level coverage in 6 states: CA, IL, NM, AZ, CO and TX" | County | Storage and wind "aren't covered in this release" | V · [Transect support](https://support.transect.com/local-solar-regulations); V-idx (six-state figure) · same page via search |
| **Paces** | No geographic claim. "Power and Permitting Reports"; example from Hansford County, TX | Site or project | Not described | V · [paces.com](https://www.paces.com/) |
| **Shovels Decisions** | "600+ cities and nearly 200,000 decision records"; "half the jurisdictions where we already have permit coverage" | City | Cities only | V · [Decisions launch](https://www.shovels.ai/blog/decisions-api-launch/) |
| **Zoneomics** | "10000+ Cities digitized", "100M+ Parcels" | City (code text) | Cities | V · [pricing](https://www.zoneomics.com/pricing) |
| **Cleanview** | "Track every data center in the United States"; power projects nationwide | Project | Not local rules | V · [pricing](https://cleanview.co/pricing) |
| **LandGate** | PowerTools: parcels, substations, interconnection queues, owner contacts. No zoning or meeting product found | Parcel | n/a | S · [NA Clean Energy](https://nacleanenergy.com/wind/product-suite-providing-increased-insight-into-land-resources) |
| **Enverus** | No local ordinance or moratorium tracker surfaced in search | — | — | (negative search; see Gaps) |
| **OrdinanceWatch** | **Georgia: 13 counties and 40 municipalities**, almost all metro Atlanta plus regional cities (Augusta, Savannah, Macon, Columbus, Valdosta …). Florida also monitored | County or city | Not rural | V · [Georgia page](https://ordinancewatch.com/index.php/what-we-monitor/georgia) |
| **Documenters** (City Bureau) | Chicago, Cleveland, Detroit, Minneapolis, Atlanta, Omaha, Fresno, plus LA County (2025); "11 cities" | Big-city and county bodies, covered by paid residents | None | S · [GMF](https://www.gmfus.org/gmf-cities/democracy-actions-cities/resident-journalists), [Berkeley Possibility Lab](https://possibilitylab.berkeley.edu/project/la-documenters-active) |
| **Newsroom agenda bots** | LoCOBot (Lost Coast Outpost, Humboldt County, CA); Agenda Watch (Big Local News/Stanford with RJI, "agencies across the country"); LocalLens (bought by APM in 2025; MPR searches "the entire state of Minnesota"); CivicTide (Seattle); citymeetings.nyc; Council Data Project (Seattle) | Single newsroom footprint | Narrow, apart from LocalLens in MN | S · [Nieman Lab](https://www.niemanlab.org/2025/03/local-newsrooms-are-using-ai-to-listen-in-on-public-meetings/), [RJI](https://rjionline.org/news/welcome-to-agenda-watch/), [Current](https://current.org/?p=8006127), [GeekWire](https://www.geekwire.com/2026/former-seattle-city-council-president-launches-ai-powered-site-to-track-and-report-on-city-hall/), [NY1](https://ny1.com/nyc/all-boroughs/CTV/2024/10/12/new-website-uses-ai-to-monitor-city-hall-meetings) |
| **DIY scrapers** (Apify) | "City Council Watch": **Legistar cities only**, "upcoming council/committee meetings" with `agendaFile`. A separate "Stafford Data Center Planning Monitor" (Stafford County, VA) exists | City (Legistar) | Legistar is a big-city platform [K] | V · [City Council Watch](https://apify.com/m_ctim/city-council-watch); S (listing title only) · [Stafford monitor](https://apify.com/mikechiou/stafford-data-center-planning.md) |
| **Granicus** (govDelivery, Legistar) | "more than 7,000 government organizations" | Per body, per government | Wherever a government buys it | V-idx · [granicus.com/llms.txt](https://granicus.com/llms.txt) |
| **CivicPlus Notify Me / Agenda Center** | No customer count found. In use from TN to TX, WA, ID, MT and NY | Per board, per town | Small towns and counties use it: La Vergne TN, Portland TN, Taylor County TX, Spokane County WA, Belgrade MT, West Seneca NY | V-idx · [La Vergne](https://www.lavergnetn.gov/list.aspx), [Taylor County](https://www.taylorcounty.texas.gov/list.aspx), [Spokane County](https://www.spokanecounty.gov/list.aspx?ListID=503), [Belgrade](https://www.belgrademt.gov/AgendaCenter/PreviousVersions/_04202026-454) |
| **Newspaper public-notice sites** | Statewide sites: TX (texaslegalnotices.com, being rebuilt with Column), PA, WI, VA, SC, WA. Statutory email alerts in **Iowa** ("free, searchable … email alerts") and **Maine** (free email notifications). USALegalNotice links 47 state sites | Every notice a government publishes, including zoning hearings | Statewide wherever newspapers carry legal notices | S · [TPA/Column](https://www.texaspress.com/node/12725), [Iowa Code 618.3A](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf), [Maine 1 MRSA §603](https://mainelegislature.org/legis/statutes/1/title1sec603.html), [VPA](https://theenterprise.net/vpa-launches-statewide-public-notice-website/), [SC](https://www.theitem.com/stories/newspapers-press-association-launch-new-online-public-notice-database,319919), [PA](https://panewsmedia.org/?p=1225), [E&P on USALegalNotice](https://www.editorandpublisher.com/stories/nam-creates-nationwide-public-notice-website,190382) |

**B. Hamlet per-state coverage, and its share of the local governments that make land-use decisions**

The figures come from the myhamlet.com/coverage rows ("Cities & Counties" / "Jurisdictions") as quoted by the search index [V-idx, https://www.myhamlet.com/coverage].
- "Jurisdictions" is not defined. CT shows 33 places but 1,102 "jurisdictions", so it probably counts bodies or meetings.
- Rows for SC, TN, NJ, KY, OK, WA and OR were not returned before the search budget ran out.

How the land-use denominator was built [E]:
- PA, OH, MI, WI, MN, NY, ME, NH, VT, CT, RI, MA, IN, IL and TX: Census of Governments 2022, as adjusted in `expansion_markets.md` §4.3 (program page: https://www.census.gov/programs-surveys/cog.html).
- Other states: MyTownView's municipality counts [V, https://mytownview.com/coverage] plus the state's county count [K].

| Region | State | Hamlet places | "Jurisdictions" | Land-use governments (E) | Hamlet share (E) |
|---|---|---|---|---|---|
| Township-zoning | PA | 55 | 347 | 2,625 | **2.1%** |
| | OH | 80 | 460 | 2,322 | **3.4%** |
| | MI | 76 | 665 | 1,856 | **4.1%** |
| | WI | 55 | 742 | 1,922 | **2.9%** |
| | MN | 75 | 380 | 2,720 | **2.8%** |
| Midwest, non-zoning townships | IL | 69 | 711 | ~1,400 | 4.9% |
| | IN | 57 | 340 | ~660 | 8.6% |
| Plains | IA | 46 | 262 | ~1,038 | 4.4% |
| | KS | 48 | 144 | ~731 | 6.6% |
| | NE | 9 | 24 | ~622 | **1.4%** |
| | MO | 57 | 450 | ~1,055 | 5.4% |
| Southeast | GA | 74 | 302 | ~697 | 10.6% |
| | NC | 116 | 451 | ~651 | 17.8% |
| | VA | 64 | 533 | ~323 | 19.8% |
| | SC, TN | not retrieved | — | — | — |
| Texas | TX | 176 | 1,293 | ~1,471 nominal (600 decision units) | 12% (29% of decision units) |
| Mountain West | AZ | 41 | 251 | ~106 | 39% |
| | NV | 17 | 295 | ~35 | 49% |
| | NM | 15 | 70 | ~139 | 10.8% |
| | CO | 56 | 338 | ~334 | 16.8% |
| | UT | 37 | 122 | ~283 | 13.1% |
| | ID | 16 | 105 | ~244 | 6.6% |
| Rest of New England | ME | 13 | 140 | 484 | **2.7%** |
| | NH | 20 | 314 | 234 | 8.5% |
| | VT | 7 | 10 | 277 | **2.5%** |
| | CT | 33 | 1,102 | 179 | 18.4% |
| Reference | NY | 76 | 584 | 1,525 | 5.0% |
| | MA | 82 | — | 351 | 23.4% |
| | RI | 12 | 76 | 39 | 30.8% |
| | CA | 319 | — | ~540 | ~59% |
| | FL | 148 | — | ~478 | ~31% |
| | AL | 34 | — | ~529 | 6.4% |

**Caveat:** the earlier MA test found that a Hamlet "place" can mean only 1–2 non-land-use bodies. Examples: Amherst ("2 governing bodies"), Fitchburg Park Commissioners, Westford Pedestrian Safety Committee (`competitor_behind_login.md` §5). The shares above are therefore upper bounds for land-use coverage [E].

**C. Where Citizen Portal reaches rural siting bodies (all post-meeting recaps, found through the search index)**
- **OH townships.** Williams County: trustees of Springfield, Center and Velasquez townships "have passed resolutions" on large solar — [cpo.soar.com 6023790](https://cpo.soar.com/articles/6023790/Ohio/Township-trustees-press-commissioners-for-tools-to-limit-large-solar-fields). Washington County commissioners on data centers — [7904045](https://citizenportal.ai/articles/7904045/Ohio/Washington-County/Commissioners-approve-routine-business-residents-raise-data-center-concerns).
- **PA townships and counties.** Warriors Mark Twp (Huntingdon Co.) solar conditional-use hearing — [9335109](https://citizenportal.ai/articles/9335109/pennsylvania/huntingdon-county/warriors-mark/township-schedules-solar-conditionaluse-hearing-motions-to-prompt-ordinance-update). Cameron County data-center ordinance addendum — [9996768](https://citizenportal.ai/articles/9996768/Pennsylvania/Cameron-County/Commissioners-approve-SAO-addendum-to-address-data-centers).
- **Plains counties.** Keith County, NE wind/solar moratorium extension — [6135698](https://citizenportal.ai/articles/6135698/Nebraska/Keith-County/Keith-County-extends-12-month-moratorium-on-commercial-wind-and-solar-projects). Butler County, KS data centers — [8913279](https://citizenportal.ai/articles/8913279/Kansas/Butler-County/Commissioner-asks-county-to-clarify-data-center-information-on-its-website). Des Moines County, IA data-center moratorium — [9584849](https://citizenportal.ai/articles/9584849/Iowa/Des-Moines-County/Residents-urge-supervisors-to-keep-datacenter-moratorium-in-place).
- **Texas commissioners courts (BESS).** Dimmit — [7472469](https://citizenportal.ai/articles/7472469/Texas/Dimmit-County/Dimmit-County-tables-battery-storage-permit-and-asks-county-attorney-for-review), [7988954](https://citizenportal.ai/articles/7988954/Texas/Dimmit-County/Dimmit-County-approves-permit-for-NW-Group-battery-energy-storage-project). Kerr — [7252162](https://citizenportal.ai/articles/7252162/Texas/Kerr-County/Kerr-County-workshop-flags-BESS-safety-urges-permit-fees-and-expert-review). Harrison — [6067668](https://citizenportal.ai/articles/6067668/texas/harrison-county/developer-presents-300mw-battery-storage-plan-county-and-residents-press-for-safety-data).
- **Southeast.** Coweta County, GA data-center rezoning — [6068053](https://citizenportal.ai/articles/6068053/georgia/coweta-county/coweta-commissioners-approve-rezoning-for-project-peach-data-center-campus-near-palmetto-amid-heavy-public-opposition), [7061939](https://citizenportal.ai/articles/7061939/georgia/coweta-county/residents-urge-coweta-commissioners-to-resist-rezoning-rural-conservation-land-for-data-center).
- **Michigan.** St. Clair County solar and data centers (Nov 2024) — [cpo.soar.com 1461929](https://cpo.soar.com/articles/1461929/St-Clair-County/Michigan/Residents-rally-against-solar-and-data-center-expansion-plans).
- **No index hits** (a lower bound, not proof of absence): AZ/UT/ID/NM county energy items; NH/VT/CT boards; NC/SC.

### Inferences
- [E] The **Hamlet share gradient is the clearest geographic signal**. Its coverage favours states with few large general-purpose governments (CA, FL, AZ, NV, RI) and falls below 5% wherever thousands of townships or towns hold zoning power: PA, OH, MI, WI, MN, ME and VT, plus NY and IA, and NE at 1.4%.
- [E] Coverage counts are **not comparable across products**. MyTownView's 22,946 is a municipal directory. Red Tape's 7,273 are crowd-submitted bodies. GatherGov's 9,300 are "towns and counties". MultiState's 4,850 are analyst-monitored jurisdictions. Only Hamlet and OrdinanceWatch publish per-state or per-place lists.
- [E] The **county-grain siting tools** (Heatmap, Spark, SitePath, Learnewable, Transect) fit county-zoning states: TX, the Southeast, the Plains, the Mountain West and IN. In township states they claim townships but show no list. Spark limits itself to places "where public online sources exist", and Heatmap gathers data by calling counties.
- [E] **Citizen Portal is the only product with visible rural-township and rural-county siting stories**. It is also the main reason "nothing covers rural X" cannot be claimed, but its items are recaps written after the meeting (Q2).

### Gaps
- Hamlet's state rows for SC, TN, NJ, KY, OK, WA and OR were not retrieved before the search budget ran out. The "Jurisdictions" column is undefined.
- Hamlet's per-state rows come from the search index. They could not be checked on the live page, which is behind a Vercel checkpoint.
- Citizen Portal publishes no jurisdiction count. Per-state article counts were seen only for CA and AZ, through a search summary.
- No per-state list exists for MultiState, Quorum, FiscalNote, GatherGov, Spark, Heatmap or Civic IQ. None of them publishes which townships, if any, it reaches.
- **Govlist:** no product of that name was found. Searches returned only CivicPlus and GovDelivery list pages.
- **Enverus:** no local-ordinance or moratorium product surfaced.
- **LandGate:** no zoning or meeting product surfaced.
- **Kite:** nothing new beyond `where_we_win.md`.
- Planned but not run (budget exhausted): Citizen Portal checks for Wisconsin towns, Minnesota townships and Michigan townships.

---

## 2. Which products read agendas before meetings, which summarize afterwards, and which track only adopted ordinances?

### Takeaway
**Pre-meeting agenda reading is claimed by enterprise government-affairs tools** (MultiState, Quorum, FiscalNote), by Hamlet, Spark, Civic IQ and OrdinanceWatch, and by the free per-board "Notify Me" lists. None of them shows a town- or township-level siting list.
- The products with visible rural reach work after the meeting. Citizen Portal writes recaps from video. GatherGov says items are searchable "within 24 hours of the meeting".
- Every free data-center tracker and every ordinance database records actions **after adoption**, or at best once they are pending.

### Cited Findings

| Freshness tier | Product | What its own words say | Label · Source |
|---|---|---|---|
| **Before the meeting (agenda-based)** | MultiState | Analysts "scour city and county websites … to identify upcoming action"; "As soon as we know, you'll know"; hourly snapshots | V · [MultiState](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma) |
| | Quorum Local | "notified the moment your issues appear on any agenda" | V · [Quorum](https://www.quorum.us/products/local/) |
| | FiscalNote PolicyNote / Curate | Processes "meeting minutes, agendas, and planning documents". A rival says Curate runs a "weekly refresh cycle typical" | S · [press release](https://www.financialcontent.com/article/bizwire-2026-5-19-fiscalnote-expands-policynote-api-adding-local-government-intelligence-to-enterprise-and-ai-agent-workflows); S (competitor claim) · [GatherGov](https://gathergov.com/articles/gathergov-curate-alternative-in-2026) |
| | Hamlet | Agenda objects with "agenda-monitoring topics". Coverage rows list "Upcoming" meeting dates | V · [API](https://api.myhamlet.com/openapi.json); V-idx · [coverage](https://www.myhamlet.com/coverage) |
| | Spark | Alerts for "new ordinances, moratoria, and agendas"; refresh "Daily" or "multiple times per week" (the two pages disagree) | V · [sparkhq.ai](https://www.sparkhq.ai/) |
| | Civic IQ | Agendas and **packets**; signals "6 to 18 months before formal RFPs" (procurement focus) | S · [Civic IQ](https://civiciq.com/mcp/public-meetings-mcp) |
| | OrdinanceWatch (GA, FL) | "We can tell you what they are going to do before they do it"; email with "a running history of the issue" | V · [OrdinanceWatch GA](https://ordinancewatch.com/index.php/what-we-monitor/georgia) |
| | Agenda Watch (Big Local News) | "harvests those documents on a daily basis"; alerts "when similar items crop up in new documents" | S · [RJI](https://rjionline.org/news/welcome-to-agenda-watch/), [MuckRock](https://muckrock.com/news/archives/2023/jun/28/agenda-watch-muckrock-accounts) |
| | LoCOBot (Humboldt Co.) | Downloads and summarizes agendas; reporters are alerted when a new agenda goes up | S · [Nieman Lab](https://www.niemanlab.org/2025/03/local-newsrooms-are-using-ai-to-listen-in-on-public-meetings/) |
| | Apify City Council Watch | "Also fetch upcoming council/committee meetings"; Legistar only | V · [Apify](https://apify.com/m_ctim/city-council-watch) |
| | CivicPlus Notify Me / Granicus govDelivery | Email or text when a board's agenda posts; one list per board, no keyword filter | V-idx · [Minneapolis GovDelivery](https://www.minneapolismn.gov/media/-www-content-assets/documents/ABC-GovDelivery-Notices.pdf), [La Vergne](https://www.lavergnetn.gov/list.aspx) |
| | Newspaper public-notice sites | Hearing notices published before the hearing; email alerts by statute in IA and ME | S · [Iowa 618.3A](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf), [Maine §603](https://mainelegislature.org/legis/statutes/1/title1sec603.html) |
| **After the meeting (recaps, transcripts, minutes)** | Citizen Portal | Mostly recaps; rare agenda previews (Warwick, MA) | earlier note `competitor_behind_login.md` §3 |
| | GatherGov | "Meetings searchable within 24 hours"; moratorium items surface "within 24 hours of the meeting". Its tracker also counts pre-adoption stages ("Formally introduced: 120", "Staff study or legal review: 232") | V · [DC tracker](https://gathergov.com/articles/data-center-moratorium-2026-tracker), [Curate comparison](https://gathergov.com/articles/gathergov-curate-alternative-in-2026) |
| | MyTownView | Summaries of "what passed, who voted how"; a free Sunday email of "what happened and what's coming up" | V · [mytownview.com](https://mytownview.com/) |
| | Red Tape Recordings, CivicSearch, Learnewable | Transcripts of posted video (Learnewable uses YouTube) | V · [Red Tape](https://redtaperecordings.com/coverage); S · [civictech.guide](https://civictech.guide/projects/civicsearch), [pv magazine](https://www.pv-magazine.com/2026/03/05/ai-platform-aims-to-transform-solar-site-assessment-2/) |
| | Shovels Decisions | "we don't create a decision record until the minutes are posted"; minutes can lag "weeks" | V · [Shovels](https://www.shovels.ai/blog/decisions-api-launch/) |
| | Documenters | Paid residents attend meetings and publish notes | S · [Berkeley Possibility Lab](https://possibilitylab.berkeley.edu/project/la-documenters-active) |
| **Adopted ordinances or periodic snapshots** | Heatmap Pro | Local laws "sourced through regular direct calls"; opposition database "Updated daily" from news and calls; meetings not listed as a source | V · [Heatmap Pro](https://heatmap.news/pro) |
| | SitePath, Transect, Zoneomics | Graded county records; solar permit matrices; zoning-code text | V · [SitePath](https://www.sitepathintel.com/), [Transect](https://support.transect.com/local-solar-regulations), [Zoneomics](https://www.zoneomics.com/pricing) |
| | dcmap.us | 70 actions: "In force (60), Pending (1), Expired (3), Defeated (6)"; "smaller local pauses can go unreported" | V · [dcmap policy](https://dcmap.us/insights/policy/) |
| | Electric Choice | "506 active restrictions"; "reconciled monthly"; sources include "planning commission agendas"; "a floor rather than a precise census" | V · [Electric Choice](https://www.electricchoice.com/datacenters/moratoriums/) |
| | Axis Intelligence | 10 actions; updated weekly on Sundays | V · [Axis](https://axis-intelligence.com/data-center-moratorium-tracker/) |
| | NLC Data Center Local Action Tracker | ≥76 local governments "have attempted moratoriums or permanent bans" | S · [Route Fifty](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/) |
| | Data Center Watch (10a Labs) | Quarterly reports on projects blocked or delayed | S · [DCD](https://www.datacenterdynamics.com/en/news/group-claims-64bn-in-us-data-center-projects-impacted-by-local-opposition-in-last-two-years/), [AI Weekly](https://aiweekly.co/alerts/data-center-watch-45-us-ai-data-center-projects-worth-68b-blocked-or-delayed-in) |
| | NREL ordinance databases | 2025 wind (issued 2025-09-12) and solar (2025-12-30), built with LLMs; state, county and township ordinances | S · [data.gov solar](https://catalog.data.gov/dataset/u-s-solar-siting-regulation-and-zoning-ordinances-2025), [data.gov wind](https://catalog.data.gov/dataset/u-s-wind-siting-regulation-and-zoning-ordinances-2025) |
| | U-Michigan Energy Zoning Database | Ordinance PDFs for counties, townships and cities in IL, IN, MI, MN, OH, WI | S · [U-M news](https://news.umich.edu/?p=140351) |
| | Penn State PA Solar Ordinance Database | 4,900 provisions, 300 local governments, 57 counties | S · [CELP about](https://celp.psu.edu/solarordinance/about), [database](https://celp.psu.edu/publications/pa_solar_database/) |
| | Sabin Center | Annual. 6th edition (Sep 2026): 888 restrictions (865 local) as of Dec 31, 2025 | S · [Sabin press release](https://climate.law.columbia.edu/news/new-sabin-center-reports-find-widespread-restrictions-and-misinformation-are-hampering) |
| | Ballotpedia | Ballot measures only (data-center measures, 2026) | V-idx · [Ballotpedia News](https://news.ballotpedia.org/2026/09/21/ohio-leads-states-in-number-of-local-ballot-measures-on-data-centers-for-2026/) |

### Inferences
- [E] **No product that shows rural-township reach is pre-meeting**, and no product that is pre-meeting shows rural-township reach. That intersection is the gap 351 Watch fills in MA.
- [E] **The data-center trackers disagree badly, which shows nobody has a complete local feed.**
  - Michigan: Electric Choice 63, dcmap 0, GatherGov "20 or more".
  - Massachusetts: Electric Choice 4, dcmap 0, GatherGov 20+; 351 Watch counted items in 53 towns.
  - A pre-meeting, town-level feed would be new in every state.
- [E] GatherGov is the **closest rival on data centers**. It is national, counts "formally introduced" and "staff study" stages, and sells to developers (Prologis, Beale). But it is post-meeting (within 24 hours) and publishes no list of the jurisdictions it covers.

### Gaps
- No product's actual lead time could be measured (no accounts).
- Hamlet's alert delivery and Spark's agenda alerts are claims only.
- GatherGov's statement that Curate refreshes weekly is a competitor's claim. FiscalNote's own Curate page returned 403.

---

## 3. How does coverage break down by topic?

### Takeaway
Siting-intelligence tools cover **solar, BESS, wind and data centers**. Government-affairs tools cover **any custom keyword**. Data-center trackers cover **only data centers**. **No product found specifically flags 40B-style housing comprehensive permits or wireless-tower siting**, and only Shovels and the generic keyword tools reach ordinary zoning changes.

### Cited Findings

● = claimed on the product's page; ○ = possible through custom keywords only; — = not mentioned.

| Product | Solar | BESS | Wind | Data centers | Moratoria | Housing comp. permits | Wireless towers | General zoning changes | Transmission | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| Heatmap Pro | ● | ● (polling) | ● | ● | ● (local laws) | — | — | — | — | [V](https://heatmap.news/pro) |
| Spark | ● utility-scale | ● | ● (permitting matrix) | ● | ● | — | — | — | — | [V](https://www.sparkhq.ai/) |
| SitePath | ● | ● | — | ● ("siting signals") | ● ("active moratoria") | — | — | — | — | [V](https://www.sitepathintel.com/) |
| Learnewable | ● | ● | ● | ● | ● | — | — | — | — | [S](https://www.pv-magazine.com/2026/03/05/ai-platform-aims-to-transform-solar-site-assessment-2/) |
| Transect | ● (local regs, beta) | ✕ "not covered in this release" | ✕ | — | ● (sentiment uses moratoriums) | — | — | — | ● (platform) | [V](https://support.transect.com/local-solar-regulations), [S](https://netzerocompare.com/software/transect) |
| Shovels Decisions | ● | — | ● | — | — | ○ ("density changes") | — | ● rezonings, code changes | ● | [V](https://www.shovels.ai/blog/decisions-api-launch/) |
| Zoneomics | — | — | — | — | — | — | — | ● (code text only) | — | [V](https://www.zoneomics.com/pricing) |
| Cleanview | ● projects | ● projects | ● projects | ● projects | — | — | — | — | — | [V](https://cleanview.co/pricing) |
| GatherGov | ○ | ○ | ○ | ● (moratorium tracker) | ● | ○ | ○ | ● entitlements | ○ | [V](https://gathergov.com/) |
| MultiState / Quorum / FiscalNote | ○ | ○ | ○ | ● (MultiState DC pages) | ○ | ○ | ○ | ● (FiscalNote "zoning" among 400+ filters) | ○ | [V MultiState](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma), [S FiscalNote](https://www.financialcontent.com/article/bizwire-2026-5-19-fiscalnote-expands-policynote-api-adding-local-government-intelligence-to-enterprise-and-ai-agent-workflows) |
| Hamlet | ○ | ○ | ○ | ● ("data center sentiment indices", §4.4) | ○ | ● ("Housing" sample topic) | ○ | ● ("zoning changes") | ○ | earlier notes; [V API](https://api.myhamlet.com/openapi.json) |
| Citizen Portal | ● "Solar Policy" topic | ● | ● | ● "Economic Development Data Centers" topic | ● | ○ | ○ | ● "Land Use Energy" topic | ○ | V-idx · topic-alert labels on articles [6135698](https://citizenportal.ai/articles/6135698/Nebraska/Keith-County/Keith-County-extends-12-month-moratorium-on-commercial-wind-and-solar-projects), [8913279](https://citizenportal.ai/articles/8913279/Kansas/Butler-County/Commissioner-asks-county-to-clarify-data-center-information-on-its-website) |
| OrdinanceWatch | — | — | — | — | — | — | ● "Telecommunications" | ● "Land Development Code" | — | [V](https://ordinancewatch.com/index.php/what-we-monitor/georgia) |
| dcmap, Electric Choice, NLC, Axis, Data Center Watch | — | — | — | ● | ● | — | — | — | — | [V dcmap](https://dcmap.us/insights/policy/), [V EC](https://www.electricchoice.com/datacenters/moratoriums/) |
| NREL databases | ● | — | ● | — | — | — | — | — | — | [S](https://catalog.data.gov/dataset/u-s-wind-siting-regulation-and-zoning-ordinances-2025) |
| U-M Energy Zoning / Penn State | ● (17 solar traits) / ● | — | ● / — | — | — | — | — | — | — | [S U-M](https://news.umich.edu/?p=140351), [S PSU](https://celp.psu.edu/solarordinance/about) |
| Sabin Center | ● | ● (myths report) | ● (most targeted) | — | ● | — | — | — | — | [S](https://climate.law.columbia.edu/news/new-sabin-center-reports-find-widespread-restrictions-and-misinformation-are-hampering) |
| MyTownView, Red Tape, CivicSearch | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ (CivicSearch: 75 policy topics) | ○ | [V MyTownView](https://mytownview.com/), [S CivicSearch](https://civictech.guide/projects/civicsearch) |

### Inferences
- [E] **Data centers are the most crowded topic**: at least 7 free trackers plus GatherGov, Heatmap, Spark, SitePath and Cleanview. But the counts disagree by more than an order of magnitude in some states (Q5). A pre-meeting, town-level data-center layer is still differentiated, but only as a source feed, not as "the first tracker".
- [E] **BESS is under-tracked by the free databases.** NREL and U-M cover wind and solar, Transect's local regs exclude storage, and no free BESS moratorium tracker was found. Yet BESS items show up in rural county courts in Texas (Dimmit, Kerr, Harrison) and in NH town boards (Wakefield PB, Jun 18, 2026: solar tracker "with a battery storage system" conditional use permit — [agenda](https://www.wakefieldnh.gov/sites/g/files/vyhlif1366/f/agendas/6-18-2026_pb_agenda_final.pdf)).
- [E] **Housing comprehensive permits and wireless towers have no dedicated local monitor anywhere found.** Outside MA, RI, CT, IL and NJ (the states with 40B-like laws, §4.6 of expansion notes) housing is a weak expansion hook.

### Gaps
- Kite's and Paces' topic lists were not visible on their pages.
- Hamlet's topic catalogue is not public.
- No public BESS-specific moratorium tracker was found. Carina's NY count, cited in the earlier notes, is the nearest.

---

## 4. What does each product cost, using public prices?

### Takeaway
Self-serve published prices exist only at the **consumer or small-team end**:
- Citizen Portal: $12–49/mo.
- MyTownView: $29.99/yr to $2,499/yr.
- Zoneomics: $92–279/mo.
- Shovels: $599–999/mo.
- Cleanview: $9k/yr.
- Apify scrapers: per query.

Every siting-intelligence and enterprise government-affairs tool is **"request a demo"**. The only third-party price points are Vendr medians: Quorum about **$21.4k/yr**, FiscalNote about **$46.8k/yr**.

### Cited Findings

| Product | Public price | Label · Source |
|---|---|---|
| MyTownView | Free tier (3 AI questions a day). **Resident $29.99/yr** (5 custom alerts). **Pro $17/mo or $199/yr** (unlimited alerts). **Municipal Pro $108/mo or $1,299/yr**. **All Access $208/mo or $2,499/yr**. API "Coming Soon". 14-day trial | V · [pricing](https://mytownview.com/pricing) |
| Citizen Portal | $12–49/mo; lifetime $199–999 (conflicting listings) | earlier note `competitor_behind_login.md` |
| Hamlet | Not published; "Talk to sales"; 14-day trial; "$49/mo plan" (reported) | earlier notes; S · [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/) |
| GatherGov | "Start for free" / "Book a demo"; no prices | V · [gathergov.com](https://gathergov.com/) |
| Quorum (all products) | Vendr median **$21,429/yr** (range ~$16,192–34,456). Local-only price not shown | S · [Vendr](https://www.vendr.com/marketplace/quorum) |
| FiscalNote | Vendr median **$46,750/yr** (12 purchases) | S · [Vendr](https://vendr.com/marketplace/fiscalnote) |
| MultiState | Not published (contact) | V · [MultiState](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma) |
| Civic IQ | Not found | S · [Civic IQ](https://civiciq.com/mcp/public-meetings-mcp) |
| OrdinanceWatch | "30-day trial"; package prices on a page not read | V · [OrdinanceWatch GA](https://ordinancewatch.com/index.php/what-we-monitor/georgia) |
| Heatmap Pro | "Request a Demo"; annual access. Heatmap News is $9.99/mo or $99/yr, which is not Pro | V · [Heatmap Pro](https://heatmap.news/pro) |
| Spark | "Annual software subscription", priced by seats and usage; quote only | V · [sparkhq.ai](https://www.sparkhq.ai/) |
| SitePath | "Free to explore the map"; access "priced to your organization and the number of people" | V · [sitepathintel.com](https://www.sitepathintel.com/) |
| Paces | Demo only | V · [paces.com](https://www.paces.com/) |
| Learnewable, LandGate, Transect, Kite | No public price found | S · [pv magazine](https://www.pv-magazine.com/2026/03/05/ai-platform-aims-to-transform-solar-site-assessment-2/), [G2 LandGate](https://www.g2.com/products/landgate/reviews) |
| Cleanview | Data-center or power platform **$9,000/yr** (5 users); **API +$5,000/yr**; one-time download $4,900; research $18,000/yr | V · [pricing](https://cleanview.co/pricing) |
| Zoneomics | **$92/mo** Essentials, **$279/mo** Advanced; Enterprise custom; 20% off annual | V · [pricing](https://www.zoneomics.com/pricing) |
| Shovels Decisions | Beta: "one credit per decision". Plans $599/$999/mo per earlier note | V · [Decisions](https://www.shovels.ai/blog/decisions-api-launch/); earlier `where_we_win.md` |
| Apify City Council Watch | "from $5.50 / 1,000" city queries | V · [Apify](https://apify.com/m_ctim/city-council-watch) |
| Councilmatic | "Contact us for pricing" | V · [councilmatic.org](https://www.councilmatic.org/) |
| Free | dcmap, Electric Choice, NLC, Axis (CSV, CC BY 4.0, email gate), Data Center Watch, NREL, U-M, Penn State, Sabin, CivicSearch, Agenda Watch (MuckRock account), Ballotpedia, CivicPlus/Granicus lists, PA/VA/SC/IA/ME notice sites. WI notice alerts were $75/mo or $600/yr in 2011 (current status unknown) | V · [Axis](https://axis-intelligence.com/data-center-moratorium-tracker/); S · [WI 2011](https://wisblawg.law.wisc.edu/2011/02/04/wisconsin-public-notices-searchable-via-new-website/) |

### Inferences
- [E] Published prices sort into four bands:
  - **Consumer, $0–$50/mo:** Citizen Portal, MyTownView.
  - **Small team, $100–$1,000/mo:** Zoneomics, Shovels.
  - **Data platform, $9–14k/yr:** Cleanview.
  - **Enterprise, $20–50k+/yr:** Quorum, FiscalNote; MultiState is likely here too, though unpublished.
- [E] The siting tools that cover rural counties all sell by quote. A published, self-serve price for **town- and township-level, pre-meeting siting alerts** has no direct comparator anywhere in the US. That matches the band proposed in `where_we_win.md` (the $349/mo Siting Desk).

### Gaps
- Quorum's Vendr figure covers its whole product line, not Local alone.
- No third-party price was found for MultiState, Hamlet enterprise, GatherGov, Heatmap Pro, Spark, SitePath, Paces, Learnewable, Transect, LandGate or Civic IQ.
- OrdinanceWatch's package page was not read.

---

## 5. Which large, siting-heavy areas are clearly unserved?

### Takeaway
**The clearest gaps are the township-zoning states: PA, OH, MI, WI and MN.** In each one:
- Hamlet lists 2–4% of local governments.
- The only rural-township coverage visible is Citizen Portal recaps written after the meeting.
- The only pre-meeting claims are enterprise tools with no published township lists.
- The only state-specific resources are databases of adopted ordinances (Penn State; U-Michigan's six-state database).

**Northern New England (ME, VT, and to a lesser degree NH)** is the second gap, with Hamlet at 2.5–8.5%.

**Plains counties (NE, IA, MO, KS)** are thin but county-grain, so national siting tools fit them better. **Texas, the Mountain West and the Atlanta/Charlotte metros are the most served.** Georgia has the only regional pre-meeting firm found, OrdinanceWatch, but it does not cover siting topics.

### Cited Findings

**Region × product matrix.**

Data-center tracker counts are per state:
- **EC:** Electric Choice "tracked" restrictions [V](https://www.electricchoice.com/datacenters/moratoriums/).
- **dcmap:** dcmap actions [V](https://dcmap.us/insights/policy/).
- **GG:** GatherGov jurisdictions "in a formal process" [V](https://gathergov.com/articles/data-center-moratorium-2026-tracker).

Hamlet shares come from Q1 table B.

| State | Hamlet places (share, E) | Citizen Portal siting evidence (post-meeting) | DC trackers EC / dcmap / GG | Adopted-ordinance DBs | Regional or pre-meeting specialist found | Verdict (E) |
|---|---|---|---|---|---|---|
| **PA** | 55 (2.1%) | Warriors Mark Twp solar CU hearing; Cameron Co. DC addendum | 7 / 1 / — | Penn State (300 govts, 57 cos.); NREL | None. PA newspapers' notice site (free email) [S](https://panewsmedia.org/?p=1225) | **Clear gap** (township grain) |
| **OH** | 80 (3.4%) | Williams Co. township trustees (solar) | 55 / 4 / — | U-M; NREL | None. Township DC moratoria are active: Pierce [S](https://www.fox19.com/2026/09/10/pierce-township-trustees-rule-out-data-center-extend-zoning-moratorium/), Liberty [S](https://www.wcpo.com/news/local-news/butler-county/liberty-township/liberty-township-zoning-commission-advances-data-center-restrictions-to-trustees-for-final-vote), Hubbard [S](https://www.tribtoday.com/news/local-news/2026/02/hubbard-township-oks-moratorium-on-data-centers/), Muhlenberg [S](https://www.circlevilleherald.com/community/muhlenberg-trustees-pass-12-month-moratorium-on-data-centers/article_1669c51d-3606-432b-b2c5-633b7e5a25fb.html); Ballotpedia: 20 OH DC ballot measures in 17 jurisdictions | **Clear gap**: highest township DC activity seen |
| **MI** | 76 (4.1%) | St. Clair Co. (2024) | **63 / 0 / 20+** | U-M; NREL | None | **Clear gap**: trackers disagree most here |
| **WI** | 55 (2.9%) | not checked (budget) | 18 / 1 / **36** | U-M | None. WI notice site [S](https://themonroetimes.com/views/wisconsin-is-keeping-you-informed); Rock Co. moratorium debate [S](https://www.gazettextra.com/news/rock-county-board-wrestles-over-whether-county-could-enforce-data-center-moratorium/article_b851705b-b65a-48fb-b8d8-1efc8c0f1c32.html) | **Clear gap** |
| **MN** | 75 (2.8%) | not checked (budget) | 4 / 0 / — | U-M | LocalLens/MPR statewide search, newsroom-only [S](https://current.org/?p=8006127) | **Clear gap**, but the state takes ≥50 MW (expansion §4.5), which lowers its value |
| **IL** | 69 (4.9%) | — | 11 / 1 / — | U-M; NREL | None; NLC: ≥10 IL jurisdictions proposed moratoria [S](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/) | Gap (county + municipal grain) |
| **IN** | 57 (8.6%) | — | 25 / 3 / — | U-M; NREL; Heatmap county analysis [S](https://heatmap.news/plus/the-fight/spotlight/data-centers-indiana-renewable-energy-restrictions) | None; "nearly a third of Indiana counties" restrict DCs [S](https://www.insideindianabusiness.com/?p=204751) | Partial: county tools fit, no pre-meeting feed |
| **IA** | 46 (4.4%) | Des Moines Co. DC moratorium | 30 / 4 / — | NREL | Statutory statewide notice site with free email alerts [S](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf) | Gap (county grain) |
| **KS** | 48 (6.6%) | Butler Co. DC | 8 / 0 / — | NREL | None; Crawford Co. moratorium [S](https://morningsun.net/news/local-news/a-request-to-extend-moratorium/) | Partial (county grain) |
| **NE** | **9 (1.4%)** | Keith Co. wind/solar moratorium | 13 / 1 / — | NREL | None; Hayes Co. 12-month moratorium covering wind, solar, BESS and DCs [S](https://hayescounty.ne.gov/posting_files/pdfs/board/minutes/2026/20260630_091147_board_minutes.pdf); Deuel Co. [S](https://deuelcountyne.gov/posting_files/pdfs/board/minutes/2024/20241203_172839_board_minutes.pdf) | **Gap**: lowest Hamlet share measured |
| **MO** | 57 (5.4%) | — | 9 / 1 / — | NREL | None; NLC: St. Charles ban, Festus/St. Louis agreements [S](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/) | Gap (county grain) |
| **GA** | 74 (10.6%) | Coweta Co. DC rezonings | 42 / 6 / **45** | — | **OrdinanceWatch**: 13 counties, 40 cities, no siting categories [V](https://ordinancewatch.com/index.php/what-we-monitor/georgia); Georgia Tech DC moratorium tracker (~40 govts) [S](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/) | Metro served; rural counties partial |
| **NC** | 116 (17.8%) | none found | **56** / 4 / 39 | — | None; Stokes Co. DC rezoning lawsuit [S](https://insideclimatenews.org/news/19032026/north-carolina-county-data-center-rezoning-lawsuit/) | Partial; DC-crowded |
| **SC** | not retrieved | none found | 8 / 1 / — | — | Statewide notice database [S](https://www.theitem.com/stories/newspapers-press-association-launch-new-online-public-notice-database,319919) | Likely gap (unverified) |
| **VA** | 64 (19.8%) | — | 4 / 5 / — | — | VPA notice site [S](https://theenterprise.net/vpa-launches-statewide-public-notice-website/); single-county Apify DC monitor (Stafford) [S](https://apify.com/mikechiou/stafford-data-center-planning.md); Ballotpedia covers all VA local measures | Partial: few counties, county tools fit |
| **TN** | not retrieved | — | 26 / 2 / — | — | NLC: Memphis agreement [S](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/) | Likely gap (unverified) |
| **TX** | 176 (12%; 29% of decision units) | **Dimmit, Kerr, Harrison** commissioners courts (BESS) | 7 / 2 / — | Transect 80%+ county solar regs | texaslegalnotices.com (search and alerts in rebuild) [S](https://www.texaspress.com/node/12725) | Most served of the large states (county grain); Hill Co. DC/BESS moratorium [S](https://news.bloomberglaw.com/texas-brief/dallas-exurb-hits-pause-on-data-centers-in-a-rare-texas-rebuke) |
| **AZ** | 41 (39%) | no county energy hits; AZ article volume 42,980 [S](https://cp.soar.com/) | 4 / 5 / — | Transect (80%+) | None | Served (few governments) |
| **NV** | 17 (49%) | — | 4 / 0 / — | — | None | Served |
| **NM** | 15 (10.8%) | — | 4 / 0 / — | Transect (80%+) | None | Partial |
| **CO** | 56 (16.8%) | — | 8 / 2 / — | Transect (80%+) | None; Mountain West county DC moratoria [S](https://www.kunc.org/2026-03-27/some-mountain-west-counties-impose-moratoriums-on-data-centers-as-national-pause-is-proposed) | Partial |
| **UT** | 37 (13.1%) | — | 4 / 0 / — | — | None | Partial |
| **ID** | 16 (6.6%) | — | 2 / 0 / — | — | None; Bannock Co. DC moratorium [S](https://www.bannockcounty.gov/wp-content/uploads/2026/07/Data-Center-Moratorium_Final.pdf) | Partial (small market) |
| **ME** | 13 (2.7%) | heavy in earlier notes (§4.4) | 2 / 0 / — | — | Statutory free notice emails [S](https://mainelegislature.org/legis/statutes/1/title1sec603.html) | **Clear gap** (town grain) |
| **NH** | 20 (8.5%) | none found | 3 / 0 / — | — | None; Wakefield PB solar+BESS hearing on agenda [S](https://www.wakefieldnh.gov/sites/g/files/vyhlif1366/f/agendas/6-18-2026_pb_agenda_final.pdf) | **Gap** (town grain) |
| **VT** | **7 (2.5%)**, 10 bodies | none found | 1 / 0 / — | — | None | Gap, but state PUC siting (§4.5) |
| **CT** | 33 (18.4%) | none found | 4 / 0 / — | — | None | Partial; state Siting Council ≥1 MW (§4.5) |
| *Ref.* MA | 82 (23%) | 18/30 sample towns | 4 / 0 / 20+ | — | **351 Watch 240 towns** | 351 Watch home |
| *Ref.* NY | 76 (5.0%) | heavy (§4.4) | 10 / 1 / — | — | **351 Watch 33 towns** | Gap outside the 33 towns |
| *Ref.* RI | 12 (31%) | Westerly (earlier note) | 3 / 0 / — | — | **351 Watch 39 municipalities** | Covered by 351 Watch |
| *Ref.* NJ | not retrieved | — | **93** / 2 / 33 | — | Statewide legal-notice directory (earlier note) | DC/housing; check later |
| *Ref.* CA | 319 (~59%) | 118,883 articles [S](https://cp.soar.com/) | 16 / 4 / 20+ | Transect | LoCOBot (Humboldt) [S](https://www.niemanlab.org/2025/03/local-newsrooms-are-using-ai-to-listen-in-on-public-meetings/) | Most served |
| *Ref.* FL | 148 (~31%) | — | 38 / 2 / 37 | — | OrdinanceWatch FL | Served |

**Conflicting counts to flag:**
- **GatherGov:** its own tracker page gives GA 45, NC 39, FL 37, WI 36, NJ 33 [V](https://gathergov.com/articles/data-center-moratorium-2026-tracker). A CRE Daily summary of a GatherGov count gives CA 73, GA 66, FL 60, NJ 51, NC 50 [S](https://www.credaily.com/?p=222881). These are probably different stage definitions or dates.
- **Electric Choice:** its NC summary says 52 but its table says 56 [V](https://www.electricchoice.com/datacenters/moratoriums/).
- **Data Center Watch:** reports conflict on 2025 vs 2026 dating and dollar totals [S](https://www.datacenterdynamics.com/en/news/group-claims-64bn-in-us-data-center-projects-impacted-by-local-opposition-in-last-two-years/).

### Inferences

Ranked gap list. These are places where no product shows town- or township-level, pre-meeting monitoring of siting items. All rankings are [E].

1. **Ohio.** Township trustees and township zoning commissions are passing data-center moratoria and solar resolutions now (Pierce, Liberty, Hubbard, Muhlenberg, Williams Co. townships).
   - Electric Choice counts 55 restrictions, and Ballotpedia counts 20 local DC ballot measures.
   - Hamlet lists 3.4% of governments; Citizen Portal writes recaps.
   - No regional specialist was found. **The strongest single gap.**
2. **Pennsylvania.** Local siting at any size across 2,625 governments; Hamlet lists 2.1%.
   - The only state resource, the Penn State database, covers adopted ordinances (300 governments).
   - Citizen Portal reaches some townships after the meeting. Code fit is weaker (see `where_we_win.md` §4).
3. **Michigan.** The data-center trackers disagree most here (63 vs 0 vs 20+), and the state has 1,240 townships; Hamlet lists 4.1%.
4. **Wisconsin.** GatherGov's 4th-highest DC state (36) and 742 Hamlet "jurisdictions" across only 55 places (2.9%); towns hold zoning.
5. **Northern New England (ME, NH, VT).** Same town-meeting and select-board form as MA, so 351 Watch's code and warrant features carry over. Hamlet lists 2.5–8.5% of towns, with no regional specialist. Energy value is lower in VT (PUC) and NH (state above 30 MW).
6. **Minnesota and Illinois.** Fragmented, and Hamlet is under 5%. In MN the state takes projects of 50 MW and up, and IL townships do not zone, so the grain is county plus municipal.
7. **Plains counties (NE, IA, MO, KS).** Hamlet is under 7% (NE 1.4%). Moratoria covering wind, solar, BESS and data centers at once are visible in county board minutes (Hayes, Deuel, Keith, Crawford, Des Moines). Because the grain is county, Heatmap and Spark already claim it, so this is a feed-speed gap rather than a coverage gap.
8. **SC and TN.** Unverified gaps: Hamlet rows were not retrieved, and no Citizen Portal hits surfaced. Electric Choice shows TN 26.

**Least attractive, because they are relatively served:**
- **CA, FL, AZ, NV:** Hamlet lists 30–60% of governments.
- **Texas:** Hamlet 176 places, Citizen Portal in rural commissioners courts, Transect, and county tools that fit its grain.
- **GA and NC metros:** OrdinanceWatch, GatherGov's top DC states, and Hamlet NC at 17.8%.

**Strategic reading:**
- The gap is not "no one covers the state". It is **no one shows, at town or township grain, that it read the posted agenda before the meeting**.
- In township states, that claim can be tested and published per place. Rivals' national claims (MultiState's townships, Spark's "township levels where public online sources exist") come without lists.

### Gaps
- Not run because the search budget ran out:
  - Hamlet rows for SC, TN and NJ.
  - Citizen Portal township and town checks for WI, MN and MI.
  - Citizen Portal checks for the Mountain West and northern New England beyond one query each.
- The Hamlet shares use mixed denominators: Census figures for some states, MyTownView plus [K] county counts for others. They are approximate.
- Whether MultiState, Quorum or FiscalNote actually monitor any PA/OH/MI/WI/MN township board cannot be seen without a demo. Quorum's 3,000-population floor excludes small townships, but their share was not measured.
- No state-specific commercial municipal-monitoring firm was found for PA, OH, MI, WI, MN, IA, NE, KS, MO, ME, NH or VT. Absence in search is not proof.
- Pages not reachable (HTTP 403 to the fetcher; not retried another way):
  - energyzoning.org (U-M database contents and counts)
  - documenters.org (current city list)
  - FiscalNote's Curate page
  - Civic IQ pages
- Build.inc's "live geofenced alerts for institutional real estate" (with Parallel) appeared in search, but its page returned 404. It is a possible rival for data-center developers, not assessed.
