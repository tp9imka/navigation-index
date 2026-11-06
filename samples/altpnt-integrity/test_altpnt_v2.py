import json
import math
import os
import random
import unittest

import altpnt_integrity as v1
import altpnt_v2 as v
import calibration as cal

SIBLINGS = all(os.path.isdir(cal.rel(s)) for s in (cal.RELNAV, cal.GEOLOC, cal.TRN, cal.GOLDEN))


class TestCalibration(unittest.TestCase):
    @unittest.skipUnless(SIBLINGS, "sibling sample results not present")
    def test_committed_calibration_matches_sources(self):
        with open(cal.OUT) as fh:
            committed = json.load(fh)
        self.assertEqual(committed, json.loads(json.dumps(cal.build())))

    def test_overbound_covers_gaussian_and_absorbs_bias(self):
        rng = random.Random(3)
        xs = [rng.gauss(0, 2.0) for _ in range(2000)]
        s, _ = cal.gaussian_overbound(xs)
        self.assertGreater(s, 1.9)
        self.assertLess(s, 2.6)
        biased, _ = cal.gaussian_overbound([x + 3.0 for x in xs])
        self.assertGreater(biased, s + 1.0)
        b, core = cal.paired_overbound([x + 3.0 for x in xs])
        self.assertAlmostEqual(b, 3.0, delta=0.2)
        self.assertLess(core, 2.6)

    def test_zero_failure_bound(self):
        self.assertAlmostEqual(cal.zero_failure_upper(296), 0.01007, places=4)
        self.assertAlmostEqual(cal.zero_failure_upper(300) * 300, 3.0, delta=0.05)

    def test_measured_numbers(self):
        c = v.load_cal()
        self.assertAlmostEqual(c["relative"]["models"]["openvins-uzhfpv"]["fit_whole_run"]["yaw_err_deg"], 3.585, places=2)
        self.assertEqual(c["geoloc"]["golden_table"]["fixes"], 246)
        self.assertEqual(c["geoloc"]["wrong_fix"]["wrong_fixes"], 0)
        self.assertAlmostEqual(c["trn"]["sigma_per_axis_over_spread_div_sqrt2"]["hilly"], 1.07, places=2)


class TestEkf2(unittest.TestCase):
    def test_vio_jacobian_matches_finite_difference(self):
        cfg = v.ladder()["L3"]
        x = [0, 0, 25.0, 10.0, 0, 0, 0.02, 0.05]
        f = v.Ekf2(x, [[1.0 if i == j else 0.0 for j in range(8)] for i in range(8)], cfg)
        h, H = f._vio_model()
        for j in (2, 3, 6, 7):
            g = v.Ekf2(x, f.P, cfg)
            g.x[j] += 1e-6
            h2, _ = g._vio_model()
            for i in range(2):
                self.assertAlmostEqual((h2[i] - h[i]) / 1e-6, H[i][j], places=3)

    def test_heading_state_learns_bias_from_fixes(self):
        w = v.worlds()["measured"]
        sc = v.scenario(w, faults=False)
        data = v.simulate(sc, 2, w)
        rows = v.run_v2(sc, 2, v.ladder()["L3"], data=data)
        truth = data[1][-1]["vio_truth_yaw"]
        self.assertLess(abs(rows[-1]["psi_est"] - truth), math.radians(1.0))


class TestWorlds(unittest.TestCase):
    def test_assumed_world_is_v1(self):
        w = v.worlds()["assumed"]
        sc = v.scenario(w)
        a = v.simulate(sc, 4, w)
        b = v1.simulate(sc, 4)
        self.assertEqual(a[1][100]["vgeo"], b[1][100]["vgeo"])

    def test_measured_world_statistics(self):
        w = v.worlds()["measured"]
        sc = v.scenario(w, faults=False, duration=3000)
        _, eps = v.simulate(sc, 1, w)
        slots = [e for e in eps if int(e["t"]) % v1.VGEO_PERIOD == 0]
        avail = sum(e["vgeo"] is not None for e in slots) / len(slots)
        self.assertAlmostEqual(avail, w.vgeo_avail, delta=0.12)
        self.assertGreater(max(abs(e["vio_truth_yaw"]) for e in eps), math.radians(2.0))


class TestHeadline(unittest.TestCase):
    """The calibration lesson in two assertions, seed 1."""

    def test_v1_filter_misleads_in_measured_world(self):
        w = v.worlds()["measured"]
        sc = v.scenario(w)
        rows = v1.run(sc, 1, "full", data=v.simulate(sc, 1, w))
        self.assertGreater(v.metrics(rows, sc, 50.0)["mi"], 100)

    def test_v2_filter_bounds_measured_world(self):
        w = v.worlds()["measured"]
        sc = v.scenario(w)
        rows = v.run_v2(sc, 1, v.ladder()["L2"], data=v.simulate(sc, 1, w))
        m = v.metrics(rows, sc, 50.0)
        self.assertEqual(m["mi"], 0)
        self.assertEqual(m["hmi"], 0)
        self.assertLess(m["avail"], 0.4)


if __name__ == "__main__":
    unittest.main()
