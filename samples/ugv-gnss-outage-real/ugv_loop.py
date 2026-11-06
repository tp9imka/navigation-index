"""Ground-vehicle GNSS outage loop on a real NCLT Segway log: wheel odometry / IMU dead reckoning
bridging GNSS outages, a chi-square innovation gate, and an odometry-vs-GNSS drag detector.

Configs (what propagates the state between GNSS fixes):
  ins       MEMS accel + gyro strapdown (Microstrain GX3, levelled with its roll/pitch); no wheels.
            Reuses the 8-state EKF of ../gnss-ins-ekf-outage (mechanize + update).
  odo-mems  wheel speed + MEMS z gyro; 5-state EKF [n, e, psi, gyro bias, wheel scale].
  odo-fog   wheel speed + KVH fibre-optic gyro; same 5-state EKF.

python3 ugv_loop.py                 all experiments on data/2013-01-10
python3 ugv_loop.py stats|outage|multipath|spoof
Python 3 stdlib only.
"""
import argparse
import bisect
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "gnss-ins-ekf-outage"))
import ekf_outage as base  # noqa: E402
import matlite as m  # noqa: E402

import nclt_io  # noqa: E402

CONFIGS = ("ins", "odo-mems", "odo-fog")
GNSS_SD_BY_MODE = {3: 4.0, 2: 8.0}  # m per axis; set a priori for a consumer receiver, not fitted
GNSS_UPDATE_PERIOD_S = 1.0  # consumer fixes arrive at ~5-8 Hz with correlated errors; use 1 Hz
CHI2_GATE = base.CHI2_2DOF_999
GATE_ALARM_CONSECUTIVE = base.ALARM_CONSECUTIVE
COV_PERIOD_S = 0.1
MAX_PROP_GAP_S = 0.5  # a sensor gap longer than this is skipped, not integrated across

# Drag detector: GNSS displacement vs odometry displacement over a sliding window.
# These three values were fixed before the clean log was evaluated and were not tuned on it.
DRAG_WINDOW_S = 30.0
DRAG_THRESHOLD_M = 15.0
DRAG_PERSIST = 3
DRAG_EPISODE_GAP_S = 5.0  # no evaluation for this long (GNSS gap) ends an alarm episode

OUTAGE_LENGTHS_S = (10, 30, 60, 120)
OUTAGE_START_STEP_S = 20.0
OUTAGE_FIRST_START_S = 60.0
SPOOF_RATES_MPS = (0.1, 0.3, 1.0)
SPOOF_STARTS_S = (100, 200, 300, 400, 500, 600, 700, 800)
SPOOF_MAX_S = 200.0
SPOOF_DIRECTION_RAD = base.SPOOF_DIRECTION_RAD
ATTRIBUTION_S = 10.0  # an attack-run alarm this close to a clean-log alarm is not credited
BAD_FIX_M, GOOD_FIX_M = 15.0, 10.0  # truth-labelled consumer fix error classes

ODO_NOISE = {  # continuous-time process noise densities
    "odo-mems": {"q_pos": 0.05, "q_psi": math.radians(0.3) ** 2, "q_bg": math.radians(0.005) ** 2,
                 "q_k": 1e-7, "bg0_sd": math.radians(0.5)},
    "odo-fog": {"q_pos": 0.05, "q_psi": math.radians(0.02) ** 2, "q_bg": math.radians(0.0005) ** 2,
                "q_k": 1e-7, "bg0_sd": math.radians(0.05)},
}
INS_EXTRA_Q_ACC = 0.3 ** 2  # m^2/s^3: tilt error and Segway pitching leak into level accel
INS_EXTRA_Q_BA = 1e-3 ** 2
INS_EXTRA_Q_PSI = math.radians(0.3) ** 2


class OdoEkf:
    """x = [n, e, psi, gyro bias, wheel scale]. Propagated by gyro samples; wheel speed is held."""

    def __init__(self, n, e, psi, noise):
        self.x = [n, e, psi, 0.0, 1.0]
        self.P = m.diag([3.0 ** 2, 3.0 ** 2, math.radians(2.0) ** 2, noise["bg0_sd"] ** 2, 0.1 ** 2])
        self.q = noise
        self.v_wheel = 0.0
        self.t = None
        self.cov_dt = 0.0
        self.cov_on = True

    def wheel(self, t, v):
        self.v_wheel = v

    def gyro(self, t, w):
        if self.t is not None and 0.0 < t - self.t <= MAX_PROP_GAP_S:
            dt = t - self.t
            n, e, psi, bg, k = self.x
            v = k * self.v_wheel
            self.x[0] = n + v * math.cos(psi) * dt
            self.x[1] = e + v * math.sin(psi) * dt
            self.x[2] = psi + (w - bg) * dt
            if self.cov_on:
                self.cov_dt += dt
                if self.cov_dt >= COV_PERIOD_S:
                    self.propagate_cov(self.cov_dt)
                    self.cov_dt = 0.0
        self.t = t

    def propagate_cov(self, dt):
        psi, k = self.x[2], self.x[4]
        vw = self.v_wheel
        c, s = math.cos(psi), math.sin(psi)
        F = m.eye(5)
        F[0][2], F[0][4] = -k * vw * s * dt, vw * c * dt
        F[1][2], F[1][4] = k * vw * c * dt, vw * s * dt
        F[2][3] = -dt
        q = self.q
        Q = m.diag([q["q_pos"] * dt, q["q_pos"] * dt, q["q_psi"] * dt, q["q_bg"] * dt, q["q_k"] * dt])
        self.P = m.symmetrize(m.add(m.matmul(m.matmul(F, self.P), m.transpose(F)), Q))

    def innovation(self, zn, ze, sd):
        return position_innovation(self, zn, ze, sd)

    def update(self, y, Si):
        position_update(self, y, Si)


class InsEkf(base.Ekf):
    """The 8-state 2-D INS of gnss-ins-ekf-outage, driven by real levelled MEMS accel and gyro.
    mechanize() and update() are the base class's; process and measurement noise are local."""

    def __init__(self, n, e, psi):
        super().__init__([n, e, 0.0, 0.0, psi, 0.0, 0.0, 0.0])
        self.P[2][2] = self.P[3][3] = 0.1 ** 2
        self.t = None
        self.cov_dt = 0.0
        self.cov_on = True

    def imu(self, t, fx, fy, w):
        if self.t is not None and 0.0 < t - self.t <= MAX_PROP_GAP_S:
            dt = t - self.t
            self.mechanize(fx, fy, w, dt)
            if self.cov_on:
                self.cov_dt += dt
                if self.cov_dt >= COV_PERIOD_S:
                    self.propagate_cov(self.cov_dt)
                    self.cov_dt = 0.0
        self.t = t

    def propagate_cov(self, dt):
        super().propagate_cov(dt)
        self.P[2][2] += INS_EXTRA_Q_ACC * dt
        self.P[3][3] += INS_EXTRA_Q_ACC * dt
        self.P[4][4] += INS_EXTRA_Q_PSI * dt
        self.P[5][5] += INS_EXTRA_Q_BA * dt
        self.P[6][6] += INS_EXTRA_Q_BA * dt

    def innovation(self, zn, ze, sd):
        return position_innovation(self, zn, ze, sd)


def position_innovation(f, zn, ze, sd):
    y = (zn - f.x[0], ze - f.x[1])
    S = [[f.P[0][0] + sd * sd, f.P[0][1]], [f.P[1][0], f.P[1][1] + sd * sd]]
    Si = m.inv2(S)
    nis = y[0] * (Si[0][0] * y[0] + Si[0][1] * y[1]) + y[1] * (Si[1][0] * y[0] + Si[1][1] * y[1])
    return y, Si, nis


def position_update(f, y, Si):
    nx = len(f.x)
    PHt = [[row[0], row[1]] for row in f.P]
    K = m.matmul(PHt, Si)
    for i in range(nx):
        f.x[i] += K[i][0] * y[0] + K[i][1] * y[1]
    KH = m.zeros(nx, nx)
    for i in range(nx):
        KH[i][0], KH[i][1] = K[i][0], K[i][1]
    f.P = m.symmetrize(m.matmul(m.sub(m.eye(nx), KH), f.P))


def level_accel(f_body, roll, pitch):
    """Body specific force (x fwd, y right, z down) => horizontal components in the heading frame."""
    fx, fy, fz = f_body
    cr, sr, cp, sp = math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch)
    return cp * fx + sp * sr * fy + sp * cr * fz, cr * fy - sr * fz


def build_events(session, cfg):
    """Time-sorted propagation events for one config: (t, kind, ...)."""
    ev = []
    if cfg == "ins":
        et = [r[0] for r in session.euler]
        for r in session.imu:
            i = min(max(bisect.bisect_left(et, r[0]), 0), len(et) - 1)
            roll, pitch = session.euler[i][1], session.euler[i][2]
            fx, fy = level_accel((r[4], r[5], r[6]), roll, pitch)
            ev.append((r[0], "i", fx, fy, r[9]))
        return ev
    for r in session.wheels:
        ev.append((r[0], "w", 0.5 * (r[1] + r[2])))
    if cfg == "odo-mems":
        ev.extend((r[0], "g", r[9]) for r in session.imu)
    else:
        for a, b in zip(session.kvh, session.kvh[1:]):
            dt = b[0] - a[0]
            if dt > 0:
                ev.append((b[0], "g", -nclt_io.wrap(b[1] - a[1]) / dt))
    ev.sort(key=lambda e: e[0])
    return ev


def step(f, e):
    if e[1] == "g":
        f.gyro(e[0], e[2])
    elif e[1] == "w":
        f.wheel(e[0], e[2])
    else:
        f.imu(e[0], e[2], e[3], e[4])


def make_filter(cfg, truth, t):
    n, e = truth.pos(t)
    psi = truth.heading(t)
    return InsEkf(n, e, psi) if cfg == "ins" else OdoEkf(n, e, psi, ODO_NOISE[cfg])


def decimate(fixes, period=GNSS_UPDATE_PERIOD_S):
    out, last = [], -1e9
    for fx in fixes:
        if fx[0] >= last + period - 1e-6:
            out.append(fx)
            last = fx[0]
    return out


def inject_drag(fixes, start, rate, direction=SPOOF_DIRECTION_RAD):
    """Coherent drag added to recorded fixes from `start`: offset grows at `rate` m/s."""
    out = []
    for t, mode, zn, ze in fixes:
        off = rate * (t - start) if t >= start else 0.0
        out.append((t, mode, zn + off * math.cos(direction), ze + off * math.sin(direction)))
    return out


class DragDetector:
    """|GNSS displacement - odometry displacement| over DRAG_WINDOW_S. The odometry track is
    a free-running wheel + gyro integration; its heading is re-anchored to the filter heading
    at the start of each window, so only the filter's state from W seconds ago is trusted."""

    def __init__(self, window=DRAG_WINDOW_S, threshold=DRAG_THRESHOLD_M, persist=DRAG_PERSIST):
        self.window, self.threshold, self.persist = window, threshold, persist
        self.dn = self.de = self.h = 0.0
        self.t = None
        self.v = 0.0
        self.hist = []  # (t, zn, ze, dn, de, h, psi_filter)
        self.count = 0
        self.alarm_t = None
        self.episodes = []
        self.stats = []

    def wheel(self, t, v):
        self.v = v

    def gyro(self, t, w, bg, k):
        if self.t is not None and 0.0 < t - self.t <= MAX_PROP_GAP_S:
            dt = t - self.t
            self.dn += k * self.v * math.cos(self.h) * dt
            self.de += k * self.v * math.sin(self.h) * dt
            self.h += (w - bg) * dt
        self.t = t

    def fix(self, t, zn, ze, psi_filter):
        self.hist.append((t, zn, ze, self.dn, self.de, self.h, psi_filter))
        ts = [h[0] for h in self.hist]
        i = bisect.bisect_left(ts, t - self.window - 1.0)
        self.hist = self.hist[i:]
        ts = ts[i:]
        j = bisect.bisect_left(ts, t - self.window)
        if j >= len(self.hist) or abs(self.hist[j][0] - (t - self.window)) > 1.0:
            return None
        a = self.hist[j]
        rot = a[6] - a[5]
        odn, ode = self.dn - a[3], self.de - a[4]
        c, s = math.cos(rot), math.sin(rot)
        on, oe = c * odn - s * ode, s * odn + c * ode
        stat = math.hypot((zn - a[1]) - on, (ze - a[2]) - oe)
        if self.stats and t - self.stats[-1][0] > DRAG_EPISODE_GAP_S:
            self.count = 0
        self.stats.append((t, stat))
        self.count = self.count + 1 if stat > self.threshold else 0
        if self.count == self.persist:
            self.episodes.append(t)
            if self.alarm_t is None:
                self.alarm_t = t
        return stat


def run(session, cfg, fixes, gate=True, events=None, snapshot_times=(), drag=False):
    """One pass over the log. Returns a dict with per-fix records, gate alarm episodes,
    the drag detector and (event index, filter copy) snapshots."""
    events = events if events is not None else build_events(session, cfg)
    k0 = next(i for i, e in enumerate(events) if session.truth.pos(e[0]) is not None)
    f = make_filter(cfg, session.truth, events[k0][0])
    det = DragDetector() if drag and cfg != "ins" else None
    snaps, snap_i = [], 0
    snapshot_times = sorted(snapshot_times)
    recs, gate_episodes = [], []
    consecutive, gi = 0, 0
    while gi < len(fixes) and fixes[gi][0] < events[k0][0]:
        gi += 1
    for k in range(k0, len(events)):
        e = events[k]
        t = e[0]
        while gi < len(fixes) and fixes[gi][0] <= t:
            ft, mode, zn, ze = fixes[gi]
            gi += 1
            sd = GNSS_SD_BY_MODE[mode]
            y, Si, nis = f.innovation(zn, ze, sd)
            prior = (f.x[0], f.x[1])
            rejected = gate and nis > CHI2_GATE
            if rejected:
                consecutive += 1
                if consecutive == GATE_ALARM_CONSECUTIVE:
                    gate_episodes.append(ft)
            else:
                consecutive = 0
                f.update(y, Si)
            if det is not None:
                det.fix(ft, zn, ze, f.x[2])
            recs.append({"t": ft, "z": (zn, ze), "prior": prior, "post": (f.x[0], f.x[1]),
                         "nis": nis, "rejected": rejected, "mode": mode})
        while snap_i < len(snapshot_times) and snapshot_times[snap_i] <= t:
            snaps.append((snapshot_times[snap_i], k, copy.deepcopy(f)))
            snap_i += 1
        step(f, e)
        if det is not None:
            if e[1] == "w":
                det.wheel(t, e[2])
            elif e[1] == "g":
                det.gyro(t, e[2], f.x[3], f.x[4])
    return {"recs": recs, "gate_episodes": gate_episodes, "drag": det, "snaps": snaps, "filter": f}


def free_run(f, events, k0, t_start, checkpoints, truth):
    """Propagate a filter copy with no GNSS. Per checkpoint L: (absolute error vs truth at
    t_start + L, dead-reckoning drift = error of the displacement since t_start)."""
    f = copy.deepcopy(f)
    f.cov_on = False
    p0, g0 = (f.x[0], f.x[1]), truth.pos(t_start)
    out, ci = {}, 0
    cps = sorted(checkpoints)
    for e in events[k0:]:
        while ci < len(cps) and e[0] >= t_start + cps[ci]:
            g = truth.pos(t_start + cps[ci])
            drift = math.hypot((f.x[0] - p0[0]) - (g[0] - g0[0]), (f.x[1] - p0[1]) - (g[1] - g0[1]))
            out[cps[ci]] = (math.hypot(f.x[0] - g[0], f.x[1] - g[1]), drift)
            ci += 1
        if ci >= len(cps):
            break
        step(f, e)
    return out


def err_to_truth(truth, t, p):
    g = truth.pos(t)
    return None if g is None else math.hypot(p[0] - g[0], p[1] - g[1])


def pct(vals, q):
    s = sorted(vals)
    return s[min(len(s) - 1, int(q * (len(s) - 1) + 0.5))] if s else float("nan")


def natural_gaps(fixes, min_gap=5.0):
    return [(a[0], b[0]) for a, b in zip(fixes, fixes[1:]) if b[0] - a[0] >= min_gap]


# ----------------------------------------------------------------------------------- reports

def report_stats(s):
    t0, t1 = s.truth.span()
    print(f"session span {t1 - t0:.0f} s, truth path {s.truth.path_length(t0, t1):.0f} m")
    print(f"frame fit on RTK 3-D fixes: rotation {math.degrees(s.frame.theta):.2f} deg, "
          f"residual median {pct(s.align_residuals, 0.5):.2f} m, p95 {pct(s.align_residuals, 0.95):.2f} m "
          f"(n={len(s.align_residuals)})")
    print(f"consumer GPS fixes: {len(s.gps)} raw, {len(decimate(s.gps))} at 1 Hz")
    for mode in (3, 2):
        errs = [err_to_truth(s.truth, t, (n, e)) for t, md, n, e in s.gps if md == mode]
        errs = [x for x in errs if x is not None]
        print(f"  mode {mode}: n={len(errs)} error median {pct(errs, 0.5):.1f} m, p95 {pct(errs, 0.95):.1f} m, "
              f"max {max(errs):.1f} m")
    print("natural gaps >= 5 s in consumer fixes:",
          ", ".join(f"{a:.1f}-{b:.1f} s ({b - a:.1f} s)" for a, b in natural_gaps(s.gps)) or "none")


def report_outage(s):
    fixes = decimate(s.gps)
    t0, t1 = s.truth.span()
    starts = []
    t = OUTAGE_FIRST_START_S
    while t + min(OUTAGE_LENGTHS_S) < t1:
        starts.append(t)
        t += OUTAGE_START_STEP_S
    print(f"Injected outages: start every {OUTAGE_START_STEP_S:.0f} s from {OUTAGE_FIRST_START_S:.0f} s; "
          "filter runs gated on real 1 Hz fixes up to the start, then dead-reckons with no GNSS.")
    print("Horizontal error at outage end [m], median / p95 / max over start times (n windows).")
    print("drift = error of the dead-reckoned displacement since outage start; abs = absolute error "
          "vs truth (adds the GNSS-aided error at the start).")
    print(f"{'config':<15}" + "".join(f"{str(L) + ' s':>24}" for L in OUTAGE_LENGTHS_S))
    dist = {L: [] for L in OUTAGE_LENGTHS_S}
    nat = {}
    for cfg in CONFIGS:
        ev = build_events(s, cfg)
        r = run(s, cfg, fixes, gate=True, events=ev, snapshot_times=starts)
        res = {L: [] for L in OUTAGE_LENGTHS_S}
        for ts, k, f in r["snaps"]:
            out = free_run(f, ev, k, ts, [L for L in OUTAGE_LENGTHS_S if ts + L < t1], s.truth)
            for L, v in out.items():
                res[L].append(v)
                if cfg == CONFIGS[0]:
                    dist[L].append(s.truth.path_length(ts, ts + L))
        for idx, label in ((1, "drift"), (0, "abs")):
            cells = [f"{pct([v[idx] for v in res[L]], .5):6.1f} /{pct([v[idx] for v in res[L]], .95):6.1f}"
                     f" /{max(v[idx] for v in res[L]):6.1f} ({len(res[L])})" for L in OUTAGE_LENGTHS_S]
            print(f"{cfg + ' ' + label:<15}" + "".join(f"{c:>24}" for c in cells))
        for a, b in natural_gaps(fixes, 20.0):
            rec = next(x for x in r["recs"] if x["t"] == b)
            before = next(x for x in reversed(r["recs"]) if x["t"] == a)
            nat.setdefault((a, b), {})[cfg] = (err_to_truth(s.truth, a, before["post"]),
                                               err_to_truth(s.truth, b, rec["prior"]))
    print("truth path length in window [m], median / max: " +
          ", ".join(f"{L} s: {pct(dist[L], .5):.0f} / {max(dist[L]):.0f}" for L in OUTAGE_LENGTHS_S))
    for (a, b), d in nat.items():
        print(f"Natural GNSS gap {a:.1f}-{b:.1f} s ({b - a:.1f} s, path {s.truth.path_length(a, b):.0f} m): "
              "error at gap start => at gap end before the first new fix")
        for cfg, (e0, e1) in d.items():
            print(f"  {cfg:<10}{e0:7.1f} m => {e1:7.1f} m")


def report_multipath(s):
    fixes = decimate(s.gps)
    print(f"Gate: chi-square 2 dof 99.9 % (NIS > {CHI2_GATE}); 1 Hz real consumer fixes; "
          f"fix classes by error vs truth: bad > {BAD_FIX_M:.0f} m, good < {GOOD_FIX_M:.0f} m")
    print(f"{'config':<10}{'bad fixes rejected':>20}{'good rejected':>15}{'gate alarms':>13}"
          f"{'RMS gate':>10}{'RMS no-gate':>13}{'max gate':>10}{'max no-gate':>13}")
    for cfg in CONFIGS:
        ev = build_events(s, cfg)
        rg = run(s, cfg, fixes, gate=True, events=ev)
        rn = run(s, cfg, fixes, gate=False, events=ev)
        bad = good = bad_rej = good_rej = 0
        for rec in rg["recs"]:
            fe = err_to_truth(s.truth, rec["t"], rec["z"])
            if fe is None:
                continue
            if fe > BAD_FIX_M:
                bad += 1
                bad_rej += rec["rejected"]
            elif fe < GOOD_FIX_M:
                good += 1
                good_rej += rec["rejected"]
        eg = [x for x in (err_to_truth(s.truth, r["t"], r["post"]) for r in rg["recs"]) if x is not None]
        en = [x for x in (err_to_truth(s.truth, r["t"], r["post"]) for r in rn["recs"]) if x is not None]
        rms = lambda v: math.sqrt(sum(x * x for x in v) / len(v))
        print(f"{cfg:<10}{f'{bad_rej}/{bad}':>20}{f'{good_rej}/{good}':>15}{len(rg['gate_episodes']):>13}"
              f"{rms(eg):>10.1f}{rms(en):>13.1f}{max(eg):>10.1f}{max(en):>13.1f}")
        if rg["gate_episodes"]:
            print(f"{'':<10}gate alarm episodes (3 consecutive rejects) at: "
                  + ", ".join(f"{t:.0f} s" for t in rg["gate_episodes"]))


def report_spoof(s):
    fixes = decimate(s.gps)
    t1 = s.truth.span()[1]
    print(f"Injected drag on the REAL consumer fixes (synthetic attack, real noise and multipath): offset "
          f"grows at rate r from each start time, direction {math.degrees(SPOOF_DIRECTION_RAD):.0f} deg, "
          f"for up to {SPOOF_MAX_S:.0f} s. Detectors: gate alarm = {GATE_ALARM_CONSECUTIVE} consecutive "
          f"rejects; drag test = |dGNSS - dOdo| over {DRAG_WINDOW_S:.0f} s > {DRAG_THRESHOLD_M:.0f} m "
          f"for {DRAG_PERSIST} consecutive fixes.")
    for cfg in ("odo-mems", "odo-fog"):
        ev = build_events(s, cfg)
        clean = run(s, cfg, fixes, gate=True, events=ev, drag=True)
        st = [v for _, v in clean["drag"].stats]
        print(f"\n[{cfg}] clean log: gate alarm episodes {len(clean['gate_episodes'])} "
              f"({', '.join(f'{t:.0f}' for t in clean['gate_episodes']) or '-'} s); drag alarm episodes "
              f"{len(clean['drag'].episodes)} ({', '.join(f'{t:.0f}' for t in clean['drag'].episodes) or '-'} s); "
              f"drag statistic median {pct(st, .5):.1f} m, p99 {pct(st, .99):.1f} m, max {max(st):.1f} m")
        print(f"{'rate m/s':>9}{'gate: detected':>16}{'median s':>10}{'offset m':>10}"
              f"{'drag: detected':>16}{'median s':>10}{'offset m':>10}")
        missed = []
        for rate in SPOOF_RATES_MPS:
            g_lat, d_lat, n = [], [], 0
            for ts in SPOOF_STARTS_S:
                if ts + 60 > t1:
                    continue
                n += 1
                sp = [fx for fx in inject_drag(fixes, ts, rate) if fx[0] <= ts + SPOOF_MAX_S]
                sp += [fx for fx in fixes if fx[0] > ts + SPOOF_MAX_S]
                r = run(s, cfg, sp, gate=True, events=ev, drag=True)
                ga = attack_alarms(r["gate_episodes"], clean["gate_episodes"], ts)
                da = attack_alarms(r["drag"].episodes, clean["drag"].episodes, ts)
                if ga:
                    g_lat.append(ga[0] - ts)
                if da:
                    d_lat.append(da[0] - ts)
                else:
                    missed.append(f"{rate} m/s from {ts} s")
            fmt = lambda lat: (f"{len(lat)}/{n}", f"{pct(lat, .5):.0f}" if lat else "-",
                               f"{rate * pct(lat, .5):.0f}" if lat else "-")
            a, b = fmt(g_lat), fmt(d_lat)
            print(f"{rate:>9}{a[0]:>16}{a[1]:>10}{a[2]:>10}{b[0]:>16}{b[1]:>10}{b[2]:>10}")
        print(f"drag test missed: {', '.join(missed) or 'none'}")
    print(f"\nAn alarm in an attack run counts as a detection only if it falls inside the attack window "
          f"and no clean-log alarm of the same detector lies within {ATTRIBUTION_S:.0f} s of it. Offset = "
          "rate x median delay.")


def attack_alarms(episodes, clean_episodes, start):
    return [t for t in episodes if start <= t <= start + SPOOF_MAX_S
            and not any(abs(t - c) <= ATTRIBUTION_S for c in clean_episodes)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", nargs="?", default="all", choices=("all", "stats", "outage", "multipath", "spoof"))
    ap.add_argument("--data", default=os.path.join(HERE, "data", "2013-01-10"))
    args = ap.parse_args()
    if not os.path.exists(os.path.join(args.data, "groundtruth.csv")):
        sys.exit(f"no data in {args.data}; run: python3 fetch_nclt.py")
    s = nclt_io.Session(args.data)
    for name, fn in (("stats", report_stats), ("outage", report_outage),
                     ("multipath", report_multipath), ("spoof", report_spoof)):
        if args.what in ("all", name):
            print(f"== {name}")
            fn(s)
            print()


if __name__ == "__main__":
    main()
