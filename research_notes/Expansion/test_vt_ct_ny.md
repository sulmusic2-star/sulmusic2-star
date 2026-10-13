# Agenda Ahead Wave 1: Vermont, Connecticut and 50 more New York places

- **Run dates:** 2026-10-12 and 2026-10-13 (UTC). Branch `worktree-agent-a0ef056dcd46a1079`, from 8928cc1.
- **What was added:**
  - a Vermont Act 250 state feed;
  - a Connecticut Siting Council state feed;
  - 50 more New York towns, cities and villages, chosen for battery-storage (BESS) moratoria, BESS laws and data-center fights.
- **Status:** all three stay gated and off in production (`experiments/gate_check.py`: GATE OK).

**Question.** Are these three sources good enough, to the bar used for Michigan and Virginia, to switch on?

**Short answer.** On the agreed bar, the Vermont and Connecticut feeds pass. New York passes four of the five criteria. It misses the fifth, crawl errors, because 4 of its 50 places could not be reached from this sandbox. Two results sit exactly on their bar:

- Vermont accuracy is exactly 90.0%.
- New York readability is exactly 50%.

Read them as borderline passes, not comfortable ones.

## Pass/fail

| Criterion | Result | Verdict |
|---|---|---|
| Accuracy ≥90% on a fresh random sample of ≥60 items per source, hand-checked (the MI/VA bar), with the 95% range (Wilson) | **Vermont:** **54/60 = 90.0%** (79.9–95.3%).<br>Siting flag right 56/60 = 93.3%; record fields right 58/60 = 96.7%.<br>**Connecticut**, round 2 (fresh, after the docket-date fix): **57/60 = 95.0%** (86.3–98.3%); every tag right 56/60. Round 1 was 55/60 = 91.7% (81.9–96.4%).<br>**New York:** **55/60 = 91.7%** (81.9–96.4%); every tag right 55/60. | **PASS** in all three on the point estimate. Vermont is exactly at 90%. No interval excludes values under 90%. |
| Crawl errors <5% | **Feeds:** 0 errors in every Vermont and Connecticut run: 2 feed runs each, 2 Connecticut backfills over 279 matters, and 80 Vermont detail pages for the fresh pool.<br>**New York crawl:** 0 of 25 crawled places failed in 2 runs. Documents: 1 of 114 failed in the window (0.9%, a Word .doc) and 10 of 432 in the extended crawl (2.3%: 9 .doc, 1 .pptx).<br>**New York places:** 4 of 50 were unreachable (8.0%, 3.2–18.8%): Schroeppel, Northampton, Virgil and Greenwood. Every request to them was reset at this sandbox's egress relay (logged in the proxy's relay-failure list). Rose was unreachable on day 1 and reachable on day 2. | **PASS** for both feeds and the New York crawl<br>**FAIL** as measured for New York places (8%). This looks environmental, but that is unproven. |
| ≥50% of New York target towns readable | **25/50 = 50.0%** (36.6–63.4%) have agendas or notices read in the crawl window.<br>23/50 = 46% have a *dated* meeting document; Lewis and Westfield post month-named agendas only. | **PASS** at exactly the bar |
| Output validates against the contract | `current.validate` on `data/test/wave1/hits_wave1.json` (65 hits: CT 33, NY 28, VT 4): 0 errors | **PASS** |
| Existing MA/NY/RI hit counts unchanged | `keywords.py` is byte-identical to 8928cc1. `experiments/keyword_regression.py` on all 3,105 cached MA, NY and RI documents, old (8928cc1) against new: MA 1,063, NY 28, RI 109 hits in both, and **0 documents differ** (`data/test/wave1/keyword_regression.json`).<br>`gate_check.py`: the default daily selection is still MA 240 / NY 33 / RI 39, and a production `hits_current` build still lists only MA, NY and RI. | **PASS** |
| Off in production | VT and CT towns files are gated. Feeds refuse `data/` and `data/sources/`. The New York wave-1 config sits outside the `data/towns_*.json` glob and is gated. Daily refuses gated runs without `--output-dir`. | **PASS** (GATE OK) |

**How accuracy was judged.** Each source had its own item definition, with the same strictness as MI/VA.

- **Vermont and Connecticut:** an item is right when all of these match the source's own pages:
  - its host town;
  - its applicant: organizations named, private persons shown as `[individual]`;
  - its type or facility;
  - its status;
  - its hearing or decision date;
  - its link.

  Its siting flag and topics must also be right.
- **New York:** the MI/VA hit definition. A hit is right when it points to a real agenda item, ordinance text, or staff or public record about its topic in the land-use or siting sense.

Every sample was drawn with a fixed seed before any change it could judge. All judgments, with one-line reasons, are in `data/test/wave1/judgments.json`.

## Vermont: Act 250 feed

**What it reads.**

- The Act 250 "Agenda" list, `anrweb.vt.gov/ANR/Act250/agenda.aspx`: the last three weeks of notices, about 40 projects a day.
- Each project's detail page (`Details.aspx?Num=`).

**Access rules.**

- `anrweb.vt.gov/robots.txt` answers 404, which means everything is allowed (RFC 9309).
- GET only, at 1 request per second.
- A run refreshes up to 30 earlier pending items so it can pick up their decisions.

**What each item holds.**

- Town, with "Essex, Town of", "Rutland City" and "Barre Town" resolved against `data/towns_vt.json`. That file lists 256 towns and cities, with city/town pairs kept apart.
- Project description, applicant, application type, status and link.
- A date chosen in this order: hearing, then decision, then comment or petition deadline, then agenda.

Items are filed under the named town.

**What gets flagged.** New work of these kinds:

- solar, but not rooftop;
- battery storage;
- data centers;
- generation or transmission;
- communications towers;
- extraction: quarries, gravel and sand pits, crushing;
- large commercial or industrial development: commercial or industrial type with ≥20,000 sq ft new floor area, ≥10 acres developed, ≥50 rooms or ≥100 parking spaces, a new shopping center, or an industrial subdivision of ≥10 acres.

What is not flagged:

- administrative amendments and jurisdictional opinions that only extend dates, transfer permits or edit conditions;
- "insignificant changes";
- records created in error or inactivated.

Withdrawn items stay flagged, because a withdrawal is news.

**Today's feed.** 40 projects, 4 flagged:

- **Fayston:** a temporary 50 ft AT&T monopole on the Mt. Ellen summit at Sugarbush. Comment deadline Oct 28.
- **Berlin:** a five-story, 100-room hotel in front of the Comfort Inn. Comment deadline Oct 20.
- **Milton:** a jurisdictional opinion on expanding an earth-extraction operation. Withdrawn Oct 9.
- **Weathersfield:** renewal of the town's Bow Sand Pit. Withdrawn Oct 6.

**PUC §248 docket listing: not added.** Its ePUC searches are POST forms, and the PUC calendar is disallowed by robots.txt. It is not public, machine-readable and robots-allowed, so it does not meet the brief's condition.

**Test.**

- **Census of today's feed, in sample.** The feed holds only about 40 items, and all 40 were read while the flag rules were written. As a census, all 40 match their detail pages and all 4 flags are right. This is not an out-of-sample measure.
- **Fresh sample.** 60 projects the module never saw were drawn at random (seed 2028). The pool was base project numbers just below the newest application of six district series: 1R, 4C, 5W, 7E, 9A and 2W, 80 numbers each, 20 of which had no project. Each detail page was read by the same item builder, with the code frozen. Result: **54/60**.
  - Pool shape: mostly decided original applications from 1975 to 2026. 54 are permits; 2 are denials, and 1 each is dismissed, inactivated, findings and withdrawn.
  - So it tests the classifier and the parser more than the live feed's mix of pending applications.
  - Only 6 of the 60 were flagged, so flagged-item precision rests on few cases: 4 of 6 right in the fresh pool, 4 of 4 in the census.

**The 6 errors:**

| Project | Error |
|---|---|
| 5W1011 Warren | Missed tower: "10' high tansmitter tower w/5' antenna" (the typo is in the source, and there is no telecom word) |
| 9A0332 New Haven | Missed large development: a 66-acre, 6-lot commercial/industrial subdivision |
| 4C1286 Colchester | False positive: "reclamation of a borrow pit" closes a pit; it is not extraction |
| 2W0355 Londonderry | False positive: a 12,500 sq ft addition to a shopping center, under the module's own 20,000 sq ft bar |
| 1R0989 Benson | Applicant "VTEL" (an acronym) shown as `[individual]` |
| 1R1036 Killington | Contact name kept: "Kara Tondorf Mountain Harmony, LLC". The source glues the person and the LLC into one cell. |

**Fixes, applied after judging (in sample).**

- Tower words: radio, broadcast or transmitter tower, and antenna.
- Pit reclamation without continued or expanded extraction is not flagged.
- An *addition* to a shopping center counts only by its size.
- Industrial subdivisions of ≥10 acres are flagged.
- Acronym applicants are kept as organizations.
- Personal revocable or living trusts become `[individual]`.
- One more given name ("kara") was added to the list used to spot contact names.

Re-run offline over all 100 judged items, the fixes correct all 6 errors. The only other change is that one census applicant becomes `[individual]`: "Katharine D. Stockman Revocable Trust", a personal trust. These fixes are in sample. The 90.0% was measured before them.

## Connecticut: Siting Council feed

**What it reads**, all GET, from `portal.ct.gov/csc`:

- the pending-matters page;
- the petition list (1500–1999) and docket list (500–999);
- each matter's page;
- the Council meeting agendas and their "Upcoming Calendar Events";
- each docket page's FINAL DECISION entry.

**Access rules.** `portal.ct.gov/robots.txt` allows `/csc` (it disallows only `/sitecore/*` and beta paths). The site's policies are a disclaimer and privacy policy, with no terms on automated access. No logins and no forms.

**What it produces.**

- New petitions, declaratory rulings, dockets, hearings and decisions are filed under the host town.
- A matter with several hosts gives one item per town.
- Topics: solar, battery storage, data centers, fuel cells and other generation, transmission and substations, telecom towers and small wireless facilities.
- Tower shares at existing towers and sub-petitions are not flagged.
- Enforcement matters are kept and labelled.

**Today's run.** 73 items, 66 flagged, 33 of them in the 120-day window.

**Test.** Two fresh samples were drawn from a backfill of decided petitions and dockets from 2022 on. The module was built on the 2026 window, so this is outside it.

- **Round 1** (seed 2028, pool 247): **55/60 = 91.7%**. Four docket decision dates had been taken from the Decision and Order's service-list date. Fix: use the docket page's FINAL DECISION entry; denials now say so.
- **Round 2** (seed 2029, pool 185, round-1 items excluded, drawn after that fix): **57/60 = 95.0%**, tags 56/60. The errors:
  - Docket 516R: a court-ordered remand still open; a procedural filing was read as the decision.
  - Docket 524: the listing strikes one applicant and inserts another, and the parser misses the inserted one.
  - Petition 1658: "Storrs (Mansfield)", where the town is in the parenthesis, so the item had no town.
  - Petition 1618 (tag only): telecom equipment on a transmission structure was also tagged `clean_energy_siting`.

**Round-2 fixes (in sample).**

- A "village (town)" form now resolves to the town in the parenthesis.
- Telecom gear on a transmission structure is tagged telecom only.

Re-run offline over the backfill, Petition 1658 resolves to Mansfield, 1618 and round 1's Docket 508 lose their wrong tags, and no other judged item changes. 516R and 524 are left for a later round.

**Recall gap.** A host town that is neither in a bold run nor written "…, Connecticut" can be missed. This was not measured.

## New York: 50 more places

**Selection.** 50 places, from the Carina BESS Moratorium Monitor, the NY pilot's next-50 list and the research notes:

- 40 with BESS moratoria, active or recently ended;
- 6 with BESS laws;
- 3 data-center fights;
- 1 BESS fight.

**How they are crawled.**

- Websites come from web search: 3 places have none, and Benson's first hit was Benson, NC.
- Each place went through `discover_sites` and then hand curation (`CURATED_NY` in `experiments/wave1_test.py`, each with a note).
- The crawl uses the existing adapters plus `cmm_compass`, a new adapter for the "CMM" embeds behind small Weebly sites.
- Config: `data/test/wave1/config/towns_ny.json` (gated).

**Outcome, 50 places:**

| Outcome | n | Places |
|---|---|---|
| Readable in the window | **25** | Albany, Angelica, Arietta, Campbell, Carlton, Clymer, Corning, Denmark, Dunkirk, Eden, Ellery, Glen Cove, Greig, Lewis, Maine, Massena, Mount Pleasant, Norfolk, North Tonawanda, Peekskill, Plattekill, Riverhead, West Bloomfield, Westfield, Yonkers |
| No agenda in the ±120-day window | 10 | Sherman (the Town posts minutes only; the agendas on shermanny.gov are the Village's), Oswegatchie (latest agenda is August), Palatine (Google Drive folder), Root, Prattsburgh (minutes only), North Harmony, Rose, Stockport, Montgomery (DNN library filled by script), Sherburne |
| No agenda listing found | 3 | Brasher, Mayville, Allen |
| Unreachable from this sandbox | 4 | Schroeppel, Northampton, Virgil, Greenwood |
| Blocked: robots.txt, a security block or a bot challenge (not bypassed) | 4 | Mentz (robots.txt), Collins (documents disallowed), Yorktown (calendar answers HTTP 403 "blocked due to security reasons"), Somerset (Cloudflare challenge) |
| No town website | 3 | Gainesville, Benson, Pike |
| Website error | 1 | Carlisle (county-hosted page 404) |

**Platforms of the 25:** agenda_page 10, generic_ny 6, cmm_compass 3, CivicClerk 3, CivicPlus 3, Legistar 1.

- Yonkers' own site is behind a Cloudflare challenge, which was not bypassed. Its City Council is on Legistar, whose API and pages are open.
- Of the 25, 19 are BESS-moratorium towns, 3 BESS-law towns and all 3 data-center fights.

**Readable, read honestly.**

- 25/50 = 50.0% exactly.
- Two of the 25 post agendas named only by month: Lewis ("Agenda for September 2026", a .docx) and Westfield ("September Agenda"). They are read with no meeting date.
- One, Carlton, posts only hearing notices.
- Counting only places with a dated meeting document, it is 23/50 = 46%.
- Reaching 25 took hand curation after discovery: Lewis and Carlton (new `follow_pages` option), Eden, Maine, the CMM towns, West Bloomfield, North Tonawanda and Yonkers.

**Precision.**

- **Pool.** An extended crawl read meetings from 2026-06-14 into `data/test/wave1/ny_extended/`: 445 documents listed, 422 new, 0 places failed. Its index held 85 hits, none read before.
- **Sample.** A seeded sample of 60 (seed 2028) covers 46 documents in 17 towns. Hits in the same document are not independent, so the interval somewhat understates the uncertainty.
- **Matcher.** The shared one in `keywords.py`, unchanged; NY runs without state patterns.
- **Result: 55/60 = 91.7%.**

The 5 false positives:

- 3 hits from Denmark's 2019 zoning-law PDF: its table of contents, a use table and a site-plan checklist. Discovery had taken one document page as the Town Board listing, so the sidebar link to the zoning law was read as a June 15, 2026 document.
- 1 supervisor's report: the town hall's own solar inverter was replaced.
- 1 bare "Letter from … – Temporary Moratorium" in Riverhead's published-letters list, with no subject.

**Board and date errors.** 5 of the 60 showed the wrong board or date: the 4 Denmark zoning-law hits, and Westfield's March agenda labelled "Planning Board". After the sample, Denmark and Westfield were re-curated (in sample): the zoning PDF is no longer listed, and Westfield reads as Town Board.

**What stays.** The inverter and bare-letter cases are matcher behaviour. `keywords.py` is shared with Massachusetts and was deliberately not changed.

## Notable finds (in the current window)

**Connecticut**

- **Docket 550**, Brookfield Husky Solar (Verogy): 50 MW in Sterling and Plainfield; Council meeting Oct 15.
- **Petition 1719**, a 45 MW trash-to-energy facility in Plainfield (SMART Technology Systems): withdrawn Oct 8.
- **Petition 1712**, a 3.4 MW battery at Allied Printing in Manchester: approved Oct 1. Manchester's own 0.3 MW BESS (Petition 1713) was approved Sept 3.
- Three 4.975 MW fuel cells by Dispatch Energy, all pending: Petitions 1721 (New London), 1722 (Suffield) and 1723 (Vernon).
- **Petition 1720**, Eversource lines and substations in Southington, New Britain and Berlin: pending.
- **Enforcement Petition 1056**: GRE 314 East Lyme, 5 MW solar; hearing Nov 5.
- **Docket 552**, a Crown Castle, Verizon and T-Mobile tower in Hamden: pending.

**Vermont**

- the Fayston temporary monopole (Sugarbush summit), comments due Oct 28;
- the Berlin 100-room hotel, comments due Oct 20.

**New York**

- **Albany:** BESS permitting amendment to the city's development ordinance; Common Council hearing Sept 24.
- **Angelica:** adoption of its BESS local law, Oct 12.
- **Campbell:** hearing on a 3-year extension of its BESS and solar-with-storage moratorium, Oct 13.
- **Dunkirk:** the Planning Board asks the Council for a BESS moratorium (Sept 15), after a 5 MW / 23.5 MWh BESS site plan in July.
- **Riverhead:** a 120 ft stealth monopole at Baiting Hollow Golf Club, Planning Board Oct 15, plus a stream of public letters on BESS.
- **Yonkers:** temporary moratorium on self-storage facilities adopted Sept 15.
- **West Bloomfield:** AG-district site-plan and special-use moratorium, and a new solar law, both heard Sept 9.
- **Norfolk:** Local Law 7 of 2026, Solar Development, Sept 10.
- **Westfield:** extension of its commercial-solar moratorium.
- **Denmark:** moratorium discussion with The Lundy Group, Sept 21.

In the extended window:

- **Massena:** a data center at the old Reynolds plant (Planning Board, June and August).
- **Greig:** a moratorium on nuclear power and large data centers.
- **North Tonawanda:** a 12-month extension of its crypto-mining and data-center moratorium.
- **Arietta:** a BESS moratorium.
- **Riverhead:** BESS site plans and special permits (Hampton Jitney, Pulaski Street, 221 Scott Avenue).

## Gaps and what promotion would need

- **Vermont:** the site needs labels for the two new topics, `extraction` and `large_development`, or the feed must map them onto existing topics.
  - PUC §248 (solar and storage certificates) is not covered.
  - The Act 250 feed shows only three weeks of notices, so a pending item's later hearing or decision is caught only by the 30-item refresh.
- **Connecticut:** open remands and struck-and-inserted applicants (Dockets 516R and 524). Towns named outside bold runs and "…, Connecticut" can be missed (recall not measured).
- **New York:**
  - 4 places are unreachable from this sandbox; check them from the production runner before counting them lost.
  - Word `.doc` and `.pptx` are not extracted (Plattekill's agendas are .doc).
  - Ten places have no agenda in the window; several post minutes only, or post agendas late (Oswegatchie).
- **Privacy:** the given-name list that spots contact names glued onto organizations will always be incomplete. Vermont applicant strings should be spot-checked before launch.

## Files

**Code**

- `projects/351watch/crawler/watch351/sources/`: `state_feeds.py`, `vt_act250.py`, `ct_siting.py`.
- `projects/351watch/crawler/watch351/adapters/cmm_compass.py` (new).
- Changes to `generic_ny.py` and `agenda_page.py`, all opt-in keys.
- `boards.py` and `discover_sites.py`: NY branches, used by discovery only.
- `current.py`: the two new topic keys.

**Experiments**

- `projects/351watch/crawler/experiments/wave1_test.py` (towns, targets, discover, crawl, feeds, combine, sample).
- `projects/351watch/crawler/experiments/gate_check.py`.

**Data and results**

- Town lists: `projects/351watch/data/towns_vt.json` and `towns_ct.json` (gated).
- Under `projects/351watch/data/test/wave1/`:
  - `config/towns_ny.json`, the 50 NY places (gated), and `targets_ny.json`, the selection with its sources;
  - `sources/`, today's VT and CT items, hits and ledgers; `sources_backfill/` and `sources_backfill_r2/`, the CT 2022+ backfills behind the fresh samples;
  - `ny/`, the window crawl: two runs, index, `hits_ny_wave1.json` and request logs; `ny_extended/`, the precision pool crawl;
  - `worksheet_vt.json`, `worksheet_ct.json`, `worksheet_ct_r2.json` and `worksheet_ny.json`, the samples; `judgments.json`, every judgment with its reason;
  - `hits_wave1.json` and `validation.json`, the combined contract-shaped output and its validation; `keyword_regression.json`.

**Re-run** (from `projects/351watch/crawler`):

```
python3 experiments/wave1_test.py feeds
python3 experiments/wave1_test.py crawl --label runN
python3 experiments/wave1_test.py combine
python3 experiments/gate_check.py
```
