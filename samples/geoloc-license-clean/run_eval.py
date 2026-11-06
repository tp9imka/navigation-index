"""Evaluate geoloc.Localizer on synthetic frames (known truth) and real eBee frames (EXIF GPS truth)."""
import argparse
import json
import math
import pathlib
import platform
import statistics
import subprocess
import time

import cv2
import numpy as np
import torch
from PIL import ExifTags, Image

from geoloc import Localizer, OrthoMap, haversine_m
from synth_frames import make_frame

HERE = pathlib.Path(__file__).parent
PRIOR_OFFSET_M = 100.0
SEARCH_RADIUS_M = 150.0
HEADING_NOISE_DEG = 5.0
SCALE_NOISE = 0.05
# Sony DSC-WX220: 1/2.3" sensor, 6.17 mm wide (spec sheet value, not in EXIF)
SENSOR_WIDTH_MM = 6.17
AGL_CANDIDATES_M = (80, 100, 120)
AGL_STEP_M = 10
COLD_HEADING_STEP_DEG = 15
WARM_HEADING_STEP_DEG = 10


def cpu_name():
    try:
        return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    except Exception:
        return platform.processor() or "unknown"


def offset_lonlat(ortho, lonlat, rng, dist_m):
    x, y = ortho.lonlat_to_world(*lonlat)
    a = rng.uniform(0, 2 * math.pi)
    return ortho.world_to_lonlat(x + dist_m * math.cos(a), y + dist_m * math.sin(a))


def run_synthetic(loc, ortho, src, n, rng, label):
    rows = []
    for i in range(n):
        frame, gt = make_frame(src.rgb, src.gsd, rng)
        tx, ty = src.px_to_world(gt["truth_px"][0] + 0.5, gt["truth_px"][1] + 0.5)
        truth = src.world_to_lonlat(tx, ty)
        prior = offset_lonlat(ortho, truth, rng, PRIOR_OFFSET_M)
        heading = gt["yaw_deg"] + rng.normal(0, HEADING_NOISE_DEG)
        gsd = gt["frame_gsd"] * (1 + rng.normal(0, SCALE_NOISE))
        r = loc.localize(frame, gsd, heading, ortho, prior, SEARCH_RADIUS_M)
        r.update(case=f"{label}-{i:02d}", yaw=round(gt["yaw_deg"], 1), scale=round(gt["scale"], 2))
        r["err_m"] = round(haversine_m(truth[1], truth[0], r["fix"][1], r["fix"][0]), 2) if r["fix"] else None
        rows.append(r)
        if i == 0:
            cv2.imwrite(str(HERE / "thumbs" / f"synth_{label}_frame.jpg"),
                        cv2.cvtColor(cv2.resize(frame, (320, 240)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 80])
    return rows


def exif_gps(path):
    ex = Image.open(path).getexif()
    g = ex.get_ifd(0x8825)
    dms = lambda v: float(v[0]) + float(v[1]) / 60 + float(v[2]) / 3600
    lat = dms(g[2]) * (1 if g[1] == "N" else -1)
    lon = dms(g[4]) * (1 if g[3] == "E" else -1)
    focal = float(ex.get_ifd(0x8769)[0x920A])
    return lat, lon, float(g[6]), focal


def bearing_deg(lat1, lon1, lat2, lon2):
    p1, p2, dl = map(math.radians, (lat1, lat2, lon2 - lon1))
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360


def run_real(loc, ortho, frames, rng, work_width_px):
    """Cold start: full heading sweep. Once a frame fixes, reuse its camera-vs-track offset and AGL."""
    gps = [exif_gps(p) for p in frames]
    rows = []
    offset, agl_prev = None, None
    for i, p in enumerate(frames):
        lat, lon, alt, focal = gps[i]
        j = i + 1 if i + 1 < len(frames) else i - 1
        trk = bearing_deg(lat, lon, gps[j][0], gps[j][1]) if j > i else bearing_deg(gps[j][0], gps[j][1], lat, lon)
        img = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)
        native_w = img.shape[1]
        ds = work_width_px / native_w
        img = cv2.resize(img, None, fx=ds, fy=ds, interpolation=cv2.INTER_AREA)
        prior = offset_lonlat(ortho, (lon, lat), rng, PRIOR_OFFSET_M)
        if offset is None:
            headings = [float(h) for h in range(0, 360, COLD_HEADING_STEP_DEG)]
            agls = AGL_CANDIDATES_M
        else:
            headings = [trk + offset + d for d in (-WARM_HEADING_STEP_DEG, 0, WARM_HEADING_STEP_DEG)]
            agls = (agl_prev - AGL_STEP_M, agl_prev, agl_prev + AGL_STEP_M)
        t0 = time.perf_counter()
        best = None
        for agl in agls:
            gsd = agl * SENSOR_WIDTH_MM / (focal * native_w) / ds
            for hdg in headings:
                r = loc.localize(img, gsd, hdg % 360, ortho, prior, SEARCH_RADIUS_M)
                if best is None or r["inliers"] > best["inliers"]:
                    best = r | {"agl_assumed": agl, "heading_tried": round(hdg % 360, 1)}
        best.update(case=p.name, t_search_s=round(time.perf_counter() - t0, 2), tries=len(agls) * len(headings),
                    mode="cold" if offset is None else "warm", exif_alt_msl=alt, track_deg=round(trk, 1))
        best["err_m"] = round(haversine_m(lat, lon, best["fix"][1], best["fix"][0]), 2) if best["fix"] else None
        if best["fix"]:
            offset, agl_prev = best["heading_tried"] - trk, best["agl_assumed"]
        rows.append(best)
    return rows


def summarize(rows):
    ok = [r for r in rows if r["fix"]]
    errs = sorted(r["err_m"] for r in ok)
    t = [r["t_total_s"] for r in rows]
    return {"n": len(rows), "fixes": len(ok),
            "within_5m": sum(e <= 5 for e in errs), "within_20m": sum(e <= 20 for e in errs),
            "median_err_m": round(statistics.median(errs), 2) if errs else None,
            "max_err_m": round(max(errs), 2) if errs else None,
            "median_t_s": round(statistics.median(t), 3),
            "median_search_s": round(statistics.median(r["t_search_s"] for r in rows), 2) if "t_search_s" in rows[0] else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", nargs="+", default=["aliked", "disk", "sift"])
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--real-width", type=int, default=1024)
    ap.add_argument("--skip-real", action="store_true")
    ap.add_argument("--skip-synth", action="store_true")
    ap.add_argument("--prior-offset-m", type=float, default=PRIOR_OFFSET_M)
    ap.add_argument("--search-radius-m", type=float, default=SEARCH_RADIUS_M)
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()
    globals().update(PRIOR_OFFSET_M=a.prior_offset_m, SEARCH_RADIUS_M=a.search_radius_m)
    (HERE / "thumbs").mkdir(exist_ok=True)
    data = HERE / "data"
    ortho = OrthoMap.open(data / "naip_aukerman.tif")
    sources = {"same": ortho}
    older = sorted(data.glob("naip_aukerman_*.tif"))
    if older:
        sources["season"] = OrthoMap.open(older[0])
    frames = sorted((data / "uav").glob("*.JPG"))
    env = {"cpu": cpu_name(), "torch_threads": torch.get_num_threads(), "torch": torch.__version__,
           "opencv": cv2.__version__, "map_gsd_m": ortho.gsd, "map_px": list(ortho.rgb.shape[:2][::-1]),
           "season_source": older[0].name if older else None}
    env |= {"prior_offset_m": PRIOR_OFFSET_M, "search_radius_m": SEARCH_RADIUS_M}
    print(json.dumps(env))
    report = {"env": env, "results": {}}
    for feat in a.features:
        loc = Localizer(feat)
        loc.localize(sources["same"].rgb[:480, :640], ortho.gsd, 0, ortho,
                     ortho.world_to_lonlat(*ortho.px_to_world(2000, 2000)), 50)  # warm-up, not timed
        for label, src in ([] if a.skip_synth else sources.items()):
            rng = np.random.default_rng(a.seed)
            rows = run_synthetic(loc, ortho, src, a.n, rng, label)
            report["results"][f"{feat}/{label}"] = {"summary": summarize(rows), "rows": rows}
            print(feat, label, json.dumps(summarize(rows)))
        for label, ref in ([] if a.skip_real else sources.items()):
            rng = np.random.default_rng(a.seed)
            rows = run_real(loc, ref, frames, rng, a.real_width)
            key = f"{feat}/real-vs-{'2023' if label == 'same' else older[0].stem[-4:]}"
            report["results"][key] = {"summary": summarize(rows), "rows": rows}
            print(key, json.dumps(summarize(rows)))
            for r in rows:
                print("  ", r["case"], r["mode"], "tries", r["tries"], "inliers", r["inliers"], "err_m", r["err_m"],
                      "agl", r["agl_assumed"], "hdg", r["heading_tried"], "search_s", r["t_search_s"])
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / a.out).write_text(json.dumps(report, indent=1, default=float))


if __name__ == "__main__":
    main()
