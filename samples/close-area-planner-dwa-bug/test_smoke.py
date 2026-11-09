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
    def test_planners_run_and_match_results(self):
        import arena
        import bench

        self.assertEqual(arena.cfg_for("cf4")["sensor"]["n_beams"], 4)
        for name in ("dwa", "bug2", "tangent_bug"):
            for fan in arena.FANS:
                rows, _, _ = arena.run.evaluate(bench.PLANNERS[name], "random", 1, 3, cfg=arena.cfg_for(fan))
                self.assertIn(rows[0]["outcome"], ("reached", "collision", "stuck", "timeout"))
        # u_trap seed 0 run 0, both fans: same outcome and path length as results/dwa_bug_0.json
        with open(os.path.join(HERE, "results", "dwa_bug_0.json")) as fh:
            saved = {(c["planner"], c["fan"], c["family"]): c["runs"][0] for c in json.load(fh)["cells"]}
        for name in ("dwa", "bug2", "tangent_bug"):
            for fan in arena.FANS:
                rows, _, _ = arena.run.evaluate(bench.PLANNERS[name], "u_trap", 1, 0, cfg=arena.cfg_for(fan))
                ref = saved[(name, fan, "u_trap")]
                self.assertEqual(rows[0]["outcome"], ref["outcome"], (name, fan))
                self.assertEqual(rows[0]["path_length_m"], ref["path_length_m"], (name, fan))


if __name__ == "__main__":
    unittest.main()
