# MassDEP wetlands filings as a 351 Watch source

*Built Oct. 10–11, 2026. Code: `projects/351watch/crawler/watch351/sources/massdep.py`. Outputs: `projects/351watch/data/sources/massdep_*.json(l)`.*

## Bottom line

<!-- RESULTS -->

## What the source is

- **What gets filed:** under the Wetlands Protection Act (M.G.L. c. 131 §40, 310 CMR 10.00), anyone working in or near a wetland files with the local Conservation Commission and sends a copy to MassDEP:
  - a Notice of Intent (NOI);
  - a buffer-zone-only NOI;
  - or an ANRAD, which asks the commission to confirm wetland boundaries before a project is designed.
- **What MassDEP records:** it assigns a DEP file number and logs the filing in WIRe/eDEP. The record shows the applicant and the fee check ("CK#5707 NEW LEAF ENERGY"). When the Commission rules, it adds the Order of Conditions (or ORAD) date.
- **Why this matters for 351 Watch:**
  - **Leading indicator.** The Commission must open its hearing within 21 days of the filing (310 CMR 10.05(5)(b)). The hearing then usually runs over 2–4 sessions.
  - **Ownership.** For solar, BESS, substation and data-center projects, the applicant is usually a single-project LLC. The fee-check payor or the LLC name often reveals the developer behind it, or its engineer.

## Endpoints (confirmed Oct. 10, 2026)

The public search page `https://eeaonline.eea.state.ma.us/portal#!/search/wire` (EEA Data Portal, "Wetland Notice of Intent Projects") is an AngularJS app.
- **How I found the API:** it reads its API base from a public `<meta name="data-lake-api-url" content="/EEA/DataLake/V1.0/DataLakeAPI/">` tag. Its `searchApi` service (`/Portal/dist/scripts/custom.js`) makes plain `$http.get` calls with **no API key, token, cookie or login**.
- **What I did not do:** I did not extract or use anything embedded. The page carries a Google Maps key, and the separate MEPA eMonitor app uses an encrypted AWS key; I touched neither. I call only the same URLs a browser calls.

| Purpose | Request | Returns |
|---|---|---|
| List / search | `GET /EEA/DataLake/V1.0/DataLakeAPI/wire?FromFilingDate=2026-10-01T00:00:00.000Z&ToFilingDate=2026-10-11T00:00:00.000Z&_start=0&_end=200&ColumnName=FilingDate&Direction=asc` (optional `TownId`, `NOINum`) | `{"Items":[{NOIId, NOINum, FilingDate, ApplicantName, Company, OOCDate, TownName, ProjectAddress}], "TotalCount": n}` |
| Detail | `GET /EEA/DataLake/V1.0/DataLakeAPI/wire/{NOIId}` | `{FilingType, ProjectType, ApplicantInformation, ProjectAddress, NOINum, FilingDate, OOCDate, SOCRequest, InlandResourceAreas[], CoastalResourceAreas[], Comments, TechnicalComments}` |
| Excel export (browser button) | `GET …/wire/export-to/excel?…` | the list columns only, no detail fields, so it cannot replace detail calls |
| Public record page (for links) | `https://eeaonline.eea.state.ma.us/portal#!/wire/{NOIId}` | the human-readable detail page |

**Field notes:**
- **`FilingType`** is one of `NOI`, `Buffer Zone` or `Anrad Delineation`.
- **`OOCDate`** is the date of the Commission's decision: an Order of Conditions, or an ORAD for an ANRAD.
- **`NOINum`** is the DEP file number, `TTT-NNNN` (town code and sequence). It is empty for the first days after filing.
- **`SOCRequest = YES`** means someone asked MassDEP for a Superseding Order, i.e. appealed the local decision.
- **`Comments`** holds the project description, written by DEP staff in upper-case shorthand ("BUILD SFH", "W/", "SW IMP"). It is followed by `//`-separated bookkeeping:
  - the fee-check note (`CK#36579 BEALS & THOMAS`);
  - internal codes (`#WC-52-21`);
  - eDEP transaction ids;
  - `PD ONLINE`.
- **The API has no hearing date.** The Commission's hearing date is not in this API.

## Terms, robots and rate limits

- **robots.txt:** `https://eeaonline.eea.state.ma.us/robots.txt` redirects to `/Portal/robots.txt`, which returns **404**. Under RFC 9309 that means no restrictions.
- **Portal conditions of use** (Help page text in the app bundle):
  - Users agree to the agency's website policies (EEA Terms of Use, Privacy and Social Media policies).
  - The data "has not been fully verified for accuracy and/or completeness". The agency "assumes no obligation to either maintain or update" it.
  - The data should not be relied on to determine compliance.
- **Mass.gov Terms of Use:** material on Commonwealth websites that anyone can reach without a PIN or password is public record. Most of it can be copied and used for any purpose; third-party copyrighted material is the exception.
  - **How confirmed:** I confirmed this through a search summary of `https://www.mass.gov/massgov-terms-of-use`.
  - **Not read directly:** mass.gov answers **HTTP 403** to the 351WatchBot user agent, even for robots.txt, and also to the research fetch tool. I did not work around that block. Someone should read the page in a normal browser before a public launch.
- **Rate limits:** none are published, and the API sends no rate-limit headers.
  - **Our ceiling:** we stay at **≤1 request/second** (1.05 s spacing) and identify as `351WatchBot/0.1 (+contact: hello@351watch.example)`.
  - **On errors:** we back off on 429/5xx (honoring `Retry-After`), stop the run on any 401/403, and stop after 5 consecutive failures.
  - **Backfill cost:** about 4,650 requests over ~80 minutes, with no errors or throttling.

## Method

**Incremental fetch** (`python3 -m watch351.sources.massdep [--since YYYY-MM-DD] [--until …] [--offline] [--refresh-pending]`):
1. **Pick the date range.** The cursor in `data/sources/massdep_state.json` holds the newest filing date seen. Each run re-lists from 45 days before the cursor to today, so late entries and newly assigned file numbers or decisions are caught. The first run covers 365 days back; `--since` overrides.
2. **List the filings.** Listing uses one-week filing-date windows, at ≤200 rows per request. A window that would overflow is split instead of paged, which avoids unstable paging when many filings share a date.
3. **Fetch details.**
   - A detail request is made only for a new filing, or when its list row changed. The list row is fingerprinted; the fingerprint changes when a file number is assigned, a decision date added, or a name or address edited.
   - Recent filings (≤30 days) that still have no description are re-checked every 2+ days, because DEP often adds the description later.
   - Raw API JSON is cached in `crawler/.cache/massdep/raw/` (git-ignored), so `--offline` can rebuild every output with improved parsers and make no requests.
4. **Write the outputs:**
   - `massdep_filings.jsonl`: every filing, one minimal record each, with:
     - town, county, DEP file number, filing type and project type;
     - received (filing) date, issued (decision) date and status;
     - superseding-order flag;
     - applicant, payor, project address, description and resource areas;
     - public `source_url`, `first_seen`, classification and parent.
   - `massdep_hits.json`: energy and data-center filings in the `hits_current.json` hit shape, with extra fields under `details`. `watch351.current` already merges `data/sources/*_hits.json` and keeps only the contract fields.
   - `massdep_entities.json`: parent developers, project applicants with their links and evidence, and the most frequent third-party fee payors across all filings.

**Personal data:**
- Filings by private individuals (homeowners) are kept as minimal records, but the names are not stored: applicant and payor become `"[individual]"`. This matches the approach in `ma_target_companies.csv`.
- On company filings, the contact person's name is stored only as a salted 12-hex hash (`contact_key`). It is used only to link LLCs that share a contact.
- DEP's technical review comments are not stored, only a flag that they exist.

<!-- CLASSIFICATION -->

<!-- LINKING -->

<!-- LIMITATIONS -->
