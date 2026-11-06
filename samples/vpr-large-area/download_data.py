"""Fetch a 7 km x 7 km (49 km2) NAIP area around Aukerman Park, Ohio, for several years, plus CC0 eBee frames.

NAIP (USDA, public domain) is read straight from the Planetary Computer COGs at a reduced resolution
(GDAL picks the overview), mosaicking the 4 quarter-quads that cover the area. Output in UTM 17N.
eBee frames come from OpenDroneMap/odm_data_aukerman (CC0-1.0); the helpers are imported from
../geoloc-license-clean/download_data.py.
"""
import argparse
import json
import pathlib
import sys

import rasterio
import rasterio.errors
from rasterio.enums import Resampling
from rasterio.merge import merge
from rasterio.warp import transform as warp_transform

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "geoloc-license-clean"))
from download_data import SAS, STAC, fetch_frames, get_json  # noqa: E402

CENTER_LON, CENTER_LAT = -81.7505, 41.3036
HALF_SIZE_M = 3500
UTM17N = "EPSG:26917"
FETCH_ATTEMPTS = 3
# year => output GSD in metres (2023 native is 0.3 m, read from its overview at 0.6 m)
YEARS = {"2023": 0.6, "2021": 0.6, "2019": 0.6, "2017": 1.0, "2015": 1.0}
# every 4th frame of the 77-image survey, plus the 5 used by geoloc-license-clean
EBEE_FRAMES = sorted({f"DSC{n:05d}.JPG" for n in
                      [229, 233, 237, 241, 246, 252, 256, 260, 265, 270, 274, 278, 282, 286, 290, 294,
                       298, 302, 306, 310, 240, 255, 285]})


def fetch_ground_elevation(uav_dir: pathlib.Path):
    """USGS 3DEP 1/3 arc-second DEM (public domain) under each frame's EXIF GPS => ground_elev.json."""
    from PIL import Image
    gps = {}
    for p in sorted(uav_dir.glob("*.JPG")):
        g = Image.open(p).getexif().get_ifd(0x8825)
        dms = lambda v: float(v[0]) + float(v[1]) / 60 + float(v[2]) / 3600
        gps[p.name] = (dms(g[4]) * (1 if g[3] == "E" else -1), dms(g[2]) * (1 if g[1] == "N" else -1), float(g[6]))
    lon, lat = next(iter(gps.values()))[:2]
    res = get_json(STAC, {"collections": ["3dep-seamless"], "intersects": {"type": "Point", "coordinates": [lon, lat]},
                          "limit": 10})
    item = min(res["features"], key=lambda f: f["properties"].get("gsd", 1e9))
    token = get_json(SAS.rsplit("/", 1)[0] + "/3dep-seamless")["token"]
    out = {"dem_item": item["id"], "dem_gsd_m": item["properties"].get("gsd"), "frames": {}}
    with rasterio.open(item["assets"]["data"]["href"] + "?" + token) as src:
        for name, (lo, la, alt) in gps.items():
            x, y = warp_transform("EPSG:4326", src.crs, [lo], [la])
            out["frames"][name] = {"lon": lo, "lat": la, "exif_alt_m": alt,
                                   "ground_m": float(next(src.sample([(x[0], y[0])]))[0])}
    (uav_dir / "ground_elev.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {uav_dir / 'ground_elev.json'}")


def area_bounds():
    xs, ys = warp_transform("EPSG:4326", UTM17N, [CENTER_LON], [CENTER_LAT])
    return xs[0] - HALF_SIZE_M, ys[0] - HALF_SIZE_M, xs[0] + HALF_SIZE_M, ys[0] + HALF_SIZE_M


def fetch_year(out: pathlib.Path, year: str, gsd: float):
    b = area_bounds()
    lons, lats = warp_transform(UTM17N, "EPSG:4326", [b[0], b[2]], [b[1], b[3]])
    res = get_json(STAC, {"collections": ["naip"], "bbox": [lons[0], lats[0], lons[1], lats[1]],
                          "datetime": f"{year}-01-01T00:00:00Z/{year}-12-31T23:59:59Z", "limit": 50})
    items = res["features"]
    if not items:
        raise SystemExit(f"no NAIP {year} items over the area")
    token = get_json(SAS)["token"]
    print(f"NAIP {year}: {[f['id'] for f in items]}")
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY="5", GDAL_HTTP_RETRY_DELAY="3"):
        srcs = [rasterio.open(f["assets"]["image"]["href"] + "?" + token) for f in items]
        if any(str(s.crs) != UTM17N for s in srcs):
            raise SystemExit(f"unexpected CRS {[str(s.crs) for s in srcs]}")
        rgb, tr = merge(srcs, bounds=b, res=gsd, indexes=[1, 2, 3], resampling=Resampling.average)
        for s in srcs:
            s.close()
    profile = {"driver": "GTiff", "dtype": rgb.dtype, "count": 3, "width": rgb.shape[2], "height": rgb.shape[1],
               "crs": UTM17N, "transform": tr, "compress": "deflate", "tiled": True, "photometric": "RGB"}
    with rasterio.open(out, "w", **profile) as dst:
        dst.write(rgb)
    out.with_suffix(".json").write_text(json.dumps(
        {"items": [f["id"] for f in items], "datetime": sorted(f["properties"]["datetime"] for f in items),
         "native_gsd_m": items[0]["properties"].get("gsd"), "gsd_m": gsd, "crs": UTM17N, "bounds": b,
         "source": "Microsoft Planetary Computer STAC collection naip"}, indent=2))
    print(f"wrote {out} {rgb.shape[2]}x{rgb.shape[1]} px")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "data"))
    ap.add_argument("--years", nargs="*", default=list(YEARS))
    ap.add_argument("--frames", nargs="*", default=EBEE_FRAMES)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for y in a.years:
        p = out / f"naip_{y}.tif"
        for attempt in range(FETCH_ATTEMPTS):
            if p.exists():
                break
            try:
                fetch_year(p, y, YEARS[y])
            except rasterio.errors.RasterioIOError as e:  # truncated HTTP range reads happen on long runs
                print(f"NAIP {y} attempt {attempt + 1} failed: {e}")
    fetch_frames(out / "uav", a.frames)
    if not (out / "uav" / "ground_elev.json").exists():
        fetch_ground_elevation(out / "uav")
