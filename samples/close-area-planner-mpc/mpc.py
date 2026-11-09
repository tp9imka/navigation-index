"""Linear MPC path follower in a half-plane corridor, solved with OSQP, on top of the arena A*.

Model (matches the arena vehicle, CONTRACT.md / vehicle.py):
  state x = (px, py, vx, vy), input u = (vx_cmd, vy_cmd), the velocity setpoint.
  The arena plant is a double integrator whose velocity follows the setpoint through a
  first-order lag tau = 0.15 s, with |a| <= 3 m/s^2 and |v| <= 2 m/s. Over one planner period
  dt the setpoint is held, so the exact zero-order-hold discretisation is linear:
      e = exp(-dt/tau)
      v+ = e v + (1 - e) u
      p+ = p + tau (1 - e) v + (dt - tau (1 - e)) u
  Input = velocity setpoint, not acceleration, because send_setpoint() takes a velocity and the
  lag is part of the plant: with this model the MPC output is sent as is, with no inner loop and
  no model mismatch except the arena's norm clipping (the QP uses per-axis boxes inside it).
  The acceleration in a step is largest at its start, a = (u - v)/tau, so |a| <= A_BOX is the
  linear constraint |u_k - v_k| <= tau A_BOX.

Horizon N = 20 steps of DT = 0.1 s (2.0 s), one solve per planner step (10 Hz).

Corridor (per horizon step k, around the reference point r_k), from the same 0.1 m grid the A*
ESDF is built on:
  1. Occupied boundary cells within CORRIDOR_R_M of r_k are candidate obstacle points. If the
     ESDF at r_k is above CORRIDOR_R_M there are none (the ESDF is the gate and its value is the
     first, tightest plane's distance).
  2. Repeat up to MAX_OBS_PLANES times: take the nearest remaining point o, add the half-plane
     n.p <= n.o - min(OFFSET_M, |o - r_k|) with n = (o - r_k)/|o - r_k|, drop every point with
     n.(q - o) >= 0 (behind that plane, so at least the offset away from any p that satisfies
     it). This is the nearest-point separating-plane step of safe flight corridors
     (Liu et al., RA-L 2017) without the ellipsoid.
  3. Four window planes |p - r_k|_inf <= WINDOW_M, with WINDOW_M sqrt(2) + OFFSET_M <= CORRIDOR_R_M,
     so obstacle points outside the search radius cannot be closer than OFFSET_M.
  OFFSET_M = vehicle radius 0.15 + CORRIDOR_MARGIN_M 0.05 (grid discretisation: an occupied cell
  centre is within 0.05 m of a surface or inside it). Corridor rows are soft: one slack s_k >= 0
  per step, penalised hard (W_SLACK_L1, W_SLACK_L2), so the QP stays feasible when the vehicle is
  already inside the offset band. Runs where the slack is used at k = 1 are counted.

Reference: from the projection of the vehicle onto the A* path, march forward along the path
at the carrot follower's speed rule (V_CRUISE scaled by the ESDF at the reference point, capped
by K_GOAL x remaining path length), giving r_k and v_ref_k.

Cost: sum_k Q_P |p_k - r_k|^2 + Q_V |v_k - v_ref_k|^2 + R_DU |u_k - u_(k-1)|^2 (u_(-1) = last
command) + terminal Q_N |p_N - r_N|^2 + slack penalty.

Warm start: the previous primal solution shifted by one step (OSQP also keeps the previous
duals). Matrix sparsity is fixed at setup; each step updates q, l, u and the corridor values of A.
Timing: wall time around update + solve, plus OSQP's own solve_time, plus corridor build time.
If OSQP does not return "solved", the step falls back to the carrot command and is counted.
"""
from __future__ import annotations

import math
import time

import numpy as np
import osqp
import scipy.sparse as sp

import arena

AStarESDF = arena.astar_esdf.AStarESDF
Setpoint = arena.Setpoint
AS = arena.astar_esdf

# ---- model (arena vehicle) ----
TAU = 0.15                    # s, velocity lag (CONTRACT.md)
DT = 0.1                      # s, MPC step = planner period (plan_hz 10)
N = 20                        # horizon steps => 2.0 s
V_BOX = 1.4                   # m/s per axis => |v| <= 1.98 < 2.0 arena limit
A_BOX = 2.1                   # m/s^2 per axis => |a| <= 2.97 < 3.0 arena limit
# ---- corridor ----
RADIUS = AS.RADIUS            # 0.15 m
CORRIDOR_MARGIN_M = 0.05      # m, grid discretisation (occupied centre within res/2 of a surface)
OFFSET_M = RADIUS + CORRIDOR_MARGIN_M
CORRIDOR_R_M = 2.0            # m, obstacle search radius around each reference point
WINDOW_M = 1.25               # m, half side of the box around r_k; 1.25*sqrt(2) + 0.2 <= 2.0
MAX_OBS_PLANES = 8            # obstacle half-planes per step (plus 4 window planes)
# ---- cost ----
Q_P = 10.0
Q_N = 50.0
Q_V = 1.0
R_DU = 2.0
W_SLACK_L1 = 1e4
W_SLACK_L2 = 1e4
# ---- solver ----
OSQP_SETTINGS = dict(verbose=False, warm_starting=True, polishing=False, eps_abs=1e-4,
                     eps_rel=1e-4, max_iter=4000, adaptive_rho=True)
INF = 1e20                    # OSQP treats |bound| >= 1e20 as infinite

M_ROWS = MAX_OBS_PLANES + 4


def discretise(dt: float = DT, tau: float = TAU):
    e = math.exp(-dt / tau)
    a_pv, b_p, b_v = tau * (1 - e), dt - tau * (1 - e), 1 - e
    A = np.array([[1, 0, a_pv, 0], [0, 1, 0, a_pv], [0, 0, e, 0], [0, 0, 0, e]])
    B = np.array([[b_p, 0], [0, b_p], [b_v, 0], [0, b_v]])
    return A, B


class CorridorQP:
    """Fixed-structure QP. z = [x_0..x_N (4 each), u_0..u_(N-1) (2 each), s_1..s_N]."""

    def __init__(self, n: int = N, dt: float = DT, tau: float = TAU, warm: bool = True):
        self.n, self.dt, self.tau, self.warm = n, dt, tau, warm
        self.Ad, self.Bd = discretise(dt, tau)
        self.nx, self.nu = 4 * (n + 1), 2 * n
        self.nz = self.nx + self.nu + n
        self._build()
        self.prev = None

    # index helpers
    def ix(self, k, j):
        return 4 * k + j

    def iu(self, k, j):
        return self.nx + 2 * k + j

    def is_(self, k):              # slack of step k = 1..N
        return self.nx + self.nu + k - 1

    def _build(self):
        n = self.n
        # ---- P (constant) ----
        P = sp.lil_matrix((self.nz, self.nz))
        for k in range(1, n + 1):
            wp = Q_N if k == n else Q_P
            for j in (0, 1):
                P[self.ix(k, j), self.ix(k, j)] += 2 * wp
                P[self.ix(k, 2 + j), self.ix(k, 2 + j)] += 2 * Q_V
            P[self.is_(k), self.is_(k)] += 2 * W_SLACK_L2
        for k in range(n):
            for j in (0, 1):
                a = self.iu(k, j)
                P[a, a] += 2 * R_DU * (2 if k < n - 1 else 1)
                if k < n - 1:
                    b = self.iu(k + 1, j)
                    P[a, b] -= 2 * R_DU
                    P[b, a] -= 2 * R_DU
        self.P = sp.triu(P.tocsc(), format="csc")
        # ---- A in COO with a fixed entry list ----
        rows, cols, vals = [], [], []
        r = 0

        def add(rr, c, v):
            rows.append(rr); cols.append(c); vals.append(v)

        self.r_init = r
        for j in range(4):
            add(r, self.ix(0, j), 1.0); r += 1
        self.r_dyn = r
        for k in range(n):
            for i in range(4):
                add(r, self.ix(k + 1, i), 1.0)
                for j in range(4):
                    if self.Ad[i, j] != 0:
                        add(r, self.ix(k, j), -self.Ad[i, j])
                for j in range(2):
                    if self.Bd[i, j] != 0:
                        add(r, self.iu(k, j), -self.Bd[i, j])
                r += 1
        self.r_vbox = r
        for k in range(1, n + 1):
            for j in (0, 1):
                add(r, self.ix(k, 2 + j), 1.0); r += 1
        self.r_ubox = r
        for k in range(n):
            for j in (0, 1):
                add(r, self.iu(k, j), 1.0); r += 1
        self.r_acc = r
        for k in range(n):
            for j in (0, 1):
                add(r, self.iu(k, j), 1.0)
                add(r, self.ix(k, 2 + j), -1.0); r += 1
        self.r_slack = r
        for k in range(1, n + 1):
            add(r, self.is_(k), 1.0); r += 1
        self.r_cor = r
        self.cor_entries = len(vals)       # corridor entries start here, 3 per row
        for k in range(1, n + 1):
            for m in range(M_ROWS):
                add(r, self.ix(k, 0), 1.0)
                add(r, self.ix(k, 1), 1.0)
                add(r, self.is_(k), -1.0)
                r += 1
        self.m = r
        rows, cols = np.array(rows), np.array(cols)
        self.coo_vals = np.array(vals, float)
        # permutation COO order => CSC data order (no explicit zero is ever dropped this way)
        probe = sp.coo_matrix((np.arange(1, len(rows) + 1, dtype=float), (rows, cols)), shape=(self.m, self.nz)).tocsc()
        probe.sort_indices()
        self.perm = probe.data.astype(int) - 1
        self.A = sp.csc_matrix((self.coo_vals[self.perm], probe.indices.copy(), probe.indptr.copy()),
                               shape=(self.m, self.nz))
        self.l = np.zeros(self.m)
        self.u = np.zeros(self.m)
        self.l[self.r_vbox:self.r_ubox] = -V_BOX; self.u[self.r_vbox:self.r_ubox] = V_BOX
        self.l[self.r_ubox:self.r_acc] = -V_BOX; self.u[self.r_ubox:self.r_acc] = V_BOX
        ta = self.tau * A_BOX
        self.l[self.r_acc:self.r_slack] = -ta; self.u[self.r_acc:self.r_slack] = ta
        self.l[self.r_slack:self.r_cor] = 0.0; self.u[self.r_slack:self.r_cor] = INF
        self.l[self.r_cor:] = -INF; self.u[self.r_cor:] = INF
        self.q = np.zeros(self.nz)
        self.solver = osqp.OSQP()
        self.solver.setup(self.P, self.q, self.A, self.l, self.u,
                          **dict(OSQP_SETTINGS, warm_starting=self.warm))

    def solve(self, x0, ref, vref, normals, offsets, u_prev):
        """ref, vref: (N, 2) for k = 1..N. normals: (N, M_ROWS, 2), offsets: (N, M_ROWS).
        Returns (z, info dict)."""
        n = self.n
        q = np.zeros(self.nz)
        for k in range(1, n + 1):
            wp = Q_N if k == n else Q_P
            q[self.ix(k, 0):self.ix(k, 2)] = -2 * wp * ref[k - 1]
            q[self.ix(k, 2):self.ix(k, 4)] = -2 * Q_V * vref[k - 1]
            q[self.is_(k)] = W_SLACK_L1
        q[self.iu(0, 0):self.iu(0, 2)] = -2 * R_DU * np.asarray(u_prev)
        # the u_(-1) term also adds R_DU on u_0's diagonal: |u_0 - u_prev|^2 => folded in P via k<n-1 rule
        vals = self.coo_vals.copy()
        c = self.cor_entries
        nrm = normals.reshape(-1, 2)
        vals[c + 0::3][:len(nrm)] = nrm[:, 0]
        vals[c + 1::3][:len(nrm)] = nrm[:, 1]
        l, u = self.l.copy(), self.u.copy()
        l[self.r_init:self.r_init + 4] = x0
        u[self.r_init:self.r_init + 4] = x0
        u[self.r_cor:] = offsets.ravel()
        t0 = time.perf_counter()
        self.solver.update(q=q, l=l, u=u, Ax=vals[self.perm])
        if self.warm and self.prev is not None:
            zp = self.prev
            zs = zp.copy()
            X = zp[:self.nx].reshape(n + 1, 4); U = zp[self.nx:self.nx + self.nu].reshape(n, 2)
            S = zp[self.nx + self.nu:]
            zs[:self.nx] = np.vstack([X[1:], X[-1:]]).ravel()
            zs[:4] = x0
            zs[self.nx:self.nx + self.nu] = np.vstack([U[1:], U[-1:]]).ravel()
            zs[self.nx + self.nu:] = np.concatenate([S[1:], S[-1:]])
            self.solver.warm_start(x=zs)
        res = self.solver.solve()
        wall_ms = (time.perf_counter() - t0) * 1e3
        ok = res.info.status in ("solved", "solved inaccurate") and res.x is not None and np.all(np.isfinite(res.x))
        if ok:
            self.prev = res.x.copy()
        else:
            self.prev = None
        return (res.x if ok else None), {"status": res.info.status, "iter": int(res.info.iter),
                                          "qp_ms": wall_ms, "osqp_solve_ms": res.info.solve_time * 1e3}


def halfplane_polygon(normals, offsets, center, half=3.0):
    """Polygon of {p : n.p <= b} clipped to a square around center (for plots)."""
    poly = [(center[0] - half, center[1] - half), (center[0] + half, center[1] - half),
            (center[0] + half, center[1] + half), (center[0] - half, center[1] + half)]
    for nv, b in zip(normals, offsets):
        if b >= INF / 2:
            continue
        out = []
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            fp, fq = nv[0] * p[0] + nv[1] * p[1] - b, nv[0] * q[0] + nv[1] * q[1] - b
            if fp <= 0:
                out.append(p)
            if fp * fq < 0:
                t = fp / (fp - fq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        poly = out
        if not poly:
            break
    return poly


def dist_to_polyline(px, py, P) -> float:
    if P is None or len(P) == 0:
        return math.nan
    if len(P) == 1:
        return math.hypot(px - P[0][0], py - P[0][1])
    a, b = P[:-1], P[1:]
    ab = b - a
    L = np.maximum((ab ** 2).sum(1), 1e-12)
    t = np.clip(((px - a[:, 0]) * ab[:, 0] + (py - a[:, 1]) * ab[:, 1]) / L, 0, 1)
    q = a + t[:, None] * ab
    return float(np.hypot(q[:, 0] - px, q[:, 1] - py).min())


def log_tracking(pl, pose):
    """Tracking error at a planner step: distance to the current A* path (replanned every 0.4 s
    from the vehicle, so it restarts near zero) and to the first A* path of the run (t = 0)."""
    if pl.first_path is None and pl.path_xy is not None:
        pl.first_path = pl.path_xy.copy()
    pl.track_err.append(dist_to_polyline(pose.x, pose.y, pl.path_xy))
    pl.track_err_first.append(dist_to_polyline(pose.x, pose.y, pl.first_path))


class CarrotTracked(AStarESDF):
    """The arena's A* + carrot follower, unchanged, plus tracking-error and step-time logging."""

    def __init__(self, known_map: bool = True):
        super().__init__(known_map=known_map)
        self.name = "astar_carrot"
        self.track_err: list[float] = []
        self.track_err_first: list[float] = []
        self.step_ms: list[float] = []

    def reset(self) -> None:
        super().reset()
        self.first_path = None

    def step(self, pose, scan, goal, grid, dt):
        t0 = time.perf_counter()
        sp_ = super().step(pose, scan, goal, grid, dt)
        self.step_ms.append((time.perf_counter() - t0) * 1e3)
        log_tracking(self, pose)
        return sp_


class AStarMPC(AStarESDF):
    """Same A* and replanning as the arena planner; the carrot follower is replaced by CorridorQP."""

    def __init__(self, known_map: bool = True, warm: bool = True, use_corridor: bool = True,
                 clearance_speed: bool = True, record: bool = False):
        self.clearance_speed = clearance_speed     # False => reference at V_BOX, no ESDF slow-down
        self.qp = CorridorQP(warm=warm)
        self.record = record
        self.use_corridor = use_corridor
        super().__init__(known_map=known_map)
        self.name = "astar_mpc"
        self.track_err: list[float] = []
        self.track_err_first: list[float] = []
        self.step_ms: list[float] = []
        self.qp_ms: list[float] = []
        self.osqp_ms: list[float] = []
        self.corridor_ms: list[float] = []
        self.iters: list[int] = []
        self.fail_steps = 0
        self.slack_steps = 0           # steps where the k = 1 corridor slack > 1 cm
        self.active_steps = 0          # steps where an obstacle half-plane is active at some k
        self.truncated = 0             # corridors with obstacle points left after MAX_OBS_PLANES
        self.log: list[dict] = []

    def reset(self) -> None:
        super().reset()
        self.u_prev = np.zeros(2)
        self.bnd = None
        self.first_path = None
        if hasattr(self, "qp"):
            self.qp.prev = None

    # ---- corridor ----
    def _boundary_points(self, grid):
        """Occupied cells with a free 4-neighbour, padded with occupied cells outside the grid."""
        if self.bnd is None:
            res = grid.res
            pad = int(math.ceil(CORRIDOR_R_M / res)) + 1
            occ = np.pad(grid.occ, pad, constant_values=True)
            free = ~occ
            nb = np.zeros_like(occ)
            nb[1:, :] |= free[:-1, :]; nb[:-1, :] |= free[1:, :]
            nb[:, 1:] |= free[:, :-1]; nb[:, :-1] |= free[:, 1:]
            self.bnd = (occ & nb, pad, res, grid.x0, grid.y0)
        return self.bnd

    def corridor(self, r, grid):
        """(normals (M_ROWS, 2), offsets (M_ROWS,)) for reference point r."""
        bnd, pad, res, x0, y0 = self._boundary_points(grid)
        normals = np.tile([1.0, 0.0], (M_ROWS, 1))
        offsets = np.full(M_ROWS, INF)
        normals[:4] = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        offsets[:4] = [r[0] + WINDOW_M, -r[0] + WINDOW_M, r[1] + WINDOW_M, -r[1] + WINDOW_M]
        ci, cj = self._idx(r[0], r[1])
        if self.esdf[ci, cj] > CORRIDOR_R_M:
            return normals, offsets, 0
        w = int(math.ceil(CORRIDOR_R_M / res))
        ii, jj = ci + pad, cj + pad
        sub = bnd[ii - w:ii + w + 1, jj - w:jj + w + 1]
        bi, bj = np.nonzero(sub)
        pts = np.column_stack([x0 + (bi + ii - w - pad + 0.5) * res, y0 + (bj + jj - w - pad + 0.5) * res])
        d = np.hypot(pts[:, 0] - r[0], pts[:, 1] - r[1])
        alive = (d <= CORRIDOR_R_M) & (d > 1e-6)
        m = 4
        while alive.any() and m < M_ROWS:
            i = int(np.flatnonzero(alive)[np.argmin(d[alive])])
            o = pts[i]
            nv = (o - r) / d[i]
            normals[m] = nv
            offsets[m] = nv @ o - min(OFFSET_M, d[i])
            alive &= (pts - o) @ nv < 0
            m += 1
        return normals, offsets, int(alive.any())

    # ---- reference ----
    def _reference(self, px, py, goal):
        P = self.path_xy
        if len(P) == 1:
            g = np.tile(P[0], (N, 1))
            return g, np.zeros((N, 2))
        a, b = P[:-1], P[1:]
        ab = b - a
        seg = np.sqrt((ab ** 2).sum(1))
        L = np.maximum(seg ** 2, 1e-12)
        t = np.clip(((px - a[:, 0]) * ab[:, 0] + (py - a[:, 1]) * ab[:, 1]) / L, 0, 1)
        q = a + t[:, None] * ab
        i = int(np.argmin(np.hypot(q[:, 0] - px, q[:, 1] - py)))
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        s = cum[i] + t[i] * seg[i]
        total = cum[-1]

        def at(sv):
            sv = min(max(sv, 0.0), total)
            j = min(int(np.searchsorted(cum, sv, side="right")) - 1, len(seg) - 1)
            u = (sv - cum[j]) / max(seg[j], 1e-9)
            return a[j] + u * ab[j], ab[j] / max(seg[j], 1e-9)

        refs, vrefs = np.zeros((N, 2)), np.zeros((N, 2))
        for k in range(N):
            pt, tan = at(s)
            ci, cj = self._idx(pt[0], pt[1])
            clr = float(self.esdf[ci, cj])
            frac = (clr - AS.V_CLEAR_STOP_M) / (AS.V_CLEAR_FULL_M - AS.V_CLEAR_STOP_M)
            v = AS.V_CRUISE * min(1.0, max(AS.V_MIN_FRAC, frac)) if self.clearance_speed else V_BOX
            v = min(v, AS.K_GOAL * (total - s))
            s = min(s + v * DT, total)
            pt, tan = at(s)
            refs[k] = pt
            vrefs[k] = tan * (v if s < total else 0.0)
        return refs, vrefs

    def step(self, pose, scan, goal, grid, dt):
        t0 = time.perf_counter()
        # same replanning as AStarESDF.step (known map: no map update)
        new_occ = np.zeros((0, 2), int)
        if not self.known_map:
            new_occ = self.map.update(pose, scan)
        due = pose.t - self.last_plan_t >= AS.REPLAN_PERIOD_S - 1e-9
        if due or self.path_xy is None or self._blocked_by(new_occ):
            self._plan(pose, goal, grid)
            self.last_plan_t = pose.t
        if self.path_xy is None:
            self.u_prev = np.zeros(2)
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        refs, vrefs = self._reference(pose.x, pose.y, goal)
        tc = time.perf_counter()
        if grid is None:
            raise ValueError("AStarMPC corridor needs the prior grid (known_map=True)")
        cors = [self.corridor(r, grid) for r in refs]
        normals = np.stack([c[0] for c in cors])
        offsets = np.stack([c[1] for c in cors])
        if not self.use_corridor:              # ablation: window planes only
            offsets[:, 4:] = INF
        self.truncated += sum(c[2] for c in cors)
        self.corridor_ms.append((time.perf_counter() - tc) * 1e3)
        x0 = np.array([pose.x, pose.y, pose.vx, pose.vy])
        z, info = self.qp.solve(x0, refs, vrefs, normals, offsets, self.u_prev)
        self.qp_ms.append(info["qp_ms"])
        self.osqp_ms.append(info["osqp_solve_ms"])
        self.iters.append(info["iter"])
        if z is None:
            self.fail_steps += 1
            sp_ = AStarESDF.step(self, pose, scan, goal, grid, dt)   # carrot fallback (no replan: just planned)
            u0 = np.array([sp_.vx, sp_.vy])
        else:
            u0 = z[self.qp.iu(0, 0):self.qp.iu(0, 2)]
            if z[self.qp.is_(1)] > 0.01:
                self.slack_steps += 1
            P = z[:self.qp.nx].reshape(N + 1, 4)[1:, :2]
            g = np.einsum("kmj,kj->km", normals[:, 4:], P) - offsets[:, 4:]
            if (g > -0.01).any():
                self.active_steps += 1
        self.u_prev = u0.copy()
        h = math.atan2(u0[1], u0[0]) if np.hypot(*u0) > 0.05 else pose.yaw
        yaw_err = (h - pose.yaw + math.pi) % (2 * math.pi) - math.pi
        if self.record:
            pred = None if z is None else z[:self.qp.nx].reshape(N + 1, 4)[:, :2].copy()
            self.log.append({"t": pose.t, "p": (pose.x, pose.y), "refs": refs, "normals": normals,
                             "offsets": offsets, "pred": pred})
        self.step_ms.append((time.perf_counter() - t0) * 1e3)
        log_tracking(self, pose)
        return Setpoint(float(u0[0]), float(u0[1]), 0.0, AS.K_YAW * yaw_err)


def make(**kw):
    return AStarMPC(**kw)
