"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


@unittest.skipUnless(HAVE_DEPS, "needs numpy and scipy (sample venv)")
class SmokeTest(unittest.TestCase):
    def test_rows_match_matrix_and_replay_roundtrips(self):
        import bench
        import export_replays

        for p in bench.DEFAULT_PLANNERS:
            self.assertTrue(bench.available(p), p)
        # glass_office keeps its glass through world_glass.make_any_world (the arena fix)
        w = bench.world_glass.make_any_world("glass_office", 0, 0)
        self.assertGreaterEqual(w.materials["boxes"].count("glass"), 1)
        ref = {(r["planner"], r["family"], r["preset"], r["index"]): r
               for r in json.load(open(os.path.join(HERE, "results", "matrix_0.json")))["runs"]}
        for p, fam, pr in (("straight", "random", "ideal"), ("astar_known", "office", "crazyflie"),
                           ("astar_unknown_f2", "u_trap", "crazyflie")):
            r = bench.run_one(p, fam, pr, 0, 0)
            m = ref[(p, fam, pr, 0)]
            self.assertEqual((r["outcome"], r["min_clearance_m"]), (m["outcome"], m["min_clearance_m"]))
        with tempfile.TemporaryDirectory() as d:
            e = export_replays.export_one("straight", "glass_office", d, ref)
            self.assertTrue(e["matches_matrix"])
            self.assertLessEqual(e["bytes"], export_replays.MAX_BYTES)
            doc = json.load(open(os.path.join(d, e["file"])))
            w2 = export_replays.world_json.from_json(doc["world"])
            self.assertEqual(export_replays.world_json.to_json(w2), doc["world"])
            self.assertEqual(len(doc["t"]), len(doc["truth"]))
            self.assertEqual(len(doc["t"]), len(doc["clearance"]))


class PackCriteriaTest(unittest.TestCase):
    """pack.py criteria evaluator on a fixed records list. Stdlib only, runs under plain python3."""

    def test_criteria_verdicts_and_exit_code(self):
        import pack

        def rec(planner, i, outcome, t=None):
            return {"planner": planner, "world": "w", "seed": i, "outcome": outcome, "time_to_goal_s": t,
                    "path_length_m": 10 + i / 100, "min_clearance_m": 0.2}
        recs = ([rec("good", i, "reached", 10 + i / 2) for i in range(40)]
                + [rec("bad", i, "reached" if i % 2 else "collision", 20.0 + i if i % 2 else None) for i in range(40)]
                + [rec("short", i, "reached", 12 + i) for i in range(10)]
                + [dict(rec("dupes", 0, "reached", 15.0)) for _ in range(40)])     # 40 identical runs = 1 trial
        crit = {"reached_rate": ">= 0.9", "collision_rate": "<= 0.1", "time_to_goal_p50_s": "<= 30"}
        ev = pack.evaluate(recs, crit)
        v = {p: {m: r["verdict"] for m, r in e["criteria"].items()} for p, e in ev["planners"].items()}
        # 40/40: Wilson lower bound 40 / (40 + 1.96^2) = 0.912 >= 0.9; 0/40 upper 0.088 <= 0.1
        self.assertEqual(v["good"], {"reached_rate": "PASS", "collision_rate": "PASS", "time_to_goal_p50_s": "PASS"})
        self.assertAlmostEqual(ev["planners"]["good"]["criteria"]["reached_rate"]["lo"], 40 / (40 + 1.96 ** 2), 9)
        # 20/40: upper 0.65 < 0.9 => FAIL; collisions 20/40 lower 0.35 > 0.1 => FAIL
        self.assertEqual(v["bad"]["reached_rate"], "FAIL")
        self.assertEqual(v["bad"]["collision_rate"], "FAIL")
        # 10/10: lower 0.72 < 0.9 <= upper => NOT PROVEN
        self.assertEqual(v["short"]["reached_rate"], "NOT PROVEN")
        self.assertEqual(ev["planners"]["short"]["verdict"], "NOT PROVEN")
        self.assertEqual(ev["planners"]["dupes"]["criteria"]["reached_rate"]["n"], 1)
        self.assertEqual(v["dupes"]["reached_rate"], "NOT PROVEN")
        self.assertEqual([ev["planners"][p]["verdict"] for p in ("good", "bad")], ["PASS", "FAIL"])
        self.assertEqual(ev["exit_code"], 0)
        self.assertEqual(pack.evaluate([r for r in recs if r["planner"] != "good"], crit)["exit_code"], 1)
        # "<= 0" can never pass with a Wilson upper bound: 0/40 => upper 3.84 / 43.84 > 0
        z = pack.evaluate(recs, {"collision_rate": "<= 0"})["planners"]["good"]["criteria"]["collision_rate"]
        self.assertEqual(z["verdict"], "NOT PROVEN")
        with self.assertRaises(ValueError):
            pack.parse_criteria({"reached_rate": "about 0.9"})


if __name__ == "__main__":
    unittest.main()
