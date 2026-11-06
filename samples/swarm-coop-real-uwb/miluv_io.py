"""Stdlib reader for the MILUV CSVs this sample uses (mocap, uwb_range, height).

Layout as written by fetch_miluv.py and the MILUV devkit: data/<experiment>/<robot>/<topic>.csv.
Constants below are copied from the devkit's config/ (MIT), commit on main as of 2026-11-06.
"""
import bisect
import csv
import math
import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
ROBOTS = ("ifo001", "ifo002", "ifo003")
TAGS = {"ifo001": (10, 11), "ifo002": (20, 21), "ifo003": (30, 31)}
TAG_ROBOT = {t: r for r, ts in TAGS.items() for t in ts}
TAG_ARMS = {  # config/uwb/tags.yaml, body frame, m
    10: (0.13189, -0.17245, -0.05249), 11: (-0.17542, 0.15712, -0.05307),
    20: (0.16544, -0.15085, -0.03456), 21: (-0.15467, 0.16972, -0.01680),
    30: (0.16685, -0.18113, -0.05576), 31: (-0.13485, 0.15468, -0.05164),
}
HEIGHT_BIAS = {"ifo001": -0.0924, "ifo002": -0.0088, "ifo003": -0.1207}  # config/height/bias.yaml
ANCHORS = {  # config/uwb/anchors.yaml, mocap frame, m
    "0": {0: (3.273827392578125, 3.46404736328125, 1.8093309326171875),
          1: (3.186386962890625, 0.27394485473632812, 1.5884853515625),
          2: (2.850500244140625, -2.923056884765625, 1.89742041015625),
          3: (-2.497634521484375, -3.5018203125, 1.7730911865234375),
          4: (-2.95793310546875, 0.6128419189453125, 1.65714208984375),
          5: (-2.734676513671875, 3.65854248046875, 1.890254638671875)},
}
EXPERIMENTS = {  # config/experiments.csv: anchor constellation per experiment
    "default_3_zigzag_0": "0",
    "default_3_random_0": "0",
    "cirObstacles_3_random_0": "0",
}
MOCAP_MAX_GAP = 0.1  # s, no interpolation across mocap dropouts longer than this


@dataclass
class Range:
    t: float
    frm: int
    to: int
    r: float          # calibrated range from the devkit preprocessing
    r_raw: float      # before bias / antenna-delay calibration
    gt: float         # devkit truth: mocap tag-to-tag (or tag-to-anchor) distance


class Track:
    """Mocap pose of one robot: position + quaternion, linearly interpolated."""

    def __init__(self, t, pos, quat):
        self.t, self.pos, self.quat = t, pos, quat

    def _idx(self, t):
        k = bisect.bisect_right(self.t, t)
        if k == 0 or k == len(self.t):
            return None
        if self.t[k] - self.t[k - 1] > MOCAP_MAX_GAP:
            return None
        return k

    def at(self, t):
        k = self._idx(t)
        if k is None:
            return None
        t0, t1 = self.t[k - 1], self.t[k]
        w = (t - t0) / (t1 - t0)
        a, b = self.pos[k - 1], self.pos[k]
        return tuple(a[i] + w * (b[i] - a[i]) for i in range(3))

    def quat_at(self, t):
        k = self._idx(t)
        return None if k is None else self.quat[k - 1]

    def span(self):
        return self.t[0], self.t[-1]


def _rows(exp, robot, topic, data_dir):
    with open(os.path.join(data_dir, exp, robot, topic + ".csv"), newline="") as f:
        yield from csv.DictReader(f)


def load_track(exp, robot, data_dir=DATA_DIR):
    seen = {}
    for r in _rows(exp, robot, "mocap", data_dir):
        p = (float(r["pose.position.x"]), float(r["pose.position.y"]), float(r["pose.position.z"]))
        q = (float(r["pose.orientation.x"]), float(r["pose.orientation.y"]), float(r["pose.orientation.z"]),
             float(r["pose.orientation.w"]))
        if math.hypot(*p) < 1e-6 or math.hypot(*q) < 1e-6:
            continue  # mocap gap marker, as in the devkit
        seen[float(r["timestamp"])] = (p, q)
    ts = sorted(seen)
    return Track(ts, [seen[t][0] for t in ts], [seen[t][1] for t in ts])


def load_height(exp, robot, data_dir=DATA_DIR):
    """Downward rangefinder height, devkit bias removed; returns (times, values) for a zero-order hold."""
    rows = sorted((float(r["timestamp"]), float(r["range"]) - HEIGHT_BIAS[robot])
                  for r in _rows(exp, robot, "height", data_dir))
    return [t for t, _ in rows], [h for _, h in rows]


def zoh(times, vals, t):
    k = bisect.bisect_right(times, t)
    return vals[k - 1] if k else None


def load_ranges(exp, data_dir=DATA_DIR):
    """All two-way ranges of the experiment, de-duplicated (inter-robot ranges appear in both robots' files)."""
    out = {}
    for robot in ROBOTS:
        for r in _rows(exp, robot, "uwb_range", data_dir):
            key = (int(r["from_id"]), int(r["to_id"]), r["timestamp"])
            if key in out:
                continue
            out[key] = Range(float(r["timestamp"]), key[0], key[1], float(r["range"]), float(r["range_raw"]),
                             float(r["gt_range"]))
    return sorted(out.values(), key=lambda m: m.t)


def anchors_for(exp):
    return ANCHORS[EXPERIMENTS[exp]]


def is_anchor(node):
    return node < 10


def rotate(q, v):
    x, y, z, w = q
    # v' = v + 2 w (u x v) + 2 u x (u x v), u = (x, y, z)
    cx, cy, cz = y * v[2] - z * v[1], z * v[0] - x * v[2], x * v[1] - y * v[0]
    ccx, ccy, ccz = y * cz - z * cy, z * cx - x * cz, x * cy - y * cx
    return (v[0] + 2 * (w * cx + ccx), v[1] + 2 * (w * cy + ccy), v[2] + 2 * (w * cz + ccz))


def node_position(node, t, tracks, anchors):
    """World position of a tag (mocap pose + lever arm) or an anchor; None during mocap gaps."""
    if is_anchor(node):
        return anchors[node]
    tr = tracks[TAG_ROBOT[node]]
    p, q = tr.at(t), tr.quat_at(t)
    if p is None or q is None:
        return None
    arm = rotate(q, TAG_ARMS[node])
    return (p[0] + arm[0], p[1] + arm[1], p[2] + arm[2])


def have_data(exp, data_dir=DATA_DIR):
    return all(os.path.exists(os.path.join(data_dir, exp, r, f + ".csv"))
               for r in ROBOTS for f in ("mocap", "uwb_range", "height"))
