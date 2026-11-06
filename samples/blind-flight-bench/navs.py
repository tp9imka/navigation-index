"""Navigators. Each is causal: update(t, h) sees one sample and returns the current (east, north).

h is the measured terrain height, flight level minus radar AGL. Navigators get the DEM (not the
world surface), the start fix and heading/speed hints; nothing else about the truth.

- DeadReckonHint: hints only, no terrain. Floor reference.
- TercomBaseline: OUR batch TERCOM, core.tercom_fix from samples/terrain-heightmap-pf, driven by
  a constant-velocity track with an alpha-beta velocity correction (this case has no odometry).
- ParticleFilter: OUR SIR filter in the style of samples/terrain-relative-nav-pf, with speed,
  heading, turn rate and altitude-reference bias in the state because there is no INS.
- GagarinCR: clean-room re-implementation of the Gagarin (danilka88/gag27062026) checkpoint
  pipeline from its README text only.
- GorizontCR: clean-room re-implementation of the GORIZONT (t1Gr20an06-k/Hackathon-Blind-Flight)
  multi-hypothesis tracker from its README flag reference only.
"""
import numpy as np

from ext import hpf_core

bilinear = hpf_core.bilinear
tercom_fix = hpf_core.tercom_fix
systematic_resample = hpf_core.systematic_resample


def unit(az_deg):
    a = np.radians(az_deg)
    return np.array([np.sin(a), np.cos(a)])


def ncc(a, b):
    a = a - a.mean(axis=-1, keepdims=True)
    b = b - b.mean(axis=-1, keepdims=True)
    den = np.sqrt((a * a).sum(-1) * (b * b).sum(-1))
    return np.where(den > 1e-9, (a * b).sum(-1) / np.maximum(den, 1e-9), 0.0)


def mad_meansub(obs, ref):
    return np.abs((ref - ref.mean(-1, keepdims=True)) - (obs - obs.mean())).mean(-1)


_BEAM_CACHE = {}


def beam_map(dem, res, flight_msl=1500.0, beam_full_deg=40.0):
    """Terrain height a leading-edge radar altimeter at flight_msl would report over each cell.

    h_eff(p) = flight_msl - min over q in the beam cone of the slant range to the DEM at q.
    Possible only because the case fixes the flight level; flat attitude assumed.
    """
    key = (id(dem), flight_msl, beam_full_deg)
    if key in _BEAM_CACHE:
        return _BEAM_CACHE[key]
    half = np.radians(beam_full_deg / 2)
    rmax = int(np.ceil((flight_msl - dem.min()) * np.tan(half) / res))
    pad = np.pad(dem, rmax, mode="edge")
    best = flight_msl - dem
    H, W = dem.shape
    for di in range(-rmax, rmax + 1):
        for dj in range(-rmax, rmax + 1):
            r = np.hypot(di, dj) * res
            if r == 0 or r > rmax * res:
                continue
            zq = pad[rmax + di:rmax + di + H, rmax + dj:rmax + dj + W]
            dz = flight_msl - zq
            slant = np.where(r <= dz * np.tan(half), np.hypot(r, dz), np.inf)
            np.minimum(best, slant, out=best)
    out = flight_msl - best
    _BEAM_CACHE[key] = out
    return out


class Navigator:
    name = "base"

    def __init__(self, dem, res, prior):
        self.dem, self.res, self.prior = dem, res, prior
        self.t0 = prior["t0"]
        self.stats = {"fixes_accepted": 0, "fixes_rejected": 0}

    def update(self, t, h):
        raise NotImplementedError


class DeadReckonHint(Navigator):
    name = "dr_hint"

    def __init__(self, dem, res, prior):
        super().__init__(dem, res, prior)
        self.p0 = np.array([prior["e0"], prior["n0"]])
        self.v = prior["speed_mps"] * unit(prior["heading_deg"])

    def update(self, t, h):
        return self.p0 + self.v * (t - self.t0)


class _History:
    """Growable per-sample buffers (t, h, e, n)."""

    def __init__(self, cap=8192):
        self.a = np.zeros((cap, 4))
        self.k = 0

    def add(self, t, h, e, n):
        if self.k == len(self.a):
            self.a = np.vstack([self.a, np.zeros_like(self.a)])
        self.a[self.k] = (t, h, e, n)
        self.k += 1

    @property
    def v(self):
        return self.a[:self.k]


class TercomBaseline(Navigator):
    name = "tercom_ours"
    FIX_EVERY_M = 1000.0
    PROFILE_M = 2000.0
    RADIUS_M = 600.0
    RADIUS_GROWTH = 0.1          # search radius grows by 10% of distance flown since the last fix
    RADIUS_MAX_M = 3000.0
    GRID_HALF_CELLS = 20         # keeps the grid at most 41 x 41 when the radius grows
    STEP_M = 30.0
    AMBIGUITY_RATIO = 0.9        # same acceptance rule as terrain-heightmap-pf
    VEL_GAIN = 0.5
    MAX_PROFILE_PTS = 150

    def __init__(self, dem, res, prior):
        super().__init__(dem, res, prior)
        self.p = np.array([prior["e0"], prior["n0"]])
        self.vel = prior["speed_mps"] * unit(prior["heading_deg"])
        self.t_prev = self.t0
        self.t_last_fix = self.t0
        self.since = 0.0
        self.since_accept = 0.0
        self.hist = _History()

    def update(self, t, h):
        dt = t - self.t_prev
        self.t_prev = t
        self.p = self.p + self.vel * dt
        self.since += np.linalg.norm(self.vel) * dt
        self.since_accept += np.linalg.norm(self.vel) * dt
        self.hist.add(t, h, *self.p)
        if self.since >= self.FIX_EVERY_M:
            self._try_fix(t)
        return self.p.copy()

    def _try_fix(self, t):
        H = self.hist.v
        span = np.linalg.norm(self.vel) * (t - H[:, 0])
        sel = np.where(span <= self.PROFILE_M)[0]
        if span[0] < self.PROFILE_M or len(sel) < 20:
            return
        self.since = 0.0
        sel = sel[np.linspace(0, len(sel) - 1, min(len(sel), self.MAX_PROFILE_PTS)).astype(int)]
        radius = min(self.RADIUS_M + self.RADIUS_GROWTH * max(self.since_accept - self.PROFILE_M, 0.0),
                     self.RADIUS_MAX_M)
        step = max(self.STEP_M, radius / self.GRID_HALF_CELLS)
        r = tercom_fix(self.dem, self.res, H[sel, 2], H[sel, 3], H[sel, 1], radius, step)
        ok = (r is not None and r[2] < self.AMBIGUITY_RATIO * r[3]
              and max(abs(r[0]), abs(r[1])) < radius - step / 2)
        if not ok:
            self.stats["fixes_rejected"] += 1
            return
        self.stats["fixes_accepted"] += 1
        d = np.array(r[:2])
        self.hist.a[:self.hist.k, 2:4] += d
        self.p = self.p + d
        self.vel = self.vel + self.VEL_GAIN * d / max(t - self.t_last_fix, 10.0)
        self.t_last_fix = t
        self.since_accept = 0.0


class ParticleFilter(Navigator):
    name = "pf_ours"
    N = 4000
    UPDATE_DIST_M = 60.0         # ~2 DEM cells; denser updates reuse the same correlated error
    MEAS_SIGMA_M = 15.0          # radar noise + footprint + canopy + map error, lumped
    OUTLIER_EPS = 0.05
    OUTLIER_SPAN_M = 400.0
    POS_JITTER_M = 4.0
    HEADING_JITTER_DEG = 0.3
    SPEED_JITTER = 0.1
    HEADING_RW = 0.3             # deg / sqrt(s)
    TURN_RATE_RW = 0.02          # deg/s / sqrt(s), between jumps
    TURN_RATE_MAX = 5.0
    TURN_JUMP_PER_S = 0.01       # piecewise-constant turn rate: chance per second of a new value
    TURN_ZERO_SHARE = 0.5        # share of jumps that return to straight flight
    SPEED_RW = 0.15              # m/s / sqrt(s)
    BIAS_SIGMA0_M = 50.0
    BIAS_RW = 0.5                # m / sqrt(s); covers baro drift of a few cm/s
    HEADING_SIGMA0_DEG = 8.0
    SPEED_SIGMA0 = 3.0

    def __init__(self, dem, res, prior, seed=0):
        super().__init__(dem, res, prior)
        self.rng = np.random.default_rng(seed)
        r, N = self.rng, self.N
        ps = max(prior["pos_sigma_m"], 10.0) * 1.5
        self.x = np.column_stack([
            prior["e0"] + ps * r.standard_normal(N),
            prior["n0"] + ps * r.standard_normal(N),
            prior["speed_mps"] + self.SPEED_SIGMA0 * r.standard_normal(N),
            prior["heading_deg"] + self.HEADING_SIGMA0_DEG * r.standard_normal(N),
            np.zeros(N),
            self.BIAS_SIGMA0_M * r.standard_normal(N),
        ])
        self.w = np.full(N, 1.0 / N)
        self.t_prev = self.t0
        self.update_dt = self.UPDATE_DIST_M / max(prior["speed_mps"], 5.0)
        self.est = np.array([prior["e0"], prior["n0"]])
        self.t_est = self.t0
        self.v_est = prior["speed_mps"] * unit(prior["heading_deg"])

    def _predict(self, dt):
        r, x, N = self.rng, self.x, self.N
        x[:, 4] += self.TURN_RATE_RW * np.sqrt(dt) * r.standard_normal(N)
        jump = r.random(N) < self.TURN_JUMP_PER_S * dt
        new = np.where(r.random(N) < self.TURN_ZERO_SHARE, 0.0,
                       r.uniform(-self.TURN_RATE_MAX, self.TURN_RATE_MAX, N))
        x[:, 4] = np.clip(np.where(jump, new, x[:, 4]), -self.TURN_RATE_MAX, self.TURN_RATE_MAX)
        x[:, 3] += x[:, 4] * dt + self.HEADING_RW * np.sqrt(dt) * r.standard_normal(N)
        x[:, 2] = np.clip(x[:, 2] + self.SPEED_RW * np.sqrt(dt) * r.standard_normal(N), 5.0, 120.0)
        a3 = np.radians(x[:, 3])
        x[:, 0] += x[:, 2] * np.sin(a3) * dt
        x[:, 1] += x[:, 2] * np.cos(a3) * dt
        x[:, 5] += self.BIAS_RW * np.sqrt(dt) * r.standard_normal(N)

    def update(self, t, h):
        dt = t - self.t_prev
        if dt >= self.update_dt:
            self.t_prev = t
            self._predict(dt)
            pred = bilinear(self.dem, self.x[:, 0], self.x[:, 1], self.res, fill=np.nan) - self.x[:, 5]
            resid = h - pred
            g = np.exp(-0.5 * (resid / self.MEAS_SIGMA_M) ** 2) / (np.sqrt(2 * np.pi) * self.MEAS_SIGMA_M)
            lik = (1 - self.OUTLIER_EPS) * g + self.OUTLIER_EPS / self.OUTLIER_SPAN_M
            lik = np.where(np.isfinite(lik), lik, 1e-12)
            w = self.w * lik
            self.w = w / w.sum()
            ess = 1.0 / np.sum(self.w ** 2)
            if ess < self.N / 2:
                idx = systematic_resample(self.w, self.rng)
                self.x = self.x[idx]
                self.x[:, :2] += self.POS_JITTER_M * self.rng.standard_normal((self.N, 2))
                self.x[:, 3] += self.HEADING_JITTER_DEG * self.rng.standard_normal(self.N)
                self.x[:, 2] += self.SPEED_JITTER * self.rng.standard_normal(self.N)
                self.w = np.full(self.N, 1.0 / self.N)
            self.est = self.w @ self.x[:, :2]
            a3 = np.radians(self.x[:, 3])
            self.v_est = np.array([self.w @ (self.x[:, 2] * np.sin(a3)), self.w @ (self.x[:, 2] * np.cos(a3))])
            self.t_est = t
        return self.est + self.v_est * (t - self.t_est)


class GagarinCR(Navigator):
    """Clean-room, from the Gagarin README "checkpoint" section (algorithm steps 1-9, gates table,
    DR + weighted correction formula, minima ratio, roughness gate, position recovery).

    Deviations forced by evaluating causally: RANSAC becomes an innovation test against the
    accepted innovations so far, and multi-start picks the running-best mean NCC instead of the
    post-hoc best. Velocity is fixed after initialisation, as the checkpoint section describes.
    """
    name = "gagarin_cr"
    WS = 200
    AZ_INIT_SAMPLES = 60
    TOP_K = 3
    SPEEDS = np.arange(10.0, 150.1, 5.0)
    GRID_PX = 4
    EXCL_PX = 2
    P2V_MIN = 5.0
    MAD_MAX = 30.0
    NCC_MIN = 0.3
    DISCR_MIN = 1.0
    ROUGH_REJECT = 0.5
    MULTISTART_STD_M = 20.0
    LOST_AFTER = 5
    RECOVERY_N = 7
    RECOVERY_STEP_M = 150.0
    RECOVERY_CONF_MIN = 0.3

    def __init__(self, dem, res, prior, az_init_samples=None, az_window_deg=None):
        super().__init__(dem, res, prior)
        self.az_window = az_window_deg
        if az_init_samples is not None:
            self.AZ_INIT_SAMPLES = az_init_samples
        self.start = np.array([prior["e0"], prior["n0"]])
        self.hint_v = prior["speed_mps"] * unit(prior["heading_deg"])
        self.buf_t, self.buf_h = [], []
        self.tracks = None
        self.step_ = self.WS // 4
        g = np.arange(-self.GRID_PX, self.GRID_PX + 1) * res
        gx, gy = np.meshgrid(g, g)
        self.grid = np.column_stack([gx.ravel(), gy.ravel()])
        self.ambiguous = False

    def _profile_from_start(self, t, az, speed):
        return self.start[:, None] + np.outer(unit(az), speed * (t - t[0]))

    def _init(self):
        t = np.array(self.buf_t)
        h = np.array(self.buf_h)
        na = min(self.AZ_INIT_SAMPLES, len(t))
        if self.az_window is None:
            azs = np.arange(0, 360, 1.0)
        else:
            azs = (self.prior["heading_deg"] + np.arange(-self.az_window, self.az_window + 0.5, 1.0)) % 360
        dirs = np.stack([unit(a) for a in azs])
        d = self.prior["speed_mps"] * (t[:na] - t[0])
        pe = self.start[0] + dirs[:, :1] * d[None, :]
        pn = self.start[1] + dirs[:, 1:] * d[None, :]
        c = np.abs(ncc(h[None, :na], bilinear(self.dem, pe, pn, self.res, fill=0.0)))
        order = np.argsort(-c)
        picked = []
        for i in order:
            if all(min(abs(azs[i] - azs[j]), 360 - abs(azs[i] - azs[j])) >= 10 for j in picked):
                picked.append(i)
            if len(picked) == self.TOP_K:
                break
        cands = []
        for i in picked:
            az = azs[i]
            best = None
            for s in self.SPEEDS:
                p = self._profile_from_start(t, az, s)
                ref = bilinear(self.dem, p[0], p[1], self.res, fill=np.nan)
                if np.isnan(ref).any():
                    continue
                m = mad_meansub(h, ref)
                if best is None or m < best[0]:
                    best = (m, s, float(ncc(h, ref)))
            if best is not None:
                cands.append({"az": az, "speed": best[1], "ncc0": best[2]})
        if not cands:
            cands = [{"az": self.prior["heading_deg"], "speed": self.prior["speed_mps"], "ncc0": 0.0}]
        cands.sort(key=lambda c: -c["ncc0"])
        if np.std(h) >= self.MULTISTART_STD_M:
            cands = cands[:1]
        if len(cands) > 1 and abs(cands[0]["ncc0"] - cands[1]["ncc0"]) < 0.1 * abs(cands[0]["ncc0"]):
            da = abs(cands[0]["az"] - cands[1]["az"])
            self.ambiguous = min(da, 360 - da) > 30
        self.tracks = []
        for c in cands:
            v = c["speed"] * unit(c["az"])
            tc = t[len(t) // 2]
            self.tracks.append({"v": v, "filt": self.start + v * (tc - t[0]), "tc": tc,
                                "innov": [], "poor": 0, "ncc_sum": 0.0, "n": 0})

    def _window(self, tr, t, h):
        tc = t[len(t) // 2]
        dr = tr["filt"] + tr["v"] * (tc - tr["tc"])
        base = dr[:, None] + np.outer(tr["v"], t - tc)
        pe = base[0][None, :] + self.grid[:, :1]
        pn = base[1][None, :] + self.grid[:, 1:]
        ref = bilinear(self.dem, pe, pn, self.res, fill=np.nan)
        mad = np.where(np.isnan(ref).any(1), np.inf, mad_meansub(h, np.nan_to_num(ref)))
        b = int(np.argmin(mad))
        far = np.max(np.abs(self.grid - self.grid[b]), axis=1) > self.EXCL_PX * self.res
        second = mad[far].min() if far.any() else np.inf
        discr = second / max(mad[b], 1e-6)
        c = float(ncc(h, np.nan_to_num(ref[b])))
        r_obs = np.std(np.diff(h))
        r_ref = np.std(np.diff(np.nan_to_num(ref[b])))
        rough = abs(r_obs - r_ref) / max(r_obs, r_ref, 1e-6)
        meas = dr + self.grid[b]
        ok = (np.ptp(h) >= self.P2V_MIN and mad[b] <= self.MAD_MAX and c >= self.NCC_MIN
              and discr >= self.DISCR_MIN and rough <= self.ROUGH_REJECT and np.isfinite(mad[b]))
        innov = np.linalg.norm(meas - dr)
        if ok and len(tr["innov"]) >= 4:
            med = np.median(tr["innov"])
            ok = innov <= med + 2 * np.median(np.abs(np.array(tr["innov"]) - med)) + self.res
        if ok:
            tr["innov"].append(innov)
            w = float(np.clip((discr - 1.0) / 10.0, 0.0, 1.0))
            tr["filt"] = dr + w * (meas - dr)
            tr["poor"] = 0
            tr["ncc_sum"] += c
            tr["n"] += 1
            self.stats["fixes_accepted"] += 1
        else:
            tr["filt"] = dr
            tr["poor"] += 1
            self.stats["fixes_rejected"] += 1
            if tr["poor"] >= self.LOST_AFTER:
                self._recover(tr, t, h, dr, tc)
        tr["tc"] = tc

    def _recover(self, tr, t, h, dr, tc):
        k = (self.RECOVERY_N - 1) // 2
        g = np.arange(-k, k + 1) * self.RECOVERY_STEP_M
        gx, gy = np.meshgrid(g, g)
        offs = np.column_stack([gx.ravel(), gy.ravel()])
        base = dr[:, None] + np.outer(tr["v"], t - tc)
        ref = bilinear(self.dem, base[0][None, :] + offs[:, :1], base[1][None, :] + offs[:, 1:],
                       self.res, fill=0.0)
        c = ncc(h[None, :], ref)
        b = int(np.argmax(c))
        med = float(np.median(c))
        conf = (c[b] - med) / max(1.0 - med, 1e-6)
        self.stats.setdefault("recoveries", 0)
        if conf >= self.RECOVERY_CONF_MIN:
            tr["filt"] = dr + offs[b]
            tr["poor"] = 0
            self.stats["recoveries"] += 1

    def update(self, t, h):
        self.buf_t.append(t)
        self.buf_h.append(h)
        n = len(self.buf_t)
        if self.tracks is None:
            if n >= self.WS:
                self._init()
            else:
                return self.start + self.hint_v * (t - self.t0)
        elif (n - self.WS) % self.step_ == 0:
            tw = np.array(self.buf_t[-self.WS:])
            hw = np.array(self.buf_h[-self.WS:])
            for tr in self.tracks:
                self._window(tr, tw, hw)
        best = max(self.tracks, key=lambda tr: tr["ncc_sum"] / max(tr["n"], 1))
        return best["filt"] + best["v"] * (t - best["tc"])


class _KF:
    """Constant-velocity Kalman filter, state [e, n, ve, vn]."""

    def __init__(self, p, v, pos_sigma, vel_sigma, accel_sigma):
        self.x = np.r_[p, v].astype(float)
        self.P = np.diag([pos_sigma ** 2] * 2 + [vel_sigma ** 2] * 2)
        self.q = accel_sigma ** 2

    def predict(self, dt):
        F = np.eye(4)
        F[0, 2] = F[1, 3] = dt
        G = np.array([[dt * dt / 2, 0], [0, dt * dt / 2], [dt, 0], [0, dt]])
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + self.q * G @ G.T

    def update(self, z, sigma):
        H = np.zeros((2, 4))
        H[0, 0] = H[1, 1] = 1
        S = H @ self.P @ H.T + np.eye(2) * sigma ** 2
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ (z - H @ self.x)
        self.P = (np.eye(4) - K @ H) @ self.P


class GorizontCR(Navigator):
    """Clean-room, from the GORIZONT README (step description and the flag reference table).

    Not reproduced: the offline stages (RTS smoothing, final fix, --refit), because the bench
    scores causal estimates. The README gives penalty weights without units; here each penalty
    term is normalised to [0, 1] by its search range. The local translation grid uses a 2 px
    step inside the 10 px radius (README default step is 10 px, i.e. a 3x3 grid).
    """
    name = "gorizont_cr"
    WS = 200
    BOOTSTRAP_PERIOD = 200
    LOCAL_PERIOD = 50
    MAX_HISTORY = 300
    MIN_ROUGH_BOOT = 4.0
    MIN_ROUGH_LOCAL = 1.0
    BOOT_AZ_STEP = 5.0
    BOOT_SPEED_STEP_PX = 0.2
    SPEED_RANGE = (5.0, 60.0)        # README default max is 45 m/s; bench flights go to 55 m/s
    BOOT_RADIUS_PX = 8
    BOOT_GRID_PX = 4
    LOCAL_RADIUS_PX = 10
    LOCAL_GRID_PX = 2
    THETAS = np.array([-8.0, -4.0, 0.0, 4.0, 8.0])
    ENDPOINT_GATE_PX = 35.0
    MIN_CORR_BOOT = 0.65
    MIN_CORR_LOCAL = 0.55
    TOP_CANDIDATES = 6
    MAX_HYP = 8
    NMS_PX = 8.0
    W_CORR, P_OFFSET, P_THETA, P_RANK, P_INNOV = 1.0, 0.03, 0.03, 0.04, 0.20
    P_FLAT, P_NOCAND = 0.01, 0.1
    INIT_POS_SIGMA_PX, INIT_VEL_SIGMA, ACCEL_SIGMA = 3.0, 3.0, 0.05
    MEAS_SIGMA_PX = (1.0, 25.0)
    RADAR_MEDIAN = 3                 # README: --radar-median 3
    RADAR_CUTOFF_HZ = 3.0            # README: --radar-cutoff 3.0, first-order low-pass here
    MATCH_PTS = 100
    SCORE_DECAY = 0.9
    BOOT_CHUNK = 2000
    TRACK_CAP = 8192

    def __init__(self, dem, res, prior, speed_range=None, az_window_deg=180.0):
        super().__init__(dem, res, prior)
        self.az_window = az_window_deg      # README flag --initial-az-window-deg, default 180 = full circle
        if speed_range is not None:
            self.SPEED_RANGE = speed_range
        self.start = np.array([prior["e0"], prior["n0"]])
        self.hint_v = prior["speed_mps"] * unit(prior["heading_deg"])
        self.buf_t, self.buf_h = [], []
        self.raw = []
        self.lp = None
        self.hyps = None
        self.next_boot = self.WS
        r = self.LOCAL_RADIUS_PX
        g = np.arange(-r, r + 1, self.LOCAL_GRID_PX) * res
        gx, gy = np.meshgrid(g, g)
        self.loc_offs = np.column_stack([gx.ravel(), gy.ravel()])

    @staticmethod
    def rough(h):
        x = np.arange(len(h))
        return float(np.std(h - np.polyval(np.polyfit(x, h, 1), x))) if len(h) > 2 else 0.0

    def _bootstrap(self):
        t = np.array(self.buf_t)
        h = np.array(self.buf_h)
        if self.rough(h) < self.MIN_ROUGH_BOOT:
            return
        sel = np.linspace(0, len(t) - 1, min(len(t), 2 * self.MATCH_PTS)).astype(int)
        ts, hs = t[sel] - t[0], h[sel]
        res = self.res
        if self.az_window >= 180:
            azs = np.arange(0, 360, self.BOOT_AZ_STEP)
        else:
            azs = (self.prior["heading_deg"]
                   + np.arange(-self.az_window, self.az_window + 1e-9, self.BOOT_AZ_STEP)) % 360
        speeds = np.arange(self.SPEED_RANGE[0], self.SPEED_RANGE[1] + 1e-9, self.BOOT_SPEED_STEP_PX * res)
        g = np.arange(-self.BOOT_RADIUS_PX, self.BOOT_RADIUS_PX + 1, self.BOOT_GRID_PX) * res
        gx, gy = np.meshgrid(g, g)
        offs = np.column_stack([gx.ravel(), gy.ravel()])
        A, S, O = np.meshgrid(np.arange(len(azs)), np.arange(len(speeds)), np.arange(len(offs)), indexing="ij")
        A, S, O = A.ravel(), S.ravel(), O.ravel()
        dirs = np.stack([unit(a) for a in azs])
        c = np.empty(len(A))
        for k0 in range(0, len(A), self.BOOT_CHUNK):
            a, sp, o = A[k0:k0 + self.BOOT_CHUNK], S[k0:k0 + self.BOOT_CHUNK], O[k0:k0 + self.BOOT_CHUNK]
            pe = self.start[0] + offs[o, :1] + dirs[a, :1] * speeds[sp, None] * ts[None, :]
            pn = self.start[1] + offs[o, 1:] + dirs[a, 1:] * speeds[sp, None] * ts[None, :]
            ref = bilinear(self.dem, pe, pn, res, fill=np.nan)
            c[k0:k0 + self.BOOT_CHUNK] = np.where(np.isnan(ref).any(1), -1.0, ncc(hs[None, :], np.nan_to_num(ref)))
        order = np.argsort(-c)
        hyps = []
        for i in order:
            if c[i] < self.MIN_CORR_BOOT or len(hyps) >= self.TOP_CANDIDATES:
                break
            v = speeds[S[i]] * dirs[A[i]]
            p_end = self.start + offs[O[i]] + v * (t[-1] - t[0])
            if any(np.linalg.norm(p_end - hh["kf"].x[:2]) < self.NMS_PX * res for hh in hyps):
                continue
            kf = _KF(p_end, v, self.INIT_POS_SIGMA_PX * res, self.INIT_VEL_SIGMA, self.ACCEL_SIGMA * res)
            track = np.zeros((self.TRACK_CAP, 2))
            track[:len(t)] = (self.start + offs[O[i]])[None, :] + np.outer(t - t[0], v)
            hyps.append({"kf": kf, "track": track, "k": len(t), "score": float(c[i]), "t": t[-1]})
        if hyps:
            self.hyps = hyps

    def _local(self, hyp, t, h):
        n = min(len(t), self.MAX_HISTORY)
        k = hyp["k"]
        tw, hw, tr = t[-n:], h[-n:], hyp["track"][k - n:k]
        if self.rough(hw) < self.MIN_ROUGH_LOCAL:
            hyp["score"] = self.SCORE_DECAY * hyp["score"] - self.P_FLAT
            return
        sel = np.linspace(0, n - 1, min(n, self.MATCH_PTS)).astype(int)
        pred = hyp["kf"].x[:2]
        rel = tr[sel] - tr[-1]
        best = None
        cands = []
        for th in self.THETAS:
            a = np.radians(th)
            R = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
            rot = rel @ R.T + pred
            pe = rot[:, 0][None, :] + self.loc_offs[:, :1]
            pn = rot[:, 1][None, :] + self.loc_offs[:, 1:]
            ref = bilinear(self.dem, pe, pn, self.res, fill=np.nan)
            c = np.where(np.isnan(ref).any(1), -1.0, ncc(hw[sel][None, :], np.nan_to_num(ref)))
            for j in np.argsort(-c)[:self.TOP_CANDIDATES]:
                cands.append((c[j], th, j))
        cands.sort(key=lambda x: -x[0])
        gate = self.ENDPOINT_GATE_PX * self.res
        rmax = np.hypot(self.LOCAL_RADIUS_PX, self.LOCAL_RADIUS_PX) * self.res
        for rank, (c, th, j) in enumerate(cands[:self.TOP_CANDIDATES]):
            if c < self.MIN_CORR_LOCAL:
                continue
            off = np.linalg.norm(self.loc_offs[j])
            if off > gate:
                continue
            score = (self.W_CORR * c - self.P_OFFSET * off / rmax - self.P_THETA * abs(th) / self.THETAS.max()
                     - self.P_RANK * rank / self.TOP_CANDIDATES - self.P_INNOV * off / gate)
            if best is None or score > best[0]:
                best = (score, c, th, j)
        if best is None:
            hyp["score"] = self.SCORE_DECAY * hyp["score"] - self.P_NOCAND
            self.stats["fixes_rejected"] += 1
            return
        score, c, th, j = best
        q = np.clip((c - self.MIN_CORR_LOCAL) / (1 - self.MIN_CORR_LOCAL), 0, 1)
        sig = (self.MEAS_SIGMA_PX[1] + q * (self.MEAS_SIGMA_PX[0] - self.MEAS_SIGMA_PX[1])) * self.res
        z = pred + self.loc_offs[j]
        hyp["kf"].update(z, sig)
        a = np.radians(th)
        R = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
        full = (tr - tr[-1]) @ R.T + hyp["kf"].x[:2]
        hyp["track"][k - n:k] = full
        hyp["score"] = self.SCORE_DECAY * hyp["score"] + score
        self.stats["fixes_accepted"] += 1

    def _prune(self):
        self.hyps.sort(key=lambda hh: -hh["score"])
        kept = []
        for hh in self.hyps:
            if all(np.linalg.norm(hh["kf"].x[:2] - k["kf"].x[:2]) >= self.NMS_PX * self.res for k in kept):
                kept.append(hh)
        self.hyps = kept[:self.MAX_HYP]

    def _prefilter(self, t, h):
        self.raw.append(h)
        m = float(np.median(self.raw[-self.RADAR_MEDIAN:]))
        if self.lp is None:
            self.lp = m
        else:
            dt = max(t - self.buf_t[-1], 1e-3)
            a = np.exp(-2 * np.pi * self.RADAR_CUTOFF_HZ * dt)
            self.lp = a * self.lp + (1 - a) * m
        return self.lp

    def update(self, t, h):
        h = self._prefilter(t, h)
        self.buf_t.append(t)
        self.buf_h.append(h)
        n = len(self.buf_t)
        if self.hyps is None:
            if n >= self.next_boot:
                self.next_boot += self.BOOTSTRAP_PERIOD
                self._bootstrap()
            if self.hyps is None:
                return self.start + self.hint_v * (t - self.t0)
            return self.hyps[0]["kf"].x[:2].copy()
        for hh in self.hyps:
            hh["kf"].predict(t - hh["t"])
            hh["t"] = t
            if hh["k"] == len(hh["track"]):
                hh["track"] = np.vstack([hh["track"], np.zeros_like(hh["track"])])
            hh["track"][hh["k"]] = hh["kf"].x[:2]
            hh["k"] += 1
        if n % self.LOCAL_PERIOD == 0:
            ta = np.array(self.buf_t)
            ha = np.array(self.buf_h)
            for hh in self.hyps:
                self._local(hh, ta, ha)
            self._prune()
        best = max(self.hyps, key=lambda hh: hh["score"])
        return best["kf"].x[:2].copy()


NAVIGATORS = {
    "dr_hint": DeadReckonHint,
    "tercom_ours": TercomBaseline,
    "pf_ours": ParticleFilter,
    "gagarin_cr": GagarinCR,
    "gagarin_cr_az200": lambda d, r, p: GagarinCR(d, r, p, az_init_samples=200),
    "gorizont_cr": GorizontCR,
    "gagarin_cr_hint": lambda d, r, p: GagarinCR(d, r, p, az_init_samples=200, az_window_deg=20.0),
    "gorizont_cr_hint": lambda d, r, p: GorizontCR(d, r, p, az_window_deg=20.0),
    "tercom_ours_beam": lambda d, r, p: _beam(TercomBaseline, "tercom_ours_beam", d, r, p),
    "pf_ours_beam": lambda d, r, p: _beam(ParticleFilter, "pf_ours_beam", d, r, p),
}


def _beam(cls, name, dem, res, prior):
    nav = cls(beam_map(dem, res, prior["flight_msl_m"]), res, prior)
    nav.name = name
    return nav
