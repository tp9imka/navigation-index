"""Terrain under the VPAIR flight: projections, NRW 1 m DSM mosaic, GLO-30 on the same grid.

Grid frame: east/north metres from the mosaic's south-west corner in ETRS89 / UTM 32N
(EPSG:25832), row 0 = southern edge, cell (i, j) at north = i * res, east = j * res (the
convention of ../terrain-heightmap-pf/core.py). The e2e sample works in a local tangent
East/North frame from the first query; `Frames` converts between the two through lat/lon.
"""
import glob
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
E2E = os.path.join(HERE, "..", "e2e-visual-nav-vpair")
sys.path.insert(0, E2E)
import nav_core as nc  # noqa: E402

UTM = "EPSG:25832"
GLO30_URL = ("https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N50_00_E007_00_DEM/"
             "Copernicus_DSM_COG_10_N50_00_E007_00_DEM.tif")


def _to_utm(lon, lat):
    from rasterio.warp import transform
    e, n = transform("EPSG:4326", UTM, list(map(float, lon)), list(map(float, lat)))
    return np.array(e), np.array(n)


def _to_ll(e, n):
    from rasterio.warp import transform
    lon, lat = transform(UTM, "EPSG:4326", list(map(float, e)), list(map(float, n)))
    return np.array(lat), np.array(lon)


def query_lla(vpair_dir):
    """lat, lon, height above mean sea level (ellipsoid height minus the file's undulation)."""
    rows = [l.strip().split(",") for l in open(os.path.join(vpair_dir, "poses_query.txt")) if l.strip()][1:]
    lla = np.array([nc.ecef_to_lla(*map(float, r[1:4])) for r in rows])
    und = np.array([float(r[4]) for r in rows])
    return lla[:, 0], lla[:, 1], lla[:, 2] - und


def track_utm(vpair_dir):
    lat, lon, msl = query_lla(vpair_dir)
    e, n = _to_utm(lon, lat)
    return np.stack([e, n, msl], 1)


class Frames:
    """local EN (nav_core, spherical tangent at the first query) <=> grid (UTM minus origin)."""

    def __init__(self, lat0, lon0, origin):
        self.lat0, self.lon0, self.origin = lat0, lon0, np.asarray(origin, float)

    def en_to_grid(self, en):
        en = np.atleast_2d(en)
        ll = np.array([nc.common.enu_to_ll(self.lat0, self.lon0, float(p[0]), float(p[1])) for p in en])
        e, n = _to_utm(ll[:, 1], ll[:, 0])
        return np.stack([e, n], 1) - self.origin

    def grid_to_en(self, g):
        g = np.atleast_2d(g) + self.origin
        lat, lon = _to_ll(g[:, 0], g[:, 1])
        return np.array([nc.common.ll_to_enu(self.lat0, self.lon0, a, b) for a, b in zip(lat, lon)])

    def rotation_deg(self, en):
        """Angle from local-EN to grid axes along the track (UTM grid convergence + tangent-plane effects)."""
        g = self.en_to_grid(en)
        d0, d1 = np.diff(en, axis=0), np.diff(g, axis=0)
        return math.degrees(math.atan2(np.sum(d0[:, 0] * d1[:, 1] - d0[:, 1] * d1[:, 0]), np.sum(d0 * d1)))


def load_dsm(cache):
    """Mosaic every cached DOM1 tile into one 1 m grid. Missing tiles stay NaN."""
    import rasterio
    files = sorted(glob.glob(os.path.join(cache, "dom1_32_*_*_1_nw_*.tif")))
    if not files:
        raise FileNotFoundError(f"no DOM1 tiles in {cache}; run fetch_terrain.py")
    keys = [tuple(int(x) for x in os.path.basename(f).split("_")[2:4]) for f in files]
    e0, n0 = min(k[0] for k in keys), min(k[1] for k in keys)
    e1, n1 = max(k[0] for k in keys) + 1, max(k[1] for k in keys) + 1
    dsm = np.full(((n1 - n0) * 1000, (e1 - e0) * 1000), np.nan, np.float32)
    for f, (ek, nk) in zip(files, keys):
        with rasterio.open(f) as src:
            a = src.read(1).astype(np.float32)
            assert src.res == (1.0, 1.0) and a.shape == (1000, 1000)
            if src.nodata is not None:
                a[a == src.nodata] = np.nan
        r, c = (nk - n0) * 1000, (ek - e0) * 1000
        dsm[r:r + 1000, c:c + 1000] = a[::-1]
    return dsm, np.array([e0 * 1000.0, n0 * 1000.0])


def glo30_on_grid(origin, shape_m, res=30.0, cache=None):
    """Copernicus GLO-30 reprojected (bilinear) onto the mosaic grid at `res`. Cached as .npy."""
    path = cache and os.path.join(cache, f"glo30_{int(origin[0])}_{int(origin[1])}_{int(res)}.npy")
    if path and os.path.exists(path):
        return np.load(path)
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.warp import Resampling, reproject
    h, w = int(shape_m[0] // res), int(shape_m[1] // res)
    dst = np.full((h, w), np.nan, np.float32)
    tf = from_origin(origin[0], origin[1] + h * res, res, res)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open("/vsicurl/" + GLO30_URL) as src:
            reproject(rasterio.band(src, 1), dst, dst_transform=tf, dst_crs=UTM, resampling=Resampling.bilinear,
                      dst_nodata=np.nan)
    out = dst[::-1].copy()
    if path:
        np.save(path, out)
    return out


def block_mean(a, k):
    """Block average (NaN-aware: a block with any valid cell keeps their mean)."""
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    b = a[:h, :w].reshape(h // k, k, w // k, k)
    with np.errstate(invalid="ignore"):
        return np.nanmean(b, axis=(1, 3)) if np.isnan(b).any() else b.mean(axis=(1, 3))


def fill_nearest(a):
    """NaN cells take the value of the nearest valid cell (flat, featureless extension)."""
    from scipy.ndimage import distance_transform_edt
    bad = ~np.isfinite(a)
    if not bad.any():
        return a, bad
    idx = distance_transform_edt(bad, return_distances=False, return_indices=True)
    return a[tuple(idx)], bad
