"""Relocalization after VIO loss for the arena flight: the hub's close-area-relocalize arm (f) multi_ig.

    ad = ArenaAdapter.from_spec("arena:random:0", arena_dir, fault="jump")
    shim = RelocShim(ad, reloc_dir, odom=open("results/first_flight_reloc_odometry.jsonl", "w"))
    run(ad, planner, safety, ad.goal, grid=ad.grid, reloc=shim, ...)

What it does (sim only, synthetic):

- Wraps the arena estimator in `disambiguate.DisambPoseSource(kind="infogain")` from
  samples/close-area-relocalize, loaded by path (relocalize.py, disambiguate.py; neither edited).
  Same construction as its run_disambiguate.py arm multi_ig: own range fan (rng [seed, index, 4301]),
  move rng [seed, index, 4501], goal B as the tie-break. Installed as the SimAdapter pose source,
  so `ArenaAdapter.pose()` returns the relocalized pose. arena_adapter.py is not changed.
- The relocalizer runs at RELOC_HZ (10 Hz, the rate it was measured at). On the 20 Hz loop ticks
  in between, the estimator is still stepped and the pose is raw + the current anchor offset.
- Loss triggers, hover, matching, the RatioPersistence accept rule and the info-gain move are
  the sample's code. While it relocalizes the pose reports quality 0 (NavHealth => lost) and
  `relocalizing` is True; `cmd` is the move to fly or None (hover). flightloop/loop.py reads both.
- Map-consistency fix (this file's own rule, not measured in the sample): on a nominal 10 Hz call,
  if the scan scores >= S_INNOV (0.5) at the reported pose, sigma_xy is reported as
  min(estimator sigma, MAP_SIGMA_M). MAP_SIGMA_M = 0.10 m is the matcher's likelihood width, an
  assumption, not fitted. Without it the estimator's dark-zone sigma (0.40 m at B in the jump
  flight) keeps health degraded and the arrival rule never confirms.
- The pose given to the loop keeps the estimator's own reset_counter (NavHealth counts VIO
  resets). The re-anchor goes out on the ODOMETRY stream instead, below.

ODOMETRY dry run (`odom=` file, one JSON line per loop tick): MAVLink ODOMETRY-like fields as a
companion would send them to the autopilot. Contract from hub doc
docs/research/close-area-nav/10-relocalization-prior-art.md section 4: quality 0 while
relocalizing, and one `reset_counter` increment at each accepted re-anchor, sent with quality
back up. PX4 EKF2 v1.17.0 `ev_control.cpp:52` treats a changed counter as a reset and
`ev_pos_control.cpp:246` snaps the horizontal position to the new pose (doc 10; not run here).
Nothing is sent to an autopilot.

Stdlib at import time. numpy / scipy load when the shim is built (venv).
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import math
import os
import sys

try:
    from .adapter import enu_to_ned, flu_to_frd, world_to_body, yaw_enu_to_ned
except ImportError:
    from adapter import enu_to_ned, flu_to_frd, world_to_body, yaw_enu_to_ned

RELOC_HZ = 10.0            # relocalizer call rate (run.DEFAULTS["plan_hz"] in the sample's runs)
MAP_SIGMA_M = 0.10         # sigma_xy reported when the scan matches the map at the pose (assumed)
KIND = "infogain"          # arm (f) multi_ig
MAV_FRAME_LOCAL_NED = 1
MAV_FRAME_BODY_FRD = 12
MAV_ESTIMATOR_TYPE_VIO = 3


def load_reloc(reloc_dir: str):
    """Load relocalize.py (as `relocalize`, which disambiguate.py imports) and disambiguate.py."""
    reloc_dir = os.path.abspath(reloc_dir)
    mods = []
    for name in ("relocalize", "disambiguate"):
        if name in sys.modules and getattr(sys.modules[name], "__file__", "").startswith(reloc_dir):
            mods.append(sys.modules[name])
            continue
        path = os.path.join(reloc_dir, name + ".py")
        if not os.path.exists(path):
            raise FileNotFoundError(f"{name}.py not found in {reloc_dir}: pass --reloc-dir or set RELOC=")
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        mods.append(mod)
    return mods[0], mods[1]


def odometry_msg(pose, reset_counter: int, quality: int) -> dict:
    """One MAVLink ODOMETRY-like message from a local-ENU Pose. Position in LOCAL_NED,
    velocity in BODY_FRD (child_frame_id), yaw-only quaternion [w, x, y, z]."""
    n, e, d = enu_to_ned((pose.x, pose.y, pose.z))
    vb = flu_to_frd(world_to_body((pose.vx, pose.vy, pose.vz), pose.yaw))
    psi = yaw_enu_to_ned(pose.yaw)
    var = None if pose.sigma_xy is None else round(pose.sigma_xy ** 2, 5)
    return {"msg": "ODOMETRY", "time_usec": int(round(pose.t * 1e6)),
            "frame_id": MAV_FRAME_LOCAL_NED, "child_frame_id": MAV_FRAME_BODY_FRD,
            "x": round(n, 3), "y": round(e, 3), "z": round(d, 3),
            "q": [round(math.cos(psi / 2), 4), 0.0, 0.0, round(math.sin(psi / 2), 4)],
            "vx": round(vb[0], 3), "vy": round(vb[1], 3), "vz": round(vb[2], 3),
            "pose_covariance_xx_yy": [var, var], "reset_counter": int(reset_counter),
            "estimator_type": MAV_ESTIMATOR_TYPE_VIO, "quality": int(quality)}


class OdometryStream:
    """Companion side of the contract: quality 0 while relocalizing, counter +1 per re-anchor."""

    def __init__(self, fh=None) -> None:
        self.fh, self.counter, self.lines, self.increments = fh, 0, 0, []

    def emit(self, pose, relocalizing: bool, reanchors: int) -> dict:
        if reanchors > self.counter:
            self.increments.append(round(pose.t, 3))
            self.counter = reanchors
        q = 0 if relocalizing else max(0, int(pose.quality))
        m = odometry_msg(pose, self.counter, q)
        if self.fh is not None:
            self.fh.write(json.dumps(m) + "\n")
            self.lines += 1
        return m


class RelocShim:
    """Pose source for ArenaAdapter.sim plus the `relocalizing` / `cmd` the loop reads."""

    def __init__(self, ad, reloc_dir: str, odom=None) -> None:
        if ad.estimator is None:
            raise ValueError("--reloc needs --fault (a pose estimator to relocalize)")
        import numpy as np
        R, D = load_reloc(reloc_dir)
        run = importlib.import_module("close_area_arena.run")
        sensors = importlib.import_module("close_area_arena.sensors")
        self.R, self.ad, self.est = R, ad, ad.estimator
        w, seed, index = ad.world, ad.seed, ad.index
        fan = sensors.RangeFan(rng=np.random.default_rng([seed, index, 4301]), **run.DEFAULTS["sensor"])
        self.last_scan = None

        def scan_fn(truth):
            self.last_scan = fan.scan(w, truth.x, truth.y, truth.yaw, truth.t)
            return self.last_scan

        self.src = D.DisambPoseSource(self.est, w.grid, scan_fn, KIND,
                                      rng=np.random.default_rng([seed, index, 4501]), goal=w.goal)
        self.np = np
        self.odom = OdometryStream(odom)
        self.map_ok = False
        self._next_t = None
        ad.sim.pose_source = self       # SimAdapter.pose() => self(truth)

    @property
    def relocalizing(self) -> bool:
        return self.src.state == "reloc"

    @property
    def cmd(self):
        return self.src.cmd

    @property
    def events(self):
        return self.src.events

    def reanchors(self) -> int:
        return sum(1 for e in self.src.events if e.result == "accepted")

    def __call__(self, truth):
        dt = 1.0 / RELOC_HZ
        if self._next_t is None or truth.t >= self._next_t - 1e-9:
            self._next_t = (truth.t if self._next_t is None else self._next_t) + dt
            out = self.src(truth)
            if not self.relocalizing and self.last_scan is not None:
                s = self.src.matcher.score_at(self.last_scan, out.yaw, (out.x, out.y))
                self.map_ok = s is not None and s >= self.R.S_INNOV
            else:
                self.map_ok = False
        else:                                    # between relocalizer calls: raw + anchor
            raw = self.est(truth)
            q = 0 if self.relocalizing else (raw.quality if raw.quality > 0 else 50)
            out = type(raw)(t=raw.t, x=raw.x + float(self.src.offset[0]), y=raw.y + float(self.src.offset[1]),
                            z=raw.z, vx=raw.vx, vy=raw.vy, vz=raw.vz, yaw=raw.yaw, quality=q,
                            reset_counter=raw.reset_counter, sigma_xy=raw.sigma_xy)
        if self.map_ok and out.sigma_xy is not None:
            out = type(out)(t=out.t, x=out.x, y=out.y, z=out.z, vx=out.vx, vy=out.vy, vz=out.vz,
                            yaw=out.yaw, quality=out.quality, reset_counter=out.reset_counter,
                            sigma_xy=min(out.sigma_xy, MAP_SIGMA_M))
        self.odom.emit(out, self.relocalizing, self.reanchors())
        return out

    def summary(self, truth_err_m: float = 0.5) -> dict:
        ev = [e.to_dict() for e in self.src.events]
        return {"events": len(ev), "reanchors": self.reanchors(),
                "wrong_commits": sum(1 for e in ev if e["err_m"] is not None and e["err_m"] > truth_err_m),
                "open_at_end": sum(1 for e in ev if e["result"] == "open"),
                "moves": sum(1 for ms in self.src.moves.values() for m in ms if m.get("move") is not None),
                "reset_counter_out": self.odom.counter, "increments_t": self.odom.increments,
                "reasons": [e["reason"] for e in ev]}
