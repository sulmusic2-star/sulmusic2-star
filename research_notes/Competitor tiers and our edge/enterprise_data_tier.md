# Enterprise and data-licensing tier of US siting intelligence: who sells local land-use data, how they source it, and where an agenda-level supplier wins

Prepared 2026-10-12 for 351 Watch (being renamed; https://351watch.vercel.app). US only. Public pages only, no accounts. About 30 searches and fetches this session.

This note extends, and does not repeat:
- `../Meeting monitor national expansion/who_needs_it_most.md` (segments; P5 "platforms as licensees"; price anchors table)
- `../Meeting monitor national expansion/data_center_and_other_fights.md` §Q4 (data-center tracker table: DCW, dcmap, Savrn, Heatmap, Cleanview, LocalGovIndex, Data Center Census, Brockovich, Citizen Portal)
- `../Meeting monitor national expansion/competitor_coverage_map.md` (coverage claims and freshness tiers) and `../Meeting monitor deep dive/durability_and_acquirers.md` (acquisitions to Jul 2026, Shovels/Hamlet/GovSpend detail)

Where a fact already sits in those notes it is referenced, not restated.

**Labels**
- **[V] verified:** read on the vendor's or government's own page this session.
- **[S] secondary:** trade press, aggregator, job-board profile, or a search-engine summary of a page that blocked direct fetch (marked "search summary").
- **[E] estimate:** my judgment or arithmetic.

**New since the earlier notes (headline facts)**
1. **Wood Mackenzie bought LandGate** (announced 24 June 2026) [V]. **S&P Global agreed to buy datacenterHawk** (28 July 2026), to combine it with 451 Research [S]. The two largest energy-data houses have each just bought a siting-data company. Neither acquired company sells local zoning, moratorium or meeting data.
2. **Enverus has shipped a "Renewable Sentiment" layer in PRISM** that includes "local moratorium and ban tracking, permitting decisions" and "years of analyst notes" [S, search summary of the Enverus blog].
3. **Delivery norms for licensed energy data are now visible**: Interconnection.fyi/GridTracker sells "monthly CSV delivery and daily Snowflake direct-share subscription options" plus an MCP server [V]; Rystad sells its data-center asset database by API and MCP [V]; Cleanview's API is a $5,000/yr add-on with keys issued by hand [V].
4. **Heatmap Pro's local-law data is a phone-and-research operation**, staffed by researchers paid $65,000–75,000 [V].
5. **No vendor in this tier publishes a jurisdiction coverage list, a measured lead time, an accuracy rate, an SLA or licence terms** [V, negative across the pages read].

---

## 1. Who sells local land-use and siting data to large buyers, at what grain, from what sources, how fresh, on what licence, at what price, to whom?

### Takeaway
The enterprise tier splits into four groups:
1. **Siting-risk platforms** (Heatmap Pro, Spark, SitePath, Paces, Kite, Learnewable, Transect, Carina). They sell county-grain risk and ordinance data by seat-based annual subscription, with no published price and no API.
2. **Energy-data majors** (Enverus, Wood Mackenzie plus LandGate, S&P Global plus datacenterHawk and 451, Rystad). They sell parcel, grid and asset data by enterprise licence and API. Their local-rule layers are thin, or come from analyst notes.
3. **Project and queue databases** (Cleanview, Interconnection.fyi/GridTracker, Grid Status, DC Byte). They sell project records at published or semi-published prices, delivered by API, Snowflake or CSV. None carries local decisions.
4. **Data-center opposition trackers** (Data Center Watch, Savrn, plus the free lists in the Q4 table). These are research products, quarterly or weekly, with no licence terms.

Sourcing is overwhelmingly **phone calls, analysts and news, plus AI over minutes or video after the meeting**. Only Spark and Kite claim agenda inputs. Carina reviews agendas and minutes by hand but publishes monthly.

### Cited Findings

**A. Vendor table**

| Vendor | Local data sold, and grain | How it is sourced | Freshness | API / licence | Price | Customers | Licenses third-party data? |
|---|---|---|---|---|---|---|---|
| **Heatmap Pro** | Opposition database by "every county, state, region, and ISO"; risk scores for "every U.S. county and zip code"; local laws for "every U.S. county and township" [V] | Opposition data: "local news coverage, Heatmap sources, and regular phone calls to all 3,100+ U.S. counties". Local laws: "sourced through regular direct calls to all 3,100+ U.S. counties". "Powered by journalism and data, not black-box AI" [V] — [Heatmap Pro](https://heatmap.news/pro). The 2025 build began "last June to call every county in the United States that had zoning authority"; "The vast majority of counties responded"; it holds 182 municipal laws in places without county zoning [V] — [Heatmap Q&A, Jul 17, 2025](https://heatmap.news/plus/the-fight/qa/heatmap-pro-charlie-clynes). A researcher posting covers "Researching energy projects and local laws", "structured datasets" and "database maintenance", at $65,000–75,000 plus equity, remote; date not shown [V] — [Heatmap job post](https://heatmap.news/heatmap-pro-is-hiring-a-researcher) | Opposition database "Updated daily". No cadence stated for local laws [V] | No API mentioned. "custom data exports" through a "Dedicated Support Team" of "Real humans to... verify findings" [V] | Demo only; annual ("for a year") [V] | AES (case study); unnamed solar, wind and data-center developers and an NGO [V] | No partner named on the Pro page [V]. Heatmap's public restriction articles build on Sabin data (prior note) |
| **Spark** (sparkhq.ai) | "3,000+ counties", "down to county and township levels"; parcel search and diligence briefs [V] | "town hall and commission minutes, meeting videos, project filings and permit records, zoning ordinances and moratoria, local news, and community social media"; pipeline "crawl → extract → normalize → index → cite"; "purpose-built extractors". No human analysts or calls mentioned [V] — [Spark](https://www.sparkhq.ai/) | "Daily" on the homepage; "crawls multiple times per week" in the FAQ (conflict) [V] | No API or licence mentioned; "alongside GIS and mapping tools"; exportable briefs; SOC 2 [V] | "Annual software subscription. Pricing typically depends on seats + usage volume"; a "Free for developers" diligence report on a county, township or parcel [V] | Clenera, Colliers Engineering, Doral, Dynamic Energy, Intersect Power, NextEra, Standard Solar, Stellera, Summit Ridge [V] | None named [V] |
| **SitePath Intelligence** | "Every U.S. county is graded", 0–100 risk score; setbacks, active moratoria, caps, approved and denied projects, ordinance text, board membership [V] — [SitePath](https://www.sitepathintel.com/) | "Every figure cited to a primary document"; "If a value cannot be verified against a primary document, it is not published"; sources include board minutes, ordinances, state filings and IRPs; "Source-document depth varies" [V]. Launch release: "thousands of jurisdictions", "links every record to its original public source", flags data gaps, "preserves historical changes" [V, vendor release] — [Utility Dive press release, Aug 7, 2026](https://www.utilitydive.com/press-release/20260807-sitepath-intelligence-launches-county-level-permitting-intelligence-platfor-1/) | Not stated [V] | Not mentioned [V] | "Priced to your team" by size and seats; free map and free email alert [V] | None named. Its launch drew "more than 20 demonstration requests" in 48 hours. Founder Jaimie Henderson; founded 2026 [V, vendor release] | None named |
| **Paces** | "Power and Permitting Reports" for sites; no zoning, moratoria or opposition fields named [V] — [Paces](https://www.paces.com/) | "AI Agent autonomously completes key workflows", "backed by world-class data and human expert validation" [V] | Not stated | Not mentioned | Demo only | Demeter Land Development, Qcells ("over a thousand parcels in Illinois that our GIS team had missed"), onCORE Origination [V]. $11M Series A, 48 people (prior note) | Relies on unnamed "world-class data" [V], so it is a data buyer by construction [E] |
| **Kite** (kitecompliance.ai) | BESS Risk Monitor on "moratoria, public agendas, meeting activity"; Permit Matrix by jurisdiction; project precedents [V] — [Kite BESS](https://www.kitecompliance.ai/bess) | "Each item links back to the underlying public record". Method not stated. Also sells "Engagement Execution", including hearing preparation and testimony support [V] | Keeps "each jurisdiction's ordinance posture current"; no cadence [V] | Login only; no API [V] | Demo only | None named; New York address [V] | None named |
| **Learnewable / Site Scout** | County map; opposition sentiment, regulatory factors, "names and contact information of key stakeholders" [S] — [pv magazine](https://www.pv-magazine.com/2025/10/27/ai-platform-aims-to-transform-solar-site-assessment/) | "public records, local news and social media"; transcribes meetings "posted to YouTube"; uses "multiple AI models" (founder Jeremy Solomon) [S]. Founded 2023 [S] — [Solar Power World](https://www.solarpowerworldonline.com/2025/04/learnewable-ai-insights/) | Not found | Not found | Not found | Not found | Not found |
| **Transect** | Local Solar Regulations (beta, county). Risk Monitor alerts on federal and state permits, regulations and species; zoning appears only as a parcel layer (Mar 2025 release notes) [S, search summary of Transect help pages] — [Risk Monitor](https://support.transect.com/risk-monitor), [Release notes](https://support.transect.com/release-notes) | Not stated | Alerts "whenever key data points are updated" [S] | No API documentation found [S] | Subscription by quote (prior note) | Developers (prior note) | Not found |
| **Carina Energy** (Carina Power Partners LLC, Madison WI) | BESS moratorium database: 15+ fields; Status ACTIVE / EXPIRED / PENDING / LIFTED / UNDER_REVIEW; Scope; Type MORATORIUM / BAN / ZONING_AMENDMENT / SETBACK [V] — [Carina](https://carina.energy/bess-moratoriums/) | "Updated monthly using AI-powered legislative monitoring"; "combines automated news scanning with manual review of government agendas and meeting minutes"; "Each record is verified before publication" [V] | Monthly data; weekly email alerts; Excel export [V] | Subscription; attribution to "Carina Energy's BESS Moratorium Tracker" required; journalists can request extracts [V] | Not stated | "READ BY HUNDREDS OF BESS PLAYERS" (five logos, unlabelled) [V] | None. Carina is a **development-services firm** (origination, permitting, interconnection) whose tracker is a lead magnet [V] |
| **LandGate** (Wood Mackenzie since Jun 2026) | Value scores from "200-plus public datasets" for nearly every US acre; "more than 150 million land parcels"; transmission grid; "large-load demand" [V] — [WoodMac release, Jun 24, 2026](https://www.woodmac.com/press-releases/wood-mackenzie-acquires-landgate-to-deliver-connected-intelligence-for-the-new-era-of-us-power-markets/) | Public datasets; Topos AI diligence bought Dec 2025 (prior note) | Not stated | To be folded "into our platform" (Wood Mackenzie) [V] | Not published; terms of the deal undisclosed [V] | Data-center, power and renewables developers (unnamed) [V] | Yes, it is built on public datasets. No zoning, moratoria or local regulation is mentioned in the deal release [V] |
| **Wood Mackenzie** | Power-market forecasting plus LandGate land and grid data [V] | Analysts plus acquired data | — | Enterprise platform | Not published. Cleanview cites "$40,000–80,000 annual contracts" for WoodMac, S&P and New Project Media [V, Cleanview's claim] — [Cleanview pricing](https://cleanview.co/pricing) | Utilities, developers, investors | **Buys data companies** (LandGate) [V]. Owned by Veritas Capital [S] — [KippsDeSanto](https://www.kippsdesanto.com/experience/landgate-corp-wood-mackenzie) |
| **S&P Global** (451 Research + datacenterHawk) | 451 data-center forecasts plus datacenterHawk "asset-level" supply, demand, pricing, pipeline and site-selection data, and Fiber Locator [S] — [S&P press, Jul 28, 2026](https://press.spglobal.com/2026-07-28-S-P-Global-to-Acquire-datacenterHawk-Connecting-Global-Data-Center,-Power-and-Infrastructure-Markets) | datacenterHawk: "team of analysts checks every data point"; 10,000+ data points from 35+ markets (2022) [S] — [BusinessWire 2022](https://businesswire.com/news/home/20220602005271/en/datacenterHawk-Reports-Data-Center-Demand-at-an-All-Time-High-Across-North-America-Europe-and-APAC-Markets) | Quarterly recaps [S] | Enterprise | Not published; deal "not expected to have a material impact" [S] | Operators, investors, vendors, brokers, consultants [S] — [CB Insights](https://www.cbinsights.com/compare/datacenterhawk-vs-dc-byte) | **Buys data companies.** One syndicated copy says the deal closed Sep 1, 2026 [S, unconfirmed]. No S&P local-siting-restriction product found [S, negative search] |
| **Enverus** (power and renewables) | "Renewable Sentiment" in PRISM for customers with "Parcels and Suitable Land Analytics"; example: Lincoln County, NE with "two Wind Moratoriums and one wind ordinance" [S, search summary; blog returned 403] — [Enverus blog](https://www.enverus.com/blog/renewable-sentiment-the-siting-signal-youre-not-tracking/) | "public regulatory signals, news, local moratorium and ban tracking, permitting decisions, governmental research like NREL, and years of analyst notes" [S, search summary] | Not found | Enterprise PRISM module | Not published; a rival estimates $10–50k/yr (prior note) | Developers, utilities | **Yes: it uses NREL research** [S]. Serial acquirer (Energy Acuity, RatedPower; prior note) |
| **Rystad Energy** | Data centers: "Asset-level project database with power strategies, risk scores, and development timelines"; no permitting or opposition named [V] — [Rystad](https://www.rystadenergy.com/services/data-center-solution) | Not stated | "Real-time monitoring" (marketing) [V] | **API and MCP**; Spektra workspaces; "Live data in Excel, Python, Power BI" [V] | Not published | Hyperscalers, investors, banks, utilities (target list) [V] | Not stated. Relevant only as an asset-level buyer [E] |
| **DC Byte** | Data-center supply, pipeline, planning [S] | "no substitute for firsthand data gathering"; "validating sites through planning applications"; clients see "planning documentation, site imagery, or local permits"; rejects "calling the right person" as "not scalable"; "50 team members", half analysts "embedded in key regional markets" [S, founder interview] — [W.Media](https://w.media/from-data-gaps-to-global-insights-edward-galvin-on-the-mission-behind-dc-byte/) | "quarterly reviewed insights" [S, search summary] | Not stated | Not published | Hyperscalers, developers, suppliers, metals traders [S] | Not stated. Reads planning applications by analyst [S] |
| **Cleanview** | Data-center and power-project records; API endpoints: Data Centers ("capacity, tenants, and locations"), Interconnection Queues (ERCOT, CAISO, PJM, MISO, SPP, NYISO, ISO-NE), EIA 860M, Unified Power Projects [V] — [Cleanview API docs](https://docs.cleanview.co) | Its "data center database, EIA records, and interconnection queue information" [V] | "Real-time Data" (no cadence) [V] | API key "provisioned by the Cleanview team"; no licence terms or rate limits published [V] | $9,000/yr per platform; **API +$5,000/yr**; $4,900 one-time download; $18,000/yr research [V] — [Cleanview pricing](https://cleanview.co/pricing) | None named [V] | Yes, public EIA and ISO data. **No local zoning, moratoria or opposition fields** [V] |
| **Interconnection.fyi / GridTracker** | 44,281 queue requests (1995–2026) from "50+ ISOs and utilities"; data-center projects by state; DG requests [V] — [Interconnection.fyi](https://www.interconnection.fyi/) | Public ISO and utility queue files | "at least once a day" [V] | Free list view; GridTracker gates names, contacts, documents and export; **"monthly CSV delivery and daily Snowflake direct-share subscription options"**; **MCP server** [V] | Not listed [V] | LBNL "Queued Up" cites GridTracker as a data source [V] | Its data is licensed *to* others; no local permitting [V] |
| **Grid Status** | ISO market and queue data [S] | Open-source BSD-3 library over ISO sources [S] — [GitHub](https://github.com/gridstatus/gridstatusio) | Live | Hosted API; free tier of 500,000 rows/month; enterprise Snowflake delivery [S] — [apis.io profile](https://apis.io/plans/gridstatus/gridstatus-plans-pricing/) | Paid tiers not captured (pricing page returned 403) | Not found | No local data [S] |
| **LevelTen**, **Anza** | No local permitting or zoning data found. LevelTen is a PPA marketplace; Anza is equipment procurement and pricing analytics [S, negative searches] — [Built In: Anza](https://www.builtinnyc.com/company/anza-renewables) | — | — | — | — | — | Possible downstream consumers of a project-risk field, not suppliers [E] |
| **Savrn** | 1,233 local data-center measures (prior note); statuses "In force", "Paused", "Proposed", "Failed / vetoed", each dated [V] — [Savrn tracker](https://savrn.com/data-center-moratorium-tracker) | "adds a jurisdiction only once a primary source for its specific action has been read"; "Every week we re-verify every state and local measure" [V]. The page shows duplicate rows and status labels that contradict their own descriptions [V] | Weekly | No licence, API or download terms on the page [V] | Tracker free; weekly email | — | Savrn is an AI-infrastructure company (Index, Cloud, site-screening "Intelligence"); the tracker is marketing [V] |
| **Data Center Watch** (funded by 10a Labs) | Quarterly blocked and delayed project counts; "In-Depth Analysis" with "full project-level data, case studies, and political analysis" [V] — [DCW Q1 2026](https://datacenterwatch.org/q1-2026) | Not described on the page [V]. 10a Labs is "an applied research and technology company specializing in AI security", ~28 staff, serving "AI unicorns, Fortune 10 companies" [S] — [Built In](https://builtin.com/company/10a-labs) | Quarterly | No licence terms; deck sold online; in-depth by email [V] | Not shown | Press and AI-company clients of 10a Labs [S] | Not stated |

**B. Sourcing patterns visible in hiring and methods**
- **People who phone counties.** Heatmap hires researchers at $65–75k to build "structured datasets" of local laws [V] — [Heatmap job](https://heatmap.news/heatmap-pro-is-hiring-a-researcher). Shovels runs "Project Storm" phone and records requests (prior note).
- **Embedded analysts.** At DC Byte, half of 50 staff are analysts in regional markets [S]. At datacenterHawk, "analysts check every data point" [S].
- **AI over posted documents or video after the meeting.** Spark crawls minutes and videos [V]; Learnewable transcribes YouTube [S]; Carina uses "AI-powered legislative monitoring" plus manual review [V].
- **Analyst notes plus public research.** Enverus combines analyst notes with NREL data [S].
- **No vendor read this session describes reading agenda packets or legal notices before the meeting at township grain** [V, negative across pages read].

### Inferences
- [E] **Labour is the cost these vendors carry.** Assume one $70k researcher handles about 300–500 counties at quarterly re-call depth. On that assumption, covering all 3,100 counties takes 6–10 researchers, about $0.5–0.8M a year loaded, before any township. That is the budget a supplier displaces. This is arithmetic on the Heatmap salary band, not a reported headcount.
- [E] **The majors are consolidating land, grid and asset data, not local decisions.** WoodMac–LandGate and S&P–datacenterHawk both bought parcel and asset layers. The local-rule layer is still analyst notes (Enverus) or absent (S&P, Rystad, Cleanview). That is the empty seat a supplier can fill inside their platforms.
- [E] **Prices cluster in two bands.** Self-serve or published: Cleanview $9k + $5k API; LocalGovIndex $399/mo to $2,500+/mo with API (prior note). Enterprise: $40–80k by Cleanview's account of WoodMac and S&P. No siting-risk platform publishes a price.

### Gaps
- No price was found for Heatmap Pro, Spark, SitePath, Kite, Paces, Learnewable, Transect, Carina's full database, Enverus PRISM's sentiment module, Rystad, DC Byte, datacenterHawk, DCW in-depth or GridTracker.
- The Heatmap researcher posting is undated, so current team size is unknown.
- The Enverus blog (403) and the Grid Status pricing page (403) were read only through search summaries.
- The close of S&P–datacenterHawk rests on one syndicated copy.
- No job posting at Spark, Paces, SitePath, Kite or Transect for agenda or minutes analysts surfaced in search.
- Wood Mackenzie's and S&P's own US local-policy products: none found by search. This is a negative result, not proof of absence.

---

## 2. Where is local, pre-meeting, township-grain data missing from each?

### Takeaway
Every vendor misses at least two of the three properties: **pre-meeting timing, township or town grain, and a structured status lifecycle with source links**. The closest are:
- **Spark**: township claimed, agendas implied, but "where public online sources exist" and no list.
- **Kite**: "public agendas", but BESS only and no coverage claim.
- **Carina**: reads agendas, but publishes monthly and covers BESS moratoria only.

The majors and project databases carry no local-decision records at all.

### Cited Findings
| Vendor | Pre-meeting? | Township/town grain? | Lifecycle + source link? | Main hole (evidence) |
|---|---|---|---|---|
| Heatmap Pro | No: calls and news [V] | Laws "every county and township" claimed; 182 municipal laws noted [V] | Opposition DB yes; laws are snapshots | Learns of township actions when a county answers the phone or news reports them [V/E] |
| Spark | Partly: crawls minutes, video and ordinances [V] | Claimed [V] | Cites sources [V] | "multiple times per week" crawl of *posted* minutes; no township list (prior note) |
| SitePath | No: "board minutes, ordinances" [V] | County graded; "municipal" in release [V] | Primary-doc citations, history kept [V] | MA pages show "No tracked activity yet" (prior note) |
| Kite | Claims "public agendas" [V] | Not stated | Links to record [V] | BESS only; no coverage list |
| Carina | Reviews agendas and minutes [V] | Jurisdiction | Status enum, 15+ fields [V] | Monthly; BESS moratoria only. Carina itself says moratoria "may not appear in databases for weeks or months" (prior note) |
| Learnewable | No: YouTube video [S] | County map [S] | Not stated | Rural boards without video are invisible [E] |
| Transect | No | County [S] | Not stated | Zoning is a static parcel layer [S] |
| Enverus | No: analyst notes and news [S] | County example [S] | Unknown | Sentiment layer, not event feed [E] |
| WoodMac/LandGate, S&P/dcHawk, Rystad, DC Byte | No | Parcel or asset, not jurisdiction rules | No | No local-decision product found |
| Cleanview, Interconnection.fyi, Grid Status | No | Project or queue | Project status only | "No local zoning, moratoria or opposition" [V] |
| Savrn, DCW | No: adopted or blocked measures [V] | Local, but "a floor" (prior note) | Savrn statuses dated [V] | Weekly or quarterly; data centers only |

- **Statutory review gives a pre-meeting window in township states.** Ohio: a township zoning amendment must be sent to the county or regional planning commission "within five days after the adoption of the motion"; the township hearing is set "not less than twenty nor more than forty days" out; notice runs "at least ten days before" [V] — [ORC 519.12](https://codes.ohio.gov/ohio-revised-code/section-519.12). Michigan: a township "shall submit for review and recommendation the proposed zoning ordinance" to the county zoning commission, which has 30 days [V] — [MCL 125.3307](https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-125-3307).

### Inferences
- [E] **The missing product is a pre-meeting event feed at town and township grain with a status lifecycle.** Every incumbent holds either the rule after adoption (Heatmap, SitePath, Transect, Enverus) or the project (Cleanview, majors). The event between those two, from proposal through hearing to vote, is the gap.
- [E] **County planning-commission agendas in OH and MI carry township amendments 20–40 days before the township acts.** Monitoring about 88 Ohio and 83 Michigan county planning bodies reaches thousands of townships early. County-grain incumbents read these agendas, if at all, as county items, not as township signals.
- [E] **BESS and data-center trackers (Carina, Savrn, DCW) are single-topic.** A multi-topic schema (solar, BESS, data center, moratoria, zoning, towers, wetlands, housing) is itself a gap.

### Gaps
- No vendor's actual lead time could be measured without accounts.
- PA (MPC county review) and WI and MN county review rules were not checked this session.

---

## 3. Supplier to platforms, or compete directly?

### Takeaway
Lead as a **supplier**, with a narrow direct product kept for segments the platforms underserve (BESS and community-solar developers, counsel) [E]. The platforms already pay for this data with labour (Heatmap's researchers, Carina's manual review, DC Byte's analysts), and the majors have just shown they buy rather than build (WoodMac–LandGate, S&P–datacenterHawk, LandGate–Topos, Shovels–ReZone). The main risks are copying (Spark and LocalGovIndex already crawl) and channel conflict once a direct tier sells to the platforms' own customers.

### Cited Findings
- Majors buying siting data in 2026: Wood Mackenzie–LandGate (Jun 24) [V] — [WoodMac](https://www.woodmac.com/press-releases/wood-mackenzie-acquires-landgate-to-deliver-connected-intelligence-for-the-new-era-of-us-power-markets/); S&P–datacenterHawk (Jul 28) [S] — [S&P press](https://press.spglobal.com/2026-07-28-S-P-Global-to-Acquire-datacenterHawk-Connecting-Global-Data-Center,-Power-and-Infrastructure-Markets). Earlier deals are in `durability_and_acquirers.md` §2.
- Platforms that rely on bought or public data: Paces cites "world-class data" [V]; Enverus uses NREL research [S]; Cleanview resells EIA and ISO data [V]; LBNL cites GridTracker [V].
- Platforms already doing the job by hand: Heatmap calls counties and hires researchers [V]; Carina reviews agendas manually [V]; DC Byte analysts read planning applications [S].
- Copy-capable competitors: Spark crawls minutes and video "multiple times per week" [V]. LocalGovIndex reads agendas for 2,823 governments and sells an enterprise API at $2,500+/mo (prior note, Q4).
- Delivery norms buyers already accept: Snowflake share, CSV, MCP (Interconnection.fyi [V]; Grid Status [S]); API plus MCP (Rystad [V]).

### Inferences
**Supplier model [E]**
- **For.** It needs few deals: there are about 10–15 platforms plus 4 majors. Platforms carry the sales cost to 389 data-center and ~150 BESS developers (counts in prior note). Labour displacement gives a hard ROI. Attribution clauses create the citations that feed the free tier.
- **Against.** Platforms cap the price at their cost to replicate. A single large licensee can become dependent revenue. They can learn the coverage list and crawl it themselves.

**Direct model [E]**
- **For.** Higher price per buyer. Owns the customer relationship. Published prices are a channel no rival uses.
- **Against.** It competes with Heatmap, Spark and SitePath for the same IPP buyers, against their sales teams, brands and polling. And it makes the platforms unwilling to license.

**How to reduce the risks [E]**
1. **Copying.**
   - Licence the **records**, not the coverage list or source map.
   - Keep the crawl schedule, OCR and county-review linkage private.
   - Price so that buying stays cheaper than building one state's crawl.
   - Hold history (point-in-time archive), which a late copier cannot recreate.
2. **Channel conflict.**
   - Split by product shape. Platforms get bulk and API records with a 24–72-hour embargo option or none.
   - The direct tier serves town-level alerts for small developers, counsel and consultants, a segment the platforms do not price for.
   - Do not sell bulk to end developers who are a licensee's named accounts during the term, or offer that as a paid exclusivity.
3. **Concentration.** Non-exclusive by default. Exclusivity only per state, time-boxed (12 months), and priced as a premium.
4. **Acquirer optionality.** Being a supplier to WoodMac, S&P or Enverus is also the usual route to acquisition (see `durability_and_acquirers.md` §2c: buyers pay for early signal and archive).

### Gaps
- No platform publicly states that it licenses local-decision data from a third party, so willingness to buy is inferred from labour and acquisitions, not observed.
- No licence fee benchmarks for local-decision data were found. The nearest anchors are Cleanview's $5k API add-on, LocalGovIndex's $2,500+/mo enterprise tier and Cleanview's $40–80k account of the majors.

---

## 4. What must a data licence include to be bought?

### Takeaway
Buyers of licensed data check six things before signing [S]:
1. point-in-time history with an append-only guarantee and a restatement policy;
2. coverage proof, including gaps during the periods that matter;
3. methodology;
4. delivery in their stack (API, Snowflake share, CSV, MCP);
5. accuracy evidence;
6. stable identifiers that join to their own entities.

No siting vendor read this session publishes any of these. Publishing them is a differentiator in itself [V, negative].

### Cited Findings
- Buyer diligence norms from alt-data checklists:
  - "Is history point-in-time, and what is the restatement policy?" [S] — [FlashAlpha](https://flashalpha.com/articles/options-data-vendor-due-diligence-checklist)
  - "Methodology and point-in-time integrity almost never come up in the first call and almost always come up before signature" [S] — [Guideline](https://www.guideline.ai/capital-markets-seo/alternative-data-vendor-due-diligence)
  - Buyers ask for "point-in-time samples and the append-only guarantee, plus coverage-uptime history", and churn vendors over "time-series gaps" [S] — [Actowiz report](https://www.actowizsolutions.com/alternative-data-industry-report-2026-funds-insurers-buying.php)
  - Buyers test whether a vendor "backfilled historical records using information unavailable at the time" [S] — [PracHub](https://prachub.com/interview-questions/evaluate-alternative-data-for-an-investment-pitch)
  - All four are vendor or marketing sources; no neutral standard was found.
- Delivery norms in energy data:
  - GridTracker: monthly CSV, daily Snowflake share, MCP [V]
  - Grid Status: API row quotas, Snowflake for enterprise [S]
  - Rystad: API and MCP [V]
  - Cleanview: API key by hand, no published rate limits [V]
- Schema precedents:
  - Carina status enum ACTIVE / EXPIRED / PENDING / LIFTED / UNDER_REVIEW with Scope and Type [V]
  - Savrn In force / Paused / Proposed / Failed [V]
  - Shovels Decisions statuses proposed / discussed / approved / disapproved / postponed (prior note)
  - SitePath "preserves historical changes" and "flags data gaps" [V]
  - Carina requires attribution [V]

### Inferences
**Minimum licence package [E]**
1. **Schema and IDs**
   - Stable `item_id`; `jurisdiction_id` keyed to Census GEOID or GNIS codes for county subdivisions and places; `body_id` (planning board, ZBA, select board, township trustees, county planning commission).
   - `topic` (multi-label) and `action_type` (moratorium, rezoning, special permit, bylaw or ordinance amendment, site plan, NOI or wetlands, tower).
   - Project and applicant, with entity resolution to LLC, parent and developer.
   - Parcel or address where stated; `meeting_datetime`; `source_url` plus a hash of the archived PDF.
2. **Lifecycle**
   - Stages: proposed, noticed, hearing scheduled, continued, recommended (including county review), adopted or denied, withdrawn, AG or state review, appealed, expired.
   - Each transition carries a timestamp and a source, append-only.
3. **Lead-time fields**
   - `first_seen_at` (our crawl), `agenda_posted_at` (from source metadata), `meeting_at`, `decision_at`.
   - Derived lead time is published per record, with distributions per state.
4. **Coverage proof**
   - A machine-readable list of every body crawled, with source URL, platform (CivicPlus, Granicus and others), last successful crawl and the gap log.
   - "Known not covered" listed explicitly.
5. **Accuracy audit**
   - A quarterly sample (e.g., 400 random items) hand-checked for precision on topic and status.
   - A recall test against an outside list (Carina, Savrn, Sabin, AG decisions); results published.
6. **History**
   - Point-in-time backfill as far as archived agendas go, flagged `backfilled=true` with the date of capture, so buyers can separate real-time records from reconstructed ones.
7. **SLA**
   - Crawl frequency per body (e.g., daily); item latency from posting (e.g., p90 under 24h); API uptime; a restatement notice period.
8. **Delivery**
   - REST API plus webhooks, a daily Snowflake or S3 drop, monthly CSV and an MCP endpoint.
9. **Licence terms**
   - Internal use plus display in the licensee's product with attribution.
   - No resale of raw bulk; a derived-works clause.
   - State-level scoping and pricing.
   - Term and renewal; a non-exclusive default.

### Gaps
- No published licence agreement from any siting vendor was found to benchmark terms.
- SLA norms in this niche are unknown. The checklists above are finance-side.

---

## 5. What makes the edge defensible here?

### Takeaway
Five assets compound, and none can be bought after the fact:
1. **published coverage lists**, where no rival publishes one;
2. **measured lead time per record**, where no rival measures it;
3. **township reach through county reviews** in Ohio and Michigan, which are statutory and pre-meeting;
4. **verified-bot access** to blocked municipal sites;
5. **a cost per jurisdiction** below the labour model of phone-and-analyst incumbents.

The weakest of these is crawl capability alone. Spark and LocalGovIndex already crawl.

### Cited Findings
- No coverage lists: none of Heatmap, Spark, SitePath, Kite, Paces, Learnewable, Transect or Carina publishes a jurisdiction list [V, pages above]; also prior note `competitor_coverage_map.md` §1.
- No lead-time measures: none of the pages read states lead time. Freshness claims are "Updated daily" (Heatmap opposition), "multiple times per week" (Spark), "monthly" (Carina), "weekly" (Savrn), "quarterly" (DCW, DC Byte) [V/S].
- Labour model: Heatmap researchers at $65–75k [V]; DC Byte has about 25 analysts [S]; datacenterHawk analysts check "every data point" [S].
- County review windows: ORC 519.12 and MCL 125.3307 [V].
- Acquirers pay for early signal and archive (prior note `durability_and_acquirers.md` §2c).

### Inferences
1. **Coverage lists [E].** They turn "trust us" into a checkable claim and are the first diligence ask. They also expose gaps, so publish them with the gap log. A rival can copy the list but not the run history behind it.
2. **Measured lead time [E].**
   - `first_seen_at` against `meeting_at` and `decision_at` on every record is proof no incumbent can backfill: a call-based or minutes-based source cannot show a timestamp before the meeting.
   - Publish the median and p10 lead time by state and topic, and compare against the first appearance in Heatmap or Savrn where public.
3. **Township reach through county reviews [E].**
   - In OH (and MI after the township hearing), county planning-commission agendas carry township amendments with text and maps.
   - Reading about 170 county bodies yields early township signals across thousands of townships.
   - This gives the "township grain" claim a cheap, defensible mechanism. It needs state-by-state statute work, a moat that compounds as states are added.
4. **Verified-bot access [E].** Where municipal sites sit behind Cloudflare or Vercel challenges, an identified, rate-limited crawler with clerk permission keeps access that anonymous copiers lose. This needs evidence. Earlier notes found Hamlet and Citizen Portal behind challenges, and the coverage map notes 403s on several sites.
5. **Cost structure [E].**
   - An automated agenda, packet and OCR pipeline costs cents to dollars per body-month in compute (an assumption, not measured here).
   - A $70k researcher covers a few hundred counties at quarterly depth.
   - At licence prices near Cleanview's $5k API add-on per platform per state bundle, the supplier is profitable where a platform's in-house build is not.
6. **What is not a moat [E].**
   - "We read agendas": Spark, Kite, LocalGovIndex, Hamlet and MultiState all claim it (prior notes).
   - AI summarisation.
   - Single-topic trackers, which are free (Savrn, dcmap, Carina's public map).

### Gaps
- Bot-access advantage is asserted, not measured. No count of blocked municipal sites by state was made this session.
- Compute cost per body-month for 351 Watch's pipeline was not measured here.
- PA, WI and MN county-review statutes, which would extend the township-reach mechanism, were not read.
