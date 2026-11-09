"""Relocalization against an imperfect prior map: the README headline assumed the map is exact.

.venv/bin/python run_stalemap.py --layouts 100 --seed 2          # random family, dropout and jump

Map-error ladder (map_perturb.py): a_exact, b_removed (1-2 mapped obstacles gone), c_added (1-2
unmapped obstacles near the path), d_shift01 / d_shift02 (every obstacle moved 0.1 / 0.2 m),
e_selfmap (map = log-odds grid the unknown-map A* built on an outbound A => B leg on the VIO-like
estimator, no fault; the fault hits on the return leg B => A).

Arms (A* known-map planner on the map, scored on the real geometry):
  truth     planner sees the true pose (reference: what the map error alone costs)
  single    (b) commit to the best match at once + innovation test (experiment.py arm, unchanged)
  multi     (c) RatioPersistence, hover until accept (experiment.py arm, unchanged)
  multi_ig  (f) (c) + after 1 s the info-gain move (disambiguate.py "infogain", unchanged)
Relocalizer and move check use the map, the range scan comes from the real world.

Collision kinds (per collided run, at the collision sample):
  unmapped  the map's ESDF at the collision point is > UNMAPPED_M (the map said there was room)
  in_move   a disambiguating move was being flown in the last MOVE_WINDOW_S before the collision
Writes results/stalemap_<family>_<seed>.json / .md.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy

from arena import astar_esdf, estimator, run, world
import disambiguate as D
import experiment as X
import map_perturb as P
import relocalize as R
import run_disambiguate as RD

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("truth", "single", "multi", "multi_ig")
LABEL = {"truth": "truth", "single": "(b) single", "multi": "(c) multi", "multi_ig": "(f) multi_ig"}
FAULTS = ("dropout", "jump")
UNMAPPED_M = 0.20            # m, map ESDF above which a collision point counts as unmapped
MOVE_WINDOW_S = 0.2          # s, a move flown this close before the collision end counts as in_move
OUT_NEAR_B_M = 1.0           # m, outbound leg used for e_selfmap if it reached B or got stuck this close


class MoveGate(RD.DisambGate):
    """DisambGate that records the last time it flew a disambiguating move."""

    def __init__(self, inner, src):
        super().__init__(inner, src)
        self.last_move_t = None

    def step(self, pose, scan, goal, grid, dt):
        if pose.quality == 0 and self.src.cmd is not None:
            self.last_move_t = pose.t
        return super().step(pose, scan, goal, grid, dt)


# ---- e_selfmap outbound leg ----
def outbound(args):
    """Fly A => B with the unknown-map A* on the estimator (fault none, dark zones). Returns the map."""
    seed, index = args
    base = world.make_world("random", seed, index)
    est = estimator.make_pose_source_factory("none", dark=True)(base, seed, index)
    log = []

    def src(truth):
        p = est(truth)
        log.append((truth.x, truth.y, p.x - truth.x, p.y - truth.y))
        return p

    pl = astar_esdf.make(known_map=False)
    row, _, xy = run.run_one(pl, base, seed, index, run.DEFAULTS, src)
    occ, unk = P.selfmap_layers(pl.map.lo)
    end = [float(xy[-1, 0]), float(xy[-1, 1])]
    d_b = math.hypot(end[0] - base.goal[0], end[1] - base.goal[1])
    ok = row["outcome"] == "reached" or (row["outcome"] == "stuck" and d_b <= OUT_NEAR_B_M)
    return index, {"occ": np.packbits(occ), "unk": np.packbits(unk), "shape": occ.shape, "end": end,
                   "off": np.array(log, np.float32), "d0": [float(log[-1][2]), float(log[-1][3])],
                   "outcome": row["outcome"], "end_to_b_m": round(d_b, 3), "used": bool(ok),
                   "est_err_end_m": round(float(est.errs[-1]), 4), "est_err_max_m": round(float(max(est.errs)), 4)}


def prepare(rung, seed, index, ob):
    """(real world with .grid = planner map, relocalizer map, info) or None when the rung is skipped."""
    base = world.make_world("random", seed, index)
    if rung != "e_selfmap":
        real, info = P.perturb(base, rung, seed, index)
        return real, real.grid, info, None
    if ob is None or not ob["used"]:
        return None
    n = int(np.prod(ob["shape"]))
    occ = np.unpackbits(ob["occ"])[:n].reshape(ob["shape"]).astype(bool)
    unk = np.unpackbits(ob["unk"])[:n].reshape(ob["shape"]).astype(bool)
    ox, oy = ob["end"]
    real = P.shift_world(base, ox, oy, (0.0, 0.0))           # return leg: start where outbound ended, goal A
    match, plan = P.selfmap_grids(occ, unk, ox, oy)
    real.grid = plan
    info = {"rung": rung, "outbound_outcome": ob["outcome"], "outbound_end_to_b_m": ob["end_to_b_m"],
            "outbound_est_err_end_m": ob["est_err_end_m"], "outbound_est_err_max_m": ob["est_err_max_m"],
            "d0": [round(v, 4) for v in ob["d0"]]}
    info.update(P.selfmap_stats(match, real))
    off = ob["off"].astype(float) - np.array([ox, oy, 0.0, 0.0])   # (x, y, est - truth) in the return frame
    return real, match, info, off


class Offset:
    """Return-leg pose source: the estimator plus the outbound leg's final error d0, so the drone starts
    the return leg in the frame its self-built map is in (it keeps believing where it was)."""

    def __init__(self, est, d0):
        self.est, self.d0 = est, d0

    def __call__(self, truth):
        p = self.est(truth)
        return dataclasses.replace(p, x=p.x + self.d0[0], y=p.y + self.d0[1])


class Trace:
    """Outermost pose source: records truth (t, x, y) at every planner step."""

    def __init__(self, src):
        self.src, self.trace = src, []

    def __call__(self, truth):
        self.trace.append((truth.t, truth.x, truth.y))
        return self.src(truth)


def map_frame_errors(row, trace, off):
    """err_map_m per accepted event: |accepted - (truth + local map offset)|. The local offset is the
    outbound estimator error at the outbound sample nearest the current truth (e_selfmap), else 0.
    The self-built map was drawn at the outbound estimate, so a correct match lands there."""
    if not trace:
        return
    tr = np.array(trace)
    for e in row.get("events", []):
        if e["result"] != "accepted":
            continue
        k = int(np.argmin(np.abs(tr[:, 0] - e["t_end"])))
        p = tr[k, 1:3]
        d = np.zeros(2) if off is None else off[int(np.argmin(np.hypot(off[:, 0] - p[0], off[:, 1] - p[1]))), 2:4]
        e["err_map_m"] = round(float(np.hypot(*(np.array(e["accepted_xy"]) - p - d))), 4)


def build(arm, w, est, rgrid, seed, index):
    scan = X.scan_fn_for(w, seed, index)
    if arm == "multi_ig":
        src = D.DisambPoseSource(est, rgrid, scan, "infogain", rng=np.random.default_rng([seed, index, 4501]),
                                 goal=w.goal)
        return src, MoveGate(astar_esdf.make(known_map=True), src)
    return R.RelocPoseSource(est, rgrid, scan, mode=arm, innovation=True), X.HoverGate(astar_esdf.make(known_map=True))


def classify(row, xy, rgrid, planner):
    if row["outcome"] != "collision":
        return {"collision_kind": None}
    p = xy[-1]
    e = rgrid.esdf()
    ix, iy = rgrid.to_index(float(p[0]), float(p[1]))
    inside = 0 <= ix < e.shape[0] and 0 <= iy < e.shape[1]
    map_esdf = float(e[ix, iy]) if inside else 0.0
    lm = getattr(planner, "last_move_t", None)
    in_move = lm is not None and lm >= row["duration_s"] - MOVE_WINDOW_S - 1e-9
    return {"collision_kind": ("move_" if in_move else "") + ("unmapped" if map_esdf > UNMAPPED_M else "mapped"),
            "collision_map_esdf_m": round(map_esdf, 3), "collision_xy": [round(float(p[0]), 3), round(float(p[1]), 3)],
            "last_move_t": lm}


def run_cell(args):
    fault, arm, rung, layouts, seed, obs = args
    rows, t0 = [], time.perf_counter()
    for i in range(layouts):
        prep = prepare(rung, seed, i, obs.get(i) if obs else None)
        if prep is None:
            continue
        w, rgrid, info, off = prep
        tr = None
        if arm == "truth":
            est = src = None
            planner = astar_esdf.make(known_map=True)
        else:
            est = estimator.make_pose_source_factory(fault, dark=True, sink=[])(w, seed, i)
            inner = est if off is None else Offset(est, info["d0"])
            src, planner = build(arm, w, inner, rgrid, seed, i)
            tr = Trace(src)
        row, _, xy = run.run_one(planner, w, seed, i, run.DEFAULTS, tr)
        if est is not None:
            row.update(RD.extra(row, est, src, est.fault))
            map_frame_errors(row, tr.trace, off)
            row["wrong_commits_map"] = sum(1 for e in row["events"] if (e.get("err_map_m") or 0) > X.WRONG_M)
        row["rung_info"] = info
        row.update(classify(row, xy, rgrid, planner))
        rows.append(row)
    return fault, arm, rung, rows, round(time.perf_counter() - t0, 1)


def summarize(rows):
    s = RD.summarize(rows)
    kinds = [r.get("collision_kind") for r in rows]
    s["collisions"] = {k: kinds.count(k) for k in ("mapped", "unmapped", "move_mapped", "move_unmapped")}
    s["collision_n"] = sum(1 for r in rows if r["collision"])
    s["wrong_commits_map"] = sum(r.get("wrong_commits_map", 0) for r in rows)
    s["runs_with_wrong_commit_map"] = sum(1 for r in rows if r.get("wrong_commits_map"))
    rec = [e["recover_s"] for r in rows for e in r.get("events", []) if e["result"] == "accepted"]
    s["recover_s_accepted"] = ({"median": round(float(np.median(rec)), 2), "p95": round(float(np.percentile(rec, 95)), 2),
                                "max": round(float(max(rec)), 2)} if rec else None)
    return s


def f(v):
    return "-" if v is None else f"{v}"


HEAD = ("| rung | fault | arm | runs | reached % | collision % | of which: move into unmapped / other unmapped / mapped "
        "| stuck % | relocs accepted | wrong commits (> 0.5 m) truth / map frame | runs with a wrong commit (map frame) "
        "| still hovering at end | recover s median / p95 / max | moves flown |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(rung, fault, arm, s):
    c = s["collisions"]
    rel = arm != "truth"
    r = s["recover_s_accepted"]
    return (f"| {rung} | {fault if rel else 'none'} | {LABEL[arm]} | {s['n']} | {s['reached_pct']} | {s['collision_pct']} "
            f"| {c['move_unmapped']} / {c['unmapped']} / {c['mapped'] + c['move_mapped']} | {s['stuck_pct']} "
            f"| {s['accepted'] if rel else '-'} | {(str(s['wrong_commits']) + ' / ' + str(s['wrong_commits_map'])) if rel else '-'} "
            f"| {s['runs_with_wrong_commit_map'] if rel else '-'} | {s['open_at_end'] if rel else '-'} "
            f"| {(str(r['median']) + ' / ' + str(r['p95']) + ' / ' + str(r['max'])) if (rel and r) else '-'} "
            f"| {s['moves_total'] if arm == 'multi_ig' else '-'} |")


def rung_table(res, obs):
    out = ["| rung | layouts flown | obstacles removed / added (total) | median changed map cells | other |",
           "|---|---|---|---|---|"]
    for rung, rows in res.items():
        info = [r["rung_info"] for r in rows]
        rem = sum(len(i.get("removed", [])) for i in info)
        add = sum(len(i.get("added", [])) for i in info)
        cc = [i["changed_cells"] for i in info if "changed_cells" in i]
        other = "-"
        if rung == "e_selfmap" and obs:
            o = list(obs.values())
            outc = {k: sum(1 for x in o if x["outcome"] == k) for k in ("reached", "collision", "stuck", "timeout")}
            used = [x for x in o if x["used"]]
            pf = [i["phantom_frac"] for i in info if i.get("phantom_frac") is not None]
            other = (f"outbound {outc}; used {len(used)} of {len(o)}; outbound end est err median "
                     f"{np.median([x['est_err_end_m'] for x in used]):.3f} m, run max median "
                     f"{np.median([x['est_err_max_m'] for x in used]):.3f} m; map occupied cells >0.2 m from a real "
                     f"surface: median {np.median(pf):.3f} of cells")
        elif rung.startswith("d_"):
            other = f"resampled for a free path: {sum(1 for i in info if i.get('tries', 1) > 1)} layouts"
        out.append(f"| {rung} | {len(rows)} | {rem} / {add} | {f(int(np.median(cc)) if cc else None)} | {other} |")
    return "\n".join(out)


def collision_report(path):
    """Per collided run of a relocalizing arm, from a written stalemap JSON. Writes <stem>_collisions.md."""
    with open(path) as fh:
        d = json.load(fh)
    out = [f"From `{os.path.basename(path)}` (synthetic). One row per collided run of a relocalizing arm. "
           "`map ESDF` = clearance the map claimed at the collision point; `last move t` = last planner step "
           "that flew a disambiguating move; `to added` = distance from the collision point to the nearest "
           "added (unmapped) obstacle surface, c_added only.\n",
           "| rung | fault | arm | layout | kind | map ESDF m | collision t s | last move t s | moves in run "
           "| wrong commits in run (map frame) | to added m |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for rung, by_f in d["results"].items():
        for fl, by_a in by_f.items():
            for arm, cell in by_a.items():
                if arm == "truth":
                    continue
                for r in cell["runs"]:
                    if r["outcome"] != "collision":
                        continue
                    added = r["rung_info"].get("added") or []
                    to_add = (min(float(P.shape_dist((k, tuple(s)), [r["collision_xy"]])[0]) for k, s in added)
                              if added else None)
                    nm = sum(1 for e in r.get("events", []) for m in e.get("moves", []) if m.get("move") is not None)
                    out.append(f"| {rung} | {fl} | {LABEL[arm]} | {r['index']} | {r['collision_kind']} "
                               f"| {r['collision_map_esdf_m']} | {r['duration_s']} | {f(r.get('last_move_t'))} | {nm} "
                               f"| {r.get('wrong_commits_map', 0)} | {f(None if to_add is None else round(to_add, 3))} |")
    stem = os.path.splitext(path)[0]
    with open(stem + "_collisions.md", "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"wrote {os.path.basename(stem)}_collisions.md")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", metavar="JSON", help="only write the per-collision table from a stalemap JSON")
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--rungs", default=",".join(P.RUNGS))
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    if a.report:
        return collision_report(a.report)
    rungs = [x for x in a.rungs.split(",") if x]
    arms = [x for x in a.arms.split(",") if x]
    cmd = "python run_stalemap.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t0 = time.perf_counter()
    obs = {}
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        if "e_selfmap" in rungs:
            obs = dict(ex.map(outbound, [(a.seed, i) for i in range(a.layouts)]))
            print(f"outbound legs done {time.perf_counter() - t0:.1f} s", flush=True)
        cells = [(fl, arm, rung, a.layouts, a.seed, obs if rung == "e_selfmap" else None)
                 for rung in rungs for arm in arms for fl in FAULTS if not (arm == "truth" and fl != FAULTS[0])]
        out = list(ex.map(run_cell, cells))
    wall = time.perf_counter() - t0
    res, by_rung = {}, {}
    for fl, arm, rung, rows, cw in out:
        res.setdefault(rung, {}).setdefault(fl, {})[arm] = {"summary": summarize(rows), "cell_wall_s": cw, "runs": rows}
        if arm == arms[0] and fl == FAULTS[0]:
            by_rung[rung] = rows
    lines = [HEAD]
    for rung in rungs:
        if "truth" in arms:
            lines.append(line(rung, "none", "truth", res[rung][FAULTS[0]]["truth"]["summary"]))
        for fl in FAULTS:
            for arm in arms:
                if arm != "truth":
                    lines.append(line(rung, fl, arm, res[rung][fl][arm]["summary"]))
    tab = "\n".join(lines)
    rt = rung_table(by_rung, obs)
    print(rt + "\n\n" + tab)
    print(f"\nwall {wall:.1f} s")
    os.makedirs(a.out, exist_ok=True)
    stem = f"stalemap_random_{a.seed}"
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    params = {"UNMAPPED_M": UNMAPPED_M, "MOVE_WINDOW_S": MOVE_WINDOW_S, "OUT_NEAR_B_M": OUT_NEAR_B_M,
              "REMOVE_NEAR_M": P.REMOVE_NEAR_M, "ADD_GAP_M": P.ADD_GAP_M, "ADD_END_KEEP_M": P.ADD_END_KEEP_M}
    params.update({k: getattr(R, k) for k in ("S_MIN", "RATIO", "N_SCANS", "W0_M", "SEP_M", "K_MAX", "S_INNOV")})
    params.update({k: getattr(D, k) for k in ("HOVER_TIMEOUT_S", "MAX_MOVES", "CLEAR_M", "MOVE_DISTS_M")})
    outbound_log = {i: {k: v for k, v in o.items() if k not in ("occ", "unk", "shape", "off")} for i, o in obs.items()}
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "family": "random", "seed": a.seed, "wall_s": round(wall, 1),
                   "workers": a.workers, "params": params, "config": run.DEFAULTS, "env": env,
                   "outbound": outbound_log, "results": res}, fh, indent=None, separators=(",", ":"))
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s, {a.workers} workers, "
                 f"{env['machine']} CPython {env['python']} numpy {env['numpy']} scipy {env['scipy']}\n\n"
                 f"{rt}\n\n{tab}\n")
    print(f"wrote {stem}.json / .md")
    collision_report(os.path.join(a.out, stem + ".json"))


if __name__ == "__main__":
    main()
