# Round 5: six reviewers chosen for the people and the money we want, and what changed (Oct 13 to 16, 2026)

Round 4 proved the redesign beat the old site. Round 5 asked harder judges: five people whose jobs or money would make or break the service, plus a style director briefed to judge fonts, layout, flow and feel with taste. Each reviewer used the live site with no memory of earlier rounds, checked write-ups against the towns' own agenda PDFs, and scored what they would pay or whether they would rely on it. Reports and screenshots are in the session scratchpad (`value-test/round5/`); the style director's spec is `style_director.md` beside this note.

## Scores before the fixes

| Reviewer | Who | Score | Would pay | What they trusted | What broke trust |
|---|---|---|---|---|---|
| Organizer | Statewide clean-energy group, phone | 3/5 | $75/mo for statewide topic alerts into Slack plus a weekly list; $25/mo for the list alone | Dated, tagged, statewide list; one-tap share text | "Which town?" dead end for a statewide user; "no rules stated" on speaking; "Pedro Rodri uez, as the agenda spells it"; citation "Retrieved Oct 10" under "Checked Oct 13" |
| Town planner | Carver's planner, laptop | 3/5 accuracy, 3/5 use | n/a | Every date, time and room right; both Oct 27 continuance requests; the three Attorney General letters match | A missing 40R article and a missing minor modification; "heard" where the agenda says continued; "Mentions solar." on a solar-credit purchase; a quote that starts mid-sentence; postponed-to dates absent from Coming up |
| Planning consultant | Zoning consultant, laptop | 4/5 | $50/mo for the rulings index plus a weekly digest; $100 with bylaw text | Struck-clause summaries, "Before this" chains, letters one click away | Rulings page not in the top nav; Words box is phrase-match with no empty message; blank Lee date; lowercase "the state energy department" at a sentence start; stacked parentheticals; "Choose Town Office" as a venue |
| Land-use attorney | Worcester firm, laptop | 2.5/5 | $200/mo firm seat for county and matter watchlists across 40 towns | AG table with letters, "Asks to postpone" badges, Copy citation, honest "can't read yet" | 18 of 60 Worcester County towns unread and unsaid; Shutesbury and Templeton approvals with no letter; county search that fails; asides about "our records"; a PFAS item under Moratoriums |
| Data-center site analyst | Site selection, laptop | 2.5/5 | $200/mo for CSV export, a town-level tracker and a three-state topic alert; $100 for an API | Direct PDF links, stage labels, the by-kind AG table, 312 towns a day | Topic alerts that drop the topic at "Which town?"; no export; unsourced Attorney General claims; "ban on new zoning"; Gill under Disapproved for data centers |
| Style director | Fonts, layout, flow and feel | taste 7/10 → spec | n/a | Barlow, the palette, the write-ups | A phone layout stretched to 1366 px; four text layers told apart only by grey; the time and room the greyest text; a mark that reads as a menu button; an unreadable dark-mode button hover |

## What changed (commit ca34f20, live Oct 16)

**Write-ups.** Eighty-nine corrected rows: no more asides about our records or our copy (the checker now fails them, with a test), the default speaking rule instead of "no rules stated", Carver's Federal Pond hearing "continued" with the agenda's full item as its quote, the 61A line as a right of first refusal, the Swansea name aside gone, Leyden's question marks turned into plain sentences, Northfield's vote described as the recommendation it is. All 269 verified under the stricter rule. The writers' rules are in `ARCHITECTURE.md` under the briefs contract.

**Data.** The three data-center letters (Shutesbury 12047, Templeton 12294, Gill 12422) are in the rulings list, each linked to the copy the town itself posted, so the approvals the analyst and attorney called unsourced now have their letters. The solar-and-battery moratorium record ("15 of 15") excludes them by technology. Moratorium-only items about PFAS, winter shut-offs or street openings no longer count as hits (nine dropped).

**Pages.** The status sits beside each headline; a request to postpone carries "The board decides at this meeting whether to postpone; until it does, the hearing is still on"; town pages list hearings an earlier agenda moved to a day with no agenda yet ("Also ahead, from earlier agendas"); the meeting page has a ticket with the day, room, speaking rule, agenda link and alerts button, in a rail on desktop and under the title on phones; town pages carry Next door and About in the rail; story rows are three-column records on desktop with the filled dot for a vote or hearing everywhere; the home page is two halves on desktop; the mark is a sheet of paper with three lines; dark mode has a readable button; write-ups use curly quotes; citations say "Read Oct 10"; "Worcester County" finds its towns and each county says how many we can't read; topic pages show the whole next seven days, copy the week as text, download the list as CSV and state coverage; the alerts page keeps the topic it came from; the rulings Words box matches every word and says when nothing matches.

## Not done, and whose it is

- **Statewide or multi-town alerts, CSV of any search, a town-level tracker, a firm seat.** Every paying reviewer asked for one of these; they are the paid tier. The price signals above go into the pricing note when pricing is decided (the owner's call; nothing on the site).
- **Carver's 40R article and the Meadow Solar minor modification.** The 40R keyword was added Oct 13; the daily crawl re-reads documents when the keyword set changes, but only those still in its cache. Items that share a window with another item are one hit today; splitting a window into its agenda items is crawler work.
- **Email alerts.** Deferred by the owner.
- **Reading the unread towns** (Worcester, Brookfield, Petersham, Templeton, Middleborough, Berkley). Crawler coverage work.

## Round 6

Nine reviewers against the live site: a newsroom editor, a solar developer's community-relations manager, a neighborhood association leader on a phone, a farmer approached by a solar lessor, a legislator's aide, a land broker, the organizer and the analyst again on their round-5 tasks, and the style director scoring its own spec. Results in `tester_round6.md`.
