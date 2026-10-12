// Email alert links and actions.
//   GET|POST /api/email?action=confirm&t=<token>       confirms the address, then 303 to /w/<private id>?email=confirmed
//   GET|POST /api/email?action=unsubscribe&t=<token>   removes the address at once; GET shows a page, POST
//                                                      (RFC 8058 one-click, List-Unsubscribe-Post) answers 200 JSON
//   POST     /api/email?action=resend&id=<private id>  one more confirmation email: at once if the first failed,
//                                                      otherwise once, 24 hours after the first
import { allow, bodySize, noStore, throttled } from './_store.js';
import { SITE_NAME, publicBase, publicView, resolveWatchlist, saveWatchlist } from './_watch.js';
import { emailEnabled } from './_email.js';
import {
  EMAIL_OFF_MESSAGE, MAX_LISTS_PER_ADDRESS, admitAddress, confirmAddress, detachEmail, emailView, findByToken,
  linkPage, maskEmail, resendAvailableAt, sameToken, saveIndex, sendConfirmation,
} from './_email_alerts.js';

const HOUR = 60 * 60 * 1000;

function fmtTime(iso) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York', timeZoneName: 'short',
  });
}

async function confirm(req, res, token) {
  const found = await findByToken(token);
  const wl = found?.wl;
  if (!wl?.email || !sameToken(wl.email.confirm_token, token)) {
    return linkPage(res, 404, 'This link no longer works',
      'The address may have been removed or changed, or the watchlist deleted. To get email alerts, add the address again on the watchlist page.');
  }
  if (!wl.email.confirmed && !(await confirmAddress(wl))) {
    return linkPage(res, 409, `This address already gets ${MAX_LISTS_PER_ADDRESS} watchlists`,
      `One address can get alerts from ${MAX_LISTS_PER_ADDRESS} watchlists. Unsubscribe it from one of them (the link is at the bottom of each email), then open this link again.`);
  }
  res.statusCode = 303;
  res.setHeader('Location', `/w/${wl.id}?email=confirmed`);
  return res.end();
}

async function unsubscribe(req, res, token) {
  const found = await findByToken(token);
  const wl = found?.wl;
  let masked = null;
  if (wl?.email && sameToken(wl.email.unsubscribe_token, token)) {
    masked = maskEmail(wl.email.address);
    await detachEmail(wl);
    wl.updated_at = new Date().toISOString();
    await saveWatchlist(wl);
  }
  if (req.method === 'POST') return res.status(200).json({ ok: true, unsubscribed: true });
  if (masked) {
    return linkPage(res, 200, 'You are unsubscribed',
      `${masked} will get no more emails from this watchlist. Its web page and feeds keep working.`);
  }
  return linkPage(res, 200, 'This address is not on the list',
    `It may have been removed already. No more emails from ${SITE_NAME} will be sent through this link.`);
}

async function resend(req, res) {
  const fail = (status, error, extra) => res.status(status).json({ ok: false, error, ...(extra || {}) });
  if (bodySize(req) > 4096) return fail(413, 'Request too large.');
  const id = typeof req.query?.id === 'string' ? req.query.id : '';
  const { wl, readonly } = await resolveWatchlist(id);
  if (!wl) return fail(404, 'Watchlist not found. It may have been deleted.');
  if (readonly) return fail(403, 'This is a read-only link. Use the private link to change this watchlist.');
  const e = wl.email;
  if (!e?.address) return fail(400, 'This watchlist has no email address.');
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
  const action = typeof req.query?.action === 'string' ? req.query.action : '';
  const token = typeof req.query?.t === 'string' ? req.query.t : '';
  try {
    if (action === 'confirm') return await confirm(req, res, token);
    if (action === 'unsubscribe') return await unsubscribe(req, res, token);
    if (action === 'resend' && req.method === 'POST') return await resend(req, res);
    return res.status(400).json({ ok: false, error: 'Unknown action.' });
  } catch (err) {
    console.error('email action failed', action, err);
    if (req.method === 'GET') return linkPage(res, 500, 'Something went wrong', 'Please open the link again in a few minutes.');
    return res.status(500).json({ ok: false, error: 'Something went wrong. Please try again.' });
  }
}
