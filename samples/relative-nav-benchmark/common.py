"""Shared helpers: TUM trajectory IO, evo-based metrics, drift-per-distance, navdash/1 export."""
import json
import math
import os
import platform
import resource
import time

import numpy as np

R_EARTH = 6378137.0
SEGMENT_LENGTHS = (100, 200, 300, 400, 500, 600, 700, 800)


def quat_from_R(R):
    from scipy.spatial.transform import Rotation
    x, y, z, w = Rotation.from_matrix(R).as_quat()
    return w, x, y, z


def write_tum(path, stamps, poses):
    """poses: (N,4,4). TUM line: t x y z qx qy qz qw."""
    from scipy.spatial.transform import Rotation
    with open(path, "w") as f:
        for t, T in zip(stamps, poses):
            q = Rotation.from_matrix(T[:3, :3]).as_quat()
            f.write(f"{t:.6f} {T[0,3]:.6f} {T[1,3]:.6f} {T[2,3]:.6f} {q[0]:.9f} {q[1]:.9f} {q[2]:.9f} {q[3]:.9f}\n")


def path_length(xyz):
    return float(np.sum(np.linalg.norm(np.diff(xyz, axis=0), axis=1)))


def kitti_segment_errors(gt, est, lengths=SEGMENT_LENGTHS, step=10):
    """KITTI devkit style relative translation error (%) and rotation error (deg/100 m).

    gt, est: (N,4,4) synchronized poses. Segments start every `step` frames; a length is
    used only if the sequence is long enough to contain it.
    """
    xyz = gt[:, :3, 3]
    dist = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(xyz, axis=0), axis=1))])
    t_err, r_err, used = [], [], set()
    for i in range(0, len(gt), step):
        for L in lengths:
            j = int(np.searchsorted(dist, dist[i] + L))
            if j >= len(gt):
                continue
            used.add(L)
            dg = np.linalg.inv(gt[i]) @ gt[j]
            de = np.linalg.inv(est[i]) @ est[j]
            E = np.linalg.inv(de) @ dg
            t_err.append(np.linalg.norm(E[:3, 3]) / L)
            ang = math.acos(max(-1.0, min(1.0, (np.trace(E[:3, :3]) - 1) / 2)))
            r_err.append(math.degrees(ang) / L * 100)
    if not t_err:
        return None
    return {"t_rel_pct": 100 * float(np.mean(t_err)), "r_rel_deg_per_100m": float(np.mean(r_err)),
            "lengths_used_m": sorted(used), "segments": len(t_err)}


def evo_metrics(gt_tum, est_tum, max_diff=0.02, scale=False, rpe_delta_m=None):
    """ATE (aligned and origin-anchored) + RPE with evo; returns a dict of numbers."""
    from evo.core import metrics, sync
    from evo.tools import file_interface
    import copy

    ref = file_interface.read_tum_trajectory_file(gt_tum)
    est = file_interface.read_tum_trajectory_file(est_tum)
    ref, est = sync.associate_trajectories(ref, est, max_diff=max_diff)
    out = {"matched_poses": int(ref.num_poses), "gt_path_m": float(ref.path_length),
           "est_path_m": float(est.path_length), "duration_s": float(ref.timestamps[-1] - ref.timestamps[0])}

    a = copy.deepcopy(est)
    rot, tr, s = a.align(ref, correct_scale=scale)
    ape = metrics.APE(metrics.PoseRelation.translation_part)
    ape.process_data((ref, a))
    st = ape.get_all_statistics()
    out["ate_aligned"] = {"align": "sim3" if scale else "se3", "scale": float(s),
                          "rmse_m": st["rmse"], "mean_m": st["mean"], "max_m": st["max"]}

    o = copy.deepcopy(est)
    o.align_origin(ref)
    ape = metrics.APE(metrics.PoseRelation.translation_part)
    ape.process_data((ref, o))
    st = ape.get_all_statistics()
    end_err = float(np.linalg.norm(o.positions_xyz[-1] - ref.positions_xyz[-1]))
    out["origin_anchored"] = {"rmse_m": st["rmse"], "max_m": st["max"], "final_error_m": end_err,
                              "final_drift_pct_of_distance": 100 * end_err / max(ref.path_length, 1e-9),
                              "max_error_pct_of_distance": 100 * st["max"] / max(ref.path_length, 1e-9)}
    if rpe_delta_m:
        rpe = metrics.RPE(metrics.PoseRelation.translation_part, delta=rpe_delta_m,
                          delta_unit=metrics.Unit.meters, all_pairs=True)
        try:
            rpe.process_data((ref, a))
            st = rpe.get_all_statistics()
            out[f"rpe_{rpe_delta_m:g}m"] = {"rmse_m": st["rmse"], "mean_m": st["mean"],
                                            "mean_pct": 100 * st["mean"] / rpe_delta_m}
        except Exception as e:  # sequence shorter than delta
            out[f"rpe_{rpe_delta_m:g}m"] = {"error": str(e)}
    return out


def enu_to_ll(lat0, lon0, e, n):
    lat = lat0 + math.degrees(n / R_EARTH)
    lon = lon0 + math.degrees(e / (R_EARTH * math.cos(math.radians(lat0))))
    return lat, lon


def ll_to_enu(lat0, lon0, lat, lon):
    n = math.radians(lat - lat0) * R_EARTH
    e = math.radians(lon - lon0) * R_EARTH * math.cos(math.radians(lat0))
    return e, n


def write_navdash(path, track, role, label, rows, color=None, primary=False, extra=None, events=()):
    """rows: iterable of dicts with t, lat, lon (+ optional r95_m, health, sources)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    hdr = {"schema": "navdash/1", "track": track, "role": role, "label": label}
    if color:
        hdr["color"] = color
    if primary:
        hdr["primary"] = True
    hdr.update(extra or {})
    with open(path, "w") as f:
        f.write(json.dumps({"header": hdr}) + "\n")
        for r in rows:
            f.write(json.dumps({k: (round(v, 8) if isinstance(v, float) else v) for k, v in r.items()}) + "\n")
        for ev in events:
            f.write(json.dumps(ev) + "\n")


def write_manifest(path, title, tracks):
    with open(path, "w") as f:
        json.dump({"title": title, "tracks": tracks}, f, indent=1)


class RunStats:
    """Wall time, CPU time and peak RSS of this process (children included when requested)."""

    def __init__(self):
        self.t0 = time.perf_counter()
        self.c0 = time.process_time()

    def done(self):
        ru = resource.getrusage(resource.RUSAGE_SELF)
        rss = ru.ru_maxrss / (1 if platform.system() == "Darwin" else 1 / 1024)
        return {"wall_s": round(time.perf_counter() - self.t0, 2),
                "cpu_s": round(time.process_time() - self.c0, 2),
                "peak_rss_mb": round(rss / 1e6, 1),
                "host": f"{platform.system()} {platform.machine()} python{platform.python_version()}"}
