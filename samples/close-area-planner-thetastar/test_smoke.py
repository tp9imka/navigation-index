"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
import json
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


@unittest.skipUnless(HAVE_DEPS, "needs numpy and scipy (sample venv)")
class SmokeTest(unittest.TestCase):
    def test_search_and_fly(self):
        import numpy as np
        import arena
        import thetastar

        # open 40 x 40 grid with one wall: a few any-angle segments, not a cell-by-cell path
        blocked = np.zeros((40, 40), bool)
        blocked[20, 5:40] = True
        cost = np.ones((40, 40))
        for lazy in (False, True):
            st = {}
            p = thetastar.theta_star(blocked, cost, (5, 30), (35, 30), lazy=lazy, stats=st)
            self.assertIsNotNone(p)
            self.assertLessEqual(len(p), 6)
            L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p[:-1], p[1:]))
            self.assertLess(L, 1.02 * 2 * math.hypot(15, 26))   # near the taut path around the wall end
            self.assertAlmostEqual(st["cost"], thetastar.path_cost(p, cost, blocked), places=6)
        self.assertIsNone(thetastar.theta_star(np.ones((40, 40), bool), cost, (5, 5), (30, 30)))
        # make() with no arguments works; one arena flight matches results/flights_0.json
        self.assertEqual(thetastar.make().name, "thetastar_known")
        rows, _, _ = arena.run.evaluate(lambda: thetastar.make(), "random", 1, 0)
        ref_path = os.path.join(HERE, "results", "flights_0.json")
        if os.path.exists(ref_path):
            ref = [r for r in json.load(open(ref_path))["runs"]
                   if (r["planner"], r["family"], r["preset"], r["index"]) == ("thetastar_known", "random", "ideal", 0)]
            self.assertEqual(rows[0]["outcome"], ref[0]["outcome"])
            self.assertEqual(rows[0]["path_length_m"], ref[0]["path_length_m"])
        else:
            self.assertEqual(rows[0]["outcome"], "reached")


if __name__ == "__main__":
    unittest.main()
