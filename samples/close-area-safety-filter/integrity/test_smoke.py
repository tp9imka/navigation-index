"""Smoke test: the monitor's decisions on hand-made epochs, and one arena run end to end.

.venv/bin/python -m unittest test_smoke -v     (skips without numpy)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import numpy as np
except ImportError:  # plain python3 without packages
    np = None


@unittest.skipIf(np is None, "needs numpy (sample venv)")
class Smoke(unittest.TestCase):
    def setUp(self):
        import monitor
        import uwb

        class W:
            xmin, ymin, xmax, ymax = -1.5, -1.5, 18.5, 18.5

        self.monitor = monitor
        self.anchors = uwb.make_anchors(W)
        self.p = np.array([4.0, 6.0, 1.0])     # off both anchor diagonals
        self.r = np.linalg.norm(self.anchors - self.p, axis=1) + np.array([0.02, -0.03, 0.01, -0.01])

    def step(self, variant, vio_off=(0.0, 0.0), nlos=None):
        r = self.r.copy()
        if nlos:
            r[nlos[0]] += nlos[1]
        return self.monitor.Monitor(self.anchors, variant).step(self.p[:2] + np.array(vio_off), 0.15, r, 1.0)

    def test_decisions(self):
        o = self.step("ss2")
        self.assertEqual(o["status"], "ok")
        self.assertLess(abs(o["x"][0] - 4.0) + abs(o["x"][1] - 6.0), 0.1)
        self.assertEqual(self.step("ss2", vio_off=(0.8, 0.0))["excluded"], ("vio",))
        self.assertEqual(self.step("ss2", nlos=(1, 1.0))["excluded"], ("a1",))
        self.assertTrue(self.step("2src", nlos=(1, 1.0))["ambiguous"])      # two sources cannot be split
        self.assertFalse(self.step("maxsep", nlos=(1, 1.0))["ambiguous"])   # max-separation always guesses

    def test_arena_run(self):
        import run_monitor
        res, arrays = run_monitor.run_layout(("uwb_nlos", 0, 0, ["ss2"]))
        c = res["variants"]["ss2"]
        self.assertGreater(c["epochs"], 10)
        self.assertEqual(len(arrays["ss2"][0]), c["avail"])


if __name__ == "__main__":
    unittest.main()
