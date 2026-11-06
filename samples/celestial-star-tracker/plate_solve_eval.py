"""Lost-in-space plate solving with cedar-solve (tetra3 API) on real star images.

Part A: SkyView Mellinger cutouts with a known WCS => solve rate, attitude error vs the WCS
        (total, cross-boresight, roll), FOV error, runtime.
Part B: the 24 cedar-solve test images (real camera frames, no reference WCS) => solve rate
        and runtime only.

Needs the venv (numpy, scipy, pillow, astropy, cedar-solve). Run fetch_data.py first.
"""
import argparse
import glob
import json
import math
import os
import platform
import time
import warnings

import numpy as np
import tetra3
from tetra3 import tetra3 as t3core
from astropy.io import fits
from astropy.wcs import WCS
from PIL import Image

warnings.filterwarnings("ignore", module="astropy")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "results")
MAX_CENTROIDS = 30          # cedar-solve example: ~30 is "more than enough"
SOLVE_TIMEOUT_MS = 5000
MATCH_FOUND = 1             # tetra3.tetra3 status constant
# hand-picked: keep columns left of x in frames where a lit tree / roof edge fills the right side
OBSTRUCTION_MASKS = {"tree.jpg": 270, "roof.jpg": 250}
GRID = 5                    # GRID x GRID image points used to compare attitudes


def to_uint8(a):
    a = np.nan_to_num(np.asarray(a, dtype=np.float64))
    lo, hi = np.percentile(a, [1, 99.98])
    return np.clip((a - lo) / max(hi - lo, 1e-9) * 255, 0, 255).astype(np.uint8)


def radec_to_vec(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)], -1)


def kabsch(a, b):
    """Rotation R minimising |R a_i - b_i|."""
    u, _, vt = np.linalg.svd(b.T @ a)
    d = np.sign(np.linalg.det(u @ vt))
    return u @ np.diag([1, 1, d]) @ vt


def attitude_error(sol, wcs, h, w):
    """Compare solved and WCS sky directions on a grid of image points (tetra3 pixel
    convention: (y, x), 0.5 = centre of the top-left pixel; the FITS array is shown flipped
    so that row 0 is the top)."""
    ys, xs = np.meshgrid(np.linspace(0.1, 0.9, GRID) * h, np.linspace(0.1, 0.9, GRID) * w,
                         indexing="ij")
    pts = np.stack([ys.ravel(), xs.ravel()], -1)
    est = t3core.transform_to_celestial_coords(pts, w, h, sol["FOV"], sol["rotation_matrix"],
                                               sol["distortion"] or 0)
    est_v = radec_to_vec(*np.array(est).T)
    fx = pts[:, 1] - 0.5
    fy = (h - 1) - (pts[:, 0] - 0.5)
    ra, dec = wcs.all_pix2world(fx, fy, 0)
    ref_v = radec_to_vec(ra, dec)
    c = np.array([[h / 2, w / 2]])
    est_c = radec_to_vec(*np.array(t3core.transform_to_celestial_coords(
        c, w, h, sol["FOV"], sol["rotation_matrix"], sol["distortion"] or 0)).T)[0]
    ra_c, dec_c = wcs.all_pix2world([w / 2 - 0.5], [(h - 1) - (h / 2 - 0.5)], 0)
    ref_c = radec_to_vec(ra_c, dec_c)[0]
    r = kabsch(ref_v, est_v)
    total = math.degrees(math.acos(np.clip((np.trace(r) - 1) / 2, -1, 1))) * 3600
    # split the residual rotation into its component about the boresight (roll) and across it
    rotvec_axis = np.array([r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]])
    s = np.linalg.norm(rotvec_axis)
    ang = math.radians(total / 3600)
    rv = rotvec_axis / s * ang if s > 0 else np.zeros(3)
    roll = abs(np.dot(rv, ref_c))
    cross = np.linalg.norm(rv - np.dot(rv, ref_c) * ref_c)
    boresight = math.degrees(math.acos(np.clip(np.dot(est_c, ref_c), -1, 1))) * 3600
    grid_rms = math.degrees(np.sqrt(np.mean(np.arccos(np.clip(
        np.sum(est_v * ref_v, -1), -1, 1)) ** 2))) * 3600
    return {"total_arcsec": total, "cross_arcsec": math.degrees(cross) * 3600,
            "roll_arcsec": math.degrees(roll) * 3600, "boresight_arcsec": boresight,
            "grid_rms_arcsec": grid_rms}


def solve(t3, img, fov_estimate=None):
    t0 = time.perf_counter()
    cent = tetra3.get_centroids_from_image(img)
    t1 = time.perf_counter()
    sol = t3.solve_from_centroids(cent[:MAX_CENTROIDS], size=img.shape[:2],
                                  fov_estimate=fov_estimate, solve_timeout=SOLVE_TIMEOUT_MS,
                                  return_rotation_matrix=True)
    t2 = time.perf_counter()
    sol["n_centroids"] = len(cent)
    sol["t_extract_ms"] = (t1 - t0) * 1e3
    sol["t_solve_wall_ms"] = (t2 - t1) * 1e3
    return sol


def pct(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def run_skyview(t3, fov_hint):
    pts = json.load(open(os.path.join(DATA, "skyview", "pointings.json")))
    rows = []
    for p in pts:
        path = os.path.join(DATA, "skyview", p["name"] + ".fits")
        if not os.path.exists(path):
            continue
        with fits.open(path) as hd:
            data, hdr = hd[0].data, hd[0].header
        wcs = WCS(hdr)
        img = to_uint8(np.flipud(data))
        h, w = img.shape
        sol = solve(t3, img, fov_estimate=p["fov"] if fov_hint else None)
        row = {"name": p["name"], "fov": p["fov"], "ra": p["ra"], "dec": p["dec"],
               "rot": p["rot"], "status": int(sol["status"]), "n_centroids": sol["n_centroids"],
               "t_extract_ms": sol["t_extract_ms"], "t_solve_ms": sol["t_solve_wall_ms"]}
        if sol["status"] == MATCH_FOUND:
            row.update(attitude_error(sol, wcs, h, w))
            # SkyView "Size" is pixels x CDELT; a pinhole (TAN) camera spans 2 atan(w/2 tan CDELT)
            scale = math.radians(float(np.mean(wcs.proj_plane_pixel_scales()[0].value)))
            row["fov_ref"] = math.degrees(2 * math.atan(w / 2 * math.tan(scale)))
            row.update({"fov_est": sol["FOV"], "matches": sol["Matches"], "prob": sol["Prob"],
                        "rmse_arcsec": sol["RMSE"]})
        rows.append(row)
    return rows


def run_cedar(t3):
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA, "cedar", "*.jpg"))):
        with Image.open(path) as im:
            img = np.asarray(im.convert("L"), dtype=np.uint8)
        sol = solve(t3, img)
        row = {"name": os.path.basename(path), "shape": list(img.shape),
               "status": int(sol["status"]), "n_centroids": sol["n_centroids"],
               "t_extract_ms": sol["t_extract_ms"], "t_solve_ms": sol["t_solve_wall_ms"]}
        if sol["status"] == MATCH_FOUND:
            row.update({k: float(sol[k]) for k in ("RA", "Dec", "Roll", "FOV", "RMSE", "Prob")})
            row["matches"] = int(sol["Matches"])
        rows.append(row)
    return rows


def run_masked(t3):
    rows = []
    for name, x_max in OBSTRUCTION_MASKS.items():
        path = os.path.join(DATA, "cedar", name)
        if not os.path.exists(path):
            continue
        with Image.open(path) as im:
            img = np.asarray(im.convert("L"), dtype=np.uint8).copy()
        img[:, x_max:] = 0
        sol = solve(t3, img)
        rows.append({"name": name, "mask_x_max": x_max, "status": int(sol["status"]),
                     "n_centroids": sol["n_centroids"], "t_solve_ms": sol["t_solve_wall_ms"],
                     "RA": sol.get("RA"), "Dec": sol.get("Dec"), "matches": sol.get("Matches")})
        print(f"  {name} masked to x < {x_max}: status {sol['status']}, "
              f"{sol['n_centroids']} centroids, matches {sol.get('Matches')}, "
              f"{sol['t_solve_wall_ms']:.1f} ms")
    return rows


def summarize(rows, label):
    ok = [r for r in rows if r["status"] == MATCH_FOUND]
    print(f"\n{label}: solved {len(ok)} of {len(rows)}")
    if not rows:
        return {}
    te = [r["t_extract_ms"] for r in rows]
    ts = [r["t_solve_ms"] for r in rows]
    print(f"  extract ms median {pct(te, 50):.0f} p95 {pct(te, 95):.0f}; "
          f"solve ms median {pct(ts, 50):.1f} p95 {pct(ts, 95):.1f} max {max(ts):.1f}")
    s = {"n": len(rows), "solved": len(ok), "extract_ms_median": pct(te, 50),
         "solve_ms_median": pct(ts, 50), "solve_ms_p95": pct(ts, 95), "solve_ms_max": max(ts)}
    if ok and "total_arcsec" in ok[0]:
        for k in ("total_arcsec", "cross_arcsec", "roll_arcsec", "grid_rms_arcsec"):
            v = [r[k] for r in ok]
            print(f"  {k:16s} median {pct(v, 50):7.1f}  p95 {pct(v, 95):7.1f}  max {max(v):7.1f}")
            s[k + "_median"], s[k + "_p95"], s[k + "_max"] = pct(v, 50), pct(v, 95), max(v)
        fe = [abs(r["fov_est"] - r["fov_ref"]) / r["fov_ref"] * 100 for r in ok]
        print(f"  FOV error % (vs pinhole FOV of the WCS) median {pct(fe, 50):7.3f}  max {max(fe):7.3f}")
        s["fov_err_pct_max"] = max(fe)
    fails = [r["name"] for r in rows if r["status"] != MATCH_FOUND]
    if fails:
        print("  not solved:", ", ".join(f"{r['name']}(status {r['status']}, "
                                         f"{r['n_centroids']} centroids)"
                                         for r in rows if r["status"] != MATCH_FOUND))
    s["not_solved"] = fails
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fov-hint", action="store_true", help="pass the true FOV as fov_estimate")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    t3 = tetra3.Tetra3(load_database="default_database")
    print(f"python {platform.python_version()} numpy {np.__version__} on {platform.machine()}"
          f" ({platform.processor() or 'cpu'}), fov_hint={a.fov_hint}")
    sv = run_skyview(t3, a.fov_hint)
    cd = run_cedar(t3)
    summary = {"skyview_all": summarize(sv, "SkyView Mellinger cutouts (reference WCS)")}
    for fov in sorted({r["fov"] for r in sv}):
        summary[f"skyview_fov{fov}"] = summarize([r for r in sv if r["fov"] == fov],
                                                 f"  FOV {fov} deg")
    summary["cedar_images"] = summarize(cd, "cedar-solve test images (no reference)")
    print("\nObstructed frames with the obstruction masked out")
    masked = run_masked(t3)
    tag = "_fovhint" if a.fov_hint else ""
    with open(os.path.join(OUT, f"plate_solve{tag}.json"), "w") as f:
        json.dump({"summary": summary, "skyview": sv, "cedar": cd, "masked": masked}, f,
                  indent=1, default=float)
    print(f"\nwrote results/plate_solve{tag}.json")


if __name__ == "__main__":
    main()
