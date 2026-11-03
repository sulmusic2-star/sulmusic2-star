# New York wave 2: the battery belt, the data-center towns and the county route

Written Nov 3, 2026 from the wave-2 engineer's hand-back. Outputs under `projects/351watch/data/test/wave2/`; the production list is `data/towns_ny.json`.

## What changed on the live site

- `data/towns_ny.json` went from 57 places (33 read every morning) to 79 places (55 read every morning): the wave-1 rows that read cleanly were promoted, with the rest kept in the gated config with a precise reason.
- The county 239-m referral route is in: 40 county planning boards discovered, 6 readable today (Allegany, Chemung, Greene, Lewis, Livingston, Orleans); their items are filed under the township they concern, so a town with no site of its own still shows its zoning changes and moratoriums.

## The engineer's report

Wave 2 NY: county route, extended-window crawl and precision sample are finished. Outputs under data/test/wave2/.

**County websites** (targets_ny.json): 40/45 counties now have a site (Suffolk set from the infobox probe; the Wikipedia job found Saratoga, St. Lawrence, Sullivan, Ulster, Washington, Westchester, Wyoming). Still none: Schenectady, Schoharie, Steuben, Tompkins, Wayne.

**County discovery** (40 county rows in config/towns_ny.json): 6 automated â Allegany, Chemung, Greene, Lewis, Livingston, Orleans. Reasons for the rest: no_agendas_found 16, no_recent_agendas 5 (Essex, Cattaraugus, Saratoga, St. Lawrence, Wyoming), bot_challenge 5 (Cayuga, Chenango, Ontario, Orange, Washington), vendor_blocked 5 (Cortland iqm2, Oneida primegov, Erie destiny, Ulster and Westchester granicus), robots_disallow 2 (Genesee, Montgomery), waf_block 1 (Delaware).

**Crawls into ny_extended/** (140 days back / 120 ahead): towns run 28/28 ok, 86 new hits, 183 MB, 312 s, 88 doc errors (not characterized), 4 need OCR â runs/run_extended.json. County run 6/6 ok, 40 new hits (36 current; moratorium 21, battery_storage 10, data_center 10, solar 8, wireless 5, zoning_amendment 4) â runs/run_counties.json. hits_ny_wave2.json: 104 current hits over 45 documents, meeting dates 2026-07-08..2026-11-05; county hits attribute to townships (New Hudson 8, Amity, Turin, Athens, Greig, Port Leyden, â¦).

**Bug fixed in experiments/wave2_test.py** (`cmd_discover` county_body fix-up): the generic page label "County Planning Board" (Lewis, Orleans) passed the `re.search("county")` check and became the county_body, so 3 places' coverage_county_body and 17 hits were ambiguous. Now the label must contain the county's name. Patched the two config rows and their listing labels, patched 10 records in ny_extended/state/docs/NY/*.jsonl, and a regen crawl (runs/run_counties_regen.json, 0 network requests) relabelled the hits file: 0 generic labels left. Earlier edit in the same file: county target rows now take their website from WEBSITES[...].

**Annotate:** config + production places: direct 83, via_county 6, none 71. Config places alone: direct 28, via_county 5 (AthensâGreene, Turin and LewisâLewis, CarltonâOrleans, AllenâAllegany), none 48.

**Precision sample:** data/test/wave2/worksheet_ny.json â pool 112, n 40, seed 2031, source ny_extended; 15 of 40 are county-board items; topics moratorium 21, battery_storage 16, solar 11, data_center 8, wireless_telecom 2, zoning_amendment 1; towns incl. North Elba 5, Bergen 4, New Hudson 4, Elba 3, Lake George 3. (Pool 112 vs 104 in hits file: the sample reads idx.current_hits() directly; not investigated.)

## What is left

- The 5 behind bot walls, 5 vendor-blocked and 2 robots-closed counties, and the 24 towns we cannot read, have unblock drafts in `ny_unblock_drafts.md` (the owner sends them). The 5 counties filed as "no website found" (Schenectady, Schoharie, Steuben, Tompkins, Wayne) need a discovery pass from the production host; four of the five answered a probe on Nov 3, see the last section of that file.
- 88 document errors in the extended crawl are not yet characterised; the posting lead time for the new places should be read off the next two weeks of runs.
