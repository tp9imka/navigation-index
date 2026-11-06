import math
import unittest

from geom import Gate, affine_scale_rot, frame_gsd_m, haversine_m, offset_latlon, summarize

try:
    import cv2
    import numpy as np
    HAVE_CV = True
except ImportError:
    HAVE_CV = False


def rot_scale_h(scale, deg, tx=0.0, ty=0.0):
    r = math.radians(deg)
    return [[scale * math.cos(r), -scale * math.sin(r), tx],
            [scale * math.sin(r), scale * math.cos(r), ty],
            [0.0, 0.0, 1.0]]


class GeomTest(unittest.TestCase):
    def test_gsd_m4t_at_324m(self):
        # DJI M4T thermal as stored in Thermal-UAV: 1280x1024, 9.83 mm diagonal, 12 mm lens
        g = frame_gsd_m(324.0, 12.0, 9.83, 1280, 1024)
        self.assertAlmostEqual(g, 0.1619, places=3)

    def test_offset_roundtrip(self):
        lat, lon = offset_latlon(28.24, 112.99, 100.0, 37.0)
        self.assertAlmostEqual(haversine_m(28.24, 112.99, lat, lon), 100.0, delta=0.05)

    def test_scale_rot(self):
        s, r, det = affine_scale_rot(rot_scale_h(1.1, 12.0, 5, 7))
        self.assertAlmostEqual(s, 1.1, places=6)
        self.assertAlmostEqual(r, 12.0, places=6)
        self.assertGreater(det, 0)


class GateTest(unittest.TestCase):
    def test_accepts_consistent_fix(self):
        ok, why = Gate().check(80, 120, rot_scale_h(1.02, 3.0), 90.0, 150.0, 300.0)
        self.assertTrue(ok, why)

    def test_rejects_few_inliers(self):
        ok, why = Gate().check(12, 20, rot_scale_h(1.0, 0.0), 10.0, 150.0, 300.0)
        self.assertFalse(ok)
        self.assertTrue(any("inliers" in w for w in why))

    def test_rejects_wrong_scale_and_rotation(self):
        ok, why = Gate().check(200, 300, rot_scale_h(1.6, 40.0), 10.0, 150.0, 300.0)
        self.assertFalse(ok)
        self.assertTrue(any("scale" in w for w in why))
        self.assertTrue(any("rotation" in w for w in why))

    def test_rejects_mirror_and_outside_radius(self):
        h = [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        ok, why = Gate().check(200, 300, h, 400.0, 150.0, 300.0)
        self.assertFalse(ok)
        self.assertTrue(any("mirrored" in w for w in why))
        self.assertTrue(any("search radius" in w for w in why))

    def test_rejects_perspective(self):
        h = rot_scale_h(1.0, 0.0)
        h[2][0] = 1e-3
        ok, why = Gate().check(200, 300, h, 10.0, 150.0, 300.0)
        self.assertFalse(ok)
        self.assertTrue(any("perspective" in w for w in why))

    def test_summarize_counts_false_fixes(self):
        s = summarize([2.0, 4.0, 300.0], 10, 20.0)
        self.assertEqual((s["accepted"], s["correct"], s["false_fixes"]), (3, 2, 1))
        self.assertAlmostEqual(s["fix_rate"], 0.3)
        self.assertAlmostEqual(s["median_err_m"], 3.0)


@unittest.skipIf(not HAVE_CV, "numpy/opencv not installed")
class PreprocTest(unittest.TestCase):
    def test_grad_is_contrast_sign_invariant(self):
        try:
            from thermal_geoloc import preprocess
        except ImportError as e:
            self.skipTest(f"thermal_geoloc deps missing: {e}")
        img = np.zeros((64, 64), np.uint8)
        img[16:48, 16:48] = 200
        a = preprocess(img, "grad").astype(int)
        b = preprocess(255 - img, "grad").astype(int)
        self.assertLessEqual(np.abs(a - b).max(), 1)
        self.assertGreater(a.max(), 200)

    def test_north_up_centre(self):
        try:
            from thermal_geoloc import north_up
        except ImportError as e:
            self.skipTest(f"thermal_geoloc deps missing: {e}")
        img = np.zeros((100, 200), np.uint8)
        out, mask, c = north_up(img, 0.2, 90.0, 0.4)
        self.assertEqual(out.shape[0], 100)
        self.assertIn(out.shape[1], (50, 51))
        self.assertAlmostEqual(c[0], 24.5, delta=1.0)
        self.assertAlmostEqual(c[1], 49.5, delta=1.0)


if __name__ == "__main__":
    unittest.main()
