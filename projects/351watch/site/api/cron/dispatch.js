// Vercel Cron target (vercel.json "crons"), daily after the data refresh.
// For every watchlist with a webhook, posts the matching items first seen after its
// last_dispatched_at cursor (at most 20, then an "and N more" line), then advances the cursor
// to the data snapshot time. A failed delivery leaves the cursor alone so the items are retried.
import { timingSafeEqual } from 'node:crypto';
import { allow, listPathnames, noStore, readJSON } from '../_store.js';
import { buildPayload, loadHits, matchItems, postWebhook, publicBase, saveWatchlist, shareId, webhookKind } from '../_watch.js';

const MAX_ITEMS = 20;
const CONCURRENCY = 4;

function authorized(req) {
  const expected = process.env.CRON_SECRET || '';
  const header = String(req.headers.authorization || '');
  const given = header.startsWith('Bearer ') ? header.slice(7) : '';
  if (!expected || given.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(given), Buffer.from(expected));
}

async function dispatchOne(path, hitsDoc, base) {
  const wl = await readJSON(path);
  if (!wl || !wl.webhook?.url) return 'no_webhook';
  const cursor = wl.last_dispatched_at || wl.created_at || '';
  const fresh = matchItems(hitsDoc.hits, wl).filter((h) => (h.first_seen || '') > cursor);
  const snapshot = hitsDoc.generated && hitsDoc.generated > cursor ? hitsDoc.generated : cursor;
  if (!fresh.length) return 'nothing_new';

  const items = fresh.slice(0, MAX_ITEMS);
  const more = fresh.length - items.length;
  const link = `${base}/w/${shareId(wl)}`;
  const result = await postWebhook(wl.webhook.url, buildPayload(webhookKind(wl.webhook), { wl, items, more, link }));
  const at = new Date().toISOString();
  wl.last_delivery = { at, ok: result.ok, status: result.status, sent: items.length, more, ...(result.error ? { error: result.error } : {}) };
  if (result.ok) {
    wl.last_dispatched_at = snapshot;
    wl.failures = 0;
  } else {
    wl.failures = (wl.failures || 0) + 1;
  }
  await saveWatchlist(wl);
  return result.ok ? 'sent' : 'failed';
}

export default async function handler(req, res) {
  noStore(res);
  if (!allow(req, res, ['GET', 'POST'])) return;
  if (!authorized(req)) return res.status(401).json({ ok: false, error: 'Unauthorized' });

  try {
    const hitsDoc = await loadHits(req);
    const base = publicBase(req);
    const paths = (await listPathnames('watchlists/')).filter((p) => p.endsWith('.json'));
    const counts = { watchlists: paths.length, sent: 0, failed: 0, nothing_new: 0, no_webhook: 0, errors: 0 };

    let next = 0;
    async function worker() {
      while (next < paths.length) {
        const path = paths[next++];
        try {
          counts[await dispatchOne(path, hitsDoc, base)] += 1;
        } catch (err) {
          counts.errors += 1;
          console.error('dispatch failed for one watchlist', err);
        }
      }
    }
    await Promise.all(Array.from({ length: CONCURRENCY }, worker));
    return res.status(200).json({ ok: true, data_generated: hitsDoc.generated || null, ...counts });
  } catch (err) {
    console.error('dispatch failed', err);
    return res.status(500).json({ ok: false, error: 'Dispatch failed' });
  }
}
