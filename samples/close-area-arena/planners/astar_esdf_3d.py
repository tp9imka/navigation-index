"""3D grid planner: A* on a 0.1 m OccGrid3 (world_z.py) with an ESDF clearance cost.

Known map only (uses_grid = True: the run passes the prior OccGrid3). Same structure as
planners/astar_esdf.py, one dimension up:
  1. ESDF = scipy distance_transform_edt over the 3D occupancy (outside the grid, i.e. walls,
     floor and ceiling, counts as occupied). Computed once per run: the map is static.
  2. Blocked = ESDF <= RADIUS + TRACK_MARGIN. If A* finds no path, retry with RADIUS only.
  3. 26-connected A*, step cost = length * (1 + CLEARANCE_WEIGHT * max(0, 1 - esdf / CLEARANCE_SOFT_M)).
     Heuristic = max(3D octile distance, geodesic distance on a 2x coarser grid) times
     HEURISTIC_WEIGHT (weighted A*, 2.0). The coarse geodesic (scipy csgraph Dijkstra, once per
     run) points the search at the window instead of flooding the wall face.
  4. Forward greedy line-of-sight shortcut: extend each segment while the straight line keeps the
     clearance of the A* sub-path it replaces (capped at SHORTCUT_CLEAR_M).
Follower: carrot LOOKAHEAD_M ahead along the 3D path, pulled back while the chord passes closer than
CARROT_CLEAR_M; speed scaled by the chord ESDF and capped by K_GOAL * 3D distance to B; the
velocity vector is scaled down so |vz| <= VZ_CMD_MAX. Replans when the vehicle is more than
REPLAN_DEVIATION_M from the dense path, or every NO_PATH_RETRY_S while it has no path.

Plan/compare: .venv/bin/python run_z.py --layouts 50 --seed 0
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np
from scipy.ndimage import distance_transform_edt

try:
    from ..adapter import Setpoint
    from .base import Planner
except ImportError:
    from adapter import Setpoint
    from planners.base import Planner

# ---- vehicle and inflation ----
RADIUS = 0.15                 # m, vehicle radius (CONTRACT.md)
TRACK_MARGIN = 0.05           # m, extra inflation (0.10 in 2D leaves no free cell in a 0.6 m window)
# ---- costs ----
CLEARANCE_WEIGHT = 4.0        # extra cost per metre at zero clearance
CLEARANCE_SOFT_M = 0.8        # m, ESDF above which the clearance cost is zero
HEURISTIC_WEIGHT = 2.0        # weighted A*: cost <= 2x optimal (if h is a lower bound). 1.0 is far slower
SHORTCUT_CLEAR_M = 0.5        # m, a shortcut segment must keep min(this, sub-path clearance)
# ---- replanning ----
REPLAN_DEVIATION_M = 0.35     # m, distance from the dense path that triggers a replan
NO_PATH_RETRY_S = 1.0         # s
# ---- follower ----
LOOKAHEAD_M = 0.8
LOOKAHEAD_MIN_M = 0.2
LOOKAHEAD_STEP_M = 0.1
CARROT_CLEAR_M = RADIUS + 0.10   # m, chord ESDF the follower keeps; above the planning inflation
                                 # because the grid ESDF can read up to ~0.09 m above the true clearance
V_CRUISE = 1.5                # m/s, 3D speed
V_CLEAR_STOP_M = 0.2          # m, ESDF at which speed is V_MIN_FRAC * V_CRUISE
V_CLEAR_FULL_M = 0.8          # m, ESDF at which speed is V_CRUISE
V_MIN_FRAC = 0.2
VZ_CMD_MAX = 0.8              # m/s, below the vehicle's 1.0 m/s vz limit so direction is kept
K_GOAL = 1.0                  # 1/s
K_YAW = 1.5                   # 1/s

COARSE_FACTOR = 2             # heuristic from a geodesic on a 2x coarser grid; 1 = octile only

S2, S3 = math.sqrt(2.0), math.sqrt(3.0)


def _coarse_geodesic(free: np.ndarray, goal: tuple, f: int) -> np.ndarray:
    """Heuristic in fine-cell units: 26-connected geodesic distance to the goal on a grid f times
    coarser, where a coarse cell is free when any of its fine cells is free (optimistic), minus
    f * sqrt(3) for the fine-to-coarse offset at both ends, floored at 0. scipy csgraph Dijkstra
    (C code), once per run. Unreachable cells get a large value."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    nx, ny, nz = (s // f for s in free.shape)
    fr = free[:nx * f, :ny * f, :nz * f].reshape(nx, f, ny, f, nz, f).any(axis=(1, 3, 5))
    ids = np.arange(nx * ny * nz).reshape(nx, ny, nz)
    rows, cols, w = [], [], []
    for dx, dy, dz in [(1, -1, -1), (1, -1, 0), (1, -1, 1), (1, 0, -1), (1, 0, 0), (1, 0, 1), (1, 1, -1),
                       (1, 1, 0), (1, 1, 1), (0, 1, -1), (0, 1, 0), (0, 1, 1), (0, 0, 1)]:
        def sl(d, n):
            return (slice(0, n - d), slice(d, n)) if d >= 0 else (slice(-d, n), slice(0, n + d))
        (ax, bx), (ay, by), (az, bz) = sl(dx, nx), sl(dy, ny), sl(dz, nz)
        m = fr[ax, ay, az] & fr[bx, by, bz]
        rows.append(ids[ax, ay, az][m])
        cols.append(ids[bx, by, bz][m])
        w.append(np.full(int(m.sum()), f * math.sqrt(dx * dx + dy * dy + dz * dz)))
    n = nx * ny * nz
    g = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()
    gc = tuple(min(goal[i] // f, (nx, ny, nz)[i] - 1) for i in range(3))
    dist = dijkstra(g, directed=False, indices=int(ids[gc]))
    dist = np.where(np.isfinite(dist), np.maximum(dist - f * S3, 0.0), 1e6).reshape(nx, ny, nz)
    out = np.zeros(free.shape)
    out[:nx * f, :ny * f, :nz * f] = dist.repeat(f, 0).repeat(f, 1).repeat(f, 2)
    return out


def astar3(blocked_pad: np.ndarray, cost_pad: list, h_pad: list, start: int, goal: int):
    """26-connected A* on a padded grid (border cells blocked, so no bounds checks).
    blocked_pad: bool array (NX, NY, NZ). cost_pad, h_pad: flat lists. start/goal: flat indices.
    Returns (list of flat indices start => goal or None, expansions)."""
    NX, NY, NZ = blocked_pad.shape
    closed = bytearray(blocked_pad.ravel().tobytes())   # blocked cells start closed
    if closed[goal]:
        return None, 0
    nbrs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                k = abs(dx) + abs(dy) + abs(dz)
                if k:
                    nbrs.append(((dx * NY + dy) * NZ + dz, (1.0, S2, S3)[k - 1]))
    gs = {start: 0.0}
    parent = {start: -1}
    heap = [(h_pad[start], 0.0, start)]
    push, pop = heapq.heappush, heapq.heappop
    inf = math.inf
    n_exp = 0
    while heap:
        _, gc, u = pop(heap)
        if u == goal:
            path = []
            while u != -1:
                path.append(u)
                u = parent[u]
            return path[::-1], n_exp
        if closed[u]:
            continue
        closed[u] = 1
        n_exp += 1
        for off, ln in nbrs:
            v = u + off
            if closed[v]:
                continue
            ng = gc + ln * cost_pad[v]
            if ng < gs.get(v, inf):
                gs[v] = ng
                parent[v] = u
                push(heap, (ng + h_pad[v], ng, v))
    return None, n_exp


class AStarESDF3D(Planner):
    name = "astar_esdf_3d"
    uses_grid = True

    def __init__(self):
        self.replan_ms: list[float] = []
        self.setup_ms: list[float] = []       # ESDF + cost/heuristic arrays, once per run
        self.expansions: list[int] = []
        self.fallbacks = 0
        self.no_path = 0
        self.reset()

    def reset(self) -> None:
        self.static = None
        self.path_xyz = None
        self.dense_xyz = None
        self.last_plan_t = -math.inf

    # ---- map ----
    def _prepare(self, grid, goal):
        t0 = time.perf_counter()
        padded = np.pad(grid.occ, 1, constant_values=True)
        esdf_pad = distance_transform_edt(~padded) * grid.res
        esdf_pad[0, :, :] = esdf_pad[-1, :, :] = 0.0
        esdf_pad[:, 0, :] = esdf_pad[:, -1, :] = 0.0
        esdf_pad[:, :, 0] = esdf_pad[:, :, -1] = 0.0
        cost = 1.0 + CLEARANCE_WEIGHT * np.clip(1.0 - esdf_pad / CLEARANCE_SOFT_M, 0.0, None)
        NX, NY, NZ = padded.shape
        gi = self._pidx_raw(goal, grid, (NX, NY, NZ))
        ix, iy, iz = np.meshgrid(np.arange(NX), np.arange(NY), np.arange(NZ), indexing="ij", sparse=True)
        d = np.sort(np.stack(np.broadcast_arrays(np.abs(ix - gi[0]), np.abs(iy - gi[1]),
                                                 np.abs(iz - gi[2])), axis=-1), axis=-1)
        h = S3 * d[..., 0] + S2 * (d[..., 1] - d[..., 0]) + (d[..., 2] - d[..., 1])
        if COARSE_FACTOR > 1:
            hc = _coarse_geodesic(esdf_pad[1:-1, 1:-1, 1:-1] > RADIUS + 1e-9,
                                  tuple(g - 1 for g in gi), COARSE_FACTOR)
            hp = np.zeros_like(h)
            hp[1:-1, 1:-1, 1:-1] = hc
            h = np.maximum(h, hp)
        h = h * HEURISTIC_WEIGHT
        self.static = {"esdf": esdf_pad, "cost": cost.ravel().tolist(), "h": h.ravel().tolist(),
                       "shape": (NX, NY, NZ), "res": grid.res, "origin": (grid.x0, grid.y0, grid.z0),
                       "goal": gi}
        self.setup_ms.append((time.perf_counter() - t0) * 1e3)

    @staticmethod
    def _pidx_raw(p, grid, shape):
        o = (grid.x0, grid.y0, grid.z0)
        return tuple(min(max(int((p[i] - o[i]) // grid.res) + 1, 1), shape[i] - 2) for i in range(3))

    def _pidx(self, p):
        s = self.static
        o, res, shape = s["origin"], s["res"], s["shape"]
        return tuple(min(max(int((p[i] - o[i]) // res) + 1, 1), shape[i] - 2) for i in range(3))

    def _xyz(self, c):
        s = self.static
        o, res = s["origin"], s["res"]
        return tuple(o[i] + (c[i] - 1 + 0.5) * res for i in range(3))

    # ---- planning ----
    def _plan(self, pose, goal, grid):
        if self.static is None:
            self._prepare(grid, goal)
        t0 = time.perf_counter()
        s = self.static
        esdf = s["esdf"]
        NX, NY, NZ = s["shape"]
        flat = lambda c: (c[0] * NY + c[1]) * NZ + c[2]
        path = None
        exp_total = 0
        for k, infl in enumerate((RADIUS + TRACK_MARGIN, RADIUS)):
            blocked = esdf <= infl + 1e-9
            st = self._pidx((pose.x, pose.y, pose.z))
            if blocked[st]:
                free = np.argwhere(~blocked)
                if not len(free):
                    continue
                dd = ((free - np.array(st)) ** 2).sum(1)
                st = tuple(int(v) for v in free[int(np.argmin(dd))])
            path, n_exp = astar3(blocked, s["cost"], s["h"], flat(st), flat(s["goal"]))
            exp_total += n_exp
            if path is not None:
                self.fallbacks += k
                break
        self.expansions.append(exp_total)
        if path is None:
            self.no_path += 1
            self.path_xyz = self.dense_xyz = None
        else:
            cells = [(u // (NY * NZ), (u // NZ) % NY, u % NZ) for u in path]
            sc = self._shortcut(cells, esdf, blocked)
            self.path_xyz = np.array([self._xyz(c) for c in sc])
            self.path_xyz[-1] = goal
            self.dense_xyz = np.array([self._xyz(c) for c in cells])
        self.replan_ms.append((time.perf_counter() - t0) * 1e3)

    @staticmethod
    def _seg(a, b):
        n = int(max(abs(b[i] - a[i]) for i in range(3)) * 2) + 1
        t = np.linspace(0.0, 1.0, n + 1)
        return tuple(np.rint(a[i] + (b[i] - a[i]) * t).astype(int) for i in range(3))

    def _shortcut(self, cells, esdf, blocked):
        if len(cells) <= 2:
            return list(cells)
        pe = np.array([esdf[c] for c in cells])
        out, i, n = [cells[0]], 0, len(cells)
        while i < n - 1:
            j = i + 1
            while j + 1 < n:
                need = min(SHORTCUT_CLEAR_M, float(pe[i:j + 2].min()))
                xs, ys, zs = self._seg(cells[i], cells[j + 1])
                if blocked[xs, ys, zs].any() or esdf[xs, ys, zs].min() < need - 1e-9:
                    break
                j += 1
            out.append(cells[j])
            i = j
        return out

    # ---- following ----
    def _min_esdf(self, p0, p1) -> float:
        s = self.static
        o, res, shape = s["origin"], s["res"], s["shape"]
        L = math.dist(p0, p1)
        t = np.linspace(0, 1, int(L / (res / 2)) + 2)
        idx = [np.clip(((p0[i] + (p1[i] - p0[i]) * t - o[i]) // res).astype(int) + 1, 1, shape[i] - 2)
               for i in range(3)]
        return float(s["esdf"][idx[0], idx[1], idx[2]].min())

    def _carrot_at(self, p, look):
        P = self.path_xyz
        if len(P) == 1:
            return P[0]
        a, b = P[:-1], P[1:]
        ab = b - a
        L = np.maximum((ab ** 2).sum(1), 1e-12)
        t = np.clip(((p - a) * ab).sum(1) / L, 0, 1)
        q = a + t[:, None] * ab
        i = int(np.argmin(np.linalg.norm(q - p, axis=1)))
        left, pt = look, q[i]
        while i < len(P) - 1:
            seg = float(np.linalg.norm(P[i + 1] - pt))
            if seg >= left:
                return pt + (P[i + 1] - pt) * (left / max(seg, 1e-9))
            left -= seg
            pt, i = P[i + 1], i + 1
        return P[-1]

    def _carrot(self, p):
        need = min(CARROT_CLEAR_M, self._min_esdf(p, p))
        look = LOOKAHEAD_M
        while True:
            c = self._carrot_at(p, look)
            if look <= LOOKAHEAD_MIN_M or self._min_esdf(p, c) >= need - 1e-9:
                return c
            look -= LOOKAHEAD_STEP_M

    def step(self, pose, scan, goal, grid, dt):
        p = np.array([pose.x, pose.y, pose.z])
        if self.dense_xyz is None:
            due = pose.t - self.last_plan_t >= NO_PATH_RETRY_S - 1e-9
        else:
            due = float(np.linalg.norm(self.dense_xyz - p, axis=1).min()) > REPLAN_DEVIATION_M
        if due:
            self._plan(pose, goal, grid)
            self.last_plan_t = pose.t
        if self.path_xyz is None:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        c = self._carrot(p)
        e = c - p
        dc = float(np.linalg.norm(e))
        if dc < 1e-6:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        clr = self._min_esdf(p, c)
        frac = (clr - V_CLEAR_STOP_M) / (V_CLEAR_FULL_M - V_CLEAR_STOP_M)
        speed = V_CRUISE * min(1.0, max(V_MIN_FRAC, frac))
        speed = min(speed, K_GOAL * math.dist(p, goal))
        v = e / dc * speed
        if abs(v[2]) > VZ_CMD_MAX:
            v *= VZ_CMD_MAX / abs(v[2])
        yaw_rate = 0.0
        if math.hypot(e[0], e[1]) > 0.05:
            h = math.atan2(e[1], e[0])
            yaw_rate = K_YAW * ((h - pose.yaw + math.pi) % (2 * math.pi) - math.pi)
        return Setpoint(float(v[0]), float(v[1]), float(v[2]), yaw_rate)


def make(**kw) -> Planner:
    return AStarESDF3D(**kw)
