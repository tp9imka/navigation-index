"""Run every navigator on the same synthetic blind flights over real GLO-30 terrain.

python run_bench.py                       # full grid, writes out/results.json + out/leaderboard.md
python run_bench.py --runs 2 --regions ural --families straight   # quick look
"""
import argparse
import json
import os
import platform
import time

import numpy as np

import metrics
import navs
import regions
import sim

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def run_one(dem, res, region, family, seed, nav_names, scenario_kw=None):
    sc = sim.Scenario(family=family, **(scenario_kw or {}))
    d = sim.generate(dem, res, sc, seed)
    rows = []
    for name in nav_names:
        ctor = navs.NAVIGATORS[name]
        nav = ctor(dem, res, d["prior"])
        est = np.zeros((len(d["t"]), 2))
        step_ms = np.zeros(len(d["t"]))
        t_start = time.perf_counter()
        for k, (t, h) in enumerate(zip(d["t"], d["terrain_meas"])):
            t0 = time.perf_counter()
            est[k] = nav.update(float(t), float(h))
            step_ms[k] = (time.perf_counter() - t0) * 1e3
        total_s = time.perf_counter() - t_start
        errs = metrics.error_at_distances(d["s"], d["e"], d["n"], est[:, 0], est[:, 1])
        rows.append({
            "region": region, "family": family, "seed": seed, "nav": name,
            "err_5km": errs[0], "err_10km": errs[1], "err_20km": errs[2],
            "cpu_s": total_s, "flight_s": float(d["t"][-1] - d["t"][0]),
            "step_ms_p99": float(np.percentile(step_ms, 99)), "step_ms_max": float(step_ms.max()),
            "stats": nav.stats, "alt_bias_m": d["alt_bias_m"],
            "kept_frac": d["n_kept"] / d["n_epochs"],
        })
    return rows, d


def leaderboard(rows, nav_names):
    lines = []
    keys = sorted({(r["region"], r["family"]) for r in rows}, key=lambda x: (x[1], x[0]))
    for fam in ("straight", "turns"):
        sub = [r for r in rows if r["family"] == fam]
        if not sub:
            continue
        lines.append(f"\n### {fam} flights, all regions pooled\n")
        lines.append("| navigator | 5 km med/p95 | 10 km med/p95 | 20 km med/p95 | diverged | CPU s per 1000 s flown | worst step ms |")
        lines.append("|---|---|---|---|---|---|---|")
        for nav in nav_names:
            rr = [r for r in sub if r["nav"] == nav]
            cells = []
            for c in ("err_5km", "err_10km", "err_20km"):
                s = metrics.summarize([r[c] for r in rr])
                cells.append(f"{s['median']:.0f} / {s['p95']:.0f}")
            div = metrics.divergence_rate([r["err_20km"] for r in rr])
            cpu = 1000 * np.sum([r["cpu_s"] for r in rr]) / np.sum([r["flight_s"] for r in rr])
            worst = max(r["step_ms_max"] for r in rr)
            lines.append(f"| {nav} | " + " | ".join(cells) + f" | {div:.0%} | {cpu:.1f} | {worst:.0f} |")
    lines.append("\n### Per region, 20 km error median / p95 (m) and divergence rate\n")
    lines.append("| region | family | " + " | ".join(nav_names) + " |")
    lines.append("|---|---|" + "---|" * len(nav_names))
    for reg, fam in keys:
        cells = []
        for nav in nav_names:
            rr = [r for r in rows if r["region"] == reg and r["family"] == fam and r["nav"] == nav]
            s = metrics.summarize([r["err_20km"] for r in rr])
            div = metrics.divergence_rate([r["err_20km"] for r in rr])
            cells.append(f"{s['median']:.0f} / {s['p95']:.0f} ({div:.0%})")
        lines.append(f"| {reg} | {fam} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def ablation_cases():
    """One impairment at a time on top of an ideal sensor, then everything, then 1 Hz."""
    R0 = dict(footprint=False, noise_m=0.0, noise_frac=0.0, dropout_p=0.0, burst_p=0.0, outlier_p=0.0)
    ideal = dict(radar=sim.RadarModel(**R0),
                 altref=sim.AltRefModel(bias_sigma_m=0.0, drift_sigma_mps=0.0, wander_sigma_m=0.0),
                 world=sim.WorldModel(dem_err_sigma_m=0.0, forest_frac=1e-6))
    cases = {"ideal": ideal}
    cases["+footprint 40 deg"] = {**ideal, "radar": sim.RadarModel(**{**R0, "footprint": True})}
    cases["+range noise"] = {**ideal, "radar": sim.RadarModel(**{**R0, "noise_m": 0.5, "noise_frac": 0.005})}
    cases["+dropouts, outliers"] = {**ideal, "radar": sim.RadarModel(
        **{**R0, "dropout_p": 0.02, "burst_p": 0.002, "outlier_p": 0.005})}
    cases["+baro reference error"] = {**ideal, "altref": sim.AltRefModel()}
    cases["+map error, canopy"] = {**ideal, "world": sim.WorldModel()}
    cases["all (default)"] = {}
    cases["all, 1 Hz"] = {"sample_hz": 1.0}
    cases["all, 2% range noise"] = {"radar": sim.RadarModel(noise_frac=0.02)}
    return cases


def run_ablation(a):
    rows = []
    for reg in a.regions:
        dem, res = regions.ensure(reg)
        for case, kw in ablation_cases().items():
            for i in range(a.runs):
                r, _ = run_one(dem, res, reg, "straight", a.seed0 + i, a.navs, kw)
                for x in r:
                    x["case"] = case
                rows.extend(r)
            print(f"{reg} {case} done", flush=True)
    lines = ["| case | " + " | ".join(a.navs) + " |", "|---|" + "---|" * len(a.navs)]
    for case in ablation_cases():
        cells = []
        for nav in a.navs:
            rr = [x for x in rows if x["case"] == case and x["nav"] == nav]
            s = metrics.summarize([x["err_20km"] for x in rr])
            cells.append(f"{s['median']:.0f} ({metrics.divergence_rate([x['err_20km'] for x in rr]):.0%})")
        lines.append(f"| {case} | " + " | ".join(cells) + " |")
    with open(os.path.join(OUT, f"{a.tag}.json"), "w") as f:
        json.dump({"rows": rows, "args": vars(a)}, f, indent=1, default=float)
    with open(os.path.join(OUT, f"{a.tag}.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--regions", nargs="*", default=list(regions.REGIONS))
    ap.add_argument("--families", nargs="*", default=["straight", "turns"])
    ap.add_argument("--navs", nargs="*", default=list(navs.NAVIGATORS))
    ap.add_argument("--tag", default="results")
    ap.add_argument("--ablation", action="store_true", help="straight flights, one impairment at a time")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.ablation:
        return run_ablation(a)
    rows = []
    t0 = time.time()
    for reg in a.regions:
        dem, res = regions.ensure(reg)
        for fam in a.families:
            for i in range(a.runs):
                seed = a.seed0 + i + 1000 * a.families.index(fam)
                r, _ = run_one(dem, res, reg, fam, seed, a.navs)
                rows.extend(r)
                msg = " ".join(f"{x['nav']}={x['err_20km']:.0f}" for x in r)
                print(f"{reg:8s} {fam:8s} seed {seed:5d}: {msg}", flush=True)
    meta = {"python": platform.python_version(), "numpy": np.__version__, "machine": platform.platform(),
            "processor": platform.processor(), "wall_s": time.time() - t0, "args": vars(a)}
    with open(os.path.join(OUT, f"{a.tag}.json"), "w") as f:
        json.dump({"meta": meta, "rows": rows}, f, indent=1, default=float)
    lb = leaderboard(rows, a.navs)
    with open(os.path.join(OUT, f"{a.tag}_leaderboard.md"), "w") as f:
        f.write(lb + "\n")
    print(lb)
    print(f"\nwall {meta['wall_s']:.0f} s")


if __name__ == "__main__":
    main()
