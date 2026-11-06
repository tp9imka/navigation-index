"""Heuristic GNSS jamming / spoofing scorer over receiver telemetry epochs. Stdlib only.

Feed one Epoch per navigation epoch (typically 1 Hz), including epochs without a fix. Every
field except `t` is optional, so the scorer works with whatever a receiver exposes.

Three kinds of detector:
- instantaneous rules (C/N0, AGC, jamInd, receiver flags, clock and position jumps);
- consistency detectors with CUSUM memory: position vs an independent reference (IMU / odometry
  velocity in `ref_vel_e/ref_vel_n`, or a constant-velocity prior learned on clean epochs),
  GNSS Doppler velocity vs that reference, and receiver clock rate vs its learned rate plus an
  oscillator wander allowance;
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
BASELINE_ALPHA = 0.1  # EWMA weight for clean epochs
BASELINE_MAX_SCORE = 0.2  # epochs scoring above this never update the baseline

CN0_DROP_DB = 6.0
CN0_DROP_SV_FRACTION = 0.75
CN0_RISE_DB = 4.0
CN0_UNIFORM_SD_DB = 2.0
CN0_UNIFORM_MIN_SVS = 6
AGC_REL_CHANGE = 0.20
JAM_IND_HIGH = 100  # MON-RF jamInd (CW indicator) is 0..255; u-blox gives no fixed cut-off
CLOCK_JUMP_NS = 1000.0  # ~300 m of range
MAX_SPEED_MPS = 100.0  # set per platform: pedestrian ~5, car ~70, UAV ~60, airliner ~300
RX_FLAG_ALERT_STATE = 2  # spoofDetState / jammingState >= 2 means "indicated" / "warning"

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
POS_ALPHA = 0.1  # reference position pull toward the fix on clean epochs (constant-velocity prior)
EXT_POS_ALPHA = 0.02  # same with an external velocity reference: slower pull, harder to drag along
NOISE_INFLATION_MAX = 2.0  # learned noise sigmas may grow at most this much after arming
CV_WINDOW = 30  # constant-velocity prior: least-squares slope over this many clean fixes
CV_MIN_POINTS = 5
REF_VEL_SIGMA_MPS = 0.05  # error of an external velocity reference (IMU/odometry), grows position error while frozen
CV_VEL_SIGMA_MPS = 1.0  # same for the learned constant-velocity prior (no external reference)
VEL_SIGMA_FLOOR_MPS = 0.2

CLOCK_RATE_SIGMA_FLOOR_NS_S = 2.0
OSC_WANDER_NS_S2 = 0.1  # TCXO at steady temperature; thermal transients need several times more

MAX_EPOCH_GAP_S = 3.0  # a telemetry gap this long counts as lost fix
CLEAR_EPOCHS = 10
CLEAR_SIGMA = 3.0  # consistency residuals must be back inside this for CLEAR_EPOCHS in a row

ALERT_SCORE = 0.5
EARTH_RADIUS_M = 6371000.0

JAM_WEIGHTS = {"cn0_drop": 0.5, "agc_change": 0.3, "jam_ind": 0.3, "rx_jam_flag": 0.6}
SPOOF_WEIGHTS = {"cn0_uniform": 0.35, "cn0_rise": 0.3, "clock_jump": 0.35,
                 "position_jump": 0.35, "rx_spoof_flag": 0.6,
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

    def update(self, z: float) -> bool:
        self.s = min(CUSUM_CAP, max(0.0, self.s + z - self.k))
        return self.s >= CUSUM_H and z >= self.k


class NoiseVar:
    """EWMA variance; once the detector is armed it may not grow past NOISE_INFLATION_MAX^2 x the armed value."""

    def __init__(self, floor_sigma: float):
        self.var = floor_sigma ** 2
        self.cap: float | None = None

    @property
    def sigma(self) -> float:
        return math.sqrt(self.var)

    def learn(self, sample_var: float, armed: bool):
        if armed and self.cap is None:
            self.cap = self.var * NOISE_INFLATION_MAX ** 2
        self.var += BASELINE_ALPHA * (sample_var - self.var)
        if self.cap is not None:
            self.var = min(self.var, self.cap)


class PositionConsistency:
    """Reference track in local metres: alpha filter driven by an external velocity when given,
    else by a constant-velocity prior (least-squares slope over the last clean fixes)."""

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

    def _enu(self, ep):
        lat0, lon0 = self.origin
        k = math.pi / 180.0 * EARTH_RADIUS_M
        return [(ep.lon - lon0) * k * math.cos(math.radians(lat0)), (ep.lat - lat0) * k]

    def reset(self):
        self.pos = None
        self.window.clear()
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

    def step(self, ep: Epoch, armed: bool, may_learn: bool, hits, alerts):
        if self.origin is None:
            self.origin = (ep.lat, ep.lon)
        fix = self._enu(ep)
        ext = ep.ref_vel_e is not None and ep.ref_vel_n is not None
        scale = ep.hdop if ep.hdop else 1.0
        if self.pos is None:
            self.pos, self.t = fix, ep.t
            self.vel = [ep.ref_vel_e, ep.ref_vel_n] if ext else [0.0, 0.0]
            self.window.append((ep.t, *fix))
            return
        dt = ep.t - self.t
        self.t = ep.t
        if dt <= 0:
            return
        prev_vel = self.vel
        self.vel = [ep.ref_vel_e, ep.ref_vel_n] if ext else self._cv_velocity()
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
                                f"position {r:.0f} m off {'reference' if ext else 'constant-velocity'} "
                                f"track ({z:.1f} sigma, CUSUM {self.pos_cusum.s:.1f})",
                                {"residual_m": round(r, 1), "sigma_m": round(sigma, 1),
                                 "cusum": round(self.pos_cusum.s, 1), "frozen_s": round(self.frozen_s, 1),
                                 "reference": "external" if ext else "cv-prior",
                                 "ref_vel_mps": [round(v, 2) for v in self.vel]}))
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


class InterferenceScorer:
    def __init__(self, max_speed_mps: float = MAX_SPEED_MPS):
        self.max_speed_mps = max_speed_mps
        self.base_cn0: dict[str, float] = {}
        self.base_agc: float | None = None
        self.clean_epochs = 0
        self.prev: Epoch | None = None
        self.prev_fix: Epoch | None = None
        self.last_fix_t: float | None = None
        self.pos = PositionConsistency()
        self.clock = ClockConsistency()
        self.alarm = AlarmState()

    @property
    def baseline_ready(self) -> bool:
        return self.clean_epochs >= BASELINE_MIN_EPOCHS

    def acknowledge(self, t: float, relearn: bool = False) -> None:
        """Operator clear: re-anchor the references on the next fix; relearn=True also resets the C/N0/AGC baseline."""
        self.alarm = AlarmState(cleared_t=t, clear_reason="acknowledged")
        self.pos.reset()
        self.clock.reset()
        if relearn:
            self.base_cn0, self.base_agc, self.clean_epochs = {}, None, 0

    def assess(self, ep: Epoch) -> Assessment:
        hits: set[str] = set()
        alerts: list[Alert] = []

        if self.baseline_ready:
            self._check_cn0_vs_baseline(ep, hits, alerts)
            if ep.agc_cnt is not None and self.base_agc:
                rel = (ep.agc_cnt - self.base_agc) / self.base_agc
                if abs(rel) >= AGC_REL_CHANGE:
                    self._add(hits, alerts, "agc_change", rel, AGC_REL_CHANGE, "rel",
                              f"AGC {rel:+.0%} vs baseline", {"agc": ep.agc_cnt, "baseline": round(self.base_agc, 1)})
        self._check_cn0_uniform(ep, hits, alerts)
        if ep.jam_ind is not None and ep.jam_ind >= JAM_IND_HIGH:
            self._add(hits, alerts, "jam_ind", ep.jam_ind, JAM_IND_HIGH, "", f"jamInd {ep.jam_ind:.0f}")
        if ep.jamming_state is not None and ep.jamming_state >= RX_FLAG_ALERT_STATE:
            self._add(hits, alerts, "rx_jam_flag", ep.jamming_state, RX_FLAG_ALERT_STATE, "",
                      f"receiver jammingState {ep.jamming_state}")
        if ep.spoof_det_state is not None and ep.spoof_det_state >= RX_FLAG_ALERT_STATE:
            self._add(hits, alerts, "rx_spoof_flag", ep.spoof_det_state, RX_FLAG_ALERT_STATE, "",
                      f"receiver spoofDetState {ep.spoof_det_state}")
        if self.prev is not None:
            self._check_clock_jump(self.prev, ep, hits, alerts)
        if self.prev_fix is not None and ep.has_fix:
            self._check_position_jump(self.prev_fix, ep, hits, alerts)

        lost = self._check_lost_fix(ep, alerts)
        armed = self.baseline_ready
        may_learn = not self.alarm.active and not lost  # sub-alert hits alone do not freeze the references
        if ep.has_fix:
            self.pos.step(ep, armed, may_learn, hits, alerts)
        self.clock.step(ep, armed, may_learn, "clock_jump" in hits, hits, alerts)

        jam = min(1.0, sum(w for k, w in JAM_WEIGHTS.items() if k in hits))
        spoof = min(1.0, sum(w for k, w in SPOOF_WEIGHTS.items() if k in hits))
        result = Assessment(ep.t, jam, spoof, [a.message for a in alerts], alerts, lost)
        self._update_alarm(result, ep)
        result.alarm = self.alarm.snapshot()
        if max(jam, spoof) <= BASELINE_MAX_SCORE and not lost and not self.alarm.active:
            self._update_baseline(ep)
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
                 and max(self.pos.last_z, self.pos.last_vz, self.clock.last_z) < CLEAR_SIGMA)
        al.quiet_epochs = al.quiet_epochs + 1 if quiet else 0
        if al.quiet_epochs >= CLEAR_EPOCHS:
            self.alarm = AlarmState(cleared_t=ep.t, clear_reason=(
                f"{CLEAR_EPOCHS} epochs with scores <= {BASELINE_MAX_SCORE}, a fix, and "
                f"consistency residuals < {CLEAR_SIGMA} sigma"))
            self.pos.pos_cusum, self.pos.vel_cusum = Cusum(), Cusum()
            self.clock.up, self.clock.down = Cusum(CUSUM_K_SIGNED), Cusum(CUSUM_K_SIGNED)

    def _check_cn0_vs_baseline(self, ep, hits, alerts):
        if not self.base_cn0 or ep.cn0 is None:
            return
        common = [sv for sv in ep.cn0 if sv in self.base_cn0]
        lost = [sv for sv in self.base_cn0 if sv not in ep.cn0]
        deltas = [ep.cn0[sv] - self.base_cn0[sv] for sv in common]
        dropped = sum(1 for d in deltas if d <= -CN0_DROP_DB) + len(lost)
        frac = dropped / len(self.base_cn0)
        if frac >= CN0_DROP_SV_FRACTION:
            self._add(hits, alerts, "cn0_drop", frac, CN0_DROP_SV_FRACTION, "fraction of SVs",
                      f"C/N0 drop >= {CN0_DROP_DB:.0f} dB or lost on {dropped}/{len(self.base_cn0)} SVs",
                      {"dropped_or_lost": dropped, "baseline_svs": len(self.base_cn0)})
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

    def _update_baseline(self, ep):
        if ep.cn0 is None:
            return
        for sv, c in ep.cn0.items():
            old = self.base_cn0.get(sv)
            self.base_cn0[sv] = c if old is None else old + BASELINE_ALPHA * (c - old)
        for sv in [sv for sv in self.base_cn0 if sv not in ep.cn0]:
            del self.base_cn0[sv]  # set or blocked SVs; a whole-sky loss never reaches here
        if ep.agc_cnt is not None:
            old = self.base_agc
            self.base_agc = ep.agc_cnt if old is None else old + BASELINE_ALPHA * (ep.agc_cnt - old)
        self.clean_epochs += 1
