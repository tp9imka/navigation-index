"""Unit tests, no SITL. Plain python3: the companion test is skipped without pymavlink."""
import json
import math
import random
import unittest
from pathlib import Path

import fw_core
import to_navdash_fw

HERE = Path(__file__).resolve().parent
try:
    import pymavlink  # noqa: F401
    HAVE_PYMAVLINK = True
except ImportError:
    HAVE_PYMAVLINK = False


class Geometry(unittest.TestCase):
    def test_cross_track_and_along(self):
        pts = [(0.0, 0.0), (0.0, 1000.0), (1000.0, 1000.0)]
        d, along, i = fw_core.cross_track((30.0, 500.0), pts)
        self.assertAlmostEqual(d, 30.0)
        self.assertAlmostEqual(along, 500.0)
        self.assertEqual(i, 0)
        d, along, i = fw_core.cross_track((400.0, 1040.0), pts)
        self.assertAlmostEqual(d, 40.0)
        self.assertAlmostEqual(along, 1400.0)
        self.assertEqual(i, 1)

    def test_route_is_a_long_range_leg(self):
        self.assertTrue(20000 <= fw_core.route_length_m() <= 30000)


class ArduPilotFrame(unittest.TestCase):
    def test_round_trip_with_location_offset_formula(self):
        lat0, lon0 = -35.363261, 149.165230
        n, e = 11000.0, 5000.0
        # Location::offset_latlng: dlat = n / LATLON_TO_M, dlng = e / LATLON_TO_M / cos(lat0 + dlat/2)
        dlat = n / fw_core.LATLON_TO_M
        lat = lat0 + dlat * 1e-7
        lon = lon0 + e / fw_core.LATLON_TO_M / math.cos(math.radians(lat0 + dlat * 1e-7 / 2)) * 1e-7
        got = fw_core.ap_ne_from_ll(lat, lon, lat0, lon0)
        self.assertAlmostEqual(got[0], n, places=6)
        self.assertAlmostEqual(got[1], e, places=6)

    def test_differs_from_wgs84_local_enu_by_tens_of_metres(self):
        from navapp.geo import enu_to_geodetic
        lat, lon = enu_to_geodetic(5000.0, 11000.0, -35.363261, 149.165230)
        n, _ = fw_core.ap_ne_from_ll(lat, lon, -35.363261, 149.165230)
        self.assertTrue(25 < n - 11000.0 < 45)


class SpoofModel(unittest.TestCase):
    def test_coherent_drag_moves_velocity_and_position(self):
        s = fw_core.Spoof("coherent", 100.0, 1.0, 90.0)
        self.assertEqual(s.offset_m(99.0), 0.0)
        e, n = s.offset_en(160.0)
        self.assertAlmostEqual(e, 60.0)
        self.assertAlmostEqual(n, 0.0, places=9)
        self.assertAlmostEqual(s.vel_en(160.0)[0], 1.0)
        self.assertEqual(fw_core.Spoof("position", 100.0, 1.0, 90.0).vel_en(160.0), (0.0, 0.0))


class FixModels(unittest.TestCase):
    @unittest.skipIf(not (fw_core.SAMPLES / "thermal-geolocalization" / "out" / "main_revised.jsonl").exists(),
                     "thermal-geolocalization per-frame results are git-ignored; run its run_eval.py first")
    def test_committed_models_match_the_measured_results(self):
        self.assertEqual(fw_core.derive_fix_models(), fw_core.load_fix_models())

    def test_committed_model_counts(self):
        models = fw_core.load_fix_models()
        self.assertEqual((models["day"]["fixes"], models["day"]["attempts"]), (149, 188))
        self.assertAlmostEqual(models["night"]["availability"], 17 / 111)

    def test_day_model_reproduces_availability_and_median(self):
        m = fw_core.FixModel.from_models(fw_core.load_fix_models(), "day", random.Random(1))
        out = [m.attempt((0.0, 0.0)) for _ in range(20000)]
        got = [math.hypot(*f) for f in out if f is not None]
        self.assertAlmostEqual(len(got) / len(out), 0.7926, delta=0.01)
        self.assertAlmostEqual(sorted(got)[len(got) // 2], 2.6, delta=0.1)

    def test_night_model_draws_from_the_measured_pool(self):
        models = fw_core.load_fix_models()
        m = fw_core.FixModel.from_models(models, "night", random.Random(2))
        got = [math.hypot(f[0] - 10.0, f[1] - 20.0) for f in (m.attempt((10.0, 20.0)) for _ in range(5000)) if f is not None]
        pool = models["night"]["err_pool_m"]
        self.assertTrue(all(min(abs(r - p) for p in pool) < 1e-6 for r in got))
        self.assertAlmostEqual(len(got) / 5000, 17 / 111, delta=0.015)


class Calibration(unittest.TestCase):
    def _fly(self, cal, heading_err, scale_err, wind, use_air):
        rng = random.Random(3)
        for k in range(600):
            psi = math.radians(0 if k < 200 else 90 if k < 400 else 225)
            v_air = (22 * math.sin(psi), 22 * math.cos(psi))
            v_true = (v_air[0] + wind[0], v_air[1] + wind[1]) if use_air else v_air
            raw = fw_core.rotate_scale(v_air if use_air else v_true, heading_err, scale_err)
            g = (v_true[0] + rng.gauss(0, 0.1), v_true[1] + rng.gauss(0, 0.1))
            cal.update(raw, g, 1.0)
        return cal

    def test_vo_heading_and_scale_are_recovered(self):
        cal = self._fly(fw_core.VelocityCalibration(False), 2.0, 0.03, (0, 0), False)
        v = fw_core.rotate_scale((10.0, 15.0), 2.0, 0.03)
        c = cal.correct(v)
        self.assertLess(math.dist(c, (10.0, 15.0)), 0.1)

    def test_airspeed_wind_is_learned_and_frozen(self):
        cal = self._fly(fw_core.VelocityCalibration(True), 2.0, 0.02, (3.0, -4.0), True)
        c = cal.correct(fw_core.rotate_scale((0.0, 22.0), 2.0, 0.02))
        self.assertLess(math.dist(c, (3.0, 18.0)), 0.2)
        cal.frozen = True
        before = list(cal.theta)
        cal.update((0.0, 22.0), (10.0, 10.0), 1.0)
        self.assertEqual(cal.theta, before)


class Reference(unittest.TestCase):
    def test_committed_dashboard_data(self):
        data = HERE / "data"
        if not (data / "manifest.json").exists():
            self.skipTest("no reference run committed")
        man = json.loads((data / "manifest.json").read_text())
        for t in man["tracks"]:
            head = json.loads((data / t).read_text().splitlines()[0])["header"]
            self.assertEqual(head["schema"], "navdash/1")
        summary = json.loads((data / "summary.json").read_text())
        self.assertIn("baseline", summary)
        for s, r in summary.items():
            self.assertIn("xte_max_after_onset_m", r)

    def test_analyse_tiny_log(self):
        o = (-35.0, 149.0)
        from navapp.geo import enu_to_geodetic
        rows = [{"type": "COMPANION_START", "t": None, "t_host": 0, "scenario": "day", "seed": 1, "ref_kind": "vo",
                 "fix_model": "day", "spoof": {"kind": "coherent", "onset_s": 10.0, "rate_mps": 1.0, "bearing_deg": 90},
                 "route_ne": [(1000.0, 0.0)]},
                {"type": "GPS_GLOBAL_ORIGIN", "t": None, "t_host": 0, "latitude": int(o[0] * 1e7), "longitude": int(o[1] * 1e7)}]
        for k in range(0, 50):
            lat, lon = enu_to_geodetic(max(0, k - 10) * 1.0, k * 20.0, *o)
            rows.append({"type": "SIMSTATE", "t": float(k), "t_host": k, "lat": int(lat * 1e7), "lng": int(lon * 1e7)})
            rows.append({"type": "GLOBAL_POSITION_INT", "t": float(k), "t_host": k, "lat": int(lat * 1e7), "lon": int(lon * 1e7)})
        rows.append({"type": "COMPANION_ROUTE_END", "t": 49.0, "t_host": 49, "outcome": "route_complete"})
        s, _ = to_navdash_fw.analyse(rows)
        self.assertAlmostEqual(s["xte_max_after_onset_m"], 39.0, delta=0.2)
        self.assertEqual(s["outcome"], "route_complete")


@unittest.skipIf(not HAVE_PYMAVLINK, "needs pymavlink")
class CompanionArgs(unittest.TestCase):
    def test_parse_defaults(self):
        import companion_fw
        a = companion_fw.parse(["--scenario", "dr", "--log", "x.jsonl"])
        self.assertEqual((a.spoof, a.rate, a.onset), ("coherent", 1.0, 480.0))
        self.assertEqual(companion_fw.SOURCE_SET["dr"], 3)


if __name__ == "__main__":
    unittest.main()
