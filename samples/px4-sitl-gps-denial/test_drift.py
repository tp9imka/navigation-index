import io
import unittest

import drift

LAT0, LON0 = 47.397742, 8.545594
CM = 0.01


class DriftTest(unittest.TestCase):
    def test_latlon_roundtrip(self):
        lat, lon = drift.ne_to_latlon(120.0, -340.0, LAT0, LON0)
        n, e = drift.latlon_to_ne(lat, lon, LAT0, LON0)
        self.assertAlmostEqual(n, 120.0, delta=1e-6)
        self.assertAlmostEqual(e, -340.0, delta=1e-6)

    def test_horizontal_error(self):
        lat, lon = drift.ne_to_latlon(3.0, 4.0, LAT0, LON0)
        self.assertAlmostEqual(drift.horizontal_error_m(lat, lon, LAT0, LON0), 5.0, delta=CM)

    def test_synthetic_drift_profile(self):
        rows = drift.load_rows(io.StringIO(drift.synthetic_csv()))
        summary, tta = drift.summarize(rows)
        self.assertLess(summary["pre-denial"]["max_m"], CM)
        # tau = 19.8 s: north 0.15*19.8 + 0.01*19.8^2 = 6.89 m, east ~ -0.02 m
        self.assertAlmostEqual(summary["gps-denied"]["max_m"], 6.89, delta=CM)
        self.assertLess(summary["recovery"]["mean_m"], summary["gps-denied"]["max_m"])
        self.assertIsNotNone(tta)
        self.assertTrue(10.0 < tta < 20.0)

    def test_missing_truth_is_not_measured(self):
        csv_text = ("t,phase,est_lat,est_lon,true_lat,true_lon\n"
                    f"0,gps-denied,{LAT0},{LON0},,\n"
                    f"1,gps-denied,{LAT0},{LON0},,\n")
        summary, tta = drift.summarize(drift.load_rows(io.StringIO(csv_text)))
        self.assertEqual(summary["gps-denied"]["samples"], 2)
        self.assertEqual(summary["gps-denied"]["measured"], 0)
        self.assertIsNone(summary["gps-denied"]["max_m"])
        self.assertIsNone(tta)
        self.assertIn("not measured", drift.report(summary, tta))


if __name__ == "__main__":
    unittest.main()
