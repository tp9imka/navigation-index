"""Compare A* + carrot with A* + corridor MPC on the arena, and plot one narrow_gap run.

.venv/bin/python bench.py --layouts 50 --seed 0 [--families random,narrow_gap] [--out results]

Followers (all on the same A*: known map, replanned every 0.4 s, arena planners/astar_esdf.py):
  astar_carrot           the arena carrot follower, unchanged
  astar_mpc              mpc.AStarMPC, warm start, corridor on
  astar_mpc_cold         same, OSQP warm start off (iterations / time ablation)
  astar_mpc_nocorridor   same, obstacle half-planes off, window box only (does the corridor matter)
Writes <out>/mpc_compare_<seed>.json (summary + per-run rows), .md (tables) and
<out>/mpc_narrow_gap_<seed>_run<k>.png.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time

import numpy as np

import arena
import mpc

HERE = os.path.dirname(os.path.abspath(__file__))

FOLLOWERS = {
    "astar_carrot": lambda: mpc.CarrotTracked(known_map=True),
    "astar_mpc": lambda: mpc.AStarMPC(known_map=True),
    "astar_mpc_cold": lambda: mpc.AStarMPC(known_map=True, warm=False),
    "astar_mpc_nocorridor": lambda: mpc.AStarMPC(known_map=True, use_corridor=False),
    "astar_mpc_fast": lambda: mpc.AStarMPC(known_map=True, clearance_speed=False),
    "astar_mpc_fast_nocorridor": lambda: mpc.AStarMPC(known_map=True, clearance_speed=False, use_corridor=False),
}


def pct(a, q):
    a = np.asarray([v for v in a if np.isfinite(v)], float)
    return None if not len(a) else round(float(np.percentile(a, q)), 3)


def evaluate(name, family, layouts, seed):
    made = []

    def factory():
        p = FOLLOWERS[name]()
        made.append(p)
        return p

    t0 = time.perf_counter()
    rows, summ, _ = arena.run.evaluate(factory, family, layouts, seed)
    wall = time.perf_counter() - t0
    cat = lambda attr: [v for p in made for v in getattr(p, attr, [])]
    te, tf, st = cat("track_err"), cat("track_err_first"), cat("step_ms")
    for r, p in zip(rows, made):
        r["track_err_median_m"] = pct(p.track_err, 50)
        r["track_err_p95_m"] = pct(p.track_err, 95)
        r["track_err_first_p95_m"] = pct(p.track_err_first, 95)
        for k in ("fail_steps", "slack_steps", "active_steps", "truncated"):
            if hasattr(p, k):
                r[k] = getattr(p, k)
    m = {"summary": summ, "wall_s": round(wall, 1),
         "worst_min_clearance_m": min(r["min_clearance_m"] for r in rows),
         "planner_steps": len(te),
         "track_err_m": {"median": pct(te, 50), "p95": pct(te, 95)},
         "track_err_first_path_m": {"median": pct(tf, 50), "p95": pct(tf, 95)},
         "step_ms": {"median": pct(st, 50), "p95": pct(st, 95), "max": pct(st, 100)},
         "runs": rows}
    if name != "astar_carrot":
        qp, osq, cor, it = cat("qp_ms"), cat("osqp_ms"), cat("corridor_ms"), cat("iters")
        m.update({
            "qp_ms": {"median": pct(qp, 50), "p95": pct(qp, 95), "max": pct(qp, 100)},
            "osqp_solve_ms": {"median": pct(osq, 50), "p95": pct(osq, 95)},
            "corridor_ms": {"median": pct(cor, 50), "p95": pct(cor, 95)},
            "iters": {"median": pct(it, 50), "p95": pct(it, 95)},
            "fail_steps": sum(p.fail_steps for p in made),
            "slack_steps": sum(p.slack_steps for p in made),
            "active_steps": sum(p.active_steps for p in made),
            "truncated_corridors": sum(p.truncated for p in made),
        })
    return m


def plot(path, family, seed, k):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    w = arena.world.make_world(family, seed, k, radius=mpc.RADIUS)
    car = mpc.CarrotTracked(known_map=True)
    rc, _, xyc = arena.run.run_one(car, w, seed, k)
    mp = mpc.AStarMPC(known_map=True, record=True)
    rm, _, xym = arena.run.run_one(mp, w, seed, k)
    # corridor snapshot: the last MPC step at least 0.6 m before the point where the vehicle had its
    # smallest ESDF (the gap), so the 2 s horizon runs into the gap
    esd = [float(mp.esdf[mp._idx(*e["p"])]) for e in mp.log]
    j = int(np.argmin(esd))
    pj = np.array(mp.log[j]["p"])
    before = [i for i in range(j + 1) if np.hypot(*(np.array(mp.log[i]["p"]) - pj)) >= 0.6]
    snap = mp.log[before[-1] if before else j]
    g = w.grid
    ext = [g.x0, g.x0 + g.occ.shape[0] * g.res, g.y0, g.y0 + g.occ.shape[1] * g.res]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2))
    cx, cy = snap["refs"][len(snap["refs"]) // 2]
    for ax, zoom in zip(axes, (False, True)):
        ax.imshow(g.occ.T, origin="lower", extent=ext, cmap="Greys", vmin=0, vmax=1.6)
        for kk in range(0, mpc.N, 1 if zoom else 4):
            poly = mpc.halfplane_polygon(snap["normals"][kk], snap["offsets"][kk], snap["refs"][kk])
            if len(poly) >= 3:
                ax.add_patch(Polygon(poly, closed=True, fill=True, alpha=0.06 if zoom else 0.1,
                                     color="tab:orange", lw=0.6, ec="tab:orange"))
        fp = car.first_path
        ax.plot(fp[:, 0], fp[:, 1], "--", color="tab:green", lw=1.2, label="A* path at t = 0")
        ax.plot(xyc[:, 0], xyc[:, 1], color="tab:blue", lw=1.4,
                label=f"carrot: {rc['outcome']}, min clr {rc['min_clearance_m']} m")
        ax.plot(xym[:, 0], xym[:, 1], color="tab:red", lw=1.4,
                label=f"MPC: {rm['outcome']}, min clr {rm['min_clearance_m']} m")
        if snap["pred"] is not None:
            ax.plot(snap["pred"][:, 0], snap["pred"][:, 1], ".", color="k", ms=3,
                    label=f"MPC prediction at t = {snap['t']:.1f} s")
        ax.plot(snap["refs"][:, 0], snap["refs"][:, 1], "x", color="tab:orange", ms=3, label="reference r_k")
        ax.plot([0], [0], "o", color="tab:green"); ax.plot([w.goal[0]], [w.goal[1]], "o", color="tab:red")
        ax.set_aspect("equal")
        if zoom:
            ax.set_xlim(cx - 1.5, cx + 1.5); ax.set_ylim(cy - 1.5, cy + 1.5)
            ax.set_title("zoom 3 x 3 m at the gap, corridor of all 20 steps")
        else:
            ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
            ax.set_title(f"{family} seed {seed} run {k} (synthetic); corridor every 4th step")
            ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return rc, rm, snap["t"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--families", default="random,narrow_gap")
    ap.add_argument("--followers", default=",".join(FOLLOWERS))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--no-plot", action="store_true")
    a = ap.parse_args(argv)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    os.makedirs(a.out, exist_ok=True)
    import osqp
    import scipy
    consts = {k: v for k, v in vars(mpc).items() if k.isupper() and isinstance(v, (int, float))}
    out = {"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts,
           "mpc_constants": consts, "osqp_settings": mpc.OSQP_SETTINGS,
           "env": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                   "osqp": osqp.__version__, "machine": platform.machine(), "system": platform.system(),
                   "processor": platform.processor()},
           "results": {}}
    t_all = time.perf_counter()
    for fam in a.families.split(","):
        out["results"][fam] = {}
        for name in a.followers.split(","):
            m = evaluate(name, fam, a.layouts, a.seed)
            out["results"][fam][name] = m
            s = m["summary"]
            print(f"{fam} {name}: reached {s['reached_pct']} coll {s['collision_pct']} "
                  f"clr {s['median_min_clearance_m']} te {m['track_err_m']} qp {m.get('qp_ms')} wall {m['wall_s']}",
                  flush=True)
    out["wall_s"] = round(time.perf_counter() - t_all, 1)
    stem = os.path.join(a.out, f"mpc_compare_{a.seed}")
    png = None
    if not a.no_plot and "narrow_gap" in out["results"] and "astar_carrot" in out["results"]["narrow_gap"]:
        runs = out["results"]["narrow_gap"]["astar_carrot"]["runs"]
        k = min(runs, key=lambda r: r["min_clearance_m"])["index"]     # tightest carrot pass
        png = os.path.join(a.out, f"mpc_narrow_gap_{a.seed}_run{k}.png")
        rc, rm, ts = plot(png, "narrow_gap", a.seed, k)
        out["plot"] = {"file": os.path.basename(png), "run": k, "carrot": rc["outcome"], "mpc": rm["outcome"],
                       "corridor_snapshot_t_s": ts, "rule": "narrow_gap run with the smallest carrot min clearance"}
    with open(stem + ".json", "w") as fh:
        json.dump(out, fh, indent=1)
    f = lambda v: "-" if v is None else f"{v}"
    L = [f"`{cmd}` in samples/close-area-planner-mpc (synthetic: simulated layouts, vehicle and sensor), "
         f"wall {out['wall_s']} s, {out['env']['machine']} {out['env']['system']}, Python {out['env']['python']}, "
         f"numpy {out['env']['numpy']}, osqp {out['env']['osqp']}", "",
         "| follower | family | layouts | reached % | collision % | stuck % | timeout % | median min clearance m "
         "| worst min clearance m | tracking err median / p95 m | vs t=0 path median / p95 m | step ms median / p95 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for fam, d in out["results"].items():
        for name, m in d.items():
            s = m["summary"]
            L.append(f"| {name} | {fam} | {s['n']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} | "
                     f"{f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_min_clearance_m'])} | "
                     f"{m['worst_min_clearance_m']} | {m['track_err_m']['median']} / {m['track_err_m']['p95']} | "
                     f"{m['track_err_first_path_m']['median']} / {m['track_err_first_path_m']['p95']} | "
                     f"{m['step_ms']['median']} / {m['step_ms']['p95']} |")
    L += ["", "MPC solver (per planner step; QP = wall time of OSQP update + solve; step = replan + reference "
          "+ corridor + QP):", "",
          "| follower | family | steps | QP ms median / p95 / max | OSQP solve_time ms median / p95 "
          "| corridor ms median / p95 | iterations median / p95 | not solved | slack > 1 cm at k=1 "
          "| steps with an active obstacle plane | truncated corridors |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for fam, d in out["results"].items():
        for name, m in d.items():
            if "qp_ms" not in m:
                continue
            L.append(f"| {name} | {fam} | {m['planner_steps']} | {m['qp_ms']['median']} / {m['qp_ms']['p95']} / "
                     f"{m['qp_ms']['max']} | {m['osqp_solve_ms']['median']} / {m['osqp_solve_ms']['p95']} | "
                     f"{m['corridor_ms']['median']} / {m['corridor_ms']['p95']} | {m['iters']['median']} / "
                     f"{m['iters']['p95']} | {m['fail_steps']} | {m['slack_steps']} | {m['active_steps']} | "
                     f"{m['truncated_corridors']} |")
    for fam, d in out["results"].items():
        names = list(d)
        L += ["", f"Per run, {fam} (outcome, min clearance m):", "",
              "| run | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for i in range(a.layouts):
            L.append(f"| {i} | " + " | ".join(f"{d[n]['runs'][i]['outcome']} {d[n]['runs'][i]['min_clearance_m']}"
                                              for n in names) + " |")
    if png:
        p = out["plot"]
        L += ["", f"Plot: [{p['file']}]({p['file']}), narrow_gap run {p['run']} ({p['rule']}). "
              f"Carrot {p['carrot']}, MPC {p['mpc']}. Orange = MPC corridor polytopes at t = {p['corridor_snapshot_t_s']:.1f} s."]
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {stem}.json, {stem}.md" + (f", {png}" if png else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
