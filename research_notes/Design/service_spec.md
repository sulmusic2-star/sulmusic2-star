# Agenda Ahead as a public service: the spec (Nov 6, 2026)

Why this exists. After three redesign rounds the owner's verdict on Nov 6 was: the home page is still overloaded with words and information, the maps are bad, the whole site reads as made by AI and is confusing to operate, and the wording is AI. The rounds were judged by reviewers I simulated, so they graded the work by my own rules. This round stops inventing and adopts a design system built by a real team for exactly this job: the GOV.UK Design System patterns (the patterns, not the crown or the name), the most tested plain-language public-service design there is. Where this spec and GOV.UK guidance differ, GOV.UK wins.

## 1. The one rule on words

The site shows the agenda's own words and the facts around them. It does not narrate. Every sentence a program composed ("It's a public hearing, so anyone can go and speak. The town hasn't posted that agenda yet, so there's no time...") goes. In its place: a label, a fact or nothing.

- Headline of an item: the agenda's own line, verbatim, trimmed to about 90 characters at a word boundary, numbering and boilerplate stripped ("Article 12." and "Public Hearing:" prefixes removed, case left as the clerk wrote it unless it is all capitals, then sentence case). Only when no clean agenda line exists does the old computed subject appear.
- Under it, one meta line of facts in plain commas, the label first as its own short sentence: "Public hearing. Planning Board, Tue Dec 8, 7 pm, Town Hall." Labels are fixed words: "Public hearing", "Vote", "Discussion", "Continued from Nov 10", "Canceled", "Time not yet posted".
- "Anyone can speak" appears only as part of the label "Public hearing, anyone can speak" when the agenda says public hearing. "Public comment" when the agenda lists a public comment period. Never a sentence about speaking.
- Then the source link: "Agenda (PDF)" or "Agenda", nothing more. Middle dots, pipes and arrows never appear in meta lines; commas and full stops do. The quote the sentence was built from stays available on the meeting page as a verbatim excerpt.
- No "we" on content pages. No explanation of what the site is anywhere but the About page. No "plain sentence" wording. The footer says "Not a government website." and nothing else about us.
- The town page has no lead paragraph. The meeting page has no lead paragraph. Headings are the content, not a summary of it.

## 2. Pages

**Home** (at most 80 visible words; the map and the stories are gone):
- Black top bar: Agenda Ahead.
- H1: "What is your town about to decide?"
- One line: "Town and county agendas in Massachusetts, New York, Rhode Island, Virginia, Maryland, Michigan and Ohio, read every morning: solar, batteries, data centers, zoning, housing."
- The town box (label "Town or county", button "Search") with autocomplete as today.
- One line of links with counts, comma separated: "This week: data centers (16), solar (33), batteries (18), zoning (45), moratoriums (7), housing (9), cell towers (5)".
- One line: "Or browse by state: Massachusetts, New York, Rhode Island, Virginia, Maryland, Michigan, Ohio" linking to the state pages.
- Footer.

**State page** (/ma, /ny, /ri, /va, /md, /mi, /oh): H1 "Massachusetts", then "This week" items grouped by day (rows as in section 1, town shown), then "Next week", then a one-line link to the state's places list (/towns#ma). The day headings are the only counts on the page, and there is no map.

**Town page** (/ma/carver): H1 "Carver, Massachusetts". A follow button "Follow Carver" and a one-line note "Email or calendar feed. Free." Then H2 "Coming up" rows; H2 "Recent" rows (two); one line "Next door: Plympton, Wareham, Middleborough" as links; one line "Source: carverma.gov, read Nov 6, 7:31 am". For a town we cannot read: one line "We can't read Carver's agendas yet: its site runs a bot check." then the next-door line and the request form (label, input, button). Townships read through their county: one line "Carver's zoning changes reach us through the Plymouth County Planning Commission; its own agendas are not online." then the county's rows.

**Meeting page** (/m/...): H1 is the item headline. A summary list (GOV.UK pattern: bold key, value): When, Where, Board, Public hearing (yes, anyone can speak / no), Agenda (link), Add to calendar. Then H2 "From the agenda" with the verbatim excerpt as a blockquote. Then H2 "Also on this agenda" as a plain list. Nothing else.

**Places** (/towns): a search box, then states as H2 with their places as a plain comma-separated run of links, read ones in normal weight, unread ones followed by "(not read yet)". That is the only status word on the page; it has no map and no counts.

**Coming up** (/upcoming): everything, grouped by day, filter row of checkboxes (state, subject) above. Same rows.

**Topics, Rulings, Trending, Search, Follow, About, How it works**: same type and spacing; each page's intro is one line or none.

## 3. Look

GOV.UK Design System values, applied without the brand:
- Type: the GOV.UK stack without GDS Transport: `"Helvetica Neue", Helvetica, Arial, sans-serif`. Body 19px/1.32 (16px under 640px). H1 48px bold (32px mobile), H2 27px (24), H3 19px bold. No serif anywhere. The site fonts in site/fonts are no longer loaded.
- Colour: text #0b0c0c, links #1d70b8 underlined, visited #4c2c92, hover #003078, focus background #ffdd00 with a 3px black bottom border, secondary text #505a5f, rules #b1b4b6, page white, top bar #0b0c0c with white name, button #00703c green with white text (the GOV.UK button), error #d4351c. No other colours. No red pin. No icons.
- Space: 5, 10, 15, 20, 30, 40, 50 px steps; page max width 960px with 15px gutters (30px above 640px); content column two-thirds on desktop.
- Components: the top bar, the text input (2px black border, 40px high), the button, the summary list, the inset text (left border 10px grey) for the cannot-read line, the back link, plain lists. Rows are a list with a 1px #b1b4b6 rule between them, the headline a bold link, the meta line in secondary colour.
- Nothing decorative: the maps, the masthead date and the brand mark all go. The favicon becomes a plain black square with a white "A".

## 4. Proof before it ships

- Visible word counts: home at most 80; a town page's chrome (everything outside rows) at most 40; a meeting page's chrome at most 30.
- grep of site/**: zero rows containing "we", "We", "It's a", "The town hasn't", "so anyone", "no vote is listed"; zero `<svg class="map`.
- Screenshots at 390 and 1366 of: home, /ma, /ma/carver, a meeting page, a cannot-read town, a via-county township, /towns, /upcoming; no horizontal overflow at 390.
- axe: 0 violations on those pages. Lint (`.claude/skills/de-slop/scripts/slop_lint.py`) clean on them bar place-name title-case.
- Tests in tools/test_*.py pass; python3 build.py passes; the four files tools/ check pass.
