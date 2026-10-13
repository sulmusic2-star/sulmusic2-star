# Tester round 4: the old site against the new, same people, same tasks (Oct 13, 2026)

Three of the round-3 testers, memory wiped, each ran the same tasks on the production site (the old design, agendaahead.vercel.app, still labelled "351 Watch") and then on the preview that carries the round-3 fixes and the new mark (4e6e7f4). The order was old first, new second, with instructions not to let one color the other. Reports and screenshots are in the session scratchpad (`value-test/round4/`).

## Scores

| Tester | Old site | New preview | Keeps |
|---|---|---|---|
| Dana, 58, Plymouth, phone | 2/5 ("none for meetings still ahead" in Plymouth, four days before its vote; gave up on two of three tasks) | 3.5/5 (vote real, Sat 8 am at Plymouth North, in 15 seconds; Carver's postponement request in 10) | New |
| Marcus, weekly reporter, six towns | 2/5 (fragments cut mid-list, "date not listed" on a warrant whose first line is the date; saves ~20 of 55 minutes) | 3.5/5 (six towns with times, rooms, stage and postponements in a minute; saves ~40 of 55) | New |
| Jordan, product designer | taste 5/10, usability 3/10 (stat ledger, triplicate CTA, pasted agenda text, a 125,000-pixel towns page) | taste 7/10, usability 7/10 (up from 6 and 6 in round 3) | New |

The old site scored lower for every tester on every task, which is the calibration the protocol requires before a tester round counts.

## Checked against the source documents (Marcus)

Right: Carver's two continuance requests; Plymouth Articles 14 to 16 (the Sep 22 minutes confirm the 4-1 vote on 14 and the abstention on 15); Northfield's Oct 20 public hearing. Soft: Burrillville "Vote" where the agenda says "consider and act on a petition"; "the Select Board discussed Article 16 on Sep 22" where its minutes show a 5-0 vote to recommend. Wrong: Kingston and Northfield shown as "Online meeting" when both are hybrid (fixed where a write-up names the room). Missed: Carver's 40R smart-growth article and two Wareham housing articles, outside the topics we track (40R added to the housing keywords).

## What still fails, and whose it is

- **Email alerts** are the one change all three named first. The flow is built; the Resend key is not set in Vercel, so the site says "Email alerts are coming" and offers a calendar feed. Owner.
- The mark showed two lines instead of three in the nav (a CSS shadow collapsed the third), so it read as a hamburger; now an inline SVG. The fold chevron doubled with the browser's marker; now one glyph. The footer sat on a wider gutter than the content. Fixed.
- "Plym" + Continue on the alerts page said "We don't know that town"; now the one town that starts that way. Fixed.
- A calendar-only list greeted people with "Alerts on" because the API's empty webhook stub counted as a channel; now "Calendar feed on". Fixed.
- Desktop is a phone layout stretched (Jordan); a two-column desktop with a sticky town box is the next design step, not a blocker.

## Launch call

The preview beats production for every tester on every task, the write-ups pass an independent reader and the checker, and nothing on the remaining list changes what a visitor can do. The redesign is ready to replace production once the owner says so; email alerts turn on the moment the key is set, without a redeploy.
