# 351 Watch: which other local-government subjects to track, ranked by value

Run date: 2026-10-12. US only. About 35 minutes of web research, no accounts.

**Builds on, does not redo:**
- `research_notes/Meeting monitor national expansion/data_center_and_other_fights.md`. Its Q5–Q6 already scored data centers 4.5, on-site gas 4.3, transmission 4.1, warehouses 3.7, quarries 3.3, crypto 3.1, housing 2.9, CAFOs 2.8, CO2 pipelines 2.6 and lithium 2.3.
- `reports/Meeting monitor national expansion.md` (subjects section).

For subjects already scored there, this note reuses the score and adds only new facts: keywords, buyers and prices, and new numbers.

**Labels:**
- **[V]** verified on the cited page this session
- **[S]** secondary: news, a search summary, a vendor blog or a prior note
- **[E]** my estimate or arithmetic

**Scoring:** the same composite as the prior note, so the two tables can be merged. It weights stakes per decision 30%, frequency and growth 2025–27 25%, tracking gap at agenda grain 25%, and buyer willingness to pay 20%. Each factor is scored 1–5.

**Current matcher** (`projects/351watch/crawler/watch351/keywords.py`) has these topics: battery_storage, solar, moratorium, clean_energy_siting, 40b_comprehensive_permit, wireless_telecom, data_center (including crypto mining) and zoning_amendment. **It has no wind topic,** although the report sells "solar and wind siting" as core. That gap is fixed in the recommendations below.

---

## 1. Bottom line

1. **The best new subject is the money and utilities around large loads, not another facility type.** That means:
   - tax abatements, PILOTs, TIF and CRA/LERTA/ERA/bond-for-title deals, and Texas Chapter 312/380/381 agreements;
   - water, sewer and annexation agreements.

   Each decision carries $50M to $6B+ of public value. These items go through several boards (county, city, school board, development authority) weeks before the project is public, and the moratorium trackers do not count them. Evidence:
   - Sabey (Indianapolis): $49.5M + $36M abatements [V];
   - Independence, MO (Nebius): more than $6.2B of abatements requested [S];
   - Effingham, GA (OpenAI affiliate): 50% PILOT for 15 years [S];
   - Lima, OH: 20-year sale of 5–10 MGD of water [S].
2. **Most of the top 10 can be added as tags on agendas 351 Watch already reads.** Three need new source types:
   - Georgia, Virginia and Indiana development authorities and economic-development commissions;
   - school boards (Ohio CRA, Pennsylvania LERTA);
   - utility boards and groundwater districts.
3. **Nuclear/SMR siting is the fastest-growing item from a low base.** It appears in 2026 as:
   - county zoning text amendments (Campbell VA, Woodbury IA);
   - planning-commission study items (Green River UT);
   - "nuclear-ready" resolutions (Indiana's new program);
   - moratoria bundled with data centers and hydrogen (Saline KS).

   No local tracker was found.
4. **Short-term rentals, cannabis and housing reform are high-volume but low-value for paying buyers.** They suit the free tier as tags, not as paid lines.
5. **These subjects are fading or mostly decided at state or federal level:** hydrogen, offshore-wind landfalls, CO2 pipelines, lithium, broadband, airports and ICE detention. Leave them out, or keep them as free-tier tags only.

---

## 2. Per-subject findings

Format per subject: decisions per year · $ per decision · growth 2025→27 · who pays and what they pay now · early on agendas, and which board · existing local tracking · keywords and false positives.

### 2.1 Data-center incentive and tax deals (abatements, PILOTs, TIF, CRA, LERTA, ERA, bond-for-title, Ch. 312/380/381) — NEW, rank 1

**Decisions per year:** about 600–1,200 large-load fiscal actions nationally [E]. Basis:
- Cleanview's 2,522 planned data centers (prior note) × roughly 1–3 fiscal votes each over 2–3 years;
- several bodies vote on each deal: county, city, school district, development authority.

The expansion states (GA, IN, OH, PA, VA, MI, UT, ME) hold an estimated 35–45% of that [E]. A general "abatement" tag would also catch thousands of small non-data-center industrial abatements a year (Ohio CRA and Enterprise Zone, Indiana ERA, Michigan IFT), so a size filter is needed.

**$ per decision:**

| Deal | Value | Label and source |
|---|---|---|
| Sabey, Marion Co IN (Aug 19 2026) | 10-yr real-property abatement about $49.5M + 15-yr personal-property abatement $36M on a $2B campus | [V] [Bond Buyer, Sep 9 2026](https://www.bondbuyer.com/news/indiana-counties-response-to-data-centers-reflects-broader-political-risk) |
| St. Joseph Co IN (Amazon) | $11B; 50% abatement for 10 years; $143M community enhancement agreement | [S] [DCD](https://www.datacenterdynamics.com/en/news/st-joseph-county-leaders-approve-11bn-amazon-data-center-in-indiana) |
| Independence MO (Nebius) | More than $6.2B property-tax abatement + more than $330M sales-tax breaks on a $150B campus | [S] [Good Jobs First letter, Mar 2 2026](https://goodjobsfirst.org/?p=30290) |
| Guadalupe Co TX | $500M abatement denied 3-2 (Feb 24 2026); a commissioner wanted water use in writing | [S] [Community Impact](https://communityimpact.com/bastrop-cedar-creek/business/new-22b-cedar-creek-data-center-project-abatements-under-review/) |
| Effingham Co GA (OpenAI affiliate, about $20B) | IDA approved a PILOT of 50% of appraised value at the 2026 rate for 15 years | [S] [WTOC](https://www.wtoc.com/2026/07/30/effingham-county-data-center-deal-discount/); [AJC](https://www.ajc.com/news/2026/08/openai-in-georgia-how-20b-data-center-plan-secretly-took-root-in-effingham/) |
| Stanton Springs JDA GA | $42B bond to Baymare LLC (Feb 23 2026) | [S] [DCD](https://www.datacenterdynamics.com/en/news/new-900000-sq-ft-data-center-coming-atlanta-georgia-under-name-baymare-llc/) |
| Columbia Co GA | $17B deal; a November referendum on the incentive tool | [S] [WRDW](https://www.wrdw.com/2026/08/26/columbia-county-advances-17-billion-data-center-deal/) |
| Trenton OH (Prologis, 250 MW) | CRA abatement of 75% for 15 years (Jul 2026); residents petitioning a charter ban | [S] [WYSO](https://www.wyso.org/2026-07-09/trenton-approves-15-year-tax-abatement-for-data-center) |
| Wood Co OH ($750M data center) | 75% for 15 years; school districts approved first | [S] [BG Independent](https://bgindependentmedia.org/?p=81254) |
| Medina Co TX (CyrusOne, 244 acres) | Ch. 312 agreement effective Nov 3 2025 | [S] [Medina Co PDF](https://www.medinatx.gov/upload/page/0110/docs/Cyrusone%20Tax%20Abatemnt%20Agreement.pdf) |

**Growth 2025→27:** rising [E]. Signals:
- Fulton Co GA voted 5-0 to oppose data-center abatements and urged its development authorities not to grant them [S] — [Civic Atlanta](https://civicatlanta.org/blog/2026-08-09-fulton-commissioners-vote-to-oppose-data-center-tax-incentives).
- 25 of Indiana's 92 counties have data-center moratoria and 3 have bans, so every remaining deal is contested [V] — [Bond Buyer](https://www.bondbuyer.com/news/indiana-counties-response-to-data-centers-reflects-broader-political-risk).
- Good Jobs First says each of GA, TX, VA and OH may lose more than $1B a year to data-center exemptions [S] — [Register](https://www.theregister.com/2026/04/15/us_states_gaap_datacenters/).
- Estimated growth is +30–60% in contested fiscal votes [E].

**Who pays to know early:**
- data-center developers and their site selectors (which county will deal, and on what terms);
- municipal-bond investors and analysts (Bond Buyer now covers these deals as credit risk);
- bond and development-authority counsel;
- competing localities;
- utilities' economic-development teams.

**What they pay now:**

| Product | What it covers | Price | Label and source |
|---|---|---|---|
| Cleanview | Projects, not deals | $9k/yr | prior note |
| LocalGovIndex Professional | Agenda search, including a data-center dossier citing "$5B+ in investment stated in the record" | $399/mo | [V] [LocalGovIndex](https://localgovindex.com/) |
| FT Locations IncentivesFlow | Incentive deals recorded since 2010 | Unpublished | [S] [FT Locations](https://www.ftlocations.com/products-and-services/incentives-flow) |
| Conway Analytics (Site Selection) | Project database | Unpublished | [S] [Conway](https://conway.com/wp-content/uploads/2019/08/Conway-Analytics.pdf) |
| datacenterHawk, DC Byte | Data-center market intelligence | Unpublished, sales-led | [S] [CB Insights](https://www.cbinsights.com/compare/datacenterhawk-vs-dc-byte) |
| Good Jobs First Subsidy Tracker | Post-hoc subsidy records | Free | — |

**Early on agendas? Yes, and often first.** Before construction, and often before the end user is named, these items appear as:
- **TX:** reinvestment-zone and abatement notices on commissioners-court agendas, as with Haskell Co's "Ranger RZ 2026" notices for Feb 10 and Feb 24 2026 [S] — [Haskell notice](https://www.haskellcountytx.gov/upload/page/7687/Agenda%20Amended%20Notice%20of%20Consideration%20of%20Tax%20Abatement%20Agreement%20Final.pdf). The Comptroller publishes Ch. 380 agreements [S] — [example](https://assets.comptroller.texas.gov/dat/ch380/0003113/0003113-Dallas.pdf).
- **OH:** CRA agreements need school-board agreement when schools get under 50% of forgone taxes, so the school board is an earlier venue [S] — [Bricker](https://www.bricker.com/insights/publications/Ohio-General-Assembly-considering-significant-CRA-law-change-during-lame-duck-session).
- **PA:** LERTA needs ordinances from the township, the county and the school district: three agendas [S] — [PMEDC](https://www.pmedc.com/properties/lerta/).
- **GA:** development-authority inducement resolutions and bond validations.
- **IN:** ERA declaratory and confirmatory resolutions at county or city council, or Indianapolis's MDC.
- **MI:** IFT/PA 198 district hearings. Data centers need a local resolution to stack PA 198 on the state exemption [S] — [MEDC guidelines](https://www.michiganbusiness.org/globalassets/documents/data-center/enterprise-data-center-guidelines.pdf).

**Existing local tracking:**
- Good Jobs First (advocacy, post-hoc);
- LocalGovIndex (agenda search, not deal-structured);
- local press.

No deal-level, pre-vote tracker was found [S, negative search].

**Keywords:**
- *General:* abatement, "tax abatement", "payment(s) in lieu of taxes", PILOT, PILT, "tax increment", TIF, TID, "reinvestment zone", "community reinvestment area", "enterprise zone", "economic revitalization area", "statement of benefits", "declaratory resolution", "confirmatory resolution", "community enhancement agreement", "host community agreement", "development agreement", "performance agreement".
- *State-specific:* LERTA, KOZ, "industrial facilities exemption", IFT, "PA 198", "bond-for-title", "bond validation", "inducement resolution", "Chapter 312", "Chapter 380", "Chapter 381", JETI, "credit enhancement agreement" (Maine TIF), "computer equipment" tax rate (VA), "qualified energy project" (Ohio solar PILOT).

**False positives:**
- "pilot program" and "pilot project": PILOT must be all caps or followed by "payment" or "agreement";
- routine residential CRA and TIF items, and homestead abatements;
- "TIF" in budget line items.

Fix: require co-occurrence with data_center, MW, "megawatt", "campus", an acreage of 50 or more, or "$… million/billion".

### 2.2 Water, sewer, annexation and utility-service agreements for large loads (including groundwater and municipal-utility power) — NEW, rank 3

**Decisions per year:** about 150–400 data-center-linked actions nationally [E]: annexations, water and wastewater sale agreements, outside-user agreements and groundwater permits. Routine annexations run into the thousands and need filtering.

**$ per decision:**

| Case | Terms | Label and source |
|---|---|---|
| Lima OH | 6-2 vote for a 20-year water sale to Project BOSC, 5 MGD expected, up to 10 MGD | [S] [Hometown Stations](https://www.hometownstations.com/news/allen_county/lima-city-council-approves-water-deal-for-american-township-data-center/article_14f3a9b2-fcea-4cc9-b1e1-514400b31893.html) |
| Amarillo TX (Fermi America) | Up to 5.5 MGD; council vote set for Oct 28 2026 | [S] podcast summary, verify on the agenda |
| Ridgeland MS (Amazon) | Up to 3.67 MGD | [S] [Mississippi Free Press](https://www.mississippifreepress.org/inside-the-private-deal-between-amazon-and-ridgelands-water-system/) |
| Taylor TX | 664-acre data center + on-site power-plant annexation (Oct 2026) | [S] [KUT](https://www.kut.org/energy-environment/2026-10-09/taylor-tx-annex-data-center-power-plant) |
| Temple TX | About 302-acre annexation, rezoning and utility agreement (Apr 2026) | [S] [KXXV](https://www.kxxv.com/news/local-news/in-your-neighborhood/bell-county/temple/temple-city-council-approves-water-service-agreement-for-data-center) |
| Port Washington WI | About 2,000-acre city-town agreement | [S] [Ozaukee Press](https://ozaukeepress.com/content/city-town-ink-land-deal-data-centers) |
| Gallup NM | 4-1 vote to delay a deal for about 110M gal/yr of wastewater | [S] [Source NM](https://sourcenm.com/2026/04/29/gallup-city-council-punts-decision-on-wastewater-agreement-with-proposed-nm-data-center-project/) |
| Cheyenne WY | Pre-annexation outside-user agreement for city water and sewer | [S] [WTE](https://newslj.com/cheyenne-city-council-delays-annexation-data-center-until-september) |
| King George VA (Amazon) | Groundwater permit withdrawn | [S] [Virginia Mercury](https://virginiamercury.com/2026/08/26/amazon-changes-course-on-water-use-for-king-george-data-center-campus/) |
| Virginia statewide | A DEQ study found no evaluated region could support a 3 MGD groundwater withdrawal | [S] [DCK](https://www.datacenterknowledge.com/data-center-site-selection/virginia-report-finds-groundwater-running-dry-for-new-data-centers) |
| Polk Co TX | Resolution and draft groundwater-permit policy aimed at data centers | [S] [Brazos Valley GCD](https://brazosvalleygcd.org/2026/08/polk-county-hears-groundwater-briefing-adopts-resolution-and-draft-permit-policy-aimed-at-data-center-impacts-citizen-portal/) |

**Growth:** rising. Water has become the second line of attack after zoning, as in Guadalupe's abatement vote above [E].

**Who pays:**
- data-center developers, who need water and sewer capacity before closing on land;
- site selectors;
- water-utility investors and engineers;
- the same platform licensees (Heatmap, Cleanview), which track projects but not utility deals.

Prices are the same anchors as 2.1.

**Early on agendas? Yes, usually before any zoning item where land is annexed into a city.** Boards involved:
- city council and public-works or utility committees;
- municipal utility boards and water commissions (a new source in some cities);
- Texas groundwater conservation districts and MUD creation (new sources);
- Michigan PA 425 conditional land-transfer agreements (township and city boards);
- Ohio JEDD/CEDA agreements and Type 2 annexations (township trustees and county commissioners).

**Existing local tracking:** none found [S, negative search].

**Keywords:** annexation, "pre-annexation", "425 agreement", "conditional land transfer", JEDD, CEDA, "water service agreement", "utility service agreement", "wastewater agreement", "outside user", "extraterritorial", "capacity reservation", "million gallons per day", MGD, "groundwater withdrawal", "water withdrawal permit", "electric service agreement", "large load".

**False positives:**
- routine residential annexations;
- small water-main extensions;
- "MGD" in WWTP operating reports.

Fix: require co-occurrence with data_center, MW, an acreage of 100 or more, or industrial/campus.

### 2.3 Large industrial rezonings, megasites and comprehensive/master-plan amendments (including semiconductor and battery gigafactories) — NEW, rank 5

**Decisions per year:**
- 200+ acre industrial rezonings: estimated in the low hundreds a year nationally [E];
- comprehensive/master/general-plan amendments: thousands, mostly small [E].

**$ per decision:**
- **Pittsylvania VA (Berry Hill, Jan 2026):** new by-right heavy-industrial district on about 3,500 acres that allows data centers and power generation; planning commission and board voted unanimously at one joint meeting [S] — [Cardinal News](https://cardinalnews.org/2026/01/16/rezoning-will-allow-for-more-heavy-industrial-developments-at-pittsylvania-county-megasite/).
- **Pitt Co NC:** about 3,320 acres for a $451M project (2025) [S] — [WITN](https://www.witn.com/2025/06/19/pitt-county-board-approves-rezoning-451m-megasite-project).
- **Lorain Co OH, New Russia Twp:** 622 acres (Mar 2026) [S] — [Hoodline](https://hoodline.com/2026/03/lorain-mega-site-uproar-has-county-scrambling-for-cover/).

**Growth:** mixed.
- Clean-tech manufacturing is shrinking. E2 counts 2025 cancellations and downsizing at about $34.8B ($30.2B of it manufacturing), and 28 EV and battery projects cancelled, closed or downsized since 2025 [S] — [E2 memo](https://e2.org/wp-content/uploads/2026/02/E2-Clean-Economy-Works-December-Year-End-Analysis-Memo-vfinal.pdf).
- Megasites are being re-zoned for data centers plus power (Pittsylvania), so the subject persists under a new end use [E].

**Who pays:**
- site selectors and industrial land brokers;
- economic-development organizations;
- utilities' economic-development teams;
- construction-lead buyers.

**What they pay now:**
- Conway, unpublished [S];
- ConstructConnect Starter $129/mo per market and seat, Professional from $199/mo, Premium from $10k/yr. This comes from a competitor's guide [S] — [ConstructionBids.ai, Oct 6 2026](https://constructionbids.ai/blog/constructconnect-pricing-guide-2026).
- Dodge is quote-only; third parties cite about $3k+/yr or $300/user/mo [S] — [SelectHub](https://www.selecthub.com/construction-bidding-software/constructconnect-vs-dodge-data-and-analytics/).
- BuildCentral ("early-stage" leads) charges per user, price unpublished [S] — [Capterra](https://www.capterra.co.za/software/218776/build-central).

**Early on agendas? Yes.** A comprehensive-plan or future-land-use amendment usually precedes the rezoning by months. Prince William's Digital Gateway started as one (prior note).

**Boards:** planning commission/board, governing body, and in GA the regional commissions' DRI review (the report notes it is robots-closed).

**Existing local tracking:**
- Dodge, ConstructConnect and BuildCentral cover planning-stage projects, not plan or text amendments.
- No tracker keyed to acreage or plan amendments was found.

**Keywords:** megasite, "mega site", "comprehensive plan amendment", "future land use", "master plan amendment" (MI), "general plan amendment" (UT), "heavy industrial", "advanced manufacturing", gigafactory, semiconductor, "battery cell", plus an acreage parser (a number of 100 or more followed by "acres", near rezone or industrial).

**False positives:**
- park and trail master plans;
- annual comprehensive-plan reviews;
- "fab" (do not use).

### 2.4 On-site gas plants and fuel cells — prior score 4.3, rank 2

New facts only:
- **Fauquier VA:** rezoning for on-site gas fuel cells (prior note).
- **Indiana Michigan Power:** a 1,520 MW gas plant at Rockport, with nuclear also under evaluation [S] — [Indiana Capital Chronicle](https://indianacapitalchronicle.com/2026/07/23/indiana-officials-aim-to-inspire-nuclear-development-starting-with-local-level-support/).
- **Indiana SB 425:** would let utilities swap coal for gas or an SMR on the same parcel without rezoning [S, same source]. That would remove some local decisions in Indiana.

**Keywords:** "natural gas" near (plant|generation|generating|turbine|power), "combined cycle", "combustion turbine", "simple cycle", peaker, "reciprocating engine", "fuel cell", "behind-the-meter", "on-site generation", "power plant", "generating facility".

**False positives:**
- **Ohio municipal "natural gas aggregation" programs**, which appear on most Ohio council agendas;
- gas-station items;
- "fuel cell" vehicle purchases.

### 2.5 Transmission lines and substations — prior score 4.1, rank 4

New fact: Fairfax VA's Edsall Road data-center substation faces a "2232" public-facilities review. It would serve 176 MW, is due to be energized Oct 2027, and its Planning Commission hearing was moved to Dec 2. A supervisor and a congressman asked the commission to deny it [S] — [FFXnow](https://www.ffxnow.com/2026/08/07/mason-district-supervisor-asks-planning-commission-to-reject-data-center-substation/).

That makes **Virginia's § 15.2-2232 review** the local decision point for substations, and "2232" a precise Virginia keyword.

**Keywords:** substation, "transmission line", "\d{2,3} ?kV", CPCN, "certificate of public convenience", "2232", "right-of-way" near (electric|transmission), "switching station", "switchyard".

**False positives:**
- **"police substation" and "fire substation"**, which are common;
- distribution-line easements;
- "kV" in streetlight bids.

### 2.6 Nuclear and SMR siting — NEW, rank 6

**Decisions per year:** about 20–60 local items in 2026 [E], likely 50–150 by 2027 [E]. Examples:

| Place | Item | Label and source |
|---|---|---|
| Campbell Co VA | "Industrial intensive" district that would allow SMRs by right at Appalachian Power's Joshua Falls site; board hired experts first (Jul 2026); reactor expected mid-2030s | [S] [WDBJ](https://www.wdbj7.com/2026/07/07/campbell-county-supervisors-discuss-zoning-change-that-would-allow-small-nuclear-reactors/) |
| Woodbury Co IA | Text amendment making nuclear facilities and waste storage conditional uses, with 10-mile notice (2025) | [S] [Woodbury PDF](https://www.woodburycountyiowa.gov/files/meeting_assets/zoning_ordinance_text_amendments_for_nuclear_energy_2025-07-01_60188.pdf) |
| Green River UT | Planning and zoning agendas of Jul 21 and Aug 18 2026: "Discuss Nuclear Reactors" alongside "Discuss Data Centers" | [S] search summary |
| Brigham City UT | Fight over clustering SMRs nearby (Jul 2026) | [S] [Hoodline](https://hoodline.com/2026/07/nuclear-showdown-in-brigham-city-as-data-center-power-demand-soars/) |
| Eagle Mountain UT | Energy overlay vote, including nuclear, delayed | [S] [Deseret](https://www.deseret.com/utah/2025/12/17/eagle-mountain-delays-nuclear-energy-vote/) |
| Utah (state) | HB249 lets counties seek "electrical energy development zones" through the Utah Energy Council | [S] [Yahoo/Deseret](https://www.yahoo.com/news/more-local-input-legislature-signs-130252403.html) |
| Indiana (state) | Advanced Nuclear Ready Community program (Jul 2026) courts counties; 2025 SB 424 reportedly caps local moratoria at one year | [S] [Indiana Capital Chronicle](https://indianacapitalchronicle.com/2026/07/23/indiana-officials-aim-to-inspire-nuclear-development-starting-with-local-level-support/) |
| Saline Co KS | 3-year moratorium on data-center, nuclear and hydrogen facilities | [S, prior note `energy_siting_hotspots.md`] |
| Arizona (state) | 2026 bills to preempt county zoning of SMRs | [S] [AZ HB2456](https://www.azleg.gov/legtext/57leg/2R/bills/HB2456H.htm) |

**$ per decision:** multi-billion per site [E; no 2026 cost figure verified].

**Growth:** the steepest of any subject, from a small base [E].

**Who pays:**
- SMR developers and utilities;
- hyperscalers co-locating with them;
- **public-equity investors in listed nuclear names**, for whom alternative data on site support or opposition is tradable [E];
- counsel.

No priced local product was found. Heatmap Pro sells "clean energy project opposition" in every county, but its page does not name nuclear [S] — [Heatmap Pro](https://heatmap.news/pro).

**Early on agendas? Yes:** text amendments, resolutions of support, energy-zone applications, and planning-commission study items before any NRC filing. Boards are the county board, planning commission and city council.

**Existing local tracking:** none found.

**Keywords:** nuclear (near reactor|energy|facility|power|generation), "small modular reactor", SMR, microreactor, "advanced reactor", "nuclear ready", "energy development zone".

**False positives:**
- **"nuclear density gauge"** (Troxler gauges in road-construction contracts);
- "nuclear medicine";
- radiological emergency planning (REP), KI tablets and sirens, which counties near existing plants approve routinely;
- "SMR", which needs nuclear context.

### 2.7 Referendums, petitions and recalls on siting decisions — NEW (cross-subject), rank 7

**Decisions per year:** tens nationally [S/E].
- Ballotpedia counts at least five local data-center ballot measures in 2026 [V] — [Ballotpedia](https://news.ballotpedia.org/2026/03/19/voters-in-at-least-five-jurisdictions-will-decide-ballot-measures-related-to-data-centers-in-2026/):
  - Boulder City NV (rezoning);
  - Monterey Park CA (ban);
  - Augusta Twp MI (522.2-acre rezoning);
  - Port Washington WI (TIF);
  - Janesville WI (projects over $450M).
- It also names proposed measures in Marana AZ, Frederick Co MD, Festus, Joplin and Independence MO, and Wilmington OH.
- Augusta voters overturned the rezoning by about 90% (Aug 2026), and recall petitions followed [S] — [WEMU](https://www.wemu.org/wemu-news/2026-08-05/augusta-township-voters-overturn-data-center-rezoning).
- Ohio township zoning referenda under SB 52 apply to solar and wind (report).

**$ per decision:** the whole project, often $1B or more [E].

**Who pays:** developers and investors, who need to know the moment a petition is filed or certified.

**Early on agendas? Yes:** the clerk's petition certification and the board's ballot-placement resolution come 60–120 days before the vote.

**Existing tracking:** Ballotpedia, after certification.

**Keywords:** referendum, "referendum petition", "petition to place", "ballot question", "ballot measure", "certif(y|ication) of petition", "initiative petition", recall.

**False positives:** **school levies, millage renewals and bond referenda** (very common in MI and OH). Require co-occurrence with zoning, data_center, solar, wind, battery or a rezoning ordinance number.

### 2.8 Warehouses and logistics, plus truck stops and travel centers — prior warehouse score 3.7; combined rank 8

New facts:
- **Truck stops are frequent, contested rezonings:**
  - Vanderburgh Co IN commissioners unanimously denied a Love's rezoning after a 7-3 plan-commission recommendation to deny (date unconfirmed) [S] — [Inside Indiana Business](https://insideindianabusiness.com/?p=160292);
  - Louisa Co VA Love's denial (older) [S] — [Central Virginian](https://www.thecentralvirginian.com/news/bos-votes-to-deny-request-from-love-s-travel-stop/article_aba81a42-6a71-11ef-973c-afccbee46162.html);
  - Monument CO Buc-ee's fight (Aug 2026) [S] — [Gazette](https://gazette.com/2026/08/06/monument-weighs-in-on-buc-ees-zoning-question-1/).
- **Volume:** an estimated 150–300 truck-stop and travel-center approvals a year [E].
- **$ per site:** about $10–30M; Buc-ee's more [E].
- **EV truck-charging hubs:** mostly ministerial in California and low-conflict elsewhere [S] — [CEQAnet](https://ceqanet.lci.ca.gov/2026040810). Low value; fold into this tag.

**Who pays:**
- fuel retailers' site teams;
- industrial and logistics developers;
- construction-lead buyers (ConstructConnect and Dodge prices above).

**Keywords:** warehouse, "distribution center", "fulfillment center", logistics, "truck terminal", "high-cube", "travel center", "travel plaza", "truck stop", "truck parking", "fueling station", "megawatt charging", "truck charging".

**False positives:**
- **"pilot program"** (do not key on Pilot alone);
- DPW salt and storage sheds;
- municipal EV-charger grants.

### 2.9 Wind siting and decommissioning/bond rules — partly NEW, rank 9

**Wind is missing from the matcher.** Wind-energy-conversion-system ordinances are core in MI, OH and IN, and SB 52 restricted areas cover wind. Fix this regardless of rank.

**Decommissioning and bond decisions:**
- **Pennsylvania Act 44 of 2026** (signed Jul 20 2026) preempts municipal solar decommissioning rules for facilities over 2 MW from January 2027. Its financial-security terms are phased in and are more lenient than most ordinances [S] — [PSATS](https://www.psats.org/governor-signs-act-that-will-invalidate-municipal-solar-decommissioning-ordinances/).
- Pennsylvania townships with solar ordinances must amend or repeal them, for example Reading Twp's Oct 19 2026 hearing (report). That implies roughly 100–300 PA hearings in 2026–27 [E].
- **Virginia § 15.2-2241.2**, the bonding statute for solar decommissioning, was updated in 2026 [S] — [Va. Code](https://law.lis.virginia.gov/vacodeupdates/title15.2/section15.2-2241.2/).

**$ per decision:** about $1–10M of financial security per facility [E].

**Who pays:**
- solar, BESS and wind developers and their counsel;
- surety underwriters;
- landowners.

This feeds the report's proposed $1,500/yr State Decision Ledger.

**Existing tracking:** none local. PSATS alerts members.

**Keywords:**
- *Wind:* "wind energy (conversion|facility|system)", WECS, "wind turbine", "wind farm", "wind (energy )?overlay".
- *Decommissioning:* decommission\w*, "financial (security|assurance)", "surety bond", "decommissioning (bond|plan|escrow)", "siting agreement" (Va. § 15.2-2316.7), "qualified energy project" (OH).

**False positives:**
- "wind" alone (weather, windows); use the phrases above;
- "decommissioning" of wells and water tanks; require solar, wind or BESS context.

### 2.10 Quarries, sand and gravel — prior score 3.3, rank 10

New facts:
- **Allen Co IN BZA (May 2026):** special-use denial for a quarry on about 524 acres of a 1,600-acre site, with 55 speakers against and 1 for. The developer's attorney says state law lets it proceed anyway [S] — [Journal Gazette](https://www.journalgazette.net/local/southwest-allen-county-quarry-question-might-not-be-settled-after-all/article_a2e8fca0-c50a-4ea1-90d4-977467cc263a.html).
- **Jefferson Co NY:** county planning board referral items [S] — [CPB minutes](https://www.jeffersoncountyny.gov/media/Planning/CPB/MEETING%20MINUTES%2006302026.pdf).

**Buyers:** aggregate majors' land teams (large firms, few seats), plus road and data-center contractors. No priced local tracker was found.

**Keywords:** quarry, "sand and gravel", "gravel pit", "mineral extraction", "surface mining", "earth removal" (MA), "aggregate(s)? (mining|operation|extraction|quarry)".

**False positives:** **"in the aggregate" or "aggregate amount"** in budgets and bonds. Never key on "aggregate" alone.

### 2.11 Below the line, in order of composite score

| Subject | Decisions/yr | $ per decision | Growth 25→27 | Who pays now (product, price) | Early on agendas? Board | Local tracker? | Keywords / false positives | Composite |
|---|---|---|---|---|---|---|---|---|
| **RNG and anaerobic digesters** | About 100–150 approvals/yr [E], from the North American pipeline of 500 operating, 153 under construction and 293 planned [S — [CCJ](https://www.ccjdigital.com/alternative-power/natural-gas/article/15748922/rng-coalition-announces-500th-operational-facility)] | About $20–100M [E] | Up (goal of 1,000 operating by 2030) | RNG developers and offtakers; RNG Coalition map (members); no local product | Yes: township and county CUP or rezoning. Cases: Winneshiek IA 3-2 against its P&Z [S — [Gazette](https://www.thegazette.com/news/agriculture/winneshiek-supervisors-decline-to-block-manure-digester/article_3ed21025-08d2-523d-938e-123713c32760.html)]; Bath Twp OH BZA cease-and-desist [S]; Freedom Twp MI Vanguard [S — [WEMU](https://www.wemu.org/wemu-news/2025-10-23/anaerobic-biodigesters-raise-a-stink-in-freedom-township)] | None | digester, "anaerobic digest", biogas, "renewable natural gas", RNG, biomethane. **FP: WWTP sludge digesters** (exclude sewer, WWTP, treatment-plant context) | **3.1** |
| **Landfills and waste-to-energy** | About 50–100 expansion or siting decisions/yr among 1,637 active MSW landfills [S — [EREF](https://erefdn.org/?p=3184)] [E] | Campbell VA expansion saves $30–40M over 24 years and extends life from 2029 to 2054; 4-3 denial Jan 2025 [S — [WDBJ](https://www.wdbj7.com/2026/08/11/nelson-county-accepts-campbell-county-landfill-deal/)] | Flat | Waste majors' M&A teams, landfill-gas developers; Waste Business Journal (price not found) | Yes: solid-waste plan amendments (MI Part 115), host agreements (PA Act 101), VA certificates of consistency and CUPs | None | landfill near (expansion, cell, permit, rezone, CUP), "solid waste (management )?plan amendment", "host (community )?agreement", "waste-to-energy". **FP: tipping fees and landfill operating budgets** | **3.0** |
| **Hydrogen and e-fuels** | Few | Large | Short rush, then a cliff: 45V requires construction to begin before Jan 1 2028 [S — [GH2](https://gh2.org/blog/us-hydrogen-policy-crossroads-updated)]; DOE ended 321 grants worth $7.56B in Oct 2025, then kept about $5B for five hubs (Apr 2026) [S — [Planetizen](https://www.planetizen.com/node/136099)] | Developers; none local | Mostly inside bundled moratoria (Saline KS) | None | hydrogen, electrolyzer, "e-fuel", "sustainable aviation fuel". FP: "hydrogen sulfide" (odor complaints) | 2.85 |
| **Offshore-wind landfall and cable routes** | Very few in the expansion states (VA, ME) | $B per project | Down under the 2025–26 federal posture | Developers; heavily covered by press and advocates | Yes: town easements and select boards (Falmouth MA [S — [Cape News](https://www.capenews.net/falmouth/news/falmouth-town-meeting-to-vote-on-mayflower-wind/article_cd32a08f-7658-58bf-8f64-a5efca079f56.html)]; Virginia Beach Sandbridge [S]) | Press | "offshore wind", "cable landing", "export cable", "landfall" | 2.65 |
| **Car-wash and gas-station moratoria** (found in passing) | Dozens/yr [E]: Warren MI 8 months (May 19 2026) [S — [Warren flyer](https://www.cityofwarren.org/wp-content/uploads/2026/06/Car-Wash-Gas-Station-Moratorium-Flyer.pdf)]; Mission TX 6 months [S — [KRGV](https://www.krgv.com/news/we-have-enough-mission-puts-temporary-hold-on-new-car-washes/)] | About $5–8M/site [E] | Up | PE-backed car-wash roll-ups' site teams | Yes: council moratoria | None | "car wash" + moratorium (already caught by the moratorium tag) | 2.5 |
| **EV charging hubs** | Few dozen | $5–30M | Slowed | Charging developers | Often ministerial (LA County) [S] | None | Folded into 2.8 | 2.5 |
| **Cannabis siting** | OH: 125 active / 149 municipalities with moratoria as of Feb 10 2026 (page inconsistent) [S — [OSU Moritz](https://moritzlaw.osu.edu/faculty-and-research/drug-enforcement-and-policy-center/research-and-grants/policy-and-data-analyses/ohio-marijuana-moratoriums)]. VA: General Assembly passed a retail bill (Senate 21-18 on Mar 13, House 64-32) that gives localities zoning control but no referendum opt-out; governor's signature not verified [S — [VA Lawyers Weekly](https://valawyersweekly.com/2026/03/16/virginia-approves-cannabis-retail-market-bill-passed/); [Virginia Mercury](https://virginiamercury.com/2026/02/17/virginia-general-assembly-advances-cannabis-retail-framework/)], so about 133 VA localities would write zoning in 2026–27 [E]. PA not legal (Senate resistance) [S — [PhillyVoice](https://www.phillyvoice.com/pennsylvania-marijuana-legalization-2026-shapiro-cannabis/)]. MI and ME are mature; GA, IN and UT have no adult use | About $1–5M/store [E] | Up in VA, flat elsewhere | MSOs and brokers. Cannabiz Media regional upgrade $1,000/yr [S — [Cannabiz](https://cannabiz.media/cannabiz-media-announces-free-regional-subscriptions-for-cannabis-license-holders/)]; CannaRegs (local rules) price unpublished [S] | Yes: council and planning zoning text | OSU (OH), CannaRegs | cannabis, marijuana, dispensar\w+, "adult-use". FP: police-report and drug-enforcement items | 2.45 |
| **Short-term rental rules** | About 300+/yr nationally [E, from a vendor roundup of more than 12 jurisdictions in about 2 weeks — [RedAwning](https://redawning.com/pm/post/short-term-rental-regulation-updates-september-2026)]; heavy in ME coast, MI resort townships, UT resort towns | Low per decision | Steady | STR investors and managers: AirDNA $19–99/mo (older case study) [S — [HBS Digit](https://d3.harvard.edu/platform-digit/submission/airdna-smarter-short-term-rental-pricing-with-artificial-intelligence/)] (pricing page returned 403); Granicus Host Compliance (sold to governments) | Yes: council and planning | Many vendor blogs | "short-term rental", STR, "transient rental", "vacation rental". FP: "STR" street abbreviation | 2.45 |
| **ICE detention sites** | Tens/yr in 2026 | Purchases about $100–130M per warehouse (prior note) | Up in 2026 | No payer (journalists and advocates) | Council resolutions (Roxbury NJ, Merrillville IN, Washington Co MD) [S — [Wikipedia table](https://en.wikipedia.org/wiki/ICE_detention_expansion_plan)]; local zoning preempted | Press, Wikipedia | "detention (center|facility)", ICE, "immigration". FP: stormwater "detention basin" or "detention pond" (very common) | 2.35 |
| **Broadband and pole attachments** | Many (franchises, ROW, BEAD subgrants) | Small locally | Flat | ISPs (not 351 Watch's buyers) | Council consent items | State BEAD offices | "pole attachment", "broadband" + franchise or ROW | 2.05 |
| **Flock/ALPR camera contracts** (found in passing) | 1,700+ cities and counties in 48 states, "$180M+" in the record [V — LocalGovIndex homepage dossier] | Small | Up | Advocates and vendors | Council consent agendas | **LocalGovIndex already has a dossier** | — | 2.0 |
| **Airports and heliports** | Few | Varies | Flat | Aviation developers | Airport authorities (new source) | FAA | heliport, vertiport, "airport layout plan" | 1.8 |

Prior-note scores stand for crypto 3.1 (keep inside data_center), housing 2.9 (keep 40B in MA/RI; ADU and missing-middle as a free-tier tag), CAFOs 2.8, CO2 pipelines 2.6 and lithium 2.3. For CAFOs, **"CFO" also means Chief Financial Officer**, so never key on the bare abbreviation; use "confined (animal )?feeding", CAFO, "livestock facility".

---

## 3. Ranking: top 10 to add, in order

The composite uses the prior note's weights. Scores marked † come from the prior note.

| Rank | Subject | Stakes | Freq/growth | Gap | WTP | **Composite** | How to add |
|---|---|---|---|---|---|---|---|
| 1 | **Large-load incentive and tax deals** (abatement, PILOT, TIF, CRA, LERTA, ERA, bond-for-title, Ch. 312/380/381) | 5 | 4 | 4 | 5 | **4.50** | **Tag** on council, county and commissioners-court agendas already read. **New sources** for full value: GA and VA development authorities and IDAs, Indianapolis MDC, OH and PA school boards, TX Comptroller Ch. 380/312 registries |
| 2 | On-site gas and fuel cells † | 5 | 3 | 5 | 4 | **4.30** | **Tag** (same planning and township agendas) |
| 3 | **Water, sewer, annexation and utility-service agreements** (including groundwater, PA 425, JEDD/CEDA) | 4 | 4 | 5 | 4 | **4.25** | **Tag** on council agendas. **New sources:** municipal utility and water boards, TX groundwater districts |
| 4 | Transmission and substations † (including VA "2232" reviews) | 5 | 3 | 5 | 3 | **4.10** | **Tag**. State dockets (SCC, PUC) are a later, separate source |
| 5 | **Large industrial rezonings, megasites and comprehensive/master-plan amendments** (including gigafactories) | 4 | 4 | 4 | 4 | **4.00** | **Tag**, plus an acreage parser on zoning items already matched |
| 6 | **Nuclear and SMR siting** (text amendments, nuclear-ready resolutions, energy zones) | 5 | 2 | 5 | 3 | **3.85** | **Tag**. Optional later: Utah Energy Council, NRC dockets |
| 7 | **Referendums, petitions and recalls on siting decisions** | 5 | 2 | 4 | 4 | **3.80** | **Tag** (co-occurrence rule); Ballotpedia as a cross-check |
| 8 | Warehouses and logistics † plus truck stops and travel centers | 3 | 4 | 5 | 3 | **3.70** † | **Tag** |
| 9 | **Wind siting (missing today) plus decommissioning, bonds and state-preemption labels** | 3 | 3 | 4 | 4 | **3.45** | **Tag**. A matcher fix plus State Decision Ledger labels |
| 10 | Quarries and aggregates † | 3 | 3 | 5 | 2 | **3.30** † | **Tag** |

**Next in line:** RNG digesters 3.1, landfills 3.0, hydrogen 2.85, offshore wind 2.65, car washes 2.5, EV hubs 2.5, cannabis 2.45, STR 2.45, ICE detention 2.35, broadband 2.05, Flock/ALPR 2.0, airports 1.8.

### Cheap tags vs new sources

- **All ten can start as tags on agendas already read.** Items 2, 4, 5, 6, 7, 8, 9 and 10 need no new sources at all. Each needs:
  - a regex group in `keywords.py`;
  - the false-positive rules listed above;
  - for 1, 3, 5 and 7, a co-occurrence or size rule (MW, "megawatt", data center, an acreage of 50–100+, or "$… million/billion").
- **Items 1 and 3 reach full value only with new source types:**
  - **development authorities and EDCs** (GA IDAs/JDAs such as Effingham and Stanton Springs; VA EDAs/IDAs; Indianapolis MDC);
  - **school boards** (OH CRA consent below the 50% threshold; PA LERTA's three-body approval);
  - **utility and water boards and TX groundwater conservation districts**;
  - **state registries:** TX Comptroller Ch. 380/381 and Ch. 312 registries, and MI State Tax Commission IFT approvals.

  Development authorities and school boards often use the same CivicPlus/BoardDocs/Simbli platforms as the counties, so the adapter cost is mostly discovery, not code [E].
- **Cheap tags for the free tier only** (low paid value, high resident interest): cannabis (OH, VA), STR (ME, MI, UT), housing reform (ADU, by-right), car-wash moratoria, ICE detention resolutions.

### State-specific labels worth adding with these tags (expansion states)

- **MI:** PA 425 agreement, IFT/PA 198, solar PILT, "master plan amendment", township zoning referendum petition.
- **OH:** CRA, Enterprise Zone, JEDD/CEDA, Type 2 annexation, QEP PILOT, township zoning referendum (ORC 519.12), adult-use cannabis moratorium (ORC 3780.25).
- **PA:** LERTA, KOZ, curative amendment, Act 44 decommissioning repeal, Act 101 host agreement.
- **IN:** ERA, statement of benefits, declaratory/confirmatory resolution, community enhancement agreement, Nuclear Ready Community.
- **VA:** 2232 review, siting agreement (§ 15.2-2316.7), performance agreement, computer-equipment tax rate, comprehensive-plan amendment, cannabis retail zoning.
- **GA:** bond-for-title, bond validation, inducement resolution, PILOT, DRI.
- **UT:** CRA project area, energy development zone (HB249), general-plan amendment, moderate-income housing report.
- **ME:** TIF credit enhancement agreement, town-meeting warrant article, STR ordinance.

---

## 4. Gaps and caveats

- **Decision counts are estimates.** No national count of data-center abatements, annexations or water deals exists. The best next step is to run the proposed regexes over the existing 351 Watch and NY/RI pilot corpora and count real hits per 1,000 agendas.
- **Most buyer prices are unpublished:** Heatmap Pro, IncentivesFlow, Conway, DC Byte, datacenterHawk, CannaRegs, Waste Business Journal and BuildCentral. The ConstructConnect figures come from a competitor's guide. AirDNA's pricing page returned 403.
- **Two pages could not be read.** The OSU Moritz cannabis page (403) gives two different counts on one page. The LocalGovIndex homepage was read, but its `/issues` index returned 404, so other dossiers may exist that were not listed.
- **Not verified:** whether Virginia's governor signed the cannabis bill, the final text of Indiana SB 424/425, and the Amarillo vote (Oct 28).
- **No 2026 cost per SMR, RNG plant or quarry was verified.** Those $ figures are labelled [E].
