# Comparables: how the good sites set up each page, and what ours gets wrong

Written Nov 2, 2026. This note adds to `research_notes/Design/human_first_spec.md` and `research_notes/Design/how_websites_should_be.md` and repeats neither. Everything quoted below was read on the page linked next to it today, with the WebFetch tool, or seen in a Playwright (Chromium) screenshot at 390 by 844 and 1366 by 900. Screenshots are in `scratchpad/design4/shots/`; the names below are relative to that folder (`<site>_<page>_<width>.png` is the first screen, `_full.png` is the page down to 5,000 or 6,000 px). Numbers such as "first row at 575 px" come from `shoot.cjs`, `measure_ours.cjs` and `measure2.cjs` in the same folder (results in `out*.json`, `ours_measure.json`, `ours_measure.log`); "words before the first control" counts visible text in DOM order up to the first input, button or button-styled link. No bot check was bypassed and no user agent was changed; the default headless Chromium was used as is.

**Could not be read, and were not bypassed.** GovTrack.us (HTTP 403 on the home, bills list, a bill page and the login page, both for the fetch tool and the browser; `govtrack_home_390.png` shows the block page). LegiScan (403 on the home, the Massachusetts list and the GAITS page, both tools). Ballotpedia (403 on the main page, the Sample Ballot Lookup and a state page, both tools; the browser got a page titled "403 ERROR"). BuildZoom (403, both tools). Axios Local Boston (403, both tools). NYC Councilmatic (the proxy returned "ERR_TUNNEL_CONNECTION_FAILED"). Documenters.org returned 403 to the fetch tool but 200 to the browser, so it is covered below from the browser's text and screenshots. Three addresses in the brief led elsewhere: `open.pluralpolicy.com/ma/bills/` is a 404 and the old Open States home says most tools "are now disabled"; `curate.co` is an event-catering product (headline "AI-Assisted Operations Platform for Event Businesses"), so the local-government minutes reader was read at curatesolutions.com; `local.nixle.com` redirects to everbridge.com/products/nixle/. `contrarianboston.substack.com` is a 404; that newsletter lives at scottvanvoorhis.substack.com, reached through contrarianboston.com. Feedly's home page now sells threat intelligence to security teams ("The fastest way to track emerging threats with AI"), so it is a weak comparable and gets a short entry.

Twenty-four sites were read in full: Plural (and its free Open tool), Chicago Councilmatic, Legistar (Boston), Boston.gov (notices, events, a notice page, home), Cambridge's IQM2 portal, Documenters (network home, Chicago, Detroit, the meetings list), Curate, Vote411, Shovels, Zoneomics, Patch (Plymouth, and the subscribe page), Nextdoor (Carver), 6AM City (company home and CHStoday), Google Alerts, Visualping, Feedly, Nixle/Everbridge, a Substack landing page, Cambridge Day (a local newsletter box, added because Patch and Cambridge Day are the closest things to a town newsletter in our area), Wikipedia, Craigslist, Hacker News, GOV.UK (home and a start page) and USA.gov.

---

## Section 1: one teardown per site

Format for each: (1) home at 390 and 1366, (2) the list page, (3) the detail page, (4) sign-up or alerts, (5) what they never do, (6) three to copy and one not to.

### Plural (pluralpolicy.com), with Plural Open and the old Open States

URLs: https://pluralpolicy.com/, https://pluralpolicy.com/open, https://open.pluralpolicy.com/. Shots: `plural_home_390.png`, `plural_home_1366.png`, `plural_open_390.png`, `plural_open_1366.png`, `plural_list_390.png` (Open States), `plural_home_390_full.png`.

1. Home. h1 "AI-Native Legislative and Regulatory Tracking Software"; one line "Track bills and regulations across all 50 states, DC, Puerto Rico, Congress, and 40+ countries."; then a search box whose placeholder is a worked example, "Ohio cannabis licensing", with three example chips under it ("bills preempting local rent control", "data privacy in the Southeast", "PFAS restrictions in New England"); then two buttons, "Book a Demo" (filled) and "Explore Our Coverage" (outlined). Words before the box: 33 at 1366 (at 390 the header's "Book a Demo" comes first, after 3 words). The product itself is not shown; the example chips stand in for it. Below the first screen: "Trusted by over 500 teams across advocacy, academia, and government affairs" with seven logos (Common Cause, NBC Universal, Columbia, X, Affirm, Google, the Rockefeller Foundation), "COVERAGE" with the counts 50, 40+, "DC + PR", Congress, then features, then plans ("$609 per year, per seat", "$5,000 per year", "Custom pricing"), then "See it on your own jurisdictions". Page height 8,399 px at 390. A first-timer gets nothing here without a demo; the free tool is /open: h1 "Find Your Legislators.", "Search Legislation / Look up a bill" with a box labelled "ENTER KEYWORDS OR BILL #" at 634 px (390), and "Find Your Legislators / Enter your address". The old open.pluralpolicy.com says "Open States is now Plural / SAI360!" and "Most other tools here are now disabled".
2. List. The Massachusetts bills list at the address in the brief is a 404; no list was reachable without an account.
3. Detail. Not reachable without an account.
4. Sign-up. "Book a Demo" and "Log In" in the header; no public form. The free tool asks for one thing per box (keywords, or an address).
5. Never: no filter or count in the hero; no explanation of method; the search box carries its own example instead of a label like "Search".
6. Copy: the example-in-the-box pattern ("Ohio cannabis licensing" plus three chips) is the cheapest way to show what a product does; one filled button and one outlined, never two filled; "Enter your address" as the whole instruction. Do not copy: a home page that ends in prices and a demo form for a product residents are meant to use.

### Chicago Councilmatic (chicago.councilmatic.org)

URLs: https://chicago.councilmatic.org/, https://chicago.councilmatic.org/events/, https://chicago.councilmatic.org/event/city-council-8ca40f706813/, https://chicago.councilmatic.org/search/?q=zoning. Shots: `councilmatic_home_390.png`, `councilmatic_home_1366.png`, `councilmatic_list_390.png`, `councilmatic_list_1366.png`, `councilmatic_detail_390.png`, `councilmatic_search_390.png`, `councilmatic_home_390_full.png`.

1. Home. A photo of City Hall behind h1 "Chicago City Council, demystified", the label "Search Chicago legislation" and one box with the placeholder "police, zoning, O2015-7825, etc." at 285 px on a phone (21 words before it). Under the photo: "Chicago City Council consists of 50 elected alders and meets monthly to shape the city." Then "Find Your Ward" and "Compare Alders" cards, "Engage City Council", then "Upcoming Meetings" with a "Next City Council meeting" block ("Mon 11/02/2026", "10:00a.m.", "Council Chambers, City Hall 121 N LaSalle St, Chicago, IL", a "Details" button), then "Latest Council Meeting" ("took action on 23 items, including 20 non-routine"), "Legislative topics" with counts, "Since the last council meeting" ("81 new items were introduced"). Real data is on the home page, below the fold. Page 5,640 px at 390. No account anywhere; the next meeting is one scroll away.
2. List (/events/). Above the heading: a month picker ("Select a month and year"), "< Previous month" and "Next month >" buttons; then h2 "Upcoming meetings" at about 262 px and an "RSS" link; then rows, each three things on two lines: "Mon 11/02/2026", "10:00 a.m.", "City Council" (the name is the link). Six rows fit the first phone screen. No place, no agenda, no subject in the row; everything else is a tap away. A "What are these meetings?" explainer sits lower on the page.
3. Detail. h1 "City Council" (the body, not the matter), then "Chicago City Council", "Mon 11/02/2026", "10:00 a.m.", the address; three links: "Notice" (PDF), "Agenda" (PDF), "View on the Chicago City Clerk website"; then "Agenda: 2 items" as a table (#, Action, Description, ID, Sponsor(s)); "Alder Attendance"; "Attachments". No add-to-calendar, no public-comment line.
4. Sign-up. None; RSS only.
5. Never: no counts in the hero; no "we can't"; no nested disclosure; the placeholder is three examples, not an instruction.
6. Copy: the "Next City Council meeting" block (date, time, place, one button) as the first thing a town page says; a month at a time with Previous/Next; the search placeholder made of examples. Do not copy: a detail page headed with the body's name, with the subject buried in a table.

### Legistar, City of Boston (boston.legistar.com)

URL: https://boston.legistar.com/Calendar.aspx (the home address redirects to the same calendar). Shots: `legistar_list_390.png`, `legistar_list_1366.png`.

1 and 2. One page serves as home and list. h1 "Meeting Calendar". Above the table: a banner ("Welcome to our new legislative management system! While we work to transfer over our content, you can find meetings prior to August 18, 2021 here."), tabs (Home, Search Agenda Items, Calendar, City Council, Other Meeting Bodies, Members), "List View / Calendar View", a "Search:" box, two dropdowns ("This Month", "All Other Meeting Bodies"), "notes" and "closed captions" checkboxes, "Search Calendar", "8 records", "Group", "Export", and icons for RSS and "Alerts". Nine columns: Name, Meeting Date, Meeting Time, Meeting Location, Meeting Details, Agenda, Agenda Packet, Minutes, Video. A row: "Boston School Committee | 11/18/2026 | 5:30 PM | Bolling Building | Meeting details | Agenda | Not available | Not available". Each row has an iCal icon. At 390 the whole desktop page is shrunk to fit (the first-screen word count is 204 at both widths, so nothing reflows) and the text is unreadable; nine inputs sit in the first screen. 43 words before the first control.
3. Detail. Not opened (the "Meeting details" links need a session id); the row already carries the agenda PDF.
4. Sign-up. An "Alerts" icon and "Sign In"; no wording about what you get.
5. Never: never hides the source document; every row links the agenda directly.
6. Copy: the agenda PDF and the calendar file in the row itself; a sortable table on desktop; "This Month" as the default range. Do not copy: "Not available" printed in 24 cells; nine controls above eight rows; a page that does not reflow on a phone.

### Boston.gov: public notices, events, a notice page, home

URLs: https://www.boston.gov/public-notices, https://www.boston.gov/events, https://www.boston.gov/public-notices/16634391, https://www.boston.gov/. Shots: `bostongov_notices_390.png`, `bostongov_notices_1366.png`, `bostongov_events_390_full.png`, `bostongov_detail_390.png`, `bostongov_home_390.png`.

1. Home (390). Banner "An official website of the City of Boston. Here's how you know", red MENU, a photo with "Welcome to the CITY OF BOSTON", then, at about 350 px, the heading "MONDAY, NOVEMBER 2" (today's date) and a list of today's facts with icons: "CITY HALL OPERATING HOURS", "TRASH AND RECYCLING / Pickup is on a normal schedule.", "STREET CLEANING / Street cleaning is on a normal schedule.", "PARKING METERS". The first screen says what is true today.
2. List (public notices). h1 "PUBLIC NOTICES" at 235 px; "You can find out about all upcoming City of Boston public notices and hearings below. We also have information on archived public notices."; then one blue "FILTER" button at 565 px (on desktop the filter is a row of "SEARCH PUBLIC NOTICES", "FILTER BY DEPARTMENT", "APPLY" above the list); the first row at about 665 px: an italic serif title link ("Notice of Advance Processing and Removal of Early Voted Ballots for November 3, 2026, State Election"), then "When NOVEMBER 02, 2026 8:30AM - 5:30PM", "Where", "Posted", a department icon, and, when there is one, a sentence ("The public can offer testimony."). About one row per phone screen. Pages "1" to "8". No subscribe. Events (/events) is tighter: day headings ("NOVEMBER 2, 2026"), then per row a time range and a capitalised title with a chevron ("9:00am-5:00pm / CANCELED: DIGITAL LITERACY WORKSHOP"); about eight rows a screen; "first ›", pages 1 to 9; an RSS feed; "OTHER CALENDARS" at the end.
3. Detail (a notice). h1 in capitals, 12 words ("CITY COUNCIL COMMITTEE ON GOVERNMENT OPERATIONS WORKING SESSION ON DOCKET #1711"), then one italic sentence ("A working session to amend a proposed ordinance that would extend protections for tenants facing displacement by condominium or cooperative conversion."), then "PAGE SECTIONS", then "DISCUSSION TOPICS" with "Docket #1711" and its text; the fetch tool read "When November 2, 2026, 10:00AM", "Where Virtually via Zoom", "Posted 10/22/2026 - 2:51PM", a contact and the sentence that there will be no public comment period. Links: "Docket #1711" (PDF), "Official Filed Posting" (PDF), an email, a phone number. No add-to-calendar, print or share.
4. Sign-up. None on these pages; "NEWSLETTERS" is a menu item.
5. Never: never a count or a crawler note; the filter is one button on a phone and one row on desktop; a canceled event is said in the title ("Canceled: Digital Literacy Workshop"); "The public can offer testimony." appears only when it is true.
6. Copy: today's date as the first heading on the home page with today's facts under it; the one-button FILTER on phones; "The public can offer testimony." as a row sentence only when true; the one-sentence summary under a notice title. Do not copy: one notice per phone screen with "When / Where / Posted" labels stacked under an italic title.

### Cambridge, MA Open Meeting Portal (IQM2 / Granicus)

URLs: https://cambridgema.iqm2.com/Citizens/Calendar.aspx, https://cambridgema.iqm2.com/Citizens/Detail_Meeting.aspx?ID=4822. Shots: `cambridge_list_390.png`, `cambridge_list_1366.png`, `cambridge_detail_390.png`.

1 and 2. The calendar is the entry page. A red seal and a painting banner, tabs (Welcome, Meetings, Browse, Notices, Boards+), a pink left column holding only "Print This Page", then "Meeting Calendar", "Displaying 28 meetings from 1/1/2026 to 12/31/2026 for All Meeting Groups", a year list (2026 back to 2014, "See More..."), a "Group" dropdown, "View: List | Calendar", an RSS icon. Rows under month headings ("January, 2026"): "Jan 5, 2026 10:00 AM / City Council - Inaugural Meeting" with up to five document links (Agenda Summary, Agenda Packet, Final Actions, Minutes, Video), blanks where nothing is posted. About nine rows a screen on desktop. At 390 the page does not reflow: the right side is cut off ("Displaying 28 meetings from 1" is the visible text) and 458 words are crammed into the first screen. 14 words before the first control. No account.
3. Detail. "City Council Inaugural Meeting", then Date, Time, Location, Body (per the fetch tool); at 390 the first screen shows "Downloads: Agenda Summary, Agenda Packet, Final Actions, Minutes" and the outline "I. Call to Order / 1. Roll Call", plus "Loading - Please Wait..." and a "Shortcut Keys" box. No calendar link, no public-comment line.
4. Sign-up. "Log in / Register" and an RSS "Calendar" feed; nothing says what either gives.
5. Never: never a sentence about anything; the row is a filename list.
6. Copy: the month heading with the date and time first in every row; blanks rather than "Not available"; the result sentence "Displaying 28 meetings from ... to ..." as the only count. Do not copy: a fixed-width page that cuts off on a phone and a sidebar that holds one button.

### Documenters (documenters.org, City Bureau)

URLs: https://www.documenters.org/, https://chicago.documenters.org/, https://detroit.documenters.org/, https://chicago.documenters.org/meetings/. Shots: `documenters_home_390.png`, `documenters_home_1366.png`, `documenters_chicago_390_full.png`, `documenters_meetings_390.png`, `documenters_meetings_1366.png`, `documenters_detroit_390.png`. (The fetch tool got 403; all of this is from the browser.)

1. Home. A yellow strip "The Documenters Network is powered by City Bureau"; header "Documenters", "Sign In" (yellow), "Become a Documenter" (black), "Our Network 31", nav "Reporting, Meetings, Workshops, About", a search box on desktop ("Search Documenters.org"). h1 "City Bureau's Documenters Network: People-powered news and information"; the line "We're putting every public meeting on the record in Atlantic County" with the place highlighted (it changes per visit; Chicago's page says "Chicago"); a drawn crowd; then two boxes, "Who we are / A network of newsrooms and community organizations committed to participatory civic media." and "What we do / We train and pay hundreds of people to attend under-reported public meetings and publish the results."; then "The Future is Informed" and a feed of real notes, each a card: city ("Detroit"), topic ("HOUSING"), date ("Oct. 29, 2026"), two or three sentences ("Commissioners reintroduced themselves and reviewed their work. Rep. Rashida Tlaib said she just learned about the TRC ..."), the body ("Detroit Tenants Rights Commission"), "Live reporting by Perry Sylvester". The product (the notes) is on the home page but starts about two screens down on a phone. First-screen words 82; 16 words before the first control. Page 8,103 px at 390. No account to read anything.
2. List (/meetings/). h1 "Meetings"; tabs "Upcoming | Past"; on a phone one "Filters" button, on desktop a left panel ("Search meetings", "Date: All time", "Time: All time", "Location / County, city, zip code", "Accessibility / In-person / Remote", "Topic" chips from AGRICULTURE to UTILITIES); "387 results". Each meeting is a card: a topic label ("ELECTIONS"), the title as the link ("Board of Elections"), a Documenters icon, "Monday, Nov 2, 2026 9:30 a.m. - 11:30 a.m. CST", the body ("Illinois State Board of Elections"), and an add-to-calendar icon at the card's top right. A canceled meeting starts "Canceled". About two and a half cards fit a phone screen.
3. Detail. Not opened.
4. Sign-up. "Become a Documenter" and "Sign In" are for note-takers, not readers; readers get the feed and the list with no account.
5. Never: never a count in the hero (the "31" is a network badge in the nav); never a method note on the page; one level of filters.
6. Copy: the notes feed, where each card is place, topic, date, two sentences, body, author (the exact shape of a good row); the single "Filters" button on phones becoming a left panel on desktop; the calendar icon on every card. Do not copy: a hero that takes two phone screens (headline, place, illustration, two boxes) before the first real card.

### Curate (curatesolutions.com)

URL: https://www.curatesolutions.com/ (curate.co is a different company). Shots: `curate_solutions_390.png`, `curate_solutions_1366.png`, `curate_solutions_390_full.png`.

1. Home. A photo of a town hall behind h1 "Know What's Happening in Local Government", the line "Stay ahead of policy change within cities, counties, and school districts with AI-powered local legislative tracking software." and one outlined button "SEE A DEMO"; a cookie panel covers the lower half of the phone screen (60 words before its first button). Below: a laptop screenshot ("54 Locations", "6 Topics"), "Easy, Efficient & Comprehensive Local Policy Tracking", stat cards ("400,000+ Minutes & Agendas Scanned Each Week", "168,000+ Up-to-date Local Government Contacts", "12,000+ Cities & Counties Tracked Each Week"), a video, "Trusted by Hundreds of Organizations" with five logos, audience cards, a newsletter "SUBSCRIBE". No prices, no sample alert, no sample hit. "Curate is owned and operated by FiscalNote, Inc." Page 10,408 px at 390. Nothing for a first-timer without a demo.
2, 3. No list or detail is public.
4. Sign-up. "Request Demo" and "LOGIN".
5. Never: never shows one real sentence from a minutes document, which is the whole product.
6. Copy: the plain headline that names the reader's goal ("Know What's Happening in Local Government"); counts kept below the fold, each with a noun; one button in the hero. Do not copy: the empty hero over a stock photo with a cookie panel on top.

### Vote411 (League of Women Voters)

URLs: https://www.vote411.org/, https://www.vote411.org/ballot. Shots: `vote411_home_390.png`, `vote411_home_1366.png`, `vote411_ballot_390.png`, `vote411_ballot_1366.png`.

1. Home. h1 "ELECTION INFORMATION YOU NEED", "Brought to you by the League of Women Voters Education Fund"; three tiles ("See What's On Your Ballot", "Register to Vote", "Check Your Registration") on a photo; a yellow "VOTING FAQ" strip; then "PERSONALIZED VOTING INFORMATION" with the form "Enter Your Address to Get Started:" (Street Address, City, Select a state, Zip Code). Then state picker, hotlines, 28 sponsor logos, "Make a donation". 14 words before the first control. No account; one address gives the ballot.
2. List. None in the usual sense; the ballot page is the result.
3. Detail (/ballot). "YOUR VOTERS' GUIDE / Personalized Ballot and Candidate Information", "Enter your address to find your races", "We currently have information on 56593 candidates and 28991 races.", one field "Street Address*", "Or, use your location to find races for that area", "*Your address will never be saved, sold, or used for marketing purposes.", "Get Started", and "If you'd rather not enter an address, you can view all races or all candidates".
4. Sign-up. None; the address is the only input and the privacy line sits next to it.
5. Never: never asks for an email to show a ballot; never hides the "view all" path for people who will not type an address.
6. Copy: "Enter your address to find your races" as a complete instruction; the privacy line beside the field; the "If you'd rather not" escape. Do not copy: a home page whose first action is three picture tiles that each lead to another page, with the real form a screen lower.

### Shovels (shovels.ai)

URL: https://www.shovels.ai/. Shots: `shovels_home_390.png`, `shovels_home_1366.png`, `shovels_home_390_full.png`.

1. Home. h1 "The prediction engine for the built world", "Every permit, parcel, contractor, and land-use decision in American local government. Then we draw it forward.", one button "Search for free" (it goes to sign-up), an illustration; 31 first-screen words, 1 word before the first control (the menu). Then "TRUSTED BY TEAMS AT" (Redfin, Houzz, Angi, Thumbtack, JLL and others), counts ("196M+ building permits", "3.89M+ licensed contractors", "2,820+ jurisdictions", "7M+ new permits added monthly"), "Four datasets, ordered by how early they tell you", delivery options, coverage map, blog, a footer "Email address / Subscribe". No sample permit anywhere. Page 8,551 px at 390.
2, 3. Behind sign-up.
4. Sign-up. "Search for free" twice, "Get Started", "Sign In"; no fields on the page.
5. Never: never a count in the hero (they come after the logos); never more than one button in the hero.
6. Copy: the two-sentence hero where the second sentence says what the data does for you; one button; counts with nouns below the fold. Do not copy: "Search for free" that opens a sign-up form; a search product with no search box on its home page.

### Zoneomics (zoneomics.com)

URL: https://www.zoneomics.com/. Shots: `zoneomics_home_390.png`, `zoneomics_home_1366.png`.

1. Home. At 390 the first screen is a blue announcement ("Introducing Bassett.ai, our new AI Operating System for Zoning Intelligence", two buttons) and then a picture of the product (a zoning card over a photo: "Maximum Lot Area SqFt. 500", "601 Elm St, Dallas, TX"); the h1 "AI-driven Zoning Analysis & Site Search" arrives at about 800 px, below the first screen. Then "Preferred by real estate industry leaders ...", logos (Redfin, Moody's, Cushman & Wakefield), a "Zoning Coverage by City Size" map that read "Loading map...", four product sections each with a button ("Find Zoning Information", "Sign up", "Explore our Zoning APIs", "Explore our Zoning Reports"), testimonials, counts ("27000+ cities digitized", "136.9 Million lots/parcels searchable"). Page 14,218 px at 390, the longest in the set. 0 words before the first control.
2, 3. Not public.
4. Sign-up. "Sign up" buttons; no fields on the page.
5. Never: nothing worth recording.
6. Copy: a picture of one real result (an address with its zoning facts) near the top, which is the one thing a first-timer can understand. Do not copy: an announcement bar that pushes the headline off the first screen.

### Patch (patch.com, Plymouth MA, and the subscribe page)

URLs: https://patch.com/massachusetts/plymouth, https://patch.com/subscribe. Shots: `patch_town_390.png`, `patch_town_1366.png`, `patch_town_390_full.png`, `patch_subscribe_390.png`, `patch_subscribe_1366.png`.

1. Town page. Header: menu, Patch, search, "Sign up"; "Plymouth, MA" with a filled "Subscribe" button; tabs "News Feed, Events, Local Businesses, Advertise"; "Thank you to our Local Business Sponsor: RowCal - Boston"; "Plymouth Local News" with "26,376 visits in the last 30 days"; the first story card at about 280 px ("Across Massachusetts, MA | News | 2d", headline, "Jessie Castellano, Patch Staff", a photo); then a "Patch Local Partner" card; a sticky bottom bar "Post your event (It's easy!)". On desktop a large "Advertise on Patch" banner sits above the header and the header holds a "Your town or ZIP code" box. 4 words before the first control. The product (stories) is on the first screen; no account.
2. List. The feed is the list: place, section, age, headline, byline, summary, photo; one story per phone screen; the fetch tool counted ten stories before a "Read more" link, with a sponsored story in position 3.
3. Detail. Not opened.
4. Sign-up (/subscribe). One phone screen: "Trusted local news for your community", "The stories, events, and updates your community is talking about.", "Delivered in a quick daily email. Always free.", a phone mockup of the newsletter ("Here's what's happening near you this week"), two fields ("Your town or ZIP code", "Email address"), one green button "Subscribe Free", then "Free. Unsubscribe anytime." and "By subscribing, you agree to Patch's Privacy Policy and Terms of Use." 24 words before the first field.
5. Never: never asks for a password to subscribe; never puts the sign-up form in the feed (the button is in the header).
6. Copy: the subscribe page whole: what, how often, "Always free", a picture of the thing, town then email, one button, "Unsubscribe anytime"; the age ("2d") and place in every row. Do not copy: a visit counter under the page title, a sponsor line above the first story, a sticky promo bar.

### Nextdoor (nextdoor.com, public Carver page)

URL: https://nextdoor.com/city/carver--ma/. Shots: `nextdoor_city_390.png`, `nextdoor_city_1366.png`, `nextdoor_city_390_full.png`.

1. City page. "Log in", "Sign up"; breadcrumb "United States › Massachusetts › Carver"; a photo with "2025 Winner"; h1 "Carver / Massachusetts, United States"; "#14 best city to live in Massachusetts"; a grid of eight numbers ("Residents: 11,641", "Safety: 100", "Affordability: 85" ...); a paragraph; "Where is this data from?"; an orange "Trick or treat in Carver, MA" box with "See Carver's 2026 Halloween map"; then "Conversations happening in Carver" with six real posts ("We're all set for a fun night of trick-or-treating! #TreatMap"), groups with member counts, "Latest safety updates near Carver", for-sale items, FAQs. 142 first-screen words, 0 before the first control, 19,632 px tall at 390. Real content without an account, but the first screen is a ranking and eight scores.
2 to 4. Posts need an account to open; the sign-up links lead to an address page (per the fetch tool).
5. Never: never hides the town's name or the breadcrumb.
6. Copy: the breadcrumb and the plain h1 "Carver"; real posts visible before any account. Do not copy: a first screen made of scores and a "#14 best city" badge instead of what is happening.

### 6AM City (6amcity.com) and CHStoday

URLs: https://6amcity.com/, https://6amcity.com/sc/charleston/ (chstoday.6amcity.com redirects there). Shots: `sixam_home_390.png`, `sixam_city_390.png`, `sixam_city_1366.png`, `sixam_city_390_full.png`.

1. The company home is for advertisers ("Community, Delivered", "Let's build something"); its "Local Everywhere" counts read "0 States, 0 Cities, 0 Subscribers" on the day read. The city page is the one that matters: a top strip "LATEST ISSUE / Conference takeaways + the biz of building less / Read now →"; header "CHStoday" with a filled "Subscribe"; eyebrow "CHARLESTON'S DAILY NEWSLETTER"; h1 "Your morning starts here."; one sentence ending "curated every morning and delivered to your inbox."; an email box ("Enter your email address") and "Subscribe free →"; under it "View latest issue · See archive · 100% Free · No spam"; then the editor's photo and a quote, a "LATEST ISSUE" card, "Today in Charleston" weather ("65° Mostly Sunny"), "Recent Articles". 10 words before the first control. A first-timer reads the latest issue in one tap.
2. List. "Recent Articles" with a section label and a headline each.
3. Detail. Not opened.
4. Sign-up. Email only, on the first screen, with the frequency ("every morning"), the price ("100% Free · No spam") and the sample ("View latest issue") beside the button.
5. Never: never asks for a town (the site is the town); never a count of subscribers.
6. Copy: "View latest issue" next to the subscribe button; "100% Free · No spam" as a chip; the editor's face and one sentence as the only social proof. Do not copy: a "LATEST ISSUE" strip plus a construction notice plus a header, three bars before the headline.

### Google Alerts

URL: https://www.google.com/alerts. Shots: `googlealerts_home_390.png`, `googlealerts_home_1366.png`.

1. Home. "Alerts", "Monitor the web for interesting new content", one box with the placeholder "Create an alert about...", "Sign in" top right, and nothing else on the first screen (17 words at 390, 0 before the box). The fetch tool read the options that open under the box: "How often: As-it-happens / At most once a day / At most once a week", "Sources", "Language", "Region", "How many: Only the best results / All results", "Create Alert".
2, 3. None.
4. Sign-up. The topic comes first; the account comes after (the page offers "Sign in"; creating an alert was not tried).
5. Never: never explains how it works on the page; never shows a count; never a second button.
6. Copy: the empty page with one box; frequency as three plain choices with "At most once a day" in the middle; the verb-first button "Create Alert". Do not copy: a page that needs a Google account to finish (we do not need one; say so).

### Visualping

URL: https://visualping.io/. Shots: `visualping_home_390.png`, `visualping_home_1366.png`, `visualping_home_390_full.png`.

1. Home. h1 "We monitor [website changes / price changes] so you don't have to!" (the middle words rotate; the fetch tool read "website changes", the browser "price changes"), and under it the product itself: a form "Enter a page: time.com" with a "Go" button, a snapshot area ("Click Go to take a snapshot"), "Alert me when:", "Check: Every day", "Send to you@company.com". Header: "Book a demo", "Login", "Get started it's free". 20 words before the box at 1366. Below: "Trusted by Thousands", "85% of Fortune 500", "2 million users", mockups of email, SMS, Slack alerts, "PREVIOUS / CURRENT" screenshots, G2 badges. Page 13,127 px at 390.
2, 3. None.
4. Sign-up. URL first, then the condition, then the frequency, then the email, in one panel on the first screen.
5. Never: never asks for the email first.
6. Copy: the live form in the hero, with the thing to watch first and the email last; "Check: Every day" as a visible default. Do not copy: the rotating headline word and a 13,000 px sales page under it.

### Feedly

URL: https://feedly.com/. Shots: `feedly_home_390.png`, `feedly_home_1366.png`.

1. Home. A promo bar ("Credential Leak Dark Web Agent"), header with "Go to News Reader", h1 "The fastest way to track emerging threats with AI", "Feedly is the AI platform CTI teams use to track threats, contextualize what matters, and deliver tailored intel in minutes", two buttons ("Get started for free", "Book a Demo"), then tabs "Collect / Analyze / Deliver" over a product screenshot, a cookie bar "Feedly uses cookies to deliver its service and analyze traffic / Got it". "Trusted by 380 CTI teams, including half of the Fortune 10". Nothing for a resident.
2 to 4. Account first.
5 and 6. Copy only the tabbed product screenshot as a way to show three views in one place. Do not copy anything else; it is a sales page for security teams.

### Nixle (Everbridge)

URL: https://www.everbridge.com/products/nixle/ (local.nixle.com and www.nixle.com redirect here). Shots: `nixle_everbridge_390.png`, `nixle_everbridge_1366.png`, `nixle_everbridge_390_full.png`.

1. Home. Two promo banners ("Be ready. Get the ASIS 2026 Active Assailant Preparedness Report / Access report"), then a cookie modal covering the phone screen ("Cookie Settings", "Reject All Cookies", "Accept All Cookies"), then h1 "Everbridge Nixle", "Looking to receive alerts from your local agencies and businesses?", two buttons ("Resident sign-up and login", "Nixle for agencies and business"), a phone image. Then "Stay safe and informed before, during, and after a critical event in your community", the sign-up block "Want to opt-in to receive alerts? / Text your ZIP code / to 888777", the opt-out block "Text STOP ALL to 888777 or 333111", carrier notes, "Schedule demo". 18 words before the first control (the banner's button).
2, 3. None.
4. Sign-up. One thing, a ZIP code, sent by text; no web form; the alerts are named ("severe weather, criminal activities, severe traffic, missing persons, or local events").
5. Never: never asks for an email or a password from a resident.
6. Copy: one fact to give (a place), the list of what you will be told, and the opt-out written next to the opt-in. Do not copy: a resident page wrapped in a vendor's banners and cookie modal.

### Substack landing page (Contrarian Boston)

URL: https://scottvanvoorhis.substack.com/ (reached from contrarianboston.com). Shots: `substack_landing_390.png`, `substack_landing_1366.png`.

1. Home. A full-screen gate and nothing else: a logo (a broken image box on the day read), "Contrarian Boston", "Fact-based news, commentary and original reporting with a contrarian edge about local, regional and national events.", "By Scott Van Voorhis · Over 15,000 subscribers", an email box ("Type your email...") with "Subscribe", the terms line, "No thanks ›", and on phones "Subscribe in the app". 53 words; 26 before the box at 390. The posts are behind "No thanks".
2. List. Behind the gate (not read).
3. Detail. Not opened.
4. Sign-up. Email only; the promise is the one-line description and the subscriber count; no frequency.
5. Never: never explains the mechanism; never more than one field.
6. Copy: the one-line description under the name as the entire pitch; "No thanks" as an honest way past the form. Do not copy: a gate before the content; a subscriber count as the proof.

### Cambridge Day (local newsletter box)

URL: https://www.cambridgeday.com/. Shots: `cambridgeday_home_390.png`, `cambridgeday_home_1366.png`.

1. Home. A real-estate ad banner, "CAMBRIDGE DAY" with "Menu", then the lead story with a photo, headline ("Cambridge Common, Café Barada will close"), a one-sentence dek, "by Tom Meek / Sunday, November 1, 2026". 5 words before the first control. Stories are the first screen.
4. Sign-up. After the three lead stories: "Sign up for The Cambridge Day newsletter to get updates in your inbox." and a "Sign up" button; in the footer "Sign up to our free newsletter to get the latest news delivered straight to your inbox." and "Join our community for free. Sign up now." The dialog asks for an email, with "Continue with Google" as an alternative. No frequency is stated anywhere.
5. Never: never a count.
6. Copy: the story first, the ask after three stories. Do not copy: two different sign-up sentences and no frequency.

### Wikipedia (article page)

URL: https://en.wikipedia.org/wiki/Carver,_Massachusetts. Shots: `wikipedia_article_390.png`, `wikipedia_article_1366.png`.

1. Page. Header: menu, logo, "Search Wikipedia" box with a "Search" button, "Donate / Create account / Log in" small at the right. h1 "Carver, Massachusetts", "From Wikipedia, the free encyclopedia", the first sentence "Carver is a town in Plymouth County, Massachusetts, United States.", the infobox (Town Hall photo, flag, seal, map, "Country United States / State Massachusetts / County Plymouth / Settled 1660 / Incorporated 1790"), a left "Contents" list (History and overview, Geography, Demographics, Government, Education, Transportation, References, External links), and on the right an "Appearance" panel ("Text: Small / Standard / Large", "Width: Standard / Wide", "Color: Automatic / Light / Dark"). 765 words in the first phone screen (the densest page in the set), 5 before the search box. Footer: "This page was last edited on 28 September 2026, at 02:02 (UTC)."
2, 3. Not applicable.
4. Sign-up. "Create account" is a small header link; nothing asks.
5. Never: never puts the last-edited time anywhere but the footer; never a count in the heading; never a button in the content.
6. Copy: the first sentence that says the whole thing; the facts box with a key and a value per row; last-edited in the footer only; the reader's choice of text size and colour. Do not copy: 765 words on the first phone screen.

### Craigslist (Boston home and a search)

URLs: https://www.craigslist.org/area/boston, https://www.craigslist.org/search/area/boston?cat=sss&query=desk. Shots: `craigslist_home_390.png`, `craigslist_home_1366.png`, `craigslist_search_390.png`, `craigslist_search_1366.png`.

1. Home. "craigslist", "post an ad", a "search craigslist" box, an event calendar, and the category index (community, services, discussion forums, housing, for sale, jobs, gigs, resumes) with about 200 links on one desktop screen (204 links counted in the first screen at 1366); "nearby cl" down the right. 4 words before the search box. Nothing explains what craigslist is. At 390 the index is one column with the "boston" and "for sale" dropdowns on top.
2. List (search "desk"). The query echoed in the box; chips "+ price condition sold by"; view icons (list, gallery, map); "relevance" sort; "1 - 2 of 983" at the top right; a bell icon (save search); rows as cards: price badge ("$350"), photo, title link ("Desk with hutch"), "<1hr ago • Acton". On desktop a left panel: categories with counts ("furniture 526"), "search titles only", "has image", "posted today", "miles from location", a price histogram ("avg: $107"), "reset / apply". The fetch tool read the plain list form: numbered rows "Desk with hutch | $350 | Acton", 339 to a page.
3. Detail. Not opened.
4. Sign-up. None to read; "acct" and a bell for a saved search.
5. Never: never explains itself; never a hero; never a count of users; the count shown is the result count.
6. Copy: the deciding fact (price) printed on every row; the age and place as one grey line; the result count at the top right in the form "1 - 2 of 983". Do not copy: 200 links as a home page for a site with one job.

### Hacker News

URLs: https://news.ycombinator.com/, https://news.ycombinator.com/item?id=1. Shots: `hn_home_390.png`, `hn_home_1366.png`, `hn_item_390.png`.

1. Home. One orange bar: "Hacker News new | past | comments | ask | show | jobs | submit", "login". Then 30 rows, two lines each: "2. ▲ Postgres 19 is late because so many more bugs are being found now (rhaas.blogspot.com)" and "606 points by soheilpro 15 hours ago | hide | 369 comments". 15 rows fit the first phone screen, 25 at 1366. No explanation of what the site is anywhere on the page. The search box is in the footer (805 words before it). "More" leads to page 2.
2. List. The home page is the list; the title opens the source and the comment count opens the discussion.
3. Detail. "Y Combinator (ycombinator.com)", "57 points by pg on Oct 9, 2006 | hide | past | favorite | 3 comments", then the threaded comments, each with a vote arrow, a name, an age and a "[–]" fold.
4. Sign-up. "login" only.
5. Never: never a hero, a count of users, a picture, a filter, a fold, or a sentence about method.
6. Copy: two lines a row, 15 rows a screen; the title as the link to the source; the number that decides order printed on every row. Do not copy: the footer search and the absence of any line saying what the page is (we need one sentence; they can skip it).

### GOV.UK (home and a start page)

URLs: https://www.gov.uk/, https://www.gov.uk/check-mot-history. Shots: `govuk_home_390.png`, `govuk_home_1366.png`, `govuk_start_390.png`, `govuk_start_1366.png`, `govuk_home_390_full.png`.

1. Home. A cookie banner first ("Cookies on GOV.UK", three paragraphs, "Accept additional cookies", "Reject additional cookies", "View cookies"; it fills about 450 px at 390 and the first control is its button, 48 words in). Then the blue header (crown, "GOV.UK", "Menu", a search icon), h1 "The best place to find government services and information", a label "Search" with a box and a button. Below: "Popular on GOV.UK" (six links: "HMRC account: sign in or set up", "eVisas: access and use your online immigration status" ...), "Services and information" (16 categories from "Benefits" to "Working, jobs and pensions"), "Featured", "Government activity", "Is this page useful? Maybe / Yes / No".
2. List. The categories and the "Popular" list are plain links, no description, no icon.
3. Start page. Breadcrumb "Home › Vehicle tax, MOT and insurance"; h1 "Check the MOT history of a vehicle"; "Check the past results of a vehicle's MOT tests, including:" and three bullets ("if it passed or failed", "the mileage recorded when it was tested", "when the next MOT is due"); short sections for what you can and cannot get; "You'll need the vehicle's number plate (registration number)."; one green "Start now" button; the fetch tool counted about 228 words before it (about 192 without headings); then "Related content" and "Is this page useful?".
4. Sign-up. None.
5. Never: never a count, a photo, a testimonial or a logo; never a button before the text explains what happens when you press it; never "click here".
6. Copy: the start page's order (what you get as three bullets, what you need, one button); the label above the box instead of a placeholder; "Is this page useful?" at the end of every page. Do not copy: a cookie banner that is the first screen (we set no cookies and need none).

### USA.gov

URL: https://www.usa.gov/. Shots: `usagov_home_390.png`, `usagov_home_1366.png`, `usagov_home_390_full.png`.

1. Home. "An official website of the United States government / Here's how you know"; a notice "Visit vote.gov to learn how to register to vote or to update your registration."; the logo, "Español", a search box (at 390 behind "MENU"), "Call us at 1-844-USAGOV1"; a flag photo with h1 "Making government services easier to find" and "USA.gov helps you locate and understand government benefits, programs, and information."; then "How do I ..." with four tasks ("Check my voter registration", "Get or renew a passport", "Get housing help", "Find unclaimed money"), "Jump to all topics and services", "Government benefits and financial assistance / Find benefits", "All topics and services" (21 cards). About 64 words before the search box (fetch tool count); 12 to 16 before the first control in the browser. No counts, no sign-up.
5. Never: never a number, never an ask.
6. Copy: "How do I ..." followed by four real tasks as links; the one-line explanation under the h1 in the second person. Do not copy: a flag photo behind the headline, and a search box that hides behind "MENU" on phones.

---

## Section 2: what the majority do, with counts

Sets: "home" is the 24 entry pages above (for Legistar and Cambridge the calendar is the entry page; for Patch, Nextdoor and 6AM City the town or city page; for Wikipedia the article). "List" is the 9 list pages read in full: Councilmatic events, Legistar's calendar, Boston.gov notices, Boston.gov events, Cambridge's calendar, Documenters' meetings, Craigslist's search, Hacker News' front page, Patch's feed. "Detail" is the 4 detail pages read: a Councilmatic event, a Boston.gov notice, a Cambridge meeting, a Hacker News item. "Sign-up" is the 9 flows with a public form or instruction: Patch, CHStoday, Substack, Cambridge Day, Google Alerts, Visualping, Nixle, Vote411, Nextdoor. All first-screen figures are at 390 by 844 unless marked.

### Home

| Pattern | Count | Who | Ours today |
|---|---|---|---|
| The product itself (real rows, a real article, or the working box) is inside the first screen | 15 of 24 | Boston.gov, Legistar, Cambridge, Patch, Nextdoor, Cambridge Day, Wikipedia, Craigslist, HN (content); Plural, Councilmatic, Google Alerts, Visualping, GOV.UK, USA.gov (a working box or task links). The 9 without are the sales pages: Documenters, Curate, Vote411, Shovels, Zoneomics, CHStoday, Feedly, Nixle, Substack | Yes: the town box at 365 px and the first row at 651 px |
| A one-line explanation of what the site is in the first screen | 17 of 24 | All but Legistar, Boston.gov home, Cambridge, Zoneomics, Cambridge Day, Craigslist, HN | Yes (h1 and one sentence) |
| Exactly one call to action in the first screen | 11 of 24 | Councilmatic, Curate, Shovels, CHStoday, Google Alerts, Visualping, Substack, Wikipedia, Craigslist, GOV.UK, USA.gov | No: "Find my town" (filled) and "Follow a town" (outlined, in the header) |
| A count about the service in the first screen | 5 of 24 | Plural "40+", Documenters "31", Patch "26,376 visits in the last 30 days", Nextdoor "#14 best city", Substack "Over 15,000 subscribers" | No count, but a timestamp: "last checked Oct 30, 2:33 pm" |
| The system's own clock or method in the first screen ("last checked", "a program writes") | 0 of 24 | Wikipedia prints "last edited" in the footer; Boston.gov prints "Posted" per notice | Yes, on the home page, on both town pages and on the meeting page |
| A decorative photo or drawing in the first screen | 11 of 24 | Councilmatic, Documenters, Curate, Vote411, Shovels, Zoneomics, Nextdoor, Boston.gov home, USA.gov, Feedly, Cambridge | No |
| Something above the site's own header (promo strip, cookie banner, ad, official-site strip) | 11 of 24 | Curate, Nixle, GOV.UK, Feedly, Zoneomics, CHStoday, Cambridge Day, Patch (desktop), USA.gov, Boston.gov, Documenters; three of these (Curate, Nixle, GOV.UK) fill the phone screen with a cookie panel | No |
| Words before the main action (the box or the one button) | median about 24; range 0 (Google Alerts, Craigslist) to about 64 (USA.gov, by the fetch tool's count) | Plural 33, Councilmatic 21, CHStoday 10, Visualping 20, Substack 26, Patch subscribe 24, Shovels about 31, GOV.UK about 58 with its cookie banner | 43 |
| A first-timer gets value with no account in 0 or 1 taps | 17 of 24 | Councilmatic, Legistar, Boston.gov, Cambridge, Documenters, Vote411, Patch, Nextdoor (part), CHStoday, Nixle, Substack ("No thanks"), Wikipedia, Craigslist, HN, GOV.UK, USA.gov, Cambridge Day. The 7 that need an account or a demo: Plural, Curate, Shovels, Zoneomics, Feedly, Google Alerts, Visualping (the last two were not tested past the form) | Yes: rows on the home page; a town in 2 taps plus typing |
| The first screen shows a fresh date from the content | 5 of 24 | Boston.gov home "MONDAY, NOVEMBER 2", HN "15 hours ago", Craigslist "<1hr ago", Patch "2d", Cambridge Day "Sunday, November 1, 2026" | The hero says Oct 30 on Nov 2 |
| An example of the output in the first screen (a worked example in the box, chips, a mockup) | 4 of 24 | Plural ("Ohio cannabis licensing" and three chips), Councilmatic ("police, zoning, O2015-7825, etc."), Visualping ("Enter a page: time.com"), Patch's subscribe page (a picture of the newsletter) | "Or try Carver, Amherst or Clay, NY." (three links) |

### List

| Pattern | Count | Who | Ours (/upcoming) |
|---|---|---|---|
| Rows inside the first phone screen | median 6 | HN 15, Cambridge about 9, Boston events about 8, Legistar 8 (unreadable), Councilmatic 6, Documenters about 2.5, Craigslist gallery 1, Boston notices 1, Patch 1 | 1 (the first row starts at 575 px; median row 266 px, so about 3 a screen after that) |
| A date or time printed on every row | 9 of 9 | all | The day is a heading; the row has the time; the date is in a screen-reader suffix only |
| Day or month headings | 2 of 9 | Boston events (day), Cambridge (month); the other 7 put the full date in the row | Day headings, plus an h2 "This week", plus week folds: three levels of grouping |
| Filters above the list | 7 of 9 | not HN, not Patch | Yes |
| Filters collapsed behind one button on a phone | 3 of 7 | Boston notices, Boston events, Documenters (the other 4 leave the controls open: Councilmatic, Legistar, Cambridge, Craigslist) | Yes ("Narrow by county, subject or town") |
| Anything other than controls inside the filter | 0 of 9 | | 573 hidden words; 14 sentences begin "We can't read these ... towns yet"; "website blocks automatic reading" appears 12 times |
| A result count, at the top | 4 of 9 | Legistar "8 records", Cambridge "Displaying 28 meetings from 1/1/2026 to 12/31/2026", Documenters "387 results", Craigslist "1 - 2 of 983" | None at the top; "13 items at 9 meetings" on each week fold |
| The title or subject is the link | 6 of 9 | Councilmatic, Documenters, Craigslist, HN, Patch, Boston notices | Yes |
| Generic link words repeated on every row | 3 of 9 | Legistar "Meeting details" and "Agenda", Cambridge "Agenda Summary" and three more, Boston events "Event details for" | "Read the Nov 2 agenda (PDF)" on every Nov 2 row and "Details" on all 64 |
| The source document linked from the row | 3 of 9 | Legistar, Cambridge, HN | Yes |
| Add to calendar in the row | 2 of 9 | Legistar (iCal icon), Documenters (calendar icon) | Yes, inside the row's Details |
| A sentence of prose in the row | 3 of 9 | Boston notices (when there is one), Boston events (a short description), Patch (a dek) | One to four sentences on every row |
| A canceled item says so in its title | 3 of 3 that had one | Boston events "Canceled: Digital Literacy Workshop", Documenters "Canceled", ours "Canceled: hearing on solar" | Yes |
| Folds inside folds | 0 of 9 | | 18 on /upcoming, 12 on /ma/carver, 3 on /ma/somerset |
| The list is split into pages, months or years | 6 of 9 | Boston (two lists), HN, Craigslist, Councilmatic (month), Cambridge (year) | One page: 64 rows, 14,613 px at 390 (17 screens) |

### Detail

| Pattern | Count | Who | Ours (/m/...) |
|---|---|---|---|
| The heading is the matter, not the body | 2 of 4 | Boston.gov (the notice title), HN (the story title); Councilmatic and Cambridge head with the body or meeting name | The matter ("Draft battery storage bylaw") |
| When and where are the first things after the heading | 3 of 4 | Councilmatic (body, date, time, place), Boston.gov (one sentence, then When, Where, Posted), Cambridge (date, time, location) | One lead sentence, then When, Where |
| The source document is linked | 3 of 4 | Councilmatic (Notice, Agenda), Boston.gov (two PDFs), Cambridge (four PDFs) | Yes |
| Add to calendar | 0 of 4 | | Yes, at about 760 px |
| Whether the public can speak is stated | 1 of 4 | Boston.gov, in the body text | Yes, as a labelled line |
| A subscribe or follow box on the detail page | 0 of 4 | | Yes, at 1,392 px, repeating the header button |
| The system's "first seen" or "last checked" on the page | 0 of 4 | | Twice: "(first seen Oct 23)" by the agenda link and "first seen Oct 23 ... Last checked Oct 30, 2:32 pm" at the end |

### Sign-up

| Pattern | Count | Who | Ours (/watch) |
|---|---|---|---|
| One field on the first step | 7 of 9 | CHStoday, Substack, Cambridge Day, Google Alerts, Nixle, Nextdoor, Vote411 (Patch asks two; Visualping one box plus three settings) | One, then a second step with four buttons |
| The first thing asked is a place | 4 of 9 | Patch (town or ZIP), Nixle (ZIP), Vote411 (address), Nextdoor (address); 3 ask an email first (CHStoday, Substack, Cambridge Day); 2 ask what to watch (Google Alerts, Visualping) | A town |
| How often, said before the button | 4 of 9 | Patch "quick daily email", CHStoday "every morning", Google Alerts "At most once a day", Visualping "Check: Every day" | "Every morning" |
| "Free" said in words | 2 of 9 | Patch "Always free" and "Free. Unsubscribe anytime.", CHStoday "Subscribe free" and "100% Free · No spam" | "Free, no account" |
| A sample of what arrives | 3 of 9 | Patch (a picture of the email), CHStoday ("View latest issue"), Substack (the posts behind "No thanks") | On step 2 only ("Coming up next: Plympton Planning Board Tue Nov 17 ...") |
| A privacy line beside the field | 3 of 9 | Patch, Substack, Vote411 ("Your address will never be saved, sold, or used for marketing purposes.") | None, though nothing is collected |
| The button names what you get | 6 of 9 | "Subscribe Free", "Subscribe free →", "Subscribe", "Create Alert", "Sign up" (two), against "Go", "Get Started", and Nixle's text message | "Continue", then "Follow these towns" |
| Social proof beside the form | 2 of 9 | Substack (subscriber count), CHStoday (the editor's photo and a quote) | None |

---

## Section 3: the dos and don'ts that follow

Each with the sites that support it. "Resident sites" means the ones people use without being sold to: Boston.gov, Patch, Nextdoor, Cambridge Day, CHStoday, Wikipedia, Craigslist, HN, GOV.UK, USA.gov, Google Alerts, Councilmatic, Legistar, Cambridge, Documenters, Vote411, Nixle.

Dos.

1. Show the thing on the first screen. Boston.gov's home shows today's date and four facts about today at 350 px; HN shows 15 stories; Craigslist 200 categories; Patch and Cambridge Day a story at about 250 px; Wikipedia the first sentence and the facts box; Legistar and Cambridge the rows. Where there is no row to show yet, show the working box with an example inside it (Plural, Councilmatic, Google Alerts, Visualping). 15 of 24.
2. One sentence under the name says what the page is, in the second person. USA.gov "USA.gov helps you locate and understand government benefits, programs, and information."; Google Alerts "Monitor the web for interesting new content"; CHStoday "Your morning starts here."; Curate "Know What's Happening in Local Government". 17 of 24.
3. One action per screen, and the header does not compete with it. Google Alerts, Substack, Shovels, Curate, Wikipedia, GOV.UK, USA.gov, Councilmatic. 11 of 24; the ones with two or three (Plural, Vote411, Nixle, Feedly) read as sales pages.
4. Freshness comes from the content's own dates, never from the system's clock. HN "15 hours ago", Craigslist "<1hr ago", Patch "2d", Boston.gov "MONDAY, NOVEMBER 2", Cambridge Day "Sunday, November 1, 2026"; Wikipedia keeps "last edited" in the footer. 0 of 24 print a crawl time near the top.
5. Two lines a row, with the deciding fact on every row. HN (points, age, comments), Craigslist (price, age, place), Councilmatic (date, time, name), Documenters (topic, time, body), Boston.gov events (time, title, place), Boston.gov notices ("The public can offer testimony." only when true). The median list shows 6 rows a screen.
6. The filter is one button on a phone and a row or a side panel on desktop, and holds controls only. Boston.gov (two lists), Documenters, Craigslist. 0 of 9 put prose in it.
7. A canceled item says so in its title. Boston.gov events, Documenters. 3 of 3.
8. The source document and the calendar file live in the row. Legistar, Cambridge, HN (source); Legistar, Documenters (calendar icon).
9. A sign-up asks for one thing, says how often, says it is free, and shows a sample beside the button. Patch (town, email, "quick daily email", "Always free", a picture of it), CHStoday (email, "every morning", "100% Free · No spam", "View latest issue"), Google Alerts (topic, then "At most once a day"), Nixle (a ZIP code by text, and the list of what you will be told), Vote411 (an address, and "Your address will never be saved").
10. The start page order: what you get as three bullets, what you need, one button, then related links. GOV.UK "Check the MOT history of a vehicle". USA.gov's "How do I ..." with four real tasks is the same idea for a home page.
11. A plain place name as the heading with a breadcrumb above it. Nextdoor "United States › Massachusetts › Carver", Wikipedia "Carver, Massachusetts", GOV.UK "Home › Vehicle tax, MOT and insurance".
12. Give the reader a way past the ask. Substack "No thanks", Vote411 "If you'd rather not enter an address, you can view all races or all candidates".
13. Result counts, when shown, are about the results and sit at the top right of the list: Craigslist "1 - 2 of 983", Legistar "8 records", Documenters "387 results", Cambridge "Displaying 28 meetings". 4 of 9; none of the 9 counts anything else.

Don'ts.

1. Don't print when your system last ran, or how it works, in the first screen. 0 of 24 do; Wikipedia's footer is the only place a date like that appears.
2. Don't put a number about yourself in the hero. 19 of 24 don't; the 5 that do (Plural's "40+", Documenters' "31", Patch's visit counter, Nextdoor's ranking, Substack's subscriber count) are the weaker first screens in the set.
3. Don't nest folds. 0 of 9 lists do; Boston.gov and Documenters have one fold, for filters.
4. Don't tell the reader what you cannot do inside a control. 0 of 9; Legistar's "Not available" in 24 cells is what it looks like when a system talks about itself.
5. Don't let bars and banners take the first screen: Zoneomics' announcement pushes its headline below the fold; Nixle has two banners and a cookie modal before its name; CHStoday has three bars before "Your morning starts here."; GOV.UK's cookie banner is the first 450 px on a phone.
6. Don't gate value behind an email (Substack) or a demo (Plural, Curate, Shovels, Feedly). The resident sites give the content first; 17 of 24 need nothing.
7. Don't head a detail page with the body's name (Councilmatic "City Council", Cambridge "City Council Inaugural Meeting") when the reader came for the matter (Boston.gov, HN).
8. Don't use "Today" or "this morning" on a page that is not rebuilt daily. HN writes "on Oct 9, 2006" once an item is old; Boston.gov writes the full date.
9. Don't give one item a whole phone screen when scanning is the task: Boston.gov notices, Patch and Craigslist's gallery each show one; HN, Councilmatic and Boston.gov events show six to fifteen.
10. Don't shrink a desktop page onto a phone (Legistar, Cambridge: the same 204 and 458 words at both widths).
11. Don't write a sentence where a line will do. Boston.gov notices stack "When / Where / Posted" under an italic title and get one row a screen; Boston.gov events put the time and the title on one line and get eight.
12. Don't make the reader choose between two sign-up sentences (Cambridge Day's "Sign up for The Cambridge Day newsletter to get updates in your inbox." and "Sign up to our free newsletter to get the latest news delivered straight to your inbox.") or two hints for one box.

---

## Section 4: our site against those patterns, page by page

Measured Nov 2, 2026 at https://agendaahead.vercel.app with the same scripts (`ours_measure.log`, `measure2.cjs`, the `ours_*` shots). Where a page already matches the pattern it is said once, so the gaps stand out. The owner's verdict is "still not good or up to professional standards"; this section says exactly where the gap is in pixels, words and wording.

### Home (/)

Shots: `ours_home_390.png`, `ours_home_1366.png`, `ours_home_390_full.png`. 5 requests, 211 KB; 3,363 px tall at 390.

- Matches: h1 and one sentence ("See what your town is about to decide" / "Type your town. We'll tell you in plain words what its boards have coming up, with a link to each agenda."); a labelled box with a verb button at 365 px; no photo; no count in the hero; real rows ("This week") on the page; no account needed.
- Gap, freshness: the hero says "We read the agendas every morning; last checked Oct 30, 2:33 pm." and was read on Monday Nov 2, so the first screen contradicts itself (every morning, three days ago). 0 of 24 comparables print a system time in the first screen; Boston.gov's first heading is today's date.
- Gap, the system in the hero: the sentence "It's free and you don't need an account. We read the agendas every morning; last checked ..." is 22 words of self-description between the box and the first row. The first "This week" row starts at 651 px with 73 words before it; the pattern (15 of 24) puts the thing itself in the first screen, and Boston.gov's today-list starts at 350 px.
- Gap, two actions: "Find my town" (filled) and "Follow a town" (outlined, in the header) are both in the first screen; 11 of 24 show one.
- Gap, the sample: the three "This week" rows are three data-center moratoriums with the same sentence shape ("The Town Council talks about this. No vote is listed." three times, one with "Planning Board"); a first-timer sees one story three times and no hearing anyone can speak at. Then "What Carver's page says this morning" at 1,301 px quotes a past meeting ("On Tue Oct 27, Planning Board, 6:30 pm ... The Planning Board held a public hearing.") in a five-sentence paragraph. Patch's sample is a picture of the thing you will get; Plural's is three live queries.
- Gap, link soup: "How it works" step 2 is one 39-word sentence with ten underlined topics ("solar, battery storage, data centers, moratoriums, clean-energy permit rules, zoning changes, affordable housing (40b), cell towers and wetlands permits"); GOV.UK's start page uses three bullets of three to eight words.
- Gap, header: two rows at 390 (wordmark plus the outlined button, then three links), 101 px; HN, GOV.UK and USA.gov use one row.

### Coming up (/upcoming)

Shots: `ours_upcoming_390.png`, `ours_upcoming_1366.png`, `ours_upcoming_390_full.png`. 5 requests, 302 KB; 14,613 px tall at 390 (17 screens); 64 rows.

- Matches: one page, no infinite scroll; day headings; the subject is the link; the agenda PDF is in the row; "Canceled: hearing on solar" names the cancellation in the title; "Anyone can go and speak." when true; a visited-link style now exists; the Narrow fold is one button like Boston.gov's FILTER; the calendar link and the public-comment sentence are in each row's Details (the Oct 28 note asked for this; done).
- Gap, the first screen: the first row is at 575 px (478 at 1366) and only one row fits the first phone screen. Before it: a 20-word lead, the tabs "By date / Biggest stories", the Narrow fold, an h2 "This week" and an h3 "Mon Nov 2" (three heading levels before any content). The comparables' median is 6 rows in the first screen; Boston.gov events, with the same day-heading shape, shows about 8.
- Gap, row height: median 266 px (223 to 402) at 390, five visual lines each (subject, who-line, sentence, agenda link, Details), so about 3 rows a screen afterwards. HN's row is two lines and 15 fit; Councilmatic's is two lines and 6 fit.
- Gap, equal weight for unequal things: in the 45 rows of saved text, 32 sentences end "No vote is listed.", 7 say "nothing is set to be discussed or decided", 5 are public hearings, 1 is canceled, none is a vote. A row that says nothing will happen is as tall and as high as a hearing. HN orders by points and prints them; Craigslist prints the price; Boston.gov prints "The public can offer testimony." only where it applies.
- Gap, hidden prose: the Narrow fold holds 573 words, of which 14 sentences begin "We can't read these ... towns yet" and 12 say "website blocks automatic reading". 0 of 9 lists carry anything but controls in the filter; the only comparable that talks about its own gaps in the list is Legistar ("Not available").
- Gap, nested folds: 18 details sit inside other details ("Week of Nov 9 / 13 items at 9 meetings" folds hold each row's Details). 0 of 9 comparables nest; GOV.UK's rule says not to.
- Gap, headings: "Affordable housing permit (40B) for a housing project by MP Properties IV at 0 & 194 Lowland Street" (18 words), "Special permit and site plans for a solar and battery project at 2 Sand Pit Road" (16), "Affordable housing permit (40B) for 50 units of housing by Sandwich Road Housing on Sandwich Road" (16), "Old Warren Development II at 440 Old Warren Rd" (a developer's name as the subject). HN's longest first-screen title is 11 words; Councilmatic's rows are two or three.
- Gap, repeated link text: "Read the Nov 2 agenda (PDF)" appears 19 times in the saved text (the screen-reader suffix differs; the eye cannot tell), and "Details" 64 times.
- Gap, sentences: 70 sentences over 25 words in the main (folded text included).

### Town pages (/ma/carver, /ma/somerset)

Shots: `ours_carver_390.png`, `ours_carver_390_full.png`, `ours_carver_1366.png`, `ours_somerset_390.png`, `ours_somerset_1366.png`.

- Somerset is close to the pattern: breadcrumb, h1 "Somerset, Massachusetts", a two-sentence lead that names the next meeting ("The first is the Zoning Board of Appeals on Thu Nov 5 ..."), the button at 515 px, the first row at 650 px with "The Zoning Board of Appeals holds a public hearing. Anyone can go and speak." and the agenda link at 827 px. Gaps: 96 words before the first row; the system note under the lead (below).
- Carver, gap, the lead contradicts the rows: "Nothing new is on Carver's agendas about solar, batteries, data centers, zoning or housing, but two items have moved to November, listed below." is followed by two rows that each say "It's a public hearing, so anyone can go and speak." Councilmatic's home says the next meeting first ("Next City Council meeting / Mon 11/02/2026 / 10:00a.m.").
- Gap, the system under the lead, on both pages: "We read the agendas Carver posts online Oct 30, 7:07 am. A program writes each sentence from the agenda; the link under it is the source." 0 of 24 comparables explain their method on the page; Wikipedia puts its one such line in the footer.
- Gap, the section heading: "Coming up, dated from earlier agendas" wraps to two lines at 390 and describes the generator's problem; Boston.gov's heading is the date.
- Gap, two rows that look like one: "Federal Pond Solar, 104 Tremont St" (Conservation Commission, Wed Nov 4) and "Federal Pond Solar's hearing at 104 Tremont Street" (Planning Board, Tue Nov 10), one with "St" and one with "Street", each followed by a four-sentence paragraph that starts "The town hasn't posted that agenda yet, so there's no time; the date comes from the Oct 21 agenda."
- Gap, order: on Carver the Follow button is at 1,186 px (after the rows); on Somerset at 515 px (before them). The same page type has two orders.
- Gap, the past before the neighbours: "Most recent" (two past meetings with Details) runs from 1,282 to about 2,100 px before "Next door"; 12 nested folds ("Earlier meetings, back to July" holds row Details).
- Gap, "Next door": "Plympton has solar on its agenda for Tue Nov 17. Nothing in Kingston, Plymouth and Wareham. We can't read Middleborough's agendas yet (why)." The negative is the last thing on the page's main part; Patch's "Nearby Communities" and Craigslist's "nearby cl" are names only.
- 30 sentences over 25 words on Carver, 15 on Somerset.

### Meeting page (/m/egremont-planning-board-2026-10-30)

Shots: `ours_meeting_390.png`, `ours_meeting_390_full.png`, `ours_meeting_1366.png`. 5 requests, 176 KB.

- Matches, and better than all four comparables: the matter is the h1; When, Where, Public comment ("No public hearing is listed. The agenda doesn't say whether you can comment; the town clerk would know."), Agenda and Calendar as a plain list; the calendar link at about 760 px (0 of 4 comparables have one); the source PDF.
- Gap, a stale word: "Today at 10 am, online." was read on Nov 2 for a meeting on Fri Oct 30. HN writes "on Oct 9, 2006"; Boston.gov writes the full date.
- Gap, crawler facts twice: "(first seen Oct 23)" beside the agenda link and "From the Planning Board agenda first seen Oct 23 on egremont-ma.gov. Last checked Oct 30, 2:32 pm. Copy citation" at the end. 0 of 4 comparables print either.
- Gap, the same item explained twice: "On the agenda" repeats the h1 ("A draft battery storage bylaw: discussion", "Discussion", "Topics: Battery storage, clean-energy permit rules"), then an "Agenda wording" fold, then an open paragraph "Words on the agenda. Battery energy storage: large batteries that store electricity ..." (one fold and one open paragraph for one sentence of agenda text).
- Gap, a follow box on a detail page: "Follow Egremont" (heading, two sentences, a filled button, "Copy link") at 1,392 px repeats the header button; 0 of 4 comparables carry one.

### Follow a town (/watch)

Shots: `ours_watch_390.png`, `ours_watch_1366.png`, `ours_watch2_390.png` (step 2 after choosing Carver), `ours_watch2_390_full.png`. 9 requests, 392 KB (towns.json 54 KB, neighbors.json 133 KB) to show one box. `/api/status` returns `{"ok":true,"email_alerts":false}`.

- Matches: a town first (like Patch, Nixle, Vote411, Nextdoor); "Every morning" and "Free, no account" before the field (like Patch and CHStoday); one field on step 1; a preview on step 2 ("Over the last 30 days, Carver and 5 towns next to it had 10 meetings on these topics ... Coming up next: Plympton Planning Board Tue Nov 17 / Parallel Products ground-mounted solar, 87 County Road: hearing continues Nov 17").
- Gap, two hints for one box: "Start typing and pick it from the list." above the field and "Pick it from the list as you type." below it.
- Gap, a 49-word lead in three sentences before the field; Patch's subscribe page uses 24 words, CHStoday 10.
- Gap, the promise withdrawn on the same screen: step 2 says "so expect about that many alerts a month" and three lines later "You get this two ways: a page you can bookmark that updates every morning, and a feed for your phone's calendar. We can't email yet." Nothing arrives; the page calls them alerts.
- Gap, four buttons on step 2: "Change town", "Change topics", "Choose topics or towns", "Follow these towns"; Patch has one ("Subscribe Free"), CHStoday one ("Subscribe free →").
- Gap, the button words: "Continue" then "Follow these towns" (6 of 9 comparables name what you get: "Subscribe", "Create Alert").
- Gap, no line about data: nothing is collected and the page does not say so; Vote411 says "Your address will never be saved".

### Search (/search)

Shot: `ours_search_390.png`. 6 requests, 227 KB on open (the Oct 28 figure was 217 requests and 6.6 MB; fixed).

- Matches: a label ("Search for"), one button, example links ("Try battery storage, data center moratorium, cell tower or 40B."), a Filters fold, and nothing loads until a search.
- Gap: the example "data center moratorium" is a placeholder inside the box; GOV.UK uses a label and no placeholder, and the spec's rule 43 says the same. Councilmatic and Plural do use example placeholders, so this is the smallest gap on the site.

### Towns (/towns)

Shot: `ours_towns_390.png`, `ours_towns_1366.png`. 45 folds, none nested (the nested state folds from the Oct 28 note are gone).

- Gap: every line leads with what we cannot do: "351 towns, 243 we read every morning", then "Barnstable County 15 towns, 3 we can't read yet", "Berkshire County 32 towns, 15 we can't read yet", for 14 counties. Craigslist's region list and Patch's "Nearby Communities" are names; GOV.UK's "Services and information" is 16 plain categories.

### Biggest stories (/trending)

Shot: `ours_trending_390.png`, `ours_trending_1366.png`. 9 requests, 447 KB.

- Gap, a control above the content: a grey "Your towns" panel (placeholder "Type a town", an "Add" button) at 457 px and a "Filter by date or topic" fold put the first row at 595 px with 99 words before it; the spec's rule 8 keeps filters off the first screen, and 3 of 7 comparables collapse them.
- Gap, the ranking is not shown: "ranked by what's at stake and how stirred up people are" with no number on the row; HN prints the points that order it. The rows carry two extra lines ("Proposed ban", "Two boards are handling this") and the "New on an agenda" label.
- 19 sentences over 25 words.

### How it works (/how-it-works)

Shot: `ours_howitworks_390.png`. 8 sentences over 25 words; the first sentence is 40 words.

- Gap: GOV.UK's start page says what you get as three bullets; this page's first paragraph is one sentence listing six topics and three states. "What the labels mean" explains words (Vote, Hearing, Discussion) that now appear only inside a row's Details.

### Across pages

- The header's "Follow a town" button is outlined on every page and filled on /watch, so the site has two button styles on most first screens.
- Three pages carry the crawler's clock in the first screen (home, Carver, Somerset) and one carries it twice (the meeting page). None of 24 comparables does this once.
- Nested folds: 18 on /upcoming, 12 on Carver, 3 on Somerset; 0 in the comparables.
- Sentences over 25 words: 70, 30, 19, 15, 8 on the five pages with prose.

---

## Section 5: the 15 changes with the biggest effect, ranked

Each: the page, the element, the exact wording or order, the site it copies, and why it is professional rather than decorative. "Professional" here means what the comparables share: the page proves itself with its content, speaks in the reader's terms, and never talks about its own machinery.

1. **Home: put the first row in the first screen and take the system out of the hero.** Delete the paragraph "It's free and you don't need an account. We read the agendas every morning; last checked Oct 30, 2:33 pm." Make the line under the box "Or try Carver, Amherst or Clay, NY. Free, no account." Start "This week" directly after it. The first row moves from 651 px to about 560 px at 390 and the words before it from 73 to about 45; with change 11 it reaches about 500 px. Copies Boston.gov's home (today's facts at 350 px) and HN. Professional because the first screen shows the product doing its job instead of describing it.

2. **Every page: no clock in the first screen, and no "Today" on a page that is not rebuilt daily.** Either build every morning including Saturday and Sunday (the site claims "every morning"; on Monday Nov 2 it said Oct 30), or write absolute dates only. In the generator: never emit "Today", "Tomorrow" or "this morning"; the meeting lead becomes "Fri Oct 30 at 10 am, online."; the town note "We read the agendas Carver posts online Oct 30, 7:07 am. A program writes each sentence from the agenda; the link under it is the source." moves to the page-end "About Carver's agendas" fold; the home hero's "last checked" goes to the footer as "Checked Mon Nov 2, 7:03 am". Copies Wikipedia (last-edited in the footer only), HN ("on Oct 9, 2006"), Boston.gov (the date as a heading, never a time of crawl). Professional because a wrong "Today" or a three-day-old "every morning" is the fastest way to lose a first-timer's trust.

3. **Coming up: six rows in the first phone screen, two lines each where the sentence adds nothing.** Order of the top: h1 "Coming up", one 12-word line ("Town meetings in the next few weeks about solar, batteries, data centers, zoning, housing and cell towers."), then the tabs and the Narrow fold on one line, then the day heading (drop the h2 "This week"; the day heading is enough, as on Boston.gov events). Row: subject link on line one; on line two "Town Council, 4 pm, Town Hall or online · Agenda (PDF)" with the agenda link in the line; the sentence only when it says something ("Public hearing: anyone can go and speak.", "The board votes.", "Canceled."); "Details" only when the row has a quote or a comment rule. Target: first row at about 380 px, median row under 140 px, six rows a screen. Copies HN (two lines, 15 a screen) and Boston.gov events (time, title, place, one link, 8 a screen). Professional because density is what a list is for; a reader should see a week at a glance.

4. **Coming up: rank each day by weight, and fold the mentions.** Within a day: hearings and votes first, then discussions, then one line "Also on agendas today: solar in Truro, data centers in Acton and 5 more" that opens to the mention rows. Today 39 of 45 saved rows say nothing will be decided and they sit level with the five hearings. Copies HN (the number that decides order is printed on every row), Craigslist (price on every row), Boston.gov notices ("The public can offer testimony." only when true). Professional because a list that knows what matters is the difference between a tool and a dump.

5. **Coming up and town pages: no fold inside a fold.** Make "Later, by week" plain h2 week headings with the rows open, or keep one fold per week whose rows have no Details of their own (put the comment rule and the calendar link as plain lines in those rows). Remove the row Details from inside "Earlier meetings, back to July" on town pages. 18, 12 and 3 nested folds become 0. Copies Boston.gov and Documenters (one fold, for filters) and the GOV.UK accordion rule. Professional because two levels of hiding is where usability studies stop measuring.

6. **Coming up: the Narrow fold holds controls only.** Move the 14 "We can't read these ... towns yet" sentences (573 hidden words) to /towns under each county, and keep in the fold just County, Topic, Town, "Clear filters" and "Only my towns". Copies Documenters' Filters panel and Craigslist's sidebar. Professional because a filter is a control; a confession inside it reads as a system apologising.

7. **Subject headings: eight words, the thing first, no applicant.** Generator rule: strip "Special permit and site plans for", "for a housing project by X", "at 0 &"; move the applicant to the sentence. "Affordable housing permit (40B) for a housing project by MP Properties IV at 0 & 194 Lowland Street" becomes "40B housing at 194 Lowland Street" with "MP Properties IV asks for the permit." as the sentence; "Old Warren Development II at 440 Old Warren Rd" becomes "Project at 440 Old Warren Road (public hearing)"; "Affordable housing permit (40B) for 50 units of housing by Sandwich Road Housing on Sandwich Road" becomes "50 homes (40B) on Sandwich Road". Copies HN and Councilmatic (titles of two to eleven words) and Boston.gov notices' one-sentence summary under a long title. Professional because the heading is the only thing most people read.

8. **Carver: a lead that agrees with the rows, one heading per hearing, and the Follow button in the same place on every town page.** Lead: "Two public hearings on Federal Pond Solar's project at 104 Tremont Street are coming up: the Conservation Commission on Wed Nov 4 and the Planning Board on Tue Nov 10. Anyone can go and speak." Section heading "Coming up" (not "Coming up, dated from earlier agendas"). Row headings "Federal Pond Solar, 104 Tremont Street: Conservation Commission hearing" and "...: Planning Board hearing". Row sentence order: the right to speak first, then "The town hasn't posted that agenda yet, so there's no time; the date comes from the Oct 21 agenda." Put the Follow button after the lead on every town page (Somerset's order, 515 px), never after the rows (Carver's, 1,186 px). Copies Councilmatic's "Next City Council meeting" block and Boston.gov's date-first heading. Professional because a page that says "nothing new" above two hearings is wrong, and a first-timer cannot tell which half to believe.

9. **Follow a town: one hint, one promise, one button, and the sample beside the button.** Step 1: delete "Pick it from the list as you type."; cut the lead to "Every morning we read your town's agendas and put what its boards have coming up on a page and a calendar feed, for your town and the towns next door. Free, no account, no email." Step 2: replace "so expect about that many alerts a month" with "so expect about ten meetings a month on your page"; put "Coming up next: ..." directly under the heading; one filled button "Make my page and calendar feed"; "Change town" and "Change topics" as plain links on one line; drop "Choose topics or towns". Add under the button: "We store nothing. The page address is yours to bookmark." Copies Patch's subscribe page (town, email, "quick daily email", "Always free", a picture of the thing, one button, "Unsubscribe anytime") and CHStoday ("View latest issue" beside "Subscribe free"). Professional because the page keeps every promise it makes on the same screen.

10. **Meeting page: absolute date in the lead, crawler facts once at the end, no follow box.** Lead: "Fri Oct 30 at 10 am, online. The Planning Board talks about this. No vote is listed." Remove "(first seen Oct 23)" from the Agenda line (it stays in the citation). Replace the "Follow Egremont" box (heading, two sentences, button, "Copy link") with one line after the facts list: "Everything coming up in Egremont · Follow Egremont". Merge "On the agenda" and "Agenda wording" into one block: the item line, then the quoted agenda words open, no fold. Copies Boston.gov's notice page (title, one sentence, When, Where, the PDFs) and the GOV.UK summary list. Professional because the page already beats all four comparables on the comment line and the calendar link; the rest is weight.

11. **Header: one row, no button.** "Follow a town" becomes the fourth plain link ("Coming up · Towns · Search · Follow"); the only button on any page is that page's own. The header drops from two rows (101 px) to one (about 56 px) at 390, and every first screen has one filled control. Copies HN (one bar), GOV.UK and USA.gov (one row with Menu and Search). Professional because a site with one job does not need to sell its second feature in the chrome.

12. **Towns: names and counts of what we read, with the gaps one level down.** "Massachusetts: 243 towns" as the state line; each county "Barnstable County: 12 towns" with the three we cannot read inside the fold under their own line "Not yet: Barnstable and Chatham (their websites block automatic reading), Harwich (allows fewer than one visit a day)". Copies Craigslist's "nearby cl" list and GOV.UK's category list (names, no caveats). Professional because the page leads with what it can do; the caveat is there for whoever needs it.

13. **Coming up: cap every generated sentence at 25 words and vary the stock sentence.** Split "what" sentences at the first "to build", "at" or "within"; move statutes to Details. Replace the 32 identical "The X talks about this. No vote is listed." with the shorter "Discussion only." on the second line of the row (change 3), and keep the full sentence for hearings and votes. Copies GOV.UK (bullets of three to eight words) and Councilmatic's rows (a name, a date, a time). Professional because 70 long sentences on one page is a readability failure a tester can measure.

14. **Biggest stories: filters off the first screen and the rank shown.** Move the "Your towns" panel and "Filter by date or topic" into one "Narrow" fold like /upcoming, so the first row sits at about 380 px instead of 595. Print the thing that ranks the row as a short grey line ("Ban proposed · 2 boards · 3 towns nearby") or drop the claim "ranked by what's at stake and how stirred up people are". Copies HN (points on every row) and the site's own /upcoming fold. Professional because a ranking without a visible reason reads as an opinion.

15. **Home: the sample is a hearing, and How it works is three bullets.** Choose the three "This week" rows by kind (one public hearing, one vote or moratorium, one project), not by score, so the sample shows the right to speak. Replace "What Carver's page says this morning" (a past meeting, five sentences) with the next hearing from any town in two sentences and "Read Plymouth's page". Rewrite step 2 of How it works as three bullets: "solar, batteries and data centers", "zoning and affordable housing (40B)", "cell towers and wetlands permits". Copies Patch (a picture of the newsletter on the sign-up page), GOV.UK's three bullets. Professional because the example is the promise, and the promise is "what your town is about to decide", not what it decided last Tuesday.

Changes 1, 2, 3, 5, 6, 10, 11, 12 and 13 are generator rules and a few CSS lines; 4, 7 and 15 need a ranking rule and a heading rule in the generator; 8 and 9 are wording; 14 is a layout move. None needs a framework, a second script or a new colour.

---

## Summary

1. 24 sites were read page by page and screenshotted at 390 and 1366; GovTrack, LegiScan, Ballotpedia, BuildZoom and Axios refused both the fetch tool and the browser (403) and are not quoted; Documenters refused the fetch tool but loaded in the browser.
2. The resident sites that work (Boston.gov, HN, Craigslist, Patch, Wikipedia, GOV.UK, Councilmatic) put the thing itself on the first screen: 15 of 24 do; the 9 that open with a slogan are the ones selling to businesses.
3. 0 of 24 print when their system last ran or how it works in the first screen; our home, both town pages and the meeting page do, and on Nov 2 the home page said "last checked Oct 30" under "every morning".
4. Lists: the comparables' median is 6 rows in the first phone screen (HN 15, Boston.gov events 8); ours shows 1, with the first row at 575 px and a median row of 266 px.
5. 0 of 9 comparable lists nest folds or put prose in the filter; /upcoming has 18 nested folds and 573 hidden words of "we can't read" inside Narrow.
6. Of 45 saved rows on /upcoming, 39 say no decision will be made and sit level with 5 hearings; HN, Craigslist and Boston.gov print the deciding fact on every row and order by it.
7. Our meeting page already beats all four comparable detail pages (the matter as heading, a public-comment line, a calendar link); its faults are a stale "Today", crawler facts twice and a follow box nobody else has.
8. Sign-ups that work ask one thing, say how often and that it is free, and show a sample beside the button (Patch, CHStoday); /watch does most of this but shows two hints for one box, promises "alerts" and then says "We can't email yet", and ends in four buttons.
9. Carver's lead ("Nothing new") sits above two public hearings, two near-duplicate headings, and a Follow button 670 px lower than Somerset's.
10. The 15 changes, in order: first row in the first screen and no clock in the hero; absolute dates and daily builds; six two-line rows a screen; rank by weight and fold mentions; no nested folds; controls only in Narrow; eight-word headings; Carver's lead and order; one hint, one promise, one button on Follow; the meeting page's lead and box; a one-row header; /towns leads with what we read; 25-word cap and fewer stock sentences; Biggest stories' filters folded and its rank shown; a hearing as the home sample and three bullets in How it works.
