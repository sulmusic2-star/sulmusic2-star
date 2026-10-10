# Massachusetts-Specific Compliance SaaS / Document Kits That Software Can Deliver End to End

Research date: October 10, 2026. Scope: small-business and landlord compliance products driven by Massachusetts rules, proven as paid self-serve products elsewhere, deliverable with no licensed professional and no per-customer manual work (AI coding agent builds and runs it; customers self-serve; Stripe bills). "Verified" means a cited source states it; "Inference" means my reasoning; "Gap" means not found or not reliable. Note: mass.gov pages returned HTTP 403 to direct fetches during this session, so several mass.gov facts come from search-result extracts of mass.gov documents rather than full-page reads. Census API now requires a key, so Census County Business Patterns counts could not be pulled directly.

## Q1. Ranked shortlist: which 4–6 MA compliance products are worth building?

### Takeaway
The strongest software-only opportunity is a Massachusetts 201 CMR 17.00 WISP generator with an annual-review subscription (broadest legal driver, real AG enforcement, proven $249–$499 one-time and ~$119/yr subscription price points, low UPL risk). Second is a small-landlord security-deposit and move-in compliance kit (treble-damages exposure, MA-only rules that national landlord apps do not visibly handle). Next come an MA employer notice/acknowledgment tracker (PFML, Earned Sick Time, pay transparency), a home-improvement-contractor (c. 142A) contract and compliance kit, an Open Meeting Law minutes drafter for small-town boards, and allergen-awareness training (possible since DPH's October 2024 rule change, but cheap and already contested). Discard LLC annual-report reminders (crowded, low value) and noncompete document generation (UPL risk, low volume). The Massachusetts Data Privacy Act is a watch item, not a driver: as of October 10, 2026 it remains in conference committee.

### Cited Findings
- 201 CMR 17.00 requires "every person that owns or licenses personal information" about a Massachusetts resident to develop, implement and maintain a comprehensive WISP, and it is not limited to entities domiciled in Massachusetts — [mass.gov regulation text](https://www.mass.gov/doc/201-cmr-1700-standards-for-the-protection-of-personal-information-of-residents-of-the-0/download); [Boston Bar Journal](https://bostonbar.org/journal/the-importance-of-written-information-security-policies-in-data-governance/)
- Massachusetts security deposit violations (c. 186 §15B(7)) carry liability of three times the deposit, plus 5% interest, court costs and reasonable attorney fees — [iPropertyManagement](https://ipropertymanagement.com/laws/massachusetts-security-deposit); [Tellus](https://resources.tellusapp.com/landlords/massachusetts/security-deposits/massachusetts-security-deposit-laws-for-landlords)
- TurboTenant's pricing page advertises "state-specific" leases and a $199 Landlord Forms Pack, but does not describe Massachusetts-specific security deposit handling — [TurboTenant pricing](https://www.turbotenant.com/pricing/)
- Massachusetts Data Privacy Act (S.2619): passed Senate 40–0 on 9/25/2025; House substituted H5472 text and passed it 146–0 as H5479 on 6/4/2026; Senate non-concurred and appointed conferees 6/11/2026; House appointed conferees 6/17/2026; no later action listed when read on 10/10/2026 — [malegislature.gov bill history](https://malegislature.gov/Bills/194/S2619/BillHistory)

### Inferences
- Suggested ranking (my judgment from the evidence in Q2–Q8):
  1. **MA WISP generator + annual review subscription** (201 CMR 17.00, with c. 93H breach-response module). Broadest market, clear enforcement, low UPL risk, highly automatable.
  2. **MA small-landlord deposit and move-in compliance kit** (c. 186 §15B receipts, statement of condition, interest calendar, lead-law form delivery tracking, broker-fee disclosure). High penalty pain, MA-only rules, clear gap in national tools.
  3. **MA employer notice and acknowledgment tracker** (PFML new-hire notice + signed acknowledgment, annual rate notices, Earned Sick Time policy and poster, pay-range posting checker for 25+ employers). Real requirements, but crowded by payroll/HRIS vendors; best aimed at 1–50 employee firms not on a full HRIS.
  4. **HIC contract and compliance kit** (c. 142A required contract terms, registration-number fields, deadlines). MA-specific, recurring per job, but the state publishes a free sample contract and UPL risk is moderate.
  5. **Open Meeting Law minutes drafter for small-town boards and committees** (AG minutes checklist compliance). Feasible and MA-specific; buyers are municipalities, with procurement friction.
  6. **Allergen-awareness training + Person-in-Charge training log** (105 CMR 590). Automatable since DPH stopped approving specific courses on Oct 7, 2024, but low price (historically $10) and accredited competitors.
- Discard: LLC/corporation annual report reminders (state filing is simple; registered-agent firms bundle it); noncompete generator (UPL, low frequency). Watch: MA Data Privacy Act (could create a privacy-notice/data-map product if enacted).

### Gaps
- No primary-source count of MA employer firms, landlords, food establishments or HIC registrants could be pulled directly (Census API key required; mass.gov blocked). See Q8.

## Q2. WISP generator for 201 CMR 17.00 (MA data security regulation)

### Takeaway
Every business holding MA residents' personal information (which includes any MA employer holding employee SSNs) must keep a WISP. The AG has enforced it through Assurances of Discontinuance with civil penalties and required WISPs. Over 2,000 breaches a year are reported to the state. The only free government template is the IRS one, built for tax pros. Paid WISP products are proven at $249–$499 one-time (Verito) and auto-updating policy subscriptions are proven at $119/yr (Termageddon, privacy policies). A Massachusetts-specific self-serve WISP builder with annual-review reminders, employee training attestations, a vendor log and an MA breach-notice workflow fits software-only delivery well.

### Cited Findings
**Legal driver**
- 201 CMR 17.00 applies to every person that owns or licenses personal information about a MA resident and requires a comprehensive WISP; applies regardless of where the business is headquartered — [mass.gov 201 CMR 17.00 text](https://www.mass.gov/doc/201-cmr-1700-standards-for-the-protection-of-personal-information-of-residents-of-the-0/download); [Boston Bar Journal](https://bostonbar.org/journal/the-importance-of-written-information-security-policies-in-data-governance/)
- Required WISP elements include a designated coordinator, risk assessment, employee training, third-party vendor oversight, regular monitoring, at-least-annual review, and documentation of breach responses; the safeguards should fit the business's size, scope, resources, amount of stored data and need for confidentiality (vendor summary, last reviewed May 2026) — [D3RX 201 CMR 17 guide](https://d3rx.com/compliance-guides/massachusetts-201-cmr-17-healthcare); [D3RX MA page](https://d3rx.com/states/ma)
- The regulation took effect in 2010 (it postdated the Briar Group breach; the AG still cited it as a reference point) — [Proskauer, 2011](https://privacylaw.proskauer.com/2011/04/articles/data-breaches/bay-state-brings-it-attorney-general-enters-consent-agreement-with-restaurant-group-for-data-security-failures/)

**Enforcement and penalties**
- Belmont Savings Bank: Assurance of Discontinuance with a $7,500 civil penalty plus new security and training procedures after a 2011 backup-tape incident; commentary says the AG's position is that having a WISP alone is insufficient (secondary source) — [Brainlink](https://brainlink.com/?p=1877)
- TradeSource (2022 AOD): must maintain a WISP compliant with 201 CMR 17.03–17.04, provide the WISP to the AG within 90 days, obtain a third-party security assessment within 180 days, act on and report findings; obligations run three years — [mass.gov TradeSource AOD](https://www.mass.gov/doc/tradesource-final-aod/download)
- Briar Group (restaurant group, 2011 consent judgment): complaint cited default POS passwords, shared employee passwords, excess admin access and clear-text card data — [Proskauer](https://privacylaw.proskauer.com/2011/04/articles/data-breaches/bay-state-brings-it-attorney-general-enters-consent-agreement-with-restaurant-group-for-data-security-failures/)
- 2012 settlement over a stolen laptop with unencrypted personal information, based on the Consumer Protection Act (c. 93A) plus 201 CMR 17.00, focused on encryption — [Proskauer, 2012](https://privacylaw.proskauer.com/2012/04/articles/data-breaches/massachusetts-ago-stresses-the-importance-of-encryption/)
- Breach volume: the mass.gov summary lists 2,292 breaches reported to OCABR in 2024 affecting 4,448,136 MA residents. Conflict: an older version of the table lists 229 breaches for 2024, and the 2024 PDF header shows 4,488,136 residents — [mass.gov Data Breach Reports](https://www.mass.gov/lists/data-breach-reports); [Data Breach Report 2024](https://www.mass.gov/doc/data-breach-report-2024)

**Proven comparables and pricing**
- IRS Publication 5708: a free, 28-page WISP template for tax professionals, updated by the IRS/Security Summit; IRS reminded tax pros of the WISP requirement in July 2025 — [CPA Practice Advisor 2025](https://www.cpapracticeadvisor.com/2025/07/29/irs-reminds-tax-pros-of-requirement-for-a-written-security-plan-wisp/165822/); [CPA Practice Advisor](https://www.cpapracticeadvisor.com/?p=109001)
- FTC Safeguards Rule (GLBA) drives the tax-pro WISP market: MFA required since June 9, 2023; security events affecting 500+ people reportable to the FTC since May 13, 2024 — [The Tax Adviser, Aug 2024](https://www.thetaxadviser.com/issues/2024/aug/protecting-taxpayer-data-and-where-to-even-begin/)
- Verito sells a WISP at a flat per-firm fee: $499 one-time, promoted at $249 (half off), with a "guided" option delivering an implemented plan in five business days — [Verito buy WISP](https://www.verito.com/buy-written-information-security-plan); [Verito WISP](https://verito.com/wisp)
- Ace Cloud Hosting sells a customized WISP-creation service for CPA/tax firms (price not shown) — [Ace Cloud Hosting](https://www.acecloudhosting.com/written-information-security-plan/)
- Many WISP templates are free lead magnets: TaxDome, Financial Cents, CountingWorks PRO (gated) — [TaxDome](https://taxdome.com/blog/free-wisp-template); [Financial Cents](https://financial-cents.com/resources/checklist-templates/wisp-template/); [CountingWorks PRO](https://info.countingworkspro.com/free-wisp-template)
- WISP CPE courses ("A WISP Away") sell at $79 member / $109 non-member across state CPA societies — [WICPA](https://www.wicpa.org/cpe/157932imp:a-wisp-away); [FICPA](https://www.ficpa.org/cpe/599107imp:acpen-a-wisp-away)
- Proven subscription model for auto-updating compliance documents: Termageddon charges $12/month or $119/year per website for privacy policy, T&C, disclaimer, EULA, cookie policy and consent, with "Automatic Updates & Email Notifications" as laws change — [Termageddon pricing](https://termageddon.com/pricing/)

**Pending law that could expand the product**
- Massachusetts Data Privacy Act: S.2619 passed the Senate 40–0 (9/25/2025); House passed H5479 146–0 (6/4/2026); conference committee appointed (Senate 6/11/2026; House 6/17/2026); no enactment shown as of 10/10/2026 — [malegislature.gov](https://malegislature.gov/Bills/194/S2619/BillHistory)
- S.2619 provided exclusive AG enforcement with no private right of action; the chambers differ mainly on enforcement and the private right of action — [Mondaq comparison](https://www.mondaq.com/unitedstates/privacy-protection/1805522/one-step-closer-to-a-massachusetts-data-privacy-law-comparing-the-current-house-and-senate-bills)
- LegiScan labels the 194th General Court "Adjourned Sine Die" — [LegiScan](https://legiscan.com/MA/C/). (Conflict: FastDemocracy shows a "Became Law" label while its last action is the 6/11 conferee appointment; the official bill history does not support enactment — [FastDemocracy](https://fastdemocracy.com/bill/ma/194th/bills/MAB00082326/).)

### Inferences
- Market: every MA employer firm holds employee PI (SSNs, bank account numbers for direct deposit), so the addressable base is at least all MA employer firms (roughly 126k by an unverified third-party figure; see Q8), plus out-of-state businesses serving MA residents. In practice the reachable buyers are businesses that get prompted: tax preparers and bookkeepers (IRS/FTC), MA insurance agents, medical/dental offices, property managers, payroll-holding small firms, and firms whose cyber-insurance applications ask for a WISP.
- Product shape (fully automatable): questionnaire → MA-tailored WISP (201 CMR 17.03–17.04 elements, including encryption of laptops/portable devices and transmitted data) → e-signed coordinator designation → employee training video + quiz + attestation log → vendor-contract checklist → annual review reminder and re-generation → incident log and MA breach-notice letter templates (AG + OCABR) → dual-mode "IRS 5708 + FTC Safeguards + 201 CMR 17" for tax pros. Price anchor: $149–$299 first year, $99–$149/yr renewal; or $19–$29/month with training seats.
- Differentiation: national tax-pro WISP templates are built around IRS/FTC rules, not 201 CMR 17's specific computer-system requirements and the AG's "WISP is necessary but not sufficient" stance. The annual-review and training attestation trail is what the AG asked of TradeSource and Belmont, so a record-keeping subscription beats a one-time PDF.
- UPL risk: low. A WISP is an internal security policy, not a legal instrument. Avoid "guaranteed compliant" claims; present it as a template/tool, not legal advice.
- If the Data Privacy Act is enacted in a later session, the same customer base would need privacy notices and data-subject request workflows; Termageddon-style auto-updates would become a natural upsell.

### Gaps
- Could not read the AG's own free small-business WISP guide or compliance checklist (mass.gov blocked); a free state template likely exists and would be the main "free competitor." Verify before launch.
- No MA-specific paid WISP SaaS found in searches (only national tax-pro products and healthcare vendor guides like D3RX); not proof none exists.
- Exact number and size of AG 201 CMR 17 penalties in 2024–2026 not found; enforcement examples found are 2011–2022.
- Whether the conference committee could still report the Data Privacy Act after formal sessions ended is not confirmed.

## Q3. Landlord compliance kit for MA small landlords (1–4 units)

### Takeaway
Massachusetts has some of the strictest small-landlord paperwork rules in the U.S.: deposits must sit in a separate interest-bearing MA bank account, landlords must give receipts and a statement of condition on deadlines, pay annual interest, and give the unaltered Tenant Lead Law Notification for pre-1978 housing. Breaking the deposit rules risks treble damages plus fees, and since August 1, 2025 broker fees follow whoever hired the broker. National landlord apps (TurboTenant at $149–$199/yr, Avail) publish MA law explainers but do not visibly automate MA deposit compliance; MassLandlords sells forms through membership. A deadline-driven "MA deposit and move-in compliance" app is a credible software-only product.

### Cited Findings
**Legal drivers**
- Security deposits (M.G.L. c. 186 §15B): deposit held in a separate, interest-bearing account in a bank located in Massachusetts; no commingling; receipt within 30 days naming bank and location, amount and account number — [Avail MA landlord-tenant law](https://www.avail.com/education/laws/massachusetts-landlord-tenant-law); [MassLandlords security deposit basics](https://masslandlords.net/laws/security-deposits/basics/)
- Conflict on receipt timing: EZ Landlord Forms says 10 days of receipt or start of tenancy (whichever later); MassLandlords and Avail say 30 days — [EZ Landlord Forms](https://www.ezlandlordforms.com/documents/massachusetts-security-deposit-followup-statement-802762/); [MassLandlords](https://masslandlords.net/laws/security-deposits/basics/)
- Statement of Condition due within 10 days of move-in; without it the landlord cannot deduct for pre-existing conditions; tenants can make their own (MassLegalHelp provides a form) — [MassLegalHelp Security Deposits 2025](https://www.masslegalhelp.org/sites/default/files/2025-02/03%20Security%20Deposits%202025.pdf); [Tellus](https://resources.tellusapp.com/landlords/massachusetts/security-deposits/massachusetts-security-deposit-laws-for-landlords)
- Interest owed annually at the lower of the bank's rate or 5% — [Tellus](https://resources.tellusapp.com/landlords/massachusetts/security-deposits/massachusetts-security-deposit-laws-for-landlords)
- Penalty: treble damages (3x deposit) plus 5% interest, court costs and attorney fees under §15B(7); failure to give the receipt lets the tenant recover the deposit immediately — [iPropertyManagement](https://ipropertymanagement.com/laws/massachusetts-security-deposit); [iPropertyManagement returns](https://ipropertymanagement.com/laws/massachusetts-security-deposit-returns)
- Before a tenancy, landlords may collect only first month, last month, security deposit, and lock-change cost — [MassLandlords](https://masslandlords.net/forcing-tenants-to-pay-brokers-fees-is-already-illegal-no-new-legislation-needed/)
- Broker fee law: effective August 1, 2025 per the AG advisory (one MassLandlords post gives a July 4, 2025 enactment date); the party that hires the broker pays; tenants owe a fee only if they retained the broker in writing; report violations to the AG Consumer Hotline (617) 727-8400 — [AG Broker Fee Advisory](https://www.mass.gov/doc/broker-fee-advisory/download); [Cambridge Housing Liaison](https://www.cambridgema.gov/Departments/officeofthehousingliaison/brokersfees); [Mass Legal Services](https://www.masslegalservices.org/content/tenants-rights-regarding-broker-fees); [RentWise Boston disclosure](https://www.rentwiseboston.com/massachusetts-broker-fee-disclosure)
- Lead law (105 CMR 460.725; M.G.L. c. 111 §§189A–199B): before signing, owners renting pre-1978 housing must give two copies of the Tenant Lead Law Notification and Tenant Certification Form plus any lead inspection/risk assessment report and any Letter of Compliance/Interim Control; the form's wording may not be amended, rearranged or reduced in type size; applies whether or not a child under 6 lives there — [105 CMR 460.725 (Justia)](https://regulations.justia.com/states/massachusetts/105-cmr/title-105-cmr-460-000/initial-inspection-reinspection-and-enforcement-procedures/section-460-725); [mass.gov Tenant Lead Law Notification](https://www.mass.gov/info-details/tenant-lead-law-notification)
- Lead penalties: state civil penalty (amount not stated on mass.gov page) plus federal civil and criminal penalties; EPA reportedly fined one Boston landlord $84,600 for 14 paperwork violations (secondary) — [mass.gov](https://www.mass.gov/info-details/tenant-lead-law-notification); [MassLandlords](https://masslandlords.net/epa-slaps-hefty-fines-for-not-giving-lead-paint-disclosures/)
- State Sanitary Code (105 CMR 410): last major amendments effective May 12, 2023 (mold/moisture, heating season, mandatory equipment, lighting, accessibility); no 2025 amendment to 105 CMR 410 found; DPU opened D.P.U. 25-150 on May 30, 2025 to realign 220 CMR 29.00 utility-billing rules with the revised code — [mass.gov Housing Code](https://www.mass.gov/info-details/housing-code-effective-april-2023); [Essex MA](https://www.essexma.org/node/63206); [DPU 25-150 notice](https://www.mass.gov/doc/25-150-notice/download)

**Market size**
- About 57% of MA homes are single-family, 20% are in 2–4 unit buildings, 22% in larger multifamily; multifamily housing is over 75% renter-occupied — [mass.gov housing supply overview](https://www.mass.gov/info-details/supply-overview-for-massachusetts-housing-stock)
- Small Property Owners Association claims small owners supply more than 65% of MA rental housing (advocacy claim, method not shown) — [New Bedford Light](https://newbedfordlight.org/small-landlords-push-back-against-massachusetts-rent-control-ballot-proposal/)
- MassLandlords: about 2,600 members owning more than 72,000 units; average 16 units, median 6 — [MassLandlords](https://masslandlords.net/massachusetts-landlord-association/)
- A rent control ballot proposal exempting owner-occupied buildings of four or fewer units is in play in 2026 — [New Bedford Light](https://newbedfordlight.org/small-landlords-push-back-against-massachusetts-rent-control-ballot-proposal/); [Dorchester Reporter, May 2026](https://www.dotnews.com/2026/05/22/small-landlords-air-their-case-vs-rent-control-in-state-house-setting/); [Greenfield Recorder](https://recorder.com/2025/12/26/rent-increase-caps-impact/)

**Competition and pricing**
- TurboTenant: Free plan; Essentials $149/yr and Pro $199/yr for 1–10 units ($12.42 and $16.48/month); Landlord Forms Pack $199 on Free plan; no MA deposit-specific features described — [TurboTenant pricing](https://www.turbotenant.com/pricing/)
- TurboTenant's MA receipt page treats receipts as required only for deposits/last month's rent and lists amount, date, tenant name and purpose, omitting the bank details MA law requires — [TurboTenant MA rent receipt](https://www.turbotenant.com/rent-collection/rent-receipt/massachusetts/)
- Avail publishes MA law explainers (separate MA bank account, 30-day receipt) — [Avail](https://www.avail.com/education/articles/massachusetts-landlord-tenant-laws-the-top-8-laws-to-know)
- EZ Landlord Forms sells a Massachusetts Security Deposit Follow-up Statement (updated 11/20/2023) — [EZ Landlord Forms](https://www.ezlandlordforms.com/documents/massachusetts-security-deposit-followup-statement-802762/); [support article](https://support.ezlandlordforms.com/support/solutions/articles/72000616906-massachusetts-security-deposit-follow-up-statement-11-20-2023-)
- MassLandlords offers 50+ rental forms (including a security deposit receipt) to members for "affordable monthly dues"; the price is not on the join page — [MassLandlords join](https://masslandlords.net/join/); [MassLandlords forms](https://masslandlords.net/?p=41797)
- Free state/legal-aid resources: mass.gov security deposit law page; MassLegalHelp statement of condition form; mass.gov lead notification form — [mass.gov](https://mass.gov/info-details/massachusetts-law-about-tenants-security-deposits); [MassLegalHelp](https://www.masslegalhelp.org/sites/default/files/2025-02/03%20Security%20Deposits%202025.pdf)

### Inferences
- Product shape: (1) deposit intake: generate the at-signing receipt and the 30-day bank receipt with required fields, with timers; (2) photo-based Statement of Condition with tenant e-sign and the 15-day tenant-response window tracked; (3) annual interest calculator (lower of bank rate or 5%), anniversary reminders, and interest statements, also for last month's rent; (4) lead-law packet: serve the official unaltered mass.gov form and collect signed certification (avoid re-typesetting it); (5) broker-fee disclosure and "who hired the broker" record; (6) move-out deduction itemization within 30 days with receipts. Price anchor: $49–$99 per unit-year or $99–$199/yr per landlord (in line with TurboTenant tiers), or a one-time $49–$79 move-in kit.
- The "bank located in Massachusetts" rule likely rules out national fintech escrow features, which helps explain why national apps don't automate MA deposits. (Inference; not verified for any specific vendor.)
- UPL risk: low for receipts, statements of condition, interest math and delivery tracking, which are statutory ministerial records. It is higher for leases, notices to quit and deduction disputes; stay with fill-in of statutory forms and timers, and exclude eviction notices.
- If the 2026 rent control ballot measure passes, it would create a new rent-increase compliance need for non-exempt landlords, but owner-occupied 1–4 unit buildings would be exempt.

### Gaps
- No count of MA landlords who own 1–4 units (ACS B25032 renter units by structure could not be pulled; no DOR Schedule E count found).
- MA lead-law civil penalty amount not confirmed (check c. 111 §197A).
- Exact statutory receipt deadlines conflict across secondary sources; verify against the §15B text before building timers. (My unverified understanding is that §15B requires two receipts, one at payment and a bank receipt within 30 days.)
- Did not verify whether Avail, RentRedi or Landlord Studio automate MA deposit interest or receipts; their pricing pages were not checked.
- Outcome and date of the 2026 rent control ballot vote not confirmed.

## Q4. Employer compliance for MA small businesses (Earned Sick Time, PFML, Wage Act, pay transparency, noncompetes)

### Takeaway
MA employers face several concrete, document-heavy duties: PFML new-hire notices with signed acknowledgments within 30 days, annual rate notices and posters; Earned Sick Time posting and policy; pay ranges in job postings (25+ employees since Oct 29, 2025) and EEO data reports (100+ employees, Feb 1 annually). Penalties are real (pay transparency fines up to $25,000 after warnings; PFML notice fines of $50/$300 per employee per 2019 alerts; treble damages under sick-time and Wage Act claims). But payroll/HRIS vendors (Gusto, etc.) and many law-firm alerts cover this ground. The gap is a cheap MA-only "notices and acknowledgments" tracker for very small employers not on a full HRIS. A noncompete generator should be discarded (UPL).

### Cited Findings
**Pay transparency (Frances Perkins Workplace Equity Act, G.L. c. 149 §105E; signed July 31, 2024)**
- Employers with 25+ employees must include pay ranges in job postings (effective October 29, 2025) and provide ranges to employees on request and for promotions/transfers; bonuses, commissions and benefits not required — [mass.gov](https://www.mass.gov/info-details/pay-transparency-in-massachusetts); [Mercer](https://www.mercer.com/insights/law-and-policy/massachusetts-to-require-salary-disclosures-wage-data-reporting); [OneDigital](https://www.onedigital.com/blog/massachusetts-pay-transparency-october2025/)
- Employers with 100+ employees must file annual EEO demographic and pay data reports by February 1 (first due Feb 1, 2025); a federal EEO-1 filing can satisfy it; individual filings are not public; the state publishes aggregate data — [Nilan Johnson](https://nilanjohnson.com/massachusetts-pay-transparency-law-takes-effect-in-october/); [Fisher Phillips](https://www.fisherphillips.com/en/news-insights/pay-transparency-coming-to-massachusetts-in-2025.html)
- Penalties: warning, then up to $500, then up to $1,000, then up to $25,000 for 4th and subsequent offenses; an "offense" is all postings by the same employer within 48 hours; AG enforces exclusively; no private right of action — [Choate](https://www.choate.com/insights/massachusetts-pay-transparency-requirements-take-effect-on-october-29-2025/?output=pdf); [Seyfarth](https://www.seyfarth.com/news-insights/massachusetts-pay-transparency-law-takes-effect-what-employers-need-to-know.html)
- Conflict on cure period: two-business-day cure after a Notice to Cure through October 29, 2027 (Choate; K&L Gates) vs. through October 29, 2026 (Greenberg Traurig) — [Choate](https://www.choate.com/insights/massachusetts-pay-transparency-requirements-take-effect-on-october-29-2025/?output=pdf); [K&L Gates 2026 update](https://www.klgates.com/Massachusetts-Employment-Law-Update-for-2026-12-31-2025); [Greenberg Traurig](https://www.gtlaw.com/en/insights/2025/10/massachusetts-pay-transparency-law-takes-effect-on-oct-29-2025)

**PFML (M.G.L. c. 175M)**
- New hires must get DFML notices within 30 days of hire and sign (or decline to sign) an acknowledgment the employer retains; current employees must get written notice of contribution rates (e.g., 2025 rates by Dec 2, 2024); employers must post the DFML poster — [Seyfarth 2025 PFML update](https://www.seyfarth.com/news-insights/massachusetts-pfml-update-dfml-releases-new-2025-rate-sheets-poster-and-employee-notices.html); [Mondaq](https://www.mondaq.com/unitedstates/employee-rights-labour-relations/1546326/massachusetts-pfml-update-dfml-releases-new-2025-rate-sheets-poster-and-employee-notices)
- Notice penalty (2019-era alerts; may be outdated): $50 per individual for a first violation, $300 per individual for subsequent violations — [Foley](https://www.foley.com/?p=49859)
- 2026: maximum weekly benefit $1,230.39 (from $1,170.64 in 2025); total contribution rate unchanged at 0.88% for employers with 25+ covered individuals; sources differ on the split and on the rate quoted for under-25 employers — [Mondaq 2026 rates](https://www.mondaq.com/unitedstates/employee-rights-labour-relations/1687788/massachusetts-announces-paid-family-and-medical-leave-2026-contribution-rates-maximum-weekly-benefits); [Foley Jan 2026](https://www.foley.com/insights/publications/2026/01/new-year-new-massachusetts-paid-family-and-medical-leave/)
- Employers with fewer than 25 MA employees owe no employer share (2025) — [USI](https://info.usi.com/rs/121-VCO-807/images/Massachusetts_Paid_Family_Leave_2025_Contributions_and_Benefits_Oct_4_2024.pdf)
- DFML publishes an FY2025 annual report (applications data, not employer counts) — [mass.gov DFML FY2025 report](https://www.mass.gov/doc/dfml-fy2025-annual-report/download)

**Earned Sick Time (M.G.L. c. 149 §148C; 940 CMR 33.00; effective July 1, 2015)**
- Employers with 11+ employees must provide paid sick time; 10 or fewer may provide unpaid; employers must post the AG's multilingual notice and give a copy to employees; employees can sue for treble damages and attorney fees — [Cooley](https://www.cooley.com/news/insight/2014/massachusetts-new-sick-time-law-effective-july-1-2015); [Kecheslaw](https://kecheslaw.com/practice-areas/employment-law/new-sick-leave-law/); [mass.gov poster requirements](https://www.mass.gov/info-details/massachusetts-workplace-poster-requirements)

**Wage Act and other**
- Vendor guide says the MA Wage Act imposes mandatory treble damages with no good-faith defense, and c. 151B covers employers with 6+ employees (vendor source; verify) — [FirstHR MA compliance guide](https://firsthr.app/compliance-hub/massachusetts/massachusetts-hr-compliance-guide)
- K&L Gates flags 2026 legislative and litigation activity affecting wage requirements and noncompete enforceability — [K&L Gates](https://www.klgates.com/thought-leadership/Massachusetts-Employment-Law-Update-for-2026-12-31-2025)

**Competition**
- Payroll/HR vendors publish MA PFML and compliance hubs (Gusto, FirstHR, Keka), signalling that the payroll layer already covers basics — [Gusto MA PFML](https://gusto.com/resources/states/massachusetts/paid-family-leave); [Keka](https://www.keka.com/compliance/employment-laws/massachusetts); [FirstHR](https://firsthr.app/compliance-hub/massachusetts/massachusetts-hr-compliance-guide)
- Pay transparency compliance content is also produced by compensation software vendors (e.g., Compport) — [Compport](https://www.compport.com/blog/massachusetts-pay-transparency-law)

### Inferences
- Best software-only wedge: "MA Employer Notice Kit" ($9–$19/month per business): auto-generated PFML new-hire notice with e-signature acknowledgment storage (the law requires the employer to retain it), yearly rate-sheet distribution with delivery proof, EST policy generator with accrual rules for under-11 vs 11+ employers, poster bundle, and a job-posting pay-range linter (for 25+ employers, 48-hour offense window logic). All of this is deterministic and can be updated each year by an agent tracking DFML/AG releases.
- Weakness: firms with 25+ employees usually run Gusto/ADP/Paychex/Rippling, which already handle PFML withholding and often posters. The real niche is micro-employers (1–24 employees) with seasonal or household workers, and the price ceiling is low.
- UPL risk: low for notices and posters (state-issued content); moderate for policies; high for noncompetes (individualized agreements with garden-leave/consideration terms), so discard noncompete generation.

### Gaps
- Current AG citation amounts for Earned Sick Time and PFML notice violations not verified (2019 figures only).
- Pricing of poster-compliance services (e.g., subscription poster updates) not retrieved.
- A reference to "Chapter 101 of the Acts of 2026" shifting PFML contributions effective Jan 1, 2027 appeared in one search summary but could not be verified; treat as unconfirmed.
- MA noncompete law (2018 Noncompetition Agreement Act) requirements were not researched in depth because the candidate was discarded on UPL grounds.

## Q5. MA LLC/corporation annual report reminders and filing assistance

### Takeaway
Discard. The $500 MA LLC annual report fee is real and recurring, but the filing itself is a simple online form. Registered-agent and formation companies already bundle annual-report reminders and filing, and the value a reminder adds is small relative to the state fee.

### Cited Findings
- MA LLC annual report: $500/year, due on or before the formation anniversary, filed with the Secretary of the Commonwealth; failure for two consecutive years can lead to administrative dissolution; corporations' annual report is $125 — [Zenind MA LLC fees](https://www.zenind.com/help/post/massachusetts-llc-filing-fees-and-requirements-a-complete-guide); [Terms.law](https://terms.law/2025/09/11/how-to-start-an-llc-in-massachusetts/)
- Conflict: one source adds a $20 online/fax fee ($520 total); others list no extra fee — [Zenind cost breakdown](https://www.zenind.com/help/post/how-much-does-an-llc-cost-in-massachusetts-a-current-fee-breakdown)
- Registered-agent services cost about $100–$300/yr (one guide) or $199–$400/yr (another); MA requires a resident agent with a physical MA address — [Terms.law](https://terms.law/INC/MA/massachusetts-llc-formation-guide.html); [Zenind](https://www.zenind.com/help/post/how-much-does-an-llc-cost-in-massachusetts-a-current-fee-breakdown)
- Formation-service sites (file.business, howtostartanllc, VJM Global) all market MA annual-report handling, indicating a crowded market — [file.business MA](https://main.file.business/states/massachusetts.html); [VJM Global](https://www.vjmglobal.com/feeds/blog/massachusetts-llc-formation-costs)

### Inferences
- Crowded and low-differentiation; registered-agent incumbents (which must have a physical MA address, something a software-only operator lacks) own this customer. Not a fit.

### Gaps
- Number of active MA LLCs and corporations not retrieved; Secretary of the Commonwealth reminder practices not verified.

## Q6. Food establishment / retail MA compliance (allergen awareness, food protection manager, tobacco)

### Takeaway
Massachusetts requires at least one certified food protection manager per establishment to hold an allergen-awareness certificate (5-year validity) and requires the Person in Charge to train staff. Since October 7, 2024, DPH no longer approves specific courses: a course qualifies if it is ANSI/ANAB-accredited, FAREcheck-approved, or includes an interactive video, a knowledge exam and the required content. A software-only course is now legally possible, but the historical price is about $10 and accredited national vendors (StateFoodSafety, Trust20) already market MA versions. Certified Food Protection Manager exams require ANSI accreditation and proctoring, so they are not a fit.

### Cited Findings
- Requirement: at least one certified food protection manager per establishment must hold an allergen-awareness certificate from a DPH-recognized program; the certificate is valid 5 years (older MDPH memos cite 105 CMR 590.009(G)/590.011) — [MDPH memo (2018)](https://www.mass.gov/doc/to-obtain-food-allergen-awareness-training-with-certificate-0/download); [MDPH vendor memo (2011)](https://www.mass.gov/files/documents/2016/07/wo/allergen-awareness-vendors.pdf); [Concord MA](https://concordma.gov/639/Allergy-Awareness-Requirements)
- Historical price: online training cost $10 via approved vendors (Berkshire AHEC, Massachusetts Restaurant Association) — [MDPH vendor memo](https://www.mass.gov/files/documents/2016/07/wo/allergen-awareness-vendors.pdf)
- October 2024 change: per DPH guidance dated Sept 11, 2024 (memo to boards of health Oct 2, 2024), effective October 7, 2024 DPH no longer reviews/approves specific courses; acceptable courses are ANSI/ANAB-accredited with required Food Protection Program allergen content, FAREcheck-approved, or (otherwise) include an interactive video, knowledge exam and required content areas; sesame added as a major allergen; new employee poster; clarified Person in Charge must train employees and be on site — [DPH Food Allergen Awareness Guidance 2024](https://www.mass.gov/doc/food-allergen-awareness-guidance-2024-0/download); [Lee MA allergen update](https://leema.gov/DocumentCenter/View/739/Allergen-Update-10224); [mass.gov guidance list](https://www.mass.gov/lists/food-allergen-awareness-guidance)
- Conflict: StateFoodSafety claims MDPH requires all staff and managers to complete allergen training, while MDPH memos specify the certificate for at least one CFPM — [StateFoodSafety](https://statefoodsafety.com/food-allergens/massachusetts); [MDPH memo](https://www.mass.gov/doc/to-obtain-food-allergen-awareness-training-with-certificate-0/download)
- Competitors: StateFoodSafety MA allergen courses (certificate valid 3 years per vendor); Trust20 MA food allergy course (ANAB-accredited per vendor); AllerTrain classroom course $75/person (Quaboag Valley CDC) — [StateFoodSafety MA courses](https://www.statefoodsafety.com/food-allergens/massachusetts-courses); [Trust20](https://trust20.co/massachusetts-food-allergy); [QVCDC AllerTrain](https://qvcdc.coursestorm.com/course/aller-train-class)

### Inferences
- A non-accredited course meeting the "interactive video + knowledge exam + required content" path is permissible on paper. But local boards of health may favor accredited or FAREcheck courses, and price competition is near $10–$20, so standalone economics are weak. Better as a bundle: "MA Food Establishment Compliance Binder" (allergen certificate tracker for each CFPM with 5-year expiry alerts, Person-in-Charge staff training log with a short employee module and quiz, the new DPH poster, menu allergen notice, plus a 201 CMR 17 WISP for card/POS data, given the Briar Group precedent), at $10–$20 per location per month.
- CFPM certification (ServSafe etc.) requires ANSI-accredited exams and proctoring and is out of scope.
- Tobacco/vape retailer rules were not researched in depth; MA retail tobacco permits are local, so this is a weak fit for a statewide product (inference).

### Gaps
- Current price of StateFoodSafety/Trust20 MA allergen courses not retrieved.
- Number of MA food establishments not retrieved (CBP NAICS 722 needs a Census API key).
- Whether local boards of health accept non-accredited "interactive video + exam" courses in practice is not verified.
- Tobacco/vape retailer training requirements not verified.

## Q7. Other MA-specific niches (HIC contracts, Open Meeting Law minutes, data privacy)

### Takeaway
Two additional niches are credible. (1) Home Improvement Contractor (c. 142A / 201 CMR 18.00) contracts: MA prescribes required contract terms for residential jobs over $1,000 on owner-occupied 1–4 unit homes. A per-job contract generator with registration fields, a deposit-limit check and a 3-day cancellation notice is automatable, though the state offers a free sample contract. (2) Open Meeting Law minutes for volunteer boards: the AG has said AI drafting is allowed if the body ensures accuracy, and the AG minutes checklist is specific. Competitors exist (GovClerk from ~$21/month), with procurement friction. The MA Data Privacy Act is pending, not law.

### Cited Findings
**Home improvement contractors**
- Contractors (and subcontractors) doing residential contracting on existing owner-occupied 1–4 unit residences must register as HICs; registration fee $150 plus a Guaranty Fund payment from $100 (0–3 employees) to $500 (30+) — [mass.gov HIC registration](https://mass.gov/info-details/home-improvement-contractor-registration-and-renewal)
- 201 CMR 18.00 governs HIC registration and enforcement; applies to projects totaling more than $1,000 — [201 CMR 18.00](https://www.mass.gov/regulations/201-CMR-1800-home-improvement-contractor-registration-and-enforcement-of-home)
- mass.gov publishes "Required contract terms in a home improvement contract" and a free sample contract that "satisfies all basic requirements" of c. 142A (with HIC registration number and issue/expiration date fields) but "does not include standard language to protect homeowners" — [mass.gov required terms](https://www.mass.gov/info-details/required-contract-terms-in-a-home-improvement-contract); [mass.gov sample contract](https://www.mass.gov/doc/sample-home-improvement-contract-0/download)
- The MA Contractor Hub publicly shows each contractor's registration status, complaints, Guaranty Fund payouts and arbitration cases — [mass.gov contractor guide](https://www.mass.gov/doc/contractor-guide-ma-contractor-hub-portal/download)
- An OCABR overview page lists figures "31,000" and "12,289" without clear labels; not confirmable as HIC registration counts — [OCABR overview](https://www.mass.gov/info-details/overview-of-the-office-of-consumer-affairs-and-business-regulation)

**Open Meeting Law (G.L. c. 30A §§18–25)**
- An Assistant AG opinion to Westborough: OML does not prohibit AI drafting minutes, but the public body must ensure accuracy; a human's input is legally required; Zoom transcripts do not attribute comments to speakers — [Martha's Vineyard Times](https://www.mvtimes.com/?p=1029470)
- AG minutes checklist: minutes need not be a transcript but must let a non-attendee understand what occurred; required contents include votes, discussion summary, documents used, and names of remote participants — [AG OML minutes checklist](https://www.mass.gov/doc/110624-oml-minutes-checklist/download); [Boxborough OML](https://boxborough-ma.gov/221/Open-Meeting-Law)
- Harvard Allen Lab policy brief (Aug 2026) on technology, remote meetings, AI and OML recommends modernizing guidance — [Harvard Allen Lab](https://ash.harvard.edu/wp-content/uploads/2026/08/Harvard-Allen-Lab-MA-Open-Meeting-Law-Policy-Brief.pdf)
- Competitors/pricing: GovClerk lists ~$21/month (essential, AI minutes, 2 users), ~$63/month (premium), ~$1,098/month (municipal); PublicInput markets AI-powered minutes; CivicPlus/CivicClerk pricing on request; Lee County, FL paid a $17 card charge for about a month of Sembly AI in 2026 — [GetApp GovClerk](https://www.getapp.com/all-software/a/govclerk/); [PublicInput](https://publicinput.com/wp/solutions/meetings/); [Software Advice CivicClerk](https://www.softwareadvice.com/product/484697-CivicClerk); [CivicIQ Lee County](https://civiciq.com/public-contract/7ae65e78-6eb6-4ef8-aa4f-4d6b1bd812da)

**Data privacy (pending)**
- See Q2: S.2619/H5479 in conference committee as of 10/10/2026, not enacted — [malegislature.gov](https://malegislature.gov/Bills/194/S2619/BillHistory)

### Inferences
- HIC kit: per-job contract builder with c. 142A required terms, registration-number validation against the public Contractor Hub, a deposit check (my unverified understanding is that c. 142A caps upfront deposits at one-third of the price, except special-order materials; verify), a 3-day cancellation notice, change-order forms, and a reminder for the 2-year registration renewal. Price: $15–$29/month or $5–$10 per contract. UPL risk is moderate (contract drafting for businesses); limit it to statutory required terms with user-entered scope, as in the state's own sample. Violations of c. 142A are generally treated as c. 93A violations (my understanding, not verified this pass).
- OML minutes: upload audio, then speaker-labeled transcript, then draft minutes structured to the AG checklist (votes by roll call for remote participation, documents used, executive-session handling), then clerk review and approve. Target the many small-town volunteer boards and committees that lack clerks; card payment of ~$20–$50/month per board stays under typical purchase thresholds. The human-accuracy duty sits with the board, not the vendor, so no licensed professional is needed.

### Gaps
- Exact c. 142A contract-term list, deposit cap and 93A linkage not read from primary text (mass.gov blocked).
- Number of active HIC registrants not confirmed.
- Number of MA municipal boards/committees not found (the commonly cited figure of 351 cities and towns was not verified in this pass).
- No MA-specific OML minutes product identified; not proof none exists.

## Q8. Cross-cutting: market counts, UPL risk, automation feasibility

### Takeaway
Massachusetts has about 723,000 small businesses (SBA 2024), most of them nonemployers. Employer firms, the realistic buyers for WISP and employer-notice products, likely number around 126,000 (unverified 2025 third-party split). UPL risk is lowest for security policies, statutory notices, receipts, calculators and trackers, and highest for individualized legal instruments (leases, noncompetes, eviction notices). Courts have treated decision-tree document assembly with human review as UPL in at least one state (Missouri), and no MA-specific authority was found.

### Cited Findings
- SBA 2024 Massachusetts profile: 722,819 small businesses (99.5% of businesses), about 1.4 million small-business employees (43.9%) — [SBA Advocacy 2024 MA profile](https://advocacy.sba.gov/wp-content/uploads/2024/11/Massachusetts.pdf)
- SBA 2023 profile: 697,585 small businesses, 44.7% of employees — [SBA 2023 MA profile](https://advocacy.sba.gov/wp-content/uploads/2023/11/2023-Small-Business-Economic-Profile-MA.pdf)
- Third-party (unverified against SBA): 756,096 MA small businesses in 2025, split 126,237 employer firms and 629,859 nonemployers — [Boostsuite](https://boostsuite.com/small-business-statistics/massachusetts)
- A 2025 MA Small Business Credit Availability report charts small-business counts of about 660k–770k between 2019 and 2024 — [mass.gov report](https://www.mass.gov/doc/2025-small-business-credit-availability-report/download)
- UPL precedent: in Janson v. LegalZoom (W.D. Mo. 2011), the court distinguished permissible blank forms/books from impermissible document preparation where software selects clauses from answers and employees review the result; the case settled (up to $6M), with LegalZoom denying liability — [Quimbee](https://www.quimbee.com/cases/janson-v-legalzoom-com-inc); [Georgetown J. Legal Ethics](https://www.law.georgetown.edu/legal-ethics-journal/wp-content/uploads/sites/24/2019/11/GT-GJLE190045.pdf)
- State outcomes vary (North Carolina dispute and legislation; South Carolina opinion found LegalZoom's practices consistent with professional-conduct rules) — [NC Lawyers Weekly](https://nclawyersweekly.com/2015/05/01/the-legalzoom-zone/); [Goldberg Segalla](https://www.goldbergsegalla.com/blog/professional-liability-matters/ethics/legal-zooms-business-model-prompts-ethical-debate/)

### Inferences
- Automation feasibility summary (my assessment):
  - WISP: high. Deterministic questionnaire-to-policy generation, training/attestation, reminders; yearly content refresh by agent. UPL low.
  - Landlord deposit kit: high. Rules-engine timers, interest math, e-sign, PDF generation, official-form delivery. UPL low if leases and eviction notices are excluded.
  - Employer notice kit: high. State-issued notice content, e-acknowledgment, posting linter. UPL low to moderate (policies).
  - HIC contracts: medium-high. Template assembly from statutory terms. UPL moderate.
  - OML minutes: medium-high. Speech-to-text plus structured drafting; human approval is done by the customer's clerk/board, not the operator. UPL none (not legal advice).
  - Allergen training: high technically, but weak economics.
- Shared risk controls: "not legal advice" positioning; no human review step by the operator (the review step is what made Janson look like a service); cite statutes inline; let users edit; annual law-change monitoring by the agent; Stripe subscriptions tied to annual review cycles.
- A single "Massachusetts Small Business Compliance Hub" could cross-sell WISP + employer notices + industry modules (landlord, HIC, food) to the same ~126k employer firms, rather than six separate products.

### Gaps
- No Massachusetts SJC or bar opinion on software document assembly and UPL was found; MA Rule 5.5 analysis not done.
- Census CBP/Nonemployer counts by industry (landlords NAICS 5311, food service 722, remodelers 236118, accountants 5412) could not be pulled (API key required); SBA 2025 MA profile figures could not be confirmed (PDF returned 403).
- No conversion or willingness-to-pay data specific to MA small businesses for compliance software was found; price anchors are from national comparables.
