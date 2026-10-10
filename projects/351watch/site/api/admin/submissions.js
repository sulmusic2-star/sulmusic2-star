// Owner-only export of earlier waitlist signups, contact messages and a watchlist count (bearer ADMIN_TOKEN).
import { timingSafeEqual } from 'node:crypto';
import { blob, listPathnames } from '../_store.js';

function authorized(req) {
  const expected = process.env.ADMIN_TOKEN || '';
  const header = req.headers.authorization || '';
  const given = header.startsWith('Bearer ') ? header.slice(7) : '';
  if (!expected || given.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(given), Buffer.from(expected));
}

async function readAll(prefix) {
  const { list, get } = await blob();
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
  return records.filter(Boolean).sort((a, b) => String(a.created_at).localeCompare(String(b.created_at)));
}

export default async function handler(req, res) {
  if (!authorized(req)) return res.status(401).json({ ok: false, error: 'Unauthorized' });
  res.setHeader('Cache-Control', 'no-store');
  const [waitlist, contact, watchlists] = await Promise.all([readAll('waitlist'), readAll('contact'), listPathnames('watchlists/')]);
  return res.status(200).json({
    ok: true,
    watchlist_count: watchlists.length,
    waitlist_count: waitlist.length,
    unique_emails: new Set(waitlist.map((s) => s.email).filter(Boolean)).size,
    waitlist,
    contact,
  });
}
