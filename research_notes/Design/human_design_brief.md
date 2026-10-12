# Agenda Ahead: design brief for humans

2026-10-12. From Playwright screenshots of https://agendaahead.vercel.app (1440 and 390 px) and the sources below [n].

**The job:** someone types their town and, within 10 seconds, sees what's coming up and how to be told next time.

## 1. Rules

1. **Open with one question: "What town?"** *Why:* GOV.UK, Zillow and Our World in Data all do, and people expect that (Jakob's law) [15][43].
2. **One primary action per screen: "Get free alerts".** *Why:* more choices mean slower decisions (Hick's law) [15][4].
3. **Lead each item with a plain sentence, with the agenda text behind a click.** *Why:* the first words decide the click (information scent) [5][18].
4. **Reading age 9 to 12, 20 words a sentence at most, no unexplained acronyms (BESS, 40B, CMR).** *Why:* experts prefer plain language too [19][20][23].
5. **The answer goes above the fold, in 60 words or fewer. The whole home page stays under 400.** *Why:* people read 20 to 28% of a page, and 57% of viewing time is spent on the first screen [8][9][14].
6. **Show the next three things, and keep the rest one click away, two levels at most.** *Why:* progressive disclosure [4].
7. **Body text 18 px on phones (16 px at least), lines of 50 to 75 characters, 5 type sizes at most.** *Why:* small, light text is the top complaint of older users [10][11][29][16].
8. **Tap targets 44 px or larger.** *Why:* Apple's guideline. WCAG's floor is 24 px, and small targets are slow (Fitts's law) [13][12][15].
9. **Four visible top-level links at most.** *Why:* people use hidden navigation less [31][32].
10. **Red only for "hearing soon" or a deadline, and contrast of 4.5:1 or more.** *Why:* colour should carry meaning, never alone [16][35].
11. **Email is the default alert. Calendar, RSS, Slack and Teams go under "Other ways".** *Why:* older residents live in email [4][10].
12. **Alert setup asks one thing per page, with no account.** *Why:* people who lack confidence, and phone users, do better [21].
13. **A compact list view for professionals, as a toggle.** *Why:* density works when rows are uniform, as on HN, Craigslist and Linear [34][43].
14. **Show the source quietly: "Source: Planning Board agenda, p. 3".** *Why:* honest, and as little design as possible (Rams) [17].

**What to borrow:**
- **Our World in Data:** one grey line ("14,088 charts across 126 topics. All free.") instead of a stat block [43].
- **Airbnb:** asks Where, then When.
- **ZoLa:** an address box, but no pop-up on arrival.
- **Stripe:** status colours with predictable contrast [35].
- **Basecamp:** copy is interface [28].
- **Kennedy:** design in greyscale first [33].
- **Ive:** simplicity is clear purpose, not just less clutter [36].

## 2. Wording guide

| Screen | Don't | Do |
|---|---|---|
| Home headline | Siting items on town board agendas | See what your town is about to decide |
| Home box | Town, board, keyword | Enter your town or ZIP code |
| Button | Create a watchlist | Get free alerts |
| Trust line | 312 / 1,169 / 164 / 5 days (stat block) | Free. 312 towns in MA, NY and RI. Every item links to its agenda. |
| Item | "in Highway Overlay Type C setback from 115 feet to 10.3 feet for … BESS equipment" | **Battery storage project asks to cut its required setback from 115 ft to 10.3 ft.** Clay, NY · Zoning Board of Appeals · Mon Oct 12 |
| Item meta | First seen the day before the meeting (red) | Posted 1 day before the meeting (grey) · "You can speak at this hearing" when it is one |
| Town page | Boards we read · Last successful crawl | Coming up in Amherst |
| Alert setup | Slack, Teams or Discord webhook URL | Your email address |
| Empty | 0 items | Nothing on these topics right now. We check every day. |
| Search | No results | Nothing mentions "lithium" in Hadley since June. Try "battery", or all of MA. |
| Error | Invalid input | That email is missing an @. |
| Email subject | 351 Watch: 3 new items for watchlist | Swansea, Tue Oct 13: solar and battery project near wetlands |
| Navigation | Tracker · AG decisions · Coverage | Towns · Topics · Search · Get alerts |

Buttons: verb plus noun [25]. Errors: next to the field, with the fix [26]. Empty states: say what to do next [27]. Tone: calm, never cute [24].

## 3. Layout spec (390 px first)

**Home.**
- *Above the fold:* header (Agenda Ahead · Get alerts); a one-line headline; the town/ZIP box with "Use my location"; the trust line; 2 "Coming up near you" items.
- *Below:* 5 more items; topic links; "How it works" in 3 steps; the footer.
- *Moved off home:* stats, tracker table, law timeline and AG decisions, each to its own page linked from the footer.

**Town page.**
- *Above the fold:* the town name; "Next meeting: Conservation Commission, Wed Oct 14"; a full-width "Get alerts for Amherst" button; the first item card (summary, board, date, how to take part).
- *Below:* the other upcoming items; "Earlier this year" (collapsed after 5, no duplicates); "Towns next door" with counts.
- *Behind a click:* the agenda text, and "How we get these agendas", which holds the crawl table.

**Alert setup**, one question per screen:
1. "Which town?" (prefilled from a town page; link: "Watching many towns? Add a county or paste a list.")
2. "Also watch the towns next door?" Already ticked. Topics: all, with "Choose topics" as a link.
3. "Where should we send alerts?" An email field and "Get alerts".
4. Confirmation: what happens next, a sample alert, "Add meetings to my calendar", how to stop.

**Search results.**
- *Above the fold:* the box (keeps the query); one row of chips (Place, Topic, Upcoming/Past); a count in words ("23 upcoming items mention 'data center'"); then rows sorted by soonest meeting, each with a bold summary, town · board · date, and one excerpt line with the match highlighted. "Get alerts for this search" sits top right.
- *Behind a click:* more filters, compact view, CSV/RSS export.

## 4. The 8 biggest problems on the live site

| # | Problem | Fix |
|---|---|---|
| 1 | No town box. The H1 is jargon ("Siting items…"), then a 55-word paragraph. | Town box and plain headline first (rules 1, 4). |
| 2 | Home page: 5,051 words, 181 links, about 32 phone screens tall (26,951 px). | 400 words at most. The tracker, laws and AG decisions get their own pages. |
| 3 | Items are raw, cut-off agenda text ("BOARD OLUTION NO. 70-: WHEREAS…", BESS, 225 CMR). | One plain summary sentence. Raw text behind "Show agenda text". |
| 4 | /watch: 467 town checkboxes, a webhook field, no email, no neighbors. | The 3-step email flow. |
| 5 | The town page opens with crawl status. On a phone no item is visible, and "Recent" repeats items. | Next meeting and items first, crawl data behind a link, duplicates removed. |
| 6 | No search across agendas (/search returns 404). | The search results page above, linked in the navigation. |
| 7 | Most text is 12.8 to 15 px. 104 of the 189 tappable elements at 390 px are under 24 px. Red marks neutral facts. | Rules 7, 8, 10. |
| 8 | Wrong name and insider words: the page says "351 Watch", the canonical URL points to another domain, and labels read "Tracker", "AG decisions", "Coverage", "40B". | "Agenda Ahead" everywhere, plain navigation. |

## 5. Test plan

**Every build (Playwright at 390 and 1440 px):** home under 400 words and 5 screens; no horizontal scroll; text 16 px or more; targets 44 px or more; axe-core 0 serious issues; Lighthouse accessibility 95 or more; summaries at grade 8 or below.

**Task tests** (5 people per audience finds most problems [38]):

| Task | Pass |
|---|---|
| "Is anything about solar or batteries coming up in your town?" | 4 of 5, within 60 s |
| "Get email alerts for your town and its neighbors." | 4 of 5, within 2 min, 4 screens at most |
| "Get alerts for upcoming data-center items in Worcester County." | 4 of 5, within 3 min |
| "Which towns vote on a moratorium in the next 2 weeks? Open one agenda." | 4 of 5, within 3 min |
| "Stop these alerts" (from the email) | 5 of 5 |

- **First click:** 80% or more correct. A correct first click predicts success, 87% against 46% [40].
- **SUS:** 80 or higher (an A); the average is 68 [41].

**5-second test.** Show the home page at 390 px for 5 seconds, then ask what it is for, who it is for, and what they would do first. Pass: 80% describe upcoming items on their town's agendas, and 80% would enter a town or get alerts [39].

**Synthetic first-time visitor panel** (run before real people):
- *Setup:* 3 personas × 3 fresh evaluators. Each gets only a screenshot and a persona card, with no code, no other answers, and no label for which version is new.
  - **Margaret, 68.** Hadley, iPhone set to large text. Worried about a battery project near her road. Not technical.
  - **Dev, 41.** Solar permitting manager tracking 60 towns. Lives in Slack.
  - **Priya, 29.** Regional reporter covering 15 towns. Needs leads and source documents.
- *Questions:* What is this site for? Who is it for? Where would you tap first to [task]? List every confusing word. Would you use it (1 to 5)? Then walk each task screen by screen: "where next?"
- *Pass:* 8 of 9 state the purpose (town + upcoming meetings + before the decision); 8 of 9 pick the intended first tap; Margaret's evaluators name no jargon; every score beats the current site, run as the baseline.
- *Limits:*
  - AI evaluators agree too easily and score too kindly [42].
  - They read tiny text perfectly, never miss a tap, never tire of scrolling, and share blind spots.
  - It checks comprehension, not usability. Confirm with 5 real residents (library, council on aging) before launch, and never report it as user research [42].

---

## Sources

1. NN/g, 10 Usability Heuristics. https://www.nngroup.com/articles/ten-usability-heuristics/
2. NN/g, F-Shaped Pattern of Reading. https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
3. NN/g, The Layer-Cake Pattern of Scanning. https://www.nngroup.com/articles/layer-cake-pattern-scanning/
4. NN/g, Progressive Disclosure. https://www.nngroup.com/articles/progressive-disclosure/
5. NN/g, Information Scent (Budiu, 2020). https://www.nngroup.com/articles/information-scent/
6. NN/g, Minimize Cognitive Load. https://www.nngroup.com/articles/minimize-cognitive-load/
7. NN/g, Aesthetic and Minimalist Design. https://www.nngroup.com/articles/aesthetic-minimalist-design/
8. NN/g, How Little Do Users Read? (20 to 28%; half only at 111 words or fewer). https://www.nngroup.com/articles/how-little-do-users-read/
9. NN/g, Scrolling and Attention (57% above the fold, 74% in the first two screens, 2018). https://www.nngroup.com/articles/scrolling-and-attention/
10. NN/g, Usability for Seniors (123 participants aged 65+, 2001 to 2019). https://www.nngroup.com/articles/usability-for-senior-citizens/
11. W3C WAI, Older Users and Web Accessibility. https://www.w3.org/WAI/older-users/
12. W3C, Understanding WCAG 2.2 SC 2.5.8 Target Size (Minimum), 24x24 px. https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
13. Apple Human Interface Guidelines, Accessibility (44x44 pt hit targets). https://developer.apple.com/design/human-interface-guidelines/accessibility
14. Steve Krug, Don't Make Me Think (trunk test; "get rid of half the words on each page, then get rid of half of what's left"). https://sensible.com/dont-make-me-think/
15. Jon Yablonski, Laws of UX (Hick's, Jakob's, Miller's and Fitts's laws, aesthetic-usability effect). https://lawsofux.com/
16. Wathan and Schoger, Refactoring UI ("Hierarchy is everything", "Labels are a last resort", "Establish a type scale", "Don't rely on color alone"). https://www.refactoringui.com/
17. Dieter Rams, Ten principles of good design (Vitsoe). https://www.vitsoe.com/us/about/good-design
18. GOV.UK, Create a clear structure (front-loading; users read 20 to 28%). https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-structure/
19. GOV.UK, Use clear language (split sentences over 25 words; active voice). https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
20. GOV.UK, Writing for GOV.UK (reading age of 9; now redirects into the publishing guidance). https://www.gov.uk/guidance/content-design/writing-for-gov-uk
21. GOV.UK, One thing per page (Tim Paul, 2015) and the Question pages pattern. https://designnotes.blog.gov.uk/2015/07/03/one-thing-per-page/ ; https://design-system.service.gov.uk/patterns/question-pages/
22. Digital.gov, Plain language guide series (formerly plainlanguage.gov). https://digital.gov/guides/plain-language
23. NN/g, Plain Language Is for Everyone, Even Experts (2017). https://www.nngroup.com/articles/plain-language-experts/
24. Mailchimp Content Style Guide, Voice and Tone. https://styleguide.mailchimp.com/voice-and-tone/
25. Shopify Polaris, Common actions (verb + noun labels). https://polaris.shopify.com/patterns/common-actions/best-practices
26. NN/g, Error-Message Guidelines. https://www.nngroup.com/articles/error-message-guidelines/
27. NN/g, Designing Empty States. https://www.nngroup.com/articles/empty-state-interface-design/
28. 37signals, Getting Real: Copywriting is interface design. https://basecamp.com/gettingreal/09.7-copywriting-is-interface-design
29. Baymard Institute, Readability: The Optimal Line Length (50 to 75 characters). https://baymard.com/blog/line-length-readability
30. NN/g, Cards: UI-Component Definition. https://www.nngroup.com/articles/cards-component/
31. NN/g, How to Make Navigation (Even a Hamburger) Discoverable on Mobile (2016). https://www.nngroup.com/articles/find-navigation-mobile-even-hamburger/
32. Luke Wroblewski, Obvious Always Wins (2015); Mobile First. https://www.lukew.com/ff/entry.asp?1945 ; https://www.lukew.com/resources/mobile_first.asp
33. Erik Kennedy, 7 Rules for Creating Gorgeous UI. https://www.learnui.design/blog/7-rules-for-creating-gorgeous-ui-part-1.html
34. Linear, How we redesigned the Linear UI (2024). https://linear.app/now/how-we-redesigned-the-linear-ui
35. Stripe, Designing accessible color systems (2019). https://stripe.com/blog/accessible-color-systems
36. Jony Ive on simplicity (2012 Telegraph interview, as reported by TechRadar). https://www.techradar.com/news/computing/apple/ive-on-apple-s-quest-for-simplicity-1081643
37. Honest density: https://news.ycombinator.com/ and https://www.craigslist.org/ (uniform text rows, no decoration), observed 2026-10-12.
38. NN/g, Why You Only Need to Test with 5 Users. https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/
39. Lyssna, Five-second testing guide (5 to 8 questions, 5 to 10 people, about 80% understanding). https://www.lyssna.com/guides/five-second-testing/
40. MeasuringU, Getting the First Click Right (87% vs 46%; MeasuringU's later replications found smaller gaps). https://measuringu.com/first-click/
41. MeasuringU, Measuring Usability with the SUS (average 68; A is above 80.3). https://measuringu.com/sus/
42. NN/g, Synthetic Users: If, When, and How to Use AI-Generated "Research" (2024). https://www.nngroup.com/articles/synthetic-users/
43. Reference screens captured with Playwright at 390 px on 2026-10-12: https://www.gov.uk/ , https://www.zillow.com/ , https://ourworldindata.org/ , https://zola.planning.nyc.gov/ ; also observed: https://www.airbnb.com/ , https://news.ycombinator.com/ , https://www.craigslist.org/
44. Live-site audit: https://agendaahead.vercel.app (/, /ma/amherst, /watch, /towns, /topics, /pricing, /proof), screenshots and DOM measurements from Playwright and Chromium, 2026-10-12.
