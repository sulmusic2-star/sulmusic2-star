# Free and entry tiers of local-government and land-use monitoring tools, and where a new service wins

Prepared 2026-10-12 for the owner of 351 Watch (being renamed). Status: complete for this pass (about 30 searches and fetches, plus the earlier note).

Scope: US only. Public pages only, no accounts. This note builds on `../Product strategy/free_tier.md` and does not repeat its detail. Read that note for the basic LocalGovIndex, Citizen Portal, MyTownView, Hamlet, Notify Me, data-center tracker and Visualping pricing rows. This note adds:
- the full 13-column matrix
- facts checked this session (LocalGovIndex's Civic plan has no pre-meeting preview; Red Tape coverage counts; Colorado notice-alert prices; CivicSearch alert cadence; GatherGov coverage)
- user complaints
- a product-by-product comparison with our free tier

**Labels**
- **[V] verified**: read on the product's own page (or the primary news article) this session.
- **[V-idx]**: the product's own text as quoted by the search index; the page itself was not loaded.
- **[V-prior]**: verified in `free_tier.md` or another earlier note in this repo; the URL is repeated.
- **[S] secondary**: a third-party article, review site, directory or forum post.
- **[E] estimate**: my judgment.

**Our baseline.** Today 351 Watch reads agendas in "240 of 351 in Massachusetts, 33 of 57 in New York and all 39 in Rhode Island", 312 towns in all. It reads every day and covers planning boards, zoning boards, conservation commissions, select boards and councils. Topics are battery storage, solar, data centers, moratoria, 40B housing, cell towers and zoning changes, plus MassDEP wetlands filings. It delivers by RSS/JSON, a calendar feed, and a daily Slack, Teams or Discord message. It needs no account ("the watchlist's private link is its key"), and watchlists are free during the founding beta [V · [351watch.vercel.app](https://351watch.vercel.app/)]. The planned free tier adds:
- email with double opt-in
- full-text search over every agenda read
- the home town plus every town next to it (owner's brief)

---

## 1. Feature-by-feature matrix of free and entry tiers

### Takeaway
- **Every rival that has a free tier fits one of three patterns:**
  - **Recap after the meeting.** Citizen Portal, Red Tape, CivicSearch, Hamlet, Documenters and Patch tell you what happened.
  - **One place or one board.** LocalGovIndex free covers one board; Citizen Portal follows one location; MyTownView keeps alerts on a paid plan.
  - **Keyword tools that don't know agendas.** Google Alerts, Visualping, and newspaper notice searches whose daily email costs money in some states.
- **Only two free products send anything before the meeting:**
  - **LocalGovIndex** emails an agenda summary for one board. Its $9 Civic plan lists only recaps after the meeting and "change alerts", with no preview before the meeting.
  - **Town Notify Me and govDelivery lists** send every agenda for one board. You need an account, and there is no topic filter.
- **No free product combines the five things in our planned free tier:** siting topics only, every board, the neighbouring towns, alerts days before the meeting, and calendar/RSS/Slack delivery without an account.
- **Our free tier loses on three things:**
  - **Breadth.** We read 312 towns in 3 states; Red Tape covers 7,334 governments, GatherGov 9,300+ and MyTownView 23,000+.
  - **Transcripts and video.** We don't offer them.
  - **A mobile app.** We have none.

### Cited Findings

#### Matrix A: scope, timing, delivery, account

| Product (tier) | Places allowed | Boards | Topics | Timing | Delivery channels | Account required | Label · Source |
|---|---|---|---|---|---|---|---|
| **351 Watch, planned free** | Home town + every adjoining town (current coverage: 312 towns in MA, NY, RI) | All the boards it reads (planning, zoning, conservation, select board, council) | Siting only: solar, BESS, data centers, moratoria, 40B/housing, cell towers, zoning changes, wetlands | **Before the meeting**, daily read | Planned: email (double opt-in). Live: calendar, RSS/JSON, Slack/Teams/Discord | **No** | V · [351watch.vercel.app](https://351watch.vercel.app/); plan from owner's brief |
| **LocalGovIndex Free** | "One board or council" | One | Not stated | **Agenda summary before** + recap after | Email only | Sign-in to save places | V · [pricing](https://localgovindex.com/pricing) |
| **LocalGovIndex Civic $9/mo ($90/yr)** | "Any place, official, item, or topic" | Any | Followable topics | **Recap after** each followed meeting; "email change alerts". **No pre-meeting summary is listed** for Civic | Email only | Yes (implied by saving and alerts) | V · [pricing](https://localgovindex.com/pricing) |
| **Citizen Portal free** | "Follow 1 location"; browse meetings at "all 5 levels of government" | All for that location | Search topics; **topic alerts are paid** on the pricing page (the help page says alerts are free with sign-in; conflict unresolved) | After (articles about meetings) | Not stated beyond the site | Yes to follow; "free account never expires", no card | V-idx · [pricing](https://citizenportal.ai/checkoutlifetime); V-prior · [help](https://citizenportal.ai/help) |
| **Citizen Portal Pro $15/mo** | More locations (the $299 one-time plan says "nearly unlimited topics and locations") | All | Topic alerts | After | Alerts (channel not published) | Yes | V-idx · [pricing](https://citizenportal.ai/checkoutlifetime) |
| **MyTownView free** | "Browse all covered municipalities" (23,000+) | Not stated | Not stated | Browsing; a free Sunday "what happened and what's coming up" email (earlier note) | Web; Sunday email | **No** ("doesn't require an account at all") | V · [pricing](https://mytownview.com/pricing); V-prior · [home](https://mytownview.com/) |
| **MyTownView Resident $29.99/yr** | "The town you care about most" | Not stated | "5 custom alerts" | Not stated | Not stated | Yes | V · [pricing](https://mytownview.com/pricing) |
| **Hamlet free** | Free search; 3,000+ governments (Feb 2026); earlier 1.2k+ cities | From video | Search terms | After (video); data refreshed weekly, moving to daily | **No alerts on free** ("real-time notifications" need the 14-day trial) | Not stated | S · [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/), [The Hustle](https://thehustle.co/news/local-government-but-more-accessible-and-hilarious) |
| **GatherGov free** | "9300+ jurisdictions", "live in over 94% of the US population" | Planning meetings, staff reports, permits | Construction pipeline ("Compare us to CoStar, Dodge & Construction Wire") | Pre-construction forecasting; meeting timing not stated | App; "GatherGov Readout" newsletter | Yes ("Start for free" sign-up) | V · [gathergov.com](https://gathergov.com/) |
| **CivicSearch** | 547 cities and towns (US and Canada) | City councils and other bodies in the LocalView data set | 75 policy topics + keyword | After (transcripts) | **Email updates "1–4 times a month"** | Sign-up asks name and ZIP | S · [civictech.guide](https://civictech.guide/projects/civicsearch), [beSpacific](https://bespacific.com/?p=103781) |
| **Red Tape Recordings** | 7,334 governments; 12,019 meetings archived (CA 1,514; UT 891; TX 786; NY 571; FL 560; MA 358) | Any with video | Filters (data centers, housing, warehouses, water …) | After (archived video) | Site-wide RSS `/feed.xml`; "Get Updates" covers **product news, not meeting alerts** | No to look up; yes for "My Saved Items" | V · [home](https://redtaperecordings.com/), [coverage](https://redtaperecordings.com/coverage) |
| **Councilmatic** | Chicago and LA Metro only | Council committees | Bills, people, events | Agenda events posted ahead | Email subscriptions; committee RSS | Yes for email | V-prior · [councilmatic.org](https://www.councilmatic.org/); S · [DataMade 2017](https://datamade.us/blog/councilmatic-notifications/) |
| **Ballotpedia** | 100 largest cities + overlapping counties + state capitals; all local measures in CA and VA | None (elections) | Elections, ballot measures | Election cycle | "More than a dozen newsletters" | No to read | V-prior · [Services](https://ballotpedia.org/Services), [llms.txt](https://apply.workable.com/ballotpedia/llms.txt) |
| **Documenters** (City Bureau) | About 8 cities | Whatever paid note-takers attend | All | After (notes, live posts) | Web, social | No | S · [LA Documenters](https://losangeles.documenters.org/) (V-prior list) |
| **Patch** | 1,100 communities before AI; AI newsletters expanded that to 30,000 | Not structured | General news | Daily newsletter, mostly after the fact [E] | Web, email newsletter (app exists, not verified this session) | Email for the newsletter [E] | S · [Axios 2025](https://www.axios.com/2025/03/04/patch-news-ai-newsletters-local-communities), [CJR](https://www.cjr.org/feature/hyperlocal-ai-patch-newsletter-million-subscribers.php) |
| **Nextdoor** | Your neighbourhood + nearby ones | None structured; "committees … are not qualified" to post as agencies | Whatever neighbours post | Any time | App, email, push | Yes (address-verified account) [E for verification step] | V-idx · [agency FAQ](https://business.nextdoor.com/en-au/publicservices-faq); S · [GetApp](https://www.getapp.com/collaboration-software/a/nextdoor/) |
| **CivicPlus Notify Me** | One town (CivicPlus towns only) | **One list per board** | None (every agenda) | When the clerk posts | Email and/or SMS | **"Sign In" first** | V-prior · [Henry County IN](https://henrycounty.in.gov/List.aspx); S · [Shelter Island NY](https://shelterislandtown.gov/list.aspx) |
| **Granicus govDelivery** | One agency | Per topic list (board or "agendas and notices") | None | When posted | Email, SMS | Subscriber profile by email | S · [Iowa DX guide](https://dxtraining.iowa.gov/govdelivery-mass-communications/govdelivery-subscribing-unsubscribing-and-unsuppressing) |
| **Newspaper legal-notice sites** | Statewide, newspaper notices only | n/a (hearing notices) | Keywords on notice text | Notices run before hearings (MA ≥14 days) | Free manual search everywhere seen. Daily email is **paid** in CO ($75/30 days, $600/yr), AL ("low monthly rate"), MN ("subscription fee") and NM (fee for "expedited delivery"). **Free by statute in ME**; required in IA (cost-recovery fee allowed) | Yes for alerts (CO: password login) | V · [Colorado Smart Search](https://www.publicnoticecolorado.com/SmartSearchSignup.aspx); V-idx · [Alabama](https://alabamapublicnotices.com), [New Mexico](https://newmexicopublicnotices.com/); S · [MNA](https://mna.org/?p=7502); V-prior · [Iowa 618.3A](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf), [Maine §603](https://mainelegislature.org/legis/statutes/1/title1sec603.html) |
| **Google Alerts** | Web-wide | n/a | Any keyword | When Google indexes the page | Email; RSS when signed in | No for email; Google account for RSS | V-prior · [google.com/alerts](https://www.google.com/alerts) |
| **Talkwalker Alerts** (added) | Web, news, X, blogs, forums | n/a | Keyword | "As it happens" | Email, RSS, Slack | Email verification | V-prior · [talkwalker.com/alerts](https://www.talkwalker.com/alerts) |
| **Visualping free** | 5 pages | Whatever page you pick | Any page change (AI filter optional) | Hourly at best (150 checks/mo) | Email, webhooks, Telegram (no Slack/Teams on free) | Yes | V-prior · [pricing](https://visualping.io/pricing) |
| **dcmap.us** | National data centers | n/a | Data centers | Monthly; after announcement | Web, keyless JSON, MCP | No | V-prior · [developers](https://dcmap.us/developers/) |
| **Cleanview free trackers** | National | n/a | Data centers, solar, BESS, wind, gas | After announcement | Web map | No for the map | V-prior · [pricing](https://cleanview.co/pricing) |
| **Electric Choice tracker** | National moratoria | n/a | Data-center moratoria | "Reconciled monthly" | Web page | No | V-prior · [tracker](https://www.electricchoice.com/datacenters/moratoriums/) |
| **Data Center Watch** (10a Labs) | National | n/a | Data-center opposition | Weekly | Substack email; quarterly reports | Email | V-prior · [datacenterwatch.org](https://datacenterwatch.org/) |
| **Town apps** (added; e.g. Gardiner, ME "Gardiner Current") | One town | Town choice | Town choice | When the town pushes | Push | "No account needed" | V-idx · [Gardiner Notify Me](https://www.gardinermaine.gov/Services/Notify-Me) |

#### Matrix B: search, AI, video, app, ads, export, reported accuracy problems

| Product (tier) | Search depth and history | AI summaries | Transcripts or video | Mobile app | Ads | Data export | Accuracy problems users report | Label · Source |
|---|---|---|---|---|---|---|---|---|
| **351 Watch, planned free** | Planned: full text of every agenda read (archive starts when we started reading) | Not in the alert (agenda line quoted) [E: planned design] | No | No (web, calendar, feeds) | No | RSS/JSON feeds | None public yet | V · [351watch.vercel.app](https://351watch.vercel.app/) |
| **LocalGovIndex Free** | "Search every indexed meeting, item, and official"; depth not stated | "Plain-English" recap; AI not stated | Not stated | Not stated | Not stated | "No bulk feed or exports" | **No reviews found** | V · [pricing](https://localgovindex.com/pricing) |
| **LocalGovIndex Civic $9** | Same | Same | Not stated | Not stated | Not stated | "Light exports for personal, civic, and non-commercial use" | No reviews found | V · [pricing](https://localgovindex.com/pricing) |
| **Citizen Portal free** | Search topics and locations; "a few articles a day" | Yes (AI articles) | Links into video; full transcripts on Pro | **No US app found** for citizenportal.ai (other "Citizen Portal" apps are unrelated) | None seen | None seen | An article corrected after first using "lane" instead of "lien" for an ordinance; pages say "AI makes mistakes … refer to the video". A commenter says it "tends towards glossing over issues and relying too much on what officials are saying" | V-idx · [pricing](https://citizenportal.ai/checkoutlifetime); S · [Citizen Portal article via search](https://cpo.soar.com/articles/7513017/Mills/Natrona/Wyoming/Audit-Issues-found-in-draft-articles), [disclaimer via search](https://cp.soar.com/articles/6720514/Lindsay-City/Tulare-County/California/Council-approves-working-items-in-single-consent-motion), [Substack comment](https://jeffinman.substack.com/p/they-all-lie/comments) |
| **MyTownView free** | Browse; 3 AI questions a day | Yes ("Plain-English AI summaries of your meetings" on free town pages) | Mentions transcription and video as data sources only | Not stated | Not stated | None (PDF on Resident, CSV on Pro) | No reviews found | V · [pricing](https://mytownview.com/pricing) |
| **Hamlet free** | "Initial searches" | Yes (video summaries) | Full transcripts are trial or paid | Not found | Not seen | Not stated | No reviews found; refresh is weekly | S · [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/), [TechCrunch](https://techcrunch.com/?p=3073247) |
| **GatherGov free** | "Agent" chat over its knowledge base | Chat agent | Not stated | Web app | Not seen | Not stated | No reviews found | V · [gathergov.com](https://gathergov.com/) |
| **CivicSearch** | Transcript search, recent LocalView content | Topic clustering | Transcripts | No | No | No | Coverage count drifts (547 vs 545) | S · [civictech.guide](https://civictech.guide/projects/civicsearch) |
| **Red Tape** | All 12,019 archived meetings; 11,398 "with a real transcript" | Not stated | **Yes**: video with "clickable deep links", transcripts, agendas | No | Not seen | RSS only | None found | V · [coverage](https://redtaperecordings.com/coverage), [home](https://redtaperecordings.com/) |
| **Councilmatic** | Full legislative history for 2 cities | No | Links to video where available | No | No | Open data | n/a | V-prior · [councilmatic.org](https://www.councilmatic.org/) |
| **Ballotpedia** | Encyclopedia | No | No | No | No | Paid data packages | n/a | V-prior · [Services](https://ballotpedia.org/Services) |
| **Documenters** | Notes archive per city | No (human) | Live posts; some notes | No | No | No | Some city sites last posted in 2025 | V-prior / S · [LA](https://losangeles.documenters.org/) |
| **Patch** | Site search | **Yes**: AI newsletters "built from Patch datasets" and vetted sites | No | Yes (not verified this session) | Ad-supported [E/K] | No | CJR: PatchAM leans on "aggregation, automated event calendars and Nextdoor posts". A reader post says headlines became "junk tabloid style weird news from around the world" | S · [Axios](https://www.axios.com/2025/03/04/patch-news-ai-newsletters-local-communities), [CJR](https://www.cjr.org/feature/hyperlocal-ai-patch-newsletter-million-subscribers.php), [Patch reader post](https://patch.com/california/montrose/what-happened-to-local-news-on-patch) |
| **Nextdoor** | Feed search | Not core | No | **Yes** | Yes (sponsored; an advertiser's 1-star review over a kept ad deposit) | No | Capterra 3.8 (104 reviews, Mar 2026). App reviews say it "won't respect the neighborhood settings and keeps spamming me with notifications for neighboring towns" and that comment notifications "can absolutely flood your email" | S · [Capterra](https://www.capterra.com/p/207178/Nextdoor/reviews?page=3), [GetApp](https://www.getapp.com/collaboration-software/a/nextdoor/), [Kimola App Store roundup (now 410)](https://kimola.com/reports/unlock-nextdoors-user-feedback-insights-challenges-app-store-us-151142) |
| **Notify Me** | Agenda Center archive per town | No | Town's own video, if any | Some towns have their own apps | No | No | Every agenda for the board, with no filter; per board, per town | V-prior · [Henry County](https://henrycounty.in.gov/List.aspx) |
| **govDelivery** | None for subscribers | No | No | No | No | No | Outlook junk rules can send every topic to junk; the footer unsubscribe can drop you from **all topics** or put you on a "do not market list" | S · [Iowa DX](https://dxtraining.iowa.gov/govdelivery-mass-communications/govdelivery-subscribing-unsubscribing-and-unsuppressing) |
| **Legal-notice sites** | Free manual search; history about 12 months (MA, IA) | No | No | No | Some sites carry ads [E] | Print queue (CO) | Covers only legal notices, not agendas or workshops | V · [Colorado](https://www.publicnoticecolorado.com/SmartSearchSignup.aspx); V-prior · [Iowa 618.3A](https://www.legis.iowa.gov/docs/code/2026/618.3A.pdf) |
| **Google Alerts** | n/a (alerts only) | No | No | No | No | RSS | Long-running "misses" complaints: a user who got "20 or 30 alerts a day" now gets "two or three"; Financial Brand: volume "decreased by at least 80 percent"; Computerworld: "a direct Web search" finds what Alerts missed (mostly 2013–2018). A 2026 vendor piece: "returns unwanted results or misses out on important ones" | S · [SE Roundtable](https://seroundtable.com/google-alerts-issues-16470.html), [Computerworld](https://www.computerworld.com/article/1496864/are-google-alerts-dying-a-slow-death.html), [Plagiarism Today](https://www.plagiarismtoday.com/?p=16254), [Contify](https://testwebsite.contify.com/resources/blog/how-does-google-alerts-work-and-why-it-doesnt/) |
| **Visualping free** | 3 months of change history | "AI Summaries" for all users; AI filter | No | Not stated | No | Not on free | G2 (~400 reviews, ~4.6): "false alerts for minor changes"; trouble with "floating components (ads, accept cookie banners, etc.)"; false alerts "when a website fails to load"; free credits "a little difficult" to manage. Capterra has only 2 reviews | S · [G2](https://www.g2.com/products/visualping/reviews), [SaaSworthy](https://www.saasworthy.com/product/visualping-io/reviews), [Capterra](https://www.capterra.com/p/211816/Visualping/) |
| **dcmap / Cleanview / Electric Choice / Data Center Watch** | Current maps; Cleanview has state pages | No | No | No | No | dcmap: keyless JSON (no bulk copying); Cleanview: downloads paid ($9,000/yr) | Counts disagree widely by state (MI: 63 vs 0 vs 20+). Electric Choice calls its count "a floor rather than a precise census" | V-prior · [dcmap](https://dcmap.us/developers/), [Cleanview](https://cleanview.co/pricing), [Electric Choice](https://www.electricchoice.com/datacenters/moratoriums/); V-prior · `../Meeting monitor national expansion/competitor_coverage_map.md` |

#### Others found, with no free resident tier
- **Curate**: AI tracking of minutes, agendas and planning documents from "over 12,000 local government entities". Sold through a reseller; no free tier seen [S · [SoftwareOne listing](https://platform.softwareone.com/product/curate/PCP-9784-4606)].
- **Quorum Local**: paid agenda tracking for "all counties and city populations of 3,000 or greater" [V-idx · [quorum.us](https://www.quorum.us/products/local/)].
- **Stateside Local Government Monitoring**: paid; "three million unique local government webpages" searched daily, with alerts and summaries [V-idx · [stateside.com](https://stateside.com/locality-monitoring)].
- **DIY scrapers**: an Apify actor tracks planning and zoning items in cities that use Legistar [S · [Apify](https://apify.com/tristana/zoning-planning-tracker)].
- **Visualping's own marketing**: it pitches catching "a zoning application appear[ing] on a planning commission agenda two weeks before the hearing", so it is selling itself as a DIY substitute for us [V-idx · [Visualping blog](https://visualping.io/blog/municipal-website-monitoring)].

### Inferences
- [E] **The market splits by timing.** Products with transcripts and AI (Citizen Portal, Red Tape, Hamlet, CivicSearch, Patch) are built on video and arrive after the meeting. Products built on agendas (LocalGovIndex free, Notify Me, govDelivery, Councilmatic) arrive before the meeting but cover one body at a time. Legal-notice sites arrive early but miss workshops, agenda items without a hearing, and moratoria discussed at regular meetings.
- [E] **LocalGovIndex's own ladder makes the case for us.** Its only pre-meeting feature is on the free one-board plan. The $9 plan widens places but lists recaps and "change alerts", not previews. A resident who wants "before the meeting, for every board, plus the next town" cannot buy it there at $9 as described.
- [E] **Free channels are thin across the market.** Outside Talkwalker and town apps, no rival offers free Slack, Teams, Discord or calendar delivery. Red Tape's RSS is site-wide, not per area. Calendar subscriptions appear nowhere in the matrix.

### Gaps
- **Not loaded this session:**
  - Citizen Portal pages (403 before; one article host failed DNS today), so Citizen Portal facts come from the search index.
  - The Patch App Store listing (404) and the Kimola Nextdoor report (410), so app ratings for Patch, Nextdoor and town apps were not read first-hand.
- **Not published:** Hamlet's free search limits; GatherGov's free limits and prices; MyTownView's alert channels.
- **Not checked:** Hamlet, GatherGov and MyTownView mobile apps. None surfaced in search, but the stores were not searched directly.

---

## 2. What users love and hate (reviews, forums, news)

### Takeaway
- **There are almost no public user reviews of the AI civic-meeting startups.** No G2, Capterra, Product Hunt or Reddit reviews surfaced for LocalGovIndex, MyTownView, Hamlet, GatherGov, Red Tape or CivicSearch. That is a sign of small user bases. The loudest evidence comes from residents in news coverage and from reviews of the general tools.
- **Five complaint themes recur:**
  1. finding out too late, often because the agenda was vague
  2. noise and irrelevant alerts
  3. missed items in keyword tools
  4. paywalls and sign-ups on public information
  5. AI summaries that get facts wrong or gloss over them
- **What users love:** ease of use (Visualping), lost pets and local recommendations (Nextdoor), and finding what an official said (Citizen Portal). None of these is the job of knowing about a siting item before the vote.

### Cited Findings

**Finding out too late (the strongest theme in 2026 news)**
- **Spartanburg County, SC (June 15, 2026).** Resident Eric Allison: the agenda "is put out usually four to five days in advance so residents can go over it", but "there was no mention of data centers, moratorium or anything listed in the agenda". He learned of the discussion about 30 minutes before the meeting. Council member Jessica Coker: "there is no requirement for agendas to include specific wording", and agendas "only need to provide enough information about the topic being discussed" [V · [Fox Carolina](https://www.foxcarolina.com/2026/06/17/we-were-shocked-spartanburg-county-residents-criticize-handling-data-center-discussions/)].
- **Kenilworth, NJ.** Residents said the board advanced an AI data-center proposal "without providing ample notice"; some living nearby "got no notification" [S · [News12 NJ via search](https://newjersey.news12.com/anger-boils-over-as-kenilworth-moves-ahead-with-ai-data-center-proposal)].
- **Granville Township, PA (2026).** A supervisor said individuals knew of data-center talks for 19 days before the supervisors did [S · [Lewistown Sentinel via search](https://www.lewistownsentinel.com/news/local-news/2026/06/residents-demand-answers-on-granville-data-centers/)].
- **Wrightstown, WI.** An advocacy petition says the developer contacted village officials from January 2026 while residents heard nothing. Voters rejected the project on Aug 11, 2026 (one-sided source) [S · [change.org](https://www.change.org/p/require-transparency-on-wrightstown-s-data-center-deals)].
- **League City, TX (2024).** "A yard sale-like sign is how most residents found out" about a proposed battery-storage facility [S · [ABC13 via search](https://abc13.com/post/league-city-residents-proposed-battery-storage-facility-council-vote/14515634/)].

**Noise and irrelevance**
- **Nextdoor:** the app "won't respect the neighborhood settings and keeps spamming me with notifications for neighboring towns". Commenting triggers a notification "for every other comment … which can absolutely flood your email". Other reviews: "Worse than social media!!" and comments with "peoples opinions rather than relevant info" [S · [Kimola roundup via search](https://kimola.com/reports/unlock-nextdoors-user-feedback-insights-challenges-app-store-us-151142), [GetApp](https://www.getapp.com/collaboration-software/a/nextdoor/), [Capterra](https://www.capterra.com/p/207178/Nextdoor/reviews?page=3)].
- **Visualping:** false alerts from ads, cookie banners and pages that fail to load [S · [G2](https://www.g2.com/products/visualping/reviews)].
- **Patch:** a reader complains of "junk tabloid style weird news from around the world" and copied press releases, and says they may unsubscribe [S · [Patch reader post](https://patch.com/california/montrose/what-happened-to-local-news-on-patch)].
- **Notify Me:** sends every agenda for a board with no topic filter, so a resident watching for one siting item gets every routine agenda [V-prior · [Henry County](https://henrycounty.in.gov/List.aspx)].

**Missed items**
- **Google Alerts:** sharp drops in alert volume, and items a manual search finds but Alerts never sent [S · [SE Roundtable](https://seroundtable.com/google-alerts-issues-16470.html), [Computerworld](https://www.computerworld.com/article/1496864/are-google-alerts-dying-a-slow-death.html)]. Mostly 2013–2018 evidence; current reliability is unconfirmed.
- **Agenda timing:** in MA, the 10th-percentile agenda posts 2 days ahead and 4% first appear on the meeting day [V-prior · `../Product strategy/where_we_win.md`].

**Paywalls and sign-up friction**
- **Colorado notices:** "Individual manual searches are free", but daily email results cost $75 for 30 days or $600 a year, with a password login [V · [publicnoticecolorado.com](https://www.publicnoticecolorado.com/SmartSearchSignup.aspx)].
- **Citizen Portal:** "a few articles a day" free; topic alerts and transcripts on Pro at $15/mo [V-idx · [pricing](https://citizenportal.ai/checkoutlifetime)].
- **MyTownView:** alerts start at $29.99/yr [V · [pricing](https://mytownview.com/pricing)].
- **Hamlet:** notifications only in the trial [S · [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/)].
- **Notify Me:** "Sign In" is step 1 [S · [Shelter Island](https://shelterislandtown.gov/list.aspx)].
- **govDelivery:** the footer unsubscribe can drop all topics or add a "do not market list" entry [S · [Iowa DX](https://dxtraining.iowa.gov/govdelivery-mass-communications/govdelivery-subscribing-unsubscribing-and-unsuppressing)].

**AI accuracy**
- **Citizen Portal:** a corrected "lane"/"lien" error, and its own disclaimer "AI makes mistakes … please refer to the video". A commenter says it glosses over issues and leans on officials' framing [S · [via search](https://cp.soar.com/articles/6720514/Lindsay-City/Tulare-County/California/Council-approves-working-items-in-single-consent-motion), [Substack comment](https://jeffinman.substack.com/p/they-all-lie/comments)].
- **Medway, UK (outside US scope; shows the risk only):** a council's AI search gave wrong answers on basic democratic information [S · [localauthority.news](https://www.localauthority.news/medways-new-ai-search-fell-over-almost-immediately/)].

**What users love**
- **Visualping:** praised for ease of use and reliability (G2 about 4.6) [S · [G2](https://www.g2.com/products/visualping/reviews)].
- **Nextdoor:** local recommendations, lost pets and selling items [S · [Capterra](https://www.capterra.com/p/207178/Nextdoor/reviews?page=3)].
- **Citizen Portal:** an endorsement praises finding what each official said on an issue [S · [Latter-day Saint Magazine via search](https://latterdaysaintmag.com/be-an-informed-citizen-the-ideal-tool-for-discovering-unbiased-sources-regarding-elected-officials/)].
- **Town apps:** "no account needed" push is a selling point [V-idx · [Gardiner](https://www.gardinermaine.gov/Services/Notify-Me)].

### Inferences
- [E] **The complaint that matters most for us is "too late", and it has two causes.**
  - **Cause 1: people did not see a posted agenda.** We fix this by reading every board and pushing the item days before the meeting.
  - **Cause 2: the agenda never named the topic** (Spartanburg). We cannot fully fix this. We can reduce it by flagging generic items such as "zoning text amendment", "development agreement" or "executive session re: land acquisition", and by reading packets and minutes where posted.
- [E] **Nextdoor users already resent neighbouring-town alerts.** Our free "town + neighbours" default must stay relevant: siting items only, clearly labelled "next door in [Town]", and easy to remove per town.
- [E] **AI-error complaints are an opening.** If every alert quotes the agenda line word for word and links the source PDF, we avoid the failure users report, even if we later add AI summaries.

### Gaps
- **Reddit:** no r/localgovernment, r/urbanplanning or town-subreddit threads surfaced through the search tool, and Reddit was not fetched directly.
- **Facebook groups:** need an account, so they were not read.
- **Product Hunt:** no matching launches were found for these civic tools.
- **App stores:** listings for Patch and Nextdoor could not be read first-hand (404/410), so star ratings are missing apart from Capterra's 3.8 for Nextdoor.
- **Reviews of the AI civic startups:** none found for LocalGovIndex, MyTownView, Hamlet, GatherGov, Red Tape or CivicSearch. Treat their accuracy as untested rather than good.

---

## 3. How our free tier beats each one, and where it does not

### Takeaway
- **We win on timing, scope inside our area, channels and friction.** That means before the meeting, every board, the neighbouring towns, siting only, calendar/RSS/Slack/Teams/Discord/email, and no account.
- **We lose on:**
  - **breadth:** 312 towns in 3 states against national rivals
  - **depth:** no transcripts, no video, no recaps of what was decided
  - **topics:** siting only, so no budgets or schools
  - **mobile:** no app or push
  - **speed:** a daily read, against Visualping's hourly checks and Google's "as it happens"
  - **vague agendas:** we cannot flag what the agenda doesn't say

### Cited Findings and comparison
(Facts are from §1; each verdict is an estimate [E].)

| Rival | Where our free tier is clearly better [E] | Where it is not [E] |
|---|---|---|
| **LocalGovIndex free / $9** | Free has 1 board by email; we have every board in home + adjoining towns, filtered to siting, with calendar, RSS and chat delivery and no sign-in. The $9 plan lists recaps and "change alerts" but no preview before the meeting [V · [pricing](https://localgovindex.com/pricing)] | National breadth ("2,600+" in its data-center dossier, V-prior); all topics; a recap after the meeting; officials and companies as follow targets |
| **Citizen Portal** | 1 location and "a few articles a day" against our multi-town area with no cap; alerts before the meeting, not stories after it; no account; source-quoted items instead of AI prose with known errors | Five levels of government nationally; transcripts and video links; "what was said" by each official |
| **MyTownView** | Free alerts (theirs start at $29.99/yr for 5); before the meeting; feeds and chat delivery | 23,000+ places; budgets, scorecards, AI chat; a free Sunday digest already exists |
| **Hamlet free** | Alerts on free (theirs need a trial); daily rather than weekly; built on agendas, so earlier | 3,000+ governments; video and transcript search |
| **GatherGov free** | Resident-oriented; no account; before the meeting; neighbour logic | 9,300+ jurisdictions; permits and staff reports; construction-pipeline forecasting for professionals |
| **CivicSearch** | Topic alerts before the meeting versus updates 1–4 times a month after it; boards beyond councils (planning, ZBA, conservation) | 547 cities with spoken-word transcripts; national |
| **Red Tape** | Alerts per area (theirs is site-wide RSS and product news); agendas before the meeting; siting filters on every board | 7,334 governments; 11,398 transcripts; video deep links; a deep archive |
| **Councilmatic** | Covers small towns; Councilmatic is in 2 cities | Full legislative history in Chicago and LA |
| **Ballotpedia** | Different job (land use versus elections); covers small towns | Elections and ballot measures; huge newsletter reach (600k+ subscribers, V-prior) |
| **Documenters** | Every meeting in the area, automatically, before it happens | Human notes on what happened; trusted local reporters |
| **Patch** | Structured, sourced siting items, not aggregation; no ads | A mobile app; general news; a big email audience |
| **Nextdoor** | Facts from the source, not neighbour hearsay; neighbour-town items filtered to siting only; no ads | The conversation and organising happen there; app and push; where 52% of adults get local news via forums/groups (V-prior Pew) |
| **Notify Me / govDelivery** | One link for every board in several towns, versus one sign-in per board per town per vendor; topic filter; calendar; unsubscribe per watch | Official source, posted at the moment the clerk posts; SMS; covers non-siting notices |
| **Legal-notice sites** | Free alerts (theirs are paid in CO, AL, MN, NM); agenda items that never get a legal notice (workshops, moratorium discussions, consent items) | Hearing notices often run ≥14 days ahead, earlier than agendas; free statutory alerts in ME (and IA, where a cost-recovery fee is allowed) |
| **Google Alerts** | Reads PDFs whether or not Google has indexed them; knows the board, date and town; fewer misses on unindexed agendas [E] | Unlimited keywords on the whole web; "as it happens" |
| **Visualping free** | No page-picking; no false alerts from cookie banners; dozens of boards across several towns versus 5 pages; Slack/Teams free | Hourly checks; watches any page, not just agendas |
| **Data-center trackers** | Before adoption (agenda stage) rather than monthly after it; every siting topic, not only data centers; the local board level | National totals and maps; moratorium counts; machine-readable JSON (dcmap) |

### Inferences
- [E] **Our clearest, defensible win** is the one cell no rival fills: **before the meeting × every board × neighbouring towns × siting-only × no account × calendar/chat channels**.
- [E] **Our biggest weakness is coverage, not features.** A resident outside the 312 towns gets nothing, while Red Tape, MyTownView, Citizen Portal and GatherGov show something for most US places. A visible "is my town covered? request it" path matters more than any feature.
- [E] **We should not compete on transcripts.** Point to Red Tape or Citizen Portal for what was said, and own the job of knowing before the vote.

### Gaps
- No head-to-head test was run (for example, the same town and week in LocalGovIndex free versus 351 Watch), because accounts were out of scope.
- LocalGovIndex's per-town coverage list is not public. Whether it reads small New England towns is unknown.

---

## 4. Five user complaints to turn into reasons to choose us

### Takeaway
- **Each complaint below is documented in §2.**
- **Each answer uses a feature already live or planned in our free tier.**
- **Each claim needs a caveat** so we don't overpromise.

### Cited Findings and proposed answer

| # | Complaint (evidence) | Reason to choose us [E] | Caveat to state honestly [E] |
|---|---|---|---|
| 1 | **"We found out too late."** Spartanburg resident learned 30 minutes before; Kenilworth neighbours "got no notification"; League City residents learned from a "yard sale-like sign" [V · [Fox Carolina](https://www.foxcarolina.com/2026/06/17/we-were-shocked-spartanburg-county-residents-criticize-handling-data-center-discussions/); S · [News12](https://newjersey.news12.com/anger-boils-over-as-kenilworth-moves-ahead-with-ai-data-center-proposal), [ABC13](https://abc13.com/post/league-city-residents-proposed-battery-storage-facility-council-vote/14515634/)] | **"Know before the vote."** Every board, read daily, flagged the day the agenda posts, with a "posted N days before the meeting" stamp and a calendar entry | Only as early as the town posts; MA's 10th percentile is 2 days ahead and 4% appear on the day (V-prior). Vague agendas can't be flagged reliably, so also flag generic land items |
| 2 | **"It's all noise."** Every agenda from every board (Notify Me); Nextdoor "spamming me with notifications for neighboring towns"; Visualping false alerts; Patch "junk" [V-prior · [Notify Me](https://henrycounty.in.gov/List.aspx); S · [GetApp](https://www.getapp.com/collaboration-software/a/nextdoor/), [G2](https://www.g2.com/products/visualping/reviews), [Patch](https://patch.com/california/montrose/what-happened-to-local-news-on-patch)] | **"Only siting items, only near you."** Topic-filtered items, one daily digest, neighbour items labelled "next door in [Town]" and removable per town or topic | Topic matching will have false positives (for example "solar" in a library roof item); publish how matching works |
| 3 | **"Public information behind a paywall."** CO notice alerts $75/30 days; Citizen Portal "a few articles a day"; MyTownView alerts $29.99/yr; Hamlet alerts only in a trial [V · [Colorado](https://www.publicnoticecolorado.com/SmartSearchSignup.aspx), [MyTownView](https://mytownview.com/pricing); V-idx · [Citizen Portal](https://citizenportal.ai/checkoutlifetime); S · [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/)] | **"Free for your town and its neighbours, for good."** Every board, every channel, full-text search, never delayed on purpose. Paid is for professionals watching many areas | Say so in writing ("free tier will not be cut back for residents") only if the owner commits |
| 4 | **"Sign up per board, per town, per vendor; then the unsubscribe wipes everything."** Notify Me "Sign In" first, one list per board; govDelivery footer unsubscribe drops all topics; Colorado password login [V-prior · [Henry County](https://henrycounty.in.gov/List.aspx); S · [Shelter Island](https://shelterislandtown.gov/list.aspx), [Iowa DX](https://dxtraining.iowa.gov/govdelivery-mass-communications/govdelivery-subscribing-unsubscribing-and-unsuppressing); V · [Colorado](https://www.publicnoticecolorado.com/SmartSearchSignup.aspx)] | **"One link, no account."** One watch covers every board in several towns, whatever vendor each town uses. Email by double opt-in; one-click unsubscribe per watch; calendar, RSS and Slack/Teams/Discord without any sign-up | The private link is the key; split read and manage links before people share it (see `free_tier.md` §4) |
| 5 | **"The AI summary got it wrong."** Citizen Portal "lane"/"lien" correction and "AI makes mistakes" disclaimer; "glossing over issues"; Google Alerts and Visualping missing or misfiring [S · [Citizen Portal via search](https://cp.soar.com/articles/6720514/Lindsay-City/Tulare-County/California/Council-approves-working-items-in-single-consent-motion), [Substack](https://jeffinman.substack.com/p/they-all-lie/comments), [Computerworld](https://www.computerworld.com/article/1496864/are-google-alerts-dying-a-slow-death.html), [G2](https://www.g2.com/products/visualping/reviews)] | **"The town's own words, with the link."** Each alert quotes the agenda line word for word, names the board, date and page, and links the source PDF. A public coverage page shows which towns were read and when | We are still a machine reader. Show "verify with the town" and a one-click "report a miss or error" |

### Inferences
- [E] **Lead with #1 and #3 in marketing.** They are the emotional and economic reasons, and the 2026 data-center coverage keeps producing new "found out too late" stories.
- [E] **#2 and #4 are reasons to stay.** They show up in the first week of use.
- [E] **#5 is a reason to trust us.** It is what journalists and town committees will check first.
- [E] **Our breadth gap risks a sixth complaint ("my town isn't covered").** Pre-empt it with a coverage map, a "request my town" button, and an honest count on the home page, as the site already does ("240 of 351").

### Gaps
- Whether residents actually prefer verbatim agenda lines to AI summaries is untested; no user interviews were done.
- A free-forever promise is a business decision, not a research finding.
