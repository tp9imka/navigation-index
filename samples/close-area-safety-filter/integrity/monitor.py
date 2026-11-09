"""Snapshot solution-separation integrity monitor over the VIO-EKF position and UWB ranges.

    mon = Monitor(anchors, variant="ss2")
    out = mon.step(vio_xy, vio_sigma_xy, ranges, z)
    out["pl"]        protection level, metres, horizontal, at integrity risk IR per epoch (inf = unavailable)
    out["detected"]  the all-in-view test tripped
    out["excluded"]  tuple of excluded fault groups ("vio", "a0".."a3", or "uwb"), () if none
    out["ambiguous"] detected, but no single consistent exclusion => unavailable (hover)
    out["status"]    "ok" | "excluded" | "ambiguous";  out["reason"] for ambiguous
    out["x"]         the solution the PL bounds (all-in-view, or the subset after exclusion)

Measurements per epoch (10 Hz): the VIO-EKF position from the arena estimator as a 2D
pseudo-measurement with per-axis sigma = sigma_xy / sqrt(2) (its own reported value), and 4
UWB ranges with sigma uwb.SIGMA_MODEL. Unknowns: horizontal x, y (height known).

Fault groups: "vio" and one group per anchor ("anchors" grouping), or "vio" and the whole
UWB constellation as one block ("blocks" grouping, the plain two-source monitor).

For a kept set B and up to m simultaneous faults (ARAIM-style, snapshot weighted least squares):
- every fault hypothesis E (subset of B, 1 <= |E| <= m) with B \\ E still solvable gets the
  subset solution x_{B\\E}, covariance P_{B\\E}; all covariances use one linearisation point, so
  P_{B\\E} - P_B is the separation covariance.
- detection: |x_B - x_{B\\E}| > T_E = K_fa sqrt(lmax(P_{B\\E} - P_B)), K_fa from P_FA / N.
- PL = max(K_ff sqrt(lmax P_B), max_E T_E + K_md,E sqrt(lmax P_{B\\E})), with
  K(p) = sqrt(-2 ln p): for 2D Gaussian error e ~ N(0, P), P(|e| > K sqrt(lmax P)) <= exp(-K^2/2).
  The budget IR minus the prior of unmonitored hypotheses (charge_unmonitored) is split
  equally over the fault-free case and the N hypotheses; K_md,E = K(IR_each / prior_E).
- exclusion ("subset", from samples/multi-source-fde): for sizes s = 1..m, E is consistent if
  B \\ E passes its own test (with max(1, m - s) faults, at least one testable hypothesis).
  Exactly one consistent E at the smallest size => exclude it and output x_{B\\E} with its own
  PL. Two or more => ambiguous ("multiple_consistent"). None at any size => ambiguous
  ("none_consistent"). Re-run every epoch, no latch.
- "maxsep" (reference, FT-CBF / altpnt style): on detection drop the single hypothesis with the
  largest |dx| / T_E, never ambiguous.

Priors and budgets are named constants below; they are illustrative, not derived from data.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

try:
    from . import uwb as uwb_mod
except ImportError:
    import uwb as uwb_mod

IR = 1e-3              # integrity risk per epoch the PL is computed at
P_FA = 1e-3            # false-alarm budget per epoch, split over the monitored hypotheses
PRIOR_VIO = 1e-2       # per-epoch fault prior, VIO (jump / bias / dropout), assumed
PRIOR_ANCHOR = 1e-2    # per-epoch fault prior, one UWB anchor (NLOS), assumed
COND_MAX = 1e8         # information-matrix condition number above which a subset is unsolvable
GN_ITERS = 8

VARIANTS = {
    # name: grouping, max simultaneous faults, charge unmonitored prior, exclusion rule
    "ss2": {"grouping": "anchors", "m": 2, "charge": True, "exclusion": "subset"},
    "ss1": {"grouping": "anchors", "m": 1, "charge": False, "exclusion": "subset"},
    "maxsep": {"grouping": "anchors", "m": 1, "charge": False, "exclusion": "maxsep"},
    "2src": {"grouping": "blocks", "m": 1, "charge": False, "exclusion": "subset"},
}


def kfac(p: float) -> float:
    return 0.0 if p >= 1.0 else math.sqrt(-2.0 * math.log(max(p, 1e-300)))


def lmax2(P) -> float:
    a, b, d = P[0, 0], P[0, 1], P[1, 1]
    return max(0.0, 0.5 * (a + d) + math.sqrt(max(0.0, 0.25 * (a - d) ** 2 + b * b)))


def make_groups(grouping: str, n_anchors: int = 4):
    """[(name, rows, prior)]; rows 0, 1 = VIO x, y; rows 2.. = ranges."""
    g = [("vio", (0, 1), PRIOR_VIO)]
    if grouping == "anchors":
        g += [(f"a{i}", (2 + i,), PRIOR_ANCHOR) for i in range(n_anchors)]
    elif grouping == "blocks":
        p = 1.0 - (1.0 - PRIOR_ANCHOR) ** n_anchors
        g += [("uwb", tuple(2 + i for i in range(n_anchors)), p)]
    else:
        raise ValueError(grouping)
    return g


def _esym_tail(ps, m: int) -> float:
    """Sum over subsets with more than m elements of the product of their priors."""
    e = [1.0] + [0.0] * len(ps)
    for p in ps:
        for k in range(len(ps), 0, -1):
            e[k] += e[k - 1] * p
    return float(sum(e[m + 1:]))


class Epoch:
    """All subset solutions for one epoch, solved lazily and cached."""

    def __init__(self, vio_xy, vio_sigma_xy, ranges, anchors, z, sigma_r, groups, x0):
        self.y = np.concatenate([np.asarray(vio_xy, float), np.asarray(ranges, float)])
        s_v = max(float(vio_sigma_xy), 1e-4) / math.sqrt(2.0)
        self.w = np.concatenate([[1 / s_v ** 2] * 2, [1 / sigma_r ** 2] * len(ranges)])
        self.anchors = np.asarray(anchors, float)
        self.z = float(z)
        self.groups = groups
        self.x0 = np.asarray(x0, float)
        self.cache: dict = {}
        self.H_lin = None
        full = frozenset(range(len(groups)))
        sol = self._gn(self._rows(full), self.x0)
        if sol is None:
            raise RuntimeError("all-in-view solution unsolvable")
        self.x_lin = sol
        _, self.H_lin = self._model(self.x_lin)

    def _rows(self, keep):
        return np.array(sorted(r for gi in keep for r in self.groups[gi][1]), int)

    def _model(self, x):
        n = len(self.y)
        h = np.empty(n)
        H = np.empty((n, 2))
        h[0:2] = x
        H[0:2] = np.eye(2)
        dx = x[0] - self.anchors[:, 0]
        dy = x[1] - self.anchors[:, 1]
        dz = self.z - self.anchors[:, 2]
        d = np.sqrt(dx * dx + dy * dy + dz * dz)
        h[2:] = d
        H[2:, 0] = dx / d
        H[2:, 1] = dy / d
        return h, H

    def _info(self, H, w):
        I = (H * w[:, None]).T @ H
        ev = np.linalg.eigvalsh(I)
        if ev[0] <= 0 or ev[-1] / ev[0] > COND_MAX:
            return None
        return I

    def _gn(self, rows, x):
        x = x.copy()
        w = self.w[rows]
        for _ in range(GN_ITERS):
            h, H = self._model(x)
            Hr = H[rows]
            I = self._info(Hr, w)
            if I is None:
                return None
            step = np.linalg.solve(I, (Hr * w[:, None]).T @ (self.y[rows] - h[rows]))
            x = x + step
            if float(step @ step) < 1e-10:
                break
        return x

    def solve(self, keep: frozenset):
        """(x, P) for the kept groups, or None if unsolvable."""
        if keep in self.cache:
            return self.cache[keep]
        out = None
        if keep:
            rows = self._rows(keep)
            I = self._info(self.H_lin[rows], self.w[rows])
            if I is not None:
                x = self._gn(rows, self.x_lin)
                if x is not None:
                    out = (x, np.linalg.inv(I))
        self.cache[keep] = out
        return out


def test_set(ep: Epoch, B: frozenset, m: int, charge: bool) -> dict:
    """Detection test and PL for kept set B with up to m monitored faults."""
    base = ep.solve(B)
    if base is None:
        return {"solvable": False, "testable": False, "detected": False, "pl": math.inf, "hyps": []}
    xB, PB = base
    hyps, p_nm = [], 0.0
    for s in range(1, m + 1):
        for E in itertools.combinations(sorted(B), s):
            rest = B - frozenset(E)
            p = math.prod(ep.groups[g][2] for g in E)
            sol = ep.solve(rest) if rest else None
            if sol is None:
                p_nm += p
            else:
                hyps.append((frozenset(E), p, sol))
    if charge:
        p_nm += _esym_tail([ep.groups[g][2] for g in B], m)
    else:
        p_nm = 0.0
    n = len(hyps)
    ir_mon = IR - p_nm
    sB = math.sqrt(lmax2(PB))
    if ir_mon <= 0:
        pl_budget_ok = False
        ir_each = 0.0
    else:
        pl_budget_ok = True
        ir_each = ir_mon / (n + 1)
    k_fa = kfac(P_FA / n) if n else 0.0
    detected, pl = False, (kfac(ir_each) * sB if pl_budget_ok else math.inf)
    out_h = []
    for E, p, (xE, PE) in hyps:
        sdx = math.sqrt(lmax2(PE - PB))
        T = k_fa * sdx
        stat = float(math.hypot(*(xB - xE)))
        det = stat > T
        detected |= det
        if pl_budget_ok:
            pl = max(pl, T + kfac(ir_each / p) * math.sqrt(lmax2(PE)))
        out_h.append({"E": E, "stat": stat, "T": T, "det": det})
    return {"solvable": True, "testable": n > 0, "detected": detected, "pl": pl, "x": xB, "hyps": out_h}


class Monitor:
    def __init__(self, anchors, variant: str = "ss2", sigma_r: float | None = None):
        cfg = VARIANTS[variant]
        self.variant = variant
        self.m = cfg["m"]
        self.charge = cfg["charge"]
        self.exclusion = cfg["exclusion"]
        self.anchors = np.asarray(anchors, float)
        self.groups = make_groups(cfg["grouping"], len(self.anchors))
        self.sigma_r = uwb_mod.SIGMA_MODEL if sigma_r is None else sigma_r
        self.x_prev = None

    def names(self, E) -> tuple:
        return tuple(self.groups[g][0] for g in sorted(E))

    def step(self, vio_xy, vio_sigma_xy, ranges, z) -> dict:
        x0 = self.x_prev if self.x_prev is not None else np.asarray(vio_xy, float)
        ep = Epoch(vio_xy, vio_sigma_xy, ranges, self.anchors, z, self.sigma_r, self.groups, x0)
        A = frozenset(range(len(self.groups)))
        ra = test_set(ep, A, self.m, self.charge)
        out = {"detected": ra["detected"], "excluded": (), "ambiguous": False, "reason": None,
               "status": "ok", "pl": ra["pl"], "x": ra["x"]}
        if ra["detected"]:
            if self.exclusion == "maxsep":
                h = max((h for h in ra["hyps"] if len(h["E"]) == 1),
                        key=lambda h: h["stat"] / max(h["T"], 1e-12))
                rb = test_set(ep, A - h["E"], 1, self.charge)
                out.update(status="excluded", excluded=self.names(h["E"]), pl=rb["pl"], x=rb["x"])
            else:
                self._subset_exclusion(ep, A, out)
        self.x_prev = ep.x_lin
        return out

    def _subset_exclusion(self, ep, A, out) -> None:
        for s in range(1, self.m + 1):
            cands = []
            for E in itertools.combinations(sorted(A), s):
                B = A - frozenset(E)
                rb = test_set(ep, B, max(1, self.m - s), self.charge)
                if rb["testable"] and not rb["detected"]:
                    cands.append((E, rb))
            if len(cands) == 1:
                E, rb = cands[0]
                out.update(status="excluded", excluded=self.names(E), pl=rb["pl"], x=rb["x"])
                return
            if len(cands) > 1:
                out.update(status="ambiguous", ambiguous=True, reason="multiple_consistent",
                           pl=math.inf, excluded=())
                return
        out.update(status="ambiguous", ambiguous=True, reason="none_consistent", pl=math.inf)
