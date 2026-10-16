# Agenda Ahead: design direction and spec

Style director review, Oct 13, 2026. I went through the preview (351watch-70nf9gjzb) at 390 and 1366 px in Chromium, in light and dark mode, and read `styles.css` and the built HTML. Screenshots and measurements are in the session scratchpad under `value-test/style/`.

## 1. Verdict

Agenda Ahead is a well-written public notice laid out on a strip the width of a phone. The write-ups are the best thing on it and the type was clearly chosen, so it already reads as made by a person. It does not yet read as designed. At 1366 px the logo sits at x=125, the content starts at x=273, and the text stops near x=920, leaving the right third of the screen empty. On a town page the four layers of an item (meeting line, headline, summary, history) are 16, 18, 18 and 16 px, told apart only by weight and grey. Items sit 12 px apart, less than half a line of body text, so three of them read as one long paragraph. The time and room, which are what a resident came for, are the greyest text on the page. The status dot is filled for "Vote" on a town page and hollow for the same vote on the home page. The mark, three rounded bars in the top-left corner, looks like a menu button with a purple stripe. The site could be a civic cousin of the Times election pages: a quiet record you trust at a glance, with one thing people forward to a neighbour, the meeting's date, room and speaking rule. Getting there is about four days of layout and type work, and the look stays the same. Use the width, give every item a real headline, make the meeting's time and place the loudest thing on the page, and replace the mark.

## 2. Typography

Keep Barlow and Barlow Semi Condensed. Barlow was drawn from California's highway signs and license plates, so it has the look of public infrastructure without dressing up as a government site, and one family in two widths gives the site a single voice. Jordan already called it "a real choice, not Inter". A serif would add a fourth font file and the cream-and-serif look; Inter would throw away the one thing that already reads as chosen.

What it needs is a clearer split of jobs. Semi Condensed 700 sets the things you find your way by: page titles, town names, write-up headlines, the meeting date and day headings. Barlow sets everything you read or operate. Today each write-up's headline is Barlow 600 at 18 px, the same size as the paragraph under it.

| Role | Face | Phone | Desktop (≥1024 px) | Tracking |
|---|---|---|---|---|
| H1 | SC 700 | 32/1.1 | 44/1.05, `clamp(2rem, 1.2rem + 2vw, 2.75rem)` | -0.012em |
| H2 | SC 700 | 26/1.15 | 28/1.15 | -0.006em |
| Write-up headline, ticket date | SC 700 | 22/1.22 | same | 0 |
| Summaries, body | Barlow 400 | 18/1.55 | same | 0 |
| List headline | Barlow 600 | 18/1.4 | same | 0 |
| Meta, history, facts | Barlow 400 | 16/1.5 | same | 0 |

That keeps it to five sizes per screen, as the brief asks. Three rules go with the scale.

- Meta lines drop from 600 to 400. Today `.row-when` and `.meet-head` are semibold grey and compete with the semibold headline under them. Only the town name in a meta line stays at 600, in ink.
- Dates and counts get `font-variant-numeric: tabular-nums lining-nums` (the subset has `tnum`) on `.row-day`, `.ticket`, `table`, `.n` and `.sub-count`, so columns of dates line up.
- Running text stops at `max-width: 64ch`, about 70 characters. The Attorney General page's "Why" paragraphs run about 100 characters to the line.

Two details people notice without naming them. Brief text uses straight quotes ("Elderly Housing", lawyer's) beside the site's curly ones; convert them at build time, outside `<blockquote>`. And the stylesheet credits `fonts/OFL-Barlow.txt`, which doesn't exist, while the Besley and Public Sans licences ship with no fonts that need them.

## 3. Layout and rhythm

**First, clean up the stylesheet.** The "simple pages" and "value-test round" blocks redeclare `.home-hero`, `.chips`, `.near-me`, `details.more`, `.item-from` and `.sr-only`, so which rule wins is now an accident. Fold the second half into the first.

**Spacing.** Keep the tokens (4, 8, 12, 16, 24, 32, 48, 64) and use them by rule: 4 to 8 px inside an item, 24 between items, 48 between meetings, 64 between sections.

**The desktop frame.** Header, content and footer share one wrap, `max-width: 1160px; padding: 0 20px`. Today the header uses 1160 and the content 860, which is why the logo and the H1 don't line up. At ≥1024 px:

```css
.page-grid { display: grid; grid-template-columns: minmax(0, 720px) 320px;
  justify-content: space-between; column-gap: 80px; align-items: start; }
.rail { position: sticky; top: 24px; }
```

A rail goes only where something should stay in view: the town (alerts, next door), the meeting (the ticket), the search (filters). Lists use the full width.

**Home, desktop.** Two halves, `grid-template-columns: 1fr 1fr; column-gap: 80px`: the H1, sentence and town box on the left, "This week" on the right, all inside one 900 px screen. On phones, cut the 96 px of empty space between "Or try" and "This week" to 48.

**The list row.** On desktop each row becomes a three-column record, so the status dots line up like a results table. Today each one floats 57 to 306 px after the end of its headline.

```
Tue Oct 13   Boxborough  Planning Board                                  ○ Possible vote
             Data center ban article: Planning Board reviews lawyer's edits...
             Swansea  Conservation Commission                            ● Hearing
             Solar farm with batteries off Old Warren Rd: wetlands hearing
```

```css
@media (min-width: 760px) {
  .row a { grid-template-columns: 7rem minmax(0, 46rem) 9.5rem;
    grid-template-areas: "day meta stage" "day line stage"; column-gap: 24px; align-items: baseline; }
  .row-day { grid-area: day; font-weight: 600; font-variant-numeric: tabular-nums; }
  .row[data-same-day] .row-day { visibility: hidden; }
}
```

In date-sorted lists each day prints once; /trending is ranked, so its rows keep their dates. On phones the date becomes a heading over its rows, as Luma does it. Town and board are set apart by weight and colour (town 600 ink, board 400 grey, 12 px gap) instead of middle dots. On desktop, hovering a row tints all of it: `background: var(--land); margin: 0 -12px; padding: 12px`.

**The meeting page.** It answers "when, where, can I speak" before "what":

```
Plymouth Town Meeting                    | Sat Oct 17, 8 am
                                         | Plymouth North High School
One-year ban on new data centers  ● Vote | 41 Obery Street, or online
No new data-center applications ...      | Members vote. Other registered voters
Before this: ...                         | may speak over Zoom with 48 hours' notice.
Agenda wording ›                         | Add to calendar    Warrant (PDF)
                                         | [Get alerts for Plymouth]
```

The ticket is the only tinted block on the site: `background: var(--land); padding: 20px; border-top: 3px solid var(--ink)`. On phones it goes under the H1, before the items. Remove the second "Warrant (PDF)" link at the foot, and give the place its own line: on a phone it wraps today so the line starts with a stray "·".

**The town page.** Main column: H1, "Next: Town Meeting, Sat Oct 17, 8 am", then each meeting with its ticket line in ink and its write-ups. Rail: the alerts button at full width, "Next door" as a two-column list (town, status), then "Boards we read … Last checked Oct 13", one sentence that is now folded away under "About Plymouth's agendas". On phones the rail content follows the list, except the button, which stays under the H1.

**Write-ups.** Headline in SC at 22 px, with the status beside it (`grid-template-columns: minmax(0,1fr) auto; column-gap: 16px`) and the facts line left-aligned. Today `.line-facts` uses `justify-content: space-between`, so on Carver "Solar, battery storage", "104 Tremont Street" and "Federal Pond Solar, LLC" spread across 650 px like a table with no headings.

**Other pages.** /trending: two selects on one line ("This year", "All topics") in place of eleven chips, with the near-your-town box below the list. /towns at desktop: counties in `columns: 3 240px`, which takes Massachusetts from 14 rows to 5. /topics: `vertical-align: middle` on cells, since the numbers sit 10 px above their topic names. /upcoming: `.meet-head { align-items: baseline }`, since the town link drops below its own meta line.

## 4. Color and marks

Keep the palette: white paper, green-grey ink #1f2724, rules #d6ddd8 and one purple, #7a2c80 (8.4:1 on white). The green-grey tint is what keeps it from looking like a template. Purple has five jobs and no others: the primary button (one per screen), the filled status dot, the mark's middle line, focus rings and the search highlight.

**Status dot.** Each channel means one thing. The fill says whether the board acts: filled purple for a vote or hearing, hollow (1.5 px #6f7a74) for a discussion, review or postponement. The word's colour says when: amber #7a4d00 within 48 hours, grey otherwise. Bug: rows on / and /trending render `class="stage"` without `act`, so every vote there is hollow. Fix the row renderer in build.py and `storyNode` in trending.js.

**The mark.** In the corner where people look for a menu, three rounded bars look like one, even now that all three show. Make it what it stands for, a sheet of paper with one line marked:

```html
<svg class="brand-mark" viewBox="0 0 24 30" aria-hidden="true">
  <rect x="1" y="1" width="22" height="28" rx="2" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/>
  <rect x="6" y="8" width="12" height="2" fill="var(--dot)"/>
  <rect x="6" y="13.5" width="12" height="3" fill="var(--mark)"/>
  <rect x="6" y="20" width="8" height="2" fill="var(--dot)"/>
</svg>
```

Draw it 28 px tall with square ends, aligned to the content's left edge, and use the same drawing for the favicon. A tall sheet of paper can't be mistaken for a button.

**Dark mode.** Keep the #151a18 paper and the greys, and fix two things. `.btn:hover` hard-codes #5e2062 behind the dark-mode label colour #1b1220, which is 1.6:1, so the label disappears on hover. And the pastel #d59bdc button looks like another brand's. Give the button its own tokens:

```css
:root { --mark-fill: #7a2c80; --mark-fill-hover: #5e2062; --on-mark: #fff; }
/* both dark blocks; white text 5.4:1 and 4.8:1, fill against paper 3.3:1 and 3.6:1 */
  --mark-fill: #9b4aa2; --mark-fill-hover: #a352aa; --on-mark: #fff;
.btn { background: var(--mark-fill); color: var(--on-mark); }
```

Keep #d59bdc for dots, focus rings and the mark in dark mode.

**Search highlights.** Every word gets its own pink box today ("Data" and "Centers" are two), which buries the snippet. Use a low highlighter stroke and merge neighbouring marks in search.js: `mark { background: linear-gradient(transparent 58%, var(--hl) 58%); padding: 0; }`.

## 5. Flow and feel

**A resident finds her town and one item.** Typing "Ply" and picking Plymouth is quick, and the suggestion list is good. The town page is where she stalls. The time and place are a 16 px grey line, and on a phone the speaking rule is 1,628 px down, after three write-ups. The headlines don't look tappable on a phone either. The fixes: a ticket at the top of every meeting, and headline links with a light underline that is always there (`text-decoration-color: var(--rule)`, ink on hover).

**A reporter scans six towns.** Today that is six town pages, or a search with town chips that sorts by best match. The first result for "data center moratorium" is a past meeting from Sep 23, and "Meetings still ahead first" is an unticked box inside Filters. At 1366 px, /upcoming is 13,146 px tall with every write-up open. The fixes: a one-line view of /upcoming filtered to his towns (`/upcoming?town=…&view=lines`), grouped by day, with a switch between "One line each" and "With write-ups" and his saved towns (`agendaahead:areas`) one tap away. Search puts upcoming meetings first by default.

**Someone sets up alerts.** /watch still uses the browser's own suggestion list (Chrome's ▼) instead of the home page's. Step two puts "Add to my calendar" above the neighbours checkbox and the topics line, so people commit before they choose. And it ends in a calendar because the email key isn't set, which only the owner can fix. The fixes: the home page's suggestion list; step two ordered as preview, choices, one button; and once email is on, the preview drawn as the email itself (From: Agenda Ahead, subject "Plymouth, Sat Oct 17: Town Meeting votes on a data center ban", the two items) above a button that says "Email me about Plymouth". On desktop the preview sits in the rail beside the form.

**Micro-interactions worth having:** the row tint on hover; a `:target` wash in `--mark-wash` on a meeting reached from an alert link, fading over 1.5 s so people see where they landed; "Copy citation" changing to "Copied" for two seconds; the sticky rail; Escape closing the suggestion list. **Refuse:** sections fading in on scroll, cards lifting on hover, shimmering placeholders on static pages, numbers that count up, page transitions, toasts, confetti on sign-up, and tooltips on the dot (the word is already beside it).

## 6. The ten changes, ranked

1. **Desktop frame and rails** (every page; rails on town, meeting, search). One 1160 px wrap and `.page-grid`. Answers the "phone layout stretched" note from every desktop tester and gives the ticket a home. *A day.*
2. **Write-up hierarchy** (town, meeting, /upcoming). `.line-say { font: 700 1.375rem/1.22 var(--f-head) }`; status beside the headline; `.lines > .line + .line { margin-top: 24px }`; `.meeting { padding: 48px 0 24px }`; `.line-facts { justify-content: flex-start }`. People see where one item ends and the next begins, which is most of scanning. *An hour* (CSS, plus moving one span in build.py).
3. **The meeting ticket** (meeting pages; top of each meeting on town pages). Date and time in SC 22 ink, place on its own line, speaking rule, calendar and warrant links, in the one tinted block. Dana gets her three answers before she scrolls. *An hour* on phones; desktop comes with change 1.
4. **The list row and the dot fix** (/, /trending, /upcoming). Three-column grid, meta at 400, `act` on rows, day headings on phones. Lists scan like a results table and the dot means one thing everywhere. *An hour*, plus three for grouping by day.
5. **The mark** (header, favicon). The sheet drawing. Removes the one element testers mistook for a control. *An hour.*
6. **Home in two halves** (/ at ≥1024 px). H1 to 44 px, question left, "This week" right. The home page asks and answers in one screen. *An hour.*
7. **Dark-mode button tokens** (every button). Fixes an unreadable hover and gives dark mode the same purple. *An hour.*
8. **The reporter's view** (/upcoming, search). `view=lines`, town filter, saved towns, upcoming first. Marcus saves about 40 of 55 minutes now; most of what's left is scrolling. *A day.*
9. **The alerts flow** (/watch). The home page's suggestion list, choices above the button, the email preview. Every tester asked for email alerts first; this has the flow ready the day the key is set. *A day.*
10. **Type details** (sitewide). Meta at 400, tabular dates, curly quotes, 64ch lines, highlighter marks, the /topics and /upcoming alignment. None shows alone; together they are the difference between generated and typeset. *About three hours.*

## 7. What to refuse

- **A map on the home page.** At 390 px, 447 towns make taps too small to hit, and typing is faster. A map can come later, as data on a topic page.
- **An icon or colour per topic.** Nine colours would scatter across every list and break the one-accent rule.
- **Cards with shadows.** Rules and spacing already group items, and shadowed cards are the commonest sign of a generated site.
- **A row of big numbers.** The grey count under "See everything coming up" already says it.
- **A hamburger menu or sticky header on phones.** Five visible links beat a hidden menu, and a sticky header takes a sixth of the screen.
- **A serif "to feel editorial", or Inter "to look neutral".** One adds a fourth font file; the other erases the choice that already works.
- **More purple**: gradients, purple links, purple headings. The accent works because it is rare.
- **Tracked capitals above sections** ("COMING UP"), "Hot" badges, red counts, infinite scroll.
- **A theme switch, a location prompt, a pop-up or a chat box.** The system setting picks the theme, the town box asks the question, and the town page is the answer.
