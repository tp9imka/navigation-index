import math
import unittest

import timing_holdover as th

SPOOF_KW = dict(settle_s=th.SPOOF_SETTLE_S, train_s=th.SPOOF_TRAIN_S,
                end_s=th.SPOOF_SETTLE_S + th.SPOOF_TRAIN_S + th.SPOOF_DURATION_S)
SPOOF_START = th.SPOOF_SETTLE_S + th.SPOOF_TRAIN_S


class NoiseModel(unittest.TestCase):
    def test_white_fm_adev_matches_parameter(self):
        g = th.Grade("test", 1e-10, 0.0, 0.0, "test")
        x = th.free_run_phase(g, 40000, 1.0, seed=3)
        for m in (1, 10, 100):
            expected = g.adev_1s / math.sqrt(m)
            self.assertAlmostEqual(th.oadev(x, 1.0, m) / expected, 1.0, delta=0.15)

    def test_aging_gives_quadratic_phase(self):
        d = 1e-14
        g = th.Grade("test", 1e-15, d, 0.0, "test")
        x = th.free_run_phase(g, 86400, 10.0, seed=1)
        self.assertAlmostEqual(x[-1] / (0.5 * d * 86400 ** 2), 1.0, delta=0.01)


class Discipline(unittest.TestCase):
    def test_loop_locks_to_pps_noise_level(self):
        cfg = th.Config()
        for g in th.GRADES:
            r = th.run(g, cfg, 5, settle_s=4 * 3600, end_s=5 * 3600)
            # TCXO white FM alone is ~35 ns at its 1200 s loop time constant
            limit = 5 * cfg.sigma_pps if g.name == "TCXO" else 2 * cfg.sigma_pps
            self.assertLess(r.te_locked_rms, limit, g.name)

    def test_holdover_ordering_at_24h(self):
        res = th.holdover_study(th.Config(), runs=3)
        day = th.HOLDOVER_CHECKPOINTS[-1]
        te = {k: v["te_median_us"][day] for k, v in res.items()}
        self.assertLess(te["Rb"], min(te["CSAC"], te["OCXO"]))
        self.assertLess(max(te["CSAC"], te["OCXO"]), te["TCXO"])


class Spoofing(unittest.TestCase):
    cfg = th.Config(temp_fraction=0.1)

    def test_cross_source_catches_walk_on_every_grade(self):
        for g in th.GRADES:
            r = th.run(g, self.cfg, 1, spoof_at=SPOOF_START, spoof_rate=2e-9, **SPOOF_KW)
            self.assertIsNotNone(r.alarm_cross_s, g.name)
            self.assertLess(r.alarm_cross_s, 600, g.name)

    def test_no_alarm_without_spoof(self):
        for g in th.GRADES:
            for seed in (11, 12):
                r = th.run(g, self.cfg, seed, **SPOOF_KW)
                self.assertIsNone(r.alarm_cross_s, g.name)
                self.assertIsNone(r.alarm_internal_s, g.name)

    def test_cross_detector_is_live(self):
        blind = th.Config(temp_fraction=0.1, cross_margin=1e-3)
        r = th.run(th.GRADE_BY_NAME["Rb"], blind, 1, spoof_at=SPOOF_START, spoof_rate=2e-9, **SPOOF_KW)
        self.assertIsNone(r.alarm_cross_s)

    def test_guard_holds_rb_close_to_truth(self):
        g = th.GRADE_BY_NAME["Rb"]
        kw = dict(spoof_at=SPOOF_START, spoof_rate=2e-9, **SPOOF_KW)
        followed = th.run(g, self.cfg, 1, mitigate=False, **kw)
        guarded = th.run(g, self.cfg, 1, mitigate=True, **kw)
        self.assertLess(abs(guarded.te_end), 0.1 * abs(followed.te_end))

    def test_internal_monitor_misses_slow_walk_on_tcxo(self):
        r = th.run(th.GRADE_BY_NAME["TCXO"], self.cfg, 1, spoof_at=SPOOF_START, spoof_rate=0.5e-9, **SPOOF_KW)
        self.assertIsNone(r.alarm_internal_s)


if __name__ == "__main__":
    unittest.main()
