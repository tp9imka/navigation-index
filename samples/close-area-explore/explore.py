"""Find B when it is not a coordinate: search arms on the arena's unknown-map A*, then A* to B.

B is given as a region (nominal point + radius R, R = 0 means B is exactly at the nominal) or
not given at all (R = None). The true B is the arena layout's goal; the nominal is drawn at a
uniform random point within R of it (seeded per layout). B is "detected" when the vehicle is
within DETECT_RANGE_M of it with a clear line of sight (exact ray cast on truth geometry). From
then on the planner knows B (relative measurement, no error added) and flies there with the
same A*. Scored on truth with the arena scorer (reached = within 0.3 m of B).

DETECT_RANGE_M = 2.0 m comes from samples/fiducial-goal-apriltag results/sweep_harsh.md
(0.16 m tag36h11, blur 1.5 px, noise 6 DN, synthetic): detection rate 1.00 at 2 m for view
angles 0-50 deg and 0.95 at 60 deg; at 3 m frontal it is already 0.85. 2 m is the largest
swept range where the harsh setting holds >= 0.9 out to 60 deg.

Arms (all drive with the arena's AStarESDF follower on its log-odds map from range hits only):
  frontier          Nearest frontier (Yamauchi 1997). Frontier = known-free cell next to an
                    unknown cell, clusters >= MIN_FRONTIER_CELLS. Nearest by path length
                    (scipy.sparse.csgraph.dijkstra over known-free cells). Ignores the region.
  nominal_frontier  A* to the nominal first; then nearest frontier inside R + detection
                    range of the nominal; then any frontier. With R = None it is `frontier`.
  lawnmower         Boustrophedon lanes LANE_M apart over the region's bounding box (the whole
                    geofence when R = None), waypoints every LANE_M; skips waypoints that fail;
                    then nearest frontier.
  random_walk       Random waypoints: uniform in the region disk, or a 2-5 m step in a random
                    heading when R = None. New waypoint on arrival, failure or timeout.
  oracle            B handed over at t = 0 (B as a coordinate). Reference row only.

The planner gets the geofence (area bounds), the nominal and R. It never reads the world.
numpy + scipy only, no threads or processes: runs under Pyodide.
"""
from __future__ import annotations

import math
import time

import numpy as np
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

try:
    from . import arena as A
except ImportError:
    import arena as A

AS = A.astar_esdf
Setpoint = A.Setpoint

# ---- task ----
DETECT_RANGE_M = 2.0          # m, fiducial-goal-apriltag results/sweep_harsh.md (see docstring)
MAX_TIME_S = 180.0            # s, search + approach budget per run
REGION_SEED = 8101            # rng constant for the nominal offset
WALK_SEED = 8201              # rng constant for random_walk
# ---- search ----
SELECT_PERIOD_S = 1.0         # s, frontier re-check period
TARGET_TIMEOUT_S = 15.0       # s, give up on a target after max(this, TIMEOUT_PER_M x distance)
TIMEOUT_PER_M = 4.0           # s per metre of straight-line distance when the target was set
REACH_M = 0.5                 # m, a search target counts as visited
MIN_TARGET_DIST_M = 1.0       # m, prefer frontiers at least this far by path
MIN_FRONTIER_CELLS = 4        # cells, smaller frontier clusters are noise
BLACKLIST_M = 1.0             # m, failed targets exclude frontiers this close
SAFE_M = AS.RADIUS + AS.TRACK_MARGIN + 0.05   # m, ESDF a target cell must have
LANE_M = 3.0                  # m, lawnmower lane spacing (2 x detection range minus 1 m overlap)
WALK_STEP_M = (2.0, 5.0)      # m, random_walk step without a region
STUCK_PATH_M = 0.5            # m, truth path length in 10 s below which the run is stuck
MAP_MARGIN_M = 2.0            # m, log-odds map extends this far outside the geofence

ARMS = ("frontier", "nominal_frontier", "lawnmower", "random_walk", "oracle")
SQRT2 = math.sqrt(2.0)


def wilson(k: int, n: int, z: float = 1.96):
    """Wilson score interval for k successes in n, in percent."""
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1))


def nominal_for(w, seed: int, index: int, radius):
    """Nominal point within `radius` of the true B (uniform in the disk). Same direction and
    radial fraction for every radius of a layout, so R = 2 and R = 5 differ only in scale."""
    if radius is None:
        return None
    rng = np.random.default_rng([seed, index, REGION_SEED])
    u, th = rng.random(), rng.uniform(-math.pi, math.pi)
    r = radius * math.sqrt(u)
    x = min(max(w.goal[0] + r * math.cos(th), w.xmin + 0.2), w.xmax - 0.2)
    y = min(max(w.goal[1] + r * math.sin(th), w.ymin + 0.2), w.ymax - 0.2)
    return (x, y)


class Explorer(AS.AStarESDF):
    """Search for B on the unknown map, then fly to it. Same follower as astar_esdf unknown."""

    def __init__(self, arm: str, bounds, nominal=None, radius=None, seed=(0, 0)):
        if arm not in ARMS:
            raise ValueError(f"arm {arm!r} not in {ARMS}")
        self.arm, self.bounds = arm, tuple(float(v) for v in bounds)
        self.nominal, self.radius = nominal, radius
        if (nominal is None) != (radius is None):
            raise ValueError("give both nominal and radius, or neither")
        self.seed = tuple(seed)
        super().__init__(known_map=False)
        self.name = arm

    # ---- lifecycle ----
    def reset(self) -> None:
        super().reset()
        xmin, ymin, xmax, ymax = self.bounds
        self.map.x0, self.map.y0 = xmin - MAP_MARGIN_M, ymin - MAP_MARGIN_M
        n = self.map.lo.shape[0]
        need = int(math.ceil((max(xmax - xmin, ymax - ymin) + 2 * MAP_MARGIN_M) / self.map.res))
        if need > n:
            self.map.lo = np.zeros((need, need), np.float32)
            n = need
        c = self.map.x0 + (np.arange(n) + 0.5) * self.map.res
        d = self.map.y0 + (np.arange(n) + 0.5) * self.map.res
        self.inside = ((c[:, None] > xmin) & (c[:, None] < xmax) & (d[None, :] > ymin) & (d[None, :] < ymax))
        self.b = None
        self.target = None
        self.target_t = -math.inf
        self.target_budget = TARGET_TIMEOUT_S
        self.last_select_t = -math.inf
        self.blacklist: list[tuple[float, float]] = []
        self.phase = "nominal" if (self.arm == "nominal_frontier" and self.nominal is not None) else "search"
        self.rng = np.random.default_rng(list(self.seed) + [WALK_SEED])
        self.waypoints = None
        self.wp_i = 0
        self.n_targets = 0
        self.last_none = False
        self.select_ms: list[float] = []

    def observe_goal(self, xy) -> None:
        """B detected (or handed over): fly to it from now on."""
        if self.b is None:
            self.b = (float(xy[0]), float(xy[1]))
            self.target = self.b
            self.path_xy = None

    # ---- map helpers ----
    def _esdf_now(self):
        occ = self.map.occupied()
        padded = np.pad(occ, 1, constant_values=True)
        self.geo = (self.map.res, self.map.x0, self.map.y0) + occ.shape
        return (ndimage.distance_transform_edt(~padded) * self.map.res)[1:-1, 1:-1]

    def _snap(self, xy, esdf, max_m=None):
        """Nearest cell to xy with ESDF > SAFE_M inside the geofence, or None."""
        ok = (esdf > SAFE_M) & self.inside
        c = self._idx(*xy)
        if ok[c]:
            return self._xy(c)
        cand = np.argwhere(ok)
        if not len(cand):
            return None
        d = np.hypot(cand[:, 0] - c[0], cand[:, 1] - c[1])
        k = int(np.argmin(d))
        if max_m is not None and d[k] * self.map.res > max_m:
            return None
        return self._xy(tuple(cand[k]))

    def _path_dist(self, trav, start):
        nx, ny = trav.shape
        idx = np.arange(nx * ny).reshape(nx, ny)
        rows, cols, wts = [], [], []
        for dx, dy, c in ((1, 0, 1.0), (0, 1, 1.0), (1, 1, SQRT2), (1, -1, SQRT2)):
            j0, j1 = max(0, -dy), ny - max(0, dy)
            a = trav[0:nx - dx, j0:j1] & trav[dx:nx, j0 + dy:j1 + dy]
            rows.append(idx[0:nx - dx, j0:j1][a])
            cols.append(idx[dx:nx, j0 + dy:j1 + dy][a])
            wts.append(np.full(int(a.sum()), c * self.map.res))
        r, cc, ww = np.concatenate(rows), np.concatenate(cols), np.concatenate(wts)
        G = csr_matrix((ww, (r, cc)), shape=(nx * ny, nx * ny))
        return dijkstra(G, directed=False, indices=start[0] * ny + start[1]).reshape(nx, ny)

    def _frontier_target(self, pose, esdf, within=None):
        lo = self.map.lo
        free = lo < AS.LO_FREE
        unk = (lo >= AS.LO_FREE) & (lo <= AS.LO_OCC) & self.inside
        fr = free & ndimage.binary_dilation(unk, structure=np.ones((3, 3), bool)) & (esdf > SAFE_M) & self.inside
        lab, n = ndimage.label(fr, structure=np.ones((3, 3), int))
        if n == 0:
            return None
        sizes = np.bincount(lab.ravel())
        fr &= sizes[lab] >= MIN_FRONTIER_CELLS
        if not fr.any():
            return None
        trav = free & (esdf > AS.RADIUS + AS.TRACK_MARGIN)
        s = self._idx(pose.x, pose.y)
        if not trav[s]:
            cand = np.argwhere(trav)
            if not len(cand):
                return None
            s = tuple(cand[int(np.argmin(np.hypot(cand[:, 0] - s[0], cand[:, 1] - s[1])))])
        dist = self._path_dist(trav, s)
        cells = np.argwhere(fr & np.isfinite(dist))
        if not len(cells):
            return None
        xs = self.map.x0 + (cells[:, 0] + 0.5) * self.map.res
        ys = self.map.y0 + (cells[:, 1] + 0.5) * self.map.res
        keep = np.ones(len(cells), bool)
        for bx, by in self.blacklist:
            keep &= np.hypot(xs - bx, ys - by) > BLACKLIST_M
        if within is not None:
            (cx, cy), rad = within
            keep &= np.hypot(xs - cx, ys - cy) <= rad
        if not keep.any():
            return None
        cells, xs, ys = cells[keep], xs[keep], ys[keep]
        dd = dist[cells[:, 0], cells[:, 1]]
        far = dd >= MIN_TARGET_DIST_M
        if far.any():
            dd = np.where(far, dd, np.inf)
        k = int(np.argmin(dd))
        return (float(xs[k]), float(ys[k]))

    def _is_frontier(self, xy):
        lo = self.map.lo
        i, j = self._idx(*xy)
        if not lo[i, j] < AS.LO_FREE:
            return False
        win = lo[max(0, i - 1):i + 2, max(0, j - 1):j + 2]
        ins = self.inside[max(0, i - 1):i + 2, max(0, j - 1):j + 2]
        return bool((((win >= AS.LO_FREE) & (win <= AS.LO_OCC)) & ins).any())

    # ---- arms ----
    def _lawnmower_points(self, pose):
        xmin, ymin, xmax, ymax = self.bounds
        if self.nominal is None:
            x0, y0, x1, y1 = xmin + 0.6, ymin + 0.6, xmax - 0.6, ymax - 0.6
        else:
            (nx_, ny_), r = self.nominal, self.radius
            x0, x1 = max(xmin + 0.6, nx_ - r), min(xmax - 0.6, nx_ + r)
            y0, y1 = max(ymin + 0.6, ny_ - r), min(ymax - 0.6, ny_ + r)
            if r == 0:
                return [self.nominal]
        nl = max(1, int(math.ceil((y1 - y0) / LANE_M)))
        lanes = [y0 + (k + 0.5) * (y1 - y0) / nl for k in range(nl)]
        npt = max(1, int(math.ceil((x1 - x0) / LANE_M)))
        xs = [x0 + (x1 - x0) * k / npt for k in range(npt + 1)] if x1 > x0 else [x0]
        if abs(pose.y - lanes[-1]) < abs(pose.y - lanes[0]):
            lanes = lanes[::-1]
        flip = abs(pose.x - xs[-1]) < abs(pose.x - xs[0])
        pts = []
        for k, y in enumerate(lanes):
            row = xs[::-1] if (k % 2 == 1) != flip else xs
            pts += [(x, y) for x in row]
        return pts

    def _random_point(self, pose, esdf):
        xmin, ymin, xmax, ymax = self.bounds
        for _ in range(20):
            if self.nominal is not None:
                r = self.radius * math.sqrt(self.rng.random())
                th = self.rng.uniform(-math.pi, math.pi)
                p = (self.nominal[0] + r * math.cos(th), self.nominal[1] + r * math.sin(th))
            else:
                r = self.rng.uniform(*WALK_STEP_M)
                th = self.rng.uniform(-math.pi, math.pi)
                p = (pose.x + r * math.cos(th), pose.y + r * math.sin(th))
            p = (min(max(p[0], xmin + 0.5), xmax - 0.5), min(max(p[1], ymin + 0.5), ymax - 0.5))
            q = self._snap(p, esdf, max_m=1.0)
            if q is not None:
                return q
        return None

    def _select(self, pose, esdf):
        """Next search target (x, y) or None when the arm has nothing left."""
        if self.arm == "frontier" or (self.arm == "nominal_frontier" and self.phase == "search"):
            within = None
            if self.arm == "nominal_frontier" and self.nominal is not None:
                within = (self.nominal, self.radius + DETECT_RANGE_M)
                t = self._frontier_target(pose, esdf, within)
                if t is not None:
                    return t
            return self._frontier_target(pose, esdf)
        if self.arm == "nominal_frontier":                 # phase "nominal"
            return self._snap(self.nominal, esdf)
        if self.arm == "lawnmower":
            if self.waypoints is None:
                self.waypoints = self._lawnmower_points(pose)
            while self.wp_i < len(self.waypoints):
                q = self._snap(self.waypoints[self.wp_i], esdf, max_m=1.5)
                if q is not None:
                    return q
                self.wp_i += 1
            return self._frontier_target(pose, esdf)
        if self.arm == "random_walk":
            if self.nominal is not None and self.radius == 0:
                return self._snap(self.nominal, esdf)
            return self._random_point(pose, esdf)
        return None                                        # oracle before B is known: hover

    def _done_with_target(self, failed: bool):
        if failed and self.target is not None:
            self.blacklist.append(self.target)
        if self.arm == "nominal_frontier" and self.phase == "nominal":
            self.phase = "search"
        if self.arm == "lawnmower" and self.waypoints is not None and self.wp_i < len(self.waypoints):
            self.wp_i += 1
        self.target = None

    def _update_target(self, pose):
        if self.b is not None:
            return
        t = pose.t
        if self.target is not None:
            d = math.hypot(self.target[0] - pose.x, self.target[1] - pose.y)
            if d < REACH_M:
                self._done_with_target(False)
            elif t - self.target_t > self.target_budget:
                self._done_with_target(True)
        frontier_mode = (self.arm == "frontier" or (self.arm == "nominal_frontier" and self.phase == "search")
                         or (self.arm == "lawnmower" and self.waypoints is not None
                             and self.wp_i >= len(self.waypoints)))
        recheck = (frontier_mode and self.target is not None and t - self.last_select_t >= SELECT_PERIOD_S
                   and not self._is_frontier(self.target))
        if self.target is None or recheck:
            if self.target is None and self.last_none and t - self.last_select_t < SELECT_PERIOD_S:
                return
            t0 = time.perf_counter()
            esdf = self._esdf_now()
            new = self._select(pose, esdf)
            self.select_ms.append((time.perf_counter() - t0) * 1e3)
            self.last_select_t = t
            self.last_none = new is None
            if new is not None and new != self.target:
                self.target, self.target_t = new, t
                self.target_budget = max(TARGET_TIMEOUT_S, TIMEOUT_PER_M * math.hypot(new[0] - pose.x, new[1] - pose.y))
                self.n_targets += 1
                self.path_xy = None
            elif new is None:
                self.target = None

    # ---- planner step ----
    def step(self, pose, scan, goal, grid, dt):
        new_occ = self.map.update(pose, scan)
        self._update_target(pose)
        if self.target is None:
            return Setpoint(0.0, 0.0, 0.0, 0.6)            # nothing to search: hover and turn
        g = (self.target[0], self.target[1], 1.0)
        due = pose.t - self.last_plan_t >= AS.REPLAN_PERIOD_S - 1e-9
        if due or self.path_xy is None or self._blocked_by(new_occ):
            self._plan(pose, g, None)
            self.last_plan_t = pose.t
        if self.path_xy is None:
            if self.b is None:
                self._done_with_target(True)
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        ex, ey = g[0] - pose.x, g[1] - pose.y
        dist_goal = math.hypot(ex, ey)
        c = self._carrot(pose.x, pose.y)
        cx, cy = c[0] - pose.x, c[1] - pose.y
        dc = math.hypot(cx, cy)
        if dc < 1e-6:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        clr = self._min_esdf((pose.x, pose.y), c)
        frac = (clr - AS.V_CLEAR_STOP_M) / (AS.V_CLEAR_FULL_M - AS.V_CLEAR_STOP_M)
        speed = AS.V_CRUISE * min(1.0, max(AS.V_MIN_FRAC, frac))
        # search targets are pass-through points: do not brake for them, only for B
        cap = dist_goal if self.b is not None else max(dist_goal, REACH_M + 0.5)
        speed = min(speed, AS.K_GOAL * cap)
        h = math.atan2(cy, cx)
        yaw_err = (h - pose.yaw + math.pi) % (2 * math.pi) - math.pi
        return Setpoint(speed * cx / dc, speed * cy / dc, 0.0, AS.K_YAW * yaw_err)

    def known_free_m2(self) -> float:
        return float(((self.map.lo < AS.LO_FREE) & self.inside).sum()) * self.map.res ** 2


def line_of_sight(w, x, y, bx, by) -> bool:
    d = math.hypot(bx - x, by - y)
    if d < 1e-6:
        return True
    hit = w.raycast(x, y, np.array([math.atan2(by - y, bx - x)]), d)[0]
    return not np.isfinite(hit) or hit >= d - 1e-6


def run_one(arm: str, family: str, seed: int, index: int, radius, preset: str = "ideal",
            max_time_s: float = MAX_TIME_S, keep_trace: bool = False, w=None) -> dict:
    """Fly one search. radius None => B unknown. Returns a row (and the trace if asked)."""
    cfg = A.run.DEFAULTS
    if w is None:
        w = A.world.make_world(family, seed, index, radius=cfg["vehicle"]["radius"])
    B = (float(w.goal[0]), float(w.goal[1]))
    nominal = nominal_for(w, seed, index, radius)
    pl = Explorer(arm, (w.xmin, w.ymin, w.xmax, w.ymax), nominal, radius, seed=(seed, index))
    pl.reset()
    look = nominal if nominal is not None else (B if arm == "oracle" else (0.5 * (w.xmin + w.xmax), 0.5 * (w.ymin + w.ymax)))
    vk = cfg["vehicle"]
    veh = A.vehicle.Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(look[1], look[0]), **vk)
    sensor = A.presets.make_sensor(preset, np.random.default_rng([seed, index, 7]))
    ad = A.adapter.SimAdapter(w, veh, sensor)
    HZ = A.vehicle.HZ
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    n_steps = int(round(max_time_s * HZ))
    lag = int(round(A.scorer.STUCK_WINDOW_S * HZ))
    rad = vk["radius"]
    t_found = None
    if arm == "oracle":
        pl.observe_goal(B)
        t_found = 0.0
    ts, xy, cum = [0.0], [(0.0, 0.0)], [0.0]
    step_ms = []
    for k in range(n_steps):
        if k % ratio == 0:
            px, py = float(veh.p[0]), float(veh.p[1])
            if t_found is None and math.hypot(B[0] - px, B[1] - py) <= DETECT_RANGE_M \
                    and line_of_sight(w, px, py, *B):
                t_found = round(float(veh.t), 3)
                pl.observe_goal(B)
            t0 = time.perf_counter()
            sp = pl.step(ad.pose(), ad.ranges(), None, None, pdt)
            step_ms.append((time.perf_counter() - t0) * 1e3)
            ad.send_setpoint(sp)
        ad.tick()
        px, py = float(veh.p[0]), float(veh.p[1])
        ts.append(veh.t)
        xy.append((px, py))
        if math.hypot(px - B[0], py - B[1]) <= A.scorer.GOAL_TOL:
            break
        if w.clearance(px, py) < rad:
            break
        seg = math.hypot(px - xy[-2][0], py - xy[-2][1])
        cum.append(cum[-1] + seg)
        if len(cum) > lag and cum[-1] - cum[-1 - lag] < STUCK_PATH_M:
            break
    res = score_search(ts, xy, w, B, rad)
    res.update({
        "arm": arm, "family": family, "seed": seed, "index": index, "preset": preset,
        "region_m": radius, "found": t_found is not None, "time_to_find_s": t_found,
        "time_to_b_s": res["time_to_goal_s"],
        "b": [round(B[0], 3), round(B[1], 3)],
        "nominal": None if nominal is None else [round(nominal[0], 3), round(nominal[1], 3)],
        "nominal_err_m": None if nominal is None else round(math.hypot(nominal[0] - B[0], nominal[1] - B[1]), 3),
        "search_targets": pl.n_targets, "known_free_m2": round(pl.known_free_m2(), 1),
        "no_path_replans": pl.no_path,
        "step_ms_mean": round(float(np.mean(step_ms)), 3), "step_ms_max": round(float(np.max(step_ms)), 2),
    })
    if keep_trace:
        return res, w, np.array(ts), np.array(xy)
    return res


def score_search(t, xy, w, B, radius) -> dict:
    """arena scorer.score with one change: stuck = truth path length over the last 10 s below
    STUCK_PATH_M (hovering), instead of net displacement below 0.2 m. A search loop that comes
    back to where it was 10 s ago is not stuck. reached / collision / timeout are the arena's."""
    t = np.asarray(t, float)
    xy = np.asarray(xy, float)
    clr = w.sdf(xy)
    i_r, i_c, _ = A.scorer.first_events(t, xy, clr, (B[0], B[1]), radius)
    seg = np.hypot(np.diff(xy[:, 0]), np.diff(xy[:, 1]))
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    lag = np.searchsorted(t, t - A.scorer.STUCK_WINDOW_S + 1e-9)
    ok = t >= A.scorer.STUCK_WINDOW_S - 1e-9
    s = np.flatnonzero(ok & (cum - cum[lag] < STUCK_PATH_M))
    i_s = int(s[0]) if len(s) else None
    cands = [(i, n) for i, n in ((i_r, "reached"), (i_c, "collision"), (i_s, "stuck")) if i is not None]
    end, outcome = min(cands) if cands else (len(t) - 1, "timeout")
    return {
        "outcome": outcome, "reached": outcome == "reached", "collision": outcome == "collision",
        "stuck": outcome == "stuck", "timeout": outcome == "timeout",
        "time_to_goal_s": round(float(t[end]), 3) if outcome == "reached" else None,
        "min_clearance_m": round(float(clr[: end + 1].min()), 4),
        "path_length_m": round(float(cum[end]), 3), "duration_s": round(float(t[end]), 3),
    }


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    k = lambda f: sum(1 for r in rows if r[f])
    med = lambda v: round(float(np.median(v)), 2) if v else None
    nf, nr, nc = k("found"), k("reached"), k("collision")
    return {
        "n": n,
        "found_pct": round(100 * nf / n, 1) if n else None, "found_ci": wilson(nf, n),
        "reached_pct": round(100 * nr / n, 1) if n else None, "reached_ci": wilson(nr, n),
        "collision_pct": round(100 * nc / n, 1) if n else None, "collision_ci": wilson(nc, n),
        "stuck_pct": round(100 * k("stuck") / n, 1) if n else None,
        "timeout_pct": round(100 * k("timeout") / n, 1) if n else None,
        "median_time_to_find_s": med([r["time_to_find_s"] for r in rows if r["found"]]),
        "median_time_to_b_s": med([r["time_to_b_s"] for r in rows if r["reached"]]),
        "median_path_m": med([r["path_length_m"] for r in rows]),
    }
