"""High-resolution test on real 1 m airborne LiDAR (Geobasis NRW DOM1/DGM1, Duelmen 4 x 4 km).

Question from the paper: does the literal binary-edge feature (|gradient| > 5 m) work when
the reference map is a 1 m LiDAR surface model, and how does it compare with continuous
gradient magnitude, at 1 m and at 30 m reference resolution? Same flights for every config.
Writes out/lidar_results.json, out/lidar_output.txt, out/lidar.png. Needs data/duelmen.npz
from fetch_lidar.py.
"""
import argparse
import json
import os
import time

import numpy as np

import nav2
import sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
BLOCK = 30

# 1 m: LiDAR-like local map 51 x 51 m (paper: 30-60 m), update every 10 m (paper), 10 m/s
CFG_1M = sim.with_(sim.Config(), methods=("pf",), length_m=4000.0, speed=10.0, patch_cells=51, swath_m=50.0,
                   obs_res_m=1.0, obs_noise=0.3, dem_err_sigma=0.3, dem_err_corr_cells=2.0,
                   update_every_m=10.0, jitter_min_m=0.5, init_sigma_m=15.0,
                   search_min_m=20.0, search_max_m=200.0)
# 30 m: same sensor and flight, map binned to 30 m, so the local map must be 21 x 21 cells (630 m)
CFG_30M = sim.with_(CFG_1M, patch_cells=21, swath_m=600.0, obs_res_m=30.0, dem_err_sigma=0.3,
                    update_every_m=150.0, jitter_min_m=3.0, search_min_m=150.0, search_max_m=400.0)
FEATURES = {"binary5": dict(feature="binary", grad_thr=5.0, weight_power=1.0, jitter_frac=0.05),
            "grad": dict(feature="grad", weight_power=3.0, jitter_frac=0.1)}


def block_mean(a, k):
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    return a[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def loop_trajectory(dem, res, cfg, rng):
    """Wobbly loop around the area centre, sampled every speed*dt metres of arc length."""
    h, w = dem.shape
    c = np.array([w, h]) * res / 2
    r0 = 0.3 * min(h, w) * res
    th = np.linspace(0, 2 * np.pi, 20000)
    ph = rng.uniform(0, 2 * np.pi, 2)
    r = r0 * (1 + 0.15 * np.sin(3 * th + ph[0]) + 0.08 * np.sin(7 * th + ph[1]))
    th0 = rng.uniform(0, 2 * np.pi)
    xy = c + np.stack([r * np.cos(th + th0), r * np.sin(th + th0)], 1)
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
    s = np.arange(0, min(cfg.length_m, arc[-1]), cfg.speed * cfg.dt)
    pos = np.stack([np.interp(s, arc, xy[:, 0]), np.interp(s, arc, xy[:, 1])], 1)
    return pos, s


def edge_stats(dem, thr):
    from core import gradient_magnitude
    g = gradient_magnitude(dem)
    return {"frac_edges": float((g > thr).mean()), "mean_grad": float(g.mean())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    a = ap.parse_args()
    z = np.load(os.path.join(HERE, "data", "duelmen.npz"))
    surfaces = {"dsm": z["dsm"].astype(np.float64), "dtm": z["dtm"].astype(np.float64)}
    seeds = list(range(300, 300 + a.seeds))
    results, lines = {"seeds": seeds, "configs": {}}, []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    log("| map | res | feature | filter | final err med/p90 [m] | RMSE med | odom final med | updates applied | ms/update med |")
    log("|---|---|---|---|---|---|---|---|---|")
    curves = {}
    for surf in ("dsm", "dtm"):
        for res_name, base, k in (("1m", CFG_1M, 1), ("30m", CFG_30M, BLOCK)):
            if surf == "dtm" and res_name == "30m":
                continue
            dem = surfaces[surf] if k == 1 else block_mean(surfaces[surf], k)
            res = float(k)
            for fname, fkw in FEATURES.items():
                cfg = sim.with_(base, **fkw)
                fmap = sim.map_features(dem, cfg)
                st = edge_stats(dem, 5.0)
                for filt in ("v1", "v2"):
                    t0 = time.time()
                    runs = []
                    for s in seeds:
                        if filt == "v1":
                            runs.append(sim.run(None, s, cfg, dem, res, fmap, traj_fn=loop_trajectory))
                        else:
                            runs.append(nav2.run_v2(dem, res, s, cfg, nav2.V2(), fmap, traj_fn=loop_trajectory))
                    fin = np.array([r["err_pf"][-1] for r in runs])
                    rmse = np.median([np.sqrt(np.mean(r["err_pf"] ** 2)) for r in runs])
                    odo = np.median([r["err_odom"][-1] for r in runs])
                    if filt == "v1":
                        tt = np.concatenate([r["t_update_s"] for r in runs])
                        app = None
                    else:
                        tt = np.concatenate([r["rec_t"] for r in runs])
                        app = float(np.mean([r["rec_applied"].mean() for r in runs]))
                    key = f"{surf}_{res_name}_{fname}_{filt}"
                    results["configs"][key] = {"final_median": float(np.median(fin)), "final_p90": float(np.percentile(fin, 90)),
                                               "rmse_median": float(rmse), "odom_final_median": float(odo),
                                               "applied_frac": app, "ms_update_median": float(np.median(tt) * 1e3),
                                               "frac_edges_gt5": st["frac_edges"], "wall_s": time.time() - t0}
                    grid = np.linspace(0, runs[0]["dist"][-1], 100)
                    curves[key] = (grid, np.median([np.interp(grid, r["dist"], r["err_pf"]) for r in runs], 0))
                    curves.setdefault(f"odom_{res_name}", (grid, np.median([np.interp(grid, r["dist"], r["err_odom"]) for r in runs], 0)))
                    log(f"| {surf} | {res_name} | {fname} | {filt} | {np.median(fin):.1f}/{np.percentile(fin, 90):.1f} | {rmse:.1f} | "
                        f"{odo:.0f} | {'-' if app is None else f'{app:.2f}'} | {np.median(tt) * 1e3:.1f} |")
    results["edge_fraction"] = {f"{s}_{r}": edge_stats(surfaces[s] if r == "1m" else block_mean(surfaces[s], BLOCK), 5.0)["frac_edges"]
                                for s in ("dsm", "dtm") for r in ("1m", "30m")}
    log(f"\nfraction of cells with |gradient| > 5 m/cell: {json.dumps({k: round(v, 3) for k, v in results['edge_fraction'].items()})}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "lidar_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(OUT, "lidar_output.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    plot(surfaces["dsm"], curves, os.path.join(OUT, "lidar.png"))


def plot(dsm, curves, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource

    from core import features
    from run_eval import shrink_png
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
    i0, j0, n = 1900, 1500, 400
    crop = dsm[i0:i0 + n, j0:j0 + n]
    ax[0].imshow(LightSource(315, 45).hillshade(crop, vert_exag=1), cmap="gray", origin="lower", extent=[0, n, 0, n])
    e = np.ma.masked_equal(features(crop, "binary", 5.0), 0)
    ax[0].imshow(e, cmap="autumn", origin="lower", extent=[0, n, 0, n], alpha=0.8)
    ax[0].set_title("1 m DSM, |grad| > 5 m (orange)", fontsize=9)
    ax[0].set_xlabel("m")
    d30 = block_mean(dsm, BLOCK)
    ax[1].imshow(LightSource(315, 45).hillshade(d30, vert_exag=3), cmap="gray", origin="lower", extent=[0, 4, 0, 4])
    e30 = np.ma.masked_equal(features(d30, "binary", 5.0), 0)
    ax[1].imshow(e30, cmap="autumn", origin="lower", extent=[0, 4, 0, 4], alpha=0.7)
    ax[1].set_title("same DSM binned to 30 m, |grad| > 5 m", fontsize=9)
    ax[1].set_xlabel("km")
    style = {"dsm_1m_binary5_v1": ("#d95f02", "-"), "dsm_1m_binary5_v2": ("#e7298a", "-"), "dsm_1m_grad_v2": ("#1b9e77", "-"),
             "dsm_30m_binary5_v1": ("#d95f02", ":"), "dsm_30m_grad_v2": ("#1b9e77", ":"),
             "dtm_1m_binary5_v2": ("#7570b3", "--"), "odom_1m": ("#888888", "-")}
    for k, (c, ls) in style.items():
        if k in curves:
            g, m = curves[k]
            ax[2].plot(g / 1000, m, color=c, ls=ls, lw=1.5, label=k.replace("_", " "))
    ax[2].set_yscale("log")
    ax[2].set_xlabel("distance flown [km]")
    ax[2].set_ylabel("median horizontal error [m]")
    ax[2].grid(alpha=0.3, which="both")
    ax[2].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)
    shrink_png(path)


if __name__ == "__main__":
    main()
