// Watchlist logic shared by watchlists.js, feed.js, email.js, cron/dispatch.js, checkout.js and
// stripe-webhook.js: the data contract (ARCHITECTURE.md), validation (including the free area),
// item matching and webhook message formats.
import { randomBytes } from 'node:crypto';
import { clean, readJSON, writeJSON } from './_store.js';

export const CANONICAL_BASE = 'https://351watch-sulmusic2-4637s-projects.vercel.app';

// The product name in messages, feeds and emails: one default here, or the SITE_NAME env var.
// Templates use this constant, never a literal name.
export const SITE_NAME = clean(process.env.SITE_NAME || '', 60) || 'Agenda Ahead';

export const TOPICS = {
  battery_storage: 'Battery storage',
  solar: 'Solar',
  data_center: 'Data centers',
  moratorium: 'Moratoria',
  clean_energy_siting: 'Consolidated permit',
  '40b_comprehensive_permit': '40B housing',
  wireless_telecom: 'Wireless / cell towers',
  zoning_amendment: 'Zoning amendments',
  wetlands_filing: 'Wetlands filings (MassDEP)',
};

export const MAX_TOWNS = 200;
export const MAX_BODY_BYTES = 16 * 1024;
const ID_RE = /^[A-Za-z0-9_-]{24,64}$/;

export const newId = () => randomBytes(18).toString('base64url'); // 24 URL-safe chars, 144 bits
export const validId = (id) => typeof id === 'string' && ID_RE.test(id);
export const blobPath = (id) => `watchlists/${id}.json`;

export const loadWatchlist = (id) => (validId(id) ? readJSON(blobPath(id)) : Promise.resolve(null));
export const saveWatchlist = (wl) => writeJSON(blobPath(wl.id), wl);

// Each watchlist has two keys. Its id is the private key that can edit or delete it. Its feed_id
// is a read-only key used in feed, calendar and share links, so publishing a calendar link never
// hands out edit rights. feeds/<feed_id>.json points back to the watchlist.
export const feedIndexPath = (feedId) => `feeds/${feedId}.json`;

export async function ensureFeedId(wl) {
  if (wl.feed_id) return false;
  wl.feed_id = newId();
  await writeJSON(feedIndexPath(wl.feed_id), { watchlist_id: wl.id });
  await saveWatchlist(wl);
  return true;
}

// Resolve an id from a link: the private key gives { wl, readonly: false }, a feed key { wl, readonly: true }.
export async function resolveWatchlist(id) {
  if (!validId(id)) return { wl: null, readonly: true };
  const own = await readJSON(blobPath(id));
  if (own) return { wl: own, readonly: false };
  const ref = await readJSON(feedIndexPath(id));
  if (!ref?.watchlist_id || !validId(ref.watchlist_id)) return { wl: null, readonly: true };
  const wl = await readJSON(blobPath(ref.watchlist_id));
  return wl && wl.feed_id === id ? { wl, readonly: true } : { wl: null, readonly: true };
}

export const shareId = (wl) => wl.feed_id || wl.id;

export function townSlug(name) {
  return String(name).toLowerCase().replace(/['’]/g, '').replace(/\s+/g, '-');
}

// ---------- origins ----------

function requestOrigin(req) {
  const host = String(req.headers['x-forwarded-host'] || req.headers.host || '').split(',')[0].trim();
  if (!/^[a-z0-9.-]+(:\d{1,5})?$/i.test(host)) return null;
  const proto = String(req.headers['x-forwarded-proto'] || 'https').split(',')[0].trim();
  return `${proto === 'http' ? 'http' : 'https'}://${host}`;
}

// Base URL used in links we send out (feeds, webhooks, Stripe redirects).
export function publicBase(req) {
  return (process.env.PUBLIC_BASE_URL || requestOrigin(req) || CANONICAL_BASE).replace(/\/$/, '');
}

function dataOrigins(req) {
  const list = [];
  if (process.env.DATA_ORIGIN) list.push(process.env.DATA_ORIGIN);
  const own = requestOrigin(req);
  if (own) list.push(own);
  if (process.env.VERCEL_URL) list.push(`https://${process.env.VERCEL_URL}`);
  if (process.env.VERCEL_PROJECT_PRODUCTION_URL) list.push(`https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`);
  list.push(CANONICAL_BASE);
  return [...new Set(list.map((o) => o.replace(/\/$/, '')))];
}

// ---------- published data (cached per instance) ----------

const cache = new Map();
const ttlMs = () => Number(process.env.HITS_CACHE_SECONDS ?? 300) * 1000;

async function fetchStatic(req, path) {
  const hit = cache.get(path);
  if (hit && Date.now() - hit.at < ttlMs()) return hit.data;
  let lastError;
  for (const origin of dataOrigins(req)) {
    try {
      const res = await fetch(`${origin}${path}`, { signal: AbortSignal.timeout(8000), headers: { accept: 'application/json' } });
      if (!res.ok) throw new Error(`${path} from ${origin}: HTTP ${res.status}`);
      const data = await res.json();
      cache.set(path, { at: Date.now(), data });
      return data;
    } catch (err) {
      lastError = err;
    }
  }
  if (hit) return hit.data; // stale beats nothing
  throw lastError || new Error(`could not load ${path}`);
}

export async function loadHits(req) {
  const doc = await fetchStatic(req, '/data/hits_current.json');
  return { ...doc, hits: Array.isArray(doc.hits) ? doc.hits : [] };
}

// /data/lines.json: the site's own sentence for each item, and each agenda's time, place and cancellation
// ({at: {url: [time, place, cancelled]}}), so a feed says what the page says. Missing: the feed falls back to raw text.
export async function loadLines(req) {
  try {
    const doc = await fetchStatic(req, '/data/lines.json');
    return doc && typeof doc === 'object' ? doc : {};
  } catch (err) {
    console.error('lines unavailable', err.message);
    return {};
  }
}

// Valid towns: the site's town index plus any town present in the current data.
export async function loadTownIndex(req, hitsDoc) {
  let towns = [];
  try {
    const doc = await fetchStatic(req, '/data/towns.json');
    towns = Array.isArray(doc.towns) ? doc.towns : [];
  } catch (err) {
    console.error('town index unavailable', err.message);
  }
  const ids = new Set(towns.map((t) => t.id));
  for (const h of hitsDoc?.hits || []) ids.add(`${h.state}:${h.town}`);
  return ids;
}

// Neighbor lists for the free area (data/neighbors.json, built by tools/neighbors.py).
// Returns the map, or null when the file can't be loaded (callers answer 503 then).
export async function loadNeighbors(req) {
  try {
    const doc = await fetchStatic(req, '/data/neighbors.json');
    return doc && typeof doc === 'object' ? doc : null;
  } catch (err) {
    console.error('neighbor data unavailable', err.message);
    return null;
  }
}

// The free area around a home town: the town itself plus every town whose boundary touches it.
export function areaOf(neighbors, home) {
  const list = Array.isArray(neighbors?.[home]) ? neighbors[home] : [];
  return new Set([home, ...list]);
}

export function topicSet(hitsDoc) {
  const set = new Set(Object.keys(TOPICS));
  for (const h of hitsDoc?.hits || []) for (const t of h.topics || []) set.add(t);
  return set;
}

// ---------- matching ----------

export function matchItems(hits, wl) {
  const towns = new Set(wl.towns || []);
  const topics = new Set(wl.topics || []);
  return hits
    .filter((h) => towns.has(`${h.state}:${h.town}`) && (h.topics || []).some((t) => topics.has(t)))
    .sort((a, b) =>
      (b.first_seen || '').localeCompare(a.first_seen || '') ||
      (b.meeting_date || '').localeCompare(a.meeting_date || '') ||
      String(a.id).localeCompare(String(b.id)));
}

export function publicItem(h, base) {
  return {
    id: h.id,
    state: h.state,
    town: h.town,
    county: h.county || null,
    board: h.board,
    board_key: h.board_key,
    meeting_date: h.meeting_date || null,
    topics: h.topics || [],
    topic_labels: (h.topics || []).map((t) => TOPICS[t] || t),
    snippet: h.snippet,
    source_url: h.source_url,
    listing_url: h.listing_url || null,
    document_title: h.document_title || null,
    first_seen: h.first_seen,
    days_before_meeting: typeof h.days_before_meeting === 'number' ? h.days_before_meeting : null,
    source: h.source || 'agenda',
    town_url: `${base}/${String(h.state).toLowerCase()}/${townSlug(h.town)}`,
  };
}

export function fmtDate(iso) {
  if (!iso) return 'date not listed';
  const d = new Date(`${iso}T12:00:00Z`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
}

// ---------- validation ----------

const WEBHOOK_HOSTS = [
  { kind: 'slack', test: (h) => h === 'hooks.slack.com' },
  { kind: 'teams', test: (h) => h === 'outlook.office.com' || h.endsWith('.webhook.office.com') },
  // Teams "Workflows" (Power Automate) webhooks, which replaced the retired Office 365 connectors.
  { kind: 'teams_workflow', test: (h) => h.endsWith('.logic.azure.com') || h.endsWith('.api.powerplatform.com') },
  { kind: 'discord', test: (h, path) => h === 'discord.com' && path.startsWith('/api/webhooks/') },
];
export const WEBHOOK_FORMATS = new Set(['auto', 'json']);

export function parseWebhook(raw) {
  const value = typeof raw === 'string' ? raw.trim() : '';
  if (!value) return { url: null };
  if (value.length > 1000) return { error: 'That webhook URL is too long.' };
  let u;
  try {
    u = new URL(value);
  } catch {
    return { error: 'That webhook URL is not a valid URL.' };
  }
  if (u.protocol !== 'https:') return { error: 'Webhook URLs must start with https://.' };
  if (u.username || u.password || (u.port && u.port !== '443')) return { error: 'That webhook URL is not supported.' };
  const host = u.hostname.toLowerCase();
  const match = WEBHOOK_HOSTS.find((h) => h.test(host, u.pathname));
  if (!match) {
    return { error: 'Use a Slack, Discord or Microsoft Teams (Workflows) webhook URL.' };
  }
  u.hash = '';
  return { url: u.toString(), kind: match.kind };
}

export function webhookKind(webhook) {
  if (!webhook?.url) return null;
  if (webhook.format === 'json') return 'json';
  return parseWebhook(webhook.url).kind || 'json';
}

function maskUrl(url) {
  try {
    const u = new URL(url);
    const tail = u.pathname.replace(/\/$/, '').slice(-4);
    return `${u.hostname}/…${tail}`;
  } catch {
    return 'hidden';
  }
}

function toList(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === 'string') return value.split(',');
  return [];
}

export const FREE_AREA_MESSAGE =
  'Free alerts cover one town and the towns next to it. Need more places? Use the contact form on the How it works page.';

// Returns { value, errors, code }. With `partial` (PATCH), absent fields are left out of `value`
// and `current` is the stored watchlist. code is 'free_area' when the towns go past the free area,
// or 'area_unavailable' when the neighbor data could not be loaded.
export function validateConfig(body, { towns, topics, neighbors }, { partial = false, current = null } = {}) {
  const errors = {};
  const value = {};
  let code = null;

  if (!partial || 'name' in body) value.name = clean(body.name, 80);

  // home_town: required on new watchlists; on an update an empty value means "unchanged".
  const home = clean(body.home_town, 80);
  if (home) {
    if (!towns.has(home)) errors.home_town = `Unknown town: ${home}.`;
    else value.home_town = home;
  } else if (!partial) {
    errors.home_town = 'Choose your town.';
  }

  if (!partial || 'towns' in body) {
    const list = [...new Set(toList(body.towns).map((t) => clean(t, 80)).filter(Boolean))];
    const unknown = list.filter((t) => !towns.has(t));
    if (!list.length) errors.towns = 'Choose at least one town.';
    else if (list.length > MAX_TOWNS) errors.towns = `Choose up to ${MAX_TOWNS} towns.`;
    else if (unknown.length) errors.towns = `Unknown town: ${unknown.slice(0, 3).join(', ')}.`;
    value.towns = list;
  }

  if (!partial || 'topics' in body) {
    const list = [...new Set(toList(body.topics).map((t) => clean(t, 60)).filter(Boolean))];
    const unknown = list.filter((t) => !topics.has(t));
    if (!list.length) errors.topics = 'Choose at least one topic.';
    else if (unknown.length) errors.topics = `Unknown topic: ${unknown.slice(0, 3).join(', ')}.`;
    value.topics = list;
  }

  if (!partial || 'webhook_url' in body) {
    const parsed = parseWebhook(body.webhook_url);
    if (parsed.error) errors.webhook_url = parsed.error;
    else value.webhook_url = parsed.url;
  }
  if (!partial || 'webhook_format' in body) {
    value.webhook_format = WEBHOOK_FORMATS.has(body.webhook_format) ? body.webhook_format : 'auto';
  }

  if (!errors.towns && !errors.home_town && (value.towns || value.home_town)) {
    const area = checkArea(value, current, neighbors);
    if (area === 'unavailable') code = 'area_unavailable';
    else if (area === 'outside') {
      code = 'free_area';
      errors.towns = FREE_AREA_MESSAGE;
    }
  }

  return { value, errors, code };
}

// The free limit: a watchlist's towns lie inside one area, a home town plus its neighbors.
// - New watchlist: every town is in area(home_town).
// - Home town unchanged: towns already on the list stay (even if the neighbor data changes later);
//   added towns must be in the area.
// - Home town changed: the whole list must fit the new area, so a list can't collect areas.
// - Watchlist from before the limit (no home_town): removing towns is always allowed. Adding a town
//   makes it a one-area list: the whole list must fit area(home_town), using the home_town sent or,
//   without one, the first town on the list whose area holds them all (saved as home_town).
// Returns 'ok', 'outside' or 'unavailable'. May set value.home_town on an old list.
function checkArea(value, current, neighbors) {
  const list = value.towns || current?.towns || [];
  const before = new Set(current?.towns || []);
  const added = list.filter((t) => !before.has(t));
  const fits = (home) => {
    const area = areaOf(neighbors, home);
    return list.every((t) => area.has(t));
  };

  const homeChanged = Boolean(value.home_town) && value.home_town !== current?.home_town;
  if (current && !homeChanged && !added.length) return 'ok'; // removals and reorders need no neighbor data
  if (!neighbors) return 'unavailable';

  if (!current) return fits(value.home_town) ? 'ok' : 'outside';
  if (current.home_town && (!value.home_town || value.home_town === current.home_town)) {
    const area = areaOf(neighbors, current.home_town);
    return added.every((t) => area.has(t)) ? 'ok' : 'outside';
  }
  if (value.home_town) return fits(value.home_town) ? 'ok' : 'outside';
  const inferred = list.find((t) => fits(t));
  if (!inferred) return 'outside';
  value.home_town = inferred;
  return 'ok';
}

// The private view (private key only). `email` comes from _email_alerts.js emailView(); the
// read-only view below never includes it.
export function publicView(wl, base, { email } = {}) {
  const kind = webhookKind(wl.webhook);
  return {
    readonly: false,
    id: wl.id,
    name: wl.name || '',
    home_town: wl.home_town || null,
    grandfathered: !wl.home_town, // made before the one-area limit; can drop towns, not add outside one area
    towns: wl.towns,
    topics: wl.topics,
    webhook: wl.webhook?.url
      ? { configured: true, kind, format: wl.webhook.format || 'auto', host: new URL(wl.webhook.url).hostname, masked: maskUrl(wl.webhook.url) }
      : { configured: false },
    email: email || { configured: false, available: false, confirmed: false, masked: null },
    plan: wl.plan || 'beta',
    created_at: wl.created_at,
    updated_at: wl.updated_at,
    last_dispatched_at: wl.last_dispatched_at || null,
    last_delivery: wl.last_delivery || null,
    links: {
      page: `${base}/w/${wl.id}`,
      ...feedLinks(wl, base),
    },
  };
}

// Feed and share links carry only the read-only key.
function feedLinks(wl, base) {
  const fid = shareId(wl);
  return {
    share: `${base}/w/${fid}`,
    json: `${base}/api/feed?id=${fid}&format=json`,
    rss: `${base}/api/feed?id=${fid}&format=rss`,
    ics: `${base}/api/feed?id=${fid}&format=ics`,
  };
}

// What a read-only link may see: no private key, no webhook or email details, no delivery log.
export function readonlyView(wl, base) {
  return {
    readonly: true,
    name: wl.name || '',
    home_town: wl.home_town || null,
    towns: wl.towns,
    topics: wl.topics,
    created_at: wl.created_at,
    updated_at: wl.updated_at,
    links: feedLinks(wl, base),
  };
}

// ---------- webhook messages ----------

const slackEsc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const slackUrl = (u) => String(u).replace(/\|/g, '%7C').replace(/>/g, '%3E');
const mdEsc = (s) => String(s ?? '').replace(/([\\`*_[\]<>])/g, '\\$1');
const topicText = (h) => (h.topics || []).map((t) => TOPICS[t] || t).join(', ');

export function messageTitle(wl) {
  return `${SITE_NAME}: ${wl.name || 'your watchlist'}`;
}

export function buildPayload(kind, { wl, items, more = 0, link, intro, test = false }) {
  const title = messageTitle(wl);
  const total = items.length + more;
  const lead = intro || `${total} new agenda item${total === 1 ? '' : 's'} for your towns and topics.`;

  if (kind === 'slack') {
    const blocks = [
      { type: 'header', text: { type: 'plain_text', text: title.slice(0, 150) } },
      { type: 'context', elements: [{ type: 'mrkdwn', text: slackEsc(lead) }] },
      ...items.map((h) => ({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*${slackEsc(h.town)}* · ${slackEsc(h.board)} · ${slackEsc(fmtDate(h.meeting_date))}\n_${slackEsc(topicText(h))}_\n>${slackEsc(h.snippet)}\n<${slackUrl(h.source_url)}|Open agenda>`.slice(0, 2900),
        },
      })),
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: more ? `…and ${more} more. <${slackUrl(link)}|See them all on ${slackEsc(SITE_NAME)}>` : `<${slackUrl(link)}|Open this watchlist on ${slackEsc(SITE_NAME)}>`,
        },
      },
    ];
    return { text: `${title}: ${lead}`, blocks, unfurl_links: false, unfurl_media: false };
  }

  if (kind === 'teams') {
    const lines = items.map(
      (h) => `**${mdEsc(h.town)}** · ${mdEsc(h.board)} · ${fmtDate(h.meeting_date)}  \n_${mdEsc(topicText(h))}_  \n${mdEsc(h.snippet)} [Open agenda](${h.source_url})`,
    );
    if (more) lines.push(`…and ${more} more. [See them all on ${mdEsc(SITE_NAME)}](${link})`);
    return {
      '@type': 'MessageCard',
      '@context': 'https://schema.org/extensions',
      summary: title,
      themeColor: '1F5F4A',
      title,
      text: lead,
      sections: lines.length ? [{ text: lines.join('\n\n') }] : [],
      potentialAction: [{ '@type': 'OpenUri', name: 'Open watchlist', targets: [{ os: 'default', uri: link }] }],
    };
  }

  if (kind === 'teams_workflow') {
    const body = [
      { type: 'TextBlock', text: title, weight: 'Bolder', size: 'Medium', wrap: true },
      { type: 'TextBlock', text: lead, isSubtle: true, wrap: true, spacing: 'Small' },
      ...items.map((h) => ({
        type: 'Container',
        separator: true,
        items: [
          { type: 'TextBlock', text: `**${mdEsc(h.town)}** · ${mdEsc(h.board)} · ${fmtDate(h.meeting_date)}`, wrap: true },
          { type: 'TextBlock', text: topicText(h), isSubtle: true, spacing: 'None', wrap: true },
          { type: 'TextBlock', text: `${mdEsc(h.snippet)} [Open agenda](${h.source_url})`, wrap: true, spacing: 'Small' },
        ],
      })),
    ];
    if (more) body.push({ type: 'TextBlock', text: `…and ${more} more.`, wrap: true, separator: true });
    return {
      type: 'message',
      attachments: [
        {
          contentType: 'application/vnd.microsoft.card.adaptive',
          contentUrl: null,
          content: {
            $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
            type: 'AdaptiveCard',
            version: '1.4',
            body,
            actions: [{ type: 'Action.OpenUrl', title: more ? `See them all on ${SITE_NAME}` : 'Open watchlist', url: link }],
          },
        },
      ],
    };
  }

  if (kind === 'discord') {
    const head = `**${title}**\n${lead}\n`;
    const footer = (n) => (n ? `…and ${n} more: <${link}>` : `Watchlist: <${link}>`);
    let content = head;
    let shown = 0;
    for (const h of items) {
      const line = `\n• **${mdEsc(h.town)}** · ${mdEsc(h.board)} · ${fmtDate(h.meeting_date)} (${topicText(h)})\n> ${mdEsc(h.snippet).slice(0, 220)}\n<${h.source_url}>\n`;
      if ((content + line + footer(more + items.length - shown - 1)).length > 1950) break;
      content += line;
      shown += 1;
    }
    content += `\n${footer(more + items.length - shown)}`;
    return { username: SITE_NAME.slice(0, 80), content: content.slice(0, 2000), allowed_mentions: { parse: [] } };
  }

  // Generic JSON
  return {
    source: '351watch',
    type: test ? 'test' : 'new_items',
    watchlist: { id: wl.id, name: wl.name || '', url: link },
    message: lead,
    count: items.length,
    more,
    items: items.map((h) => publicItem(h, new URL(link).origin)),
  };
}

export async function postWebhook(url, payload) {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'user-agent': '351WatchBot/1.0 (+https://351watch-sulmusic2-4637s-projects.vercel.app/proof)' },
      body: JSON.stringify(payload),
      redirect: 'manual',
      signal: AbortSignal.timeout(10000),
    });
    await res.text().catch(() => '');
    return { ok: res.status >= 200 && res.status < 300, status: res.status };
  } catch (err) {
    return { ok: false, status: 0, error: err.name === 'TimeoutError' ? 'timed out' : 'could not connect' };
  }
}
