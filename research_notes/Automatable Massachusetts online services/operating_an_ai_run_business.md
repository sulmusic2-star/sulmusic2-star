# Operating an AI-Built, AI-Run Online Business as a Solo Massachusetts Owner (as of October 10, 2026)

Scope note: Massachusetts (MA) specifics are labeled "MA"; national/US data is labeled "US" or "National". Several official mass.gov and sec.state.ma.us pages returned HTTP 403 to automated fetches during this research, so some MA figures come from mass.gov search snippets or reputable third-party summaries. Each one is flagged where that applies. Nothing here is legal or tax advice.

## 1. Massachusetts business setup costs and duties (entity, DBA, sales tax, income tax, Stripe Tax)

### Takeaway
A MA single-member LLC costs about $500 to form and $500 every year after that, with a $20 surcharge when filed online. That makes it one of the most expensive LLC states, and forming out of state doesn't avoid the fee, because operating in MA triggers a $500 foreign registration. A sole proprietor can instead file a city/town business certificate (about $65 in Boston, renewed every 4 years). MA taxes SaaS and prewritten software at 6.25% whether it's sold B2B or B2C, and remote sellers must register once they pass $100K in MA sales. Most third-party guides say e-books and music-style digital goods are not taxed. The 4% surtax only applies above $1,107,750 of income (2026), so it won't matter for a micro-business.

### Cited Findings
**LLC formation and annual report (MA)**
- Certificate of Organization filing fee is $500. Filing online or by fax adds an automatic $20 expedite fee, for $520 total. — [Zenind](https://www.zenind.com/help/post/cost-to-start-a-massachusetts-llc-filing-fees-annual-reports-and-hidden-expenses); [LLC University](https://www.llcuniversity.com/massachusetts-llc/costs/)
- The LLC Annual Report costs $500 per year, or $520 online. It is due on or before the anniversary date of the original Certificate of Organization. One aggregator lists "November 1" instead, which conflicts with the anniversary rule. — [LLC University](https://www.llcuniversity.com/massachusetts-llc/costs/); [Zenind](https://www.zenind.com/help/post/massachusetts-llc-filing-fees-and-requirements-a-complete-guide); [Harbor Compliance agency page](https://www.harborcompliance.com/agency/massachusetts-secretary-of-the-commonwealth-corporations-division)
- Missing the annual report two years in a row can lead to administrative dissolution. — [Zenind](https://www.zenind.com/help/post/cost-to-start-a-massachusetts-llc-filing-fees-annual-reports-and-hidden-expenses)
- A foreign LLC (for example, one formed in Wyoming or Delaware) that transacts business in MA must register within 10 days, and the registration fee is reported at $500. — [limitedliabilitycompanycenter.com](https://www.limitedliabilitycompanycenter.com/massachusetts/)
- Verification caveat: the sec.state.ma.us fee page could not be fetched (it returned an empty page or 403). The $500 figures are consistent across 5+ third-party sources but should be confirmed on the Secretary of the Commonwealth's fee schedule.

**Sole proprietor "doing business as" (business certificate, MA municipal)**
- Boston: the filing fee is $65, the certificate must be renewed every 4 years, and renewal costs the same $65. The form must be notarized and filed in person or by mail. There is no online filing. — [City of Boston](https://www.boston.gov/node/16626546); [Boston New Business Certificate Form](https://boston.gov/sites/default/files/file/2024/07/New%20Business%20Certificate%20Form%201.pdf)
- Late penalty: up to $100 per month, capped at $300 total (M.G.L. c. 110 §5). Third-party guides add a $35 non-resident surcharge in Boston, which I could not confirm on the city's own page. Fees in other towns are commonly cited at $50–$65. — [StartupSavant](https://startupsavant.com/how-to-get-a-dba/massachusetts); [TRUiC](https://howtostartanllc.com/dba/dba-massachusetts)

**Sales/use tax on software and SaaS (MA)**
- The DOR fact sheet for 830 CMR 64H.1.3 (search snippet) says prewritten software sold to a customer in MA is "deemed a transfer of tangible personal property subject to the sales or use tax regardless of the method of delivery." Its list of taxable transfers includes "rights to use software installed on a remote server," which is SaaS. Custom software "will generally continue to be treated as nontaxable personal service transactions." — [Mass.gov 830 CMR 64H.1.3 fact sheet](https://www.mass.gov/regulations/830-CMR-64h13-reg-fact-sheet) (fetch blocked, 403; content from search snippet); background in [TIR 13-10](https://www.mass.gov/technical-information-release/tir-13-10-sales-and-use-tax-on-computer-and-software-services-law)
- Rate is 6.25% with no local sales tax. MA "taxes SaaS sold to businesses and consumers alike." Registration is through MassTaxConnect. Business customers with users in several states can apportion the tax (Form ST-12 / Software Apportionment Certificate), and apportionment "may not be based on the location of the servers." — [Kintsugi MA SaaS guide](https://trykintsugi.com/blog/massachusetts-saas-sales-tax)
- The DOR's 2013 directive on distinguishing taxable prewritten software from non-taxable services was a "working draft for practitioner comment," and I found no evidence it was finalized. EY's December 2024 SALT summary mentions a newer draft regulation with examples on bundled software and services. Whether that draft was adopted is unconfirmed. — [Mass.gov working draft directive](https://www.mass.gov/directive/working-draft-directive-13-xx-criteria-for-determining-whether-a-transaction-is-a-taxable); [EY Tax News](https://taxnews.ey.com/news/2024-2326-state-and-local-tax-weekly-for-november-15-and-november-29)
- Remote-seller economic nexus: register and collect if MA sales exceeded $100,000 in the prior or current calendar year. There is no transaction-count test. The rule is 830 CMR 64H.1.9. — [Kintsugi](https://trykintsugi.com/blog/massachusetts-saas-sales-tax); [Kintsugi MA guide](https://trykintsugi.com/sales-tax-guides/usa/massachusetts)
- For an MA-based seller, physical presence in MA already creates nexus, so the $100K threshold matters only for out-of-state sellers. This is an inference, but standard. See Inferences.

**Digital products other than software (MA)**
- Most compliance-vendor guides say MA does not tax digital goods such as e-books and digital music, while prewritten software and SaaS are taxable. One Boston-focused guide is an outlier and says digital products are taxable at 6.25%. — [Numeral](https://www.numeral.com/blog/saas-sales-tax-massachusetts); [Kintsugi MA guide](https://trykintsugi.com/sales-tax-guides/usa/massachusetts); contradicted by [Quaderno Boston guide](https://quaderno.io/guides/boston-sales-tax)

**Income tax (MA)**
- The 4% surtax ("millionaires' tax") threshold for tax year 2026 is $1,107,750. It was $1,083,150 for 2025, $1,053,750 for 2024 and $1,000,000 for 2023. The DOR certified the 2026 figure on November 20, 2025. — [Mass.gov 2026 Form 1-ES instructions](https://www.mass.gov/doc/2026-form-1-es-estimated-tax-payment-vouchers-instructions-and-worksheets/download); [Mass.gov Massachusetts Tax Rates](https://www.mass.gov/info-details/massachusetts-tax-rates); [Comptroller surtax certification](https://arizent.brightspotcdn.com/5d/1e/d6f17b52459a8c75563195e0bfdc/fy26-period-4-surtax-certification.pdf)
- Several secondary sites still list stale thresholds ($1,000,000 or $1,083,150) for 2026. Rely on the DOR figure. — [Mass.gov Tax Rates](https://www.mass.gov/info-details/massachusetts-tax-rates)
- The base MA personal income tax rate on most income is 5% (Part B). A single-member LLC is disregarded by default, so business profit flows to the owner's Form 1. — [Mass.gov Massachusetts Tax Rates](https://www.mass.gov/info-details/massachusetts-tax-rates) (rate listing; confirm on the page)

**Stripe Tax (US)**
- Tax Basic (pay-as-you-go) costs 0.5% per transaction where you are registered, when used with Stripe Billing, Checkout, Invoicing or Payment Links. Via API it is 50¢ per transaction, including 10 calculation calls, with 5¢ per extra call. Tax Basic covers monitoring, calculation and collection only. It does not file returns. — [Stripe Tax pricing](https://stripe.com/tax/pricing)
- Tax Complete starts at $90/month, with tiers at $90, $430, $1,000 and $1,500 per month on 1-year contracts. It includes registrations and filings: US sales tax filing in select states through TaxJar, and 90+ countries through Taxually. — [Stripe Tax pricing](https://stripe.com/tax/pricing)

### Inferences
- First-year fixed state cost: about $520 for an LLC, or about $65 for a Boston DBA. Recurring cost is about $520/yr (LLC) versus about $65 per 4 years (DBA). Over 5 years the LLC route costs roughly $2,600 in state fees alone, versus roughly $130 for a DBA. The LLC's main benefit is liability separation, which insurance partly substitutes for.
- Forming in a cheaper state doesn't help an MA resident operating from MA, because the $500 MA foreign registration plus the home-state fees cost more.
- Because the seller is based in MA, it has nexus from day one and must collect 6.25% on SaaS sold to MA customers, B2B included. Out-of-state customers only become a collection duty once the seller passes each state's own economic nexus threshold. Stripe Tax's monitoring helps here.
- A product designed as a downloadable e-book, template or report (not software) may avoid MA sales tax under the majority view. However, "access to an online tool" is SaaS and taxable. The classification question is worth one CPA consult.
- Federal self-employment tax and quarterly estimated payments (MA Form 1-ES plus federal 1040-ES) apply to profits. These are standard duties and weren't separately researched here.

### Gaps
- Could not fetch sec.state.ma.us directly. The $500/$500 LLC fees and the $20 online surcharge are confirmed only by multiple third-party sources.
- Could not confirm whether MA DOR adopted a final revised 830 CMR 64H.1.3 after the 2024 draft, or whether any 2025–2026 TIRs changed SaaS treatment.
- No official DOR source retrieved on e-book and digital-music treatment. The vendor majority view says they're exempt, with one dissenting source.
- MA sales tax filing frequency thresholds weren't retrieved.

## 2. Massachusetts privacy and data rules (WISP, breach notice, MA privacy bill status, CAN-SPAM, TCPA, ADA)

### Takeaway
Any business that stores MA residents' personal information (name plus SSN, driver's license or financial account number) must keep a written information security program (WISP) under 201 CMR 17.00. A breach triggers notice to the AG, OCABR and the affected residents under c. 93H. A comprehensive MA consumer privacy law has not been enacted as of October 2026. The Senate passed S.2619 (Sept 2025) and the House passed H.5479 (June 2026), and the bill has sat in conference committee since June 17, 2026. CAN-SPAM penalties stay at $53,088 per violation for 2026. The FCC's stricter TCPA "one-to-one consent" rule was vacated in January 2025. Website accessibility suits keep rising: 5,000+ digital accessibility suits in 2025 by UsableNet's count.

### Cited Findings
**201 CMR 17.00 (WISP) (MA)**
- The regulation applies to persons "engaged in commerce" who "collect and retain personal information in connection with the provision of goods and services or for the purposes of employment." Municipalities are excluded. — [OCABR FAQ on 201 CMR 17.00](https://www.mass.gov/doc/frequently-asked-questions-for-201-cmr-1700/download)
- The security program "must be in writing," and its scope "will vary depending on your resources, and the type of personal information you are storing." It is risk-based and modeled on the FTC Safeguards Rule. — [OCABR FAQ](https://www.mass.gov/doc/frequently-asked-questions-for-201-cmr-1700/download)
- OCABR publishes a small-business compliance checklist covering administrative, technical and physical safeguards. The checklist is "not a substitute for compliance." — [Mass.gov 201 CMR 17.00 Compliance Checklist](https://www.mass.gov/info-details/201-cmr-1700-compliance-checklist)
- Caveat: the FAQ dates from about 2010. Free WISP templates exist, including one from a Boston IT firm that advises consulting an attorney. — [PowerUp Boston WISP template](https://powerupboston.com/resources/wisp-template)

**Data breach notice, M.G.L. c. 93H (MA)**
- When a breach occurs, notice goes to the Attorney General, OCABR and affected residents. The report to the AG and OCABR must state whether the organization maintains a WISP. — [Mass.gov Requirements for Data Breach Notifications](https://www.mass.gov/info-details/requirements-for-data-breach-notifications) (fetch blocked, 403; from search snippet); [PowerUp Boston](https://powerupboston.com/blog/wisp-compliance-massachusetts-business)

**Comprehensive MA consumer privacy law (status as of October 2026)**
- Senate passed S.2619 (Massachusetts Data Privacy Act) 40–0 in September 2025. — [League of Women Voters MA](https://lwvma.org/in-big-win-senate-approves-data-privacy-act/); [Sen. Joan Lovely](https://www.senatorjoanlovely.com/senate-passes-the-massachusetts-data-privacy-act/)
- House passed its amended version, H.5479, 146–0 on June 4, 2026. The Senate non-concurred and appointed conferees (Creem, Finegold, O'Connor) on June 11, 2026. The House insisted and appointed conferees (M. Moran, Farley-Bouvier, Vieira) on June 17, 2026. The official bill history shows no later action, no accepted conference report and no enactment. — [malegislature.gov S.2619 Bill History](https://malegislature.gov/Bills/194/S2619/BillHistory)
- Key differences between the versions:
  - The Senate version banned the sale of all sensitive data and had AG-only enforcement with a 60-day cure period.
  - The House version allows the sale of sensitive data, except precise geolocation, with affirmative consent. It eliminates the cure period and adds a private right of action against "large data holders."
  - Sources: [Foley Hoag (June 2026)](https://foleyhoag.com/news-and-insights/blogs/state-ag-insights/2026/june/one-step-closer-to-a-massachusetts-data-privacy-law-comparing-the-current-house-and-senate-bills/); [TechCrunch (June 8, 2026)](https://techcrunch.com/2026/06/08/massachusetts-votes-to-pass-new-privacy-rights-bill-that-bans-sale-of-precise-location-data/); [ACLU of MA](https://www.aclum.org/campaigns-initiatives/data-privacy-now/)
- One bill tracker (FastDemocracy) displays "Became Law," but its own action list ends at the June 17 conference appointment. That label appears to be an error. — [FastDemocracy](https://fastdemocracy.com/bill-search/ma/194th/bills/MAB00082326/) versus [malegislature.gov](https://malegislature.gov/Bills/194/S2619/BillHistory)

**CAN-SPAM (US)**
- The FTC's 2025 inflation-adjusted maximum civil penalty under FTC Act §5(l) and §5(m)(1)(A)/(B) is $53,088, up from $51,744, effective January 17, 2025. CAN-SPAM violations are penalized under these provisions. — [FTC press release, Feb 2025](https://search.ftc.gov/news-events/news/press-releases/2025/02/ftc-publishes-inflation-adjusted-civil-penalty-amounts-2025)
- The FTC made no adjustment for 2026 and continues to apply the 2025 levels, because the government shutdown prevented BLS from publishing the October 2025 CPI-U data. — [Federal Register public inspection 2026-18853](https://public-inspection.federalregister.gov/2026-18853.pdf) (per search summary)
- Third-party compliance sites say the penalty applies per non-compliant email. I could not confirm that wording in FTC text. — [Prospeo](https://prospeo.io/s/can-spam-penalties-per-email)

**TCPA (US; SMS and calls)**
- On January 24, 2025, the 11th Circuit (Insurance Marketing Coalition v. FCC) vacated the FCC's "one-to-one" consent rule days before its January 27, 2025 effective date. The prior "prior express written consent" standard governs marketing texts and autodialed or prerecorded calls. — [Kelley Drye](https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/eleventh-circuit-vacates-tcpa-11-consent-rule); [Mintz (May 2025)](https://www.mintz.com/insights-center/viewpoints/2776/2025-05-02-telephone-and-texting-compliance-news-litigation-update)
- Many carriers and texting platforms still require businesses to show one-to-one style consent as a business rule. — [Nelson Mullins](https://www.nelsonmullins.com/insights/alerts/fcc-download/all/the-1-to-1-consent-rule-is-no-more)
- Real-world example: Medvi, the AI-heavy telehealth company profiled in Section 6, faces two lawsuits alleging that unsolicited texts and emails violated spam laws, which Medvi denies. — [Yahoo Finance](https://finance.yahoo.com/sectors/healthcare/articles/1-8-billion-startup-just-190000841.html)

**ADA website accessibility (US)**
- UsableNet counted more than 5,000 digital accessibility lawsuits in 2025 across federal and key state courts, including 2,019 in the first half. 1,427 of the 2025 suits targeted companies previously sued. A growing share involve sites that already use accessibility overlays or widgets. Caveat: UsableNet sells remediation services. — [UsableNet via Newswire](https://www.newswire.com/news/digital-accessibility-lawsuits-surge-in-2025-22618502)
- Seyfarth Shaw's federal-only count of website suits is 3,117 in 2025, up 27% from 2,452 in 2024. The two trackers measure different things. — reported in [TestParty](https://testparty.ai/blog/ada-lawsuit-trends-ecommerce-2025-2026-data) and [Fox Rothschild event page](https://www.foxrothschild.com/events/ada-website-lawsuit-trends-what-2025-filings-mean-for-2026) (secondary)
- A secondary summary says only 36% of companies sued in 1H 2025 had revenue above $25M, so most were small or mid-sized. Not confirmed in UsableNet's primary report. — [AccessibilityChecker](https://www.accessibilitychecker.org/blog/ada-website-compliance-lawsuits/)

### Inferences
- The cheapest compliance posture for an AI-run micro-business:
  - Never store SSNs, driver's license numbers or card numbers. Let Stripe hold payment data.
  - That keeps most 201 CMR 17.00 exposure limited to a short WISP. A WISP is still prudent, because a breach report must say whether you have one.
- If the MA privacy act is enacted, its applicability thresholds will decide whether a micro-business is covered. Comprehensive state privacy laws typically exempt small processors, but the thresholds in the final MA text are unknown because conference is unresolved. Monitor it.
- Email marketing to consenting users with a working unsubscribe is low-risk. SMS marketing carries the highest litigation risk, given TCPA private suits plus carrier rules, and is best avoided or tightly consented.
- WCAG 2.1 AA conformance, which an AI coding agent can build in and test, is a cheaper defense than overlays. Overlays don't prevent suits.

### Gaps
- The exact c. 93H notice timing language ("as soon as practicable and without unreasonable delay"), the credit-monitoring duration and the definition details were not retrieved from primary text, because the mass.gov page returned 403.
- The applicability thresholds in S.2619/H.5479 (number of consumers or revenue) weren't extracted.
- No info on whether the conference committee met after the July 31, 2026 end of formal sessions, or whether the bill can still pass in informal session.

## 3. What an AI agent can operate versus what the human owner must do; platform rules on automation and AI content

### Takeaway
The legal and financial "root" of the business has to be a verified human. Payment processors, banks, ad platforms and the state all require a real person: Stripe requires a US individual's SSN as the business representative, and Google Ads can demand identity documents before an appeal. Agents can increasingly transact. Stripe now offers agent wallets and protocols for agent-created accounts, but spending still defaults to human approval. Anthropic's own Project Vend found agents capable but "not robust": they're easily manipulated into discounts, giveaways and near-illegal contracts. Google's spam policy (updated August 28, 2026) explicitly names "using generative AI tools… to generate many pages without adding value," which makes mass programmatic AI SEO a direct enforcement risk.

### Cited Findings
**Identity and KYC (US)**
- Stripe: "Stripe is required by its regulators to collect certain information from account holders in order to prevent abuse of the financial system." It covers the individual opening the account, the business, and "any individuals who ultimately own or control that business." Account holders must "promptly update" changes. — [Stripe KYC obligations](https://support.stripe.com/questions/know-your-customer-obligations)
- For sole-proprietor accounts, the business representative must be a US individual. Stripe expects the SSN "as issued by the Social Security Administration and what you would list on your US tax return." — [Stripe support: sole proprietorship tax ID requirements](https://support.stripe.com/questions/business-rep-owner-tax-id-requirements-for-us-companies-sole-proprietorship-accounts)
- Stripe verifies legal entity name, type (sole prop or LLC), EIN, SSN/ITIN and business address for US accounts. — [Stripe: requirements for a US Stripe account](https://support.stripe.com/questions/requirements-for-having-a-us-stripe-account)
- Secondary: 25%+ owners must be listed with name, DOB, address and SSN. Reps provide the last 4 of their SSN plus contact details and a payout bank account. — [Flex integration guide](https://docs.withflex.com/developer-guides/integration/stripe/payouts-and-verification)

**Agent payments infrastructure (US, 2026)**
- Stripe's updated Link wallet lets users issue virtual cards to AI agents with spending controls. By default, users "get a notification to approve the spend request." Stripe says it will later let users set limits or let agents act without approval. — [TechCrunch, Apr 30, 2026](https://techcrunch.com/2026/04/30/stripe-link-digital-wallet-ai-agents-shopping/)
- Stripe's Machine Payments Protocol enables programmatic agent payments, including microtransactions and recurring payments. — [Stripe blog: Machine Payments Protocol](https://stripe.com/blog/machine-payments-protocol)

**Ad platform verification (US)**
- Advertisers suspended for policy violations "may be prompted to successfully complete this verification in order to appeal," and the accounts stay suspended until the appeal is granted. False information during verification leads to revocation and possible suspension. — [Google Ads Help: About verification](https://support.google.com/adspolicy/answer/9703665); [PPC Land](https://ppc.land/google-emphasizes-consequences-for-false-verification-information/)
- For billing suspensions, Google may require payment-method verification within 30 days before it reviews the appeal. — [Google Ads Help: billing and payment suspensions](https://support.google.com/google-ads/answer/13704200)
- Secondary: verification usually asks for an identity document and a description of the business. Failures commonly come from mismatches between payment-profile name, legal documents and the displayed advertiser name. — [Ivitskiy guide](https://ivitskiy.com/blog/en/google-ads-advertiser-verification/)

**Evidence on agent reliability: Anthropic Project Vend phase 2 (published December 2025)**
- With Claude Sonnet 4/4.5, a CRM, payment links and a "CEO" agent, the shop stabilized and "weeks with negative profit margin were largely eliminated." It expanded to SF, NY and London. Yet "The gap between 'capable' and 'completely robust' remains wide." — [Anthropic: Project Vend phase two](https://www.anthropic.com/research/project-vend-2)
- What humans still did:
  - Physical stocking and delivery. Agents "still needed a great deal of human support."
  - Purchases required human check-in, because the agent had no payment interface.
  - Staff intervened in difficult customer situations.
  - Source: [Anthropic](https://www.anthropic.com/research/project-vend-2)
- Failure modes:
  - The CEO agent approved customer requests about 8 times as often as it denied them.
  - Agents nearly signed an illegal forward onion-price contract until a staffer flagged the law.
  - Agents proposed paying a security worker $10/hour, below California minimum wage.
  - Manipulation via a fake vote installed an "imposter CEO."
  - Source: [Anthropic](https://www.anthropic.com/research/project-vend-2)
- In a Wall Street Journal adversarial test, about 70 journalists twice talked the agent into setting all prices to zero and giving away items, including a PS5 and a live fish, leaving it more than $1,000 in the red. — [The Decoder](https://the-decoder.com/anthropics-ai-store-makes-money-while-debating-eternal-transcendence/); [Gigazine](https://gigazine.net/gsc_news/en/20251219-anthropic-project-vend-phase-two)

**Google Search spam policy on AI and programmatic content (US/global)**
- Definition: "Scaled content abuse is when many pages are generated for the primary purpose of manipulating search rankings." Examples include:
  - using generative AI to produce many pages without adding user value
  - scraping feeds or search results, including synonymizing or translating
  - stitching content together without adding value
  - creating multiple sites to hide scale
  - keyword-stuffed nonsense pages
  - The page was last updated August 28, 2026. — [Google Search Central spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- The policy also covers site reputation abuse (third-party content riding a host's signals) and expired domain abuse. — [Google Search Central](https://developers.google.com/search/docs/essentials/spam-policies)
- Google's spam policies now officially apply to AI Overviews and AI Mode. — [PPC Land](https://ppc.land/google-spam-policies-now-officially-cover-ai-overviews-and-ai-mode-in-search)
- Google publishes no page-count threshold. Method (AI or human) matters less than purpose. — [PPC Land](https://ppc.land/scaled-content-abuse/); [Return On Now](https://returnonnow.com/?p=1831877)
- An August 2026 spam update rolled out August 18–21, 2026. Operators reported anecdotal losses on mass-produced AI articles, and Google did not say it targeted AI content. — [GSQi case studies](https://gsqi.com/marketing-blog/august-2026-google-spam-update-case-studies/)
- A single vendor blog claims the March 2026 core update primarily targeted scaled content abuse. This is uncorroborated. — [SEOQuick](https://seoquick.com.ua/en/ai-content-google-penalty-2026/)

**Community platforms (Reddit)**
- Reddit's long-standing principle: "It's perfectly fine to be a Redditor with a website, it's not okay to be a website with a Reddit account." Spam enforcement looks at account patterns. The "9:1" ratio is community custom, not formal policy. Many subreddits added explicit AI rules (more than doubled in one year, per a CHI 2025 study cited secondhand). These are secondary sources. — [DEV Community summary](https://dev.to/sh20raj/reddit-self-promotion-framework-how-to-post-smart-and-stay-unbanned-1kfg)

**Self-described limits of a high-profile "AI-run" business**
- Nat Eliason's "Felix" (an OpenClaw agent) "needs Nat for hard judgment calls, strategy shifts, and novel situations," and the agent can't get on calls. — [Let's Data Science](https://letsdatascience.com/news/openclaw-operates-businesses-using-ai-agents-bf26ffe1)
- Polsia's founder said AI ran its fundraising and he "only appeared to sign the documents." Legal signature still required a human. — [AIN.ua](https://en.ain.ua/2026/05/25/ai-startup-polsia-with-no-employees-raised-30m-in-funding/)

### Inferences
Human-only duties (cannot be delegated to the agent):
- KYC and identity for Stripe, the bank and the ad platforms, including SSN and ID documents
- Being the LLC organizer and registered agent, or hiring a registered agent
- Signing contracts and terms
- Receiving and responding to legal notices: demand letters, ADA suits, DMCA, AG inquiries
- Approving spend above a set limit
- Owning the root credentials and 2FA for domain registrar, hosting, email, Stripe and Google
- Tax filings and attestations
- Handling chargebacks and disputes that need judgment
- Being the human escalation path for support

What an agent can realistically operate day to day:
- Writing and deploying code, monitoring and fixing bugs
- Generating and updating content
- Drafting support replies and handling tier-1 tickets
- Running data pipelines and scraping within terms of service
- Sending transactional email
- Drafting marketing copy
- Reconciliation reports

Project Vend shows that any agent with pricing, refund or discount authority needs hard guardrails: caps, required checks and human approval above thresholds. It also shows that customer-facing agents get socially engineered.

Programmatic SEO is still viable only if each page carries unique, useful data, for example aggregated MA-specific public records with real utility. AI-paraphrased template pages at scale are the exact pattern Google names.

### Gaps
- I didn't find explicit Stripe or bank terms banning "fully automated" account operation. The binding constraint found is KYC: a verified human must be responsible.
- I didn't retrieve app store (Apple/Google Play) developer identity rules or Google Workspace and Gmail rules on automated account creation.
- No primary Reddit Help Center text retrieved on bots or AI disclosure.

## 4. Customer acquisition without sales calls (SEO, ads, cold email, communities, directories) and conversion benchmarks

### Takeaway
SEO is slow and uncertain for a new site. Ahrefs' May 2025 update found only 1.74% of newly published pages reach Google's top 10 within a year, and the average #1 page is 5 years old. Google Ads average CPC was about $5.26–$5.42 in 2025, with legal, dental and home-services terms near $8. Cold and bulk email must meet Gmail, Yahoo (Feb 2024) and Microsoft (May 2025) authentication rules and stay under a 0.3% spam rate. Self-serve SaaS benchmarks: about 2.5–8.5% of visitors start a trial, and about 18% (no card) to about 49% (card required) of trials convert, mostly per one firm's data.

### Cited Findings
**SEO time to rank (national/global)**
- Ahrefs (May 2025 update of its 2017 study):
  - Only 1.74% of newly published pages ranked in the top 10 within a year, down from 5.7% in 2017.
  - 72.9% of top-10 pages are 3+ years old, up from 59% in 2017.
  - The average #1 page is 5 years old, versus 2 years old in 2017.
  - Low-volume keywords can rank relatively quickly.
  - Source: [Ahrefs](https://ahrefs.com/blog/how-long-does-it-take-to-rank/)
- In the 2017 study, the "lucky" pages that reached the top 10 mostly did so in about 61–182 days. Higher Domain Rating sites performed better. — [Ahrefs](https://ahrefs.com/blog/how-long-does-it-take-to-rank/)

**Google Ads costs (US)**
- WordStream/LocaliQ (over 16,000 campaigns): average CPC $5.42, up from $4.66. Another version of the benchmark reports $5.26 CPC and a 7.52% conversion rate (June 2025 LocaliQ). The two figures likely come from different report editions. — [Search Engine Land](https://searchengineland.com/google-ads-costs-keep-rising-but-conversion-rates-improved-in-2025-477927); [Search Engine Land (earlier)](https://searchengineland.com/google-ads-costs-rise-again-but-conversions-improve-report-455663)
- Industry CPCs (secondary aggregator): legal $8.58, dental $7.85, home improvement $7.85, arts and entertainment $1.60, restaurants $2.05, travel $2.12. Conversion rates: automotive 14.67%, finance and insurance 2.55%. — [Digital Gravity summary](https://www.digitalgravity.ae/blog/?p=5305) (verify against the WordStream primary report)

**Email deliverability rules (US/global mailbox providers)**
- Gmail requirements, effective February 1, 2024:
  - All senders: SPF or DKIM, valid forward and reverse DNS, TLS, and a spam rate "below 0.3%" in Postmaster Tools.
  - Bulk senders (more than 5,000 messages per day to Gmail): SPF, DKIM and DMARC (p=none is allowed), From-domain alignment, and one-click unsubscribe (List-Unsubscribe-Post plus an HTTPS List-Unsubscribe) with a visible unsubscribe link.
  - The best-practice spam rate is below 0.10%.
  - Source: [Google Workspace Admin Help: Email sender guidelines](https://support.google.com/a/answer/81126)
- Yahoo adopted parallel requirements at the same time, and secondary sources say unsubscribes must be honored within about 2 days. — [Bounteous](https://www.bounteous.com/insights/2024/01/31/2024-gmail-and-yahoo-deliverability-changes/); [Mailgun](https://www.mailgun.com/blog/deliverability/gmail-yahoo-webinar-key-takeaways/)
- Microsoft (Outlook.com, Hotmail, Live) began enforcing SPF, DKIM and DMARC for senders of 5,000+ per day on May 5, 2025. Sources conflict on junk-first versus outright rejection (error 550 5.7.515). Microsoft 365 enterprise mail is not covered. — [dmarcian](https://dmarcian.com/microsoft-enforces-spf-dkim-dmarc/); [Egressif](https://egressif.io/resources/sender-requirements/microsoft)

**Self-serve conversion benchmarks (national, mostly B2B SaaS)**
- First Page Sage (86 SaaS companies, Q1 2022–Q3 2025, via secondary summaries):
  - Opt-out trials (card required): about 2.5% visitor-to-trial and 48.8% trial-to-paid.
  - Opt-in trials (no card): about 8.5% visitor-to-trial and 18.2% trial-to-paid.
  - Freemium: about 13.3% visitor-to-signup and 2.6% free-to-paid.
  - Sources: [Powered by Search](https://www.poweredbysearch.com/learn/b2b-saas-trial-conversion-rate-benchmarks/); [Shno](https://www.shno.co/marketing-statistics/free-trial-conversion-statistics)
- Userpilot (2025): B2B SaaS trial conversion is typically 15–30%, with top performers at 35–45%. A ChartMogul / Growth Unhinged / ProductLed report (January 2026) shows much lower rates. — [Userpilot](https://userpilot.com/blog/free-trial-conversion-rate/)

**Communities and partnerships**
- On Reddit, account patterns of mostly self-links get treated as spam. See Section 3. — [DEV Community](https://dev.to/sh20raj/reddit-self-promotion-framework-how-to-post-smart-and-stay-unbanned-1kfg)

### Inferences
- Rough paid-acquisition arithmetic: at about $5 CPC, an 8.5% visitor-to-trial rate and an 18% trial-to-paid rate (no card), 1 customer costs about 65 clicks, or about $330.
  - That is only viable for products priced at roughly $30+/month with low churn, or for one-time purchases above about $300.
  - For legal or home-services keywords (about $8 CPC), customer acquisition cost roughly doubles. This is illustrative arithmetic, not a benchmark.
- SEO should be treated as a 6–24 month bet. Low-competition, long-tail, MA-specific local queries are the realistic early wins, since low-volume keywords rank faster.
- Cold B2B email at low volume (under 5,000 per day) still needs SPF and DKIM and a sub-0.3% complaint rate. Sending from a separate domain protects the main domain's reputation. CAN-SPAM rules (Section 2) apply to every commercial email.
- Channels that suit "no sales calls" and an AI operator:
  - long-tail SEO built on genuinely unique data
  - integrations and marketplace listings
  - niche directories
  - helpful participation in communities, where the human owner should own the account
  - small, tightly targeted Google Ads tests

### Gaps
- No credible 2025–2026 cold-email reply-rate benchmarks retrieved.
- No quantitative data on directory or marketplace listings (Product Hunt, G2, Capterra) as acquisition sources for micro-SaaS.
- Could not retrieve WordStream's primary report. Category CPCs for "business services" and "software" were not found.
- Reddit Ads CPC data not researched.

## 5. Ongoing operating costs (hosting, LLM APIs, scraping, email, insurance, compliance tools)

### Takeaway
Infrastructure for a small automated web business can run under $100/month. Examples: Vercel Pro $20 or Cloudflare Workers $5, Resend Pro $20 or Postmark $15, Firecrawl $16–$83, Claude Pro or Max $20–$200 for the coding agent, and modest LLM API spend. Insurance (tech E&O, which often includes cyber) adds about $70–$180/month. Stripe Tax adds 0.5% of taxed transactions. The MA LLC report adds about $43/month amortized.

### Cited Findings
**Hosting**
- Vercel:
  - Hobby is $0 but "for personal, non-commercial use." It cannot host a commercial business.
  - Pro is $20/month per seat, includes a $20 usage credit and 1 TB/month Fast Data Transfer (then from $0.15/GB). Function invocations start at $0.60 per 1M.
  - Source: [Vercel pricing](https://vercel.com/pricing)
- Cloudflare Workers:
  - Free plan: 100,000 requests per day.
  - Paid plan: $5/month minimum for 10M requests and 30M CPU-ms per month, then $0.30 per additional 1M requests and $0.02 per 1M CPU-ms. No bandwidth charges.
  - D1 on Paid: 25B rows read and 50M rows written per month included, with 5 GB storage.
  - R2: 10 GB-month free, then $0.015/GB-month, with free egress.
  - Source: [Cloudflare Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/)

**Transactional and marketing email**
- Resend:
  - Free: 3,000 emails/month, capped at 100 per day.
  - Pro: $20/month for 50,000 emails, or $35/month for 100,000. Overage is $0.90 per 1,000.
  - Marketing: free up to 1,000 contacts, $40/month for 5,000 contacts.
  - Source: [Resend pricing](https://resend.com/pricing)
- Postmark: free developer tier of 100 emails/month. Basic is $15/month, Pro $16.50 and Platform $18, each for 10,000 emails. Overage is $1.80, $1.30 and $1.20 per 1,000 respectively. — [Postmark pricing](https://postmarkapp.com/pricing)

**LLM API (as listed on claude.com/pricing, fetched October 10, 2026)**
- Per million tokens, input / output:
  - Opus 5.5: $4 / $20
  - Sonnet 5.5: $2 / $10
  - Haiku 5.5 (prompts up to 100K tokens): $0.10 / $0.50
  - Haiku 5.5 (prompts over 100K tokens): $0.50 / $2.50
  - Cache reads are much cheaper: Sonnet $0.10, Haiku $0.01.
  - "Save 50% with batch processing."
  - Source: [Claude pricing](https://claude.com/pricing)
- Claude subscription plans for the coding agent: Pro is $20/month billed monthly ($17/month billed annually) and Max starts "from $100" per month. Both include Claude Code. — [Claude pricing](https://claude.com/pricing)

**Scraping and data**
- Firecrawl:
  - Free: 1,000 credits (about 1,000 pages).
  - Hobby: $16/month annual ($19 monthly) for 5,000 pages.
  - Standard: $83/month annual for 100,000 pages.
  - Growth: $333/month annual for 500,000 pages.
  - Source: [Firecrawl pricing](https://www.firecrawl.dev/pricing)

**Insurance (US, Insureon customer averages, not quotes)**
- Tech E&O (often bundled with cyber), for a $1M/$1M policy with a $2,500 deductible:
  - Software developers: about $111/month ($1,330/yr)
  - SaaS companies: about $91/month
  - Web developers: about $68/month
  - Annual range: about $500 to $9,000+
  - Sources: [Insureon software developers](https://www.insureon.com/technology-business-insurance/software-developers/cost); [Insureon SaaS](https://insureon.com/technology-business-insurance/saas-companies/cost); [Insureon web developers](https://insureon.com/technology-business-insurance/web-developers/cost); [Insureon IT](https://insureon.com/technology-business-insurance/cost)
- Standalone cyber: about $145/month small-business average and about $148–$179/month for IT businesses. The pages are inconsistent with each other. — [Insureon cyber](https://insureon.com/small-business-insurance/cyber-liability/cost); [TechInsurance](https://www.techinsurance.com/technology-business-insurance/cybersecurity/cost)

**Tax tooling**
- Stripe Tax: 0.5% per taxed transaction (no-code), or Tax Complete from $90/month including filing. See Section 1. — [Stripe Tax pricing](https://stripe.com/tax/pricing)

### Inferences
- Illustrative LLM cost: 1,000 summarizations per day at about 3,000 input and 300 output tokens each is about 90M input and 9M output tokens per month.
  - Haiku 5.5: about $9 + $4.50 = about $13.50/month.
  - Sonnet 5.5: about $180 + $90 = about $270/month.
  - Batch processing halves either figure.
  - These are estimates computed from list prices.
- Lean monthly stack estimate (excluding payment processing fees):
  - Hosting: $5–$20
  - Email: $15–$20
  - Scraping: $0–$83
  - Coding agent subscription: $20–$200
  - LLM API: $10–$300
  - Domain: about $1–$2 amortized (not researched)
  - Insurance: $70–$180
  - MA LLC report: about $43 amortized
  - Total: roughly $180–$850/month. Without insurance and on a DBA, it can be under $100/month.
- Payment processing fees (Stripe card fees) were not researched here and will usually be the largest variable cost after LLM usage.

### Gaps
- Stripe card processing fees, domain registration prices, uptime monitoring, error tracking and bookkeeping software costs were not retrieved.
- OpenAI and Google model prices weren't compared.
- No MA-specific insurance pricing found; Insureon figures are national averages.
- Apify and other data-provider prices weren't retrieved.

## 6. Evidence: indie and micro-SaaS revenue distributions, time to milestones, failure rates, and documented AI-built or AI-run businesses (2025–2026)

### Takeaway
Typical outcomes are small. In verified-revenue datasets, median MRR is about $170–$330. About a quarter of tracked products pass $1K MRR, and those datasets are survivor-biased upward. Successful indie products reach $1K MRR in a median of about 8 months in one small Stripe-verified sample. The headline "AI-run company" stories (Medvi, Polsia, Felix) have unaudited or company-reported numbers, and some carry regulatory controversies. The best-verified AI-era solo win is Base44: a bootstrapped side project sold to Wix for $80M in June 2025, which by then had a small team.

### Cited Findings
**Revenue distributions (national/global)**
- An analysis of 3,787 bootstrapped SaaS businesses reports that the 2025 cohort had a $168 median MRR and 23.5% earned over $1K MRR. The author notes survivorship bias, since dead projects stop being tracked. — [BigIdeasDB State of Indie SaaS Revenue 2026](https://bigideasdb.com/state-of-indie-saas-revenue-2026) (from search snippet; page fetch rate-limited)
- TrustMRR is a public leaderboard of revenue verified through read-only payment-provider connections, updated hourly.
  - A November 2025 write-up put the median MRR across tracked startups at $334.
  - Another analysis of 748 AI startups under $5K MRR found a $177 median versus a $1,539 mean, a heavy skew.
  - Platform counts conflict (840+ in the API docs, "6,000–8,000+" per third parties).
  - Sources: [Quasa: hard numbers from TrustMRR](https://quasa.io/media/startup-reality-the-hard-numbers-from-trustmrr); [BigIdeasDB TrustMRR](https://bigideasdb.com/trustmrr); [TrustMRR API docs](https://trustmrr.com/docs/api/list-startups); [ExitBid TrustMRR review 2026](https://exitbid.io/blog/trustmrr-review-2026)
- MicroConf State of Independent SaaS:
  - The latest published edition found is 2024, with just under 700 usable responses.
  - Exit figures cited from it: 20% of bootstrapped SaaS exits happen at $1M–$3M ARR, and 60% price at 1x–3x ARR.
  - No 2025 or 2026 edition was found.
  - Sources: [MicroConf State of Indie SaaS](https://microconf.com/state-of-indie-saas); [MicroConf 0–10K ARR](https://microconf.com/founders/0-10k-arr); [Startups for the Rest of Us ep. 721](https://www.startupsfortherestofus.com/episodes/episode-721-7-key-takeaways-from-the-2024-state-of-independent-saas-report)

**Time to milestones and failure rates (national/global)**
- A 2022 Indie Hackers analysis of Stripe-verified products found 9 months average and 8 months median to reach $1K MRR (25th percentile 5 months), on a small dataset. — [Indie Hackers](https://www.indiehackers.com/post/it-takes-5-months-to-reach-1k-in-mrr-491742f806)
- A critical analysis of Indie Hackers public revenue data counted 2,868 listed startups, of which 915 were over $10K MRR. Using a rough guess of about 30,000 bootstrapping attempts, it estimated a success rate of about 3.5%. Self-reported data is heavily survivor-biased. — [softwaredesign.ing](https://www.softwaredesign.ing/blog/real-world-stats-for-bootstrapping)
- Stripe: the top 100 AI companies on Stripe reached $1M annualized revenue in a median 11.5 months, 4 months faster than the fastest-growing SaaS companies. These companies have human founding teams and mostly venture backing, and the figures are not representative of solo businesses. — [Stripe: Indexing the AI economy](https://stripe.com/guides/indexing-the-ai-economy)

**Documented AI-built or AI-run businesses: verified versus claimed**
- **Medvi (GLP-1 telehealth, two brothers).**
  - The NYT profile of April 2, 2026 reported $401M of 2025 sales per financials the Times reviewed, a pace of $1.8B for 2026, and two full-time employees.
  - AI handled the marketing and customer-service layer. Clinical work ran through a partner platform (OpenLoop).
  - The FDA issued a warning letter on February 20, 2026, alleging misleading claims. It was part of a sweep of 30+ telehealth firms.
  - Business Insider reported affiliate marketing that used fake doctors and AI-generated testimonials.
  - The company faces two spam-law (text and email) lawsuits, which it denies.
  - Sources: [Yahoo Finance](https://finance.yahoo.com/sectors/healthcare/articles/1-8-billion-startup-just-190000841.html); [Morning Brew](https://www.morningbrew.com/stories/one-guy-built-ai-telehealth-startup-red-flags); [Tony Lee analysis](https://tonylee.im/en/blog/medvi-two-person-430m-ai-compressed-funnel); [Camino Strategy Group](https://caminostrategygroup.com/resources/medvizelthy1)
  - Status: the revenue was reviewed by the NYT but not audited publicly. Claims of "800 fake doctor accounts" come from blogs and social posts and are unconfirmed.
- **Polsia (Ben Sera; an "autonomous company" platform).**
  - Raised $30M (announced May 25, 2026) from Sound Ventures, True Ventures and others. It has one founder and no employees.
  - The company says annual revenue is "approaching $10 million." A Substack interview cites $6.3M+ annualized and notes that subscription revenue, paying users and retention were not disclosed.
  - A competitor's review claims the best-performing Polsia-run company makes about $50/month MRR. That is anecdotal and conflicted.
  - All figures are company-reported. Online commenters question the claims.
  - Sources: [AIN.ua](https://en.ain.ua/2026/05/25/ai-startup-polsia-with-no-employees-raised-30m-in-funding/); [Henry Shi Substack](https://henrythe9th.substack.com/p/how-a-solo-founder-cloned-himself); [Zilla review](https://zilla.so/blog/polsia-review)
- **Felix (Nat Eliason's OpenClaw agent).**
  - Reported lifetime revenue was $177,417 as of March 2026. Other reports say about $80K or "almost $200K."
  - The total mixes marketplace creator earnings ($80,991), guide sales and other streams.
  - Figures are self-reported from Eliason's dashboard and are unaudited. The coverage was Zapier-sponsored.
  - Sources: [Mixergy](https://mixergy.com/interviews/how-nat-eliasons-openclaw-earned-177417/amp/); [Let's Data Science](https://letsdatascience.com/news/openclaw-operates-businesses-using-ai-agents-bf26ffe1)
- **Base44 (Maor Shlomo; AI app builder).**
  - A bootstrapped side project, acquired by Wix in June 2025 for an $80M initial payment plus milestone payments through 2029.
  - It had 250,000 users in about 6 months, and 6–8 employees at acquisition.
  - Post-acquisition, CTech headlines report $50M ARR in November 2025 and $100M ARR in March 2026. I saw those as headlines only.
  - Sources: [Globes](https://en.globes.co.il/en/article-wix-acquires-israeli-vibe-coding-co-base44-1001513267); [DesignRush](https://news.designrush.com/wix-buys-ai-startup-base44-for-80m-six-month-sprint-deal); [CTech Base44 tag](https://www.calcalistech.com/tags/Base44)
  - Status: the acquisition is verified by public-company disclosure. ARR comes via Wix reporting and press.
- **Anthropic Project Vend (lab experiment).** A real AI-operated shop with human physical support. It became roughly profitable in phase 2 but remained manipulable. One CEO-agent message showed $2,649 against a $15,000 quarterly revenue target (17.7%). — [Anthropic](https://www.anthropic.com/research/project-vend-2)
- No case was found of a fully autonomous, AI-operated business with independently audited revenue. Agent payment rails exist, but the documented businesses have human founders. — [Stripe Machine Payments Protocol](https://stripe.com/blog/machine-payments-protocol); [TechCrunch](https://techcrunch.com/2026/04/30/stripe-link-digital-wallet-ai-agents-shopping/)

### Inferences
- A realistic planning baseline for a solo, AI-built niche tool:
  - The most likely outcome is under $500 MRR.
  - Roughly a quarter of tracked (already-surviving) products pass $1K MRR. Reaching $1K MRR in about 6–12 months is good performance.
  - $10K MRR is a minority outcome, single-digit percent of attempts by the rough estimates available.
- The "AI-run" success stories share a pattern:
  - A human founder makes strategy, legal, regulatory and fundraising decisions.
  - AI compresses marketing, content, code and support.
  - The biggest revenue claims are unaudited.
  - Medvi shows that aggressive automated marketing creates FDA, TCPA and spam-law exposure that lands on the human owner.
- Verified-revenue platforms (Stripe-connected leaderboards such as TrustMRR) are the best available check on claims. Their self-selection still overstates typical outcomes.

### Gaps
- No 2025 or 2026 MicroConf, Baremetrics or ChartMogul report with solo-founder revenue distributions was retrieved. The 2024 MicroConf report's revenue tables are behind a form.
- The BigIdeasDB 2026 page couldn't be fetched (HTTP 429). Its methodology (likely TrustMRR data) is unconfirmed.
- No rigorous measured failure rate exists. The 3.5% figure is a rough estimate.
- No MA-specific data on solo online businesses' revenue.
- The Freemius "State of Micro-SaaS 2025" report was found but not reviewed: [Freemius](https://freemius.com/blog/state-of-micro-saas-2025/).
