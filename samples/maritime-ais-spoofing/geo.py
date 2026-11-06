"""Small spherical-earth helpers (stdlib). Good to ~0.5% at AIS scales."""
import math

EARTH_R_M = 6371008.8


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R_M * math.asin(min(1.0, math.sqrt(a)))


def bearing_deg(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360.0


def destination(lat, lon, bearing, dist_m):
    p1, l1 = math.radians(lat), math.radians(lon)
    b, d = math.radians(bearing), dist_m / EARTH_R_M
    p2 = math.asin(math.sin(p1) * math.cos(d) + math.cos(p1) * math.sin(d) * math.cos(b))
    l2 = l1 + math.atan2(math.sin(b) * math.sin(d) * math.cos(p1), math.cos(d) - math.sin(p1) * math.sin(p2))
    return math.degrees(p2), (math.degrees(l2) + 540.0) % 360.0 - 180.0


def angle_diff_deg(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def to_enu(lat0, lon0, lat, lon):
    """Equirectangular local tangent approximation, metres east/north of (lat0, lon0)."""
    x = math.radians(lon - lon0) * EARTH_R_M * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * EARTH_R_M
    return x, y


def circumradius_m(p0, p1, p2):
    """Radius of the circle through three (lat, lon) points; inf if collinear."""
    ax, ay = 0.0, 0.0
    bx, by = to_enu(p0[0], p0[1], p1[0], p1[1])
    cx, cy = to_enu(p0[0], p0[1], p2[0], p2[1])
    a, b, c = math.hypot(bx - cx, by - cy), math.hypot(cx - ax, cy - ay), math.hypot(bx - ax, by - ay)
    cross = abs(bx * cy - by * cx)
    if cross < 1e-9:
        return math.inf
    return a * b * c / (2.0 * cross)
