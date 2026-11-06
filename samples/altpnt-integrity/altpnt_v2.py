"""altpnt-integrity v2: the same flight and monitor, with error models measured in sibling
samples (calibration.json) instead of assumed ones, plus the filter changes they call for.

    python3 altpnt_v2.py                  # seed 1: v1 vs v2 filter in the assumed and measured worlds
    python3 altpnt_v2.py --runs 20        # Monte Carlo matrix, writes results/v2_mc.json
    python3 altpnt_v2.py --runs 20 --quick   # headline rows only

v1 (altpnt_integrity.py) is untouched and still reproduces its README. Stdlib only.
"""

import argparse
import copy
import json
import math
import os
import random
from statistics import NormalDist

import altpnt_integrity as v1
import mat
import stanford

HERE = os.path.dirname(os.path.abspath(__file__))
CAL_PATH = os.path.join(HERE, "calibration.json")

GM_TAU = 300.0              # correlation time of heading / scale error: assumed, as v1's VIO bias
WATER_WHITE_RATIO = v1.VIO_WHITE_WATER / v1.VIO_WHITE
TRN_PERIOD = 10
TRN_SEGMENT_S = 60          # terrain (and so TRN spread) held constant per segment: assumed
TRN_FAULT_SCALE = (3.0, 6.0)  # a TRN fault puts the fix this many spreads off
IR_FAULT = 1e-5             # per-epoch integrity budget for faulted hypotheses (illustrative)
GNSS_FAULT_PRIOR = 1e-2     # per epoch in a contested area: assumed, nothing measured it
STRESS_AVAILABILITY = 0.2   # geoloc-license-clean: best real-frame config fixed 1 of 5
TRN_REGIONS = ("hilly", "mixed", "flat", "flat_smooth")


def load_cal(path=CAL_PATH):
    with open(path) as fh:
        return json.load(fh)


class World:
    """Truth error models for the relative source, visual geoloc and TRN."""

    def __init__(self, name, measured, relative=None, trn=False, stress=False, gnss=True, cal=None):
        self.name, self.measured, self.trn, self.stress, self.gnss = name, measured, trn, stress, gnss
        self.relative = relative
        if not measured:
            return
        cal = cal or load_cal()
        r = cal["relative"]["models"][relative]
        f, w = r["fit_whole_run"], r["per_window"]
        self.yaw0 = f["yaw_err_rad"]
        self.scale0 = f["scale_err"]
        self.yaw_sigma = math.radians(w["yaw_abs_max_deg"])
        self.scale_sigma = w["scale_std_pct"] / 100
        self.white = f["white_frac_of_speed"] * v1.SPEED
        g = cal["geoloc"]
        t = g["golden_table"]
        self.residuals = t["residuals_e_n_m"]
        self.vgeo_avail = t["availability"]
        self.fix_run_s, self.gap_run_s = t["fix_run_s_at_30mps_mean"], t["outage_run_s_at_30mps_mean"]
        self.outlier_rate = g["wrong_fix"]["rate_upper_95"]
        self.stress_bias = max(g["real_frames"]["fix_errors_m"] or [0.0])
        tr = cal["trn"]
        self.trn_ln = (tr["spread_lognormal"]["mu_ln_m"], tr["spread_lognormal"]["sigma_ln"])
        self.trn_infl = tr["sigma_per_axis_over_spread_div_sqrt2"]
        self.trn_applied = tr["applied_frac"]
        self.trn_fault = tr["fault_rate_upper_95"]


def worlds(cal=None):
    cal = cal or load_cal()
    return {
        "assumed": World("assumed (v1)", False),
        "assumed-nognss": World("assumed (v1), GNSS off", False, gnss=False),
        "measured-nognss": World("measured, GNSS off", True, "openvins-uzhfpv", gnss=False, cal=cal),
        "measured": World("measured: OpenVINS + real geoloc", True, "openvins-uzhfpv", cal=cal),
        "measured+trn": World("measured + TRN", True, "openvins-uzhfpv", trn=True, cal=cal),
        "measured-kiss": World("measured: KISS-ICP + real geoloc", True, "kiss-icp-kitti04", cal=cal),
        "measured-vpair": World("measured: nadir VO + real geoloc", True, "nadir-vo-vpair", cal=cal),
        "stress": World("measured, map-age stress", True, "openvins-uzhfpv", stress=True, cal=cal),
    }


def scenario(world, **kw):
    """v1 Scenario; the TRN source rides in v1's 'magnav' slot so v1 code can consume it unchanged."""
    return v1.Scenario(magnav=world.trn, gnss=world.gnss, **kw)


def simulate(sc, seed, world):
    """v1 truth, IMU and GNSS (same draw per seed); VIO, vgeo and TRN replaced in measured worlds."""
    truth, epochs = v1.simulate(sc, seed)
    if not world.measured:
        return truth, epochs
    rng = random.Random(seed + 20_000)
    sign = rng.choice((-1.0, 1.0))
    yaw, scale = sign * world.yaw0, rng.choice((-1.0, 1.0)) * world.scale0
    phi = math.exp(-v1.EPOCH / GM_TAU)
    rot = rng.uniform(0, 2 * math.pi)        # registration offset of a different map tile
    c, s = math.cos(rot), math.sin(rot)
    res = [(c * a - s * b, s * a + c * b) for a, b in world.residuals]
    stress_b = (world.stress_bias * math.cos(rot + 1.0), world.stress_bias * math.sin(rot + 1.0))
    avail = STRESS_AVAILABILITY if world.stress else world.vgeo_avail
    # Two-state Markov chain for fix availability: mean run lengths from the golden table grid.
    p_lose = 1.0 / max(world.fix_run_s / v1.VGEO_PERIOD, 1.0)
    p_gain = p_lose * avail / (1.0 - avail)
    have = rng.random() < avail
    trn_spread, trn_infl = None, None
    for k, (ep, tr) in enumerate(zip(epochs, truth[1:]), start=1):
        t, vx, vy = tr[0], tr[3], tr[4]
        yaw = yaw * phi + rng.gauss(0, world.yaw_sigma * math.sqrt(1 - phi * phi))
        scale = scale * phi + rng.gauss(0, world.scale_sigma * math.sqrt(1 - phi * phi))
        water = sc.over_water(t)
        w = world.white * (WATER_WHITE_RATIO if water else 1.0)
        cy, sy = math.cos(yaw), math.sin(yaw)
        mvx = (1 + scale) * (cy * vx - sy * vy) + rng.gauss(0, w)
        mvy = (1 + scale) * (sy * vx + cy * vy) + rng.gauss(0, w)
        ep["vio"] = ((mvx, mvy), v1.VIO_R_WATER if water else v1.VIO_R)
        ep["vio_white_water"] = water

        vgeo, vs = None, "none"
        if k % v1.VGEO_PERIOD == 0:
            have = (rng.random() >= p_lose) if have else (rng.random() < p_gain)
            u_out, u_tail = rng.random(), rng.random()
            mag, ang = rng.uniform(*v1.OUTLIER_RANGE), rng.uniform(0, 2 * math.pi)
            ex, ey = res[rng.randrange(len(res))]
            if water:
                vs = "water"
            elif not have:
                vs = "dropout"
            else:
                gx, gy = tr[1] + ex, tr[2] + ey
                if world.stress:
                    gx, gy = gx + stress_b[0], gy + stress_b[1]
                vs = "ok"
                if sc.misregistered(t):
                    gx, gy = gx + sc.misreg_offset[0], gy + sc.misreg_offset[1]
                    vs = "misreg"
                if (sc.textured(t) and u_out < v1.OUTLIER_PROB) or u_tail < world.outlier_rate:
                    gx, gy = gx + mag * math.cos(ang), gy + mag * math.sin(ang)
                    vs = "outlier"
                vgeo = (gx, gy)
        ep["vgeo"], ep["vgeo_state"] = vgeo, vs

        if world.trn and (k - 1) % TRN_SEGMENT_S == 0:
            trn_spread = math.exp(rng.gauss(*world.trn_ln))
            trn_infl = world.trn_infl[rng.choice(TRN_REGIONS)]
        trn = None
        if world.trn and k % TRN_PERIOD == 0 and rng.random() < world.trn_applied:
            sig = trn_infl * trn_spread / math.sqrt(2)
            ex, ey = rng.gauss(0, sig), rng.gauss(0, sig)
            if rng.random() < world.trn_fault:
                m, a = rng.uniform(*TRN_FAULT_SCALE) * trn_spread, rng.uniform(0, 2 * math.pi)
                ex, ey = m * math.cos(a), m * math.sin(a)
            trn = (tr[1] + ex, tr[2] + ey)
        ep["magnav"] = trn
        ep["trn_spread"] = trn_spread if trn else None
        ep["vio_truth_yaw"] = yaw
    return truth, epochs


class FilterCfg:
    """v2 filter tuning. Defaults reproduce v1's assumed noise values; calibrated() applies
    the measured envelope from calibration.json."""

    def __init__(self, label, **kw):
        self.label = label
        self.psi_sigma = 0.0
        self.s_sigma = 0.0
        self.vio_r = v1.VIO_R
        self.vio_r_water = v1.VIO_R_WATER
        self.gnss_r = v1.GNSS_R
        self.vgeo_r = v1.VGEO_R
        self.vgeo_bias = 0.0
        self.trn_from_spread = False
        self.trn_infl = 1.0
        self.trn_r_const = v1.MAGNAV_R
        self.priors = None
        for k, v in kw.items():
            if not hasattr(self, k):
                raise AttributeError(k)
            setattr(self, k, v)


def calibrated_values(cal=None, source=None):
    """The measured envelope over all relative sources (or one source) and the geoloc overbound."""
    cal = cal or load_cal()
    models = cal["relative"]["models"]
    rel = [models[source]] if source else list(models.values())
    ob = cal["geoloc"]["overbound"]
    white = max(m["fit_whole_run"]["white_frac_of_speed"] for m in rel) * v1.SPEED
    return {
        "psi_sigma": max(math.radians(m["per_window"]["yaw_abs_max_deg"]) for m in rel),
        "s_sigma": max(max(abs(m["fit_whole_run"]["scale_err"]), m["per_window"]["scale_std_pct"] / 100) for m in rel),
        "vio_r": white,
        "vio_r_water": white * WATER_WHITE_RATIO,
        "vgeo_r": max(ob["paired_sigma_e_m"], ob["paired_sigma_n_m"]),
        "vgeo_bias": math.hypot(ob["paired_bias_e_m"], ob["paired_bias_n_m"]),
        "vgeo_r_folded": ob["sigma_m"],
        "trn_infl": max(cal["trn"]["sigma_per_axis_over_spread_div_sqrt2"][r] for r in TRN_REGIONS),
        "priors": {"gnss": GNSS_FAULT_PRIOR, "vgeo": cal["geoloc"]["wrong_fix"]["rate_upper_95"],
                   "magnav": cal["trn"]["fault_rate_upper_95"]},
    }


def ladder(cal=None):
    c = calibrated_values(cal)
    states = dict(psi_sigma=c["psi_sigma"], s_sigma=c["s_sigma"])
    meas_r = dict(states, vio_r=c["vio_r"], vio_r_water=c["vio_r_water"], vgeo_r=c["vgeo_r_folded"], vgeo_bias=c["vgeo_bias"])
    return {
        "L1": FilterCfg("+ heading, scale states", **states),
        "L2": FilterCfg("+ measured VIO R, vgeo folded overbound R + bias in PL", **meas_r),
        "L2p": FilterCfg("+ measured VIO R, vgeo paired sigma R + bias in PL", **dict(meas_r, vgeo_r=c["vgeo_r"])),
        "L2n": FilterCfg("+ measured VIO R, vgeo folded overbound R, no bias term", **dict(meas_r, vgeo_bias=0.0)),
        "L3": FilterCfg("+ fault priors per source", **dict(meas_r, priors=c["priors"])),
        "L4": FilterCfg("+ TRN, R from spread", **dict(meas_r, priors=c["priors"], trn_from_spread=True, trn_infl=c["trn_infl"])),
        "L4c": FilterCfg("+ TRN, constant R", **dict(meas_r, priors=c["priors"])),
        **{key: per_source(f"L3 tuned to {src} only", src, cal) for key, src in PER_SOURCE.items()},
    }


PER_SOURCE = {"L3o": "openvins-uzhfpv", "L3k": "kiss-icp-kitti04", "L3v": "nadir-vo-vpair"}


def per_source(label, source, cal=None):
    c = calibrated_values(cal, source)
    return FilterCfg(label, psi_sigma=c["psi_sigma"], s_sigma=c["s_sigma"], vio_r=c["vio_r"],
                     vio_r_water=c["vio_r_water"], vgeo_r=c["vgeo_r_folded"], vgeo_bias=c["vgeo_bias"],
                     priors=c["priors"])


def _gm(sigma):
    phi = math.exp(-v1.EPOCH / GM_TAU)
    return phi, sigma * sigma * (1 - phi * phi)


def transition(cfg):
    F, Q = v1._transition()
    F, Q = [r[:] for r in F], [r[:] for r in Q]
    phi_s, q_s = _gm(cfg.s_sigma)
    phi_p, q_p = _gm(cfg.psi_sigma)
    for i in range(6, 8):
        for j in range(8):
            F[i][j] = F[j][i] = 0.0 if i != j else F[i][j]
            Q[i][j] = Q[j][i] = 0.0
    F[6][6], Q[6][6] = phi_s, q_s
    F[7][7], Q[7][7] = phi_p, q_p
    return F, Q


class Ekf2:
    """State [px, py, vx, vy, bax, bay, s, psi]: v1's INS error model with VIO scale and heading
    error states in place of v1's nav-frame VIO velocity bias. VIO: z = (1 + s) R(psi) v."""

    def __init__(self, x, P, cfg, excludes=None):
        self.x, self.P, self.cfg, self.excludes = list(x), [r[:] for r in P], cfg, excludes
        self.F, self.Q = transition(cfg)

    def clone(self, excludes):
        e = copy.copy(self)
        e.x, e.P, e.excludes = list(self.x), [r[:] for r in self.P], excludes
        return e

    def predict(self, imu):
        x = self.x
        for amx, amy in imu:
            ax, ay = amx - x[4], amy - x[5]
            x[0] += x[2] * v1.DT_IMU + 0.5 * ax * v1.DT_IMU ** 2
            x[1] += x[3] * v1.DT_IMU + 0.5 * ay * v1.DT_IMU ** 2
            x[2] += ax * v1.DT_IMU
            x[3] += ay * v1.DT_IMU
        x[6] *= self.F[6][6]
        x[7] *= self.F[7][7]
        self.P = mat.sym(mat.add(mat.mul(mat.mul(self.F, self.P), mat.T(self.F)), self.Q))

    def _vio_model(self):
        _, _, vx, vy, _, _, s, p = self.x
        c, sn = math.cos(p), math.sin(p)
        h = [(1 + s) * (c * vx - sn * vy), (1 + s) * (sn * vx + c * vy)]
        H = [[0, 0, (1 + s) * c, -(1 + s) * sn, 0, 0, c * vx - sn * vy, (1 + s) * (-sn * vx - c * vy)],
             [0, 0, (1 + s) * sn, (1 + s) * c, 0, 0, sn * vx + c * vy, (1 + s) * (c * vx - sn * vy)]]
        return h, H

    def _meas(self, src, ep):
        cfg = self.cfg
        if src == "vio":
            h, H = self._vio_model()
            return ep["vio"][0], h, H, cfg.vio_r_water if ep.get("vio_white_water") else cfg.vio_r
        z = ep[src]
        if src == "gnss":
            r = cfg.gnss_r
        elif src == "vgeo":
            r = cfg.vgeo_r
        else:
            spread = ep.get("trn_spread")
            r = cfg.trn_infl * spread / math.sqrt(2) if cfg.trn_from_spread and spread else cfg.trn_r_const
        return z, [self.x[0], self.x[1]], v1.H_POS, r

    def innovation(self, src, ep):
        z, h, H, r = self._meas(src, ep)
        y = [z[0] - h[0], z[1] - h[1]]
        S = mat.add(mat.mul(mat.mul(H, self.P), mat.T(H)), [[r * r, 0.0], [0.0, r * r]])
        Si = mat.inv2(S)
        return y, H, Si, sum(y[i] * Si[i][j] * y[j] for i in range(2) for j in range(2))

    def fuse(self, src, ep, gate):
        y, H, Si, nis = self.innovation(src, ep)
        if gate and nis > v1.CHI2_2DOF_999:
            return nis, False
        K = mat.mul(mat.mul(self.P, mat.T(H)), Si)
        self.x = [a + b for a, b in zip(self.x, mat.mv(K, y))]
        self.P = mat.sym(mat.mul(mat.sub(mat.eye(8), mat.mul(K, H)), self.P))
        return nis, True

    def pos_cov(self):
        return [[self.P[0][0], self.P[0][1]], [self.P[1][0], self.P[1][1]]]


class Monitor2(v1.Monitor):
    """v1's solution-separation bank (detection, exclusion, ambiguity, rewind, probation reused)
    with per-source fault priors in K_md and the paired-overbound bias added to the PL."""

    def __init__(self, main, monitored, gate, cfg):
        super().__init__(main, monitored, gate)
        self.cfg = cfg

    def _k_md(self, s):
        pri = self.cfg.priors
        if not pri:
            return self.k_md
        n = max(len(self.subs), 1)
        return v1.q_inv(min(0.5, IR_FAULT / (n * pri.get(s, GNSS_FAULT_PRIOR))))

    def _probation(self, src, ep, t):
        ex = self.excluded[src]
        nis = self.main.innovation(src, ep)[3]
        if ex["streak"] is None:
            ex["streak"] = {"start": t, "passes": 0, "fails": 0}
        st = ex["streak"]
        if nis <= v1.CHI2_2DOF_999:
            st["passes"] += 1
            st["fails"] = 0
        else:
            st["fails"] += 1
            if st["fails"] >= 2 or st["passes"] == 0:
                ex["streak"] = None

    def step(self, ep):
        t = self.t = ep["t"]
        events = []
        for f in [self.main, *self.subs.values()]:
            f.predict(ep["imu"])
        for src in v1._available_sources(ep):
            if src in self.excluded:
                self._probation(src, ep, t)
                continue
            _, ok = self.main.fuse(src, ep, self.gate)
            if ok:
                self.last_fused[src] = t
            else:
                events.append(f"gate:{src}")
            for s, f in self.subs.items():
                if s != src:
                    f.fuse(src, ep, self.gate)
        if self.subs and not self.ambiguous:
            self._detect(t, ep, events)
        self._readmit(t, events)
        self.history.append((self.main.clone(None), ep))
        return self._hpl(), events

    def _rewind(self, cur):
        if not self.history:
            return
        snap, _ = self.history[0]
        f = snap.clone(None)
        for ep in (*[e for _, e in list(self.history)[1:]], cur):
            f.predict(ep["imu"])
            f.fuse("vio", ep, self.gate)
        self.main = f

    def _bias(self, excluded_src=None):
        b = self.cfg.vgeo_bias
        if not b or excluded_src == "vgeo" or "vgeo" in self.excluded:
            return 0.0
        return b if self.t - self.last_fused.get("vgeo", -math.inf) <= v1.ACTIVE_WINDOW + v1.LOOKBACK else 0.0

    def _separations(self):
        # A nominal registration bias moves main and every branch that fuses vgeo, so it shows up
        # in the separations: widen each threshold by it (else it alarms on healthy data).
        b = self._bias()
        return {s: (d, thr + b, sig) for s, (d, thr, sig) in super()._separations().items()}

    def _hpl(self):
        sig0 = math.sqrt(mat.lmax2(self.main.pos_cov()))
        terms = [self.k_ff * sig0 + self._bias()]
        for s, (_, thr, sig) in self._separations().items():
            terms.append(thr + self._k_md(s) * sig + self._bias(s))
        until, spread = self.post_exclusion
        if self.t <= until:
            terms.append(spread + self.k_md * sig0 + self._bias())
        return max(terms)


def run_v2(sc, seed, cfg, mode="full", alert_limit=v1.ALERT_LIMIT, data=None):
    truth, epochs = data
    rng = random.Random(seed + 10_000)
    t0 = truth[0]
    x0 = [t0[1] + rng.gauss(0, 3), t0[2] + rng.gauss(0, 3),
          t0[3] + rng.gauss(0, 0.3), t0[4] + rng.gauss(0, 0.3), 0, 0, 0, 0]
    P0 = mat.zeros(8, 8)
    for i, s in enumerate([3, 3, 0.3, 0.3, 0.05, 0.05, cfg.s_sigma, cfg.psi_sigma]):
        P0[i][i] = s * s
    mon = Monitor2(Ekf2(x0, P0, cfg), v1.monitored_sources(sc) if mode == "full" else (), mode != "none", cfg)
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
            "alert": mon.ambiguous, "gnss_state": ep["gnss_state"], "vgeo_state": ep["vgeo_state"],
            "excluded": "+".join(sorted(mon.excluded)), "events": " ".join(events),
            "psi_est": x[7], "s_est": x[6],
        })
    return rows


def relimit(rows, al):
    """Re-evaluate availability and Stanford regions at another alert limit (HPL does not depend on AL)."""
    out = []
    for r in rows:
        a = r["hpl"] < al and not r["alert"]
        out.append(dict(r, available=a, region=stanford.classify(r["hpe"], r["hpl"] if a else max(r["hpl"], al), al)))
    return out


def metrics(rows, sc, al):
    s = v1.summarize(relimit(rows, al), sc, al)
    return {"epochs": s["epochs"], "avail": s["availability"], "mi": s["mi"], "hmi": s["hmi"],
            "missed": s["missed_hazards"], "wrong_blame": s["wrong_attributions"],
            "hpe_rms": s["hpe_rms"], "hpe_max": s["hpe_max"], "hpl_median": s["hpl_median"]}


ROWS_QUICK = [
    ("assumed", "v1", "none"), ("assumed", "v1", "full"),
    ("measured", "v1", "none"), ("measured", "v1", "full"),
    ("assumed", "L3", "full"), ("measured", "L1", "full"), ("measured", "L2", "full"), ("measured", "L3", "full"),
]
ROWS_FULL = [
    ("assumed", "v1", "none"), ("assumed", "v1", "gate"), ("assumed", "v1", "full"),
    ("assumed", "L1", "full"), ("assumed", "L3", "full"),
    ("measured", "v1", "none"), ("measured", "v1", "gate"), ("measured", "v1", "full"),
    ("measured", "L1", "full"), ("measured", "L2", "full"), ("measured", "L2p", "full"), ("measured", "L2n", "full"),
    ("measured", "L3", "full"), ("measured", "L3o", "full"),
    ("measured+trn", "v1", "full"), ("measured+trn", "L4c", "full"), ("measured+trn", "L4", "full"),
    ("measured-kiss", "v1", "full"), ("measured-kiss", "L3", "full"), ("measured-kiss", "L3k", "full"),
    ("measured-vpair", "v1", "full"), ("measured-vpair", "L3", "full"), ("measured-vpair", "L3v", "full"),
    ("stress", "v1", "full"), ("stress", "L3", "full"),
    ("assumed-nognss", "v1", "full"), ("measured-nognss", "v1", "none"), ("measured-nognss", "v1", "full"),
    ("measured-nognss", "L3", "full"),
]
ALS = (50.0, 100.0)


def run_row(world, sc, seed, filt, mode, data, cfgs):
    if filt == "v1":
        return v1.run(sc, seed, mode, data=data)
    return run_v2(sc, seed, cfgs[filt], mode, data=data)


def monte_carlo(runs, rows=ROWS_FULL, progress=False):
    ws, cfgs = worlds(), ladder()
    agg = {}
    for seed in range(1, runs + 1):
        cache = {}
        for wname, filt, mode in rows:
            w = ws[wname]
            sc = scenario(w)
            if wname not in cache:
                cache[wname] = simulate(sc, seed, w)
            rs = run_row(w, sc, seed, filt, mode, cache[wname], cfgs)
            for al in ALS:
                m = metrics(rs, sc, al)
                a = agg.setdefault((wname, filt, mode, al), {k: 0.0 for k in m})
                for k, v in m.items():
                    a[k] += v * (m["epochs"] if k in ("avail", "hpe_rms", "hpl_median") else 1) if k != "hpe_max" else 0
                a["hpe_max"] = max(a["hpe_max"], m["hpe_max"])
        if progress:
            print(f"  seed {seed} done", flush=True)
    out = []
    for (wname, filt, mode, al), a in agg.items():
        n = a["epochs"]
        out.append({"world": wname, "filter": filt, "filter_label": "v1 as tuned" if filt == "v1" else cfgs[filt].label,
                    "mode": mode, "al": al, "seeds": runs, "epochs": int(n), "avail_pct": round(100 * a["avail"] / n, 1),
                    "mi_star": int(a["mi"]), "hmi": int(a["hmi"]), "missed_hazards": int(a["missed"]),
                    "wrong_blame": int(a["wrong_blame"]), "hpe_rms_mean": round(a["hpe_rms"] / n, 1),
                    "hpe_max": round(a["hpe_max"], 1), "hpl_median_mean": round(a["hpl_median"] / n, 1)})
    return out


def print_table(out, al):
    print(f"\nAL = {al:.0f} m  (MI* = MI + HMI + unavailable-and-MI epochs)")
    print(f"{'world':16}{'filter':8}{'mode':6}{'avail %':>8}{'MI*':>7}{'HMI':>7}{'missed':>8}{'wrong':>7}"
          f"{'HPE rms':>9}{'HPE max':>9}{'HPL med':>9}")
    for r in out:
        if r["al"] != al:
            continue
        print(f"{r['world']:16}{r['filter']:8}{r['mode']:6}{r['avail_pct']:>8}{r['mi_star']:>7}{r['hmi']:>7}"
              f"{r['missed_hazards']:>8}{r['wrong_blame']:>7}{r['hpe_rms_mean']:>9}{r['hpe_max']:>9}{r['hpl_median_mean']:>9}")


def single(seed, gnss=True):
    ws, cfgs = worlds(), ladder()
    out = []
    for wname, filt, mode in ROWS_QUICK:
        w = copy.copy(ws[wname])
        w.gnss = gnss
        sc = scenario(w)
        data = simulate(sc, seed, w)
        rs = run_row(w, sc, seed, filt, mode, data, cfgs)
        m = metrics(rs, sc, v1.ALERT_LIMIT)
        s = v1.summarize(rs, sc)
        log = sorted(v1._events(rs, "alert:") + v1._events(rs, "exclude:") +
                     [(t, "blame " + x) for t, x in v1._events(rs, "blame:")])
        out.append((wname, filt, mode, m, s, log))
    print(f"seed={seed} AL={v1.ALERT_LIMIT:.0f} m gnss={'on' if gnss else 'off'}")
    print(f"{'world':10}{'filter':7}{'mode':6}{'avail %':>8}{'MI*':>6}{'HMI':>6}{'HPE rms':>9}{'HPE max':>9}{'HPL med':>9}  monitor log")
    for wname, filt, mode, m, s, log in out:
        print(f"{wname:10}{filt:7}{mode:6}{100 * m['avail']:>8.1f}{m['mi']:>6}{m['hmi']:>6}{m['hpe_rms']:>9.1f}"
              f"{m['hpe_max']:>9.1f}{m['hpl_median']:>9.1f}  " + ", ".join(f"{t:.0f}s {x}" for t, x in log[:6]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--runs", type=int, default=0, help="Monte Carlo over seeds 1..N")
    ap.add_argument("--quick", action="store_true", help="headline rows only")
    ap.add_argument("--no-gnss", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "results", "v2_mc.json"))
    a = ap.parse_args(argv)
    if not a.runs:
        single(a.seed, gnss=not a.no_gnss)
        return
    rows = ROWS_QUICK if a.quick else ROWS_FULL
    out = monte_carlo(a.runs, rows, progress=True)
    for al in ALS:
        print_table(out, al)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump({"runs": a.runs, "calibrated": calibrated_values(),
                   "rows": out}, fh, indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
