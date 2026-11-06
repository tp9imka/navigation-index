"""Cooperative localization for a GNSS-denied team: run and compare estimators.

python3 coop_loc.py                      nominal comparison, seed 1
python3 coop_loc.py --bearing            add camera relative bearings
python3 coop_loc.py --scenario spoof     agent 0 GNSS spoofed from t=300 s
python3 coop_loc.py --seeds 10           Monte Carlo summary
"""
import argparse
import csv
import math
import os
import statistics
import time

from filters import Centralized, DeadReckoning, Decentralized, nis2
from sim import Config, generate

TS_STEP = 60  # s between rows of the per-agent time-series tables


def nominal_methods(init, cfg):
    return [
        DeadReckoning(init, cfg),
        Centralized(init, cfg, robust=False),
        Centralized(init, cfg, robust=True),
        Decentralized(init, cfg, mode="naive", robust=True),
        Decentralized(init, cfg, mode="ci", robust=False),
        Decentralized(init, cfg, mode="ci", robust=True),
    ]


def spoof_methods(init, cfg):
    out = [DeadReckoning(init, cfg)]
    for integ in ("none", "gate", "ss"):
        out.append(Centralized(init, cfg, robust=True, integrity=integ))
    for integ in ("none", "gate", "vote", "ss"):
        out.append(Decentralized(init, cfg, mode="ci", robust=True, integrity=integ))
    return out


def run(cfg, scenario):
    if scenario == "spoof" and cfg.spoof_agent < 0:
        cfg.spoof_agent = cfg.gnss_agents[0]
    init, epochs = generate(cfg)
    methods = (spoof_methods if scenario == "spoof" else nominal_methods)(init, cfg)
    res = {}
    for m in methods:
        t0 = time.perf_counter()
        err, nees, est = [], [], []
        for ep in epochs:
            m.step(ep)
            row_e, row_n, row_x = [], [], []
            for a in range(cfg.n_agents):
                x, P = m.est(a)
                e = (x[0] - ep.truth[a][0], x[1] - ep.truth[a][1])
                row_e.append(math.hypot(*e))
                row_n.append(nis2(e, P))
                row_x.append((x[0], x[1], math.sqrt(P[0][0]), math.sqrt(P[1][1])))
            err.append(row_e)
            nees.append(row_n)
            est.append(row_x)
        res[m.name] = {"err": err, "nees": nees, "est": est, "bytes": m.bytes,
                       "rejected": getattr(m, "rejected", 0), "detections": getattr(m, "detections", []),
                       "cpu_s": time.perf_counter() - t0}
    return init, epochs, res


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


def summarize(cfg, epochs, r):
    n, T = cfg.n_agents, len(epochs)
    denied = [a for a in range(n) if a not in cfg.gnss_agents]
    allv = [r["err"][k][a] for k in range(T) for a in range(n)]
    den = [r["err"][k][a] for k in range(T) for a in denied]
    per_agent = [rms([r["err"][k][a] for k in range(T)]) for a in range(n)]
    nees = statistics.mean(min(r["nees"][k][a], 1e6) for k in range(T) for a in range(n))
    return {"rmse": rms(allv), "rmse_denied": rms(den), "per_agent": per_agent,
            "final_mean": statistics.mean(r["err"][-1]), "max": max(allv), "nees": nees,
            "bps_agent": r["bytes"] / T / n}


def fmt(v, w=7, p=1):
    return f"{v:{w}.{p}f}"


def print_nominal(cfg, epochs, res):
    n = cfg.n_agents
    print(f"\nPosition error per method (seed {cfg.seed}, {n} agents, GNSS on {list(cfg.gnss_agents)}, "
          f"{cfg.duration} s, bearing={'on' if cfg.bearing else 'off'})")
    print("NEES: mean of e^T P^-1 e over agents/epochs; 2.0 = consistent 2-D estimate.")
    hdr = f"{'method':22s}{'RMSE':>7s}{'denied':>8s}{'final':>7s}{'max':>8s}{'NEES':>9s}{'B/s/ag':>8s}{'rej':>6s}"
    print(hdr)
    for name, r in res.items():
        s = summarize(cfg, epochs, r)
        print(f"{name:22s}{fmt(s['rmse'])}{fmt(s['rmse_denied'], 8)}{fmt(s['final_mean'])}{fmt(s['max'], 8)}"
              f"{fmt(s['nees'], 9)}{fmt(s['bps_agent'], 8)}{r['rejected']:6d}")
    print("\nPer-agent RMSE (m)")
    print(f"{'method':22s}" + "".join(f"{'a' + str(a) + ('*' if a in cfg.gnss_agents else ''):>8s}" for a in range(n)))
    for name, r in res.items():
        s = summarize(cfg, epochs, r)
        print(f"{name:22s}" + "".join(fmt(v, 8) for v in s["per_agent"]))
    print("(* = has GNSS)")


def print_timeseries(cfg, epochs, res, names):
    for name in names:
        r = res[name]
        print(f"\nError over time, {name} (m)")
        print(f"{'t':>5s}" + "".join(f"{'a' + str(a):>8s}" for a in range(cfg.n_agents)))
        for k, ep in enumerate(epochs):
            if int(ep.t) % TS_STEP == 0:
                print(f"{int(ep.t):5d}" + "".join(fmt(v, 8) for v in r["err"][k]))


def print_spoof(cfg, epochs, res):
    s0 = cfg.spoof_agent
    others = [a for a in range(cfg.n_agents) if a != s0]
    kk = [k for k, ep in enumerate(epochs) if ep.t >= cfg.spoof_start]
    pre = [k for k, ep in enumerate(epochs) if ep.t < cfg.spoof_start]
    print(f"\nGNSS spoofing of agent {s0}: walk-off {cfg.spoof_rate} m/s at {cfg.spoof_dir_deg} deg from "
          f"t={cfg.spoof_start:.0f} s (offset {math.hypot(*epochs[-1].spoof_offset):.0f} m at end)")
    print(f"{'method':24s}{'a' + str(s0) + ' RMSE':>10s}{'others':>8s}{'oth max':>9s}{'oth end':>9s}"
          f"{'pre RMSE':>10s}{'B/s/ag':>8s}  detections (t, agent)")
    for name, r in res.items():
        a0 = rms([r["err"][k][s0] for k in kk])
        ot = rms([r["err"][k][a] for k in kk for a in others])
        omax = max(r["err"][k][a] for k in kk for a in others)
        oend = statistics.mean(r["err"][-1][a] for a in others)
        pre_rmse = rms([r["err"][k][a] for k in pre for a in range(cfg.n_agents)])
        det = r["detections"]
        dtxt = ", ".join(f"({t:.0f},{a})" for t, a in det[:4]) + (" ..." if len(det) > 4 else "")
        bps = r["bytes"] / len(epochs) / cfg.n_agents
        print(f"{name:24s}{fmt(a0, 10)}{fmt(ot, 8)}{fmt(omax, 9)}{fmt(oend, 9)}{fmt(pre_rmse, 10)}{fmt(bps, 8)}  {dtxt or '-'}")
    print("RMSE columns cover t >= spoof start; 'pre RMSE' is all agents before it.")


def write_csv(outdir, cfg, epochs, res):
    os.makedirs(outdir, exist_ok=True)
    for name, r in res.items():
        path = os.path.join(outdir, f"{name.replace('+', '_')}.csv")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t", "agent", "true_x", "true_y", "est_x", "est_y", "sigma_x", "sigma_y", "err_m"])
            for k, ep in enumerate(epochs):
                for a in range(cfg.n_agents):
                    ex, ey, sx, sy = r["est"][k][a]
                    w.writerow([int(ep.t), a, f"{ep.truth[a][0]:.2f}", f"{ep.truth[a][1]:.2f}", f"{ex:.2f}",
                                f"{ey:.2f}", f"{sx:.2f}", f"{sy:.2f}", f"{r['err'][k][a]:.2f}"])
    print(f"\nwrote {len(res)} CSV files to {outdir}")


def print_meas_stats(cfg, epochs):
    c = {k: sum(ep.counts[k] for ep in epochs) for k in epochs[0].counts}
    got = sum(len(ep.ranges) for ep in epochs)
    nb = sum(1 for ep in epochs for m in ep.ranges if m.bearing is not None)
    heard = sum(ep.heard[a][o] for ep in epochs for a in range(cfg.n_agents) for o in range(cfg.n_agents) if a != o)
    up = sum(ep.uplink_ok[a] for ep in epochs for a in range(cfg.n_agents))
    hops = [h for ep in epochs for h in ep.hops if h]
    print(f"ranging: {c['attempts']} attempts, {c['dropouts']} dropouts, {got} ranges "
          f"({c['nlos']} NLOS-biased, {c['outliers']} gross outliers), {nb} bearings")
    print(f"comms: {heard} of {len(epochs) * cfg.n_agents * (cfg.n_agents - 1)} broadcast receptions, "
          f"{up} of {len(epochs) * cfg.n_agents} uplinks reached the leader, "
          f"mean hops {statistics.mean(hops) if hops else 0:.2f}, max {max(hops) if hops else 0}")


def monte_carlo(args, scenario):
    rows = {}
    for seed in range(1, args.seeds + 1):
        cfg = make_cfg(args, seed)
        _, epochs, res = run(cfg, scenario)
        for name, r in res.items():
            s = summarize(cfg, epochs, r)
            if scenario == "spoof":
                kk = [k for k, ep in enumerate(epochs) if ep.t >= cfg.spoof_start]
                oth = [a for a in range(cfg.n_agents) if a != cfg.spoof_agent]
                s["others"] = rms([r["err"][k][a] for k in kk for a in oth])
                s["a0"] = rms([r["err"][k][cfg.spoof_agent] for k in kk])
                s["false"] = sum(1 for t, _ in r["detections"] if t < cfg.spoof_start)
                post = [t for t, _ in r["detections"] if t >= cfg.spoof_start]
                s["latency"] = post[0] - cfg.spoof_start if post else None
            else:
                s["false"] = len(r["detections"])
            rows.setdefault(name, []).append(s)
    print(f"\nMonte Carlo, {args.seeds} seeds, scenario={scenario}, bearing={'on' if args.bearing else 'off'}: "
          "mean [min, max] over seeds")
    if scenario == "spoof":
        print(f"{'method':24s}{'spoofed a RMSE':>22s}{'others RMSE':>22s}{'det':>5s}{'false':>6s}{'latency s':>16s}{'B/s/ag':>8s}")
        for name, ss in rows.items():
            a0 = [s["a0"] for s in ss]
            ot = [s["others"] for s in ss]
            lat = [s["latency"] for s in ss if s["latency"] is not None]
            ltxt = f"{statistics.median(lat):5.0f} [{min(lat):3.0f},{max(lat):4.0f}]" if lat else "-"
            print(f"{name:24s}{statistics.mean(a0):8.1f} [{min(a0):5.1f},{max(a0):6.1f}]"
                  f"{statistics.mean(ot):8.1f} [{min(ot):5.1f},{max(ot):6.1f}]{len(lat):5d}"
                  f"{sum(s['false'] for s in ss):6d}{ltxt:>16s}{statistics.mean(s['bps_agent'] for s in ss):8.1f}")
        print("det = seeds with a detection at or after spoof start; false = detections before it; "
              "latency = median [min, max] of first detection - spoof start")
    else:
        print(f"{'method':22s}{'team RMSE':>24s}{'denied RMSE':>24s}{'NEES':>8s}{'B/s/ag':>8s}")
        for name, ss in rows.items():
            a = [s["rmse"] for s in ss]
            d = [s["rmse_denied"] for s in ss]
            ne = statistics.mean(s["nees"] for s in ss)
            bps = statistics.mean(s["bps_agent"] for s in ss)
            print(f"{name:22s}{statistics.mean(a):8.1f} [{min(a):6.1f},{max(a):7.1f}]"
                  f"{statistics.mean(d):8.1f} [{min(d):6.1f},{max(d):7.1f}]{ne:8.1f}{bps:8.1f}")


def make_cfg(args, seed):
    return Config(n_agents=args.agents, gnss_agents=tuple(args.gnss), duration=args.duration, bearing=args.bearing,
                  packet_loss=args.loss, comm_range=args.comm_range, max_links=args.max_links, seed=seed,
                  spoof_rate=args.spoof_rate)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", choices=["nominal", "spoof"], default="nominal")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seeds", type=int, default=0, help="Monte Carlo over seeds 1..N instead of one run")
    ap.add_argument("--agents", type=int, default=6)
    ap.add_argument("--gnss", type=int, nargs="+", default=[0, 1], help="agents that keep GNSS")
    ap.add_argument("--duration", type=int, default=600)
    ap.add_argument("--bearing", action="store_true", help="add camera relative bearings")
    ap.add_argument("--loss", type=float, default=0.10, help="packet loss per hop")
    ap.add_argument("--comm-range", type=float, default=250.0)
    ap.add_argument("--max-links", type=int, default=3, help="ranging slots per agent per epoch")
    ap.add_argument("--spoof-rate", type=float, default=0.5)
    ap.add_argument("--timeseries", action="store_true", help="print per-agent error tables for every method")
    ap.add_argument("--csv", metavar="DIR", help="write per-method time series CSVs")
    args = ap.parse_args()
    if args.seeds:
        monte_carlo(args, args.scenario)
        return
    cfg = make_cfg(args, args.seed)
    _, epochs, res = run(cfg, args.scenario)
    print_meas_stats(cfg, epochs)
    if args.scenario == "spoof":
        print_spoof(cfg, epochs, res)
        names = list(res) if args.timeseries else ["central-robust", "central-robust+ss", "ci-robust", "ci-robust+ss"]
    else:
        print_nominal(cfg, epochs, res)
        names = list(res) if args.timeseries else ["dead-reckoning", "central-robust", "ci-robust"]
    print_timeseries(cfg, epochs, res, names)
    print("\ncpu per method (s): " + ", ".join(f"{k} {v['cpu_s']:.1f}" for k, v in res.items()))
    if args.csv:
        write_csv(args.csv, cfg, epochs, res)


if __name__ == "__main__":
    main()
