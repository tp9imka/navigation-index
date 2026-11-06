"""Typed boundaries between the pipeline stages.

Every stage talks in a local ENU frame (metres, east/north/up) around a fixed origin.
Swap any implementation (SITL, recorded log, real receiver, EKF, factor graph, TAK,
MAVLink) without touching the others.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class Vec2:
    east: float
    north: float

    def __add__(self, o: "Vec2") -> "Vec2":
        return Vec2(self.east + o.east, self.north + o.north)

    def __sub__(self, o: "Vec2") -> "Vec2":
        return Vec2(self.east - o.east, self.north - o.north)

    def scale(self, k: float) -> "Vec2":
        return Vec2(self.east * k, self.north * k)

    def norm(self) -> float:
        return (self.east ** 2 + self.north ** 2) ** 0.5


@dataclass(frozen=True)
class Epoch:
    """One time step of sensor input. None means the source produced nothing (outage)."""
    t: float
    velocity: Optional[Vec2]        # dead-reckoning velocity (INS, odometry, VIO)
    velocity_sigma: float
    absolute: Optional[Vec2]        # absolute fix (GNSS, visual geoloc, TRN)
    absolute_sigma: float
    absolute_source: str = "gnss"
    truth: Optional[Vec2] = None    # ground truth when the scenario has it; never used by the filter


class Health(str, Enum):
    TRUSTED = "trusted"
    SUSPECT = "suspect"
    EXCLUDED = "excluded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Verdict:
    health: Health
    statistic: Optional[float]      # e.g. normalized innovation squared
    threshold: Optional[float]
    alarm: bool
    reason: str = ""


@dataclass(frozen=True)
class NavState:
    t: float
    position: Vec2
    sigma_h: float                  # 1-sigma horizontal position uncertainty, metres
    sources_used: tuple[str, ...] = field(default_factory=tuple)


@runtime_checkable
class PoseSource(Protocol):
    def epochs(self) -> Iterator[Epoch]: ...


@runtime_checkable
class NavFilter(Protocol):
    def predict(self, epoch: Epoch) -> None: ...
    def innovation(self, epoch: Epoch) -> Optional[tuple[Vec2, float]]:
        """Residual of the absolute fix against the prediction and its variance per axis."""
        ...
    def update(self, epoch: Epoch) -> None: ...
    def state(self, t: float) -> NavState: ...


@runtime_checkable
class IntegrityMonitor(Protocol):
    def check(self, epoch: Epoch, innovation: Optional[tuple[Vec2, float]]) -> Verdict: ...


@runtime_checkable
class Publisher(Protocol):
    def publish(self, state: NavState, verdict: Verdict) -> object: ...
