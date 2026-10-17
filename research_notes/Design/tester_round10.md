# Round 10: the same five reviewers against the overnight fixes (Oct 17, 2026, morning)

Round 10 put the editor, the analyst, the attorney, the developer and the style director on the build that carried the round-9 fixes (commits d0ba15a to 5d92771). Reports and screenshots are in the session scratchpad (`value-test/round10/`). This is the last simulated round for now: the owner reviews the site next.

## Scores

| Reviewer | R8 | R9 | R10 | What moved them | What still holds them |
|---|---|---|---|---|---|
| Editor (12 Plymouth County towns) | 3 | 3 | 3.5 | The county view and the flagged 7-day CSV "beat twelve AgendaCenter tabs"; Search kept her twelve towns; Article 16 listed once | Three towns unread (Duxbury, Hanover, Middleborough) and Kingston read for one board; petition articles without headlines; a Monday email |
| Analyst (data-center site selection) | 3 | 3.5 | 4 | The ledger "I cite in one click", In effect and Status agreeing on all 63 rows, proposed terms out of the in-effect fields, NY and RI towns linked | One data-center feed for three states, alerts for any towns, a ledger changelog |
| Attorney (land-use, Worcester) | 3 | 4 | 4 | The county held in the address bar, unread towns with reasons under the count, City Clerk for Worcester, decisions apart from court rulings | Data-center votes the ledger knew but Upcoming didn't (Uxbridge, Auburn, Charlton); citations that lost their caveats or links when pasted |
| Developer (nine towns, solar and storage) | 3.5 | 4 | 4 | The Town filter in the address bar, Search keeping nine towns, Dartmouth under Town Meeting | One list of any towns delivered by email or Slack, with a price; Westford's Oct 26 warrant |
| Style director (taste / usability) | 8.5 / 8.5 | 9 / 8.5 | 9 / 9 | Status words at one x on every list, the rail level with the H1, a one-line view that copies cleanly | The speaking line hanging under the last item; phone tables squeezing summaries to 150 px; "Only my towns" never appearing |

## What changed the same morning (commit 6b25e55, live Oct 17)

- **Warrants dated from their own heading.** A warrant whose running head prints "October 27, 2026 Fall Annual Town Meeting" takes that day when its listing gave no date (Auburn) or the posting day (Uxbridge, Colrain). Uxbridge's and Auburn's data-center articles now show on /upcoming for Oct 27. Charlton's Oct 19 warrant is not a document we hold.
- **Speaking.** Lists print only the agenda's own rule, keyed "Speaking:", above the items; the generic stamps are gone from lists and stay in the meeting page's ticket. Any stage naming a hearing gets the hearing rule; 32 Representative Town Meetings say elected members vote; Plymouth's rule keeps the Moderator's permission; no Zoom link is promised for a Town Meeting.
- **Citations.** Court rulings in court form ("489 Mass. 775 (2022)", "Mass. Land Ct. Mar. 2026"); absolute links; the date caveat and a link to the row kept in the ledger's citation; Brookfield's letter marked revised.
- **Ledger.** A proposed measure prints the dates it has and stops; "How sure" one word beside the status with the reason behind a fold; sources named with their dates; filter in the address bar; county names searchable; Templeton, Uxbridge, Hopkinton and Lysander corrected against their sources; plain words in the notes.
- **Rulings.** Grouped by year; the County filter covers court rulings and city ordinances too; filters in the address bar.
- **Lists and Search.** A day that has passed since the morning build is hidden; counts are meetings still ahead; topic pages show 30 days; "Only my towns" uses every alert's towns and the towns added in Search; Search shows and searches remembered towns on arrival; filters in one row; "+3" reads "and 3 more items"; copied links with spaces encoded; CSV topics per item.
- **Phones.** The summary cell takes the full width on both Attorney General tables.

## Not done, and whose it is

- **One list of any towns, delivered by email or Slack, with a price.** Every paying reviewer's last item. The email key and the paid tier: the owner's.
- **Unread towns.** Bot checks we will not bypass; the unblock requests wait on the owner.
- **Petition articles as headlines** (Plymouth 24, Marshfield 9, Carver's 6:05 petition) and **Westford's Oct 26 warrant**, whose posted agenda is one line. Matcher and writer work.
- **Smaller asks**: an agenda link in the one-line view (the editor wants it, the style director's spec keeps it off the row); Lakeville's one hearing on two rows; OCR fragments in Search snippets; substations as a topic; Kingston's partial coverage named under the county.
