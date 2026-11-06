import math
import unittest

import adapter
import filters
import miluv_io as io
import range_stats as rs
from filters import Centralized, DeadReckoning

ZIGZAG, RANDOM = "default_3_zigzag_0", "default_3_random_0"
HAVE_ZIGZAG, HAVE_RANDOM = io.have_data(ZIGZAG), io.have_data(RANDOM)


def denied_rmse(method, eps, denied):
    e2 = []
    for ep in eps:
        method.step(ep)
        x, _ = method.est(denied)
        e2.append((x[0] - ep.truth[denied][0]) ** 2 + (x[1] - ep.truth[denied][1]) ** 2)
    return math.sqrt(sum(e2) / len(e2))


class TestGeometry(unittest.TestCase):
    def test_multilateration_recovers_point_from_exact_ranges(self):
        anchors = [a[:2] for a in io.anchors_for(ZIGZAG).values()]
        p = (0.7, -1.3)
        obs = [(a, math.dist(a, p)) for a in anchors]
        fix = adapter.multilaterate(obs, (0.0, 0.0))
        self.assertLess(math.dist(fix, p), 1e-4)

    def test_horizontal_projection(self):
        self.assertAlmostEqual(adapter.horizontal(5.0, 3.0), 4.0)
        self.assertIsNone(adapter.horizontal(1.0, 2.0))

    def test_quaternion_rotation(self):
        q = (0.0, 0.0, math.sin(math.pi / 4), math.cos(math.pi / 4))  # +90 deg yaw
        v = io.rotate(q, (1.0, 0.0, 0.5))
        for got, want in zip(v, (0.0, 1.0, 0.5)):
            self.assertAlmostEqual(got, want)

    def test_fault_ramp(self):
        f = adapter.Fault("anchor", 0, 10.0, 0.02)
        self.assertEqual(f.bias(5.0), 0.0)
        self.assertAlmostEqual(f.bias(60.0), 1.0)

    def test_describe_quantiles_and_tails(self):
        d = rs.describe([0.0] * 90 + [2.0] * 10)
        self.assertAlmostEqual(d["median"], 0.0)
        self.assertAlmostEqual(d["gt1.0"], 0.10)
        self.assertAlmostEqual(d["robust_sd"], 0.0)

    def test_indoor_constants_apply_and_restore(self):
        sim_r = filters.R_GNSS
        adapter.apply_indoor()
        self.assertAlmostEqual(filters.R_GNSS, adapter.INDOOR["R_GNSS"])
        adapter.apply_indoor(False)
        self.assertEqual(filters.R_GNSS, sim_r)

    def test_sim_error_model_has_heavy_positive_tail(self):
        v = rs.describe(rs.sim_errors())
        self.assertGreater(v["gt1.0"], 0.10)


@unittest.skipUnless(HAVE_RANDOM, "MILUV data missing: python3 fetch_miluv.py --exp default_3_random_0")
class TestRealRandom(unittest.TestCase):
    def setUp(self):
        adapter.apply_indoor()

    def tearDown(self):
        adapter.apply_indoor(False)

    def test_truth_rederived_from_mocap_matches_devkit(self):
        tracks = {r: io.load_track(RANDOM, r) for r in io.ROBOTS}
        anchors = io.anchors_for(RANDOM)
        diffs = []
        for m in io.load_ranges(RANDOM)[::20]:
            a, b = io.node_position(m.frm, m.t, tracks, anchors), io.node_position(m.to, m.t, tracks, anchors)
            if a and b:
                diffs.append(abs(math.dist(a, b) - m.gt))
        self.assertGreater(len(diffs), 200)
        self.assertLess(sorted(diffs)[len(diffs) // 2], 0.01)

    def test_real_ranges_have_no_multi_metre_tail(self):
        errs = rs.real_errors(RANDOM)
        d = rs.describe(errs[("inter", "air", "cal")])
        self.assertLess(abs(d["median"]), 0.1)
        self.assertLess(d["gt2.0"], 0.01)

    def test_build_epochs(self):
        cfg, init, eps, info = adapter.build(RANDOM, denied=2)
        self.assertEqual(cfg.gnss_agents, (0, 1))
        self.assertGreater(len(eps), 100)
        self.assertTrue(all(2 not in ep.gnss for ep in eps))
        self.assertGreater(info["fixes"], len(eps))
        self.assertTrue(all(len(ep.ranges) <= 3 for ep in eps))

    def test_cooperative_ranging_beats_dead_reckoning_for_denied_drone(self):
        for denied in (0, 2):
            cfg, init, eps, _ = adapter.build(RANDOM, denied=denied, seed=1)
            dr = denied_rmse(DeadReckoning(init, cfg), eps, denied)
            cen = denied_rmse(Centralized(init, cfg, robust=True), eps, denied)
            self.assertLess(cen, 0.8 * dr, f"denied {denied}: central {cen:.3f} vs DR {dr:.3f}")

    def test_synthetic_model_breaks_plain_filter_but_real_ranges_do_not(self):
        cfg, init, eps, _ = adapter.build(RANDOM, denied=2, seed=1, range_source="real")
        real = denied_rmse(Centralized(init, cfg, robust=False), eps, 2)
        cfg, init, eps, _ = adapter.build(RANDOM, denied=2, seed=1, range_source="synthetic")
        syn = denied_rmse(Centralized(init, cfg, robust=False), eps, 2)
        self.assertLess(real, 0.5)
        self.assertGreater(syn, 3 * real)


@unittest.skipUnless(HAVE_ZIGZAG, "MILUV data missing: python3 fetch_miluv.py")
class TestRealFault(unittest.TestCase):
    def setUp(self):
        adapter.apply_indoor()

    def tearDown(self):
        adapter.apply_indoor(False)

    def _run(self, integrity, fault):
        cfg, init, eps, _ = adapter.build(ZIGZAG, denied=2, seed=1, fault=fault)
        m = Centralized(init, cfg, robust=True, integrity=integrity)
        for ep in eps:
            m.step(ep)
        return m.detections

    def test_solution_separation_detects_anchor_fault_and_blames_right_drone(self):
        det = self._run("ss", adapter.Fault("anchor", 0, 120.0, 0.02))
        self.assertTrue(det)
        t, a = det[0]
        self.assertEqual(a, 0)
        self.assertGreater(t, 120.0)
        self.assertLess(t, 200.0)

    def test_no_false_alarm_without_fault(self):
        self.assertEqual(self._run("ss", None), [])

    def test_monitor_off_detects_nothing(self):
        self.assertEqual(self._run("none", adapter.Fault("anchor", 0, 120.0, 0.02)), [])


if __name__ == "__main__":
    unittest.main()
