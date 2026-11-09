"""NavHealth: turn what the estimator reports in Pose into ok / degraded / lost.

Inputs are only Pose fields: quality (0-100, -1 unknown), reset_counter, sigma_xy, t.
Reported sigma is often overconfident, so quality and resets weigh as much as sigma.
Thresholds are proposals, not tuned on flight data. Change the constants, not the logic.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

try:
    from .adapter import Pose
except ImportError:
    from adapter import Pose

OK, DEGRADED, LOST = "ok", "degraded", "lost"
_RANK = {OK: 0, DEGRADED: 1, LOST: 2}

QUALITY_DEGRADED = 50        # quality below this => degraded
QUALITY_LOST = 20            # quality below this => lost
UNKNOWN_QUALITY_STATE = DEGRADED  # quality == -1 (driver does not report it)
SIGMA_DEGRADED_M = 0.30      # reported 1-sigma horizontal above this => degraded
SIGMA_LOST_M = 1.00          # above this => lost
RESET_HOLD_S = 2.0           # stay degraded this long after any reset_counter jump
RESET_WINDOW_S = 10.0        # window for counting resets
RESET_LOST_COUNT = 3         # this many resets inside the window => lost
POSE_STALE_S = 0.5           # pose.t not advancing this long => lost


@dataclass
class HealthReport:
    state: str
    reasons: list[str] = field(default_factory=list)


class NavHealth:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._last_counter: int | None = None
        self._reset_times: deque[float] = deque()
        self._last_t: float | None = None
        self._last_t_change: float | None = None

    def update(self, pose: Pose, now: float | None = None) -> HealthReport:
        """now: clock for the stale check (defaults to pose.t; pass time.monotonic() on hardware)."""
        now = pose.t if now is None else now
        state, reasons = OK, []

        def worse(s: str, why: str) -> None:
            nonlocal state
            reasons.append(why)
            if _RANK[s] > _RANK[state]:
                state = s

        if pose.quality < 0:
            if UNKNOWN_QUALITY_STATE != OK:
                worse(UNKNOWN_QUALITY_STATE, "quality_unknown")
        elif pose.quality < QUALITY_LOST:
            worse(LOST, f"quality={pose.quality}")
        elif pose.quality < QUALITY_DEGRADED:
            worse(DEGRADED, f"quality={pose.quality}")

        if pose.sigma_xy is not None:
            if pose.sigma_xy > SIGMA_LOST_M:
                worse(LOST, f"sigma_xy={pose.sigma_xy:.2f}")
            elif pose.sigma_xy > SIGMA_DEGRADED_M:
                worse(DEGRADED, f"sigma_xy={pose.sigma_xy:.2f}")

        if self._last_counter is not None and pose.reset_counter != self._last_counter:
            self._reset_times.append(now)
        self._last_counter = pose.reset_counter
        while self._reset_times and now - self._reset_times[0] > RESET_WINDOW_S:
            self._reset_times.popleft()
        if len(self._reset_times) >= RESET_LOST_COUNT:
            worse(LOST, f"resets={len(self._reset_times)}/{RESET_WINDOW_S:g}s")
        elif self._reset_times and now - self._reset_times[-1] <= RESET_HOLD_S:
            worse(DEGRADED, "reset_recent")

        if self._last_t is None or pose.t != self._last_t:
            self._last_t, self._last_t_change = pose.t, now
        elif now - self._last_t_change > POSE_STALE_S:
            worse(LOST, "pose_stale")

        return HealthReport(state, reasons)
