# Meeting-monitoring tools: what people like and dislike

Screenshots: `/tmp/claude-0/-home-user-sulmusic2-star/815cfdd0-e090-5147-aee8-a5db345f6b5d/scratchpad/research/meeting-tools/` (`-desktop` 1366×900, `-mobile` 390×844). G2, TrustRadius and Reddit blocked automated reading.

## 1. Services studied
- **Curate (FiscalNote)**: AI scan of agendas/minutes from 12,000+ municipalities, daily email reports; businesses pay, demo-only pricing.
- **Granicus govMeetings/Legistar**: clerk software; public portal with search, RSS, account-based alerts; cities pay.
- **CivicPlus Agenda Center + Notify Me**: agendas on the town site; per-board email/SMS after creating an account.
- **BoardDocs (Diligent)**: school-board/council portal; Capterra 4.6 (73).
- **CivicClerk (CivicPlus Agenda & Meeting Management)**: calendar portal, sign in to subscribe; 0 reviews.
- **Municode Meetings** (now CivicPlus "Essential"): date-table portal with Subscribe tab.
- **OpenGov**: no agenda product listed.
- **Councilmatic** (Chicago, NYC): free nonprofit tracker; email/RSS alerts on committees, legislation, searches.
- **Agenda Watch** (Big Local News/RJI): keyword search, real-time/daily/weekly alerts; journalists at verified organizations only.
- **Plural** (ex Civic Eagle, now SAI360): state/federal bills; $609/yr seat, $5,000/yr team; no local coverage.
- **Newer**: Hamlet (3,000+ bodies, free search, paid alerts for developers, data-center firms, PACs); Next30Days (Seattle, free twice-weekly Legistar digest); citymeetings.nyc (one person, "AI and human oversight"); CivicSearch; Engagic (open source); Legistar Agenda Radar (Apify, $1/1,000 results); M4L AWARE (Moms for Liberty, Oct 2026, scores school-board items 1–10).

## 2. What people praise
**It catches what they would have missed.** "This product has helped keep track of activity that otherwise would have gone unnoticed." (FiscalNote, Capterra, 2019-09-27). "Very little has slipped through the cracks." (FiscalNote, Capterra, 2019-06-26).

**Relevant alerts that link to the source.** "Love getting alerts … Direct source to bill … Discovery alerts pick up on good/relevant material" (FiscalNote, Capterra, 2019-06-21). Next30Days: "Every item links back to official council records, so you can verify before you share."

**One searchable place.** "The searchable archive is the most helpful feature … The layout is also very easy to navigate even for the public." (BoardDocs, Capterra, 2025-06-20). "It is easy to view all school board meeting agenda items" (BoardDocs, Capterra, 2026-07-07).

**Short, same-day, human-checked.** citymeetings.nyc: the "3-minute Q&A or testimony you care about in a 12-hour hearing"; errors "sometimes appear" and readers report them.

## 3. What people complain about
**Too many clicks.** "I can't imagine that someone who comes to a meeting once every five years is going to be able to find (materials)." (Fort Worth city secretary, Fort Worth Report, 2022-05-18). "It can be tough for 'more experienced' constituents to navigate the site, find the schedules and documents they are seeking." (BoardDocs, Capterra, 2025-08-10).

**Search and speed.** "Search is terrible." (BoardDocs, Capterra, 2022-11-03). "It takes forever to load meeting information at times." (2026-07-07). "Legistar can at times be sluggish to respond or counterintuitive in its user interface." (Ann Arbor Chronicle, 2014-02-15).

**Vague agendas, too many meetings.** "Some agendas are helpful; others contain vague action items and jargon." (Isthmus, 2025-06-12). "Many of us have missed important public meetings because there simply are too many to cover." (RJI, 2023-06-23). "It's a total black box, and almost intentionally opaque." (Hamlet founder, TechCrunch, 2025-12-05).

**Accounts, spam folders, blunt unsubscribe.** Notify Me: "You must sign in to subscribe"; Peapack-Gladstone: "We have been getting calls about not getting PG Notify." Iowa on Granicus: the footer link "could unsubscribe you from all topics."

**Price and lag.** "It's so expensive" (FiscalNote, Capterra, 2022-01-28). "Sometimes does not provide latest legislative update" (2019-06-12). "The pricing felt higher than some simpler alternatives." (BoardDocs, 2025-10-30).

## 4. Look and feel
- Vendor pages (`curate-desktop`, `granicus-govmeetings-desktop`, `fiscalnote-local-desktop`): hero photo, "Book a demo", no prices, cookie banner, chat widget, 5–7 s loads. Sales pages.
- Portals: `legistar-seattle-desktop` is a 2005-style table of 3,979 rows, PDF icons, "Sign In" for alerts; `agendacenter-daytona-desktop` buries "Agendas are posted here" under a city hero and seven circle icons; `notifyme-laverne-desktop` demands sign-in first; `civicclerk-morganhill-desktop` showed grey skeleton cards for 3 s; `boarddocs-public-desktop` opens on a mission statement. Dates are numerals (10/21/2026), places addresses, sources PDF icons.
- Independent sites read trustworthy: `councilmatic-chicago-desktop` ("demystified", search first), `citymeetings-nyc-desktop` (press logos, named testimonials), `civicsearch-desktop` (one search box, "datacenter" deep dive), `next30days-desktop` ("Oldest source observation shown: Tue Sep 22"). `agendawatch-desktop` is a login wall.
- Ours: `aa-home-desktop/-mobile` load under 1 s, no banner; town box, "This week" list with town, board, "New" pill, Hearing/Vote tag. `aa-meeting-mobile`: time, room, "Watch on Channel 15", agenda PDF. `aa-watch-desktop`: "No account needed." Weak: `aa-404-desktop` is Vercel's default error page with a debug ID; `aa-search-desktop` is an empty box; nothing says when we last read each agenda.

## 5. Implications for Agenda Ahead
1. Replace the Vercel 404 with our own page (town box, nearby towns). Cheapest fix.
2. Print "Agenda read Oct 16, 6:10 am" on town and meeting pages; Next30Days shows its source time; lag is the main paid-tool complaint.
3. Say "No account needed" on the home page; every incumbent alert path needs a sign-in.
4. Put "report an error" on each write-up and say how fast fixes land, as citymeetings.nyc does; nobody else publishes an accuracy process.
5. Seed /search with example results and a per-town "last 30 days" so a first visit is never empty; "terrible" search is the top portal complaint.
6. Add "what this hearing decides, what you can do, by when" to meeting pages; Next30Days' "where there is still time to act" is what moves people.
7. For businesses watching many towns, offer a keyword RSS/Slack feed with per-item source links before any pricing; Hamlet, Curate and Legistar Agenda Radar sell that.

## 6. Sources
https://www.capterra.com/p/224307/BoardDocs/reviews/ · https://www.capterra.com/p/185611/FiscalNote/reviews/ · https://www.getapp.com/government-social-services-software/a/curate/ · https://www.getapp.com/nonprofit-software/a/enview/ · https://capterra.com/p/202580/CivicClerk/ · https://pluralpolicy.com/pricing/ · https://fiscalnote.com/products/curate · https://fiscalnote.com/solutions/us-local-bill-tracker · https://granicus.com/product/agenda-management-legistar/ · https://www.civicplus.com/agenda-meeting-management/ · https://opengov.com/products/ · https://annarborchronicle.com/tag/legistar/index.html · https://isthmus.com/opinion/from-the-editor/local-governments-mixed-record-on-meeting-notices/ · https://fortworthreport.org/2022/05/18/residents-will-see-changes-to-fort-worth-city-council-agenda-posting%EF%BF%BC/ · https://my.lwv.org/node/26207 · https://www.talawanda.org/district-blog/entry/formatting-issues-with-board-docs-software-program/ · https://www.cityofmadison.com/council/district10/blog/2023-10-28/more-about-agenda-navigation · https://www.brisbaneca.gov/CivicAlerts.asp?AID=302 · https://revelstoke.ca/DocumentCenter/View/15712/City-of-Revelstoke_Notify-Me-Subscription-Service_13-January-2026 · https://www.peapackgladstone.org/resident/pg-notify · https://dxtraining.iowa.gov/digital-services/granicus-communications/granicus-communications-subscribing-unsubscribing-and-unsuppressing · https://laverneca.gov/List.aspx · https://www.daytonabeach.gov/AgendaCenter · https://datamade.us/blog/councilmatic-notifications/ · https://chicago.councilmatic.org/ · https://rjionline.org/news/welcome-to-agenda-watch/ · https://agendawatch.org/ · https://techcrunch.com/?p=3073247 · https://thehustle.co/news/local-government-but-more-accessible-and-hilarious · https://www.publicceo.com/2026/02/hamlet-launches-nationwide-public-meeting-coverage-over-3000-local-governments-videos-now-discoverable/ · https://www.publicceo.com/2024/06/hamlet-partners-with-the-city-of-palo-alto-to-provide-ai-powered-city-council-summaries/ · https://www.geekwire.com/2026/can-ai-revive-democracy-former-amazon-product-manager-builds-tool-to-spark-civic-engagement/ · https://www.next30days.org/ · https://citymeetings.nyc/about/ · https://www.vikramoberoi.com/how-citymeetings-nyc-uses-ai-to-make-it-easy-to-navigate-city-council-meetings/ · https://civicsearch.org · https://civictech.guide/projects/engagic · https://apify.com/opalescent_game/legistar-agenda-radar · https://www.klif.com/2026/10/15/moms-for-liberty-puts-13000-school-districts-on-notice-with-ai-watchdog/ · https://agendaahead.vercel.app (home, /ma/carver, /m/carver-conservation-commission-2026-10-21, /upcoming, /attorney-general, /watch, /search, /alerts-for-groups)
