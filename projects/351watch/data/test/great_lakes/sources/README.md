# Sources for the Great Lakes wave targets (2026-11-02)

- `wikipedia_township_lists.json`: the township rows of Wikipedia's "List of townships in Michigan" and "List of townships in Ohio" (name, county, type, 2020 population, article URL), read once with PoliteFetcher. Used for the township lists of the twelve southeast Michigan counties and the eight Ohio counties.
- `county_census_rows.json`: the OH and MI rows of `research_notes/Meeting monitor national expansion/coverage_county_census.csv` (county websites, from Wikidata P856, probed 2026-10-11/12).
- `township_sites.json`: official website per township row (`"ST:County:Row name"` -> `{website, source[, note]}`), merged by `merge_sites.py` (kept in the scratch directory; the merge order is the `source` field) from:
  1. hand-recorded web-search results (`websearch_sites.json`): one WebSearch per township; the site is taken only when the search digest names it and ties it to the right county; `null` = no township site found by search;
  2. Licking County's own per-township zoning pages (lickingcounty.gov/depts/planning/zoninginfo/<twp>.htm, "Website" link);
  3. one Wikipedia infobox (Allen Township, Union County): Wikimedia answered HTTP 429 to the bot after two requests at 1 req/s and again at 1 req/5 s, so Wikipedia was not read further;
  4. county government township-link pages (Livingston, Oakland, Franklin, Delaware, Clermont zoning pages) and regional agency member pages (LUC Planning for Logan/Union/Champaign, Macomb County's communities page, Tri-County RPC), plain GETs through PoliteFetcher.
- The Michigan Townships Association directory (find-a-township/?fips=NNNNN) was tried with the Census county-subdivision FIPS codes; after one page it served a "please wait while your request is being verified" interstitial to the bot, so it was not used (never bypassed).
