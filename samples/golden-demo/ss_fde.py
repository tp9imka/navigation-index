"""Solution-separation FDE and horizontal protection level for the golden demo companion.

Ported from samples/altpnt-integrity/altpnt_integrity.py (Monitor: _separations, _detect,
_probation, _readmit, _rewind, _hpl). Constants, matrix helpers and q_inv are imported from
there unchanged. What differs:

- The filter is a 4-state [east, north, bias_ve, bias_vn] position filter propagated with VIO
  velocity (the companion has VIO + absolute fixes, no IMU stream), instead of the 8-state
  INS error model.
- Two monitored absolute sources (GNSS, visual geoloc). With both active a separation
  failure is detectable but not identifiable from the bank alone. altpnt-integrity answers
  with an alert + 45 s probation. Here the VIO dead-reckoning solution replayed from a
  LOOKBACK-old snapshot is used as a third witness first: if exactly one source fails a
  chi-square test against it, that source is excluded at once; otherwise the altpnt path runs.
- GATE_EXCLUDE_N consecutive gate rejections exclude a source (a fast drag or a step is gated
  by every filter in the bank, so it never shows up as a separation).
- VelocityConsistency: windowed chi-square on GNSS velocity minus VIO velocity. Not in
  altpnt-integrity; added because a coherent spoof drags velocity too.
"""
from __future__ import annotations

import copy
import math
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "altpnt-integrity"))
sys.path.insert(0, str(HERE.parents[1] / "templates" / "project-repo" / "src"))

import mat  # noqa: E402
from altpnt_integrity import (ACTIVE_WINDOW, CHI2_2DOF_999, EXCLUSION_HOLD, IR_FF,  # noqa: E402
                              LOOKBACK, P_FA, P_MD, PROBATION_PASSES, PROBATION_TIME,
                              SIGMA_D_FLOOR, q_inv)
from navapp.integrity import chi2_threshold_even  # noqa: E402

VIO_BIAS_SIGMA = 0.1          # m/s, Gauss-Markov overbound of the VIO velocity bias
VIO_BIAS_TAU = 300.0          # s
Q_POS = 0.05                  # m^2/s, unmodelled motion between VIO samples
GATE_EXCLUDE_N = 3            # consecutive chi-square gate rejections that exclude a source
H = [[1, 0, 0, 0], [0, 1, 0, 0]]


class PosFilter:
    """State [e, n, be, bn]; VIO velocity u = v_true + b + w drives the position."""

    def __init__(self, e, n, sigma_pos):
        self.x = [e, n, 0.0, 0.0]
        self.P = mat.zeros(4, 4)
        self.P[0][0] = self.P[1][1] = sigma_pos ** 2
        self.P[2][2] = self.P[3][3] = VIO_BIAS_SIGMA ** 2

    def clone(self):
        return copy.deepcopy(self)

    def predict(self, vel_en, sigma_v, dt):
        phi = math.exp(-dt / VIO_BIAS_TAU)
        x = self.x
        x[0] += (vel_en[0] - x[2]) * dt
        x[1] += (vel_en[1] - x[3]) * dt
        x[2] *= phi
        x[3] *= phi
        F = [[1, 0, -dt, 0], [0, 1, 0, -dt], [0, 0, phi, 0], [0, 0, 0, phi]]
        qp = (sigma_v * dt) ** 2 + Q_POS * dt
        qb = VIO_BIAS_SIGMA ** 2 * (1 - phi * phi)
        Q = [[qp, 0, 0, 0], [0, qp, 0, 0], [0, 0, qb, 0], [0, 0, 0, qb]]
        self.P = mat.sym(mat.add(mat.mul(mat.mul(F, self.P), mat.T(F)), Q))

    def innovation(self, z, r):
        y = [z[0] - self.x[0], z[1] - self.x[1]]
        S = mat.add(mat.mul(mat.mul(H, self.P), mat.T(H)), [[r * r, 0.0], [0.0, r * r]])
        Si = mat.inv2(S)
        return y, Si, sum(y[i] * Si[i][j] * y[j] for i in range(2) for j in range(2))

    def update(self, z, r, gate=True):
        y, Si, nis = self.innovation(z, r)
        if gate and nis > CHI2_2DOF_999:
            return nis, False
        K = mat.mul(mat.mul(self.P, mat.T(H)), Si)
        self.x = [a + b for a, b in zip(self.x, mat.mv(K, y))]
        self.P = mat.sym(mat.mul(mat.sub(mat.eye(4), mat.mul(K, H)), self.P))
        return nis, True

    def pos_cov(self):
        return [[self.P[0][0], self.P[0][1]], [self.P[1][0], self.P[1][1]]]

    def sigma_h(self):
        return math.sqrt(mat.lmax2(self.pos_cov()))


class SolutionSeparation:
    """Main filter fuses every admitted source; branch s excludes monitored source s."""

    def __init__(self, e0, n0, sigma0, r_m: dict, monitored=("gnss", "vgeo")):
        self.r_m = dict(r_m)
        self.monitored = tuple(monitored)
        self.main = PosFilter(e0, n0, sigma0)
        self.subs = {s: self.main.clone() for s in self.monitored}
        self.excluded: dict[str, dict] = {}
        self.ambiguous = False
        self.k_md = q_inv(P_MD)
        self.k_ff = q_inv(IR_FF / 2)
        self.history: deque = deque()
        self.last_fused: dict[str, float] = {}
        self.gate_streak: dict[str, int] = {}
        self.post_exclusion = (-math.inf, 0.0)
        self.t = None

    def _k_fa(self):
        return q_inv(P_FA / (2 * max(len(self.subs), 1)))

    def step(self, t, vio_en, sigma_v, fixes: dict):
        """fixes: source => (e, n) or None. Returns a dict for logging."""
        dt = 1.0 if self.t is None else max(t - self.t, 1e-3)
        self.t = t
        events = []
        for f in [self.main, *self.subs.values()]:
            f.predict(vio_en, sigma_v, dt)
        for src, z in fixes.items():
            if z is None:
                continue
            if src in self.excluded:
                self._probation(src, z, t)
                continue
            _, ok = self.main.update(z, self.r_m[src])
            if ok:
                self.last_fused[src] = t
                self.gate_streak[src] = 0
            else:
                events.append(f"gate:{src}")
                self.gate_streak[src] = self.gate_streak.get(src, 0) + 1
            for s, f in self.subs.items():
                if s != src:
                    f.update(z, self.r_m[src])
        if self.subs and not self.ambiguous:
            # A step bigger than the gate never separates the branches (every filter gates it),
            # so persistent rejection is an exclusion of its own (not in altpnt-integrity).
            gated = [s for s in self.subs if self.gate_streak.get(s, 0) >= GATE_EXCLUDE_N]
            if gated:
                events.append(f"detect:gate x{GATE_EXCLUDE_N} {gated[0]}")
                self._exclude_one(gated[0], t, events)
            else:
                self._detect(t, fixes, events, (vio_en, sigma_v, dt))
        self._readmit(t, events)
        self.history.append((t, self.main.clone(), vio_en, sigma_v, dt))
        while self.history and t - self.history[0][0] > LOOKBACK:
            self.history.popleft()
        sep = self._separations()
        return {"hpl": self._hpl(sep), "events": events, "e": self.main.x[0], "n": self.main.x[1],
                "sigma_h": self.main.sigma_h(), "excluded": sorted(self.excluded),
                "ambiguous": self.ambiguous,
                "sep": {s: [round(d, 2), round(thr, 2)] for s, (d, thr, _) in sep.items()}}

    def _probation(self, src, z, t):
        ex = self.excluded[src]
        _, _, nis = self.main.innovation(z, self.r_m[src])
        if ex["streak"] is None:
            ex["streak"] = {"start": t, "passes": 0, "fails": 0}
        st = ex["streak"]
        if nis <= CHI2_2DOF_999:
            st["passes"] += 1
            st["fails"] = 0
        else:
            st["fails"] += 1
            if st["fails"] >= 2 or st["passes"] == 0:
                ex["streak"] = None

    def _readmit(self, t, events):
        for s, ex in list(self.excluded.items()):
            st = ex["streak"]
            if (t - ex["t"] >= EXCLUSION_HOLD and st and t - st["start"] >= PROBATION_TIME
                    and st["passes"] >= PROBATION_PASSES):
                del self.excluded[s]
                events.append(f"readmit:{s}")
                for other in self.excluded.values():
                    other["streak"] = None
                if self.ambiguous:
                    self.ambiguous = False
                    self.subs = {k: self.main.clone() for k in self.monitored if k not in self.excluded}
                    events.extend(f"blame:{k}" for k in self.excluded)
                elif s in self.monitored:
                    self.subs[s] = self.main.clone()

    def _separations(self):
        k_fa = self._k_fa()
        out = {}
        for s, f in self.subs.items():
            d = math.hypot(self.main.x[0] - f.x[0], self.main.x[1] - f.x[1])
            pd = mat.sub(f.pos_cov(), self.main.pos_cov())
            sig_d = max(math.sqrt(max(mat.lmax2(pd), 0.0)), SIGMA_D_FLOOR)
            out[s] = (d, k_fa * sig_d, f.sigma_h())
        return out

    def _detect(self, t, fixes, events, current):
        sep = self._separations()
        tripped = {s: d / thr for s, (d, thr, _) in sep.items() if d > thr}
        if not tripped:
            return
        active = [s for s in self.subs if t - self.last_fused.get(s, -math.inf) <= ACTIVE_WINDOW]
        if len(active) == 2:
            dr = self._rewind(current)
            nis = {s: dr.innovation(fixes[s], self.r_m[s])[2] for s in active if fixes.get(s)}
            bad = [s for s, v in nis.items() if v > CHI2_2DOF_999]
            if len(nis) == 2 and len(bad) == 1:
                events.append(f"detect:dr-witness nis={','.join(f'{k}:{v:.1f}' for k, v in nis.items())}")
                self._exclude_one(bad[0], t, events)
                return
            events.append("alert:ambiguous")
            for s in active:
                self.excluded[s] = {"t": t, "streak": None}
            self.ambiguous = True
            self.subs = {}
            self.main = dr
            return
        candidates = {s: r for s, r in tripped.items() if s in active} or tripped
        self._exclude_one(max(candidates, key=candidates.get), t, events)

    def _exclude_one(self, worst, t, events):
        events.append(f"exclude:{worst}")
        self.excluded[worst] = {"t": t, "streak": None}
        base = self.subs[worst]
        # A wrong exclusion leaves main on a faulty branch while the rebuilt bank starts at
        # zero separation; keep the spread between candidate branches in the PL meanwhile.
        spread = max([math.hypot(f.x[0] - base.x[0], f.x[1] - base.x[1])
                      for s, f in self.subs.items() if s != worst] or [0.0])
        self.post_exclusion = (t + LOOKBACK, spread)
        self.main = base.clone()
        self.subs = {s: base.clone() for s in self.monitored if s not in self.excluded}

    def _rewind(self, current):
        """VIO-only dead reckoning from the oldest snapshot in the LOOKBACK window to now."""
        if not self.history:
            return self.main.clone()
        f = self.history[0][1].clone()
        for vio, sig, dt in [h[2:] for h in list(self.history)[1:]] + [current]:
            f.predict(vio, sig, dt)
        return f

    def _hpl(self, sep):
        terms = [self.k_ff * self.main.sigma_h()]
        for _, thr, sig in sep.values():
            terms.append(thr + self.k_md * sig)
        until, spread = self.post_exclusion
        if self.t <= until:
            terms.append(spread + self.k_md * self.main.sigma_h())
        return max(terms)


GNSS_VEL_LAG_BOUND_S = 0.4    # GPS_RAW_INT velocity can be this stale vs the VIO sample


class VelocityConsistency:
    """Windowed chi-square on GNSS velocity minus VIO velocity (east, north). The variance is
    inflated by (|a| * lag bound)^2, a from VIO, so manoeuvres do not read as a spoof."""

    def __init__(self, sigma_mps, window=10, p_fa=1e-4):
        self.sigma = sigma_mps
        self.window: deque = deque(maxlen=window)
        self.gates = {n: chi2_threshold_even(p_fa, 2 * n) for n in range(1, window + 1)}

    def check(self, v_gnss, v_vio, accel_mps2=0.0):
        if v_gnss is None or v_vio is None:
            return None
        de, dn = v_gnss[0] - v_vio[0], v_gnss[1] - v_vio[1]
        var = self.sigma ** 2 + (accel_mps2 * GNSS_VEL_LAG_BOUND_S) ** 2
        self.window.append((de * de + dn * dn) / var)
        stat, gate = sum(self.window), self.gates[len(self.window)]
        return {"stat": stat, "gate": gate, "alarm": len(self.window) == self.window.maxlen and stat > gate,
                "de": de, "dn": dn}
