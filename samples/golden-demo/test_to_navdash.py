import json
import tempfile
import unittest
from pathlib import Path

import to_navdash as T
from navapp.geo import enu_to_geodetic

LAT0, LON0 = -35.363261, 149.16523
MISSION = [(400.0, 0.0), (400.0, 150.0), (0.0, 150.0)]


def synthetic_run(mode: str, west_drift_mps: float, alarm_t: float | None) -> list[dict]:
    """Copter flies north at 10 m/s; after onset (t=25) the truth drifts west, the EKF does not."""
    rows = [{"type": "COMPANION_START", "t": None, "mode": mode, "mission_ne": MISSION,
             "spoof": {"onset_s": 25.0, "rate_mps": 1.0, "bearing_deg": 90.0, "max_m": 150.0}},
            {"type": "GPS_GLOBAL_ORIGIN", "t": None, "latitude": int(LAT0 * 1e7),
             "longitude": int(LON0 * 1e7), "altitude": 584000}]
    for i in range(400):
        t = i * 0.1
        drift = west_drift_mps * max(0.0, t - 25.0)
        tl = enu_to_geodetic(-drift, 10 * t, LAT0, LON0)
        el = enu_to_geodetic(0.0, 10 * t, LAT0, LON0)
        rows.append({"type": "SIMSTATE", "t": t, "lat": tl[0] * 1e7, "lng": tl[1] * 1e7})
        rows.append({"type": "GLOBAL_POSITION_INT", "t": t, "lat": el[0] * 1e7, "lon": el[1] * 1e7})
        rows.append({"type": "EKF_STATUS_REPORT", "t": t, "flags": 0x033F, "pos_horiz_variance": 0.1})
        if t >= 25.0:
            rows.append({"type": "COMPANION_SPOOF", "t": t, "offset_m": t - 25.0})
        if i % 10 == 0:
            on = alarm_t is not None and t >= alarm_t
            rows.append({"type": "COMPANION_MONITOR", "t": t, "health": "excluded" if on else "trusted",
                         "alarm": on, "statistic": 60.0 if on else 3.0, "threshold": 52.4,
                         "reason": "test", "lat": el[0], "lon": el[1], "sigma_h": 1.0, "sources": []})
    if alarm_t is not None:
        rows.append({"type": "COMPANION_ACTION", "t": alarm_t, "action": "set_ekf_source_set"})
        rows.append({"type": "COMMAND_ACK", "t": alarm_t + 0.1, "command": 42007, "result": 0})
    return rows


class Geometry(unittest.TestCase):
    def test_cross_track_on_first_leg(self):
        self.assertAlmostEqual(T.path_deviation((-30.0, 200.0), MISSION), 30.0, places=6)

    def test_corner_is_distance_to_nearest_segment(self):
        self.assertAlmostEqual(T.path_deviation((10.0, 410.0), MISSION), 10.0, places=6)

    def test_interp_midpoint_and_out_of_range(self):
        tr = [{"t": 0.0, "lat": 0.0, "lon": 0.0}, {"t": 2.0, "lat": 2.0, "lon": 4.0}]
        self.assertEqual(T.interp(tr, 1.0), (1.0, 2.0))
        self.assertIsNone(T.interp(tr, 3.0))

    def test_decimate_keeps_period(self):
        rows = [{"t": i * 0.1} for i in range(21)]
        self.assertEqual([round(r["t"], 1) for r in T.decimate(rows, 0.5)], [0.0, 0.5, 1.0, 1.5, 2.0])


class Analyse(unittest.TestCase):
    def test_numbers_from_synthetic_runs(self):
        mon = T.analyse(synthetic_run("monitor", 0.0, alarm_t=32.0))
        base = T.analyse(synthetic_run("baseline", 1.0, alarm_t=None))
        self.assertEqual(mon["time_to_detect_s"], 7.0)
        self.assertAlmostEqual(mon["spoof_offset_at_alarm_m"], 7.0, places=0)
        self.assertEqual(mon["max_path_deviation_after_onset_m"], 0.0)
        self.assertIsNone(base["time_to_detect_s"])
        self.assertAlmostEqual(base["max_path_deviation_after_onset_m"], 14.9, places=0)
        self.assertAlmostEqual(base["max_ekf_error_m"], 14.9, places=0)

    def test_convert_writes_navdash_tracks(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            T.convert(synthetic_run("monitor", 0.0, 32.0), synthetic_run("baseline", 1.0, None), out)
            manifest = json.loads((out / "manifest.json").read_text())
            for name in manifest["tracks"]:
                head = json.loads((out / name).read_text().splitlines()[0])["header"]
                self.assertEqual(head["schema"], "navdash/1")
            events = [json.loads(x) for x in (out / "ekf-monitor.jsonl").read_text().splitlines()[1:]]
            kinds = {e.get("event") for e in events}
            self.assertTrue({"spoof_suspected", "source_switched"} <= kinds)


if __name__ == "__main__":
    unittest.main()
