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
    def test_movers_move_and_runs_match_results(self):
        import numpy as np
        import arena
        import moving
        import run_moving

        w0 = arena.world.make_world("random", 0, 1)
        movers, n = moving.draw_movers(w0, 0, 1)
        self.assertTrue(1 <= len(movers) <= 3)
        mw = moving.MovingWorld(w0, movers, 1.0)
        m = movers[0]
        p0, p1 = m.at(0.0, 1.0), m.at(1.0, 1.0)
        self.assertAlmostEqual(math.hypot(p1[0] - p0[0], p1[1] - p0[1]), 1.0, delta=1e-6)
        # truth clearance and the ray cast see the mover where it is now, the prior grid does not
        for t, (mx, my) in ((0.0, p0), (1.0, p1)):
            mw.set_time(t)
            self.assertLess(mw.clearance(mx, my), 0.0)
            self.assertGreater(w0.clearance(mx, my), 0.0)
            ix, iy = w0.grid.to_index(mx, my)
            self.assertFalse(mw.grid.occ[ix, iy])
            d = mw.raycast(mx - 1.0, my, np.array([0.0]), 6.0)[0]
            self.assertAlmostEqual(d, 1.0 - m.r, delta=1e-6)
        # every arm runs, and one saved collision run reproduces
        for arm in run_moving.ARMS:
            r = run_moving.run_one(arm, 0.5, 0, 0)
            self.assertIn(r["outcome"], ("reached", "collision", "stuck", "timeout"))
        path = os.path.join(HERE, "results", "moving_0.json")
        if os.path.exists(path):
            saved = [x for x in json.load(open(path))["runs"]
                     if x["arm"] == "astar" and x["speed_mps"] == 1.0 and x["index"] == 1][0]
            r = run_moving.run_one("astar", 1.0, 1, 0)
            for k in ("outcome", "min_clearance_m", "t_collision_s", "warning_s"):
                self.assertEqual(saved[k], r[k])


if __name__ == "__main__":
    unittest.main()
