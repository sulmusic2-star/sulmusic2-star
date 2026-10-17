# Round 11: the owner's direction, then six reviewers (Oct 17, 2026, afternoon)

The owner looked at the site after round 10 and asked for less on every page: /towns showing only the states until you open one, Biggest stories built from any towns you type in, and every page simpler and clearer for people rather than machines. The rebuild (commits 003cfab to ff67b49) put every page in one centered column, every meeting, story and record in a box, the legal pages as one-line records that open in place, and the filters behind one tap. Round 11 put a resident on a phone, the analyst, the attorney, the editor, the developer and the style director on that build. Reports and screenshots are in the session scratchpad (`value-test/round11/`).

## Scores

| Reviewer | R10 | R11 | What moved them | What still holds them |
|---|---|---|---|---|
| Resident (Carver, iPhone, new this round) | | 4 | Her town, the room and "anyone can attend and ask to speak" in three taps; Rulings answering her question in three boxes | No email or text alerts; "warrant", "40R" and statute numbers; the battery answer at the top of Rulings not matching the table |
| Analyst (data-center site selection) | 4 | 4 | The ledger grouped by status and cited in one click | One feed of his towns across three states; the ledger and Coming up disagreeing on Auburn, Lysander and Chicopee; "ban" for a moratorium |
| Attorney (land-use, Worcester) | 4 | 4 ("nearer 4.5") | County-filtered rulings sent as a link, with citations that paste | Data-center votes on Coming up without article numbers; Templeton's date window lost in the paste; counts and the CSV ignoring the filters; Sunpin and the consolidated permit missing from the answer page |
| Editor (12 Plymouth County towns) | 3.5 | 4 | "Only my towns" in one click to four boxes with PDFs | Four towns we can't read looking quiet; "Mentions zoning: …" quotes as headlines; Search titles and snippets |
| Developer (nine towns, solar and storage) | 4 | 4 | Nine towns plus neighbors, energy only, one screen | A shareable Your towns link; a paid digest with a price; "attachment text" rows; "New to this town" on items with a history |
| Style director (taste / usability) | 9 / 9 | 8.5 / 8 | The owner's direction carried out cleanly: one column, one hairline box, records that open | Uneven padding inside boxes; Carver 413 px wide on a phone; the Stories Add race; wording that reads machine-made |

The style director scored against the owner's new direction, not the old refuse list, so the drop from 9 is a change of yardstick as much as of the site.

## What changed the same afternoon

- **Rulings page.** A fourth box, New in 2026: Sunpin (SJC, Jul 14, 2026) and the consolidated permit (every town since Oct 1, 2026; a decision within 12 months or the project is approved). The count sits under the boxes; the glossary moved to the end. Gill's box says the battery half of its article was struck.
- **Rulings list.** Per-year counts and the download follow the filters ("Download what's shown"); the count is the Attorney General's rulings only. Court rulings print in court form; a month-only date reads "Mar 2026"; Templeton's decision window ("decided between Sep 14 and Sep 22, 2026; Sep 22 is the Town Clerk's posting date") stays in its citation.
- **Ledger.** The effective-date sentence follows G.L. c. 40A, § 5 (a town's moratorium counts from the Town Meeting vote once approved and posted). County and deciding body as labeled rows, "How sure" in the same list, sources one per line, the row's key the date that matters under its status heading, and the next meeting with a data-center item from Coming up.
- **Lists.** Counties named within their state ("Onondaga County, NY"; old `county=Worcester` links still work). Several towns with commas in the Town box. "Only my towns" names the towns, lists the ones we can't read with the reason, and puts `mine=1` in the address bar. Empty "Next 7 days" or "Later" headings go. The agenda link moved onto the meeting's top line in the short list. "Mentions…" lines no longer quote a fragment of the agenda; rows that are only bylaw text quoted in an attachment are gone; headlines say moratorium where the agenda does.
- **Write-ups.** The 80 upcoming items with no write-up got one from four writers, each checked against its agenda (article numbers in Town Meeting lines, petitions named).
- **Stories.** Towns, neighbors, dates and topics all in the link; a pick from the list and Add no longer race; "First time on an agenda" only for an item with no earlier meeting.
- **Town pages.** "Also ahead" as the same boxes as stories, with a short status ("Moved from Oct 21", "Asked to move here"); Next door one town per line, so Carver fits a phone again. "/towns" counts read "2 meetings" in grey, not a badge.
- **Words.** "The agenda prints no other rule", "we don't know yet whether it agreed", "the town's listing checked", the /towns legend and the Search "Try" line after a search are gone; the Search heading reads "71 agendas with "data center moratorium" · 15 coming up, shown first".

## Not done, and whose it is

- **Email or text alerts, and a paid multi-town digest with a price.** Every paying reviewer's last item and the resident's. The email key and the paid tier: the owner's.
- **Towns we can't read** (Duxbury, Hanover, Middleborough and the rest): bot checks we will not bypass; the unblock requests wait on the owner.
- **One feed of your towns across three states** (the analyst's RSS/JSON ask) and a ledger changelog.
- **Search titles and OCR snippets** ("STM Warrant 10.19.26", "By Kelly A McElreath at 12:36 pm").
- **Phone first screen** on Rulings and the ledger (first record near y 630 and 710), and one inner grid shared by every list.
- **NY and RI rulings.** Researched (scratchpad `research/ny_ri_rules.md`): large projects there go to a state board (ORES in New York, the Energy Facility Siting Board in Rhode Island) that can override town rules, and neither state reviews town bylaws the way the Massachusetts Attorney General does. Waiting on the owner before any of it goes on the site.
