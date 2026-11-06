"""Physics for the jammer sensor network (stdlib): log-distance path loss with spatially
correlated shadowing, optional building blockage, and the C/N0 / AGC response of a
u-blox-class GPS L1 C/A receiver to a noise jammer.

C/N0 under interference (Kaplan & Hegarty, "Understanding GPS", interference chapter by
Ward et al.; same structure as the spectral-separation form on ESA Navipedia):
    1/(C/N0)_eff = 1/(C/N0) + (J/S) / (Q * Rc)
Q = 1 narrowband/CW, 1.5 narrowband matched-spectrum, 2 wideband Gaussian noise.
Since S/(C/N0) = N0 for every satellite, the drop D = (C/N0) - (C/N0)_eff in dB is the same
for all tracked SVs and inverts to the jammer power at the antenna without knowing S:
    J = Q * Rc * N0 * (10^(D/10) - 1)
"""
import math
import random

C_M_S = 299_792_458.0
F_L1_HZ = 1575.42e6
RC_CA_CHIPS_S = 1.023e6
Q_CW = 1.0
Q_WIDEBAND = 2.0
KT_DBM_HZ = -174.0               # thermal noise density at 290 K
NOISE_FIGURE_DB = 2.0            # assumed receiver noise figure
N0_DBM_HZ = KT_DBM_HZ + NOISE_FIGURE_DB
FRONTEND_BW_HZ = 2.0e6           # assumed pre-correlation bandwidth seen by the AGC
GPS_L1CA_MIN_DBM = -128.5        # IS-GPS-200 minimum received power, -158.5 dBW
TRACK_LOSS_CN0_DBHZ = 28.0       # assumed tracking threshold; not a u-blox figure
MIN_SV_FOR_FIX = 4
D0_M = 1.0
D_MIN_M = 5.0                    # near-field / same-site floor for the path-loss model
FSPL_D0_DB = 20 * math.log10(4 * math.pi * D0_M * F_L1_HZ / C_M_S)
PLE_DEFAULT = 2.7                # path-loss exponent, ground-level suburban (scenario choice)

AGC_MAX_REDUCTION_DB = 50.0      # synthetic AGC range
AGC_REF_COUNTS = 5000            # synthetic clear-sky agcCnt (field range 0..8191)
AGC_COUNTS_PER_DB = 60.0         # synthetic; real receivers need per-device calibration
AGC_NOISE_DB = 0.4
CN0_SV_NOISE_DB = 1.0
JAM_IND_BASE = 8                 # synthetic idle jamInd; jamInd is a CW-only indicator (0..255)
JAM_STATE_UNKNOWN, JAM_STATE_OK, JAM_STATE_WARNING, JAM_STATE_CRITICAL = 0, 1, 2, 3
WARNING_DROP_DB = 3.0


def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def path_loss_db(d_m, ple=PLE_DEFAULT):
    return FSPL_D0_DB + 10.0 * ple * math.log10(max(d_m, D_MIN_M) / D0_M)


def cn0_effective(cn0_dbhz, j_dbm, q=Q_WIDEBAND):
    s_dbm = cn0_dbhz + N0_DBM_HZ
    inv = db2lin(-cn0_dbhz) + db2lin(j_dbm - s_dbm) / (q * RC_CA_CHIPS_S)
    return -lin2db(inv)


def jammer_dbm_from_cn0_drop(drop_db, q=Q_WIDEBAND):
    """J at the antenna from the C/N0 drop; None when the drop is not positive."""
    if drop_db <= 0:
        return None
    return N0_DBM_HZ + lin2db(q * RC_CA_CHIPS_S) + lin2db(db2lin(drop_db) - 1.0)


def cn0_drop_from_jammer_dbm(j_dbm, q=Q_WIDEBAND):
    return lin2db(1.0 + db2lin(j_dbm - N0_DBM_HZ) / (q * RC_CA_CHIPS_S))


def agc_reduction_db(j_dbm):
    """Gain the AGC removes to hold total in-band power: noise floor + jammer."""
    return min(lin2db(1.0 + db2lin(j_dbm - N0_DBM_HZ - lin2db(FRONTEND_BW_HZ))), AGC_MAX_REDUCTION_DB)


def jammer_dbm_from_agc_reduction(r_db):
    if r_db <= 0:
        return None
    return N0_DBM_HZ + lin2db(FRONTEND_BW_HZ) + lin2db(db2lin(r_db) - 1.0)


def d_power_d_drop(drop_db):
    """dJ/dD (dB per dB) for both inversions; large near zero drop (poor sensitivity)."""
    lin = db2lin(drop_db)
    return lin / (lin - 1.0)


class ShadowField:
    """Zero-mean Gaussian shadowing over a link (rx, tx) with ~Gaussian correlation of length
    corr_m in each end's position (sum of random sinusoids in 4-D). No common-mode part:
    moving either end by more than corr_m gives a new, independent draw."""

    N_WAVES = 96

    def __init__(self, sigma_db, corr_m, rng):
        self.sigma = sigma_db
        self.waves = [tuple(rng.gauss(0, 1 / corr_m) for _ in range(4)) + (rng.uniform(0, 2 * math.pi),)
                      for _ in range(self.N_WAVES)]
        self.amp = sigma_db * math.sqrt(2.0 / self.N_WAVES)

    def __call__(self, rx, tx):
        if self.sigma == 0:
            return 0.0
        return self.amp * sum(math.cos(a * rx[0] + b * rx[1] + c * tx[0] + d * tx[1] + ph)
                              for a, b, c, d, ph in self.waves)


def segment_hits_rect(p, q, rect):
    """Liang-Barsky clip of segment p=>q against rect (xmin, ymin, xmax, ymax)."""
    x0, y0 = p
    dx, dy = q[0] - x0, q[1] - y0
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, x0 - rect[0]), (dx, rect[2] - x0), (-dy, y0 - rect[1]), (dy, rect[3] - y0)):
        if pk == 0:
            if qk < 0:
                return False
            continue
        r = qk / pk
        if pk < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 > t1:
            return False
    return True


class Environment:
    """Propagation truth: path-loss exponent, link shadowing, buildings."""

    def __init__(self, sigma_db=6.0, corr_m=50.0, ple=PLE_DEFAULT, buildings=(), building_loss_db=15.0,
                 rng=None):
        rng = rng or random.Random(0)
        self.ple = ple
        self.sigma_db = sigma_db
        self.shadow = ShadowField(sigma_db, corr_m, rng)
        self.buildings = list(buildings)
        self.building_loss_db = building_loss_db

    def received_dbm(self, rx_xy, tx_xy, eirp_dbm):
        d = math.hypot(rx_xy[0] - tx_xy[0], rx_xy[1] - tx_xy[1])
        loss = path_loss_db(d, self.ple) + self.shadow(rx_xy, tx_xy)
        loss += self.building_loss_db * sum(segment_hits_rect(tx_xy, rx_xy, b) for b in self.buildings)
        return eirp_dbm - loss


class Jammer:
    def __init__(self, path, eirp_dbm, q=Q_WIDEBAND, t_on=0.0, t_off=math.inf, name="J1"):
        self.path, self.eirp_dbm, self.q, self.t_on, self.t_off, self.name = path, eirp_dbm, q, t_on, t_off, name

    def active(self, t):
        return self.t_on <= t < self.t_off


def total_jammer_dbm(env, rx_xy, jammers, t):
    """Sum of active jammers in linear power, with each jammer's Q folded in relative to
    wideband so one effective J drives the C/N0 model. None when nothing is on."""
    lin = 0.0
    for j in jammers:
        if j.active(t):
            lin += db2lin(env.received_dbm(rx_xy, j.path(t), j.eirp_dbm)) * (Q_WIDEBAND / j.q)
    return lin2db(lin) if lin > 0 else None


def linear_path(p0, p1, t0, t1):
    def f(t):
        a = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
        return p0[0] + a * (p1[0] - p0[0]), p0[1] + a * (p1[1] - p0[1])
    return f


def polyline_path(points, speed_mps, t_start=0.0, loop=True):
    segs, total = [], 0.0
    pts = list(points) + ([points[0]] if loop else [])
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((total, L, a, b))
        total += L

    def f(t):
        s = max(t - t_start, 0.0) * speed_mps
        s = s % total if loop else min(s, total)
        for s0, L, a, b in segs:
            if s <= s0 + L or (s0, L, a, b) == segs[-1]:
                u = (s - s0) / L if L else 0.0
                return a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])
    return f


def static_path(xy):
    return lambda t: xy


class SimNode:
    """A u-blox-class sensor node. Produces the fields a pyubx2 reader would give:
    NAV-PVT fix, NAV-SAT C/N0 per SV, MON-RF agcCnt / jamInd / jammingState."""

    GNSS_POS_SIGMA_M = 2.0
    DR_DRIFT_MPS = 0.5
    SURVEY_SIGMA_M = 0.5

    def __init__(self, node_id, path, static, rng, n_sv=9, agc_cal_err_db=1.5):
        self.id, self.path, self.static, self.rng = node_id, path, static, rng
        self.cn0_clear = [rng.uniform(38.0, 48.0) for _ in range(n_sv)]
        self.agc_ref = AGC_REF_COUNTS + rng.randint(-200, 200)
        self.agc_cal_err_db = rng.gauss(0, agc_cal_err_db)
        self.seq = 0
        self.lost_since = None
        self.dr_dir = rng.uniform(0, 2 * math.pi)
        self.last_fix_xy = None

    def meta(self):
        return {"agc_ref": self.agc_ref, "agc_db_per_cnt": round(1.0 / AGC_COUNTS_PER_DB, 6)}

    def observe(self, t, j_dbm, q=Q_WIDEBAND):
        """j_dbm: total jammer power at the antenna (None = clear). Returns obs fields + truth xy."""
        rng = self.rng
        xy = self.path(t)
        tracked = []
        for c in self.cn0_clear:
            eff = cn0_effective(c, j_dbm, q) if j_dbm is not None else c
            eff += rng.gauss(0, CN0_SV_NOISE_DB)
            if eff >= TRACK_LOSS_CN0_DBHZ:
                tracked.append((c, eff))
        fix = len(tracked) >= MIN_SV_FOR_FIX
        drops = sorted(c - e for c, e in tracked)
        drop = drops[len(drops) // 2] if drops else None
        red = agc_reduction_db(j_dbm) if j_dbm is not None else 0.0
        red += rng.gauss(0, AGC_NOISE_DB) + (self.agc_cal_err_db if red > 1.0 else 0.0)
        agc = int(min(max(self.agc_ref - max(red, 0.0) * AGC_COUNTS_PER_DB, 0), 8191))
        if q == Q_CW and j_dbm is not None:
            jam_ind = int(min(255, JAM_IND_BASE + max(0.0, 6.0 * (drop or 40.0))))
        else:
            jam_ind = JAM_IND_BASE + rng.randint(-3, 3)
        if not fix:
            state = JAM_STATE_CRITICAL
        elif drop is not None and drop > WARNING_DROP_DB:
            state = JAM_STATE_WARNING
        else:
            state = JAM_STATE_OK

        if self.static:
            pos = (xy[0] + rng.gauss(0, self.SURVEY_SIGMA_M), xy[1] + rng.gauss(0, self.SURVEY_SIGMA_M))
            ps, src = self.SURVEY_SIGMA_M, "survey"
        elif fix:
            self.lost_since = None
            pos = (xy[0] + rng.gauss(0, self.GNSS_POS_SIGMA_M), xy[1] + rng.gauss(0, self.GNSS_POS_SIGMA_M))
            ps, src = self.GNSS_POS_SIGMA_M, "gnss"
        else:
            if self.lost_since is None:
                self.lost_since = t
                self.dr_dir = rng.uniform(0, 2 * math.pi)
            drift = self.DR_DRIFT_MPS * (t - self.lost_since)
            pos = (xy[0] + drift * math.cos(self.dr_dir), xy[1] + drift * math.sin(self.dr_dir))
            ps, src = self.GNSS_POS_SIGMA_M + drift, "dr"
        self.seq += 1
        return {"seq": self.seq, "t": t, "xy": pos, "ps": ps, "pf": src, "fix": int(fix),
                "nsv": len(tracked), "cn0": round(sum(e for _, e in tracked) / len(tracked), 1) if tracked else None,
                "dcn0": round(drop, 2) if drop is not None else None, "agc": agc, "jam": jam_ind,
                "jst": state}, xy
