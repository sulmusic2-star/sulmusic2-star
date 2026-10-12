"""Match 351 Watch towns to Census 2024 Gazetteer county-subdivision centroids.
usage: python3 -I match_points.py GAZETTEER.txt PROJECT_DIR OUT.json"""
import csv
import json
import re
import sys
from pathlib import Path

gaz, proj, out = sys.argv[1:]
proj = Path(proj)
FIPS = {"MA": "25", "NY": "36", "RI": "44"}


def norm(name):
    n = name.lower().replace("’", "'").replace("'", "")
    n = re.sub(r"\s+(town city|city town|town|city|village|plantation|reservation|ccd)$", "", n)
    n = re.sub(r"[^a-z0-9]+", " ", n).strip()
    return n


rows = {}
with open(gaz, encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f, delimiter="\t")
    head = [h.strip() for h in next(reader)]
    for r in reader:
        rec = dict(zip(head, (c.strip() for c in r)))
        st = rec["USPS"]
        if st not in FIPS:
            continue
        key = (st, norm(rec["NAME"]))
        # Prefer the larger land area when a name repeats (NY has same-named towns in two counties).
        area = float(rec["ALAND_SQMI"] or 0)
        prev = rows.get(key)
        rows.setdefault(key, [])
        rows[key].append((area, float(rec["INTPTLAT"]), float(rec["INTPTLONG"]), rec["NAME"], rec["GEOID"]))

points, missing = {}, []
for path in sorted((proj / "data").glob("towns_*.json")):
    doc = json.loads(path.read_text())
    towns = doc.get("towns", []) if isinstance(doc, dict) else doc
    for t in towns:
        if not isinstance(t, dict) or not t.get("town"):
            continue
        st = (t.get("state") or "MA").upper()
        if st not in FIPS:
            continue
        cands = rows.get((st, norm(t["town"])), [])
        if len(cands) > 1 and t.get("county"):
            # NY: disambiguate same-named towns by county FIPS is not in the gazetteer row; keep largest.
            pass
        if not cands:
            missing.append(f"{st}:{t['town']}")
            continue
        area, lat, lon, name, geoid = max(cands)
        points[f"{st}:{t['town']}"] = [round(lat, 4), round(lon, 4)]

Path(out).write_text(json.dumps({
    "_about": "Town centroids (internal points) from the U.S. Census Bureau 2024 Gazetteer, county subdivisions "
              "(https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_cousubs_national.zip). "
              "Public domain. Used only to draw the dot maps on the site.",
    "points": points,
}, indent=0, sort_keys=True))
print(len(points), "matched;", len(missing), "missing:", missing[:40])
