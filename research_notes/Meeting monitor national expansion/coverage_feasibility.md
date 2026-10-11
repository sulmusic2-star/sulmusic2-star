# Coverage feasibility: automated agenda reading for siting bodies in candidate US states

*Status: IN PROGRESS (2026-10-11). Sections are filled as probes finish. Sample tables are CSVs in this folder.*

Labels used throughout: **verified** (checked directly this session with a plain HTTP request from 351WatchBot, robots.txt obeyed, at most 1 request/second/host), **secondary** (from a vendor, association, statute or news page read this session but not independently tested), **estimate** (my inference from the verified and secondary material).

## Method (draft)

- County census: every county website listed in Wikidata (P856) for 26 states was fetched with the crawler's own `PoliteFetcher` (351WatchBot UA, robots.txt checked on every redirect hop, >=1.05 s between requests to a host, crawl-delay cap 10 s, no logins, no challenge solving). For each site: home page plus up to 6 same-site pages whose links look like agendas, meetings or the governing body. Vendor portals linked from those pages were recorded and checked separately.
- Township/municipal samples: 8-12 siting-relevant jurisdictions per priority state.
- State-level feeds: each tested for machine readability (API, CSV, RSS) and currency.

(Results pending.)
