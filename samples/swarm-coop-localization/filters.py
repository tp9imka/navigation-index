"""Estimators: independent dead reckoning, centralized EKF, decentralized naive / covariance
intersection, with optional robust ranging and two integrity monitors.

Per-agent state: [px, py, bx, by] - position and a world-frame odometry bias (m/s), so the
filter can learn a mis-scaled or mis-aligned odometer from GNSS or ranges."""
import math
from collections import deque

D = 4                  # states per agent
GATE_1DOF = 10.83      # chi-square 1 dof, 99.9 %
GATE_2DOF = 13.82      # chi-square 2 dof, 99.9 %
HUBER_K = 1.5          # normalised-innovation knee for Huber reweighting
GATE_LONG = 3.0 ** 2   # gate for ranges longer than predicted (NLOS side)
HUBER_K_LONG = 1.0
LOCKOUT_N = 8          # consecutive rejected ranges before an agent's covariance is inflated
LOCKOUT_SIGMA = 5.0    # m, inflation applied on lockout
Q_POS = 0.15 ** 2      # m^2 per s per axis, white odometry noise
Q_BIAS = 0.005 ** 2    # (m/s)^2 per s, odometry bias drift (heading changes rotate it)
P0 = 2.0 ** 2          # initial position variance (surveyed launch point)
PB0 = 0.25 ** 2        # initial bias variance: ~5 % of 5 m/s
R_GNSS = 3.5 ** 2
R_UWB = 0.15 ** 2
R_BEARING = math.radians(2.5) ** 2
OMEGAS = [k / 10 for k in range(1, 10)]
WINDOW = 5             # integrity: last N tests per source / peer
WINDOW_FAILS = 3       # fails within WINDOW that raise a flag
PEER_QUORUM = 2        # distinct peers that must flag an agent before the team acts
FLAG_MAX_AGE = 3.0     # s, how long a peer's flag stays counted without a fresh broadcast
NLOS_MAX_EXCESS = 10.0  # m, NLOS only lengthens UWB ranges; the peer test tolerates this much
SS_MAX_SIGMA = 10.0    # m, a no-own-GNSS copy looser than this is not used as a reference
RESET_SIGMA = 30.0     # m, covariance inflation applied by a flagged agent
RESET_COOLDOWN = 10.0  # s, a flagged agent ignores further votes while peers re-test it
DECENTRAL_MSG_BYTES = 24   # id, flags, reset counter, peer-flag mask, x (2 x f32), P (3 x f32)
UPLINK_HDR_BYTES = 4
ODO_BYTES = 8
GNSS_BYTES = 8
RANGE_BYTES = 5            # peer id + f32
BEARING_BYTES = 4
EST_BYTES = 20             # x (2 x f32) + P (3 x f32)


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def robust_variance(nu, S, R, robust, nlos_aware=False):
    """Effective measurement variance after gating and Huber reweighting; None = reject.

    nlos_aware: a range longer than predicted is the NLOS signature, so that side gets a
    tighter gate and knee."""
    if not robust:
        return R
    gate, knee = GATE_1DOF, HUBER_K
    if nlos_aware and nu > 0:
        gate, knee = GATE_LONG, HUBER_K_LONG
    e2 = nu * nu / S
    if e2 > gate:
        return None
    e = math.sqrt(e2)
    if e > knee:
        return R + S * (e / knee - 1.0)
    return R


def peer_range_fails(nu, S):
    """NLOS-aware peer consistency test: short ranges are tested at the 1-dof gate, long ranges
    get NLOS_MAX_EXCESS of slack because multipath only ever adds path length."""
    k = math.sqrt(GATE_1DOF * S)
    return nu < -k or nu > NLOS_MAX_EXCESS + k


def rel_terms(pa, po, m, with_bearing):
    """Scalar terms of a range (and bearing, if `pa` is the initiator) between a and o.

    Each term: (z, h, Ha, Ho, R, angular), Ha / Ho = d h / d position."""
    dx, dy = po[0] - pa[0], po[1] - pa[1]
    d = max(math.hypot(dx, dy), 1e-6)
    out = [(m.r, d, (-dx / d, -dy / d), (dx / d, dy / d), R_UWB, False)]
    if with_bearing and m.bearing is not None:
        d2 = d * d
        out.append((m.bearing, math.atan2(dy, dx), (dy / d2, -dx / d2), (-dy / d2, dx / d2), R_BEARING, True))
    return out


def inv2(P):
    a, b, c, d = P[0][0], P[0][1], P[1][0], P[1][1]
    det = a * d - b * c
    return [[d / det, -b / det], [-c / det, a / det]]


def nis2(e, P):
    Pi = inv2(P)
    return e[0] * (Pi[0][0] * e[0] + Pi[0][1] * e[1]) + e[1] * (Pi[1][0] * e[0] + Pi[1][1] * e[1])


def kf_update(x, P, H, nu, R):
    """In-place scalar Kalman update; H is a sparse list of (index, value)."""
    n = len(x)
    PHt = [sum(P[r][c] * v for c, v in H) for r in range(n)]
    S = sum(v * PHt[c] for c, v in H) + R
    for r in range(n):
        x[r] += PHt[r] / S * nu
    for r in range(n):
        kr = PHt[r] / S
        if kr:
            row = P[r]
            for c in range(n):
                row[c] -= kr * PHt[c]
    for r in range(n):
        for c in range(r + 1, n):
            v = 0.5 * (P[r][c] + P[c][r])
            P[r][c] = P[c][r] = v


def innov_var(P, H):
    return sum(vr * P[r][c] * vc for r, vr in H for c, vc in H)


def predict_block(x, P, base, odo):
    """Propagate one agent's [p, b] block: p += odo - b, b random walk."""
    n = len(x)
    x[base] += odo[0] - x[base + 2]
    x[base + 1] += odo[1] - x[base + 3]
    for k in (0, 1):
        Pp, Pb = P[base + k], P[base + 2 + k]
        for c in range(n):
            Pp[c] -= Pb[c]
    for k in (0, 1):
        cp, cb = base + k, base + 2 + k
        for r in range(n):
            P[r][cp] -= P[r][cb]
    P[base][base] += Q_POS
    P[base + 1][base + 1] += Q_POS
    P[base + 2][base + 2] += Q_BIAS
    P[base + 3][base + 3] += Q_BIAS


def init_block(p):
    x = [p[0], p[1], 0.0, 0.0]
    P = [[0.0] * D for _ in range(D)]
    P[0][0] = P[1][1] = P0
    P[2][2] = P[3][3] = PB0
    return x, P


def pos_cov(P, base=0):
    return [[P[base][base], P[base][base + 1]], [P[base + 1][base], P[base + 1][base + 1]]]


def gnss_nis(x, P, base, z):
    e = (z[0] - x[base], z[1] - x[base + 1])
    S = pos_cov(P, base)
    S[0][0] += R_GNSS
    S[1][1] += R_GNSS
    return nis2(e, S)


def gnss_update(x, P, base, z, gate):
    """2-D GNSS position update on block `base`; returns False if gated out."""
    if gate and gnss_nis(x, P, base, z) > GATE_2DOF:
        return False
    for axis in (0, 1):
        kf_update(x, P, [(base + axis, 1.0)], z[axis] - x[base + axis], R_GNSS)
    return True


class DeadReckoning:
    """(a) No cooperation: GNSS agents fuse their own GNSS, the others integrate odometry."""

    def __init__(self, init, cfg, gnss_gate=False):
        self.name = "dead-reckoning"
        self.blocks = [init_block(p) for p in init]
        self.gnss_gate = gnss_gate
        self.bytes = 0
        self.rejected = 0

    def step(self, ep):
        for a, odo in enumerate(ep.odo):
            x, P = self.blocks[a]
            predict_block(x, P, 0, odo)
        for a, z in ep.gnss.items():
            x, P = self.blocks[a]
            if not gnss_update(x, P, 0, z, self.gnss_gate):
                self.rejected += 1

    def est(self, a):
        x, P = self.blocks[a]
        return x[:2], pos_cov(P)


class CentralEKF:
    """Joint 4N-state EKF at a fusion centre."""

    def __init__(self, init, robust, use_bearing, gnss_gate, excluded=None):
        n = len(init)
        self.n = n
        self.x = []
        self.P = [[0.0] * (D * n) for _ in range(D * n)]
        for a, p in enumerate(init):
            xb, Pb = init_block(p)
            self.x += xb
            for r in range(D):
                for c in range(D):
                    self.P[D * a + r][D * a + c] = Pb[r][c]
        self.robust = robust
        self.use_bearing = use_bearing
        self.gnss_gate = gnss_gate
        self.excluded = set() if excluded is None else excluded
        self.rejected = 0
        self.reject_run = [0] * n
        self.lockouts = 0

    def predict(self, odo):
        for a, o in enumerate(odo):
            predict_block(self.x, self.P, D * a, o)

    def gnss_nis(self, a, z):
        return gnss_nis(self.x, self.P, D * a, z)

    def gnss_update(self, a, z):
        if a in self.excluded:
            return
        if not gnss_update(self.x, self.P, D * a, z, self.gnss_gate):
            self.rejected += 1

    def rel_update(self, m):
        bi, bj = D * m.i, D * m.j
        pi = (self.x[bi], self.x[bi + 1])
        pj = (self.x[bj], self.x[bj + 1])
        for z, h, Hi, Hj, R, ang in rel_terms(pi, pj, m, self.use_bearing):
            H = [(bi, Hi[0]), (bi + 1, Hi[1]), (bj, Hj[0]), (bj + 1, Hj[1])]
            nu = wrap(z - h) if ang else z - h
            S = innov_var(self.P, H) + R
            Re = robust_variance(nu, S, R, self.robust, nlos_aware=not ang)
            if Re is None:
                self.rejected += 1
                if not ang:
                    self._lockout(m.i, 1)
                    self._lockout(m.j, 1)
                continue
            if not ang:
                self._lockout(m.i, 0)
                self._lockout(m.j, 0)
            kf_update(self.x, self.P, H, nu, Re)

    def _lockout(self, a, rejected):
        """Gate lock-out recovery: an agent whose ranges keep failing the gate is more likely
        wrong than all its neighbours, so widen its position covariance."""
        self.reject_run[a] = self.reject_run[a] + 1 if rejected else 0
        if self.reject_run[a] >= LOCKOUT_N:
            b = D * a
            self.P[b][b] += LOCKOUT_SIGMA ** 2
            self.P[b + 1][b + 1] += LOCKOUT_SIGMA ** 2
            self.reject_run[a] = 0
            self.lockouts += 1

    def est(self, a):
        b = D * a
        return [self.x[b], self.x[b + 1]], pos_cov(self.P, b)

    def copy_from(self, other):
        self.x = list(other.x)
        self.P = [list(r) for r in other.P]


class Centralized:
    """(b) Fusion centre at `leader`. Uplinks travel multi-hop over the lossy mesh.

    integrity: 'none' | 'gate' (per-fix chi-square) | 'ss' (gate + solution separation: one
    sub-filter per GNSS agent that excludes that agent's GNSS; a fix that disagrees with its
    sub-filter in WINDOW_FAILS of WINDOW epochs is excluded and the main filter is replaced by
    that sub-filter). Monitoring stops once fewer than two GNSS sources remain."""

    def __init__(self, init, cfg, robust=True, integrity="none", leader=None):
        self.name = "central-" + ("robust" if robust else "plain") + ("" if integrity == "none" else "+" + integrity)
        self.cfg = cfg
        self.leader = cfg.gnss_agents[-1] if leader is None else leader
        self.excluded = set()
        gate = integrity in ("gate", "ss")
        self.main = CentralEKF(init, robust, cfg.bearing, gate, self.excluded)
        self.integrity = integrity
        self.subs = {}
        self.win = {}
        if integrity == "ss" and len(cfg.gnss_agents) >= 2:
            for g in cfg.gnss_agents:
                self.subs[g] = CentralEKF(init, robust, cfg.bearing, gate, {g})
                self.win[g] = deque(maxlen=WINDOW)
        self.bytes = 0
        self.detections = []

    @property
    def rejected(self):
        return self.main.rejected

    @property
    def lockouts(self):
        return self.main.lockouts

    def step(self, ep):
        filters = [self.main] + list(self.subs.values())
        for f in filters:
            f.predict(ep.odo)
        for a in range(self.cfg.n_agents):
            if ep.hops[a] is None:
                continue
            nr = sum(1 for m in ep.ranges if m.i == a)
            nb = sum(1 for m in ep.ranges if m.i == a and m.bearing is not None)
            size = UPLINK_HDR_BYTES + ODO_BYTES + (GNSS_BYTES if a in ep.gnss else 0) + nr * RANGE_BYTES + nb * BEARING_BYTES
            self.bytes += size * ep.hops[a]
        self.bytes += ep.downlink_reach * self.cfg.n_agents * EST_BYTES
        for g, z in ep.gnss.items():
            if not ep.uplink_ok[g] or g in self.excluded:
                continue
            if g in self.subs:
                self.win[g].append(self.subs[g].gnss_nis(g, z) > GATE_2DOF)
                if sum(self.win[g]) >= WINDOW_FAILS:
                    self._exclude(g, ep.t)
                    continue
            for f in [self.main] + list(self.subs.values()):
                f.gnss_update(g, z)
        for m in ep.ranges:
            if ep.uplink_ok[m.i]:
                for f in [self.main] + list(self.subs.values()):
                    f.rel_update(m)

    def _exclude(self, g, t):
        self.excluded.add(g)
        self.detections.append((t, g))
        self.main.copy_from(self.subs[g])
        # Other sub-filters fused the faulty source; with one source left there is nothing
        # independent to compare it against, so monitoring ends.
        self.subs = {}

    def est(self, a):
        return self.main.est(a)


class Decentralized:
    """(c) Each agent keeps only its own 4-state estimate and broadcasts its position and
    position covariance once per epoch.

    mode 'ci': covariance intersection on the joint [x_a; p_o] - consistent for any unknown
    cross-correlation. mode 'naive': treats the neighbour estimate as independent.
    integrity: 'none' | 'gate' | 'vote' (gate + peer range-consistency votes, quorum of
    PEER_QUORUM) | 'ss' (gate + distributed solution separation: every agent also runs one copy
    of its filter per GNSS agent g that excludes everything derived from g's GNSS, and
    broadcasts those copies too; agent g tests its fix against its own copy)."""

    def __init__(self, init, cfg, mode="ci", robust=True, integrity="none"):
        self.name = mode + "-" + ("robust" if robust else "plain") + ("" if integrity == "none" else "+" + integrity)
        self.cfg = cfg
        self.mode = mode
        self.robust = robust
        self.integrity = integrity
        n = cfg.n_agents
        self.blocks = [init_block(p) for p in init]
        # ss: copies[g][a] = agent a's estimate built without anything derived from g's GNSS
        self.copies = {}
        if integrity == "ss" and len(cfg.gnss_agents) >= 2:
            self.copies = {g: [init_block(p) for p in init] for g in cfg.gnss_agents}
        self.ss_win = {g: deque(maxlen=WINDOW) for g in self.copies}
        self.informed = None
        self.faulty = None
        self.ss_avail = 0
        self.gnss_excluded = [False] * n
        self.reset_count = [0] * n
        self.last_reset = [-1e9] * n
        self.seen_reset = [[0] * n for _ in range(n)]
        self.win = [[deque(maxlen=WINDOW) for _ in range(n)] for _ in range(n)]
        self.flags = [set() for _ in range(n)]           # peers this agent currently flags
        self.peer_flags = [dict() for _ in range(n)]     # a's view: peer => (time, set it flags)
        self.bytes = 0
        self.detections = []
        self.rejected = 0
        self.reject_run = [0] * n
        self.lockouts = 0

    def step(self, ep):
        cfg = self.cfg
        n = cfg.n_agents
        gate = self.integrity in ("gate", "vote", "ss")
        for a, odo in enumerate(ep.odo):
            predict_block(*self.blocks[a], 0, odo)
            for cp in self.copies.values():
                predict_block(*cp[a], 0, odo)
        self._spread_exclusion(ep)
        for a, z in ep.gnss.items():
            if self.gnss_excluded[a]:
                continue
            if a in self.copies and self.faulty is None and self._copy_sigma(a) <= SS_MAX_SIGMA:
                self.ss_avail += 1
                self.ss_win[a].append(gnss_nis(*self.copies[a][a], 0, z) > GATE_2DOF)
                if sum(self.ss_win[a]) >= WINDOW_FAILS:
                    active = [g for g in cfg.gnss_agents if not self.gnss_excluded[g]]
                    if len(active) <= 2:
                        # two sources disagree: detectable, not identifiable - drop both
                        for g in active:
                            self.gnss_excluded[g] = True
                        self.faulty = "both"
                    else:
                        self.gnss_excluded[a] = True
                        self.faulty = a
                    self.informed = set()
                    self.detections.append((ep.t, a))
                    self._switch(a)
                    continue
            if not gnss_update(*self.blocks[a], 0, z, gate):
                self.rejected += 1
            for g, cp in self.copies.items():
                if g != a:
                    gnss_update(*cp[a], 0, z, gate)
        snap = [((self.blocks[o][0][0], self.blocks[o][0][1]), pos_cov(self.blocks[o][1]), self.reset_count[o],
                 set(self.flags[o])) for o in range(n)]
        csnap = {g: [((cp[o][0][0], cp[o][0][1]), pos_cov(cp[o][1])) for o in range(n)] for g, cp in self.copies.items()}
        self.bytes += n * (DECENTRAL_MSG_BYTES + len(self.copies) * EST_BYTES)
        if self.integrity == "vote":
            self._vote_bookkeeping(ep, snap)
        for m in ep.ranges:
            for a, o in ((m.i, m.j), (m.j, m.i)):
                if not ep.heard[a][o] or self._distrusted(a, o, ep.t):
                    continue
                with_b = a == m.i and cfg.bearing
                for g, cp in self.copies.items():
                    upd = self._ci(cp[a], csnap[g][o], m, with_b)
                    if upd:
                        cp[a] = upd
                self._rel_update(a, snap[o], o, m, with_b)

    def _copy_sigma(self, g):
        P = self.copies[g][g][1]
        return math.sqrt(max(P[0][0], P[1][1]))

    def _switch(self, a):
        """Agent a adopts its estimate that never used the faulty GNSS or, when the fault
        cannot be attributed, widens its position covariance and coasts."""
        if self.faulty == "both":
            P = self.blocks[a][1]
            P[0][0] += RESET_SIGMA ** 2
            P[1][1] += RESET_SIGMA ** 2
        else:
            x, P = self.copies[self.faulty][a]
            self.blocks[a] = (list(x), [list(r) for r in P])
        self.reset_count[a] += 1
        self.informed.add(a)

    def _spread_exclusion(self, ep):
        """The exclusion flag floods one hop per epoch over received broadcasts; once every
        agent has switched, the copies are dropped (one GNSS left: nothing to compare)."""
        if self.faulty is None or not self.copies:
            return
        newly = [a for a in range(self.cfg.n_agents)
                 if a not in self.informed and any(ep.heard[a][o] for o in self.informed)]
        for a in newly:
            self._switch(a)
        if len(self.informed) == self.cfg.n_agents:
            self.copies = {}

    def _vote_bookkeeping(self, ep, snap):
        n = self.cfg.n_agents
        for a in range(n):
            for o in range(n):
                if ep.heard[a][o]:
                    self.peer_flags[a][o] = (ep.t, snap[o][3])
                    if snap[o][2] != self.seen_reset[a][o]:
                        self.seen_reset[a][o] = snap[o][2]
                        self.win[a][o].clear()
                        self.flags[a].discard(o)
        for o in range(n):
            if ep.t - self.last_reset[o] <= RESET_COOLDOWN:
                continue
            voters = {p for p, (t, fl) in self.peer_flags[o].items() if ep.t - t <= FLAG_MAX_AGE and o in fl}
            if len(voters) >= PEER_QUORUM:
                if o in self.cfg.gnss_agents:
                    self.gnss_excluded[o] = True
                P = self.blocks[o][1]
                P[0][0] += RESET_SIGMA ** 2
                P[1][1] += RESET_SIGMA ** 2
                self.reset_count[o] += 1
                self.last_reset[o] = ep.t
                self.detections.append((ep.t, o))
                self.peer_flags[o].clear()

    def _distrusted(self, a, o, t):
        if self.integrity != "vote":
            return False
        if o in self.flags[a]:
            return True
        voters = {p for p, (tf, fl) in self.peer_flags[a].items() if t - tf <= FLAG_MAX_AGE and o in fl}
        return len(voters) >= PEER_QUORUM

    def _accepted_terms(self, block, snap_o, m, with_bearing, a=None, o=None):
        """Robust-weighted scalar terms; a / o given => main filter (lockout and vote bookkeeping)."""
        po, Po = snap_o[0], snap_o[1]
        xa, Pa = block
        accepted = []
        for z, h, Ha, Ho, R, ang in rel_terms(xa, po, m, with_bearing):
            nu = wrap(z - h) if ang else z - h
            S = (Ha[0] * (Pa[0][0] * Ha[0] + Pa[0][1] * Ha[1]) + Ha[1] * (Pa[1][0] * Ha[0] + Pa[1][1] * Ha[1])
                 + Ho[0] * (Po[0][0] * Ho[0] + Po[0][1] * Ho[1]) + Ho[1] * (Po[1][0] * Ho[0] + Po[1][1] * Ho[1]) + R)
            if a is not None and self.integrity == "vote" and not ang:
                self.win[a][o].append(peer_range_fails(nu, S))
                if sum(self.win[a][o]) >= WINDOW_FAILS:
                    self.flags[a].add(o)
                    return None
            Re = robust_variance(nu, S, R, self.robust, nlos_aware=not ang)
            if Re is None:
                if a is not None:
                    self.rejected += 1
                    if not ang:
                        self.reject_run[a] += 1
                        if self.reject_run[a] >= LOCKOUT_N:
                            Pa[0][0] += LOCKOUT_SIGMA ** 2
                            Pa[1][1] += LOCKOUT_SIGMA ** 2
                            self.reject_run[a] = 0
                            self.lockouts += 1
                continue
            if a is not None and not ang:
                self.reject_run[a] = 0
            accepted.append((nu, Ha, Ho, Re))
        return accepted

    def _fuse(self, block, Po, accepted):
        xa, Pa = block
        if self.mode == "naive":
            return joint_update(xa, Pa, Po, 1.0, 1.0, accepted)
        # omega minimises the prior-normalised trace over all four states, so a gain in
        # position cannot be bought by silently inflating the local-only bias states
        best = None
        for w in OMEGAS:
            cand = joint_update(xa, Pa, Po, w, 1.0 - w, accepted)
            score = sum(cand[1][k][k] / Pa[k][k] for k in range(D))
            if best is None or score < best[0]:
                best = (score, cand)
        if best[0] >= D:
            return None
        return best[1]

    def _ci(self, block, snap_o, m, with_bearing):
        acc = self._accepted_terms(block, snap_o, m, with_bearing)
        return self._fuse(block, snap_o[1], acc) if acc else None

    def _rel_update(self, a, snap_o, o, m, with_bearing):
        acc = self._accepted_terms(self.blocks[a], snap_o, m, with_bearing, a, o)
        if acc:
            upd = self._fuse(self.blocks[a], snap_o[1], acc)
            if upd:
                self.blocks[a] = upd

    def est(self, a):
        x, P = self.blocks[a]
        return x[:2], pos_cov(P)


def joint_update(xa, Pa, Po, wa, wo, accepted):
    """Update [x_a (4); p_o (2)] with P = blkdiag(Pa / wa, Po / wo); return a's posterior.

    Innovations were computed at the prior, so the joint state is carried as an error state."""
    n = D + 2
    x = [0.0] * n
    P = [[0.0] * n for _ in range(n)]
    for r in range(D):
        for c in range(D):
            P[r][c] = Pa[r][c] / wa
    for r in range(2):
        for c in range(2):
            P[D + r][D + c] = Po[r][c] / wo
    for nu, Ha, Ho, R in accepted:
        H = [(0, Ha[0]), (1, Ha[1]), (D, Ho[0]), (D + 1, Ho[1])]
        pred = sum(v * x[c] for c, v in H)
        kf_update(x, P, H, nu - pred, R)
    return [xa[k] + x[k] for k in range(D)], [P[r][:D] for r in range(D)]
