"""Tests for the anti-spoof config sample. Plain python3; the pymavlink test skips without it."""
from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import resil_analyse as R  # noqa: E402
import resil_fly  # noqa: E402
import resil_sweep as W  # noqa: E402

try:
    import pymavlink  # noqa: F401
    HAVE_PYMAVLINK = True
except ImportError:
    HAVE_PYMAVLINK = False

LAT0, LON0 = 41.3018, -81.7514
M_PER_DEG_LAT = R.A.EARTH_R_M * math.pi / 180
DATA = HERE / "data"


def synthetic_log(spoof="coherent", rate=1.0, switch_at=None, follow=True, onset=25.0, end=78.0, flag_at=None):
    """ArduPilot-shaped log: truth flies north at 5 m/s; spoof drags east; the EKF follows the
    spoof until `switch_at` s after onset (then back on truth) unless follow is False."""
    rows = [{"type": "EXPERIMENT", "autopilot": "ardupilot", "config": "test", "params": {"EK3_SRC_OPTIONS": 1.0},
             "spoof": spoof, "rate_mps": rate if spoof != "none" else None, "step_m": None, "onset_s": onset,
             "seed": 1, "t": None},
            {"type": "GPS_GLOBAL_ORIGIN", "latitude": int(LAT0 * 1e7), "longitude": int(LON0 * 1e7), "t": None},
            {"type": "PARAM_VALUE", "param_id": "EK3_SRC_OPTIONS", "param_value": 1.0, "param_type": 9, "t": 0.0}]
    m_per_deg_lon = M_PER_DEG_LAT * math.cos(math.radians(LAT0))
    t = 0.0
    while t <= end:
        off = max(0.0, rate * (t - onset)) if spoof != "none" else 0.0
        on_spoof = follow and (switch_at is None or t - onset < switch_at)
        ekf_e = off if on_spoof else 0.0
        n = 5.0 * t
        lat = int((LAT0 + n / M_PER_DEG_LAT) * 1e7)
        rows.append({"type": "SIMSTATE", "t": t, "lat": lat, "lng": int(LON0 * 1e7)})
        rows.append({"type": "GLOBAL_POSITION_INT", "t": t, "lat": lat, "lon": int((LON0 + ekf_e / m_per_deg_lon) * 1e7)})
        if t >= onset and spoof != "none":
            rows.append({"type": "COMPANION_SPOOF", "t": t, "offset_m": off})
        flag = flag_at is not None and t - onset >= flag_at
        rows.append({"type": "EKF_STATUS_REPORT", "t": t, "flags": R.A.AP_GPS_GLITCHING if flag else 0,
                     "pos_horiz_variance": 0.1, "velocity_variance": 0.1})
        rows.append({"type": "HEARTBEAT", "t": t, "custom_mode": 3, "autopilot": 3})
        t = round(t + 0.1, 3)
    if switch_at is not None:
        rows.append({"type": "STATUSTEXT", "t": onset + switch_at, "text": R.LUA_SWITCH_TEXT + " pos 2 m vel 0.9 m/s"})
    rows.append({"type": "COMPANION_END", "t": end, "outcome": "mission_complete"})
    return rows


class TestAnalysis(unittest.TestCase):
    def test_switch_caught_early_is_safe(self):
        f = R.summarise(synthetic_log(rate=1.0, switch_at=3.0))
        self.assertEqual(f["switch_s"], 3.0)
        self.assertEqual(f["switch_by"], "lua")
        self.assertEqual(f["reject_s"], 3.0)
        self.assertLess(f["ekf_err_max_m"], 4.0)
        self.assertTrue(f["safe"])

    def test_believed_drag_is_not_safe(self):
        f = R.summarise(synthetic_log(rate=1.0))
        self.assertIsNone(f["switch_s"])
        self.assertIsNone(f["reject_s"])
        self.assertGreater(f["ekf_err_max_m"], 50.0)
        self.assertAlmostEqual(f["capture_ratio_end"], 1.0, delta=0.02)
        self.assertFalse(f["safe"])

    def test_flag_alone_is_not_a_reject(self):
        f = R.summarise(synthetic_log(rate=1.0, flag_at=2.0))
        self.assertEqual(f["first_gps_flag_s"], 2.0)
        self.assertIsNone(f["reject_s"])
        self.assertFalse(f["safe"])

    def test_clean_flight_false_alarm(self):
        ok = R.summarise(synthetic_log(spoof="none"))
        self.assertTrue(ok["clean"])
        self.assertFalse(ok["false_alarm"])
        self.assertTrue(ok["case"].endswith("clean-s1"))
        bad = R.summarise(synthetic_log(spoof="none", switch_at=10.0))
        self.assertTrue(bad["false_alarm"])

    def test_false_alarm_ranks_last(self):
        fl = [R.summarise(synthetic_log(rate=1.0, switch_at=3.0)) | {"config": "jumpy"},
              R.summarise(synthetic_log(spoof="none", switch_at=10.0)) | {"config": "jumpy"},
              R.summarise(synthetic_log(rate=1.0)) | {"config": "quiet"},
              R.summarise(synthetic_log(spoof="none")) | {"config": "quiet"}]
        self.assertEqual([r["config"] for r in R.ranking(fl)], ["quiet", "jumpy"])

    def test_ranking_orders_by_safe_then_false_alarms(self):
        fl = [R.summarise(synthetic_log(rate=1.0, switch_at=3.0)) | {"config": "good"},
              R.summarise(synthetic_log(spoof="none")) | {"config": "good"},
              R.summarise(synthetic_log(rate=1.0)) | {"config": "bad"},
              R.summarise(synthetic_log(spoof="none")) | {"config": "bad"}]
        rows = R.ranking(fl)
        self.assertEqual([r["config"] for r in rows], ["good", "bad"])
        self.assertEqual(rows[0]["rank"], 1)
        self.assertEqual(rows[0]["per_rate"]["1"]["safe"], 1)
        self.assertTrue(rows[0]["params_ok"])


class TestPx4Flags(unittest.TestCase):
    def rows(self):
        # mission starts at sim 50 s, so t = t_sim - 50
        return [{"type": "X", "t": 10.0, "t_sim": 60.0}]

    def test_gnss_off_after_onset(self):
        flags = [{"t_sim": 50.0 + t, "cs_gnss_pos": t < 32.0} for t in range(0, 60, 2)]
        g = R.gnss_status(self.rows(), flags, onset=25.0)
        self.assertEqual(g["gnss_pos_off_s"], 7.0)
        self.assertFalse(g["gnss_off_before_onset"])

    def test_gnss_lost_before_onset(self):
        flags = [{"t_sim": 50.0 + t, "cs_gnss_pos": t < 10.0, "cs_gnss_hgt_fault": t >= 10.0} for t in range(0, 60, 2)]
        g = R.gnss_status(self.rows(), flags, onset=25.0)
        self.assertTrue(g["gnss_off_before_onset"])
        self.assertTrue(g["gnss_hgt_fault_seen"])

    def test_listener_parse(self):
        txt = "TOPIC: estimator_status_flags\n    timestamp: 89068000 (0.2 seconds ago)\n    cs_gnss_pos: False\n    cs_aux_gpos: True\n"
        self.assertEqual(W.parse_listener(txt), {"t_sim": 89.068, "cs_gnss_pos": False, "cs_aux_gpos": True})
        self.assertIsNone(W.parse_listener("nothing"))


class TestConfigs(unittest.TestCase):
    def test_every_config_has_a_file(self):
        for cfg in W.PX4_CONFIGS:
            self.assertTrue(W.config_file("px4", cfg).exists(), cfg)
        for cfg in W.AP_CONFIGS:
            self.assertTrue(W.config_file("ardupilot", cfg).exists(), cfg)

    def test_param_files_parse(self):
        p = resil_fly.read_params(W.config_file("ardupilot", "lua-switch-fuse-all-vel"))
        self.assertEqual(p, {"SCR_ENABLE": "1", "EK3_SRC_OPTIONS": "1"})
        p = resil_fly.read_params(W.config_file("px4", "ev-vel-gpsmode1"))
        self.assertEqual(p, {"EKF2_EV_CTRL": "4", "EKF2_GPS_MODE": "1"})
        self.assertEqual(resil_fly.read_params(W.config_file("px4", "default")), {})

    def test_case_matrix(self):
        cases = list(W.all_cases())
        per_cfg = (len(W.RATES) + 1) * len(W.SEEDS)
        self.assertEqual(len(cases), per_cfg * (len(W.PX4_CONFIGS) + len(W.AP_CONFIGS)))
        self.assertEqual(W.case_name("ardupilot", "lua-switch", "coherent", 0.3, 2), "ardupilot-lua-switch-coherent-0.3-s2")
        self.assertEqual(W.case_name("px4", "default", "none", 0.0, 1), "px4-default-clean-s1")
        args = W.fly_args("ardupilot", "dual-gps-blend", "coherent", 1.0, 1, "x.jsonl", "c.parm")
        self.assertIn("--gps2", args)
        self.assertIn("--monitor", W.fly_args("px4", "companion-monitor", "none", 0.0, 1, "x", "c"))
        self.assertLessEqual(W.AP_PORT0 + 9, W.AP_PORT_MAX)

    def test_lua_applet_constants(self):
        lua = (HERE / "scripts" / "gnss_extnav_switch.lua").read_text()
        self.assertIn("set_posvelyaw_source_set(SET_EXTNAV)", lua)
        self.assertIn(R.LUA_SWITCH_TEXT, lua)
        self.assertIn("local SET_EXTNAV = 1", lua)


@unittest.skipUnless((DATA / "flights.json").exists(), "no committed sweep data")
class TestCommittedData(unittest.TestCase):
    def setUp(self):
        self.flights = json.loads((DATA / "flights.json").read_text())
        self.rank = json.loads((DATA / "ranking.json").read_text())

    def test_params_echoed(self):
        for f in self.flights:
            for k, v in f["params_requested"].items():
                self.assertIn(k, f["params_echoed"], f["case"])
                self.assertAlmostEqual(float(f["params_echoed"][k]), float(v), places=3, msg=f["case"])

    def test_ranking_matches_flights(self):
        for r in self.rank:
            fs = [f for f in self.flights if f["autopilot"] == r["autopilot"] and f["config"] == r["config"]]
            self.assertEqual(r["spoofed_flights"] + r["clean_flights"] + r["incomplete_flights"], len(fs))
            self.assertEqual(r["safe"], sum(f["safe"] for f in fs))


@unittest.skipUnless(HAVE_PYMAVLINK, "pymavlink not installed")
class TestFlyImports(unittest.TestCase):
    def test_dual_gps_subclass_builds(self):
        sys.path.insert(0, str(HERE.parent / "golden-demo"))
        import companion as G
        cls = resil_fly.with_gps2(G.Companion)
        self.assertTrue(issubclass(cls, G.Companion))
        self.assertIn("send_gps_input", cls.__dict__)


if __name__ == "__main__":
    unittest.main()
