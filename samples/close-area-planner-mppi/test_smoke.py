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
    def test_model_make_and_flight(self):
        import numpy as np
        import bench
        import mppi

        # rollout model == the arena vehicle (50 Hz Euler, same clipping) for a constant setpoint
        veh = bench.vehicle.Vehicle(0.0, 0.0, 1.0, v_max=2.0)
        veh.v[:2] = (0.5, -0.2)
        p = mppi.make()
        V = np.tile([[1.8, 1.4]], (1, 10, 1))
        P = p.rollout((0.0, 0.0), (0.5, -0.2), V)
        for _ in range(10 * p.sub):
            veh.step(1.8, 1.4)
        self.assertLess(float(np.hypot(*(P[0, -1] - veh.p[:2]))), 1e-9)
        # make() with no arguments plans one step and respects the setpoint cap
        w = bench.world_glass.make_any_world("random", 0, 0)
        ad = bench.arena.adapter.SimAdapter(w, bench.vehicle.Vehicle(), bench.presets.make_sensor(
            "ideal", np.random.default_rng([0, 0, 7])))
        for guide in ("none", "astar"):
            pl = mppi.make(guide=guide)
            sp = pl.step(ad.pose(), ad.ranges(), (w.goal[0], w.goal[1], 1.0), None, 0.1)
            self.assertLessEqual(float(np.hypot(sp.vx, sp.vy)), mppi.V_MAX + 1e-9)
        # one flight reproduces results/bench_ideal_0.json (outcome and path length)
        with open(os.path.join(HERE, "results", "bench_ideal_0.json")) as fh:
            ref = json.load(fh)["runs"]
        ref = next(r for r in ref if r["planner"] == "mppi_astar" and r["family"] == "u_trap" and r["index"] == 0)
        row, _, _ = bench.run_one("mppi_astar", "u_trap", "ideal", 0, 0)
        self.assertEqual(row["outcome"], ref["outcome"])
        self.assertEqual(row["path_length_m"], ref["path_length_m"])


if __name__ == "__main__":
    unittest.main()
