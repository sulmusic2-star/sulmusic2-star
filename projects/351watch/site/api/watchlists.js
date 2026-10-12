// Watchlists: POST creates, GET ?id= reads, PATCH ?id= updates, DELETE ?id= deletes.
// POST ?action=test sends a test message to a webhook (a saved one with ?id=, or webhook_url in the body).
// No accounts: the random id is the credential. Stored as private blobs at watchlists/<id>.json.
// Free limit: one area per watchlist, a home_town plus its neighbors (validateConfig in _watch.js).
// Email: an optional `email` field starts double opt-in (_email_alerts.js); confirm, unsubscribe and
// resend live in email.js.
import { allow, bodySize, clean, noStore, readBody, removeJSON, throttled, writeJSON } from './_store.js';
import {
  MAX_BODY_BYTES, buildPayload, ensureFeedId, feedIndexPath, loadHits, loadNeighbors, loadTownIndex, matchItems,
  newId, parseWebhook, postWebhook, publicBase, publicView, readonlyView, resolveWatchlist, saveWatchlist, shareId,
  topicSet, validateConfig, webhookKind,
} from './_watch.js';
import { emailEnabled } from './_email.js';
import {
  EMAIL_OFF_MESSAGE, admitAddress, attachEmail, detachEmail, emailView, maskEmail, parseEmail, sameAddress, saveIndex,
  sendConfirmation,
} from './_email_alerts.js';

const HOUR = 60 * 60 * 1000;

function fail(res, status, error, fields, extra) {
  return res.status(status).json({ ok: false, error, ...(fields ? { fields } : {}), ...(extra || {}) });
}

async function referenceData(req) {
  const hitsDoc = await loadHits(req);
  const [towns, neighbors] = await Promise.all([loadTownIndex(req, hitsDoc), loadNeighbors(req)]);
  return { hitsDoc, towns, topics: topicSet(hitsDoc), neighbors };
}

function invalid(res, errors, code) {
  if (code === 'area_unavailable') {
    return fail(res, 503, 'The town data is unavailable right now. Try again in a few minutes.', null, { code });
  }
  return fail(res, 400, Object.values(errors)[0], errors, code ? { code } : null);
}

// The optional `email` field: { present, address } or { present, error }. On an update, the stored
// address in any case, or its masked form echoed back by a form, means "unchanged".
function readEmailField(body, current = null) {
  if (!('email' in body)) return { present: false };
  const raw = typeof body.email === 'string' ? body.email.trim() : body.email;
  const stored = current?.email?.address;
  if (stored && (raw === maskEmail(stored) || sameAddress(raw, stored))) return { present: true, unchanged: true };
  const parsed = parseEmail(raw);
  if (parsed.error) return { present: true, error: parsed.error };
  if (parsed.address && !emailEnabled()) return { present: true, error: EMAIL_OFF_MESSAGE };
  return { present: true, address: parsed.address };
}

// Per-network and per-address limits on confirmation emails, then the 3-watchlists-per-address cap.
async function admit(req, res, address, watchlistId) {
  if (throttled(req, 'email', 10, HOUR)) {
    const error = 'Too many email sign-ups from this network. Try again in an hour.';
    fail(res, 429, error, { email: error });
    return null;
  }
  const admitted = await admitAddress(address, watchlistId);
  if (admitted.error) {
    fail(res, admitted.status, admitted.error, { email: admitted.error });
    return null;
  }
  return admitted.idx;
}

const view = (wl, req) => publicView(wl, publicBase(req), { email: emailView(wl) });

async function create(req, res, body) {
  if (throttled(req, 'create', 20, HOUR)) return fail(res, 429, 'Too many alert sign-ups from this network. Try again later.');
  const ref = await referenceData(req);
  const { value, errors, code } = validateConfig(body, ref);
  const email = readEmailField(body);
  if (email.error) errors.email = email.error;
  if (Object.keys(errors).length || code) return invalid(res, errors, code);

  const now = new Date().toISOString();
  const wl = {
    id: newId(),
    feed_id: newId(),
    version: 1,
    name: value.name,
    home_town: value.home_town,
    towns: value.towns,
    topics: value.topics,
    webhook: value.webhook_url ? { url: value.webhook_url, format: value.webhook_format } : null,
    email: null,
    plan: 'beta',
    billing: null,
    created_at: now,
    updated_at: now,
    // Webhooks only carry items that reach the data after this snapshot (see cron/dispatch.js).
    last_dispatched_at: ref.hitsDoc.generated || now,
    last_delivery: null,
  };

  let idx = null;
  if (email.address) {
    idx = await admit(req, res, email.address, wl.id);
    if (!idx) return;
    attachEmail(wl, email.address, ref.hitsDoc.generated || now);
  }
  await saveWatchlist(wl);
  await writeJSON(feedIndexPath(wl.feed_id), { watchlist_id: wl.id });
  if (idx) {
    // Sent after the save so the confirmation link works as soon as it arrives.
    await sendConfirmation(wl, idx, publicBase(req));
    await saveWatchlist(wl);
    await saveIndex(email.address, idx);
  }
  return res.status(201).json({ ok: true, id: wl.id, watchlist: view(wl, req) });
}

async function update(req, res, wl, body) {
  const ref = await referenceData(req);
  const { value, errors, code } = validateConfig(body, ref, { partial: true, current: wl });
  const email = readEmailField(body, wl);
  if (email.error) errors.email = email.error;
  if (Object.keys(errors).length || code) return invalid(res, errors, code);

  // Email: empty removes the address, the same address changes nothing, a new one starts over.
  let emailChange = null;
  if (email.present && !email.unchanged) emailChange = email.address ? 'new' : wl.email ? 'remove' : null;
  let idx = null;
  if (emailChange === 'new') {
    idx = await admit(req, res, email.address, wl.id);
    if (!idx) return;
  }

  if ('name' in value) wl.name = value.name;
  if (value.home_town) wl.home_town = value.home_town;
  if (value.towns) wl.towns = value.towns;
  if (value.topics) wl.topics = value.topics;
  if ('webhook_url' in value) {
    wl.webhook = value.webhook_url ? { url: value.webhook_url, format: value.webhook_format || wl.webhook?.format || 'auto' } : null;
    wl.last_delivery = null;
  } else if (value.webhook_format && wl.webhook) {
    wl.webhook.format = value.webhook_format;
  }
  if (emailChange) await detachEmail(wl);
  if (emailChange === 'new') {
    await ensureFeedId(wl); // tokens carry the read-only key
    attachEmail(wl, email.address, ref.hitsDoc.generated);
  }
  wl.updated_at = new Date().toISOString();
  await saveWatchlist(wl);
  if (emailChange === 'new') {
    await sendConfirmation(wl, idx, publicBase(req));
    await saveWatchlist(wl);
    await saveIndex(email.address, idx);
  }
  return res.status(200).json({ ok: true, watchlist: view(wl, req) });
}

async function sendTest(req, res, body, saved) {
  if (throttled(req, 'test', 10, HOUR)) return fail(res, 429, 'Too many test messages. Try again later.');
  let webhook = saved?.webhook || null;
  if (!saved) {
    const parsed = parseWebhook(body.webhook_url);
    if (parsed.error) return fail(res, 400, parsed.error, { webhook_url: parsed.error });
    if (!parsed.url) return fail(res, 400, 'Enter a webhook URL first.', { webhook_url: 'Enter a webhook URL first.' });
    webhook = { url: parsed.url, format: body.webhook_format === 'json' ? 'json' : 'auto' };
  }
  if (!webhook) return fail(res, 400, 'These alerts have no webhook.');

  const base = publicBase(req);
  const wl = saved || { id: 'test', name: clean(body.name, 80), towns: [], topics: [] };
  if (!saved && Array.isArray(body.towns) && Array.isArray(body.topics)) {
    wl.towns = body.towns.slice(0, 200).map((t) => clean(t, 80));
    wl.topics = body.topics.slice(0, 20).map((t) => clean(t, 60));
  }
  let sample = [];
  try {
    sample = matchItems((await loadHits(req)).hits, wl).slice(0, 2);
  } catch {
    sample = [];
  }
  const link = saved ? `${base}/w/${shareId(saved)}` : `${base}/watch`;
  const intro = sample.length
    ? `Test message: webhook delivery works. New items will look like ${sample.length === 1 ? 'this one' : 'these'} (already on your alerts page, shown as a sample).`
    : 'Test message: webhook delivery works. New agenda items for your towns and topics will arrive here once a day.';
  const payload = buildPayload(webhookKind(webhook), { wl, items: sample, link, intro, test: true });
  const result = await postWebhook(webhook.url, payload);
  if (!result.ok) {
    return fail(res, 502, `The webhook did not accept the test message (${result.error || `HTTP ${result.status}`}). Check the URL.`);
  }
  return res.status(200).json({ ok: true, status: result.status });
}

export default async function handler(req, res) {
  noStore(res);
  if (!allow(req, res, ['GET', 'POST', 'PATCH', 'DELETE'])) return;
  const id = typeof req.query?.id === 'string' ? req.query.id : '';
  const action = typeof req.query?.action === 'string' ? req.query.action : '';

  if (req.method !== 'GET' && req.method !== 'DELETE') {
    if (bodySize(req) > MAX_BODY_BYTES) return fail(res, 413, 'Request too large.');
  }
  const body = readBody(req);
  // Honeypot: real people never see or fill this field.
  if (req.method === 'POST' && clean(body.website, 200)) return res.status(200).json({ ok: true, id: null });

  try {
    if (req.method === 'POST' && !id && action !== 'test') return await create(req, res, body);
    if (req.method === 'POST' && action === 'test' && !id) return await sendTest(req, res, body, null);

    const { wl, readonly } = await resolveWatchlist(id);
    if (!wl) return fail(res, 404, 'These alerts were not found. They may have been deleted.');

    if (req.method === 'GET') {
      if (readonly) return res.status(200).json({ ok: true, watchlist: readonlyView(wl, publicBase(req)) });
      await ensureFeedId(wl); // watchlists made before read-only links existed get one now
      return res.status(200).json({ ok: true, watchlist: view(wl, req) });
    }
    if (readonly) return fail(res, 403, 'This is a read-only link. Use the private link to change these alerts.');
    if (req.method === 'PATCH') return await update(req, res, wl, body);
    if (req.method === 'DELETE') {
      await removeJSON(`watchlists/${wl.id}.json`);
      if (wl.feed_id) await removeJSON(feedIndexPath(wl.feed_id));
      if (wl.email) await detachEmail(wl);
      return res.status(200).json({ ok: true, deleted: true });
    }
    if (req.method === 'POST' && action === 'test') return await sendTest(req, res, body, wl);
    return fail(res, 400, 'Unknown action.');
  } catch (err) {
    console.error('watchlists failed', err);
    return fail(res, 500, 'Something went wrong. Please try again.');
  }
}
