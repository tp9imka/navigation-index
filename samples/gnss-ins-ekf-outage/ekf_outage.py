"""2D loosely-coupled GNSS/INS EKF with a GNSS outage and a slow spoofing walk-off.

State x = [px, py, vx, vy, psi, bax, bay, bg] (nav-frame position/velocity, heading,
body-frame accelerometer bias, gyro bias). IMU at 100 Hz, GNSS position at 1 Hz.
Compares: INS-only dead reckoning, EKF accepting every fix, EKF with a chi-square
innovation gate, and the gated EKF that latches into INS holdover once it alarms. Python 3 stdlib only.

Usage: python3 ekf_outage.py [--seed N] [--spoof-rate M_PER_S] [--sweep]
"""

import argparse
import math
import random

import matlite as m

IMU_HZ = 100
COV_DECIMATION = 10  # covariance propagated at IMU_HZ / COV_DECIMATION
GNSS_HZ = 1
DURATION_S = 400.0

OUTAGE_START_S, OUTAGE_END_S = 150.0, 210.0
SPOOF_START_S = 280.0
SPOOF_RATE_MPS = 1.0
SPOOF_DIRECTION_RAD = math.radians(30.0)

ACCEL_NOISE_SD = 0.05  # m/s^2 per sample
GYRO_NOISE_SD = math.radians(0.05)  # rad/s per sample
ACCEL_BIAS_TRUE = (0.06, -0.04)  # m/s^2, a few mg (consumer MEMS)
GYRO_BIAS_TRUE = math.radians(0.03)  # rad/s
ACCEL_BIAS_RW = 1e-4  # m/s^2/sqrt(s)
GYRO_BIAS_RW = math.radians(1e-3)  # rad/s/sqrt(s)
GNSS_NOISE_SD = 2.5  # m, per axis

CHI2_2DOF_999 = 13.816  # 99.9 % gate for a 2-D innovation
ALARM_CONSECUTIVE = 3  # rejected fixes in a row before raising a spoofing alarm

MODES = {"ins": "INS-only", "ekf": "EKF", "gate": "EKF+gate", "latch": "EKF+gate+latch"}

SEGMENTS = [
    ("nominal", 0.0, OUTAGE_START_S),
    ("outage", OUTAGE_START_S, OUTAGE_END_S),
    ("recovery", OUTAGE_END_S, SPOOF_START_S),
    ("spoofing", SPOOF_START_S, DURATION_S),
]


def truth_profile(t):
    """Speed and yaw rate of a weaving ground vehicle, plus forward acceleration."""
    speed = 15.0 + 5.0 * math.sin(2 * math.pi * t / 60.0)
    accel_fwd = 5.0 * 2 * math.pi / 60.0 * math.cos(2 * math.pi * t / 60.0)
    yaw_rate = 0.12 * math.sin(2 * math.pi * t / 45.0)
    return speed, accel_fwd, yaw_rate


def simulate(rng):
    dt = 1.0 / IMU_HZ
    steps = int(DURATION_S * IMU_HZ)
    px = py = psi = 0.0
    bax, bay = ACCEL_BIAS_TRUE
    bg = GYRO_BIAS_TRUE
    truth, imu = [], []
    for k in range(steps):
        t = k * dt
        speed, accel_fwd, yaw_rate = truth_profile(t)
        vx, vy = speed * math.cos(psi), speed * math.sin(psi)
        truth.append((t, px, py, vx, vy, psi))
        fx = accel_fwd + bax + rng.gauss(0, ACCEL_NOISE_SD)
        fy = speed * yaw_rate + bay + rng.gauss(0, ACCEL_NOISE_SD)
        w = yaw_rate + bg + rng.gauss(0, GYRO_NOISE_SD)
        imu.append((t, fx, fy, w))
        bax += rng.gauss(0, ACCEL_BIAS_RW * math.sqrt(dt))
        bay += rng.gauss(0, ACCEL_BIAS_RW * math.sqrt(dt))
        bg += rng.gauss(0, GYRO_BIAS_RW * math.sqrt(dt))
        px += vx * dt
        py += vy * dt
        psi += yaw_rate * dt
    return truth, imu


def gnss_fixes(truth, rng, spoof_rate):
    """{imu_step_index: (zx, zy, spoof_offset_m)}; none during the outage."""
    fixes = {}
    every = IMU_HZ // GNSS_HZ
    for k in range(every, len(truth), every):
        t, px, py = truth[k][:3]
        if OUTAGE_START_S <= t < OUTAGE_END_S:
            continue
        off = spoof_rate * (t - SPOOF_START_S) if t >= SPOOF_START_S else 0.0
        zx = px + off * math.cos(SPOOF_DIRECTION_RAD) + rng.gauss(0, GNSS_NOISE_SD)
        zy = py + off * math.sin(SPOOF_DIRECTION_RAD) + rng.gauss(0, GNSS_NOISE_SD)
        fixes[k] = (zx, zy, off)
    return fixes


class Ekf:
    def __init__(self, x0):
        self.x = list(x0)
        self.P = m.diag([3.0**2, 3.0**2, 0.5**2, 0.5**2, math.radians(2.0) ** 2,
                         0.1**2, 0.1**2, math.radians(0.2) ** 2])
        self.last_f = (0.0, 0.0)

    def mechanize(self, fx, fy, w, dt):
        px, py, vx, vy, psi, bax, bay, bg = self.x
        ux, uy = fx - bax, fy - bay
        c, s = math.cos(psi), math.sin(psi)
        ax, ay = c * ux - s * uy, s * ux + c * uy
        self.x[0] = px + vx * dt + 0.5 * ax * dt * dt
        self.x[1] = py + vy * dt + 0.5 * ay * dt * dt
        self.x[2] = vx + ax * dt
        self.x[3] = vy + ay * dt
        self.x[4] = psi + (w - bg) * dt
        self.last_f = (fx, fy)

    def propagate_cov(self, dt):
        psi, bax, bay = self.x[4], self.x[5], self.x[6]
        ux, uy = self.last_f[0] - bax, self.last_f[1] - bay
        c, s = math.cos(psi), math.sin(psi)
        A = m.zeros(8, 8)
        A[0][2] = A[1][3] = 1.0
        A[2][4], A[3][4] = -s * ux - c * uy, c * ux - s * uy
        A[2][5], A[2][6], A[3][5], A[3][6] = -c, s, -s, -c
        A[4][7] = -1.0
        F = m.add(m.eye(8), m.scale(A, dt))
        imu_dt = 1.0 / IMU_HZ
        q_acc = ACCEL_NOISE_SD**2 * imu_dt
        q_gyr = GYRO_NOISE_SD**2 * imu_dt
        Q = m.diag([0.0, 0.0, q_acc * dt, q_acc * dt, q_gyr * dt,
                    ACCEL_BIAS_RW**2 * dt, ACCEL_BIAS_RW**2 * dt, GYRO_BIAS_RW**2 * dt])
        self.P = m.symmetrize(m.add(m.matmul(m.matmul(F, self.P), m.transpose(F)), Q))

    def innovation(self, zx, zy):
        y = (zx - self.x[0], zy - self.x[1])
        S = [[self.P[0][0] + GNSS_NOISE_SD**2, self.P[0][1]],
             [self.P[1][0], self.P[1][1] + GNSS_NOISE_SD**2]]
        Si = m.inv2(S)
        nis = (y[0] * (Si[0][0] * y[0] + Si[0][1] * y[1])
               + y[1] * (Si[1][0] * y[0] + Si[1][1] * y[1]))
        return y, Si, nis

    def update(self, y, Si):
        PHt = [[row[0], row[1]] for row in self.P]
        K = m.matmul(PHt, Si)
        for i in range(8):
            self.x[i] += K[i][0] * y[0] + K[i][1] * y[1]
        KH = m.zeros(8, 8)
        for i in range(8):
            KH[i][0], KH[i][1] = K[i][0], K[i][1]
        self.P = m.symmetrize(m.matmul(m.sub(m.eye(8), KH), self.P))


def run(truth, imu, fixes, mode):
    """mode: 'ins' (no GNSS), 'ekf' (accept all fixes), 'gate' (chi-square gate),
    'latch' (gate, and after the alarm stop trusting GNSS: INS holdover)."""
    t0, px, py, vx, vy, psi = truth[0]
    f = Ekf([px, py, vx, vy, psi, 0.0, 0.0, 0.0])
    dt = 1.0 / IMU_HZ
    errors, events = [], {"rejected": 0, "spoof_rejected": 0, "alarm_t": None}
    consecutive = 0
    for k, (t, fx, fy, w) in enumerate(imu):
        if k > 0:
            f.mechanize(fx, fy, w, dt)
            if mode != "ins" and k % COV_DECIMATION == 0:
                f.propagate_cov(dt * COV_DECIMATION)
        if mode != "ins" and k in fixes:
            zx, zy, off = fixes[k]
            y, Si, nis = f.innovation(zx, zy)
            gated = mode in ("gate", "latch")
            latched = mode == "latch" and events["alarm_t"] is not None
            if latched or (gated and nis > CHI2_2DOF_999):
                events["rejected"] += 1
                events["spoof_rejected"] += off > 0
                consecutive += 1
                if consecutive >= ALARM_CONSECUTIVE and events["alarm_t"] is None:
                    events["alarm_t"] = t
            else:
                consecutive = 0
                f.update(y, Si)
        _, tx, ty = truth[k][:3]
        errors.append((t, math.hypot(f.x[0] - tx, f.x[1] - ty)))
    return errors, events


def segment_stats(errors, lo, hi):
    vals = [e for t, e in errors if lo <= t < hi]
    rms = math.sqrt(sum(v * v for v in vals) / len(vals))
    return rms, max(vals), vals[-1]


def report(seed, spoof_rate):
    rng = random.Random(seed)
    truth, imu = simulate(rng)
    fixes = gnss_fixes(truth, rng, spoof_rate)
    results = {mode: run(truth, imu, fixes, mode) for mode in MODES}

    print(f"seed={seed} spoof_rate={spoof_rate} m/s  IMU {IMU_HZ} Hz, GNSS {GNSS_HZ} Hz, "
          f"outage {OUTAGE_START_S:.0f}-{OUTAGE_END_S:.0f} s, spoof from {SPOOF_START_S:.0f} s")
    print("Horizontal position error [m]: RMS / max / end-of-segment")
    header = f"{'segment':<10}" + "".join(f"{MODES[mode]:>27}" for mode in MODES)
    print(header)
    for name, lo, hi in SEGMENTS:
        cells = []
        for mode in MODES:
            rms, mx, end = segment_stats(results[mode][0], lo, hi)
            cells.append(f"{rms:8.1f} /{mx:8.1f} /{end:7.1f}")
        print(f"{name:<10}" + "".join(f"{c:>27}" for c in cells))
    ev = results["gate"][1]  # 'latch' raises the alarm at the same epoch
    spoofed = sum(1 for _, _, off in fixes.values() if off > 0)
    alarm = f"{ev['alarm_t']:.0f} s ({ev['alarm_t'] - SPOOF_START_S:.0f} s after onset)" if ev["alarm_t"] else "never"
    print(f"gate: rejected {ev['rejected']} fixes ({ev['spoof_rejected']}/{spoofed} spoofed); "
          f"spoofing alarm ({ALARM_CONSECUTIVE} consecutive rejects) at {alarm}")
    print(f"final spoof offset {spoof_rate * (DURATION_S - SPOOF_START_S):.0f} m")


def sweep(seed):
    print("End-of-run horizontal error [m] vs spoof walk-off rate")
    print(f"{'rate m/s':>9}{'alarm after s':>15}{'EKF':>9}{'EKF+gate':>10}{'+latch':>9}")
    for rate in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0):
        rng = random.Random(seed)
        truth, imu = simulate(rng)
        fixes = gnss_fixes(truth, rng, rate)
        e_ekf, _ = run(truth, imu, fixes, "ekf")
        e_gate, ev = run(truth, imu, fixes, "gate")
        e_latch, _ = run(truth, imu, fixes, "latch")
        alarm = f"{ev['alarm_t'] - SPOOF_START_S:.0f}" if ev["alarm_t"] else "never"
        print(f"{rate:>9}{alarm:>15}{e_ekf[-1][1]:>9.1f}{e_gate[-1][1]:>10.1f}{e_latch[-1][1]:>9.1f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--spoof-rate", type=float, default=SPOOF_RATE_MPS)
    ap.add_argument("--sweep", action="store_true", help="vary spoof walk-off rate")
    args = ap.parse_args()
    if args.sweep:
        sweep(args.seed)
    else:
        report(args.seed, args.spoof_rate)
