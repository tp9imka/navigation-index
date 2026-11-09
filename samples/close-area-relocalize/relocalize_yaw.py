"""3-DoF (x, y, yaw) relocalization: yaw search on top of relocalize.py and disambiguate.py.

relocalize.py takes yaw from the estimator ("yaw is truth" in its README limits). This file adds
a yaw search without editing that file (numpy + scipy, map only, truth never used):

YawScanMatcher    subclass of relocalize.ScanMatcher. hypotheses() scores the same xy lattice
                  (STEP_M in a +-window around the estimate) at every yaw offset of a coarse
                  lattice YAW_HALF_DEG / YAW_STEP_DEG around the estimator's yaw, keeps the best
                  yaw per xy cell, runs the same SEP_M non-maximum suppression (up to K_MAX
                  hypotheses, so RatioPersistence sees the same kind of list), then refines each
                  peak on a STEP_M / 4 xy lattice x a YAW_FINE_STEP_DEG lattice spanning one
                  coarse step. Each hypothesis carries dyaw = yaw correction to add to the
                  estimator yaw. score() and score_at() are unchanged (xy at a given yaw).
YawCorrected      wraps the raw estimator: output deltas are the raw deltas rotated by the
                  current yaw correction dyaw, output yaw = raw yaw + dyaw. Changing dyaw only
                  rotates future deltas, so the pose stays continuous.
YawDisambPoseSource  disambiguate.DisambPoseSource (mode multi, hover timeout + chosen move)
                  on YawCorrected, with YawScanMatcher. On accept the xy offset is re-anchored as
                  before and dyaw += the accepted hypothesis' dyaw, so the heading is corrected
                  too. The move chooser still predicts scans at one common yaw (the current
                  corrected estimate); hypotheses that differ by a few degrees are not modelled
                  separately there.
                  heading_first=True (option): while the xy verdict is still open, if every live
                  hypothesis (score >= best / RATIO^2) agrees on dyaw within YAW_AGREE_DEG, the
                  best score is >= S_MIN and |dyaw| >= YAW_MIN_FIX_DEG for HEADING_SCANS scans in
                  a row, apply the mean dyaw at once. In a corridor the hypotheses tie along the
                  axis but agree on heading, so disambiguating moves are then flown with the
                  corrected heading.

The yaw window is a prior: a heading error larger than YAW_HALF_DEG is not searched, so a
180 deg look-alike is invisible to this matcher (run_yaw.py measures what that means).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

import disambiguate as D
import relocalize as R

YAW_HALF_DEG = 15.0        # deg, coarse yaw window around the estimator's yaw
YAW_STEP_DEG = 2.5         # deg, coarse yaw lattice step: 13 yaws over +-15 deg
YAW_FINE_STEP_DEG = 0.25   # deg, refine lattice over +-YAW_STEP_DEG / 2 around the coarse peak
# ---- heading first (option, added after the first corridor run, see run_yaw.py) ----
YAW_AGREE_DEG = 1.0        # deg, every live hypothesis' dyaw within this of the best one
YAW_MIN_FIX_DEG = 1.0      # deg, smaller agreed corrections wait for the accept
HEADING_SCANS = 3          # scans in a row with agreement and best score >= S_MIN


def wrap_pi(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


def rot(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]])


@dataclass
class YawHypothesis(R.Hypothesis):
    dyaw: float = 0.0      # rad, correction to add to the yaw the matcher was given


class YawScanMatcher(R.ScanMatcher):
    def __init__(self, grid, half_deg: float = YAW_HALF_DEG, step_deg: float = YAW_STEP_DEG,
                 fine_step_deg: float = YAW_FINE_STEP_DEG, sigma: float = R.SIGMA_M):
        super().__init__(grid, sigma)
        n = int(round(half_deg / step_deg))
        offs = np.arange(-n, n + 1) * step_deg
        if half_deg >= 180.0 - 1e-9:                          # full circle: -180 == +180
            offs = offs[offs > -180.0 + 1e-9]
        self.yaw_offsets = np.radians(offs)
        m = int(round(0.5 * step_deg / fine_step_deg))
        self.fine_offsets = np.radians(np.arange(-m, m + 1) * fine_step_deg)
        self.half_deg, self.step_deg, self.fine_step_deg = half_deg, step_deg, fine_step_deg

    def _lik_mean(self, b: np.ndarray, cands: np.ndarray) -> np.ndarray:
        px = cands[:, 0:1] + b[None, :, 0]
        py = cands[:, 1:2] + b[None, :, 1]
        return self._look(self.lik, px, py, 0.0).mean(axis=1)

    def hypotheses(self, scan, yaw: float, centre, half_width: float = R.W0_M,
                   k: int = R.K_MAX, step: float = R.STEP_M) -> list[YawHypothesis]:
        if int(np.isfinite(np.asarray(scan.distances, float)).sum()) < R.MIN_RETURNS:
            return []
        g = np.arange(-half_width, half_width + 1e-9, step)
        X, Y = np.meshgrid(centre[0] + g, centre[1] + g, indexing="ij")
        C = np.column_stack([X.ravel(), Y.ravel()])
        clear = self._look(self.dist, C[:, 0], C[:, 1], 0.0) >= R.MIN_CLEAR_M
        S = np.full((len(self.yaw_offsets), len(C)), -1.0)
        Cc = C[clear]
        for j, o in enumerate(self.yaw_offsets):
            S[j, clear] = self._lik_mean(self.beams(scan, yaw + o), Cc)
        jb = np.argmax(S, axis=0)
        s = S[jb, np.arange(len(C))]
        picks: list[tuple[np.ndarray, float]] = []
        for i in np.argsort(-s):
            if s[i] < R.KEEP_FLOOR:
                break
            if all(math.hypot(*(C[i] - p)) >= R.SEP_M for p, _ in picks):
                picks.append((C[i], float(self.yaw_offsets[jb[i]])))
                if len(picks) == k:
                    break
        fine = np.arange(-step, step + 1e-9, step / 4)
        FX, FY = np.meshgrid(fine, fine, indexing="ij")
        F = np.column_stack([FX.ravel(), FY.ravel()])
        out = []
        for p, o0 in picks:
            P = p + F
            okc = self._look(self.dist, P[:, 0], P[:, 1], 0.0) >= R.MIN_CLEAR_M
            best = (-1.0, 0, o0)
            for o in o0 + self.fine_offsets:
                sf = np.where(okc, self._lik_mean(self.beams(scan, yaw + o), P), -1.0)
                j = int(np.argmax(sf))
                if sf[j] > best[0]:
                    best = (float(sf[j]), j, float(o))
            sc, j, o = best
            out.append(YawHypothesis(float(P[j, 0]), float(P[j, 1]), sc, wrap_pi(o)))
        out.sort(key=lambda h: -h.score)
        return out


class YawCorrected:
    """Raw estimator => yaw-corrected stream. Deltas rotated by dyaw, yaw + dyaw."""

    def __init__(self, est):
        self.est = est
        self.dyaw = 0.0
        self.prev = None
        self.out = None

    def __call__(self, truth):
        raw = self.est(truth)
        p = np.array([raw.x, raw.y])
        self.out = p.copy() if self.prev is None else self.out + rot(self.dyaw) @ (p - self.prev)
        self.prev = p
        v = rot(self.dyaw) @ np.array([raw.vx, raw.vy])
        return replace(raw, x=float(self.out[0]), y=float(self.out[1]), vx=float(v[0]), vy=float(v[1]),
                       yaw=wrap_pi(raw.yaw + self.dyaw))


class YawDisambPoseSource(D.DisambPoseSource):
    """DisambPoseSource with a 3-DoF matcher; the accepted dyaw corrects the heading."""

    def __init__(self, est, grid, scan_fn, kind: str = "infogain", rng=None, innovation: bool = True,
                 goal=None, half_deg: float = YAW_HALF_DEG, step_deg: float = YAW_STEP_DEG,
                 heading_first: bool = False):
        self.heading_first = heading_first
        self.agree_run = 0
        self.heading_fixes: dict[int, list] = {}  # event index => early heading fixes (scoring only)
        self.yc = YawCorrected(est)
        super().__init__(self.yc, grid, scan_fn, kind, rng, innovation, goal)
        self.matcher = YawScanMatcher(grid, half_deg, step_deg)
        self.chooser.matcher = self.matcher
        inner = self.matcher.hypotheses

        def recording(*a, **kw):
            self.last_hyps = inner(*a, **kw)
            return self.last_hyps
        self.matcher.hypotheses = recording
        rule_update = self.rule.update
        self._accepted = None

        def update(hyps, odo_delta=(0.0, 0.0)):
            verdict, h = rule_update(hyps, odo_delta)
            if verdict == "accept":
                self._accepted = h
            return verdict, h
        self.rule.update = update
        self.yaw_fixes: dict[int, dict] = {}      # event index => accepted dyaw and yaw error (scoring only)

    def __call__(self, truth):
        self._accepted = None
        out = super().__call__(truth)
        h = self._accepted
        if self.heading_first:
            out = self._heading_first(out, truth)
        if h is not None:
            self.yc.dyaw = wrap_pi(self.yc.dyaw + h.dyaw)
            out = replace(out, yaw=wrap_pi(out.yaw + h.dyaw))
            self.yaw_fixes[len(self.events) - 1] = {
                "dyaw_deg": round(math.degrees(h.dyaw), 3),
                "yaw_err_after_deg": round(math.degrees(wrap_pi(out.yaw - truth.yaw)), 3)}
        return out


    def _heading_first(self, out, truth):
        hy = self.last_hyps if self.state == "reloc" else []
        if not hy or hy[0].score < R.S_MIN:
            self.agree_run = 0
            return out
        live = D.MoveChooser.live(hy)
        d0 = hy[0].dyaw
        agree = all(abs(wrap_pi(h.dyaw - d0)) <= math.radians(YAW_AGREE_DEG) for h in live)
        if not agree or abs(d0) < math.radians(YAW_MIN_FIX_DEG):
            self.agree_run = 0
            return out
        self.agree_run += 1
        if self.agree_run < HEADING_SCANS:
            return out
        d = wrap_pi(d0 + float(np.mean([wrap_pi(h.dyaw - d0) for h in live])))
        self.yc.dyaw = wrap_pi(self.yc.dyaw + d)
        self.agree_run = 0
        out = replace(out, yaw=wrap_pi(out.yaw + d))
        self.heading_fixes.setdefault(len(self.events) - 1, []).append({
            "t": round(truth.t, 3), "dyaw_deg": round(math.degrees(d), 3), "n_live": len(live),
            "yaw_err_after_deg": round(math.degrees(wrap_pi(out.yaw - truth.yaw)), 3)})
        return out
