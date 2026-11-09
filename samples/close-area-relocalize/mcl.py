"""AF-MCL-style particle filter on the known map (adds to relocalize.py, does not edit it).

Baseline for the relocalization arms, after AF-MCL (augmented filtered Monte Carlo localization,
arXiv 2610.32645, Oct 2026, full HTML read 2026-11-09): Crazyflie, four single-point ranges plus
measured heading, EDT likelihood field, beam rejection at the previous estimate, random-particle
injection when the short-term likelihood falls below the long-term one. Its Table I parameters
are used unchanged except the particle count (see N_PARTICLES).

AFMCL (map only, truth never used), one update per 10 Hz scan:
  motion         every particle moves by the raw estimator delta (VIO / IMU, the same deltas the
                 other arms use) plus N(0, SIGMA_U^2 dt) per axis. AF-MCL uses body velocities from
                 the Flow deck; here the arena estimator's position delta plays that role. A VIO
                 jump therefore moves every particle: that is the kidnap.
  beam filter    for each finite reading (0 < z < max range), ray cast the expected range z_hat from
                 the previous estimate on the map (no hit within range => z_hat = max range).
                 Mixture z_hit p_hit + z_short p_short + z_max p_max + z_rand p_rand; keep the beam
                 if z_hit p_hit / p > CHI.
  weight         l_i = exp(mean over kept beams of log N(d_EDT(endpoint_i); 0, SIGMA_OBS)), the
                 geometric mean of the per-beam EDT likelihoods (the relocalize.py ScanMatcher EDT).
                 No kept beam => motion only, weights uniform, averages unchanged.
  divergence     l_bar = mean_i l_i (unnormalized). Two moving averages l_slow, l_fast (ALPHA_SLOW,
                 ALPHA_FAST), both started at the first l_bar. p_random = min(NU, max(0, 1 - l_fast / l_slow)).
  resampling     when ESS < GAMMA N or p_random > 0: floor(p_random N) particles drawn uniformly over
                 the unoccupied cells of the map, the rest by systematic resampling; weights reset.
  output         the mean of the final particle set (injected particles included, as in the paper)
                 and sigma = sqrt(trace(cov)), the paper's online uncertainty.
  hardening      off by default. ESTIMATE = "posterior" reports the weighted mean before injection;
                 EMPTY_FALLBACK = K uses all in-range beams after K empty-beam updates (the paper's
                 own suggested extension). Both were added after the first probe (README section).

MCLPoseSource (arena PoseSource), two modes:
  "mean"   AF-MCL as published: the planner always flies on the particle mean. Arm "mcl".
  "gate"   the hub's hover-on-ambiguity wrapper on the same filter: report quality 0 (HoverGate
           hovers) while sigma > SIGMA_GATE, resume after N_CONV scans in a row at or below it.
           Arm "mcl_gate". The trigger is the filter's own uncertainty only; reset_counter and VIO
           quality are not used (AF-MCL does not read them).
Both modes log "ambiguity events" the same way (open when sigma > SIGMA_GATE, close after N_CONV
scans at or below it), with the error to truth at the close: that is the pose navigation resumes
on. Truth is used only by the sensor model and for these logs.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

import disambiguate as D
import relocalize as R

# ---- AF-MCL Table I (simulation parameters), unchanged ----
Z_MAX, Z_RAND, Z_SHORT, Z_HIT = 0.1, 0.1, 0.1, 0.7
SIGMA_0 = 0.2          # m, initial particle spread around the known start
GAMMA = 0.5            # resample when ESS < GAMMA N
LAMBDA_SHORT = 4.0     # 1/m
SIGMA_U = 0.03         # m / sqrt(s), motion noise
SIGMA_OBS = 0.15       # m, EDT likelihood width
ALPHA_SLOW = 0.001
ALPHA_FAST = 0.9
CHI = 0.4              # beam kept if posterior hit probability > CHI
NU = 0.3               # cap on the injected fraction per update
# ---- changed for the arena ----
N_PARTICLES = 400      # AF-MCL: 100 in 6 x 6 m and 10 x 10 m maps. The arena is 20 x 20 m, so 400
                       # keeps the particle density of the paper's 10 x 10 m case (1 per m^2).
# ---- hub gate (proposal, not from the paper) ----
SIGMA_GATE = 0.25      # m, half the 0.5 m wrong-commit radius
N_CONV = 3             # scans in a row at or below SIGMA_GATE to resume (as RatioPersistence N_SCANS)
OUT_CVAL_M = 1.0       # m, EDT distance assigned to endpoints outside the padded map
# ---- hardening options (off by default = AF-MCL as published; run_mcl.py --hardened turns both on) ----
ESTIMATE = "final"     # "final": mean of the final set, injected particles included (paper);
                       # "posterior": weighted mean before injection (what AMCL-style filters report).
                       # sigma always comes from the final set (the paper's uncertainty signal).
EMPTY_FALLBACK = 0     # 0 = off (paper). K > 0: after K empty-beam updates in a row, weight and
                       # detect divergence on all in-range beams (the extension the paper suggests
                       # in II-B "Empty beam set")


class AFMCL:
    def __init__(self, grid, max_range: float, x0, rng, n: int = N_PARTICLES, beam_filter: bool = True,
                 inject: bool = True, estimate: str = ESTIMATE, empty_fallback: int = EMPTY_FALLBACK):
        if estimate not in ("final", "posterior"):
            raise ValueError(estimate)
        self.matcher = R.ScanMatcher(grid)           # padded EDT in metres (self.matcher.dist)
        self.mm = D.MapModel(grid, max_range)
        self.max_range = float(max_range)
        self.rng = rng
        self.n = n
        self.beam_filter, self.inject = beam_filter, inject
        self.estimate, self.empty_fallback = estimate, empty_fallback
        self.empty_run = 0
        self.fallback_steps = 0
        free = np.argwhere(~grid.occ)
        self.free_xy = np.column_stack([grid.x0 + (free[:, 0] + 0.5) * grid.res,
                                        grid.y0 + (free[:, 1] + 0.5) * grid.res])
        self.res = grid.res
        self.p = np.asarray(x0, float)[None, :] + rng.normal(0.0, SIGMA_0, (n, 2))
        self.w = np.full(n, 1.0 / n)
        self.l_slow = self.l_fast = None
        self.est = np.asarray(x0, float).copy()
        self.sigma = SIGMA_0 * math.sqrt(2)
        self.last = {}

    def _uniform(self, k: int) -> np.ndarray:
        i = self.rng.integers(0, len(self.free_xy), k)
        return self.free_xy[i] + self.rng.uniform(-0.5, 0.5, (k, 2)) * self.res

    def _systematic(self, k: int) -> np.ndarray:
        c = np.cumsum(self.w)
        c[-1] = 1.0
        u = (self.rng.random() + np.arange(k)) / k
        return self.p[np.searchsorted(c, u)]

    def classify(self, angles_w: np.ndarray, z: np.ndarray) -> np.ndarray:
        """Bool per reading: static beam (kept) under the mixture at the previous estimate."""
        if not self.beam_filter:
            return np.ones(len(z), bool)
        zh = self.mm.raycast(self.est[None, :], angles_w)[0]
        zh = np.where(np.isfinite(zh), zh, self.max_range)
        p_hit = np.exp(-0.5 * ((z - zh) / SIGMA_OBS) ** 2) / (math.sqrt(2 * math.pi) * SIGMA_OBS)
        kappa = 1.0 / (1.0 - np.exp(-LAMBDA_SHORT * zh))
        p_short = np.where(z <= zh, kappa * LAMBDA_SHORT * np.exp(-LAMBDA_SHORT * z), 0.0)
        p_rand = 1.0 / self.max_range                 # p_max = 0: only readings below max range are used
        p = Z_HIT * p_hit + Z_SHORT * p_short + Z_RAND * p_rand
        return Z_HIT * p_hit / p > CHI

    def update(self, odo, dt: float, yaw: float, scan) -> dict:
        self.p = self.p + np.asarray(odo, float)[None, :] + self.rng.normal(0.0, SIGMA_U * math.sqrt(dt), (self.n, 2))
        a = np.asarray(scan.angles, float) + yaw
        z = np.asarray(scan.distances, float)
        ok = np.isfinite(z) & (z > 0) & (z < self.max_range)
        a, z = a[ok], z[ok]
        keep = self.classify(a, z) if len(z) else np.zeros(0, bool)
        fallback = False
        if len(z) and not keep.any():
            self.empty_run += 1
            if self.empty_fallback and self.empty_run >= self.empty_fallback:
                keep, fallback = np.ones(len(z), bool), True
                self.fallback_steps += 1
        else:
            self.empty_run = 0
        a, z = a[keep], z[keep]
        p_random, lbar, resampled = 0.0, None, False
        post = None
        if len(z) == 0:
            self.w = np.full(self.n, 1.0 / self.n)
        else:
            bx, by = z * np.cos(a), z * np.sin(a)
            px = self.p[:, 0:1] + bx[None, :]
            py = self.p[:, 1:2] + by[None, :]
            d = self.matcher._look(self.matcher.dist, px, py, OUT_CVAL_M)
            logp = -0.5 * (d / SIGMA_OBS) ** 2 - math.log(math.sqrt(2 * math.pi) * SIGMA_OBS)
            l = np.exp(logp.mean(axis=1))
            lbar = float(l.mean())
            if self.l_slow is None:
                self.l_slow = self.l_fast = lbar
            self.l_slow += ALPHA_SLOW * (lbar - self.l_slow)
            self.l_fast += ALPHA_FAST * (lbar - self.l_fast)
            if self.inject and self.l_slow > 0:
                p_random = min(NU, max(0.0, 1.0 - self.l_fast / self.l_slow))
            w = self.w * l
            s = w.sum()
            self.w = w / s if s > 0 else np.full(self.n, 1.0 / self.n)
            post = (self.w[:, None] * self.p).sum(axis=0)
            k_rand = int(math.floor(p_random * self.n))
            ess = 1.0 / float((self.w ** 2).sum())
            if ess < GAMMA * self.n or k_rand > 0:
                parts = [self._systematic(self.n - k_rand)]
                if k_rand:
                    parts.append(self._uniform(k_rand))
                self.p = np.vstack(parts)
                self.w = np.full(self.n, 1.0 / self.n)
                resampled = True
        mean = (self.w[:, None] * self.p).sum(axis=0)
        dv = self.p - mean[None, :]
        self.sigma = float(math.sqrt(max(0.0, (self.w * (dv ** 2).sum(axis=1)).sum())))
        self.est = post if (self.estimate == "posterior" and post is not None) else mean
        self.last = {"kept": int(len(z)) if not fallback else 0, "readings": int(ok.sum()), "p_random": p_random,
                     "lbar": lbar, "resampled": resampled, "fallback": fallback}
        return self.last


class MCLPoseSource:
    """mode "mean" (AF-MCL output, no hover gate) or "gate" (quality 0 while sigma > SIGMA_GATE)."""

    def __init__(self, est, grid, scan_fn, max_range: float, rng, mode: str = "mean", n: int = N_PARTICLES,
                 beam_filter: bool = True, inject: bool = True, estimate: str = ESTIMATE,
                 empty_fallback: int = EMPTY_FALLBACK):
        if mode not in ("mean", "gate"):
            raise ValueError(mode)
        self.est, self.scan_fn, self.mode = est, scan_fn, mode
        self.grid, self.max_range, self.rng = grid, max_range, rng
        self.n, self.beam_filter, self.inject = n, beam_filter, inject
        self.estimate, self.empty_fallback = estimate, empty_fallback
        self.pf = None
        self.prev_raw = None
        self.prev_t = None
        self.ambiguous = False
        self.conv = 0
        self.events: list[dict] = []
        self.errs: list[float] = []
        self.hover_steps = 0
        self.inject_steps = 0
        self.injected = 0
        self.empty_steps = 0
        self.sigmas: list[float] = []
        self.update_ms: list[float] = []

    def __call__(self, truth):
        import time
        raw = self.est(truth)
        rxy = np.array([raw.x, raw.y])
        if self.pf is None:
            self.pf = AFMCL(self.grid, self.max_range, rxy, self.rng, self.n, self.beam_filter, self.inject,
                            self.estimate, self.empty_fallback)
            odo, dt = np.zeros(2), 0.0
        else:
            odo, dt = rxy - self.prev_raw, truth.t - self.prev_t
        self.prev_raw, self.prev_t = rxy, truth.t
        scan = self.scan_fn(truth)
        t0 = time.perf_counter()
        info = self.pf.update(odo, dt, raw.yaw, scan)
        self.update_ms.append((time.perf_counter() - t0) * 1e3)
        self.inject_steps += int(info["p_random"] > 0)
        self.injected += int(math.floor(info["p_random"] * self.n))
        self.empty_steps += int(info["kept"] == 0)
        out = self.pf.est
        sig = self.pf.sigma
        self.sigmas.append(sig)
        err = float(math.hypot(out[0] - truth.x, out[1] - truth.y))
        self.errs.append(err)
        if not self.ambiguous and sig > SIGMA_GATE:
            self.ambiguous, self.conv = True, 0
            self.events.append({"t_trigger": round(truth.t, 4), "reason": "sigma", "t_end": None,
                                "recover_s": None, "result": "open", "err_m": None,
                                "pre_err_m": round(err, 4), "max_sigma_m": round(sig, 3)})
        elif self.ambiguous:
            ev = self.events[-1]
            ev["max_sigma_m"] = round(max(ev["max_sigma_m"], sig), 3)
            self.conv = self.conv + 1 if sig <= SIGMA_GATE else 0
            if self.conv >= N_CONV:
                self.ambiguous = False
                ev.update({"t_end": round(truth.t, 4), "recover_s": round(truth.t - ev["t_trigger"], 4),
                           "result": "accepted", "err_m": round(err, 4)})
        hover = self.mode == "gate" and self.ambiguous
        self.hover_steps += int(hover)
        q = 0 if hover else (raw.quality if raw.quality > 0 else 50)
        return replace(raw, x=float(out[0]), y=float(out[1]), quality=q, sigma_xy=sig)
