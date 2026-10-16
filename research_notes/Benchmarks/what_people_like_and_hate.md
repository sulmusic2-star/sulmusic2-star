# What people praise and complain about in services like ours (Oct 16, 2026)

Five researchers each took a category, read the reviews (Capterra, Trustpilot, the app stores, Hacker News, Reddit through mirrors, local press) and used the sites at 1366 and 390 px without accounts or forms. Their reports are beside this note: `reviews_meeting_tools.md` (Curate, Granicus, CivicPlus, BoardDocs, Councilmatic, Hamlet, Next30Days, citymeetings.nyc), `reviews_local_news.md` (Patch, Nextdoor, Citizen, Ring, Front Porch Forum, Axios Local, the Massachusetts nonprofits), `reviews_alert_tools.md` (Google Alerts, Visualping, Distill, Feedly, Inoreader, Morning Brew, Axios), `reviews_trackers.md` (GovTrack, LegiScan, Plural, FastDemocracy, Quorum, FiscalNote, malegislature.gov, the AG portal, MassDEP) and `reviews_plain_sites.md` (GOV.UK, weather.gov, Wikipedia, Craigslist, MBTA.com, Boston.gov, town sites on CivicPlus). Quotes below are theirs, with the source each report names.

## What people say they rely on, across every category

1. **Silence until the one thing changes.** "No spam emails, just the notification letting me know the thing I was surveilling finally had changed" (Visualping, Trustpilot). Front Porch Forum: one digest a day, 81 percent of members say it makes them better informed, 61 percent went to a meeting because of a post.
2. **A direct link to the real document, and a date on it.** "Direct source to bill" (FiscalNote, Capterra). GovTrack prints "Source: Congress.gov, Last Updated". CivicPlus prints "Posted Oct 12, 2026 3:50 PM" beside every agenda. "If it doesn't have a date, that's a much stronger negative signal than an old date" (Hacker News).
3. **Nothing slips.** "Helped keep track of activity that otherwise would have gone unnoticed" (FiscalNote). This is what businesses pay $1,000 to $5,000 a year for.
4. **Do the task and leave.** GOV.UK: "you go in and do whatever you need to do, and then you leave." Craigslist: "it works. Don't change it." Weather.gov: "zero ads."
5. **Short, same time, human.** Morning Brew: "one letter every weekday, clean, concise." Axios Local "far better than anything I ever read in a newspaper." citymeetings.nyc: the three minutes you care about in a twelve-hour hearing, with errors reported and fixed.

## What makes them quit

1. **Noise and wrong matches.** "I get an alert every day with the subject 'Important Change'" (Visualping). "Still receive a lot of bills that don't impact my business" (Quorum). Patch's CEO: "'It's the wrong Springfield', we hear that at least single-digit times a week."
2. **Notifications they cannot stop.** "Over 130 clicks to disable email and push notifications" (Nextdoor). "Impossible to unsubscribe" (Ring). "Purposely makes it hard to cancel" (Feedly).
3. **Fear, ads and paywalls on top of safety or civic information.** "People on this app become more and more paranoid" (Nextdoor). "Be ready to be spammed by ads for premium" (Citizen). "Nearly every article is paywalled" (Google News).
4. **Stale data shown as live; cases closed without fixing.** NJ Transit "says no buses are coming when they are." BOS:311: "the only response is 'case closed'." Open States: "MA: new bills are delayed."
5. **Accounts and sign-in walls for the simplest thing.** CivicPlus Notify Me: "You must sign in to subscribe." Legistar alerts, BillTrack50 search, Plural tracking: all behind an account.
6. **Price, lock-in, shrinking free tiers.** "I need to give a 60 day notice" (Quorum). "IFTTT switches off functionality for existing free accounts." "Used to be really good but now they're too expensive and enterprise-y" (Visualping).
7. **Redesigns that hide the thing.** Weather.gov 2.0 "incredibly slow and more limited." Northfield's new town site: "the calendar is not as visible", alert subscriptions "did not transfer."

## How the sites look next to ours

The sales pages (Curate, Granicus, Quorum, FiscalNote, Visualping, Citizen, Ring) share a hero photo, a slogan, "Book a demo", a cookie wall and 5 to 11 second loads with dozens of third-party hosts. The portals residents meet (Legistar, Agenda Center, BoardDocs) are tables of PDF icons behind a city hero, with sign-in for alerts. The sites people call honest (GOV.UK, weather.gov zone forecasts, Councilmatic, Next30Days, the Plymouth Independent, Universal Hub) are one text column, a search box, dates and sources inline, no overlays.

Every researcher put Agenda Ahead in the honest group: text, one box, "Free", date, board and place per row, the agenda PDF one click away, "Before this" history, a glossary, no cookie banner or trackers, under two seconds. What they found missing, service by service: a visible check time on every page and a posted time per item; a sample alert before anyone types an email; the cadence and the stop link stated first; "without an account or ads" said out loud; a reason beside "can't read yet"; a per-item way to say "wrong town" or "not about this"; a weekly option; one permanent page per project across its hearings; a line on who runs this; and our own 404 page instead of the platform's.

## What we changed the same day (commits d43a721 to ea7506b)

- "Free, without an account or ads." on the home page; the cadence promise and one-click stop on the first alerts screen; example searches so /search is never an empty box; our own 404 page with the town box.
- The time of day we last read a town on town and meeting pages ("most recently Oct 16, 7:07 am"); the home count matches the list it links to.
- Feeds say what the page says: cancelled, start hour, room, the site's sentence, one entry per item; the calendar file on every meeting page.
- The Search export fixed and enriched (items, status, time, place, both links); re-posted agendas appear once in Search.

## Still open, from this research

- **A sample alert on the home page and /watch**, and a weekly roundup beside daily-when-new (both wait on email, which the owner has deferred).
- **"Wrong town" or "not about this" per item**, one tap. Cheap once there is a place to read them.
- **One page per project** across its hearings (Federal Pond Solar: Sep 2 to Nov 4). Design work.
- **A reason beside each "can't read yet"** (the site blocks programs; the vendor's bot check). The health file has the error; the page can say it.
- **A line on who runs this** on How it works. The owner's call (`OWNER_NAME`).
- **A posted time per item** from the town's listing, as CivicPlus shows it. The crawler reads the listing; it can keep the posted time.
