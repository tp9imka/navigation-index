"""Network of GNSS-disciplined clocks linked by two-way packet time transfer (PTP-like):
regional jamming, a time-push spoof on one node, and all GNSS lost.

Stdlib only. Oscillator grades and the loop design come from ../timing-holdover.
Run `python3 timing_network.py --help`.
"""
import argparse
import json
import math
import os
import random
import statistics
import sys
from collections import deque
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "timing-holdover"))
import timing_holdover as th  # noqa: E402

NS = 1e-9
US = 1e-6
HOUR = 3600.0

U_AVG_WINDOW_S = th.U_AVG_WINDOW_S
STEER_LOOKBACK_S = th.STEER_LOOKBACK_S
MONITOR_PERIOD_S = 10        # consistency check cadence
CONS_K = 6.0                 # threshold, multiples of each node's training RMS residual
CONS_CONSEC = 3
LS_SWEEPS = 60
TRK_ACQ_S = 300              # after (re)anchoring the tracker averages phase only, this long
BUDGETS = (1 * US, 1.5 * US, 5 * US, 10 * US)
CHECKPOINTS = (HOUR, 4 * HOUR, 12 * HOUR, 24 * HOUR)


@dataclass(frozen=True)
class Node:
    name: str
    grade: str


@dataclass(frozen=True)
class Link:
    a: str
    b: str
    kind: str
    asym: float     # one-way delay a->b minus b->a, s (static, unknown to PTP)
    q_ab: float     # mean queueing delay a->b, s (exponential packet delay variation)
    q_ba: float
    ts: float       # timestamp noise per packet, 1 sigma, s


# Synthetic site layout. Grades are the timing-holdover sample's (Vig table 1, Microchip SA65).
NODES = (
    Node("base-station", "OCXO"),
    Node("radar", "Rb"),
    Node("comms-relay", "TCXO"),
    Node("c2-post", "OCXO"),
    Node("sensor-north", "CSAC"),
    Node("sensor-south", "TCXO"),
)
# Synthetic links: fiber with hardware timestamps, microwave backhaul, tactical radio.
LINKS = (
    Link("base-station", "radar", "fiber", 40 * NS, 0.2 * US, 0.3 * US, 8 * NS),
    Link("base-station", "c2-post", "fiber", -60 * NS, 0.2 * US, 0.4 * US, 8 * NS),
    Link("radar", "c2-post", "fiber", 30 * NS, 0.2 * US, 0.2 * US, 8 * NS),
    Link("base-station", "comms-relay", "microwave", 250 * NS, 1.0 * US, 2.0 * US, 30 * NS),
    Link("c2-post", "comms-relay", "microwave", -150 * NS, 1.0 * US, 1.5 * US, 30 * NS),
    Link("comms-relay", "sensor-north", "radio", 400 * NS, 2.0 * US, 5.0 * US, 50 * NS),
    Link("comms-relay", "sensor-south", "radio", -300 * NS, 2.0 * US, 4.0 * US, 50 * NS),
    Link("sensor-north", "sensor-south", "radio", 200 * NS, 3.0 * US, 3.0 * US, 50 * NS),
)
JAMMED_REGION = ("comms-relay", "sensor-north", "sensor-south")


@dataclass
class Config:
    dt: float = 5.0
    sigma_pps: float = 20 * NS      # GNSS 1PPS noise per second (assumption, as timing-holdover)
    temp_fraction: float = 0.1      # fraction of each grade's temperature spec swung daily
    pkt_rate: float = 16.0          # sync packets per second per direction (G.8275.1 default rate)
    pkt_filter: str = "min"         # "min" (lucky packet) or "mean" per step
    calibrate: bool = True          # learn each link's offset bias while all nodes have GNSS
    asym_scale: float = 1.0         # multiplies every link's static asymmetry
    pdv_scale: float = 1.0          # multiplies every queueing delay mean
    cons_margin: float = 50 * NS    # extra allowance on the consistency threshold (assumption)
    ensemble_tau: float = 24 * HOUR  # tau at which ADEV weights are evaluated


@dataclass
class Scenario:
    end_s: float
    loss: dict = field(default_factory=dict)  # node => (start, end) of GNSS loss
    mode: str = "peers"            # what a node without GNSS does: alone | peers | best | ensemble
    ref_t: float = 0.0             # metrics measured from here
    calib: tuple = None            # (t0, t1) window for link bias calibration
    spoof_node: str = None
    spoof_at: float = None
    spoof_rate: float = 0.0
    monitor_from: float = None     # consistency check: training starts here
    train_s: float = HOUR
    guard: bool = True             # isolate the flagged node
    asym_change: dict = field(default_factory=dict)  # link index => (t, extra asymmetry s)
    checkpoints: tuple = CHECKPOINTS
    trace_every: float = None      # record every node's TE at this period (s) after ref_t
    # link index => (1 Hz series of offset error, s; start index). Replaces that link's synthetic
    # asymmetry, queueing and timestamp noise; looped. m = x_a - x_b + series, so a node b taking
    # time from a over this link sees TE = +series (real_link.py feeds PPS truth this way).
    link_replay: dict = field(default_factory=dict)


@dataclass
class Result:
    te_at: dict = field(default_factory=dict)      # node => {checkpoint: TE s}
    exceed_at: dict = field(default_factory=dict)  # node => {budget: s after ref_t or None}
    max_te: dict = field(default_factory=dict)     # node => max |TE| after ref_t
    alarms: list = field(default_factory=list)     # (s after spoof_at or monitor end, node)
    weights: dict = field(default_factory=dict)
    trace: list = field(default_factory=list)      # (s after ref_t, [TE per node])
    thresholds: dict = field(default_factory=dict)  # consistency-check alarm threshold per node, s


def adev_model(grade, tau, temp_fraction):
    """sigma_y(tau) from the datasheet terms: white FM, linear drift (D*tau/sqrt 2) and a
    temperature term taken as its full swing / sqrt 2 (conservative)."""
    white = grade.adev_1s ** 2 / tau
    drift = (grade.aging_per_s * tau) ** 2 / 2.0
    temp = (temp_fraction * grade.temp_spec) ** 2 / 2.0
    return math.sqrt(white + drift + temp)


def ensemble_weights(cfg):
    inv = {n.name: 1.0 / adev_model(th.GRADE_BY_NAME[n.grade], cfg.ensemble_tau, cfg.temp_fraction) ** 2
           for n in NODES}
    s = sum(inv.values())
    return {k: v / s for k, v in inv.items()}


def best_clock(cfg):
    w = ensemble_weights(cfg)
    return max(w, key=w.get)


def replay_value(series, start, t, dt):
    """Mean of a looped 1 Hz error series over the step [t, t + dt)."""
    n = len(series)
    w = max(1, int(round(dt)))
    i0 = int(t) + start
    return sum(series[(i0 + j) % n] for j in range(w)) / w


def replay_noise(series, dt):
    w = max(1, int(round(dt)))
    means = [sum(series[i:i + w]) / w for i in range(0, len(series) - w + 1, w)]
    return statistics.pstdev(means) if len(means) > 1 else 0.0


def step_noise(link, cfg):
    """1-sigma noise of one filtered offset sample on a link (used to pick tracker gains)."""
    n = max(1, round(cfg.pkt_rate * cfg.dt))
    qa, qb = link.q_ab * cfg.pdv_scale, link.q_ba * cfg.pdv_scale
    if cfg.pkt_filter == "min":
        return math.sqrt(((qa / n) ** 2 + (qb / n) ** 2) / 4.0 + link.ts ** 2 / 2.0)
    return math.sqrt((qa ** 2 + qb ** 2) / (4.0 * n) + link.ts ** 2 / (2.0 * n))


def offset_bias(link, cfg, extra_asym=0.0):
    """Expected error of a filtered two-way offset (x_a - x_b): -asym/2 plus half the
    difference of the residual queueing delays the filter leaves behind."""
    n = max(1, round(cfg.pkt_rate * cfg.dt))
    qa, qb = link.q_ab * cfg.pdv_scale, link.q_ba * cfg.pdv_scale
    resid = (qb - qa) / n if cfg.pkt_filter == "min" else (qb - qa)
    return -(link.asym * cfg.asym_scale + extra_asym) / 2.0 + resid / 2.0


class Graph:
    def __init__(self):
        self.names = [n.name for n in NODES]
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.adj = {i: [] for i in range(len(NODES))}
        for k, l in enumerate(LINKS):
            a, b = self.idx[l.a], self.idx[l.b]
            self.adj[a].append((b, k, 1.0))
            self.adj[b].append((a, k, -1.0))
        self.rank = {i: -ensemble_weights(Config())[n] for i, n in enumerate(self.names)}

    def path(self, src, dst):
        """[(link index, sign)] along a shortest-hop path; sum of sign*meas = x_src - x_dst + bias."""
        prev = {src: None}
        frontier = [src]
        while frontier and dst not in prev:
            nxt = []
            for u in frontier:
                for v, k, s in self.adj[u]:
                    if v not in prev:
                        prev[v] = (u, k, s)
                        nxt.append(v)
            frontier = nxt
        out, v = [], dst
        while prev[v] is not None:
            u, k, s = prev[v]
            out.append((k, s))
            v = u
        return out

    def nearest(self, src, allowed):
        """Nearest node in `allowed` by hops, best grade first on ties (BMCA-like)."""
        seen, frontier = {src}, [src]
        while frontier:
            hits = [v for v in frontier if v in allowed and v != src]
            if hits:
                return min(hits, key=lambda v: self.rank[v])
            nxt = []
            for u in frontier:
                for v, _, _ in self.adj[u]:
                    if v not in seen:
                        seen.add(v)
                        nxt.append(v)
            frontier = nxt
        return None


def solve_offsets(nodes, edges):
    """Weighted least squares node offsets from edge differences d = o_a - o_b, median-anchored."""
    o = {i: 0.0 for i in nodes}
    for _ in range(LS_SWEEPS):
        for i in nodes:
            num = den = 0.0
            for a, b, d, w in edges:
                if a == i:
                    num += w * (o[b] + d)
                    den += w
                elif b == i:
                    num += w * (o[a] - d)
                    den += w
            if den:
                o[i] = num / den
    med = statistics.median(o.values())
    return {i: v - med for i, v in o.items()}


def run(scn, cfg, seed):
    rng = random.Random(seed)
    g = Graph()
    nn = len(NODES)
    grades = [th.GRADE_BY_NAME[n.grade] for n in NODES]
    dt = cfg.dt
    npk = max(1, round(cfg.pkt_rate * dt))
    w_day = 2.0 * math.pi / th.SECONDS_PER_DAY

    y0 = [gr.aging_per_s * th.SECONDS_PER_YEAR * rng.choice((-1.0, 1.0)) for gr in grades]
    tph = [rng.uniform(0.0, 2.0 * math.pi) for _ in grades]
    amp = [cfg.temp_fraction * gr.temp_spec for gr in grades]
    gains = []
    for gr in grades:
        tc = th.loop_time_constant(gr, cfg.sigma_pps, cfg.temp_fraction)
        gains.append([(2.0 * th.LOOP_DAMPING / c, 1.0 / (c * c)) for c in (th.ACQ_TC_S, tc)])
    trk_gains = []
    for i, gr in enumerate(grades):
        sig = max(replay_noise(scn.link_replay[k][0], dt) if k in scn.link_replay else step_noise(LINKS[k], cfg)
                  for _, k, _ in g.adj[i])
        tc = th.loop_time_constant(gr, sig, cfg.temp_fraction)
        trk_gains.append((2.0 * th.LOOP_DAMPING / tc, 1.0 / (tc * tc)))
    # phase-only averaging while acquiring: the held-over oscillator's frequency is already
    # corrected by its frozen steering, and a short noisy window would mis-estimate it
    trk_acq = (1.0 / th.ACQ_TC_S, 0.0)
    weights = ensemble_weights(cfg)
    wvec = [weights[n] for n in g.names]
    best = g.idx[best_clock(cfg)]
    hub = g.idx["c2-post"]
    paths_to_hub = [g.path(i, hub) for i in range(nn)]
    paths_to_best = [g.path(i, best) for i in range(nn)]
    loss = {g.idx[k]: v for k, v in scn.loss.items()}
    spoof_i = g.idx[scn.spoof_node] if scn.spoof_node else None

    x = [0.0] * nn
    f = [0.0] * nn
    u = [0.0] * nn
    hold = [None] * nn             # frozen steering when in holdover
    untrusted = set()               # isolated by the consistency check
    u_hist = [deque(maxlen=max(1, int(U_AVG_WINDOW_S / dt))) for _ in range(nn)]
    anchor_cache = {}
    u_by_period = [{} for _ in range(nn)]
    trk = [None] * nn               # [p, v, anchor, start time]
    bias = [0.0] * len(LINKS)
    cal_acc = [[0.0, 0] for _ in LINKS]
    calibrated = False

    res = Result(weights=weights)
    for n in g.names:
        res.te_at[n] = {}
        res.exceed_at[n] = {b: None for b in BUDGETS}
        res.max_te[n] = 0.0
    cps = sorted(scn.checkpoints)
    cp_i = 0

    mon_acc = [[0.0, 0] for _ in LINKS]
    train_rows = []
    base = var = thr = None
    consec = [0] * nn
    mon_end = scn.monitor_from + scn.train_s if scn.monitor_from is not None else None

    def has_gnss(i, t):
        lo_hi = loss.get(i)
        return not (lo_hi and lo_hi[0] <= t < lo_hi[1])

    t = 0.0
    steps = int(round(scn.end_s / dt)) + 1
    for _ in range(steps):
        locked = [has_gnss(i, t) and i not in untrusted for i in range(nn)]

        # two-way exchange on every link, filtered per step
        meas = []
        for k, l in enumerate(LINKS):
            a, b = g.idx[l.a], g.idx[l.b]
            extra = 0.0
            ch = scn.asym_change.get(k)
            if ch and t >= ch[0]:
                extra = ch[1]
            qa, qb = l.q_ab * cfg.pdv_scale, l.q_ba * cfg.pdv_scale
            if cfg.pkt_filter == "min":
                qf = rng.expovariate(npk / qa) if qa > 0 else 0.0
                qr = rng.expovariate(npk / qb) if qb > 0 else 0.0
                nz = rng.gauss(0.0, l.ts / math.sqrt(2.0))
            else:
                qf = qa + rng.gauss(0.0, qa / math.sqrt(npk))
                qr = qb + rng.gauss(0.0, qb / math.sqrt(npk))
                nz = rng.gauss(0.0, l.ts / math.sqrt(2.0 * npk))
            m = x[a] - x[b] - (l.asym * cfg.asym_scale + extra) / 2.0 + (qr - qf) / 2.0 + nz
            if k in scn.link_replay:
                m = x[a] - x[b] + replay_value(*scn.link_replay[k], t, dt)
            meas.append(m)
            if scn.calib and cfg.calibrate and scn.calib[0] <= t < scn.calib[1] and locked[a] and locked[b]:
                cal_acc[k][0] += m
                cal_acc[k][1] += 1
        if scn.calib and cfg.calibrate and not calibrated and t >= scn.calib[1]:
            bias = [s / c if c else 0.0 for s, c in cal_acc]
            calibrated = True
        cm = [m - b for m, b in zip(meas, bias)]

        def path_meas(p):
            return sum(s * cm[k] for k, s in p)

        # discipline or hold over; output time = oscillator minus tracker correction
        locked_set = frozenset(i for i in range(nn) if locked[i])
        if locked_set not in anchor_cache:
            anchor_cache[locked_set] = {}
            for i in range(nn):
                a_i = g.nearest(i, locked_set)
                anchor_cache[locked_set][i] = (a_i, g.path(i, a_i) if a_i is not None else None)
        anchors = anchor_cache[locked_set]
        hub_off = None
        out = [0.0] * nn
        for i in range(nn):
            if locked[i]:
                hold[i] = None
                trk[i] = None
                spoof = scn.spoof_rate * (t - scn.spoof_at) if (i == spoof_i and t > scn.spoof_at) else 0.0
                z = x[i] - spoof + rng.gauss(0.0, cfg.sigma_pps / math.sqrt(dt))
                kp, ki = gains[i][0] if t < th.ACQ_S else gains[i][1]
                f[i] -= ki * z * dt
                u[i] = f[i] - kp * z
                u_hist[i].append(u[i])
                out[i] = x[i]
                continue
            if hold[i] is None:
                hold[i] = statistics.fmean(u_hist[i]) if u_hist[i] else 0.0
            u[i] = hold[i]
            z = None
            anchor = None
            if scn.mode == "peers" or (scn.mode in ("best", "ensemble") and locked_set):
                anchor, pth = anchors[i]
                if anchor is not None:
                    z = path_meas(pth)
            elif scn.mode == "best":
                anchor = best
                z = path_meas(paths_to_best[i]) if i != best else None
            elif scn.mode == "ensemble":
                anchor = -1
                if hub_off is None:
                    hub_off = [path_meas(paths_to_hub[j]) for j in range(nn)]
                z = hub_off[i] - sum(wj * h for wj, h in zip(wvec, hub_off))
            if z is None:
                out[i] = x[i] - (trk[i][0] if trk[i] else 0.0)
                continue
            if trk[i] is None or trk[i][2] != anchor:
                trk[i] = [z, trk[i][1] if trk[i] else 0.0, anchor, t]
            else:
                kp, ki = trk_acq if t - trk[i][3] < TRK_ACQ_S else trk_gains[i]
                e = trk[i][0] - z
                trk[i][1] -= ki * e * dt
                trk[i][0] += (trk[i][1] - kp * e) * dt
            out[i] = x[i] - trk[i][0]

        # metrics
        if t >= scn.ref_t:
            el = t - scn.ref_t
            for i, n in enumerate(g.names):
                a = abs(out[i])
                if a > res.max_te[n]:
                    res.max_te[n] = a
                ex = res.exceed_at[n]
                for b in BUDGETS:
                    if ex[b] is None and a > b:
                        ex[b] = el
            if scn.trace_every and (el + 1e-9) % scn.trace_every < dt:
                res.trace.append((el, list(out)))
            while cp_i < len(cps) and el >= cps[cp_i] - 1e-9:
                for i, n in enumerate(g.names):
                    res.te_at[n][cps[cp_i]] = out[i]
                cp_i += 1

        # cross-node consistency check over edges between GNSS-locked, trusted nodes
        if scn.monitor_from is not None and t >= scn.monitor_from:
            for k, l in enumerate(LINKS):
                if locked[g.idx[l.a]] and locked[g.idx[l.b]]:
                    mon_acc[k][0] += cm[k]
                    mon_acc[k][1] += 1
            tick = int(round(t / dt))
            if tick % max(1, int(MONITOR_PERIOD_S / dt)) == 0:
                period = int(round(t)) // MONITOR_PERIOD_S
                for i in range(nn):
                    if locked[i] and u_hist[i]:
                        u_by_period[i][period] = statistics.fmean(u_hist[i])
                row = {k: s / c for k, (s, c) in enumerate(mon_acc) if c}
                mon_acc = [[0.0, 0] for _ in LINKS]
                if t < mon_end:
                    train_rows.append(row)
                else:
                    if base is None:
                        base, var, thr = _train(train_rows, g, cfg)
                        res.thresholds = {g.names[i]: v for i, v in thr.items()}
                    edges = [(g.idx[LINKS[k].a], g.idx[LINKS[k].b], d - base[k], 1.0 / var[k])
                             for k, d in row.items() if k in base]
                    nodes = sorted({e[0] for e in edges} | {e[1] for e in edges})
                    if len(nodes) >= 3:
                        o = solve_offsets(nodes, edges)
                        for i in range(nn):
                            hit = i in o and abs(o[i]) > thr.get(i, math.inf)
                            consec[i] = consec[i] + 1 if hit else 0
                            if consec[i] == CONS_CONSEC:
                                ref = scn.spoof_at if scn.spoof_at is not None else mon_end
                                res.alarms.append((t - ref, g.names[i]))
                                if scn.guard:
                                    untrusted.add(i)
                                    back = period - STEER_LOOKBACK_S // MONITOR_PERIOD_S
                                    hold[i] = u_by_period[i].get(back, u_by_period[i][min(u_by_period[i])])

        for i in range(nn):
            gr = grades[i]
            tm = t + 0.5 * dt
            y = y0[i] + gr.aging_per_s * tm + amp[i] * math.sin(w_day * tm + tph[i])
            x[i] += (y + u[i]) * dt + rng.gauss(0.0, gr.adev_1s * math.sqrt(dt))
        t += dt
    return res


def _train(rows, g, cfg):
    keys = set().union(*rows) if rows else set()
    base = {k: statistics.fmean(r[k] for r in rows if k in r) for k in keys}
    var = {k: max(statistics.pvariance([r[k] for r in rows if k in r]), (1 * NS) ** 2) for k in keys}
    resid = {}
    for r in rows:
        edges = [(g.idx[LINKS[k].a], g.idx[LINKS[k].b], d - base[k], 1.0 / var[k]) for k, d in r.items()]
        nodes = sorted({e[0] for e in edges} | {e[1] for e in edges})
        if len(nodes) < 3:
            continue
        for i, v in solve_offsets(nodes, edges).items():
            resid.setdefault(i, []).append(v)
    thr = {i: CONS_K * math.sqrt(statistics.fmean(v * v for v in vals)) + cfg.cons_margin
           for i, vals in resid.items()}
    return base, var, thr


# ---------------------------------------------------------------- studies

SETTLE_S = 6 * HOUR
OUTAGE_S = 24 * HOUR


def _summ(values):
    return {"median": statistics.median(values), "p95": th.pct(values, 0.95), "max": max(values)}


def _exceed_summary(vals, horizon):
    """Median time under a budget; a run that never exceeds counts as the horizon."""
    filled = [horizon if v is None else v for v in vals]
    return {"median_s": statistics.median(filled), "never": sum(v is None for v in vals), "runs": len(vals)}


def regional_jamming_study(cfg, seeds, outage_s=OUTAGE_S):
    out = {}
    for label, mode, cal in (("alone", "alone", True), ("peers, uncalibrated", "peers", False),
                             ("peers, calibrated", "peers", True)):
        c = Config(**{**cfg.__dict__, "calibrate": cal})
        per = {n: {"te": {cp: [] for cp in CHECKPOINTS}, "max": [], "exceed": {b: [] for b in BUDGETS}}
               for n in JAMMED_REGION}
        for s in seeds:
            scn = Scenario(end_s=SETTLE_S + outage_s, mode=mode, ref_t=SETTLE_S,
                           loss={n: (SETTLE_S, math.inf) for n in JAMMED_REGION},
                           calib=(SETTLE_S - HOUR, SETTLE_S))
            r = run(scn, c, s)
            for n in JAMMED_REGION:
                for cp in CHECKPOINTS:
                    if cp in r.te_at[n]:
                        per[n]["te"][cp].append(abs(r.te_at[n][cp]))
                per[n]["max"].append(r.max_te[n])
                for b in BUDGETS:
                    per[n]["exceed"][b].append(r.exceed_at[n][b])
        out[label] = {n: {"te": {cp: _summ(v) for cp, v in d["te"].items() if v},
                          "max": _summ(d["max"]),
                          "exceed": {b: _exceed_summary(v, outage_s) for b, v in d["exceed"].items()}}
                      for n, d in per.items()}
    return out


def asymmetry_study(cfg, deltas_ns, seeds, outage_s=4 * HOUR):
    """Extra asymmetry on both microwave links into comms-relay while the region is jammed:
    present from the start (uncalibrated) or appearing after calibration (route change)."""
    k_link = next(k for k, l in enumerate(LINKS) if {l.a, l.b} == {"c2-post", "comms-relay"})
    k_other = next(k for k, l in enumerate(LINKS) if {l.a, l.b} == {"base-station", "comms-relay"})
    rows = []
    for d in deltas_ns:
        row = {"extra_asym_ns": d}
        for label, cal, when in (("uncalibrated", False, 0.0), ("calibrated, no change", True, None),
                                 ("calibrated, then route change", True, SETTLE_S)):
            c = Config(**{**cfg.__dict__, "calibrate": cal})
            ch = {}
            if when is not None:
                ch = {k_link: (when, d * NS), k_other: (when, d * NS)}
            vals = []
            for s in seeds:
                scn = Scenario(end_s=SETTLE_S + outage_s, mode="peers", ref_t=SETTLE_S + HOUR,
                               loss={n: (SETTLE_S, math.inf) for n in JAMMED_REGION},
                               calib=(SETTLE_S - HOUR, SETTLE_S), asym_change=ch, checkpoints=())
                vals.append(run(scn, c, s).max_te["comms-relay"])
            row[label] = statistics.median(vals)
        rows.append(row)
    return {"link": "both microwave links into comms-relay", "rows": rows,
            "note": "max |TE| of comms-relay 1-4 h after regional jamming, peer holdover, median of runs"}


def filter_study(cfg, seeds, outage_s=4 * HOUR):
    out = {}
    for filt in ("min", "mean"):
        for pdv in (1.0, 4.0):
            c = Config(**{**cfg.__dict__, "pkt_filter": filt, "pdv_scale": pdv, "calibrate": False})
            vals = []
            for s in seeds:
                scn = Scenario(end_s=SETTLE_S + outage_s, mode="peers", ref_t=SETTLE_S + HOUR,
                               loss={n: (SETTLE_S, math.inf) for n in JAMMED_REGION},
                               checkpoints=())
                r = run(scn, c, s)
                vals.append(max(r.max_te[n] for n in JAMMED_REGION))
            out[f"{filt} filter, PDV x{pdv:g}"] = statistics.median(vals)
    return out


SPOOF_SETTLE_S = 2 * HOUR
SPOOF_TRAIN_S = HOUR
SPOOF_WALK_S = 2 * HOUR
SPOOF_JAMMED = ("sensor-north", "sensor-south")


def spoof_scenario(node, rate, guard, monitor=True):
    start = SPOOF_SETTLE_S + SPOOF_TRAIN_S
    return Scenario(end_s=start + SPOOF_WALK_S, mode="peers", ref_t=start,
                    loss={n: (SPOOF_SETTLE_S, math.inf) for n in SPOOF_JAMMED},
                    calib=(SPOOF_SETTLE_S - 1800, SPOOF_SETTLE_S),
                    spoof_node=node if rate else None, spoof_at=start if rate else None, spoof_rate=rate,
                    monitor_from=SPOOF_SETTLE_S if monitor else None, train_s=SPOOF_TRAIN_S,
                    guard=guard, checkpoints=())


def spoof_study(cfg, nodes, rates_ns, seeds, control_seeds):
    c = Config(**{**cfg.__dict__, "dt": 1.0})
    rows = []
    for node in nodes:
        for rate in rates_ns:
            det, iso_ok, te_unguarded, te_guarded, te_self = [], 0, [], [], []
            for s in seeds:
                ug = run(spoof_scenario(node, rate * NS, guard=False), c, s)
                gd = run(spoof_scenario(node, rate * NS, guard=True), c, s)
                first = gd.alarms[0] if gd.alarms else None
                det.append(first[0] if first else None)
                iso_ok += bool(first and first[1] == node and len(gd.alarms) == 1)
                te_unguarded.append(max(ug.max_te[n] for n in SPOOF_JAMMED))
                te_guarded.append(max(gd.max_te[n] for n in SPOOF_JAMMED))
                te_self.append(gd.max_te[node])
            hit = [d for d in det if d is not None]
            rows.append({"node": node, "rate_ns_per_s": rate, "runs": len(seeds),
                         "detected": len(hit), "detect_s_median": statistics.median(hit) if hit else None,
                         "detect_s_max": max(hit) if hit else None, "isolated_only_spoofed": iso_ok,
                         "downstream_max_te_unguarded_us": statistics.median(te_unguarded) / US,
                         "downstream_max_te_guarded_us": statistics.median(te_guarded) / US,
                         "spoofed_node_max_te_guarded_us": statistics.median(te_self) / US})
    fa, hours = 0, 0.0
    for s in control_seeds:
        r = run(spoof_scenario(nodes[0], 0.0, guard=True), c, s)
        fa += len(r.alarms)
        hours += SPOOF_WALK_S / HOUR
    return {"rows": rows, "control_runs": len(control_seeds), "false_alarms": fa, "monitored_hours": hours}


def all_lost_study(cfg, seeds, outage_s=OUTAGE_S):
    out = {"weights": ensemble_weights(cfg), "best_clock": best_clock(cfg)}
    for mode in ("alone", "best", "ensemble"):
        worst = {cp: [] for cp in CHECKPOINTS}
        per_node = {n.name: {cp: [] for cp in CHECKPOINTS} for n in NODES}
        exceed = {b: [] for b in BUDGETS}
        for s in seeds:
            scn = Scenario(end_s=SETTLE_S + outage_s, mode=mode, ref_t=SETTLE_S,
                           loss={n.name: (SETTLE_S, math.inf) for n in NODES},
                           calib=(SETTLE_S - HOUR, SETTLE_S))
            r = run(scn, cfg, s)
            for cp in CHECKPOINTS:
                if all(cp in r.te_at[n.name] for n in NODES):
                    worst[cp].append(max(abs(r.te_at[n.name][cp]) for n in NODES))
                    for n in NODES:
                        per_node[n.name][cp].append(abs(r.te_at[n.name][cp]))
            for b in BUDGETS:
                ts = [r.exceed_at[n.name][b] for n in NODES]
                exceed[b].append(None if all(v is None for v in ts) else min(v for v in ts if v is not None))
        out[mode] = {"worst_node": {cp: _summ(v) for cp, v in worst.items() if v},
                     "per_node_median": {n: {cp: statistics.median(v) for cp, v in d.items() if v}
                                         for n, d in per_node.items()},
                     "worst_exceed": {b: _exceed_summary(v, outage_s) for b, v in exceed.items()}}
    return out


# ---------------------------------------------------------------- printing

def fmt(v):
    if v is None:
        return "-"
    a = abs(v)
    if a >= 1e-3:
        return f"{v * 1e3:.2f} ms"
    if a >= 1e-6:
        return f"{v * 1e6:.2f} us"
    return f"{v * 1e9:.0f} ns"


def fmt_dur(v, never=0, runs=0):
    if runs and never == runs:
        return f"whole {v / HOUR:.0f} h"
    s = f"{v / HOUR:.1f} h" if v >= HOUR else f"{v / 60:.0f} min"
    return s + (f" ({never}/{runs} never exceed)" if never else "")


def write_trace(path, cfg, seed=1, every=600.0):
    """CSV of |TE| vs time per node for one seed: regional jamming (alone, peers) and all lost
    (alone, best, ensemble)."""
    rows = []
    cases = [("regional", m, {n: (SETTLE_S, math.inf) for n in JAMMED_REGION}) for m in ("alone", "peers")]
    cases += [("all-lost", m, {n.name: (SETTLE_S, math.inf) for n in NODES}) for m in ("alone", "best", "ensemble")]
    for name, mode, loss in cases:
        scn = Scenario(end_s=SETTLE_S + OUTAGE_S, mode=mode, ref_t=SETTLE_S, loss=loss,
                       calib=(SETTLE_S - HOUR, SETTLE_S), checkpoints=(), trace_every=every)
        for el, te in run(scn, cfg, seed).trace:
            rows.append([name, mode, f"{el / HOUR:.3f}"] + [f"{v / NS:.1f}" for v in te])
    with open(path, "w") as fh:
        fh.write(",".join(["scenario", "mode", "hours"] + [f"{n.name}_te_ns" for n in NODES]) + "\n")
        for r in rows:
            fh.write(",".join(r) + "\n")
    return len(rows)


def budget_label(b):
    return f"<{b / US:g} us"


def print_regional(res, outage_s):
    print(f"\n(a) Regional jamming: {', '.join(JAMMED_REGION)} lose GNSS for {outage_s / HOUR:.0f} h "
          "after 6 h of discipline")
    print("    |TE| median (p95) over runs at 1 h / 4 h / 24 h; then median time staying under each budget")
    for label, per in res.items():
        print(f"  {label}")
        for n, d in per.items():
            te = "  ".join(f"{fmt(d['te'][cp]['median']):>9} ({fmt(d['te'][cp]['p95']):>9})"
                           for cp in (HOUR, 4 * HOUR, 24 * HOUR) if cp in d["te"])
            ex = "  ".join(f"{budget_label(b)}: {fmt_dur(e['median_s'], e['never'], e['runs'])}"
                           for b, e in d["exceed"].items())
            grade = next(x.grade for x in NODES if x.name == n)
            print(f"    {n:<13} {grade:<5} {te}")
            print(f"    {'':<19} {ex}")


def print_asym(res):
    print(f"\n(a2) Path asymmetry, extra delay on {res['link']}; {res['note']}")
    print(f"  {'extra asym':>10} {'uncalibrated':>13} {'calibrated':>11} {'calibrated, then route change':>30}")
    for r in res["rows"]:
        print(f"  {r['extra_asym_ns']:>7g} ns {fmt(r['uncalibrated']):>13} {fmt(r['calibrated, no change']):>11} "
              f"{fmt(r['calibrated, then route change']):>30}")


def print_filter(res):
    print("\n(a3) Packet filter vs queueing asymmetry, uncalibrated, worst jammed node max |TE| 1-4 h after jamming")
    for k, v in res.items():
        print(f"  {k:<22} {fmt(v)}")


def print_spoof(res):
    print(f"\n(b) Time-push spoof on one node's GNSS; {', '.join(SPOOF_JAMMED)} are GNSS-denied and take time "
          "from the network")
    print("    settle 2 h, consistency-check training 1 h, walk 2 h; dt 1 s")
    print(f"  {'node':<12} {'ns/s':>5} {'detected':>9} {'det med s':>10} {'det max s':>10} {'clean isolation':>16} "
          f"{'downstream unguarded':>21} {'downstream guarded':>19} {'spoofed node guarded':>21}")
    for r in res["rows"]:
        print(f"  {r['node']:<12} {r['rate_ns_per_s']:>5g} {r['detected']:>4}/{r['runs']:<4} "
              f"{r['detect_s_median'] if r['detect_s_median'] is not None else '-':>10} "
              f"{r['detect_s_max'] if r['detect_s_max'] is not None else '-':>10} "
              f"{r['isolated_only_spoofed']:>12}/{r['runs']:<3} "
              f"{fmt(r['downstream_max_te_unguarded_us'] * US):>21} {fmt(r['downstream_max_te_guarded_us'] * US):>19} "
              f"{fmt(r['spoofed_node_max_te_guarded_us'] * US):>21}")
    print(f"  no-spoof control: {res['false_alarms']} alarms in {res['control_runs']} runs "
          f"({res['monitored_hours']:.0f} monitored hours)")
    print("  detection s = seconds after the walk starts; TE columns = median over runs of max |TE| during the walk")


def print_all_lost(res):
    print("\n(c) All GNSS lost for 24 h. ADEV weights at tau = 24 h: "
          + ", ".join(f"{k} {v:.3f}" for k, v in res["weights"].items()))
    print(f"    best single clock by the same model: {res['best_clock']}")
    for mode in ("alone", "best", "ensemble"):
        d = res[mode]
        wn = "  ".join(f"{cp / HOUR:g} h {fmt(v['median'])} ({fmt(v['p95'])})" for cp, v in d["worst_node"].items())
        ex = "  ".join(f"{budget_label(b)}: {fmt_dur(e['median_s'], e['never'], e['runs'])}"
                       for b, e in d["worst_exceed"].items())
        print(f"  {mode:<9} worst node |TE| median (p95): {wn}")
        print(f"  {'':<9} worst node time under budget: {ex}")
    print("  per node median |TE| at 24 h:")
    for n in NODES:
        print(f"    {n.name:<13} {n.grade:<5} " + "  ".join(
            f"{mode} {fmt(res[mode]['per_node_median'][n.name].get(24 * HOUR))}" for mode in ("alone", "best", "ensemble")))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", type=int, default=10, help="Monte Carlo runs for (a) and (c)")
    p.add_argument("--spoof-seeds", type=int, default=5)
    p.add_argument("--control-runs", type=int, default=20)
    p.add_argument("--rates", type=float, nargs="+", default=[1.0, 5.0, 50.0], help="spoof walk rates, ns/s")
    p.add_argument("--spoof-nodes", nargs="+", default=["comms-relay", "radar"])
    p.add_argument("--temp-fraction", type=float, default=0.1)
    p.add_argument("--only", choices=["a", "b", "c"], help="run one study")
    p.add_argument("--json", help="write all results to this JSON file")
    p.add_argument("--trace", help="write a CSV of TE vs time per node (one seed) to this file")
    a = p.parse_args(argv)

    cfg = Config(temp_fraction=a.temp_fraction)
    seeds = list(range(1, a.seeds + 1))
    print("nodes: " + ", ".join(f"{n.name} ({n.grade})" for n in NODES))
    print("links: " + ", ".join(f"{l.a}<=>{l.b} {l.kind} asym {l.asym / NS:+.0f} ns "
                                f"q {l.q_ab / US:g}/{l.q_ba / US:g} us" for l in LINKS))
    print(f"temperature fraction {cfg.temp_fraction}, PPS noise {cfg.sigma_pps / NS:.0f} ns, "
          f"{cfg.pkt_rate:g} sync packets/s, {cfg.pkt_filter} filter")
    out = {}
    if a.only in (None, "a"):
        out["regional"] = regional_jamming_study(cfg, seeds)
        print_regional(out["regional"], OUTAGE_S)
        out["asymmetry"] = asymmetry_study(cfg, [0, 500, 1000, 2000, 4000], seeds[:3])
        print_asym(out["asymmetry"])
        out["filter"] = filter_study(cfg, seeds[:3])
        print_filter(out["filter"])
    if a.only in (None, "b"):
        out["spoof"] = spoof_study(cfg, a.spoof_nodes, a.rates, list(range(1, a.spoof_seeds + 1)),
                                   list(range(100, 100 + a.control_runs)))
        print_spoof(out["spoof"])
    if a.only in (None, "c"):
        out["all_lost"] = all_lost_study(cfg, seeds)
        print_all_lost(out["all_lost"])
    if a.trace:
        print(f"\ntrace: {write_trace(a.trace, cfg)} rows => {a.trace}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
