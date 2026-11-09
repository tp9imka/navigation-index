"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
import json
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
    def test_gap_world_plan_and_fly(self):
        import numpy as np
        import arena
        import rrt_star

        # gap=None reproduces the arena layout; a fixed gap keeps the rest of the layout
        self.assertEqual(arena.gap_world(None, 0, 3).to_dict(), arena.world.make_world("narrow_gap", 0, 3).to_dict())
        w = arena.gap_world(1.2, 0, 0)
        self.assertAlmostEqual(w.gap_m, 1.2)
        # informed RRT* finds a path at 1.2 m and the shortcut path is free on the exact geometry
        esdf = w.grid.esdf()
        r = rrt_star.plan_on_grid(w.grid, esdf, (0.0, 0.0), (*w.goal, 1.0), 1000, np.random.default_rng(0), True)
        self.assertIsNotNone(r["path_xy"])
        self.assertGreater(min(float(w.sdf(p)) for p in r["path_xy"]), 0.15)
        # flight in the arena: same outcome and path length as results/arena_narrow_gap_0.json run 0
        name = "informed_rrt_star iters=5000"
        ref = json.load(open(os.path.join(HERE, "results", "arena_narrow_gap_0.json")))["modes"][name]["runs"][0]
        rows, _, _ = arena.run.evaluate(lambda: rrt_star.RRTStarPlanner(5000, True, seed=0), "narrow_gap", 1, 0)
        self.assertEqual(rows[0]["outcome"], ref["outcome"])
        self.assertEqual(rows[0]["path_length_m"], ref["path_length_m"])


if __name__ == "__main__":
    unittest.main()
