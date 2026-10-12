// Email alerts for watchlists: address checks, the per-address index, confirmation and unsubscribe
// tokens, the confirmation and daily digest messages, and the email block of the private view.
// Sending goes through _email.js (the provider module).
//
// On the watchlist (watchlists/<id>.json):
//   email: { address, confirmed, confirm_token, unsubscribe_token, requested_at, confirm_sends,
//            confirm_sent_at, confirmed_at, last_emailed_at, last_email, failures }
// Tokens are "<feed_id>.<24 random chars>": the read-only key finds the watchlist, the random part
// proves the link came from our email. Neither token is the private key.
//
// Per address (emails/<sha256 of the lowercased address>.json, private):
//   { watchlists: { <watchlist id>: { confirmed, at } }, sends: [ISO times of confirmation emails] }
// It enforces 3 watchlists per address and the confirmation-email limits, and holds no address.
import { createHash, timingSafeEqual } from 'node:crypto';
import { readJSON, removeJSON, writeJSON } from './_store.js';
import { emailEnabled, sendEmail } from './_email.js';
import { SITE_NAME, TOPICS, blobPath, feedIndexPath, fmtDate, newId, saveWatchlist, shareId, validId } from './_watch.js';

export const MAX_LISTS_PER_ADDRESS = 3;
export const DIGEST_MAX_ITEMS = 50;
const DAY = 24 * 60 * 60 * 1000;
const PENDING_HOLDS_SLOT = 7 * DAY; // an unconfirmed address stops counting toward the 3 after a week
const SENDS_PER_DAY = 3; // confirmation emails per address, all watchlists together
const SENDS_PER_30_DAYS = 6;
const RESEND_AFTER = DAY;

export const EMAIL_OFF_MESSAGE =
  'Email alerts are not set up on this site yet. Use the RSS or calendar feed, or a Slack, Teams or Discord webhook.';

// ---------- addresses ----------

const EMAIL_RE = /^[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]{1,64}@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$/;
const BAD_ADDRESS = 'Enter an email address like name@example.com.';

// Returns { address } (null when empty) or { error }.
export function parseEmail(raw) {
  if (raw === undefined || raw === null) return { address: null };
  if (typeof raw !== 'string') return { error: BAD_ADDRESS };
  const value = raw.trim();
  if (!value) return { address: null };
  if (value.length > 254) return { error: 'That email address is too long.' };
  const at = value.lastIndexOf('@');
  const local = value.slice(0, at);
  if (!EMAIL_RE.test(value) || local.startsWith('.') || local.endsWith('.') || local.includes('..')) return { error: BAD_ADDRESS };
  return { address: `${local}@${value.slice(at + 1).toLowerCase()}` };
}

export const sameAddress = (a, b) => String(a || '').toLowerCase() === String(b || '').toLowerCase();

// j***@example.com
export function maskEmail(address) {
  const at = String(address || '').lastIndexOf('@');
  if (at < 1) return null;
  return `${address[0]}***@${address.slice(at + 1)}`;
}

const addressKey = (address) => createHash('sha256').update(String(address).toLowerCase()).digest('hex');
export const emailIndexPath = (address) => `emails/${addressKey(address)}.json`;

// ---------- the per-address index ----------

export async function loadIndex(address) {
  const idx = await readJSON(emailIndexPath(address));
  return { watchlists: idx?.watchlists || {}, sends: Array.isArray(idx?.sends) ? idx.sends : [] };
}

export async function saveIndex(address, idx) {
  const now = Date.now();
  idx.sends = idx.sends.filter((t) => now - Date.parse(t) < 30 * DAY);
  if (!Object.keys(idx.watchlists).length && !idx.sends.length) {
    await removeJSON(emailIndexPath(address)).catch(() => {});
    return;
  }
  await writeJSON(emailIndexPath(address), idx);
}

function slotsTaken(idx, exceptId, now = Date.now()) {
  return Object.entries(idx.watchlists).filter(
    ([id, e]) => id !== exceptId && (e.confirmed || now - Date.parse(e.at) < PENDING_HOLDS_SLOT),
  ).length;
}

function sendLimit(idx, now = Date.now()) {
  const times = idx.sends.map((t) => Date.parse(t)).filter(Number.isFinite);
  if (times.filter((t) => now - t < DAY).length >= SENDS_PER_DAY) return 'tomorrow';
  if (times.filter((t) => now - t < 30 * DAY).length >= SENDS_PER_30_DAYS) return 'in a few weeks';
  return null;
}

// Checks a new address for a watchlist before anything is saved or sent.
// Returns { idx } or { status, error }.
export async function admitAddress(address, watchlistId) {
  const idx = await loadIndex(address);
  if (slotsTaken(idx, watchlistId) >= MAX_LISTS_PER_ADDRESS) {
    return {
      status: 400,
      error: `This address already gets ${MAX_LISTS_PER_ADDRESS} sets of alerts, the most one address can have. Unsubscribe it from one of them first (the link is at the bottom of each email).`,
    };
  }
  const later = sendLimit(idx);
  if (later) return { status: 429, error: `We have sent several confirmation emails to this address recently. Try again ${later}.` };
  return { idx };
}

// ---------- the watchlist's email state ----------

const makeToken = (wl) => `${wl.feed_id}.${newId()}`;
const TOKEN_RE = /^([A-Za-z0-9_-]{24,64})\.[A-Za-z0-9_-]{24,64}$/;

export function sameToken(stored, given) {
  if (typeof stored !== 'string' || typeof given !== 'string' || stored.length !== given.length) return false;
  return timingSafeEqual(Buffer.from(stored), Buffer.from(given));
}

// A new, unconfirmed address. Items first seen after `since` (the data snapshot when it was asked
// for) go in the first digest once it is confirmed.
export function attachEmail(wl, address, since) {
  const now = new Date().toISOString();
  wl.email = {
    address,
    confirmed: false,
    confirm_token: makeToken(wl),
    unsubscribe_token: makeToken(wl),
    requested_at: now,
    confirm_sends: 0,
    confirm_sent_at: null,
    confirmed_at: null,
    last_emailed_at: since || now,
    last_email: null,
    failures: 0,
  };
}

// Removes the address from the watchlist object and from its index. The caller saves the watchlist.
export async function detachEmail(wl) {
  const address = wl.email?.address;
  wl.email = null;
  if (!address) return;
  try {
    const idx = await loadIndex(address);
    delete idx.watchlists[wl.id];
    await saveIndex(address, idx);
  } catch (err) {
    console.error('email index update failed', err.message);
  }
}

// Sends the confirmation email and records it on the watchlist and in `idx` (the caller saves both).
export async function sendConfirmation(wl, idx, base) {
  const e = wl.email;
  const result = await sendEmail({ to: e.address, ...confirmationMessage(wl, base) });
  const now = new Date().toISOString();
  idx.watchlists[wl.id] = { confirmed: false, at: e.requested_at };
  if (result.ok) {
    e.confirm_sends += 1;
    e.confirm_sent_at = now;
    delete e.confirm_error;
    idx.sends.push(now);
  } else {
    e.confirm_error = result.error || `HTTP ${result.status}`;
  }
  return result;
}

// When one more confirmation email may be asked for: at once if none got out, 24 hours after the
// first one, and never after a second one. Null once confirmed or when no more are allowed.
export function resendAvailableAt(e) {
  if (!e || e.confirmed) return null;
  if (!e.confirm_sends) return e.requested_at;
  if (e.confirm_sends === 1) return new Date(Date.parse(e.confirm_sent_at) + RESEND_AFTER).toISOString();
  return null;
}

// Resolves a confirmation or unsubscribe token to { wl } (or null) through the feed index.
export async function findByToken(token) {
  const m = typeof token === 'string' ? TOKEN_RE.exec(token) : null;
  if (!m) return null;
  const ref = await readJSON(feedIndexPath(m[1]));
  if (!ref?.watchlist_id || !validId(ref.watchlist_id)) return null;
  const wl = await readJSON(blobPath(ref.watchlist_id));
  return wl && wl.feed_id === m[1] ? { wl } : null;
}

export async function confirmAddress(wl) {
  const e = wl.email;
  const idx = await loadIndex(e.address);
  const confirmedElsewhere = Object.entries(idx.watchlists).filter(([id, x]) => id !== wl.id && x.confirmed).length;
  if (confirmedElsewhere >= MAX_LISTS_PER_ADDRESS) return false;
  e.confirmed = true;
  e.confirmed_at = new Date().toISOString();
  idx.watchlists[wl.id] = { confirmed: true, at: e.requested_at };
  await saveWatchlist(wl);
  await saveIndex(e.address, idx);
  return true;
}

// The private view's email block. The read-only view and the feeds never call this.
export function emailView(wl) {
  const available = emailEnabled();
  const e = wl.email;
  if (!e?.address) return { configured: false, available, confirmed: false, masked: null };
  return {
    configured: true,
    available,
    confirmed: Boolean(e.confirmed),
    masked: maskEmail(e.address),
    status: e.confirmed ? 'confirmed' : 'pending',
    requested_at: e.requested_at || null,
    confirmed_at: e.confirmed_at || null,
    confirmation_sent: Boolean(e.confirm_sends),
    resend_available_at: resendAvailableAt(e),
    last_email: e.last_email || null,
  };
}

// ---------- messages ----------

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const townName = (id) => String(id).split(':').slice(1).join(':');
const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;

export function watchlistLabel(wl) {
  if (wl.name) return wl.name;
  const towns = wl.towns || [];
  if (wl.home_town && towns.includes(wl.home_town)) {
    const others = towns.length - 1;
    return others ? `${townName(wl.home_town)} and neighbors` : townName(wl.home_town);
  }
  if (!towns.length) return 'your towns';
  return towns.length > 1 ? `${townName(towns[0])} and ${plural(towns.length - 1, 'other town')}` : townName(towns[0]);
}

function townList(wl, max = 15) {
  const byState = new Map();
  for (const id of (wl.towns || []).slice(0, max)) {
    const st = String(id).split(':')[0];
    if (!byState.has(st)) byState.set(st, []);
    byState.get(st).push(townName(id));
  }
  const parts = [...byState].map(([st, names]) => `${names.join(', ')} (${st})`);
  const rest = (wl.towns || []).length - max;
  return parts.join('; ') + (rest > 0 ? ` and ${rest} more` : '');
}

const topicList = (topics) => (topics || []).map((t) => TOPICS[t] || t).join(', ');

function links(wl, base) {
  return {
    share: `${base}/w/${shareId(wl)}`,
    manage: `${base}/w/${wl.id}`,
    confirm: `${base}/api/email?action=confirm&t=${wl.email.confirm_token}`,
    unsubscribe: `${base}/api/email?action=unsubscribe&t=${wl.email.unsubscribe_token}`,
  };
}

function unsubscribeHeaders(url) {
  return { 'List-Unsubscribe': `<${url}>`, 'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click' };
}

const STYLE = {
  body: 'margin:0;padding:24px 16px;background:#ffffff;color:#1a1a1a;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5',
  box: 'max-width:600px;margin:0 auto',
  p: 'margin:0 0 12px',
  small: 'margin:0 0 8px;font-size:14px;color:#555555',
  meta: 'margin:0;font-size:14px;color:#555555',
  link: 'color:#1b4f8a',
  item: 'border-top:1px solid #dddddd;padding:12px 0',
  quote: 'margin:6px 0 8px;padding:0 0 0 12px;border-left:3px solid #cccccc;color:#333333',
  foot: 'border-top:1px solid #dddddd;margin-top:8px;padding-top:12px',
};

function htmlDoc(subject, inner) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(subject)}</title></head>
<body style="${STYLE.body}"><div style="${STYLE.box}">
${inner}
</div></body></html>
`;
}

export function confirmationMessage(wl, base) {
  const l = links(wl, base);
  const label = watchlistLabel(wl);
  const subject = `${SITE_NAME}: confirm daily emails for ${label}`;
  const text = [
    `This address was entered on ${SITE_NAME} to get a daily email when town agendas have something new for these towns and subjects:`,
    '',
    `Alerts for: ${label}`,
    `Towns: ${townList(wl)}`,
    `Topics: ${topicList(wl.topics)}`,
    '',
    'To start the emails, open this link and press Confirm:',
    l.confirm,
    '',
    'No alerts are sent until the address is confirmed. If you did not ask for this, ignore this email, or remove the address now:',
    l.unsubscribe,
    '',
  ].join('\n');
  const html = htmlDoc(subject, [
    `<p style="${STYLE.p}">This address was entered on ${esc(SITE_NAME)} to get a daily email when town agendas have something new for these towns and subjects:</p>`,
    `<p style="${STYLE.p}"><b>${esc(label)}</b><br>Towns: ${esc(townList(wl))}<br>Topics: ${esc(topicList(wl.topics))}</p>`,
    `<p style="${STYLE.p}"><a href="${esc(l.confirm)}" style="${STYLE.link};font-weight:bold">Start the daily emails</a></p>`,
    `<p style="${STYLE.small}">No alerts are sent until the address is confirmed. If you did not ask for this, ignore this email, or <a href="${esc(l.unsubscribe)}" style="${STYLE.link}">remove the address now</a>.</p>`,
  ].join('\n'));
  return { subject, text, html, headers: unsubscribeHeaders(l.unsubscribe) };
}

const oneLine = (s, max = 200) => {
  const flat = String(s ?? '').replace(/\s+/g, ' ').trim();
  return flat.length > max ? `${flat.slice(0, max - 1).trimEnd()}…` : flat;
};
const matchedTopics = (h, wl) => {
  const wanted = new Set(wl.topics || []);
  return topicList((h.topics || []).filter((t) => wanted.has(t)));
};

export function digestMessage(wl, items, more, base) {
  const l = links(wl, base);
  const label = watchlistLabel(wl);
  const total = items.length + more;
  const subject = `${SITE_NAME}: ${plural(total, 'new item')} for ${label}`;
  const since = wl.email.last_email?.ok ? 'since the last email' : 'since you signed up';
  const lead = `${SITE_NAME} found ${plural(total, 'new agenda item')} for ${label} ${since}.`;
  const why = `You get this email because ${maskEmail(wl.email.address)} confirmed daily alerts for these towns. Days without new items get no email. Agendas can change: confirm the time and place with the town.`;

  const textItems = items.map((h) => [
    `${h.town}, ${h.state}: ${h.board}`,
    `Meeting: ${fmtDate(h.meeting_date)}`,
    `Topics: ${matchedTopics(h, wl)}`,
    `“${oneLine(h.snippet)}”`,
    `Agenda: ${h.source_url}`,
  ].join('\n'));
  const text = [
    lead,
    '',
    textItems.join('\n\n'),
    ...(more ? ['', `And ${more} more on your alerts page: ${l.share}`] : []),
    '',
    '--',
    `Alerts page (safe to share): ${l.share}`,
    `Change towns, topics or email (private link, do not forward this email): ${l.manage}`,
    `Unsubscribe from these emails: ${l.unsubscribe}`,
    '',
    why,
    '',
  ].join('\n');

  const htmlItems = items.map((h) => `<div style="${STYLE.item}">
<p style="margin:0;font-weight:bold">${esc(h.town)}, ${esc(h.state)}: ${esc(h.board)}</p>
<p style="${STYLE.meta}">Meeting ${esc(fmtDate(h.meeting_date))}. Topics: ${esc(matchedTopics(h, wl))}</p>
<blockquote style="${STYLE.quote}">${esc(oneLine(h.snippet))}</blockquote>
<p style="margin:0"><a href="${esc(h.source_url)}" style="${STYLE.link}">Open the agenda</a></p>
</div>`);
  const html = htmlDoc(subject, [
    `<p style="${STYLE.p}">${esc(lead)}</p>`,
    ...htmlItems,
    ...(more ? [`<p style="${STYLE.item}">And ${more} more on the <a href="${esc(l.share)}" style="${STYLE.link}">alerts page</a>.</p>`] : []),
    `<div style="${STYLE.foot}">`,
    `<p style="${STYLE.small}"><a href="${esc(l.share)}" style="${STYLE.link}">Alerts page</a> (safe to share)</p>`,
    `<p style="${STYLE.small}"><a href="${esc(l.manage)}" style="${STYLE.link}">Change towns, topics or email</a> (private link, do not forward this email)</p>`,
    `<p style="${STYLE.small}"><a href="${esc(l.unsubscribe)}" style="${STYLE.link}">Unsubscribe</a> from these emails</p>`,
    `<p style="${STYLE.small}">${esc(why)}</p>`,
    '</div>',
  ].join('\n'));
  return { subject, text, html, headers: unsubscribeHeaders(l.unsubscribe) };
}

// ---------- small HTML pages for the confirm and unsubscribe links ----------
// Link scanners (Safe Links, mail gateways) open every link in an email, so a GET only shows a page.
// The page's button posts a plain form back to the same URL (no script, fits the site CSP), and
// only that POST changes anything.
//   form: { action, token, button }   link: { before, href, text }

export function linkPage(res, status, title, message, { form, link } = {}) {
  const formHtml = form
    ? `<form method="post" action="${esc(form.action)}"><input type="hidden" name="t" value="${esc(form.token)}">` +
      `<button type="submit" class="btn">${esc(form.button)}</button></form>`
    : '';
  const linkHtml = link ? `<p>${esc(link.before)} <a href="${esc(link.href)}">${esc(link.text)}</a>.</p>` : '';
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('X-Robots-Tag', 'noindex');
  res.status(status).send(`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><meta name="referrer" content="no-referrer">
<title>${esc(title)} | ${esc(SITE_NAME)}</title><link rel="stylesheet" href="/styles.css"></head>
<body><header class="site"><div class="wrap"><a class="brand" href="/">${esc(SITE_NAME)}</a></div></header>
<main id="main"><div class="wrap"><section class="hero compact"><h1>${esc(title)}</h1><p class="lead">${esc(message)}</p>
${formHtml}${linkHtml}</section></div></main>
</body></html>
`);
}
