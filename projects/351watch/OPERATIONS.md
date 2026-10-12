# 351 Watch — operations runbook

## Daily refresh (scheduled 6:59 am America/New_York)

1. Repo `sulmusic2-star/sulmusic2-star`, branch `claude/massachusetts-market-service-ead9ho` (`git pull --ff-only` first).
2. `bash projects/351watch/ops/daily.sh` — refreshes MassDEP wetlands filings, crawls MA/NY/RI agendas incrementally (state in `data/state/`), rebuilds the site, commits "Daily refresh YYYY-MM-DD", pushes. Last printed line = commit SHA. A fresh container works: only listing pages are re-read; agenda documents already processed are skipped.
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
4. Verify: deployment READY; `https://351watch-sulmusic2-4637s-projects.vercel.app/data/hits_current.json` shows today's `generated`.
5. Watch `data/state/town_health.json` for towns with `consecutive_failures` ≥ 3 and `data/state/runs/<date>.json` for errors.

## Webhook delivery

Vercel Cron calls `/api/cron/dispatch` daily at 13:30 UTC (after the refresh) with `CRON_SECRET`; it posts items first seen since each watchlist's last delivery.

## Environment variables (Vercel project `351watch`)

`BLOB_READ_WRITE_TOKEN` (private store `351watch-submissions`), `ADMIN_TOKEN`, `CRON_SECRET` and `WBA_PRIVATE_KEY` are set. To enable paid plans: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_SITING_DESK`, `STRIPE_PRICE_COUNSEL`, `STRIPE_PRICE_DATACENTER`, `STRIPE_WEBHOOK_SECRET` (webhook endpoint `/api/stripe-webhook`; events `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`) — and move off the Hobby plan first (non-commercial use only).

## Bot verification (Web Bot Auth)

351WatchBot signs every request (HTTP Message Signatures, Ed25519) so sites behind Cloudflare can verify it. The key directory is served at `https://351watch.vercel.app/.well-known/http-message-signatures-directory` by `site/api/key-directory.js`, signed with `WBA_PRIVATE_KEY` (Vercel env, sensitive). The crawler signs only when the same value is in its environment as `WBA_PRIVATE_KEY`; otherwise it runs unsigned. Checks, from `crawler/`:

- `python3 -m watch351.botauth check-directory` — the live directory is well formed and its signature verifies.
- `python3 -m watch351.botauth test` — Cloudflare's test endpoint: `401` = well formed but key not registered yet, `200` = registered and verified, `400` = malformed.

Registration (owner, Cloudflare dashboard): Manage Account → Configurations → Bot Submission Form → Verification Method "Request Signature" → key directory URL above, User-Agent `351WatchBot`. Track status under BotBase → Submission history. The bot's public page is `/bot`.

## Crawler rules

Identify as 351WatchBot (`351WatchBot/0.1 (+https://351watch.vercel.app/bot)`, Web Bot Auth signature when the key is present); obey robots.txt on every host and redirect; ≤1 request/second/host (2.5 s for `opengov.sos.ri.gov`); no logins; never solve or bypass bot challenges; skip hosts asking for crawl-delay > 10 s.
