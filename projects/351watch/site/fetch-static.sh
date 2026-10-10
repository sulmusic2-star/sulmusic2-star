#!/bin/sh
# Vercel build step: pull the pre-built static pages for this deployment from GitHub.
# The pages are rendered locally by build.py and committed; SITE_REF picks the branch or commit.
set -eu
REF="${SITE_REF:-claude/massachusetts-market-service-ead9ho}"
BASE="https://raw.githubusercontent.com/sulmusic2-star/sulmusic2-star/${REF}/projects/351watch/site"
mkdir -p public
for f in index.html privacy.html styles.css app.js robots.txt; do
  curl -fsSL "${BASE}/${f}" -o "public/${f}"
done
echo "fetched static files from ${REF}"
