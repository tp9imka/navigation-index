"""The flight loop: Adapter => NavHealth => Planner => SafetyFilter => send_setpoint at 20 Hz.

- The planner runs in one worker thread with a budget of PLAN_BUDGET_S per tick. If it has not
  answered in time, the loop re-sends the last planner setpoint (keep-alive), still passed
  through the safety filter on the fresh scan. PX4 Offboard, ArduPilot GUIDED and Tello all stop
  or fail safe without a steady setpoint stream, so a slow planner must never stall the stream.
- Health degraded => horizontal speed capped at DEGRADED_SPEED_CAP_MS.
- Health lost => hover (zero velocity), planner not called.
- One JSONL line per tick: t, pose, setpoint, intervened, health, mode (+ source, reasons, plan_ms).

realtime=False runs lockstep, as fast as Python allows: right for MockAdapter, whose
send_setpoint() advances its own clock by 0.05 s. A real driver needs realtime=True.
"""
from __future__ import annotations

import json
import math
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from typing import IO

try:
    from .adapter import Adapter, Pose, Setpoint
    from .health import DEGRADED, LOST, HealthReport, NavHealth
except ImportError:
    from adapter import Adapter, Pose, Setpoint
    from health import DEGRADED, LOST, HealthReport, NavHealth

RATE_HZ = 20.0
DT_S = 1.0 / RATE_HZ
PLAN_BUDGET_S = 0.030        # wall time the loop waits for the planner each tick
DEGRADED_SPEED_CAP_MS = 0.3  # horizontal speed cap while health is degraded
GOAL_TOL_M = 0.20            # estimated 3D distance to goal that counts as arrived
TIMEOUT_S = 60.0             # flight time limit (pose.t)

HOVER = Setpoint(0.0, 0.0, 0.0, 0.0)


@dataclass
class FlightResult:
    arrived: bool
    ticks: int
    t_s: float
    final_dist_m: float      # from the estimate, not truth
    intervened_ticks: int = 0
    keepalive_ticks: int = 0
    planner_errors: int = 0
    overrun_ticks: int = 0   # realtime only: tick took longer than DT_S
    modes: dict[str, int] = field(default_factory=dict)
    health: dict[str, int] = field(default_factory=dict)


def _sp(sp) -> Setpoint:
    """Accept any object with vx, vy, vz, yaw_rate (e.g. the arena's Setpoint)."""
    return Setpoint(float(sp.vx), float(sp.vy), float(sp.vz), float(getattr(sp, "yaw_rate", 0.0)))


def _cap(sp: Setpoint, vmax: float) -> Setpoint:
    n = math.hypot(sp.vx, sp.vy)
    if n <= vmax:
        return sp
    k = vmax / n
    return Setpoint(sp.vx * k, sp.vy * k, sp.vz, sp.yaw_rate)


def _r(v):
    return None if v is None else (round(v, 4) if math.isfinite(v) else str(v))


def _log_line(pose: Pose, sp: Setpoint, intervened: bool, hr: HealthReport, mode: str,
              source: str, plan_ms: float | None) -> str:
    return json.dumps({
        "t": _r(pose.t),
        "pose": {"x": _r(pose.x), "y": _r(pose.y), "z": _r(pose.z), "yaw": _r(pose.yaw),
                 "vx": _r(pose.vx), "vy": _r(pose.vy), "quality": pose.quality,
                 "reset_counter": pose.reset_counter, "sigma_xy": _r(pose.sigma_xy)},
        "setpoint": {"vx": _r(sp.vx), "vy": _r(sp.vy), "vz": _r(sp.vz), "yaw_rate": _r(sp.yaw_rate)},
        "intervened": intervened, "health": hr.state, "mode": mode,
        "source": source, "reasons": hr.reasons, "plan_ms": _r(plan_ms),
    })


def run(adapter: Adapter, planner, safety, goal: tuple[float, float, float], *,
        grid=None, health: NavHealth | None = None, log: IO[str] | None = None,
        timeout_s: float = TIMEOUT_S, budget_s: float = PLAN_BUDGET_S,
        realtime: bool = False, clock=time.monotonic, sleep=time.sleep) -> FlightResult:
    health = health or NavHealth()
    health.reset()
    planner.reset()
    grid_arg = grid if getattr(planner, "uses_grid", False) else None
    res = FlightResult(False, 0, 0.0, math.inf)
    last_plan = HOVER
    pending: Future | None = None
    submitted_at = 0.0
    t0: float | None = None
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="planner")
    next_tick = clock()
    try:
        while True:
            pose, scan = adapter.pose(), adapter.ranges()
            t0 = pose.t if t0 is None else t0
            hr = health.update(pose, clock() if realtime else None)
            dist = math.dist((pose.x, pose.y, pose.z), goal)
            res.final_dist_m, res.t_s = dist, pose.t - t0
            plan_ms = None
            if dist < GOAL_TOL_M:
                mode, source, target = "arrived", "none", HOVER
            elif pose.t - t0 >= timeout_s:
                mode, source, target = "timeout", "none", HOVER
            elif hr.state == LOST:
                mode, source, target = "hover", "none", HOVER
            else:
                if pending is None:
                    pending = pool.submit(planner.step, pose, scan, goal, grid_arg, DT_S)
                    submitted_at, source = clock(), "plan"
                else:
                    source = "late"   # result of a call that overran an earlier tick
                done, _ = wait([pending], timeout=budget_s)
                mode = "capped" if hr.state == DEGRADED else "nominal"
                if done:
                    plan_ms = (clock() - submitted_at) * 1000.0
                    err = pending.exception()
                    if err is None:
                        last_plan = _sp(pending.result())
                    else:
                        res.planner_errors += 1
                        last_plan, mode = HOVER, "planner_error"
                    pending = None
                else:
                    source = "keepalive"
                    res.keepalive_ticks += 1
                target = _cap(last_plan, DEGRADED_SPEED_CAP_MS) if hr.state == DEGRADED else last_plan
            sp, intervened = safety.filter(target, pose, scan, hr)
            adapter.send_setpoint(sp)
            res.ticks += 1
            res.intervened_ticks += int(intervened)
            res.modes[mode] = res.modes.get(mode, 0) + 1
            res.health[hr.state] = res.health.get(hr.state, 0) + 1
            if log is not None:
                log.write(_log_line(pose, sp, intervened, hr, mode, source, plan_ms) + "\n")
            if mode in ("arrived", "timeout"):
                res.arrived = mode == "arrived"
                return res
            if realtime:
                next_tick += DT_S
                delay = next_tick - clock()
                if delay > 0:
                    sleep(delay)
                else:
                    res.overrun_ticks += 1
                    next_tick = clock()
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
