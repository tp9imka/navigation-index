"""Fetch Copernicus GLO-30 windows for the evaluation regions and reproject to a local UTM grid.

Reads only the needed window of each public COG over HTTPS (no login), reprojects to
UTM at 30 m, flips rows so row 0 is the southern edge, and caches data/<region>.npz.
"""
import argparse
import os

import numpy as np
import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject
from rasterio.windows import from_bounds

URL = "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{t}_DEM/Copernicus_DSM_COG_10_{t}_DEM.tif"
RES_M = 30.0

# (lon_min, lat_min, lon_max, lat_max), tile, UTM EPSG, description
REGIONS = {
    "hilly": ((13.30, 48.70, 13.51, 48.84), "N48_00_E013_00", 32633,
              "Bavarian Forest foothills near Grafenau, DE: rolling hills, valleys, forest"),
    "flat": ((20.40, 47.30, 20.61, 47.44), "N47_00_E020_00", 32634,
             "Great Hungarian Plain near Kisujszallas, HU: flat farmland, few villages"),
    "mixed": ((11.78, 48.24, 11.99, 48.38), "N48_00_E011_00", 32632,
              "Erding, DE (SPRIN-D challenge area): flat-to-gentle, town, airbase, forest patches"),
}


def fetch(name, out_dir):
    bounds, tile, epsg, _ = REGIONS[name]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open("/vsicurl/" + URL.format(t=tile)) as src:
            win = from_bounds(*bounds, transform=src.transform)
            data = src.read(1, window=win).astype(np.float32)
            src_tf = src.window_transform(win)
            src_crs = src.crs
    h, w = data.shape
    left, bottom, right, top = rasterio.transform.array_bounds(h, w, src_tf)
    dst_crs = f"EPSG:{epsg}"
    tf, dw, dh = calculate_default_transform(src_crs, dst_crs, w, h, left, bottom, right, top, resolution=RES_M)
    dst = np.full((dh, dw), np.nan, np.float32)
    reproject(data, dst, src_transform=src_tf, src_crs=src_crs, dst_transform=tf, dst_crs=dst_crs,
              resampling=Resampling.bilinear, dst_nodata=np.nan)
    # crop the NaN rim left by the lat/lon => UTM rotation: drop the worst border until clean
    r0, r1, c0, c1 = 0, dst.shape[0], 0, dst.shape[1]
    while True:
        sub = np.isnan(dst[r0:r1, c0:c1])
        edges = [sub[0].sum(), sub[-1].sum(), sub[:, 0].sum(), sub[:, -1].sum()]
        if max(edges) == 0:
            break
        k = int(np.argmax(edges))
        r0, r1, c0, c1 = (r0 + (k == 0), r1 - (k == 1), c0 + (k == 2), c1 - (k == 3))
    dst = dst[r0:r1, c0:c1]
    assert not np.isnan(dst).any()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.npz")
    np.savez_compressed(path, dem=dst[::-1].copy(), res=RES_M, epsg=epsg, bounds_lonlat=np.array(bounds))
    print(f"{name}: {dst.shape[1]}x{dst.shape[0]} cells ({dst.shape[1]*RES_M/1000:.1f} x {dst.shape[0]*RES_M/1000:.1f} km), "
          f"h {np.nanmin(dst):.0f}..{np.nanmax(dst):.0f} m => {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
    ap.add_argument("regions", nargs="*", default=list(REGIONS))
    a = ap.parse_args()
    for r in a.regions:
        fetch(r, a.out)
