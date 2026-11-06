import math
import unittest

import geo_math as g

# WGS84 meridian arc length from the equator to 45 deg latitude.
MERIDIAN_ARC_45_M = 4984944.378
TILE_GSD_M = 0.5
TILE_ORIGIN = (465000.0, 5205000.0)  # UTM 32N, top-left corner


def similarity_h(scale, angle_deg, tx, ty):
    c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    return [[scale * c, -scale * s, tx], [scale * s, scale * c, ty], [0.0, 0.0, 1.0]]


class GeotransformTests(unittest.TestCase):
    def setUp(self):
        self.t = (TILE_GSD_M, 0.0, TILE_ORIGIN[0], 0.0, -TILE_GSD_M, TILE_ORIGIN[1])

    def test_corner_and_centre(self):
        self.assertEqual(g.pixel_to_world(self.t, 0, 0), TILE_ORIGIN)
        x, y = g.pixel_to_world(self.t, 0.5, 0.5)
        self.assertAlmostEqual(x, TILE_ORIGIN[0] + 0.25)
        self.assertAlmostEqual(y, TILE_ORIGIN[1] - 0.25)

    def test_round_trip_with_rotation_terms(self):
        t = (0.4, 0.1, 1000.0, 0.05, -0.4, 2000.0)
        col, row = g.world_to_pixel(t, *g.pixel_to_world(t, 123.4, 567.8))
        self.assertAlmostEqual(col, 123.4, places=9)
        self.assertAlmostEqual(row, 567.8, places=9)

    def test_from_gdal(self):
        gdal = (TILE_ORIGIN[0], TILE_GSD_M, 0.0, TILE_ORIGIN[1], 0.0, -TILE_GSD_M)
        self.assertEqual(g.from_gdal(gdal), self.t)


class HomographyTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(g.apply_homography([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 3.0, 4.0), (3.0, 4.0))

    def test_similarity(self):
        x, y = g.apply_homography(similarity_h(2.0, 90.0, 10.0, 20.0), 1.0, 0.0)
        self.assertAlmostEqual(x, 10.0)
        self.assertAlmostEqual(y, 22.0)

    def test_projective_divide(self):
        H = [[1, 0, 0], [0, 1, 0], [0.001, 0, 1]]
        x, y = g.apply_homography(H, 1000.0, 500.0)
        self.assertAlmostEqual(x, 500.0)
        self.assertAlmostEqual(y, 250.0)

    def test_degenerate(self):
        with self.assertRaises(ValueError):
            g.apply_homography([[1, 0, 0], [0, 1, 0], [0, 0, 0]], 1.0, 1.0)


class FrameCentreTests(unittest.TestCase):
    def test_rotated_scaled_frame_centre_lands_on_expected_ground_point(self):
        w, h = 640, 480
        tile_t = (TILE_GSD_M, 0.0, TILE_ORIGIN[0], 0.0, -TILE_GSD_M, TILE_ORIGIN[1])
        H = similarity_h(0.5, 30.0, 800.0, 600.0)
        cx, cy = (w - 1) / 2, (h - 1) / 2
        c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
        tile_px = (0.5 * (c * cx - s * cy) + 800.0, 0.5 * (s * cx + c * cy) + 600.0)
        expect = (TILE_ORIGIN[0] + (tile_px[0] + 0.5) * TILE_GSD_M,
                  TILE_ORIGIN[1] - (tile_px[1] + 0.5) * TILE_GSD_M)
        got = g.frame_center_to_world(H, w, h, tile_t)
        self.assertAlmostEqual(got[0], expect[0], places=6)
        self.assertAlmostEqual(got[1], expect[1], places=6)


class UtmTests(unittest.TestCase):
    def test_central_meridian_at_45n(self):
        e, n = g.latlon_to_utm(45.0, 9.0, 32)
        self.assertAlmostEqual(e, g.UTM_FALSE_EASTING, places=6)
        self.assertAlmostEqual(n, g.UTM_K0 * MERIDIAN_ARC_45_M, delta=0.01)

    def test_symmetry_about_central_meridian(self):
        e1, n1 = g.latlon_to_utm(47.3, 9.0 + 2.1, 32)
        e2, n2 = g.latlon_to_utm(47.3, 9.0 - 2.1, 32)
        self.assertAlmostEqual(e1 - g.UTM_FALSE_EASTING, g.UTM_FALSE_EASTING - e2, places=6)
        self.assertAlmostEqual(n1, n2, places=6)

    def test_round_trip_north_and_south(self):
        for lat, lon, zone, south in [(47.37, 8.54, 32, False), (50.45, 30.52, 36, False),
                                      (-33.86, 151.21, 56, True), (64.1, -21.9, 27, False)]:
            e, n = g.latlon_to_utm(lat, lon, zone, south)
            lat2, lon2 = g.utm_to_latlon(e, n, zone, south)
            self.assertLess(g.haversine_m(lat, lon, lat2, lon2), 0.01, (lat, lon))


class HaversineTests(unittest.TestCase):
    def test_one_degree_latitude(self):
        expect = math.radians(1) * g.MEAN_EARTH_RADIUS_M
        self.assertAlmostEqual(g.haversine_m(10.0, 20.0, 11.0, 20.0), expect, places=3)


if __name__ == "__main__":
    unittest.main()
