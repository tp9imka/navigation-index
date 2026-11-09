"""World JSON (`close-area-world/1`): one file format for arena layouts, a browser playground
and the replay viewer.

to_json(world) -> dict      from_json(dict) -> world.World (grid rasterized, materials, tags)

Schema (all lengths in metres, local ENU, 2.5D: obstacles are vertical prisms):

    {
      "schema": "close-area-world/1",
      "frame": "local ENU m, origin at A",
      "family": "office", "seed": 0, "index": 0,     # provenance; "custom" for hand-made worlds
      "bounds": [xmin, ymin, xmax, ymax],            # walled area
      "a": [0.0, 0.0],                               # start A
      "b": [bx, by],                                 # goal B
      "z": 1.0,                                      # hold altitude
      "radius": 0.15,                                # vehicle radius the free path was checked for
      "obstacles": [
        {"type": "box", "cx": .., "cy": .., "hx": .., "hy": .., "material": "matte", "tag": "desk"},
        {"type": "cylinder", "cx": .., "cy": .., "r": .., "material": "matte", "tag": "pole"},
        {"type": "wall", "x0": .., "y0": .., "x1": .., "y1": .., "thickness": .., "material": "glass", "tag": "glass"}
      ]
    }

- box: axis-aligned, centre (cx, cy), half sizes (hx, hy).
- cylinder: vertical, centre and radius.
- wall: a segment from (x0, y0) to (x1, y1) with flat ends, `thickness` across it. Only
  axis-aligned walls are accepted (the arena has no rotated boxes); from_json raises otherwise.
  to_json writes a box as a wall when its short half size is <= 0.1 m and its long side is at
  least 4x the short one.
- material: one of MATERIALS. Only sensors_cone.ConeRangeFan reads it ("glass", "mirror"
  invisible, "dark" short range). Truth geometry and the free-path check include every material.
  Missing => "matte".
- tag: free text for drawing (wall, desk, shelf, pallet, pole, glass). Optional.
- If "a" is not [0, 0], from_json shifts everything so A is the origin (the arena frame).
- Numbers are rounded to 4 decimals (0.1 mm). to_json(from_json(d)) == d for any d to_json wrote.

from_json does not re-check the free path; call worlds_complex.has_free_path(w) for that.

python world_json.py --check     # round trip on layouts 0-2 of every family, results/worlds_roundtrip.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

try:
    from . import world as W
except ImportError:
    import world as W

SCHEMA = "close-area-world/1"
MATERIALS = ("matte", "dark", "glass", "mirror", "pole")
WALL_MAX_HALF = 0.1      # m, short half size at or below which a box is written as a wall
WALL_ASPECT = 4.0
ND = 4                   # decimals


def _r(v):
    return round(float(v), ND)


def to_json(w: W.World, radius: float = W.RADIUS, z: float = 1.0) -> dict:
    mats = getattr(w, "materials", None) or {}
    tags = getattr(w, "tags", None) or {}
    bm = mats.get("boxes") or ["matte"] * len(w.boxes)
    cm = mats.get("cylinders") or ["matte"] * len(w.cylinders)
    bt = tags.get("boxes") or [None] * len(w.boxes)
    ct = tags.get("cylinders") or [None] * len(w.cylinders)
    obs = []
    for b, m, t in zip(w.boxes, bm, bt):
        short, long_ = min(b.hx, b.hy), max(b.hx, b.hy)
        if short <= WALL_MAX_HALF and long_ >= WALL_ASPECT * short:
            if b.hx >= b.hy:
                o = {"type": "wall", "x0": _r(b.cx - b.hx), "y0": _r(b.cy), "x1": _r(b.cx + b.hx),
                     "y1": _r(b.cy), "thickness": _r(2 * b.hy)}
            else:
                o = {"type": "wall", "x0": _r(b.cx), "y0": _r(b.cy - b.hy), "x1": _r(b.cx),
                     "y1": _r(b.cy + b.hy), "thickness": _r(2 * b.hx)}
        else:
            o = {"type": "box", "cx": _r(b.cx), "cy": _r(b.cy), "hx": _r(b.hx), "hy": _r(b.hy)}
        o["material"] = m
        if t:
            o["tag"] = t
        obs.append(o)
    for c, m, t in zip(w.cylinders, cm, ct):
        o = {"type": "cylinder", "cx": _r(c.cx), "cy": _r(c.cy), "r": _r(c.r), "material": m}
        if t:
            o["tag"] = t
        obs.append(o)
    return {
        "schema": SCHEMA, "frame": "local ENU m, origin at A",
        "family": w.family, "seed": w.seed, "index": getattr(w, "index", None),
        "bounds": [_r(w.xmin), _r(w.ymin), _r(w.xmax), _r(w.ymax)],
        "a": [0.0, 0.0], "b": [_r(w.goal[0]), _r(w.goal[1])], "z": z, "radius": radius,
        "obstacles": obs,
    }


def _num(d, k, positive=False):
    v = d.get(k)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError(f"field {k!r} must be a finite number, got {v!r}")
    if positive and v <= 0:
        raise ValueError(f"field {k!r} must be > 0, got {v!r}")
    return float(v)


def _pair(d, k):
    v = d.get(k)
    if not (isinstance(v, (list, tuple)) and len(v) == 2):
        raise ValueError(f"field {k!r} must be [x, y]")
    return _num({"x": v[0]}, "x"), _num({"y": v[1]}, "y")


def from_json(d: dict, res: float = W.RES) -> W.World:
    """Validate a close-area-world/1 dict and build a World (A at the origin, grid rasterized)."""
    if not isinstance(d, dict) or d.get("schema") != SCHEMA:
        raise ValueError(f"not a {SCHEMA} document")
    bnd = d.get("bounds")
    if not (isinstance(bnd, (list, tuple)) and len(bnd) == 4):
        raise ValueError("bounds must be [xmin, ymin, xmax, ymax]")
    xmin, ymin, xmax, ymax = (_num({"v": v}, "v") for v in bnd)
    if not (xmin < xmax and ymin < ymax):
        raise ValueError("bounds must have xmin < xmax and ymin < ymax")
    ax, ay = _pair(d, "a") if "a" in d else (0.0, 0.0)
    bx, by = _pair(d, "b")
    for nm, (px, py) in (("a", (ax, ay)), ("b", (bx, by))):
        if not (xmin < px < xmax and ymin < py < ymax):
            raise ValueError(f"{nm} is outside bounds")
    obs = d.get("obstacles", [])
    if not isinstance(obs, list):
        raise ValueError("obstacles must be a list")
    boxes, cyls, bm, cm, bt, ct = [], [], [], [], [], []
    for i, o in enumerate(obs):
        if not isinstance(o, dict):
            raise ValueError(f"obstacle {i} must be an object")
        m = o.get("material", "matte")
        if m not in MATERIALS:
            raise ValueError(f"obstacle {i}: material {m!r} not in {MATERIALS}")
        tag = o.get("tag")
        typ = o.get("type")
        if typ == "box":
            boxes.append(W.Box(_num(o, "cx") - ax, _num(o, "cy") - ay, _num(o, "hx", True), _num(o, "hy", True)))
            bm.append(m); bt.append(tag)
        elif typ == "wall":
            x0, y0, x1, y1 = (_num(o, k) for k in ("x0", "y0", "x1", "y1"))
            th = _num(o, "thickness", True)
            if abs(y1 - y0) <= 1e-9 and abs(x1 - x0) > 0:
                boxes.append(W.Box((x0 + x1) / 2 - ax, y0 - ay, abs(x1 - x0) / 2, th / 2))
            elif abs(x1 - x0) <= 1e-9 and abs(y1 - y0) > 0:
                boxes.append(W.Box(x0 - ax, (y0 + y1) / 2 - ay, th / 2, abs(y1 - y0) / 2))
            else:
                raise ValueError(f"obstacle {i}: only axis-aligned walls with nonzero length are supported")
            bm.append(m); bt.append(tag)
        elif typ == "cylinder":
            cyls.append(W.Cylinder(_num(o, "cx") - ax, _num(o, "cy") - ay, _num(o, "r", True)))
            cm.append(m); ct.append(tag)
        else:
            raise ValueError(f"obstacle {i}: type {typ!r} not in ('box', 'cylinder', 'wall')")
    seed = d.get("seed", 0)
    w = W.World(family=str(d.get("family", "custom")), seed=seed if isinstance(seed, int) else 0,
                xmin=xmin - ax, ymin=ymin - ay, xmax=xmax - ax, ymax=ymax - ay,
                goal=(bx - ax, by - ay), boxes=boxes, cylinders=cyls)
    w.index = d.get("index")
    w.materials = {"boxes": bm, "cylinders": cm}
    w.tags = {"boxes": bt, "cylinders": ct}
    w.grid = w.rasterize(res)
    for c in w.cylinders:            # a pole thinner than a cell can fall between cell centres
        ix, iy = w.grid.to_index(c.cx, c.cy)
        if 0 <= ix < w.grid.occ.shape[0] and 0 <= iy < w.grid.occ.shape[1]:
            w.grid.occ[ix, iy] = True
    return w


def roundtrip_check(families, layouts: int = 3, seed: int = 0) -> list[dict]:
    """to_json => json text => from_json => to_json must be identical; geometry and grid must match."""
    try:
        from . import worlds_complex as WC
    except ImportError:
        import worlds_complex as WC
    out = []
    for fam in families:
        for i in range(layouts):
            w = WC.make_any_world(fam, seed, i)
            d = to_json(w)
            text = json.dumps(d, separators=(",", ":"))
            w2 = from_json(json.loads(text))
            same_doc = to_json(w2) == d
            pts = np.random.default_rng([seed, i, 99]).uniform(
                [w.xmin, w.ymin], [w.xmax, w.ymax], size=(4000, 2))
            sdf_err = float(np.max(np.abs(w.sdf(pts) - w2.sdf(pts))))
            grid_diff = int(np.count_nonzero(w.grid.occ != w2.grid.occ))
            path = WC.has_free_path(w2) if fam in WC.FAMILY_CODE else W.bfs_free_path(
                w2.grid.inflated(W.RADIUS), w2.grid.to_index(0, 0), w2.grid.to_index(*w2.goal)) is not None
            mat_ok = (getattr(w, "materials", None) or {}) == w2.materials or fam not in WC.FAMILY_CODE
            ok = same_doc and sdf_err < 1e-3 and path and mat_ok
            out.append({"family": fam, "index": i, "bytes": len(text), "same_doc": same_doc,
                        "max_sdf_err_m": round(sdf_err, 6), "grid_cells_differ": grid_diff,
                        "free_path_after": bool(path), "materials_kept": bool(mat_ok), "ok": bool(ok)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--layouts", type=int, default=3)
    a = ap.parse_args(argv)
    if not a.check:
        ap.print_help()
        return 0
    try:
        from . import world_glass
    except ImportError:
        import world_glass
    fams = tuple(world_glass.FAMILIES)
    rows = roundtrip_check(fams, a.layouts)
    for r in rows:
        print(r)
    bad = [r for r in rows if not r["ok"]]
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "worlds_roundtrip.json")
    with open(p, "w") as fh:
        json.dump({"command": "python world_json.py " + " ".join(argv if argv is not None else sys.argv[1:]),
                   "input": "synthetic", "families": list(fams), "layouts": a.layouts,
                   "failed": len(bad), "rows": rows}, fh, indent=1)
    print(f"{len(rows) - len(bad)}/{len(rows)} ok; wrote {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
