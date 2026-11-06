"""Re-run ekf_outage.py with the hand-written EKF swapped for filterpy's ExtendedKalmanFilter.

Same mechanization, Jacobian, Q, R and gate; only covariance propagation, the innovation
covariance and the measurement update go through filterpy (Joseph-form update). If the two
tables agree, the matlite algebra in ekf_outage.py is not the source of the results.

  python3 filterpy_crosscheck.py            # seed 7, spoof 1.0 m/s, same table as ekf_outage.py
  python3 filterpy_crosscheck.py --sweep
"""

import argparse

import numpy as np
from filterpy.kalman import ExtendedKalmanFilter

import ekf_outage

H = np.zeros((2, 8))
H[0, 0] = H[1, 1] = 1.0
R = np.eye(2) * ekf_outage.GNSS_NOISE_SD**2


class FilterpyEkf(ekf_outage.Ekf):
    """Keeps the stdlib mechanize(); covariance and update are filterpy's."""

    def __init__(self, x0):
        super().__init__(x0)
        self.kf = ExtendedKalmanFilter(dim_x=8, dim_z=2)
        self.kf.P = np.array(self.P)
        self.kf.R = R
        self.kf.predict_x = lambda u=0: None  # mean is propagated by mechanize() at IMU rate

    def propagate_cov(self, dt):
        # reuse the stdlib F and Q by running the parent on a scratch copy of P
        self.P = self.kf.P.tolist()
        super().propagate_cov(dt)
        P_stdlib = np.array(self.P)
        self.kf.x = np.array(self.x).reshape(8, 1)
        self.kf.P = P_stdlib

    def innovation(self, zx, zy):
        y = np.array([zx - self.x[0], zy - self.x[1]])
        S = H @ self.kf.P @ H.T + R
        Si = np.linalg.inv(S)
        return y, Si, float(y @ Si @ y)

    def update(self, y, Si):
        self.kf.x = np.array(self.x).reshape(8, 1)
        z = (np.array(self.x[:2]) + y).reshape(2, 1)
        self.kf.update(z, HJacobian=lambda x: H, Hx=lambda x: x[:2])
        self.x = self.kf.x.ravel().tolist()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--spoof-rate", type=float, default=ekf_outage.SPOOF_RATE_MPS)
    ap.add_argument("--sweep", action="store_true")
    args = ap.parse_args()
    ekf_outage.Ekf = FilterpyEkf
    if args.sweep:
        ekf_outage.sweep(args.seed)
    else:
        ekf_outage.report(args.seed, args.spoof_rate)
