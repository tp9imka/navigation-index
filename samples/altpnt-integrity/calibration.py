"""Measured error models for altpnt-integrity v2, extracted from committed results of
sibling samples. Stdlib only. Writes calibration.json next to this file.

    python3 calibration.py            # read ../<samples>, print and write calibration.json
    python3 calibration.py --check    # recompute and compare with the committed calibration.json

Every number in calibration.json carries the file it came from.
"""

import argparse
import cmath
import json
import math
import os
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.dirname(HERE)
OUT = os.path.join(HERE, "calibration.json")

RELNAV = "relative-nav-benchmark"
GEOLOC = "geoloc-license-clean"
TRN = "terrain-heightmap-pf"
GOLDEN = "golden-demo"

TUM_PAIRS = {
    "openvins-uzhfpv": ("results/vio/uzhfpv_indoor_forward_3_gt.tum", "results/vio/uzhfpv_indoor_forward_3_openvins.tum"),
    "kiss-icp-kitti04": ("results/lidar/kitti04_gt.tum", "results/lidar/kitti04_kiss_icp.tum"),
    "nadir-vo-vpair": ("results/aerial/vpair_gt.tum", "results/aerial/vpair_attitude_aided_yaw_bias_0deg.tum"),
}
RESAMPLE_S = 1.0
ANCHOR_FRACTION = 0.1      # same anchoring as relative-nav-benchmark/integrate/vo_to_altpnt.py
ANCHOR_MIN_M = 20.0
MOVING_MPS = 0.2
WINDOW_M = 50.0            # heading/scale fitted per 50 m of travelled distance
WRONG_FIX_M = 20.0         # geoloc-license-clean's "wrong fix" threshold
CONF = 0.95
TAIL_FROM = 0.5
VGEO_SPEED_FOR_GAPS = 30.0  # altpnt-integrity flight speed, converts spatial gaps to seconds


def rel(*p):
    return os.path.join(SAMPLES, *p)


def src(*p):
    return "samples/" + "/".join(p)


def load_json(*p):
    with open(rel(*p)) as fh:
        return json.load(fh)


def load_tum(path):
    t, xy = [], []
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            v = line.split()
            t.append(float(v[0]))
            xy.append(complex(float(v[1]), float(v[2])))
    return t, xy


def interp(t, z, tq):
    out, j = [], 0
    for q in tq:
        while j + 1 < len(t) - 1 and t[j + 1] < q:
            j += 1
        a = (q - t[j]) / (t[j + 1] - t[j]) if t[j + 1] > t[j] else 0.0
        out.append(z[j] + (z[j + 1] - z[j]) * min(max(a, 0.0), 1.0))
    return out


def linfit(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx if sxx else 0.0
    resid = [c - (my + b * (a - mx)) for a, c in zip(x, y)]
    return my - b * mx, b, math.sqrt(sum(r * r for r in resid) / max(n - 2, 1))


def heading_scale_track(gt_path, est_path):
    """Per-window heading and scale error of an odometry estimate vs ground truth.

    Anchored like vo_to_altpnt.py (2D rotation fitted on the first 10 % of the path, as if an
    absolute fix was there at the start); then per WINDOW_M of travel c = <dg, de> / |dg|^2,
    heading error = arg(c), scale error = |c| - 1."""
    tg, g = load_tum(gt_path)
    te, e = load_tum(est_path)
    t0, t1 = max(tg[0], te[0]), min(tg[-1], te[-1])
    grid = [t0 + k * RESAMPLE_S for k in range(int((t1 - t0) / RESAMPLE_S))]
    g, e = interp(tg, g, grid), interp(te, e, grid)
    g = [p - g[0] for p in g]
    e = [p - e[0] for p in e]
    run = [0.0]
    for a, b in zip(g, g[1:]):
        run.append(run[-1] + abs(b - a))
    k = next((i for i, r in enumerate(run) if r >= max(ANCHOR_MIN_M, ANCHOR_FRACTION * run[-1])), len(run) - 1)
    k = max(k, 2)
    rot = sum(ei.conjugate() * gi for ei, gi in zip(e[:k], g[:k]))
    rot /= abs(rot)
    e = [p * rot for p in e]
    dg = [(b - a) / RESAMPLE_S for a, b in zip(g, g[1:])]
    de = [(b - a) / RESAMPLE_S for a, b in zip(e, e[1:])]
    rows, acc_n, acc_d, dist, wstart = [], 0j, 0.0, 0.0, 0.0
    for i, (a, b) in enumerate(zip(dg, de)):
        if abs(a) <= MOVING_MPS:
            continue
        acc_n += a.conjugate() * b
        acc_d += abs(a) ** 2
        dist += abs(a) * RESAMPLE_S
        if dist - wstart >= WINDOW_M:
            c = acc_n / acc_d
            rows.append({"t_s": grid[i + 1] - t0, "dist_m": dist, "yaw_rad": cmath.phase(c), "scale": abs(c) - 1})
            acc_n, acc_d, wstart = 0j, 0.0, dist
    dur = grid[-1] - grid[0]
    speed = dist / dur
    yaw = [r["yaw_rad"] for r in rows]
    _, rate_per_m, resid = linfit([r["dist_m"] for r in rows], yaw)
    _, rate_per_s, _ = linfit([r["t_s"] for r in rows], yaw)
    sc = [r["scale"] for r in rows]
    return {
        "windows": len(rows), "window_m": WINDOW_M, "distance_m": round(dist, 1), "duration_s": round(dur, 1),
        "mean_speed_mps": round(speed, 3),
        "yaw_mean_deg": round(math.degrees(sum(yaw) / len(yaw)), 3),
        "yaw_abs_max_deg": round(math.degrees(max(abs(y) for y in yaw)), 3),
        "yaw_drift_deg_per_100m": round(math.degrees(rate_per_m) * 100, 3),
        "yaw_drift_deg_per_s": round(math.degrees(rate_per_s), 4),
        "yaw_window_resid_std_deg": round(math.degrees(resid), 3),
        "scale_mean_pct": round(100 * sum(sc) / len(sc), 3),
        "scale_std_pct": round(100 * math.sqrt(sum((s - sum(sc) / len(sc)) ** 2 for s in sc) / max(len(sc) - 1, 1)), 3),
        "track": [{k: round(v, 4) for k, v in r.items()} for r in rows],
    }


def wilson_upper(k, n, conf=CONF):
    z = NormalDist().inv_cdf(conf)
    p = k / n
    c = (p + z * z / (2 * n) + z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)
    return min(c, 1.0)


def zero_failure_upper(n, conf=CONF):
    """One-sided upper bound on a rate with 0 events in n trials (exact binomial, 'rule of three')."""
    return 1.0 - (1.0 - conf) ** (1.0 / n)


def gaussian_overbound(samples, conf=CONF):
    """Zero-mean Gaussian sigma whose two-sided tail lies above the empirical tail at every sample.

    Folded-CDF overbound (DeCleene 2000 for symmetric unimodal errors; here applied to the
    folded |e| so a bias is absorbed into sigma): sigma = max_i |e|_(i) / Q^-1(p_i / 2), where
    p_i is the CONF upper bound on P(|e| >= |e|_(i)). Only the tail (empirical exceedance <=
    TAIL_FROM) constrains: near zero a confidence bound on an exceedance close to 1 says nothing."""
    a = sorted(abs(x) for x in samples)
    n = len(a)
    best, at = 0.0, None
    for i, v in enumerate(a):
        if (n - i) / n > TAIL_FROM:
            continue
        p = wilson_upper(n - i, n, conf)
        s = v / NormalDist().inv_cdf(1 - p / 2)
        if s > best:
            best, at = s, v
    return best, at


def paired_overbound(samples, conf=CONF):
    """Rife-style bias + sigma pair: |mean| as the bias bound, then a zero-mean overbound of the
    centred residuals. Used in the filter as (b, sigma) with b added to the PL."""
    m = sum(samples) / len(samples)
    s, _ = gaussian_overbound([x - m for x in samples], conf)
    return abs(m), s


def quantile(xs, q):
    a = sorted(xs)
    return a[min(int(q * (len(a) - 1) + 0.5), len(a) - 1)]


def relnav_models():
    fits = load_json(RELNAV, "results", "altpnt_from_vo.json")
    out = {"source_fit": src(RELNAV, "results", "altpnt_from_vo.json"), "models": {}}
    for label, (gt, est) in TUM_PAIRS.items():
        f = fits[label]["fit"]
        track = heading_scale_track(rel(RELNAV, gt), rel(RELNAV, est))
        out["models"][label] = {
            "source_tum": [src(RELNAV, gt), src(RELNAV, est)],
            "fit_whole_run": {
                "scale_err": f["scale_err"], "yaw_err_rad": f["yaw_err_rad"],
                "yaw_err_deg": round(math.degrees(f["yaw_err_rad"]), 3),
                "white_frac_of_speed": f["white_mps"] / f["mean_speed_mps"],
                "mean_speed_mps": f["mean_speed_mps"], "end_error_pct": f["end_error_pct"]},
            "per_window": {k: v for k, v in track.items() if k != "track"},
            "track": track["track"],
        }
    vpair = load_json(RELNAV, "results", "aerial", "vpair_result.json")
    v = vpair["variants"]
    out["vpair_heading_sensitivity"] = {
        "source": src(RELNAV, "results", "aerial", "vpair_result.json"),
        "per_step_direction_std_deg": v["attitude_aided_yaw_bias_0deg"]["per_step"]["direction_err_deg_std"],
        "final_drift_pct": {k: v[k]["final_drift_pct_of_distance"] for k in
                            ("attitude_aided_yaw_bias_0deg", "attitude_aided_yaw_bias_2deg", "attitude_aided_yaw_bias_5deg")},
    }
    kitti = load_json(RELNAV, "results", "lidar", "kitti04_result.json")
    out["kiss_icp_kitti_segment"] = {"source": src(RELNAV, "results", "lidar", "kitti04_result.json"),
                                     **kitti["kitti_segment_errors"]}
    return out


def geoloc_models():
    table = load_json(GOLDEN, "data", "vgeo_table.json")
    nodes = table["nodes"]
    fixes = [n for n in nodes if n["de"] is not None]
    de, dn = [n["de"] for n in fixes], [n["dn"] for n in fixes]
    e2d = [math.hypot(a, b) for a, b in zip(de, dn)]
    # Spatial outages: along each east-west row of the 20 m grid, run lengths of no-fix nodes.
    rows = {}
    for n in nodes:
        rows.setdefault(n["n"], []).append(n)
    gaps, runs_ok = [], []
    for r in rows.values():
        r.sort(key=lambda x: x["e"])
        cur_gap = cur_ok = 0
        for x in r:
            if x["de"] is None:
                cur_gap += 1
                if cur_ok:
                    runs_ok.append(cur_ok)
                cur_ok = 0
            else:
                cur_ok += 1
                if cur_gap:
                    gaps.append(cur_gap)
                cur_gap = 0
        if cur_gap:
            gaps.append(cur_gap)
        if cur_ok:
            runs_ok.append(cur_ok)
    step = table["step_m"]
    ob_e, at_e = gaussian_overbound(de)
    ob_n, at_n = gaussian_overbound(dn)
    b_e, s_e = paired_overbound(de)
    b_n, s_n = paired_overbound(dn)

    res = load_json(GEOLOC, "out", "results.json")["results"]
    tight = load_json(GEOLOC, "out", "results_real_tight.json")["results"]
    real = {}
    for name, d in (("results.json", res), ("results_real_tight.json", tight)):
        for k, v in d.items():
            if "real" in k:
                real[f"{name}:{k}"] = {"n": v["summary"]["n"], "fixes": v["summary"]["fixes"],
                                       "errors_m": [r["err_m"] for r in v["rows"] if r["err_m"] is not None]}
    real_fix_errors = [e for v in real.values() for e in v["errors_m"]]
    real_n = sum(v["n"] for v in real.values())
    real_fixes = sum(v["fixes"] for v in real.values())
    accepted, wrong = 0, 0
    for name, d in (("results.json", res), ("results_real_tight.json", tight)):
        for k, v in d.items():
            if "/same" in k:
                continue  # frames cut from the matched map itself, no evidence about real outliers
            for r in v["rows"]:
                if r["err_m"] is not None:
                    accepted += 1
                    wrong += r["err_m"] > WRONG_FIX_M
    accepted += len(fixes)
    wrong += sum(e > WRONG_FIX_M for e in e2d)
    synth = {k: v["summary"] for k, v in res.items() if "/same" in k or "/season" in k}
    return {
        "golden_table": {
            "source": src(GOLDEN, "data", "vgeo_table.json"),
            "what": "ALIKED + LightGlue on frames rendered from NAIP 2019, matched against NAIP 2023, 150 m AGL, 20 m grid",
            "nodes": len(nodes), "fixes": len(fixes), "availability": round(len(fixes) / len(nodes), 4),
            "bias_e_m": round(sum(de) / len(de), 3), "bias_n_m": round(sum(dn) / len(dn), 3),
            "err2d_median_m": round(quantile(e2d, 0.5), 3), "err2d_p95_m": round(quantile(e2d, 0.95), 3),
            "err2d_max_m": round(max(e2d), 3),
            "outage_run_nodes_mean": round(sum(gaps) / len(gaps), 3), "outage_run_nodes_max": max(gaps),
            "fix_run_nodes_mean": round(sum(runs_ok) / len(runs_ok), 3),
            "outage_run_s_at_30mps_mean": round(sum(gaps) / len(gaps) * step / VGEO_SPEED_FOR_GAPS, 2),
            "fix_run_s_at_30mps_mean": round(sum(runs_ok) / len(runs_ok) * step / VGEO_SPEED_FOR_GAPS, 2),
            "residuals_e_n_m": [[a, b] for a, b in zip(de, dn)],
        },
        "overbound": {
            "method": "zero-mean folded-CDF Gaussian overbound per axis, 95 % Wilson upper bound on each tail fraction",
            "sigma_e_m": round(ob_e, 3), "binding_at_e_m": at_e, "sigma_n_m": round(ob_n, 3), "binding_at_n_m": at_n,
            "sigma_m": round(max(ob_e, ob_n), 3),
            "paired_bias_e_m": round(b_e, 3), "paired_sigma_e_m": round(s_e, 3),
            "paired_bias_n_m": round(b_n, 3), "paired_sigma_n_m": round(s_n, 3),
            "v1_assumed_sigma_m": 8.0, "v1_truth_sigma_m": 5.0,
        },
        "real_frames": {
            "source": [src(GEOLOC, "out", "results.json"), src(GEOLOC, "out", "results_real_tight.json")],
            "what": "eBee frames 2016 vs NAIP 2019/2023, EXIF GPS as truth, all extractors and prior configs",
            "attempts": real_n, "fixes": real_fixes, "fix_errors_m": real_fix_errors,
            "best_config": "aliked/real-vs-2019, prior +30 m, radius 60 m: 1/5",
        },
        "synthetic": {"source": src(GEOLOC, "out", "results.json"), "summaries": synth},
        "wrong_fix": {
            "threshold_m": WRONG_FIX_M,
            "accepted_fixes_counted": accepted, "wrong_fixes": wrong,
            "counted": "golden table + synthetic cross-season + real frames (same-map synthetic excluded)",
            "rate_upper_95": round(zero_failure_upper(accepted) if wrong == 0 else wilson_upper(wrong, accepted), 5),
        },
    }


def trn_models():
    d = load_json(TRN, "out", "v2_results.json")
    c = d["confidence"]
    n = c["n_updates"]
    regions = ("pooled", "hilly", "mixed", "flat", "flat_smooth")
    # Spread is sqrt(trace(P)) = sqrt(2) sigma for a circular 2D Gaussian. Radial error / sigma is
    # Rayleigh, so coverage F at k x spread gives an effective per-axis sigma for each k.
    infl = {}
    for reg in regions:
        best = 0.0
        for k in (1, 2):
            cov = c[f"coverage_{k}x_spread"][reg]
            if cov >= 1.0:
                continue
            x = math.sqrt(-2 * math.log(1 - cov))      # Rayleigh quantile in sigma units
            best = max(best, k / x)                    # sigma_eff / spread
        infl[reg] = round(best * math.sqrt(2), 4)      # sigma_eff / (spread / sqrt 2)
    # Spread distribution: log-normal through the two published shares.
    s50, s100 = c["err_when_spread_le_50"]["share_of_updates"], c["err_when_spread_le_100"]["share_of_updates"]
    z50, z100 = NormalDist().inv_cdf(s50), NormalDist().inv_cdf(s100)
    sig = (math.log(100) - math.log(50)) / (z100 - z50)
    mu = math.log(50) - z50 * sig
    return {
        "source": src(TRN, "out", "v2_results.json"),
        "n_updates": n,
        "spearman_spread_vs_error": c["spearman_spread"],
        "coverage_k_spread": {k: c[f"coverage_{k}x_spread"] for k in (1, 2, 3)},
        "sigma_per_axis_over_spread_div_sqrt2": infl,
        "sigma_rule": "per-axis sigma = inflation x spread / sqrt(2); inflation from the Rayleigh quantile of the "
                      "measured 1x and 2x coverage (max over k); 3x coverage is 100 % and gives no tail point",
        "spread_lognormal": {"mu_ln_m": round(mu, 4), "sigma_ln": round(sig, 4), "median_m": round(math.exp(mu), 2),
                             "fit": "through P(spread<=50 m)=%.3f and P(spread<=100 m)=%.3f" % (s50, s100)},
        "err_when_spread_le_50": c["err_when_spread_le_50"],
        "applied_frac": c["applied_frac"],
        "fault_rate_upper_95": round(zero_failure_upper(n), 6),
        "fault_definition": "true error > 3 x spread: 0 of %d updates" % n,
    }


def golden_detection():
    d = load_json(GOLDEN, "data", "mc_summary.json")
    rows = []
    for r in d["table"]:
        rows.append({"spoof": r["spoof"], "rate_mps": r["rate_mps"], "mode": r["mode"], "runs": r["runs"],
                     "ttd_ss_median_s": r["ttd_ss_s"].get("median"), "false_alarm_ss": r["false_alarm_ss"],
                     "false_alarm_chi2": r["false_alarm_chi2"], "ss_misleading_epochs": r.get("ss_misleading_epochs"),
                     "vgeo_fix_rate": r.get("vgeo_fix_rate")})
    return {"source": src(GOLDEN, "data", "mc_summary.json"), "rows": rows}


def build():
    return {
        "note": "Measured error models for altpnt-integrity v2. Regenerate with python3 calibration.py.",
        "relative": relnav_models(),
        "geoloc": geoloc_models(),
        "trn": trn_models(),
        "golden_detection": golden_detection(),
    }


def summary(cal):
    lines = []
    for k, m in cal["relative"]["models"].items():
        f, w = m["fit_whole_run"], m["per_window"]
        lines.append(f"{k:18} whole-run yaw {f['yaw_err_deg']:+.2f} deg scale {100 * f['scale_err']:+.2f} % "
                     f"white {100 * f['white_frac_of_speed']:.2f} % of speed | per >= {w['window_m']:.0f} m window: yaw mean "
                     f"{w['yaw_mean_deg']:+.2f} max |{w['yaw_abs_max_deg']:.2f}| drift {w['yaw_drift_deg_per_100m']:+.2f} deg/100 m "
                     f"({w['yaw_drift_deg_per_s']:+.4f} deg/s), scale {w['scale_mean_pct']:+.2f} +- {w['scale_std_pct']:.2f} %")
    g = cal["geoloc"]
    t, o, wf = g["golden_table"], g["overbound"], g["wrong_fix"]
    lines.append(f"vgeo golden table: {t['fixes']}/{t['nodes']} fixes ({100 * t['availability']:.0f} %), bias "
                 f"({t['bias_e_m']:+.2f}, {t['bias_n_m']:+.2f}) m, 2D median {t['err2d_median_m']} p95 {t['err2d_p95_m']} "
                 f"max {t['err2d_max_m']} m; outage runs mean {t['outage_run_s_at_30mps_mean']} s at 30 m/s")
    lines.append(f"vgeo overbound: zero-mean sigma {o['sigma_m']} m (e {o['sigma_e_m']}, n {o['sigma_n_m']}); paired "
                 f"bias/sigma e {o['paired_bias_e_m']}/{o['paired_sigma_e_m']} n {o['paired_bias_n_m']}/{o['paired_sigma_n_m']}")
    rf = g["real_frames"]
    lines.append(f"vgeo real eBee frames: {rf['fixes']}/{rf['attempts']} attempts fixed, errors {rf['fix_errors_m']} m")
    lines.append(f"vgeo wrong fixes (> {wf['threshold_m']:.0f} m): {wf['wrong_fixes']} of {wf['accepted_fixes_counted']} => "
                 f"rate <= {wf['rate_upper_95']} (95 %)")
    tr = cal["trn"]
    lines.append(f"TRN: sigma inflation over spread/sqrt2 {tr['sigma_per_axis_over_spread_div_sqrt2']}; spread log-normal "
                 f"median {tr['spread_lognormal']['median_m']} m; fault (err > 3 spread) rate <= {tr['fault_rate_upper_95']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="compare with the committed calibration.json")
    a = ap.parse_args(argv)
    cal = build()
    print(summary(cal))
    if a.check:
        with open(OUT) as fh:
            same = json.load(fh) == json.loads(json.dumps(cal))
        print("calibration.json matches recomputation:", same)
        return 0 if same else 1
    with open(OUT, "w") as fh:
        json.dump(cal, fh, indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
