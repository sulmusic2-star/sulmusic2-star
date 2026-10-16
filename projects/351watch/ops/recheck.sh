#!/usr/bin/env bash
# Afternoon re-check: re-read the listings of every town with a meeting in the next three days, so an agenda
# a town re-posted after the morning run (Carver posted its Oct 20 agenda three times in a week) is picked up
# the same day, with the old link retired. Runs the daily pipeline for those towns only, with listing pages
# fetched fresh, then rebuilds, commits and pushes like ops/daily.sh. Last printed line = commit SHA.
#
#   bash projects/351watch/ops/recheck.sh            # towns with meetings today through three days ahead
#   DAYS=5 bash projects/351watch/ops/recheck.sh     # a wider window
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$HERE/.." && pwd)"
DAYS="${DAYS:-3}"

TOWNS="$(python3 - "$PROJECT/data/hits_current.json" "$DAYS" <<'PY'
import json, sys
from datetime import date, timedelta
doc = json.load(open(sys.argv[1]))
today = date.today()
end = (today + timedelta(days=int(sys.argv[2]))).isoformat()
towns = sorted({h["town"] for h in doc["hits"]
                if today.isoformat() <= (h.get("meeting_date") or "") <= end and h.get("source", "agenda") == "agenda"})
print(",".join(towns))
PY
)"
if [ -z "$TOWNS" ]; then
  echo "recheck: no meetings in the next $DAYS days; nothing to re-read" >&2
  exit 0
fi
echo "recheck: $(echo "$TOWNS" | tr ',' '\n' | wc -l | tr -d ' ') towns with meetings in the next $DAYS days" >&2
exec bash "$HERE/daily.sh" "$@" --towns "$TOWNS" --fresh-listings
