# Massachusetts clean-energy moratorium tracker: source notes

Verified: 2026-10-10. Dataset: `projects/351watch/data/tracker.json` (10 framework entries, 24 town rows).

## Method

- About 55 web searches, plus direct downloads of primary documents: malegislature.gov bill pages and texts, Attorney General (AG) decision letters, town warrants, minutes and meeting packets, DOER and mass.gov PDFs, and court decisions.
- A row was included only when at least one source I opened during this session supports its status and date. When a source only reported a preview or a proposal, I used the last status that source confirms and wrote "latest found" in the summary.
- citizenportal.ai summaries showed up often in search results, but the site blocks automated fetches (Cloudflare 403). I could not read them, so I did not rely on them for any row (see Gaps).
- Link check on 2026-10-10. Of 54 unique source URLs, 51 returned HTTP 200 to curl. The other three opened during research but failed the final automated check:
  - Petersham AG decision (townofpetersham.gov): returns 403 to curl but opened through the fetch tool.
  - Yahoo/MassLive Leominster article: returned 429 (rate limit) on the final check; it opened earlier.
  - Amherst Article 18 PDF: intermittent connection resets; it returned 200 on two other attempts.
- Some sites (mass.gov `/doc/` downloads, gazettenet.com, recorder.com) return 403 or 429 to bursts of automated requests. Each of those links returned 200 or opened normally on at least one check.
- mass.gov "info-details" pages, such as the DOER Clean Energy Siting & Permitting hub, returned 403 to every automated fetch. I cited the underlying mass.gov `/doc/` PDFs instead.

## Framework entries

| Entry | How verified |
|---|---|
| Chapter 239 of the Acts of 2024 | Session-law page on malegislature.gov. Its text ends "Approved, November 20, 2024." The 25 MW / 100 MWh thresholds and the 12-month and 15-month clocks are confirmed in the 225 CMR 29.00 text and in the House bill summary for H.5641. |
| 225 CMR 29.00 | Final regulation PDF. § 29.05: towns may accept applications from July 1 to Sept. 30, 2026 and must accept them by Oct. 1, 2026. § 29.10(3): 12-month review. § 29.10(5)(b): constructive approval. § 29.10(3)(b): towns can request EFSB de novo review within 60 days. Promulgation date of Feb. 27, 2026 comes from the DOER model permitting bylaw and Foley Hoag (Mar. 11, 2026). |
| Oct. 1, 2026 guideline | The DOER Guideline on the Consolidated Local Permit Application is headed "Effective Date: Oct. 1, 2026" and lists the four required forms. |
| EFSB 980 CMR | Foley Hoag (Mar. 11, 2026) lists 980 CMR 13, 14 and 16 as published Feb. 27, 2026. I did not open the 980 CMR PDFs themselves. |
| DOER model permitting bylaw | PDF dated May 22, 2026. It states "Adoption of this Model Bylaw is not required." |
| DOER model solar and BESS zoning bylaws | Both final PDFs are dated "August 2026" with no day given, so `date` is blank. The October 2025 drafts are confirmed by the DOER webinar slides (Oct. 21, 2025; drafts posted Oct. 6). |
| AG stance on moratoria | Blandford decision (Mar. 11, 2026), footnote 2: earlier disapprovals of Northfield (Oct. 30, 2024, #11346), Ware (Mar. 15, 2023, #10725) and Carver (Nov. 14, 2022, #10526), plus bans on standalone BESS in Wareham, Leyden, Pelham, Spencer and Wendell. Becket and Worthington are added from their own rows. The approvals are the Wilbraham, Hadley and Petersham letters. |
| Duxbury Land Court | Climate Case Chart gives docket 23 MISC 000643 and a June 23, 2025 decision. The Wendell Land Court decision independently cites "Duxbury Energy Storage, LLC v. Town of Duxbury, 33 LCR 293 (June 23, 2025)." Sherin and Lodgen describes the holding. |
| Sunpin (SJC) | Foley Hoag (July 17, 2026): decided July 14, 2026. The Petersham AG letter cites it as 497 Mass. 794 (2026). |
| H.4690 | malegislature.gov bill history: accompanied a study order (H.5323) on Apr. 6, 2026. |

## Row-by-row verification

1. **Becket: bylaw moratorium, Disapproved by AG (June 22, 2026).** The House bill summary for H.5641 states the AG disapproved Article 4 of the Mar. 7, 2026 Special Town Meeting on June 22, 2026 and quotes the c. 40A § 3 reasoning. The town handout gives the Article 4 text and the Sept. 30, 2026 end date. I did not open the AG letter itself.
2. **Becket: H.5641, Pending at Legislature.** Bill history: referred Aug. 4, 2026; Senate concurred Aug. 6; hearing Sept. 21, 2026, written testimony only. The summary says the hearing window ran Sept. 21 to 28 and that Becket approved the petition as Article 5 (92 in favor, 109 present). The bill text gives six months and exempts residential BESS. No action after the hearing was listed.
3. **Worthington: three bylaw moratoria, Disapproved by AG (June 8, 2026).** The town STM page and warrant give the Article 6 to 8 terms: more than 600 kWh, through June 30, 2027, and a 5 MWh cap in Article 8. The town's auto-generated transcript (the town warns it may be inaccurate) records each article as "it passes." The Gazette (June 22, 2026) reports the AG letter of June 8, 2026 rejecting all three and approving Article 9, which is not a siting article. I did not open the AG letter.
4. **Worthington: H.5294, Rejected.** Bill history: referred Mar. 23, 2026; hearing Apr. 8; "accompanied a study order, see H5480" on June 8, 2026. H.5480 is the study order. *Judgment call:* the schema has no "sent to study" status. A study order is not a floor vote, but it usually ends a bill for the session, and labeling it "Pending" would mislead. I used **Rejected** and explained this in the summary.
5. **Lee: BESS moratorium, Adopted.** The town hearing notice (dated Mar. 30, 2026) sets the Apr. 27, 2026 Planning Board hearing on § 199-9.14 and a term from adoption through Nov. 14, 2026 or until BESS zoning is adopted. The Berkshire Eagle (May 16, 2026) reports voters approved "a moratorium on large-scale battery energy storage systems" at the annual town meeting. *Gaps:* I did not find the exact town meeting date or the vote count. `key_date` is the Nov. 14 end date instead. No AG decision was found. Because Lee adopted BESS zoning on Oct. 1, 2026, the moratorium may already have ended under its own "whichever comes first" clause once that zoning takes effect.
6. **Lee: Clean Energy zoning bylaw, Adopted (Oct. 1, 2026).** The Oct. 1 STM warrant contains Article 4 (new §§ 199-9.12.1 to .3, with BESS rules "based largely on" the DOER framework). The Berkshire Edge (Oct. 2, 2026) reports all articles passed and Article 4 passed unanimously. AG review is pending or not found.
7. **Sturbridge: BESS moratorium, Adopted (Apr. 27, 2026).** The town's Apr. 27, 2026 meeting packet includes the STM warrant and minutes: Article 63, "Passed 118/13," a 2/3 vote; definition of 250 kWh or more; ends Dec. 1, 2026. The Planning Board agenda for Dec. 1, 2025 lists "Proposed Moratorium Battery Energy Storage Systems." The old sturbridge.gov/node/171911 page from earlier research now returns 404. No AG decision was found.
8. **Sutton: consolidated permit, In effect (Oct. 1, 2026).** Town news flash (July 2, 2026) and the town DOER page. *Judgment call:* "In effect" means only that the town said it would accept applications from Oct. 1. As of July the town was still choosing between a local bylaw and the DOER model rules, and I found no later update. The earlier research note that Sutton "adopted DOER model rules" is **not** supported by these sources.
9. **Blandford: Disapproved by AG (Mar. 11, 2026).** I read the AG decision PDF (Case #12153): Article 1 of the Nov. 17, 2025 STM, running through May 31, 2026. Foley Hoag and the State Impact Center confirm it.
10. **Northfield: Disapproved by AG (Oct. 30, 2024).** I read the AG decision PDF (Case #11346): Articles 26 and 27 of the May 6, 2024 ATM. Both moratoria were disapproved; the BESS definition was approved.
11. **Wendell: Disapproved by AG (Nov. 14, 2024).** The Land Court memorandum (25 MISC 000014) records the May 1, 2024 town meeting and the Nov. 14, 2024 AG decision, and affirms the AG. The PDF was created Mar. 12, 2026; the decision's own date line was not readable. The Athol Daily News gives the 100 to 1 vote. *Judgment call:* Wendell adopted this as a *general* (licensing) bylaw, not a zoning bylaw. The schema has no "general bylaw" action, so the row uses "Zoning bylaw" and the summary states what it was. The AG and the court both found it was zoning in substance.
12. **Wilbraham: Approved by AG (Sept. 5, 2024).** I read the AG decision PDF (Case #11474), Article 32 of the June 3, 2024 ATM.
13. **Hadley: Approved by AG (Nov. 12, 2024).** I read the AG decision PDF (Case #11355, copy hosted by Worthington), Article 23 of the May 2, 2024 ATM. The earth-removal clause in § 28.5.4.3.9 was disapproved.
14. **Petersham: Approved by AG (Aug. 13, 2026).** I read the AG decision PDF (Case #12175), Articles 3 to 8 of the Dec. 8, 2025 STM. §§ 18.8(f)(4) and 18.9(5) were partly disapproved. The articles had been placed on a "299 hold" on Apr. 3, 2026; Article 9 was approved separately on May 12, 2026.
15. **Westfield: interim BESS restriction, Adopted.** Ordinance § 5-31 on the city website, footer dated 2/26/26, ends "until, and through, September 30, 2026." Planning Board minutes (Feb. 3, 2026) and the Council hearing notice (Feb. 5, 2026) confirm it. *Judgment call:* I used **Adopted**, not "Expired." By its terms it lapsed Sept. 30, 2026, but I could not confirm whether the council extended it or adopted permanent rules, so the expiry is given as `key_date`. Westfield is a city, so the AG does not review its ordinances.
16. **Leominster: Adopted.** MassLive via Yahoo (Tue., Sept. 29, 2026) says the council voted 8 to 0 "on Monday" and the moratoria are "in effect until July 31, 2027." `key_date` 2026-09-28 is *inferred* as the Monday before publication.
17. **Chicopee: BESS ordinance, Proposed.** The Reminder (Sept. 17, 2026) covers the Laflamme amendment: first discussed Aug. 4, referred to committees, with steps still remaining as of Sept. 15.
18. **Hampden: Proposed.** The Reminder (June 19, 2024) reports the May 13, 2024 ATM took no action on a moratorium. The Reminder (Aug. 21, 2024) reports the Planning Board recommended a six-month moratorium for the Oct. 29, 2024 Town Meeting. I found no outcome. Planning Board minutes (May 12, 2025) mention a report "submitted with the proposed BESS Bylaw to the Attorney General," which suggests a permanent bylaw was later pursued. I did not make a row for it because I lacked details.
19. **Whately: Adopted.** Recorder (May 29, 2026): Article 24, based on the DOER model, with Tier 2 and Tier 3 bans in the aquifer district and within 300 ft of wells. Recorder (June 4, 2026): voters "passed a new section of the town's zoning bylaw that specifically regulates battery energy storage systems." Recorder (Nov. 13, 2025): Nov. 12, 2025 STM Article 6 set a 250 kWh cap in the aquifer district. `key_date` 2026-06-02 is *inferred* from "Tuesday." No vote count or AG decision was found.
20. **Harvard: Proposed.** Planning Board memo dated July 28, 2026 says the hearing was set for Aug. 17, 2026. I did not confirm whether the hearing was held or what happened at town meeting.
21. **Amherst: Proposed.** The Article 18 draft PDF is headed "recommended by CRC after First Reading – 2026-09-10." Final Town Council action was not found.
22. **Plainfield: Withdrawn.** Gazette (Nov. 13, 2025): the Select Board took "no action" on Article 3 at the Nov. 12, 2025 STM. Gazette (Oct. 27, 2025): the Planning Board voted unanimously for a six-month solar moratorium. *Judgment call:* "no action" is recorded as **Withdrawn**. Whether a moratorium went to the 2026 annual town meeting was not found.
23. **Hatfield: Proposed.** Gazette (Jan. 12, 2026): Planning Board discussion on Jan. 7, 2026. The article says a May 2026 vote was "unlikely." No outcome was found.
24. **Duxbury: Proposed.** Town draft dated Dec. 30, 2025, "To Be Considered at March 2026 Annual Town Meeting," which would prohibit BESS in about 90% of town. I found no outcome. A search summary of June 2026 subcommittee minutes said the bylaw was still in draft, but I could not open that page (403), so it is not cited.

## Conflicts found

- **Climate Act signing date.** Sutton's page says Nov. 21, 2024. The session law says "Approved, November 20, 2024." I used Nov. 20 (primary source).
- **Becket moratorium length.** The town bylaw (Article 4) ran through Sept. 30, 2026. The separate special act (H.5641) proposes six months from passage. These are different instruments and both are correct.
- **Becket hearing date.** The bill page lists a Sept. 21, 2026 written-testimony hearing. The bill summary lists Sept. 21 to 28, 2026. I used Sept. 21.
- **Sturbridge town meeting date.** The Town Minute guide (independent) lists a June 1, 2026 business meeting. Town records show the ATM and STM were held Apr. 27, 2026. I used the town records.
- **Lee town meeting date.** Berkshire Edge (Apr. 13, 2026) mentions both "May 8" and a "May 18" warrant. The Eagle results story ran May 16, 2026. I left the exact date out.
- **Lee "executive order" claim.** Berkshire Edge (Sept. 17, 2026) says a March executive order from Gov. Healey requires towns to adopt BESS bylaws. I did not verify this, and it conflicts with DOER's statement that adopting the model bylaw is not required. I did not use it.
- **225 CMR 29.00 timing in secondary sources.** A Nutter advisory (June 2026) reportedly said the rules took effect July 1, 2026 and called them finalized "February 2025." The regulation itself has a July 1 optional start and an Oct. 1 mandatory start, and DOER says it was promulgated Feb. 27, 2026. I used the regulation's text.
- **Carver.** Earlier leads tied Carver to recent moratorium disapprovals. The Carver moratorium decision is from Nov. 14, 2022, which is outside 2024 to 2026, so there is no Carver row. The town-hosted PDF of that decision now returns 404. An archived copy exists at web.archive.org.

## Gaps and leads not included

These are leads I could not source or could not read:

- **Chicopee moratorium vote.** Search snippets from citizenportal.ai say the council defeated an immediate BESS moratorium 1 to 11 on Aug. 4, 2026. The page blocks fetches and no other outlet confirmed it, so it was left out. Only the separate ordinance proposal is listed.
- **Templeton.** citizenportal.ai snippets say town meeting adopted a data-center moratorium, but a battery-storage moratorium (Article 39) failed to reach two-thirds. Not verified.
- **Shelburne.** A Recorder headline says "Shelburne voters give blessing to bylaws on short-term rentals, battery energy storage." The page returned 503 or reset each time, so the date and details are unverified.
- **Chesterfield.** A town notice of an Aug. 27, 2026 Planning Board hearing on a BESS zoning bylaw could not be fetched (Cloudflare 403).
- **Bernardston** (July 2026 draft bylaw, 403), **Westhampton** (Mar. 3, 2026 first reading, agenda only), **Uxbridge** (STM BESS bylaw, citizenportal only), **Ayer** (citizenportal only): not included.
- **Towns named in the brief with nothing relevant found for 2024 to 2026:** Medway (its BESS moratorium ran Nov. 2021 to June 30, 2023, outside the range), Carver (2022 decision, see above; a June 4, 2024 citizen-petition "battery safety bylaw" was mentioned, outcome not found), Hanover, Wakefield, Sudbury, Leicester, Fall River, Plymouth (Apr. 11, 2026 ATM "motions as voted" contains only municipal solar-lease articles), Middleborough, Holliston, Westford, Charlton, Ludlow, Buckland, Shirley, Townsend. These were not exhaustively searched, so absence here does not mean no action.
- **AG decisions still pending or not found:** Lee (moratorium and Oct. 1 bylaw), Sturbridge, Whately (2025 and 2026), Hampden. The AG generally has 90 days from submission, extendable by 90 days, so Lee and Sturbridge decisions may be issued soon. I could not search the AG's own decision portal directly, so AG decisions came from town-posted letters and news coverage.
- **State project overrides** such as the EFSB Tewksbury battery project decision (June 30, 2026) are state actions, not town actions, and were not included.

## Suggested follow-ups after launch

1. Check the AG's decisions for Sturbridge (Article 63) and Lee (§ 199-9.14 and the Oct. 1 Article 4). Based on precedent, both moratoria are likely to be disapproved.
2. Confirm whether Westfield extended its interim restriction past Sept. 30, 2026 or adopted permanent BESS zoning.
3. Watch H.5641 (Becket) for a committee report.
4. Confirm the outcomes for Hampden (Oct. 29, 2024), Duxbury (March 2026), Harvard (fall 2026), Hatfield, Plainfield (2026 ATM) and Amherst (Town Council).
5. Find a non-citizenportal source for the Chicopee and Templeton votes and a readable copy of the Shelburne article.
