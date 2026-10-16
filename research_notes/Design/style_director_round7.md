# Agenda Ahead: round 7, what landed

Style director review, Oct 16, 2026, against my spec and round-6 read. Chromium at 390 and 1366 px, light and dark; screenshots in `value-test/round7/style/`.

## 1. Verdict

The cascade is clean and it shows. No stray "·" on any phone page, "This week" level with the H1 (both y=110), /attorney-general/rulings 390 px wide on a phone (was 489), the home row's headline 392 px, not 208. Headlines have one grammar: "Holds a hearing" 20 to 0, "Discusses a" 23 to 0, "(no vote listed)" 37 to 0. Dark mode is the spec exactly: paper #151a18, button rgb(155,74,162) under white, hover rgb(163,82,170). What still separates it from a quiet record: "New" on 73 of 117 items, a glossary that contradicts the write-up above it, and a share line one item short. **Taste 8.5/10, usability 8/10.**

## 2. The round-6 next three

1. **Clean the cascade: landed**, except the measure. `.brief-what` stops at 712 px, 82–87 characters a line; `.speak-line`, `.line-before` and `.terms` at 544 px, 76–81. The spec said 30em, about 70.
2. **One headline grammar: mostly.** Subject first on 116 of 117 /upcoming headlines; the holdout is "Planning Board discusses new state clean-energy siting rules". Two headlines carry the newsroom's notes to itself: "40B Projects is a menu link (not a 40B item)" and "(not a solar item)". The town page's meeting line has its speaking rule under it. "New" did not move: 73 of 117 on /upcoming, 12 of 20 on /trending, 2 of 3 on the home page.
3. **The two flows: half.** /upcoming has "With write-ups / One line each", remembered across reloads; it halves the page, 14,619 to 6,424 px at 1366, 21,848 to 9,423 at 390. But each meeting is still a 148–272 px block (meta line, headline, status, "Agenda (PDF)"), each prints its own date, there is no town filter, and /topics/solar (12,440 px) has no switch. /watch is unchanged: `#home-town` still has `list="town-names"`, and "Add to my calendar" (y=540) still sits above the neighbours box (588) and topics (796).

Also landed: row hover tint, /trending's pill in ink, "Copied" after Copy citation.

## 3. Two new things

**"Words on the agenda."** Right form: one grey 16 px paragraph at the foot of the items, the lead in bold, each term a `<dfn>` in ink, no box, no tooltips. It contradicts the page: write-up and agenda say "65-foot and 100-foot Buffer Zone"; the glossary says "Buffer Zone: the 100 feet next to a wetland". It defines a word the page never uses: "(BESS)" is on neither the agenda nor the write-ups. And "Notice of Intent" was glossed inline, better, 900 px earlier ("a wetlands permit (a Notice of Intent)"). Keep the paragraph; cut it to words the page uses and has not glossed.

**The shared line.** `navigator.share` gets title "Carver Conservation Commission, Wed Oct 21, 7 pm" and text "Carver Conservation Commission, Wed Oct 21, 7 pm, Carver Town Hall. Solar canopies with battery storage, 235 Main St (Parallel Products): wetlands hearing Anyone can attend and ask to speak." plus the URL; the clipboard fallback is the same with the link on a second line. This is the forwardable line the spec asked for, nearly. The full stop after "wetlands hearing" is missing, so the headline runs into the rule. It carries only the first item, so a Tremont Street neighbour forwards a line that never mentions 104 Tremont or Nov 4. "Carver Town Hall" drops the agenda's "Meeting Room #1". And the button sits at the foot (y=1228 at 1366, below the fold), not in the ticket whose contents it repeats.

Against the agenda PDF: "MEETING ROOM #1 – CARVER TOWN HALL … 7:00 PM" | "Carver Town Hall, Wed Oct 21, 7 pm". "cablecast by Area 58 … Channel 15 … on YouTube" | nothing. "CONTINUED TO NOVEMBER 4, 2026" | "Postponed to Wed Nov 4", right. "All interested parties are invited to attend" | "The usual rule applies: anyone can attend and ask to speak".

## 4. What reads generated

- "New" on 62 percent of /upcoming.
- "The usual rule applies" seven times on /upcoming; "Town Meeting: the town's voters decide (elected members, where the town has a representative town meeting). Ask the town clerk how others may speak." seven times.
- "Postponed to Wed Nov 4" beside "continued to Nov 4" above "Continued to Wed Nov 4, 2026.": one fact, three times.
- /topics/solar: "Canceled, the town says" over "The October 20 meeting is cancelled".

## 5. What to refuse

- A glossary box, dotted underlines or hover definitions on the `<dfn>` terms.
- Share icons per network; one button and the system sheet is right.
- Tinted rows or a table header in the one-line view; grouping by day does that work.
- A colour or count on "New".

## 6. To 10/10, in order

1. "New" for 48 hours or not at all. *An hour.*
2. The share line: full stop, every item on the page, the room from the agenda, Share in the ticket. *An hour.*
3. The one-line view as one line: the spec's three-column row, day printed once, the preference honoured on /topics/*, saved towns. *A day.*
4. /watch on the home page's list, choices above one button. *Half a day.*
5. `.brief-what` at 30em; the glossary cut to the page's words and the town's numbers. *An hour.*
6. Sort "This week" by date; "Add to calendar" in the ticket. *An hour.*
