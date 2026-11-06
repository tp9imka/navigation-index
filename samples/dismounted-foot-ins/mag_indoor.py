"""Is the foot magnetometer usable for heading indoors? Real data from the pyshoe hallway
raw logs (imumagnetic_field.csv, Gauss; Microstrain IMU per a pyshoe script comment).

For each trial with a magnetometer log: remove hard iron with a sphere fit, then at every
stance onset compare the horizontal field direction (tilt-compensated with the INS
attitude) with its value at the start standstill. A uniform field gives a constant
direction; indoors it does not. Then fuse it as a 5 deg heading aid and compare.

usage: python3 mag_indoor.py data/hallway
"""
import csv
import glob
import math
import os
import statistics
import sys

import detectors
import run_hallway as R

GAUSS_TO_UT = 100.0
ACC_MATCH_TOL = 1e-9


def gauss_solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def sphere_fit(pts):
    """|m - c|^2 = r^2 => 2 c.m + (r^2 - |c|^2) = |m|^2, linear least squares."""
    A = [[0.0] * 4 for _ in range(4)]
    b = [0.0] * 4
    for m in pts:
        row = [2 * m[0], 2 * m[1], 2 * m[2], 1.0]
        y = m[0] ** 2 + m[1] ** 2 + m[2] ** 2
        for i in range(4):
            b[i] += row[i] * y
            for j in range(4):
                A[i][j] += row[i] * row[j]
    cx, cy, cz, k = gauss_solve(A, b)
    return (cx, cy, cz), math.sqrt(k + cx * cx + cy * cy + cz * cz)


def load_mag(trial_dir, tr):
    """Align raw mag rows to processed IMU samples via the shared ROS seq number."""
    with open(os.path.join(trial_dir, "imuimu_head.csv")) as fh:
        rows = [r for r in csv.reader(fh) if len(r) > 21]
    a0 = tr["acc"][0]
    seq0 = next(int(r[2]) for r in rows[1:]
                if all(abs(float(r[19 + i]) - a0[i]) < ACC_MATCH_TOL for i in range(3)))
    by_seq = {}
    with open(os.path.join(trial_dir, "imumagnetic_field.csv")) as fh:
        for r in list(csv.reader(fh))[1:]:
            by_seq[int(r[2])] = [float(r[8]) * GAUSS_TO_UT, float(r[9]) * GAUSS_TO_UT, float(r[10]) * GAUSS_TO_UT]
    mag = [by_seq.get(seq0 + k) for k in range(len(tr["acc"]))]
    missing = sum(m is None for m in mag)
    for k in range(len(mag)):
        if mag[k] is None:
            mag[k] = mag[k - 1]
    return mag, missing


def main(data_dir):
    print("| trial | hard iron (uT) | |B| after cal: min-max (uT) | heading residual: median abs / p95 abs / max abs (deg) "
          "| horizontal ARMSE none / mag / corridor (m) | max err none / mag / corridor (m) |")
    print("|---|---|---|---|---|---|")
    for p in sorted(glob.glob(os.path.join(data_dir, "*/*/*/imumagnetic_field.csv"))):
        d = os.path.dirname(p)
        tr = R.load_trial(os.path.join(d, "processed_data.mat"))
        tr["gi_set"] = set(tr["gi"])
        raw, missing = load_mag(d, tr)
        c, radius = sphere_fit(raw[::10])
        mag = [[m[i] - c[i] for i in range(3)] for m in raw]
        zv = detectors.stance(detectors.shoe(tr["acc"], tr["gyro"]), R.DEFAULT_DET[1])
        yaw0 = R.entry_yaw(tr, zv)
        res = {}
        for label, kw in (("none", {}), ("mag", {"mag_apply": True}), ("hde", {"hde": True})):
            est, st, _ = R.run(tr, zv, yaw0=yaw0, mag=mag, **kw)
            res[label] = (R.metrics(tr, est), st)
        resid = [abs(x) for x in res["none"][1]["mag_resid_deg"]]
        norms = res["none"][1]["mag_norm"]
        trial = os.path.relpath(d, data_dir)
        print("| %s | %.1f (|c|), fit r %.1f | %.1f - %.1f | %.1f / %.1f / %.1f | %.2f / %.2f / %.2f | %.2f / %.2f / %.2f |" % (
            trial + (" (%d mag samples missing)" % missing if missing else ""),
            math.sqrt(sum(x * x for x in c)), radius, min(norms), max(norms),
            statistics.median(resid), sorted(resid)[int(0.95 * len(resid))], max(resid),
            res["none"][0]["armse_h"], res["mag"][0]["armse_h"], res["hde"][0]["armse_h"],
            res["none"][0]["max_h"], res["mag"][0]["max_h"], res["hde"][0]["max_h"]))
    print("heading residual = horizontal field direction at each stance onset (INS-unaided attitude) "
          "minus its direction at the start standstill; 0 everywhere in a uniform field.")


if __name__ == "__main__":
    main(sys.argv[1])
