#!/usr/bin/env bash
# 351 Watch daily refresh: idempotent runbook for a fresh cloud container.
#
#   ops/daily.sh                       # crawl, build, commit "Daily refresh YYYY-MM-DD", push
#   ops/daily.sh --no-commit           # crawl + build only (testing)
#   ops/daily.sh --states MA,NY        # any other option is passed to `python3 -m watch351.daily`
#
# Steps: install Python deps if missing (requests, beautifulsoup4, lxml); try to install
# poppler-utils + tesseract-ocr if missing (OCR is optional: without it, image-only PDFs are
# recorded as needs_ocr and retried on a later run); run the incremental crawl, which skips
# every document already in data/state/ and downloads only listing pages plus new agendas;
# refresh MassDEP wetlands filings (best effort); rebuild the site; commit data/ and site/ (never the crawler cache) only when something
# changed; push to the current branch with 4 retries (2s/4s/8s/16s backoff).
# The LAST line printed is the resulting commit SHA (HEAD).
set -euo pipefail

NO_COMMIT=0
DAILY_ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --no-commit) NO_COMMIT=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) DAILY_ARGS+=("$1") ;;
  esac
  shift
done

log() { echo "[daily $(date -u +%H:%M:%S)] $*" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT"
TODAY="$(date -u +%Y-%m-%d)"

# One run at a time per container.
if command -v flock >/dev/null 2>&1; then
  exec 9>"${TMPDIR:-/tmp}/351watch-daily.lock"
  flock -n 9 || { log "another daily run is in progress"; exit 1; }
fi

# ---------------------------------------------------------------- dependencies
if ! python3 -c 'import requests, bs4, lxml' >/dev/null 2>&1; then
  log "installing Python dependencies"
  python3 -m pip install --quiet requests beautifulsoup4 lxml \
    || python3 -m pip install --quiet --break-system-packages requests beautifulsoup4 lxml \
    || { log "could not install Python dependencies"; exit 1; }
fi

APT_PKGS=()
command -v pdftotext >/dev/null 2>&1 || APT_PKGS+=(poppler-utils)
command -v tesseract >/dev/null 2>&1 || APT_PKGS+=(tesseract-ocr)
if [ ${#APT_PKGS[@]} -gt 0 ]; then
  SUDO=""
  if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo -n"; fi
  log "installing ${APT_PKGS[*]}"
  export DEBIAN_FRONTEND=noninteractive
  if ! { timeout 600 $SUDO apt-get install -y -qq "${APT_PKGS[@]}" \
         || { timeout 300 $SUDO apt-get update -qq && timeout 600 $SUDO apt-get install -y -qq "${APT_PKGS[@]}"; }; \
       } >/dev/null 2>&1; then
    log "apt-get install failed; continuing (no OCR: scanned agendas wait for a run with tesseract)"
  fi
fi

# ------------------------------------------------------------------ crawl + build
log "wetlands filings (MassDEP)"
(cd crawler && python3 -m watch351.sources.massdep) || log "MassDEP refresh failed; keeping yesterday's wetlands data"
log "crawl"
(cd crawler && python3 -m watch351.daily "${DAILY_ARGS[@]+"${DAILY_ARGS[@]}"}")
log "search text: rows for indexed documents still missing one (local cache only, no network)"
(cd crawler && python3 -m watch351.fulltext backfill >&2) || log "search backfill failed; continuing"
python3 trending.py >&2 || log "trending failed; keeping the last data/trending.json"
python3 tools/verify_briefs.py --quiet >&2 || log "some written briefs failed verification; they will not render"
log "build site"
python3 build.py

if [ "$NO_COMMIT" -eq 1 ]; then
  log "--no-commit: leaving changes in the working tree"
  git status --short -- data site >&2 || true
  git rev-parse HEAD
  exit 0
fi

# ------------------------------------------------------------------ commit + push
git add -A -- data site
if git diff --cached --quiet -- data site; then
  log "no changes to commit"
else
  if ! git config user.email >/dev/null 2>&1; then
    export GIT_AUTHOR_NAME="Claude" GIT_AUTHOR_EMAIL="noreply@anthropic.com"
    export GIT_COMMITTER_NAME="Claude" GIT_COMMITTER_EMAIL="noreply@anthropic.com"
  fi
  SUMMARY="$(python3 - "$TODAY" <<'PY' 2>/dev/null || true
import json, sys
try:
    r = json.load(open(f"data/state/runs/{sys.argv[1]}.json"))
except Exception:
    sys.exit(0)
print(f"Towns crawled {r['towns_succeeded']}/{r['towns_attempted']}; new documents {r['new_documents']}; "
      f"new hits {r['new_hits']}; current hits {r['hits_current']}; "
      f"requests {r['network']['requests']}; runtime {r['duration_seconds']:.0f}s.")
PY
)"
  MSG_FILE="$(mktemp)"
  {
    echo "Daily refresh $TODAY"
    if [ -n "$SUMMARY" ]; then echo; echo "$SUMMARY"; fi
    echo
    echo "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  } > "$MSG_FILE"
  git commit -q -F "$MSG_FILE" -- data site
  rm -f "$MSG_FILE"
  log "committed $(git rev-parse --short HEAD)"
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" = "HEAD" ]; then
  log "detached HEAD: not pushing"
  git rev-parse HEAD
  exit 1
fi

pushed=0
for delay in 2 4 8 16 0; do
  if out="$(git push -u origin "$BRANCH" 2>&1)"; then
    pushed=1
    break
  fi
  log "push failed: $(echo "$out" | tail -n 2 | tr '\n' ' ')"
  if echo "$out" | grep -qiE "non-fast-forward|fetch first|rejected"; then
    # someone else pushed: replay our commit on top (abort on conflict)
    git pull --rebase -q origin "$BRANCH" >&2 || { git rebase --abort >/dev/null 2>&1 || true; }
  fi
  [ "$delay" -gt 0 ] || break
  log "retrying in ${delay}s"
  sleep "$delay"
done
if [ "$pushed" -ne 1 ]; then
  log "push failed after 4 retries"
  git rev-parse HEAD
  exit 1
fi
log "pushed to $BRANCH"
git rev-parse HEAD
