"""50 Hz point-mass multirotor: double integrator with a first-order velocity lag.

a_cmd = (v_cmd - v) / tau, clipped to a_max (horizontal norm, vertical separately), then
v += a dt (clipped to v_max) and p += v dt. Yaw follows the commanded rate, clipped.
With hold_z (default) the 2.5D arena ignores vz and keeps z at z0.
"""
from __future__ import annotations

import math

import numpy as np

HZ = 50
DT = 1.0 / HZ


class Vehicle:
    def __init__(self, x: float = 0.0, y: float = 0.0, z0: float = 1.0, yaw: float = 0.0,
                 tau: float = 0.15, a_max: float = 3.0, v_max: float = 2.0,
                 vz_max: float = 1.0, yaw_rate_max: float = 2.0, radius: float = 0.15,
                 hold_z: bool = True, dt: float = DT):
        self.p = np.array([x, y, z0], dtype=float)
        self.v = np.zeros(3)
        self.yaw = float(yaw)
        self.t = 0.0
        self.k = 0                     # physics step counter; t = k * dt exactly
        self.tau, self.a_max, self.v_max = tau, a_max, v_max
        self.vz_max, self.yaw_rate_max = vz_max, yaw_rate_max
        self.radius, self.hold_z, self.dt = radius, hold_z, dt

    def step(self, vx: float, vy: float, vz: float = 0.0, yaw_rate: float = 0.0) -> None:
        dt = self.dt
        vc = np.array([vx, vy, 0.0 if self.hold_z else vz], dtype=float)
        a = (vc - self.v) / self.tau
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
