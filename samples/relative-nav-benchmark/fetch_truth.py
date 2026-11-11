"""Download the public datasets and write the ground-truth files this repo does not redistribute.

KITTI and UZH-FPV are CC BY-NC-SA 3.0 and VPAIR is "academic use only", so the repo ships only
the trajectories this sample computed. This script runs fetch_data.sh for a part and writes:

  lidar:  results/lidar/kitti04_gt.tum, results/lidar/kitti04_oxts.tum, results/navdash/kitti04/truth.jsonl
  vio:    results/vio/uzhfpv_indoor_forward_3_gt.tum, results/navdash/uzhfpv_indoor_forward_3/truth.jsonl
  aerial: results/aerial/vpair_gt.tum, results/navdash/vpair/truth.jsonl

It puts truth.jsonl back into each navdash manifest and compares every file with the SHA-256
in results/truth_sha256.json (the copy behind the README numbers). No estimator runs.

Usage: .venv/bin/python fetch_truth.py [lidar|vio|aerial|all] [--no-download]
Downloads: lidar 1.13 GB, vio 1.61 GB, aerial 0.86 GB (see fetch_data.sh). Paths are git-ignored.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

R = HERE / "results"
DATA = Path(os.environ.get("RELNAV_DATA", HERE / "data"))
SEQ = "04"
UZH = "uzhfpv_indoor_forward_3"


def fetch(part):
    subprocess.run([str(HERE / "fetch_data.sh"), part], check=True)


def add_truth_to_manifest(nd):
    p = nd / "manifest.json"
    m = json.loads(p.read_text())
    if "truth.jsonl" not in m["tracks"]:
        m["tracks"].insert(0, "truth.jsonl")
        common.write_manifest(str(p), m["title"], m["tracks"])


def truth_lidar():
    """Same steps as lidar/run_kiss_icp_kitti.py, without KISS-ICP."""
    sys.path.insert(0, str(HERE / "lidar"))
    from run_kiss_icp_kitti import oxts_enu_poses, read_stamps
    from kiss_icp.datasets.kitti_raw import KITTIRawDataset
    ds = KITTIRawDataset(DATA / "kitti", SEQ)
    i0, i1 = ds.valid_idx
    stamps = read_stamps(os.path.join(ds.root_dir, "velodyne_points", "timestamps.txt"), i0, i1)
    c = ds.calibration
    Tr = c["T_cam0_velo"]
    gt_cam = np.loadtxt(DATA / "kitti" / "dataset" / "poses" / f"{SEQ}.txt").reshape(-1, 3, 4)
    gt_cam = np.concatenate([gt_cam, np.tile([[[0, 0, 0, 1]]], (len(gt_cam), 1, 1))], axis=1)
    gt = np.linalg.inv(Tr) @ gt_cam @ Tr
    assert len(gt) == len(stamps), (len(gt), len(stamps))
    (R / "lidar").mkdir(parents=True, exist_ok=True)
    common.write_tum(R / "lidar" / f"kitti{SEQ}_gt.tum", stamps, gt)
    T_w_imu, ll = oxts_enu_poses(ds.oxts_files)
    common.write_tum(R / "lidar" / f"kitti{SEQ}_oxts.tum", stamps, T_w_imu @ np.linalg.inv(c["T_velo_imu"]))
    nd = R / "navdash" / f"kitti{SEQ}"
    common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "OXTS GPS/INS (KITTI raw)",
                         [{"t": float(t), "lat": la, "lon": lo} for t, (la, lo) in zip(stamps, ll)])
    add_truth_to_manifest(nd)
    return [f"results/lidar/kitti{SEQ}_gt.tum", f"results/lidar/kitti{SEQ}_oxts.tum", f"results/navdash/kitti{SEQ}/truth.jsonl"]


def truth_vio():
    """GT topic of the bag only (vio/eval_uzhfpv.py also decodes every image)."""
    sys.path.insert(0, str(HERE / "vio"))
    from eval_uzhfpv import GT_TOPIC, navdash_rows, pose_mat
    from rosbags.highlevel import AnyReader
    bag = DATA / "uzhfpv" / "indoor_forward_3_snapdragon_with_gt.bag"
    gt_t, gt = [], []
    with AnyReader([bag]) as r:
        conns = [c for c in r.connections if c.topic == GT_TOPIC]
        for c, _, raw in r.messages(connections=conns):
            m = r.deserialize(raw, c.msgtype)
            p, q = m.pose.position, m.pose.orientation
            gt_t.append(m.header.stamp.sec + m.header.stamp.nanosec * 1e-9)
            gt.append(pose_mat((p.x, p.y, p.z), (q.x, q.y, q.z, q.w)))
    gt_t, gt = np.array(gt_t), np.array(gt)
    (R / "vio").mkdir(parents=True, exist_ok=True)
    common.write_tum(R / "vio" / f"{UZH}_gt.tum", gt_t, gt)
    nd = R / "navdash" / UZH
    common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "UZH-FPV ground truth (placeholder geodetic origin)",
                         navdash_rows(gt_t[::10], gt[::10], gt_t[0], gt[0], ["truth"]))
    add_truth_to_manifest(nd)
    return [f"results/vio/{UZH}_gt.tum", f"results/navdash/{UZH}/truth.jsonl"]


def truth_aerial():
    """Same steps as aerial/run_nadir_vo.py, without the VO."""
    sys.path.insert(0, str(HERE / "aerial"))
    from run_nadir_vo import FRAME_DT, ecef_to_lla
    root = DATA / "vpair" / "vpair_sample"
    rows = [l.strip().split(",") for l in open(root / "poses_query.txt") if l.strip()][1:]
    lla = [ecef_to_lla(*map(float, r[1:4])) for r in rows]
    lat0, lon0, _ = lla[0]
    en = np.array([common.ll_to_enu(lat0, lon0, la, lo) for la, lo, _ in lla])
    stamps = np.arange(len(rows)) * FRAME_DT
    to_T = lambda xy: [np.block([[np.eye(2), np.zeros((2, 1)), np.array([[x], [y]])], [np.zeros((2, 2)), np.eye(2)]]) for x, y in xy]
    (R / "aerial").mkdir(parents=True, exist_ok=True)
    common.write_tum(R / "aerial" / "vpair_gt.tum", stamps, to_T(en))
    nd = R / "navdash" / "vpair"
    common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "VPAIR query poses (GNSS)",
                         [{"t": float(t), "lat": la, "lon": lo} for t, (la, lo, _) in zip(stamps, lla)])
    add_truth_to_manifest(nd)
    return ["results/aerial/vpair_gt.tum", "results/navdash/vpair/truth.jsonl"]


PARTS = {"lidar": truth_lidar, "vio": truth_vio, "aerial": truth_aerial}


def check(paths):
    ref = json.loads((R / "truth_sha256.json").read_text())["files"]
    same = True
    for p in paths:
        h = hashlib.sha256((HERE / p).read_bytes()).hexdigest()
        ok = h == ref.get(p)
        same &= ok
        print(f"{'same' if ok else 'DIFFERENT'}  {p}")
    if not same:
        print("A file differs from the copy behind the README numbers (library version or data revision?). "
              "Rerun ./run.sh <part> to recompute the metrics against it.")
    return same


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("part", nargs="?", default="all", choices=[*PARTS, "all"])
    ap.add_argument("--no-download", action="store_true", help="data/ is already there")
    a = ap.parse_args()
    paths = []
    for part in (PARTS if a.part == "all" else [a.part]):
        if not a.no_download:
            fetch(part)
        paths += PARTS[part]()
    sys.exit(0 if check(paths) else 1)


if __name__ == "__main__":
    main()
