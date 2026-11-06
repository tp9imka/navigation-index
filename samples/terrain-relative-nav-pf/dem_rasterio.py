"""Load a real DEM (e.g. Copernicus GLO-30) into the same Dem class the filter uses.

Unverified sketch: requires `rasterio` (pip install rasterio). GLO-30 tiles are
geographic (EPSG:4326, 1 arc-second); the filter works in metres, so the tile is
reprojected on read to a UTM zone through a WarpedVRT.

Usage:
    python3 dem_rasterio.py Copernicus_DSM_COG_10_N47_00_E008_00_DEM.tif 32632
"""

import sys

import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from terrain import Dem

NODATA_FILL_M = 0.0


def load_dem(path, utm_epsg):
    with rasterio.open(path) as src:
        with WarpedVRT(src, crs=CRS.from_epsg(utm_epsg), resampling=Resampling.bilinear) as vrt:
            band = vrt.read(1, masked=True)
            t = vrt.transform
            heights = band.filled(NODATA_FILL_M).astype(float).tolist()
    # Dem indexes pixel centres; the affine transform points at the top-left corner.
    return Dem(heights, t.c + t.a / 2, t.f + t.e / 2, t.a, t.e)


if __name__ == "__main__":
    dem = load_dem(sys.argv[1], int(sys.argv[2]))
    cx = dem.x0 + dem.dx * dem.cols / 2
    cy = dem.y0 + dem.dy * dem.rows / 2
    print(f"{dem.rows}x{dem.cols} cells, dx={dem.dx:.1f} dy={dem.dy:.1f}, "
          f"centre ({cx:.0f}, {cy:.0f}) height {dem.height(cx, cy):.1f} m")
