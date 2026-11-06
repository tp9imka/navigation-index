"""v2 pieces without SITL: SS FDE + PL, velocity test, spoof model, replay lookup, detections.
Stdlib only (plus the sibling samples it imports)."""
import json
import math
import random
import tempfile
import unittest
from pathlib import Path

import ss_fde
import to_navdash as T
import vgeo_replay
from companion import Spoof

R = {"gnss": 2.0, "vgeo": 5.0}


def fly(drag_mps, coherent=False, seconds=90, onset=20, vgeo_bias=(0.0, 0.0), seed=1):
    """Straight north at 10 m/s, 1 Hz epochs. GNSS is dragged east after onset."""
    rng = random.Random(seed)
    ss = ss_fde.SolutionSeparation(0.0, 0.0, 2.0, R)
    out = []
    for k in range(1, seconds + 1):
        t = float(k)
        te, tn = 0.0, 10.0 * t
        drag = drag_mps * max(0.0, t - onset)
        g = (te + drag + rng.gauss(0, 1.0), tn + rng.gauss(0, 1.0))
        v = (te + vgeo_bias[0] + rng.gauss(0, 2.0), tn + vgeo_bias[1] + rng.gauss(0, 2.0))
        vio = (0.05 + rng.gauss(0, 0.1), 10.0 - 0.03 + rng.gauss(0, 0.1))
        r = ss.step(t, vio, 0.15, {"gnss": g, "vgeo": v})
        r["err"] = math.hypot(r["e"] - te, r["n"] - tn)
        out.append(r)
    return out


class SolutionSeparationTests(unittest.TestCase):
    def test_no_fault_no_exclusion_and_pl_bounds_error(self):
        rows = fly(0.0)
        self.assertFalse(any(r["excluded"] for r in rows))
        self.assertTrue(all(r["err"] < r["hpl"] for r in rows))

    def test_slow_drag_alerts_then_probation_blames_gnss(self):
        rows = fly(1.0, seconds=120)
        first = next(i for i, r in enumerate(rows) if r["excluded"])
        self.assertIn("gnss", rows[first]["excluded"])
        self.assertLess(first + 1 - 20, 20)       # detected within 20 s of onset at 1 m/s
        events = [e for r in rows for e in r["events"]]
        self.assertIn("blame:gnss", events)
        self.assertEqual(rows[-1]["excluded"], ["gnss"])
        self.assertLess(rows[-1]["err"], 10.0)    # main solution stays on vgeo + VIO afterwards

    def test_fast_drag_is_excluded_by_persistent_gating(self):
        rows = fly(3.0)
        first = next(i for i, r in enumerate(rows) if r["excluded"])
        self.assertEqual(rows[first]["excluded"], ["gnss"])
        self.assertTrue(any(e.startswith("detect:gate") for e in rows[first]["events"]))

    def test_protection_level_grows_when_only_one_source_is_left(self):
        rows = fly(3.0)
        i = next(i for i, r in enumerate(rows) if r["excluded"])
        self.assertGreater(rows[-1]["hpl"], rows[i - 1]["hpl"])


class VelocityTests(unittest.TestCase):
    def test_coherent_drag_trips_and_acceleration_inflates_variance(self):
        vc = ss_fde.VelocityConsistency(0.18)
        alarms = [vc.check((1.0, 10.0), (0.0, 10.0))["alarm"] for _ in range(10)]
        self.assertTrue(alarms[-1])
        quiet = ss_fde.VelocityConsistency(0.18)
        res = [quiet.check((0.0, 9.0), (0.0, 10.0), accel_mps2=3.0) for _ in range(10)]
        self.assertFalse(res[-1]["alarm"])


class SpoofTests(unittest.TestCase):
    def test_position_spoof_leaves_velocity_alone(self):
        s = Spoof("position", 25.0, 1.0, 90.0)
        self.assertEqual(s.vel_en(30.0), (0.0, 0.0))
        e, n = s.offset_en(30.0)
        self.assertAlmostEqual(e, 5.0)
        self.assertAlmostEqual(n, 0.0, places=9)

    def test_coherent_spoof_moves_velocity_with_position(self):
        s = Spoof("coherent", 25.0, 3.0, 90.0)
        self.assertEqual(s.offset_m(20.0), 0.0)
        ve, vn = s.vel_en(30.0)
        self.assertAlmostEqual(ve, 3.0)
        self.assertAlmostEqual(vn, 0.0, places=9)
        self.assertEqual(s.vel_en(25.0 + 151 / 3.0), (0.0, 0.0))   # capped offset => no more drag


class ReplayTests(unittest.TestCase):
    def table(self):
        nodes = []
        for e in (0.0, 20.0):
            for n in (0.0, 20.0):
                fail = e == 20.0 and n == 20.0
                nodes.append({"e": e, "n": n, "inliers": 5 if fail else 50,
                              "de": None if fail else 3.0, "dn": None if fail else -1.0})
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"home": [41.3, -81.75, 290.0], "step_m": 20.0, "nodes": nodes}, f)
        return vgeo_replay.load(Path(f.name))

    def test_node_residual_and_failure(self):
        t = self.table()
        fix, info = vgeo_replay.lookup(t, (41.3, -81.75), 0.0, 0.0, random.Random(1))
        self.assertEqual(fix, (3.0, -1.0))
        fix, info = vgeo_replay.lookup(t, (41.3, -81.75), 20.0, 20.0, random.Random(1))
        self.assertIsNone(fix)
        self.assertIn("no fix", info["reason"])

    def test_wrong_home_is_refused(self):
        with self.assertRaises(SystemExit):
            vgeo_replay.lookup(self.table(), (41.31, -81.75), 0.0, 0.0, random.Random(1))


class DetectionTests(unittest.TestCase):
    def test_pre_onset_detection_is_a_false_alarm(self):
        rows = [{"type": "COMPANION_DETECT", "t": 10.0, "detector": "vel"},
                {"type": "COMPANION_DETECT", "t": 31.0, "detector": "ss"}]
        d = T.detections(rows, 25.0, "coherent")
        self.assertTrue(d["vel"]["false_alarm"])
        self.assertIsNone(d["vel"]["ttd_s"])
        self.assertEqual(d["ss"]["ttd_s"], 6.0)
        self.assertTrue(d["any"]["false_alarm"])


if __name__ == "__main__":
    unittest.main()
