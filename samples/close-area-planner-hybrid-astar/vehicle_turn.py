"""Turn-rate-limited variant of the arena vehicle (subclass, the arena file is not edited).

The stock arena vehicle (close-area-arena/vehicle.py) is holonomic: the velocity vector can turn
as fast as |a| <= 3 m/s^2 allows (2 rad/s at 1.5 m/s, unbounded near standstill). This variant
also limits how fast the velocity direction turns: the acceleration component normal to the
velocity is clipped to omega_max * |v|, so the turn rate of the velocity vector is <= omega_max.
Below v_free (0.05 m/s) there is no normal limit, so it can start off in any direction from a
near standstill ("turn in place at low speed"). Tangential acceleration and every other limit are
the stock ones. Models a multirotor whose forward-looking sensor must point where it flies and
whose yaw rate is capped, or a conservative attitude controller. Not a measured vehicle model.
"""
from __future__ import annotations

import math

import numpy as np

from arena import mod

Vehicle = mod("vehicle").Vehicle


class TurnLimitedVehicle(Vehicle):
    def __init__(self, *args, omega_max: float = 1.0, v_free: float = 0.05, **kw):
        super().__init__(*args, **kw)
        self.omega_max, self.v_free = omega_max, v_free

    def step(self, vx: float, vy: float, vz: float = 0.0, yaw_rate: float = 0.0) -> None:
        dt = self.dt
        vc = np.array([vx, vy, 0.0 if self.hold_z else vz], dtype=float)
        a = (vc - self.v) / self.tau
        vh = math.hypot(self.v[0], self.v[1])
        if vh > self.v_free:                       # split into tangential + normal, clip the normal part
            tx, ty = self.v[0] / vh, self.v[1] / vh
            at = a[0] * tx + a[1] * ty
            an = -a[0] * ty + a[1] * tx
            an_max = self.omega_max * vh
            an = max(-an_max, min(an_max, an))
            a[0], a[1] = at * tx - an * ty, at * ty + an * tx
        ah = math.hypot(a[0], a[1])
        if ah > self.a_max:
            a[:2] *= self.a_max / ah
        a[2] = max(-self.a_max, min(self.a_max, a[2]))
        self.v += a * dt
        vh = math.hypot(self.v[0], self.v[1])
        if vh > self.v_max:
            self.v[:2] *= self.v_max / vh
        self.v[2] = max(-self.vz_max, min(self.vz_max, self.v[2]))
        self.p += self.v * dt
        r = max(-self.yaw_rate_max, min(self.yaw_rate_max, yaw_rate))
        self.yaw = (self.yaw + r * dt + math.pi) % (2 * math.pi) - math.pi
        self.k += 1
        self.t = self.k * dt
