# Moats and threats for an AI-run local-government agenda monitor

*Research run 2026-10-12 for the product currently named 351 Watch (being renamed; https://351watch.vercel.app). It builds on `Product strategy/where_we_win.md`, `Expansion/cheap_township_coverage.md` and `Meeting monitor deep dive/durability_and_acquirers.md`, and does not repeat their competitor matrix. New this run: about 30 searches and fetches. No accounts were created and nothing behind a login was read.*

**Labels**
- **verified**: read this session on the primary page, or verified in an earlier note (named).
- **secondary**: a search-result summary, aggregator, trade press, or an earlier note's secondary item.
- **estimate**: my inference, judgment or arithmetic.

---

## Ranked edges we can build

The ranking uses how hard each edge is for a funded rival or a DIY AI agent to copy within 12 months, weighted by value to paying buyers (developers, counsel, data-center site selectors). All rankings are **estimates** built on the findings in Q1–Q6.

| # | Edge | What it takes | How long | Defensibility | Why it holds or fails |
|---|---|---|---|---|---|
| 1 | **Dated pre-meeting archive: first-seen time, every agenda version, and lifecycle to outcome** (agenda → hearing → continuance → vote → AG or appeal) | Keep the daily crawl running. Store raw files and content hashes per version, which the current design may not do. Link each item to its later minutes or decision | Starts the day snapshots are frozen; worth something after 6 months, strong after 18–24 | **High, and it rises every month.** Nobody can go back and collect what a town posted on a past date, or when it posted it. An entrant with more money still starts at zero | Acquirers say they are buying history (Clio–vLex for $1B; InstaTrac's "three decades") (verified, earlier note). LocalGovIndex already says "Agendas schedule; minutes decide" and tracks outcomes (verified), so others are building the same thing. Starting late is the main risk |
| 2 | **Published coverage registry with measured lead time**: every body read, last fetch, posted date vs first-seen date, and misses, at town and township grain | MA: the 64 bot-blocked towns (1.10M residents). RI: the SOS portal covers all 39. Township states: county-review routing (PA Act 247, OH 519.12, MI MZEA, WI/MN county zoning). Keep the registry public and current | MA complete plus RI: 2–4 months. PA/OH/MI county routing: 2–4 weeks per state for the first 2,200–3,500 townships (estimate, earlier note) | **Medium-high.** Collection work is the moat that held for CoStar (1,500+ researchers, secondary), Shovels (Project Storm calls offline jurisdictions) and Heatmap (calls 3,100+ counties) (verified, earlier note). AI makes adapters cheaper. It does not make permissions, blocked hosts or the long tail of scanned PDFs cheaper | National rivals claim scale ("9,300+ jurisdictions", "3,000+ bodies", "every authority in the US") but publish no per-body list or lead-time proof (verified/secondary). A public, checkable list does what their marketing claims cannot |
| 3 | **Permissioned and statutory access**: Cloudflare Verified Bot (Web Bot Auth), clerk and vendor allow-lists, Legistar tokens, notice-by-request rights (VA §2.2-3707(F), MI 15.266, IN 5-14-1.5-5 by **Dec 31, 2026**, WI 19.84, MN 13D.04, OH 121.22(F)), and press-association licences | Bot approval; one signed letter per body; a mail-in pipeline (Cloudflare Email Routing); legal view on "news media" status | 1–3 months for the first wave; Indiana's annual deadline is Dec 31 | **Medium.** None of it is exclusive, since anyone may ask. But it compounds, and it gets more valuable because the web is closing to unverified AI agents (Cloudflare has blocked AI crawlers by default since July 2025, secondary) | General AI agents and quick clones are the actors most likely to get blocked. A named, verified, polite bot with clerks' consent is a status that takes months to earn |
| 4 | **Answer layers: structured outcomes with exceptions.** The MA AG bylaw ledger (131 decisions), county-review recommendations, moratorium lifecycle and expiry, and data-center HCA status | Legal-grade classification, a published method, an exceptions list, a "cite this" box, and a correction log | Each layer takes 1–3 months. The AG ledger exists | **Medium-high in MA, medium elsewhere.** The AG layer is MA-only. Competitors are converging on outcome fields: Shovels statuses, SitePath votes, LocalGovIndex's "116 places won limits" (verified) | Being correct and citable is what keeps lawyers and journalists. Rivals publish tallies, not decision-level reasoning with exceptions |
| 5 | **Entity resolution: LLC → parent developer → consultant**, using the MassDEP payor field, SMART/CPS lists and state corporation records, with company pages and "watch a company" | Matching pipeline, human-checked seed list, public company pages | 1–2 months for MA | **Medium.** Shovels and Reonomy-style products show buyers pay for linked entities (verified/secondary). User and clerk corrections improve the matches over time | Gets stronger when combined with #1: an LLC's history across towns cannot be backfilled |
| 6 | **Free public item pages plus free full-text search** (town × topic, item permalinks, cite-this, CC BY CSV) | Programmatic pages, schema markup, a stable URL policy, attribution terms | 1–2 months to ship; 6–12 months to rank | **Low-medium.** This is distribution, not a moat on its own. Zillow gets about 80% of its traffic from organic or direct visits (secondary), but SEO alone did not keep Opendoor out (secondary). LocalGovIndex, Citizen Portal and Hamlet compete for the same searches. AI answer engines reduce click-through | Pages earn links when journalists and lawyers cite them. That turns #4 into durable referring domains |
| 7 | **Cost structure: AI-run, near-zero staff, near-zero marginal cost**, which allows a generous free tier and published self-serve prices | Keep unit costs low (feeds over fetches, cached OCR); move off Vercel Hobby before charging | Already true | **Medium against funded rivals, low against DIY.** Funded rivals have 16–48 staff and sell by demo (GatherGov 16, secondary; Paces 48, verified earlier). They can cut prices but cannot easily cut costs. A DIY agent has the same cost structure, so this does not protect against it | Lets us give away what Heatmap, Spark and Hamlet charge for, and charge for what they do not have (#1–#5) |
| 8 | **Neighbour-town and abutter alerts, and county-reveals-township signals** | Adjacency graph; county-to-township name extractor | Weeks | **Low on its own** (easy to copy) | Worth building because it raises lead time, which feeds #2's measured proof |

**What is not an edge** (estimate): AI summaries, meeting transcripts, keyword alerts and "pre-meeting" as a claim. Granicus and CivicPlus now ship AI Q&A and full-text search for their own customers' meetings (verified). Hamlet, GatherGov, LocalGovIndex and Spark all say they read agendas (verified/secondary).

---

## Ranked threats, with early-warning signs and our response

| # | Threat | Likelihood × impact (estimate) | Early-warning signs to watch monthly | Our response |
|---|---|---|---|---|
| 1 | **Funded national aggregators reach town grain in our states and topics.** LocalGovIndex (data-center tracker over 2,841 local governments, refreshed daily, verified); Hamlet (3,000+ bodies, about $7.5–10M raised); GatherGov (9,300+ jurisdictions, 16 staff); Spark (YC; "every authority in the US"; customers include NextEra and Alphabet's Intersect) | **High × high** | LocalGovIndex or Hamlet pages for MA towns or PA/OH/MI townships; Hamlet's MA count rising above 81; Spark or Heatmap marketing "township agenda alerts"; Shovels Decisions adding New England; any rival publishing a coverage list or lead-time numbers | Compete on what they do not publish: a per-body coverage list, measured lead time, MA answer layers, entity links. Put a **data licence page** up so they buy rather than build (Cleanview's API add-on is $5k/yr, verified earlier) |
| 2 | **General AI agents make DIY monitoring cheap.** A developer's analyst sets up a scheduled agent over 50 town sites | **High × medium** | Buyers say "we built it in-house"; agent-browsing products advertise scheduled page monitoring; churn among small teams | Be the source agents call: an API and **MCP endpoint**, priced per query or flat. Sell what an agent cannot produce: history (#1), permissioned access (#3), checked outcomes (#4), and a coverage guarantee. Note that unverified agents are increasingly blocked (Cloudflare default, secondary) |
| 3 | **Agenda platforms add resident-facing AI and cross-town alerts, or close access.** Granicus: "GXA for Public Meetings" Q&A plus full-text portal search (available, verified) and agenda agents (Aug 2026, secondary); govDelivery reaches "120 million" (secondary). CivicPlus: AI Editing Assistant (Jan 2026, verified); CivicPlus Agent connected to Municode and Agenda (Sept 2026, secondary) | **Medium × high** (low today for cross-town topic alerts, high if one ships) | A Granicus or CivicPlus announcement of **cross-agency** search, a topic "network" or a data API; robots or terms tightening on `*.granicus.com`, `civicplus.com`, `municode`; towns migrating from open CivicPlus to closed BoardDocs or Diligent Community; a rise in our per-host fetch failures | Both vendors sell to governments and their products are scoped to a single customer (verified on their pages). Position as complementary: link back to their portals, send them traffic, and ask for allow-listing. Diversify inputs (RSS, county reviews, push email, notice-by-request) so no one vendor can switch us off |
| 4 | **The web closes to bots** (Cloudflare default AI blocking since Jul 2025; a reported Sept 15, 2026 default for mixed-purpose crawlers; Akamai; vendor `Disallow: /`) | **Medium-high × medium** | Monthly share of bodies failing with 403 or a challenge; Cloudflare policy posts; Verified Bot application status | Finish Web Bot Auth and get Verified Bot status. File notice-by-request letters. Expand email-push intake. Publish a bot-info page with an operator contact |
| 5 | **Boston Globe / InstaTrac builds a paid MA municipal-intelligence product** (bought Jul 2026; 6 staff, 380+ orgs; verified earlier) | **Medium × high in MA** | MuniTrac marketing to non-municipal buyers; Globe "local data" product launches; job posts for land-use or data roles | Speed to complete MA coverage, the AG and lifecycle ledgers, and law-firm citations. Treat the Globe as the likeliest acquirer as well as a rival |
| 6 | **Legal and terms claims.** Contract claims from vendor or site terms (hiQ lost on breach of LinkedIn's user agreement in 2022, secondary); anti-circumvention claims (Reddit v. SerpApi pending); copyright in third-party content inside packets (consultant studies, plans, photos) | **Low-medium × high** | Cease-and-desist letters; vendor terms adding "no automated access" for public pages; takedown requests from consultants | No accounts, no logins, no challenge-solving, robots honoured (already policy). Show snippets and link to the official copy instead of rehosting whole packets. Run a takedown and correction desk. Get a short counsel memo on terms and "news media" status |
| 7 | **AI answer engines take the search traffic** (people ask an AI assistant instead of clicking our town pages) | **Medium × medium** | Falling click-through on stable rankings; AI assistants quoting rivals | Make pages the cited source (structured data, permalinks, cite-this, CC BY with attribution). License the feed to answer engines and agents |
| 8 | **Platform and operator concentration**: Vercel Hobby is non-commercial; one owner; dependence on one AI vendor | **Medium × medium** | Billing switch-on; vendor terms changes | Move hosting before charging (already flagged, verified earlier). Keep the crawler model-agnostic |

---

## The three moves that matter most in the next 90 days (to about Jan 10, 2027)

1. **Start the history clock and publish the proof.**
   - Freeze a content-hashed snapshot of every agenda version, starting now, with its first-seen time.
   - Publish the coverage registry: every body read, last fetch, posted-vs-first-seen lead time, and failures.
   - Close the MA gaps (the 64 blocked towns) and add RI through the SOS portal, so "every municipality" is literally true in two states.
   - Why first: #1 and #2 are the only edges that money cannot buy later, and LocalGovIndex already tracks agenda-to-minutes outcomes nationally (verified).
2. **Lock in permissioned access before the year-end deadlines.**
   - Finish Cloudflare Verified Bot.
   - File Indiana media notice requests **by Dec 31, 2026**, and Virginia §2.2-3707(F) requests to blocked or closed counties.
   - Wire the PA, OH and MI county planning-commission agendas that reveal township items.
   - Send one allow-list request each to Granicus and Diligent, through client towns.
   - Get a counsel memo on vendor terms, packet copyright and "news media" status.
   - Why: access is closing to unverified bots (secondary), and each permission compounds.
3. **Ship the citable answer layer and the licence/API front door together.**
   - AG ledger, moratorium lifecycle and LLC → parent company pages, each with a permalink, cite-this and a correction log.
   - A public data-licence page with prices, plus an API and MCP endpoint.
   - Why: it makes funded rivals and AI agents customers rather than rebuilders. It earns journalist and law-firm citations that keep the pages ranking. And it is where the AI-run cost structure (#7) beats demo-led rivals.

---

## Q1. Threats from incumbent agenda platforms (Granicus, CivicPlus, Diligent/BoardDocs, PrimeGov, Municode)

### Takeaway
Granicus and CivicPlus shipped AI meeting features in 2026, but all of it is scoped to one customer government: resident Q&A, portal full-text search and clerk drafting assistants. No vendor has announced cross-town topic alerts or a third-party data program. The risk is less that they become a competitor and more that they control access, through robots rules, closed portals and contract terms.

### Cited Findings
- **Granicus, "2026 Mid-year Innovation update":** "GXA for Public Meetings & Government Transparency" (status Available) lets residents ask plain-language questions about agendas, minutes and decisions; "New integrations with agenda solutions make public meetings easier to understand and navigate." The same page lists "Public portal search & accessibility" (Available: "full-text search" of public meeting content), self-managed captioning with "searchable transcripts" (Available), and an accessible PDF viewer and eComment rebuild (Preview). For govDelivery it lists subscriber verification and a "Contact data platform" (Preview) that builds "unified audience profiles beyond existing subscriber databases". It also lists an "Expanded permit API". No cross-jurisdiction meeting search and no third-party data access is described. — [granicus.com/innovation](https://granicus.com/innovation/) (verified)
- **Granicus, Aug 21, 2026 release:** agents for "Agenda and Meeting Management… preparation, routing, coordination, and follow-up while preserving required clerk, legal, and departmental" oversight, developed with customers (not yet generally available). — [Granicus news](https://granicus.com/news-press/), [GXA expansion release](https://granicus.com/press-release/granicus-expands-gxa-as-adoption-accelerates-across-governments-driven-by-proven-outcomes/) (secondary, search summary)
- **Granicus, Jan 2026:** GXA and workflow agents in preview. — [Granicus semiannual update](https://granicus.com/blog/granicus-january-2026-semiannual-update-ai-agents-and-federal-cloud-solutions/) (secondary)
- **Granicus acquisitions:** a search found no Granicus acquisition in 2025–2026 (negative result). — [CB Insights listing](https://www.cbinsights.com/investor/granicus-group) (secondary). Its agenda footprint came from earlier deals: Legistar/Daystar (2011), Novusolutions (2017–18) and iQM2 (2018). — [GovTech](https://www.govtech.com/biz/granicus-acquires-agenda-tech-company-novusolutions.html) (verified, earlier note)
- **Granicus govDelivery reach:** "120 million people every day" (vendor claim). — [Kansas admin page](https://admin.ks.gov/offices/systems-management/it-support/applications/govdelivery) (secondary, earlier note)
- **CivicPlus, Jan 29, 2026:** six "CivicPlus Intelligence" releases. The only meeting feature is the "AI Editing Assistant" in Agenda and Meeting Management for "drafting, polishing and formatting agenda items and minutes in real time". The article mentions no cross-jurisdiction search, resident topic alerts or third-party API. — [GovTech](https://www.govtech.com/biz/civicplus-new-ai-tools-work-for-meetings-crm-websites) (verified)
- **CivicPlus Agent, Sept 30, 2026:** connects natively with CivicPlus Municipal Websites, **Municode** Codification, Agenda and Meeting Management, and SeeClickFix. — [GlobeNewswire](https://www.globenewswire.com/news-release/2026/09/30/3371958/0/en/civicplus-agent-adoption-grows-as-local-governments-embrace-ai-powered-self-service.html) (secondary; returned 403 to our fetch)
- **Diligent:** positions Diligent Community as "the next generation of BoardDocs"; public-facing "context-sensitive search". AI marketing targets directors and general counsel, not residents. — [Diligent BoardDocs page](https://www.diligent.com/lp/boarddocs) (secondary)
- **No PrimeGov AI or resident-alert news** was found (negative search). Earlier notes group PrimeGov with Granicus-hosted, robots-closed portals (`olmstedcounty.primegov.com` robots `Disallow: /`). — [robots](https://olmstedcounty.primegov.com/robots.txt) (verified, earlier note)
- **No data-partner programs:** Granicus's partner page lists resellers, integrators and AWS, with no data-access or allow-list program. APIs need a customer contract (third-party scorecard). — [Granicus partners](https://granicus.com/partners/) (verified, earlier note); [Supergood report card](https://supergood.ai/api-report-card/granicus) (secondary)
- **Robots on vendor hosts:** `legistar*.granicus.com` disallows all but Googlebot, Slurp and msnbot. The Legistar Web API host is open. — [legistar2 robots](https://legistar2.granicus.com/robots.txt) (verified, earlier note)
- **Contract terms:** Granicus's US subscription agreement grants the product "solely for its internal use" and bars reverse engineering and disruption. It governs customers, not public visitors, and does not mention scraping. — [Granicus subscription agreement (May 2022)](https://granicus.com/wp-content/uploads/2023/05/subscription-agreement_us-master_versionmay-2022.pdf) (secondary). No Granicus public-site terms banning automated reading of agendas were found (negative).
- **The free vendor baseline:** CivicPlus "Notify Me" emails or texts per board when an agenda posts, with no keyword filter. — [example](https://pa-southfayette.civicplus.com/notifyme) (verified, earlier note)

### Inferences
- The vendors' incentive is to sell each government a better portal, not to sell residents or developers a cross-town feed. A cross-customer product would need data-sharing consent in each customer contract. That makes a near-term Granicus or CivicPlus "topic alerts across all towns" launch **unlikely within 12 months** (estimate).
- The **most plausible incumbent move** is govDelivery or CivicPlus Notify Me adding AI keyword filtering per town. That would weaken our free resident tier in towns that adopt it. It would not touch multi-town, history, entity or outcome products (estimate).
- The **bigger incumbent risk is access.** Town migrations to robots-closed portals (BoardDocs to Diligent Community, PrimeGov, iQM2) remove readable sources faster than any feature launch (estimate). Watch the fetch-failure rate.
- Vendor AI Q&A and portal search train residents to expect searchable meetings, which helps the category (estimate).

### Gaps
- Granicus's and CivicPlus's public-site terms of use were not read in full. Neither restriction nor permission on automated reading of public agendas is confirmed.
- PrimeGov's ownership and 2025–26 roadmap were not confirmed this run.
- Whether the "Contact data platform" lets govDelivery recommend topics across agencies is unknown.

---

## Q2. Threats from AI-first startups and general AI agents

### Takeaway
Anyone can now build a single-town monitor with an AI agent in a day. What they cannot buy is: (a) a dated archive of what was posted and when; (b) access to the blocked and closed long tail, which now requires verified-bot status, permission or statutory notice; (c) checked outcomes and entity links; and (d) distribution. The AI-native startups already in this market are well funded and claim national scale, but none publishes per-body coverage or lead time.

### Cited Findings
- **LocalGovIndex** data-center tracker: "2,841" local governments in 50 states, "5,178" development-related agenda items, "116" places that won limits. "Last refreshed October 12, 2026". It treats agendas as scheduling and minutes as decisions ("Agendas schedule; minutes decide"), and infers 11 of 148 outcomes from clerk language. No MA count is shown. — [LocalGovIndex data centers](https://localgovindex.com/issues/data-centers) (verified)
- **LocalGovIndex access terms:** its robots.txt refuses all unnamed bots; "AI USE REQUIRES A LICENSE"; "the extracted record is itself a licensable product." Professional plan $399/mo. — [robots.txt](https://localgovindex.com/robots.txt) (verified, earlier note)
- **Spark data-center product:** YC launch about one month ago (around Sept 2026), "Stakeholder Intelligence for Data Center Permitting": "See who decides your permit, and how they'll vote." Claims it "mapped and tracked every jurisdiction, project, and land use regulation in the country". Meeting records for "every authority in the US", naming county boards, township councils and zoning authorities. Scores every county. Customers named: Alphabet (Intersect), NextEra, DE Shaw Renewables, Nodiac, with "over 200GW of pipeline". — [YC launch](https://www.ycombinator.com/launches/TVc-spark-ai-stakeholder-intelligence-for-data-center-permitting) (verified)
- **Spark's numbers:** it cites that 42% of gigawatt-scale data-center projects announced in 2025 hit a local moratorium, suspension, challenge or denial. — same page (verified; it is Spark's own figure)
- **Cost of collection at scale, as shown by others:**
  - Heatmap Pro is "updated daily using local news coverage… and regular phone calls to all 3,100+ U.S. counties" (verified, earlier note: [heatmap.news/pro](https://heatmap.news/pro)).
  - Shovels' "Project Storm" phones and files requests with "approximately 10,000" offline jurisdictions (verified, earlier note: [Shovels ReZone post](https://www.shovels.ai/blog/shovels-acquires-rezone/)).
- **The web is closing to unverified AI crawlers.** Cloudflare has blocked AI bots by default on new domains since July 1, 2025, and launched "Pay Per Crawl" (HTTP 402). — [MIT Technology Review](https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/) (secondary). A further default from Sept 15, 2026 blocks mixed search/training/agent crawlers on ad pages and sorts crawlers by purpose. — [Massive blog](https://www.joinmassive.com/blog/the-closing-web-ai-crawler-blocking-and-agent-access) (secondary, single source)
- **Cloudflare Verified Bots:** "historically, Verified bots have been excluded in default bot configurations across all plans." — [Cloudflare docs](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/) (verified, earlier note)
- **Free baselines AI agents compete with:** Google Custom Search JSON API is closed to new customers and ends Jan 1, 2027. Brave's base terms forbid storing results. — (verified, earlier note: [Google](https://developers.google.com/custom-search/v1/overview), [Brave terms](https://api-dashboard.search.brave.com/terms-of-service))

### Inferences
- **What stops a DIY agent** (estimate, in order):
  1. **History.** It starts today; we started earlier.
  2. **Access.** Unverified agents increasingly meet Cloudflare and Akamai walls and vendor robots `Disallow`. Respecting them leaves gaps; ignoring them creates legal and reputational risk (see Q5).
  3. **Coverage operations.** Discovering every body in every town, re-finding moved URLs, and OCR on scanned packets is ongoing work, not a one-off build.
  4. **Accuracy.** False positives, such as cross-references read as moratoria, cost a lawyer's trust. Our own spot check found 38 of 40 data-center hits genuine (verified, earlier note).
  5. **Distribution.** Buyers want a trusted, citable source, not a homemade feed.
- **For funded AI-first startups,** the barrier is focus, not capability. LocalGovIndex, Spark and GatherGov already have national pipelines. Their gaps are town-grain New England, Town Meeting warrants, state review layers, and published proof of coverage (estimate).
- **Hidden upside:** the more agents there are, the more value in being the **licensed, agent-callable source**. dcmap.us already advertises an "Agent API" (verified, earlier note), and CivicIQ sells a public-meetings MCP connector (secondary, earlier note).

### Gaps
- No public data on how many developers run DIY agent monitors.
- LocalGovIndex's Massachusetts and township depth was not measured; its data-center page shows no state breakdown.
- Spark's agenda (pre-meeting) coverage is not stated on its launch page.

---

## Q3. Competitors' funding and momentum

### Takeaway
The best-funded rivals (Spark, Hamlet, Paces, Shovels) are VC-backed with 10–50 staff and sell mainly by demo. LocalGovIndex and GatherGov are smaller but ship fast at national scale. Cleanview and Heatmap are lean, media-led businesses. Momentum in 2026 is toward data-center siting: Spark's launch, LocalGovIndex's tracker, and Shovels' "moratoriums routine" post.

### Cited Findings
| Company | Funding (label) | Headcount (label) | 2025–26 momentum signals (label) |
|---|---|---|---|
| **Hamlet** (myhamlet.com) | About $10M (Slow, Crosslink, Banana, Kapor) — [TechCrunch](https://techcrunch.com/?p=3073247) (verified, earlier note). A PitchBook profile that may be the same company lists a $5M seed (Dec 2023), $7.5M total, and investors including Crosslink and Kapor — [PitchBook](https://pitchbook.com/profiles/company/529032-97) (secondary; match unconfirmed). No 2026 round found | About 8 (secondary, earlier note) | Feb 2026: "3,000+" bodies, adding "dozens of agencies each week", daily refresh planned, keyword alerts — [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/) (verified, earlier note). Lists 81 of 351 MA municipalities (verified, earlier note). About 20 high-end customers (secondary) |
| **LocalGovIndex** | Not found | Not found | Data-center tracker over 2,841 local governments, refreshed Oct 12, 2026 (verified, [page](https://localgovindex.com/issues/data-centers)). Flock Safety tracker over 1,809 cities and counties (secondary, [page](https://localgovindex.com/issues/flock-safety)). Self-serve pricing up to $399/mo (verified, earlier note) |
| **Citizen Portal** | StartEngine Reg CF about $1.37–1.4M from about 1,900 investors at an $8M valuation, closed Aug 2024 (secondary, earlier note `durability_and_acquirers.md`) | 3 employees in FY2023; FY2023 revenue $321.9K (secondary, same) | AI-written civic articles; Journalist Pro $49/mo; terms bar competitive use (verified/secondary, earlier notes) |
| **GatherGov** (Turl Street Group) | "Seed-stage" per PitchBook; amount not shown — [PitchBook](https://pitchbook.com/profiles/company/741447-46) (secondary) | 16 (secondary, PitchBook) | "9300+ jurisdictions… 735K+ agendas & minutes" — [GatherGov data](https://gathergov.com/data) (verified, earlier note). The About page says 6,200+ cities and towns (secondary, [about](https://gathergov.com/about-us)). Focus on commercial real estate — [BestCRE review](https://bestcre.com/gathergov-review-cre-ai/) (secondary). Has an API |
| **Heatmap** (News + Pro) | $4M Series A, Mar 2023 (Autumn Road; $11.5M post-money) — [Axios](https://www.axios.com/2023/03/07/climate-news-startup-heatmap-the-week-alum-funding) (secondary). $1M Series A-II, Aug 2025; about $5M total — [CB Insights](https://www.cbinsights.com/company/heatmap-news/financials) (secondary) | 10+ reporters; 2.6M readers; 140K+ newsletter subscribers (verified, earlier note) | Pro calls all 3,100+ counties; county and ZIP scores (verified, earlier note). No 2026 Pro launch found |
| **Paces** | $11M Series A, Jul 2024 (Navitas) (verified, earlier note) | 48 (verified, earlier note) | Hiring for enterprise AE, transmission and environmental roles. No 2025–26 round found (earlier note) |
| **Spark** (sparkhq.ai, YC W24) | Conflicting figures: $26.5M over 4 rounds — [StartupIntros](https://startupintros.com/orgs/spark); $500K — [PitchBook](https://pitchbook.com/profiles/company/590821-93); pre-seed with YC lead — [Crunchbase](https://www.crunchbase.com/organization/spark-ff99) (all secondary; treat $26.5M as unconfirmed) | Not stated | New data-center "Stakeholder Intelligence" launch about Sept 2026, with named customers Alphabet/Intersect, NextEra, DE Shaw Renewables (verified, [YC launch](https://www.ycombinator.com/launches/TVc-spark-ai-stakeholder-intelligence-for-data-center-permitting)) |
| **Cleanview** | No outside funding found; describes itself as a small, bootstrapped Colorado team — [Cleanview about](https://cleanview.co/about) (secondary, search summary) | Small (secondary) | Founded Apr 2024 (Crunchbase, secondary). Tracks "10,000+" clean-energy projects — [MCJ podcast](https://mcj.vc/inevitable-podcast/michael-thomas-cleanview) (secondary). Data-center tracker; published prices of $9k/yr plus $5k API (verified, earlier note). The founder's newsletter (Distilled) feeds the funnel (secondary) |
| *Reference: Shovels* | $5M seed, Jun 2025 (Base10) (verified, earlier note) | 6 → 11 (verified, earlier note) | Bought ReZone Jan 2026; Decisions grew from 20K to about 200K across 600+ cities; post "Data Center Moratoriums Went From Rare to Routine" (verified, earlier note: [Shovels](https://www.shovels.ai/blog/decisions-api-launch/)) |

### Inferences
- **The dangerous combination** is Spark's named enterprise customers plus LocalGovIndex's daily national data-center tracker. Between them they cover the data-center buyer that `where_we_win.md` offer 3 targets. Offer 3 should lean on **licensing to them**, plus MA/New England depth they lack, rather than head-on sales (estimate).
- **Hamlet** is the likeliest funded entrant into all 351 MA towns, but its video-first input misses boards without recordings (estimate, earlier note).
- **Cleanview proves** a lean, media-led, published-price data business can sell $9k+/yr contracts without VC (secondary/estimate). That is the closest model to ours.

### Gaps
- No funding or headcount found for LocalGovIndex. Spark's total raised is unresolved. GatherGov's amount is not shown.
- No revenue figures for any rival except Citizen Portal FY2023 (secondary).

---

## Q4. Moats that held for similar data businesses

### Takeaway
The moats that held were **collection labour that compounds into proprietary history** (CoStar, Shovels, InstaTrac), **entity linking** (Shovels, Reonomy), and **distribution through public pages** (Zillow, BuildZoom), but only when tied to a paid product. Brand trust with journalists alone did not pay the bills (OpenSecrets). Exclusive access was rarely the moat; persistent, permissioned collection was.

### Cited Findings
- **CoStar:** more than 1,500 researchers verify property details; the core network runs at 47% margins (secondary, [Motley Fool, Feb 2026](https://www.fool.com/investing/2026/02/19/costars-core-network-runs-at-47-margins-is-homesco/)). A competitor "can't just wake up one day and decide to replicate 37 years of proprietary data collection". CoStar now adds satellite imagery, automated feeds and machine learning (secondary, [Investor's Podcast](https://www.theinvestorspodcast.com/intrinsic-value/costar-csgp/)).
- **Reonomy:** Altus Group agreed to buy it for US$201.5M in Nov 2021 to strengthen commercial real-estate data and analytics. No later sale or impairment was found (secondary, [CRETech](https://cretech.com/news/page/214); negative search).
- **Shovels:** "Project Storm" uses phone calls and formal requests for about 10,000 offline jurisdictions. Its decision schema links applicant, owner, developer, contractor and property. Revenue "tripled" after the seed round (verified, earlier note: [Shovels](https://www.shovels.ai/blog/shovels-acquires-rezone/)).
- **BuildZoom:** gathered "125 million building permits" and matched them with contractors. Earns commission when a homeowner hires through the site (secondary, [Santa Barbara Independent, 2016](https://www.independent.com/2016/10/06/buildzoom-connects-you-contractors/)). Early coverage was about 10% of the US market. Beta traffic reached about 500K uniques a month (secondary, [TechCrunch 2013](https://techcrunch.com/2013/03/14/buildzoom-connects-homeowners-with-contractors-for-remodeling-projects-doesnt-charge-for-access-or-leads/)). Later "2.5M monthly visitors" claims are unreliable (secondary, conflicting).
- **Zillow:** about 80% of traffic from organic or direct sources (secondary, [William Blair](https://www.williamblair.com/News/Zillow-Group-Inc-Initiation)). About 44% of portal traffic in 2023 vs Realtor.com 19% (secondary, [Real Estate News](https://www.realestatenews.com/2023/03/23/zillow-dominates-the-portals-but-homes-com-gains-ground)). SEO strength did not stop Opendoor from competing (secondary, [Growth Memo](https://www.growth-memo.com/p/when-seo-is-not-enough-to-win)).
- **OpenSecrets:** laid off about a third of its staff in late 2024, much of it research. 2023 revenue was $2.5M against $4.3M expenses (secondary, [Wikipedia](https://en.wikipedia.org/wiki/OpenSecrets); [The Bulwark](https://www.thebulwark.com/p/open-government-nonprofits-are-dying)).
- **Acquirers name history as the asset:** Clio bought vLex for $1B for its "1 billion+" document corpus (verified, earlier note: [Clio](https://www.clio.com/about/press/clio-signs-definitive-agreement-to-acquire-vlex/)). Boston Globe Media bought InstaTrac (founded 1994; 6 staff; 380+ orgs) in Jul 2026 (verified, earlier note: [Boston Globe](https://www.bostonglobe.com/2026/07/16/business/boston-globe-media-acquires-instatrac/)).
- **Breadth without depth churned:** FiscalNote's net revenue retention fell below 100%, and it sold units in 2024–25 (verified, earlier note `durability_and_acquirers.md`).

### Inferences
Which moats actually held, and how they map to us (estimate):

| Moat type | Held? | Evidence | Our version |
|---|---|---|---|
| Proprietary history built by ongoing collection | **Yes, strongest** | CoStar, InstaTrac, vLex, Shovels | Dated pre-meeting archive (edge #1) |
| Entity resolution | **Yes, as a paid differentiator** | Shovels, Reonomy (US$201.5M) | LLC → parent (edge #5) |
| Data effects from user corrections | **Plausible, unproven** in this category | No quantified case found | Correction log (edges #4–5) |
| SEO and public pages | **Yes for distribution, not alone** | Zillow ~80% organic/direct; BuildZoom pages tied to commission; Opendoor got in anyway | Item pages (edge #6) |
| Brand trust with journalists | **Necessary, not sufficient** | OpenSecrets cuts despite trust | Free newsroom access in exchange for citations, with a paid B2B product behind it |
| Exclusive or permissioned access | **Rarely exclusive.** It works as accumulated permissions, not monopolies | Shovels' formal requests; CoStar calls | Verified Bot, statutory notice, allow-lists (edge #3) |
| Regulatory notice rights | **Untested as a moat**, but cheap and durable | State statutes (verified, earlier note) | Notice-by-request letters |

### Gaps
- PitchBook and Ballotpedia: no current readership, correction-loop or moat evidence found this run; the Ballotpedia search returned only 2020 pageview posts.
- No quantified evidence anywhere that user corrections improved coverage or retention in a public-records product.
- CoStar's researcher count comes from secondary investor writeups, not the 10-K.

---

## Q5. Legal and policy risks and protections

### Takeaway
Reading public government pages without logging in, honouring robots and not circumventing bot walls sits on the safest ground current case law offers. The live risks are:
- **contract claims**, if we ever accept terms by creating accounts (hiQ lost on that);
- **anti-circumvention claims**, if we bypass protections (Google v. SerpApi mostly failed in July 2026, but Reddit's suit is pending);
- **copyright in third-party material inside packets**, since the government edicts doctrine covers law made by officials, not consultants' reports;
- **aggregators' own terms** (LocalGovIndex, press associations, Citizen Portal).

Notice laws are moving notices onto government websites, which helps us.

### Cited Findings
- **hiQ v. LinkedIn:** in Nov 2022 the district court held hiQ breached LinkedIn's user agreement through automated scraping and through fake profiles made by hired crowd-workers. A Dec 2022 consent judgment ordered hiQ to pay $500K, stop scraping and destroy the data. The stipulated conclusions are not precedential. — [National Law Review](https://www.natlawreview.com/article/linkedin-s-data-scraping-battle-hiq-labs-ends-proposed-judgment); [ZwillGen](https://www.zwillgen.com/alternative-data/hiq-v-linkedin-wrapped-up-web-scraping-lessons-learned/) (secondary)
- **Meta v. Bright Data (N.D. Cal., Judge Chen, 2024):** Meta's terms govern logged-in users and do not reach logged-out scraping of public data; summary judgment for Bright Data on contract. Meta later dropped the suit and waived appeal, so this is a district-court ruling only. — [Farella Braun + Martel](https://www.fbm.com/post/102kqw7/); [MediaPost](https://www.mediapost.com/publications/article/393996/None) (secondary)
- **Google v. SerpApi (N.D. Cal., Jul 20, 2026):** DMCA anti-circumvention claims over public search results dismissed without leave to amend. Leave to amend for copyrighted Knowledge Panel images. Reddit's separate suit against SerpApi (S.D.N.Y.) is pending. — [Beaumont & Sheridan](https://beaumontandsheridan.com/blog/google-serpapi-dmca-2026-07-28.html); [The Next Web](https://thenextweb.com/news/google-serpapi-dmca-scraping-lawsuit-dismissed) (secondary; sources differ on full vs partial dismissal)
- **Georgia v. Public.Resource.Org (U.S. 2020, 5–4):** under the government edicts doctrine, works produced by legislators in their official duties are not copyrightable, whether or not they have the force of law. — [SCOTUSblog](https://www.scotusblog.com/cases/georgia-v-public-resource-org-inc/) (secondary)
- **Aggregator and press terms:**
  - LocalGovIndex: "AI USE REQUIRES A LICENSE" (verified, earlier note).
  - Seven press-association notice sites limit use to personal, non-commercial and forbid putting notices "in any database" (verified, earlier note: [PNA terms](https://www.publicnoticepa.com/Terms-of-Use.aspx)).
  - Citizen Portal terms bar competitive use (verified, earlier note).
- **Notice-law shifts** (secondary, earlier note `cheap_township_coverage.md` §4):
  - **NJ S-4654:** effective Mar 1, 2026. Entities post legal notices on their own websites, with a statewide directory ([Saiber](https://www.saiber.com/insights/publications/2025-08-06-new-law-modernizes-legal-notice-requirements-in-new-jersey)).
  - **Indiana HEA 1210:** from Jul 1, 2027, units may publish on their own website, with a standard digital form ([FBT Gibbons](https://fbtgibbons.com/indiana-amends-public-records-access-laws-and-public-notice-requirements/)).
  - **Ohio HB 33 (2023):** a narrow municipal website option; township zoning notices stay in newspapers ([PNRC](https://www.pnrc.net/wp-content/uploads/2023/09/PNRC-Analysis.pdf)).
  - **Florida HB 7049 (2022):** a county-designated website can replace the newspaper ([FL Senate](https://flsenate.gov/Committees/billsummaries/2022/html/7049)).
  - **New Hampshire:** town warrants must be on town websites from Oct 18, 2026 (verified, earlier note `where_we_win.md`).
- **Statutory notice rights:** VA §2.2-3707(F) gives any person notice of all meetings, by email. MI 15.266 makes notice free to media. IN 5-14-1.5-5 gives media notice on an annual request due by Dec 31. WI 19.84, MN 13D.04 and OH 121.22(F) are similar. — [Va. Code](https://law.lis.virginia.gov/vacode/title2.2/chapter37/section2.2-3707/) (verified, earlier note)

### Inferences
- **Our posture** (no accounts, robots honoured, no challenge-solving, no proxies) maps to the fact patterns where scrapers won (Bright Data logged-out; SerpApi on public results). It avoids the patterns where they lost (hiQ's accepted terms and fake accounts). Keep it that way. **Never create a site account to read agendas**: signing up for Notify Me or a portal profile may bind us to terms (estimate).
- **Republishing whole packets is the main copyright exposure.** Agendas and ordinances made by officials fit the edicts doctrine. Applicant site plans, engineering studies and photos in packets may be privately copyrighted (estimate). Show excerpts, link to the official copy, and run a takedown process. Facts and dates are not copyrightable (estimate, background).
- **Website-notice laws expand our free inputs.** Every state that moves notices from newspapers to government sites weakens the press associations' licence gate (estimate).
- A short memo from counsel should cover: vendor portal terms, "news media" status for MI, IN and WI, and the packet excerpt policy.

### Gaps
- No court opinion was read in full this run; all case descriptions are secondary.
- Granicus, CivicPlus and Diligent public-site terms were not located.
- No case law found that applies scraping doctrines specifically to municipal or vendor-hosted public meeting portals.

---

## Q6. The flywheel

### Takeaway
Comparable products show that free public pages work as acquisition, provided each page leads to a paid workflow: Zillow's public pages and agents; BuildZoom's permit pages and contractor commission; Heatmap News' readers and Pro; Cleanview's newsletter and paid tracker; Shovels' free credits and paid plans. The correction loop is the least-proven link, but it is cheap, and it builds the relationships with clerks that also unlock access.

### Cited Findings
- **Zillow:** about 80% organic or direct traffic (secondary, [William Blair](https://www.williamblair.com/News/Zillow-Group-Inc-Initiation)). Its broad keyword footprint comes from programmatic pages and user content (secondary, analyst commentary: [gracker.ai](https://gracker.ai/case-studies/zillow)).
- **BuildZoom:** public permit-based contractor pages led to commissions on hires; contractors pay only when hired (secondary, [Independent](https://www.independent.com/2016/10/06/buildzoom-connects-you-contractors/)).
- **Heatmap:** a news audience of 2.6M readers and 140K+ newsletter subscribers sits alongside the demo-sold Pro product (verified, earlier note).
- **Cleanview:** the founder's Distilled newsletter preceded the paid tracker (secondary, [Cleanview about](https://cleanview.co/about); [Substack spotlight](https://substack.com/home/post/p-149507542)).
- **Free tiers in the category:**
  - Shovels: 500 free credits, then $599/$999 a month (verified, earlier note).
  - Hamlet: a free tier, plus free access for journalists (verified, earlier note).
  - dcmap.us: a "Cite this data" page (verified, earlier note).
- **Citations that already happen:** Foley Hoag writes client alerts on each AG moratorium ruling (verified, earlier note: [Foley Hoag](https://foleyhoag.com/news-and-insights/blogs/law-and-the-environment/2026/march/massachusetts-ago-rejects-yet-another-municipal-solar-and-battery-storage-moratorium/)).
- **Counter-example:** OpenSecrets had journalist trust but no paid product, and cut a third of its staff (secondary, [Wikipedia](https://en.wikipedia.org/wiki/OpenSecrets)).

### Inferences
The proposed loop (estimate):
1. A **resident or reporter** finds a town × topic page or item permalink through search, a share in a neighbourhood group, or a news citation.
2. They **watch the town**, free and with no account, by RSS, iCal or a neighbour-town alert. Each watch is a signal of demand by town, which tells us where coverage matters most.
3. A **shared item page** reaches developers' staff, consultants and counsel. Every Slack or Teams alert is a public permalink.
4. **Corrections** from clerks, residents and developers fix dates, outcomes and LLC matches. Each correction is logged publicly, which raises accuracy (edge #4) and builds clerk relationships. Those relationships turn into allow-listing and notice-list access (edge #3).
5. **Professionals pay** for multi-town watchlists, company watch, the history and lifecycle, exports, the API/MCP, and Slack.
6. **Revenue and licence fees pay for coverage operations:** permission letters, county routing, new states. Wider coverage feeds more pages and longer history (edges #1–2).
7. **The link that breaks most often** is step 5: free users who never convert (the OpenSecrets risk). Keep the paywall on workflow and history, never on the facts of a single public item.
8. **Measure the loop:** organic sessions per page; watches per 100 sessions; permalink visits from Slack or Teams referrers; corrections per month and time to fix; referring domains from law firms and newsrooms; trials and paid conversions.

### Gaps
- No product in this category publishes conversion rates from free public pages to paid plans.
- No quantified evidence that correction loops raise retention in civic data products.
- Zillow and BuildZoom traffic figures are analyst or vendor numbers, not audited.
