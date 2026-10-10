// Owner-only export of waitlist signups and contact messages (bearer ADMIN_TOKEN).
import { list, get } from '@vercel/blob';
import { timingSafeEqual } from 'node:crypto';

function authorized(req) {
  const expected = process.env.ADMIN_TOKEN || '';
  const header = req.headers.authorization || '';
  const given = header.startsWith('Bearer ') ? header.slice(7) : '';
  if (!expected || given.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(given), Buffer.from(expected));
}

async function readAll(prefix) {
  const blobs = [];
  let cursor;
  do {
    const page = await list({ prefix: `${prefix}/`, cursor, limit: 1000 });
    blobs.push(...page.blobs);
    cursor = page.hasMore ? page.cursor : undefined;
  } while (cursor);

  const records = await Promise.all(
    blobs.map(async (b) => {
      const result = await get(b.pathname, { access: 'private', useCache: false });
      if (!result || result.statusCode !== 200) return null;
      return JSON.parse(await new Response(result.stream).text());
    }),
  );
  return records.filter(Boolean).sort((a, b) => a.created_at.localeCompare(b.created_at));
}

export default async function handler(req, res) {
  if (!authorized(req)) return res.status(401).json({ ok: false, error: 'Unauthorized' });
  const [waitlist, contact] = await Promise.all([readAll('waitlist'), readAll('contact')]);
  return res.status(200).json({
    ok: true,
    waitlist_count: waitlist.length,
    unique_emails: new Set(waitlist.map((s) => s.email)).size,
    waitlist,
    contact,
  });
}
