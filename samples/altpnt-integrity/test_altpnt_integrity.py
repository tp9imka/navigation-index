import io
import math
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import altpnt_integrity as ai
import mat
import stanford


class TestHelpers(unittest.TestCase):
    def test_q_inv(self):
        self.assertAlmostEqual(ai.q_inv(0.5), 0.0, places=6)
        self.assertAlmostEqual(ai.q_inv(1e-3), 3.0902, places=3)

    def test_lmax2(self):
        self.assertAlmostEqual(mat.lmax2([[4.0, 0.0], [0.0, 1.0]]), 4.0)
        self.assertAlmostEqual(mat.lmax2([[2.0, 1.0], [1.0, 2.0]]), 3.0)

    def test_classify_regions(self):
        al = 50.0
        self.assertEqual(stanford.classify(5, 20, al), "nominal")
        self.assertEqual(stanford.classify(5, 60, al), "unavailable")
        self.assertEqual(stanford.classify(30, 20, al), "MI")
        self.assertEqual(stanford.classify(70, 20, al), "HMI")
        self.assertEqual(stanford.classify(90, 60, al), "unavail_MI")


class TestEkf(unittest.TestCase):
    def test_gate_rejects_far_fix(self):
        P = mat.eye(8)
        f = ai.Ekf([0.0] * 8, P)
        nis, ok = f.update(ai.H_POS, (100.0, 0.0), 2.0, gate=True)
        self.assertFalse(ok)
        self.assertGreater(nis, ai.CHI2_2DOF_999)
        self.assertEqual(f.x[0], 0.0)

    def test_update_shrinks_covariance(self):
        f = ai.Ekf([0.0] * 8, [[100.0 if i == j else 0.0 for j in range(8)] for i in range(8)])
        f.update(ai.H_POS, (1.0, 1.0), 2.0, gate=True)
        self.assertLess(f.P[0][0], 100.0)


class TestScenario(unittest.TestCase):
    SEEDS = (1, 2, 3)

    def _sum(self, sc, seed, mode):
        return ai.summarize(ai.run(sc, seed, mode), sc)

    def test_deterministic(self):
        sc = ai.Scenario()
        a = ai.run(sc, 5, "full")
        b = ai.run(sc, 5, "full")
        self.assertEqual([r["hpe"] for r in a], [r["hpe"] for r in b])

    def test_nominal_is_bounded_and_available(self):
        sc = ai.Scenario(faults=False)
        for seed in self.SEEDS:
            s = self._sum(sc, seed, "full")
            self.assertEqual(s["mi"], 0)
            self.assertEqual(s["availability"], 1.0)
            self.assertEqual(len(s["detections"]), 0, "false alert in a fault-free run")

    def test_full_monitor_has_no_misleading_information(self):
        for sc in (ai.Scenario(), ai.Scenario(magnav=True), ai.Scenario(spoof_rate=0.3)):
            for seed in self.SEEDS:
                s = self._sum(sc, seed, "full")
                self.assertEqual(s["hmi"], 0)
                self.assertEqual(s["regions"]["MI"], 0)
                self.assertEqual(s["missed_hazards"], 0)

    def test_negative_control_shows_misleading_information(self):
        sc = ai.Scenario()
        for seed in self.SEEDS:
            s = self._sum(sc, seed, "none")
            self.assertGreater(s["hmi"], 0)
            self.assertGreater(s["missed_hazards"], 0)

    def test_gate_alone_does_not_stop_spoofing(self):
        sc = ai.Scenario()
        rows = ai.run(sc, 1, "gate")
        spoofed = [r for r in rows if r["gnss_state"] == "spoofed"]
        self.assertTrue(any(r["region"] in ("MI", "HMI") for r in spoofed))

    def test_spoof_is_detected_and_blamed(self):
        sc = ai.Scenario()
        s = self._sum(sc, 1, "full")
        self.assertIsNotNone(s["spoof_detected_after"])
        self.assertLessEqual(s["spoof_detected_after"], 30)
        self.assertIn("gnss", [src for _, src in s["attributions"]])
        self.assertEqual(s["wrong_attributions"], 0)

    def test_three_sources_identify_without_ambiguity(self):
        sc = ai.Scenario(magnav=True)
        rows = ai.run(sc, 1, "full")
        self.assertTrue(any("exclude:gnss" in r["events"] for r in rows))

    def test_single_absolute_source_costs_availability(self):
        alt_only = self._sum(ai.Scenario(gnss=False), 1, "full")
        with_gnss = self._sum(ai.Scenario(), 1, "full")
        self.assertLess(alt_only["availability"], with_gnss["availability"])
        self.assertEqual(alt_only["hmi"], 0)


class TestOutputs(unittest.TestCase):
    def test_csv_svg_ascii(self):
        with tempfile.TemporaryDirectory() as d:
            csv_p, svg_p = os.path.join(d, "o.csv"), os.path.join(d, "s.svg")
            buf = io.StringIO()
            with redirect_stdout(buf):
                ai.main(["--csv", csv_p, "--svg", svg_p])
            with open(csv_p) as fh:
                lines = fh.read().splitlines()
            self.assertEqual(len(lines), 1 + 3 * 600)
            self.assertTrue(lines[0].startswith("mode,t,"))
            with open(svg_p) as fh:
                svg = fh.read()
            self.assertIn("<svg", svg)
            self.assertIn("</svg>", svg)
            out = buf.getvalue()
            self.assertIn("Stanford diagram, mode=full", out)
            self.assertIn("HMI=", out)

    def test_hazard_episode_tta(self):
        rows = [{"t": float(t), "hpe": h, "available": a} for t, h, a in
                [(1, 10, True), (2, 60, True), (3, 70, False), (4, 10, True), (5, 80, True)]]
        eps = ai.hazard_episodes(rows, 50.0)
        self.assertEqual(len(eps), 2)
        self.assertEqual(eps[0]["tta"], 1.0)
        self.assertIsNone(eps[1]["tta"])
        self.assertTrue(math.isfinite(eps[0]["start"]))


if __name__ == "__main__":
    unittest.main()
