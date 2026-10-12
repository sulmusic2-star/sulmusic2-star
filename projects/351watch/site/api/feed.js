// GET /api/feed?id=<watchlist>&format=json|rss|ics
// Items matching the watchlist's towns and topics from /data/hits_current.json, newest first.
// The iCalendar feed has one all-day event per upcoming meeting with matched items.
import { createHash } from 'node:crypto';
import { allow, noStore } from './_store.js';
import { SITE_NAME, TOPICS, fmtDate, loadHits, matchItems, publicBase, publicItem, resolveWatchlist, shareId } from './_watch.js';

const RSS_LIMIT = 100;
const JSON_LIMIT = 500;

const xml = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[c]);
const html = xml;
const rfc822 = (iso) => new Date(iso || Date.now()).toUTCString();
const topicText = (h) => (h.topics || []).map((t) => TOPICS[t] || t).join(', ');

function easternToday() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}

function describe(wl) {
  const towns = wl.towns.map((t) => t.split(':').slice(1).join(':'));
  const shown = towns.slice(0, 6).join(', ') + (towns.length > 6 ? ` and ${towns.length - 6} more` : '');
  return `Agenda items on ${wl.topics.map((t) => TOPICS[t] || t).join(', ')} in ${shown}.`;
}

function rss(wl, items, base, feedUrl, generated) {
  const entries = items.slice(0, RSS_LIMIT).map((h) => {
    const town = `${h.town}${h.state && h.state !== 'MA' ? `, ${h.state}` : ''}`;
    const body =
      `<p>${html(h.snippet)}</p>` +
      `<p>${html(town)} · ${html(h.board)} · meeting ${html(fmtDate(h.meeting_date))}</p>` +
      `<p><a href="${html(h.source_url)}">Open the agenda</a> · <a href="${html(publicItem(h, base).town_url)}">${html(h.town)} on ${html(SITE_NAME)}</a></p>`;
    return `<item>
<title>${xml(`${town}: ${h.board}, ${fmtDate(h.meeting_date)} (${topicText(h)})`)}</title>
<link>${xml(h.source_url)}</link>
<guid isPermaLink="false">351watch-${xml(h.id)}</guid>
<pubDate>${rfc822(h.first_seen)}</pubDate>
${(h.topics || []).map((t) => `<category>${xml(TOPICS[t] || t)}</category>`).join('')}
<description>${xml(body)}</description>
</item>`;
  });
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>${xml(`${SITE_NAME}: ${wl.name || 'alerts'}`)}</title>
<link>${xml(`${base}/w/${shareId(wl)}`)}</link>
<atom:link href="${xml(feedUrl)}" rel="self" type="application/rss+xml"/>
<description>${xml(describe(wl))}</description>
<language>en-us</language>
<lastBuildDate>${rfc822(generated)}</lastBuildDate>
<ttl>360</ttl>
${entries.join('\n')}
</channel>
</rss>
`;
}

// ---------- iCalendar ----------

const icsText = (s) => String(s ?? '').replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');

function fold(line) {
  const bytes = Buffer.from(line, 'utf8');
  if (bytes.length <= 75) return line;
  const parts = [];
  let current = '';
  let size = 0;
  for (const ch of line) {
    const n = Buffer.byteLength(ch, 'utf8');
    if (size + n > (parts.length ? 74 : 75)) {
      parts.push(current);
      current = '';
      size = 0;
    }
    current += ch;
    size += n;
  }
  parts.push(current);
  return parts.join('\r\n ');
}

const icsDate = (iso) => iso.replace(/-/g, '');
function nextDay(iso) {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}
const stamp = (iso) => new Date(iso || Date.now()).toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');

function ics(wl, items, base, generated) {
  const today = easternToday();
  const meetings = new Map();
  for (const h of items) {
    if (!h.meeting_date || h.meeting_date < today) continue;
    const key = `${h.state}|${h.town}|${h.board}|${h.meeting_date}`;
    if (!meetings.has(key)) meetings.set(key, []);
    meetings.get(key).push(h);
  }
  const events = [...meetings.entries()]
    .sort((a, b) => a[1][0].meeting_date.localeCompare(b[1][0].meeting_date) || a[0].localeCompare(b[0]))
    .map(([key, group]) => {
      const h = group[0];
      const wanted = new Set(wl.topics);
      const topics = [...new Set(group.flatMap((g) => g.topics || []))].filter((t) => wanted.has(t)).map((t) => TOPICS[t] || t);
      const agendas = [...new Set(group.map((g) => g.source_url))];
      const description = [
        ...group.map((g) => `• ${g.snippet}`),
        '',
        ...agendas.map((u) => `Agenda: ${u}`),
        `Alerts page: ${base}/w/${shareId(wl)}`,
        'Confirm the time and place with the town; agendas can change.',
      ].join('\n');
      const uid = createHash('sha1').update(`${wl.id}|${key}`).digest('hex').slice(0, 20);
      return [
        'BEGIN:VEVENT',
        `UID:${uid}@351watch`,
        `DTSTAMP:${stamp(generated)}`,
        `DTSTART;VALUE=DATE:${icsDate(h.meeting_date)}`,
        `DTEND;VALUE=DATE:${icsDate(nextDay(h.meeting_date))}`,
        `SUMMARY:${icsText(`${h.town} ${h.board}: ${topics.join(', ')}`)}`,
        `LOCATION:${icsText(`${h.town}, ${h.state}`)}`,
        `DESCRIPTION:${icsText(description)}`,
        `URL:${agendas[0]}`,
        'TRANSP:TRANSPARENT',
        'END:VEVENT',
      ];
    });
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    `PRODID:-//${icsText(SITE_NAME)}//Agenda alerts//EN`,
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    `X-WR-CALNAME:${icsText(`${SITE_NAME}: ${wl.name || 'alerts'}`)}`,
    `X-WR-CALDESC:${icsText(describe(wl))}`,
    'X-PUBLISHED-TTL:PT6H',
    'REFRESH-INTERVAL;VALUE=DURATION:PT6H',
    ...events.flat(),
    'END:VCALENDAR',
  ];
  return lines.map(fold).join('\r\n') + '\r\n';
}

export default async function handler(req, res) {
  if (!allow(req, res, ['GET', 'HEAD'])) return;
  const id = typeof req.query?.id === 'string' ? req.query.id : '';
  const format = ['json', 'rss', 'ics'].includes(req.query?.format) ? req.query.format : 'json';

  try {
    const { wl } = await resolveWatchlist(id);
    if (!wl) {
      noStore(res);
      return res.status(404).json({ ok: false, error: 'These alerts were not found.' });
    }
    const doc = await loadHits(req);
    const base = publicBase(req);
    const items = matchItems(doc.hits, wl);
    // Feed readers get a short shared cache; the watchlist page asks for fresh=1 so edits show at once.
    res.setHeader('Cache-Control', req.query?.fresh === '1' ? 'no-store' : 'public, max-age=300, s-maxage=300');

    if (format === 'rss') {
      res.setHeader('Content-Type', 'application/rss+xml; charset=utf-8');
      return res.status(200).send(rss(wl, items, base, `${base}/api/feed?id=${shareId(wl)}&format=rss`, doc.generated));
    }
    if (format === 'ics') {
      res.setHeader('Content-Type', 'text/calendar; charset=utf-8');
      res.setHeader('Content-Disposition', 'inline; filename="351watch.ics"');
      return res.status(200).send(ics(wl, items, base, doc.generated));
    }
    return res.status(200).json({
      ok: true,
      watchlist: { name: wl.name || '', towns: wl.towns, topics: wl.topics, page: `${base}/w/${shareId(wl)}` },
      generated: doc.generated || null,
      window: doc.window || null,
      count: items.length,
      items: items.slice(0, JSON_LIMIT).map((h) => publicItem(h, base)),
    });
  } catch (err) {
    console.error('feed failed', err);
    noStore(res);
    return res.status(503).json({ ok: false, error: 'The data is temporarily unavailable. Try again shortly.' });
  }
}
