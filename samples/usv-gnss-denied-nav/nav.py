"""Dead-reckoning EKF and the GNSS integrity monitor (solution separation against a GNSS-free filter).

State: [x, y, compass bias b (rad), speed-log scale error s].
"""
import copy
import math

from geo import CHI2_2DOF_999, CHI2_3DOF_999, eye, inv, madd, mm, mv, quad, tr, wrap_pi

GNSS_SIGMA_M = 3.0
SIGMA_V_MS = 0.05
SIGMA_PSI_RAD = math.radians(0.5)
Q_BIAS_RW = math.radians(0.003) ** 2
Q_SCALE_RW = 1e-8
P0 = (5.0 ** 2, 5.0 ** 2, math.radians(3.0) ** 2, 0.02 ** 2)
SS_THRESHOLD = 23.03          # chi-square 2 dof, P_fa = 1e-5 per test
SS_PERSIST_S = 3
SS_FLOOR_M = 3.0              # model-mismatch margin added to the separation covariance
ISOLATE_WINDOW_S = 60         # GNSS is excluded only if the GNSS-free filter took
ISOLATE_MIN_FIXES = 3         # at least this many radar fixes within the window
ALARM_CLEAR_S = 30
BIAS_WINDOW_S = 30            # GNSS-minus-reference mean over this window
GNSS_BIAS_SIGMA_M = 2.0       # assumed slowly varying GNSS error (multipath, iono) that does not average out
READMIT_NIS = 9.21            # chi-square 2 dof, 99 %
READMIT_S = 120
GNSS_RESET_S = 10            # consecutive gated-out GNSS fixes before the filter snaps back to GNSS
PL_K = 4.80                   # sqrt(-2 ln 1e-5): isotropic 2D Gaussian tail, not a certified PL


class Ekf:
    def __init__(self, x0, y0):
        self.x = [x0, y0, 0.0, 0.0]
        self.P = [[P0[i] if i == j else 0.0 for j in range(4)] for i in range(4)]

    def predict(self, psi_m, v_m, dt):
        b, s = self.x[2], self.x[3]
        psi = psi_m - b
        v = v_m / (1.0 + s)
        sp, cp = math.sin(psi), math.cos(psi)
        self.x[0] += v * sp * dt
        self.x[1] += v * cp * dt
        F = eye(4)
        F[0][2], F[1][2] = -v * cp * dt, v * sp * dt
        F[0][3], F[1][3] = -v * sp * dt / (1 + s), -v * cp * dt / (1 + s)
        G = [[sp * dt, v * cp * dt], [cp * dt, -v * sp * dt]]  # d(dx, dy)/d(v, psi) noise
        qv, qp = SIGMA_V_MS ** 2, SIGMA_PSI_RAD ** 2
        Q = [[0.0] * 4 for _ in range(4)]
        for i in range(2):
            for j in range(2):
                Q[i][j] = G[i][0] * G[j][0] * qv + G[i][1] * G[j][1] * qp
        Q[2][2], Q[3][3] = Q_BIAS_RW * dt, Q_SCALE_RW * dt
        self.P = madd(mm(mm(F, self.P), tr(F)), Q)

    def innovation(self, z, H, R, angle_rows=()):
        y = [zi - hi for zi, hi in zip(z, mv(H, self.x))]
        for k in angle_rows:
            y[k] = wrap_pi(y[k])
        S = madd(mm(mm(H, self.P), tr(H)), R)
        return y, S

    def update(self, z, H, R, gate=None, angle_rows=()):
        """Returns (accepted, NIS)."""
        y, S = self.innovation(z, H, R, angle_rows)
        Si = inv(S)
        nis = quad(y, Si)
        if gate is not None and nis > gate:
            return False, nis
        K = mm(mm(self.P, tr(H)), Si)
        self.x = [xi + d for xi, d in zip(self.x, mv(K, y))]
        IKH = madd(eye(4), mm(K, H), -1.0)
        self.P = madd(mm(mm(IKH, self.P), tr(IKH)), mm(mm(K, R), tr(K)))  # Joseph form
        return True, nis

    def update_gnss(self, z, gate):
        H = [[1, 0, 0, 0], [0, 1, 0, 0]]
        R = [[GNSS_SIGMA_M ** 2, 0], [0, GNSS_SIGMA_M ** 2]]
        return self.update(list(z), H, R, gate)

    def update_radar(self, fix, psi_m, gate):
        """Radar fix observes position and, through the matched heading, the compass bias:
        b = psi_compass - psi_radar."""
        H = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]
        C = fix.cov
        sgn = (1, 1, -1)
        R = [[C[i][j] * sgn[i] * sgn[j] for j in range(3)] for i in range(3)]
        R[2][2] += SIGMA_PSI_RAD ** 2  # the compass sample in z carries its own noise
        z = [fix.x, fix.y, wrap_pi(psi_m - fix.psi)]
        return self.update(z, H, R, gate, angle_rows=(2,))

    def sigma_major(self):
        a, b, d = self.P[0][0], self.P[0][1], self.P[1][1]
        return math.sqrt(0.5 * (a + d) + math.hypot(0.5 * (a - d), b))

    def heading(self, psi_m):
        return wrap_pi(psi_m - self.x[2])


class Navigator:
    """Configurations:
      dr         dead reckoning only
      gnss_dr    GNSS + DR, per-fix innovation gate, no monitor (typical autopilot)
      single     GNSS + radar + DR in one filter, per-measurement gates only
      radar_dr   radar + DR, GNSS never used
      monitor    'single' plus a GNSS-free sub-filter, solution-separation test, GNSS exclusion
    """

    def __init__(self, mode, x0, y0):
        self.mode = mode
        self.main = Ekf(x0, y0)
        self.sub = Ekf(x0, y0) if mode == "monitor" else None
        self.excluded = False
        self.alarm = False
        self.ss_count = 0
        self.readmit_count = 0
        self.events = []
        self.last_ss = 0.0
        self.gnss_rejects = 0
        self.sub_fix_times = []
        self.bias_win = []
        self.last_bias = 0.0
        self.ss_clear = 0

    def use_gnss(self):
        return self.mode in ("gnss_dr", "single", "monitor")

    def use_radar(self):
        return self.mode in ("single", "radar_dr", "monitor")

    def predict(self, psi_m, v_m, dt):
        self.main.predict(psi_m, v_m, dt)
        if self.sub:
            self.sub.predict(psi_m, v_m, dt)

    def radar_prior(self):
        """Filter whose state seeds the radar search window."""
        return self.sub if self.sub else self.main

    def on_radar(self, t, fix, psi_m):
        res = {}
        if not (self.use_radar() and fix.ok):
            return res
        res["main"] = self.main.update_radar(fix, psi_m, CHI2_3DOF_999)
        if self.sub:
            res["sub"] = self.sub.update_radar(fix, psi_m, CHI2_3DOF_999)
            if res["sub"][0]:
                self.sub_fix_times.append(t)
        return res

    def on_gnss(self, t, z):
        if z is None:
            self.bias_win = []
        if not self.use_gnss() or z is None:
            return None
        if self.excluded:
            _, S = self.main.innovation(list(z), [[1, 0, 0, 0], [0, 1, 0, 0]],
                                        [[GNSS_SIGMA_M ** 2, 0], [0, GNSS_SIGMA_M ** 2]])
            y = [z[0] - self.main.x[0], z[1] - self.main.x[1]]
            nis = quad(y, inv(S))
            self.readmit_count = self.readmit_count + 1 if nis < READMIT_NIS else 0
            if self.readmit_count >= READMIT_S:
                self.excluded = False
                self.alarm = False
                self.events.append((t, "fix_readmitted", f"GNSS consistent with radar/DR for {READMIT_S} s"))
            return False, nis
        if self.sub:
            self.bias_win = (self.bias_win + [(z[0] - self.sub.x[0], z[1] - self.sub.x[1])])[-BIAS_WINDOW_S:]
        ok, nis = self.main.update_gnss(z, CHI2_2DOF_999)
        self.gnss_rejects = 0 if ok else self.gnss_rejects + 1
        if self.gnss_rejects >= GNSS_RESET_S:
            # Autopilot-style recovery from a long GNSS lockout: trust GNSS again. A spoofer
            # exploits exactly this; the monitor catches the jump through solution separation.
            m = self.main
            m.x[0], m.x[1] = z
            for i in range(4):
                for j in range(4):
                    if i < 2 or j < 2:
                        m.P[i][j] = 0.0
            m.P[0][0] = m.P[1][1] = GNSS_SIGMA_M ** 2
            self.gnss_rejects = 0
            self.events.append((t, "gnss_reset", f"GNSS gated out {GNSS_RESET_S} s, position reset to GNSS"))
        return ok, nis

    def check(self, t):
        """Solution separation main (with GNSS) vs sub (without). Run once per epoch after updates.
        Detection raises the alarm; exclusion also needs a GNSS-free reference that is actually
        being fixed by radar, otherwise a wrong radar lock would get good GNSS excluded."""
        if not self.sub or self.excluded:
            return
        d = [self.main.x[0] - self.sub.x[0], self.main.x[1] - self.sub.x[1]]
        S = [[self.sub.P[i][j] - self.main.P[i][j] for j in range(2)] for i in range(2)]
        if S[0][0] * S[1][1] - S[0][1] ** 2 <= 0 or S[0][0] <= 0:
            S = [[self.sub.P[i][j] for j in range(2)] for i in range(2)]
        S[0][0] += SS_FLOOR_M ** 2
        S[1][1] += SS_FLOOR_M ** 2
        self.last_ss = quad(d, inv(S))
        self.last_bias = self._bias_test()
        over = max(self.last_ss, self.last_bias) > SS_THRESHOLD
        self.ss_count = self.ss_count + 1 if over else 0
        self.ss_clear = 0 if over else self.ss_clear + 1
        if self.alarm and self.ss_clear >= ALARM_CLEAR_S:
            self.alarm = False
            self.events.append((t, "alarm_cleared", "GNSS and radar/DR agree again"))
        if self.ss_count < SS_PERSIST_S:
            return
        recent = [x for x in self.sub_fix_times if t - x <= ISOLATE_WINDOW_S]
        if len(recent) >= ISOLATE_MIN_FIXES:
            self.excluded = True
            self.alarm = True
            self.readmit_count = 0
            self.main = copy.deepcopy(self.sub)
            self.events.append((t, "spoof_suspected",
                                f"{self._which()} over {SS_THRESHOLD} for {SS_PERSIST_S} s, GNSS excluded"))
        elif not self.alarm:
            self.alarm = True
            self.events.append((t, "alarm_raised",
                                f"{self._which()}: GNSS and radar/DR disagree, "
                                f"only {len(recent)} radar fixes in {ISOLATE_WINDOW_S} s, cannot isolate"))

    def _bias_test(self):
        """Mean GNSS-minus-(radar+DR) offset over the window against its expected spread."""
        n = len(self.bias_win)
        if n < BIAS_WINDOW_S:
            return 0.0
        m = [sum(v[0] for v in self.bias_win) / n, sum(v[1] for v in self.bias_win) / n]
        var = GNSS_BIAS_SIGMA_M ** 2 + GNSS_SIGMA_M ** 2 / n + SS_FLOOR_M ** 2
        S = [[self.sub.P[0][0] + var, self.sub.P[0][1]], [self.sub.P[1][0], self.sub.P[1][1] + var]]
        return quad(m, inv(S))

    def _which(self):
        return (f"GNSS-vs-radar/DR offset test {self.last_bias:.0f}" if self.last_bias >= self.last_ss
                else f"solution separation {self.last_ss:.0f}")

    def pl(self):
        return PL_K * self.main.sigma_major()
