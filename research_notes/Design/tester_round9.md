# Round 9: the four paying personas and the style director against the reorganized site (Oct 16, 2026, evening)

Between round 8 and round 9 the site was rebuilt against `layout_for_humans.md` (measured at 1366 and 390 px: one grid per list, the day printed once, the status in one column, one right edge, spacing from the scale, one measure), the data-center ledger went up at `/attorney-general/data-centers` with a CSV, the afternoon re-check of towns meeting in the next three days went on the schedule (2:29 pm, `ops/recheck.sh`), and every town we can't read says why beside its name. Round 9 put the same four paying reviewers and the style director on the live site (commits c2bc947 to b97f2c7). Reports and screenshots are in the session scratchpad (`value-test/round9/`); the style director's note is `style_director_round9.md` beside this one.

## Scores before the fixes

| Reviewer | Who | Score | Would pay | What they trusted | What broke trust |
|---|---|---|---|---|---|
| Editor | Managing editor, 12 Plymouth County towns, laptop | 3/5 (was 3) | $40/mo for a twelve-town Monday feed by RSS or email, once the three dark towns are read and the town list sticks | County filter to twelve meetings in two seconds; Copy this list and Download CSV fixed; every fact checked right (Plymouth Art. 16, Marshfield Art. 6, Carver); the time column, date rules and the status at the right | Search forgot her twelve towns; Plymouth's Article 16 listed twice, the stub leading the alerts preview, the calendar file and the CSV; Marshfield Art. 9 and Plymouth Art. 24 (petitions) still missing or a quote tail; boilerplate above every headline |
| Analyst | Data-center site selection, laptop | 3.5/5 (was 3) | $150/mo for the ledger and CSV once the contradictory rows are fixed; $300 with a three-state feed and a changelog | The ledger: "sixty-three sourced rows with confidence notes and a CSV replace my spreadsheet and the clipping service"; Gill, Spencer and Shutesbury rows identical to their sources; Hopkinton RI and Northfield meetings exact | Shutesbury's ban and Lysander read "Not in effect" in one column and "In effect" in the next; a proposed term in the CSV's in-effect field; no three-state topic alert; the ledger not linked from Topics; Northfield's town page listed Oct 27 above Oct 20 |
| Attorney | Land-use partner, Worcester, laptop | 4/5 (was 3) | $50 a seat today for the ledger and rulings CSV; three seats at $100 when a list of towns can be delivered | Worcester County in a minute: twelve towns, seventeen items; Leominster and Templeton rows right against the agenda and the letter; the notes "would survive a paralegal's memo"; topic CSV with county, item, status, clean links | The county choice not in the URL; three data-center votes the ledger lists but Upcoming cannot show (Charlton, Uxbridge, Auburn: undated or unheld warrants); unread towns and reasons only on hover; Templeton's estimated date unflagged; no Copy citation on the tables; city rows mixed into "Every ruling"; Worcester's page said Town Clerk |
| Developer | Solar and storage developer, nine towns | 4/5 (was 3.5) | $200/mo for one watchlist of nine towns, a daily email or Slack post, the CSV | "Day headings, the time column, the status column and One line each let me read 119 items in 71 towns in two minutes"; Rochester, Lakeville and Harvard checked right; alerts in three clicks with webcal, RSS, JSON and a webhook box | No town filter on /upcoming; "Show later meetings" folded; Westford's Oct 26 warrant only as "Also ahead"; Dartmouth's warrant under Select Board in Search; one hearing listed twice |
| Style director | Fonts, layout, flow and feel | taste 9/10, usability 8.5/10 (was 8.5/8.5) | n/a | "The lists scan like a results table now": every status word at one x (98 of 98 on /upcoming), each day printed once (32 "Mon Oct 19" became one), one right edge, the one-line view one line at 50 px (was 148 to 272), 8,031 px a page (was 15,302), dark mode "to the digit" | Search unticked its own "Meetings still ahead first"; the ledger seven columns and 264 px rows; /topics without the view switch; the town page's rail 58 px below the H1; three speaking-rule stamps on 33 of 57 meetings; the one-line prefix as uncopyable CSS text |

## What changed the same evening (commits d0ba15a to 8992974, live Oct 16)

**Lists.** The speaking rule is one short line under a meeting's items, not above its first headline. The one-line view's prefix is real text with the town linked, and the board is not repeated when the headline names it. A Town filter and "Only my towns" (for a device with alerts) beside the county filter and the view switch on /upcoming and every topic page; the choice in the address bar; with a county chosen, the towns in it we can't read, grouped by reason, under the count; the next 30 days in view before "Show meetings more than 30 days out", and that count follows the filter. "New to this town" in grey in the meta line.

**Ledger.** Four columns (town, measure, dates as a list, status and what happened). A proposed measure's term is kept apart from in-effect dates on the page and in the CSV (`proposed_term_from/to`); a row in effect with no start date says so. Sources named (Attorney General letter, Warrant, Agenda, News report). Templeton's decision date carries its note (the clerk's posting date) on the page and in the CSV. Copy citation on every row. The state name searchable, every town linked, the data-centers topic page links the ledger above the fold.

**Rulings.** The Attorney General's decisions in the main table; court rulings and city ordinances in their own table under it; a County filter; Copy citation on every row.

**Town pages.** Meetings in date order (Northfield). The "Next meeting on our list" line cut, since the day heading and time column say it. The rail starts level with the H1. A city we can't read says City Clerk.

**Search.** "Meetings still ahead first" stays checked on a shared link and an uncheck sticks. The towns added last time come back. The count is the results' heading. A warrant posted under a board's listing files under Town Meeting in the index.

**Duplicates.** Plymouth's Article 16 and Southbridge's Section 8.11 were each flagged more than once; the extra matches carry the item's write-up and the lists show them once.

## Not done, and whose it is

- **One watchlist for any towns, delivered by email or Slack** (editor $40, analyst $150 to $300, attorney $300, developer $200). The paid tier and the email key: the owner's.
- **Unread towns** (Duxbury, Hanover, Middleborough for the editor; 18 in Worcester County for the attorney): bot checks we will not bypass; the unblock requests wait on the owner.
- **Three data-center votes the ledger lists but Upcoming cannot** (Charlton's Oct 19 Special Town Meeting, Uxbridge's Oct 27 Town Meeting, Auburn's Article 20): Auburn's and Uxbridge's warrants print no date we can read and Charlton's warrant is not a document we hold. Data work: a date read from the listing's own words, or a hand-dated warrant.
- **Petition articles** (Marshfield Art. 9, Plymouth Art. 24, Carver's 6:05 citizens' petition, Westford's Oct 26 warrant): the matcher caps a long warrant at five items per topic, and a one-line agenda carries no words to match. Writer and matcher work.
- **A three-state topic alert, a weekly option, a changelog of ledger rows, a date range on Upcoming**: design work on the alerts flow, after email.
- **Posted time per item**: the crawler reads each listing and can keep the posted time; per-platform adapter work.

## Scores across rounds

| Reviewer | R5 | R6 | R7 | R8 | R9 |
|---|---|---|---|---|---|
| Analyst | 2.5 | 3 | n/a | 3 | 3.5 |
| Attorney | 2.5 | n/a | n/a | 3 | 4 |
| Editor | n/a | 3 | 3 | 3 | 3 |
| Developer | n/a | 3 | n/a | 3.5 | 4 |
| Style (taste / usability) | 7 / 7 | 8 / 7.5 | 8.5 / 8 | 8.5 / 8.5 | 9 / 8.5 |

The layout work moved the three reviewers who read lists (attorney, developer, style director). The editor stayed at 3 on three things: her towns forgotten (fixed), phantom items leading the alerts (fixed), and three towns we cannot read (the owner's). Every paying reviewer's "to 5/5" still ends with the same line: a list of many towns delivered to them.
