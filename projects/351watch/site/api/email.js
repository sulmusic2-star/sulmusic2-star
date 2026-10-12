// Email alert links and actions. Mail scanners open links, so a GET never changes anything: it
// shows a page whose button POSTs a plain form back to the same URL.
//   GET  /api/email?action=confirm&t=<token>       page with a "Confirm alerts for j***@…" button
//   POST /api/email?action=confirm&t=<token>       confirms, then 303 to /w/<private id>?email=confirmed
//   GET  /api/email?action=unsubscribe&t=<token>   page with an "Unsubscribe j***@…" button
//   POST /api/email?action=unsubscribe&t=<token>   removes the address at once. The RFC 8058 one-click
//                                                  POST (body List-Unsubscribe=One-Click, sent by mail
//                                                  providers) answers 200 JSON; the form answers a page.
//   POST /api/email?action=resend&id=<private id>  one more confirmation email: at once if the first send
//                                                  failed, otherwise once, 24 hours after the first
import { allow, bodySize, noStore, throttled } from './_store.js';
import { SITE_NAME, publicBase, publicView, resolveWatchlist, saveWatchlist } from './_watch.js';
import { emailEnabled } from './_email.js';
import {
  EMAIL_OFF_MESSAGE, MAX_LISTS_PER_ADDRESS, admitAddress, confirmAddress, detachEmail, emailView, findByToken,
  linkPage, maskEmail, resendAvailableAt, sameToken, saveIndex, sendConfirmation, watchlistLabel,
} from './_email_alerts.js';

const HOUR = 60 * 60 * 1000;
const STALE_TITLE = 'This link no longer works';
const STALE_TEXT = 'The address may have been removed or changed, or the alerts deleted. To get email alerts, add the address again on your alerts page.';

function fmtTime(iso) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York', timeZoneName: 'short',
  });
}

// Form fields from a POST: a parsed object, or { _raw } when the body arrived as text or bytes.
function readForm(req) {
  let body;
  try {
    body = req.body; // Vercel parses lazily and can throw on a malformed body
  } catch {
    return {};
  }
  if (body && typeof body === 'object' && !Buffer.isBuffer(body)) return body;
  const raw = Buffer.isBuffer(body) ? body.toString('utf8') : typeof body === 'string' ? body : '';
  return { _raw: raw.slice(0, 4000) };
}

// RFC 8058: urlencoded "List-Unsubscribe=One-Click", or the same field in multipart/form-data.
const isOneClick = (form) =>
  form['List-Unsubscribe'] === 'One-Click' || /List-Unsubscribe(?:=|"\s*)One-Click/i.test(form._raw || '');

const formAction = (action, token) => `/api/email?action=${action}&t=${encodeURIComponent(token)}`;

async function confirm(req, res, token) {
  const found = await findByToken(token);
  const wl = found?.wl;
  if (!wl?.email || !sameToken(wl.email.confirm_token, token)) return linkPage(res, 404, STALE_TITLE, STALE_TEXT);
  const masked = maskEmail(wl.email.address);

  if (req.method === 'GET') {
    return linkPage(res, 200, 'Confirm email alerts',
      `Confirming starts a daily email to ${masked} about new items on town agendas for ${watchlistLabel(wl)}.`,
      { form: { action: formAction('confirm', token), token, button: `Confirm alerts for ${masked}` } });
  }
  if (!wl.email.confirmed && !(await confirmAddress(wl))) {
    return linkPage(res, 409, `This address already gets ${MAX_LISTS_PER_ADDRESS} sets of alerts`,
      `One address can get ${MAX_LISTS_PER_ADDRESS} sets of alerts. Unsubscribe it from one of them (the link is at the bottom of each email), then confirm again.`);
  }
  res.statusCode = 303;
  res.setHeader('Location', `/w/${wl.id}?email=confirmed`);
  return res.end();
}

async function unsubscribe(req, res, token, form) {
  const found = await findByToken(token);
  const wl = found?.wl;
  const valid = Boolean(wl?.email && sameToken(wl.email.unsubscribe_token, token));
  const oneClick = req.method === 'POST' && isOneClick(form);

  if (req.method === 'GET') {
    if (!valid) {
      return linkPage(res, 200, 'This address is not on the list',
        `It may have been removed already. No more emails from ${SITE_NAME} will be sent through this link.`);
    }
    const masked = maskEmail(wl.email.address);
    return linkPage(res, 200, 'Unsubscribe from email alerts',
      `This stops the daily emails to ${masked} for ${watchlistLabel(wl)}; the watchlist's web page and feeds keep working.`,
      { form: { action: formAction('unsubscribe', token), token, button: `Unsubscribe ${masked}` } });
  }

  let masked = null;
  if (valid) {
    masked = maskEmail(wl.email.address);
    await detachEmail(wl);
    wl.updated_at = new Date().toISOString();
    await saveWatchlist(wl);
  }
  if (oneClick) return res.status(200).json({ ok: true, unsubscribed: true });
  if (!masked) {
    return linkPage(res, 200, 'This address is not on the list',
      `It may have been removed already. No more emails from ${SITE_NAME} will be sent through this link.`);
  }
  return linkPage(res, 200, "You're unsubscribed", `${masked} will get no more emails from these alerts.`,
    { link: { before: 'To get them again, add your address on', href: `/w/${wl.id}`, text: 'your alerts page' } });
}

async function resend(req, res) {
  const fail = (status, error, extra) => res.status(status).json({ ok: false, error, ...(extra || {}) });
  const id = typeof req.query?.id === 'string' ? req.query.id : '';
  const { wl, readonly } = await resolveWatchlist(id);
  if (!wl) return fail(404, 'These alerts were not found. They may have been deleted.');
  if (readonly) return fail(403, 'This is a read-only link. Use the private link to change these alerts.');
  const e = wl.email;
  if (!e?.address) return fail(400, 'These alerts have no email address.');
  if (e.confirmed) return fail(400, 'This address is already confirmed.');
  if (!emailEnabled()) return fail(400, EMAIL_OFF_MESSAGE);

  const at = resendAvailableAt(e);
  if (!at) return fail(429, `Two confirmation emails have gone to ${maskEmail(e.address)} already. Look for a message from ${SITE_NAME} in the spam folder.`);
  if (Date.parse(at) > Date.now()) {
    return fail(429, `You can ask for one more confirmation email after ${fmtTime(at)}.`, { retry_after: at });
  }
  if (throttled(req, 'email', 10, HOUR)) return fail(429, 'Too many email requests from this network. Try again in an hour.');
  const admitted = await admitAddress(e.address, wl.id);
  if (admitted.error) return fail(admitted.status, admitted.error);

  const result = await sendConfirmation(wl, admitted.idx, publicBase(req));
  await saveWatchlist(wl);
  await saveIndex(e.address, admitted.idx);
  if (!result.ok) return fail(502, 'The confirmation email could not be sent. Try again later.');
  return res.status(200).json({ ok: true, watchlist: publicView(wl, publicBase(req), { email: emailView(wl) }) });
}

export default async function handler(req, res) {
  noStore(res);
  if (!allow(req, res, ['GET', 'POST'])) return;
  if (req.method === 'POST' && bodySize(req) > 8192) return res.status(413).json({ ok: false, error: 'Request too large.' });
  const action = typeof req.query?.action === 'string' ? req.query.action : '';
  const form = req.method === 'POST' ? readForm(req) : {};
  const token = typeof req.query?.t === 'string' ? req.query.t : typeof form.t === 'string' ? form.t : '';
  try {
    if (action === 'confirm') return await confirm(req, res, token);
    if (action === 'unsubscribe') return await unsubscribe(req, res, token, form);
    if (action === 'resend' && req.method === 'POST') return await resend(req, res);
    return res.status(400).json({ ok: false, error: 'Unknown action.' });
  } catch (err) {
    console.error('email action failed', action, err);
    if (action !== 'resend') return linkPage(res, 500, 'Something went wrong', 'Open the link again in a few minutes.');
    return res.status(500).json({ ok: false, error: 'Something went wrong. Try again.' });
  }
}
