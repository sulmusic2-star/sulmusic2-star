"""Import written briefs from work files into data/briefs/ (one append per hit id).

    python3 tools/import_briefs.py WORK.jsonl [...]   (paths under data/briefs_work/)
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from briefs import append_brief, FIELDS  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
n = 0
for work in sys.argv[1:]:
    for line in Path(work).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        state, date = row.pop("state", None), row.get("meeting_date")
        append_brief(DATA, row, state, date)
        n += 1
print(f"imported {n} briefs")
