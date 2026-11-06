"""Tests: inline synthetic NCLT-format fixtures always run; real-data tests skip without data/."""
import math
import os
import random
import shutil
import tempfile
import unittest

import nclt_io
import ugv_loop as u

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "2013-01-10")
HAVE_DATA = os.path.exists(os.path.join(DATA, "groundtruth.csv")) and os.path.exists(os.path.join(DATA, "kvh.csv"))

T0_US = 1_357_847_000_000_000
LAT0, LON0 = 0.7381679, -1.4609865
FRAME_OFFSET = (50.0, -20.0)  # truth frame origin vs the first RTK fix
SPEED = 1.5


def yaw_rate(t):
    return 0.15 if 30.0 <= t < 40.0 else (-0.1 if 70.0 <= t < 85.0 else 0.0)


def write_fixture(folder, duration=120.0, gps_noise=0.0, seed=1):
    """A Segway-like run in the NCLT CSV layouts: 1.5 m/s with two turns, perfect sensors."""
    rng = random.Random(seed)
    dt = 0.01
    n = e = psi = 0.0
    rows = {k: [] for k in ("gt", "gps", "rtk", "imu", "eul", "wh", "kvh")}
    for k in range(int(duration / dt) + 1):
        t = k * dt
        us = T0_US + int(round(t * 1e6))
        w = yaw_rate(t)
        tn, te = n + FRAME_OFFSET[0], e + FRAME_OFFSET[1]
        rows["gt"].append(f"{us},{tn},{te},0,0,0,{psi}")
        if k % 2 == 0:
            rows["imu"].append(f"{us},0,0,0,0,{SPEED * w},-9.81,0,0,{w}")
            rows["eul"].append(f"{us},0,0,0")
            rows["kvh"].append(f"{us},{-psi}")
        if k % 4 == 0:
            rows["wh"].append(f"{us},{SPEED},{SPEED}")
        if k % 20 == 0:
            lat = LAT0 + n / nclt_io.EARTH_R
            lon = LON0 + e / (nclt_io.EARTH_R * math.cos(LAT0))
            rows["rtk"].append(f"{us},3,0,{lat},{lon},270,0,0")
            gn, ge = rng.gauss(0, gps_noise), rng.gauss(0, gps_noise)
            rows["gps"].append(f"{us},3,0,{lat + gn / nclt_io.EARTH_R},"
                               f"{lon + ge / (nclt_io.EARTH_R * math.cos(LAT0))},270,0,0")
        n += SPEED * math.cos(psi) * dt
        e += SPEED * math.sin(psi) * dt
        psi += w * dt
    names = {"gt": "groundtruth.csv", "gps": "gps.csv", "rtk": "gps_rtk.csv", "imu": "ms25.csv",
             "eul": "ms25_euler.csv", "wh": "wheels.csv", "kvh": "kvh.csv"}
    for key, name in names.items():
        with open(os.path.join(folder, name), "w") as f:
            f.write("\n".join(rows[key]) + "\n")


class FixtureCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        write_fixture(cls.dir, gps_noise=1.0)
        cls.s = nclt_io.Session(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def test_rigid_fit_recovers_transform(self):
        th, tn, te = math.radians(3.0), 10.0, -4.0
        src = [(0, 0), (10, 0), (0, 25), (-7, 3)]
        dst = [(math.cos(th) * x - math.sin(th) * y + tn, math.sin(th) * x + math.cos(th) * y + te) for x, y in src]
        got = nclt_io.fit_rigid_2d(src, dst)
        for a, b in zip(got, (th, tn, te)):
            self.assertAlmostEqual(a, b, places=6)

    def test_session_alignment_on_fixture(self):
        self.assertLess(max(self.s.align_residuals), 0.05)
        self.assertAlmostEqual(self.s.frame.tn, FRAME_OFFSET[0], delta=0.05)
        self.assertEqual(len(u.decimate(self.s.gps)), 121)

    def test_level_accel_removes_gravity_under_pitch(self):
        pitch = math.radians(10.0)
        f_body = (9.81 * math.sin(pitch), 0.0, -9.81 * math.cos(pitch))
        fx, fy = u.level_accel(f_body, 0.0, pitch)
        self.assertAlmostEqual(fx, 0.0, places=9)
        self.assertAlmostEqual(fy, 0.0, places=9)

    def test_odometry_dead_reckoning_is_tight_with_perfect_sensors(self):
        d = tempfile.mkdtemp()
        try:
            write_fixture(d, gps_noise=0.0)
            s = nclt_io.Session(d)
        finally:
            shutil.rmtree(d)
        for cfg in ("odo-mems", "odo-fog"):
            ev = u.build_events(s, cfg)
            r = u.run(s, cfg, u.decimate(s.gps), events=ev, snapshot_times=[20.0])
            ts, k, f = r["snaps"][0]
            out = u.free_run(f, ev, k, ts, [60], s.truth)
            self.assertLess(out[60][1], 0.1, cfg)

    def test_gate_rejects_a_jump_and_accepts_normal_fixes(self):
        fixes = u.decimate(self.s.gps)
        jumped = [(t, md, n + (60.0 if 50 <= t < 53 else 0.0), e) for t, md, n, e in fixes]
        r = u.run(self.s, "odo-mems", jumped)
        rej = [x["t"] for x in r["recs"] if x["rejected"]]
        self.assertEqual(len(rej), 3)
        self.assertTrue(all(50 <= t < 53 for t in rej))
        self.assertEqual(len(r["gate_episodes"]), 1)
        clean = u.run(self.s, "odo-mems", fixes)
        self.assertEqual(sum(x["rejected"] for x in clean["recs"]), 0)

    def test_drag_detector_fires_on_drag_and_not_on_clean(self):
        fixes = u.decimate(self.s.gps)
        clean = u.run(self.s, "odo-fog", fixes, drag=True)
        self.assertEqual(clean["drag"].episodes, [])
        dragged = u.run(self.s, "odo-fog", u.inject_drag(fixes, 40.0, 1.0), drag=True)
        self.assertTrue(dragged["drag"].episodes)
        delay = dragged["drag"].episodes[0] - 40.0
        self.assertGreater(delay, u.DRAG_THRESHOLD_M / 1.0 - 1.0)
        self.assertLess(delay, u.DRAG_WINDOW_S)

    def test_inject_drag_offsets(self):
        fixes = [(t, 3, 0.0, 0.0) for t in (0.0, 10.0, 20.0)]
        out = u.inject_drag(fixes, 10.0, 0.5, direction=0.0)
        self.assertEqual([round(f[2], 9) for f in out], [0.0, 0.0, 5.0])


@unittest.skipIf(not HAVE_DATA, "no NCLT data; run python3 fetch_nclt.py")
class RealDataCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = nclt_io.Session(DATA)
        cls.fixes = u.decimate(cls.s.gps)

    def test_frame_alignment_residual(self):
        self.assertLess(u.pct(self.s.align_residuals, 0.5), 1.5)

    def test_wheels_beat_imu_only_over_60_s(self):
        drift = {}
        starts = [200.0, 400.0, 600.0]
        for cfg in u.CONFIGS:
            ev = u.build_events(self.s, cfg)
            r = u.run(self.s, cfg, self.fixes, events=ev, snapshot_times=starts)
            drift[cfg] = max(u.free_run(f, ev, k, ts, [60], self.s.truth)[60][1] for ts, k, f in r["snaps"])
        self.assertLess(drift["odo-mems"], drift["ins"])
        self.assertLess(drift["odo-fog"], drift["ins"])

    def test_gate_spares_good_fixes(self):
        r = u.run(self.s, "odo-mems", self.fixes)
        good_rejected = sum(1 for x in r["recs"] if x["rejected"]
                            and u.err_to_truth(self.s.truth, x["t"], x["z"]) < u.GOOD_FIX_M)
        self.assertEqual(good_rejected, 0)

    def test_fast_drag_is_detected(self):
        r = u.run(self.s, "odo-fog", u.inject_drag(self.fixes, 300.0, 1.0), drag=True)
        hits = [t for t in r["drag"].episodes if 300.0 <= t <= 360.0]
        self.assertTrue(hits)


if __name__ == "__main__":
    unittest.main()
