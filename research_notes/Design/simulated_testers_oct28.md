# Agenda Ahead: eight simulated testers walk the live site

Written Oct 28, 2026, against https://agendaahead.vercel.app as it stood that afternoon (pages say "last checked Oct 28, 7:18 am"). The redesign spec is `research_notes/Design/human_first_spec.md`. No real people took part. Each tester is a profile built from published research, read first hand where the publisher let us in, and every behaviour a tester shows below is tied to a source. The walkthroughs ran in headless Chromium through Playwright, with the viewport, device scale and scroll budget each profile calls for. Screenshots and step logs are in `/tmp/claude-0/-home-user-sulmusic2-star/815cfdd0-e090-5147-aee8-a5db345f6b5d/scratchpad/design3/testers/`.

Three honesty notes before the findings.

1. Where a tester's evidence says they stop after two or three screenfuls, the walkthrough stops there too, and anything lower on the page counts as not seen. Where the evidence says they read everything, they do, and the log says how far down the answer was.
2. The 200% zoom tester runs at a 195 by 422 CSS-pixel viewport at 4x device scale. That is what Safari's Page Zoom or Chrome's zoom does to a 390-pixel phone at 200%: it halves the layout width. A separate 320-pixel run checks the WCAG reflow line.
3. We did not press the final "Follow these towns" button, to avoid creating alerts on the owner's server. What the next step shows is read from the page's own hidden markup and said so.

Sources that blocked us are listed at the end of Part 1.

---

## Part 1. The evidence base

### A. Who looks at town-government information

**A1. Pew Research Center, "Consumption and sources of local political news" (Jul 24, 2024; survey of 5,146 adults, Jan 2024).** 68% of U.S. adults at least sometimes get news about local government and politics. By source: local news outlets 66%, social media 54%, local government websites 32%, local politicians directly 30%. Age gap: 81% of adults 65 and older get local political news at least sometimes (34% often); 56% of adults 18 to 29 do (12% often). 71% of 18 to 29 use social media for it; 36% of 65 and older do. 75% of 65 and older use local outlets; 53% of under-30s do. "Older adults also are more likely to get local political news directly from local politicians."
https://www.pewresearch.org/journalism/2024/07/24/consumption-and-sources-of-local-political-news/

**A2. Pew, Local News Fact Sheet (survey Dec 8 to 14, 2025).** "In 2025, 21% of Americans say they follow local news very closely, down from 37% in 2016." By age: 15% of 18 to 29, 17% of 30 to 49, 23% of 50 to 64, 32% of 65 and older. 40% often or sometimes get local news from "local government agencies or officials, such as city council offices or libraries" (35% in 2024, 30% in 2018). Preferred pathway: television 34%, news website or app 28%, social media 20%, print newspaper 8%.
https://www.pewresearch.org/journalism/fact-sheet/local-news-fact-sheet/

**A3. Pew, engagement topline (report Jul 2026; fieldwork Jul 9 to Dec 5, 2025, 5,393 adults).** "Attended a city council or school board meeting, either in person or online" in the past 12 months: 13% yes, 86% no. A Sept 8 to 14, 2025 wave of the same question: 14% yes. Read from the PDF with pdftotext.
https://www.pewresearch.org/wp-content/uploads/sites/20/2026/07/PJ_26.07.16_engagement_topline.pdf

**A4. Pew, Mobile Fact Sheet (survey Jan 30 to Jun 18, 2026, 5,511 adults).** 16% of adults are "smartphone-only" internet users (a smartphone, no home broadband). By age: 18 to 29 24%, 30 to 49 14%, 50 to 64 12%, 65 and older 16%. By income: under $30,000 29%, $100,000 and over 7%. By community: urban 20%, suburban 11%, rural 20%. 79% of adults 65 and older own a smartphone.
https://www.pewresearch.org/internet/fact-sheet/mobile/

**A5. Knight Foundation with Gallup, "State of Public Trust in Local News" (Oct 29, 2019).** Americans "give local news organizations stronger ratings than national organizations across most trust dimensions"; the report reads this as "more a sign of skepticism toward national media than of enthusiasm toward local news." Only the summary page was readable; the full PDF was not opened.
https://knightfoundation.org/reports/state-of-public-trust-in-local-news/

**A6. Harvard Ash Center, Allen Lab, "The Landscape of Digital Civic Infrastructure in Massachusetts" (Hubbard, Sun, Goux, Miller, Riveros Garcia, Allen; file dated Aug 2026).** Takeaway 2: "Municipal Websites Prioritize Transactional Features over Transparency Features." "Of the municipal websites evaluated, 98 percent supported online payments, yet the user experience of accessing how money is spent by the municipality was considerably more difficult." "Almost every municipality posted their meeting minutes online with a PDF; however, nearly 25 percent of these were not searchable." "Over 83 percent of municipal budgets were shared as PDFs." Takeaway 5: "Budget and Staffing Technical Resources Pose a Huge Constraint for Many Municipalities." Takeaway 6: "Hybrid Meetings Often Fail to Enable Two-Way Participation." Of municipalities evaluated, "97 percent had an official municipal Facebook page and 100 percent had a community-run Facebook group." Read from the PDF with pdftotext.
https://ash.harvard.edu/wp-content/uploads/2026/08/Harvard-Allen-Lab-The-Landscape-of-Digital-Civic-Infrastructure-in-Massachusetts.pdf

**A7. Massachusetts Open Meeting Law, G.L. c. 30A, s. 20.** A public body "shall post notice of every meeting at least 48 hours prior to the meeting, excluding Saturdays, Sundays and legal holidays." For local bodies the notice is filed with the municipal clerk and posted "in a manner conspicuously visible to the public at all hours in or on the municipal building in which the clerk's office is located." The notice must carry "a listing of topics that the chair reasonably anticipates will be discussed at the meeting."
https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIII/Chapter30A/Section20

**A8. Massachusetts Zoning Act, G.L. c. 40A, s. 11 (abutter notice).** Notice of a zoning hearing goes "by publication in a newspaper of general circulation in the city or town once in each of two successive weeks," the first at least 14 days before the hearing, by "posting such notice in a conspicuous place in the city or town hall," and by mail to "parties in interest," which include the petitioner, abutters, owners across the street, the planning board, and "abutters to the abutters within three hundred feet of the property line of the petitioner."
https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40A/Section11

**A9. Lawrence Berkeley National Laboratory developer survey (Nilson, Hoen, Rand; Jan 2024), read through Inside Climate News, Feb 23, 2024.** 123 developers from 62 companies, responsible for about half of U.S. large wind and solar built 2016 to 2023. About one third of applications were canceled because of community opposition and about half were delayed six months or more. For both wind and solar, "community opposition and restrictive local ordinances or zoning were among the top three reasons for delays and cancellations." "For both wind and solar, opposition is becoming more prevalent and is more expensive to address than it was five years ago." Average sunk cost of a canceled solar project about $2 million. The LBL pages themselves returned 403 twice.
https://insideclimatenews.org/news/23022024/community-opposition-and-grid-challenges-slow-pace-of-renewable-efforts/

**A10. Pew, survey of U.S. journalists (Jun 14, 2022; 11,889 journalists, Feb 16 to Mar 17, 2022).** "94% of journalists surveyed report using social media in their work to some degree." 30% say their organization has been expanding, 22% cutting back.
https://www.pewresearch.org/journalism/2022/06/14/journalists-sense-turmoil-in-their-industry-amid-continued-passion-for-their-work/

**A11. Medill Local News Initiative, "State of Local News 2025."** Local news deserts are "now 213 counties." The summary page gives no state figures and nothing on weekly staffing; the full report was not opened.
https://localnewsinitiative.northwestern.edu/projects/state-of-local-news/2025/

**A12. National Association of Realtors, 2024 Technology Survey (PDF read with pdftotext).** "These technology tools used in their businesses were very impactful: eSignature (81 percent), lockbox/showing tech (63 percent), and transaction management (50 percent)." "Eighty-seven percent of respondents use Facebook in their real estate business." Top lead source: social media (52 percent). The survey has no figure on daily phone use, so phone habits for the agent profile come from A4 and B9 instead.
https://www.nar.realtor/sites/default/files/documents/2024-technology-survey-report-08-08-2024.pdf

**A13. Pew, "Parenting Children in the Age of Screens" (Jul 28, 2020; 3,640 parents, Mar 2 to 15, 2020).** 68% of parents say they at least sometimes feel distracted by their phone when spending time with their kids (17% often); 56% say they spend too much time on their smartphone; 66% say parenting is harder than 20 years ago.
https://www.pewresearch.org/internet/2020/07/28/parenting-children-in-the-age-of-screens/

**A14. MassINC and UMass study of limited English proficiency, reported Jul 29, 2024.** Roughly 480,000 working-age Massachusetts adults have limited English, "one-tenth" of the workforce, from 2022 Census data; the authors say the true figure is probably higher.
https://thenationaldesk.com/news/americas-news-now/one-tenth-of-massachusetts-workforce-has-limited-english-speaking-skills-report-says-institute-for-a-new-commonwealth-and-the-university-of-massachusetts-found-migration-immigrants-maura-healey-governor-kim-driscoll-boston-new-england-border

**A15. Massachusetts Broadband Institute, Statewide Digital Equity Plan slides (Pioneer Valley listening session deck, Sept 2023; PDF read with pdftotext).** Statewide, "households with no computer (laptop or desktop)": 68K (24%) and 43K (15%, "neither device nor access"); "households with no broadband internet subscriptions": 79K (28%), source U.S. Census Bureau. The deck's preliminary survey counted 656 responses from "residents in rural areas," 398 from "aging individuals."
https://broadband.masstech.org/sites/default/files/2023-09/Pioneer%20Valley_LS_Deck.pdf

**A16. Town age profiles.** The Census Bureau API refused our calls (it now needs a key) and QuickFacts returned 403, so town ages come from Wikipedia's census summaries: Somerset, MA, 2020 census: population 18,303, "The median age was 47 years," "24.8% who were 65 years of age or older." Plympton's Wikipedia age figures are from 2000 (median 38) and are not used. Tester ages below are invented within these ranges, and nothing in the findings depends on them.
https://en.wikipedia.org/wiki/Somerset,_Massachusetts

**Not found.** Two searches each for a MassINC Polling Group poll or a Massachusetts Municipal Association survey on how residents get town information turned up nothing on that subject; A6 is the Massachusetts-specific source used instead.

### B. How such people behave on websites

**B1. NN/g, "F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile)" (Pernice, Nov 12, 2017).** "The F-pattern is the default pattern when there are no strong cues to attract the eyes towards meaningful information." "First lines of text on a page receive more gazes than subsequent lines." "First few words on the left of each line of text receive more fixations than subsequent words on the same line." "Users may skip important content simply because it appears on the right side of the page." Advice: the most important points in the first two paragraphs; headings that start with the words carrying most information.
https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/

**B2. NN/g, "First 2 Words: A Signal for the Scanning Eye" (Nielsen, Apr 6, 2009; 80 people).** "Users typically see about 2 words for most list items." Links should "front-load user- and action-oriented terms" and let users "confidently predict what they'll get if they click."
https://www.nngroup.com/articles/first-2-words-a-signal-for-scanning/

**B3. NN/g, "Scrolling and Attention" (Fessenden, Apr 15, 2018; 130,000 fixations).** "Users spent about 57% of their page-viewing time above the fold." "74% of the viewing time was spent in the first two screenfuls." "People still don't scroll a lot; they rarely go beyond the third screenful of info." "Reserve the top of the page for high-priority content."
https://www.nngroup.com/articles/scrolling-and-attention/

**B4. NN/g, "How People Read Online: New and Old Findings" (Moran, Apr 5, 2020).** "People still primarily scan, rather than read." "Scanning all of the text on a page, or even a majority, is still extremely rare." Advice: "clear, noticeable headings" and "placing information up front."
https://www.nngroup.com/articles/how-people-read-online/

**B5. NN/g, "Lower-Literacy Users: Writing for a Broad Consumer Audience" (Nielsen, Mar 13, 2005).** "Lower-literacy users focus exclusively on each word and slowly move their eyes across each line of text." "This gives them a narrow field of view and they therefore miss objects outside the main flow of the text." "As soon as text becomes too dense, lower-literacy users start skipping, usually looking for the next link." "Having to scroll breaks lower-literacy users' visual concentration." They "often have difficulty spelling the query terms" and "often simply pick the first hit on the list." Target a 6th-grade level for home and landing pages, 8th for others.
https://www.nngroup.com/articles/writing-for-lower-literacy-users/

**B6. NN/g, "Usability for Senior Citizens: Improved, But Still Lacking" (Nielsen, May 28, 2013).** Seniors (65 and older) took 43% longer than users 21 to 55 (7:49 vs 5:28). Task success 55.3% vs 74.5%. Errors 2.4 vs 1.1 per task. Seniors blamed themselves "90% of the time" (58% for younger users). "Almost twice as likely to give up on a task." 95% rated methodical (35% of younger users). 45% showed "discomfort with trying new things or reluctance to explore." Younger users were twice as likely to try site search or help. Error messages failed through "unclear wording or poor placement."
https://www.nngroup.com/articles/usability-seniors-improvements/

**B7. NN/g, "Usability for Older Adults: Challenges and Changes" (Kane, Sep 8, 2019; 123 participants 65 and older, studies 2001, 2013, 2018 to 19).** "Older users make more mistakes than younger users do." Interface text "too small and too lightly colored"; "buttons, dropdowns, and links are often too small." Sites that accept input "in only one format" frustrated them. Ability to use websites declined "by 0.8% per year between ages 25 and 60" in the middle-aged study.
https://www.nngroup.com/articles/usability-for-senior-citizens/

**B8. NN/g, "Mobile Content Is Twice as Difficult" (Nielsen, Feb 27, 2011, with 2016 note).** Comprehension of privacy-policy text: desktop 39.18%, iPhone-size screen 18.93%. The 2016 update: "readers can understand short, simple text content on mobile devices just as well as on computers," but difficult text slows them on mobile.
https://www.nngroup.com/articles/mobile-content-is-twice-as-difficult-2011/

**B9. NN/g, "Mobile User Experience: Limitations and Strengths" (Budiu, Apr 19, 2015).** "The average mobile session duration is 72 seconds" (desktop about 150). "We are more likely to be interrupted when using such devices." "Because attention is fragmented, strive to show users what they need as soon as possible." "The gist should always come before the minutiae."
https://www.nngroup.com/articles/mobile-ux/

**B10. NN/g, "Hamburger Menus and Hidden Navigation Hurt UX Metrics" (Pernice and Budiu, Jun 26, 2016).** Hidden menus were used in 27% of cases on desktop and 57% on mobile; "content discoverability was significantly lower when the navigation was hidden," a drop of more than 20%.
https://www.nngroup.com/articles/hamburger-menus/

**B11. NN/g, "PDF: Still Unfit for Human Consumption, 20 Years Later" (Nielsen and Kaley, Aug 9, 2020).** On mobile, users must "pinch, zoom, squint, and scroll around out of context to navigate a PDF." Offer an HTML gateway page that summarizes and links the PDF as a download.
https://www.nngroup.com/articles/pdf-unfit-for-human-consumption/

**B12. NN/g, "Plain Language Is for Everyone, Even Experts" (Loranger, Oct 8, 2017).** "Highly educated online readers crave succinct information that is easy to scan." "Being direct and plainspoken is not talking down. It is clear communication."
https://www.nngroup.com/articles/plain-language-experts/

**B13. NN/g, "Accordions on Mobile" (Budiu, May 31, 2015).** "On mobile, accordions are one of the most useful design elements," but "accordions can also increase user disorientation" and "a good webpage announces what it is about."
https://www.nngroup.com/articles/mobile-accordions/

**B14. NN/g, "Placeholders in Form Fields Are Harmful" (Sherwin, May 11, 2014).** "Disappearing placeholder text strains users' short-term memory." "Some users assume the placeholder text is a default value and skip the field completely." "Not all screen readers read placeholder text aloud."
https://www.nngroup.com/articles/form-design-placeholders/

**B15. Baymard Institute, "Mobile: Always Provide a Search Submit Button" (Collins, Jun 1, 2021).** Users "won't always look towards the touch keyboard to submit their search queries" and reach for a submit button to the right of the field "whether it's there or not." 21% of benchmarked mobile sites lack one.
https://baymard.com/research-articles/mobile-search-submit-button

**B16. GOV.UK content guidance, "Use clear language."** "Try to split up sentences that are over 25 words long." "Plain English is mandatory for all of GOV.UK." "1 in 6 adults in England have very poor literacy skills." "There will also be some users who do not have English as their first language." "Research shows that people with higher levels of literacy prefer plain English." "Some users can understand complex specialist language, but they do not want to read it if there's an alternative." "Explain the term in plain English when you first use it." The current page states no reading-age target; the old "reading age of 9" figure survives on council sites that restate GOV.UK's standard, for example Surrey County Council: "We aim for our pages to have a reading age of 9 years old. This matches GOV.UK's content design guidance standard."
https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
https://www.surreycc.gov.uk/website/writing-guide/reading-levels-for-web-pages

**B17. GOV.UK Service Manual, "Form structure" (updated Aug 7, 2018).** "Start with one thing per page": "one piece of information you're telling a user," "one decision they have to make," "one question they have to answer." It helps people "understand what you're asking them to do," "focus on the specific question and its answer," "use the service on a mobile device," and "recover easily from form errors."
https://www.gov.uk/service-manual/design/form-structure

**B18. NCES, PIAAC 2023 national results.** The share of U.S. adults 16 to 65 at Level 1 or below in literacy "increased from 19 to 28 percent" between 2017 and 2023. "Level 1 or below is a score lower than 226."
https://nces.ed.gov/surveys/piaac/2023/national_results.asp

**B19. CDC PLACES, disability measures (2022 data).** "Cognition was the most prevalent disability type reported (13.9%)"; mobility 12.2%; independent living 7.7%; hearing 6.2%; vision 5.5%; self-care 3.6%; about 1 in 4 adults report at least one.
https://www.cdc.gov/places/measure-definitions/disability/

**B20. WebAIM, Screen Reader User Survey #10 (Dec 2023 to Jan 2024, 1,539 responses).** "91.3% of respondents report using a screen reader on a mobile device"; VoiceOver 70.6%. First step on a long page: "navigating through headings" 71.6%. Most problematic items after CAPTCHA: "interactive elements that don't behave as expected," "links or buttons that don't make sense," "screens that change unexpectedly." Low vision 19.9% of respondents.
https://webaim.org/projects/screenreadersurvey10/

**B21. WebAIM, Survey of Users with Low Vision #2 (Sept 2018, 248 responses).** 44.0% use browser zoom; 48.4% use screen magnification. Typical magnification: under 200% 30.7%; 200 to 400% 29.7%; 400% or more 17.9%. 14.8% "often stop reading because text is hard to read comfortably every day," 27.6% a few times a week. Primary device: desktop or laptop 82.3%, phone 4.8%.
https://webaim.org/projects/lowvisionsurvey2/

**B22. W3C, Understanding WCAG 2.2 Success Criterion 1.4.10 Reflow.** Content must work "without requiring scrolling in two dimensions" for "vertical scrolling content at a width equivalent to 320 CSS pixels." "320 CSS pixels is equivalent to a starting viewport width of 1280 CSS pixels wide at 400% zoom." People with low vision who enlarge text otherwise scroll sideways across long lines and lose their place.
https://www.w3.org/WAI/WCAG22/Understanding/reflow

### Sources that blocked or moved

- emp.lbl.gov (news and publications pages): HTTP 403 twice. Read through A9's press coverage instead.
- mass.gov Open Meeting Law page and checklist: HTTP 403 twice. The statute (A7) was read instead.
- api.census.gov: redirected to a "missing key" page. census.gov QuickFacts: 403. api.censusreporter.org: 404.
- plainlanguage.gov redirected to digital.gov, whose page has no quote on second-language readers; GOV.UK (B16) covers it.
- gov.uk/guidance/content-design/writing-for-gov-uk has moved; the new "Use clear language" page is cited.
- Pew's engagement topline, the NAR survey, the MBI deck and the Harvard report were PDFs; all four were read with pdftotext, not through a bot bypass.

---

## Part 2. The eight testers

Each name is invented. Towns, meetings and documents are real and on the site today.

**T1. Donna Reilly, 58, Plympton, MA.** iPhone, Safari, 390 by 844, no zoom. A letter came in the mail about "Parallel Products ground-mounted solar, 87 County Road"; as an abutter within 300 feet she gets one by law (A8). She has never been to a Planning Board meeting (A3: 13% of adults attended one last year). She knows the street and the words "public hearing" from the letter. Gets local news from a Facebook group (A1: 54% use social media for local political news).
- Scans in an F pattern and reads the start of a line, not the end (B1).
- Judges a link or heading by its first two words (B2).
- Spends most attention above the fold and rarely goes past the third screenful; budget 3 screens (B3).
- A phone session is about 72 seconds and gets interrupted (B9).
- Dislikes being sent to a PDF on a phone (B11).

**T2. Walter Pacheco, 74, Carver, MA.** Windows laptop, 1366 by 768, browser zoom 125% (1093 by 614 CSS px). Retired; reads the Select Board agenda every week on the town site (A1: 81% of 65 and older get local political news; A2: 32% follow local news very closely). A neighbour said this site "reads the agendas for you." Wants to be told by email when something new goes up.
- Takes 43% longer and succeeds less often (55% vs 75%); 95% methodical, so he reads the whole page in order (B6).
- Blames himself when something fails (90%) and is almost twice as likely to give up; 45% uncomfortable trying new things, half as likely to try site search (B6).
- Trips on small, light text and small targets, and on unclear wording (B7, B6).
- Presses Enter rather than hunting for a button; expects a familiar input format (B7).

**T3. Priya Natarajan, 39, Northampton, MA.** Android phone, 360 by 800. Two children; heard at school pickup that the city wants to ban data centers. Checks her phone in gaps (A13: 68% of parents say they are at least sometimes distracted by their phone with their kids).
- Session of about 72 seconds, likely interrupted; wants the gist first (B9).
- Scans headings and the first sentence, does not read (B4).
- 74% of her attention is in the first two screenfuls; budget 2 screens (B3).
- Uses navigation she can see; hidden menus cut discoverability by more than 20% (B10).

**T4. Marcus Bell, 31, reporter at a weekly paper covering Plymouth County.** Desktop 1366 by 768. Works alone across five towns (A11; A10: 22% say their outlet is cutting back). Uses social media for work (A10: 94%). Wants the primary document, the date, and a list he can paste into a story or share.
- Expert who still prefers succinct, scannable text (B12, B16).
- Scans then searches; will use filters and site search (B4).
- Needs links whose first words say what they are (B2).
- Wants to avoid opening a PDF unless it is the source document (B11).

**T5. Elena Ruiz-Hartman, 44, permitting lead at a solar developer, Boston office.** Desktop 1920 by 1080. Tracks Carver, Plympton and Somerset. A third of applications in her industry get canceled and half delayed, with local ordinances and opposition among the top three causes, and opposition is "more prevalent and more expensive to address than five years ago" (A9). She watches for moratoria and bylaw changes across many towns.
- Specialist who does not want to read complex language when there is an alternative (B16, B12).
- Will scroll, filter and search; reads the whole list when the task calls for it (B4).
- Expects filters to produce a shareable URL and an alert she can set for several towns at once (her job, A9; no behavioural claim beyond that).

**T6. Janet Kowalczyk, 61, Town Clerk, Acushnet, MA.** Office PC 1366 by 768. Posts every meeting notice 48 hours ahead, not counting weekends and holidays (A7). Her town's website runs on a small budget (A6: staffing and budget are "a huge constraint"). Came to check what the site says about Acushnet and how it reads the town's agendas.
- Reads methodically and checks accuracy against the source (B6 pattern; she is under 65, so B7's "0.8% per year" decline applies rather than the 65-plus figures).
- Prefers plain text to jargon even as an expert (B12).
- Expects a way to report an error and reach a person (B6: unclear error paths lose older users).

**T7. Ray Thibodeau, 52, real-estate agent, Swansea and Somerset, MA.** iPhone 390 by 844, in the car between showings. His phone runs his business (A12: lockbox and showing tech and eSignature rated most impactful; 87% use Facebook for business). Wants to know what towns near a listing have coming up, and to send a link to a client.
- 72-second sessions, interrupted (B9).
- Budget 2 screenfuls (B3).
- Reads the first two words of a heading (B2).
- Looks for a share action where the content is, not at the bottom (B9: "gist before minutiae").

**T8. Beatriz Fonseca, 67, Somerset, MA, Riverside Avenue.** Portuguese is her first language (A14: about 480,000 working-age adults in the state have limited English). Low vision from macular degeneration (B19: vision disability 5.5% of adults). iPhone with Safari Page Zoom at 200%, which halves the layout width to 195 CSS px (B21: 44% of low-vision users use browser zoom; 29.7% sit at 200 to 400%). She saw a sign about the battery plant on Riverside Avenue.
- Stops reading when text is hard (B21: 14.8% do so every day).
- Reads word by word and slows down on difficult text on a phone (B8, 2016 note). Note: B5's "plowing" and skipping findings are about lower-literacy English readers; we apply them to a second-language reader only as an inference and say so where used.
- Needs each term explained the first time it appears (B16).
- Needs the page to reflow at narrow widths without sideways scrolling (B22).

---

## Part 3. Walkthrough logs

Format: step, what is on screen (CSS px from the top of the page), will the tester know what to do, see it, connect it to the goal, see progress; where they stall and why; words they would not understand; result. "Screen n" means the nth screenful at that tester's viewport. A note on closed disclosures: Chromium keeps the layout of closed `<details>` content, so our text dumps sometimes list hidden filter labels; the positions quoted below are from the screenshots and visible controls.

### T1 Donna, iPhone, 3-screen budget

**Task A. Is anything coming up in Plympton?**
1. Home. First screen: title, "See what your town is about to decide", "Type your town...", label "Your town", input (188 wide) and "Find my town" button side by side at 365, "Or try Carver, Amherst or Clay, NY", then "This week" at 604. Knows what to do: yes, the box is the obvious thing. (t1_a1_home.png)
2. She types "Plimpton" (one common slip). The listbox stays hidden. Pressing "Find my town" lands on /towns?q=Plimpton with "No towns match. Check the spelling, or search by county." above a page of 351 towns. She can recover, but the recovery page is the longest on the site. (t1_a2_misspelling.png; extra_misspelled_submit.png)
3. She retypes "Plympton": suggestion "Plympton MA · 1 meeting coming up" appears. Tap "Find my town". (t1_a3_typed.png)
4. /ma/plympton. First screen: "Plympton, Massachusetts" and the lead "One meeting is coming up in Plympton: the Planning Board on Tue Nov 17, about Parallel Products ground-mounted solar, 87 County Road." The answer is the first sentence. (t1_a4_plympton.png)
Result: done, within one screen of the town page. Stall: the misspelling path (B5: spelling is a known trip; the recovery is a long list rather than a nearest-match suggestion).

**Task B. When is the solar hearing, and can she speak?**
1. On /ma/plympton the row heading "Parallel Products ground-mounted solar, 87 County Road" is an underlined link at 710 (screen 1). First two words "Parallel Products" match her letter. She taps.
2. /m/plympton-planning-board-2026-11-17. First screen: heading, then "On Nov 17 at 6:30 pm, at Deborah Sampson Meeting Room. The Planning Board's hearing continues. Anyone can go and speak." Then When, Where, Public comment ("Public hearing: anyone can attend and ask to speak."). (t1_b1_meeting.png)
Result: done, first screen. Two doubts she would carry out of the room: "Where: Deborah Sampson Meeting Room" has no building or street, and she has never been to Town House; and "hearing continues" sounds like she missed the start (the explanation, "The public hearing continues from an earlier session," is in screen 2, and "Continued" is defined only in "Words on the agenda" lower still). Words she would not know: "site plan approval under zoning bylaw Section 300-6.10", "Assessors M-B-L 4-2-11".

**Task C. Find the agenda PDF.**
1. Same meeting page: "Agenda: Open the agenda (first seen Oct 16)" at 636, a 21 px tall link. Nothing says it is a PDF. On the town page the row's link read "Read the Nov 17 agenda : Plympton Planning Board", also without "(PDF)", while the Carver Oct 21 row on another page does say "(PDF)".
2. The link opens https://www.town.plympton.ma.us/AgendaCenter/ViewFile/Agenda/_11172026-645, served as application/pdf ("NOTICE OF HEARING- 11 17 29026.pdf"), in the browser.
Result: done, but she gets a PDF she was not warned about (B11), from a 21 px target (B7, spec: 44 px). Stall severity medium.

### T2 Walter, laptop at 125%, reads everything

**Task A. What is the Select Board deciding on Thu Oct 29?**
1. Home at 1093 by 614: box and button on the first screen at 335. He types "Carver" and presses Enter; it works (good: B7 flexible input). (t2_a2_typed.png)
2. /ma/carver. Lead: "Nothing is on Carver's agendas right now about solar, batteries, data centers, zoning or housing. Two items have moved to later days: Federal Pond Solar, 104 Tremont St (now Wed Nov 4) and Federal Pond Solar's hearing at 104 Tremont Street (now Tue Nov 10). The next agenda we know of is the Select Board's, for Thu Oct 29." He reads it twice. There is no link on "Select Board's" and no row for Oct 29 anywhere on the page. (t2_a3_carver.png)
3. He scrolls methodically. Under the heading "Coming up" the next thing is "Most recent" and a past meeting (Tue Oct 27, "The Planning Board held a public hearing"). He opens "Earlier meetings, back to July" and finds Select Board rows for Oct 20, Oct 6 and Sep 8, each with "Read the ... agenda : Carver Select Board". None for Oct 29. (t2_a4_carver_full.png)
Result: stalled. The sentence promises an agenda the page does not give, and the "Coming up" heading sits over a list of past meetings. He would conclude he did something wrong (B6: seniors blame themselves 90% of the time) and go back to carverma.gov. The two "moved" items also have no row for Nov 4 or Nov 10; the links on them jump to anchors of past meetings.

**Task B. Get told when Carver posts something new.**
1. /ma/carver: "Follow Carver's meetings" button at 451 (first screen) with "You get a page and a calendar feed for Carver and the towns next door, updated every morning. Free, no account." He wants email; the word is not there. He clicks anyway.
2. /watch?town=MA:Carver. "Follow Carver". Then: "Over the last 30 days, Carver and 5 towns next to it had 12 meetings on these topics, so expect about that many alerts a month. Coming up next: ..." Then "The next page has your calendar feed and a private page for these towns." A ticked checkbox "Also the 5 towns next door: Kingston, Middleborough, Plymouth, Plympton and Wareham (Middleborough can't be read yet)". "Topics: ... Change topics". A closed "Other ways: topics, towns, calendar, RSS". The button "Follow these towns" is at 825, on screen 2. (t2_b1_watch.png, t5_b2_watch2.png)
3. He opens "Other ways": topic checkboxes and a town list. No email field. The page's hidden markup holds an "email-option" block ("Your email address", "At most one email a day, only when something new is posted") inside the send step, so email is offered only after the button is pressed. We did not press it.
Result: stalled with doubt. He cannot see, before committing, that email exists; "calendar feed", "private page" and "RSS" are unexplained (B6: unclear wording; B7). He is reluctant to explore (B6: 45%), so the odds he presses a button whose outcome he cannot predict are poor.

**Task C. Who is proposing the solar project at 235 Main Street?**
1. /ma/carver, row for Tue Oct 27: heading "Special permit and site plans for Parallel Products Solar Energy at 235 Main Street". The proposer is in the heading; it is not a link (the meeting is past). "Details" adds the hearing lines but no separate applicant line.
Result: done. Note the heading's first two words are "Special permit", not the subject, which is against the spec's own rule and B2.

### T3 Priya, Android 360 by 800, 2-screen budget

**Task A. Anything coming up in Northampton?**
1. Home: box at 437; "Northampton" plus Enter.
2. /ma/northampton: "One meeting is coming up in Northampton: the Planning Board on Thu Oct 29, about 365-day moratorium on new data centers." (t3_a2_northampton.png)
Result: done, first screen.

**Task B. When is the moratorium hearing, can she speak?**
1. Row link "365-day moratorium on new data centers" at 778 (bottom of screen 1). Tap.
2. Meeting page first screen: "Tomorrow at 7 pm, at City Council Chambers, 212 Main St. The Planning Board holds a public hearing. Anyone can go and speak. The ordinance would define data centers and impose a 365 day temporary moratorium on establishing one, by changing zoning sections 350-2.0 and 350-5.2." When 626, Where 658, Public comment 746 ("...After the hearing the Planning Board makes a recommendation; the City Council votes on the ordinance."). (t3_b1_meeting.png)
Result: done, first screen. Words she would skip: "ordinance", "zoning sections 350-2.0 and 350-5.2", later "joint council committee" and "Committee on Legislative Matters". The sentence about the Council voting later is useful and plain.

**Task C. Get told when something new is posted.**
1. The header shows "Follow a town" as a visible button on every page (56, 133 by 44). Good (B10). Tap.
2. /watch: "Follow a town", one paragraph, "Your town" input with two hints that say the same thing ("Start typing and pick it from the list." and "Pick it from the list as you type."), "Continue" at 555. (t3_c1_watch.png)
3. Types Northampton, suggestion "Northampton MA", Continue. Step 2 appears in place: "Follow Northampton", "5 meetings" a month, "The next page has your calendar feed and a private page for these towns." (t3_c3_watch2.png)
4. "Follow these towns" is at 1227 on an 800-tall screen: screen 2.5. Her budget ends at 1600, so she reaches it, but only after the neighbour checkbox, the topic sentence and a closed "Other ways" row.
Result: done with doubt. Nothing on screen says she can get a text or an email; "calendar feed" is the only delivery named. In a 72-second session (B9) the odds she presses an unexplained button are mixed; we score it a partial.

### T4 Marcus, reporter, desktop 1366 by 768

**Task A. Every meeting in Plymouth County this week.**
1. /upcoming: "Narrow by county, subject or town" is a closed disclosure at 306, on the first screen. He opens it: County, Topic, Town. (t4_a2_narrow_open.png)
2. County = Plymouth. The URL becomes /upcoming?county=MA:Plymouth (shareable, good). The page says "2 of 44 meetings, 2 items", then "We can't read these Plymouth County towns yet: Duxbury, Hanover, Hanson and Middleborough (website blocks automatic reading); Abington (agendas posted without dates). Why", then the rows (Wed Oct 28, Tue Nov 17). (t4_a3_plymouth.png)
3. He notices the county list has "Bristol" twice with no state, and runs MA counties, then "Columbia", then "Bristol, Newport, Providence" with no state headings. At the bottom: "Copy this week's list" and "Download CSV".
Result: done. The can't-read paragraph is useful to him, less so to residents (see T7).

**Task B. Who is behind the Parallel Products solar project, across towns?**
1. /search, "Parallel Products", Search. "7 meetings with 'Parallel Products' on the agenda, 1 of them still ahead, shown first." Plympton Nov 17 first, then Carver Oct 21 and older rows. (t4_b1_search.png)
2. Misspelled "Parrallel Products": "No agendas contain 'parrallel'. Showing 7 meetings for 'parallel Products' instead." Good recovery. (t4_b2_misspelled.png)
3. On the unfiltered /search page the first result card reads "Agenda" with the snippet "Agenda. Agenda. Ashby, Massachusetts. Planning Board. Loading… Sign in", scraped from a Google Drive page. He would distrust that card. (explore_search.png)
Result: done.

**Task C. The agenda, the source and a citation for the Plympton hearing.**
1. /m/plympton-planning-board-2026-11-17: Applicant "Parallel Products Solar Energy, LLC"; "Open the agenda (first seen Oct 16)"; at the bottom "From the Planning Board agenda first seen Oct 16 on town.plympton.ma.us. Last checked Oct 28, 7:03 am. Copy citation". (t4_c1_meeting.png)
2. /trending says of this story "Also in 2 other towns", but the meeting page does not link the Carver items about the same company; he has to search again.
Result: done; the cross-town link is a gap, not a stall.

### T5 Elena, developer, desktop 1920 by 1080

**Task A. Every moratorium and permit-rule change coming up.**
1. /trending: ranked stories, "Your towns" box, closed "Filter by date or topic". Opening it shows When (week, month, year) and nine topic chips. Tapping "Moratoriums" gives /trending?topics=moratorium with three stories (Northampton, Somerset, and a Town Meeting article). (extra_trending_moratoriums.png)
2. /upcoming, Topic = "Clean-energy permit rules": three meetings (Oct 30, Nov 5, Nov 10), URL carries the filter. (t5_a3_upcoming_permit_rules.png)
Result: done.

**Task B. Alerts for Carver, Plympton and Somerset.**
1. /watch, "Carver", Continue. Step 2 offers Carver plus "the 5 towns next door" as one checkbox (Plympton is among them), "Change town" (which replaces, not adds), "Change topics" with all nine topics pre-ticked, and under "Other ways" a town list limited to Carver and its five neighbours. There is no "add another town". Somerset cannot join this alert set. (t5_b3_watch_full.png)
Result: stalled for her purpose. She would have to set up a second follow and get two feeds. The volume line ("12 meetings a month") is good and plain.

**Task C. The state's rulings on town bylaws.**
1. /attorney-general: "What a town can do", one paragraph, then three summaries with "See them" links (340 by 28), tabs "Every ruling, Town actions, Data-center ledger, State law", and "Words on this page". (t5_c1_ag.png)
Result: done. Dense but it is her material (B16: specialists tolerate it; still, the "See them" links are short targets).

### T6 Janet, town clerk, office desktop

**Task A. What does the site say about Acushnet, and is it right?**
1. /towns, type "Acushnet" in "Town or county", click the link. (t6_a2_towns_filtered.png)
2. /ma/acushnet: "One meeting is coming up in Acushnet: the Conservation Commission on Wed Oct 28, about 001- 0555 Morses Lane Solar 1 LLC at 001-0555 Morses Lane." The row heading repeats "001- 0555 Morses Lane Solar 1 LLC at 001-0555 Morses Lane". "Read the Oct 28 agenda" goes to acushnet.ma.us AgendaCenter, the right source. "About Acushnet's agendas" lists the four boards read and the check time. (t6_a3_acushnet.png)
Result: done. She recognises the parcel number the agenda used; a resident would not (B2: the first two words "001- 0555" say nothing). "Next door" names Fairhaven and New Bedford as unreadable with a "why" link.

**Task B. How does the site read agendas, and why can't it read Fairhaven?**
1. /how-it-works: "How we collect agendas: Our program, AgendaAheadBot, visits town websites once a day and reads only public agenda pages. It follows each website's rules for programs like ours." "Why, town by town" lists reasons. (t6_b1_how.png)
2. /bot: robots.txt instructions, "It never logs in, fills in forms or gets past a bot check," rate limits, "Send us a note". (t6_b2_bot.png)
Result: done. Plain and complete for her.

**Task C. Report a mistake.**
1. "Report a problem with this page" is at 1661 on the Acushnet page, a 19 px tall link at the very bottom. She reads to the bottom, so she finds it.
2. /contact?about=/ma/acushnet: "What is this about?" (three choices), Message, Send message; "The form doesn't ask who you are, so add your email address if you'd like an answer." "Town officials: send us an adopted bylaw's text or Town Meeting vote results." (t6_c1_contact.png)
Result: done. A clerk expecting a reply has to remember to type her email into the message body.

### T7 Ray, agent, iPhone, 2-screen budget

**Task A. What do towns near Somerset have coming up?**
1. /ma/somerset: lead "Somerset has four meetings coming up, on battery storage and data centers. The first is the Board of Selectmen on Wed Oct 28, about temporary ban on new data centers (a moratorium)." Follow button, then rows. (t7_a1_somerset.png)
2. The "Next door" heading is at 2986 on a page 4.9 screens long: screen 3.5. His budget ends at 1688. The sentence he needed, "Nothing is coming up in Dighton, Fall River, Freetown and Swansea. We can't read Berkley's agendas yet (why)," is never seen. (t7_a2_somerset_bottom.png)
Result: stalled (B3: rarely beyond the third screenful; B9: 72-second session).

**Task B. Zoning changes in Bristol County this month.**
1. /upcoming: "Narrow by county, subject or town" at 373, first screen. Open; County = Bristol (the first of two "Bristol" entries; he guesses MA); Topic = Zoning changes. (t7_b2_narrow_open.png)
2. "4 of 44 meetings, 4 items", then the can't-read paragraph for Bristol County, then rows from 1020: "Zoning change" (Mansfield), "Town Meeting article about zoning changes" (North Attleborough), Nov 4, Nov 16. First result on screen 2. (t7_b3_filtered.png)
Result: done within budget. The heading "Zoning change" tells him nothing about what changes (B2).

**Task C. Send a client the link to the battery-plant hearing.**
1. /m/somerset-zoning-board-of-appeals-2026-10-29: the first two screens hold the heading, lead, When, Where, Watch (YouTube), Public comment, Agenda link and the start of "On the agenda". (t7_c1_meeting.png)
2. "Copy link" and "Add this meeting to my calendar" are at 1795, screen 3, below his budget. The page does not call the phone's share sheet.
Result: stalled on the page; he would copy the URL from the browser bar, which works, so the task is done without the page's help.

### T8 Beatriz, low vision, second-language reader, 200% zoom (195 by 422)

**Task A. Anything coming up in Somerset?**
1. Home. First screen: the three-bar mark and "Agenda Ahead" (clipped at the right), "Follow a town" button, nav row "Coming up  Towns  Se" (the "Search" link's right edge is at 229 on a 205-wide document, and the page cannot scroll sideways, so "Search" is cut off and unreachable at this zoom), then the heading one word per line: "See what / your town / is about / to decide", then "Type your town." (t8_a1_home_zoom.png)
2. Screen 2: the town box. The input is 28 px wide next to a 162 px "Find my town" button. She cannot see what she types. (extra_zoom_home_box_scrolled.png)
3. She types "Somerset" by feel and presses the keyboard's Go. /ma/somerset: breadcrumb, heading, lead sentence. (t8_a3_somerset_zoom.png)
Result: done, with a high-severity stall at the box (B21: hard text and hard controls make her stop; B22: reflow is about keeping things usable when enlarged).

**Task B. When and where is the battery hearing?**
1. On /ma/somerset the "Battery storage plant at 1606 Riverside Ave" link is at 1738, screen 4.1 of 12.7. She scrolls and taps. (t8_a3b_somerset_zoom4.png)
2. Meeting page: screen 1 is the heading ("Battery / storage / plant / at 1606 / Riverside / Ave") and the lead; "When" is at 823 (screen 2), "Public comment" at 1281 (screen 3), "Agenda" at 1536 (screen 4). (t8_b1_meeting_zoom.png)
Result: done after three zoomed screens. The lead sentence already carries the answer ("Tomorrow at 6 pm, at Somerset Old Town Hall, 1480 County Street"), which saves her.

**Task C. Who is proposing it, and what do the words mean?**
1. The sentence she needs, "Somerset Energy Storage, LLC wants zoning approval (a Planned Development under Section 6.10 of the zoning bylaw) to build a commercial battery energy storage system at 1606 Riverside Avenue, on land owned by Somerset Riverside 1606, LLC in the Industrial Zoning District and the Business Industrial Overlay District," is 54 words (B16: 25-word ceiling) and sits on screens 4 to 5. "Applicant: Somerset Energy Storage, LLC" is at 2914, screen 7.
2. Words that stop her: "Zoning Board of Appeals" (breadcrumb, heading row, and three more times, never explained), "ZBA hearing", "petition", "Planned Development", "zoning bylaw", "Assessor's Map B2, Lot 203". The "Words on the agenda" box explains only "Overlay district" and "Battery energy storage," and it is at about screen 8 of 10, far below the words it explains.
Result: stalled. She gets a company name she does not recognise and three unexplained terms before the glossary. (B16: explain the term the first time; B8: difficult text is slower on a phone; B5's skipping-when-dense finding is applied here as an inference about second-language readers, not a measured one.)

### Checks against the spec's own ship list (all testers)

- First meeting row inside the first 500 px on a phone: /upcoming puts "Wed Oct 28" at 538 and the first heading at 576; /ma/somerset puts the first heading at 737; home's first "This week" row starts at 651. All miss.
- Every control 44 px or taller: misses on "Open the agenda" (21), "Read the ... agenda" row links (36), "Copy link" (40), "Add this meeting to my calendar" (40), "Copy citation" (25), "Report a problem with this page" (19), "Why" (19), the example-town links on home (19), "See them" on the rulings page (28).
- Nothing under 16 px: passes on every page we loaded.
- No horizontal scroll at 320: passes on /, /upcoming, /ma/somerset, the meeting page, /watch, /search. At 195 (200% on a 390 phone) the page does not scroll sideways either, but the header nav clips "Search".
- "(PDF)" marking: the Somerset, Plympton and Northampton agenda links are all served as application/pdf and none is marked; Carver's Oct 21 row is marked. The meeting-page "Open the agenda" never is.

---

## Part 4. Every stall

Severity: High blocks the task for the testers named; Medium slows it or leaves them unsure; Low is friction or inconsistency.

| # | Page | Element | Testers | What happens | Evidence | Severity |
|---|------|---------|---------|--------------|----------|----------|
| 1 | /ma/carver | Lead sentence "The next agenda we know of is the Select Board's, for Thu Oct 29" and the two "moved" items | T2 (and any Carver resident) | No link, no row, no agenda for Oct 29, Nov 4 or Nov 10; "Coming up" heading sits over past meetings; reader blames himself | B6 (90% self-blame, twice as likely to give up); B1 (first lines get the gaze) | High |
| 2 | /watch step 2 | Delivery wording and the "Follow these towns" button | T2, T3, T5 | Email is not mentioned before the button; "calendar feed", "private page", "RSS" unexplained; button at screen 2 (laptop) and 2.4 to 2.5 (phones) | B6, B7 (unclear wording); B17 (one thing per page, say what happens next); B3 | High |
| 3 | Home | Town box at 195 CSS px (200% zoom on a 390 phone) | T8 | Input collapses to 28 px beside a 162 px button; typing is invisible | B21 (14.8% stop daily when text is hard); B22 | High |
| 4 | /ma/somerset and other town pages | "Next door" heading at screen 3.5 of 4.9 (phone) | T7, T1, T3 | Never reached within a 2 or 3-screen budget | B3 (57% above the fold, rarely past screen 3); B9 | Medium |
| 5 | Meeting page | "Copy link", "Add this meeting to my calendar" at screen 3 (phone) | T7, T3 | Share and calendar never reached; no native share sheet | B3; B9 (gist before minutiae) | Medium |
| 6 | Meeting page, town rows | Agenda links not marked as PDF; "Open the agenda" is a 21 px target | T1, T2, T7 | Reader lands in a PDF viewer unwarned; small target | B11; B7 (small targets); B6 | Medium |
| 7 | /upcoming, /ma/acushnet, /ma/boston rows | Headings "001- 0555 Morses Lane Solar 1 LLC at 001-0555 Morses Lane", "Battery storage", "Zoning change" | T6, T7, T1, T3 | First two words carry no meaning; lead sentence repeats the parcel code | B2 (two words decide); B1 | Medium |
| 8 | Meeting page | Glossary "Words on the agenda" at screen 8 of 10 at zoom; terms used four to five times before it; "Zoning Board of Appeals", "petition", "Planned Development", "ordinance", "site plan", "Assessor's Map" never defined | T8, T1, T3 | Second-language and first-time readers stop at the words | B16 (explain on first use; non-native speakers); B8; B5 (inference) | Medium |
| 9 | Meeting page | 54-word applicant sentence (Somerset ZBA) | T8, T3 | Too long to hold on a phone | B16 (25 words); B8 | Medium |
| 10 | Meeting page (Plympton) | "Where: Deborah Sampson Meeting Room" with no building or street | T1 | A first-time attendee cannot find it | B1 (reader takes the first line as the answer); spec rule 6 | Medium |
| 11 | /watch step 2 | No way to add a second town; "Change town" replaces | T5 | Professional tracking three towns must set up separate follows | A9 (her job); B17 | Medium |
| 12 | Site-wide | Targets under 44 px: "Read the ... agenda" (36), "Copy citation" (25), "Report a problem" (19), "Why" (19), example towns (19), "See them" (28) | T2, T8, T6 | Mis-taps and misses for older and low-vision users | B7; B6; spec ship list | Medium |
| 13 | /upcoming | County select lists "Bristol" twice and mixes three states with no group labels | T7, T4 | Wrong county chosen, or hesitation | B2 (links and options must predict their result) | Low |
| 14 | /upcoming after a filter | "We can't read these ... towns yet" paragraph pushes the first result to screen 2 on a phone | T7, T3 | Diagnostic before content | B3; spec rule 9 | Low |
| 15 | Home | Misspelled town submits to /towns?q= with a 351-town list | T1, T8 | Long recovery page; no near-match suggestion | B5 (spelling; first hit) | Low |
| 16 | Header at 195 px | Nav row clips "Search"; page cannot scroll to it | T8 | Search unreachable at 200% on a small phone (fine at 320) | B22 (sideways loss); B10 | Low |
| 17 | /search default page | Result card "Agenda" with snippet "Agenda. Agenda. Ashby, Massachusetts. Planning Board. Loading… Sign in" | T4 | Looks broken; lowers trust | B2 | Low |
| 18 | /watch | Two hints saying the same thing above the town box | T3, T2 | Noise before the field | B14 pattern (hint text competes with the field) | Low |
| 19 | /watch and /contact | Honeypot "Website" text field in the accessibility tree (off-screen, tabindex -1) | screen-reader users (B20) | "Website, edit text" is announced in forms mode with no purpose | B20 ("links or buttons that don't make sense") | Low |
| 20 | Home header | The three-bar mark reads as a menu icon on a phone | all phone testers | A tap goes to the home page instead of opening a menu | B10 (the icon is the hamburger convention) | Low |

---

## Part 5. The 15 fixes with the biggest effect, ranked

1. **Town page lead: never name an agenda you do not link.** /ma/carver (and the same template everywhere). Replace "The next agenda we know of is the Select Board's, for Thu Oct 29." with a sentence that links the agenda and says what is on it: "The Select Board meets Thu Oct 29 at 5 pm. Its agenda has nothing on these subjects. Read the Oct 29 agenda (PDF)." For moved items with no new agenda yet: "Federal Pond Solar's hearing moved to Tue Nov 10. The town hasn't posted that agenda yet; we'll add it the morning it appears." Give each such item a dated row under "Coming up" so the page's structure matches the sentence. (Stall 1)

2. **Follow, step 2: say how you will be told, before the button.** /watch. Insert, directly under the volume sentence: "You can get this three ways: an email each morning something new is posted, a page you can bookmark, or a feed for your phone's calendar." Replace "The next page has your calendar feed and a private page for these towns." with "Next, you choose email or page." Rename the button to "Choose how to get it" and move it above the neighbour checkbox and topics line, so it sits on the first screen at 390. Replace "RSS" with "a feed for a news app" in the "Other ways" label. (Stall 2)

3. **Home town box: stack the button under the input below 360 px.** In styles.css, for the `.home-hero` field row: `@media (max-width: 359px) { .field-row { flex-direction: column; } #town-q { width: 100%; } }`, and give `#town-q` `min-width: 12ch`. Also check the /trending "Your towns" row, which uses the same layout. (Stall 3)

4. **"Next door" moves up to the lead.** Town page template: put the "Next door" sentence as the last sentence of the lead block, before the Follow button: "Next door, nothing is coming up in Dighton, Fall River, Freetown and Swansea; we can't read Berkley's agendas yet (why)." Keep the lower section as a repeat with the town links. (Stall 4)

5. **Share and calendar move into the when/where list.** Meeting page: add a fourth line to the list that holds When, Where and Public comment: "Share: Copy the link · Add it to your calendar", using `navigator.share` when the browser has it and falling back to Copy link. Make both 44 px tall. (Stall 5)

6. **Mark every PDF, everywhere, from the content type.** At build time, record the content-type of each agenda URL; render "Read the Nov 17 agenda (PDF)" and "Open the agenda (PDF)". Plympton, Somerset and Northampton links are PDFs today and say nothing. Raise "Open the agenda" to a 44 px row. (Stall 6)

7. **Headings start with the thing, not a code or a bare topic.** Rewrite rule for row headings: strip leading parcel numbers and use the street: "Solar project at 555 Morses Lane (Morses Lane Solar 1 LLC)" instead of "001- 0555 Morses Lane Solar 1 LLC at 001-0555 Morses Lane"; "Battery storage: City Council discussion" instead of "Battery storage"; "Zoning change: [the article's subject]" instead of "Zoning change" when the agenda gives it, otherwise "Zoning change (the agenda doesn't say what)". Apply the same to the lead sentence, which repeats the heading. (Stall 7)

8. **Explain the board and the term inline, the first time.** Meeting page lead and "On the agenda": "The Zoning Board of Appeals (the board that grants exceptions to zoning rules) holds a public hearing." Add "petition (the formal request)", "Planned Development (a project approved as one package under the zoning bylaw)", "ordinance (a city law)", "site plan review (the board's check of layout, parking, drainage and lighting)" to the glossary, and move "Words on the agenda" to directly under "On the agenda", open by default. (Stall 8)

9. **Split the applicant sentence.** Meeting page write-up: cap sentences at 25 words. Somerset ZBA today: "Somerset Energy Storage, LLC wants permission to build a battery storage plant at 1606 Riverside Avenue. The land belongs to Somerset Riverside 1606, LLC. It's in the town's industrial zone, with an extra overlay zone on top. The board treats it as a Planned Development under Section 6.10 of the zoning bylaw." (Stall 9)

10. **Every "Where" gets a building and street.** Keep a per-town venue table (room name to building and address). Plympton: "Deborah Sampson Meeting Room, Plympton Town House, 5 Palmer Road" if that is the venue (check it with the clerk); when unknown, print "The agenda doesn't give the address." as the spec's rule 5 already asks. (Stall 10)

11. **Follow: "Add another town".** /watch step 2: under the neighbour checkbox add a link "Add another town" that opens the same town box and appends to the list, with the chosen towns read back as a sentence: "You'll follow Carver, Plympton and Somerset, and the towns next to them." (Stall 11)

12. **Raise every control to 44 px.** styles.css: give `.line-link`, `.copy`, `.cite`, the "Why" link, the example-town links and "Report a problem" `display: inline-block; min-height: 44px; padding: 11px 0;` (or a 44 px line-height). The spec's own check requires it. (Stall 12)

13. **County filter: group by state and disambiguate.** /upcoming and /search selects: `<optgroup label="Massachusetts">`, `"New York"`, `"Rhode Island"`, and option text "Bristol, MA" / "Bristol, RI". (Stall 13)

14. **Fold the can't-read note after a filter.** /upcoming: render "5 Plymouth County towns we can't read yet (why)" as a one-line `<details>` summary under the count, closed, so the first row returns to the first screen on a phone. Move the first row above 500 px on every list page by trimming the lead to one sentence and the tabs row to one line, as the spec's ship list requires. (Stall 14)

15. **Smaller cleanups in one pass.** Home: on a miss, suggest the closest names ("Did you mean Plympton?") before sending to /towns. Header: let the nav wrap at narrow widths (`flex-wrap: wrap`) so "Search" is never clipped, and consider dropping the three-bar mark on phones. /watch: delete one of the two duplicate hints. /search: hide snippets that contain "Loading…" or "Sign in". Honeypot: add `aria-hidden="true"` and `autocomplete="off"` to the hidden "Website" field. (Stalls 15 to 20)

---

## Part 6. Summary, ten lines

1. The redesign's core works: every tester who asked "is anything coming up in my town" (six of the eight) got the answer from the first screen of the town page, and the meeting page's first sentence answers when, where and whether you can speak for every tester who reached it.
2. The worst failure is on Carver's page: the lead names a Select Board agenda and two moved hearings that the page neither links nor lists, and the retiree who reads every line ends up blaming himself.
3. The follow flow hides the one word the older testers were looking for, "email", until after the commit button, and explains delivery in "calendar feed" and "RSS".
4. At 200% zoom on a phone the home town box shrinks to 28 px wide and the "Search" link is clipped; at the WCAG 320 px line the site passes.
5. Anything below screen 3 on a phone is invisible to the resident, parent and agent testers: "Next door", "Copy link" and "Add to calendar" all live there.
6. Five of the six town agendas we checked are PDFs and only one row says so; the meeting page's "Open the agenda" never does and is a 21 px target.
7. Headings that begin with a parcel code or a bare topic ("001- 0555 Morses Lane...", "Battery storage", "Zoning change") fail the two-word test that residents and the agent apply.
8. The glossary is the right idea in the wrong place: it sits at the bottom, after the terms have appeared four or five times, and omits the board names and "petition".
9. The spec's own ship checks miss today on first-row position (538 to 737 px on phones) and on ten controls under 44 px; they pass on text size and horizontal scroll.
10. The fifteen fixes are wording and position changes, not new features; the first six remove every High stall and most of the Medium ones.
