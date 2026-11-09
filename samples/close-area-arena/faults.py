"""Named, seeded fault cases for the VIO-like estimator (estimator.py).

A fault is an object the estimator asks at fixed points:

  vio_ok(t)              -> False drops the VIO sample at time t (IMU-only prediction)
  vio_bias(t)            -> (bx, by) m/s added to the VIO velocity at time t
  on_call(truth, est)    -> (dx, dy) step added to the VIO output now, or None
  report_sigma(s, err)   -> sigma_xy the estimator reports (err = true horizontal error)

Cases (all start times drawn from np.random.default_rng([seed, index, 4200 + code])):

  none           no fault (dark zones still apply, they are part of the world)
  jump           0.5 m step in the VIO output, random direction, at the first planner step
                 after an armed time U(1, 10) s where the true clearance is < 1.0 m.
                 reset_counter increments, as a VIO relocalization would report it
  bias           0.05 m/s VIO velocity bias, random direction, for 10 s from U(1, 10) s
  dropout        no VIO samples for 2 s from U(1, 12) s; the filter runs on IMU only.
                 VIO re-initialises after the gap, so the IMU-only error stays
  overconfident  dynamics as `none`, but reported sigma_xy = 0.25 x the true error

`log` records what was armed and when it fired (`fired_t` None = run ended first).
"""
from __future__ import annotations

import math

import numpy as np

CASES = ("none", "jump", "bias", "dropout", "overconfident")
_CODE = {name: i for i, name in enumerate(CASES)}


class Fault:
    name = "none"

    def __init__(self, world, rng):
        self.world = world
        self.rng = rng
        self.log = {"fault": self.name}

    def vio_ok(self, t: float) -> bool:
        return True

    def vio_bias(self, t: float) -> tuple[float, float]:
        return 0.0, 0.0

    def on_call(self, truth, est):
        return None

    def report_sigma(self, sigma: float, err: float) -> float:
        return sigma


class Jump(Fault):
    name = "jump"

    def __init__(self, world, rng, step_m: float = 0.5, near_m: float = 1.0):
        super().__init__(world, rng)
        self.arm_t = float(rng.uniform(1.0, 10.0))
        self.ang = float(rng.uniform(-math.pi, math.pi))
        self.step_m, self.near_m = step_m, near_m
        self.done = False
        self.log.update({"armed_t": round(self.arm_t, 3), "step_m": step_m, "near_m": near_m,
                         "dir_rad": round(self.ang, 4), "fired_t": None, "clearance_at_fire_m": None})

    def on_call(self, truth, est):
        if self.done or truth.t < self.arm_t:
            return None
        c = self.world.clearance(truth.x, truth.y)
        if c >= self.near_m:
            return None
        self.done = True
        self.log["fired_t"] = round(truth.t, 3)
        self.log["clearance_at_fire_m"] = round(c, 4)
        return self.step_m * math.cos(self.ang), self.step_m * math.sin(self.ang)


class Bias(Fault):
    name = "bias"

    def __init__(self, world, rng, bias_mps: float = 0.05, dur_s: float = 10.0):
        super().__init__(world, rng)
        self.t0 = float(rng.uniform(1.0, 10.0))
        self.t1 = self.t0 + dur_s
        ang = float(rng.uniform(-math.pi, math.pi))
        self.b = (bias_mps * math.cos(ang), bias_mps * math.sin(ang))
        self.log.update({"start_t": round(self.t0, 3), "dur_s": dur_s, "bias_mps": bias_mps,
                         "dir_rad": round(ang, 4), "fired_t": None})

    def vio_bias(self, t):
        if self.t0 <= t < self.t1:
            if self.log["fired_t"] is None:
                self.log["fired_t"] = round(t, 3)
            return self.b
        return 0.0, 0.0


class Dropout(Fault):
    name = "dropout"

    def __init__(self, world, rng, dur_s: float = 2.0):
        super().__init__(world, rng)
        self.t0 = float(rng.uniform(1.0, 12.0))
        self.t1 = self.t0 + dur_s
        self.log.update({"start_t": round(self.t0, 3), "dur_s": dur_s, "fired_t": None})

    def vio_ok(self, t):
        if self.t0 <= t < self.t1:
            if self.log["fired_t"] is None:
                self.log["fired_t"] = round(t, 3)
            return False
        return True


class Overconfident(Fault):
    name = "overconfident"

    def __init__(self, world, rng, factor: float = 0.25):
        super().__init__(world, rng)
        self.factor = factor
        self.log.update({"factor": factor, "start_t": 0.0, "fired_t": 0.0})

    def report_sigma(self, sigma, err):
        return self.factor * err


def make(name: str, world, seed: int, index: int) -> Fault:
    """Fresh fault for one layout, seeded per (seed, index, case)."""
    if name not in _CODE:
        raise ValueError(f"unknown fault {name!r}, choose from {CASES}")
    rng = np.random.default_rng([seed, index, 4200 + _CODE[name]])
    cls = {"none": Fault, "jump": Jump, "bias": Bias, "dropout": Dropout,
           "overconfident": Overconfident}[name]
    return cls(world, rng)
