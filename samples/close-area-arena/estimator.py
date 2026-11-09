"""VIO-like pose source for the arena: a position/velocity EKF on simulated VIO and IMU.

Plug in with run.evaluate(..., make_pose_source=make_pose_source_factory("none")).
run_faults.py does that for every case in faults.py.

What it simulates between two planner steps (the hook is only called at 10 Hz):
- Truth is interpolated over the interval with constant acceleration (v1 - v0) / T plus a
  linear correction so the path ends exactly at the new truth position.
- IMU at 50 Hz: horizontal accel = truth accel + per-run bias N(0, 0.03 m/s^2) per axis + white
  N(0, 0.05 m/s^2). Both values are assumptions for a MEMS IMU after attitude removal, not
  measured in the hub.
- VIO at 30 Hz: position deltas = truth delta + random walk in distance travelled. The VIO
  output (an odometry frame anchored at A) is fused as a position measurement, like PX4 EKF2
  external-vision position fusion.
- EKF state [x, y, vx, vy], predict on the latest IMU sample (zero-order hold) to each event
  time, update on each VIO sample.

Calibration of nominal drift (the only calibrated number here):
  samples/relative-nav-benchmark/README.md, OpenVINS v2.7 stereo + IMU on UZH-FPV
  indoor_forward_3 (real data): RPE over 10 m = 1.5 %, i.e. 0.15 m per 10 m; final error
  0.73 m over 278.3 m. A random walk in distance, sigma(d) = C * sqrt(d), with
  C = 0.15 / sqrt(10) = 0.047 m / sqrt(m), gives 0.15 m at 10 m and predicts 0.79 m at 278 m,
  close to the measured 0.73 m. A constant scale error fitted to 1.5 % would predict 4.2 m at
  278 m, so the random walk is the better fit to both numbers.

Dark zones (rectangles where VIO quality drops and drift grows) are NOT calibrated: drift x4,
an extra 0.03 m/sqrt(s) time random walk (drifts while hovering), measurement noise x5, 30 %
of frames lost, quality 25. They model texture-poor or unlit patches
(docs/research/close-area-nav/03-close-area-localization.md, failure modes).

Reported fields: quality 90 nominal, 25 when the last VIO sample was in a dark zone, 0 when no
VIO sample was fused in the last 0.2 s. reset_counter increments on a VIO re-initialisation
(after a dropout) or a reported jump. sigma_xy = sqrt(Pxx + Pyy + VIO drift variance), where
the VIO drift variance is what the VIO model itself accumulated, so it is honest in
expectation unless a fault overrides it. yaw, z and vz are passed through from truth.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

try:
    from .adapter import Pose
except ImportError:
    from adapter import Pose

VIO_HZ = 30
IMU_HZ = 50
DRIFT_C = 0.15 / math.sqrt(10.0)   # m / sqrt(m), from the OpenVINS RPE over 10 m (see docstring)
VIO_WHITE = 0.005                  # m, per-sample jitter on the VIO output (assumed)
ACC_NOISE = 0.05                   # m/s^2 white per sample (assumed)
ACC_BIAS = 0.03                    # m/s^2 per-axis bias std, per run (assumed)
Q_ACC = 0.1                        # m/s^2, filter process noise (covers noise + bias)
DARK = {"drift_mult": 4.0, "time_walk": 0.03, "white_mult": 5.0, "drop_p": 0.3, "quality": 25}
QUALITY_OK = 90
LOST_AFTER_S = 0.2


@dataclass
class DarkZone:
    x0: float
    y0: float
    x1: float
    y1: float

    def contains(self, x: float, y: float) -> bool:
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1

    def to_list(self):
        return [round(self.x0, 3), round(self.y0, 3), round(self.x1, 3), round(self.y1, 3)]


def make_dark_zones(world, rng, n: int = 2) -> list[DarkZone]:
    """Zone 0 is centred near the A-B line (so straight-ish paths cross it), the rest are
    anywhere in the area. Sizes 2-4 m per side. Seeded by the caller's rng."""
    zones = []
    gx, gy = world.goal
    L = math.hypot(gx, gy) or 1.0
    for k in range(n):
        if k == 0:
            f = rng.uniform(0.25, 0.75)
            off = rng.normal(0.0, 1.0)
            cx, cy = f * gx - off * gy / L, f * gy + off * gx / L
        else:
            cx = rng.uniform(world.xmin + 2.0, world.xmax - 2.0)
            cy = rng.uniform(world.ymin + 2.0, world.ymax - 2.0)
        hw, hh = rng.uniform(1.0, 2.0, size=2)
        zones.append(DarkZone(max(world.xmin, cx - hw), max(world.ymin, cy - hh),
                              min(world.xmax, cx + hw), min(world.ymax, cy + hh)))
    return zones


class VioEstimator:
    """PoseSource: call with the truth Pose, returns the estimated Pose."""

    def __init__(self, rng, dark_zones=(), fault=None):
        self.rng = rng
        self.zones = list(dark_zones)
        self.fault = fault
        self.acc_bias = rng.normal(0.0, ACC_BIAS, 2)
        self.prev = None
        self.reset_counter = 0
        # per planner step, for run_faults.py
        self.errs: list[float] = []
        self.sigmas: list[float] = []
        self.qualities: list[int] = []
        self.dark_steps = 0

    # ---- helpers ----
    def _dark(self, x, y) -> bool:
        return any(z.contains(x, y) for z in self.zones)

    def _predict(self, dt: float) -> None:
        if dt <= 0:
            return
        a = self.acc
        self.x[0:2] += self.x[2:4] * dt + 0.5 * a * dt * dt
        self.x[2:4] += a * dt
        F = np.eye(4)
        F[0, 2] = F[1, 3] = dt
        g = np.array([0.5 * dt * dt, dt])
        Q = np.zeros((4, 4))
        for i in (0, 1):
            idx = [i, i + 2]
            Q[np.ix_(idx, idx)] = np.outer(g, g) * Q_ACC ** 2
        self.P = F @ self.P @ F.T + Q

    def _update(self, z, r: float) -> None:
        H = np.zeros((2, 4))
        H[0, 0] = H[1, 1] = 1.0
        S = H @ self.P @ H.T + np.eye(2) * r * r
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ (z - H @ self.x)
        self.P = (np.eye(4) - K @ H) @ self.P

    def _imu(self, a_true) -> None:
        self.acc = a_true + self.acc_bias + self.rng.normal(0.0, ACC_NOISE, 2)

    def _vio(self, tv: float, pt) -> None:
        drop_draw = self.rng.random()          # always drawn: same stream across fault cases
        noise = self.rng.normal(0.0, 1.0, 2)
        meas = self.rng.normal(0.0, 1.0, 2)
        if self.fault is not None and not self.fault.vio_ok(tv):
            self.vio_lost = True
            return
        if self.vio_lost:                      # re-initialise: new VIO frame at the EKF pose
            self.vio_lost = False
            self.vio_pos = self.x[0:2].copy()
            self.vio_ref = pt.copy()
            self.drift_var += self.P[0, 0] + self.P[1, 1]
            self.last_vio_t = tv
            self.reset_counter += 1
            return
        dark = self._dark(pt[0], pt[1])
        if dark and drop_draw < DARK["drop_p"]:
            return                              # frame lost, the next delta covers both
        d = pt - self.vio_ref
        dl = float(math.hypot(d[0], d[1]))
        dt = tv - self.last_vio_t
        c = DRIFT_C * (DARK["drift_mult"] if dark else 1.0)
        var_h = c * c * dl + ((DARK["time_walk"] ** 2) * dt if dark else 0.0)
        delta = d + noise * math.sqrt(var_h / 2.0)
        if self.fault is not None:
            bx, by = self.fault.vio_bias(tv)
            delta = delta + np.array([bx, by]) * dt
        self.vio_pos = self.vio_pos + delta
        self.vio_ref = pt.copy()
        self.drift_var += var_h
        self.last_vio_t = tv
        self.last_dark = dark
        white = VIO_WHITE * (DARK["white_mult"] if dark else 1.0)
        self._update(self.vio_pos + meas * white, white)

    # ---- read-only accessor (belief-space safety filters) ----
    def belief(self) -> dict | None:
        """Copies of the EKF mean and covariance after the last call, plus the noise settings the
        filter uses. Reads state only; changes nothing. None before the first call.

        x [x, y, vx, vy], P 4x4 (EKF only, no VIO drift), drift_var (horizontal VIO drift variance
        accumulated so far, m^2, both axes together), q_acc (process noise, m/s^2 per axis),
        vio_r (std of the next VIO position measurement, m), vio_hz, imu_hz, drift_c (m/sqrt(m)
        now), time_walk (m/sqrt(s) now), last_dark, vio_lost, last_vio_t."""
        if self.prev is None:
            return None
        dark = bool(self.last_dark)
        return {
            "t": float(self.tf), "x": self.x.copy(), "P": self.P.copy(),
            "drift_var": float(self.drift_var), "q_acc": Q_ACC,
            "vio_r": VIO_WHITE * (DARK["white_mult"] if dark else 1.0),
            "vio_hz": VIO_HZ, "imu_hz": IMU_HZ,
            "drift_c": DRIFT_C * (DARK["drift_mult"] if dark else 1.0),
            "time_walk": DARK["time_walk"] if dark else 0.0,
            "last_dark": dark, "vio_lost": bool(self.vio_lost), "last_vio_t": float(self.last_vio_t),
        }

    # ---- PoseSource ----
    def __call__(self, truth: Pose) -> Pose:
        p1 = np.array([truth.x, truth.y])
        v1 = np.array([truth.vx, truth.vy])
        if self.prev is None:
            self.x = np.array([truth.x, truth.y, truth.vx, truth.vy], float)
            self.P = np.diag([0.01 ** 2, 0.01 ** 2, 0.02 ** 2, 0.02 ** 2])
            self.tf = truth.t
            self.kv = int(round(truth.t * VIO_HZ))
            self.ki = int(round(truth.t * IMU_HZ))
            self.vio_pos = p1.copy()
            self.vio_ref = p1.copy()
            self.last_vio_t = truth.t
            self.last_dark = False
            self.vio_lost = False
            self.drift_var = 0.0
            self._imu(np.zeros(2))
        else:
            t0, p0, v0 = self.prev
            T = truth.t - t0
            a = (v1 - v0) / T if T > 0 else np.zeros(2)
            res = p1 - (p0 + v0 * T + 0.5 * a * T * T) if T > 0 else np.zeros(2)

            def interp(t):
                tau = t - t0
                return p0 + v0 * tau + 0.5 * a * tau * tau + res * (tau / T)

            while True:
                tv = (self.kv + 1) / VIO_HZ
                ti = (self.ki + 1) / IMU_HZ
                te = min(tv, ti)
                if te > truth.t + 1e-9:
                    break
                self._predict(te - self.tf)
                self.tf = te
                if ti <= tv:
                    self._imu(a)
                    self.ki += 1
                else:
                    self._vio(tv, interp(tv))
                    self.kv += 1
            self._predict(truth.t - self.tf)
            self.tf = truth.t
        self.prev = (truth.t, p1, v1)

        if self.fault is not None:
            step = self.fault.on_call(truth, self)
            if step is not None:
                self.vio_pos = self.vio_pos + np.array(step)
                self.reset_counter += 1

        ex, ey = float(self.x[0]), float(self.x[1])
        err = math.hypot(ex - truth.x, ey - truth.y)
        sigma = math.sqrt(max(0.0, self.P[0, 0] + self.P[1, 1] + self.drift_var))
        if self.fault is not None:
            sigma = self.fault.report_sigma(sigma, err)
        if truth.t - self.last_vio_t > LOST_AFTER_S:
            q = 0
        elif self.last_dark:
            q = DARK["quality"]
        else:
            q = QUALITY_OK
        self.errs.append(err)
        self.sigmas.append(sigma)
        self.qualities.append(q)
        self.dark_steps += int(self._dark(truth.x, truth.y))
        return replace(truth, x=ex, y=ey, vx=float(self.x[2]), vy=float(self.x[3]),
                       quality=q, reset_counter=self.reset_counter, sigma_xy=sigma)


def make_pose_source_factory(fault_name: str = "none", dark: bool = True, sink: list | None = None):
    """Returns make_pose_source(world, seed, index) for run.evaluate. Each built estimator
    is appended to `sink` (if given) so the caller can read its logs after the run."""
    try:
        from . import faults
    except ImportError:
        import faults

    def make_pose_source(world, seed, index):
        zones = make_dark_zones(world, np.random.default_rng([seed, index, 4001])) if dark else []
        est = VioEstimator(np.random.default_rng([seed, index, 4101]), zones,
                           faults.make(fault_name, world, seed, index))
        if sink is not None:
            sink.append(est)
        return est

    return make_pose_source
