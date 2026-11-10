"""Theta* and Lazy Theta* (any-angle A*) on the same grid and cost model as the arena's astar_esdf.

Search (function theta_star), on the flat [ix * ny + iy] grid astar_esdf uses:
  - 8-connected expansion, neighbour step u => v costs step_length * cost[v] (astar_esdf's edge).
  - Theta* (Daniel, Nash, Koenig, Felner 2010): when v is generated from u, also try the
    any-angle edge parent(u) => v. With a cost field the any-angle edge is priced by the same
    rule: the segment is sampled every half cell, and its cost is length * mean cost of the
    sampled cells. It must not touch a blocked cell. The cheaper of the two edges wins, so the
    clearance cost still pushes the path away from walls (plain Theta* minimises length only).
  - Lazy Theta* (lazy=True, Nash, Koenig, Tovey 2010): the parent(u) => v edge is taken on trust
    with an estimated cost (length * mean of the two end-cell costs) and checked only when v is
    expanded. If the segment is blocked or a closed neighbour gives a cheaper path, v gets that
    neighbour as parent. One line check per expansion instead of one per generated neighbour.
  - Heuristic: Euclidean distance in cells (admissible: every cell costs >= 1 per cell length).
Around the search (class ThetaStarESDF), everything is astar_esdf's own code or a copy of its
_plan: the ESDF, the cost 1 + CLEARANCE_WEIGHT * max(0, 1 - esdf / CLEARANCE_SOFT_M) (+ the
unknown-cell penalty on the unknown map), the two inflation levels (RADIUS + TRACK_MARGIN, then
RADIUS only), the replan schedule, the log-odds map, the carrot follower, the speed and yaw laws.
The one difference: no post-hoc shortcut. The Theta* vertices are the path.

make()                                 => Theta*, known map (same default as astar_esdf.make()).
make(lazy=True)                        => Lazy Theta*.
make(known_map=False, bounds=(xmin, ymin, xmax, ymax))
                                       => unknown map with the log-odds map corner on the area
                                          bounds - 2 m, as close-area-benchmark's astar_unknown.
numpy + scipy only (runs in Pyodide).
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np
from scipy.ndimage import distance_transform_edt

try:
    from . import arena
except ImportError:
    import arena

A = arena.astar_esdf
SQRT2 = math.sqrt(2.0)
INF = math.inf
UNIFORM_MIN_FRAC = 0.01      # cost values covering at least this share of cells get uniform discs
GEOFENCE_MARGIN_M = 2.0       # m, map corner = area corner - this (close-area-benchmark GeofencedAStar)


def _line_cost(cb, ny, ax, ay, bx, by):
    """Cost of the straight segment from cell (ax, ay) to cell (bx, by): length (cells) times the
    mean of cb over samples every half cell (start cell excluded). INF if a sample is blocked."""
    dx, dy = bx - ax, by - ay
    m = 2 * max(abs(dx), abs(dy))
    if m == 0:
        return 0.0
    sx, sy = dx / m, dy / m
    x, y = ax + 0.5, ay + 0.5            # int(x) of a positive x is floor: nearest cell centre
    s = 0.0
    for _ in range(m):
        x += sx
        y += sy
        c = cb[int(x) * ny + int(y)]
        if c == INF:
            return INF
        s += c
    return s * math.hypot(dx, dy) / m


def theta_star(blocked: np.ndarray, cost: np.ndarray, start, goal, lazy: bool = False,
               stats: dict | None = None):
    """Theta* (lazy=False) or Lazy Theta* (lazy=True) on cell grids [ix, iy]. cost >= 1 per cell.
    Returns the list of path vertices (ix, iy) from start to goal, or None. stats (optional dict)
    gets expansions, line checks and the path cost (same units as astar_esdf: cells x cost)."""
    nx, ny = blocked.shape
    cb_arr = np.where(blocked, INF, cost).astype(float)
    cb_arr[0, :] = cb_arr[-1, :] = INF   # ring blocked => neighbours of free cells are in the grid
    cb_arr[:, 0] = cb_arr[:, -1] = INF
    cb = cb_arr.ravel().tolist()
    # Uniform-cost discs, an exact speed-up: for each cost value that covers >= UNIFORM_MIN_FRAC of
    # the grid (1.0 = free and far from walls; 1 + UNKNOWN_PENALTY = unknown and far from walls), rd
    # is the distance (cells) from a cell of that value to the nearest cell with another value. A
    # segment between two cells of the same value, covered by their two discs, costs value x length
    # without walking it (_line_cost would return the same number).
    rd_arr = np.zeros(cb_arr.shape)
    vals, counts = np.unique(cb_arr[np.isfinite(cb_arr)], return_counts=True)
    for v in vals[counts >= UNIFORM_MIN_FRAC * cb_arr.size][:3]:
        m = cb_arr == v
        rd_arr[m] = distance_transform_edt(m)[m]
    rd = rd_arr.ravel().tolist()
    s = start[0] * ny + start[1]
    g_ = goal[0] * ny + goal[1]
    gx, gy = goal
    if cb[g_] == INF or cb[s] == INF:
        return None
    nbrs = [(-ny - 1, -1, -1, SQRT2), (-ny, -1, 0, 1.0), (-ny + 1, -1, 1, SQRT2), (-1, 0, -1, 1.0),
            (1, 0, 1, 1.0), (ny - 1, 1, -1, SQRT2), (ny, 1, 0, 1.0), (ny + 1, 1, 1, SQRT2)]
    n = nx * ny
    g = [INF] * n
    par = [-1] * n
    closed = bytearray(n)
    unchecked = bytearray(n)             # lazy: parent edge not yet line-checked
    g[s], par[s] = 0.0, s
    heap = [(math.hypot(start[0] - gx, start[1] - gy), s)]
    push, pop, hypot = heapq.heappush, heapq.heappop, math.hypot
    expansions = lines = 0
    while heap:
        _, u = pop(heap)
        if closed[u]:
            continue
        ux, uy = divmod(u, ny)
        if lazy and unchecked[u]:        # SetVertex: verify the trusted parent edge
            unchecked[u] = 0
            p = par[u]
            px, py = divmod(p, ny)
            d = hypot(ux - px, uy - py)
            cu = cb[u]
            if cb[p] == cu and d + 2.0 <= rd[p] + rd[u]:
                best, bp = g[p] + cu * d, p
            else:
                lines += 1
                best, bp = g[p] + _line_cost(cb, ny, px, py, ux, uy), p
            for off, _, _, ln in nbrs:
                w = u + off
                if closed[w]:
                    c1 = g[w] + ln * cu
                    if c1 < best:
                        best, bp = c1, w
            g[u], par[u] = best, bp
        closed[u] = 1
        expansions += 1
        if u == g_:
            path = []
            while True:
                path.append(divmod(u, ny))
                if par[u] == u:
                    break
                u = par[u]
            if stats is not None:
                stats.update(expansions=expansions, lines=lines, cost=g[g_])
            return path[::-1]
        gu = g[u]
        pu = par[u]
        pux, puy = divmod(pu, ny)
        gpu = g[pu]
        cpu = cb[pu]
        for off, dx, dy, ln in nbrs:
            v = u + off
            cv = cb[v]
            if cv == INF or closed[v]:
                continue
            vx, vy = ux + dx, uy + dy
            best, bp, trust = gu + ln * cv, u, 0
            if pu != u:
                if lazy:
                    est = gpu + hypot(vx - pux, vy - puy) * 0.5 * (cpu + cv)
                    if est < best:
                        best, bp, trust = est, pu, 1
                else:
                    d = hypot(vx - pux, vy - puy)
                    if gpu + d < best and gpu + d < g[v]:      # else the line cannot win (cost >= length)
                        if cpu == cv and d + 2.0 <= rd[pu] + rd[v]:
                            c2 = gpu + cv * d                # inside two uniform discs: exact, no walk
                        else:
                            lines += 1
                            c2 = gpu + _line_cost(cb, ny, pux, puy, vx, vy)
                        if c2 < best:
                            best, bp = c2, pu
            if best < g[v]:
                g[v], par[v], unchecked[v] = best, bp, trust
                push(heap, (best + hypot(vx - gx, vy - gy), v))
    if stats is not None:
        stats.update(expansions=expansions, lines=lines, cost=None)
    return None


def densify(cells):
    """Path vertices => every cell along the segments (sampled every half cell), for the follower's
    "new obstacle touches the path" check and for comparing clearance."""
    out = [tuple(cells[0])]
    for a, b in zip(cells[:-1], cells[1:]):
        xs, ys = A._segment_cells(a, b)
        for c in zip(xs.tolist(), ys.tolist()):
            if c != out[-1]:
                out.append(c)
    return out


def path_cost(cells, cost: np.ndarray, blocked: np.ndarray) -> float:
    """Any polyline of cells priced the way theta_star prices it (cells x cost): a one-cell step by
    astar_esdf's edge rule, a longer segment by _line_cost. So A* + shortcut and Theta* paths
    compare on one scale. INF if a segment touches a blocked cell."""
    cb_arr = np.where(blocked, INF, cost).astype(float)
    cb = cb_arr.ravel().tolist()
    ny = blocked.shape[1]
    total = 0.0
    for a, b in zip(cells[:-1], cells[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if max(abs(dx), abs(dy)) == 1:       # one 8-neighbour step: astar_esdf's edge rule
            total += math.hypot(dx, dy) * cb[b[0] * ny + b[1]]
        else:
            total += _line_cost(cb, ny, a[0], a[1], b[0], b[1])
    return float(total)


class ThetaStarESDF(A.AStarESDF):
    """astar_esdf with the A* + shortcut global path replaced by a Theta* / Lazy Theta* path."""

    def __init__(self, known_map: bool = True, lazy: bool = False, bounds=None,
                 margin: float = GEOFENCE_MARGIN_M):
        self.lazy = lazy
        self.bounds, self.margin = bounds, margin
        self.search_ms: list[float] = []
        self.search_stats: list[dict] = []
        super().__init__(known_map=known_map)
        self.name = f"{'lazy_' if lazy else ''}thetastar_{'known' if known_map else 'unknown'}"

    def reset(self) -> None:
        super().reset()
        if self.map is not None and self.bounds is not None:
            self.map.x0 = self.bounds[0] - self.margin
            self.map.y0 = self.bounds[1] - self.margin

    def _plan(self, pose, goal, grid):
        t0 = time.perf_counter()
        unknown, esdf = self._layers(grid)
        self.esdf = esdf
        cost = 1.0 + A.CLEARANCE_WEIGHT * np.clip(1.0 - esdf / A.CLEARANCE_SOFT_M, 0.0, None)
        cost = cost + A.UNKNOWN_PENALTY * unknown
        g = self._idx(goal[0], goal[1])
        path = None
        search = 0.0
        st: dict = {}
        for k, infl in enumerate((A.RADIUS + A.TRACK_MARGIN, A.RADIUS)):
            blocked = esdf <= infl + 1e-9
            s = self._idx(pose.x, pose.y)
            if blocked[s]:                    # inside the inflation: start from the nearest free cell
                free = np.argwhere(~blocked)
                if not len(free):
                    continue
                dd = np.hypot(free[:, 0] - s[0], free[:, 1] - s[1])
                s = tuple(int(v) for v in free[int(np.argmin(dd))])
            ts = time.perf_counter()
            path = theta_star(blocked, cost, s, g, lazy=self.lazy, stats=st)
            search += time.perf_counter() - ts
            if path is not None:
                self.fallbacks += k
                break
        if path is None:
            self.no_path += 1
            self.path_xy = self.dense_xy = None
        else:
            self.path_xy = np.array([self._xy(c) for c in path])
            self.path_xy[-1] = goal[:2]
            self.dense_xy = np.array([self._xy(c) for c in densify(path)])
        self.replan_ms.append((time.perf_counter() - t0) * 1e3)
        self.search_ms.append(search * 1e3)
        self.search_stats.append(st)


def make(known_map: bool = True, lazy: bool = False, bounds=None, **kw) -> ThetaStarESDF:
    return ThetaStarESDF(known_map=known_map, lazy=lazy, bounds=bounds)
