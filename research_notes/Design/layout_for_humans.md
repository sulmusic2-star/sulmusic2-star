# Layout for humans: Agenda Ahead

Measured Oct 16, 2026 at 1366×900 and 390×844 in Chromium; screenshots and `measure.json` sit beside this file. It builds on `style_director.md` (Oct 13).

## What "scattered" is, measured

Three things, on every page.

1. **Two right edges.** Content runs x 123–1243. Paragraphs stop at 540–680 px, but H1s, H2s, rules, meta lines and tables run to 1243. On /topics/solar one venue line is 1,075 px (about 115 characters) over a body that wraps at 540. Each item is a 650 px block with a 1,120 px underline.
2. **The status word floats.** `.line-say` gives it an `auto` column, so its x depends on the word's length: 10 x positions on /topics/solar (548–728), 7 on /upcoming, 7 on /ma/carver. Nothing lines up down the page.
3. **Dates repeat; spacing is off the scale.** /upcoming prints a date 75 times for 8 days ("Mon Oct 19" 32 times). The left column of /upcoming, /topics/solar and /ma/carver has 21–22 distinct vertical gaps (5, 9, 31, 49, 55 px), from `min-height: 44px` on inline links and `--s1` margins on 16 px text.

## Five rules

1. **One grid, one left edge.** GOV.UK: "Your main content should always be in a two-thirds column" (design-system.service.gov.uk/styles/layout/). The weather.gov zone forecast starts every period at the left margin and wraps flush left (forecast.weather.gov ZFP). Fixations concentrate "at the top and the left side of the page" (nngroup.com/articles/f-shaped-pattern-reading-web-content/). Here: every page uses `.page-grid` (720 + 80 + 320) or the list grid `7rem | minmax(0,46rem) | 9.5rem`. Nothing is one column 1,120 px wide.
2. **Group by day; print the day once.** The Massachusetts court daily list prints "Monday, October 19, 2026" once and lists each matter under it as time, event, session (mass.gov, Suffolk Juvenile Public Daily List); Patch's calendar does the same. Scanners read headings and skip bodies: the "layer-cake" pattern, "by far the most effective way" to scan (nngroup.com/articles/text-scanning-patterns-eyetracking/). Here: a day heading, then rows that begin with the time.
3. **A box or rule is earned.** "In many situations it's enough to rely on proximity"; borders "overpower other grouping principles" (nngroup.com/articles/common-region/). "Do you really need a rule or border? … increasing the space above and below the text. Try that first" (practicaltypography.com/rules-and-borders.html). "Erase non-data-ink" (Tufte via Stasko, faculty.cc.gatech.edu/~stasko/7450/13/Notes/tufte.pdf). "Borders help many users find and read information that's laid out in rows" (GOV.UK summary list). Here: one rule per day group and per table row; one tinted block per page, the ticket; no pills.
4. **Spacing from the scale only.** GOV.UK's scale runs 5–60 px and "adapts based on screen size" (design-system.service.gov.uk/styles/spacing/). "Limit how many elements are big to a maximum of 2" (nngroup.com/articles/visual-hierarchy-ux-definition/). Here: the director's rhythm (4–8 inside an item, 24 between items, 48 between meetings, 64 between sections) and nothing else; tap height is padding on the link, never `min-height` on the row.
5. **One measure.** "No more than 75 characters per line" (GOV.UK layout); "45–90 characters, including spaces" (practicaltypography.com/line-length.html). Here: `--measure: 64ch` on every running-text block and meta line; no table text cell under 45 characters.

(nytimes.com, bostonglobe.com and bbc.co.uk are blocked from here; the court list, zone forecast, Patch and the MBTA timetable, mbta.com/schedules/CR-Providence/timetable, stand in.)

## Page by page

**Home.** Already two 520 px halves. Phone: cut the 100 px between "Or try" and "This week" to 48 (`.next { margin-top: var(--s7) }`). The "New" badge moves headline starts from x 851 to 898; remove `.badge-new` and say "new" in the meta line.

**/upcoming, with write-ups.** Before the first item the eye passes seven stacked blocks of seven widths (select 142, paragraph 609, button 232, topic links 627, tabs 246, H2 1,120), and the right half is empty for 40,000 px. Sketch:

```
Coming up
[County ▾] [Topic ▾]   With write-ups | One line each
Mon Oct 19
7 pm   Belchertown · Conservation Commission             ○ Discussion
       Tower Road solar project in Pelham: conservation update
       Town Hall Auditorium, 2 Jabish Street
10 am  Dover · Planning Board                            ○ Discussion
```

CSS: `.meeting { display: grid; grid-template-columns: 7rem minmax(0,46rem) 9.5rem; column-gap: var(--s5) }`: time, text, `.stage` in columns 1–3, so every status shares one x. `.meet-head` loses the date; `<h3 class="day">` carries it: `font: 700 var(--t-h3) var(--f-head); border-top: 1px solid var(--rule); padding-top: var(--s4); margin-top: var(--s7)`. Delete `.meet-place::before` (the stray "·"). Intro to one sentence; "Get alerts for your town" under the filter row at `.btn` width.

**/upcoming, one line each.** A "line" is three lines and a rule today (148–272 px per meeting; 15,302 px page). Use the `.row a` grid: `7 pm | Egremont · Planning Board — Planning Board discusses new state clean-energy siting rules | ○ Discussion`, the Agenda link only on the meeting page, day heading once. `.meetings.one .meeting { grid-template-areas: "when line stage" }`.

**/ma/carver.** Four lines in three greys precede the first headline (board, date, "· Meeting Room…", speaking rule). Replace with the director's ticket line: `Wed Oct 21, 7 pm · Conservation Commission` in SC 22 ink, place on its own 16 px line, rule after. `.line-say { grid-template-columns: minmax(0,1fr) 9.5rem }` puts every status at x 691. The three grey fact lines become a summary list: `<dl class="facts">` with `grid-template-columns: 7rem 1fr`, keys "Topics / Parcel / Applicant" muted 600. Rail: alerts button first, full width, "Next door" under it. The rail starts at y 208, the H1 at 150: `grid-template-areas: "head rail" "main rail"` so the button tops out with the H1.

**/m/carver-conservation-commission-2026-10-21.** The clearest page; keep it. The ticket's rule is at y 208, the first headline at 225: `.page-grid .meeting:first-child { padding-top: var(--s5) }` so headline top meets the ticket's text top. Facts become the same `<dl>`.

**/topics/solar.** The "Get alerts" button sits 780 px from its heading (`.sec-head` uses `space-between`). `.sec-head { justify-content: flex-start; gap: var(--s5) }`. Then the /upcoming grid and day headings, which also ends the 1,075 px venue line (column 2 is 46rem) and the ten status positions.

**/attorney-general.** The table is 1,120 px with 145 px rows for two lines of text, a pill that wraps ("Approved, often with some parts / struck") and links on 44 px lines. `table.stack th, table.stack td { padding: var(--s3) var(--s4) var(--s3) 0; vertical-align: top } .stack a { min-height: 0 }`; widths `5fr 3fr 2fr 3fr`; outcome as bold text, no `.badge`. Paragraphs to 64ch (measured 678 px, about 82 characters).

**/attorney-general/rulings.** Five filter controls at five widths (89–473 px) on two rows, "143 of 143 shown" floating at x 971, then a five-column table whose summary column is 273 px (about 32 characters), so rows average 219 px and the page is 32,191 px. Filters: one row, `.filterbar label { flex: 1 1 10rem }`, count under it at x 123. Table: three columns `8rem | 1fr | 11rem` (Date | town, article, type, summary at 64ch | outcome as bold text), grouped by year with the year printed once as a `<th scope="rowgroup">` row.

**/search.** Twelve control widths on one page; open filters take 431 px, then the count, a tip line and an outlined button before the first result at y 878, with no heading. Order: search box; "Meetings still ahead first" under it; filters closed when results exist (`details.filters` without `open`); on desktop five equal selects in one row (`grid-template-columns: repeat(5, minmax(0,1fr))`); the count as the results heading ("123 agendas · 9 upcoming first"). Drop the outlined "Get alerts" button; the nav has it.

**/watch.** Three widths at one edge (text 630, input 560, button 119) and an empty right half. `form { max-width: 36rem }`, input at 100%; "Which town?" becomes the input's label; "Alerts are free…" sits under the H1.

**/towns.** Three county columns (x 135, 519, 903) with two left edges inside each (name 165, count 158), and the state's count at 123 under a name at 145. Put the count on the name's line in muted ("Barnstable County · 15 towns, 3 we can't read yet"): `.county > summary .sub-count { flex-basis: auto; padding-left: 0 }`, which halves the height. Input capped at 36rem.

## Refuse

Hero photos. Cards for everything: "card layouts are less scannable than lists", and for "very homogenous items… a standard vertical list" (nngroup.com/articles/cards-component/). Icons per topic or board. Tinted boxes beyond the ticket, including outcome pills and the "New" badge. A rule under every element. Centred headings or text ("Whole text blocks should not be centered", practicaltypography.com/centered-text.html). A fourth font, a second accent, and everything on the director's refuse list.
