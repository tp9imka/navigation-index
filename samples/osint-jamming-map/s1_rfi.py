"""Sentinel-1 RFI over one area, from Microsoft Planetary Computer (no login).

Two independent signals per scene of one relative-orbit stack:

1. ESA's own RFI annotation (annotation/rfi/rfi-iw-<pol>.xml, IPF >= 3.40). On Planetary
   Computer it is the asset mislabelled `schema-product-<pol>`. Per noise-sensing pulse
   per swath: rfiDetected, maxKLDivergence, maxFisherZ, maxRfiPsd; per burst:
   inBandOutBandPowerRatio.
2. A port of zephr-xyz/sentinel1-rfi-detection temporal_rfi.py: VH backscatter at 1/8
   resolution, scene-median normalisation, DEM slope mask, 0.01 deg baseline grid,
   per-pixel z-score, z > 3 flags. Deviation: the scored scene is left out of its own
   baseline (zephr includes it).

Usage: python s1_rfi.py --date 2026-10-01 --orbit 51 --point 20.5 54.7
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import h3
import numpy as np
import rasterio
from rasterio.enums import Resampling
from scipy.interpolate import RectBivariateSpline

log = logging.getLogger("s1_rfi")
HERE = Path(__file__).parent
STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

# zephr temporal_rfi.py / rfi_pipeline.py constants, unchanged
SUBSAMPLE = 8
GRID_RES = 0.01
Z_THRESHOLD = 3.0
MIN_OBS = 3
STD_FLOOR_DB = 0.5
SLOPE_THRESHOLD_DEG = 15.0
DEM_RES = 0.003
MIN_VALID_PX = 1000

# this sample's aggregation, not zephr's
HEX_RES = 5
MIN_HEX_PX = 500            # valid pixels a hex needs on the target date to be scored
MIN_PCT_Z3 = 1.0            # % of pixels over z=3 a hex needs to be a candidate
# IW1/IW2/IW3 share of GRD range width. Approximate: the product annotation with the
# exact swath merge is not exposed on Planetary Computer.
SWATH_SPAN = {"IW1": (0.0, 0.36), "IW2": (0.33, 0.68), "IW3": (0.65, 1.0)}
NOISE_REPORT_SPACING_S = 5.5
RECUR_MIN_DATES = 3       # stack dates an ESA strip must be flagged on to count as recurrent


# ---------- ESA RFI annotation ----------

def parse_rfi_xml(text: str) -> dict:
    root = ET.fromstring(text)
    hdr = root.find("adsHeader")
    noise = []
    for r in root.iter("rfiDetectionFromNoiseReport"):
        noise.append({
            "swath": r.findtext("swath"),
            "time": r.findtext("noiseSensingTime"),
            "detected": r.findtext("rfiDetected") == "true",
            "max_kl": float(r.findtext("maxKLDivergence")),
            "max_fisher_z": float(r.findtext("maxFisherZ")),
            "max_rfi_psd": float(r.findtext("maxRfiPsd")),
        })
    bursts = [{"swath": b.findtext("swath"), "time": b.findtext("azimuthTime"),
               "in_out_ratio": float(b.findtext("inBandOutBandPowerRatio"))}
              for b in root.iter("rfiBurstReport")]
    return {"start": hdr.findtext("startTime"), "stop": hdr.findtext("stopTime"),
            "polarisation": hdr.findtext("polarisation"),
            "mitigation": root.findtext("rfiMitigationApplied"), "noise": noise, "bursts": bursts}


def _t(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s)


def strip_polygon(geo, rep: dict, start: str, stop: str, height: int, width: int):
    """Approximate ground footprint of one noise-sensing report: swath x ~5.5 s along track."""
    t0, t1 = _t(start), _t(stop)
    dur = (t1 - t0).total_seconds()
    a = ((_t(rep["time"]) - t0).total_seconds()) / dur
    b = a + NOISE_REPORT_SPACING_S / dur
    a, b = max(0.0, a), min(1.0, b)
    if b <= a:
        return None
    c0, c1 = SWATH_SPAN[rep["swath"]]
    ring = [(a, c0), (a, c1), (b, c1), (b, c0), (a, c0)]
    lat_i, lon_i = geo
    return [[round(float(lon_i(r * (height - 1), c * (width - 1))[0][0]), 5),
             round(float(lat_i(r * (height - 1), c * (width - 1))[0][0]), 5)] for r, c in ring]


# ---------- geolocation, DEM ----------

def gcp_interpolators(gcps):
    rows = np.unique([g.row for g in gcps])
    cols = np.unique([g.col for g in gcps])
    ri = {v: i for i, v in enumerate(rows)}
    ci = {v: i for i, v in enumerate(cols)}
    lat = np.zeros((len(rows), len(cols)))
    lon = np.zeros_like(lat)
    for g in gcps:
        lat[ri[g.row], ci[g.col]] = g.y
        lon[ri[g.row], ci[g.col]] = g.x
    return (RectBivariateSpline(rows, cols, lat, kx=1, ky=1),
            RectBivariateSpline(rows, cols, lon, kx=1, ky=1))


def dem_slope_mask(lats, lons, cache: Path):
    """Copernicus GLO-30 from the public AWS bucket, read at DEM_RES through COG overviews."""
    tp = int(round(1.0 / DEM_RES))
    la0, la1 = int(np.floor(lats.min())), int(np.ceil(lats.max()))
    lo0, lo1 = int(np.floor(lons.min())), int(np.ceil(lons.max()))
    mosaic = np.full(((la1 - la0) * tp, (lo1 - lo0) * tp), np.nan, np.float32)
    cache.mkdir(parents=True, exist_ok=True)
    for la in range(la0, la1):
        for lo in range(lo0, lo1):
            name = f"Copernicus_DSM_COG_10_N{la:02d}_00_E{lo:03d}_00_DEM"
            npy = cache / f"{name}_{tp}.npy"
            if npy.exists():
                tile = np.load(npy)
            else:
                url = f"/vsicurl/https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/{name}/{name}.tif"
                try:
                    with rasterio.open(url) as src:
                        tile = src.read(1, out_shape=(tp, tp), resampling=Resampling.average).astype(np.float32)
                except rasterio.errors.RasterioIOError:
                    tile = np.zeros((tp, tp), np.float32)  # no tile = open sea
                np.save(npy, tile)
            r = (la1 - la - 1) * tp
            c = (lo - lo0) * tp
            mosaic[r:r + tp, c:c + tp] = tile
    ns = DEM_RES * 111320.0
    ew = ns * np.cos(np.radians((la0 + la1) / 2))
    dy, dx = np.gradient(mosaic, ns, ew)
    slope = np.degrees(np.arctan(np.hypot(dx, dy)))
    rr = np.clip(((la1 - lats) / DEM_RES).astype(int), 0, slope.shape[0] - 1)
    cc = np.clip(((lons - lo0) / DEM_RES).astype(int), 0, slope.shape[1] - 1)
    return np.nan_to_num(slope[rr, cc]) > SLOPE_THRESHOLD_DEG


# ---------- per scene ----------

def load_scene(item, cache: Path, use_dem: bool):
    """VH at 1/SUBSAMPLE => (relative dB, pixel lats, pixel lons, meta). Cached as npz."""
    npz = cache / f"{item.id}.npz"
    if npz.exists():
        z = np.load(npz, allow_pickle=False)
        return z["rel"], z["lat"], z["lon"], json.loads(str(z["meta"]))
    import planetary_computer as pc
    href = pc.sign(item.assets["vh"].href)
    with rasterio.open(href) as src:
        h, w = src.height, src.width
        sh, sw = h // SUBSAMPLE, w // SUBSAMPLE
        dn = src.read(1, out_shape=(sh, sw), resampling=Resampling.average).astype(np.float32)
        gcps = src.gcps[0]
    lat_i, lon_i = gcp_interpolators(gcps)
    rows = np.arange(sh) * SUBSAMPLE + SUBSAMPLE // 2
    cols = np.arange(sw) * SUBSAMPLE + SUBSAMPLE // 2
    lat = lat_i(rows, cols).astype(np.float32)
    lon = lon_i(rows, cols).astype(np.float32)
    with np.errstate(divide="ignore", invalid="ignore"):
        db = 10.0 * np.log10(np.where(dn > 0, dn, np.nan))  # zephr's intensity_to_db on GRD DN
    if use_dem:
        db[dem_slope_mask(lat, lon, cache / "dem")] = np.nan
    valid = np.isfinite(db)
    if valid.sum() < MIN_VALID_PX:
        return None
    rel = (db - np.median(db[valid])).astype(np.float32)
    meta = {"height": h, "width": w}
    np.savez_compressed(npz, rel=rel, lat=lat, lon=lon, meta=json.dumps(meta))
    return rel, lat, lon, meta


def grid_index(lat, lon, grid):
    la0, lo0, nr, nc = grid
    r = ((lat - la0) / GRID_RES).astype(np.int64)
    c = ((lon - lo0) / GRID_RES).astype(np.int64)
    ok = (r >= 0) & (r < nr) & (c >= 0) & (c < nc)
    return r, c, ok


def accumulate(rel, lat, lon, grid):
    nr, nc = grid[2], grid[3]
    r, c, ok = grid_index(lat, lon, grid)
    ok &= np.isfinite(rel)
    flat = r[ok] * nc + c[ok]
    v = rel[ok].astype(np.float64)
    n = nr * nc
    return (np.bincount(flat, v, n), np.bincount(flat, v * v, n), np.bincount(flat, None, n))


def zscores(rel, lat, lon, grid, s, ss, cnt):
    """Per-pixel z against the per-cell temporal baseline (zephr compute_scene_zscores)."""
    nc = grid[3]
    r, c, ok = grid_index(lat, lon, grid)
    ok &= np.isfinite(rel)
    flat = np.where(ok, r * nc + c, 0)
    n = cnt[flat]
    good = ok & (n >= MIN_OBS)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = s[flat] / n
        std = np.sqrt(np.maximum(ss[flat] / n - mean ** 2, 0.0))
    std = np.maximum(std, STD_FLOOR_DB)
    z = np.full(rel.shape, np.nan, np.float32)
    z[good] = ((rel[good] - mean[good]) / std[good]).astype(np.float32)
    return z


def hex_counts(z, lat, lon):
    ok = np.isfinite(z)
    la, lo, zz = lat[ok], lon[ok], z[ok]
    # Hex lookup per pixel is slow in Python; resolve once per 0.01 deg cell centre.
    key = np.round(la / GRID_RES).astype(np.int64) * 100000 + np.round(lo / GRID_RES).astype(np.int64)
    uniq, inv = np.unique(key, return_inverse=True)
    cells = [h3.latlng_to_cell((k // 100000) * GRID_RES, (k % 100000) * GRID_RES, HEX_RES) for k in uniq]
    hexes = np.array(cells)[inv]
    out = {}
    order = np.argsort(hexes, kind="stable")
    hs, zs = hexes[order], zz[order]
    bounds = np.flatnonzero(np.r_[True, hs[1:] != hs[:-1], True])
    for a, b in zip(bounds[:-1], bounds[1:]):
        seg = zs[a:b]
        out[hs[a]] = (int(seg.size), int((seg > Z_THRESHOLD).sum()), float(seg.max()))
    return out


def rank_hexes(per_date: dict, target: str):
    """Hexes where the target date has the highest z>3 share of the whole stack."""
    rows = []
    for hx, (n, k, zmax) in per_date[target].items():
        if n < MIN_HEX_PX:
            continue
        pct = 100.0 * k / n
        others = [100.0 * v[1] / v[0] for d, m in per_date.items() if d != target
                  for v in [m.get(hx)] if v and v[0] >= MIN_HEX_PX]
        if len(others) < MIN_OBS:
            continue
        rows.append({"h3": hx, "n_px": n, "pct_z3": round(pct, 2), "z_max": round(zmax, 1),
                     "pct_z3_other_median": round(float(np.median(others)), 2),
                     "pct_z3_other_max": round(max(others), 2), "n_other_dates": len(others),
                     "candidate": pct >= MIN_PCT_Z3 and pct > max(others)})
    return rows


# ---------- driver ----------

def find_stack(point, orbit, start, end):
    import pystac_client
    cat = pystac_client.Client.open(STAC_URL)
    items = cat.search(collections=["sentinel-1-grd"], intersects={"type": "Point", "coordinates": point},
                       datetime=f"{start}/{end}", query={"sat:relative_orbit": {"eq": orbit}}).items()
    by_date = {}
    for it in items:
        by_date.setdefault(it.properties["datetime"][:10], it)
    return dict(sorted(by_date.items()))


def esa_summary(item, cache: Path):
    import planetary_computer as pc
    import requests
    out = {}
    for pol in ("vh", "vv"):
        f = cache / f"{item.id}_rfi_{pol}.xml"
        if not f.exists():
            f.write_text(requests.get(pc.sign(item.assets[f"schema-product-{pol}"].href), timeout=60).text)
        out[pol] = parse_rfi_xml(f.read_text())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-01")
    ap.add_argument("--orbit", type=int, default=51)
    ap.add_argument("--point", type=float, nargs=2, default=[20.5, 54.7], metavar=("LON", "LAT"))
    ap.add_argument("--stack-from", default="2026-07-15")
    ap.add_argument("--stack-to", default="2026-10-31")
    ap.add_argument("--no-dem", action="store_true")
    ap.add_argument("--cache", type=Path, default=HERE / "cache" / "s1")
    ap.add_argument("--out", type=Path, default=HERE / "out")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    args.cache.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)

    stack = find_stack(args.point, args.orbit, args.stack_from, args.stack_to)
    if args.date not in stack:
        raise SystemExit(f"no orbit {args.orbit} scene on {args.date}; dates: {list(stack)}")
    log.info("stack: %d scenes, orbit %d: %s", len(stack), args.orbit, ", ".join(stack))

    esa, ok_dates = {}, []
    for d, it in stack.items():
        log.info("scene %s %s", d, it.id)
        esa[d] = esa_summary(it, args.cache)
        if load_scene(it, args.cache, not args.no_dem) is not None:
            ok_dates.append(d)

    from shapely.geometry import shape
    b = np.array([shape(stack[d].geometry).bounds for d in ok_dates])
    la0, lo0 = np.floor(b[:, 1].min() * 100) / 100, np.floor(b[:, 0].min() * 100) / 100
    grid = (la0, lo0, int((b[:, 3].max() - la0) / GRID_RES) + 2, int((b[:, 2].max() - lo0) / GRID_RES) + 2)

    def scene(d):
        return load_scene(stack[d], args.cache, not args.no_dem)

    acc = {d: accumulate(*scene(d)[:3], grid) for d in ok_dates}
    tot = [sum(a[i] for a in acc.values()) for i in range(3)]
    per_date, scene_rows = {}, []
    for d in ok_dates:
        rel, lat, lon, meta = scene(d)
        loo = [tot[i] - acc[d][i] for i in range(3)]  # leave-one-out baseline
        z = zscores(rel, lat, lon, grid, *loo)
        per_date[d] = hex_counts(z, lat, lon)
        nz = int(np.isfinite(z).sum())
        n3 = int((z > Z_THRESHOLD).sum())
        vh = esa[d]["vh"]
        scene_rows.append({"date": d, "id": stack[d].id, "pct_px_z3": round(100.0 * n3 / max(nz, 1), 3),
                           "esa_vh_rfi_detected": sum(r["detected"] for r in vh["noise"]),
                           "esa_vv_rfi_detected": sum(r["detected"] for r in esa[d]["vv"]["noise"]),
                           "esa_noise_reports": len(vh["noise"]),
                           "esa_vh_max_kl": round(max(r["max_kl"] for r in vh["noise"]), 2),
                           "esa_vh_in_out_ratio_mean": round(float(np.mean([b["in_out_ratio"] for b in vh["bursts"]])), 3),
                           "esa_mitigation": vh["mitigation"]})
        log.info("  %s z>3 %.3f%% of %d px, ESA VH rfiDetected %d/%d", d, 100.0 * n3 / max(nz, 1), nz,
                 scene_rows[-1]["esa_vh_rfi_detected"], len(vh["noise"]))

    target_item = stack[args.date]
    t_meta = scene(args.date)[3]
    hexes = rank_hexes(per_date, args.date)
    feats = []
    for r in hexes:
        ring = [[lo, la] for la, lo in h3.cell_to_boundary(r["h3"])]
        ring.append(ring[0])
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                      "properties": {"kind": "c-band-rfi" if r["candidate"] else "s1-scored",
                                     "method": "s1-temporal-z", "label": f"S1 VH z>3 {r['pct_z3']}%", **r}})
    # ESA flags, located by approximate swath x time strip
    import planetary_computer as pc
    with rasterio.open(pc.sign(target_item.assets["vh"].href)) as src:
        geo = gcp_interpolators(src.gcps[0])
    for pol in ("vh", "vv"):
        x = esa[args.date][pol]
        for rep in x["noise"]:
            if rep["detected"]:
                ring = strip_polygon(geo, rep, x["start"], x["stop"], t_meta["height"], t_meta["width"])
                if ring:
                    feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                                  "properties": {"kind": "c-band-rfi", "method": "esa-rfi-annotation",
                                                 "label": f"ESA rfiDetected {pol.upper()} {rep['swath']}",
                                                 "polarisation": pol, **rep}})
    # Recurrence of ESA flags over the stack. Frames of one relative orbit repeat to within ~1 s,
    # so each date's strip is placed with the target scene's geolocation.
    recur = {}
    for d in ok_dates:
        dates_seen = set()
        for pol in ("vh", "vv"):
            x = esa[d][pol]
            dur = (_t(x["stop"]) - _t(x["start"])).total_seconds()
            for rep in x["noise"]:
                if rep["detected"]:
                    k = (rep["swath"], round((_t(rep["time"]) - _t(x["start"])).total_seconds() / NOISE_REPORT_SPACING_S))
                    if k not in dates_seen:
                        dates_seen.add(k)
                        recur.setdefault(k, []).append(d)
    t_esa = esa[args.date]["vh"]
    for (sw, slot), ds in sorted(recur.items()):
        rep = {"swath": sw, "time": (_t(t_esa["start"]) + dt.timedelta(seconds=slot * NOISE_REPORT_SPACING_S)).isoformat()}
        ring = strip_polygon(geo, rep, t_esa["start"], t_esa["stop"], t_meta["height"], t_meta["width"])
        if ring:
            feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                          "properties": {"kind": "c-band-rfi" if len(ds) >= RECUR_MIN_DATES else "esa-rfi-sporadic",
                                         "method": "esa-rfi-recurrence", "swath": sw, "n_dates": len(ds),
                                         "n_stack": len(ok_dates), "dates": ds,
                                         "label": f"ESA rfiDetected on {len(ds)}/{len(ok_dates)} dates {sw}"}})
    fp = {"type": "Feature", "geometry": target_item.geometry,
          "properties": {"kind": "s1-footprint", "label": target_item.id, "method": "footprint"}}
    gj = {"type": "FeatureCollection", "features": [fp] + feats}
    (args.out / "s1_cells.geojson").write_text(json.dumps(gj))
    summary = {"target": target_item.id, "overpass_utc": target_item.properties["datetime"],
               "relative_orbit": args.orbit, "orbit_state": target_item.properties["sat:orbit_state"],
               "n_scenes": len(ok_dates), "grid": {"lat0": grid[0], "lon0": grid[1], "rows": grid[2], "cols": grid[3]},
               "hex_res": HEX_RES, "n_hex_scored": len(hexes),
               "n_hex_candidates": sum(r["candidate"] for r in hexes),
               "dem_mask": not args.no_dem, "scenes": scene_rows}
    (args.out / "s1_summary.json").write_text(json.dumps(summary, indent=1))
    log.info("hexes scored %d, candidates %d", summary["n_hex_scored"], summary["n_hex_candidates"])


if __name__ == "__main__":
    main()
