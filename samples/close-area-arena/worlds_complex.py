"""Complex layout families for the arena: office, warehouse, forest, maze, glass_office.

Same world model as world.py (2.5D axis-aligned boxes and vertical cylinders in a walled
20 x 20 m area, local ENU with the origin at A). Each layout is seeded by
np.random.default_rng([seed, index, family_code]) and resampled until a 4-connected path
A => B exists on the 0.1 m grid inflated by the vehicle radius (world.bfs_free_path), and A and
B have exact clearance > radius + 0.1 m.

Families (area frame [0, 20]^2 before the shift to the A origin; sizes are arena choices, not
measurements of real buildings):
- office: a corridor (1.6-2.0 m wide) across the middle, 3-6 rooms of 3.6-4.4 x 3.6-4.4 m off
  it on both sides, one 0.8-1.0 m doorway per room on the corridor side, 1-2 desks per room
  (1.2-1.6 x 0.6-0.8 m). Walls 0.1 m thick. A and B are in different rooms (B in one of the two
  rooms farthest from A's room). The floor outside the rooms is open.
- warehouse: shelf rows along x (0.8-1.0 m deep) with 1.2-1.6 m aisles, a 1.8-2.4 m main
  aisle on the left, rows run into the right wall, 1-2 cross aisles 1.2-1.6 m wide, 2-6 pallets
  (0.8-1.2 m along the aisle, 0.4-0.7 m across) pushed against a shelf face. A in the bottom
  aisle near the left, B in the top aisle near the right.
- forest: 40-90 poles, diameter 0.1-0.35 m. Dart throwing (Poisson-disk style) with 1.3 m
  minimum centre spacing, then 3-6 "tight spot" poles placed 0.3-0.6 m (surface to surface)
  from an existing pole. A tight spot under about 0.4 m is closed on the inflated grid.
- maze: 10 x 10 cells of 2 m, depth-first (recursive backtracker) spanning tree, then 8-15 %
  of the remaining interior walls removed to make loops. Walls 0.1 m thick, collinear runs
  merged into one box. A in the bottom-left cell, B in the top-right cell.
- glass_office: an office plus 1-3 glass panels (0.04 m thick) across part of the corridor
  (45-65 % of its width, from one side), placed between A's and B's doorways when they are
  1.2 m or more apart along the corridor. Material "glass": sensors_cone.ConeRangeFan returns
  nothing for them; truth geometry, the prior grid and the free-path check contain them.

Every world carries w.materials = {"boxes": [...], "cylinders": [...]} (as world_glass.py) and
w.tags (same shape: "wall", "desk", "shelf", "pallet", "pole", "glass"), plus w.index.

python worlds_complex.py --preview --examples   # results/worlds_preview.png, worlds_examples/
python worlds_complex.py --sanity --layouts 20  # straight vs astar_esdf known, results/worlds_sanity_0.*
"""
from __future__ import annotations

# FAMILIES is defined before importing world: world.py imports this module at its end to
# register the families, and reads FAMILIES while this module may be half initialised.
FAMILIES = ("office", "warehouse", "forest", "maze", "glass_office")
FAMILY_CODE = {"office": 20, "warehouse": 21, "forest": 22, "maze": 23, "glass_office": 24}

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

try:
    from . import world as W
except ImportError:
    import world as W

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
AREA = 20.0
T = 0.05                 # m, half thickness of office and maze walls
GLASS_HALF_T = 0.02      # m, half thickness of a glass panel (as world_glass.PANEL_HALF_T)
END_CLEAR = 0.1          # m, exact clearance of A and B above the vehicle radius


def _ext(xa, xb, ya, yb):
    """Box (cx, cy, hx, hy) from its extents."""
    return (0.5 * (xa + xb), 0.5 * (ya + yb), 0.5 * abs(xb - xa), 0.5 * abs(yb - ya))


def _box_point_dist(b, x, y):
    q = np.abs(np.array([x - b[0], y - b[1]])) - (b[2], b[3])
    return float(np.linalg.norm(np.maximum(q, 0.0)) + min(q.max(), 0.0))


def _ob(kind, geom, mat="matte", tag="wall"):
    return {"kind": kind, "geom": tuple(float(v) for v in geom), "mat": mat, "tag": tag}


# ---------------------------------------------------------------- office

def _office_layout(rng):
    yc = rng.uniform(9.0, 11.0)
    wc = rng.uniform(1.6, 2.0)
    n = int(rng.integers(3, 7))
    n_top = int(rng.integers(1, n))              # at least one room per side
    rooms = []                                    # dict(x0, x1, y0, y1, front_y, side)
    for side, k in (("top", n_top), ("bot", n - n_top)):
        widths = rng.uniform(3.6, 4.4, size=k)
        depth = rng.uniform(3.6, 4.4)
        x = rng.uniform(0.5, max(0.5, AREA - 0.5 - widths.sum()))
        for wdt in widths:
            if side == "top":
                y0 = yc + wc / 2
                rooms.append({"x0": x, "x1": x + wdt, "y0": y0, "y1": y0 + depth, "front": y0, "side": side})
            else:
                y1 = yc - wc / 2
                rooms.append({"x0": x, "x1": x + wdt, "y0": y1 - depth, "y1": y1, "front": y1, "side": side})
            x += wdt
    obs, seen = [], set()

    def add(geom, mat="matte", tag="wall"):
        key = tuple(round(v, 6) for v in geom)
        if key not in seen:
            seen.add(key)
            obs.append(_ob("box", geom, mat, tag))

    for r in rooms:
        dw = rng.uniform(0.8, 1.0)
        dc = rng.uniform(r["x0"] + 0.3 + dw / 2, r["x1"] - 0.3 - dw / 2)
        r["door"] = (dc, r["front"], dw)
        back = r["y1"] if r["side"] == "top" else r["y0"]
        add(_ext(r["x0"] - T, r["x1"] + T, back - T, back + T))
        add(_ext(r["x0"] - T, r["x0"] + T, r["y0"] - T, r["y1"] + T))
        add(_ext(r["x1"] - T, r["x1"] + T, r["y0"] - T, r["y1"] + T))
        f = r["front"]
        add(_ext(r["x0"] - T, dc - dw / 2, f - T, f + T))
        add(_ext(dc + dw / 2, r["x1"] + T, f - T, f + T))
    ia = int(rng.integers(len(rooms)))
    cen = np.array([[(r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2] for r in rooms])
    far = np.argsort(-np.linalg.norm(cen - cen[ia], axis=1))[:2]
    ib = int(far[int(rng.integers(len(far)))])

    def inside(r, m):
        return (float(rng.uniform(r["x0"] + m, r["x1"] - m)), float(rng.uniform(r["y0"] + m, r["y1"] - m)))

    a = inside(rooms[ia], 0.8)
    b = inside(rooms[ib], 0.8)
    for r in rooms:
        dc, f, _ = r["door"]
        inward = 0.6 if r["side"] == "top" else -0.6
        keep = [(a[0], a[1], 0.8), (b[0], b[1], 0.8), (dc, f + inward, 1.0)]
        for _ in range(int(rng.integers(1, 3))):
            for _try in range(30):
                L, S = rng.uniform(1.2, 1.6), rng.uniform(0.6, 0.8)
                hx, hy = (L / 2, S / 2) if rng.random() < 0.5 else (S / 2, L / 2)
                m = 0.3 + T
                if r["x1"] - r["x0"] - 2 * m < 2 * hx or r["y1"] - r["y0"] - 2 * m < 2 * hy:
                    continue
                cx = rng.uniform(r["x0"] + m + hx, r["x1"] - m - hx)
                cy = rng.uniform(r["y0"] + m + hy, r["y1"] - m - hy)
                g = (cx, cy, hx, hy)
                if all(_box_point_dist(g, kx, ky) > kr for kx, ky, kr in keep):
                    obs.append(_ob("box", g, "matte", "desk"))
                    break
    corridor = {"yc": yc, "wc": wc, "x0": min(r["x0"] for r in rooms), "x1": max(r["x1"] for r in rooms)}
    return a, b, obs, {"rooms": rooms, "ia": ia, "ib": ib, "corridor": corridor}


def _glass_office_layout(rng):
    a, b, obs, info = _office_layout(rng)
    rooms, cor = info["rooms"], info["corridor"]
    da, db = rooms[info["ia"]]["door"][0], rooms[info["ib"]]["door"][0]
    lo, hi = sorted((da, db))
    if hi - lo >= 1.2:
        lo, hi = lo + 0.6, hi - 0.6
    else:
        lo, hi = cor["x0"] + 0.5, cor["x1"] - 0.5
    doors = [r["door"] for r in rooms]
    ybot = cor["yc"] - cor["wc"] / 2 + T
    ytop = cor["yc"] + cor["wc"] / 2 - T
    placed = []
    for _ in range(int(rng.integers(1, 4))):
        for _try in range(50):
            px = float(rng.uniform(lo, hi))
            if any(abs(px - dc) < dw / 2 + 0.3 for dc, _, dw in doors):
                continue
            if any(abs(px - q) < 0.8 for q in placed):
                continue
            L = rng.uniform(0.45, 0.65) * (ytop - ybot)
            if rng.random() < 0.5:
                g = _ext(px - GLASS_HALF_T, px + GLASS_HALF_T, ybot, ybot + L)
            else:
                g = _ext(px - GLASS_HALF_T, px + GLASS_HALF_T, ytop - L, ytop)
            obs.append(_ob("box", g, "glass", "glass"))
            placed.append(px)
            break
    return a, b, obs, info


# ---------------------------------------------------------------- warehouse

def _warehouse_layout(rng):
    xs = rng.uniform(1.8, 2.4)                    # main aisle x in [0, xs]
    d = rng.uniform(0.8, 1.0)
    aisles = [(0.0, rng.uniform(1.2, 1.6))]
    shelves = []
    y = aisles[0][1]
    while True:
        w = rng.uniform(1.2, 1.6)
        if y + d + w > AREA:
            break
        shelves.append((y, y + d))
        aisles.append((y + d, y + d + w))
        y += d + w
    aisles[-1] = (aisles[-1][0], AREA)            # top aisle takes the remainder
    k = int(rng.integers(1, 3))
    cross = []
    while len(cross) < k:
        c, w = rng.uniform(6.0, 17.0), rng.uniform(1.2, 1.6)
        if all(abs(c - q[0]) > 4.0 for q in cross):
            cross.append((c, w))
    cuts = sorted((c - w / 2, c + w / 2) for c, w in cross)
    obs = []
    for (y0, y1) in shelves:
        x = xs
        for (c0, c1) in cuts + [(AREA, AREA)]:
            if c0 - x > 0.2:
                obs.append(_ob("box", _ext(x, c0, y0, y1), "matte", "shelf"))
            x = c1
    a0, a1 = aisles[0]
    t0, t1 = aisles[-1]
    a = (float(rng.uniform(xs + 0.8, xs + 4.0)), float(a0 + 0.5 * (a1 - a0)))
    b = (float(rng.uniform(16.0, AREA - 1.0)), float(t0 + 0.7))
    for _ in range(int(rng.integers(2, 7))):
        for _try in range(30):
            ai = int(rng.integers(len(aisles)))
            y0, y1 = aisles[ai]
            if ai == len(aisles) - 1:
                y1 = min(y1, y0 + 1.6)
            L, S = rng.uniform(0.8, 1.2), rng.uniform(0.4, 0.7)
            cx = rng.uniform(xs + 0.5, AREA - 0.5)
            g = _ext(cx - L / 2, cx + L / 2, y0, y0 + S) if rng.random() < 0.5 else \
                _ext(cx - L / 2, cx + L / 2, y1 - S, y1)
            if _box_point_dist(g, *a) > 1.0 and _box_point_dist(g, *b) > 1.0:
                obs.append(_ob("box", g, "matte", "pallet"))
                break
    return a, b, obs, {"aisles": aisles, "cross": cross}


# ---------------------------------------------------------------- forest

FOREST_DMIN = 1.3         # m, minimum centre spacing of the dart-throwing pass
FOREST_R = (0.05, 0.175)  # m, radius => 0.1-0.35 m diameter


def _forest_layout(rng):
    a = (1.5 + rng.uniform(-0.5, 0.5), 1.5 + rng.uniform(-0.5, 0.5))
    b = (AREA - 1.5 + rng.uniform(-0.5, 0.5), AREA - 1.5 + rng.uniform(-0.5, 0.5))
    n = int(rng.integers(40, 91))
    k_tight = int(rng.integers(3, 7))
    poles = []                                    # (cx, cy, r)

    def free_of_ends(x, y, r):
        return np.hypot(x - a[0], y - a[1]) > 1.0 + r and np.hypot(x - b[0], y - b[1]) > 1.0 + r

    tries = 0
    while len(poles) < n - k_tight and tries < 20000:
        tries += 1
        x, y = rng.uniform(0.5, AREA - 0.5, size=2)
        r = rng.uniform(*FOREST_R)
        if not free_of_ends(x, y, r):
            continue
        if poles and np.min(np.hypot(*(np.array(poles)[:, :2] - (x, y)).T)) < FOREST_DMIN:
            continue
        poles.append((float(x), float(y), float(r)))
    tries = 0
    added = 0
    while added < k_tight and tries < 2000:
        tries += 1
        j = int(rng.integers(len(poles)))
        r = rng.uniform(*FOREST_R)
        gap = rng.uniform(0.3, 0.6)
        ang = rng.uniform(0, 2 * np.pi)
        cj = poles[j]
        dist = cj[2] + r + gap
        x, y = cj[0] + dist * np.cos(ang), cj[1] + dist * np.sin(ang)
        if not (0.5 < x < AREA - 0.5 and 0.5 < y < AREA - 0.5) or not free_of_ends(x, y, r):
            continue
        P = np.array(poles)
        surf = np.hypot(P[:, 0] - x, P[:, 1] - y) - P[:, 2] - r
        surf[j] = np.inf
        if surf.min() < 0.3:
            continue
        poles.append((float(x), float(y), float(r)))
        added += 1
    obs = [_ob("cyl", p, "matte", "pole") for p in poles]
    return a, b, obs, {"n_tight": added}


# ---------------------------------------------------------------- maze

MAZE_N = 10
MAZE_CELL = 2.0


def _maze_layout(rng):
    N, C = MAZE_N, MAZE_CELL
    # h[i, j]: wall on line y = j*C between cells (i, j-1) and (i, j), j = 1..N-1
    # v[i, j]: wall on line x = i*C between cells (i-1, j) and (i, j), i = 1..N-1
    h = np.ones((N, N + 1), bool)
    v = np.ones((N + 1, N), bool)
    seen = np.zeros((N, N), bool)
    start = (int(rng.integers(N)), int(rng.integers(N)))
    stack = [start]
    seen[start] = True
    while stack:
        i, j = stack[-1]
        nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= i + di < N and 0 <= j + dj < N and not seen[i + di, j + dj]]
        if not nb:
            stack.pop()
            continue
        ni, nj = nb[int(rng.integers(len(nb)))]
        if ni != i:
            v[max(i, ni), j] = False
        else:
            h[i, max(j, nj)] = False
        seen[ni, nj] = True
        stack.append((ni, nj))
    interior = [("h", i, j) for i in range(N) for j in range(1, N) if h[i, j]] + \
               [("v", i, j) for i in range(1, N) for j in range(N) if v[i, j]]
    n_rm = int(round(rng.uniform(0.08, 0.15) * len(interior)))
    for k in rng.choice(len(interior), size=n_rm, replace=False):
        kind, i, j = interior[int(k)]
        (h if kind == "h" else v)[i, j] = False
    obs = []
    for j in range(1, N):                         # horizontal runs
        i = 0
        while i < N:
            if h[i, j]:
                i0 = i
                while i < N and h[i, j]:
                    i += 1
                g = _ext(max(0.0, i0 * C - T), min(AREA, i * C + T), j * C - T, j * C + T)
                obs.append(_ob("box", g))
            else:
                i += 1
    for i in range(1, N):                         # vertical runs
        j = 0
        while j < N:
            if v[i, j]:
                j0 = j
                while j < N and v[i, j]:
                    j += 1
                g = _ext(i * C - T, i * C + T, max(0.0, j0 * C - T), min(AREA, j * C + T))
                obs.append(_ob("box", g))
            else:
                j += 1
    a = (C / 2 + rng.uniform(-0.4, 0.4), C / 2 + rng.uniform(-0.4, 0.4))
    b = (AREA - C / 2 + rng.uniform(-0.4, 0.4), AREA - C / 2 + rng.uniform(-0.4, 0.4))
    return a, b, obs, {"removed_walls": n_rm}


_LAYOUTS = {"office": _office_layout, "warehouse": _warehouse_layout, "forest": _forest_layout,
            "maze": _maze_layout, "glass_office": _glass_office_layout}


# ---------------------------------------------------------------- build + guarantee

def build_world(family, seed, index, a, b, obs, attempts=1, res=W.RES) -> W.World:
    """World in the A-origin frame from area-frame obstacles, with materials, tags and grid."""
    ax, ay = a
    boxes = [o for o in obs if o["kind"] == "box"]
    cyls = [o for o in obs if o["kind"] == "cyl"]
    w = W.World(family=family, seed=seed, xmin=-ax, ymin=-ay, xmax=AREA - ax, ymax=AREA - ay,
                goal=(b[0] - ax, b[1] - ay),
                boxes=[W.Box(o["geom"][0] - ax, o["geom"][1] - ay, o["geom"][2], o["geom"][3]) for o in boxes],
                cylinders=[W.Cylinder(o["geom"][0] - ax, o["geom"][1] - ay, o["geom"][2]) for o in cyls],
                attempts=attempts)
    w.index = index
    w.materials = {"boxes": [o["mat"] for o in boxes], "cylinders": [o["mat"] for o in cyls]}
    w.tags = {"boxes": [o["tag"] for o in boxes], "cylinders": [o["tag"] for o in cyls]}
    w.grid = w.rasterize(res)
    return w


def has_free_path(w: W.World, radius: float = W.RADIUS) -> bool:
    if w.clearance(0.0, 0.0) <= radius + END_CLEAR or w.clearance(*w.goal) <= radius + END_CLEAR:
        return False
    blocked = w.grid.inflated(radius)
    return W.bfs_free_path(blocked, w.grid.to_index(0.0, 0.0), w.grid.to_index(*w.goal)) is not None


def make_world(family: str, seed: int = 0, index: int = 0, radius: float = W.RADIUS,
               res: float = W.RES, max_attempts: int = 200) -> W.World:
    """Deterministic complex layout for (family, seed, index). Resamples until a free path exists."""
    if family not in FAMILY_CODE:
        raise ValueError(f"unknown complex family {family!r}, expected one of {FAMILIES}")
    rng = np.random.default_rng([seed, index, FAMILY_CODE[family]])
    for attempt in range(1, max_attempts + 1):
        a, b, obs, _ = _LAYOUTS[family](rng)
        w = build_world(family, seed, index, a, b, obs, attempt, res)
        if has_free_path(w, radius):
            return w
    raise RuntimeError(f"no free layout for {family} seed {seed} index {index} in {max_attempts} tries")


def make_any_world(family: str, seed: int = 0, index: int = 0, radius: float = W.RADIUS) -> W.World:
    """Complex families with their materials; every other family through world_glass.make_any_world."""
    if family in FAMILY_CODE:
        return make_world(family, seed, index, radius)
    try:
        from . import world_glass
    except ImportError:
        import world_glass
    return world_glass.make_any_world(family, seed, index, radius)


# ---------------------------------------------------------------- outputs

COLORS = {"wall": "#3c3c3c", "desk": "#a0703c", "shelf": "#4a6fa5", "pallet": "#c8a040",
          "pole": "#3c7a3c", "glass": "#40c8e8"}


def preview(path: str, seed: int = 0) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    fig, axs = plt.subplots(1, len(FAMILIES), figsize=(4 * len(FAMILIES), 4.3))
    for ax, fam in zip(axs, FAMILIES):
        w = make_world(fam, seed, 0)
        ax.add_patch(Rectangle((w.xmin, w.ymin), w.xmax - w.xmin, w.ymax - w.ymin, fill=False, lw=2))
        for bx, tag in zip(w.boxes, w.tags["boxes"]):
            ax.add_patch(Rectangle((bx.cx - bx.hx, bx.cy - bx.hy), 2 * bx.hx, 2 * bx.hy,
                                   color=COLORS[tag], lw=1.5 if tag == "glass" else 0))
        for c, tag in zip(w.cylinders, w.tags["cylinders"]):
            ax.add_patch(Circle((c.cx, c.cy), c.r, color=COLORS[tag]))
        ax.plot(0, 0, "o", color="#00aa00", ms=8)
        ax.plot(*w.goal, "o", color="#dd0000", ms=8)
        ax.text(0.3, 0.3, "A", color="#00aa00", fontsize=11)
        ax.text(w.goal[0] + 0.3, w.goal[1] + 0.3, "B", color="#dd0000", fontsize=11)
        ax.set_xlim(w.xmin - 0.3, w.xmax + 0.3)
        ax.set_ylim(w.ymin - 0.3, w.ymax + 0.3)
        ax.set_aspect("equal")
        ax.set_title(f"{fam} (seed {seed}, layout 0)\n{len(w.boxes)} boxes, {len(w.cylinders)} cylinders, "
                     f"{w.attempts} draw(s)", fontsize=9)
        ax.tick_params(labelsize=7)
    fig.suptitle("close-area-arena complex families (synthetic). Cyan = glass. Local frame, origin at A, m",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


def export_examples(out_dir: str, seed: int = 0) -> list[dict]:
    try:
        from . import world_json
    except ImportError:
        import world_json
    os.makedirs(out_dir, exist_ok=True)
    listing = []
    for fam in FAMILIES:
        d = world_json.to_json(make_world(fam, seed, 0))
        p = os.path.join(out_dir, f"{fam}_0.json")
        with open(p, "w") as fh:
            json.dump(d, fh, separators=(",", ":"))
        listing.append({"family": fam, "file": os.path.basename(p), "bytes": os.path.getsize(p),
                        "obstacles": len(d["obstacles"])})
    return listing


def sanity(layouts: int, seed: int) -> tuple[list[dict], float]:
    try:
        from . import run
    except ImportError:
        import run
    rows = []
    t_all = time.perf_counter()
    for fam in FAMILIES:
        for pname, kw in (("straight", {}), ("astar_esdf", {"known_map": True})):
            t0 = time.perf_counter()
            runs, s, _ = run.evaluate(lambda: run.load_planner(pname, **kw), fam, layouts, seed)
            att = [r["layout_attempts"] for r in runs]
            nob = [r["n_obstacles"] for r in runs]
            rows.append({"family": fam, "planner": pname + ("_known" if kw else ""), "summary": s,
                         "layout_attempts_median": float(np.median(att)), "layout_attempts_max": int(max(att)),
                         "n_obstacles_median": float(np.median(nob)), "wall_s": round(time.perf_counter() - t0, 1),
                         "runs": runs})
            print(f"{fam:13s} {rows[-1]['planner']:16s} reached {s['reached_pct']} % collision "
                  f"{s['collision_pct']} % median t {s['median_time_to_goal_s']} s ({rows[-1]['wall_s']} s)",
                  flush=True)
    return rows, time.perf_counter() - t_all


def sanity_table(rows) -> str:
    f = lambda v: "-" if v is None else f"{v}"
    out = ["| family | planner | reached % | collision % | stuck % | timeout % | median time to goal s "
           "| median obstacles | layout draws median / max |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        s = r["summary"]
        out.append(f"| {r['family']} | {r['planner']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} "
                   f"| {f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_time_to_goal_s'])} "
                   f"| {r['n_obstacles_median']:g} | {r['layout_attempts_median']:g} / {r['layout_attempts_max']} |")
    return "\n".join(out)


def _env():
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", action="store_true", help="write results/worlds_preview.png")
    ap.add_argument("--examples", action="store_true", help="write results/worlds_examples/<family>_0.json")
    ap.add_argument("--sanity", action="store_true", help="straight vs astar_esdf known on every family")
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    cmd = "python worlds_complex.py " + " ".join(argv if argv is not None else sys.argv[1:])
    if a.preview:
        p = os.path.join(RESULTS, "worlds_preview.png")
        preview(p, a.seed)
        print(f"wrote {p}")
    if a.examples:
        for e in export_examples(os.path.join(RESULTS, "worlds_examples"), a.seed):
            print(f"wrote worlds_examples/{e['file']}: {e['obstacles']} obstacles, {e['bytes']} bytes")
    if a.sanity:
        rows, wall = sanity(a.layouts, a.seed)
        tab = sanity_table(rows)
        stem = os.path.join(RESULTS, f"worlds_sanity_{a.seed}")
        with open(stem + ".json", "w") as fh:
            json.dump({"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts,
                       "wall_s": round(wall, 1), "env": _env(), "rows": rows}, fh, indent=1)
        with open(stem + ".md", "w") as fh:
            fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s\n\n{tab}\n")
        print(tab)
        print(f"wall {wall:.1f} s; wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
