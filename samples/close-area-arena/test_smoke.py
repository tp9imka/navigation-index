"""Smoke test. Runs in the sample venv; skips under plain python3 without numpy/scipy.

.venv/bin/python -m unittest test_smoke -v
"""
import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


def load_arena():
    """The import recipe from CONTRACT.md: load this folder as package close_area_arena."""
    if "close_area_arena" in sys.modules:
        return sys.modules["close_area_arena"]
    spec = importlib.util.spec_from_file_location(
        "close_area_arena", os.path.join(HERE, "__init__.py"), submodule_search_locations=[HERE])
    mod = importlib.util.module_from_spec(spec)
    sys.modules["close_area_arena"] = mod
    spec.loader.exec_module(mod)
    return mod


@unittest.skipUnless(HAVE_DEPS, "needs numpy and scipy (sample venv)")
class SmokeTest(unittest.TestCase):
    def test_families_run_deterministic_and_scored_on_truth(self):
        load_arena()
        import importlib
        world = importlib.import_module("close_area_arena.world")
        run = importlib.import_module("close_area_arena.run")
        adapter = importlib.import_module("close_area_arena.adapter")

        for fam in world.FAMILIES:
            w = world.make_world(fam, seed=0, index=0)
            blocked = w.grid.inflated(world.RADIUS)
            self.assertIsNotNone(world.bfs_free_path(blocked, w.grid.to_index(0, 0), w.grid.to_index(*w.goal)))

        make = lambda: run.load_planner("straight")
        rows_a, summ_a, _ = run.evaluate(make, "random", layouts=2, seed=3)
        rows_b, summ_b, _ = run.evaluate(make, "random", layouts=2, seed=3)
        strip = lambda rows: [{k: v for k, v in r.items() if not k.startswith("planner_ms")} for r in rows]
        self.assertEqual(strip(rows_a), strip(rows_b))
        self.assertEqual(summ_a, summ_b)
        for r in rows_a:
            self.assertIn(r["outcome"], ("reached", "collision", "stuck", "timeout"))

        # pose_source hook: a 5 m east offset reaches the planner, the scorer still uses truth
        shift = lambda p: adapter.Pose(p.t, p.x + 5.0, p.y, p.z, p.vx, p.vy, p.vz, p.yaw, quality=10)
        rows_s, _, _ = run.evaluate(make, "random", layouts=1, seed=3, make_pose_source=lambda w, s, i: shift)
        self.assertAlmostEqual(rows_s[0]["max_pose_error_m"], 5.0, places=6)
        self.assertNotEqual(strip(rows_s)[0]["path_length_m"], strip(rows_a)[0]["path_length_m"])

    def test_world_from_room_example_spec(self):
        load_arena()
        import importlib
        import json
        wfr = importlib.import_module("close_area_arena.world_from_room")
        with open(os.path.join(HERE, "rooms", "hall_8x6.json")) as fh:
            doc = wfr.room_to_world(json.load(fh))
        self.assertEqual(doc["bounds"], [0.0, 0.0, 8.0, 6.0])
        self.assertEqual(len(doc["obstacles"]), 8)          # 2 wall pieces (door cut), 4 boxes, 2 pillars
        w, problems = wfr.check(doc)                        # world_json.from_json + has_free_path
        self.assertEqual(problems, [])
        self.assertAlmostEqual(w.goal[0], 6.4)               # B moved into the A-origin frame
        self.assertGreater(w.clearance(5.0 - 0.8, 4.05 - 0.8), 0.4)   # door centre is free


if __name__ == "__main__":
    unittest.main()
