"""Multi-hypothesis relocalization after VIO loss, against a known 2D occupancy grid.

Three pieces, usable without the arena (numpy + scipy only):

ScanMatcher       correlative grid search. Likelihood field = exp(-d^2 / 2 SIGMA_M^2), d = distance
                  from a scan endpoint to the nearest occupied cell (scipy EDT, bilinear lookup).
                  Score of a candidate (x, y) = mean likelihood over the finite returns, in [0, 1].
                  Candidates on a STEP_M lattice in a square window around the current estimate,
                  dropped if they sit closer than MIN_CLEAR_M to an occupied cell. Peaks are kept
                  greedily with SEP_M non-maximum suppression, up to K_MAX = 5, then refined on a
                  STEP_M / 4 lattice. Yaw is taken from the estimator (not searched).

RatioPersistence  the named acceptance rule. Per scan, on the ranked hypotheses:
                    "none"       best score < S_MIN (or fewer than MIN_RETURNS returns): none of
                                 them explains the scan, keep hovering. After NONE_WIDEN scans
                                 the window doubles (up to W_MAX_M), for "truth not in the set"
                    "ambiguous"  best / second < RATIO: keep hovering
                    "pending"    best passes, but has not been best for N_SCANS scans in a row
                                 (same place within ASSOC_M after the odometry delta)
                    "accept"     passes for N_SCANS scans in a row
                  RatioPersistence(s_min=0, ratio=1, n_scans=1) is "commit to the best match at
                  once" (arm b in experiment.py).

RelocPoseSource   PoseSource (arena CONTRACT.md) that wraps the VIO-like estimator. Loss triggers:
                  reset_counter changed, quality fell to 0, or an innovation test (score of the
                  scan at the current estimate < S_INNOV for INNOV_SCANS scans in a row). On a
                  trigger it reports quality 0 (the planner gate in experiment.py hovers on
                  quality 0), waits SETTLE_SCANS for the estimate to settle, then matches every
                  scan until the rule accepts. Accept => re-anchor: offset = hypothesis - raw
                  estimate at that scan, output = raw + offset from then on.

Truth is used only to simulate the range scan (scan_fn) and to log errors for scoring. It never
enters a decision.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import distance_transform_edt, map_coordinates

# ---- matcher ----
SIGMA_M = 0.10        # m, likelihood field width (range noise 0.02 m + 0.1 m grid quantisation)
STEP_M = 0.1          # m, coarse candidate lattice
W0_M = 2.0            # m, half width of the search window around the estimate
W_MAX_M = 4.0         # m, widest window after "none" scans
SEP_M = 0.5           # m, minimum distance between kept hypotheses (= the wrong-commit radius)
K_MAX = 5             # hypotheses kept
KEEP_FLOOR = 0.2      # a peak below this score is not a hypothesis at all
MIN_CLEAR_M = 0.1     # m, candidate must be this far from an occupied cell centre
MIN_RETURNS = 10      # finite returns needed to score a scan
# ---- acceptance rule (tuned on seed 1, see tune.py) ----
S_MIN = 0.6
RATIO = 1.02
N_SCANS = 3
ASSOC_M = 0.3
NONE_WIDEN = 10
# ---- loss detection ----
S_INNOV = 0.5
INNOV_SCANS = 3
SETTLE_SCANS = 2      # 0.2 s at 10 Hz: the EKF absorbs a VIO step over a few 30 Hz samples


@dataclass
class Hypothesis:
    x: float
    y: float
    score: float


class ScanMatcher:
    def __init__(self, grid, sigma: float = SIGMA_M):
        padded = np.pad(grid.occ, 1, constant_values=True)
        self.dist = distance_transform_edt(~padded) * grid.res
        self.lik = np.exp(-0.5 * (self.dist / sigma) ** 2)
        self.res = grid.res
        self.x0 = grid.x0 - grid.res       # padded grid corner
        self.y0 = grid.y0 - grid.res

    def _look(self, arr, x, y, cval):
        fx = (np.asarray(x) - self.x0) / self.res - 0.5
        fy = (np.asarray(y) - self.y0) / self.res - 0.5
        return map_coordinates(arr, [fx.ravel(), fy.ravel()], order=1, mode="constant",
                               cval=cval).reshape(np.shape(fx))

    @staticmethod
    def beams(scan, yaw: float) -> np.ndarray:
        """World-frame endpoint offsets (B, 2) of the finite returns."""
        a = np.asarray(scan.angles, float) + yaw
        d = np.asarray(scan.distances, float)
        ok = np.isfinite(d)
        return np.column_stack([d[ok] * np.cos(a[ok]), d[ok] * np.sin(a[ok])])

    def score(self, b: np.ndarray, cands: np.ndarray) -> np.ndarray:
        """Mean likelihood of endpoints for each candidate (N, 2); -1 for infeasible candidates."""
        px = cands[:, 0:1] + b[None, :, 0]
        py = cands[:, 1:2] + b[None, :, 1]
        s = self._look(self.lik, px, py, 0.0).mean(axis=1)
        clear = self._look(self.dist, cands[:, 0], cands[:, 1], 0.0)
        return np.where(clear >= MIN_CLEAR_M, s, -1.0)

    def score_at(self, scan, yaw: float, xy) -> float | None:
        b = self.beams(scan, yaw)
        if len(b) < MIN_RETURNS:
            return None
        return float(self.score(b, np.asarray(xy, float).reshape(1, 2))[0])

    def hypotheses(self, scan, yaw: float, centre, half_width: float = W0_M,
                   k: int = K_MAX, step: float = STEP_M) -> list[Hypothesis]:
        b = self.beams(scan, yaw)
        if len(b) < MIN_RETURNS:
            return []
        g = np.arange(-half_width, half_width + 1e-9, step)
        X, Y = np.meshgrid(centre[0] + g, centre[1] + g, indexing="ij")
        C = np.column_stack([X.ravel(), Y.ravel()])
        s = self.score(b, C)
        picks: list[np.ndarray] = []
        for i in np.argsort(-s):
            if s[i] < KEEP_FLOOR:
                break
            if all(math.hypot(*(C[i] - p)) >= SEP_M for p in picks):
                picks.append(C[i])
                if len(picks) == k:
                    break
        fine = np.arange(-step, step + 1e-9, step / 4)
        FX, FY = np.meshgrid(fine, fine, indexing="ij")
        F = np.column_stack([FX.ravel(), FY.ravel()])
        out = []
        for p in picks:
            sf = self.score(b, p + F)
            j = int(np.argmax(sf))
            out.append(Hypothesis(float(p[0] + F[j, 0]), float(p[1] + F[j, 1]), float(sf[j])))
        out.sort(key=lambda h: -h.score)
        return out


@dataclass
class RatioPersistence:
    s_min: float = S_MIN
    ratio: float = RATIO
    n_scans: int = N_SCANS
    assoc_m: float = ASSOC_M
    track: tuple | None = None
    count: int = 0

    def reset(self) -> None:
        self.track, self.count = None, 0

    def update(self, hyps: list[Hypothesis], odo_delta=(0.0, 0.0)):
        if not hyps or hyps[0].score < self.s_min:
            self.reset()
            return "none", None
        best = hyps[0]
        second = hyps[1].score if len(hyps) > 1 else 0.0
        if second > 0 and best.score < self.ratio * second:
            self.reset()
            return "ambiguous", None
        if self.track is not None and math.hypot(best.x - self.track[0] - odo_delta[0],
                                                 best.y - self.track[1] - odo_delta[1]) <= self.assoc_m:
            self.count += 1
        else:
            self.count = 1
        self.track = (best.x, best.y)
        return ("accept" if self.count >= self.n_scans else "pending"), best


def single_rule() -> RatioPersistence:
    """Arm b: best match, committed on the first scan."""
    return RatioPersistence(s_min=0.0, ratio=1.0, n_scans=1)


@dataclass
class Event:
    t_trigger: float
    reason: str
    t_end: float | None = None
    result: str = "open"                 # accepted | resumed | no_returns | open (run ended)
    accepted_xy: list | None = None
    err_m: float | None = None           # |accepted - truth| at the accepted scan
    pre_err_m: float | None = None       # |estimate - truth| at the trigger call (a VIO step
                                         # reaches the EKF over the next few samples)
    first_hyps: list = field(default_factory=list)   # [x, y, score, err to truth]
    truth_in_set: bool | None = None     # a first-scan hypothesis within SEP_M of truth
    verdicts: dict = field(default_factory=dict)
    max_window_m: float = W0_M
    last_verdict: str | None = None
    last_returns: int | None = None      # finite returns in the last matched scan

    def to_dict(self):
        r = lambda v: None if v is None else round(float(v), 4)
        return {"t_trigger": r(self.t_trigger), "reason": self.reason, "t_end": r(self.t_end),
                "recover_s": None if self.t_end is None else r(self.t_end - self.t_trigger),
                "result": self.result, "accepted_xy": self.accepted_xy, "err_m": r(self.err_m),
                "pre_err_m": r(self.pre_err_m), "first_hyps": self.first_hyps,
                "truth_in_set": self.truth_in_set, "verdicts": self.verdicts,
                "max_window_m": self.max_window_m, "last_verdict": self.last_verdict,
                "last_returns": self.last_returns}


class RelocPoseSource:
    """mode: "hover_only" (hover while lost, then resume on the raw estimate),
    "single" (rule = single_rule()) or "multi" (RatioPersistence defaults)."""

    def __init__(self, est, grid, scan_fn, mode: str = "multi", rule: RatioPersistence | None = None,
                 innovation: bool = True):
        if mode not in ("hover_only", "single", "multi"):
            raise ValueError(mode)
        self.est, self.scan_fn, self.mode = est, scan_fn, mode
        self.innovation = innovation and mode != "hover_only"
        self.matcher = ScanMatcher(grid)
        self.rule = rule or (single_rule() if mode == "single" else RatioPersistence())
        self.offset = np.zeros(2)
        self.state = "nominal"
        self.settle = 0
        self.window = W0_M
        self.none_run = 0
        self.innov_bad = 0
        self.prev_q = None
        self.prev_reset = 0
        self.prev_raw = None
        self.event: Event | None = None
        self.events: list[Event] = []
        self.errs: list[float] = []          # |output - truth| per call
        self.hover_steps = 0
        self.match_ms: list[float] = []

    def _close(self, t, result):
        self.event.t_end, self.event.result = t, result
        self.event = None
        self.state = "nominal"
        self.innov_bad = 0

    def __call__(self, truth):
        import time
        raw = self.est(truth)
        rxy = np.array([raw.x, raw.y])
        odo = (0.0, 0.0) if self.prev_raw is None else tuple(rxy - self.prev_raw)
        self.prev_raw = rxy
        txy = np.array([truth.x, truth.y])
        scan = self.scan_fn(truth)
        if self.state == "nominal":
            reason = None
            if raw.reset_counter != self.prev_reset:
                reason = "reset_counter"
            elif raw.quality == 0 and self.prev_q not in (None, 0):
                reason = "quality_0"
            elif self.innovation:
                s0 = self.matcher.score_at(scan, raw.yaw, rxy + self.offset)
                self.innov_bad = self.innov_bad + 1 if (s0 is not None and s0 < S_INNOV) else 0
                if self.innov_bad >= INNOV_SCANS:
                    reason = "innovation"
            if reason:
                self.state, self.settle, self.window, self.none_run = "reloc", SETTLE_SCANS, W0_M, 0
                self.rule.reset()
                self.event = Event(truth.t, reason, pre_err_m=float(np.hypot(*(rxy + self.offset - txy))))
                self.events.append(self.event)
        self.prev_q, self.prev_reset = raw.quality, raw.reset_counter

        if self.state == "reloc":
            ev = self.event
            if self.settle > 0:
                self.settle -= 1
            elif self.mode == "hover_only":
                if raw.quality > 0:
                    self._close(truth.t, "resumed")
            else:
                t0 = time.perf_counter()
                hyps = self.matcher.hypotheses(scan, raw.yaw, rxy + self.offset, self.window)
                self.match_ms.append((time.perf_counter() - t0) * 1e3)
                if not ev.first_hyps and hyps:
                    ev.first_hyps = [[round(h.x, 3), round(h.y, 3), round(h.score, 4),
                                      round(float(math.hypot(h.x - truth.x, h.y - truth.y)), 3)] for h in hyps]
                    ev.truth_in_set = any(h[3] <= SEP_M for h in ev.first_hyps)
                verdict, h = self.rule.update(hyps, odo)
                if not hyps and self.mode == "single":
                    verdict = "no_returns"
                ev.verdicts[verdict] = ev.verdicts.get(verdict, 0) + 1
                ev.last_verdict = verdict
                ev.last_returns = int(np.isfinite(np.asarray(scan.distances, float)).sum())
                if verdict == "accept":
                    self.offset = np.array([h.x, h.y]) - rxy
                    ev.accepted_xy = [round(h.x, 3), round(h.y, 3)]
                    ev.err_m = float(math.hypot(h.x - truth.x, h.y - truth.y))
                    self._close(truth.t, "accepted")
                elif verdict == "no_returns":
                    self._close(truth.t, "no_returns")        # single: keep the estimate
                elif verdict == "none":
                    self.none_run += 1
                    if self.none_run >= NONE_WIDEN and self.window < W_MAX_M:
                        self.window = min(2 * self.window, W_MAX_M)
                        ev.max_window_m = self.window
                        self.none_run = 0

        out = rxy + self.offset
        self.errs.append(float(np.hypot(*(out - txy))))
        if self.state == "reloc":
            q = 0
            self.hover_steps += 1
        else:
            q = raw.quality if raw.quality > 0 else 50     # map-anchored, IMU only
        return type(raw)(t=raw.t, x=float(out[0]), y=float(out[1]), z=raw.z, vx=raw.vx, vy=raw.vy,
                         vz=raw.vz, yaw=raw.yaw, quality=q, reset_counter=raw.reset_counter,
                         sigma_xy=raw.sigma_xy)
