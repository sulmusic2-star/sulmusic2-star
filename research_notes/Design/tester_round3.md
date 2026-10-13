# Tester round 3: fresh eyes on the preview (Oct 13, 2026)

Four simulated testers with no memory of the site, each following `tester_protocol_v2` (five-second look, scan view, patience rules, alternatives first, scored on actions), browsing the preview at 390 px and 1366 px with real Chromium. Full reports and screenshots are in the session scratchpad (`value-test/round3/`); this is the record of what they found and what changed because of it. The preview they saw was 24aac7b; the fixes below shipped in 318b095 and the commits after it.

## Scores

| Tester | Who | Score | One change that would raise it most |
|---|---|---|---|
| Dana | 58, Plymouth, phone, never been to a meeting | 3/5 | Time, place and "to speak, ask the Town Clerk by Thu Oct 15" at the top of the Plymouth item |
| Marcus | weekly-paper reporter, six towns, laptop | 3/5 | List every item on a covered agenda, one line each, and never hide a town's earlier meetings behind "Nothing on our topics" |
| Priya | solar permitting manager, 25 towns | 3.5/5 | A county-and-topic watchlist delivered to Slack or email the day an agenda posts |
| Jordan | product designer, no civic interest | taste 6/10, usability 6/10 | Make "Get alerts" true or say so up front; one status style and one accent; items that tap through |

## What held up

- Against the alternatives, every tester got more in less time: Google and the town sites gave Dana nothing in two minutes; Marcus got five publishable briefs in three minutes against zero from six town sites ("about 90 minutes a week saved, 20 minutes of PDF checks left"); Priya had Carver and Rochester status in under a minute each against two analyst-days a month.
- The write-ups, the "Before this:" history, "Postponed" and "Next door:" up front, "Checked Oct 13", the Attorney General page ("the page I'd screenshot for my VP"), honest empty states ("We can't read Middleborough's agendas yet"), no account, no icons.
- Jordan: "Not AI. It's the GOV.UK design system with the green swapped for purple." Barlow over Barlow Semi Condensed "is a real choice, not Inter."

## What failed, and the fix

| Finding | Fix |
|---|---|
| Plymouth Town Meeting page had no time or place; the warrant's first page says 8 am, Plymouth North High School (Dana, Marcus) | Meeting time and place come from the written brief when the agenda header gave none (`when_time`, `when_place`); the speaking rule sits under the date on meeting pages |
| "Postponed: … moves to Oct 27" stated as fact where the agenda shows the applicant asking (Dana, Marcus, Priya, the reader audit) | Twelve headlines rewritten as "request to move it to Oct 27"; the stage reads "Asks to postpone to Tue Oct 27"; no speaking line on those |
| "Vote" on "may vote to amend" (Marcus, Priya) | "Possible vote" when the agenda allows a vote without promising one |
| Alerts snapped mid-word ("We don't know 'plym'"), then said "Alerts on" without asking how; buttons promised email that isn't configured (Dana, Priya, Jordan) | No error while typing; "Calendar feed on for …" until an email or chat channel exists; buttons say "Get Plymouth alerts"; the browser datalist on the home page replaced by a visible suggestion list with a "Which one?" for names in two states |
| Three different "coming up" counts for one topic (Priya) | The topics table counts meetings, as the topic pages do |
| Attorney General page reachable only from How it works (Priya) | Linked from the footer |
| Town page said "Nothing on our topics" with earlier meetings folded away (Marcus) | The two most recent meetings show under "Most recent" when nothing is coming up |
| Auburn's "Electronic Data Storage" moratorium missed (Marcus) | Keyword added for the crawler (`data storage facility/center/project`), checked against every cached document |
| Status words as plain grey text, selected filters black, browser triangles on folds, items that don't tap (Jordan) | One status mark (a dot, filled when the board acts), purple selected filters, chevrons on every `details`, headlines link to the meeting page |
| "per our records", "(in our records)" asides; OCR cent-sign bullets in search snippets (Marcus, Priya) | Stripped at render and in the search index |
| "on its new business, with no verb" (Marcus) | Rewritten |

## Not fixed yet

- Every item on a covered agenda, one line each (Marcus's one change; the P2 "full hearing calendar"); amended-agenda detection; CSV export; a county-and-topic professional watchlist to Slack or email (Priya's one change).
- Coverage: Kingston's Town Meeting warrant and boards beyond the Planning Board; Middleborough.
- The four-dot mark (Jordan: the one element that "smells generated").
- Email alerts need the Resend key in Vercel.
