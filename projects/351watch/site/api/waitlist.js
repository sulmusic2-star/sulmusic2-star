// Stores one waitlist signup per private blob. Emails are never exposed publicly.
import { EMAIL, clean, readBody, save, postOnly } from './_store.js';

const ROLES = new Set(['developer', 'attorney', 'consultant', 'municipal', 'advocacy', 'journalist', 'other']);

export default async function handler(req, res) {
  if (!postOnly(req, res)) return;
  const body = readBody(req);

  // Honeypot field: real people never see or fill it.
  if (clean(body.website, 200)) return res.status(200).json({ ok: true });

  const email = clean(body.email, 254).toLowerCase();
  if (!EMAIL.test(email)) {
    return res.status(400).json({ ok: false, error: 'Please enter a valid email address.' });
  }

  const record = {
    email,
    role: ROLES.has(body.role) ? body.role : 'other',
    organization: clean(body.organization, 120),
    towns: clean(body.towns, 500),
    wants: clean(body.wants, 500),
    source: clean(body.source, 60) || 'tracker',
    created_at: new Date().toISOString(),
  };

  try {
    await save('waitlist', record);
  } catch (err) {
    console.error('waitlist write failed', err);
    return res.status(500).json({ ok: false, error: 'Something went wrong. Please try again.' });
  }
  return res.status(200).json({ ok: true });
}
