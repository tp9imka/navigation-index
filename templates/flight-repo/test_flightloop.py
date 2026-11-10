"""Smoke tests for the flight loop on the mock. Stdlib only: python3 -m unittest -v"""
from __future__ import annotations

import io
import json
import importlib.util
import math
import os
import tempfile
import time
import unittest
from dataclasses import replace

from flightloop import (DEGRADED, LOST, OK, GoToGoal, MockAdapter, NavHealth, PassThrough, Planner,
                        RangeStop, SafetyFilter, Setpoint, run)
from flightloop.loop import ARRIVE_DWELL_S, ARRIVE_WAIT_S, DEGRADED_SPEED_CAP_MS, DT_S
from flightloop.safety_shim import ArmShim, accepts_nav_health

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.environ.get("BENCH_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-benchmark"))
ARENA_DIR = os.environ.get("ARENA_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-arena"))
HAVE_SCI = all(importlib.util.find_spec(m) is not None for m in ("numpy", "scipy"))
OPEN = ((0.0, 0.0, 1.0), (5.0, 3.0, 1.0))
BLOCKED = ((0.0, 0.0, 1.0), (6.0, 0.0, 1.0))


class FaultyPose:
    """Wraps MockAdapter; after t_fault the reported pose gets the given field values."""
    def __init__(self, ad: MockAdapter, t_fault: float, **fields) -> None:
        self.ad, self.t_fault, self.fields = ad, t_fault, fields

    def pose(self):
        p = self.ad.pose()
        return replace(p, **self.fields) if p.t >= self.t_fault else p

    def ranges(self):
        return self.ad.ranges()

    def send_setpoint(self, sp):
        self.ad.send_setpoint(sp)


class SlowPlanner(GoToGoal):
    name = "slow"

    def step(self, *a):
        time.sleep(0.1)
        return super().step(*a)


def fly(start_goal, planner=None, safety=None, wrap=None, **kw):
    ad = MockAdapter(start=start_goal[0])
    log = io.StringIO()
    r = run(wrap(ad) if wrap else ad, planner or GoToGoal(), safety or RangeStop(), start_goal[1],
            log=log, **kw)
    return ad, r, [json.loads(line) for line in log.getvalue().splitlines()]


class FlightLoop(unittest.TestCase):
    def test_protocols(self):
        self.assertIsInstance(GoToGoal(), Planner)
        self.assertIsInstance(RangeStop(), SafetyFilter)
        self.assertIsInstance(PassThrough(), SafetyFilter)

    def test_open_reaches_and_logs_every_tick(self):
        ad, r, lines = fly(OPEN)
        self.assertTrue(r.arrived)
        self.assertFalse(ad.collided)
        self.assertEqual(len(lines), r.ticks)
        for f in ("t", "pose", "setpoint", "intervened", "health", "mode"):
            self.assertIn(f, lines[0])
        self.assertEqual(lines[-1]["mode"], "arrived")

    def test_safety_filter_catches_blind_planner(self):
        blind = lambda: GoToGoal(stop_dist=0.0)
        ad, r, _ = fly(BLOCKED, blind(), RangeStop(), timeout_s=10.0)
        self.assertFalse(ad.collided)
        self.assertGreater(r.intervened_ticks, 0)
        ad, r, _ = fly(BLOCKED, blind(), PassThrough(), timeout_s=10.0)
        self.assertTrue(ad.collided)

    def test_keepalive_when_planner_overruns(self):
        ad, r, lines = fly(OPEN, SlowPlanner(), timeout_s=3.0)
        self.assertGreater(r.keepalive_ticks, 0)
        self.assertAlmostEqual(ad.t, r.ticks * DT_S, places=6)   # one setpoint sent per tick
        self.assertIn("keepalive", {ln["source"] for ln in lines})

    def test_degraded_caps_speed_and_lost_hovers(self):
        _, r, lines = fly(OPEN, wrap=lambda ad: FaultyPose(ad, 1.0, quality=40), timeout_s=5.0)
        late = [ln for ln in lines[:-1] if ln["t"] >= 1.0]   # last tick is "timeout"
        self.assertTrue(all(ln["health"] == DEGRADED and ln["mode"] == "capped" for ln in late))
        self.assertTrue(all(math.hypot(ln["setpoint"]["vx"], ln["setpoint"]["vy"])
                            <= DEGRADED_SPEED_CAP_MS + 1e-9 for ln in late))
        _, r, lines = fly(OPEN, wrap=lambda ad: FaultyPose(ad, 1.0, quality=5), timeout_s=5.0)
        late = [ln for ln in lines[:-1] if ln["t"] >= 1.0]   # last tick is "timeout"
        self.assertTrue(all(ln["health"] == LOST and ln["mode"] == "hover" for ln in late))
        self.assertTrue(all(ln["setpoint"]["vx"] == 0.0 == ln["setpoint"]["vy"] for ln in late))

    def test_health_reset_jumps(self):
        h, mk = NavHealth(), MockAdapter().pose
        p = replace(mk(), quality=100, sigma_xy=0.05)
        self.assertEqual(h.update(p).state, OK)
        states = [h.update(replace(p, t=t, reset_counter=i)).state
                  for i, t in enumerate([1.0, 4.0, 5.0, 6.0], start=1)]
        self.assertEqual(states, [DEGRADED, DEGRADED, LOST, LOST])
        self.assertEqual(h.update(replace(p, t=30.0, reset_counter=4)).state, OK)
        self.assertEqual(h.update(replace(p, t=31.0, reset_counter=4, sigma_xy=2.0)).state, LOST)

    def test_arrival_gated_on_health(self):
        # degraded the whole flight: reaches B on the estimate, hovers, must not say "arrived"
        _, r, lines = fly(OPEN, wrap=lambda ad: FaultyPose(ad, 0.0, quality=40))
        self.assertFalse(r.arrived)
        self.assertEqual(r.outcome, "unconfirmed")
        self.assertEqual(lines[-1]["mode"], "unconfirmed")
        wait = [ln for ln in lines if ln["mode"] == "arrive_wait"]
        self.assertGreaterEqual(len(wait) * DT_S, ARRIVE_WAIT_S - 2 * DT_S)
        self.assertTrue(all(ln["setpoint"]["vx"] == 0.0 == ln["setpoint"]["vy"] for ln in wait))
        # healthy: arrived only after ARRIVE_DWELL_S of ok inside the tolerance
        _, r, lines = fly(OPEN)
        self.assertEqual(r.outcome, "arrived")
        dwell = [ln for ln in lines if ln["mode"] == "arrive_dwell"]
        self.assertGreaterEqual(len(dwell) * DT_S, ARRIVE_DWELL_S - DT_S)

    def test_shim_passes_nav_health_only_to_aware_arms(self):
        class Plain:      # F0-F2 signature
            def filter(self, setpoint, pose, scan, map_obstacles, health, dt):
                return setpoint, False

        class Aware:
            got = None

            def filter(self, setpoint, pose, scan, map_obstacles, health, dt, nav_health=None):
                Aware.got = nav_health
                return setpoint, False

        p, rep = MockAdapter().pose(), NavHealth().update(MockAdapter().pose())
        for arm, aware in ((Plain(), False), (Aware(), True)):
            shim = ArmShim.__new__(ArmShim)   # skip loading filters.py (numpy)
            shim.arm, shim.world, shim.dt = arm, None, DT_S
            shim.health_aware = accepts_nav_health(arm)
            self.assertEqual(shim.health_aware, aware)
            shim.filter(Setpoint(0.1, 0.0, 0.0, 0.0), p, None, rep)
        self.assertIs(Aware.got, rep)

    def test_reloc_mode_hovers_moves_and_resumes(self):
        class FakeReloc:      # relocalizing for t in [1, 2), move cmd in [1.5, 2)
            def __init__(self, ad, until=2.0):
                self.ad, self.until = ad, until

            @property
            def relocalizing(self):
                return 1.0 <= self.ad.t < self.until

            @property
            def cmd(self):
                return (0.2, 0.0) if 1.5 <= self.ad.t < self.until else None

        for until, outcome in ((2.0, "arrived"), (math.inf, "timeout")):
            ad = MockAdapter(start=OPEN[0])
            log = io.StringIO()
            r = run(ad, GoToGoal(), PassThrough(), OPEN[1], log=log, timeout_s=15.0,
                    reloc=FakeReloc(ad, until))
            lines = [json.loads(x) for x in log.getvalue().splitlines()]
            self.assertEqual(r.outcome, outcome)
            hov = [ln for ln in lines if ln["mode"] == "reloc_hover"]
            mov = [ln for ln in lines if ln["mode"] == "reloc_move"]
            self.assertGreaterEqual(len(hov), 9)
            self.assertGreaterEqual(len(mov), 9)
            self.assertTrue(all(ln["setpoint"]["vx"] == 0.0 == ln["setpoint"]["vy"] for ln in hov))
            self.assertTrue(all(ln["setpoint"]["vx"] == 0.2 and ln["setpoint"]["vy"] == 0.0 for ln in mov))
            if until == math.inf:   # never trusts the estimate while relocalizing: no arrival
                self.assertFalse({"arrive_dwell", "arrive_wait", "arrived"} & set(r.modes))

    def test_odometry_counter_increments_once_per_reanchor(self):
        from flightloop.reloc_shim import OdometryStream
        p = replace(MockAdapter().pose(), x=1.0, y=2.0, z=1.0, quality=80, sigma_xy=0.1)
        st = OdometryStream()
        seq = [(False, 0), (True, 0), (True, 0), (False, 1), (False, 1), (True, 1), (False, 2)]
        msgs = [st.emit(replace(p, t=0.1 * i), rel, n) for i, (rel, n) in enumerate(seq)]
        self.assertEqual([m["reset_counter"] for m in msgs], [0, 0, 0, 1, 1, 1, 2])
        self.assertEqual([m["quality"] for m in msgs], [80, 0, 0, 80, 80, 0, 80])
        self.assertEqual(st.increments, [0.3, 0.6])
        self.assertEqual((msgs[0]["x"], msgs[0]["y"], msgs[0]["z"]), (2.0, 1.0, -1.0))   # ENU => NED


@unittest.skipUnless(HAVE_SCI and os.path.exists(os.path.join(BENCH_DIR, "bench.py"))
                     and os.path.exists(os.path.join(ARENA_DIR, "__init__.py")),
                     "needs numpy + scipy (make venv) and the hub's close-area-benchmark (BENCH_DIR)")
class BenchPlanner(unittest.TestCase):
    def test_bench_straight_flies_in_a_world_file(self):
        """bench:straight via bench.py PLANNERS, flown 2 s in a world: adapter built from a JSON file."""
        import importlib
        from flightloop import bench_planner
        from flightloop.arena_adapter import ArenaAdapter
        gen = ArenaAdapter(ARENA_DIR, "random", 0, 0)
        wj = importlib.import_module("close_area_arena.world_json")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "random_0.json")
            with open(path, "w") as fh:
                json.dump(wj.to_json(gen.world), fh)
            ad = ArenaAdapter.from_spec(f"world:{path}", ARENA_DIR)
        for got, want in zip(ad.goal[:2], gen.goal[:2]):     # world_json rounds to 4 decimals
            self.assertAlmostEqual(got, want, places=4)
        self.assertEqual(ad.world.grid.occ.shape, gen.world.grid.occ.shape)
        rows = {r["id"]: r for r in bench_planner.describe(BENCH_DIR)}
        self.assertGreaterEqual(len(rows), 18)
        self.assertFalse(rows["straight"]["needs_world"])
        self.assertTrue(rows["dstar_lite"]["needs_world"])
        pl, arm = bench_planner.make("straight", BENCH_DIR, ad.world)
        self.assertIsNone(arm)
        log = io.StringIO()
        r = run(ad, pl, PassThrough(), ad.goal, grid=ad.grid, log=log, timeout_s=2.0)
        self.assertEqual(r.planner_errors, 0)
        self.assertGreater(ad.vehicle.p[0] ** 2 + ad.vehicle.p[1] ** 2, 0.5 ** 2)   # it moved
        with self.assertRaises(ValueError):
            bench_planner.make("no_such_planner", BENCH_DIR, ad.world)


if __name__ == "__main__":
    unittest.main()
