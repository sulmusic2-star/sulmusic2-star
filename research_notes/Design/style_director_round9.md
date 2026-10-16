# Style director, round 9 (Oct 16, 2026, evening): the layout rebuild measured

The style director's fourth read, after the site was rebuilt against `layout_for_humans.md`. Measured in Chromium at 390 and 1366 px, light and dark; 92 screenshots in the session scratchpad (`value-test/round9/style/`). Scores: taste 9/10, usability 8.5/10 (round 8: 8.5/8.5). What the same evening fixed from the list at the end is in `tester_round9.md`.

---


Style director review, Oct 16, 2026, against my spec, rounds 6–8 and today's `layout_for_humans.md`. Chromium at 390 and 1366 px, light and dark; 92 screenshots in `value-test/round9/style/`.

## 1. Verdict

The lists scan like a results table now. Every status word on a page sits at one x: 98 of 98 on /upcoming (843), 74 on /topics/solar, 19 on /ma/carver (691, as predicted), where there were 7 to 10 positions. Each day prints once: /upcoming's ten visible dates print ten times, where "Mon Oct 19" alone printed 32. The frame on /upcoming ends at x 995 for H1, rules and status column; nothing is 1,120 px wide except the two Attorney General tables. The one-line view is one line, `10 am | Egremont · Planning Board: headline | ○ Discussion`, 50 px for 60 of 85 meetings at 1366, 8,031 px a page (15,302). Dark mode is the spec to the digit. What pulls it back: /topics/solar ignores the one-line preference, search still puts past meetings first, /ma/carver prints "Wed Oct 21" three times before its first headline, and the new data-center ledger is a seven-column table whose date columns mostly say "Not yet". **Taste 9/10, usability 8.5/10.**

## 2. Measured

- Vertical gaps, left column at 1366: /upcoming 14 distinct (21–22 before), 1,053 of 1,065 on the scale, the strays 5 px (headline to summary), 44 and 52; /topics/solar 12, /ma/carver 9, one-line view 8, meeting page 5.
- Right edges at 1366: /upcoming two (text 799–843, frame 995); /ma/carver three (843, 995, rail 1243); AG pages two (lead 735, table 1243).
- At 390 a one-line meeting is 131 px: time, headline and status stacked.
- /attorney-general/rulings 20,671 px (32,191); the ledger 17,585, 51,708 at 390.

## 3. The round-8 six

1. **Five links on phones: landed**, 109 px.
2. **Who-votes line, copied list: outside today's pages.**
3. **One-line view: landed on /upcoming**, not on /topics/solar. The filter is a County select; no saved towns.
4. **/watch: landed.** The site's listbox; button last.
5. **Measure: landed.**
6. **Search: half.** Filters closed by default. But "Meetings still ahead first" carries `checked` in the HTML and the script unticks it on load: for "solar" in Carver and Plymouth the first upcoming result is sixth. The count is a grey paragraph, not a heading.

## 4. The layout spec, page by page

- **Home: landed.** H1 and "This week" both at y 110; the badge is gone; "New to this town" sits in the meta line at 600 ink, outweighing the board name. Phone: 84 px above "This week", not 48.
- **/upcoming: landed**, except the head: six stacked blocks of five widths before the first item at y 593.
- **/ma/carver: half.** The rail starts at 208 with the H1 at 150, the button stays in the main column, and the date arrives as "Next meeting on our list: Conservation Commission, Wed Oct 21, 7 pm.", then "Wed Oct 21", then "7 pm · Conservation Commission".
- **Meeting page: kept**; headline 224, ticket text 235, still 11 px apart.
- **/topics/solar: half.** `.sec-head` gap 24, day headings; no switch.
- **/attorney-general/rulings: half.** Five equal controls on one row, count at x 123, outcome as bold text, summary column 470 (273), rows 139 (219). Still five columns, no year groups; on a phone the stacked cells lack the ledger's labels.
- **/towns: landed.** Three county columns, the count on the county's line.
- **/watch: half.** Form still 872 wide, input 560, button 119.

## 5. New today: the data-center ledger

Bold status words, no pills, a "How sure" line per row: right. Seven columns in 1,120 px, rows 264 px tall at 1366 and 799 at 390: wrong. The "Attorney General" column is 78 px, so "Sep 24, 2026, case 12422" takes four lines; "Adopted" says "Not yet" 54 times in 63; 139 links are "Source 1" to "Source 6" where the rulings page names its letters.

## 6. What reads generated

- Three speaking-rule stamps cover 33 of 57 meetings on /upcoming: "Public hearing: anyone can attend and ask to speak. The agenda prints no other rule." ×12, "Town Meeting: the town's voters decide…" ×12, "The agenda has a public comment period…" ×9.
- "How sure: high/medium/low." ×63.
- "Egremont · Planning Board: Planning Board discusses…": the board twice, and the prefix is a `::before`, uncopyable.

## 7. What to refuse

Cards for the ledger on phones; labels are enough. Colour for "How sure". A pill for "New to this town". Icons on Source links. A sticky filter bar.

## 8. To 10/10, in order

1. Search honours its own `checked`: upcoming first, count as the results heading. *An hour.*
2. The ledger in three columns (town | measure, dates as one sentence, summary at 64ch | status), sources named, "How sure" one word at the summary's end; the rulings cells labelled on phones. *Half a day.*
3. /topics/solar takes the switch and the preference; the row prefix as real text, the town a link. *Two hours.*
4. /ma/carver: button to the rail's top (`"head rail" "main rail"`), the "Next meeting on our list" line cut. *An hour.*
5. A town filter and saved towns on /upcoming. *Half a day.*
6. "New to this town" at 400 grey; 48 px above "This week" on phones; `form { max-width: 36rem }` on /watch. *Half an hour.*
