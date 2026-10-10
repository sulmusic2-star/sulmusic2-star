# Hamlet and Citizen Portal: what they actually deliver for Massachusetts boards

Checked 2026-10-10 (Saturday), for 351 Watch. Goal: find out whether either service alerts on **agendas before meetings** or only summarizes **recordings or minutes after meetings**, so 351 Watch makes only claims it can prove.

**Bottom line**
- **No account was created on either service.** Both sites blocked a plain Playwright Chromium on the first page view (the terms page), so the rules required stopping. Citizen Portal's terms, as shown in the search index, also bar building a competing product.
- Everything below comes from three things only: Hamlet's public API spec (no login), third-party search-index snippets, and one third-party news article.
- **Do not claim "competitors only cover meetings after the fact."**
  - Hamlet's API models agendas and has "agenda-monitoring topics."
  - Hamlet's marketing promises alerts "the moment agendas are posted."
  - Citizen Portal has published agenda-preview articles for at least one Massachusetts town (Warwick).

## Verdict table

| Service | Agenda-based pre-meeting alerts? | MA bodies covered | Test cases found (6) | Pricing | ToS notes |
|---|---|---|---|---|---|
| **Hamlet** (myhamlet.com) | **Claimed yes, unverified.** API: `Meeting.has_agenda` ("Whether a processed agenda exists for this meeting"), an `Agenda` tree of `AgendaItem`, and `AgendaItem.matched_topics` ("Agenda-monitoring topics matched on this item..."). Marketing snippets: "notify your team the moment agendas are posted" and "continuous agenda tracking, instant alerts on topics like impact fees and zoning changes". Could not check delivery for any MA board (site challenge, no account). | Self-reported **81 cities + 1 county** in MA ("4,886+" MA meetings). Chicopee (not a sample town) lists 15 bodies, including Planning Board, ZBA and Conservation Commission. In the 30 sample towns only odd bodies are indexed: Amherst ("2 governing bodies"), Fitchburg Park Commissioners, Westford Pedestrian Safety Committee. No sample-town PB, ZBA or ConCom page was seen. | **0 of 6 verifiable.** Every myhamlet.com page is behind a Vercel checkpoint, and the search index shows no page for any of the 6 items. | No public price. "Talk to sales" for plans. Free tier for searches, plus a **14-day free trial** that "unlocks full transcripts and real-time notifications as new results are indexed" (PublicCEO, 2026-02-18). In-app pricing not seen. | **Could not read.** www.myhamlet.com/terms returned the Vercel Security Checkpoint (HTTP 429, `x-vercel-mitigated: challenge`, "Failed to verify your browser, Code 21"). The terms are unread, so there was no sign-up. |
| **Citizen Portal** (citizenportal.ai) | **Unclear, mostly no in practice.** It claims to pull "directly from public meeting agendas, video, minutes, and government documents". Alerts are worded "instant alerts when your location has a **new meeting**" and "notified when your topic is **debated** in any meeting". Agenda-preview articles exist for Warwick, MA (June 2026). Every sample-town article found is a recap of a meeting already held. | Found for **18 of 30** sample towns. Land-use boards (PB, ZBA, ConCom or Pittsfield's CDB) found in **13 of 30**. Select boards and councils in many. No town meeting sessions seen for sample towns. Details in the table below. | **0 of 6 shown before the meeting.** 0 of 2 past meetings shown afterward either (Fitchburg Oct 6, Northampton Oct 8, as of Oct 10). Carver: no coverage at all. Related earlier items exist: Pittsfield CDB vote of Apr 21; Sudbury BESS bylaw drafting. | Conflicting public listings: Citizen Pro **$12/mo (2 topic alerts)** or **$15/mo**; Civic Analyst **$24/mo (10 topic alerts)**; Journalist Pro **$49/mo (50 topic alerts)**; lifetime "Founding Member" **$199**, **$299** or **$999** one-time, depending on page. In-app pricing not seen. | **Prohibits competitive use.** Terms (https://citizenportal.ai/terms, "Last updated: December 2024"), as quoted in the search index: users may not "**build a competitive product or service, or copy any features or functions of the Services**". The live page itself returned a Cloudflare challenge. Do not sign up for benchmarking. |

## Access log (what was attempted, and where it stopped)

All browser visits used Node Playwright with `/opt/pw-browsers/chromium`, the default user agent, no stealth plugins, and one view per URL. All times are UTC on 2026-10-10.

| Host / URL | Result | Action |
|---|---|---|
| https://citizenportal.ai/terms (browser) | HTTP 403, `cf-mitigated: challenge`, "Performing security verification", Ray ID a486b422c8cb5d21 | **Stopped all citizenportal.ai access.** Proof: `proof/citizenportal_terms_cloudflare_challenge_2026-10-10.png` |
| https://www.myhamlet.com/terms (browser) | HTTP 429, `x-vercel-mitigated: challenge`, "Failed to verify your browser, Code 21" | **Stopped all www.myhamlet.com access.** Proof: `proof/hamlet_terms_vercel_checkpoint_429_2026-10-10.png` |
| https://info.myhamlet.com/ (browser) | Redirects to www.myhamlet.com, which serves the same checkpoint | Stopped. Proof: `proof/hamlet_info_site_redirects_to_vercel_checkpoint_2026-10-10.png` |
| https://gov.myhamlet.com/ (browser) | 404 DEPLOYMENT_NOT_FOUND. The GovCenter host is gone. | none |
| https://api.myhamlet.com/openapi.json (curl) | HTTP 200, public, no challenge. sha256 `9544787e…38f1cf` (same file as a 14:34 UTC download earlier today) | Saved: `proof/hamlet_openapi_2026-10-10.json` |
| api.myhamlet.com `/health`, `/`, `/docs`, `/reference` | `/health` returns `{"status":"ok","version":"0.1.0"}`. `/` returns 404 JSON. `/docs` returns 302 to www.myhamlet.com/docs (not followed). `/reference` returns 404. | none |

Not done, per the rules:
- No CAPTCHA or challenge solving, and no alternate fetchers, reader proxies or archives to reach challenged pages.
- No account, no payment details, no Gmail access.
- `competitor_accounts.txt` was **not** created, because there is nothing to store.

Search-index lookups (the WebSearch tool) and one third-party article fetch (publicceo.com) were the only other sources. Snippets marked *(index)* below are the search tool's quotes of the indexed page, not a page I viewed myself.

## 1. Hamlet's public API spec (https://api.myhamlet.com/openapi.json)

`info.title` = "Hamlet Public API", version 0.1.0. Description: "Public API for programmatic access to Hamlet civic intelligence data: government meetings, transcripts, and related records from local governments." Auth is `bearerAuth` on every `/v1` route.

**Endpoints:**
- `GET /v1/meetings` (`updated_since`, `cursor`, `government_body_uuid`)
- `GET /v1/meetings/{uuid}/agenda`
- `GET /v1/meetings/{uuid}/transcript`
- `GET /v1/locations`
- `GET /v1/locations/{uuid}/government-bodies`
- `GET /health`

**Schemas:** `Health`, `MeetingList`, `Meeting`, `Error`, `Agenda`, `AgendaItem`, `MatchedTopic`, `Transcript`, `LocationList`, `Location`, `GovernmentBodyList`, `GovernmentBody`.

**Agenda ingestion: yes.**
- `Meeting.has_agenda`: "Whether a processed agenda exists for this meeting."
- `GET /v1/meetings/{uuid}/agenda`: "Returns the meeting's agenda as a hierarchical tree of items, nested by parent into `children` and ordered as published... If the meeting has more than one agenda, the most recently updated is returned."
- `Agenda` fields are `uuid`, `meeting_uuid`, `created_at`, `updated_at` and `items`.
  - The example agenda `created_at` is `2026-05-19T18:00:00.000Z`, for a meeting `date` of `2026-05-20`. That is the day before the meeting, which is consistent with pre-meeting capture.
  - It is only an example value, not evidence for any real meeting.
- `AgendaItem` fields are `item_number`, `item_title`, `item_description`, `matched_topics` and `children`.
- `AgendaItem.matched_topics`: "**Agenda-monitoring topics** matched on this item, filtered to the topics your API subscription for this meeting's government body includes."
- `MatchedTopic.name`: "The matched agenda-monitoring topic's name." Example: "Housing".

**Not in the data model** (confirmed by text search of the whole spec):
- No agenda source URL or PDF link, and no document type. The words "pdf" and "document" do not appear.
- No **posted or published timestamp** for the agenda. "published" appears only in "ordered as published" and "numbering as published". The only times are Hamlet's own `created_at` and `updated_at`.
- No minutes object ("minutes" appears only in the example item title "Approve minutes of the May 5 meeting").
- No video URL.
- No alert, subscription or webhook resource. `"webhooks":{}` is empty. "alert" never appears. Topic subscriptions are set up outside the API ("your API subscription").
- `GovernmentBody.type` lists "CITY_COUNCIL, PLANNING_COMMISSION, OTHER, BOARD_OF_SUPERVISORS, SCHOOL_BOARD". These are California-style types, with no Select Board, ZBA, Conservation Commission or Town Meeting type, so MA boards likely land in `OTHER`. `Location.type` is CITY, COUNTY or STATE; there is no TOWN.

**Transcripts:** `Transcript` is a JSONL download of utterances, timestamped "absolute against the recording", plus `generated_at`. This is the after-the-meeting product.

**Reading:**
- Hamlet's data model carries **both** pre-meeting agendas, with topic matching, and post-meeting transcripts.
- It does not expose when the town posted the agenda, so its own timeliness can't be audited through the API.
- Proof: `proof/hamlet_openapi_agenda_schema_excerpt_2026-10-10.png`.

## 2. Hamlet's public claims (search index; site not viewable)

**Agenda alerts** *(index, myhamlet.com/about-us and myhamlet.com/home)*:
- "continuous agenda tracking, instant alerts on topics like impact fees and zoning changes, and early warnings on regulatory shifts"
- "notify your team the moment agendas are posted"
- "Hamlet reads the public record of 6,600+ governing bodies: 94,000+ meeting transcripts, plus the agendas behind them."
- Town and body pages carry "Start free trial" for tracking "the topics they care about on every agenda".

**Keyword alerts** (PublicCEO, 2026-02-18, fetched): "The platform now also includes full meeting transcripts, saved searches and keyword alerts". The trial "unlocks full transcripts and real-time notifications as new results are indexed". It covers "more than 3,000 city councils, planning commissions and additional governing bodies". Agendas are not mentioned in that article.

**Massachusetts coverage** *(index)*:
- myhamlet.com/coverage/MA: "Search 4,886+ Massachusetts city council, planning commission, and board meetings... across 81 cities and 1 counties"
- The coverage map lists Massachusetts as "82 Cities & Counties".
- Chicopee, MA has "15 governing bodies covered", including Planning Board, Zoning Board of Appeals, Conservation Commission and City Council committees.
- The Chicopee Planning Board page reads "View meeting schedules, agendas, and video transcripts". Its latest listed meeting was Mar 5, 2026 (past).

**Sample towns** (earlier DuckDuckGo work in `../Meeting monitor validation/coverage_check.md`, not re-verified because the site is challenged):
- Amherst: partial ("2 governing bodies covered").
- Fitchburg: Board of Park Commissioners only.
- Westford: Pedestrian Safety Committee only.
- The other 27: no evidence.

**Pricing:** not published. The contact page routes "pricing, plans, partnerships, and enterprise deployments" to "Talk to sales".

## 3. Citizen Portal public evidence (search index; site not viewable)

**Sources it claims** *(index, citizenportal.ai/about-us and /learn)*: it pulls "directly from public meeting agendas, video, minutes, and government documents". It turns "60,000+ meetings each month into structured, timestamped articles". Meeting ("source") pages carry a timestamped segment breakdown, a summary, and a transcript where one exists. The Great Barrington Selectboard page for July 6, 2026 says "No transcript available".

**Alerts** *(index)*:
- "instant alerts when your location has a new meeting"
- "notified when your topic is debated in any meeting"
- Topic pages offer email alerts "when new meetings or documents mention it"
- Tiers include 2, 10 or 50 topic alerts.

It is not clear whether a "new meeting" alert fires when the agenda is posted or when the recording is processed.

**Agenda-preview articles do exist** (Warwick, MA, Franklin County, June 2026):
- 8360106 "Warwick Selectboard posts June 15 agenda including WCS playground update..."
- 8446509 "Selectboard agenda flags possible hearing on Six Town Regionalization Planning Board proposal" (body: "No motion, vote tally, or formal action is recorded in the agenda")
- 8446510 "Selectboard to review and vote on Auctions International contract"
- 8446513 "Warwick Selectboard agenda includes discussion and possible vote on coordinator position"

Publication timestamps are not visible through the index, so whether these went up before the meeting is unverified. Their wording suggests it.

**Typical MA article = post-meeting recap.** Every sample-town article found describes a meeting that already happened, for example:
- "At the June 24 Planning Board meeting..." (Sudbury)
- "On July 27, the board named..." (Lee)
- "voted Oct. 1 to conditionally approve a decommissioning bond" (Charlton)
- "The Select Board finalized the fall town meeting warrant on Sept. 28" (Dartmouth)

The index reports article ages only as relative ("about 172 days old"), so exact publication lag could not be measured. Article IDs are not in meeting-date order; for example, 10495674 covers a July meeting and 10358958 a Sept. 28 meeting. Some articles therefore appear weeks or months after the meeting.

**Filing quirks:**
- Fitchburg City Council is filed under `.../School-Boards/Fitchburg-Public-Schools/`.
- Sudbury Planning Board items are under `.../School-Boards/Lincoln-Sudbury/`.
- Lee and some Great Barrington items are under `.../Berkshire-County/Lenox-Dale/`.
- Westford Planning Board is under `.../school-boards/westford-public-schools/`.

A town filter in Citizen Portal may therefore miss these, though this is unverified in the app.

**Pricing** *(index, conflicting)*:
- /memberships: Citizen Pro $15/mo with topic alerts, and Founding Member $299 one-time.
- /signup: Citizen Pro $12/mo (2 topic alerts), Civic Analyst $24/mo (10), Journalist Pro $49/mo (50), lifetime $999.
- /founding-member and the checkout page: lifetime $199 one-time.

## 4. Test cases (items 351 Watch's crawler found on posted agendas)

351 Watch's evidence:
- `projects/351watch/data/agenda_hits.json`, `generated` 2026-10-10T15:11:10Z.
- All four agenda PDFs checked (Fitchburg, Pittsfield, Westford, Northampton) returned HTTP 200 `application/pdf` at 15:44 UTC.
- Hits carry no per-item first-seen time, so the crawl run time is the only provable capture time.

| # | Item | Meeting | 351 Watch capture (provable) | Hamlet | Citizen Portal |
|---|---|---|---|---|---|
| 1 | Fitchburg City Council: temporary zoning moratorium on commercial BESS (Ch. 181) | Tue Oct 6 | From the agenda PDF, but crawled Oct 10, **after** the meeting | Not verifiable (challenge). The index shows only Fitchburg Park Commissioners. | Council covered in general (e.g. 9650011, 10206206). **No article on the Oct 6 moratorium** found as of Oct 10. The index has Leominster (8516864) and Chicopee (9920119) BESS-moratorium recaps, but not Fitchburg. |
| 2 | Pittsfield City Council: "Battery Energy Storage Systems" zoning amendment (O&R report) | Tue Oct 13 | From the agenda packet, **3 days before** | Not verifiable. No Pittsfield page in the index. | Only an earlier step: 9686612 "Community Development Board will petition update to BESS zoning rules" (Apr 21 CDB meeting, written after it). **No preview of Oct 13.** |
| 3 | Westford Select Board warrant review: new §6.6 Small Clean Energy Infrastructure Facilities (also PB hearing Oct 5; STM Oct 26) | Tue Oct 13 / Mon Oct 26 | From the agenda, **3 days and 16 days before** | Not verifiable. The index shows only Westford Pedestrian Safety Committee. | **Not found.** Westford PB covered in general (8026389, Open Space plan). |
| 4 | Northampton Planning Board: consolidated local permitting for small clean energy (225 CMR 29.00) | Thu Oct 8 | From the agenda PDF, crawled Oct 10, **after** the meeting | Not verifiable | Northampton PB, ZBA and ConCom covered in general (7392950, 7591082, 7361488). **No article on this item** found as of Oct 10. |
| 5 | Sudbury Planning Board: Battery Energy Storage System bylaw (also on Sep 9 and Sep 23 agendas) | Wed Oct 14 | From the agenda, **4 days before** | Not verifiable | Earlier recaps of the BESS bylaw work: 9876698, 9885166, 8581383 (June 24 PB briefing). **No preview of Oct 14.** |
| 6 | Carver Planning Board: Federal Pond Solar, LLC special permit and site plan, with coupled BESS (ConCom NOI Oct 7) | Tue Oct 13 | From the agenda, **3 days before** | Not verifiable | **Carver not covered**: no Carver, MA article in any search. |

**Caveat:** search indexes lag. Absence from the index two to four days after a meeting does not prove Citizen Portal will not publish an article later, or that it has no article yet.

**Re-check:** search again for items 1 to 6 after Oct 20, then record when (if ever) each appears.

## 5. Sample-town coverage (30 towns)

- **Citizen Portal**: checked by per-town `site:citizenportal.ai` index searches on 2026-10-10. Each search returns 10 results, so "not found" is a lower bound, not a definitive no.
- **Hamlet**: from the earlier DuckDuckGo work, not re-verifiable (challenge).

| Town | Citizen Portal bodies seen (example article IDs) | Hamlet (earlier, unverified) |
|---|---|---|
| Lee | Select Board (9460442, 8761059; filed under Lenox-Dale) | no evidence |
| Becket | not found | no evidence |
| Worthington | not found | no evidence |
| Pittsfield | City Council (6299665), Community Development Board (9686612), a commission (9559951) | no evidence |
| Great Barrington | Selectboard (8409875), Planning Board (8777088), Conservation Commission (8302534) | no evidence |
| Northampton | Planning Board (7392950), ZBA (7591082), ConCom (7361488), council committees (6423997) | no evidence |
| Amherst | not found (only Amherst, NY) | partial: "2 governing bodies covered" |
| Westfield | not found (only legislature mentions) | no evidence |
| Sturbridge | not found | no evidence |
| Sutton | not found (only Sutton, VT) | no evidence |
| Shrewsbury | not found | no evidence |
| Westborough | Planning Board (7314742), Select Board (7329352, 7317184), Advisory Finance Committee (9614992) | no evidence |
| Grafton | Select Board with School Committee (7294312) | no evidence |
| Charlton | Planning Board (5991782), ConCom (6702200), Select Board (5942864) | no evidence |
| Leominster | City Council (8516864) | no evidence |
| Fitchburg | City Council (9650011) | partial: Board of Park Commissioners |
| Framingham | Planning Board (7317278), City Council (7164303) | no evidence |
| Sudbury | Planning Board (9876698, 8581383) | no evidence |
| Westford | Planning Board (8026389), Affordable Housing Trust (8763340) | partial: Pedestrian Safety Committee |
| Billerica | Planning Board (8070214) | no evidence |
| Andover | not found (Andover, ME and North Andover schools only) | no evidence |
| Wakefield | Town Council, tri-board and committees (9907320, 7951243); no land-use board seen | no evidence |
| Plymouth | not found | no evidence (Hamlet's one MA county appears to be Plymouth County) |
| Carver | not found | no evidence |
| Middleborough | Planning Board (6363417), Select Board (6363321); items from early 2025 | no evidence |
| Bridgewater | Planning Board (8314949) | no evidence |
| Medway | School Committee only (7159537) | no evidence |
| Fall River | Planning Board (8160903, 9925432) | no evidence |
| Barnstable | not found (Dennis, Bourne, Yarmouth and Falmouth instead) | no evidence |
| Dartmouth | Planning Board (9743972), Select Board (10358958) | no evidence |

**Citizen Portal totals:**
- A municipal body was seen in **18 of 30** towns.
- A land-use board (PB, ZBA, ConCom or CDB) was seen in **13 of 30**.
- **12 of 30** had nothing found: Becket, Worthington, Amherst, Westfield, Sturbridge, Sutton, Shrewsbury, Andover, Plymouth, Carver, Medway and Barnstable.
- Town meeting sessions were not seen for any sample town. Warrants show up only through Select Board or Finance Committee recaps.

**Hamlet:** 3 of 30 partial, with no land-use body.

## 6. Keyword alert setup ("battery storage", Massachusetts)

Not done, because no account exists on either service. The only alert features documented are public descriptions:
- **Hamlet:**
  - "saved searches and keyword alerts"
  - "real-time notifications as new results are indexed" (trial)
  - Agenda Monitoring alerts "the moment agendas are posted" (sales product)
  - The API exposes agenda-monitoring topic matches per agenda item, scoped by "your API subscription for this meeting's government body".
  - Frequency, delivery channel, MA availability and whether trial users get agenda alerts were not seen.
- **Citizen Portal:**
  - Topic alerts (2, 10 or 50 depending on tier)
  - Location "new meeting" alerts
  - Email alerts on topic pages
  - Frequency settings and agenda-versus-recording triggering were not seen.

## 7. What 351 Watch can and cannot claim

**Safe, provable claims** (keep dated evidence):
- "351 Watch reads the posted agenda PDFs and warrants themselves and flags items before the meeting." Proof: the Oct 10 crawl captured the Pittsfield, Westford, Carver and Sudbury items 3 to 4 days ahead, and Westford's STM article 16 days ahead.
  - **Add a per-item `first_seen` timestamp to the crawler** so every future "N days before the meeting" claim can be backed up. The current hits have only a run-level `generated` time.
- "In our 6-item test (Oct 2026 BESS, solar and clean-energy agenda items in Fitchburg, Pittsfield, Westford, Northampton, Sudbury and Carver), none appeared in Citizen Portal's publicly indexed articles before the meeting, and Carver had no Citizen Portal coverage at all." State the date and that it was a public-index check.
- "Hamlet lists 81 Massachusetts cities plus 1 county (out of 351 municipalities)." Cite Hamlet's coverage page and the date.
- "351 Watch covers boards without video": select boards, planning boards, ZBAs and ConComs that post agendas but don't stream. This is true by design, but only claim it for towns the crawler actually automates (24 of 30 sample towns today).

**Do not claim:**
- "Hamlet / Citizen Portal only summarize meetings after they happen." Hamlet's API and marketing say otherwise, and Citizen Portal has published agenda previews (Warwick).
- "Hamlet doesn't cover Massachusetts planning boards." Chicopee's Planning Board, ZBA and ConCom are on Hamlet.
- "Citizen Portal doesn't cover town X." Index absence is a lower bound.
- Any claim about competitors' alert timing, alert settings or in-app pricing. None of it was observed.
- Statewide "all 351 towns" coverage, unless 351 Watch actually automates them.

**Possible next step** (owner's decision, not done): Hamlet's sales team offers a demo, and its terms are still unread. A human, in a normal desktop browser, could:
- read Hamlet's terms,
- ask Hamlet sales whether agenda alerts cover MA select boards, ZBAs, ConComs and town meeting warrants, and
- ask what lead time those alerts give.

Under its terms as indexed, Citizen Portal should not be used for competitive evaluation.

## Sources

- Hamlet API spec: https://api.myhamlet.com/openapi.json (copy in `proof/`)
- PublicCEO, "Hamlet launches nationwide public meeting coverage...", 2026-02-18: https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/
- Hamlet pages (index only): https://myhamlet.com/about-us, https://www.myhamlet.com/about, https://www.myhamlet.com/coverage, https://www.myhamlet.com/chicopee-ma, https://www.myhamlet.com/chicopee-ma/planning-board--6193, https://www.myhamlet.com/contact
- Citizen Portal pages (index only): https://citizenportal.ai/terms, https://citizenportal.ai/memberships, https://citizenportal.ai/signup, https://citizenportal.ai/founding-member, https://citizenportal.ai/about-us, https://citizenportal.ai/learn
- Citizen Portal articles: `https://citizenportal.ai/articles/<id>/...`, with IDs cited inline. The Warwick agenda previews are 8360106, 8446509, 8446510 and 8446513, e.g. https://citizenportal.ai/articles/8446509/Massachusetts/Franklin-County/Warwick/Selectboard-agenda-flags-possible-hearing-on-Six-Town-Regionalization-Planning-Board-proposal
- 351 Watch crawl: `/home/user/sulmusic2-star/projects/351watch/data/agenda_hits.json` (generated 2026-10-10T15:11:10Z)
- Earlier coverage work: `../Meeting monitor validation/coverage_check.md`

**Proof files** (`proof/`):
- `citizenportal_terms_cloudflare_challenge_2026-10-10.png`
- `hamlet_terms_vercel_checkpoint_429_2026-10-10.png`
- `hamlet_info_site_redirects_to_vercel_checkpoint_2026-10-10.png`
- `hamlet_openapi_agenda_schema_excerpt_2026-10-10.png`
- `hamlet_openapi_2026-10-10.json`
