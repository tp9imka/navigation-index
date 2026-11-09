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
    def test_planners_run_on_both_fans_and_match_results(self):
        import arena
        import apf
        import vfh_plus

        self.assertEqual(arena.cfg_for("cf4")["sensor"]["n_beams"], 4)
        self.assertEqual(arena.cfg_for("cf4")["sensor"]["max_range"], 4.0)
        for make in (apf.make, vfh_plus.make):
            for fan in arena.FANS:
                rows, _, _ = arena.run.evaluate(make, "random", 1, 3, cfg=arena.cfg_for(fan))
                self.assertIn(rows[0]["outcome"], ("reached", "collision", "stuck", "timeout"))
        # u_trap seed 0 run 0, default fan: same outcomes as the plots in results/
        r_apf, _, _ = arena.run.evaluate(apf.make, "u_trap", 1, 0, cfg=arena.cfg_for("default"))
        r_vfh, _, _ = arena.run.evaluate(vfh_plus.make, "u_trap", 1, 0, cfg=arena.cfg_for("default"))
        self.assertEqual(r_apf[0]["outcome"], "reached")
        self.assertEqual(r_vfh[0]["outcome"], "stuck")
        r_again, _, _ = arena.run.evaluate(apf.make, "u_trap", 1, 0, cfg=arena.cfg_for("default"))
        self.assertEqual(r_apf[0]["path_length_m"], r_again[0]["path_length_m"])


if __name__ == "__main__":
    unittest.main()
