# Agenda Ahead: round 8, what landed

Style director review, Oct 16, 2026, against my spec and the round-6 and round-7 reads. Chromium at 390 and 1366 px, light and dark; 56 screenshots in `value-test/round8/style/`.

## 1. Verdict

The meeting page is now the record in the spec: date, room, broadcast, speaking rule, agenda, button, Share and Add to my calendar in one ticket, under the H1 on a phone and in the rail on a laptop. The share line has its full stop, both items and the room. "New" means something again: 16 of 105 items on /upcoming, not 73 of 117. Dark mode is the spec to the digit. Two things pull it back. The sixth menu item breaks the phone header: five links fill one 14 px row and "Get alerts" sits alone on a third, so the header is 149 px, 18 percent of the screen. And the one-line view and /watch did not move. **Taste 8.5/10, usability 8.5/10.**

## 2. The round-7 six

1. **"New" for 48 hours: landed.** 16 of 105 on /upcoming, 0 on Carver, 2 of 3 on the home page.
2. **The share line: landed, all four.** Full stop, both items, "Meeting Room #1, Carver Town Hall, 108 Main Street", the button in the ticket. The fallback says "Copied, ready to paste".
3. **The one-line view as one line: not.** Each meeting is still a 146 to 298 px block at 1366: meta line, a headline wrapping inside 540 px with 1,120 free, status, "Agenda (PDF)". The date prints 150 times for 8 days. No town filter; /topics/solar has no switch. With write-ups, /upcoming is 40,410 px at 1366 and 58,626 at 390.
4. **/watch: not.** `#home-town` still has `list="town-names"`. "Add to my calendar" (y=540) still sits above the neighbours box (588) and the topics line (648).
5. **Measure and glossary: landed.** `.brief-what` 540 px, 69 characters; the 16 px lines 544. Carver's glossary now squares with the 65 and 100 feet above it, and "(BESS)" is gone.
6. **"This week" by date; calendar in the ticket: landed.** Sat Oct 17, Mon Oct 19, Wed Oct 21. The .ics carries the room, both items and the agenda link.

Also landed: rule-colour underlines on headlines; one dot rule on every page.

## 3. The new things

**Six menu items.** Fine at 1366. At 390 they wrap, and the orphan is the link that matters most. Five fit; six do not at any gap above 11 px.

**Who finally votes.** "After the hearing the Planning Board makes a recommendation; Town Meeting votes on the bylaw." Right sentence, wrong place: a paragraph after the last write-up, 400 px below the ticket at 1366, 1,160 on a phone. It is the ticket's fourth line.

**"Words on this page."** Right form, and every term is used on the page. One cut: "Moratorium: a temporary ban" repeats the lead's "moratorium (a temporary ban)". The miss is the measure: the lead stops at 612 px, but the "Why" paragraphs run the full 1,120 px, 121 to 150 characters a line.

**Copy this list and Download CSV** on /search. The copied lines are the agenda's file titles with the site's origin glued to the town's URL: "Carver Planning Board, Oct 13, 2026: October 13, 2026 - PB Agenda. https://agendaahead.vercel.apphttps://www.carverma.gov/…". No link in the list opens. Search still has no rail, a datalist for towns, and past meetings first.

## 4. Against the agenda

Carver Conservation Commission, Oct 21: "MEETING ROOM #1 – CARVER TOWN HALL … 7:00 PM" | "Wed Oct 21, 7 pm, Meeting Room #1, Carver Town Hall, 108 Main Street". "cablecast by Area 58 … Channel 15 … on YouTube" | "Watch on Channel 15 or YouTube". The home page says "141 items at meetings still ahead"; the page it links to lists 105.

## 5. What reads generated

- "Public hearing: anyone can attend and ask to speak. The agenda prints no other rule." 18 times on /upcoming; "Ask the town clerk how others may speak." 10 times. Honest, still a stamp.
- Lakeville's glossary: "BESS: a battery energy storage system: large batteries that store electricity and feed it back to the grid. Battery energy storage: large batteries that store electricity and feed it back to the grid."
- Carver, still: "Postponed to Wed Nov 4" beside "continued to Nov 4" above "is continued to November 4, 2026".

## 6. What to refuse

- A hamburger to fit the sixth link; drop one on phones.
- A box, icon or heading for "who votes"; it is one line in the ticket.
- Tinted rows or a table header in the one-line view, again.

## 7. To 10/10, in order

1. Five links on phones: hide "Biggest stories" below 480 px; it lives under Topics. *An hour.*
2. The who-votes line into the ticket under the speaking rule; the copied list with the site's headline and one working link a line. *An hour.*
3. The one-line view as one line: `7rem minmax(0,1fr) 9.5rem`, the day once, the agenda link off the row, a town filter, the preference on /topics/*. *A day.*
4. /watch on the home page's list, the button last. *Half a day.*
5. `max-width: 34em` on the Attorney General page's paragraphs; "Moratorium" out of its glossary; one BESS definition on Lakeville. *An hour.*
6. Search: "Meetings still ahead first" on by default, filters in a rail. *Two hours.*
