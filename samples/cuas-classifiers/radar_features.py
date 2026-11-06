"""Per-track kinematic and RCS features for NRC/Echodyne radar tracks.

Frame (checked on the data, see README): posY is vertical (posY ~= range*sin(elevation)),
posZ is roughly along boresight. The annotated .xlsx files carry no timestamps; the
dataset docs state a 10 Hz track-update rate, so dt is taken as UPDATE_DT_S.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

UPDATE_DT_S = 0.1
MIN_UPDATES = 10
EPS = 1e-9
VERTICAL_AXIS = 1  # index into (x, y, z)

KINEMATIC_FEATURES = [
    "duration_s", "speed_mean", "speed_std", "speed_p90", "speed_max",
    "vz_abs_mean", "vz_std", "climb_ratio",
    "accel_mean", "accel_std", "accel_p90",
    "turn_rate_mean", "turn_rate_std", "turn_rate_p90",
    "curvature_median", "straightness", "speed_cv",
]
RCS_FEATURES = ["rcs_mean", "rcs_std", "rcs_median", "rcs_p10", "rcs_p90", "rcs_iqr", "rcs_missing_frac"]
FEATURES = KINEMATIC_FEATURES + RCS_FEATURES


def heading_change(vel_xy):
    """Unsigned heading change (rad) between consecutive horizontal velocity vectors."""
    h = np.arctan2(vel_xy[:, 1], vel_xy[:, 0])
    d = np.diff(h)
    return np.abs((d + np.pi) % (2 * np.pi) - np.pi)


def track_features(pos, vel, rcs, dt=UPDATE_DT_S):
    """pos, vel: (n, 3) arrays in radar frame (m, m/s); rcs: (n,) dBsm with NaN allowed."""
    pos = np.asarray(pos, float)
    vel = np.asarray(vel, float)
    rcs = np.asarray(rcs, float)
    n = len(pos)
    speed = np.linalg.norm(vel, axis=1)
    vz = vel[:, VERTICAL_AXIS]
    horiz = np.delete(vel, VERTICAL_AXIS, axis=1)
    hspeed = np.linalg.norm(horiz, axis=1)

    acc = np.linalg.norm(np.diff(vel, axis=0), axis=1) / dt
    dh = heading_change(horiz)
    moving = (hspeed[1:] > 0.5) & (hspeed[:-1] > 0.5)
    turn_rate = dh[moving] / dt if moving.any() else np.zeros(1)

    step = np.linalg.norm(np.diff(pos, axis=0), axis=1)
    path_len = step.sum()
    net = np.linalg.norm(pos[-1] - pos[0])

    # curvature |v x a| / |v|^3 on the tracker's own velocity, ignoring near-hover samples
    a_vec = np.diff(vel, axis=0) / dt
    v_mid = vel[1:]
    sp = np.linalg.norm(v_mid, axis=1)
    ok = sp > 1.0
    curv = np.linalg.norm(np.cross(v_mid[ok], a_vec[ok]), axis=1) / sp[ok] ** 3 if ok.any() else np.array([np.nan])

    r = rcs[np.isfinite(rcs)]
    rq = np.percentile(r, [10, 25, 50, 75, 90]) if len(r) else [np.nan] * 5
    return {
        "n_updates": n,
        "duration_s": n * dt,
        "speed_mean": speed.mean(),
        "speed_std": speed.std(),
        "speed_p90": np.percentile(speed, 90),
        "speed_max": speed.max(),
        "speed_cv": speed.std() / (speed.mean() + EPS),
        "vz_abs_mean": np.abs(vz).mean(),
        "vz_std": vz.std(),
        "climb_ratio": np.abs(vz).mean() / (hspeed.mean() + EPS),
        "accel_mean": acc.mean(),
        "accel_std": acc.std(),
        "accel_p90": np.percentile(acc, 90),
        "turn_rate_mean": turn_rate.mean(),
        "turn_rate_std": turn_rate.std(),
        "turn_rate_p90": np.percentile(turn_rate, 90),
        "curvature_median": np.nanmedian(curv) if len(curv) else np.nan,
        "straightness": net / (path_len + EPS),
        "rcs_mean": r.mean() if len(r) else np.nan,
        "rcs_std": r.std() if len(r) else np.nan,
        "rcs_median": rq[2],
        "rcs_p10": rq[0],
        "rcs_p90": rq[4],
        "rcs_iqr": rq[3] - rq[1],
        "rcs_missing_frac": 1.0 - len(r) / n,
    }


def session_key(file_name):
    """Demo-0 used two radars at once (-R1/-R2): both files see the same flights, so they
    must land in the same CV group."""
    return re.sub(r"-R\d+\.xlsx$", "", file_name).replace(".xlsx", "")


def load_dataset(root, min_updates=MIN_UPDATES):
    """root: data/radar (the downloaded repo layout). Returns one row per labelled track."""
    root = Path(root)
    labels = pd.read_csv(root / "metadata" / "track_labels.csv")
    labels = labels[labels["file"].str.endswith(".xlsx")]
    rows = []
    for (folder, fname), lab in labels.groupby(["folder", "file"]):
        df = pd.read_excel(root / "data" / folder / fname, sheet_name=0)
        df = df[pd.to_numeric(df["SystemTrackID"], errors="coerce").notna()]
        df["SystemTrackID"] = df["SystemTrackID"].astype(float).astype(int)
        by_id = dict(tuple(df.groupby("SystemTrackID", sort=False)))
        for _, lr in lab.iterrows():
            t = by_id.get(int(lr["system_track_id"]))
            if t is None or len(t) < min_updates:
                continue
            f = track_features(t[["posX", "posY", "posZ"]].to_numpy(),
                               t[["veloX", "veloY", "veloZ"]].to_numpy(),
                               t["rcs"].to_numpy())
            f.update(folder=folder, file=fname, session=f"{folder}/{session_key(fname)}",
                     track_id=int(lr["system_track_id"]), label=lr["label"],
                     range_mean=t["range"].mean())
            rows.append(f)
    return pd.DataFrame(rows)
