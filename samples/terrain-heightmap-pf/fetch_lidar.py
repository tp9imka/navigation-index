"""Fetch a 1 m airborne-LiDAR DSM (DOM1) and DTM (DGM1) mosaic from Geobasis NRW open data.

Licence: Datenlizenz Deutschland - Zero - Version 2.0 (https://www.govdata.de/dl-de/zero-2-0),
per "Nutzung von Geobasisdaten ... unter Open Data-Prinzipien", Bezirksregierung Koeln, 3/2020.
Tiles are 1 x 1 km GeoTIFFs in ETRS89 / UTM 32N (EPSG:25832), 1 m grid, ~2.5 MB each.
Writes data/<name>.npz with dsm, dtm (row 0 = southern edge), res=1.
"""
import argparse
import os
import urllib.request

import numpy as np
import rasterio

BASE = "https://www.opengeodata.nrw.de/produkte/geobasis/hm/{p}_tiff/{p}_tiff/{p}_32_{e}_{n}_1_nw_{y}.tif"
# name => (east_km_min, north_km_min, size_km, year, description)
AREAS = {
    "duelmen": (379, 5741, 4, 2024,
                "Duelmen, Muensterland, NRW: small town, farmland, hedgerows, forest; flat (50-100 m)"),
}
HERE = os.path.dirname(os.path.abspath(__file__))


def tile(product, e, n, year, cache):
    url = BASE.format(p=product, e=e, n=n, y=year)
    path = os.path.join(cache, os.path.basename(url))
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path + ".part")
        os.replace(path + ".part", path)
    with rasterio.open(path) as src:
        a = src.read(1).astype(np.float32)
        assert src.res == (1.0, 1.0) and a.shape == (1000, 1000), (src.res, a.shape)
        assert abs(src.bounds.left - e * 1000) < 1 and abs(src.bounds.bottom - n * 1000) < 1
        if src.nodata is not None:
            a[a == src.nodata] = np.nan
    return a[::-1]


def fetch(name, data_dir):
    e0, n0, k, year, _ = AREAS[name]
    cache = os.path.join(data_dir, "nrw_tiles")
    os.makedirs(cache, exist_ok=True)
    out = {}
    for product, key in (("dom1", "dsm"), ("dgm1", "dtm")):
        m = np.empty((k * 1000, k * 1000), np.float32)
        for di in range(k):
            for dj in range(k):
                m[di * 1000:(di + 1) * 1000, dj * 1000:(dj + 1) * 1000] = tile(product, e0 + dj, n0 + di, year, cache)
        assert not np.isnan(m).any(), f"{product}: nodata in mosaic"
        out[key] = m
    path = os.path.join(data_dir, f"{name}.npz")
    np.savez_compressed(path, dsm=out["dsm"], dtm=out["dtm"], res=1.0, epsg=25832,
                        origin_utm=np.array([e0 * 1000.0, n0 * 1000.0]))
    print(f"{name}: {k}x{k} km at 1 m, dsm {out['dsm'].min():.0f}..{out['dsm'].max():.0f} m, "
          f"dtm {out['dtm'].min():.0f}..{out['dtm'].max():.0f} m => {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "data"))
    ap.add_argument("areas", nargs="*", default=list(AREAS))
    a = ap.parse_args()
    for name in a.areas:
        fetch(name, a.out)
