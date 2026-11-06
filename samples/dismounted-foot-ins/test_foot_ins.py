"""Stdlib unit tests: python3 -m unittest -v test_foot_ins"""
import math
import os
import random
import struct
import tempfile
import unittest
import zlib

import detectors
import foot_ins
import matfile
from foot_ins import FootINS, GRAVITY

G = GRAVITY
FS = 200.0
DT = 1.0 / FS


def still(n, tilt_deg=0.0, noise=0.0, seed=1, gyro_bias=(0.0, 0.0, 0.0)):
    rnd = random.Random(seed)
    t = math.radians(tilt_deg)
    acc = [[G * math.sin(t) + rnd.gauss(0, noise), rnd.gauss(0, noise), -G * math.cos(t) + rnd.gauss(0, noise)]
           for _ in range(n)]
    gyro = [[gyro_bias[i] + rnd.gauss(0, noise * 1e-2) for i in range(3)] for _ in range(n)]
    return acc, gyro


class Detectors(unittest.TestCase):
    def test_shoe_low_when_still_any_tilt(self):
        for tilt in (0.0, 30.0):
            acc, gyro = still(50, tilt_deg=tilt, noise=1e-3)
            stat = detectors.shoe(acc, gyro)
            self.assertTrue(all(detectors.stance(stat, 1e7)), tilt)

    def test_shoe_high_when_rotating(self):
        acc, gyro = still(50)
        gyro = [[0.0, 2.0, 0.0] for _ in gyro]
        self.assertFalse(any(detectors.stance(detectors.shoe(acc, gyro), 8.5e7)))

    def test_shoe_matches_formula_on_one_window(self):
        acc = [[0.1 * i, -0.2, -G + 0.05 * i] for i in range(5)]
        gyro = [[0.01 * i, 0.0, -0.02] for i in range(5)]
        m = [sum(a[j] for a in acc) / 5 for j in range(3)]
        nm = math.sqrt(sum(x * x for x in m))
        ref = sum(sum((a[j] - G * m[j] / nm) ** 2 for j in range(3)) / detectors.SIGMA_A ** 2
                  + sum(w[j] ** 2 for j in range(3)) / detectors.SIGMA_W ** 2 for a, w in zip(acc, gyro)) / 5
        self.assertAlmostEqual(detectors.shoe(acc, gyro)[0], ref, delta=ref * 1e-12)

    def test_blocks_fill_window_and_tail_is_stance(self):
        acc, gyro = still(12)
        gyro = [[0.0, 0.0, float(i)] for i in range(12)]
        stat = detectors.ared(gyro)
        self.assertEqual(stat[0], stat[4])
        self.assertAlmostEqual(stat[5], sum(i * i for i in range(5, 10)) / 5)
        self.assertEqual(stat[10:], [0.0, 0.0])  # pyshoe leaves the partial tail window at 0

    def test_amvd_and_mbgtd_zero_for_constant_acc(self):
        acc, _ = still(20)
        self.assertTrue(all(abs(s) < 1e-12 for s in detectors.amvd(acc)))
        self.assertTrue(all(abs(s) < 1e-12 for s in detectors.mbgtd(acc)[:16]))

    def test_mbgtd_detects_jump(self):
        acc, _ = still(10)
        for a in acc[5:]:
            a[0] += 3.0
        stat = detectors.mbgtd(acc)
        self.assertGreater(stat[3], 1.0)
        self.assertAlmostEqual(stat[0], 0.0)


class Strapdown(unittest.TestCase):
    def test_euler_quat_roundtrip(self):
        q = foot_ins.quat_from_euler(0.1, -0.2, 2.5)
        self.assertAlmostEqual(foot_ins.yaw_of(q), 2.5, places=12)
        C = foot_ins.quat_to_dcm(q)
        for i in range(3):
            for j in range(3):
                dot = sum(C[k][i] * C[k][j] for k in range(3))
                self.assertAlmostEqual(dot, 1.0 if i == j else 0.0, places=12)

    def test_initial_levelling(self):
        acc, _ = still(20, tilt_deg=20.0)
        f = FootINS(acc)
        C = f.C
        self.assertAlmostEqual(math.degrees(-math.asin(C[2][0])), 20.0, places=6)

    def test_yaw_rate_integration(self):
        acc, _ = still(1)
        f = FootINS(acc, freeze_biases=True)
        for _ in range(200):
            f.propagate([0.0, 0.0, -G], [0.0, 0.0, math.pi / 2], DT)
        self.assertAlmostEqual(foot_ins.yaw_of(f.q), math.pi / 2, places=9)

    def test_constant_acceleration(self):
        acc, _ = still(1)
        f = FootINS(acc, freeze_biases=True, pyshoe_order=False)
        for _ in range(200):
            f.propagate([1.0, 0.0, -G], [0.0, 0.0, 0.0], DT)
        self.assertAlmostEqual(f.v[0], 1.0, places=9)
        self.assertAlmostEqual(f.p[0], 0.5, places=9)
        self.assertAlmostEqual(f.p[2], 0.0, places=9)


class Filter(unittest.TestCase):
    def assert_cov_ok(self, P):
        for i in range(15):
            self.assertGreaterEqual(P[i][i], 0.0)
            for j in range(15):
                self.assertAlmostEqual(P[i][j], P[j][i], places=15)

    def test_zupt_holds_still_imu(self):
        acc, gyro = still(2000, tilt_deg=10.0, noise=0.02, seed=3)
        f = FootINS(acc)
        for k in range(1, len(acc)):
            f.propagate(acc[k], gyro[k], DT)
            f.zupt()
        self.assertLess(math.sqrt(sum(p * p for p in f.p)), 0.01)
        self.assertLess(math.sqrt(sum(v * v for v in f.v)), 0.01)
        self.assert_cov_ok(f.P)

    def test_no_zupt_drifts_quadratically(self):
        acc, gyro = still(400, tilt_deg=10.0)
        acc = [[a[0] + 0.05, a[1], a[2]] for a in acc]  # uncompensated bias
        f = FootINS(still(1, tilt_deg=10.0)[0], freeze_biases=True)
        for k in range(1, len(acc)):
            f.propagate(acc[k], gyro[k], DT)
        self.assertGreater(math.hypot(f.p[0], f.p[1]), 0.05 * 0.5 * 1.9 ** 2)

    def test_zaru_estimates_gyro_bias(self):
        old = foot_ins.SIGMA_BG0
        foot_ins.SIGMA_BG0 = 0.005  # consumer-MEMS-sized prior for this test
        self.addCleanup(setattr, foot_ins, "SIGMA_BG0", old)
        bias = (0.002, -0.001, 0.003)
        acc, gyro = still(1000, gyro_bias=bias)
        f = FootINS(acc)
        for k in range(1, len(acc)):
            f.propagate(acc[k], gyro[k], DT)
            f.zupt()
            f.zaru(gyro[k])
        for i in range(3):
            self.assertAlmostEqual(f.bg[i], bias[i], delta=1e-4)
        self.assert_cov_ok(f.P)

    def test_frozen_biases_stay_zero(self):
        acc, gyro = still(100, gyro_bias=(0.01, 0.0, 0.0))
        f = FootINS(acc, freeze_biases=True)
        for k in range(1, len(acc)):
            f.propagate(acc[k], gyro[k], DT)
            f.zupt()
            f.zaru(gyro[k])
        self.assertEqual(f.bg, [0.0, 0.0, 0.0])
        self.assertTrue(all(f.P[i][j] == 0.0 for i in range(9, 15) for j in range(15)))

    def test_heading_update_pulls_yaw(self):
        acc, _ = still(1)
        f = FootINS(acc, yaw0=0.0)
        f.P[8][8] = math.radians(10) ** 2
        f.heading_update(math.radians(10), math.radians(1))
        self.assertAlmostEqual(math.degrees(foot_ins.yaw_of(f.q)), 10 * 100 / 101, places=4)

    def test_range_update_and_gate(self):
        acc, _ = still(1)
        f = FootINS(acc)
        for i in range(3):
            f.P[i][i] = 4.0
        anchor = (10.0, 0.0, 0.0)
        nis = f.range_update(anchor, 9.0, 0.1)  # truth is 1 m closer to the anchor
        self.assertAlmostEqual(f.p[0], 1.0 * 4.0 / 4.01, places=6)
        self.assertAlmostEqual(nis, 1.0 / 4.01, places=6)
        before = f.p[:]
        nis = f.range_update(anchor, 3.0, 0.1, gate=6.63)  # 6 m NLOS-like outlier
        self.assertGreater(nis, 6.63)
        self.assertEqual(f.p, before)

    def test_pyshoe_order_differs_only_in_integration(self):
        acc, gyro = still(1)
        a = FootINS(acc, freeze_biases=True, pyshoe_order=False)
        b = FootINS(acc, freeze_biases=True, pyshoe_order=True)
        for f in (a, b):
            for _ in range(100):
                f.propagate([1.0, 0.0, -G], [0.0, 0.0, 0.0], DT)
        self.assertAlmostEqual(b.p[0] - a.p[0], 100 * DT * DT * 1.0, places=9)


def mat_element(name, rows, compress=False):
    nr, nc = len(rows), len(rows[0])
    data = struct.pack("<%dd" % (nr * nc), *[rows[r][c] for c in range(nc) for r in range(nr)])
    nm = name.encode()
    body = struct.pack("<II", 6, 8) + struct.pack("<II", 6, 0)
    body += struct.pack("<II", 5, 8) + struct.pack("<ii", nr, nc)
    body += struct.pack("<HH", 1, len(nm)) + nm.ljust(4, b"\0") if len(nm) <= 4 else \
        struct.pack("<II", 1, len(nm)) + nm + b"\0" * (-len(nm) % 8)
    body += struct.pack("<II", 9, len(data)) + data
    el = struct.pack("<II", 14, len(body)) + body
    if compress:
        z = zlib.compress(el)
        return struct.pack("<II", 15, len(z)) + z + b"\0" * (-len(z) % 8)
    return el


class MatFile(unittest.TestCase):
    def test_roundtrip_plain_and_compressed(self):
        hdr = b"MATLAB 5.0 MAT-file test".ljust(116, b" ") + b"\0" * 8 + struct.pack("<H", 0x0100) + b"IM"
        blob = hdr + mat_element("imu", [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]) + \
            mat_element("gt_idx", [[7.0, 8.0, 9.0]], compress=True)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.mat")
            with open(p, "wb") as fh:
                fh.write(blob)
            m = matfile.loadmat(p)
        self.assertEqual(m["imu"], [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        self.assertEqual(m["gt_idx"], [[7.0, 8.0, 9.0]])


if __name__ == "__main__":
    unittest.main()
