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
    def test_plan_vehicle_and_flight(self):
        import numpy as np
        import arena
        import bench
        import hybrid_astar
        from vehicle_turn import TurnLimitedVehicle

        # make() with no arguments; known-map plan on maze 0 is a Hybrid A* path clear of obstacles
        self.assertEqual(hybrid_astar.make().name, "hybrid_astar_unknown")
        w = arena.mod("world_glass").make_any_world("maze", 0, 0)
        p = hybrid_astar.make(known_map=True)
        p.reset()
        p._plan(arena.Pose(0, 0, 0, 1, 0, 0, 0, math.atan2(w.goal[1], w.goal[0])), (*w.goal, 1.0), w.grid)
        self.assertEqual(p.last_source, "hybrid")
        self.assertLess(math.hypot(*(p.path_xy[-1] - np.array(w.goal))), 1e-6)
        self.assertGreater(min(float(w.sdf(q)) for q in p.path_xy), 0.15)

        # the turn-limited vehicle turns its velocity at <= omega_max at speed
        v = TurnLimitedVehicle(omega_max=1.0)
        for _ in range(100):
            v.step(1.5, 0.0)
        h0 = math.atan2(v.v[1], v.v[0])
        for _ in range(25):                       # 0.5 s of a 90 deg command
            v.step(0.0, 1.5)
        self.assertLessEqual(abs(math.atan2(v.v[1], v.v[0]) - h0), 0.5 + 1e-6)

        # one flight reproduces results/bench_0.json (hybrid_astar, random 0, ideal, turn1)
        ref = next(r for r in json.load(open(os.path.join(HERE, "results", "bench_0.json")))["runs"]
                   if r["planner"] == "hybrid_astar" and r["family"] == "random" and r["preset"] == "ideal"
                   and r["vehicle"] == "turn1" and r["index"] == 0)
        row = bench.run_one("hybrid_astar", "random", "ideal", "turn1", 0, 0)
        self.assertEqual(row["outcome"], ref["outcome"])
        self.assertEqual(row["path_length_m"], ref["path_length_m"])


if __name__ == "__main__":
    unittest.main()
