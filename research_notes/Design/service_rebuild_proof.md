# Agenda Ahead as a public service: the proof (Nov 6, 2026)

This is the proof the spec (`service_spec.md`, section 4) asks for, run against the site as `python3 build.py` wrote it on Nov 6, 2026 (1,565 pages: 1,245 town pages, 7 state pages, 141 meeting pages, 2,433 agenda hits), after the coordinator's five fixes of the same day. The numbers come from the scripts in `service_rebuild_checks/` (`words.py` for the visible word counts, `proof.py` for the greps, `questions.py` for the rows that speak to the reader, `shots.cjs` for the screenshots, the overflow check and axe). The screenshots are in `service_rebuild_shots/`.

## What was built

Rows. A row is the agenda's own line for its main item, then one meta line, then the source link. The line comes from the agenda passage we hold for the item (the write-up's quote, the classifier's item text, the quotes, the snippet), with numbering, bullets, times, clerk's labels ("Purpose:"), leading asides and section headings ("Old Business", "Public Hearing:") stripped, the clerk's dashes and pipes turned into commas, all-capitals lines put in sentence case, the legal tail cut at the first connector ("pursuant to", "in accordance with", "under Section", "as required by", a "located at" that only cites a parcel), the result trimmed to about 90 characters at a comma or semicolon when one sits in the second half, else at a word, and never ending on a function word. A passage that gives no clean line (it starts mid-word or inside a closed quotation, has no word for what it is about, is a table header, a file name, minutes narrative or table cells run together) falls back to the old computed subject. The meta line is the label as its own short sentence, then the facts in commas: town, board, day, time or "time not yet posted", place, "2 more items". Nothing is composed into a sentence any more; `meeting_row`, `stage_sentence`, `meeting_paragraph`, `explain_terms` and the speak lines are no longer called by any page.

Continued items. When an agenda itself moves an item to a later day that has no agenda yet, the item is listed under that later day as its own row, "Continued from Nov 10", with "time not yet posted" and the earlier agenda as its document, and gets its own meeting page and calendar file (`split_moved()`, `virtual_all()`). The earlier meeting keeps its other items under its own day; a meeting whose every item moved reads "Continued to Dec 8" and sits with the recent ones on the town page. On a meeting page the "Public hearing" value is "Public hearing continued to Dec 8" (or "Continued to Dec 8" when it is not a hearing), "Public hearing continued from Nov 10" on the later day's page, "Continuance asked, to Dec 8" when the applicant asked and the board has not said.

Pages, per spec section 2: the home page (question, one line, the town box, the week's subjects with counts, the states); state pages at `/ma`, `/ny`, `/ri`, `/va`, `/md`, `/mi`, `/oh` ("Next 7 days" by day, then "Later" by day, then the link to the state's places); the town page (name, Follow button, Coming up, Recent, next door, source; the inset line and request form for a place we can't read; the via-county line and the county's rows for a township read through its county); the meeting page (headline, summary list, the agenda's words, the other items, a continued one marked); `/towns` (search box, each state's places in one run of links, unread ones marked); `/upcoming` (state and subject checkboxes, "Next 7 days" by day, then "Later meetings (N)" folded in a details element so a phone page is one screen of days, not twenty thousand pixels); topics, trending, search, follow, about, how it works and the rulings pages restyled with one-line or no intros. The maps, the stories, the masthead date, the brand mark, the program note and the footer columns are gone.

Look, per spec section 3: `site/styles.css` is rewritten to the GOV.UK values (the Helvetica/Arial stack, 19px/1.32 body and 16px under 640px, 48/32px H1, 27/24px H2, 19px H3, the colours listed in the spec and nothing else, the 5 to 50px steps, 960px frame with 15/30px gutters, a two-thirds content column, the black bar, the service menu under it, the text input, the green button, the summary list, the inset text, the back link, the details, the checkboxes, plain lists, rows with a 1px #b1b4b6 rule). No font files are loaded; `site/fonts` stays on disk. The favicon, the Apple touch icon (`tools/icons.py`) and the share image (`tools/og_image.py`) are a black square with a white A and the same type and colours.

## Visible word counts

Counted with `words.py`: the text a visitor sees, with hidden, offscreen and screen-reader-only text left out and a token with no letter or digit (a comma between two links) not counted as a word.

| Page | Limit | Count |
|---|---|---|
| `/` (home) | 80 | 78 |
| `/ma/carver`, everything outside the rows | 40 | 38 (157 in all, 4 rows) |
| `/m/carver-planning-board-2026-11-10`, everything outside the headline, the summary values, the excerpt and the item list | 30 | 29 (114 in all) |
| `/m/carver-planning-board-2026-12-08` (the continued item's page), the same | 30 | 25 (105 in all) |
| `/ma/abington` (a town we can't read) | none | 43 in all |
| `/mi/adrian-charter-township` (read through its county) | none | 77 in all |
| `/ma` outside the rows | none | 70 (71 rows) |
| `/upcoming` outside the rows | none | 114 (141 rows) |
| `/towns` | none | 3,773, the names of 1,245 places and their state headings |

The home page's 78 words: Agenda Ahead; Coming up, Places, Search, Follow; the question; the one line (24 words); Town or county, Search; the This week line (20 words, seven subjects with counts); the state line (13 words); Not a government website. About.

## Greps over site/**

`proof.py` over all 1,424 HTML pages:

- Rows: 1,341. Rows containing "we", "We", "It's a", "The town hasn't", "so anyone" or "no vote is listed": **0**. (Before the junk-headline rule, one row, `/ma/yarmouth`, carried the clerk's line "Potential 2027 Annual Town Meeting (ATM) Zoning Amendments As we head into the final…"; that line's first eight words hold none of the small function words, so it now falls back to the computed subject. The rule, not the "we", removed it.)
- Pages with `<svg class="map`: 0.
- Pages loading `/fonts/`: 0.
- "we" inside `<main>` on the content pages (home, the seven state pages, every town and meeting page, `/towns`, `/upcoming`; 1,396 pages): 457 instances of the spec's own line "We can't read X's agendas yet: …", and 0 others. The reason phrases that used to say "a system we can't open yet" and "the website we found belongs to another place" now say "an agenda system no program can open yet" and "the website listed for it belongs to another place".

Headlines: 112 of the 141 meeting pages (and the same 112 of the 141 rows on `/upcoming`) carry the agenda's own line; **29 fall back** to the computed subject (before the junk rule: 12 of 136). The rule rejects, as asked, lines that start with She, He, They, Mr., Ms., Mrs., Dr., "The Board voted", "Motion by", "Proof of", "Correspondence" or "Approval of Minutes", lines that hold said, stated, noted, addressed, asked, moved, seconded, discussed or reported, and lines of eight or more words whose first eight hold none of the, of, for, to, a, an, and, on (the set was widened with by, or, in, at, with, from, as, is, so that "Discussion by Council, Vote or Other Action Regarding an Emergency Ordinance…" still stands). The fallbacks now: three "Cell towers", two "Zoning change", two "Request to rezone 1945 Jackson Road", two "Data-center rules", "Variance for a data center at 1 Railroad Avenue", "State's new permit process for small clean-energy projects", "Special permit and site plans for a cell tower at 12 Dudley Road", "Solar and battery storage ordinance", "Solar", "Site plans for a cell tower on Hilltop Ct", "SBA Network Services's hearing at 677 Timpany Blvd", "Request to rezone 68 Church Street", "Proposal to prohibit battery storage and data centers", "Mount Solar's hearing at 575 Nanaquaket Road", "Draft data-center bylaw", "Data centers", "Beacon Solar at 50 Florence Road", "Battery storage rules", "Affordable housing project by Friendly on Washington Street", three "Affordable housing permit (40B)…" subjects, "Affordable housing", "40 homes, 10 affordable, at 24 Bancroft Street (Woodland Ridge 40B)". Some of what the first-eight-words rule rejects was a fair agenda line ("Beacon Solar, LLC, 50 Florence Road (MassDEP File # 151-314) for the large-scale solar project", "The Board…" aside); the rule is kept as asked. No headline ends on a function word (0 of 141). "Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review" now ends where the legal tail began.

Rows whose headline is a question or speaks to the reader (`questions.py`; the clerk's words, listed and not changed): eight. "I've started drafting a zoning ordinance How does this relate to Data Centers?" (`/ma/greenfield`); "Use Table; 6. AI data center moratorium?" (`/ma/leyden`); "These amendments make our zoning bylaws consistent with the Affordable Homes Act and 760…" (`/ma/wellfleet`); "I further move that: The proposed zoning amendment revise Sections 17.50.120…" (`/ma/winthrop`); "Potter Can I burn leaves Zoning check" (`/mi`, `/mi/clinton-county` and two more); "On August 18, 2026, I requested records concerning Hail No Los Alamos Data Center…" (`/mi/ypsilanti-charter-township`); "6 Too many apartments building constructed on the old AMA property I oppose AI Data…" (`/ny/st-armand`); "Solar Ordinance Draft with I-1 Wellness Centers, Boutique Hotels" (`/va/gloucester-county`, the "I" is a zoning district). The script also lists "Gibson Solar I, LLC" and "Article I", where the "I" is a numeral, not the reader.

The labels in use across every row on the site, with counts: Discussion 593, Public hearing, anyone can speak 401, Vote 55, "Continued from" a named day 27, Discussion, public comment 25, Continued hearing 20, Vote, public comment 16, Filed with the state 9, Canceled 9, Possible vote 8, Continued, no date given 8, "Continued to" a named day 4, Possible vote, public comment 3, Withdrawn 2, Continuance asked 2; 18 rows on `/upcoming` carry no label (the subject comes up in the agenda's words with nothing listed to discuss or decide).

## Screenshots, overflow and axe

`shots.cjs` with Playwright's Chromium at 390×844 and 1366×900, device scale 1, full page, then `document.documentElement.scrollWidth > clientWidth` and axe-core 4.10 (wcag2a, wcag2aa, wcag21aa, best-practice). Results in `service_rebuild_shots/axe-results.json`: 34 checks, 34 with no violations, 0 with horizontal overflow at 390.

The spec's eight pages and the continued item's page, both widths, in `research_notes/Design/service_rebuild_shots/`:

- `home-390.png`, `home-1366.png` (`/`)
- `ma-390.png`, `ma-1366.png` (`/ma`)
- `ma-carver-390.png`, `ma-carver-1366.png` (`/ma/carver`)
- `m-carver-planning-board-2026-11-10-390.png`, `m-carver-planning-board-2026-11-10-1366.png` (a meeting page)
- `m-carver-planning-board-2026-12-08-390.png`, `m-carver-planning-board-2026-12-08-1366.png` (the page for the item continued to Dec 8)
- `ma-abington-390.png`, `ma-abington-1366.png` (a town we can't read)
- `mi-adrian-charter-township-390.png`, `mi-adrian-charter-township-1366.png` (a township read through its county)
- `towns-390.png`, `towns-1366.png` (`/towns`)
- `upcoming-390.png`, `upcoming-1366.png` (`/upcoming`)

The same run also checked `/trending`, `/search`, `/watch`, `/topics`, `/topics/solar`, `/about`, `/how-it-works` and `/attorney-general` at both widths: zero violations and nothing wider than the screen (those shots stayed in the session's scratch folder). A browser drive (`drive.cjs` in the scratch folder) typed "carv" in the town box and went to `/ma/carver` on Enter, ticked Massachusetts and Data centers on `/upcoming` (12 of 141 meetings, the address bar carrying the choice, the Later fold recounting), opened `/upcoming?state=RI` pre-ticked, filtered `/towns` for "plymouth" (27 of 1,245 places), added Carver on `/trending` (2 stories), and reached step two of `/watch`, with zero console errors.

## Lint

`python3 .claude/skills/de-slop/scripts/slop_lint.py` on the nine pages above: score 2 over 10,186 words, two hits. One is `heading-question` on the home page's H1, "What is your town about to decide?", which is the spec's own heading. The other is `title-case` on "Adrian Charter Township, Michigan", a place name (the known false positive). The agenda's own lines carry `data-slop-ignore`, because they are the clerk's words, not ours; the computed fallback subjects do not, and are linted. `site/styles.css`: clean. This note: clean.

## Tests and build

`python3 build.py`: passes (1,565 pages). `tools/test_dates.py` 11 tests OK, `tools/test_briefs.py` 32 OK, `tools/test_replaced.py` 6 OK, `tools/test_trending.py` 36 OK. The three render tests in `test_briefs.py` asserted the old sentences ("Asked to move" beside a writer's line, the "Speaking:" line, the "Agenda wording" fold); they now assert the new rows with the same intent: a verified brief's item shows the agenda's own line as the headline, "Continuance asked" as its label and on its meeting page, no composed sentence, and its exact quote on the meeting page; a live hearing carries "Public hearing, anyone can speak" and the meeting page answers "Yes, anyone can speak"; without a brief the rules' reading gives the label and the snippet's sentence is the quote. A fourth test covers the continued item: "Continued to Oct 27" on the Oct 13 row and page, and the item listed again under Oct 27 as "Continued from Oct 13", time not yet posted, with the Oct 13 agenda as its document.

## Departures from the spec

- Labels: the spec's fixed words are used, plus a few more fixed words the agendas need: "Possible vote" (the agenda allows a vote without promising one), "Withdrawn", "Filed with the state" (a wetlands filing, not a meeting), "Continued hearing" (continued, with no earlier day printed), "Continued to Dec 8" and "Continued, no date given" (the agenda itself moves the item), "Continuance asked" (the applicant asked; the board has not said), and ", public comment" after a label when the agenda lists a public comment period. Each is a label or a fact, never a sentence.
- "Time not yet posted" sits inside the comma list as "time not yet posted" (in the time's place), rather than as a sentence of its own, so the meta line stays one line.
- The meeting page's summary list has no Town row; the Board value says "Carver Planning Board" and the back link above the headline is the town's name, so the town is on the page twice without a row of its own.
- The town page shows two Recent rows (a meeting whose every item moved to a later day counts as recent) and nothing older; the earlier meetings, the state's rulings on the town's bylaws and the news links that used to sit on the page are gone from it (the rulings keep their own pages; older agendas are on `/search`).
- State pages and `/upcoming` group by rolling days, "Next 7 days" then "Later", not by the spec's "This week" and "Next week": on a Friday the calendar week read as empty.
- The home page's subject line lists the spec's seven subjects. Clean-energy permit rules and wetlands permits are not on it (the 80-word budget); they are on `/topics` and `/upcoming`.
- The spec's home page names only the black bar; without any way from it to Coming up, Places, Search or Follow, the site would be hard to operate, so a GOV.UK service-navigation menu with those four entries sits under the black bar on every page, and the footer carries one link, "About". These are counted in every word count above.
- The via-county line names the body ("Lenawee County Planning Commission") and links it to the county's page.
- Alert pages (`/w/<key>`, drawn by `site/w.js`) still render items client-side in the earlier item format with their stage words; their headline is now the agenda's own line (from `lines.json`) and they take the shared stylesheet, but they were not rebuilt as rows. The search page's results (`site/search.js`) keep their own result rows, styled plainly.
- `data/trending.json` now carries each story's row as built (`html`) and no longer the `subject`/`say` sentences; `trending.js` redraws from it. `lines.json` `lines[id][0]` is the agenda headline. ARCHITECTURE.md describes both.
- Headline quality is the agenda's: a few lines are still tables, notice fragments or ordinance text ("Lighting. The Energy Storage Facility shall implement dark sky friendly lighting solutions", "Proposed zoning language is shown in red", "Stone Farm Subdivision, process update, A) subdivision, Kevin and B) sizing…"). They are the clerk's words and pass the checks; a better passage for them would have to come from the crawler or a write-up.
