"""Fly RRT* (best sweep setting) and the A* baseline in close-area-arena, scored on truth.

python bench.py [--layouts 50] [--seed 0] [--families random,narrow_gap] [--iters 5000] [--informed 1]
Writes results/arena_<family>_<seed>.json and .md, same table columns as the arena's
results/astar_esdf_<family>_<seed>.md.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import arena  # noqa: E402
import rrt_star  # noqa: E402

RESULTS = os.path.join(HERE, "results")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--families", default="random,narrow_gap")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--informed", type=int, default=1)
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    import scipy
    os.makedirs(a.out, exist_ok=True)
    rrt_name = f"{'informed_' if a.informed else ''}rrt_star iters={a.iters}"
    for fam in a.families.split(","):
        out = {"family": fam, "seed": a.seed, "layouts": a.layouts, "input": "synthetic", "command": cmd,
               "config": arena.run.DEFAULTS,
               "rrt_constants": {k: v for k, v in vars(rrt_star).items() if k.isupper() and isinstance(v, (int, float))},
               "env": {"python": platform.python_version(), "numpy": np.__version__,
                       "scipy": scipy.__version__, "machine": platform.machine(), "system": platform.system()},
               "modes": {}}
        for name in ("astar_esdf known_map", rrt_name):
            made = []

            def factory(name=name, made=made):
                if name.startswith("astar"):
                    p = arena.astar_esdf.AStarESDF(known_map=True)
                else:   # RNG seed per layout = layout index, so a run is repeatable
                    p = rrt_star.RRTStarPlanner(iters=a.iters, informed=bool(a.informed), seed=len(made))
                made.append(p)
                return p

            t0 = time.perf_counter()
            rows, summ, _ = arena.run.evaluate(factory, fam, a.layouts, a.seed)
            wall = time.perf_counter() - t0
            for r, p in zip(rows, made):
                r["replans"] = len(p.replan_ms)
                r["fallback_replans"] = p.fallbacks
                r["no_path_replans"] = p.no_path
            ms = [m for p in made for m in p.replan_ms]
            plan = {"replans": len(ms),
                    "median_ms": round(float(np.median(ms)), 2) if ms else None,
                    "p95_ms": round(float(np.percentile(ms, 95)), 2) if ms else None,
                    "max_ms": round(float(np.max(ms)), 2) if ms else None,
                    "fallback_replans": sum(p.fallbacks for p in made),
                    "no_path_replans": sum(p.no_path for p in made)}
            out["modes"][name] = {"summary": summ, "planning": plan, "wall_s": round(wall, 1), "runs": rows}
            print(f"{fam} {name}: {summ} plan {plan} wall {wall:.1f} s", flush=True)
        stem = os.path.join(a.out, f"arena_{fam}_{a.seed}")
        with open(stem + ".json", "w") as fh:
            json.dump(out, fh, indent=1)
        f = lambda v: "-" if v is None else f"{v}"
        lines = [f"`{cmd}` from samples/close-area-planner-sampling (synthetic: simulated layouts, vehicle and sensor)\n",
                 "| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s "
                 "| median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |",
                 "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, m in out["modes"].items():
            s, p = m["summary"], m["planning"]
            lines.append(f"| {name} | {fam} | {s['n']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} | "
                         f"{f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_time_to_goal_s'])} | "
                         f"{f(s['median_min_clearance_m'])} | {p['replans']} | {f(p['median_ms'])} | "
                         f"{f(p['p95_ms'])} | {p['fallback_replans']} | {p['no_path_replans']} | {m['wall_s']} |")
        names = list(out["modes"])
        lines += ["", "Per run (outcome, min clearance m, path m):", "",
                  "| run | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for i in range(a.layouts):
            cells = [f"{out['modes'][n]['runs'][i]['outcome']} {out['modes'][n]['runs'][i]['min_clearance_m']} "
                     f"{out['modes'][n]['runs'][i]['path_length_m']}" for n in names]
            lines.append(f"| {i} | " + " | ".join(cells) + " |")
        with open(stem + ".md", "w") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
