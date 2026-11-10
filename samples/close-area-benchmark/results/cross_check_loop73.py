"""loop-73 checks for the 7 rows added to matrix_0 by `bench.py --add-to matrix_0` (stdlib only).

    python3 samples/close-area-benchmark/results/cross_check_loop73.py     # from the repo root, < 2 s

1. Old rows unchanged: every run of the 14 older planners equals the committed matrix_0.json
   (`git show HEAD:samples/close-area-benchmark/results/matrix_0.json`), and so does their summary.
2. Same as the source sample's own run, run by run, on outcome, min clearance, time to goal and path length:
   close-area-planner-thetastar results/flights_0.json, close-area-planner-mppi results/bench_ideal_0.json and
   bench_crazyflie_0.json (its "mppi_none" = matrix "mppi"), close-area-planner-hybrid-astar results/bench_0.json
   (vehicle "stock" only; "turn1" is a different vehicle).
Writes results/matrix_0_loop73_checks.md. Input: synthetic.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.dirname(SAMPLES)
NEW = ("thetastar_known", "lazy_thetastar_known", "thetastar_unknown", "lazy_thetastar_unknown", "mppi",
       "mppi_astar", "hybrid_astar")
KEYS = ("outcome", "min_clearance_m", "time_to_goal_s", "path_length_m")


def main():
    m = json.load(open(os.path.join(HERE, "matrix_0.json")))
    head = json.loads(subprocess.run(["git", "show", "HEAD:samples/close-area-benchmark/results/matrix_0.json"],
                                     cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    old = [r for r in m["runs"] if r["planner"] not in NEW]
    same_runs = old == head["runs"]
    same_summ = all(m["summary"][pr][p] == head["summary"][pr][p] for pr in head["summary"] for p in head["summary"][pr])
    mx = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in m["runs"]}
    srcs = [
        ("close-area-planner-thetastar/results/flights_0.json", {p: p for p in NEW if "theta" in p}, None),
        ("close-area-planner-mppi/results/bench_ideal_0.json", {"mppi_none": "mppi", "mppi_astar": "mppi_astar"}, None),
        ("close-area-planner-mppi/results/bench_crazyflie_0.json", {"mppi_none": "mppi", "mppi_astar": "mppi_astar"}, None),
        ("close-area-planner-hybrid-astar/results/bench_0.json", {"hybrid_astar": "hybrid_astar"}, "stock"),
    ]
    rows, diffs = [], []
    for path, names, vehicle in srcs:
        d = json.load(open(os.path.join(SAMPLES, path)))
        per = {}
        for r in d["runs"]:
            if r["planner"] not in names or (vehicle and r.get("vehicle") != vehicle):
                continue
            p = names[r["planner"]]
            o = mx.get((p, r["family"], r["preset"], r["index"]))
            ok = o is not None and all(o.get(k) == r.get(k) for k in KEYS)
            c = per.setdefault((p, r["preset"]), [0, 0])
            c[0] += int(ok)
            c[1] += 1
            if not ok:
                diffs.append(f"{p} {r['preset']} {r['family']} #{r['index']}")
        rows += [(path, p, pr, f"{c[0]}/{c[1]}") for (p, pr), c in per.items()]
    md = ["`python3 samples/close-area-benchmark/results/cross_check_loop73.py`. Input: synthetic. Checks for the 7 rows "
          "added by `bench.py --add-to matrix_0` in loop-73.", "",
          f"1. Older rows unchanged vs the committed matrix_0.json (git HEAD): {len(old)} runs "
          f"{'identical' if same_runs else 'DIFFER'}, summaries {'identical' if same_summ else 'DIFFER'}.", "",
          "2. Matrix rows vs the source sample's own run (same family, preset, layout index, seed 0), identical in "
          + ", ".join(KEYS) + ":", "", "| source file | matrix row | preset | runs identical |", "|---|---|---|---|"]
    md += [f"| samples/{s} | {p} | {pr} | {v} |" for s, p, pr, v in rows]
    md += ["", f"Differences: {len(diffs)}" + (" (" + ", ".join(diffs[:40]) + ")" if diffs else ""), ""]
    open(os.path.join(HERE, "matrix_0_loop73_checks.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
