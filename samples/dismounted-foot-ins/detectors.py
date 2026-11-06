"""Zero-velocity (stance) detectors for a foot-mounted IMU.

Definitions follow Skog et al. 2010 and match utiasSTARS/pyshoe ins_tools/EKF.py
(non-overlapping windows of W samples for SHOE/ARED/AMVD, sliding window for MBGTD),
so the same thresholds G apply. Each function returns the test statistic per sample;
stance is statistic < G.
"""
import math

GRAVITY = 9.8029  # pyshoe's value for Toronto
SIGMA_A = 0.00098  # pyshoe hallway setting ("microstrain"), m/s^2
SIGMA_W = 8.7266463e-5  # rad/s
DEFAULT_W = 5


def _blockwise(n, w, stat_of_window):
    out = [0.0] * n
    for k in range(0, n - w + 1, w):
        t = stat_of_window(k) / w
        for s in range(k, k + w):
            out[s] = t
    return out


def shoe(acc, gyro, w=DEFAULT_W, sigma_a=SIGMA_A, sigma_w=SIGMA_W, g=GRAVITY):
    """Stance hypothesis optimal detector (GLRT on acc direction + gyro energy)."""
    inv_a, inv_w = 1.0 / sigma_a ** 2, 1.0 / sigma_w ** 2

    def window(k):
        mx = sum(a[0] for a in acc[k:k + w]) / w
        my = sum(a[1] for a in acc[k:k + w]) / w
        mz = sum(a[2] for a in acc[k:k + w]) / w
        n = math.sqrt(mx * mx + my * my + mz * mz)
        ux, uy, uz = g * mx / n, g * my / n, g * mz / n
        t = 0.0
        for s in range(k, k + w):
            a, r = acc[s], gyro[s]
            t += inv_a * ((a[0] - ux) ** 2 + (a[1] - uy) ** 2 + (a[2] - uz) ** 2)
            t += inv_w * (r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
        return t

    return _blockwise(len(acc), w, window)


def ared(gyro, w=DEFAULT_W):
    """Angular rate energy detector: mean |omega|^2 over the window."""
    return _blockwise(len(gyro), w, lambda k: sum(r[0] ** 2 + r[1] ** 2 + r[2] ** 2 for r in gyro[k:k + w]))


def amvd(acc, w=DEFAULT_W):
    """Acceleration moving variance detector."""
    def window(k):
        blk = acc[k:k + w]
        m = [sum(a[i] for a in blk) / w for i in range(3)]
        return sum((a[0] - m[0]) ** 2 + (a[1] - m[1]) ** 2 + (a[2] - m[2]) ** 2 for a in blk)
    return _blockwise(len(acc), w, window)


def mbgtd(acc, w=DEFAULT_W):
    """Memory-based graph theoretic detector (Wagstaff et al. 2017): max mean distance
    between the acc samples on either side of every split of a sliding window."""
    n = len(acc)
    out = [1.0] * n

    def d(i, j):
        a, b = acc[i], acc[j]
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)

    for k in range(n - w + 1):
        dist = [[d(k + i, k + j) if i < j else 0.0 for j in range(w)] for i in range(w)]
        best = 0.0
        for a in range(w - 1):
            for b in range(a + 1, w):
                tot = sum(dist[i][j] for i in range(a + 1) for j in range(b, w))
                best = max(best, tot / ((b - a) * (w - b + 1)))
        out[k] = best
    return out


def stance(stat, threshold):
    return [t < threshold for t in stat]
