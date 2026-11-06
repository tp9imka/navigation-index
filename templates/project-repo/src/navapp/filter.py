"""Minimal NavFilter: dead reckoning on a velocity source, corrected by absolute fixes.

Scalar position state per axis with one shared variance. Stand-in for an EKF or factor
graph; keep the interface, replace the maths.
"""
from __future__ import annotations

import math
from typing import Optional

from .interfaces import Epoch, NavState, Vec2

# Allowance for unmodelled odometry bias, m^2 per second of dead reckoning.
DEFAULT_BIAS_Q_M2PS = 0.25


class DeadReckoningFilter:
    def __init__(self, bias_q_m2ps: float = DEFAULT_BIAS_Q_M2PS):
        self.bias_q = bias_q_m2ps
        self.x: Optional[Vec2] = None
        self.P = math.inf
        self.t: Optional[float] = None
        self.last_sources: tuple[str, ...] = ()

    def predict(self, epoch: Epoch) -> None:
        if self.x is None:
            # First fix is taken on trust: document this assumption in the threat model.
            if epoch.absolute is not None:
                self.x, self.P = epoch.absolute, epoch.absolute_sigma ** 2
            self.t = epoch.t
            return
        dt = epoch.t - self.t
        self.t = epoch.t
        self.last_sources = ()
        if epoch.velocity is None or dt <= 0:
            return
        self.x = self.x + epoch.velocity.scale(dt)
        self.P += (epoch.velocity_sigma * dt) ** 2 + self.bias_q * dt
        self.last_sources = ("dr",)

    def innovation(self, epoch: Epoch) -> Optional[tuple[Vec2, float]]:
        if self.x is None or epoch.absolute is None:
            return None
        return epoch.absolute - self.x, self.P + epoch.absolute_sigma ** 2

    def update(self, epoch: Epoch) -> None:
        innov = self.innovation(epoch)
        if innov is None:
            return
        residual, s = innov
        k = self.P / s
        self.x = self.x + residual.scale(k)
        self.P *= 1.0 - k
        self.last_sources = self.last_sources + (epoch.absolute_source,)

    def state(self, t: float) -> NavState:
        pos = self.x if self.x is not None else Vec2(math.nan, math.nan)
        return NavState(t=t, position=pos, sigma_h=math.sqrt(self.P), sources_used=self.last_sources)
