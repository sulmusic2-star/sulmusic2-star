# Trending: review of the ranked list and its headlines

Review date: 2026-10-12. Input: `projects/351watch/data/hits_current.json` generated 2026-10-12 13:11 UTC (1,169 hits; 164 with a meeting today or later), the agenda text in `data/search/`, `tracker.json` and `ag_decisions.json`. Output: `data/trending.json` from `python3 trending.py` (top 100 stories kept). Contract and weights: `projects/351watch/ARCHITECTURE.md`, "data/trending.json".

Method: I ran the ranker, read every headline, dek, quote and reason in the top 40 against the agenda text it came from, fixed the code where a line was wrong or vague, and ran it again. That took about fifteen passes. A second pass removed system language from everything a reader sees: no "packet", "mentions", "hits", "tracker" or "first seen", no reasons that only repeat the topic, and dates instead of "tomorrow". The headline, dek and reason lines were then checked with `.claude/skills/de-slop/scripts/slop_lint.py`: score 0 on 3,274 words ("clean"). `tools/test_trending.py` repeats both checks on sample data.

**Main finding.** The ranking holds up. The top 6 are all data-center moratoria or bans; of the 8 with upcoming meetings, 7 are in the top 11 and the tentative Leyden line ("AI data center moratorium?") is #17. Of the top 16, 12 are data-center or battery-storage rules (moratoria, bans, bylaws) and the other 4 are battery-storage or data-center projects. Routine solar items sit low: Carver's continuance is #70. Getting there needed more than weights. Many agenda PDFs carry minutes of an earlier meeting, and several notices list a project that has already asked to be continued. Read naively, both produce false headlines. Two cases from the brief show this:

- "Carver planners hear Federal Pond Solar permit request" would be wrong. The Oct 13 agenda says of Federal Pond Solar "Applicant has requested a continuance to October 27, 2026", and the same of Parallel Products Solar Energy. The page now says "Federal Pond Solar asks Carver planners for continuance to Oct 27" and ranks it #70.
- The Pittsfield City Council packet for Oct 13 mentions the data-center moratorium and the BESS ordinance, but only in the minutes of Sept 22 printed after the agenda. Minutes never lead a story and are never shown. The Pittsfield story is led by the Community Development Board's Oct 20 hearing; that board also had it on Sep 15.

## The top 20 as they would appear

### 1. Plymouth Town Meeting takes up a one-year data-center moratorium

Plymouth's Town Meeting is Saturday, Oct 17. The warrant lists an article proposing a temporary moratorium on data centers.

> …"Data Center", and by creating a new section, §207-12, Temporary Moratorium on Data Centers, which would enact a one-year temporary moratorium from October 17, 2026, until October 16, 2027 on the…

Reasons: Moratorium vote; 2 town boards; Town Meeting Oct 17. Score 27.68.

### 2. Boxborough weighs a data-center moratorium

The Planning Board meets Tuesday, Oct 13. The agenda lists a proposed moratorium on data centers.

> Review of Warrant The Board will review legal council's feedback on the proposed moratorium on Data Centers as a use type in Boxborough, a vote whether to amend the article per legal feedback.

Reasons: Proposed moratorium; Also on the Sep 23 agenda; Meeting Oct 13. Score 27.00.

### 3. South Hadley planners hold hearing on prohibiting data centers

The Planning Board meets Monday, Oct 26. The agenda lists a public hearing on a proposal to prohibit data centers.

> …to consider amendments to the Zoning Bylaw to prohibit the construction of data centers by amending Section 255-10 Terms defined and inserting a definition for "data center," and by amending…

Reasons: Public hearing on a ban; 2 town boards; Hearing Oct 26. Score 24.60.

### 4. Burrillville Town Council takes up petition to prohibit data centers

The Town Council meets Wednesday, Oct 14. The agenda lists a petition to prohibit data centers.

> 26-320 Consider and act on a petition from Roberta Lacey for an amendment to the Burrillville General Ordinances, Chapter 30 Zoning to prohibit data centers

Reasons: Proposed ban; Vote Oct 14. Score 24.30.

### 5. Northfield planners hold hearing on a data-center moratorium

The Planning Board meets Tuesday, Oct 20. The agenda lists a public hearing on a draft moratorium on data centers.

> Discuss draft proposed moratorium for data storage centers

Reasons: Moratorium hearing; Also on the Oct 27 agenda; Hearing Oct 20. Score 22.80.

### 6. Pittsfield Community Development Board holds hearing on a data-center moratorium

The Community Development Board meets Tuesday, Oct 20. The agenda lists a public hearing on a temporary moratorium on data centers.

> Article 23-4 Section 4.332 "Data Centers, Temporary Moratorium" to amend the Zoning Ordinance to impose a temporary moratorium on Data Centers in Pittsfield.

Reasons: Moratorium hearing; Also on the Sep 15 agenda; Hearing Oct 20. Score 22.80.

### 7. Westfield City Council holds hearing on battery storage rules

The City Council meets Thursday, Oct 15. The agenda lists a public hearing on battery storage rules. It was on the Planning Board agenda Oct 6.

> …to consider a petition of the City Council to adopt zoning regulations for clean energy systems, including BESS.

Reasons: Public hearing; 2 city boards; Hearing Oct 15; Town has an earlier vote on this. Score 21.20.

### 8. Geneva Town Board considers adopting a battery storage law

The Town Board meets Tuesday, Oct 13. The agenda lists a resolution adopting a battery storage law.

> Adopting Local Law No. 5 of 2026, Battery Energy Storage Systems.

Reasons: Adoption vote; Also on the Sep 8 agenda; Vote Oct 13. Score 21.00.

### 9. Rochester planners hear High Street Solar permit request

The Planning Board meets Tuesday, Oct 13. The agenda lists a special permit and site plan review for High Street Solar.

> (continued from September 8, 2026) A Site Plan Review and Special Permit application filed by High Street Solar 1, LLC & High Street Solar 2, LLC, 55 Technology Drive, Suite 102, Lowell, MA 01851…

Reasons: Continued public hearing; 2 town boards; Hearing Oct 13. Score 20.85.

### 10. Harvard Town Meeting takes up solar and battery storage rules

Harvard's Town Meeting is Tuesday, Oct 20. The warrant lists an article on solar and battery storage rules.

> …incorporating standards for Solar Photovoltaic Installations, Battery Energy Storage Systems, and Consolidated Local Permitting consistent with 225 CMR 29.00 and Chapter 239 of the Acts of 2024

Reasons: Town Meeting vote; 3 town boards; Town Meeting Oct 20. Score 20.64.

### 11. Northampton planners hold hearing on a 365-day data-center moratorium

The Planning Board meets Thursday, Oct 29. The agenda lists a public hearing on a temporary moratorium on data centers.

> Proposed zoning ordinance amendments to establish definition of data centers and to impose a 365 day temporary moratorium on establishment of a data center by amending 350-2.0 and 350- 5.2. ### For…

Reasons: Moratorium hearing; 2 city boards; Hearing Oct 29. Score 18.45.

### 12. Somerset zoning board hears Somerset Energy Storage petition

The Zoning Board of Appeals meets Thursday, Oct 15. The agenda lists a planned development permit for Somerset Energy Storage.

> Somerset Energy Storage, LLC for 1606 Riverside Ave., Somerset, MA: petition of Somerset Energy Storage, LLC

Reasons: Public hearing; Also on the Oct 1 agenda; Hearing Oct 15. Score 18.09.

### 13. Westfield planners take up Servistar Realties data-center permit extension

The Planning Board meets Tuesday, Oct 13. The agenda lists a permit extension for Servistar Realties.

> Request by Servistar Realties LLC for permit extension allowing a data center off Ampad Rd. & Servistar Industrial Way (originally granted 10/19/21)

Reasons: Permit application; Also on the Sep 15 agenda; Meeting Oct 13. Score 18.00.

### 14. Falmouth Town Meeting takes up data-center rules

Falmouth's Town Meeting is Monday, Oct 26. The warrant lists an article on data-center rules.

> By inserting new definition for Data Center to section 240-3.2 to read as follows:

Reasons: Town Meeting vote; Town Meeting Oct 26. Score 18.00.

### 15. Swansea Conservation Commission hears Old Warren Rd Development wetlands filing

The Conservation Commission meets Tuesday, Oct 13. The agenda lists a Notice of Intent for Old Warren Rd Development.

> SE72-1889-AMEND-Notice of Intent by Pedro Rodri uez/Old Warren Rd Development LLC for proper located at 0 Old Warren Rd, Swansea, MA; (Map:3 Lot:22) for proposed ground-mounted photovoltaic solar &…

Reasons: Public hearing; 4.9 MW; State wetlands filing Sep 30; Hearing Oct 13. Score 17.76.

### 16. Lakeville planners hold hearing on a battery storage bylaw

The Planning Board meets Thursday, Oct 22. The agenda lists a public hearing on a battery storage bylaw.

> Zoning By-Law and would add a new section _§270-12, Battery Energy _ Storage Systems-BESS.

Reasons: Public hearing; 2 town boards; Hearing Oct 22. Score 17.64.

### 17. Leyden planners discuss a possible data-center moratorium

The Planning Board meets Wednesday, Oct 14. The agenda lists a possible moratorium on data centers.

> AI data center moratorium?

Reasons: Possible moratorium; Meeting Oct 14. Score 17.55.

### 18. Upton planners hear permit request for ground-mounted solar array at 169 South St

The Planning Board meets Tuesday, Oct 13. The agenda lists a public hearing on a special permit for a ground-mounted solar array.

> Special Permit for a proposed Large-Scale Ground-Mounted Solar Photovoltaic Installation

Reasons: Public hearing; 2 town boards; Hearing Oct 13. Score 16.95.

### 19. Middlefield Conservation Commission discusses solar and battery storage rules

The Conservation Commission meets Wednesday, Oct 14. The agenda lists an item on solar and battery storage rules.

> …the Transfer Station Discussion of Solar and Battery Storage ByLaw Response to Mr. Lewis of 0 Town Hill Road New/Old Business

Reasons: Draft rules; 2 town boards; Meeting Oct 14. Score 15.53.

### 20. Sudbury planners discuss battery storage rules

The Planning Board meets Wednesday, Oct 14. The agenda lists an item on battery storage rules.

> Battery Energy Storage System Bylaw

Reasons: Draft rules; Also on the Sep 23 agenda; Meeting Oct 14. Score 14.85.

## The top 40, read as a skeptical local reader

Four questions per story: is the headline true to the agenda, plain and specific, free of hype and stock phrases, and placed sensibly? Every headline passes the third question; there are no adjectives of importance anywhere in the templates. The table records what each line rests on and anything a careful reader could object to.

| # | Headline (short) | What the agenda says | Verdict |
|---|---|---|---|
| 1 | Plymouth TM, one-year data-center moratorium | Article 16 creates §207-12, a one-year temporary moratorium from Oct 17, 2026 to Oct 16, 2027. The warrant on file has no meeting date in our record; "Saturday, October 17, 2026" is read from the warrant's first page (`meeting_date_source: warrant`). | True. "Takes up", not "adopts". |
| 2 | Boxborough weighs a data-center moratorium | Planning Board reviews counsel's feedback on the moratorium article and votes on whether to amend it; the board had it Sep 23 too. | True. The vote is on amending the article, so the headline does not say "votes on the moratorium". |
| 3 | South Hadley hearing on prohibiting data centers | Hybrid public hearing on amendments "to prohibit the construction of data centers". | True. Uses the agenda's verb, "prohibit", not "ban". |
| 4 | Burrillville petition to prohibit data centers | "Consider and act on a petition ... to prohibit data centers". | True. |
| 5 | Northfield hearing on a data-center moratorium | Under "Public Hearing:" the agenda says "Discuss draft proposed moratorium for data storage centers"; the Oct 27 agenda lists a vote. | True. The agenda says "data storage centers"; the quote shows those words. |
| 6 | Pittsfield CDB hearing on moratorium | Notice of public hearing on Article 23-4 §4.332 "Data Centers, Temporary Moratorium"; the board had it Sep 15. | True. The council packet's Sept 22 minutes are not shown. |
| 7 | Westfield council hearing on battery storage rules | Petition "to adopt zoning regulations for clean energy systems, including BESS". "Town has an earlier vote on this": the city's BESS moratorium (tracker: expired). | True but narrow: the petition covers clean energy systems in general. The quote shows the full wording. |
| 8 | Geneva (NY) considers adopting a battery storage law | Resolution No. 68-2026 adopting Local Law No. 5 of 2026, BESS. | True. "Considers adopting", no outcome. |
| 9 | Rochester hears High Street Solar | Continued hearing (from Sept 8) on High Street Solar 1 and 2, LLC; the proposal includes a BESS. | True. The other Rochester project (Walnut Plain Road) asked to continue and does not lead. |
| 10 | Harvard TM, solar and battery storage rules | STM article replaces the solar overlay with a "Clean Energy Facilities" bylaw that includes BESS standards. | True. |
| 11 | Northampton, 365-day data-center moratorium | Joint hearing notice: "impose a 365 day temporary moratorium". | True. Ranked below the Oct 13-15 items because it is 17 days out. |
| 12 | Somerset hears Somerset Energy Storage petition | Petition for a planned development to allow a commercial BESS at 1606 Riverside Ave. | True. |
| 13 | Westfield, Servistar Realties permit extension | "Request by Servistar Realties LLC for permit extension allowing a data center" (granted 10/19/21). | True. |
| 14 | Falmouth TM, data-center rules | Article inserts a data center definition into §240-3.2. | True but broad: "rules" covers a definition. |
| 15 | Swansea, Old Warren Rd Development wetlands filing | Amended Notice of Intent for ground-mounted solar and BESS at 0 Old Warren Rd. | True. The 4.9 MW reason comes from the linked MassDEP filing for phase 2 at the same address (shown as "State wetlands filing Sep 30"), so it is not in the headline. |
| 16 | Lakeville hearing on a battery storage bylaw | Hearing on new §270-12, Battery Energy Storage Systems. | True. |
| 17 | Leyden, possible data-center moratorium | Topic list line "6. AI data center moratorium?" | True. "Possible" mirrors the question mark; ranked below formal hearings. |
| 18 | Upton hears ground-mounted solar at 169 South St | Hearing on a special permit for a large-scale ground-mounted array at 169 South St/0 Sawmill Brook Lane; the Conservation Commission has the same site Oct 14. | True. |
| 19 | Middlefield ConCom discusses solar and battery rules | "Discussion of Solar and Battery Storage ByLaw". | True. |
| 20 | Sudbury discusses battery storage rules | Untimed item "Battery Energy Storage System Bylaw". | True; "discuss" is the safest verb for an untimed item. |
| 21 | Clay (NY) ZBA, variance for BESS | Area variances (setbacks) for BESS equipment at 4664 Wetzel Road, meeting Oct 12. | True. Says "reviews": no hearing word sits next to the item. |
| 22 | Westford, Town Meeting article on clean energy siting | Select Board reviews STM articles incl. new §6.6 Small Clean Energy Infrastructure Facilities. | True. |
| 23 | Egremont, draft battery storage bylaw | "Battery Energy Storage System Draft Bylaw". | True. |
| 24 | Weston, rezoning at 300 Wellesley St | Petition to rezone 28.251 acres to allow 215 age-restricted units. | True. |
| 25 | Saugus, 300-unit 40B rental plan | 20 Bennett LLC, "three hundred (300) rental apartment units". | True. |
| 26 | Ashland, 116-unit 40B rental plan | 116 rental units (87 market, 29 restricted) at 55 West Union Street. | True after a fix: the first run said "87-unit" (see below). |
| 27 | Mashpee, 65-unit 40B rental plan | On Commons LLC, "sixty-five (65) rental units", continued eight times. | True. |
| 28-30 | Lenox, Pepperell, South Kingstown zoning hearings | Public hearings on zoning amendments. | True, generic. These fill the list because few towns post this far ahead. |
| 31 | Falmouth, solar carport | Special permit hearing for a solar carport at 709 and 737 Gifford Street. | True. |
| 32 | Shirley ConCom, Parker Village 40B | Peer review and stormwater update on the Parker Village comprehensive permit. | True. |
| 33 | Amherst ConCom, solar wetlands filing | Amended NOI by PureSky Energy for a transformer containment change at an approved solar facility. | True, but it is a minor change; #33 is generous. |
| 34-40 | Holliston, Middleton, Newport, Lunenburg zoning hearings; Plymouth, Milton, Norton TM zoning articles | Hearings and warrant articles amending zoning bylaws. | True, generic. |

What a reader could still object to: #7 and #14 use a slightly narrower or broader noun than the agenda, the quotes keep OCR damage verbatim ("Pedro Rodri uez", "legal council's"), and the lower half of the list is dominated by generic zoning hearings.

## What reading the list changed

| Problem found | Fix |
|---|---|
| Minutes of an earlier meeting, printed in the same PDF as the agenda (Pittsfield, Seekonk, Wellesley), were read as agenda items. | Minutes test on the text around the match: motion and vote language, two narrative verbs ("said", "inquired"), minutes line numbers, or narrative after the packet's first "made a motion". Such hits never lead a story, are never shown, and do not count as a board; they only group with other hits. |
| Projects that had requested a continuance read as hearings (both Carver hearings; Rochester's Walnut Plain Road). | Continuance test over the whole numbered item, including the "(requested to continue until ...)" note before it. A continuance to a date before the meeting is treated as minutes. |
| One agenda item's words leaked into its neighbor on run-on agendas (Middlefield, Egremont, Upton, Falmouth). | Item boundaries from numbering, bullets (including PDF symbol-font and minus-sign bullets), times, section headers and " … " joins; for run-on text, a hearing word only counts when no other item ("Discussion of", "Request for") sits between it and the match. Names and addresses are taken from the same item, preferring the one just before the match. |
| "Lot 17." was read as item 17, which cut the High Street Solar item in half. | Numbers after "Lot", "Map", "&", "and" and similar are not item numbers. |
| Bylaw citations ("under Section 6.10 of the Zoning By-laws") made project petitions look like bylaw changes (Somerset); 40B bylaw waivers did the same (Saugus). | Citations are masked before choosing bylaw versus project; a comprehensive permit application with waivers is always a project. |
| "AI data center moratorium?" outranked formal hearings. | A tentative moratorium (question mark, "possible") gets × 1.2 instead of × 1.6, and the headline says "possible". |
| A PFAS moratorium, a road-opening moratorium and a crypto-kiosk moratorium were tagged `moratorium`. | A moratorium counts only when a siting subject is named next to it; others fall to "other" (1 point). |
| A utility's pole petition "to provide power for solar battery project" read as a project application (Leominster). | Utility pole, conduit and grant-of-location items are listings, not applications. |
| "Solar District" (an overlay district name) made a retail project a solar story (Lancaster). | A solar word that only names an overlay district is a listing. |
| The units extractor skipped "a total of 116 rental units" and reported 87 for Ashland. | Only "of which" and "% of" shares are skipped; the largest stated count wins. Covered by a unit test. |
| Conservation Commission wetlands reviews outranked planning and zoning hearings on the same kind of project. | Conservation Commission project items × 0.85. |
| Reasons used system words ("First seen Oct 10", "On our tracker: ...", "Data-center item", "packet mentions") and relative days ("Hearing tomorrow"). | Reasons are now reader phrases with dates: "Moratorium vote", "Public hearing", "3 town boards", "Neighboring towns too", "Also on the Sep 23 agenda", "Hearing Oct 20", "Town has an earlier vote on this" (only when `tracker.json` records a vote by the town on the subject). Fallback headlines read "Battery storage item on Holyoke Planning Board agenda" and deks "The agenda lists an item on battery storage." |
| Spec example "Carver planners hear Federal Pond Solar permit request". | Not used: the agenda shows a continuance request. |

## Limits

- Coverage is short. The crawl began Oct 10, 2026, so every story is new this week and gets the same novelty point (kept out of the reasons; `is_new` carries it). "First time this has come up in [town]" needs 60 days of that town's agendas before the story and no earlier item on the topic; no town has that much history yet, so the Oct 12 file has no such reason.
- Only 164 hits have a meeting today or later, so the bottom half of the 100 is generic zoning items and bare listings ("Solar item on Salem Planning Board agenda"). That will improve as more towns post ahead.
- Classification is rules over agenda text, not understanding. Run-on agendas without punctuation are the weak spot. When the rules cannot tell, the templates fall back to the bare listing, which is true but vague.
- Quotes are verbatim agenda text with only OCR noise tokens removed, so typos and OCR damage stay ("legal council's", "Rodri uez").
- Reasons give dates; the page shows relative time from `meeting_date`. Deks name the weekday with the date ("meets Tuesday, Oct 13").
- Town Meeting dates read from warrant text (`meeting_date_source: warrant`) depend on the warrant naming the meeting date on its first pages; when it does not, the story says "gives no date" and gets the undated timing factor (0.75).
- Names come from "LLC", "Inc.", "Trust" and similar suffixes or "X Solar" patterns. Applicants without a suffix (PureSky Energy) are not named, and owner or law-firm LLCs are filtered by position and keywords, which can miss.
