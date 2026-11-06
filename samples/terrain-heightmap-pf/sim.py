"""Flight simulation over a real DEM: truth, drifting odometry, local heightmap and radar altimeter.

One run produces three navigation solutions on the same flight and sensor noise:
compass-aligned odometry, the heightmap-gradient particle filter, and batch TERCOM.
"""
import os
import time
from dataclasses import dataclass, field, replace

import numpy as np
from scipy.ndimage import gaussian_filter

import core

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@dataclass
class Config:
    # flight
    length_m: float = 10000.0
    speed: float = 20.0
    dt: float = 1.0
    start_margin_m: float = 2500.0
    # odometry (VIO-like, compass-aligned): per-run scale factor and compass bias
    odo_scale_sigma: float = 0.02
    compass_bias_sigma_deg: float = 3.0
    compass_rw_deg_sqrt_s: float = 0.05
    odo_vel_noise: float = 0.3
    # reference DEM vs world: the world is the DEM plus correlated error (GLO-30 is not truth)
    dem_err_sigma: float = 2.0
    dem_err_corr_cells: float = 2.0
    # local heightmap observation
    patch_cells: int = 41
    swath_m: float = 600.0
    obs_noise: float = 2.0
    obs_res_m: float = 30.0
    obs_scale_err: float = 0.01
    obs_dropout: float = 0.05
    # matcher / PF
    prep: str = "none"            # "none" (terrain heights) or "ndsm" (height above local ground)
    feature: str = "binary"       # "binary" (paper) or "grad"
    grad_thr: float = 2.0         # m per cell for "binary"
    ndsm_open_cells: int = 5
    blur_cells: float = 1.0
    n_particles: int = 2000
    update_every_m: float = 150.0
    jitter_frac: float = 0.05
    jitter_min_m: float = 3.0
    kmeans_k: int = 4
    weight_power: float = 1.0
    init_sigma_m: float = 100.0
    init_offset_m: float = 0.0    # extra deterministic offset of the initial guess (convergence test)
    # radar altimeter TERCOM baseline
    radalt_noise: float = 1.0
    baro_noise: float = 0.5
    baro_bias_sigma: float = 20.0
    tercom_every_m: float = 1000.0
    tercom_profile_m: float = 2000.0
    tercom_radius_m: float = 600.0
    tercom_step_m: float = 15.0
    tercom_accept_ratio: float = 0.9
    methods: tuple = field(default=("pf", "tercom"))


SMOOTH_SUFFIX = "_smooth"
SMOOTH_SIGMA_CELLS = 10.0


def load_region(name):
    """Real GLO-30 window; '<region>_smooth' is a control with sub-300 m features (trees, villages) blurred away."""
    base = name[:-len(SMOOTH_SUFFIX)] if name.endswith(SMOOTH_SUFFIX) else name
    z = np.load(os.path.join(DATA, f"{base}.npz"))
    dem = z["dem"].astype(np.float64)
    if base != name:
        dem = gaussian_filter(dem, SMOOTH_SIGMA_CELLS)
    return dem, float(z["res"])


def rot(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])


def make_world(dem, cfg, rng):
    e = gaussian_filter(rng.normal(0, 1, dem.shape), cfg.dem_err_corr_cells)
    return dem + e * (cfg.dem_err_sigma / e.std())


def make_trajectory(dem, res, cfg, rng):
    """Weaving path heading roughly across the map; 1 sample per dt."""
    h, w = dem.shape
    n = int(cfg.length_m / (cfg.speed * cfg.dt)) + 1
    base = np.deg2rad(rng.uniform(25, 65))
    ph1, ph2 = rng.uniform(0, 2 * np.pi, 2)
    s = np.arange(n) * cfg.speed * cfg.dt
    hdg = base + np.deg2rad(35) * np.sin(2 * np.pi * s / 3000 + ph1) + np.deg2rad(20) * np.sin(2 * np.pi * s / 1100 + ph2)
    step = cfg.speed * cfg.dt * np.stack([np.cos(hdg), np.sin(hdg)], 1)
    start = np.array([cfg.start_margin_m, cfg.start_margin_m]) + rng.uniform(0, 1500, 2)
    pos = start + np.vstack([[0, 0], np.cumsum(step[:-1], 0)])
    lim = np.array([w, h]) * res - cfg.start_margin_m * 0.6
    if np.any(pos > lim) or np.any(pos < cfg.start_margin_m * 0.6):
        raise ValueError("trajectory leaves the map; enlarge region or shorten flight")
    return pos, s


def make_odometry(truth, cfg, rng):
    """Odometry increments in the world frame as seen through compass bias and scale error."""
    n = len(truth)
    scale = 1 + rng.normal(0, cfg.odo_scale_sigma)
    bias = np.deg2rad(rng.normal(0, cfg.compass_bias_sigma_deg)
                      + np.cumsum(rng.normal(0, cfg.compass_rw_deg_sqrt_s * np.sqrt(cfg.dt), n)))
    d_true = np.diff(truth, axis=0)
    d = np.empty_like(d_true)
    for k in range(n - 1):
        d[k] = scale * rot(bias[k]) @ d_true[k] + rng.normal(0, cfg.odo_vel_noise * cfg.dt, 2)
    return d, bias


def observe_patch(world, res, truth, k, compass_err, cfg, rng):
    """Local north-aligned heightmap around truth[k] as a downward stereo/LiDAR/SfM map would give.

    Errors: compass rotation, horizontal+vertical scale error (SfM scale), coarser native
    resolution, white height noise, unknown vertical offset, swath coverage of the recent
    track only, random cell dropout. Returns (patch, valid_mask) on the map grid.
    """
    n = cfg.patch_cells
    c = n // 2
    half = c * res
    nf = max(2, int(round(2 * half / cfg.obs_res_m)) + 1)
    f = np.linspace(-half, half, nf)
    fu, fv = np.meshgrid(f, f)
    R = rot(compass_err) * (1 + cfg.obs_scale_err)
    pe = truth[k, 0] + R[0, 0] * fu + R[0, 1] * fv
    pn = truth[k, 1] + R[1, 0] * fu + R[1, 1] * fv
    fine = core.bilinear(world, pe, pn, res) + rng.normal(0, cfg.obs_noise, fu.shape)
    g = (np.arange(n) - c) * res
    gu, gv = np.meshgrid(g, g)
    step = f[1] - f[0]
    patch = core.bilinear(fine, gu + half, gv + half, step)
    patch = patch * (1 + cfg.obs_scale_err) + rng.normal(0, 50)
    # swath coverage: cells near the track flown over the last patch-length of path
    span = int(2 * half / (cfg.speed * cfg.dt))
    past = truth[max(0, k - span):k + 1:max(1, int(res / (cfg.speed * cfg.dt)))]
    cell_e = truth[k, 0] + R[0, 0] * gu + R[0, 1] * gv
    cell_n = truth[k, 1] + R[1, 0] * gu + R[1, 1] * gv
    d2 = (cell_e[..., None] - past[:, 0]) ** 2 + (cell_n[..., None] - past[:, 1]) ** 2
    mask = (d2.min(-1) <= (cfg.swath_m / 2) ** 2) & (rng.random(gu.shape) >= cfg.obs_dropout)
    mask &= np.isfinite(patch)
    return patch, mask


def prep_heights(h, cfg, mask=None):
    if cfg.prep == "none":
        return h
    if cfg.prep == "ndsm":
        hh = h.copy()
        if mask is not None:
            hh[~mask] = np.median(h[mask])
        return core.height_above_ground(hh, cfg.ndsm_open_cells)
    raise ValueError(cfg.prep)


def template_features(patch, mask, cfg):
    h = prep_heights(patch, cfg, mask)
    h = np.where(mask, h, np.nan)
    f = core.features(h, cfg.feature, cfg.grad_thr)
    valid = np.isfinite(f)
    return np.where(valid, f, 0.0), valid


def map_features(dem, cfg):
    return core.features(prep_heights(dem, cfg), cfg.feature, cfg.grad_thr)


def run(region, seed, cfg, dem=None, res=None, fmap=None):
    """One Monte Carlo run. Returns dict with per-step distance and errors, timings, events."""
    if dem is None:
        dem, res = load_region(region)
    if fmap is None:
        fmap = map_features(dem, cfg)
    rng = np.random.default_rng(seed)
    world = make_world(dem, cfg, rng)
    truth, dist = make_trajectory(dem, res, cfg, rng)
    d_odo, compass_err = make_odometry(truth, cfg, rng)
    n = len(truth)

    init_dir = rng.uniform(0, 2 * np.pi)
    start_guess = truth[0] + cfg.init_offset_m * np.array([np.cos(init_dir), np.sin(init_dir)])
    start_guess = start_guess + rng.normal(0, cfg.init_sigma_m, 2)
    odo = start_guess + np.vstack([[0, 0], np.cumsum(d_odo, 0)])

    out = {"dist": dist, "err_odom": np.linalg.norm(odo - truth, axis=1), "odo": odo}

    if "pf" in cfg.methods:
        pf = core.HeightmapPF(cfg.n_particles, start_guess, cfg.init_sigma_m + cfg.init_offset_m / 2, rng,
                              cfg.kmeans_k, cfg.weight_power)
        est = start_guess.copy()
        nav = np.empty((n, 2))
        nav[0] = est
        last_upd = 0.0
        acc = np.zeros(2)
        t_upd, spreads = [], []
        for k in range(1, n):
            pf.predict(d_odo[k - 1])
            est = est + d_odo[k - 1]
            acc += d_odo[k - 1]
            if dist[k] - last_upd >= cfg.update_every_m and dist[k] >= cfg.patch_cells * res / 2:
                moved = np.linalg.norm(acc)
                patch, mask = observe_patch(world, res, truth, k, compass_err[k], cfg, rng)
                t0 = time.perf_counter()
                templ, valid = template_features(patch, mask, cfg)
                c = pf.p.mean(0)
                half_ext = float(np.clip(3 * pf.spread(), 150, 2000))
                sm = core.similarity_map(fmap, templ, valid, c[0], c[1], half_ext, res, cfg.blur_cells)
                if sm is not None and templ[valid].std() > 0:
                    jit = max(cfg.jitter_min_m, cfg.jitter_frac * moved)
                    pf.update(sm[0], sm[1], sm[2], res, jit)
                est = pf.estimate()
                t_upd.append(time.perf_counter() - t0)
                spreads.append(pf.spread())
                last_upd = dist[k]
                acc[:] = 0
            nav[k] = est
        out["err_pf"] = np.linalg.norm(nav - truth, axis=1)
        out["nav_pf"] = nav
        out["t_update_s"] = np.array(t_upd)
        out["pf_spread"] = np.array(spreads)

    if "tercom" in cfg.methods:
        baro_bias = rng.normal(0, cfg.baro_bias_sigma)
        h_true = core.bilinear(world, truth[:, 0], truth[:, 1], res)
        prof_meas = h_true + baro_bias + rng.normal(0, cfg.baro_noise, n) + rng.normal(0, cfg.radalt_noise, n)
        corr = np.zeros(2)
        nav = odo.copy()
        last_fix = 0.0
        n_prof = int(cfg.tercom_profile_m / (cfg.speed * cfg.dt))
        t_fix, accepted = [], 0
        for k in range(1, n):
            nav[k] = odo[k] + corr
            if dist[k] - last_fix >= cfg.tercom_every_m and k >= n_prof:
                sl = slice(k - n_prof + 1, k + 1)
                track = odo[sl] + corr
                t0 = time.perf_counter()
                fx = core.tercom_fix(dem, res, track[:, 0], track[:, 1], prof_meas[sl],
                                     cfg.tercom_radius_m, cfg.tercom_step_m)
                t_fix.append(time.perf_counter() - t0)
                last_fix = dist[k]
                if fx is not None:
                    de, dn, best, second = fx
                    on_border = max(abs(de), abs(dn)) >= cfg.tercom_radius_m - 1e-6
                    if best < cfg.tercom_accept_ratio * second and not on_border:
                        corr += np.array([de, dn])
                        nav[k] = odo[k] + corr
                        accepted += 1
        out["err_tercom"] = np.linalg.norm(nav - truth, axis=1)
        out["nav_tercom"] = nav
        out["t_tercom_s"] = np.array(t_fix)
        out["tercom_accepted"] = accepted
        out["tercom_attempts"] = len(t_fix)
    out["truth"] = truth
    return out


def terrain_stats(dem, res):
    g = core.gradient_magnitude(dem)
    lp = gaussian_filter(dem, 33)
    return {
        "height_std_m": float(dem.std()),
        "local_relief_std_m": float((dem - lp).std()),
        "mean_grad_m_per_cell": float(g.mean()),
        "frac_grad_gt_2m": float((g > 2).mean()),
        "size_km": [round(dem.shape[1] * res / 1000, 1), round(dem.shape[0] * res / 1000, 1)],
    }


def with_(cfg, **kw):
    return replace(cfg, **kw)
