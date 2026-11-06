import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geo  # noqa: E402

try:
    import cv2
    import numpy as np
    import vpr
except ImportError:
    vpr = None


class TileGridTest(unittest.TestCase):
    def test_counts_and_extent(self):
        c = geo.tile_centres(1000, 600, 200, 100)
        self.assertEqual(len(c), 9 * 5)
        self.assertEqual(c[0], (100, 100))
        self.assertEqual(c[-1], (900, 500))

    def test_tiles_stay_inside(self):
        for e, s in geo.tile_centres(7000, 7000, 250, 50):
            self.assertGreaterEqual(e - 125, -1e-9)
            self.assertLessEqual(e + 125, 7000 + 1e-9)
            self.assertGreaterEqual(s - 125, -1e-9)

    def test_tile_larger_than_map(self):
        self.assertEqual(geo.tile_centres(100, 100, 200, 50), [])

    def test_worst_case_distance(self):
        self.assertAlmostEqual(geo.grid_worst_case_m(50), 35.355, places=3)


class AffineTest(unittest.TestCase):
    def test_round_trip(self):
        e0, n0, g = 433672.0, 4576232.0, 0.6
        for col, row in [(0, 0), (123.5, 77.25), (11666, 11666)]:
            e, n = geo.px_to_world(col, row, e0, n0, g)
            c2, r2 = geo.world_to_px(e, n, e0, n0, g)
            self.assertAlmostEqual(c2, col, places=6)
            self.assertAlmostEqual(r2, row, places=6)

    def test_north_is_up(self):
        _, n_top = geo.px_to_world(0, 0, 0.0, 1000.0, 1.0)
        _, n_down = geo.px_to_world(0, 10, 0.0, 1000.0, 1.0)
        self.assertGreater(n_top, n_down)

    def test_offset_to_world(self):
        self.assertEqual(geo.offset_to_world(500.0, 2000.0, 125.0, 125.0), (625.0, 1875.0))


class AngleTest(unittest.TestCase):
    def test_angle_diff_wraps(self):
        self.assertAlmostEqual(geo.angle_diff_deg(350, 10), 20)
        self.assertAlmostEqual(geo.angle_diff_deg(10, 350), 20)
        self.assertAlmostEqual(geo.angle_diff_deg(0, 180), 180)
        self.assertAlmostEqual(geo.angle_diff_deg(-90, 270), 0)

    def test_yaw_offset_is_rotation(self):
        for yaw in (0, 37, 90, 211):
            du, dv = geo.frame_offset_to_source(3.0, 4.0, yaw)
            self.assertAlmostEqual(math.hypot(du, dv), 5.0)
        self.assertEqual(geo.frame_offset_to_source(1.0, 0.0, 0), (1.0, 0.0))

    def test_haversine_one_degree_lat(self):
        self.assertAlmostEqual(geo.haversine_m(41.0, -81.0, 42.0, -81.0), 111195, delta=5)


class RecallTest(unittest.TestCase):
    def test_recall(self):
        d = [[10, 500], [300, 40], [600, 700]]
        r = geo.recall_at(d, ks=(1, 2), radii=(50, 1000))
        self.assertAlmostEqual(r["R@1<=50m"], 1 / 3)
        self.assertAlmostEqual(r["R@2<=50m"], 2 / 3)
        self.assertAlmostEqual(r["R@1<=1000m"], 1.0)

    def test_empty(self):
        self.assertEqual(geo.recall_at([], ks=(1,), radii=(50,)), {"R@1<=50m": 0.0})


@unittest.skipIf(vpr is None, "numpy / opencv / torch not installed")
class RenderTest(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        base = cv2.resize(rng.integers(0, 255, (40, 40, 3), dtype=np.uint8), (400, 400), interpolation=cv2.INTER_CUBIC)
        self.map = base

    def test_yaw_zero_is_plain_crop(self):
        t = vpr.render_tile(self.map, 1.0, (199.5, 199.5), 100, 100, 0)
        self.assertLess(np.abs(t.astype(int) - self.map[150:250, 150:250].astype(int)).mean(), 1.0)

    def test_rotated_tile_unrotates_to_north_up(self):
        north = vpr.render_tile(self.map, 1.0, (199.5, 199.5), 100, 101, 0)
        for yaw in (45, 90, 200):
            t = vpr.render_tile(self.map, 1.0, (199.5, 199.5), 100, 101, yaw)
            back = vpr.rotate_square(t, yaw)
            c = slice(30, 71)
            err = np.abs(back[c, c].astype(int) - north[c, c].astype(int)).mean()
            self.assertLess(err, 6.0, f"yaw {yaw}: {err}")

    def test_query_crop_ground_size(self):
        frame = np.zeros((480, 640, 3), np.uint8)
        crop, ground = vpr.query_crop(frame, 0.5, 200, 224)
        self.assertEqual(crop.shape, (224, 224, 3))
        self.assertAlmostEqual(ground, 200)
        _, ground = vpr.query_crop(frame, 0.5, 400, 224)
        self.assertAlmostEqual(ground, 240)

    def test_circle_mask(self):
        m = vpr.circle_patch_mask(16)
        self.assertEqual(m.shape, (256,))
        self.assertEqual(m.reshape(16, 16)[0, 0], 0)
        self.assertEqual(m.reshape(16, 16)[8, 8], 1)

    def test_ring_histogram_rotation_invariant(self):
        img = vpr.render_tile(self.map, 1.0, (199.5, 199.5), 150, 224, 0)
        a = vpr.ring_histogram(img)
        b = vpr.ring_histogram(vpr.rotate_square(img, 90))
        self.assertGreater(float(a @ b), 0.99)


if __name__ == "__main__":
    unittest.main()
