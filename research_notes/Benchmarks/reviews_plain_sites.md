# Plain information sites: what earns trust, what earns complaints

16 Oct 2026. Screenshots in `research/plain-sites/` (`pass2/`, `pass3/`). Reddit blocked our fetcher; its quotes come via mirrors.

## 1. Services studied

GOV.UK (taxpayer-funded). Weather.gov (federal). Wikipedia (donations). Craigslist (paid job and car ads). Hacker News (Y Combinator). MBTA.com, rebuilt 2017. Boston.gov (2016), Mass.gov (2017). NJ Transit site and app. Zillow, Redfin (agent referrals, mortgages). SeeClickFix/CivicPlus, BOS:311 (cities pay). AllTrails (free tier plus $36–80/yr). Town sites on CivicPlus (Carver, Plymouth, Wareham, Amherst) and behind Cloudflare (Middleborough, Kingston); towns pay.

## 2. What people praise

**Source data, no ads.** "radar.weather.gov is a terrific site, works on all devices... with zero Ads" (circusfly, HN, 2024). "your local NWS office's AFD... is easily the most accurate, honest forecast you can find" (teeray, same thread). "NWS is always the gold standard and free" (r/Pennsylvania, Jan 2026).

**Do the task and leave.** "you go in and do whatever you need to do, and then you leave" (codeulike on GOV.UK, HN, 2021).

**Unchanged and fast.** Craigslist: "For the love of god...it works. Don't change it" (cuda13579, Slashdot, 2022).

**Status first, dates shown.** MBTA: "77% of visitors to mbta.com click through to a schedule page or a stops page" (2019). CivicPlus prints "Posted Oct 12, 2026 3:50 PM" beside every agenda.

## 3. What people complain about

**Ads and prompts in the way.** "Users have hated popups since the 1990s, and they still hate them today" (NN/g, 2021). Cookie banners: "a nag-box that appears every time someone visits a new website" (ablob, HN, Jul 2026).

**Subscription traps.** AllTrails, Trustpilot 1.3/5: "charged me 35.99 for a full year anyway" (Aug 2026); "I HATE the continuous effort to try and get you to pay out more money" (Jul 2026).

**Stale data shown as live; closed without fixing.** NJ Transit: "It lags. It crashes. It says no buses are coming when they are" (Jasmine Hamada, NorthJersey.com, 2023). AllTrails: "they post reviews from a hike they did three years ago" (squidvicious, Oregon Hikers, 2024). BOS:311: "the only response... is 'case closed' or 'duplicate request'" (2018).

**Redesigns that hide the thing.** Weather.gov 2.0: "incredibly slow and has more limited useful information compared to its predecessor" (ericjmorey, HN, 2024). Northfield's new CivicPlus site: "the calendar is not as visible"; alert subscriptions "did not transfer" (Recorder, Feb 2026).

**Town agendas.** Mashpee: "our committee disappeared from the town website list" (Nov 2024). Sturbridge complaint: the agenda page "does not indicate the date and time that the agenda was posted" (May 2025). Amherst: half of 49 boards post minutes late (Aug 2025); after a denial-of-service attack the clerk was "unable to post the agenda" (Mar 2025). GDS: PDFs are "less likely to be actively maintained." Undated pages: "if it doesn't have a date, that's (to me) a much stronger negative signal than an old date" (dragonwriter, HN, 2014).

## 4. Look and feel

**Reads honest:** one text column, a search box, dates and source inline, about a second to load. GOV.UK (`govuk-bank-holidays-desktop.png`): equal Accept/Reject cookie buttons, then "The next bank holiday in England and Wales is 25 December". Weather.gov zone forecast (`pass2/weathergov-forecast-carver-desktop.png`): "Last update 16 Oct 12:51 pm EDT", plain day-by-day text, no ads, but 27–45 s to load.

**Reads like a sales page:** hero photo, slogan, sign-in. Zillow mobile (`zillow-home-mobile.png`) drops a "Sign in to Zillow with Google" sheet over listings. NJ Transit (`njtransit-home-mobile.png`): red alert, hero photo, cookie box with only "Accept". Town sites (`pass3/town-carver-desktop.png`, `pass3/town-wareham-desktop.png`): "EMERGENCY ALERT" banner used for a survey, full-width photo, agendas two taps down; Wareham took 16 s. Agenda Center (`pass3/town-carver-agendas-desktop.png`): "Adobe Reader may be required", pre-2025 files moved to "Document Center", but a posted timestamp on every row. Middleborough and Kingston answered our browser with Cloudflare "Attention Required" (403).

**Agenda Ahead** (`agendaahead-home-desktop.png`, `pass2/agendaahead-meeting-desktop.png`) is in the honest group: text, one search box, "Free", date/board/place per row, "Agenda (PDF)", "Before this:" history, posted/read dates on meeting pages, no cookie banner, email asked only on /watch, under 1.5 s. Gaps: home and /upcoming say "every morning" with no timestamp; list rows lack a posted time; "Get alerts" promises email while saying "Email alerts are coming"; no page says who runs it; Middleborough is "(can't read yet)" with no reason.

## 5. Implications for Agenda Ahead

1. Show the check time on every page ("Checked today 6:12 am") and a posted time per item, as CivicPlus does (Sturbridge; dragonwriter).
2. Keep nothing over the content: no cookie banner, modal or sign-in sheet; email stays optional (NN/g; Zillow).
3. Add one line on who runs this, and a reason beside "(can't read yet)", e.g. "Middleborough's site blocks automated readers" (GOV.UK "Make things open"; Mashpee).
4. Ship email alerts before advertising them; print "once a day, only when new, one click to stop" on the form (Northfield; AllTrails).
5. Keep the HTML summary ahead of the PDF and keep marking postponed or cancelled items (GDS; "case closed").
6. No redesign for looks: no hero photo, one column, under 2 s (Weather.gov 2.0, Northfield).
7. Put "Report a problem" on list pages too (Mass.gov: 30,000 feedback items a month; Boston.gov: 88% of emails were actionable).

## 6. Sources

https://www.gov.uk/guidance/government-design-principles
https://news.ycombinator.com/item?id=3811052
https://news.ycombinator.com/item?id=17541045
https://news.ycombinator.com/item?id=27672100
https://gds.blog.gov.uk/2018/07/16/why-gov-uk-content-should-be-published-in-html-and-not-pdf/
https://www.dezeen.com/2013/04/17/mail-online-gov-uk-boring-designs-of-the-year-design-museum/
https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-structure/
https://news.ycombinator.com/item?id=39571308
https://news.ycombinator.com/item?id=44018282
https://hn.algolia.com/api/v1/search?query=%22weather.gov%22%20ads&tags=comment
https://reddit.sentinel-team.org/posts/1qnpy21/snapshots/2026-01-27T02%3A11%3A03.31726Z
https://reddit.sentinel-team.org/posts/1q4cztp/snapshots/2026-01-05T16%3A16%3A39.563928Z
https://apps.apple.com/us/app/the-weather-channel-forecast/id295646461
https://unstar.app/blog/weather-channel-app-ads-before-alerts-radar-reviews-2026
https://news.ycombinator.com/item?id=34441654
https://yougov.co.uk/news/2014/08/09/more-british-people-trust-wikipedia-trust-news
https://www.mediawiki.org/wiki/Reading/Web/Desktop_Improvements/Repository/Sentiment_Survey
https://tech.slashdot.org/story/22/09/16/2123239/why-craigslist-still-looks-the-same-after-25-years
https://news.ycombinator.com/item?id=18196816
https://news.ycombinator.com/item?id=8574198
https://news.ycombinator.com/item?id=8286898
https://archive.blogs.harvard.edu/liana/2019/09/
https://universalhub.com/node/93724
https://www.freshtilledsoil.com/transit-transformation-mbta-website-redesign-challenge/
https://news.ycombinator.com/item?id=7486525
https://news.ycombinator.com/item?id=18181320
https://statescoop.com/?p=6805
https://www.acquia.com/resources/case-studies/city-boston
https://boston.gov/node/29171
https://www.bostonglobe.com/metro/2017/06/01/state-official-homepage-gets-makeover/iWymdhAg0ExfOq0aByinkI/story.html
https://lastcallmedia.com/mass-gov-feedback
https://apps.apple.com/us/app/nj-transit-mobile-app/id589549928
https://www.yahoo.com/news/nj-transit-bus-time-knows-083103497.html
https://apps.apple.com/us/app/zillow-real-estate-rentals/id310738695
https://news.ycombinator.com/item?id=10343949
https://news.ycombinator.com/item?id=14666867
https://apps.apple.com/us/app/seeclickfix-311/id322000552
https://apps.apple.com/us/app/bos-311/id330894558
https://www.capterra.com/p/202342/SeeClickFix/reviews/?page=2
https://theraleighcommons.org/raleighpublicrecord/news/2014/10/10/a-social-network-for-concerned-citizens/
https://www.trustpilot.com/review/alltrails.com
https://www.oregonhikers.org/forum/viewtopic.php?p=230624
https://mwm.ai/articles/alltrails-v26-7-40-crashes-on-offline-maps-sparking-user-backlash-in-july-2026
https://doverma.gov/m/faq?cat=49
https://tyngsboroughma.gov/CivicAlerts.asp?AID=31
https://www.capenews.net/mashpee/news/mashpee-cpc-discusses-subcommittee-amidst-communication-failures-at-town-hall/article_421dc3a6-ac6b-11ef-a117-aff5b69fd63a.html
https://www.amherstindy.org/?p=71635
https://www.amherstindy.org/?p=68259
https://www.amherstindy.org/2026/08/07/town-of-amherst-introduces-new-agenda-and-minutes-center-for-public-meetings/
https://plymptonhalifaxexpress.com/many-town-web-sites-failed-monday/
https://recorder.com/2026/02/08/new-northfield-site-launched/
https://www.sturbridge.gov/planning-board/agenda/planning-board-meeting-agenda-94
https://www.mass.gov/doc/westwood-citizen-engagement/download
https://commoncause.org/massachusetts/resource/transparency-in-massachusetts-municipal-websites
https://www.nngroup.com/articles/overlay-overload/
https://news.ycombinator.com/item?id=49057175
https://uxmovement.com/forms/the-conversion-rate-illusion-of-modal-newsletter-forms/
https://www.plainlanguage.gov/guidelines/audience/
https://digital.gov/guides/plain-language
https://agendaahead.vercel.app/
