# Where 351 Watch wins: segments, offers, regions and the next ten features

Prepared Oct 10–11, 2026 for the 351 Watch owner. It builds on, and does not repeat, `reports/Meeting monitor deep dive.md` and the notes in `research_notes/Meeting monitor deep dive/` and `research_notes/Meeting monitor validation/`. New this session: 24 web searches and about 25 page fetches covering the competitors and buyer workflows the brief named, plus a re-analysis of 351 Watch's own data files. Constraint carried throughout: **no email outreach**. Every acquisition path below runs through the product, public pages, feeds, integrations, partnerships or communities.

**Labels**
- **[V]** verified: read this session on a primary source, or verified in an earlier note and cited to it.
- **[R]** reported: a third-party summary, aggregator, search snippet or vendor claim about a rival.
- **[I]** inference: my judgment, or arithmetic on cited figures.
- **[K]** background knowledge, not checked this session.

---

## Decision summary

1. **Win first with Massachusetts community-scale solar and battery (BESS) developers, sold as a team plan that their permitting engineers and counsel join for free.** The demand is real: 54 firms have 3 or more siting-relevant MA projects [V, `ma_target_companies.csv`]. Since Oct 1, 2026 every town runs a 12-month consolidated-permit clock [V]. Bylaw rewrites are under way in an estimated 100–250 towns [EST]. Their tools are county-grained (Heatmap, Spark, SitePath, Learnewable) [V], and counties have no zoning power in Massachusetts [V].
2. **Second, land-use and energy attorneys, including town counsel.** No rival has anything like the Attorney General (AG) bylaw-review ledger, which is built from 2,719 decision letters and covers 131 decisions [V]. Law firms already publish client alerts about each AG moratorium ruling (Foley Hoag, March 2026) [V], so a citable ledger gets links without outreach.
3. **Third, data-center developers and site selectors, reached mostly through the national siting platforms they already pay for.** The Oct 10 statewide scan flagged **133 data-center agenda items in 53 MA towns**, and a 40-item spot check found 38 genuine data-center zoning, moratorium or policy items [V, own data]. A widely cited national tracker (dcmap.us) lists 70 actions in 27 states and **none in Massachusetts** [V]. The best price anchor in the category is Cleanview at **$9,000 a year** for its data-center platform, plus $5,000 for API access, against "legacy" contracts of $40,000–80,000 [V].
4. **Everyone else is either a distribution channel or a later revenue line:**
   - Distribution channels, with free access: advocacy groups, journalists, regional planning agencies.
   - Later revenue lines: utility-scale developers, utilities, financiers, 40B developers, land agents, wireless.
5. **Proposed prices** are untested. They are set against published anchors: Zoneomics $92–279/mo, Shovels $599–999/mo, Cleanview $9k/yr, Docket Alarm $99/mo [V].
   - **Siting Desk:** $349/mo billed annually.
   - **Counsel:** $1,500/yr.
   - **Data-Center Feed:** $499/mo self-serve, or $6–12k per state per year as a platform licence.
6. **Regions:** Rhode Island and Maine are where the code is already close to complete-state coverage. New York is the biggest BESS-moratorium prize, but the paused NY pilot automated only 21 of 57 towns, against 68% in MA. Pennsylvania is the large later bet. The AG "answers" layer is unique to Massachusetts and does not travel; coverage and pre-meeting reading do.
7. **The ten features to build next** are led by four: LLC-to-parent entity linking, a consolidated-permit clock tracker, the MassDEP wetlands feed fused into project timelines, and Slack/Teams/calendar delivery with public permalinks, which is the main growth loop.
8. **Claims to fix now.** The live homepage says "15 of 15 town moratoria struck down by the Attorney General since 2024." That should read "15 of 15 solar and battery-storage moratorium articles the AG ruled on since 2024 were disapproved (12 towns)." Also never say "only pre-meeting monitor": MultiState, Quorum, FiscalNote, Hamlet, Kite and Spark all say they read agendas.

---

## 1. Competitor feature matrix

**What 351 Watch has today** (Oct 10, 2026 data unless noted):
- **Coverage:** 240 of 351 towns automated: 224 planning boards, 194 ZBAs, 221 conservation commissions, 225 select boards or councils [V, census].
- **Statewide scan** (meetings Sep 10–Dec 9, 2026): 934 flagged items in 170 towns. 139 were for meetings still ahead, first seen a median 3.2 days before the meeting [V, `agenda_hits_ma_all.json`].
- **Hits by topic:** zoning amendment 361, solar 233, BESS 142, data center 133, 40B 114, moratorium 81, consolidated permit 55, wireless 36.
- **Hits by board:** select board 366, planning board 282, Town Meeting 170 (39 towns), ZBA 73, conservation commission 43.

| Product | MA land-use board coverage | Pre-meeting agendas / packets | Town Meeting warrants | AG bylaw-review data | Wetlands / permit filings | Entity (LLC→parent) linking | Alert channels | Self-serve? | Price |
|---|---|---|---|---|---|---|---|---|---|
| **351 Watch** | **240/351 towns; PB 224, ZBA 194, ConCom 221** [V] | **Yes**, agendas and packets with OCR (639 of 641 image scans recovered) [V] | **92 of 292** Town Meeting towns found; 170 warrant hits in 39 towns [V] | **Yes**: 2,719 letters → 131 decisions; 18/18 moratoria disapproved since Jun 2022, 15/15 since 2024 [V] | MassDEP feed in build; 36 commercial solar/BESS filings a year measured [V] | Planned: wetlands "payor" field + ~500 SMART/CPS LLC names [I] | Web, RSS/JSON, iCal, Slack/Teams/generic webhook (in build) [V, ARCHITECTURE.md] | Yes (free beta; Stripe off) | Free beta; untested |
| **Hamlet** | 81 municipalities + 1 county (self-reported); Chicopee PB/ZBA/ConCom seen [V, index] | Claimed: "the moment agendas are posted"; API has agenda-monitoring topics; MA delivery unverified [V claim] | No Town Meeting body type in API [V] | None found [I] | None found | None in API schema [V] | Keyword alerts, notifications, bearer API; no webhooks in spec [V] | Free tier + 14-day trial; enterprise by sales [V] | Not published; "$49/mo plan" [R] |
| **Citizen Portal** | Lower bound: 18/30 sample towns any body, 13 with a land-use board [V, index] | Rare (Warwick agenda previews); mostly recaps [V] | Not seen [V] | No | No | No | Email topic and location alerts [V, index] | Yes | $12–49/mo; lifetime $199–999 (conflicting) [V, index]. **Terms bar competitive use** |
| **InstaTrac / Boston Globe** (MuniTrac, MassTrac) | MuniTrac is sold **to municipalities** for minutes and transcripts; only Everett named; no board count [V] | No: generated from uploaded agendas and recordings; output is minutes [V] | No evidence | No (MassTrac = legislature) [V] | No | No | MassInsider daily email; MobileTrac app [V] | Free trial / demo [V] | Not published; "more than 380 organizations" [V] |
| **MultiState** (local) | 4,850+ jurisdictions nationwide; MA page exists; MA count not given [V] | **Yes**: analysts read posted agendas and "send you advanced notice" [V] | Not stated | No | No | No | Email; hourly snapshots; web platform [V] | No (contact form) | Not published |
| **Quorum Local** | "All counties and cities of 3,000 or greater"; "12,500 sources"; MA not mentioned [V] | Yes: agenda and minutes alerts [V] | Not stated | No | No | No | Email, push [V] | No (demo) | Not published |
| **FiscalNote** (PolicyNote / Curate) | "12,000+ US cities and counties" (Curate: towns ≥2,000 people) [V, press] | Yes: agendas, minutes, planning documents [V, press] | Not stated | No | No | No | Dashboard, daily email reports, API [V] | No | Not published |
| **GovSpend Meeting Intelligence** | 10,000+ agencies; MA unknown [V] | Yes: daily scrapers, agendas and packets [V] | No | No | No | No | Platform | No; annual quote, "no tiers" [V] | Quote only |
| **Starbridge** | 320,000+ public-sector entities; sales-intelligence focus [V] | Mixed (minutes, plans, video) [V] | No | No | No | No | Platform | No; "premium, no free tier" (rival's claim) [R] | Not published |
| **Shovels Decisions** | 600+ cities, ~200k decisions; no MA or New England mention [V] | **No**: record only "after the minutes are posted" [V] | No | No | **Building permits (core)** [V] | **Yes**: applicant, owner, developer, contractor, property [V] | API, CLI, app; alerts not mentioned [V] | Yes | Free (500 credits); **$599**; **$999/mo**; enterprise [V] |
| **SitePath** | Every county graded; MA meeting pages: "No tracked activity yet"; town bylaws on file for 15/30 sample towns [V] | No | No | Essay on Carver ruling only [V, notes] | No | No | "Free email updates" [V] | Free map; paid by seat quote [V] | Not published |
| **Heatmap Pro** | County and ZIP scores; local laws for "every county and township"; news + phone calls [V] | No | No | No | No | Project database [V] | "Key project and policy alerts" (channel unstated) [V] | No (demo, annual) [V] | Not published |
| **Spark** (sparkhq.ai) | 3,000+ counties; townships "where public online sources exist" [V] | Yes, claimed: agendas, minutes, video; crawl "daily" / "multiple times per week" [V] | Not stated | No | "Project filings and permit records" [V] | Not stated | Alerts on any county; channel unstated [V] | No (quote by seats + usage) [V] | Not published; customers include NextEra, Intersect, Clenera [V] |
| **Kite** (BESS) | Coverage not stated [V] | Yes, claimed: "public agendas, meeting activity" [V] | Not stated | No | No | No | Not stated | No (demo) | Not published |
| **Learnewable / Site Scout** | 3,000+ counties; transcribes meetings posted to YouTube [V, trade press] | No (video) | No | No | No | No | Not stated | Not stated | Not published |
| **Paces** | No meeting monitoring described; "Permitting Predictor" [V] | No | No | No | Permitting reports [V] | No | Not stated | No (demo) | Not published |
| **LandGate** | Parcels, landowner marketplace, PowerTools CRM; bought Topos (BESS diligence) [R] | No | No | No | No | Parcel owner data [R] | Platform | Subscription [R] | Not published |
| **Cleanview** | Project tracking (133 MA utility-scale BESS projects page); no local-rule tracking described [V] | No | No | No | No | Project-level [V] | Platform, API add-on [V] | Yes | **$9,000/yr per platform (5 users); API +$5,000/yr; $4,900 one-time download** [V] |
| **Zoneomics** | Zoning-code text, not meetings [V] | No | No | No | No | No | App, integrations [V] | Yes | **$92 / $279 per month**; enterprise [V] |
| *Free:* **national data-center trackers** (dcmap.us, Savrn, Electric Choice, morethanjustparks) | dcmap: 70 actions, 27 states, **0 MA** [V]; morethanjustparks has an MA map [V, notes] | No (after adoption) | No | No | No | No | Web; dcmap "Agent API" link [V] | Yes | Free |
| *Free:* **Sabin Center** | State and local restriction counts (MA 21) [V] | No | No | No | No | No | None | Yes | Free; annual data |
| *Free:* **town "Notify Me"** (CivicPlus) | Per town, per board; only CivicPlus towns (195 MA AgendaCenter sites) [V] | **Yes**: emails or texts when an agenda or minutes are posted; some towns require a site account [V] | Some towns | No | No | No | Email, SMS [V] | Yes | Free; no keyword filter, one subscription per board per town [I] |
| *Free:* **Google Alerts** | Web-index keyword alerts [K] | Only once a page is indexed; town PDFs index slowly [K/I] | Incidental | No | No | No | Email, RSS [K] | Yes | Free |
| *Free:* **masspublicnotices.org** (MNPA) | Newspaper legal notices statewide, incl. hearings; 12-month search [V] | **Yes**: c. 40A §11 hearing notices run ≥14 days ahead [V statute] | Some | No | No | No | "Smart Search" (price not shown) [V] | Yes | Free |
| *Free:* **AG Municipal Law Unit portal** | Every bylaw decision letter [V] | No (after the vote) | Decisions on articles | **Raw letters**; tags miss some letters [V] | No | No | None | Yes | Free |
| *Free:* **MassDEP WIRe / EEA Data Portal** | Wetlands NOIs statewide, daily [V] | Filing date precedes ConCom hearing [V] | No | No | **Yes** | **Payor field** names the firm behind an LLC [V] | None | Yes | Free |

**What the matrix says** [I]:
- **Pre-meeting agenda reading is not unique.** At least eight paid products claim it, and the free town "Notify Me" lists already email residents the moment an agenda is posted.
- **What no listed product shows is the combination.** That combination is:
  1. small-town Massachusetts land-use boards at scale (224/194/221);
  2. Town Meeting warrants;
  3. the AG review outcome;
  4. wetlands filings linked to the parent developer;
  5. a published self-serve price.
- **The rivals fall into three groups:**
  - **Enterprise government-affairs tools** (MultiState, Quorum, FiscalNote, GovSpend, Starbridge) sell by demo, are aimed at policy teams, and say nothing about zoning structure.
  - **Siting-intelligence platforms** (Heatmap, Spark, SitePath, Kite, Learnewable) are county-grained, demo-priced, and say nothing about Massachusetts towns.
  - **The only self-serve priced tools** that touch the topic are Shovels (no MA, after the minutes), Cleanview (projects, not rules), Zoneomics (code text) and Citizen Portal (consumer recaps).
- **The opening is published, self-serve, Massachusetts-complete coverage priced between Zoneomics and Shovels.**

---

## 2. Segment-by-segment scoring

Scores run from 1 to 5:
- **Pain:** frequency × cost of missing an item.
- **WTP:** willingness to pay, from published anchors.
- **Edge:** our evidence-backed advantage today.
- **Reach:** reachable with no email outreach.
- **Volume:** the number of MA buyers.

Composite = 25% Pain + 25% WTP + 25% Edge + 15% Reach + 10% Volume. WTP is anchored, not tested. No segment has been offered a price yet.

| # | Segment | Pain | WTP | Edge | Reach | Volume | Composite | Role |
|---|---|---|---|---|---|---|---|---|
| 1 | Community-scale solar/BESS developers (<25 MW / <100 MWh) | 5 | 4 | 5 | 4 | 4 | **4.50** | **Win first (paid)** |
| 5 | Land-use & energy attorneys (developer side and town counsel) | 4 | 4 | 5 | 4 | 3 | **4.15** | **Win first (paid)** |
| 3 | Data-center developers / site selectors (and their platforms) | 5 | 5 | 3 | 3 | 2 | **3.90** | **Win first (paid + licence)** |
| 6 | Consultants / engineers (civil, wetlands, permitting) | 4 | 3 | 4 | 4 | 3 | 3.65 | Folded into #1 as free collaborators, then paid |
| 12 | Advocacy / community groups | 4 | 1 | 4 | 5 | 4 | 3.40 | Distribution (free) |
| 2 | Utility-scale developers (EFSB-jurisdiction) | 3 | 5 | 3 | 2 | 2 | 3.25 | Later; via API / platform partners |
| 9 | 40B / housing developers | 3 | 3 | 4 | 3 | 3 | 3.25 | Second wave |
| 11 | Municipalities / regional planning agencies | 3 | 1 | 4 | 4 | 4 | 3.00 | Distribution + source access |
| 13 | Journalists | 3 | 1 | 4 | 5 | 2 | 2.95 | Distribution (free) |
| 4 | Land agents / brokers | 3 | 2 | 3 | 4 | 3 | 2.90 | Low-price tier later |
| 8 | Utilities / transmission | 3 | 4 | 3 | 1 | 1 | 2.75 | Later; enterprise data licence |
| 7 | Tax-equity / financiers / insurers | 2 | 4 | 2 | 2 | 2 | 2.50 | After decision history exists |
| 10 | Wireless / tower companies | 2 | 3 | 2 | 2 | 1 | 2.15 | Not a focus |

The ranking holds if Reach and Volume are dropped: the top three stay the top three [I, recomputed]. It would flip only if data-center WTP proved low in MA, and the offer below hedges that by selling through platforms.

### Segment detail

**1. Community-scale solar/BESS developers. Priority: win first.**
- **Pain [V]:**
  - Since Oct 1, 2026, towns must accept consolidated permits and decide within 12 months, or the project is constructively approved.
  - An estimated 100–250 towns are rewriting energy bylaws [EST].
  - The statewide scan found 233 solar and 142 BESS items in 76 and 55 towns. Thirty-four solar/BESS hits in 13 towns name an LLC rather than a developer.
  - Carina Energy's BESS permitting guide warns that moratoriums "can pass within a single board meeting cycle and may not appear in databases for weeks or months," and tells developers to track agendas, minutes and local news themselves.
- **Current workaround:**
  - Permitting staff check town sites by hand, one Notify Me list per board per town (a 50-town portfolio is about 150 subscriptions) [I].
  - Google Alerts, local counsel and engineers' word of mouth [I].
  - County-grain risk scores from Heatmap, Spark or SitePath [V].
- **Who serves them:** Heatmap Pro (AES case study), Spark (NextEra, Intersect, Clenera), Kite, Learnewable, SitePath [V]. All are county-level and demo-sold. None shows MA town meetings; SitePath's MA pages show "No tracked activity yet" [V].
- **WTP anchors:**
  - Shovels $599–999/mo [V].
  - Cleanview $9k/yr for 5 users [V].
  - Zoneomics $279/mo [V].
  - A Carina fatal-flaw screen "typically costs under $5,000" per site [V].
  - Anything priced at one site screen a year is easy to approve [I].
- **Our edge:**
  - 221 conservation commissions and 224 planning boards [V].
  - The AG ledger [V].
  - The wetlands payor field ties single-project LLCs to their parents: New Leaf Energy is behind at least 9 of the 36 commercial solar/BESS filings [V].
  - Three companies appear both in state program lists and in our agenda hits (Parallel Products, Kearsarge, New Leaf) [V].
- **No-email acquisition:**
  - Town × topic SEO pages, such as "Carver battery storage bylaw" and "[town] consolidated permit."
  - Company pages ("Golden Pond Solar 1, LLC → New Leaf Energy").
  - Slack/Teams alerts that link to public item pages.
  - Free collaborator seats for engineers and counsel.
  - Presence at trade-group events and member resource pages: SEBANE, NECEC, Coalition for Community Solar Access, Energy Storage Association [K for names].
- **Size:** 54 firms with 3+ projects; 63 solar/storage firms in the target list [V].

**2. Utility-scale developers. Priority: later.**
- **Pain:** projects of 25 MW+ or 100 MWh+ go to the EFSB on a 15-month clock [V]. Local host agreements, zoning-exemption petitions and conservation-commission filings still happen (for example EFSB 26-01 Moraga/Oakham and 26-02 Hillman/Tewksbury) [V].
- **Current workaround:** in-house counsel plus national platforms (Heatmap, Spark, Paces) [V/I].
- **WTP:** high per account. The legacy platform range is $40–80k per year, per Cleanview [R].
- **Our edge:** town-level MA signal, but only 17 standalone BESS projects sit in the ISO-NE queue, so there are few buyers [V].
- **No-email acquisition:** be the town-level data inside the platforms they already use (see offer 3) [I].

**3. Data-center developers and site selectors. Priority: win first, mainly through platforms.**
- **Pain:**
  - Data Center Watch counted at least 75 projects worth about $130B blocked or delayed in Q1 2026 [R, via search summary].
  - The Sept 8, 2026 MA executive order requires a host-community benefits agreement for projects over 25 MW, which moves decisions to select boards and councils: exactly the boards we read in 225 towns [V].
  - Data-center moratoria are **approved** by the AG (Shutesbury, Templeton, Gill), so in MA they stick [V].
- **Current workaround:**
  - Free national trackers (dcmap.us, Savrn, Electric Choice) [V].
  - Consultants and counsel [I].
  - Heatmap and Spark, which both list data centers [V].
  - MultiState's state monitoring pages are titled "Data Centers" [V, search listing].
- **Our edge:**
  - 133 data-center items in 53 towns [V].
  - Snippets mention a moratorium in 28 towns and prohibition language in 10. Some are cross-references, so hand-check before citing [V/I].
  - Real project items appear too, for example Westfield's Servistar Realties data-center permit extension [V].
  - dcmap shows 0 MA actions [V].
- **WTP:** Cleanview $9k/yr data-center platform plus $5k/yr API [V].
- **Weakness:** MA has about 14–20 named data-center firms and 4 proposed facilities [V, siting_market.md]. MA alone is a thin direct market, so the offer is a Northeast feed and a platform licence.
- **No-email acquisition:**
  - A free, citable MA (then Northeast) data-center local-action map with "cite this" attribution.
  - Inbound licensing to the platforms (Heatmap, Spark, SitePath, Cleanview, Paces, LandGate).
  - Journalists' citations.

**4. Land agents and brokers. Priority: low-price tier later.**
- **Pain:** they need to know whether a town is turning hostile before optioning land. Moderate pain [I].
- **Current workaround:** parcel apps (LandGlide $99.99/yr [R, snippet]), LandGate PowerTools (unpublished price) [R], Regrid [K], phone calls to town halls [I].
- **Our edge:** town pages plus, later, parcel IDs [I].
- **WTP:** low per person [I].
- **No-email acquisition:** free town pages, plus a $29/mo "Scout" tier once parcel links exist [I].

**5. Land-use and energy attorneys, including town counsel. Priority: win first.**
- **Pain:**
  - Town Meeting articles, AG review (a median of about 108 days from town meeting to ruling for 2025–26 moratoria [V]), 40B ZBA hearings, and consolidated-permit appeals.
  - Firms already write about each AG ruling, for example Foley Hoag's "AGO Rejects Yet Another Municipal Solar and Battery Storage Moratorium" (March 2026) [V].
- **Current workaround:** searching the AG portal by hand (its topic tags miss letters, and about 11% of tagged letters are missing from its full-text index [V]), client tips, and firm blogs [I].
- **Who serves them:** nobody structures AG outcomes. InstaTrac covers the legislature, not bylaws [V].
- **WTP anchors:** Docket Alarm $99/mo for unlimited alerts; Plural $609/yr per seat; BillTrack50 $1,000/yr per state [V, comparables notes]. Billing rates make a $100–150/mo tool trivial [K].
- **Our edge:**
  - 131 decisions with exceptions.
  - 16 of 33 partial approvals struck a herbicide clause.
  - Our ledger documents Hanson and Hampden, which the AG's own 2026 footnoted list omits [V].
- **No-email acquisition:**
  - A citable ledger with permalinks per decision and per article.
  - An RSS feed of new AG decisions.
  - Talks at MCLE, the Boston Bar Association land-use section, the Massachusetts Municipal Lawyers Association and the APA-MA conference [K for names].
- **Size:** 4 firms listed in the target CSV; the MA land-use bar likely has 100+ firms [EST].

**6. Consultants and engineers. Priority: free collaborators inside offer 1, then paid.**
- **Pain:** they attend the hearings and juggle multi-town calendars. They also need business development: who is filing where [I].
- **Evidence they are in the loop:** wetlands payor fields show Beals and Thomas paying 4 filings, Farland Corp 3 and Kimley-Horn 1 [V]. Weston & Sampson prepared Montague's BESS application packet [V].
- **WTP anchors:** Zoneomics $92–279/mo; Shovels [V].
- **Our edge:** conservation-commission coverage plus the wetlands feed [V].
- **No-email acquisition:** invited into developer workspaces as free collaborators. Each consultant serves several developers, so one invite exposes many firms [I].

**7. Tax-equity investors, financiers and insurers. Priority: after decision history exists.**
- **Pain:** episodic, at diligence. Counsel review "real estate, state and local taxes, permitting" for tax-equity investors (K&L Gates practice description) [V].
- **WTP anchors:** a per-project report. Carina screens cost under $5k; Cleanview's one-time download is $4,900 [V].
- **Our edge today:** weak. They need a permit-history record (hearing, conditions, appeal period, AG status) that is not built yet [I].
- **No-email acquisition:** a "permit history report" button on project pages, bought by the attorneys who run diligence [I].

**8. Utilities and transmission. Priority: later.**
- **Pain:** substation zoning exemptions and line rebuilds that cross many towns (National Grid's EFSB 25-01 runs through 17 towns) [V]. Large-load forecasting depends on where data centers are banned or welcomed [I].
- **WTP:** enterprise, but procurement-heavy and sales-led. That conflicts with the no-email constraint [I].
- **No-email acquisition:** an enterprise data licence later, once inbound demand exists [I].

**9. 40B and housing developers. Priority: second wave.**
- **Volume:** 114 40B items in 43 towns in the scan window; ZBA coverage 194 towns [V]. The MBTA Communities rezoning wave is mostly over (157 of 177 compliant) [V].
- **Pain:** moderate. They know their own projects; the value is competitor and pipeline intelligence plus "safe harbor" fights [I].
- **No-email acquisition:** SEO pages such as "[town] 40B comprehensive permit hearing" [I].

**10. Wireless and tower companies. Not a focus.**
- **Volume:** 36 items in 26 towns [V]. There are 10–20 concentrated buyers who use site-acquisition contractors and national tools [V/I]. Low pain per dollar.

**11. Municipalities and regional planning agencies. Distribution plus source access.**
- **Pain:** benchmarking neighbours' bylaws, abutter notices under c. 40A §5, and AG outcomes for town counsel [V/I]. In the scan, Heath's planning board noted "FRCOG money and assistance available to support new bylaws" [V, own data].
- **WTP:** low, under Chapter 30B procurement [V/I]. MuniTrac sells to towns, but for minutes, not intelligence [V].
- **Strategic value:**
  1. **Permission to crawl the 64 towns that block bots** (1.10M residents) [V].
  2. Distribution to member towns through a free regional dashboard [I].

**12. Advocacy and community groups. Distribution (free).**
- **Pain:** high attention, little money [I].
- **Current workaround:** Notify Me, Citizen Portal at $12–24/mo, Facebook groups [V/I].
- **Edge:** a free tracker and town pages [V].
- **Role:** the sharing engine. They share town pages in neighbourhood groups and at hearings [I].
- **Policy:** the same facts for everyone, no advocacy, and a published correction log, because developers and opponents use the same pages (Hamlet also serves both residents and developers [V]).

**13. Journalists. Distribution (free).**
- **Current tools:** Hamlet plans to give its tool to local journalists for free [V, TechCrunch via search]. Citizen Portal's Journalist Pro is $49/mo [V, index]. The Globe owns InstaTrac [V].
- **Role:** citations from the Gazette, Recorder, Berkshire Eagle, The Shoestring, MassLive, WBUR, CommonWealth Beacon and, in RI, ecoRI [K for names]. Each citation brings backlinks and credibility. Offer newsroom access free in exchange for credit [I].

---

## 3. The top three segments: exact offers and acquisition loops

All three use one product and one data spine (towns, boards, items, companies, decisions). They differ in packaging. Pricing is self-serve and published on the site: there are no sales calls, and every trial runs without a sales touch. Billing goes through Stripe Checkout, which exists in the codebase but is disabled. **Before charging, move off Vercel Hobby, which is limited to non-commercial use** [V, VALIDATION.md].

### Offer 1: "Siting Desk" for MA community-scale solar/BESS developers, with their engineers and counsel as free collaborators

| | Free (public) | **Siting Desk** |
|---|---|---|
| Coverage | All public pages: tracker, town pages, AG ledger, item permalinks | All monitored MA towns, all topics |
| Watchlists | 1 watchlist, up to 5 towns, daily | Unlimited watchlists; **company watch** (up to 25 parent companies and their LLCs) |
| Delivery | Web + RSS | **Slack/Teams app, iCal hearing calendar, webhooks, RSS/JSON, CSV export** |
| Freshness | Daily | **Every 6 hours** for watched towns (the 10th-percentile agenda goes up 2 days ahead; 4% first appear on the meeting day [V]) |
| Project tools | — | **Consolidated-permit clock** per application (completeness date, 12-month constructive-approval date, continuances); **wetlands NOI feed** fused into each project's timeline |
| Seats | 1 | 5 internal + **unlimited external collaborators** (engineers, counsel, landowners' agents) |
| Price | $0 | **$349/mo billed annually ($4,188/yr), or $399 month-to-month.** Founding offer on the site: $199/mo locked for 12 months for the first 20 teams, in exchange for using the correction form and permission to show the firm's name |

**Why this price** [I]:
- It sits above Zoneomics Advanced ($279/mo) and below Shovels Basic ($599/mo) and Cleanview ($750/mo equivalent) [V anchors].
- A year costs less than one Carina fatal-flaw site screen ($5k) [V].
- It falls inside the earlier report's illustrative $200–600/mo band.

**Acquisition loop (no email):**
1. **Search:** permitting staff search "[town] battery storage bylaw," "[town] consolidated permit 225 CMR 29" or an LLC name. They land on a town page or company page that shows dated, sourced items. Long-tail town × topic pages are uncontested: Citizen Portal articles are recaps filed under odd paths, and the national trackers stop at the state or county [V/I].
2. **One-click "Watch this town / company":** a watchlist with no account (architecture: a random ID acts as the credential) [V]. It delivers by RSS or **"Add to Slack/Teams"**.
3. **Every alert in Slack is a public permalink** with "Tracked by 351 Watch · watch this town." Colleagues click it, and so do the consultant and the lawyer in the shared channel. Each new reader is a new watchlist [I].
4. **iCal hearing feed:** hearings appear in Outlook and Google calendars with links back. The product stays visible and spreads to everyone invited to the hearing [I].
5. **Collaborator invites:** the developer invites an engineer and counsel as free collaborators. They meet the product for other clients' towns and start their own workspaces. That spreads it across the 6+ consultant firms and 100+ law firms that touch many developers [I].
6. **Upgrade triggers:** more than 5 towns, company watch, Slack, the clock tracker or exports require Siting Desk.
7. **Community presence:** talks and published data at SEBANE / NECEC / CCSA events and MACC's annual conference (conservation commissioners) [K]. These are presentations, not outreach lists.

**KPIs:**
- Organic sessions to town and company pages.
- Watchlists created per 100 sessions.
- Slack/Teams installs.
- Permalink visits from Slack referrers (the viral coefficient).
- Collaborator-to-workspace conversion.
- Trials to paid.

**Kill or adjust:** if fewer than 5 of the 54 multi-project firms have started a trial within 90 days of the paid launch, test the price and packaging, not the segment, first [I].

### Offer 2: "Counsel" for land-use and energy attorneys and town counsel

| | Free | **Counsel** |
|---|---|---|
| AG ledger | Full public ledger with permalinks; **RSS of new AG decisions** | Same, plus alerts filtered by topic, town or client |
| Warrant watch | Public warrant items on town pages | **Every posted warrant article on solar, BESS, data centers, moratoria, 40B or consolidated permits, auto-classified** (moratorium, ban, district prohibition, tiered regulation, herbicide clause, visibility clause, insurance requirement) with the **historical AG outcome for that pattern** and the **expected decision window** (median about 108 days) |
| Pending review | Pending list | Watch any pending article; alert when the letter posts |
| Comparables | — | Provision-level comparables: which towns adopted the DOER model BESS bylaw as written, and which provisions the AG struck (herbicide 16 of 33 partial approvals; view-elimination; $100M insurance) |
| Hearings | Town pages | 40B and consolidated-permit hearing calendar (iCal), matter tags, citation-ready CSV (case number, letter link) |
| Seats / price | — | **$1,500/yr for up to 3 attorneys; $3,000/yr firm-wide (up to 15)** |

**Why this price** [I]: it is the same order as BillTrack50 at $1,000 per state per year, and below Docket Alarm's flat plan at $99/mo, which is $1,188/yr per user [V anchors]. Firms buy it as a research tool, not a seat-heavy platform.

**Disclaimer:** every page carries "historical track record, not legal advice." The wording needs a lawyer's review before launch [V, earlier report].

**Acquisition loop (no email):**
1. **A citable ledger:** each decision gets a stable URL, a "cite this" box and a free CSV under attribution (CC BY). When firms write the next client alert on an AG ruling (they already do [V]), the natural link is the ledger [I].
2. **A new-decision RSS feed:** AG letters land on the portal without notification [V]. Our feed is the free daily habit, and it links to the warrant-watch paywall.
3. **Town counsel and planners** reach the ledger while drafting bylaws. Answering "will this survive?" with exceptions shown builds trust [I].
4. **Continuing education:** offer the dataset and a talk to MCLE, the BBA land-use section, the Massachusetts Municipal Lawyers Association, the APA-MA conference and the Massachusetts Association of Planning Directors [K for names]. These are invitations to present, not cold outreach.
5. **Upgrade triggers:** client-filtered alerts, the warrant-pattern classifier, comparables, exports.

**KPIs:**
- Referring domains to `/ag/` pages, and law-firm citations.
- RSS subscribers.
- Counsel trials.

### Offer 3: "Data-Center Local Action Feed" for Massachusetts first, then the Northeast; self-serve and platform licence

| | Free | **Feed (self-serve)** | **Platform licence** |
|---|---|---|---|
| Content | Public MA map and list: town, board, date, action type (definition, use-table change, moratorium, prohibition, HCA vote, special permit or extension), source link | Same, with status lifecycle (proposed → hearing → Town Meeting / council vote → AG approved or disapproved → in effect → expiry), host-community-agreement tracker, abutter-town notices; MA + RI + ME at launch, NY and NH as covered | Bulk and API feed of the same records with stable IDs, for display inside the partner's product, with attribution |
| Delivery | Web, RSS | Webhook, API, CSV/GeoJSON, Slack/Teams | API, daily bulk file |
| Price | $0 | **$499/mo billed annually ($5,988/yr), 5 seats** | **$6,000–12,000 per state per year**, or revenue share; attribution and a link back required |

**Why this price** [I]: it sits under Cleanview's $9k data-center platform plus $5k API, and far under the $40–80k "legacy" contracts Cleanview cites [V]. The licence turns every national platform into a distribution channel instead of a competitor.

**The answer layer differs here:** data-center moratoria are **approved** by the AG, because data centers are not a protected use [V]. The feed says "this restriction is likely to stand," which is the opposite of the solar/BESS message, and is worth as much to a site selector.

**Acquisition loop (no email):**
1. **The public map is the only town-level MA data-center layer we found.** dcmap.us shows 0 MA entries [V], and morethanjustparks has an MA map at a coarser level [V, notes]. Journalists covering the MA moratorium wave link to it [I].
2. **"Cite this data" and attribution-required CSV:** national trackers that publish their methods (dcmap's "Cite this data" page) pick up MA entries with a link back [V/I].
3. **Inbound licensing:** a public "Data licence" page with the published price. Heatmap, Spark, SitePath, Cleanview, Paces and LandGate are the natural licensees. All sell to the same buyers and all are county-grained [V]. A licence brings attribution inside their products, which is distribution [I].
4. **An agent integration:** a documented API plus an MCP / "agent API" endpoint, so AI agents in diligence workflows can query MA town actions. dcmap already advertises an "Agent API" [V], so the expectation exists [I].
5. **Northeast expansion feeds the map:** Maine (Bangor and Westbrook data-center moratoria found by the stock crawler [V]) and Rhode Island (Charlestown data-center and BESS ban; Westerly one-year moratorium; Smithfield ban [V, ecoRI and Citizen Portal via search]) make the map regional within weeks.

**KPIs:**
- Map citations and referring domains.
- Licence inquiries from the public page.
- Feed trials.

**Kill or adjust:** if no platform licenses within 6 months of the RI and ME data going live, keep the free map for distribution and fold the feed into Siting Desk [I].

---

## 4. Regions: where 351 Watch excels beyond Massachusetts, and why

**What makes 351 Watch strong** is a specific stack: (a) town or township decision-makers that county tools miss; (b) agendas or warrants legally required and posted online; (c) local control of siting; (d) a CivicPlus-heavy web estate the code already reads; (e) a statewide filing point or review layer; (f) an active data-center or BESS fight. The AG review layer, which turns alerts into answers, is **Massachusetts-only**. Other New England states do not send town bylaws to the AG [K]. Outside MA the edge is therefore coverage and pre-meeting reading, not the verdict.

| State | Town grain | Agenda law vs MA | Local siting | Code fit (measured) | Demand signal | Fit verdict |
|---|---|---|---|---|---|---|
| **Rhode Island** | 39 municipalities, no county government [V] | **Comparable:** 48 h excluding weekends, a statement of business, **filed electronically with the Secretary of State** [V] | Local under 40 MW; storage not state-sited [V] | 3/6 towns with town-site adapters; **one SOS-portal adapter covers all 39 with "filed on" timestamps**, including the Cloudflare-blocked Hopkinton and Exeter [V] | Charlestown data-center **and first BESS ban**; Westerly one-year data-center moratorium; Smithfield ban; Hopkinton emergency moratorium listed [V, search]; a 40B-analog housing act [V] | **Best fit, first add-on.** It is the only place we can honestly claim *every* municipality, with provable lead times. Same Southern New England developers. Small market (score 30.6) [V] |
| **Maine** | ~484 towns [V] | Weaker: "ample time," no agenda rule [V]; 7-day warrant posting [V] | Home rule; DEP permit over 20 acres [V] | **5/6 automated with stock code; 32 hits** [V] | Bangor and Westbrook data-center moratoria; 32 local restrictions [V]; statewide data-center ban vetoed in Apr 2026 [V, notes] | **Cheap add-on.** Code works today, and it feeds the data-center map. Energy pipeline small after net energy billing closed [V] |
| **New York** | 1,525 towns, villages and cities; **town-board government** like MA [V] | Mixed: 72 h notice, **records online 24 h ahead "to the extent practicable"**, no agenda rule [V] | Local under 25 MW and for **standalone BESS** [V] | Probe: 4/6. **Paused NY pilot: 21 of 57 BESS-moratorium towns automated (37%)**; 17 had no listing or stale listings, 7 bot challenges, 5 robots, 3 crawl-delay [V, `towns_ny.json`, WIP] | **The national BESS-moratorium centre:** Carina counts 98 of 150+ [R]; Sabin: 86 local restrictions, 52 contested projects (most in US) [V]; town notices from Lockport, Marcellus, Walton and others [V]; Suffolk County planning-commission staff reports on town BESS moratorium extensions (Southold) [V, search] | **Biggest BESS prize; the second build.** It needs more adapters (Drupal and WordPress listings). It also needs a different answer layer: county planning referrals (GML 239-m [K]), ORES override (§142(5)) [V] and moratorium-extension patterns. Data centers: EO 62 pauses *state* permits for 50 MW+, and the 20 MW bill is unsigned as of mid-July [V]; local zoning still decides |
| **New Hampshire** | 234 towns [V] | Weaker (24 h, no agenda) [V], **but town warrants must be on town websites from Oct 18, 2026** [V] | Local under 30 MW [V] | Good where reachable; Cloudflare blocked 3/6 [V] | Data-center fights (Bow, Nottingham, Rochester) [V] | **Warrant feature transfers directly.** Small energy pipeline. Add for data centers and warrants |
| **Pennsylvania** | 2,625 governments [V] | 24-h online agenda; no action on unlisted items [V] | **Fully local at any size**; HB 502 stalled [V] | Weak for current code (no CivicPlus; JavaScript libraries) [V] | 60 restrictions; 61 data-center measures [V] | **Largest market (score 71.8), needs real adapter work.** Third build |
| **New Jersey** | 564 municipalities [V] | 48 h agenda "to the extent known"; **land-use documents on file 10 days before hearings**; website legal notices plus a **statewide directory since Mar 1, 2026** [V] | Disputed for energy [V] | Weak (eCode360 robots, Akamai) [V] | **Most data-center measures in US (119, Savrn)** [V] | Data-center and housing market only. The legal-notice directory is a ready source list |
| **Connecticut, Vermont** | Towns | Weaker / comparable | **State siting** (CT over 1 MW; VT all generation) [V] | Weak [V] | Harwinton data-center/BESS/solar moratorium drafts (CT) [V] | Housing (8-30g) and data-center alerts only |

**Why this order** [I]:
1. **RI and ME are near-complete coverage at almost no code cost.** "Complete" is our differentiator, and both add towns to the data-center map.
2. **NY has the deepest BESS demand.** But its pilot automation rate (37%) is half of MA's (68%), so it needs about a month of adapter work before any coverage claim.
3. **PA is the big later market,** and needs a new adapter family.

---

## 5. The ten features to build next, ranked by value to the top three segments

Value columns: **Dev** = solar/BESS developers, **Law** = attorneys, **DC** = data center. ●●● = high value.

| # | Feature | Dev | Law | DC | Evidence it matters |
|---|---|---|---|---|---|
| 1 | **Entity resolution and "watch a company":** match agenda and NOI lines to parent developers through the MassDEP payor field, the ~500 SMART and Clean Peak LLC names and Secretary of State records; company pages; alerts when any of a company's LLCs appears anywhere | ●●● | ●● | ●● | 34 solar/BESS hits in 13 towns name an LLC [V]; New Leaf is behind ≥9 of 36 filings; Beals and Thomas pays 4 [V]; agenda lines often name only an LLC or address [V]; Shovels sells exactly this applicant/owner linkage [V] |
| 2 | **Consolidated-permit clock tracker and town-adoption status:** per-town status (own bylaw vs DOER model vs undecided), per-application clock (completeness date, 12-month constructive-approval date), EFSB de novo requests | ●●● | ●●● | ● | Oct 1, 2026 mandatory acceptance; 12-month constructive approval [V]; no DOER or other public adoption tracker was found [V, negative search]; Sutton still choosing in July [V]; 55 consolidated-permit hits in 27 towns [V] |
| 3 | **MassDEP wetlands feed fused into project timelines:** NOI filing → conservation-commission hearing → order of conditions, matched to agenda items | ●●● | ●● | ● | Free daily public API with the payor field [V]; conservation commissions are only 43 of 934 hits because NOI lines rarely say "solar" [V]; 25–40% of projects need a wetlands filing [EST] |
| 4 | **Delivery and integration layer:** Slack/Teams app, iCal hearing calendar, webhooks, RSS/JSON, public API and an agent/MCP endpoint; every alert links to a public permalink | ●●● | ●● | ●●● | The main no-email growth loop [I]; channels named by rivals are email, push or unstated (MultiState, Quorum, SitePath, Heatmap, Spark) [V]; Shovels and dcmap offer API or agent access [V] |
| 5 | **Warrant watch with AG outcome patterns:** raise warrant coverage from 92 to 292 towns; classify each article; attach historical outcome and expected decision window; publish a new-AG-decision RSS feed | ●● | ●●● | ●● | Warrants found for only 92 of 292 towns [V]; Westford's article was caught 16 days ahead [V]; 131 decisions with consistent reasoning; median ~108 days to ruling [V]; the AG portal has no notifications and imperfect tags [V] |
| 6 | **Hearing legal-notice feed (c. 40A §11):** the newspaper notices that must run at least 14 days before PB and ZBA hearings, via a licence with MNPA's masspublicnotices.org or towns' legal-notice pages | ●●● | ●● | ● | §11 sets the 14-day minimum [V]; ZBA coverage trails because small towns post ZBA hearings as legal notices, not agendas [V]; agendas give a 5-day median [V]. **Check MNPA terms and robots before any automated use** |
| 7 | **Data-center and host-community-agreement tracker** with a public map and status lifecycle (offer 3), extended to RI, ME and NH | ● | ● | ●●● | 133 items in 53 MA towns [V]; dcmap shows 0 MA [V]; the Sept 8, 2026 executive order moves 25 MW+ decisions to select boards and councils [V]; AG approves data-center moratoria [V] |
| 8 | **Coverage completion:** permission programme for the 64 bot-blocked towns (Worcester, Cambridge, Framingham, Revere, Newton, Brookline, New Bedford, Lynn; MyTownGovernment's 14 towns); a fixed allow-listed IP; abutter-town notices; 6-hour refresh | ●● | ●● | ●● | 64 towns, 1.10M residents blocked [V]; abutter notices revealed the Uxbridge and Northbridge actions [V]; 4% of agendas first appear on the meeting day [V]. Route requests through regional planning agencies and partner towns, not mass email |
| 9 | **Decision lifecycle and backfill, plus a "permit history report":** one record per application (filing → hearings → continuances → vote → conditions → appeal → AG); per-project PDF or CSV | ●● | ●●● | ● | Acquirers pay for history (InstaTrac's "three decades", Clio–vLex) [V]; Shovels statuses are "coming soon" [V]; tax-equity diligence covers permitting [V]; per-site screens cost under $5k [V] |
| 10 | **Bylaw provision comparables:** text diff against the DOER model bylaws; which provisions survive AG review | ● | ●●● | ● | 100–250 towns rewriting bylaws [EST]; the AG strikes specific provisions (herbicide 16 of 33, view elimination, $100M insurance) [V]; regional planning agencies are funding bylaw drafting (FRCOG) [V] |

**Deliberately not on the list** [I]:
- AI meeting summaries or video transcripts. Hamlet, Citizen Portal, MuniTrac and GovSpend already offer them, mostly free or bundled [V].
- Speed claims against rivals. Not measurable [V].
- Email digests. The owner's constraint, and the architecture uses no email [V].

---

## 6. Claims ledger update

The ledger in `reports/Meeting monitor deep dive.md` stays in force. Its robots.txt and per-item timing rows are now fixed [V, report header]. Additions and corrections from this session:

### New claims we can make (dated, with method)

| Claim | Evidence | As of |
|---|---|---|
| "Our Oct 10 statewide scan flagged 934 agenda items in 170 Massachusetts towns for meetings from Sep 10 to Dec 9, 2026." (Call them "flagged items," not "siting actions"; pilot precision was about 90%.) | `agenda_hits_ma_all.json` [V] | Oct 10, 2026 |
| "We found data-center items on agendas or warrants in 53 Massachusetts towns (133 items) in that window." (In a 40-item spot check, 38 were real data-center zoning, moratorium or policy items.) | Same file; spot check this session [V] | Oct 10, 2026 |
| "A national data-center policy tracker (dcmap.us) listed 70 actions in 27 states and none in Massachusetts in October 2026." (Attribute and date it.) | dcmap.us/insights/policy [V] | Oct 2026 |
| "Of 139 flagged items for meetings still ahead, we first saw the agenda a median of 3 days before the meeting." (State that the first crawl ran Oct 10, so this measures our first fetch, not the town's posting date.) | first_seen data; proof page [V] | Oct 10, 2026 |
| "Since 2024, the Attorney General disapproved all 15 solar or battery-storage moratorium articles she ruled on, in 12 towns." | `ag_decisions.json` [V] | Through Oct 10, 2026 |
| "Data-center moratoria in Massachusetts towns have been approved by the AG (Shutesbury, Templeton, Gill), because data centers are not a protected use." | AG letters [V] | Through Oct 10, 2026 |
| "MultiState, Quorum and FiscalNote describe national local-government monitoring of agendas; their published coverage descriptions do not mention Massachusetts town boards, Town Meeting warrants or AG review." (Describe their pages, not their data.) | Vendor pages [V] | Oct 10–11, 2026 |
| "Quorum describes its local coverage as counties and cities of 3,000 or more people." | quorum.us/products/local [V] | Oct 2026 |
| "We publish our prices." (Only once true. None of the siting-intelligence rivals checked publishes a price: Heatmap Pro, Spark, SitePath, Kite, Paces, MultiState, Quorum, FiscalNote, GovSpend, Starbridge [V].) | Vendor pages [V] | Oct 2026 |
| "Carina Energy's BESS permitting guide warns that moratoriums can pass within a single board meeting cycle and may not appear in databases for weeks or months." (Quote it as industry context.) | carina.energy guide [V] | Accessed Oct 2026 |

### New claims we must not make

| Must not say | Why | Safe alternative |
|---|---|---|
| "15 of 15 town moratoria **struck down**" (current homepage and proof-page tile) | Counts articles, not moratoria; "struck down" suggests a court; Spencer's no-action is excluded | "15 of 15 solar and battery-storage moratorium articles the AG ruled on since 2024 were disapproved (12 towns)" |
| "We're the only service that alerts before the meeting" / "competitors only cover meetings after the fact" | MultiState ("advanced notice"), Quorum (agenda alerts), FiscalNote/Curate, Hamlet, Kite and Spark all say they read agendas; CivicPlus Notify Me emails when agendas post [V] | "We read every posted agenda for 224 planning boards, 194 ZBAs and 221 conservation commissions, including Town Meeting warrants and AG outcomes." |
| "53 Massachusetts towns have data-center moratoria" | 53 towns have *items*; many are definitions, hearings or cross-references [V] | "Data-center items appeared on agendas in 53 towns; moratorium language in about 28 (hand-checked list to follow)" |
| "Nobody tracks data centers (or BESS bylaws) in Massachusetts" | morethanjustparks has an MA map; MultiState runs data-center state pages; The Shoestring and WBUR cover it; Citizen Portal writes recaps [V] | "We found no other town-by-town, agenda-sourced MA data-center list as of Oct 2026" |
| "Quorum / FiscalNote / MultiState / Spark / Heatmap don't cover Massachusetts towns" | They claim national coverage including townships; unverified either way [V] | Describe only what their public pages say, dated |
| "Cheaper than Heatmap, SitePath or Spark" | Their prices are unpublished [V] | "Published self-serve pricing" |
| "Real-time" | Daily crawl today; 6-hour refresh planned | "Checked daily" (later "every 6 hours"), with the published lead-time table |
| "The AG will strike your moratorium" / "this bylaw will be approved" | A legal prediction; data-center moratoria go the other way [V] | "Historical record: N of N comparable articles…," with the exceptions list and a "not legal advice" notice |
| "We cover Rhode Island, Maine or New York" | Only probes and a paused NY pilot (21 of 57 towns) [V] | "We have tested our crawler in every Northeast state" |
| "InstaTrac / the Globe doesn't track land use" | Only its public pages were read [V] | "InstaTrac's public pages describe MuniTrac as a minutes and transcript service sold to municipalities" |
| Any price as "validated" or any revenue figure as fact | No buyer has been offered a price [V] | Label prices "launch pricing" and revenue "EST" |

---

## Gaps and what would change these conclusions

- **No willingness to pay has been tested.** Every price here is anchored, not measured. The founding-team offer on the site is the cheapest test that respects the no-email rule.
- **Prices unknown:** Hamlet, Heatmap Pro, SitePath, Spark, Kite, Paces, LandGate, MultiState, Quorum, FiscalNote, GovSpend and Starbridge publish none; searches found no third-party price for any of them. Hamlet's "$49/mo" remains [R].
- **Competitors' MA depth is unverified:**
  - Quorum's 3,000-population floor and FiscalNote's 2,000 floor would still include most MA towns [I].
  - Spark and Kite claim agenda monitoring, but no coverage lists are published.
  - None was tested with an account, consistent with the earlier rules.
- **How developers track risk today** comes from vendor guides (Carina) and vendor marketing (Kite, Spark), not from interviews. Five short user interviews, booked through inbound site sign-ups rather than email, would firm up segment 1.
- **Data-center demand in MA itself is thin** (about 14–20 firms). Offer 3 depends on platforms licensing the data or on fast RI, ME and NY coverage.
- **New York automation (37%) comes from a paused WIP pilot.** Rerun it before planning NY dates.
- **Not verified:** MNPA/masspublicnotices.org terms for automated use; GML 239-m referral mechanics; trade-association and continuing-education venue names marked [K].

## Sources (new this session; earlier sources are in the files listed at the top)

- **InstaTrac and Boston Globe:**
  - InstaTrac MuniTrac: https://www.instatrac.com/products/munitrac
  - InstaTrac home: https://www.instatrac.com/
  - Boston Globe, Jul 16, 2026: https://www.bostonglobe.com/2026/07/16/business/boston-globe-media-acquires-instatrac/
- **Government-affairs monitors:**
  - MultiState MA local monitoring: https://www.multistate.us/solutions/monitor-local-government-activity-in-ma
  - Quorum Local: https://quorum.us/products/local
  - FiscalNote PolicyNote API (local): https://fiscalnote.com/newsroom/fiscalnote-expands-policynote-api-adding-local-government-intelligence-to-enterprise-and-ai-agent-workflows
  - FiscalNote Curate: https://fiscalnote.com/products/curate
  - GovSpend FAQ (pricing model): https://govspend.com/faq/
  - Starbridge contract vehicles: https://hc.starbridge.ai/contract-vehicles
  - Civic IQ vs Starbridge (rival's claim): https://civiciq.com/civic-iq-vs-starbridge
- **Shovels:**
  - Pricing: https://www.shovels.ai/pricing
  - Decisions API: https://www.shovels.ai/blog/decisions-api-launch/
- **Siting-intelligence platforms:**
  - Heatmap Pro: https://heatmap.news/pro
  - Heatmap Pro launch: https://www.utilitydive.com/press-release/20240529-heatmap-news-announces-new-pro-platform-for-clean-energy-developers-and-inv-1/
  - SitePath: https://www.sitepathintel.com/
  - Paces: https://www.paces.com/
  - Spark: https://www.sparkhq.ai/
  - Kite: https://www.kitecompliance.ai/bess
  - Learnewable / Site Scout: https://www.pv-magazine.com/2026/08/24/ai-platform-aims-to-transform-solar-site-assessment-3/
  - Carina Energy BESS permitting guide: https://carina.energy/bess-permitting-guide/
- **Price anchors:**
  - Cleanview pricing: https://cleanview.co/pricing
  - Cleanview MA BESS projects: https://cleanview.co/battery-storage-projects/massachusetts
  - Zoneomics pricing: https://www.zoneomics.com/pricing
  - LandGate PowerTools: https://nacleanenergy.com/wind/product-suite-providing-increased-insight-into-land-resources
  - LandGate (Dealroom): https://app.dealroom.co/companies/landgate
  - LandGlide pricing (search snippet): https://landglide.com/faqs-support/subscriptions-corporate-accounts/multi-user-discount/
- **Free baselines:**
  - CivicPlus Notify Me examples: https://pa-southfayette.civicplus.com/notifyme
  - Milton, MA: https://miltonma.gov/1025/Notifications-and-Alerts
  - masspublicnotices.org: https://www.masspublicnotices.org/
  - dcmap.us policy tracker: https://dcmap.us/insights/policy/
- **Hamlet:**
  - TechCrunch: https://techcrunch.com/?p=3073247
  - Nieman Lab: https://www.niemanlab.org/2026/01/highlighting-the-funniest-moments-this-startup-aims-to-bring-public-meetings-into-the-tiktok-era/
  - Solo Founders: https://solofounders.com/blog/the-secret-2-trillion-market-close-to-home-with-sunil-rajaraman-hamlet/
- **Data-center context:**
  - Columbia Sabin blog: https://blogs.law.columbia.edu/climatechange/2026/05/27/local-moratoria-considerations/
  - Data Center Watch via States Newsroom: https://www.newsfromthestates.com/node/409512
  - Perkins Coie: https://perkinscoie.com/sites/default/files/2026-03/Siting%20and%20Land%20Use—State%20and%20Community%20Engagement.pdf
- **Rhode Island:**
  - ecoRI, Charlestown: https://ecori.org/charlestown-considers-banning-data-centers-battery-storage-facilities/
  - Westerly (Citizen Portal article, index only): https://citizenportal.ai/articles/8873247/Rhode-Island/School-Districts/Westerly/Council-enacts-one-year-moratorium-on-data-centers-to-allow-zoning-rules
- **New York:**
  - Data-center bill: https://www.mondaq.com/unitedstates/environmental-law/1803860/new-york-legislature-passes-data-center-moratorium-bill-awaits-governors-approval
  - EO 62: https://qz.com/new-york-data-center-moratorium-hochul-071426
  - Suffolk County staff report (Southold BESS moratorium extension): https://suffolkcountyny.gov/Portals/0/formsdocs/planning/scplanningcommission/2025/Z-4_Staff_Report_SD-25-02_Southold_BESS_Moratorium_Extension.pdf
- **Attorneys and diligence:**
  - Foley Hoag on AG moratorium rulings: https://foleyhoag.com/news-and-insights/blogs/law-and-the-environment/2026/march/massachusetts-ago-rejects-yet-another-municipal-solar-and-battery-storage-moratorium/
  - K&L Gates tax-equity diligence scope: https://www.klgates.com/lawyers/William-H-Holmes/experience
- **351 Watch data:**
  - `projects/351watch/data/agenda_hits_ma_all.json`, `first_seen.json`, `ag_decisions.json`, `towns_ma_all.json`, `towns_ny.json` (WIP)
  - `projects/351watch/ARCHITECTURE.md`, `projects/351watch/VALIDATION.md`
  - `projects/351watch/site/index.html`, `proof.html`
