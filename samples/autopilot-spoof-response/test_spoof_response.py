"""Tests for the EKF fault-handling sample. Plain python3; pymavlink / matplotlib tests skip without them."""
from __future__ import annotations

import contextlib
import io
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import spoof_analyse as A  # noqa: E402
import spoof_fly as F  # noqa: E402
import spoof_sweep as S  # noqa: E402

try:
    import pymavlink  # noqa: F401
    HAVE_PYMAVLINK = True
except ImportError:
    HAVE_PYMAVLINK = False
try:
    import matplotlib  # noqa: F401
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False

LAT0, LON0 = 41.3018, -81.7514
M_PER_DEG_LAT = A.EARTH_R_M * math.pi / 180


def synthetic_px4_log(reset_at=(10.0, 20.0), rate=3.0, onset=25.0, end=60.0):
    """Position drag east at `rate`; EKF lags the spoof and jumps onto it at `reset_at` (s after onset)."""
    rows = [{"type": "EXPERIMENT", "autopilot": "px4", "config": "default", "params": {"EKF2_GPS_P_GATE": 3.0},
             "spoof": "position", "rate_mps": rate, "step_m": None, "onset_s": onset, "seed": 1, "t": None},
            {"type": "GPS_GLOBAL_ORIGIN", "latitude": int(LAT0 * 1e7), "longitude": int(LON0 * 1e7), "t": None},
            {"type": "PARAM_VALUE", "param_id": "EKF2_GPS_P_GATE", "param_value": 3.0, "param_type": 9, "t": 0.0}]
    m_per_deg_lon = M_PER_DEG_LAT * math.cos(math.radians(LAT0))
    ekf_e, counter = 0.0, 0
    t = 0.0
    while t <= end:
        off = max(0.0, rate * (t - onset))
        if t >= onset and any(abs(t - onset - r) < 1e-6 for r in reset_at):
            ekf_e, counter = off, counter + 1
        n = 10.0 * t
        rows.append({"type": "HIL_STATE_QUATERNION", "t": t, "lat": int((LAT0 + n / M_PER_DEG_LAT) * 1e7),
                     "lon": int(LON0 * 1e7)})
        rows.append({"type": "GLOBAL_POSITION_INT", "t": t, "lat": int((LAT0 + n / M_PER_DEG_LAT) * 1e7),
                     "lon": int((LON0 + ekf_e / m_per_deg_lon) * 1e7)})
        rows.append({"type": "ODOMETRY", "t": t, "reset_counter": counter})
        if t >= onset:
            rows.append({"type": "COMPANION_SPOOF", "t": t, "offset_m": off})
        rejected = t >= onset and off - ekf_e > 5.0
        rows.append({"type": "ESTIMATOR_STATUS", "t": t, "flags": A.PX4_GPS_GLITCH if rejected else 0,
                     "pos_horiz_ratio": 2.0 if rejected else 0.1, "vel_ratio": 0.1})
        t = round(t + 0.1, 3)
    rows.append({"type": "COMPANION_END", "t": end, "outcome": "mission_complete"})
    return rows


class AnalyseTest(unittest.TestCase):
    def test_resets_and_flags(self):
        s = A.summarise(synthetic_px4_log())
        self.assertEqual(s["case"], "px4-default-position-3")
        self.assertEqual([r["t_s"] for r in s["resets"]], [10.0, 20.0])
        self.assertTrue(all(abs(r["jump_east_m"] - 30.0) < 1.5 for r in s["resets"]))
        self.assertEqual([x[0] for x in s["px4_odometry_reset_steps"]], [10.0, 20.0])
        self.assertAlmostEqual(s["first_gps_flag_s"], 1.8, delta=0.2)
        self.assertEqual(len(s["gps_flag_intervals_s"]), 3)
        self.assertEqual(s["params_echoed"], {"EKF2_GPS_P_GATE": 3.0})
        self.assertAlmostEqual(s["spoof_offset_end_m"], 105.0, delta=0.5)

    def test_no_reset_when_ekf_follows(self):
        s = A.summarise(synthetic_px4_log(reset_at=()))
        self.assertEqual(s["reset_count"], 0)
        self.assertLess(s["ekf_err_end_m"], 1.0)

    def test_path_deviation(self):
        self.assertAlmostEqual(A.path_deviation((10.0, 200.0)), 10.0)
        self.assertAlmostEqual(A.path_deviation((75.0, 400.0)), 0.0)

    def test_int_param_echo(self):
        import struct
        raw = struct.unpack("<f", struct.pack("<i", 1))[0]
        got = A.param_echo([{"param_id": "EKF2_GPS_MODE", "param_value": raw, "param_type": 6}], {"EKF2_GPS_MODE"})
        self.assertEqual(got, {"EKF2_GPS_MODE": 1})

    def test_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.raw.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in synthetic_px4_log()))
            out = Path(d) / "s.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(A.main([str(p), "--out", str(out)]), 0)
            self.assertEqual(json.loads(out.read_text())[0]["reset_count"], 2)
            tl = Path(d) / "tl.json"
            A.main([str(p), "--timeline", str(tl)])
            self.assertEqual(len(json.loads(tl.read_text())["t"]), len(json.loads(tl.read_text())["spoof_m"]))


class FlyAndSweepTest(unittest.TestCase):
    def test_step_spoof(self):
        class Base:
            u = (1.0, 0.0)
        sp = F.StepSpoof(25.0, 100.0, 90.0, Base())
        self.assertEqual(sp.offset_m(24.9), 0.0)
        self.assertEqual(sp.offset_en(30.0), (100.0, 0.0))
        self.assertEqual(sp.vel_en(30.0), (0.0, 0.0))

    def test_parse_sets_types(self):
        got = F.parse_sets(["EKF2_GPS_MODE=1", "EKF2_GPS_P_GATE=3", "EK3_POS_I_GATE=300"])
        self.assertIsInstance(got["EKF2_GPS_MODE"], int)
        self.assertIsInstance(got["EKF2_GPS_P_GATE"], float)

    def test_case_matrix(self):
        cases = list(S.all_cases())
        self.assertEqual(len(cases), 9 * 3 + 9 * 2)
        args = S.fly_args("px4", "gates3", "step", 100, "x.jsonl")
        self.assertIn("--step", args)
        self.assertIn("EKF2_GPS_P_GATE=3", args)

    @unittest.skipIf(not HAVE_PYMAVLINK, "needs pymavlink")
    def test_build_both_autopilots(self):
        a, ca, base = F.build(["--autopilot", "px4", "--log", "x.jsonl", "--spoof", "step", "--step", "20"])
        self.assertEqual(ca.spoof, "position")
        self.assertEqual(ca.mode, "baseline")
        a, ca, base = F.build(["--autopilot", "ardupilot", "--log", "x.jsonl", "--rate", "3"])
        self.assertEqual(ca.gps, "inject")
        self.assertEqual(ca.mode, "baseline")


class DataTest(unittest.TestCase):
    def test_committed_summary(self):
        p = HERE / "data" / "sweep_summary.json"
        if not p.exists():
            self.skipTest("no committed sweep")
        rows = json.loads(p.read_text())
        for r in rows:
            for k, v in r["params_requested"].items():
                self.assertAlmostEqual(r["params_echoed"].get(k), v, msg=f"{r['case']} {k} not echoed")
        sample = json.loads((HERE / "sample.json").read_text())
        for k in ("id", "verified", "verified_status", "deps", "first_command"):
            self.assertIn(k, sample)

    @unittest.skipIf(not HAVE_MPL, "needs matplotlib")
    def test_plot_imports(self):
        import spoof_plot  # noqa: F401


if __name__ == "__main__":
    unittest.main()
