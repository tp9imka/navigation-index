"""Monte Carlo evaluation: odometry vs heightmap-gradient PF (paper / tuned) vs radar-altimeter TERCOM.

Writes out/results.json, out/error_vs_distance.png, out/tracks.png and prints the tables
quoted in README.md. Needs data/<region>.npz from fetch_dem.py.
"""
import argparse
import json
import os
import platform
import subprocess
import time

import numpy as np

import sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REGIONS = ["hilly", "mixed", "flat", "flat_smooth"]
CHECK_KM = [1, 2, 5, 10]
CONVERGED_M = 75.0

PAPER = dict(feature="binary", prep="none", grad_thr=5.0, weight_power=1.0, jitter_frac=0.05)
TUNED = dict(feature="grad", prep="none", weight_power=3.0, jitter_frac=0.1)
METHODS = {"odom": "err_odom", "pf_paper": "err_pf", "pf_grad": "err_pf", "tercom": "err_tercom"}

SWEEP = [
    ("obs_noise", [0.5, 2.0, 5.0, 10.0]),
    ("obs_scale_err", [0.0, 0.02, 0.05, 0.10]),
    ("compass_bias_sigma_deg", [0.0, 3.0, 10.0, 20.0]),
    ("obs_res_m", [30.0, 60.0, 120.0]),
    ("patch_cells", [21, 41, 61]),
    ("swath_m", [300.0, 600.0, 1200.0]),
]


def cpu_name():
    try:
        return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    except Exception:
        return platform.processor() or platform.machine()


def err_at(runs, key, d_m):
    return np.array([np.interp(d_m, r["dist"], r[key]) for r in runs])


def converge_dist(r, key):
    """Distance after which the error stays below CONVERGED_M for the rest of the flight."""
    e = r[key]
    bad = np.where(e >= CONVERGED_M)[0]
    if len(bad) == 0:
        return 0.0
    if bad[-1] == len(e) - 1:
        return None
    return float(r["dist"][bad[-1] + 1])


def run_set(region, seeds, base, extra=None):
    dem, res = sim.load_region(region)
    runs = {}
    for name, kw in (("pf_paper", PAPER), ("pf_grad", TUNED)):
        methods = ("pf", "tercom") if name == "pf_paper" else ("pf",)
        cfg = sim.with_(base, methods=methods, **kw, **(extra or {}))
        fmap = sim.map_features(dem, cfg)
        runs[name] = [sim.run(region, s, cfg, dem, res, fmap) for s in seeds]
    by_method = {"odom": runs["pf_paper"], "pf_paper": runs["pf_paper"],
                 "pf_grad": runs["pf_grad"], "tercom": runs["pf_paper"]}
    return by_method, dem, res


def summarize(by_method, cfg):
    s = {}
    for m, key in METHODS.items():
        rs = by_method[m]
        d = {f"{k}km": {"median": float(np.median(err_at(rs, key, k * 1000 - 1))),
                        "p90": float(np.percentile(err_at(rs, key, k * 1000 - 1), 90))} for k in CHECK_KM}
        rmse = [np.sqrt(np.mean(r[key] ** 2)) for r in rs]
        conv = [converge_dist(r, key) for r in rs]
        ok = [c for c in conv if c is not None]
        d["rmse_median"] = float(np.median(rmse))
        d["converged_frac"] = len(ok) / len(conv)
        d["converge_dist_median_m"] = float(np.median(ok)) if ok else None
        d["converge_time_median_s"] = float(np.median(ok)) / cfg.speed if ok else None
        s[m] = d
    tu = np.concatenate([r["t_update_s"] for r in by_method["pf_paper"]])
    tg = np.concatenate([r["t_update_s"] for r in by_method["pf_grad"]])
    tt = np.concatenate([r["t_tercom_s"] for r in by_method["tercom"]])
    s["timing_ms"] = {
        "pf_paper_update_median": float(np.median(tu) * 1e3), "pf_paper_update_p95": float(np.percentile(tu, 95) * 1e3),
        "pf_grad_update_median": float(np.median(tg) * 1e3), "pf_grad_update_p95": float(np.percentile(tg, 95) * 1e3),
        "tercom_fix_median": float(np.median(tt) * 1e3), "tercom_fix_p95": float(np.percentile(tt, 95) * 1e3),
    }
    acc = sum(r["tercom_accepted"] for r in by_method["tercom"])
    att = sum(r["tercom_attempts"] for r in by_method["tercom"])
    s["tercom_fix_accept_rate"] = acc / att if att else None
    return s


def print_table(title, summ):
    print(f"\n## {title}")
    print("| method | err@1km med/p90 | err@2km | err@5km | err@10km | RMSE med | conv. runs | conv. dist med |")
    print("|---|---|---|---|---|---|---|---|")
    for m in METHODS:
        d = summ[m]
        cells = [f"{d[f'{k}km']['median']:.0f}/{d[f'{k}km']['p90']:.0f}" for k in CHECK_KM]
        cd = "-" if d["converge_dist_median_m"] is None else f"{d['converge_dist_median_m']:.0f} m"
        print(f"| {m} | " + " | ".join(cells) + f" | {d['rmse_median']:.0f} | {d['converged_frac']*100:.0f}% | {cd} |")


def shrink_png(path, colors=64):
    from PIL import Image
    Image.open(path).convert("RGB").quantize(colors).save(path, optimize=True)


def plot_errors(all_runs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"odom": "#888888", "pf_paper": "#d95f02", "pf_grad": "#1b9e77", "tercom": "#7570b3"}
    labels = {"odom": "odometry", "pf_paper": "PF, paper binary edges", "pf_grad": "PF, gradient magnitude",
              "tercom": "TERCOM (radar alt.)"}
    fig, axes = plt.subplots(1, len(all_runs), figsize=(14, 3.6), sharey=True)
    grid = np.linspace(0, 9999, 200)
    for ax, (region, by_method) in zip(axes, all_runs.items()):
        for m, key in METHODS.items():
            e = np.array([np.interp(grid, r["dist"], r[key]) for r in by_method[m]])
            ax.plot(grid / 1000, np.median(e, 0), color=colors[m], label=labels[m], lw=1.6)
            ax.fill_between(grid / 1000, np.percentile(e, 25, 0), np.percentile(e, 75, 0), color=colors[m], alpha=0.15, lw=0)
        ax.set_title(region)
        ax.set_xlabel("distance flown [km]")
        ax.set_yscale("log")
        ax.set_ylim(5, 2000)
        ax.grid(alpha=0.3, which="both")
    axes[0].set_ylabel("horizontal error [m] (median, IQR)")
    axes[0].legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)
    shrink_png(path)


def plot_tracks(all_runs, dems, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    fig, axes = plt.subplots(1, len(all_runs), figsize=(14, 4))
    for ax, (region, by_method) in zip(axes, all_runs.items()):
        dem, res = dems[region]
        ext = [0, dem.shape[1] * res / 1000, 0, dem.shape[0] * res / 1000]
        ax.imshow(LightSource(315, 45).hillshade(dem[::2, ::2], vert_exag=3), cmap="gray", origin="lower", extent=ext)
        r = by_method["pf_grad"][0]
        rp = by_method["pf_paper"][0]
        for xy, c, lab, lw in ((r["truth"], "k", "truth (run 0)", 2.2), (r["odo"], "#888888", "odometry", 1.2),
                               (rp["nav_tercom"], "#7570b3", "TERCOM", 1.0), (rp["nav_pf"], "#d95f02", "PF paper", 1.0),
                               (r["nav_pf"], "#1b9e77", "PF grad", 1.2)):
            ax.plot(xy[:, 0] / 1000, xy[:, 1] / 1000, color=c, lw=lw, label=lab)
        ax.set_title(f"{region}: {dem.min():.0f}-{dem.max():.0f} m")
        ax.set_xlabel("km")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)
    shrink_png(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--sweep-seeds", type=int, default=12)
    ap.add_argument("--no-sweep", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    base = sim.Config()
    seeds = list(range(a.seeds))
    t0 = time.time()
    results = {"cpu": cpu_name(), "python": platform.python_version(), "numpy": np.__version__,
               "seeds": a.seeds, "config": {k: v for k, v in vars(base).items() if k != "methods"},
               "paper_variant": PAPER, "tuned_variant": TUNED, "regions": {}}
    all_runs, dems = {}, {}
    for region in REGIONS:
        by_method, dem, res = run_set(region, seeds, base)
        all_runs[region] = by_method
        dems[region] = (dem, res)
        summ = summarize(by_method, base)
        summ["terrain"] = sim.terrain_stats(dem, res)
        results["regions"][region] = summ
        print_table(f"{region} (init sigma {base.init_sigma_m:.0f} m, {a.seeds} runs)", summ)
        print("timing ms:", {k: round(v, 2) for k, v in summ["timing_ms"].items()},
              "tercom accept rate:", round(summ["tercom_fix_accept_rate"], 2))
        print("terrain:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in summ["terrain"].items()})

    print(f"\n# Convergence: initial guess offset 300 m, particles spread sigma 100+150 m, {a.seeds} runs")
    results["convergence"] = {}
    for region in REGIONS:
        by_method, _, _ = run_set(region, seeds, base, extra=dict(init_offset_m=300.0))
        summ = summarize(by_method, base)
        results["convergence"][region] = {m: {k: summ[m][k] for k in ("converged_frac", "converge_dist_median_m",
                                                                         "converge_time_median_s", "rmse_median")}
                                          for m in METHODS}
        print_table(f"{region}, 300 m initial offset", summ)

    if not a.no_sweep:
        results["sweep"] = {}
        sweep_seeds = list(range(200, 200 + a.sweep_seeds))
        dem, res = dems["mixed"]
        print(f"\n# Sensitivity sweep, region mixed, PF gradient-magnitude variant, {a.sweep_seeds} runs each")
        print("| parameter | value | RMSE med | err@10km med | err@10km p90 | odom err@10km med |")
        print("|---|---|---|---|---|---|")
        for p, vals in SWEEP:
            for v in vals:
                cfg = sim.with_(base, methods=("pf",), **TUNED, **{p: v})
                fmap = sim.map_features(dem, cfg)
                rs = [sim.run("mixed", s, cfg, dem, res, fmap) for s in sweep_seeds]
                rm = np.median([np.sqrt(np.mean(r["err_pf"] ** 2)) for r in rs])
                e10 = err_at(rs, "err_pf", 9999)
                o10 = err_at(rs, "err_odom", 9999)
                results["sweep"][f"{p}={v}"] = {"rmse_median": float(rm), "err10_median": float(np.median(e10)),
                                                 "err10_p90": float(np.percentile(e10, 90)),
                                                 "odom10_median": float(np.median(o10))}
                print(f"| {p} | {v} | {rm:.0f} | {np.median(e10):.0f} | {np.percentile(e10, 90):.0f} | {np.median(o10):.0f} |")

    plot_errors(all_runs, os.path.join(OUT, "error_vs_distance.png"))
    plot_tracks(all_runs, dems, os.path.join(OUT, "tracks.png"))
    results["wall_time_s"] = time.time() - t0
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(f"\nwall time {results['wall_time_s']:.0f} s on {results['cpu']}; wrote {OUT}/results.json and PNGs")


if __name__ == "__main__":
    main()
