// Stores corrections, data-removal requests and general messages as private blobs.
import { EMAIL, clean, readBody, save, postOnly } from './_store.js';

const KINDS = new Set(['correction', 'removal', 'message']);

export default async function handler(req, res) {
  if (!postOnly(req, res)) return;
  const body = readBody(req);
  if (clean(body.website, 200)) return res.status(200).json({ ok: true });

  const email = clean(body.email, 254).toLowerCase();
  const message = clean(body.message, 2000);
  if (!EMAIL.test(email) || !message) {
    return res.status(400).json({ ok: false, error: 'Please include a valid email address and a message.' });
  }

  try {
    await save('contact', {
      email,
      kind: KINDS.has(body.kind) ? body.kind : 'message',
      message,
      created_at: new Date().toISOString(),
    });
  } catch (err) {
    console.error('contact write failed', err);
    return res.status(500).json({ ok: false, error: 'Something went wrong. Please try again.' });
  }
  return res.status(200).json({ ok: true });
}
