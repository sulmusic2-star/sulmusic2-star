# Round 8: the editor and the clerk again, the analyst, the attorney and the developer back, the style director's fourth read (Oct 16, 2026)

Round 7's fixes went live late on Oct 16 (commits fc531d8 to 9efc251). Round 8 put six reviewers on that build: the editor and the clerk from round 7 on the same tasks, the data-center analyst and the land-use attorney from round 5, the solar developer from round 6, and the style director. Each used the live site, checked write-ups against the towns' PDFs and feeds against the town's own notices, and scored what they would pay or whether they would rely on it. Reports and screenshots are in the session scratchpad (`value-test/round8/`); the style director's note is `style_director_round8.md` beside this one.

## Scores before the fixes

| Reviewer | Who | Score | Would pay | What they trusted | What broke trust |
|---|---|---|---|---|---|
| Editor (return) | Managing editor, 12 towns, laptop | 3/5 (was 3) | $40/mo for a twelve-town feed by RSS or a Monday email, once links and the export work | Search with twelve towns added; every fact checked right (Plymouth's Article 16, Marshfield's Article 6, Carver's two boards); "Before this" and Copy citation | The new Search export glued our origin onto every town URL; the CSV had no headline, time or place; Carver's Select Board agenda three times in Search, two of them dead; a citizen's petition amending zoning (Plymouth's Article 24) missed |
| Clerk (return) | Town Clerk, Rochester, laptop | 3.5/5 (was 3) | The town won't pay; would link it next month | Eight items, five meetings, every date, board, place and status right; all nine links open; the calendar feed now says CANCELED with STATUS:CANCELLED, 7 to 9 pm, the agenda link | The meeting ticket never said cancelled and still offered "anyone can attend and ask to speak"; every item twice in RSS and JSON; the postponement note on past items; "Holds a hearing on a solar project." in the feed |
| Analyst (return) | Data-center site selection, laptop | 3/5 (was 2.5) | $150/mo for a data-center ledger with CSV and one three-state feed; $300 with email and an API key | Three AG letters behind one filter; the topic CSV with status, time, place and agenda URL; Spencer's and Southbridge's pages exact against the agendas | No ledger with in-effect and expired; a phantom Westerly story; Southbridge's third reading labelled "Public hearing"; the Search export bug |
| Attorney (return) | Land-use partner, Worcester, laptop | 3/5 (was 2.5) | $100 a seat, three seats, once county filters, a working CSV and the unread towns are done | Brookfield's letter matched on every ground; the rulings page "the first page of a bench memo"; the town-actions CSV | No county or date filter on Upcoming or Search; the export bug; "Article 4" cited for bylaw section 4.8.12; 18 Worcester County towns unread |
| Developer (return) | Solar and storage developer, nine towns | 3.5/5 (was 3) | $200/mo for one watchlist of all our towns, a daily email or Slack post, a CSV that opens | Every status right (Hearing, Possible vote, Postponed to Wed Nov 4, Canceled); the AG summary "my VP's briefing"; the feed's cancelled flag | Dartmouth's Town Meeting warrant filed under the Select Board; Rochester's cancelled meeting three times in Search; one list per town |
| Style director | Fonts, layout, flow and feel | taste 8.5/10, usability 8.5/10 (was 8.5/8) | n/a | The ticket as specified (date, room, broadcast, rule, agenda, button, Share, calendar); "New" on 16 of 105 items; dark mode to the digit | Six menu items wrapping the phone header to three rows; the who-votes line 400 px below the ticket; the one-line view still a block per meeting; /watch unchanged |

Every laptop reviewer hit the same bug within minutes: the Search export I had shipped an hour earlier doubled the URL prefix. Three found a cancelled or re-posted agenda listed more than once in Search.

## What changed (commits d43a721 to ea7506b, live Oct 16)

**Search.** Copy this list and Download CSV fixed; one row per flagged item with the site's sentence, status, time, place, topics in words and both links; "Only agendas with a flagged item" hides routine agendas; replaced agendas stay out of the index and a board's day posted three times appears once; example searches on the empty page.

**Reading the agenda right.** A warrant posted under a Select Board listing files as Town Meeting; the matcher keeps up to five items per topic in a long warrant; "Article 4" is no longer cited for section 4.8.12; quoted agenda words start with a word; a story whose items were all dropped is dropped.

**Cancelled and postponed.** The ticket says "Canceled by the town" and drops the speaking line; feeds carry one entry per item and the site's headline grammar; the postponement note shows only while the meeting is ahead; a write-up's last sentence no longer repeats the postponement its status states.

**Words.** A vote with a public comment item says so instead of "Public hearing"; Southbridge's write-ups quote the Citizens Forum; "Discusses X" and "Holds a hearing on X" read subject first in lists and feeds; who finally votes sits in the ticket under the speaking rule; one definition per term.

**From the benchmark research** (`research_notes/Benchmarks/what_people_like_and_hate.md`): "Free, without an account or ads."; the time of day we last read a town; the cadence and one-click stop promise on the first alerts screen; our own 404 page; five menu items on phones; the home count matching the list; the Attorney General page's measure.

**Also.** A county filter on /upcoming; Leominster's moratorium filed under data centers too.

## Not done, and whose it is

- **One watchlist for any towns, delivered by email or Slack** (editor $40, analyst $150 to $300, attorney $300, developer $200). The paid tier and the email key, both the owner's.
- **A data-center ledger** (proposed, adopted, approved, in effect, expired, with dates and CSV). Data work on the tracker: end dates and an "ended" status.
- **The one-line view as one line, /watch on the home page's list, Search filters in a rail, "Meetings still ahead first" on by default.** The style director's day of design work.
- **Unread towns** (Worcester, Northborough, Templeton, Barre, Brookfield, Duxbury, Hanover, Middleborough): bot checks we will not bypass; the unblock requests wait on the owner.
- **Posted time per item, a reason beside "can't read yet", a sample alert, a weekly option, one page per project.** From the research; listed in the benchmark note.

## Scores across rounds

| Reviewer | R5 | R6 | R7 | R8 |
|---|---|---|---|---|
| Organizer | 3 | 3.5 | n/a | n/a |
| Analyst | 2.5 | 3 | n/a | 3 |
| Attorney | 2.5 | n/a | n/a | 3 |
| Editor | n/a | 3 | 3 | 3 |
| Developer | n/a | 3 | n/a | 3.5 |
| Neighbor | n/a | 2 | 4 | n/a |
| Farmer | n/a | 3 | 3.5 | n/a |
| Clerk | n/a | n/a | 3 | 3.5 |
| Retiree | n/a | n/a | 4 | n/a |
| Style (taste / usability) | 7 / 7 | 8 / 7.5 | 8.5 / 8 | 8.5 / 8.5 |

The residents are at 4; the people with money are at 3 to 3.5, and what holds them there is the same thing in every report: a list of many towns delivered to them. That is the paid tier.
