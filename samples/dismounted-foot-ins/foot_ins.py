"""Stdlib 15-state error-state EKF for a foot-mounted IMU (ZUPT-aided INS).

Nominal state: position p, velocity v (NED, m), attitude q (body => NED quaternion
w,x,y,z), accelerometer bias ba, gyro bias bg. Error state (15): dp, dv, dtheta
(global/left attitude error, C_true = (I + [dtheta]x) C_hat), dba, dbg.

Updates: ZUPT (v = 0), ZARU (omega = 0 => gyro bias), heading (yaw), range to an
anchor (UWB) with an NIS gate. With freeze_biases=True the bias states get no prior
and no process noise, so the filter reduces to pyshoe's 9-state INS; with
pyshoe_order=True (default) the strapdown step also follows pyshoe's nav_eq order
(attitude first, then velocity, then position from the new velocity), which scored
better on the hallway data than the textbook order (see README).
"""
import math

N = 15
IP, IV, IA, IBA, IBG = 0, 3, 6, 9, 12

GRAVITY = 9.8029
SIGMA_ACC = 0.5  # m/s^2 per sample, pyshoe's process noise
SIGMA_GYRO = math.radians(0.5)  # rad/s per sample
SIGMA_ZUPT = 0.01  # m/s
SIGMA_ZARU = math.radians(0.1)  # rad/s, foot is not perfectly still in stance
SIGMA_YAW_RW = math.radians(0.15)  # rad/sqrt(s): ~2 deg after 200 s, the drift ZUPT cannot observe
SIGMA_BA_RW = 1e-4  # m/s^2 / sqrt(s)
SIGMA_BG_RW = 1e-5  # rad/s / sqrt(s)
SIGMA_BA0 = 0.005  # m/s^2
SIGMA_BG0 = 1e-4  # rad/s (~0.006 deg/s) residual after initialising bg from the first standstill
INIT_SAMPLES = 20  # pyshoe levels on the first 20 samples


def quat_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def quat_from_rotvec(r):
    ang = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
    if ang < 1e-12:
        return (1.0, 0.5 * r[0], 0.5 * r[1], 0.5 * r[2])
    s = math.sin(ang / 2) / ang
    return (math.cos(ang / 2), r[0] * s, r[1] * s, r[2] * s)


def quat_normalize(q):
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q)


def quat_to_dcm(q):
    w, x, y, z = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]


def quat_from_euler(roll, pitch, yaw):
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (cr * cp * cy + sr * sp * sy, sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy, cr * cp * sy - sr * sp * cy)


def yaw_of(q):
    c = quat_to_dcm(q)
    return math.atan2(c[1][0], c[0][0])


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def mat3_vec(m, v):
    return [m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
            m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
            m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]]


def inv3(m):
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]


class FootINS:
    def __init__(self, acc0, yaw0=0.0, gyro_bias0=(0.0, 0.0, 0.0), freeze_biases=False,
                 sigma_zupt=SIGMA_ZUPT, pyshoe_order=True, yaw_rw=SIGMA_YAW_RW):
        k = min(INIT_SAMPLES, len(acc0))
        ax, ay, az = (sum(a[i] for a in acc0[:k]) / k for i in range(3))
        roll = math.atan2(-ay, -az)
        pitch = math.atan2(ax, math.sqrt(ay * ay + az * az))
        self.q = quat_from_euler(roll, pitch, yaw0)
        self.p = [0.0, 0.0, 0.0]
        self.v = [0.0, 0.0, 0.0]
        self.ba = [0.0, 0.0, 0.0]
        self.bg = list(gyro_bias0)
        self.freeze = freeze_biases
        self.pyshoe_order = pyshoe_order
        self.q_yaw = yaw_rw ** 2
        self.r_zupt = sigma_zupt ** 2
        self.P = [[0.0] * N for _ in range(N)]
        for i in range(3):
            self.P[IP + i][IP + i] = 1e-10
            self.P[IV + i][IV + i] = 1e-10
            self.P[IA + i][IA + i] = math.radians(0.1) ** 2
            if not freeze_biases:
                self.P[IBA + i][IBA + i] = SIGMA_BA0 ** 2
                self.P[IBG + i][IBG + i] = SIGMA_BG0 ** 2
        self.C = quat_to_dcm(self.q)

    def propagate(self, acc, gyro, dt):
        f = [acc[i] - self.ba[i] for i in range(3)]
        w = [gyro[i] - self.bg[i] for i in range(3)]
        C = self.C
        self.q = quat_normalize(quat_mul(self.q, quat_from_rotvec([w[0] * dt, w[1] * dt, w[2] * dt])))
        self.C = quat_to_dcm(self.q)
        if self.pyshoe_order:
            # pyshoe nav_eq: rotate f with the updated attitude, position from the new velocity
            fn_nav = mat3_vec(self.C, f)
            an = [fn_nav[0], fn_nav[1], fn_nav[2] + GRAVITY]
            for i in range(3):
                self.v[i] += an[i] * dt
                self.p[i] += self.v[i] * dt + 0.5 * an[i] * dt * dt
            fn = mat3_vec(C, f)
        else:
            fn = mat3_vec(C, f)
            an = [fn[0], fn[1], fn[2] + GRAVITY]
            for i in range(3):
                self.p[i] += self.v[i] * dt + 0.5 * an[i] * dt * dt
                self.v[i] += an[i] * dt
        # dv' = -[fn]x dtheta - C dba ; dtheta' = -C dbg ; dp' = dv
        M = [[0.0, fn[2], -fn[1]], [-fn[2], 0.0, fn[0]], [fn[1], -fn[0], 0.0]]
        self._cov_step(M, C, dt)

    def _cov_step(self, M, C, dt):
        frz = self.freeze

        def apply(row):
            out = row[:]
            for i in range(3):
                out[IP + i] = row[IP + i] + dt * row[IV + i]
                s = M[i][0] * row[IA] + M[i][1] * row[IA + 1] + M[i][2] * row[IA + 2]
                if not frz:
                    s -= C[i][0] * row[IBA] + C[i][1] * row[IBA + 1] + C[i][2] * row[IBA + 2]
                out[IV + i] = row[IV + i] + dt * s
                if not frz:
                    out[IA + i] = row[IA + i] - dt * (C[i][0] * row[IBG] + C[i][1] * row[IBG + 1] + C[i][2] * row[IBG + 2])
            return out

        P = self.P
        cols = [apply([P[r][c] for r in range(N)]) for c in range(N)]  # columns of F P
        P = [apply([cols[c][r] for c in range(N)]) for r in range(N)]  # rows of F P F^T
        qv, qa = (SIGMA_ACC * dt) ** 2, (SIGMA_GYRO * dt) ** 2
        for i in range(3):
            P[IV + i][IV + i] += qv
            P[IA + i][IA + i] += qa
            if not frz:
                P[IBA + i][IBA + i] += SIGMA_BA_RW ** 2 * dt
                P[IBG + i][IBG + i] += SIGMA_BG_RW ** 2 * dt
        P[IA + 2][IA + 2] += self.q_yaw * dt
        self.P = P

    def _update_block(self, idx, y, R):
        """Update with H selecting three consecutive error states starting at idx."""
        P = self.P
        S = [[P[idx + i][idx + j] + R[i][j] for j in range(3)] for i in range(3)]
        Si = inv3(S)
        PHt = [[P[r][idx + j] for j in range(3)] for r in range(N)]
        K = [[sum(PHt[r][k] * Si[k][j] for k in range(3)) for j in range(3)] for r in range(N)]
        dx = [K[r][0] * y[0] + K[r][1] * y[1] + K[r][2] * y[2] for r in range(N)]
        HP = [P[idx + j] for j in range(3)]
        self.P = [[P[r][c] - (K[r][0] * HP[0][c] + K[r][1] * HP[1][c] + K[r][2] * HP[2][c])
                   for c in range(N)] for r in range(N)]
        self._inject(dx)
        self._symmetrize()

    def _update_scalar(self, h, y, r, gate=None):
        """Scalar update with sparse H given as {state index: value}. Returns NIS."""
        P = self.P
        PHt = [sum(P[row][i] * hv for i, hv in h.items()) for row in range(N)]
        s = sum(hv * PHt[i] for i, hv in h.items()) + r
        nis = y * y / s
        if gate is not None and nis > gate:
            return nis
        K = [v / s for v in PHt]
        self.P = [[P[a][b] - K[a] * PHt[b] for b in range(N)] for a in range(N)]
        self._inject([k * y for k in K])
        self._symmetrize()
        return nis

    def _symmetrize(self):
        P = self.P
        for i in range(N):
            for j in range(i + 1, N):
                m = 0.5 * (P[i][j] + P[j][i])
                P[i][j] = P[j][i] = m

    def _inject(self, dx):
        for i in range(3):
            self.p[i] += dx[IP + i]
            self.v[i] += dx[IV + i]
        self.q = quat_normalize(quat_mul(quat_from_rotvec(dx[IA:IA + 3]), self.q))
        self.C = quat_to_dcm(self.q)
        if not self.freeze:
            for i in range(3):
                self.ba[i] += dx[IBA + i]
                self.bg[i] += dx[IBG + i]

    def zupt(self):
        r = self.r_zupt
        self._update_block(IV, [-self.v[0], -self.v[1], -self.v[2]], [[r, 0, 0], [0, r, 0], [0, 0, r]])

    def zaru(self, gyro):
        if self.freeze:
            return
        r = SIGMA_ZARU ** 2
        self._update_block(IBG, [gyro[i] - self.bg[i] for i in range(3)], [[r, 0, 0], [0, r, 0], [0, 0, r]])

    def heading_update(self, yaw_meas, sigma):
        return self.yaw_residual_update(wrap(yaw_meas - yaw_of(self.q)), sigma)

    def yaw_residual_update(self, dyaw, sigma):
        """Yaw innovation already formed by the caller (e.g. corridor direction - step direction)."""
        return self._update_scalar({IA + 2: 1.0}, dyaw, sigma ** 2)

    def height_update(self, z_down, sigma):
        """Down-position fix (barometer, or a known floor height while the foot is in stance)."""
        return self._update_scalar({IP + 2: 1.0}, z_down - self.p[2], sigma ** 2)

    def range_update(self, anchor, rng, sigma, gate=None):
        d = [self.p[i] - anchor[i] for i in range(3)]
        rhat = math.sqrt(sum(c * c for c in d))
        h = {IP + i: d[i] / rhat for i in range(3)}
        return self._update_scalar(h, rng - rhat, sigma ** 2, gate)

    def inflate_horizontal(self, var):
        self.P[IP][IP] += var
        self.P[IP + 1][IP + 1] += var

    def sigma_h(self):
        return math.sqrt(max(self.P[0][0] + self.P[1][1], 0.0))
