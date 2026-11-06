"""Run utiasSTARS/pyshoe's own INS on the hallway trials and dump estimates at the
ground-truth markers to JSON (consumed by run_hallway.py --pyshoe).

Needs numpy<1.24 (pyshoe uses np.int / np.float / np.maximum_sctype) + scipy and a
pyshoe checkout (no license file in that repo, so it is not vendored here). The LSTM /
SVM detectors and liegroups are stubbed out: only the classical SHOE path runs.

usage: python pyshoe_compare.py <pyshoe-checkout> <data/hallway> <out.json>
"""
import glob
import json
import os
import sys
import types

import numpy as np
import scipy.io as sio

SHOE_G = 8.5e7  # pyshoe process_error_hallway.py middle SHOE threshold
SHOE_W = 5
SIGMA_A, SIGMA_W, T_NOMINAL = 0.00098, 8.7266463e-5, 1.0 / 200


def stub_modules():
    for name in ("ins_tools.LSTM", "ins_tools.SVM", "liegroups", "sklearn", "sklearn.externals"):
        sys.modules[name] = types.ModuleType(name)
    sys.modules["liegroups"].SO3 = None
    sys.modules["sklearn.externals"].joblib = None
    sys.modules["sklearn"].externals = sys.modules["sklearn.externals"]


def main(pyshoe_dir, data_dir, out_path):
    stub_modules()
    sys.path.insert(0, pyshoe_dir)
    from ins_tools.INS import INS

    out = {}
    for f in sorted(glob.glob(os.path.join(data_dir, "*/*/*/processed_data.mat"))):
        trial = os.path.relpath(os.path.dirname(f), data_dir)
        d = sio.loadmat(f)
        imu, ts, gi = d["imu"], d["ts"][0], d["gt_idx"][0]
        rec = {}
        for label, dt in (("T200", None), ("ts", np.r_[np.diff(ts), np.diff(ts)[-1]])):
            ins = INS(imu, sigma_a=SIGMA_A, sigma_w=SIGMA_W, T=T_NOMINAL, dt=dt)
            zv = ins.Localizer.compute_zv_lrt(W=SHOE_W, G=SHOE_G, detector="shoe")
            x = ins.baseline(zv=zv)
            rec[label] = x[gi, 0:3].tolist()
        rec["zv"] = "".join("1" if z else "0" for z in zv)
        out[trial] = rec
        print(trial, flush=True)
    with open(out_path, "w") as fh:
        json.dump(out, fh)


if __name__ == "__main__":
    main(*sys.argv[1:4])
