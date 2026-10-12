// Vercel Cron target (vercel.json "crons"), daily after the data refresh.
// 1. Webhooks: for every watchlist with a webhook, posts the matching items first seen after its
//    last_dispatched_at cursor (at most 20, then an "and N more" line), then advances the cursor
//    to the data snapshot time. A failed delivery leaves the cursor alone so the items are retried.
// 2. Email, after all webhooks: every confirmed address gets one digest of the matching items first
//    seen after its email.last_emailed_at cursor (at most 50, then "and N more"), and only when
//    there is something new. Same cursor rule. Sends are paced for the provider's rate limit; once
//    the time budget is spent, the rest are counted as email_deferred and go out the next day.
import { timingSafeEqual } from 'node:crypto';
import { allow, listPathnames, noStore, readJSON } from '../_store.js';
import { buildPayload, loadHits, matchItems, postWebhook, publicBase, saveWatchlist, shareId, webhookKind } from '../_watch.js';
import { emailEnabled, sendEmail, sendIntervalMs } from '../_email.js';
import { DIGEST_MAX_ITEMS, digestMessage } from '../_email_alerts.js';

const MAX_ITEMS = 20;
const CONCURRENCY = 4;
const EMAIL_CONCURRENCY = 2;
// The function may run 60 s; stop starting email sends after this many ms from the start.
const emailBudgetMs = () => Number(process.env.DISPATCH_EMAIL_BUDGET_MS ?? 50000);

function authorized(req) {
  const expected = process.env.CRON_SECRET || '';
  const header = String(req.headers.authorization || '');
  const given = header.startsWith('Bearer ') ? header.slice(7) : '';
  if (!expected || given.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(given), Buffer.from(expected));
}

const freshItems = (hitsDoc, wl, cursor) => matchItems(hitsDoc.hits, wl).filter((h) => (h.first_seen || '') > cursor);
const snapshotAfter = (hitsDoc, cursor) => (hitsDoc.generated && hitsDoc.generated > cursor ? hitsDoc.generated : cursor);

async function webhookOne(wl, hitsDoc, base) {
  if (!wl.webhook?.url) return 'no_webhook';
  const cursor = wl.last_dispatched_at || wl.created_at || '';
  const fresh = freshItems(hitsDoc, wl, cursor);
  if (!fresh.length) return 'nothing_new';

  const items = fresh.slice(0, MAX_ITEMS);
  const more = fresh.length - items.length;
  const link = `${base}/w/${shareId(wl)}`;
  const result = await postWebhook(wl.webhook.url, buildPayload(webhookKind(wl.webhook), { wl, items, more, link }));
  const at = new Date().toISOString();
  wl.last_delivery = { at, ok: result.ok, status: result.status, sent: items.length, more, ...(result.error ? { error: result.error } : {}) };
  if (result.ok) {
    wl.last_dispatched_at = snapshotAfter(hitsDoc, cursor);
    wl.failures = 0;
  } else {
    wl.failures = (wl.failures || 0) + 1;
  }
  await saveWatchlist(wl);
  return result.ok ? 'sent' : 'failed';
}

const emailCursor = (e) => e.last_emailed_at || e.confirmed_at || '';
const wantsDigest = (wl, hitsDoc) =>
  Boolean(wl?.email?.confirmed && wl.email.address) && freshItems(hitsDoc, wl, emailCursor(wl.email)).length > 0;

async function emailOne(path, hitsDoc, base) {
  // Read again: the address may have been removed or changed since the webhook pass.
  const wl = await readJSON(path);
  if (!wantsDigest(wl, hitsDoc)) return 'email_nothing_new';
  const e = wl.email;
  const cursor = emailCursor(e);
  const fresh = freshItems(hitsDoc, wl, cursor);
  const snapshot = snapshotAfter(hitsDoc, cursor);
  const items = fresh.slice(0, DIGEST_MAX_ITEMS);
  const more = fresh.length - items.length;
  const result = await sendEmail({
    to: e.address,
    ...digestMessage(wl, items, more, base),
    idempotencyKey: `digest/${wl.feed_id || wl.id.slice(0, 8)}/${snapshot}`,
  });
  e.last_email = {
    at: new Date().toISOString(), ok: result.ok, status: result.status, sent: items.length, more,
    ...(result.error ? { error: result.error } : {}),
  };
  if (result.ok) {
    e.last_emailed_at = snapshot;
    e.failures = 0;
  } else {
    e.failures = (e.failures || 0) + 1;
  }
  await saveWatchlist(wl);
  return result.ok ? 'email_sent' : 'email_failed';
}

async function pool(list, size, fn) {
  let next = 0;
  async function worker() {
    while (next < list.length) await fn(list[next++]);
  }
  await Promise.all(Array.from({ length: size }, worker));
}

export default async function handler(req, res) {
  noStore(res);
  if (!allow(req, res, ['GET', 'POST'])) return;
  if (!authorized(req)) return res.status(401).json({ ok: false, error: 'Unauthorized' });

  const started = Date.now();
  try {
    const hitsDoc = await loadHits(req);
    const base = publicBase(req);
    const paths = (await listPathnames('watchlists/')).filter((p) => p.endsWith('.json'));
    const email = emailEnabled();
    const counts = {
      watchlists: paths.length, sent: 0, failed: 0, nothing_new: 0, no_webhook: 0, errors: 0,
      email_alerts: email, email_sent: 0, email_failed: 0, email_nothing_new: 0, email_deferred: 0,
    };

    // 1. webhooks; note which watchlists have a digest due
    const digests = [];
    await pool(paths, CONCURRENCY, async (path) => {
      try {
        const wl = await readJSON(path);
        if (!wl) return;
        counts[await webhookOne(wl, hitsDoc, base)] += 1;
        if (email && wl.email?.confirmed) {
          if (wantsDigest(wl, hitsDoc)) digests.push(path);
          else counts.email_nothing_new += 1;
        }
      } catch (err) {
        counts.errors += 1;
        console.error('dispatch failed for one watchlist', err);
      }
    });

    // 2. email digests, paced
    const interval = sendIntervalMs();
    let nextSlot = 0;
    await pool(digests, EMAIL_CONCURRENCY, async (path) => {
      if (Date.now() - started > emailBudgetMs()) {
        counts.email_deferred += 1;
        return;
      }
      const now = Date.now();
      const wait = Math.max(0, nextSlot - now);
      nextSlot = Math.max(now, nextSlot) + interval;
      if (wait) await new Promise((resolve) => setTimeout(resolve, wait));
      try {
        counts[await emailOne(path, hitsDoc, base)] += 1;
      } catch (err) {
        counts.errors += 1;
        console.error('digest failed for one watchlist', err);
      }
    });

    return res.status(200).json({ ok: true, data_generated: hitsDoc.generated || null, ...counts });
  } catch (err) {
    console.error('dispatch failed', err);
    return res.status(500).json({ ok: false, error: 'Dispatch failed' });
  }
}
