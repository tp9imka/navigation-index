"""Heuristic GNSS jamming / spoofing scorer over receiver telemetry epochs. Stdlib only.

Feed one Epoch per navigation epoch (typically 1 Hz), including epochs without a fix. Every
field except `t` is optional, so the scorer works with whatever a receiver exposes.

Four kinds of detector:
- instantaneous rules (C/N0, AGC, jamInd, receiver flags, clock, position and velocity jumps,
  decoded ephemerides that disagree with an independent broadcast source);
- power CUSUMs: the median per-SV C/N0 deviation from a robust per-SV baseline, and the AGC
  deviation, so a staircase of steps each under the instantaneous thresholds still accumulates;
- consistency detectors with CUSUM memory: position vs a reference track (IMU / odometry velocity
  in `ref_vel_e/ref_vel_n`; else the receiver's own reported velocity integrated, which keeps
  normal driving consistent; else a constant-velocity prior), GNSS Doppler velocity vs an
  external reference, and receiver clock rate vs its learned rate plus an oscillator wander allowance;
- lost fix after a fix was held (denial is a signal too).

Any alert latches the alarm (`Assessment.alarm`); it clears only after CLEAR_EPOCHS
consecutive epochs that pass every clear condition, or on `acknowledge()`.

Thresholds are starting points for a hackathon, not certified detection limits: tune them on
recordings from your own antenna and platform.
"""

from __future__ import annotations

import math
import statistics
from collections import deque
from dataclasses import dataclass, field

BASELINE_MIN_EPOCHS = 10
BASELINE_ALPHA = 0.1  # EWMA weight for learning epochs
BASELINE_MAX_SCORE = 0.2  # alarm clear condition: both scores at or below this
CN0_INNOV_CLIP_DB = 3.0  # per-SV baseline innovation clip: one bad epoch moves a baseline at most 0.3 dB
# While the C/N0 evidence holds (jamming hit, or the CUSUM at half an alarm) a baseline may still
# fall at this rate x the clipped innovation, i.e. at most ~0.9 dB/min: a moving platform's sky
# changes, and a frozen baseline would otherwise go stale and hold the alarm for good.
CN0_FROZEN_ALPHA = 0.005

CN0_DROP_DB = 6.0
CN0_DROP_SV_FRACTION = 0.75
CN0_RISE_DB = 4.0
CN0_UNIFORM_SD_DB = 2.0
CN0_UNIFORM_MIN_SVS = 6
AGC_REL_CHANGE = 0.20
JAM_IND_HIGH = 100  # MON-RF jamInd (CW indicator) is 0..255; u-blox gives no fixed cut-off
CLOCK_JUMP_NS = 1000.0  # ~300 m of range
MAX_SPEED_MPS = 100.0  # set per platform: pedestrian ~5, car ~70, UAV ~60, airliner ~300
MAX_ACCEL_MPS2 = 10.0  # reported-velocity change limit, ~1 g: hard braking or a tight turn at speed
VEL_JUMP_MAX_DT_S = 2.0  # only consecutive fixes this close are compared
RX_FLAG_ALERT_STATE = 2  # spoofDetState / jammingState >= 2 means "indicated" / "warning"
EPH_MISMATCH_M = 50.0  # two valid broadcasts for the same SV and time agree to a few metres

# Power CUSUMs. The C/N0 statistic is the median over SVs of (C/N0 - per-SV baseline); SVs lost
# since the baseline count as having fallen to CN0_LOST_DBHZ. Tuned on the 3 tuning logs only
# (see README "Real-data evaluation").
CN0_CUSUM_K = 1.5  # sigmas
CN0_SIGMA_FLOOR_DB = 1.0
CN0_LOST_DBHZ = 20.0
CN0_STEP_MIN_SVS = 4
AGC_CUSUM_K = 1.0
AGC_SIGMA_FLOOR_REL = 0.02

# CUSUM on normalized residuals: S = clip(S + z - K, 0, CAP); hit while S >= H and z >= K.
CUSUM_K = 2.0  # per-axis sigmas; a clean 2-D residual magnitude exceeds 2 sigma ~13 % of epochs
CUSUM_K_SIGNED = 0.5  # for zero-mean signed residuals (clock rate), tuned to a 1-sigma shift
CUSUM_H = 8.0
CUSUM_CAP = 2 * CUSUM_H  # bounds recovery time once the residual is back inside K
REF_GATE_SIGMA = 3.0  # residuals above this never pull the reference toward the fix
# References and noise estimates stop learning while their CUSUM holds half an alarm's worth of
# evidence, so a slow drag cannot teach the detector that the drag is normal. Gating at S == 0
# instead truncates the noise estimate and talks it down into false alarms.
CUSUM_LEARN_MAX = CUSUM_H / 2

POS_SIGMA_FLOOR_M = 2.0
POS_ALPHA = 0.1  # reference position pull toward the fix on learning epochs (constant-velocity prior)
EXT_POS_ALPHA = 0.02  # same with an external velocity reference: slower pull, harder to drag along
NOISE_INFLATION_MAX = 2.0  # learned noise sigmas may grow at most this much after arming
CV_WINDOW = 30  # constant-velocity prior: least-squares slope over this many learning fixes
CV_MIN_POINTS = 5
REF_VEL_SIGMA_MPS = 0.05  # error of an external velocity reference (IMU/odometry), grows position error while frozen
DOPPLER_WINDOW_S = 10.0  # reported-velocity mode: fix displacement vs integrated velocity over this window
DOPPLER_RES_SIGMA_FLOOR_M = 1.0
DOPPLER_WARMUP = 20  # residuals learned unconditionally before the doppler check arms
DOPPLER_REL_VEL_SIGMA = 0.02  # reported velocity error as a fraction of speed (heading, time tagging)
CV_VEL_SIGMA_MPS = 1.0  # same for the learned constant-velocity prior
VEL_SIGMA_FLOOR_MPS = 0.2

CLOCK_RATE_SIGMA_FLOOR_NS_S = 2.0
OSC_WANDER_NS_S2 = 0.1  # TCXO at steady temperature; thermal transients need several times more

MAX_EPOCH_GAP_S = 3.0  # a telemetry gap this long counts as lost fix
CLEAR_EPOCHS = 10
CLEAR_SIGMA = 3.0  # consistency and power residuals must be back inside this for CLEAR_EPOCHS in a row

ALERT_SCORE = 0.5
EARTH_RADIUS_M = 6371000.0

JAM_WEIGHTS = {"cn0_drop": 0.5, "cn0_step": 0.5, "agc_change": 0.3, "agc_step": 0.3,
               "jam_ind": 0.3, "rx_jam_flag": 0.6}
SPOOF_WEIGHTS = {"cn0_uniform": 0.35, "cn0_rise": 0.3, "clock_jump": 0.35,
                 "position_jump": 0.35, "vel_jump": 0.35, "rx_spoof_flag": 0.6, "eph_mismatch": 0.6,
                 "pos_drift": 0.6, "vel_mismatch": 0.6, "clock_drift": 0.5}
LOST_FIX = "lost_fix"


@dataclass
class Epoch:
    t: float
    cn0: dict[str, float] | None = field(default_factory=dict)  # sv id -> C/N0 dB-Hz; None = not reported
    agc_cnt: float | None = None
    jam_ind: float | None = None
    clk_bias_ns: float | None = None
    clk_drift_ns_s: float | None = None
    lat: float | None = None
    lon: float | None = None
    spoof_det_state: int | None = None
    jamming_state: int | None = None
    fix_ok: bool | None = None  # None => inferred from lat/lon presence
    vel_e: float | None = None  # GNSS (Doppler) velocity, m/s
    vel_n: float | None = None
    ref_vel_e: float | None = None  # independent reference velocity (IMU/odometry/known static), m/s
    ref_vel_n: float | None = None
    hdop: float | None = None  # scales the learned position / velocity noise when given
    # sv id -> disagreement (m) of the receiver-decoded ephemeris vs an independent broadcast source
    # (ephemeris_check.py); SVs without both are absent, None = not measured at all
    eph_mismatch_m: dict[str, float] | None = None

    @property
    def has_fix(self) -> bool:
        if self.fix_ok is not None:
            return self.fix_ok and self.lat is not None and self.lon is not None
        return self.lat is not None and self.lon is not None


@dataclass
class Alert:
    detector: str
    family: str  # jamming | spoofing | lost-fix
    value: float
    threshold: float
    unit: str
    message: str
    evidence: dict = field(default_factory=dict)


@dataclass
class AlarmState:
    active: bool = False
    since_t: float | None = None
    families: list[str] = field(default_factory=list)
    causes: dict[str, float] = field(default_factory=dict)  # detector -> first t since raise
    quiet_epochs: int = 0
    cleared_t: float | None = None
    clear_reason: str | None = None

    def snapshot(self) -> AlarmState:
        return AlarmState(self.active, self.since_t, list(self.families), dict(self.causes),
                          self.quiet_epochs, self.cleared_t, self.clear_reason)


@dataclass
class Assessment:
    t: float
    jam_score: float
    spoof_score: float
    reasons: list[str]
    alerts: list[Alert] = field(default_factory=list)
    lost_fix: bool = False
    alarm: AlarmState = field(default_factory=AlarmState)

    @property
    def families(self) -> list[str]:
        out = []
        if self.jam_score >= ALERT_SCORE:
            out.append("jamming")
        if self.spoof_score >= ALERT_SCORE:
            out.append("spoofing")
        if self.lost_fix:
            out.append("lost-fix")
        return out

    @property
    def verdict(self) -> str:
        return "+".join(self.families) or "clean"


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


class Cusum:
    def __init__(self, k: float = CUSUM_K):
        self.k = k
        self.s = 0.0

    def update(self, z: float, weight: float = 1.0) -> bool:
        """weight < 1 for residuals that overlap in time (one independent sample per 1/weight epochs). Only
        the accumulation is weighted: correlated residuals inflate evidence, the decay stays at full speed."""
        inc = z - self.k
        self.s = min(CUSUM_CAP, max(0.0, self.s + (weight * inc if inc > 0 else inc)))
        return self.s >= CUSUM_H and z >= self.k


class NoiseVar:
    """EWMA variance; once the detector is armed it may not grow past NOISE_INFLATION_MAX^2 x the armed value."""

    def __init__(self, floor_sigma: float, hard_floor: bool = False):
        self.floor = floor_sigma if hard_floor else 0.0
        self.var = floor_sigma ** 2
        self.cap: float | None = None

    @property
    def sigma(self) -> float:
        return max(self.floor, math.sqrt(self.var))

    def learn(self, sample_var: float, armed: bool):
        if armed and self.cap is None:
            self.cap = self.var * NOISE_INFLATION_MAX ** 2
        self.var += BASELINE_ALPHA * (sample_var - self.var)
        if self.cap is not None:
            self.var = min(self.var, self.cap)


class PositionConsistency:
    """Position vs the best motion reference available, in local metres.

    - external (`ref_vel_*`, IMU / odometry / known static): a reference track integrated from that
      velocity, frozen while the residual is suspect, so a slow drag accumulates against it;
    - doppler (receiver-reported `vel_*` only): fix displacement over the last DOPPLER_WINDOW_S vs
      the integral of the reported velocity over the same window. Real driving (turns, stop-go)
      is consistent by construction; a position jump or pull that the velocity does not show is
      not. Windowed, so one bad stretch (e.g. a jammed fix) cannot leave a stale reference behind.
      A spoofer that keeps position and Doppler coherent is invisible here: that needs an external
      reference;
    - cv-prior (neither): a constant-velocity track, least-squares slope over the last learning fixes."""

    def __init__(self):
        self.origin: tuple[float, float] | None = None
        self.pos: list[float] | None = None
        self.vel = [0.0, 0.0]
        self.t: float | None = None
        self.noise = NoiseVar(POS_SIGMA_FLOOR_M)  # per-axis fix noise per unit HDOP
        self.vel_noise = NoiseVar(VEL_SIGMA_FLOOR_MPS)
        self.window: deque = deque(maxlen=CV_WINDOW)
        self.updates = 0
        self.frozen_s = 0.0
        self.pos_cusum, self.vel_cusum = Cusum(), Cusum()
        self.last_z = 0.0
        self.last_vz = 0.0
        self.mode: str | None = None
        self.odo = [0.0, 0.0]  # integrated reported velocity (doppler mode)
        self.hist: deque = deque()  # (t, fix, odo) over the doppler window
        self.dop_noise = NoiseVar(DOPPLER_RES_SIGMA_FLOOR_M, hard_floor=True)
        self.dop_learned = 0

    def _enu(self, ep):
        lat0, lon0 = self.origin
        k = math.pi / 180.0 * EARTH_RADIUS_M
        return [(ep.lon - lon0) * k * math.cos(math.radians(lat0)), (ep.lat - lat0) * k]

    def reset(self):
        self.pos = None
        self.window.clear()
        self.hist.clear()
        self.odo = [0.0, 0.0]
        self.updates = 0
        self.frozen_s = 0.0
        self.pos_cusum, self.vel_cusum = Cusum(), Cusum()
        self.last_z = self.last_vz = 0.0

    def _cv_velocity(self):
        if len(self.window) < CV_MIN_POINTS:
            return [0.0, 0.0]
        ts = [w[0] for w in self.window]
        tm = sum(ts) / len(ts)
        den = sum((t - tm) ** 2 for t in ts)
        out = []
        for i in (1, 2):
            xm = sum(w[i] for w in self.window) / len(self.window)
            out.append(sum((w[0] - tm) * (w[i] - xm) for w in self.window) / den if den else 0.0)
        return out

    @staticmethod
    def _mode(ep) -> str:
        if ep.ref_vel_e is not None and ep.ref_vel_n is not None:
            return "external"
        if ep.vel_e is not None and ep.vel_n is not None:
            return "doppler"
        return "cv-prior"

    def _velocity(self, ep, mode):
        if mode == "external":
            return [ep.ref_vel_e, ep.ref_vel_n]
        if mode == "doppler":
            return [ep.vel_e, ep.vel_n]
        return self._cv_velocity()

    def _step_doppler(self, ep, fix, armed, may_learn, hits, alerts):
        v = [ep.vel_e, ep.vel_n]
        dt = ep.t - self.t if self.t is not None else None
        # A discontinuity is position_jump's to report and starts a new segment: the window and its CUSUM
        # restart from the new fix (evidence from before the jump is already in the latched alarm).
        jumped = "position_jump" in hits
        if self.mode != "doppler" or dt is None or dt > MAX_EPOCH_GAP_S or jumped:
            self.hist.clear()
            self.odo = [0.0, 0.0]
            if jumped:
                self.pos_cusum = Cusum()
        elif dt > 0:
            self.odo = [self.odo[i] + 0.5 * (self.vel[i] + v[i]) * dt for i in range(2)]
        if dt is not None and dt <= 0:
            return
        self.pos, self.vel, self.t, self.mode, self.frozen_s = fix, v, ep.t, "doppler", 0.0
        self.window.clear()
        while len(self.hist) > 1 and self.hist[1][0] <= ep.t - DOPPLER_WINDOW_S:
            self.hist.popleft()
        self.hist.append((ep.t, fix, list(self.odo)))
        t0, f0, o0 = self.hist[0]
        if ep.t - t0 < DOPPLER_WINDOW_S:
            self.last_z = 0.0
            return
        d = [(fix[i] - f0[i]) - (self.odo[i] - o0[i]) for i in range(2)]
        r = math.hypot(*d)
        travel = math.hypot(self.odo[0] - o0[0], self.odo[1] - o0[1])
        sigma = math.hypot(self.dop_noise.sigma, DOPPLER_REL_VEL_SIGMA * travel)
        z = r / sigma
        self.last_vz = 0.0
        armed = armed and self.dop_learned >= DOPPLER_WARMUP
        self.last_z = z if armed else 0.0
        if armed and self.pos_cusum.update(z, min(1.0, dt / DOPPLER_WINDOW_S)):
            hits.add("pos_drift")
            alerts.append(Alert("pos_drift", "spoofing", r, CUSUM_K * sigma, "m",
                                f"fix moved {r:.0f} m differently from its own reported velocity over "
                                f"{ep.t - t0:.0f} s ({z:.1f} sigma, CUSUM {self.pos_cusum.s:.1f})",
                                {"residual_m": round(r, 1), "sigma_m": round(sigma, 1),
                                 "cusum": round(self.pos_cusum.s, 1), "window_s": round(ep.t - t0, 1),
                                 "reference": "doppler"}))
        if may_learn and z < REF_GATE_SIGMA and self.pos_cusum.s < CUSUM_LEARN_MAX or not armed:
            self.dop_noise.learn(max(0.0, r * r - (DOPPLER_REL_VEL_SIGMA * travel) ** 2) / 2, armed)
            self.dop_learned += 1

    def step(self, ep: Epoch, armed: bool, may_learn: bool, hits, alerts):
        if self.origin is None:
            self.origin = (ep.lat, ep.lon)
        fix = self._enu(ep)
        mode = self._mode(ep)
        if mode == "doppler":
            self._step_doppler(ep, fix, armed, may_learn, hits, alerts)
            return
        ext = mode == "external"
        scale = ep.hdop if ep.hdop else 1.0
        if self.pos is None:
            self.pos, self.t, self.mode = fix, ep.t, mode
            self.vel = self._velocity(ep, mode) if mode != "cv-prior" else [0.0, 0.0]
            self.window.append((ep.t, *fix))
            return
        dt = ep.t - self.t
        self.t = ep.t
        if dt <= 0:
            return
        prev_vel = self.vel
        self.vel = self._velocity(ep, mode)
        self.mode = mode
        pred = [self.pos[i] + 0.5 * (prev_vel[i] + self.vel[i]) * dt for i in range(2)]
        d = [fix[i] - pred[i] for i in range(2)]
        r = math.hypot(*d)
        vel_sigma = REF_VEL_SIGMA_MPS if ext else CV_VEL_SIGMA_MPS
        fix_sigma = max(POS_SIGMA_FLOOR_M, self.noise.sigma * scale)
        sigma = math.hypot(fix_sigma, vel_sigma * self.frozen_s)
        z = r / sigma
        self.last_z = z
        if armed and self.pos_cusum.update(z):
            hits.add("pos_drift")
            alerts.append(Alert("pos_drift", "spoofing", r, CUSUM_K * sigma, "m",
                                f"position {r:.0f} m off {mode} reference track ({z:.1f} sigma, "
                                f"CUSUM {self.pos_cusum.s:.1f})",
                                {"residual_m": round(r, 1), "sigma_m": round(sigma, 1),
                                 "cusum": round(self.pos_cusum.s, 1), "frozen_s": round(self.frozen_s, 1),
                                 "reference": mode, "ref_vel_mps": [round(v, 2) for v in self.vel]}))
        if ext and ep.vel_e is not None and ep.vel_n is not None:
            vr = math.hypot(ep.vel_e - ep.ref_vel_e, ep.vel_n - ep.ref_vel_n)
            vsig = max(VEL_SIGMA_FLOOR_MPS, self.vel_noise.sigma * scale)
            vz = vr / vsig
            self.last_vz = vz
            if armed and self.vel_cusum.update(vz):
                hits.add("vel_mismatch")
                alerts.append(Alert("vel_mismatch", "spoofing", vr, CUSUM_K * vsig, "m/s",
                                    f"GNSS velocity {vr:.1f} m/s off reference ({vz:.1f} sigma)",
                                    {"residual_mps": round(vr, 2), "sigma_mps": round(vsig, 2),
                                     "cusum": round(self.vel_cusum.s, 1)}))
            if may_learn and vz < REF_GATE_SIGMA and self.vel_cusum.s < CUSUM_LEARN_MAX or not armed:
                self.vel_noise.learn((vr / scale) ** 2 / 2, armed)
        else:
            self.last_vz = 0.0
        if may_learn and z < REF_GATE_SIGMA and self.pos_cusum.s < CUSUM_LEARN_MAX or not armed:
            alpha = max(EXT_POS_ALPHA if ext else POS_ALPHA, 1.0 / (self.updates + 2))
            self.pos = [pred[i] + alpha * d[i] for i in range(2)]
            self.noise.learn((r / scale) ** 2 / 2, armed)
            self.window.append((ep.t, *fix))
            self.updates += 1
            self.frozen_s = 0.0
        else:
            self.pos = pred
            self.frozen_s += dt


class ClockConsistency:
    """Receiver clock rate (reported drift or differenced bias) vs its learned rate."""

    def __init__(self):
        self.prev: tuple[float, float] | None = None
        self.rate: float | None = None
        self.noise = NoiseVar(CLOCK_RATE_SIGMA_FLOOR_NS_S)
        self.frozen_s = 0.0
        self.up, self.down = Cusum(CUSUM_K_SIGNED), Cusum(CUSUM_K_SIGNED)
        self.last_z = 0.0

    def reset(self):
        self.up, self.down = Cusum(CUSUM_K_SIGNED), Cusum(CUSUM_K_SIGNED)
        self.frozen_s = 0.0
        self.last_z = 0.0

    def step(self, ep: Epoch, armed: bool, may_learn: bool, jumped: bool, hits, alerts):
        if ep.clk_bias_ns is None and ep.clk_drift_ns_s is None:
            return
        meas = ep.clk_drift_ns_s
        if ep.clk_bias_ns is not None:
            if meas is None and self.prev is not None and ep.t > self.prev[0] and not jumped:
                meas = (ep.clk_bias_ns - self.prev[1]) / (ep.t - self.prev[0])
            dt = ep.t - self.prev[0] if self.prev else 0.0
            self.prev = (ep.t, ep.clk_bias_ns)
        else:
            dt = 1.0
        if meas is None:
            return
        if self.rate is None:
            self.rate = meas
            return
        res = meas - self.rate
        sigma = math.hypot(self.noise.sigma, OSC_WANDER_NS_S2 * self.frozen_s)
        z = res / sigma
        self.last_z = abs(z)
        if armed:
            hit = self.up.update(z) or self.down.update(-z)
            if hit:
                hits.add("clock_drift")
                alerts.append(Alert("clock_drift", "spoofing", res, CUSUM_K_SIGNED * sigma, "ns/s",
                                    f"clock rate {meas:+.1f} ns/s vs learned {self.rate:+.1f} ns/s "
                                    f"({z:+.1f} sigma)",
                                    {"rate_ns_s": round(meas, 1), "expected_ns_s": round(self.rate, 1),
                                     "sigma_ns_s": round(sigma, 1),
                                     "cusum": round(max(self.up.s, self.down.s), 1)}))
        if may_learn and abs(z) < REF_GATE_SIGMA and max(self.up.s, self.down.s) < CUSUM_LEARN_MAX or not armed:
            self.rate += BASELINE_ALPHA * res
            self.noise.learn(max(res * res, CLOCK_RATE_SIGMA_FLOOR_NS_S ** 2), armed)
            self.frozen_s = 0.0
        else:
            self.frozen_s += max(dt, 0.0)


class PowerBaseline:
    """Per-SV C/N0 and AGC baselines plus the power CUSUMs.

    Learning gate (decided per epoch by the scorer and here): no lost fix, no spoofing alert (a
    spoofer's power must not become the baseline), and the C/N0 evidence quiet (no jamming-family hit,
    CUSUM below CUSUM_LEARN_MAX). Spoofing sub-alerts such as `cn0_rise` alone do not stop learning,
    so a recovery after a slow decline is re-learned instead of freezing the baseline for good. While
    the C/N0 evidence holds, upward innovations still learn at the full rate (a recovered sky can
    clear the alarm) and downward ones at CN0_FROZEN_ALPHA. Each per-SV innovation is clipped to
    +-CN0_INNOV_CLIP_DB, so one outlier epoch cannot drag a baseline."""

    def __init__(self):
        self.cn0: dict[str, float] = {}
        self.agc: float | None = None
        self.epochs = 0
        self.cn0_noise = NoiseVar(CN0_SIGMA_FLOOR_DB, hard_floor=True)
        self.agc_noise = NoiseVar(AGC_SIGMA_FLOOR_REL, hard_floor=True)
        self.cn0_cusum = Cusum(CN0_CUSUM_K)
        self.agc_up, self.agc_down = Cusum(AGC_CUSUM_K), Cusum(AGC_CUSUM_K)
        self.last_dev: float | None = None
        self.last_agc_rel: float | None = None
        self.last_z = 0.0

    @property
    def ready(self) -> bool:
        return self.epochs >= BASELINE_MIN_EPOCHS

    def reset(self):
        self.__init__()

    def reset_cusums(self):
        self.cn0_cusum = Cusum(CN0_CUSUM_K)
        self.agc_up, self.agc_down = Cusum(AGC_CUSUM_K), Cusum(AGC_CUSUM_K)

    def median_deviation(self, cn0: dict[str, float] | None) -> tuple[float | None, int]:
        if cn0 is None or not self.cn0:
            return None, 0
        devs = [cn0[sv] - b if sv in cn0 else min(0.0, CN0_LOST_DBHZ - b) for sv, b in self.cn0.items()]
        if len(devs) < CN0_STEP_MIN_SVS:
            return None, len(devs)
        return statistics.median(devs), len(devs)

    def step(self, ep: Epoch, armed: bool, hits, alerts):
        self.last_dev, n = self.median_deviation(ep.cn0)
        zc = za = 0.0
        if self.last_dev is not None:
            zc = -self.last_dev / self.cn0_noise.sigma
            if armed and self.cn0_cusum.update(zc):
                hits.add("cn0_step")
                alerts.append(Alert("cn0_step", "jamming", self.last_dev, -CN0_CUSUM_K * self.cn0_noise.sigma, "dB",
                                    f"median C/N0 {self.last_dev:+.1f} dB vs per-SV baseline, accumulated "
                                    f"(CUSUM {self.cn0_cusum.s:.1f})",
                                    {"median_dev_db": round(self.last_dev, 1), "n_svs": n,
                                     "sigma_db": round(self.cn0_noise.sigma, 2),
                                     "cusum": round(self.cn0_cusum.s, 1)}))
        self.last_agc_rel = None
        if ep.agc_cnt is not None and self.agc:
            rel = (ep.agc_cnt - self.agc) / self.agc
            self.last_agc_rel = rel
            za = rel / self.agc_noise.sigma
            if armed and (self.agc_up.update(za) or self.agc_down.update(-za)):
                hits.add("agc_step")
                alerts.append(Alert("agc_step", "jamming", rel, AGC_CUSUM_K * self.agc_noise.sigma, "rel",
                                    f"AGC {rel:+.0%} vs baseline, accumulated "
                                    f"(CUSUM {max(self.agc_up.s, self.agc_down.s):.1f})",
                                    {"agc": ep.agc_cnt, "baseline": round(self.agc, 1),
                                     "cusum": round(max(self.agc_up.s, self.agc_down.s), 1)}))
        self.last_z = max(abs(zc), abs(za))

    def learn(self, ep: Epoch, armed: bool, jam_hit: bool):
        if ep.cn0 is None:
            return
        frozen = jam_hit or self.cn0_cusum.s >= CUSUM_LEARN_MAX
        for sv, c in ep.cn0.items():
            old = self.cn0.get(sv)
            if old is None:
                if not frozen:
                    self.cn0[sv] = c
                continue
            innov = max(-CN0_INNOV_CLIP_DB, min(CN0_INNOV_CLIP_DB, c - old))
            alpha = CN0_FROZEN_ALPHA if frozen and innov < 0 else BASELINE_ALPHA
            self.cn0[sv] = old + alpha * innov
        if frozen:
            return
        for sv in [sv for sv in self.cn0 if sv not in ep.cn0]:
            del self.cn0[sv]  # set or blocked SVs; a whole-sky loss never reaches here
        if self.last_dev is not None:
            self.cn0_noise.learn(self.last_dev ** 2, armed)
        if ep.agc_cnt is not None:
            old = self.agc
            if old is None:
                self.agc = ep.agc_cnt
            else:
                if self.last_agc_rel is not None:
                    self.agc_noise.learn(self.last_agc_rel ** 2, armed)
                self.agc = old + BASELINE_ALPHA * (ep.agc_cnt - old)
        self.epochs += 1


class InterferenceScorer:
    def __init__(self, max_speed_mps: float = MAX_SPEED_MPS, max_accel_mps2: float = MAX_ACCEL_MPS2):
        self.max_speed_mps = max_speed_mps
        self.max_accel_mps2 = max_accel_mps2
        self.power = PowerBaseline()
        self.prev: Epoch | None = None
        self.prev_fix: Epoch | None = None
        self.last_fix_t: float | None = None
        self.pos = PositionConsistency()
        self.clock = ClockConsistency()
        self.alarm = AlarmState()

    @property
    def base_cn0(self) -> dict[str, float]:
        return self.power.cn0

    @property
    def base_agc(self) -> float | None:
        return self.power.agc

    @property
    def clean_epochs(self) -> int:
        return self.power.epochs

    @property
    def baseline_ready(self) -> bool:
        return self.power.ready

    def acknowledge(self, t: float, relearn: bool = False) -> None:
        """Operator clear: re-anchor the references on the next fix; relearn=True also resets the C/N0/AGC baseline."""
        self.alarm = AlarmState(cleared_t=t, clear_reason="acknowledged")
        self.pos.reset()
        self.clock.reset()
        self.power.reset_cusums()
        if relearn:
            self.power.reset()

    def assess(self, ep: Epoch) -> Assessment:
        hits: set[str] = set()
        alerts: list[Alert] = []

        armed = self.baseline_ready
        if armed:
            self._check_cn0_vs_baseline(ep, hits, alerts)
            if ep.agc_cnt is not None and self.base_agc:
                rel = (ep.agc_cnt - self.base_agc) / self.base_agc
                if abs(rel) >= AGC_REL_CHANGE:
                    self._add(hits, alerts, "agc_change", rel, AGC_REL_CHANGE, "rel",
                              f"AGC {rel:+.0%} vs baseline", {"agc": ep.agc_cnt, "baseline": round(self.base_agc, 1)})
        self.power.step(ep, armed, hits, alerts)
        self._check_cn0_uniform(ep, hits, alerts)
        if ep.jam_ind is not None and ep.jam_ind >= JAM_IND_HIGH:
            self._add(hits, alerts, "jam_ind", ep.jam_ind, JAM_IND_HIGH, "", f"jamInd {ep.jam_ind:.0f}")
        if ep.jamming_state is not None and ep.jamming_state >= RX_FLAG_ALERT_STATE:
            self._add(hits, alerts, "rx_jam_flag", ep.jamming_state, RX_FLAG_ALERT_STATE, "",
                      f"receiver jammingState {ep.jamming_state}")
        if ep.spoof_det_state is not None and ep.spoof_det_state >= RX_FLAG_ALERT_STATE:
            self._add(hits, alerts, "rx_spoof_flag", ep.spoof_det_state, RX_FLAG_ALERT_STATE, "",
                      f"receiver spoofDetState {ep.spoof_det_state}")
        self._check_ephemeris(ep, hits, alerts)
        if self.prev is not None:
            self._check_clock_jump(self.prev, ep, hits, alerts)
        if self.prev_fix is not None and ep.has_fix:
            self._check_position_jump(self.prev_fix, ep, hits, alerts)
            self._check_velocity_jump(self.prev_fix, ep, hits, alerts)

        lost = self._check_lost_fix(ep, alerts)
        # Each reference is protected by its own detector's gates (residual < REF_GATE_SIGMA, CUSUM <
        # CUSUM_LEARN_MAX), not by the global alarm: freezing every reference on any alarm let one
        # detector's alarm make the others' references stale on a moving platform, and they then
        # kept each other latched.
        may_learn = not lost
        if ep.has_fix:
            self.pos.step(ep, armed, may_learn, hits, alerts)
        self.clock.step(ep, armed, may_learn, "clock_jump" in hits, hits, alerts)

        jam = min(1.0, sum(w for k, w in JAM_WEIGHTS.items() if k in hits))
        spoof = min(1.0, sum(w for k, w in SPOOF_WEIGHTS.items() if k in hits))
        result = Assessment(ep.t, jam, spoof, [a.message for a in alerts], alerts, lost)
        self._update_alarm(result, ep)
        result.alarm = self.alarm.snapshot()
        # Spoofing sub-alerts (cn0_rise alone) do not stop learning, so a recovered sky is re-learned; a
        # spoofing alert does, so a spoofer's power is not learned and its departure does not read as jamming.
        if not lost and result.spoof_score < ALERT_SCORE:
            self.power.learn(ep, armed, jam_hit=any(k in hits for k in JAM_WEIGHTS))
        self.prev = ep
        if ep.has_fix:
            self.prev_fix = ep
        return result

    @staticmethod
    def _add(hits, alerts, det, value, thr, unit, msg, evidence=None):
        hits.add(det)
        family = "jamming" if det in JAM_WEIGHTS else "spoofing"
        alerts.append(Alert(det, family, float(value), float(thr), unit, msg, evidence or {}))

    def _check_lost_fix(self, ep, alerts) -> bool:
        gap = ep.t - self.prev.t if self.prev is not None else 0.0
        if ep.has_fix:
            lost = gap > MAX_EPOCH_GAP_S and self.last_fix_t is not None
            if lost:
                alerts.append(Alert(LOST_FIX, "lost-fix", gap, MAX_EPOCH_GAP_S, "s",
                                    f"no epochs for {gap:.0f} s before this fix",
                                    {"gap_s": round(gap, 1)}))
            self.last_fix_t = ep.t
            return lost
        if self.last_fix_t is None:
            return False  # never had a fix: still acquiring, not a loss
        since = ep.t - self.last_fix_t
        tracked = "C/N0 not reported" if ep.cn0 is None else f"{len(ep.cn0)} SVs with C/N0"
        alerts.append(Alert(LOST_FIX, "lost-fix", since, 0.0, "s",
                            f"no fix for {since:.0f} s (last fix t={self.last_fix_t:.0f}, {tracked})",
                            {"since_last_fix_s": round(since, 1), "last_fix_t": self.last_fix_t,
                             "n_sv_tracked": None if ep.cn0 is None else len(ep.cn0)}))
        return True

    def _update_alarm(self, res: Assessment, ep: Epoch):
        al = self.alarm
        if res.families:
            if not al.active:
                self.alarm = al = AlarmState(active=True, since_t=ep.t)
            for f in res.families:
                if f not in al.families:
                    al.families.append(f)
            for a in res.alerts:
                al.causes.setdefault(a.detector, ep.t)
            al.quiet_epochs = 0
            return
        if not al.active:
            return
        quiet = (max(res.jam_score, res.spoof_score) <= BASELINE_MAX_SCORE and ep.has_fix
                 and max(self.pos.last_z, self.pos.last_vz, self.clock.last_z, self.power.last_z) < CLEAR_SIGMA)
        al.quiet_epochs = al.quiet_epochs + 1 if quiet else 0
        if al.quiet_epochs >= CLEAR_EPOCHS:
            self.alarm = AlarmState(cleared_t=ep.t, clear_reason=(
                f"{CLEAR_EPOCHS} epochs with scores <= {BASELINE_MAX_SCORE}, a fix, and "
                f"consistency and power residuals < {CLEAR_SIGMA} sigma"))
            self.pos.pos_cusum, self.pos.vel_cusum = Cusum(), Cusum()
            self.clock.up, self.clock.down = Cusum(CUSUM_K_SIGNED), Cusum(CUSUM_K_SIGNED)
            self.power.reset_cusums()

    def _check_cn0_vs_baseline(self, ep, hits, alerts):
        base = self.base_cn0
        if not base or ep.cn0 is None:
            return
        common = [sv for sv in ep.cn0 if sv in base]
        lost = [sv for sv in base if sv not in ep.cn0]
        deltas = [ep.cn0[sv] - base[sv] for sv in common]
        dropped = sum(1 for d in deltas if d <= -CN0_DROP_DB) + len(lost)
        frac = dropped / len(base)
        if frac >= CN0_DROP_SV_FRACTION:
            self._add(hits, alerts, "cn0_drop", frac, CN0_DROP_SV_FRACTION, "fraction of SVs",
                      f"C/N0 drop >= {CN0_DROP_DB:.0f} dB or lost on {dropped}/{len(base)} SVs",
                      {"dropped_or_lost": dropped, "baseline_svs": len(base)})
        if deltas and statistics.median(deltas) >= CN0_RISE_DB:
            med = statistics.median(deltas)
            self._add(hits, alerts, "cn0_rise", med, CN0_RISE_DB, "dB",
                      f"median C/N0 rise {med:+.1f} dB", {"n_common_svs": len(common)})

    def _check_cn0_uniform(self, ep, hits, alerts):
        values = list((ep.cn0 or {}).values())
        if len(values) >= CN0_UNIFORM_MIN_SVS:
            sd = statistics.pstdev(values)
            if sd < CN0_UNIFORM_SD_DB:
                self._add(hits, alerts, "cn0_uniform", sd, CN0_UNIFORM_SD_DB, "dB",
                          f"C/N0 spread only {sd:.1f} dB over {len(values)} SVs", {"n_svs": len(values)})

    def _check_ephemeris(self, ep, hits, alerts):
        if not ep.eph_mismatch_m:
            return
        tracked = ep.cn0.keys() if ep.cn0 else None  # a stale spoofed set of an SV no longer tracked is not current
        bad = {sv: m for sv, m in ep.eph_mismatch_m.items()
               if m >= EPH_MISMATCH_M and (tracked is None or sv in tracked)}
        if bad:
            worst = max(bad.values())
            self._add(hits, alerts, "eph_mismatch", worst, EPH_MISMATCH_M, "m",
                      f"decoded ephemeris of {len(bad)} SV(s) disagrees with the independent broadcast "
                      f"by up to {worst / 1000:.1f} km", {"svs": sorted(bad), "max_m": round(worst, 1)})

    def _check_clock_jump(self, prev, ep, hits, alerts):
        dt = ep.t - prev.t
        if dt <= 0 or prev.clk_bias_ns is None or ep.clk_bias_ns is None:
            return
        drift = prev.clk_drift_ns_s or 0.0
        residual = ep.clk_bias_ns - (prev.clk_bias_ns + drift * dt)
        if abs(residual) >= CLOCK_JUMP_NS:
            self._add(hits, alerts, "clock_jump", residual, CLOCK_JUMP_NS, "ns",
                      f"clock bias jump {residual:+.0f} ns")

    def _check_position_jump(self, prev, ep, hits, alerts):
        dt = ep.t - prev.t
        if dt <= 0:
            return
        speed = haversine_m(prev.lat, prev.lon, ep.lat, ep.lon) / dt
        if speed > self.max_speed_mps:
            self._add(hits, alerts, "position_jump", speed, self.max_speed_mps, "m/s",
                      f"implied speed {speed:.0f} m/s")

    def _check_velocity_jump(self, prev, ep, hits, alerts):
        dt = ep.t - prev.t
        if not 0 < dt <= VEL_JUMP_MAX_DT_S or None in (prev.vel_e, prev.vel_n, ep.vel_e, ep.vel_n):
            return
        acc = math.hypot(ep.vel_e - prev.vel_e, ep.vel_n - prev.vel_n) / dt
        if acc > self.max_accel_mps2:
            self._add(hits, alerts, "vel_jump", acc, self.max_accel_mps2, "m/s^2",
                      f"reported velocity changed at {acc:.0f} m/s^2")
