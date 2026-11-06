import io
import math
import unittest

from navapp.filter import DeadReckoningFilter
from navapp.integrity import ChiSquareMonitor, NullMonitor, chi2_sf_even, chi2_threshold_even
from navapp.interfaces import IntegrityMonitor, NavFilter, PoseSource, Publisher
from navapp.pipeline import run
from navapp.publishers import CotPublisher, JsonlPublisher, MavlinkStatusPublisher
from navapp.sim import Scenario, SyntheticSource

MAX_SPOOF_DETECT_S = 15.0


def run_scenario(kind, monitor=None, seed=7):
    sc = Scenario(kind=kind, seed=seed)
    log = JsonlPublisher(io.StringIO())
    recs = run(SyntheticSource(sc), DeadReckoningFilter(), monitor or ChiSquareMonitor(), log=log)
    return sc, recs


def first_alarm_after(recs, onset):
    return next((r["t"] - onset for r in recs if r["t"] >= onset and r["alarm"]), None)


class ProtocolConformance(unittest.TestCase):
    def test_implementations_satisfy_protocols(self):
        self.assertIsInstance(SyntheticSource(Scenario()), PoseSource)
        self.assertIsInstance(DeadReckoningFilter(), NavFilter)
        self.assertIsInstance(ChiSquareMonitor(), IntegrityMonitor)
        self.assertIsInstance(NullMonitor(), IntegrityMonitor)
        self.assertIsInstance(CotPublisher("u", 0, 0), Publisher)
        self.assertIsInstance(MavlinkStatusPublisher(), Publisher)


class ChiSquare(unittest.TestCase):
    def test_two_dof_closed_form(self):
        self.assertAlmostEqual(chi2_threshold_even(1e-3, 2), -2 * math.log(1e-3), places=6)

    def test_threshold_inverts_sf(self):
        for dof in (2, 10, 20):
            x = chi2_threshold_even(1e-4, dof)
            self.assertAlmostEqual(chi2_sf_even(x, dof), 1e-4, places=8)

    def test_rejects_odd_dof(self):
        with self.assertRaises(ValueError):
            chi2_sf_even(1.0, 3)


class Scenarios(unittest.TestCase):
    def test_clean_has_no_alarm_across_seeds(self):
        for seed in range(10):
            _, recs = run_scenario("clean", seed=seed)
            self.assertFalse(any(r["alarm"] for r in recs), f"false alarm with seed {seed}")

    def test_spoof_detected_and_excluded(self):
        sc, recs = run_scenario("spoof")
        ttd = first_alarm_after(recs, sc.attack_onset_s)
        self.assertIsNotNone(ttd)
        self.assertLessEqual(ttd, MAX_SPOOF_DETECT_S)
        self.assertEqual(recs[-1]["health"], "excluded")

    def test_integrity_beats_baseline_under_spoof(self):
        def worst(recs):
            return max(math.hypot(r["east"] - r["truth_east"], r["north"] - r["truth_north"]) for r in recs)
        _, guarded = run_scenario("spoof")
        _, baseline = run_scenario("spoof", NullMonitor())
        self.assertLess(worst(guarded) * 3, worst(baseline))

    def test_jam_raises_alarm_then_recovers(self):
        sc, recs = run_scenario("jam")
        self.assertIsNotNone(first_alarm_after(recs, sc.attack_onset_s))
        self.assertEqual(recs[-1]["health"], "trusted")
        during = [r for r in recs if sc.attack_onset_s <= r["t"] < sc.attack_onset_s + sc.jam_duration_s]
        self.assertTrue(all(r["sources"] == ["dr"] for r in during))
        self.assertGreater(during[-1]["sigma_h"], during[0]["sigma_h"])


if __name__ == "__main__":
    unittest.main()
