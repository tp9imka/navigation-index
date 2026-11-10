"""Room spec JSON => close-area-world/1 JSON, so a real room can be flown in the arena.

python world_from_room.py rooms/hall_8x6.json -o rooms/hall_8x6.world.json [--fly] [--preview PNG]

Room spec (metres, origin at the room's lower-left corner, +x right, +y up on the plan):

    {
      "name": "hall_8x6",
      "size_m": [8.0, 6.0],                 # outer walls = the world bounds
      "height_m": 3.0,                      # optional ceiling; only checks z_m is below it
      "z_m": 1.0,                           # optional hold altitude, default 1.0
      "wall_thickness_m": 0.1,              # optional default for interior walls
      "walls": [                            # interior walls, axis-aligned only
        {"from": [5.0, 0.0], "to": [5.0, 6.0], "thickness": 0.12,
         "doors": [[3.5, 0.9]]}             # [offset from "from" along the wall, width], metres
      ],
      "pillars": [{"at": [2.5, 3.0], "r": 0.2}],                  # => cylinders
      "boxes":   [{"at": [1.6, 4.4], "size": [1.6, 0.8], "tag": "table"}],   # centre + full size
      "a": [0.8, 0.8], "b": [7.2, 5.2]
    }

Every item takes an optional "material" (world_json.MATERIALS) and "tag". The output keeps the
plan frame: bounds [0, 0, w, h] and "a" as given (from_json moves the origin to A).

--fly flies astar_esdf with the known map (run.run_one, truth pose, ideal arena defaults) and
writes results/room_<name>.json; --preview writes the map and flown path as a PNG.
Exit code 1 if the world fails world_json.from_json or the free-path check.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

try:
    from . import world as W, world_json as WJ, worlds_complex as WC
except ImportError:
    import world as W
    import world_json as WJ
    import worlds_complex as WC

ND = 4


def _r(v):
    return round(float(v), ND)


def _xy(v, what):
    if not (isinstance(v, (list, tuple)) and len(v) == 2
            and all(isinstance(t, (int, float)) and not isinstance(t, bool) and math.isfinite(t) for t in v)):
        raise ValueError(f"{what} must be [x, y] in metres, got {v!r}")
    return float(v[0]), float(v[1])


def _pos(v, what):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
        raise ValueError(f"{what} must be a number > 0, got {v!r}")
    return float(v)


def _extra(item, i, kind):
    out = {}
    m = item.get("material", "matte")
    if m not in WJ.MATERIALS:
        raise ValueError(f"{kind} {i}: material {m!r} not in {WJ.MATERIALS}")
    out["material"] = m
    if item.get("tag"):
        out["tag"] = str(item["tag"])
    return out


def wall_segments(x0, y0, x1, y1, doors):
    """Split an axis-aligned wall into the pieces left after cutting the door gaps."""
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    cuts = []
    for d in doors:
        if not (isinstance(d, (list, tuple)) and len(d) == 2):
            raise ValueError(f"door must be [offset_m, width_m], got {d!r}")
        off, wid = float(d[0]), _pos(d[1], "door width")
        if off < 0 or off + wid > length + 1e-9:
            raise ValueError(f"door {d!r} does not fit a {length:.2f} m wall")
        cuts.append((off, off + wid))
    cuts.sort()
    pieces, s = [], 0.0
    for c0, c1 in cuts:
        if c0 < s - 1e-9:
            raise ValueError("doors overlap")
        if c0 - s > 1e-6:
            pieces.append((s, c0))
        s = c1
    if length - s > 1e-6:
        pieces.append((s, length))
    return [(x0 + ux * p0, y0 + uy * p0, x0 + ux * p1, y0 + uy * p1) for p0, p1 in pieces]


def room_to_world(spec: dict) -> dict:
    if not isinstance(spec, dict):
        raise ValueError("room spec must be a JSON object")
    w, h = _xy(spec.get("size_m"), "size_m")
    if w <= 0 or h <= 0:
        raise ValueError("size_m must be positive")
    z = float(spec.get("z_m", 1.0))
    if "height_m" in spec and z > _pos(spec["height_m"], "height_m") - 0.3:
        raise ValueError(f"z_m {z} is within 0.3 m of the ceiling height_m {spec['height_m']}")
    t_def = _pos(spec.get("wall_thickness_m", 0.1), "wall_thickness_m")
    obs = []
    for i, wl in enumerate(spec.get("walls", [])):
        x0, y0 = _xy(wl.get("from"), f"wall {i} from")
        x1, y1 = _xy(wl.get("to"), f"wall {i} to")
        if not ((abs(x0 - x1) < 1e-9) ^ (abs(y0 - y1) < 1e-9)):
            raise ValueError(f"wall {i}: only axis-aligned walls with nonzero length are supported")
        th = _pos(wl.get("thickness", t_def), f"wall {i} thickness")
        ex = _extra(wl, i, "wall")
        ex.setdefault("tag", "wall")
        for sx0, sy0, sx1, sy1 in wall_segments(x0, y0, x1, y1, wl.get("doors", [])):
            obs.append({"type": "wall", "x0": _r(sx0), "y0": _r(sy0), "x1": _r(sx1), "y1": _r(sy1),
                        "thickness": _r(th), **ex})
    for i, b in enumerate(spec.get("boxes", [])):
        cx, cy = _xy(b.get("at"), f"box {i} at")
        sx, sy = _xy(b.get("size"), f"box {i} size")
        _pos(sx, f"box {i} size x"), _pos(sy, f"box {i} size y")
        obs.append({"type": "box", "cx": _r(cx), "cy": _r(cy), "hx": _r(sx / 2), "hy": _r(sy / 2),
                    **_extra(b, i, "box")})
    for i, p in enumerate(spec.get("pillars", [])):
        cx, cy = _xy(p.get("at"), f"pillar {i} at")
        ex = _extra(p, i, "pillar")
        ex.setdefault("tag", "pillar")
        obs.append({"type": "cylinder", "cx": _r(cx), "cy": _r(cy), "r": _r(_pos(p.get("r"), f"pillar {i} r")), **ex})
    a = _xy(spec.get("a"), "a")
    b = _xy(spec.get("b"), "b")
    return {
        "schema": WJ.SCHEMA, "frame": "local ENU m, origin at A",
        "family": "custom", "seed": 0, "index": 0,
        "bounds": [0.0, 0.0, _r(w), _r(h)],
        "a": [_r(a[0]), _r(a[1])], "b": [_r(b[0]), _r(b[1])],
        "z": _r(z), "radius": W.RADIUS, "obstacles": obs,
    }


def check(doc: dict):
    """from_json + the arena's free-path check. Returns (world, problems list)."""
    w = WJ.from_json(doc)
    problems = []
    for nm, (x, y) in (("A", (0.0, 0.0)), ("B", w.goal)):
        c = w.clearance(x, y)
        if c <= W.RADIUS + WC.END_CLEAR:
            problems.append(f"{nm} has {c:.3f} m clearance, needs > {W.RADIUS + WC.END_CLEAR:.2f} m")
    if not WC.has_free_path(w):
        problems.append(f"no free path A => B on the 0.1 m grid inflated by {W.RADIUS} m")
    return w, problems


def fly(w, name: str, preview: str | None = None, out_dir: str | None = None, extra: dict | None = None) -> dict:
    """astar_esdf known map through run.run_one (truth pose, arena defaults). Synthetic."""
    try:
        from . import run
    except ImportError:
        import run
    planner = run.load_planner("astar_esdf", known_map=True)
    row, _, xy = run.run_one(planner, w, seed=0, index=0)
    t = "-" if row["time_to_goal_s"] is None else f"{row['time_to_goal_s']} s"
    line = (f"astar_known on {name}: {row['outcome']}, time to goal {t}, "
            f"min clearance {row['min_clearance_m']} m, path {row['path_length_m']} m, "
            f"{row['n_obstacles']} obstacles (synthetic, truth pose)")
    out_dir = out_dir or run.RESULTS
    os.makedirs(out_dir, exist_ok=True)
    rec = os.path.join(out_dir, f"room_{name}.json")
    with open(rec, "w") as fh:
        json.dump({"input": "synthetic (world from a room description, simulated vehicle and sensor)",
                   "planner": "astar_esdf known_map=True", "command": " ".join(["python", os.path.basename(sys.argv[0])] + sys.argv[1:]),
                   "score_line": line, **(extra or {}), "run": row}, fh, indent=1)
    if preview:
        run.plot_run(preview, w, xy, row, run.DEFAULTS["vehicle"]["radius"], px_per_cell=6)
    return {"line": line, "row": row, "record": rec}


def finish(doc: dict, out: str, name: str, do_fly: bool, preview: str | None, extra: dict | None = None) -> int:
    """Shared tail of both CLIs: write, check, optionally fly and render."""
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=1)
    try:
        w, problems = check(doc)
    except ValueError as e:
        print(f"FAIL world_json.from_json: {e}")
        return 1
    print(f"wrote {out}: {len(doc['obstacles'])} obstacles, bounds {doc['bounds']}, A {doc['a']}, B {doc['b']}")
    if problems:
        for p in problems:
            print("FAIL " + p)
        return 1
    print("ok from_json, ok has_free_path")
    if do_fly or preview:
        r = fly(w, name, preview, extra=extra)
        print(r["line"])
        print(f"wrote {os.path.relpath(r['record'])}" + (f", {preview}" if preview else ""))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="room spec JSON")
    ap.add_argument("-o", "--out", help="world JSON to write (default: <spec>.world.json)")
    ap.add_argument("--fly", action="store_true", help="fly astar_esdf known map, write results/room_<name>.json")
    ap.add_argument("--preview", help="PNG of map + flown path (implies --fly)")
    a = ap.parse_args(argv)
    with open(a.spec) as fh:
        spec = json.load(fh)
    name = str(spec.get("name") or os.path.splitext(os.path.basename(a.spec))[0])
    try:
        doc = room_to_world(spec)
    except ValueError as e:
        print(f"FAIL room spec: {e}")
        return 1
    out = a.out or os.path.splitext(a.spec)[0] + ".world.json"
    return finish(doc, out, name, a.fly, a.preview)


if __name__ == "__main__":
    raise SystemExit(main())
