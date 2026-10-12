# Professional (paid, multi-place) tiers of US local-government monitors: feature matrix and where a new service can win

Checked 2026-10-12 for the product now called 351 Watch (being renamed; https://351watch.vercel.app).

This note extends the following and does not repeat them. Coverage maps, topic tables and list prices are in those files.
- `../Meeting monitor national expansion/competitor_coverage_map.md`
- `../Meeting monitor deep dive/competitor_behind_login.md`, which has the Hamlet API and Citizen Portal evidence.
- `../Product strategy/where_we_win.md` §1
- `../Product strategy/free_tier.md`
- `../Meeting monitor national expansion/data_center_and_other_fights.md`, which has the first LocalGovIndex read.

**Labels** (per the brief):
- **[V] verified:** I read it on the vendor's own page, docs, API reference or pricing page this session, or it was verified in a cited earlier note.
- **[S] secondary:** a third-party page, review site, competitor's claim, or a search-engine quote of a page I could not load.
- **[E] estimate:** my inference or arithmetic.

**How this was checked:**
- No accounts were created. Public pages only.
- The following were blocked to the fetcher and were read only through search quotes:
  - fiscalnote.com/policynote-api-pricing (403)
  - g2.com/products/quorum (403)
  - civiciq.com
  - myhamlet.com and citizenportal.ai (see the earlier notes)
- api.gathergov.com/docs rendered only its title.
- The session's usage limit interrupted this work once. The search budget therefore went to the products with the most buyer overlap.

**The planned paid tier, for reference:**
- many areas in one feed
- routing of alerts to different channels
- faster refresh
- company watch (LLC to parent)
- exports and an API
- decision history

---

## 1. Feature-by-feature matrix of paid professional tiers

### Takeaway
Only four products in this space publish a self-serve professional price for **multi-place monitoring of local agendas**:
- LocalGovIndex Professional: $399/mo
- Citizen Portal: $12–49/mo, a consumer product
- MyTownView All Access: $2,499/yr
- OrdinanceWatch: a 30-day trial, but prices by phone, Florida and Georgia only

Everyone else falls into one of these groups:
- **Enterprise government-affairs suites:** Quorum (about $21k/yr median), FiscalNote (about $47k/yr median) and MultiState (unpublished).
- **Sales-led national indexes:** GatherGov, Hamlet and Civic IQ.
- **Adjacent data products** that publish prices but do not watch agendas: Shovels, Zoneomics, Reonomy, ConstructConnect and BillTrack50.

Across the whole field:
- **No product combines all of these:** Slack/Teams/webhook routing, a published per-place coverage list, a proposed-to-adopted status lifecycle, and LLC-to-parent company watch.
- **Every product that offers webhooks or an API puts it at enterprise prices or behind sales.**
- **Human verification is sold only by MultiState and Zoneomics.** MultiState's analysts read every document and call towns. Zoneomics reports are "authenticated by our Zoning Analysts".

### Cited Findings

The matrix is split into three tables with the same rows. Each row's sources are listed under Table C.

**Table A: coverage, timing, topics**

| Product / paid tier | Coverage grain and count | Published per-place list | Pre- or post-meeting | Refresh speed | Topics and custom keywords |
|---|---|---|---|---|---|
| **LocalGovIndex Professional** ($399/mo) and **Enterprise** ($2,500+/mo) | Places, bodies, officials. Coverage page: **12,214 "Places", 51 states, 192,053 officials, 6,285,951 meetings, 30,555,125 documents** [V]. The 2,823 governments in an earlier read [V earlier] conflicts with this; "Places" probably includes school districts [E]. Townships are not mentioned [V] | Place pages exist with state navigation. No downloadable list was seen [V] | **Both.** Free tier: "agenda summary before each meeting, recap after" [V] | Not stated. "4,535 meetings today" counter [V] | Follow "any place, official, item, or topic" [V]. Topic dossiers, e.g. data centers [V earlier] |
| **Hamlet** (paid / enterprise) | City, county, state only. There is no TOWN or TOWNSHIP type in the API [V]. 2,011 cities and 453 counties [S] | Per-state coverage page [S] | Both: agenda objects with "agenda-monitoring topics" [V]; transcripts after the meeting [V] | Weekly, "moving to daily" [S, earlier note] | Topic subscriptions per government body [V]; saved searches and keyword alerts [S] |
| **GatherGov** (sales-led) | "9300+ jurisdictions including towns and counties"; "735K+ agendas & minutes"; "25+ municipal boards" [V] | Coverage map only [V] | **Post-meeting**: "Meetings searchable within 24 hours" [V] | Within 24 h of the meeting [V] | Search by keyword. Playbooks show "who's behind them" [V] |
| **Citizen Portal** (paid) | Individual bodies, including rural townships, after the meeting [S, earlier] | No | Mostly post-meeting recaps; rare agenda previews [V earlier] | Not stated | 2, 10 or 50 topic alerts by tier [S earlier] |
| **Quorum Local** | "all counties and cities of 3,000 or greater"; "over 12,500 sources" [V] | No | Pre-meeting: agendas and minutes [V] | "near real-time … scans … each day" [V] | Issue keywords. Quincy AI surfaces "decisions and changes most relevant" [V] |
| **MultiState** (local) | ">4,850 jurisdictions", including "municipalities, counties, townships, and special districts" [V] | No | **Pre-meeting**: analysts "identify upcoming action" [V] | "Snapshots go out each hour when new information is available" [V] | Custom per client. Can extend to "ballot measures, social media, news reports" [V] |
| **FiscalNote PolicyNote / Curate** | ">12,000 US cities and counties, 4,000+ school districts, 200+ state boards"; "400,000+ meeting minutes, agendas, and planning documents" a week [S, press release] | No | Agendas and minutes [S] | GatherGov says Curate runs a "Weekly refresh cycle typical" [S, competitor claim] | "600+ expert topics" with agenda snippets [S, search quote of pricing page]. Reviewers: alert setup "can be complex" [S] |
| **Civic IQ** | "100,000+ agencies"; "80,000+ agencies across all 50 states"; "30K+ public meetings monitored monthly" [S] | No | Pre-RFP signals, "6 to 18 months before formal RFPs" [S earlier] | Not stated | Matches "what you sell" (procurement) [S] |
| **Agenda Watch** (Big Local News / RJI) | At launch: four regions (Atlanta/GA, Philadelphia/PA, Los Angeles, SF Bay Area), drawing on a catalogue of 90,000+ agency sites [S] | No | Pre-meeting (documents harvested daily) [S] | Daily [S] | Topic search with "alerts when similar items crop up" [S] |
| **OrdinanceWatch** | **Florida: 67 counties and 326 cities. Georgia: 13 counties and 40 municipalities** [V] | **Yes**, per state [V] | **Pre-meeting**: "advance notice on pending local government council and commission action" [V] | "real time" (not defined) [V] | **128 issue categories** [V] |
| **BillTrack50** | State legislatures, Congress and regulations. **Only the DC City Council locally** [V] | n/a | n/a (bills) | Daily email alerts [V] | Keyword searches on bills [V] |
| **Govlaunch-like B2G tools** (Govlaunch, GovSpend, Starbridge, Vendor Registry) | Govlaunch is a free wiki for governments; vendors pay [S]. GovSpend: 10,000+ agencies. Starbridge: 320,000+ entities [V earlier] | No | GovSpend reads agendas and packets daily [V earlier] | Daily (GovSpend) [V earlier] | Procurement and sales signals, not land use [E] |
| **Shovels** (Basic $599, Pro $999/mo) | Permits nationwide. Decisions in "600+ cities" [V earlier] | No | **Post-decision**: no record "until the minutes are posted" [V earlier] | Not stated | Permit filters and Decisions categories [V earlier] |
| **Zoneomics** (Essentials $92, Advanced $279/mo) | "10000+" cities' zoning codes digitized; "100M+" parcels [V] | No | Neither: code text, not meetings [V] | Not stated | Zoning search [V] |
| **ConstructConnect** | ">825,000 active public and private projects across 400+ North American markets" [S] | No | Projects at five stages, from conceptual to post-bid [S] | Not stated | Project search; planning projects only on the higher tier [S] |
| **Dodge Construction Central** | National project leads. "3,000 municipalities, 19,000+ web sources" is a third-party claim [S, unverified] | No | "Pre-design" stage: "awaiting financing, land acquisition, review agency approvals" [S, Dodge help glossary via search] | "adds or updates 6,500 jobs every day" (company claim) [S] | Project types [S] |
| **Reonomy** | Commercial property ownership, nationwide [S] | n/a | n/a | n/a | n/a (ownership data, not monitoring) |
| **Spark / Heatmap Pro** (siting tools, from earlier notes) | County grain. Townships "where public online sources exist" (Spark) [V earlier] | No | Spark claims agendas. Heatmap uses calls and news [V earlier] | Spark: "Daily" or "multiple times per week" [V earlier] | Solar, BESS, wind, data centers [V earlier] |
| **MyTownView** All Access ($2,499/yr) | 22,946 municipalities as a directory [V earlier] | Per-state counts [V earlier] | Post-meeting summaries [V earlier] | Weekly free email [V earlier] | Custom alerts [V earlier] |
| ***Our planned pro tier*** | Town, township, county and board grain. Today: 240 MA towns, plus NY and RI pilots [V earlier] | **Yes**, per board [plan] | **Pre-meeting** (median 3.2 days ahead in MA) [V earlier] | Daily now; 6-hourly planned | Siting classifier, plus custom keywords [plan] |

**Table B: delivery, search, AI, citations, seats, exports**

| Product / paid tier | Alert channels | Search and history depth | AI summaries | Source links and citations | Team seats and collaboration | Exports and API |
|---|---|---|---|---|---|---|
| **LocalGovIndex Pro / Enterprise** | **Email only** on every portal plan. Slack, Teams, webhook and RSS are not mentioned [V]. API sync is by **polling** `/v2/changes` ("append-only change events … poll from it"). Webhooks are not mentioned [V] | Record stretches back "decades" [V] | Yes. The model "does not add facts, it condenses the ones already in the record" [V] | "every page links back to the source"; "Source-linked records with permanent URLs"; stable 12-character PublicIds [V] | Seats not stated. "Organization access" on Enterprise [V] | Pro: "Bulk CSV for scoped use cases and limited production exports"; plan card says no API. The page contradicts itself: keys are "issued by hand for Researcher and up" [V]. Enterprise: API at "5,000 requests/min per key"; Snowflake, Iceberg and MCP are "on the roadmap" [V] |
| **Hamlet** | Keyword alerts and "real-time notifications" [S]. No webhooks in the API spec [V] | 101k+ transcripts [S] | Yes (transcripts, highlights) [S] | **The API has no source URL, PDF link or posted-time field** [V] | Not stated | Bearer API: meetings, agenda, transcript [V] |
| **GatherGov** | Not stated. The "Custom API" grid lists "alerts" [V] | "3000+ hours processed daily"; transcripts [V] | Yes: "Agent" chat over its knowledge base [V] | Not stated | Not stated | Transcript API, Search API and Custom API (JSON). The example response shows city, county, address, **applicant, project, category, status, summary** [V] |
| **Citizen Portal** | Email topic and location alerts [S earlier] | Articles and video [S] | Yes (AI-written articles) [S] | Links to the meeting source page [S earlier] | No team plan seen | None seen |
| **Quorum Local** | "email or push notification"; "in platform" [V] | Not stated | Quincy AI analyzes agendas and minutes, preps meetings, drafts outreach [V] | Not stated | "Align teams around shared insights"; Notes; CRM agent [V] | "shareable dashboards", custom reports; integrates with Quorum's federal, state and CRM tools [V]. No public API detail [V] |
| **MultiState** | "an email alert"; hourly snapshots; client-scheduled snapshots [V] | Client tracking database [V] | Not stated | Analysts attach the documents [E] | Not stated | "easily view and export the data" [V]. No API stated |
| **FiscalNote PolicyNote** | Dashboard, daily email reports, API [V earlier] | Full records or snippets [S] | Not described by GatherGov [S] | Snippets [S] | Seat-based [E] | PolicyNote API: Free tier, 4,000 results/mo; Self-Serve **$300/mo**, 20,000 results; Full Service custom. Local data is "an incremental subscription" [S]. Reviewer: "inability to export contacts is frustrating" [S] |
| **Civic IQ** | Platform plus an **MCP server** ("add the Civic IQ MCP server as a connector in Claude") [S] | Agendas, packets, minutes [S] | Yes (chat) [S] | Not seen | Not seen | MCP [S] |
| **Agenda Watch** | Email alerts [S] | Documents harvested daily [S] | Not stated | Documents [S] | MuckRock accounts [S earlier] | Not stated |
| **OrdinanceWatch** | **Email advisories** plus a "Website Issues Feed" [V] | "tens of thousands of records spanning more than 15 years" [V] | Not stated | "a running history of the issue" [V earlier] | Standard: **10 email subscriptions, same domain**. Premium: 20, across domains. **Premium+: unlimited, "for lawyers as a client retention tool"**, with a custom email template and splash page [V] | Issue feed for websites [V] |
| **BillTrack50** | Daily email; mobile app [V] | Legislation back to **2011**; regulations from 2024 [V] | Yes [V] | Bill text [V] | **"Unlimited users", including external people**; sharing widgets; user groups [V] | API included [V]. Exports not mentioned [V] |
| **Shovels** | Alerts, monitoring and webhooks not mentioned [V] | "Full historical records" on paid plans; 1 year on Free [V] | "Charlie" assistant [V] | Not stated | Basic 1 seat; Pro up to 2; Enterprise custom [V] | **API and CLI on every plan**; downloads use credits [V] |
| **Zoneomics** | No alerts mentioned [V] | Not stated | "Bassett AI Assistant" (10, 100 or 1,000+ messages/mo) [V] | Analyst-authenticated reports [V] | 1 user (Essentials, Advanced); "3+ Users" Enterprise [V] | API "for internal business and research use only"; partner integrations; MS Word plug-in [V] |
| **ConstructConnect** | Platform alerts [S] | Projects by stage [S] | Not stated | Project documents [S] | Per market, per seat [S] | Not verified |
| **Dodge** | Platform [S] | "who, what, where, when, and how much" per project [S] | Not stated | Architect, owner, planholders [S] | Not verified | Not verified |
| **Reonomy** | Not applicable | Ownership history [S] | Machine learning that "unwinds shell entities, holding companies, and trust structures" [S] | Not stated | Teams page exists [S] | Annual plan includes 1k exports/mo; extra exports $75 per 1k; bulk CSV feeds [S] |
| ***Our planned pro tier*** | Email, **Slack, Teams, webhook, RSS/JSON, iCal**, with each alert routed by watchlist [plan] | Decision history per application [plan] | Short item flags, not recaps [plan] | **Agenda PDF link plus first-seen timestamp per item** [V earlier, `first_seen`] | Unlimited external collaborators [plan] | CSV, JSON and API with stable IDs [plan] |

**Table C: entities, lifecycle, maps, verification, commercial terms**

| Product / paid tier | Company or entity tracking | Status lifecycle (proposed → adopted) | Mapping | Accuracy and verification method | Support | Contract style | Public price |
|---|---|---|---|---|---|---|---|
| **LocalGovIndex** | **"company and organization tracking"** (Researcher and up); officials' scorecards, voting alignment, "crystal-ball forecasts" [V] | Partial. Votes are described "only when the material explicitly records one"; "An agenda tells you what a body intended to take up, not what it ultimately decided" [V]. No formal lifecycle described [V] | Not stated | **Automated**: OCR plus AI. It warns that "OCR can misread scans… models can misread messy text". No human review stated [V] | Pro: "priority support for production workflows". Enterprise: integration support [V] | **Self-serve via Stripe** up to Professional; Enterprise by written agreement [V] | Pro **$399/mo or $4,000/yr**; Enterprise **$2,500+/mo**. **Pro is "commercial internal-use"; redistribution, AI training and custom geography are Enterprise-only** [V] |
| **Hamlet** | None in the API [V] | No status fields [V] | Coverage map [S] | Automated (transcripts) [E] | Sales [S] | Free tier, 14-day trial, "Talk to sales" [S] | Not published; "$49/mo plan" reported [S] |
| **GatherGov** | Applicant field in the API example; "who's behind them" [V] | **"Track developments through the application, planning, entitlement, and approval phases"** [V]. Its data-center tracker counts stages ("Formally introduced", "Staff study") [V earlier] | Coverage map [V] | Automated AI over transcripts [V] | support@ address; **SOC 2 Type 1** badge [V] | "Start for free" / "Book a demo" [V] | Not published. Customers include Prologis, Beale Infrastructure, Copenhagen Infrastructure Partners and a "Top 5 REIT" [V]. YC-alum founder [S] |
| **Citizen Portal** | No | No | No | Automated (AI articles) [S] | Not seen | Self-serve | $12–49/mo [S earlier] |
| **Quorum Local** | Officials directory: "verified contact data for 75,000+ local officials" [V] | Not stated | **"auto-updating heat maps"** [V] | Automated: "automated system that scans" [V] | Account team [E] | Sales-led (demo) [V] | Vendr median **$21,429/yr** for all Quorum products [S earlier] |
| **MultiState** | No | Tracks an item from agenda onward in the client database [V] | No | **Human.** "analysts review every document"; when a document is not online, "they contact the locality directly" [V]. A Senior Director of Local Operations manages "a team of policy analysts" [S] | Analyst relationship; client portal (vendor testimonial) [S] | Sales-led ("Get Started" form) [V] | Not published |
| **FiscalNote** | No | Not stated | Not stated | Automated plus topic taxonomy [E] | Mixed reviews [S] | Sales-led; PolicyNote API has self-serve tiers [S] | Vendr median **$46,750/yr** [S earlier]; API Self-Serve $300/mo [S] |
| **Civic IQ** | Buying agencies, not companies [S] | "tells you which stage the agency has reached" (procurement) [S] | Not seen | Automated [E] | Not seen | Sales-led. G2: "has not provided pricing information" [S] | Not published |
| **Agenda Watch** | No | No | No | Automated [S] | Newsroom project | Free for journalists [S] | Free |
| **OrdinanceWatch** | No | "running history of the issue" [V earlier] | No | Not stated (likely staff-curated, given 128 hand categories) [E] | Phone and email [V] | **30-day free trial**, then a quote by phone [V] | Not published |
| **BillTrack50** | No | Bill status [V] | Not stated | Automated [E] | "unlimited training and support", live meetings [V] | Self-serve; **annual term only**; card or invoice; optional auto-renew [V] | **$1,000 per state per year; $5,000 for all states and Congress** [V] |
| **Shovels** | **Contractors** ("licenses, work history, and contact details"), residents and homeowners, employees [V] | Decision records; statuses "coming soon" [V earlier] | App map [E] | Automated extraction; "uses multiple vendors" (partner page) [S] | Free and Basic: knowledge base plus email. Pro and Enterprise: dedicated [V] | Self-serve, billed monthly; Enterprise by agreement [V] | **$599 / $999 per month** [V] |
| **Zoneomics** | No | No | Parcel maps [E] | **Human-checked reports**: "authenticated by our Zoning Analysts" [V] | "Dedicated Zoning Technician" on every plan [V] | Self-serve, 20% off annual; Enterprise "Talk To Our Team" [V] | **$92 / $279 per month** [V] |
| **ConstructConnect** | Owners, architects and bidders on projects [S] | **Five stages: conceptual, design, final planning, bidding, post-bid** [S] | Yes [E] | Reviews: "information not updated and sometimes misleading"; "contact information can occasionally be outdated" [S] | Reviews call support "slow and unresponsive" [S] | Annual; reviews cite "contract rigidity and cancellation friction" [S] | $129–199/mo per market and seat; Premium from $10k/yr (competitor's guide; unverified) [S] |
| **Dodge** | Owner, architect, bidders [S] | Pre-design through bid [S] | Yes [E] | Research staff claimed by a third party [S, unverified] | Rep-led [S] | Demo and quote [S] | Not published [S] |
| **Reonomy** | **True owner behind LLCs** via machine learning [S]. A reviewer says "there are no researchers to confirm accuracy" [S]; the company claims about 80% accuracy [S] | n/a | Yes [E] | Automated [S] | Not verified | Self-serve monthly or annual [S] | **$500/mo monthly, or $400/mo billed annually** [S] |
| **Spark / Heatmap Pro** | Heatmap: project database [V earlier] | Not described | County maps and risk scores [V earlier] | Heatmap: "regular phone calls to all 3,100+ U.S. counties" (human) [V earlier] | Account team [E] | Quote, annual [V earlier] | Not published |
| ***Our planned pro tier*** | **LLC to parent** via MassDEP payor and Secretary of State records [plan] | **Proposed → hearing → vote → adopted → appeal/AG** [plan] | Town map [plan] | Automated, plus a published correction log and a per-item first-seen proof [plan] | Founder-led | Self-serve | $349/mo, proposed in `where_we_win.md` [E] |

**Row sources**
- **LocalGovIndex:**
  - [pricing](https://localgovindex.com/pricing), [API](https://localgovindex.com/api), [methodology](https://localgovindex.com/methodology), [coverage](https://localgovindex.com/coverage) — all [V]
  - Earlier 2,823 figure — `data_center_and_other_fights.md` [V earlier]
  - Data-reuse licence and robots.txt — `../Expansion/cheap_township_coverage.md` [V earlier]
- **Hamlet:**
  - [OpenAPI spec](https://api.myhamlet.com/openapi.json) [V]
  - [coverage page](https://www.myhamlet.com/coverage) [S]
  - [PublicCEO, Feb 2026](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/) [S]
- **GatherGov:**
  - [home](https://gathergov.com/) [V], [API page](https://gathergov.com/api) [V]
  - [GatherGov vs Curate, Aug 21, 2026](https://gathergov.com/articles/gathergov-curate-alternative-in-2026) [V for GatherGov's own claims; S for its claims about Curate]
  - [about](https://www.gathergov.com/about-us) [S]
- **Citizen Portal:** `competitor_behind_login.md` [S/V earlier]
- **Quorum:**
  - [Quorum Local](https://www.quorum.us/products/local/) [V]
  - [Vendr](https://www.vendr.com/marketplace/quorum) [S]
- **MultiState:**
  - [MA local page](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma) [V]
  - [Jay Wimberly bio](https://www.multistate.us/meet-the-team/jay-wimberly) [S]
- **FiscalNote:**
  - [PolicyNote API pricing](https://fiscalnote.com/policynote-api-pricing) [S: 403 to the fetcher, read through a search quote]
  - [press release, May 19, 2026](https://www.financialcontent.com/article/bizwire-2026-5-19-fiscalnote-expands-policynote-api-adding-local-government-intelligence-to-enterprise-and-ai-agent-workflows) [S]
  - [Vendr](https://vendr.com/marketplace/fiscalnote), [G2 seller page (4.2 from 7 reviews)](https://www.g2.com/sellers/fiscalnote), [SoftwareFinder](https://softwarefinder.com/analytics-software/fiscalnote), [Capterra AU](https://www.capterra.com.au/software/185611/fiscalnote), [Software Advice](https://www.softwareadvice.com/collaboration/fiscalnote-profile) — all [S]
- **Civic IQ:** [MCP page](https://civiciq.com/mcp/public-meetings-mcp), [founders page](https://civiciq.com/use-cases/founders), [G2 pricing](https://www.g2.com/products/civic-iq/pricing) — all [S]
- **Agenda Watch:** [RJI launch post](https://rjionline.org/news/welcome-to-agenda-watch/) [S]
- **OrdinanceWatch:** [home](https://ordinancewatch.com/), [packages](https://www.ordinancewatch.com/index.php/subscription-packages), [Georgia](https://ordinancewatch.com/index.php/what-we-monitor/georgia) — all [V]
- **BillTrack50:** [pricing](https://www.billtrack50.com/info/pricing) [V]; [testimonials](https://www.billtrack50.com/info/testimonials) [S]
- **Govlaunch:** [help article](https://help.govlaunch.com/en/articles/3383740-how-do-you-make-money-if-this-is-free), [Vendor Registry](https://govlaunch.com/products/vendor-registry) — [S]. GovSpend and Starbridge: `where_we_win.md` [V earlier]
- **Shovels:**
  - [pricing](https://www.shovels.ai/pricing) [V]
  - [Decisions launch](https://www.shovels.ai/blog/decisions-api-launch/) [V earlier]
  - [Cherre partnership](https://blog.cherre.com/?p=1714) [S]
- **Zoneomics:** [pricing](https://www.zoneomics.com/pricing) [V]
- **ConstructConnect:**
  - [vs PlanHub](https://www.constructconnect.com/planhub-alternative), [early-stage blog](https://www.constructconnect.com/blog/how-contractors-find-early-stage-projects-with-constructconnect) [S]
  - [ConstructionBids.ai guide (a competitor)](https://constructionbids.ai/blog/constructconnect-pricing-guide-2026), [PricingSaaS](https://pricingsaas.com/companies/constructconnect) [S]
  - [G2 reviews](https://www.g2.com/products/constructconnect-project-intelligence/reviews), [SelectHub](https://www.selecthub.com/construction-bidding-software/constructconnect/), [BBB](https://www.bbb.org/us/oh/cincinnati/profile/computer-software-developers/constructconnect-0292-11047629) [S]
- **Dodge:** [help glossary](https://www.construction.com/help/dcc/search_filter_glossary.aspx), [Alex Berman blog](https://alexberman.com/dodge-reports-construction-leads), [Levelset](https://www.levelset.com/blog/construction-bidding-websites/) — all [S]
- **Reonomy:** [pricing](https://reonomy.com/pricing), [CRE Daily review](https://www.credaily.com/reviews/reonomy-review/), [Commercial Observer](https://commercialobserver.com/2019/07/how-reonomys-data-network-lifts-the-veil-on-llcs), [SPEEDA Edge](https://sp-edge.com/companies/205393) — all [S]
- **Spark, Heatmap Pro, MyTownView:** `competitor_coverage_map.md` and `where_we_win.md` [V earlier]

**Placer.ai** (foot traffic) was judged not relevant. It does not monitor government actions [E]. Reonomy is included only as the price and feature anchor for LLC-to-owner resolution.

### Inferences
- [E] **LocalGovIndex Professional is the direct price comparator.** At $4,000/yr it is within $200 of the proposed $4,188/yr "Siting Desk". But it has the following limits:
  - It delivers by email only.
  - It reserves the API for Enterprise at $30,000+/yr ($2,500 × 12).
  - It forbids redistribution. That matters to consultants and lawyers who forward alerts to clients.
  - It describes no status lifecycle.
- [E] **Machine delivery is the most consistently gated feature in the category:**

  | Product | How machine delivery is sold |
  |---|---|
  | LocalGovIndex | API on Enterprise only; polling, no webhooks |
  | GatherGov | Custom API, sold by demo |
  | Hamlet | Bearer API, no webhooks |
  | FiscalNote | Local data as an add-on to the API |
  | Quorum | No public API |

  Shovels is the exception: an API on every plan, but no alerts.
- [E] **Human verification is the premium signal.** MultiState sells it explicitly (analysts, calls to localities), as do Zoneomics ("authenticated by our Zoning Analysts") and Heatmap (phone calls to counties). Products without it draw the main review complaint in adjacent categories: ConstructConnect's outdated leads, and Reonomy's "no researchers to confirm accuracy".
- [E] **The status lifecycle exists in construction-lead products, not in agenda monitors.** ConstructConnect has five stages, Dodge has "pre-design" and GatherGov has its phases. The pure agenda monitors (LocalGovIndex, Hamlet, Quorum, MultiState) do not model "proposed → hearing → vote → adopted". A siting lifecycle is a gap that buyers already understand from lead products.
- [E] **Seat models split two ways.** BillTrack50 ("unlimited users, including external people") and OrdinanceWatch Premium+ (unlimited email subscriptions, aimed at lawyers' clients) sell collaboration as a flat fee. Shovels (1–2 seats), Zoneomics (1 user) and ConstructConnect (per market and seat) charge per seat. Unlimited external collaborators fits the consultant and lawyer workflow, and two precedents already exist.

### Gaps
- **Prices not published:** Hamlet, GatherGov, Civic IQ, MultiState, OrdinanceWatch, Dodge and Heatmap/Spark. FiscalNote's local add-on price was not found. Quorum's Vendr figure covers all its products.
- **Seat counts not published:** LocalGovIndex at any tier, Quorum and MultiState.
- **Alert-delivery channels and refresh not confirmed** for GatherGov, Hamlet or Civic IQ. The GatherGov API docs did not render, and civiciq.com and myhamlet.com are challenged.
- **ConstructConnect and Dodge:** their methods (whether research staff read planning-board agendas or call towns) were not verified on their own pages. The "3,000 municipalities, 19,000 web sources" figure is from a third-party blog.
- **No job postings were found** that show human agenda review at GatherGov, Hamlet, LocalGovIndex, Dodge or ConstructConnect. MultiState's human method comes from its own page and a staff bio, not a posting.
- **LocalGovIndex counts conflict:** 12,214 places (coverage page today) vs 2,823 governments (earlier read). The coverage page gives no type breakdown or per-state township list.

---

## 2. Per competitor: 2–3 concrete ways our professional tier can beat it (for developers, land-use lawyers, site selectors), and where it already beats us

### Takeaway
The repeatable wedge against almost every rival has four parts:
1. **Town- and township-grain siting coverage with a published per-board list.**
2. **Days-ahead agenda capture with a first-seen timestamp and a source PDF link on every item.**
3. **Alerts routed to Slack, Teams or a webhook per watchlist, at a self-serve price.**
4. **A proposed-to-adopted status record keyed to LLC-to-parent company watch.**

The rivals already beat us on:
- national breadth (LocalGovIndex, GatherGov, Quorum, FiscalNote)
- human verification (MultiState)
- transcripts and video (Hamlet, GatherGov)
- officials and CRM features (Quorum)
- permits and contractor graphs (Shovels)
- years of archive (OrdinanceWatch, LocalGovIndex, BillTrack50)

### Cited Findings and per-competitor reading
Each "beat" is an [E] judgment built on the cited facts in §1 and the earlier notes.

**LocalGovIndex (Professional $399/mo; Enterprise $2,500+/mo)**

How we beat it:
1. **Routing at the pro price.** LGI is email-only on every portal plan, and its API is Enterprise-only with polling and no webhooks [V]. Offer Slack, Teams and webhooks per watchlist at about $349/mo, so a developer's permitting channel and counsel's channel get different town sets.
2. **A siting status record.** LGI states that an agenda shows only what a body "intended to take up" and records votes only when explicit [V]. Give one record per matter (proposed → hearing → continued → vote → adopted → appeal/AG) with dates. That is what a lawyer cites and what a site selector screens on.
3. **Client-shareable licence.** Pro is "commercial internal-use" only; redistribution is Enterprise [V]. Let consultants and counsel forward alerts and exports to named clients under the pro tier.
4. Possibly: a **per-board completeness list in township states**. LGI publishes counts, not a township list [V].

Where it beats us:
- 12,214 places and 30.6M documents going back "decades" [V]
- officials' voting alignment and forecasts [V]
- company and organization tracking already at $49/mo [V]
- stable IDs and a change feed [V]
- self-serve today

**Hamlet (paid / enterprise)**

How we beat it:
1. **Town and township boards.** Its API has no TOWN or TOWNSHIP type, and it covers under 5% of governments in the township states [V, earlier].
2. **Citable evidence.** Its API has no source URL or posted-time field [V]. Every item of ours carries the agenda PDF and a first-seen time, which lawyers need.
3. **A published self-serve price** against "Talk to sales" [S].

Where it beats us:
- transcripts and video search
- 2,011 cities and 453 counties
- an agenda-topic API already in production
- free journalist distribution [S]

**GatherGov (sales-led)**

How we beat it:
1. **Lead time.** GatherGov is searchable "within 24 hours" *after* the meeting [V]. We alert days *before* it (median 3.2 days in MA) [V earlier]. Site selectors care because a moratorium hearing can still be attended or commented on.
2. **Boards without video.** Its pipeline is "3000+ hours processed daily" of meetings [V]. Small planning boards, ZBAs and conservation commissions that post agendas but do not stream are our core [V earlier].
3. **A published coverage list and price** against "Book a demo" [V].

Where it beats us:
- national reach: 9,300+ jurisdictions [V]
- entitlement-phase tracking with applicant, project and status fields in its API [V]
- named developer and REIT customers (Prologis, Beale, CIP) [V]
- SOC 2 Type 1 [V], which enterprise procurement asks for

**Citizen Portal (paid, $12–49/mo)**

How we beat it:
1. **A team product at all.** It offers 2–50 topic alerts, email only, and no seats, exports or API [S, earlier].
2. **Pre-meeting rather than recaps** [V, earlier].
3. **Clean place filing.** Fitchburg council is filed under a school district, for example [V, earlier]. A multi-town feed needs correct places.

Where it beats us:
- rural township and county breadth after the meeting [S, earlier]
- price
- AI recaps from video

Its terms bar competitive use, so do not benchmark inside it [V, earlier].

**Quorum Local (about $21k/yr median, all products)**

How we beat it:
1. **Below its population floor.** Quorum covers "counties and cities of 3,000 or greater" [V]. Many siting townships and towns fall under that.
2. **Slack, Teams and webhooks** against "email or push" [V].
3. **Self-serve price and siting lifecycle** against a sales-led suite [V/S].

Where it beats us:
- officials directory ("75,000+ local officials") [V]
- outreach, CRM and meeting-prep agents [V]
- social listening [V]
- heat maps and dashboards [V]
- state and federal in one tool, which matters to public-affairs teams

**MultiState (local)**

How we beat it:
1. **Machine delivery and a public list.** MultiState sends email and hourly snapshots, publishes no list [V], and describes no API.
2. **Price transparency and self-serve onboarding** against a contact form [V].
3. **Siting depth:** classifier, lifecycle and LLC watch, against generic issue tracking [E].

Where it beats us:
- **human analysts who "review every document" and "contact the locality directly" when documents are not online** [V]. This is the strongest accuracy claim in the category.
- 4,850+ jurisdictions, townships included [V]
- about 20 years' track record [V]
- tailored scopes, ballot measures and social media [V]

**FiscalNote PolicyNote / Curate (about $46.8k/yr median)**

How we beat it:
1. **Freshness.** A rival says Curate refreshes weekly [S]. We crawl daily, with 6-hourly planned.
2. **Precision without setup.** Reviewers say alert search-term setup "can be complex" and ask to flag high-priority items [S]. Ship pre-built siting topics and a priority flag.
3. **Price.** Local data is an "incremental subscription" on top of the API [S]. The median contract is about 12× our proposed tier [E].

Where it beats us:
- 12,000+ cities and counties
- a mature API with a self-serve $300/mo tier (20,000 results) [S]
- 600+ topics
- state and federal bundles

**Civic IQ**

How we beat it:
1. **A different job.** Civic IQ sells procurement signals to vendors ("6 to 18 months before formal RFPs") [S]. Siting buyers need land-use matters.
2. **Township grain and lifecycle for siting** [E].

Where it beats us:
- 80,000–100,000+ agencies
- an MCP connector for Claude already live [S]

Copy the MCP idea; dcmap does the same [V, earlier].

**Agenda Watch (newsroom tool)**

How we beat it:
1. **Business features:** teams, routing, exports, lifecycle [E].
2. **Coverage beyond four launch regions** [S].

Where it beats us: free, with journalist trust and the Stanford/RJI brand [S].

It is a distribution partner rather than a competitor [E].

**OrdinanceWatch (FL/GA)**

How we beat it:
1. **Geography and siting topics.** It covers FL and GA metros only, under 128 general categories [V].
2. **Channels beyond email** [V].

Where it beats us:
- **15+ years of archive** [V]
- **Premium+ "for lawyers as a client retention tool"** with branded email templates [V]. This is a feature to copy for the lawyer segment: white-label client alerts.
- lobbyist-registration rules [V]

**BillTrack50 (state bills)**

Not a local competitor; its only local coverage is the DC council [V].

How we beat it: local siting coverage, which it does not have.

Where it beats us, as a model for our pricing:
- per-state pricing capped at $5,000 [V]
- "Unlimited users, including external people" [V]
- API included [V]
- history to 2011 [V]

Lawyers and policy teams already budget for this shape [E].

**Govlaunch-like B2G tools (Govlaunch, GovSpend, Starbridge, Vendor Registry)**

How we beat them: they serve vendors selling *to* governments [S/V earlier]. No siting overlap, so there is nothing to beat beyond the topic focus [E].

Where they beat us: procurement data and bid alerts. Not our buyer.

**Shovels (Basic $599, Pro $999/mo)**

How we beat it:
1. **Before the decision.** Shovels creates no Decision record "until the minutes are posted" [V, earlier]. We flag the agenda days ahead.
2. **Small towns.** Its Decisions cover 600+ cities [V, earlier].
3. **Alerts.** Shovels mentions none [V].

Where it beats us:
- nationwide building permits
- contractor, owner and resident entity graph [V]
- API and CLI on every plan, including free [V]
- full history

Its applicant-and-owner linking is the bar for our company watch.

**Zoneomics ($92–279/mo)**

How we beat it:
1. **Pending changes.** Zoneomics digitizes adopted code text and has no alerts [V]. We show the amendment or moratorium while it is still on the agenda, before the code changes.
2. **Multi-seat** against "1 User" on its self-serve plans [V].

Where it beats us:
- parcel-level zoning for 10,000+ cities
- analyst-authenticated reports [V]
- a Word plug-in for lawyers' memos [V]

**ConstructConnect and Dodge (project leads)**

How we beat them:
1. **Policy events, not just projects.** Moratoria, bylaw rewrites and use-table changes never become "projects" in a lead database [E].
2. **Verifiable freshness.** The top review complaint is outdated leads: "information not updated and sometimes misleading" [S]. Every item of ours shows the source PDF and first-seen time.
3. **Flexible terms** against "contract rigidity and cancellation friction" [S].

Where they beat us:
- 825,000 projects
- owner, architect and bidder contacts [S]
- bid documents
- a five-stage project lifecycle buyers already know [S]

**Reonomy (and Placer-type data)**

How we beat it: we do not compete on property ownership. Our company watch links the *agenda applicant* LLC to its parent, which Reonomy's property-owner graph does not cover for pending applications [E].

Where it beats us:
- a mature true-owner model at $400–500/mo [S]

It is a price anchor showing that LLC resolution sells at about $5k/yr [E]. Placer.ai is not relevant [E].

**Spark / Heatmap Pro (from earlier notes)**

How we beat them:
1. **Town and township grain** against county grain [V, earlier].
2. **A published price and Slack delivery** [V, earlier].

Where they beat us:
- risk scores and polling
- phone calls to every county (Heatmap) [V, earlier]
- enterprise customers (NextEra, AES)

Best treated as licensees rather than targets (`where_we_win.md`).

### Inferences
- [E] **Easiest to displace for our three buyers:** GatherGov (post-meeting), Hamlet (no towns, no citations), Citizen Portal (consumer) and LocalGovIndex Pro (email-only, internal-use licence). Each loses on a feature a developer or lawyer can test in a trial week: lead time, source PDF, Slack routing, client sharing.
- [E] **Hardest to displace:**
  - MultiState and Quorum, through relationships, humans and bundled state/federal coverage.
  - Shovels, through its permit graph.

  Against these, position as the *siting layer* they lack, and integrate with them (export, webhook, API) rather than replace them.
- [E] **Features to copy rather than beat:**
  - OrdinanceWatch's white-label client alerts for lawyers
  - BillTrack50's unlimited-users flat price
  - LocalGovIndex's stable IDs and change feed
  - Civic IQ's and dcmap's MCP connector

### Gaps
- None of these comparisons was tested with an account. Lead-time and accuracy claims for rivals are their own statements.
- GatherGov's alert channels and seat model are unknown. If it offers Slack and webhooks under its demo-sold plan, the "routing" wedge against it narrows.

---

## 3. Which features matter most to developers, land-use lawyers and site selectors (review evidence)

### Takeaway
Review evidence for local-agenda monitors themselves is thin:
- G2 blocked the fetcher.
- MultiState and Shovels have no visible G2 reviews.
- FiscalNote has 7 reviews.

The adjacent categories (project leads, ownership data, bill tracking) give a consistent order of what buyers praise or complain about:
1. **Accuracy and freshness of each record**, ideally with human verification.
2. **Completeness in the places that actually decide.**
3. **Precise alerts that are easy to set up and prioritise.**
4. **Price and value, flexible terms, and unlimited users.**
5. **Exports and integrations.**
6. **Responsive support.**

AI summaries and maps are not what reviewers praise or miss. Every rival has them.

### Cited Findings
**1. Accuracy and freshness**
- ConstructConnect reviews:
  - "information not updated and sometimes misleading"
  - "contact information can occasionally be outdated"
  - SelectHub reports "inaccurate or outdated project information, leading to wasted time"
  - A BBB complaint calls the leads "outdated"
  - Sources: [G2](https://www.g2.com/products/constructconnect-project-intelligence/reviews), [SelectHub](https://www.selecthub.com/construction-bidding-software/constructconnect/), [BBB](https://www.bbb.org/us/oh/cincinnati/profile/computer-software-developers/constructconnect-0292-11047629) [S]
- Positive mirror: one G2 reviewer trusts data that is "updated often enough that you can actually trust what you are seeing" [S, same G2 source].
- Reonomy: CRE Daily says "when it comes to the accuracy of data, Reonomy falls short… there are no researchers to confirm accuracy" — [CRE Daily](https://www.credaily.com/reviews/reonomy-review/) [S]. The company claims about 80% accuracy — [SPEEDA Edge](https://sp-edge.com/companies/205393) [S].
- BillTrack50 testimonial: "receiving alerts on my bills quickly and with more accuracy than any other site" — [testimonials](https://www.billtrack50.com/info/testimonials) [S, vendor-selected].
- Vendors sell human checking as the premium:
  - MultiState: "analysts review every document… contact the locality directly" — [V](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma)
  - Zoneomics: "authenticated by our Zoning Analysts" — [V](https://www.zoneomics.com/pricing)
  - LocalGovIndex warns the opposite: "treat every AI summary as a fast way to understand a document, not as a substitute for it" — [V](https://localgovindex.com/methodology)

**2. Completeness where decisions happen**
- Build.inc's site-selection guide:
  - "Zoning is the most fragmented data layer"
  - "Many jurisdictions have interim zoning freezes, overlay amendments, or pending rezoning petitions"
  - "There is no substitute for a direct call to the planning department before advancing a site"
  - Source: [V](https://build.inc/insights/site-selection-data-sources-guide)
- Carina Energy (earlier note): moratoriums "can pass within a single board meeting cycle and may not appear in databases for weeks or months" — `where_we_win.md` [V earlier].
- Quorum's coverage floor is population 3,000 — [V](https://www.quorum.us/products/local/).

**3. Entitlement risk now ranks with power for data-center buyers**
- A NAIOP I.CON Data Centers panel (Newmark, Link Logistics, Logistix, Active Infrastructure) said:
  - "entitlement issues are far less predictable"
  - "In some cases, unresolved entitlement questions are creating more concern than difficult infrastructure challenges"
  - "election cycles, leadership changes and shifting public sentiment" can change approvals
  - Source: [V](https://blog.credaglobal.org/2026/05/rethinking-power-entitlement-risk-and-execution-in-an-increasingly-complex-data-center-market/)
- Acres' 2026 playbook: zoning and entitlement risk is "increasingly a first-pass filter, not a final-step check" — [S, search quote](https://www.acres.com/hubfs/Guides%20and%20Playbooks/2026%20Data%20Center%20Site%20Selection%20Playbook%20by%20Acres.com.pdf).

**4. Alert precision and ease of setup**
- FiscalNote: "setting up search terms for alerts can be complex" — [SoftwareFinder](https://softwarefinder.com/analytics-software/fiscalnote) [S].
- FiscalNote: a request for a way to "star" or "flag" a bill as high importance so that updated alerts can be prioritised — [Software Advice](https://www.softwareadvice.com/collaboration/fiscalnote-profile) [S].
- BillTrack50 claims its alerts are "narrower and faster than Quorum's" — [BillTrack50 vs Quorum](https://www.billtrack50.com/info/blog/comparative-analysis-quorum-and-billtrack50) [S, vendor's own comparison].

**5. Price, value, terms and users**
- BillTrack50 is praised as "about one-third the price of its competitors" — [Worldmetrics](https://worldmetrics.org/best/legislative-tracking-software/) [S]. It sells "Unlimited users" — [V](https://www.billtrack50.com/info/pricing).
- ConstructConnect: reviewers "question the value of the leads relative to the price"; complaints about "contract rigidity and cancellation friction" — [SelectHub](https://www.selecthub.com/construction-bidding-software/constructconnect/), [rfp.wiki](https://www.rfp.wiki/vendors/constructconnect) [S].

**6. Exports and integration**
- FiscalNote: "inability to export contacts is frustrating"; acquired products are not integrated "into the broader FiscalNote platform" — [Capterra AU](https://www.capterra.com.au/software/185611/fiscalnote) [S].

**7. Support**
- ConstructConnect support is called "slow and unresponsive" — [SelectHub](https://www.selecthub.com/construction-bidding-software/constructconnect/) [S].

### Inferences
Ranked feature priorities for the professional tier, by buyer. All [E], built on the evidence above.

| Rank | Feature | Developers | Land-use lawyers | Site selectors | Why (evidence) |
|---|---|---|---|---|---|
| 1 | **Per-item proof: source PDF, posted or first-seen time, and a correction log; optional human check on high-stakes items** | ●●● | ●●● | ●●● | Accuracy is the top complaint in lead and ownership tools. MultiState, Zoneomics and Heatmap sell humans |
| 2 | **Published per-board coverage list, including towns and townships** | ●●● | ●● | ●●● | "Zoning is the most fragmented data layer"; "may not appear in databases for weeks or months"; Quorum's 3,000 floor |
| 3 | **Pre-meeting lead time, plus a status lifecycle from proposed to adopted to appeal** | ●●● | ●●● | ●●● | Entitlements are "far less predictable"; no agenda monitor models the lifecycle; lead tools (ConstructConnect, Dodge) taught buyers stages |
| 4 | **Pre-built siting topics, priority flags and a low-noise filter** | ●●● | ●● | ●● | FiscalNote reviewers on complex setup and the wish to "star" items |
| 5 | **Routing to Slack, Teams or webhook per watchlist, plus iCal** | ●●● | ● | ●● | Machine delivery is gated at every rival (§1). It is also the growth loop (`where_we_win.md`) |
| 6 | **Flat price with unlimited or external seats, monthly terms** | ●● | ●●● | ●● | BillTrack50 praise; ConstructConnect contract complaints; OrdinanceWatch Premium+ for lawyers |
| 7 | **Company watch, LLC to parent** | ●●● | ●● | ●● | Shovels and Reonomy show people pay for entity resolution ($400–999/mo); LocalGovIndex has mention-level company tracking only |
| 8 | **Exports and API with stable IDs and a change feed; client-shareable licence** | ●● | ●● | ●●● | FiscalNote export complaint; LocalGovIndex IDs and change feed; its internal-use-only Pro licence |
| 9 | **Decision history and archive** | ●● | ●●● | ●● | OrdinanceWatch's 15 years and BillTrack50's 2011 history are selling points for lawyers |
| 10 | AI summaries, maps | ● | ● | ● | Commodity: offered by LocalGovIndex, GatherGov, Hamlet, Quorum, Citizen Portal and Zoneomics. No review praises or misses them |

- [E] **The single most defensible bundle** joins the top three rows: proof, a list and a lifecycle. Each answers a documented complaint, and no rival in §1 shows all three.
- [E] **For lawyers specifically,** the bundle is citation-grade items plus decision history plus white-label client forwarding. OrdinanceWatch Premium+ proves that shape sells, but only in FL and GA.

### Gaps
- **No first-party reviews** of local-agenda monitors were readable:
  - G2 returned 403 for Quorum.
  - No G2 reviews surfaced for MultiState, Shovels, GatherGov, Hamlet or LocalGovIndex.
  - FiscalNote's G2 page shows only 7 reviews, with no local-specific text.
- The feature ranking therefore leans on adjacent categories and on vendor positioning. It should be validated with 5–10 buyer interviews or trial-usage data.
- **No survey ranks** "local hearing and moratorium monitoring" among site-selection criteria. The NAIOP panel and the Acres and Build guides are qualitative.
