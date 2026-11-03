# Virginia and Maryland: unblock requests (drafts, not sent)

Drafted 2026-11-02 from the discovery run behind `data/towns_va.json` and `data/towns_md.json` (gated). The owner sends these; nothing here has gone out. Each draft follows the one-page template in `cheap_township_coverage.md` section 8: who we are, what we read, how much, why, the ask, the offer. Replace `[your address]` and `[your name]` before sending. The bot page is https://agendaahead.vercel.app/bot; the key directory for Web Bot Auth is at `/.well-known/http-message-signatures-directory` on the same host.

Facts to keep straight when sending:

- AgendaAheadBot (formerly 351WatchBot) obeys robots.txt on every host and redirect, makes at most one request a second to a host, never logs in, never posts a form and never solves a bot challenge. A daily pass is a few listing pages per host plus new agenda files only.
- We ask for agendas and packets, never video, never search pages, never anything that needs an account.
- Where a vendor is closed, the locality is the client: the vendor acts on the client's request, so the locality draft comes first and the vendor draft goes in parallel.

Order to send: 1 (localities on BoardDocs), 2 (Granicus and iQM2 localities), 3 (Cloudflare localities), 4 (Akamai localities), 5 (robots.txt and crawl-delay localities), 6 (document-store and script-only sites), then the vendor letters 7 to 10, then the Virginia notice requests in 11 to every locality above as a backstop.

---

## 1. Localities whose agendas are on BoardDocs (Diligent)

BoardDocs (`go.boarddocs.com`, `www.boarddocs.com`) answers HTTP 403 to AgendaAheadBot on every page. Affected: Accomack County, Northampton County, Prince George County, Pulaski County and the Town of Culpeper (every board); Essex County (Board of Supervisors only; its Planning Commission and BZA read from the county's CivicPlus Agenda Center); Northumberland County (BZA only); St. Mary's County, MD (some boards; the commissioners and Planning Commission read from the county site).

To: the clerk to the board (county administrator's office) or the town clerk. Subject: Reading your public agendas automatically

> I run Agenda Ahead, a free service that reads local government agendas every morning and tells residents, in plain words, when a solar farm, a battery storage project, a data center, a zoning change or a moratorium is about to come before a board. It links every item back to your agenda.
>
> Your agendas are published on BoardDocs, which refuses our program (AgendaAheadBot) on every page. We never log in, never post and never get around a block; we simply cannot read them.
>
> Could you do one of these three things:
> 1. Ask BoardDocs (Diligent) to allow AgendaAheadBot to read your public agenda pages (`https://go.boarddocs.com/va/<your code>/Board.nsf/Public`). The user agent is `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`. We would make at most one request every five seconds and at most 50 requests a day.
> 2. Or add our address to the list that receives the agenda packet when it goes to board members, as Va. Code § 2.2-3707 provides for anyone who asks (Virginia) or your agenda notification list (Maryland).
> 3. Or publish an RSS feed or a plain page that lists each meeting's date and its agenda PDF; we can read that directly.
>
> We stop on request, name a technical contact and can send a monthly log of our requests. Thank you for considering it.
>
> [your name], Agenda Ahead, [your address]

## 2. Localities whose agendas are on Granicus or iQM2

Granicus `ViewPublisher.php` and iQM2 hosts disallow every bot except named search engines in robots.txt; iQM2 also answers 429 to low-rate reads. Affected, every tracked board: Harford County MD, Talbot County MD, City of Frederick MD, City of Fairfax, City of Manassas, Town of Ashland; iQM2: Washington County VA, Town of Haymarket. Affected, some boards: Prince William County (Board of County Supervisors; the Planning Commission reads from the county site), Loudoun County (video and committee materials; the Board reads from eSCRIBE), Montgomery County MD and Howard County MD (video; the councils read from their own pages), Roanoke County (Board of Supervisors and Planning Commission on iQM2; the BZA reads from the county site), Goochland County (BZA on iQM2), Chesapeake (City Council and Planning Commission on Granicus; one board reads from the Agenda Center), Norfolk (BZA), Charlottesville (BZA), Harrisonburg (BZA), Purcellville (Planning Commission and BZA), Altavista (BZA), College Park MD (Board of Appeals).

To: the clerk of the governing body. Subject: Letting a public-notice service read your agendas

> I run Agenda Ahead, a free service that reads local agendas every morning and alerts residents, in plain words, to solar, battery storage, data center, zoning and moratorium items before the meeting, with a link back to your agenda.
>
> Your agendas are posted on Granicus [or iQM2], whose robots.txt tells every program but the big search engines to stay away. Our program (AgendaAheadBot) respects that, so today we cannot read [body names]. Nothing is wrong on your side; it is the vendor's default.
>
> Granicus will change the rule for a client. Could you ask your Granicus representative to add these lines to the robots.txt on `<your subdomain>.granicus.com` [or `<your subdomain>.iqm2.com`]:
>
>     User-agent: AgendaAheadBot
>     Allow: /ViewPublisher.php
>     Allow: /AgendaViewer.php
>     Allow: /MetaViewer.php
>
> We would read only agenda and minutes pages, at most one request every five seconds and at most 50 a day, never video. If that is not possible, an email copy of each agenda when it is published, or an RSS feed, does the job as well.
>
> We stop on request and name a technical contact. Thank you.
>
> [your name], Agenda Ahead, [your address]

## 3. Localities behind a Cloudflare bot challenge

The site answers every page with a Cloudflare challenge (HTTP 403). Affected: Culpeper County (`web.culpepercounty.gov`), Highland County, James City County, City of Fredericksburg, City of Waynesboro, Town of Lovettsville, Town of Strasburg, Town of Chatham. (Culpeper's Board of Supervisors and Planning Commission also use the county's own agenda portal behind the same wall.)

To: the county administrator or town manager, copy to the IT director. Subject: A verified bot that reads your agendas

> I run Agenda Ahead, a free service that reads local agendas each morning and tells residents, in plain words, when solar, battery storage, data center, zoning or moratorium items are coming up, linking to your agenda.
>
> Your website shows a Cloudflare check to every visitor that is not a browser. Our program (AgendaAheadBot) does not get around such checks, so we cannot read your agendas today.
>
> AgendaAheadBot signs every request (Web Bot Auth, HTTP Message Signatures, Ed25519); its public key directory is at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory and it is submitted to Cloudflare's Verified Bots list. Two ways to let it through, either of which takes a few minutes in the Cloudflare dashboard:
> 1. Security, Bots: set Verified Bots to Allow (on Pro and higher plans), or
> 2. Security, WAF, Custom rules: skip the managed challenge for requests whose user agent contains `AgendaAheadBot` and whose path starts with your agenda pages (for example `/AgendaCenter`), optionally limited to our signature.
>
> We make at most one request a second, read only agenda pages and files, and never log in. If you would rather, add our address to the list that receives agenda packets when they go to board members (Va. Code § 2.2-3707 lets anyone ask). Thank you.
>
> [your name], Agenda Ahead, [your address]

## 4. Localities behind an Akamai wall, or a site firewall answering 403

Akamai answers HTTP 403 to AgendaAheadBot on every page. Affected: Albemarle County, Bedford County, Clarke County, Fauquier County, Frederick County VA (`fcva.us`), City of Lexington, City of Staunton, Town of Leesburg, Town of Blacksburg; Charles County MD, City of Gaithersburg MD; Prince George's County MD (the website only; the County Council's Legistar reads). A firewall that is not Akamai answers 403 at Nelson County, Town of Chase City and Baltimore County MD.

To: the county administrator, copy to IT. Subject: Allowing a public-notice service through your firewall

> I run Agenda Ahead, a free service that reads local agendas each morning and alerts residents, in plain words, to solar, battery storage, data center, zoning and moratorium items before the meeting, with a link to your agenda.
>
> Your website's firewall answers 403 to our program (AgendaAheadBot). We do not get around firewalls, so your Board of Supervisors, Planning Commission and Board of Zoning Appeals agendas are invisible to us today. [For Fauquier: this matters right now, as your October 8 vote to end by-right data centers shows how closely residents want to follow these agendas.]
>
> Could your IT staff allow the user agent `AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)` to read your agenda pages? If the firewall is Akamai Bot Manager, we have also asked Akamai to verify the bot; a client-side allow rule on the user agent (or on our Web Bot Auth signature, key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory) is quicker. We make at most one request a second and read only agenda pages and files.
>
> If that is not possible, please add our address to the list that receives agenda packets when they go to board members, as Va. Code § 2.2-3707 provides [Maryland: your agenda notification list].
>
> We stop on request and name a technical contact. Thank you.
>
> [your name], Agenda Ahead, [your address]

## 5. robots.txt disallows us, or asks for a crawl delay over our cap

robots.txt on the site disallows AgendaAheadBot (or every bot): Charlotte County, Rappahannock County, Carroll County MD, Somerset County MD; Richmond County (the agenda files, not the pages); `onboard.loudoun.gov` (Loudoun County's Planning Commission). A crawl delay above what we honour (20 s for listing pages, 10 s for files): Alleghany County (60 s), Fluvanna County (15 s on files), City of Portsmouth (20 s, so the files cannot be read).

To: the county administrator or webmaster. Subject: robots.txt and a public-notice service

> I run Agenda Ahead, a free service that reads local agendas each morning and tells residents, in plain words, when solar, battery storage, data center, zoning or moratorium items are coming before a board, with a link to your agenda.
>
> Your website's robots.txt [disallows our program / asks every program to wait N seconds between requests]. We honour robots.txt to the letter, so we do not read your agendas today. [Charlotte County: with Randolph Solar and the county's other solar applications, residents have asked us for this.]
>
> Could you add these lines to robots.txt (they change nothing for other visitors):
>
>     User-agent: AgendaAheadBot
>     Allow: /
>     Crawl-delay: 5
>
> Our program makes a few requests a day to your site: the agenda listing pages and any new agenda file. If you prefer, add our address to the list that receives agenda packets when they go to board members (Va. Code § 2.2-3707) or send us an RSS feed address.
>
> We stop on request and name a technical contact. Thank you.
>
> [your name], Agenda Ahead, [your address]

## 6. Agendas only in a document store, or on a page built by script

Laserfiche WebLink only, no dated listing: Montgomery County VA (`weblink.montva.com`), City of Bristol, City of Virginia Beach (full agendas; the clerk's brief agenda reads), Loudoun County (Planning Commission, `lfportal.loudoun.gov`). Homepage built by script with no server HTML: City of Manassas Park, Town of Dumfries, Town of Clarksville. No agenda page found at all: Grayson County, Town of Blackstone. Board pages with no dated agenda in the window: Dickenson County, Towns of Round Hill, Middleburg, Luray, Orange, Christiansburg, Abingdon, Vinton (their CivicPlus Agenda Centers are empty; agendas go to Archive Center pages without dates or to video pages).

To: the clerk. Subject: Where do your agendas live?

> I run Agenda Ahead, a free service that reads local agendas each morning and tells residents, in plain words, when solar, battery storage, data center, zoning or moratorium items are coming before a board, linking to your agenda.
>
> We could not find a page on your website that lists each meeting's date with its agenda file [Laserfiche: your agendas are in a Laserfiche folder, which has no dates we can read; script-only: your pages are built in the browser, which our program cannot run]. We read 240 Massachusetts towns and most Virginia counties this way without any effort on the town's part, so we would like to add you.
>
> Any one of these would do: a page or RSS feed that lists meetings with dates and links to the agenda files (CivicPlus Agenda Center does this if you have it); an email copy of each agenda when it is published (Va. Code § 2.2-3707 lets anyone ask for meeting notices); or the address of an existing listing we missed.
>
> Thank you for your time.
>
> [your name], Agenda Ahead, [your address]

---

## 7. Diligent (BoardDocs and Diligent Community / iCompass CivicWeb)

To: Diligent partner programme (https://www.diligent.com/company/partners) and BoardDocs support. Subject: Allow-list request for a public-notice crawler

> Agenda Ahead is a free public-notice service: it reads published local government agendas every morning and alerts residents to land-use and energy-siting items before the meeting, always linking to the source. Our crawler, AgendaAheadBot (`AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`), obeys robots.txt, makes at most one request a second to a host, never logs in, never posts and never solves challenges.
>
> Two Diligent products refuse it: BoardDocs (`go.boarddocs.com`, `www.boarddocs.com`) answers HTTP 403 to every request, and Diligent Community / iCompass (`*.civicweb.net`, `*.community.diligentoneplatform.com`) disallows all bots in robots.txt. Public agenda pages are what we need: `Board.nsf/Public` and the agenda PDFs on BoardDocs; `/Portal/MeetingInformation.aspx` and `/document/` on CivicWeb and Community.
>
> Ask: allow AgendaAheadBot on those public paths, at most one request every five seconds per client and 50 requests a day per client, agendas and minutes only. Clients who have asked or will ask: Accomack, Northampton, Prince George and Pulaski Counties and the Town of Culpeper, Virginia (BoardDocs); Essex and Northumberland Counties, Virginia (one board each); St. Mary's County, Maryland; Lancaster County, Newport News and Williamsburg, Virginia (CivicWeb); earlier, Hillsdale, Saginaw, Tuscola and Jackson Counties and Camden Township, Michigan.
>
> Offer: a named technical contact, a monthly request log, and we stop on request. If you would rather provide a feed or export of published agendas, we can read that instead.

## 8. Granicus (ViewPublisher, iQM2, Legistar)

To: Granicus partner portal (https://granicus.com/granicus-online-partner-portal/) and support, with the client requests from section 2 in parallel. Subject: robots.txt allowance for a public-notice crawler

> Agenda Ahead reads published local agendas every morning and alerts residents to land-use and energy-siting items before the meeting, linking to the source. Our crawler, AgendaAheadBot, obeys robots.txt, keeps to one request a second per host, never logs in or posts, and signs its requests (Web Bot Auth).
>
> Your robots.txt on `*.granicus.com` and `*.iqm2.com` allows only named search engines, and iQM2 answers 429 to low-rate reads. We therefore cannot read the agendas of Harford, Talbot and Washington Counties, the Cities of Frederick, Fairfax and Manassas and the Towns of Ashland and Haymarket, among others in Virginia and Maryland, and of Framingham in Massachusetts.
>
> Ask: on `*.granicus.com` add `User-agent: AgendaAheadBot` with `Allow` lines for `/ViewPublisher.php`, `/AgendaViewer.php`, `/MetaViewer.php` and `/GeneratedAgendaViewer.php`; on `*.iqm2.com` allow `/Citizens/` agenda and detail pages and lift the 429 for our rate. We would make at most one request every five seconds per client and 50 a day per client, agenda and minutes pages only, no video. Legistar's public web API already serves us well; we read Legistar clients through it and their `MeetingDetail.aspx` pages, never `legistar1.com`.
>
> Offer: a named technical contact, a monthly request log, stop on request.

## 9. Cloudflare Verified Bots

Already in motion (OPERATIONS.md, Bot verification): submit AgendaAheadBot to BotBase with the key directory `https://agendaahead.vercel.app/.well-known/http-message-signatures-directory`. Note for the form's "sites that would benefit" field: Culpeper, Highland and James City Counties, Fredericksburg, Waynesboro, Lovettsville, Strasburg and Chatham, Virginia; Becket, Middleborough and Barnstable, Massachusetts. Verified Bot status does not pass Free-plan Bot Fight Mode, so the locality letters in section 3 still go out.

## 10. Akamai Bot Manager

To: the bot verification request on https://www.akamai.com/products/bot-manager. Subject: Bot verification request, AgendaAheadBot

> AgendaAheadBot (`AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`) reads published local government agendas for Agenda Ahead, a free public-notice service. It obeys robots.txt, keeps to one request a second per host, never logs in or posts, and signs requests under Web Bot Auth with the key directory at https://agendaahead.vercel.app/.well-known/http-message-signatures-directory. Customers whose sites answer 403 to it, and who we are asking to allow it: Albemarle, Bedford, Clarke, Fauquier and Frederick Counties, Lexington, Staunton, Leesburg and Blacksburg, Virginia; Charles County, Gaithersburg and Prince George's County, Maryland. Please add it to the known-bots directory, or tell us what the verification needs.

## 11. Virginia notice requests (every blocked Virginia locality, as a backstop)

Va. Code § 2.2-3707 lets any person file an annual written request for notice of all meetings of a public body, with electronic notice if the person does not object, and requires at least one copy of the proposed agenda and all agenda packets to be available for public inspection when they are furnished to members. One letter per locality, to the clerk of each body, filed once a year (note the date; the request lapses).

> To the Clerk of the [Board of Supervisors / Planning Commission / Board of Zoning Appeals], [County]:
>
> Under Va. Code § 2.2-3707, I request notice of all meetings of the [body] for the coming year, by electronic mail to [your address], and ask that the proposed agenda and the agenda packet be sent to the same address when they are furnished to the members. Name: [your name]. Organization: Agenda Ahead. Address: [postal address]. Daytime telephone: [number].
>
> Agenda Ahead is a free service that tells residents, in plain words, when land-use and energy items are coming before local boards, linking to the official agenda. Thank you.

Maryland has no equivalent right to ask; the Open Meetings Act (General Provisions § 3-302 and § 3-302.1) requires reasonable advance notice and an agenda available before the meeting. For the Maryland localities above, ask the clerk to add the address to the agenda notification list (Montgomery and Prince George's Counties, Howard County and Frederick County each run one).

## Not requests: retry from the production host

Unreachable from the test sandbox only (the egress proxy answered 502 to CONNECT, or robots.txt timed out, on three tries): Bath, Buchanan, Giles, Lee, New Kent, Rockingham, Russell and Tazewell Counties; the Towns of Hamilton, Woodstock, Stephens City and Gordonsville; Laytonsville and Barnesville, Maryland. Floyd County's listed address (`www.floydcova.org`) answered 404; the current address needs checking. Run `python3 experiments/va_md_wave.py discover --state VA --places "Bath County,Buchanan County,..."` from the production host before writing to any of them.
