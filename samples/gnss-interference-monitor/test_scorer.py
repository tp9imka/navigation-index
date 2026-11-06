"""Unit tests on synthetic epochs. Run: python3 -m unittest -v test_scorer.py"""

import random
import unittest

from scorer import (BASELINE_MIN_EPOCHS, CLEAR_EPOCHS, CN0_FROZEN_ALPHA, CN0_INNOV_CLIP_DB, Epoch,
                    InterferenceScorer)

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
        n = 20
        for k in range(n):
            ep = clean_epoch(t + k, self.rng)
            ep.cn0 = {sv: c - 15.0 for sv, c in ep.cn0.items()}
            ep.agc_cnt = AGC0 * 0.4
            sc.assess(ep)
        # only the bounded frozen-baseline drift (CN0_FROZEN_ALPHA x clipped innovation) is allowed
        bound = n * CN0_FROZEN_ALPHA * CN0_INNOV_CLIP_DB + 1e-9
        for sv, b in base_before.items():
            self.assertLessEqual(b - sc.base_cn0[sv], bound, sv)
            self.assertLess(b - sc.base_cn0[sv], 0.5)

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



POS_NOISE_M = 2.0
VEL_NOISE_MPS = 0.3
CLK_NOISE_NS = 5.0
DRAG_ACCEL = 0.5  # m/s^2, the gnss-signal-chain dragoff value
WARMUP = BASELINE_MIN_EPOCHS + 20


def nav_epoch(t, rng, north_m=0.0, east_m=0.0, vn=0.0, ve=0.0, ref=None, clk_extra_ns=0.0, with_vel=True):
    """Navigation-only epoch around (LAT0, LON0); position noise, Doppler velocity (unless with_vel=False,
    a receiver that reports none), clock without reported drift."""
    lat = LAT0 + (north_m + rng.gauss(0, POS_NOISE_M)) * DEG_PER_M
    lon = LON0 + (east_m + rng.gauss(0, POS_NOISE_M)) * DEG_PER_M / 0.6157  # cos(52 deg)
    vel_n, vel_e = vn + rng.gauss(0, VEL_NOISE_MPS), ve + rng.gauss(0, VEL_NOISE_MPS)
    ep = Epoch(t=t, lat=lat, lon=lon, fix_ok=True,
               vel_n=vel_n if with_vel else None, vel_e=vel_e if with_vel else None,
               clk_bias_ns=1000.0 + 50.0 * t + clk_extra_ns + rng.gauss(0, CLK_NOISE_NS))
    if ref is not None:
        ep.ref_vel_n, ep.ref_vel_e = ref
    return ep


def run(sc, epochs):
    return [sc.assess(ep) for ep in epochs]


def first_hit(results, detector):
    return next((a.t for a in results if any(x.detector == detector for x in a.alerts)), None)


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(7)

    def drag(self, ref, n=60, accel=DRAG_ACCEL, with_vel=True):
        sc = InterferenceScorer()
        run(sc, [nav_epoch(float(t), self.rng, ref=ref, with_vel=with_vel) for t in range(WARMUP)])
        out = []
        for k in range(n):
            d = 0.5 * accel * k * k
            out.append(sc.assess(nav_epoch(float(WARMUP + k), self.rng, east_m=d, ve=accel * k, ref=ref,
                                           with_vel=with_vel)))
        return out

    def test_very_slow_drag_external_reference(self):
        # 0.02 m/s^2: the residual grows slower than a learned noise estimate could follow it
        res = self.drag(ref=(0.0, 0.0), n=120, accel=0.02)
        t = next((a.t for a in res if a.verdict != "clean"), None)
        self.assertIsNotNone(t)
        self.assertLessEqual(t - WARMUP, 60)

    def test_slow_drag_cv_prior(self):
        res = self.drag(ref=None, with_vel=False)
        t = first_hit(res, "pos_drift")
        self.assertIsNotNone(t)
        self.assertLessEqual(t - WARMUP, 15)
        self.assertFalse(any(x.detector in ("position_jump", "clock_jump") for a in res for x in a.alerts))

    def test_slow_drag_external_reference_faster(self):
        cv = first_hit(self.drag(ref=None, with_vel=False), "pos_drift")
        self.rng = random.Random(7)
        res = self.drag(ref=(0.0, 0.0))
        ext = min(first_hit(res, "pos_drift"), first_hit(res, "vel_mismatch"))
        self.assertLess(ext, cv)

    def test_coherent_drag_invisible_to_doppler_reference(self):
        # documented limit: position and Doppler moved together look like real motion without an external reference
        res = self.drag(ref=None, with_vel=True)
        self.assertIsNone(first_hit(res, "pos_drift"))

    def test_alarm_has_no_silent_epochs_during_drag(self):
        res = self.drag(ref=None, with_vel=False)
        start = next(i for i, a in enumerate(res) if a.alarm.active)
        self.assertTrue(all(a.alarm.active for a in res[start:]))
        self.assertIn("pos_drift", res[-1].alarm.causes)

    def test_static_clean_no_alerts(self):
        for ref in (None, (0.0, 0.0)):
            sc = InterferenceScorer()
            res = run(sc, [nav_epoch(float(t), self.rng, ref=ref) for t in range(400)])
            self.assertEqual([a.t for a in res if a.verdict != "clean"], [], ref)

    def test_constant_velocity_motion_not_a_drift(self):
        sc = InterferenceScorer()
        res = run(sc, [nav_epoch(float(t), self.rng, north_m=15.0 * t, vn=15.0) for t in range(200)])
        self.assertEqual([a.verdict for a in res if a.verdict != "clean"], [])

    def test_maneuver_with_matching_reference_not_a_drift(self):
        sc = InterferenceScorer()
        eps = [nav_epoch(float(t), self.rng, ref=(0.0, 0.0)) for t in range(WARMUP)]
        for k in range(60):  # real acceleration, seen by GNSS and by the reference alike
            eps.append(nav_epoch(float(WARMUP + k), self.rng, east_m=0.5 * DRAG_ACCEL * k * k,
                                 ve=DRAG_ACCEL * k, ref=(0.0, DRAG_ACCEL * k)))
        res = run(sc, eps)
        self.assertEqual([a.t for a in res if a.verdict != "clean"], [])

    def test_velocity_mismatch(self):
        sc = InterferenceScorer()
        run(sc, [nav_epoch(float(t), self.rng, ref=(0.0, 0.0)) for t in range(WARMUP)])
        res = run(sc, [nav_epoch(float(WARMUP + k), self.rng, ve=2.0, ref=(0.0, 0.0)) for k in range(10)])
        self.assertIsNotNone(first_hit(res, "vel_mismatch"))

    def test_no_velocity_check_without_reference(self):
        sc = InterferenceScorer()
        run(sc, [nav_epoch(float(t), self.rng) for t in range(WARMUP)])
        res = run(sc, [nav_epoch(float(WARMUP + k), self.rng, ve=2.0) for k in range(10)])
        self.assertIsNone(first_hit(res, "vel_mismatch"))

    def test_clock_time_drag(self):
        sc = InterferenceScorer()
        run(sc, [nav_epoch(float(t), self.rng) for t in range(WARMUP)])
        # +20 ns/s extra (6 m/s of pseudorange ramp) is far below the 1000 ns jump test
        res = run(sc, [nav_epoch(float(WARMUP + k), self.rng, clk_extra_ns=20.0 * k) for k in range(30)])
        t = first_hit(res, "clock_drift")
        self.assertIsNotNone(t)
        self.assertLessEqual(t - WARMUP, 10)
        self.assertIsNone(first_hit(res, "clock_jump"))
        a = next(a for a in res if a.t == t)
        ev = next(x for x in a.alerts if x.detector == "clock_drift").evidence
        self.assertAlmostEqual(ev["expected_ns_s"], 50.0, delta=5.0)

    def test_steady_oscillator_drift_learned_not_alerted(self):
        sc = InterferenceScorer()
        res = run(sc, [nav_epoch(float(t), self.rng, clk_extra_ns=0.002 * t * t) for t in range(300)])
        self.assertIsNone(first_hit(res, "clock_drift"))

    def test_reported_drift_change(self):
        sc, t = warmed_scorer(self.rng)
        for k in range(10):
            ep = clean_epoch(t + k, self.rng)
            ep.clk_drift_ns_s = 50.0 + self.rng.gauss(0, 1.0)
            sc.assess(ep)
        res = []
        for k in range(10, 20):
            ep = clean_epoch(t + k, self.rng)
            ep.clk_drift_ns_s = 90.0
            ep.clk_bias_ns = 1000.0 + 50.0 * (t + 10) + 90.0 * (t + k - (t + 10))
            res.append(sc.assess(ep))
        self.assertIsNotNone(first_hit(res, "clock_drift"))


class LostFixAndAlarmTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(3)

    def test_lost_fix_after_fix(self):
        sc, t = warmed_scorer(self.rng)
        a = sc.assess(Epoch(t=t, fix_ok=False, cn0={}))
        self.assertIn("lost-fix", a.verdict)
        ev = next(x for x in a.alerts if x.detector == "lost_fix")
        self.assertEqual((ev.family, ev.unit), ("lost-fix", "s"))
        self.assertEqual(ev.evidence["last_fix_t"], t - 1)
        a = sc.assess(Epoch(t=t + 5, fix_ok=False, cn0=None))
        self.assertEqual(a.alerts[-1].evidence["since_last_fix_s"], 6.0)
        self.assertIsNone(a.alerts[-1].evidence["n_sv_tracked"])

    def test_no_lost_fix_while_still_acquiring(self):
        sc = InterferenceScorer()
        for k in range(20):
            self.assertEqual(sc.assess(Epoch(t=float(k), fix_ok=False)).verdict, "clean")

    def test_telemetry_gap_counts_as_lost_fix(self):
        sc, t = warmed_scorer(self.rng)
        a = sc.assess(clean_epoch(t + 10, self.rng))
        self.assertIn("lost-fix", a.verdict)

    def test_fix_ok_false_overrides_stale_position(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.fix_ok = False
        self.assertIn("lost-fix", sc.assess(ep).verdict)

    def test_latched_alarm_and_clear(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.spoof_det_state = 2
        first = sc.assess(ep)
        self.assertTrue(first.alarm.active)
        self.assertEqual(first.alarm.causes, {"rx_spoof_flag": t})
        states = [sc.assess(clean_epoch(t + 1 + k, self.rng)) for k in range(CLEAR_EPOCHS)]
        self.assertEqual(CLEAR_EPOCHS, 10)
        self.assertTrue(all(a.verdict == "clean" for a in states))
        self.assertTrue(all(a.alarm.active for a in states[:-1]))
        self.assertFalse(states[-1].alarm.active)
        self.assertIn("epochs with scores", states[-1].alarm.clear_reason)

    def test_alarm_stays_while_fix_is_lost(self):
        sc, t = warmed_scorer(self.rng)
        res = [sc.assess(Epoch(t=t + k, fix_ok=False)) for k in range(3 * CLEAR_EPOCHS)]
        self.assertTrue(all(a.alarm.active for a in res))

    def test_baseline_frozen_by_power_evidence_not_by_other_alarms(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.spoof_det_state = 2
        sc.assess(ep)
        n = sc.clean_epochs
        a = sc.assess(clean_epoch(t + 1, self.rng))
        self.assertTrue(a.alarm.active)
        self.assertEqual(sc.clean_epochs, n + 1)  # a spoofing-flag alarm does not stale the C/N0 baseline
        ep = clean_epoch(t + 2, self.rng)
        ep.cn0 = {sv: c - 15.0 for sv, c in ep.cn0.items()}
        sc.assess(ep)
        self.assertEqual(sc.clean_epochs, n + 1)  # jamming evidence does

    def test_acknowledge_clears_and_reanchors(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.lat += 5000 * DEG_PER_M
        sc.assess(ep)
        self.assertTrue(sc.alarm.active)
        sc.acknowledge(t + 1)
        self.assertFalse(sc.alarm.active)
        self.assertEqual(sc.alarm.clear_reason, "acknowledged")
        self.assertIsNone(sc.pos.pos)

    def test_every_alert_explains_itself(self):
        sc, t = warmed_scorer(self.rng)
        ep = clean_epoch(t, self.rng)
        ep.cn0 = {sv: 46.0 + self.rng.gauss(0, 0.5) for sv in SKY}
        ep.clk_bias_ns += 25_000.0
        ep.lat += 2_000.0 * DEG_PER_M
        ep.agc_cnt = AGC0 * 2
        a = sc.assess(ep)
        self.assertGreaterEqual(len(a.alerts), 5)
        for x in a.alerts:
            self.assertIn(x.family, ("jamming", "spoofing", "lost-fix"))
            self.assertTrue(x.message and x.detector)
            self.assertIsInstance(x.value, float)
        self.assertEqual(a.reasons, [x.message for x in a.alerts])


if __name__ == "__main__":
    unittest.main()
