"""Truth trajectories and sensor / comm draws for the cooperative localization sample.

All randomness lives here, so every estimator sees the identical measurement stream.
"""
import math
import random
from dataclasses import dataclass, field


@dataclass
class Config:
    n_agents: int = 6
    gnss_agents: tuple = (0, 1)
    duration: int = 600            # s, one epoch per second
    speed: float = 5.0             # m/s formation centre
    ring_radius: float = 100.0     # m, formation slot radius
    wander: float = 40.0           # m, per-agent slot wander amplitude
    odo_noise: float = 0.10        # m/s white, per axis
    odo_scale_sigma: float = 0.02  # per-agent constant scale factor error
    odo_heading_sigma_deg: float = 1.5
    gnss_sigma: float = 3.0
    uwb_sigma: float = 0.10
    uwb_range: float = 200.0
    uwb_dropout: float = 0.15
    nlos_enter: float = 0.02       # per pair per s
    nlos_exit: float = 0.10
    nlos_bias: tuple = (1.0, 8.0)  # m, positive (longer path)
    outlier_prob: float = 0.03
    outlier_range: tuple = (5.0, 30.0)
    bearing: bool = False
    cam_range: float = 120.0
    cam_prob: float = 0.5
    bearing_sigma_deg: float = 2.0
    comm_range: float = 250.0
    packet_loss: float = 0.10
    max_links: int = 3             # ranging slots per agent per epoch (TDMA budget)
    spoof_agent: int = -1          # -1: no spoofing
    spoof_start: float = 300.0
    spoof_rate: float = 0.5        # m/s walk-off
    spoof_dir_deg: float = 45.0
    seed: int = 1


@dataclass
class RangeMeas:
    i: int                 # initiator
    j: int
    r: float
    bearing: float = None  # world-frame bearing i => j, measured by i
    nlos: bool = False
    outlier: bool = False


@dataclass
class Epoch:
    t: float
    truth: list
    odo: list              # measured displacement over (t-1, t]
    gnss: dict             # agent => (x, y)
    ranges: list
    heard: list            # heard[a][o]: a received o's broadcast this epoch
    uplink_ok: list        # centralized: agent's packet reached the leader
    hops: list             # hops to the leader, 0 for the leader, None if unreachable
    downlink_reach: int = 0
    spoof_offset: tuple = (0.0, 0.0)
    counts: dict = field(default_factory=dict)


def truth_track(cfg, rng):
    n = cfg.n_agents
    periods = [(rng.uniform(150, 300), rng.uniform(150, 300), rng.uniform(0, 2 * math.pi),
                rng.uniform(0, 2 * math.pi)) for _ in range(n)]
    track = []
    for k in range(cfg.duration + 1):
        t = float(k)
        cx = cfg.speed * t
        cy = 150.0 * math.sin(2 * math.pi * t / 400.0)
        row = []
        for a in range(n):
            th = 2 * math.pi * a / n
            p, q, ph, ps = periods[a]
            row.append((cx + cfg.ring_radius * math.cos(th) + cfg.wander * math.sin(2 * math.pi * t / p + ph),
                        cy + cfg.ring_radius * math.sin(th) + cfg.wander * math.cos(2 * math.pi * t / q + ps)))
        track.append(row)
    return track


def _hops_to(leader, pos, comm_range):
    n = len(pos)
    hops = [None] * n
    hops[leader] = 0
    frontier = [leader]
    while frontier:
        nxt = []
        for u in frontier:
            for v in range(n):
                if hops[v] is None and math.dist(pos[u], pos[v]) <= comm_range:
                    hops[v] = hops[u] + 1
                    nxt.append(v)
        frontier = nxt
    return hops


def generate(cfg, leader=None):
    rng = random.Random(cfg.seed)
    n = cfg.n_agents
    if leader is None:
        leader = cfg.gnss_agents[-1]
    track = truth_track(cfg, rng)
    scale = [1.0 + rng.gauss(0, cfg.odo_scale_sigma) for _ in range(n)]
    head = [math.radians(rng.gauss(0, cfg.odo_heading_sigma_deg)) for _ in range(n)]
    nlos = {}
    nlos_bias = {}
    sdir = math.radians(cfg.spoof_dir_deg)
    bsig = math.radians(cfg.bearing_sigma_deg)
    epochs = []
    for k in range(1, cfg.duration + 1):
        t = float(k)
        pos = track[k]
        odo = []
        for a in range(n):
            dx = pos[a][0] - track[k - 1][a][0]
            dy = pos[a][1] - track[k - 1][a][1]
            c, s = math.cos(head[a]), math.sin(head[a])
            odo.append((scale[a] * (c * dx - s * dy) + rng.gauss(0, cfg.odo_noise),
                        scale[a] * (s * dx + c * dy) + rng.gauss(0, cfg.odo_noise)))
        off = (0.0, 0.0)
        if cfg.spoof_agent >= 0 and t >= cfg.spoof_start:
            w = cfg.spoof_rate * (t - cfg.spoof_start)
            off = (w * math.cos(sdir), w * math.sin(sdir))
        gnss = {}
        for a in cfg.gnss_agents:
            g = (pos[a][0] + rng.gauss(0, cfg.gnss_sigma), pos[a][1] + rng.gauss(0, cfg.gnss_sigma))
            if a == cfg.spoof_agent:
                g = (g[0] + off[0], g[1] + off[1])
            gnss[a] = g
        for a in range(n):
            for b in range(a + 1, n):
                key = (a, b)
                if nlos.get(key, False):
                    if rng.random() < cfg.nlos_exit:
                        nlos[key] = False
                elif rng.random() < cfg.nlos_enter:
                    nlos[key] = True
                    nlos_bias[key] = rng.uniform(*cfg.nlos_bias)
        ranges = []
        done = set()
        counts = {"attempts": 0, "dropouts": 0, "nlos": 0, "outliers": 0}
        for i in range(n):
            cand = [j for j in range(n) if j != i and math.dist(pos[i], pos[j]) <= cfg.uwb_range]
            rng.shuffle(cand)
            used = 0
            for j in cand:
                if used >= cfg.max_links:
                    break
                key = (min(i, j), max(i, j))
                if key in done:
                    continue
                done.add(key)
                used += 1
                counts["attempts"] += 1
                if rng.random() < cfg.uwb_dropout:
                    counts["dropouts"] += 1
                    continue
                d = math.dist(pos[i], pos[j])
                r = d + rng.gauss(0, cfg.uwb_sigma)
                is_nlos = nlos.get(key, False)
                if is_nlos:
                    r += nlos_bias[key] + abs(rng.gauss(0, 0.5))
                    counts["nlos"] += 1
                is_out = rng.random() < cfg.outlier_prob
                if is_out:
                    r += rng.uniform(*cfg.outlier_range)
                    counts["outliers"] += 1
                b = None
                if cfg.bearing and d <= cfg.cam_range and rng.random() < cfg.cam_prob:
                    b = math.atan2(pos[j][1] - pos[i][1], pos[j][0] - pos[i][0]) + rng.gauss(0, bsig)
                ranges.append(RangeMeas(i, j, r, b, is_nlos, is_out))
        heard = [[a != o and math.dist(pos[a], pos[o]) <= cfg.comm_range and rng.random() >= cfg.packet_loss
                  for o in range(n)] for a in range(n)]
        hops = _hops_to(leader, pos, cfg.comm_range)
        uplink_ok = []
        for a in range(n):
            if hops[a] is None:
                uplink_ok.append(False)
            else:
                uplink_ok.append(all(rng.random() >= cfg.packet_loss for _ in range(hops[a])))
        reach = sum(1 for h in hops if h is not None)
        epochs.append(Epoch(t, pos, odo, gnss, ranges, heard, uplink_ok, hops, reach, off, counts))
    return track[0], epochs
