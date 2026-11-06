"""Part 1: KISS-ICP LiDAR odometry on a KITTI raw drive, scored with evo against KITTI odometry GT.

Usage: python lidar/run_kiss_icp_kitti.py --data <dir with 2011_09_30/> --poses <dir with poses/NN.txt> --seq 04
"""
import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402

HERE = Path(__file__).resolve().parents[1]


def read_stamps(path, i0, i1):
    out = []
    for line in open(path).read().split("\n"):
        if line.strip():
            out.append(datetime.strptime(line.strip()[:26], "%Y-%m-%d %H:%M:%S.%f").timestamp())
    out = np.array(out[i0:i1 + 1])
    return out - out[0]


def oxts_enu_poses(oxts_files):
    """T_world_imu with world = local ENU at the first packet (flat earth, fine over < 5 km)."""
    lat0 = lon0 = alt0 = None
    poses, ll = [], []
    for fn in oxts_files:
        v = [float(x) for x in open(fn).read().split()]
        lat, lon, alt, roll, pitch, yaw = v[:6]
        if lat0 is None:
            lat0, lon0, alt0 = lat, lon, alt
        e, n = common.ll_to_enu(lat0, lon0, lat, lon)
        cr, sr, cp, sp, cy, sy = math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        T = np.eye(4)
        T[:3, :3] = Rz @ Ry @ Rx
        T[:3, 3] = (e, n, alt - alt0)
        poses.append(T)
        ll.append((lat, lon))
    return np.array(poses), ll


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="dir that holds 2011_09_30/ (calib + drive)")
    ap.add_argument("--poses", required=True, help="dir that holds KITTI odometry poses/NN.txt")
    ap.add_argument("--seq", default="04")
    ap.add_argument("--out", default=str(HERE / "results" / "lidar"))
    ap.add_argument("--max-range", type=float, default=100.0)
    ap.add_argument("--no-deskew", action="store_true")
    a = ap.parse_args()

    from kiss_icp.config import load_config
    from kiss_icp.datasets.kitti_raw import KITTIRawDataset
    from kiss_icp.kiss_icp import KissICP

    stats = common.RunStats()
    ds = KITTIRawDataset(Path(a.data), a.seq)
    cfg = load_config(None)
    cfg.data.max_range = a.max_range
    cfg.mapping.voxel_size = a.max_range / 100.0
    cfg.data.deskew = not a.no_deskew
    odom = KissICP(cfg)

    i0, i1 = ds.valid_idx
    stamps = read_stamps(os.path.join(ds.root_dir, "velodyne_points", "timestamps.txt"), i0, i1)
    est = []
    n_pts = 0
    for k in range(len(ds)):
        pts, ts = ds[k]
        n_pts += len(pts)
        odom.register_frame(pts, ts if cfg.data.deskew else np.array([]))
        est.append(odom.last_pose.copy())
        if k % 50 == 0:
            print(f"frame {k}/{len(ds)}", flush=True)
    est = np.array(est)
    run = stats.done()
    run["frames"] = len(ds)
    run["fps"] = round(len(ds) / run["wall_s"], 1)
    run["mean_points_per_scan"] = int(n_pts / len(ds))

    # Odometry GT is cam0 (rectified) frame; conjugate into the velodyne frame.
    c = ds.calibration
    Tr = c["T_cam0_velo"]
    gt_cam = np.loadtxt(os.path.join(a.poses, f"{a.seq}.txt")).reshape(-1, 3, 4)
    gt_cam = np.concatenate([gt_cam, np.tile([[[0, 0, 0, 1]]], (len(gt_cam), 1, 1))], axis=1)
    gt = np.linalg.inv(Tr) @ gt_cam @ Tr
    assert len(gt) == len(est), (len(gt), len(est))

    os.makedirs(a.out, exist_ok=True)
    gt_path, est_path = os.path.join(a.out, f"kitti{a.seq}_gt.tum"), os.path.join(a.out, f"kitti{a.seq}_kiss_icp.tum")
    common.write_tum(gt_path, stamps, gt)
    common.write_tum(est_path, stamps, est)
    res = {"part": "lidar", "method": "KISS-ICP (pip kiss-icp, default config)", "dataset": f"KITTI odometry {a.seq} via raw drive {Path(ds.root_dir).name}",
           "config": {"max_range_m": a.max_range, "voxel_size_m": cfg.mapping.voxel_size, "deskew": cfg.data.deskew},
           "metrics": common.evo_metrics(gt_path, est_path, rpe_delta_m=100),
           "kitti_segment_errors": common.kitti_segment_errors(gt, est),
           "run": run}

    # OXTS GPS/INS as an independent geodetic truth for the dashboard and a cross-check.
    T_w_imu, ll = oxts_enu_poses(ds.oxts_files)
    T_imu_velo = np.linalg.inv(c["T_velo_imu"])
    est_w = T_w_imu[0] @ T_imu_velo @ est @ c["T_velo_imu"]  # IMU position, comparable to OXTS
    lat0, lon0 = ll[0]
    truth_rows = [{"t": float(t), "lat": la, "lon": lo} for t, (la, lo) in zip(stamps, ll)]
    est_rows = []
    for t, T in zip(stamps, est_w):
        la, lo = common.enu_to_ll(lat0, lon0, T[0, 3], T[1, 3])
        est_rows.append({"t": float(t), "lat": la, "lon": lo, "health": "trusted", "sources": ["lidar-odometry"]})
    oxts_w = T_w_imu @ T_imu_velo
    gt_oxts_path = os.path.join(a.out, f"kitti{a.seq}_oxts.tum")
    common.write_tum(gt_oxts_path, stamps, oxts_w)
    res["metrics_vs_oxts"] = common.evo_metrics(gt_oxts_path, est_path, rpe_delta_m=100)

    nd = HERE / "results" / "navdash" / f"kitti{a.seq}"
    common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "OXTS GPS/INS (KITTI raw)", truth_rows)
    common.write_navdash(str(nd / "kiss_icp.jsonl"), "kiss-icp", "fused", "KISS-ICP lidar odometry, origin-anchored",
                         est_rows, color="#4fc3f7", primary=True,
                         extra={"run_meta": {"anchor": "first OXTS pose; no later absolute fixes"}})
    common.write_manifest(str(nd / "manifest.json"), f"KITTI {a.seq}: KISS-ICP vs OXTS", ["truth.jsonl", "kiss_icp.jsonl"])

    with open(os.path.join(a.out, f"kitti{a.seq}_result.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
