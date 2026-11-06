"""IntegrityMonitor: chi-square tests on filter innovations, detect before fuse.

- single-epoch gate on NIS => SUSPECT (fix not fused this epoch)
- windowed sum of NIS over the last N epochs => EXCLUDED + alarm (catches slow drag-off
  that a single-epoch gate lets the filter absorb)
- fix missing for N epochs => UNAVAILABLE + alarm (jamming / outage)
Exclusion latches until the windowed test passes for READMIT epochs in a row.
"""
from __future__ import annotations

import math
from collections import deque
from typing import Optional

from .interfaces import Epoch, Health, Vec2, Verdict

DOF_PER_EPOCH = 2                  # east + north residuals
EPOCH_FALSE_ALARM_P = 1e-3
WINDOW_FALSE_ALARM_P = 1e-4
WINDOW_EPOCHS = 10
READMIT_EPOCHS = 5
MISSING_EPOCHS_FOR_ALARM = 3


def chi2_sf_even(x: float, dof: int) -> float:
    """Survival function of chi-square with even dof (closed form, stdlib only)."""
    if dof <= 0 or dof % 2:
        raise ValueError("dof must be a positive even integer")
    half, term, total = x / 2.0, 1.0, 1.0
    for i in range(1, dof // 2):
        term *= half / i
        total += term
    return math.exp(-half) * total


def chi2_threshold_even(p_false_alarm: float, dof: int) -> float:
    lo, hi = 0.0, 1.0
    while chi2_sf_even(hi, dof) > p_false_alarm:
        hi *= 2.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if chi2_sf_even(mid, dof) > p_false_alarm else (lo, mid)
    return hi


class ChiSquareMonitor:
    def __init__(self, window: int = WINDOW_EPOCHS, readmit: int = READMIT_EPOCHS,
                 missing_for_alarm: int = MISSING_EPOCHS_FOR_ALARM):
        self.window: deque[float] = deque(maxlen=window)
        self.readmit = readmit
        self.missing_for_alarm = missing_for_alarm
        self.epoch_gate = chi2_threshold_even(EPOCH_FALSE_ALARM_P, DOF_PER_EPOCH)
        self._window_gates = {n: chi2_threshold_even(WINDOW_FALSE_ALARM_P, n * DOF_PER_EPOCH)
                              for n in range(1, window + 1)}
        self.excluded = False
        self.clean_run = 0
        self.missing = 0

    def check(self, epoch: Epoch, innovation: Optional[tuple[Vec2, float]]) -> Verdict:
        if innovation is None:
            self.missing += 1
            alarm = self.missing >= self.missing_for_alarm
            return Verdict(Health.UNAVAILABLE, None, None, alarm,
                           f"no absolute fix for {self.missing} epochs")
        self.missing = 0
        residual, s = innovation
        nis = (residual.east ** 2 + residual.north ** 2) / s
        self.window.append(nis)
        stat, gate = sum(self.window), self._window_gates[len(self.window)]

        if stat > gate:
            self.excluded, self.clean_run = True, 0
        elif self.excluded:
            self.clean_run += 1
            if self.clean_run >= self.readmit:
                self.excluded = False
        if self.excluded:
            return Verdict(Health.EXCLUDED, stat, gate, True, "windowed NIS over gate")
        if nis > self.epoch_gate:
            return Verdict(Health.SUSPECT, nis, self.epoch_gate, False, "single-epoch NIS over gate")
        return Verdict(Health.TRUSTED, stat, gate, False)


class NullMonitor:
    """Baseline that trusts every fix. Run it next to the real monitor for the before/after plot."""

    def check(self, epoch: Epoch, innovation: Optional[tuple[Vec2, float]]) -> Verdict:
        if innovation is None:
            return Verdict(Health.UNAVAILABLE, None, None, False, "no absolute fix")
        return Verdict(Health.TRUSTED, None, None, False, "integrity monitor disabled")
