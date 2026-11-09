"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy/osqp.

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
    import osqp  # noqa: F401
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


@unittest.skipUnless(HAVE_DEPS, "needs numpy, scipy and osqp (sample venv)")
class SmokeTest(unittest.TestCase):
    def test_model_and_one_run_match_results(self):
        import numpy as np
        import arena
        import mpc

        # discretisation reproduces the arena vehicle (no clipping) over one 0.1 s hold
        A, B = mpc.discretise()
        veh = arena.run.Vehicle if hasattr(arena.run, "Vehicle") else None
        self.assertIsNotNone(veh)
        v = veh(0.0, 0.0, 1.0, tau=0.15, a_max=100.0, v_max=100.0)
        v.v[:2] = [0.3, -0.2]
        x = np.array([0.0, 0.0, 0.3, -0.2])
        for _ in range(5):
            v.step(1.0, 0.5)
        x = A @ x + B @ np.array([1.0, 0.5])
        self.assertLess(np.abs(np.r_[v.p[:2], v.v[:2]] - x).max(), 0.02)   # Euler 50 Hz vs exact

        # narrow_gap seed 0 run 0: same outcome and min clearance as results/mpc_compare_0.json
        made = []
        rows, _, _ = arena.run.evaluate(lambda: made.append(mpc.AStarMPC()) or made[-1], "narrow_gap", 1, 0)
        with open(os.path.join(HERE, "results", "mpc_compare_0.json")) as fh:
            ref = json.load(fh)["results"]["narrow_gap"]["astar_mpc"]["runs"][0]
        self.assertEqual(rows[0]["outcome"], ref["outcome"])
        self.assertEqual(rows[0]["min_clearance_m"], ref["min_clearance_m"])
        self.assertEqual(made[0].fail_steps, 0)
        self.assertGreater(len(made[0].qp_ms), 0)


if __name__ == "__main__":
    unittest.main()
