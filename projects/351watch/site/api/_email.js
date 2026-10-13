// Email provider: the only module that knows how mail leaves the app, so the provider can be
// swapped by rewriting sendEmail() alone.
//
//   Resend (default)      POST https://api.resend.com/emails, Bearer RESEND_API_KEY
//   EMAIL_TRANSPORT=file  local testing: each message is written as JSON (plus .html and .txt copies)
//                         to EMAIL_OUTBOX (default <tmp>/351watch-outbox). Ignored on Vercel.
//
// Email is on only when EMAIL_FROM is set and either RESEND_API_KEY is set or the file transport
// is active. EMAIL_FROM is "Name <alerts@example.com>" or a bare address; a bare address gets
// SITE_NAME as its display name.
import { randomBytes } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { SITE_NAME } from './_watch.js';

const RESEND_URL = 'https://api.resend.com/emails';

export function emailTransport() {
  return process.env.EMAIL_TRANSPORT === 'file' && !process.env.VERCEL ? 'file' : 'resend';
}

export function emailEnabled() {
  const from = (process.env.EMAIL_FROM || '').trim();
  if (!from) return false;
  return emailTransport() === 'file' || Boolean((process.env.RESEND_API_KEY || '').trim());
}

export function fromHeader() {
  const from = (process.env.EMAIL_FROM || '').trim();
  if (from.includes('<')) return from;
  return `${SITE_NAME.replace(/["<>\\]/g, '')} <${from}>`;
}

// Pause between sends in the daily digest run. Resend's default API limit is 2 requests a second.
export function sendIntervalMs() {
  if (emailTransport() === 'file') return 0;
  const n = Number(process.env.EMAIL_SEND_INTERVAL_MS);
  return Number.isFinite(n) && n >= 0 ? n : 550;
}

// message: { to, subject, text, html, headers?, idempotencyKey? }
// Returns { ok, status, id?, error? }. Never throws; never logs the address.
export async function sendEmail(message) {
  if (!emailEnabled()) return { ok: false, status: 0, error: 'email is not configured' };
  const payload = {
    from: fromHeader(),
    to: [message.to],
    subject: message.subject,
    text: message.text,
    html: message.html,
    ...(message.headers && Object.keys(message.headers).length ? { headers: message.headers } : {}),
  };
  if (emailTransport() === 'file') return writeToOutbox(payload, message.idempotencyKey);

  try {
    const res = await fetch(RESEND_URL, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${process.env.RESEND_API_KEY.trim()}`,
        'content-type': 'application/json',
        ...(message.idempotencyKey ? { 'idempotency-key': String(message.idempotencyKey).slice(0, 256) } : {}),
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.id) return { ok: true, status: res.status, id: data.id };
    const reason = clip(data.message || data.name || `HTTP ${res.status}`);
    console.error('email send failed', res.status, reason);
    return { ok: false, status: res.status, error: reason };
  } catch (err) {
    console.error('email send failed', err.name);
    return { ok: false, status: 0, error: err.name === 'TimeoutError' ? 'timed out' : 'could not connect' };
  }
}

const clip = (s) => String(s).replace(/\S+@\S+/g, '[address]').slice(0, 200);

async function writeToOutbox(payload, idempotencyKey) {
  const dir = process.env.EMAIL_OUTBOX || join(tmpdir(), '351watch-outbox');
  const id = `${new Date().toISOString().replace(/[:.]/g, '-')}-${randomBytes(4).toString('hex')}`;
  try {
    await mkdir(dir, { recursive: true });
    await writeFile(join(dir, `${id}.json`), JSON.stringify({ id, ...payload, idempotency_key: idempotencyKey || null }, null, 2));
    if (payload.html) await writeFile(join(dir, `${id}.html`), payload.html);
    if (payload.text) await writeFile(join(dir, `${id}.txt`), payload.text);
    return { ok: true, status: 200, id };
  } catch (err) {
    console.error('email outbox write failed', err.message);
    return { ok: false, status: 0, error: 'outbox write failed' };
  }
}
