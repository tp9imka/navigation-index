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


if __name__ == "__main__":
    unittest.main()
