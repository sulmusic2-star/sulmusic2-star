# Civic and plain-language rules for Agenda Ahead

What the best civic and plain-language designers have already worked out, applied to a site whose one job is to answer "what is my town about to decide?" on five pages: home, a town page, a list of upcoming meetings, a single meeting page, and a sign-up to follow a town.

Everything quoted below was read from the linked page on 28 Oct 2026. Where a site blocked automated reading (documenters.org, axios.com), the note says so and the source is the nearest page that could be read.

Live-site measurements in section 5 come from Playwright with the preinstalled Chromium at 390×844 and 1366×900. Screenshots and metrics are in `/tmp/claude-0/-home-user-sulmusic2-star/815cfdd0-e090-5147-aee8-a5db345f6b5d/scratchpad/design2/shots/`.

---

## 1. The 30 most applicable rules

Format: **rule** — source — *how it applies here*.

### Writing

1. **Put the most important information first; taper to detail (the inverted pyramid).** — [GOV.UK, Create a clear structure](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-structure/): "Put the most important information first." — *Every page opens with the decision, not with counts, filters, or when we last checked.*
2. **People read 20 to 28% of a page and skim in an F shape, so write for skimming.** — [GOV.UK, Create a clear structure](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-structure/): users "only read 20 to 28% of text on a webpage." — *Each meeting row must survive being read as its first line only.*
3. **Split sentences over 25 words; no paragraph over 5 sentences.** — [GOV.UK, Use clear language](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/): "Try to split up sentences that are over 25 words long." — *The town-page summary paragraph (56 words, three ideas) becomes three short lines.*
4. **Write for a reading age of about 9; people with high literacy prefer plain English too.** — [GOV.UK, Use clear language](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/): "Research shows that people with higher levels of literacy prefer plain English." The reading-age-9 target is the GOV.UK standard as restated by councils that follow it ([Surrey CC](https://www.surreycc.gov.uk/website/writing-guide/reading-levels-for-web-pages)). — *"Moratorium", "40B", "ZBA", "Notice of Intent" need a plain phrase first, the term second.*
5. **Explain a term in plain English the first time it appears on a page; after that use the short form.** — [GOV.UK, Use clear language](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/): "Explain the term in plain English when you first use it." and [A to Z](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/): "The first time you use an abbreviation on a page, explain it in full." — *No "What the labels mean" link doing the job the row itself should do.*
6. **Address the reader as "you"; say who "we" is before using "we".** — [GOV.UK, Use the right tone](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/right-tone/): "Address the user as 'you' where possible." "Do not assume the audience will know who the 'we' is." — *Rows say "you can speak", not "public comment: unknown".*
7. **Active voice, present tense, strongest verb; avoid hidden verbs.** — [digital.gov Plain language: Writing](https://digital.gov/guides/plain-language/writing): "Active voice makes it clear who should do what." — *"The board votes on this Tuesday", not "a vote is listed" or "Vote".*
8. **Headings are descriptive, front-loaded, not questions, and still make sense without the text.** — [GOV.UK, Create a clear structure](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-structure/): "users want answers, not questions." — *"Coming up in Carver", not "Coming up"; "This week" over "Next 7 days".*
9. **Titles ≤ 65 characters, unique, saying what the page is for; summaries ≤ 160 characters, ending in a full stop, not repeating the title.** — [GOV.UK, Write clear titles](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-titles/); [Write clear summaries](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/summaries/). — *Meeting page title = the decision, not the board's name.*
10. **Users see about the first 2 words (11 characters) of a list item; make them carry the meaning.** — [NN/g, First 2 Words](https://www.nngroup.com/articles/first-2-words-a-signal-for-scanning/): "Users typically see about 2 words for most list items." — *Start each row with the subject ("Solar farm", "Data-center ban"), never with "An item on…" or "Discusses…".*
11. **Half the word count; one idea per paragraph; highlighted keywords; meaningful subheads; bulleted lists.** — [NN/g, How Users Read on the Web](https://www.nngroup.com/articles/how-users-read-on-the-web/): "79 percent of our test users always scanned any new page." — *Cut every page's intro to one sentence.*
12. **Link text is descriptive, front-loaded, unique per destination, and starts with a verb for a task.** — [GOV.UK, Write effective links](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/add-links/): "do not reuse the same link text to link to different pages"; "start your link with a verb". — *49 links reading "Agenda" on one page become "Read the Oct 28 agenda (PDF)".*
13. **Dates: "2 June" not "2nd June"; ranges use "to" not dashes; times "5:30pm", "midday"; ranges "10am to 11am".** — [GOV.UK A to Z style guide](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/). — *One date style everywhere: "Tue 4 Nov, 7pm" (US order "Tue Nov 4, 7pm" is fine; keep it identical on every page).*
14. **Sentence case everywhere, including titles, tags and service names; no block capitals.** — [GOV.UK A to Z](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/): "Always use sentence case, even in page titles and service names." — *Board names stay proper nouns; labels are sentence case.*
15. **Bold only for interface elements in instructions; emphasise by front-loading, headings, bullets.** — [GOV.UK A to Z](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/): "Only use bold to indicate interface elements". — *Don't bold the whole item sentence; bold nothing or the first two words.*
16. **Do not use FAQs, footnotes, or "further reading" piles; put information where it is needed.** — [GOV.UK A to Z](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/): "Do not use FAQs on GOV.UK."; [Write effective links](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/add-links/): don't "put all the links together at the bottom of the page". — *Definitions live in the row, not on /how-it-works.*
17. **Tell what's new in one strong sentence, then why it matters, then let the reader choose to go deeper.** — Smart Brevity "Core 4": muscular tease (≤ 6 words), one strong first sentence, "Why it matters", "Go deeper" ([Axios HQ](https://www.axioshq.com/smart-brevity); [book excerpt](https://www.goodreads.com/quotes/11463319-smart-brevity-s-core-4-smart-brevity-in-written-form-has)). — *Row = tease line + one sentence + "why it matters to you" + a link.*
18. **Tone: brisk, not terse; emotionless; conversational, one-to-one; no "please note".** — [GOV.UK, Use the right tone](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/right-tone/) and theSkimm's "What's going on:" / "The bigger picture:" lead-ins ([Daily Skimm](https://www.theskimm.com/daily-skimm)). — *Explain like a neighbour who went to the last meeting; no hype, no jokes.*
19. **Report a canceled meeting as news in the first sentence, with what happens instead.** — [Outlier Media / Detroit Documenters](https://outliermedia.org/newsletter/canceled-meeting-documenters-go-the-extra-mile/): the summary "states the cancellation in its first sentence". — *"Canceled: Planning Board, Oct 27. The solar hearing moves to Nov 10."*

### Structure and components

20. **One thing per page: one question, one task, one decision.** — [GOV.UK Service Manual, Form structure](https://www.gov.uk/service-manual/design/form-structure); [Question pages](https://design-system.service.gov.uk/patterns/question-pages/): "Start by asking one question per page". — *Follow-a-town asks for the town, then (next page) how to be told; the meeting page is about one meeting.*
21. **A start page says what the service does, what you need, how long it takes, and has one button worded as the action.** — [GOV.UK, Start using a service](https://design-system.service.gov.uk/patterns/start-using-a-service/): button "with text that's consistent with the action you're asking users to take." — *Home = one sentence + town box + "Show my town's meetings".*
22. **Summary list for key facts: a key, a value, optionally one action; not for tables or plain lists.** — [GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/): "Use a summary list to show information as a list of key facts." — *When / Where / Can you speak? / Agenda on the meeting page, after the decision, not before it.*
23. **Statuses: smallest set that works; adjectives not verbs; sentence case; red only for a problem; the thing needing action stands out, the done thing is plain text.** — [GOV.UK Tag](https://design-system.service.gov.uk/components/tag/): "Use adjectives (descriptive words) and not verbs"; [Complete multiple tasks](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/). — *Keep at most three visual statuses: needs you (hearing/vote), changed (moved/canceled), nothing to do (talk/mention).*
24. **Users confuse tags for buttons; don't mix static and interactive tags; don't overdo tags.** — [USWDS Tag](https://designsystem.digital.gov/components/tag/): "Users frequently confuse tags as buttons." "Don't overdo it." — *One tag per row at most; most rows need none because the sentence says it.*
25. **A collection item = date block, linked heading, short description, optional meta (time, place, tags); six or fewer per group; no "read more" links.** — [USWDS Collection](https://designsystem.digital.gov/components/collection/): limit to "six or fewer"; calendar variant puts `SEP 30` before the heading. — *The meeting list is a collection grouped by week, not a card grid.*
26. **Cards for mixed, browsable content; a plain vertical list for homogeneous items people scan and compare; cards take more space and flatten ranking.** — [NN/g, Cards](https://www.nngroup.com/articles/cards-component/): for "very homogenous items… consider using a standard vertical list"; [USWDS Card](https://designsystem.digital.gov/components/card/): "Don't use a card as a substitute for a table row." — *Meeting rows are homogeneous: use a list with rules between items, not bordered cards.*
27. **A summary box calls out 3 to 5 things a reader must not miss; it is not a table of contents and not for short pages.** — [USWDS Summary box](https://designsystem.digital.gov/components/summary-box/): "Use five bullet points or less." — *Town page: "This month in Carver: 3 bullets", then the list.*
28. **Chunk: short paragraphs, 50–75 characters a line, related things close and aligned, rules or background to separate groups.** — [NN/g, Chunking](https://www.nngroup.com/articles/chunking/); [USWDS Typography](https://designsystem.digital.gov/components/typography/): "Most lines of text should be 45–90 characters" and "A good target for long texts is 66 characters." — *Set the list column at about 36em, not the full 1366 width.*
29. **Body text at least 16px (GOV.UK uses 19px/25px), line height 1.5+ for running text, flush left, at least 1em between paragraphs.** — [GOV.UK type scale](https://design-system.service.gov.uk/styles/type-scale/); [USWDS Typography](https://designsystem.digital.gov/components/typography/): "Set type flush left." — *Keep today's 18px body; raise row titles to the 19/25 or 24/30 step so the subject is the biggest thing in the row.*
30. **Ask for an email only with the reason stated, label "Email address", `type=email`, `autocomplete=email`, then show it back; don't make people type it twice.** — [GOV.UK Email addresses](https://design-system.service.gov.uk/patterns/email-addresses/): "Make it clear what the email address will be used for". — *If the follow page ever takes an address, say exactly what arrives and how often.*

Two more that shape everything, from the sites people say are easy: Axios Local runs "about five items" a morning in bullet style ([Poynter](https://www.poynter.org/?p=1017307)); The Mill sends essentially one story a day by email with a long, specific headline ([manchestermill.co.uk](https://manchestermill.co.uk/); [Tofel](https://dicktofel.substack.com/p/a-local-news-tree-grows-in-britain)); 6AM City editions are 750–1,000 words of "small, conversational blurbs" with links to the source ([Simon Owens](https://simonowens.substack.com/p/how-6am-city-is-scaling-crowdsourced)). None of them shows a count, a filter, or a status word above the first item.

---

## 2. How these systems show a list of dated events on a phone

What the read pages actually do:

| System | First thing in the row | Date placement | Per row | "What you can do" |
|---|---|---|---|---|
| [USWDS Collection, calendar variant](https://designsystem.digital.gov/components/collection/) | Date block `SEP` / `30` (a `<time>`), then the linked heading | Left of the heading, stacked month over day | heading + 1–2 line description (+ meta: time, place, tags in the default variant); "six or fewer" per collection | the heading is the link; no secondary buttons |
| [Boston.gov events](https://www.boston.gov/events) | Day heading "October 28, 2026" groups the day; within it the time "9:00am-5:00pm" leads, then the title | A date heading per day; the time is the first word of each row | time, title, bulleted place / contact / price, short description, "Event details for …" link | one link at the end; canceled = "Canceled:" prefixed to the title plus "Reason for cancellation:" |
| [Boston.gov public notices](https://www.boston.gov/public-notices) | Title (link) | After the title as "When October 28, 2026 9:30AM - 11:00AM" | title, 1-line description, When, Where, Posted, dept logo; 10 per page | title link only |
| [Boston Fleet "events list details"](https://patterns.boston.gov/components/detail/events_list_details--default.html) | Date flag "Nov 20" beside the title | A small flag with month + day, no year | title, When, Where, contact, audience, price, one button "See Events Details" | one button |
| [Chicago Councilmatic](https://chicago.councilmatic.org/) | "Next City Council meeting": date, time, location on separate lines, "Details" link; committees as one-liners "Wed 10/28 - Committee on Budget and Government Operations" | Weekday + numeric date first, no year | one line per committee meeting; no time on the one-liners | "Details" link; legislation rows carry "10/21/2026 - Referred" (date + action) |
| Documenters (documenters.org blocks automated reading; from [search snippets](https://charlotte-nc.documenters.org/assignments/board-meeting-8831/) and [City Bureau](https://www.citybureau.org/documenters)) | Agency, meeting name, date and time, a status word ("Canceled." near the top), add-to-calendar | Under the agency name | agency, title, when, where, status, documents | add to calendar; read notes |
| [GOV.UK summary list](https://design-system.service.gov.uk/components/summary-list/) (for the single-event page) | Key / value rows: "When", "Where" | In the value cell | one fact per row | an optional action link per row |

Common ground: the date is the anchor and sits left or above; the first words after it are the subject; the row is 2 to 4 short lines; there is exactly one link or button; a canceled item says so in its title; nobody shows a status badge at the end of the row; nobody shows filters before the first item on a phone.

### Sketch at 390px

```
Carver, MA                                   h1 (town = the question)
3 things coming up on solar and zoning.      one-line summary (≤160 chars)
[Tell me when this changes]                  one button, verb first

This week
──────────────────────────────────────────
TUE   Solar farm at 235 Main Street          date block left; subject first
 4    Planning Board, 7pm, Town Hall         who / when / where, one line
Nov   Public hearing. Anyone can speak.      what you can do, plain sentence
      The board may vote the same night.     the status, as a sentence
      Read the agenda (PDF) ›                one link, verb first
──────────────────────────────────────────
THU   Data-center ban (a moratorium)
 6    Select Board, 6:30pm, online
Nov   The board votes. No public comment
      is listed.
      Read the agenda ›
──────────────────────────────────────────
Later in November
──────────────────────────────────────────
TUE   Canceled: Federal Pond Solar hearing   "Canceled:" in the title
10    Planning Board. Moved to Tue 10 Nov    (Boston), old date once
Nov   because the applicant asked.
──────────────────────────────────────────
Nothing else is on an agenda yet. Agendas    empty-state in a sentence,
usually go up 5 days before a meeting.       not "0 items"
```

Rules embedded in the sketch: date block before the heading (USWDS calendar date; Boston date flag); week groups of six or fewer (USWDS); the subject in the first two words (NN/g); time inside the row, not as a heading (Boston events uses time-first rows under a day heading; on a phone, one row per meeting with the time inline is shorter); status as a sentence, with "Canceled:" the only prefix (Boston); a single verb-first link (GOV.UK links); "to" in ranges and no ordinals (GOV.UK A to Z); no year inside the next twelve months (Councilmatic, Boston date flag).

On a 1366px screen the same list keeps a 36em measure (USWDS: 45–90 characters, target 66) in the left two-thirds; filters, if any, move to a right-hand column below the summary, and the row's date block gets more room but nothing is added to the row.

---

## 3. Wording status, and plain-English replacements for our labels

What the systems do:

- GOV.UK: statuses are **adjectives, sentence case, the fewest possible**; the task that needs action is a coloured tag, the finished task is plain black text; red only for "There is a problem" ([Tag](https://design-system.service.gov.uk/components/tag/); [Complete multiple tasks](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/)). Verb-shaped tags ("Vote") read as buttons.
- USWDS: tags are for "new, important content" or filters; "Users frequently confuse tags as buttons"; "Don't overdo it" ([Tag](https://designsystem.digital.gov/components/tag/)).
- Boston.gov: no badge; a canceled event is "Canceled: Digital Literacy Workshop" with a "Reason for cancellation:" line ([events](https://www.boston.gov/events)).
- Councilmatic: a status word ("Active", "Passed") plus a dated action line "10/21/2026 - Referred" ([Chicago](https://chicago.councilmatic.org/)).
- City Scrapers / Documenters data model: four meeting statuses only: `cancelled`, `tentative`, `confirmed`, `passed` ([constants.py](https://github.com/City-Bureau/city-scrapers-core/blob/main/city_scrapers_core/constants.py)); the live pages print "Canceled." near the top of the meeting.
- Documenters write-ups: active verbs, "approved", "voted", the cancellation in the first sentence ([Outlier](https://outliermedia.org/newsletter/canceled-meeting-documenters-go-the-extra-mile/)).

So: **the status is a sentence in the row** ("The board votes on this Tuesday"), and a tag appears only when something has changed since the reader last looked (new, moved, canceled). "Vote" as a bare word is a verb-shaped tag, which both GOV.UK and USWDS warn reads as a button.

### Replacements

| Today | In the row (sentence) | If a short label is still needed | Note |
|---|---|---|---|
| Hearing | "Public hearing. Anyone can come and speak." | *Public hearing* | Say the right, not the procedure. "Hearing continues from Sep 23" → "The hearing continues; it started Sep 23." |
| Vote | "The Select Board votes on this Tuesday." | *Vote expected* | Name the board; adjective form for the label. |
| Possible vote | "The board may vote on this; the agenda doesn't say for sure." | *Vote possible* | Keep the hedge in words, not in a weaker colour. |
| Discussion | "The board talks about this. No vote is listed." | *Talk only* | Many readers read "Discussion" as a hearing. |
| Mentioned | "Solar comes up on the agenda, but nothing is set to be discussed or decided." | *Comes up* | Consider leaving these off the main list and showing them under "Also on agendas". |
| Moved to Nov 10 | "Moved to Tue Nov 10 (was Oct 27). The applicant asked." | *Moved* / *New date* | Say the new date once in the row; don't repeat it in a tag. |
| Canceled | "Canceled: Planning Board, Oct 27. The town canceled the meeting." | *Canceled* (prefix in the title, Boston style) | If only the item was pulled, say "taken off the agenda", not "canceled". |
| Withdrawn | "Withdrawn. The applicant pulled the request; nothing will be decided." | *Withdrawn* | Add who withdrew it. |
| New on an agenda | "First time on any agenda." | *New* | GOV.UK wants the smallest set; "New" alone is enough as a tag. |
| clean-energy permit rules | "rules for permitting solar and battery projects (the state's new consolidated permit)" | *Solar and battery permit rules* | Define "consolidated permit" the first time on each page. |
| 40B | "an affordable-housing project under state law 40B, which lets it skip some town zoning rules" | *40B affordable housing* | First use: the sentence; later uses: "40B". |
| Town Meeting warrant | "the list of articles Town Meeting will vote on (the warrant)" | *Town Meeting articles* | "Warrant not posted yet" → "The town hasn't posted the list of articles yet." |
| special permit | "a special permit (the board's case-by-case permission for a use the zoning allows only with conditions)" | *Special permit* | Pair with what is being permitted: "a special permit for a solar farm". |
| site plan review | "site plan review (the board checks the layout: parking, drainage, lighting; it can set conditions but not refuse the use)" | *Site plan review* | Say what the board can and can't do. |
| Notice of Intent | "a wetlands permit request (a Notice of Intent filed with the Conservation Commission)" | *Wetlands permit request* | Lead with the plain phrase; keep the legal name in brackets for people searching for it. |
| Filing | "The application is filed with the state; the Conservation Commission hasn't heard it yet." | *Filed, not yet heard* | |
| No time listed | "The agenda doesn't give a time." | — | A sentence, not a label. |

Spelling: Boston.gov and documenters.org both use "Canceled" (one l). Keep it.

---

## 4. Open-source pieces to adopt under a strict CSP, self-hosted fonts, no frameworks

The live site already serves `default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'`, one stylesheet (50 KB) and one deferred script (54 KB), with Barlow self-hosted as three woff2 files. Everything below fits that: copy CSS values and markup, serve fonts from `/fonts`, add no inline styles or scripts.

### Adopt

- **govuk-frontend type scale and spacing scale** (MIT licence for the code: "Unless stated otherwise, the codebase is released under the MIT License" — [repo](https://github.com/alphagov/govuk-frontend)). Type scale, large screens: 48/50, 36/40, 24/30, 19/25, 16/20; small screens: 32/35, 27/30, 21/25, 19/25, 16/20 ([type scale](https://design-system.service.gov.uk/styles/type-scale/)). Spacing scale, large/small: 5, 10, 15, 20/15, 25/15, 30/20, 40/25, 50/30, 60/40 ([spacing](https://design-system.service.gov.uk/styles/spacing/)). Write these as CSS custom properties; no Sass needed.
- **govuk-frontend summary list, tag, inset text and the "Start now" button**: CSS-only components; copy the compiled CSS for `govuk-summary-list`, `govuk-tag` (light background, dark text, sentence case, regular weight) and `govuk-button` from `dist/`, renamed to your own prefix. No JavaScript involved, so nothing to reconcile with the CSP.
- **USWDS tokens** (code is CC0 1.0 public domain; fonts and Material icons are the stated exceptions — [LICENSE.md](https://github.com/uswds/uswds/blob/develop/LICENSE.md)): font-size system tokens 13, 14, 15, 16, 17, 18, 20, 22, 24, 28, 32, 36, 40, 48 ([font-size](https://designsystem.digital.gov/design-tokens/typesetting/font-size/)); spacing units 4, 8, 12, 16, 20, 24, 32, 40, 48, 64 ([spacing units](https://designsystem.digital.gov/design-tokens/spacing-units/)); line-height tokens 1, 1.15, 1.35, 1.5, 1.62, 1.75 with 1.62 for reading text ([line-height](https://designsystem.digital.gov/design-tokens/typesetting/line-height/)); measure 45–90 characters, target 66 ([typography](https://designsystem.digital.gov/components/typography/)). Pick one scale (GOV.UK's or USWDS's), not both.
- **USWDS Collection markup** (`usa-collection__calendar-date` with a `<time>`, month and day spans, then heading and description) as the model for the meeting row; the condensed variant for the town page's "next door" list ([Collection](https://designsystem.digital.gov/components/collection/)). Copy the structure and the few CSS rules, not the whole `uswds.css`.
- **USWDS Summary box** (3–5 bullets, one heading) for the town page's "This month in Carver" ([Summary box](https://designsystem.digital.gov/components/summary-box/)).
- **Fonts, all SIL Open Font License 1.1, all self-hostable as woff2 from `/fonts`, all fine under `font-src` falling back to `default-src 'self'`:**
  - *Public Sans* — "A strong, neutral, principles-driven, open source typeface for text or display", fork of Libre Franklin, webfonts in `fonts/webfonts`; tabular numerals help times line up; note the repo says it "is not currently being actively developed or maintained" at v2.001, which is fine for a static font ([uswds/public-sans](https://github.com/uswds/public-sans)).
  - *Source Sans 3* — OFL-1.1, variable font available, releases on GitHub ([adobe-fonts/source-sans](https://github.com/adobe-fonts/source-sans)). Large x-height, narrow; the best match for the current Barlow look.
  - *Atkinson Hyperlegible* — "offering greater legibility and readability for low vision readers"; four styles (Regular, Bold, Italic, Bold Italic); OFL 1.1; repo archived, so pin the files you ship ([googlefonts/atkinson-hyperlegible](https://github.com/googlefonts/atkinson-hyperlegible)). Only two weights, no condensed; use it for body and UI if legibility is the priority, pair with nothing.
  - One family, two weights (400, 700) and italic if needed. Three files, same as today.
- **Structures (not code) from Boston Fleet and Councilmatic**: the date flag beside the title and the When / Where / one-button block ([Fleet events list](https://patterns.boston.gov/components/detail/events_list_details--default.html)); "Next meeting" as date, time, place on three lines with one "Details" link, and "date - action" lines for history ([Chicago Councilmatic](https://chicago.councilmatic.org/)).

### Do not adopt

- **GDS Transport** and anything that looks like GOV.UK branding (crown, black header, the GOV.UK blue/yellow focus style as a whole): "If your service is publicly available on a subdomain other than service.gov.uk, use an alternative typeface" ([Typeface](https://design-system.service.gov.uk/styles/typeface/)); GDS states the font is licensed for gov.uk domains only. Agenda Ahead also says on every page that it "isn't a government website"; looking like one would contradict that.
- **The USWDS JavaScript bundle and full `uswds.css`**: the JS expects its own init and the CSS is far larger than the 50 KB you ship; take tokens and two components' rules instead. Never add the USWDS "official government website" banner.
- **Boston Fleet CSS** (`patterns.boston.gov`): Boston-branded, licence not stated on the pages read; copy the arrangement, not the stylesheet.
- **Councilmatic itself**: a Django/Solr application, not a front-end you can lift; borrow its page shapes only.
- **Status-tag colour systems**: GOV.UK's eight tag colours exist for long task lists; here three states are the ceiling (needs you / changed / nothing to do).
- **Any CDN font or script** (Google Fonts, Tailwind, icon fonts): all blocked by the current `'self'` policy anyway, and nothing above needs them.

---

## 5. Five mistakes the current pages make against these rules

Measured at 390×844 (mobile) and 1366×900 (desktop) on 28 Oct 2026. Body font Barlow 18px / 27.9px line height; h1 32px on mobile, 40px on desktop; no horizontal scroll; no text under 14px. The typography is sound. The problems are order, wording and chrome.

**1. The list starts a screen too late.**
On `/upcoming` at 390px the first meeting (Boston City Council) begins at **874px**, below the 844px fold, after **543 words** of intro, counts ("60 items at 44 meetings in 37 towns."), "Checked Oct 28, 7:18 am…", a By date / Biggest stories switch, a grey filter box (County, Topic, Town, Show: Titles only / With details) and a "What the labels mean" link. At 1366px the first row starts at 661px. The home page's first "This week" item sits at about 650px on mobile after the town box, the "Or try…" line and "Free, no account…". Rules broken: GOV.UK "Put the most important information first"; NN/g F-pattern ("First lines of text on a page receive more gazes"); USWDS summary box ("key information at the top", digital.gov design guide). Fix: h1, one-sentence summary, then the first row inside the first 400px; filters below the first group or in a side column on desktop.

**2. Rows are database records, not sentences.**
A row on `/upcoming` reads, in order: `12 pm · Boston · City Council / Council Chambers / Agenda / Discusses battery storage / ○ Discussion`. The subject comes fourth, as a link; the status is a noun with a filled or hollow dot at the end; place comes before the matter; the "Agenda" link is repeated **49 times** on one page with different hidden suffixes (GOV.UK: "do not reuse the same link text to link to different pages"). Each row is a bordered card **178px** tall on mobile, so about four fit a screen, for perfectly homogeneous items (NN/g: use "a standard vertical list"; USWDS: "Don't use a card as a substitute for a table row"). **103 tap targets under 32px** on the page, 15 on a town page. The rows also quote agendas raw: "Discusses a zoning change: 'Not all items listed may in fact be discussed and other items not listed may also be discussed to the extent permitted by law AGENDA Approach & Schedule for Zoning Bylaw Amendments'" (Hull). Fix: date block, subject first, one sentence, one verb-first link; quotes only behind "Agenda wording".

**3. Labels are code words, explained somewhere else.**
"Hearing", "Discussion", "Mentioned", "Possible vote", "Filing", "New on an agenda", "Moved from Oct 21", "ZBA hearing", "40B", "moratorium", "Notice of Intent" appear bare in rows; the definitions sit behind a "What the labels mean" disclosure (four `<details>` on `/upcoming`, one on each meeting page) and on `/how-it-works`, which is the FAQ pattern GOV.UK says not to use. Verb-shaped tags ("Vote") read as buttons (GOV.UK Tag: "Use adjectives… not verbs"; USWDS: "Users frequently confuse tags as buttons"). The same fact is often shown twice in two forms: the Carver row says "wetlands hearing continued to Nov 4" in the sentence and "Moved from Oct 21" in a tag; the Nov 10 row says "Postponed: … moves to Tue Nov 10" and tags "Moved from Oct 27". Fix: section 3's sentences; the term explained on first use in the row; one tag at most, only for change.

**4. The pages talk about the system, not the reader.**
Above the content on every page: "Checked Oct 28, 7:18 am from the agendas towns post online." Counts as the lead sentence: "60 items at 44 meetings in 37 towns.", "16 items at 15 meetings coming up in 15 towns.", "351 towns, 243 checked every morning". The Carver summary is one 56-word paragraph: "Nothing coming up on solar, battery storage, data centers, moratoriums, clean-energy permit rules, zoning changes, affordable housing, cell towers or wetlands permits. Most recent: Tue Oct 27, Planning Board: … The next agenda we know of: Select Board, Thu Oct 29." The "Next door" list shows crawler diagnostics to residents: "Middleborough Can't read yet (website blocks automatic reading)", "Granby Can't read yet (agendas posted without dates)". Controls are named for the data model: "Titles only / With details", "Copy citation", "Agenda wording". Rules broken: GOV.UK right tone (write "as if speaking one-to-one"; "brisk, but not terse"), clear language (25-word sentences, 5-sentence paragraphs), NN/g "half the word count", the newsletters' habit of five items and no counts. Fix: one plain lead ("Nothing is on Carver's agendas this month. The last item was the solar farm hearing on Oct 27."), the checked-time in the footer, "Can't read yet" reduced to "No agendas we can read" with the reason behind a link, and counts removed unless the number is the news.

**5. The meeting page and the follow page don't lead with the decision or the action.**
On `/m/somerset-board-of-selectmen-2026-10-28` the h1 is the board ("Somerset Board of Selectmen"); then a grey summary box (When, Where, Public comment, Agenda); the actual matter, "A temporary ban on new data centers (a moratorium): vote", appears after about 90 words and below the fold on mobile. "Public comment: No public hearing on these items. The agenda doesn't say whether the board takes comments on them." is a shrug where the reader wants "Can I say something? Yes/No/Unknown, and how". The follow box repeats the button label twice ("Follow Somerset" heading, "Follow Somerset" button) and describes the output as "A private page and a calendar feed", which is the system's view; the reader's view is "tell me when this town is about to decide something". On `/watch` the page is sound in shape (one question, one Continue) but the heading "Which town?" is a question (GOV.UK: "users want answers, not questions") and nothing says what arrives, in what form, or how often, before the person commits (GOV.UK start page: tell users what the service does, cost and time; email pattern: "Make it clear what the email address will be used for"). Fix: h1 = the decision ("Somerset may ban new data centers"), first line = when and what the board does, second = whether you can speak, then the summary list, then "Tell me if this changes" as the one button with a sentence saying what you'll get.

Smaller things seen on the way: date formats differ within a page ("Wed Oct 28", "Oct 28, 7:18 am", "6 pm", "Sep 23", "(first seen Oct 27)"); the home page explains itself twice ("Every morning we read…" in the body and again in the footer); the "Biggest stories" tab has no explanation of what makes a story big; "No time listed" is a label where a sentence belongs.

---

## Summary

1. Lead every page with the decision in one plain sentence; counts, checked-times and filters go below the first group or into the footer.
2. The meeting list is a plain vertical list, not cards: date block left, subject in the first two words, one sentence, what you can do, one verb-first link, six or fewer per group.
3. Status is a sentence ("The board votes on this Tuesday"); a tag appears only for change (New, Moved, Canceled), as an adjective in sentence case; "Canceled:" prefixes the title as Boston.gov does.
4. Explain every term the first time it appears in the row (40B, moratorium, Notice of Intent, special permit); retire "What the labels mean" and the FAQ on /how-it-works.
5. Write to a reading age of about 9: sentences under 25 words, "you" and a named "we", active verbs, no system talk ("website blocks automatic reading", "Titles only / With details", "Copy citation").
6. Meeting page: h1 = the decision, then when / can you speak / where as a summary list, then one button worded as the action.
7. Follow page: say what arrives and how often before asking for anything; one question per page; heading is a statement, not a question.
8. Adopt govuk-frontend's type and spacing scales plus its summary list, tag and button CSS, or USWDS's tokens, collection and summary box, as copied CSS values; all MIT/CC0 and CSP-safe.
9. Fonts: Public Sans, Source Sans 3 or Atkinson Hyperlegible, all OFL 1.1, self-hosted as two or three woff2 files like Barlow today; never GDS Transport, never GOV.UK or USWDS government branding.
10. Current pages measured at 390 and 1366: first meeting at 874px on mobile after 543 words; 49 identical "Agenda" links and 103 sub-32px targets on /upcoming; 178px cards for homogeneous rows; crawler diagnostics shown to residents; meeting page leads with the board, not the decision.
