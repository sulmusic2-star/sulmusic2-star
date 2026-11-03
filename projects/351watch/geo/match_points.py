"""Match Agenda Ahead places to Census 2024 Gazetteer centroids, for the dot maps (geo/town_points.json).

Massachusetts, Rhode Island and New York towns and cities come from the county-subdivision Gazetteer, as before.
Virginia and Maryland counties and independent cities come from the county Gazetteer (an independent city is a
county equivalent, "Alexandria city"); their towns and municipalities from the place Gazetteer. Michigan and Ohio
townships and cities come from the county-subdivision Gazetteer (a same-named township is told apart by its county
FIPS code, read against the county Gazetteer); their county rows from the county Gazetteer. A regional planning body
that covers several counties sits at the mean of their centroids. Points already in OUT are kept as they are.

usage: python3 -I geo/match_points.py COUSUBS.txt COUNTIES.txt PLACES.txt PROJECT_DIR OUT.json
"""
import csv
import json
import re
import sys
from pathlib import Path

cousubs, counties, places, proj, out = sys.argv[1:6]
proj = Path(proj)
OUT = Path(out)
FIPS = {"MA": "25", "NY": "36", "RI": "44", "VA": "51", "MD": "24", "MI": "26", "OH": "39"}
COUSUB_STATES = {"MA", "NY", "RI", "MI", "OH"}


def norm(name):
    n = name.lower().replace("’", "'").replace("'", "")
    n = re.sub(r"\s+(town city|city town|charter township|township|town|city|village|plantation|reservation|ccd)$", "", n)
    n = re.sub(r"[^a-z0-9]+", " ", n).strip()
    return n


def tight(name):
    """norm without spaces: "LaSalle" and "La Salle", "Bokes Creek" and "Bokescreek" are one name."""
    return norm(name).replace(" ", "")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t")
        head = [h.strip() for h in next(reader)]
        for r in reader:
            yield dict(zip(head, (c.strip() for c in r)))


# counties: (state, "loudoun") -> (lat, lon); county FIPS -> county name; independent cities keep their "city" suffix
county_pt, county_name = {}, {}
for rec in read(counties):
    st = rec["USPS"]
    if st not in FIPS:
        continue
    county_pt[(st, norm(rec["NAME"]), rec["NAME"].lower().endswith(" city"))] = (float(rec["INTPTLAT"]), float(rec["INTPTLONG"]))
    county_name[rec["GEOID"]] = re.sub(r"\s+County$", "", rec["NAME"])

# county subdivisions: (state, "pittsfield", kind) -> [(area, lat, lon, county name)]
sub = {}
for rec in read(cousubs):
    st = rec["USPS"]
    if st not in FIPS or st not in COUSUB_STATES:
        continue
    name = rec["NAME"]
    kind = "city" if name.lower().endswith(" city") else ("township" if "township" in name.lower() else "town")
    key = (st, norm(name), kind if st in ("MI", "OH") else "")
    row = (float(rec["ALAND_SQMI"] or 0), float(rec["INTPTLAT"]), float(rec["INTPTLONG"]), county_name.get(rec["GEOID"][:5], ""))
    sub.setdefault(key, []).append(row)
    if st in ("MI", "OH"):
        sub.setdefault((st, tight(name), kind), []).append(row)

# places (incorporated towns and cities): (state, "culpeper", kind) -> (lat, lon)
plc = {}
for rec in read(places):
    st = rec["USPS"]
    if st not in ("VA", "MD"):
        continue
    if rec["LSAD"] not in ("25", "43", "47"):  # city, town, village; not CDPs
        continue
    kind = {"25": "city", "43": "town", "47": "village"}[rec["LSAD"]]
    plc[(st, norm(rec["NAME"]), kind)] = (float(rec["INTPTLAT"]), float(rec["INTPTLONG"]))

existing = json.loads(OUT.read_text()).get("points", {}) if OUT.exists() else {}
points, missing = dict(existing), []
for path in sorted((proj / "data").glob("towns_*.json")):
    doc = json.loads(path.read_text())
    towns = doc.get("towns", []) if isinstance(doc, dict) else doc
    for t in towns:
        if not isinstance(t, dict) or not t.get("town"):
            continue
        st = (t.get("state") or "MA").upper()
        if st not in FIPS:
            continue
        tid = f"{st}:{t['town']}"
        if tid in existing:
            continue
        kind = t.get("kind") or "town"
        name = re.sub(r"\s*\([^()]*County\)$", "", t["town"])
        bare = re.sub(r"^(?:City|Town|Village) of ", "", name)
        pt = None
        if kind == "county" and st in ("NY", "VA", "MD", "MI", "OH"):
            if t.get("covers_counties"):  # a regional body: the mean of its counties
                pts = [county_pt.get((st, norm(f"{c} County"), False)) for c in t["covers_counties"]]
                pts = [p for p in pts if p]
                if pts:
                    pt = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
            else:
                pt = county_pt.get((st, norm(bare), False))
        elif kind == "city" and st in ("VA", "MD"):
            pt = county_pt.get((st, norm(bare), True)) or plc.get((st, norm(bare), "city"))
        elif st in ("VA", "MD"):
            pt = plc.get((st, norm(bare), kind)) or plc.get((st, norm(bare), "town")) or plc.get((st, norm(bare), "city"))
        else:
            cands = sub.get((st, norm(name), kind if st in ("MI", "OH") else ""), [])
            if not cands and st in ("MI", "OH"):
                cands = sub.get((st, tight(bare), kind), [])
            if st in ("MI", "OH") and t.get("county"):
                same = [c for c in cands if norm(c[3]) == norm(t["county"])]
                cands = same or cands
            if cands:
                area, lat, lon, _ = max(cands)
                pt = (lat, lon)
        if not pt:
            missing.append(tid)
            continue
        points[tid] = [round(pt[0], 4), round(pt[1], 4)]

OUT.write_text(json.dumps({
    "_about": "Place centroids (internal points) from the U.S. Census Bureau 2024 Gazetteer: county subdivisions for "
              "Massachusetts, Rhode Island, New York, Michigan and Ohio towns, cities and townships; counties for Virginia, "
              "Maryland, Michigan and Ohio counties and Virginia's and Baltimore's independent cities; places for Virginia "
              "towns and Maryland municipalities "
              "(https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/). Public domain. Used only to "
              "draw the maps on the site.",
    "points": points,
}, indent=0, sort_keys=True))
print(len(points), "points;", len(points) - len(existing), "added;", len(missing), "missing:", missing[:60])
