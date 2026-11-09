"""Bug2 (Lumelsky and Stepanov 1987) and TangentBug (Kamon, Rivlin and Rimon 1998) on range returns.

Both read only the pose and the range scan. Yaw follows the commanded velocity, so the front
beam of a sparse fan faces travel and, while wall-following with the wall on the right, the
right beam faces the wall. The completeness arguments in both papers assume a point robot,
perfect position and a continuous contact (Bug2) or range (TangentBug) sensor; the arena gives
a 0.15 m radius, a lagged vehicle, noisy beams with dropout and a 60 s budget, so this file
measures how much of the guarantee survives.

Shared pieces
- Wall follow (WF): nearest return u_n at d_n (world-frame direction). Command V_WF along the
  tangent (u_n rotated by side * 90 deg) plus K_D * (d_n - RADIUS - D_DES) along u_n.
  side = +1 keeps the wall on the right (turns left round it). No return within WF_LOST_M:
  turn towards where the wall was (last u_n rotated by side * 45 deg), the convex-corner case.
- Brake: for every beam with d < 1.5 m, the velocity component towards it is capped at
  K_BRAKE * (d - RADIUS - C_STOP). A wall between beams is not seen and not braked for.

Bug2 state machine (class Bug2)
  GO      move along the m-line (start => B) at V_GO.
          => FOLLOW when a return within HIT_CONE of the goal direction is closer than
             RADIUS + D_HIT. Store hit point H and d_hit = |H - B|.
  FOLLOW  wall follow with side = BUG2_SIDE (fixed, as in Bug2).
          => GO (leave rule) when the vehicle crosses the m-line (signed distance changes sign
             or |distance| < M_TOL, projection inside the segment), |p - B| < d_hit - LEAVE_M,
             and no return within D_FREE in +/- 45 deg of the goal direction.
          => FAIL when it comes back within LOOP_R of H after having been LOOP_AWAY m away
             (Bug2's "goal unreachable" exit).
  FAIL    zero velocity (the arena scores this as stuck).

TangentBug state machine (class TangentBug)
  Every scan first passes a dropout hold (DROPOUT_HOLD): a beam with no return that had one in
  the previous scan keeps the old return for one scan. Without it, the arena's 2 % dropout put
  false free beams inside the U cup and the planner left FOLLOW at once (dev seed 1).
  M2G     motion to goal. If the segment p => B, cut at min(|p - B|, R_SENSE), keeps
          RADIUS + TB_MARGIN from every return point: head to B. Otherwise build tangent
          points O_i at range discontinuities (adjacent beams with one return and one no-return,
          or a jump > JUMP_M): the nearer return, turned away from its obstacle by
          asin((RADIUS + TB_MARGIN) / d). Head to the O_i that minimises
          h = |p - O_i| + |O_i - B|.
          => FOLLOW when h exceeds its running minimum by more than H_INC_M (Kamon's local
             minimum test), or no O_i exists while blocked. side = the side of the last chosen
             O_i (O_i left of the goal direction => obstacle on the right => side +1).
  FOLLOW  wall follow. d_followed = min |q - B| over the returns that blocked the segment to B
          on entry, then over returns q within FOLLOW_R of the vehicle seen since (points of
          the followed obstacle).
          d_reach = min |p + R_SENSE u_j - B| over free beams j (no return within R_SENSE: the
          visible free point closest to B), 0 if B is in range and the segment to it is clear.
          Simplification: Kamon's d_reach also counts visible obstacle points; with ray returns
          and no obstacle segmentation, those made it leave in the same step it entered FOLLOW
          (dev seed 1), so only free-space points count here.
          => M2G when d_reach < d_followed - TB_LEAVE_M. The h minimum is reset.
"""
from __future__ import annotations

import math

try:
    from .arena import VEHICLE, Planner, Setpoint
except ImportError:
    from arena import VEHICLE, Planner, Setpoint

RADIUS = VEHICLE["radius"]        # 0.15 m
# ---- motion ----
V_GO = 1.0                        # m/s towards B (or a tangent point)
K_GOAL = 1.0                      # 1/s, speed cap = K_GOAL * distance to B
K_YAW = 1.5                       # 1/s
K_BRAKE = 1.5                     # 1/s, range brake gain
C_STOP = 0.1                      # m, clearance at which the brake allows zero speed towards a return
# ---- wall follow ----
V_WF = 0.6                        # m/s along the wall
D_DES = 0.45                      # m, clearance kept from the wall
K_D = 1.0                         # 1/s, distance correction gain
WF_LOST_M = 1.5                   # m, no return closer => wall lost (convex corner)
# ---- Bug2 ----
HIT_CONE = math.radians(30)       # rad, half-width of the goal-direction cone for a hit
D_HIT = 0.5                       # m, clearance in that cone that counts as a hit
BUG2_SIDE = 1                     # +1 wall on the right; fixed as in Bug2
M_TOL = 0.1                       # m, |distance to m-line| that counts as on it
LEAVE_M = 0.5                     # m, leave only this much closer to B than the hit point
D_FREE = 1.0                      # m, goal direction must be free this far to leave
LOOP_R = 0.5                      # m, back at H within this => goal unreachable
LOOP_AWAY = 1.5                   # m, must first have been this far from H
# ---- TangentBug ----
R_SENSE = 4.0                     # m, range used for the free-segment and reach tests (cf4 max)
TB_MARGIN = 0.15                  # m, extra clearance for the free-segment test and tangent offset
JUMP_M = 0.6                      # m, range jump between adjacent beams that marks a discontinuity
H_INC_M = 0.3                     # m, h above its running minimum => local minimum => FOLLOW
FOLLOW_R = 1.5                    # m, returns this close are the followed obstacle
TB_LEAVE_M = 0.3                  # m, leave when d_reach < d_followed - this
DROPOUT_HOLD = True               # hold a beam's last return for one scan when it drops out


def wrap(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


class _BugBase(Planner):
    def reset(self):
        self.mode = "go"
        self.side = 1
        self.u_last = None
        self.log = []                     # (t, mode) on each mode change

    def _set(self, t, mode):
        if mode != self.mode:
            self.mode = mode
            self.log.append((round(t, 2), mode))

    @staticmethod
    def _returns(pose, scan):
        return [(wrap(pose.yaw + a), d) for a, d in zip(scan.angles, scan.distances) if math.isfinite(d)]

    def _wall_follow(self, rets):
        near = min(rets, key=lambda r: r[1], default=None)
        if near is not None and near[1] < WF_LOST_M:
            phi, d = near
            self.u_last = phi
            ux, uy = math.cos(phi), math.sin(phi)
            tx, ty = -self.side * uy, self.side * ux
            e = K_D * (d - RADIUS - D_DES)
            return V_WF * tx + e * ux, V_WF * ty + e * uy
        base = self.u_last if self.u_last is not None else 0.0
        a = base + self.side * math.radians(45)
        return V_WF * math.cos(a), V_WF * math.sin(a)

    @staticmethod
    def _brake(vx, vy, rets):
        for phi, d in rets:
            if d > 1.5:
                continue
            ux, uy = math.cos(phi), math.sin(phi)
            toward = vx * ux + vy * uy
            cap = max(0.0, K_BRAKE * (d - RADIUS - C_STOP))
            if toward > cap:
                vx -= (toward - cap) * ux
                vy -= (toward - cap) * uy
        return vx, vy

    def _out(self, pose, vx, vy, hg):
        h = math.atan2(vy, vx) if math.hypot(vx, vy) > 0.05 else hg
        return Setpoint(vx, vy, 0.0, K_YAW * wrap(h - pose.yaw))


class Bug2(_BugBase):
    name = "bug2"

    def reset(self):
        super().reset()
        self.start = None
        self.hit = None
        self.d_hit = math.inf
        self.away = False
        self.prev_s = None

    def step(self, pose, scan, goal, grid, dt):
        t = pose.t
        if self.start is None:
            self.start = (pose.x, pose.y)
        gx, gy = goal[0], goal[1]
        ex, ey = gx - pose.x, gy - pose.y
        dist = math.hypot(ex, ey)
        hg = math.atan2(ey, ex)
        rets = self._returns(pose, scan)

        # signed distance to the m-line and projection fraction along it
        sx, sy = self.start
        lx, ly = gx - sx, gy - sy
        L = math.hypot(lx, ly) or 1e-9
        s = ((pose.x - sx) * ly - (pose.y - sy) * lx) / L
        frac = ((pose.x - sx) * lx + (pose.y - sy) * ly) / (L * L)
        crossed = self.prev_s is not None and (s == 0 or (s > 0) != (self.prev_s > 0) or abs(s) < M_TOL)
        self.prev_s = s

        if self.mode == "go":
            if any(abs(wrap(phi - hg)) <= HIT_CONE and d < RADIUS + D_HIT for phi, d in rets):
                self.hit, self.d_hit, self.away = (pose.x, pose.y), dist, False
                self.side = BUG2_SIDE
                self._set(t, "follow")
        elif self.mode == "follow":
            dh = math.hypot(pose.x - self.hit[0], pose.y - self.hit[1])
            if dh > LOOP_AWAY:
                self.away = True
            goal_free = all(not (abs(wrap(phi - hg)) <= math.radians(45) and d < D_FREE) for phi, d in rets)
            if crossed and 0.0 <= frac <= 1.0 and dist < self.d_hit - LEAVE_M and goal_free:
                self._set(t, "go")
            elif self.away and dh < LOOP_R:
                self._set(t, "fail")

        if self.mode == "go":
            v = min(V_GO, K_GOAL * dist)
            # follow the m-line: aim at B with a pull back onto the line
            vx, vy = v * ex / max(dist, 1e-9), v * ey / max(dist, 1e-9)
            vx -= 0.5 * s * ly / L
            vy += 0.5 * s * lx / L
        elif self.mode == "follow":
            vx, vy = self._wall_follow(rets)
        else:
            vx = vy = 0.0
        vx, vy = self._brake(vx, vy, rets)
        return self._out(pose, vx, vy, hg)


class TangentBug(_BugBase):
    name = "tangent_bug"

    def reset(self):
        super().reset()
        self.h_min = math.inf
        self.d_followed = math.inf
        self.last_side = 1
        self.m2g_steps = 0
        self.follow_entries = 0
        self.prev_d = None

    @staticmethod
    def _blockers(px, py, gx, gy, length, pts, clear):
        """Return points within `clear` of the segment p => B cut at `length`."""
        dx, dy = gx - px, gy - py
        n = math.hypot(dx, dy) or 1e-9
        ux, uy = dx / n, dy / n
        out = []
        for qx, qy in pts:
            rx, ry = qx - px, qy - py
            along = rx * ux + ry * uy
            if -clear <= along <= length + clear and abs(rx * uy - ry * ux) < clear:
                out.append((qx, qy))
        return out

    def _tangents(self, pose, scan):
        ang = [wrap(pose.yaw + a) for a in scan.angles]
        dd = list(scan.distances)
        n = len(ang)
        out = []
        if n < 2:
            return out
        for i in range(n):
            j = (i + 1) % n
            di, dj = dd[i], dd[j]
            fi, fj = math.isfinite(di) and di <= R_SENSE, math.isfinite(dj) and dj <= R_SENSE
            if fi == fj and (not fi or abs(di - dj) <= JUMP_M):
                continue
            # k = the nearer return, o = the other beam (the open side)
            if fi and (not fj or di < dj):
                k, o = i, j
            else:
                k, o = j, i
            d = dd[k]
            turn = math.asin(min(1.0, (RADIUS + TB_MARGIN) / max(d, 1e-3)))
            sgn = 1.0 if wrap(ang[o] - ang[k]) > 0 else -1.0
            a = ang[k] + sgn * turn
            out.append((pose.x + d * math.cos(a), pose.y + d * math.sin(a)))
        return out

    def _hold(self, scan):
        """Dropout hold: a beam with no return now but a return in the previous scan keeps that
        return for one scan (a dropped beam would otherwise read as free space and make a false
        tangent point or a false leave)."""
        d = list(scan.distances)
        prev = self.prev_d
        self.prev_d = list(scan.distances)
        if DROPOUT_HOLD and prev is not None and len(prev) == len(d):
            d = [p if (not math.isfinite(c) and math.isfinite(p)) else c for c, p in zip(d, prev)]
        return type(scan)(t=scan.t, angles=scan.angles, distances=d, max_range=scan.max_range)

    def step(self, pose, scan, goal, grid, dt):
        t = pose.t
        scan = self._hold(scan)
        gx, gy = goal[0], goal[1]
        ex, ey = gx - pose.x, gy - pose.y
        dist = math.hypot(ex, ey)
        hg = math.atan2(ey, ex)
        rets = self._returns(pose, scan)
        pts = [(pose.x + d * math.cos(phi), pose.y + d * math.sin(phi)) for phi, d in rets if d <= R_SENSE]
        clear = RADIUS + TB_MARGIN
        blockers = self._blockers(pose.x, pose.y, gx, gy, min(dist, R_SENSE), pts, clear)
        free = not blockers

        target = None
        if self.mode == "go":
            self.m2g_steps += 1
            if free:
                target = (gx, gy)
                h = dist
            else:
                cands = self._tangents(pose, scan)
                if cands:
                    target = min(cands, key=lambda o: math.hypot(o[0] - pose.x, o[1] - pose.y)
                                 + math.hypot(gx - o[0], gy - o[1]))
                    h = math.hypot(target[0] - pose.x, target[1] - pose.y) + math.hypot(gx - target[0], gy - target[1])
                    self.last_side = 1 if wrap(math.atan2(target[1] - pose.y, target[0] - pose.x) - hg) > 0 else -1
                else:
                    h = math.inf
            if h > self.h_min + H_INC_M or (not free and target is None):
                self.side = self.last_side
                # seed d_followed with the obstacle that blocks the way to B
                seed_pts = blockers or pts
                self.d_followed = min((math.hypot(gx - qx, gy - qy) for qx, qy in seed_pts), default=math.inf)
                self.follow_entries += 1
                self._set(t, "follow")
            else:
                self.h_min = min(self.h_min, h)

        if self.mode == "follow":
            for (qx, qy), (phi, d) in zip(pts, [r for r in rets if r[1] <= R_SENSE]):
                if d < FOLLOW_R:
                    self.d_followed = min(self.d_followed, math.hypot(gx - qx, gy - qy))
            if dist <= R_SENSE and free:
                d_reach = 0.0
            else:
                d_reach = math.inf
                for a, d in zip(scan.angles, scan.distances):
                    if d <= R_SENSE:
                        continue          # only free beams: their end point on the range circle
                    qx, qy = pose.x + R_SENSE * math.cos(pose.yaw + a), pose.y + R_SENSE * math.sin(pose.yaw + a)
                    d_reach = min(d_reach, math.hypot(gx - qx, gy - qy))
            if d_reach < self.d_followed - TB_LEAVE_M:
                self.h_min = math.inf
                self._set(t, "go")
                target = (gx, gy) if free else None
                if target is None:
                    cands = self._tangents(pose, scan)
                    target = min(cands, key=lambda o: math.hypot(o[0] - pose.x, o[1] - pose.y)
                                 + math.hypot(gx - o[0], gy - o[1]), default=(gx, gy))

        if self.mode == "go":
            tx, ty = target if target is not None else (gx, gy)
            dx, dy = tx - pose.x, ty - pose.y
            n = math.hypot(dx, dy) or 1e-9
            v = min(V_GO, K_GOAL * dist)
            vx, vy = v * dx / n, v * dy / n
        else:
            vx, vy = self._wall_follow(rets)
        vx, vy = self._brake(vx, vy, rets)
        return self._out(pose, vx, vy, hg)


def make(variant: str = "bug2", **kw) -> Planner:
    return {"bug2": Bug2, "tangent_bug": TangentBug}[variant]()
