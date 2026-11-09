"""Score a flown A=>B trajectory log (JSONL, see log_format.md) and draw planned vs flown.

python score_log.py <log.jsonl> [--plot out.png] [--json out.json]

Works on a log from the arena, SITL or a real drone: imports only numpy and matplotlib
(matplotlib only when --plot is given). Prints reached, time to goal, min clearance to the
declared obstacles, path length, filter interventions (count and fraction), pilot-mode entries.

Definitions match scorer.py where they overlap (goal 0.3 m, collision = clearance < radius,
stuck = < 0.2 m moved in 10 s, first event in time ends the run):
  reached      a logged position within goal_tol of B (samples only, no interpolation)
  collision    clearance < radius on the straight segments between samples (densified to
               0.05 m), so a 10 Hz log does not skip over a contact
  min clearance  centre to nearest declared surface, on the densified segments, up to the end
  interventions  rising edges of filter_intervened; fraction = share of logged steps with it set
Positions come from the "truth" object (sim truth or mocap) when every step has one, else
from the logged pose, which is the drone's own estimate. The output says which.

Demo writer (needs the arena venv, the only place this file touches the arena):
python score_log.py --write-arena-log results/log_arena.jsonl --family random --seed 0 --index 2
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

FORMAT = "close-area-log/1"
DEFAULTS = {"goal_tol": 0.3, "radius": 0.15, "stuck_window_s": 10.0, "stuck_dist": 0.2}
MANUAL_MODES = {"MANUAL", "POSCTL", "POSITION", "ALTCTL", "STABILIZED", "ACRO", "STABILIZE",
                "ALT_HOLD", "POSHOLD", "RATTITUDE"}
DENSE_STEP = 0.05     # m, segment densification for clearance and collision


# ---- reading ----

def read_log(path: str) -> tuple[dict, list[dict]]:
    header, steps = None, []
    with open(path) as fh:
        lines = [ln.strip() for ln in fh]
    last = max((n for n, ln in enumerate(lines, 1) if ln), default=0)
    for n, line in enumerate(lines, 1):
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            if n > 1 and n == last:                 # torn last line after a crash: keep the rest
                print(f"warning: line {n} is not JSON ({e.msg}), ignored", file=sys.stderr)
                break
            raise SystemExit(f"{path}:{n}: not JSON: {e.msg}")
        if d.get("type") == "header":
            header = d
        else:
            steps.append(d)
    if header is None:
        raise SystemExit(f"{path}: no header line ({{\"type\": \"header\", ...}})")
    if len(steps) < 2:
        raise SystemExit(f"{path}: need at least 2 step lines, got {len(steps)}")
    for k, s in enumerate(steps):
        for f in ("t", "x", "y"):
            if not isinstance(s.get(f), (int, float)):
                raise SystemExit(f"{path}: step {k} has no numeric '{f}'")
    steps.sort(key=lambda s: s["t"])
    return header, steps


# ---- geometry ----

class Obstacles:
    """Signed distance to declared boxes [cx, cy, hx, hy, (yaw)], cylinders [cx, cy, r] and the
    area walls [xmin, ymin, xmax, ymax] (optional). Positive in free space."""

    def __init__(self, world: dict):
        self.area = world.get("area")
        b = [list(x) + [0.0] * (5 - len(x)) for x in world.get("boxes") or []]
        self.boxes = np.array(b, float).reshape(-1, 5)
        self.cyl = np.array(world.get("cylinders") or [], float).reshape(-1, 3)

    @property
    def empty(self) -> bool:
        return self.area is None and not len(self.boxes) and not len(self.cyl)

    def sdf(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p, float).reshape(-1, 2)
        d = np.full(len(p), np.inf)
        if self.area is not None:
            x0, y0, x1, y1 = self.area
            d = np.minimum.reduce([d, p[:, 0] - x0, x1 - p[:, 0], p[:, 1] - y0, y1 - p[:, 1]])
        for cx, cy, hx, hy, yaw in self.boxes:
            c, s = math.cos(yaw), math.sin(yaw)
            dx, dy = p[:, 0] - cx, p[:, 1] - cy
            q = np.abs(np.stack([c * dx + s * dy, -s * dx + c * dy], 1)) - [hx, hy]
            d = np.minimum(d, np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(q.max(1), 0.0))
        if len(self.cyl):
            dc = np.linalg.norm(p[:, None, :] - self.cyl[None, :, :2], axis=2) - self.cyl[None, :, 2]
            d = np.minimum(d, dc.min(1))
        return d


def densify(t: np.ndarray, xy: np.ndarray, step: float = DENSE_STEP):
    """Points every <= step metres along the polyline. Returns (t_d, xy_d, seg_end_index)."""
    ts, ps, idx = [t[:1]], [xy[:1]], [np.array([0])]
    for k in range(1, len(xy)):
        n = max(1, int(math.ceil(float(np.hypot(*(xy[k] - xy[k - 1]))) / step)))
        f = np.arange(1, n + 1) / n
        ps.append(xy[k - 1] + f[:, None] * (xy[k] - xy[k - 1]))
        ts.append(t[k - 1] + f * (t[k] - t[k - 1]))
        idx.append(np.full(n, k))
    return np.concatenate(ts), np.concatenate(ps), np.concatenate(idx)


# ---- scoring ----

def score(header: dict, steps: list[dict]) -> dict:
    cfg = {k: float(header.get(k, v)) for k, v in DEFAULTS.items()}
    B = np.array(header["B"][:2], float)
    t = np.array([s["t"] for s in steps], float)
    t0 = float(header.get("t0", t[0]))
    t = t - t0
    on_truth = all(isinstance(s.get("truth"), dict) for s in steps)
    src = [s["truth"] if on_truth else s for s in steps]
    xy = np.array([[p["x"], p["y"]] for p in src], float)
    pose_xy = np.array([[s["x"], s["y"]] for s in steps], float)

    # first events: reach on samples, collision on the densified path, stuck on samples
    d_goal = np.hypot(*(xy - B).T)
    reach = np.flatnonzero(d_goal <= cfg["goal_tol"])
    i_r = int(reach[0]) if len(reach) else None
    obs = Obstacles(header.get("world") or {})
    td, xyd, segk = densify(t, xy)
    clr_d = obs.sdf(xyd) if not obs.empty else np.full(len(xyd), np.inf)
    coll = np.flatnonzero(clr_d < cfg["radius"])
    i_c = int(segk[coll[0]]) if len(coll) else None
    lag = np.searchsorted(t, t - cfg["stuck_window_s"] + 1e-9)
    disp = np.hypot(*(xy - xy[lag]).T)
    st = np.flatnonzero((t >= cfg["stuck_window_s"] - 1e-9) & (disp < cfg["stuck_dist"]))
    i_s = int(st[0]) if len(st) else None
    cands = [(i, n) for i, n in ((i_r, "reached"), (i_c, "collision"), (i_s, "stuck")) if i is not None]
    end, outcome = min(cands) if cands else (len(t) - 1, "log_ended")

    upto = segk <= end
    if obs.empty:
        min_clr, closest = None, None
    else:
        j = int(np.argmin(np.where(upto, clr_d, np.inf)))
        min_clr, closest = float(clr_d[j]), [float(xyd[j, 0]), float(xyd[j, 1]), float(td[j])]
    seg = np.hypot(*np.diff(xy[: end + 1], axis=0).T)
    flags = np.array([bool(s.get("filter_intervened", False)) for s in steps[: end + 1]])
    rises = int(flags[0]) + int(np.count_nonzero(flags[1:] & ~flags[:-1]))
    modes = [str(s.get("mode", "")).upper() for s in steps[: end + 1]]
    manual = set(m.upper() for m in header.get("manual_modes", MANUAL_MODES))
    entries = sum(1 for k, m in enumerate(modes) if m in manual and (k == 0 or modes[k - 1] not in manual))
    dts = np.diff(t)
    res = {
        "log_input": header.get("input", "unknown"),
        "positions_from": "truth" if on_truth else "pose (onboard estimate)",
        "outcome": outcome,
        "reached": outcome == "reached",
        "time_to_goal_s": round(float(t[end]), 3) if outcome == "reached" else None,
        "duration_s": round(float(t[end]), 3),
        "final_dist_to_B_m": round(float(d_goal[end]), 3),
        "min_clearance_m": None if min_clr is None else round(min_clr, 4),
        "closest_approach_xyt": None if closest is None else [round(v, 3) for v in closest],
        "path_length_m": round(float(seg.sum()), 3),
        "straight_line_m": round(float(np.hypot(*(B - np.array(header.get("A", [0, 0])[:2], float)))), 3),
        "interventions": rises,
        "intervention_fraction": round(float(flags.mean()), 4),
        "manual_mode_entries": entries,
        "steps_scored": int(end + 1),
        "steps_in_log": len(steps),
        "log_rate_hz_median": round(float(1.0 / np.median(dts)), 2) if len(dts) and np.median(dts) > 0 else None,
    }
    if on_truth:
        res["max_pose_error_m"] = round(float(np.hypot(*(pose_xy - xy)[: end + 1].T).max()), 4)
    res["_trace"] = {"xy": xy, "end": end, "obs": obs, "cfg": cfg, "B": B,
                     "A": np.array(header.get("A", [0, 0])[:2], float),
                     "plans": [(k, np.array(s["planned"], float)[:, :2]) for k, s in enumerate(steps)
                               if s.get("planned")]}
    return res


def report(res: dict) -> str:
    f = lambda v, u="": "-" if v is None else f"{v}{u}"
    lines = [
        f"input            {res['log_input']} (positions from {res['positions_from']})",
        f"outcome          {res['outcome']}",
        f"reached          {res['reached']}",
        f"time to goal     {f(res['time_to_goal_s'], ' s')}   (run ends at {res['duration_s']} s, "
        f"{res['final_dist_to_B_m']} m from B)",
        f"min clearance    {f(res['min_clearance_m'], ' m')}   at {res['closest_approach_xyt']} (x, y, t)",
        f"path length      {res['path_length_m']} m   (straight A=>B {res['straight_line_m']} m)",
        f"interventions    {res['interventions']}   fraction {res['intervention_fraction']} of logged steps",
        f"manual modes     {res['manual_mode_entries']} entries",
        f"steps            {res['steps_scored']} scored of {res['steps_in_log']}, median rate {f(res['log_rate_hz_median'], ' Hz')}",
    ]
    if "max_pose_error_m" in res:
        lines.append(f"max pose error   {res['max_pose_error_m']} m (logged pose vs truth)")
    return "\n".join(lines)


# ---- plot ----

def plot(res: dict, path: str, title: str = "") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon, Rectangle

    tr = res["_trace"]
    obs, xy, end, A, B, cfg = tr["obs"], tr["xy"], tr["end"], tr["A"], tr["B"], tr["cfg"]
    fig, ax = plt.subplots(figsize=(7, 7))
    if obs.area is not None:
        x0, y0, x1, y1 = obs.area
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=2, ec="0.2"))
    for cx, cy, hx, hy, yaw in obs.boxes:
        c, s = math.cos(yaw), math.sin(yaw)
        corners = [(cx + c * u - s * v, cy + s * u + c * v) for u, v in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy))]
        ax.add_patch(Polygon(corners, fc="0.35", ec="0.2"))
    for cx, cy, r in obs.cyl:
        ax.add_patch(Circle((cx, cy), r, fc="0.35", ec="0.2"))
    plans = tr["plans"]
    for k, (_, p) in enumerate(plans):
        last = k == len(plans) - 1
        ax.plot(p[:, 0], p[:, 1], "--", color="tab:orange", lw=2 if last else 1, alpha=1 if last else 0.4, zorder=4,
                label=("planned (last)" if last else "planned (earlier)") if k in (0, len(plans) - 1) else None)
    if not plans:
        ax.plot([A[0], B[0]], [A[1], B[1]], ":", color="tab:orange", zorder=4, label="straight A=>B (no plan logged)")
    ax.plot(xy[: end + 1, 0], xy[: end + 1, 1], "-", color="tab:blue", lw=2, label=f"flown ({res['positions_from']})")
    if end < len(xy) - 1:
        ax.plot(xy[end:, 0], xy[end:, 1], "-", color="tab:blue", lw=1, alpha=0.3, label="after end event")
    ax.add_patch(Circle(tuple(A), cfg["goal_tol"], fc="tab:green", alpha=0.6))
    ax.add_patch(Circle(tuple(B), cfg["goal_tol"], fc="tab:red", alpha=0.6))
    ax.annotate("A", A, xytext=(6, 6), textcoords="offset points", weight="bold")
    ax.annotate("B", B, xytext=(6, 6), textcoords="offset points", weight="bold")
    if res["closest_approach_xyt"] is not None:
        cx, cy, ct = res["closest_approach_xyt"]
        ax.add_patch(Circle((cx, cy), res["min_clearance_m"], fill=False, ec="magenta", lw=1.5))
        ax.plot([cx], [cy], "x", color="magenta", ms=10, mew=2,
                label=f"closest approach {res['min_clearance_m']:.2f} m at t={ct:.1f} s")
    ax.plot([xy[end, 0]], [xy[end, 1]], "o", mfc="none", mec="k", ms=9, label=f"end: {res['outcome']}")
    tg = "-" if res["time_to_goal_s"] is None else f"{res['time_to_goal_s']} s"
    import textwrap
    ax.set_title(("\n".join(textwrap.wrap(title, 90)) + "\n" if title else "") +
                 f"{res['outcome']} | time {tg} | min clr {res['min_clearance_m']} m | "
                 f"path {res['path_length_m']} m | interv {res['interventions']} "
                 f"({100 * res['intervention_fraction']:.0f} %)", fontsize=9)
    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_xlabel("x east, m (origin A)")
    ax.set_ylabel("y north, m")
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


# ---- demo writer: one arena run => JSONL (arena imports stay inside this function) ----

def write_arena_log(path: str, family: str, seed: int, index: int, planner: str = "straight") -> dict:
    """Fly one arena layout like run.run_one, logging every planner step plus the end tick.
    filter_intervened marks steps where the straight planner's obstacle slow-down cut the
    commanded speed below 99 % of its nominal speed (the arena has no safety filter yet).
    Returns the arena's own 50 Hz scorer row for the same run, as a cross-check."""
    import importlib
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "close_area_arena", os.path.join(here, "__init__.py"), submodule_search_locations=[here])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["close_area_arena"] = pkg
    spec.loader.exec_module(pkg)
    run = importlib.import_module("close_area_arena.run")
    world_mod = importlib.import_module("close_area_arena.world")
    scorer = importlib.import_module("close_area_arena.scorer")
    from close_area_arena.adapter import SimAdapter
    from close_area_arena.sensors import RangeFan
    from close_area_arena.vehicle import HZ, Vehicle

    cfg = run.DEFAULTS
    w = world_mod.make_world(family, seed, index, radius=cfg["vehicle"]["radius"])
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    veh = Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **cfg["vehicle"])
    sensor = RangeFan(rng=np.random.default_rng([seed, index, 7]), **cfg["sensor"])
    ad = SimAdapter(w, veh, sensor)
    pl = run.load_planner(planner)
    pl.reset()
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    grid = w.grid if getattr(pl, "uses_grid", False) else None
    r4 = lambda v: None if v is None else round(float(v), 4)
    wd = w.to_dict()
    header = {"type": "header", "format": FORMAT, "input": "synthetic",
              "source": f"close-area-arena {family} seed {seed} index {index}, planner {planner}, "
                        f"logged at {cfg['plan_hz']} Hz by score_log.py --write-arena-log",
              "frame": "local ENU, metres, origin at A", "A": [0.0, 0.0], "B": [r4(goal[0]), r4(goal[1])],
              "goal_tol": scorer.GOAL_TOL, "radius": cfg["vehicle"]["radius"],
              "world": {"area": wd["area"], "boxes": wd["boxes"], "cylinders": wd["cylinders"]},
              "notes": "filter_intervened = straight planner slow-down active (speed < 99 % nominal)"}

    def line(pose, sp, flag, planned=None):
        d = {k: r4(v) if isinstance(v, float) else v for k, v in vars(pose).items()}
        tr = ad.truth()
        d.update(sp={"vx": r4(sp.vx), "vy": r4(sp.vy), "vz": r4(sp.vz), "yaw_rate": r4(sp.yaw_rate)},
                 filter_intervened=bool(flag), mode="OFFBOARD",
                 truth={"x": r4(tr.x), "y": r4(tr.y), "z": r4(tr.z)})
        if planned is not None:
            d["planned"] = planned
        return json.dumps(d)

    xy = [(0.0, 0.0)]
    sp, flag, last_plan = None, False, None
    with open(path, "w") as fh:
        fh.write(json.dumps(header) + "\n")
        for k in range(int(round(cfg["max_time_s"] * HZ))):
            if k % ratio == 0:
                pose = ad.pose()
                sp = pl.step(pose, ad.ranges(), goal, grid, pdt)
                ad.send_setpoint(sp)
                plan = getattr(pl, "path", None)
                plan = [[0.0, 0.0], [r4(goal[0]), r4(goal[1])]] if plan is None else [[r4(p[0]), r4(p[1])] for p in plan]
                nominal = min(getattr(pl, "cruise", math.inf), getattr(pl, "k_goal", 1.0) *
                              math.hypot(goal[0] - pose.x, goal[1] - pose.y))
                flag = math.hypot(sp.vx, sp.vy) < 0.99 * nominal if math.isfinite(nominal) else False
                fh.write(line(pose, sp, flag, plan if plan != last_plan else None) + "\n")
                last_plan = plan
            ad.tick()
            px, py = float(veh.p[0]), float(veh.p[1])
            xy.append((px, py))
            stop = (math.hypot(px - goal[0], py - goal[1]) <= scorer.GOAL_TOL or w.clearance(px, py) < veh.radius
                    or (len(xy) > lag and math.hypot(px - xy[-1 - lag][0], py - xy[-1 - lag][1]) < scorer.STUCK_DIST))
            if stop:
                break
        fh.write(line(ad.pose(), sp, flag) + "\n")           # end tick, so a 10 Hz log sees the event
    ref, _, _ = run.run_one(run.load_planner(planner), w, seed, index)
    return {k: ref[k] for k in scorer.FIELDS}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", nargs="?", help="JSONL log (log_format.md)")
    ap.add_argument("--plot", help="write planned-vs-flown PNG here (needs matplotlib)")
    ap.add_argument("--json", help="write the metrics as JSON here")
    ap.add_argument("--title", default="")
    ap.add_argument("--write-arena-log", metavar="OUT", help="demo: fly one arena layout and write its log")
    ap.add_argument("--family", default="random")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--planner", default="straight")
    a = ap.parse_args(argv)
    if a.write_arena_log:
        ref = write_arena_log(a.write_arena_log, a.family, a.seed, a.index, a.planner)
        print(f"wrote {a.write_arena_log}\narena scorer.py on the 50 Hz truth trace: {json.dumps(ref)}")
        return 0
    if not a.log:
        ap.error("give a log file or --write-arena-log")
    header, steps = read_log(a.log)
    res = score(header, steps)
    print(report(res))
    out = {k: v for k, v in res.items() if not k.startswith("_")}
    out["log"] = a.log
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1)
        print(f"wrote {a.json}")
    if a.plot:
        plot(res, a.plot, a.title or header.get("source", os.path.basename(a.log)))
        print(f"wrote {a.plot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
