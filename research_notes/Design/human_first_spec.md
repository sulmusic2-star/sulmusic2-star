# Human-first front end: the spec

Written Oct 28, 2026 from three inputs: a structural critique of the live pages, a study of how GOV.UK, USWDS, Boston.gov, Documenters, Councilmatic and the morning newsletters present dated civic items (scratchpad `design2/civic_rules.md`), and a static mockup of the home and Carver pages built from real data (`design2/mock/`). The owner's brief: the site reads robotic and confusing; it should read like a neighbour who went to the last meeting.

## What was wrong, measured

- The list on /upcoming starts at 874 px on a phone, after 543 words of counts, filters and a view switch.
- A row reads as a database record: time, town, board, place, "Agenda", then the subject as a link, then a status noun with a dot. Rows are 178 px cards for identical kinds of items.
- Labels ("Hearing", "Discussion", "Possible vote", "Mentioned", "Filing") are code words explained somewhere else. Verb-shaped tags read as buttons.
- Pages talk about the system ("Checked Oct 28, 7:18 am", "60 items at 44 meetings in 37 towns", "Titles only / With details", "website blocks automatic reading").
- The meeting page leads with the board's name; the decision is below the fold.

## The rules we now build to

1. Every page opens with the decision in one plain sentence. Counts and the checked-time go to the page end.
2. A meeting in a list is a dated paragraph, not a card: the day and time in a left column (stacked above on phones), then the subject first, then one to three sentences, then one verb-first link to the agenda, then "Details" folded.
3. Status is said in the sentence ("The Planning Board votes on this.", "Anyone can go and speak."). A coloured word appears only when something changed: Moved, Canceled, Withdrawn. No dots, no stage tags in the open.
4. A term is explained the first time it appears in the row: "a temporary ban on new data centers (a moratorium)", "an affordable housing permit (40B)", "a wetlands permit request".
5. Sentences under 25 words; "you" for the reader; active verbs; no labels where a sentence belongs ("The agenda doesn't give a time", not "No time listed").
6. The meeting page's heading is the matter, not the board. Then when, where and whether you can speak as sentences, then the one button.
7. The follow page says what you get and how often before it asks for anything. Its heading is a statement.
8. Filters stay off the first screen: one "Narrow this list" disclosure that opens to county, subject and town. The view switch goes; details fold per meeting instead.
9. "Next door" names what's coming up next door in a sentence; a town we can't read is "no agendas we can read yet", with the reason one tap away, not a diagnostic in the row.
10. One family: Public Sans (OFL 1.1), Regular, Italic and SemiBold, self-hosted like Barlow was. Sizes 40/32 (h1), 24 (h2), 20 (dates, lead), 18 body at 1.55, 16 small; nothing smaller. Spacing on a 4 px grid; 66ch measure; a 760 px column plus a 192 px date column from 760 px up.
11. Colour: paper, ink, muted, rule, panel, plum (mark, the one button, focus), amber for a changed date. Green and red go.

## How a row is composed

From the meeting's lines, ranked as today:

- Heading: the main item's subject, capitalised, no leading article: "Solar farm at 235 Main Street", "Temporary ban on new data centers (a moratorium)". Canceled meetings: "Canceled: …". It links to the meeting's page while the meeting is ahead.
- Sentence 1, by the main item's stage: hearing becomes "The {Board} holds a public hearing. Anyone can go and speak." (continued becomes "The {Board}'s hearing continues; it started {date}."); vote becomes "The {Board} votes on this."; possible vote becomes "The {Board} may vote on this; the agenda doesn't say for sure."; discussion becomes "The {Board} talks about this. No vote is listed."; mention becomes "It comes up on the {Board}'s agenda, but nothing is set to be discussed or decided."; signing becomes "The {Board} signs its decision."; Town Meeting becomes "Town Meeting votes on this (Article n). Registered voters decide."; state filing becomes "Filed with the state; the Conservation Commission hasn't heard it yet."
- Sentence 2: the write-up's "what", when it adds something and is under 260 characters.
- Sentence 3: "Also on the agenda, it talks about X and votes on Y." for the other items (at most three named, "and n more").
- Sentence 4: where. "It's at Town Hall." / "It's online." / "It's at Town Hall, or online." The agenda's own speaking rule, when it has one, replaces the generic "anyone can go and speak".
- Then any change: "Moved to Tue Nov 10 (was Oct 27). The applicant asked." in amber words. "The town canceled this meeting."
- The link: "Read the Oct 28 agenda (PDF)" / "Read the warrant" / "Read the state filing".
- Details (folded): the item rows as before, with their stage words, facts, agenda wording and "New on an agenda".

The home page's "This week" and the Biggest stories list use the same row with the town in the date column.

## Pages

- Home: h1, one sentence, the town box with "Find my town", "Or try Carver, Amherst or Clay, NY. It's free and you don't need an account.", then "This week" (three rows), then one real example of a town's lead, then How it works (three steps) and the subjects as one sentence.
- Town page: h1 "Carver, Massachusetts"; a lead of at most three short sentences (what's coming, what moved, next agenda); "We checked Carver's agendas this morning at 7:03." small; the Follow button with what it gives; "Coming up" rows; "The last two meetings"; folded: earlier meetings, Town Meeting warrants, the state's rulings; "Next door" as a sentence; about this page with the CSV.
- Coming up: h1, one sentence, "Narrow this list" folded, the rows by day, the count at the end.
- Meeting page: h1 = the matter; the row's sentences as the lead; when / where / can you speak / agenda as a plain list; the Follow button; the items with their details open.
- Follow: "Follow a town" with the sentence about what arrives, then the town box.

## Checks before it ships

slop_lint.py on every built page; the four test files; screenshots at 390 and 1366 of home, /upcoming, /ma/carver, a meeting page and /watch; the first meeting row inside the first 500 px on a phone; no horizontal scroll at 320; every control 44 px or taller; nothing under 16 px.
