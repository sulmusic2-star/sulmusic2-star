# 351 Watch — validation test (started Oct 10, 2026)

**Live site:** https://351watch-sulmusic2-4637s-projects.vercel.app
**Decision rule:** build the paid product if about 20 business emails join the waitlist by **Nov 9, 2026**.

## What was checked today

| Check | Result |
|---|---|
| Does Hamlet already cover Massachusetts? | Its own MA coverage page lists 81 of 351 municipalities (~23%). In the 30-town sample: 3 partial, 0 confirmed full, 5 no evidence, 22 unverifiable (site blocks automated checks). |
| Other competitors | SitePath: bylaws on file for 15 of 30 towns but no meeting-level tracking. CivicSearch: 2 of 30. **Citizen Portal (citizenportal.ai)** writes AI articles from planning/conservation/select board meetings in at least 6 sample towns — the closest threat. |
| Can software read the agendas? | Yes. The crawler automated 24 of 30 towns, scanned 338 agenda documents (93 were image scans, recovered with OCR) and flagged 178 items. |
| Did it find things manual research missed? | Yes — e.g. Fitchburg's proposed BESS moratorium (Oct 6), Pittsfield's BESS zoning amendment (Oct 13), Westford's clean-energy zoning article for its Oct 26 town meeting. |
| Is the business model proven elsewhere? | Yes. Deltek bought Onvia for $70M; mdf commerce bought Periscope for $207M; Byggfakta bought Glenigan for £72.9M; Shovels (permit data, $599–$999/mo) bought ReZone, a zoning-decision tracker, in Jan 2026. Details: `research_notes/Meeting monitor validation/`. |

Towns the crawler could not read: Becket, Middleborough, Barnstable (Cloudflare bot protection), Framingham (Granicus robots.txt), Medway (HeyGov API robots.txt), Worthington (no agendas posted online). These need the town's or vendor's permission, not more code.

## Checking signups

- **Vercel dashboard:** Storage → `351watch-submissions` → `waitlist/` folder (one JSON file per signup).
- **API:** `GET /api/admin/submissions` with `Authorization: Bearer <ADMIN_TOKEN>`. The token is stored as a sensitive Vercel env var and can't be read back; to get a new one, upsert `ADMIN_TOKEN` on the `351watch` project and redeploy.
- One test message from `deploy-check@351watch.invalid` is in `contact/` — ignore it.

## Getting the 20 signups (owner tasks)

The page won't get traffic on its own in 30 days. Suggested outreach, all owner-approved:

1. Post the tracker on LinkedIn and in the Northeast Clean Energy Council, SEBANE and MassCEC community channels, framed as a free resource ("every BESS/solar moratorium in Massachusetts, sourced").
2. Email 30–50 Massachusetts solar/storage developers and land-use attorneys individually (template below). Keep it to a handful a day from a normal mailbox.
3. Send the tracker to reporters who cover these fights (local papers in Berkshire, Worcester and Plymouth counties).

**Email template**

> Subject: Free tracker — every BESS/solar moratorium in Massachusetts towns
>
> Hi {name} — I built a free, source-linked tracker of battery storage and solar moratoria, special acts and new consolidated-permit bylaws across Massachusetts towns: {site URL}
>
> It also reads town board agendas automatically — this week it flagged Fitchburg's proposed BESS moratorium and Pittsfield's BESS zoning amendment before the meetings.
>
> I'm deciding whether to turn it into daily agenda alerts for the towns you choose. If that would help your team, the waitlist is on the page. Any corrections welcome too.

## Before charging money

- The project is on Vercel's Hobby plan, which Vercel limits to non-commercial use. Move to Pro ($20/mo; a free trial is available on this account) before launching paid plans.
- Optional: `351watch.com` was available on Oct 10, 2026 (not purchased).
- Rerun `crawler/` and `build.py`, commit, and redeploy to refresh the page.
