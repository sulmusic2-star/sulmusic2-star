# Analog patterns: what Agenda Ahead should borrow

Research date: 2026-10-12. Method: visited each site as a signed-out visitor, a few page loads each, with Playwright Chromium (`/opt/pw-browsers/chromium-1194`) at 1440x900 desktop and 390x844 phone. No accounts, no scraping beyond reading the pages viewed. Sites that showed a bot check, refused the connection or were down are listed as skipped.

Screenshots: `/tmp/claude-0/-home-user-sulmusic2-star/815cfdd0-e090-5147-aee8-a5db345f6b5d/scratchpad/analogs/` (file names below; `_desktop.png` is 1440 wide, `_390.png` is the phone view at 2x, both cut off at about 2,200 to 2,600 CSS px).

Companion note: `human_design_brief.md` in this folder (live-site audit of agendaahead.vercel.app).

**Main finding.** The closest analog, PlanningAlerts, has the same problem we have: it prints the council's raw description in full for every item. The sites that read well to ordinary people (CPSC recalls, Boston's project pages, Zillow, weather.gov, GovTrack) put a short summary written to a fixed pattern first, then a few labeled facts, then a status in words with "what happens next". The official wording sits behind a link. For us that means three things: a fixed one-line item format, a 4-stage tracker, and an alert signup that shows a preview and asks only for an email.

---

## 1. Sites at a glance

| Site | What it does | Pattern worth stealing | Screenshot(s) |
|---|---|---|---|
| PlanningAlerts.org.au ([home](https://www.planningalerts.org.au/), [results](https://www.planningalerts.org.au/applications/address?q=24+Bondi+Road%2C+Bondi+NSW+2026), [item](https://www.planningalerts.org.au/applications/3571765)) | Development applications within 2 km of an address, emailed | Home asks one question ("What is being built and knocked down in your area?") with one address box and "or use my current location". The "Save this search as an email alert [Save]" bar sits right above results. Item meta line: "3 days ago, 890 m away". Provenance sentence: "We found this application on the planning authority's website on 10 October 2026, 3 days ago. It was received by them 12 days earlier." "949 people were notified of this application." **What to avoid:** full raw council text in every list row (results page 15,408 px tall on a phone), and Save now leads to "Create an account or sign in." | `planningalerts_home_desktop.png`, `planningalerts_home_390.png`, `planningalerts_address_desktop.png`, `planningalerts_address_390.png`, `planningalerts_item_390.png`, `planningalerts_save_desktop.png` |
| UK PlanIt ([home](https://www.planit.org.uk/)) | National aggregator of UK planning applications | Admits its coverage gaps: "Currently 417 planning authorities are available (although currently more than 30 of these are not up to date)." **What to avoid:** a 417-name A-to-Z list on the home page, and a picker that offers "Rectangle Circle Postcode Boundary Area Identifier". | `planit_home_desktop.png`, `planit_home_390.png` |
| UK council weekly lists (Idox) | Weekly list of new applications per council | Skipped. Brighton & Hove showed an Imperva hCaptcha bot check; Manchester was refused by the network proxy. | none |
| Seattle Land Use Information Bulletin | Seattle land-use notices | Skipped. Both `web.seattle.gov/sdci/luib/` and `seattle.gov/sdci/permits/land-use-information-bulletin` returned 404. | none |
| NYC ZAP ([search](https://zap.planning.nyc.gov/projects), [project](https://zap.planning.nyc.gov/projects/2023Q0364)) | NYC zoning applications, with email notifications | Each row has a plain name ("31-10 & 31-16 Hunters Point Ave Rezoning"), the applicant, a summary cut at about 150 characters with "...", place tags ("Queens \| CD 2") and a date. The map legend has 4 stages: Noticed, Filed, In Public Review, Completed. **What to avoid:** a modal on page load, 12 jargon filters ("RACIAL EQUITY REPORT APPLICABILITY", "ULURP TYPE", "CEQR"), and 14 milestones on the project page. | `nyc_zap_desktop.png`, `nyc_zap_390.png`, `nyc_zap_project_desktop.png` |
| NYC ZoLa ([map](https://zola.planning.nyc.gov/)) | Zoning and land-use map | Little to borrow. It opens with a "new features" carousel and layer toggles ("Tax Lots", "Zoning Districts"). | `nyc_zola_desktop.png`, `nyc_zola_390.png` |
| Boston Planning ([list](https://www.bostonplans.org/projects/development-projects), [project](https://www.bostonplans.org/projects/development-projects/74-ashton-street)) | Development projects under review | One-line description: "Four story apartment building with 24 units and 16 parking spaces". Fact strip: Neighborhood, Address, Land Sq. Feet, Gross Floor Area, Contact. A vertical "Project Phase" stepper (Letter of Intent > Under Review > Board Approved > Under Construction > Construction Complete) marks the current step. Deadline above the form: "Comment period ends Nov 09, 2026". List rows carry a status chip (UNDER REVIEW). | `boston_planning_desktop.png`, `boston_planning_390.png`, `boston_project_desktop.png`, `boston_project_390.png` |
| SF Property Information Map ([map](https://sfplanninggis.org/pim/)) | Parcel and permit lookup | One box: "Search by address, parcel or planning application number, or click on the map". **What to avoid:** a blank map as the whole first screen. | `sf_pim_desktop.png`, `sf_pim_390.png` |
| Toronto Application Information Centre ([page](https://www.toronto.ca/city-government/planning-development/application-information-centre/)) | Active development applications, ward subscriptions | States how fresh the data is ("data is refreshed daily") and offers ward-level alerts ("Subscribe to receive updates of new development applications in a specific Toronto ward"). **What to avoid:** a legend made of body names (Community Planning, Committee of Adjustment, Toronto Local Appeal Body). | `toronto_aic_desktop.png`, `toronto_aic_390.png` |
| Chicago Councilmatic ([home](https://chicago.councilmatic.org/), [meetings](https://chicago.councilmatic.org/events/), [item](https://chicago.councilmatic.org/legislation/o2026-0029019/)) | City council legislation and meetings, "demystified" | A **"Non-Routine" tag** separates real items from disabled-parking permits. A "What are these meetings?" box sits beside the meeting list. "Next City Council meeting: Wed 10/14/2026 10:00a.m." is on the home page. Item pages have "RSS updates for this legislation" and "View on the Chicago City Clerk website". NYC Councilmatic was refused by the proxy. | `councilmatic_chicago_desktop.png`, `councilmatic_chicago_390.png`, `councilmatic_chicago_meetings_desktop.png`, `councilmatic_bill_desktop.png` |
| Utah Public Notice Website ([home](https://www.utah.gov/pmn/)) | Every public body's meeting notices | Opens with "Meetings and Events Around Me", already filtered ("Showing Upcoming Events for ZIP Code 84111."). **What to avoid:** notices titled just "Agenda", and a 3-step cascade (Government Type > Entity > Public Body). | `utah_pmn_desktop.png`, `utah_pmn_390.png` |
| GovTrack.us ([bill](https://www.govtrack.us/congress/bills/119/hr1), [start](https://www.govtrack.us/start)) | Bill status and alerts | Status line: "Enacted — Signed by the President on July 4, 2025", then a plain sentence. Each history step says what comes next: "Passed House (Senate next). The bill was passed in a vote in the House. It goes to the Senate next." Source is labeled ("Source: Congress.gov"). Each section has one "Track ... to be alerted when ..." sentence. | `govtrack_bill_desktop.png`, `govtrack_bill_390.png`, `govtrack_alerts_desktop.png` |
| Plural / Open States ([MA bills](https://openstates.org/ma/bills/), redirects to pluralpolicy.com) | State bill tracking | Every row has a status tag (INTRODUCED), "LATEST ACTION: OCTOBER 13, 2026" and a TRACK button. **What to avoid:** the sort puts routine filings first ("A communication from the Office of the Comptroller..."), out of 19,518 results. | `openstates_ma_desktop.png`, `openstates_ma_390.png` |
| TheyWorkForYou ([home](https://www.theyworkforyou.com/)) | UK Parliament record and alerts | Hero: "Understand who represents you", with "Create and manage email alerts" as the first link under it. The alert and MP pages returned 503 on the day. | `theyworkforyou_home_desktop.png`, `theyworkforyou_home_390.png` |
| FixMyStreet ([home](https://www.fixmystreet.com/)) | Report street problems to the council | Location box with an example: "Enter a nearby UK postcode, or street name and area: e.g. 'B2 4QA' or 'Tib St, Manchester'", plus "Use my current location". 4-step "How to report a problem". "Recently reported problems" shows times like "20:15 today". "Local alerts" is in the top nav. The `/around` and `/alert` pages were down (503). | `fixmystreet_home_desktop.png`, `fixmystreet_home_390.png` |
| USPS / UPS tracking | Package status | Skipped. USPS rendered a blank page in headless Chromium at both widths. | none |
| FlightAware ([UA1](https://www.flightaware.com/live/flight/UAL1)) | Live flight status and alerts | On a phone the status headline comes first: "EN ROUTE AND ON TIME / Arriving in 2 hours 14 minutes". Below it is one progress bar with "14h 30m elapsed / 2h 14m remaining", and "updated a few seconds ago". **What to avoid:** a cookie banner plus an "Unlimited Flight Alerts" upsell covering half the first screen. | `flightaware_flight_desktop.png`, `flightaware_flight_390.png` |
| CPSC Recalls ([list](https://www.cpsc.gov/Recalls)) | Product recalls | Headlines follow one formula: "[Company] Recalls [Product] Due to [Hazard]". Every item has the same labeled fields (Hazard, Remedy, Units, Consumer Contact). | `cpsc_recalls_desktop.png`, `cpsc_recalls_390.png` |
| Google Alerts ([page](https://www.google.com/alerts)) | Keyword alerts by email | The page is one box ("Create an alert about..."). Typing a topic brings up an **Alert preview** of what you would get, plus an email field, a "Create Alert" button and a collapsed "Show options". When nothing is new it says: "There are no recent results for your search query. Below are existing results that match your search query." | `google_alerts_desktop.png`, `google_alerts_preview_desktop.png`, `google_alerts_preview_390.png` |
| Zillow ([search](https://www.zillow.com/amherst-ma/), [listing](https://www.zillow.com/homedetails/33-Gaylord-St-Amherst-MA-01002/56256098_zpid/)) | Home listings, saved searches | "Save search" is the only filled button in the filter row. Cards show "4 bds \| 4 ba \| 2,787 sqft \| House for sale". A change badge sits on the card: "Price cut: $49,900 (9/29)". Listings show "What's special" chips (STONE PATIO, COZY STUDIO) above the description, and the description is cut off with "Show more". Freshness and source: "Zillow last checked: 7 hours ago / Listing updated: October 09, 2026 / Source: MLS PIN". A two-button bar (Contact, Request a tour) stays on screen. | `zillow_city_390.png`, `zillow_city_desktop.png`, `zillow_listing_390.png`, `zillow_listing_desktop.png` |
| Redfin ([01002](https://www.redfin.com/zipcode/01002)) | Home listings, saved searches | 3 highlights pulled from the long description, placed under the address: "Queen anne victorian • Screened side porch • Modern kitchen". "Save search" sits in the filter row. | `redfin_zip_desktop.png`, `redfin_zip_390.png` |
| Google Flights / Kayak ([Flights](https://www.google.com/travel/flights?hl=en), [Kayak](https://www.kayak.com/flights)) | Price tracking | Google pitches the alert to people not ready to act: "Not ready to book yet? Observe price changes for a route or flight and get notified when prices drop." Kayak's `/price-alerts` was a 404, and its flights page only has an FAQ entry ("How can I track the price of a flight?"). | `google_flights_desktop.png`, `kayak_home_desktop.png` |
| weather.gov ([Amherst forecast](https://forecast.weather.gov/MapClick.php?lat=42.3732&lon=-72.5199), [alerts](https://www.weather.gov/alerts)) | Forecasts and hazard alerts | A glance strip comes first (Tonight / Tuesday / Tuesday Night, each with an icon, "Low: 52 °F" and a 3-word phrase). Then the "Detailed Forecast" in plain sentences, then "Text Only Forecast" and "Printable Forecast" links. "Last update 12 Oct 3:55 pm EDT". | `weathergov_point_390.png`, `weathergov_point_desktop.png`, `weathergov_alerts_desktop.png` |
| USGS Earthquake Notification Service ([ENS](https://earthquake.usgs.gov/ens/)) | Earthquake email/SMS alerts | Offers 3 typical setups in plain words: "Large earthquakes anywhere in the world / Moderate earthquakes in the U.S. / Earthquakes of any size near you". Every message type links to an "Example ... Message". Messages are "a short text summary plus a link to the full product". **What to avoid:** "one earthquake can generate up to five notifications", and a username/password login form on the landing page. | `usgs_ens_desktop.png`, `usgs_ens_390.png` |
| AirNow ([Amherst](https://www.airnow.gov/?city=Amherst&state=MA&country=USA)) | Air quality now and forecast | When current data is missing it says "Not Available" and still shows "Forecast AQI: Today Good / Tomorrow Good" as colored dots. One action sentence: "Enjoy your outdoor activities." Credits the source: "Forecast courtesy of Massachusetts Dept. of Environmental Protection". | `airnow_390.png`, `airnow_desktop.png` |
| Nextdoor public city page ([Amherst](https://nextdoor.com/city/amherst--ma/)) | Neighborhood posts | A "Where is this data from?" link sits next to its town stats. Posts show neighborhood + "1d" + "See more" truncation. **What to avoid:** made-up scores ("Safety: 67, Affordability: 96"). | `nextdoor_city_desktop.png`, `nextdoor_city_390.png` |
| Patch ([Newton](https://patch.com/massachusetts/newton)) | Town news | The town name and a "Subscribe" button are always in the header. A named human editor ("Edited by Benjamin Pierce"). Kicker line: place \| category \| age ("Newton \| News \| 14h"). **What to avoid:** sponsor cards and other towns' stories ("Salem Halloween 2026") mixed into the Newton feed. | `patch_town_390.png` |
| Citizen ([site](https://citizen.com/)) | Real-time safety alerts | Notification format: source + age, headline, place ("4m ago / Oil Tanker Crashed, Gallons Spilling Into River / Boyle Heights, Los Angeles"). **What to avoid:** an alarm tone ("live video from the scene"). | `citizen_home_desktop.png`, `citizen_home_390.png` |
| PulsePoint ([site](https://www.pulsepoint.org/)) | CPR and emergency alerts | "LAST 24 HOURS" counters (275 CPR-needed activations, 916 nearby responders). Little else to borrow: the site is mostly marketing. | `pulsepoint_home_desktop.png`, `pulsepoint_home_390.png` |
| SeeClickFix ([New Haven](https://seeclickfix.com/new-haven)) | 311-style requests | A **"Nearby Service Providers"** section (Bridgeport, Middletown), and a track record on each card ("151,326 Requests Resolved All Time"). **What to avoid:** huge logo cards that push the content down on a phone. | `seeclickfix_city_390.png`, `seeclickfix_city_desktop.png`, `seeclickfix_issue_desktop.png` |
| Carfax ([reports](https://www.carfax.com/vehicle-history-reports/)) | Vehicle history summaries | "Every CARFAX Vehicle History Report Checks for..." followed by the categories (Accident Data, Service History, Type of Use, Ownership History). The sample-report URL returned 404, so the report summary itself was not seen. | `carfax_vhr_desktop.png`, `carfax_vhr_390.png`, `carfax_home_desktop.png` |
| Wikipedia infobox ([Amherst, MA](https://en.wikipedia.org/wiki/Amherst,_Massachusetts)) | Key facts per entity | The same labeled rows on every town (County, Settled, Government Type, Population, Website). The article also spells out neighbors: "bordered by Hadley to the west, Sunderland and Leverett to the north, Shutesbury, Pelham, and Belchertown to the east, and Granby and South Hadley to the south". | `wikipedia_town_desktop.png`, `wikipedia_town_390.png` |
| Google Maps place panel ([Amherst Town Hall](https://www.google.com/maps/search/Amherst+Town+Hall+4+Boltwood+Ave+Amherst+MA)) | One place, summarized | A row of icon buttons (Directions, Save, Nearby, Send to phone, Share), then fact rows with icons. Time-sensitive status in amber ("Closes soon · 4:30 PM · Opens 8AM Tue") with a caveat ("Columbus Day might affect these hours"), and "Suggest an edit". | `google_maps_search_desktop.png`, `google_maps_search_390.png` |

---

## 2. The 12 best patterns, ranked by how much they would help our users

The sketches use real towns, with project names and details made up for illustration (Federal Pond Solar is the example from the brief). Today is Mon Oct 12, 2026.

### The item line (used everywhere)

```
{Board} · {Day Mon D} — {Project or topic}: {what the board will do}
```

- `Planning Board · Tue Oct 13 — Federal Pond Solar: special permit hearing`
- `Select Board · Thu Oct 15 — Data center moratorium: vote on sending it to Town Meeting`
- `ZBA · Mon Oct 19 — 40 Main St apartments (24 units): hearing continues`
- With more than one town in view, put the town first: `Hadley · Planning Board · Tue Oct 20 — Route 9 battery storage: site plan review`

Rules: board short name; weekday plus date with no year; a name a resident would use (not "Application #2026-14"); a verb phrase from a fixed set (hearing, hearing continues, vote, discussion, site visit, decision expected). Keep it to about 90 characters so it fits on two lines at 390 px.

---

### 1. A summary written to a fixed pattern, with the legal text behind a link
**Seen at:** CPSC (fixed headline formula plus Hazard/Remedy/Units fields), Boston ("Four story apartment building with 24 units and 16 parking spaces"), NYC ZAP rows (plain name, summary cut at 150 characters), Zillow ("Show more" after 4 lines). **Counter-example:** PlanningAlerts prints the full council text in every row.

Town page, one item (phone):
```
Planning Board · Tue Oct 13 — Federal Pond Solar: special permit hearing
5 MW ground-mounted solar on 22 acres off Federal St. Residents can speak.
● Hearing → vote next          Added Oct 9

  What      Ground-mounted solar array with battery storage
  Where     Federal St near Pond Rd (2.4 mi from you)
  Who       Planning Board, Town Hall Room 101, 7:00 pm
  Next      Board can vote Oct 13 or continue to a later meeting
  Speak up  Come to the hearing, or email planning@town.gov before Oct 13

  ▸ Show the agenda wording        (raw legal text, collapsed)
  ▸ Original agenda (PDF, p. 3)
```
The 5 fields are always the same and always in the same order (the CPSC lesson). The raw legal text becomes one collapsed line, never the default.

### 2. A stage tracker that says what happens next
**Seen at:** GovTrack ("Passed House (Senate next). ... It goes to the Senate next."), Boston's vertical Project Phase stepper, FlightAware's single progress bar, ZAP's 4-stage legend. **Counter-example:** ZAP's 14-step milestone list.

Four stages, the same everywhere:
```
On agenda ── Hearing ── Vote ── Decided
   ✓           ●
Hearing opens Tue Oct 13 (vote next).
The board hears from the applicant and residents. It can vote the same night or continue the hearing.
```
Off-ramps use the same bar, with a label: `Continued to Oct 27`, `Withdrawn`, `Approved with conditions`, `Denied`. In list rows, show only the short form: `● Hearing → vote next`. Add Councilmatic's "What are these meetings?" as a one-line link under the bar: "What is a special permit hearing?"

### 3. Show a preview before asking for an email, and ask only for the email
**Seen at:** Google Alerts (type a topic, see an "Alert preview", one email field, "Show options" collapsed), USGS ENS (3 ready-made setups in plain words), GovTrack ("Track bills ... to be alerted when ...").

Alert setup, in this order:
```
Get alerts for Amherst
In the last 30 days you would have received 3 alerts:
  Planning Board · Tue Oct 13 — Federal Pond Solar: special permit hearing
  Select Board · Thu Oct 15 — Data center moratorium: vote on sending it to Town Meeting
  Town Council · Mon Sep 28 — Battery storage bylaw: first reading

[ your@email.com          ] [ Send me these ]
  ☑ Also include towns that border Amherst (Hadley, Pelham, Shutesbury, Belchertown +4)
  ▸ More options: topics, weekly or as-they-happen, calendar, RSS, Slack
```
The town is already filled in from the page the visitor came from. Email is the only required field and there is no account. Calendar, RSS and Slack go under "More options", which replaces today's /watch page with 467 checkboxes and a webhook field in the main form.

### 4. Put "Save this as an alert" right above the results
**Seen at:** PlanningAlerts ("Save this search as an email alert [Save]" directly above the list), Zillow ("Save search" is the one filled button), Patch ("Subscribe" in the header of every town page), Toronto (ward subscription in the intro). **Counter-example:** PlanningAlerts now sends Save to "Create an account or sign in".

Town page and search results:
```
Amherst: 4 items coming up                    [ Get these by email ]
```
Search page, after a query for "battery storage":
```
12 upcoming items mention battery storage in 9 towns
[ Email me when a new one is posted ]
```
One tap opens the preview from pattern 3 with the town or query already filled in.

### 5. Location entry with an example, "use my location" and nearby towns by name
**Seen at:** PlanningAlerts ("Find applications within 2 km of:" plus "or use my current location"), FixMyStreet ("e.g. 'B2 4QA' or 'Tib St, Manchester'"), Utah ("Meetings and Events Around Me", already filtered to a ZIP), SeeClickFix ("Nearby Service Providers"), Wikipedia (neighbors spelled out). **Counter-example:** Utah's Government Type > Entity > Public Body cascade.

Home page, first screen:
```
What's coming up before your town's boards?
[ Town or ZIP, e.g. Amherst or 01002         ] [ Show me ]
  ⌖ Use my location
```
On the town page, neighbors are named instead of shown as a radius on a map:
```
Nearby: Hadley (2 items) · Pelham (0) · Belchertown (1) · South Hadley (0)   [ Add neighbors to my alerts ]
```

### 6. Hide routine items by default and say how many are hidden
**Seen at:** Councilmatic's "Non-Routine" tag (on top of a feed full of parking permits). **Counter-example:** Plural, where routine Comptroller filings come first among 19,518 results.

Town page, under the list:
```
Showing 4 items on solar, battery storage, data centers, moratoria, zoning and housing.
23 routine items hidden (minutes, appointments, liquor licenses).  [ Show all ]
```
This one change cuts most of the length the owner is worried about.

### 7. A this-week strip first, then the detail
**Seen at:** weather.gov (Tonight / Tuesday / Tuesday Night strip, then "Detailed Forecast"), Councilmatic ("Next City Council meeting: Wed 10/14/2026 10:00a.m."), FlightAware (status headline first on a phone).

Top of the town page (this replaces the crawl-status table that currently sits above the items):
```
Amherst this week
 Tue Oct 13          Thu Oct 15         Mon Oct 19
 Planning Board      Select Board       ZBA
 2 items             1 item             nothing on our list
```
Each column is a tap target that jumps to that meeting's items. On a phone it is a row you scroll sideways inside, 3 columns visible, with no horizontal scroll on the page itself.

### 8. Say where the item came from, in a sentence
**Seen at:** PlanningAlerts ("We found this application on the planning authority's website on 10 October 2026, 3 days ago."), Zillow ("Zillow last checked: 7 hours ago / Listing updated: October 09, 2026 / Source: MLS PIN"), GovTrack ("Source: Congress.gov"), AirNow ("Forecast courtesy of Massachusetts Dept. of Environmental Protection"), Toronto ("data is refreshed daily"), PlanIt (admits which authorities are out of date).

Item footer:
```
From the Planning Board agenda posted Oct 9 on amherstma.gov. We last checked 2 hours ago.
Original agenda (PDF, page 3) · Report a mistake
```
Town page footer (the crawl table moves here, rewritten as a sentence):
```
We read agendas from 6 Amherst boards, most recently 2 hours ago. Not covered yet: Conservation Commission.
```

### 9. Badges for what changed and what is new since the last visit
**Seen at:** Zillow ("Price cut: $49,900 (9/29)" on the card), PlanningAlerts ("3 days ago"), Patch and FixMyStreet ages ("14h", "20:15 today"), Plural ("LATEST ACTION: OCTOBER 13, 2026").

A small badge with a date, on the card:
```
[New]  Planning Board · Tue Oct 13 — Federal Pond Solar: special permit hearing
[Moved to Oct 27]  ZBA · Mon Oct 19 — 40 Main St apartments (24 units): hearing continues
```
Return visit (remembered on this device only):
```
2 new since you last looked (Oct 5)
```
Badge set: New, Moved to {date}, Continued, Decided, Withdrawn. No more than one badge per item.

### 10. Key-fact chips pulled from the long text
**Seen at:** Zillow "What's special" chips, Redfin ("Queen anne victorian • Screened side porch • Modern kitchen"), Boston's fact strip, Wikipedia's infobox rows, Zillow's "4 bds | 4 ba | 2,787 sqft".

Under the item line, at most 4 chips:
```
5 MW · 22 acres · Federal St · Special permit
```
For housing: `24 units · 4 stories · 16 parking spaces · Chapter 40B`. For a moratorium: `Large solar and battery storage · 12 months · Needs Town Meeting vote`. Chips double as search filters (tap "Special permit" to see all upcoming special permits nearby).

### 11. A calm empty state that still gives an answer and a next date
**Seen at:** AirNow ("Not Available" for now, but "Today Good / Tomorrow Good" and "Enjoy your outdoor activities."), Google Alerts ("There are no recent results ... Below are existing results that match your search query.").

Town page with nothing coming up:
```
Nothing on our list for Pelham in the next 3 weeks.
Next meetings we will read: Planning Board, Wed Oct 21 · Select Board, Mon Oct 26.
Recently decided: Planning Board approved the Amherst Rd solar bylaw on Sep 30.
[ Tell me when something comes up ]
```
Search with no upcoming results: "No upcoming items mention 'data center' in Franklin County. 3 past items: ..."

### 12. One row of actions and a visible deadline on each item
**Seen at:** Google Maps (Directions, Save, Nearby, Send to phone, Share; amber "Closes soon · 4:30 PM"), Boston ("Comment period ends Nov 09, 2026"), PlanningAlerts ("Make a comment now"), Zillow (two-button bar that stays on screen on a phone).

Item detail:
```
Hearing tomorrow · 7:00 pm · Town Hall Room 101          (amber when within 48 hours)
[ Add to calendar ]  [ Follow this item ]  [ Share ]  [ How to speak ]
```
On a phone, "Add to calendar" and "Follow this item" stay pinned at the bottom of the item page. "Follow this item" sends updates only when the stage changes (pattern 2), not a new email every time the agenda is reposted.

---

### Putting it together: the alert email

We could not see any of these sites' real alert emails without making accounts. This sketch is built from what their pages say about their messages: USGS sends "a short text summary plus a link", Google Alerts shows the email's contents as the preview, and PlanningAlerts tells you how many people were notified. Citizen's push format (age, headline, place) gives the Slack and push version.

```
Subject: Amherst + 3 nearby towns: 2 hearings this week (Federal Pond Solar, Route 9 battery storage)

AMHERST
[New] Planning Board · Tue Oct 13 — Federal Pond Solar: special permit hearing
      5 MW ground-mounted solar on 22 acres off Federal St. Residents can speak.
      ● Hearing → vote next · Add to calendar · Details

HADLEY
Planning Board · Tue Oct 20 — Route 9 battery storage: site plan review
      ● On agenda → hearing next · Details

Nothing new this week in Pelham or Belchertown.

You get this because you asked for Amherst and its neighbors, weekly.
Change towns · Switch to as-it-happens · Pause · Unsubscribe (one click, no login)
Sources: agendas posted on each town's website; we checked them Mon Oct 12.
```
Slack/push version: `Amherst · Planning Board · Tue Oct 13 — Federal Pond Solar: special permit hearing` (one line, link to the item).

Subject line rule: towns, then a count by stage, then up to two project names. The "Nothing new in..." line stops quiet towns from looking broken.

---

## 3. Patterns to avoid

| Pattern | Seen at | Why to avoid it |
|---|---|---|
| Full raw description in every list row | PlanningAlerts results (15,408 px tall on a phone; tree-pruning notices run 10 to 15 lines) | This is our current problem. The visitor has to read legal text to learn whether an item matters. |
| A modal or carousel on first load | NYC ZAP ("New CEQR Filter Option"), ZoLa ("new features"), FlightAware (cookie banner plus alerts upsell) | It covers the one thing the visitor came for, and on a phone it covers everything. |
| Filters named with agency jargon | NYC ZAP (RACIAL EQUITY REPORT APPLICABILITY, ULURP TYPE, CEQR), Toronto (Committee of Adjustment, TLAB) | Ordinary people cannot pick a filter they cannot name. Use topics (solar, housing) and towns instead. |
| A map as the first screen | SF PIM (blank map), ZoLa (layer toggles) | Maps are slow on phones and give no answer until the visitor knows what to click. A list with "2.4 mi from you" works better. |
| Making people pick the government before the place | Utah (Government Type > Entity > Public Body), PlanIt (417-name list), our own /watch (467 checkboxes) | People know their town, not which body handles what. Ask for the town once and fill in the rest. |
| Meeting-level titles | Utah ("Agenda", "Agenda", ...), Councilmatic meeting list (board names only) | "Agenda" tells nobody what is being decided. Lead with the item, then show the meeting. |
| Long milestone lists | NYC ZAP (14 steps, from "CEQR Fee Paid" to "Approval Letter Sent to Responsible Agency") | Residents care about when they can speak and when it is decided. Four stages are enough. |
| Several messages for one event | USGS ENS ("one earthquake can generate up to five notifications") | Alert fatigue leads to unsubscribes. Send one message per stage change, and group items into a digest by default. |
| Requiring an account to save an alert | PlanningAlerts ("Create an account or sign in."), USGS (username/password on the landing page) | Each extra step loses people. An email address plus a confirmation link is enough. |
| Routine items mixed in with the ones that matter | Plural (Comptroller filings first), Councilmatic before its Non-Routine filter | The few items people care about get lost. Filter by default and show the count of what was hidden. |
| Ads, sponsors and other towns in a town's feed | Patch (sponsor cards; a Salem story in the Newton feed) | It breaks trust in "this is about my town". |
| Alarm tone | Citizen ("live video from the scene") | Our items are days or weeks away and people can act on them calmly. Urgent styling (amber) should mean only "within 48 hours". |
| Scores without a source | Nextdoor ("Safety: 67, Affordability: 96", though it does link "Where is this data from?") | A made-up score invites distrust. If we show numbers (items per town, towns covered), each one gets a source line. |
| Big logo cards | SeeClickFix (one town logo per screen on a phone) | Decoration pushes the content below the first screen. Town names as text are enough. |

---

## 4. Phone layout notes (390 px)

- **Status first.** FlightAware and AirNow put the answer ("EN ROUTE AND ON TIME", "Today Good") above everything else. Our town page should open with "Amherst this week" (pattern 7) and the first item line, not the crawl table. Today no agenda item shows above the fold on /ma/amherst.
- **One filled button per screen.** Zillow's filter row has one filled button (Save search), and its listing page keeps one two-button bar on screen. Ours: "Get these by email" on list pages, and "Add to calendar" / "Follow this item" on item pages.
- **Truncate, then expand.** Zillow cuts at 4 lines plus "Show more", and ZAP at about 150 characters plus "...". The agenda wording on our items starts collapsed.
- **Single column with the meta line under the title.** PlanningAlerts and Patch both use title, then one grey meta line ("3 days ago, 890 m away"; "Newton | News | 14h"). Ours: `● Hearing → vote next · Added Oct 9 · 2.4 mi`.

## 5. Skipped or unavailable on 2026-10-12

- Bot check: Brighton & Hove Idox weekly list (Imperva hCaptcha).
- Blank page in headless Chromium: USPS tracking.
- Refused by the network proxy: nyc.councilmatic.org, pa.manchester.gov.uk.
- 404: Seattle LUIB (both URLs), carfax.com/sample-report, kayak.com/price-alerts, planit.org.uk/find/, planningalerts.org.au/help.
- 503 (down): FixMyStreet /around and /alert, TheyWorkForYou /alert and /mp.
- Not inspected: real alert emails from any site (they need an account or a confirmed subscription).
