"""Fetch the public-domain / CC0 inputs for the sample into ./data (git-ignored).

1. A NAIP RGB window (USDA aerial orthophoto, public domain) around Aukerman Park, Ohio,
   read straight from the Cloud-Optimized GeoTIFF on Microsoft Planetary Computer.
2. A few raw eBee frames from OpenDroneMap/odm_data_aukerman (CC0-1.0), with EXIF GPS.
"""
import argparse
import json
import pathlib
import urllib.request

import rasterio
from rasterio.warp import transform as warp_transform
from rasterio.merge import merge

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/naip"
AUKERMAN_RAW = "https://raw.githubusercontent.com/OpenDroneMap/odm_data_aukerman/master/images/"
DEFAULT_FRAMES = ["DSC00229.JPG", "DSC00240.JPG", "DSC00255.JPG", "DSC00270.JPG", "DSC00285.JPG"]
CENTER_LON, CENTER_LAT = -81.7505, 41.3036
HALF_SIZE_M = 1000


def get_json(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_naip(out: pathlib.Path, year=None):
    res = get_json(STAC, {"collections": ["naip"],
                          "intersects": {"type": "Point", "coordinates": [CENTER_LON, CENTER_LAT]},
                          "sortby": [{"field": "properties.datetime", "direction": "desc"}],
                          "limit": 20})
    if not res["features"]:
        raise SystemExit("no NAIP item covers the point")
    year = year or res["features"][0]["properties"]["datetime"][:4]
    items = [f for f in res["features"] if f["properties"]["datetime"].startswith(year)]
    token = get_json(SAS)["token"]
    hrefs = [f["assets"]["image"]["href"] + "?" + token for f in items]
    print(f"NAIP {year}: {[f['id'] for f in items]}")
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY="3"):
        srcs = [rasterio.open(h) for h in hrefs]
        crs = srcs[0].crs
        xs, ys = warp_transform("EPSG:4326", crs, [CENTER_LON], [CENTER_LAT])
        bounds = (xs[0] - HALF_SIZE_M, ys[0] - HALF_SIZE_M, xs[0] + HALF_SIZE_M, ys[0] + HALF_SIZE_M)
        rgb, tr = merge(srcs, bounds=bounds, indexes=[1, 2, 3])
        for s in srcs:
            s.close()
    profile = {"driver": "GTiff", "dtype": rgb.dtype, "count": 3, "width": rgb.shape[2],
               "height": rgb.shape[1], "crs": crs, "transform": tr, "compress": "deflate",
               "tiled": True, "photometric": "RGB"}
    with rasterio.open(out, "w", **profile) as dst:
        dst.write(rgb)
    out.with_suffix(".json").write_text(json.dumps(
        {"items": [f["id"] for f in items], "datetime": items[0]["properties"]["datetime"],
         "gsd_m": items[0]["properties"].get("gsd"), "crs": str(crs), "bounds": bounds,
         "source": "Microsoft Planetary Computer STAC collection naip"}, indent=2))
    print(f"wrote {out} {rgb.shape[2]}x{rgb.shape[1]} px, crs={crs}")


def fetch_frames(out_dir: pathlib.Path, names):
    out_dir.mkdir(parents=True, exist_ok=True)
    for n in names:
        p = out_dir / n
        if p.exists():
            continue
        urllib.request.urlretrieve(AUKERMAN_RAW + n, p)
        print(f"wrote {p} ({p.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(pathlib.Path(__file__).parent / "data"))
    ap.add_argument("--frames", nargs="*", default=DEFAULT_FRAMES)
    ap.add_argument("--season-year", default="2019",
                    help="older NAIP year used as the source of cross-season synthetic frames ('' to skip)")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if not (out / "naip_aukerman.tif").exists():
        fetch_naip(out / "naip_aukerman.tif")
    if a.season_year and not (out / f"naip_aukerman_{a.season_year}.tif").exists():
        fetch_naip(out / f"naip_aukerman_{a.season_year}.tif", a.season_year)
    fetch_frames(out / "uav", a.frames)
