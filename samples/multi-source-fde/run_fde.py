"""Multi-source FDE on the real VPAIR flight: GNSS (simulated), visual fixes (real), LiDAR TRN and GLO-30 TRN
(simulated from real terrain at real poses), dead reckoning from real nadir VO.

Data, error models and TRN simulation are ../two-source-integrity-vpair's (imported). Filters are altpnt v2's
EKF (via ../e2e-visual-nav-vpair run_fusion.EkfNoImu). One filter per subset of the absolute sources runs
from GNSS loss; fde.py makes the detection / exclusion decisions on that bank.

    python run_fde.py --data <dir with vpair_sample/>      # writes results/fde_result.json
"""
import argparse
import copy
import itertools
import json
import math
import statistics
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "two-source-integrity-vpair"))
import fde  # noqa: E402
import run_two_source as ts  # noqa: E402  (puts e2e-visual-nav-vpair and altpnt-integrity on the path)

nc, rf, v1, v2 = ts.nc, ts.rf, ts.v1, ts.v2

SOURCES4 = ("gnss", "vgeo", "trn", "trn2")      # GNSS, visual fixes, LiDAR-heightmap TRN, GLO-30 TRN
SOURCES3 = ("gnss", "vgeo", "trn")
SOURCES_ALT = ("vgeo", "trn", "trn2")           # GNSS denied: the alt-PNT sources only
SEEDS = 10
EXAMPLE_CONFIGS = ("4src_detect", "4src_fde1", "4src_fde2", "alt3_fde1", "alt3_altpnt_maxsep")   # seed 0 per frame
ALS = (25.0, 50.0, 100.0)
GNSS_SEED_OFFSET = 1000
# GNSS drag-off: the spoofer pulls the reported position away at a constant rate from onset to the end
SPOOF = {"onset": 60, "rate_mps": 2.0, "dir_deg": 120.0}
# Visual wrong-place lock: the matcher locks onto a similar-looking place 60 m away for 30 frames
WRONG_PLACE = {"frames": (100, 130), "offset_m": 60.0, "dir_deg": 200.0}
SCENARIOS = {
    "nominal": {},
    "gnss_spoof": {"gnss": SPOOF["onset"]},
    "visual_misreg": {"vgeo": "misreg"},
    "visual_wrong_place": {"vgeo": "wrong_place"},
    "trn_ambiguity": {"trn": "ambig"},
    "double_spoof_trn": {"gnss": SPOOF["onset"], "trn": "ambig"},
    "double_spoof_visual": {"gnss": ts.MISREG["persistent"]["frames"][0], "vgeo": "misreg"},
}
CONFIGS = {   # name: (sources, max_faults, mode)
    "3src_detect": (SOURCES3, 1, "detect"), "3src_fde1": (SOURCES3, 1, "fde"), "3src_fde2": (SOURCES3, 2, "fde"),
    "4src_detect": (SOURCES4, 1, "detect"), "4src_fde1": (SOURCES4, 1, "fde"), "4src_fde2": (SOURCES4, 2, "fde"),
    "alt3_detect": (SOURCES_ALT, 1, "detect"), "alt3_fde1": (SOURCES_ALT, 1, "fde"),
    "alt3_fde2": (SOURCES_ALT, 2, "fde"),
}
# altpnt v2 Monitor2: exclude the branch with the largest normalised separation. Its third slot is 'gnss':
# the simulated GNSS (prior 1e-2) or, GNSS denied, the GLO-30 TRN (TRN prior) as in two-source's three-source run
BASELINES = {"3src_altpnt_maxsep": ("gnss", {"vgeo": "vgeo", "magnav": "trn", "gnss": "gnss"}),
             "alt3_altpnt_maxsep": ("trn2", {"vgeo": "vgeo", "magnav": "trn", "gnss": "trn2"})}


class BankEkf(rf.EkfNoImu):
    """altpnt v2 EKF on VO; absolute sources carry their own R in ep['abs'][src] = ((E, N), r)."""

    def _meas(self, src, ep):
        if src == "vio":
            return super()._meas(src, ep)
        z, r = ep["abs"][src]
        return z, [self.x[0], self.x[1]], v1.H_POS, r


def subsets(sources):
    return [frozenset(c) for n in range(len(sources) + 1) for c in itertools.combinations(sources, n)]


def initial(ctx):
    en, start, cfg = ctx["en"], ctx["start"], ctx["cfg"]
    x0 = [en[start][0], en[start][1], *(en[start] - en[start - 1]) / nc.FRAME_DT, 0, 0, 0, 0]
    P0 = v2.mat.zeros(8, 8)
    for i, s in enumerate([3, 3, 1.0, 1.0, 0.05, 0.05, cfg.s_sigma, cfg.psi_sigma]):
        P0[i][i] = s * s
    return x0, P0


def run_bank(ctx, meas):
    """meas: {src: {frame: (E, N, r)}}. One gated filter per subset of SOURCES4, all from GNSS loss."""
    en, start, steps, cfg = ctx["en"], ctx["start"], ctx["steps"], ctx["cfg"]
    x0, P0 = initial(ctx)
    filters = {s: BankEkf(x0, P0, cfg) for s in subsets(SOURCES4)}
    bank, gated = [], {s: 0 for s in SOURCES4}
    for k in range(start + 1, len(en)):
        ab = {s: ((m[k][0], m[k][1]), m[k][2]) for s, m in meas.items() if k in m}
        ep = {"t": float(k), "imu": rf.IMU_ZERO, "vio": (tuple(steps[k - 1] / nc.FRAME_DT), cfg.vio_r), "abs": ab}
        out = {}
        for sub, f in filters.items():
            f.predict(ep["imu"])
            f.fuse("vio", ep, True)
            for s in SOURCES4:
                if s in sub and s in ab:
                    _, ok = f.fuse(s, ep, True)
                    if not ok and len(sub) == len(SOURCES4):
                        gated[s] += 1
            out[sub] = (f.x[0], f.x[1], f.pos_cov())
        bank.append((k, out))
    return bank, gated


def gnss_fixes(ctx, seed, onset=None):
    en, start = ctx["en"], ctx["start"]
    rng = np.random.default_rng(GNSS_SEED_OFFSET + seed)
    u = np.array([math.sin(math.radians(SPOOF["dir_deg"])), math.cos(math.radians(SPOOF["dir_deg"]))])
    out = {}
    for k in range(start + 1, len(en)):
        p = en[k] + rng.normal(0.0, v1.GNSS_WHITE, 2)
        if onset is not None and k >= onset:
            p = p + SPOOF["rate_mps"] * (k - onset + 1) * nc.FRAME_DT * u
        out[k] = (float(p[0]), float(p[1]), v1.GNSS_R)
    return out


def wrong_place_fixes(vis):
    a, b = WRONG_PLACE["frames"]
    u = WRONG_PLACE["offset_m"] * np.array([math.sin(math.radians(WRONG_PLACE["dir_deg"])),
                                            math.cos(math.radians(WRONG_PLACE["dir_deg"]))])
    return {k: (np.asarray(p) + u if a <= k < b else np.asarray(p)) for k, p in vis.items()}


def scenario_inputs(ctx, name, seed, cache):
    spec, n = SCENARIOS[name], len(ctx["en"])
    vis = ctx["vis"][ts.PRIMARY[1]]
    windows = {}
    g_on = spec.get("gnss")
    if g_on is not None:
        windows["gnss"] = (g_on, n)
    if spec.get("vgeo") == "misreg":
        vis = ts.misreg_fixes(vis, ts.MISREG["persistent"])
        windows["vgeo"] = tuple(ts.MISREG["persistent"]["frames"])
    elif spec.get("vgeo") == "wrong_place":
        vis = wrong_place_fixes(vis)
        windows["vgeo"] = WRONG_PLACE["frames"]
    trnfx = cache[("lidar5", seed, spec.get("trn") == "ambig")]
    if spec.get("trn") == "ambig":
        windows["trn"] = ts.AMBIG_FRAMES
    vgeo_r = ctx["cfg"].vgeo_r
    meas = {"gnss": gnss_fixes(ctx, seed, g_on), "vgeo": {k: (float(p[0]), float(p[1]), vgeo_r) for k, p in vis.items()},
            "trn": trnfx, "trn2": cache[("glo30", seed, False)]}
    return meas, vis, windows


def windows_for(windows, config):
    """A GNSS fault does not exist for a configuration that does not use GNSS."""
    return {s: w for s, w in windows.items() if s != "gnss" or not config.startswith("alt3")}


def run_altpnt(ctx, vis, meas, third):
    """altpnt v2 Monitor2 on visual + LiDAR TRN + `third` in its 'gnss' slot, via two-source's run_filter."""
    c = dict(ctx)
    c["cfg3"] = copy.copy(ctx["cfg3"])
    c["cfg3"].priors = dict(ctx["cfg"].priors, gnss=v2.GNSS_FAULT_PRIOR if third == "gnss" else ctx["cfg"].priors["magnav"])
    rows = ts.run_filter(c, vis, meas["trn"], "full", ("vgeo", "magnav", "gnss"), third=meas[third])
    names = BASELINES["3src_altpnt_maxsep" if third == "gnss" else "alt3_altpnt_maxsep"][1]
    out = []
    for r in rows:
        ev = []
        for e in r["events"]:
            if e.startswith(("alert:", "exclude:")):
                ev.append("detect")
            if e.startswith(("exclude:", "blame:")):
                ev.append("exclude:" + names[e.split(":", 1)[1]])
        out.append({"k": r["k"], "hpe": r["hpe"], "hpl": r["hpl"], "alert": r["alert"], "events": ev,
                    "admitted": r["excluded"]})
    return out


def aggregate(evals, faulted):
    n = len(evals)
    lat = [e["latency"] for e in evals if e["latency"] is not None]
    outc = {}
    for e in evals:
        outc[e["outcome"]] = outc.get(e["outcome"], 0) + 1
    out = {"runs": n, "outcomes": outc,
           "correct_exclusion_runs": outc.get("correct_exclusion", 0),
           "wrong_exclusion_runs": outc.get("wrong_exclusion", 0),
           "missed_runs": outc.get("missed", 0),
           "detected_runs": sum(e["detected_at"] is not None for e in evals) if faulted else None,
           "latency_frames": {"median": statistics.median(lat), "min": min(lat), "max": max(lat)} if lat else None,
           "false_detection_epochs_before_onset": sum(e["false_detections_before_onset"] for e in evals),
           "wrong_excluded": sorted({s for e in evals for s in e["wrong_excluded"]}),
           "hpe_max_m": max(e["hpe_max"] for e in evals),
           "hpl_median_m": round(statistics.median(e["hpl_median"] for e in evals), 1), "per_al": {}}
    for al in evals[0]["per_al"]:
        p = [e["per_al"][al] for e in evals]
        out["per_al"][al] = {"avail_pct": round(statistics.mean(x["avail_pct"] for x in p), 1),
                             "avail_post_onset_pct": (round(statistics.mean(x["avail_post_onset_pct"] for x in p), 1)
                                                      if faulted else None),
                             "HMI": sum(x["HMI"] for x in p), "MI": sum(x["MI"] for x in p)}
    return out


def compact(rows):
    return [[r["k"], round(r["hpe"], 1), round(r["hpl"], 1), int(r["alert"]), r.get("admitted", ""), " ".join(r["events"])]
            for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="directory containing vpair_sample/")
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--scenarios", default=",".join(SCENARIOS))
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args()
    wall0 = time.perf_counter()
    ctx = ts.load(a.data)
    en, start = ctx["en"], ctx["start"]
    truth = {k: (float(en[k][0]), float(en[k][1])) for k in range(len(en))}
    priors = {"gnss": v2.GNSS_FAULT_PRIOR, "vgeo": ctx["cfg"].priors["vgeo"], "trn": ctx["cfg"].priors["magnav"],
              "trn2": ctx["cfg"].priors["magnav"]}
    vgeo_bias = ctx["cfg"].vgeo_bias
    amb = set(range(*ts.AMBIG_FRAMES))
    cache, trn_diag = {}, {}
    for seed in range(a.seeds):
        cache[("lidar5", seed, False)], d0 = ts.trn_fixes(ctx, "lidar5", seed)
        cache[("lidar5", seed, True)], d1 = ts.trn_fixes(ctx, "lidar5", seed, amb)
        cache[("glo30", seed, False)], d2 = ts.trn_fixes(ctx, "glo30", seed)
        trn_diag[seed] = {"lidar5": d0, "lidar5_ambig_offsets_m": d1.get("fault_offset_m", []), "glo30": d2}
    res = {"dataset": "VPAIR sample (Zenodo 6473989), 199 nadir frames, frame = 1 s",
           "frames_scored": len(en) - start - 1, "sources": {
               "gnss": f"simulated: VPAIR pose + N(0, {v1.GNSS_WHITE} m) per axis, R {v1.GNSS_R} m, 1 Hz",
               "vgeo": f"real imagery fixes, map stride {ts.PRIMARY[1]}, R {round(ctx['cfg'].vgeo_r, 2)} m",
               "trn": "lidar5 heightmap PF over real NRW DSM at real poses (simulated sensor), R = own sigma",
               "trn2": "GLO-30 heightmap PF (simulated sensor, real GLO-30 map), R = own sigma",
               "dead_reckoning": "real nadir VO, heading +2 deg, drives every filter; not a monitored source"},
           "priors": priors, "vgeo_bias_m": round(vgeo_bias, 2), "spoof": SPOOF, "wrong_place": WRONG_PLACE,
           "misreg": ts.MISREG["persistent"], "ambiguity_frames": ts.AMBIG_FRAMES, "seeds": a.seeds,
           "constants": {"P_FA": v1.P_FA, "IR_FF": v1.IR_FF, "IR_FAULT": v2.IR_FAULT, "hold_epochs": fde.HOLD_EPOCHS,
                         "probation_epochs": fde.PROBATION_EPOCHS},
           "unmonitored_dual_prior_sum": {
               "3src": round(sum(fde.prior(e, priors) for e in fde.hypotheses(SOURCES3, 2) if len(e) == 2), 7),
               "4src": round(sum(fde.prior(e, priors) for e in fde.hypotheses(SOURCES4, 2) if len(e) == 2), 7)},
           "trn_fault_offsets_m": {s: trn_diag[s]["lidar5_ambig_offsets_m"] for s in trn_diag},
           "results": {}, "examples_columns": ["k", "hpe_m", "hpl_m", "alert", "admitted", "events"], "examples": {}, "bank_gate_rejects_all_in_view": {}}
    for name in a.scenarios.split(","):
        per = {c: [] for c in (*CONFIGS, *BASELINES)}
        t0 = time.perf_counter()
        for seed in range(a.seeds):
            meas, vis, windows = scenario_inputs(ctx, name, seed, cache)
            bank, gated = run_bank(ctx, meas)
            res["bank_gate_rejects_all_in_view"].setdefault(name, []).append(gated)
            for cname, (srcs, mf, mode) in CONFIGS.items():
                rows = fde.run(bank, truth, srcs, priors, mf, mode, vgeo_bias)
                per[cname].append(fde.evaluate(rows, windows_for(windows, cname), ALS))
                if seed == 0 and cname in EXAMPLE_CONFIGS:
                    res["examples"].setdefault(name, {})[cname] = compact(rows)
            for bname, (third, _) in BASELINES.items():
                rows = run_altpnt(ctx, vis, meas, third)
                per[bname].append(fde.evaluate(rows, windows_for(windows, bname), ALS))
                if seed == 0 and bname in EXAMPLE_CONFIGS:
                    res["examples"][name][bname] = compact(rows)
        res["results"][name] = {c: aggregate(v, bool(windows_for(windows, c))) | {"per_seed": v} for c, v in per.items()}
        print(f"{name} ({time.perf_counter() - t0:.0f} s):", flush=True)
        for c, agg in res["results"][name].items():
            p = agg["per_al"]["50"]
            print(f"  {c:20} outcomes {agg['outcomes']}  lat {agg['latency_frames']}  avail50 {p['avail_pct']}% "
                  f"post {p['avail_post_onset_pct']}%  HMI50 {p['HMI']}  HMI25 {agg['per_al']['25']['HMI']}  "
                  f"PLmed {agg['hpl_median_m']}  HPEmax {agg['hpe_max_m']}", flush=True)
    res["wall_s"] = round(time.perf_counter() - wall0, 1)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "fde_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(f"wrote {out.name}/fde_result.json, {res['wall_s']} s")


if __name__ == "__main__":
    main()
