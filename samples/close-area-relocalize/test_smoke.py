"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np
    import scipy  # noqa: F401
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


@unittest.skipUnless(HAVE_DEPS, "needs numpy and scipy (sample venv)")
class SmokeTest(unittest.TestCase):
    def test_matcher_rule_and_one_flight(self):
        from arena import run, sensors, world
        import relocalize as R
        import experiment as X

        w = world.make_world("random", seed=1, index=0)
        fan = sensors.RangeFan(rng=np.random.default_rng(0), **run.DEFAULTS["sensor"])
        x, y, yaw = 3.0, 3.0, 0.3
        if w.clearance(x, y) < 0.3:
            x, y = 0.5, 0.5
        scan = fan.scan(w, x, y, yaw, 0.0)
        hyps = R.ScanMatcher(w.grid).hypotheses(scan, yaw, (x + 0.4, y - 0.3))
        self.assertTrue(1 <= len(hyps) <= R.K_MAX)
        self.assertLess(math.hypot(hyps[0].x - x, hyps[0].y - y), 0.2)

        rule = R.RatioPersistence()
        H = R.Hypothesis
        self.assertEqual(rule.update([])[0], "none")
        self.assertEqual(rule.update([H(0, 0, 0.9), H(1, 0, 0.895)])[0], "ambiguous")
        self.assertEqual([rule.update([H(0, 0, 0.9), H(1, 0, 0.5)])[0] for _ in range(3)],
                         ["pending", "pending", "accept"])
        self.assertEqual(R.single_rule().update([H(0, 0, 0.1), H(1, 0, 0.1)])[0], "accept")

        _, arm, rows, _ = X.run_cell(("jump", "multi", "random", 1, 0))
        self.assertEqual(arm, "multi")
        self.assertIn(rows[0]["outcome"], ("reached", "collision", "stuck", "timeout"))
        self.assertIn("events", rows[0])


if __name__ == "__main__":
    unittest.main()
