# Coverage without letters: official sources that already carry the hearings we cannot read

*Run 2026-11-06 by the crawler engineer. The owner said on Nov 6: "we aren't sending letters out, find ways around that." This note records what was checked, what each source allows, what was built, what it yields and what it does not cover. Nothing here needed anyone's permission; nothing was posted, no form was submitted, no challenge was solved. Every request went through `crawler/watch351/fetch.py` (AgendaAheadBot, robots.txt on every hop, at most one request a second per host, crawl-delay honoured).*

**Code:** `crawler/watch351/sources/notice_feeds.py` (shared helpers), `ny_enb.py`, `ny_ores.py`, `oh_opsb.py`, `md_psc_cpcn.py`; runner and hand-check tooling in `crawler/experiments/notices_test.py`. **Outputs:** `data/test/notices/` only (`<source>_items.json`, `<source>_hits.json`, `<source>_ledger.json`, `runs/`, `stats.json`, `precision_worksheet.json`, `precision_judgments.json`). The feeds refuse to write to `data/` or `data/sources/` while `notice_feeds.GATED` is true, so nothing reaches production until promoted.

## 1. The short version

| Source | Allowed? | Built? | Yield | Precision (hand check) |
|---|---|---|---|---|
| masspublicnotices.org (MA) | No. Terms: personal, non-commercial use only; "You may not engage in any screen scraping, database scraping, or spidering, or ... any other automated means to collect information"; no database, compilation or cache. robots.txt allows `*`. | No | none | none |
| nypublicnotices.com (NY) | No. Redirects to newyork.column.us (Column). Column's Terms of Use: "You may not use any scraper, crawler, spider, robot or other automated means of any kind to access or copy data on the Site." Its public API needs a bearer token (an account). | No | none | none |
| publicnoticevirginia.com (VA) | No. Same platform and same words as Massachusetts. | No | none | none |
| mdpublicnotices.com (MD) | No. That domain no longer resolves; the MDDC Press Association's site is mddcpublicnotices.com, same platform and terms, plus liquidated damages of "$100 per public notice affected or $10,000 per incident" for putting notices in a database. | No | none | none |
| mipublicnotices.com (MI) | No. Run by Detroit Legal News Publishing; terms allow download "for your internal use and not used as a reseller or data center or service bureau" and forbid publishing, transmitting or distributing content. robots.txt is a 404. The app's own API needs no key, but the terms rule out what we would do with it. | No | none | none |
| publicnoticesohio.com (OH) | No. Terms: personal, non-commercial use only; no republishing "for commercial purposes" without ONA's written consent. | No | none | none |
| ripublicnotices.com (RI) | No. robots.txt ends with `User-agent: * Disallow: /` (only Googlebot, Slurp, MSNBot and ia_archiver are allowed). Rhode Island's meeting notices already reach us through the Secretary of State portal (`adapters/ri_sos.py`). | No | none | none |
| NY DEC Environmental Notice Bulletin | Yes. robots.txt disallows only the bulletin's own listing page; every notice page and the sitemaps are allowed. State site, no terms beyond the standard notice. | **ny_enb** | 31 notices a week, 6 relevant hits a week (60-day run: 267 notices, 51 hits, 45 places) | 26 of 30 (0.87); town right 30 of 30 |
| NY ORES permit applications (dps.ny.gov) | Yes. Drupal default robots.txt; one page. | **ny_ores** | 52 applications on the docket, 9 pending; 18 hits (one per host town) | 18 of 18; town right 18 of 18 |
| MA Environmental Monitor (MEPA) | No, not reachable. The Monitor moved to mass.gov in 2021 and mass.gov answers 403 ("Not allowed") to AgendaAheadBot on every page including robots.txt; eeaonline's copy stops at July 2021; the ePLACE portal and the DPU/EFSB file room are script-only pages. | No | none | none |
| Ohio Power Siting Board | Yes, through the PUCO docket (dis.puc.state.oh.us): robots.txt disallows only a list of named AI crawlers. opsb.ohio.gov itself answers 404 to every page. | **oh_opsb** | 62 case records read, 85 items, 5 hits in 30 days (3 local public hearings, 2 Board entries) | 5 of 5; county right 5 of 5 (2 from the hearing venue) |
| Michigan PSC siting (PA 233) | No, not reachable. michigan.gov answers 403 (Akamai) on every page; E-Dockets (mi-psc.my.site.com) allows robots but every page is a Salesforce script shell ("Loading"); the sitemaps list hearings and filings but the pages render nothing without scripts. | No | none | none |
| Virginia DEQ permit-by-rule notices | No, not reachable. deq.virginia.gov answers 403 (Akamai) on every page including robots.txt. | No | none | none |
| Maryland PSC CPCN dockets | Yes. psc.maryland.gov: robots.txt allows all with `Crawl-delay: 10` (honoured). The case files (webpsc.psc.state.md.us) sit behind a Cloudflare challenge and are not read. | **md_psc_cpcn** | 138 cases (2024 to 2026), 8 public comment hearings listed, 8 hits | 8 of 8; county right 8 of 8 |

Of the 36 hits judged on the three docket feeds and the 30 on the ENB, 57 were real hearings, comment periods, decisions or docket entries on our topics; the 4 misses are all Environmental Notice Bulletin permit renewals at quarries (a water withdrawal, a discharge permit, an air permit) and one comprehensive plan amendment.

## 2. Press-association notice sites: what each one says

I read each site's robots.txt and its terms page with the project's fetcher before anything else. The six associations on the shared ASP.NET platform (Massachusetts, Virginia, Ohio, Maryland and the others the earlier note covered) publish the same terms with small edits; New York and Michigan run different platforms with their own terms; Rhode Island's site blocks robots outright.

- **Massachusetts** (masspublicnotices.org, Massachusetts Newspaper Publishers Association). robots.txt: `User-agent: *` allowed, a few folders disallowed, a long list of AI crawlers disallowed by name (not ours). Terms of Use, section 3: "download or print individual pages of this site solely for your own personal, non-commercial use ... No other use is permitted. You may not, for example, incorporate the content in any database, compilation, archive or cache ... You may not engage in any screen scraping, database scraping, or spidering, or collection of personally identifiable information, or use of any other automated means to collect information from the site. You may not use any software, tool, or other device (such as browsers, spiders, or avatars) to search the site, other than the search functionality offered through the site." The site also has neither an RSS feed nor a category page; the only way in is the search form (a POST). Out on terms and on form.
- **Virginia** (publicnoticevirginia.com, Virginia Press Association). Same robots.txt, same section 3 wording ("no screen scraping, database scraping, or spidering"). Out.
- **Ohio** (publicnoticesohio.com, Ohio News Media Association). Same robots.txt. Terms, section 1: a "limited right to access and use this Site for your personal, non-commercial use only. You agree (a) not to copy, reproduce, republish ... any content on the Site for commercial purposes ... (d) except with ONA's written consent, not to ... commercially exploit this Site or Site content." The terms do not name automated reading, but republishing excerpts in an alert service is what they reserve for written consent. Out on terms; the "Zoning and Planning" popular search exists but is a POST.
- **Maryland** (mdpublicnotices.com does not resolve; the association's page at mddcpress.com/mddc-public-notices links to mddcpublicnotices.com, MDDC Press Association). Same platform and the Massachusetts wording, with section 9 "Liquidated damages": "(a) for incorporating the site content in any database, compilation, archive or cache, $100 per public notice affected or $10,000 per incident, whichever is greater." Out.
- **New York** (nypublicnotices.com redirects to newyork.column.us, Column Software PBC, the New York Press Association's partner since February 2026). newyork.column.us and api.column.us answer 404 for robots.txt (allowed); the search page is a Next.js app that queries an Elasticsearch backend at api.column.us by script, and its subscriptions are POSTs. Column's Terms of Use (help.column.us, article 937216, revised Aug 12, 2024), section 2: "You may not use any scraper, crawler, spider, robot or other automated means of any kind to access or copy data on the Site, deep-link to any feature or content on the Site, bypass our robot exclusion headers or other measures." Column's documented public API ("accessing notices by state") needs a bearer token issued to an account. Out on terms; the API is an account, not a public feed.
- **Michigan** (mipublicnotices.com, Detroit Legal News Publishing LLC for the Michigan Press Association). robots.txt is a 404. The site is a React app over `/api/v1/` endpoints (`/api/v1/notices/`, `/api/v1/search/search`, `/api/v1/counties`) that the browser calls without a key. Terms of Service (Oct 1, 2024), 2.2 and 2.3: "You may not modify, publish, transmit, participate in the transfer or sale of, reproduce (except as provided in Section 2.3), create new works from, distribute, perform, display, or in any way exploit, any of the Services"; downloaded content must be "used for your internal use and not used as a reseller or data center or service bureau." Showing a notice's line on a town page is publishing. Out on terms.
- **Rhode Island** (ripublicnotices.com). robots.txt: `User-agent: * Disallow: /`. Out on robots; nothing else was requested. Rhode Island's open-meeting notices and agendas already come from the Secretary of State portal.

What this means: the press-association route is closed everywhere without a licence, as the Oct 12 note (`cheap_township_coverage.md`, section 4) already found for the states it read. The owner can revisit it only by asking an association for a licence, which is a letter. The rest of this note is about sources that need no one's leave.

## 3. State bulletins and dockets

### 3.1 New York: DEC Environmental Notice Bulletin (built: `ny_enb`)

The ENB is the weekly bulletin (Wednesdays) of DEC permit applications, SEQR determinations, hearings and comment periods. Each notice is its own page, `dec.ny.gov/news/environmental-notice-bulletin/<issue date>/[seqr|completed-application|public-notice/]<town>-<project>`, titled "Town of X - Project". The SEQR notices are the useful ones: a town board, planning board or zoning board, as lead agency, says what it is deciding (a solar array, a battery system, a zoning law, a planned development district) around the time it votes. The completed-application notices are DEC permits (mines, wetlands, discharges) with the comment deadline and the DEC contact.

- robots.txt: `Disallow: /news/environmental-notice-bulletin` and `Allow: /news/environmental-notice-bulletin/*`, the same pattern the site uses for every listing page. The listing page is not read. The notice pages and the sitemap (`/sitemap.xml`, 15 pages) are allowed, and the module asks the fetcher before every request.
- How notices are found: the sitemap pages carry every notice URL with its issue date (15,807 notices back to 2019). The site regenerates the sitemap on its own schedule; on Nov 6 it ran to the Oct 21 issue (the Oct 28 and Nov 4 issues were not yet listed), so a notice can reach us a week or two late. There is no RSS for the bulletin (`/rss.xml` is empty; the per-section feed paths are 404).
- Fields read: title, publish date, category (the notice's first line: Negative Declaration, Positive Declaration, Notice of Completed Application, SPDES permit renewal, Adirondack Park Agency completed application), municipality and county, lead agency or applicant, description, permits applied for, comment deadline ("Deadline for Comments", "Comment Period Ends", "comments must be submitted no later than"), hearing date and place where a notice gives one (one in 267).
- Attribution: the title's "Town of / City of / Village of X" is resolved to the site's name for the place: a configured row in `data/towns_ny.json` when there is one, else the bare town name (every New York town and city name is checked against `data/neighbors.json`), else "X (village)" or "X (city)", the site's convention. A notice naming two places ("Village of Bainbridge and Town of Bainbridge") gives one hit per place. Statewide notices get no hit.
- Topics: the shared matcher plus docket words (mines and quarries to `extraction`, warehouses with a size to `large_development`, both gated topics the site has no label for; wind, transmission and gas plants to `clean_energy_siting`; zoning laws under their New York names: "Local Law Amending Zoning Code", "Zoning Map Update", "Zoning Text Amendments", planned development districts).
- Yield (60 days, Sep 7 to Nov 6): 267 notices, 52 relevant, 51 hits on 45 places; about 31 notices and 6 hits a week. By topic: extraction 18, zoning_amendment 16, solar 7, battery_storage 6, clean_energy_siting 4, large_development 3, wireless 1. By date: 31 SEQR determinations with no date of their own (meeting_date null), 19 comment deadlines, 1 hearing.
- Where the hits land: 5 on places we read, 4 on configured places we cannot read today (Halfmoon twice, Huntington, Hurley), 42 on New York towns and villages that are not on the site at all (Avon, Cambria, Hamburg, Ithaca, Lancaster, Lyons, Tully, Wheatfield and others). The second group is the point: those are places with neither a page nor an agenda reader, and the bulletin names their boards and their projects anyway.
- Precision: 26 of 30 sampled hits (0.87). The four misses are a comprehensive plan amendment with no zoning change and three permit renewals (water withdrawal, discharge, air) at facilities that happen to be quarries. The town was right in all 30. Judgments: `data/test/notices/precision_judgments.json`.
- Cost: one sitemap index plus 15 sitemap pages (about 7 MB) and the new notice pages, once a day.

### 3.2 New York: ORES permit applications (built: `ny_ores`)

The Office of Renewable Energy Siting and Electric Transmission permits every renewable facility of 25 MW or more and the large transmission lines; the towns are consulted but do not decide. `dps.ny.gov/ores-permit-applications` lists every application by stage (notices of intent, pending completeness, incomplete, complete and under review, permitted, withdrawn or relinquished, denied, declaratory rulings) with the permit number, project name and a description naming the towns, the county and the size.

- Allowed: dps.ny.gov's robots.txt is the Drupal default. ores.ny.gov itself could not be reached through our network (the tunnel failed); the DPS page is the official one now. The matter pages in the Document and Matter Management system (documents.dps.ny.gov, robots 404) load their filings and calendars by script, so hearing dates are not available here.
- Yield: 52 applications, 9 pending (Bull Run Wind 449 MW, Cayuga Solar, Addison Solar 120 MW, Alabama Solar 130 MW, Town Line Solar and Storage 200 MW, Little Salmon Solar 200 MW, North Country Wind, two declaratory rulings), 18 hits (one per host town, pending stages and decisions in the window). Decisions carry their date (Flat Creek Solar relinquished Oct 6, 2026); pending listings have `meeting_date` null and `date_kind` "listed".
- Where the hits land: 2 on places we read (Lansing, Campbell), 16 on towns not on the site (Altona, Clinton, Ellenburg, Mooers, Alabama, Batavia, Oakfield, Addison, Erwin, Thompson, Forestburgh, Fort Covington, Westville, Bellmont, Burke, Chateaugay).
- Precision: 18 of 18; the host towns are those the application names.

### 3.3 Massachusetts: Environmental Monitor (not readable)

The Monitor moved to mass.gov on July 23, 2021. mass.gov answers HTTP 403 "Not allowed" to AgendaAheadBot on every page, robots.txt included (an Akamai rule, not a robots.txt rule, so there is nothing to obey and nothing to read). The old eeaonline.eea.state.ma.us page still serves issues from 2009 to July 9, 2021 only. The MEPA ePLACE public portal and the DPU/EFSB file room (`eeaonline.eea.state.ma.us/DPU/Fileroom`) are script-only shells. Nothing to build; the MassDEP wetlands feed (`sources/massdep.py`) remains the Massachusetts state source. A Cloudflare verified-bot listing does not help here (Akamai), and mass.gov's rule would need the Commonwealth's web team to allow the bot: a letter.

### 3.4 Ohio: Power Siting Board (built: `oh_opsb`)

opsb.ohio.gov answered 404 to every page we tried, including its home page and robots.txt (puco.ohio.gov too). The Board's docket is the PUCO Docketing Information System, dis.puc.state.oh.us, whose robots.txt disallows only a list of named AI crawlers (GPTBot, ClaudeBot, CCBot and the like); everyone else is allowed. Everything there is a plain GET once the home page has started the ASP.NET session (the daily reports are empty without it; the module loads the home page first, with neither a login nor a cookie it was not given).

- Read: the five most recent Docketing Division daily activity reports (every new case and every entry, order and filing of the day, with case number, title and summary); the open-case lists for the Board's purpose codes under industry EL (BGN generating station certificate, BGA its amendment, BTX transmission certificate, BTA its amendment, BSB substation); the case record of every case opened in the last 18 months or named in a report (title, status, dates, latest 15 docket entries), and the printable docket card when the 15 do not reach the window or do not name the county.
- Not read: the search forms (posts), the documents, and letters of notification and construction notices (BLN, BNR: small line work; items only, 23 of them in the five reports).
- Fields: county (from the title, "Oak Run Solar Project, LLC-Solar-Powered Electric Generation Facility in Madison County, Ohio", or from a docket entry; when neither names it, from the local public hearing's venue when that venue is a county seat, recorded as `county_source`), townships named in the docket, MW, topics (solar, battery, wind, gas plants and lines to `clean_energy_siting`), hearing entries ("Administrative Law Judge Entry scheduling a local public hearing on December 15, 2026, at 6:00 p.m., at Southern State Community College, Lecture Hall, Hillsboro, Ohio"), decisions (opinions and orders, entries on rehearing, orders on remand).
- Attribution: the county row ("Highland County") and, when the docket names a configured township in that county, that township too (`attribution.known_townships` and `resolve_known`).
- Yield (30 days): 62 case records read, 85 items, 13 hearing entries found across the docket (most before the window), 5 hits: local public hearings for Barr Energy Storage (Highland County, Dec 15), the Baku to Gavin 765 kV line (Jackson County, Oct 27) and the Portsmouth Gas DevCo plant (Pike County, Dec 10), and the Board's Oct 29 entries on rehearing in the two Oak Run Solar cases (Madison County). About one event a week; the Board's docket is small.
- Where the hits land: Highland, Jackson and Pike counties are county rows we cannot read today; Madison County is read.
- Gaps: the county is unknown for 43 of 85 items (new-style case titles carry only the company name, and the application's summary does not always name the county); those cases stay items with no hit until a docket entry or a hearing venue names it. The PowerConneX New Albany hearing (Oct 22) was missed for that reason.
- Precision: 5 of 5.

### 3.5 Michigan: PSC siting under PA 233 (not readable)

michigan.gov (where the Commission lists siting applications) answers 403 on every page, robots.txt included (Akamai). E-Dockets at mi-psc.my.site.com allows robots and publishes sitemaps of filings and hearings (`sitemap-hearing__c-1.xml`, `sitemap-filing__c-weekly.xml`), but every page is a Salesforce Experience Cloud shell that says "Loading" without scripts, and the data calls behind it are posts to the Aura API. Nothing to build. The Michigan county planning commission route (`attribution.py`, via_county) stays the Michigan answer.

### 3.6 Virginia: DEQ permit-by-rule notices (not readable)

deq.virginia.gov answers 403 on every page, robots.txt included (Akamai). Nothing to build; the Virginia notices remain the counties' own agendas and the §2.2-3707(F) notice-on-request route, which is a letter and is not used.

### 3.7 Maryland: PSC CPCN cases (built: `md_psc_cpcn`)

Every generating station over 2 MW and every high-voltage line needs a CPCN; the Commission holds a public comment hearing in the county. psc.maryland.gov publishes the case list by year (case number, applicant, MW, county, withdrawals), the upcoming public comment hearings (case, date and time, place, written-comment deadline) and a proceedings dashboard (filing date and stage per case). robots.txt: allow all, `Crawl-delay: 10`, which the fetcher honours (three pages, about 30 seconds). The case files at webpsc.psc.state.md.us sit behind a Cloudflare challenge and are not read.

- Yield (30 days): 138 cases listed for 2024 to 2026 (28 filed in 2026 so far, almost all 3 to 5 MW community solar, plus four transmission lines), 8 CPCN public comment hearings listed, 8 hits (Caroline, Carroll three times, Prince George's, Queen Anne's twice, Washington), all with date, time, place or "virtual", and the written-comment deadline. About two hearing items a week.
- Where the hits land: Carroll County (three hearings) is a county row we cannot read today; Caroline, Prince George's, Queen Anne's and Washington are read. Baltimore, Harford, Somerset and Talbot counties and the City of Frederick, the other Maryland places we cannot read, had no CPCN hearing in the window.
- Precision: 8 of 8.

## 4. What the four feeds give the blocked places

The 599 production rows that are not automated split into 262 blocked (bot checks, vendors, robots.txt, script-only sites, crawl delays over the cap, unreachable) and 337 that post no agendas or have no site. In the 30-day windows the four feeds put items on these of them:

- New York (22 not automated): Halfmoon (two SEQR notices: a solar array before the Planning Board, a planned development district before the Town Board), Huntington, Hurley (a zoning law for battery storage). Nothing in the window for the other 19.
- Ohio (186 not automated, 46 blocked): Highland, Jackson and Pike counties.
- Maryland (10 not automated): Carroll County (three solar hearings).

That is 7 of the roughly 100 blocked places in the windows (10 hits: 4 ENB, 3 OPSB, 3 Maryland). The larger effect is elsewhere: 58 of the 82 hits land on places that are not on the site at all (42 New York towns and villages from the ENB, 16 from ORES). The state feeds reach the whole state, not the 114 New York rows we chose; they give a page's worth of items to towns that have no page.

What remains uncovered: Massachusetts beyond MassDEP (mass.gov is closed to us), Michigan and Virginia state routes (both state sites are closed to us), Rhode Island (already covered by the Secretary of State portal), every press-association notice site (closed by terms), and in Ohio the half of Board cases whose county the docket never names. The letters route stays closed by the owner's decision; the verified-bot form The one permission-shaped step that is a form, not a campaign.

## 5. Promotion: what changes to put a feed into the daily run

Each feed is gated the way the Vermont and Connecticut feeds are:

1. `crawler/watch351/sources/notice_feeds.py`: set `GATED = False` (or give the one feed its own flag) so `check_out_dir` accepts `data/sources`.
2. `ops/daily.sh`: add, before `trending.py`, one line per feed, for example `python3 -m watch351.sources.ny_enb --out-dir ../data/sources --days 45` (ENB; the 45 days cover the sitemap's lag), `python3 -m watch351.sources.ny_ores --out-dir ../data/sources`, `python3 -m watch351.sources.oh_opsb --out-dir ../data/sources`, `python3 -m watch351.sources.md_psc_cpcn --out-dir ../data/sources`. `current.other_hits` already merges every `data/sources/*_hits.json`; the `source` field is the feed id.
3. The site: label rows by `source_kind` ("public_notice" shows as "Hearing notice", "state_docket" as "State docket"), show `headline`, `place` and `comment_deadline`, and accept `meeting_date` null for listed and notice items (the contract already allows null). `current.normalize` keeps only the contract's fields, so the site reads these extra fields from the `data/sources/<feed>_hits.json` files or `normalize` grows four optional fields; that is the site owner's call.
4. Topics `extraction` and `large_development` (18 and 3 of the ENB hits) are in the contract for gated feeds only; either the site gains labels or the feed drops those hits at promotion (one line in `ny_enb.to_hit`).
5. New York places the ENB names that are not rows get the site's convention ("Hilton (village)"); `build.py` would need to render a page for a town id with no row, or the feed limits hits to configured rows (`configured` is on every hit).

## 6. Cloudflare Verified Bots (one-time optional form, not a letter campaign)

Cloudflare's Verified Bots programme is a form in the Cloudflare dashboard ("BotBase submission form"), reviewed by Cloudflare, not by any town. A verified bot is "transparent about who it is and what it does": it identifies itself with a Web Bot Auth signature or a published IP list, obeys robots.txt and crawl directives, and keeps reasonable request rates. Approval puts the bot in BotBase and Cloudflare Radar's bots and agents directory; sites on default bot settings then let it through, and sites can allow it by name. Status is tracked under BotBase > Submission history (Waiting For Review, Accepted, Rejected, Cancelled). Breaches (undisclosed purpose, ignoring crawl-delay) remove the bot. Our signing is already built (`crawler/watch351/botauth.py`, Ed25519, `WBA_PRIVATE_KEY`), the key directory is live at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory (one Ed25519 key, `x` = `JTaGTbtdJXp0OOXWGIn7wXfXp_eqVUCXtU64i6lZirA`), and the bot page is https://agendaahead.vercel.app/bot. Checked Nov 6, 2026 against the current docs (developers.cloudflare.com/bots/concepts/bot/verified-bots/, updated Nov 2, 2026; web-bot-auth, updated Oct 8, 2026).

Text to paste into the form (edit the contact line):

> **Bot name:** AgendaAheadBot
>
> **User agent:** `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`
>
> **Operator:** Agenda Ahead (agendaahead.vercel.app), [owner name], [contact email]
>
> **Verification method:** Web Bot Auth. Key directory: https://agendaahead.vercel.app/.well-known/http-message-signatures-directory (Ed25519, JWKS, served with the `Signature`/`Signature-Input` headers over the directory itself). Every request carries `Signature-Agent: "https://agendaahead.vercel.app"`, `Signature-Input` and `Signature` with `tag="web-bot-auth"`, created/expires within 60 seconds, a fresh nonce per request.
>
> **Behavior / category:** Search (indexing public government pages so residents can find them). Legacy category: Search Engine Crawler. Operated directly by us (Direct), no third party can send requests through it.
>
> **What it does:** Once a day it reads the public meeting-agenda pages that town, township and county governments in Massachusetts, New York, Rhode Island, Virginia, Maryland, Michigan and Ohio post, plus state bulletins and dockets (NYS DEC Environmental Notice Bulletin, NYS ORES, Ohio Power Siting Board docket, Maryland PSC). It publishes, for each place, a short plain-English line about items concerning solar, battery storage, data centers, zoning changes and moratoriums, with a link back to the official page. It does not train models, does not fetch video, does not read anything behind a login, and never submits a form.
>
> **Rate and scope:** At most one request a second per host; crawl-delay honoured up to 20 seconds; a few listing pages per host per day plus new agenda files only; files over 40 MB skipped; 404s cached so they are not re-requested.
>
> **robots.txt:** Obeyed on every host and on every redirect hop, for `AgendaAheadBot` and for our former name `351WatchBot`. A site that adds `User-agent: AgendaAheadBot` / `Disallow: /` is left alone the same day.
>
> **Bot documentation page:** https://agendaahead.vercel.app/bot (purpose, how to block, the user agent, the key directory).
>
> **Why verification matters:** About 60 of the ~650 local governments we cover sit behind Cloudflare bot protection on default settings and answer every request with a challenge; we never solve challenges, so those residents get nothing. Verification lets those sites' default configuration recognise an honest crawler. We ask for nothing beyond the standard programme.

Before submitting, run `python3 -m watch351.botauth check-directory` (verifies the live directory) and `python3 -m watch351.botauth test` (one signed request to Cloudflare's test endpoint; 401 means well formed but not yet known, which is the expected state before approval).

## 7. Files

- `crawler/watch351/sources/notice_feeds.py`: shared helpers (gate, dates, headline cutter, topics for dockets, New York place resolver, county names, hit builder, outputs).
- `crawler/watch351/sources/ny_enb.py`, `ny_ores.py`, `oh_opsb.py`, `md_psc_cpcn.py`: the four feeds; each runnable with `python3 -m watch351.sources.<name> --days 30 [--offline]`.
- `crawler/experiments/notices_test.py`: `run`, `stats` (yield and where the hits land), `sample` (the hand-check worksheet).
- `data/test/notices/`: items, hits, ledgers, run reports, `stats.json`, `precision_worksheet.json`, `precision_judgments.json`.
- Not touched: `build.py`, `site/`, `research_notes/Design/`, `fetch.py`, `daily.py`, `keywords.py`, `attribution.py`, the towns files.
