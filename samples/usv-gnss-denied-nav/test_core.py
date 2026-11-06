"""Stdlib unit tests: python3 -m unittest test_core"""
import math
import random
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import chart as chartmod
import export
import matcher
import sim
from geo import LocalFrame, closest_on_segment, inv, mm, ray_segment
from nav import Navigator


def box_harbour():
    """A 2 km x 1 km basin open to the south plus a pier: enough geometry for a full fix."""
    segs = []
    pts = [(-1000, -200), (-1000, 800), (1000, 800), (1000, -200)]
    for a, b in zip(pts, pts[1:]):
        segs.append((*a, *b, "coast", "c"))
    segs.append((300, 800, 300, 400, "coast", "pier"))
    return chartmod.Chart(segs)


def straight_coast():
    return chartmod.Chart([(-6000, 500, 6000, 500, "coast", "c")])


def quiet_radar():
    return sim.Radar(clutter_mean=0.0, pd_near=1.0, pd_far=1.0, sigma_bearing_deg=0.01)


class Geometry(unittest.TestCase):
    def test_frame_roundtrip(self):
        f = LocalFrame(55.62, 12.70)
        for lat, lon in ((55.5, 12.5), (55.75, 13.0), (55.62, 12.70)):
            x, y = f.to_xy(lat, lon)
            la, lo = f.to_ll(x, y)
            self.assertAlmostEqual(la, lat, places=9)
            self.assertAlmostEqual(lo, lon, places=9)
        x, y = f.to_xy(55.62 + 0.01, 12.70)
        self.assertAlmostEqual(y, 1113.0, delta=2.0)  # 0.01 deg latitude ~ 1.11 km

    def test_ray_and_segment(self):
        self.assertAlmostEqual(ray_segment(0, 0, 0, 1, -10, 100, 10, 100), 100.0)
        self.assertIsNone(ray_segment(0, 0, 0, -1, -10, 100, 10, 100))
        d2, cx, cy = closest_on_segment(5, 5, 0, 0, 10, 0)
        self.assertEqual((d2, cx, cy), (25.0, 5.0, 0.0))

    def test_inverse(self):
        A = [[4.0, 1.0, 0.5], [1.0, 3.0, 0.2], [0.5, 0.2, 2.0]]
        I = mm(A, inv(A))
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(I[i][j], 1.0 if i == j else 0.0, places=12)


class RadarAndMatching(unittest.TestCase):
    def test_radar_range_to_wall(self):
        ch = straight_coast()
        ret = quiet_radar().scan(ch, [], 0.0, 0.0, 0.0, random.Random(1))
        ahead = [r for r, b, _ in ret if abs(b) < math.radians(0.3)]
        self.assertTrue(ahead)
        self.assertAlmostEqual(ahead[0], 500.0, delta=40.0)

    def test_fix_recovers_offset_with_clutter_and_ship(self):
        ch = box_harbour()
        rng = random.Random(2)
        x, y, psi = 0.0, 200.0, math.radians(10)
        ret = sim.Radar().scan(ch, [("s", 400.0, 300.0, 20.0)], x, y, psi, rng)
        fx = matcher.match(ch, ret, x + 60.0, y - 45.0, psi + math.radians(1.0), 40.0, 7.5)
        self.assertTrue(fx.ok, fx.reason)
        self.assertLess(math.hypot(fx.x - x, fx.y - y), 5.0)
        self.assertLess(abs(math.degrees(fx.psi - psi)), 0.5)

    def test_straight_coast_is_degenerate(self):
        ch = straight_coast()
        ret = quiet_radar().scan(ch, [], 0.0, 0.0, 0.0, random.Random(3))
        fx = matcher.match(ch, ret, 30.0, 0.0, 0.0, 20.0, 7.5)
        self.assertFalse(fx.ok)
        self.assertEqual(fx.reason, "degenerate")

    def test_open_water_has_no_fix(self):
        ch = chartmod.Chart([(20000, 0, 20000, 10, "coast", "far")])
        ret = sim.Radar().scan(ch, [], 0.0, 0.0, 0.0, random.Random(4))
        self.assertEqual(matcher.match(ch, ret, 0, 0, 0, 20, 7.5).reason, "few_returns")


def run_monitor(mode, radar_period, t_end=900, spoof_start=200, radar_until=10 ** 6):
    """Straight run north at 5 m/s with radar fixes every radar_period s (none if 0) until radar_until."""
    rng = random.Random(5)
    nav = Navigator(mode, 0.0, 0.0)
    attack = sim.Attack("spoof", t_start=spoof_start, drag_accel=0.01, drag_rate=1.0)
    errs = []
    for t in range(t_end):
        y_true = 5.0 * t
        if t:
            nav.predict(math.radians(0.5), 5.0, 1.0)
        if radar_period and t % radar_period == 0 and t < radar_until:
            fx = matcher.Fix(True, "ok", 0.0 + rng.gauss(0, 2), y_true + rng.gauss(0, 2), 0.0,
                             cov=[[9.0, 0, 0], [0, 9.0, 0], [0, 0, 1e-6]])
            nav.on_radar(t, fx, math.radians(0.5))
        ox, oy = attack.offset(t)
        nav.on_gnss(t, (ox + rng.gauss(0, 1.5), y_true + oy + rng.gauss(0, 1.5)))
        nav.check(t)
        errs.append(math.hypot(nav.main.x[0], nav.main.x[1] - y_true))
    return nav, errs


class Monitor(unittest.TestCase):
    def test_drag_detected_and_excluded(self):
        nav, errs = run_monitor("monitor", 5)
        ev = [e for e in nav.events if e[1] == "spoof_suspected"]
        self.assertTrue(ev)
        self.assertGreater(ev[0][0], 200)
        self.assertLess(ev[0][0], 300)
        self.assertLess(max(errs), 40.0)
        self.assertLess(errs[-1], 10.0)

    def test_no_monitor_follows_spoofer(self):
        _, errs = run_monitor("gnss_dr", 5)
        self.assertGreater(errs[-1], 500.0)

    def test_no_reference_means_alarm_without_exclusion(self):
        nav, _ = run_monitor("monitor", 5, radar_until=150)
        kinds = {e[1] for e in nav.events}
        self.assertIn("alarm_raised", kinds)
        self.assertNotIn("spoof_suspected", kinds)
        self.assertFalse(nav.excluded)

    def test_clean_run_no_alarm(self):
        nav, errs = run_monitor("monitor", 5, spoof_start=10 ** 6)
        self.assertEqual(nav.events, [])
        self.assertLess(max(errs), 10.0)

    def test_radar_heading_calibrates_compass_bias(self):
        nav, _ = run_monitor("monitor", 5, spoof_start=10 ** 6)
        self.assertAlmostEqual(math.degrees(nav.sub.x[2]), 0.5, delta=0.1)

    def test_drag_profile(self):
        a = sim.Attack("spoof", t_start=100, drag_accel=0.01, drag_rate=1.0, drag_dir_deg=90)
        self.assertEqual(a.offset(99), (0.0, 0.0))
        self.assertAlmostEqual(a.offset(200)[0], 50.0)       # end of ramp: 0.5 a t^2
        self.assertAlmostEqual(a.offset(300)[0], 150.0)      # then 1 m/s


class RealChartAndOutputs(unittest.TestCase):
    def test_route_stays_in_water(self):
        frame, ch, _ = chartmod.chart_and_world(0)
        truth = sim.truth_trajectory()
        for a, b in zip(truth[::10], truth[10::10]):
            L = math.hypot(b.x - a.x, b.y - a.y)
            ux, uy = (b.x - a.x) / L, (b.y - a.y) / L
            for i in ch.near(a.x, a.y, L + 1):
                t = ray_segment(a.x, a.y, ux, uy, *ch.segs[i][:4])
                self.assertFalse(t is not None and t <= L, f"route crosses chart at t={a.t}")
        end = sim.ROUTE_XY[-1]
        self.assertLess(math.hypot(truth[-1].x - end[0], truth[-1].y - end[1]), 10.0)

    def test_cot_is_fused_surface_track(self):
        frame = chartmod.default_frame()
        rows = [{"t": 0.0, "x": 0.0, "y": 0.0, "sigma": 3.0, "excluded": True},
                {"t": 10.0, "x": 50.0, "y": 0.0, "sigma": 3.0, "excluded": True}]
        out = Path(self.id().replace(".", "_") + ".xml")
        try:
            export.write_cot(out, frame, rows)
            lines = out.read_text().splitlines()
            ev = ET.fromstring(lines[0])
            ev2 = ET.fromstring(lines[1])
        finally:
            out.unlink(missing_ok=True)
        self.assertEqual(ev.get("type"), "a-f-S")
        self.assertEqual(ev.get("how"), "m-f")
        self.assertAlmostEqual(float(ev.find("point").get("lat")), 55.62, places=6)
        self.assertIn("excluded", ev.find("detail/remarks").text)
        self.assertAlmostEqual(float(ev2.find("detail/track").get("course")), 90.0)
        self.assertAlmostEqual(float(ev2.find("detail/track").get("speed")), 5.0)


if __name__ == "__main__":
    unittest.main()
