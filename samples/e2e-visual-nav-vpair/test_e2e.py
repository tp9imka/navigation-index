"""python3 -m unittest test_e2e   (numpy-dependent tests skip without numpy; the results check is stdlib)."""
import json
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    import numpy as np
    import nav_core as nc
    import run_fusion as rf
except ImportError:
    np = None

RESULT = HERE / "results" / "e2e_result.json"


def cand(pos, inliers=100):
    return {"pos": None if pos is None else np.array(pos, float), "inliers": inliers}


@unittest.skipIf(np is None, "numpy not installed")
class VoteTest(unittest.TestCase):
    def setUp(self):
        self.vo = np.array([[45.0 * k, 0.0] for k in range(10)])  # straight east at 45 m per frame

    def test_consistent_candidates_win_over_a_strong_outlier(self):
        c = {k: [cand([45.0 * k + 2, 1.0], 80)] for k in range(6)}
        c[5].append(cand([60000.0, 3000.0], 500))
        pos, support, _ = nc.vote(c, self.vo, 5, 4, 30.0, 3)
        self.assertLess(np.linalg.norm(pos - [227.0, 1.0]), 1e-9)
        self.assertEqual(support, 5)

    def test_one_frame_is_not_enough(self):
        c = {5: [cand([227.0, 0.0])]}
        self.assertIsNone(nc.vote(c, self.vo, 5, 4, 30.0, 3))

    def test_disagreeing_frames_do_not_vote_together(self):
        c = {3: [cand([135.0, 300.0])], 4: [cand([180.0, -300.0])], 5: [cand([225.0, 0.0])]}
        self.assertIsNone(nc.vote(c, self.vo, 5, 4, 30.0, 2))

    def test_single_frame_takes_most_inliers(self):
        self.assertEqual(nc.single_frame_fix([cand([1, 1], 30), cand([9, 9], 300), cand(None, 0)])["inliers"], 300)
        self.assertIsNone(nc.single_frame_fix([cand(None, 0)]))


@unittest.skipIf(np is None, "numpy not installed")
class GeometryTest(unittest.TestCase):
    def test_tile_scale_recovers_reflected_similarity(self):
        T = np.array([[1.0, 0.0], [0.0, -1.0]]) / 765.0
        rng = np.random.default_rng(0)
        X = rng.normal(0, 3e4, (20, 2))
        Tf = nc.fit_tile_scale(X, X @ T.T)
        self.assertTrue(np.allclose(Tf, T, atol=1e-9))

    def test_nadir_offset_is_zero_when_level(self):
        P = np.eye(2)
        self.assertTrue(np.allclose(nc.nadir_offset(np.array([0.0, 0.0, 1.0]), 0.0, 320.0, P), 0.0))

    def test_fix_position_at_tile_centre(self):
        p = nc.fix_position(np.array([10.0, 20.0]), np.eye(2), 300.0, [399.5, 299.5], [399.5, 299.5], np.array([1.0, -1.0]))
        self.assertTrue(np.allclose(p, [11.0, 19.0]))

    def test_error_profile(self):
        truth = np.array([[45.0 * k, 0.0] for k in range(60)])
        est = truth + [3.0, 4.0]
        prof, err = nc.error_profile(est, truth, nc.distance_along(truth), 10)
        self.assertAlmostEqual(prof["final_m"], 5.0)
        self.assertAlmostEqual(prof["rms_m"], 5.0)
        self.assertIn("1000", prof["at_distance_m"])


@unittest.skipIf(np is None, "numpy not installed")
class FilterTest(unittest.TestCase):
    """altpnt v2 Monitor2 on a synthetic straight flight: the chi-square gate drops a 5 km fix."""

    def run_flight(self, mode, bad_frame=40):
        n, start = 80, 10
        en = np.array([[45.0 * k, 0.0] for k in range(n)])
        poses = {"en": en}
        steps = np.diff(en, axis=0)
        fx = {k: en[k] + [2.0, -1.0] for k in range(start + 1, n, 3)}
        fx[bad_frame] = en[bad_frame] + [5000.0, 0.0]
        return rf.run_filter(steps, fx, poses, rf.filter_cfg(5.4), mode, start)

    def test_gate_rejects_far_fix(self):
        rows = self.run_flight("gate")
        bad = [r for r in rows if r["k"] == 40][0]
        self.assertFalse(bad["accepted"])
        self.assertLess(max(r["hpe"] for r in rows), 10.0)

    def test_no_gate_follows_far_fix(self):
        rows = self.run_flight("none")
        self.assertGreater(max(r["hpe"] for r in rows), 1000.0)


@unittest.skipUnless(RESULT.exists(), "run run_fusion.py first")
class ResultsTest(unittest.TestCase):
    """Committed numbers keep the claims the README makes (stdlib only)."""

    @classmethod
    def setUpClass(cls):
        cls.res = json.loads(RESULT.read_text())
        cls.runs = cls.res["runs"]

    def pick(self, **kw):
        return [r for r in self.runs if all(r.get(k) == v for k, v in kw.items())]

    def test_voting_never_produced_a_false_fix(self):
        votes = self.pick(config="vote_fix")
        self.assertTrue(votes)
        self.assertEqual(sum(r["fix_frontend"]["false"] for r in votes), 0)

    def test_loose_gate_single_frame_without_filter_gate_accepts_false_fixes(self):
        r = self.pick(config="single_fix", match_gate="loose", integrity="none", map_stride=8, fix_period=1, yaw_bias_deg=2.0)[0]
        self.assertGreater(r["fixes_accepted_false"], 0)

    def test_chi_square_gate_accepts_no_false_fix(self):
        for r in self.pick(integrity="gate"):
            self.assertEqual(r["fixes_accepted_false"], 0)

    def test_fixes_beat_vo_only(self):
        vo = self.pick(config="vo_only", yaw_bias_deg=2.0)[0]
        fx = self.pick(config="single_fix", match_gate="strict", integrity="gate", map_stride=1, fix_period=1, yaw_bias_deg=2.0)[0]
        self.assertLess(fx["rms_m"] * 5, vo["rms_m"])

    def test_runtime_recorded(self):
        self.assertGreater(self.res["runtime_per_frame_median"]["total_s_stride1"], 0)
        self.assertTrue(math.isfinite(self.res["runtime_per_frame_median"]["total_s_stride1"]))


if __name__ == "__main__":
    unittest.main()
