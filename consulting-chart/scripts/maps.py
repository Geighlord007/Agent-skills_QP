import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLD_CANDIDATES = (
    ROOT / "assets" / "geo" / "world-110m.geojson",
    ROOT / "vendor" / "geo" / "world-110m.geojson",
)

_cache = None


def resolve_world_geojson():
    for candidate in WORLD_CANDIDATES:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(p) for p in WORLD_CANDIDATES)
    raise FileNotFoundError(
        f"未找到世界地图底图 world-110m.geojson (已查找: {searched})。"
        "请将 Natural Earth 110m Admin 0 Countries GeoJSON 放置于 assets/geo/world-110m.geojson。"
    )


def world():
    global _cache
    if _cache is None:
        with resolve_world_geojson().open(encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def iso(feature):
    p = feature["properties"]
    return p.get("ISO_A3") if p.get("ISO_A3") not in (None, "-99") else p.get("ADM0_A3")


def features():
    return [f for f in world()["features"] if iso(f) not in ("ATA", None, "-99")]


def rings(feature):
    g = feature.get("geometry")
    if not g:
        return
    if g["type"] == "Polygon":
        polys = [g["coordinates"]]
    elif g["type"] == "MultiPolygon":
        polys = g["coordinates"]
    else:
        return
    for poly in polys:
        for ring in poly:
            yield ring


def merc(lat):
    lat = max(min(lat, 85.0), -60.0)
    return math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def projector(feats, x0, y0, x1, y1):
    xs, ys = [], []
    for f in feats:
        for ring in rings(f):
            for lon, lat in ring:
                xs.append(lon)
                ys.append(merc(lat))
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    scale = min((x1 - x0) / (maxx - minx), (y1 - y0) / (maxy - miny))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    clon, cmy = (minx + maxx) / 2, (miny + maxy) / 2
    return lambda lon, lat: (cx + (lon - clon) * scale, cy - (merc(lat) - cmy) * scale)


def path_d(feature, project):
    parts = []
    for ring in rings(feature):
        pts = [project(lon, lat) for lon, lat in ring]
        if len(pts) < 3:
            continue
        if max(p[0] for p in pts) - min(p[0] for p in pts) > 620:
            continue
        d = "M" + " L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts) + " Z"
        parts.append(d)
    return " ".join(parts)


def centroid(feature, project):
    g = feature.get("geometry")
    if not g:
        return None
    if g["type"] == "Polygon":
        polys = [g["coordinates"]]
    elif g["type"] == "MultiPolygon":
        polys = g["coordinates"]
    else:
        return None
    best = max((poly[0] for poly in polys), key=len, default=None)
    if not best:
        return None
    lon = sum(p[0] for p in best) / len(best)
    lat = sum(p[1] for p in best) / len(best)
    return project(lon, lat)
