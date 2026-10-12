# Cheap, legitimate routes to township and county siting coverage

*Run 2026-10-12 by a research agent for 351 Watch. Builds on [coverage_feasibility.md](../Meeting%20monitor%20national%20expansion/coverage_feasibility.md) (county census, vendor blocks) and uses its census CSV for per-state counts.*

**Hard limit honoured throughout.** No robots.txt overrides, no challenge solving, no headless browsers, no proxies, no spoofed user agents, no terms violations, no accounts or signups. When a site blocked our bot (403, Cloudflare challenge, connection reset), I did not retry it through another tool. I used search-result summaries instead and labelled them secondary.

**Labels.**
- **verified**: fetched this session with the crawler's own `PoliteFetcher`, or read directly from the cited page. The fetcher uses the 351WatchBot UA, checks robots.txt on every hop, waits at least 1.05 s between requests to a host, and makes no logins and no POSTs.
- **secondary**: a web-search summary or a third-party page I did not fetch myself.
- **estimate**: my inference.

---

## Summary

1. **The cheapest big lever is the county or regional planning body that already sees township zoning by statute.** Five of the six township states send township zoning to a county body, either for review or because the county decides:
   - **PA:** the county planning agency gets amendments at least 30 days before the township hearing, and land developments for 30 days.
   - **OH:** the county or regional planning commission recommends before the township zoning commission's hearing.
   - **MI:** the county planning commission reviews after the township planning commission's hearing and before the board's vote.
   - **WI:** the county zoning committee *decides* for about 760 county-zoned towns and approves town ordinances.
   - **MN:** the county decides for townships without their own zoning.

   I fetched 12 county or regional bodies in these states. 10 publish agendas or packets that list township items, 1 had not yet posted its next agenda, and 1 showed no listing (verified). They include data-center ordinances for Tinicum, Marple, Newtown and Chester Heights (Delaware County PA), South Shenango (Crawford County PA) and Paris Township (LUC, OH). One county source stands in for 10–60 townships. **Estimate:** about 2,200–3,500 townships across PA/OH/MI/WI/MN become visible for about $0 and 2–4 weeks of curation.
2. **Feeds we are allowed to read are under-used.**
   - CivicPlus AgendaCenter **RSS** (`/RSSFeed.aspx`) and iCal are allowed by CivicPlus's standard robots.txt.
   - **Town Web** WordPress category feeds (600–800+ small towns, rooted in Wisconsin) are allowed.
   - **Utah PMN** has per-body RSS and email.
   - The **Legistar Web API `eventitems`** endpoint returns agenda item text even though the PDF host (`legistar*.granicus.com`) disallows bots.
   - **County ArcGIS land-application layers** are open. Loudoun's LOLA layer had filings dated 2026-10-09.

   All of these were verified.
3. **Push channels are legitimate and cover blocked sites.** We can receive email that publishers send to anyone who asks:
   - govDelivery bulletins;
   - CivicPlus Notify Me;
   - Utah PMN email;
   - Town Web "Subscribe to Updates";
   - notices that state open-meetings laws make bodies send on request: **VA §2.2-3707(F)** (electronic notice of all meetings), **MI MCL 15.266** (free to news media), **IN 5-14-1.5-5** (news media, annual request by Dec 31), **WI 19.84** (news media), **MN 13D.04** (special meetings, can be subject-limited) and **OH 121.22(F)** (notice of meetings on a "specific type of public business").

   Inbound mail is free on Cloudflare Email Routing (verified docs). Signups need a person, not a script.
4. **Bot walls have an official front door.**
   - **Cloudflare Verified Bots**, via Web Bot Auth: "historically, Verified bots have been excluded in default bot configurations across all plans" (verified docs).
   - **Akamai's bot-verification request** (secondary).

   Cloudflare challenges 95 counties in the census, 43 of them in the 10 target states. This is the cheapest fix for them.
5. **Press-association notice sites are not a free catch-all.** All seven I read (PA, OH, VA, GA, MN, UT, TX) allow personal, non-commercial use only and forbid putting the notices in a database (verified). We need a licence or written consent; prices are unpublished. The same goes for LocalGovIndex, whose robots.txt refuses every unnamed bot and says "the extracted record is itself a licensable product" (verified).
6. **Search APIs are only discovery aids.** Google's Custom Search JSON API is closed to new customers and ends Jan 1, 2027 (verified). Brave costs $5 per 1,000 requests, and its base terms forbid storing results (verified). A search hit never makes a robots-disallowed document fetchable.

---

## Ranked route table

Ranked by coverage per dollar and per engineering day. Township and county counts are **estimates** built on the verified samples and the census CSV, unless marked otherwise.

| # | Route | Coverage gain (estimate) | Money | Eng. time | Legal / terms risk | Set-up time | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | **County / regional planning-body agendas that list township items** (Act 247 lists, ORC 519.12 recommendations, MZEA reviews, WI/MN county zoning committees) | **PA** 600–900 of 1,546 townships (zoning amendments and land developments; *not* conditional uses).<br>**OH** 500–800 of 1,308.<br>**MI** 300–600 of 1,240 (board-vote stage).<br>**WI** 250–450 of ~1,250 towns.<br>**MN** 500–800 of 1,779 | $0 | 1 wk parser work plus ~75–100 h curation (~300 county bodies at 15–20 min each) | Low (public agendas; robots checked) | 2–4 wks | §1 (12 bodies fetched, 10 showed township items) |
| 2 | **Allowed feeds**: CivicPlus RSS/iCal, Town Web and WordPress feeds, Legistar `eventitems`, CivicClerk API | Mainly cheaper, fresher polling of bodies already readable, plus ~100–300 WI/MN/MI towns on Town Web | $0 | 2–4 days | Low | 1 wk | §2 |
| 3 | **Statewide portals and bulletins**: UT PMN (RSS/email), MN EQB Monitor (weekly), NV | **UT**: all 29 counties and ~270 municipal entities.<br>**MN**: every EAW/AUAR statewide | $0 | 2–3 days | Low (utah.gov disclaimer allows copying for informational use) | 1 wk | §2, §6 |
| 4 | **Push inbox**: govDelivery, Notify Me, Town Web and PMN email, township newsletters; parsed by Cloudflare Email Routing and a Worker | Posting signals for blocked or closed bodies: in target states, 43 Cloudflare, 22 Akamai, 46 other-403 counties plus closed-vendor counties. Full text only when the email carries it | $0–5/mo | 3–5 days pipeline; signups by a person, 2–3 min per list | Low (receiving what publishers send). Never automate signups | 2–6 wks | §3 |
| 5 | **Statutory notice-on-request letters** (VA, MI, IN, WI, MN, OH) | Every responding body in those states, including towns with no website. Notices often lack agendas (MI and OH require none) | $0 to small fees and postage | 1–2 days (template, tracking) | Low. "News media" status for 351 Watch is a legal question | 1–3 mo (IN requests due by Dec 31 for 2027) | §3 |
| 6 | **Cloudflare Verified Bot (Web Bot Auth) plus Akamai bot verification** | Up to 43 Cloudflare-challenged counties in the target states (GA 10, TX 7, WI 6, MN 6, MI 5, VA 3, OH 2, PA 2, IN 2), only where sites use default bot settings (perhaps 30–60%). Akamai: up to 22 (WI 6, VA 5, TX 5, MN 2, GA 2, MI 1, PA 1) | $0 (needs a Cloudflare account) | 3–5 days (Ed25519 signing, key directory) | Low; this is the vendor's sanctioned path | 2–8 wks review; approval not guaranteed | §8 |
| 7 | **Honour long crawl delays with a daily budget** | **IN** +19 counties (29% to 53% readable); +1–4 per other state | $0 | 1 day | Low (honouring the delay *is* the rule) | Days | census CSV |
| 8 | **County GIS and permit portals** (ArcGIS REST land-application layers) | Application-stage signal (weeks to months before hearings) in large VA/GA/TX/MN counties; ~10–30 counties worth wiring | $0 | 1–2 h per county | Low (robots 404 or allow; public REST) | 1–2 wks | §6 (Loudoun LOLA verified) |
| 9 | **State-agency permission**: GA DCA DRI system | **GA**: every data center ≥500k sq ft statewide (≥300k in ARC urban/suburban areas) | $0 | 1–2 days once allowed | Low with permission | 1–6 mo | §8 |
| 10 | **Vendor allow-listing**: Granicus (ViewPublisher, iQM2, PrimeGov, Legistar files), Diligent (BoardDocs, iCompass, Community), HeyGov | Closed-vendor counties in target states: TX 17, VA 9, MN 4, GA 4, MI 2, WI 2, IN 1, OH 1, UT 1, plus many data-center cities | $0 to unknown | 1–2 wks per vendor once allowed | Low with permission | 3–12 mo; uncertain | §8 |
| 11 | **Press-association public-notice licence** (or the Column API where a state uses it) | The only catch-all for small townships with no web presence (OH and MN most). Zoning hearings require newspaper notice | Unpublished; contact each association (estimate $1–10k/yr per state) | 1–2 wks per state | **High without a licence** (terms forbid commercial use) | 1–3 mo | §4 |
| 12 | **Aggregator licence**: LocalGovIndex, GatherGov, Hamlet, CivicIQ, Citizen Portal | Fallback for specific blocked cities | LocalGovIndex Professional $399/mo (self-serve; data reuse needs a written licence); others "book a demo" | Days | **High without a written licence** | 1–2 mo | §5 |
| 13 | **Search-engine APIs** (Brave; Google CSE closing) | Discovery of new documents on allowed hosts only | Brave $5 per 1k requests, $5/mo free credit | 2–3 days | Medium if results are stored (Brave base terms forbid it) | Days | §7 |

---

## 1. County and regional review of township zoning

### Statute and timing by state

| State | Statute | What the county body gets | Timing vs township action | Who decides | Label |
|---|---|---|---|---|---|
| **PA** | MPC (Act 247) §609(e) and §304/§505: amendments. §607(e), §304, §302: new ordinances, comprehensive plans, official maps. §502(b) and §704(b): subdivisions, land developments and planned residential developments (PRDs) | Every zoning text or map amendment and every land-development plan (data-center site plans included). **Conditional uses are not referred**, and PA grid-scale solar is usually a conditional use | Amendments: submitted **≥30 days before** the governing body's hearing; county has 45 days for new ordinances. Land development: the municipality cannot act for **30 days** | Township; county is advisory | secondary (county summaries of the MPC) — [Allegheny County MPC submittals summary](https://www.alleghenyplaces.com/pdf/MPC%20Submittals%20Summary%20-%20Sept%202019.pdf), [Berks E-Flash Jan 2026](https://www.berkspa.gov/getmedia/deec894e-6528-4c42-a6eb-22c12534a1ec/EFlash-Jan2026-FINAL.pdf); PA solar usually conditional use: [Penn State Extension](https://extension.psu.edu/ordinance-considerations-for-grid-scale-solar-development) (secondary) |
| **OH** | ORC 519.12 | Every township zoning text or map amendment, transmitted **within 5 days** of the motion, resolution or application | County or regional planning commission recommendation is considered **at the township zoning commission hearing** (held 20–40 days after initiation). Limited-home-rule townships (ch. 504) are exempt | Township trustees; county is advisory | secondary — [ORC 519.12 (9-23-2026 PDF)](https://codes.ohio.gov/assets/laws/revised-code/authenticated/5/519/519.12/9-23-2026/519.12-9-23-2026.pdf) (codes.ohio.gov robots disallow all, so not fetched), [Stark County RPC procedure](https://starkcountyohio.gov/Regional%20Planning%20Commission/Twp%20Zoning%20Procedure%20-%20Website%20%20(2026%20Update).pdf) |
| **MI** | MZEA, MCL 125.3307 | A township zoning ordinance or amendment, after the township planning commission's public hearing, goes to the county planning or zoning commission (or a coordinating zoning committee) | Review deemed waived if not returned **within 30 days**. County boards may waive review by resolution. It comes **after the PC hearing, before the board vote** | Township board; county is advisory | secondary — [MCL 125.3307](https://legislature.mi.gov/documents/mcl/pdf/MCL-125-3307.pdf) (legislature.mi.gov returns 403 to our bot), [Breitung Twp](https://www.zoneomics.com/code/breitung-charter-township-MI/chapter_14), [Vassar Twp](https://vassartownship.org/wp-content/uploads/2023/03/ZoningOrdinanceAmendmentResolution_2014-09.pdf), [Isabella County PC annual report](https://www.isabellacounty.org/wp-content/uploads/2026/01/2025-PC-Annual-Report.pdf) |
| **WI** | Wis. Stat. 59.69(5)(e): county zoning amendments. 60.62(3)(a): town ordinances | In county-zoned towns, **the county decides** rezonings and conditional uses. In counties with a county ordinance (pop. < 485,000), a town's own zoning ordinance or amendment needs **county board approval** | County hearing after a class 2 notice. Notice goes to the town clerk **≥10 days before** the hearing. The town board may disapprove within 10 days after (extendable by 20) | County, with a town veto on some amendments | verified — [59.69(5)(e)](https://docs.legis.wisconsin.gov/document/statutes/59.69(5)(e)), [60.62](https://docs.legis.wisconsin.gov/document/statutes/60.62) |
| **MN** | Minn. Stat. 394.33, 394.26 | Townships without their own zoning are zoned by the county. A town's controls may not be less restrictive than the county's. County hearings require written notice to the affected town board | County planning commission or board of adjustment hearings | County, unless the township zones itself | verified — [394.33](https://www.revisor.mn.gov/statutes/cite/394.33), [394.26](https://www.revisor.mn.gov/statutes/cite/394.26) |
| **IN** | IC 36-7-4 (area and advisory plan commissions) | Townships do not zone; the county or area plan commission and BZA *are* the deciders | n/a | County | background (prior notes) |
| **VA, GA, TX, UT** | County zoning (VA, GA); no county zoning (TX); Utah PMN | Counties are the deciders. GA adds **Developments of Regional Impact** (regional commission review; data centers ≥500k sq ft, ≥300k sq ft in ARC urban/suburban areas, since Nov 2025) | DRI review runs before local action | County / city | GA DRI: secondary — [Georgia Recorder](https://georgiarecorder.com/2025/11/21/georgia-board-approves-new-review-process-for-large-data-centers/), [AJC](https://ajc.com/business/2025/11/data-centers-to-get-regional-review-public-notice-on-key-georgia-website/) |

### Sampled county and regional bodies

Bodies were sampled politely, with plain GETs that obeyed robots.txt.

| State | Body | Online? | What it showed | Label / link |
|---|---|---|---|---|
| PA | **Delaware County Planning Commission** | Yes, monthly "Act 247 Review applications" PDF | **Aug 20, 2026:** data-center zoning amendments for **Tinicum**, **Marple** (revisions) and **Newtown Townships**, plus a warehouse land development. **Sept 17, 2026:** **Chester Heights Borough data-center** amendment | verified — [Aug](https://delcopa.gov/sites/default/files/2026-08/Agenda202608.pdf), [Sept](https://delcopa.gov/sites/default/files/2026-09/Agenda202609.pdf) |
| PA | **Crawford County Planning Commission** | Yes, WordPress PDF | Jul 27, 2026: "Action – South Shenango Township – Zoning Amendment Data Centers" | verified — [agenda](https://crawfordcountypa.net/wp-content/uploads/2026/07/2026-07-27_Regular-Meeting-Agenda.pdf) |
| PA | **Lancaster County Planning Commission** | Yes, CivicPlus AgendaCenter plus RSS | Oct 13, 2026 packet, posted Oct 9 (83 pp.): staff reports on township ordinance reviews (Fulton, East Cocalico, Rapho, Warwick; info items East Hempfield, Drumore, Columbia) and 13 land developments | verified — [RSS](https://lancastercountyplanning.org/RSSFeed.aspx?ModID=65&CID=All-0), [packet](https://lancastercountyplanning.org/AgendaCenter/ViewFile/Agenda/_10132026-593) |
| PA | York County Planning Commission | No agenda listing found (AgendaCenter 404, RSS empty) | — | verified — [RSS](https://ycpc.org/RSSFeed.aspx?ModID=65&CID=All-0) |
| PA | Lehigh Valley Planning Commission (2 counties) | Publishes per-municipality review agendas (2023 packet) | The site reset our connection | secondary — [2023 packet](https://lvpc.org/pdf/2023/comp%20planning/Dec%20Comprehensive%20Planning%20Committee%20Final%20Packet.pdf) |
| OH | **Delaware County Regional Planning Commission** | Yes, a "monthly mailing" page lists items and PDFs ~2.5 weeks ahead | Oct 29, 2026 items: "Addison Properties / Orange / FR-1 to PUD", "Genoa Twp. Zoning Commission / Zoning Resolution amendments". WordPress events API exposed | verified — [mailing](https://regionalplanning.co.delaware.oh.us/current_events/mailing/) |
| OH | **Logan-Union-Champaign RPC** (3 counties, ~43 townships) | Yes, Wix page with agenda and staff-report PDFs | Oct 8, 2026: "Review of Paris Township Zoning Text Amendment (Union County)". 2026 staff reports include the Harrison Twp (Logan) data-center/BESS prohibition (secondary) | verified — [agenda](https://www.lucplanning.com/_files/ugd/540e57_f7c0a792473f48deb08cec3c7131723c.pdf), [this month](https://www.lucplanning.com/thismonthatluc) |
| OH | **Clark County** (Planning Commission, Rural Zoning Commission, CEDA) | Yes, CivicPlus RSS plus Notify Me lists per board | RZC public hearing Oct 15, 2026 (agenda posted Oct 8): "Rezoning Case # Z-2026-09… Moorefield Township" (county rural zoning) | verified — [RSS](https://www.clarkcountyohio.gov/RSSFeed.aspx?ModID=65&CID=All-0), [RZC agenda](https://www.clarkcountyohio.gov/AgendaCenter/ViewFile/Agenda/_10152026-1331) |
| MI | **Clinton County Planning Commission** | Yes, CivicPlus RSS | Oct 8, 2026: "Eagle Township Permanent Zoning Ordinance Draft" (communications); special land use in Greenbush Twp (county-zoned) | verified — [agenda](https://www.clinton-county.org/AgendaCenter/ViewFile/Agenda/_10082026-2057) |
| MI | Livingston County Planning Commission | Reviews township amendments | Reviewed Howell Twp's "Data Processing" amendment; recommended against the 1,000-acre data-center rezoning (Nov 2025) | secondary — [county memo](https://thelivingstonpost.com/wp-content/uploads/2025/11/County-planning-DC.pdf), [WLNS](https://www.wlns.com/top-stories/officials-recommend-no-rezoning-of-farm-land-for-data-center-in-livingston-county/amp/) |
| WI | **Dane County Zoning & Land Regulation Committee** | Yes, via the Legistar Web API | Oct 13, 2026 agenda (published Oct 8): rezone and CUP petitions in the Towns of Cottage Grove, Montrose, Burke, Springdale, Albion and Blooming Grove. Item text comes from `eventitems`; PDF host disallowed | verified — [events](https://webapi.legistar.com/v1/dane/events?$filter=EventBodyId%20eq%20190), [items](https://webapi.legistar.com/v1/dane/events/12016/eventitems?AgendaNote=1&MinutesNote=0&Attachments=0) |
| WI | **Marquette County P&Z** | Yes, WordPress PDF | Aug 6, 2026: Town of Buffalo rezone hearing | verified — [pdf](https://www.marquettecountywi.gov/wp-content/uploads/2026/07/8-6-2026-PZ.pdf) |
| WI | **Grant County CS&Z** | Yes, WordPress PDF | Jul 2, 2026: rezones in the Towns of Platteville and Hickory Grove; CUP hearings | verified — [pdf](https://gcinternetwebsite.co.grant.wi.gov/wp-content/uploads/simple-file-list/Meetings-Minutes-Agendas/Conservation-Sanitation-and-Zoning-Department/AGENDA-07-02-2026.pdf) |
| WI | Walworth County Zoning Agency | CivicClerk | Meetings listed through Dec 2026; the Oct 15 agenda was not yet published on Oct 12 | verified — [API](https://walworthcowi.api.civicclerk.com/v1/Events?$filter=contains(eventName,'Zoning')) |

**Tally:** 10 of 12 bodies fetched showed township-level items: PA 3/4, OH 3/3, MI 1/1, WI 3/4. Walworth's next agenda was not yet posted, and York showed no listing. LVPC and Livingston do too (secondary). MN was not sampled at county level this run. Its 33 readable county sites in the census are mostly CivicPlus and CivicClerk, which carry planning-commission agendas (estimate).

**Scale context.**
- WI (secondary, Wisconsin Towns Association c. 2011): ~759 towns under county zoning, 242 with their own zoning, 258 with neither. — [Stadelman deck](https://www3.uwsp.edu/cnr-ap/UWEXLakes/Documents/programs/convention/2011/WorkingWithTownGovernment-Stadelman.pdf)
- MI: a jurisdiction-by-jurisdiction "zoning authority" dataset exists, the UM/EGLE Wind and Solar Zoning Ordinance Database. The MTU ArcGIS item metadata was verified; the layer itself returned error 500. — [iteminfo](https://portal1-geo.sabu.mtu.edu/server/rest/services/MICARES/Township_Zoning/MapServer/info/iteminfo?f=pjson)
- No statewide count of OH or MI county planning commissions was found. The township estimates in the ranked table assume 40–60% of counties both have a reviewing commission and post item-level agendas.

**Engineering notes.**
- Most of these bodies are already on supported platforms (CivicPlus, CivicClerk, Legistar) or WordPress PDFs. The `generic` adapter handles them.
- The new work is a **township-name extractor**: map "Tinicum Township", "Orange" (DCRPC uses township short names) or "Town of Burke" to our jurisdiction IDs, so a county hit is filed under the township.
- **Lead time:**
  - PA amendments are submitted at least 30 days before the township hearing;
  - OH recommendations come before the first township hearing;
  - MI reviews give warning before the board vote but miss the PC hearing;
  - in WI and MN the county meeting *is* the decision.

---

## 2. Official APIs and feeds

| Source | What is allowed | robots.txt on the API or feed host | Data-partner / allow-list program | Label / evidence |
|---|---|---|---|---|
| **Legistar Web API** (`webapi.legistar.com`) | Read-only GETs of public events, items and matters, no key for most clients. "Some clients require use of an API Token… please refer to that client for their token policy." Max 1,000 rows per query | **404**, so allowed. **But** agenda files sit on `legistar1/2.granicus.com`, robots `Disallow: /`. Use `events/{id}/eventitems` for item text (our adapter already avoids the PDFs) | None published. Tokens are granted **by the client government**, so ask the county or city | verified — [examples page](https://webapi.legistar.com/Home/Examples), [legistar2 robots](https://legistar2.granicus.com/robots.txt) |
| **Granicus ViewPublisher, iQM2, PrimeGov** | ViewPublisher robots allow only Googlebot, Slurp and msnbot. PrimeGov's portal JSON is on the tenant host, which has `Disallow: /`. iQM2 returns 429 | Closed | No data-partner program. The partners page lists Carahsoft, resellers, integrators and AWS. APIs need a customer contract and support-issued credentials (third-party scorecard, Sept 2026) | verified — [granicus.com/partners](https://granicus.com/partners/), [olmstedcounty.primegov.com/robots.txt](https://olmstedcounty.primegov.com/robots.txt); secondary — [supergood Granicus](https://supergood.ai/api-report-card/granicus) |
| **CivicClerk** (`<tenant>.api.civicclerk.com`) | Public, unauthenticated OData events and files (our adapter) | API host **404**; portal host `User-agent: *` with no disallow | No public developer program found. CivicPlus APIs are reported to be contract-gated | verified (robots, API); secondary — [supergood CivicPlus](https://supergood.ai/api-report-card/civicplus) |
| **CivicPlus AgendaCenter RSS** (`/RSSFeed.aspx?ModID=65&CID=All-0`), **iCal** (`/common/modules/iCalendar/iCalendar.aspx`), **Notify Me** (`/list.aspx`) | RSS gives title, pubDate and link for every agenda posting or update across all boards; iCal also works. The standard CivicPlus robots disallows `/RSS.aspx` (the listing page) but **not** `/RSSFeed.aspx` | Allowed (tested on Clark Co OH, Lancaster Co PA, Clinton Co MI, Otsego Co MI) | Notify Me is the publisher's own email/SMS list per board (needs a profile per site) | verified — [Clark RSS](https://www.clarkcountyohio.gov/RSSFeed.aspx?ModID=65&CID=All-0), [Clark robots](https://www.clarkcountyohio.gov/robots.txt), [Notify Me](https://www.clarkcountyohio.gov/list.aspx) |
| **Municode Meetings** (CivicPlus) | Open portal; some tenants set `Crawl-delay: 15` | `meetings.municode.com` 404 | None found | verified (prior run and this run) |
| **BoardDocs / Diligent Community / iCompass** | BoardDocs: CloudFront 403 even on robots.txt. Community and civicweb: `Disallow: /` | Closed | Diligent's partner program (since 2022: referral/resell, integration, content partners, 3 tiers) is GRC-oriented. **No public-data or allow-list program found** | verified (prior run); secondary — [Diligent partners](https://www.diligent.com/news/diligent-launches-first-single-source-partner-program-integrating-solutions-across-grc-audit-and-esg) |
| **eSCRIBE** (`pub-<client>.escribemeetings.com`) | Portal home and HTML agenda view are open. Some tenants put `FileStream.ashx` behind a browser check (not solved) | 404 | None found | verified (robots); adapter notes |
| **govDelivery** | `content.govdelivery.com` (individual bulletins) is allowed. On `public.govdelivery.com`, robots allows only `/accounts/` and `/system/images/`, so topic RSS feeds under `/topics/` are **disallowed**. The bulletin archive list redirects to a login | Partly | Email subscription is the intended channel | verified — [public robots](https://public.govdelivery.com/robots.txt), [EQB bulletin](https://content.govdelivery.com/accounts/MNEQB/bulletins/42d3d41) |
| **Town Web** WordPress sites (600–800+ municipalities, Wisconsin-rooted) | `/feed/` and category feeds such as `/twd_repository_cat/town-board/feed/` | Allowed (only `/wp-admin/` is disallowed) | — | verified — [Town of Utica Town Board feed](https://townofuticawi.gov/twd_repository_cat/town-board/feed/) (Oct 12 agenda posted Oct 10); client count secondary — [Town Web blog](https://townwebdesign.com/blog/five-reasons-to-join-town-web) |
| **WordPress events APIs and ICS** on planning sites | e.g. `wp-json/tribe/events/v1/` on DCRPC | Allowed | — | verified (link seen on [DCRPC](https://regionalplanning.co.delaware.oh.us)) |
| **Utah Public Notice Website** | "Subscription options for bodies and individual notices available are RSS feed and Email." utah.gov disclaimer: "Anyone may view, copy, or distribute information… for personal or informational use… if the documents are not modified" | Allowed | Not needed | verified — [PMN FAQ](https://www.utah.gov/pmn/help.html), [utah.gov disclaimer](https://www.utah.gov/support/disclaimer.html) |
| **HeyGov** (WI towns) | API robots disallow (prior run) | Closed | None found | verified (prior run) |
| **ArcGIS REST** (county GIS) | Public map and feature services | `services.arcgis.com` robots answers 403 "Invalid URL", which counts as allow under RFC 9309. `hub.arcgis.com`: Crawl-delay 60, `/sites/` disallowed | — | verified |

---

## 3. Push channels: receiving what publishers send

**Is it legitimate?**
- Yes for the receiving side (estimate, low risk).
- These are public lists that agencies run so that anyone can be told about postings. Being on the list is receiving, not crawling.
- What stays off-limits:
  - **Automating the signup forms.** CivicPlus Notify Me needs a per-site profile, and govDelivery confirms by email. A person should sign up, or ask the clerk to add the address.
  - **Following links in the emails to hosts that block us.** The fetcher's robots/WAF rules still apply to every link.
- The email body itself (title, date, often the bulletin text) is ours to process.
- I could not read govDelivery's subscriber terms (not found in search); Granicus' help centre is [subscriberhelp.granicus.com](https://subscriberhelp.granicus.com/s/) (secondary). **Gap:** read those terms before launch.

**Channels and scale.**

| Channel | Who uses it | What arrives | Label |
|---|---|---|---|
| govDelivery (Granicus) | Thousands of agencies; "120 million people every day" (vendor claim) | Full bulletin HTML, often the agenda text or a link | secondary — [KS admin page](https://admin.ks.gov/offices/systems-management/it-support/applications/govdelivery) |
| CivicPlus Notify Me | Every CivicPlus CivicEngage site (160 counties in the census on AgendaCenter alone) | "Agenda posted" email or SMS per board, with a link | verified (list page) |
| Town Web "Subscribe to Updates" | 600–800+ towns | Per-category post notices | secondary — [Town of Utica](https://townofuticawi.gov/twd_repository_cat/town-board) |
| Utah PMN email | All Utah public bodies | Notice plus attachment link | verified (FAQ) |
| Township newsletters (Mailchimp, Constant Contact) | Varies | Meeting announcements | estimate |

**Statutory notice-on-request.** This is the strongest push route for towns with no website.

| State | Provision | Who can request | Delivery | Label / link |
|---|---|---|---|---|
| **VA** | §2.2-3707(F) | **Any person**, annually, in writing (with email) | "Shall provide notice of all meetings directly to each such person… may provide electronic notice" | verified — [Va. Code](https://law.lis.virginia.gov/vacode/title2.2/chapter37/section2.2-3707/) |
| **MI** | MCL 15.266 | Any person (yearly fee for printing and postage); **newspapers and radio/TV stations free**, at posting time | First-class mail; email by agreement (estimate) | secondary — [MCL 15.266](https://www.legislature.mi.gov/documents/mcl/pdf/MCL-15-266.pdf), [AG Op. 6305](https://www.ag.state.mi.us/opinion/datafiles/1980s/op06305.htm) |
| **IN** | IC 5-14-1.5-5(b) | **News media** filing an annual written request **by Dec 31** for the next calendar year | Mail, email or fax (agency's choice) | secondary — [PAC 13-FC-343](https://secure.in.gov/pac/files/advisory/13-FC-343.pdf) |
| **WI** | 19.84(1)(b) | News media filing a written request with each body | Communication from the presiding officer | verified — [19.84](https://docs.legis.wisconsin.gov/document/statutes/19.84) |
| **MN** | 13D.04 subd. 2 | Any person, for **special meetings**. "May limit the request to notification of meetings concerning particular subject matter" | Mail or delivery, or published notice instead | verified — [13D.04](https://www.revisor.mn.gov/statutes/cite/13D.04) |
| **OH** | 121.22(F) | Any person: "reasonable advance notification of all meetings at which any specific type of public business is to be discussed" (fee allowed). Media get 24 h notice of special meetings | Per each body's rule (mailing lists, email) | secondary — body rules quoting it, e.g. [OAC 3706-1-01](https://codes.ohio.gov/ohio-administrative-code/rule-3706-1-01) |
| PA | Sunshine Act notice-on-request | Not confirmed this run | — | gap |

- **Caveat:** whether 351 Watch counts as "news media" in IN, WI and MI is a legal judgment. It publishes alerts, which is arguable (estimate). Get a short legal opinion before relying on the media provisions.
- MI and OH notices need not include an agenda.

**Automation design (estimate; the platform facts are verified).**
- Use one domain (e.g. `notices.351watch…`) with **plus-addressed or per-state aliases**: `va+loudoun@…`, `mi+clinton@…`.
- Route mail with **Cloudflare Email Routing**: inbound is "Unlimited" on the Workers Free and Paid plans. An `email()` Worker parses the message, stores the raw MIME in R2, and enqueues a job that matches sender and subject to a jurisdiction and runs the same keyword and LLM classifier as agendas. — [CF Email pricing](https://developers.cloudflare.com/email-service/platform/pricing/), [limits](https://developers.cloudflare.com/email-service/platform/limits/) (verified docs)
- **Costs:**
  - $0–5/mo (Workers Paid for CPU headroom);
  - 3–5 engineering days;
  - 2–3 minutes of a person's time per list (2,000 lists ≈ 70–100 h, estimate).
- **Volume:** 2,000 lists produce roughly 300–800 emails a day (estimate), well within the free tier.

---

## 4. Legal-notice feeds and notice-law changes

**Press-association sites.** Robots allow them, but the terms do not. All seven terms pages I read restrict use to personal, non-commercial use (verified):
- **PA (PNA):** "solely for your own personal, non-commercial use… You may not, for example, incorporate the content in any database, compilation, archive or cache… reproduce, publish, reuse, resell, license…". PNA "reserves the right to charge a fee for… 'smart search'". — [publicnoticepa.com terms](https://www.publicnoticepa.com/Terms-of-Use.aspx)
- **OH (ONMA) and MN (MNA):** "personal, non-commercial use only… not to copy, reproduce, republish… any content on the Site for commercial purposes… except with ONA's [MNA's] written consent." — [OH](https://www.publicnoticesohio.com/Terms-of-Use.aspx), [MN](https://www.mnpublicnotice.com/Terms-of-Use.aspx)
- **VA, GA, UT, TX:** the same wording as PA. — [VA](https://www.publicnoticevirginia.com/Terms-of-Use.aspx), [GA](https://www.georgiapublicnotice.com/Terms-of-Use.aspx), [UT](https://www.utahlegals.com/Terms-of-Use.aspx), [TX](https://www.texaspublicnotices.com/Terms-of-Use.aspx)
- **Smart Search** (keyword email alerts, daily) is offered on all of them; signing up needs an account and the same terms apply. MI (mipublicnotices.com) and WI (wisconsinpublicnotice.org) run a different JavaScript platform; their terms were not read. IN's site is behind Cloudflare (prior run).
- **Conclusion:** we need a **written licence from each association** for alerting use. No public price list or API was found for any of the 10 target states. Contact each association's administrator (link on each site).

**Column** (column.us) built "the first ever publicly accessible API for public notice data" with press associations. Access is segmented by state, with bearer tokens. Partner states named in press releases are Maine, Arizona, Louisiana and New York, none of them our 10. — [docs](https://docs.column.us/reference/accessing-notices-by-state) (JS app; secondary), [Maine](https://www.column.us/blog/maine-joins-column-partner-program/) (secondary)

**Notice-law changes and what they change for us.**

| Law | Change | Effect on 351 Watch | Label |
|---|---|---|---|
| **NJ S-4654** (signed June 30, 2025; effective Mar 1, 2026) | Public entities must post legal notices on their own websites, with a prominent homepage link | Every NJ municipality now has a legal-notice page, a crawlable list where robots allow it. Out of the 10-state scope, but a model for others | secondary — [Saiber](https://www.saiber.com/insights/publications/2025-08-06-new-law-modernizes-legal-notice-requirements-in-new-jersey), [O'Sullivan](https://www.oslaw.com/news/2025-07-28-new-jersey-modernizes-legal-notice-requirements-with-online-publication-law) |
| **Indiana HEA 1210** (2026) | From **July 1, 2027**, units may publish notices in a newspaper (print or electronic) **or on their own website**. Bars charging people to view notices online; standard digital notice form via the State Board of Accounts | From mid-2027, IN notices increasingly sit on unit websites, free and in a standard format. Plan a per-unit "notices page" listing type. The SBOA form may make a statewide index feasible | secondary — [FBT Gibbons](https://fbtgibbons.com/indiana-amends-public-records-access-laws-and-public-notice-requirements/), [The Republic](https://www.therepublic.com/?p=891566) |
| **Ohio HB 33** (2023) | Narrow municipal-notice website option (ORC 731.21); ONMA statewide site posting stays free to governments | Small effect on townships; zoning hearing notices still go to newspapers. The ONMA site stays the catch-all and stays licence-gated | secondary — [PNRC analysis](https://www.pnrc.net/wp-content/uploads/2023/09/PNRC-Analysis.pdf), [ONA bulletin](https://ohionews.org/aws/ONA/ebulletin/view_mail/234750/3338075) |
| **Florida HB 7049** (2022; §50.0311; effective Jan 1, 2023) | A local government may publish on a county-designated public website instead of a newspaper | Out of scope, but shows the pattern: county notice sites become crawlable government sources | secondary — [FL Senate summary](https://flsenate.gov/Committees/billsummaries/2022/html/7049), [Lee Co Ord. 23-15](https://www.leegov.com/bocc/Ordinances/23-15.pdf) |

---

## 5. Licensed data from aggregators

| Aggregator | Coverage claim | Price | Terms on reuse, resale, display | How they say they get data | Label |
|---|---|---|---|---|---|
| **LocalGovIndex** | 2,823 local governments in 50 states (prior run) | Free; Civic $9/mo; Researcher $49/mo; **Professional $399/mo** (prior run) | robots.txt refuses every unnamed bot (`User-agent: * Disallow: /`). "AI USE REQUIRES A LICENSE… not permitted without our written license". "The extracted record is itself a licensable product". **Any reuse in 351 Watch alerts needs a written licence** | Agendas, minutes and attachments (product description) | verified — [robots.txt](https://localgovindex.com/robots.txt); pricing from [data_center_and_other_fights.md](../Meeting%20monitor%20national%20expansion/data_center_and_other_fights.md) |
| **GatherGov** (Turl Street Group LLC) | "9300+ jurisdictions… 735K+ agendas & minutes", 94% of population | Not published ("Start for free", "Book a demo"); has an API ("View documentation") | Terms page did not render for our fetcher | "We aggregate data from public sources, including local government websites, meeting portals, agendas, minutes, staff reports, permits, and planning records" | verified — [data](https://gathergov.com/data), [api](https://gathergov.com/api); contact support@gathergov.com |
| **Hamlet** (myhamlet.com) | "3,000+" councils and commissions (Feb 2026) | Not published; free tier for journalists; enterprise for developers | Not read (site answered 429 to robots.txt) | Meeting video and transcripts plus agendas (press) | secondary — [PublicCEO](https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/), [TechCrunch](https://techcrunch.com/?p=3073247) |
| **Citizen Portal** (citizenportal.ai) | Five government levels nationwide | $12–49/mo consumer (prior note); no API found | Pricing and terms pages behind a Cloudflare challenge | "Primary government sources" | secondary — [navtools listing](https://navtools.ai/tool/citizen-portal-ai) |
| **CivicIQ** (civiciq.com) | "80,000–100,000+ agencies" (B2G sales signals); MCP connector | Not found | Pricing page behind a Cloudflare challenge | Agendas and minutes for pre-RFP signals | secondary — [CivicIQ MCP page](https://civiciq.com/mcp/public-meetings-mcp) |

**Bottom line (estimate).** These are fallbacks, not foundations. Only LocalGovIndex has a published price, and it explicitly reserves data reuse. A **targeted licence** is the right shape: specific blocked cities (e.g. Granicus/BoardDocs data-center cities), alert-only use, with links back. Ask each for a written licence that allows:
- displaying snippets with attribution;
- storing derived alert records;
- no resale of raw data.

---

## 6. Partnerships

| Partner | What they could give us | Evidence / label |
|---|---|---|
| **Michigan Townships Association** | A website directory per township (already used, 272 read). Ask for: bulk directory export; a member bulletin asking clerks to add notices@ to their OMA notice lists | verified (prior run); robots `Crawl-delay: 10` |
| **PSATS** (PA) | "Find My Township" directory (dynamic search; not exercised). Model large-solar ordinance (shows they track siting). Ask for a directory export and a bulletin item | verified page — [Find My Township](https://www.psats.org/find-my-township-2/), [model ordinance](https://www.psats.org/wp-content/uploads/2020/09/Solar-Model-Large-Scale-Facility.doc) |
| **Ohio Township Association** | County membership coordinator directory. Ask for: township contact list; a bulletin item on 121.22(F) notice lists | verified — [ohiotownships.org](https://www.ohiotownships.org/) |
| **Wisconsin Towns Association** | County units and the town roster. Ask which towns are county-zoned (the 759/242/258 split is 2011 data) | verified site; secondary deck |
| **Minnesota Association of Townships** | Township roster; which townships zone themselves | verified site |
| **County planning directors' associations**: County Planning Directors Association of Ohio (CCAO affiliate); PA, MI, MN (MACPZA) and WI (code administrators) equivalents | One ask reaches every county review body: post or forward the monthly township review list (PA Act 247 list, OH 519.12 list) or add notices@ to the distribution | OH: secondary — [CCAO affiliates](https://www.ccao.org/affiliates); others estimate |
| **Regional planning commissions** (LUC, DCRPC, LVPC, MORPC, SEWRPC…) | Already publish; ask for an RSS feed or email list of township referrals | verified (LUC, DCRPC) |
| **County GIS and permit portals** | Application-stage records. **Loudoun LOLA** ArcGIS layer: robots 404, plain GET, current to 2026-10-09 (zoning map amendments, legislative applications, data-center rezonings such as "VANTAGE DATA CENTER – BROAD RUN") | verified — [LOLA layer query](https://logis.loudoun.gov/gis/rest/services/Projects/LOLA_DATA/MapServer/0/query?where=1%3D1&outFields=PlanNumber,PlanType,PlanStatus,PlanName&returnGeometry=false&resultRecordCount=5&f=pjson) |
| **State open-meetings portals** | UT PMN (all bodies, RSS and email), NV notice.nv.gov, RI SOS. None found in MI, OH, PA, WI, MN, IN, VA, GA or TX for local bodies. MN EQB Monitor covers environmental review. Indiana Gateway (DLGF; robots 404) offers downloads of local finance reports and a TIF viewer, an after-the-fact abatement backstop | verified — [UT PMN](https://www.utah.gov/pmn/), [IN Gateway](https://gateway.ifionline.org/) |
| **University of Michigan Energy Zoning Database** (Graham Institute, Sarah Mills) | Ordinances and **zoning-jurisdiction classification for IL, IN, MI, MN, OH, WI**. This is exactly the township-to-decider routing table §1 needs. Behind Cloudflare for us, so ask for a data share | secondary — [energyzoning.org](https://energyzoning.org/) (403 challenge), [UM news](https://news.umich.edu/?p=140351); MTU metadata verified |
| **Penn State CELP — PA Solar Ordinance Database** | 4,900 provisions from 300 local governments in 57 counties (updated Aug 27, 2026). Useful for knowing which townships have solar or conditional-use rules; not a live feed | secondary — [celp.psu.edu/pa-solar-ordinances](https://celp.psu.edu/pa-solar-ordinances/) |

---

## 7. Search-engine APIs

- **Google Custom Search JSON API:** "closed to new customers… Existing Custom Search JSON API customers have until January 1, 2027 to transition". Vertex AI Search covers "up to 50 domains". Not an option for a new build. — [Google docs](https://developers.google.com/custom-search/v1/overview) (verified)
- **Bing Search APIs** retired Aug 11, 2025. — [Microsoft](https://learn.microsoft.com/en-us/lifecycle/announcements/bing-search-api-retirement) (secondary)
- **Brave Search API:**
  - "$5 per 1,000 requests", with "$5 in free credits every month" (≈1,000 queries).
  - Base terms forbid storing results: "store, cache, or create a database of Search Results… other than transient storage". Storage needs "a plan that explicitly grants storage rights".
  - [pricing](https://brave.com/search/api/), [terms](https://api-dashboard.search.brave.com/terms-of-service) (verified)

**Where search is fine and where it is not:**
1. **Fine:** querying the API and using the **result URL, title and snippet transiently** to decide what to fetch, or to show a "possible new item, open source" alert that links out. That use is licensed by the search provider, not by the target site.
2. **Fine:** fetching a discovered document **when its own host's robots.txt allows 351WatchBot**. Examples: a township WordPress PDF, a county `/sites/default/files/` agenda, a CivicPlus `ViewFile`.
3. **Not fine:** fetching a discovered document on a host that disallows us, even though Google indexed it. The robots rules that admit Googlebot do not admit us. Examples:
   - `*.granicus.com` and `legistar*.granicus.com` (Googlebot, Slurp and msnbot allowed; `*` disallowed);
   - PrimeGov, Diligent, `apps.dca.ga.gov`.
4. **Not fine:** using search-engine **cached copies** or third-party SERP scrapers (SerpAPI-style) to read blocked documents. That evades the publisher's rule and breaks the search engine's terms.
5. **Not fine (on Brave's base plan):** storing snippets in our database as a record. Buy storage rights or keep only our own derived flag ("search hit on date X") plus the URL.

**Value (estimate):** Low to medium. Use it for the **long tail of township WordPress sites** with no feed: `site:` queries per township domain for "data center", "solar", "moratorium" weekly. At ~2,000 townships × 1 query/week ≈ 8,700 queries/month ≈ $40/month.

---

## 8. Direct permission and allow-listing

**Published programs found.**
- **Cloudflare Verified Bots** (BotBase submission form in a Cloudflare dashboard account):
  - Must use Web Bot Auth or IP validation, obey robots.txt and crawl directives, and keep reasonable rates.
  - Signed requests carry `Signature`, `Signature-Input` and `Signature-Agent` headers, with an Ed25519 key directory at `/.well-known/http-message-signatures-directory`.
  - "Historically, Verified bots have been excluded in default bot configurations across all plans." Free-plan **Bot Fight Mode** cannot be bypassed by site rules. Super Bot Fight Mode (Pro and up) has an explicit "Verified bots: Allow" action.
  - [verified bots](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/), [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/), [Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/) (verified docs, updated Oct 2026)
- **Akamai Bot Manager:** "Verify your bot or AI agent to avoid unnecessary challenges. Submit a verification request." Directory of 1,400+ known bots. — [Akamai Bot Manager](https://www.akamai.com/products/bot-manager) (secondary)
- **Legistar API tokens:** granted by each client government ("please refer to that client for their token policy"). (verified)
- **Granicus, Diligent, CivicPlus, PrimeGov:** no published data-access or allow-list program. Partner programs are reseller, integrator or GRC-oriented. (verified absent on the Granicus partners page; secondary for the others)

**How others get data.**
- **GatherGov:** "public sources, including local government websites, meeting portals…". It does not say how it handles blocked portals.
- **LocalGovIndex:** says nothing public about sourcing, but treats its own extraction as licensable and refuses unknown bots.
- **Hamlet:** emphasises meeting video and transcripts.
- None describes a vendor allow-list. (verified and secondary as cited in §5)

**What a request should look like (template, estimate).** Keep it to one page:
1. **Who:** 351 Watch, the bot name `351WatchBot`, a contact address, and a public bot-info page (purpose, robots policy, rate, Web Bot Auth key directory).
2. **What:** list the hosts and paths, e.g. `*.granicus.com/ViewPublisher.php`, `AgendaViewer.php`, `/MetaViewer.php`, `legistar2.granicus.com/<client>/meetings/*`.
3. **How much:** at most 1 request per 5 s per host; at most 50 requests a day per client; agenda and minutes documents only; no video; no search pages.
4. **Why:** early public notice of land-use items. Alerts link back to the official page, and nothing is resold as raw documents.
5. **Ask:** add `User-agent: 351WatchBot` with `Allow` lines to robots.txt, or allow-list our Web Bot Auth signature or IP; alternatively give us a feed or export.
6. **Offer:** to stop on request; a named technical contact; a monthly request log on demand.

---

## Recommended route mix per state (cheapest first)

| State | Route mix | Rough cost | Expected coverage (estimate) |
|---|---|---|---|
| **MI** | (1) County planning-commission agendas, about 40–60 counties, mostly CivicPlus/CivicClerk/generic, CivicPlus via RSS. (2) MTA directory plus Town Web and WordPress feeds for larger townships. (3) MCL 15.266 written requests as news media to the ~50 siting-hotspot townships with no web agendas. (4) Cloudflare Verified Bot (5 counties). (5) Data share with UM Energy Zoning DB for the township-to-decider map | $0; ~3 wks eng and curation | 300–600 townships at board-vote stage, plus direct reads of ~35–50% of townships with web agendas |
| **OH** | (1) County and regional planning commissions under ORC 519.12 (LUC, DCRPC, Clark, MORPC-area, Stark, Licking, Medina…): highest-value township source. (2) 121.22(F) "specific type of business" notice requests to township zoning commissions in hotspot counties. (3) ONMA notice licence (OH townships are the least web-present, 15–25%) | $0 plus licence (unknown); ~3 wks | 500–800 townships before the first township hearing |
| **PA** | (1) Act 247 county review lists: Delco, Crawford, Lancaster verified; target all 66 county agencies; LVPC and others need a reachable host. (2) CivicPlus RSS and generic township listings for siting-fight townships. (3) PNA notice licence for conditional-use hearings (not referred to counties). (4) Penn State CELP database to flag conditional-use solar townships | $0 plus licence; ~3–4 wks | 600–900 townships for amendments and land development; conditional uses need the PNA licence |
| **WI** | (1) County zoning committees (Dane via Legistar items, Marquette, Grant…) for ~760 county-zoned towns, plus 60.62 town-ordinance approvals. (2) Town Web feeds. (3) Cloudflare and Akamai verification: 12 WI counties are behind those walls (tied with GA for the most). (4) HeyGov permission. (5) 19.84 media notice requests | $0; ~2–3 wks | 250–450 towns now; +100–200 with WAF allow-listing |
| **MN** | (1) County planning commissions and boards of adjustment for county-zoned townships (33 readable counties; CivicPlus 14, CivicClerk 10). (2) EQB Monitor weekly (data centers). (3) 13D.04 subject-limited special-meeting requests to townships with own zoning near hotspots. (4) Ask PrimeGov and Diligent for 4 counties | $0; ~2 wks | 500–800 townships via county; statewide EAWs |
| **IN** | (1) Honour 30–300 s crawl delays with a daily budget (+19 counties, to about 53% readable). (2) County APC and BZA agendas (townships do not zone). (3) IC 5-14-1.5-5 media notice requests **filed by Dec 31, 2026** for 2027 to counties in hotspots. (4) From July 2027, HEA 1210 unit-website notice pages | $0; ~1 wk | ~41–50 of 77 reachable counties |
| **VA** | (1) Already 38 of 84 reachable counties readable (CivicPlus 18, CivicClerk 11). (2) §2.2-3707(F) electronic notice requests to every blocked or closed county (18 blocked, 9 closed). This is the best statutory push in the set. (3) Loudoun-style ArcGIS land-application layers for Loudoun, Prince William, Fauquier, Culpeper, etc. (4) Granicus and Diligent permission (9 counties). (5) Akamai verification (5 counties) | $0; ~2 wks | 60–75% of counties with at least a notice signal; full text ~50% |
| **GA** | (1) **DCA DRI permission** (statewide data-center reviews). (2) County agendas: 40 of 145 readable; Novus and Municode adapters. (3) Cloudflare Verified Bot (10 GA counties, the most in the set). (4) GPA notice licence for the 61 "none found" counties | $0 plus licence; DRI 1–6 mo | DRI covers every large data center; counties ~30–45% |
| **TX** | (1) City Legistar and CivicClerk (6 of 10 data-center cities readable). (2) Generic adapter for the shared county template (76 of 252 readable). (3) Permission from Granicus (6) and Destiny (5). (4) Cloudflare (7) and Akamai (5) verification. (5) TPA licence only if county abatement notices matter | $0; ~2 wks | Cities high; counties ~35–45% |
| **UT** | **Utah PMN RSS or email per body.** It covers all 29 counties and ~270 municipal entities; the copy/distribute disclaimer is verified | $0; 2–3 days | ~100% of public bodies (as posted) |

---

## Permission requests to make (short list, in order)

1. **Cloudflare:** submit 351WatchBot to BotBase as a Verified Bot using Web Bot Auth. Build the signing and key directory first. Ask for nothing beyond the standard programme. — [form path](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/)
2. **Akamai:** a bot verification request from the Bot Manager page, for the 22 Akamai-blocked counties in the target states (WI 6, VA 5, TX 5 lead). — [Akamai](https://www.akamai.com/products/bot-manager)
3. **Georgia DCA, DRI program** (Community Assistance / planning; main line (404) 679-4840 per dca.georgia.gov): ask to allow `351WatchBot` on `apps.dca.ga.gov/DRI/` at 1 request per 10 s, or for a weekly CSV or RSS of new DRI submissions (number, jurisdiction, type, size, comment deadline).
4. **Granicus** (via the partner portal and the support of a client county; there is no data programme): ask them to add `351WatchBot` to robots.txt on `*.granicus.com` (ViewPublisher, AgendaViewer, MetaViewer) and `legistar1/2.granicus.com` for agenda and minutes documents only, ≤1 req/5 s, and to stop iQM2's 429s for low-rate agenda reads. In parallel, ask 3–5 client counties (Amarillo and Temple TX, Mount Pleasant and DeForest WI, Manassas VA) to request it on our behalf; Legistar tokens are client-granted. — [partner portal](https://granicus.com/granicus-online-partner-portal/)
5. **Diligent** (partner programme contact): ask for an allow-list on BoardDocs CloudFront and on Community/civicweb robots for public meeting pages (Culpeper VA, Douglasville GA, Lowell MI, 2 MN counties). — [Diligent partners](https://www.diligent.com/es/company/partners)
6. **Press associations** (PNA, ONMA, MPA, WNA, MNA, HSPA, VPA, GPA, TPA, UPA; via each site's administrator link): ask for a commercial licence to receive Smart Search keyword alerts, or a daily export, for zoning, solar, battery and data-center notices. Rights wanted: store derived alert records and show short excerpts with attribution and links. Ask for a price.
7. **UM Graham Institute** (Energy Zoning Database, Sarah Mills): ask for the zoning-jurisdiction table for MI, OH, IN, MN, WI (and IL), and offer our alert data back.
8. **County planning directors' associations** (OH CPDAO via CCAO; PA, MI, WI and MN equivalents): ask them to add notices@ to referral distribution lists, or to post monthly referral lists.
9. **HeyGov:** ask for robots allowance on public agenda endpoints for WI towns.
10. **Township associations** (MTA, PSATS, OTA, WTA, MAT): ask for a directory export and a bulletin item asking clerks to add notices@ to meeting notice lists.

---

## Gaps and cautions

- **Statute texts:** PA MPC (palegis.us returned 503), OH ORC (codes.ohio.gov robots disallow) and MI MCL (403 to our bot) were taken from county summaries and search snippets. Confirm the exact text before quoting it in the product.
- **Not exercised:** PSATS and press-site searches and Smart Search signups (account or POST). govDelivery subscriber terms not read.
- **Small samples:** county-body samples are 1–4 per state, and none was sampled at county level in MN. The township coverage numbers are estimates. The UM jurisdiction data would turn them into counts.
- **Cloudflare approval is not guaranteed** for a low-volume bot. Sites with custom WAF rules, "Under Attack" mode or AI-bot blocking may still challenge verified bots.
- **"News media" status** for statutory notice requests (MI, IN, WI) needs counsel's view.
- **Existing adapter compliance:** our Legistar adapter already avoids the robots-disallowed PDF host (checked in `crawler/watch351/adapters/legistar.py`). Keep CivicPlus polling on `/RSSFeed.aspx`, not `/RSS.aspx`.
