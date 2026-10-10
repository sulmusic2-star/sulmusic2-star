# Subscription Data/Alert Products from Massachusetts Public Sources (software-only build and operation)

Research date: October 10, 2026. All prices are as reported by the cited source on the date shown. "Verified" means read on a primary or official page (or an official document's text). "Third-party" means a review, directory or competitor blog. Anything labeled inference or estimate is my reasoning, not a sourced fact.

Method notes (observed directly in this session, Oct 10, 2026): direct HTTP fetches of mass.gov pages (Land Court report lists, report PDFs) returned HTTP 403 to both the fetch tool and curl. mass.gov facts below therefore come from search-engine extracts of mass.gov pages, not full-page reads. corp.sec.state.ma.us "ListNewFilings.aspx" returned HTTP 200 with an essentially empty body, which suggests it needs a session or JavaScript. The web-search budget ran out near the end, so a few planned checks (TCPA/CAN-SPAM, MA foreclosure-rescue rules, Warren Group foreclosure volumes, Hamlet's price list) are listed as gaps.

---

## Q1. Local government meeting and agenda monitoring for MA (land use, zoning, clean energy siting): is it proven elsewhere, what does it cost, and is MA poorly covered?

### Takeaway
This is the strongest candidate. Paid meeting-monitoring products exist (Hamlet, OrdinanceWatch, Voterheads, and UK comparables with public prices), and they sell to developers, law firms and associations. MA's data is spread across hundreds of separate town websites, and no statewide aggregator turned up in this research. MA also has a dated demand trigger: from October 1, 2026, towns must offer a 12-month consolidated local permit for small clean-energy and battery-storage projects, while several towns are pursuing battery-storage moratoria in 2026. That makes MA-specific monitoring for solar/BESS developers and land-use attorneys a timely, B2B-priced, fully automatable product.

### Cited Findings
**Comparables and pricing**
- Hamlet (founded 2022, Santa Cruz area) monitors "more than 3,000 city councils, planning commissions and other governing bodies" across the US (announcement dated Feb 18, 2026). It offers free initial searches, a 14-day free trial that unlocks full transcripts and real-time notifications, saved searches and keyword alerts, and weekly data refresh with daily updates "planned". Target users include local governments, real estate developers, data center operators, journalists, residents and nonprofits. The article does not mention Massachusetts or New England. — [PublicCEO, Feb 2026](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/)
- Hamlet's clients include real estate developers and city governments. It runs on a SaaS model with "custom pricing". Enterprise clients get agenda tracking, topic alerts, meeting summaries and video-archive search (for example, mentions of competitors). AI narratives are reviewed by human fact-checkers. Reported funding is about $10M (Slow Ventures, Crosslink, Banana Capital, Kapor Capital). The $5M seed is dated inconsistently (Dec 2023 vs Dec 2025). Third-party and directory sources, unconfirmed. — [Signalbase](https://www.trysignalbase.com/news/funding/hamlet-secures-5m-seed-investment-for-ai-powered-public-meeting-insights); [Dealroom](https://app.dealroom.co/companies/hamlet_2)
- Hamlet's first city deployment (Saratoga, CA, 2023) summarized council agendas, supporting documents and audio/video. — [PublicCEO, Sep 2023](https://www.publicceo.com/2023/09/hamlet-elevates-saratogas-civic-engagement-with-ai-powered-city-council-summaries/)
- Hamlet's pricing page (myhamlet.com/pricing) returned HTTP 429 when fetched. No published price was found.
- OrdinanceWatch sells advance-notice email alerts on pending local council and commission actions, with 128 issue categories, a searchable archive of 15+ years, and lobbyist registration information. Tiers are Standard (10 email subscriptions), Premium (20), Premium+ (unlimited) and a Website Issues Feed. Prices come by quote, with a 30-day free trial. It covers Florida (67 counties, 326 cities) and Georgia only. Named buyers are associations (member alerts) and law firms (Premium+ as a "client retention tool"). Verified on vendor page. — [OrdinanceWatch](https://ordinancewatch.com/)
- Voterheads offers keyword-based alerts for cities, counties and school boards (400+ categories) in all 50 states plus DC. Its meeting data appears on Ballotpedia city/county pages. No price was found. — [GovFresh](https://govfresh.com/signal/voterheads-wants-make-easier-follow-government-council-meetings); [SCRA](https://scra.org/voterheads23/)
- CivicSearch is free. It sends email digests 1–4 times a month on topics local governments discuss, built on LocalView transcripts covering about 545–547 cities. — [civictech.guide](https://civictech.guide/projects/civicsearch); [directory listing](https://directory.civictech.guide/listing/civicsearch)
- Open Council Network (UK) publishes prices: a business product from £50/month with topic watch for council meetings, and an API at £249/month (Starter, up to 30 meetings and 5,000 requests a month) or £549/month (Partner, up to 300 meetings a month, aimed at commercial products). — [Open Council Network API pricing](https://opencouncil.network/api/pricing); [for Business](https://opencouncil.network/about/business)
- Planning Signal (UK) charges £4.99/month or £49/year for planning-application alerts aimed at parish councils. — [Planning Signal](https://www.planningsignal.co.uk/for-parish-councils)
- An Apify "Zoning & Planning Commission Tracker" scrapes US planning commissions via Legistar from $4.00 per 1,000 results. — [Apify](https://apify.com/tristana/zoning-planning-tracker)
- SitePath Intelligence launched in August 2026 as a "county-level permitting intelligence platform" for energy developers. It covers municipal permitting requirements, zoning ordinances, planning commission decisions, moratoriums, setbacks, approval history and community activity. No price was published. — [Utility Dive press release, Aug 7, 2026](https://www.utilitydive.com/press-release/20260807-sitepath-intelligence-launches-county-level-permitting-intelligence-platfor-1/)

**MA demand triggers (clean energy siting)**
- The 2024 Climate Act (signed November 2024) directed DOER to create an optional consolidated local permitting pathway for small clean energy facilities. Municipalities keep jurisdiction over generation under 25 MW, storage under 100 MWh and smaller T&D projects, while larger projects go to the state Energy Facilities Siting Board. Towns have 12 months to decide, and permits are constructively approved if they miss the deadline. 225 CMR 29.00 was promulgated February 27, 2026. Towns may offer the pathway from July 1, 2026 and must offer it by October 1, 2026. DOER draft guidelines were issued January 21, 2026 (finalization unconfirmed). — [ABA, Spring 2026](https://www.americanbar.org/groups/environment_energy_resources/resources/natural-resources-environment/2026-spring/ray-hope-massachusetts-renewables-permitting-reform); [DOER slides](https://www.mass.gov/doc/doer-clean-energy-siting-permitting-public-information-session-presentation-slides/download); [DOER update on siting regs](https://www.mass.gov/doc/update-on-siting-permitting-regulations/download)
- Sutton, MA began accepting consolidated-permit applications October 1, 2026 and is still deciding between its own bylaw and DOER's model regulations. — [Sutton newsflash](https://suttonma.gov/m/newsflash?cat=7)
- 2026 BESS/solar moratorium activity in MA:
  - Lee Planning Board held a hearing on April 27, 2026 on a commercial BESS moratorium to run until November 14, 2026 or until zoning is adopted. — [Lee hearing notice](https://leema.gov/DocumentCenter/View/4860/Planning-Board-Public-Hearing-Bess-Moratorium-Bylaw-Amendment-April-27)
  - Sturbridge Planning Board held a hearing on January 26, 2026 on a temporary moratorium on large standalone BESS. — [Sturbridge](https://www.sturbridge.gov/node/171911)
  - Becket home-rule petition H.5641 (moratorium on large-scale solar and non-residential BESS) was referred to committee August 4, 2026. — [H.5641](https://malegislature.gov/Bills/194/H5641)
  - Worthington H.5294 (solar and BESS moratorium) is in committee. — [H.5294](https://malegislature.gov/Bills/194/H5294)
  - Final town-meeting outcomes were not confirmed.

**How MA towns publish (data access)**
- Open Meeting Law (M.G.L. c. 30A §§18–25): notice must be posted at least 48 hours before a meeting, not counting Saturdays, Sundays or legal holidays. It must include date, time, location and the topics the chair reasonably anticipates. The AG interprets topic specificity strictly. Amendments within 48 hours must record the amendment time. — [AG OML notice checklist (11/06/2024)](https://www.mass.gov/doc/11062024-oml-notice-checklist/download); [AG Public Body Checklist – Notice](https://www.mass.gov:443/files/documents/2017/09/25/Public%20Body%20Checklist%20-%20Notice.pdf)
- Local public bodies file notices with the municipal clerk, who posts them at the municipal building or at an adopted alternative location such as the town website. — [AG Public Body Checklist – Notice](https://www.mass.gov:443/files/documents/2017/09/25/Public%20Body%20Checklist%20-%20Notice.pdf); [AG "new OML meeting notice requirements"](https://www.mass.gov/doc/new-open-meeting-law-meeting-notice-requirements/download)
- Towns run their own alert sign-ups, and no statewide aggregator was found:
  - CivicPlus-style "Notify Me" sign-ups exist in Westford, Middleborough and Middleton, the last with separate Planning Board and ZBA lists that require sign-in. — [Westford](https://www.westfordma.gov/Calendar.aspx?EID=12818); [Middleborough](https://www.middleboroughma.gov/Calendar.aspx?EID=9000); [Middleton Notify Me](https://middletonma.gov/list.aspx)
  - Other towns post agendas as PDFs under a common "/sites/g/files/vyhlif…/f/agendas/" path, for example West Boylston, Hanover, Wayland and Norwell. — [West Boylston PB agenda](https://www.westboylston-ma.gov/sites/g/files/vyhlif1421/f/agendas/march_15_2024_planning_board_agenda_for_posting.pdf); [Hanover](https://www.hanover-ma.gov/sites/g/files/vyhlif12081/f/agendas/planning_board_agenda_8-19-24.pdf); [Wayland](https://www.wayland.ma.us/sites/g/files/vyhlif9231/f/agendas/planning_board_1.23.2024.pdf); [Norwell](https://www.townofnorwell.net/sites/g/files/vyhlif1011/f/agendas/pb_2.15.2024_agenda.pdf)
  - Holbrook handles Planning Board agenda requests by phone or email. — [Holbrook](https://www.holbrookma.gov/print/34)

### Inferences
- **Coverage gap (estimate).** MA has 351 municipalities. At roughly 6–12 relevant bodies each (select board, planning board, ZBA, conservation commission, board of health, town meeting, plus historic and licensing boards), MA alone likely has around 2,000–4,000 public bodies. That is comparable to Hamlet's entire national footprint of 3,000+ bodies, so national tools probably cover only a fraction of MA's small-town boards, especially ZBAs and conservation commissions. This is unverified: Hamlet's MA coverage list was not obtainable.
- **Platform pattern.** The "/sites/g/files/vyhlif…" path looks like a Granicus-hosted Drupal (govAccess) platform, and "Calendar.aspx?EID" / "list.aspx" is CivicPlus CivicEngage. A scraper set built around a few dominant CMS templates plus generic PDF discovery could plausibly cover most towns. This is inferred from URL patterns, and market-share counts were not found.
- **Why MA-specific now.** The consolidated-permit regime (12-month clock, constructive approval, live from Oct 1, 2026) means developers must track hearings, notices and board decisions in every host town in parallel. Moratorium articles at town meeting are a high-value early warning for BESS and solar developers.
- **Buyer segments (inference):**
  - solar/BESS/EV-charging developers and their land agents
  - land-use and permitting attorneys (as subscribers, not operators)
  - residential/commercial developers and 40B developers
  - cell tower and fiber siting firms
  - engineering and environmental consultants (conservation commission Notices of Intent)
  - trade associations
  - local journalists
- **Pricing hypothesis (estimate, not sourced).** Individual or town-pack plans at about $49–$99/month (anchored to Open Council Network's £50/month business tier). Statewide team plans at about $299–$999/month for developers (anchored to Open Council Network's £249–£549 API tiers and quote-based Hamlet and OrdinanceWatch).
- **Automation.** Scheduled crawls of town agenda pages and PDF agendas, OCR where needed, then LLM topic classification (BESS, solar, 40B, cell tower, moratorium, special permit, variance), entity extraction (address, applicant) and email digests. All of this can run without human review. The main ongoing cost is scraper maintenance as town sites change, which a coding agent can handle by detecting breakage and repairing it. Hamlet's use of human fact-checkers suggests accuracy matters. An alert product that links back to the source PDF and avoids paraphrased "facts" reduces that need.
- **Legal (inference).** Agendas and minutes are public records that towns publish to meet the OML. The main risks are terms of service on individual CMS sites and fair crawling (rate limits). No MA-specific prohibition on reusing municipal agendas was found.

### Gaps
- Hamlet's, Voterheads', Quorum Local's and OrdinanceWatch's actual price points (all quote-based or not retrieved).
- Hamlet's MA coverage: which MA towns and bodies are indexed.
- Counts of MA towns by website platform (CivicPlus vs Granicus vs others) and how many post minutes or video (local cable access YouTube).
- Whether citymeetings.nyc, CivicClerk or BoardDocs public portals are used by MA towns (not researched before the search budget ran out).
- Direct evidence of willingness to pay from MA developers or attorneys (forum or Reddit posts) was not found.

---

## Q2. Public bid and procurement alerts (COMMBUYS, Central Register, town bid pages): proven pricing, MA coverage, and room for an MA-specific product?

### Takeaway
Bid alerts are a proven, priced category, but MA is not empty. COMMBUYS is free and already ingested by national aggregators, and BidNet Direct runs a Massachusetts Purchasing Group with free vendor sign-up. The MA-specific opening is narrower. It means parsing the Secretary of the Commonwealth's weekly Central Register (required for all construction contracts of $10,000 or more and for municipal real-property transactions), adding filtering by trade and by sub-bid, and covering the small written-quote solicitations posted only on town websites or ProjectDog. Willingness to pay is likely modest ($25–$50/month per firm, estimate), and differentiation is moderate.

### Cited Findings
**Legal publication rules (verified from the Inspector General's Chapter 30B Manual, July 2026 edition, text extracted from the PDF)**
- Construction services and materials contracts estimated at $10,000 or more must be advertised in the Central Register (M.G.L. c. 9, §20A; 950 CMR 21.00). — [OIG Chapter 30B Manual 2026](https://maoig.gov/wp-content/uploads/Chapter-30B-Manual-2026.pdf)
- Public works projects over $50,000: the IFB must be advertised in the Central Register, a local newspaper and COMMBUYS at least two weeks before the bid deadline. Contract awards are also published in the Central Register. — [OIG Chapter 30B Manual 2026](https://maoig.gov/wp-content/uploads/Chapter-30B-Manual-2026.pdf)
- Chapter 30B procurements over $50,000 ($100,000 for municipal and regional school districts) and surplus sales over $10,000 must be posted to COMMBUYS. Procurements over $100,000 must also appear in the Goods and Services Bulletin. Chapter 30B real property transactions are published in the Central Register, and acquisitions over 2,500 sq ft require a Central Register ad at least 30 days before proposals open. Any public agency can post to COMMBUYS free of charge. — [OIG Chapter 30B Manual 2026](https://maoig.gov/wp-content/uploads/Chapter-30B-Manual-2026.pdf)
- Public works up to $50,000 under c. 30 §39M need no newspaper ad but do require posting. Small construction contracts also have an option to solicit three written responses with advertising in the Central Register and COMMBUYS plus posting on the town website. — [OIG Chapter 30B Manual 2026](https://maoig.gov/wp-content/uploads/Chapter-30B-Manual-2026.pdf)

**The Central Register itself**
- It is a weekly publication of public contracting opportunities, awards and real-property notices under M.G.L. c. 9 §20A. — [Central Register Vol. 45 Issue 26 (06/25/2025)](https://www.mass.gov/doc/central-register-volume-45-issue-26-06-25-2025/download)
- Subscription is $101.50 per year, electronic only, through the Secretary's subscription site (as stated in the June 25, 2025 issue, via search extract). — [Central Register issue](https://www.mass.gov/doc/central-register-volume-45-issue-26-06-25-2025/download); [SOC subscription page](https://www.sec.state.ma.us/PUBLICATIONSUBSCRIPTIONPUBLIC/Subscription/SubscriptionPage.aspx)
- Print editions of the Goods and Services Bulletin and the Central Register were discontinued, and PDFs are free online through the State Library of Massachusetts, with individual weekly issues in the archive. Whether current issues appear there promptly is unconfirmed. — [Lenox Library notice](https://lenoxlib.org/?p=1365); [State Library archive item](https://archives.lib.state.ma.us/entities/journalfile/deded9e9-2d37-449e-ae1f-4b9b1d7f4485)

**COMMBUYS access**
- Public search is free (Contract & Bid Search). No official public API or bulk feed was found. A third-party Firecrawl page describes anonymous access to search, detail pages and attachment URLs. — [mass.gov how-to](https://www.mass.gov/how-to/search-for-procurements-in-commbuys); [Firecrawl provider page](https://www.firecrawl.dev/alexandria/agents/providers/commbuys-com)

**Other MA channels**
- ProjectDog is the bid-document and e-bid platform for many MA towns. Examples: Marblehead (2021–2025 drainage, COA and catch-basin bids), Fairhaven (2024), Dunstable (2025 sub-bids) and Acton (2025, which disclaims documents obtained elsewhere). — [Marblehead legal ad](https://marbleheadma.gov/wp-content/uploads/2025/04/Legal-Ads-IFB-Catch-Basin.pdf); [Acton bid](https://www.acton-ma.gov/bids.aspx?bidID=168); [Dunstable legals](https://grotonherald.com/dunstable-legals?page=3)
- North Andover publishes solicitations on BidNet Direct "in partnership with the Massachusetts Purchasing Group", with free vendor registration. — [North Andover](https://www.northandoverma.gov/node/18)

**Comparable pricing**

| Product | Price | Source and caveat |
|---|---|---|
| BidNet Direct | Free Basic tier; $599/yr one state; $1,199/yr three states; $1,999/yr nationwide | Checked Aug 26, 2026 — [Civic IQ](https://civiciq.com/blog/civic-iq-bidnet-direct-pricing) |
| DemandStar | State Plan $35–$1,299 per year per state | [Jorpex comparison](https://jorpex.com/compare/demandstar-alternatives/); [DemandStar pricing](https://network.demandstar.com/?p=80) |
| BidPrime | Quote-based (Enhanced, Expert, Enterprise tiers; 30-day free trial); regional plan estimated at ~$1,500–$3,000/yr | Third-party — [ColdIQ](https://coldiq.com/tools/bidprime); [Jorpex](https://jorpex.com/compare/demandstar-alternatives/) |
| GovSpend | ~$7,300–$24,500/yr; one median estimate $11,576 | Competitor blogs — [Fed-Spend](https://fed-spend.com/blog/govspend-pricing-2026-cost-alternatives); [Pursuit](https://www.pursuit.us/blog/govwin-alternatives-and-competitors) |
| GovWin IQ | ~$12,000–$42,000/yr, annual contracts | Competitor blogs — [Fed-Spend](https://fed-spend.com/blog/govwin-iq-pricing-2026-deltek-cost-alternatives) |
| HigherGov | $500/yr single user; $2,500/yr up to 10 users | Third-party — [Prospeo](https://prospeo.io/s/deltek-govwin-iq-pricing-reviews-pros-and-cons) |

- BidPulsar.ai has a Massachusetts page showing about 830 "qualified notices" sourced from COMMBUYS, "Massachusetts Market Feeds" (town-level) and SAM.gov. It does not mention the Central Register, ProjectDog or BidNet, and no pricing is shown. — [BidPulsar MA](https://bidpulsar.ai/state/ma)

### Inferences
- National aggregators can ingest COMMBUYS cheaply, so an MA product will not win on "state bids". The defensible MA-specific pieces are the following (inference from the posting rules above):
  - Central Register parsing. Every construction contract of $10,000 or more and every municipal real-property RFP or disposition passes through it. It is a paid, PDF-only weekly that is poorly searchable.
  - Trade-level filtering for MA's filed sub-bid trades. Electricians, plumbers, HVAC and others have to watch c. 149 building projects. The sub-bid trade list was not verified in this research.
  - Surplus municipal land and building disposition alerts for developers.
  - Award and plan-holder tracking, so suppliers can sell to winners.
- **Buyers:** small and mid-size MA contractors and sub-contractors, design and engineering firms, suppliers, and developers (for real-property dispositions).
- **Pricing hypothesis (estimate).** About $25–$50/month or $250–$500/year per firm. This sits under BidNet's $599/year single-state plan, though the free BidNet/COMMBUYS options cap willingness to pay.
- **Automation.** Fully automatable: weekly Central Register PDF parsing, COMMBUYS crawling, town bid-page crawling, LLM classification by trade, NAICS-like category and town, then email. Risks are COMMBUYS bot controls and the terms of the Central Register subscription (resale terms not verified).

### Gaps
- Central Register subscription terms of use: whether commercial redistribution or summarizing of its contents is permitted (not found).
- How quickly the State Library posts current Central Register issues for free.
- How well BidPrime, BidNet and DemandStar actually cover small MA towns' sub-$50K solicitations (no audit or coverage list found).
- MA demand evidence from contractor forums (not found before the search budget ran out).

---

## Q3. Real-estate distress / motivated-seller lists from MA court and public sources: what MA-unique data exists, who sells it, and how risky is it?

### Takeaway
MA has an unusually clean, free and official early-foreclosure signal. The Land Court publishes nightly-updated lists of new Servicemembers (SCRA) cases and Tax Lien cases with case number, filing date, city, street and party names. Mortgage servicers file these before a foreclosure sale. National investor tools sell distress lists at $59–$699/month, and the MA incumbent (The Warren Group) does not publish prices. A weekly MA "SCRA + tax lien + auction notice" list with property enrichment is cheap to build and fully automatable. The key risks are mass.gov bot-blocking, court access rules on reuse, and reputational or regulatory exposure from customers soliciting distressed (sometimes military) homeowners.

### Cited Findings
**MA data sources**
- Land Court "MassCourts reports": three reports listing each new case filed in a rolling 3-month period for Servicemembers, Tax Lien and Miscellaneous case types. Each entry shows case number, filing date, city, street and party names. The reports update nightly and roll monthly. They are static lists, with details available via masscourts.org by docket number or party. — [Land Court MassCourts Reports](https://www.mass.gov/lists/land-court-masscourts-reports); [Tax Lien cases report](https://www.mass.gov/doc/tax-lien-cases/download); [Servicemember cases report](https://www.mass.gov/doc/servicemember-cases/download)
- A Servicemembers case is "brought by a bank or other mortgage holder against a property owner who has defaulted on their mortgage". It is not itself a foreclosure. It determines SCRA protection before foreclosure proceeds. — [Land Court SM FAQ](https://www.mass.gov/info-details/frequently-asked-questions-about-servicemembers-cases-in-the-land-court); [Filing SCRA complaints](https://www.mass.gov/info-details/filing-complaints-under-the-servicemembers-civil-relief-act)
- A 2026 SM report lists January 2026 filings, for example "26 SM 000035, 01/07/2026", with plaintiffs such as servicers and trusts. — [Servicemember cases report](https://www.mass.gov/doc/servicemember-cases/download)
- The Feb–Apr 2026 Tax Lien report shows municipal plaintiffs (Malden, Lawrence, Boston, Revere, Everett) against owners and trusts. Tax lien complaints are brought under G.L. c. 60 §65 to foreclose rights of redemption after the redemption period. — [Tax Lien cases report](https://www.mass.gov/doc/tax-lien-cases/download); [Tax lien complaint form](https://www.mass.gov/doc/tax-lien-complaint/download)
- Land Court Orders of Notice in SCRA cases are also published in newspapers, naming defendant, mortgagee and address. One example is a Lee property with a response date of July 20, 2026. — [Berkshire Eagle notices](https://shoplocal.berkshireeagle.com/places/view/27471/the_commonwealth_of_massachusetts_land_court_department.html)
- Land Court Standing Order 1-26 (adopted Feb 2, 2026, effective Apr 1, 2026) limits which Land Court docket documents are viewable through the eAccess Public Portal. — [Standing Order 1-26](https://www.mass.gov/land-court-rules/land-court-standing-order-1-26-limiting-public-remote-access-to-certain-types-of-electronic-court-records-in-the-land-court-department-of-the-trial-court)
- masspublicnotices.org popular searches include "Foreclosures", "Estate Claims" and "Tax Deeds". — [masspublicnotices.org](https://www.masspublicnotices.org/)

**Market size and comparables**
- BatchData's July 2026 MA report counts 4,216 MA properties entering the pre-foreclosure pipeline in the prior 12 months, 64.1% at the "initial Notice of Default stage". — [BatchData MA pre-foreclosure report](https://reports.batchdata.io/market-reports/preforeclosure/2026-07/state/ma/)
- The Warren Group Foreclosures database covers New England foreclosure petitions, auctions and REOs with property, assessment, sales and financing history. It updates weekly, offers an optional weekly E-Alert and a downloadable sample report, and does not publish pricing. Verified on vendor page. — [Warren Group Foreclosures](https://www.thewarrengroup.com/data-solutions/warren-group-foreclosures/); [NEREJ launch article](https://www.nerej.com/the-warren-group-launches-a-new-way-to-search-foreclosure-info)
- Competitor prices:

| Product | Price | Source and caveat |
|---|---|---|
| PropStream | Essentials $99/mo ($81 annual); Pro $199/mo; Elite $699/mo; seat add-ons $30/mo | Third-party citing official page — [PropStream news, May 15, 2026](https://www.propstream.com/news/how-much-does-propstream-cost); [Jamil Academy](https://www.jamilacademy.com/blog/propstream-vs-batchleads-vs-dealmachine) |
| DealMachine | Starter $99 annual / $119 monthly; Pro $149/$179; Pro Plus $232/$279; mail $0.55–$0.72 per piece | As of July 16, 2026; sources disagree — [Goliath Data](https://goliathdata.com/propstream-vs-dealmachine-an-investor-s-guide-for-2026) |
| PropertyRadar | Essential $59/mo; Complete $99/mo | Third-party — [Capterra](https://www.capterra.com/p/230568/PropertyRadar/) |

### Inferences
- **MA edge (inference).** Because MA foreclosures are mostly non-judicial, the Land Court SCRA filing is the earliest public, address-level distress signal. BatchData's "Notice of Default" label for MA is ambiguous, since MA has no standard recorded NOD, so national tools' MA pre-foreclosure fields may be inconsistent. Not verified.
- **Product.** A weekly (or daily) MA distress feed combining:
  - SCRA filings and tax lien filings, parsed from the Land Court PDFs
  - mortgagee's-sale auction notices and estate claims from published legal notices
  - enrichment with assessor data (owner mailing address, assessed value, last sale), plus county and town filters and CSV export
- **Pricing hypothesis (estimate).** $49–$99/month per county or $149–$199/month statewide, priced under PropStream Pro because it is MA-specific and earlier-signal.
- **Buyers:** real estate investors and wholesalers, iBuyers and local cash buyers, foreclosure-defense and bankruptcy attorneys (as subscribers), title and moving companies, and nonprofit housing counselors (possibly at discount).
- **Automation.** Fully automatable (PDF download, parse, geocode, enrich, email or CSV). Operational risk: mass.gov returned 403 to automated fetches in this session, so production jobs may need a compliant, polite fetch strategy or a public-records request for a recurring export.
- **Ethics and legal (inference).** Customers will contact defaulted homeowners, some of them servicemembers. The product's terms should bar FCRA-covered uses and require compliance with consumer-protection and telemarketing laws. MA AG foreclosure-rescue rules could not be verified (see Gaps).

### Gaps
- Exact annual volume of Land Court SM and Tax Lien filings in 2025–2026. The search for Warren Group monthly foreclosure statistics was blocked by the search budget.
- Whether the Land Court's published PDF lists carry reuse or resale restrictions. The masscourts.org public-portal terms were not retrieved, and the Attorney Portal terms forbid scraping and resale (see Q6).
- MA AG regulations on foreclosure-rescue transactions (believed to be 940 CMR 25.00) and their reach to list sellers versus buyers: not verified.
- Warren Group prices; whether PropStream or PropertyRadar include the MA SCRA signal.
- Registry of Deeds (masslandrecords.com) tax-taking instruments and probate (MassCourts) feeds were not researched in depth. Probate data falls under the MassCourts access rules.
- Reddit or BiggerPockets demand evidence for MA SCRA lists: none found.

---

## Q4. Public notice aggregation (masspublicnotices.org and newspaper legal notices): is there room for a paid alert product?

### Takeaway
Weak as a standalone product. The MA incumbent (Massachusetts Newspaper Publishers Association) already offers free search and a Smart Search daily email alert that is "Free During Introductory Period". Peer state press-association sites charge about $75/month for the same function, which proves willingness to pay but caps the price. The value lies in using notices as one input to vertical products (zoning/ZBA hearings for Q1, mortgagee sales and estate claims for Q3, bids for Q2), subject to the site's terms of use, which could not be retrieved.

### Cited Findings
- masspublicnotices.org is a public service of MA newspapers and the MNPA (header also names the Massachusetts Press Association). Search is free, with filters by county, city, publication and date. Current search covers 12 months, plus an archive. It receives notices daily, "the majority of the state's newspapers participate", and categories include foreclosures, hearings, bid ads, financial reports and ordinances. Use is governed by a Terms of Use whose text was not shown. — [masspublicnotices.org](https://www.masspublicnotices.org/)
- MA Smart Search: subscription rates "Free During Introductory Period". It supports multiple keywords, saved searches and daily automatic emails. The length of the intro period is not stated. Contact MNPA@publicnoticehelp.com. — [MA Smart Search signup](https://www.masspublicnotices.org/SmartSearchSignup.aspx)
- Peer pricing:
  - Colorado Smart Search: $75 for 30 days or $210 for 90 days (listed as of Nov 22, 2024). — [Colorado](https://www.publicnoticecolorado.com/SmartSearchSignup.aspx)
  - Wisconsin alert service: $75/month or $600/year. — [WisBlawg](https://wisblawg.law.wisc.edu/?p=2191)
  - Minnesota: Smart Search is a paid subscription, with basic search free. — [MNA](https://mna.org/mnpublicnotice/)
- The terms-of-use URL guessed at masspublicnotices.org/TermsOfUse.aspx returned 404 (observed in this session).

### Inferences
- Because MNPA gives MA alerts away for free (for now), a generic MA "notice alert" product would struggle. A product that classifies notices by use case (for example, "special permit hearings for BESS in Worcester County", or "mortgagee's sale of real estate in Essex County with assessed value") adds value the keyword alert does not. Pricing would follow the Q1 and Q3 products.
- If MNPA's terms bar automated access or republication, notices should be used only as links or pointers and not republished. Primary sources (town agendas, Land Court lists) can replace most notice content.

### Gaps
- masspublicnotices.org Terms of Use text (automated access, commercial reuse).
- When the MA Smart Search introductory free period ends, and the planned price.
- Whether local licensing boards' liquor and other license hearing notices appear on the site consistently (not researched).

---

## Q5. New business and license leads (MA Corporations Division, liquor/other licenses): proven, priced, and accessible?

### Takeaway
The category is proven but commoditized. Lead lists of new LLCs and corporations sell for about $3–$20 per 1,000 records on marketplaces, or $50–$200/month from list services. MA has volume (about 66,000–67,000 new entities a year), and the marketplace scrapers checked here did not cover MA, which suggests some access friction. Expect low prices, low defensibility and CAN-SPAM/TCPA exposure for buyers. It is a reasonable low-effort add-on, not a lead product.

### Cited Findings
- The MA Corporations Division organized or registered more than 67,000 new business entities in FY2024 and more than 66,000 in FY2023. — [SOC Annual Report FY2024](https://www.sec.state.ma.us/divisions/public-records/download/archives/SOC-Annual-Report-FY-2024.pdf); [SOC Annual Report FY2023](https://www.sec.state.ma.us/divisions/public-records/download/archives/SOC-Annual-Report-FY-2023.pdf)
- The Corporations Division has a "ListNewFilings.aspx" page under its login system. Its content and requirements could not be read (empty response in this session). — [corp.sec.state.ma.us ListNewFilings](https://corp.sec.state.ma.us/corpweb/loginsystem/ListNewFilings.aspx); [Corporations Division about](https://www.sec.state.ma.us/divisions/corporations/general-information/corporations-about.htm)
- Marketplace pricing for new-business filing leads:
  - $10 per 1,000 rows (CO, CT, NY) — [Apify scrapemint](https://apify.com/scrapemint/new-business-registration-leads)
  - From $3 per 1,000 (eight states) and $5–$20 per 1,000 in others — [Apify listings](https://apify.com/great_pistachio/us-new-business-filings)
  - Sellers claim list services charge $50–$200/month for the same public data (self-reported) — [Apify listings](https://apify.com/great_pistachio/us-new-business-filings)
  - Sellers pitch the leads to insurance agents (GL, workers' comp, commercial auto, E&O) — [Omni Online Strategies](https://omnionlinestrategies.com/blog/how-to-use-new-llc-filings-to-find-health-insurance-prospects)
- One "Official State Registries" Apify actor covers CO, CT and NY only. MA is not included. Fields: entity_id, name, type, filing_date, status, address, registered agent. — [Apify esco.api new-business-filings](https://apify.com/esco.api/new-business-filings)

### Inferences
- About 67,000 entities a year is roughly 1,300 new MA entities a week (arithmetic on the SOC figure). Buyers: insurance agents, CPAs and bookkeepers, payroll and merchant-services firms, web and marketing agencies, and banks.
- **Pricing hypothesis (estimate).** $29–$79/month for weekly MA new-entity lists by county or industry keyword. The price is low because comparable data costs only dollars per thousand records.
- The absence of MA in sampled scrapers may reflect that the MA corporate search lacks a public date-range "new filings" view (unverified). A public-records request (c. 66 §10) for a recurring new-filings export is a possible compliant alternative (see Q6).
- Liquor and other local license applications (local licensing boards, ABCC) are a plausible higher-value niche for distributors, POS vendors and insurers. They would surface through the meeting and notice pipeline in Q1 and Q4, but this was not researched.

### Gaps
- Whether the Corporations Division sells bulk or recurring new-filing data, or exposes a date-filterable public search.
- Terms of use for corp.sec.state.ma.us automated access.
- ABCC or local liquor license data availability and comparable products and prices.
- Building and occupancy permit leads in MA. Construction Monitor appears to cover some MA cities (Cambridge, Boston and Framingham permits appear on Levelset pages sourced from it), and Shovels' coverage claims conflict (1,800+ vs 20,000+ jurisdictions; one directory lists $599/month). MA town-by-town coverage was not established. — [Levelset (Construction Monitor data)](https://levelset.com/contractors/elaine-construction/permits); [Construction Monitor](https://constructionmonitor.com/); [Shovels (Sacra)](https://sacra.com/c/shovels/); [Boston permits Apify scraper, $1 per 1,000](https://apify.com/quarterly_jingo/boston-permits-scraper)

---

## Q6. Cross-cutting data access and legal risks (Public Records Law, court data rules, scraping, FCRA, privacy, marketing laws)

### Takeaway
Municipal agendas, procurement notices and the Land Court's own published PDF lists are low-risk public sources. Scraping MassCourts case data is high-risk: court rules and the Attorney Portal terms explicitly prohibit scraping and resale, so products should avoid MassCourts and use court-published reports or records requests instead. FCRA risk is controlled by banning eligibility uses in the terms of service. The CFPB's 2024 data-broker rule was withdrawn in May 2025. MA's comprehensive privacy bill (with possible data-broker provisions) passed both chambers in different versions, and enactment was unconfirmed as of this research.

### Cited Findings
**Court records**
- Trial Court Rule XIV (Uniform Rules on Public Access to Court Records) separates compiled data (Rule 3), bulk data (Rule 4) and remote access (Rule 5). Bulk data means records "as originally entered" in case management databases. Remote access runs through the eAccess Public Portal and a registered-attorney portal. — [Trial Court Rule XIV](https://www.mass.gov/doc/trial-court-rule-xiv-uniform-rules-on-public-access-to-court-records/download); [Rule 1 definitions](https://mass.gov/trial-court-rules/uniform-rules-on-public-access-to-court-records-rule-1-scope-and-definitions)
- The Trial Court Attorney Portal Terms of Use (effective July 1, 2018) prohibit "data scraping", defined as using a computer program or automated process to extract data from the Trial Court's case management system. They also prohibit selling information obtained "directly or indirectly" to third parties, and use is monitored. The public-portal (masscourts.org) terms were not retrieved. — [Attorney Portal terms of use](https://www.mass.gov/info-details/attorney-portal-terms-of-use)

**Public Records Law and municipal access**
- Under the Public Records Law (M.G.L. c. 66 §10), municipalities must respond within 10 business days and designate Records Access Officers. Town guidelines say electronic production is the norm. — [Plymouth guideline](https://plymouth-ma.gov/1400/Plymouth-Public-Records-Access-Guideline); [Belmont guidelines](https://belmont-ma.gov/public-records-access-officer/files/belmont-public-records-access-guidelines); [Amesbury summary](https://schools.amesburyma.gov/Page/495)
- Fee figures ($0.05 per page, $25 per hour) appear in one school-district summary and may be outdated. — [Amesbury summary](https://schools.amesburyma.gov/Page/495)

**FCRA and federal data-broker rules**
- FCRA status turns on use. Data not assembled or used for eligibility decisions (credit, employment, insurance, tenancy) is generally argued not to be a "consumer report". Tenant screening and similar uses are the high-risk pattern. This is an industry or practitioner view, not a court holding. — [Troutman CFPB FCRA panel transcript](https://www.troutman.com/a/web/xt7aE8f1E4nX4mdfoqvrFc/893dzq/transcript_cfp_fcra_focus_cfpb_rulemaking_under_the_fcra_pt_3.pdf); [Offlist explainer (secondary)](https://www.offlist.me/blog/fcra-data-brokers-explained)
- The CFPB withdrew its December 2024 proposed rule "Protecting Americans from Harmful Data Broker Practices" (FCRA/Regulation V) on May 15, 2025 (90 FR 20568). It said the rule was "not necessary or appropriate at this time". — [Orrick InfoBytes](https://infobytes.orrick.com/2025-05-16/cfpb-withdraws-its-proposed-rule-on-data-brokers/); [NASCUS](https://www.nascus.org/cfpb-summaries/summary-cfpb-withdrawal-of-the-proposed-rule-on-harmful-data-broker-practices/)

**MA privacy bill**
- The MA House reportedly passed H 5472 on June 5, 2026, after the Senate passed S 2619 in September 2025. Earlier drafts would require data broker registration with the AG. Final enactment is unconfirmed, and the source is an aggregator. — [ThreatCluster](https://threatcluster.io/cluster/massachusetts-passes-landmark-data-privacy-legislation-325ffa9e); [Digital Policy Alert](https://digitalpolicyalert.org/change/4504-massachusetts-data-broker-registration-requirement-in-data-privacy-protection-act-sd-745-hd-2281); [Optery](https://www.optery.com/?p=23760)

### Inferences
- **Safe-sourcing design (inference):**
  - Use municipal websites (OML postings), COMMBUYS public pages, Central Register issues (if subscription terms allow), and Land Court-published PDF reports.
  - Avoid automated MassCourts queries entirely.
  - For anything else, file recurring c. 66 §10 requests, which an agent can draft and send by email. Fulfillment is manual on the town's side but needs no per-customer work from the owner.
- **FCRA posture (inference).** Sell distress and business lists for marketing and research only. The terms of service should prohibit eligibility uses, and the product should not offer tenant, employment or credit screening features.
- **Email and marketing (inference, not verified in this research).** Alert emails to paying, opted-in subscribers are mostly transactional or relationship messages under CAN-SPAM. Customers' cold outreach (calls or texts to homeowners or new LLC owners) carries TCPA and MA telemarketing exposure, so the product should not bundle skip-traced phone numbers.
- **MA privacy (inference).** If MA enacts a law with a data-broker registry, a distress-list product selling personal data about MA residents may need to register and honor deletion requests. Municipal-meeting and bid products are largely unaffected.

### Gaps
- masscourts.org public-portal terms and Rule XIV Rule 4 bulk-data conditions (exact text not retrieved).
- TCPA, CAN-SPAM, MA c. 159C telemarketing and 940 CMR 25.00 specifics. Not verified because the search budget was exhausted.
- Final status of MA H 5472 / S 2619 (check malegislature.gov).

---

## Q7. Ranking: which 4–6 products best fit "proven elsewhere, weak in MA, fully software-run, no licensed professional"?

### Takeaway
Ranked by demand evidence, MA gap and automation fit:
1. MA clean-energy and land-use meeting/permit monitor.
2. MA early-distress list (Land Court SCRA and tax lien, plus auction notices).
3. Central Register-centered construction and real-property bid alerts, with trade and sub-bid filters.
4. Vertical public-notice alerts (only as a feature of 1–3).
5. New-entity/business-license leads (low-price add-on).
6. Building-permit leads (unproven MA coverage gap; needs more research).

### Cited Findings
- Demand and timing for #1:
  - consolidated local clean-energy permits mandatory from Oct 1, 2026, with a 12-month clock and constructive approval — [ABA](https://www.americanbar.org/groups/environment_energy_resources/resources/natural-resources-environment/2026-spring/ray-hope-massachusetts-renewables-permitting-reform)
  - multiple 2026 BESS moratorium efforts — [Lee](https://leema.gov/DocumentCenter/View/4860/Planning-Board-Public-Hearing-Bess-Moratorium-Bylaw-Amendment-April-27); [Sturbridge](https://www.sturbridge.gov/node/171911); [H.5641](https://malegislature.gov/Bills/194/H5641)
  - developer-facing paid comparables — [Hamlet](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/); [OrdinanceWatch](https://ordinancewatch.com/); [SitePath](https://www.utilitydive.com/press-release/20260807-sitepath-intelligence-launches-county-level-permitting-intelligence-platfor-1/)
- Data for #2 is official, free and nightly — [Land Court reports](https://www.mass.gov/lists/land-court-masscourts-reports). Comparables price at $59–$699/month — [PropStream](https://www.propstream.com/news/how-much-does-propstream-cost); [PropertyRadar (Capterra)](https://www.capterra.com/p/230568/PropertyRadar/)
- #3's data is legally mandated to pass through the Central Register ($10K+ construction, real property) — [OIG 30B Manual 2026](https://maoig.gov/wp-content/uploads/Chapter-30B-Manual-2026.pdf). Comparables cost $35–$1,999/year at the low end — [BidNet via Civic IQ](https://civiciq.com/blog/civic-iq-bidnet-direct-pricing); [DemandStar](https://network.demandstar.com/?p=80)
- #4's incumbent alert is currently free in MA — [MA Smart Search](https://www.masspublicnotices.org/SmartSearchSignup.aspx)
- #5's comparables are commoditized at $3–$20 per 1,000 rows — [Apify](https://apify.com/scrapemint/new-business-registration-leads)

### Inferences
- **Summary scoring (all inference or estimate):**

| # | Product | Buyers | Price hypothesis | MA gap | Automation | Main risk |
|---|---|---|---|---|---|---|
| 1 | Meeting/permit monitor (BESS, solar, 40B, cell, moratoria; all 351 towns) | Energy developers, land-use attorneys, developers, consultants, associations, journalists | $49–$99/mo individual; $299–$999/mo team | High (fragmented town sites; no statewide aggregator found; national coverage likely thin) | High; scraper upkeep is the main cost | Site heterogeneity, accuracy, sales cycle |
| 2 | Early-distress list (SCRA + tax lien + auctions + estate claims) | Investors, wholesalers, attorneys, title and moving firms | $49–$199/mo | Medium-high (MA-unique SCRA signal; Warren Group incumbent) | Very high (PDFs) | mass.gov bot-blocking, court reuse terms, ethics and solicitation laws, privacy bill |
| 3 | Central Register + town bid alerts with filed-sub-bid trades and surplus property | Contractors, subs, suppliers, developers | $25–$50/mo | Medium (COMMBUYS free; national aggregators present) | High | Low willingness to pay, Central Register terms |
| 4 | Vertical notice alerts | Same as 1–3 | Feature, not product | Low (MNPA free) | High | MNPA terms |
| 5 | New entity / license leads | Insurance agents, CPAs, vendors | $29–$79/mo | Low-medium | High (if data accessible) | Commodity pricing, CAN-SPAM/TCPA |
| 6 | Building permit leads | Contractors, solar installers, suppliers | Unknown | Unknown | Medium (many permit portals) | Coverage unverified |

- **Bundling (inference).** One crawler fleet (town websites + Land Court + Central Register + public notices) can feed products 1–4, which spreads maintenance cost. All six can be billed self-serve via Stripe with no per-customer manual work. None requires a licensed professional, provided the product offers data and alerts, not legal advice or eligibility screening.

### Gaps
- No direct MA customer-demand evidence (forums, Reddit, surveys) was found for any of the six. Validation via landing pages or waitlists is recommended.
- Real conversion and pricing data for MA buyers is unavailable. All price points above for MA products are estimates anchored to the comparables listed.
