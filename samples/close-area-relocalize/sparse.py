"""Spin-stack relocalization for sparse range sensors (adds to relocalize.py, does not edit it).

Problem: ScanMatcher needs MIN_RETURNS = 10 finite returns per scan. A Crazyflie Multi-ranger
gives 4 horizontal beams (front, left, back, right), so one scan never reaches 10 and the matcher
never proposes a pose.

Fix: when VIO is lost, hover and yaw-spin at SPIN_RATE_RAD_S. Every 10 Hz scan is stored with the
raw estimator position and yaw at that instant. The stored scans are stacked into one
pseudo-scan in the body frame of the current pose (the hover point, up to the residual motion
while the vehicle stops): endpoint = (p_k - p_now) + R(yaw_k) * beam_k, then rotated by -yaw_now.
Stacking starts once the raw estimator speed is below STILL_MPS (or STILL_WAIT_S after the
trigger), so the stack is taken from one hover point. Matching starts once the stack has swept MIN_ARC_RAD (a quarter turn: 4 beams 90 deg apart then
cover every bearing once). After that the stack is a sliding window over the last STACK_ARC_RAD
of yaw, and the unchanged ScanMatcher runs on it every scan.

Two changes were needed on top of stacking, both set on seed 1 static poses
(run_sparse.py --tune, results/sparse_tune_seed1.json), seed 0 held out:
- Cone correction (cone_opening). A 27 deg cone reads the closest return in the cone (arena
  model, doc 08 section 2.3). Plotted along the centre ray, a wall then sits short of the map,
  and the median matcher score at the true pose falls to about 0.4, below S_MIN. Over a spin,
  each bearing is covered by several readings; their maximum recovers the wall (grey-scale
  opening). Readings with INF_DROP or more no-return neighbours are dropped (the cone saw the end
  of a wall; open space is behind it).
- Stricter ratio. With about 20 points from 1-2 walls in 3 m, look-alike poses are common:
  SPARSE_RATIO = 1.10 instead of 1.02. S_MIN 0.6 and N_SCANS 3 are unchanged.

Assumptions, named:
- Yaw comes from the IMU / gyro and is good over a spin of a few seconds. In the arena the
  estimator passes truth yaw through, so a gyro scale error or bias is NOT modelled.
- Position deltas between stacked scans come from the raw estimator (VIO deltas after a jump,
  IMU-only prediction during a dropout). Their error is in the sim.
- Doc 08 section 3 says frequent yaw makes the Flow deck drift (yaw flow is not separated from
  translation). The arena estimator does not model that. A real spin would add drift.
- The cone correction inverts the arena's own cone model (k-th closest of 11 sub-rays). A real
  VL53L1x is not exactly that model; the correction is not validated on a real sensor.
- Consecutive stacks share all but one scan, so "3 scans in a row" is weaker evidence on a stack
  than on independent 72-beam scans.

Pieces:
cone_opening         the cone correction.
ScanStack            buffer, sliding window, pseudo-scan.
SpinMixin            pose-source logic shared by the two classes below: owns the estimator and
                     sensor calls, clears the stack while a disambiguating move flies (a new
                     quarter turn is stacked at the end point), keeps the parent's matching
                     off (settle held at 1) until the arc is complete, delays a disambiguating
                     move until 1 s after it, sets `yaw_rate` (spin_rate while lost, else 0)
                     for the gate.
SpinStackPoseSource  RelocPoseSource ("multi" with the sparse rule, or "single") + spin stack.
SpinMovePoseSource   disambiguate.DisambPoseSource (rule + move after a hover timeout) + spin
                     stack. The move chooser predicts a full-circle scan (72 rays, the sensor's
                     max range) at each hypothesis, which is what a completed spin stack sees.
SpinGate             planner gate: while quality is 0 fly src.cmd (or zero) with yaw_rate.

In nominal flight the scan passes through unchanged, so with 4 beams the innovation test
(score at the estimate, needs 10 returns) never runs: only reset_counter and quality 0 trigger.
Truth is used only by the sensor model (scan at the true pose) and for logging errors.
"""
from __future__ import annotations

import math
from collections import deque

import numpy as np

import disambiguate as D
import experiment as X
import relocalize as R
from arena import Setpoint, adapter

SPIN_RATE_RAD_S = 1.0          # rad/s (57 deg/s), 0.1 rad per 10 Hz scan; arena vehicle cap 2 rad/s
MIN_ARC_RAD = math.pi / 2      # match only after a quarter turn: 4 beams => every bearing seen once
STACK_ARC_RAD = math.pi / 2    # sliding window: the last quarter turn (17 scans at 1 rad/s)
STILL_MPS = 0.1               # m/s, raw estimator speed below which a new stack may start (hover, then spin)
STILL_WAIT_S = 1.0             # s after the trigger (or a move), start the stack anyway (IMU-only velocity may read > 0.1)
INF_DROP = 2                   # drop a reading when >= 2 no-return readings cover its bearing (seed-1 sweep)
SPARSE_RATIO = 1.10            # best / second for stacked sparse scans (seed-1 sweep; R.RATIO is 1.02)
SPARSE_S_MIN = R.S_MIN         # 0.6, unchanged


def _wrap(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


def sparse_rule() -> R.RatioPersistence:
    return R.RatioPersistence(s_min=SPARSE_S_MIN, ratio=SPARSE_RATIO)


def cone_opening(bearings: np.ndarray, d: np.ndarray, half_cone: float, inf_drop: int = INF_DROP) -> np.ndarray:
    """Undo the cone's "closest return in the cone" bias over a spin (grey-scale opening).

    A cone beam at bearing b reads m(b) = min of the true range r over [b - h, b + h]. For each
    reading k, r(b_k) >= m(b_j) for every reading j whose cone contains b_k, so
    r_hat(b_k) = max of those m(b_j). That is exact for a flat wall seen across the spin and not
    longer than the truth (up to noise). inf_drop > 0: if that many no-return readings cover b_k,
    reading k is dropped (it is likely the edge of a surface with open space behind). Bearings
    are world-frame, readings from (nearly) one point: parallax from residual motion is ignored."""
    out = np.array(d, float)
    fin = np.isfinite(out)
    if half_cone <= 0 or not fin.any():
        return out
    near = np.abs((bearings[:, None] - bearings[None, :] + math.pi) % (2 * math.pi) - math.pi) <= half_cone + 1e-9
    big = np.where(fin, out, -np.inf)
    for k in np.flatnonzero(fin):
        nb = near[k]
        if inf_drop and int((~fin & nb).sum()) >= inf_drop:
            out[k] = np.inf
        else:
            out[k] = big[nb].max()
    return out


class ScanStack:
    """Scans with the pose they were taken at; pseudo-scan relative to a given pose."""

    def __init__(self, arc_rad: float | None = STACK_ARC_RAD):
        self.arc_rad = arc_rad
        self.buf: deque = deque()

    def reset(self) -> None:
        self.buf.clear()

    def add(self, t: float, xy, yaw: float, scan) -> None:
        self.buf.append((t, np.asarray(xy, float).copy(), float(yaw),
                         np.asarray(scan.angles, float), np.asarray(scan.distances, float)))
        if self.arc_rad is not None:
            while len(self.buf) > 2 and self._swept(1) >= self.arc_rad - 1e-9:
                self.buf.popleft()

    def _swept(self, start: int = 0) -> float:
        y = [b[2] for b in list(self.buf)[start:]]
        return float(sum(abs(_wrap(b - a)) for a, b in zip(y[:-1], y[1:])))

    def swept(self) -> float:
        return self._swept(0)

    def pseudo(self, t: float, xy, yaw: float, max_range: float, half_cone: float = 0.0,
               inf_drop: int = INF_DROP):
        """RangeScan in the body frame of (xy, yaw): every stored finite return as one beam.
        half_cone > 0 applies cone_opening() to the stacked readings first."""
        xy = np.asarray(xy, float)
        if not self.buf:
            ang = dist = np.zeros(0)
        else:
            P = np.concatenate([np.repeat(p[None, :], len(a), 0) for _, p, _, a, _ in self.buf])
            W = np.concatenate([a + y0 for _, _, y0, a, _ in self.buf])
            d = np.concatenate([d for *_, d in self.buf])
            if half_cone > 0:
                d = cone_opening(W, d, half_cone, inf_drop)
            ok = np.isfinite(d)
            ex = P[ok, 0] - xy[0] + d[ok] * np.cos(W[ok])
            ey = P[ok, 1] - xy[1] + d[ok] * np.sin(W[ok])
            ang = np.arctan2(ey, ex) - yaw
            dist = np.hypot(ex, ey)
        return adapter.RangeScan(t=float(t), angles=[float(v) for v in ang],
                                 distances=[float(v) for v in dist], max_range=float(max_range))


class SpinMixin:
    """Pose-source mixin: must precede a RelocPoseSource subclass in the MRO."""

    def _spin_setup(self, est, sensor_fn, max_range: float, half_cone: float, spin_rate: float,
                    stack_arc: float):
        self._real_est, self._sensor = est, sensor_fn
        self.max_range, self.half_cone, self.spin_rate = max_range, half_cone, spin_rate
        self.stack = ScanStack(stack_arc)
        self.min_arc = max(MIN_ARC_RAD, stack_arc)
        self._raw = self._scan = None
        self._stack_ev = None
        self._t_wait = 0.0                        # trigger or end-of-move time of the current stack
        self.arc_done = True
        self.yaw_rate = 0.0
        self.spin_steps = 0
        self.spin_log: dict[int, dict] = {}       # event index => spin facts
        self.est = self._est_cached               # the parent reads the cached estimate

    def _est_cached(self, truth):
        return self._raw

    def _scan_cached(self, truth):
        return self._scan

    def _pseudo(self, t, rxy, yaw):
        return self.stack.pseudo(t, rxy, yaw, self.max_range, self.half_cone)

    def __call__(self, truth):
        raw = self._real_est(truth)
        self._raw = raw
        scan = self._sensor(truth)
        rxy = (raw.x, raw.y)
        self._scan = scan
        if self.state == "reloc":
            if self.event is not self._stack_ev:          # new loss event
                self._stack_ev, self.arc_done, self._t_wait = self.event, False, self.event.t_trigger
                self.stack.reset()
            if getattr(self, "move", None) is not None:   # a move is flying: stack again after it
                self.stack.reset()
                self.arc_done, self._t_wait = False, truth.t
            still = math.hypot(raw.vx, raw.vy) < STILL_MPS or truth.t - self._t_wait >= STILL_WAIT_S - 1e-9
            if self.settle == 0 and getattr(self, "move", None) is None and (self.stack.buf or still):
                self.stack.add(truth.t, rxy, raw.yaw, scan)     # the parent would match this scan
            if self.settle == 0:
                if not self.arc_done and self.stack.swept() >= self.min_arc - 1e-9:
                    self.arc_done = True
                    self._scan = self._pseudo(truth.t, rxy, raw.yaw)
                    lg = self.spin_log[len(self.events) - 1]
                    if lg["arc_done_t"] is None:
                        lg["arc_done_t"] = round(truth.t, 3)
                        lg["first_stack_returns"] = int(np.isfinite(self._scan.distances).sum())
                elif self.arc_done:
                    self._scan = self._pseudo(truth.t, rxy, raw.yaw)
                else:
                    self.settle = 1                       # parent decrements to 0 and skips matching
                    if hasattr(self, "timer_t"):
                        self.timer_t = truth.t            # first move no earlier than 1 s after the arc
        out = super().__call__(truth)
        if self.state == "reloc":                         # the gate yaws for the next planner period
            self.yaw_rate = self.spin_rate
            self.spin_steps += 1
            lg = self.spin_log.setdefault(len(self.events) - 1, {"arc_done_t": None, "first_stack_returns": None,
                                                                  "spin_steps": 0})
            lg["spin_steps"] += 1
        else:
            self.yaw_rate = 0.0
        return out


class SpinStackPoseSource(SpinMixin, R.RelocPoseSource):
    def __init__(self, est, grid, sensor_fn, max_range: float, half_cone: float = 0.0, mode: str = "multi",
                 spin_rate: float = SPIN_RATE_RAD_S, stack_arc: float = STACK_ARC_RAD, innovation: bool = True):
        R.RelocPoseSource.__init__(self, est, grid, self._scan_cached, mode=mode,
                                   rule=sparse_rule() if mode == "multi" else None, innovation=innovation)
        self._spin_setup(est, sensor_fn, max_range, half_cone, spin_rate, stack_arc)


class SpinMovePoseSource(SpinMixin, D.DisambPoseSource):
    def __init__(self, est, grid, sensor_fn, max_range: float, half_cone: float = 0.0, kind: str = "infogain",
                 rng=None, goal=None, spin_rate: float = SPIN_RATE_RAD_S, stack_arc: float = STACK_ARC_RAD,
                 innovation: bool = True):
        D.DisambPoseSource.__init__(self, est, grid, self._scan_cached, kind, rng=rng,
                                    innovation=innovation, goal=goal)
        self.rule = sparse_rule()
        self.chooser = D.MoveChooser(grid, kind, rng, max_range=max_range)
        self.chooser.matcher = self.matcher
        # live = would block or nearly block the sparse ratio test (disambiguate uses 1 / 1.02^2)
        self.chooser.live = lambda hyps: [h for h in hyps if h.score >= hyps[0].score / SPARSE_RATIO ** 2] if hyps else []
        self._spin_setup(est, sensor_fn, max_range, half_cone, spin_rate, stack_arc)


class SpinGate(X.HoverGate):
    """HoverGate that yaws at src.yaw_rate and flies src.cmd (a disambiguating move, if any)
    while the pose source reports quality 0."""

    def __init__(self, inner, src):
        super().__init__(inner)
        self.src = src
        self.name = "spin_gate+" + inner.name

    def step(self, pose, scan, goal, grid, dt):
        if pose.quality == 0:
            self.held = True
            cmd = getattr(self.src, "cmd", None) or (0.0, 0.0)
            return Setpoint(cmd[0], cmd[1], 0.0, getattr(self.src, "yaw_rate", 0.0))
        return super().step(pose, scan, goal, grid, dt)
