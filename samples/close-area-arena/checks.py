"""Sanity checks that the arena can fail a planner, saved so README can quote them.

python checks.py   # writes results/checks.json

1. BFS free-path guarantee vs gap width: a 0.3 m wall across the area with one gap.
2. Collision path of the scorer: the straight planner with its slow-down disabled.
"""
import json
import os

import run
import world as W
from planners.straight import StraightPlanner

HERE = os.path.dirname(os.path.abspath(__file__))


def gap_probe(gap: float) -> bool:
    lo = 10 - gap / 2
    hi = W.AREA - (10 + gap / 2)
    w = W.World("probe", 0, -1.5, -1.5, 18.5, 18.5, (17.0, 17.0), boxes=[
        W.Box(8.5, -1.5 + lo / 2, 0.15, lo / 2),
        W.Box(8.5, -1.5 + 10 + gap / 2 + hi / 2, 0.15, hi / 2)])
    w.grid = w.rasterize()
    blocked = w.grid.inflated(W.RADIUS)
    return W.bfs_free_path(blocked, w.grid.to_index(0, 0), w.grid.to_index(*w.goal)) is not None


def main():
    gaps = {f"{g:.2f}": gap_probe(g) for g in (0.0, 0.3, 0.35, 0.4, 0.5, 0.6)}
    blind = lambda: StraightPlanner(stop_dist=-10.0, slow_dist=-9.0)
    rows, summ, _ = run.evaluate(blind, "random", 20, 0)
    out = {
        "input": "synthetic",
        "bfs_gap_probe": {"note": "gap width m => free path found (vehicle radius 0.15 m, grid 0.1 m)",
                          "result": gaps},
        "straight_no_slowdown_random_seed0": {"params": {"stop_dist": -10.0, "slow_dist": -9.0},
                                              "summary": summ,
                                              "outcomes": [r["outcome"] for r in rows]},
    }
    path = os.path.join(HERE, "results", "checks.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({"gaps": gaps, "no_slowdown": summ}, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
