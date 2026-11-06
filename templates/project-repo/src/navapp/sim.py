"""Synthetic PoseSource: a vehicle with biased odometry and a GNSS fix that can be jammed or spoofed.

Replace with a SITL / log / receiver adapter that yields the same Epoch objects.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterator, Optional

from .interfaces import Epoch, Vec2

SCENARIOS = ("clean", "jam", "spoof")


@dataclass(frozen=True)
class Scenario:
    kind: str = "clean"
    duration_s: float = 180.0
    dt_s: float = 1.0
    attack_onset_s: float = 60.0
    jam_duration_s: float = 60.0
    spoof_drag_mps: float = 1.5      # slow drag-off: offset grows linearly after onset
    gnss_sigma_m: float = 2.0
    odo_sigma_mps: float = 0.1
    odo_bias_mps: float = 0.05
    seed: int = 7

    def onset(self) -> Optional[float]:
        return None if self.kind == "clean" else self.attack_onset_s


class SyntheticSource:
    def __init__(self, scenario: Scenario):
        if scenario.kind not in SCENARIOS:
            raise ValueError(f"unknown scenario {scenario.kind!r}, expected one of {SCENARIOS}")
        self.sc = scenario

    @staticmethod
    def true_velocity(t: float) -> Vec2:
        return Vec2(6.0, 3.0 * math.sin(2 * math.pi * t / 120.0))

    def epochs(self) -> Iterator[Epoch]:
        sc, rng = self.sc, random.Random(self.sc.seed)
        pos, t = Vec2(0.0, 0.0), 0.0
        steps = int(round(sc.duration_s / sc.dt_s))
        for _ in range(steps + 1):
            v = self.true_velocity(t)
            odo = Vec2(v.east + sc.odo_bias_mps + rng.gauss(0, sc.odo_sigma_mps),
                       v.north + sc.odo_bias_mps + rng.gauss(0, sc.odo_sigma_mps))
            fix: Optional[Vec2] = Vec2(pos.east + rng.gauss(0, sc.gnss_sigma_m),
                                       pos.north + rng.gauss(0, sc.gnss_sigma_m))
            attacked = t >= sc.attack_onset_s
            if sc.kind == "jam" and attacked and t < sc.attack_onset_s + sc.jam_duration_s:
                fix = None
            elif sc.kind == "spoof" and attacked:
                fix = fix + Vec2(0.0, sc.spoof_drag_mps * (t - sc.attack_onset_s))
            yield Epoch(t=t, velocity=odo, velocity_sigma=sc.odo_sigma_mps,
                        absolute=fix, absolute_sigma=sc.gnss_sigma_m, truth=pos)
            pos = pos + v.scale(sc.dt_s)
            t += sc.dt_s
