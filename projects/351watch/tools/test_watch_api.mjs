#!/usr/bin/env node
// End-to-end checks for the watchlist API: the free area, email alerts (opt-in, confirm, digest,
// unsubscribe, limits), feeds, webhooks and delete. Runs the local dev server in this process with
// its in-memory Blob store, so tests can seed and inspect blobs. No network: email goes to a temp
// outbox (EMAIL_TRANSPORT=file) and webhook posts to a mock server.
//
//   node projects/351watch/tools/test_watch_api.mjs        (prints the outbox folder at the end)
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
import { mkdtemp, readFile, readdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const tmp = await mkdtemp(join(tmpdir(), '351watch-test-'));
const OUTBOX = join(tmp, 'outbox');
const HITS = join(tmp, 'hits.json');
const hitsDoc = JSON.parse(await readFile(join(ROOT, 'data/hits_current.json'), 'utf8'));
const NEIGHBORS = JSON.parse(await readFile(join(ROOT, 'data/neighbors.json'), 'utf8'));
await writeFile(HITS, JSON.stringify(hitsDoc));

const hooks = [];
const mock = createServer((req, res) => {
  let raw = '';
  req.on('data', (c) => { raw += c; });
  req.on('end', () => {
    hooks.push({ url: req.headers['x-original-url'], headers: req.headers, body: JSON.parse(raw || '{}') });
    const resend = String(req.headers['x-original-url']).startsWith('https://api.resend.com/');
    res.writeHead(200, { 'content-type': resend ? 'application/json' : 'text/plain' });
    res.end(resend ? JSON.stringify({ id: `mock-${hooks.length}` }) : 'ok');
  });
});
await new Promise((resolve) => mock.listen(0, '127.0.0.1', resolve));

const PORT = 18000 + Math.floor(Math.random() * 2000);
for (const k of ['BLOB_READ_WRITE_TOKEN', 'RESEND_API_KEY', 'VERCEL', 'SITE_NAME', 'PUBLIC_BASE_URL', 'DATA_ORIGIN']) delete process.env[k];
Object.assign(process.env, {
  PORT: String(PORT),
  HITS_FILE: HITS,
  EMAIL_TRANSPORT: 'file',
  EMAIL_FROM: 'alerts@example.org',
  EMAIL_OUTBOX: OUTBOX,
  CRON_SECRET: 'test-secret',
  MOCK_WEBHOOK_URL: `http://127.0.0.1:${mock.address().port}/hook`,
});
await import(pathToFileURL(join(ROOT, 'site/dev-server.mjs')).href);
const store = globalThis.__351watchBlobShim;
const W = await import(pathToFileURL(join(ROOT, 'site/api/_watch.js')).href);
const EA = await import(pathToFileURL(join(ROOT, 'site/api/_email_alerts.js')).href);
const ORIGIN = `http://127.0.0.1:${PORT}`;

// ---------- helpers ----------
let ipCount = 0;
const newIp = () => { ipCount += 1; return `10.1.${Math.floor(ipCount / 250)}.${(ipCount % 250) + 1}`; };
async function api(method, path, { body, ip = newIp(), headers = {} } = {}) {
  const res = await fetch(ORIGIN + path, {
    method,
    redirect: 'manual',
    headers: { 'content-type': 'application/json', 'x-forwarded-for': ip, ...headers },
    body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body),
  });
  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch { json = null; }
  return { status: res.status, json, text, headers: res.headers };
}
for (let i = 0; i < 50; i += 1) {
  try { if ((await fetch(`${ORIGIN}/api/status`)).ok) break; } catch { /* not listening yet */ }
  await new Promise((resolve) => setTimeout(resolve, 100));
}
const getBlob = async (path) => {
  const r = await store.get(path);
  return r ? JSON.parse(await new Response(r.stream).text()) : null;
};
const putBlob = (path, data) => store.put(path, JSON.stringify(data), { allowOverwrite: true, contentType: 'application/json' });
async function outbox() {
  let files = [];
  try { files = (await readdir(OUTBOX)).filter((f) => f.endsWith('.json')).sort(); } catch { return []; }
  return Promise.all(files.map(async (f) => JSON.parse(await readFile(join(OUTBOX, f), 'utf8'))));
}
const mailTo = async (address) => (await outbox()).filter((m) => m.to[0].toLowerCase() === address.toLowerCase());
const indexOf = (address) => getBlob(`emails/${createHash('sha256').update(address.toLowerCase()).digest('hex')}.json`);
const PAGES = [];
const keepPage = (r) => { PAGES.push(r.text); return r; };
const linkIn = (text, action) => new URL(text.match(new RegExp(`https?://\\S+/api/email\\?action=${action}&t=\\S+`))[0]);
const cron = () => api('POST', '/api/cron/dispatch', { headers: { authorization: 'Bearer test-secret' } });
const TOPICS = Object.keys(W.TOPICS);
const area = (home) => [home, ...NEIGHBORS[home]];
const make = (extra) => api('POST', '/api/watchlists', { body: { topics: TOPICS, ...extra } });

let passed = 0;
let failed = 0;
async function test(name, fn) {
  try {
    await fn();
    passed += 1;
    console.log(`ok   ${name}`);
  } catch (err) {
    failed += 1;
    console.log(`FAIL ${name}\n     ${err.stack.split('\n').slice(0, 3).join('\n     ')}`);
  }
}

// ---------- /api/status ----------
await test('GET /api/status: email_alerts true when configured', async () => {
  const r = await api('GET', '/api/status');
  assert.equal(r.status, 200);
  assert.deepEqual(r.json, { ok: true, email_alerts: true });
});

await test('email off: status false, email field rejected, empty email accepted', async () => {
  const saved = process.env.EMAIL_TRANSPORT;
  delete process.env.EMAIL_TRANSPORT; // EMAIL_FROM set, no RESEND_API_KEY
  try {
    assert.equal((await api('GET', '/api/status')).json.email_alerts, false);
    const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: 'someone@example.com' });
    assert.equal(r.status, 400);
    assert.match(r.json.fields.email, /not set up/);
    const ok = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: '' });
    assert.equal(ok.status, 201);
    assert.equal(ok.json.watchlist.email.configured, false);
    assert.equal(ok.json.watchlist.email.available, false);
    process.env.RESEND_API_KEY = 're_test_key';
    assert.equal((await api('GET', '/api/status')).json.email_alerts, true);
    process.env.EMAIL_FROM = '';
    assert.equal((await api('GET', '/api/status')).json.email_alerts, false);
  } finally {
    process.env.EMAIL_TRANSPORT = saved;
    process.env.EMAIL_FROM = 'alerts@example.org';
    delete process.env.RESEND_API_KEY;
  }
});

await test('Resend provider: request shape (to the mock server)', async () => {
  const saved = process.env.EMAIL_TRANSPORT;
  delete process.env.EMAIL_TRANSPORT;
  process.env.RESEND_API_KEY = 're_test_key';
  process.env.EMAIL_FROM = 'Agenda Ahead <alerts@agendaahead.com>';
  try {
    const before = hooks.length;
    const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: 'via.resend@example.org' });
    assert.equal(r.status, 201, r.text);
    assert.equal(r.json.watchlist.email.confirmation_sent, true);
    assert.equal(hooks.length, before + 1);
    const call = hooks.at(-1);
    assert.equal(call.url, 'https://api.resend.com/emails');
    assert.equal(call.headers.authorization, 'Bearer re_test_key');
    assert.equal(call.body.from, 'Agenda Ahead <alerts@agendaahead.com>');
    assert.deepEqual(call.body.to, ['via.resend@example.org']);
    assert.ok(call.body.subject && call.body.text && call.body.html);
    assert.equal(call.body.headers['List-Unsubscribe-Post'], 'List-Unsubscribe=One-Click');
  } finally {
    process.env.EMAIL_TRANSPORT = saved;
    process.env.EMAIL_FROM = 'alerts@example.org';
    delete process.env.RESEND_API_KEY;
  }
});

// ---------- the free area ----------
let carver; // { id, feed } of a Carver-area list without email
await test('create inside the free area (home town plus neighbors) passes', async () => {
  const r = await make({ name: 'Carver area', home_town: 'MA:Carver', towns: area('MA:Carver') });
  assert.equal(r.status, 201, r.text);
  assert.equal(r.json.watchlist.home_town, 'MA:Carver');
  assert.equal(r.json.watchlist.grandfathered, false);
  assert.deepEqual(r.json.watchlist.email, { configured: false, available: true, confirmed: false, masked: null });
  carver = { id: r.json.id, feed: new URL(r.json.watchlist.links.share).pathname.split('/').pop() };
});

await test('create outside the free area fails with fields.towns and the plain message', async () => {
  const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver', 'MA:Boston'] });
  assert.equal(r.status, 400);
  assert.equal(r.json.code, 'free_area');
  assert.equal(r.json.fields.towns, W.FREE_AREA_MESSAGE);
  assert.equal(r.json.error, 'Free alerts cover one town and the towns next to it. Need more places? Tell us at /privacy#contact.');
  const halifax = await make({ home_town: 'MA:Carver', towns: ['MA:Carver', 'MA:Halifax'] });
  assert.equal(halifax.status, 400, 'Halifax does not touch Carver');
});

await test('create needs a known home_town', async () => {
  const none = await make({ towns: ['MA:Carver'] });
  assert.equal(none.status, 400);
  assert.equal(none.json.fields.home_town, 'Choose your town.');
  const bad = await make({ home_town: 'MA:Atlantis', towns: ['MA:Carver'] });
  assert.equal(bad.status, 400);
  assert.match(bad.json.fields.home_town, /Unknown town/);
});

await test('free area crosses state lines and allows neighbors without the home town', async () => {
  const r = await make({ home_town: 'MA:Seekonk', towns: ['MA:Seekonk', 'RI:East Providence', 'RI:Pawtucket'] });
  assert.equal(r.status, 201, r.text);
  const only = await make({ home_town: 'MA:Carver', towns: ['MA:Plymouth'] });
  assert.equal(only.status, 201, only.text);
});

await test('update: add a neighbor passes, add a far town fails, read-only key cannot edit', async () => {
  const small = await make({ home_town: 'MA:Carver', towns: ['MA:Carver', 'MA:Plymouth'] });
  const id = small.json.id;
  const add = await api('PATCH', `/api/watchlists?id=${id}`, { body: { towns: ['MA:Carver', 'MA:Plymouth', 'MA:Wareham'] } });
  assert.equal(add.status, 200, add.text);
  const far = await api('PATCH', `/api/watchlists?id=${id}`, { body: { towns: ['MA:Carver', 'MA:Boston'] } });
  assert.equal(far.status, 400);
  assert.equal(far.json.fields.towns, W.FREE_AREA_MESSAGE);
  const feed = new URL(small.json.watchlist.links.share).pathname.split('/').pop();
  const ro = await api('PATCH', `/api/watchlists?id=${feed}`, { body: { name: 'x' } });
  assert.equal(ro.status, 403);
});

await test('update: a new home town must hold the whole list', async () => {
  const outsideCarver = NEIGHBORS['MA:Plymouth'].find((t) => !area('MA:Carver').includes(t));
  const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver', 'MA:Plymouth'] });
  const id = r.json.id;
  const move = await api('PATCH', `/api/watchlists?id=${id}`, { body: { home_town: 'MA:Plymouth', towns: ['MA:Plymouth', outsideCarver] } });
  assert.equal(move.status, 200, move.text);
  assert.equal(move.json.watchlist.home_town, 'MA:Plymouth');
  const hop = await api('PATCH', `/api/watchlists?id=${id}`, { body: { home_town: 'MA:Boston' } });
  assert.equal(hop.status, 400, 'old towns must fit the new area');
  assert.equal(hop.json.code, 'free_area');
});

await test('validateConfig: kept towns survive neighbor-data changes; MAX_TOWNS kept; missing data', async () => {
  const ref = { towns: new Set(Object.keys(NEIGHBORS).filter((k) => !k.startsWith('_'))), topics: new Set(TOPICS), neighbors: NEIGHBORS };
  const current = { home_town: 'MA:Carver', towns: ['MA:Carver', 'MA:Halifax'], topics: ['solar'] };
  assert.deepEqual(W.validateConfig({ towns: ['MA:Carver', 'MA:Halifax'] }, ref, { partial: true, current }).errors, {});
  assert.equal(W.validateConfig({ towns: ['MA:Carver', 'MA:Halifax', 'MA:Boston'] }, ref, { partial: true, current }).code, 'free_area');
  const many = [...ref.towns].slice(0, W.MAX_TOWNS + 1);
  assert.match(W.validateConfig({ home_town: 'MA:Carver', towns: many, topics: ['solar'] }, ref).errors.towns, /up to 200/);
  const noData = { ...ref, neighbors: null };
  assert.equal(W.validateConfig({ home_town: 'MA:Carver', towns: ['MA:Carver'], topics: ['solar'] }, noData).code, 'area_unavailable');
  assert.equal(W.validateConfig({ towns: ['MA:Carver'] }, noData, { partial: true, current }).code, null);
});

// ---------- grandfathered lists ----------
async function seedOld(towns) {
  const wl = {
    id: W.newId(), feed_id: W.newId(), version: 1, name: 'Old list', towns, topics: ['solar', 'battery_storage'],
    webhook: null, plan: 'beta', billing: null, created_at: '2026-10-01T00:00:00+00:00', updated_at: '2026-10-01T00:00:00+00:00',
    last_dispatched_at: '2026-10-01T00:00:00+00:00', last_delivery: null,
  };
  await putBlob(`watchlists/${wl.id}.json`, wl);
  await putBlob(`feeds/${wl.feed_id}.json`, { watchlist_id: wl.id });
  return wl;
}

await test('grandfathered list: keeps working, can drop towns, cannot add outside one area', async () => {
  const old = await seedOld(['MA:Boston', 'MA:Carver', 'MA:Amherst', 'NY:Southold']);
  const get = await api('GET', `/api/watchlists?id=${old.id}`);
  assert.equal(get.status, 200);
  assert.equal(get.json.watchlist.home_town, null);
  assert.equal(get.json.watchlist.grandfathered, true);
  assert.equal((await api('GET', `/api/feed?id=${old.feed_id}&format=json`)).status, 200);
  assert.equal((await api('PATCH', `/api/watchlists?id=${old.id}`, { body: { topics: ['solar'] } })).status, 200);
  const drop = await api('PATCH', `/api/watchlists?id=${old.id}`, { body: { towns: ['MA:Boston', 'MA:Carver', 'NY:Southold'] } });
  assert.equal(drop.status, 200, drop.text);
  assert.equal(drop.json.watchlist.grandfathered, true);
  const add = await api('PATCH', `/api/watchlists?id=${old.id}`, { body: { towns: ['MA:Boston', 'MA:Carver', 'NY:Southold', 'MA:Worcester'] } });
  assert.equal(add.status, 400);
  assert.equal(add.json.code, 'free_area');
  const pick = await api('PATCH', `/api/watchlists?id=${old.id}`, { body: { home_town: 'MA:Carver' } });
  assert.equal(pick.status, 400, 'a home town must hold the whole old list');
  const fit = await api('PATCH', `/api/watchlists?id=${old.id}`, { body: { towns: ['MA:Boston', 'MA:Cambridge'] } });
  assert.equal(fit.status, 200, fit.text);
  assert.equal(fit.json.watchlist.home_town, 'MA:Boston', 'home town inferred from the list');
  assert.equal(fit.json.watchlist.grandfathered, false);
});

// ---------- webhooks (regression) ----------
let hooked;
await test('webhook test message still posts', async () => {
  const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], webhook_url: 'https://hooks.slack.com/services/T000/B000/XXXXXXXX' });
  assert.equal(r.status, 201, r.text);
  hooked = r.json.id;
  assert.equal(r.json.watchlist.webhook.kind, 'slack');
  const before = hooks.length;
  const t = await api('POST', `/api/watchlists?id=${hooked}&action=test`, { body: {} });
  assert.equal(t.status, 200, t.text);
  assert.equal(hooks.length, before + 1);
  assert.match(hooks.at(-1).url, /^https:\/\/hooks\.slack\.com\//);
  assert.match(hooks.at(-1).body.blocks[0].text.text, /^Agenda Ahead: /);
});

// ---------- email opt-in ----------
const A = 'Jane.Doe@Example.COM';
const A_STORED = 'Jane.Doe@example.com';
let listA;
await test('create with email: pending, masked, one confirmation email, index entry', async () => {
  const r = await make({ name: 'Carver email', home_town: 'MA:Carver', towns: area('MA:Carver'), topics: ['solar', 'battery_storage', 'zoning_amendment'], email: A });
  assert.equal(r.status, 201, r.text);
  const e = r.json.watchlist.email;
  assert.equal(e.configured, true);
  assert.equal(e.confirmed, false);
  assert.equal(e.masked, 'J***@example.com');
  assert.equal(e.status, 'pending');
  assert.equal(e.confirmation_sent, true);
  assert.ok(Date.parse(e.resend_available_at) > Date.now() + 23 * 3600e3);
  assert.ok(!r.text.includes('Jane.Doe@'), 'private view shows only the masked address');
  listA = { id: r.json.id, feed: new URL(r.json.watchlist.links.share).pathname.split('/').pop() };
  const mail = await mailTo(A_STORED);
  assert.equal(mail.length, 1);
  assert.equal(mail[0].from, 'Agenda Ahead <alerts@example.org>');
  assert.equal(mail[0].subject, 'Agenda Ahead: confirm daily emails for Carver email');
  assert.match(mail[0].text, /\/api\/email\?action=confirm&t=/);
  assert.match(mail[0].headers['List-Unsubscribe'], /^<http.*action=unsubscribe&t=.*>$/);
  assert.equal(mail[0].headers['List-Unsubscribe-Post'], 'List-Unsubscribe=One-Click');
  const idx = await indexOf(A);
  assert.deepEqual(Object.keys(idx.watchlists), [listA.id]);
  assert.equal(idx.watchlists[listA.id].confirmed, false);
  assert.equal(idx.sends.length, 1);
  assert.ok(!JSON.stringify(idx).includes('Jane'), 'the index holds no address');
});

await test('read-only key and feeds show nothing about email', async () => {
  const ro = await api('GET', `/api/watchlists?id=${listA.feed}`);
  assert.equal(ro.status, 200);
  assert.equal(ro.json.watchlist.readonly, true);
  assert.equal('email' in ro.json.watchlist, false);
  for (const text of [
    ro.text,
    (await api('GET', `/api/feed?id=${listA.feed}&format=json`)).text,
    (await api('GET', `/api/feed?id=${listA.feed}&format=rss`)).text,
    (await api('GET', `/api/feed?id=${listA.feed}&format=ics`)).text,
    (await api('GET', `/api/feed?id=${listA.id}&format=json`)).text,
  ]) {
    assert.ok(!/jane|J\*\*\*|example\.com/i.test(text), 'no address, masked or not');
  }
});

await test('confirmation link confirms and redirects to the private page; bad token fails', async () => {
  const [mail] = await mailTo(A_STORED);
  const link = linkIn(mail.text, 'confirm');
  const bad = keepPage(await api('GET', `${link.pathname}${link.search.slice(0, -2)}xx`));
  assert.equal(bad.status, 404);
  assert.match(bad.text, /no longer works/);
  const r = await api('GET', link.pathname + link.search);
  assert.equal(r.status, 303);
  assert.equal(r.headers.get('location'), `/w/${listA.id}?email=confirmed`);
  const again = await api('GET', link.pathname + link.search);
  assert.equal(again.status, 303, 'a second click still lands on the page');
  const v = await api('GET', `/api/watchlists?id=${listA.id}`);
  assert.equal(v.json.watchlist.email.confirmed, true);
  assert.equal(v.json.watchlist.email.status, 'confirmed');
  assert.equal(v.json.watchlist.email.resend_available_at, null);
  assert.equal((await indexOf(A)).watchlists[listA.id].confirmed, true);
});

// ---------- daily digest ----------
const B = 'pending.person@example.net';
let listB;
await test('digest: nothing before new items; then only items first seen since the last email', async () => {
  const b = await make({ home_town: 'MA:Carver', towns: area('MA:Carver'), topics: ['solar'], email: B });
  assert.equal(b.status, 201, b.text);
  listB = b.json.id; // never confirmed

  const unauth = await api('POST', '/api/cron/dispatch', { headers: { authorization: 'Bearer wrong' } });
  assert.equal(unauth.status, 401);
  const before = (await outbox()).length;
  const first = await cron();
  assert.equal(first.status, 200, first.text);
  assert.equal(first.json.email_sent, 0);
  assert.ok(first.json.email_nothing_new >= 1);
  assert.equal((await outbox()).length, before);

  const proto = hitsDoc.hits[0];
  const fresh = (n, town, topics, snippet) => ({
    ...proto, id: `test${n}`, state: 'MA', town, county: 'Plymouth', board: 'Planning Board', board_key: 'planning_board',
    meeting_date: '2026-10-20', topics, snippet, source_url: `https://example.gov/agenda/${n}`, first_seen: '2026-10-13T11:00:00+00:00',
  });
  const next = {
    ...hitsDoc,
    generated: '2026-10-13T11:05:00+00:00',
    hits: [
      ...hitsDoc.hits,
      fresh(1, 'Carver', ['solar'], 'NEW ITEM ONE: public hearing on a 5 MW ground-mounted solar array off Route 58.'),
      fresh(2, 'Plymouth', ['battery_storage'], 'NEW ITEM TWO: special permit for a battery energy storage system.'),
      fresh(3, 'Boston', ['solar'], 'BOSTON ITEM outside the area.'),
      fresh(4, 'Carver', ['wireless_telecom'], 'TOWER ITEM on a topic the list does not follow.'),
    ],
  };
  await writeFile(HITS, JSON.stringify(next));
  process.env.DISPATCH_EMAIL_BUDGET_MS = '-1'; // out of time before the first email
  const late = await cron();
  delete process.env.DISPATCH_EMAIL_BUDGET_MS;
  assert.equal(late.json.email_deferred, 1, late.text);
  assert.equal(late.json.email_sent, 0);
  assert.equal(late.json.sent, 1, 'webhooks go first and are not held back');
  const second = await cron();
  assert.equal(second.json.email_sent, 1, second.text);
  assert.equal(second.json.sent, 0, 'the webhook already went out on the earlier run');

  const digests = (await mailTo(A_STORED)).filter((m) => /: \d+ new items?/.test(m.subject));
  assert.equal(digests.length, 1);
  const d = digests[0];
  assert.equal(d.subject, 'Agenda Ahead: 2 new items for Carver email');
  assert.match(d.text, /^Agenda Ahead found 2 new agenda items for Carver email since you signed up\./);
  assert.match(d.text, /NEW ITEM ONE/);
  assert.match(d.text, /NEW ITEM TWO/);
  assert.ok(!/BOSTON ITEM|TOWER ITEM/.test(d.text), 'only matching towns and topics');
  const old = W.matchItems(hitsDoc.hits, { towns: area('MA:Carver'), topics: ['solar', 'battery_storage', 'zoning_amendment'] });
  assert.ok(old.length > 0, 'fixture has older matching items');
  assert.ok(old.every((h) => !d.text.includes(h.source_url)), 'items from before the opt-in are left out');
  assert.match(d.text, /Carver, MA: Planning Board\nMeeting: Tue, Oct 20, 2026\nTopics: Solar\n“NEW ITEM ONE/);
  assert.ok(d.text.includes(`/w/${listA.feed}`) && d.text.includes(`/w/${listA.id}`), 'share and manage links');
  assert.match(d.headers['List-Unsubscribe'], /action=unsubscribe/);
  assert.equal(d.headers['List-Unsubscribe-Post'], 'List-Unsubscribe=One-Click');
  assert.match(d.html, /<blockquote[^>]*>NEW ITEM ONE/);
  assert.equal((await mailTo(B)).filter((m) => /: \d+ new items?/.test(m.subject)).length, 0, 'unconfirmed address gets no digest');
  assert.match(JSON.stringify(hooks.at(-1).body), /NEW ITEM ONE/);

  const stored = await getBlob(`watchlists/${listA.id}.json`);
  assert.equal(stored.email.last_emailed_at, '2026-10-13T11:05:00+00:00');
  assert.equal(stored.email.last_email.ok, true);
  assert.equal(stored.email.last_email.sent, 2);

  const third = await cron();
  assert.equal(third.json.email_sent, 0);
  assert.equal((await mailTo(A_STORED)).length, 2, 'no second digest for the same items');
});

await test('subjects read naturally for unnamed lists', async () => {
  const wl = { id: 'x', feed_id: 'y', name: '', home_town: 'MA:Carver', towns: area('MA:Carver'), topics: ['solar'],
    email: { address: 'a@example.org', confirm_token: 'y.t', unsubscribe_token: 'y.u', last_email: { ok: true } } };
  const items = W.matchItems(hitsDoc.hits, { towns: ['MA:Plymouth'], topics: TOPICS }).slice(0, 2);
  const d = EA.digestMessage(wl, items, 0, 'https://example.org');
  assert.equal(d.subject, 'Agenda Ahead: 2 new items for Carver and neighbors');
  assert.match(d.text, /since the last email\./);
  assert.equal(EA.digestMessage({ ...wl, towns: ['MA:Carver'] }, items.slice(0, 1), 0, 'https://example.org').subject, 'Agenda Ahead: 1 new item for Carver');
  assert.equal(EA.watchlistLabel({ towns: ['MA:Boston', 'MA:Carver', 'NY:Southold'] }), 'Boston and 2 other towns');
  assert.equal(EA.confirmationMessage(wl, 'https://example.org').subject, 'Agenda Ahead: confirm daily emails for Carver and neighbors');
});

// ---------- unsubscribe ----------
await test('unsubscribe link removes the address at once (GET page, POST one-click)', async () => {
  const d = (await mailTo(A_STORED)).find((m) => /: \d+ new items?/.test(m.subject));
  const link = linkIn(d.text, 'unsubscribe');
  const r = keepPage(await api('GET', link.pathname + link.search));
  assert.equal(r.status, 200);
  assert.match(r.text, /You are unsubscribed/);
  assert.match(r.text, /J\*\*\*@example\.com/);
  const v = await api('GET', `/api/watchlists?id=${listA.id}`);
  assert.equal(v.json.watchlist.email.configured, false);
  assert.equal((await getBlob(`watchlists/${listA.id}.json`)).email, null);
  assert.equal((await indexOf(A))?.watchlists?.[listA.id], undefined);
  const again = keepPage(await api('GET', link.pathname + link.search));
  assert.match(again.text, /not on the list/);

  const c = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: 'one.click@example.org' });
  const [mail] = await mailTo('one.click@example.org');
  const u = linkIn(mail.text, 'unsubscribe');
  const post = await api('POST', u.pathname + u.search, { body: 'List-Unsubscribe=One-Click', headers: { 'content-type': 'application/x-www-form-urlencoded' } });
  assert.equal(post.status, 200);
  assert.deepEqual(post.json, { ok: true, unsubscribed: true });
  assert.equal((await getBlob(`watchlists/${c.json.id}.json`)).email, null);
});

// ---------- limits ----------
await test('at most 3 watchlists per address, and 3 confirmation emails a day per address', async () => {
  const L = 'limit@example.net';
  const ids = [];
  for (let i = 0; i < 3; i += 1) {
    const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: L });
    assert.equal(r.status, 201, r.text);
    ids.push(r.json.id);
  }
  const fourth = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: L });
  assert.equal(fourth.status, 400);
  assert.match(fourth.json.fields.email, /already gets 3 sets of alerts/);
  const del = await api('DELETE', `/api/watchlists?id=${ids[0]}`);
  assert.equal(del.status, 200);
  const retry = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: L });
  assert.equal(retry.status, 429, 'a free slot, but 3 confirmation emails went out today');
  assert.match(retry.json.fields.email, /several confirmation emails/);
});

await test('per-network limit on email sign-ups', async () => {
  const ip = '10.200.0.1';
  for (let i = 0; i < 10; i += 1) {
    const r = await api('POST', '/api/watchlists', { ip, body: { home_town: 'MA:Carver', towns: ['MA:Carver'], topics: ['solar'], email: `net${i}@example.org` } });
    assert.equal(r.status, 201, r.text);
  }
  const r = await api('POST', '/api/watchlists', { ip, body: { home_town: 'MA:Carver', towns: ['MA:Carver'], topics: ['solar'], email: 'net10@example.org' } });
  assert.equal(r.status, 429);
  assert.match(r.json.fields.email, /network/);
});

await test('one resend, allowed after 24 hours', async () => {
  const R = 'resend.me@example.org';
  const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: R });
  const id = r.json.id;
  const early = await api('POST', `/api/email?action=resend&id=${id}`);
  assert.equal(early.status, 429);
  assert.ok(early.json.retry_after);
  const feed = new URL(r.json.watchlist.links.share).pathname.split('/').pop();
  assert.equal((await api('POST', `/api/email?action=resend&id=${feed}`)).status, 403);
  const wl = await getBlob(`watchlists/${id}.json`);
  wl.email.confirm_sent_at = new Date(Date.now() - 25 * 3600e3).toISOString();
  await putBlob(`watchlists/${id}.json`, wl);
  const ok = await api('POST', `/api/email?action=resend&id=${id}`);
  assert.equal(ok.status, 200, ok.text);
  assert.equal((await mailTo(R)).length, 2);
  const third = await api('POST', `/api/email?action=resend&id=${id}`);
  assert.equal(third.status, 429);
  assert.match(third.json.error, /Two confirmation emails/);
  assert.equal((await mailTo(R)).length, 2);
});

await test('changing or removing the address on update', async () => {
  const p1 = 'first.address@example.org';
  const p2 = 'second.address@example.org';
  const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: p1 });
  const id = r.json.id;
  const [m1] = await mailTo(p1);
  const oldUnsub = linkIn(m1.text, 'unsubscribe');
  const bad = await api('PATCH', `/api/watchlists?id=${id}`, { body: { email: 'not-an-address' } });
  assert.equal(bad.status, 400);
  assert.match(bad.json.fields.email, /like name@example.com/);
  const change = await api('PATCH', `/api/watchlists?id=${id}`, { body: { email: p2 } });
  assert.equal(change.status, 200, change.text);
  assert.equal(change.json.watchlist.email.masked, 's***@example.org');
  assert.equal((await mailTo(p2)).length, 1);
  assert.equal((await indexOf(p1))?.watchlists?.[id], undefined);
  assert.ok((await indexOf(p2)).watchlists[id]);
  const stale = await api('GET', oldUnsub.pathname + oldUnsub.search);
  assert.match(stale.text, /not on the list/, 'old links stop working');
  assert.equal((await getBlob(`watchlists/${id}.json`)).email.address, p2);
  const same = await api('PATCH', `/api/watchlists?id=${id}`, { body: { email: p2.toUpperCase() } });
  assert.equal(same.status, 200);
  assert.equal((await mailTo(p2)).length, 1, 'same address in another case sends nothing');
  const echo = await api('PATCH', `/api/watchlists?id=${id}`, { body: { name: 'renamed', email: 's***@example.org' } });
  assert.equal(echo.status, 200, echo.text);
  assert.equal((await getBlob(`watchlists/${id}.json`)).email.address, p2, 'the masked form sent back changes nothing');
  assert.equal((await mailTo(p2)).length, 1);
  const off = await api('PATCH', `/api/watchlists?id=${id}`, { body: { email: '' } });
  assert.equal(off.json.watchlist.email.configured, false);
  assert.equal((await indexOf(p2))?.watchlists?.[id], undefined);
});

// ---------- delete (regression) ----------
await test('delete removes the watchlist, its feed index and its email index entry', async () => {
  const D = 'delete.me@example.org';
  const r = await make({ home_town: 'MA:Carver', towns: ['MA:Carver'], email: D });
  const id = r.json.id;
  const feed = new URL(r.json.watchlist.links.share).pathname.split('/').pop();
  assert.ok(await getBlob(`feeds/${feed}.json`));
  assert.ok((await indexOf(D)).watchlists[id]);
  const del = await api('DELETE', `/api/watchlists?id=${id}`);
  assert.deepEqual(del.json, { ok: true, deleted: true });
  assert.equal(await getBlob(`watchlists/${id}.json`), null);
  assert.equal(await getBlob(`feeds/${feed}.json`), null);
  assert.equal((await indexOf(D))?.watchlists?.[id], undefined);
  assert.equal((await api('GET', `/api/feed?id=${feed}&format=json`)).status, 404);
});

await test('feeds (json, rss, ics) still answer for a list', async () => {
  const json = await api('GET', `/api/feed?id=${carver.feed}&format=json`);
  assert.equal(json.status, 200);
  assert.ok(json.json.items.length > 0);
  assert.match((await api('GET', `/api/feed?id=${carver.feed}&format=rss`)).text, /<rss version="2.0"/);
  assert.match((await api('GET', `/api/feed?id=${carver.id}&format=ics`)).text, /BEGIN:VCALENDAR/);
});

await test('neighbors.json is served at /data/neighbors.json', async () => {
  const r = await api('GET', '/data/neighbors.json');
  assert.equal(r.status, 200);
  assert.ok(r.json['MA:Carver'].includes('MA:Plymouth'));
});

// The link pages, saved next to the emails so the copy linter can read them.
await Promise.all(PAGES.map((html, i) => writeFile(join(OUTBOX, `page-${i}.html`), html)));
console.log(`\n${passed} passed, ${failed} failed. Outbox (emails and link pages): ${OUTBOX}`);
process.exit(failed ? 1 : 0);
