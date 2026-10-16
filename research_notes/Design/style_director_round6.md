# Agenda Ahead: round 6, what landed

Style director review, Oct 16, 2026, against my Oct 13 spec. Chromium at 390 and 1366 px, light and dark; screenshots in the session scratchpad under `value-test/round6/style/`.

## 1. Verdict

It now reads as designed. Logo and H1 share one left edge, town and meeting pages have a rail, headlines are Semi Condensed 22 with the status beside them, and the mark is a sheet of paper nobody will tap for a menu. The meeting page is the record I described: date, place, speaking rule and button in one tinted ticket before the first item. What still separates it from a quiet, trusted record is copy and cascade, not layout. On a phone every place line opens with a stray "·" (78 times on /upcoming), because the fix sits above the rule it overrides. Most rows wear "New", so it means nothing. The two flows I gave a day each, the reporter's view and /watch, did not move. **Taste 8/10, usability 7.5/10**, against Jordan's 7 and 7.

## 2. The ten changes

1. **Frame and rails: partly.** Logo and H1 both at x=123; rail at x=923, sticky. Search has no rail. *Finish:* move search's filters into `<aside class="rail">` inside `.page-grid`.
2. **Write-up hierarchy: landed.** `.line-say` 22 px SC 700, items 24 px apart, meetings 49, facts left-aligned.
3. **Meeting ticket: partly.** Landed on /m/ pages. No "Add to calendar", and on /ma/plymouth the speaking rule still follows the third write-up. *Finish:* move `.speak-line` from `.meet-src` to just under `.meet-head`.
4. **List row and dot: partly.** On / and /trending the dot is filled rgb(122,44,128) for Vote and Hearing, hollow for Discussion, aligned at x=1019. No day grouping (`data-same-day`: 0), and "This week" runs Wed Oct 21, Sat Oct 17, Mon Oct 19. *Finish:* sort by date and emit `data-same-day`.
5. **The mark: landed.** 22×28 sheet; the favicon matches.
6. **Home in two halves: partly.** Grid and 44 px H1 landed, but the three-column row in a 520 px half leaves each headline 208 px wide, four lines deep. *Finish:* `.home .row a { grid-template-columns: 6.5rem minmax(0,1fr); grid-template-areas: "day when" "day line" "day stage"; }`.
7. **Dark button tokens: landed.** Hover measures rgb(163,82,170) under white, 4.8:1; rest 5.4:1.
8. **Reporter's view: not.** No one-line view; /upcoming is 11,297 px tall at 1366, 16,555 at 390. *Finish:* a toggle adding `.compact` to `.meetings`, with `.compact :is(.brief-what, .line-before, .line-facts, .meet-src) { display: none }`.
9. **Alerts flow: not.** `#home-town` still has `list="town-names"`, so Chrome draws its ▼, and "Add to my calendar" (y=665) still sits above the neighbours box (772) and topics (869). *Finish:* move `.submit-row` to the end of `#step-send`.
10. **Type details: partly.** Meta at 400, tabular dates, highlighter strokes, /upcoming baselines (both y=489) and the licence file landed. Running text sets 84–90 characters a line: 64ch of Barlow's 10.2 px zero is 651 px, and its average character is 7.7. The speaking line on /upcoming runs 153. Straight quotes survive: (the "Act"). *Finish:* `max-width: 30em` (about 70 characters) on `.brief-what, .line-before, .speak-line, .lead`.

## 3. What reads generated

- "New" on 82 of 132 items on /upcoming, 12 of 20 on /trending. On most rows it marks nothing.
- Subjectless verbs: 20 "Holds a hearing on…" and 23 "Discusses a…" on /upcoming, beside a second template, "Temporary ban on data centers, draft: Planning Board hearing".
- "(no vote listed)" 37 times on /upcoming, each beside "Discussion". Egremont adds "No vote is listed."
- One meeting, three spellings: "Town Meeting vote (Article 16)", ": vote (Article 14)", ". Vote (Article 15)".
- "Open the warrant (Town Meeting's agenda) (PDF)".
- "in Plymouth, MA, or join online", on Plymouth's own page.
- "Mentions solar: “…disorder and the benefits of outdoor exercise in winter…”", under two meetings.
- Search: "Discusses an item on data-center rules (no vote listed). +4".
- Eleven pills on /trending; the checked one is filled purple, a sixth job for the accent.

## 4. What to refuse

- Fixing "New" with a colour, icon or count; show it for 48 hours or drop it.
- A second tinted block. Don't tint "Next door" or /upcoming's meetings to match the ticket.
- A map, stats or chart in /upcoming's empty right side. Saved towns go there, or nothing.
- A sticky header for long pages; the one-line view is the fix.
- A combobox library on /watch. The home page's list exists.
- Purple status words to straighten the right-aligned dots.

## 5. Next three, in order

1. **Clean the cascade** (two hours). Fold the two appended blocks ("simple pages", "Value-test round") into the sheet. That removes the phone's stray "·", lifts "This week" level with the H1 (now 32 px lower, because `.wrap.narrow > section > h2` outranks `.home .next h2`) and sets the 30em measure. Add `.filterbar select { max-width: 100% }`: the 473 px Technology select makes /attorney-general/rulings 489 px wide on a 390 px phone.
2. **One headline grammar** (half a day, copy rules in the build). Subject first, board and action after the colon. No "(no vote listed)" where the status says Discussion; "New" for 48 hours. The town page's meeting line becomes a small ticket with the speaking rule under it.
3. **The two flows** (a day). A one-line /upcoming with saved towns; /watch on the home page's list, choices above one button.
