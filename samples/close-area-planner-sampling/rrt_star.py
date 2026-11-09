"""RRT* and Informed RRT* on the arena's known inflated 0.1 m grid (numpy, own implementation).

Planner core (class RRTStar):
  - Uniform samples over the grid extent, GOAL_BIAS of them on B. Every sample counts as one
    iteration of the budget, including samples that land in an obstacle (rejected).
  - Steer at most STEP_M from the nearest node. Edge check: points every half cell on the
    segment against the blocked grid (outside the grid is blocked).
  - Choose parent and rewire within r = min(gamma * sqrt(log n / n), R_NEAR_MAX_M), gamma from
    the RRT* bound 2 * sqrt(1 + 1/d) * sqrt(free area / pi) with d = 2 (Karaman and Frazzoli 2011).
    Rewiring pushes the cost change down the subtree.
  - B is reached when a node lies within STEP_M of B with a free segment to it. The best such
    connection is the current solution c_best.
  - informed=True: once c_best is finite, samples are drawn uniformly from the ellipse with
    foci A and B and transverse diameter c_best (Gammell et al. 2014), clipped to the grid.
  - The whole budget is always used (anytime planner); the time to the first solution is kept.
Inflation: same rule as planners/astar_esdf: blocked = ESDF <= RADIUS + TRACK_MARGIN; when that
finds no path within the budget, one more budget at RADIUS only.
Shortcut: the tree path is densified to grid cells and passed to astar_esdf.shortcut, the same
clearance-keeping line-of-sight rule the A* baseline uses.
Follower (class RRTStarPlanner): subclass of astar_esdf.AStarESDF(known_map=True), so the carrot,
the speed-by-clearance law and the yaw law are the baseline's code. Only _plan differs: plan once,
keep the path while the vehicle stays within DEVIATE_M of it, replan otherwise, give up after
MAX_PLANS plans without a path (the vehicle then hovers and the scorer calls it stuck).
"""
from __future__ import annotations

import math
import time

import numpy as np

import arena

ast = arena.astar_esdf
RADIUS = ast.RADIUS
TRACK_MARGIN = ast.TRACK_MARGIN

STEP_M = 1.0              # m, max edge length when steering
R_NEAR_MAX_M = 2.0        # m, cap on the choose-parent / rewire radius
GOAL_BIAS = 0.05          # fraction of samples placed on B
DEVIATE_M = 0.6           # m, replan when the vehicle is farther than this from the path
MAX_PLANS = 5             # plans per run before the follower gives up


class RRTStar:
    """RRT* on a boolean blocked grid [ix, iy] with cell size res and corner (x0, y0)."""

    def __init__(self, blocked, res, x0, y0, rng, informed=False, step=STEP_M,
                 r_near_max=R_NEAR_MAX_M, goal_bias=GOAL_BIAS):
        self.blocked = blocked
        self.res, self.x0, self.y0 = res, x0, y0
        self.nx, self.ny = blocked.shape
        self.rng = rng
        self.informed = informed
        self.step = step
        self.r_near_max = r_near_max
        self.goal_bias = goal_bias
        free_area = float((~blocked).sum()) * res * res
        self.gamma = 2.0 * math.sqrt(1.5) * math.sqrt(free_area / math.pi)
        self.xmax = x0 + self.nx * res
        self.ymax = y0 + self.ny * res

    # ---- geometry ----
    def _pt_blocked(self, x, y) -> bool:
        ix = int((x - self.x0) // self.res)
        iy = int((y - self.y0) // self.res)
        if ix < 0 or iy < 0 or ix >= self.nx or iy >= self.ny:
            return True
        return bool(self.blocked[ix, iy])

    def _edges_free(self, a, B) -> np.ndarray:
        """a (2,), B (k, 2) => bool (k,) segment a => B[i] is free."""
        d = np.hypot(B[:, 0] - a[0], B[:, 1] - a[1])
        m = int(d.max() / (self.res / 2)) + 2 if len(d) else 2
        t = np.linspace(0.0, 1.0, m)
        X = a[0] + (B[:, 0:1] - a[0]) * t[None]
        Y = a[1] + (B[:, 1:2] - a[1]) * t[None]
        ix = np.floor((X - self.x0) / self.res).astype(np.int64)
        iy = np.floor((Y - self.y0) / self.res).astype(np.int64)
        inside = (ix >= 0) & (iy >= 0) & (ix < self.nx) & (iy < self.ny)
        hit = ~inside
        hit[inside] = self.blocked[ix[inside], iy[inside]]
        return ~hit.any(axis=1)

    def _sample(self, start, goal, c_best):
        if self.rng.random() < self.goal_bias:
            return goal
        if self.informed and math.isfinite(c_best):
            c_min = math.hypot(goal[0] - start[0], goal[1] - start[1])
            r1 = c_best / 2.0
            r2 = math.sqrt(max(c_best * c_best - c_min * c_min, 0.0)) / 2.0
            th = math.atan2(goal[1] - start[1], goal[0] - start[0])
            ang = self.rng.uniform(0.0, 2.0 * math.pi)
            rad = math.sqrt(self.rng.random())
            ux, uy = r1 * rad * math.cos(ang), r2 * rad * math.sin(ang)
            cx, cy = (start[0] + goal[0]) / 2.0, (start[1] + goal[1]) / 2.0
            return np.array([cx + ux * math.cos(th) - uy * math.sin(th),
                             cy + ux * math.sin(th) + uy * math.cos(th)])
        return np.array([self.rng.uniform(self.x0, self.xmax), self.rng.uniform(self.y0, self.ymax)])

    # ---- planner ----
    def plan(self, start, goal, iters: int) -> dict:
        t0 = time.perf_counter()
        start = np.asarray(start, float)
        goal = np.asarray(goal, float)
        N = iters + 1
        P = np.empty((N, 2))
        cost = np.empty(N)
        parent = np.full(N, -1, np.int64)
        children: list[list[int]] = [[] for _ in range(N)]
        P[0], cost[0], n = start, 0.0, 1
        goal_cand: dict[int, float] = {}      # node => free distance to B
        c_best, best_node = math.inf, -1
        first_iter, first_ms = None, None
        for it in range(1, iters + 1):
            q = self._sample(start, goal, c_best)
            if self._pt_blocked(q[0], q[1]):
                continue
            d2 = (P[:n, 0] - q[0]) ** 2 + (P[:n, 1] - q[1]) ** 2
            i_near = int(np.argmin(d2))
            dn = math.sqrt(d2[i_near])
            if dn < 1e-9:
                continue
            if dn > self.step:
                q = P[i_near] + (q - P[i_near]) * (self.step / dn)
                if self._pt_blocked(q[0], q[1]):
                    continue
            r = min(self.gamma * math.sqrt(math.log(n + 1) / (n + 1)), self.r_near_max)
            d2 = (P[:n, 0] - q[0]) ** 2 + (P[:n, 1] - q[1]) ** 2
            near = np.flatnonzero(d2 <= r * r)
            if i_near not in near:
                near = np.append(near, i_near)
            free = self._edges_free(q, P[near])
            if not free.any():
                continue
            near, dnear = near[free], np.sqrt(d2[near[free]])
            via = cost[near] + dnear
            k = int(np.argmin(via))
            j = n
            P[j], cost[j], parent[j] = q, via[k], near[k]
            children[near[k]].append(j)
            n += 1
            # rewire
            better = cost[j] + dnear < cost[near] - 1e-9
            for m_, dm in zip(near[better], dnear[better]):
                m_ = int(m_)
                if m_ == parent[j]:
                    continue
                children[parent[m_]].remove(m_)
                parent[m_] = j
                children[j].append(m_)
                delta = cost[j] + dm - cost[m_]
                stack = [m_]
                while stack:
                    u = stack.pop()
                    cost[u] += delta
                    stack.extend(children[u])
            # goal connection
            dg = math.hypot(goal[0] - q[0], goal[1] - q[1])
            if dg <= self.step and self._edges_free(q, goal[None])[0]:
                goal_cand[j] = dg
            if goal_cand:
                ids = np.fromiter(goal_cand.keys(), np.int64)
                tot = cost[ids] + np.fromiter(goal_cand.values(), float)
                kk = int(np.argmin(tot))
                c_best, best_node = float(tot[kk]), int(ids[kk])
                if first_iter is None:
                    first_iter, first_ms = it, (time.perf_counter() - t0) * 1e3
        out = {"ms": (time.perf_counter() - t0) * 1e3, "nodes": n, "first_iter": first_iter,
               "first_ms": first_ms, "cost": c_best if math.isfinite(c_best) else None, "path": None}
        if best_node >= 0:
            path = [goal]
            u = best_node
            while u != -1:
                path.append(P[u].copy())
                u = int(parent[u])
            out["path"] = np.array(path[::-1])
        return out


def densify_cells(path_xy, res, x0, y0, nx, ny):
    """Waypoints => list of grid cells along the polyline (consecutive duplicates removed)."""
    cells = []
    for a, b in zip(path_xy[:-1], path_xy[1:]):
        m = int(math.hypot(*(b - a)) / (res / 2)) + 2
        t = np.linspace(0.0, 1.0, m)
        ix = np.clip(np.floor((a[0] + (b[0] - a[0]) * t - x0) / res).astype(int), 0, nx - 1)
        iy = np.clip(np.floor((a[1] + (b[1] - a[1]) * t - y0) / res).astype(int), 0, ny - 1)
        for c in zip(ix.tolist(), iy.tolist()):
            if not cells or cells[-1] != c:
                cells.append(c)
    return cells


def path_length(xy) -> float:
    xy = np.asarray(xy)
    return float(np.hypot(*np.diff(xy, axis=0).T).sum()) if len(xy) > 1 else 0.0


def plan_on_grid(grid, esdf, start, goal, iters, rng, informed=False):
    """Two-level inflation like astar_esdf, then shortcut. Returns a dict with path_xy (or None),
    planning ms (both levels and the shortcut), fallback flag, first-solution stats."""
    t0 = time.perf_counter()
    res, x0, y0 = grid.res, grid.x0, grid.y0
    nx, ny = grid.occ.shape
    info = {"path_xy": None, "fallback": 0, "first_iter": None, "first_ms": None,
            "tree_cost": None, "iters": 0}
    for k, infl in enumerate((RADIUS + TRACK_MARGIN, RADIUS)):
        blocked = esdf <= infl + 1e-9
        s = np.asarray(start, float)
        si = (min(max(int((s[0] - x0) // res), 0), nx - 1), min(max(int((s[1] - y0) // res), 0), ny - 1))
        if blocked[si]:                       # inside the inflation: start from the nearest free cell
            free = np.argwhere(~blocked)
            c = free[int(np.argmin(np.hypot(free[:, 0] - si[0], free[:, 1] - si[1])))]
            s = np.array([x0 + (c[0] + 0.5) * res, y0 + (c[1] + 0.5) * res])
        t_level = time.perf_counter()
        r = RRTStar(blocked, res, x0, y0, rng, informed=informed).plan(s, goal[:2], iters)
        info["iters"] += iters
        if r["path"] is None:
            continue
        cells = densify_cells(r["path"], res, x0, y0, nx, ny)
        sc = ast.shortcut(cells, esdf, blocked)
        xy = np.array([(x0 + (c[0] + 0.5) * res, y0 + (c[1] + 0.5) * res) for c in sc])
        xy[0] = s
        xy[-1] = goal[:2]
        # first solution: counted from the start of plan_on_grid, so a burned first level is included
        info.update(path_xy=xy, dense_xy=r["path"], fallback=k, first_iter=r["first_iter"] + k * iters,
                    first_ms=(t_level - t0) * 1e3 + r["first_ms"], tree_cost=r["cost"])
        break
    info["ms"] = (time.perf_counter() - t0) * 1e3
    return info


class RRTStarPlanner(ast.AStarESDF):
    """astar_esdf's follower with an RRT* (or Informed RRT*) global plan on the known map."""

    def __init__(self, iters=2000, informed=False, seed=0):
        super().__init__(known_map=True)
        self.iters = iters
        self.informed = informed
        self.seed = seed
        self.name = f"{'informed_' if informed else ''}rrt_star_{iters}"
        self.runs = 0

    def reset(self) -> None:
        super().reset()
        self.plans = 0
        self.runs = getattr(self, "runs", 0) + 1

    def _plan(self, pose, goal, grid):
        _, esdf = self._layers(grid)
        self.esdf = esdf
        if self.path_xy is not None:
            d = np.hypot(self.dense_xy[:, 0] - pose.x, self.dense_xy[:, 1] - pose.y).min()
            if d <= DEVIATE_M:
                return                        # known static map: keep the path
        if self.plans >= MAX_PLANS:
            self.path_xy = self.dense_xy = None
            return
        rng = np.random.default_rng([self.seed, self.runs, self.plans, 20])
        self.plans += 1
        r = plan_on_grid(grid, esdf, (pose.x, pose.y), goal, self.iters, rng, self.informed)
        self.replan_ms.append(r["ms"])
        if r["path_xy"] is None:
            self.no_path += 1
            self.path_xy = self.dense_xy = None
        else:
            self.fallbacks += r["fallback"]
            self.path_xy = r["path_xy"]
            # densified shortcut path, for the deviation check
            pts = [self.path_xy[0]]
            for a, b in zip(self.path_xy[:-1], self.path_xy[1:]):
                m = int(math.hypot(*(b - a)) / 0.1) + 1
                pts.extend(a + (b - a) * t for t in np.linspace(0, 1, m + 1)[1:])
            self.dense_xy = np.array(pts)


def make(iters=2000, informed=False, seed=0, **kw):
    return RRTStarPlanner(iters=iters, informed=informed, seed=seed)
