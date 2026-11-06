"""On-land masks from Natural Earth 10m land polygons (public domain), via pyshp + shapely.

The 10m coastline is generalised (harbours, canals and narrow fjords are missing), so the
land polygon is eroded inward by margin_m before testing. Points outside the
0.1-99.9 percentile box (+0.5 deg) of all positions are never tested. Points in canals and rivers that
Natural Earth draws as land still come out as on-land: see README.
"""
import io
import math
import urllib.request
import zipfile
from pathlib import Path

NE_LAND_URL = "https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip"
DEFAULT_MARGIN_M = 1000.0
BBOX_PAD_DEG = 0.5
BBOX_PCT = 0.1        # outlier positions (often spoofed or corrupt) must not blow up the clip box
M_PER_DEG_LAT = 111_320.0


def fetch_land(out_dir):
    out = Path(out_dir) / "ne_10m_land.shp"
    if not out.exists():
        z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(NE_LAND_URL, timeout=300).read()))
        for n in z.namelist():
            if n.startswith("ne_10m_land."):
                (Path(out_dir) / n).write_bytes(z.read(n))
    return out


def land_geometry(shp_path, bbox, margin_m=DEFAULT_MARGIN_M):
    """bbox = (lon_min, lat_min, lon_max, lat_max). Returns (geometry, kx) in a lon-scaled frame."""
    import shapefile
    from shapely import box, transform
    from shapely.geometry import shape
    from shapely.ops import unary_union

    lon0, lat0, lon1, lat1 = bbox
    clip = box(lon0 - BBOX_PAD_DEG, lat0 - BBOX_PAD_DEG, lon1 + BBOX_PAD_DEG, lat1 + BBOX_PAD_DEG)
    r = shapefile.Reader(str(shp_path))
    parts = [shape(s.__geo_interface__).intersection(clip) for s in r.shapes()
             if box(*s.bbox).intersects(clip)]
    land = unary_union([p for p in parts if not p.is_empty])
    kx = math.cos(math.radians(0.5 * (lat0 + lat1)))
    scaled = transform(land, lambda c: c * [kx, 1.0])
    return scaled.buffer(-margin_m / M_PER_DEG_LAT), kx


def masks_for_tracks(tracks, shp_path, margin_m=DEFAULT_MARGIN_M):
    import numpy as np
    import shapely
    lats = np.concatenate([[f.lat for f in t.fixes] for t in tracks])
    lons = np.concatenate([[f.lon for f in t.fixes] for t in tracks])
    lo, hi = np.percentile(lons, [BBOX_PCT, 100 - BBOX_PCT]), np.percentile(lats, [BBOX_PCT, 100 - BBOX_PCT])
    geom, kx = land_geometry(shp_path, (lo[0], hi[0], lo[1], hi[1]), margin_m)
    shapely.prepare(geom)
    inside = shapely.contains_xy(geom, lons * kx, lats)
    out, k = {}, 0
    for t in tracks:
        n = len(t.fixes)
        out[t.mmsi] = inside[k:k + n].tolist()
        k += n
    return out
