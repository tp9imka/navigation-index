"""Harness tests. Metric and NMEA tests are stdlib-only; the rest need numpy/scipy and skip without them."""
import math
import unittest

import metrics

try:
    import numpy as np
    from scipy.ndimage import gaussian_filter
    import navs
    import sim
    HAVE_NP = True
except ImportError:
    HAVE_NP = False


class TestMetrics(unittest.TestCase):
    def test_error_at_distances_picks_first_epoch_reaching_checkpoint(self):
        s = [0.0, 4000, 5000, 9000, 10000, 15000]
        e_true = [0.0] * 6
        n_true = list(s)
        e_est = [0, 0, 30, 0, 40, 0.0]
        n_est = list(n_true)
        n_est[4] += 30
        out = metrics.error_at_distances(s, e_true, n_true, e_est, n_est, checkpoints=(5000, 10000, 20000))
        self.assertAlmostEqual(out[0], 30)
        self.assertAlmostEqual(out[1], 50)
        self.assertTrue(math.isnan(out[2]))

    def test_percentile_matches_linear_interpolation(self):
        self.assertAlmostEqual(metrics.percentile([10, 20, 30, 40, 1000], 95), 808.0)
        self.assertAlmostEqual(metrics.percentile([1, 2, 3, 4], 50), 2.5)

    def test_summarize_and_divergence(self):
        s = metrics.summarize([10, 20, 30, 40, float("nan"), 1000])
        self.assertEqual(s["n"], 5)
        self.assertEqual(s["median"], 30)
        self.assertAlmostEqual(s["p95"], 808.0)
        self.assertAlmostEqual(metrics.divergence_rate([100, 600, float("nan"), 499]), 1 / 3)
        self.assertTrue(math.isnan(metrics.summarize([])["median"]))


@unittest.skipIf(not HAVE_NP, "needs numpy + scipy")
class TestSim(unittest.TestCase):
    def test_nmea_roundtrip_and_checksum_rejects_corruption(self):
        t = np.array([0.0, 0.1, 0.2, 3599.9])
        a = np.array([545.4, 546.0, 1200.25, 7.0])
        lines = sim.to_nmea(t, a)
        self.assertTrue(lines[0].startswith("$GPGGA,120000.000,,,,,,,,545.4,M,"))
        tt, aa = sim.parse_nmea(lines)
        self.assertTrue(np.allclose(tt, t, atol=1e-3) and np.allclose(aa, np.round(a, 1)))
        bad = lines[1].replace("546.0", "556.0")
        tt2, _ = sim.parse_nmea([lines[0], bad])
        self.assertEqual(len(tt2), 1)

    def test_footprint_never_longer_than_nadir_and_equal_on_flat_ground(self):
        rng = np.random.default_rng(0)
        res = 30.0
        e = np.full(5, 3000.0)
        n = np.full(5, 3000.0)
        alt = np.full(5, 1500.0)
        rm = sim.RadarModel()
        self.assertTrue(np.allclose(sim.radar_range(np.full((200, 200), 100.0), res, e, n, alt, rm), 1400.0))
        hilly = 100 + 50 * rng.standard_normal((200, 200))
        nadir = alt - navs.bilinear(hilly, e, n, res)
        self.assertTrue(np.all(sim.radar_range(hilly, res, e, n, alt, rm) <= nadir + 1e-9))

    def test_radar_sees_a_ridge_inside_the_beam(self):
        res = 30.0
        dem = np.full((200, 200), 100.0)
        dem[:, 107:111] = 600.0  # ridge 210-300 m east of the aircraft at col 100
        e, n, alt = np.array([3000.0]), np.array([3000.0]), np.array([1500.0])
        r = sim.radar_range(dem, res, e, n, alt, sim.RadarModel(beam_full_deg=40))
        self.assertTrue(900 < r[0] < 960)  # slant to the ridge edge, sqrt(210^2 + 900^2) = 924 m
        narrow = sim.radar_range(dem, res, e, n, alt, sim.RadarModel(beam_full_deg=10))
        self.assertAlmostEqual(narrow[0], 1400.0)

    def test_beam_map_matches_radar_model_on_ridge(self):
        res = 30.0
        dem = np.full((120, 120), 100.0)
        dem[:, 70:73] = 600.0
        bm = navs.beam_map(dem, res, 1500.0, 40.0)
        r = sim.radar_range(dem, res, np.array([60 * res]), np.array([60 * res]), np.array([1500.0]),
                            sim.RadarModel(beam_full_deg=40, rings=40, spokes=64))
        self.assertLess(abs((1500.0 - bm[60, 60]) - r[0]), 15)

    def test_altitude_bias_sign(self):
        dem = np.full((300, 300), 200.0)
        sc = sim.Scenario(radar=sim.RadarModel(footprint=False, noise_m=0, noise_frac=0, dropout_p=0,
                                               burst_p=0, outlier_p=0),
                          altref=sim.AltRefModel(bias_sigma_m=40, drift_sigma_mps=0, wander_sigma_m=0),
                          world=sim.WorldModel(dem_err_sigma_m=0, forest_frac=1e-6))
        old = sim.FLIGHT_LEN_M, sim.EDGE_MARGIN_M
        sim.FLIGHT_LEN_M, sim.EDGE_MARGIN_M = 2000.0, 500.0
        try:
            d = sim.generate(dem, 30.0, sc, 3)
        finally:
            sim.FLIGHT_LEN_M, sim.EDGE_MARGIN_M = old
        self.assertTrue(np.allclose(d["terrain_meas"], 200.0 - d["alt_bias_m"], atol=0.06))


@unittest.skipIf(not HAVE_NP, "needs numpy + scipy")
class TestNavigators(unittest.TestCase):
    def test_dead_reckoning_with_perfect_hints_is_exact(self):
        prior = {"e0": 1000.0, "n0": 2000.0, "pos_sigma_m": 1.0, "heading_deg": 90.0, "speed_mps": 40.0,
                 "flight_msl_m": 1500.0, "t0": 0.0}
        nav = navs.DeadReckonHint(np.zeros((10, 10)), 30.0, prior)
        self.assertTrue(np.allclose(nav.update(10.0, 0.0), [1400.0, 2000.0]))

    def test_tercom_baseline_recovers_offset_on_synthetic_hills(self):
        rng = np.random.default_rng(1)
        dem = gaussian_filter(rng.standard_normal((400, 400)), 6) * 400 + 300
        res = 30.0
        truth_v = np.array([0.0, 40.0])
        prior = {"e0": 6000.0 + 150, "n0": 3000.0 - 120, "pos_sigma_m": 200.0, "heading_deg": 0.0,
                 "speed_mps": 40.0, "flight_msl_m": 1500.0, "t0": 0.0}
        nav = navs.TercomBaseline(dem, res, prior)
        p0 = np.array([6000.0, 3000.0])
        for k in range(1, 1000):
            t = k * 0.1
            p = p0 + truth_v * t
            est = nav.update(t, float(navs.bilinear(dem, p[0], p[1], res)))
        self.assertGreaterEqual(nav.stats["fixes_accepted"], 1)
        self.assertLess(np.linalg.norm(est - p), 40.0)


if __name__ == "__main__":
    unittest.main()
