"""PX4 port pieces without SITL: row normalisation, PX4 summary fields, comparison, mode encoding.
The converter tests are stdlib only; companion tests need pymavlink and skip without it."""
import json
import tempfile
import unittest
from pathlib import Path

import to_navdash_px4 as P
from to_navdash_px4 import T

try:
    import companion_px4 as C
except ImportError:  # companion_px4 imports pymavlink
    C = None

LAT0, LON0 = 41.3018, -81.751397
MISSION = [(400.0, 0.0), (400.0, 150.0), (0.0, 150.0)]


def synthetic_run(mode: str, drift_mps: float, alarm_t: float | None) -> list[dict]:
    """Truth flies north at 10 m/s and drifts west after onset (t=25); EKF2 does not see it."""
    rows = [{"type": "COMPANION_START", "t": None, "mode": mode, "mission_ne": MISSION, "gps": "inject",
             "vgeo": {"mode": "replay"}, "detector": "ss+vel",
             "spoof": {"kind": "coherent", "onset_s": 25.0, "rate_mps": 1.0, "bearing_deg": 90.0, "max_m": 150.0}},
            {"type": "GPS_GLOBAL_ORIGIN", "t": None, "latitude": int(LAT0 * 1e7),
             "longitude": int(LON0 * 1e7), "altitude": 290000}]
    for i in range(400):
        t = i * 0.1
        d = drift_mps * max(0.0, t - 25.0)
        tl = T.enu_to_geodetic(-d, 10 * t, LAT0, LON0)
        el = T.enu_to_geodetic(0.0, 10 * t, LAT0, LON0)
        rows.append({"type": "HIL_STATE_QUATERNION", "t": t, "lat": int(tl[0] * 1e7), "lon": int(tl[1] * 1e7)})
        rows.append({"type": "GLOBAL_POSITION_INT", "t": t, "lat": el[0] * 1e7, "lon": el[1] * 1e7})
        if i % 5 == 0:
            rows.append({"type": "ESTIMATOR_STATUS", "t": t, "flags": 16 | (1024 if 30 < t < 31 else 0),
                         "pos_horiz_ratio": 1.5 if t > 35 else 0.2, "pos_horiz_accuracy": 0.8})
        if t >= 25.0:
            rows.append({"type": "COMPANION_SPOOF", "t": t, "offset_m": t - 25.0})
    if alarm_t is not None:
        rows.append({"type": "COMPANION_DETECT", "t": alarm_t, "detector": "vel", "events": []})
        rows.append({"type": "COMPANION_ACTION", "t": alarm_t, "action": "set_ekf_source_set", "reason": "vel"})
        rows.append({"type": "COMPANION_PX4_ACTION", "t": alarm_t, "params": {"EKF2_GPS_CTRL": 0, "EKF2_EV_CTRL": 5}})
        rows.append({"type": "PARAM_VALUE", "t": alarm_t + 0.05, "param_id": "EKF2_GPS_CTRL", "param_value": 0.0, "param_type": 6})
    return sorted(rows, key=lambda r: -1 if r["t"] is None else r["t"])


class ConverterTests(unittest.TestCase):
    def test_px4_fields_replace_ardupilot_fields(self):
        s = P.analyse(P.normalise(synthetic_run("monitor", 0.0, 28.0)))
        self.assertEqual(s["time_to_detect_s"], 3.0)
        self.assertEqual(s["gps_ctrl_echo"]["value"], 0.0)
        self.assertEqual(s["px4_action_params"], {"EKF2_GPS_CTRL": 0, "EKF2_EV_CTRL": 5})
        self.assertEqual(s["ekf_gps_glitch_reports"], 1)
        self.assertGreater(s["ekf_pos_horiz_ratio_over_1_after_onset"], 0)
        for k in P.ARDUPILOT_ONLY:
            self.assertNotIn(k, s)

    def test_truth_from_hil_state_measures_deviation(self):
        s = P.analyse(P.normalise(synthetic_run("baseline", 1.0, None)))
        self.assertIsNone(s["alarm_t_s"])
        self.assertAlmostEqual(s["max_path_deviation_after_onset_m"], 14.9, delta=0.2)
        self.assertGreater(s["max_ekf_error_m"], 14.0)

    def test_convert_writes_dashboard_set_and_compare(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            s = P.convert(synthetic_run("monitor", 0.0, 28.0), synthetic_run("baseline", 1.0, None), out)
            manifest = json.loads((out / "manifest.json").read_text())
            for name in manifest["tracks"]:
                head = json.loads((out / name).read_text().splitlines()[0])["header"]
                self.assertEqual(head["schema"], "navdash/1")
            ev = [json.loads(x) for x in (out / "ekf-monitor.jsonl").read_text().splitlines()[1:]]
            sw = [e for e in ev if e.get("event") == "source_switched"]
            self.assertIn("EKF2_GPS_CTRL=0", sw[0]["text"])
            c = P.compare(s, s)
            self.assertEqual(c["time_to_detect_s"]["px4_monitor"], 3.0)
            self.assertIsNone(c["time_to_detect_s"]["ardupilot_baseline"])


@unittest.skipIf(C is None, "requires pymavlink")
class CompanionTests(unittest.TestCase):
    def test_px4_custom_mode_encoding(self):
        self.assertEqual(C.px4_mode("MISSION"), (4 << 16) | (4 << 24))
        self.assertEqual(C.px4_mode("TAKEOFF"), (4 << 16) | (2 << 24))

    def test_int_params_go_bytewise(self):
        self.assertEqual(C.float_as_int(C.int_as_float(7)), 7)
        self.assertEqual(P.param_value({"param_type": 6, "param_value": C.int_as_float(5)}), 5)

    def test_parse_fixes_v2_settings(self):
        a = C.parse(["--mode", "baseline", "--log", "x.jsonl"])
        self.assertEqual((a.gps, a.extnav, a.spoof, a.vgeo, a.detector), ("inject", "reference", "coherent", "replay", "ss+vel"))


if __name__ == "__main__":
    unittest.main()
