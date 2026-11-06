"""Part 2: extract GT from a UZH-FPV bag, run the mono VO baseline, convert OpenVINS output,
score both with evo, export navdash/1.

Usage: python vio/eval_uzhfpv.py --bag <indoor_forward_3_snapdragon_with_gt.bag> [--openvins <dir>]
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from mono_vo import MonoVO, chain  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
# OpenVINS config/uzhfpv_indoor/kalibr_imucam_chain.yaml, cam0 (v2.7)
K0 = np.array([[278.66723066149086, 0, 319.75221200593535], [0, 278.48991409740296, 241.96858910358173], [0, 0, 1]])
D0 = np.array([-0.013721808247486035, 0.020727425669427896, -0.012786476702685545, 0.0025242267320687625])
T_CAM_IMU = np.array([[-0.028228787368606456, -0.999601488301944, 1.2175294828553618e-05, 0.02172388268966517],
                      [0.014401251861751119, -0.00041887083271471837, -0.9998962088597202, -6.605455433829172e-05],
                      [0.999497743623523, -0.028225682131089447, 0.014407337010089172, -0.00048817563004522853],
                      [0, 0, 0, 1]])
CAM_TOPIC = "/snappy_cam/stereo_l"
GT_TOPIC = "/groundtruth/pose"
# Dashboard needs WGS84; UZH-FPV indoor has none. Arbitrary placeholder origin (Zurich, UZH-FPV's city).
PLACEHOLDER_ORIGIN = (47.3970, 8.5490)


def pose_mat(p, q_xyzw):
    T = np.eye(4)
    T[:3, :3] = Rotation.from_quat(q_xyzw).as_matrix()
    T[:3, 3] = p
    return T


def interp_pose(ts, poses, t):
    i = int(np.searchsorted(ts, t))
    if i <= 0 or i >= len(ts):
        return None
    a = (t - ts[i - 1]) / (ts[i] - ts[i - 1])
    p = (1 - a) * poses[i - 1][:3, 3] + a * poses[i][:3, 3]
    from scipy.spatial.transform import Slerp
    R = Slerp([0, 1], Rotation.from_matrix([poses[i - 1][:3, :3], poses[i][:3, :3]]))(a).as_matrix()
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def read_bag(bag, stride):
    from rosbags.highlevel import AnyReader
    imgs, gt_t, gt = [], [], []
    with AnyReader([Path(bag)]) as r:
        topics = {c.topic: c.msgtype for c in r.connections}
        conns = [c for c in r.connections if c.topic in (CAM_TOPIC, GT_TOPIC)]
        n = 0
        for c, t, raw in r.messages(connections=conns):
            m = r.deserialize(raw, c.msgtype)
            st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            if c.topic == GT_TOPIC:
                p, q = m.pose.position, m.pose.orientation
                gt_t.append(st)
                gt.append(pose_mat((p.x, p.y, p.z), (q.x, q.y, q.z, q.w)))
            else:
                n += 1
                if n % stride == 0:
                    imgs.append((st, np.frombuffer(m.data, np.uint8).reshape(m.height, m.width).copy()))
    return topics, imgs, np.array(gt_t), np.array(gt)


def run_mono(imgs, gt_t, gt):
    stats = common.RunStats()
    vo = MonoVO(K0, D0, fisheye=True)
    steps, kf_t = [], []
    for k, (t, img) in enumerate(imgs):
        if interp_pose(gt_t, gt, t) is None:
            continue
        r = vo.step(img, k)
        if r is None:
            if not kf_t:
                kf_t.append(t)
            continue
        i0, i1, R, tu, n = r
        steps.append((imgs[i0][0], t, R, tu))
    # GT step lengths act as the scale oracle (camera centre displacement).
    T_imu_cam = np.linalg.inv(T_CAM_IMU)
    scales, rel = [], []
    for t0, t1, R, tu in steps:
        c0 = interp_pose(gt_t, gt, t0) @ T_imu_cam
        c1 = interp_pose(gt_t, gt, t1) @ T_imu_cam
        scales.append(np.linalg.norm(c1[:3, 3] - c0[:3, 3]))
        rel.append((R, tu))
    t_first = steps[0][0]
    cams = chain(interp_pose(gt_t, gt, t_first) @ T_imu_cam, rel, scales)
    bodies = [T @ T_CAM_IMU for T in cams]
    stamps = [t_first] + [s[1] for s in steps]
    run = stats.done()
    run.update({"frames_in": len(imgs), "keyframes": len(steps) + 1, "rejected_pairs": vo.rejected})
    return np.array(stamps), np.array(bodies), run


def read_openvins(path):
    rows = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
    stamps, poses = [], []
    for r in rows:
        v = [float(x) for x in r[:8]]
        # OpenVINS stores JPL q_GtoI; its x,y,z,w equal the Hamilton q_ItoG used by TUM.
        stamps.append(v[0])
        poses.append(pose_mat(v[5:8], v[1:5]))
    return np.array(stamps), np.array(poses)


def navdash_rows(stamps, poses, t0, origin_T, sources):
    rows = []
    for t, T in zip(stamps, poses):
        p = (np.linalg.inv(origin_T) @ T)[:3, 3]
        la, lo = common.enu_to_ll(*PLACEHOLDER_ORIGIN, p[0], p[1])
        rows.append({"t": round(float(t - t0), 3), "lat": la, "lon": lo, "sources": sources})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", required=True)
    ap.add_argument("--openvins", help="dir with ov_state_est.txt from run_openvins.sh")
    ap.add_argument("--stride", type=int, default=1, help="use every Nth camera frame")
    ap.add_argument("--name", default="uzhfpv_indoor_forward_3")
    a = ap.parse_args()
    out = HERE / "results" / "vio"
    out.mkdir(parents=True, exist_ok=True)

    topics, imgs, gt_t, gt = read_bag(a.bag, a.stride)
    print("bag topics:", topics)
    print(f"{len(imgs)} images, {len(gt)} GT poses over {gt_t[-1] - gt_t[0]:.1f} s")
    gt_path = out / f"{a.name}_gt.tum"
    common.write_tum(gt_path, gt_t, gt)
    res = {"part": "vio", "dataset": f"UZH-FPV {a.name} (Snapdragon, 640x480 fisheye stereo, IMU)", "gt_topic": GT_TOPIC}

    stamps, poses, run = run_mono(imgs, gt_t, gt)
    mono_path = out / f"{a.name}_mono_vo.tum"
    common.write_tum(mono_path, stamps, poses)
    res["mono_vo"] = {"method": "OpenCV mono VO (KLT + essential matrix), GT step-length scale oracle, left cam",
                      "metrics": common.evo_metrics(str(gt_path), str(mono_path), max_diff=0.02, rpe_delta_m=10),
                      "run": run}
    nd = HERE / "results" / "navdash" / a.name
    t0 = gt_t[0]
    common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "UZH-FPV ground truth (placeholder geodetic origin)",
                         navdash_rows(gt_t[::10], gt[::10], t0, gt[0], ["truth"]))
    common.write_navdash(str(nd / "mono_vo.jsonl"), "mono-vo", "ins", "Mono VO, GT-scale oracle",
                         navdash_rows(stamps, poses, t0, gt[0], ["mono-vo"]), color="#ffb74d")
    tracks = ["truth.jsonl", "mono_vo.jsonl"]

    if a.openvins:
        est = Path(a.openvins) / "ov_state_est.txt"
        ot, op = read_openvins(est)
        ov_path = out / f"{a.name}_openvins.tum"
        common.write_tum(ov_path, ot, op)
        ov = {"method": "OpenVINS v2.7 MSCKF, config uzhfpv_indoor, stereo + IMU, ros1_serial_msckf in Docker",
              "metrics": common.evo_metrics(str(gt_path), str(ov_path), max_diff=0.02, rpe_delta_m=10)}
        tf = Path(a.openvins) / "run_time.json"
        if tf.exists():
            ov["run"] = json.load(open(tf))
        res["openvins"] = ov
        # Anchor OpenVINS (own gravity-aligned world frame) at the first GT pose: known start, no later fixes.
        from evo.tools import file_interface
        from evo.core import sync
        ref = file_interface.read_tum_trajectory_file(str(gt_path))
        e = file_interface.read_tum_trajectory_file(str(ov_path))
        ref, e = sync.associate_trajectories(ref, e, max_diff=0.02)
        e.align_origin(ref)
        common.write_navdash(str(nd / "openvins.jsonl"), "openvins", "fused", "OpenVINS stereo-inertial, origin-anchored",
                             navdash_rows(e.timestamps[::5], e.poses_se3[::5], t0, gt[0], ["vio"]), color="#4fc3f7", primary=True)
        tracks.append("openvins.jsonl")
    common.write_manifest(str(nd / "manifest.json"), f"{a.name}: VO/VIO vs ground truth (local frame on placeholder origin)", tracks)
    with open(out / f"{a.name}_result.json", "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
