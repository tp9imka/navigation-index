"""Run the USV transit scenarios and write metrics, navdash/1 tracks and own-ship CoT.

  python3 run.py                         # all scenarios, seed 1, writes out/
  python3 run.py --scenarios spoof-coastal --seeds 1 2 3 4 5 --no-export
"""
import argparse
import json
import math
import multiprocessing
import os
import statistics
import time
from pathlib import Path

import chart as chartmod
import export
import matcher
import sim
from nav import Navigator

RADAR_PERIOD_S = 5
CONFIGS = ("dr", "gnss_dr", "single", "monitor")
SHORT_RANGE = {"max_range": 1500.0}   # harbour range scale: little geometry in view
SCENARIOS = {
    "clean": (sim.Attack("none"), {}),
    "spoof-coastal": (sim.Attack("spoof", t_start=1500), {}),
    "spoof-open": (sim.Attack("spoof", t_start=60), {}),
    "jam": (sim.Attack("jam", t_start=1200), {}),
    "spoof-coastal-1500m": (sim.Attack("spoof", t_start=1500), SHORT_RANGE),
}
LEG_NAMES = ["open water by Lillgrund", "Drogden south", "Drogden channel", "off Kastrup",
             "Kongedybet / Middelgrunden"]


def leg_of(x, y):
    from geo import closest_on_segment
    best = min(range(len(sim.ROUTE_XY) - 1),
               key=lambda k: closest_on_segment(x, y, *sim.ROUTE_XY[k], *sim.ROUTE_XY[k + 1])[0])
    return best


def generate_world(seed, radar_kw=None):
    frame, chart, world = chartmod.chart_and_world(seed)
    truth = sim.truth_trajectory()
    dr = sim.DrSensors().generate(truth, sim.make_rng(seed, "dr"))
    ships = sim.AisTraffic(frame)
    radar = sim.Radar(**(radar_kw or {}))
    rr = sim.make_rng(seed, "radar")
    scans = {}
    for s in truth:
        if int(s.t) % RADAR_PERIOD_S == 0:
            scans[int(s.t)] = radar.scan(world, ships.at(s.t), s.x, s.y, s.psi, rr)
    return frame, chart, truth, dr, scans, ships, radar


def run_config(mode, chart, truth, dr, gnss, scans, radar):
    s0 = truth[0]
    nav = Navigator(mode, s0.x, s0.y)
    rows, fixes = [], []
    for k, s in enumerate(truth):
        psi_m, v_m, _ = dr[k]
        if k:
            nav.predict(psi_m, v_m, s.t - truth[k - 1].t)
        if nav.use_radar() and int(s.t) in scans:
            pf = nav.radar_prior()
            fx = matcher.match(chart, scans[int(s.t)], pf.x[0], pf.x[1], pf.heading(psi_m),
                               pf.sigma_major(), radar.sigma_range)
            res = nav.on_radar(s.t, fx, psi_m)
            fixes.append((s.t, fx, res))
        nav.on_gnss(s.t, gnss[k])
        nav.check(s.t)
        m = nav.main
        rows.append({"t": s.t, "x": m.x[0], "y": m.x[1], "sigma": m.sigma_major(), "pl": nav.pl(),
                     "excluded": nav.excluded, "alarm": nav.alarm, "ss": nav.last_ss,
                     "sub": (nav.sub.x[0], nav.sub.x[1], nav.sub.sigma_major()) if nav.sub else None,
                     "err": math.hypot(m.x[0] - s.x, m.x[1] - s.y)})
    return rows, fixes, nav.events


def err_stats(errs):
    if not errs:
        return {}
    s = sorted(errs)
    return {"rms": math.sqrt(sum(e * e for e in errs) / len(errs)), "p95": s[int(0.95 * (len(s) - 1))],
            "max": s[-1], "final": errs[-1]}


def summarize(name, attack, truth, results, gnss):
    out = {"scenario": name, "attack": attack.__dict__, "duration_s": truth[-1].t,
           "distance_km": sum(math.hypot(b.x - a.x, b.y - a.y) for a, b in zip(truth, truth[1:])) / 1000,
           "configs": {}}
    for mode, (rows, fixes, events) in results.items():
        errs = [r["err"] for r in rows]
        c = {"all": err_stats(errs)}
        att = [r["err"] for r in rows if r["t"] >= attack.t_start]
        if att:
            c["during_attack"] = err_stats(att)
        alarms = [t for t, ev, _ in events if ev in ("spoof_suspected", "alarm_raised")]
        excl = [t for t, ev, _ in events if ev == "spoof_suspected"]
        c["alarms"] = len(alarms)
        c["false_alarms"] = len([t for t in alarms if t < attack.t_start])
        c["false_exclusions"] = len([t for t in excl if t < attack.t_start])
        spoof = attack.kind == "spoof"
        hit = [t for t in alarms if t >= attack.t_start]
        hit_x = [t for t in excl if t >= attack.t_start]
        c["detection_s"] = hit[0] - attack.t_start if hit and spoof else None
        c["exclusion_s"] = hit_x[0] - attack.t_start if hit_x and spoof else None
        if hit and spoof:
            c["spoof_offset_at_detection_m"] = math.hypot(*attack.offset(hit[0]))
        c["events"] = [{"t": t, "event": ev, "text": tx} for t, ev, tx in events]
        if rows[0]["sub"]:
            c["gnss_free_subfilter"] = err_stats([math.hypot(r["sub"][0] - s.x, r["sub"][1] - s.y)
                                                  for r, s in zip(rows, truth)])
        out["configs"][mode] = c
    fixes = results["monitor"][1]
    legs = {}
    by_t = {int(s.t): s for s in truth}
    for t, fx, res in fixes:
        s = by_t[int(t)]
        L = legs.setdefault(leg_of(s.x, s.y), {"scans": 0, "reasons": {}, "fix_err": []})
        L["scans"] += 1
        L["reasons"][fx.reason] = L["reasons"].get(fx.reason, 0) + 1
        if fx.ok:
            e = math.hypot(fx.x - s.x, fx.y - s.y)
            L["fix_err"].append(e)
    out["radar_by_leg"] = []
    for k in sorted(legs):
        L = legs[k]
        row = {"leg": k, "name": LEG_NAMES[k], "scans": L["scans"], "reasons": L["reasons"]}
        if L["fix_err"]:
            v = sorted(L["fix_err"])
            row["fix_err_median_m"] = statistics.median(v)
            row["fix_err_p95_m"] = v[int(0.95 * (len(v) - 1))]
        out["radar_by_leg"].append(row)
    rej = sum(1 for _, fx, res in fixes if fx.ok and res.get("sub") and not res["sub"][0])
    out["radar_fixes_rejected_by_subfilter_gate"] = rej
    return out


def run_scenario(name, seed):
    attack, radar_kw = SCENARIOS[name]
    frame, chart, truth, dr, scans, ships, radar = generate_world(seed, radar_kw)
    gnss = sim.Gnss().generate(truth, attack, sim.make_rng(seed, f"gnss:{attack.kind}:{attack.t_start}"))
    results = {m: run_config(m, chart, truth, dr, gnss, scans, radar) for m in CONFIGS}
    return frame, truth, dr, gnss, scans, results, attack


def task(args):
    name, seed, out, do_export = args
    t1 = time.time()
    frame, truth, dr, gnss, scans, results, attack = run_scenario(name, seed)
    sm = summarize(name, attack, truth, results, gnss)
    sm["seed"] = seed
    sm["radar"] = SCENARIOS[name][1] or "default"
    if do_export:
        export.write_all(Path(out) / name, name, frame, truth, dr, gnss, results, attack)
    print(export.summary_line(sm), f"seed {seed} ({time.time() - t1:.0f} s)", flush=True)
    return sm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="+", default=list(SCENARIOS))
    ap.add_argument("--seeds", nargs="+", type=int, default=[1])
    ap.add_argument("--out", default="out")
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(exist_ok=True)
    jobs = [(name, seed, str(out), not a.no_export and seed == a.seeds[0])
            for seed in a.seeds for name in a.scenarios]
    with multiprocessing.Pool(min(a.jobs, len(jobs))) as pool:
        summaries = pool.map(task, jobs)
    (out / "summary.json").write_text(json.dumps(summaries, indent=1))
    (out / "summary.md").write_text(export.summary_markdown(summaries))
    print(f"wrote {out}/summary.json, {out}/summary.md")


if __name__ == "__main__":
    main()
