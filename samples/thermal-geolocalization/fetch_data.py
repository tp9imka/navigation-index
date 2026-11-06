"""Fetch a small subset of Thermal-UAV (SCC-Loc, HF FloralHercules/Thermal-UAV, Apache-2.0 card).

The bundle is one 19.9 GB ZIP (NUDT.zip). We read its central directory with HTTP range
requests and pull only:
  - N evenly spaced thermal frames per chosen flight + its Thermal_info.csv (GT pose)
  - the Changsha reference map ref.tif (2.8 GB deflated, 3.4 GB raw), streamed once to
    data/_full/, cropped to one GeoTIFF window per flight, then deleted (unless --keep-full)

Usage: python fetch_data.py [--n 20] [--keep-full]
"""
import argparse
import csv
import io
import json
import shutil
import sys
import time
import zipfile
import zlib
from pathlib import Path

import remote_zip

URL = "https://huggingface.co/datasets/FloralHercules/Thermal-UAV/resolve/main/NUDT.zip"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
REF_MEMBER = "Reference_map/changsha/ref.tif"
MAP_MARGIN_M = 700.0

# flight dir => condition label. test split + two fog flights from train (we do not train anything).
FLIGHTS = {
    "test/changsha/city1_300_ortho_day": "city-day",
    "test/changsha/city1_300_ortho_night": "city-night",
    "test/changsha/village1_300_ortho_day": "village-day",
    "test/changsha/village1_300_ortho_night": "village-night",
    "train/changsha/village2_300_ortho_day&fog": "village-day-fog",
    "train/changsha/village2_300_ortho_night&fog": "village-night-fog",
}
# validation-split flights, used only to check the gate revised on FLIGHTS
HELDOUT = {
    "valid/changsha/city7_300_ortho_night": "city-night",
    "valid/changsha/village5_300_ortho_day": "village-day",
    "valid/changsha/village5_300_ortho_night": "village-night",
}


def slug(flight):
    return flight.split("/")[-1].replace("&", "_")


def pick(rows, n):
    if len(rows) <= n:
        return rows
    step = (len(rows) - 1) / (n - 1)
    return [rows[round(i * step)] for i in range(n)]


def stream_member(z, f, name, dest, chunk=64 << 20):
    """Fetch one deflated member with large Range requests and inflate it locally.

    zipfile's own reader issues many small reads, about 1 MB/s over HTTP here; 64 MB ranges
    run at link speed.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    info = z.getinfo(name)
    if dest.exists() and dest.stat().st_size == info.file_size:
        return
    f.seek(info.header_offset)
    hdr = f.read(30)
    data_start = info.header_offset + 30 + int.from_bytes(hdr[26:28], "little") + int.from_bytes(hdr[28:30], "little")
    if info.compress_type != zipfile.ZIP_DEFLATED:
        raise RuntimeError(f"unexpected compression {info.compress_type}")
    inflate = zlib.decompressobj(-15)
    tmp = dest.with_suffix(dest.suffix + ".part")
    t0, pos, crc = time.time(), 0, 0
    with open(tmp, "wb") as out:
        while pos < info.compress_size:
            n = min(chunk, info.compress_size - pos)
            raw = inflate.decompress(f._range(data_start + pos, data_start + pos + n))
            crc = zlib.crc32(raw, crc)
            out.write(raw)
            pos += n
            print(f"  {name}: {pos >> 20} / {info.compress_size >> 20} MB, {time.time() - t0:.0f} s", flush=True)
        tail = inflate.flush()
        crc = zlib.crc32(tail, crc)
        out.write(tail)
    if crc != info.CRC:
        raise RuntimeError(f"CRC mismatch for {name}")
    tmp.rename(dest)


def crop_maps(full_tif, frames_by_flight):
    import rasterio
    from rasterio.warp import transform as warp_transform
    from rasterio.windows import Window, from_bounds

    out_dir = DATA / "maps"
    out_dir.mkdir(parents=True, exist_ok=True)
    with rasterio.open(full_tif) as src:
        print("ref.tif:", src.width, "x", src.height, src.count, "bands", src.crs, src.transform, src.dtypes)
        for flight, rows in frames_by_flight.items():
            dest = out_dir / f"{slug(flight)}.tif"
            if dest.exists():
                continue
            lons = [float(r["lon"]) for r in rows]
            lats = [float(r["lat"]) for r in rows]
            xs, ys = warp_transform("EPSG:4326", src.crs, lons, lats)
            win = from_bounds(min(xs) - MAP_MARGIN_M, min(ys) - MAP_MARGIN_M,
                              max(xs) + MAP_MARGIN_M, max(ys) + MAP_MARGIN_M, src.transform)
            win = win.round_offsets().round_lengths().intersection(Window(0, 0, src.width, src.height))
            data = src.read([1, 2, 3], window=win)
            prof = src.profile.copy()
            prof.update(driver="GTiff", width=win.width, height=win.height, count=3,
                        transform=src.window_transform(win), compress="deflate", tiled=True,
                        blockxsize=512, blockysize=512, photometric="RGB", BIGTIFF="NO")
            prof.pop("nodata", None)
            with rasterio.open(dest, "w", **prof) as dst:
                dst.write(data)
            print(f"  map {dest.name}: {win.width} x {win.height} px")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="frames per flight")
    ap.add_argument("--keep-full", action="store_true", help="keep the 3.4 GB ref.tif")
    ap.add_argument("--heldout", action="store_true", help="also fetch the validation-split flights")
    args = ap.parse_args()
    flights = {**FLIGHTS, **(HELDOUT if args.heldout else {})}

    f = remote_zip.HttpRangeFile(URL)
    z = zipfile.ZipFile(f)
    names = set(z.namelist())
    manifest = {"source": URL, "zip_bytes": f.size, "frames": []}
    frames_by_flight = {}
    for flight, cond in flights.items():
        base = f"Thermal-UAV/{flight}"
        text = z.read(f"{base}/Thermal_info.csv").decode("utf-8-sig")
        rows = [r for r in csv.DictReader(io.StringIO(text)) if f"{base}/Thermal/{r['filename']}" in names]
        chosen = pick(rows, args.n)
        frames_by_flight[flight] = chosen
        out = DATA / "frames" / slug(flight)
        out.mkdir(parents=True, exist_ok=True)
        for r in chosen:
            dest = out / r["filename"]
            if not dest.exists():
                dest.write_bytes(z.read(f"{base}/Thermal/{r['filename']}"))
            manifest["frames"].append({
                "flight": slug(flight), "condition": cond, "split": "heldout" if flight in HELDOUT else "main", "path": str(dest.relative_to(HERE)),
                "lat": float(r["lat"]), "lon": float(r["lon"]), "rel_height": float(r["rel_height"]),
                "yaw": float(r["yaw"]), "pitch": float(r["pitch"]), "date": r["date"]})
        print(f"{flight}: {len(chosen)} of {len(rows)} frames", flush=True)

    full = DATA / "_full" / "ref.tif"
    if not (DATA / "maps").exists() or any(not (DATA / "maps" / f"{slug(fl)}.tif").exists() for fl in flights):
        print("streaming", REF_MEMBER, "(2.8 GB compressed)", flush=True)
        stream_member(z, f, REF_MEMBER, full)
        crop_maps(full, frames_by_flight)
        if not args.keep_full:
            shutil.rmtree(full.parent)
    meta = json.loads(z.read("metadata/test_Thermal.json"))
    first = meta[0] if isinstance(meta, list) else next(iter(meta.values()))
    manifest["camera"] = {k: first[k] for k in ("cam_size", "focal_len", "width", "height")}
    manifest["bytes_fetched"] = f.bytes_fetched
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print("done; HTTP bytes fetched:", f.bytes_fetched >> 20, "MB", file=sys.stderr)


if __name__ == "__main__":
    main()
