#!/bin/sh
# Vercel build: assemble a Build Output API v3 bundle (.vercel/output) from this repo at SITE_REF.
#
# Deployments upload almost nothing; the project's build command is
#   curl -fsSL https://raw.githubusercontent.com/sulmusic2-star/sulmusic2-star/$SHA/projects/351watch/site/vercel-build.sh | SITE_REF=$SHA sh
# so pages, data and API functions all come from git at one commit, and a redeploy with a new
# SHA ships everything (including API changes) without re-uploading code.
#
#   static/     every committed page and asset under projects/351watch/site (minus api and tooling)
#               plus data/hits_current.json for the feeds and data/neighbors.json (free watchlist area)
#   static/pagefind/  the /search index, built from data/search by search/build-index.mjs
#   functions/  one Node function per api/**/*.js that isn't a _helper; each bundles the whole
#               api/ tree (for relative imports) and @vercel/blob
#   config.json headers, clean URLs (overrides), the /w/:id rewrite and the daily cron
set -eu
REF="${SITE_REF:-claude/massachusetts-market-service-ead9ho}"
URL="${SITE_TARBALL_URL:-https://codeload.github.com/sulmusic2-star/sulmusic2-star/tar.gz/${REF}}"
OUT="${OUTPUT_DIR:-.vercel/output}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -fsSL --retry 3 --retry-delay 2 "$URL" -o "$TMP/repo.tgz"
TOP="$(tar -tzf "$TMP/repo.tgz" | head -n 1 | cut -d/ -f1)"
tar -xzf "$TMP/repo.tgz" -C "$TMP" "$TOP/projects/351watch/site" "$TOP/projects/351watch/data/hits_current.json" \
  "$TOP/projects/351watch/data/neighbors.json" "$TOP/projects/351watch/data/search" "$TOP/projects/351watch/search"
SRC="$TMP/$TOP/projects/351watch"

rm -rf "$OUT"
mkdir -p "$OUT/static/data" "$OUT/functions"

# ---- static files
(cd "$SRC/site" && tar -cf - \
  --exclude=./api --exclude=./node_modules --exclude=./public --exclude=./.vercel \
  --exclude=./package.json --exclude=./package-lock.json --exclude=./vercel.json \
  --exclude=./fetch-static.sh --exclude=./vercel-build.sh --exclude=./manifest.txt \
  --exclude=./dev-server.mjs --exclude='./*.md' --exclude=./data/hits_current.json \
  .) | (cd "$OUT/static" && tar -xf -)
cp "$SRC/data/hits_current.json" "$OUT/static/data/hits_current.json"
cp "$SRC/data/neighbors.json" "$OUT/static/data/neighbors.json"  # free watchlist area: a town plus its neighbors
for required in index.html watch.html w.html data/towns.json data/hits_current.json data/neighbors.json; do
  [ -s "$OUT/static/$required" ] || { echo "vercel-build: missing $required at ${REF}" >&2; exit 1; }
done

# ---- full-text search index (Pagefind, version pinned by search/package-lock.json) -> static/pagefind
(cd "$SRC/search" && npm ci --no-audit --no-fund --loglevel=error >/dev/null)
node "$SRC/search/build-index.mjs" "$SRC/data/search" "$OUT/static/pagefind"
[ -s "$OUT/static/pagefind/pagefind.js" ] || { echo "vercel-build: search index missing at ${REF}" >&2; exit 1; }

# ---- function dependencies (installed once, copied into each function)
BLOB_VERSION="$(sed -n 's/.*"@vercel\/blob": *"\([^"]*\)".*/\1/p' "$SRC/site/package.json")"
mkdir -p "$TMP/deps"
(cd "$TMP/deps" && printf '{"private":true}\n' > package.json &&
  npm install --no-audit --no-fund --omit=dev --loglevel=error "@vercel/blob@${BLOB_VERSION:-2.8.1}" >/dev/null)

# ---- functions
(cd "$SRC/site" && find api -name '*.js' ! -name '_*' | sort) | while read -r rel; do
  name="${rel%.js}"
  func="$OUT/functions/$name.func"
  mkdir -p "$func"
  cp -R "$SRC/site/api" "$func/api"
  cp -R "$TMP/deps/node_modules" "$func/node_modules"
  printf '{"type":"module"}\n' > "$func/package.json"
  max=30
  [ "$name" = "api/cron/dispatch" ] && max=60
  if grep -q '^export default' "$SRC/site/$rel"; then
    handler="$rel"; helpers=true
  else
    # Web-signature module (export GET/POST/...): adapt Node req/res to Request/Response.
    handler="__web.mjs"; helpers=false
    cat > "$func/__web.mjs" <<EOF
import * as mod from './$rel';
export default async function (req, res) {
  const fn = mod[req.method];
  if (typeof fn !== 'function') {
    res.statusCode = 405;
    res.setHeader('Allow', Object.keys(mod).filter((k) => /^[A-Z]+\$/.test(k)).join(', '));
    return res.end();
  }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const headers = new Headers();
  for (const [k, v] of Object.entries(req.headers)) if (v !== undefined) headers.set(k, Array.isArray(v) ? v.join(', ') : String(v));
  const url = 'https://' + (req.headers['x-forwarded-host'] || req.headers.host || 'localhost') + req.url;
  const body = ['GET', 'HEAD'].includes(req.method) ? undefined : Buffer.concat(chunks);
  const out = await fn(new Request(url, { method: req.method, headers, body }));
  res.statusCode = out.status;
  out.headers.forEach((v, k) => res.setHeader(k, v));
  res.end(Buffer.from(await out.arrayBuffer()));
}
EOF
  fi
  cat > "$func/.vc-config.json" <<EOF
{"runtime":"nodejs22.x","handler":"$handler","launcherType":"Nodejs","shouldAddHelpers":$helpers,"maxDuration":$max}
EOF
done

# ---- routing config (clean URLs via overrides; same headers as vercel.json)
node - "$OUT" <<'EOF'
const fs = require('fs');
const path = require('path');
const out = process.argv[2];
const staticDir = path.join(out, 'static');
const overrides = {};
(function walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p);
    else if (e.name.endsWith('.html') && e.name !== 'index.html' && path.relative(staticDir, p) !== '404.html') {
      const rel = path.relative(staticDir, p).split(path.sep).join('/');
      overrides[rel] = { path: rel.slice(0, -5), contentType: 'text/html; charset=utf-8' };
    }
  }
})(staticDir);
const security = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'X-Frame-Options': 'DENY',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; img-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
};
const config = {
  version: 3,
  routes: [
    { src: '^/(.*)$', headers: security, continue: true },
    { src: '^/api/(?!feed)(.*)$', headers: { 'Cache-Control': 'no-store' }, continue: true },
    { src: '^/w(/.*)?$', headers: { 'X-Robots-Tag': 'noindex' }, continue: true },
    { src: '^/data/(.*)$', headers: { 'Cache-Control': 'public, max-age=300, s-maxage=300' }, continue: true },
    // fonts and the hashed search-index chunks never change under their names; styles and scripts for a few minutes
    { src: '^/fonts/(.*)$', headers: { 'Cache-Control': 'public, max-age=31536000, immutable' }, continue: true },
    { src: '^/pagefind/(index|fragment|filter)/(.*)$', headers: { 'Cache-Control': 'public, max-age=31536000, immutable' }, continue: true },
    { src: '^/(.*)\\.(css|js)$', headers: { 'Cache-Control': 'public, max-age=300, stale-while-revalidate=3600' }, continue: true },
    { src: '^/index\\.html$', status: 308, headers: { Location: '/' } },
    { src: '^/(.+)\\.html$', status: 308, headers: { Location: '/$1' } },
    // one address per page: no trailing slash (the /w/:id pages keep theirs until the rewrite below)
    { src: '^/((?!api/|w/).+)/$', status: 308, headers: { Location: '/$1' } },
    // a state's own address goes to that state on the towns page
    { src: '^/(ma|ny|ri)/?$', status: 308, headers: { Location: '/towns#$1' } },
    { handle: 'filesystem' },
    { src: '^/\\.well-known/http-message-signatures-directory/?$', dest: '/api/key-directory' },
    { src: '^/w/[^/]*/?$', dest: '/w' },
    // anything else that isn't a file: our own 404 page (kept under its file name, see overrides)
    { src: '^/(?!api/).*$', dest: '/404.html', status: 404 },
  ],
  overrides,
  crons: [{ path: '/api/cron/dispatch', schedule: '30 13 * * *' }],
};
fs.writeFileSync(path.join(out, 'config.json'), JSON.stringify(config, null, 1));
console.log(`vercel-build: ${Object.keys(overrides).length} pages, config written`);
EOF
echo "vercel-build: $(find "$OUT/static" -type f | wc -l | tr -d ' ') static files, $(find "$OUT/functions" -name .vc-config.json | wc -l | tr -d ' ') functions from ${REF}"
