"""python3 -m unittest test_safety  (stdlib only, no vehicle needed)"""
import json
import os
import tempfile
import unittest

import mav_mcp_server
import nav_health
import safety

HOME = (-35.363261, 149.165230)


def square_fence(half_m=200.0, **kw):
    """Square around HOME built through a throwaway fence's projection."""
    probe = safety.Fence([HOME, (HOME[0] + 0.001, HOME[1]), (HOME[0], HOME[1] + 0.001)])
    poly = [probe.to_latlon(x, y) for x, y in
            [(-half_m, -half_m), (half_m, -half_m), (half_m, half_m), (-half_m, half_m)]]
    return safety.Fence(poly, **kw)


def l_shape_fence():
    """Concave L: the notch is the north-east quadrant (x > 0 and y > 0 is outside)."""
    probe = safety.Fence([HOME, (HOME[0] + 0.001, HOME[1]), (HOME[0], HOME[1] + 0.001)])
    xy = [(-200, -200), (200, -200), (200, 0), (0, 0), (0, 200), (-200, 200)]
    return safety.Fence([probe.to_latlon(x, y) for x, y in xy], margin_m=5), probe


class FenceTests(unittest.TestCase):
    def test_contains_and_margin(self):
        f = square_fence(margin_m=10)
        c = f.to_latlon(0, 0)
        self.assertTrue(f.contains(*c))
        self.assertFalse(f.contains(*f.to_latlon(195, 0)))   # inside but within margin
        self.assertTrue(f.contains(*f.to_latlon(185, 0)))
        self.assertFalse(f.contains(*f.to_latlon(250, 0)))

    def test_altitude_band(self):
        f = square_fence(min_alt_m=5, max_alt_m=60)
        f.check_alt(30)
        for bad in (2, 61, float("nan")):
            with self.assertRaises(safety.SafetyError):
                f.check_alt(bad)

    def test_goto_rejects_outside_target(self):
        f = square_fence()
        with self.assertRaises(safety.SafetyError):
            f.check_goto(*f.to_latlon(500, 0), 20, current=f.to_latlon(0, 0))

    def test_concave_path_crossing_rejected(self):
        f, probe = l_shape_fence()
        a = probe.to_latlon(100, -100)      # south-east arm
        b = probe.to_latlon(-100, 100)      # north-west arm
        via = probe.to_latlon(-100, -100)   # south-west corner, both legs inside
        self.assertTrue(f.contains(*a) and f.contains(*b))
        # endpoints inside, straight leg passes through the notch corner region
        with self.assertRaises(safety.SafetyError):
            f.check_goto(*probe.to_latlon(150, 150), 20, current=a)
        f.check_goto(*via, 20, current=a)
        f.check_goto(*b, 20, current=via)

    def test_concave_leg_through_notch(self):
        f, probe = l_shape_fence()
        a = probe.to_latlon(150, -20)
        b = probe.to_latlon(-20, 150)
        with self.assertRaises(safety.SafetyError):
            f.check_leg(a, b)

    def test_vehicle_outside_only_exits(self):
        f = square_fence()
        with self.assertRaises(safety.SafetyError):
            f.check_goto(*f.to_latlon(0, 0), 20, current=f.to_latlon(400, 0))

    def test_max_leg(self):
        f = square_fence(half_m=2000, max_leg_m=500)
        with self.assertRaises(safety.SafetyError):
            f.check_leg(f.to_latlon(-800, 0), f.to_latlon(800, 0))

    def test_bad_lat_lon(self):
        f = square_fence()
        for lat, lon in ((91, 0), (0, 181), (float("inf"), 0)):
            with self.assertRaises(safety.SafetyError):
                f.check_point(lat, lon)

    def test_mission_checks_every_leg(self):
        f, probe = l_shape_fence()
        wps = [{"lat": la, "lon": lo, "rel_alt_m": 20} for la, lo in
               (probe.to_latlon(100, -100), probe.to_latlon(-100, 100))]
        with self.assertRaises(safety.SafetyError):
            f.check_mission(wps)
        wps.insert(1, dict(zip(("lat", "lon"), probe.to_latlon(-100, -100)), rel_alt_m=20))
        self.assertEqual(f.check_mission(wps)["waypoints"], 3)

    def test_mission_altitude_and_empty(self):
        f = square_fence()
        with self.assertRaises(safety.SafetyError):
            f.check_mission([])
        with self.assertRaises(safety.SafetyError):
            f.check_mission([{"lat": HOME[0], "lon": HOME[1], "rel_alt_m": 500}])


class SurveyTests(unittest.TestCase):
    def test_survey_inside_and_spaced(self):
        f = square_fence(half_m=300, margin_m=10)
        area = [f.to_latlon(x, y) for x, y in [(-100, -50), (100, -50), (100, 50), (-100, 50)]]
        wps = safety.plan_survey(f, area, spacing_m=20, rel_alt_m=25)
        self.assertEqual(len(wps), 20)   # 10 north-south passes x 2 ends
        f.check_mission(wps)
        xs = sorted({round(f.to_xy(w["lat"], w["lon"])[0]) for w in wps})
        self.assertEqual([b - a for a, b in zip(xs, xs[1:])], [20] * 9)

    def test_survey_spacing_floor(self):
        f = square_fence()
        with self.assertRaises(safety.SafetyError):
            safety.plan_survey(f, f.polygon, spacing_m=1, rel_alt_m=20)


class NavHealthTests(unittest.TestCase):
    GOOD_GPS = {"fix_type": 3, "satellites_visible": 10, "eph": 80}

    def ekf(self, flags, var=0.1):
        return {"flags": flags, "velocity_variance": var, "pos_horiz_variance": var,
                "pos_vert_variance": var, "compass_variance": var, "terrain_alt_variance": 0}

    def test_nominal(self):
        r = nav_health.assess(self.ekf(0x3FF & ~0x80 & ~0x400 | 0x10), self.GOOD_GPS)
        self.assertEqual(r["verdict"], "nominal", r)
        self.assertTrue(r["gnss_ok"])

    def test_gps_lost_but_ekf_holding_is_degraded(self):
        r = nav_health.assess(self.ekf(1 | 2 | 4 | 8 | 16 | 32), {"fix_type": 1, "satellites_visible": 0, "eph": 65535})
        self.assertEqual(r["verdict"], "degraded")
        self.assertFalse(r["gnss_ok"])
        self.assertIsNone(r["gps"]["hdop"])

    def test_const_pos_mode_is_lost(self):
        r = nav_health.assess(self.ekf(1 | 128), self.GOOD_GPS)
        self.assertEqual(r["verdict"], "lost")

    def test_variance_and_glitch(self):
        r = nav_health.assess(self.ekf(1 | 2 | 16 | 32768, var=0.85), self.GOOD_GPS)
        self.assertEqual(r["verdict"], "degraded")
        self.assertIn("EKF flags GPS_GLITCHING", r["reasons"])
        self.assertEqual(r["variance_levels"]["pos_horiz_variance"], "bad")

    def test_unknown_without_ekf(self):
        self.assertEqual(nav_health.assess(None, None)["verdict"], "unknown")


class ServerDryRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "log.jsonl")
        here = os.path.dirname(os.path.abspath(__file__))
        fence = safety.Fence.from_json(os.path.join(here, "fence.example.json"))
        self.server = mav_mcp_server.Server("none", fence, dry_run=True, log_path=self.log)

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, name, **args):
        r = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                "params": {"name": name, "arguments": args}})
        res = r["result"]
        return res["isError"], json.loads(res["content"][0]["text"])

    def test_goto_outside_rejected_and_logged(self):
        err, body = self.call("goto", lat=-35.3700, lon=149.1652, rel_alt_m=20)
        self.assertTrue(err)
        self.assertTrue(body["rejected"])
        with open(self.log) as f:
            entry = json.loads(f.readlines()[-1])
        self.assertEqual((entry["tool"], entry["outcome"]), ("goto", "rejected"))

    def test_goto_inside_dry_run(self):
        err, body = self.call("goto", lat=HOME[0], lon=HOME[1] + 0.001, rel_alt_m=20)
        self.assertFalse(err, body)
        self.assertTrue(body["dry_run"])
        self.assertFalse(body["fence_check"]["path_checked"])

    def test_auto_requires_validated_mission(self):
        err, body = self.call("set_mode", mode="AUTO")
        self.assertTrue(err and body["rejected"])
        err, _ = self.call("upload_mission", waypoints=[{"lat": HOME[0], "lon": HOME[1], "rel_alt_m": 20}])
        self.assertFalse(err)
        err, body = self.call("set_mode", mode="AUTO")
        self.assertFalse(err, body)

    def test_mode_allowlist(self):
        err, body = self.call("set_mode", mode="ACRO")
        self.assertTrue(err and body["rejected"])

    def test_takeoff_alt_limit(self):
        err, body = self.call("arm_takeoff", rel_alt_m=120)
        self.assertTrue(err and body["rejected"])

    def test_unknown_tool_is_rpc_error(self):
        r = self.server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                "params": {"name": "disarm_now"}})
        self.assertEqual(r["error"]["code"], mav_mcp_server.INVALID_PARAMS)

    def test_survey_tool_returns_checked_waypoints(self):
        err, body = self.call("plan_survey", spacing_m=40, rel_alt_m=25)
        self.assertFalse(err, body)
        self.assertGreater(len(body["waypoints"]), 4)


if __name__ == "__main__":
    unittest.main()
