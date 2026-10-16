# Local news and neighborhood alerts: what people like, what drives them off

Screenshots: `research/local-news/` (`-desk` 1366x900, `-phone` 390x844). Reddit and Nextdoor block generic crawlers, so neither was visited; Nextdoor evidence is from app stores, Capterra, HN and press. New Bedford Light, CommonWealth Beacon and Axios desktop showed bot walls.

## 1. Services studied

- **Patch**: staffed town sites plus "Patch AM" AI newsletters in ~14,000 towns; ads, sponsored posts.
- **Nextdoor**: address-verified feed; ads, business fees.
- **Citizen**: scanner-sourced crime alerts; Premium ~$20/mo.
- **Ring Neighbors**: safety feed inside Ring's app; sells cameras.
- **Front Porch Forum** (VT): one emailed digest a day, real names, staff read every post first; ads, donations.
- **NewsBreak**, **Google News**: aggregators; ads.
- **Axios Boston**, **6AM City/BOStoday**: sponsored daily newsletters; BOStoday skips politics.
- **Plymouth Independent, New Bedford Light, CommonWealth Beacon, Bedford Citizen**: free MA nonprofits, donor funded.
- **Universal Hub**: one-person Boston aggregator; ads, donations.

## 2. What people praise

**Finding one thing fast.** "it has allowed me to find my missing packages/ alert/ get help when my dog has went missing" (Capterra, Nextdoor). "Helped find my Adorable Lost cat" (App Store, Ring, 2026-05-10).

**Calm, slow, human.** "I've been amazed at the civilized tone in FPF" (HN, 2024-08-10). "This app doesn't do everything, but that's the point" (App Store, FPF, 2025-11-05). New_ Public's 13,000-member survey: 81% felt more informed on FPF vs 26% on Facebook, 32% on Nextdoor; 61% attended a meeting or event because of a post.

**Someone in the meeting room, free.** New Bedford Light: "Paywalls perpetuate inequity." Plymouth's Select Board vice chair: "I continue to see the value in having a professional relationship between the town and the Independent" (Globe, 2025).

## 3. What people complain about

**Fear and bickering.** "Noisy neighbors spread fear and paranoia" (BetaNews, 2018). "i removed myself after months of watching people on this app become more and more paranoid" (HN, 2022). "a good amount of them aren't even crimes. i once got a notification that someone was smoking near me" (App Store, Citizen, 2026-10-08).

**Notifications that will not stop.** "Over 130 clicks to disable email and push notifications?" (HN, Nextdoor, 2022). "It is impossible to unsubscribe from emails from the app" (App Store, Ring, 2026-03-11).

**Ads and paywalls on safety.** "Be ready to be spammed by ads for premium. If it were really about safety, they'd be less shameless" (Citizen, 2026-10-10). "Nearly every article is paywalled" (Google News, 2026-10-04). "It's just a cheesy advertising platform" (Trustpilot, Patch, 2025-10-31).

**Not local, or not true.** Patch's CEO: "'It's the wrong Springfield'—we hear that at least single-digit times a week" (CJR, 2026-03-05). After automation: "There's no longer a 'what's happening locally' feel to it" (Nieman Lab, 2025). NewsBreak's AI reported a shooting police called "entirely false" (Reuters, 2024).

**Opaque moderation.** "Every single one of my posts since May has been denied" (Ring, 2026-08-09).

## 4. Look and feel

- **Patch Plymouth** (`patch-plymouth-desk.png`, `-phone.png`): top 280px is a "$0 solar" ad, 9s load; the first "Plymouth Local News" item is a Reading, MA killing; sponsors, a "Brand Partner" item and the "Patch AM Team" byline share one list.
- **NewsBreak** (`newsbreak-plymouth-desk.png`): "Crime Map" in nav, cookie banner, Plymouth Independent stories beside "familyvacationsus.com".
- **Citizen** (`citizen-home-desk.png`): black, "Where people protect each other.", nav PREMIUM / JOURNALIST / ENTERPRISE.
- **Ring** (`ring-neighbors-desk.png`): "Be a hero in your neighborhood." under a camera banner and cookie bar.
- **Front Porch Forum** (`fpf-home-desk.png`): the home page is the sign-up form; plain.
- **Axios Boston** (`axios-boston-phone.png`): email box first, "Why it matters".
- **Plymouth Independent, Bedford Citizen, Universal Hub** (`plymouth-independent-desk.png`, `bedford-citizen-desk.png`, `universal-hub-desk.png`): nameplate, bylines, dates written out, Donate and newsletter box above the fold, sponsors labeled apart. Universal Hub: 58 iframes, 13s.
- **Agenda Ahead** (`aa-home-desk.png`, `aa-carver-phone.png`, `aa-upcoming-desk.png`, `aa-meeting-desk.png`, `aa-watch-phone.png`): one sentence, a town box, weekday/town/board/item rows with Hearing/Vote tags; no ads, iframes or banners; 4-5s. The meeting page gives the room and "Add to my calendar". But `/ma/carver` desktop timed out at 30s, the phone nav wraps "Get alerts" onto its own line, no page has an email field, and `/watch` says "Email alerts are coming."

## 5. Implications for Agenda Ahead

1. **Say "No ads, no comments, no account" on the home page.** Nearly every complaint above is about other users' posts, moderation or ads.
2. **Ship email; make "at most one a day, only when something is new, one click to stop" the first line of `/watch`.** Unstoppable notifications are the most repeated reason people quit.
3. **Put provenance on every item**: "From Carver's Oct 21 agenda, read Oct 16, PDF" plus "wrong town? tell us". That is the failure people now expect from automated local news.
4. **Keep the verbs neutral.** Hearing, Vote, Postponed read like FPF; "alert", "threat" read like Citizen.
5. **Make "how to speak at this meeting" a standard field**; 61% of FPF members attended a meeting because of a post.
6. **Fix the cold-start timeout and the wrapped phone nav.**
7. **Add one line of "why it matters"** per meeting, as Axios and the Independent do; bare agendas are what Patch AM scrapes.

## 6. Sources

- Apple App Store review feeds, read 2026-10-16, ids 640360962, 1218902777, 1039889567, 459182288, 1458651656
- https://play.google.com/store/apps/details?id=com.nextdoor (also sp0n.citizen, com.ring.neighborhoods, com.particlenews.newsbreak)
- https://www.capterra.com/p/207178/Nextdoor/reviews/, https://ca.trustpilot.com/review/patch.com
- https://news.ycombinator.com/item?id=31818074, ?id=41208506, ?id=26013184
- https://betanews.com/2018/10/17/goodbye-noisy-neighbors-i-quit-nextdoor/
- https://newpublic.substack.com/p/the-vermont-miracle-how-one-local
- https://www.niemanlab.org/2025/04/the-origins-of-patchs-big-ai-newsletter-experiment/, https://www.cjr.org/?p=118905
- https://news.slashdot.org/story/24/06/06/0157205/newsbreak-most-downloaded-us-news-app-caught-sharing-entirely-false-ai-generated-stories
- https://localnewsinitiative.northwestern.edu/posts/2024/12/12/massachusetts-local-news-startups-replace-ghost-papers/
- https://www.bostonglobe.com/2025/01/18/business/plymouth-independent-communications-ban-town-officials
- https://6amcity.com/, https://agendaahead.vercel.app/ (/ma/carver, /m/carver-select-board-2026-10-20, /upcoming, /attorney-general, /watch)
