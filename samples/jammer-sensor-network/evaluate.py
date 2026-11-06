"""Monte Carlo: localization error vs number of static nodes, node density and shadowing
sigma, for weighted centroid, RSS least squares, grid likelihood, DF triangulation
(../interference-geolocation-to-tak/triangulate.py) and grid + DF fusion.

Each trial: random jittered-grid layout of N static nodes over a square of side L, one
static wideband jammer uniform in the inner 60% of the square, EIRP uniform 0..20 dBm,
fresh shadowing field. Each node averages OBS_PER_NODE 1 Hz observations (one fuse window).

    python3 evaluate.py                 # full sweep (~minutes), writes out/eval.json
    python3 evaluate.py --trials 5      # quick
"""
import argparse
import json
import math
import os
import random

import siblings  # noqa: F401
import jsn_aggregator as A
import jsn_localize as L
import jsn_model as M
import jsn_protocol as P
import jsn_scenarios as S
import triangulate  # noqa: E402
from geo import LocalFrame  # noqa: E402
from kraken import Bearing  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OBS_PER_NODE = 10
DF_BEARINGS_PER_STATION = 30
GRID_N = 41
INNER_FRAC = 0.6
EIRP_RANGE_DBM = (0.0, 20.0)
BASE = {"n": 16, "side_m": 4000.0, "sigma_db": 6.0}
SWEEPS = {
    "n": [4, 8, 16, 32],
    "side_m": [2000.0, 4000.0, 8000.0],
    "sigma_db": [2.0, 4.0, 6.0, 8.0, 10.0],
}
METHODS = ["wc", "ls", "grid", "df", "grid+df"]


FRAME = LocalFrame(*S.ORIGIN)


def trial(cfg, rng, ple_true=M.PLE_DEFAULT):
    half = cfg["side_m"] / 2
    env = M.Environment(sigma_db=cfg["sigma_db"], ple=ple_true, rng=rng)
    jx, jy = (rng.uniform(-INNER_FRAC * half, INNER_FRAC * half) for _ in range(2))
    eirp = rng.uniform(*EIRP_RANGE_DBM)
    meas = []
    for i, p in enumerate(S.node_layout(cfg["n"], half, rng)):
        node = M.SimNode(f"s{i}", M.static_path(p), True, rng)
        meta = {"static": True, **node.meta()}
        ms = []
        for t in range(OBS_PER_NODE):
            j = env.received_dbm(p, (jx, jy), eirp)
            f, _ = node.observe(float(t), j)
            ms.append(P.to_measurement({"id": node.id, "t": float(t), **f}, meta, f["xy"]))
        meas.append(A._window_mean(ms))
    area = (-half, -half, half, half)
    res = {"detected": sum(m.kind != "upper" for m in meas)}
    wc = L.weighted_centroid(meas)
    if wc:
        res["wc"] = (wc, None)
    ls = L.rss_ls(meas, area, sigma_sh=cfg["sigma_db"])
    if ls:
        x, y, _ = ls["sources"][0]
        res["ls"] = ((x, y), [[ls["cov"][0][0], ls["cov"][0][1]], [ls["cov"][1][0], ls["cov"][1][1]]])
    g = L.GridFilter(area, n=GRID_N, sigma_sh=cfg["sigma_db"])
    g.set_static(meas)
    if res["detected"]:
        e = g.estimate(use_df=False)
        res["grid"] = ((e["x"], e["y"]), e["cov"])
    stations = {k: (x * half / S.HALF_M, y * half / S.HALF_M) for k, (x, y) in S.DF_STATIONS.items()}
    bearings, df_obs = [], []
    for sid, (sx, sy) in stations.items():
        if env.received_dbm((sx, sy), (jx, jy), eirp) <= S.DF_MIN_DBM:
            continue
        true_b = math.degrees(math.atan2(jx - sx, jy - sy))
        lat, lon, _ = FRAME.to_geodetic(sx, sy)
        bs = []
        for t in range(DF_BEARINGS_PER_STATION):
            b = true_b + (rng.uniform(25, 160) * rng.choice((-1, 1)) if rng.random() < S.DF_OUTLIER_P
                          else rng.gauss(0, S.DF_SIGMA_DEG))
            bs.append(b % 360.0)
            bearings.append(Bearing(t=float(t), station_id=sid, lat=lat, lon=lon, bearing_deg=b % 360.0))
        mean, n = A._circ_robust_mean(bs)
        df_obs.append((sx, sy, mean, max(S.DF_SIGMA_DEG / math.sqrt(n), L.DF_SIGMA_FLOOR_DEG)))
    res["df_stations"] = len(df_obs)
    if len(df_obs) >= 2:
        try:
            f = triangulate.locate(bearings, S.DF_SIGMA_DEG)
            x, y, _ = FRAME.to_enu(f["lat"], f["lon"])
            res["df"] = ((x, y), f["cov"])
        except (ValueError, ZeroDivisionError):
            pass
    if df_obs:
        g.set_bearings(df_obs)
        e = g.estimate(use_df=True)
        res["grid+df"] = ((e["x"], e["y"]), e["cov"])
    return (jx, jy), res


def run_config(cfg, trials, seed):
    rng = random.Random(seed)
    stats = {m: {"err": [], "inside": [], "fail": 0} for m in METHODS}
    undetected = 0
    for _ in range(trials):
        truth, res = trial(cfg, rng)
        if not res["detected"]:
            undetected += 1
        for m in METHODS:
            if m not in res:
                stats[m]["fail"] += 1
                continue
            (x, y), cov = res[m]
            stats[m]["err"].append(math.hypot(x - truth[0], y - truth[1]))
            if cov is not None:
                stats[m]["inside"].append(L.inside_ellipse(truth[0] - x, truth[1] - y, cov))
    out = {"cfg": cfg, "trials": trials, "undetected": undetected, "methods": {}}
    for m, s in stats.items():
        e = sorted(s["err"])
        out["methods"][m] = {
            "median_m": round(e[len(e) // 2]) if e else None,
            "p90_m": round(e[int(0.9 * (len(e) - 1))]) if e else None,
            "cover95": round(sum(s["inside"]) / len(s["inside"]), 2) if s["inside"] else None,
            "no_estimate": s["fail"]}
    return out


def table(rows, key):
    head = f"| {key} | density /km2 | " + " | ".join(METHODS) + " | 95% cover ls / grid / grid+df |"
    lines = [head, "|" + "---|" * (len(METHODS) + 3)]
    for r in rows:
        c = r["cfg"]
        dens = c["n"] / (c["side_m"] / 1000) ** 2
        cells = []
        for m in METHODS:
            v = r["methods"][m]
            cells.append("-" if v["median_m"] is None else f"{v['median_m']} / {v['p90_m']}"
                         + (f" ({v['no_estimate']} none)" if v["no_estimate"] else ""))
        cov = " / ".join("-" if r["methods"][m]["cover95"] is None else f"{r['methods'][m]['cover95']:.2f}"
                         for m in ("ls", "grid", "grid+df"))
        lines.append(f"| {c[key]:g} | {dens:.2f} | " + " | ".join(cells) + f" | {cov} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default=os.path.join(HERE, "out", "eval.json"))
    a = ap.parse_args()
    results = {}
    cache = {}
    for key, vals in SWEEPS.items():
        rows = []
        for v in vals:
            cfg = dict(BASE, **{key: v})
            ck = tuple(sorted(cfg.items()))
            if ck not in cache:
                cache[ck] = run_config(cfg, a.trials, a.seed)
            rows.append(cache[ck])
        results[key] = rows
        print(f"\nsweep {key} (others: {', '.join(f'{k}={v:g}' for k, v in BASE.items() if k != key)}), "
              f"{a.trials} trials, median / p90 error in m:\n")
        print(table(rows, key))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
