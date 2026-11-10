"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
import json
import os
import sys
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
    def test_wilson(self):
        import explore
        self.assertEqual(explore.wilson(0, 20), (0.0, 16.1))
        self.assertEqual(explore.wilson(20, 20), (83.9, 100.0))

    def test_search_run_matches_published_row(self):
        import explore
        w = explore.A.world.make_world("random", 0, 0)
        nom = explore.nominal_for(w, 0, 0, 5.0)
        self.assertLessEqual(((nom[0] - w.goal[0]) ** 2 + (nom[1] - w.goal[1]) ** 2) ** 0.5, 5.0 + 1e-9)
        self.assertEqual(explore.nominal_for(w, 0, 0, 0.0), (w.goal[0], w.goal[1]))
        row = explore.run_one("lawnmower", "random", 0, 0, 5.0, "ideal")
        ref = next(r for r in json.load(open(os.path.join(HERE, "results", "bench_0.json")))["runs"]
                   if r["arm"] == "lawnmower" and r["family"] == "random" and r["index"] == 0
                   and r["region_m"] == 5.0 and r["preset"] == "ideal")
        for k in ("outcome", "found", "time_to_find_s", "path_length_m", "min_clearance_m"):
            self.assertEqual(row[k], ref[k], k)

    def test_replay_loads_as_world(self):
        from arena import world_json
        path = os.path.join(HERE, "results", "replay_office_0_nominal_frontier_r5_ideal.json")
        doc = json.load(open(path))
        self.assertEqual(doc["schema"], "close-area-replay/2")
        self.assertEqual(doc["world"]["schema"], "close-area-world/1")
        w = world_json.from_json(doc["world"])
        self.assertEqual(world_json.to_json(w), doc["world"])
        self.assertEqual(len(doc["t"]), len(doc["truth"]))
        self.assertTrue(doc["matrix"]["match"])


if __name__ == "__main__":
    unittest.main()
