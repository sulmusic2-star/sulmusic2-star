# 351 Watch Should Sell Verdicts, Not Summaries

> **Update, Oct 10, 2026 (after this report was written):** next steps 1–3 are done, and part of step 7. The crawler now records a per-item `first_seen` time and the days before each meeting (`data/first_seen.json`). The two robots.txt gaps in `fetch.py` are fixed: HTML-typed robots files are parsed when they contain directives, and redirects are followed hop by hop with a robots check before each request. `tracker.json` is corrected (Lee, Sturbridge and Hampden disapproved) and adds five more AG-disapproved moratoria (Hanson, Southwick, Chesterfield, Gill, Brookfield). A public coverage-and-method page is live at /proof. It shows the all-351-town status table, agenda lead times, the AG moratorium ledger with letter links, and the crawler's rules. It does not yet show a per-town "last successful crawl" column. The "must not claim" rows about robots.txt and per-item timing now have their fixes in place, but speed claims against competitors still need observed competitor timing.

351 Watch can already prove two things, breadth and answers, but it cannot prove the third thing its pitch has implied: that it is faster than rivals. On October 10, 2026 its crawler read current agendas in **240 of Massachusetts' 351 municipalities, home to 73% of residents**. That includes 224 planning boards, 194 zoning boards of appeals (ZBAs) and 221 conservation commissions; Hamlet lists 81 Massachusetts municipalities. Its Attorney General (AG) dataset, built from all 2,719 bylaw decision letters issued since January 2022, shows the AG has **disapproved every one of the 18 solar and battery-storage (BESS) moratorium articles she has ruled on since June 2022**, while approving 96% of bylaws that regulate those uses, in whole or in part. Lead time is a different matter, because it belongs to the towns. Agendas go up a median of **five days** before the meeting, so any daily crawler gets the same head start, and Hamlet's own API already models agendas with "agenda-monitoring topics." The asset that lasts is a complete, sourced record of Massachusetts siting decisions: every hearing, vote, AG ruling and applicant company. The pitch should therefore cover every siting decision, not just bans: moratoria were only **8 of 59 siting events** in the pilot. On expansion, about a dozen states match or beat Massachusetts' agenda-posting rule, but who holds siting power matters more than posting law. New York should come first, Maine and Rhode Island are cheap add-ons, and Pennsylvania is the larger second bet. The likeliest buyer and the most dangerous competitor are now the same company: Boston Globe Media, which bought the Massachusetts tracker InstaTrac in July 2026. The main gaps are 111 towns not yet automated (64 of them behind bot walls), no per-item timestamps yet to prove our own alert timing, competitor sites that blocked every check, and market sizes that are estimates.

| Owner's question | Short answer | Where |
|---|---|---|
| 1. Do other states require agendas, and where should we expand? | Yes, about 12 states match or beat MA on paper. Northeast: New York first, Maine and Rhode Island as cheap add-ons, Pennsylvania second. Nationally: Pennsylvania-style township states (OH, MI) and Illinois. | "A dozen states match..." |
| 2. Can we prove we go deeper on MA? | Yes on breadth: 240 towns and 235 with a land-use board automated. Lead time is proven for town posting (5-day median) but not yet for our own alerts. | "240 of 351 towns..." |
| 3. Can we prove we give answers? | Yes for AG bylaw review: 18 of 18 moratoria struck since June 2022 and 109 of 114 regulating bylaws approved, with ten documented exceptions. Not yet for project permits. | "The AG record..." |
| 4. What do competitors deliver? | Hamlet and Citizen Portal both touch agendas. No rival shows all-351 land-use coverage. Never say rivals are "after the fact only." | "Rivals already read agendas..." |
| 5. Will the lead last? | Summaries and speed are easy to copy. Completeness, the MA legal process, history and company and parcel links are not. | "Completeness, history..." |
| 6. Is a ban-focused pitch too narrow? | Yes. Bans were 1 event in 7. The market is roughly 120 to 250 solar and storage projects a year, plus data centers and 40B housing, sold to a 92-company target list. | "Bans were one siting event..." |
| 7. Who buys us if we win? | Boston Globe/InstaTrac, Shovels, Hamlet, the Warren Group. They pay for history and early signal, and small deals have undisclosed prices. | "Buyers pay for history..." |

## 240 of 351 towns are automated, and their agendas post five days early

The statewide census run on October 10, 2026 is the strongest proof the company has. It used the same polite crawler as the 30-town pilot: it identifies itself as 351WatchBot, obeys robots.txt, sends at most one request per second to each host, never logs in and never solves bot challenges. It found a current, dated agenda listing for at least one meeting board in **240 of 351 municipalities, covering 5.19 million of the state's 7.14 million residents** ([351 Watch census summary](<../projects/351watch/data/ma_census_summary.json>)). A stricter test, requiring two or more dated agendas, still passes 233 towns. Counting land-use boards specifically from the per-town file, **235 towns have at least one planning board, ZBA or conservation commission automated, and 182 have all three** ([per-town census](<../projects/351watch/data/towns_ma_all.json>)). Discovery was fully automatic, and it reproduced the hand-built pilot exactly: the same 24 of 30 sample towns were automated and the same 6 were not.

| Board | Towns automated | Share | Residents covered |
|---|---|---|---|
| Planning Board | **224** | 64% of 351 | 3.95 M |
| Zoning Board of Appeals | **194** | 55% | 4.35 M |
| Conservation Commission | **221** | 63% | 3.95 M |
| Select Board / City or Town Council | **225** | 64% | 4.83 M |
| Town Meeting warrant found online | 92 | 32% of 292 Town Meeting towns | 1.23 M |
| All four meeting boards | 177 | 50% | 3.30 M |

The comparison with rivals rests on a fixed 30-town sample checked the same day. Hamlet's coverage page, seen only as a search-index snippet because the site blocks automated visitors, claims "81 cities and 1 counties" in Massachusetts, about 23% of municipalities ([Hamlet coverage](https://www.myhamlet.com/coverage)). In the sample, Hamlet showed only three partial towns and no land-use body. Citizen Portal articles turned up for some municipal body in 18 of 30 sample towns and for a land-use board in 13, both lower bounds from per-town searches of its public index ([Citizen Portal articles](https://citizenportal.ai/articles/9876698/Massachusetts/School-Boards/Lincoln-Sudbury/Sudbury-staff-begin-drafting-battery-storage-bylaw-as-state-rules-take-effect-Board-seeks-protections-for-water-districts)). SitePath grades every county, but its Massachusetts county pages read "Energy-related meetings & dockets: No tracked activity yet" ([SitePath](https://www.sitepathintel.com/)). CivicSearch covers two sample towns, and only their councils or select boards ([CivicSearch](https://civicsearch.org/carver-massachusetts)).

| 30-town sample, Oct 10, 2026 | 351 Watch | Hamlet | Citizen Portal | SitePath | CivicSearch |
|---|---|---|---|---|---|
| Statewide footprint | 240 towns automated | 81 + 1 county (self-reported) | No count published | Every county graded; no MA meetings tracked | 15 MA places |
| Sample towns, any body | **24** | 3 partial | 18 (lower bound) | 0 meetings | 2 |
| Sample towns, PB/ZBA/ConCom | **23** | 0 seen | 13 (lower bound) | 0 meetings | 0 |

The lead-time evidence needs careful framing, because it measures the towns, not us. CivicPlus AgendaCenter prints a "Posted" time on each agenda and CivicClerk publishes one in its API. From those stamps the census measured **4,116 first postings in 103 towns for meetings held April 13 to October 9, 2026**. The median agenda went up **5 days** before the meeting. The 10th percentile was 2 days, or 33 hours before the meeting day began. **94% were online at least 24 hours** before the meeting day and 82% at least 48 hours before ([lead-time data](<../projects/351watch/data/leadtime_ma_all.json>)). Exact CivicClerk times, measured to the scheduled start, give a median of 121 hours. Practice beats the law by a wide margin: the statute requires only 48 hours' notice, excluding weekends and holidays, posted at the clerk's office ([M.G.L. c. 30A §20](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIII/Chapter30A/Section20)).

| Board | Agendas | Median lead | 10th percentile | Up ≥48 h before meeting day | ≥24 h | First online on or after meeting day |
|---|---|---|---|---|---|---|
| Planning Board | 873 | 5 d | 2 d (37 h) | 88% | 96% | 3% |
| Zoning Board of Appeals | 608 | **7 d** | 2 d (36 h) | 85% | 96% | 3% |
| Conservation Commission | 862 | 5 d | 2 d (33 h) | 77% | 94% | 4% |
| Select Board / Council | 1,748 | 4 d | 2 d (32 h) | 82% | 93% | 5% |
| **All boards** | **4,116** | **5 d** | **2 d (33 h)** | **82%** | **94%** | **4%** |

A crawl every 24 hours therefore alerts before about 94% of meetings, and a six-hour crawl would catch most of the late postings. The roughly 4% that first appear online on the meeting day cannot be caught early from websites at all. The flip side matters more for positioning: a five-day public head start is available to anyone who crawls daily. What 351 Watch can prove is that it reads those agendas across far more Massachusetts boards than anyone else shows, not that it reads them sooner.

The six-item test of October 2026 clean-energy agenda items shows both the strength and the weak spot. Four items were captured 3 to 16 days before their meetings. Two were read from the agenda only after the meeting, because the crawl ran on October 10, and the crawler stores only a run-level timestamp, not a per-item "first seen" time ([pilot agenda hits](<../projects/351watch/data/agenda_hits.json>)).

| Item | Meeting | 351 Watch capture | Citizen Portal public index, Oct 10 | Hamlet |
|---|---|---|---|---|
| Fitchburg City Council: BESS zoning moratorium | Oct 6 | From agenda, but crawled after the meeting | No article found | Not verifiable (site blocked) |
| Pittsfield City Council: BESS zoning amendment | Oct 13 | **3 days before** | Only an April 21 board recap | Not verifiable |
| Westford: §6.6 small clean-energy facilities (Select Board; Special Town Meeting) | Oct 13; Oct 26 | **3 and 16 days before** | Not found | Not verifiable |
| Northampton Planning Board: 225 CMR 29 consolidated permitting | Oct 8 | From agenda, but crawled after the meeting | No article found | Not verifiable |
| Sudbury Planning Board: BESS bylaw | Oct 14 | **4 days before** | Earlier recaps only | Not verifiable |
| Carver Planning Board: Federal Pond Solar special permit with BESS | Oct 13 | **3 days before** | Carver not covered | Not verifiable |

The statewide crawl also shows how deep the reading goes. For meetings dated September 10 to December 9, 2026, it scanned **2,524 agenda documents**. A quarter (641) were image-only scans with no text layer, and OCR (text recognition) recovered 639 of them. It produced **882 topic hits in 168 towns, 174 of them (20%) from OCR text** that a plain text scraper would never see, and 135 hits in 67 towns were still actionable on October 10 ([statewide hits](<../projects/351watch/data/agenda_hits_ma_all.json>)). Examples the pilot could not see:

- Lakeville Planning Board's October 22 hearing on a new BESS zoning section with Tier 1 to 3 permitting.
- A Somerset ZBA petition from Somerset Energy Storage LLC for a commercial BESS at 1606 Riverside Ave.
- Votes by the Middleton, Mattapoisett and Halifax select boards to adopt the state's consolidated permit process.
- Data-center moratorium drafting in Northfield and Boxborough.

In the pilot, about 90% of hits were real siting items, so hits still need a spot-check before anything is published.

The gaps are real. **111 towns (1.94 million residents) are not automated.** Of those, **64 towns (1.10 million) sit behind bot protection or vendor refusals**:

- Cloudflare or Akamai walls on the town site: Brookline, Newton, New Bedford, Barnstable and others.
- 14 towns on the MyTownGovernment vendor.
- iQM2/Granicus portals that answer HTTP 429 (Cambridge, Framingham, Revere).
- A robots.txt disallow on Worcester's PrimeGov portal.

The census rightly declined a legacy "http://www." alias that would have sidestepped MyTownGovernment's protection. Another 21 towns had no current, dated listing (Peabody, Greenfield and Acton deserve a manual look). Town Meeting warrants were found for only 92 of 292 towns. Conservation Commission hits were thin (43 of 882). Boston is only partly covered: its City Council and ZBA, but not its planning agency or Conservation Commission. **The verdict on question 2:** breadth can be proven today with dated numbers. Lead time is proven as town behavior, but not yet as 351 Watch's own alert timing.

## The AG record turns alerts into answers: 18 of 18 moratoria struck since 2022

The AG's Municipal Law Unit publishes every bylaw decision letter in a public lookup that needs no login ([Municipal Law Unit](https://www.mass.gov/the-municipal-law-unit); [decision look-up](https://massago.hylandcloud.com/231publicaccess/MLU.html)). The build did not rely on the portal's topic tags. Those tags miss letters (Gill's BESS moratorium is tagged DATA CENTERS), and about 11% of tagged letters are missing from the full-text index. Instead, the build downloaded **all 2,719 decision letters dated January 1, 2022 to October 10, 2026**, scanned their text and read every candidate. The result is **131 AG decisions in 93 towns**, plus 5 court rulings, 3 city ordinances and 1 pending article ([AG decisions dataset](<../projects/351watch/data/ag_decisions.json>)). Every row's article numbers, town and meeting date match the letter's header (131 of 131). The dataset is also more complete than the AG's own summary. The footnoted list of moratorium disapprovals in her 2026 letters omits **Hanson (2024) and Hampden (2025)**, both of which this dataset documents.

| Bylaw type (letters) | Approved | Approved in part | Disapproved | No action (moot) | Total |
|---|---|---|---|---|---|
| Moratorium | 1 | 0 | **15** | 1 | 17 |
| Zoning regulation | 73 | 32 | 2 | 0 | 107 |
| Zoning prohibition | 1 | 1 | 1 | 0 | 3 |
| General bylaw (licensing) | 0 | 0 | 2 | 0 | 2 |
| General bylaw (other) | 1 | 0 | 0 | 0 | 1 |
| Consolidated permit bylaw | 1 | 0 | 0 | 0 | 1 |
| **Total** | **77** | **33** | **20** | **1** | **131** |

Those 17 moratorium letters cover 21 articles. The SJC decided *Tracer Lane II* on June 2, 2022, holding that a near-total solar ban is impermissible. Since then, **the AG has disapproved all 18 solar or BESS moratorium articles she has ruled on, in 14 towns**, including **all 15 from 2024 to October 2026 (12 towns)**. The pace accelerated in 2026, when ten moratorium letters came down, all disapprovals, in the run-up to the October 1 deadline for towns to accept consolidated permit applications. Bylaws that regulate rather than ban fared the other way. **109 of 114 non-moratorium decisions (96%) were approved in whole or in part** (76 outright, 33 with specific text struck). Since January 2024, no solar or BESS zoning bylaw has been disapproved in full (47 non-moratorium bylaws approved and 16 approved in part over that period). The only full disapprovals in that period were general licensing bylaws from Wendell and Shutesbury, which the AG said had to be adopted as zoning. The Land Court affirmed the Wendell ruling in March 2026.

| AG decision | Town | Article(s) | Technology | Outcome |
|---|---|---|---|---|
| 2022-05-17 | Medway | Art. 10 (one district only) | BESS | **Approved** (before *Tracer Lane II*) |
| 2022-11-14 | Carver | Arts. 26, 38 | Solar; BESS | Disapproved |
| 2023-03-15 | Ware | Art. 22 | BESS | Disapproved |
| 2024-03-07 | Hanson | Art. 34 | BESS | Disapproved |
| 2024-07-19 | Spencer | Arts. 14, 15 | Solar; storage | **No action (moot)** |
| 2024-10-30 | Northfield | Arts. 26, 27 | BESS; solar | Disapproved |
| 2025-03-11 | Hampden | Art. 18 | BESS | Disapproved |
| 2026-03-11 | Blandford | Art. 1 | Both | Disapproved |
| 2026-04-24 | Southwick | Art. 5 | Both | Disapproved |
| 2026-06-08 | Worthington | Art. 6 (town-wide) | Both | Disapproved |
| 2026-06-08 | Worthington | Arts. 7, 8 (limited areas) | Solar; storage | Disapproved |
| 2026-06-22 | Becket | Art. 4 | Both | Disapproved |
| 2026-08-13 | Sturbridge | Art. 63 | BESS | Disapproved |
| 2026-08-31 | Lee | Art. 26 | BESS | Disapproved |
| 2026-09-23 | Chesterfield | Art. 3 | BESS | Disapproved |
| 2026-09-24 | Gill | Art. 7 (BESS part) | BESS | Disapproved (data-center part approved) |
| 2026-10-07 | Brookfield | Art. 35 | BESS | Disapproved |

The reasoning is consistent enough to turn into rules. Under G.L. c. 40A §3, paragraph 9, a bylaw may not "prohibit or unreasonably regulate" solar unless that is necessary for health, safety or welfare. From late 2023 the AG's letters treat BESS as solar energy systems, citing *NextSun* (Land Court 2023) and, from September 2025, *Duxbury Energy Storage* (Land Court 2025). From August 2026 they also cite *Sunpin v. Petersham* (SJC, July 14, 2026), along with a moratorium's conflict with the duty to accept consolidated permit applications from October 1. Moratoria fail for lacking "any articulated public health, safety, or welfare justification... (even for a short amount of time)."

Among partial approvals, the provision most often struck is a herbicide or pesticide ban at the site, which the Pesticide Control Act preempts; that accounts for **16 of 33**. Other provisions that get struck:

- rules meant to eliminate views of a facility;
- $100 million insurance requirements;
- making the owner pay for responder training;
- caps on the number of installations;
- fiscal-impact tests for denial.

What survives:

- size tiers with district-by-district special permits;
- prohibitions in some districts that leave others open;
- an aquifer-district cap (Whately, 250 kWh);
- reasonable setbacks and decommissioning rules;
- fire-code (NFPA 855) compliance;
- a consolidated permit bylaw that tracks 225 CMR 29 (Medway 2026).

| Pattern on a warrant | Historical outcome | Basis |
|---|---|---|
| Solar or BESS moratorium, any length or area | Disapproved, 18 of 18 since June 2022 | c. 40A §3; *Zuckerman*; Ch. 239 (Lee, Sturbridge) |
| Town-wide or standalone-BESS ban; size cap everywhere | Disapproved | Wendell, Pelham, Worthington Art. 8 |
| BESS licensing via a general bylaw | Disapproved | c. 40A §5 (Wendell, Shutesbury) |
| Herbicide or pesticide ban at sites | Struck | c. 132B (16 letters) |
| Tiered zoning with districts and special permits | Approved | Wilbraham, Lunenburg, Hubbardston 2025 |
| Prohibition only in sensitive districts | Usually approved | Whately, Tewksbury, Millis, Northborough |
| Data-center moratorium | Approved | Shutesbury, Templeton, Gill (not a protected use) |

The exceptions are what make the claim credible, and every public statement should carry them:

| Exception | What happened | Effect on the claim |
|---|---|---|
| Medway, May 17, 2022 | A one-district BESS moratorium was approved 16 days before *Tracer Lane II* | Date the claim "since June 2022" |
| Spencer, July 19, 2024 | No action: moot once the town adopted solar and BESS zoning | Say "ruled on," not "every moratorium found" |
| Gill, Sept. 24, 2026 | BESS part struck, data-center part approved | Technology decides the outcome |
| Data-center moratoria | Approved in Shutesbury (Jan. 20, 2026), Templeton (Sept. 22, 2026) and Gill | Never say "moratoria are illegal in MA" |
| Oakham, Jan. 4, 2023 | Standalone-BESS ban approved before the line hardened | A ban is not a moratorium; one historical approval |
| Cities | Ordinances are not submitted to the AG: Westfield's interim BESS ban (through Sept. 30, 2026), Leominster (reported through July 31, 2027), Fitchburg and Pittsfield proposals | The record covers towns only |
| Review lag | Median of about 108 days from town meeting to ruling for 2025–26 moratoria; Chesterfield's expired Sept. 30 and was struck Sept. 23 | A struck moratorium can still delay a project |
| Unsubmitted | Acushnet's 2022 moratorium was never submitted and "never had lawful effect" | Cannot be counted |
| Bare approvals | Some letters say only "We approve Article 6"; Whately's cap was found only through news | Approvals may be undercounted; moratoria are low-risk because every one drew written analysis |
| Pending | Lee Art. 4 (Oct. 1 STM), Whately Art. 24, Brookfield Art. 36 hold, Duxbury | Refresh monthly |

**This is the clearest example of an answer rather than a summary.** A summary says a moratorium article is on Becket's warrant. An answer says that every comparable article since June 2022 has been disapproved, that rulings arrive about three and a half months after town meeting, and that the town's companion bylaw is likely to survive with any herbicide clause struck. Two limits apply. First, this is a track record, not legal advice, and the wording needs a lawyer's review. Second, the proof covers one decision type. Planning board votes, ZBA decisions and conservation-commission orders of conditions are not yet structured the same way. The tracker also needs updating to match this dataset: Lee and Sturbridge are not pending (both were disapproved in August 2026), and Hampden's moratorium passed town meeting and was disapproved in March 2025.

## Rivals already read agendas, so claim breadth rather than exclusivity

The most important correction from this research is that "competitors only cover meetings after the fact" is false and must never be said. Hamlet's public API specification defines a `Meeting.has_agenda` flag, a hierarchical `Agenda` of `AgendaItem`s, and `AgendaItem.matched_topics`, described as "Agenda-monitoring topics matched on this item" ([Hamlet Public API](https://api.myhamlet.com/openapi.json)). Its marketing, seen through the search index, promises to "notify your team the moment agendas are posted" ([Hamlet about page](https://myhamlet.com/about-us)). Citizen Portal published agenda-preview articles for Warwick's Selectboard in June 2026 ([Citizen Portal, Warwick](https://citizenportal.ai/articles/8446509/Massachusetts/Franklin-County/Warwick/Selectboard-agenda-flags-possible-hearing-on-Six-Town-Regionalization-Planning-Board-proposal)). GovSpend's scrapers "run every day" across 10,000+ agencies, reading agendas and agenda packets ([GovSpend help center](https://support.govspend.com/data-over-meeting-intelligence)).

The same API also shows Hamlet's limits in Massachusetts:

- It records no time when the town posted the agenda, and it carries no source link to the agenda PDF.
- Its body types are California-shaped (CITY_COUNCIL, PLANNING_COMMISSION, BOARD_OF_SUPERVISORS, SCHOOL_BOARD, OTHER), and its location types are CITY, COUNTY or STATE, with no TOWN. Massachusetts select boards, ZBAs, conservation commissions and Town Meeting likely land in OTHER.

No competitor's actual delivery could be checked for any Massachusetts board. Both main sites served bot challenges on their terms pages, and no account was created.

| Competitor | What it delivers (evidence) | When it first knows about an item | Massachusetts footprint |
|---|---|---|---|
| **Hamlet** (Orinda, CA; about $10M raised) | Video transcripts, summaries, keyword alerts and sentiment indices. Went from "dozens of jurisdictions" to "3,000+" bodies in Feb 2026 ([PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/)), and now claims 6,600+ in search snippets. Free tier plus a 14-day trial; enterprise pricing through sales. CEO's goal: the "Bloomberg" of the space ([TechCrunch](https://techcrunch.com/2025/12/05/new-streaming-channel-launches-to-give-viewers-a-peek-into-city-council-meetings/)) | Mainly video after the meeting, refreshed weekly and "moving to daily." Agenda monitoring is offered to enterprise and API subscribers, with timing unverified | 81 municipalities + 1 county. Chicopee has 15 bodies, including its planning board, ZBA and conservation commission ([Hamlet Chicopee](https://www.myhamlet.com/chicopee-ma)). 3 of 30 sample towns partial |
| **Citizen Portal** (Utah; crowdfunded about $1.4M, reported) | AI-written articles drawn from agendas, video and minutes; topic alerts at $12–49/month, with conflicting lifetime offers of $199–999 ([sign-up](https://citizenportal.ai/signup)). Its terms bar users from building "a competitive product" ([terms](https://citizenportal.ai/terms)) | Mostly recaps; agenda previews seen only for Warwick | 18 of 30 sample towns (13 with a land-use board), lower bounds. Some articles are misfiled under school-board paths |
| **InstaTrac / Boston Globe Media** (founded 1994; 6 employees; "380+" organizations) | MassTrac (legislative tracking), MuniTrac (AI minutes and searchable transcripts, "human edited") and the MassInsider newsletter ([InstaTrac](https://www.instatrac.com/)). Bought by the Globe in July 2026 to "expand reporting on local communities across Massachusetts" ([Boston Globe](https://www.bostonglobe.com/2026/07/16/business/boston-globe-media-acquires-instatrac/)) | After the meeting: the clerk uploads the agenda and video, and a transcript comes back in about 24 hours ([InstaTrac blog](https://instatrac.com/blog/transforming-agendas-into-actionable-records-with-munitrac)) | Massachusetts-only; Everett is the only named municipal client |
| **Shovels / ReZone** ($5M seed, 2025) | Decisions API: "600+ cities," about **200,000 decisions, up from about 20,000** at the ReZone deal (Jan 2026). Each decision links to property, applicant, owner and contractor. Statuses are "coming soon" ([Decisions API](https://www.shovels.ai/blog/decisions-api-launch/)). Self-serve plans at $599 and $999 a month | "We don't create a decision record until the minutes are posted," often weeks later | No Massachusetts or New England mention found |
| **SitePath Intelligence** | Every US county graded for solar, storage and data-center siting: moratoria with resolution number and vote, ordinance text, approved and denied projects. "Every figure cited to a primary document." Seat-priced, demo first ([SitePath](https://www.sitepathintel.com/)) | After the action, from primary documents | Massachusetts county pages show no tracked energy meetings. Lee was listed with "no active moratorium" despite a BESS moratorium hearing on Apr. 27, 2026 ([Lee hearing notice](https://leema.gov/DocumentCenter/View/4860/)) |
| **Heatmap Pro** | Opposition Risk Scores for every county and ZIP code, contested projects and local laws, "updated daily using local news coverage... and regular phone calls to all 3,100+ U.S. counties" ([Heatmap Pro](https://heatmap.news/pro)) | When news covers an item or a call reaches it | County and ZIP grain; Massachusetts towns are not its unit |

Other players matter at the edges. **GovSpend** shows that daily agenda and packet scraping works at national scale, and its own statement that only "around 40–50 percent of agencies provide video and audio meeting recordings" is the best evidence that video-first tools structurally miss half of all boards ([GovSpend](https://support.govspend.com/data-over-meeting-intelligence)). Its buyers, though, are vendors selling to government, not developers. **Starbridge** raised a $42M Series A, monitors "320,000+ public sector entities," and is hiring for sales rather than land-use data ([Starbridge jobs](https://jobs.ashbyhq.com/starbridge)). **MultiState** has a page specifically about monitoring Massachusetts local government, using human analysts across 4,850+ jurisdictions ([MultiState](https://www.multistate.us/solutions/monitor-local-government-activity-in-ma)). That makes "no one monitors Massachusetts towns" unsafe even though its depth is unknown. **OrdinanceWatch** covers only Florida and Georgia ([OrdinanceWatch](https://ordinancewatch.com/index.php/what-we-monitor/georgia)). Paces, LandGate and Enverus sell site-selection data to the same developers and are better treated as buyers than competitors.

The single most consequential fact here is the Globe deal. InstaTrac already holds municipal clerk relationships, lobbyist and newsroom customers and an AI transcript pipeline, and its new owner has the state's largest news distribution. It still works from video uploaded after the meeting, and there is no evidence that it structures clean-energy or land-use data, links records to parcels or serves developers. Those are exactly the gaps 351 Watch fills.

## Bans were one siting event in seven; the market is every permit

A product built around bans would miss most of what developers track. Over about 52 days, the 24-town pilot surfaced 59 distinct siting events. Only **8 were moratoria** (3 BESS, 5 data center). The rest:

- 13 solar or BESS project-permit items covering 14 projects;
- 11 energy-siting bylaw rewrites;
- 8 Chapter 40B comprehensive permits;
- 5 data-center zoning items;
- 2 wireless items;
- 11 other zoning changes.

Project permits and bylaw rewrites outnumbered moratoria about six to one ([pilot agenda hits](<../projects/351watch/data/agenda_hits.json>)). The statewide crawl tells the same story. Topic tags of the 882 hits ran zoning or bylaw amendment 357, solar 235, BESS 142, 40B 115, and moratorium only 77.

The AG record weakens the case for a ban-focused pitch further. Town solar and BESS moratoria do not survive review, so the rules that actually bind projects are the regulating bylaws the AG approves 96% of the time, with specific provisions struck. A developer needs to know which provisions are in force, not merely that a ban was proposed. Moratoria still matter in three places: data centers, where the AG approves them; cities, whose ordinances never reach the AG; and the months of delay before a ruling. Nationally, new anti-renewable restrictions are falling, from 165 in 2023 to 112 in 2024 to 70 in 2025, while data-center measures climb ([Sabin Center](https://oppositionreport.org/reports/current/); [Savrn tracker](https://savrn.com/data-center-moratorium-tracker)).

The fuller Massachusetts market is large in event count, though moderate in money. Figures marked EST are estimates whose method is described in the notes behind this report.

| Measure | Count | Source and date |
|---|---|---|
| Municipalities hosting a siting-relevant solar project (≥500 kW, not rooftop) or ≥1 MW Clean Peak storage unit | **169 of 351 (48%)** | DOER SMART and CPS lists, Jun–Jul 2026 ([qualified units](https://www.mass.gov/info-details/lists-of-qualified-generation-units)) |
| SMART 1.0/2.0 siting-relevant solar | 355 projects, 985 MW, 145 towns (66 not yet operating) | DOER, Jun 1, 2026 |
| SMART 3.0 siting-relevant pipeline | 78 projects, 187 MW, 60 towns (56 with a storage adder) | DOER, Jul 7, 2026 |
| Clean Peak qualified storage | 149 units, 748 MW, 102 towns | DOER CPS list, Jul 1, 2026 ([CPS list](https://www.mass.gov/doc/clean-peak-qualified-units-list-7126/download)) |
| ISO-NE active MA queue | 17 standalone BESS (4,430 MW), 4 offshore wind, no MA solar; 184 MA withdrawals since Jan 2025 | Downloaded Oct 10, 2026 ([ISO-NE IRTT](https://irtt.iso-ne.com/reports/external)) |
| Energy Facilities Siting Board (EFSB) | 12 open dockets; **zero** consolidated-permit applications as of Aug 10, 2026 | ([EFSB dashboard](https://www.mass.gov/info-details/efsb-permitting-dashboard)) |
| Commercial solar/BESS wetlands filings | 36 filings in 24 towns over 12 months. New Leaf Energy is behind at least 9 | MassDEP WIRe, Oct 2025–Sep 2026 ([WIRe](https://eeaonline.eea.state.ma.us/portal#!/search/wire)) |
| Distinct solar/storage projects before a local board each year | **~120–250 (EST)** | Crawler, SMART and wetlands triangulation |
| Solar/storage agenda appearances per year | **~800–1,200 (EST)** | Crawler extrapolation |
| Towns holding energy-bylaw hearings in the next 12 months | **~100–250 (EST)**, a one-time wave driven by 225 CMR 29 | Crawler (11 of 24 pilot towns in 52 days) |
| Municipalities with data-center moratoria, bans or zoning in 2026 | **19 identified, a floor** | Crawler and press |
| 40B comprehensive permits with hearings per year | ~150–250 (EST) | Crawler extrapolation |
| MBTA Communities | 157 of 177 compliant; the rezoning wave is mostly over | EOHLC, Aug 31, 2026 ([MBTA Communities](https://www.mass.gov/info-details/multi-family-zoning-requirement-for-mbta-communities)) |

Timing is shifting what customers need. Under the 2024 Climate Act, towns had to begin accepting consolidated local permit applications for projects under 25 MW or 100 MWh by October 1, 2026. They must decide within 12 months of a complete application, or the project is approved by default. Projects above those thresholds go to the EFSB on a 15-month clock ([Foley Hoag](https://foleyhoag.com/news-and-insights/blogs/energy-and-climate-counsel/2026/june/siting-battery-storage-in-massachusetts-a-new-regulatory-landscape/)). That explains why the pilot found Northampton, Westford, Sturbridge, Amherst, Great Barrington, Charlton, Pittsfield and Westfield all rewriting energy bylaws within the same six weeks.

The bylaw wave should fade in 2027. What follows is steadier and more valuable: hundreds of permit clocks running in local boards, where a missed hearing now has statutory consequences. Data centers add a second track. A September 8, 2026 executive order requires projects over 25 MW of peak demand to obtain a host-community benefits agreement before state permitting, which moves that decision to select boards and city councils ([WBUR](https://www.wbur.org/news/2026/09/08/proposed-data-centers-local-approvals-healey-massachusetts)).

The buyer list is concrete. The target file names **92 companies**:

- 63 solar and storage firms, 54 of which have three or more siting-relevant Massachusetts projects;
- 14 data-center operators or developers;
- 4 law firms;
- 6 consultants;
- 4 transmission or wind companies;
- 1 tower company.

Every row carries a public evidence link and no personal data ([target companies](<../research_notes/Meeting monitor deep dive/ma_target_companies.csv>)). The largest by project count are Nexamp (63), Borrego (43), NextGrid (34), BlueWave (28), Grid Builders (28), Clearway (26), Kearsarge (26) and AES (23). Three companies appear both in state lists and in the pilot's agenda hits (Parallel Products, Kearsarge and New Leaf), which confirms that state program lists name the same applicants who show up at local boards.

The "payor" field on wetlands filings is a hidden gem. It identifies the firm behind a single-project LLC: Beals and Thomas pays for four filings, Farland Corp for three Parallel Products canopies, and Kimley-Horn for ReWild. That is exactly the link a monitor needs to tie an anonymous "Golden Pond Solar 1, LLC" agenda line to a paying customer. Attorneys and consultants are under-sampled; the full Massachusetts land-use bar and engineering field is likely over 100 firms (EST). An illustrative revenue range, not a forecast, assumes 60 to 120 paying organizations at $200 to $600 a month, which gives roughly **$150,000 to $850,000 in annual recurring revenue** from Massachusetts alone. Shovels' $599 to $999 self-serve plans cap what a self-serve tier can charge, and no price has been tested.

## Completeness, history and entity links outlast AI summaries

Three things are easy to copy. The first is AI summaries, which Citizen Portal publishes free, Hamlet bundles with a free tier and Hamlet TV, and MuniTrac sells to clerks. The second is keyword alerts. The third is lead time, because the towns hand everyone the same five days.

Funded rivals are moving fast. Hamlet says it adds "dozens of agencies each week" ([PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/)). Shovels grew its decisions dataset tenfold in five months ([Shovels](https://www.shovels.ai/blog/decisions-api-launch/)). As an AI summaries and alerts product, 351 Watch is not durable.

Five things are hard to copy, and each draws on evidence from this research.

1. **Collection work in the long tail.** Heatmap phones 3,100+ counties. Shovels' "Project Storm" uses phone calls and formal records requests to reach about 10,000 offline jurisdictions and connected 350+ in under three months ([Project Storm](https://www.shovels.ai/blog/project-storm-how-were-bringing-americas-offline-jurisdictions-online/)). National firms pay for that work only where the return justifies it, and small New England towns with scanned PDFs and vendor-hosted portals come last. Permission from the 64 blocked Massachusetts towns, once obtained, is itself a barrier to competitors.
2. **Massachusetts' legal process.** Town Meeting warrants, AG review, 40B comprehensive permits, conservation-commission orders of conditions and the 225 CMR 29 permit clocks are steps that California-shaped national schemas leave out. Hamlet's API has no body type for a select board, ZBA or Town Meeting.
3. **Backfilled history.** AI makes new summaries cheap but cannot produce the past, and buyers name history as what they paid for (see the acquirer section).
4. **Links to companies and parcels.** That means matching single-project LLCs to their parent firms through wetlands payor fields and roughly 500 LLC names from the SMART and Clean Peak lists, and attaching MassGIS parcel IDs, which mirrors the property-applicant-owner model that Shovels sells.
5. **A visible correction log and sourcing.** SitePath advertises "every figure cited to a primary document" and InstaTrac says "all transcripts are human edited." No source measured the value of community corrections, so the evidence here is thin. It is cheap to build all the same.

| Threat | What it could do | What it would still lack in Massachusetts | Severity |
|---|---|---|---|
| Boston Globe / InstaTrac | Turn MuniTrac and MassTrac into a paid municipal-intelligence product under the Globe brand | Pre-meeting input, land-use structure, parcel links, developer customers | **High** |
| Hamlet | Move from 81 toward 351 at "dozens of agencies each week" | Boards with no video, the MA legal process, posted-time audit | **High** |
| Shovels | Add MA towns to Decisions through Project Storm-style outreach | Records start at posted minutes; statuses not live | Medium-high |
| Citizen Portal | Own search traffic for "town + board + topic" | B2B model, land-use structure | Medium |
| SitePath / Heatmap | Add town-level MA meeting tracking | Town grain; agendas as a source | Medium (also buyers) |
| GovSpend / Starbridge | Already scrape minutes and packets | The developer buyer | Low |

The window is set by how fast the Globe and Hamlet move. Neither has announced an all-351 land-use product, though that is a negative search result rather than proof. The build order follows from this. First, make every claim provable with per-item timestamps. Second, make coverage the published core metric. Third, turn the AG dataset's method (exhaustive collection, structured outcomes, explicit exceptions) into a record of each application's life from filing to hearing, continuance, vote, conditions, AG review and appeal, then backfill it. Fourth, link everything to companies and parcels, so the data bolts onto a buyer's product. The ranked list appears under next steps.

## A dozen states match Massachusetts' agenda rule, but siting power picks the targets

Massachusetts requires notice **48 hours ahead, excluding weekends and holidays**, listing the topics the chair reasonably expects. Posting at the clerk's office is enough; the statute requires no website and no documents ([c. 30A §20](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIII/Chapter30A/Section20)). By that yardstick, about **12 states match or beat Massachusetts on paper**.

- **Stronger:** California (72 hours, agenda linked from the home page), Texas (72 hours, subject of each item, online for cities and counties) and Virginia (three working days, agenda on the website, packets public when members get them) are verified. Nevada, Hawaii, Delaware and New Mexico are stronger by background knowledge only.
- **Comparable:** Rhode Island, Vermont and New Jersey are verified. Illinois and Idaho rest partly on background knowledge.
- **Mixed:** New York and Pennsylvania.
- **Weaker:** New Hampshire, Connecticut, Maine and most of the Midwest and South. Ohio, Michigan and Minnesota require no agenda at all.

All rows, with citations, are in the 50-state table ([state agenda laws](<../research_notes/Meeting monitor deep dive/state_agenda_laws.csv>)). Posting law turns out to be a weaker constraint than it looks. Massachusetts towns post a median of five days ahead against a 48-business-hour rule, and the 27 directly time-stamped agendas in the Northeast probe had a median of 5.35 days. What decides the market is whether towns, rather than a state board, decide projects.

| State | Lead time and agenda rule | Online / documents | Who decides solar and BESS | Vs MA |
|---|---|---|---|---|
| **Rhode Island** | 48 h excl. weekends and holidays; statement of business ([§42-46-6](http://webserver.rilegislature.gov/Statutes/TITLE42/42-46/42-46-6.HTM)) | Every body files electronically with the Secretary of State | Local under 40 MW; storage not state-sited | Closest match; one statewide filing point |
| **Vermont** | 48 h agenda (calendar hours) ([§312](https://legislature.vermont.gov/statutes/section/01/005/00312)) | Website if one exists | **State** PUC certificate; bylaws "shall not regulate" generation or storage ([§4413](https://legislature.vermont.gov/statutes/section/24/117/04413)) | Comparable law, little local decision |
| **New Jersey** | 48 h, agenda "to the extent known" ([OPMA](https://www.nj.gov/njoem/serc/pdf/Open_Public_Meetings_Act_N.J.S.A._10_4-6-21.pdf)) | Website legal notices from Mar 1, 2026 ([NJ Monitor](https://newjerseymonitor.com/2025/07/01/new-jersey-removes-mandate-to-publish-legal-notices-in-newspapers/)); land-use maps and documents on file 10 days before hearings | Local land-use review (conflicting evidence, see below) | Comparable |
| **New York** | 72 h notice; no agenda requirement ([§104](https://www.nysenate.gov/legislation/laws/PBO/104)) | Website; records online 24 h ahead "to the extent practicable" ([§103](https://www.nysenate.gov/legislation/laws/PBO/103)) | Local under 25 MW and standalone BESS; state (ORES) at 25 MW+ ([PSL §137](https://www.nysenate.gov/legislation/laws/PBS/137)) | Mixed |
| **Pennsylvania** | Agenda online 24 h ahead; no action on unlisted items ([Sunshine Act](https://www.palegis.us/statutes/consolidated/view-statute?txtType=HTM&ttl=65&div=0&chapter=7)) | Website | **Fully local**; HB 502 state board stalled in committee since Apr 23, 2025 ([HB 502](https://www.palegis.us/legislation/bills/2025/hb502)) | Weaker lead, stronger online |
| **New Hampshire** | 24 h excl. Sundays and holidays; no agenda ([91-A:2](https://gc.nh.gov/rsa/html/VI/91-A/91-A-2.htm)) | Optional; warrants must go on town websites from Oct 18, 2026 | Local under 30 MW | Weaker |
| **Connecticut** | Agenda filed 24 h ahead ([§1-225](https://portal.ct.gov/FOI/Regulations/The-FOI-Act/Sec-1225--Formerly-Sec-121--Meetings-of-government-agencies-to-be-public--Recording-of-votes--Schedu)) | Local website posting not clearly required | **State** Siting Council above 1 MW ([§16-50x](https://codes.findlaw.com/ct/title-16-public-service-companies/ct-gen-st-sect-16-50x/)) | Weaker |
| **Maine** | "Ample time"; no fixed period, no agenda ([§406](https://legislature.maine.gov/statutes/1/title1sec406.html)) | None required | Local home rule; DEP permit over 20 acres | Weaker |

Market opportunity and ease of entry point in different directions, and both matter. A scoring model across the 48 contiguous states weighted local pipeline (30%), opposition (25%), fragmentation (15%), how much siting stays local (15%), the competitor gap (10%) and 40B-style housing (5%). It used LBNL queue data, EIA planned units, Census counts of governments and Sabin Center restriction counts ([LBNL Queued Up](https://emp.lbl.gov/queued-2026-edition-characteristics-power-plants-seeking-transmission-interconnection-end-2025); [EIA-860M](https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx); [Census of Governments](https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org02.zip); [Sabin Center](https://oppositionreport.org/reports/current/)).

Results:

- **Northeast order:** **Pennsylvania 71.8, New York 63.8, Maine 53.6**, then Massachusetts 50.3, New Jersey 41.8, New Hampshire 34.8, Connecticut 34.2, Rhode Island 30.6 and Vermont 27.1.
- **National top 10:** Pennsylvania, Texas, California, Illinois, Ohio, New York, Michigan, Virginia, Indiana and Minnesota. The first nine stay in the top 10 under all five weightings tested; Minnesota's slot is unstable.
- **Caveat:** the competitor-gap, preemption and BESS-moratorium inputs are judgment calls.

A crawler probe of 48 towns, six per Northeast state, then tested whether the Massachusetts code works elsewhere unchanged ([Northeast results](<../projects/351watch/data/agenda_hits_northeast.json>)).

| State | Towns automated (of 6) | Verdict for the existing code |
|---|---|---|
| Maine | **5** (32 hits) | Works now. CivicPlus with New England board names. Real data-center moratoria in Bangor and Westbrook ([Bangor agenda](https://www.bangormaine.gov/AgendaCenter/ViewFile/Agenda/_09282026-931)) |
| New York | 4 | Fair once "Town Board" is aliased. Clay ZBA BESS setback variance and Lysander data-center moratorium extension found ([Clay ZBA](https://townofclayny.gov/sites/default/files/2026-10/Zoning%20Board%20Agenda%20-%20October%2012%2C%202026.pdf)) |
| Rhode Island | 3 | Fair now, best potential. One Secretary of State portal adapter would cover all 39 municipalities with filed-on timestamps ([RI Open Meetings](https://opengov.sos.ri.gov)) |
| New Hampshire | 3 | Good where reachable, but Cloudflare blocked 3 of 6, including two data-center fight towns |
| New Jersey | 4 (thin) | Weak. eCode360 robots rules and Akamai block towns; township board names are missed |
| Pennsylvania | 3 | Weak for current code, high signal. No CivicPlus; JavaScript document libraries; data-center ordinances everywhere ([Upper Burrell](https://upperburrelltwp.com/wp-content/uploads/2026/10/UBT-BOS-Meeting-Agenda-10-7-2026-.pdf)) |
| Connecticut | 2 | Weak. Heavy blocking; Zoning Commission and Inland Wetlands names are missed ([Harwinton](https://www.harwinton.gov/AgendaCenter/ViewFile/Agenda/_10132026-552)) |
| Vermont | 3 | Weak, and the PUC decides siting anyway |

The recommendation is to take **New York first**. It has the strongest opposition signal in the region: 86 local restrictions and 52 contested projects, the most of any state ([Sabin Center](https://oppositionreport.org/reports/current/)). It is also the center of the BESS-moratorium wave. Carina Energy counted 98 New York moratoria, 65% of a US total of at least 150, in March 2026, though that is a commercial count whose methodology was not reviewed ([Carina Energy](https://www.globenewswire.com/news-release/2026/03/10/3252888/0/en/150-Local-Governments-Have-Moved-to-Block-Battery-Storage-Development-New-Database-Reveals.html)). Towns decide solar under 25 MW and standalone storage, the town-board form of government matches the Massachusetts playbook, and the crawler already works after one alias. New York's law requires no agenda, so the edge depends on the documents posted 24 hours ahead and on local practice (the probe's proxy median was 5.4 days). Citizen Portal already writes New York planning-board stories.

**Maine and Rhode Island** are cheap add-ons rather than markets. Maine runs on the stock code, and Rhode Island needs one portal adapter. Both have small pipelines: Maine has 1.0 GW in transmission queues, and Rhode Island is mainly a 40B-analog housing market.

**Pennsylvania** is the larger second bet: 2,625 general-purpose governments, siting that stays local at any size, 60 local restrictions and 61 data-center measures. It needs real adapter work, and the HB 502 state board must stay stalled.

On this ordering the two lines of evidence disagree. The state-law analysis ranks Pennsylvania, then New Jersey, then New York; the market model and the crawler probe favor New York first. The choice here rests on operational fit and opposition intensity.

**New Jersey** looks like a data-center and housing market, with 119 data-center measures in Savrn's count. Sabin describes state (NJDEP) principal authority over renewables above 0.1 MW, while the statute review found local land-use control with no state preemption, so siting authority must be settled before any energy pitch. Connecticut and Vermont decide energy siting at the state level and are worth adding only for housing alerts.

Nationally, the best fit is the town and township grain that county-level national tools miss. Pennsylvania, Ohio and Michigan all rank in the top seven under every weighting. Ohio's SB 52 lets counties ban wind and solar projects, often prompted by township resolutions ([Bricker Graydon](https://www.bricker.com/insights/publications/Ohio-General-Assembly-passes-S-B-52-Changes-to-wind-and-solar-siting-requirements)). Michigan has the most local restrictions in the US, and its PA 233 framework is still moving through the courts ([Sabin Center blog](https://blogs.law.columbia.edu/climatechange/2026/07/14/michigan-court-of-appeals-decision-largely-upholds-michigan-pscs-renewable-energy-siting-process/)). Both states have weak agenda laws, so the pre-meeting edge must be tested town by town. Illinois offers the best mix of law and hearings: 48-hour online agendas, county hearings required under statewide standards, and the most small planned units in the country ([Taft](https://www.taftlaw.com/news-events/law-bulletins/illinois-clean-and-reliable-grid-affordability-act-enacts-new-statewide-zoning-standards-for-energy-storage-systems/)). Texas, California and Virginia have huge pipelines, but county-level tools fit Texas and Virginia, and California is Hamlet's home market.

## Buyers pay for history and early signal, and the Globe is first in line

Recent buyers in this category described what they were buying in strikingly consistent terms:

- **Early signal:** Shovels bought ReZone in January 2026 for "months of early project visibility" ([Shovels](https://www.shovels.ai/blog/shovels-acquires-rezone/)).
- **History:** the Globe bought something InstaTrac "built... over the last three decades" ([Boston Globe](https://www.bostonglobe.com/2026/07/16/business/boston-globe-media-acquires-instatrac/)). Clio paid about $1 billion for vLex's "1 billion+" legal documents ([LawNext](https://www.lawnext.com/2025/11/clio-completes-historic-1-billion-vlex-acquisition-announces-500-million-series-g-at-5-billion-valuation-plus-exclusive-interview-with-ceo-and-cfo.html)). Enverus bought Energy Acuity's catalogue of "thousands of renewables projects" ([Enverus](https://enverus.com/newsroom/enverus-acquires-energy-acuity-expanding-its-power-and-renewables-offering/)).
- **Customers kept under their own brand:** InstaTrac, ReZone and Nimonik's BillTrack50 all kept their brands and customers ([Pulse 2.0](https://pulse2.com/nimonik-acquires-legination-to-expand-regulatory-and-legislative-intelligence-platform/)).
- **Entry into a new region:** the Warren Group entered New Hampshire and Vermont by buying records collected since 1977 ([Banker & Tradesman](https://bankerandtradesman.com/the-warren-group-purchases-assets-of-real-data-corp/)).

A Massachusetts-complete record of siting decisions is exactly that kind of entry asset for a national player.

| Rank | Likely acquirer | Why it fits | What it would pay for | Main risk |
|---|---|---|---|---|
| 1 | **Boston Globe Media / InstaTrac** | Stated intent to expand local Massachusetts coverage; existing municipal and legislative products; lobbyist and newsroom buyers | Pre-meeting land-use coverage, developer customers, structured clean-energy data | It builds instead of buying |
| 2 | **Shovels** | Already bought a meeting-decisions company; chasing coverage parity with its permit jurisdictions | 351 small jurisdictions arriving with history and parcel links | Its own outreach reaches MA first |
| 3 | **Hamlet** | Funded; sells to developers; already at 81 of 351 | Boards with no video and the clean-energy wedge | Fast organic expansion |
| 4 | **The Warren Group** | Massachusetts records business with roots in 1872; refocused on data in 2018 ([history](https://www.thewarrengroup.com/history-of-the-warren-group/)) | Land-use decisions that come before its deed and mortgage records | Unproven appetite for meeting data |
| 5 | SitePath, Heatmap, LandGate, Enverus, Paces | Same developer buyers. LandGate bought Topos for BESS diligence in Dec 2025 ([PrivSource](https://www.privsource.com/acquisitions/deal/ArSJvr)) | A town-level MA restrictions layer, likely licensed first | Licensing rather than buying |
| 6 | Starbridge, GovSpend | Capital and scrapers in place | Signal data | Wrong buyer |

Price evidence is thin for deals of this size. All four small 2025–26 deals (LandGate–Topos, Shovels–ReZone, Globe–InstaTrac and Nimonik–LegiNation) had undisclosed terms. Prices are disclosed only for scaled targets:

- **Onvia:** $70 million cash, about **2.9 times** revenue of about $24.5 million ([GovConWire](https://govconwire.com/2017/10/deltek-to-purchase-onvia-for-70m-cash)).
- **Glenigan:** £72.9 million, about **6.0 times** revenue and 10.7 times EBITDA (£72.9M ÷ £12.2M revenue and ÷ £6.8M adjusted EBITDA) ([Ascential](https://www.ascential.com/files/content-files/press-releases/sale-of-glenigan-15-12-2020.pdf)).

Applying those multiples to the illustrative Massachusetts revenue range of $150,000 to $850,000 gives roughly $0.4 million to $5 million. Those multiples come from businesses about 20 or more times larger, so the range is a ceiling for illustration, not a valuation.

The closest analogue is InstaTrac itself: 32 years, six employees, Massachusetts only, 380+ customer organizations, sold to the dominant in-state media company rather than a national data firm. The realistic win is a quiet purchase of data, customers and team, priced on how complete and correct the Massachusetts record is. BillTrack50's decade-long partnership with Nimonik before the sale suggests that a licensing relationship is the usual first step.

## Claims ledger: what we can say today and what we must not

| Claim we can make | Evidence | Date |
|---|---|---|
| "We automatically monitor posted agendas in 240 of Massachusetts' 351 cities and towns, home to 73% of residents." | Statewide census ([summary](<../projects/351watch/data/ma_census_summary.json>)) | Oct 10, 2026 |
| "We read agendas for 224 planning boards, 194 zoning boards of appeals and 221 conservation commissions; 235 towns have at least one land-use board covered." | Census per-town file ([towns](<../projects/351watch/data/towns_ma_all.json>)) | Oct 10, 2026 |
| "Massachusetts boards post agendas a median of five days before meetings; 94% are online at least 24 hours before the meeting day." (Describe it as town behavior, not our alert speed.) | 4,116 first postings, 103 towns ([lead-time data](<../projects/351watch/data/leadtime_ma_all.json>)) | Meetings Apr 13–Oct 9, 2026 |
| "We read scanned agendas: a quarter of agendas in our window had no text layer, and we recovered 639 of 641 by OCR; 20% of our hits came from those scans." | Statewide crawl ([hits](<../projects/351watch/data/agenda_hits_ma_all.json>)) | Window Sep 10–Dec 9, 2026; run Oct 10 |
| "We captured October clean-energy items in Pittsfield, Westford, Carver and Sudbury 3–4 days before their meetings, and Westford's Town Meeting article 16 days before." | Pilot crawl, run-level timestamp ([pilot hits](<../projects/351watch/data/agenda_hits.json>)) | Oct 10, 2026 |
| "Since the SJC's *Tracer Lane II* decision (June 2, 2022), the Attorney General has disapproved every solar or battery-storage moratorium she has ruled on: 18 articles in 14 towns, including all 15 from 2024 to 2026." | All 2,719 AG decision letters ([dataset](<../projects/351watch/data/ag_decisions.json>); [portal](https://massago.hylandcloud.com/231publicaccess/MLU.html)) | Through Oct 10, 2026 |
| "From 2022 to 2026 the AG approved 96% of solar and BESS regulating bylaws in whole or in part (109 of 114), usually striking specific provisions." | Same | Through Oct 10, 2026 |
| "Our ledger documents two moratorium disapprovals (Hanson, Hampden) missing from the AG's own 2026 footnoted list." | Same | Oct 10, 2026 |
| "Hamlet lists 81 Massachusetts municipalities plus one county." (Attribute to Hamlet.) | Hamlet coverage page, search-index snippet ([Hamlet](https://www.myhamlet.com/coverage)) | Oct 10, 2026 |
| "In a public-index test of six October 2026 clean-energy agenda items, none appeared in Citizen Portal articles before the meeting, and Carver had no Citizen Portal coverage." (State the method and the date.) | Search-index lookups | Oct 10, 2026; re-check after Oct 20 |
| "SitePath's public Massachusetts county pages show no tracked energy meetings." | SitePath public pages ([SitePath](https://www.sitepathintel.com/)) | Oct 10, 2026 |
| "Shovels says it creates a decision record only after minutes are posted." (Quote it.) | Shovels blog ([Shovels](https://www.shovels.ai/blog/decisions-api-launch/)) | Jun 2026 |
| "GovSpend reports that only 40–50% of agencies post meeting recordings, so video-first tools miss many boards." | GovSpend help center ([GovSpend](https://support.govspend.com/data-over-meeting-intelligence)) | Accessed Oct 10, 2026 |
| "Our crawler identifies itself, limits itself to one request per second per host, and never logs in or solves bot challenges." | Census method | Oct 10, 2026 |

| Claim we must not make | Why not | Safe alternative |
|---|---|---|
| "Competitors only summarize meetings after they happen." | Hamlet's API has agenda-monitoring topics; its marketing promises alerts "the moment agendas are posted"; Citizen Portal published Warwick agenda previews; GovSpend scrapes agendas daily | "We read posted agendas and packets for every land-use board we cover, including boards with no video." |
| "We cover all 351 towns" or "every board." | 240 automated; 111 not; warrants found for 92 of 292 | Publish the live count and a coverage dashboard |
| "We alert N days before every meeting" or "we're faster than Hamlet." | Only run-level timestamps; two test items were read after the meeting; 4% of agendas first appear on the meeting day; competitor timing never observed | State the town-posting statistics; add per-item `first_seen` before any speed claim |
| "Hamlet doesn't cover Massachusetts planning boards." | Chicopee's planning board, ZBA and conservation commission are on Hamlet, as are Boxborough's and Freetown's planning boards | Quote Hamlet's own 81 + 1 count |
| "Citizen Portal doesn't cover town X." | Index searches are lower bounds. Its terms bar competitive use, so no account-based check is possible | Report only dated public-index tests |
| Any claim about competitor alert timing, alert settings or in-app pricing | Never observed; no accounts | None |
| "No one monitors Massachusetts local government." | MultiState has an MA local-monitoring page; InstaTrac's MuniTrac; Citizen Portal | "No monitor we found shows complete coverage of MA land-use boards." |
| "Shovels, SitePath or Heatmap have no Massachusetts data." | Unverified; subscriber views unseen | "We found no public Massachusetts meeting tracking from them as of Oct 10, 2026." |
| "Moratoria are illegal in Massachusetts" or "the AG will strike your moratorium." | Data-center moratoria are approved; city ordinances aren't reviewed; Medway 2022 and Oakham 2023 were approved; it's also a legal prediction | "Since June 2022, every solar or BESS moratorium the AG has ruled on was disapproved," with the exceptions list |
| "Our crawler always honors robots.txt." | Known gaps in `fetch.py`: a robots.txt served as `text/html` is treated as allow-all, and redirects are followed before the target's robots check | Fix first, then claim it |
| "We cover New York, Maine, Rhode Island..." | Only a 48-town feasibility probe | "We have tested our crawler in all Northeast states." |
| Market-size or revenue figures stated as fact | Estimates | Label EST and show the method |
| "Our lead is durable" or "years ahead" | Funded rivals expand weekly; lead time is public | Point to completeness and history metrics |

## Twelve next steps, ranked by proof value

| # | Action | Why it comes here | Who / effort |
|---|---|---|---|
| 1 | Store a per-item `first_seen` timestamp on every hit, and crawl actionable boards every six hours | Every "N days before" claim currently rests on a run-level time | Claude; days |
| 2 | Fix the two robots.txt gaps in `fetch.py` (HTML-typed robots.txt treated as allow-all; redirects followed before the robots check) | A public claim and a legal-risk control; must precede scaling | Claude; hours |
| 3 | Correct `tracker.json` (Lee and Sturbridge disapproved; Hampden passed and disapproved), publish the AG ruling ledger with its exceptions, and refresh it monthly from the portal's date search | The strongest "answers" proof and a free marketing page | Claude; days, plus lawyer review of the wording |
| 4 | Request permission or allow-listing from the 64 bot-protected towns and vendors, largest first: Worcester, Cambridge, Framingham, Revere, Newton, Brookline, New Bedford, Lynn; MyTownGovernment (14 towns), HeyGov, iQM2/Granicus. Test a fixed, allow-listed IP address | 1.10 million residents and the hardest-to-copy part of coverage | Owner sends; Claude drafts; weeks |
| 5 | Add `data_center` and `ev_charging` topics, an LLC watch-list of about 500 SMART, Clean Peak and wetlands names, conservation-commission priority, and abutter-town notices | Catches anonymous LLC agenda lines and the fastest-growing siting topic | Claude; days |
| 6 | Add the MassDEP wetlands Data Lake API as a second daily feed | Free, public, independent of town websites; the payor field links LLCs to parent companies | Claude; days |
| 7 | Publish a public coverage dashboard (towns × boards × last successful crawl) | Turns the breadth claim into something a buyer can check | Claude; 1–2 weeks |
| 8 | Build the decision-lifecycle schema and backfill it, starting with solar and BESS in the 169 host towns | The asset buyers pay for and rivals can't produce quickly | Claude; months |
| 9 | Run a paid pilot with 10–15 buyers from the 92-company list (for example Kearsarge, NextGrid, BlueWave, Nexamp, New Leaf, Parallel Products; Foley Hoag, Pierce Atwood; Beals and Thomas, Farland). Test price against Shovels' $599–999 anchor | No demand or price has been tested | Owner; 4–8 weeks |
| 10 | In a normal browser, open Hamlet's Massachusetts coverage page and terms, and book a sales demo to ask about select boards, ZBAs, conservation commissions, warrants and alert lead time. Re-search the six test items after Oct 20. Do not use Citizen Portal for benchmarking | Closes the biggest competitor unknown within the rules | Owner; 1–2 hours |
| 11 | Northeast: move board aliases into `boards.py`, build the Rhode Island Secretary of State adapter, run a New York pilot of about 50 towns drawn from the 2026 BESS-moratorium list, and verify New Jersey's siting authority and all background-knowledge statute cells | Cheapest proof that the method travels | Claude; weeks |
| 12 | Once the dashboard and history exist, open a licensing or data-feed conversation with one likely buyer (the Globe/InstaTrac or Shovels) | Partner first, sell later, as BillTrack50 did | Owner; later |

## What we could not verify

| Gap | What happened | Effect on conclusions |
|---|---|---|
| Hamlet | Every myhamlet.com page, including its terms, coverage and careers pages, returned a Vercel bot checkpoint (HTTP 429). The GovCenter host is gone (404). No account was created | MA per-town list, alert timing and prices are unseen. 22 sample towns are "unknown," not negative |
| Citizen Portal | Cloudflare 403. Its terms, as indexed, bar building a competing product | Coverage counts are lower bounds; no account-based testing allowed |
| Search and archives | DuckDuckGo flagged the egress IP after about 8 queries; the Wayback Machine and Common Crawl were unreachable; Austin Bulldog and Kingscrowd blocked | Hamlet team size, "about 20 customers" and the $49 plan are reported only |
| Statute sites | cga.ct.gov (503/TLS), ilga.gov and California leginfo failed | Connecticut's P&Z notice rule is unverified; IL and CA rest on secondary copies |
| State data | MEPA eMonitor API returned 403 (its embedded key was not extracted); mass.gov info-details pages refuse automated requests; Data Center Watch state data is paywalled | No ENF counts; data-center opposition is national only |
| Massachusetts towns | 64 bot-protected; 21 with no dated listing; lead-time stamps exist for only 103 towns, mostly CivicPlus | Coverage and lead-time figures omit those towns |
| Northeast towns | 9 of 48 behind Cloudflare or Akamai; 5 robots disallows; only 6 towns per state | Feasibility verdicts are directional |
| Estimates | Annual projects, agenda appearances, bylaw-hearing towns, 40B and wireless volumes, revenue range, Texas zoning units, competitor-gap, preemption and BESS scores | Use as ranges, never as facts |
| Background-knowledge statute cells | Most non-Northeast open-meeting and siting details are marked as from background knowledge, not checked this session | Verify before any state launch |
| Conflicts | New Jersey siting authority (Sabin vs. statute review); expansion order (PA-first vs. NY-first) | Both flagged above |
| Staleness | Sabin and LBNL data are as of Dec 31, 2025; the Carina BESS count is from Mar 2026 | Opposition counts move monthly |

## Conclusion

The research inverts the founding thesis. The edge was supposed to be timing, catching items before the meeting. Massachusetts towns give everyone that timing with five days' notice, and Hamlet already reads agendas. What no rival shows is the combination of every land-use board in every town, with the verdict attached. The AG dataset is the template for the whole product. It collected exhaustively (2,719 letters, not just tagged ones), ended up more complete than the source's own summary, and states its exceptions openly. Repeating that method for planning-board, ZBA and conservation-commission decisions is the product, and an alert becomes a pointer into that record.

The October 1, 2026 deadline also changes what customers will pay for next. The 2026 wave of bylaw rewrites and doomed moratoria is a one-time spike. From 2027 the steady-state need is tracking 12-month permit clocks across hundreds of boards, where a missed hearing has legal consequences, alongside a growing data-center track that the AG does not shield developers from. Because the Globe's purchase of InstaTrac made the main threat and the likeliest buyer the same company, the strategy is to build precisely what InstaTrac lacks: pre-meeting land-use coverage, developer customers, and history linked to companies and parcels. A New York pilot would then show that the method travels.
