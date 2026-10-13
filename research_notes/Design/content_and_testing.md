# Agenda Ahead: what to say about each item, and how to test it on people who skim

2026-10-12. Builds on `human_design_brief.md` (layout, wording of the site's own interface), `analog_patterns.md` (how other sites lay items out) and the value-test `fix_list.md` (accuracy bugs). This note covers the **words and facts inside each item**, and a **better tester protocol**. The protocol itself is in `scratchpad/value-test/tester_protocol_v2.md`.

**Bottom line.** The preview reads like a log of what the robot found ("The agenda lists a petition…", "mentions solar projects"). People want to know three things: what would change near them, when it gets decided, and how they can have a say. They want them in that order and in their own words. The agendas usually hold more of those facts than we show: Carver's agenda gives the street address, the 3-minute speaking limit and the fact that both solar hearings are being postponed. Plymouth's warrant says how to ask to speak.

---

## A1. What a person wants to know, in priority order

Sources: a Tewksbury resident's letter urging neighbors to act [A1], the Gazette's Hadley battery story [A2], Boston's hearing notices [A3], PlanningAlerts [A4], GovTrack [A5], Documenters [A6], and the real agendas in the appendix.

1. **What would change, in plain words, and the stage.** "A battery storage plant", "a one-year ban on new data centers". Then the stage: *vote*, *hearing* (you can speak), *discussion* (no vote expected), or *postponed*.
2. **Exactly where.** The street address and a landmark. Residents measure everything from home: "near homes, schools… just over half a mile away" [A1]; "a short distance from Zatyrka Park" [A2]. Drop map and lot numbers.
3. **When it's decided, and who decides.** Day, date, time, room. Who votes: the 5-member Planning Board, elected Town Meeting members (Plymouth), every registered voter (open Town Meeting), or the state. The Tewksbury letter leads with "not… decided by a town vote. The decision rests at the state level" [A1].
4. **How to have a say, with the rules and deadlines.** Speak in person (the time limit, the sign-up), write (to whom, by when), or join on Zoom. Agendas often say this: "comments will be kept to 3 minutes or less… sign the attendance sheet" (Carver). Plymouth's warrant asks non-members to tell the Town Clerk 48 hours ahead. Boston asks for written comments 48 hours ahead [A3].
5. **How big.** Megawatts, acres, number of battery containers, housing units, height. For a rule change: what it would allow or forbid, and for how long.
6. **Who is behind it.** The applicant as named (LLC), plus the developer if it's on the record. For a rule change: who proposed it and who recommends it (warrants print board recommendations).
7. **What happened before.** Continued from when, earlier denial, lawsuit, a related wetlands filing. The Gazette's second paragraph is the history: denied 4-0, then a lawsuit [A2].
8. **What happens next.** GovTrack's pattern: "It goes to the Senate next" [A5]. Ours: "If Town Meeting passes it, the Attorney General reviews it."
9. **The source.** Board, document, page, and the date we got it.

Facts 1 to 4 go in the first two lines. Facts 5 to 8 go in the brief. Fact 9 goes in the grey meta line.

## A2. Use the words people use

GOV.UK and Sarah Richards: write in the words your users search with and say aloud [A7][A8]. digital.gov: "use language your audience understands" [A9]. Residents' own words (from [A1], [A2], the testers) are on the right.

| Agenda says | Write |
|---|---|
| Large-Scale Ground-Mounted Solar Photovoltaic Installation | solar farm (add acres or MW) |
| dual-use photovoltaic / agrivoltaic | solar panels over farmland |
| Battery Energy Storage System, BESS, B.E.S.S. | battery storage plant (for a project); battery storage (for rules) |
| temporary moratorium on data centers | a temporary ban on new data centers (say how long) |
| Special Permit and Site Plan Review; petition for a Planned Development | permit to build; zoning approval |
| Notice of Intent (wetlands) | wetlands permit request |
| Public Hearing Cont'd | the hearing continues from [date] |
| Applicant has requested a continuance to Oct 27 | the company asked to postpone to Oct 27 |
| article, warrant | Article 16 on the Town Meeting agenda (the "warrant") |
| consider and act on; adopting Local Law No. 5 | vote on; final vote on |
| zoning bylaw/ordinance amendment | change to the town's zoning rules |
| 225 CMR 29.00, Chapter 239 of the Acts of 2024 | the 2024 state law that speeds up clean-energy permits |
| privilege of the floor; public participation | time when anyone can speak |
| abutter | next-door neighbor |

**Verbs that say the stage:** votes on, holds a hearing on, discusses (no vote listed), postponed to, final vote. **Avoid:** "takes up", "weighs" and "considers", which hide whether there's a vote. Also avoid "mentions" (a keyword hit), "the agenda lists" in the lead (attribution belongs in the meta line), "siting", "use type".

## A3. How to write the one-line summary and the three-line brief

**One line (at most 12 words or 80 characters).** [Thing in plain words] + [where] + [stage verb]. Put the date, board and town in the meta line above it, so the line doesn't repeat them. Lead with the most newsworthy point and stay under 20 words, in the present or future tense [A10][A11]. Then check it: if someone reads only this line, do they know whether to care?

**Three-line brief.**
- Line 1, *what and where*: what would change, where, how big, who's behind it.
- Line 2, *when and how to take part*: time, place, whether anyone can speak, any limit or deadline.
- Line 3, *before and next*: the history in one clause, then the next step.

Then a collapsed "From the agenda" quote with the whole sentence (fix list #4).

| Kind | One-line pattern | What the brief must add |
|---|---|---|
| **Moratorium** | Temporary ban on new [use]: [board] [votes/holds hearing] | How long (dates), what's paused (permits, construction), the stated reason, who proposed it, the vote needed, and what follows (AG review, expiry). |
| **Permit hearing** | [Project in plain words] at [address]: hearing | Size, applicant, whether anyone can speak and how, which session this is ("continues from Sep 8"), and the likely outcome tonight (vote or continue). Say what the board judges: a Conservation Commission rules only on wetlands. |
| **Bylaw or ordinance change** | New rules for [thing]: [board] hearing | One clause on what the rules would do. If the notice doesn't say, write "The notice doesn't say what the rules require" and link the full text. Then who votes after the hearing. |
| **Town Meeting article** | [Town] Town Meeting votes on [thing] (Article N) | Use the warrant's own "Summary:" when it has one. Add who recommends it, who can vote (open vs representative), two-thirds for zoning [A12], and AG review [A13]. |
| **Continuance** | Postponed: [project] hearing moves to [date] | "The company asked to postpone. If the board agrees, there will be no discussion tonight." Give the new date and place. Never write "will decide" (fix list #3). |
| **Discussion only** | [Board] discusses [thing] (no vote listed) | Why it's on now. Boxborough's "moratorium" item is a 15-minute review of the lawyer's edits before the Nov 16 Town Meeting. |

**When the agenda doesn't state a fact**, in this order:
1. **Fill it from our own sourced records.** That means an earlier agenda for the same project, the MassDEP wetlands filing (Swansea's 4.9 MW came from there), a warrant summary, or a state siting docket. Tag the source in the line: "(from its Sep 30 state wetlands filing)".
2. **Say it's missing, in one short clause:** "The agenda doesn't give the size."
3. **Give the next step:** "Plans are on file with the Town Clerk", with a link or phone.
4. **Never fill a gap from the model's general knowledge**, such as a parent company, likely size, or a "usually" outcome. The one exception is a fixed, sourced explainer ("Zoning changes need a two-thirds vote").
5. **If the item may not be what it seems**, show the quote instead of a paraphrase (solar credits, solar trash cans).

Eight real items, rewritten with their source text, are in the appendix.

---

## B. Simulating real people better (summary; the full protocol is in `tester_protocol_v2.md`)

**What's wrong with persona agents.**
- **They are too capable and too goal-directed.** In AgentA/B, 1,000 agents on Amazon took shorter, more purposeful paths than humans [B1]. In an Oxford study, LLMs alone named the right condition 94.9% of the time; people using the same LLMs managed under 34.5%. Simulated-patient tests didn't predict that gap [B2].
- **They don't click like people.** Across 12 real first-click tests (3,431 people), GPT's click distributions differed significantly in 53% of tasks. Personas and chain-of-thought did nothing for fidelity "apart from inflating believability" [B3].
- **They don't predict people's next move.** Prompted LLMs predicted real shoppers' next action 11.86% of the time [B4].
- **They know too much.** They answer obscure facts "perfectly", the hyper-accuracy distortion [B5].
- **They flatten groups.** They misportray and flatten demographic groups [B6], and synthetic samples show trends but not the size of effects or the spread [B7].
- **They please.** They tell people what they want to hear [B8].
- **What helps:** agents built from real interviews matched people's survey answers 85% as well as people matched themselves two weeks later [B9]. Interview-based twins beat persona descriptions [B7].

**So the protocol:**
1. **The harness, not the prompt, enforces limits.**
   - A 5-second first look: the screenshot is removed after one answer.
   - A scan view: only headings, bold text, link and button text, and the first 12 words of each block, at phone size.
   - A budget of actions and simulated seconds. A patience meter drops at each confusing moment, and the tester quits at zero.
   - Sentences above the persona's reading grade come back marked "[skimmed, didn't take in]". 28% of US adults read at PIAAC Level 1 or below [B10].
2. **Real alternatives first.** Testers do the same task on the town's website, a Facebook group post and LocalGovIndex's public page, then on ours, in rotating order.
3. **Score what they did, not what they said** [B11]:
   - success, checked against a hidden answer key
   - correct first click
   - actions and simulated time
   - backtracks
   - whether they gave up

   Ratings (reaction words [B12], SEQ, SUS [B13]) come last.
4. **Personas from real words.** Each persona is grounded in quotes from residents (letters to the editor, minutes of public comment, Facebook posts shared with permission). Identity is given through life details, not labels [B6].
5. **Calibrate.** The panel must rate the old site worse than the preview, and fail on a page with a planted error. Then check once against 5 real people.

**What simulated testing can't tell us:**
- whether anyone cares enough to sign up and come back
- whether a stranger's site is trusted
- real eyesight, thumbs and interruptions
- local names ("Federal Pond" or "the Tremont St solar")
- whether our facts are wrong
- how a post lands in a heated Facebook group
- how many people will use it

**Cheapest real feedback:**
- **5 hallway tests** (NN/g; Krug's "3 users, once a month") at a library or council on aging: 15 minutes each, a $10 card, a phone set to large text, the same tasks, and no explaining [B14][B15].
- **One post in a town Facebook group, with the admin's permission:** a real item in the new style, plus "Is this useful? What's missing?"
- **Ask 3 clerks or planners** to check one town page for accuracy.
- **A "Was this useful? Yes / No, what's missing?" link** on every item.

---

## Appendix: eight real items, rewritten

Today is Mon Oct 12, 2026. "Preview" is the current text on the preview site. "Source" is quoted from the original agenda or warrant, fetched today. **Bold** marks the one-line summary; the three-line brief follows.

**1. Continuance: Carver Planning Board, Tue Oct 13.**
- *Source:* "Public Hearing Cont'd: 3. Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review… located at 104 Tremont Street… in the Residential Agricultural (RA) Zoning District. Construction, installation and operation of ground-mounted solar and dual-use photovoltaic systems and coupled BESS… – Applicant has requested a continuance to October 27, 2026"
- *Preview:* the project appears twice. "The Planning Board will hold a public hearing on solar projects and battery storage (continued…)" / "The Planning Board will decide whether to allow a solar project by Federal Pond Solar, LLC."
- *Rewrite:* **Postponed: Federal Pond Solar hearing, 104 Tremont St, moves to Oct 27.**
  - Federal Pond Solar, LLC wants to build a solar farm, part of it over farmland, with battery storage at 104 Tremont St, in a residential-farm zone.
  - The company asked to postpone. If the board agrees, there will be no discussion Oct 13; the hearing reopens Tue Oct 27, 6:30 pm, Town Hall Room 1. Speakers get 3 minutes and must sign in.
  - The Conservation Commission heard its wetlands filing Oct 7.
- *Missing:* the size, the distance to homes, and when the hearing opened. Take them from the Oct 7 wetlands agenda and Carver's "applications under review" page. Item 4 on the same agenda (Parallel Products, 235 Main St) is also being postponed, and the preview says the board "will decide" on it.

**2. Permit hearing: Somerset Zoning Board of Appeals, Thu Oct 15.**
- *Source:* "petition of Somerset Energy Storage, LLC… 1606 Riverside Avenue… for a Planned Development under Section 6.10… to allow for the construction of a commercial Battery Energy Storage System (B.E.S.S.), located within the underlying Industrial Zoning District…"
- *Preview:* "Somerset zoning board hears Somerset Energy Storage petition. …The agenda lists a planned development permit for Somerset Energy Storage."
- *Rewrite:* **Battery storage plant proposed at 1606 Riverside Ave: hearing.**
  - Somerset Energy Storage, LLC wants zoning approval to build a commercial battery storage plant at 1606 Riverside Ave, in an industrial zone.
  - Public hearing Thu Oct 15, 6 pm, at the Fairfield Inn, 602 GAR Hwy (not Town Hall). Anyone can speak.
  - It was on the Oct 1 agenda too. The board can vote that night or continue.
- *Missing:* the size and the nearest homes. The agenda says plans are "filed with the Town Clerk", so link to the clerk.

**3. Moratorium, Town Meeting article: Plymouth, Sat Oct 17.**
- *Source:* "ARTICLE 16… a new section, §207-12, Temporary Moratorium on Data Centers, which would enact a one-year temporary moratorium from October 17, 2026, until October 16, 2027 on the application, permitting, construction, expansion, or conversion of any Data Center…" Also: "Registered… voters wishing to participate… shall submit a request… to the Town Clerk not less than forty-eight (48) hours in advance."
- *Preview:* the headline is good, but the dek repeats it ("The warrant lists an article proposing a temporary moratorium").
- *Rewrite:* **One-year ban on new data centers: Town Meeting vote (Article 16).**
  - No new data-center permits or building from Oct 17, 2026 to Oct 16, 2027, while the Planning Board writes rules for fall 2027.
  - Sat Oct 17, 8 am, Plymouth North High School and Zoom. Elected Town Meeting members vote. Other voters can ask the Town Clerk by Thu Oct 15, 8 am, to speak.
  - The Planning Board proposed it. It needs two-thirds, then Attorney General review.
- *Missing:* whether any data center is actually proposed in Plymouth. Say so if we don't know.

**4. Bylaw change by Town Meeting: Harvard, Tue Oct 20.**
- *Source:* "Insert a new §125-53 titled 'Clean Energy Facilities'… incorporating standards for Solar Photovoltaic Installations, Battery Energy Storage Systems, and Consolidated Local Permitting consistent with 225 CMR 29.00 and Chapter 239 of the Acts of 2024". The warrant's own summary: "The current solar overlay district needs replacing because of a new state permitting law… for the first time, includes standards for battery energy storage systems."
- *Preview:* "Harvard Town Meeting takes up solar and battery storage rules."
- *Rewrite:* **New rules for solar farms and, for the first time, battery storage: Town Meeting vote (Article 5).**
  - The article replaces Harvard's 2010 solar zoning with rules on where and how solar and battery storage can be built, covering safety, screening and cleanup bonds, to fit a 2024 state law.
  - Tue Oct 20, 6 pm, Bromfield School auditorium. Registered voters attend, speak and vote.
  - The Select Board recommends it unanimously; the Finance Committee took no position. It needs two-thirds, then AG review.
- *Missing:* nothing that matters. The warrant's summary did the work.

**5. Ordinance hearing: Westfield City Council, Thu Oct 15.**
- *Source:* "by the City Council to consider a petition of the City Council to adopt zoning regulations for clean energy systems, including BESS. Access the full petition at the City Clerk's Office (City Hall) or at: www.cityofwestfield.org/applications"
- *Preview:* "Westfield City Council holds hearing on battery storage rules."
- *Rewrite:* **New zoning rules for clean-energy projects, including battery storage: hearing.**
  - The council proposes zoning rules for clean-energy projects, including battery storage. The notice doesn't say what they require; the full text is at cityofwestfield.org/applications.
  - Thu Oct 15, 6 pm, Council Chambers, City Hall, 59 Court St. Anyone can speak.
  - The Planning Board took it up Oct 6. The council votes after the hearing, possibly at a later meeting.
- *Missing:* the content of the rules. Fetch the petition and summarize it; until then, link it.

**6. Final adoption vote: Geneva (NY) Town Board, Tue Oct 13.**
- *Source:* "RESOLUTION NO. 68-2026 — Adopting Local Law No. 5 of 2026, Battery Energy Storage Systems". The resolution also says the hearing "was duly held on September 8, 2026."
- *Preview:* "Geneva Town Board considers adopting a battery storage law."
- *Rewrite:* **Final vote on Geneva's battery storage law.**
  - The law adds battery storage rules to the town code and zoning.
  - Vote Tue Oct 13 at the regular meeting, after a 6 pm budget hearing. There's no hearing on this law, but anyone can speak at "privilege of the floor" early in the meeting.
  - The hearing was Sep 8. If passed, the law is filed with the NY Secretary of State.
- *Missing:* what the law requires (size limits, setbacks) and the meeting place, which the agenda doesn't state. Link the Sep 8 hearing notice.

**7. Permit extension: Westfield Planning Board, Tue Oct 13.**
- *Source:* "Request by Servistar Realties LLC for permit extension allowing a data center off Ampad Rd. & Servistar Industrial Way (originally granted 10/19/21)"
- *Preview:* "Westfield planners take up Servistar Realties data-center permit extension." Its tag: "Permit application."
- *Rewrite:* **Data center approved in 2021 off Ampad Rd asks for more time.**
  - Servistar Realties LLC got a permit in Oct 2021 for a data center off Ampad Rd and Servistar Industrial Way, and wants it extended.
  - Special meeting Tue Oct 13, 6 pm, Zoom only (ID 897 2449 3800), or Channel 15. Not a hearing; public comment only if the board votes to allow it.
  - It was on the Sep 15 agenda too.
- *Missing:* the size, the length of the extension, and whether anything is built. Find the 2021 decision.

**8. Wetlands hearing: Swansea Conservation Commission, Tue Oct 13.**
- *Source:* "SE72-1889-AMEND-Notice of Intent by Pedro Rodri uez/Old Warren Rd Development LLC for proper located at 0 Old Warren Rd… for proposed ground-mounted photovoltaic solar & battery energy storage system within the Jurisdictional wetland resource areas."
- *Preview:* "Swansea Conservation Commission hears Old Warren Rd Development wetlands filing." Its tag: "4.9 MW".
- *Rewrite:* **4.9 MW solar farm with batteries off Old Warren Rd: wetlands hearing.**
  - Old Warren Rd Development LLC filed an amended wetlands request for a solar farm with battery storage at 0 Old Warren Rd (4.9 MW, from its Sep 30 state filing).
  - Tue Oct 13, 6 pm, Swansea Police Station, 1700 GAR Hwy. Anyone can speak. The Commission rules only on wetlands, not on whether the project is allowed.
  - The same night: Phase 2 of a solar facility at 440 Old Warren Rd.
- *Missing:* acres and the nearest homes. Use the MassDEP filing.

---

## Sources

**Part A: how real services and people write about upcoming decisions**
- [A1] Tewksbury resident, "Letter to the editor: proposed lithium-ion battery storage facility," Tewksbury Carnation, Oct 6, 2025. https://tewksburycarnation.org/2025/10/06/letter-to-the-editor-proposed-lithium-ion-battery-storage-facility/ ; state docket page: https://www.mass.gov/info-details/tewksbury-battery-project
- [A2] Scott Merzbach, "New hearing scheduled for contentious battery storage project in Hadley," Daily Hampshire Gazette, Jun 20, 2026. https://gazettenet.com/?p=464384
- [A3] City of Boston, Zoning Board of Appeal hearing notice (written comments 48 hours ahead; sign up to testify). https://www.boston.gov/public-notices/16487791
- [A4] PlanningAlerts (OpenAustralia Foundation), application page. https://www.planningalerts.org.au/applications/3530779
- [A5] GovTrack bill pages, as captured in analog_patterns.md. https://www.govtrack.us/congress/bills/119/hr1 (a direct fetch returned 403 today)
- [A6] City Bureau, "Bridging the civic information gap: how we record public meetings matters," May 28, 2025 (notes open with who, what, where, when; about 5,000 words shorter than minutes). https://www.citybureau.org/notebook/2025/5/28/bridging-the-civic-information-gap-how-we-record-public-meetings-matters ; study summary: https://brechner.jou.ufl.edu/2025/04/03/study-documenters-empower-citizen-governance/
- [A7] GOV.UK, Plan and manage content (user needs). https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content ; clear language: https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
- [A8] Sarah Richards, *Content Design* (2017), and Apolitical, "How the UK transformed digital content." https://apolitical.co/en/articles/how-the-uk-transformed-digital-content
- [A9] Digital.gov, Principles of plain language. https://digital.gov/guides/plain-language/principles ; avoid jargon: https://digital.gov/guides/plain-language/principles/avoid-jargon
- [A10] Amy Schade, "Inverted Pyramid: Writing for Comprehension," NN/g, Feb 11, 2018. https://www.nngroup.com/articles/inverted-pyramid/
- [A11] The News Manual, Ch. 5, "Writing the intro" (20 words or fewer; most newsworthy point first; active voice; present or future tense). https://www.thenewsmanual.net/Manuals%20Volume%201/volume1_05.htm
- [A12] Mass. General Laws c. 40A §5 (zoning amendments need a two-thirds Town Meeting vote, with some housing exceptions). https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40A/Section5
- [A13] Mass. General Laws c. 40 §32 (Attorney General review of town bylaws). https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40/Section32
- Town notice written for residents: Blandford Town Administrator (2-minute comments, questions due in advance). https://townofblandford.gov/tag/battery-energy-storage-systems-bess/page/6/
- Patch "upcoming meetings" roundups list only board, time and room, with no agenda content (an example of too little). https://new.patch.com/massachusetts/foxborough/upcoming-foxborough-meetings-schedule
- Agendas quoted in the appendix (fetched 2026-10-12):
  - Carver PB: https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10132026-616
  - Somerset ZBA: https://www.townofsomerset.org/AgendaCenter/ViewFile/Agenda/_10152026-2195
  - Plymouth warrant: https://www.plymouth-ma.gov/DocumentCenter/View/11128/FINAL-2026-Fall-Annual-Town-Meeting-Warrant-PDF
  - Harvard warrant: https://www.harvard-ma.gov/DocumentCenter/View/3148/STM-Warrant---October-20-2026
  - Westfield City Council: https://www.cityofwestfield.org/AgendaCenter/ViewFile/Agenda/_10152026-8687
  - Geneva NY: https://townofgenevany.gov/Documents/Departments%20and%20Services/Agendas%20&%20Minutes/Town%20Board%20Meeting%20Agendas/2026.10.13%20Town%20Board%20Meeting%20Agenda.pdf
  - Westfield PB: https://www.cityofwestfield.org/AgendaCenter/ViewFile/Agenda/_10132026-8701
  - Swansea ConCom: https://www.swanseama.gov/con%20com%2010.13.26.pdf
  - Boxborough PB: https://www.boxborough-ma.gov/AgendaCenter/ViewFile/Agenda/_10132026-5103
- Preview inspected with Playwright at 390 and 1366 px: https://351watch-7a3k1y6a6-sulmusic2-4637s-projects.vercel.app (/, /ma/carver, /trending, /watch, /search).
- Not reached: Facebook and Nextdoor group posts (they need an account), Axios Local and Boston Globe local briefs (no usable examples turned up in search), a real PlanningAlerts or UK council alert email, and CRS summary guidelines.

**Part B: testing**
- [B1] Wang et al., "AgentA/B: Automated and Scalable Web A/B Testing with Interactive LLM Agents," arXiv 2504.09723 (agents more goal-directed, shorter paths than 1M human users). https://arxiv.org/abs/2504.09723
- [B2] Bean et al., "Clinical knowledge in LLMs does not translate to human interactions," arXiv 2504.18919, 2025 (1,298 people; 94.9% vs under 34.5%). https://arxiv.org/abs/2504.18919
- [B3] Kuric, Demcak and Krajcovic, "What Would GPT Click," arXiv 2605.18302, May 2026 (12 first-click tests, n=3,431; 53% of tasks differ). https://arxiv.org/abs/2605.18302
- [B4] Lu et al., "Can LLM Agents Simulate Multi-Turn Human Behavior? Evidence from Real Online Customer Behavior Data," arXiv 2503.20749 (11.86% next-action accuracy). https://arxiv.org/abs/2503.20749
- [B5] Aher, Arriaga and Kalai, "Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies," ICML 2023 (hyper-accuracy distortion). https://proceedings.mlr.press/v202/aher23a.html
- [B6] Wang, Morgenstern and Dickerson, "Large language models that replace human participants can harmfully misportray and flatten identity groups," Nature Machine Intelligence (2025); arXiv 2402.01908. https://arxiv.org/abs/2402.01908
- [B7] Raluca Budiu, "Evaluating AI-Simulated Behavior: Insights from Three Studies on Digital Twins and Synthetic Users," NN/g, Aug 15, 2025. https://www.nngroup.com/articles/ai-simulations-studies/ ; earlier: https://www.nngroup.com/articles/synthetic-users/
- [B8] Sharma et al., "Towards Understanding Sycophancy in Language Models," arXiv 2310.13548. https://arxiv.org/abs/2310.13548
- [B9] Park et al., "Generative Agent Simulations of 1,000 People," arXiv 2411.10109, 2024. https://arxiv.org/abs/2411.10109
- [B10] NCES, U.S. PIAAC 2023 results (28% of adults at Level 1 or below in literacy, up from 19% in 2017). https://ies.ed.gov/learn/press-release/u-s-adults-score-par-international-average-literacy-skills-below-international-average-numeracy-and
- [B11] Jakob Nielsen, "First Rule of Usability? Don't Listen to Users," NN/g, 2001. https://www.nngroup.com/articles/first-rule-of-usability-dont-listen-to-users/
- [B12] Benedek and Miner, Microsoft Desirability Toolkit (2002; 118 product reaction cards), via MeasuringU. https://measuringu.com/tag/microsoft-desirability-toolkit/
- [B13] MeasuringU on SUS: https://measuringu.com/sus/ ; Single Ease Question: https://measuringu.com/seq10/
- [B14] NN/g, Why You Only Need to Test with 5 Users. https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/
- [B15] Steve Krug, *Rocket Surgery Made Easy* (2010) and *Don't Make Me Think* (trunk test). https://sensible.com/rocket-surgery-made-easy/ ; https://sensible.com/dont-make-me-think/
- Also used in the protocol:
  - UXAgent (Lu et al.), arXiv 2504.09407 (persona generator, fast/slow loops, "not substitutes for human data"). https://arxiv.org/abs/2504.09407
  - NN/g, Thinking Aloud. https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/
  - NN/g, How Long Do Users Stay on Web Pages (the first 10 seconds decide). https://www.nngroup.com/articles/how-long-do-users-stay-on-web-pages/
  - NN/g, F-shaped reading. https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
  - Lyssna, five-second tests. https://www.lyssna.com/guides/five-second-testing/
  - MeasuringU, first click. https://measuringu.com/first-click/
  - NN/g, Success Rate. https://www.nngroup.com/articles/success-rate-the-simplest-usability-metric/
