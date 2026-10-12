# Agenda Ahead: design brief for humans

Draft in progress (2026-10-12). Sections being filled in.

## Live-site audit (Playwright, Chromium, 1440x900 and 390x844)

Measured on https://agendaahead.vercel.app on 2026-10-12:

- Home: 5,051 words, 181 links, 12,973 px tall at desktop and 26,951 px (about 32 phone screens) at 390 px.
- Home at 390 px: 189 tappable elements, 104 of them under 24 px in one dimension; most body text is 12.8 to 15 px.
- /watch: 467 town checkboxes, 946 interactive elements, no email option, a webhook URL field in the main form.
- /ma/amherst: crawl-status table ("Boards we read", "Last successful crawl") sits above the upcoming items; on a phone no agenda item is visible above the fold.
- Brand on the page and in the title tag is "351 Watch", not Agenda Ahead.
- No search across agendas (/search returns 404); the only search box filters the moratorium tracker table.
