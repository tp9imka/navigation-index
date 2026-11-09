"""Range x view-angle sweep: render a tag36h11 tag at known poses, detect it with pupil-apriltags,
measure detection rate and pose error per cell. All images are synthetic.

.venv/bin/python sweep.py                      # default: blur 0.8 px, noise 3 DN, 20 trials per cell
.venv/bin/python sweep.py --blur 1.5 --noise 6 --name sweep_harsh
"""
import argparse
import json
import math
import os
import platform
import time

import cv2
import numpy as np
import pupil_apriltags

import render as rd

HERE = os.path.dirname(os.path.abspath(__file__))
RANGES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
ANGLES = [0, 10, 20, 30, 40, 50, 60, 70]
GROSS_YAW_DEG = 10.0     # |yaw error| above this counts as a gross (flipped / ambiguous) pose
FAIL_RATE = 0.5          # a cell "fails" below this detection rate
GOOD_RATE = 0.9


def make_detector(decimate):
    return pupil_apriltags.Detector(families="tag36h11", nthreads=1, quad_decimate=decimate,
                                    quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25)


def trial_pose(rng, range_m, angle_deg, tag_size):
    """Camera at range_m from the tag centre, angle_deg off the tag normal (about the vertical
    axis), random in-plane tag roll and a random pan/tilt so the tag is not always centred."""
    a = math.radians(angle_deg)
    R, t = rd.look_at_pose(range_m * np.array([math.sin(a), 0.0, -math.cos(a)]))
    R = R @ rd.rot_z(rng.uniform(0, 2 * math.pi))          # tag printed at any roll
    tag_ang = math.atan(0.75 * tag_size * math.sqrt(2) / range_m)   # half-diagonal incl. margin
    pan_max = max(0.0, math.radians(rd.HFOV_DEG / 2) - tag_ang - math.radians(3)) * 0.8
    tilt_max = max(0.0, math.radians(rd.VFOV_DEG / 2) - tag_ang - math.radians(3)) * 0.8
    Rd = rd.rot_x(rng.uniform(-tilt_max, tilt_max)) @ rd.rot_y(rng.uniform(-pan_max, pan_max))
    return Rd @ R, Rd @ t


def pct(xs, q):
    return None if not xs else float(np.percentile(xs, q))


def run_cell(renderer, det, rng, range_m, angle_deg, trials, blur, noise):
    pos_err, yaw_err, n_det, n_wrong, det_ms = [], [], 0, 0, []
    for _ in range(trials):
        R, t = trial_pose(rng, range_m, angle_deg, renderer.tag_size)
        img = renderer.render(R, t, rng, blur_px=blur, noise_dn=noise)
        t0 = time.perf_counter()
        dets = det.detect(img, estimate_tag_pose=True, camera_params=(rd.FX, rd.FY, rd.CX, rd.CY),
                          tag_size=renderer.tag_size)
        det_ms.append(1000 * (time.perf_counter() - t0))
        n_wrong += sum(1 for d in dets if d.tag_id != renderer.tag_id)
        hit = [d for d in dets if d.tag_id == renderer.tag_id]
        if not hit:
            continue
        n_det += 1
        d = hit[0]
        pos_err.append(float(np.linalg.norm(d.pose_t.ravel() - t)))
        yaw_err.append(abs(math.degrees(rd.wrap(rd.heading_of(d.pose_R) - rd.heading_of(R)))))
    r3 = lambda x: None if x is None else round(x, 4)
    return {
        "range_m": range_m, "angle_deg": angle_deg, "trials": trials,
        "detected": n_det, "rate": round(n_det / trials, 3), "wrong_id": n_wrong,
        "pos_err_med_m": r3(pct(pos_err, 50)), "pos_err_p95_m": r3(pct(pos_err, 95)),
        "pos_err_med_pct_range": r3(None if not pos_err else 100 * pct(pos_err, 50) / range_m),
        "yaw_err_med_deg": r3(pct(yaw_err, 50)), "yaw_err_p95_deg": r3(pct(yaw_err, 95)),
        "gross_yaw": sum(1 for e in yaw_err if e > GROSS_YAW_DEG),
        "detect_ms_med": round(float(np.median(det_ms)), 2),
    }


def summarise(cells):
    out = []
    for a in ANGLES:
        col = sorted((c for c in cells if c["angle_deg"] == a), key=lambda c: c["range_m"])
        good = [c["range_m"] for c in col if c["rate"] >= GOOD_RATE]
        # contiguous band of cells with rate >= GOOD_RATE that starts at the first good cell
        lo = hi = None
        for c in col:
            if c["rate"] >= GOOD_RATE:
                lo = c["range_m"] if lo is None else lo
                hi = c["range_m"]
            elif lo is not None:
                break
        far_fail = next((c["range_m"] for c in col if c["rate"] < FAIL_RATE and (hi is None or c["range_m"] > hi)), None)
        near_fail = max((c["range_m"] for c in col if c["rate"] < FAIL_RATE and lo is not None and c["range_m"] < lo), default=None)
        out.append({"angle_deg": a, "band_rate_ge_0.9_m": [lo, hi], "far_fail_rate_lt_0.5_m": far_fail,
                    "near_fail_rate_lt_0.5_m": near_fail, "cells_ge_0.9": len(good)})
    return out


def fmt(x, nd=3):
    return "-" if x is None else f"{x:.{nd}f}"


def heatmap(cells, path, title):
    """Three panels (detection rate, median position error, p95 yaw error), drawn with OpenCV."""
    cw, ch, left, top = 64, 34, 70, 70
    panels = [("detection rate", "rate", lambda v: v, "{:.2f}"),
              ("median pos err [cm]", "pos_err_med_m", lambda v: 1 - min(v / 0.10, 1), "{:.1f}"),
              ("p95 yaw err [deg]", "yaw_err_p95_deg", lambda v: 1 - min(v / 20.0, 1), "{:.1f}")]
    pw = left + cw * len(ANGLES) + 20
    img = np.full((top + ch * len(RANGES) + 50, pw * len(panels), 3), 255, np.uint8)
    cv2.putText(img, title, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
    lut = {(c["range_m"], c["angle_deg"]): c for c in cells}
    for p, (name, key, good, f) in enumerate(panels):
        x0 = p * pw
        cv2.putText(img, name, (x0 + left, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        for i, r in enumerate(RANGES):
            y = top + i * ch
            cv2.putText(img, f"{r:g} m", (x0 + 8, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
            for j, a in enumerate(ANGLES):
                x = x0 + left + j * cw
                v = lut[(r, a)][key]
                if v is None:
                    color, txt = (200, 200, 200), "-"
                else:
                    g = good(v)
                    color = (int(80 + 120 * g), int(60 + 180 * g), int(230 - 150 * g))  # BGR red => green
                    txt = f.format(100 * v if key == "pos_err_med_m" else v)
                cv2.rectangle(img, (x, y), (x + cw - 2, y + ch - 2), color, -1)
                cv2.putText(img, txt, (x + 6, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        yb = top + len(RANGES) * ch + 20
        for j, a in enumerate(ANGLES):
            cv2.putText(img, f"{a}", (x0 + left + j * cw + 20, yb), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img, "view angle [deg]", (x0 + left, yb + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imwrite(path, img)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--blur", type=float, default=0.8, help="Gaussian blur sigma, output px")
    ap.add_argument("--noise", type=float, default=3.0, help="Gaussian noise sigma, 8-bit DN")
    ap.add_argument("--tag-size", type=float, default=rd.TAG_SIZE, help="black border edge, m")
    ap.add_argument("--decimate", type=float, default=1.0, help="pupil-apriltags quad_decimate")
    ap.add_argument("--name", default="sweep")
    ap.add_argument("--ranges", type=float, nargs="*", default=None)
    ap.add_argument("--angles", type=float, nargs="*", default=None)
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    global RANGES, ANGLES
    if a.ranges:
        RANGES = a.ranges
    if a.angles:
        ANGLES = a.angles

    t_start = time.time()
    rng = np.random.default_rng(a.seed)
    renderer = rd.Renderer(tag_size=a.tag_size)
    det = make_detector(a.decimate)
    cells = [run_cell(renderer, det, rng, r, ang, a.trials, a.blur, a.noise) for r in RANGES for ang in ANGLES]
    summary = summarise(cells)
    wall_s = round(time.time() - t_start, 1)
    import pupil_apriltags as _pa  # noqa: F401
    from importlib.metadata import version
    meta = {
        "input": "synthetic (rendered images, no real camera)",
        "camera": {"width": rd.W, "height": rd.H, "fx": rd.FX, "fy": rd.FY, "cx": rd.CX, "cy": rd.CY,
                   "hfov_deg": round(rd.HFOV_DEG, 1), "vfov_deg": round(rd.VFOV_DEG, 1), "distortion": "none"},
        "tag": {"family": "tag36h11", "id": rd.TAG_ID, "size_m": a.tag_size, "size_means": "black border edge"},
        "render": {"supersample": renderer.ss, "blur_sigma_px": a.blur, "noise_sigma_dn": a.noise,
                   "ink_dn": rd.BLACK, "paper_dn": rd.WHITE},
        "detector": {"package": "pupil-apriltags " + version("pupil-apriltags"), "quad_decimate": a.decimate,
                     "nthreads": 1, "refine_edges": 1, "decode_sharpening": 0.25},
        "trials_per_cell": a.trials, "seed": a.seed, "gross_yaw_deg": GROSS_YAW_DEG,
        "fail_rate_below": FAIL_RATE, "good_rate_at_least": GOOD_RATE,
        "python": platform.python_version(), "numpy": np.__version__, "opencv": cv2.__version__,
        "machine": platform.machine(), "wall_s": wall_s,
        "command": "python sweep.py " + " ".join(argv if argv is not None else __import__("sys").argv[1:]),
    }
    if a.no_write:
        return meta, cells, summary
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    base = os.path.join(HERE, "results", a.name)
    with open(base + ".json", "w") as f:
        json.dump({"meta": meta, "summary_by_angle": summary, "cells": cells}, f, indent=1)

    L = [f"# {a.name}: tag36h11 detection and pose error vs range and view angle (synthetic)", "",
         f"Command: `{meta['command'].strip()}`, wall {wall_s} s. Input: synthetic rendered images.",
         f"Camera {rd.W}x{rd.H}, fx=fy={rd.FX:g}, cx={rd.CX}, cy={rd.CY}, no distortion "
         f"(HFOV {rd.HFOV_DEG:.1f} deg). Tag {a.tag_size} m black edge. Blur sigma {a.blur} px, "
         f"noise sigma {a.noise} DN, {a.trials} trials per cell, seed {a.seed}, quad_decimate {a.decimate}.", "",
         "## Where detection holds, per view angle", "",
         "| view angle deg | ranges with rate >= 0.9 m | far fail: first range beyond with rate < 0.5 m | "
         "near fail: closest-side range with rate < 0.5 m |",
         "|---|---|---|---|"]
    for s in summary:
        lo, hi = s["band_rate_ge_0.9_m"]
        band = "none" if lo is None else f"{lo:g}-{hi:g}"
        L.append(f"| {s['angle_deg']:g} | {band} | {fmt(s['far_fail_rate_lt_0.5_m'], 1)} | "
                 f"{fmt(s['near_fail_rate_lt_0.5_m'], 1)} |")
    L += ["", "## Per cell", "",
          "| range m | angle deg | rate | pos err med m | pos err p95 m | pos err med % range | "
          "yaw err med deg | yaw err p95 deg | gross yaw (>10 deg) | wrong id |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        L.append(f"| {c['range_m']:g} | {c['angle_deg']:g} | {c['rate']:.2f} | {fmt(c['pos_err_med_m'])} | "
                 f"{fmt(c['pos_err_p95_m'])} | {fmt(c['pos_err_med_pct_range'], 2)} | {fmt(c['yaw_err_med_deg'], 2)} | "
                 f"{fmt(c['yaw_err_p95_deg'], 2)} | {c['gross_yaw']}/{c['detected']} | {c['wrong_id']} |")
    with open(base + ".md", "w") as f:
        f.write("\n".join(L) + "\n")
    heatmap(cells, base + "_heatmap.png",
            f"{a.name}: tag {a.tag_size} m, blur {a.blur} px, noise {a.noise} DN, {a.trials}/cell (synthetic)")
    print("\n".join(L[:len(summary) + 9]))
    print(f"wrote {base}.json .md _heatmap.png in {wall_s} s")
    return meta, cells, summary


if __name__ == "__main__":
    main()
