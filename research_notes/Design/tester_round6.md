# Round 6: nine reviewers against the live site, their scores, what changed (Oct 16, 2026)

Round 5's fixes went live on Oct 16 (commit ca34f20). Round 6 put nine fresh reviewers on that build the same day: the organizer and the data-center analyst on their round-5 tasks, six new people chosen for the money and the audiences we want (a newsroom editor, a solar developer, a neighborhood group admin on a phone, a cranberry grower approached by a lessor, a legislator's aide, a land broker), and the style director scoring its own spec. Each used the live site without memory of earlier rounds, checked write-ups against the towns' agenda PDFs, and scored what they would pay. Reports and screenshots are in the session scratchpad (`value-test/round6/`); the style director's note is `style_director_round6.md` beside this one.

## Scores before the fixes

| Reviewer | Who | Score | Would pay | What they trusted | What broke trust |
|---|---|---|---|---|---|
| Organizer (return) | Statewide clean-energy group, phone | 3.5/5 (was 3) | $75/mo statewide topic alerts into Slack; $25 for the weekly list | Copy the week as text, 23 lines ready to paste; CSV with agenda and page links; citation start and date fixed | Carver's Federal Pond hearing listed as live when the agenda says "CONTINUED TO NOVEMBER 4"; the default speaking rule dressed as the agenda's; Rhode Island rides along in the copy; "Which town?" still the only door |
| Analyst (return) | Data-center site selection, laptop | 3/5 (was 2.5) | $200/mo for topic-and-state feeds, a per-town CSV with outcomes; $100 for an API | The topic CSV is real; all three data-center approvals now carry decision letters; town pages carry the rulings | Search's "Email me" still drops the topic; "Plymouth Town Meeting Undated" beside the dated row; a Smithfield, RI junk row in the CSV; the feed page says "Nothing on these topics" the day before Plymouth votes |
| Editor | Managing editor, 12 Plymouth County towns | 3/5 | $150/mo once every board is covered and a saved 12-town list arrives Monday by email or Slack | One search across twelve towns with every PDF linked; "Before this"; Copy citation | Continued and cancelled hearings read as live; no way to copy or download the Monday list; six topics, not every item; citation date off the page date |
| Developer | Solar and storage developer, nine towns | 3/5 | $300–400/mo for same-morning email on nine towns with cancellations flagged, a Town actions CSV, letter full-text search | All six towns found in seven minutes; Lakeville's battery bylaw hearing exact; the AG table | Federal Pond shown as Hearing; Rochester's meeting cancelled and the site silent; Westford's Town Meeting article not carried forward; filename and utility-pole matches |
| Neighbor | Street group admin, 64, phone | 2/5 | Nothing; would come back for one page per project with "what's next" | "Carver Town Hall, Meeting Room #1"; "anyone can speak" | Three dates fighting for one project (Oct 13 past, Oct 21 with no street, Oct 27 "if the board agreed"); no page for 104 Tremont St; "applicant", "Notice of Intent", "Buffer Zone" unexplained |
| Farmer | Cranberry grower, Carver, phone | 3/5 | $5/mo if it said what the board did the morning after | Dates, boards and PDF links; Carver's own ruling history ("disapproved", then approved except the clearing cap) | Never says what the board did; "(no vote listed)" where the agenda says "possible vote"; the Oct 20 Select Board link dead with "Checked Oct 16" beside it; "moratorium" and "Tracer Lane II" unexplained on the first screen |
| Aide | Legislator's aide, five-town district | 3/5 | n/a | Five towns in 30 days found; coffee-hour paragraph written from the site | Easthampton's Oct 21 hearing labeled with another item's e-bike wording; Southampton and Westhampton unread; Search matches street names, not towns |
| Broker | Land broker, Worcester County | 3/5 | $40/mo for a weekly Worcester-and-Providence digest with a county CSV | The rulings summary table ("replaces an hour with town counsel") | Southbridge's "Third Reading" read as discussion; no county filter or column; no AG CSV; 18 blind towns including Worcester; the Words box searches summaries, not letters |
| Style director | Fonts, layout, flow and feel | taste 8/10, usability 7.5/10 (was 7/7) | n/a | Frame and rails, headline hierarchy, the ticket, the sheet mark, dark-mode button | Stray "·" on every phone place line; "New" on most rows; no one-line view; three headline spellings for one Town Meeting; 84–90 characters a line |

Seven of nine landed on 3. The shared complaint, from five reviewers independently, was the same item: a continued hearing shown as live. The second shared complaint was silence about what happened next.

## What changed (commit 906458c, live Oct 16)

**Reading the agenda right.** A "continued to" line below the item window now postpones the hearing (Carver: "Postponed: Federal Pond Solar's hearing moves to Wed Nov 4"); a cancelled meeting is marked "Canceled, the town says" with every item's status set to Canceled (Rochester); "Third Reading", "Discussion & Action" and "ordinance adoption" read as votes (Southbridge); Town Meeting dates named in a write-up's "next" sentence carry forward to the town page's "Also ahead" (Westford); when a town re-posts an agenda under a new file, the old document is marked replaced, its items keep their ids and link to the new file, and items the new file dropped go away (Carver's Oct 20 Select Board), with five tests in `tools/test_replaced.py`.

**Words.** The speaking line says "Public hearing. The usual rule applies: anyone can attend and ask to speak…" and Town Meeting gets its own voters-only line; the citation says "Read Oct 10; the town's listing checked Oct 16"; "(no vote listed)" is gone from headlines; one spelling, "…: vote (Article N)"; mention lines quote agenda words only when the words are a sentence, not a filename.

**Pages.** Copy the week groups lines by state and skips cancelled meetings and mentions; a county filter and county column on topic pages, with the count ("14 of 90 meetings"); the Attorney General's rulings and town actions download as CSV; /upcoming has a one-line view (remembered); the style director's cascade notes are folded into the sheet: no stray "·" on phones, "This week" level with the H1, home rows in two columns, the rulings page no longer scrolls sideways on a phone, 30em measure on running text.

## Not done, and whose it is

- **What the board did.** Farmer, neighbor, aide, editor and analyst all asked for outcomes. That needs minutes, which post weeks later and are a different document class; it is the next crawler feature, not a page fix.
- **Statewide or multi-town alerts, a saved town list, email.** Organizer, analyst, editor, developer and broker. The paid tier, and email alerts are deferred by the owner. Price signals from both rounds go into the pricing note when pricing is decided; nothing on the site.
- **One page per project** (104 Tremont St across three boards). Design work: a project key from the address.
- **Every agenda item, not six topics** (editor). A different product; noted for the roadmap.
- **Unread towns** (Worcester, Brookfield, Petersham, Templeton, Middleborough, Berkley, Southampton, Westhampton, Duxbury). Crawler coverage; some are bot checks we will not bypass.
- **Easthampton's e-bike wording on a hearing**, the Words box searching summaries, the feed page's "Nothing on these topics" beside Plymouth's warrant, write-ups for the new upcoming items. Open; round 7's list.

## Round 7

Re-score the three lowest with the same personas and tasks (neighbor, farmer, editor), add two new judges for audiences we have not asked (a town clerk who posts the agendas, and a retiree who reads the paper and distrusts websites), keep the style director. Results in `tester_round7.md`.
