# What a free tier for 351 Watch should include

Prepared 2026-10-12 for the 351 Watch owner. Status: complete (about 60 searches and fetches this session).

Scope: US only. No accounts were created; only public pricing pages, docs, help centres and press were read. Prices are noted only where they define what the first paid step adds. The owner decides prices last.

**Labels**
- **[V] verified**: read on the product's own page (pricing, docs, help centre, statute) this session.
- **[V-idx]**: the product's own page text as quoted by the search index; the page itself was not loaded (blocked or bot-checked).
- **[V-prior]**: verified in an earlier note in this repo (Oct 10-11, 2026); URL repeated.
- **[S] secondary**: third-party article, review site or aggregator.
- **[E] estimate**: my judgment or arithmetic.

Context read first: `../Meeting monitor national expansion/competitor_coverage_map.md`, `../Meeting monitor national expansion/who_needs_it_most.md`, `where_we_win.md` (Offer 1 already sketched "Free: 1 watchlist, up to 5 towns, daily, web + RSS"), and `projects/351watch/ARCHITECTURE.md` (watchlist = random 24+ char ID as credential; RSS, JSON, iCal, webhooks dispatched once a day).

## Summary

1. **What exists free.** Every civic-meeting rival with a published free tier gives one place or one body free (LocalGovIndex: one board by email; Citizen Portal: follow 1 location; MyTownView: browse free, own-town alerts $29.99/yr). Their first paid step buys "any place" plus alerts. Towns give free per-board agenda emails behind an account, with no topic filter. Iowa and Maine require free legal-notice email alerts (Iowa allows a cost-recovery fee). Data-center maps are free but monthly and after adoption. [V, §1]
2. **The gap.** No free product gives siting-only alerts across every board, across the town line, before the meeting, on a calendar, without an account. Neighbouring towns are notified by law in MA, NY and VA, but only their officials, not their residents. [V/E, §2]
3. **What gets gated elsewhere.** Places (onX, BillTrack50, the civic rivals), count and speed (Visualping, F5Bot), history, exports and API (Shovels, Crunchbase), team channels (F5Bot, Visualping). Public pages stay free wherever growth came from search (Zillow, Ballotpedia, OpenSecrets, dcmap). Ungated freemium converts about 8% of sign-ups in the 2026 benchmark, but that is B2B SaaS. [V/S, §3]
4. **Recommendation: Design A, "My town and its neighbours".** Free = home town + every touching jurisdiction (+ the zoning county board), all topics and boards, web/RSS/iCal/one webhook, daily, never delayed. Paid starts at a second area and adds one feed for many areas, routing, 6-hour refresh, company watch, exports, API and bulk history. Search and public pages stay fully free. Split the watchlist link into read and manage links, validate the area server-side, throttle area changes, fence free webhooks per Slack workspace, and accept some leakage. Cap the area in county states (VA, UT). [E, §4]
5. **Features to love and share:** item permalinks that preview well in Facebook groups and Nextdoor, neighbour alerts, an iCal feed of hearings, a printable "what's coming up" sheet with a QR code, and a "how to take part" box on each hearing. [E/S, §5]

---

## 1. Free-access inventory (per product)

### Takeaway
- **Every civic-meeting product that publishes a free tier draws the free line at one place or one body:** LocalGovIndex (one board or council), Citizen Portal (follow 1 location), MyTownView (own town on the cheapest paid step; browsing free). The first paid step is cheap ($9/mo to $29.99/yr) and buys **"any place" plus alerts**, not more data.
- **Alert utilities draw the line at count and speed**, not geography: Visualping (5 pages, hourly), F5Bot (email only, few keywords), Shovels (500 records, 1 year of history, no downloads).
- **Feeds (RSS, JSON, Slack, webhooks) are usually paid.** F5Bot puts RSS/JSON and Slack/Discord on its top plan; Visualping keeps Slack and Teams off its free and first paid plans; LocalGovIndex's API is Enterprise-only. Only Talkwalker Alerts (email, RSS, Slack free) and dcmap.us (keyless JSON and MCP) give machine delivery away.
- **Town-run tools are free but per board, account-gated and keyword-blind** (CivicPlus Notify Me, govDelivery). Newspaper notice sites are free by statute in Iowa and Maine, with email alerts; Iowa lets the site charge cost-recovery for alerts.
- **No free product found gives pre-meeting, topic-filtered siting alerts at town or township grain, with a calendar feed, without an account.**

### A. Civic-meeting and agenda products

| Product | Free (no account / with free account) | Limits on free | First paid step adds | Label · Source |
|---|---|---|---|---|
| **LocalGovIndex** | Free plan: "One board or council": agenda summary before the meeting and recap after, **by email**. Saving places needs sign-in | One body; no exports; no API (anonymous API tier = "no data access"); email is the only channel named; no RSS/Slack/webhook mentioned | **Civic $9/mo or $90/yr**: "any place, official, item, or topic, with email change alerts", recaps after each followed meeting, weekly briefs, "light" non-commercial exports. Researcher $49/mo (CSV, extracts); Professional $399/mo (bulk CSV); Enterprise $2,500+/mo (API 5,000 req/min) | V · [pricing](https://localgovindex.com/pricing), [API](https://localgovindex.com/api), [home](https://localgovindex.com/) (data-center dossier: "2,600+ local governments") |
| **Citizen Portal** (citizenportal.ai) | Pricing page (as indexed): browse meetings, "a few articles a day", search topics and locations, **follow 1 location**. Help centre: free sign-in lets you "save locations, filter by topic, and set up alerts" (the two pages conflict on whether topic alerts are free) | Articles per day; 1 location; post-meeting recaps | **Citizen Pro $15/mo**: unlimited articles and transcripts, AI breakdowns, topic and speaker search, topic alerts. One-time **$299 Founding Member**: "all 5 levels of government" and "nearly unlimited topics and locations". Earlier note saw $12–49/mo | V-idx · [pricing via search](https://citizenportal.ai/checkoutlifetime), [help](https://citizenportal.ai/help) (both 403 to direct fetch); V-prior · `competitor_behind_login.md` |
| **MyTownView** | Free: "All the civic data your town publishes, structured and searchable"; browse all covered municipalities; **browsing "doesn't require an account at all"**; 3 AI questions a day. Earlier note: a free Sunday email of "what happened and what's coming up" | AI questions; no custom alerts | **Resident $29.99/yr**: "Deep intelligence for the town you care about most": 5 custom alerts, 300 AI questions/month, budget history, PDF report builder. **Pro $17/mo or $199/yr**: unlimited alerts, saved views, CSV exports. API "coming soon" with a "rate-limited free tier" | V · [pricing](https://mytownview.com/pricing); V-prior · [home](https://mytownview.com/) |
| **Hamlet** | "A free tier for initial searches" | Searches only; full transcripts and real-time notifications need the 14-day trial | Trial unlocks "full transcripts and real-time notifications"; saved searches and keyword alerts exist (tier not stated). Data refreshed weekly, moving to daily. No public price ("$49/mo plan" reported). Free access for journalists reported | S · [PublicCEO, Feb 2026](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/); V-prior · `durability_and_acquirers.md` (site behind Vercel checkpoint, HTTP 429 again today) |
| **GatherGov** | "Start for free" / "Try us for free. Compare us to CoStar, Dodge & Construction Wire." "#GatherGov Readout" subscription | Not published | Not published ("Book a demo"); /pricing returns 404 | V · [home](https://gathergov.com/) |
| **CivicSearch** | Free search across ~550–650 cities' council transcripts; newsletter sign-up | No alerts seen | No paid tier | S · [civictech.guide](https://civictech.guide/projects/civicsearch); V-prior · `coverage_check.md` (site is a JS app; nothing readable today) |
| **Red Tape Recordings** | Free lookup of meeting video, transcript, agenda; topic filters (data centers, housing development, warehouses, water, Flock cameras); **site-wide RSS** (`/feed.xml`) | "Sign in / Register" for "My Saved Items"; no alerts described | No pricing page | V · [home](https://redtaperecordings.com/), [coverage](https://redtaperecordings.com/coverage) |
| **Councilmatic** | "Free and open access, open source code and open data"; Chicago and LA Metro only; email subscriptions to bills, committees, events and people (launched 2017, via a profile page); committee event RSS | Two places only; account for email | Paid = deploying Councilmatic to a new city ("Contact us for pricing") | V · [councilmatic.org](https://www.councilmatic.org/); S · [DataMade 2017](https://datamade.us/blog/councilmatic-notifications/) |
| **Civic IQ** | None seen | — | Agendas, packets and minutes of "100,000+ agencies" via MCP; procurement focus; price not public | S · [MCP page via search](https://civiciq.com/mcp/public-meetings-mcp) (pricing page 403) |
| **Govlist** | **No product of this name found** in two sessions (searches return CivicPlus/GovDelivery list pages; govlist.com/.ai/.io/.us do not resolve) | — | — | E · searches this session and `competitor_coverage_map.md` Gaps |
| **Ballotpedia** (local) | Whole encyclopedia free; "more than a dozen newsletters", "more than 600,000 active subscribers"; local scope = 100 largest cities + overlapping counties + state capitals, all local measures in CA and VA | Local elections and ballot measures only | Data packages and custom quotes ("custom quotes for local expansion available on request") | V · [Ballotpedia careers llms.txt](https://apply.workable.com/ballotpedia/llms.txt); V-idx · [Services](https://ballotpedia.org/Services); V-prior · [Texas cities](https://ballotpedia.org/Texas_cities) |
| **Documenters** (City Bureau) | Free notes, live-posts and reports from paid resident note-takers | ~8 city sites seen (LA, Detroit, Twin Cities, Kansas City, Chicago, Grand Rapids, Akron, San Diego); some last posted 2025 | Not a product; grant-funded | S · [LA Documenters](https://losangeles.documenters.org/), [Detroit](https://detroit.documenters.org/) (documenters.org 403 to direct fetch) |
| **Agenda Watch** (Big Local News) | Daily harvest of agendas; alerts "when similar items crop up" | Needs a MuckRock account; limited to a handful of agenda platforms | Not sold | S · [RJI](https://rjionline.org/news/welcome-to-agenda-watch/), [MuckRock](https://muckrock.com/news/archives/2023/jun/28/agenda-watch-muckrock-accounts) |

### B. Siting and data-center trackers

| Product | Free | Limits on free | Paid step | Label · Source |
|---|---|---|---|---|
| **Heatmap** | Free articles after registration (count not stated); some newsletters | Metered; **The Fight** (weekly local-opposition newsletter) and "Key project and policy alerts" are **Heatmap Plus** benefits | Heatmap News $9.99/mo or $99/yr; Plus (price not seen); **Pro** by demo: local-law database, county/ZIP Opposition Risk Score, contested-project database, custom exports | V · [Heatmap Pro](https://heatmap.news/pro); V-idx · [subscription page](https://heatmap.news/st/Landing_Subscription) |
| **Cleanview** | "Free Trackers": Data Center Map, Solar Farm, Battery Storage, Wind Farm and Gas Power Plant trackers; state pages and largest-project tables visible without sign-in | No downloads or alerts stated on free | Data-center or power platform **$9,000/yr** (5 users, unlimited downloads); API **+$5,000/yr**; one-time download $4,900 | V · [pricing](https://cleanview.co/pricing), [US data centers](https://cleanview.co/data-centers/us) |
| **dcmap.us** | Map, state/county/market pages, and a "free research layer for agents": static JSON with "No key, account, JavaScript, or query cost", OpenAPI 3.1, MCP server with "No authentication required" | "Updated monthly"; terms bar "bulk reproduction or scraping of the underlying dataset"; cite as "US Data Center Map, data as of Oct 2026" | None | V · [home](https://dcmap.us/), [developers](https://dcmap.us/developers/), [cite](https://dcmap.us/cite/) |
| **Data Center Watch** (10a Labs) | "Free weekly updates on the political risks facing American data center projects" (Substack); quarterly reports | Gating of reports not stated | None seen | V · [datacenterwatch.org](https://datacenterwatch.org/) |
| **Electric Choice tracker** | Open page; counts "reconciled monthly", "a floor rather than a precise census" | No download, no alerts; "All rights reserved" | None (lead-gen for energy rates) | V · [tracker](https://www.electricchoice.com/datacenters/moratoriums/) |
| **Carina BESS Moratorium Monitor** | Public map of 174 jurisdictions | Monthly updates | "Full Database + Alerts" by subscription | V-prior · [Carina](https://carina.energy/bess-moratoriums/) |
| **SitePath** | "Free to explore the map"; "Free email updates" | — | Priced per organisation and seats | V-prior · [sitepathintel.com](https://www.sitepathintel.com/) |
| **Zoneomics** | **No free plan** | — | Essentials $92/mo (25 searches, 1 report); Advanced $279/mo (150 searches) | V · [pricing](https://www.zoneomics.com/pricing) |
| **Shovels** | Free: **500 credits/mo** ("1 credit = 1 record"), **1 year** of history, API and CLI included, "up to 10 results per query"; no card | **No downloads**; no Employees dataset | **Basic $599/mo**: 25,000 credits, downloads, "full historical records" | V · [pricing](https://www.shovels.ai/pricing) |

### C. General-purpose free alert tools

| Product | Free | Limits | First paid step | Label · Source |
|---|---|---|---|---|
| **Google Alerts** | Keyword alerts; "As-it-happens", "At most once a day", "At most once a week"; sources, region, "Only the best results"/"All results" | Email; **RSS delivery only when signed in**; covers only indexed pages (town PDFs index slowly) | None | V · [google.com/alerts](https://www.google.com/alerts), [help](https://support.google.com/websearch/answer/4815696?hl=en); S · [Search Engine Land](https://searchengineland.com/google-adds-rss-feeds-for-web-search-results-15287), [RSS Ground](https://rssground.helpwise.help/article/224-how-to-generate-google-alert-rss-feed); E (PDF lag) |
| **Talkwalker Alerts** | "You can receive Alerts via email, RSS, or through a Slack integration"; "As it happens" | Email verification; news, X, blogs, forums | None stated | V · [talkwalker.com/alerts](https://www.talkwalker.com/alerts) |
| **F5Bot** | "Free forever": keyword alerts on Reddit, HN, Lobsters; **email only**; basic filters; account by email, no card | Keyword cap not stated; emails carry ads (Silver is "Ad-free") | **Silver $9.99/mo**: 20 keywords, full text, ad-free. **Gold $49.99/mo**: 200 keywords, **RSS/JSON, Slack/Discord**, AI filtering | V · [f5bot.com](https://f5bot.com/) |
| **Visualping** | **5 pages, 150 checks/mo, 60-min minimum interval**; email, webhooks, Telegram; 3 months of history | No Slack, Teams, SMS on free | **Personal $14/mo** ($10/mo annual): 10 pages, 1,000 checks, every 15 min; no new channels | V · [pricing](https://visualping.io/pricing) |

### D. Town-run and public-notice options

| Option | Free | Limits | Label · Source |
|---|---|---|---|
| **CivicPlus Notify Me / Agenda Center** | Email and/or SMS per list; lists named by board (BZA, Planning Commission, Commissioners …) | **"Sign In" is step 1**; one list per board; **no keyword filter**; email verification; only CivicPlus towns | V · [Henry County, IN](https://henrycounty.in.gov/List.aspx); S · [Milton, MA guide](https://miltonma.gov/1025/Notifications-and-Alerts) |
| **Granicus govDelivery** | Email or text by topic (e.g. Sunnyvale "Meeting Agendas & Public Notices") | Subscriber account by email; topic = board or whole-city notices, no keyword filter; spam-folder issues noted | S · [Iowa DX training](https://dxtraining.iowa.gov/digital-services/granicus-communications/granicus-communications-subscribing-unsubscribing-and-unsuppressing), [Sunnyvale](https://www.sunnyvale.ca.gov/your-government/about/subscribe), [Gray, ME](https://www.graymaine.org/home/home/news/gray-town-meeting-portal-updates) |
| **BoardDocs / board portals** | Varies: Essex County, NY portal "Subscriptions" per board after creating an account; Boardable public sites email subscribers per committee without an account | No vendor help page found for BoardDocs | S · [Essex County NY](https://essex.org/1384/NEW-AGENDA-NOTIFICATIONS), [Boardable docs](https://docs.boardable.com/knowledge/subscribe-to-public-site-updates) |
| **Town Facebook pages / groups** | Free; where most residents already are: **52% of US adults get local news from online forums or groups (community Facebook groups, Nextdoor)** in 2025, up from 38% in 2018; 40% from local government agencies or officials | Algorithmic reach; no structured alerts | S · [Pew chart (Dec 2025 survey), via search index](https://www.pewresearch.org/chart/where-americans-get-local-news/) (403 to direct fetch) |
| **Nextdoor** | Free for agencies; residents in the jurisdiction are auto-subscribed to agency posts | **"Programs, committees, task forces, sub-districts, and elected officials are not qualified"**, so a planning board cannot post as an agency | V-idx · [Nextdoor agency FAQ via search](https://business.nextdoor.com/en-au/publicservices-faq), [Nextdoor public agency](https://business.nextdoor.com/en-us/public-agency) |
| **Iowa statewide notice site** | Statute: notices "available to the public at no cost"; search; **1 year** of access; must offer **email alerts**, but "may charge a fee to an individual subscriber" up to cost. iowapublicnotices.com: free "Smart Search" registration with daily email of matching notices; 8,000–10,000 notices a month | Account for Smart Search; keyword on notice text | V · [Iowa Code 618.3A](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf); V-idx · [iowapublicnotices.com](https://iowapublicnotices.com/); S · [INA](https://inanews.com/?p=249) |
| **Maine** | Statute: statewide association provides "e-mail notification of legal notices upon request and at no charge", sent "on the same day" | Legal notices only (hearings, not agendas) | V · [1 MRSA §603](https://mainelegislature.org/legis/statutes/1/title1sec603.html) |
| **Massachusetts** (masspublicnotices.org) | Statewide legal notices, 12-month search; c.40A §11 hearing notices run ≥14 days ahead; also notifies "the planning board of every abutting city or town" | "Smart Search" price not shown | V-prior · `where_we_win.md`; V · [c.40A §11](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40A/Section11) |
| **Patch** | Free local sites and daily town newsletters | Coverage uneven; "more than 1,000 local sites" (c. 2022); a directory claims "30,000 communities" of AI newsletters (low confidence) | S · [Radio Ink](https://radioink.com/?p=55351), [Nieman Lab 2016](https://www.niemanlab.org/?p=132500), [bitscale (low quality)](https://bitscale.ai/directory/patchcom) |

## 2. What a resident or a professional already gets free, and the gaps

### Takeaway
A resident can already get, free: an email when a board posts any agenda (if the town uses Notify Me or govDelivery and they make an account), legal-notice search (and email alerts in IA and ME), post-meeting recaps for one place (Citizen Portal, LocalGovIndex, MyTownView), and national data-center maps that update monthly. **What nobody gives free is the combination residents need: siting topics only, across every board, across the town line, before the meeting, on a calendar, with no account.** A professional can get free samples (Shovels 500 records, Visualping 5 pages, Cleanview and Carina maps, dcmap JSON) but no free multi-town pre-meeting siting feed; the paid steps start at $92/mo and most siting tools are quote-only.

### Cited Findings: by job to be done

| Job | Free today | Who | Gap | Label · Source |
|---|---|---|---|---|
| Know an agenda is posted | Per-board email/SMS lists | CivicPlus Notify Me (195 MA AgendaCenter sites), govDelivery | Account; one subscription per board per town; every agenda, no topic filter; only towns on those vendors | V · [Henry County Notify Me](https://henrycounty.in.gov/List.aspx); V-prior · `where_we_win.md` row "town Notify Me" |
| Know a siting item is on any board's agenda | LocalGovIndex free: one board, agenda summary + recap by email | LocalGovIndex | One body only; email only; account; coverage "thousands of places" not listed | V · [LocalGovIndex pricing](https://localgovindex.com/pricing) |
| Know a hearing is coming | Newspaper legal notices; MA hearing notices run ≥14 days ahead; free statutory email alerts in IA (fee allowed at cost) and ME | State press associations | Mailed notice reaches only owners within 300 ft (MA) | V · [Iowa 618.3A](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf), [Maine §603](https://mainelegislature.org/legis/statutes/1/title1sec603.html), [MA c.40A §11](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40A/Section11) |
| Hear what a neighbouring town is doing | Statutes notify the neighbour's **government**, not its residents: MA notifies "the planning board of every abutting city or town"; NY GML §239-nn notifies the adjacent municipality's clerk ≥10 days ahead for site plans, special permits, use variances and subdivisions within 500 ft; VA §15.2-2204 notifies the adjoining locality's chief administrative officer ≥10 days ahead for land within one-half mile | Statute | No free tool turns these into resident alerts | V · [MA c.40A §11](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40A/Section11), [NY GML §239-nn](https://www.nysenate.gov/legislation/laws/GMU/239-NN), [VA §15.2-2204](https://law.lis.virginia.gov/vacode/title15.2/chapter22/section15.2-2204/) |
| Read what happened | Recaps and transcripts | Citizen Portal (1 location, a few articles a day), MyTownView (browse, no account), Red Tape, CivicSearch, Hamlet (initial searches), Documenters (≈8 cities), Patch | After the meeting; coverage uneven | V/V-idx · §1 table A |
| Watch data centers | National maps and trackers | dcmap (monthly, keyless JSON/MCP), Cleanview free trackers, Electric Choice (monthly), Data Center Watch (weekly newsletter) | After adoption; counts disagree by an order of magnitude by state (MI: 63 vs 0 vs 20+) | V · §1 table B; V-prior · `competitor_coverage_map.md` §2 |
| Keyword alerts on the web | Google Alerts, Talkwalker | Google, Talkwalker | Only once a page is indexed or covered by news; in news deserts there is little to index | V · [Google Alerts](https://www.google.com/alerts), [Talkwalker](https://www.talkwalker.com/alerts); E |
| Get it where neighbours talk | Facebook groups, Nextdoor | Residents | 52% of adults get local news from online forums/groups (2025); planning boards cannot post as Nextdoor agencies | S · [Pew chart](https://www.pewresearch.org/chart/where-americans-get-local-news/); V-idx · [Nextdoor FAQ](https://business.nextdoor.com/en-au/publicservices-faq) |
| Professional: sample data | Shovels 500 records/mo (1 yr, no downloads); Visualping 5 pages hourly; Docket Alarm 5 actions/week; BillTrack50 bill search | Vendors | Samples, not a multi-town feed | V · [Shovels](https://www.shovels.ai/pricing), [Visualping](https://visualping.io/pricing), [Docket Alarm](https://www.docketalarm.com/about), [BillTrack50](https://www.billtrack50.com/info/pricing) |
| Professional: multi-town pre-meeting siting feed | **None free.** Paid comparators: Zoneomics $92+/mo, Shovels $599+/mo, Cleanview $9k/yr, LocalGovIndex Professional $399/mo; Heatmap, Spark, Hamlet by quote | — | Whole gap | V · §1; V-prior · `competitor_coverage_map.md` §4 |

### Inferences
- [E] **The resident gap is not data, it is packaging.** The facts are public (agendas, notices), but they arrive per board, per vendor, behind accounts, without a topic filter and without the neighbouring towns. A free 351 Watch area that fixes those five things has no free equal.
- [E] **The neighbour gap is the most distinctive free feature.** Three states already treat abutting towns as affected parties, yet only the neighbour's officials hear about it. Residents near a town line are the people most likely to be surprised.
- [E] **A professional's free substitute is DIY.** Visualping's free plan can watch five agenda pages hourly, so a single-area free tier from 351 Watch does not undercut anything a professional could not already do for free. Professionals pay for breadth (dozens of towns), filtering and team delivery, which DIY cannot match at scale.

## 3. Free-tier designs that drove growth in comparable products

### Takeaway
- **Public pages stay free and ungated in every data business that grew on search** (Zillow, Ballotpedia, OpenSecrets, dcmap). They monetise a smaller professional audience (agents, data licensees) or donors, not the readers.
- **Paid steps gate one of five things:** places, count, speed, history/export/API, or team channels. Products sold by geography (onX, BillTrack50) price per area with a cap. Utilities (Visualping, F5Bot) gate count and speed. Data products (Shovels, Crunchbase) gate history, exports and API. Alert products keep team channels (Slack, Teams, Discord, RSS) for paid tiers.
- **Conversion evidence:** in the one current benchmark (ChartMogul/ProductLed, Jan 2026, n=200), freemium turns 9% of visitors into sign-ups and 5.5% of those into payers; **ungated** freemium (use before sign-up, which is 351 Watch's model) gets 7% and 8%, about 5.6 payers per 1,000 visitors. "Good" self-serve freemium conversion is 3–5% (Lenny Rachitsky). These are B2B SaaS numbers; a product whose free users are mostly residents should expect far lower whole-base conversion and should measure conversion on the professional subset only [E].

### Cited Findings: what comparable products give and gate

| Product | Free | What paid gates | Growth / outcome evidence | Label · Source |
|---|---|---|---|---|
| **Zillow** | All home pages and Zestimates: "an unwavering commitment to giving consumers free access to as much useful information as possible" | Nothing for consumers; agents and lenders pay for advertising to that audience | 123.7M average monthly unique users (Q4 2015, +61% y/y); "The majority of our traffic comes direct, not dependent on search engines" | V · [Zillow 10-K FY2015](https://www.sec.gov/Archives/edgar/data/0001617640/000119312516461241/d78539d10k.htm) |
| **Ballotpedia** | Everything; a dozen newsletters | Custom data packages and quotes | "more than 600,000 active subscribers"; "77th most-visited website in the U.S." in the month of the Nov 2020 election | V · [careers llms.txt](https://apply.workable.com/ballotpedia/llms.txt); V-idx · [Services](https://ballotpedia.org/Services) |
| **OpenSecrets** | Whole website | Commercial data licensing and custom research; API reportedly deactivated | ">7 million annual users" | S · [civictech.guide](https://directory.civictech.guide/listing/opensecretsorg), [Devpost note on API](https://devpost.com/software/openpocket), [2009 licensing](https://lists-archive.okfn.org/pipermail/okfn-discuss/2009-April/012492.html) |
| **dcmap.us** | Map, pages, keyless JSON, MCP | Nothing; bars bulk copying | Cited as a free baseline in earlier notes | V · [developers](https://dcmap.us/developers/), [cite](https://dcmap.us/cite/) |
| **Google Alerts** | Unlimited keyword alerts; email; RSS when signed in | No paid tier | Ubiquitous; the RSS link is an unguessable URL, the model 351 Watch copies | V · [google.com/alerts](https://www.google.com/alerts); S · [Search Engine Land](https://searchengineland.com/google-adds-rss-feeds-for-web-search-results-15287) |
| **Talkwalker Alerts** | Email, RSS and Slack, as it happens | No paid alert tier; acts as a front door to the enterprise social-listening platform | — | V · [talkwalker.com/alerts](https://www.talkwalker.com/alerts); E (funnel reading) |
| **Visualping** | 5 pages, 150 checks/mo, hourly, email + webhook, 3 months history | Count (10 pages, 1,000 checks) and **speed** (15 min); Slack/Teams/SMS only higher | "2M+ users since 2013" (vendor claim) | V · [pricing](https://visualping.io/pricing), [claim](https://visualping.io/versionista-alternative) |
| **F5Bot** | Email keyword alerts, ad-supported | Keywords (20/200), ad-free, full text; **RSS/JSON and Slack/Discord only on the top plan** | Was free-only for years before adding tiers [K] | V · [f5bot.com](https://f5bot.com/) |
| **Shovels** | 500 records/mo, 1 year of history, API included | Volume, **full history, downloads** | Revenue "tripled" after the mid-2025 seed | V · [pricing](https://www.shovels.ai/pricing); V-prior · `durability_and_acquirers.md` |
| **Crunchbase** | Search and basic profiles; limited profile views; no exports, alerts or lists | **Pro ~$49/mo annual**: full search, saved searches, alerts, exports (2,000–5,000 rows) | — | S · [ZoomInfo review](https://pipeline.zoominfo.com/sales/crunchbase-pricing), [SyncGTM](https://syncgtm.com/blog/crunchbase-pro-review-2026) |
| **PitchBook** | Public company profile pages (SEO), news | Everything else; no general free tier; trial disputed | — | S · [Capterra review](https://www.capterra.ch/reviews/202323/pitchbook), [Babson guide](https://www.babson.edu/media/babson/assets/cutler-center/Pitchook_-Beginners-Guide-to-Getting-Started_Li_Update-Feb-2023.pdf) (pitchbook.com 403 to fetch) |
| **CourtListener** (Free Law Project) | Search; **5 docket alerts free**; +10 with the RECAP extension; webhooks | Unlimited alerts for monthly donors; free memberships for .edu | Nonprofit; donor-supported | S · [Free Law 2018](https://free.law/2018/08/21/announcing-pacer-docket-alerts-for-journalists-lawyers-researchers-and-the-public/), [Free Law 2025](https://free.law/2025/09/05/libguide/); V · [alerts help](https://wiki.free.law/c/courtlistener/help/alerts/) |
| **Docket Alarm** | "5 free actions / week" | Pay-as-you-go $39.99/mo; flat $99/mo "everything unlimited" | — | V · [about](https://www.docketalarm.com/about) |
| **BillTrack50** | Search and share bills in the current session; no saving, tracking or alerts | **Per state**: $1,000/yr per state "until you reach the maximum of $5,000" (all states); unlimited users; API; history to 2011 | — | V · [pricing](https://www.billtrack50.com/info/pricing) |
| **onX Hunt** | 7-day trial only | **Per area**: one state $34.99/yr, two states $49.99/yr, all states $99.99/yr | Upgrade path is "add another state" | V · [pricing](https://www.onxmaps.com/hunt/app/pricing) |
| **LocalGovIndex** | One board or council by email | "Any place" at $9/mo; exports at $49; bulk at $399; API at $2,500+ | — | V · [pricing](https://localgovindex.com/pricing) |
| **Citizen Portal** | Follow 1 location; a few articles/day | Unlimited reading and topic alerts $15/mo; "nearly unlimited topics and locations" $299 once | — | V-idx · [pricing via search](https://citizenportal.ai/checkoutlifetime) |
| **MyTownView** | Browse all towns, no account | Own-town alerts $29.99/yr; unlimited alerts and CSV $199/yr | — | V · [pricing](https://mytownview.com/pricing) |

**Conversion benchmarks**

| Metric | Value | Label · Source |
|---|---|---|
| Freemium visitor→sign-up / free→paid | 9% / 5.5% (≈5 payers per 1,000 visitors) | V · [ChartMogul SaaS Conversion Report, Feb 2026, n=200](https://chartmogul.com/reports/saas-conversion-report/) |
| Ungated freemium (use before sign-up) | 7% / 8% (≈5.6 per 1,000); "up to a 3x increase in visitors who start using" (author observation) | V · same |
| Free trial (no card) / card-required trial | 4.5% / 8%; card-required 3.5% / 30% | V · same |
| Distribution | Bimodal: 25% of freemium products convert <2.5%, 25% convert 10–15%; median 8% | V · same; S · [Userpilot summary](https://userpilot.com/blog/freemium-to-premium) |
| "Good / great" self-serve freemium | 3–5% / 6–8%; sales-assisted 5–7% / 10–15% | V · [Lenny's Newsletter](https://www.lennysnewsletter.com/p/what-is-a-good-free-to-paid-conversion) |

### Inferences
- [E] **Per-area pricing is a proven consumer pattern and a proven professional pattern.** onX (one state → two states → all) and BillTrack50 (per state up to a cap) both sell geography, and both cap the top so heavy users are not punished. That is the closest analogue to "free for one area, paid for more".
- [E] **The civic-meeting rivals all put "one place" free and "any place" in the first paid step**, so 351 Watch's model matches the market. Where 351 Watch can be more generous is the definition of the place (see §4) and the channels (calendar, feeds) that rivals keep to email or to paid.
- [E] **Alerts alone rarely pay for themselves** (Google, Talkwalker, Ballotpedia and OpenSecrets give them away). Money comes from a professional layer: breadth, history, exports/API, team channels, speed. 351 Watch's paid line should be built from those, not from withholding facts from residents.
- [E] **Gating team channels works because teams, not individuals, pay.** F5Bot and Visualping keep Slack/Teams off their entry tiers. For 351 Watch, Slack/Teams/webhook delivery of more than one area is a natural paid line; a single-area Discord or Slack hook for a community group can stay free without much loss.

## 4. Three free-tier designs for 351 Watch, and a recommendation

### Takeaway
**Recommend Design A, "My town and its neighbours".** One free area is the home town plus every jurisdiction that touches it, with every topic, every board, every delivery channel 351 Watch already has, and the same data residents would get if they paid. Paid starts at the second area and adds what only multi-area users need: many areas in one feed, team routing, faster refresh, company watch, exports, API and history in bulk. Search and every public page stay free and indexable. Abuse is handled by splitting the watchlist link into a shareable read link and a private manage link, by making each free watchlist a valid area that cannot be rotated around the state, and by fencing free webhooks per destination (a Slack workspace's ID is in its webhook URL), while accepting some leakage.

### What "one area" should mean

| Unit | MA / RI / NY (town grain) | MI, PA, OH, WI (township grain) | VA, UT, TX, Plains (county grain) | Verdict [E] |
|---|---|---|---|---|
| **One town** | Clean, but misses abutting-town projects that state law already treats as affecting neighbours | Townships are 6×6 mi squares [K]; one is small | A county is large; a city alone misses the county board that zones around it | Too narrow for residents |
| **County** | MA has no county zoning; NY counties only review (GML §239-m referrals) [V-prior, `state_agenda_laws.md`]; NY counties hold 20–30 towns [K] | Too big (dozens of townships) | The real zoning unit for unincorporated land | Right only in county states |
| **Radius of N miles** | 5 mi ≈ home + neighbours; 10 mi ≈ 10–15 towns (MA towns average ~22 sq mi: ~7,800 sq mi / 351 [K/E]) | Similar | Usually equals a county | Fair across states, but agenda items are rarely geocoded, so it is a proxy for a jurisdiction set and is harder to explain |
| **Home + adjacent jurisdictions + the county board that zones the home** | ~7 towns (≈150 sq mi) [E] | ~9 townships + cities [E] | County + adjacent counties: can cover a whole data-center market (e.g. Loudoun with Fairfax, Fauquier, Clarke [K]) | **Best fit for town and township states; needs a cap in county states** |

Legal hook for "neighbours": MA notifies "the planning board of every abutting city or town"; NY notifies an adjacent municipality for site plans, special permits, use variances and subdivisions within 500 ft; VA notifies an adjoining locality for land within one-half mile [V · [MA](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40A/Section11), [NY](https://www.nysenate.gov/legislation/laws/GMU/239-NN), [VA](https://law.lis.virginia.gov/vacode/title15.2/chapter22/section15.2-2204/)].

### Design A (recommended): "My town and its neighbours"

| | Free | Paid (first step = a second area) |
|---|---|---|
| Area | Home jurisdiction + all jurisdictions that touch it (pre-selected, removable) + the county board where counties zone. In county states, cap at the home county + its cities/towns, and add neighbouring counties' items only when they are near the line (VA's half-mile rule gives a test) [E] | Any number of areas in **one** feed; county clusters; statewide topic feeds (e.g. every BESS moratorium in MA) |
| Topics, boards | All siting topics, all boards, warrants, AG decisions, wetlands filings as they ship | Same, plus **company/LLC watch** |
| Delivery | Web page, RSS/JSON, **iCal**, one webhook (Slack, Teams, Discord), printable sheet; later web push | Many areas routed to many channels; per-topic routing; seats for collaborators |
| Refresh | Daily (today's cadence); **never delayed on purpose** | Every 6 hours for watched areas (proposed in `where_we_win.md`) |
| History, search | Full public history and site search, free | Bulk CSV/JSON export, API, history downloads, project timelines (consolidated-permit clock) |
| Public pages | Town, item, hearing, tracker, AG ledger pages: free, indexable, no login wall | Same |
| Fit with owner's model | Exactly "free for one area"; the area is defined around a person | Exactly "paid for more than one area" |

**Why A** [E, built on the evidence above]:
1. **It is the only design that answers the resident's real question** ("what is coming near me?") and the gap no free product fills (§2). The legal notice regime already treats neighbours as affected.
2. **It costs almost nothing.** 351 Watch crawls every covered town anyway; a bigger free area only changes which already-matched items a feed shows.
3. **It does not give away the professional product.** Professionals' value is breadth (dozens of towns; 6.5 planned sites per data-center developer, `who_needs_it_most.md` §5), team delivery and speed. Single-area DIY is already free (Visualping 5 pages hourly).
4. **It matches the market's first paid step** ("any place": LocalGovIndex, Citizen Portal) and per-area pricing (onX, BillTrack50), but with a more generous free unit, which is the differentiation residents will notice.
5. **Ungated beats gated.** Public pages and watchlists without sign-up fit the ungated-freemium pattern that gets more people to use the product (ChartMogul).

### Design B: "One town free, neighbours paid"

| | Free | Paid |
|---|---|---|
| Area | Exactly one town (or county in county states) | "+ neighbours" as a small consumer add-on; then multi-area |
| Delivery, refresh, pages | As Design A | As Design A |
| Fit | "One area" read literally | Adds a consumer step before the professional step |

- **For:** clearest upsell; some consumer revenue; simplest to explain.
- **Against:** charges residents for the cross-border case that matters most; consumer anchors are low ($9/mo LocalGovIndex, $15/mo Citizen Portal, $29.99/yr MyTownView), and news-desert residents are the least likely to pay; neighbours' items are on free public pages anyway, so the gate only blocks alerts, which looks like a paywall on public information [E].

### Design C: "Radius around a place"

| | Free | Paid |
|---|---|---|
| Area | Every jurisdiction within N miles (e.g. 5) of the home town's boundary | Larger radius, several radii, or a radius around a project site or parcel |
| Delivery, refresh, pages | As Design A | As Design A, plus "site watch" for professionals |
| Fit | Normalises area across states (6-mile townships vs 400-sq-mi counties [K]) | Natural slider upsell |

- **For:** fairest across states; maps to how impacts spread; a radius around a project site is a good paid professional feature even if A is chosen.
- **Against:** items are at jurisdiction grain, so the radius is a proxy; a county board's item covers the whole county, which makes the radius jump; harder to explain and to compute; in county states 5 miles often equals the whole county [E].

### Abuse controls without accounts (all designs)

Current state, read from the code: one random ID (24+ chars) both reads the feeds and edits or deletes the watchlist (`site/api/watchlists.js`: "POST creates, GET ?id= reads, PATCH ?id= updates, DELETE ?id= deletes"); up to `MAX_TOWNS = 200` towns per watchlist; a honeypot field on create; a webhook host allowlist and a "test" action; feeds cached 300 s [V · local code `projects/351watch/site/api/_watch.js`, `watchlists.js`, `feed.js`].

| Control | Why | Label · Source |
|---|---|---|
| **Split the link**: a shareable read-only link (web, RSS, iCal) and a private manage link (edit, delete, webhook); allow "regenerate" | Sharing the iCal or page link in a Facebook group (which §5 encourages) currently hands out edit and delete rights. W3C guidance: unguessable IDs, HTTPS, keep out of search, avoid third-party scripts and Referer leaks, allow revocation and regeneration, separate permissions | V · [W3C TAG, Good Practices for Capability URLs](https://www.w3.org/TR/capability-urls/); V · local code |
| **Validate the free area server-side** (home + adjacency set, or the county rule) instead of the 200-town cap | Makes "one area" real without accounts | E |
| **Throttle area changes** (e.g. one change a week per free watchlist) | Stops one free watchlist being rotated around the state | E |
| **One free area per webhook destination.** Slack URLs carry the workspace ID (`hooks.slack.com/services/T…/B…/…`, one channel per hook); count free areas per workspace and put an upgrade line in messages beyond the first | The only cheap, account-free fence on team use; Slack also says the URL "contains a secret" | V · [Slack incoming webhooks](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks); E (T = workspace inferred from the doc's `team_id` example) |
| **Bot friction on create**: keep the honeypot, add a challenge (e.g. Turnstile) and a per-IP rate limit | Stops scripted mass creation | E |
| **Expire idle watchlists** (no page visit or feed fetch in N days); 410 after expiry | Cleans out abandoned or bot lists; feed polling keeps real ones alive | V · [W3C capability URLs](https://www.w3.org/TR/capability-urls/) (expiry, 410) |
| **Terms for reuse**: free citation with attribution; no bulk copying; API and bulk files paid | dcmap's model: "Just don't copy the whole dataset" | V · [dcmap cite](https://dcmap.us/cite/) |
| **Accept some leakage** | A firm that hand-builds 20 free watchlists pays in time and gets 20 separate feeds; the paid line sells one feed, routing, speed and exports. Without accounts, caps per person cannot be enforced; value must do the work | E |

### Risks of Design A
1. **Leakage by professionals** making many free watchlists. Mitigated by the webhook-destination fence and convenience, not prevented [E].
2. **County states give away markets.** "Loudoun + neighbours" covers much of Northern Virginia's data-center market. Use the capped county rule there and revisit with real usage before launching VA and UT [E/K].
3. **Residents rely on it to attend.** A missed or late item harms trust. Show the source link, posting time and "verify with the town" on every item, and never delay free alerts on purpose [E]. MA data: the 10th-percentile agenda posts 2 days ahead and 4% first appear on the meeting day [V-prior · `where_we_win.md`].
4. **Calendar lag.** Google Calendar refreshes subscribed iCal feeds on its own schedule (reported as up to 12–24 hours), so the iCal feed suits hearings days away, not same-day changes [S · [AddCal](https://help.addcal.co/en/articles/11933752-calendar-subscriber-update-delay), [Usecarly](https://usecarly.com/blog/google-calendar-ics-refresh-rate/)].
5. **Teams delivery may break.** Office 365 connector webhooks (`*.webhook.office.com`) were retired in 2026 (dates reported from Mar 31 to May 22); replacement Workflows URLs are reported on Power Automate hosts. The current allowlist accepts `*.webhook.office.com`, `outlook.office.com` and `*.logic.azure.com` only; check a fresh Workflows URL before promising Teams on the free tier [S · [Argo CD docs](https://argo-cd.readthedocs.io/en/latest/operator-manual/notifications/services/teams/), [Beanbag](https://blog.beanbaginc.com/?p=1308), [HANDS ON tek](https://m365admin.handsontek.net/?p=17449); V · local code].
6. **Hosting terms.** Charging requires moving off Vercel Hobby (non-commercial) [V-prior · `where_we_win.md`, VALIDATION.md].
7. **Perception.** Free alerts will be used most by people opposing projects. Keep the same facts, neutral wording and the same free tier for every side [E].
8. **Consumer price anchors are low** if the owner later wants a consumer paid step ($9/mo to $29.99/yr). Revenue should be planned around professionals [E].

## 5. Free features most likely to be loved and shared

### Takeaway
Residents share where they already talk: community Facebook groups and Nextdoor (52% of US adults get local news there) [S · [Pew](https://www.pewresearch.org/chart/where-americans-get-local-news/)], and planning boards cannot post on Nextdoor as agencies [V-idx · [Nextdoor FAQ](https://business.nextdoor.com/en-au/publicservices-faq)]. So the free features that spread are the ones that make a single item easy to post, easy to put on a calendar and easy to print. Ranked by expected love × spread [E]:

| Rank | Feature | Why it spreads or sticks | Build notes | Label |
|---|---|---|---|---|
| 1 | **Item permalinks that preview well** (board, date, topic, address, one-line summary, source link, "posted N days before the meeting") | Each share in a town Facebook group or Nextdoor is an ad for the town page and a "watch this area" button. Open Graph title and image matter more than the page | One stable URL per item; OG tags; "Share" and "Copy link"; a "watch this area" button on every item | E; S (Pew) |
| 2 | **Neighbour alerts ("Across the line")** | Nobody else does it; the law already says neighbours are affected (MA abutting planning boards, NY 500 ft, VA half mile); it is what residents near a border miss | Tag items in adjacent jurisdictions in the free area; label "next door in [Town]" | V (statutes, §2); E |
| 3 | **iCal feed of upcoming hearings for my area** | Lives in the calendar people already check; each event links back; reminders come free from the calendar app; hearings are days away, so calendar refresh lag is tolerable | Exists today (`format=ics`); add "Add to Google / Apple / Outlook" buttons and per-item "Add to calendar" | V (local code); S (refresh lag, §4 risk 4) |
| 4 | **Printable "What's coming up" sheet** per area (one page, week or month; QR code to the area page) | Reaches people offline and in news deserts: library, town hall, general store, senior centre, church bulletin. Every sheet is a poster for the product | Print CSS or PDF; large type; dates, boards, items, how to comment; QR | E |
| 5 | **"How to take part" box on each hearing item**: date, time, place, remote link, written-comment deadline, what the board can decide, what happens next (e.g. continued, AG review) | Turns an alert into action; the reason people forward it | From agenda text and known process (MA AG review median ≈108 days, `where_we_win.md`) | V-prior; E |
| 6 | **Status timeline per item** (on agenda → continued → decided → AG approved/disapproved) | Makes people come back; settles arguments in comment threads | Link repeat appearances of the same item | E |
| 7 | **Free Discord/Slack hook for a community group's one area** | Community groups and town committees organise in Discord, Slack or GroupMe; one hook reaches many members | Exists (webhooks); keep one per free area | V (local code); E |
| 8 | **Email without an email product**: a one-click "get this by email" that hands the RSS link to a free RSS-to-email service | Many residents only use email. Blogtrottr has a free plan with "no limits on the number of subscriptions" (ads in each message); Feedrabbit's free plan allows 10 feeds and 20 emails a day; follow.it 20 feeds | Link out; no list kept by 351 Watch | S · [TidBITS 2024](https://tidbits.com/2024/08/22/comparing-blogtrottr-feedrabbit-and-follow-it-for-receiving-rss-feeds-in-email/) |
| 9 | **Web push for an installed home-screen app** | Phone notifications without email or an app store; iOS supports push for home-screen web apps since 16.4, only after a user tap | Service worker + Push API; later | S · [WebKit blog via search](https://webkit.org/?p=13878), [9to5Mac](https://9to5mac.com/2023/02/16/iphone-web-app-new-features-ios-16-4/) |
| 10 | **Embeddable "coming up" widget and "cite this"** for library sites, local newsletters, Patch-style blogs and newsrooms | Each embed is a backlink; journalists and newsletters cite dated, sourced items | iframe or script; CC BY citation box | E; V-prior (`where_we_win.md` citation plan) |

### Inferences
- [E] **The first three cost little because the pieces exist** (permalinks, ICS, adjacency from town boundaries). The printable sheet is the cheapest feature aimed squarely at news-desert towns.
- [E] **Keep every one of these free in Design A.** None of them is what a multi-area professional pays for, and each one creates a visit, a share or a citation.
- [E] **Measure sharing, not sign-ups:** item-permalink visits from facebook.com / nextdoor.com referrers, QR scans from printed sheets (use a `?src=print` tag), ICS subscribers (distinct feed fetchers), and watchlists created from an item page.

---

## Gaps and things not checked

- **Govlist**: no product of that name was found (also not in the Oct 11 session). If the owner has a URL, it should be checked.
- **Pages blocked to the fetcher today**: citizenportal.ai (403; read through search-index quotes), myhamlet.com (HTTP 429 Vercel checkpoint), civiciq.com pricing (403), documenters.org (403 earlier), pitchbook.com profiles (403), Pew chart (403; quoted from the search index), Nextdoor agency FAQ (US page 404; quoted from the AU page via search). No bot check was bypassed and no account was made.
- **Citizen Portal's free tier conflicts** between its pricing page (topic alerts paid) and help centre (alerts free with sign-in). Not resolvable without an account.
- **Hamlet's free tier limits** (how many searches; whether saved searches and keyword alerts are free) are not published.
- **GatherGov's "Start for free"** has no published limits; its /pricing returns 404.
- **CivicSearch** is a JavaScript app; nothing was readable directly today.
- **BoardDocs** public subscription behaviour could not be confirmed from a vendor page.
- **Google Alerts RSS requires sign-in** is from secondary sources; Google's own help page mentions only email.
- **Crunchbase and PitchBook** free-tier details are from review sites, not the vendors' pages.
- **No public evidence was found** that ties a specific free-tier change in a data or alert product (Visualping, Crunchbase, Shovels) to a measured change in conversion; the conversion figures are cross-industry benchmarks.
- **Teams Workflows webhook hosts** were not checked against Microsoft's own docs; test a real Workflows URL against the allowlist.
- **"Area" sizes** (towns per area, sq mi) are estimates from background knowledge; compute them from Census TIGER county-subdivision adjacency before launch.
- **No user interviews.** Whether residents prefer iCal, a printable sheet or Discord, and how many professionals would hand-build multiple free watchlists, are untested.
