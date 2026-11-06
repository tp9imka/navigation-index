"""Run the swarm-coop-localization filters on real MILUV UWB ranges.

python3 fetch_miluv.py                       once: ~65 MB of CSVs out of an 11 GB zip
python3 run_real.py stats                    real range error vs the sim's UWB model
python3 run_real.py nominal                  DR / centralized / naive / CI, plain vs robust
python3 run_real.py fault                    biased anchor ranges on one drone: detection time
python3 run_real.py fault --kind peer        biased inter-drone ranges of the denied drone
python3 run_real.py all                      all of the above (saved copies in out/)
"""
import argparse
import math
import statistics
import sys

import adapter
import miluv_io as io
import range_stats as rs
import coop_loc  # noqa: E402  (sim sample, on sys.path via adapter)
from filters import nis2

EXPS = ("default_3_zigzag_0", "default_3_random_0")
FAULT_START = 120.0   # s after the first epoch
FAULT_RATE = 0.02     # m/s range bias growth


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


def run_methods(methods, cfg, epochs):
    out = {}
    for m in methods:
        err, nees = [], []
        for ep in epochs:
            m.step(ep)
            re, rn = [], []
            for a in range(cfg.n_agents):
                x, P = m.est(a)
                e = (x[0] - ep.truth[a][0], x[1] - ep.truth[a][1])
                re.append(math.hypot(*e))
                rn.append(min(nis2(e, P), 1e6))
            err.append(re)
            nees.append(rn)
        out[m.name] = {"err": err, "nees": nees, "rejected": getattr(m, "rejected", 0),
                       "detections": list(getattr(m, "detections", []))}
    return out


def cmd_stats(args):
    print("UWB two-way-ranging error = measured range - truth (m). Real: MILUV, truth = devkit gt_range "
          "(mocap tag/anchor positions with lever arms, re-derived here to < 1 cm on 99.9 % of rows).")
    print("Sim: samples/swarm-coop-localization sim.generate, default Config, seed 1 (all range draws).")
    print(rs.HDR)
    for exp in args.exps + ["cirObstacles_3_random_0"]:
        if not io.have_data(exp, args.data):
            print(f"{exp}: no data (python3 fetch_miluv.py --exp {exp})")
            continue
        errs = rs.real_errors(exp, args.data)
        for kind in ("anchor", "inter"):
            for phase in ("air", "ground"):
                for cal in ("cal", "raw"):
                    v = errs.get((kind, phase, cal))
                    if v and (cal == "cal" or phase == "air"):
                        short = exp.replace("default_3_", "").replace("cirObstacles_3_random_0", "obstacles")
                        print(rs.row(f"{short} {kind} {phase} {cal}", rs.describe(v)))
    print(rs.row("sim model (all draws)", rs.describe(rs.sim_errors())))
    print("cal = devkit-calibrated range (antenna delay + power bias), raw = before calibration; "
          "air = all involved drones above 0.3 m (mocap z). rob sd = 1.4826 x MAD.")
    ok = [e for e in args.exps if io.have_data(e, args.data)]
    if ok:
        _, _, _, info = adapter.build(ok[0], 2, data_dir=args.data)
        print(f"\nWhat the 2-D filters see in {ok[0]} (denied ifo003, median per pair per epoch, horizontal "
              f"projection with height sensors, no lever arms): inter-drone {rs.row('', rs.describe(info['inter_err']))[34:]}")
        fe = sorted(info["fix_err"])
        print(f"anchor multilateration fixes: n={len(fe)} median {rs.quantile(fe, .5):.3f} m, p95 "
              f"{rs.quantile(fe, .95):.3f} m, max {fe[-1]:.3f} m (filter assumes sigma "
              f"{math.sqrt(adapter.INDOOR['R_GNSS']):.2f} m per axis)")


def cmd_nominal(args):
    names = None
    for exp in args.exps:
        if not io.have_data(exp, args.data):
            print(f"{exp}: no data")
            continue
        for src in ("real", "synthetic"):
            rows = {}
            for denied in range(3):
                for seed in range(1, args.seeds + 1):
                    cfg, init, eps, info = adapter.build(exp, denied, seed=seed, range_source=src, data_dir=args.data)
                    res = run_methods(coop_loc.nominal_methods(init, cfg), cfg, eps)
                    names = list(res)
                    for name, r in res.items():
                        T = len(eps)
                        d = rows.setdefault(name, {"denied": [], "anch": [], "nees": [], "final": [], "rej": 0})
                        d["denied"].append(rms([r["err"][k][denied] for k in range(T)]))
                        d["anch"].append(rms([r["err"][k][a] for k in range(T) for a in range(3) if a != denied]))
                        d["final"].append(r["err"][-1][denied])
                        d["nees"].append(statistics.fmean(r["nees"][k][a] for k in range(T) for a in range(3)))
                        d["rej"] += r["rejected"]
            print(f"\n{exp}, {src} inter-drone ranges, {len(eps)} epochs x {adapter.DT} s; 3 choices of denied "
                  f"drone x {args.seeds} odometry seeds = {3 * args.seeds} runs: mean [min, max] over runs")
            print(f"{'method':18s}{'denied-drone RMSE':>24s}{'anchored RMSE':>22s}{'denied final':>14s}{'NEES':>9s}{'rej/run':>9s}")
            for name in names:
                d = rows[name]
                print(f"{name:18s}{statistics.fmean(d['denied']):8.3f} [{min(d['denied']):5.3f},{max(d['denied']):6.3f}]"
                      f"{statistics.fmean(d['anch']):8.3f} [{min(d['anch']):5.3f},{max(d['anch']):5.3f}]"
                      f"{statistics.fmean(d['final']):14.3f}{statistics.fmean(d['nees']):9.1f}{d['rej'] / len(d['denied']):9.0f}")
    print("\nOdometry is synthetic (mocap displacement + sim odometer model); ranges are real unless 'synthetic', "
          "which replaces each real inter-drone range by the sim's UWB model applied to the same true distance.")


def cmd_fault(args):
    exp = args.exps[0]
    if not io.have_data(exp, args.data):
        print(f"{exp}: no data")
        return
    for faulted in (True, False):
        rows = {}
        for denied in range(3):
            anchored = [a for a in range(3) if a != denied]
            target = denied if args.kind == "peer" else anchored[0]
            for seed in range(1, args.seeds + 1):
                fault = adapter.Fault(args.kind, target, FAULT_START, args.rate) if faulted else None
                cfg, init, eps, info = adapter.build(exp, denied, seed=seed, fault=fault, data_dir=args.data)
                res = run_methods(coop_loc.spoof_methods(init, cfg), cfg, eps)
                kk = [k for k, ep in enumerate(eps) if ep.t >= FAULT_START]
                for name, r in res.items():
                    d = rows.setdefault(name, {"tgt": [], "oth": [], "lat": [], "false": 0, "det": 0, "wrong": 0,
                                               "runs": 0})
                    d["runs"] += 1
                    others = [a for a in range(3) if a != target]
                    d["tgt"].append(rms([r["err"][k][target] for k in kk]))
                    d["oth"].append(rms([r["err"][k][a] for k in kk for a in others]))
                    pre = [t for t, _ in r["detections"] if t < FAULT_START]
                    post = [(t, a) for t, a in r["detections"] if t >= FAULT_START]
                    d["false"] += len(pre)
                    if post:
                        d["det"] += 1
                        d["lat"].append(post[0][0] - FAULT_START)
                        d["wrong"] += post[0][1] != target
        what = (f"{args.kind} fault: +{args.rate} m/s ramp from t={FAULT_START:.0f} s on "
                + ("the first anchored drone's ranges to anchors 0-2" if args.kind == "anchor"
                   else "every inter-drone range of the denied drone"))
        print(f"\n{exp}, {what}" if faulted else f"\n{exp}, NO fault (false-alarm control)")
        print(f"{'method':22s}{'target RMSE':>20s}{'others RMSE':>20s}{'det':>6s}{'wrong':>6s}{'false':>6s}"
              f"  {'latency s':>16s}  (RMSE from t={FAULT_START:.0f} s, {rows[next(iter(rows))]['runs']} runs)")
        for name, d in rows.items():
            lat = d["lat"]
            ltxt = f"{statistics.median(lat):5.1f} [{min(lat):4.1f},{max(lat):5.1f}]" if lat else "-"
            print(f"{name:22s}{statistics.fmean(d['tgt']):7.3f} [{min(d['tgt']):4.2f},{max(d['tgt']):5.2f}]"
                  f"{statistics.fmean(d['oth']):7.3f} [{min(d['oth']):4.2f},{max(d['oth']):5.2f}]"
                  f"{d['det']:6d}{d['wrong']:6d}{d['false']:6d}  {ltxt:>16s}")
    print(f"\ndet = runs with a detection at or after onset; wrong = first such detection names a non-faulty drone; "
          f"false = detections before onset (all runs). latency = median [min, max] s; bias at detection = "
          f"latency x {args.rate} m/s. 'gate' rejects fixes without logging a detection.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["stats", "nominal", "fault", "all"])
    ap.add_argument("--exps", nargs="+", default=list(EXPS))
    ap.add_argument("--seeds", type=int, default=10, help="odometry noise seeds per configuration")
    ap.add_argument("--kind", choices=["anchor", "peer"], default="anchor")
    ap.add_argument("--rate", type=float, default=FAULT_RATE)
    ap.add_argument("--data", default=io.DATA_DIR)
    args = ap.parse_args()
    if not any(io.have_data(e, args.data) for e in args.exps):
        print("no MILUV data found; run: python3 fetch_miluv.py", file=sys.stderr)
        return 1
    adapter.apply_indoor()
    if args.cmd in ("stats", "all"):
        cmd_stats(args)
    if args.cmd in ("nominal", "all"):
        cmd_nominal(args)
    if args.cmd in ("fault", "all"):
        cmd_fault(args)
        if args.cmd == "all":
            args.kind = "peer"
            cmd_fault(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
