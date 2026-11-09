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
    def test_harness_matches_arena_and_results(self):
        import arena
        import filters
        import run_kill
        import unsensed

        # F0 on truth, unsensed off, reproduces the arena's own A* run
        ref, _, _ = arena.run.evaluate(lambda: arena.astar_esdf.make(known_map=True), "random", 1, 0)
        mine = run_kill.run_one("F0", "truth", False, 0, 0)
        for k in ("outcome", "min_clearance_m", "path_length_m"):
            self.assertEqual(ref[0][k], mine[k])
        # unsensed obstacles: in truth geometry, invisible to the wrapped fan
        w0 = arena.world.make_world("random", 0, 0)
        w, placed = unsensed.add_unsensed(w0, 0, 0)
        self.assertEqual(len(placed), unsensed.N_PER_LAYOUT)
        u = placed[0]
        self.assertLess(w.clearance(u.cx, u.cy), 0.0)
        self.assertGreater(w0.clearance(u.cx, u.cy), 0.0)
        # every arm runs; F2 jump run 0 matches the saved result
        for arm in filters.REGISTRY:
            r = run_kill.run_one(arm, "jump", True, 0, 0)
            self.assertIn(r["outcome"], ("reached", "collision", "stuck", "timeout"))
        path = os.path.join(HERE, "results", "kill_a_unsensed_on_0.json")
        if os.path.exists(path):
            saved = [x for x in json.load(open(path))["runs"]
                     if x["arm"] == "F2" and x["case"] == "jump" and x["index"] == 0][0]
            self.assertEqual(saved["outcome"], r["outcome"])
            self.assertEqual(saved["min_clearance_m"], r["min_clearance_m"])


if __name__ == "__main__":
    unittest.main()
