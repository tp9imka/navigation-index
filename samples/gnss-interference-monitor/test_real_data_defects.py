"""Regression tests for the four defects the Jammertest 2024 replay (samples/real-attack-replay) found in
the previous scorer, on small synthetic fixtures. Against scorer.py at commit dae8229 the defect tests
fail (driving, position pull, velocity jump, step drop after recovery, C/N0 and AGC staircase, spoofed
ephemeris); the guards for the new mechanisms (static-noise soak, spoofer power not learned, stale
baseline clears, matching ephemeris) pass on both. Stdlib only.
Run: python3 -m unittest -v test_real_data_defects.py"""

import math
import random
import unittest

from ephemeris_check import EphemerisChecker
from scorer import BASELINE_MIN_EPOCHS, EPH_MISMATCH_M, Epoch, InterferenceScorer
from test_ephemeris_check import EPH, encode_sfrbx, shifted

LAT0, LON0 = 69.28, 16.0
M_PER_DEG_LAT = 111_320.0
M_PER_DEG_LON = M_PER_DEG_LAT * math.cos(math.radians(LAT0))
SKY = {"G02": 46.0, "G05": 41.0, "G12": 44.0, "G15": 37.0, "G24": 43.0,
       "E07": 39.0, "E11": 45.0, "R03": 40.0, "R12": 36.0, "C20": 42.0}


def drive(n, rng, pos_noise_m=0.3, vel_noise_mps=0.05):
    """Stop-go car route: accelerate at 2 m/s^2 to 20 m/s, cruise, 90 deg turns at 0.15 rad/s,
    brake at 3 m/s^2, stand 20 s; repeated. Yields (t, east, north, ve, vn) with filtered-fix noise."""
    e = nrt = 0.0
    heading, speed = 0.0, 0.0
    phase_t, phase = 0.0, "stand"
    turned = 0.0
    out = []
    for k in range(n):
        if phase == "stand" and phase_t >= 20:
            phase, phase_t = "accel", 0.0
        elif phase == "accel" and speed >= 20.0:
            phase, phase_t = "cruise", 0.0
        elif phase == "cruise" and phase_t >= 30:
            phase, phase_t, turned = "turn", 0.0, 0.0
        elif phase == "turn" and turned >= math.pi / 2:
            phase, phase_t = "cruise2", 0.0
        elif phase == "cruise2" and phase_t >= 20:
            phase, phase_t = "brake", 0.0
        elif phase == "brake" and speed <= 0.0:
            phase, phase_t, speed = "stand", 0.0, 0.0
        acc = {"accel": 2.0, "brake": -3.0}.get(phase, 0.0)
        yaw = 0.15 if phase == "turn" else 0.0
        v0, h0 = speed, heading
        speed = max(0.0, speed + acc)
        heading += yaw
        turned += yaw
        vm, hm = 0.5 * (v0 + speed), 0.5 * (h0 + heading)
        e += vm * math.sin(hm)
        nrt += vm * math.cos(hm)
        phase_t += 1.0
        out.append((float(k), e + rng.gauss(0, pos_noise_m), nrt + rng.gauss(0, pos_noise_m),
                    speed * math.sin(heading) + rng.gauss(0, vel_noise_mps),
                    speed * math.cos(heading) + rng.gauss(0, vel_noise_mps)))
    return out


def drive_epoch(t, e, n, ve, vn, rng, cn0_offset=0.0):
    return Epoch(t=t, lat=LAT0 + n / M_PER_DEG_LAT, lon=LON0 + e / M_PER_DEG_LON, fix_ok=True, hdop=0.6,
                 vel_e=ve, vel_n=vn, cn0={sv: c + cn0_offset + rng.gauss(0, 0.7) for sv, c in SKY.items()})


def static_epoch(t, rng, cn0_offset=0.0, agc=None):
    return Epoch(t=t, lat=LAT0 + rng.gauss(0, 0.5) / M_PER_DEG_LAT, lon=LON0 + rng.gauss(0, 0.5) / M_PER_DEG_LON,
                 fix_ok=True, hdop=0.6, vel_e=rng.gauss(0, 0.03), vel_n=rng.gauss(0, 0.03), agc_cnt=agc,
                 cn0={sv: c + cn0_offset + rng.gauss(0, 0.7) for sv, c in SKY.items()})


def alerting(results):
    return [a for a in results if a.verdict != "clean"]


class Defect1DrivingIsNotDrift(unittest.TestCase):
    """Old: the constant-velocity prior raised pos_drift on 86% of real driving and 98% of the quiet slot."""

    def test_stop_go_and_turns_stay_clean(self):
        rng = random.Random(1)
        sc = InterferenceScorer(max_speed_mps=70.0)
        res = [sc.assess(drive_epoch(*row, rng)) for row in drive(900, rng)]
        self.assertEqual([(a.t, a.verdict) for a in alerting(res)], [])

    def test_position_pull_the_velocity_does_not_show_is_caught(self):
        rng = random.Random(2)
        sc = InterferenceScorer(max_speed_mps=70.0)
        rows = drive(400, rng)
        res = []
        for k, (t, e, n, ve, vn) in enumerate(rows):
            if k >= 300:
                e += 1.5 * (k - 300)  # fix pulled east at 1.5 m/s, reported velocity unchanged
            res.append(sc.assess(drive_epoch(t, e, n, ve, vn, rng)))
        hit = next((a.t for a in res if any(x.detector == "pos_drift" for x in a.alerts)), None)
        self.assertIsNotNone(hit)
        self.assertLessEqual(hit - 300, 20)
        self.assertEqual(alerting(res[:300]), [])


    def test_static_noise_hour_stays_clean(self):
        # iid 2 m fixes, 0.3 m/s velocity: the 10 s windows overlap, so each residual counts as 1/10 of a sample
        for seed in range(3):
            rng = random.Random(seed)
            sc = InterferenceScorer()
            for t in range(3600):
                ep = Epoch(t=float(t), lat=LAT0 + rng.gauss(0, 2) / M_PER_DEG_LAT,
                           lon=LON0 + rng.gauss(0, 2) / M_PER_DEG_LON, fix_ok=True,
                           vel_e=rng.gauss(0, 0.3), vel_n=rng.gauss(0, 0.3))
                self.assertEqual(sc.assess(ep).verdict, "clean", (seed, t))

    def test_velocity_jump_beyond_platform_limit(self):
        rng = random.Random(7)
        sc = InterferenceScorer(max_speed_mps=70.0)
        rows = drive(120, rng)
        res = []
        for k, (t, e, n, ve, vn) in enumerate(rows):
            if k == 100:
                ve += 25.0  # a takeover that steps the reported velocity
            res.append(sc.assess(drive_epoch(t, e, n, ve, vn, rng)))
        self.assertEqual([a.t for a in res if any(x.detector == "vel_jump" for x in a.alerts)], [100.0, 101.0])


class Defect2BaselineRecoversAfterRise(unittest.TestCase):
    """Old: a cn0_rise sub-alert (0.3) sat between the learning gate (0.2) and the alert (0.5), so after a
    slow decline and recovery the baseline never learned again and a later step drop was compared with a
    stale low baseline and missed (2.6.1b, 2.4.12, 0.3.1e on the real logs)."""

    def test_step_drop_after_decline_and_recovery_is_detected(self):
        rng = random.Random(3)
        sc = InterferenceScorer()
        t = 0
        for _ in range(60):
            sc.assess(static_epoch(float(t), rng))
            t += 1
        for k in range(300):  # -0.05 dB/s to -15 dB: too slow for any step test, the baseline follows
            sc.assess(static_epoch(float(t), rng, cn0_offset=-0.05 * k))
            t += 1
        for _ in range(120):  # back to the open sky in one step
            sc.assess(static_epoch(float(t), rng))
            t += 1
        drop_t = t
        res = [sc.assess(static_epoch(float(t + k), rng, cn0_offset=-12.0)) for k in range(30)]
        first = next((a.t for a in res if "jamming" in a.verdict), None)
        self.assertIsNotNone(first)
        self.assertLessEqual(first - drop_t, 5)


    def test_stale_baseline_after_jamming_lets_alarm_clear(self):
        # the sky settles 2 dB lower after a jamming episode (moving platform); the frozen baseline may drift
        # at a bounded rate, so the alarm clears instead of holding for good
        rng = random.Random(8)
        sc = InterferenceScorer()
        t = 0
        for _ in range(60):
            sc.assess(static_epoch(float(t), rng))
            t += 1
        for _ in range(60):
            sc.assess(static_epoch(float(t), rng, cn0_offset=-15.0))
            t += 1
        res = [sc.assess(static_epoch(float(t + k), rng, cn0_offset=-2.0)) for k in range(900)]
        self.assertTrue(res[0].alarm.active)
        self.assertFalse(res[-1].alarm.active)


    def test_spoofer_power_not_learned(self):
        # rise-aware learning must not absorb a spoofer: its departure would then read as jamming
        rng = random.Random(9)
        sc = InterferenceScorer()
        for t in range(60):
            sc.assess(static_epoch(float(t), rng))
        for k in range(40):
            ep = static_epoch(60.0 + k, rng)
            ep.cn0 = {sv: 48.0 + rng.gauss(0, 0.4) for sv in SKY}
            ep.spoof_det_state = 2
            self.assertIn("spoofing", sc.assess(ep).verdict)
        res = [sc.assess(static_epoch(100.0 + k, rng)) for k in range(30)]
        self.assertEqual([a.verdict for a in res if a.verdict != "clean"], [])


class Defect3StaircasePower(unittest.TestCase):
    """Old: 2.4.3 lowered C/N0 in steps of 2-6 dB; each step stayed under the 6 dB / 75 % rule and the EWMA
    baseline followed, so nothing fired."""

    def test_cn0_staircase_is_detected(self):
        rng = random.Random(4)
        sc = InterferenceScorer()
        for t in range(60):
            self.assertEqual(sc.assess(static_epoch(float(t), rng)).verdict, "clean")
        res = []
        for k in range(120):  # -3 dB every 15 s
            res.append(sc.assess(static_epoch(60.0 + k, rng, cn0_offset=-3.0 * (k // 15 + 1))))
        hits = [a for a in res if any(x.detector == "cn0_step" for x in a.alerts)]
        self.assertTrue(hits)
        self.assertLessEqual(hits[0].t - 60, 30)
        self.assertNotIn("cn0_drop", {x.detector for x in res[0].alerts})  # the per-SV rule alone stays silent at -3 dB

    def test_agc_staircase_accumulates(self):
        rng = random.Random(5)
        sc = InterferenceScorer()
        agc0 = 3000.0
        for t in range(60):
            sc.assess(static_epoch(float(t), rng, agc=agc0 * (1 + rng.gauss(0, 0.01))))
        res = [sc.assess(static_epoch(60.0 + k, rng, agc=agc0 * (1 - 0.06 * (k // 15 + 1))))
               for k in range(45)]  # -6 % per step, each under the 20 % agc_change rule for the first 3 steps
        self.assertTrue(any(x.detector == "agc_step" for a in res for x in a.alerts))
        self.assertFalse(any(x.detector == "agc_change" for a in res[:15] for x in a.alerts))


class Defect4SpooferEphemeris(unittest.TestCase):
    """Old: nothing compared the navigation data the receiver decoded with an independent source; on the
    real logs the spoofers' ephemerides (IODE 2/3, km off) ended up in the logged nav file."""

    def run_checker(self, broadcast_eph, reference_eph, n=30):
        rng = random.Random(6)
        chk = EphemerisChecker({"G05": [reference_eph]})
        t0 = 1726125465.0  # 2024-09-12 07:17:45 UTC, within the fixture ephemeris' validity
        for p in encode_sfrbx(broadcast_eph, sv=5):
            chk.feed_sfrbx(p, t0)
        sc = InterferenceScorer()
        out = []
        for k in range(n):
            ep = static_epoch(t0 + k, rng)
            ep.eph_mismatch_m = chk.mismatch_m(ep.t)
            out.append(sc.assess(ep))
        return out

    def test_spoofed_ephemeris_raises_spoofing(self):
        res = self.run_checker(shifted(EPH, m0=EPH["m0"] + 0.01), EPH)
        late = res[BASELINE_MIN_EPOCHS:]
        self.assertTrue(all("spoofing" in a.verdict for a in late))
        x = next(x for x in late[0].alerts if x.detector == "eph_mismatch")
        self.assertGreater(x.value, EPH_MISMATCH_M)
        self.assertEqual(x.evidence["svs"], ["G05"])

    def test_matching_ephemeris_stays_clean(self):
        self.assertEqual(alerting(self.run_checker(EPH, EPH)), [])


if __name__ == "__main__":
    unittest.main()
