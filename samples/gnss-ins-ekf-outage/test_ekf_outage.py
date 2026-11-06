"""Stdlib tests for matlite and the loosely-coupled GNSS/INS EKF."""

import math
import random
import unittest

import ekf_outage
import matlite as m

try:
    import numpy as np
    import filterpy_crosscheck
except ImportError:
    np = None

R_VAR = ekf_outage.GNSS_NOISE_SD ** 2


def is_psd(a, tol=1e-12):
    """Cholesky with a small tolerance; False if any pivot goes negative."""
    n = len(a)
    L = m.zeros(n, n)
    for i in range(n):
        for j in range(i + 1):
            s = a[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if s < -tol:
                    return False
                L[i][i] = math.sqrt(max(s, 0.0))
            elif L[j][j] > 0:
                L[i][j] = s / L[j][j]
    return True


def is_symmetric(a):
    return all(a[i][j] == a[j][i] for i in range(len(a)) for j in range(len(a)))


def trace(a):
    return sum(a[i][i] for i in range(len(a)))


class MatliteTest(unittest.TestCase):
    def test_matmul_known_answer(self):
        self.assertEqual(m.matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]), [[19, 22], [43, 50]])
        self.assertEqual(m.matmul([[1, 2, 3]], [[1], [0], [2]]), [[7]])

    def test_inv2_is_inverse(self):
        a = [[4.0, 1.5], [1.5, 9.0]]
        prod = m.matmul(a, m.inv2(a))
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(prod[i][j], 1.0 if i == j else 0.0, places=12)

    def test_transpose_symmetrize(self):
        self.assertEqual(m.transpose([[1, 2, 3]]), [[1], [2], [3]])
        self.assertEqual(m.symmetrize([[1.0, 2.0], [4.0, 1.0]]), [[1.0, 3.0], [3.0, 1.0]])


class EkfStepTest(unittest.TestCase):
    def make(self, pos_var=4.0):
        f = ekf_outage.Ekf([0.0] * 8)
        f.P = m.diag([pos_var, pos_var, 1.0, 1.0, 0.01, 0.01, 0.01, 1e-6])
        return f

    def test_mechanize_rotates_body_accel_into_nav_frame(self):
        f = self.make()
        f.x[4] = math.pi / 2
        f.mechanize(2.0, 0.0, 0.0, 0.5)  # body-forward accel, heading 90 deg => +y
        self.assertAlmostEqual(f.x[0], 0.0, places=12)
        self.assertAlmostEqual(f.x[1], 0.5 * 2.0 * 0.25)
        self.assertAlmostEqual(f.x[3], 1.0)

    def test_mechanize_removes_bias(self):
        f = self.make()
        f.x[5], f.x[7] = 0.3, 0.01
        f.mechanize(0.3, 0.0, 0.01, 1.0)
        self.assertAlmostEqual(f.x[2], 0.0)
        self.assertAlmostEqual(f.x[4], 0.0)

    def test_nis_known_answer(self):
        f = self.make(pos_var=4.0)
        y, Si, nis = f.innovation(3.0, 4.0)
        self.assertEqual(y, (3.0, 4.0))
        self.assertAlmostEqual(nis, 25.0 / (4.0 + R_VAR))

    def test_update_known_answer(self):
        f = self.make(pos_var=4.0)
        y, Si, _ = f.innovation(5.0, 0.0)
        f.update(y, Si)
        gain = 4.0 / (4.0 + R_VAR)
        self.assertAlmostEqual(f.x[0], gain * 5.0)
        self.assertAlmostEqual(f.x[1], 0.0)
        self.assertAlmostEqual(f.P[0][0], 4.0 * R_VAR / (4.0 + R_VAR))
        self.assertAlmostEqual(f.P[2][2], 1.0)  # uncorrelated states untouched

    def test_update_shrinks_error_and_covariance(self):
        rng = random.Random(1)
        f = self.make(pos_var=100.0)
        f.x[0], f.x[1] = 20.0, -15.0  # truth at origin
        before = math.hypot(f.x[0], f.x[1])
        tr_before = trace(f.P)
        for _ in range(5):
            y, Si, _ = f.innovation(rng.gauss(0, 0.1), rng.gauss(0, 0.1))
            f.update(y, Si)
            self.assertTrue(is_psd(f.P))
            self.assertTrue(is_symmetric(f.P))
        self.assertLess(math.hypot(f.x[0], f.x[1]), 0.2 * before)
        self.assertLess(trace(f.P), tr_before)

    def test_propagation_grows_position_variance_and_stays_psd(self):
        f = self.make(pos_var=1.0)
        f.last_f = (0.5, 0.2)
        p0 = f.P[0][0]
        for _ in range(200):
            f.propagate_cov(0.1)
            self.assertTrue(is_symmetric(f.P))
        self.assertTrue(is_psd(f.P))
        self.assertGreater(f.P[0][0], p0)
        self.assertGreater(f.P[0][2], 0.0)  # position-velocity correlation builds up

    def test_psd_check_can_fail(self):
        self.assertFalse(is_psd([[1.0, 2.0], [2.0, 1.0]]))


class ScenarioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = random.Random(7)
        cls.truth, cls.imu = ekf_outage.simulate(rng)
        cls.fixes = ekf_outage.gnss_fixes(cls.truth, rng, 1.0)
        cls.res = {mode: ekf_outage.run(cls.truth, cls.imu, cls.fixes, mode) for mode in ekf_outage.MODES}

    def stats(self, mode, segment):
        _, lo, hi = next(s for s in ekf_outage.SEGMENTS if s[0] == segment)
        return ekf_outage.segment_stats(self.res[mode][0], lo, hi)

    def test_readme_table_seed7(self):
        # README "Expected output", seed 7, spoof 1.0 m/s: RMS / max / end
        expected = {
            ("ins", "outage"): (995.2, 1303.8, 1303.8),
            ("ekf", "nominal"): (1.9, 5.7, 1.8),
            ("ekf", "outage"): (4.9, 7.7, 7.7),
            ("ekf", "recovery"): (1.4, 2.4, 0.9),
            ("ekf", "spoofing"): (70.4, 122.8, 122.8),
            ("gate", "spoofing"): (33.7, 66.3, 66.3),
            ("latch", "spoofing"): (24.4, 46.5, 46.5),
        }
        for (mode, seg), want in expected.items():
            got = self.stats(mode, seg)
            for g, w in zip(got, want):
                self.assertAlmostEqual(g, w, delta=0.05, msg=f"{mode}/{seg}")
        ev = self.res["gate"][1]
        self.assertEqual(ev["rejected"], 101)
        self.assertEqual(ev["spoof_rejected"], 101)
        self.assertEqual(ev["alarm_t"], 300.0)

    def test_no_fixes_during_outage(self):
        for k in self.fixes:
            t = self.truth[k][0]
            self.assertFalse(ekf_outage.OUTAGE_START_S <= t < ekf_outage.OUTAGE_END_S)

    def test_first_fix_after_outage_shrinks_error(self):
        errors = self.res["ekf"][0]
        k_end = next(k for k in sorted(self.fixes) if self.truth[k][0] >= ekf_outage.OUTAGE_END_S)
        self.assertLess(errors[k_end][1], errors[k_end - 1][1])

    def test_gate_never_rejects_clean_fixes_here(self):
        ev = self.res["gate"][1]
        self.assertEqual(ev["rejected"] - ev["spoof_rejected"], 0)
        self.assertEqual(self.res["ekf"][1]["rejected"], 0)
        self.assertIsNone(self.res["ekf"][1]["alarm_t"])

    def test_ordering_ins_worst_latch_best_under_spoofing(self):
        ends = {mode: self.res[mode][0][-1][1] for mode in ekf_outage.MODES}
        self.assertGreater(ends["ins"], ends["ekf"])
        self.assertGreater(ends["ekf"], ends["gate"])
        self.assertGreater(ends["gate"], ends["latch"])


@unittest.skipIf(np is None, "numpy / filterpy not installed")
class FilterpyCrosscheckTest(unittest.TestCase):
    def test_single_update_matches_stdlib(self):
        x0 = [1.0, -2.0, 3.0, 0.5, 0.1, 0.0, 0.0, 0.0]
        a, b = ekf_outage.Ekf(x0), filterpy_crosscheck.FilterpyEkf(x0)
        a.last_f = b.last_f = (0.4, -0.1)
        a.propagate_cov(0.1)
        b.propagate_cov(0.1)
        ya, Sia, nisa = a.innovation(6.0, 1.0)
        yb, Sib, nisb = b.innovation(6.0, 1.0)
        self.assertAlmostEqual(nisa, nisb, places=9)
        a.update(ya, Sia)
        b.update(yb, Sib)
        for i in range(8):
            self.assertAlmostEqual(a.x[i], b.x[i], places=9)


if __name__ == "__main__":
    unittest.main()
