// Shared helpers for the 351 Watch API: private Vercel Blob storage and request handling.
// The Blob SDK is loaded lazily so the local dev server (dev-server.mjs) can substitute an
// in-memory store when BLOB_READ_WRITE_TOKEN is unset.
import { randomUUID } from 'node:crypto';

let blobImpl;
export async function blob() {
  if (!blobImpl) blobImpl = globalThis.__351watchBlobShim || (await import('@vercel/blob'));
  return blobImpl;
}

export function clean(value, max) {
  return typeof value === 'string' ? value.replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max) : '';
}

export function readBody(req) {
  if (typeof req.body === 'object' && req.body !== null && !Buffer.isBuffer(req.body)) return req.body;
  if (typeof req.body === 'string' && req.body.length < 20000) {
    try {
      const parsed = JSON.parse(req.body);
      return typeof parsed === 'object' && parsed !== null ? parsed : {};
    } catch {
      return {};
    }
  }
  return {};
}

export function bodySize(req) {
  const declared = Number(req.headers['content-length'] || 0);
  if (declared) return declared;
  try {
    return JSON.stringify(req.body ?? '').length;
  } catch {
    return Infinity;
  }
}

// Writes one record per blob under `prefix/` (contact messages).
export async function save(prefix, record) {
  const { put } = await blob();
  const stamp = record.created_at.replace(/[:.]/g, '-');
  await put(`${prefix}/${stamp}-${randomUUID()}.json`, JSON.stringify(record), {
    access: 'private',
    contentType: 'application/json',
  });
}

export async function readJSON(pathname) {
  const { get } = await blob();
  let result;
  try {
    result = await get(pathname, { access: 'private', useCache: false });
  } catch (err) {
    if (err && err.name === 'BlobNotFoundError') return null;
    throw err;
  }
  if (!result || result.statusCode !== 200) return null;
  return JSON.parse(await new Response(result.stream).text());
}

export async function writeJSON(pathname, data) {
  const { put } = await blob();
  await put(pathname, JSON.stringify(data), {
    access: 'private',
    contentType: 'application/json',
    addRandomSuffix: false,
    allowOverwrite: true,
    cacheControlMaxAge: 60,
  });
}

export async function removeJSON(pathname) {
  const { del } = await blob();
  await del(pathname);
}

export async function listPathnames(prefix) {
  const { list } = await blob();
  const names = [];
  let cursor;
  do {
    const page = await list({ prefix, cursor, limit: 1000 });
    names.push(...page.blobs.map((b) => b.pathname));
    cursor = page.hasMore ? page.cursor : undefined;
  } while (cursor);
  return names;
}

export function allow(req, res, methods) {
  if (methods.includes(req.method)) return true;
  res.setHeader('Allow', methods.join(', '));
  res.status(405).json({ ok: false, error: 'Method not allowed' });
  return false;
}

export function postOnly(req, res) {
  return allow(req, res, ['POST']);
}

export function noStore(res) {
  res.setHeader('Cache-Control', 'no-store');
}

// Best-effort per-instance throttle (serverless instances are short-lived; this only blunts bursts).
const hits = new Map();
export function throttled(req, bucket, limit, windowMs) {
  const ip = String(req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown').split(',')[0].trim();
  const key = `${bucket}:${ip}`;
  const now = Date.now();
  const recent = (hits.get(key) || []).filter((t) => now - t < windowMs);
  recent.push(now);
  hits.set(key, recent);
  if (hits.size > 5000) hits.clear();
  return recent.length > limit;
}
