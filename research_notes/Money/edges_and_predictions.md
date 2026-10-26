# The money in the data

Written Oct 26, 2026, from three research reports (appendices A, B and C in this folder; every number there carries a source link; where a price could not be found, the reports say so instead of guessing). This page is the synthesis and the recommendation.

## The short answer

Nobody got rich from a public record. The record was always free. The people who made money read it first, turned it into something a buyer could act on, kept the history, and sold it to the one buyer who loses money by being late. That is exactly what Agenda Ahead already does for nine subjects in 315 towns, so the question is not whether the edge exists but who pays for it, how much, and how long it takes.

The closest story to ours is Curate: two founders in Madison, Wisconsin, started in 2016 scraping 7,000 town agendas and minutes into a weekly spreadsheet for contractors who kept losing bids by hearing late. Raised about $2 million, grew to 25 people and 12,000 municipalities, and sold to FiscalNote in 2021 for an undisclosed "eight-figure" sum. The buyer said it wanted the dataset. Five years, one state first, one kind of customer first.

The realistic shape of this, from every case studied: real money takes five to ten years; it is sold per organization per topic (Politico Pro launched at $3,295 a year, Quorum at $4,800, Thinknum at $16,800, PitchBook around $20,000); renewal rate is the business; and the exit, when there is one, is to a bigger data company at two to seven times revenue. One-person operations live on the same kind of feed at $40 to $500 a year per reader (Capitol Fax, Chicago Cityscape), usually with a few institutions paying far more.

"Tons of money" fast is not on the list. A business that pays well and grows into a sale is.

## 1. What our data can predict, and who pays

Appendix B ranks what an agenda line predicts by value to the buyer, how early we see it, and how reliably our data shows it. The top five, as products:

| Product | What the buyer gets, in one sentence | Buyer | Lead time | Price comparables |
|---|---|---|---|---|
| **Bylaw Outlook (MA)** | Every solar or battery bylaw and moratorium on a warrant, the day it posts, with the Attorney General's record on each clause type since 2022, so you know before Town Meeting what will stand | Solar and battery developers, their lawyers, land brokers | Weeks before the vote; AG rules 90–180 days later | $400–1,000 a seat a month, or $6K–25K a year per firm |
| **Storage Window (NY)** | Every New York town battery-storage moratorium, extension and expiry, from the first agenda that names it | Storage developers, counsel, lenders | 1–3 months before adoption | $12K–40K a year per company. Needs New York coverage first (today: 2 towns in our ledger vs ~100 with moratoria) |
| **Housing Ahead (MA, RI)** | Every 40B and MBTA-district project on a planning or zoning agenda, with units, address and hearing dates, 6–24 months before the first shovel | Contractors, suppliers, lenders, construction-lead vendors | 6–24 months | $100–200 a seat a month, or a $20K–60K data license |
| **Data-Center Ledger (MA, NY, RI)** | Every town that has discussed, proposed, voted or enacted a data-center moratorium or ban, dated and sourced, the morning the agenda posts | Developers, land investors, utilities, site-selection vendors who phone counties today | Weeks to months before the vote | $15K–50K a year enterprise feed |
| **First Notice (MA)** | The day a Planning Board puts a zoning amendment on its agenda, which parcels it touches and how many days remain to file before the first notice freezes rights | Housing and land developers, land-use attorneys, title firms | Weeks to months | $4K–12K a year per firm |

Why these work: the lead time is set by statute and is the same every time (Massachusetts c. 40A §5: referral, hearing within 65 days, 14 days' notice, then 90–180 days of AG review; New York Town Law §264; 40B's 30- and 40-day clocks). A developer who learns of a New York moratorium one hearing too late forfeits an estimated $200,000 to $2.2 million on a withdrawn project (Modo Energy). Nationally, local opposition blocked or stalled 48 data-center projects worth $156 billion in 2025 (Data Center Watch; caveats in Appendix B).

What the data cannot do yet, stated plainly:

- We read agendas, not outcomes. We can say what is coming; we cannot yet say what share of "discussion" items became moratoria, because we do not read minutes or New York local-law filings. The one outcome series we hold is the Massachusetts Attorney General record (18 of 18 solar and battery moratoria struck since June 2022; 109 of 114 regulating bylaws approved). Until the outcome table exists, we sell base rates and counts, not predictions.
- Three states, uneven depth: Massachusetts deep, New York thin, Rhode Island small. Two of the five products need New York coverage before they can be sold.
- The state is overtaking the town on the biggest projects (New York's Executive Order 62 for data centers over 50 MW; the Massachusetts single permit). Towns still decide standalone storage in New York, data centers under 50 MW, clean energy under 25 MW in Massachusetts, and all housing.
- Hedge funds are not a market. Nothing in three towns' agendas moves a REIT or a utility.

## 2. Where else the same machine could be pointed

Appendix C surveyed sixteen public-record streams. The federal and state ones (building permits, procurement, liens, court dockets, FDA/FCC/USPTO, customs, job postings) are already aggregated and sold at every price, from $1.60 per thousand rows to $50,000 contracts, and none of them use our sources. Stay out.

What is scattered across hundreds of town websites as PDFs, read by almost nobody, and months ahead of the money, is what we already crawl. Ranked:

1. **Development Ahead**: the regional project pipeline from planning-board, ZBA and conservation-commission agendas: warehouses, data centers, subdivisions, big-box retail, battery storage, cannabis, 40B, hotels, self-storage. One sentence per filing, ranked by size and stage, weekly, with alerts. Buyers: civil engineers, land-use lawyers, industrial brokers, site-work contractors, building-product reps, community banks, utilities. National keyword tools (FiscalNote/Curate, Civic IQ, Hamlet) prove the buyers exist; none writes the item in plain words for a named trade in a region. Proposed $199 a seat a month or $1,990 a year per firm.
2. **Warrant Watch**: every article on every Town Meeting warrant, parsed into type, department, dollars and funding source, plus the capital-plan items that precede the article by months. No seller found anywhere; bid services only see the RFP a year later. Buyers: fire-apparatus and DPW equipment dealers, municipal architects, roofing and HVAC contractors, water engineers, bond underwriters. Proposed $149 a month, a $490 spring season pass, $2,990 for a vendor-category bundle.
3. **Opening Ahead**: restaurant openings from local liquor, common-victualler and entertainment license hearings, 30–90 days before the state record the national services read. Buyers: equipment dealers, POS vendors, distributors, insurers. Proposed $99–249 a month or $12 a lead.

All three run on the crawler, the writer and the pages we have. Each needs a new subject taxonomy and sentence templates, a 90-day backfill from agendas already read to prove the lead time, and forty named calls.

## 3. How the people who did this did it

Patterns from Appendix A, each with the case that proves it.

The first ten customers were always people who already paid someone to read badly: Washington brokers after the 1989 crash for CoStar, Wisconsin contractors bidding late for Curate, lobbyists for Politico Pro. Nobody started with the general public.

The price is per organization per topic. A cheap tier for individuals works, but the organizations pay the bills: over 95% of Politico Pro's buyers were organizations, and its renewal rate was 96%. Renewal is the business.

Every winner stayed in one geography until renewal was proven. CoStar stayed in Washington for seven years; Curate was Wisconsin-only before six Midwest states, then fifty.

The moat was never the scraper. It was upstream access and the archive. Glenigan's exclusive gets UK planning applications three weeks before council websites; Dodge's edge in 1891 was a man with index cards who knew the clerks. For us that means the 315 town clerks who would email us packets on filing, and a tagged history a buyer can query: which towns moved on battery bylaws this quarter, and what passed.

The first year was funded by a sponsor or an anchor customer, not by seats. Punchbowl's $10 million first year was mostly sponsorship; Bloomberg's first customer paid $30 million for twenty terminals before anyone else could buy.

Edges die four ways: the government publishes the record well (free EDGAR killed the resellers), the subjects opt out, the input commoditizes, or the firm outgrows its renewing customers. Assume Massachusetts or a vendor will one day publish a free statewide agenda search, and sell the synthesis, the history and the clerk relationships, which stay valuable when the raw feed is free.

The legal lines are clear. Read only what boards post. Never copy another service's write-ups or photos (CoStar won $500 million from Xceligent). Respect portal terms of service (hiQ paid and died). Build no profiles of residents who speak at hearings. Never act on anything a staffer tells you before it is posted.

## 4. Recommendation

In order, each step funding the next:

1. **This quarter: sell what we already make.** A professional tier of Agenda Ahead for solar, battery and data-center developers and their lawyers: alerts across every town we read, the CSVs, the Data-Center Ledger, and the Attorney General record per clause type (Bylaw Outlook). Two anchor customers first, at $10,000–20,000 a year each for first look at all 315 towns, then the per-organization tier in the $3,000–5,000 a year range the comparables support, with a $300–500 individual tier. The first call list is the 92-company target list we already built. This needs the email alerts switched on (the Resend key) and a pricing decision from you; nothing about price goes on the site until you say.
2. **Next quarter: Development Ahead.** Add the non-energy subjects to the crawler (warehouses, subdivisions, retail, cannabis, hotels) and publish a weekly written pipeline for the trades. It is the Curate play with sentences instead of a spreadsheet, on towns we already read.
3. **From March: Warrant Watch**, when the spring warrants post. No competitor exists; the fall special Town Meetings posting now are the test bed.
4. **All year: build the outcome table.** Minutes, Attorney General decisions, New York local-law filings, interconnection-queue withdrawals, our own first-seen stamps. This is what turns "alerts" into "predictions", and it is the archive a buyer eventually pays eight figures for.
5. **Expand New York** before promising New York products; the battery moratoria and the 12 GW data-center queue are there, and our coverage is two towns.
6. **Keep the resident side free.** It is the distribution, the trust, and the reason clerks and reporters talk to us.

What I need from you: a pricing band (or "go with the comparables"), a yes or no on anchor-customer outreach (I draft, you send; I will not send mail on your behalf), the Resend key for alerts, and which second product you want first.

## Appendices

- A. How public-record edges became businesses and fortunes: `appendix_a_how_edges_became_businesses.md`
- B. What the data can predict, the clocks, the buyers and the prices: `appendix_b_what_the_data_can_predict.md`
- C. The same edge in other industries, ranked: `appendix_c_other_industries.md`
