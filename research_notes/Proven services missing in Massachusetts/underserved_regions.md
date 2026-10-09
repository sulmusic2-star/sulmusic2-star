# Underserved Geographic Markets in Massachusetts for Consumer and Business Services (as of Oct 2026)

**How these notes were built.** Most of the numbers below were computed directly from primary federal bulk files. I downloaded them and processed them with scripts; no third-party summaries were used for these:
- Census Vintage 2025 county and sub-county (town) population estimates. The county file came out Mar 26, 2026 and the town file in May 2026.
- ACS 2020–2024 5-year detailed tables: B19013 (income), B25077 (home value), B25064 (rent), and B01001 (age).
- County Business Patterns (CBP) 2023 and ZIP Code Business Patterns (ZBP) 2023. These are the latest releases; CBP 2024 was not yet posted, and its URL returned 404.
- BLS QCEW 2025 annual averages.
- Census Building Permits Survey (BPS), annual county files for 2021–2025.
- Census Business Formation Statistics (BFS), annual county business applications through 2025.

Qualitative evidence comes from news and agency sources. Where a fact came only from a search-result summary and I did not fetch the page, it is marked "(search summary)".

Source files:
- Pop (county): https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv
- Pop (towns): https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025_25.csv
- ACS 5-yr 2024 table-based summary file: https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/
- CBP 2023 county: https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip
- ZBP 2023 detail: https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip
- QCEW 2025 annual (example, Worcester County): https://data.bls.gov/cew/data/api/2025/a/area/25027.csv
- BPS county annual: https://www2.census.gov/econ/bps/County/co2025a.txt
- BFS county applications: https://www.census.gov/econ/bfs/xlsx/bfs_county_apps_annual.xlsx

---

## 1. Population and household growth 2020–2025 by county and city, and where people move when they leave Greater Boston

### Takeaway
Worcester County (+3.06%, +26,409) and Plymouth County (+3.02%, +16,011) grew fastest among mainland counties from 2020 to 2025. Bristol (+2.48%) and Middlesex (+2.33%) came next, while Suffolk, Hampden, Berkshire and Franklin shrank.

People leaving Greater Boston on net mostly go to Barnstable (Cape), Hampshire, Plymouth, Bristol and Berkshire, the counties with positive net domestic migration. Worcester County grew mainly through international immigration and natural increase; its net domestic migration was negative (−8,298).

### Cited Findings

**County population, Census Vintage 2025.** Change runs from the Apr 1, 2020 estimates base to Jul 1, 2025. Components are cumulative 2020–2025. [Census V2025 county file](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv)

| County (region) | 2020 base | Jul 2025 | Change | % | Natural chg | Net domestic mig. | Net intl mig. | 2024→25 change |
|---|---|---|---|---|---|---|---|---|
| Massachusetts | 7,033,112 | 7,154,084 | +120,972 | +1.72% | +26,617 | −182,145 | +286,765 | +15,524 |
| Worcester (Central MA) | 862,093 | 888,502 | +26,409 | +3.06% | +4,308 | −8,298 | +31,095 | +4,780 |
| Plymouth (SE MA) | 530,818 | 546,829 | +16,011 | +3.02% | −275 | +3,076 | +13,673 | +2,166 |
| Bristol (South Coast/Taunton/Attleboro) | 579,295 | 593,640 | +14,345 | +2.48% | −2,427 | +2,972 | +14,426 | +2,775 |
| Middlesex (incl. Lowell, MetroWest) | 1,631,912 | 1,669,979 | +38,067 | +2.33% | +18,568 | −67,912 | +88,944 | +6,050 |
| Essex (incl. Lawrence, Haverhill) | 809,943 | 826,653 | +16,710 | +2.06% | +5,093 | −22,089 | +33,532 | +483 |
| Barnstable (Cape Cod) | 229,064 | 233,539 | +4,475 | +1.95% | −9,046 | +8,116 | +6,090 | −412 |
| Norfolk | 726,021 | 739,749 | +13,728 | +1.89% | +3,673 | −14,194 | +24,031 | +2,148 |
| Hampshire (Northampton/Amherst) | 162,315 | 164,065 | +1,750 | +1.08% | −2,690 | +5,896 | +3,028 | −614 |
| Hampden (Springfield/Holyoke) | 465,818 | 464,338 | −1,480 | −0.32% | −1,916 | −8,800 | +9,271 | +920 |
| Franklin | 71,029 | 70,698 | −331 | −0.47% | −1,588 | +654 | +636 | −213 |
| Berkshire (Pittsfield) | 129,026 | 128,224 | −802 | −0.62% | −4,212 | +1,740 | +1,909 | −825 |
| Suffolk (Boston) | 800,934 | 791,891 | −9,043 | −1.13% | +16,779 | −82,574 | +58,602 | −1,644 |
| Dukes (Martha's Vineyard) | 20,593 | 21,219 | +626 | +3.04% | −15 | −445 | +1,103 | −135 |
| Nantucket | 14,251 | 14,758 | +507 | +3.56% | +365 | −287 | +425 | +45 |

- **Statewide growth slowed sharply.** The state added only 15,524 people between July 2024 and July 2025 (+0.2%), down from about 1.0% the previous year. Net international migration stayed positive but fell from its 2024 peak, and it still more than offset domestic out-migration. — [UMass Donahue Institute](https://donahue.umass.edu/news-events/institute-news/analysis-shows-massachusetts-population-growth-slowing-but-still-positive) (search summary; matches my calculation from the Census file: 7,138,560 → 7,154,084)
- **Domestic migration in 2025 alone** was still negative for Worcester (−1,253), Middlesex (−11,269), Suffolk (−12,966) and Essex (−5,184). It was positive for Bristol (+906), Barnstable (+547) and Plymouth (+59). — [Census V2025](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv)

**Cities and towns, Census V2025 sub-county estimates** (towns are minor civil divisions; base 2020 → Jul 2025). [Census V2025 sub-county file](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025_25.csv)

- **Largest absolute gains:**

  | Place | Change | % |
  |---|---|---|
  | Worcester | +7,354 | +3.6% (to 213,862) |
  | Plymouth | +6,635 | +10.8% (to 67,846) |
  | Everett | +4,504 | +9.2% |
  | Lowell | +4,375 | +3.8% (to 119,971) |
  | Cambridge | +4,193 | |
  | Somerville | +3,223 | |
  | Taunton | +3,157 | +5.3% (to 62,522) |
  | Woburn | +3,085 | +7.5% |
  | Lynn | +2,977 | |
  | Weymouth | +2,325 | |
  | Chelmsford | +2,176 | +6.0% |
  | Wakefield | +2,124 | +7.8% |

- **Fastest % growth, towns of 8,000+ residents:**

  | Town | % | Change |
  |---|---|---|
  | Millis | +11.8% | +1,002 |
  | Plymouth | +10.8% | |
  | Raynham | +9.3% | +1,404 |
  | Ayer | +9.2% | |
  | Everett | +9.2% | |
  | Rehoboth | +8.5% | |
  | Lancaster | +8.3% | |
  | Rutland | +8.1% | |
  | Lakeville | +7.9% | |
  | Wakefield | +7.8% | |
  | Woburn | +7.5% | |
  | Westminster | +7.2% | |
  | Grafton | +7.0% | +1,381 |
  | Upton | +7.0% | |
  | North Reading | +6.5% | |
  | Bellingham | +6.4% | |
  | Douglas | +6.3% | |
  | Wellesley | +6.2% | |
  | Kingston | +6.2% | |
  | Westborough | +6.2% | +1,329 |
  | Hopkinton | +5.9% | |

- **Selected named cities, 2020 → 2025:**

  | Region | City/town | Change | % |
  |---|---|---|---|
  | Central MA | Shrewsbury | +1,306 | +3.4% |
  | Central MA | Northborough | +339 | +2.2% |
  | MetroWest | Framingham | +629 | +0.9% |
  | MetroWest | Marlborough | +989 | +2.4% |
  | MetroWest | Natick | −40 | −0.1% |
  | Merrimack Valley | Lawrence | +147 | +0.2% |
  | Merrimack Valley | Haverhill | +584 | +0.9% |
  | Merrimack Valley | Methuen | +1,561 | +2.9% |
  | South Coast | New Bedford | +787 | +0.8% |
  | South Coast | Fall River | +1,316 | +1.4% |
  | South Coast | Dartmouth | +423 | +1.2% |
  | Southeastern | Brockton | +476 | +0.5% |
  | Southeastern | Middleborough | +905 | +3.7% |
  | Cape | Barnstable (town) | +1,199 | +2.5% |
  | Cape | Falmouth | +826 | +2.5% |
  | Pioneer Valley | Springfield | −1,171 | −0.8% |
  | Pioneer Valley | Holyoke | −233 | −0.6% |
  | Pioneer Valley | Chicopee | −270 | −0.5% |
  | Pioneer Valley | Westfield | −268 | −0.7% |
  | Pioneer Valley | Northampton | +1,470 | +5.0% |
  | Pioneer Valley | Amherst | +1,651 | +4.2% |
  | Pioneer Valley | Easthampton | −362 | −2.2% |
  | Berkshires | Pittsfield | −1,048 | −2.4% |
  | Berkshires | North Adams | −572 | −4.4% |

- **Largest declines:** Boston (−5,644, −0.8%), Revere (−2,108), Springfield (−1,171), Pittsfield (−1,048), Winthrop (−675), Chelsea (−616), North Adams (−572). — [Census V2025 sub-county](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025_25.csv)
- **IRS-based migration data for the Worcester metro (2022–23):** 24,762 people moved in and 26,327 moved out, a net of −1,565. Boston, MA-NH was the largest corridor in both directions: 12,314 in from the Boston metro and 7,977 out to it, which implies a net gain of about 4,300 from Boston. — [Shilo.ai, aggregating IRS SOI data](https://www.shilo.ai/tools/where-america-moves/massachusetts/worcester) (secondary aggregator; search summary)
- **Conflicting NAR data for 2022:** inbound movers to Greater Boston rose 2.6% year over year, while movers into Greater Worcester fell 13.4%. — [Worcester Business Journal](https://wbjournal.com/article/worcester-residents-look-to-boston-but-boston-looks-to-providence) (search summary)
- **Plymouth's growth:** a Census-based ranking for 2020–2023 put Plymouth second in the state, at 65,405 by July 2023 (+6.8%). — [WUPE](https://wupe.com/here-are-the-top-3-fastest-growing-cities-in-ma/) (search summary)

### Inferences
- Two different growth engines are at work:
  - **Domestic movers leaving Boston's housing costs** show up as positive net domestic migration in Plymouth, Bristol, Barnstable, Hampshire and Berkshire. These markets skew toward owner-occupied single-family homes and older households.
  - **International immigration** drives growth in Worcester, Lowell, Lynn, Everett, Taunton and Brockton. These markets skew younger, larger households, more renters, and more price-sensitive and multilingual demand.
- The best-balanced growth markets combine above-average growth with above-average income:
  - Worcester County suburbs: Shrewsbury, Westborough, Grafton, Northborough, Hopkinton, Upton, Douglas, Rutland and Lancaster, which grew 2–8% with median household income of $131k–$223k.
  - The Plymouth/Kingston/Lakeville corridor.
  - The Taunton/Raynham/Rehoboth corridor.
- Williamstown (Berkshire) shows +22.2% (+1,666), which is very likely a group-quarters/college estimate artifact (Williams College) and not real household growth. Treat it as unreliable.
- The 2024→2025 slowdown (0.2% statewide) means "growth" markets are growing slowly in absolute terms. Worcester County's +4,780 in a year is notable but modest.

### Gaps
- I found no 2025 county-to-county flow data showing exactly where Boston/Suffolk out-migrants land. The IRS SOI 2022–23 county flows would answer this but were not retrieved. The Shilo.ai figures are secondary and metro-level.
- Household (as opposed to population) growth 2020–2025 by county was not retrieved. The Census does not publish annual county household estimates; ACS 1-year 2025 was not accessible (HTTP 401 on the bulk file).
- UMass Donahue's V2025 county and town summary PDFs could not be retrieved, because the documents now redirect after a site migration. Their projections to 2030/2050 were not reviewed.

---

## 2. Household income, home values, older-adult share, and new housing construction (permits, MBTA Communities)

### Takeaway
Income is highest in Middlesex ($130.8k), Norfolk ($130.7k) and Plymouth ($114.2k). It is lowest in Hampden ($71.3k), Franklin ($74.9k) and Berkshire ($76.0k).

Worcester ($95.9k income, $423.7k median home value) offers near-state-median income at roughly 25% lower home values than the state ($562.1k).

Outside Suffolk, new housing per capita from 2021 to 2025 was strongest on the Cape and Islands, in Plymouth, Norfolk, Middlesex and Worcester, and in Hampshire. Plymouth, Bristol and Barnstable permits are mostly single-family/small buildings, which drives demand for home services.

### Cited Findings

**ACS 2020–2024 5-year estimates by county.** [ACS tables B19013, B25077, B25064, B01001](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

| County | Median HH income | Median home value | Median gross rent | % 65+ | % under 18 | % 25–34 |
|---|---|---|---|---|---|---|
| Massachusetts | $103,960 | $562,100 | $1,762 | 17.9 | 19.4 | 14.0 |
| Middlesex | $130,847 | $727,800 | $2,201 | 16.3 | 19.5 | 15.1 |
| Norfolk | $130,739 | $683,900 | $2,149 | 17.8 | 20.5 | 12.9 |
| Plymouth | $114,201 | $556,000 | $1,747 | 19.8 | 20.7 | 11.2 |
| Essex | $101,883 | $619,100 | $1,756 | 18.5 | 20.8 | 12.5 |
| Worcester | $95,939 | $423,700 | $1,426 | 17.0 | 20.6 | 13.0 |
| Suffolk | $95,631 | $705,800 | $2,129 | 13.3 | 16.0 | 22.3 |
| Barnstable | $95,241 | $629,000 | $1,678 | 33.1 | 14.1 | 9.1 |
| Hampshire | $87,001 | $390,300 | $1,388 | 19.4 | 14.2 | 9.9 |
| Bristol | $85,625 | $451,200 | $1,245 | 17.8 | 20.5 | 12.9 |
| Berkshire | $76,013 | $305,400 | $1,097 | 25.0 | 16.0 | 10.5 |
| Franklin | $74,907 | $329,000 | $1,177 | 24.6 | 16.6 | 11.3 |
| Hampden | $71,306 | $298,800 | $1,136 | 18.3 | 20.9 | 13.3 |
| Dukes | $125,786 | $1,165,800 | $1,277 | 26.5 | 16.8 | 12.0 |
| Nantucket | $139,688 | $1,593,800 | $2,213 | 16.1 | 20.5 | 10.5 |

**Selected towns, ACS 2020–24.** [Same ACS source, county-subdivision geography](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

| Region | Town | Median HH income | Median home value | % 65+ |
|---|---|---|---|---|
| Central MA | Worcester | $70,102 | $374,400 | 13.3 |
| Central MA | Shrewsbury | $139,302 | $592,300 | |
| Central MA | Westborough | $141,944 | $685,300 | |
| Central MA | Grafton | $131,484 | $525,300 | |
| Central MA | Northborough | $153,199 | | |
| Central MA | Holden | $141,923 | | |
| Central MA | Auburn | $116,711 | | |
| Central MA | Millbury | $118,790 | | |
| Central MA | Sutton | $147,125 | | |
| Central MA | Fitchburg | $73,040 | | |
| Central MA | Leominster | $83,816 | | |
| Central MA | Southbridge | $66,287 | | |
| MetroWest | Hopkinton | $222,801 | | |
| MetroWest | Framingham | $107,419 | | |
| MetroWest | Natick | $138,538 | | |
| MetroWest | Marlborough | $91,968 | | |
| MetroWest | Milford | $96,365 | | |
| Merrimack Valley | Lowell | $78,658 | | |
| Merrimack Valley | Lawrence | $60,433 | | |
| Merrimack Valley | Haverhill | $88,326 | | |
| Merrimack Valley | Methuen | $113,310 | | |
| Merrimack Valley | Chelmsford | $140,629 | | |
| Merrimack Valley | Andover | $172,606 | | |
| South Coast | New Bedford | $56,981 | | 15.4 |
| South Coast | Fall River | $56,673 | | 16.1 |
| South Coast | Dartmouth | $99,839 | | 21.0 |
| South Coast | Westport | | | 24.2 |
| South Coast | Somerset | | | 25.3 |
| South Coast | Swansea | | | 25.0 |
| Southeastern | Plymouth | $116,941 | $527,400 | 25.2 |
| Southeastern | Brockton | $80,115 | | |
| Southeastern | Taunton | $79,283 | | |
| Southeastern | Raynham | $124,012 | | |
| Southeastern | Lakeville | $133,984 | | |
| Southeastern | Kingston | $119,876 | | |
| Cape Cod | Barnstable (town) | $91,982 | | 26.8 |
| Cape Cod | Falmouth | $93,043 | | 33.9 |
| Cape Cod | Yarmouth | | | 35.0 |
| Cape Cod | Dennis | | | 39.8 |
| Cape Cod | Harwich | | | 35.8 |
| Pioneer Valley | Springfield | $52,656 | $245,000 | |
| Pioneer Valley | Holyoke | $53,605 | | |
| Pioneer Valley | Chicopee | $62,615 | | |
| Pioneer Valley | Northampton | $80,288 | | |
| Pioneer Valley | Amherst | $66,968 | | 10.1 |
| Berkshires | Pittsfield | $70,582 | $256,900 | |
| Berkshires | North Adams | $47,500 | | |
| Berkshires | Lenox | | | 40.1 |

**Housing units authorized by building permits, 2021–2025.** Census BPS annual county estimates, including imputation for non-reporting places. [Census BPS](https://www2.census.gov/econ/bps/County/co2025a.txt) (also co2021a–co2024a files)

| County | 2021 | 2022 | 2023 | 2024 | 2025 | Total 21–25 | Per 1,000 pop (2025) | Share in 5+ unit bldgs |
|---|---|---|---|---|---|---|---|---|
| Middlesex | 4,671 | 3,257 | 3,894 | 3,495 | 2,341 | 17,658 | 10.6 | 67% |
| Suffolk | 3,738 | 4,069 | 2,590 | 2,007 | 2,338 | 14,742 | 18.6 | 91% |
| Worcester | 1,895 | 2,124 | 1,215 | 2,506 | 1,690 | 9,430 | 10.6 | 45% |
| Norfolk | 2,418 | 2,314 | 887 | 1,224 | 1,194 | 8,037 | 10.9 | 60% |
| Plymouth | 2,489 | 1,327 | 1,014 | 1,256 | 931 | 7,017 | 12.8 | 32% |
| Essex | 1,703 | 856 | 1,140 | 1,011 | 942 | 5,652 | 6.8 | 55% |
| Bristol | 866 | 751 | 761 | 863 | 1,156 | 4,397 | 7.4 | 27% |
| Barnstable | 672 | 887 | 547 | 640 | 630 | 3,376 | 14.5 | 24% |
| Hampshire | 398 | 411 | 282 | 318 | 291 | 1,700 | 10.4 | 57% |
| Hampden | 263 | 254 | 360 | 443 | 318 | 1,638 | 3.5 | 14% |
| Nantucket | 275 | 239 | 232 | 262 | 250 | 1,258 | 85.2 | 7% |
| Berkshire | 193 | 126 | 145 | 127 | 149 | 740 | 5.8 | 20% |
| Dukes | 188 | 140 | 81 | 103 | 183 | 695 | 32.8 | 7% |
| Franklin | 84 | 75 | 66 | 83 | 64 | 372 | 5.3 | 6% |
| **State** | | | | | | **76,712** | **10.7** | |

- **Bristol permits rose to 1,156 units in 2025,** its highest in the 5-year window (+34% vs 2024). — [Census BPS](https://www2.census.gov/econ/bps/County/co2025a.txt)
- **MBTA Communities Act compliance:**
  - The Attorney General says 165 of 177 MBTA Communities have come into compliance, and the law has sparked projects for nearly 7,000 homes across 34 communities.
  - The AG sought court orders against 9 noncompliant towns: Dracut, East Bridgewater, Halifax, Holden, Marblehead, Middleton, Tewksbury, Wilmington, and Winthrop.
  - Carver and Rehoboth have until Dec 31, 2026.
  - [Mass. AG press release](https://www.mass.gov/news/ag-campbell-sues-nine-communities-for-noncompliance-with-mbta-communities-law) (search summary)
  - Boston.com counted 133 compliant, 7 conditionally compliant and 25 in interim compliance as of Jan 23, 2026. — [Boston.com](https://www.boston.com/news/local-news/2024/10/17/map-mbta-communities-whats-next-for-your-town/) (search summary; counting methods differ)
  - Holdouts are losing state grant funding. — [Streetsblog Mass, Jan 16 2026](https://mass.streetsblog.org/2026/01/16/mbta-communities-act-holdouts-are-losing-state-funding) (search summary)

### Inferences
- **Plymouth County has the strongest mix of demand signals for owner-household services:**
  - Third-highest income ($114k).
  - Highest per-capita permitting of any mainland non-urban county (12.8 per 1,000, and only 32% multifamily, so mostly single-family homes).
  - Older households: 19.8% county-wide and 25.2% in Plymouth town.
  - Together these support home services, home health and senior services, and the young families moving into new subdivisions support childcare.
- **Worcester County adds the most new units outside the Boston core** (9,430). It combines near-state income with much lower home values ($423.7k), so a household there has more disposable income after housing than in Middlesex or Norfolk.
- **Several MBTA rezoning holdouts sit in or next to the identified growth corridors:** Holden (Worcester County), Dracut and Tewksbury (Merrimack Valley), and East Bridgewater, Halifax, Carver and Rehoboth (Plymouth/Bristol). Future multifamily supply there depends on litigation and town-meeting outcomes.
- **Barnstable has the oldest population (33.1% aged 65+)** and towns at 34–40%. That is a structural demand base for home health, elder services, medical transport, home maintenance and downsizing services.

### Gaps
- I did not compute town-level building permits (the BPS place-level files were not processed), and MBTA unit capacity by town is not in these notes.
- ACS 5-year figures are averages over 2020–2024; the ACS 2025 1-year figures were not retrievable.

---

## 3. Supply: service establishments per 10,000 residents by county, and where supply is thin relative to income

### Takeaway
Compared with the state per-capita average, two county groups stand out:
- **Thin supply, lower demand:** Hampden, Franklin, Hampshire, Worcester and Bristol are below average in many consumer-service categories, but they also have lower incomes, so some of that thinness reflects weaker demand.
- **Thin supply, solid demand:** Worcester County stands out because supply is below average while population growth leads the state and income is near the median. It is short of personal care/salons (0.65–0.72x state), childcare (0.71–0.81x), accounting/bookkeeping (0.67–0.77x), fitness (0.73–0.76x), dentists (0.83–0.89x) and residential property management (0.49x).

Plymouth County is well supplied with contractors and landscapers but thin in dentists (0.83x), home health (0.84–0.92x), childcare (0.87–0.91x) and property management (0.42x). Bristol is thin in home health (0.57–0.75x), dentists (0.75–0.78x) and fitness (0.74–0.75x).

On a "median income ÷ supply" ratio, Middlesex, Norfolk, Plymouth and Worcester have the most income per unit of service supply among non-urban counties. Suffolk ranks first only because its supply is structurally low (see Inferences).

### Cited Findings

**CBP 2023 establishments (with paid employees) per 10,000 residents,** using July 2023 population. Values in parentheses are the county's index vs the state per-capita rate (1.00 = state average). [Census CBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip)

| NAICS category | MA /10k | Worcester | Plymouth | Bristol | Essex | Middlesex | Norfolk | Hampden | Hampshire | Franklin | Berkshire | Barnstable | Suffolk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2382 Bldg equipment contractors | 8.30 | 7.80 (0.94) | 11.40 (1.37) | 8.85 (1.07) | 7.80 (0.94) | 8.67 (1.04) | 9.24 (1.11) | 5.73 (0.69) | 6.60 (0.80) | 6.63 (0.80) | 10.62 (1.28) | 15.24 (1.84) | 3.10 (0.37) |
| – 238220 Plumbing/HVAC | 4.34 | 3.75 (0.86) | 5.89 (1.36) | 4.74 (1.09) | 4.05 (0.93) | 4.68 (1.08) | 4.90 (1.13) | 2.64 (0.61) | 3.51 (0.81) | 3.39 (0.78) | 5.43 (1.25) | 8.78 (2.02) | 1.57 (0.36) |
| 2383 Bldg finishing (painting, flooring etc.) | 5.15 | 4.83 (0.94) | 5.52 (1.07) | 5.08 (0.99) | 5.34 (1.04) | 5.47 (1.06) | 5.04 (0.98) | 2.96 (0.58) | 2.66 (0.52) | 2.68 (0.52) | 5.12 (0.99) | 11.64 (2.26) | 2.97 (0.58) |
| 5617 Services to buildings | 9.86 | 8.93 (0.91) | 11.28 (1.14) | 9.02 (0.91) | 11.03 (1.12) | 9.57 (0.97) | 9.24 (0.94) | 7.14 (0.72) | 7.93 (0.80) | 8.19 (0.83) | 13.25 (1.34) | 26.41 (2.68) | 4.37 (0.44) |
| – 561720 Janitorial | 2.48 | 2.22 (0.89) | 2.58 (1.04) | 2.15 (0.87) | 2.79 (1.12) | 2.65 (1.07) | 2.05 (0.83) | 1.58 (0.64) | 1.39 (0.56) | 0.85 (0.34) | 2.02 (0.81) | 4.24 (1.71) | 2.64 (1.06) |
| – 561730 Landscaping | 6.44 | 5.88 (0.91) | 7.21 (1.12) | 5.85 (0.91) | 7.47 (1.16) | 5.98 (0.93) | 6.00 (0.93) | 4.70 (0.73) | 6.11 (0.95) | 6.77 (1.05) | 10.00 (1.55) | 20.46 (3.18) | 1.39 (0.22) |
| 54194 Veterinary | 0.82 | 0.89 (1.08) | 0.98 (1.19) | 0.75 (0.91) | 0.82 (0.99) | 0.81 (0.98) | 0.82 (1.00) | 0.56 (0.68) | 1.21 (1.47) | 1.98 (2.40) | 0.78 (0.94) | 1.80 (2.18) | 0.36 (0.43) |
| 6212 Dentists | 4.51 | 4.01 (0.89) | 3.76 (0.83) | 3.50 (0.78) | 4.65 (1.03) | 5.53 (1.23) | 6.31 (1.40) | 3.53 (0.78) | 3.75 (0.83) | 2.82 (0.63) | 4.11 (0.91) | 4.24 (0.94) | 3.43 (0.76) |
| 6216 Home health | 1.27 | 1.26 (0.99) | 1.17 (0.92) | 0.94 (0.74) | 1.53 (1.21) | 1.30 (1.02) | 1.72 (1.36) | 1.36 (1.08) | 0.85 (0.67) | 0.71 (0.56) | 1.16 (0.92) | 1.71 (1.35) | 0.73 (0.57) |
| 6244 Child day care | 3.26 | 2.65 (0.81) | 2.91 (0.89) | 3.17 (0.97) | 3.06 (0.94) | 3.80 (1.16) | 4.42 (1.35) | 2.34 (0.72) | 2.84 (0.87) | 2.12 (0.65) | 1.86 (0.57) | 2.31 (0.71) | 3.53 (1.08) |
| 8111 Auto repair | 5.40 | 5.97 (1.11) | 6.49 (1.20) | 6.00 (1.11) | 5.50 (1.02) | 5.22 (0.97) | 5.53 (1.02) | 5.17 (0.96) | 4.54 (0.84) | 5.79 (1.07) | 6.43 (1.19) | 6.81 (1.26) | 3.30 (0.61) |
| 8121 Personal care | 6.57 | 4.75 (0.72) | 6.56 (1.00) | 5.71 (0.87) | 7.53 (1.15) | 7.29 (1.11) | 9.01 (1.37) | 3.87 (0.59) | 3.69 (0.56) | 2.54 (0.39) | 3.80 (0.58) | 7.36 (1.12) | 7.12 (1.08) |
| – 812112 Beauty salons | 3.63 | 2.46 (0.68) | 3.43 (0.94) | 2.87 (0.79) | 4.10 (1.13) | 4.10 (1.13) | 4.72 (1.30) | 2.34 (0.64) | 2.60 (0.72) | 1.83 (0.51) | 2.09 (0.58) | 4.75 (1.31) | 4.08 (1.12) |
| 812910 Pet care (non-vet) | 1.07 | 1.00 (0.93) | 1.43 (1.33) | 1.09 (1.02) | 1.24 (1.15) | 1.01 (0.94) | 1.27 (1.19) | 0.50 (0.46) | 1.09 (1.02) | 0.85 (0.79) | 1.24 (1.16) | 1.67 (1.56) | 0.75 (0.70) |
| 8123 Drycleaning/laundry | 1.16 | 0.77 (0.66) | 1.04 (0.89) | 1.16 (1.00) | 1.25 (1.07) | 1.30 (1.11) | 1.55 (1.33) | 0.76 (0.65) | 0.61 (0.52) | 0.85 (0.73) | 0.78 (0.67) | 0.94 (0.81) | 1.55 (1.33) |
| 5412 Accounting/tax/bookkeeping | 3.61 | 2.79 (0.77) | 3.61 (1.00) | 3.46 (0.96) | 3.72 (1.03) | 3.72 (1.03) | 4.94 (1.37) | 2.99 (0.83) | 2.60 (0.72) | 2.82 (0.78) | 4.57 (1.27) | 5.44 (1.51) | 2.71 (0.75) |
| 713940 Fitness centers | 1.74 | 1.32 (0.76) | 2.35 (1.35) | 1.28 (0.74) | 1.61 (0.93) | 2.05 (1.18) | 2.34 (1.35) | 0.91 (0.52) | 1.45 (0.84) | 0.85 (0.49) | 0.70 (0.40) | 2.10 (1.21) | 1.63 (0.94) |
| 611691 Exam prep/tutoring | 0.35 | 0.19 (0.56) | 0.30 (0.85) | 0.12 (0.34) | 0.29 (0.84) | 0.58 (1.66) | 0.51 (1.46) | 0.24 (0.68) | 0.00 | 0.42 (1.22) | 0.31 (0.89) | 0.13 (0.37) | 0.32 (0.92) |
| 531311 Residential property mgrs | 2.25 | 1.11 (0.49) | 0.94 (0.42) | 1.04 (0.46) | 1.68 (0.75) | 2.07 (0.92) | 2.44 (1.09) | 1.67 (0.74) | 1.51 (0.67) | 0.42 (0.19) | 2.09 (0.93) | 2.57 (1.14) | 6.30 (2.80) |

Other per-10k figures from the same file: all private establishments MA 259.8. Worcester 219.4, Hampden 202.1, Hampshire 211.3, Franklin 218.6, Bristol 225.5, Essex 244.5, Plymouth 248.7, Middlesex 271.4, Norfolk 284.0, Suffolk 280.8, Berkshire 290.6, Barnstable 383.5. — [Census CBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip)

**Cross-check with BLS QCEW 2025** (newer data; private UI-covered establishments per 10,000 residents in 2025, index vs MA in parentheses). The pattern matches CBP. [BLS QCEW 2025 annual](https://data.bls.gov/cew/data/api/2025/a/area/25027.csv)

| County | Personal care (MA 6.00) | Beauty salons (MA 3.29) | Child care (MA 2.89) | Dentists (MA 4.24) | Home health (MA 1.41) | Accounting (MA 4.73) | Fitness (MA 1.84) |
|---|---|---|---|---|---|---|---|
| Worcester | 3.87 (0.65) | 1.98 (0.60) | 2.05 (0.71) | 3.52 (0.83) | 1.24 (0.88) | 3.19 (0.67) | 1.35 (0.73) |
| Plymouth | 6.09 (1.02) | | 2.63 (0.91) | 3.53 (0.83) | 1.24 (0.88) | 4.04 (0.85) | 2.01 (1.09) |
| Bristol | 5.19 (0.87) | | 2.61 (0.90) | 3.20 (0.75) | 0.81 (0.57) | 3.82 (0.81) | 1.38 (0.75) |
| Hampden | 3.34 (0.56) | 2.15 (0.65) | 2.15 (0.74) | 3.10 (0.73) | | 3.40 (0.72) | 1.16 (0.63) |
| Hampshire | 3.96 (0.66) | | 2.74 (0.95) | 2.86 (0.67) | 0.61 (0.43) | 2.68 (0.57) | |
| Berkshire | 3.59 (0.60) | | 2.34 (0.81) | 3.59 (0.85) | | | 1.09 (0.59) |
| Barnstable | | | 1.88 (0.65) | 4.20 (0.99) | | | |

- **Additional QCEW 2025 detail:**
  - Bristol: janitorial 1.79 (0.69), vet 0.67 (0.77).
  - Hampden: contractors (2382) 5.53 (0.66), vets 0.54 (0.62), pet care 0.52 (0.47).
  - Hampshire: janitorial 1.34 (0.52).
  - Berkshire: contractors 11.46 (1.37), landscaping 10.22 (1.71). — [BLS QCEW 2025](https://data.bls.gov/cew/data/api/2025/a/area/25013.csv)
- **Age-adjusted supply** (CBP 2023 establishments vs ACS 2020–24 age groups). [CBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip) + [ACS B01001](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)
  - **Childcare centers per 1,000 children under 5** (state 6.61): Hampden 4.44 (0.67), Berkshire 4.87 (0.74), Worcester 5.20 (0.79), Franklin 5.68 (0.86), Essex 5.73 (0.87), Plymouth 5.73 (0.87), Bristol 6.34 (0.96), Middlesex 7.56 (1.14), Norfolk 8.65 (1.31).
  - **Home health establishments per 10,000 residents aged 65+** (state 7.13): Franklin 2.86 (0.40), Hampshire 4.45 (0.62), Berkshire 4.63 (0.65), Barnstable 5.21 (0.73), Bristol 5.32 (0.75), Suffolk 5.47 (0.77), Plymouth 5.96 (0.84), Worcester 7.45 (1.04), Hampden 7.45 (1.05), Essex 8.33 (1.17), Norfolk 9.72 (1.36).
- **Composite "income per unit of supply."** This is the mean CBP index across 11 core categories: 2382, 5617, 561720, 561730, 54194, 6212, 6216, 6244, 8111, 8121, 812910. The ratio is the median-income index divided by the supply index.

  | County | Supply idx | Income idx | Ratio |
  |---|---|---|---|
  | Suffolk | 0.67 | 0.92 | 1.38 |
  | Middlesex | 1.04 | 1.26 | 1.21 |
  | Norfolk | 1.14 | 1.26 | 1.11 |
  | Plymouth | 1.09 | 1.10 | 1.00 |
  | Worcester | 0.93 | 0.92 | 1.00 |
  | Hampshire | 0.85 | 0.84 | 0.98 |
  | Hampden | 0.73 | 0.69 | 0.94 |
  | Essex | 1.08 | 0.98 | 0.91 |
  | Bristol | 0.92 | 0.82 | 0.89 |
  | Franklin | 0.86 | 0.72 | 0.83 |
  | Berkshire | 1.02 | 0.73 | 0.71 |
  | Barnstable | 1.68 | 0.92 | 0.54 |
  | Dukes | 2.74 | 1.21 | 0.44 |
  | Nantucket | 4.10 | 1.34 | 0.33 |

  — my calculation from [CBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip) and [ACS B19013](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

**Town-level supply from ZIP Code Business Patterns 2023.** USPS city names were aggregated, and population is the sum of ACS 2020–24 ZCTA populations. The supply index is the mean ratio to the state for 8 categories where ZIP totals match county totals closely: contractors 2382, services to buildings 5617, dentists, childcare, auto repair, personal care, accounting and fitness. Values below 1 mean thinner supply. [Census ZBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip)

| Region | Town (index) |
|---|---|
| Central MA | Lancaster 0.25, Douglas 0.38, Rutland 0.41, Grafton (01519) 0.49, Westminster 0.55, Millbury 0.56, Southbridge 0.63, Upton 0.68, Fitchburg 0.71, Worcester city 0.75, Charlton 0.76, Uxbridge 0.79, Webster 0.82, Oxford 0.82, Gardner 0.85, North Grafton 0.95, Sutton 0.98, Shrewsbury 1.00, Holden 1.13, Leominster 1.14, Westborough 1.43, Northborough 1.59, Auburn 1.63 |
| MetroWest | Millis 0.74, Hopkinton 1.07, Bellingham 1.19, Framingham 1.25, Medway 1.33, Milford 1.44, Natick 1.49, Marlborough 1.59 |
| Merrimack Valley / North Shore | Lowell 0.49, Lawrence 0.75, Lynn 0.79, Haverhill 0.80, Methuen 0.87, Tewksbury 1.07, Dracut 1.16, North Andover 1.42, Chelmsford 1.48, Woburn 1.87 |
| South Coast / Bristol | New Bedford 0.66, Fall River 0.71, Taunton 0.76, Attleboro 0.88, South Dartmouth 0.92, Rehoboth 1.07, North Dartmouth 1.31, Raynham 1.40 |
| Southeastern / Plymouth | Brockton 0.76, Wareham 0.82, Bridgewater 1.01, Middleborough 1.07, Plymouth 1.20, Lakeville 1.30, Kingston 1.64 |
| Pioneer Valley | Amherst 0.32, Springfield 0.40, Chicopee 0.58, Longmeadow 0.59, Belchertown 0.65, Holyoke 0.66, Westfield 0.83, West Springfield 1.19, Northampton 1.43 |
| Berkshires | North Adams 0.71, Great Barrington 1.02, Pittsfield 1.08 |
| Cape | Mashpee 1.10, Falmouth 2.04, Sandwich 2.05, Hyannis 3.08 |
| Inner core | Everett 0.65, Cambridge 0.70, Somerville 0.73, Quincy 0.93 |

- **Worcester city (ZIP aggregate, pop 207,324)** has 1.6 childcare centers per 10k vs 2.99 statewide in ZBP, 4.6 personal care vs 6.42, 0.9 fitness vs 1.46, and 0.3 drycleaners vs 0.88. — [ZBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip)
- **Plymouth town (3 ZIPs, pop 63,689)** has 2.2 childcare centers per 10k vs 2.99 statewide, but 12.1 building-equipment contractors vs 8.10 (well supplied). — [ZBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip)
- **Data quality note:** ZBP 2023 statewide totals match CBP for contractors (5,704 vs 5,868), services to buildings (6,826 vs 6,977), personal care (4,521 vs 4,647), childcare (2,107 vs 2,309) and all establishments (182,803 vs 183,767). They are far lower for veterinary (281 vs 583), pet care (513 vs 759), home health (692 vs 897) and drycleaning (620 vs 824), so ZIP-level counts for those four categories are unreliable and were excluded from the town index. — my comparison of [ZBP](https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip) and [CBP](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip)

### Inferences
- **Suffolk's low per-capita contractor, landscaping and building-services counts are structural.** Trades firms based in the suburbs serve Boston, and Boston has few yards. Suffolk is not a genuine gap market for those trades.
- **Cape and Islands per-capita supply is inflated.** It looks very high (Barnstable 2.68x for building services, 3.18x for landscaping) because the year-round population denominator excludes seasonal residents and second homes (see Q4). It does not mean those markets are saturated relative to actual demand.
- **Worcester County is the clearest "below-average supply, above-average growth" county.** The pattern holds in both CBP 2023 and QCEW 2025, for personal care, childcare, accounting, fitness, dentists and property management.
- **Hampden, Franklin and Berkshire are thin in many categories, but demand is also weaker** (low income, shrinking population). Their gaps in childcare and dentists are mostly gaps of affordability and public payers (MassHealth, EEC vouchers), not unmet private demand.
- **Home health is thinnest relative to seniors in Franklin, Hampshire, Berkshire, Barnstable, Bristol and Plymouth.** These are the counties with older populations. Agencies often serve multi-county territories, so location counts understate actual coverage.
- **Thin-supply towns next to high-income growth suburbs suggest service areas for mobile and home-based businesses.** Examples are Grafton, Upton, Douglas, Rutland, Lancaster, Millbury and Westminster in Worcester County, and Millis in Norfolk. They suit cleaning, lawn and snow, handyman, mobile grooming and in-home care better than storefronts, because residents shop in neighboring hubs such as Shrewsbury, Westborough, Auburn and Worcester.

### Gaps
- **Nonemployer counts were not retrieved.** CBP, ZBP and QCEW count only establishments with paid employees, so sole-proprietor supply is missing, and it is large in personal care, landscaping, cleaning, painting and pet care. The Census Nonemployer Statistics by county would close this.
- **I found no source quantifying presence of national chains or franchises by MA county** (e.g., franchise unit counts for Mr. Handyman, Molly Maid, Great Clips, The Goddard School, Home Instead). This supply indicator remains unmeasured.
- **CBP 2024 (expected later in 2026) was not yet published** (HTTP 404); CBP 2023 is the latest establishment-level detail.
- **Some QCEW county cells are suppressed** ("N"), mainly in Dukes, Nantucket and Franklin.

---

## 4. Evidence of regional service gaps from news and agency reports

### Takeaway
Independent sources corroborate gaps in the following areas:
- Childcare, statewide but worst in Central MA, Western MA, the Southeast and the Outer Cape.
- Dental access in the Berkshires.
- Home care workforce, statewide.
- Veterinary/emergency vet capacity, with a Pioneer Valley example.
- Cape Cod labor and housing constraints that limit trades and service staffing.

Many reports are 2021–2024 vintage; the only 2025–2026 items are the state childcare data (Aug 2025), the UMass Boston childcare analysis (Mar 2026), the UMass Donahue human-services workforce data (Jan 2026), a Berkshire dental opening (Mar 2025) and nursing-home staffing (Jul 2026).

### Cited Findings
**Childcare**
- **State Data Advisory Commission (Aug 2025):**
  - About 59,000 infants (70%), 43,000 toddlers (43%) and 10,000 preschoolers (5%) live in childcare "access deserts," defined as areas with one slot per three children.
  - Central Massachusetts has regions with more than 10 children per slot.
  - Seats are most available to families in the highest income brackets.
  - — [CommonWealth Beacon, Aug 6 2025](https://commonwealthbeacon.org/newsletter/dl-08-06-25/)
- **Infant/toddler capacity** grew 5% over the prior year, but growth slowed in Central MA. Formal-care enrollment there was 48% vs 56% in the Boston area. — [Governing](https://www.governing.com/management-and-administration/vast-majority-of-massachusetts-infants-live-in-areas-lacking-child-care) (search summary)
- **UMass Boston analysis (March 2026)** found persistent shortfalls in western, central and southeastern Massachusetts, with infants and toddlers most affected. — [Hoodline, Mar 2026](https://hoodline.com/2026/03/lowell-revere-and-brockton-scramble-as-child-care-seats-run-dry/) (secondary aggregator; search summary)
- **Worcester:** a family childcare incubator (Guild of St. Agnes and Seven Hills Foundation) is placing providers in neighborhoods described as Worcester childcare deserts. — [The 74](https://www.the74million.org/zero2eight/pilot-program-provides-early-childhood-educators-with-rent-free-business-spaces/) (search summary)
- **Cape Cod:**
  - 113 of the 636 MA early-education programs that closed since March 2020 were on Cape Cod. — [Cape Cod Commission](https://capecodcommission.org/about-us/newsroom/addressing-cape-cods-childcare-shortage) (search summary; undated)
  - Cape Cod Children's Place in Eastham had about 40 families waitlisted for 28 slots (June 2024), and its director estimated more than 90% of Cape centers are in a "staffing crisis." — [Provincetown Independent](https://provincetownindependent.org/tag/child-care/) (search summary)

**Dental, Berkshires**
- **Greylock Dental opened in North Adams in Jan 2025,** citing "a shortage of options in Berkshire County." The owner said "there's just not a lot of places for all the patients to get in," attributing it to retiring dentists and hygienists. — [iBerkshires, Mar 3 2025](https://iberkshires.com/story/78162/Greylock-Dental-Opens-in-North-Adams-Aims-to-Increase-Access.html)
- **CHP Berkshires expanded its Great Barrington dental practice** because fewer private practices accept MassHealth, and it noted waits of several months for new appointments. — [iBerkshires](https://iberkshires.com/story/76889/CHP-Berkshires-Completes-Dental-Expansion.html) (search summary; date not confirmed)
- **2016 op-ed (dated):** nearly half of Berkshire dentists were nearing retirement, and the county had 2% of the state's private dental practices. — [The Berkshire Edge, May 22 2016](https://theberkshireedge.com/berkshires-state-need-accessible-dental-care-providers/)
  - This is a 10-year-old op-ed by a state representative. A search summary misdated it to March 2026, and the fetched page shows May 22, 2016.

**Home care and senior care**
- **Human-services providers had a 15% vacancy rate** for full-time client-facing roles as of Jan 2026, nearly five times the statewide job-openings rate. — [UMass Donahue Institute](https://donahue.umass.edu/news-events/institute-news/report-massachusetts-human-services-workforce-stretched-to-capacity) (search summary)
- **Half of MA nursing homes were out of compliance** with one or both state staffing standards at the end of 2025. — [WTOP, Jul 2026](https://wtop.com/news/2026/07/half-of-all-nursing-homes-in-massachusetts-are-understaffed/) (search summary)
- **Over 4,000 older adults were awaiting home care services,** mainly for lack of workers. — [WHDH 7 Investigates](https://whdh.com/news/7-investigates-home-healthcare-worker-shortage/) (search summary; undated)

**Veterinary**
- **2021, Boston:** emergency waits at Angell Animal Medical Center rose from under 1 hour (2019) to as long as 5 hours, and Angell diverted new emergencies on some nights. — [Boston Globe, Jul 9 2021](https://www.bostonglobe.com/2021/07/09/metro/overwhelmed-veterinarians-struggle-with-staggering-surge-pet-visits) (search summary)
- **Springfield:** VCA Boston Road ended 24/7 emergency care in fall 2019 because of an ER-vet shortage and closed in July 2020. — [The Reminder](https://archives.thereminder.com/localnews/GreaterSpringfield/springfields-boston-road-vca-animal-hospital-to-cl) (search summary)
  - A 24/7 emergency hospital in West Springfield (134 Capital Drive) later opened, likely Oct 2023. — [WWLP](https://www.wwlp.com/news/local-news/hampden-county/24-7-emergency-veterinary-hospital-to-open-in-west-springfield/amp/) (search summary; date inferred)
- **Aug 2024:** the Thomas J. O'Connor Animal Control & Adoption Center (Springfield) stopped accepting surrenders after losing its veterinarian, and the position had been posted since January. — [WAMC, Aug 12 2024](https://wamc.org/news/2024-08-12/national-veterinarian-shortage-felt-in-pioneer-valley) (search summary)

**Cape Cod labor and housing, and seasonal demand**
- **Year-round population** was 228,996 in the 2020 Census. — [Cape Cod Commission](https://capecodcommission.org/about-us/newsroom/initial-2020-census-results-released) (search summary)
- **Summer population** swells to more than 500,000 (informal estimate). — [Pioneer Institute](https://pioneerinstitute.org/cape-cod-the-struggles-of-year-round-residents/) (search summary)
- **47% of jobs on Cape Cod** are held by people who don't live in the region, and construction firms are among employers struggling to staff locally. — [Cape Cod Chamber of Commerce](https://www.capecodchamber.org/articles-business/post/ceo-corner-framing-the-housing-challenge-on-cape-cod/) (search summary)
- **The Concord Group (economist Tim Cornwell)** linked the lack of workforce housing to labor shortages on the Cape in retail, services and elder care. — [Cape News](https://www.capenews.net/bourne/briefs/report-warns-cape-businesses-about-lack-of-workforce-housing/article_5aea8b82-7fad-53f2-8503-1d9ef308f6be.html) (search summary; undated)

**HVAC / heat pumps (statewide demand driver for 2382 contractors)**
- **Mass Save-supported heat pump households** rose from 8,603 (2021) to 28,084 (2023). — [Mass Save](https://www.masssave.com/about/news-and-events/news/mass-save-sponsors-announce-record-number-of-heat-pump-installations-across-massachusetts) (search summary)
- **Rebates up to $10,000 require a Heat Pump Installer Network contractor** (since 2023), and network membership requires trade licensure and training. — [Canary Media](https://www.canarymedia.com/articles/enn/massachusetts-heat-pump-installer-network-has-momentum-in-second-year) (search summary)

### Inferences
- **Childcare is the gap category with the strongest multi-source evidence** (state data, UMass Boston, establishment counts) in Worcester County and the Southeast. Margins depend on staffing and on state subsidy rates (EEC C3 grants and vouchers), and the evidence says seats are scarcest for infants and toddlers and for lower-income families.
- **Berkshire dental shortage evidence is real but partly dated;** the strongest current signal is a 2025 practice opening specifically to fill a capacity gap. CBP shows Berkshire dentists at 0.91x and QCEW at 0.85x state per capita. A gap exists, but it is not extreme on establishment counts alone; the retirement wave matters more.
- **For a proven home-services operator, the Cape is better framed as a labor-constrained market than an under-supplied one.** Demand exceeds what local labor can deliver, which favors operators who can bring workforce housing or off-Cape crews.

### Gaps
- **I found no current (2025–2026) quantitative source** on contractor shortages on Cape Cod, vet shortages specific to MA regions, or dentists accepting new patients by county.
- **I did not retrieve regional planning agency reports** (CMRPC, PVPC, SRPEDD, MAPC, Cape Cod Commission CEDS), MassINC Gateway Cities research, or chamber reports with service-gap data.
- **Dental shortage designations by county were not retrieved** (HRSA HPSA data). Neither were EEC licensed-capacity data by town.

---

## 5. Cost side: commercial rents and wage levels by region

### Takeaway
- **Rent is the biggest cost advantage outside Boston.** Office asking rents are about $16–24/SF in Springfield, Worcester and Framingham, vs about $62–66/SF in Waltham and downtown Boston.
- **The wage gap is much narrower for service work than headline averages suggest.** Worcester's all-private average weekly wage is 72% of the state's, but in personal care, childcare, building services and trades it is only about 8–14% below the state rate.

### Cited Findings
**BLS QCEW 2025 annual average weekly wage, private sector.** County index vs MA in parentheses. [BLS QCEW 2025](https://data.bls.gov/cew/data/api/2025/a/area/25000.csv)

| County | All private (MA $1,959) | 8121 Personal care (MA $707) | 6244 Child care (MA $815) | 5617 Svcs to bldgs (MA $1,041) | 2382 Bldg equip. contractors (MA $2,006) | 8111 Auto repair (MA $1,215) |
|---|---|---|---|---|---|---|
| Suffolk | $2,721 (1.39) | $774 (1.09) | $957 (1.17) | $914 (0.88) | $2,445 (1.22) | $1,236 (1.02) |
| Middlesex | $2,343 (1.20) | $709 (1.00) | $839 (1.03) | $1,059 (1.02) | $2,027 (1.01) | $1,302 (1.07) |
| Norfolk | $1,676 (0.86) | $717 (1.01) | $797 (0.98) | $1,139 (1.09) | $2,308 (1.15) | $1,259 (1.04) |
| Essex | $1,493 (0.76) | $726 (1.03) | $822 (1.01) | $973 (0.93) | $1,894 (0.94) | $1,175 (0.97) |
| Worcester | $1,410 (0.72) | $609 (0.86) | $751 (0.92) | $959 (0.92) | $1,815 (0.90) | $1,162 (0.96) |
| Plymouth | $1,366 (0.70) | $731 (1.03) | $750 (0.92) | $1,143 (1.10) | $2,085 (1.04) | $1,189 (0.98) |
| Berkshire | $1,297 (0.66) | $733 (1.04) | $784 (0.96) | $826 (0.79) | $1,593 (0.79) | $980 (0.81) |
| Bristol | $1,253 (0.64) | $588 (0.83) | $723 (0.89) | $1,067 (1.02) | $1,739 (0.87) | $1,118 (0.92) |
| Barnstable | $1,243 (0.63) | $728 (1.03) | $781 (0.96) | $1,154 (1.11) | $1,668 (0.83) | $1,174 (0.97) |
| Hampden | $1,215 (0.62) | $629 (0.89) | $762 (0.93) | $870 (0.84) | $1,828 (0.91) | $1,114 (0.92) |
| Hampshire | $1,095 (0.56) | $765 (1.08) | $660 (0.81) | $932 (0.90) | $1,548 (0.77) | $1,260 (1.04) |
| Franklin | $1,068 (0.55) | N | $640 (0.79) | $908 (0.87) | $1,334 (0.67) | $1,155 (0.95) |

**Commercial rents** (vintages and methods differ; treat as indicative)
- **Worcester office:** average asking rent $22.79/SF across 117 listings. — [CommercialCafe Worcester](https://www.commercialcafe.com:443/office/us/ma/worcester) (search summary; page undated)
- **Other 2025 office asking rents:** Springfield $16.51/SF, Framingham $23.71/SF, Waltham $61.63/SF. — [CommercialCafe Springfield](https://www.commercialcafe.com/office-market-trends/us/ma/springfield/), [Framingham](https://www.commercialcafe.com/office-market-trends/us/ma/framingham/), [Waltham](https://www.commercialcafe.com/office-market-trends/us/ma/waltham/) (search summary)
- **Downtown Boston office asking rate** was $66.32/SF in Q2 2026. — [CBRE Q2 2026 Downtown Boston Office Figures](https://mktgdocs.cbre.com/2299/cff9e2d3-dcdc-4fab-a746-f83ade7f1460-414677795/Q2_2026_DT_Office_Figures_(Sho.pdf) (search summary)
- **Boston retail:**
  - Matthews' Q2 2026 report puts vacancy at 2.6% and average asking rent at about $29.00/SF. — [Matthews Q2 2026](https://www.matthews.com/insights/boston-ma-retail-market-report-q2-2026) (search summary)
  - Matthews' year-end 2025 report gave $24.93/SF. — [Matthews YE 2025](https://www.matthews.com/insights/boston-retail-2025) (search summary)
  - A 16% jump in two quarters is implausible, so the two reports likely use different geographies or bases. **Conflict noted.**
- **Downtown Worcester street-level retail** was listed at $20/SF/yr for 30,000 SF at 22 Front St (list updated Mar 24, 2025); most listings were "negotiable." — [Downtown Worcester BID](https://www.downtownworcester.org/available-retail-space/) (search summary)
- **Greater Boston industrial asking rent** reached a record $16.06/SF. — [Cushman & Wakefield](https://content.cushmanwakefield.com/api/public/content/99ba05ef792a4a00a9c9899aba6f11dd) (search summary; quarter not confirmed)
- **Worcester Regional Research Bureau:** downtown Worcester lease prices are in line with the I-495 belt, "not remotely approaching" Boston/Cambridge. — [WBJ](https://wbjournal.com/article/downtown-worcester-office-vacancy-at-12) (search summary; undated)

### Inferences
- **Labor cost for front-line service work is roughly flat across eastern MA.** Personal care wages are within about ±10% from Plymouth to Middlesex to Norfolk. Worcester, Bristol and Hampden are about 10–17% cheaper in personal care and about 7–11% cheaper in childcare and trades.
- **Rent differences are 2.5–4x for office/flex space,** so space-heavy models (childcare centers, fitness, vet clinics, salons) gain the most margin from locating in Worcester, Bristol or Plymouth County rather than Boston or the 128 belt.
- **High-cost Suffolk and Middlesex remain the toughest margin markets** despite strong demand.

### Gaps
- No apples-to-apples 2026 retail rent comparison by region (Worcester, Springfield, Brockton, New Bedford, Plymouth) was found. Regional broker reports (e.g., Kelleher & Sadowsky for Central MA, Colliers for Western MA) were not retrieved.
- MA EOLWD/MassHire occupational wage data by workforce area (e.g., OEWS for home health aides, childcare workers, HVAC techs) were not retrieved; the QCEW industry averages above are the proxy.

---

## 6. Overall ranking: which regions and towns offer the least competition relative to demand, and which categories are thin in each

### Takeaway
On a transparent composite (growth, income, permits, supply gap, labor cost), **Plymouth County (Southeastern MA) and Worcester County (Central MA)** rank first and second. They stay in the top three under every weighting I tested.

Bristol County (Taunton/Raynham corridor and South Coast suburbs) and Hampshire County come next among value markets. Middlesex and Norfolk have strong demand but average-or-better supply and the highest costs.

Hampden, Franklin and Berkshire have thin supply but weak or shrinking demand. The Cape and Islands are labor- and housing-constrained rather than under-supplied.

### Cited Findings
**County composite score.** Each indicator is min-max normalized across the 12 mainland counties; islands are excluded. Weights: population growth 25%, median income 20%, permits per 1,000 10%, supply gap 30% (inverse of the CBP 2023 composite supply index), low private wage 15% (inverse of QCEW 2025). Inputs come from the tables in Q1–Q3 and Q5 ([Census V2025](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv), [ACS 2020–24](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), [BPS](https://www2.census.gov/econ/bps/County/co2025a.txt), [CBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip), [QCEW 2025](https://data.bls.gov/cew/data/api/2025/a/area/25000.csv)); the scores are my calculations.

| Rank | County | Growth % (norm) | Income (norm) | Permits/1k (norm) | Supply idx (gap norm) | Avg wkly wage (low-cost norm) | Weighted score | Equal-weight score |
|---|---|---|---|---|---|---|---|---|
| 1 | Plymouth | 3.02 (0.99) | $114.2k (0.72) | 12.8 (0.62) | 1.09 (0.58) | $1,366 (0.82) | 0.751 | 0.746 |
| 2 | Worcester | 3.06 (1.00) | $95.9k (0.41) | 10.6 (0.47) | 0.93 (0.74) | $1,410 (0.79) | 0.722 | 0.684 |
| 3 | Norfolk | 1.89 (0.72) | $130.7k (1.00) | 10.9 (0.49) | 1.14 (0.53) | $1,676 (0.63) | 0.684 | 0.675 |
| 4 | Middlesex | 2.33 (0.83) | $130.8k (1.00) | 10.6 (0.47) | 1.04 (0.63) | $2,343 (0.23) | 0.678 | 0.632 |
| 5 | Bristol | 2.48 (0.86) | $85.6k (0.24) | 7.4 (0.26) | 0.92 (0.75) | $1,253 (0.89) | 0.648 | 0.600 |
| 6 | Hampshire | 1.08 (0.53) | $87.0k (0.26) | 10.4 (0.46) | 0.85 (0.82) | $1,095 (0.98) | 0.624 | 0.611 |
| 7 | Essex | 2.06 (0.76) | $101.9k (0.51) | 6.8 (0.22) | 1.08 (0.59) | $1,493 (0.74) | 0.605 | 0.566 |
| 8 | Suffolk* | −1.13 (0.00) | $95.6k (0.41) | 18.6 (1.00) | 0.67 (1.00) | $2,721 (0.00) | 0.482 | 0.482 |
| 9 | Barnstable** | 1.95 (0.74) | $95.2k (0.40) | 14.5 (0.73) | 1.68 (0.00) | $1,243 (0.89) | 0.471 | 0.552 |
| 10 | Hampden | −0.32 (0.19) | $71.3k (0.00) | 3.5 (0.00) | 0.73 (0.94) | $1,215 (0.91) | 0.467 | 0.409 |
| 11 | Franklin | −0.47 (0.16) | $74.9k (0.06) | 5.3 (0.12) | 0.86 (0.81) | $1,068 (1.00) | 0.457 | 0.430 |
| 12 | Berkshire | −0.62 (0.12) | $76.0k (0.08) | 5.8 (0.15) | 1.02 (0.65) | $1,297 (0.86) | 0.387 | 0.374 |

\*Suffolk's supply-gap score is structural; trades and home services are served from neighboring counties. \*\*Barnstable's supply index is inflated by the seasonal population (Q4).

- **Sensitivity check:** dropping wages and weighting demand (growth 40 / income 40 / permits 20) at 50% against the supply gap at 50% gives Middlesex 0.729, Worcester 0.701, Plymouth 0.696, Suffolk 0.682, Norfolk 0.660, Bristol 0.622. Worcester and Plymouth stay in the top 3. — my calculation from the same inputs
- **Business formation, BFS applications per 1,000 residents in 2025** (change 2019→2025): Worcester 9.0 (+52%), Hampden 8.6 (+52%), Plymouth 9.9 (+48%), Bristol 8.3 (+45%), Essex 10.4 (+39%), Norfolk 11.3 (+39%), Middlesex 11.5 (+34%), Barnstable 11.1 (+28%), Hampshire 6.9 (+29%), Suffolk 16.5 (+21%), Franklin 6.8 (+17%). — [Census BFS county annual](https://www.census.gov/econ/bfs/xlsx/bfs_county_apps_annual.xlsx)
  - Berkshire jumped from 1,078 (2019) to 2,568 (2025), with 1,613 → 2,568 over 2023–2025. The cause is unexplained and may be a filing anomaly, so treat it with caution.

**Thin categories by region**, from CBP 2023 and QCEW 2025 indices vs state per capita (below 0.85x in at least one source and not above 1.0x in the other). [CBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip); [QCEW 2025](https://data.bls.gov/cew/data/api/2025/a/area/25027.csv)

| Region | Thin service categories (CBP index / QCEW index) | Notably well-supplied (competitive) |
|---|---|---|
| Central MA (Worcester Co.) | Personal care 0.72/0.65; beauty salons 0.68/0.60; childcare 0.81/0.71 (0.79 per child <5); accounting/bookkeeping 0.77/0.67; fitness 0.76/0.73; dentists 0.89/0.83; drycleaning 0.66; residential property mgmt 0.49; tutoring 0.56; household-goods repair 0.57 | Auto repair 1.11/1.13; vets 1.08/1.06 |
| Southeastern MA (Plymouth Co.) | Dentists 0.83/0.83; home health 0.92/0.88 (0.84 per 65+); childcare 0.89/0.91 (0.87 per child <5); residential property mgmt 0.42; accounting 1.00/0.85 | Bldg-equipment contractors 1.37/1.32; auto repair; pet care 1.33/1.23; fitness 1.35 |
| South Coast & Taunton (Bristol Co.) | Home health 0.74/0.57 (0.75 per 65+); dentists 0.78/0.75; fitness 0.74/0.75; janitorial 0.87/0.69; vets 0.91/0.77; tutoring 0.34; property mgmt 0.46 | Auto repair 1.11; household-goods repair 1.54 |
| MetroWest / Merrimack Valley (Middlesex/Essex) | Near parity at county level. Town level: Lowell 0.49, Lawrence 0.75, Haverhill 0.80 composite (dentists, childcare, fitness, personal care thin in Lowell ZIPs) | Framingham, Natick, Marlborough, Woburn, Chelmsford (1.25–1.87) |
| Pioneer Valley (Hampden) | Contractors 0.69/0.66 (plumbing/HVAC 0.61); bldg finishing 0.58; personal care 0.59/0.56; pet care 0.46/0.47; vets 0.68/0.62; fitness 0.52/0.63; childcare 0.72/0.74 (0.67 per child <5); dentists 0.78/0.73 | Home health 1.08/1.04 |
| Pioneer Valley (Hampshire) | Home health 0.67/0.43 (0.62 per 65+); dentists 0.83/0.67; personal care 0.56/0.66; janitorial 0.56/0.52; accounting 0.72/0.57; bldg finishing 0.52 | Vets 1.47/1.54 |
| Franklin | Personal care 0.39; janitorial 0.34; bldg finishing 0.52; home health 0.56 (0.40 per 65+); dentists 0.63; childcare 0.65; fitness 0.49 | Vets 2.40 |
| Berkshires | Childcare 0.57/0.81 (0.74 per child <5); personal care 0.58/0.60; fitness 0.40/0.59; drycleaning 0.67; home health per 65+ 0.65; dentists 0.91/0.85 | Contractors 1.28/1.37; building services 1.34/1.53; landscaping 1.55/1.71 |
| Cape Cod (Barnstable) | Childcare 0.71/0.65; tutoring 0.37; home health per 65+ 0.73; elder services per 75+ 0.53 | Nearly all home trades (1.7–3.2x per year-round resident) |

**Top town and cluster candidates** (growth 2020–25 / median HH income / ZIP supply index, from the tables above):

| Cluster | Town | Growth 2020–25 | Median HH income | ZIP supply index |
|---|---|---|---|---|
| Central MA Route 9 / I-495 / Blackstone Valley | Grafton | +7.0% | $131.5k | 0.49 (Grafton) / 0.95 (N. Grafton) |
| | Upton | +7.0% | $155.5k | 0.68 |
| | Douglas | +6.3% | $152.3k | 0.38 |
| | Uxbridge | +4.3% | $124.7k | 0.79 |
| | Millbury | +3.2% | $118.8k | 0.56 |
| | Sutton | +3.1% | $147.1k | 0.98 |
| | Shrewsbury | +3.4% | $139.3k | 1.00 |
| | Westborough | +6.2% | $141.9k | 1.43 |
| North Worcester County / Wachusett | Rutland | +8.1% | $145.7k | 0.41 |
| | Lancaster | +8.3% | $134.8k | 0.25 |
| | Westminster | +7.2% | $106.3k | 0.55 |
| | Holden | +2.9% | $141.9k | 1.13 |
| Worcester city (volume, mid-income) | Worcester | +7,354 people | $70.1k | 0.75 |
| Plymouth corridor | Plymouth | +10.8% | $116.9k, 25.2% aged 65+ | 1.20, but childcare ZBP 2.2 vs 2.99 state |
| | Kingston | +6.2% | $119.9k | 1.64 |
| | Lakeville | +7.9% | $134.0k | 1.30 |
| | Middleborough | +3.7% | $97.1k | 1.07 |
| Taunton/Raynham/Rehoboth | Taunton | +5.3% | $79.3k | 0.76 |
| | Raynham | +9.3% | $124.0k | 1.40 |
| | Rehoboth | +8.5% | $138.2k | 1.07 |
| Norfolk–Worcester border | Millis | +11.8% | $156.0k | 0.74 |
| | Bellingham | +6.4% | $125.3k | 1.19 |
| | Medway | +5.3% | $173.8k | 1.33 |
| Merrimack Valley gateway (volume, thin supply) | Lowell | +4,375 people | $78.7k | 0.49 |
| | Chelmsford | +6.0% | $140.6k | 1.48 (well supplied) |

— [Census V2025 sub-county](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025_25.csv); [ACS 2020–24](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/); [ZBP 2023](https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip)

### Inferences
**Recommended ranking of regions** for a proven service business seeking the least competition relative to demand (verified data plus my judgment):
1. **Central MA / Worcester County.** It has the highest growth (+3.06%, +26.4k), the second-largest 2024–25 absolute gain (+4,780), and the most new units outside the Boston core (9,430). Supply is below average in many consumer categories, with the gaps corroborated by state childcare data. Office rents are about $20–23/SF and service wages are 8–14% below the state rate.
   - Best sub-markets: the Shrewsbury/Westborough/Grafton/Northborough/Upton/Millbury/Sutton ring (high income, thin local supply) and Worcester city (volume; immigrant-driven growth; price-sensitive).
   - Thin: salons/personal care, childcare (especially infant/toddler), bookkeeping/tax, fitness/boutique studios, dentists, drycleaning/laundry pickup, residential property management, tutoring.
2. **Southeastern MA / Plymouth County.** It has growth of +3.02%, income of $114k, the most single-family permitting per capita on the mainland, net domestic in-migration from Greater Boston, and an older population (Plymouth town 25.2% aged 65+).
   - Thin: dentists, home health/senior care, childcare, property management.
   - Not thin: home trades (HVAC/plumbing 1.36x), which are competitive.
3. **Bristol County (Taunton/Raynham/Rehoboth and the Dartmouth/Westport/Swansea/Somerset South Coast suburbs).** It has growth of +2.48%, rising permits (1,156 in 2025, a 5-year high) and positive domestic migration. Costs are low (all-private wage $1,253/week, personal care $588/week), and the South Coast suburbs are old (21–25% aged 65+).
   - Thin: home health (0.57–0.75x), dentists, fitness, commercial janitorial, vets, tutoring.
   - Lower income ($85.6k) means price points must be moderate.
4. **Hampshire County / Northampton–Amherst.** It has positive domestic migration and is the cheapest labor market in the east-west comparison.
   - Thin: home health, dentists, personal care, janitorial, accounting.
   - College populations distort per-capita measures, and the county is small (164k).
5. **Merrimack Valley Gateway Cities (Lowell, Lawrence, Haverhill).** These cities are thin at the town level, and Lowell is growing fast, but they have mid-to-low incomes. The surrounding suburbs (Chelmsford, North Andover, Methuen) are well supplied.
6. **MetroWest core (Framingham, Natick, Marlborough) and Norfolk/Middlesex generally.** Demand is high, but supply indices of 1.25–1.9 at the town level and the highest wages and rents make them the most competitive. The exception is Hopkinton ($222.8k income, +5.9%, index 1.07).
7. **Cape & Islands.** Per-capita supply is high because of the seasonal population, but the binding constraint is labor and housing. Childcare (0.65–0.71x) and elder/home-health services relative to an extremely old population are the clearest year-round gaps.
8. **Pioneer Valley urban (Springfield, Holyoke, Chicopee), Berkshires and Franklin.** These have the thinnest supply but shrinking population and the lowest incomes.
   - Gaps (childcare, dentists, vets, pet care, trades in Hampden) exist mostly in payer-driven or price-constrained segments.
   - Berkshire dental and childcare gaps are documented, but the market is small (128k) and shrinking.

**Two caveats on the town picks:**
- A thin ZIP index in small bedroom towns (Lancaster, Rutland, Douglas) partly reflects that residents use services in nearby hubs. These towns are best treated as service areas for mobile and in-home models, not storefront locations.
- Worcester County's growth is mostly international in-migration, while Plymouth and Bristol draw domestic movers from Greater Boston. The two customer bases differ (renters, younger and multilingual vs owners, older and higher-income), which should shape which service fits where.

### Gaps
- The composite weights are my judgment; there is no standard index for this. The underlying numbers are shown so they can be reweighted.
- The supply side lacks nonemployer (sole-proprietor) counts and franchise/chain presence, and CBP is 2023 data (QCEW 2025 used as a cross-check).
- Category-specific demand drivers were not quantified by region: pet ownership rates, childcare-age births by town, Medicare Advantage/MassHealth home-care authorizations, and heat-pump installs by town (Mass Save town-level data).
- Seasonal (Cape and Islands) and student (Amherst, Northampton, Worcester colleges) populations distort per-capita measures, and I did not adjust for them.
