"""Tag-relative final approach: a kinematic, camera-equipped point mass starts 3 m off the tag
axis and servos on the detected tag pose to a goal 1 m in front of the tag. Every control step
renders a synthetic camera image from the true pose and runs pupil-apriltags on it; the
controller only sees the detection. All inputs are synthetic.

.venv/bin/python final_approach.py                 # 50 seeds, writes results/final_approach.*
.venv/bin/python final_approach.py --seeds 3 --no-write
"""
import argparse
import json
import math
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np

import render as rd
from sweep import make_detector

HERE = os.path.dirname(os.path.abspath(__file__))

# world frame = tag frame: x right, y down, z into the wall; the tag faces -z.
GOAL = np.array([0.0, 0.0, -1.0])   # 1 m in front of the tag centre, camera facing the tag
P = dict(
    lateral_m=3.0,          # start offset along tag x (off-axis), sign random
    standoff_m=4.0,         # start distance along the normal, +- standoff_jitter_m
    standoff_jitter_m=0.5,
    height_jitter_m=0.2,    # start offset along tag y
    yaw0_sigma_deg=5.0,     # initial pointing error vs the bearing to the tag
    dt=0.02,                # 50 Hz dynamics
    cam_hz=10.0,            # camera and control rate
    latency_frames=1,       # command uses the detection from the previous frame
    tau_s=0.3,              # first-order velocity lag
    vmax=0.8, k_pos=0.8,    # m/s cap, 1/s proportional gain on goal offset
    k_yaw=1.5, yaw_rate_max_deg=60.0,
    creep_mps=0.3,          # no detection => creep forward along the camera axis
    v_noise_mps=0.05,       # per-axis velocity disturbance, white per 50 Hz step
    yaw_noise_dps=2.0,
    blur_px=0.8, noise_dn=3.0,
    arrive_tol_m=0.05,      # estimate-based stop rule ...
    arrive_frames=10,       # ... held this many consecutive frames
    timeout_s=60.0,
    pass_m=0.10,            # task threshold on the TRUE final error
)


def cam_pose(p, psi):
    """Level camera at p (tag frame) with yaw psi about the tag y axis; psi = 0 faces the tag."""
    R_tc = rd.rot_y(psi)
    R = R_tc.T
    return R, -R @ p, R_tc


def run_seed(seed, prm=P, tag_size=rd.TAG_SIZE):
    rng = np.random.default_rng(1000 + seed)
    renderer = rd.Renderer(tag_size=tag_size)
    det = make_detector(1.0)
    side = rng.choice([-1.0, 1.0])
    p = np.array([side * prm["lateral_m"], rng.uniform(-1, 1) * prm["height_jitter_m"],
                  -(prm["standoff_m"] + rng.uniform(-1, 1) * prm["standoff_jitter_m"])])
    psi = math.atan2(-p[0], -p[2]) + math.radians(rng.normal(0, prm["yaw0_sigma_deg"]))
    v = np.zeros(3)
    steps_per_frame = int(round(1 / (prm["cam_hz"] * prm["dt"])))
    queue = []                      # delayed detections
    cmd_v_c, cmd_yaw_rate = np.zeros(3), 0.0
    n_frames = n_seen = n_gross = 0
    first_seen_s, in_tol, arrived_s = None, 0, None
    track = [p.copy()]
    t = 0.0
    while t < prm["timeout_s"]:
        # --- camera frame: render from truth, detect, queue for latency ---
        R, tt, R_tc = cam_pose(p, psi)
        img = renderer.render(R, tt, rng, blur_px=prm["blur_px"], noise_dn=prm["noise_dn"])
        dets = [d for d in det.detect(img, True, (rd.FX, rd.FY, rd.CX, rd.CY), tag_size)
                if d.tag_id == renderer.tag_id]
        n_frames += 1
        meas = None
        if dets:
            d = dets[0]
            meas = (d.pose_R, d.pose_t.ravel())
            n_seen += 1
            first_seen_s = t if first_seen_s is None else first_seen_s
            if abs(math.degrees(rd.wrap(rd.heading_of(d.pose_R) - rd.heading_of(R)))) > 10:
                n_gross += 1
        queue.append(meas)
        meas = queue.pop(0) if len(queue) > prm["latency_frames"] else None

        # --- controller: uses only the (delayed) detection ---
        if meas is not None:
            Rm, tm = meas
            g_c = Rm @ GOAL + tm                        # goal point in the camera frame
            bearing = math.atan2(tm[0], tm[2])          # keep the tag centred
            cmd_v_c = prm["k_pos"] * g_c
            sp = np.linalg.norm(cmd_v_c)
            if sp > prm["vmax"]:
                cmd_v_c *= prm["vmax"] / sp
            ymax = math.radians(prm["yaw_rate_max_deg"])
            cmd_yaw_rate = float(np.clip(prm["k_yaw"] * bearing, -ymax, ymax))
            in_tol = in_tol + 1 if np.linalg.norm(g_c) < prm["arrive_tol_m"] else 0
            if in_tol >= prm["arrive_frames"]:
                arrived_s = t
                break
        elif first_seen_s is None:      # not acquired yet: creep along the camera axis
            cmd_v_c, cmd_yaw_rate, in_tol = np.array([0.0, 0.0, prm["creep_mps"]]), 0.0, 0
        else:                           # lost after acquisition (or latency gap): hover
            cmd_v_c, cmd_yaw_rate, in_tol = np.zeros(3), 0.0, 0

        # --- kinematics with lag and disturbance, 50 Hz, until the next frame ---
        for _ in range(steps_per_frame):
            R_tc = rd.rot_y(psi)
            v_cmd_w = R_tc @ cmd_v_c
            v += (v_cmd_w - v) * (prm["dt"] / prm["tau_s"])
            p = p + (v + rng.normal(0, prm["v_noise_mps"], 3)) * prm["dt"]
            psi += (cmd_yaw_rate + math.radians(rng.normal(0, prm["yaw_noise_dps"]))) * prm["dt"]
            t += prm["dt"]
        track.append(p.copy())

    err = float(np.linalg.norm(p - GOAL))
    R, _, _ = cam_pose(p, psi)
    return {
        "seed": seed, "start": [round(x, 3) for x in track[0]],
        "start_range_m": round(float(np.linalg.norm(track[0])), 3),
        "start_view_angle_deg": round(math.degrees(math.atan2(abs(track[0][0]), -track[0][2])), 1),
        "arrived": arrived_s is not None, "time_s": None if arrived_s is None else round(arrived_s, 2),
        "first_seen_s": None if first_seen_s is None else round(first_seen_s, 2),
        "final_err_m": round(err, 4),
        "final_lateral_err_m": round(float(np.hypot(p[0] - GOAL[0], p[1] - GOAL[1])), 4),
        "final_yaw_err_deg": round(abs(math.degrees(rd.wrap(psi))), 2),
        "frames": n_frames, "frames_detected": n_seen, "frames_gross_heading": n_gross,
        "track_xz": [[round(q[0], 3), round(q[2], 3)] for q in track],
    }


def plot(rows, path):
    """Top view (tag x right, distance from wall up), all tracks; drawn with OpenCV."""
    S, ox, oy = 90, 450, 560          # px per m, image position of the tag centre
    img = np.full((620, 900, 3), 255, np.uint8)
    to = lambda x, z: (int(ox + S * x), int(oy + S * z))      # z < 0 is in front of the wall
    cv2.line(img, to(-4.8, 0), to(4.8, 0), (0, 0, 0), 2)
    cv2.line(img, to(-0.08, 0), to(0.08, 0), (0, 0, 255), 6)
    cv2.circle(img, to(*GOAL[[0, 2]]), int(S * 0.1), (0, 160, 0), 1)
    for r in rows:
        pts = np.array([to(x, z) for x, z in r["track_xz"]], np.int32)
        cv2.polylines(img, [pts], False, (200, 120, 0) if r["final_err_m"] <= P["pass_m"] else (0, 0, 255), 1)
        cv2.circle(img, tuple(pts[0]), 3, (0, 0, 0), -1)
    for x in range(-4, 5):
        cv2.putText(img, f"{x}", to(x - 0.05, 0.35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    for z in range(1, 6):
        cv2.putText(img, f"{z} m", (8, to(0, -z)[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.line(img, (50, to(0, -z)[1]), (56, to(0, -z)[1]), (0, 0, 0), 1)
    cv2.putText(img, "top view, synthetic: tag (red) on wall, goal 1 m out (green 0.1 m circle), "
                f"{len(rows)} seeds", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imwrite(path, img)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--blur", type=float, default=P["blur_px"], help="image blur sigma, px")
    ap.add_argument("--noise", type=float, default=P["noise_dn"], help="image noise sigma, DN")
    ap.add_argument("--name", default="final_approach")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    P["blur_px"], P["noise_dn"] = a.blur, a.noise
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        rows = list(ex.map(run_seed, range(a.seeds), [dict(P)] * a.seeds))
    wall = round(time.time() - t0, 1)
    errs = [r["final_err_m"] for r in rows]
    arrived = [r for r in rows if r["arrived"]]
    q = lambda xs, k: None if not xs else round(float(np.percentile(xs, k)), 4)
    summ = {
        "seeds": a.seeds, "arrived": len(arrived),
        "within_pass_m": sum(e <= P["pass_m"] for e in errs), "pass_m": P["pass_m"],
        "final_err_med_m": q(errs, 50), "final_err_p95_m": q(errs, 95), "final_err_max_m": round(max(errs), 4),
        "final_yaw_err_med_deg": q([r["final_yaw_err_deg"] for r in rows], 50),
        "final_yaw_err_p95_deg": q([r["final_yaw_err_deg"] for r in rows], 95),
        "time_med_s": q([r["time_s"] for r in arrived], 50), "time_max_s": None if not arrived else max(r["time_s"] for r in arrived),
        "first_seen_med_s": q([r["first_seen_s"] for r in rows if r["first_seen_s"] is not None], 50),
        "start_range_m": [min(r["start_range_m"] for r in rows), max(r["start_range_m"] for r in rows)],
        "start_view_angle_deg": [min(r["start_view_angle_deg"] for r in rows), max(r["start_view_angle_deg"] for r in rows)],
        "frames_gross_heading_total": sum(r["frames_gross_heading"] for r in rows),
        "frames_detected_total": sum(r["frames_detected"] for r in rows),
        "frames_total": sum(r["frames"] for r in rows),
    }
    from importlib.metadata import version
    meta = {"input": "synthetic (rendered images, kinematic point mass)", "params": P,
            "goal_tag_frame_m": GOAL.tolist(), "tag_size_m": rd.TAG_SIZE,
            "camera": {"w": rd.W, "h": rd.H, "fx": rd.FX, "fy": rd.FY, "cx": rd.CX, "cy": rd.CY, "distortion": "none"},
            "pupil_apriltags": version("pupil-apriltags"), "python": platform.python_version(),
            "numpy": np.__version__, "opencv": cv2.__version__, "machine": platform.machine(),
            "workers": a.workers, "wall_s": wall,
            "command": "python final_approach.py " + " ".join(argv if argv is not None else __import__("sys").argv[1:])}
    pass_txt = "PASS" if summ["within_pass_m"] == a.seeds else "FAIL"
    lines = [
        f"# {a.name}: tag-relative servo to 1 m in front of a 0.16 m tag36h11 (synthetic)", "",
        f"Image blur sigma {P['blur_px']} px, noise sigma {P['noise_dn']} DN; velocity disturbance "
        f"{P['v_noise_mps']} m/s per axis, yaw-rate disturbance {P['yaw_noise_dps']} deg/s, "
        f"{P['latency_frames']} frame latency at {P['cam_hz']:g} Hz.", "",
        f"Command: `{meta['command'].strip()}`, wall {wall} s on {a.workers} workers. Input: synthetic.", "",
        "| seeds | arrived (stop rule) | true final err <= 0.1 m | final err med m | p95 m | max m | "
        "final yaw err med deg | p95 deg | time to arrive med s | max s | first detection med s |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        f"| {a.seeds} | {len(arrived)} | {summ['within_pass_m']} ({pass_txt} vs all seeds) | {summ['final_err_med_m']} | "
        f"{summ['final_err_p95_m']} | {summ['final_err_max_m']} | {summ['final_yaw_err_med_deg']} | "
        f"{summ['final_yaw_err_p95_deg']} | {summ['time_med_s']} | {summ['time_max_s']} | {summ['first_seen_med_s']} |", "",
        f"Start range {summ['start_range_m'][0]}-{summ['start_range_m'][1]} m, view angle "
        f"{summ['start_view_angle_deg'][0]}-{summ['start_view_angle_deg'][1]} deg. Frames with a detection: "
        f"{summ['frames_detected_total']} of {summ['frames_total']}; detections with heading error > 10 deg: "
        f"{summ['frames_gross_heading_total']}.", "",
        "| seed | start range m | start angle deg | arrived | time s | first seen s | final err m | yaw err deg | frames det/total | gross heading frames |",
        "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['seed']} | {r['start_range_m']} | {r['start_view_angle_deg']} | {r['arrived']} | {r['time_s']} | "
                     f"{r['first_seen_s']} | {r['final_err_m']} | {r['final_yaw_err_deg']} | "
                     f"{r['frames_detected']}/{r['frames']} | {r['frames_gross_heading']} |")
    print("\n".join(lines[:11]))
    if a.no_write:
        return summ, rows
    base = os.path.join(HERE, "results", a.name)
    with open(base + ".json", "w") as f:
        json.dump({"meta": meta, "summary": summ, "runs": rows}, f, indent=1)
    with open(base + ".md", "w") as f:
        f.write("\n".join(lines) + "\n")
    plot(rows, base + ".png")
    print(f"wrote {base}.json .md .png")
    return summ, rows


if __name__ == "__main__":
    main()
