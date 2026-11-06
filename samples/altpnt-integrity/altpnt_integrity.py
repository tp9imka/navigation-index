"""Integrity monitoring for alternative PNT: EKF + innovation gating + solution-separation
FDE + protection levels + alert logic, on a simulated GNSS-denied UAV flight.

Sources: INS (accelerometer, propagation), VIO-like velocity (relative), visual
geolocalization fixes (absolute, intermittent, with failure modes), GNSS (jammed, then
spoofed). Stdlib only.

    python3 altpnt_integrity.py                       # compare monitor modes, seed 1
    python3 altpnt_integrity.py --csv out.csv --svg stanford.svg
    python3 altpnt_integrity.py --runs 20             # Monte Carlo over seeds
"""

import argparse
import copy
import csv
import math
import random
from collections import deque
from statistics import NormalDist

import mat
import stanford

DT_IMU = 0.1
IMU_PER_EPOCH = 10
EPOCH = 1.0
SPEED = 30.0

CHI2_2DOF_999 = 13.816
ALERT_LIMIT = 50.0
P_FA = 1e-5          # false-alert budget per epoch, split across monitored subsets
P_MD = 1e-3          # missed-detection probability allocated per fault hypothesis
IR_FF = 1e-7         # fault-free integrity risk
EXCLUSION_HOLD = 30.0
PROBATION_PASSES = 5
PROBATION_TIME = 45.0
LOOKBACK = 30.0
ACTIVE_WINDOW = 30.0
SIGMA_D_FLOOR = 0.5
TTA_REQUIREMENT = 10.0

ACC_NOISE = 0.05
ACC_BIAS_TRUE = (0.03, -0.02)
Q_VEL = 0.01
Q_ACC_BIAS = 1e-8
VIO_SCALE_ERR = 0.005
VIO_YAW_ERR = 0.004
VIO_WHITE = 0.08
VIO_WHITE_WATER = 0.4
VIO_R = 0.1
VIO_R_WATER = 0.5
VIO_GM_SIGMA = 0.3
VIO_GM_TAU = 300.0
GNSS_WHITE = 2.0
GNSS_R = 2.5
VGEO_PERIOD = 5
VGEO_WHITE = 5.0
VGEO_R = 8.0
OUTLIER_PROB = 0.3
OUTLIER_RANGE = (60.0, 250.0)
DROPOUT_PROB = 0.15
MAGNAV_PERIOD = 10
MAGNAV_WHITE = 20.0
MAGNAV_R = 25.0


class Scenario:
    def __init__(self, duration=600, gnss=True, faults=True, magnav=False,
                 jam=(150, 330), spoof_onset=420, spoof_rate=1.5, spoof_dir_deg=60.0,
                 texture_zones=((60, 200), (450, 540)), water=(200, 290),
                 misreg=(300, 380), misreg_offset=(25.0, -25.0)):
        self.duration = duration
        self.gnss = gnss
        self.magnav = magnav
        self.faults = faults
        self.jam = jam
        self.spoof_onset = spoof_onset
        self.spoof_rate = spoof_rate
        self.spoof_dir = math.radians(spoof_dir_deg)
        self.texture_zones = texture_zones
        self.water = water
        self.misreg = misreg
        self.misreg_offset = misreg_offset

    @staticmethod
    def _in(t, span):
        return span is not None and span[0] <= t < span[1]

    def gnss_state(self, t):
        if not self.gnss:
            return "off"
        if self.faults and self._in(t, self.jam):
            return "jammed"
        if self.faults and self.spoof_onset is not None and t >= self.spoof_onset:
            return "spoofed"
        return "ok"

    def over_water(self, t):
        return self.faults and self._in(t, self.water)

    def textured(self, t):
        return self.faults and any(self._in(t, z) for z in self.texture_zones)

    def misregistered(self, t):
        return self.faults and self._in(t, self.misreg)


def truth_heading(t):
    w = 2 * math.pi / 120.0
    return 0.3 * math.sin(w * t) + 0.002 * t, 0.3 * w * math.cos(w * t) + 0.002


def simulate(sc, seed):
    """Truth and all sensor data, generated once so every monitor mode sees the same draw."""
    rng = random.Random(seed)
    px, py = 0.0, 0.0
    t = 0.0
    psi, _ = truth_heading(0.0)
    truth = [(0.0, px, py, SPEED * math.cos(psi), SPEED * math.sin(psi))]
    epochs = []
    bax, bay = ACC_BIAS_TRUE
    for k in range(1, sc.duration + 1):
        imu = []
        for _ in range(IMU_PER_EPOCH):
            psi, psid = truth_heading(t)
            vx0, vy0 = SPEED * math.cos(psi), SPEED * math.sin(psi)
            ax, ay = -SPEED * psid * math.sin(psi), SPEED * psid * math.cos(psi)
            imu.append((ax + bax + rng.gauss(0, ACC_NOISE), ay + bay + rng.gauss(0, ACC_NOISE)))
            t += DT_IMU
            psi1, _ = truth_heading(t)
            vx1, vy1 = SPEED * math.cos(psi1), SPEED * math.sin(psi1)
            px += 0.5 * (vx0 + vx1) * DT_IMU
            py += 0.5 * (vy0 + vy1) * DT_IMU
        t = float(k)
        psi, _ = truth_heading(t)
        vx, vy = SPEED * math.cos(psi), SPEED * math.sin(psi)
        truth.append((t, px, py, vx, vy))

        water = sc.over_water(t)
        w = VIO_WHITE_WATER if water else VIO_WHITE
        ex = VIO_SCALE_ERR * vx - VIO_YAW_ERR * vy + rng.gauss(0, w)
        ey = VIO_SCALE_ERR * vy + VIO_YAW_ERR * vx + rng.gauss(0, w)
        vio = ((vx + ex, vy + ey), VIO_R_WATER if water else VIO_R)

        gs = sc.gnss_state(t)
        gnss = None
        if gs in ("ok", "spoofed"):
            gx, gy = px + rng.gauss(0, GNSS_WHITE), py + rng.gauss(0, GNSS_WHITE)
            if gs == "spoofed":
                off = sc.spoof_rate * (t - sc.spoof_onset)
                gx += off * math.cos(sc.spoof_dir)
                gy += off * math.sin(sc.spoof_dir)
            gnss = (gx, gy)

        vgeo, vs = None, "none"
        if k % VGEO_PERIOD == 0:
            u_drop, u_out = rng.random(), rng.random()
            mag, ang = rng.uniform(*OUTLIER_RANGE), rng.uniform(0, 2 * math.pi)
            nx, ny = rng.gauss(0, VGEO_WHITE), rng.gauss(0, VGEO_WHITE)
            if water:
                vs = "water"
            elif sc.faults and u_drop < DROPOUT_PROB:
                vs = "dropout"
            else:
                vx_, vy_ = px + nx, py + ny
                vs = "ok"
                if sc.misregistered(t):
                    vx_ += sc.misreg_offset[0]
                    vy_ += sc.misreg_offset[1]
                    vs = "misreg"
                if sc.textured(t) and u_out < OUTLIER_PROB:
                    vx_ += mag * math.cos(ang)
                    vy_ += mag * math.sin(ang)
                    vs = "outlier"
                vgeo = (vx_, vy_)
        mx, my = rng.gauss(0, MAGNAV_WHITE), rng.gauss(0, MAGNAV_WHITE)
        magnav = (px + mx, py + my) if sc.magnav and k % MAGNAV_PERIOD == 0 else None
        epochs.append({"t": t, "imu": imu, "vio": vio, "gnss": gnss, "gnss_state": gs,
                       "vgeo": vgeo, "vgeo_state": vs, "magnav": magnav})
    return truth, epochs


H_POS = [[1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0]]
H_VIO = [[0, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 1, 0, 0, 0, 1]]


def _transition():
    phi = math.exp(-EPOCH / VIO_GM_TAU)
    F = mat.eye(8)
    for i in range(2):
        F[i][2 + i] = EPOCH
        F[i][4 + i] = -0.5 * EPOCH ** 2
        F[2 + i][4 + i] = -EPOCH
        F[6 + i][6 + i] = phi
    Q = mat.zeros(8, 8)
    for i in range(2):
        Q[i][i] = Q_VEL * EPOCH ** 3 / 3
        Q[i][2 + i] = Q[2 + i][i] = Q_VEL * EPOCH ** 2 / 2
        Q[2 + i][2 + i] = Q_VEL * EPOCH
        Q[4 + i][4 + i] = Q_ACC_BIAS * EPOCH
        Q[6 + i][6 + i] = VIO_GM_SIGMA ** 2 * (1 - phi * phi)
    return F, Q


F_EPOCH, Q_EPOCH = _transition()


class Ekf:
    """State [px, py, vx, vy, bax, bay, bvx, bvy]: 2D INS error model + VIO velocity bias."""

    def __init__(self, x, P, excludes=None):
        self.x = list(x)
        self.P = [row[:] for row in P]
        self.excludes = excludes

    def clone(self, excludes):
        e = copy.deepcopy(self)
        e.excludes = excludes
        return e

    def predict(self, imu):
        x = self.x
        decay = math.exp(-DT_IMU / VIO_GM_TAU)
        for amx, amy in imu:
            ax, ay = amx - x[4], amy - x[5]
            x[0] += x[2] * DT_IMU + 0.5 * ax * DT_IMU ** 2
            x[1] += x[3] * DT_IMU + 0.5 * ay * DT_IMU ** 2
            x[2] += ax * DT_IMU
            x[3] += ay * DT_IMU
            x[6] *= decay
            x[7] *= decay
        self.P = mat.sym(mat.add(mat.mul(mat.mul(F_EPOCH, self.P), mat.T(F_EPOCH)), Q_EPOCH))

    def innovation(self, H, z, r):
        y = [z[i] - sum(H[i][j] * self.x[j] for j in range(8)) for i in range(2)]
        S = mat.add(mat.mul(mat.mul(H, self.P), mat.T(H)), [[r * r, 0.0], [0.0, r * r]])
        Si = mat.inv2(S)
        nis = sum(y[i] * Si[i][j] * y[j] for i in range(2) for j in range(2))
        return y, Si, nis

    def update(self, H, z, r, gate):
        y, Si, nis = self.innovation(H, z, r)
        if gate and nis > CHI2_2DOF_999:
            return nis, False
        K = mat.mul(mat.mul(self.P, mat.T(H)), Si)
        dx = mat.mv(K, y)
        self.x = [a + b for a, b in zip(self.x, dx)]
        IKH = mat.sub(mat.eye(8), mat.mul(K, H))
        self.P = mat.sym(mat.mul(IKH, self.P))
        return nis, True

    def pos_cov(self):
        return [[self.P[0][0], self.P[0][1]], [self.P[1][0], self.P[1][1]]]


def q_inv(p):
    """Upper-tail standard-normal quantile: Q^-1(p)."""
    return NormalDist().inv_cdf(1.0 - p)


MEAS = {"gnss": (H_POS, GNSS_R), "vgeo": (H_POS, VGEO_R), "magnav": (H_POS, MAGNAV_R)}


def _fuse(f, src, ep, gate):
    if src == "vio":
        z, r = ep["vio"]
        return f.update(H_VIO, z, r, gate)
    H, r = MEAS[src]
    return f.update(H, ep[src], r, gate)


def _available_sources(ep):
    out = ["vio"]
    if ep["gnss"] is not None:
        out.append("gnss")
    for s in ("vgeo", "magnav"):
        if ep[s] is not None:
            out.append(s)
    return out


def monitored_sources(sc):
    return ("gnss", "vgeo", "magnav") if sc.magnav else ("gnss", "vgeo")


def run(sc, seed, mode="full", monitored=None, alert_limit=ALERT_LIMIT, data=None):
    """mode: 'none' (no gate, no FDE), 'gate' (chi-square gate only), 'full' (gate + SS FDE).

    VIO is not a monitored fault hypothesis: its correlated error is overbounded by the
    Gauss-Markov bias state instead (see README).
    """
    monitored = monitored or monitored_sources(sc)
    truth, epochs = data if data is not None else simulate(sc, seed)
    rng = random.Random(seed + 10_000)
    t0 = truth[0]
    x0 = [t0[1] + rng.gauss(0, 3), t0[2] + rng.gauss(0, 3),
          t0[3] + rng.gauss(0, 0.3), t0[4] + rng.gauss(0, 0.3), 0, 0, 0, 0]
    P0 = mat.zeros(8, 8)
    for i, s in enumerate([3, 3, 0.3, 0.3, 0.05, 0.05, VIO_GM_SIGMA, VIO_GM_SIGMA]):
        P0[i][i] = s * s
    mon = Monitor(Ekf(x0, P0), monitored if mode == "full" else (), gate=mode != "none")
    rows = []
    for ep, tr in zip(epochs, truth[1:]):
        hpl, events = mon.step(ep)
        x = mon.main.x
        hpe = math.hypot(x[0] - tr[1], x[1] - tr[2])
        available = hpl < alert_limit and not mon.ambiguous
        rows.append({
            "t": ep["t"], "true_x": tr[1], "true_y": tr[2], "est_x": x[0], "est_y": x[1],
            "hpe": hpe, "hpl": hpl, "available": available,
            "region": stanford.classify(hpe, hpl if available else max(hpl, alert_limit), alert_limit),
            "alert": mon.ambiguous,
            "gnss_state": ep["gnss_state"], "vgeo_state": ep["vgeo_state"],
            "excluded": "+".join(sorted(mon.excluded)), "events": " ".join(events),
        })
    return rows


class Monitor:
    """Bank of filters for solution separation: main fuses every admitted source, branch s
    excludes monitored source s.

    Detection with one or three-plus active monitored sources => exclude the source whose
    branch separates most (normalised). With exactly two, each branch keeps one of them, so
    the fault is detectable but not identifiable: raise an alert, drop both, rewind main to a
    snapshot LOOKBACK seconds old and replay it on INS + VIO only, then re-admit whichever
    source stays consistent with that dead-reckoning solution through probation."""

    def __init__(self, main, monitored, gate):
        self.main = main
        self.gate = gate
        self.monitored = tuple(monitored)
        self.subs = {s: main.clone(s) for s in self.monitored}
        self.excluded = {}
        self.ambiguous = False
        self.k_md = q_inv(P_MD)
        self.k_ff = q_inv(IR_FF / 2)
        self.history = deque(maxlen=int(LOOKBACK / EPOCH) + 1)
        self.last_fused = {}
        self.post_exclusion = (-math.inf, 0.0)
        self.t = 0.0

    def _k_fa(self):
        return q_inv(P_FA / (2 * max(len(self.subs), 1)))

    def _exclude(self, s, t):
        self.excluded[s] = {"t": t, "streak": None}

    def _probation(self, src, ep, t):
        """Excluded source: test its fix against main without fusing it. Two consecutive
        failures restart the streak; a single one (an isolated outlier) does not."""
        ex = self.excluded[src]
        _, _, nis = self.main.innovation(H_POS, ep[src], MEAS[src][1])
        if ex["streak"] is None:
            ex["streak"] = {"start": t, "passes": 0, "fails": 0}
        st = ex["streak"]
        if nis <= CHI2_2DOF_999:
            st["passes"] += 1
            st["fails"] = 0
        else:
            st["fails"] += 1
            if st["fails"] >= 2 or st["passes"] == 0:
                ex["streak"] = None

    def _readmit(self, t, events):
        for s, ex in list(self.excluded.items()):
            st = ex["streak"]
            if (t - ex["t"] >= EXCLUSION_HOLD and st and t - st["start"] >= PROBATION_TIME
                    and st["passes"] >= PROBATION_PASSES):
                del self.excluded[s]
                events.append(f"readmit:{s}")
                for other in self.excluded.values():
                    other["streak"] = None
                if self.ambiguous:
                    self.ambiguous = False
                    self.subs = {k: self.main.clone(k) for k in self.monitored if k not in self.excluded}
                    for k in self.excluded:
                        events.append(f"blame:{k}")
                elif s in self.monitored:
                    self.subs[s] = self.main.clone(s)

    def step(self, ep):
        t = self.t = ep["t"]
        events = []
        for f in [self.main, *self.subs.values()]:
            f.predict(ep["imu"])
        for src in _available_sources(ep):
            if src in self.excluded:
                self._probation(src, ep, t)
                continue
            _, ok = _fuse(self.main, src, ep, self.gate)
            if ok:
                self.last_fused[src] = t
            else:
                events.append(f"gate:{src}")
            for s, f in self.subs.items():
                if s != src:
                    _fuse(f, src, ep, self.gate)
        if self.subs and not self.ambiguous:
            self._detect(t, ep, events)
        self._readmit(t, events)
        self.history.append((self.main.clone(None), ep))
        return self._hpl(), events

    def _separations(self):
        k_fa = self._k_fa()
        out = {}
        for s, f in self.subs.items():
            d = math.hypot(self.main.x[0] - f.x[0], self.main.x[1] - f.x[1])
            pd = mat.sub(f.pos_cov(), self.main.pos_cov())
            sig_d = max(math.sqrt(max(mat.lmax2(pd), 0.0)), SIGMA_D_FLOOR)
            out[s] = (d, k_fa * sig_d, math.sqrt(mat.lmax2(f.pos_cov())))
        return out

    def _detect(self, t, ep, events):
        sep = self._separations()
        tripped = {s: d / thr for s, (d, thr, _) in sep.items() if d > thr}
        if not tripped:
            return
        # Only sources fused recently can be the cause; a jammed GNSS branch equals main.
        active = [s for s in self.subs if t - self.last_fused.get(s, -math.inf) <= ACTIVE_WINDOW]
        if len(active) == 2:
            events.append("alert:ambiguous")
            for s in active:
                self._exclude(s, t)
            self.ambiguous = True
            self.subs = {}
            self._rewind(ep)
            return
        candidates = {s: r for s, r in tripped.items() if s in active} or tripped
        worst = max(candidates, key=candidates.get)
        events.append(f"exclude:{worst}")
        self._exclude(worst, t)
        base = self.subs[worst]
        # A wrong exclusion leaves main on a faulty branch while the rebuilt bank starts at
        # zero separation; keep the spread between candidate branches in the PL meanwhile.
        spread = max([math.hypot(f.x[0] - base.x[0], f.x[1] - base.x[1])
                      for s, f in self.subs.items() if s != worst] or [0.0])
        self.post_exclusion = (t + LOOKBACK, spread)
        self.main = base.clone(None)
        self.subs = {s: base.clone(s) for s in self.monitored if s not in self.excluded}

    def _rewind(self, cur):
        if not self.history:
            return
        snap, _ = self.history[0]
        f = snap.clone(None)
        for ep in (*[e for _, e in list(self.history)[1:]], cur):
            f.predict(ep["imu"])
            _fuse(f, "vio", ep, self.gate)
        self.main = f

    def _hpl(self):
        terms = [self.k_ff * math.sqrt(mat.lmax2(self.main.pos_cov()))]
        for _, thr, sig in self._separations().values():
            terms.append(thr + self.k_md * sig)
        until, spread = self.post_exclusion
        if self.t <= until:
            terms.append(spread + self.k_md * math.sqrt(mat.lmax2(self.main.pos_cov())))
        return max(terms)


def hazard_episodes(rows, alert_limit=ALERT_LIMIT):
    """Contiguous runs with HPE >= AL. TTA = time from run start until the system is unavailable."""
    out, i = [], 0
    while i < len(rows):
        if rows[i]["hpe"] < alert_limit:
            i += 1
            continue
        j = i
        while j < len(rows) and rows[j]["hpe"] >= alert_limit:
            j += 1
        start = rows[i]["t"]
        alert_t = next((r["t"] for r in rows[i:j] if not r["available"]), None)
        out.append({"start": start, "end": rows[j - 1]["t"],
                    "tta": None if alert_t is None else alert_t - start})
        i = j
    return out


def _events(rows, prefix):
    return [(r["t"], ev.split(":", 1)[1]) for r in rows for ev in r["events"].split() if ev.startswith(prefix)]


def _faulty(r, src):
    return ((src == "gnss" and r["gnss_state"] == "spoofed") or
            (src == "vgeo" and r["vgeo_state"] in ("outlier", "misreg")))


def _latency(events, src, onset, end=None):
    """Seconds from fault onset to the first event naming src (or any detection alert)."""
    for t, s in events:
        if t >= onset and (end is None or t < end + LOOKBACK) and s in (src, "ambiguous"):
            return t - onset
    return None


def summarize(rows, sc, alert_limit=ALERT_LIMIT):
    n = len(rows)
    hpes = sorted(r["hpe"] for r in rows)
    regions = stanford.tally(rows)
    eps = hazard_episodes(rows, alert_limit)
    ttas = [e["tta"] for e in eps if e["tta"] is not None]
    detections = _events(rows, "exclude:") + _events(rows, "alert:")
    detections.sort()
    attributions = sorted(_events(rows, "exclude:") + _events(rows, "blame:"))
    wrong = 0
    for t, src in attributions:
        window = [r for r in rows if t - 2 * LOOKBACK - PROBATION_TIME <= r["t"] <= t]
        wrong += 0 if any(_faulty(r, src) for r in window) else 1
    mi_cause = {}
    for r in rows:
        if r["region"] in ("MI", "HMI", "unavail_MI"):
            t = r["t"]
            key = "gnss " + r["gnss_state"] + "".join(
                f", {name}" for name, on in (("texture zone", sc.textured(t)), ("over water", sc.over_water(t)),
                                             ("map misregistered", sc.misregistered(t))) if on)
            mi_cause[key] = mi_cause.get(key, 0) + 1
    spoof = sc.gnss and sc.faults and sc.spoof_onset is not None
    misreg = sc.faults and sc.misreg is not None
    return {
        "epochs": n,
        "hpe_rms": math.sqrt(sum(h * h for h in hpes) / n),
        "hpe_p95": hpes[int(0.95 * (n - 1))],
        "hpe_max": hpes[-1],
        "hpl_median": sorted(r["hpl"] for r in rows)[n // 2],
        "availability": sum(r["available"] for r in rows) / n,
        "regions": regions,
        "mi": regions["MI"] + regions["HMI"] + regions["unavail_MI"],
        "hmi": regions["HMI"],
        "hazard_episodes": len(eps),
        "missed_hazards": sum(1 for e in eps if e["tta"] is None),
        "tta_max": max(ttas) if ttas else None,
        "tta_over_req": sum(1 for x in ttas if x > TTA_REQUIREMENT),
        "detections": detections,
        "attributions": attributions,
        "wrong_attributions": wrong,
        "spoof_detected_after": _latency(detections, "gnss", sc.spoof_onset) if spoof else None,
        "spoof_attributed_after": _latency(attributions, "gnss", sc.spoof_onset) if spoof else None,
        "misreg_detected_after": _latency(detections, "vgeo", sc.misreg[0], sc.misreg[1]) if misreg else None,
        "misreg_attributed_after": _latency(attributions, "vgeo", sc.misreg[0], sc.misreg[1]) if misreg else None,
        "mi_cause": mi_cause,
    }


def write_csv(path, rows_by_mode):
    keys = ["mode", "t", "true_x", "true_y", "est_x", "est_y", "hpe", "hpl", "available",
            "region", "gnss_state", "vgeo_state", "excluded", "events"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for mode, rows in rows_by_mode.items():
            for r in rows:
                out = {k: r[k] for k in keys if k != "mode"}
                for k in ("true_x", "true_y", "est_x", "est_y", "hpe", "hpl"):
                    out[k] = f"{r[k]:.2f}"
                w.writerow({"mode": mode, **out})


def _fmt(v, nd=1):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def print_report(sums, sc, seed, alert_limit):
    print(f"seed={seed} duration={sc.duration}s AL={alert_limit:.0f} m  gnss={'on' if sc.gnss else 'off'} "
          f"faults={'on' if sc.faults else 'off'} magnav={'on' if sc.magnav else 'off'}")
    print(f"P_FA={P_FA:g}/epoch  P_MD={P_MD:g}  IR_ff={IR_FF:g}  gate=chi2(2) {CHI2_2DOF_999}")
    cols = list(sums)
    lines = [
        ("HPE rms / p95 / max [m]", lambda s: f"{s['hpe_rms']:.1f} / {s['hpe_p95']:.1f} / {s['hpe_max']:.1f}"),
        ("HPL median [m]", lambda s: f"{s['hpl_median']:.1f}"),
        ("availability (HPL<AL)", lambda s: f"{100 * s['availability']:.1f} %"),
        ("nominal epochs", lambda s: str(s["regions"]["nominal"])),
        ("unavailable epochs", lambda s: str(s["regions"]["unavailable"])),
        ("MI epochs (PE>PL, PL<AL)", lambda s: str(s["regions"]["MI"])),
        ("HMI epochs (PE>AL, PL<AL)", lambda s: str(s["regions"]["HMI"])),
        ("unavail+MI (PE>PL>=AL)", lambda s: str(s["regions"]["unavail_MI"])),
        ("hazard episodes (PE>=AL)", lambda s: str(s["hazard_episodes"])),
        ("  missed (no alert)", lambda s: str(s["missed_hazards"])),
        (f"  max TTA [s] / >{TTA_REQUIREMENT:.0f}s", lambda s: f"{_fmt(s['tta_max'], 0)} / {s['tta_over_req']}"),
        ("detections / attributions", lambda s: f"{len(s['detections'])} / {len(s['attributions'])}"),
        ("  wrong attributions", lambda s: str(s["wrong_attributions"])),
        ("spoof detect / blame [s]", lambda s: f"{_fmt(s['spoof_detected_after'], 0)} / {_fmt(s['spoof_attributed_after'], 0)}"),
        ("misreg detect / blame [s]", lambda s: f"{_fmt(s['misreg_detected_after'], 0)} / {_fmt(s['misreg_attributed_after'], 0)}"),
    ]
    print(f"{'':28}" + "".join(f"{c:>22}" for c in cols))
    for label, fn in lines:
        print(f"{label:28}" + "".join(f"{fn(sums[c]):>22}" for c in cols))


def monte_carlo(sc, runs, alert_limit):
    agg = {m: {"epochs": 0, "mi": 0, "hmi": 0, "avail": 0.0, "missed": 0, "false_excl": 0}
           for m in ("none", "gate", "full")}
    for seed in range(1, runs + 1):
        data = simulate(sc, seed)
        for m in agg:
            s = summarize(run(sc, seed, m, alert_limit=alert_limit, data=data), sc, alert_limit)
            a = agg[m]
            a["epochs"] += s["epochs"]
            a["mi"] += s["mi"]
            a["hmi"] += s["hmi"]
            a["avail"] += s["availability"] * s["epochs"]
            a["missed"] += s["missed_hazards"]
            a["false_excl"] += s["wrong_attributions"]
    print(f"Monte Carlo: {runs} seeds x {sc.duration} epochs, AL={alert_limit:.0f} m, "
          f"gnss={'on' if sc.gnss else 'off'} faults={'on' if sc.faults else 'off'} "
          f"magnav={'on' if sc.magnav else 'off'} spoof_rate={sc.spoof_rate}  (MI* = MI + HMI + unavail_MI)")
    print(f"{'mode':6}{'epochs':>8}{'avail %':>9}{'MI*':>6}{'HMI':>6}{'missed hazards':>16}{'wrong blame':>12}")
    for m, a in agg.items():
        print(f"{m:6}{a['epochs']:>8}{100 * a['avail'] / a['epochs']:>9.1f}{a['mi']:>6}{a['hmi']:>6}"
              f"{a['missed']:>16}{a['false_excl']:>12}")


def al_sweep(sc, seed, limits=(25, 50, 75, 100, 150, 250)):
    data = simulate(sc, seed)
    rows = {m: run(sc, seed, m, data=data) for m in ("none", "gate", "full")}
    print(f"seed={seed} magnav={'on' if sc.magnav else 'off'}: availability % / MI / HMI epochs vs alert limit")
    print(f"{'AL [m]':>7}" + "".join(f"{m:>20}" for m in rows))
    for al in limits:
        cells = []
        for m, rs in rows.items():
            ok = [r["hpl"] < al and not r["alert"] for r in rs]
            reg = [stanford.classify(r["hpe"], r["hpl"] if a else max(r["hpl"], al), al) for r, a in zip(rs, ok)]
            av = 100 * sum(ok) / len(rs)
            cells.append(f"{av:5.1f} / {reg.count('MI'):3d} / {reg.count('HMI'):3d}")
        print(f"{al:>7}" + "".join(f"{c:>20}" for c in cells))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--no-gnss", action="store_true", help="alt-PNT only, GNSS never present")
    ap.add_argument("--no-faults", action="store_true", help="nominal run, no failure modes")
    ap.add_argument("--spoof-rate", type=float, default=1.5)
    ap.add_argument("--alert-limit", type=float, default=ALERT_LIMIT)
    ap.add_argument("--magnav", action="store_true", help="add a coarse absolute MagNav-like fix every 10 s")
    ap.add_argument("--al-sweep", action="store_true", help="availability / MI / HMI vs alert limit")
    ap.add_argument("--runs", type=int, default=0, help="Monte Carlo over seeds 1..N instead")
    ap.add_argument("--csv", help="write per-epoch CSV for all modes")
    ap.add_argument("--svg", help="write Stanford diagram SVG for the full monitor")
    ap.add_argument("--no-ascii", action="store_true")
    a = ap.parse_args(argv)
    sc = Scenario(gnss=not a.no_gnss, faults=not a.no_faults, spoof_rate=a.spoof_rate, magnav=a.magnav)
    if a.runs:
        monte_carlo(sc, a.runs, a.alert_limit)
        return
    if a.al_sweep:
        al_sweep(sc, a.seed)
        return
    data = simulate(sc, a.seed)
    rows = {m: run(sc, a.seed, m, alert_limit=a.alert_limit, data=data) for m in ("none", "gate", "full")}
    sums = {m: summarize(r, sc, a.alert_limit) for m, r in rows.items()}
    print_report(sums, sc, a.seed, a.alert_limit)
    log = sorted(_events(rows["full"], "alert:") + _events(rows["full"], "exclude:") +
                 [(t, "blame " + x) for t, x in _events(rows["full"], "blame:")] +
                 [(t, "readmit " + x) for t, x in _events(rows["full"], "readmit:")])
    print("\nmonitor log (full):", ", ".join(f"{t:.0f}s {x}" for t, x in log) or "none")
    for m in ("none", "full"):
        print(f"MI/HMI epochs by condition ({m}):", sums[m]["mi_cause"] or "none")
    if not a.no_ascii:
        for m in ("none", "full"):
            print(f"\nStanford diagram, mode={m}")
            print(stanford.ascii_diagram(rows[m], a.alert_limit))
    if a.csv:
        write_csv(a.csv, rows)
        print(f"\nwrote {a.csv}")
    if a.svg:
        stanford.write_svg(a.svg, rows["full"], a.alert_limit, title=f"full monitor, seed {a.seed}")
        print(f"wrote {a.svg}")


if __name__ == "__main__":
    main()
