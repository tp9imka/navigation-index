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
        # runs needed if every run succeeds: n / (n + 1.96^2) >= bar => 16, 35, 73; "<= 0" never
        self.assertEqual([pack.runs_needed(">=", b) for b in (0.8, 0.9, 0.95)], [16, 35, 73])
        self.assertEqual(pack.runs_needed("<=", 0.05), 73)
        self.assertIsNone(pack.runs_needed("<=", 0))
        self.assertIsNone(pack.runs_needed(">=", 1))
        for b in (0.8, 0.9, 0.95):   # n passes, n - 1 does not
            n = pack.runs_needed(">=", b)
            self.assertGreaterEqual(pack.wilson(n, n)[1], b)
            self.assertLess(pack.wilson(n - 1, n - 1)[1], b)
        g = ev["planners"]["good"]["criteria"]["reached_rate"]
        self.assertEqual((g["runs_needed_all_success"], g["all_success"]), (35, True))
        self.assertEqual(z["gap"], "unprovable")
        # sample-size hint: "short" is 10/10, only n is short; "bad" FAILs => no hint
        s = pack.evaluate(recs, {"reached_rate": ">= 0.9"}, ["short", "bad"], n_worlds=1)
        self.assertEqual(len(s["hints"]), 1)
        self.assertIn("needs 35 distinct runs if every run succeeds (has 10)", s["hints"][0])
        self.assertIn("at least 35 seeds x 1 worlds", s["hints"][0])
        self.assertIsNone(s["planners"]["bad"]["size_hint"])

    def test_count_rules(self):
        import pack

        def rec(planner, i, outcome):
            return {"planner": planner, "world": "w", "seed": i, "outcome": outcome,
                    "time_to_goal_s": 10 + i / 2 if outcome == "reached" else None,
                    "path_length_m": 10 + i / 100, "min_clearance_m": 0.2}
        recs = ([rec("clean", i, "reached") for i in range(15)]
                + [rec("one", i, "collision" if i == 3 else "reached") for i in range(30)]
                + [rec("few", i, "reached") for i in range(9)]
                + [rec("hit", i, "collision" if i < 2 else "reached") for i in range(5)])
        ev = pack.evaluate(recs, {"collisions": "== 0"}, min_runs=15)
        c = {p: e["criteria"]["collisions"] for p, e in ev["planners"].items()}
        # 0 collisions in 15 distinct runs, min 15 => PASS; the rate bound stays 3.84 / 18.84 = 0.20
        self.assertEqual((c["clean"]["verdict"], c["clean"]["k"], c["clean"]["n"]), ("PASS", 0, 15))
        self.assertAlmostEqual(c["clean"]["hi"], 1.96 ** 2 / (15 + 1.96 ** 2), 9)
        self.assertIn("rate <= 0.20 (95 % Wilson bound, not a rate claim)",
                      pack.cell(c["clean"], pack.parse_criteria({"collisions": "== 0"})[0]))
        self.assertEqual(c["one"]["verdict"], "FAIL")          # 1 collision: no n fixes "== 0"
        self.assertEqual(c["few"]["verdict"], "NOT PROVEN")    # 0 in 9 < 15
        self.assertEqual(c["hit"]["verdict"], "FAIL")          # 2 in 5: FAIL before min_runs
        self.assertEqual(ev["exit_code"], 0)
        # per-rule min_runs, and a top-level min_runs; "<= 1"
        ev2 = pack.evaluate(recs, {"collisions": {"rule": "<= 1", "min_runs": 30}})
        v2 = {p: e["criteria"]["collisions"]["verdict"] for p, e in ev2["planners"].items()}
        self.assertEqual(v2, {"clean": "NOT PROVEN", "one": "PASS", "few": "NOT PROVEN", "hit": "FAIL"})
        ev3 = pack.evaluate(recs, {"collision_count": "<= 1", "min_runs": 30})
        self.assertEqual({p: e["criteria"]["collision_count"]["verdict"] for p, e in ev3["planners"].items()}, v2)
        # default min_runs = the planner's own run count
        ev4 = pack.evaluate(recs, {"collisions": "== 0"})
        self.assertEqual(ev4["planners"]["few"]["criteria"]["collisions"]["verdict"], "PASS")
        # identical runs count once toward min_runs, but every collision counts
        dup = [dict(rec("dup", 0, "reached")) for _ in range(15)]
        self.assertEqual(pack.evaluate(dup, {"collisions": "== 0"}, min_runs=15)
                         ["planners"]["dup"]["criteria"]["collisions"]["verdict"], "NOT PROVEN")
        # sample-size hint for a count rule
        h = pack.evaluate(recs, {"collisions": "== 0"}, ["few"], min_runs=15, n_worlds=3)["hints"]
        self.assertEqual(h, ["few: NOT PROVEN only on sample size. collisions == 0 needs 15 distinct runs (has 9)"
                             " => at least 5 seeds x 3 worlds."])
        for bad in ({"collisions": "== 0.5"}, {"collision_rate": "== 0"}, {"collisions": {"rule": "== 0", "n": 3}},
                    {"reached_rate": {"rule": ">= 0.9"}}, {"collisions": "== 0", "min_runs": 0}):
            with self.assertRaises(ValueError, msg=str(bad)):
                pack.parse_criteria(bad)


if __name__ == "__main__":
    unittest.main()
