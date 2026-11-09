"""Smoke tests for the flight loop on the mock. Stdlib only: python3 -m unittest -v"""
from __future__ import annotations

import io
import json
import math
import time
import unittest
from dataclasses import replace

from flightloop import (DEGRADED, LOST, OK, GoToGoal, MockAdapter, NavHealth, PassThrough, Planner,
                        RangeStop, SafetyFilter, Setpoint, run)
from flightloop.loop import DEGRADED_SPEED_CAP_MS, DT_S

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


if __name__ == "__main__":
    unittest.main()
