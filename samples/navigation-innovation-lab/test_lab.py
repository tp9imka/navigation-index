import math
import unittest
from unittest.mock import patch

import adaptation as a
import benchmark as b
import disambiguation as d
import scheduling as s
import replay_vpair as v


class LocalizationContracts(unittest.TestCase):
    def test_equal_predictions_cannot_create_known_mode_certainty(self):
        p = [0.95 / 3] * 3 + [0.05]
        for _ in range(50):
            p = d.posterior(p, [1, 1, 1], 1)
        self.assertAlmostEqual(p[0], p[1])
        self.assertLessEqual(max(p[:3]), 1 / 3 + 1e-12)

    def test_unknown_evidence_rejected_without_numerical_underflow(self):
        p = d.posterior([0.95 / 3] * 3 + [0.05], [-1, 0, 1], 100)
        self.assertEqual(p[-1], 1)
        self.assertAlmostEqual(sum(p), 1)

    def test_information_gain_zero_when_candidates_indistinguishable(self):
        self.assertAlmostEqual(d.information_gain([1 / 3] * 3 + [0], [2, 2, 2]), 0)
        self.assertGreater(d.information_gain([1 / 3] * 3 + [0], [-2, 0, 2]), 0.5)

    def test_all_candidate_geometry_enforced(self):
        self.assertNotIn((0, 1), d.safe_actions(1, 1))
        self.assertIn((0, 1), d.safe_actions(4, 1))

    def test_ambiguous_world_abstains(self):
        for policy in d.POLICIES:
            result = d.run(1000, "indistinguishable", policy)
            self.assertEqual(result["false_accept"], 0)
            self.assertEqual(result["abstain"], 1)


class AsynchronousFixContracts(unittest.TestCase):
    def test_delayed_fix_does_not_erase_post_capture_noise(self):
        error, variance = s.fuse_delayed(5, 3, 2, 1, 0)
        gain = 1 / (1 + s.R)
        self.assertAlmostEqual(error, 5 - gain * 2)
        self.assertAlmostEqual(variance, 3 - gain)
        self.assertGreater(variance, 2)

    def test_busy_or_exhausted_cannot_request(self):
        for policy in s.POLICIES:
            self.assertFalse(s.decision(policy, 40, 100, 100, True, 10, 2, 1)[0])
            self.assertFalse(s.decision(policy, 40, 100, 100, False, 0, 2, 1)[0])

    def test_shared_budget_and_finite_completion(self):
        for policy in s.POLICIES:
            r = s.run(1000, "slow_compute", policy, 1)
            self.assertLessEqual(r["requests"], s.BUDGET)
            self.assertLessEqual(r["delivered"], r["requests"])
            self.assertLessEqual(r["duration"], 120)


class IdentificationContracts(unittest.TestCase):
    def test_exact_identifiable_linear_model(self):
        k, c = a.fit_window([(v, -0.7 * v + 1.1) for v in range(12)], 0.3)
        self.assertAlmostEqual(k, 0.7)
        self.assertAlmostEqual(c, 1.1)

    def test_constant_velocity_cannot_identify_slope(self):
        self.assertIsNone(a.fit_window([(5, -2)] * 24, 0.1))

    def test_wind_bias_gauge_ambiguity(self):
        # Different (wind,bias) pairs yield identical acceleration observations.
        k, wind, bias, shift = 0.7, 2, 0.1, 3
        for v in range(10):
            self.assertAlmostEqual(-k * (v - wind) + bias,
                                   -k * (v - (wind + shift)) + bias - k * shift)

    def test_selective_does_not_adapt_without_reference(self):
        tr = a.run(1001, "reference_outage", "selective", trace=True)["trace"]
        for previous, current in zip(tr, tr[1:]):
            if not current["reference_available"]:
                self.assertEqual((previous["k"], previous["c"]), (current["k"], current["c"]))


class EvaluationContracts(unittest.TestCase):
    def test_paired_interval_direction_and_pairing(self):
        r = b.paired_interval([3, 4, 5], [1, 2, 3], 100)
        self.assertEqual((r["mean"], r["low"], r["high"]), (2, 2, 2))
        with self.assertRaises(ValueError):
            b.paired_interval([1], [1, 2])

    def test_deterministic_all_models(self):
        for module in (a, d, s):
            for scenario in module.SCENARIOS:
                r = module.run(1000, scenario, module.POLICIES[0])
                self.assertEqual(r, module.run(1000, scenario, module.POLICIES[0]))
                self.assertTrue(all(math.isfinite(v) for v in r.values()))


class RecordedReplayContracts(unittest.TestCase):
    def test_calibration_rejects_evaluation_truth(self):
        with self.assertRaises(ValueError):
            v.calibrate({}, {10: (0, 0)})

    def test_pivoted_solver_and_singular_rejection(self):
        self.assertEqual(v.solve([[0, 2], [1, 0]], [6, 4]), [4, 3])
        with self.assertRaises(ValueError):
            v.solve([[1, 1], [1, 1]], [1, 1])

    def test_future_fix_changes_cannot_rewrite_past_estimates(self):
        vo = {k: (float(k), 0.0) for k in range(10, 40)}
        def service_one(frontend, coefficients, frame, stride):
            return (frame + 1.0, 0), 0.1
        def service_two(frontend, coefficients, frame, stride):
            return (frame + (1.0 if frame < 25 else 15.0), 0), 0.1
        with patch.object(v, "cached_fix", service_one):
            a = v.replay({}, [], vo, "periodic", 1, 2, 4)
        with patch.object(v, "cached_fix", service_two):
            b = v.replay({}, [], vo, "periodic", 1, 2, 4)
        self.assertEqual(a["trace"][:17], b["trace"][:17])
        self.assertNotEqual(a["trace"][-1], b["trace"][-1])

    def test_fix_does_not_arrive_before_its_frame(self):
        vo = {k: (float(k), 0.0) for k in range(10, 20)}
        with patch.object(v, "cached_fix", return_value=((12.0, 0), 0.1)):
            r = v.replay({}, [], vo, "periodic", 1, 3, 4)
        self.assertEqual([x["accepted_total"] for x in r["trace"][:3]], [0, 0, 0])
        self.assertEqual(r["trace"][3]["accepted_total"], 1)

    def test_vo_only_never_reads_expensive_match_outcomes(self):
        vo = {k: (float(k), 0.0) for k in range(10, 20)}
        with patch.object(v, "cached_fix", side_effect=AssertionError("unrequested measurement")):
            r = v.replay({}, [], vo, "vo_only", 1, 2, 4)
        self.assertEqual(r["requests"], 0)
        self.assertEqual([x["estimate"] for x in r["trace"]], [list(vo[k]) for k in vo])


if __name__ == "__main__":
    unittest.main()
