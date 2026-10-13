// GET /api/status: which optional features this deployment has on, for the pages to show or hide them.
//   { ok: true, email_alerts: true|false }   email_alerts: RESEND_API_KEY and EMAIL_FROM are set
import { allow, noStore } from './_store.js';
import { emailEnabled } from './_email.js';

export default function handler(req, res) {
  noStore(res);
  if (!allow(req, res, ['GET', 'HEAD'])) return;
  return res.status(200).json({ ok: true, email_alerts: emailEnabled() });
}
