#!/bin/sh
# Vercel build step: fetch this deployment's static pages and data from GitHub at SITE_REF.
# Pages are rendered locally by build.py and committed. This downloads the repo tarball for
# SITE_REF (a branch, tag or commit), copies projects/351watch/site/ (minus the API functions,
# deploy config and dev tooling) into public/, and copies data/hits_current.json to
# public/data/hits_current.json for the feeds and webhooks.
set -eu
REF="${SITE_REF:-claude/massachusetts-market-service-ead9ho}"
URL="${SITE_TARBALL_URL:-https://codeload.github.com/sulmusic2-star/sulmusic2-star/tar.gz/${REF}}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -fsSL --retry 3 --retry-delay 2 "$URL" -o "$TMP/repo.tgz"
TOP="$(tar -tzf "$TMP/repo.tgz" | head -n 1 | cut -d/ -f1)"
SRC="$TMP/$TOP/projects/351watch"
tar -xzf "$TMP/repo.tgz" -C "$TMP" "$TOP/projects/351watch/site" "$TOP/projects/351watch/data/hits_current.json"

rm -rf public
mkdir -p public
(cd "$SRC/site" && tar -cf - \
  --exclude=./api --exclude=./node_modules --exclude=./public --exclude=./.vercel \
  --exclude=./package.json --exclude=./package-lock.json --exclude=./vercel.json \
  --exclude=./fetch-static.sh --exclude=./manifest.txt --exclude=./dev-server.mjs \
  --exclude='./*.md' --exclude=./data/hits_current.json \
  .) | (cd public && tar -xf -)
mkdir -p public/data
cp "$SRC/data/hits_current.json" public/data/hits_current.json

for required in index.html watch.html w.html data/towns.json data/hits_current.json; do
  [ -s "public/$required" ] || { echo "fetch-static: missing $required at ${REF}" >&2; exit 1; }
done
echo "fetched $(find public -type f | wc -l | tr -d ' ') static files from ${REF}"
