// Stripe Checkout for paid plans. Disabled (503 {beta: true}) unless STRIPE_SECRET_KEY and the
// plan's price id (STRIPE_PRICE_TOWN / STRIPE_PRICE_STATEWIDE) are set. Calls Stripe's REST API directly.
// GET  -> { enabled, plans }            (the pricing page uses this to activate its buttons)
// POST { plan, watchlist_id } -> { url } (redirect the browser to Stripe)
import { allow, bodySize, clean, noStore, readBody, throttled } from './_store.js';
import { loadWatchlist, publicBase, validId } from './_watch.js';

export const PLANS = {
  town: { name: 'Town pack', price_env: 'STRIPE_PRICE_TOWN', monthly_usd: 79 },
  statewide: { name: 'Statewide', price_env: 'STRIPE_PRICE_STATEWIDE', monthly_usd: 299 },
};

const configured = (plan) => Boolean(process.env.STRIPE_SECRET_KEY && process.env[PLANS[plan].price_env]);

export default async function handler(req, res) {
  noStore(res);
  if (!allow(req, res, ['GET', 'POST'])) return;

  if (req.method === 'GET') {
    const plans = Object.fromEntries(Object.keys(PLANS).map((k) => [k, { name: PLANS[k].name, monthly_usd: PLANS[k].monthly_usd, enabled: configured(k) }]));
    return res.status(200).json({ ok: true, enabled: Object.values(plans).some((p) => p.enabled), plans });
  }

  if (bodySize(req) > 4096) return res.status(413).json({ ok: false, error: 'Request too large.' });
  const body = readBody(req);
  const plan = clean(body.plan, 20);
  if (!PLANS[plan]) return res.status(400).json({ ok: false, error: 'Unknown plan.' });
  if (!configured(plan)) {
    return res.status(503).json({ ok: false, beta: true, error: 'Paid plans are not open yet. Everything is free during the founding beta.' });
  }
  if (throttled(req, 'checkout', 20, 60 * 60 * 1000)) return res.status(429).json({ ok: false, error: 'Too many attempts. Try again later.' });

  const id = clean(body.watchlist_id, 64);
  const wl = validId(id) ? await loadWatchlist(id) : null;
  if (!wl) return res.status(400).json({ ok: false, error: 'Create a watchlist first, then upgrade it from its page.' });

  const base = publicBase(req);
  const form = new URLSearchParams({
    mode: 'subscription',
    'line_items[0][price]': process.env[PLANS[plan].price_env],
    'line_items[0][quantity]': '1',
    success_url: `${base}/w/${wl.id}?checkout=success`,
    cancel_url: `${base}/pricing?id=${wl.id}&checkout=cancelled`,
    client_reference_id: wl.id,
    'metadata[watchlist_id]': wl.id,
    'metadata[plan]': plan,
    'subscription_data[metadata][watchlist_id]': wl.id,
    'subscription_data[metadata][plan]': plan,
    allow_promotion_codes: 'true',
  });

  try {
    const stripe = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        authorization: `Bearer ${process.env.STRIPE_SECRET_KEY}`,
        'content-type': 'application/x-www-form-urlencoded',
        'idempotency-key': `${wl.id}-${plan}-${Math.floor(Date.now() / 60000)}`,
      },
      body: form,
      signal: AbortSignal.timeout(10000),
    });
    const session = await stripe.json().catch(() => ({}));
    if (!stripe.ok || !session.url) {
      console.error('stripe checkout error', stripe.status, session?.error?.message);
      return res.status(502).json({ ok: false, error: 'Checkout is unavailable right now. Please try again later.' });
    }
    return res.status(200).json({ ok: true, url: session.url });
  } catch (err) {
    console.error('stripe checkout failed', err);
    return res.status(502).json({ ok: false, error: 'Checkout is unavailable right now. Please try again later.' });
  }
}
