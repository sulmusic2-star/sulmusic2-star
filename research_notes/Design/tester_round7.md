# Round 7: three return reviewers, a town clerk, a retiree and the style director, their scores and what changed (Oct 16, 2026)

Round 6's fixes went live at midday Oct 16 (commit 906458c), followed the same afternoon by write-ups for every upcoming item (4bf812c). Round 7 put six reviewers on that build: the neighbor, the farmer and the editor from round 6 on the same tasks, two people we had not asked before (a town clerk who posts the agendas, and a retiree who distrusts websites), and the style director scoring its own spec a third time. Reports and screenshots are in the session scratchpad (`value-test/round7/`); the style director's note is `style_director_round7.md` beside this one.

## Scores before the fixes

| Reviewer | Who | Score | Would pay | What they trusted | What broke trust |
|---|---|---|---|---|---|
| Neighbor (return) | Street group admin, 64, phone | 4/5 (was 2) | Nothing; would share it ("still call Town Hall before you drive over") | Both boards on one page with "Before this"; "Postponed to Wed Nov 4" against the agenda's "CONTINUED TO NOVEMBER 4, 2026"; the honesty of "the agenda for that day isn't posted yet" | The suggestion list covering the "Find my town" button; the Select Board speaking rule printed twice; "written comments go to the town clerk", which the agenda never says; no room or Channel 15; "New" on a project on its third agenda; sixteen words not explained |
| Farmer (return) | Cranberry grower, Carver, phone | 3.5/5 (was 3) | $5/mo if it told him what the board did and watched 61A land | Dates, boards, PDF links; "A town can't ban solar" on the first screen; Carver's own ruling history | The Oct 20 Select Board link dead again (the town posted a third file); never says what a board decided; 61A items only when "solar" is in the line; Attorney General jargon ("Tracer Lane II", "G.L. c. 40A, § 3") |
| Editor (return) | Managing editor, 12 towns, laptop | 3/5 (was 3) | $50–75/mo for a Monday 6 am email, twelve towns, every agenda one line each | Search with twelve towns added, bookmarkable; "Before this" and "Copy citation" | No saved list and no way to copy it as a table; a phantom "Sat Oct 16, 2027 Town Meeting" built from a moratorium's end date; a missed zoning article (Marshfield's overlay-district repeal); "40B Projects is a menu link (not a 40B item)" on /upcoming; "Show more (48)" hiding Carver |
| Clerk | Town Clerk, Rochester, laptop | 3/5 | The town would not pay; would link to it once two things are fixed | Every Rochester date, board and status right; all nine links work; the "Report a problem" form pre-filled with the meeting | The calendar feed put the cancelled Oct 20 meeting on her calendar as a live all-day event with a description starting mid-sentence; the alert preview called it "Hearing" and said "anyone can speak"; the speaking rule invents a clerk procedure; "Town Hall, or join online" with no address or Zoom; the original agenda linked, not the Revised one |
| Retiree | Retired electrician, 71, Lakeville, phone | 4/5 | Nothing; would come back if it said when Town Meeting votes | The hearing, date, place and the town's PDF in a minute; no email wanted; the PDF matched | Two items for one hearing; "(see the battery storage brief)" with nothing to tap; "Same item, flagged twice" on the alerts page; the canned speaking rule; the list over the button |
| Style director | Fonts, layout, flow and feel | taste 8.5/10, usability 8/10 (was 8/7.5) | n/a | The cascade clean on every phone page; one headline grammar; dark mode as specified; "Words on the agenda" in the right form | "New" on 62 percent of /upcoming; the glossary contradicting the write-up above it (a 100-foot Buffer Zone against the town's 65 and 100 feet); the shared line missing its period, the room and the second item; the one-line view still a block per meeting |

Two things every reviewer who touched Carver found: the Select Board's agenda link died a second time (the town posted the file three times in a week), and the default speaking rule said something the agenda does not. Three found the suggestion list covering the home page's button.

## What changed (commits fc531d8 and 65823ce, live Oct 16)

**Reading the agenda right.** A document replaced more than once follows the chain to the live file, with a test; a moratorium's end date in a write-up no longer becomes a phantom Town Meeting; an overlay district being repealed, created or amended is a zoning hit; a town's "Revised Agenda" is the link when it sits beside the original.

**Words.** The default speaking rule is "Public hearing: anyone can attend and ask to speak. The agenda prints no other rule." and the Town Meeting line is one sentence; a rule two write-ups give in slightly different words prints once; twelve writers' asides ("No time limit is stated", "Not stated") are gone from the data and the verifier refuses them; "Canceled by the town" replaces "Canceled, the town says"; "Same item, flagged twice" never reaches the alert pages; items a writer marked "(not a solar item)" leave the lists; a "next" line that repeats the postponement date is dropped.

**"New".** It now means new to the town: an item that overlaps an older one, or whose write-up names earlier meetings, is not new. On /upcoming the badge went from 73 items to 17.

**The ticket and the shared line.** The room and street address come from the write-up when the header had none ("Meeting Room #1, Carver Town Hall, 108 Main Street"; "Town Hall, 1 Constitution Way, or on Zoom (link on the agenda)"); "Watch on Channel N or YouTube" when the agenda says; Share sits in the ticket and its text carries up to three items and the speaking sentence, each ending in a period.

**Plain words.** The glossary skips terms the write-up already explains in passing, names BESS only when the page says BESS, says what a Buffer Zone is without contradicting a town's own distances, and runs to six terms (Continued, Dual-use, Ground-mounted, Bordering Vegetated Wetland, Assessors Map and Lot, DEP File # added). The Attorney General page explains Tracer Lane II, G.L. c. 40A § 3, 225 CMR 29.00 and the Land Court in one line each, and Rulings is in the top menu.

**Feeds.** The calendar feed marks a cancelled meeting (CANCELED in the title, STATUS:CANCELLED), starts at the meeting's hour, carries the room, and describes each item with the site's sentence; the RSS and JSON feeds carry the same; the alert pages mark a cancelled meeting too.

**Pages.** /upcoming shows every meeting in the next seven days without "Show more"; the phone's town box keeps its button beside the input; the write-up measure is 30em everywhere; /pricing no longer promises daily email before email exists; "Report a problem" answers with a reference.

## Not done, and whose it is

- **What the board did** (farmer, retiree, neighbor, editor, clerk): outcomes need minutes, a different document class. The next crawler feature.
- **A saved multi-town list, delivered Monday by email or as a table** (editor, $50–75/mo); statewide alerts (organizer). The paid tier; email alerts are deferred by the owner.
- **Chapter 61A land as its own topic** (farmer, editor). A scope decision for the owner: a new keyword topic and label.
- **Who finally votes, and when, on every bylaw hearing** (retiree): the write-ups say it when the agenda does; a standing "the Planning Board recommends, Town Meeting adopts" line needs the next warrant date, which the carry-forward now supplies when a write-up names it.
- **The one-line view as one line, saved towns, "This week" by date, Add to calendar in the ticket** (style director's next three). A day's design work.
- **Two pre-existing failures in `tools/test_watch_api.mjs`** (the email digest and its unsubscribe link, email alerts being off). To fix with the email work.

## Round 8

Re-score the editor and the clerk (the two 3s) on the same tasks, and bring back the data-center analyst and the land-use attorney from round 5 for the Attorney General pages and the feeds. Keep the style director.
