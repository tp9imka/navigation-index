"""Per-run score, always on the truth trajectory (never on the pose the planner was given).

Definitions (fixed so every approach in the hub is compared the same way):
  reached     truth within GOAL_TOL (0.3 m) of B at some time; time_to_goal_s = first such time
  collision   truth clearance < vehicle radius at some time before reaching B
              (clearance = distance from the vehicle centre to the nearest obstacle or wall surface)
  stuck       at some time t >= STUCK_WINDOW_S before reaching B, |p(t) - p(t - 10 s)| < 0.2 m
  timeout     none of the above within the run's max time
  outcome     the first event in time: "reached" | "collision" | "stuck" | "timeout"
  min_clearance_m  minimum clearance over the run up to its end (centre to surface)
  path_length_m    sum of truth segment lengths up to the end of the run
"""
from __future__ import annotations

import numpy as np

GOAL_TOL = 0.3
STUCK_WINDOW_S = 10.0
STUCK_DIST = 0.2

FIELDS = ("outcome", "reached", "collision", "stuck", "timeout", "time_to_goal_s",
          "min_clearance_m", "path_length_m", "duration_s")


def first_events(t, xy, clearance, goal, radius):
    """Index of the first reach, collision and stuck sample (or None each)."""
    t = np.asarray(t, float)
    xy = np.asarray(xy, float)
    d_goal = np.hypot(xy[:, 0] - goal[0], xy[:, 1] - goal[1])
    reach = np.flatnonzero(d_goal <= GOAL_TOL)
    coll = np.flatnonzero(np.asarray(clearance) < radius)
    stuck = None
    lag = np.searchsorted(t, t - STUCK_WINDOW_S + 1e-9)       # index of the sample 10 s back
    ok = t >= STUCK_WINDOW_S - 1e-9
    if ok.any():
        disp = np.hypot(xy[:, 0] - xy[lag, 0], xy[:, 1] - xy[lag, 1])
        s = np.flatnonzero(ok & (disp < STUCK_DIST))
        stuck = int(s[0]) if len(s) else None
    return (int(reach[0]) if len(reach) else None,
            int(coll[0]) if len(coll) else None, stuck)


def score(t, xy, world, goal, radius) -> dict:
    """Score a truth trajectory t (N,), xy (N, 2) recorded at the physics rate."""
    t = np.asarray(t, float)
    xy = np.asarray(xy, float)
    clr = world.sdf(xy)
    i_r, i_c, i_s = first_events(t, xy, clr, goal, radius)
    cands = [(i, name) for i, name in ((i_r, "reached"), (i_c, "collision"), (i_s, "stuck")) if i is not None]
    if cands:
        end, outcome = min(cands)          # ties at the same sample: reached < collision < stuck
    else:
        end, outcome = len(t) - 1, "timeout"
    seg = np.hypot(np.diff(xy[: end + 1, 0]), np.diff(xy[: end + 1, 1]))
    return {
        "outcome": outcome,
        "reached": outcome == "reached",
        "collision": outcome == "collision",
        "stuck": outcome == "stuck",
        "timeout": outcome == "timeout",
        "time_to_goal_s": round(float(t[end]), 3) if outcome == "reached" else None,
        "min_clearance_m": round(float(clr[: end + 1].min()), 4),
        "path_length_m": round(float(seg.sum()), 3),
        "duration_s": round(float(t[end]), 3),
    }


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    pct = lambda k: round(100.0 * sum(r[k] for r in rows) / n, 1) if n else None
    times = [r["time_to_goal_s"] for r in rows if r["reached"]]
    return {
        "n": n,
        "reached_pct": pct("reached"),
        "collision_pct": pct("collision"),
        "stuck_pct": pct("stuck"),
        "timeout_pct": pct("timeout"),
        "median_time_to_goal_s": round(float(np.median(times)), 2) if times else None,
        "median_min_clearance_m": round(float(np.median([r["min_clearance_m"] for r in rows])), 3) if n else None,
        "median_path_length_m": round(float(np.median([r["path_length_m"] for r in rows])), 2) if n else None,
    }
