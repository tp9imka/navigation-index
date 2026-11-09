"""Disambiguating moves for multi-hypothesis relocalization (adds to relocalize.py, does not edit it).

Problem (README "Symmetric case"): RatioPersistence never commits wrong, but when hypotheses tie
it hovers forever, and a hovering scan does not change. Fix: after HOVER_TIMEOUT_S without an
accept, fly one short move chosen to separate the hypotheses, then let the same rule decide.
Repeat up to MAX_MOVES times per loss event; after that, hover (never commit on a tie).

Pieces (numpy + scipy, map only, truth never used):

MapModel        ray cast and ESDF lookup on the prior 0.1 m OccGrid (what the planner knows).
candidates()    8 directions x MOVE_DISTS_M, in the map frame.
feasible()      a move is kept only if the straight segment from EVERY live hypothesis (and the
                current estimate) to its end keeps ESDF >= CLEAR_M, or, for a start already
                closer than CLEAR_M, never gets closer than it is. If truth is near any of
                them, the move does not bring it closer to an obstacle than CLEAR_M allows.
MoveChooser     scores each feasible move for the live hypotheses with one of:
                  "separation" (arm e, proposed): expected separation of the predicted scans as
                       the matcher sees them. For each hypothesis j, predict the scan at j + d by
                       ray cast, score it with the matcher's likelihood field at every live i + d,
                       gap_j = (s_jj - max_{i != j} s_ij) / s_jj. U = sum_j w_j max(0, gap_j). This is
                       Platt 2012's "predicted observations far apart", measured with the
                       decision rule's own score, so a beam that is inf for one hypothesis only
                       counts when the matcher can use it.
                  "infogain" (arm f, Fox 1998 style baseline): expected entropy reduction.
                       Beam model per beam: (1 - EPS) exp(-dz^2 / 2 SIGMA_B^2) + EPS for two
                       finite ranges, 1 for two no-returns, EPS for one of each; every
                       BEAM_DECIM-th beam (decorrelation). U = H(w) - sum_j w_j H(p(. | z_j)).
                  "random" (arm d): uniform over feasible moves.
                Near-ties (U >= best - max(1e-6, TIE_REL * best)) go to the move that brings the
                estimate closest to B (Fox weighs utility against path cost; here the cost only
                breaks ties), then the longer move. v1 (results/disamb_corridor_v1.*) broke exact
                ties by candidate order, which silently preferred +x; see README.
                With no live hypotheses (verdict "none": fewer than MIN_RETURNS returns, or best
                score < S_MIN) "separation" and "infogain" pick the move whose end has the most
                predicted finite returns at the estimate (give the matcher something to see);
                "random" stays random.
DisambPoseSource  RelocPoseSource (mode multi) plus the timeout, the move state and `cmd`, the
                velocity a DisambGate planner flies while quality is 0. The move is flown in the
                raw estimator frame (target = raw + d): VIO deltas are fine after a jump, only the
                anchor is wrong.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import map_coordinates

import relocalize as R

# ---- move library and execution ----
N_DIRS = 8
MOVE_DISTS_M = (1.0, 2.0)
CLEAR_M = 0.35             # m, vehicle radius 0.15 + 0.20 margin, along the segment, every hypothesis
SEG_STEP_M = 0.05          # m, segment sampling for the clearance check
HOVER_TIMEOUT_S = 1.0      # s from trigger (or from the end of the last move) to the next move;
                           # (c) accepts in a median 0.4 s, p95 0.4 s (README results table)
MAX_MOVES = 4              # per loss event; then hover, never commit on a tie
MOVE_SPEED = 0.6           # m/s cap while lost
K_MOVE = 1.5               # 1/s, proportional gain on the remaining move
MOVE_DONE_M = 0.08         # m, move finished within this of its raw-frame target
MOVE_TIMEOUT_S = 6.0       # s, give up a move after this
# ---- hypothesis weights ----
LIVE_FRAC = 1.0 / (R.RATIO ** 2)   # live = score >= best / 1.02^2 (would block or nearly block the ratio test)
# ---- predicted scan / beam model ----
RAY_STEP_M = 0.05
SIGMA_B = 0.10             # m, same as the matcher's likelihood field
EPS = 0.05                 # outlier floor of the beam model
BEAM_DECIM = 3             # use every 3rd of 72 beams in the info-gain likelihood
TIE_REL = 0.10             # moves within 10 % of the best utility count as tied
KINDS = ("separation", "infogain", "random")


class MapModel:
    def __init__(self, grid, max_range: float = 6.0):
        self.occ = np.pad(grid.occ, 1, constant_values=True)
        self.esdf_p = np.pad(grid.esdf(), 1, constant_values=0.0)
        self.res, self.x0, self.y0 = grid.res, grid.x0 - grid.res, grid.y0 - grid.res
        self.max_range = max_range
        self.steps = np.arange(RAY_STEP_M, max_range + 1e-9, RAY_STEP_M)

    def esdf(self, xy: np.ndarray) -> np.ndarray:
        xy = np.asarray(xy, float).reshape(-1, 2)
        fx = (xy[:, 0] - self.x0) / self.res - 0.5
        fy = (xy[:, 1] - self.y0) / self.res - 0.5
        return map_coordinates(self.esdf_p, [fx, fy], order=1, mode="constant", cval=0.0)

    def raycast(self, xy: np.ndarray, angles: np.ndarray) -> np.ndarray:
        """(N, 2) positions x (B,) world-frame angles => (N, B) ranges, inf = no hit within range."""
        xy = np.asarray(xy, float).reshape(-1, 2)
        c, s = np.cos(angles), np.sin(angles)
        px = xy[:, 0, None, None] + c[None, :, None] * self.steps[None, None, :]
        py = xy[:, 1, None, None] + s[None, :, None] * self.steps[None, None, :]
        ix = np.floor((px - self.x0) / self.res).astype(int)
        iy = np.floor((py - self.y0) / self.res).astype(int)
        inside = (ix >= 0) & (iy >= 0) & (ix < self.occ.shape[0]) & (iy < self.occ.shape[1])
        hit = np.ones(px.shape, bool)
        hit[inside] = self.occ[ix[inside], iy[inside]]
        first = np.argmax(hit, axis=2)
        anyhit = hit.any(axis=2)
        return np.where(anyhit, self.steps[first], np.inf)


def candidates() -> np.ndarray:
    a = np.arange(N_DIRS) * (2 * math.pi / N_DIRS)
    return np.array([(r * math.cos(t), r * math.sin(t)) for r in MOVE_DISTS_M for t in a])


def feasible(mm: MapModel, starts: np.ndarray, moves: np.ndarray) -> np.ndarray:
    """Bool per move: from every start, the segment start => start + move keeps
    ESDF >= min(CLEAR_M, ESDF at that start). A start already closer than CLEAR_M to a wall
    may move, but not closer to any obstacle than it already is (v2 required CLEAR_M at the
    start too, so one hypothesis near a wall blocked every move)."""
    ok = np.ones(len(moves), bool)
    floor = np.minimum(CLEAR_M, mm.esdf(starts) - 1e-6)
    for k, d in enumerate(moves):
        n = max(2, int(math.ceil(math.hypot(*d) / SEG_STEP_M)) + 1)
        f = np.linspace(0.0, 1.0, n)
        pts = starts[:, None, :] + f[None, :, None] * d[None, None, :]
        e = mm.esdf(pts.reshape(-1, 2)).reshape(len(starts), n)
        ok[k] = bool((e.min(axis=1) >= floor).all())
    return ok


def _entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


@dataclass
class Choice:
    move: tuple | None
    kind: str
    utility: float | None
    n_live: int
    n_feasible: int
    basis: str            # "hypotheses" | "returns" | "random"


class MoveChooser:
    def __init__(self, grid, kind: str, rng=None, angles=None, max_range: float = 6.0):
        if kind not in KINDS:
            raise ValueError(kind)
        self.kind = kind
        self.mm = MapModel(grid, max_range)
        self.matcher = R.ScanMatcher(grid)
        self.rng = rng if rng is not None else np.random.default_rng(0)
        self.body_angles = np.asarray(angles if angles is not None
                                      else -math.pi + np.arange(72) * (2 * math.pi / 72), float)
        self.moves = candidates()

    @staticmethod
    def live(hyps: list) -> list:
        if not hyps:
            return []
        return [h for h in hyps if h.score >= LIVE_FRAC * hyps[0].score]

    def _pick(self, util: np.ndarray, ok: np.ndarray, est_xy, goal) -> int:
        idx = np.flatnonzero(ok)
        best = util[idx].max()
        tied = idx[util[idx] >= best - max(1e-6, TIE_REL * abs(best))]
        dist = np.hypot(self.moves[tied, 0], self.moves[tied, 1])
        if goal is None:
            return int(tied[np.argmax(dist)])
        end = est_xy[None, :] + self.moves[tied]
        to_b = np.round(np.hypot(end[:, 0] - goal[0], end[:, 1] - goal[1]), 3)
        order = np.lexsort((-dist, to_b))        # closest to B first, then longer move
        return int(tied[order[0]])

    def utilities(self, live_xy: np.ndarray, w: np.ndarray, yaw: float, idx: np.ndarray) -> np.ndarray:
        ang = self.body_angles + yaw
        u = np.full(len(self.moves), -np.inf)
        for k in idx:
            P = live_xy + self.moves[k]
            Z = self.mm.raycast(P, ang)                         # (H, B) predicted scans
            if self.kind == "separation":
                g = np.zeros(len(P))
                for j in range(len(P)):
                    ok = np.isfinite(Z[j])
                    if ok.sum() < R.MIN_RETURNS:
                        continue
                    b = np.column_stack([Z[j, ok] * np.cos(ang[ok]), Z[j, ok] * np.sin(ang[ok])])
                    s = self.matcher.score(b, P)                # score of scan j at every hypothesis
                    if s[j] <= 0:
                        continue
                    others = np.delete(s, j)
                    g[j] = max(0.0, (s[j] - others.max()) / s[j]) if len(others) else 0.0
                u[k] = float((w * g).sum())
            else:                                               # infogain
                Zd = Z[:, ::BEAM_DECIM]
                fi = np.isfinite(Zd)
                L = np.zeros((len(P), len(P)))                  # L[j, i] = log p(z_j | i)
                for j in range(len(P)):
                    both = fi[j] & fi
                    dz = np.where(both, Zd - np.where(fi[j], Zd[j], 0.0), 0.0)
                    p = np.where(both, (1 - EPS) * np.exp(-0.5 * (dz / SIGMA_B) ** 2) + EPS,
                                 np.where(fi[j] == fi, 1.0, EPS))
                    L[j] = np.log(p).sum(axis=1)
                h0 = _entropy(w)
                eh = 0.0
                for j in range(len(P)):
                    lp = np.log(w) + L[j]
                    post = np.exp(lp - lp.max())
                    eh += w[j] * _entropy(post / post.sum())
                u[k] = h0 - eh
        return u

    def choose(self, hyps: list, est_xy, yaw: float, goal=None) -> Choice:
        lv = self.live(hyps)
        est_xy = np.asarray(est_xy, float)
        starts = np.vstack([np.array([[h.x, h.y] for h in lv]).reshape(-1, 2), est_xy[None, :]])
        ok = feasible(self.mm, starts, self.moves)
        nf = int(ok.sum())
        if nf == 0:
            return Choice(None, self.kind, None, len(lv), 0, "none_feasible")
        idx = np.flatnonzero(ok)
        if self.kind == "random":
            k = int(self.rng.choice(idx))
            return Choice(tuple(self.moves[k]), self.kind, None, len(lv), nf, "random")
        if len(lv) < 2:                                         # verdict "none": seek returns
            ang = self.body_angles + yaw
            Z = self.mm.raycast(est_xy[None, :] + self.moves[idx], ang)
            u = np.full(len(self.moves), -np.inf)
            u[idx] = np.isfinite(Z).sum(axis=1)
            k = self._pick(u, ok, est_xy, goal)
            return Choice(tuple(self.moves[k]), self.kind, float(u[k]), len(lv), nf, "returns")
        xy = np.array([[h.x, h.y] for h in lv])
        w = np.full(len(lv), 1.0 / len(lv))                     # live hypotheses tie by definition
        u = self.utilities(xy, w, yaw, idx)
        k = self._pick(u, ok, est_xy, goal)
        return Choice(tuple(self.moves[k]), self.kind, float(u[k]), len(lv), nf, "hypotheses")


class DisambPoseSource(R.RelocPoseSource):
    """RelocPoseSource(mode="multi") + hover timeout + one chosen move at a time.
    `cmd` is (vx, vy) to fly while quality is 0, or None (hover)."""

    def __init__(self, est, grid, scan_fn, kind: str, rng=None, innovation: bool = True, goal=None):
        super().__init__(est, grid, scan_fn, mode="multi", innovation=innovation)
        self.goal = goal             # B in the local frame (mission input, not truth); None = v1 tie-break
        self.chooser = MoveChooser(grid, kind, rng)
        self.chooser.matcher = self.matcher
        self.last_hyps: list = []
        inner = self.matcher.hypotheses

        def recording(*a, **kw):
            self.last_hyps = inner(*a, **kw)
            return self.last_hyps
        self.matcher.hypotheses = recording
        self.cmd = None
        self.move = None             # dict: target_raw, t0
        self.timer_t = 0.0
        self._ev = None
        self.moves: dict[int, list] = {}      # event index => list of move logs
        self.move_steps = 0

    def __call__(self, truth):
        self.last_hyps = []
        out = super().__call__(truth)
        rxy = self.prev_raw
        if self.state != "reloc":
            self.cmd, self.move, self._ev = None, None, None
            return out
        ev = self.event
        if ev is not self._ev:
            self._ev, self.timer_t, self.move = ev, truth.t, None
            self.moves[len(self.events) - 1] = []
        log = self.moves[len(self.events) - 1]
        self.cmd = None
        if self.move is not None:
            e = self.move["target_raw"] - rxy
            dist = float(math.hypot(*e))
            if dist < MOVE_DONE_M or truth.t - self.move["t0"] > MOVE_TIMEOUT_S:
                log[-1]["done_t"] = round(truth.t, 3)
                log[-1]["left_m"] = round(dist, 3)
                self.move, self.timer_t = None, truth.t
            else:
                v = min(MOVE_SPEED, K_MOVE * dist)
                self.cmd = (v * e[0] / dist, v * e[1] / dist)
        elif (self.settle == 0 and truth.t - self.timer_t >= HOVER_TIMEOUT_S - 1e-9
              and len(log) < MAX_MOVES and ev.last_verdict in ("ambiguous", "none")):
            c = self.chooser.choose(self.last_hyps, rxy + self.offset, out.yaw, self.goal)
            if c.move is None:
                self.timer_t = truth.t
                log.append({"t": round(truth.t, 3), "move": None, "basis": c.basis})
            else:
                d = np.array(c.move)
                self.move = {"target_raw": rxy + d, "t0": truth.t}
                log.append({"t": round(truth.t, 3), "move": [round(d[0], 3), round(d[1], 3)],
                            "utility": None if c.utility is None else round(c.utility, 4),
                            "n_live": c.n_live, "n_feasible": c.n_feasible, "basis": c.basis,
                            "verdict": ev.last_verdict})
                v = min(MOVE_SPEED, K_MOVE * float(np.hypot(*d)))
                self.cmd = (v * d[0] / np.hypot(*d), v * d[1] / np.hypot(*d))
        if self.cmd is not None:
            self.move_steps += 1
        return out
