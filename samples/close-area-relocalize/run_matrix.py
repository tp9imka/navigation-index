"""Held-out matrix for the relocalization headline: seeds 2-4, 7 families, 2 faults, 3 arms.

.venv/bin/python run_matrix.py --part parity     # seed 1 random 30 layouts vs results/disamb_random_1.json
.venv/bin/python run_matrix.py --part matrix     # seeds 2-4 x 7 families x dropout/jump x (b)/(c)/(f), 30 layouts
.venv/bin/python run_matrix.py --part rungs      # random seed 2: jump 1.0 / 2.0 m, dropout 5 s, 30 layouts
.venv/bin/python run_matrix.py --part refs       # same layouts: truth pose and (a) estimator only, no relocalization

Arms (unchanged code from experiment.py and run_disambiguate.py, A* known map, scored on truth):
  single    (b) commit to the best match at once + innovation test
  multi     (c) RatioPersistence, hover until accept
  multi_ig  (f) (c) + after 1 s an expected-entropy-reduction move (Fox 1998 style)
Families: random, u_trap, narrow_gap, office, warehouse, maze, glass_office. Sensor: the arena's
default 72-ray 6 m fan ("ideal" preset), which sees glass. Run time limit 60 s, 120 s for maze and
warehouse (as close-area-benchmark/bench.py LONG_FAMILIES).
Faults: the arena's dropout (2 s) and jump (0.5 m); rungs reuse the same seeded start time and
direction (rng [seed, index, 4200 + code]) with jump step 1.0 / 2.0 m or dropout 5 s.
Nothing was tuned on seeds 2-4. Input: synthetic.
Writes results/reloc_matrix_<part>.json / .md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy

from arena import estimator, faults, run, world
import experiment as X
import relocalize as R
import run_disambiguate as RD

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("single", "multi", "multi_ig")
REF_ARMS = ("truth", "estimator")
LABEL = dict(RD.LABEL, truth="(ref)", estimator="(a)")
FAMILIES = ("random", "u_trap", "narrow_gap", "office", "warehouse", "maze", "glass_office")
LONG_FAMILIES = {"maze": 120.0, "warehouse": 120.0}
SEEDS = (2, 3, 4)
FAULTS = ("dropout", "jump")
RUNGS = ("jump_1.0m", "jump_2.0m", "dropout_5s")
Z = 1.959964                     # 95 % two-sided, as close-area-safety-filter/results/kill_e_tables.py
PASS_REACH = 95.0


def wilson(k, n):
    """95 % Wilson score interval in percent (copied from kill_e_tables.py)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (100 * max(0.0, c - h), 100 * min(1.0, c + h))


def make_fault(spec, w, seed, index):
    """Base arena fault, or a severity rung with the same seeded stream as the base case."""
    if spec in faults.CASES:
        return faults.make(spec, w, seed, index)
    base, val = spec.split("_")
    rng = np.random.default_rng([seed, index, 4200 + faults.CASES.index(base)])
    if base == "jump":
        f = faults.Jump(w, rng, step_m=float(val.rstrip("m")))
    else:
        f = faults.Dropout(w, rng, dur_s=float(val.rstrip("s")))
    f.log["fault"] = spec
    return f


def make_est(spec, w, seed, index):
    """As estimator.make_pose_source_factory(fault, dark=True): same rng streams."""
    zones = estimator.make_dark_zones(w, np.random.default_rng([seed, index, 4001]))
    return estimator.VioEstimator(np.random.default_rng([seed, index, 4101]), zones, make_fault(spec, w, seed, index))


def cfg_for(family):
    cfg = dict(run.DEFAULTS)
    cfg["max_time_s"] = LONG_FAMILIES.get(family, run.DEFAULTS["max_time_s"])
    return cfg


def compact(row):
    """Per-run fields kept in the JSON (the full event logs would be ~20 MB)."""
    keep = ("outcome", "reached", "collision", "stuck", "timeout", "time_to_goal_s", "index", "est_err_max_m",
            "est_err_median_m", "hover_s", "move_s", "wrong_commits", "match_ms_median")
    out = {k: row.get(k) for k in keep}
    out["fault_fired_t"] = (row.get("fault_log") or {}).get("fired_t")
    out["events"] = [{"reason": e["reason"], "result": e["result"], "err_m": e["err_m"], "recover_s": e["recover_s"],
                      "last_verdict": e["last_verdict"], "last_returns": e["last_returns"],
                      "truth_in_set": e["truth_in_set"],
                      "moves": len([m for m in e.get("moves", []) if m.get("move") is not None])}
                     for e in row.get("events", [])]
    return out


def run_task(args):
    seed, family, spec, arm, index = args
    w = world.make_world(family, seed, index)
    est = make_est(spec, w, seed, index)
    if arm in REF_ARMS:                       # reference: truth pose, or (a) estimator only
        src, planner = (None if arm == "truth" else est), X.planner_for(arm)
    else:
        src, planner = RD.build(arm, w, est, seed, index)
    t0 = time.perf_counter()
    row, _, _ = run.run_one(planner, w, seed, index, cfg_for(family), src)
    if src is not None:
        row.update(RD.extra(row, est, src, est.fault))
    row["wall_s"] = round(time.perf_counter() - t0, 2)
    return args, row


def cell_stats(rows):
    s = RD.summarize(rows)
    n, k = s["n"], sum(1 for r in rows if r["reached"])
    kw = s["runs_with_wrong_commit"]
    lo, hi = wilson(k, n)
    wlo, whi = wilson(kw, n)
    return {"n": n, "reached": k, "reached_pct": round(100 * k / n, 1) if n else None,
            "reached_ci95": [round(lo, 1), round(hi, 1)],
            "collision_pct": s["collision_pct"], "stuck_pct": s["stuck_pct"], "timeout_pct": s["timeout_pct"],
            "accepted": s["accepted"], "wrong_commits": s["wrong_commits"], "runs_with_wrong_commit": kw,
            "runs_with_wrong_commit_ci95": [round(wlo, 1), round(whi, 1)],
            "open_at_end": s["open_at_end"], "open_by_last_verdict": s["open_by_last_verdict"],
            "runs_ended_hovering": s["runs_ended_hovering"], "no_feasible_move": s["no_feasible_move"],
            "moves_total": s["moves_total"], "median_recover_s": s["median_recover_s"],
            "p95_recover_s": s["p95_recover_s"], "max_recover_s": s["max_recover_s"],
            "fault_fired_runs": s["fault_fired_runs"]}


def fmt_ci(c):
    return f"{c[0]:.1f}-{c[1]:.1f}"


HEAD = ("| family | fault | arm | runs | reached % | 95 % CI | per seed reached % | collision % | stuck % | timeout % "
        "| wrong commits (> 0.5 m) | runs with a wrong commit (95 % CI) | still hovering at end: none (< 10 returns) "
        "/ none (low score) / ambiguous | fault fired runs |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(fam, fl, arm, s, per_seed):
    o = s["open_by_last_verdict"]
    return (f"| {fam} | {fl} | {LABEL[arm]} {arm} | {s['n']} | {s['reached_pct']} | {fmt_ci(s['reached_ci95'])} "
            f"| {per_seed} | {s['collision_pct']} | {s['stuck_pct']} | {s['timeout_pct']} | {s['wrong_commits']} "
            f"| {s['runs_with_wrong_commit']} ({fmt_ci(s['runs_with_wrong_commit_ci95'])}) "
            f"| {o['none_too_few_returns']} / {o['none_low_score']} / {o['ambiguous']} | {s['fault_fired_runs']} |")


def verdict(s):
    if s["reached_pct"] >= PASS_REACH and s["wrong_commits"] == 0:
        return "PASS" + (" (CI low >= 95)" if s["reached_ci95"][0] >= PASS_REACH else "")
    return "FAIL"


def execute(tasks, workers):
    rows = {}
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for j, (args, row) in enumerate(ex.map(run_task, tasks, chunksize=4)):
            rows[args] = row
            if (j + 1) % 200 == 0:
                print(f"{j + 1}/{len(tasks)} runs, {time.perf_counter() - t0:.0f} s", flush=True)
    return rows, round(time.perf_counter() - t0, 1)


def env_info():
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system(), "date": time.strftime("%Y-%m-%d")}


def part_parity(a):
    """Seed 1 random, first N layouts, vs the driver's run_disambiguate.py seed-1 file (same code path)."""
    ref = json.load(open(os.path.join(RESULTS, "disamb_random_1.json")))["results"]
    tasks = [(1, "random", fl, arm, i) for fl in FAULTS for arm in ARMS for i in range(a.layouts)]
    rows, wall = execute(tasks, a.workers)
    same = diff = 0
    bad = []
    for (seed, fam, fl, arm, i), row in rows.items():
        r0 = ref[fl][arm]["runs"][i]
        ok = r0["outcome"] == row["outcome"] and r0.get("wrong_commits") == row.get("wrong_commits") \
            and r0["time_to_goal_s"] == row["time_to_goal_s"]
        same += ok
        diff += not ok
        if not ok:
            bad.append([fl, arm, i, r0["outcome"], row["outcome"]])
    md = (f"`python run_matrix.py --part parity --layouts {a.layouts}` (synthetic), wall {wall} s, {a.workers} workers.\n\n"
          f"Seed 1 random, layouts 0-{a.layouts - 1}, dropout and jump, arms (b) (c) (f): {same} of {same + diff} runs have "
          f"the same outcome, wrong commits and time to goal as results/disamb_random_1.json. Mismatches: {bad or 'none'}.\n")
    print(md)
    with open(os.path.join(a.out, "reloc_matrix_parity.md"), "w") as fh:
        fh.write(md)


def summarize_part(rows, seeds, families, fspecs, arms=ARMS):
    res = {}
    for fam in families:
        for fl in fspecs:
            for arm in arms:
                per = {sd: [rows[(sd, fam, fl, arm, i)] for i in sorted(i for (s2, f2, l2, a2, i) in rows
                                                                       if (s2, f2, l2, a2) == (sd, fam, fl, arm))]
                       for sd in seeds}
                allr = [r for sd in seeds for r in per[sd]]
                if not allr:
                    continue
                st = cell_stats(allr)
                st["per_seed"] = {str(sd): cell_stats(per[sd]) for sd in seeds}
                res.setdefault(fam, {}).setdefault(fl, {})[arm] = {"summary": st,
                                                                   "runs": {str(sd): [compact(r) for r in per[sd]] for sd in seeds}}
    return res


def table(res, seeds):
    lines = [HEAD]
    for fam, d in res.items():
        for fl, da in d.items():
            for arm, c in da.items():
                ps = "/".join(f"{c['summary']['per_seed'][str(sd)]['reached_pct']:g}" for sd in seeds)
                lines.append(line(fam, fl, arm, c["summary"], ps))
    return "\n".join(lines)


def verdict_table(res):
    out = ["| family | (f) dropout reached % (95 % CI) | (f) jump reached % (95 % CI) | (f) both faults reached % (95 % CI) "
           "| (f) wrong commits | verdict: >= 95 % reach and 0 wrong commits | (b) reached % / wrong commits "
           "| (c) reached % / wrong commits |", "|---|---|---|---|---|---|---|---|"]
    for fam, d in res.items():
        fs = [d[fl]["multi_ig"]["summary"] for fl in FAULTS]
        k, n, wc = sum(s["reached"] for s in fs), sum(s["n"] for s in fs), sum(s["wrong_commits"] for s in fs)
        lo, hi = wilson(k, n)
        both = {"reached_pct": round(100 * k / n, 1), "wrong_commits": wc, "reached_ci95": [lo, hi]}
        bc = []
        for arm in ("single", "multi"):
            ss = [d[fl][arm]["summary"] for fl in FAULTS]
            bc.append(f"{100 * sum(s['reached'] for s in ss) / sum(s['n'] for s in ss):.1f} / {sum(s['wrong_commits'] for s in ss)}")
        out.append(f"| {fam} | " + " | ".join(f"{s['reached_pct']} ({fmt_ci(s['reached_ci95'])})" for s in fs)
                   + f" | {both['reached_pct']} ({fmt_ci([lo, hi])}) | {wc} | {verdict(both)} | {bc[0]} | {bc[1]} |")
    return "\n".join(out)


def part_grid(a, part):
    arms = ARMS
    if part in ("matrix", "refs"):
        seeds, families, fspecs = SEEDS, FAMILIES, FAULTS
        if part == "refs":
            arms = REF_ARMS
    else:
        seeds, families, fspecs = (2,), ("random",), RUNGS
    tasks = [(sd, fam, fl, arm, i) for fam in families for sd in seeds for fl in fspecs for arm in arms
             for i in range(a.layouts) if not (arm == "truth" and fl != fspecs[0])]   # truth ignores the fault
    tasks.sort(key=lambda t: t[1] not in LONG_FAMILIES)      # long families first so the pool does not end on them
    rows, wall = execute(tasks, a.workers)
    res = summarize_part(rows, seeds, families, fspecs, arms)
    tab = table(res, seeds)
    cmd = f"python run_matrix.py --part {part} --layouts {a.layouts}"
    md = [f"`{cmd}` (synthetic), wall {wall} s, {a.workers} workers, seeds {list(seeds)}, {a.layouts} layouts per seed "
          f"per cell. Run time limit 60 s, 120 s for maze and warehouse. Reached % and runs with a wrong commit carry "
          f"95 % Wilson intervals. 'still hovering at end' counts loss events open when the run ended, by the last "
          f"rule verdict.", "", tab]
    if part == "matrix":
        md += ["", "Per family verdict for (f) multi_ig, both faults pooled "
               f"({2 * len(seeds) * a.layouts} runs per family): PASS = reached >= 95 % and 0 wrong commits; "
               "'(CI low >= 95)' when the Wilson lower bound also clears 95 %.", "", verdict_table(res)]
    md = "\n".join(md) + "\n"
    print(md)
    params = {k: getattr(R, k) for k in ("S_MIN", "RATIO", "N_SCANS", "W0_M", "W_MAX_M", "SEP_M", "K_MAX",
                                          "MIN_RETURNS", "S_INNOV", "INNOV_SCANS", "SETTLE_SCANS")}
    with open(os.path.join(a.out, f"reloc_matrix_{part}.json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "seeds": list(seeds), "families": list(families),
                   "faults": list(fspecs), "arms": list(ARMS), "layouts": a.layouts, "wall_s": wall,
                   "workers": a.workers, "max_time_s": {f: cfg_for(f)["max_time_s"] for f in families},
                   "params": params, "config": run.DEFAULTS, "env": env_info(), "results": res}, fh)
    with open(os.path.join(a.out, f"reloc_matrix_{part}.md"), "w") as fh:
        fh.write(md)
    print(f"wrote reloc_matrix_{part}.json / .md")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", choices=("parity", "matrix", "rungs", "refs"), required=True)
    ap.add_argument("--layouts", type=int, default=30)
    ap.add_argument("--workers", type=int, default=min(14, os.cpu_count() or 1))
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    if a.part == "parity":
        part_parity(a)
    else:
        part_grid(a, a.part)


if __name__ == "__main__":
    main()
