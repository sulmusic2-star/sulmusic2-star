# Consumer Self-Serve Web Tools for Massachusetts Legal, Tax and Bureaucratic Processes

Research date: October 10, 2026. Scope: Massachusetts consumer processes where a paid DIY product is proven in other states, and where software can do the whole job (customer enters facts, software produces the filing, packet or letter plus instructions, Stripe bills) with no licensed professional and no manual work per customer. Other states appear only as comparables. "Verified" means read on a primary or official page, or in a fetched page. "Search summary" means the fact came from search-result text and the page itself was not opened. Estimates are labelled.

Research limit: the shared web-search budget for this turn ran out near the end. Items I could not check are listed under Gaps. Several mass.gov pages returned HTTP 403 to direct fetches, so some mass.gov facts come from search summaries of those pages.

---

## Q1. Where is the Massachusetts unauthorized-practice-of-law (UPL) line for self-help software and document preparation?

### Takeaway
Massachusetts bars non-lawyers from "practicing law" (c. 221 §46A) but does not define the term by statute. It has no software safe harbor like the ones in Texas or North Carolina, and I found no Massachusetts appellate ruling on self-help software. The SJC uses a fact-based "custom and practice" test. Under that test, a tool that turns the customer's own facts into a filing they sign and submit themselves (abatement application, demand letter in their own name, small claims form) carries low-to-moderate risk. Risk rises with individualized legal advice, drafting deeds or other legal instruments for others, representing people, or matching them with lawyers.

### Cited Findings
- **c. 221 §46A:** "No individual, other than a member, in good standing, of the bar of this commonwealth shall practice law" or "hold himself out as authorized, entitled, competent, qualified or able to practice law," by "word, sign, letter, advertisement or otherwise." Out-of-state lawyers may appear in a pending case only with the court's permission. The fetched text of §46A has no penalty clause. — [malegislature.gov c.221 §46A](https://malegislature.gov/Laws/GeneralLaws/PartIII/TitleI/Chapter221/Section46A)
- **c. 221 §41:** Covers practicing after removal, holding oneself out as an attorney without admission, advertising authority to settle personal-injury or property-damage claims, and non-lawyers soliciting such claims or criminal defense. First offense: fine of not more than $100 or up to 6 months in prison. Later offenses: up to $500 or up to 1 year. — [malegislature.gov c.221 §41](https://malegislature.gov/Laws/GeneralLaws/PartIII/TitleI/Chapter221/Section41)
- **Leading SJC case:** *Real Estate Bar Ass'n for Massachusetts v. National Real Estate Information Services*, 459 Mass. 512 (2011). Per the search summary, the court held that drafting deeds for others is the practice of law, and that the provider's preparation of HUD-1/HUD-1A settlement statements and other mortgage-related forms was not UPL. — [CATIC copy of the NREIS opinion](https://WWW.CATIC.COM/sites/default/files/2020-04/Massachusetts%20NREIS%20Case.pdf) (search summary; the PDF returned 403 when fetched)
- **The SJC's test:** Per a Boston College law review article, the SJC said the "practice of law" is hard to define and treated "custom and practice" as a key benchmark in a fact-based inquiry. — [BC Law article (LIRA)](https://lira.bc.edu/works/publication-article/6tbm3-xz877)
- **AG advisory:** The Massachusetts AG issued an advisory on the unauthorized practice of law dated 12/19/2014. It is filed under DAPA/DACA (immigration), and I did not retrieve its text. — [MassLegalServices listing](https://masslegalservices.org/node/127241)
- **Texas comparable:** A 1999 amendment to Tex. Gov't Code §81.101 excludes from the "practice of law" the design, creation, publication, distribution, display or sale of computer software, if the product clearly and conspicuously states it is not a substitute for an attorney's advice. The Fifth Circuit then vacated the injunction against Quicken Family Lawyer (*UPL Committee v. Parsons Technology*). Before that, the district court had held the software's interactive questions and generated documents to be the practice of law. — [5th Cir. opinion 99-10388](https://www.ca5.uscourts.gov/Opinions/pub/99/99-10388.CV0.wpd.pdf); [Chapman Law Review](https://www.chapmanlawreview.com/2013/08/69/)
- **North Carolina comparable:** G.S. 84-2.2 (2016, after LegalZoom's antitrust suit against the NC State Bar) excludes interactive document websites from the practice of law if seven conditions are met. They include: an NC-licensed attorney reviews each blank template; a statement that the forms are no substitute for an attorney; disclosure of legal name and address; no disclaiming of warranties or liability; no out-of-state venue; a prominently displayed consumer complaint process; and registration with the State Bar. It does not permit preparing deeds or contracts that convey real property. — [NC G.S. 84-2.2](https://ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_84/GS_84-2.2.html); [NC Bar Blog](https://www.ncbarblog.com/contemplations-on-an-act-to-further-define-practice-of-law-requirements-for-web-site-providers-and-chapter-84-of-the-north-carolina-general-statutes/?s=)
- **Missouri:** In *Janson v. LegalZoom* (W.D. Mo. 2011), a federal court denied LegalZoom summary judgment, finding a factual question about whether its document service was UPL. — [Eric Goldman blog](https://blog.ericgoldman.org/?p=10287)
- **Florida:** In *Florida Bar v. TIKD Services* (Oct. 14, 2021, 4–3), the Florida Supreme Court held that a traffic-ticket app engaged in UPL. TIKD took a percentage of the ticket, forwarded cases to contracted Florida lawyers it paid a flat fee, and refunded customers who got points. The majority said a non-lawyer "lacks the skill or training to ensure the quality of the legal services provided through the attorneys it contracts with." — [ABA Journal](https://www.abajournal.com/news/article/florida-supreme-court-rules-ticket-fighting-startup-was-engaged-in-unauthorized-law-practice)
- **New York / Second Circuit:** In *Upsolve v. James* (Sept. 9, 2025), the Second Circuit vacated the preliminary injunction that had shielded a nonprofit's non-lawyer debt-collection advice from New York's UPL statutes. It held that the statutes regulate speech but are content-neutral (intermediate scrutiny) and remanded. A cert petition (No. 25-948) drew amicus briefs in March 2026. Its outcome is unknown. — [Public Citizen CL&P blog](https://clpblog.citizen.org/second-circuit-holds-unlawful-practice-law-can-apply-to-debt-collection-advice/); [SCOTUS docket brief](https://www.supremecourt.gov/DocketPDF/25/25-948/400716/20260312132759863_Upsolve%20v.%20James_Final.pdf); [Cato](https://www.cato.org/legal-briefs/upsolve-v-james)
- **No lawyer needed for property tax appeals:** Mass.gov's local real-estate tax appeal guidance says "You do not need a lawyer in order to file." — [mass.gov Local real estate tax appeals](https://www.mass.gov/how-to/local-real-estate-tax-appeals) (search summary)

### Inferences
- Massachusetts has no statutory software safe harbor (I found none), so the safest design is scrivener-style. The customer supplies the facts and chooses the claims. The software fills in official forms or neutral templates, gives general published information (statute text, deadlines, fees), and the customer signs and files. No legal conclusions tailored to the customer, no representation, no lawyer referral fees.
- *TIKD* shows that pairing a ticket app with contracted lawyers, plus outcome guarantees, draws UPL action. A pure DIY tool, where the customer submits their own appeal, avoids that model.
- Voluntarily meeting North Carolina's conditions (clear "not a lawyer / not legal advice" disclosures, real name and address, Massachusetts venue, a complaint process, attorney-reviewed templates) is a sensible risk-reduction checklist. An attorney template review is a one-time cost, not per customer.
- Deeds and other real-property conveyancing documents are the clearest Massachusetts no-go zone after *NREIS*. Avoid any product that drafts deeds, trusts or conveyances.

### Gaps
- I found no SJC or Appeals Court decision on self-help software, interactive form sites (LegalZoom-type) or AI document generators in Massachusetts. I also found no Board of Bar Overseers opinion on the point.
- I could not confirm whether c. 221 has a separate penalty that applies to a plain §46A violation, beyond §41 and the courts' injunction power.
- I did not retrieve the 2014 AG UPIL advisory's text.
- Whether a computer-generated "comparable sales analysis" could count as a real estate "appraisal" under Massachusetts appraiser licensing law (c. 112, roughly §§173–195) is unverified. This matters for the abatement product. Disclaim it clearly as an assessment-equity analysis, not an appraisal, and confirm with counsel.
- I did not check Massachusetts Rule of Professional Conduct 5.5 commentary or any 2025–2026 SJC regulatory-reform initiative. One search found nothing.

---

## Q2. Which consumer-protection, billing and refund rules apply (c. 93A, AG junk-fee/auto-renewal rules, FTC DoNotPay), and what are the guarantee norms?

### Takeaway
Any Massachusetts-facing paid tool is subject to c. 93A and the AG's 940 CMR 38.00, effective Sept. 2, 2025. That rule requires the full price up front and, for subscriptions, cancellation as easy as sign-up, advance renewal notices and clear trial terms. The FTC's 2025 DoNotPay order shows the main marketing risk: claiming the tool performs like a lawyer without evidence. Comparables mostly use "no savings, no fee" contingency pricing or low flat fees.

### Cited Findings
- **940 CMR 38.00 scope:** Effective September 2, 2025, for businesses advertising or selling to Massachusetts consumers. Violations are unfair or deceptive acts under c. 93A. — [mass.gov AGO announcement](https://www.mass.gov/news/ag-campbell-releases-junk-fee-regulations-to-help-consumers-avoid-unnecessary-costs); [Frankfurt Kurnit](https://advertisinglaw.fkks.com/post/102k4uj/massachusetts-ag-implements-regulations-on-junk-fees-and-auto-renew-offers)
- **940 CMR 38.00 requirements:** All fees must be disclosed up front, with the total price shown prominently. Any product with a negative-option feature (auto-renewal, free-to-pay conversion) is covered. If a consumer enrolls through a website, they must be able to cancel through the same website. Sellers must send advance written notices about renewals. Trial terms, including the date to cancel by, must be disclosed. — [Subscription Insider](https://www.subscriptioninsider.com/article-type/news/massachusetts-junk-fee-crackdown-subscriptions-trials-and-pricing-rules-effective-sept-2); [Kelley Drye](https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/what-we-learned-from-massachusetts-junk-fee-regulation-update)
- **c. 93A §9(3) demand letter:** A consumer must send a written demand for relief "at least thirty days" before suing. The demand must identify the claimant and reasonably describe the unfair act and the injury. If the business makes a written settlement tender within 30 days and the court later finds it reasonable, recovery can be capped at the tender. Recovery is the greater of actual damages or $25. A court may award two to three times that if the violation was "willful or knowing" or the refusal was in bad faith. The demand is not required for counterclaims, or when the respondent has no place of business or assets in Massachusetts. Attorney's fees are covered in §9(4). — [malegislature.gov c.93A §9](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter93A/Section9)
- **FTC v. DoNotPay:** The FTC finalized its order on February 11, 2025 (vote 5–0 on January 16, 2025). DoNotPay, marketed as "the world's first robot lawyer," must pay $193,000, notify people who subscribed in 2021–2023, and stop claiming its service performs like a real lawyer without sufficient evidence. The complaint alleged the company never tested whether its AI matched a human lawyer when generating legal documents and giving advice, and never hired attorneys to check the quality of its legal features. — [FTC press release](https://www.ftc.gov/node/87474)
- **Ownwell guarantee:** Contingency pricing with a "Savings-or-Free" guarantee: customers pay only if the assessment is lowered. Fee is 25% of savings (worked example: $6,000 bill cut to $5,000 gives a $250 invoice). — [Ownwell FAQ](https://www.ownwell.com/faqs). A review reports 25% in TX, NY, IL and WA, and 35% in GA, FL, CA, CO and PA. — [Money Crashers](https://www.moneycrashers.com/ownwell-review/)
- **TaxProper (2020):** $149 up front or 30% of first-year savings. No charge if its algorithm finds no case, and nothing owed if the appeal is denied. — [TechCrunch, June 2020](https://techcrunch.com/2020/06/05/taxproper-raises-2m-to-automate-getting-your-property-taxes-lowered)
- **WinIt (NYC tickets):** Charges 50% of the ticket amount, and only if the ticket is dismissed. — [App Store listing](https://apps.apple.com/us/app/winit-fight-your-tickets/id929918279)
- **TIKD:** Offered a full refund if points were assessed. — [ABA Journal](https://www.abajournal.com/news/article/florida-supreme-court-rules-ticket-fighting-startup-was-engaged-in-unauthorized-law-practice)
- **DIY packet pricing:** AppealDesk charges a $49 flat fee; AppealSeal charges $100 (California only). — [AppealDesk comparison, updated Aug. 13, 2026](https://www.appealdesk.com/compare/best-property-tax-appeal-services) (vendor-published)

### Inferences
- **Billing:** For Stripe, one-time flat fees (no subscription) avoid most of 940 CMR 38.05's negative-option duties. Any subscription (for example, a landlord deposit-compliance plan) needs self-serve online cancellation, advance renewal notices and all-in pricing.
- **Refunds:** "No savings, no fee" contingency pricing needs the outcome verified (the assessor's decision letter), which means manual work unless the customer uploads it and payment is automated. A flat fee with a no-questions refund window (say 30 days, or "refund if you don't file") fits the no-manual-work rule better.
- **Marketing:** Never say "robot lawyer," "AI attorney" or "as good as a lawyer." Claims such as "X% success" need substantiation (the DoNotPay lesson), and under Massachusetts law misleading claims are also c. 93A violations.
- The 93A §9 demand-letter requirement is itself a Massachusetts-only consumer process that software can serve (see Q5).

### Gaps
- I did not read the exact advance-notice windows in 940 CMR 38.05.
- I found no Massachusetts-specific refund-norm data for DIY legal-document tools.

---

## Q3. Candidate A: DIY residential property tax abatement packet (Form 128). Demand, pricing, competition, data, feasibility

### Takeaway
This is the strongest candidate. The process is statewide, lawyer-free, deadline-driven and high-value. Free standardized statewide parcel data exists (MassGIS). Pricing is proven elsewhere: $49–$149 flat, or 25–35% contingency. However, Massachusetts is not empty. AppealDesk, a $49 national DIY packet, claims all 351 Massachusetts towns. O'Connor offers full-service work in Massachusetts. Ownwell does not serve Massachusetts directly but launched a "National Appeals Packet" in February 2026 for areas outside its core states. A Massachusetts-specific product would have to win on depth: town-specific deadlines and forms, Boston's 30-day information-request form, the over-$5,000 payment rule, and ATB next steps, plus bundled exemption checks. The season is short: late December to about February 1 in quarterly-billing towns.

### Cited Findings
**Process and rules (Massachusetts)**
- **Deadline:** Form 128 must be filed with the assessors "not later than due date of first actual (not preliminary) tax payment for fiscal year." — [Secretary of the Commonwealth, Property abatement](https://www.sec.state.ma.us/divisions/cis/tax/property-abatement.htm)
- **Collection and payment:** Filing does not stop collection. If the bill is over $5,000, payment must be made on time to keep the right to appeal to the Appellate Tax Board. — [sec.state.ma.us](https://www.sec.state.ma.us/divisions/cis/tax/property-abatement.htm)
- **Boston:** The FY2026 deadline was February 2, 2026, with filing possible after third-quarter bills went out in late December 2025. The FY2027 window ends February 1, 2027. Assessing has three months to act. If the information-request form is not returned within 30 days, "we will deny your application" and the owner may lose the ATB appeal right. Grounds: overvalued, disproportionately assessed, improperly classified, or eligible for a statutory exemption. — [boston.gov How to file a real estate tax abatement](https://www.boston.gov/departments/assessing/how-file-real-estate-tax-abatement); [boston.gov Tax exemptions and abatements](https://www.boston.gov/ar/node/15952506) (search summary)
- **Other towns:** Marlborough and Boxborough FY2026 deadlines were also February 2, 2026. Methuen's guidelines list three grounds for granting an abatement: data errors, overvaluation shown by comparable sales, and disproportionate assessment. — [Methuen guidelines](https://methuen.gov/DocumentCenter/View/5110/Guidelines-for-Preparing-an-Abatement-Application-PDF); [Boxborough FY2026 application](https://www.boxborough-ma.gov/DocumentCenter/View/6032/FY2026-Abatement-Application) (search summary)
- **ATB appeal:** If the assessors deny or fail to act within 3 months, the owner may appeal to the ATB within 3 months. ATB filing fees scale with assessed value, from $10 (≤$20,000) up to a $5,000 cap. — [c. 58A §7](https://malegislature.gov/Laws/GeneralLaws/Chapter58A/Section7) (search summary); [AppealDesk MA page](https://www.appealdesk.com/compare/best-massachusetts-property-tax-appeal-services)
- **ATB caseload:** Most single-family homeowners appeal under the ATB's informal procedure. — [CT OLR report 2020-R-0043](https://prdext3.cga.ct.gov/2020/rpt/pdf/2020-R-0043.pdf)

**Volume (no statewide count found; local data points)**
- **Boston:** 1,715 abatement applications (all property types) by the FY2024 deadline, down from 1,813 the year before. — [Boston Globe, Feb. 26, 2024](https://www.bostonglobe.com/2024/02/26/business/boston-office-tax-breaks-downtown/)
- **Boston FY2013:** 1,470 residential applications, the lowest count ever in a revaluation year. — [Banker & Tradesman](https://bankerandtradesman.com/boston-tax-abatement-applications-continue-to-drop)
- **Upton (Feb. 2023 minutes):** 62 residential applications, 1.8% of 3,396 real estate parcels. — [Upton Board of Assessors minutes](https://uptonma.gov/DocumentCenter/View/5054/Assessors-min-272023)
- **ATB:** Taxpayers filed 29,946 appeals with the ATB from July 2000 to June 2005 (about 6,000 a year). Over 90% of ATB petitions are local property-tax appeals. — [Mass. State Library archives, ATB report](https://archives.lib.state.ma.us/server/api/core/bitstreams/c51cee83-013b-41ff-90c7-076776c5359c/content) (search summary; I did not confirm which archived bitstream holds each figure)
- **Households:** Massachusetts had 2,762,070 households (2019–2023) and a 62.6% owner-occupancy rate. — [Census QuickFacts MA](https://www.census.gov/quickfacts/fact/table/MA/HSG495223)
- **National attitudes:** Ownwell's 2025 national survey found 74% of homeowners worried about rising property taxes, but only 22% had ever appealed. — [Crunchbase News](https://news.crunchbase.com/venture/ownwell-raise-lower-homeowner-property-tax/) / [VCA Online](https://www.vcaonline.com/news/2026021908/ownwell-raises-50m-launches-national-service-to-streamline-property-tax-appeals-and-make-home-ownership-more-affordable/)

**Data availability**
- **MassGIS:** Publishes statewide standardized assessor parcel data free. A statewide zip (shapefile or FGDB) is rebuilt twice a year (January 1 and July 1); the current files are dated January 1, 2026. Single towns can be downloaded from the interactive property map. — [mass.gov MassGIS Property Tax Parcels](https://www.mass.gov/info-details/massgis-data-property-tax-parcels) (search summary); [Leventhal Map Center guide](https://cartinal.leventhalmap.org/guides/mass-parcels.html)
- **Standard:** The data follow the MassGIS Standard for Digital Parcels, Version 3 (June 2022), which gives each parcel a single statewide unique identifier. — [MassGIS parcel standard](https://www.mass.gov/info-details/massgis-standard-for-digital-parcels-and-related-data-sets)

**Proven comparables and Massachusetts competition**
- **Ownwell scale:** More than 1 million appeals processed, "$400M+ saved," 86% success rate and $774 average annual savings in core markets, 25% contingency, no upfront fee. Core states: TX, IL, FL, GA, CA, WA, NY. A February 2026 "National Appeals Packet" gives homeowners outside core areas a ready-to-file packet with instructions, deadlines and valuation evidence (price not stated). — [VCA Online, Feb. 19, 2026](https://www.vcaonline.com/news/2026021908/ownwell-raises-50m-launches-national-service-to-streamline-property-tax-appeals-and-make-home-ownership-more-affordable/)
- **Ownwell funding:** $50M Series B ($30M equity led by Alpha Edison and Mercato Partners, plus $20M debt from Western Alliance Bank) announced February 19, 2026. — [Pulse 2.0](https://pulse2.com/ownwell-50-million-series-b/amp/)
- **Ownwell state count conflicts:** The FAQ and help center list seven states and no Massachusetts. — [Ownwell FAQ](https://www.ownwell.com/faqs); [Ownwell help: states](https://www.ownwell.com/help/article/11785817631771-what-states-are-you-located-in-). AppealDesk reports anywhere from seven to nine states during 2026. — [AppealDesk vs Ownwell](https://www.appealdesk.com/compare/appealdesk-vs-ownwell); [AppealDesk comparison](https://www.appealdesk.com/compare/best-property-tax-appeal-services)
- **AppealDesk in Massachusetts:** Claims coverage of "all 351 MA cities and towns" for a $49 DIY evidence packet and filing instructions (owner files; no ATB representation). It lists O'Connor & Associates as full-service in Massachusetts, including ATB representation, with the contingency rate unclear ("half of first-year savings" in one place). Its worked example: an $800,000 home at a 1.1% rate saves $880 a year with a 10% reduction. Caveats: AppealDesk is the publisher and ranks itself first; the page says "Last updated June 26, 2026" but cites August 2026 reviews. — [AppealDesk MA comparison](https://www.appealdesk.com/compare/best-massachusetts-property-tax-appeal-services)
- **TaxProper (2020):** Covered Cook and DuPage counties plus counties in NY, CA, GA, FL, HI, MO, NV, PA, TN, UT and WA. No Massachusetts. It generated the paperwork and filed for the customer. — [TechCrunch 2020](https://techcrunch.com/2020/06/05/taxproper-raises-2m-to-automate-getting-your-property-taxes-lowered)
- **Free tools:** Form 128 itself and the state's guidance are free. — [mass.gov Form 128](https://www.mass.gov/doc/state-tax-form-128-application-for-abatement-of-real-property-tax-or-personal-property-tax-0/download)

### Inferences
- **Volume estimate:** about 1.73M owner-occupied units (2.76M × 62.6%). If 1–2% file each year, as in Upton, that is roughly 17,000–35,000 residential applications statewide. More would file in revaluation years or with active marketing. Ownwell's finding that only 22% have ever appealed suggests most of the market has never tried.
- **Revenue estimate:** At $49–$79 per packet, capturing 3,000–8,000 Massachusetts customers a season would bring in about $150k–$600k in roughly 6 weeks. Treat this as illustrative only.
- **Seasonality:** Extreme. Quarterly-billing towns have a window from late December to about February 1. Semi-annual towns use the first actual bill's due date, which differs, so the product needs a deadline table for all 351 towns. Off-season revenue would have to come from exemptions (Q8) or ATB packets.
- **Automation:** Almost complete. Parcel lookup, comparables chosen by attributes, equity/disproportion analysis, a pre-filled Form 128 (plus Boston's form where it applies), a cover letter, a filing checklist and deadline reminders can all be automated. The owner signs and delivers the form; many towns accept email or mail.
- **Differentiation:** AppealDesk and Ownwell offer generic national packets. Massachusetts-specific value would be: the >$5,000 payment rule, Boston's 30-day information form, ATB fee calculation and informal-procedure instructions, the 3-month deemed-denial clock, and a check for missed exemptions.
- **UPL risk:** Low. Mass.gov says no lawyer is needed, the owner files, and the content is valuation data. Appraiser-licensing wording needs checking (Q1 Gaps).

### Gaps
- I found no statewide count of abatement applications filed or granted (DLS or ATB), and no recent ATB annual report. A DLS records request is likely needed.
- I could not confirm MassGIS sale-price and sale-date attribute names (for example LS_PRICE, LS_DATE) or how complete they are town by town (page returned 403). The comparables method depends on this.
- The price of Ownwell's National Appeals Packet, and whether it lists Massachusetts, is unknown.
- I did not independently confirm O'Connor's Massachusetts fee or AppealDesk's actual Massachusetts volume.
- Statewide success rates for residential abatements are unknown.

---

## Q4. Candidate B: Security deposit tools under c. 186 §15B (tenant demand/claim kit, landlord compliance kit)

### Takeaway
Massachusetts's deposit law is strict and technical, with treble damages, so software helps on both sides. On the tenant side, strong free tools already exist (MassLegalHelp Form 6 and a CourtFormsOnline interactive demand-letter tool), so a paid tenant tool would need to add a §15B violation checker, a treble-damages calculator, a 93A demand option and a small claims packet. The landlord side (receipts, statement of condition, bank-account notice, annual interest, sworn itemized deduction list) is a better-defended paid niche, possibly as a low-cost subscription. Free competition there is thinner (MassLandlords is members-only), and mistakes cost landlords triple the deposit.

### Cited Findings
- **Allowed upfront charges:** First month's rent, last month's rent, a security deposit no greater than one month's rent, and the cost of a lock and key. — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B)
- **Landlord paperwork duties:** Signed receipts for the deposit and last month's rent. A signed statement of condition within 10 days, with a bold-faced notice giving the tenant 15 days to respond. The deposit must sit in a separate interest-bearing Massachusetts bank account, and within 30 days the tenant must get a receipt naming the bank, amount and account number. Interest is 5% a year or the bank's lower rate, paid annually. Records must be kept 2 years. — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B)
- **Return and deductions:** Within 30 days after the tenancy ends, the landlord must return the deposit or balance. Damage deductions require an itemized list sworn under penalty of perjury, with estimates, bills or receipts. — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B)
- **Forfeiture:** Under §15B(6), the landlord forfeits the right to keep any of the deposit for: failing to deposit it as required, no itemized list within 30 days, non-conforming lease terms, failing to transfer it on sale, or failing to return the balance within 30 days. — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B)
- **Treble damages:** Under §15B(7), violations of clauses (a), (d) or (e) of subsection 6 mean "the tenant shall be awarded damages in an amount equal to three times the amount of such security deposit," plus 5% interest, court costs and reasonable attorney's fees. Waivers and conflicting lease terms are void. — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B)
- **No §15B demand requirement:** The fetched statute text contains no pre-suit demand requirement. A c. 93A claim does require a 30-day demand. — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B); [c.93A §9](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter93A/Section9)
- **Free tenant tools:** MassLegalHelp tells tenants to demand 100% of the deposit with "Security Deposit Demand Letter (Form 6)" or "the CourtFormsOnline interactive tool," then sue in small claims. — [MassLegalHelp Security Deposits handout 2025](https://www.masslegalhelp.org/sites/default/files/2025-02/Handout%203%20Security%20Deposits%202025.pdf). The Suffolk LIT Lab does not charge for its forms. — [Appeals Court Admin. Order 20-5](https://www.mass.gov/doc/appeals-court-administrative-order-20-5/download) (search summary)
- **Treble damages and the small claims cap:** Mass.gov says the court may award 3× the deposit plus interest and attorney's fees when the landlord has forfeited the right to hold it. — [mass.gov security deposit page](https://www.mass.gov/info-details/learn-about-returning-or-getting-back-a-security-deposit) (search summary). One secondary source says the $7,000 small claims cap applies to the base amount, not the trebled amount. — [Tellus](https://resources.tellusapp.com/tenants/massachusetts/security-deposits/massachusetts-security-deposit-rights) (commercial, unverified)
- **Generic letter generators:** Free: Pine and Dot & Cross (which waitlists its small claims and deadline-tracking add-ons). Paid: Vaquill's state-specific workflow inside its QuillDraft product (price not found). — [Pine](https://www.19pine.ai/tools/security-deposit-demand); [Dot & Cross](https://dotandcross.onrender.com/tools/security-deposit-demand); [Vaquill docs](https://www.vaquill.ai/docs/workflows/built-in/security-deposit-demand)
- **Landlord-side:** MassLandlords keeps its deposit training materials for members and warns that a paperwork mistake can cost "three times the amount of the deposit plus attorney's fees." — [MassLandlords](https://masslandlords.net/?p=37529). EZ Landlord Forms sells a Massachusetts Statement of Condition and Security Deposit Follow-up Statement (price not captured). — [EZ Landlord Forms MA Statement of Condition](https://www.ezlandlordforms.com/documents/108983/massachusetts-statement-of-condition/)
- **Renter share:** Massachusetts's owner-occupancy rate is 62.6% of 2,762,070 households. — [Census QuickFacts](https://www.census.gov/quickfacts/fact/table/MA/HSG495223)

### Inferences
- **Renter market:** about 1.03M renter households (37% of 2.76M; my arithmetic). Annual move-outs with a deposit are unknown. Even a few percent with disputes would be tens of thousands of potential tenant users a year (estimate).
- **Tenant product ($19–$39 one-time):** Questions about receipts, bank notice, statement of condition and itemization dates; a forfeiture/treble checklist; a demand letter in the tenant's own name (optionally with a 93A §9 demand); a pre-filled small claims Statement of Claim; deadline reminders. Free competitors cover the letter, so the paid value is the violation analysis plus the court packet. It sits closer to UPL than the abatement product because it applies law to facts, so it must present the statute's conditions and let the user decide, rather than say "you are owed $X."
- **Landlord product:** Either a $49–$99 one-time kit or about $3–$8 per unit per month (subject to 940 CMR 38). It would generate the receipts, the 10-day statement of condition with the bold notice, the 30-day bank-account receipt, annual interest calculations and notices, and a sworn itemized deduction list with uploaded receipts. This is recurring, fully automatable and lower in UPL risk (compliance paperwork from the statute's own requirements).
- **Seasonality:** Mild. Boston's September 1 turnover gives an August–October peak (common knowledge, not sourced).

### Gaps
- I found no data on deposit-dispute volume or the share of Massachusetts landlords who take deposits.
- I found no pricing for Vaquill, EZ Landlord Forms' Massachusetts documents or MassLandlords membership.
- I could not open the CourtFormsOnline catalog (the fetch returned only a title), so I could not see its full list of Massachusetts tools or usage figures.

---

## Q5. Candidate C: Small claims preparation plus a c. 93A demand-letter generator (Massachusetts-specific)

### Takeaway
Massachusetts small claims volume is large (about 90,000–120,000 filings a year in older data, much of it debt-collection filings), and filing is cheap ($40–$150). But the Trial Court's own free guided online tool and eFileMA (open to self-represented filers) make "help me fill out the form" weak on its own. The Massachusetts twist is the c. 93A §9 30-day demand letter, which must come before a 93A suit and can unlock double or treble damages. A "93A demand letter, then small claims packet" workflow for consumer disputes (contractors, car dealers, landlords, retailers) is Massachusetts-specific and fully automatable. Generic demand-letter tools are often free, so willingness to pay is likely low ($19–$49).

### Cited Findings
- **Filing volume:** District Court small claims filings peaked at 120,023 in FY2008, were 90,196 in FY2012 and 87,996 in FY2013, and 94,315 in FY2015 (up 3.0% from 91,571 in FY2014). — [mass.gov Trial Court summary of cases by fiscal year](https://www.mass.gov/doc/summary-of-cases-by-fiscal-years/download) (search summary; several annual tables, and I did not confirm which document holds each figure)
- **Debt-collection share:** A July 2024 Trial Court report on consumer debt cases filed as small claims and civil cases in the BMC and District Courts gives annual counts for 2019–2023 of roughly 61,000–95,000 (year labels unclear in the extract). — [mass.gov consumer debt report 2024](https://www.mass.gov/doc/review-of-consumer-debt-cases-filed-and-disposed-2024/download)
- **Fees and cap:** $40 for claims up to $500; $50 for $501–$2,000; $100 for $2,001–$5,000; $150 for $5,001–$7,000. The cap is $7,000 except for auto-accident property damage. — [mass.gov Small Claims Court](https://www.mass.gov/info-details/small-claims-court) (search summary)
- **Free government filing tools:** "Any litigant (attorney, self represented, state agency, etc.) may eFile," and the District Court and BMC both accept small claims through eFileMA (registration required, not mandatory). — [mass.gov Learn about eFiling](https://www.mass.gov/info-details/learn-about-efiling-in-the-trial-court). Mass.gov's small claims page calls the online route, with its guided form tool, the easiest way to file. — [mass.gov File a small claim](https://www.mass.gov/how-to/file-a-small-claim-in-the-boston-municipal-court-district-court-or-housing-court) (search summary)
- **c. 93A §9 demand rules:** 30-day pre-suit demand; tender mechanism; $25 minimum; 2–3× for willful/knowing violations or a bad-faith refusal. — [c.93A §9](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter93A/Section9)
- **DoNotPay:** The FTC alleged DoNotPay sold AI-generated legal documents without testing their quality. Its order bars "performs like a lawyer" claims without evidence. — [FTC](https://www.ftc.gov/node/87474)

### Inferences
- Most small claims filings are business-versus-consumer debt cases, so the consumer-plaintiff slice is much smaller than about 90,000 (estimate; unquantified).
- **Product:** A dispute wizard covering the facts, a 93A demand letter (with the statutory elements: who, the unfair act, the injury, the relief requested), a 30-day reminder, evaluation of any tender, then a pre-filled Statement of Claim, a filing-fee calculator, eFileMA or paper instructions, and a hearing-prep checklist with an evidence index. Flat fee of $29–$49. Bundle with the deposit product (deposit violations are commonly pleaded under 93A as well; not sourced here).
- **UPL risk:** Moderate. A demand letter sent in the consumer's own name is self-representation, but the tool should not judge claim strength. Avoid outcome or success-rate marketing without substantiation.

### Gaps
- I found no small claims filing statistics newer than FY2015, and no plaintiff-type breakdown.
- I did not identify paid Massachusetts-specific small claims or 93A tools, or Rocket Lawyer/LegalZoom pricing for comparable letters.
- I could not inspect the Trial Court guided form tool's scope (page returned 403).

---

## Q6. Candidate D: Parking ticket and EZDriveMA toll invoice disputes (RMV-adjacent)

### Takeaway
Volume is large: Boston alone issues an estimated 1.2–1.5M tickets a year and about 10% are disputed. Proven pricing exists (WinIt: 50% of the ticket, only if dismissed). But fines are small, appeals are free and online, the contingency model needs outcome verification, and the lawyer-backed variant (TIKD) was held to be UPL. EZDriveMA appeals are a written-statement-by-mail process to a Clerk under 700 CMR. That is automatable, but the customer value per case is low and there is no clear proven paid comparable for toll disputes. This is a secondary product at best: a $5–$15 flat-fee "appeal letter builder" or an add-on.

### Cited Findings
- **Boston volume:** A 2021 city bid put Boston's annual parking-ticket issuance at 1.2–1.5 million, with about 10% disputed each year. — [BINJ, Nov. 2021](https://binj.news/2021/11/23/more-tickets-more-tows-more-fees/)
- **Boston outcomes:** Of 227,183 contested tickets in one reported year, 25% were dismissed; in-person hearings had 77% dismissed (year not shown in the snippet). — [Boston Magazine](https://www.bostonmagazine.com/?p=2671110). A Boston Herald report relayed by Boston 25 said 71,922 tickets were dismissed on appeal in an earlier year. — [Boston 25 News](https://www.boston25news.com/news/politics/report-72000-boston-parking-tickets-thrown-out-during-appeal/141844847)
- **WinIt:** 50% of the ticket amount, only if dismissed. It worked with Empire Commercial Services (lawyers and ex-judges). In 2017 it claimed to have saved drivers $6M in fines over two years. — [App Store](https://apps.apple.com/us/app/winit-fight-your-tickets/id929918279); [News 12](https://bronx.news12.com/app-helps-city-residents-fight-parking-traffic-tickets-36555744)
- **TIKD:** Held to be UPL in Florida (2021) for routing tickets to contracted lawyers. — [ABA Journal](https://www.abajournal.com/news/article/florida-supreme-court-rules-ticket-fighting-startup-was-engaged-in-unauthorized-law-practice)
- **EZDriveMA appeals:** The registered owner must pay by the invoice due date or appeal under 700 CMR 7.05/11.00. A mail appeal goes to a Clerk and must include a signed statement explaining the basis for the appeal. Late fees follow a regulatory table. EZDriveMA-related fines, fees and penalties are capped at $500 a year per vehicle. — [700 CMR 7.05](https://law.cornell.edu/regulations/massachusetts/700-CMR-7-05); [700 CMR 11.06](https://law.cornell.edu/regulations/massachusetts/700-CMR-11-06)
- **EZDriveMA invoices and holds:** Pay By Plate MA invoices have replaced violations for transponder-less trips since October 28, 2016, with a $0.60 fee per invoice. Unpaid invoices can trigger registration or license non-renewal holds and collections. — [mass.gov Toll payment options](https://www.mass.gov/info-details/toll-payment-options); [EZDriveMA violations](https://ezdrivema.com/violations). New York and Massachusetts place reciprocal registration holds for unpaid tolls. — [NY DMV](https://dmv.ny.gov/more-info/new-york-and-massachusetts-tolls)
- **Pending bills:** S.2874 and S.2405 (194th session) would bar RMV non-renewal for people on toll payment plans. Status unconfirmed. — [S.2874](https://malegislature.gov/Bills/194/S2874/Senate/Bill/Text)
- **Fee schedule:** EZDriveMA terms say fees may change at MassDOT's discretion; the current schedule is on ezdrivema.com. — [EZDriveMA Terms](https://www.ezdrivema.com/documentation/TermsConditions.pdf)

### Inferences
- **Volume:** About 120,000–150,000 Boston parking disputes a year (10% of 1.2–1.5M) is a large top of funnel, but each ticket is worth little. Contingency pricing requires confirming the result, which conflicts with the no-manual-work rule unless the user self-reports.
- **EZDriveMA:** Disputes (plate misreads, rental cars, sold or stolen vehicles, transponder failures) are template-friendly. A tool could build the signed statement, an evidence checklist (plate cancellation receipt, transponder statement) and deadline reminders. UPL risk is minimal because this is an administrative appeal by the owner.
- **RMV:** I found no clearly monetizable RMV document process; most RMV forms are free and online.

### Gaps
- I found no recent (2024–2026) official Boston ticket, appeal or dismissal statistics, and no typical fine amounts.
- I found no EZDriveMA invoice or dispute volume, and no paid comparable for toll disputes in any state.
- I did not research parking appeal processes in other Massachusetts cities (Cambridge, Somerville, Worcester).

---

## Q7. Candidate E: Massachusetts Homestead Declaration (c. 188). Is a legitimate paid tool viable?

### Takeaway
Discard as a standalone paid product. The form is free from the Secretary of the Commonwealth and the registries, recording costs about $35–$36, and registries have publicly warned homeowners about third-party companies charging for homestead forms and deed copies. A paid tool would be filed under "solicitation scam" in consumers' minds, and preparing a recordable real-property instrument for others is near the *NREIS* line. At most, offer a free reminder or link inside the abatement and exemptions product.

### Cited Findings
- **Amounts:** Current c. 188 §1 sets the declared homestead exemption at "$1,000,000 created by a written declaration" and the automatic homestead at "$125,000 pursuant to section 4." It defines "elderly person" as 62 or older and disabled persons by SSI standards. — [malegislature.gov c.188 §1](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter188/Section1). Older registry and state guides give a $500,000 declared amount, so they are out of date. A secondary source attributes the rise to $1M to the 2024 Affordable Homes Act (Acts 2024 c.150). — [ezel.ai survey](https://ezel.ai/surveys/homestead-exemption-amounts/massachusetts) (secondary; the cause is unverified)
- **Recording fee:** One Norfolk County notice cites a $36 state-imposed fee. The Secretary of the Commonwealth's guide says $35, with forms at sec.state.ma.us/rod and most registries. Plymouth asks $35 plus $2 postage for mailed filings. — [Patch/Norfolk Registry](https://patch.com/massachusetts/stoughton/norfolk-register-deeds-promotes-homestead-act); [Sec. of State Homestead guide](https://www.sec.state.ma.us/divisions/cis/download/Homestead_book.pdf) (search summary; the PDF fetch returned 404); [Plymouth Registry](https://www.plymouthdeeds.org/)
- **Solicitation warnings:** In 2009 the Southern Essex Registry warned after a Beverly homeowner paid $15 online for a homestead form that is free at the registry. It had earlier exposed a company charging $59.50 for deed copies. — [Salem Deeds notices](https://www.salemdeeds.com/SalemDeeds/DownLoadFile.aspx?newsid=120); [Salem Deeds notice 128](https://www.salemdeeds.com/SalemDeeds/DownLoadFile.aspx?newsid=128). Essex County homeowners were also warned about mailers charging $100 for free deed copies. — [Patch Salem](https://patch.com/massachusetts/salem/essex-county-homeowners-warned-deed-solicitation-scam)
- **Trust-held homes:** These use a separate trust form. — [Sec. of State trust homestead form](https://www.sec.state.ma.us/divisions/registry-of-deeds/download/declaration-of-homestead-form-trust.pdf)

### Inferences
- Willingness to pay is near zero against a free one-page form and a $36 fee, and the solicitation-scam association could hurt any brand that charges for it.
- A free "homestead check" inside the abatement and exemptions product could build trust and email lists without the downside.

### Gaps
- I could not confirm current elderly/disabled homestead amounts under the post-2024 statute (the §1 definitions fetched did not state them) or the exact 2026 recording fee.
- I found no 2024–2026 registry warnings and no evidence of any legitimate paid homestead tool.

---

## Q8. Candidate F: Short-term rental host compliance, and an added candidate: property tax exemption and senior circuit breaker finder

### Takeaway
Discard short-term rental compliance. Airbnb collects and remits all Massachusetts state and local occupancy excises and fees, hosts don't file returns for Airbnb bookings, DOR registration is free, and Avalara MyLodgeTax ($27/month/property) already serves off-platform hosts. The residual need (DOR registration help, the 14-day exemption renewal by January 15, local registrations such as Nantucket's) is small and requires the host's MassTaxConnect login.

Added candidate: a Massachusetts "property-tax savings check" bundling residential exemption, personal exemptions and the Senior Circuit Breaker credit. It has proven paid analogs (Ownwell's exemption filing service), but free government filing (Schedule CB on MassTaxConnect) caps pricing. It works best as an upsell to the abatement product.

### Cited Findings
**Short-term rentals**
- **Tax scope:** State room occupancy excise is 5.7%, with local taxes and fees on top. It applies to short-term rentals of 31 days or less since July 1, 2019. — [mass.gov Room Occupancy Excise](https://www.mass.gov/info-details/room-occupancy-excise-tax) (updated April 8, 2026, per search summary)
- **Operator duties:** Register with DOR via MassTaxConnect, get and post a Certificate of Registration for each property, and give the number to intermediaries. Operators renting 14 days or fewer are tax-exempt but must still register, and must claim or renew the exemption by January 15. Liability coverage of at least $1,000,000 is required unless the platform provides it. — [mass.gov Room Occupancy Excise](https://www.mass.gov/info-details/room-occupancy-excise-tax); [mass.gov Public Registry of Lodging Operators](https://www.mass.gov/info-details/public-registry-of-lodging-operators)
- **Airbnb collects:** It remits the state excise (5.7%), local excise (0–6.5%), Cape Cod and Islands Water Protection Fund (2.75%), Community Impact Fee (3%) and Convention Center Finance Fee (2.75%) where they apply. Hosts must register with DOR (free; certificate number format "C" plus 10 digits), and Boston hosts must also complete Boston registration. "You don't need to file returns" for Airbnb transactions; off-platform rentals do need returns. — [Airbnb Help: Massachusetts](https://www.airbnb.com/help/article/2587); [Airbnb Help: tax collection locations](https://www.airbnb.com/help/article/2509)
- **MyLodgeTax:** "Starting at $27 per month" per property; it determines rates, manages licenses and prepares, files and pays. — [Avalara MyLodgeTax](https://www.avalara.com/mylodgetax/en/index.html). The Pro tier (6+ properties) is quote-based. — [STRHub](https://strhub.com/product/avalara-mylodgetax-2/). One review reports a $299 setup fee (unconfirmed). — [STR Specialist review](https://strspecialist.com/reviews/avalara-mylodgetax-tax-compliance-review)
- **Local layer example:** Nantucket requires a local registration at $250 per unit per year, plus a copy of the DOR certificate. — [BNBCalc Nantucket guide](https://www.bnbcalc.com/blog/short-term-rental-regulation/Nantucket-Massachusetts-Guide) (secondary)

**Exemptions and circuit breaker (added candidate)**
- **Circuit Breaker eligibility:** The tax year 2025 maximum credit is $2,820. The claimant must be 65 or older and the residence assessed at no more than $1,298,000. — [mass.gov Senior Circuit Breaker](https://www.mass.gov/info-details/senior-circuit-breaker-tax-credit). Income limits for 2025: $75,000 single, $94,000 head of household, $112,000 joint. — [TaxSlayer 2025 MA changes](https://support.taxslayer.com/hc/en-us/articles/360020391551-What-s-new-in-2025-for-Massachusetts)
- **Circuit Breaker filing:** Schedule CB must be filed within 3 years of the return's due date. Full-year residents who have filed before can file Schedule CB free on MassTaxConnect. — [mass.gov Senior Circuit Breaker](https://www.mass.gov/info-details/senior-circuit-breaker-tax-credit). Seniors must file even if they owe no tax, and can amend to claim missed years. — [Reading Post](https://thereadingpost.com/2019/02/28/rep-jones-tax-savings-available-through-senior-circuit-breaker/); [Westford guide](https://westfordma.gov/DocumentCenter/View/9933)
- **Circuit Breaker cost:** The state budget estimated about $80.2M for FY2019 (older figure; claimant counts not given). — [MA Tax Expenditure Budget FY2019 item 1.609](https://budget.digital.mass.gov/bb/h1/fy19h1/prnt_19/tax_19/items/ptax1609.htm)
- **Boston residential exemption:** Set at 35% of the average assessed value of Class One residential parcels for FY2026. — [Boston FY26 Tax Classification Order](https://www.boston.gov/sites/default/files/file/2025/12/FY26%20Tax%20Classification%20order.pdf). The FY26 application deadline was April 1, 2026. Boston's handout cites $3,984.21 in savings, apparently the prior year's figure; other dollar figures conflict. — [Boston FY26 residential exemption handout](https://content.boston.gov/sites/default/files/file/2025/09/FY26%20ResExempt%20Q1%20Q2_5.pdf) (search summary)
- **Ownwell exemptions:** Offers retroactive homestead-exemption services in most U.S. states (fee not found). — [Ownwell FAQ](https://www.ownwell.com/faqs); [Money Crashers](https://www.moneycrashers.com/ownwell-review/)

### Inferences
- **Short-term rentals:** Platform collection removes the core pain, and filing requires the host's MassTaxConnect credentials, which conflicts with full automation by a third party. Discard.
- **Exemptions bundle:** "Check my Massachusetts property-tax savings" (abatement + residential exemption in adopting towns + Circuit Breaker estimate + homestead reminder) raises average order value and stretches the season (residential exemption deadlines around April 1 in Boston; Circuit Breaker at income-tax season). Pricing of $19–$29 standalone, or an upsell with the abatement packet, fits given the free government routes. Circuit Breaker estimates are tax-information output; Massachusetts doesn't license tax preparers at the state level (not verified here), but avoid "tax preparation" framing.

### Gaps
- I found no count of registered Massachusetts short-term rental operators.
- I did not compile the list of towns adopting the residential exemption, or personal exemption clauses (41C, 17D, 22), for Massachusetts.
- I found no Circuit Breaker take-up or claimant data, and no Ownwell exemption-service fee.
- The search budget ran out before I could check paid circuit-breaker or exemption-filing analogs in other states.

---

## Q9. Ranking: which 4–6 Massachusetts self-serve products are best?

### Takeaway
1. **Massachusetts property tax abatement packet with exemptions check.** Clear first. Proven pricing, high per-customer savings, free statewide data, low UPL risk, but competition from a national $49 DIY packet and a sharp January deadline.
2. **Landlord §15B deposit-compliance kit.** Recurring, treble-damages fear drives demand, thin free competition.
3. **Tenant deposit recovery plus 93A demand plus small claims packet.** Free tools exist, so differentiate on analysis and bundling.
4. **General 93A demand-letter and small claims packet.** Massachusetts-specific requirement, but low willingness to pay.
5. **EZDriveMA and parking appeal letter builder.** High volume, low value.
- Discard: homestead (free form, scam stigma, real-property instrument) and short-term rental compliance (Airbnb remits; MyLodgeTax exists).

### Cited Findings
- **Abatement:** Per-customer value about $880/yr in AppealDesk's example; Ownwell average $774/yr in core markets; DIY packets $49 (AppealDesk) to $149 (TaxProper 2020); contingency 25–35%. — [AppealDesk MA](https://www.appealdesk.com/compare/best-massachusetts-property-tax-appeal-services); [VCA Online](https://www.vcaonline.com/news/2026021908/ownwell-raises-50m-launches-national-service-to-streamline-property-tax-appeals-and-make-home-ownership-more-affordable/); [TechCrunch](https://techcrunch.com/2020/06/05/taxproper-raises-2m-to-automate-getting-your-property-taxes-lowered); [Money Crashers](https://www.moneycrashers.com/ownwell-review/)
- **Abatement data:** MassGIS statewide parcels are free, refreshed January 1 and July 1. — [mass.gov MassGIS](https://www.mass.gov/info-details/massgis-data-property-tax-parcels)
- **Deposit penalties:** Landlord treble damages plus attorney's fees under §15B(7). — [c.186 §15B](https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15B)
- **Free tenant tools:** CourtFormsOnline and MassLegalHelp Form 6. — [MassLegalHelp](https://www.masslegalhelp.org/sites/default/files/2025-02/Handout%203%20Security%20Deposits%202025.pdf)
- **93A demand:** 30-day pre-suit demand requirement. — [c.93A §9](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter93A/Section9)
- **Parking and tolls:** Boston issues 1.2–1.5M tickets a year with about 10% disputed; WinIt charges 50% only if dismissed. — [BINJ](https://binj.news/2021/11/23/more-tickets-more-tows-more-fees/); [App Store](https://apps.apple.com/us/app/winit-fight-your-tickets/id929918279)
- **Homestead:** Free forms, $35–$36 recording, registry scam warnings. — [Salem Deeds](https://www.salemdeeds.com/SalemDeeds/DownLoadFile.aspx?newsid=120); [Patch/Norfolk](https://patch.com/massachusetts/stoughton/norfolk-register-deeds-promotes-homestead-act)
- **Short-term rentals:** Airbnb remits Massachusetts taxes; MyLodgeTax costs $27/month/property. — [Airbnb Help 2587](https://www.airbnb.com/help/article/2587); [Avalara MyLodgeTax](https://www.avalara.com/mylodgetax/en/index.html)

### Inferences
**1. Abatement packet with exemptions check.**
- Price: $49–$79 flat, or $29 plus an optional "pay after filing" tier. A "refund if your town rejects the filing as late or incomplete" guarantee is automatable; refund on denial needs the customer to upload the decision.
- Demand: about 17k–35k residential filers a year (estimate), most of whom have never filed.
- Build: parcel/comparables engine on MassGIS, a 351-town deadline table, Form 128 PDF fill, Boston information form, and ATB informal-procedure packet as a second-stage upsell.
- Timing: As of October 10, 2026, the FY2027 season opens late December 2026 and Boston's deadline is February 1, 2027, so a launch by early December 2026 is feasible.
- Risks: AppealDesk's existing $49 Massachusetts coverage; Ownwell's national packet; appraisal-licensing wording.

**2. Landlord §15B compliance kit.**
- Price: $49–$99 one-time, or about $5/unit/month (follow 940 CMR 38 for subscriptions).
- Build: fully automated documents and reminders.
- UPL: low (statutory compliance paperwork).
- Demand: unquantified.

**3. Tenant deposit recovery kit.**
- Price: $19–$39.
- Competition: free tools cover the basic letter; paid value is the violation checker, treble calculator, 93A option and small claims packet.
- UPL: moderate; keep it informational.

**4. 93A demand letter and small claims packet.**
- Price: $29–$49.
- Positioning: Massachusetts-only legal requirement, but the Trial Court's free online tools and eFileMA cover filing, and DoNotPay's FTC case shows the marketing risk.

**5. EZDriveMA and parking appeal builder.**
- Price: $5–$15 flat.
- Fit: high volume, low value; possibly a lead-generation or SEO play rather than a revenue core.

**Discard:** Homestead and short-term rental compliance (reasons above). Circuit Breaker and exemptions fold into product 1 as an upsell.

**Cross-cutting design rules:**
- The customer signs and files.
- Disclaim "not a lawyer / not legal advice / not an appraisal."
- Have a Massachusetts attorney review templates once.
- Make no "lawyer-equivalent" or unsubstantiated success claims (FTC DoNotPay).
- Show the full price up front and make cancellation easy (940 CMR 38).
- Use Massachusetts venue and a complaint channel (the NC 84-2.2-style checklist).

### Gaps
- The ranking rests on estimated volumes. I found no statewide abatement counts, deposit-dispute counts or consumer-only small claims counts.
- I did not test competitors' actual Massachusetts output quality (AppealDesk, Ownwell packet).
- I did not get a legal opinion on UPL or appraisal licensing for these exact products. Have Massachusetts counsel review before launch.
- The web-search budget ran out before I could check paid circuit-breaker or exemption analogs, Massachusetts motor-vehicle excise abatement tools, and Rocket Lawyer/LegalZoom letter pricing.
