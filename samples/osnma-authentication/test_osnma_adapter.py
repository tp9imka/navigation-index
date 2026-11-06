"""Run: python3 -m unittest -v test_osnma_adapter.py

Adapter and fixture tests are stdlib only. The OSNMAlib integration test runs only when OSNMALIB_PATH
points at an OSNMAlib checkout and its requirements are importable.
"""

import importlib.util
import json
import os
import unittest
from pathlib import Path

from demo_adapter import summarize
from osnma_adapter import (AuthAwareScorer, OsnmaStatus, first_alarm, from_status_entry, run_timeline)
from scorer import Epoch, InterferenceScorer

HERE = Path(__file__).parent
FIXTURE = HERE / "fixtures" / "osnma_results_20min.json"
SVS = (4, 15, 19, 21, 23, 27, 29, 30, 34)
SKY = (47.0, 44.0, 41.0, 38.0, 45.0, 39.0, 42.0, 36.0, 43.0)


def epoch(t, cn0_offset=0.0):
    return Epoch(t=t, cn0={f"E{sv:02d}": c + cn0_offset for sv, c in zip(SVS, SKY)},
                 clk_bias_ns=50.0 * t, clk_drift_ns_s=50.0, lat=52.0, lon=13.0,
                 vel_e=0.0, vel_n=0.0, ref_vel_e=0.0, ref_vel_n=0.0)


def good(t, **kw):
    return OsnmaStatus(t=t, tracked_svs=set(SVS), auth_svs=set(SVS), **kw)


def run(statuses, duration, cn0_offset=0.0):
    return run_timeline(statuses, lambda t: epoch(t, cn0_offset), duration)


class AdapterTests(unittest.TestCase):
    def test_no_status_matches_base_scorer(self):
        base, auth = InterferenceScorer(), AuthAwareScorer()
        for t in range(60):
            a, b = base.assess(epoch(float(t))), auth.assess(epoch(float(t)))
            self.assertEqual((a.spoof_score, a.verdict, a.alarm.active), (b.spoof_score, b.verdict, b.alarm.active))
            self.assertEqual(b.osnma_state, "not-measured")

    def test_clean_authentication_stays_quiet(self):
        res = run([good(30.0 * k) for k in range(10)], 330)
        self.assertIsNone(first_alarm(res))
        self.assertEqual(res[-1].osnma_state, "authenticated 9/9")

    def test_tag_failure_raises_and_latches(self):
        sts = [good(30.0 * k) for k in range(4)] + [good(120.0, tags_fail=3)] + [good(30.0 * k) for k in range(5, 8)]
        res = run(sts, 240)
        alarm = first_alarm(res)
        self.assertIsNotNone(alarm)
        self.assertEqual(alarm.t, 150.0)  # subframe starting at 120 s is known at 150 s
        self.assertIn("osnma_tag_fail", [a.detector for a in alarm.alerts])
        self.assertTrue(all(r.alarm.active for r in res[150:180]))
        # The scorer's own clear policy applies: CLEAR_EPOCHS quiet epochs after a good subframe.
        self.assertFalse(res[-1].alarm.active)
        self.assertIsNotNone(res[-1].alarm.clear_reason)

    def test_key_failure_raises(self):
        res = run([good(0.0), good(30.0, keys_fail=2)], 90)
        self.assertIn("osnma_key_fail", first_alarm(res).alarm.causes)

    def test_absence_before_first_auth_is_not_measured(self):
        sts = [OsnmaStatus(t=30.0 * k, tracked_svs=set(SVS)) for k in range(6)]
        res = run(sts, 200)
        self.assertIsNone(first_alarm(res))
        self.assertTrue(all(r.osnma_state == "not-measured" for r in res))

    def test_auth_drop_after_auth_held(self):
        sts = [good(0.0), good(30.0), OsnmaStatus(t=60.0, tracked_svs=set(SVS), auth_svs={4})]
        alarm = first_alarm(run(sts, 120))
        self.assertIsNotNone(alarm)
        self.assertIn("osnma_auth_drop", [a.detector for a in alarm.alerts])

    def test_auth_drop_with_weak_signals_is_not_spoofing(self):
        sts = [good(0.0), good(30.0), OsnmaStatus(t=60.0, tracked_svs=set(SVS), auth_svs={4})]
        res = run(sts, 120, cn0_offset=-15.0)
        self.assertNotIn("osnma_auth_drop", {a.detector for r in res for a in r.alerts})

    def test_time_offset_bound(self):
        self.assertIsNone(first_alarm(run([good(0.0, clock_offset_s=3.0)], 60)))
        alarm = first_alarm(run([OsnmaStatus(t=0.0, tracked_svs=set(SVS), clock_offset_s=60.0)], 60))
        self.assertIn("osnma_time_offset", [a.detector for a in alarm.alerts])

    def test_stale_status_is_not_measured(self):
        res = run([good(0.0)], 200)
        self.assertEqual(res[-1].osnma_state, "not-measured")

    def test_from_status_entry(self):
        entry = {
            "metadata": {"GST_subframe": [1372, 480240]},
            "nav_data_received": {"4": {}, "15": {}, "19": {}},
            "verified_OSNMA_material": {
                "tags": [{"verification": True}, {"verification": False}],
                "tesla_key": [{"verification": True}]},
            "authenticated_nav_data": {"ADKD0": {
                "4": {"last_gst": [1372, 480210]}, "15": {"last_gst": [1372, 479700]}}},
        }
        st = from_status_entry(entry, t0_gst=1372 * 604800 + 480090)
        self.assertEqual(st.t, 150.0)
        self.assertEqual(st.tracked_svs, {4, 15, 19})
        self.assertEqual(st.auth_svs, {4})  # SV 15 last authenticated 540 s earlier => stale
        self.assertEqual((st.tags_fail, st.keys_fail), (1, 0))


class RecordedScenarioTests(unittest.TestCase):
    """Timelines produced by real OSNMAlib runs (osnma_scenarios.py, 20 min of the bundled recording)."""

    @classmethod
    def setUpClass(cls):
        cls.res = {r["scenario"]: r for r in json.loads(FIXTURE.read_text())}
        cls.out = {k: summarize(v) for k, v in cls.res.items()}

    def test_osnma_blind_cases(self):
        for name in ("clean", "replay_no_clock", "meacon_3s"):
            self.assertIsNone(self.out[name]["first_alarm_s"], name)
            self.assertEqual(self.res[name]["counts"]["tags_failed"], 0)

    def test_detected_cases(self):
        expect = {"replay_60s": "osnma_time_offset", "replay_1h": "osnma_time_offset",
                  "forge_nav": "osnma_tag_fail", "forge_nav_late": "osnma_tag_fail",
                  "forge_keys": "osnma_key_fail", "strip_osnma": "osnma_auth_drop",
                  "time_shift_120s": "osnma_key_fail"}
        for name, det in expect.items():
            self.assertIsNotNone(self.out[name]["first_alarm_s"], name)
            self.assertIn(det, self.out[name]["detectors"], name)

    def test_late_forgery_is_hidden_until_iod_change(self):
        c = self.res["forge_nav_late"]["counts"]
        self.assertEqual(c["words_differ_from_authenticated_stream"], [23])
        self.assertGreaterEqual(self.out["forge_nav_late"]["first_alarm_s"], 900)

    def test_cold_start_without_public_key_never_authenticates(self):
        self.assertIsNone(self.res["cold_start_merkle"]["counts"]["first_auth_s"])
        self.assertEqual(self.out["cold_start_merkle"]["final_state"], "not-measured")


OSNMALIB = os.environ.get("OSNMALIB_PATH")


@unittest.skipUnless(OSNMALIB and importlib.util.find_spec("bitstring"), "set OSNMALIB_PATH and install OSNMAlib requirements")
class OsnmalibIntegrationTests(unittest.TestCase):
    def test_clean_vs_forged_on_real_recording(self):
        from osnma_scenarios import run_isolated
        lib = Path(OSNMALIB).resolve()
        sbf = lib / "custom_run" / "current_config.sbf"
        clean = run_isolated("clean", lib, sbf, "OSNMA_PublicKey_2.xml", 5)
        forged = run_isolated("forge_nav", lib, sbf, "OSNMA_PublicKey_2.xml", 5)
        self.assertGreater(clean["counts"]["tags_authenticated"], 0)
        self.assertEqual(clean["counts"]["tags_failed"], 0)
        self.assertGreater(forged["counts"]["tags_failed"], 0)


if __name__ == "__main__":
    unittest.main()
