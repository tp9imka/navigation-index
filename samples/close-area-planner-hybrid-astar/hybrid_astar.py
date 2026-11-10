"""Hybrid A* (Dolgov, Thrun, Montemerlo, Diebel 2008 / IJRR 2010) for the close-area arena.

Search over continuous (x, y, heading) states, binned 0.25 m x 0.25 m x 10 deg for the closed set
(each bin keeps the continuous state that reached it first at the lowest cost). Motion primitives
respect a turn-rate limit OMEGA_MAX and the arena vehicle's limits (|v| <= 2 m/s, |a| <= 3 m/s^2):
  - fast arcs, v = V_FAST (1.5 m/s, astar_esdf's cruise), 0.6 m long, turn rate 0, +-0.5, +-1.0 x OMEGA_MAX
    (curvature <= OMEGA_MAX / V_FAST = 0.67 1/m; lateral acceleration v^2 k = 1.5 m/s^2 <= 3)
  - slow arcs, v = V_SLOW (0.5 m/s), 0.4 m long, turn rate +-OMEGA_MAX (curvature 2 1/m, R = 0.5 m)
  - turn in place +-45 deg at OMEGA_MAX (a multirotor can rotate its velocity direction at low speed),
    flown at V_TURN in the speed profile
No Reeds-Shepp shot (no reverse or curvature constraint at low speed is needed for a drone): every
SHOT_EVERY expansions, a straight-line shot to B is tried; it is accepted when the segment keeps the
inflation and min(SHOT_CLEAR_M, node clearance, B clearance) of ESDF. A heading change above
SHOT_FREE_TURN rad at its start is paid as a turn in place.
Cost = flight time x (1 + astar_esdf's clearance cost + unknown-cell penalty), so it is the A*
baseline's cost model in time units. Heuristic = 2D Dijkstra from B on the same cost grid
(scipy.sparse.csgraph, Dolgov's "non-holonomic-without-obstacles" term is not used: a drone has
none) divided by V_FAST, times H_WEIGHT.
Same map (log-odds from range hits, unknown passable at a cost, or the prior grid), same two-level
inflation (0.25 m, then 0.15 m), same replan rule and the same carrot follower as astar_esdf, which
this class subclasses. Added: the planned speed profile (primitive speeds, V_TURN at turns in
place, backward pass at A_LON) caps the follower's speed. If no Hybrid A* path is found within
MAX_EXPANSIONS at either inflation, the replan falls back to astar_esdf's own grid path (counted in
grid_fallbacks) with V_TURN at its corners.

make(**kw) works with no arguments (unknown map, map corner as shipped in astar_esdf). Pass
bounds=(xmin, ymin, xmax, ymax) to put the map on the operator geofence, as the benchmark does.
numpy + scipy only (runs in Pyodide).
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from arena import Setpoint, astar_esdf

A = astar_esdf
RADIUS, TRACK_MARGIN = A.RADIUS, A.TRACK_MARGIN

# ---- vehicle limits used by the primitives ----
OMEGA_MAX = 1.0               # rad/s, planning turn-rate limit (arena yaw-rate cap is 2.0)
V_FAST = A.V_CRUISE           # 1.5 m/s, same cruise as astar_esdf
V_SLOW = 0.5                  # m/s, slow tight arcs
V_TURN = 0.2                  # m/s, speed in the profile where a turn in place happens
A_LON = 1.5                   # m/s^2, deceleration used for the speed profile (half of a_max: lag margin)
# ---- primitives and search ----
STEP_FAST_M = 0.6             # m, fast arc length
STEP_SLOW_M = 0.4             # m, slow arc length
TURN_INPLACE = math.pi / 4    # rad per turn-in-place primitive
SAMPLE_DS = 0.1               # m, collision-check spacing along primitives and shots
XY_BIN = 0.25                 # m, closed-set bin
N_HEAD = 36                   # heading bins (10 deg)
H_WEIGHT = 1.5                # heuristic inflation (weighted A*; 1.0 = optimal for the cost model)
MAX_EXPANSIONS = 4000         # per inflation level, then grid fallback
SHOT_EVERY = 3                # try the straight shot to B every n expansions
SHOT_CLEAR_M = 0.5            # m, ESDF the shot must keep (capped by node and B clearance)
SHOT_FREE_TURN = 0.4          # rad, heading change at a shot start that is not paid as a turn
GOAL_TOL_PLAN = 0.3           # m, a node this close to B ends the search
START_RELAX_M = 0.6           # m, near the start, samples need only the start's own clearance
PROFILE_LOOK_M = 0.3          # m, follower speed cap = min profile speed over this distance ahead

TWO_PI = 2.0 * math.pi
SQRT2 = math.sqrt(2.0)


def _wrap(a: float) -> float:
    return (a + math.pi) % TWO_PI - math.pi


def build_primitives(omega_max: float = OMEGA_MAX):
    """Body-frame motion primitives. Returns (moves, turns): moves = list of dicts with sample arrays
    x, y, th (relative to the start state, excluding the start point), length L, speed v, end
    heading change dth; turns = list of heading changes for turns in place."""
    moves = []
    for v, L, fracs in ((V_FAST, STEP_FAST_M, (0.0, -0.5, 0.5, -1.0, 1.0)), (V_SLOW, STEP_SLOW_M, (-1.0, 1.0))):
        for f in fracs:
            k = f * omega_max / v
            n = max(2, int(round(L / SAMPLE_DS)))
            s = np.linspace(L / n, L, n)
            if abs(k) < 1e-9:
                x, y, th = s, np.zeros(n), np.zeros(n)
            else:
                th = k * s
                x, y = np.sin(th) / k, (1.0 - np.cos(th)) / k
            moves.append({"x": x, "y": y, "th": th, "L": L, "v": v, "dth": k * L, "kappa": k})
    return moves, [TURN_INPLACE, -TURN_INPLACE]


def grid_heuristic(blocked: np.ndarray, cost: np.ndarray, goal_cell, res: float) -> np.ndarray:
    """Cost-weighted 8-connected Dijkstra distance (metres x cost) from goal_cell over free cells."""
    nx, ny = blocked.shape
    free = ~blocked
    idx = np.arange(nx * ny).reshape(nx, ny)
    rows, cols, wts = [], [], []
    for dx, dy, ln in ((1, 0, 1.0), (0, 1, 1.0), (1, 1, SQRT2), (1, -1, SQRT2)):
        sx, tx = slice(0, nx - dx), slice(dx, nx)
        sy = slice(max(0, -dy), ny - max(0, dy))
        ty = slice(max(0, dy), ny + min(0, dy))
        m = free[sx, sy] & free[tx, ty]
        rows.append(idx[sx, sy][m])
        cols.append(idx[tx, ty][m])
        wts.append(ln * res * 0.5 * (cost[sx, sy][m] + cost[tx, ty][m]))
    r, c, w = np.concatenate(rows), np.concatenate(cols), np.concatenate(wts)
    g = coo_matrix((w, (r, c)), shape=(nx * ny, nx * ny)).tocsr()
    d = dijkstra(g, directed=False, indices=int(goal_cell[0] * ny + goal_cell[1]))
    return d.reshape(nx, ny)


class HybridAStar(A.AStarESDF):
    name = "hybrid_astar"

    def __init__(self, known_map: bool = False, bounds=None, margin: float = 2.0,
                 omega_max: float = OMEGA_MAX, max_expansions: int = MAX_EXPANSIONS):
        self.bounds, self.margin = bounds, margin
        self.omega_max, self.max_expansions = omega_max, max_expansions
        self.moves, self.turns = build_primitives(omega_max)
        self._cat = (np.concatenate([m["x"] for m in self.moves]), np.concatenate([m["y"] for m in self.moves]))
        lens = [len(m["x"]) for m in self.moves]
        self._starts = np.cumsum([0] + lens[:-1])
        self._ends = np.cumsum(lens) - 1
        self.expansions: list[int] = []       # per replan, kept across runs
        self.grid_fallbacks = 0               # replans that used astar_esdf's grid path
        self.shots = 0                        # replans that ended with the straight shot to B
        super().__init__(known_map=known_map)
        self.name = "hybrid_astar_known" if known_map else "hybrid_astar_unknown"

    def reset(self) -> None:
        super().reset()
        self.prof = None                      # (m,) speed cap per dense path sample
        self.heading = None                   # (m,) planned heading per sample
        self.last_source = None               # "hybrid" or "grid"
        if self.map is not None and self.bounds is not None:
            self.map.x0 = self.bounds[0] - self.margin
            self.map.y0 = self.bounds[1] - self.margin

    # ---- search ----
    def search(self, start, goal, esdf, blocked, cost, hgrid, infl):
        """Hybrid A* from start (x, y, th) to goal (x, y). Returns (states, expansions) where states
        is a list of (x, y, th, kind, data) from start to goal, or (None, expansions)."""
        res, x0, y0, nx, ny = self.geo
        PX, PY = self._cat
        starts, ends = self._starts, self._ends
        moves, om = self.moves, self.omega_max
        hscale = H_WEIGHT / V_FAST
        gx, gy = goal

        def cell(x, y):
            return int((x - x0) // res), int((y - y0) // res)

        def inside(i, j):
            return 0 <= i < nx and 0 <= j < ny

        def h_at(x, y):
            i, j = cell(x, y)
            if not inside(i, j):
                return math.inf
            v = hgrid[i, j]
            if math.isinf(v) and blocked[i, j]:          # only near the start (relaxed check)
                return math.hypot(gx - x, gy - y) * hscale
            return v * hscale

        def key(x, y, th):
            return (int(x // XY_BIN), int(y // XY_BIN), int(round(th / TWO_PI * N_HEAD)) % N_HEAD)

        sx, sy, sth = start
        si, sj = cell(sx, sy)
        e_start = float(esdf[si, sj]) if inside(si, sj) else 0.0
        gi, gj = cell(gx, gy)
        e_goal = float(esdf[gi, gj]) if inside(gi, gj) else 0.0
        N = {"x": [sx], "y": [sy], "th": [sth], "g": [0.0], "par": [-1], "kind": [None], "data": [None]}
        h0 = h_at(sx, sy)
        if math.isinf(h0):
            return None, 0
        heap = [(h0, 0, 0)]
        best = {key(sx, sy, sth): 0.0}
        closed = set()
        cnt, exp = 1, 0
        found = -1
        while heap:
            _, _, u = heapq.heappop(heap)
            ux, uy, uth, ug = N["x"][u], N["y"][u], N["th"][u], N["g"][u]
            ku = key(ux, uy, uth)
            if ku in closed:
                continue
            closed.add(ku)
            if math.hypot(gx - ux, gy - uy) <= GOAL_TOL_PLAN:
                found = u
                break
            ci, cj = cell(ux, uy)
            if exp % SHOT_EVERY == 0:
                shot = self._shot(ux, uy, uth, goal, esdf, cost, infl, e_goal, ci, cj)
                if shot is not None:
                    tcost, turn = shot
                    for k_, v_ in (("x", gx), ("y", gy), ("th", math.atan2(gy - uy, gx - ux)),
                                   ("g", ug + tcost), ("par", u), ("kind", "shot"), ("data", turn)):
                        N[k_].append(v_)
                    found = len(N["x"]) - 1
                    self.shots += 1
                    break
            exp += 1
            if exp > self.max_expansions:
                break
            relax = math.hypot(ux - sx, uy - sy) < START_RELAX_M
            thr = min(infl, e_start * 0.999) if relax else infl
            c, s = math.cos(uth), math.sin(uth)
            X = ux + c * PX - s * PY
            Y = uy + s * PX + c * PY
            I = np.floor((X - x0) / res).astype(np.int64)
            J = np.floor((Y - y0) / res).astype(np.int64)
            inb = (I >= 0) & (J >= 0) & (I < nx) & (J < ny)
            Ic, Jc = np.clip(I, 0, nx - 1), np.clip(J, 0, ny - 1)
            ok = inb & (esdf[Ic, Jc] > thr)
            okm = np.minimum.reduceat(ok.astype(np.int8), starts).tolist()
            csum = np.add.reduceat(cost[Ic, Jc], starts).tolist()
            Xe, Ye = X[ends].tolist(), Y[ends].tolist()
            Ie, Je = Ic[ends].tolist(), Jc[ends].tolist()
            for m, mv in enumerate(moves):
                if not okm[m]:
                    continue
                nth = _wrap(uth + mv["dth"])
                nxx, nyy = Xe[m], Ye[m]
                kn = key(nxx, nyy, nth)
                if kn in closed:
                    continue
                n_s = len(mv["x"])
                g2 = ug + (mv["L"] / mv["v"]) * (csum[m] / n_s)
                if g2 >= best.get(kn, math.inf):
                    continue
                hv = hgrid[Ie[m], Je[m]]
                if math.isinf(hv):
                    if not blocked[Ie[m], Je[m]]:
                        continue
                    hv = math.hypot(gx - nxx, gy - nyy)
                best[kn] = g2
                for k_, v_ in (("x", nxx), ("y", nyy), ("th", nth), ("g", g2), ("par", u), ("kind", "move"),
                               ("data", m)):
                    N[k_].append(v_)
                heapq.heappush(heap, (g2 + hv * hscale, cnt, len(N["x"]) - 1))
                cnt += 1
            # turns in place: same position, heading +-45 deg, time = angle / omega
            c_here = float(cost[ci, cj]) if inside(ci, cj) else 1.0
            hu = h_at(ux, uy)
            for d in self.turns:
                nth = _wrap(uth + d)
                kn = key(ux, uy, nth)
                if kn in closed:
                    continue
                g2 = ug + abs(d) / om * c_here
                if g2 >= best.get(kn, math.inf):
                    continue
                best[kn] = g2
                for k_, v_ in (("x", ux), ("y", uy), ("th", nth), ("g", g2), ("par", u), ("kind", "turn"),
                               ("data", d)):
                    N[k_].append(v_)
                heapq.heappush(heap, (g2 + hu, cnt, len(N["x"]) - 1))
                cnt += 1
        if found < 0:
            return None, exp
        chain = []
        u = found
        while u != -1:
            chain.append((N["x"][u], N["y"][u], N["th"][u], N["kind"][u], N["data"][u]))
            u = N["par"][u]
        return chain[::-1], exp

    def _shot(self, x, y, th, goal, esdf, cost, infl, e_goal, ci, cj):
        """Straight segment to B. Returns (time cost, turn angle) or None."""
        res, x0, y0, nx, ny = self.geo
        dx, dy = goal[0] - x, goal[1] - y
        d = math.hypot(dx, dy)
        n = int(d / SAMPLE_DS) + 1
        t = np.linspace(0.0, 1.0, n + 1)[1:]
        I = np.floor((x + dx * t - x0) / res).astype(np.int64)
        J = np.floor((y + dy * t - y0) / res).astype(np.int64)
        if I.min() < 0 or J.min() < 0 or I.max() >= nx or J.max() >= ny:
            return None
        e = esdf[I, J]
        e_here = float(esdf[ci, cj]) if (0 <= ci < nx and 0 <= cj < ny) else 0.0
        need = max(infl, min(SHOT_CLEAR_M, e_here, e_goal))
        if float(e.min()) < need - 1e-9 or float(e.min()) <= infl:
            return None
        turn = abs(_wrap(math.atan2(dy, dx) - th))
        tc = (d / V_FAST) * float(cost[I, J].mean())
        if turn > SHOT_FREE_TURN:
            tc += turn / self.omega_max
        return tc, turn

    def _densify(self, chain):
        """Chain of states => dense (xy, heading, speed cap) arrays from the start to B."""
        xs, ys, hs, vs = [chain[0][0]], [chain[0][1]], [chain[0][2]], [V_FAST]
        for k in range(1, len(chain)):
            px, py, pth = chain[k - 1][:3]
            x, y, th, kind, data = chain[k]
            if kind == "turn":
                vs[-1] = V_TURN
                hs[-1] = th
                continue
            if kind == "move":
                mv = self.moves[data]
                c, s = math.cos(pth), math.sin(pth)
                X = px + c * mv["x"] - s * mv["y"]
                Y = py + s * mv["x"] + c * mv["y"]
                H = pth + mv["th"]
                xs += X.tolist()
                ys += Y.tolist()
                hs += H.tolist()
                vs += [mv["v"]] * len(X)
            else:                              # shot
                if data > SHOT_FREE_TURN:
                    vs[-1] = V_TURN
                d = math.hypot(x - px, y - py)
                n = max(1, int(math.ceil(d / SAMPLE_DS)))
                t = np.linspace(0.0, 1.0, n + 1)[1:]
                xs += (px + (x - px) * t).tolist()
                ys += (py + (y - py) * t).tolist()
                hs += [th] * n
                vs += [V_FAST] * n
        return np.column_stack([xs, ys]), np.array(hs), np.array(vs)

    @staticmethod
    def backward_pass(xy, v, a_lon=A_LON):
        v = v.copy()
        ds = np.hypot(*np.diff(xy, axis=0).T)
        for i in range(len(v) - 2, -1, -1):
            v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2.0 * a_lon * ds[i]))
        return v

    def _grid_profile(self, P):
        """astar_esdf polyline => dense samples with V_TURN at corners above SHOT_FREE_TURN."""
        xs, ys, vs = [P[0, 0]], [P[0, 1]], [V_FAST]
        for i in range(1, len(P)):
            if i >= 2:
                h0 = math.atan2(P[i - 1, 1] - P[i - 2, 1], P[i - 1, 0] - P[i - 2, 0])
                h1 = math.atan2(P[i, 1] - P[i - 1, 1], P[i, 0] - P[i - 1, 0])
                if abs(_wrap(h1 - h0)) > SHOT_FREE_TURN:
                    vs[-1] = V_TURN
            d = math.hypot(*(P[i] - P[i - 1]))
            n = max(1, int(math.ceil(d / SAMPLE_DS)))
            t = np.linspace(0.0, 1.0, n + 1)[1:]
            xs += (P[i - 1, 0] + (P[i, 0] - P[i - 1, 0]) * t).tolist()
            ys += (P[i - 1, 1] + (P[i, 1] - P[i - 1, 1]) * t).tolist()
            vs += [V_FAST] * n
        xy = np.column_stack([xs, ys])
        d = np.diff(xy, axis=0)
        h = np.arctan2(d[:, 1], d[:, 0])
        return xy, np.concatenate([h[:1], h]), np.array(vs)

    def _plan(self, pose, goal, grid):
        t0 = time.perf_counter()
        unknown, esdf = self._layers(grid)
        self.esdf = esdf
        cost = 1.0 + A.CLEARANCE_WEIGHT * np.clip(1.0 - esdf / A.CLEARANCE_SOFT_M, 0.0, None)
        cost = cost + A.UNKNOWN_PENALTY * unknown
        sp = math.hypot(pose.vx, pose.vy)
        th = math.atan2(pose.vy, pose.vx) if sp > 0.3 else pose.yaw
        g = self._idx(goal[0], goal[1])
        chain, n_exp = None, 0
        for k, infl in enumerate((RADIUS + TRACK_MARGIN, RADIUS)):
            blocked = esdf <= infl + 1e-9
            if blocked[g]:
                continue
            hgrid = grid_heuristic(blocked, cost, g, self.geo[0])
            chain, e = self.search((pose.x, pose.y, th), goal[:2], esdf, blocked, cost, hgrid, infl)
            n_exp += e
            if chain is not None:
                self.fallbacks += k
                break
        self.expansions.append(n_exp)
        if chain is not None:
            xy, hd, v = self._densify(chain)
            if math.hypot(xy[-1, 0] - goal[0], xy[-1, 1] - goal[1]) > 1e-6:
                xy = np.vstack([xy, goal[:2]])
                hd = np.append(hd, hd[-1])
                v = np.append(v, V_FAST)
            self.last_source = "hybrid"
        else:
            super()._plan(pose, goal, grid)    # astar_esdf grid path (appends its own replan time)
            self.replan_ms.pop()
            if self.path_xy is None:
                self.prof = self.heading = None
                self.last_source = None
                self.replan_ms.append((time.perf_counter() - t0) * 1e3)
                return
            self.grid_fallbacks += 1
            xy, hd, v = self._grid_profile(self.path_xy)
            self.last_source = "grid"
        self.path_xy = self.dense_xy = xy
        self.heading = hd
        self.prof = self.backward_pass(xy, v)
        self.replan_ms.append((time.perf_counter() - t0) * 1e3)

    def _profile_cap(self, px, py) -> float:
        P = self.path_xy
        i = int(np.argmin((P[:, 0] - px) ** 2 + (P[:, 1] - py) ** 2))
        j = i + int(math.ceil(PROFILE_LOOK_M / SAMPLE_DS)) + 1
        return float(self.prof[i:j].min())

    def step(self, pose, scan, goal, grid, dt):
        """astar_esdf.step with one change: speed is also capped by the planned speed profile."""
        new_occ = np.zeros((0, 2), int)
        if not self.known_map:
            new_occ = self.map.update(pose, scan)
        due = pose.t - self.last_plan_t >= A.REPLAN_PERIOD_S - 1e-9
        if due or self.path_xy is None or self._blocked_by(new_occ):
            self._plan(pose, goal, grid)
            self.last_plan_t = pose.t
        if self.path_xy is None:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist_goal = math.hypot(ex, ey)
        c = self._carrot(pose.x, pose.y)
        cx, cy = c[0] - pose.x, c[1] - pose.y
        dc = math.hypot(cx, cy)
        if dc < 1e-6:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        clr = self._min_esdf((pose.x, pose.y), c)
        frac = (clr - A.V_CLEAR_STOP_M) / (A.V_CLEAR_FULL_M - A.V_CLEAR_STOP_M)
        speed = A.V_CRUISE * min(1.0, max(A.V_MIN_FRAC, frac))
        speed = min(speed, A.K_GOAL * dist_goal, self._profile_cap(pose.x, pose.y))
        h = math.atan2(cy, cx)
        yaw_err = _wrap(h - pose.yaw)
        return Setpoint(speed * cx / dc, speed * cy / dc, 0.0, A.K_YAW * yaw_err)


def make(**kw) -> HybridAStar:
    """make() => unknown map, map corner as shipped in astar_esdf. kw: known_map, bounds, margin,
    omega_max, max_expansions."""
    return HybridAStar(**kw)
