"""v2 evaluation on the v1 GLO-30 regions: information gate, compass-bias state, confidence output.

Same flights as v1 (same seeds, same RNG order). Re-runs v1 `pf_grad` and checks it against
out/results.json. Writes out/v2_results.json, out/v2_output.txt, out/v2_errors.png,
out/v2_bias.png, out/v2_confidence.png.
"""
import argparse
import json
import os
import time

import numpy as np
from scipy.stats import spearmanr

import nav2
import sim
from run_eval import CHECK_KM, OUT, REGIONS, TUNED, err_at, shrink_png

V2_VARIANTS = {"v2": {}, "v2_nogate": dict(gate=False), "v2_nohead": dict(heading=False)}
BIASES = [0.0, 5.0, 10.0, 15.0, 20.0]
BIAS_REGIONS = ["hilly", "mixed"]
CONF_KEYS = ("spread", "ess", "crb", "signif")
lines = []


def log(s=""):
    print(s, flush=True)
    lines.append(s)


def summ(runs, key):
    d = {f"{k}km": {"median": float(np.median(err_at(runs, key, k * 1000 - 1))),
                    "p90": float(np.percentile(err_at(runs, key, k * 1000 - 1), 90))} for k in CHECK_KM}
    d["rmse_median"] = float(np.median([np.sqrt(np.mean(r[key] ** 2)) for r in runs]))
    return d


def row(name, d, extra=""):
    cells = " | ".join(f"{d[f'{k}km']['median']:.0f}/{d[f'{k}km']['p90']:.0f}" for k in CHECK_KM)
    return f"| {name} | {cells} | {d['rmse_median']:.0f} |{extra}"


def main_table(seeds, base):
    res_all, runs_all = {}, {}
    v1_ref = json.load(open(os.path.join(OUT, "results.json")))["regions"]
    log("## Main: 20 runs per region, seeds 0-19 (same flights as v1)\n")
    log("| region / navigator | @1 km | @2 km | @5 km | @10 km | RMSE med | updates applied | runs worse than odometry (final / RMSE) | ms/update med |")
    log("|---|---|---|---|---|---|---|---|---|")
    for region in REGIONS:
        dem, res = sim.load_region(region)
        cfg = sim.with_(base, methods=("pf",), **TUNED)
        fmap = sim.map_features(dem, cfg)
        runs = {"pf_grad_v1": [sim.run(region, s, cfg, dem, res, fmap) for s in seeds]}
        for name, kw in V2_VARIANTS.items():
            runs[name] = [nav2.run_v2(dem, res, s, cfg, nav2.V2(**kw), fmap) for s in seeds]
        out = {"odom": summ(runs["pf_grad_v1"], "err_odom")}
        log(row(f"{region} odometry", out["odom"], " - | - | - |"))
        for name, rs in runs.items():
            out[name] = summ(rs, "err_pf")
            worse_f = np.mean([r["err_pf"][-1] > r["err_odom"][-1] for r in rs])
            worse_r = np.mean([np.sqrt(np.mean(r["err_pf"] ** 2)) > np.sqrt(np.mean(r["err_odom"] ** 2)) for r in rs])
            out[name]["worse_than_odom_final"] = float(worse_f)
            out[name]["worse_than_odom_rmse"] = float(worse_r)
            if name == "pf_grad_v1":
                tt = np.concatenate([r["t_update_s"] for r in rs])
                ref = v1_ref[region]["pf_grad"]
                same = all(abs(out[name][f"{k}km"][q] - ref[f"{k}km"][q]) < 1e-6 for k in CHECK_KM for q in ("median", "p90"))
                out[name]["matches_v1_results_json"] = bool(same)
                app = "-"
            else:
                tt = np.concatenate([r["rec_t"] for r in rs])
                app = f"{np.mean([r['rec_applied'].mean() for r in rs]):.2f}"
                out[name]["applied_frac"] = float(np.mean([r["rec_applied"].mean() for r in rs]))
                out[name]["final_bias_err_deg_median_abs"] = float(np.median(
                    [abs(np.rad2deg(r["rec_bias_est"][-1] - r["rec_bias_true"][-1])) for r in rs]))
            out[name]["ms_update_median"] = float(np.median(tt) * 1e3)
            out[name]["ms_update_p95"] = float(np.percentile(tt, 95) * 1e3)
            log(row(f"{region} {name}", out[name], f" {app} | {worse_f*100:.0f}% / {worse_r*100:.0f}% | {np.median(tt)*1e3:.1f} |"))
        log(f"v1 pf_grad reproduces out/results.json exactly: {out['pf_grad_v1']['matches_v1_results_json']}")
        res_all[region] = out
        runs_all[region] = runs
    return res_all, runs_all


def bias_test(seeds, base):
    log("\n## Compass bias test: fixed bias, no random part, 12 runs each (seeds 200-211)\n")
    log("| region | bias | odometry @10 km med | v1 pf_grad @10 km med/p90 | v2 no heading state | v2 @10 km med/p90 | v2 final bias error, median abs |")
    log("|---|---|---|---|---|---|---|")
    out = {}
    for region in BIAS_REGIONS:
        dem, res = sim.load_region(region)
        for b in BIASES:
            cfg = sim.with_(base, methods=("pf",), **TUNED, compass_bias_sigma_deg=0.0, compass_bias_fixed_deg=b)
            fmap = sim.map_features(dem, cfg)
            v1 = [sim.run(region, s, cfg, dem, res, fmap) for s in seeds]
            v2 = [nav2.run_v2(dem, res, s, cfg, nav2.V2(), fmap) for s in seeds]
            nh = [nav2.run_v2(dem, res, s, cfg, nav2.V2(heading=False), fmap) for s in seeds]
            e = {n: err_at(rs, "err_pf", 9999) for n, rs in (("v1", v1), ("v2", v2), ("v2_nohead", nh))}
            odo = err_at(v1, "err_odom", 9999)
            berr = np.median([abs(np.rad2deg(r["rec_bias_est"][-1] - r["rec_bias_true"][-1])) for r in v2])
            out[f"{region}_{b:.0f}"] = {"odom10_median": float(np.median(odo)), "bias_err_deg_median": float(berr),
                                        **{f"{n}_10_median": float(np.median(x)) for n, x in e.items()},
                                        **{f"{n}_10_p90": float(np.percentile(x, 90)) for n, x in e.items()}}
            log(f"| {region} | {b:.0f} deg | {np.median(odo):.0f} | {np.median(e['v1']):.0f}/{np.percentile(e['v1'], 90):.0f} | "
                f"{np.median(e['v2_nohead']):.0f}/{np.percentile(e['v2_nohead'], 90):.0f} | "
                f"{np.median(e['v2']):.0f}/{np.percentile(e['v2'], 90):.0f} | {berr:.1f} deg |")
    return out


def confidence(runs_all):
    """Per-update confidence signals (no truth) against the true error at that instant."""
    rows = []
    for region, runs in runs_all.items():
        for r in runs["v2"]:
            k = r["rec_k"]
            for i in range(len(k)):
                rows.append((REGIONS.index(region), r["err_pf"][k[i]], *[r[f"rec_{c}"][i] for c in CONF_KEYS],
                             r["rec_applied"][i]))
    a = np.array(rows, float)
    reg, err = a[:, 0], a[:, 1]
    sig = {c: a[:, 2 + i] for i, c in enumerate(CONF_KEYS)}
    applied = a[:, 2 + len(CONF_KEYS)] > 0
    out = {"n_updates": int(len(a))}
    log(f"\n## Confidence vs true error, v2 main runs, {len(a)} updates pooled over 4 regions x 20 runs\n")
    log("| signal (no truth needed) | Spearman rho vs true error, pooled | hilly | mixed | flat | flat_smooth |")
    log("|---|---|---|---|---|---|")
    for c in CONF_KEYS:
        x = np.where(np.isfinite(sig[c]), sig[c], 1e9)
        per = [spearmanr(x[reg == i], err[reg == i])[0] for i in range(len(REGIONS))]
        pooled = spearmanr(x, err)[0]
        out[f"spearman_{c}"] = {"pooled": float(pooled), **{REGIONS[i]: float(p) for i, p in enumerate(per)}}
        log(f"| {c} | {pooled:+.2f} | " + " | ".join(f"{p:+.2f}" for p in per) + " |")
    sp = sig["spread"]
    log("\nSpread as a 1-sigma radius: share of updates with true error below k x spread")
    log("| k | pooled | hilly | mixed | flat | flat_smooth |")
    log("|---|---|---|---|---|---|")
    for k in (1, 2, 3):
        cov = [np.mean(err[reg == i] <= k * sp[reg == i]) for i in range(len(REGIONS))]
        out[f"coverage_{k}x_spread"] = {"pooled": float(np.mean(err <= k * sp)), **{REGIONS[i]: float(c) for i, c in enumerate(cov)}}
        log(f"| {k} | {np.mean(err <= k * sp)*100:.0f}% | " + " | ".join(f"{c*100:.0f}%" for c in cov) + " |")
    for thr in (50.0, 100.0):
        sel = sp <= thr
        out[f"err_when_spread_le_{thr:.0f}"] = {"share_of_updates": float(sel.mean()),
                                               "err_median": float(np.median(err[sel])), "err_p95": float(np.percentile(err[sel], 95)),
                                               "err_median_else": float(np.median(err[~sel]))}
        log(f"spread <= {thr:.0f} m on {sel.mean()*100:.0f}% of updates: true error median {np.median(err[sel]):.0f} m, "
            f"p95 {np.percentile(err[sel], 95):.0f} m (other updates: median {np.median(err[~sel]):.0f} m)")
    out["applied_frac"] = float(applied.mean())
    return out, (reg, err, sp, applied)


def plot_errors(runs_all, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    st = {"odom": ("#888888", "odometry"), "pf_grad_v1": ("#d95f02", "v1 PF gradient"),
          "v2_nogate": ("#7570b3", "v2 without gate"), "v2": ("#1b9e77", "v2 (gate + heading state)")}
    fig, axes = plt.subplots(1, len(runs_all), figsize=(14, 3.6), sharey=True)
    grid = np.linspace(0, 9999, 200)
    for ax, (region, runs) in zip(axes, runs_all.items()):
        for name, (c, lab) in st.items():
            rs, key = (runs["pf_grad_v1"], "err_odom") if name == "odom" else (runs[name], "err_pf")
            e = np.array([np.interp(grid, r["dist"], r[key]) for r in rs])
            ax.plot(grid / 1000, np.median(e, 0), color=c, label=lab, lw=1.6)
            ax.fill_between(grid / 1000, np.percentile(e, 25, 0), np.percentile(e, 75, 0), color=c, alpha=0.12, lw=0)
        ax.set_title(region)
        ax.set_yscale("log")
        ax.set_ylim(5, 2000)
        ax.set_xlabel("distance flown [km]")
        ax.grid(alpha=0.3, which="both")
    axes[0].set_ylabel("horizontal error [m] (median, IQR)")
    axes[0].legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)
    shrink_png(path)


def plot_bias(bias, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(BIAS_REGIONS), figsize=(9, 3.4), sharey=True)
    for ax, region in zip(axes, BIAS_REGIONS):
        for key, c, lab in (("odom10", "#888888", "odometry"), ("v1_10", "#d95f02", "v1 PF gradient"),
                            ("v2_nohead_10", "#7570b3", "v2 without heading state"), ("v2_10", "#1b9e77", "v2")):
            ax.plot(BIASES, [bias[f"{region}_{b:.0f}"][f"{key}_median"] for b in BIASES], "o-", color=c, label=lab, lw=1.5, ms=4)
        ax.set_yscale("log")
        ax.set_title(region)
        ax.set_xlabel("compass bias [deg]")
        ax.grid(alpha=0.3, which="both")
    axes[0].set_ylabel("error at 10 km, median [m]")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)
    shrink_png(path)


def plot_conf(data, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    reg, err, sp, _ = data
    fig, ax = plt.subplots(figsize=(5.2, 4))
    cols = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a"]
    rng = np.random.default_rng(0)
    for i, name in enumerate(REGIONS):
        sel = np.where(reg == i)[0]
        sel = rng.choice(sel, min(len(sel), 800), replace=False)
        ax.scatter(sp[sel], err[sel], s=3, alpha=0.4, color=cols[i], label=name)
    x = np.array([3, 5000])
    ax.plot(x, x, "k-", lw=0.8, label="error = spread")
    ax.plot(x, 3 * x, "k--", lw=0.8, label="error = 3 x spread")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(3, 5000)
    ax.set_ylim(0.5, 5000)
    ax.set_xlabel("particle spread [m] (no truth)")
    ax.set_ylabel("true horizontal error [m]")
    ax.legend(fontsize=7, markerscale=3)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)
    shrink_png(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--bias-seeds", type=int, default=12)
    a = ap.parse_args()
    t0 = time.time()
    base = sim.Config()
    results = {"v2_defaults": vars(nav2.V2()), "tuned_variant": TUNED}
    results["main"], runs_all = main_table(list(range(a.seeds)), base)
    results["confidence"], conf_data = confidence(runs_all)
    results["bias"] = bias_test(list(range(200, 200 + a.bias_seeds)), base)
    plot_errors(runs_all, os.path.join(OUT, "v2_errors.png"))
    plot_bias(results["bias"], os.path.join(OUT, "v2_bias.png"))
    plot_conf(conf_data, os.path.join(OUT, "v2_confidence.png"))
    results["wall_time_s"] = time.time() - t0
    log(f"\nwall time {results['wall_time_s']:.0f} s")
    with open(os.path.join(OUT, "v2_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(OUT, "v2_output.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
