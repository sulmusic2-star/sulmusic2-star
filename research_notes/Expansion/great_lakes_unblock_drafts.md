# Great Lakes wave: unblock requests (drafts, not sent)

Drafted 2026-11-02 for the owner to send. Nothing here has been sent. The crawler (AgendaAheadBot) never bypasses a bot wall, a robots.txt rule or a crawl delay; these requests ask the vendor or county to let it read public agenda listings, or to point us at a feed that is meant for machines.

Each draft gives: who to write to, what we ask for, the exact bodies it would open, and the letter text. Numbers are from the 2026-10 Michigan test (`research_notes/Expansion/test_mi_va.md`) and the 2026-11-02 Great Lakes discovery (`data/towns_mi.json`, `data/towns_oh.json`).

What every letter says about us, so the facts stay the same across vendors:

- Agenda Ahead reads published meeting agendas of local boards and tells residents and professionals which items concern land use and energy siting (solar, battery storage, data centers, zoning changes, moratoria), before the meeting.
- The crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs its requests (Web Bot Auth, Ed25519; key directory at `/.well-known/http-message-signatures-directory`), obeys robots.txt on every host, makes at most one request a second per host, downloads a listing a few times a day and each agenda document once, never logs in, never posts a form, never solves a challenge.
- We link to the vendor's own agenda page as the source; we do not re-host the documents.
- We would prefer a feed (RSS, a read-only API, a public JSON endpoint) over scraping, and we will use whichever the vendor names.

## 1. Diligent (Diligent Community, formerly iCompass Diligent Community)

**To:** Diligent Corporation, support and public-sector partnerships (the "Diligent Community" product team). Copy each county's clerk or planning director.

**What we ask:** that `*.diligent.community` and `*.community.diligentoneplatform.com` allow `AgendaAheadBot` in robots.txt for the public meeting-list and agenda pages (no login pages), or that Diligent name a public feed per site (an RSS or JSON list of upcoming meetings with agenda links).

**What it opens:**

| Body | State | Why it matters |
|---|---|---|
| Hillsdale County Planning Commission (`hillsdale.diligent.community`) | MI | reviews zoning amendments for Hillsdale County's townships (MCL 125.3307); 6 target townships, 5 of them not readable directly |
| Saginaw County Planning Commission (`saginawcounty.community.diligentoneplatform.com`) | MI | reviews zoning amendments for Saginaw County's townships; 8 target townships |
| Camden Township (`hillsdale.community.diligentoneplatform.com`) | MI | a township whose own agendas are on the county's Diligent site |

**Letter:**

> Subject: Allowing a public-interest crawler to read public agenda pages on Diligent Community
>
> Hello,
>
> Agenda Ahead is a small public-interest service. We read the published agendas of local boards and tell residents which items concern land use and energy siting, before the meeting. Several of the county planning commissions we follow in Michigan publish through Diligent Community: Hillsdale County, Saginaw County and the townships whose agendas sit on those sites.
>
> Your robots.txt disallows our crawler, so we do not read those pages. We would like to. Our crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs every request (Web Bot Auth, Ed25519; key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory), makes at most one request a second per host, reads a site's meeting list a few times a day and each agenda document once, never logs in and never submits a form. We link to your page as the source and do not re-host the documents.
>
> Two ways would work for us, and we will take whichever you prefer:
>
> 1. an `Allow` for `AgendaAheadBot` on the public meeting-list and agenda-document paths of the sites above, or
> 2. a machine-readable list of upcoming meetings with agenda links (RSS, JSON or a documented read-only endpoint), which we would use instead of the HTML pages.
>
> If there is a form, a fee or a terms document for this, please point us to it. Thank you.

## 2. BoardDocs (Diligent)

**To:** BoardDocs support (`go.boarddocs.com`), part of Diligent since 2021; copy the body's clerk.

**What we ask:** read access for `AgendaAheadBot` to the public `Board.nsf/Public` pages (meeting list and agenda items) of the sites below, or the public RSS/ICS feeds that BoardDocs sites can publish.

**What it opens:**

| Body | State | Note |
|---|---|---|
| Jackson County Board of Commissioners and its committees (`go.boarddocs.com/mi/jackson/Board.nsf/Public`) | MI | The county planning commission's packets are now read from the Region 2 Planning Commission site, so this request is for the county board itself, where zoning appeals and county-level siting items are heard; `go.boarddocs.com` answers HTTP 403 to the bot |
| Town of Culpeper | VA | listed in the 2026-10 test; the Virginia engineer's wave owns it |

**Letter:**

> Subject: Reading public BoardDocs agendas with an identified crawler
>
> Hello,
>
> Agenda Ahead reads published local-government agendas and tells residents which items concern land use and energy siting, before the meeting. Jackson County, Michigan publishes its board and committee agendas on BoardDocs. `go.boarddocs.com` returns HTTP 403 to our crawler, so we cannot read the public meeting list.
>
> The crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs its requests (Web Bot Auth), makes at most one request a second, reads the public meeting list a few times a day and each agenda once, never logs in and never posts. We link back to the BoardDocs page and do not copy the documents elsewhere.
>
> Could you allow the identified crawler on the public `Board.nsf/Public` pages for that site, or tell us which feed (RSS or ICS) we should read instead? We will follow whatever rate limit you set. Thank you.

## 3. iCompass / CivicWeb (Diligent)

**To:** iCompass (CivicWeb) support at Diligent; copy Tuscola County's clerk and Chesterfield Charter Township's clerk.

**What we ask:** `Allow` for `AgendaAheadBot` in robots.txt on `*.civicweb.net` public document and meeting pages, or the sites' public RSS feeds.

**What it opens:**

| Body | State | Why it matters |
|---|---|---|
| Tuscola County Planning Commission (`tuscolacounty.civicweb.net`) | MI | reviews zoning amendments for Tuscola County's townships; 18 target townships, 16 not readable directly; the Thumb's wind and PA 233 items |
| Chesterfield Charter Township (`chesterfieldtwp.civicweb.net`) | MI | Macomb County township, about 45,000 people, data-center and industrial rezonings |

**Letter:**

> Subject: Allowing an identified public-interest crawler on CivicWeb public pages
>
> Hello,
>
> Agenda Ahead reads published meeting agendas of local boards and tells residents which items concern land use and energy siting, before the meeting. Tuscola County's planning commission and Chesterfield Charter Township in Michigan publish on CivicWeb, and robots.txt on `civicweb.net` disallows our crawler.
>
> The crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs its requests (Web Bot Auth), makes at most one request a second per host, reads a site's meeting list a few times a day and each agenda document once, never logs in and never posts a form. We link to the CivicWeb page as the source.
>
> Would you allow `AgendaAheadBot` on the public document-list and meeting pages, or point us at the public RSS feed each site can publish? We will use whichever you name and keep to any rate limit you set. Thank you.

## 4. Granicus (iQM2)

Not on the owner's list, but two bodies in this wave sit behind iQM2, a Granicus product whose robots.txt disallows every bot but the named search engines: the Butler County (OH) Board of Commissioners (`butlercountyoh.iqm2.com`) and the City of Monroe (MI) (`monroecitymi.iqm2.com`, HTTP 429). Butler County's planning commission is read from the Development department's own page, so only the county board is missing. Granicus's own position (robots.txt) is firm; a request would go to Granicus partner relations. A one-paragraph version of letter 1 is enough, naming the two sites. Low priority.

## 5. Counties behind Cloudflare or another bot wall

A Cloudflare-style challenge (HTTP 403 with a browser check) stops the crawler at the homepage. The county controls this: in the Cloudflare dashboard it can add a WAF skip rule for the `AgendaAheadBot` user agent, or verify the bot through Cloudflare's Verified Bots program (our Web Bot Auth key directory is for that).

| County | State | Site | What it holds |
|---|---|---|---|
| Montgomery County | OH | `mcohio.org` | county planning commission (Dayton area); the townships of Montgomery County are not in this wave's eight counties but the county is one of the 88 |
| Portage County | OH | `portagecounty-oh.gov` | Portage County Regional Planning Commission |
| Montcalm County | MI | `montcalm.org` | county planning commission, 5 target townships (2026-10 test) |

**Letter (to the county administrator or IT director, copy the planning director):**

> Subject: Letting an identified crawler read your public agenda pages
>
> Hello,
>
> Agenda Ahead reads published meeting agendas of local boards and tells residents which items concern land use and energy siting, before the meeting. Your website answers our crawler with a bot challenge page, so we cannot read the planning commission's agendas.
>
> The crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)` and signs every request with Web Bot Auth (HTTP Message Signatures, Ed25519; key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory), so your firewall can verify it is us. It makes at most one request a second, reads the agenda list a few times a day and each document once, and never logs in or submits anything.
>
> Could you add a firewall rule that lets this user agent through to your public agenda pages, or tell us where the planning commission posts its agendas in a form meant for machines (an RSS feed, a calendar export)? If you would rather email us the agenda when it is posted, that works too. Thank you.

### Townships behind Cloudflare or a firewall (same letter, to the township clerk)

Michigan: Iosco, Cohoctah (Livingston); Almont, Attica, Rich (Lapeer); Bloomfield Charter Township, Orion Charter Township (Oakland); Bruce (Macomb); Fenton Charter Township (Genesee); Madison Charter Township (Lenawee); Putnam (Livingston, firewall 403); Scio (Washtenaw, Akamai 403).
Ohio: Jerome Township (Union, Akamai 403), West Chester Township (Butler, Akamai 403).

### Sites whose robots.txt disallows the bot (a shorter note to the clerk asking for an `Allow`)

Michigan: Bedford Township (Monroe), Green Oak Charter Township (Livingston), Newton Township (Calhoun), City of Saline, City of Howell, Ingham County (`ingham.org`), Lyon Charter Township and West Bloomfield Charter Township (Oakland), Mundy Charter Township (Genesee), St. Clair Township (St. Clair).
Ohio: Jefferson Township (Franklin).

Several of these are Revize-built sites whose robots.txt allows only the named search engines; Revize's default file is the thing to change, so one note to Revize (`revize.com`) asking that `AgendaAheadBot` be added to the default allow list would cover many at once.

### Documents on a host the listing does not control

**Licking County (OH), the data-center county, is the one that matters here.** Its planning commission posts agendas at `lickingcounty.gov/depts/planning/planning/agendas/` (found through the site map; the listing itself is readable), but every agenda and packet is a `civicax/filebank/blobdload.aspx` download, and the county's robots.txt disallows that path. We read the listing and nothing behind it. Two of the county's 25 townships post agendas we can read (Etna and Liberty), so the county route is the only way to most of Licking County's zoning changes. The ask, to the county IT director with a copy to the planning director:

> Subject: Letting an identified crawler read the planning commission's agenda files
>
> Hello,
>
> Agenda Ahead reads published meeting agendas of local boards and tells residents which items concern land use and energy siting, before the meeting. The Licking County Planning Commission's agenda page is readable, but the agenda and packet files sit under `/civicax/filebank/`, which your robots.txt closes to crawlers, so we see the dates and not the items.
>
> Our crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs every request (Web Bot Auth, Ed25519; key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory), reads the agenda page a few times a day and each file once, and never logs in or submits a form. Could you add an `Allow: /civicax/filebank/` line for `User-agent: AgendaAheadBot`, or post the planning commission's agendas as plain PDF links on the department page? If you would rather email the agenda to us when it is posted, that works too. Thank you.

Riga Township (MI) links agendas on `mcusercontent.com` (Mailchimp), whose robots.txt disallows everything; St. Albans Township (OH) disallows its own PDF folder; Salem Township (MI) serves documents from `documents-on-demand.com`, which answers 403; Lodi (MI), Cato (MI) and Plain (OH) townships set a crawl delay above the 10 s document cap. Each is a one-line ask to the clerk: post the PDFs on the township's own site, or lower the crawl delay.

### Crawl delay above the 20 s listing cap

Crawford, Noble, Paulding and Putnam counties (OH) and Mifflin Township (OH) ask for a 30 s crawl delay. We honour it by not crawling. A note to each asking for 10 s, or for an RSS feed, would open them.

## Order to send

1. Diligent (letters 1, 2 and 3 can go to the same account team): four Michigan county planning commissions and two townships.
2. Revize (the robots.txt default): about ten Michigan townships and cities at once.
3. Licking County (OH): the file bank behind its planning commission agendas. Then Montgomery and Portage counties (OH), Montcalm County (MI).
4. The township clerks, in the order of the fights: Scio and Lodi (Washtenaw), Green Oak, Iosco, Cohoctah and Putnam (Livingston), Bloomfield, Orion, Lyon and West Bloomfield (Oakland), West Chester and Jerome (OH).
