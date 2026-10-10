// Watchlists: POST creates, GET ?id= reads, PATCH ?id= updates, DELETE ?id= deletes.
// POST ?action=test sends a test message to a webhook (a saved one with ?id=, or webhook_url in the body).
// No accounts: the random id is the credential. Stored as private blobs at watchlists/<id>.json.
import { allow, bodySize, clean, noStore, readBody, removeJSON, throttled } from './_store.js';
import {
  MAX_BODY_BYTES, buildPayload, loadHits, loadTownIndex, loadWatchlist, matchItems, newId, parseWebhook,
  postWebhook, publicBase, publicView, saveWatchlist, topicSet, validId, validateConfig, webhookKind,
} from './_watch.js';

const HOUR = 60 * 60 * 1000;

function fail(res, status, error, fields) {
  return res.status(status).json({ ok: false, error, ...(fields ? { fields } : {}) });
}

async function referenceData(req) {
  const hitsDoc = await loadHits(req);
  return { hitsDoc, towns: await loadTownIndex(req, hitsDoc), topics: topicSet(hitsDoc) };
}

async function create(req, res, body) {
  if (throttled(req, 'create', 20, HOUR)) return fail(res, 429, 'Too many watchlists created from this network. Try again later.');
  const ref = await referenceData(req);
  const { value, errors } = validateConfig(body, ref);
  if (Object.keys(errors).length) return fail(res, 400, Object.values(errors)[0], errors);

  const now = new Date().toISOString();
  const wl = {
    id: newId(),
    version: 1,
    name: value.name,
    towns: value.towns,
    topics: value.topics,
    webhook: value.webhook_url ? { url: value.webhook_url, format: value.webhook_format } : null,
    plan: 'beta',
    billing: null,
    created_at: now,
    updated_at: now,
    // Webhooks only carry items that reach the data after this snapshot (see cron/dispatch.js).
    last_dispatched_at: ref.hitsDoc.generated || now,
    last_delivery: null,
  };
  await saveWatchlist(wl);
  return res.status(201).json({ ok: true, id: wl.id, watchlist: publicView(wl, publicBase(req)) });
}

async function update(req, res, wl, body) {
  const ref = await referenceData(req);
  const { value, errors } = validateConfig(body, ref, { partial: true });
  if (Object.keys(errors).length) return fail(res, 400, Object.values(errors)[0], errors);
  if ('name' in value) wl.name = value.name;
  if (value.towns) wl.towns = value.towns;
  if (value.topics) wl.topics = value.topics;
  if ('webhook_url' in value) {
    wl.webhook = value.webhook_url ? { url: value.webhook_url, format: value.webhook_format || wl.webhook?.format || 'auto' } : null;
    wl.last_delivery = null;
  } else if (value.webhook_format && wl.webhook) {
    wl.webhook.format = value.webhook_format;
  }
  wl.updated_at = new Date().toISOString();
  await saveWatchlist(wl);
  return res.status(200).json({ ok: true, watchlist: publicView(wl, publicBase(req)) });
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
  if (!webhook) return fail(res, 400, 'This watchlist has no webhook.');

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
  const link = saved ? `${base}/w/${saved.id}` : `${base}/watch`;
  const intro = sample.length
    ? `Test message: webhook delivery works. New items will look like ${sample.length === 1 ? 'this one' : 'these'} (already in your watchlist, shown as a sample).`
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

    if (!validId(id)) return fail(res, 404, 'Watchlist not found.');
    const wl = await loadWatchlist(id);
    if (!wl) return fail(res, 404, 'Watchlist not found. It may have been deleted.');

    if (req.method === 'GET') return res.status(200).json({ ok: true, watchlist: publicView(wl, publicBase(req)) });
    if (req.method === 'PATCH') return await update(req, res, wl, body);
    if (req.method === 'DELETE') {
      await removeJSON(`watchlists/${wl.id}.json`);
      return res.status(200).json({ ok: true, deleted: true });
    }
    if (req.method === 'POST' && action === 'test') return await sendTest(req, res, body, wl);
    return fail(res, 400, 'Unknown action.');
  } catch (err) {
    console.error('watchlists failed', err);
    return fail(res, 500, 'Something went wrong. Please try again.');
  }
}
