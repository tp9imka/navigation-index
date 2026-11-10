"""Fly the flight loop in the hub's close-area-arena world (synthetic, sim only).

    ad = ArenaAdapter.from_spec("arena:random:0", arena_dir, fault="jump")
    with open("runs/first_flight.jsonl", "w") as fh:
        log = CloseAreaLog(fh, ad, planner, input="synthetic", source="...")
        run(ad, planner, safety, ad.goal, grid=ad.grid, log=log, timeout_s=60.0)

- `ArenaAdapter` wraps the arena's `SimAdapter` (CONTRACT.md "Adapter"). Lockstep: each
  `send_setpoint()` advances the 50 Hz physics to the next 20 Hz loop tick. 0.05 s is 2.5
  physics steps, so ticks alternate 2 and 3 steps (pose.t = 0.04, 0.10, 0.14, 0.20, ...).
- `fault=None` => the planner sees truth. `fault="none" | "jump" | "bias" | "dropout" |
  "overconfident"` => the arena's `estimator.make_pose_source_factory(fault, dark=True)`: a VIO-like
  EKF with 2 seeded dark zones, which sets quality, reset_counter and sigma_xy.
- Range scans always come from the true pose (arena rule). Touching an obstacle (truth clearance
  under the radius) freezes the vehicle, like a crash; the scorer ends the run there anyway.
- `CloseAreaLog` is a `log=` sink for `loop.run()`: it turns each loop JSONL line into one
  `close-area-log/1` step (samples/close-area-arena/log_format.md) with `truth` and `planned`
  added, so `score_log.py` scores the loop's own log on truth.

Stdlib at import time. numpy / scipy load only when an arena is built (arena venv).
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import math
import os
import sys

try:
    from .adapter import Pose, RangeScan, Setpoint
except ImportError:
    from adapter import Pose, RangeScan, Setpoint

LOOP_DT_S = 0.05      # flight loop period (loop.DT_S)
Z0_M = 1.0            # arena flight height (run.DEFAULTS["z0"])


def load_arena(arena_dir: str):
    """Load samples/close-area-arena as package close_area_arena (CONTRACT.md "Import")."""
    if "close_area_arena" in sys.modules:
        return sys.modules["close_area_arena"]
    arena_dir = os.path.abspath(arena_dir)
    init = os.path.join(arena_dir, "__init__.py")
    if not os.path.exists(init):
        raise FileNotFoundError(f"arena not found at {arena_dir}: pass --arena or set ARENA_DIR")
    spec = importlib.util.spec_from_file_location(
        "close_area_arena", init, submodule_search_locations=[arena_dir])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["close_area_arena"] = pkg
    spec.loader.exec_module(pkg)
    return pkg


def parse_spec(spec: str) -> tuple[str, int, int]:
    """'arena:<family>:<seed>[:<index>]' => (family, seed, index). Index defaults to 0."""
    parts = spec.split(":")
    if parts[0] != "arena" or not 2 <= len(parts) <= 4:
        raise ValueError(f"adapter spec {spec!r}: want arena:<family>:<seed>[:<index>]")
    family = parts[1] if len(parts) > 1 else "random"
    seed = int(parts[2]) if len(parts) > 2 else 0
    index = int(parts[3]) if len(parts) > 3 else 0
    return family, seed, index


def parse_world_spec(spec: str) -> tuple[str, int]:
    """'world:<file.json>[:<seed>]' => (path, run seed). Seed defaults to 0 (the playground's)."""
    if not spec.startswith("world:") or len(spec) <= len("world:"):
        raise ValueError(f"adapter spec {spec!r}: want world:<file.json>[:<seed>]")
    rest = spec[len("world:"):]
    head, sep, tail = rest.rpartition(":")
    if sep and tail.isdigit():
        return head, int(tail)
    return rest, 0


def _pose(p) -> Pose:
    return Pose(t=p.t, x=p.x, y=p.y, z=p.z, vx=p.vx, vy=p.vy, vz=p.vz, yaw=p.yaw,
                quality=p.quality, reset_counter=p.reset_counter, sigma_xy=p.sigma_xy)


class ArenaAdapter:
    """flightloop Adapter over one arena layout. Same world, sensor seed and start yaw as
    the arena's run.run_one, so a layout here is the layout in the arena's results tables."""

    def __init__(self, arena_dir: str, family: str = "random", seed: int = 0, index: int = 0,
                 fault: str | None = None, dt: float = LOOP_DT_S, world=None) -> None:
        """world=None => world.make_world(family, seed, index). A given World (e.g. from a
        close-area-world/1 file) is used as is; seed and index then only seed the sensor noise
        and the estimator, as in the playground driver (worker.js simulate)."""
        load_arena(arena_dir)
        import numpy as np
        run = importlib.import_module("close_area_arena.run")
        world_mod = importlib.import_module("close_area_arena.world")
        sim = importlib.import_module("close_area_arena.adapter")
        sensors = importlib.import_module("close_area_arena.sensors")
        vehicle = importlib.import_module("close_area_arena.vehicle")
        cfg = run.DEFAULTS
        self.family, self.seed, self.index, self.fault = family, seed, index, fault
        self.world = world if world is not None else world_mod.make_world(
            family, seed, index, radius=cfg["vehicle"]["radius"])
        self.goal = (float(self.world.goal[0]), float(self.world.goal[1]), cfg["z0"])
        self.radius = cfg["vehicle"]["radius"]
        self.grid = self.world.grid
        self.vehicle = vehicle.Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(self.goal[1], self.goal[0]),
                                       **cfg["vehicle"])
        sensor = sensors.RangeFan(rng=np.random.default_rng([seed, index, 7]), **cfg["sensor"])
        self.estimator = None
        if fault is not None:
            est_mod = importlib.import_module("close_area_arena.estimator")
            self.estimator = est_mod.make_pose_source_factory(fault, dark=True)(self.world, seed, index)
        self.sim = sim.SimAdapter(self.world, self.vehicle, sensor, pose_source=self.estimator)
        self._SimSetpoint = sim.Setpoint
        self.hz = vehicle.HZ
        self.dt = dt
        self._t_next = 0.0
        self.collided = False
        self.min_clearance = math.inf
        self.max_pose_error = 0.0
        self.last_truth = None          # truth at the last pose() call, for the log
        self.last_pose = None

    @classmethod
    def from_spec(cls, spec: str, arena_dir: str, fault: str | None = None) -> "ArenaAdapter":
        if spec.startswith("world:"):
            path, seed = parse_world_spec(spec)
            return cls.from_world_json(path, arena_dir, fault=fault, seed=seed)
        family, seed, index = parse_spec(spec)
        return cls(arena_dir, family, seed, index, fault)

    @classmethod
    def from_world_json(cls, path: str, arena_dir: str, fault: str | None = None,
                        seed: int = 0) -> "ArenaAdapter":
        """World from a close-area-world/1 file (samples/close-area-arena/world_json.py).
        seed = run seed (sensor noise [seed, index, 7], estimator), as the playground's cfg.seed;
        index = the file's "index" (0 if missing), family = its "family"."""
        load_arena(arena_dir)
        wj = importlib.import_module("close_area_arena.world_json")
        with open(path) as fh:
            doc = json.load(fh)
        world = wj.from_json(doc)
        idx = doc.get("index")
        index = idx if isinstance(idx, int) and not isinstance(idx, bool) else 0
        ad = cls(arena_dir, str(doc.get("family", "custom")), seed, index, fault, world=world)
        ad.world_file = path
        z = doc.get("z")
        if isinstance(z, (int, float)) and abs(float(z) - Z0_M) > 1e-9:
            print(f"note: {path} z={z} m; the arena flies at {Z0_M} m (run.DEFAULTS z0)", file=sys.stderr)
        return ad

    # ---- Adapter ----
    def pose(self) -> Pose:
        self.last_truth = _pose(self.sim.truth())
        self.last_pose = _pose(self.sim.pose())
        self.max_pose_error = max(self.max_pose_error, math.hypot(
            self.last_pose.x - self.last_truth.x, self.last_pose.y - self.last_truth.y))
        return self.last_pose

    def ranges(self) -> RangeScan:
        s = self.sim.ranges()
        return RangeScan(t=float(s.t), angles=[float(a) for a in s.angles],
                         distances=[float(d) for d in s.distances], max_range=float(s.max_range))

    def send_setpoint(self, sp: Setpoint) -> None:
        """Hold sp until the next 20 Hz tick, then return (lockstep)."""
        if self.collided:                                # crashed: clock runs, vehicle does not
            sp = Setpoint(0.0, 0.0, 0.0, 0.0)
        self.sim.send_setpoint(self._SimSetpoint(float(sp.vx), float(sp.vy), float(sp.vz),
                                                 float(sp.yaw_rate)))
        self._t_next += self.dt
        while self.vehicle.t < self._t_next - 0.5 / self.hz:
            self.sim.tick()
            if self.collided:
                continue
            c = float(self.world.clearance(float(self.vehicle.p[0]), float(self.vehicle.p[1])))
            self.min_clearance = min(self.min_clearance, c)
            if c < self.radius:
                self.collided = True
                self.vehicle.v[:] = 0.0
                self.sim.send_setpoint(self._SimSetpoint(0.0, 0.0, 0.0, 0.0))

    # ---- sim only ----
    def header(self, **extra) -> dict:
        """close-area-log/1 header for this layout (log_format.md)."""
        wd = self.world.to_dict()
        h = {"type": "header", "format": "close-area-log/1", "input": "synthetic",
             "frame": "local ENU, metres, origin at A", "A": [0.0, 0.0],
             "B": [round(self.goal[0], 4), round(self.goal[1], 4)], "goal_tol": 0.3,
             "radius": self.radius,
             "world": {"area": wd["area"], "boxes": wd["boxes"], "cylinders": wd["cylinders"]}}
        h.update(extra)
        return h


def _planned(planner):
    """Current planned path as [[x, y], ...], or None. astar_esdf keeps it in path_xy."""
    p = getattr(planner, "path_xy", None)
    if p is None:
        p = getattr(planner, "path", None)
    if p is None:
        return None
    try:
        return [[round(float(q[0]), 4), round(float(q[1]), 4)] for q in list(p)]
    except (TypeError, IndexError, ValueError):
        return None


class CloseAreaLog:
    """File-like sink for loop.run(log=...): each loop line => one close-area-log/1 step.

    Keeps the loop's own fields as extras (`loop_mode`, `health`, `source`, `reasons`,
    `plan_ms`); `mode` is "OFFBOARD" (the loop never hands control to a pilot). `truth` is the
    sim truth at the same pose() call, so score_log.py scores on truth."""

    def __init__(self, fh, adapter: ArenaAdapter, planner=None, **header_extra) -> None:
        self.fh, self.ad, self.planner = fh, adapter, planner
        self._last_plan = None
        self.lines = 0
        self.fh.write(json.dumps(adapter.header(**header_extra)) + "\n")

    def write(self, s: str) -> int:
        for line in s.splitlines():
            if line.strip():
                self._step(json.loads(line))
        return len(s)

    def flush(self) -> None:
        self.fh.flush()

    def _step(self, d: dict) -> None:
        p = d["pose"]
        lp, tr = self.ad.last_pose, self.ad.last_truth
        out = {"t": d["t"], "x": p["x"], "y": p["y"], "z": p["z"], "vx": p["vx"], "vy": p["vy"],
               "vz": round(lp.vz, 4) if lp is not None else 0.0, "yaw": p["yaw"],
               "quality": p["quality"], "reset_counter": p["reset_counter"], "sigma_xy": p["sigma_xy"],
               "sp": d["setpoint"], "filter_intervened": bool(d["intervened"]), "mode": "OFFBOARD",
               "loop_mode": d["mode"], "health": d["health"], "source": d["source"],
               "reasons": d["reasons"], "plan_ms": d["plan_ms"]}
        if tr is not None:
            out["truth"] = {"x": round(tr.x, 4), "y": round(tr.y, 4), "z": round(tr.z, 4)}
        plan = _planned(self.planner) if self.planner is not None else None
        if plan is not None and plan != self._last_plan:
            out["planned"] = plan
            self._last_plan = plan
        self.fh.write(json.dumps(out) + "\n")
        self.lines += 1
