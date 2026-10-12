# 351 Watch — operations runbook

## Daily refresh (scheduled 6:59 am America/New_York)

1. Repo `sulmusic2-star/sulmusic2-star`, branch `claude/massachusetts-market-service-ead9ho` (`git pull --ff-only` first).
2. `bash projects/351watch/ops/daily.sh` — refreshes MassDEP wetlands filings, crawls MA/NY/RI agendas incrementally (state in `data/state/`), appends the text of each new document to `data/search/` (and fills any row still missing from the local cache), rebuilds the site, commits "Daily refresh YYYY-MM-DD", pushes. Last printed line = commit SHA. A fresh container works: only listing pages are re-read; agenda documents already processed are skipped, and their search text is already in git.
3. Deploy that SHA to production with the Vercel MCP `create_deployment` (no teamId):

```json
{
  "forceNew": "1",
  "skipAutoDetectionConfirmation": "1",
  "requestBody": {
    "name": "351watch",
    "project": "prj_iabrmjhEjYOlkpWyuPeQvZjul2I2",
    "target": "production",
    "projectSettings": {
      "framework": null,
      "buildCommand": "curl -fsSL https://raw.githubusercontent.com/sulmusic2-star/sulmusic2-star/<SHA>/projects/351watch/site/vercel-build.sh | SITE_REF=<SHA> sh",
      "installCommand": "",
      "outputDirectory": null
    },
    "files": [{"file": "package.json", "data": "{\"name\":\"351watch-bootstrap\",\"private\":true}\n"}]
  }
}
```

   The build (`site/vercel-build.sh`) assembles everything from git at that commit — pages, data, API functions, routing and the daily cron — so code changes ship the same way.
4. Verify: deployment READY; `https://351watch-sulmusic2-4637s-projects.vercel.app/data/hits_current.json` shows today's `generated`; `/search?q=battery+storage` lists results (the build log prints `search index: N documents from M rows`).
5. Watch `data/state/town_health.json` for towns with `consecutive_failures` ≥ 3 and `data/state/runs/<date>.json` for errors.

## Test states (Michigan, Virginia)

`data/towns_mi.json` and `data/towns_va.json` are gated (see ARCHITECTURE.md): the daily refresh above never reads them. To re-run the test: `cd crawler && python3 experiments/mi_va_test.py crawl` (writes only `data/test/`), then `analyze`. Do not pass `--states MI,VA` to `ops/daily.sh`; `watch351.daily` refuses gated states without `--output-dir`.

## Full-text search (`/search`)

- Text lives in git: `data/search/<ST>/<YYYY-MM>.jsonl`, one row per document read, first 20,000 characters (contract in `ARCHITECTURE.md`). About 12.5 MB for 3,105 documents; each new document adds about 4 kB, so 100 to 300 new documents a day add 0.4 to 1.2 MB.
- Rows come from the daily engine. `cd crawler && python3 -m watch351.fulltext backfill` re-extracts missing rows from the cache only (no network; `--no-ocr` skips scans whose OCR text is not cached); `daily.sh` runs it after the crawl. `python3 -m watch351.fulltext stats` prints counts and size.
- The index is built at deploy time by `site/vercel-build.sh` (`search/build-index.mjs`, Pagefind 1.5.2 pinned by `search/package-lock.json`, about 15 s) into `/pagefind/` (about 18 MB, 3,200 files). Searches run in the browser and download about 200 to 300 kB on a first search, then about 40 to 140 kB per search; nothing runs on the server.
- Local preview: `(cd search && npm ci) && node search/build-index.mjs data/search site/pagefind` (git-ignored), then `python3 build.py && node site/dev-server.mjs` and open `/search`.
- Changing the rows' shape or `TEXT_CAP`: rows are append-only, so rebuild the folder on a container with a full cache (`rm -r data/search && python3 -m watch351.fulltext backfill`) and commit it in one change.

## Webhook and email delivery

Vercel Cron calls `/api/cron/dispatch` daily at 13:30 UTC (after the refresh) with `CRON_SECRET`. It posts webhooks first (items first seen since each watchlist's last delivery), then sends one email digest to each confirmed address that has new items. The JSON response counts both: `sent`, `failed`, `nothing_new`, `no_webhook`, `email_sent`, `email_failed`, `email_nothing_new`, `email_deferred`, `errors`. To run it by hand: `curl -X POST -H "Authorization: Bearer $CRON_SECRET" https://<host>/api/cron/dispatch`.

- `email_failed` above zero: read the Vercel function logs for "email send failed" (status and Resend's message; addresses are never logged). The cursor did not move, so the items go out on the next run.
- `email_deferred` above zero: the 50-second budget ran out (Resend allows 2 requests a second by default, so about 90 emails a run). Ask Resend for a higher rate limit and lower `EMAIL_SEND_INTERVAL_MS`, or move to Resend's batch endpoint in `site/api/_email.js`.

## Email alerts (Resend)

Email is off until both `RESEND_API_KEY` and `EMAIL_FROM` are set on the Vercel project; `/api/status` then returns `{"ok":true,"email_alerts":true}` and the API accepts the `email` field. Setup, once:

1. Create a Resend account and add the sending domain (in the Resend dashboard, Domains, then Add domain): `agendaahead.com`, or a subdomain such as `mail.agendaahead.com` to keep its sending reputation apart from the main domain. Pick the US region (`us-east-1`).
2. Add the DNS records Resend shows for that domain, exactly as shown. They are an SPF record (a TXT record, and an MX record for bounces, on the `send` subdomain of the sending domain) and a DKIM record (a TXT record at `resend._domainkey`). If the domain's DNS is on Vercel, add them under Domains, agendaahead.com, DNS Records in the Vercel dashboard (or with the Vercel MCP `create_record`). Then press Verify in Resend and wait for "Verified" (minutes to a few hours).
3. Add a DMARC record for the domain: TXT at `_dmarc.agendaahead.com` with `v=DMARC1; p=none; rua=mailto:dmarc@agendaahead.com` (any mailbox you read). Gmail and Yahoo require DMARC from bulk senders. After a few weeks of clean reports, tighten to `p=quarantine`.
4. Create an API key in Resend with "Sending access" for that domain only.
5. On the Vercel project (Production): `RESEND_API_KEY` = the key (sensitive), `EMAIL_FROM` = `Agenda Ahead <alerts@agendaahead.com>` (the address must be on the verified domain), and `PUBLIC_BASE_URL` = `https://agendaahead.com` once the domain serves the site, so links in emails use it. Redeploy.
6. Check: `/api/status` shows `email_alerts: true`; create a test watchlist with your address on `/watch`; open the link in the email and press Confirm; delete the test watchlist from its page.

Limits to watch: Resend's free plan allows 100 emails a day and 3,000 a month (check the current plan); each confirmed address can get one digest a day, and each sign-up sends one confirmation. Resend suppresses addresses that hard-bounce or mark mail as spam; those sends then show up as failures in the logs.

## Environment variables (Vercel project `351watch`)

`BLOB_READ_WRITE_TOKEN` (private store `351watch-submissions`), `ADMIN_TOKEN`, `CRON_SECRET` and `WBA_PRIVATE_KEY` are set. To enable paid plans: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_SITING_DESK`, `STRIPE_PRICE_COUNSEL`, `STRIPE_PRICE_DATACENTER`, `STRIPE_WEBHOOK_SECRET` (webhook endpoint `/api/stripe-webhook`; events `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`) — and move off the Hobby plan first (non-commercial use only).

Email alerts (see above): `RESEND_API_KEY` (sensitive) and `EMAIL_FROM` (`Agenda Ahead <alerts@agendaahead.com>`); both are needed. Optional: `SITE_NAME` (product name in messages, default "Agenda Ahead"), `PUBLIC_BASE_URL` (base of links in emails, feeds and webhooks; default the request's host), `EMAIL_SEND_INTERVAL_MS` (gap between digest sends, default 550), `DISPATCH_EMAIL_BUDGET_MS` (default 50000). Never set `EMAIL_TRANSPORT` on Vercel (it is a local test switch and is ignored there).

The deployment has 10 functions (Hobby allows 12): checkout, contact, email, feed, key-directory, status, stripe-webhook, watchlists, admin/submissions, cron/dispatch.

## Free area data (`data/neighbors.json`)

Which towns touch which, for the free "one town plus its neighbors" watchlist area (contract in `ARCHITECTURE.md`). It changes only when town boundaries do. To rebuild (for example from a newer Census vintage: change `VINTAGE` in the script):

```sh
pip install shapely pyshp
python3 projects/351watch/tools/neighbors.py --check    # downloads 3 zip files (about 1 MB) from www2.census.gov
```

It exits non-zero if a site town has no boundary or a spot check fails (Carver, Boston, Cambridge, Springfield, Worcester, Seekonk, Nantucket, Providence, Westerly, Clifton Park, Kent). When the site adds a NY town whose name another NY place shares, rebuild so the new town gets its site id.

## API tests (local, no network)

`node projects/351watch/tools/test_watch_api.mjs` runs the dev server in-process with the in-memory Blob store, a mock webhook receiver and `EMAIL_TRANSPORT=file`, and checks the free area, grandfathered lists, email opt-in, confirm, digest, unsubscribe, limits, feeds, webhooks and delete. It prints the folder holding the emails it wrote; lint their copy with `python3 .claude/skills/de-slop/scripts/slop_lint.py <folder> --summary`.

Manual run: `EMAIL_TRANSPORT=file EMAIL_FROM=alerts@example.org EMAIL_OUTBOX=/tmp/outbox CRON_SECRET=x node projects/351watch/site/dev-server.mjs`, then use `/watch` and read the emails in `/tmp/outbox`.

## Bot verification (Web Bot Auth)

AgendaAheadBot (formerly 351WatchBot) signs every request (HTTP Message Signatures, Ed25519) so sites behind Cloudflare can verify it. The key directory is served at `https://agendaahead.vercel.app/.well-known/http-message-signatures-directory (switch to agendaahead.com once that domain is live, by setting WBA_SIGNATURE_AGENT)` by `site/api/key-directory.js`, signed with `WBA_PRIVATE_KEY` (Vercel env, sensitive). The crawler signs only when the same value is in its environment as `WBA_PRIVATE_KEY`; otherwise it runs unsigned. Checks, from `crawler/`:

- `python3 -m watch351.botauth check-directory` — the live directory is well formed and its signature verifies.
- `python3 -m watch351.botauth test` — Cloudflare's test endpoint: `401` = well formed but key not registered yet, `200` = registered and verified, `400` = malformed.

Registration (owner, Cloudflare dashboard): Manage Account → Configurations → Bot Submission Form → Verification Method "Request Signature" → key directory URL above, User-Agent `AgendaAheadBot`. Track status under BotBase → Submission history. The bot's public page is `/bot`.

## Crawler rules

Identify as AgendaAheadBot (`AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)`; robots.txt rules for the former name 351WatchBot are also obeyed, Web Bot Auth signature when the key is present); obey robots.txt on every host and redirect; ≤1 request/second/host (2.5 s for `opengov.sos.ri.gov`); no logins; never solve or bypass bot challenges; skip hosts asking for crawl-delay > 10 s (listing pages: > 20 s).
