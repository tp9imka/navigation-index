"""Rolling-submap relocalization for sparse range sensors (adds to relocalize.py, does not edit it).

Problem (README sections "Relocalization with a 4-beam sensor" and "AF-MCL baseline"): a Crazyflie-like Multi-ranger gives 4 beams per scan. One scan
never reaches ScanMatcher's MIN_RETURNS = 10. The spin-stack arm (sparse.py) hovers and yaws to
collect returns after the loss, and reached 36-64 %. AF-MCL (mcl.py) failed too.

Idea: collect the returns while flying, before VIO is lost. Keep a rolling local submap of range
returns in the odometry frame (the raw estimator frame). On loss, match that submap (dozens to
hundreds of returns) against the map, instead of one 4-beam scan.

Pieces (numpy + scipy, map only, truth never enters a decision):

Submap             scans with the raw-frame position and yaw they were taken at. Window: the last
                   WINDOW_S seconds of nominal flight, at most MAX_POINTS finite returns (oldest
                   scans dropped first). A scan is added only if the vehicle moved >= KEY_MOVE_M or
                   yawed >= KEY_YAW_RAD since the last added scan, so a hover does not fill the
                   window with copies of 4 points. While lost, the time window is frozen (only
                   MAX_POINTS trims): the pre-loss returns are the evidence.
                   Drift budget: the arena VIO drifts 0.047 m / sqrt(m) of travel (estimator.py,
                   from OpenVINS RPE 1.5 % over 10 m). The planner flies at most about 1 m/s, so a
                   6 s window spans <= 6 m: 0.12 m (1 sigma) of relative drift inside the window
                   on nominal VIO. In a dark zone drift is 4x plus a time walk (0.47 m over 6 m,
                   not within budget); that is measured, not hidden (run_submap.py --tune).
cone_opening_local the sparse.py cone correction (grey-scale opening over readings whose cone covers
                   the bearing) restricted to readings taken within PARALLAX_M of each other. In a
                   moving submap readings come from different points, so sparse.cone_opening's
                   "one point" assumption only holds locally.
InertialBridge     dead reckoning across the loss: starts at the raw estimate and EKF velocity at
                   the trigger call (the arena EKF has not absorbed a VIO step yet at that call),
                   then integrates a simulated accelerometer with the arena estimator's own IMU
                   noise (bias N(0, 0.03 m/s^2) per axis per run, white 0.05 m/s^2 at 50 Hz). The
                   arena estimator does not expose its IMU samples, so the accelerometer is
                   simulated here from truth velocity differences: a sensor model, like the range
                   fan. On a real flight controller this is the IMU it already has.
                   Why: a VIO jump moves the raw frame by an unknown step over about 0.5 s while
                   the EKF absorbs it. Returns before and after would sit in two frames. Scans
                   taken while settling are placed at the bridge position, and once the raw frame
                   has settled (raw delta agrees with the bridge delta within SETTLE_TOL_M for
                   SETTLE_N scans) the whole submap is shifted into the new raw frame. The bridge
                   runs for <= SETTLE_MAX_S, so IMU-only drift stays at centimetres.
                   The bridge only links the submap across the step. Where the vehicle is in the
                   map is decided by the match: the search window (+-2 m, widened to +-4 m) is
                   centred on the pre-loss estimate and covers both the jumped and unjumped pose.
SubmapPoseSource   PoseSource (arena CONTRACT.md) that wraps the estimator. Triggers: reset_counter
                   changed, quality fell to 0, or a submap innovation test (score of the submap at
                   the estimate < S_INNOV for INNOV_SCANS scans; it runs in nominal flight, which
                   the 4-beam spin arm could not do). While lost it reports quality 0 (the gate
                   hovers). States: nominal => bridge (settling) => match (every scan, same
                   ScanMatcher and RatioPersistence with the sparse ratio 1.10; verdicts none /
                   ambiguous / pending / accept) => nominal. Accept => offset = hypothesis - raw.
                   moves=True adds the info-gain move from disambiguate.py after HOVER_TIMEOUT_S
                   without an accept (up to MAX_MOVES), flown in the raw frame; its returns are
                   added to the submap.
Tracking          in nominal flight (track=True), every TRACK_EVERY scans: search the submap in a
                   +-TRACK_W_M window around the estimate; if the best passes S_MIN and beats the
                   score at the estimate by TRACK_MARGIN, move the anchor TRACK_ALPHA of the way to
                   it. Continuous map-based drift correction, not a relocalization (not counted as
                   a commit). Added after seed-1 dev flights showed collisions on 0.2-0.9 m dark-zone
                   drift long after a correct accept.
SubmapMoveChooser  disambiguate.MoveChooser with the prediction changed to what the move adds to a
                   submap: the 4 beams at N_ALONG points along the move, not one 72-ray scan at the
                   end. Same info-gain utility, same clearance check, same tie-break.
"""
from __future__ import annotations

import math
from collections import deque

import numpy as np

import disambiguate as D
import relocalize as R
import sparse as S
from arena import adapter

# ---- submap window ----
WINDOW_S = 6.0            # s of nominal flight kept (seed-1 sweep, run_submap.py --tune)
MAX_POINTS = 300          # finite returns kept, oldest scans dropped first
KEY_MOVE_M = 0.05         # m moved since the last added scan
KEY_YAW_RAD = 0.05        # rad yawed since the last added scan
PARALLAX_M = 0.2          # m, cone opening only among readings taken this close together
# ---- bridge / settle ----
ACC_BIAS = 0.03           # m/s^2 per axis per run (estimator.py ACC_BIAS)
ACC_NOISE = 0.05          # m/s^2 white per 50 Hz sample (estimator.py ACC_NOISE)
IMU_HZ = 50
SETTLE_TOL_M = 0.02       # m per 0.1 s: raw delta vs bridge delta
SETTLE_N = 3              # scans in a row within SETTLE_TOL_M
SETTLE_MIN = 2            # scans, at least (relocalize.SETTLE_SCANS)
SETTLE_MAX_S = 2.0        # s, then shift anyway (logged)
# ---- rule ----
SUBMAP_RATIO = S.SPARSE_RATIO     # 1.10 (stacked sparse returns; checked by --tune)
SUBMAP_S_MIN = R.S_MIN            # 0.6
S_INNOV = R.S_INNOV               # 0.5
INNOV_SCANS = R.INNOV_SCANS       # 3
# ---- nominal tracking (map-based drift correction while VIO is fine) ----
TRACK_EVERY = 2           # scans (5 Hz)
TRACK_W_M = 0.3           # m, half width of the local search around the estimate
TRACK_STEP_M = 0.05       # m
TRACK_MARGIN = 0.03       # best must beat the score at the estimate by this much
TRACK_ALPHA = 0.5         # fraction of the correction applied per update
# ---- moves ----
N_ALONG = 5               # predicted scan points along a move (fractions 0.2 .. 1.0)


def submap_rule() -> R.RatioPersistence:
    return R.RatioPersistence(s_min=SUBMAP_S_MIN, ratio=SUBMAP_RATIO)


def cone_opening_local(P: np.ndarray, W: np.ndarray, d: np.ndarray, half_cone: float,
                       parallax_m: float = PARALLAX_M, inf_drop: int = S.INF_DROP) -> np.ndarray:
    """sparse.cone_opening over readings j taken within parallax_m of reading k (P = positions,
    W = world bearings, d = ranges with inf for no return)."""
    out = np.array(d, float)
    fin = np.isfinite(out)
    if half_cone <= 0 or not fin.any():
        return out
    nb = np.abs((W[:, None] - W[None, :] + math.pi) % (2 * math.pi) - math.pi) <= half_cone + 1e-9
    dp = np.hypot(P[:, None, 0] - P[None, :, 0], P[:, None, 1] - P[None, :, 1])
    nb &= dp <= parallax_m + 1e-9
    big = np.where(fin, out, -np.inf)
    r = np.where(nb, big[None, :], -np.inf).max(axis=1)
    if inf_drop:
        n_inf = (nb & ~fin[None, :]).sum(axis=1)
        keep = fin & (n_inf < inf_drop)
    else:
        keep = fin
    return np.where(keep, r, np.inf)


class Submap:
    def __init__(self, window_s: float = WINDOW_S, max_points: int = MAX_POINTS):
        self.window_s, self.max_points = window_s, max_points
        self.buf: deque = deque()      # (t, xy (2,), yaw, angles, dists)
        self.n_fin = 0

    def reset(self) -> None:
        self.buf.clear()
        self.n_fin = 0

    def maybe_add(self, t: float, xy, yaw: float, scan) -> bool:
        xy = np.asarray(xy, float)
        if self.buf:
            _, p, y0, _, _ = self.buf[-1]
            if (math.hypot(*(xy - p)) < KEY_MOVE_M
                    and abs((yaw - y0 + math.pi) % (2 * math.pi) - math.pi) < KEY_YAW_RAD):
                return False
        d = np.asarray(scan.distances, float)
        self.buf.append((float(t), xy.copy(), float(yaw), np.asarray(scan.angles, float), d))
        self.n_fin += int(np.isfinite(d).sum())
        self._cap()
        return True

    def _pop(self) -> None:
        self.n_fin -= int(np.isfinite(self.buf.popleft()[4]).sum())

    def _cap(self) -> None:
        while len(self.buf) > 1 and self.n_fin > self.max_points:
            self._pop()

    def trim(self, t_now: float) -> None:
        while len(self.buf) > 1 and self.buf[0][0] < t_now - self.window_s - 1e-9:
            self._pop()

    def shift(self, dxy) -> None:
        dxy = np.asarray(dxy, float)
        for b in self.buf:
            b[1][:] += dxy

    def readings(self, xy):
        """All stored readings (no-returns included): positions relative to xy, world bearings, ranges."""
        if not self.buf:
            return np.zeros((0, 2)), np.zeros(0), np.zeros(0)
        P = np.concatenate([np.repeat(p[None, :], len(a), 0) for _, p, _, a, _ in self.buf])
        W = np.concatenate([a + y0 for _, _, y0, a, _ in self.buf])
        d = np.concatenate([d for *_, d in self.buf])
        return P - np.asarray(xy, float)[None, :], W, d

    def span_s(self) -> float:
        return self.buf[-1][0] - self.buf[0][0] if self.buf else 0.0

    def pseudo(self, t: float, xy, yaw: float, max_range: float, half_cone: float = 0.0, arc_sub: int = 0):
        """RangeScan in the body frame of (xy, yaw): every stored finite return as one beam,
        after cone_opening_local when half_cone > 0. arc_sub > 0 (extra "arc" scoring): no
        opening; each reading becomes arc_sub beams spread over its cone at the measured range,
        reading-major, for ArcScanMatcher (fewer than MIN_RETURNS readings => empty scan)."""
        xy = np.asarray(xy, float)
        if not self.buf:
            ang = dist = np.zeros(0)
        else:
            P = np.concatenate([np.repeat(p[None, :], len(a), 0) for _, p, _, a, _ in self.buf])
            W = np.concatenate([a + y0 for _, _, y0, a, _ in self.buf])
            d = np.concatenate([d for *_, d in self.buf])
            if arc_sub and half_cone > 0:
                ok = np.isfinite(d)
                if ok.sum() < R.MIN_RETURNS:
                    ok[:] = False
                sub = np.linspace(-half_cone, half_cone, arc_sub)
                P = np.repeat(P[ok], arc_sub, 0)
                W = (W[ok][:, None] + sub[None, :]).ravel()
                d = np.repeat(d[ok], arc_sub)
            elif half_cone > 0:
                d = cone_opening_local(P, W, d, half_cone)
            ok = np.isfinite(d)
            ex = P[ok, 0] - xy[0] + d[ok] * np.cos(W[ok])
            ey = P[ok, 1] - xy[1] + d[ok] * np.sin(W[ok])
            ang = np.arctan2(ey, ex) - yaw
            dist = np.hypot(ex, ey)
        return adapter.RangeScan(t=float(t), angles=[float(v) for v in ang],
                                 distances=[float(v) for v in dist], max_range=float(max_range))


class ArcScanMatcher(R.ScanMatcher):
    """Extra, not the specified scoring: per reading, the best likelihood over arc_sub points
    spread across its cone at the measured range (the arena cone reports a near-closest hit
    somewhere in the cone, so one point on the arc lies on a surface). Score = mean over readings
    of that maximum. Fed by Submap.pseudo(..., arc_sub=ARC_SUB); otherwise ScanMatcher unchanged."""

    def __init__(self, grid, arc_sub: int, sigma: float = R.SIGMA_M):
        super().__init__(grid, sigma)
        self.arc_sub = arc_sub

    def score(self, b, cands):
        px = cands[:, 0:1] + b[None, :, 0]
        py = cands[:, 1:2] + b[None, :, 1]
        lk = self._look(self.lik, px, py, 0.0).reshape(len(cands), -1, self.arc_sub)
        s = lk.max(axis=2).mean(axis=1)
        clear = self._look(self.dist, cands[:, 0], cands[:, 1], 0.0)
        return np.where(clear >= R.MIN_CLEAR_M, s, -1.0)


ARC_SUB = 9                # arc points per 27 deg cone (3.4 deg apart, 0.18 m at 3 m)
FWD_EPS = 0.05             # outlier floor of the forward beam model (disambiguate.EPS)


class ConeVerifier:
    """Extra: re-score hypotheses with a forward cone model. For each stored reading (finite or no
    return), predict the reading at the hypothesis by ray casting n_sub sub-rays of the cone on
    the map grid and taking the k-th closest (the arena cone model, sensors_cone.py); compare with
    (1 - EPS) exp(-dz^2 / 2 sigma^2) + EPS for two finite ranges, 1 for two no-returns, EPS for one
    of each. Score = mean over readings, in [EPS, 1]. Unlike the EDT scores it uses no-returns.
    It assumes the sensor is the arena's cone model: a real VL53L1x is not exactly that."""

    def __init__(self, grid, max_range: float, half_cone: float, n_sub: int, k: int, sigma: float = R.SIGMA_M):
        self.mm = D.MapModel(grid, max_range)
        self.max_range = max_range
        self.sub = np.linspace(-half_cone, half_cone, n_sub)
        self.k, self.sigma = k, sigma

    def predict(self, centres: np.ndarray, rel: np.ndarray, W: np.ndarray) -> np.ndarray:
        """(H, 2) hypotheses, (n, 2) reading positions relative to now, (n,) world bearings => (H, n)."""
        mm = self.mm
        pos = centres[:, None, :] + rel[None, :, :]                         # (H, n, 2)
        ang = W[:, None] + self.sub[None, :]                                 # (n, S)
        c, s = np.cos(ang), np.sin(ang)
        st = mm.steps
        px = pos[:, :, None, None, 0] + c[None, :, :, None] * st
        py = pos[:, :, None, None, 1] + s[None, :, :, None] * st
        ix = np.floor((px - mm.x0) / mm.res).astype(int)
        iy = np.floor((py - mm.y0) / mm.res).astype(int)
        inside = (ix >= 0) & (iy >= 0) & (ix < mm.occ.shape[0]) & (iy < mm.occ.shape[1])
        hit = np.ones(px.shape, bool)
        hit[inside] = mm.occ[ix[inside], iy[inside]]
        r = np.where(hit.any(axis=3), st[np.argmax(hit, axis=3)], np.inf)   # (H, n, S)
        r = np.sort(r, axis=2)[:, :, self.k - 1]
        return np.where(r <= self.max_range, r, np.inf)

    def rescore(self, hyps: list, rel, W, d) -> list:
        if not hyps or len(d) == 0:
            return hyps
        sc = self.scores(np.array([[h.x, h.y] for h in hyps]), rel, W, d)
        out = [R.Hypothesis(h.x, h.y, float(v)) for h, v in zip(hyps, sc)]
        out.sort(key=lambda h: -h.score)
        return out

    def scores(self, C: np.ndarray, rel, W, d) -> np.ndarray:
        Z = self.predict(C, rel, W)
        fz, fd = np.isfinite(Z), np.isfinite(d)[None, :]
        dz = np.where(fz & fd, Z - np.where(fd, d[None, :], 0.0), 0.0)
        p = np.where(fz & fd, (1 - FWD_EPS) * np.exp(-0.5 * (dz / self.sigma) ** 2) + FWD_EPS,
                     np.where(fz == fd, 1.0, FWD_EPS))
        return p.mean(axis=1)


class InertialBridge:
    """IMU-only dead reckoning from the last good EKF velocity (see module docstring)."""

    def __init__(self, rng):
        self.rng = rng
        self.bias = rng.normal(0.0, ACC_BIAS, 2)
        self.p = self.v = self.tv = None
        self.t = None

    def start(self, xy, v_est, truth) -> None:
        self.p = np.asarray(xy, float).copy()
        self.v = np.asarray(v_est, float).copy()
        self.tv = np.array([truth.vx, truth.vy], float)
        self.t = truth.t

    def step(self, truth) -> np.ndarray:
        dt = truth.t - self.t
        tv = np.array([truth.vx, truth.vy], float)
        if dt > 0:
            n = max(1, int(round(dt * IMU_HZ)))
            a = (tv - self.tv) / dt + self.bias + self.rng.normal(0.0, ACC_NOISE / math.sqrt(n), 2)
            v1 = self.v + a * dt
            self.p = self.p + 0.5 * (self.v + v1) * dt
            self.v = v1
        self.tv, self.t = tv, truth.t
        return self.p.copy()


class SubmapMoveChooser(D.MoveChooser):
    """Info-gain move whose predicted observation is the 4 beams at N_ALONG points along the move."""

    def __init__(self, grid, rng, beam_angles, max_range: float):
        super().__init__(grid, "infogain", rng, angles=beam_angles, max_range=max_range)
        self.frac = np.arange(1, N_ALONG + 1) / N_ALONG

    def _predict(self, starts: np.ndarray, d: np.ndarray, yaw: float) -> np.ndarray:
        ang = self.body_angles + yaw
        Z = [self.mm.raycast(starts + f * d, ang) for f in self.frac]
        return np.concatenate(Z, axis=1)                       # (H, N_ALONG * B)

    def utilities(self, live_xy, w, yaw, idx):
        u = np.full(len(self.moves), -np.inf)
        h0 = D._entropy(w)
        for k in idx:
            Z = self._predict(live_xy, self.moves[k], yaw)
            fi = np.isfinite(Z)
            H = len(live_xy)
            L = np.zeros((H, H))
            for j in range(H):
                both = fi[j] & fi
                dz = np.where(both, Z - np.where(fi[j], Z[j], 0.0), 0.0)
                p = np.where(both, (1 - D.EPS) * np.exp(-0.5 * (dz / D.SIGMA_B) ** 2) + D.EPS,
                             np.where(fi[j] == fi, 1.0, D.EPS))
                L[j] = np.log(p).sum(axis=1)
            eh = 0.0
            for j in range(H):
                lp = np.log(w) + L[j]
                post = np.exp(lp - lp.max())
                eh += w[j] * D._entropy(post / post.sum())
            u[k] = h0 - eh
        return u

    def choose(self, hyps, est_xy, yaw, goal=None):
        lv = self.live(hyps)
        est_xy = np.asarray(est_xy, float)
        starts = np.vstack([np.array([[h.x, h.y] for h in lv]).reshape(-1, 2), est_xy[None, :]])
        ok = D.feasible(self.mm, starts, self.moves)
        nf = int(ok.sum())
        if nf == 0:
            return D.Choice(None, self.kind, None, len(lv), 0, "none_feasible")
        idx = np.flatnonzero(ok)
        if len(lv) < 2:                                         # verdict "none": seek returns
            u = np.full(len(self.moves), -np.inf)
            for k in idx:
                u[k] = float(np.isfinite(self._predict(est_xy[None, :], self.moves[k], yaw)).sum())
            k = self._pick(u, ok, est_xy, goal)
            return D.Choice(tuple(self.moves[k]), self.kind, float(u[k]), len(lv), nf, "returns")
        xy = np.array([[h.x, h.y] for h in lv])
        w = np.full(len(lv), 1.0 / len(lv))
        u = self.utilities(xy, w, yaw, idx)
        k = self._pick(u, ok, est_xy, goal)
        return D.Choice(tuple(self.moves[k]), self.kind, float(u[k]), len(lv), nf, "hypotheses")


class SubmapPoseSource:
    """See module docstring. `cmd` is the (vx, vy) to fly while quality is 0 (a move) or None.
    match=False: ablation, bridge across the loss and keep the pre-loss anchor, no matching.
    scoring="arc": extra, ArcScanMatcher instead of ScanMatcher + cone_opening_local.
    scoring="arc_fwd": extra, "arc" hypotheses re-scored by ConeVerifier before the rule (cone =
    the preset dict, for n_sub and min_fill)."""

    def __init__(self, est, grid, scan_fn, max_range: float, half_cone: float, rng, moves: bool = False,
                 goal=None, beam_angles=None, window_s: float = WINDOW_S, max_points: int = MAX_POINTS,
                 innovation: bool = True, match: bool = True, scoring: str = "opening", track: bool = True, cone=None):
        if scoring not in ("opening", "arc", "arc_fwd"):
            raise ValueError(scoring)
        self.est, self.scan_fn = est, scan_fn
        self.max_range, self.half_cone = max_range, half_cone
        self.arc_sub = ARC_SUB if (scoring.startswith("arc") and half_cone > 0) else 0
        self.matcher = ArcScanMatcher(grid, self.arc_sub) if self.arc_sub else R.ScanMatcher(grid)
        self.verifier = None
        if scoring == "arc_fwd" and half_cone > 0:
            n_sub = int(cone["n_sub"])
            k = min(n_sub, max(1, math.ceil(cone["min_fill"] * n_sub - 1e-9)))
            self.verifier = ConeVerifier(grid, max_range, half_cone, n_sub, k)
        self.rule = submap_rule()
        self.submap = Submap(window_s, max_points)
        self.bridge = InertialBridge(rng)
        self.moves_on, self.goal = moves, goal
        self.innovation, self.match, self.track = innovation, match, track
        self.track_k = 0
        self.track_updates = 0
        self.track_m = 0.0
        self.chooser = None
        if moves:
            self.chooser = SubmapMoveChooser(grid, rng, beam_angles, max_range)
            self.chooser.matcher = self.matcher
            self.chooser.live = lambda hyps: ([h for h in hyps if h.score >= hyps[0].score / SUBMAP_RATIO ** 2]
                                              if hyps else [])
        self.offset = np.zeros(2)
        self.prior_offset = np.zeros(2)
        self.state = "nominal"
        self.window = R.W0_M
        self.none_run = self.innov_bad = 0
        self.prev_q = None
        self.prev_reset = 0
        self.prev_raw = None
        self.prev_bp = None
        self.settle_ok = self.bridge_steps = 0
        self.event: R.Event | None = None
        self.events: list[R.Event] = []
        self.extra: list[dict] = []              # per event: settle_s, shift_m, returns, span, moves
        self.cmd = None
        self.move = None
        self.timer_t = 0.0
        self.errs: list[float] = []
        self.hover_steps = 0
        self.move_steps = 0
        self.match_ms: list[float] = []
        self.innov_runs = 0

    # ---- helpers ----
    def _pseudo(self, t, xy, yaw):
        return self.submap.pseudo(t, xy, yaw, self.max_range, self.half_cone, self.arc_sub)

    def _close(self, t, result):
        self.event.t_end, self.event.result = t, result
        self.event = None
        self.state = "nominal"
        self.innov_bad = 0
        self.cmd = self.move = None

    def _track(self, truth, raw, rxy):
        """Nominal flight: local search (+-TRACK_W_M) of the submap around the estimate; move the
        anchor TRACK_ALPHA of the way to the best if it passes S_MIN and beats the estimate."""
        self.track_k += 1
        if self.track_k % TRACK_EVERY:
            return
        sc = self._pseudo(truth.t, rxy, raw.yaw)
        est = rxy + self.offset
        hy = self.matcher.hypotheses(sc, raw.yaw, est, TRACK_W_M, k=1, step=TRACK_STEP_M)
        if not hy:
            return
        s0 = self.matcher.score_at(sc, raw.yaw, est)
        if self.verifier is not None and s0 is not None:     # arc_fwd: compare with the forward model
            v = self.verifier.scores(np.array([est, [hy[0].x, hy[0].y]]), *self.submap.readings(rxy))
            s0, hy = float(v[0]), [R.Hypothesis(hy[0].x, hy[0].y, float(v[1]))]
        h = hy[0]
        if s0 is not None and h.score >= SUBMAP_S_MIN and h.score >= s0 + TRACK_MARGIN:
            d = TRACK_ALPHA * (np.array([h.x, h.y]) - est)
            self.offset = self.offset + d
            self.track_updates += 1
            self.track_m += float(np.hypot(*d))

    def _start(self, truth, raw, rxy, reason):
        txy = np.array([truth.x, truth.y])
        self.event = R.Event(truth.t, reason, pre_err_m=float(np.hypot(*(rxy + self.offset - txy))))
        self.events.append(self.event)
        self.extra.append({"settle_s": None, "shift_m": None, "returns_at_first_match": None,
                           "span_s_at_first_match": None, "settle_timeout": False, "moves": []})
        self.rule.reset()
        self.window, self.none_run = R.W0_M, 0
        self.state = "bridge"
        self.bridge.start(rxy, (raw.vx, raw.vy), truth)
        self.prev_bp = rxy.copy()
        self.settle_ok = self.bridge_steps = 0
        self.cmd = self.move = None

    def _match_step(self, truth, raw, rxy, odo):
        import time
        ev, ex = self.event, self.extra[-1]
        sc = self._pseudo(truth.t, rxy, raw.yaw)
        nret = len(sc.distances) // max(1, self.arc_sub)
        if ex["returns_at_first_match"] is None:
            ex["returns_at_first_match"] = nret
            ex["span_s_at_first_match"] = round(self.submap.span_s(), 2)
        t0 = time.perf_counter()
        hyps = self.matcher.hypotheses(sc, raw.yaw, rxy + self.prior_offset, self.window)
        if self.verifier is not None:
            hyps = self.verifier.rescore(hyps, *self.submap.readings(rxy))
        self.match_ms.append((time.perf_counter() - t0) * 1e3)
        if not ev.first_hyps and hyps:
            ev.first_hyps = [[round(h.x, 3), round(h.y, 3), round(h.score, 4),
                              round(float(math.hypot(h.x - truth.x, h.y - truth.y)), 3)] for h in hyps]
            ev.truth_in_set = any(h[3] <= R.SEP_M for h in ev.first_hyps)
        verdict, h = self.rule.update(hyps, tuple(odo))
        ev.verdicts[verdict] = ev.verdicts.get(verdict, 0) + 1
        ev.last_verdict = verdict
        ev.last_returns = nret
        if verdict == "accept":
            self.offset = np.array([h.x, h.y]) - rxy
            ev.accepted_xy = [round(h.x, 3), round(h.y, 3)]
            ev.err_m = float(math.hypot(h.x - truth.x, h.y - truth.y))
            self._close(truth.t, "accepted")
            return
        if verdict == "none":
            self.none_run += 1
            if self.none_run >= R.NONE_WIDEN and self.window < R.W_MAX_M:
                self.window = min(2 * self.window, R.W_MAX_M)
                ev.max_window_m = self.window
                self.none_run = 0
        if self.moves_on:
            self._move_step(truth, raw, rxy, hyps)

    def _move_step(self, truth, raw, rxy, hyps):
        log = self.extra[-1]["moves"]
        self.cmd = None
        if self.move is not None:
            e = self.move["target_raw"] - rxy
            dist = float(math.hypot(*e))
            if dist < D.MOVE_DONE_M or truth.t - self.move["t0"] > D.MOVE_TIMEOUT_S:
                log[-1]["done_t"] = round(truth.t, 3)
                log[-1]["left_m"] = round(dist, 3)
                self.move, self.timer_t = None, truth.t
            else:
                v = min(D.MOVE_SPEED, D.K_MOVE * dist)
                self.cmd = (v * e[0] / dist, v * e[1] / dist)
        elif (truth.t - self.timer_t >= D.HOVER_TIMEOUT_S - 1e-9 and len(log) < D.MAX_MOVES
              and self.event.last_verdict in ("ambiguous", "none")):
            c = self.chooser.choose(hyps, rxy + self.prior_offset, raw.yaw, self.goal)
            if c.move is None:
                self.timer_t = truth.t
                log.append({"t": round(truth.t, 3), "move": None, "basis": c.basis})
            else:
                d = np.array(c.move)
                self.move = {"target_raw": rxy + d, "t0": truth.t}
                log.append({"t": round(truth.t, 3), "move": [round(d[0], 3), round(d[1], 3)],
                            "utility": None if c.utility is None else round(c.utility, 4),
                            "n_live": c.n_live, "basis": c.basis, "verdict": self.event.last_verdict})
                v = min(D.MOVE_SPEED, D.K_MOVE * float(np.hypot(*d)))
                self.cmd = (v * d[0] / np.hypot(*d), v * d[1] / np.hypot(*d))
        if self.cmd is not None:
            self.move_steps += 1

    # ---- PoseSource ----
    def __call__(self, truth):
        raw = self.est(truth)
        rxy = np.array([raw.x, raw.y])
        odo = np.zeros(2) if self.prev_raw is None else rxy - self.prev_raw
        self.prev_raw = rxy
        scan = self.scan_fn(truth)
        reset_now = raw.reset_counter != self.prev_reset
        if self.state == "nominal":
            self.submap.maybe_add(truth.t, rxy, raw.yaw, scan)
            self.submap.trim(truth.t)
            reason = None
            if reset_now:
                reason = "reset_counter"
            elif raw.quality == 0 and self.prev_q not in (None, 0):
                reason = "quality_0"
            elif self.innovation and self.submap.n_fin >= R.MIN_RETURNS:
                s0 = self.matcher.score_at(self._pseudo(truth.t, rxy, raw.yaw), raw.yaw, rxy + self.offset)
                self.innov_runs += 1
                self.innov_bad = self.innov_bad + 1 if (s0 is not None and s0 < S_INNOV) else 0
                if self.innov_bad >= INNOV_SCANS:
                    reason = "innovation"
            if reason is None and self.track and self.submap.n_fin >= R.MIN_RETURNS:
                self._track(truth, raw, rxy)
            if reason:
                self._start(truth, raw, rxy, reason)
        elif self.state == "bridge":
            bp = self.bridge.step(truth)
            self.submap.maybe_add(truth.t, bp, raw.yaw, scan)
            self.bridge_steps += 1
            dd = float(np.hypot(*(odo - (bp - self.prev_bp))))
            self.prev_bp = bp
            self.settle_ok = 0 if reset_now else (self.settle_ok + 1 if dd < SETTLE_TOL_M else 0)
            timeout = truth.t - self.event.t_trigger >= SETTLE_MAX_S - 1e-9
            if (self.settle_ok >= SETTLE_N and self.bridge_steps >= SETTLE_MIN) or timeout:
                shift = rxy - bp
                self.submap.shift(shift)
                self.prior_offset = self.offset - shift
                ex = self.extra[-1]
                ex.update({"settle_s": round(truth.t - self.event.t_trigger, 3),
                           "shift_m": [round(float(shift[0]), 3), round(float(shift[1]), 3)],
                           "settle_timeout": bool(timeout and self.settle_ok < SETTLE_N)})
                self.timer_t = truth.t
                if self.match:
                    self.state = "match"
                    self._match_step(truth, raw, rxy, np.zeros(2))
                else:                                       # ablation: bridge only, keep the old anchor
                    self.offset = self.prior_offset
                    self.event.err_m = float(math.hypot(*(rxy + self.offset - np.array([truth.x, truth.y]))))
                    self._close(truth.t, "accepted")
        elif self.state == "match":
            self.submap.maybe_add(truth.t, rxy, raw.yaw, scan)
            if reset_now:                                   # a new step while matching: bridge again
                self.state = "bridge"
                self.bridge.start(rxy - odo, (raw.vx, raw.vy), truth)   # approx: start at the last raw
                self.prev_bp = rxy - odo
                self.settle_ok = self.bridge_steps = 0
                self.offset = self.prior_offset
                self.cmd = self.move = None
            else:
                self._match_step(truth, raw, rxy, odo)
        self.prev_q, self.prev_reset = raw.quality, raw.reset_counter

        txy = np.array([truth.x, truth.y])
        if self.state == "nominal":
            out = rxy + self.offset
            q = raw.quality if raw.quality > 0 else 50
        elif self.state == "bridge":
            out = self.bridge.p + self.offset
            q = 0
        else:
            out = rxy + self.prior_offset
            q = 0
        if q == 0:
            self.hover_steps += 1
        if self.state == "nominal":
            self.cmd = None
        self.errs.append(float(np.hypot(*(out - txy))))
        return type(raw)(t=raw.t, x=float(out[0]), y=float(out[1]), z=raw.z, vx=raw.vx, vy=raw.vy,
                         vz=raw.vz, yaw=raw.yaw, quality=q, reset_counter=raw.reset_counter,
                         sigma_xy=raw.sigma_xy)

    def event_dicts(self) -> list[dict]:
        out = []
        for ev, ex in zip(self.events, self.extra):
            d = ev.to_dict()
            d.update(ex)
            d["n_moves"] = len([m for m in ex["moves"] if m.get("move") is not None])
            out.append(d)
        return out
