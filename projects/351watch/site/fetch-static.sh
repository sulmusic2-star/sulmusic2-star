#!/bin/sh
# Vercel build step: pull the pre-built static pages for this deployment from GitHub.
# The pages are rendered locally by build.py and committed; SITE_REF picks the branch or commit.
# manifest.txt (written by build.py) lists the files to fetch.
set -eu
REF="${SITE_REF:-claude/massachusetts-market-service-ead9ho}"
BASE="https://raw.githubusercontent.com/sulmusic2-star/sulmusic2-star/${REF}/projects/351watch/site"
mkdir -p public
curl -fsSL "${BASE}/manifest.txt" -o public/manifest.txt
while read -r f; do
  [ -n "$f" ] && curl -fsSL "${BASE}/${f}" -o "public/${f}"
done < public/manifest.txt
rm public/manifest.txt
echo "fetched static files from ${REF}"
