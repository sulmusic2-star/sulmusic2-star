## Section 4: a design brief for the AI

Paste this at the top of any design session for Agenda Ahead.

1. You are writing HTML and CSS for Agenda Ahead, a static site that tells residents of Massachusetts, New York and Rhode Island towns what their town boards are about to decide. Read `DESIGN.md` (the mock notes) and `research_notes/Design/human_first_spec.md` before you touch a file. The spec wins over your defaults.
2. The reader is a neighbour on a phone who wants three things: what the board will decide, when, and whether they can go and speak. Everything else is secondary and sits lower or folds.
3. Every page opens with the decision in one plain sentence. Counts, check times, filters and controls go to the end or into one "Narrow this list" disclosure. The first meeting must sit inside the first 500 px at 390 px wide.
4. A meeting is a dated paragraph, not a card: date and time in a left column (stacked on phones), subject as the heading, one to three sentences, one verb-first agenda link, then a folded "Details". Rows are separated by 1 px hairlines. Cards, pills, chips, washes and shadows are not allowed.
5. Status is said in the sentence ("The Planning Board votes on this.", "Anyone can go and speak."). The only coloured word is a changed date in amber, or "Canceled". Dots, tags and labels such as "Hearing" or "Possible vote" never appear in the open.
6. Explain a term the first time it appears in a row: "a temporary ban (a moratorium)", "an affordable housing permit (40B)". Never a bare acronym first.
7. Sentences under 25 words, "you" for the reader, active verbs, no adjectives that sell. Say "The agenda doesn't give a time", not "No time listed". Write from the reader's side, never the system's ("checked from the agendas towns post online" is banned in the open).
8. Type: Public Sans only, self-hosted from `/fonts`, Regular, Italic and SemiBold. Sizes 40/32 (h1), 24 (h2), 20 (dates and leads), 18 body at 1.55, 16 small. Nothing under 16 px. Sentence case headings. Do not substitute Inter, Roboto or a system font.
9. Colour: paper, ink, muted, rule, panel, plum (the mark, the one button, focus), amber (a changed date). Seven roles, light and dark values, nothing else. Plum appears at most three times on a page.
10. Spacing on a 4 px grid: 4, 8, 12, 16, 24, 32, 48, 64. One 760 px column, plus a 192 px date column from 760 px up. Running text at most 66 characters a line. 16 px gutter on phones.
11. Motion: the Details triangle turns; a meeting reached by link fades its highlight once. Nothing else moves, and `prefers-reduced-motion` turns that off too.
12. Links are underlined text inside sentences. One solid plum button per page, and it says what happens ("Follow Carver's meetings"). Only links and buttons are clickable. No arrows after links, no middle dots between fields, no all-caps labels, no numbered markers except the three steps in How it works.
13. Each subject list, slogan or check-time appears once per page at most.
14. Build from today's real rows (Carver, Somerset, Northampton), never placeholder meetings. Before you call a row shape done, run it through every stage: hearing, continued hearing, vote, possible vote, mention, signing, Town Meeting article, state filing, moved, canceled.
15. Keep the quality floor without announcing it: no horizontal scroll at 320 px, 44 px controls, visible focus ring, AA contrast in light and dark, skip link, `<time datetime>` on dates, tabular figures, curly quotes, `<a>` for navigation.
16. Do not add anything: frameworks, a second script, external requests, icons, illustrations, emoji or a stats row.
17. After each build: run `slop_lint.py` and the sentence-length check; screenshot home, /upcoming, /ma/carver, a meeting page and /watch at 390 and 1366 in light and dark; look at them and list what you would remove. Remove one thing.
18. References for the look: GOV.UK content pages, the mock screenshots in `design2/mock/shots/`, a posted town agenda. Not: a SaaS landing page, a dashboard, a news app.
19. If the brief and your instinct disagree, follow the brief and say so in one line. If a sentence needs a fact you don't have, write a shorter sentence or ask. Never invent a date, a board, a place or a quote.

