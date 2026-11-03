#!/usr/bin/env python3
"""Build data/neighbors.json: which places touch which, for the free "your town plus its
neighbors" watchlist area.

Source: US Census Bureau cartographic boundary files, 1:500,000, vintage 2024.
- Massachusetts (25), Rhode Island (44), New York (36), Michigan (26) and Ohio (39): county subdivisions
  (cb_<year>_<fips>_cousub_500k.zip). In the first three a county subdivision is a town or city (NY also has
  New York City's five boroughs, kept, and Indian reservations, left out); in Michigan and Ohio it is a
  township, a charter township, a city or (Ohio) a village. Two places are neighbors when their boundaries
  come within BUFFER_M meters of each other along at least MIN_SHARED_M meters. The buffer closes slivers
  and small gaps from generalized and shoreline-clipped boundaries; the minimum length drops places that
  only meet at a corner point. Where the Census clips a boundary at the shoreline (the ocean, Nantucket
  Sound, Narragansett Bay, the Great Lakes), places across the water are not neighbors; where it does not
  (rivers, Long Island's Peconic Bay), the line down the middle of the water counts.
- Virginia (51) and Maryland (24): counties and county equivalents (cb_<year>_us_county_500k.zip; a Virginia
  independent city and Baltimore City are county equivalents) and incorporated places (cb_<year>_<fips>_place_500k.zip:
  towns, cities and villages, not census-designated places). A county's area is the touching counties and
  independent cities plus the towns inside it; a town's area is its county plus the towns and cities it
  touches. The Potomac is Maryland's, so Virginia's shore counties touch Maryland's.
- A Michigan or Ohio county is a place of its own too (its planning commission reviews township zoning): its
  area is the townships and cities inside it plus the touching counties; each township's area includes its county.

Output (keys are the site's place ids, "<ST>:<Name>", as in data/towns_*.json and site/data/towns.json):
    {"_meta": {...source, vintage, method...},
     "MA:Carver": ["MA:Kingston", "MA:Middleborough", ...], ...}

Every MA, RI and NY place is a key (an island town can have an empty list); in VA, MD, MI and OH the keys are
the places on the site plus every county and independent city, and the lists name every touching place, on the
site or not. Neighbors across the MA, RI and NY state lines and across the VA and MD line are included; other
states are not. Lists are symmetric where both places are keys.

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
DATA = ROOT / "data"

VINTAGE = "2024"
URL = "https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{fips}_cousub_500k.zip"
URL_PLACE = "https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{fips}_place_500k.zip"
URL_COUNTY = "https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_500k.zip"
STATES = {"MA": "25", "RI": "44", "NY": "36"}  # county subdivisions are towns and cities
TOWNSHIP_STATES = {"MI": "26", "OH": "39"}  # county subdivisions are townships, cities and villages
COUNTY_STATES = {"VA": "51", "MD": "24"}  # counties, independent cities and incorporated places
ORDER = ["MA", "RI", "NY", "VA", "MD", "MI", "OH"]

BUFFER_M = 50.0  # boundaries closer than this count as touching
MIN_SHARED_M = 100.0  # and run together at least this far (a corner-only contact measures about 25-55 m)
# local equirectangular projection per group; scale error under 5% across each
LAT0 = {"ne": 42.5, "va-md": 38.2, "mi-oh": 42.5}

# Spot checks, read off a state map: neighbors that must be present and places that must not be.
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
    # Virginia and Maryland: a county's area is the touching counties and cities plus the towns inside it
    "VA:Loudoun County": (["VA:Fairfax County", "VA:Prince William County", "VA:Clarke County", "VA:Fauquier County",
                           "VA:Town of Leesburg", "VA:Town of Purcellville", "MD:Montgomery County"], ["VA:Town of Culpeper"]),
    "VA:Town of Culpeper": (["VA:Culpeper County"], ["VA:Orange County"]),
    "VA:City of Manassas": (["VA:Prince William County", "VA:City of Manassas Park"], []),
    "MD:Montgomery County": (["MD:Frederick County", "MD:Howard County", "MD:Prince George's County", "VA:Loudoun County",
                              "VA:Fairfax County", "MD:City of Rockville", "MD:City of Gaithersburg"], []),
    "MD:City of Takoma Park": (["MD:Montgomery County"], ["MD:Prince George's County"]),
    # Michigan and Ohio: townships touch; each includes its county
    "MI:Pittsfield Charter Township": (["MI:Washtenaw County", "MI:City of Saline", "MI:Lodi Township", "MI:York Charter Township",
                                        "MI:Ypsilanti Charter Township", "MI:City of Ann Arbor"], []),
    "OH:Orange Township": (["OH:Delaware County", "OH:Berlin Township", "OH:Liberty Township (Delaware County)", "OH:Genoa Township"], []),
    "OH:Bokes Creek Township": (["OH:Logan County", "OH:Logan-Union-Champaign Regional Planning Commission"], []),
}


def download(url: str, cache: Path) -> Path:
    path = cache / url.rsplit("/", 1)[1]
    if not path.exists() or path.stat().st_size == 0:
        req = urllib.request.Request(url, headers={"User-Agent": "AgendaAheadBot/0.1 (+https://agendaahead.vercel.app/bot)"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            path.write_bytes(resp.read())
    return path


def read_shapes(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        stem = next(n[:-4] for n in zf.namelist() if n.endswith(".shp"))
        files = {ext: io.BytesIO(zf.read(f"{stem}.{ext}")) for ext in ("shp", "shx", "dbf")}
    reader = shapefile.Reader(shp=files["shp"], shx=files["shx"], dbf=files["dbf"], encoding="utf-8")
    fields = [f[0] for f in reader.fields[1:]]
    for sr in reader.iterShapeRecords():
        rec = dict(zip(fields, sr.record))
        yield rec, shape(sr.shape.__geo_interface__)


def project(geom, lat0):
    scale = [111_320.0 * math.cos(math.radians(lat0)), 110_574.0]
    return shapely.transform(geom, lambda coords: coords * scale)


def base_name(st: str, rec: dict) -> tuple[str, str] | None:
    """(name, kind) as the site names towns, or None for rows that are not towns or cities."""
    lsad_name = rec["NAMELSAD"]
    if rec["COUSUBFP"] == "00000" or "not defined" in lsad_name:
        return None
    if st == "MA":  # same rule as crawler/watch351/ma_census.py
        m = re.match(r"^(.*?)\s+(Town city|city|town)$", lsad_name)
    elif st in TOWNSHIP_STATES:
        m = re.match(r"^(.*?)\s+(charter township|township|city|village)$", lsad_name)
        if m and m.group(2) == "city":
            return f"City of {m.group(1)}", "city"
        if m and m.group(2) == "village":
            return f"Village of {m.group(1)}", "village"
        if m and m.group(2) == "charter township":
            return f"{m.group(1)} Charter Township", "township"
        if m:
            return f"{m.group(1)} Township", "township"
        return None  # Ohio "County subdivisions not defined" and the like
    else:  # same rule as crawler/experiments/ri_sos_build.py, plus New York City's boroughs
        m = re.match(r"^(.*?)\s+(city|town|borough)$", lsad_name)
    if not m:
        return None  # NY Indian reservations
    return m.group(1), m.group(2).split()[-1]


def county_equiv_name(rec: dict) -> tuple[str, str]:
    """("Loudoun County", "county") or ("City of Alexandria", "city") for a county-file row; Baltimore City keeps its name."""
    name = rec["NAMELSAD"]
    if name.endswith(" city"):
        base = name[:-5]
        return ("Baltimore City", "city") if (rec["STUSPS"], base) == ("MD", "Baltimore") else (f"City of {base}", "city")
    return name, "county"


def place_name_of(rec: dict) -> tuple[str, str] | None:
    """("Town of Culpeper", "town") for an incorporated place; None for a census-designated place."""
    kind = {"25": "city", "43": "town", "47": "village"}.get(rec["LSAD"])
    if not kind:
        return None
    return f"{kind.title()} of {rec['NAME']}", kind


COVERED = set(STATES) | set(TOWNSHIP_STATES) | set(COUNTY_STATES)


def tight(name: str) -> str:
    """A name with no case, spaces, punctuation or charter status: "LaSalle" and "La Salle", "Bokes Creek" and
    "Bokescreek", "Superior Charter Township" and "Superior township" are one (the Census does not record charters)."""
    return re.sub(r"[^a-z0-9]+", "", name.lower().replace("’", "").replace("Charter ", "").replace("charter ", ""))


def site_ids() -> dict[tuple[str, str, str], str]:
    """(state, name, county) -> site id for every place in a towns file of a covered state (gated ones too, so
    their areas are ready when they are promoted). A second key per place has the name with no spaces, for a
    Census spelling that differs only there."""
    out = {}
    for path in sorted(DATA.glob("towns_*.json")):
        doc = json.loads(path.read_text())
        for t in doc.get("towns", []) if isinstance(doc, dict) else doc:
            if isinstance(t, dict) and t.get("town"):
                st = (t.get("state") or "MA").upper()
                if st not in COVERED:
                    continue
                name = re.sub(r"\s*\([^()]*County\)$", "", t["town"])
                out[(st, name, t.get("county") or "")] = f"{st}:{t['town']}"
                out.setdefault((st, tight(name), t.get("county") or ""), f"{st}:{t['town']}")
    if SITE_TOWNS.exists():
        for t in json.loads(SITE_TOWNS.read_text())["towns"]:
            if t["state"] in COVERED:
                out.setdefault((t["state"], t["town"], t.get("county") or ""), t["id"])
    return out


def assign_ids(rows: list[dict], site: dict) -> None:
    """Give each row an id. Site places keep their site id. Elsewhere, a name used by more than one place in the
    state gets "(city)" or "(<County> County)" added (New York), or " (<County> County)" (Michigan and Ohio, the
    towns files' own convention)."""
    by_name = defaultdict(list)
    for r in rows:
        by_name[(r["state"], r["name"])].append(r)
    taken = set(site.values())
    matches = defaultdict(list)
    for r in rows:
        key = (r["state"], r["name"], r["county"])
        if key not in site and (r["state"], tight(r["name"]), r["county"]) in site:
            key = (r["state"], tight(r["name"]), r["county"])
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
            elif st in TOWNSHIP_STATES:
                r["id"] = f"{plain} ({r['county']} County)"
            elif r["kind"] == "city" and sum(1 for g in group if g["kind"] == "city") == 1 and f"{plain} (city)" not in taken:
                r["id"] = f"{plain} (city)"
            else:
                r["id"] = f"{plain} ({r['county']} County)"
            taken.add(r["id"])
    ids = [r["id"] for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"duplicate ids: {sorted(dupes)[:10]}")


def touching(rows: list[dict]) -> set[tuple[int, int]]:
    """Pairs of row indexes whose boundaries run together for at least MIN_SHARED_M within BUFFER_M."""
    half = BUFFER_M / 2
    grown = [r["geom"].buffer(half, quad_segs=4) for r in rows]
    tree = STRtree(grown)
    pairs = set()
    for i, g in enumerate(grown):
        for j in tree.query(g, predicate="intersects"):
            j = int(j)
            if j <= i:
                continue
            overlap = g.intersection(grown[j]).area
            shared = overlap / BUFFER_M  # a strip BUFFER_M wide along the shared line
            if shared >= MIN_SHARED_M:
                pairs.add((i, j))
    return pairs


def cousub_rows(st: str, path: Path, lat0: float) -> list[dict]:
    rows = []
    for rec, geom in read_shapes(path):
        named = base_name(st, rec)
        if not named:
            continue
        county = rec.get("NAMELSADCO", "").removesuffix(" County")
        geom = project(geom, lat0).buffer(0)
        # A city that crosses a county line (Geneva NY, Lansing MI) is one row per county; merge them. So is a
        # township the Census files in two pieces (Washington township, Union County, Ohio).
        same = next((r for r in rows if ((r["kind"] == "city" and named[1] == "city") or (st in TOWNSHIP_STATES and r["county"] == county))
                     and (r["state"], r["name"]) == (st, named[0])), None)
        if same:
            if geom.area > same["geom"].area:
                same["county"] = county
            same["geom"] = same["geom"].union(geom)
            continue
        rows.append({"state": st, "name": named[0], "kind": named[1], "county": county, "geom": geom})
    return rows


def build(cache: Path) -> tuple[dict, list[dict]]:
    site = site_ids()
    files = []
    neighbors: dict[str, set] = {}

    def add_pair(a: str, b: str) -> None:
        if a != b:
            neighbors.setdefault(a, set()).add(b)
            neighbors.setdefault(b, set()).add(a)

    # --- the Northeast: towns and cities touch
    ne = []
    for st, fips in STATES.items():
        path = download(URL.format(year=VINTAGE, fips=fips), cache)
        files.append({"state": st, "url": URL.format(year=VINTAGE, fips=fips)})
        ne += cousub_rows(st, path, LAT0["ne"])
    assign_ids(ne, site)
    for r in ne:
        neighbors.setdefault(r["id"], set())
    for i, j in touching(ne):
        add_pair(ne[i]["id"], ne[j]["id"])

    # --- counties for every state that needs them (Virginia, Maryland, Michigan, Ohio)
    county_path = download(URL_COUNTY.format(year=VINTAGE), cache)
    files.append({"state": "VA,MD,MI,OH", "url": URL_COUNTY.format(year=VINTAGE)})
    counties: dict[str, list[dict]] = defaultdict(list)
    for rec, geom in read_shapes(county_path):
        st = rec["STUSPS"]
        if st not in COUNTY_STATES and st not in TOWNSHIP_STATES:
            continue
        name, kind = county_equiv_name(rec)
        group = "va-md" if st in COUNTY_STATES else "mi-oh"
        row = {"state": st, "name": name, "kind": kind, "county": rec["NAME"], "geom": project(geom, LAT0[group]).buffer(0),
               "id": f"{st}:{name}"}
        counties[group].append(row)

    # --- Virginia and Maryland: counties and independent cities touch; towns touch; a town sits in its county
    vamd = counties["va-md"]
    for r in vamd:
        neighbors.setdefault(r["id"], set())
    for i, j in touching(vamd):
        add_pair(vamd[i]["id"], vamd[j]["id"])
    places = []
    for st, fips in COUNTY_STATES.items():
        path = download(URL_PLACE.format(year=VINTAGE, fips=fips), cache)
        files.append({"state": st, "url": URL_PLACE.format(year=VINTAGE, fips=fips)})
        for rec, geom in read_shapes(path):
            named = place_name_of(rec)
            if not named:
                continue
            if (st == "VA" and named[1] == "city") or (st, rec["NAME"]) == ("MD", "Baltimore"):
                continue  # a Virginia city and Baltimore City are county equivalents, read from the county file
            places.append({"state": st, "name": named[0], "kind": named[1], "geom": project(geom, LAT0["va-md"]).buffer(0),
                           "id": f"{st}:{named[0]}"})
    county_tree = STRtree([r["geom"] for r in vamd])
    for p in places:
        neighbors.setdefault(p["id"], set())
        # the county (or counties) holding the town: the county with the most of the town's area; a town on a county
        # line (Maryland's Takoma Park) gets both when each holds at least a fifth
        shares = []
        for k in county_tree.query(p["geom"], predicate="intersects"):
            c = vamd[int(k)]
            if c["kind"] != "county":
                continue
            shares.append((c["geom"].intersection(p["geom"]).area / max(p["geom"].area, 1.0), c["id"]))
        for share, cid in sorted(shares, reverse=True):
            if share >= 0.2 or (shares and share == max(shares)[0]):
                add_pair(p["id"], cid)
    both = places + [c for c in vamd if c["kind"] == "city"]  # towns touch towns and independent cities
    for i, j in touching(both):
        add_pair(both[i]["id"], both[j]["id"])

    # --- Michigan and Ohio: townships, cities and villages touch; each sits in its county; counties touch
    mioh = counties["mi-oh"]
    for r in mioh:
        neighbors.setdefault(r["id"], set())
    for i, j in touching(mioh):
        add_pair(mioh[i]["id"], mioh[j]["id"])
    subs = []
    for st, fips in TOWNSHIP_STATES.items():
        path = download(URL.format(year=VINTAGE, fips=fips), cache)
        files.append({"state": st, "url": URL.format(year=VINTAGE, fips=fips)})
        subs += cousub_rows(st, path, LAT0["mi-oh"])
    assign_ids(subs, site)
    for r in subs:
        neighbors.setdefault(r["id"], set())
        add_pair(r["id"], f"{r['state']}:{r['county']} County")
    for i, j in touching(subs):
        add_pair(subs[i]["id"], subs[j]["id"])
    # a regional planning body (Ohio) covers several counties: its area is theirs
    for path in sorted(DATA.glob("towns_*.json")):
        doc = json.loads(path.read_text())
        for t in doc.get("towns", []) if isinstance(doc, dict) else doc:
            if isinstance(t, dict) and t.get("covers_counties") and t.get("state") in TOWNSHIP_STATES:
                rid = f"{t['state']}:{t['town']}"
                neighbors.setdefault(rid, set())
                for c in t["covers_counties"]:
                    cid = f"{t['state']}:{c} County"
                    add_pair(rid, cid)
                    for n in list(neighbors.get(cid, ())):
                        if n != rid and not n.endswith(" County"):
                            add_pair(rid, n)

    # Keys: every place in the Northeast (as before); in the four new states, the places on the site plus every county
    # and independent city, so the file stays a size a page can load. Values name every touching place.
    site_ids_set = set(site.values())
    for key in list(neighbors):
        st = key[:2]
        if st in COUNTY_STATES or st in TOWNSHIP_STATES:
            if key not in site_ids_set and not (key.endswith(" County") or key.startswith(f"{st}:City of ") and st == "VA" or key == "MD:Baltimore City"):
                del neighbors[key]

    rows = ne + vamd + places + mioh + subs
    by_state = defaultdict(int)
    for r in rows:
        by_state[r["state"]] += 1
    meta = {
        "about": "Places whose boundaries touch, for the free watchlist area (a place plus its neighbors). "
                 "Keys and values are site place ids (<ST>:<Name>); keys starting with '_' are not places.",
        "source": "US Census Bureau, cartographic boundary files, 1:500,000: county subdivisions (MA, RI, NY, MI, OH), "
                  "counties (VA, MD, MI, OH) and incorporated places (VA, MD)",
        "vintage": VINTAGE,
        "files": files,
        "method": {
            "buffer_m": BUFFER_M,
            "min_shared_m": MIN_SHARED_M,
            "rule": "neighbors when the boundaries come within buffer_m of each other along at least min_shared_m; "
                    "places across water the Census clips at the shoreline (ocean, sounds, Narragansett Bay, the Great Lakes) are not "
                    "neighbors; across rivers and unclipped bays the line in the water counts",
            "counties": "Virginia and Maryland: a county's area is the touching counties and independent cities plus the towns "
                        "inside it; a town's area is its county (both when it straddles a line) plus the towns and cities it "
                        "touches. Michigan and Ohio: townships, cities and villages touch; each includes its county; counties "
                        "touch; a regional planning body covers its counties' places",
            "projection": f"equirectangular at latitude {LAT0['ne']} (MA, RI, NY), {LAT0['va-md']} (VA, MD), {LAT0['mi-oh']} (MI, OH)",
            "names": "places on the site keep their site id; other NY names used by more than one town or city get "
                     "' (city)' or ' (<County> County)' added; Michigan and Ohio townships are '<Name> Township' or "
                     "'<Name> Charter Township', a repeated name with ' (<County> County)'; cities are 'City of <Name>', "
                     "villages 'Village of <Name>'; Virginia and Maryland towns 'Town of <Name>', cities 'City of <Name>' "
                     "(Baltimore City keeps its name); New York City's boroughs are listed by name; a city split across "
                     "counties is one entry; NY Indian reservations are left out",
            "states": "MA, RI, NY, VA, MD, MI and OH, including neighbors across the MA, RI and NY lines and the VA and MD line; "
                      "other states are not included",
        },
        "counts": dict(by_state),
        "pairs": sum(len(v) for v in neighbors.values()) // 2,
        "built": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "script": "projects/351watch/tools/neighbors.py",
    }
    out = {"_meta": meta}
    for key in sorted(neighbors, key=lambda k: (ORDER.index(k[:2]) if k[:2] in ORDER else 9, k)):
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

    missing = sorted({tid for tid in site_ids().values() if tid not in out})
    if missing:
        print(f"warning: {len(missing)} places have no boundary: {missing[:40]}", file=sys.stderr)

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
                                    "NY:Southold", "NY:Amsterdam", "NY:Geneva", "NY:Hempstead", "VA:Culpeper County",
                                    "MD:Baltimore City", "MI:Washtenaw County", "OH:Logan-Union-Champaign Regional Planning Commission"]:
            print(f"{town}: {', '.join(out.get(town, ['(not found)'])) or '(none)'}")
        print(f"spot checks: {len(CHECKS) - failed} of {len(CHECKS)} pass")

    # One place per line keeps git diffs readable; the file is still plain JSON.
    lines = [f"{json.dumps(k)}:{json.dumps(v, ensure_ascii=False, separators=(',', ':'))}" for k, v in out.items()]
    args.out.write_text("{\n" + ",\n".join(lines) + "\n}\n")
    sizes = [len(v) for k, v in out.items() if not k.startswith("_")]
    print(f"wrote {args.out}: {len(sizes)} places, {out['_meta']['pairs']} neighbor pairs, "
          f"median {sorted(sizes)[len(sizes) // 2]} neighbors, {sizes.count(0)} with none")
    return 1 if failed or missing else 0


if __name__ == "__main__":
    sys.exit(main())
