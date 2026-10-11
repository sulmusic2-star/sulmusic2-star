// Stripe webhook: verifies the Stripe-Signature HMAC over the raw body (STRIPE_WEBHOOK_SECRET)
// and records the plan on the watchlist named in the session/subscription metadata.
// Uses the Web Request/Response signature so the raw body is available for verification.
import { createHmac, timingSafeEqual } from 'node:crypto';
import { loadWatchlist, saveWatchlist, validId } from './_watch.js';

const TOLERANCE_SECONDS = 300;
const ENDED = new Set(['canceled', 'unpaid', 'incomplete_expired']);

const json = (status, data) =>
  new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

export function verifySignature(rawBody, header, secret, now = Math.floor(Date.now() / 1000)) {
  if (!header || !secret) return false;
  const parts = { t: [], v1: [] };
  for (const piece of String(header).split(',')) {
    const [k, v] = piece.trim().split('=');
    if (k in parts && v) parts[k].push(v);
  }
  const t = Number(parts.t[0]);
  const signatures = parts.v1;
  if (!Number.isFinite(t) || !signatures.length || Math.abs(now - t) > TOLERANCE_SECONDS) return false;
  const expected = createHmac('sha256', secret).update(`${t}.${rawBody}`, 'utf8').digest('hex');
  return signatures.some((sig) => sig.length === expected.length && timingSafeEqual(Buffer.from(sig), Buffer.from(expected)));
}

async function setPlan(watchlistId, update) {
  if (!validId(watchlistId)) return false;
  const wl = await loadWatchlist(watchlistId);
  if (!wl) return false;
  Object.assign(wl, update, { updated_at: new Date().toISOString() });
  await saveWatchlist(wl);
  return true;
}

export async function POST(request) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) return json(503, { ok: false, beta: true, error: 'Payments are not enabled.' });

  const raw = await request.text();
  if (raw.length > 512 * 1024) return json(413, { ok: false, error: 'Payload too large' });
  if (!verifySignature(raw, request.headers.get('stripe-signature'), secret)) {
    return json(400, { ok: false, error: 'Invalid signature' });
  }

  let event;
  try {
    event = JSON.parse(raw);
  } catch {
    return json(400, { ok: false, error: 'Invalid JSON' });
  }
  const obj = event?.data?.object || {};
  const meta = obj.metadata || {};

  try {
    if (event.type === 'checkout.session.completed') {
      await setPlan(obj.client_reference_id || meta.watchlist_id, {
        plan: meta.plan || 'paid',
        billing: { status: 'active', customer: obj.customer || null, subscription: obj.subscription || null, event: event.id },
      });
    } else if (event.type === 'customer.subscription.updated' || event.type === 'customer.subscription.deleted') {
      const ended = event.type === 'customer.subscription.deleted' || ENDED.has(obj.status);
      await setPlan(meta.watchlist_id, {
        ...(ended ? { plan: 'beta' } : meta.plan ? { plan: meta.plan } : {}),
        billing: { status: ended ? 'ended' : obj.status, customer: obj.customer || null, subscription: obj.id || null, event: event.id },
      });
    }
  } catch (err) {
    console.error('stripe webhook processing failed', err);
    return json(500, { ok: false });
  }
  return json(200, { received: true });
}
