# New York: unblock requests (drafts, not sent)

Drafted 2026-11-03 from `data/towns_ny.json` (79 places, 55 read every morning, 24 not) and the wave-2 county discovery (`data/test/wave2/`). The owner sends these; nothing here has gone out. The format follows `va_md_unblock_drafts.md`: who we are, what we read, how much, why, the ask, the offer. Replace `[your name]` and `[your address]` before sending. The bot page is https://agendaahead.vercel.app/bot; the key directory for Web Bot Auth is at `/.well-known/http-message-signatures-directory` on the same host.

Facts to keep straight when sending:

- AgendaAheadBot (formerly 351WatchBot; the older name still appears in some reason fields) obeys robots.txt on every host and redirect, makes at most one request a second to a host, never logs in, never posts a form and never solves a bot challenge. A daily pass is a few listing pages per host plus new agenda files only.
- We ask for agendas and packets, never video, never search pages, never anything that needs an account.
- New York's legal floor: Public Officers Law §103(e) says records scheduled to be discussed at an open meeting (proposed local laws, resolutions, the agenda itself where one exists) are posted on the body's website, if it keeps a regularly updated one, to the extent practicable at least 24 hours before the meeting. The Open Meetings Law does not require an agenda. So the ask to a town that posts nothing is a courtesy backed by a soft duty, not a demand.

What is not a letter, and goes to the engineer instead, is in the last section.

Order to send: 1 (Brookhaven and Islip), 2 (the other towns behind a bot wall), 3 (the counties behind a bot wall), 4 (towns and counties whose agendas sit on a closed vendor), 5 (the vendors themselves, in parallel with 4), 6 (towns that post no agendas), 7 (one-line notes: Carmel's certificate, the crawl delays).

---

## 1. Brookhaven and Islip, the two big Suffolk towns

The two largest towns in Suffolk County, with more than 800,000 people between them, both answer every page with a Cloudflare challenge (HTTP 403). Brookhaven has a data-center moratorium in progress (Intro LL 11 of 2026) that we cannot follow from the town site. Islip's platform is unknown because nothing behind the wall could be read.

To: the town clerk, with a copy to the IT director. Subject: Letting an identified public-notice service read your agendas

> I run Agenda Ahead, a free service that reads local government agendas every morning and tells residents, in plain words, when a solar farm, a battery storage project, a data center, a zoning change or a moratorium is about to come before a board. Every sentence links back to your agenda.
>
> Your website answers our program with a Cloudflare bot challenge, so today Brookhaven [Islip] residents cannot see their own Town Board, Planning Board and Zoning Board items on our site. We never get around a challenge; we stop.
>
> Our program identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)` and signs every request with Web Bot Auth (HTTP Message Signatures, Ed25519; key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory), so Cloudflare can verify it is us. It makes at most one request a second, reads the agenda list a few times a day and each agenda file once, and never logs in or submits anything.
>
> Could you do one of these:
> 1. In the Cloudflare dashboard, add a WAF skip rule for the `AgendaAheadBot` user agent on your public agenda pages, or verify the bot through Cloudflare's Verified Bots program.
> 2. Or publish an RSS feed, or a plain page, that lists each meeting's date and its agenda PDF; we can read that without touching the rest of the site.
> 3. Or add our address to the list that receives the agenda when it is posted.
>
> We stop on request, name a technical contact and can send a monthly log of our requests. Thank you for considering it.
>
> [your name], Agenda Ahead, [your address]

## 2. The other towns behind a bot wall

Same letter as section 1, to the town clerk. Affected:

| Town | County | What blocks us |
|---|---|---|
| Hurley | Ulster | Cloudflare challenge on every page |
| Wawarsing | Ulster | Cloudflare challenge on every page |
| Halfmoon | Saratoga | Cloudflare challenge on every page |
| Duanesburg | Schenectady | Cloudflare challenge on every page |
| Horicon | Warren | Cloudflare challenge on every page |
| Newfane | Niagara | the site's firewall answers HTTP 403 Forbidden to every request |
| Livingston | Columbia | a Sucuri and Cloudflare front end returns a body that is not readable HTML |

For Newfane and Livingston, change the second paragraph to say the site's firewall rather than Cloudflare, and the first ask to "allow the `AgendaAheadBot` user agent through your firewall on the public agenda pages".

## 3. Counties whose planning boards sit behind a bot wall

Under General Municipal Law §239-m, a town's zoning change or moratorium near a county road, a state road or a municipal boundary goes to the county planning board before the town can vote on it. Reading the county board's agenda shows what a dozen towns are about to decide, including towns with no website of their own. These county sites block us at the homepage:

| County | What blocks us |
|---|---|
| Cayuga | Cloudflare-style challenge |
| Chenango | Cloudflare-style challenge |
| Ontario | Cloudflare-style challenge |
| Orange | Cloudflare-style challenge |
| Washington | Cloudflare-style challenge |
| Delaware | firewall HTTP 403 on every request |

To: the county planning director, with a copy to the county IT director. Subject: Letting an identified crawler read the county planning board's agendas

> I run Agenda Ahead, a free service that reads local government agendas every morning and tells residents, in plain words, when a solar farm, a battery storage project, a data center, a zoning change or a moratorium is about to come before a board. For towns that post little online, the county planning board's §239-m referral agenda is often the first public notice of a zoning change, so your agenda matters to residents of every town in the county.
>
> Your website answers our program with a bot challenge, so we cannot read the planning board's agendas. We never get around a challenge; we stop.
>
> Our program identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)` and signs every request with Web Bot Auth (key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory). It makes at most one request a second, reads the agenda list a few times a day and each file once, and never logs in or submits anything.
>
> Could you add a firewall rule that lets this user agent reach the planning board's public agenda pages, or tell us where the board posts its agendas in a form meant for machines (an RSS feed, a calendar export)? If you would rather email us the agenda when it is posted, that works as well. Thank you.
>
> [your name], Agenda Ahead, [your address]

## 4. Towns and counties whose agendas sit on a closed vendor

The town or county controls these: the vendor acts on a client's request. Send the locality letter first and the vendor letter (section 5) in parallel.

| Place | Vendor | What happens |
|---|---|---|
| Southampton (Suffolk) | eSCRIBE (`pub-southamptonny.escribemeetings.com`); iQM2 as well | agenda downloads return a browser-verification challenge; the iQM2 host answers HTTP 429 |
| New Castle (Westchester) | eCode360 (General Code), `ecode360.com/documents/pub/NE0395/Agendas/` | robots.txt disallows `/documents` for every agent |
| Gardiner (Ulster) | HeyGov (`api.heygov.com`) | the Agendas and Minutes page is a widget filled from an API whose robots.txt disallows all bots |
| Cortland County | iQM2 (Granicus) | robots.txt allows only the named search engines |
| Ulster County, Westchester County | Granicus | robots.txt allows only the named search engines |
| Oneida County | PrimeGov | the vendor host refuses the program |
| Erie County | DestinyHosted | the vendor host refuses the program |
| Genesee County, Montgomery County | the county's own site | robots.txt disallows the agenda path |

To: the town clerk or the clerk of the county legislature. Subject: Reading your public agendas automatically

> I run Agenda Ahead, a free service that reads local agendas every morning and tells residents, in plain words, when a solar farm, a battery storage project, a data center, a zoning change or a moratorium is about to come before a board, with a link back to your agenda.
>
> Your agendas are published on [vendor], which refuses our program on every page [or: whose robots.txt tells every program except the big search engines to stay away]. Our program (AgendaAheadBot) respects that, so today we cannot read [body names]. Nothing is wrong on your side; it is the vendor's default, and the vendor will change it for a client.
>
> Could you do one of these:
> 1. Ask [vendor] to allow `AgendaAheadBot` on your public agenda pages. The user agent is `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`. We would make at most one request every five seconds and at most 50 requests a day, and read only agenda and minutes pages, never video.
> 2. Or publish an RSS feed or a plain page on your own site that lists each meeting's date and its agenda PDF.
> 3. Or add our address to the list that receives the agenda when it is posted.
>
> We stop on request and name a technical contact. Thank you.
>
> [your name], Agenda Ahead, [your address]

For Genesee and Montgomery counties the ask is shorter: an `Allow` line for `User-agent: AgendaAheadBot` on the agenda path in the county's own robots.txt, or an RSS feed.

## 5. The vendors

Granicus and iQM2: use letter 2 in `va_md_unblock_drafts.md` word for word, naming `cortlandcountyny.iqm2.com`, `southamptonny.iqm2.com` and the Ulster and Westchester Granicus hosts. Granicus's robots.txt position is firm; the client letters in section 4 carry more weight.

eSCRIBE (Southampton's agenda host):

> Subject: Allowing an identified public-interest crawler to read public agenda files
>
> Hello,
>
> Agenda Ahead reads published meeting agendas of local boards and tells residents which items concern land use and energy siting, before the meeting. The Town of Southampton, New York publishes on eSCRIBE (`pub-southamptonny.escribemeetings.com`). The meeting list is readable, but each agenda download answers with a browser-verification challenge, so we see the dates and not the items.
>
> Our crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs every request with Web Bot Auth (Ed25519; key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory), makes at most one request a second per host, reads each agenda file once, and never logs in or submits a form. We link to the eSCRIBE page as the source.
>
> Would you allow `AgendaAheadBot` to fetch public agenda files on the public portal, or point us at a feed each site can publish? We will use whichever you name and keep to any rate limit you set. Thank you.

General Code (eCode360 document hosting, New Castle):

> Subject: Allowing an identified public-interest crawler on public agenda documents
>
> Hello,
>
> Agenda Ahead reads published meeting agendas of local boards and tells residents which items concern land use and energy siting, before the meeting. The Town of New Castle, New York hosts its agendas, minutes and packets on eCode360 (`ecode360.com/documents/pub/NE0395/Agendas/`), and robots.txt on `ecode360.com` disallows `/documents` for every agent.
>
> Our crawler identifies itself as `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`, signs every request (Web Bot Auth, Ed25519; key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory), makes at most one request a second, reads a town's agenda folder a few times a day and each file once, and never logs in or submits a form.
>
> Would you add an `Allow: /documents/pub/` line for `User-agent: AgendaAheadBot`, or tell us the public feed, if any, that lists a client's new documents? Thank you.

HeyGov (Gardiner), PrimeGov (Oneida County) and DestinyHosted (Erie County): a one-paragraph version of the General Code letter, naming the host (`api.heygov.com`, the PrimeGov portal, the Erie County DestinyHosted portal) and asking for an `Allow` on the public meetings endpoints. Low priority until the client letters have gone out.

## 6. Towns that post no agendas

These towns keep a website but post minutes, schedules or hearing notices rather than agendas. The letter asks for the agenda to go up with the notice, which §103(e) already points toward.

| Town | County | What is online today |
|---|---|---|
| Highland | Sullivan | Town Board meetings as "hybrid meeting information" news posts; minutes only |
| Berne | Albany | Town Board resolutions and annual documents; Planning and Zoning minutes only |
| Winfield | Herkimer | Town Board minutes only; its data-center moratorium appears as a hearing-notice post |
| Camillus | Onondaga | a calendar of Town Board, Planning Board and ZBA meetings with no agenda files |
| York | Livingston | annual meeting-date schedules, forms and occasional hearing notices |

To: the town clerk. Subject: Posting the agenda with the meeting notice

> I run Agenda Ahead, a free service that reads local agendas every morning and tells residents, in plain words, when a solar farm, a battery storage project, a data center, a zoning change or a moratorium is about to come before a board. Residents of [town] cannot see their boards on it, because the town site posts minutes and hearing notices but not the agenda itself.
>
> Public Officers Law §103(e) asks that records to be discussed at a meeting go on the website, to the extent practicable, at least 24 hours before. The simplest way to meet it is to post the agenda PDF on the board's page when the clerk sends it to members; most towns your size do that in a minute or two per meeting.
>
> If posting is not practical, could you add our address to the list that receives the agenda when it goes to members? We would turn it into a plain sentence per item and link to the town site.
>
> Thank you for considering it.
>
> [your name], Agenda Ahead, [your address]

## 7. One-line notes

Carmel (Putnam): `carmelny.org` serves a TLS certificate issued for another hostname, so no verified connection can be made and we skip the host. To the town IT contact: "Your site's certificate does not match `www.carmelny.org`, so browsers that check carefully, and programs like ours, cannot connect. Reissuing the certificate for the right hostname fixes it." Nothing on our side changes; we never disable certificate checks.

Huntington (`huntingtonny.gov`, Crawl-delay 15), Lansing (`lansingtownny.gov`, Crawl-delay 15) and Cicero (`ciceronewyork.net`, Crawl-delay 20): the robots.txt asks every program to wait between requests. Our listing pages now honour delays up to 20 seconds, so the agenda lists are within reach; agenda files are capped at 10 seconds and are skipped. A note to the clerk asking for `Crawl-delay: 10`, or an RSS feed, opens them; the engineering route in the next section is cheaper.

## Not letters: for the engineer

- Crawl delays: let the document fetch honour a delay up to 20 seconds for Huntington, Lansing and Cicero (a few files a day at one every 15 to 20 seconds is harmless). That reads all three without a letter.
- JavaScript-only agenda modules: Perth (Fulton), Spafford (Onondaga) and Boston (Erie) run the same "agendasandminutes" module, which fills the page from a JSON endpoint. If the endpoint is public and robots.txt allows it, an adapter that reads the JSON opens all three and any other town on the same CMS. Check robots first; if it is closed, the section 4 letter applies.
- Counties the wave-2 discovery filed as "no website found": a polite probe from this sandbox on Nov 3 found that `schenectadycountyny.gov`, `tompkinscountyny.gov` and `waynecountyny.gov` (also reached from `web.co.wayne.ny.us`) answer; `schohariecounty-ny.gov` redirects to a Revize-hosted site; `steubencountyny.gov` reset the connection from here. Add the first four to the county targets and run discovery from the production host; Steuben needs a second look before any letter.
- Southampton's HTML agenda view on eSCRIBE is readable even though the downloads are challenged; an eSCRIBE adapter that reads the HTML view would open Southampton today and other eSCRIBE towns later. That is the `escribe: no_adapter` note in the config.
