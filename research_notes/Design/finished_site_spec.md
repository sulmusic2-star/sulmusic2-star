# A finished site: the spec (Oct 17, 2026)

The owner: "every page still feels a little confusing, not complete, unfinished, disorganized … study other sites, services, designs." Three studies stand behind this spec (session scratchpad `design-study/`): a page-by-page audit of our site (`audit.md`, 20 ranked problems with quotes and measurements), civic trackers (`civic.md`: GovTrack, Councilmatic, citymeetings.nyc, Documenters, Plural) and polished information sites (`polish.md`: GOV.UK, Mass.gov, USWDS, Redfin, the Weather Service, Stripe, Linear, GetCalFresh).

Their shared finding: the site doesn't look messy so much as unfinished. Features are half-built (email promised, a calendar feed delivered; a placeholder pricing page; four topics with no page; Vercel's raw 404). The same thing is named, counted and drawn differently from page to page (one meeting drawn eight ways, eleven status words, six town pickers, five filter patterns). Pages start differently and end in nothing. The fix is a system every page follows, not more patches.

## 1. One site map, one header

Header, the same words at every width (a row that scrolls sideways on a phone, never renamed or dropped):

**Coming up · Towns · Topics · Rulings · Search**, and **Follow a town** as the one button.

- *Coming up* is the main list. *Biggest stories* is its second tab ("By date | Biggest stories"), so the list has one home. `/trending` keeps its address.
- *Rulings* covers the Attorney General summary, every ruling, town actions, state law and the data-center ledger, as tabs whose labels match their page titles.
- The current section is underlined in the header on every page below it (a town's meeting lights *Towns*; a ledger row lights *Rulings*).
- Footer, three columns: who runs the site and that it isn't a government site; *Explore* (the five sections); *About* (How it works, Follow a town, Privacy, Contact, For website managers). Last line: "Not legal advice. Confirm dates with the town clerk."
- Retired: `/pricing` (nothing to buy; the free line lives on the follow page and How it works), `/alerts-for-groups` (Slack, Teams and Discord become an option on the follow result page). Both addresses redirect.
- Unknown addresses show our 404 page with the header and a town box; `/ma`, `/ny`, `/ri` open their state on Towns.

## 2. Every page starts the same way

1. Breadcrumb, only below a section (state, town, meeting, ruling tabs).
2. H1, one line where possible.
3. A one-sentence summary that states the situation with a number or a date ("5 items at 2 meetings this week, most on solar and battery storage"), not a description of the page.
4. A freshness line: "Checked today at 9:15 am from the agendas Carver posts online."
5. At most one action.

## 3. Every page ends the same way

A page-end strip above the footer: the source (with link) and checked time where the page has one, "Copy citation" where it applies, and "Report a problem with this page". A section never ends in an empty heading: it ends in content, a "See all" link, or a sentence that says what was checked and what to do next.

## 4. One vocabulary

- **Status words** (one look each; purple never means status):
  - *Vote*, *Public hearing*: filled ink dot, ink text.
  - *Possible vote*: hollow ink dot.
  - *Discussion*: hollow grey dot, grey text.
  - *Moved to Nov 4*, *Continued to Nov 4*, *Asked to move*: amber tag, always with the date.
  - *Canceled*, *Withdrawn*: grey text, struck through for canceled.
  - *New on an agenda*: small purple tag in the meta line (replaces "First time on an agenda").
  - Rulings: *Approved* (green tag), *Approved in part* (amber), *Disapproved* (red), *Awaiting a decision* (grey).
- **One label per thing**: topics by their nine names everywhere; "Can't read yet" (one phrase) with the reason; "Follow" for alerts until email exists.
- **One counting unit per sentence, always labelled**: "items" (flagged agenda items) and "meetings". Section totals add up.

## 5. Components, drawn one way everywhere

- **Meeting card** (home, Coming up, Biggest stories, town, topic, search, follow preview): one box with the time, town and board on the first line, the place under it, the item lines with their status, the agenda link. Day headings above the cards in date lists. Only the item titles are underlined links.
- **Story card**: the meeting card's first line plus one item and a grey "why it's here" line; ranked lists show the rank, not a date column, so dates never read out of order.
- **Key facts list**: label column and value column (Applicant, Where, Size, Topics, Earlier on; on the meeting page: When, Where, Watch, Public comment, Agenda, Posted). A missing value says "Not on the agenda" rather than disappearing.
- **Record row** (rulings, ledger, town actions): one line that opens in place, the status tag on the right.
- **Filter bar**: one panel, fields 48 px tall with labels above, closed on phones behind "Filters", the result count as a sentence under it, "Clear filters" at the end.
- **Town picker**: one input with suggestions, the same words everywhere ("Type a town"); the towns a visitor chooses are remembered once and reused.
- **Follow box**: "Follow Carver": one sentence on what you get, one button, and "Add to calendar" as a text link.
- **Empty states**: a sentence that names what was checked, when, and the next step.

## 6. Visual system

- Fonts: Barlow for text, Barlow Semi Condensed for headings and dates (already self-hosted). Tabular figures for dates, times and counts.
- Type scale (desktop / phone): H1 40/32, summary 20/19, H2 26/24, card title 20/19, body 18, small 16, table 14. Six sizes.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, each with one job (polish.md (b)).
- Widths: 560 px text, 840 px lists and tables. Controls 48 px tall, 4 px radius; cards 10 px radius (the owner's boxes), 1 px hairline.
- Color, one job each: ink text and links; grey for meta; panel grey for filter bars, fact boxes and the footer only; purple for the one primary button, focus and the wordmark; green, amber and red for outcomes and schedule changes only.
- Wordmark: three stacked bars, the middle one purple and longer, beside "Agenda Ahead" in Barlow Semi Condensed Bold. Favicon: the bars alone.

## 7. Page by page

- **Home**: town box first ("Type a town"), then "3 to watch this week" (story cards with their reasons), the nine topics as links, and "See everything coming up". The summary names all the subjects in plain words.
- **Coming up**: tabs *By date* | *Biggest stories*; filter bar (County, Town, Topic); the count sentence; 7 days in view, later weeks folded by week.
- **Town page**: H1 "Carver, MA"; summary sentence with counts and the next date; freshness line; tabs *Coming up* | *Past meetings* | *Rulings and town actions*; follow box; next door as a short list; "dates from earlier agendas" inside Coming up with a small tag, not a separate section.
- **Meeting page**: H1 board and town; key facts list (When, Where, Watch, Public comment, Agenda, Posted); each item with its status and one sentence on what it means, its own key facts, and "Earlier on" as a short timeline; the words used on the agenda as a definition list; follow box; page-end strip with the source.
- **Towns**: the town box full width with a Find button; states as boxes, Massachusetts open.
- **Topics**: nine topics, each its own page on one template; the data-center topic links the ledger.
- **Search**: results first; filters folded; snippets cleaned of OCR noise; titles from the write-ups.
- **Rulings**: tabs (Summary, Every ruling, Town actions, Data-center ledger, State law) whose labels are the page titles; counts that add up; the law page's table fixed on phones.
- **Follow a town**: one question per screen; says what you get today (calendar, a private page, and Slack, Teams or Discord), no "coming soon" lines; email appears when it is switched on.
- **How it works** split into How it works, Privacy, Contact and For website managers, each its own page.

## 8. Done means

Every page passes: the same frame (start and end), no unfinished wording, no empty headings, one status vocabulary, numbers that add up, no horizontal scroll at 390 px, the de-slop linter clean, and a fresh reviewer round (newcomer, editor, attorney, developer, style director) scoring it before the owner sees it.
