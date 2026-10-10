// Shared helpers for writing form submissions to private Vercel Blob storage.
import { put } from '@vercel/blob';
import { randomUUID } from 'node:crypto';

export const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function clean(value, max) {
  return typeof value === 'string' ? value.replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, max) : '';
}

export function readBody(req) {
  return typeof req.body === 'object' && req.body !== null ? req.body : {};
}

export async function save(prefix, record) {
  const stamp = record.created_at.replace(/[:.]/g, '-');
  await put(`${prefix}/${stamp}-${randomUUID()}.json`, JSON.stringify(record), {
    access: 'private',
    contentType: 'application/json',
  });
}

export function postOnly(req, res) {
  if (req.method === 'POST') return true;
  res.setHeader('Allow', 'POST');
  res.status(405).json({ ok: false, error: 'Method not allowed' });
  return false;
}
