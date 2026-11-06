import json
import math
import os
import sys
import tempfile
import unittest

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import numpy as np
    import scipy  # noqa: F401  (common.write_tum)
    import evo  # noqa: F401
    sys.path.insert(0, HERE)
    import common
    _spec = importlib.util.spec_from_file_location("relnav_vo_to_altpnt", os.path.join(HERE, "integrate", "vo_to_altpnt.py"))
    vo_to_altpnt = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(vo_to_altpnt)
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


def straight(n=400, step=1.0, scale=1.0, yaw=0.0, wiggle=False):
    poses = []
    for i in range(n):
        T = np.eye(4)
        T[0, 3] = scale * step * i * math.cos(yaw)
        T[1, 3] = scale * step * i * math.sin(yaw)
        if wiggle:
            T[1, 3] += scale * 2.0 * math.sin(i / 50)
            T[2, 3] = scale * math.sin(i / 30)
        poses.append(T)
    return np.array(poses)


@unittest.skipIf(not HAVE_DEPS, "needs numpy, scipy, evo (requirements.txt)")
class Metrics(unittest.TestCase):
    def test_segment_error_zero_for_identical(self):
        gt = straight()
        r = common.kitti_segment_errors(gt, gt)
        self.assertAlmostEqual(r["t_rel_pct"], 0.0, places=9)

    def test_segment_error_detects_scale(self):
        r = common.kitti_segment_errors(straight(), straight(scale=1.02))
        self.assertAlmostEqual(r["t_rel_pct"], 2.0, delta=0.05)

    def test_evo_final_drift(self):
        gt, est = straight(wiggle=True), straight(scale=1.01, wiggle=True)
        with tempfile.TemporaryDirectory() as d:
            g, e = os.path.join(d, "g.tum"), os.path.join(d, "e.tum")
            t = np.arange(len(gt)) * 0.1
            common.write_tum(g, t, gt)
            common.write_tum(e, t, est)
            m = common.evo_metrics(g, e)
            self.assertAlmostEqual(m["origin_anchored"]["final_drift_pct_of_distance"], 1.0, delta=0.05)
            fit = vo_to_altpnt.fit_error_model(g, e)
            self.assertAlmostEqual(fit["scale_err"], 0.01, delta=1e-3)
            self.assertAlmostEqual(fit["yaw_err_rad"], 0.0, delta=1e-6)

    def test_navdash_header_and_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x", "t.jsonl")
            common.write_navdash(p, "trk", "fused", "L", [{"t": 0.0, "lat": 1.0, "lon": 2.0}], primary=True)
            lines = [json.loads(x) for x in open(p)]
            self.assertEqual(lines[0]["header"]["schema"], "navdash/1")
            self.assertTrue(lines[0]["header"]["primary"])
            self.assertEqual(set(lines[1]), {"t", "lat", "lon"})

    def test_enu_roundtrip(self):
        lat, lon = common.enu_to_ll(49.0, 8.4, 300.0, -200.0)
        e, n = common.ll_to_enu(49.0, 8.4, lat, lon)
        self.assertAlmostEqual(e, 300.0, places=6)
        self.assertAlmostEqual(n, -200.0, places=6)


if __name__ == "__main__":
    unittest.main()
