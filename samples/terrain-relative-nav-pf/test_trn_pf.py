"""Stdlib tests for the DEM lookup and the terrain-relative particle filter."""

import contextlib
import io
import math
import random
import unittest

import trn_pf
from terrain import Dem, synthetic_dem


def plane_dem(a, b, c, rows=5, cols=5, spacing=10.0, dy=None):
    dy = spacing if dy is None else dy
    heights = [[a * (col * spacing) + b * (r * dy) + c for col in range(cols)] for r in range(rows)]
    return Dem(heights, 0.0, 0.0, spacing, dy)


def quiet_run(*args):
    with contextlib.redirect_stdout(io.StringIO()):
        return trn_pf.run(*args)


class DemTest(unittest.TestCase):
    def test_bilinear_known_answer(self):
        dem = Dem([[0.0, 10.0, 0.0], [20.0, 30.0, 0.0], [0.0, 0.0, 0.0]], 0.0, 0.0, 1.0, 1.0)
        self.assertAlmostEqual(dem.height(0.5, 0.5), 15.0)
        self.assertAlmostEqual(dem.height(0.25, 0.0), 2.5)
        self.assertAlmostEqual(dem.height(0.0, 0.75), 15.0)

    def test_plane_is_reproduced_exactly(self):
        dem = plane_dem(0.3, -0.7, 100.0)
        for x, y in ((3.0, 4.0), (17.5, 22.25), (39.0, 0.5)):
            self.assertAlmostEqual(dem.height(x, y), 0.3 * x - 0.7 * y + 100.0, places=9)

    def test_north_up_negative_dy(self):
        dem = plane_dem(0.0, 1.0, 0.0, dy=-10.0)  # y decreases with row, like a GeoTIFF
        self.assertAlmostEqual(dem.height(5.0, -15.0), -15.0)
        self.assertIsNone(dem.height(5.0, 5.0))

    def test_outside_grid_is_none(self):
        dem = plane_dem(1.0, 1.0, 0.0)
        self.assertIsNone(dem.height(-0.1, 5.0))
        self.assertIsNone(dem.height(5.0, 40.0))  # last row has no row below it
        self.assertIsNotNone(dem.height(39.9, 39.9))

    def test_synthetic_dem_deterministic_and_seed_dependent(self):
        a = synthetic_dem(20, 20, 50.0, 7)
        b = synthetic_dem(20, 20, 50.0, 7)
        c = synthetic_dem(20, 20, 50.0, 8)
        self.assertEqual(a.h, b.h)
        self.assertNotEqual(a.h, c.h)


class ParticleMathTest(unittest.TestCase):
    def setUp(self):
        self.dem = plane_dem(1.0, 0.0, 0.0, rows=10, cols=10)  # height = x

    def test_weights_normalized_and_favor_matching_height(self):
        particles = [[10.0, 10.0, 0, 0], [30.0, 10.0, 0, 0], [50.0, 10.0, 0, 0]]
        w = trn_pf.measurement_update(particles, [1 / 3] * 3, self.dem, 31.0, 5.0)
        self.assertAlmostEqual(sum(w), 1.0, places=12)
        self.assertEqual(max(range(3), key=w.__getitem__), 1)
        self.assertTrue(all(x >= 0 for x in w))

    def test_known_answer_two_particles(self):
        particles = [[20.0, 10.0, 0, 0], [30.0, 10.0, 0, 0]]
        w = trn_pf.measurement_update(particles, [0.5, 0.5], self.dem, 20.0, 10.0)
        # likelihood ratio exp(-0.5 * (10/10)^2)
        ratio = math.exp(-0.5)
        self.assertAlmostEqual(w[0], 1 / (1 + ratio))
        self.assertAlmostEqual(w[1], ratio / (1 + ratio))

    def test_prior_weights_multiply(self):
        particles = [[20.0, 10.0, 0, 0], [20.0, 10.0, 0, 0]]
        w = trn_pf.measurement_update(particles, [0.2, 0.8], self.dem, 20.0, 5.0)
        self.assertAlmostEqual(w[0], 0.2)
        self.assertAlmostEqual(w[1], 0.8)

    def test_off_dem_particle_gets_zero_and_all_off_is_none(self):
        particles = [[20.0, 10.0, 0, 0], [-500.0, 10.0, 0, 0]]
        w = trn_pf.measurement_update(particles, [0.5, 0.5], self.dem, 20.0, 5.0)
        self.assertEqual(w, [1.0, 0.0])
        self.assertIsNone(trn_pf.measurement_update([[-500.0, 0, 0, 0]], [1.0], self.dem, 20.0, 5.0))

    def test_systematic_resample_one_hot(self):
        particles = [[float(i), 0.0, 0.0, 0.0] for i in range(5)]
        out = trn_pf.systematic_resample(random.Random(1), particles, [0, 0, 1.0, 0, 0])
        self.assertEqual([p[0] for p in out], [2.0] * 5)
        out[0][0] = 99.0
        self.assertEqual(out[1][0], 2.0)  # copies, not aliases
        self.assertEqual(particles[2][0], 2.0)

    def test_systematic_resample_counts_match_weights(self):
        n = 1000
        particles = [[0.0, 0, 0, 0], [1.0, 0, 0, 0], [2.0, 0, 0, 0], [3.0, 0, 0, 0]]
        weights = [0.1, 0.2, 0.3, 0.4]
        # contiguous blocks: systematic resampling bounds the count error per contiguous run
        big = [list(p) for p in particles for _ in range(n // 4)]
        big_w = [w / (n // 4) for w in weights for _ in range(n // 4)]
        out = trn_pf.systematic_resample(random.Random(3), big, big_w)
        self.assertEqual(len(out), n)
        for value, w in enumerate(weights):
            count = sum(1 for p in out if p[0] == value)
            self.assertLessEqual(abs(count - w * n), 1)  # systematic: within one copy

    def test_weighted_stats_known_answer(self):
        particles = [[0.0, 0.0], [10.0, 0.0]]
        mx, my, spread = trn_pf.weighted_stats(particles, [0.5, 0.5])
        self.assertEqual((mx, my), (5.0, 0.0))
        self.assertAlmostEqual(spread, 5.0)


class FilterRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rough = quiet_run(7, 2000, 200.0, 1.0)

    def test_default_run_matches_readme(self):
        # README "Observed output", seed 7, 2000 particles
        t, ins_err, pf_err, spread = self.rough["history"][-1]
        self.assertEqual(t, 200.0)
        self.assertAlmostEqual(ins_err, 380.3, places=1)
        self.assertAlmostEqual(pf_err, 13.0, places=1)
        self.assertAlmostEqual(spread, 32.9, places=1)
        self.assertEqual(self.rough["resamples"], 20)
        self.assertAlmostEqual(self.rough["terrain_std_m"], 266.1, places=1)

    def test_terrain_fixes_shrink_error_below_ins(self):
        hist = self.rough["history"]
        first_pf = hist[0][2]
        late_pf = max(h[2] for h in hist[-50:])
        self.assertLess(late_pf, first_pf)
        self.assertLess(late_pf, 0.2 * hist[-1][1])
        self.assertAlmostEqual(sum(self.rough["weights"]), 1.0, places=9)

    def test_ins_error_grows_without_bound(self):
        ins = [h[1] for h in self.rough["history"]]
        self.assertGreater(ins[-1], ins[0] + 150.0)

    def test_flat_terrain_loses_observability(self):
        flat = quiet_run(7, 500, 200.0, 0.02)
        late_flat = sum(h[2] for h in flat["history"][-50:]) / 50
        late_rough = sum(h[2] for h in self.rough["history"][-50:]) / 50
        self.assertGreater(late_flat, 3 * late_rough)
        self.assertLess(flat["terrain_std_m"], 10.0)


if __name__ == "__main__":
    unittest.main()
