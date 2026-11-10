"""Arm (d): space-time A* over the predicted swept footprints of tracked people.

State   (cell, k) on the arena's 0.1 m prior grid, k = 0 .. K layers of DT_ST = 0.2 s,
        horizon HORIZON_S = 8 s (K = 40). Moves per layer: wait, or any cell offset with
        |offset| <= V_ST * DT_ST (0.3 m => 29 moves including wait), so the lattice speed is
        at most 1.5 m/s, the arena A*'s V_CRUISE.
Static  blocked = prior ESDF <= RADIUS + TRACK_MARGIN (0.25 m, as astar_esdf), plus cells within
        0.25 m of latest-scan hits that the prior map does not explain and that are not part of a
        confirmed track (new or unconfirmed clusters stay static). Moves longer than one cell
        also check their midpoint cell.
Dynamic layer k blocks every cell within  r(tau_k) + RADIUS + TRACK_MARGIN + PERSON_MARGIN of
        the segment between the track's predicted centres at tau_(k-1) and tau_k (its swept
        footprint over the step). r(tau) and the 3 s constant-velocity extrapolation come from
        predict.py; after 3 s the person is held at its 3 s point. Turn-around hedge: layers
        with tau <= REACH_S also block the disc of radius R_ASSUMED + speed * tau around the
        person's current centre (+ the same inflation), because a U-turn breaks the
        constant-velocity guess first.
Cost    each layer costs V_ST * DT_ST (time, so waiting is not free) plus
        length * CLEARANCE_WEIGHT * max(0, 1 - esdf / CLEARANCE_SOFT_M) (the static A*'s
        clearance cost). Heuristic and terminal cost at k = K: the static clearance-weighted
        geodesic distance to B (scipy Dijkstra on the prior grid, once per run).
Search  A* until a node at k = K or at B is popped; MAX_EXPANSIONS cap, then the expanded node
        nearest B (by geodesic) is used. If no move leaves the start, retry with
        PERSON_MARGIN = 0; then step away from the nearest predicted person.
Replan  every REPLAN_S = 0.2 s (5 Hz). The tracker updates every planner step (10 Hz).
Follow  time-indexed reference: v = v_ref(t + LEAD_S) + KP * (p_ref(t + LEAD_S) - p), capped
        at V_CMD_MAX and K_GOAL * distance to B.
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

try:
    from . import arena, predict
except ImportError:
    import arena
    import predict

A = arena.astar_esdf
DT_ST = 0.2              # s, layer step
HORIZON_S = 8.0          # s
K = int(round(HORIZON_S / DT_ST))
REPLAN_S = 0.2           # s => 5 Hz
V_ST = 1.5               # m/s, lattice speed bound (= astar_esdf V_CRUISE)
INFL = A.RADIUS + A.TRACK_MARGIN   # 0.25 m
PERSON_MARGIN = 0.3      # m, extra space kept from a predicted person (tuned on seed 0 only)
REACH_S = 0.5            # s, turn-around hedge: layers up to this also block the disc the person
                         # can reach from where it is now at its tracked speed (tuned on seed 0)
MAX_EXPANSIONS = 8000
LEAD_S = 0.1             # s, reference look-ahead (about the vehicle's 0.15 s velocity lag)
KP = 1.5                 # 1/s, position error gain
V_CMD_MAX = 1.6          # m/s
SQRT2 = math.sqrt(2.0)


def geodesic_to_goal(esdf: np.ndarray, res: float, goal_idx, infl: float) -> np.ndarray:
    """Clearance-weighted 8-connected distance (m-equivalent) from every cell to goal_idx."""
    nx, ny = esdf.shape
    free = esdf > infl + 1e-9
    w = 1.0 + A.CLEARANCE_WEIGHT * np.clip(1.0 - esdf / A.CLEARANCE_SOFT_M, 0.0, None)
    idx = np.arange(nx * ny).reshape(nx, ny)
    rows, cols, vals = [], [], []
    for dx, dy, ln in ((1, 0, 1.0), (0, 1, 1.0), (1, 1, SQRT2), (1, -1, SQRT2)):
        xs0, xs1 = (0, nx - dx)
        ys0, ys1 = (0, ny - dy) if dy >= 0 else (1, ny)
        a = idx[xs0:xs1, ys0:ys1]
        b = idx[xs0 + dx:xs1 + dx, ys0 + dy:ys1 + dy]
        ok = free[xs0:xs1, ys0:ys1] & free[xs0 + dx:xs1 + dx, ys0 + dy:ys1 + dy]
        wa = w[xs0:xs1, ys0:ys1][ok]
        wb = w[xs0 + dx:xs1 + dx, ys0 + dy:ys1 + dy][ok]
        rows.append(a[ok]); cols.append(b[ok]); vals.append(ln * res * 0.5 * (wa + wb))
    g = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                   shape=(nx * ny, nx * ny)).tocsr()
    d = dijkstra(g, directed=False, indices=goal_idx[0] * ny + goal_idx[1])
    return d.reshape(nx, ny)


def _moves(max_cells: int):
    out = []
    for dx in range(-max_cells, max_cells + 1):
        for dy in range(-max_cells, max_cells + 1):
            if dx * dx + dy * dy <= max_cells * max_cells:
                out.append((dx, dy, math.hypot(dx, dy)))
    return out


def disc_cells(geo, centres: np.ndarray, radius: float) -> np.ndarray:
    """Flat indices of cells whose centre is within radius of any of the points."""
    res, x0, y0, nx, ny = geo
    out = []
    for cx, cy in centres:
        i0, i1 = max(int((cx - radius - x0) / res), 0), min(int((cx + radius - x0) / res) + 1, nx - 1)
        j0, j1 = max(int((cy - radius - y0) / res), 0), min(int((cy + radius - y0) / res) + 1, ny - 1)
        if i1 < i0 or j1 < j0:
            continue
        I, J = np.mgrid[i0:i1 + 1, j0:j1 + 1]
        m = np.hypot(x0 + (I + 0.5) * res - cx, y0 + (J + 0.5) * res - cy) <= radius
        out.append((I[m] * ny + J[m]).ravel())
    return np.concatenate(out) if out else np.zeros(0, int)


def capsule_cells(geo, p0, p1, radius: float) -> np.ndarray:
    """Flat indices of cells whose centre is within radius of segment p0-p1."""
    res, x0, y0, nx, ny = geo
    lo = np.minimum(p0, p1) - radius
    hi = np.maximum(p0, p1) + radius
    i0, i1 = max(int((lo[0] - x0) / res), 0), min(int((hi[0] - x0) / res) + 1, nx - 1)
    j0, j1 = max(int((lo[1] - y0) / res), 0), min(int((hi[1] - y0) / res) + 1, ny - 1)
    if i1 < i0 or j1 < j0:
        return np.zeros(0, int)
    I, J = np.mgrid[i0:i1 + 1, j0:j1 + 1]
    X, Y = x0 + (I + 0.5) * res, y0 + (J + 0.5) * res
    ab = p1 - p0
    L2 = float(ab @ ab)
    t = np.clip(((X - p0[0]) * ab[0] + (Y - p0[1]) * ab[1]) / L2, 0, 1) if L2 > 1e-12 else np.zeros_like(X)
    d = np.hypot(X - (p0[0] + t * ab[0]), Y - (p0[1] + t * ab[1]))
    m = d <= radius
    return (I[m] * ny + J[m]).ravel()


class SpaceTimeAStar(arena.Planner):
    name = "st_astar"
    uses_grid = True

    def __init__(self, person_margin: float = PERSON_MARGIN, horizon_s: float = HORIZON_S,
                 replan_s: float = REPLAN_S, reach_s: float = REACH_S):
        self.person_margin, self.k_max, self.replan_s = person_margin, int(round(horizon_s / DT_ST)), replan_s
        self.reach_s = reach_s
        self.replan_ms: list[float] = []
        self.reset()

    def reset(self) -> None:
        self.tracker = None
        self.geo = None
        self.plan_t0 = None
        self.plan_xy = None
        self.last_plan_t = -math.inf
        self.replan_t: list[float] = []
        self.n_capped = self.n_relaxed = self.n_escape = 0

    # ---- one-off static layers ----
    def _init_static(self, grid, goal):
        self.tracker = predict.Tracker(grid)
        esdf = self.tracker.esdf
        nx, ny = esdf.shape
        self.geo = (grid.res, grid.x0, grid.y0, nx, ny)
        self.esdf = esdf
        g = self._idx(goal[0], goal[1])
        h = geodesic_to_goal(esdf, grid.res, g, INFL)
        self.infl = INFL
        if not np.isfinite(h[self._idx(0.0, 0.0)]):          # same fallback as astar_esdf
            h = geodesic_to_goal(esdf, grid.res, g, A.RADIUS)
            self.infl = A.RADIUS
        self.h = np.where(np.isfinite(h), h, 1e9).ravel().tolist()
        self.sblk = (esdf <= self.infl + 1e-9).ravel().tolist()
        self.ccost = (A.CLEARANCE_WEIGHT * np.clip(1.0 - esdf / A.CLEARANCE_SOFT_M, 0.0, None)).ravel().tolist()
        self.goal_flat = g[0] * ny + g[1]
        res = grid.res
        mv = []
        for dx, dy, ln in _moves(int(round(V_ST * DT_ST / res))):
            mid = (int(round(dx / 2)), int(round(dy / 2))) if ln > 1.5 else None
            mv.append((dx, dy, dx * ny + dy, ln * res, None if mid is None else mid[0] * ny + mid[1]))
        self.moves = mv

    def _idx(self, x, y):
        res, x0, y0, nx, ny = self.geo
        return (min(max(int((x - x0) // res), 0), nx - 1), min(max(int((y - y0) // res), 0), ny - 1))

    def _xy(self, flat):
        res, x0, y0, nx, ny = self.geo
        i, j = divmod(flat, ny)
        return x0 + (i + 0.5) * res, y0 + (j + 0.5) * res

    # ---- layers from the tracker ----
    def _scan_static(self, pose, scan) -> set:
        beams = self.tracker.unexplained_beams
        if not len(beams):
            return set()
        keep = np.setdiff1d(beams, self.tracker.confirmed_beams())
        if not len(keep):
            return set()
        a = pose.yaw + np.asarray(scan.angles, float)[keep]
        d = np.asarray(scan.distances, float)[keep]
        pts = np.column_stack([pose.x + d * np.cos(a), pose.y + d * np.sin(a)])
        return set(disc_cells(self.geo, pts, self.infl).tolist())

    def _dyn_layers(self, tracks, margin) -> list[set]:
        layers = [set() for _ in range(self.k_max + 1)]
        for tr in tracks:
            prev = tr.at(0.0)
            for k in range(1, self.k_max + 1):
                tau = k * DT_ST
                cur = tr.at(tau)
                r = float(tr.radius(tau)) + self.infl + margin
                layers[k].update(capsule_cells(self.geo, prev, cur, r).tolist())
                rr = tr.reach_radius(tau, self.reach_s)
                if rr is not None:
                    layers[k].update(disc_cells(self.geo, tr.p[None, :], rr + self.infl + margin).tolist())
                prev = cur
        return layers

    # ---- search ----
    def _search(self, s, dyn, sstat):
        res, x0, y0, nx, ny = self.geo
        KK = self.k_max + 1
        h, sblk, ccost, moves, gflat = self.h, self.sblk, self.ccost, self.moves, self.goal_flat
        step_t = V_ST * DT_ST
        start = s * KK
        g_of = {start: 0.0}
        parent = {start: -1}
        closed = set()
        heap = [(h[s], 0, 0.0, start)]
        best = (h[s], 0, start)
        n_exp = 0
        push, pop = heapq.heappush, heapq.heappop
        while heap:
            _, negk, g, key = pop(heap)
            if key in closed:
                continue
            closed.add(key)
            u, k = divmod(key, KK)
            if (h[u], -k) < best[:2]:
                best = (h[u], -k, key)
            if k == self.k_max or u == gflat:
                return self._unwind(key, parent, KK), False
            n_exp += 1
            if n_exp > MAX_EXPANSIONS:
                break
            ux, uy = divmod(u, ny)
            dk = dyn[k + 1]
            for dx, dy, off, ln, mid in moves:
                vx, vy = ux + dx, uy + dy
                if vx < 0 or vy < 0 or vx >= nx or vy >= ny:
                    continue
                v = u + off
                if sblk[v] or v in dk or v in sstat:
                    continue
                if mid is not None and (sblk[u + mid] or (u + mid) in sstat):
                    continue
                nkey = v * KK + k + 1
                if nkey in closed:
                    continue
                ng = g + step_t + ln * ccost[v]
                if ng < g_of.get(nkey, math.inf):
                    g_of[nkey] = ng
                    parent[nkey] = key
                    push(heap, (ng + h[v], -(k + 1), ng, nkey))
        if best[2] == start:
            return None, True
        return self._unwind(best[2], parent, KK), True

    def _unwind(self, key, parent, KK):
        cells = []
        while key != -1:
            cells.append(key // KK)
            key = parent[key]
        return [self._xy(c) for c in cells[::-1]]

    def _plan(self, pose, goal, scan):
        t0 = time.perf_counter()
        tracks = self.tracker.confirmed()
        sstat = self._scan_static(pose, scan)
        s = self._idx(pose.x, pose.y)
        sflat = s[0] * self.geo[4] + s[1]
        if self.sblk[sflat]:                      # inside the static inflation: nearest free cell
            free = np.flatnonzero(~np.asarray(self.sblk))
            fx, fy = np.divmod(free, self.geo[4])
            sflat = int(free[int(np.argmin(np.hypot(fx - s[0], fy - s[1])))])
        path = None
        for margin in (self.person_margin, 0.0):
            dyn = self._dyn_layers(tracks, margin)
            path, capped = self._search(sflat, dyn, sstat)
            self.n_capped += int(capped and path is not None)
            if path is not None:
                self.n_relaxed += int(margin != self.person_margin)
                break
        if path is None:
            self.n_escape += 1
            self.plan_xy = None
        else:
            P = np.array(path)
            P[0] = (pose.x, pose.y)
            if math.hypot(P[-1, 0] - goal[0], P[-1, 1] - goal[1]) < 0.15:
                P[-1] = goal[:2]
            self.plan_xy, self.plan_t0 = P, pose.t
        self.replan_ms.append((time.perf_counter() - t0) * 1e3)

    def _escape(self, pose):
        tracks = self.tracker.confirmed()
        if not tracks:
            return arena.Setpoint(0.0, 0.0, 0.0, 0.0)
        p = np.array([pose.x, pose.y])
        near = min(tracks, key=lambda tr: math.hypot(*(tr.at(DT_ST) - p)))
        away = p - near.at(DT_ST)
        n = max(math.hypot(*away), 1e-6)
        d = away / n
        ix, iy = self._idx(*(p + 0.3 * d))
        if self.esdf[ix, iy] <= A.RADIUS + 0.05:
            return arena.Setpoint(0.0, 0.0, 0.0, 0.0)
        return arena.Setpoint(1.0 * d[0], 1.0 * d[1], 0.0, 0.0)

    def _reference(self, t):
        P = self.plan_xy
        f = (t - self.plan_t0) / DT_ST
        if f >= len(P) - 1:
            return P[-1], np.zeros(2)
        i = max(int(f), 0)
        a = f - i
        return P[i] + a * (P[i + 1] - P[i]), (P[i + 1] - P[i]) / DT_ST

    def step(self, pose, scan, goal, grid, dt):
        if self.tracker is None:
            self._init_static(grid, goal)
        self.tracker.update(pose, scan)
        if pose.t - self.last_plan_t >= self.replan_s - 1e-9 or self.plan_xy is None:
            self._plan(pose, goal, scan)
            self.last_plan_t = pose.t
            self.replan_t.append(pose.t)
        if self.plan_xy is None:
            return self._escape(pose)
        pr, vr = self._reference(pose.t + LEAD_S)
        v = vr + KP * (pr - np.array([pose.x, pose.y]))
        sp = math.hypot(*v)
        cap = min(V_CMD_MAX, A.K_GOAL * math.hypot(goal[0] - pose.x, goal[1] - pose.y) + 0.05)
        if sp > cap:
            v = v * (cap / sp)
            sp = cap
        yaw_rate = 0.0
        if sp > 0.05:
            yaw_err = (math.atan2(v[1], v[0]) - pose.yaw + math.pi) % (2 * math.pi) - math.pi
            yaw_rate = A.K_YAW * yaw_err
        return arena.Setpoint(float(v[0]), float(v[1]), 0.0, yaw_rate)


def make(**kw) -> SpaceTimeAStar:
    return SpaceTimeAStar(**kw)
