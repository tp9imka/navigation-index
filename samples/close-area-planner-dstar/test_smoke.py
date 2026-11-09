"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
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
    def test_incremental_cost_matches_astar_on_changing_grid(self):
        import numpy as np
        import dstar_lite as D
        A = D.A
        rng = np.random.default_rng(0)
        n = 60
        blocked = np.zeros((n, n), bool)
        blocked[0, :] = blocked[-1, :] = blocked[:, 0] = blocked[:, -1] = True
        cost = 1.0 + rng.random((n, n))
        goal, start = (55, 55), (4, 4)
        ds = D.DStarLite((n, n), goal)
        for step in range(6):
            if step:                                   # new wall piece + cost changes near the start
                blocked[10 + 5 * step, 3:40] = True
                cost[2:20, 2:20] = 1.0 + rng.random((18, 18))
                start = (start[0] + 1, start[1])
            pd = ds.plan(blocked.copy(), cost.copy(), start)
            pa = A.astar(blocked, cost, start, goal)
            ca, cd = D.path_cost(pa, cost, blocked), D.path_cost(pd, cost, blocked)
            self.assertIsNotNone(cd)
            self.assertLessEqual(cd, ca + 1e-9)
            self.assertLess((ca - cd) / cd, 1e-3)
            self.assertAlmostEqual(ds.cost_to_go(), cd, places=6)
        # integer costs make exact-arithmetic key ties; the strict textbook test failed 50 of 300 here
        import compare
        self.assertEqual([sd for sd in range(20) if compare.fuzz_trial(sd, 0, 0, 1) is not None], [])
        self.assertEqual([sd for sd in range(20) if compare.fuzz_trial(sd, 1, 1, 1) is not None], [])

    def test_planner_flies_one_layout_with_verify(self):
        import arena
        import dstar_lite as D
        made = []

        def f():
            made.append(D.make(backend="dstar", verify=True))
            return made[-1]

        rows, _, _ = arena.run.evaluate(f, "u_trap", 1, 0)
        self.assertEqual(rows[0]["outcome"], "reached")
        for c in made[0].checks:
            self.assertEqual(c["dstar_none"], c["astar_none"])
            if c["dstar_cost"] is not None:
                self.assertLess((c["astar_cost"] - c["dstar_cost"]) / c["dstar_cost"], 1e-3)


if __name__ == "__main__":
    unittest.main()
