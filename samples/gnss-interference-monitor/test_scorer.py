"""Unit tests on synthetic epochs. Run: python3 -m unittest -v test_scorer.py"""

import random
import unittest

from scorer import BASELINE_MIN_EPOCHS, Epoch, InterferenceScorer

# Open-sky C/N0 rises with elevation; a real sky spreads ~15 dB across SVs.
SKY = {"G01": 47.0, "G03": 44.0, "G07": 41.0, "G08": 38.0, "G11": 35.0,
       "G14": 33.0, "G17": 45.0, "G22": 39.0}
LAT0, LON0 = 52.0, 13.0
AGC0 = 3000.0
NOISE_DB = 0.7
DEG_PER_M = 1.0 / 111_320.0


def clean_epoch(t, rng):
    return Epoch(
        t=t,
        cn0={sv: c + rng.gauss(0, NOISE_DB) for sv, c in SKY.items()},
        agc_cnt=AGC0 + rng.gauss(0, 20),
        jam_ind=5,
        clk_bias_ns=1000.0 + 50.0 * t,
        clk_drift_ns_s=50.0,
        lat=LAT0 + 10.0 * t * DEG_PER_M,  # 10 m/s northbound
        lon=LON0,
        spoof_det_state=1,
        jamming_state=1,
    )


def warmed_scorer(rng):
    sc = InterferenceScorer(max_speed_mps=40.0)
    for t in range(BASELINE_MIN_EPOCHS + 5):
        sc.assess(clean_epoch(float(t), rng))
    return sc, float(BASELINE_MIN_EPOCHS + 5)


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)

    def test_clean_sky_stays_clean(self):
        sc, t = warmed_scorer(self.rng)
        for k in range(30):
            a = sc.assess(clean_epoch(t + k, self.rng))
            self.assertEqual(a.verdict, "clean", a.reasons)

    def test_broadband_jamming(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.cn0 = {sv: c - 12.0 for sv, c in ep.cn0.items() if sv not in ("G11", "G14")}
        ep.agc_cnt = AGC0 * 0.5
        a = sc.assess(ep)
        self.assertEqual(a.verdict, "jamming", a.reasons)
        self.assertGreaterEqual(a.jam_score, 0.8)

    def test_jamming_does_not_pollute_baseline(self):
        sc, t = warmed_scorer(self.rng)
        base_before = dict(sc.base_cn0)
        for k in range(20):
            ep = clean_epoch(t + k, self.rng)
            ep.cn0 = {sv: c - 15.0 for sv, c in ep.cn0.items()}
            ep.agc_cnt = AGC0 * 0.4
            sc.assess(ep)
        self.assertEqual(sc.base_cn0, base_before)

    def test_spoofer_uniform_power_clock_and_position_jump(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.cn0 = {sv: 46.0 + self.rng.gauss(0, 0.5) for sv in SKY}
        ep.clk_bias_ns += 25_000.0
        ep.lat += 2_000.0 * DEG_PER_M
        a = sc.assess(ep)
        self.assertEqual(a.verdict, "spoofing", a.reasons)
        self.assertEqual(a.spoof_score, 1.0)

    def test_receiver_flag_alone_raises_spoofing(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.spoof_det_state = 2
        self.assertEqual(sc.assess(ep).verdict, "spoofing")

    def test_uniform_check_needs_enough_svs(self):
        sc = InterferenceScorer()
        ep = Epoch(t=0.0, cn0={"G01": 40.0, "G02": 40.2, "G03": 39.9})
        self.assertEqual(sc.assess(ep).verdict, "clean")

    def test_no_baseline_no_cn0_drop_verdict(self):
        sc = InterferenceScorer()
        ep = clean_epoch(0.0, self.rng)
        ep.cn0 = {sv: c - 15.0 for sv, c in ep.cn0.items()}
        self.assertFalse(sc.baseline_ready)
        self.assertEqual(sc.assess(ep).jam_score, 0.0)

    def test_sparse_epoch_without_optional_fields(self):
        sc = InterferenceScorer()
        a = sc.assess(Epoch(t=0.0))
        self.assertEqual((a.verdict, a.reasons), ("clean", []))


if __name__ == "__main__":
    unittest.main()
