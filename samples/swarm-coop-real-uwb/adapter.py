"""Adapter: MILUV ranges + mocap => the Epoch stream that samples/swarm-coop-localization's filters consume.

Mapping (the sim's 'GNSS agents' become 'anchored drones'):
- agents = the 3 drones, 2-D state in the mocap x-y plane;
- an anchored drone gets one absolute 2-D fix per epoch: plain Gauss-Newton multilateration of
  its own real tag-to-anchor ranges, projected to the horizontal with its real height sensor;
- the denied drone never uses anchor ranges; it only has odometry and real inter-drone ranges;
- inter-drone ranges: every real tag-to-tag two-way range in the epoch, projected to the
  horizontal with both drones' height sensors. Tag lever arms (~0.22 m) are not modelled,
  as in the sim's point-agent measurement model;
- odometry: SYNTHETIC. MILUV has no wheel or VIO odometry in the experiment zips, so the
  mocap displacement is corrupted with the sim's odometer model (per-drone scale and
  heading error + white noise);
- comms: ideal (every broadcast heard, every uplink delivered, one hop).
"""
import math
import os
import random
import statistics
import sys

import miluv_io as io

SIM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "swarm-coop-localization")
if SIM_DIR not in sys.path:
    sys.path.insert(0, SIM_DIR)

import filters  # noqa: E402  (from samples/swarm-coop-localization, unmodified)
from sim import Config, Epoch, RangeMeas  # noqa: E402

DT = 0.5                 # s per epoch
ODO_SIGMA_V = 0.05       # m/s white odometry noise per axis
ODO_SCALE_SIGMA = 0.02   # same as sim.Config
ODO_HEADING_SIGMA_DEG = 1.5
MIN_ANCHORS = 3          # distinct anchors needed for a 2-D fix
FIX_ITERS = 10
FAULT_ANCHORS = (0, 1, 2)  # the +x wall; a range bias on these pulls the fix towards -x

# The sim's filter constants are for a 100 m-scale outdoor team at 1 epoch/s. Indoors at 0.5 s
# epochs, the length and per-epoch constants are rescaled; gates, Huber knees, window counts
# and R_UWB (the sim's own UWB noise assumption) stay as they are.
INDOOR = {
    "R_GNSS": 0.25 ** 2,            # fix noise: R_UWB 0.15 m x a typical HDOP of ~1.6, set before looking at fix errors
    "P0": 0.3 ** 2,
    "PB0": (0.05 * DT) ** 2,        # bias state is m per epoch: 5 % of 1 m/s
    "Q_POS": (1.5 * ODO_SIGMA_V * DT) ** 2,  # sim: Q = (1.5 x true white noise)^2
    "Q_BIAS": (0.05 * DT) ** 2 / 60,  # turns rotate the world-frame bias: allow a full PB0 change in ~60 epochs
    "LOCKOUT_SIGMA": 0.5,
    "NLOS_MAX_EXCESS": 1.0,
    "RESET_SIGMA": 3.0,
    "SS_MAX_SIGMA": 1.0,
}
_SIM_DEFAULTS = {k: getattr(filters, k) for k in INDOOR}


def apply_indoor(on=True):
    for k, v in (INDOOR if on else _SIM_DEFAULTS).items():
        setattr(filters, k, v)


def horizontal(r, dz):
    s = r * r - dz * dz
    return math.sqrt(s) if s > 0 else None


def multilaterate(obs, guess):
    """obs: [(anchor_xy, horizontal_range)]; plain Gauss-Newton, no robust weighting."""
    x, y = guess
    for _ in range(FIX_ITERS):
        a11 = a12 = a22 = b1 = b2 = 0.0
        for (ax, ay), r in obs:
            dx, dy = x - ax, y - ay
            d = max(math.hypot(dx, dy), 1e-6)
            hx, hy, e = dx / d, dy / d, r - d
            a11 += hx * hx
            a12 += hx * hy
            a22 += hy * hy
            b1 += hx * e
            b2 += hy * e
        det = a11 * a22 - a12 * a12
        if abs(det) < 1e-9:
            return None
        sx, sy = (a22 * b1 - a12 * b2) / det, (a11 * b2 - a12 * b1) / det
        x, y = x + sx, y + sy
        if math.hypot(sx, sy) < 1e-4:
            break
    return x, y


class Fault:
    """start: s after the first epoch. kind 'anchor': ramp bias on one anchored drone's ranges to FAULT_ANCHORS (a spoofed or
    tampered anchor subset => its absolute fix walks off). kind 'peer': ramp bias on every
    inter-drone range touching `drone` (a misbehaving UWB peer)."""

    def __init__(self, kind, drone, start, rate):
        self.kind, self.drone, self.start, self.rate = kind, drone, start, rate

    def bias(self, t):
        return max(0.0, t - self.start) * self.rate


def synthetic_range(rng, d, state, key, scfg):
    """The sim's UWB error model (sim.generate) applied to a true distance."""
    if state.get(key, False):
        if rng.random() < scfg.nlos_exit:
            state[key] = False
    elif rng.random() < scfg.nlos_enter:
        state[key] = True
        state[("b",) + key] = rng.uniform(*scfg.nlos_bias)
    r = d + rng.gauss(0, scfg.uwb_sigma)
    if state.get(key, False):
        r += state[("b",) + key] + abs(rng.gauss(0, 0.5))
    if rng.random() < scfg.outlier_prob:
        r += rng.uniform(*scfg.outlier_range)
    return r


def build(exp, denied, seed=1, fault=None, range_source="real", pair_mode="median", data_dir=io.DATA_DIR,
          t_max=None):
    """Return (cfg, init, epochs, info). denied: index 0..2 of the drone without anchor fixes.

    pair_mode 'median': one range per drone pair per epoch (median of that epoch's tag-to-tag
    ranges), the sim's one-slot-per-pair structure. 'all': every tag-to-tag range."""
    robots = io.ROBOTS
    n = len(robots)
    anchored = tuple(a for a in range(n) if a != denied)
    cfg = Config(n_agents=n, gnss_agents=anchored, duration=0, bearing=False, seed=seed)
    tracks = {r: io.load_track(exp, r, data_dir) for r in robots}
    heights = {r: io.load_height(exp, r, data_dir) for r in robots}
    anchors = io.anchors_for(exp)
    ranges = io.load_ranges(exp, data_dir)
    t0 = max(tr.span()[0] for tr in tracks.values()) + DT
    t1 = min(tr.span()[1] for tr in tracks.values())
    if t_max is not None:
        t1 = min(t1, t0 + t_max)
    rng = random.Random(seed)
    scale = [1.0 + rng.gauss(0, ODO_SCALE_SIGMA) for _ in range(n)]
    head = [math.radians(rng.gauss(0, ODO_HEADING_SIGMA_DEG)) for _ in range(n)]
    rrng = random.Random(seed + 1000)
    scfg = Config()
    nlos_state = {}

    def truth(t):
        return [tracks[r].at(t) for r in robots]

    init = [(p[0], p[1]) for p in truth(t0)]
    prev = init
    last_fix = {a: init[a] for a in anchored}
    ranges = [m for m in ranges if t0 < m.t <= t1]
    k = 0
    epochs = []
    info = {"fixes": 0, "fix_err": [], "inter": 0, "inter_err": [], "no_truth": 0, "skipped_proj": 0, "t0": t0}
    t = t0
    while t + DT <= t1 + 1e-9:
        t_next = t + DT
        tru = truth(t_next)
        if any(p is None for p in tru):
            info["no_truth"] += 1
            tru = [p if p is not None else (prev[a][0], prev[a][1], 0.0) for a, p in enumerate(tru)]
        pos = [(p[0], p[1]) for p in tru]
        odo = []
        for a in range(n):
            dx, dy = pos[a][0] - prev[a][0], pos[a][1] - prev[a][1]
            c, s = math.cos(head[a]), math.sin(head[a])
            odo.append((scale[a] * (c * dx - s * dy) + rng.gauss(0, ODO_SIGMA_V * DT),
                        scale[a] * (s * dx + c * dy) + rng.gauss(0, ODO_SIGMA_V * DT)))
        batch = []
        while k < len(ranges) and ranges[k].t <= t_next:
            batch.append(ranges[k])
            k += 1
        anchor_obs = {a: {} for a in anchored}
        rel = []
        for m in batch:
            ha = io.TAG_ROBOT.get(m.frm)
            hb = io.TAG_ROBOT.get(m.to)
            a = robots.index(ha) if ha else None
            b = robots.index(hb) if hb else None
            if a is None and b is None:
                continue
            if io.is_anchor(m.to) or io.is_anchor(m.frm):
                tag_robot, anc = (a, m.to) if io.is_anchor(m.to) else (b, m.frm)
                if tag_robot not in anchored:
                    continue
                h = io.zoh(*heights[robots[tag_robot]], m.t)
                if h is None:
                    continue
                r = m.r
                if fault and fault.kind == "anchor" and fault.drone == tag_robot and anc in FAULT_ANCHORS:
                    r += fault.bias(m.t - t0)
                ax, ay, az = anchors[anc]
                rh = horizontal(r, az - h)
                if rh is None:
                    info["skipped_proj"] += 1
                    continue
                anchor_obs[tag_robot].setdefault(anc, []).append(((ax, ay), rh))
                continue
            if a == b:
                continue
            ha_, hb_ = io.zoh(*heights[robots[a]], m.t), io.zoh(*heights[robots[b]], m.t)
            if ha_ is None or hb_ is None:
                continue
            if range_source == "real":
                r = m.r
            else:
                r = synthetic_range(rrng, m.gt, nlos_state, (min(a, b), max(a, b)), scfg)
            if fault and fault.kind == "peer" and fault.drone in (a, b):
                r += fault.bias(m.t - t0)
            rh = horizontal(r, ha_ - hb_)
            if rh is None:
                info["skipped_proj"] += 1
                continue
            rel.append(RangeMeas(a, b, rh))
        if pair_mode == "median":
            by_pair = {}
            for m in rel:
                by_pair.setdefault((min(m.i, m.j), max(m.i, m.j)), []).append(m.r)
            rel = [RangeMeas(i, j, statistics.median(v)) for (i, j), v in sorted(by_pair.items())]
        for m in rel:
            info["inter"] += 1
            info["inter_err"].append(m.r - math.dist(pos[m.i], pos[m.j]))
        gnss = {}
        for a in anchored:
            obs = [o for lst in anchor_obs[a].values() for o in lst]
            if len(anchor_obs[a]) < MIN_ANCHORS:
                continue
            fix = multilaterate(obs, last_fix[a])
            if fix is None:
                continue
            last_fix[a] = fix
            gnss[a] = fix
            info["fixes"] += 1
            info["fix_err"].append(math.dist(fix, pos[a]))
        heard = [[a != o for o in range(n)] for a in range(n)]
        leader = anchored[-1]
        hops = [0 if a == leader else 1 for a in range(n)]
        epochs.append(Epoch(t_next - t0, pos, odo, gnss, rel, heard, [True] * n, hops, n))
        prev = pos
        t = t_next
    return cfg, init, epochs, info
