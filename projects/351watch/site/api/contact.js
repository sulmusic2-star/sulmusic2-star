// Stores corrections, data-removal requests and general messages as private blobs.
// The form collects no email address (email alerts are separate: see _email_alerts.js).
import { bodySize, clean, noStore, readBody, save, postOnly, throttled } from './_store.js';

const KINDS = new Set(['correction', 'removal', 'message']);

export default async function handler(req, res) {
  noStore(res);
  if (!postOnly(req, res)) return;
  if (bodySize(req) > 8192) return res.status(413).json({ ok: false, error: 'Message too long.' });
  const body = readBody(req);
  if (clean(body.website, 200)) return res.status(200).json({ ok: true });
  if (throttled(req, 'contact', 10, 60 * 60 * 1000)) {
    return res.status(429).json({ ok: false, error: 'Too many messages from this network. Try again later.' });
  }

  const message = clean(body.message, 2000);
  if (message.length < 3) return res.status(400).json({ ok: false, error: 'Please write a message.' });

  try {
    await save('contact', {
      kind: KINDS.has(body.kind) ? body.kind : 'message',
      message,
      page: clean(body.page, 200),
      created_at: new Date().toISOString(),
    });
  } catch (err) {
    console.error('contact write failed', err);
    return res.status(500).json({ ok: false, error: 'Something went wrong. Please try again.' });
  }
  return res.status(200).json({ ok: true });
}
