# AG review of clean-energy bylaws, 2022 – Oct. 2026

Dataset: `projects/351watch/data/ag_decisions.json` (140 rows: 131 AG decisions, 5 court rulings, 3 city ordinances, 1 pending). Built Oct. 10, 2026.

## Bottom line

**Is the claim true?** Yes for moratoria, with two footnotes. "Regulating bylaws get approved" is also true, but usually with specific provisions struck.

- **2024 through Oct. 2026 moratoria:** the AG ruled on the merits of 15 solar or BESS moratorium articles. These came from 12 towns in 13 letters, and **all 15 were disapproved; none were approved.** The towns were Hanson, Northfield (2), Hampden, Blandford, Southwick, Worthington (3), Becket, Sturbridge, Lee, Chesterfield, Gill and Brookfield.
  - **Footnote 1, Spencer:** Spencer's two moratoria (Nov. 9, 2023 Special Town Meeting) were not struck down. On July 19, 2024 the AG took **no action** because they had become moot: the town adopted solar and BESS zoning in May 2024, which ended them by their own terms. So "every moratorium *ruled on* was struck" is exact. "Every moratorium *found*" has this one non-ruling.
  - **Footnote 2, Gill:** Gill's Article 7 combined a BESS moratorium with a data-center moratorium. The AG struck the BESS part and **approved** the data-center part.
- **Full window, 2022 – Oct. 2026:** 21 moratorium articles reached the AG. 18 were disapproved, 2 got no action (Spencer), and **1 was approved: Medway, May 17, 2022.** That was a BESS moratorium limited to one zoning district, decided 16 days before the SJC's *Tracer Lane II* ruling (June 2, 2022). No solar or BESS moratorium has survived since *Tracer Lane II*. The AG says so itself: Blandford's 2026 letter notes it approved a Blandford solar moratorium in 2019, "prior to" *Tracer Lane II*, and has disapproved them since.
- **Regulating bylaws:** 114 non-moratorium decisions.
  - 76 were approved outright and 33 approved with specific text struck.
  - 5 were disapproved in full: Wareham 2022, Shutesbury 2023, Hubbardston 2023, and the Wendell and Shutesbury 2024 licensing general bylaws.
  - Since Jan. 2024, **no zoning regulation of solar or BESS has been disapproved in full** (47 approved, 16 in part). The only full disapprovals were the two general bylaws, which the AG said had to be adopted as zoning.
- **Accurate phrasing for 351 Watch:** "Since the SJC's Tracer Lane II decision in June 2022, the Attorney General has disapproved every solar or battery-storage moratorium she has ruled on: 18 articles in 14 towns, including all 15 from 2024 to 2026. Over 2022–2026 she approved 96% of regulating bylaws in whole or in part (109 of 114), typically striking only specific provisions."

## Source and method

- **Official source.** The AG's Municipal Law Unit publishes every bylaw decision letter in the "Municipal Law Unit Decision Look-up." It is linked from mass.gov/the-municipal-law-unit (curl gets a 403 there; I confirmed the link with Playwright and Chromium). The portal is a Hyland OnBase Public Access site at `massago.hylandcloud.com/231publicaccess/MLU.html`, and its JSON API needs no login or CAPTCHA:
  - `api/CustomQuery/KeywordSearch` with QueryID 103 ("MLU Public Access") searches by Case Number, City/Town, Decision Date and Topic.
  - `api/DocumentType/FullTextSearch` with DocTypeID 121 searches the full text.
  - `api/Document/{id}/` returns the PDF.
- **Topic filters.** The AG tags letters with topics: SOLAR (183 letters, all years), BATTERY STORAGE SYSTEMS (54) and SMALL CLEAN ENERGY FACILITIES (1). For 2022 to Oct. 10, 2026 that gave 108 letters.
- **Full-text terms.** I searched battery, energy storage, BESS, solar, photovoltaic, moratorium, clean energy and renewable, by year and by month. Monthly and yearly results matched, so the search is not capped. That found 109 more candidates that had no clean-energy tag. Gill's BESS moratorium, for example, is tagged DATA CENTERS.
- **Exhaustive pass.** Tags miss some letters, and about 11% of tagged letters are missing from the full-text index (Lunenburg, for example). So I listed all **2,719** decision letters dated Jan. 1, 2022 to Oct. 10, 2026, downloaded every one (retrying 550 that hit the rate limit), and scanned the text for solar, photovoltaic, battery, energy storage, BESS and moratorium. That pass added 2 relevant letters (Tyngsborough 2023 and Hadley 2025). Every letter yielded text.
- **Reading and inclusion.** I read the disposition and reasoning of every candidate. I included letters that rule on an article whose subject is solar, BESS or clean-energy siting, including the solar or BESS sections of whole-bylaw recodifications when the AG ruled on or commented on them. I excluded:
  - letters that only put an article on hold or extend a deadline (Ashfield Dec. 2022, Charlemont Feb. 2023, Rochester June 2025);
  - incidental mentions, such as a rooftop-solar height footnote or boilerplate s. 3 text in unrelated articles: Carver Sept. 2022, North Brookfield 2022 (whose solar provisions were not before the AG), Boxborough and Wakefield recodifications, Mashpee 2024, Millbury 2025, and Shutesbury Aug. 2024.
- **Automated checks.**
  - Every AG row's article numbers, town and meeting month and year match the letter's "Re:" header (131 of 131).
  - A scan of "we disapprove" sentences found no solar or BESS disapproval hidden in a row marked approved.
  - 7 sampled URLs returned the matching PDF.
- **Web searches used: 6 of the 20 allowed** (MLU page, Tracer Lane II date, Sunpin, Duxbury, Wendell Land Court, Leominster), plus one page fetch (Whately).
- **Case numbers.** Some letter headers have typos in the case number (Worthington's says #12184, Oakham's #10690, Boxford's #11398, Hopkinton's #10454, Sherborn's #10941, Tyngsborough's #10951). The dataset uses the portal's case number.
- **Field rules.**
  - `outcome` describes the AG's ruling on the clean-energy provisions. Northfield is "disapproved" because both moratoria were struck, although a severable BESS definition was approved.
  - `bylaw_type` "zoning prohibition" marks articles whose main effect was a town-wide or standalone-BESS ban.

## Statistics (AG decisions only, n = 131, 93 towns)

| Bylaw type | approved | approved in part | disapproved | no action (moot) | total |
|---|---|---|---|---|---|
| moratorium | 1 | 0 | 15 | 1 | 17 |
| zoning regulation | 73 | 32 | 2 | 0 | 107 |
| zoning prohibition | 1 | 1 | 1 | 0 | 3 |
| general bylaw (licensing) | 0 | 0 | 2 | 0 | 2 |
| general bylaw (other) | 1 | 0 | 0 | 0 | 1 |
| consolidated permit bylaw | 1 | 0 | 0 | 0 | 1 |
| **total** | **77** | **33** | **20** | **1** | **131** |

| Year | approved | approved in part | disapproved | no action | total |
|---|---|---|---|---|---|
| 2022 | 10 | 4 | 2 | 0 | 16 |
| 2023 | 20 | 13 | 3 | 0 | 36 |
| 2024 | 17 | 8 | 4 | 1 | 30 |
| 2025 | 18 | 4 | 1 | 0 | 23 |
| 2026 (to Oct. 10) | 12 | 4 | 10 | 0 | 26 |

| Technology | approved | approved in part | disapproved | no action | total |
|---|---|---|---|---|---|
| BESS | 32 | 7 | 11 | 0 | 50 |
| solar | 38 | 13 | 1 | 0 | 52 |
| both | 6 | 13 | 8 | 1 | 28 |
| clean energy (SCEI) | 1 | 0 | 0 | 0 | 1 |

**Moratoria by year** (letters): 2022 had 2 (1 approved, 1 disapproved), 2023 had 1, 2024 had 3 (2 disapproved, 1 no action), 2025 had 1, and 2026 had 10, all disapproved. Moratoria surged in 2026, during the run-up to the Oct. 1, 2026 consolidated-permit deadline.

**Review lag.** The median time from town meeting to AG decision is about 190 days for all rows and about 108 days for 2025–26 moratoria (119 days for all moratoria). That is often close to the moratorium's own end date: Chesterfield's expired Sept. 30, 2026 and was struck on Sept. 23.

### Moratorium ledger (complete)

| AG decision | Town | Article(s) | Tech | Outcome |
|---|---|---|---|---|
| 2022-05-17 | Medway | Art. 10 (Energy Resource district only) | BESS | **approved** (before Tracer Lane II) |
| 2022-11-14 | Carver | Arts. 26, 38 | solar; BESS | disapproved |
| 2023-03-15 | Ware | Art. 22 | BESS | disapproved |
| 2024-03-07 | Hanson | Art. 34 (2-year Tier 1 moratorium within a BESS bylaw) | BESS | disapproved |
| 2024-07-19 | Spencer | Arts. 14, 15 | solar; storage | **no action (moot)** |
| 2024-10-30 | Northfield | Arts. 26, 27 | BESS; solar | disapproved |
| 2025-03-11 | Hampden | Art. 18 | BESS | disapproved |
| 2026-03-11 | Blandford | Art. 1 | both | disapproved |
| 2026-04-24 | Southwick | Art. 5 | both | disapproved |
| 2026-06-08 | Worthington | Art. 6 (town-wide) | both | disapproved |
| 2026-06-08 | Worthington | Arts. 7, 8 (limited areas) | solar; storage | disapproved |
| 2026-06-22 | Becket | Art. 4 | both | disapproved |
| 2026-08-13 | Sturbridge | Art. 63 | BESS | disapproved |
| 2026-08-31 | Lee | Art. 26 | BESS | disapproved |
| 2026-09-23 | Chesterfield | Art. 3 | BESS | disapproved |
| 2026-09-24 | Gill | Art. 7 (BESS part; data-center part approved) | BESS | disapproved |
| 2026-10-07 | Brookfield | Art. 35 | BESS | disapproved |

The AG's own list of moratorium disapprovals, footnoted in its 2026 letters, omits Hanson and Hampden. This dataset finds both.

## How the AG reasons

1. **Solar and BESS are protected uses.** G.L. c. 40A, s. 3, para. 9 (a "Dover amendment" protection) says no bylaw shall "prohibit or unreasonably regulate" solar energy systems or "structures that facilitate the collection of solar energy," except where necessary to protect public health, safety or welfare.
   - From late 2023 (Ware, #11085), letters state that "by statute BESS qualify as solar energy systems." They cite the G.L. c. 164, s. 1 definition of energy storage, *NextSun v. Fernandes* (Land Ct. 2023; cited from Sept. 2023), and from Sept. 2025 *Duxbury Energy Storage* (Land Ct. 2025; first in Rochester #11532).
   - The 2024 Climate Act is cited mainly for its consolidated-permit regime (Ch. 239 of the Acts of 2024; 225 CMR 29.00), not as a separate storage protection.
2. **Tracer Lane II balancing** (SJC, June 2, 2022). The AG weighs the interest a bylaw advances against its burden on the protected use. A near-total ban fails. Bylaws that promote solar are approved readily (Washington, Arlington, Sandwich-style canopy rules).
3. **Moratoria.** The standard 2026 sentence is that the moratorium "lacks any articulated public health, safety, or welfare justification sufficient to justify the moratorium (even for a short amount of time)." Added grounds:
   - *Zuckerman v. Hadley*: a moratorium must be limited in time and scope. This sank Worthington's limited-area Articles 7–8 and part of Sturbridge's.
   - From Aug. 2026, conflict with the duty to accept consolidated local permit applications from Oct. 1, 2026 (Sturbridge, Lee, Gill, Brookfield).
   - Procedural defects under G.L. c. 40A, s. 5 (Southwick, Brookfield).
   - From Aug. 2026, *Sunpin* (SJC 2026): towns must provide reasonable opportunities for solar.
4. **Standalone-BESS bans are struck**: Wendell 2023, Spencer 2023, Medway (Tier 2), Pelham, Sherborn, Leyden, Wareham 2024, Hubbardston 2023 (in full) and Shutesbury 2023 (in full). The one exception is Oakham, Jan. 4, 2023, approved just before this line hardened.
5. **Herbicide, pesticide and fertilizer bans at solar or BESS sites are always struck.** They are preempted by the Pesticide Control Act, G.L. c. 132B (*Town of Wendell v. AG*, 1985). This is the most common partial strike: 16 of 33.
6. **Wrong vehicle.** A general (non-zoning) bylaw that licenses BESS regulates land use, so it must be adopted under zoning procedure (c. 40A, s. 5) and is subject to s. 3. This applied to Wendell and Shutesbury in 2024, and the Land Court affirmed Wendell in March 2026.
7. **Other provisions that get struck:**
   - visibility or "eliminate any view" rules (Petersham, Barre, Wareham, Norwell);
   - five-year deforestation look-backs and acreage caps (Wareham 2022, Boxborough, Falmouth, Carver, Westhampton at 1.5 acres);
   - caps on the number of installations (Spencer at 25, Shutesbury at one per sector, Pelham) and lot-size minimums tied to array size (Monson);
   - owner-funded responder training or equipment (Pelham, Petersham);
   - a $100M insurance requirement (Barre);
   - municipal-ownership requirements (Shrewsbury);
   - fiscal-impact denial tests (Uxbridge);
   - noise limits (Rochester);
   - a total earth-removal ban (Hadley 2024);
   - permit exemptions that conflict with state codes (Athol).
8. **What survives:**
   - size tiers, with district-by-district special permits and site plan review;
   - prohibitions in *some* districts while allowing other districts (Tewksbury, Millis, Carver, Northborough's ban on large solar in one new district);
   - an aquifer-district cap of 250 kWh (Whately);
   - setbacks, screening and decommissioning rules, if they are applied reasonably;
   - NFPA 855 and fire-code compliance;
   - third-party safety certification (Medway 2026);
   - an earth-removal limit to what is "incidental and necessary" (Hadley 2025);
   - a general stormwater bylaw that requires a permit for large solar (Acushnet 2025).

   Many approvals carry a warning that applying the bylaw to deny a project "would run a serious risk of violating" s. 3.
9. **Contrast with data centers.** The AG approved data-center moratoria in Shutesbury (#12047, Jan. 20, 2026), Templeton (#12294, Sept. 22, 2026) and Gill (Sept. 24, 2026), because data centers are not a protected use. The moratorium tool is legal; it fails for solar and BESS because of s. 3.

### Draft rules for "Will this bylaw survive AG review?"

| Pattern | Expected result | Basis (examples) |
|---|---|---|
| Moratorium on solar or BESS, any length or area | Disapproved (18 of 18 since June 2022) | s. 3; Zuckerman; Ch. 239 (Lee, Sturbridge) |
| Town-wide or standalone-BESS ban; cap above a size everywhere (5 MWh) | Disapproved | s. 3 (Wendell, Pelham, Worthington Art. 8) |
| Licensing or general bylaw for BESS | Disapproved | c. 40A, s. 5 (Wendell, Shutesbury) |
| Herbicide or pesticide ban at sites | Struck | c. 132B (16 letters) |
| View-elimination, owner-pays-for-training, $100M insurance, fiscal test | Struck | s. 3 (Barre, Petersham, Uxbridge) |
| Tiered BESS or solar zoning with districts and special permits | Approved | Wilbraham, Lunenburg, Hubbardston 2025 |
| Prohibition in sensitive districts only (aquifer, residential) | Usually approved | Whately, Tewksbury, Millis, Northborough |
| Consolidated local permit bylaw that tracks 225 CMR 29.00 | Approved | Medway 2026 |

## Court rulings (in JSON as `record_type: court_ruling`)

- ***Tracer Lane II Realty v. Waltham*, 489 Mass. 775 (SJC, June 2, 2022).** A near-total solar ban is impermissible; s. 3 requires balancing. This is the turning point for moratoria.
- ***NextSun Energy v. Fernandes*, Land Ct. 19 MISC 000230 (May 9 and June 23, 2023).** BESS gets the s. 3 solar protection. The municipality was not verified.
- ***Duxbury Energy Storage v. Duxbury ZBA*, Land Ct. 23 MISC 000643 (June 23, 2025).** A standalone BESS with no solar is protected, and the denial was annulled. The AG has cited it since Sept. 2025.
- ***Town of Wendell v. Campbell*, Land Ct. 25 MISC 000014 (March 2026, reported Mar. 16).** The AG's disapproval of Wendell's BESS licensing bylaw was upheld; the bylaw had to be zoning.
- ***Sunpin Energy Services v. Petersham ZBA*, 497 Mass. 794 (SJC-13860, July 14, 2026).** Denial of a protected solar project is allowed only where necessary for health, safety or welfare. The AG has cited it in every solar and BESS letter since Aug. 2026.

## Cities: not reviewed by the AG (context)

City ordinances are not submitted under G.L. c. 40, s. 32, so city moratoria stand unless challenged in court.

- **Westfield:** Section 5-31, a BESS interim prohibition through Sept. 30, 2026 (official text in JSON).
- **Fitchburg:** a proposed BESS moratorium, on the Oct. 6, 2026 council agenda.
- **Pittsfield:** BESS zoning recommended 5–0 for the Oct. 13, 2026 council meeting.
- **Leominster:** reportedly adopted a one-year BESS and data-center pause through July 31, 2027 (MassLive via Fire Engineering). No official text was found, so it is not in the JSON.

## Pending and gaps

- **Lee, Article 4 (Oct. 1, 2026 STM), Clean Energy zoning:** pending AG review; in JSON.
- **Whately, Article 24 (June 2026 ATM), BESS zoning:** no AG decision as of Oct. 10. It is not in the JSON because the only source is news.
- **Brookfield, Article 36:** on procedural hold since Oct. 5; its subject is unknown.
- **Duxbury:** its March 2026 BESS article has no AG decision; the July 14, 2026 letter covers only Articles 15 and 20, and the town-meeting outcome was not checked.
- **Correction to earlier notes:** Lee and Sturbridge are **not pending**. The AG disapproved them on Aug. 31 and Aug. 13, 2026. Hampden's Nov. 2024 moratorium, whose town-meeting outcome was earlier listed as unknown, passed and was disapproved on Mar. 11, 2025. `tracker.json` should be updated.
- **Bare approvals.** Some letters approve an article without describing it ("We approve Article 6"). Text search cannot classify those. Whately's 250 kWh cap was caught only by cross-checking news, so other clean-energy articles approved without comment may be missing. Moratoria are low-risk here, because every moratorium found drew a written analysis.
- **Unsubmitted moratoria.** Acushnet's 2022 180-day solar moratorium was never submitted, and the AG noted it "never had lawful effect." Moratoria that towns adopt but never submit cannot be counted.
- **Letter URLs.** These are portal-generated encrypted IDs. All rows resolved on Oct. 10, 2026, but the stable key is `case_number` plus `decision_date`. To re-find a letter, search that case number in the portal.
- **Recodifications.** Only the solar and BESS parts of whole-bylaw recodifications are coded (Tewksbury 2022, Falmouth, Erving, Southampton 2024, Westhampton, Billerica, Holden, Paxton). Unrelated disapprovals in those letters are ignored.

## Files

- `projects/351watch/data/ag_decisions.json`: the dataset. AG-row fields beyond the spec are `record_type`, `case_number` and `portal_document_name`.
- The scratchpad holds the build inputs: the portal index, 2,719 letter texts, and `ag/records.py` with `build_ag.py`. Re-running `build_ag.py` rebuilds the JSON. For a monthly refresh, query `KeywordSearch` by date and run the same text scan.
