// Web Bot Auth key directory for 351WatchBot, served at
// /.well-known/http-message-signatures-directory (rewrite in vercel-build.sh).
//
// Cloudflare's Verified Bots programme reads this JSON Web Key Set to check the
// signatures our crawler attaches to its requests. The response itself must be
// signed with each listed key (tag "http-message-signatures-directory") so that
// nobody can mirror the directory and register it as their own.
//
// WBA_PRIVATE_KEY is the 32-byte Ed25519 seed, base64url-encoded; the crawler
// signs with the same value (crawler/watch351/botauth.py).
import crypto from 'node:crypto';

const PKCS8_ED25519_PREFIX = Buffer.from('302e020100300506032b657004220420', 'hex');
const TTL_SECONDS = 300;

function b64urlDecode(text) {
  return Buffer.from(text.trim().replace(/-/g, '+').replace(/_/g, '/'), 'base64');
}

function thumbprint(x) {
  const canonical = JSON.stringify({ crv: 'Ed25519', kty: 'OKP', x });
  return crypto.createHash('sha256').update(canonical).digest('base64url');
}

export default function handler(req, res) {
  const seed = process.env.WBA_PRIVATE_KEY;
  if (!seed) {
    res.statusCode = 503;
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'no-store');
    return res.end(JSON.stringify({ error: 'Key directory not configured.' }));
  }
  const key = crypto.createPrivateKey({
    key: Buffer.concat([PKCS8_ED25519_PREFIX, b64urlDecode(seed)]),
    format: 'der',
    type: 'pkcs8',
  });
  const { x } = crypto.createPublicKey(key).export({ format: 'jwk' });
  const authority = String(req.headers['x-forwarded-host'] || req.headers.host || '')
    .split(',')[0].trim().toLowerCase();
  const created = Math.floor(Date.now() / 1000);
  const nonce = crypto.randomBytes(48).toString('base64');
  const params = `("@authority";req);alg="ed25519";keyid="${thumbprint(x)}";nonce="${nonce}";`
    + `tag="http-message-signatures-directory";created=${created};expires=${created + TTL_SECONDS}`;
  const base = `"@authority";req: ${authority}\n"@signature-params": ${params}`;
  const signature = crypto.sign(null, Buffer.from(base, 'ascii'), key).toString('base64');

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/http-message-signatures-directory+json');
  res.setHeader('Signature-Input', `sig1=${params}`);
  res.setHeader('Signature', `sig1=:${signature}:`);
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify({ keys: [{ kty: 'OKP', crv: 'Ed25519', x }] }));
}
