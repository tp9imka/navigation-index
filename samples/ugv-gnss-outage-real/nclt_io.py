"""Readers for the NCLT sensor CSVs and ground truth, and the GNSS-to-truth frame alignment.

Column layouts (nclt.pdf and the tarball README; signs checked against truth in this sample):
  gps.csv, gps_rtk.csv  utime_us, mode, num_sats, lat_rad, lon_rad, alt_m, track, speed
  ms25.csv              utime_us, mag xyz, accel xyz [m/s^2], gyro xyz [rad/s]; body x fwd, z down
  ms25_euler.csv        utime_us, roll, pitch, heading [rad] (heading is magnetic, unused)
  wheels.csv            utime_us, left, right [m/s]
  kvh.csv               utime_us, heading [rad]; its rate is the negative of truth's yaw rate
  groundtruth.csv       utime_us, x, y, z, roll, pitch, heading; x north, y east, z down
"""
import bisect
import csv
import math
import os

EARTH_R = 6378137.0
FIX_MODES = (2, 3)  # gps.csv mode: 2 = 2-D fix, 3 = 3-D fix


def read_rows(path):
    out = []
    with open(path, newline="") as f:
        for r in csv.reader(f):
            try:
                vals = [float(x) for x in r]
            except ValueError:
                continue
            if vals and not math.isnan(vals[0]):
                out.append(vals)
    return out


class Truth:
    def __init__(self, rows):
        rows = [r for r in rows if not any(math.isnan(v) for v in r[:7])]
        rows.sort(key=lambda r: r[0])
        self.t0_us = rows[0][0]
        self.t = [(r[0] - self.t0_us) / 1e6 for r in rows]
        self.n = [r[1] for r in rows]
        self.e = [r[2] for r in rows]
        self.psi = [r[6] for r in rows]

    def span(self):
        return self.t[0], self.t[-1]

    def _idx(self, t):
        i = bisect.bisect_left(self.t, t)
        if i <= 0 or i >= len(self.t):
            return None
        return i

    def pos(self, t):
        i = self._idx(t)
        if i is None:
            return None
        f = (t - self.t[i - 1]) / (self.t[i] - self.t[i - 1])
        return (self.n[i - 1] + f * (self.n[i] - self.n[i - 1]),
                self.e[i - 1] + f * (self.e[i] - self.e[i - 1]))

    def heading(self, t):
        i = self._idx(t)
        if i is None:
            return None
        a, b = self.psi[i - 1], self.psi[i]
        d = wrap(b - a)
        f = (t - self.t[i - 1]) / (self.t[i] - self.t[i - 1])
        return wrap(a + f * d)

    def path_length(self, lo, hi):
        i, j = bisect.bisect_left(self.t, lo), bisect.bisect_right(self.t, hi)
        return sum(math.hypot(self.n[k + 1] - self.n[k], self.e[k + 1] - self.e[k]) for k in range(i, j - 1))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def latlon_to_ne(lat, lon, lat0, lon0):
    return EARTH_R * (lat - lat0), EARTH_R * math.cos(lat0) * (lon - lon0)


def gnss_fixes(rows, t0_us):
    """[(t_s, mode, lat, lon)] for rows with a 2-D or 3-D fix, sorted by time."""
    out = [((r[0] - t0_us) / 1e6, int(r[1]), r[3], r[4]) for r in rows
           if int(r[1]) in FIX_MODES and not math.isnan(r[3]) and not math.isnan(r[4])]
    out.sort()
    return out


def fit_rigid_2d(src, dst):
    """Least-squares rotation + translation with dst ~ R src + t (2-D Kabsch). Returns (theta, tn, te)."""
    k = len(src)
    ms = (sum(p[0] for p in src) / k, sum(p[1] for p in src) / k)
    md = (sum(q[0] for q in dst) / k, sum(q[1] for q in dst) / k)
    sxx = sxy = 0.0
    for p, q in zip(src, dst):
        a0, a1 = p[0] - ms[0], p[1] - ms[1]
        b0, b1 = q[0] - md[0], q[1] - md[1]
        sxx += a0 * b0 + a1 * b1
        sxy += a0 * b1 - a1 * b0
    th = math.atan2(sxy, sxx)
    c, s = math.cos(th), math.sin(th)
    return th, md[0] - (c * ms[0] - s * ms[1]), md[1] - (s * ms[0] + c * ms[1])


class Frame:
    """Maps lat/lon to the truth's local north/east frame."""

    def __init__(self, lat0, lon0, theta, tn, te):
        self.lat0, self.lon0, self.theta, self.tn, self.te = lat0, lon0, theta, tn, te

    def __call__(self, lat, lon):
        n, e = latlon_to_ne(lat, lon, self.lat0, self.lon0)
        c, s = math.cos(self.theta), math.sin(self.theta)
        return c * n - s * e + self.tn, s * n + c * e + self.te


def align_frame(rtk_fixes, truth):
    """Fit the lat/lon => truth-frame transform on RTK 3-D fixes only (never on the consumer GPS
    under test). Returns (Frame, residuals_m)."""
    lat0, lon0 = rtk_fixes[0][2], rtk_fixes[0][3]
    src, dst = [], []
    for t, mode, lat, lon in rtk_fixes:
        g = truth.pos(t)
        if mode == 3 and g is not None:
            src.append(latlon_to_ne(lat, lon, lat0, lon0))
            dst.append(g)
    frame = Frame(lat0, lon0, *fit_rigid_2d(src, dst))
    res = []
    for p, q in zip(src, dst):
        c, s = math.cos(frame.theta), math.sin(frame.theta)
        res.append(math.hypot(c * p[0] - s * p[1] + frame.tn - q[0], s * p[0] + c * p[1] + frame.te - q[1]))
    return frame, res


class Session:
    """Everything the loop needs, in seconds since the first valid truth sample."""

    def __init__(self, folder):
        j = lambda name: os.path.join(folder, name)
        self.truth = Truth(read_rows(j("groundtruth.csv")))
        t0 = self.truth.t0_us
        rel = lambda rows: [((r[0] - t0) / 1e6,) + tuple(r[1:]) for r in rows]
        self.imu = rel(read_rows(j("ms25.csv")))
        self.euler = rel(read_rows(j("ms25_euler.csv")))
        self.wheels = rel(read_rows(j("wheels.csv")))
        self.kvh = rel(read_rows(j("kvh.csv")))
        for lst in (self.imu, self.euler, self.wheels, self.kvh):
            lst.sort(key=lambda r: r[0])
        self.frame, self.align_residuals = align_frame(gnss_fixes(read_rows(j("gps_rtk.csv")), t0), self.truth)
        self.gps = [(t, mode) + self.frame(lat, lon)
                    for t, mode, lat, lon in gnss_fixes(read_rows(j("gps.csv")), t0)]
