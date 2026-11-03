# New York follow-up: what reads now (2026-11-03)

Built by `python3 experiments/ny_followup.py report` from data/test/ny_followup/ (config, crawl run 2026-11-03, index 18 documents). Nothing here is in production.

| Place | Platform | Status | Boards read | Documents (dated) | Meeting dates | Hits | Reason / errors |
|---|---|---|---|---|---|---|---|
| Huntington | granicus | not automated | - | 0 (0) | - | 0 | vendor_blocked: agendas on granicus: robots.txt on huntingtonny.granicus.com disallows AgendaAheadBot |
| Lansing | civicplus | ok | planning_board, select_board | 7 (7) | 2026-09-23 to 2026-11-09 | 0 |  |
| Cicero | - | not automated | - | 0 (0) | - | 0 | documents_blocked: robots.txt disallows documents on cicerony.gov |
| Pound Ridge | agenda_page | ok | select_board | 3 (3) | 2026-11-04 to 2026-11-04 | 0 |  |
| Southampton | escribe | ok | conservation_commission, planning_board, select_board, zoning_board_of_appeals | 2 (2) | 2026-11-04 to 2026-11-05 | 0 |  |
| Perth | munibit | failed | - | 0 (0) | - | 0 | meeting list read: 5 agenda files in the window {'select_board': 2, 'planning_board': 3}; files not served to the reader (see munibit_meetings.json).  |
| Spafford | munibit | failed | - | 0 (0) | - | 0 | meeting list read: 2 agenda files in the window {'planning_board': 1, 'select_board': 1}; files not served to the reader (see munibit_meetings.json).  |
| Boston | munibit | failed | - | 0 (0) | - | 0 | meeting list read: 3 agenda files in the window {'select_board': 3}; files not served to the reader (see munibit_meetings.json).  |
| Schoharie County | agenda_page | ok | planning_board | 1 (1) | 2026-11-02 to 2026-11-02 | 0 |  |
| Schenectady County | - | not automated | - | 0 (0) | - | 0 | no_agendas_found: site reachable, but no agenda listing for the tracked boards was found (agendas may be posted only on paper, only as minutes, or on pages the heuristics missed) |
| Tompkins County | iqm2 | not automated | - | 0 (0) | - | 0 | vendor_blocked: agendas on iqm2: robots.txt on tompkinscountyny.iqm2.com disallows AgendaAheadBot |
| Wayne County | civicplus | ok | planning_board | 1 (1) | 2026-10-28 to 2026-10-28 | 0 |  |
| Steuben County | - | not automated | - | 0 (0) | - | 0 | no_recent_agendas: board pages found (e.g. https://www.steubencountyny.gov/220/Planning) but no agenda dated within the last 120 or next 120 days could be read from them |

## Notes (read by hand on 2026-11-03)

- **Huntington**: The town site answers at its 15 s crawl delay, but every agenda is on huntingtonny.granicus.com, whose robots.txt disallows all agents but Googlebot, Slurp, msnbot and the county's own search; the town's /meetings page lists no documents. Needs the vendor letter, not a crawler change.
- **Lansing**: lansingtownny.gov asks a 10 s crawl delay since 2026-10-20 (15 s in October). CivicPlus AgendaCenter with Town Board and Planning Board categories; the AgendaCenter agenda files are cover sheets, so the listings carry linked_agenda and the DocumentCenter agenda is read (four Town Board agendas Sept 23 to Nov 4, one Planning Board agenda Nov 9). The ZBA page lists no dated agendas; older documents sit in a Laserfiche WebLink repository (lfweb.tompkins-co.org), not read.
- **Cicero**: ciceronewyork.net now redirects to cicerony.gov (Crawl-delay 20 s, honoured). Its /meetings/ page lists every board's agendas (ZBA Nov 2, Planning Board Nov 4, Town Board Oct 14, 16, 28) as PDFs under /wp-content/uploads/, which robots.txt disallows for all agents. The ask for the letter: Allow: /wp-content/uploads/ for User-agent: AgendaAheadBot. Hearing notices are also HTML posts (cicerony.gov/category/public-hearings/), readable if a notices listing is wanted.
- **Pound Ridge**: Wave-2 row: townofpoundridge.gov asks 15 s, readable since the cap rose. Town Board agenda, backup packet and hearing notice for Nov 4 read; the Planning Board and ZBA pages list no dated agendas in the window.
- **Southampton**: eSCRIBE portal: the Conservation Board (Nov 4) and ZBA (Nov 5) HTML agenda views read with text_source html; the Town Board (work session Nov 5, regular Nov 10) and Planning Board meetings are listed on the portal but their agendas were not yet published. The PDF download was never requested.
- **Perth**: Munibit module: the JSON lists the Town Board agenda of Nov 5 (with public hearing materials) and Oct 1, and the Planning Board's monthly meeting notices (September to November); the files are served only to the site's own viewer.
- **Spafford**: Munibit module: Town Board agenda Oct 8 (the Nov 5 meeting folder holds budget documents, no agenda yet) and Planning Board agenda Oct 15; the Oct 8 folder also holds the Local Law C-2026 solar moratorium texts and GML referral. Files served only to the viewer.
- **Boston**: Munibit module on each board page (bostonny.gov): Town Board agenda packets Sept 30 and Oct 21, agenda & minutes Sept 30; Planning Board and ZBA have no documents since June and August. Files served only to the viewer.
- **Schoharie County**: Revize site; the Planning Commission page (first Monday of the month) posts dated agendas and each meeting's referral files. The Nov 2 agenda lists referrals from Gilboa, Schoharie, Cobleskill, Richmondville, Jefferson and Seward, in the 'Town of X:' form attribution.py reads.
- **Schenectady County**: Drupal site; the Economic Development and Planning department pages (ag district, trails, aquifer, GIS) name no planning board or commission and post no agendas. 239-m reviews appear to be a department function.
- **Tompkins County**: The Legislature and its committees are on tompkinscountyny.iqm2.com (closed vendor; its robots.txt did not answer, which RFC 9309 treats as disallow). The Planning and Sustainability department's pages list advisory boards (tourism, transportation council) but no county planning board agendas; 239 reviews are staff work.
- **Wayne County**: waynecountyny.gov (web.co.wayne.ny.us redirects there): CivicPlus AgendaCenter with a 'Wayne County Planning Board' category. The Oct 28 agenda read (referrals as 'T. Ontario (Applicant)', 'V. Newark', which attribution.py reads); the Sept 23 file is an 87 MB packet, over the 40 MB download cap.
- **Steuben County**: steubencountyny.gov answered this time (CivicPlus). Its AgendaCenter holds the Legislature and its committees only; the Planning department's Planning & Zoning Assistance page says 239-m referrals are reviewed by the department on a referral form. There is no county planning board agenda to read.

## Document records

### Lansing

- 2026-09-23 · Town Board · ok · ocr · 0 hits · https://www.lansingtownny.gov/AgendaCenter/ViewFile/Agenda/_09232026-18
- 2026-09-23 · Town Board · ok · pdf · 0 hits · https://www.lansingtownny.gov/DocumentCenter/View/712
- 2026-09-29 · Town Board · ok · ocr · 0 hits · https://www.lansingtownny.gov/AgendaCenter/ViewFile/Agenda/_09292026-19
- 2026-09-29 · Town Board · ok · pdf · 0 hits · https://www.lansingtownny.gov/DocumentCenter/View/718
- 2026-10-21 · Town Board · replaced · ocr · 0 hits · https://www.lansingtownny.gov/AgendaCenter/ViewFile/Agenda/_10212026-13
- 2026-10-21 · Town Board · ok · pdf · 0 hits · https://www.lansingtownny.gov/DocumentCenter/View/696
- 2026-11-04 · Town Board · replaced · ocr · 0 hits · https://www.lansingtownny.gov/AgendaCenter/ViewFile/Agenda/_11042026-20
- 2026-11-04 · Town Board · ok · pdf · 0 hits · https://www.lansingtownny.gov/DocumentCenter/View/720
- 2026-11-09 · Planning Board · replaced · pdf · 0 hits · https://www.lansingtownny.gov/AgendaCenter/ViewFile/Agenda/_11092026-15
- 2026-11-09 · Planning Board · ok · ocr · 0 hits · https://www.lansingtownny.gov/AgendaCenter/ViewFile/Item/17?fileID=829

### Pound Ridge

- 2026-11-04 · Town Board Meeting (courtroom) · ok · pdf · 0 hits · https://www.townofpoundridge.gov/sites/default/files/fileattachments/town_board/meeting/41258/11.4.26_tbm_agenda.pdf
- 2026-11-04 · Town Board Meeting (courtroom) · ok · pdf · 0 hits · https://www.townofpoundridge.gov/sites/default/files/fileattachments/town_board/meeting/41258/proposed_lls_on_exemptions.pdf
- 2026-11-04 · Town Board Meeting (courtroom) · ok · pdf · 0 hits · https://www.townofpoundridge.gov/sites/default/files/fileattachments/town_board/meeting/packets/41258/backup_for_11.4.26_tbm.pdf

### Southampton

- 2026-11-04 · Conservation Board · ok · html · 0 hits · https://pub-southamptonny.escribemeetings.com/Meeting.aspx?Id=8132262f-311c-4d6b-838e-f12230f1b8f2&Agenda=Agenda&lang=English
- 2026-11-05 · Zoning Board of Appeals · ok · html · 0 hits · https://pub-southamptonny.escribemeetings.com/Meeting.aspx?Id=1f13e5d6-d873-4cae-993d-5d877f30ab23&Agenda=Agenda&lang=English

### Schoharie County

- 2026-11-02 · Schoharie County Planning Commission · ok · pdf · 0 hits · https://schohariecounty-ny.gov/November 2, 2026 Agenda.pdf

### Wayne County

- 2026-09-23 · Wayne County Planning Board · error · - · 0 hits · https://www.waynecountyny.gov/AgendaCenter/ViewFile/Agenda/_09232026-1559 · too large (86818080 > 41943040 bytes): https://www.waynecountyny.gov/AgendaCenter/ViewFile/Agenda/_09232026-1559
- 2026-10-28 · Wayne County Planning Board · ok · pdf · 0 hits · https://www.waynecountyny.gov/AgendaCenter/ViewFile/Agenda/_10282026-1575

