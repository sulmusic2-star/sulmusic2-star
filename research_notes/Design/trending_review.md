# Trending: review of the ranked list and its headlines

Review date: 2026-10-12. Input: `projects/351watch/data/hits_current.json` generated 2026-10-12 13:11 UTC (1,169 hits; 164 with a meeting today or later), the agenda text in `data/search/`, `tracker.json` and `ag_decisions.json`. Output: `data/trending.json` from `python3 trending.py` (116 live stories, top 100 kept). Contract and weights: `projects/351watch/ARCHITECTURE.md`, "data/trending.json".

Method: I ran the ranker, read every headline, dek, quote and reason in the top 40 against the agenda text it came from, fixed the code where a line was wrong or vague, and ran it again. That took about fifteen passes. The headline, dek and reason lines were then checked with `.claude/skills/de-slop/scripts/slop_lint.py`: score 0 on 3,904 words ("clean"). `tools/test_trending.py` repeats that check on every template with sample data.

**Main finding.** The ranking holds up. The top 6 are all data-center moratoria or bans, and all 8 upcoming ones are in the top 13. Of the top 16, 12 are data-center or battery-storage rules (moratoria, bans, bylaws) and the other 4 are battery-storage or data-center projects. Routine solar items sit low: Carver's continuance is #73, and packet minutes are #76 and below. Getting there needed more than weights. Many agenda PDFs carry minutes of an earlier meeting, and several notices list a project that has already asked to be continued. Read naively, both produce false headlines. Two cases from the brief show this:

- "Carver planners hear Federal Pond Solar permit request" would be wrong. The Oct 13 agenda says of Federal Pond Solar "Applicant has requested a continuance to October 27, 2026", and the same of Parallel Products Solar Energy. The page now says "Federal Pond Solar asks Carver planners for continuance to Oct 27" and ranks it #73.
- The Pittsfield City Council packet for Oct 13 mentions the data-center moratorium and the BESS ordinance, but only in the minutes of Sept 22 printed after the agenda. Those hits are classed as minutes. The Pittsfield story is led by the Community Development Board's Oct 20 hearing, and the council packet counts only as a second board.

## The top 20 as they would appear

### 1. Plymouth Town Meeting takes up a one-year data-center moratorium

Plymouth's Town Meeting is Saturday, Oct 17. The warrant lists an article proposing a temporary moratorium on data centers.

> …"Data Center", and by creating a new section, §207-12, Temporary Moratorium on Data Centers, which would enact a one-year temporary moratorium from October 17, 2026, until October 16, 2027 on the…

Reasons: Moratorium vote; Data-center item; 3 boards; Town Meeting on Saturday; First seen Oct 10. Score 31.05.

### 2. Boxborough weighs a data-center moratorium

The Planning Board meets Tuesday, Oct 13. The agenda lists a proposed moratorium on data centers.

> Review of Warrant The Board will review legal council's feedback on the proposed moratorium on Data Centers as a use type in Boxborough, a vote whether to amend the article per legal feedback.

Reasons: Moratorium proposal; Data-center item; 2 meetings; Meeting tomorrow; First seen Oct 10. Score 27.00.

### 3. Burrillville Town Council takes up petition to prohibit data centers

The Town Council meets Wednesday, Oct 14. The agenda lists a petition to prohibit data centers.

> 26-320 Consider and act on a petition from Roberta Lacey for an amendment to the Burrillville General Ordinances, Chapter 30 Zoning to prohibit data centers

Reasons: Proposed ban; First data-center item in Burrillville; Vote on Wednesday; First seen Oct 10. Score 27.00.

### 4. Pittsfield Community Development Board holds hearing on a data-center moratorium

The Community Development Board meets Tuesday, Oct 20. The agenda lists a public hearing on a temporary moratorium on data centers.

> Article 23-4 Section 4.332 "Data Centers, Temporary Moratorium" to amend the Zoning Ordinance to impose a temporary moratorium on Data Centers in Pittsfield.

Reasons: Moratorium hearing; Data-center item; 2 boards; Hearing Oct 20; First seen Oct 10. Score 24.60.

### 5. South Hadley planners hold hearing on prohibiting data centers

The Planning Board meets Monday, Oct 26. The agenda lists a public hearing on a proposal to prohibit data centers.

> …to consider amendments to the Zoning Bylaw to prohibit the construction of data centers by amending Section 255-10 Terms defined and inserting a definition for "data center," and by amending…

Reasons: Hearing on a proposed ban; Data-center item; 2 boards; Hearing Oct 26; First seen Oct 10. Score 24.60.

### 6. Northfield planners hold hearing on a data-center moratorium

The Planning Board meets Tuesday, Oct 20. The agenda lists a public hearing on a draft moratorium on data centers.

> Discuss draft proposed moratorium for data storage centers

Reasons: Moratorium hearing; Data-center item; 2 meetings; Hearing Oct 20; First seen Oct 10. Score 22.80.

### 7. Harvard Town Meeting takes up solar and battery storage rules

Harvard's Town Meeting is Tuesday, Oct 20. The warrant lists an article on solar and battery storage rules.

> …incorporating standards for Solar Photovoltaic Installations, Battery Energy Storage Systems, and Consolidated Local Permitting consistent with 225 CMR 29.00 and Chapter 239 of the Acts of 2024

Reasons: Town Meeting vote; Battery storage item; 3 boards; Town Meeting Oct 20; First seen Oct 10; On our tracker: battery storage and solar zoning bylaw, proposed. Score 21.84.

### 8. Geneva Town Board considers adopting a battery storage law

The Town Board meets Tuesday, Oct 13. The agenda lists a resolution adopting a battery storage law.

> Adopting Local Law No. 5 of 2026, Battery Energy Storage Systems.

Reasons: Adoption vote; Battery storage item; 2 meetings; Vote tomorrow; First seen Oct 10. Score 21.00.

### 9. Rochester planners hear High Street Solar permit request

The Planning Board meets Tuesday, Oct 13. The agenda lists a special permit and site plan review for High Street Solar.

> (continued from September 8, 2026) A Site Plan Review and Special Permit application filed by High Street Solar 1, LLC & High Street Solar 2, LLC, 55 Technology Drive, Suite 102, Lowell, MA 01851…

Reasons: Continued hearing on a specific project; Battery storage item; 2 boards; Hearing tomorrow; First seen Oct 10. Score 20.85.

### 10. Leyden planners discuss a possible data-center moratorium

The Planning Board meets Wednesday, Oct 14. The agenda lists a possible moratorium on data centers.

> AI data center moratorium?

Reasons: Possible moratorium; First data-center item in Leyden; Meeting on Wednesday; First seen Oct 10. Score 20.25.

### 11. Westfield City Council holds hearing on battery storage rules

The City Council meets Thursday, Oct 15. The agenda lists a public hearing on battery storage rules. It was on the Planning Board agenda Oct 6.

> …to consider a petition of the City Council to adopt zoning regulations for clean energy systems, including BESS.

Reasons: Bylaw hearing; Battery storage item; 2 boards; Hearing on Thursday; First seen Oct 10. Score 19.84.

### 12. Swansea Conservation Commission hears Old Warren Rd Development wetlands filing

The Conservation Commission meets Tuesday, Oct 13. The agenda lists a Notice of Intent for Old Warren Rd Development.

> SE72-1889-AMEND-Notice of Intent by Pedro Rodri uez/Old Warren Rd Development LLC for proper located at 0 Old Warren Rd, Swansea, MA; (Map:3 Lot:22) for proposed ground-mounted photovoltaic solar &…

Reasons: Hearing on a specific project; Battery storage item; 4.9 MW; 2 meetings; Hearing tomorrow; First seen Oct 10. Score 19.26.

### 13. Northampton planners hold hearing on a 365-day data-center moratorium

The Planning Board meets Thursday, Oct 29. The agenda lists a public hearing on a temporary moratorium on data centers.

> Proposed zoning ordinance amendments to establish definition of data centers and to impose a 365 day temporary moratorium on establishment of a data center by amending 350-2.0 and 350- 5.2. ### For…

Reasons: Moratorium hearing; Data-center item; 2 boards; Hearing Oct 29; First seen Oct 10. Score 18.45.

### 14. Somerset zoning board hears Somerset Energy Storage petition

The Zoning Board of Appeals meets Thursday, Oct 15. The agenda lists a planned development permit for Somerset Energy Storage.

> Somerset Energy Storage, LLC for 1606 Riverside Ave., Somerset, MA: petition of Somerset Energy Storage, LLC

Reasons: Hearing on a specific project; Battery storage item; 3 meetings; Hearing on Thursday; First seen Oct 10. Score 18.09.

### 15. Westfield planners take up Servistar Realties data-center permit extension

The Planning Board meets Tuesday, Oct 13. The agenda lists a permit extension for Servistar Realties.

> Request by Servistar Realties LLC for permit extension allowing a data center off Ampad Rd. & Servistar Industrial Way (originally granted 10/19/21)

Reasons: Project application; Data-center item; 2 meetings; Meeting tomorrow; First seen Oct 10. Score 18.00.

### 16. Falmouth Town Meeting takes up data-center rules

Falmouth's Town Meeting is Monday, Oct 26. The warrant lists an article on data-center rules.

> By inserting new definition for Data Center to section 240-3.2 to read as follows:

Reasons: Town Meeting vote; Data-center item; Town Meeting Oct 26; First seen Oct 10. Score 18.00.

### 17. Lakeville planners hold hearing on a battery storage bylaw

The Planning Board meets Thursday, Oct 22. The agenda lists a public hearing on a battery storage bylaw.

> Zoning By-Law and would add a new section _§270-12, Battery Energy _ Storage Systems-BESS.

Reasons: Bylaw hearing; Battery storage item; 2 boards; Hearing Oct 22; First seen Oct 10. Score 17.64.

### 18. Upton planners hear permit request for ground-mounted solar array at 169 South St

The Planning Board meets Tuesday, Oct 13. The agenda lists a public hearing on a special permit for a ground-mounted solar array.

> Special Permit for a proposed Large-Scale Ground-Mounted Solar Photovoltaic Installation

Reasons: Hearing on a specific project; Large solar project; 2 boards; Hearing tomorrow; First seen Oct 10. Score 16.95.

### 19. Sudbury planners discuss battery storage rules

The Planning Board meets Wednesday, Oct 14. The agenda lists an item on battery storage rules.

> Battery Energy Storage System Bylaw

Reasons: Draft bylaw; Battery storage item; 3 meetings; Meeting on Wednesday; First seen Oct 10; On our tracker: battery storage zoning bylaw, proposed. Score 16.20.

### 20. Middlefield Conservation Commission discusses solar and battery storage rules

The Conservation Commission meets Wednesday, Oct 14. The agenda lists an item on solar and battery storage rules.

> …the Transfer Station Discussion of Solar and Battery Storage ByLaw Response to Mr. Lewis of 0 Town Hill Road New/Old Business

Reasons: Draft bylaw; Battery storage item; 2 boards; Meeting on Wednesday; First seen Oct 10. Score 15.53.

## The top 40, read as a skeptical local reader

Four questions per story: is the headline true to the agenda, plain and specific, free of hype and stock phrases, and placed sensibly? Every headline passes the third question; there are no adjectives of importance anywhere in the templates. The table records what each line rests on and anything a careful reader could object to.

| # | Headline (short) | What the agenda says | Verdict |
|---|---|---|---|
| 1 | Plymouth TM, one-year data-center moratorium | Article 16 creates §207-12, a one-year temporary moratorium from Oct 17, 2026 to Oct 16, 2027. The warrant on file has no meeting date in our record; "Saturday, October 17, 2026" is read from the warrant's first page (`meeting_date_source: warrant`). | True. "Takes up", not "adopts". |
| 2 | Boxborough weighs a data-center moratorium | Planning Board reviews counsel's feedback on the moratorium article and votes on whether to amend it. | True. The vote is on amending the article, so the headline does not say "votes on the moratorium". |
| 3 | Burrillville petition to prohibit data centers | "Consider and act on a petition ... to prohibit data centers". | True. "First data-center item" holds for our RI records (since summer). |
| 4 | Pittsfield CDB hearing on moratorium | Notice of public hearing on Article 23-4 §4.332 "Data Centers, Temporary Moratorium". | True. The council packet (Sept 22 minutes) counts as a second board but is not described as an Oct 13 agenda item. |
| 5 | South Hadley hearing on prohibiting data centers | Hybrid public hearing on amendments "to prohibit the construction of data centers". | True. Uses the agenda's verb, "prohibit", not "ban". |
| 6 | Northfield hearing on a data-center moratorium | Under "Public Hearing:" the agenda says "Discuss draft proposed moratorium for data storage centers". | True. The agenda says "data storage centers"; the quote shows those words. |
| 7 | Harvard TM, solar and battery storage rules | STM article replaces the solar overlay with a "Clean Energy Facilities" bylaw that includes BESS standards. | True. |
| 8 | Geneva (NY) considers adopting a battery storage law | Resolution No. 68-2026 adopting Local Law No. 5 of 2026, BESS. | True. "Considers adopting", no outcome. |
| 9 | Rochester hears High Street Solar | Continued hearing (from Sept 8) on High Street Solar 1 and 2, LLC; the proposal includes a BESS. | True. The other Rochester project (Walnut Plain Road) asked to continue and does not lead. |
| 10 | Leyden, possible data-center moratorium | Topic list line "6. AI data center moratorium?" | True. "Possible" mirrors the question mark; ranked below formal hearings. |
| 11 | Westfield council hearing on battery storage rules | Petition "to adopt zoning regulations for clean energy systems, including BESS". | True but narrow: the petition covers clean energy systems in general. The quote shows the full wording. |
| 12 | Swansea, Old Warren Rd Development wetlands filing | Amended Notice of Intent for ground-mounted solar and BESS at 0 Old Warren Rd. | True. The 4.9 MW reason comes from the linked MassDEP filing for phase 2 at the same address, so it appears only as a reason, not in the headline. |
| 13 | Northampton, 365-day data-center moratorium | Joint hearing notice: "impose a 365 day temporary moratorium". | True. Ranked below #12 only because it is 17 days out. |
| 14 | Somerset hears Somerset Energy Storage petition | Petition for a planned development to allow a commercial BESS at 1606 Riverside Ave. | True. |
| 15 | Westfield, Servistar Realties permit extension | "Request by Servistar Realties LLC for permit extension allowing a data center" (granted 10/19/21). | True. |
| 16 | Falmouth TM, data-center rules | Article inserts a data center definition into §240-3.2. | True but broad: "rules" covers a definition. |
| 17 | Lakeville hearing on a battery storage bylaw | Hearing on new §270-12, Battery Energy Storage Systems. | True. |
| 18 | Upton hears ground-mounted solar at 169 South St | Hearing on a special permit for a large-scale ground-mounted array at 169 South St/0 Sawmill Brook Lane; the Conservation Commission has the same site Oct 14. | True. |
| 19 | Sudbury discusses battery storage rules | Untimed item "Battery Energy Storage System Bylaw". | True; "discuss" is the safest verb for an untimed item. |
| 20 | Middlefield ConCom discusses solar and battery rules | "Discussion of Solar and Battery Storage ByLaw". | True. |
| 21 | Clay (NY) ZBA, variance for BESS | Area variances (setbacks) for BESS equipment at 4664 Wetzel Road, meeting Oct 12. | True. Says "reviews": no hearing word sits next to the item. |
| 22 | Westford, Town Meeting article on clean energy siting | Select Board reviews STM articles incl. new §6.6 Small Clean Energy Infrastructure Facilities. | True. |
| 23 | Egremont, draft battery storage bylaw | "Battery Energy Storage System Draft Bylaw". | True. |
| 24 | Ashland, 116-unit 40B rental plan | 116 rental units (87 market, 29 restricted) at 55 West Union Street. | True after a fix: the first run said "87-unit" (see below). |
| 25 | Weston, rezoning at 300 Wellesley St | Petition to rezone 28.251 acres to allow 215 age-restricted units. | True. |
| 26 | Saugus, 300-unit 40B rental plan | 20 Bennett LLC, "three hundred (300) rental apartment units". | True. |
| 27 | Mashpee, 65-unit 40B rental plan | On Commons LLC, "sixty-five (65) rental units", continued eight times. | True. |
| 28 | Amherst ConCom, solar wetlands filing | Amended NOI by PureSky Energy for a transformer containment change at an approved solar facility. | True, but it is a minor change; #28 is generous. |
| 29-31 | Lenox, Pepperell, South Kingstown zoning hearings | Public hearings on zoning amendments. | True, generic. These fill the list because few towns post this far ahead. |
| 32 | Falmouth, solar carport | Special permit hearing for a solar carport at 709 and 737 Gifford Street. | True. |
| 33 | Shirley ConCom, Parker Village 40B | Peer review and stormwater update on the Parker Village comprehensive permit. | True. |
| 34-40 | Holliston, Middleton, Newport, Lunenburg zoning hearings; Plymouth, Milton, Norton TM zoning articles | Hearings and warrant articles amending zoning bylaws. | True, generic. |

What a reader could still object to: #11 and #16 use a slightly narrower or broader noun than the agenda, the quotes keep OCR damage verbatim ("Pedro Rodri uez", "legal council's"), and the lower half of the list is dominated by generic zoning hearings.

## What reading the list changed

| Problem found | Fix |
|---|---|
| Minutes of an earlier meeting, printed in the same PDF as the agenda (Pittsfield, Seekonk, Wellesley), were read as agenda items. | Minutes test on the text around the match: motion and vote language, two narrative verbs ("said", "inquired"), minutes line numbers, or narrative after the packet's first "made a motion". Such hits become `minutes` (× 0.35) with the headline "... packet mentions ...". |
| Projects that had requested a continuance read as hearings (both Carver hearings; Rochester's Walnut Plain Road). | Continuance test over the whole numbered item, including the "(requested to continue until ...)" note before it. A continuance to a date before the meeting is treated as minutes. |
| One agenda item's words leaked into its neighbor on run-on agendas (Middlefield, Egremont, Upton, Falmouth). | Item boundaries from numbering, bullets (including PDF symbol-font and minus-sign bullets), times, section headers and " … " joins; for run-on text, a hearing word only counts when no other item ("Discussion of", "Request for") sits between it and the match. Names and addresses are taken from the same item, preferring the one just before the match. |
| "Lot 17." was read as item 17, which cut the High Street Solar item in half. | Numbers after "Lot", "Map", "&", "and" and similar are not item numbers. |
| Bylaw citations ("under Section 6.10 of the Zoning By-laws") made project petitions look like bylaw changes (Somerset); 40B bylaw waivers did the same (Saugus). | Citations are masked before choosing bylaw versus project; a comprehensive permit application with waivers is always a project. |
| "AI data center moratorium?" outranked formal hearings. | A tentative moratorium (question mark, "possible") gets × 1.2 instead of × 1.6, and the headline says "possible". |
| A PFAS moratorium, a road-opening moratorium and a crypto-kiosk moratorium were tagged `moratorium`. | A moratorium counts only when a siting subject is named next to it; others fall to "other" (1 point). |
| A utility's pole petition "to provide power for solar battery project" read as a project application (Leominster). | Utility pole, conduit and grant-of-location items are mentions. |
| "Solar District" (an overlay district name) made a retail project a solar story (Lancaster). | A solar word that only names an overlay district is a mention. |
| The units extractor skipped "a total of 116 rental units" and reported 87 for Ashland. | Only "of which" and "% of" shares are skipped; the largest stated count wins. Covered by a unit test. |
| Momentum and tracker bonuses lifted packet minutes above real hearings (Pittsfield council packet at #41). | Bonuses scale down with the action multiplier when it is below 0.8; that story is now #76. |
| Conservation Commission wetlands reviews outranked planning and zoning hearings on the same kind of project. | Conservation Commission project items × 0.85. |
| Spec example "Carver planners hear Federal Pond Solar permit request". | Not used: the agenda shows a continuance request. |

## Limits

- Coverage is short. The crawl began Oct 10, 2026, so every story is "First seen Oct 10" and gets the same novelty point, and "first in this town" means first in our records. It is claimed only when we hold at least 30 days of that town's agendas before the story and no undated hit on the topic exists.
- Only 164 hits have a meeting today or later, so the bottom half of the 100 is generic zoning items and mentions. That will improve as more towns post ahead.
- Classification is rules over agenda text, not understanding. Run-on agendas without punctuation are the weak spot. When the rules cannot tell, the templates fall back to "agenda mentions", which is true but vague.
- Quotes are verbatim agenda text with only OCR noise tokens removed, so typos and OCR damage stay ("legal council's", "Rodri uez").
- `days_until` and "Meeting tomorrow" are relative to the build time. The page should recompute from `meeting_date`.
- Town Meeting dates read from warrant text (`meeting_date_source: warrant`) depend on the warrant naming the meeting date on its first pages; when it does not, the story says "gives no date" and gets the undated timing factor (0.75).
- Names come from "LLC", "Inc.", "Trust" and similar suffixes or "X Solar" patterns. Applicants without a suffix (PureSky Energy) are not named, and owner or law-firm LLCs are filtered by position and keywords, which can miss.
