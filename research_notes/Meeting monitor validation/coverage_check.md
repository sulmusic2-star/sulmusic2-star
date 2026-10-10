# Coverage check: do existing meeting monitors already cover Massachusetts town boards?

Kill test for 351watch, run 2026-10-10 against the fixed 30-town sample in `projects/351watch/data/sample_towns.json`.

**Bottom line:** the test does not kill the product, but it leaves a credible competitor standing.
- **Hamlet:** claims 81 Massachusetts cities and towns plus 1 county, out of 351. That is about 23%.
- **SitePath:** has town bylaws on file but tracks no Massachusetts energy meetings.
- **CivicSearch:** covers 2 of the 30 sample towns, and only for council or select board meetings.
- **Citizen Portal:** the real overlap. Its AI-written meeting articles cover planning boards, conservation commissions and select boards in at least 6 sample towns, and probably more.

None of these tools visibly offers complete coverage of all five bodies across all 351 towns, or clean-energy-specific structured alerts. A free, no-login check cannot confirm what they deliver behind their logins.

---

## (a) 30-town coverage table

Legend for the Hamlet column:
- **partial**: a Hamlet page for the town or one of its bodies exists, but no planning board, ZBA or conservation commission page is visible.
- **no evidence (searched)**: a DuckDuckGo `site:myhamlet.com` query for the town returned no Hamlet page for it.
- **no evidence (unverified)**: the town could not be checked, because Hamlet's site and the search engines blocked automated lookups (see caveats).

Abbreviations in "other tools":
- **SP**: SitePath Intelligence. "rules" means its county page marks the town "rules on file", meaning a solar or BESS bylaw has been captured. Every sample county shows "Energy-related meetings & dockets: No tracked activity yet".
- **CS**: CivicSearch.
- **CP**: Citizen Portal (citizenportal.ai).

| # | Town | Hamlet covered? | Bodies covered (Hamlet) | Evidence URL | Other tools found |
|---|------|-----------------|-------------------------|--------------|-------------------|
| 1 | Lee | no evidence (searched) | none seen | https://www.myhamlet.com/lee-ma (unreachable, 429 bot challenge); DDG query returned only non-Lee pages | SP Berkshire: grade B, Lee listed with no rules on file and "no active moratorium", even though the Lee PB held a BESS moratorium hearing on 4/27/2026 (https://leema.gov/DocumentCenter/View/4860/). CS: no. CP: not found |
| 2 | Becket | no evidence (searched) | none seen | https://www.myhamlet.com/becket-ma (unreachable) | SP Berkshire: no rules on file, while Becket's BESS/solar moratorium special act H.5641 is pending (https://malegislature.gov/Bills/194/H5641). CS: no. CP: only cited secondhand by Middlefield PB |
| 3 | Worthington | no evidence (searched) | none seen | https://www.myhamlet.com/worthington-ma (unreachable) | SP Hampshire: listed as an "active BESS town" in intel text but no rules flag; moratorium bill H.5294 (https://malegislature.gov/Bills/194/H5294). CS: no |
| 4 | Pittsfield | no evidence (unverified) | unknown | https://www.myhamlet.com/pittsfield-ma (unreachable) | SP Berkshire: rules on file (BESS overlay, Ch. 23 §4.331). CS: no. CP: not found (search hit Pittsfield, Maine) |
| 5 | Great Barrington | no evidence (unverified) | unknown | https://www.myhamlet.com/great-barrington-ma (unreachable) | SP Berkshire: no rules on file. CS: no |
| 6 | Northampton | no evidence (unverified) | unknown | https://www.myhamlet.com/northampton-ma (unreachable) | SP Hampshire: no rules on file. CS: no. **CP: Planning Board** (https://citizenportal.ai/articles/6100262/massachusetts/hampshire-county/northampton-city/northampton-planning-board-continues-213-park-hill-site-plan-review-to-await-zba-variance) |
| 7 | Amherst | **partial** | "2 governing bodies covered" (which two is not visible) | https://www.myhamlet.com/amherst-ma (DDG snippet) | SP Hampshire: rules on file (draft 600 ft clean-energy setback). **CS: yes, Town Council, 87 meetings** (https://civicsearch.org/amherst-massachusetts). CP: not checked individually |
| 8 | Westfield | no evidence (unverified) | unknown | https://www.myhamlet.com/westfield-ma (unreachable) | SP Hampden: no rules on file, while the City Council's interim BESS restriction hearing was set for Feb 2026 (https://www.cityofwestfield.org/AgendaCenter/ViewFile/Agenda/_02032026-8340). CS: no |
| 9 | Sturbridge | no evidence (unverified) | unknown | https://www.myhamlet.com/sturbridge-ma (unreachable) | SP Worcester: rules on file. CS: no. PB agenda of 8/24/2026 has BESS bylaw amendments (https://www.sturbridge.gov/planning-board/agenda/planning-board-meeting-agenda-111) |
| 10 | Sutton | no evidence (unverified) | unknown | https://www.myhamlet.com/sutton-ma (unreachable) | SP Worcester: rules on file. CS: no. CP: not found (search hit Sutton, Vermont) |
| 11 | Shrewsbury | no evidence (unverified) | unknown | https://www.myhamlet.com/shrewsbury-ma (unreachable) | SP Worcester: rules on file. CS: no. CP: not found |
| 12 | Westborough | no evidence (unverified) | unknown | https://www.myhamlet.com/westborough-ma (unreachable) | SP Worcester: rules on file. CS: no. **CP: Planning Board + Select Board**, many articles (https://citizenportal.ai/articles/7314742/massachusetts/worcester-county/town-of-westborough/planning-board-approves-2026-calendar-continues-two-hearings) |
| 13 | Grafton | no evidence (unverified) | unknown | https://www.myhamlet.com/grafton-ma (unreachable) | SP Worcester: no rules on file. CS: no. CP: not found |
| 14 | Charlton | no evidence (searched) | none seen | DDG: "No results found for site:myhamlet.com Charlton Massachusetts" | SP Worcester: rules on file (5 MW standalone-BESS cap, 150 MW ESA dispute). CS: no. **CP: Planning Board + Conservation Commission**, including a solar decommissioning-bond item (https://citizenportal.ai/articles/5991782/Massachusetts/Worcester-County/Town-of-Charlton/Planning-board-conditionally-approves-decommissioning-bond-for-261-North-Sturbridge-Road-solar-project) |
| 15 | Leominster | no evidence (unverified) | unknown | https://www.myhamlet.com/leominster-ma (unreachable) | SP Worcester: no rules on file. CS: no. CP: not found |
| 16 | Fitchburg | **partial** | Board of Park Commissioners (no land-use body seen) | https://www.myhamlet.com/fitchburg-ma/board-of-park-commissioners--10430 | SP Worcester: no rules on file. CS: no. CP: not found |
| 17 | Framingham | no evidence (unverified) | unknown | https://www.myhamlet.com/framingham-ma (unreachable) | SP Middlesex: no rules on file. CS: no. CP: not found |
| 18 | Sudbury | no evidence (unverified) | unknown | https://www.myhamlet.com/sudbury-ma (unreachable) | SP Middlesex: rules on file. CS: no. **CP: board item on a BESS bylaw draft**, filed under the Lincoln-Sudbury school path (https://citizenportal.ai/articles/9876698/Massachusetts/School-Boards/Lincoln-Sudbury/Sudbury-staff-begin-drafting-battery-storage-bylaw-as-state-rules-take-effect-Board-seeks-protections-for-water-districts) |
| 19 | Westford | **partial** | Pedestrian Safety Committee meeting (3/25/2026), no land-use body seen | https://www.myhamlet.com/meeting/570130ff-5eee-40ea-a096-b6d07dd355a5 | SP Middlesex: rules on file. CS: no. **CP: Planning Board** (https://citizenportal.ai/articles/8026389/massachusetts/school-boards/westford-public-schools/planning-board-endorses-draft-10-year-open-space-and-recreation-plan) |
| 20 | Billerica | no evidence (unverified) | unknown | https://www.myhamlet.com/billerica-ma (unreachable) | SP Middlesex: rules on file. CS: no. **CP: Planning Board** (https://citizenportal.ai/articles/8070214/massachusetts/middlesex-county/billerica/planning-board-subcommittee-to-draft-concise-rules-seek-town-counsel-on-collaborative-workspace) |
| 21 | Andover | no evidence (unverified) | unknown | https://www.myhamlet.com/andover-ma (unreachable) | SP Essex: rules on file. CS: no. CP: not found |
| 22 | Wakefield | no evidence (unverified) | unknown | https://www.myhamlet.com/wakefield-ma (unreachable) | SP Middlesex: no rules on file. CS: no. CP: not found |
| 23 | Plymouth | no evidence (unverified) | unknown; Hamlet's one MA county appears to be Plymouth County (water district commission page) | https://www.myhamlet.com/plymouth-county-ma/central-plymouth-county-water-district-commission--6510 (county body, not the town) | SP Plymouth: rules on file. CS: no. CP: not found |
| 24 | Carver | no evidence (unverified) | unknown | https://www.myhamlet.com/carver-ma (unreachable) | SP Plymouth: rules on file; SP essay on the AG disapproving Carver's solar/BESS moratoria. **CS: yes, Select Board, 119 meetings** (https://civicsearch.org/carver-massachusetts). CP: not found |
| 25 | Middleborough | no evidence (unverified) | unknown | https://www.myhamlet.com/middleborough-ma (unreachable) | SP Plymouth: no rules on file. CS: no. CP: not found |
| 26 | Bridgewater | no evidence (unverified) | unknown | https://www.myhamlet.com/bridgewater-ma (unreachable) | SP Plymouth: no rules on file. CS: no. Local AI-assisted newsletter "Bridgewater Raynham News" covers PEG-recorded meetings (https://bridgewaterraynhamnews.substack.com/about) |
| 27 | Medway | no evidence (unverified) | unknown | https://www.myhamlet.com/medway-ma (unreachable) | SP Norfolk: rules on file. CS: no. CP: not found |
| 28 | Fall River | no evidence (unverified) | unknown | https://www.myhamlet.com/fall-river-ma (unreachable) | SP Bristol: no rules on file. CS: no. CP: not found |
| 29 | Barnstable | no evidence (unverified) | unknown | https://www.myhamlet.com/barnstable-ma (unreachable) | SP Barnstable: no rules on file. CS: no. CP: other Cape towns (Bourne, Eastham) found, Barnstable not found |
| 30 | Dartmouth | no evidence (searched) | none seen | DDG: "No results found for site:myhamlet.com Dartmouth Massachusetts" | SP Bristol: rules on file. CS: no. CP: not found |

"CP: not found" means only that Citizen Portal did not show up in a few grouped searches, each capped at 10 results. It is not a definitive no.

## (b) Coverage counts (30 towns)

| Tool | Visible coverage in sample | Bodies seen | How complete is the check |
|------|---------------------------|-------------|---------------------------|
| **Hamlet** | **3 partial** (Amherst, Fitchburg, Westford), 0 yes. 5 no evidence (searched), 22 no evidence (unverified) | Town page with "2 bodies" (Amherst); a park board (Fitchburg); a pedestrian safety committee (Westford). **No PB, ZBA or ConCom page seen for any sample town** | Weak. Site blocked; search index thin. Statewide claim is 81 cities + 1 county, which predicts roughly 7 sample towns if coverage were spread evenly |
| **SitePath Intelligence** | 30/30 at county level (grade only); 15/30 towns have bylaws on file | **0/30 meetings.** Every sample county shows "Energy-related meetings & dockets: No tracked activity yet" | Strong for public pages (all 10 county and intel pages fetched) |
| **CivicSearch** | **2/30** (Amherst Town Council; Carver Select Board) | Council or select board only, from YouTube transcripts | Definitive. Public place list has 610 places, 15 in Massachusetts |
| **Citizen Portal** (citizenportal.ai) | **at least 6/30** (Charlton, Northampton, Westborough, Billerica, Westford, Sudbury) | Planning board (5), conservation commission (Charlton), select board (Westborough), a BESS bylaw item (Sudbury) | Lower bound only. 4 grouped searches; site blocks automated fetches |
| citymeetings.nyc | 0/30 | n/a | NYC Council only |
| Local AI newsletters | 1/30 (Bridgewater Raynham News) | PEG-recorded meetings | Spotted in passing |

**Hamlet's statewide picture.** These are all public signals found through search snippets:
- `/coverage/MA` reads: "Search 4,886+ Massachusetts city council, planning commission, and board meetings… across 81 cities and 1 counties." That is about 23% of the 351 municipalities.
- Some Massachusetts towns get deep coverage, such as Sandwich with "19 governing bodies covered".
- Planning boards and conservation commissions do appear for non-sample towns:
  - Chicopee Planning Board (`/chicopee-ma/planning-board--6193`)
  - Boxborough Planning Board (`--6139`)
  - Freetown Planning Board (`--11553`)
  - Rockland Conservation Commission (`--11648`)
  - Littleton Planning Board meeting of 6/4/2026
- Town pages also exist for towns Hamlet does not cover. Ashburnham's says "0 governing bodies covered". **A Hamlet town URL alone does not prove coverage.**

Where Hamlet does cover a town, it ingests broadly, down to the Council on Aging, library trustees and park boards. Its likely gap is breadth across the 351 towns, not depth within a covered town.

## (c) Pricing and sign-up

**Hamlet** (myhamlet.com)
- **No public price list.** The site blocks automated fetches, and no snippet or third-party listing showed dollar amounts.
- **Free tier for searches, plus a 14-day free trial** that unlocks full transcripts and real-time notifications, per the Feb 2026 launch release (https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/).
- Body pages carry "Start free trial" buttons.
- **Self-serve sign-up exists:** `info.myhamlet.com/getstarted` reads "Create your account".
- **Sales-led route as well:**
  - `/contact` and `/contact-sales` cover pricing, plans and enterprise deployments.
  - The homepage offers "schedule a call".
  - Governments are served separately through Hamlet GovCenter (gov.myhamlet.com).
- **API:** the Hamlet Public API spec is public (https://api.myhamlet.com/openapi.json). Every data endpoint, including `GET /v1/locations` and `/v1/locations/{uuid}/government-bodies`, requires a bearer key.
- **Positioning:** marketed to real estate developers, data center operators, journalists and governments. It offers keyword alerts and topic sentiment indices on data centers and zoning. Funding is reported at $5M seed, with some sources saying about $10M.
- **Model: hybrid.** Self-serve trial for individuals; sales call for pricing, teams, enterprise and API.

**SitePath Intelligence** (sitepathintel.com)
- **No public prices.** The homepage says "Access is priced to your organization and the number of people who need it" and asks for estimated seats in a **"Request a demo"** form.
- The app paywall reads: "Annual subscription · add-ons available", with "Request access →".
- Help pages say:
  - monthly or annual billing is available;
  - trials never charge;
  - billing goes through Stripe;
  - team seats usually start at 5 or 25;
  - data centers are a paid add-on.
- **Free tier:** the national map, every county's grade, and headline ordinance and setback rules.
- **Paid tier:** full ordinance text, board-meeting records and vote histories, source PDFs, project decisions, exports and the API (key required).
- **Model: sales-led** (demo first), with Stripe self-management after onboarding.

**CivicSearch:** free, with a newsletter sign-up. **Citizen Portal:** sign-up pages exist (`/signup`, `/free/signup` in its robots.txt), which suggests a free tier with topic and location alerts; pricing was not verified.

## (d) Caveats: what cannot be verified without an account

1. **Hamlet's site blocks all automated access.** Every URL, including robots.txt, sitemap.xml and /coverage/MA, returns HTTP 429 with `x-vercel-mitigated: challenge`, Vercel's JavaScript bot checkpoint. Per instructions, it was not bypassed: no headless browser and no third-party reader proxies.
   - The Wayback Machine and Common Crawl indexes were unreachable from this sandbox.
   - DuckDuckGo answered about 8 per-town queries, then flagged the egress IP as a bot. The scan stopped there rather than pushing through.
   - The 22 "unverified" rows are therefore **unknown, not negative**.
   - The fastest fix is to open `https://www.myhamlet.com/coverage/MA` in a normal browser. It needs no login and should list all 81 towns.
2. **"Bodies covered" for Hamlet** comes only from search snippets. Amherst's "2 governing bodies" is not itemized, and a covered town's page may list more bodies than were indexed.
3. **Alert quality and timeliness cannot be checked without accounts** for Hamlet, SitePath, and Citizen Portal. That includes whether agendas are captured before the meeting or only after the video is posted, whether town meeting warrants are parsed, and how keyword alerts behave.
   - Hamlet and Citizen Portal appear to work mainly from **recorded video and transcripts**. That is after the fact, and it misses boards without PEG or YouTube video. 351watch's edge would be **pre-meeting agenda and warrant PDFs**. This is an inference, not verified.
4. **SitePath's "No tracked activity yet"** is what the public intel page shows. Subscribers might see more, but the page shows no paywall on that section, unlike the sections marked "Sign in to view".
5. **Citizen Portal is undercounted.** Its site returns 403 to automated fetches, and grouped searches return only 10 results each. A per-town check, by searching or with a free account, would likely raise its 6/30.
6. **Search budget:** 31 WebSearch queries plus about 35 DuckDuckGo HTML attempts, most of them blocked. CivicSearch and SitePath were checked by direct fetch: CivicSearch's public place-list JSON and SitePath's sitemap, county and intel pages, all allowed by its robots.txt, which also disallows the data bundles. No accounts were created.

## Demand signals seen in the sample (side observations)

- BESS or solar moratorium activity in 2026 in **Lee** (PB hearing), **Becket** (special act H.5641), **Worthington** (H.5294) and **Westfield** (City Council interim BESS restriction).
- BESS bylaw work in **Sturbridge**, **Sudbury** and **Amherst**.
- **Charlton's** 150 MW BESS dispute.
- The AG disapproving **Carver's** moratoria.
- SitePath still shows "no active moratorium" for Berkshire and Hampshire, and no rules on file for Lee, Becket or Westfield. That is a concrete freshness gap a town-level monitor would close.

## Verdict

There is room for a Massachusetts-focused monitor:
- **Hamlet** reaches about 23% of Massachusetts municipalities and shows no visible land-use body coverage in this sample.
- **SitePath** works at county and bylaw level, with no Massachusetts meeting tracking.
- **CivicSearch** is negligible here.

The real competitor is **Citizen Portal**, which already writes AI articles from planning board, conservation commission and select board meetings in many small Massachusetts towns.

Position 351watch on:
- all 351 towns;
- pre-meeting agenda and warrant capture, not post-meeting video;
- clean-energy and land-use classification (BESS, solar, moratoria, AG bylaw reviews);
- structured alerts.

Before building, spend about 30 minutes in a normal browser and a free Citizen Portal account to confirm Citizen Portal's per-town depth and whether it captures agendas before meetings.
