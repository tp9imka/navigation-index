import math
import unittest

import timing_network as tn

HOUR = tn.HOUR
NS, US = tn.NS, tn.US


def regional(mode, cfg, seed=1, outage=4 * HOUR):
    scn = tn.Scenario(end_s=tn.SETTLE_S + outage, mode=mode, ref_t=tn.SETTLE_S,
                      loss={n: (tn.SETTLE_S, math.inf) for n in tn.JAMMED_REGION},
                      calib=(tn.SETTLE_S - HOUR, tn.SETTLE_S), checkpoints=())
    return tn.run(scn, cfg, seed)


class Building(unittest.TestCase):
    def test_reuses_holdover_grades(self):
        self.assertTrue(tn.th.__file__.replace("\\", "/").endswith("timing-holdover/timing_holdover.py"))
        self.assertEqual({n.grade for n in tn.NODES}, {"TCXO", "OCXO", "CSAC", "Rb"})

    def test_weights_normalised_and_rb_best(self):
        w = tn.ensemble_weights(tn.Config())
        self.assertAlmostEqual(sum(w.values()), 1.0, places=12)
        self.assertEqual(tn.best_clock(tn.Config()), "radar")
        self.assertLess(w["comms-relay"], 1e-3)

    def test_least_squares_isolates_planted_offset(self):
        edges = [(0, 1, 0.0, 1.0), (0, 2, 0.0, 1.0), (1, 2, 0.0, 1.0), (2, 3, -500.0, 1.0), (0, 3, -500.0, 1.0)]
        o = tn.solve_offsets([0, 1, 2, 3], edges)
        self.assertAlmostEqual(o[3], 500.0, delta=1e-6)
        for i in (0, 1, 2):
            self.assertAlmostEqual(o[i], 0.0, delta=1e-6)


class PeerHoldover(unittest.TestCase):
    def test_peers_keep_tcxo_relay_under_1us_alone_does_not(self):
        cfg = tn.Config()
        alone = regional("alone", cfg)
        peers = regional("peers", cfg)
        self.assertGreater(alone.max_te["comms-relay"], 10 * US)
        self.assertLess(peers.max_te["comms-relay"], 1 * US)
        self.assertLess(peers.max_te["sensor-south"], 1 * US)

    def test_unknown_asymmetry_shows_up_as_half(self):
        links = [k for k, l in enumerate(tn.LINKS) if "comms-relay" in (l.a, l.b) and l.kind == "microwave"]

        def te(cal, extra, when):
            scn = tn.Scenario(end_s=tn.SETTLE_S + 2 * HOUR, mode="peers", ref_t=tn.SETTLE_S,
                              loss={n: (tn.SETTLE_S, math.inf) for n in tn.JAMMED_REGION},
                              calib=(tn.SETTLE_S - HOUR, tn.SETTLE_S), checkpoints=(2 * HOUR,),
                              asym_change={k: (when, extra) for k in links})
            return tn.run(scn, tn.Config(calibrate=cal), 1).te_at["comms-relay"][2 * HOUR]

        # same seed, so the difference is the bias alone: half the added asymmetry
        self.assertAlmostEqual(abs(te(False, 2 * US, 0.0) - te(False, 0.0, 0.0)), 1 * US, delta=20 * NS)
        self.assertAlmostEqual(te(True, 2 * US, 0.0) - te(True, 0.0, 0.0), 0.0, delta=20 * NS)
        self.assertAlmostEqual(abs(te(True, 2 * US, tn.SETTLE_S) - te(True, 0.0, 0.0)), 1 * US, delta=20 * NS)

    def test_mean_filter_suffers_from_queue_asymmetry(self):
        mean = tn.Config(pkt_filter="mean", pdv_scale=4.0, calibrate=False)
        lucky = tn.Config(pkt_filter="min", pdv_scale=4.0, calibrate=False)
        te_mean = max(regional("peers", mean).max_te[n] for n in tn.JAMMED_REGION)
        te_min = max(regional("peers", lucky).max_te[n] for n in tn.JAMMED_REGION)
        self.assertGreater(te_mean, 5 * te_min)


class Spoof(unittest.TestCase):
    cfg = tn.Config(dt=1.0)

    def test_relay_walk_detected_isolated_and_contained(self):
        ug = tn.run(tn.spoof_scenario("comms-relay", 50 * NS, guard=False), self.cfg, 1)
        gd = tn.run(tn.spoof_scenario("comms-relay", 50 * NS, guard=True), self.cfg, 1)
        self.assertEqual(len(gd.alarms), 1)
        self.assertEqual(gd.alarms[0][1], "comms-relay")
        self.assertLess(gd.alarms[0][0], 120)
        down_ug = max(ug.max_te[n] for n in tn.SPOOF_JAMMED)
        down_gd = max(gd.max_te[n] for n in tn.SPOOF_JAMMED)
        self.assertGreater(down_ug, 100 * US)
        self.assertLess(down_gd, 1 * US)

    def test_no_alarm_without_spoof(self):
        for seed in (101, 102):
            r = tn.run(tn.spoof_scenario("comms-relay", 0.0, guard=True), self.cfg, seed)
            self.assertEqual(r.alarms, [])

    def test_blind_detector_misses(self):
        blind = tn.Config(dt=1.0, cons_margin=1e-3)
        r = tn.run(tn.spoof_scenario("comms-relay", 50 * NS, guard=True), blind, 1)
        self.assertEqual(r.alarms, [])


class AllLost(unittest.TestCase):
    def test_network_time_beats_alone(self):
        cfg = tn.Config()
        out = {}
        for mode in ("alone", "best", "ensemble"):
            scn = tn.Scenario(end_s=tn.SETTLE_S + 4 * HOUR, mode=mode, ref_t=tn.SETTLE_S,
                              loss={n.name: (tn.SETTLE_S, math.inf) for n in tn.NODES},
                              calib=(tn.SETTLE_S - HOUR, tn.SETTLE_S), checkpoints=())
            r = tn.run(scn, cfg, 3)
            out[mode] = max(r.max_te.values())
        self.assertGreater(out["alone"], 10 * US)
        self.assertLess(out["best"], 1.5 * US)
        self.assertLess(out["ensemble"], 1.5 * US)


if __name__ == "__main__":
    unittest.main()
