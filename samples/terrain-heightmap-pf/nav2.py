"""v2 navigator: SSD likelihood with self-calibrated noise, Cramer-Rao information gate,
compass bias as a particle state, and a no-truth confidence record per update.

Uses the same world, trajectory, odometry and heightmap sensor as sim.run (same RNG draw
order), so for a given seed v1 and v2 fly the identical flight.
"""
import time
from dataclasses import dataclass, replace

import numpy as np
from scipy.ndimage import gaussian_filter

import core
import sim


@dataclass
class V2:
    kappa: float = 9.0              # cells per independent residual (correlation inflation)
    ess_floor: float = 0.1          # temper an update so that ESS stays >= this fraction
    gate: bool = True
    null_frac: float = 0.3          # fraction of the noise-only NCC maximum not counted as signal in the CRB
    gate_crb_cells: float = 2.0     # skip the update when the CRB worst-axis std exceeds this many cells
    heading: bool = True
    bias_sigma0_deg: float = 10.0
    bias_max_deg: float = 36.0
    angle_step_deg: float = 3.0
    bias_rw_deg: float = 0.3        # per update
    blur_cells: float = 1.0


def crop(fmap, center_e, center_n, half_extent_m, res, tshape):
    th, tw = tshape
    h, w = fmap.shape
    ci, cj = int(round(center_n / res)), int(round(center_e / res))
    k = int(np.ceil(half_extent_m / res))
    i0, i1 = max(0, ci - k - th // 2), min(h, ci + k + th // 2 + 1)
    j0, j1 = max(0, cj - k - tw // 2), min(w, cj + k + tw // 2 + 1)
    sub = fmap[i0:i1, j0:j1]
    if sub.shape[0] < th or sub.shape[1] < tw:
        return None
    return sub, (j0 + tw // 2) * res, (i0 + th // 2) * res


def angle_grid(b, step, bmax):
    lo = np.floor(b.min() / step) * step
    hi = np.ceil(b.max() / step) * step
    lo, hi = max(lo, -bmax), min(hi, bmax)
    return np.arange(lo, hi + step / 2, step) if hi > lo else np.array([lo])


def measure(pf, fmap, patch, mask, cfg, v2, res, half_ext):
    """Log-likelihood maps per heading hypothesis plus the information diagnostics."""
    c = pf.p[:, :2].mean(0)
    step = np.deg2rad(v2.angle_step_deg)
    angles = angle_grid(pf.p[:, 2], step, np.deg2rad(v2.bias_max_deg)) if v2.heading else np.array([0.0])
    rhos, ns, valids = [], [], []
    box = None
    n_full = mask.sum()
    for a in angles:
        h, m = (core.rotate_patch(patch, mask, a) if a != 0 else (np.where(mask, patch, 0.0), mask))
        templ, valid = sim.template_features(h, m, cfg)
        if valid.sum() < 0.5 * n_full or templ[valid].std() == 0:
            return None
        if box is None:
            box = crop(fmap, c[0], c[1], half_ext, res, templ.shape)
            if box is None:
                return None
        rho, n, _ = core.ncc_map(box[0], templ, valid)
        rhos.append(rho)
        ns.append(n)
        valids.append(valid)
    logl = core.ncc_loglik(rhos, float(np.mean(ns)), v2.kappa)
    if v2.blur_cells > 0:
        logl = [gaussian_filter(l, v2.blur_cells) for l in logl]
    rho_best = max(float(r.max()) for r in rhos)
    # max NCC that pure noise reaches over M independent placements with n/kappa independent cells
    n_eff = float(np.mean(ns)) / v2.kappa
    n_place = max(sum(r.size for r in rhos) / v2.kappa, 2.0)
    rho_null = float(np.sqrt(2 * np.log(n_place) / n_eff))
    # information at the current estimate, with the mask of the heading closest to the mean bias
    kb = int(np.argmin(np.abs(angles - pf.p[:, 2].mean())))
    th, tw = valids[kb].shape
    ci, cj = int(round(c[1] / res)) - th // 2, int(round(c[0] / res)) - tw // 2
    ok = ci >= 0 and cj >= 0 and ci + th <= fmap.shape[0] and cj + tw <= fmap.shape[1]
    crb = (core.ncc_crb(fmap[ci:ci + th, cj:cj + tw], valids[kb], rho_best, v2.kappa, res, v2.null_frac * rho_null)
           if ok else float("inf"))
    return logl, angles, box[1], box[2], crb, rho_best / rho_null


def run_v2(dem, res, seed, cfg, v2, fmap, traj_fn=None):
    rng = np.random.default_rng(seed)
    world = sim.make_world(dem, cfg, rng)
    truth, dist = (traj_fn or sim.make_trajectory)(dem, res, cfg, rng)
    d_odo, compass_err = sim.make_odometry(truth, cfg, rng)
    n = len(truth)
    init_dir = rng.uniform(0, 2 * np.pi)
    start_guess = truth[0] + cfg.init_offset_m * np.array([np.cos(init_dir), np.sin(init_dir)])
    start_guess = start_guess + rng.normal(0, cfg.init_sigma_m, 2)
    odo = start_guess + np.vstack([[0, 0], np.cumsum(d_odo, 0)])

    pf = core.HeadingPF(cfg.n_particles, start_guess, cfg.init_sigma_m + cfg.init_offset_m / 2,
                        np.deg2rad(v2.bias_sigma0_deg) if v2.heading else 0.0, np.deg2rad(v2.bias_max_deg),
                        rng, cfg.kmeans_k)
    est = start_guess.copy()
    nav = np.empty((n, 2))
    nav[0] = est
    last_upd, acc = 0.0, 0.0
    rec = {k: [] for k in ("k", "spread", "ess", "beta", "crb", "signif", "applied", "bias_est", "bias_true", "t")}
    for k in range(1, n):
        pf.predict(d_odo[k - 1])
        b = pf.p[:, 2].mean()
        cb, sb = np.cos(-b), np.sin(-b)
        d = d_odo[k - 1]
        est = est + np.array([cb * d[0] - sb * d[1], sb * d[0] + cb * d[1]])
        acc += np.linalg.norm(d)
        if dist[k] - last_upd >= cfg.update_every_m and dist[k] >= cfg.patch_cells * res / 2:
            patch, mask = sim.observe_patch(world, res, truth, k, compass_err[k], cfg, rng)
            t0 = time.perf_counter()
            pf.diffuse(max(cfg.jitter_min_m, cfg.jitter_frac * acc), np.deg2rad(v2.bias_rw_deg) if v2.heading else 0.0)
            half_ext = float(np.clip(3 * pf.spread(), cfg.search_min_m, cfg.search_max_m))
            m = measure(pf, fmap, patch, mask, cfg, v2, res, half_ext)
            applied, ess, beta, crb, sig = False, 1.0, 0.0, float("inf"), 0.0
            if m is not None:
                logl, angles, oe, on, crb, sig = m
                if not v2.gate or crb <= v2.gate_crb_cells * res:
                    ll = pf.loglik_at(logl, angles, oe, on, res)
                    ess, beta = pf.update(ll, v2.ess_floor)
                    applied = True
            if applied:
                est = pf.estimate()
            rec["t"].append(time.perf_counter() - t0)
            for key, val in (("k", k), ("spread", pf.spread()), ("ess", ess), ("beta", beta), ("crb", crb), ("signif", sig),
                             ("applied", applied), ("bias_est", float(pf.p[:, 2].mean())),
                             ("bias_true", float(compass_err[k]))):
                rec[key].append(val)
            last_upd = dist[k]
            acc = 0.0
        nav[k] = est
    out = {"dist": dist, "truth": truth, "odo": odo, "err_odom": np.linalg.norm(odo - truth, axis=1),
           "nav_pf": nav, "err_pf": np.linalg.norm(nav - truth, axis=1)}
    out.update({f"rec_{k}": np.array(v) for k, v in rec.items()})
    return out


def with_(v2, **kw):
    return replace(v2, **kw)
