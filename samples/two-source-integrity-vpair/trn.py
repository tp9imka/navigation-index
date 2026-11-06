"""Terrain-relative navigation on the real VPAIR track: simulated sensors over the real NRW DSM.

The sensors are simulated; the terrain they see and the poses they are taken at are real:
- radar / laser altimeter: ../blind-flight-bench/sim.radar_range on the 1 m NRW DSM at the true
  VPAIR position and height (beam footprint = leading edge in a 40 deg cone; laser = nadir point),
  10 Hz, plus that bench's noise, dropout, loss-of-lock and outlier model, and a barometric
  altitude with bias and drift. Matched by batch TERCOM (../terrain-heightmap-pf/core.py metric)
  against the leading-edge "beam map" of the DSM (../blind-flight-bench/navs.beam_map).
- downward heightmap (scanning LiDAR / stereo): ../terrain-heightmap-pf/sim.observe_patch on the
  DSM at 5 m, matched by that sample's v2 particle filter (NCC likelihood, Cramer-Rao information
  gate, compass bias state; nav2.measure + core.HeadingPF).

Both navigators dead-reckon with the same nadir VO the fusion uses and nothing else: no visual
fixes, so their errors are independent of the visual source (not of VO).
Each returns fixes {frame: (east, north, sigma_per_axis_m)} in the grid frame plus diagnostics.
A fault hook replaces chosen fixes by the secondary peak of the same match surface (ambiguity).
"""
import importlib.util
import math
import os
import sys
import time
from dataclasses import dataclass, replace

import numpy as np
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
HPF = os.path.join(HERE, "..", "terrain-heightmap-pf")
BFB = os.path.join(HERE, "..", "blind-flight-bench")
sys.path.insert(0, HPF)
import core  # noqa: E402  (terrain-heightmap-pf)
import nav2  # noqa: E402
import sim as hpf_sim  # noqa: E402


def _load_bfb(name):
    """blind-flight-bench modules by path: its 'sim' collides with terrain-heightmap-pf's."""
    sys.path.insert(0, BFB)
    try:
        spec = importlib.util.spec_from_file_location(f"bfb_{name}", os.path.join(BFB, f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(BFB)
    return mod


bfb = _load_bfb("sim")
bfb_navs = _load_bfb("navs")

ALT_HZ = 10.0
FRAME_DT = 1.0


# ---------------------------------------------------------------- altimeter + TERCOM

@dataclass
class AltCfg:
    beam: bool = True              # True: radar leading edge in the beam cone; False: laser point
    beam_full_deg: float = bfb.RadarModel.beam_full_deg
    fix_every_m: float = 900.0
    profile_m: float = 1800.0
    radius_m: float = 300.0
    radius_growth: float = 0.1     # + this fraction of distance since the last accepted fix
    radius_max_m: float = 1500.0
    step_m: float = 10.0
    max_points: int = 200
    accept_ratio: float = 0.9      # ../terrain-heightmap-pf TERCOM ambiguity rule
    sep_cells: int = 3             # 'second best' must be this many steps from the best
    corr_m: float = 60.0           # profile samples closer than this are not independent (sigma estimate)
    sigma_floor_m: float = 5.0


def interp_track(truth_g, msl, hz=ALT_HZ):
    """Linear interpolation of the 1 frame/s VPAIR poses to the altimeter rate."""
    n = len(truth_g)
    t = np.arange(0, n - 1 + 1e-9, 1.0 / hz)
    e = np.interp(t, np.arange(n), truth_g[:, 0])
    nn = np.interp(t, np.arange(n), truth_g[:, 1])
    return t, e, nn, np.interp(t, np.arange(n), msl)


def simulate_altimeter(dsm1, truth_g, msl, cfg, rng):
    """Measured terrain height (baro altitude - measured AGL) at ALT_HZ; NaN = no measurement."""
    rm = bfb.RadarModel(beam_full_deg=cfg.beam_full_deg, footprint=cfg.beam)
    am = bfb.AltRefModel()
    t, e, n, alt = interp_track(truth_g, msl)
    rng_m = bfb.radar_range(dsm1, 1.0, e, n, alt, rm)
    agl = rng_m + rng.standard_normal(len(t)) * (rm.noise_m + rm.noise_frac * rng_m)
    out = rng.random(len(t)) < rm.outlier_p
    agl[out] += rng.uniform(*rm.outlier_m, out.sum()) * rng.choice([-1, 1], out.sum())
    keep = rng.random(len(t)) >= rm.dropout_p
    k = 0
    while k < len(t):
        if rng.random() < rm.burst_p / ALT_HZ * bfb.SAMPLE_HZ:
            nb = int(rng.uniform(*rm.burst_s) * ALT_HZ)
            keep[k:k + nb] = False
            k += nb
        k += 1
    baro = alt + am.bias_sigma_m * rng.standard_normal() + am.drift_sigma_mps * rng.standard_normal() * t
    h = np.where(keep, baro - agl, np.nan)
    nadir_agl = alt - core.bilinear(dsm1, e, n, 1.0)
    return {"t": t, "h": h, "agl_true_nadir": nadir_agl, "range_true": rng_m, "dropped": int((~keep).sum()),
            "outliers": int(out.sum())}


def tercom_surface(ref, res, track_e, track_n, profile, radius_m, step_m):
    """MAD of the mean-removed profile against ref over a translation grid (core.tercom_fix's metric)."""
    offs = np.arange(-radius_m, radius_m + step_m / 2, step_m)
    de, dn = np.meshgrid(offs, offs)
    m = core.bilinear(ref, track_e[None, :] + de.ravel()[:, None], track_n[None, :] + dn.ravel()[:, None], res)
    p = profile - profile.mean()
    m = m - m.mean(axis=1, keepdims=True)
    mad = np.abs(m - p[None, :]).mean(axis=1)
    return de.ravel(), dn.ravel(), np.where(np.isnan(mad), np.inf, mad)


def tercom_peaks(de, dn, mad, step_m, sep_cells, n_eff):
    """Best offset, secondary peak (>= sep_cells steps away) and a no-truth sigma.

    sigma: the MAD surface read as a likelihood with the noise level self-calibrated from the best
    residual (as nav2's NCC likelihood does): w = exp(-n_eff/2 ((mad/best)^2 - 1)); sigma = sqrt of
    the larger eigenvalue of the weighted offset covariance."""
    b = int(np.argmin(mad))
    far = np.hypot(de - de[b], dn - dn[b]) > sep_cells * step_m
    s = int(np.flatnonzero(far)[np.argmin(mad[far])]) if far.any() else b
    best = max(mad[b], 1e-6)
    w = np.exp(-0.5 * n_eff * ((np.minimum(mad, 10 * best) / best) ** 2 - 1))
    w /= w.sum()
    mu = np.array([np.sum(w * de), np.sum(w * dn)])
    d = np.stack([de - mu[0], dn - mu[1]], 1)
    cov = (d * w[:, None]).T @ d
    sigma = math.sqrt(max(np.linalg.eigvalsh(cov)[-1], 0.0) + step_m ** 2 / 12)
    return b, s, float(sigma)


def run_tercom(ref, ref_res, alt, d_odo, start, start_pos, cfg, fault_frames=()):
    """VO dead reckoning (grid frame) + batch TERCOM fixes. d_odo[k] = VO step frame k => k+1."""
    n = len(d_odo) + 1
    pos = np.full((n, 2), np.nan)
    pos[start] = start_pos
    for k in range(start, n - 1):
        pos[k + 1] = pos[k] + d_odo[k]
    corr = np.zeros(2)
    fixes, diag = {}, []
    t_alt, h_alt = alt["t"], alt["h"]
    last_fix_dist = 0.0
    dist = np.concatenate([[0.0], np.cumsum(np.linalg.norm(d_odo, axis=1))])
    since_acc = 0.0
    for k in range(start + 1, n):
        flown = dist[k] - dist[start]
        if flown < cfg.profile_m or dist[k] - last_fix_dist < cfg.fix_every_m:
            continue
        last_fix_dist = dist[k]
        k0 = int(np.searchsorted(dist, dist[k] - cfg.profile_m))
        sel = np.flatnonzero((t_alt >= k0) & (t_alt <= k) & np.isfinite(h_alt))
        if len(sel) < 20:
            continue
        sel = sel[np.linspace(0, len(sel) - 1, min(len(sel), cfg.max_points)).astype(int)]
        tt = t_alt[sel]
        ke = np.interp(tt, np.arange(n), pos[:, 0]) + corr[0]
        kn = np.interp(tt, np.arange(n), pos[:, 1]) + corr[1]
        radius = min(cfg.radius_m + cfg.radius_growth * since_acc, cfg.radius_max_m)
        step = max(cfg.step_m, radius / 40)
        t0 = time.perf_counter()
        de, dn, mad = tercom_surface(ref, ref_res, ke, kn, h_alt[sel], radius, step)
        n_eff = max(cfg.profile_m / cfg.corr_m, 2.0)
        b, s, sigma = tercom_peaks(de, dn, mad, step, cfg.sep_cells, n_eff)
        dt = time.perf_counter() - t0
        on_border = max(abs(de[b]), abs(dn[b])) >= radius - step / 2
        accepted = bool(np.isfinite(mad[b]) and mad[b] < cfg.accept_ratio * mad[s] and not on_border)
        rec = {"k": k, "accepted": accepted, "mad_best": float(mad[b]), "mad_second": float(mad[s]),
               "radius_m": radius, "sigma_m": sigma, "sep_m": float(math.hypot(de[s] - de[b], dn[s] - dn[b])),
               "t_s": dt, "faulted": False}
        since_acc += cfg.fix_every_m
        if accepted:
            corr = corr + np.array([de[b], dn[b]])
            since_acc = 0.0
            p = pos[k] + corr
            sig = max(sigma, cfg.sigma_floor_m)
            if k in fault_frames:
                p = p + np.array([de[s] - de[b], dn[s] - dn[b]])
                rec["faulted"] = True
            fixes[k] = (float(p[0]), float(p[1]), float(sig))
        diag.append(rec)
    return fixes, diag


# ---------------------------------------------------------------- downward heightmap + v2 PF

@dataclass
class MapCfg:
    res: float = 5.0
    patch_cells: int = 61          # 300 m square
    swath_m: float = 300.0         # ~ 2 x 270 m AGL x tan(29 deg): a 58 deg cross-track scanner
    obs_res_m: float = 5.0
    obs_noise: float = 0.5
    obs_scale_err: float = 0.01
    obs_dropout: float = 0.05
    world_err_sigma: float = 1.0   # DSM (2021) vs surface at flight time, correlated: assumed
    world_err_corr_cells: float = 4.0
    update_every_frames: int = 2
    n_particles: int = 2000
    jitter_min_m: float = 2.0
    jitter_frac: float = 0.05
    search_min_m: float = 60.0
    search_max_m: float = 600.0
    init_sigma_m: float = 5.0
    sigma_infl: float = 1.0        # per-axis sigma = sigma_infl * spread / sqrt(2)
    sigma_floor_m: float = 3.0
    peak_sep_m: float = 30.0       # secondary peak for the ambiguity fault: at least this far from the best


def hpf_config(mc, speed):
    return replace(hpf_sim.Config(), patch_cells=mc.patch_cells, swath_m=mc.swath_m, obs_res_m=mc.obs_res_m,
                   obs_noise=mc.obs_noise, obs_scale_err=mc.obs_scale_err, obs_dropout=mc.obs_dropout,
                   feature="grad", speed=speed, dt=FRAME_DT, n_particles=mc.n_particles,
                   jitter_min_m=mc.jitter_min_m, jitter_frac=mc.jitter_frac, search_min_m=mc.search_min_m,
                   search_max_m=mc.search_max_m)


def secondary_peak(logl, angles, oe, on, res, sep_m):
    best = np.max(np.stack(logl), axis=0)
    i, j = np.unravel_index(int(np.argmax(best)), best.shape)
    ii, jj = np.mgrid[0:best.shape[0], 0:best.shape[1]]
    far = np.hypot(ii - i, jj - j) * res >= sep_m
    if not far.any():
        return None
    v = np.where(far, best, -np.inf)
    i2, j2 = np.unravel_index(int(np.argmax(v)), v.shape)
    return (np.array([oe + j * res, on + i * res]), np.array([oe + j2 * res, on + i2 * res]),
            float(best[i, j] - v[i2, j2]))


def run_heightmap_pf(dem_map, dem_world, truth_g, d_odo, heading_err, start, mc, v2, seed, fault_frames=()):
    """nav2.run_v2's loop on the VPAIR track with VPAIR VO as odometry. heading_err: rad, sim convention
    (d_odo = rot(err) d_true), rotates the sensor patch the same way the AHRS heading would."""
    rng = np.random.default_rng(seed)
    res = mc.res
    speed = float(np.mean(np.linalg.norm(np.diff(truth_g, axis=0), axis=1)))
    cfg = hpf_config(mc, speed)
    fmap = hpf_sim.map_features(dem_map, cfg)
    e = gaussian_filter(rng.normal(0, 1, dem_world.shape), mc.world_err_corr_cells)
    world = dem_world + e * (mc.world_err_sigma / e.std())
    n = len(truth_g)
    pf = core.HeadingPF(cfg.n_particles, truth_g[start], mc.init_sigma_m, np.deg2rad(v2.bias_sigma0_deg),
                        np.deg2rad(v2.bias_max_deg), rng, cfg.kmeans_k)
    est = truth_g[start].copy()
    nav = np.full((n, 2), np.nan)
    nav[start] = est
    fixes, diag = {}, []
    acc = 0.0
    for k in range(start + 1, n):
        d = d_odo[k - 1]
        pf.predict(d)
        b = pf.p[:, 2].mean()
        cb, sb = math.cos(-b), math.sin(-b)
        est = est + np.array([cb * d[0] - sb * d[1], sb * d[0] + cb * d[1]])
        acc += float(np.linalg.norm(d))
        if (k - start) % mc.update_every_frames == 0 and k - start >= cfg.patch_cells * res / 2 / speed:
            patch, mask = hpf_sim.observe_patch(world, res, truth_g, k, heading_err, cfg, rng)
            t0 = time.perf_counter()
            pf.diffuse(max(cfg.jitter_min_m, cfg.jitter_frac * acc), np.deg2rad(v2.bias_rw_deg))
            half_ext = float(np.clip(3 * pf.spread(), cfg.search_min_m, cfg.search_max_m))
            m = nav2.measure(pf, fmap, patch, mask, cfg, v2, res, half_ext)
            applied, crb, sig, peak = False, float("inf"), 0.0, None
            if m is not None:
                logl, angles, oe, on, crb, sig = m
                if not v2.gate or crb <= v2.gate_crb_cells * res:
                    pf.update(pf.loglik_at(logl, angles, oe, on, res), v2.ess_floor)
                    applied = True
                    peak = secondary_peak(logl, angles, oe, on, res, mc.peak_sep_m)
            if applied:
                est = pf.estimate()
            spread = pf.spread()
            rec = {"k": k, "applied": applied, "crb_m": crb, "signif": sig, "spread_m": spread,
                   "bias_est_deg": math.degrees(float(pf.p[:, 2].mean())), "t_s": time.perf_counter() - t0,
                   "faulted": False}
            if applied:
                p = est.copy()
                if k in fault_frames and peak is not None:
                    p = p + (peak[1] - peak[0])
                    rec["faulted"] = True
                    rec["fault_offset_m"] = float(np.linalg.norm(peak[1] - peak[0]))
                fixes[k] = (float(p[0]), float(p[1]), max(mc.sigma_infl * spread / math.sqrt(2), mc.sigma_floor_m))
            diag.append(rec)
            acc = 0.0
        nav[k] = est
    return fixes, diag, nav
