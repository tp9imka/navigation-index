"""Robust bearing-only triangulation (stdlib): RANSAC pair intersections, then
range-weighted Gauss-Newton on angle residuals with iterative outlier rejection."""
import math
import random

from geo import LocalFrame, bearing_in_frame, wrap_deg

CHI2_2DOF_95 = 5.991
REJECT_K_SIGMA = 3.0
RANSAC_PAIRS = 300
RANSAC_INLIER_DEG = 10.0
GN_ITERATIONS = 15
MIN_CROSS_ANGLE_DEG = 10.0
MAX_REJECT_ROUNDS = 5


def _pred_bearing(x, y, s):
    return math.degrees(math.atan2(x - s[0], y - s[1])) % 360.0


def _intersect(s1, b1, s2, b2):
    d1 = (math.sin(math.radians(b1)), math.cos(math.radians(b1)))
    d2 = (math.sin(math.radians(b2)), math.cos(math.radians(b2)))
    det = d1[0] * -d2[1] + d2[0] * d1[1]
    if abs(det) < math.sin(math.radians(MIN_CROSS_ANGLE_DEG)):
        return None
    rx, ry = s2[0] - s1[0], s2[1] - s1[1]
    t1 = (rx * -d2[1] + d2[0] * ry) / det
    t2 = (d1[0] * ry - d1[1] * rx) / det
    if t1 <= 0 or t2 <= 0:  # behind a sensor
        return None
    return s1[0] + t1 * d1[0], s1[1] + t1 * d1[1]


def _inv2(m):
    a, b, c, d = m[0][0], m[0][1], m[1][0], m[1][1]
    det = a * d - b * c
    return [[d / det, -b / det], [-c / det, a / det]]


def _gauss_newton(x, y, obs):
    cov = None
    for _ in range(GN_ITERATIONS):
        h = [[0.0, 0.0], [0.0, 0.0]]
        g = [0.0, 0.0]
        for s, b, sig in obs:
            w = 1.0 / math.radians(sig) ** 2
            dx, dy = x - s[0], y - s[1]
            r2 = dx * dx + dy * dy
            jx, jy = dy / r2, -dx / r2
            res = math.radians(wrap_deg(b - _pred_bearing(x, y, s)))
            h[0][0] += w * jx * jx; h[0][1] += w * jx * jy; h[1][1] += w * jy * jy
            g[0] += w * jx * res; g[1] += w * jy * res
        h[1][0] = h[0][1]
        cov = _inv2(h)
        x += cov[0][0] * g[0] + cov[0][1] * g[1]
        y += cov[1][0] * g[0] + cov[1][1] * g[1]
    return x, y, cov


def ellipse(cov, chi2=CHI2_2DOF_95):
    """(semi_major_m, semi_minor_m, major_axis_bearing_deg) for an ENU 2x2 covariance."""
    a, b, d = cov[0][0], cov[0][1], cov[1][1]
    tr, det = a + d, a * d - b * b
    disc = math.sqrt(max(tr * tr / 4 - det, 0.0))
    l1, l2 = tr / 2 + disc, max(tr / 2 - disc, 0.0)
    ve, vn = (b, l1 - a) if abs(b) > 1e-12 else ((1.0, 0.0) if a >= d else (0.0, 1.0))
    return math.sqrt(chi2 * l1), math.sqrt(chi2 * l2), math.degrees(math.atan2(ve, vn)) % 180.0


def locate(bearings, sigma_deg, station_sigma=None, seed=0):
    """bearings: iterable of kraken.Bearing; sigma_deg default 1-sigma bearing noise,
    station_sigma optional {station_id: sigma_deg}. Returns lat/lon, ENU cov, inliers."""
    station_sigma = station_sigma or {}
    bearings = list(bearings)
    lat0 = sum(b.lat for b in bearings) / len(bearings)
    lon0 = sum(b.lon for b in bearings) / len(bearings)
    frame = LocalFrame(lat0, lon0)
    obs = [(frame.to_enu(b.lat, b.lon)[:2], bearing_in_frame(frame, b.lat, b.lon, b.bearing_deg),
            station_sigma.get(b.station_id, sigma_deg))
           for b in bearings]

    rng = random.Random(seed)
    best, best_n = None, -1
    for _ in range(RANSAC_PAIRS):
        (s1, b1, _), (s2, b2, _) = rng.sample(obs, 2)
        p = _intersect(s1, b1, s2, b2)
        if p is None:
            continue
        n = sum(abs(wrap_deg(b - _pred_bearing(p[0], p[1], s))) < RANSAC_INLIER_DEG for s, b, _ in obs)
        if n > best_n:
            best, best_n = p, n
    if best is None:
        raise ValueError("no usable bearing intersections (geometry too collinear?)")

    x, y = best
    inl = [o for o in obs if abs(wrap_deg(o[1] - _pred_bearing(x, y, o[0]))) < RANSAC_INLIER_DEG]
    for _ in range(MAX_REJECT_ROUNDS):
        x, y, cov = _gauss_newton(x, y, inl)
        new = [o for o in obs
               if abs(wrap_deg(o[1] - _pred_bearing(x, y, o[0]))) < REJECT_K_SIGMA * o[2]]
        if new == inl:
            break
        inl = new
    res = [wrap_deg(b - _pred_bearing(x, y, s)) for s, b, _ in inl]
    rms = math.sqrt(sum(r * r for r in res) / len(res))
    lat, lon, _ = frame.to_geodetic(x, y)
    return {"lat": lat, "lon": lon, "enu": (x, y), "frame": frame, "cov": cov,
            "n_used": len(inl), "n_total": len(obs), "residual_rms_deg": rms}
