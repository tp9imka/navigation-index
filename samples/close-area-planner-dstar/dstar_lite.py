"""D* Lite (Koenig and Likhachev 2002) on the same grid and cost model as astar_esdf's unknown-map mode.

The planner subclasses close-area-arena's AStarESDF(known_map=False) and keeps everything except the
search: the log-odds map from range returns, the ESDF, the inflation (RADIUS + TRACK_MARGIN, then
RADIUS-only fallback), the cost (1 + clearance term + unknown penalty), the replan schedule
(REPLAN_PERIOD_S plus "new obstacle touches the path"), the shortcut and the carrot follower.

backend="astar"  => astar_esdf.astar from scratch every replan (the baseline, same code path).
backend="dstar"  => one DStarLite per inflation level, kept across replans. Each replan diffs the
                    new blocked / cost arrays against the ones the search last saw and updates only
                    the changed cells and their 8 neighbours, then repairs the search.
verify=True      => with backend="dstar", also run A* from scratch on the same arrays at every
                    replan and log both path costs (doubles search time; for correctness only).

Edge model (identical to astar_esdf.astar): 8-connected, moving u => v costs step_length * cost[v],
v must not be blocked, diagonal moves do not check the two orthogonal cells. D* Lite searches
backwards from B, so g[s] is the cost-to-go from s; h is the octile distance to the vehicle cell.
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np

try:
    from . import arena
except ImportError:
    import arena

A = arena.astar_esdf
SQRT2 = math.sqrt(2.0)
INF = math.inf
KEY_EPS = 1e-9                # relative tolerance for k1 ties in the termination test; None = strict


class DStarLite:
    """Backward D* Lite on a flat [ix * ny + iy] grid. Goal fixed for the object's life.

    Invariant used to skip bounds checks: the outermost cell ring is always blocked (astar_esdf's
    ESDF pads the map with occupied cells, so ring 0 has ESDF 0.1 m <= both inflations). Blocked
    cells never get a finite g and update_vertex never looks at their neighbours."""

    def __init__(self, shape, goal):
        self.nx, self.ny = shape
        ny = self.ny
        self.goal = goal[0] * ny + goal[1]
        self.gx, self.gy = goal
        n = self.nx * ny
        self.g = [INF] * n
        self.rhs = [INF] * n
        self.blk = None
        self.cst = None
        self.prev_blk = None
        self.prev_cost = None
        self.heap = []
        self.key_of = {}
        self.km = 0.0
        self.start = None
        self.last = None
        self.nbrs = [(-ny - 1, SQRT2), (-ny, 1.0), (-ny + 1, SQRT2), (-1, 1.0),
                     (1, 1.0), (ny - 1, SQRT2), (ny, 1.0), (ny + 1, SQRT2)]
        # stats of the last plan() call
        self.changed = 0
        self.updated = 0
        self.pops = 0

    # ---- helpers ----
    def _h(self, u):
        ux, uy = divmod(u, self.ny)
        sx, sy = self.sxy
        ax, ay = abs(ux - sx), abs(uy - sy)
        return (ax + ay) + (SQRT2 - 2.0) * min(ax, ay)

    def _key(self, u):
        m = min(self.g[u], self.rhs[u])
        return (m + self._h(u) + self.km, m)

    def _queue(self, u):
        if self.g[u] != self.rhs[u]:
            k = self._key(u)
            self.key_of[u] = k
            heapq.heappush(self.heap, (k[0], k[1], u))
        else:
            self.key_of.pop(u, None)

    def _update_vertex(self, u):
        if u != self.goal:
            if self.blk[u]:
                self.rhs[u] = INF
            else:
                g, cst, blk = self.g, self.cst, self.blk
                best = INF
                for off, ln in self.nbrs:
                    v = u + off
                    if not blk[v]:
                        c = ln * cst[v] + g[v]
                        if c < best:
                            best = c
                self.rhs[u] = best
        self._queue(u)

    # ---- map changes ----
    def _apply(self, blocked: np.ndarray, cost: np.ndarray):
        if self.prev_blk is None:
            assert blocked[0, :].all() and blocked[-1, :].all() and blocked[:, 0].all() and blocked[:, -1].all()
            self.blk = blocked.ravel().tolist()
            self.cst = cost.ravel().tolist()
            self.prev_blk, self.prev_cost = blocked.copy(), cost.copy()
            self.rhs[self.goal] = 0.0
            self._queue(self.goal)
            self.changed = self.updated = int(blocked.size)
            return
        dblk = blocked != self.prev_blk
        dcost = cost != self.prev_cost
        idx = np.flatnonzero(dblk | dcost)
        if len(idx):
            bl, cl = blocked.ravel(), cost.ravel()
            for i, b, c in zip(idx.tolist(), bl[idx].tolist(), cl[idx].tolist()):
                self.blk[i] = b
                self.cst[i] = c
        trig = dblk | (dcost & ~blocked)
        self.changed = int(trig.sum())
        if self.changed:
            # changed cells plus their 8 neighbours (edges into a changed cell come from them)
            aff = trig.copy()
            aff[1:, :] |= trig[:-1, :]
            aff[:-1, :] |= trig[1:, :]
            aff[:, 1:] |= aff[:, :-1].copy()
            aff[:, :-1] |= aff[:, 1:].copy()
            upd = np.flatnonzero(aff).tolist()
            for u in upd:
                self._update_vertex(u)
            self.updated = len(upd)
        else:
            self.updated = 0
        self.prev_blk, self.prev_cost = blocked.copy(), cost.copy()

    # ---- search ----
    def _compute(self):
        heap, key_of, g, rhs, blk, cst = self.heap, self.key_of, self.g, self.rhs, self.blk, self.cst
        s, goal, nbrs = self.start, self.goal, self.nbrs
        pop, push = heapq.heappop, heapq.heappush
        pops = 0
        eps = KEY_EPS
        while True:
            while heap and key_of.get(heap[0][2]) != (heap[0][0], heap[0][1]):
                pop(heap)                                     # stale entry (lazy deletion)
            m = min(g[s], rhs[s])
            ks = (m + self.km, m)
            if not heap:
                break
            k1, k2, u = heap[0]
            # Keys that are equal in exact arithmetic can differ by an ulp (h + g summed in another
            # order), and a strict "top < key(start)" then stops one tie early with a stale g on the
            # path. Treat k1 within KEY_EPS (relative) as a tie and keep expanding ties.
            if eps is None:                                   # textbook test (kept for the fuzz demo)
                go = (k1, k2) < ks
            else:
                go = ks[0] == INF or k1 <= ks[0] * (1.0 + eps) + eps
            if not (go or rhs[s] != g[s]):
                break
            pop(heap)
            pops += 1
            knew = self._key(u)
            if (k1, k2) < knew:
                key_of[u] = knew
                push(heap, (knew[0], knew[1], u))
                continue
            del key_of[u]
            if g[u] > rhs[u]:                                 # over-consistent: settle u
                g[u] = gu = rhs[u]
                cu = cst[u]
                for off, ln in nbrs:
                    p = u + off
                    if p != goal and not blk[p]:
                        c = ln * cu + gu
                        if c < rhs[p]:
                            rhs[p] = c
                            self._queue(p)
            else:                                             # under-consistent: raise u, repair preds
                gold = g[u]
                g[u] = INF
                cu = cst[u]
                for off, ln in nbrs:
                    p = u + off
                    if p != goal and not blk[p] and rhs[p] == ln * cu + gold:
                        self._update_vertex(p)
                self._update_vertex(u)
        self.pops = pops

    def plan(self, blocked: np.ndarray, cost: np.ndarray, start):
        """Move the vehicle cell to start, apply map changes, repair. Returns cell path or None."""
        s = start[0] * self.ny + start[1]
        self.sxy = start
        if self.last is not None and s != self.last:
            lx, ly = divmod(self.last, self.ny)
            ax, ay = abs(lx - start[0]), abs(ly - start[1])
            self.km += (ax + ay) + (SQRT2 - 2.0) * min(ax, ay)
        self.start = self.last = s
        self._apply(blocked, cost)
        self._compute()
        return self.path()

    def path(self):
        g, blk, cst, ny = self.g, self.blk, self.cst, self.ny
        u = self.start
        if g[u] == INF and self.rhs[u] == INF:
            return None
        out = [divmod(u, ny)]
        for _ in range(len(g)):
            if u == self.goal:
                return out
            best, bv = INF, -1
            for off, ln in self.nbrs:
                v = u + off
                if not blk[v]:
                    c = ln * cst[v] + g[v]
                    if c < best:
                        best, bv = c, v
            if bv < 0:
                return None
            u = bv
            out.append(divmod(u, ny))
        return None

    def cost_to_go(self):
        return min(self.g[self.start], self.rhs[self.start])


def path_cost(path, cost: np.ndarray, blocked: np.ndarray):
    """Sum of step_length * cost[entered cell]; None if the path is not a valid 8-connected free path."""
    if path is None:
        return None
    tot = 0.0
    for (ax, ay), (bx, by) in zip(path[:-1], path[1:]):
        dx, dy = abs(bx - ax), abs(by - ay)
        if max(dx, dy) != 1 or blocked[bx, by]:
            return None
        tot += (SQRT2 if dx and dy else 1.0) * float(cost[bx, by])
    return tot


class GridReplanner(A.AStarESDF):
    """astar_esdf unknown-map mode with a pluggable search. Everything around the search is a copy of
    AStarESDF._plan, so backend="astar" reproduces the arena's results/astar_esdf_*_0.json runs."""

    def __init__(self, backend: str = "dstar", verify: bool = False):
        assert backend in ("astar", "dstar")
        self.backend, self.verify = backend, verify
        self.layers_ms: list[float] = []
        self.search_ms: list[float] = []
        self.checks: list[dict] = []          # verify=True: one row per D* Lite search
        self.dstats: list[tuple] = []         # (changed cells, updated vertices, pops) per D* search
        super().__init__(known_map=False)
        self.name = f"{backend}_unknown"

    def reset(self) -> None:
        super().reset()
        self.ds = [None, None]                # one D* Lite per inflation level

    def _search(self, k, blocked, cost, s, g):
        if self.backend == "astar":
            return A.astar(blocked, cost, s, g)
        if self.ds[k] is None:
            self.ds[k] = DStarLite(blocked.shape, g)
        d = self.ds[k]
        path = d.plan(blocked, cost, s)
        self.dstats.append((d.changed, d.updated, d.pops))
        if self.verify:
            ref = A.astar(blocked, cost, s, g)
            self.checks.append({"inflation": k, "dstar_cost": path_cost(path, cost, blocked),
                                "dstar_g": None if d.cost_to_go() == INF else d.cost_to_go(),
                                "astar_cost": path_cost(ref, cost, blocked),
                                "dstar_none": path is None, "astar_none": ref is None})
        return path

    def _plan(self, pose, goal, grid):
        t0 = time.perf_counter()
        unknown, esdf = self._layers(grid)
        self.esdf = esdf
        cost = 1.0 + A.CLEARANCE_WEIGHT * np.clip(1.0 - esdf / A.CLEARANCE_SOFT_M, 0.0, None)
        cost = cost + A.UNKNOWN_PENALTY * unknown
        t1 = time.perf_counter()
        g = self._idx(goal[0], goal[1])
        path = blocked = None
        search = 0.0
        for k, infl in enumerate((A.RADIUS + A.TRACK_MARGIN, A.RADIUS)):
            blocked = esdf <= infl + 1e-9
            s = self._idx(pose.x, pose.y)
            if blocked[s]:
                free = np.argwhere(~blocked)
                if not len(free):
                    continue
                dd = np.hypot(free[:, 0] - s[0], free[:, 1] - s[1])
                s = tuple(int(v) for v in free[int(np.argmin(dd))])
            ts = time.perf_counter()
            path = self._search(k, blocked, cost, s, g)
            search += time.perf_counter() - ts
            if path is not None:
                self.fallbacks += k
                break
        if path is None:
            self.no_path += 1
            self.path_xy = self.dense_xy = None
        else:
            sc = A.shortcut(path, esdf, blocked)
            self.path_xy = np.array([self._xy(c) for c in sc])
            self.path_xy[-1] = goal[:2]
            self.dense_xy = np.array([self._xy(c) for c in path])
        self.replan_ms.append((time.perf_counter() - t0) * 1e3)
        self.layers_ms.append((t1 - t0) * 1e3)
        self.search_ms.append(search * 1e3)


def make(**kw) -> GridReplanner:
    return GridReplanner(**kw)
