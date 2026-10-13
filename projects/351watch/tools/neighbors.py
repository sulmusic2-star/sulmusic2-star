#!/usr/bin/env python3
"""Build data/neighbors.json: which towns touch which, for the free "your town plus its
neighbors" watchlist area.

Source: US Census Bureau cartographic boundary files, county subdivisions, 1:500,000
(cb_<year>_<state fips>_cousub_500k.zip) for MA (25), RI (44) and NY (36). In these three
states a county subdivision is a town or city (NY also has New York City's five boroughs, kept,
and Indian reservations, left out). Two towns are neighbors when their boundaries come within
BUFFER_M meters of each other along at least MIN_SHARED_M meters. The buffer closes slivers and
small gaps from generalized and shoreline-clipped boundaries; the minimum length drops towns
that only meet at a corner point. Where the Census clips a boundary at the shoreline (the
ocean, Nantucket Sound, Narragansett Bay), towns across the water are not neighbors; where it
does not (rivers, Long Island's Peconic Bay), the line down the middle of the water counts.

Output (keys are the site's town ids, "<ST>:<Town>", as in site/data/towns.json):
    {"_meta": {...source, vintage, method...},
     "MA:Carver": ["MA:Kingston", "MA:Middleborough", ...], ...}

Every MA, RI and NY town is a key (an island town can have an empty list). Neighbors across
the MA, RI and NY state lines are included; towns in other states (CT, NH, VT, NJ, PA) are not.

Usage (needs shapely and pyshp: pip install shapely pyshp):
    python3 tools/neighbors.py                  # downloads to a temp dir, writes data/neighbors.json
    python3 tools/neighbors.py --cache DIR      # reuse/keep the zip files in DIR
    python3 tools/neighbors.py --check          # also print the spot checks
"""
from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
import tempfile
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import shapefile  # pyshp
import shapely
from shapely.geometry import shape
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "neighbors.json"
SITE_TOWNS = ROOT / "site" / "data" / "towns.json"

VINTAGE = "2024"
URL = "https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{fips}_cousub_500k.zip"
STATES = {"MA": "25", "RI": "44", "NY": "36"}

BUFFER_M = 50.0  # boundaries closer than this count as touching
MIN_SHARED_M = 100.0  # and run together at least this far (a corner-only contact measures about 25-55 m)
LAT0 = 42.5  # local equirectangular projection; scale error under 5% across MA, RI and NY

# Spot checks, read off a state map: neighbors that must be present and towns that must not be.
# Halifax is not a Carver neighbor: Plympton lies between them (closest points about 3.9 km apart).
CHECKS = {
    "MA:Carver": (["MA:Plymouth", "MA:Middleborough", "MA:Plympton", "MA:Kingston", "MA:Wareham"], ["MA:Halifax"]),
    "MA:Boston": (["MA:Cambridge", "MA:Brookline", "MA:Quincy", "MA:Milton", "MA:Dedham", "MA:Newton",
                   "MA:Watertown", "MA:Somerville", "MA:Everett", "MA:Chelsea", "MA:Revere", "MA:Winthrop"], ["MA:Hull"]),
    "MA:Cambridge": (["MA:Arlington", "MA:Belmont", "MA:Boston", "MA:Somerville", "MA:Watertown"], []),
    "MA:Springfield": (["MA:Agawam", "MA:Chicopee", "MA:East Longmeadow", "MA:Longmeadow", "MA:Ludlow",
                        "MA:West Springfield", "MA:Wilbraham"], []),
    "MA:Worcester": (["MA:Auburn", "MA:Holden", "MA:Leicester", "MA:Millbury", "MA:Paxton", "MA:Shrewsbury",
                      "MA:West Boylston"], []),
    "MA:Seekonk": (["MA:Rehoboth", "MA:Swansea", "MA:Attleboro", "RI:East Providence", "RI:Pawtucket"], []),
    "MA:Nantucket": ([], ["MA:Edgartown", "MA:Chatham"]),
    "RI:Providence": (["RI:Cranston", "RI:Johnston", "RI:North Providence", "RI:Pawtucket", "RI:East Providence"], []),
    "RI:Westerly": (["RI:Charlestown", "RI:Hopkinton"], []),
    "NY:Clifton Park": (["NY:Halfmoon", "NY:Ballston", "NY:Malta"], []),
    "NY:Kent": (["NY:Carmel", "NY:Putnam Valley", "NY:Patterson", "NY:Philipstown", "NY:East Fishkill"], []),
}


def download(year: str, fips: str, cache: Path) -> Path:
    url = URL.format(year=year, fips=fips)
    path = cache / url.rsplit("/", 1)[1]
    if not path.exists() or path.stat().st_size == 0:
        req = urllib.request.Request(url, headers={"User-Agent": "351WatchBot/0.1 (+https://351watch.vercel.app/bot)"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            path.write_bytes(resp.read())
    return path


def read_cousubs(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        stem = next(n[:-4] for n in zf.namelist() if n.endswith(".shp"))
        files = {ext: io.BytesIO(zf.read(f"{stem}.{ext}")) for ext in ("shp", "shx", "dbf")}
    reader = shapefile.Reader(shp=files["shp"], shx=files["shx"], dbf=files["dbf"], encoding="utf-8")
    fields = [f[0] for f in reader.fields[1:]]
    for sr in reader.iterShapeRecords():
        rec = dict(zip(fields, sr.record))
        yield rec, shape(sr.shape.__geo_interface__)


def project(geom):
    scale = [111_320.0 * math.cos(math.radians(LAT0)), 110_574.0]
    return shapely.transform(geom, lambda coords: coords * scale)


def base_name(st: str, rec: dict) -> tuple[str, str] | None:
    """(name, kind) as the site names towns, or None for rows that are not towns or cities."""
    lsad_name = rec["NAMELSAD"]
    if rec["COUSUBFP"] == "00000" or "not defined" in lsad_name:
        return None
    if st == "MA":  # same rule as crawler/watch351/ma_census.py
        m = re.match(r"^(.*?)\s+(Town city|city|town)$", lsad_name)
    else:  # same rule as crawler/experiments/ri_sos_build.py, plus New York City's boroughs
        m = re.match(r"^(.*?)\s+(city|town|borough)$", lsad_name)
    if not m:
        return None  # NY Indian reservations
    return m.group(1), m.group(2).split()[-1]


def site_ids(towns_json: Path) -> dict[tuple[str, str, str], str]:
    """(state, name, county) -> site id for every town on the site."""
    doc = json.loads(towns_json.read_text())
    return {(t["state"], t["town"], t.get("county") or ""): t["id"] for t in doc["towns"]}


def assign_ids(rows: list[dict], site: dict) -> None:
    """Give each row an id. Site towns keep their site id. Elsewhere (NY), a name used by more
    than one town or city in the state gets "(city)" or "(<County> County)" added."""
    by_name = defaultdict(list)
    for r in rows:
        by_name[(r["state"], r["name"])].append(r)
    taken = set(site.values())
    matches = defaultdict(list)
    for r in rows:
        key = (r["state"], r["name"], r["county"])
        if key in site:
            matches[key].append(r)
    for key, found in matches.items():
        # NY has a town and a city of the same name in one county (Amsterdam, Geneva); the site's are towns
        chosen = found[0] if len(found) == 1 else next((r for r in found if r["kind"] == "town"), found[0])
        chosen["id"] = site[key]
    for (st, name), group in by_name.items():
        for r in group:
            if "id" in r:
                continue
            plain = f"{st}:{name}"
            if len(group) == 1 and plain not in taken:
                r["id"] = plain
            elif r["kind"] == "city" and sum(1 for g in group if g["kind"] == "city") == 1 and f"{plain} (city)" not in taken:
                r["id"] = f"{plain} (city)"
            else:
                r["id"] = f"{plain} ({r['county']} County)"
            taken.add(r["id"])
    ids = [r["id"] for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"duplicate ids: {sorted(dupes)[:10]}")


def build(cache: Path) -> tuple[dict, list[dict]]:
    site = site_ids(SITE_TOWNS)
    rows = []
    files = []
    for st, fips in STATES.items():
        path = download(VINTAGE, fips, cache)
        files.append({"state": st, "url": URL.format(year=VINTAGE, fips=fips)})
        for rec, geom in read_cousubs(path):
            named = base_name(st, rec)
            if not named:
                continue
            county = rec.get("NAMELSADCO", "").removesuffix(" County")
            geom = project(geom).buffer(0)
            # A NY city that crosses a county line (Geneva) is one row per county; merge them.
            same = next((r for r in rows if r["kind"] == "city" and named[1] == "city"
                         and (r["state"], r["name"]) == (st, named[0])), None)
            if same:
                if geom.area > same["geom"].area:
                    same["county"] = county
                same["geom"] = same["geom"].union(geom)
                continue
            rows.append({"state": st, "name": named[0], "kind": named[1], "county": county, "geom": geom})
    assign_ids(rows, site)

    half = BUFFER_M / 2
    grown = [r["geom"].buffer(half, quad_segs=4) for r in rows]
    tree = STRtree(grown)
    pairs = {}
    for i, g in enumerate(grown):
        for j in tree.query(g, predicate="intersects"):
            j = int(j)
            if j <= i:
                continue
            overlap = g.intersection(grown[j]).area
            shared = overlap / BUFFER_M  # a strip BUFFER_M wide along the shared line
            if shared >= MIN_SHARED_M:
                pairs[(i, j)] = shared

    neighbors = {r["id"]: set() for r in rows}
    for i, j in pairs:
        neighbors[rows[i]["id"]].add(rows[j]["id"])
        neighbors[rows[j]["id"]].add(rows[i]["id"])

    by_state = defaultdict(int)
    for r in rows:
        by_state[r["state"]] += 1
    meta = {
        "about": "Towns whose boundaries touch, for the free watchlist area (a town plus its neighbors). "
                 "Keys and values are site town ids (<ST>:<Town>); keys starting with '_' are not towns.",
        "source": "US Census Bureau, cartographic boundary files, county subdivisions, 1:500,000",
        "vintage": VINTAGE,
        "files": files,
        "method": {
            "buffer_m": BUFFER_M,
            "min_shared_m": MIN_SHARED_M,
            "rule": "neighbors when the boundaries come within buffer_m of each other along at least min_shared_m; "
                    "towns across water the Census clips at the shoreline (ocean, sounds, Narragansett Bay) are not "
                    "neighbors; across rivers and unclipped bays the line in the water counts",
            "projection": f"equirectangular at latitude {LAT0}",
            "ny_names": "NY towns on the site keep their site id; other NY names used by more than one town or city get "
                        "' (city)' or ' (<County> County)' added; New York City's boroughs are listed by name; "
                        "a city split across counties is one entry; NY Indian reservations are left out",
            "states": "MA, RI and NY, including neighbors across their shared state lines; other states are not included",
        },
        "counts": dict(by_state),
        "pairs": len(pairs),
        "built": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "script": "projects/351watch/tools/neighbors.py",
    }
    out = {"_meta": meta}
    for key in sorted(neighbors, key=lambda k: (list(STATES).index(k[:2]), k)):
        out[key] = sorted(neighbors[key])
    return out, rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cache", type=Path, help="directory for the downloaded zip files")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--check", action="store_true", help="print spot checks")
    args = ap.parse_args()

    if args.cache:
        args.cache.mkdir(parents=True, exist_ok=True)
        out, rows = build(args.cache)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            out, rows = build(Path(tmp))

    site = json.loads(SITE_TOWNS.read_text())["towns"]
    missing = [t["id"] for t in site if t["id"] not in out]
    if missing:
        print(f"warning: {len(missing)} site towns have no boundary: {missing[:10]}", file=sys.stderr)

    failed = 0
    for town, (want, never) in CHECKS.items():
        got = out.get(town, [])
        lacking = [w for w in want if w not in got]
        extra = [n for n in never if n in got]
        if lacking or extra:
            failed += 1
            print(f"check failed: {town} lacks {lacking}, wrongly has {extra}", file=sys.stderr)
    if args.check:
        for town in list(CHECKS) + ["MA:Gosnold", "MA:Mount Washington", "MA:Williamstown", "RI:New Shoreham",
                                    "NY:Southold", "NY:Amsterdam", "NY:Geneva", "NY:Hempstead"]:
            print(f"{town}: {', '.join(out.get(town, ['(not found)'])) or '(none)'}")
        print(f"spot checks: {len(CHECKS) - failed} of {len(CHECKS)} pass")

    # One town per line keeps git diffs readable; the file is still plain JSON.
    lines = [f"{json.dumps(k)}:{json.dumps(v, ensure_ascii=False, separators=(',', ':'))}" for k, v in out.items()]
    args.out.write_text("{\n" + ",\n".join(lines) + "\n}\n")
    sizes = [len(v) for k, v in out.items() if not k.startswith("_")]
    print(f"wrote {args.out}: {len(sizes)} towns, {out['_meta']['pairs']} neighbor pairs, "
          f"median {sorted(sizes)[len(sizes) // 2]} neighbors, {sizes.count(0)} with none")
    return 1 if failed or missing else 0


if __name__ == "__main__":
    sys.exit(main())
