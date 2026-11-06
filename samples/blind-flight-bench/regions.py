"""Benchmark regions: Copernicus GLO-30 windows fetched through terrain-heightmap-pf/fetch_dem.py.

Each window lies inside one 1x1 degree GLO-30 tile (fetch_dem reads a single COG) and all
terrain stays well below the case's 1500 m MSL flight level.
"""
import os


import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from ext import fetch_dem  # noqa: E402

DATA_DIR = os.path.join(HERE, "data")

# (lon_min, lat_min, lon_max, lat_max), tile, UTM EPSG, description
REGIONS = {
    "khibiny": ((33.05, 67.50, 33.95, 67.84), "N67_00_E033_00", 32636,
                "Khibiny massif, Kola peninsula, RU: Arctic mountains up to ~1200 m, lakes, tundra"),
    "ural": ((59.15, 58.55, 59.80, 58.88), "N58_00_E059_00", 32640,
             "Middle Urals near Kachkanar, RU: forested ridges 200-880 m"),
    "taiga": ((89.10, 61.30, 89.80, 61.62), "N61_00_E089_00", 32645,
              "Yenisei ridge taiga near the GORIZONT test area (61.5 N, 89.1 E), RU: dissected plateau"),
    "flat": ((37.30, 55.02, 37.87, 55.34), "N55_00_E037_00", 32637,
             "South of Moscow inside the 55-56 N, 37-38 E map.tif bounds KROT cites, RU: low plain, fields, forest, towns"),
}


def ensure(name):
    path = os.path.join(DATA_DIR, f"{name}.npz")
    if not os.path.exists(path):
        fetch_dem.REGIONS[name] = REGIONS[name]
        fetch_dem.fetch(name, DATA_DIR)
    d = np.load(path)
    return d["dem"].astype(np.float64), float(d["res"])


if __name__ == "__main__":
    for r in sys.argv[1:] or list(REGIONS):
        dem, res = ensure(r)
        print(f"{r}: {dem.shape[1]}x{dem.shape[0]} cells, {dem.min():.0f}..{dem.max():.0f} m")
