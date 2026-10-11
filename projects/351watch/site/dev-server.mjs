#!/usr/bin/env node
// Local dev server for 351 Watch (no dependencies). Serves the built static site the way Vercel
// does (cleanUrls, vercel.json rewrites and headers, including the CSP) and runs api/*.js handlers.
//
//   python3 build.py && node site/dev-server.mjs          -> http://127.0.0.1:8351
//
// Environment:
//   PORT                   default 8351
//   HITS_FILE              file served as /data/hits_current.json (default ../data/hits_current.json)
//   BLOB_READ_WRITE_TOKEN  unset -> an in-memory Blob store replaces @vercel/blob (lost on restart)
//   MOCK_WEBHOOK_URL       if set, outbound requests to webhook hosts and api.stripe.com are sent
//                          here instead, with the original URL in an x-original-url header
//   CRON_SECRET, STRIPE_*  passed through to the handlers as on Vercel
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { createHash, randomBytes } from 'node:crypto';
import { dirname, extname, join, normalize, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SITE = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 8351);
const ORIGIN = `http://127.0.0.1:${PORT}`;
const HITS_FILE = resolve(process.env.HITS_FILE || join(SITE, '..', 'data', 'hits_current.json'));
const config = JSON.parse(await readFile(join(SITE, 'vercel.json'), 'utf8'));

process.env.DATA_ORIGIN ||= ORIGIN;
process.env.PUBLIC_BASE_URL ||= ORIGIN;
process.env.HITS_CACHE_SECONDS ||= '0';

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon',
};

// ---------- in-memory @vercel/blob ----------
if (!process.env.BLOB_READ_WRITE_TOKEN) {
  const store = new Map();
  const meta = (pathname, b) => ({
    url: `https://blob.local/${pathname}`, downloadUrl: `https://blob.local/${pathname}?download=1`, pathname,
    contentType: b.contentType, contentDisposition: 'inline', cacheControl: 'public, max-age=60', uploadedAt: b.uploadedAt,
    etag: b.etag, size: b.body.length,
  });
  globalThis.__351watchBlobShim = {
    async put(pathname, body, opts = {}) {
      let name = pathname;
      if (opts.addRandomSuffix) name = name.replace(/(\.[^./]+)?$/, `-${randomBytes(6).toString('hex')}$1`);
      if (store.has(name) && !opts.allowOverwrite && !opts.ifMatch) throw new Error('BlobError: This blob already exists');
      const buf = Buffer.isBuffer(body) ? body : Buffer.from(typeof body === 'string' ? body : JSON.stringify(body));
      const b = { body: buf, contentType: opts.contentType || 'application/octet-stream', uploadedAt: new Date(), etag: createHash('md5').update(buf).digest('hex') };
      store.set(name, b);
      return meta(name, b);
    },
    async get(pathname) {
      const b = store.get(pathname.replace(/^https:\/\/blob\.local\//, ''));
      if (!b) return null;
      return { statusCode: 200, stream: new Response(b.body).body, headers: new Headers({ 'content-type': b.contentType }), blob: meta(pathname, b) };
    },
    async head(pathname) {
      const b = store.get(pathname);
      return b ? meta(pathname, b) : null;
    },
    async del(pathnames) {
      for (const p of [].concat(pathnames)) store.delete(p);
    },
    async list({ prefix = '', cursor, limit = 1000 } = {}) {
      const keys = [...store.keys()].filter((k) => k.startsWith(prefix)).sort();
      const start = Number(cursor || 0);
      const page = keys.slice(start, start + limit);
      const hasMore = start + limit < keys.length;
      return { blobs: page.map((k) => meta(k, store.get(k))), hasMore, cursor: hasMore ? String(start + limit) : undefined };
    },
  };
  console.log('dev-server: BLOB_READ_WRITE_TOKEN unset, using an in-memory Blob store');
}

// ---------- outbound webhook / Stripe redirection for local tests ----------
if (process.env.MOCK_WEBHOOK_URL) {
  const realFetch = globalThis.fetch;
  const MOCK_HOST = /^(hooks\.slack\.com|outlook\.office\.com|discord\.com|api\.stripe\.com)$|\.webhook\.office\.com$|\.logic\.azure\.com$/;
  globalThis.fetch = (input, init = {}) => {
    const url = new URL(typeof input === 'string' || input instanceof URL ? input : input.url);
    if (!MOCK_HOST.test(url.hostname)) return realFetch(input, init);
    const headers = new Headers(init.headers);
    headers.set('x-original-url', url.href);
    return realFetch(process.env.MOCK_WEBHOOK_URL, { ...init, headers });
  };
  console.log(`dev-server: webhook and Stripe requests go to ${process.env.MOCK_WEBHOOK_URL}`);
}

// ---------- vercel.json routing ----------
function toRegex(source) {
  let out = '';
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i];
    if (ch === ':') {
      const m = /^:([A-Za-z_]\w*)/.exec(source.slice(i));
      out += '([^/]+)';
      i += m[0].length - 1;
    } else if (ch === '(') {
      let depth = 0;
      let j = i;
      for (; j < source.length; j += 1) {
        if (source[j] === '(') depth += 1;
        if (source[j] === ')' && --depth === 0) break;
      }
      out += source.slice(i, j + 1);
      i = j;
    } else {
      out += ch.replace(/[.*+?^${}|[\]\\/]/g, '\\$&');
    }
  }
  return new RegExp(`^${out}$`);
}
const headerRules = (config.headers || []).map((r) => ({ re: toRegex(r.source), headers: r.headers }));
const rewrites = (config.rewrites || []).map((r) => ({ re: toRegex(r.source), destination: r.destination }));

function applyHeaders(res, pathname) {
  for (const rule of headerRules) if (rule.re.test(pathname)) for (const h of rule.headers) res.setHeader(h.key, h.value);
}

async function fileAt(pathname) {
  const rel = normalize(decodeURIComponent(pathname)).replace(/^([/\\])+/, '');
  const full = resolve(SITE, rel);
  if (full !== SITE && !full.startsWith(SITE + sep)) return null;
  if (rel.startsWith('api') || rel.startsWith('node_modules') || /(^|\/)\./.test(rel)) return null;
  try {
    const s = await stat(full);
    return s.isFile() ? full : null;
  } catch {
    return null;
  }
}

async function resolveStatic(pathname) {
  if (pathname === '/data/hits_current.json') return HITS_FILE;
  if (pathname === '/') return fileAt('/index.html');
  if (pathname.endsWith('/')) return (await fileAt(`${pathname}index.html`)) || null;
  return (await fileAt(pathname)) || (await fileAt(`${pathname}.html`));
}

async function serveStatic(req, res, url) {
  let file = await resolveStatic(url.pathname);
  if (!file) {
    const rw = rewrites.find((r) => r.re.test(url.pathname));
    if (rw) file = await fileAt(rw.destination);
  }
  if (!file) {
    res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
    return res.end('404 Not Found');
  }
  const body = await readFile(file);
  res.writeHead(200, { 'content-type': TYPES[extname(file)] || 'application/octet-stream', 'content-length': body.length });
  res.end(req.method === 'HEAD' ? undefined : body);
}

// ---------- API handlers ----------
const modules = new Map();
async function loadHandler(pathname) {
  const rel = pathname.replace(/^\/api\//, '').replace(/\/$/, '');
  if (!rel || rel.split('/').some((seg) => !/^[A-Za-z0-9-][A-Za-z0-9_-]*$/.test(seg))) return null;
  const file = join(SITE, 'api', `${rel}.js`);
  try {
    await stat(file);
  } catch {
    return null;
  }
  if (!modules.has(file)) modules.set(file, await import(pathToFileURL(file).href));
  return modules.get(file);
}

function readRaw(req) {
  return new Promise((ok, fail) => {
    const chunks = [];
    let size = 0;
    req.on('data', (c) => {
      size += c.length;
      if (size > 5 * 1024 * 1024) req.destroy(new Error('body too large'));
      chunks.push(c);
    });
    req.on('end', () => ok(Buffer.concat(chunks)));
    req.on('error', fail);
  });
}

function parseBody(raw, type = '') {
  if (!raw.length) return undefined;
  if (type.includes('application/json')) {
    try {
      return JSON.parse(raw.toString('utf8'));
    } catch {
      return raw.toString('utf8');
    }
  }
  if (type.includes('application/x-www-form-urlencoded')) return Object.fromEntries(new URLSearchParams(raw.toString('utf8')));
  if (type.startsWith('text/')) return raw.toString('utf8');
  return raw;
}

async function runApi(req, res, url) {
  const mod = await loadHandler(url.pathname);
  if (!mod) {
    res.writeHead(404, { 'content-type': 'application/json' });
    return res.end(JSON.stringify({ ok: false, error: 'Not found' }));
  }
  req.headers['x-forwarded-proto'] = 'http';
  req.headers['x-forwarded-host'] ||= req.headers.host;
  const raw = ['GET', 'HEAD'].includes(req.method) ? Buffer.alloc(0) : await readRaw(req);

  const web = mod[req.method] || (typeof mod.default === 'object' && mod.default?.fetch);
  if (web || (!mod.default && ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'].some((m) => mod[m]))) {
    if (!web) {
      res.writeHead(405, { 'content-type': 'application/json' });
      return res.end(JSON.stringify({ ok: false, error: 'Method not allowed' }));
    }
    const request = new Request(`${ORIGIN}${url.pathname}${url.search}`, {
      method: req.method, headers: req.headers, body: raw.length ? raw : undefined,
    });
    const response = await (mod[req.method] ? mod[req.method](request) : mod.default.fetch(request));
    const body = Buffer.from(await response.arrayBuffer());
    response.headers.forEach((v, k) => res.setHeader(k, v));
    res.writeHead(response.status);
    return res.end(body);
  }

  req.query = Object.fromEntries(url.searchParams);
  req.body = parseBody(raw, req.headers['content-type']);
  res.status = (code) => {
    res.statusCode = code;
    return res;
  };
  res.json = (data) => {
    if (!res.getHeader('content-type')) res.setHeader('content-type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(data));
    return res;
  };
  res.send = (data) => {
    if (typeof data === 'object' && data !== null && !Buffer.isBuffer(data)) return res.json(data);
    if (!res.getHeader('content-type')) res.setHeader('content-type', 'text/html; charset=utf-8');
    res.end(req.method === 'HEAD' ? undefined : data);
    return res;
  };
  await mod.default(req, res);
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, ORIGIN);
  const started = Date.now();
  res.on('finish', () => {
    if (process.env.DEV_LOG) console.log(`${req.method} ${url.pathname}${url.search.replace(/id=[^&]+/, 'id=…')} ${res.statusCode} ${Date.now() - started}ms`);
  });
  try {
    applyHeaders(res, url.pathname);
    if (url.pathname.startsWith('/api/')) return await runApi(req, res, url);
    if (/\.html$/.test(url.pathname) && config.cleanUrls) {
      res.writeHead(308, { location: url.pathname.replace(/(index)?\.html$/, '') + url.search });
      return res.end();
    }
    if (!['GET', 'HEAD'].includes(req.method)) {
      res.writeHead(405);
      return res.end();
    }
    return await serveStatic(req, res, url);
  } catch (err) {
    console.error('dev-server error', err);
    if (!res.headersSent) res.writeHead(500, { 'content-type': 'text/plain' });
    res.end('500 Internal Server Error');
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`351 Watch dev server on ${ORIGIN} (site: ${SITE}, data: ${HITS_FILE})`);
});
