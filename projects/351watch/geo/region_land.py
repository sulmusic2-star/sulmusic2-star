#!/usr/bin/env python3
"""Render a region's state outlines for the site's maps: geo/<group>_land.json, read by build.py's region_map_svg().

Source: US Census Bureau cartographic boundary files, states, 1:5,000,000 (cb_2023_us_state_5m.zip), public domain.
The group's states are drawn in full ("land"); the neighbouring states inside the frame are drawn faint and clipped
to it ("land_faint"). The frame is an equirectangular projection: x = (lon - lon0) * k * scale, y = (lat1 - lat) * scale,
with k = cos(mid latitude) and scale fitting the frame's width, the same formula as geo/region_land.json (the Northeast
map, rendered this way in October 2026).

    python3 -I geo/region_land.py ZIP GROUP STATES FAINT LON0 LON1 LAT0 LAT1 OUT [WIDTH] [TOLERANCE]
    python3 -I geo/region_land.py cb_2023_us_state_5m.zip va-md VA,MD NC,TN,KY,WV,DC,DE,PA,NJ,OH -83.9 -74.9 36.4 39.9 geo/va-md_land.json
    python3 -I geo/region_land.py cb_2023_us_state_5m.zip mi-oh MI,OH WI,IN,IL,KY,WV,PA,NY,MN -90.6 -80.3 38.2 48.4 geo/mi-oh_land.json
"""
import io
import json
import math
import sys
import zipfile

import shapefile  # pyshp
from shapely.geometry import box, shape
from shapely.geometry import MultiPolygon, Polygon


def read_states(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        stem = next(n[:-4] for n in zf.namelist() if n.endswith(".shp"))
        files = {ext: io.BytesIO(zf.read(f"{stem}.{ext}")) for ext in ("shp", "shx", "dbf")}
    reader = shapefile.Reader(shp=files["shp"], shx=files["shx"], dbf=files["dbf"], encoding="utf-8")
    fields = [f[0] for f in reader.fields[1:]]
    out = {}
    for sr in reader.iterShapeRecords():
        rec = dict(zip(fields, sr.record))
        out[rec["STUSPS"]] = shape(sr.shape.__geo_interface__)
    return out


def polygons(geom):
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def path_d(geom, X, Y, min_area):
    parts = []
    for poly in polygons(geom):
        if poly.area < min_area:
            continue
        for ring in [poly.exterior] + list(poly.interiors):
            pts = [f"{X(lon):.1f} {Y(lat):.1f}" for lon, lat in ring.coords]
            if len(pts) < 4:
                continue
            parts.append("M" + " ".join(pts[:-1]) + "Z")
    return "".join(parts)


def main():
    a = sys.argv[1:]
    if len(a) < 9:
        sys.exit(__doc__)
    zip_path, group, states, faint = a[0], a[1], a[2].split(","), [s for s in a[3].split(",") if s]
    lon0, lon1, lat0, lat1 = map(float, a[4:8])
    out = a[8]
    width = int(a[9]) if len(a) > 9 else 686
    tol = float(a[10]) if len(a) > 10 else 0.012
    k = math.cos(math.radians((lat0 + lat1) / 2))
    scale = width / ((lon1 - lon0) * k)
    height = round((lat1 - lat0) * scale)
    X = lambda lon: (lon - lon0) * k * scale
    Y = lambda lat: (lat1 - lat) * scale
    frame = box(lon0 - 0.3, lat0 - 0.3, lon1 + 0.3, lat1 + 0.3)
    shapes = read_states(zip_path)
    land = "".join(f'<path d="{path_d(shapes[s].simplify(tol, preserve_topology=True), X, Y, 0.0015)}"/>' for s in states)
    land_faint = "".join(
        f'<path d="{path_d(shapes[s].intersection(frame).simplify(tol, preserve_topology=True), X, Y, 0.003)}"/>'
        for s in faint if s in shapes and shapes[s].intersects(frame))
    doc = {"lon0": lon0, "lon1": lon1, "lat0": lat0, "lat1": lat1, "width": width, "height": height, "k": k, "scale": scale,
           "land_faint": land_faint, "land": land,
           "source": "US Census Bureau cartographic boundary files, states, 1:5,000,000 (cb_2023_us_state_5m), public domain; simplified",
           "group": group, "states": states, "faint": faint}
    with open(out, "w") as f:
        json.dump(doc, f)
    print(f"{out}: {width}x{height}, land {len(land):,} chars, faint {len(land_faint):,} chars")


if __name__ == "__main__":
    main()
