"""Time scipy.ndimage.distance_transform_edt on a 200 x 200 x 50 occupancy grid (2M cells,
a 20 x 20 x 5 m volume at 0.1 m) and on the arena's 200 x 200 2D grid.

python bench_edt.py   # writes results/edt_timing.json
"""
from __future__ import annotations

import json
import os
import platform
import time

import numpy as np
import scipy
from scipy.ndimage import distance_transform_edt

HERE = os.path.dirname(os.path.abspath(__file__))
REPEATS = 7
OCC_FRACTION = 0.05


def bench(shape, rng, repeats=REPEATS):
    free = rng.random(shape) >= OCC_FRACTION        # True = free, EDT gives distance to nearest occupied
    distance_transform_edt(free, sampling=0.1)        # warm-up, not timed
    ms = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        distance_transform_edt(free, sampling=0.1)
        ms.append((time.perf_counter() - t0) * 1e3)
    return {"shape": list(shape), "cells": int(np.prod(shape)), "occupied_fraction": OCC_FRACTION,
            "repeats": repeats, "ms_min": round(min(ms), 2), "ms_median": round(float(np.median(ms)), 2),
            "ms_max": round(max(ms), 2)}


def main():
    rng = np.random.default_rng(0)
    out = {
        "input": "synthetic (uniform random occupancy, seed 0)",
        "call": "scipy.ndimage.distance_transform_edt(free_mask, sampling=0.1), one warm-up then timed repeats",
        "grid_3d": bench((200, 200, 50), rng),
        "grid_2d": bench((200, 200), rng),
        "env": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                "machine": platform.machine(), "system": platform.system(), "processor": platform.processor()},
    }
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", "edt_timing.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    for k in ("grid_3d", "grid_2d"):
        r = out[k]
        print(f"{k} {r['shape']}: median {r['ms_median']} ms (min {r['ms_min']}, max {r['ms_max']}, n={r['repeats']})")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
