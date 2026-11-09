"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy / cv2 / pupil_apriltags.

.venv/bin/python -m unittest test_smoke -v
"""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import numpy as np
    import cv2  # noqa: F401
    import pupil_apriltags  # noqa: F401
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


@unittest.skipUnless(HAVE_DEPS, "needs numpy, opencv and pupil-apriltags (sample venv)")
class SmokeTest(unittest.TestCase):
    def test_render_detect_pose_and_approach(self):
        import render as rd
        import sweep
        import final_approach as fa

        # the rendered tag is decoded as the right id and the pose matches the truth at 2 m, 40 deg
        renderer = rd.Renderer()
        det = sweep.make_detector(1.0)
        a = math.radians(40)
        R, t = rd.look_at_pose(2.0 * np.array([math.sin(a), 0, -math.cos(a)]))
        img = renderer.render(R, t, np.random.default_rng(0), blur_px=0.8, noise_dn=3)
        d = [x for x in det.detect(img, True, (rd.FX, rd.FY, rd.CX, rd.CY), rd.TAG_SIZE) if x.tag_id == rd.TAG_ID]
        self.assertEqual(len(d), 1)
        self.assertLess(np.linalg.norm(d[0].pose_t.ravel() - t), 0.02)
        self.assertLess(abs(math.degrees(rd.wrap(rd.heading_of(d[0].pose_R) - rd.heading_of(R)))), 2.0)

        # far beyond the measured range limit nothing is detected
        R, t = rd.look_at_pose([0, 0, -8.0])
        self.assertEqual(det.detect(renderer.render(R, t)), [])

        # one approach seed arrives within the 0.1 m threshold
        row = fa.run_seed(0, dict(fa.P))
        self.assertTrue(row["arrived"])
        self.assertLess(row["final_err_m"], 0.1)


if __name__ == "__main__":
    unittest.main()
