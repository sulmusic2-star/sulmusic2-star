# Legislative, regulatory and government-data trackers

Sources: Capterra, Software Advice, G2 snippets, Reddit, HN, press; Playwright at 1366x900 and 390x844, 16 Oct 2026. LegiScan, BGov and federalregister.gov blocked the browser. Screenshots: `research/trackers/<name>-desktop.png` / `-mobile.png`.

## 1. Services studied
- **GovTrack** – free federal tracker; ads, Patreon, "Hide The Ads" plan.
- **LegiScan** – 50 states; free alerts, Pro from $100/yr.
- **Open States / Plural** – open data; Plural $609–$5,000/yr, no free plan.
- **FastDemocracy** – free tier plus "Professional"; no public price.
- **Ballotpedia** – nonprofit encyclopedia; donations.
- **BillTrack50** – $1,000/yr one state; free search needs an account, no alerts.
- **Quorum, FiscalNote** – enterprise suites, quote only.
- **Bloomberg Government** – $5,700/user/yr (2011 press).
- **malegislature.gov/MyLegislature, Mass.gov, AG Municipal Law Unit, MassDEP portals, Federal Register, Regulations.gov** – government, free.

## 2. What people praise
**One place, linked to the real document.** "the status of legislation is updated throughout the day… each bill has a direct link to the actual legislation" (Capterra, Quorum, 15 Feb 2021). "Direct source to bill" (Capterra, FiscalNote, 21 Jun 2019).

**Nothing slips.** "helped keep track of activity that otherwise would have gone unnoticed" (Capterra, FiscalNote, 27 Sep 2019). "ensuring we do not fall behind in tracking legislation" (Capterra, Quorum, 27 Apr 2020).

**Plain, free, comprehensive.** "govtrack.us is a great resource for knowing what is happening" (r/50501, 27 Oct 2025); "a good comprehensive view of legislation and voting records" (r/Austin, 18 Feb 2026). federalregister.gov: "one of the most usable, data-intensive sites around" (HN, 2012).

## 3. What people complain about
**Noise and bad defaults.** "Still receive a lot of bills that don't impact my business" (Capterra, Quorum, 24 Apr 2020). FastDemocracy: "many irrelevant emails and it is hard to sort between priority emails v. spam"; "overwhelming with the default settings" (G2). "Wish there was a way to 'star' or 'flag' a bill… so… it is clear which ones I should tune in to first" (FiscalNote, 21 Jun 2019).

**Late or missing data.** "Sometimes does not provide latest legislative update, for example a Governor signing or vetoing a bill" (Capterra, FiscalNote, 12 Jun 2019). Open States GitHub: "MA: new bills are delayed in being added" (2021), "MA-events failing since at least 2024-11-04".

**Price, lock-in, forced migration.** "It's not worth the money for state work… I need to give a 60 day notice" (Capterra, Quorum, 26 Jan 2025). "The worst 'migration' experience I've had in more than a decade of advocacy work" (3 Nov 2025). "It's so expensive but well worth the price if you company can afford it" (FiscalNote, 28 Jan 2022). Why pay: "most information is hidden behind paid services" (r/LawFirm, 22 Apr 2025); "A small advantage in anticipating a regulation or legislative markup can be worth a great deal" (Sunlight, 2010).

**Government sites.** State audit, 21 Oct 2024: the website "lacks apparent content and ease of site navigation regarding pending and enacted legislation." MyLegislature promises only "Be notified of scheduling changes for hearings that you are following"; June 2025 rules move hearing notice from 72 hours to 10 days. Regulations.gov: "dockets are difficult to locate… confusing, difficult to navigate, and in some instances completely nonfunctional" (Regulatory Review, 2022).

## 4. Look and feel
**Trustworthy:** GovTrack bill page prints "Source: Congress.gov", "Last Updated: July 9, 2025"; ads are labelled (`govtrack-bill-desktop.png`). Regulations.gov docket: Docket ID, Subscribe, summary; 3.7 s (`regsgov-docket-desktop.png`). malegislature.gov bill: dated action table, text/PDF, committee-vote tab, no summary; calendar shows Confirmed/Canceled; home has a weather widget; TTFB 1.8 s (`malegislature-bill-desktop.png`). AG decisions sit on a separate Hyland lookup, 9.5 s (`ag-mlu-decisions-db-desktop.png`). MassDEP ePLACE is 2017 clip art with mobile overflow; the Data Portal loads in 11 s (`massdep-wetlands-portal-desktop.png`).

**Sales page:** Quorum "Agentic Intelligence. One platform. Total policy control.", six "Request Pricing" buttons, chatbot panel, 235 requests, 11.3 s (`quorum-pricing-desktop.png`). FiscalNote: cookie modal over the hero, logo wall, 42 third-party hosts (`fiscalnote-home-desktop.png`). FastDemocracy: "Trusted by 600+", three demo buttons (`fastdemocracy-home-desktop.png`). Plural's bill page is a real reader but Track needs an account (`openstates-bill-desktop.png`).

**Agenda Ahead:** 6 requests, 0 third-party, 3–3.7 s; "New" badges, "confirm dates with the town clerk" (`aa-home-desktop.png`). Meeting page: room, time, cable channel, PDF, "Before this" history (`aa-meeting-desktop.png`). /watch: town first, "No account needed". /upcoming is 40,410 px tall. One /ma/carver load hung 30 s (rerun 3.4 s). Mobile nav wraps "Get alerts" (`aa-carver-mobile.png`).

**They have, we don't:** per-item source and "last updated" stamp (GovTrack, Regulations.gov); tunable alerts and starring (FastDemocracy, FiscalNote); comment deadlines; full text inline (Plural); committee votes (malegislature). **We have, they don't:** value before any account, zero trackers, plain-English write-ups, cross-meeting history, a glossary, AG rulings joined to towns, Slack/Teams delivery.

## 5. Implications for Agenda Ahead
1. Stamp every item: "From Carver Planning Board agenda PDF, posted Oct 14, read Oct 16" ("direct link" praise).
2. On /watch add topic choice, daily-vs-weekly, and a "most important" line atop each email (noise complaints).
3. Add "not posted yet" and "last checked" per town and a short "what we can miss" note (late-data complaints).
4. Give each project one permanent URL across hearings (Federal Pond Solar spans Sep 2–Nov 4), like a docket ID.
5. Say "no account, no trackers, no ads" on How it works; no other site studied can.
6. Pre-render town pages; a 30 s stall is what reviewers remember ("it is sometimes slow", FiscalNote).
7. Print any price and cancellation terms for group alerts; opaque pricing and 60-day notice drew the angriest reviews.

## 6. Sources
https://www.capterra.com/p/169973/Quorum/reviews/ · https://www.capterra.com/p/185611/FiscalNote/reviews/ · https://www.softwareadvice.com/government/quorum-profile/ · https://www.g2.com/products/fastdemocracy/reviews_and_filters · https://tr-web.dev.trustradius.com/products/fiscalnote/reviews/all · https://www.billtrack50.com/info/pricing · https://www.billtrack50.com/info/testimonials · https://apps.apple.com/us/app/billtrack50/id1315336133 · https://pluralpolicy.com/pricing · https://legiscan.com/gaits/upgrade · https://info.legistorm.com/blog/best-public-affairs-software · https://www.govtrack.us/about-our-data · https://news.ycombinator.com/item?id=44202110 · https://news.ycombinator.com/item?id=2839137 · https://news.ycombinator.com/item?id=4231085 · https://news.ycombinator.com/item?id=9892301 · https://www.reddit.com/r/50501/comments/1ohhna0/ · https://www.reddit.com/r/Austin/comments/1r7jcn4/anyone_have_a_good_nonpaywalled_voters_guides/o61288d/ · https://www.reddit.com/r/LawFirm/comments/1k582ix/how_do_you_track_mediastate_law_changes/ · https://www.reddit.com/r/massachusetts/comments/1pazmtk/ · https://github.com/openstates/issues/issues?q=is%3Aissue+massachusetts · https://pluralpolicy.com/blog/openstates-december-2023/ · https://sunlightfoundation.com/2010/10/16/the-price-of-access/ · https://washingtonian.com/2011/04/04/is-bloomberg-government-the-next-washington-media-death-star/ · https://digiday.com/media/4-priciest-content-subscriptions-stack · https://mediabiasfactcheck.com/ballotpedia/ · https://www.mass.gov/news/audit-refused-by-legislature-highlights-lack-of-transparency-and-accountability · https://www.commoncause.org/?p=13640 · https://malegislature.gov/MyLegislature/About · https://www.massaudubon.org/take-action/advocate/action-center/massachusetts-state-legislature-website-101 · https://karenspilka.com/updates/factsheet-jointrules · https://www.mass.gov/info-details/about-the-municipal-law-unit · https://www.mass.gov/info-details/state-agency-decisions-and-opinions · https://massago.hylandcloud.com/203publicaccess/mlu.htm · https://www.mass.gov/info-details/wetland-notices-of-intent-lookup · https://eeaonline.eea.state.ma.us/EEA/PublicApp/ · https://eeaonline.eea.state.ma.us/portal#!/search/wetland · https://www.theregreview.org/2022/03/17/spence-thurston-regulatory-engagement-is-due-for-an-upgrade/ · https://www.gao.gov/products/gao-20-383r · https://www.regulations.gov/docket/EPA-HQ-OAR-2021-0317 · https://www.federalregister.gov/api/v1/documents.json?conditions[term]=solar · https://agendaahead.vercel.app/ (home, /ma/carver, /m/carver-conservation-commission-2026-10-21, /upcoming, /attorney-general, /watch)
