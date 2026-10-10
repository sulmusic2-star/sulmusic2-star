# Massachusetts local siting market for 351 Watch

*Research date: October 10, 2026. Every figure has a source and an as-of date. Anything marked **EST** is an estimate; the method is shown next to it.*

## Bottom line

A ban-only product is too narrow. In our 24-town crawl, moratoria were **8 of 59 distinct siting events** (3 BESS, 5 data center). The other 51 were project permits, bylaw rewrites, 40B hearings and similar items, and those are what developers have to track every week.

| What | Count | As of / source |
|---|---|---|
| MA municipalities hosting at least one solar (≥500 kW, not rooftop) or ≥1 MW Clean Peak storage project | **169 of 351 (48%)** | SMART lists Jun 1 and Jul 7, 2026; CPS list Jul 1, 2026 |
| SMART 1.0/2.0 siting-relevant projects (≥500 kW AC, not building-mounted) | **355 projects, 985 MW, 145 towns**; 66 not yet operating | DOER SMART list, Jun 1, 2026 |
| SMART 3.0 siting-relevant pipeline | **78 projects, 187 MW, 60 towns** (52 qualified, 26 under review); 56 have a storage adder | DOER SMART 3.0 list, Jul 7, 2026 |
| Clean Peak qualified storage (QESS) | **149 units, 748 MW, 102 towns** (109 units of ≥1 MW, 732 MW, 79 towns) | DOER CPS list, Jul 1, 2026 |
| ISO-NE active MA queue (transmission-level) | **25 projects**: 17 standalone BESS (4,430 MW), 4 offshore wind (3,191 MW), 1 hydro+battery, 3 transmission. **No active MA solar.** 184 MA projects withdrew since Jan 1, 2025. | ISO-NE IRTT, downloaded Oct 10, 2026 |
| EFSB open dockets | **12** (2 BESS certificates, 5 utility substation/line, 1 offshore wind transmission, others). **Zero** consolidated-permit applications as of Aug 10, 2026. | EFSB open dockets and permitting dashboard, Oct 2026 |
| Wetlands filings statewide (NOI + buffer zone + ANRAD) | **4,770 in 2025**; 5,257 in 2024; 3,631 Jan 1–Oct 9, 2026 | MassDEP WIRe data via EEA Data Portal, Oct 10, 2026 |
| Solar/BESS wetlands filings statewide, trailing 12 months | see section 2c | MassDEP WIRe detail records |
| **EST** distinct solar/storage projects going before a local board each year | **~150–300** | section 2d |
| **EST** solar/storage agenda appearances per year (all boards, with continuances) | **~900–1,200** | section 2d |
| **EST** municipalities holding energy-siting bylaw hearings in the next 12 months (driven by 225 CMR 29) | **~100–250** | section 2b |
| Municipalities with data-center moratoria, bans or zoning in 2026 (identified, a floor) | **19** | crawler and press, section 3 |
| MBTA Communities | 177 communities; **157 compliant**, 9 interim, 2 conditional, 9 noncompliant | EOHLC compliance sheet, Aug 31, 2026 |
| Target-customer list | **see `ma_target_companies.csv`** | section 4 |

---

## 1. Active project pipeline (where local permits are needed, and who the developers are)

### 1a. ISO-NE interconnection queue

Source: `https://irtt.iso-ne.com/reports/external` (full public table, 1,751 rows, downloaded Oct 10, 2026).

- **MA active: 25 projects, all FERC-jurisdictional.**
  - 17 standalone BESS: 4,430 MW net (4,571 MW summer).
  - 1 hydro + battery addition: 6.7 MW (Franklin County).
  - 4 offshore wind: Park City Offshore Wind (two entries), SouthCoast Wind 1 at 1,200 MW, Bay State Wind 4.
  - 3 transmission/other: Somerset Wind Link HVDC, plus two National Grid reliability items.
- **Zero active MA solar** in the transmission queue. MA solar connects to the distribution system, so it shows up in SMART and utility DG queues, not ISO-NE.
- **Withdrawals:** 184 MA projects withdrew from Jan 1, 2025 to date (80 solar+storage hybrids, 62 BESS, 28 solar, 8 wind). The newest request in the public table is dated Jan 14, 2025, which is consistent with the queue being closed while ISO-NE moves to its cluster process.
- **Location:** the queue gives county and point of interconnection, not town. Example POIs that identify a town:
  - Electric Ave (Lite Brite, 300 MW, Suffolk)
  - West Medway 345 kV (300 MW)
  - South Agawam (250 MW)
  - Pottersville/Somerset (168 MW)
  - Alps–Berkshire 345 kV line (290 MW) and a new Berkshire substation (136 MW)
  - Canal–Jordan tap, Cape Cod (500 MW)
  - Wakefield Junction (225 MW)
  - Saugus–Melrose line (200 MW)
  - Mystic 115/345 kV, Everett area (204 MW and 508 MW)
  - Chelsea Sta. 488 (Hecate Energy Eastern Ave, 250 MW)
  - South Wrentham (170 MW)
  - West Springfield (45 MW)
  - Millbury–Woonsocket line (204 MW)
  - one unnamed Worcester County site (180 MW)
  - one unnamed Middlesex County site (500 MW)
- **Developer names are mostly hidden** (generic "Battery Storage"). Names that are public: Hecate Energy, SouthCoast Wind, Park City Offshore Wind and Bay State Wind. The other names in the list are project labels only: Lite Brite, Norman Street.
- **Siting relevance:** 17 large BESS projects with 2027–2029 in-service dates. Under the 2024 Climate Act, storage of 100 MWh or more is a "large" facility that can use the EFSB consolidated permit, so these projects sit at the boundary between state and local review. They also drive local hearings: host agreements, zoning exemptions, ConCom filings.

### 1b. SMART solar program (DOER)

Sources:
- SMART 1.0/2.0 list, "Updated June 01, 2026": `https://www.mass.gov/doc/smart-solar-tariff-generation-units/download`
- SMART 3.0 list, "Updated July 7, 2026": `https://www.mass.gov/doc/smart-30-solar-tariff-generation-units-0/download`

Both are linked from `https://www.mass.gov/info-details/lists-of-qualified-generation-units`.

**SMART 1.0/2.0 totals:** 52,290 units; Approved 1,423 MW, Qualified 181 MW.
- 50,572 are small (25 kW or less, almost all residential) and need only a building permit.
- **1,717 are large**, totaling 1,243 MW. Of these, 1,153 are building-mounted, 188 canopy, 30 landfill, 21 agricultural, 12 brownfield and 1 floating. 293 have a storage adder.

**Siting-relevant filter:** I counted projects of at least 500 kW AC that are not building-mounted. These are the ground-mount, canopy, landfill, agricultural and floating projects that normally need site plan review, a special permit and often an NOI.
- **SMART 1.0/2.0: 355 projects, 985 MW, in 145 towns.** 289 are approved/operating; 66 are still in the pipeline (qualified, under review or waitlisted, 165 MW). Commercial-operation years run 2018 to 2026, peaking at 78 projects in 2021.
- **SMART 3.0: 1,091 applications, 505 of them large (267 MW). 78 are siting-relevant (187 MW, 60 towns).** Of the 78, 40 are 2 MW or larger and 56 have a storage adder. There are also 11 large building-mounted projects of 900 kW AC or more.
- Top siting-relevant towns, SMART 1.0/2.0: Carver 13; Southbridge, Westport and Wareham 9 each; Ware and Acushnet 8 each. SMART 3.0: Carver 7.
- **Distinct names:** 259 applicant names and 475 company names across applicant, installer and owner in SMART 1.0/2.0 siting-relevant projects; 49 applicant names in SMART 3.0. Many are single-project LLCs. Normalized to parent companies, about 60 firms have 3 or more projects (see the CSV).

**Largest names in siting-relevant SMART projects** (normalized; counts combine applicant, installer and owner roles):
- Nexamp; Borrego (now New Leaf Energy for development); NextGrid; Grid Builders; BlueWave; Clearway; Kearsarge; Syncarpha; ZPT/Zero-Point; American Renewables Construction; ENGIE; Parallel Products Solar Energy; Ameresco; Conti Solar; Navisun; CVE North America; ReWild Renewables; Dynamic Energy; Agilitas; Citizens Enterprises.
- **The SMART 3.0 front of the pipeline** (78 siting-relevant projects, normalized):
  - NextGrid: 13 projects, 38 MW, 12 towns, many under tree-named LLCs.
  - Grid Builders LLC: installer on 16 projects, most of them NextGrid's.
  - Kearsarge Solar: 9 projects, 26.5 MW, 7 towns.
  - Parallel Products Solar Energy 5; Solect 5; Greenskies 4; ReWild 3; Valta 3; BlueWave 3; Agilitas 2.
  - One each: New Leaf, PureSky, EDF/PowerFlex, CVE, Allco, Citizens Enterprises, REDP, ReVision, ProGeneration.

**Cross-check against the crawler:** three companies appear in both the state lists and our agenda hits.
- Parallel Products Solar Energy: Carver Planning Board, 235 Main St, Oct 13, 2026.
- Kearsarge Solar: Plymouth AOBC agreement.
- New Leaf Energy: Meadow Solar 1, Carver.

The SMART list therefore names the same applicants who show up at local boards.

### 1c. Clean Peak Standard qualified units

Source: `https://www.mass.gov/doc/clean-peak-qualified-units-list-7126/download`, "Updated July 1, 2026".

- **Totals:** 1,814 MW qualified, made up of 748 MW QESS, 862 MW RPS (mostly PV) and 205 MW demand response.
- **QESS: 149 storage units, 748 MW, in 102 towns.**
  - The four largest units are 250 MW Medway Grid LLC (effective Dec 3, 2025; probably the same project as the 300 MW West Medway BESS in the ISO-NE queue), 158 MW Cranberry Point Energy Storage in Carver, and Brookfield's two Rowe units at 48 and 40 MW (listed as J. Cockwell 1 and 2).
  - The rest are 5 MW or smaller, typically SMART-paired or distribution-level BESS.
- **QESS of at least 1 MW: 109 units, 732 MW, in 79 towns.** Units newly qualified by year: 2022: 15; 2023: 29; 2024: 22; 2025: 23; 2026 through July 1: 11.
- **Top owners/aggregators (≥1 MW):** Nexamp 20; AES Clean Energy Development 18 (plus 3 as The AES Corporation); Stem 7; Syncarpha 7; Engie Storage 6; Kearsarge 5; Enel X 4; Agilitas 3; AMP Solar Group 3; SYSO 6; Lodestar 2; Brookfield 2.

### 1d. EFSB, DPU and MassCEC siting dockets for larger facilities

Sources: `https://www.mass.gov/info-details/efsb-and-dpu-siting-open-dockets` and `https://www.mass.gov/info-details/efsb-permitting-dashboard` (last updated Oct 9, 2026).

**12 open dockets:**
- **BESS:**
  - EFSB 26-02, Hillman Energy Center, Tewksbury: certificate petition filed Jun 30, 2026; zoning exemptions already granted in 25-08; a motion to withdraw was filed in Sep 2026.
  - EFSB 26-01, Moraga Storage LLC, Oakham: certificate petition; 25-07 zoning exemption.
- **Eversource substation zoning exemptions:**
  - EFSB 25-11, Falmouth Tap
  - EFSB 25-09, Blandford 19J
  - EFSB 25-06, Dartmouth Fisher Rd, explicitly to interconnect distributed generation
  - EFSB 25-02, Plymouth West Pond and Wareham Tremont, both in the Carver/Plymouth solar cluster
- **National Grid:** EFSB 25-01, rebuild of the 69/115 kV line through 17 towns from Millbury to Buckland.
- **Other:**
  - EFSB 24-01, Hingham Municipal Lighting Plant 115 kV line
  - EFSB 22-06, Commonwealth Wind transmission to Barnstable
  - two gas dockets (22-05, 18-02)
  - EFSB 21-01, a public-participation inquiry

**Consolidated permits (2024 Climate Act, St. 2024 c. 239):**
- **State level:**
  - EFSB regulations were promulgated Feb 27, 2026 and finalized Jun 5, 2026.
  - The EFSB dashboard reported **zero consolidated-permit applications as of Aug 10, 2026**.
  - Large storage, meaning 100 MWh or more, goes to the EFSB, which has a 15-month decision clock (Foley Hoag, Jul 1, 2026).
  - Small facilities go to the municipality under 225 CMR 29: towns could start accepting applications Jul 1, 2026, **must accept them by Oct 1, 2026**, and must decide within 12 months of a complete application or the project is constructively approved.
- **Local deadline wave:** the Oct 1, 2026 deadline is why our crawl found Northampton, Westford, Sturbridge, Amherst, Great Barrington, Charlton, Pittsfield and Westfield all rewriting energy bylaws in the same six weeks.
- **What this means for monitoring:** the decision point for most projects stays local, and local decisions now run on statutory clocks. Missing a hearing is costlier now.
- **Generation threshold:** large generation is 25 MW or more under the Act. That figure is from my background knowledge, not re-verified this session. The storage threshold is verified.

**MassCEC:** no siting docket of its own. It shows up as a wetlands applicant (one 2025 NOI) and runs program grants. Not a target customer.

### 1e. MEPA Environmental Monitor

- **Blocked.** The new eMonitor (`eeaonline.eea.state.ma.us/EEA/MEPA-eMonitor`) calls an AWS API that returned HTTP 403 without the app's embedded, encrypted key. I did not try to extract or decrypt that key. The search found no published annual ENF count.
- **What I did find:** individual solar ENFs, for example Snipatuit Road Solar (Rochester), Stony Brook Solar (Ludlow) and Dunstable Pleasant St, and a MEPA "advance notice tracker" document for an Acushnet solar project (Dec 9, 2025).
- **Role of MEPA:** ground-mount solar typically crosses MEPA review thresholds on land alteration or tree clearing, not on megawatts. MEPA is a useful early signal (an ENF usually comes months before local hearings), but it reaches far fewer projects than local permits do.
- **Next step:** get the eMonitor API terms from EEA, or count ENFs by hand from the bi-weekly Monitor PDFs.

---

## 2. Volume of local siting events

### 2a. Crawler evidence: `projects/351watch/data/agenda_hits.json`

- **Scope:** 24 of 30 sample towns automated; 338 agenda documents (93 recovered by OCR); 178 hits.
- **Window:** meeting dates Aug 26 to Oct 29, 2026. That is 45 days back from the Oct 10 run plus whatever upcoming agendas were posted, so I treat the effective window as **~52 days**.
- **Classification:** I hand-classified every hit by reading its snippet, then collapsed repeat mentions of one item (agenda, minutes and packet) into a single event. The script is in the scratchpad.

| Category | Raw hits | Distinct events | Towns | Examples |
|---|---|---|---|---|
| Solar/BESS project permits (SP/SPR, NOI, ZBA appeal, pole petition) | 25 | 13 items covering 14 projects | 6 | Carver: Federal Pond Solar, Golden Pond Solar 1 (floating PV + BESS), Parallel Products, Wareham St Solar 2, Atwood/Meadow Solar 1 (New Leaf). Plymouth: Federal Furnace Rd Solar 1 NOI. Leominster: 259 Lancaster St BESS, 5 Chestnut St BESS appeal. Charlton: NextEra and Sturbridge Rd Solar Farm. Amherst: 191 W Pomeroy. Pittsfield: Blue Sky Utility. |
| Energy-siting bylaws (225 CMR 29 consolidated permit, BESS/solar bylaws) | 44 | 11 | 11 | Westford SCEIF §6.6; Pittsfield BESS overlay; Northampton SCEIF; Sturbridge; Amherst Art. 18; Sudbury; Westfield; Great Barrington; Fitchburg; Charlton |
| BESS moratoria | 6 | 3 | 3 | Fitchburg, Leominster; Uxbridge (seen as an abutter notice in Sutton) |
| Data-center moratoria | 15 | 5 | 5 | Northampton, Pittsfield, Plymouth, Fitchburg, Leominster |
| Data-center zoning (definitions, use rules, studies) | 6 | 5 | 4 + 2 abutters | Charlton, Bridgewater, Wakefield, Amherst; Uxbridge and Northbridge via Sutton |
| 40B comprehensive permits | 25 | 8 | 4 | Dartmouth (Hathaway, Hawthorn, ZCMP-25-2/3, Bliss Corner); Andover (Trailside, 40 units); Plymouth (120 Carver LLC, Pasture Hill); Amherst |
| Wireless | 4 | 2 | 2 | Andover small cell; Great Barrington 5G/small-cell bylaw |
| Other zoning (housing, industrial, overlays) | 35 | 11 | 11 | Billerica Rt 3 overlay, Pittsfield form-based code, Amherst ADU/PRP |
| Not siting (municipal solar contracts, non-zoning bylaws) | 18 | 4 | 6 | Plymouth/Kearsarge AOBC, Dartmouth snow bylaw |
| **Total** | **178** | **~62 (59 siting)** | 21 | |

**Precision:** 160 of 178 hits (90%) were real siting items.

**Coverage gaps that bias these numbers down:**
- Conservation Commission agendas were thin: only 8 hits, from 4 towns.
- NOI agenda lines often name a landowner or street address, not "solar".
- There is no `data_center` or `ev_charging` keyword. Data-center items were caught only through "moratorium" or "zoning amendment".
- 6 of 30 towns were not automated.

### 2b. Extrapolation method (EST)

1. **Annualize** the ~52-day window: ×7.0 (range ×6.1 to ×8.1 for a 45–60-day window).
2. **Scale the 24 towns to the state** using their measured share of statewide activity:

| Measure | Share held by the 24 crawled towns |
|---|---|
| SMART 1.0/2.0 siting-relevant projects | 48 of 355 = **13.5%** |
| SMART 3.0 siting-relevant projects | 15 of 78 = **19.2%** |
| CPS QESS ≥1 MW | 13 of 109 = **11.9%** |
| Energy-developer-named wetlands filings, 2025 | 12 of 51 = **23.5%** |
| All wetlands filings, 2025 (proxy for general development) | 492 of 4,770 = **10.3%** |

   I use **15–20%** for energy items (×5 to ×6.7) and **~10%** for 40B, wireless and other zoning (×10). These shares already correct for the sample being chosen in siting-active towns such as Carver, Plymouth and the Berkshire BESS towns.
3. **Convert a 52-day snapshot of projects into annual projects:** local permitting runs 3–6 months with continuances, so a project shows up in about 2–3 consecutive windows. Divide by 2–3.

**Results (all EST):**
- **Solar/BESS projects at a local board:** 14 / 0.15–0.20 = 70–93 active statewide in any 52-day window. Times 7, divided by 2–3, gives **~160–330 distinct projects a year**; I use **~150–300**.
- **Solar/BESS agenda appearances:** 25 hits / 0.15–0.20 × 7 = **~900–1,200 a year** across planning boards, ZBAs, ConComs and councils.
- **Energy-siting bylaw hearings:** 11 of 24 sample towns (46%) had one in this window, pushed by the Oct 1, 2026 225 CMR 29 deadline. Discounting 30–50% for the energy-heavy sample, I estimate **~100–250 municipalities** hold such hearings over the next 12 months. This is a one-time wave that should fade in 2027. Each bylaw takes 2–5 meetings (planning board hearing, council or town-meeting vote, AG review), so expect **~300–900 bylaw agenda items**.
- **BESS moratoria:** 3 in this window. The project tracker (`data/tracker.json`, verified Oct 10, 2026) lists 11 moratoria plus 2 special acts in 26 towns. The AG has disapproved most of them under c. 40A §3 (Becket, Worthington, Carver, Ware, Northfield). Moratoria are high-signal but few, consistent with the national decline (Sabin Center: 165 new restrictions in 2023, 112 in 2024, 70 in 2025).
- **40B:** 8 projects with hearings in 4 of 24 towns; 8 / 0.10 = ~80 active statewide per window. Hearings run up to 180 days, so divide by about 3: **~150–250 comprehensive-permit projects a year with hearings**. I could not find a published statewide count to check this against.

### 2c. MassDEP wetlands filings (WIRe / eDEP)

- **Source:** the EEA Data Portal's public Data Lake API, the same one the portal page at `https://eeaonline.eea.state.ma.us/portal#!/search/wire` uses. Endpoints:
  - `…/EEA/DataLake/V1.0/DataLakeAPI/wire?FromFilingDate=…&ToFilingDate=…` for counts
  - `…/wire/{NOIId}` for detail records, which include a project-description field
- **Statewide filings** (NOI + buffer-zone-only + ANRAD): 2021: 6,040 · 2022: 5,496 · 2023: 5,077 · 2024: 5,257 · **2025: 4,770** · 2026 through Oct 9: 3,631 · **trailing 12 months (Oct 1, 2025–Sep 30, 2026): 4,614**.
- **Name-based lower bound** (applicant or company name contains solar, storage, renewable or a known developer): 28 in 2024, 51 in 2025, 24 in 2026 to date, in 18–36 towns a year.
- **Utility filings:** Eversource 25 and National Grid 48 in 2025, which is the transmission/substation channel.
- **Description-based count** from the detail records: WETLANDS_RESULT_PLACEHOLDER

### 2d. Triangulated estimate for solar and storage (EST)

| Method | Distinct solar/BESS projects needing local discretionary permits per year |
|---|---|
| Crawler extrapolation (2b) | ~160–330 |
| SMART 3.0 pipeline: 78 siting-relevant + 11 large rooftop applications so far, plus SMART 1/2 projects still in the pipeline (66), plus standalone BESS outside SMART (CPS adds ~20–30 units ≥1 MW a year; 17 ISO-NE BESS) | ~120–200 entering permitting per year |
| Wetlands: WETLANDS_TRIANGULATION_PLACEHOLDER | |
| **Working estimate** | **~150–300 projects/yr; ~900–1,200 agenda appearances/yr; ~100–250 towns with energy-bylaw hearings in the next year** |

---

## 3. Other siting topics in Massachusetts

| Topic | Volume (sourced or **EST**) | Who pays to monitor | How many companies |
|---|---|---|---|
| **Data centers** | Crawl: 10 municipalities with data-center items in ~52 days (5 moratoria: Northampton, Pittsfield, Plymouth, Fitchburg, Leominster; zoning: Charlton, Bridgewater, Wakefield, Amherst; Uxbridge moratorium and Northbridge prohibition via abutter notices). Press adds Holyoke (ban, Jun 16, 2026), Lowell (1-yr moratorium, Mar 2026), Mansfield (ban, May 5, 2026 town meeting), Westfield (moratorium, Jul 2026), Shutesbury, Agawam (blocked per tracker), Everett (ban proposed), Boston (prohibited-use order, Sep 2026). **19 municipalities identified, a floor.** Executive order of Sep 8, 2026: projects over 25 MW peak need a host-community benefits agreement before state permitting, which moves the decision to select boards and city councils. Pipeline: 48 tracked facilities (44 operating, 4 proposed: Holyoke 20 MW, Westfield campus, AWS Grafton, AWS Westborough); 5 stopped. **EST:** 40–100 towns take up data-center zoning in 2026–27. | Developers and operators (site selection and expansions), utilities (large-load interconnection), land-use counsel, brokers | ~20 operators/developers named in MA (Digital Realty, Equinix, CoreSite, Centersquare/Cyxtera, TierPoint, Markley, AWS, EdgeConneX, Iron Mountain, 11:11, ColoSpace, Servistar, Chestnut River Power, Davis Cos.) |
| **MBTA Communities (§3A)** | 177 communities: 157 compliant, 9 interim, 2 conditional, 9 noncompliant (Aug 31, 2026). The rezoning wave is mostly over. What remains is as-of-right multifamily site plan reviews inside 3A districts, plus amendments and litigation in noncompliant towns. | Multifamily developers, land-use attorneys, housing consultants | Not counted (~100+ MA multifamily developers, **EST**) |
| **40B comprehensive permits** | Crawl: 8 projects in 4 of 24 towns per window. **EST ~150–250 projects a year with ZBA hearings** statewide. Also "safe harbor" fights (Plymouth). | 40B developers, abutter-side attorneys, peer-review engineers, municipalities | Not counted; dozens of active developers (**EST**) |
| **Wireless / small cell / towers** | Crawl: 2 events in 2 towns (Andover small cell; Great Barrington 5G bylaw). Wetlands: ~0.1% of filings. **EST ~50–150 local items a year**, low confidence. | Tower companies, carriers, site-acquisition firms | Concentrated: about 10–20 firms (American Tower, Crown Castle, SBA, Vertical Bridge, Verizon, AT&T, T-Mobile, plus site-acquisition contractors). Many already have national tools. Low priority. |
| **EV charging hubs** | Crawl: 0 (no keyword). Wetlands: WETLANDS_EV_PLACEHOLDER. Mostly by-right or site plan review. | Charging networks, fleet depots | Small; not a launch segment |
| **Transmission / substations** | EFSB: 5 open utility dockets (Plymouth/Wareham, Dartmouth, Blandford, Falmouth, the 17-town NGrid rebuild) plus 1 offshore wind. Wetlands: Eversource ~25 and NGrid ~48 filings in 2025 (~0.5–0.6% of all filings). | Utilities (2 investor-owned plus 41 municipal light plants), offshore wind developers, their consultants | Few buyers but high-value. Eversource, National Grid, SouthCoast Wind and Commonwealth Wind (Avangrid) are listed in the CSV. |

---

## 4. Target-customer list (`ma_target_companies.csv`)

- **Columns:** company, segment, evidence_of_ma_activity_url, approx_ma_projects, ma_towns, evidence_detail.
- **Contents:** company names and public URLs only; no personal contact data.
- **What `approx_ma_projects` means:** siting-relevant MA projects in the public lists, combining SMART 1/2 and 3.0 projects of at least 500 kW that are not rooftop, CPS QESS of at least 1 MW, and energy-named wetlands NOIs from 2024–2026. Applicant, installer and owner roles are combined, so EPCs and long-term owners are counted alongside developers.
- **Who is excluded:** residential installers (Sunrun, Tesla and similar), because their projects need only building permits, and single-project LLCs whose parent I could not identify.
- **Row counts by segment:** CSV_SEGMENT_PLACEHOLDER

**Priority buyers for a pilot:**
1. Developers with active SMART 3.0 or BESS pipelines that are in front of local boards now: Kearsarge, NextGrid, BlueWave, Nexamp, New Leaf, Parallel Products, Solect, ReWild, Agilitas, AES, Syncarpha, Lodestar, PureSky, CVE, Valta, Greenskies, EDF/PowerFlex.
2. Land-use and energy counsel and wetlands/civil consultants who appear for them: Foley Hoag, Pierce Atwood, Nutter, Bacon Wilson, Beals and Thomas, Weston & Sampson, Horsley Witten. This segment is under-sampled; see the gaps below.
3. Large-BESS and transmission players, where one missed hearing is expensive: Hecate, Moraga/Hillman parents, Medway Grid, Cranberry Point, Eversource, National Grid.
4. Data-center developers and operators.

**Illustrative revenue size (EST, not a forecast):** about 60–120 paying organizations in MA (out of ~60 developers/EPCs with 3+ projects, ~20 data-center firms, ~15–40 law/consulting firms, and a handful of utilities and wind companies) at $200–600 a month comes to **~$150k–$850k ARR** in MA alone.

---

## 5. Implications for 351 Watch

1. **Pitch "every siting decision".** In this window, project permits plus bylaw rewrites outnumbered moratoria by about 6 to 1, and Oct 1, 2026 (the 225 CMR 29 acceptance deadline) is producing a statewide wave of bylaw hearings right now.
2. **Recommended crawler changes:**
   - Add `data_center` and `ev_charging` topics.
   - Prioritize Conservation Commission agendas.
   - Match agenda lines against the developer and SPV names from the SMART, CPS and wetlands lists, because NOI lines often carry only an LLC name or address. A watch-list of about 500 SMART/CPS LLC names would catch "Golden Pond Solar 1, LLC" without any keyword.
   - Add abutter-town notices (MGL 40A §5). Sutton's PB packet revealed the Uxbridge and Northbridge actions.
3. **Use state lists as leading indicators:**
   - a new SMART 3.0 or CPS entry, or a new wetlands NOI by a known developer, comes before the local hearing
   - EFSB dockets and ISO-NE POIs flag the large BESS sites
4. **Wetlands data is free to automate.** The MassDEP Data Lake API is public and updated daily (filing date, town, applicant, company, project description). That makes it a cheap second feed that does not depend on town websites.

---

## Sources (accessed Oct 10, 2026 unless noted)

- ISO-NE IRTT public queue: https://irtt.iso-ne.com/reports/external
- DOER SMART 1.0/2.0 Solar Tariff Generation Units (updated Jun 1, 2026): https://www.mass.gov/doc/smart-solar-tariff-generation-units/download
- DOER SMART 3.0 Solar Tariff Generation Units (updated Jul 7, 2026): https://www.mass.gov/doc/smart-30-solar-tariff-generation-units-0/download
- DOER Clean Peak Standard qualified units (updated Jul 1, 2026): https://www.mass.gov/doc/clean-peak-qualified-units-list-7126/download
- Lists of qualified generation units: https://www.mass.gov/info-details/lists-of-qualified-generation-units
- SMART 3.0 program details: https://www.mass.gov/info-details/smart-30-program-details
- EFSB and DPU open dockets: https://www.mass.gov/info-details/efsb-and-dpu-siting-open-dockets
- EFSB permitting dashboard (updated Oct 9, 2026): https://www.mass.gov/info-details/efsb-permitting-dashboard
- EFSB 26-02 motion to withdraw (Sep 2026): https://media.wbur.org/wp/2026/09/EFSB-26-02-Motion-to-Withdraw-1.pdf
- EFSB 21-02 final decision (Carver BESS): https://www.mass.gov/doc/efsb-21-02-final-decision/download
- Foley Hoag, "Siting Battery Storage in Massachusetts: A New Regulatory Landscape" (Jul 1, 2026): https://foleyhoag.com/news-and-insights/blogs/energy-and-climate-counsel/2026/june/siting-battery-storage-in-massachusetts-a-new-regulatory-landscape/
- Pierce Atwood alert on the 2024 clean energy bill: https://www.pierceatwood.com/alerts/breaking-massachusetts-passes-clean-energy-bill-streamlining-permitting-process-battery
- MassDEP Wetlands NOI lookup: https://www.mass.gov/info-details/wetland-notices-of-intent-lookup ; portal: https://eeaonline.eea.state.ma.us/portal#!/search/wire
- MEPA eMonitor (API blocked): https://eeaonline.eea.state.ma.us/EEA/MEPA-eMonitor/search
- MBTA Communities compliance status (as of Aug 31, 2026): https://www.mass.gov/files/csv/2026-08/Compliance%20Status%20Sheet%20as%20of%208-31-26.csv (linked from https://www.mass.gov/info-details/multi-family-zoning-requirement-for-mbta-communities)
- Data-center tracker, Massachusetts (map dated Oct 2026): https://morethanjustparks.com/data-center-tracker/state/massachusetts
- WBUR, data-center pushback (Apr 6, 2026): https://www.wbur.org/news/2026/04/06/data-centers-ai-massachusetts-pollution-pushback
- WBUR, Healey data-center order (Sep 8, 2026): https://www.wbur.org/news/2026/09/08/proposed-data-centers-local-approvals-healey-massachusetts
- The Shoestring, western MA data-center bans (Jul 2, 2026): https://theshoestring.org/2026/07/02/ban-ban-ban-data-center-discontent-reaches-western-massachusetts/
- Boston Globe, Mansfield ban (May 13, 2026): https://www.bostonglobe.com/2026/05/13/business/mansfield-data-centers/
- Fire Engineering, Leominster moratorium: https://www.fireengineering.com/?p=729806
- WBUR, Boston data-center ban proposal (Sep 18, 2026): https://www.wbur.org/news/2026/09/18/boston-data-center-ban-proposal
- Montague BESS application packet (Weston & Sampson): https://montague-ma.gov/files/SPSPR_2025-02_Judd_Wire_BESS_App_Packet.pdf
- Columbia Sabin Center figures, already sourced in `research_notes/Meeting monitor validation/comparables_and_adjacent_niches.md`
- Crawler output: `projects/351watch/data/agenda_hits.json` (generated Oct 10, 2026, 15:11 UTC); tracker: `projects/351watch/data/tracker.json`

## Method notes and gaps

- **Blocked or unavailable:**
  - masssmartsolar.com was blocked by the egress proxy; the correct domain is masmartsolar.com, and the data comes from mass.gov anyway.
  - MEPA eMonitor API: 403.
  - Axios: 403.
  - No published statewide 40B count was found.
- **Company names:** normalized by keyword (for example, "BWC … LLC" maps to BlueWave, "NextGrid <tree> LLC" to NextGrid). Single-project LLCs without an obvious parent were dropped, so per-company counts are lower bounds.
- **Borrego:** counts are mostly from the SMART 1.0/2.0 era. Its development business now operates as New Leaf Energy (background knowledge).
- **Utility DG interconnection queues** (Eversource, National Grid, Unitil) would add distribution-level BESS that is in no state list yet. Not pulled this session.
- **Search budget:** about 9 web searches; the rest came from direct file and API downloads.
