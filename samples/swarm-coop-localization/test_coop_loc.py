import math
import random
import unittest

import coop_loc
import filters
from sim import Config, RangeMeas, generate


def short_cfg(**kw):
    kw.setdefault("duration", 200)
    return Config(**kw)


def team_rmse(cfg, eps, r, agents=None):
    agents = range(cfg.n_agents) if agents is None else agents
    return coop_loc.rms([r["err"][k][a] for k in range(len(eps)) for a in agents])


class TestMeasurementModel(unittest.TestCase):
    def test_range_and_bearing_jacobians_match_finite_differences(self):
        pa, po = (3.0, -2.0), (40.0, 25.0)
        m = RangeMeas(0, 1, 0.0, bearing=0.0)
        terms = filters.rel_terms(pa, po, m, True)
        self.assertEqual(len(terms), 2)
        eps = 1e-6
        for idx, (_, h, Ha, Ho, _, _) in enumerate(terms):
            for k in (0, 1):
                pa2 = list(pa)
                pa2[k] += eps
                po2 = list(po)
                po2[k] += eps
                ha = filters.rel_terms(pa2, po, m, True)[idx][1]
                ho = filters.rel_terms(pa, po2, m, True)[idx][1]
                self.assertAlmostEqual((ha - h) / eps, Ha[k], places=4)
                self.assertAlmostEqual((ho - h) / eps, Ho[k], places=4)

    def test_bearing_only_for_initiator(self):
        m = RangeMeas(0, 1, 10.0, bearing=0.3)
        self.assertEqual(len(filters.rel_terms((0, 0), (10, 0), m, False)), 1)


class TestRobust(unittest.TestCase):
    def test_plain_passes_everything(self):
        self.assertEqual(filters.robust_variance(100.0, 1.0, 0.1, robust=False), 0.1)

    def test_gate_rejects_and_huber_inflates(self):
        self.assertIsNone(filters.robust_variance(-4.0, 1.0, 0.1, robust=True))
        self.assertEqual(filters.robust_variance(1.0, 1.0, 0.1, robust=True), 0.1)
        inflated = filters.robust_variance(-2.5, 1.0, 0.1, robust=True)
        self.assertGreater(inflated, 0.1)

    def test_nlos_side_is_stricter(self):
        # a 3.2-sigma long range passes the symmetric gate but not the NLOS-aware one
        self.assertIsNotNone(filters.robust_variance(3.2, 1.0, 0.1, True, nlos_aware=False))
        self.assertIsNone(filters.robust_variance(3.2, 1.0, 0.1, True, nlos_aware=True))
        self.assertIsNotNone(filters.robust_variance(-3.2, 1.0, 0.1, True, nlos_aware=True))

    def test_peer_test_tolerates_nlos_excess_only_on_long_side(self):
        S = 1.0
        self.assertFalse(filters.peer_range_fails(filters.NLOS_MAX_EXCESS, S))
        self.assertTrue(filters.peer_range_fails(-filters.NLOS_MAX_EXCESS, S))


class TestCovarianceIntersection(unittest.TestCase):
    def test_ci_bound_holds_for_any_cross_correlation(self):
        # blkdiag(Pa / w, Po / (1 - w)) - [[Pa, C], [C^T, Po]] must be PSD for any valid C
        rng = random.Random(3)
        Pa = [[4.0, 1.0], [1.0, 3.0]]
        Po = [[2.0, -0.5], [-0.5, 5.0]]
        for _ in range(200):
            w = rng.uniform(0.05, 0.95)
            rho = rng.uniform(-0.99, 0.99)
            C = [[rho * math.sqrt(Pa[0][0] * Po[0][0]), 0.0], [0.0, rho * math.sqrt(Pa[1][1] * Po[1][1])]]
            joint = [[Pa[0][0], Pa[0][1], C[0][0], C[0][1]],
                     [Pa[1][0], Pa[1][1], C[1][0], C[1][1]],
                     [C[0][0], C[1][0], Po[0][0], Po[0][1]],
                     [C[0][1], C[1][1], Po[1][0], Po[1][1]]]
            if not _is_psd(joint):
                continue
            bound = [[Pa[r][c] / w if r < 2 and c < 2 else 0.0 for c in range(4)] for r in range(4)]
            for r in range(2):
                for c in range(2):
                    bound[2 + r][2 + c] = Po[r][c] / (1 - w)
            diff = [[bound[r][c] - joint[r][c] for c in range(4)] for r in range(4)]
            self.assertTrue(_is_psd(diff, tol=1e-9))

    def test_ci_update_does_not_increase_uncertainty(self):
        cfg = short_cfg()
        init = [(0.0, 0.0), (50.0, 0.0)] + [(0.0, 50.0 * k) for k in range(1, 5)]
        d = filters.Decentralized(init, cfg, mode="ci")
        d.blocks[0][1][0][0] = d.blocks[0][1][1][1] = 400.0
        before = [d.blocks[0][1][k][k] for k in range(filters.D)]
        snap = ((50.0, 0.0), [[1.0, 0.0], [0.0, 1.0]], 0, set())
        d._rel_update(0, snap, 1, RangeMeas(0, 1, 52.0), False)
        after = [d.blocks[0][1][k][k] for k in range(filters.D)]
        self.assertLess(after[0], before[0])
        self.assertLessEqual(sum(a / b for a, b in zip(after, before)), filters.D)


def _is_psd(M, tol=0.0):
    n = len(M)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = M[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if s < -tol:
                    return False
                L[i][i] = math.sqrt(max(s, 0.0)) or 1e-12
            else:
                L[i][j] = s / L[j][j]
    return True


class TestSimulation(unittest.TestCase):
    def test_deterministic_for_seed(self):
        a = generate(short_cfg(seed=7))[1]
        b = generate(short_cfg(seed=7))[1]
        self.assertEqual([m.r for m in a[50].ranges], [m.r for m in b[50].ranges])

    def test_nlos_and_outliers_only_lengthen_ranges(self):
        _, eps = generate(short_cfg())
        for ep in eps:
            for m in ep.ranges:
                d = math.dist(ep.truth[m.i], ep.truth[m.j])
                if m.nlos or m.outlier:
                    self.assertGreater(m.r - d, 0.5)

    def test_spoof_offset_applies_only_to_spoofed_agent(self):
        cfg = short_cfg(spoof_agent=0, spoof_start=100.0)
        _, eps = generate(cfg)
        ep = eps[-1]
        self.assertGreater(math.dist(ep.gnss[0], ep.truth[0]), 40.0)
        self.assertLess(math.dist(ep.gnss[1], ep.truth[1]), 20.0)


class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = Config(seed=1, duration=300)
        _, cls.eps, cls.res = coop_loc.run(cls.cfg, "nominal")

    def test_cooperation_beats_dead_reckoning_for_denied_agents(self):
        denied = [a for a in range(self.cfg.n_agents) if a not in self.cfg.gnss_agents]
        dr = team_rmse(self.cfg, self.eps, self.res["dead-reckoning"], denied)
        for name in ("central-robust", "ci-robust"):
            self.assertLess(team_rmse(self.cfg, self.eps, self.res[name], denied), 0.5 * dr, name)

    def test_robust_ranging_helps_centralized(self):
        plain = team_rmse(self.cfg, self.eps, self.res["central-plain"])
        robust = team_rmse(self.cfg, self.eps, self.res["central-robust"])
        self.assertLess(robust, plain)

    def test_naive_decentralized_is_overconfident_and_ci_is_not(self):
        naive = coop_loc.summarize(self.cfg, self.eps, self.res["naive-robust"])["nees"]
        ci = coop_loc.summarize(self.cfg, self.eps, self.res["ci-robust"])["nees"]
        self.assertGreater(naive, 50.0)
        self.assertLess(ci, 5.0)

    def test_decentralized_sends_fewer_bytes(self):
        c = self.res["central-robust"]["bytes"]
        d = self.res["ci-robust"]["bytes"]
        self.assertLess(d, c)


class TestSpoofIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = Config(seed=1, duration=450)
        _, cls.eps, cls.res = coop_loc.run(cls.cfg, "spoof")
        cls.kk = [k for k, ep in enumerate(cls.eps) if ep.t >= cls.cfg.spoof_start]
        cls.others = [a for a in range(cls.cfg.n_agents) if a != cls.cfg.spoof_agent]

    def others_rmse(self, name):
        r = self.res[name]
        return coop_loc.rms([r["err"][k][a] for k in self.kk for a in self.others])

    def test_spoof_propagates_without_integrity(self):
        self.assertGreater(self.others_rmse("central-robust"), 10.0)

    def test_central_solution_separation_detects_and_contains(self):
        det = self.res["central-robust+ss"]["detections"]
        self.assertTrue(det)
        t, agent = det[0]
        self.assertEqual(agent, self.cfg.spoof_agent)
        self.assertGreaterEqual(t, self.cfg.spoof_start)
        self.assertLess(self.others_rmse("central-robust+ss"), 0.3 * self.others_rmse("central-robust"))

    def test_no_false_alarm_without_spoofing(self):
        cfg = Config(seed=1, duration=300, spoof_agent=-1)
        init, eps = generate(cfg)
        m = filters.Centralized(init, cfg, robust=True, integrity="ss")
        for ep in eps:
            m.step(ep)
        self.assertEqual(m.detections, [])

    def test_disabled_monitor_cannot_detect(self):
        # negative control: same run with the monitor off has no detections at all
        self.assertEqual(self.res["central-robust"]["detections"], [])


class TestDecentralizedSolutionSeparation(unittest.TestCase):
    def test_with_bearings_detects_spoof_and_drops_both_anchors(self):
        cfg = Config(seed=1, duration=400, bearing=True, spoof_agent=0)
        init, eps = generate(cfg)
        m = filters.Decentralized(init, cfg, mode="ci", robust=True, integrity="ss")
        for ep in eps:
            m.step(ep)
        self.assertTrue(m.detections)
        t, _ = m.detections[0]
        self.assertGreaterEqual(t, cfg.spoof_start)
        self.assertLess(t, cfg.spoof_start + 60)
        self.assertEqual(m.faulty, "both")
        self.assertTrue(all(m.gnss_excluded[g] for g in cfg.gnss_agents))


if __name__ == "__main__":
    unittest.main()
