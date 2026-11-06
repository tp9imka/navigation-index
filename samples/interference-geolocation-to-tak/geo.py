"""WGS84 geodetic <=> local ENU (metres), stdlib only."""
import math

WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)
ECEF_TO_GEODETIC_ITERATIONS = 6


def geodetic_to_ecef(lat, lon, h=0.0):
    la, lo = math.radians(lat), math.radians(lon)
    n = WGS84_A / math.sqrt(1 - WGS84_E2 * math.sin(la) ** 2)
    return ((n + h) * math.cos(la) * math.cos(lo),
            (n + h) * math.cos(la) * math.sin(lo),
            (n * (1 - WGS84_E2) + h) * math.sin(la))


def ecef_to_geodetic(x, y, z):
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - WGS84_E2))
    h = 0.0
    for _ in range(ECEF_TO_GEODETIC_ITERATIONS):
        n = WGS84_A / math.sqrt(1 - WGS84_E2 * math.sin(lat) ** 2)
        h = p / math.cos(lat) - n
        lat = math.atan2(z, p * (1 - WGS84_E2 * n / (n + h)))
    return math.degrees(lat), math.degrees(lon), h


class LocalFrame:
    """East-North-Up tangent plane anchored at (lat0, lon0, h0)."""

    def __init__(self, lat0, lon0, h0=0.0):
        self.lat0, self.lon0, self.h0 = lat0, lon0, h0
        self.origin = geodetic_to_ecef(lat0, lon0, h0)
        la, lo = math.radians(lat0), math.radians(lon0)
        self.rows = (
            (-math.sin(lo), math.cos(lo), 0.0),
            (-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)),
            (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)),
        )

    def to_enu(self, lat, lon, h=0.0):
        d = [a - b for a, b in zip(geodetic_to_ecef(lat, lon, h), self.origin)]
        return tuple(sum(r[i] * d[i] for i in range(3)) for r in self.rows)

    def to_geodetic(self, e, n, u=0.0):
        enu = (e, n, u)
        ecef = [self.origin[i] + sum(self.rows[r][i] * enu[r] for r in range(3)) for i in range(3)]
        return ecef_to_geodetic(*ecef)


def compass_bearing(from_en, to_en):
    """Bearing in degrees clockwise from north between two local (e, n) points."""
    return math.degrees(math.atan2(to_en[0] - from_en[0], to_en[1] - from_en[1])) % 360.0


def wrap_deg(a):
    """Wrap an angle difference into [-180, 180)."""
    return (a + 180.0) % 360.0 - 180.0


BEARING_PROBE_M = 1000.0


def bearing_in_frame(frame, lat, lon, bearing_deg):
    """Re-express a bearing measured against local true north at (lat, lon) in the grid
    of `frame` (north differs between tangent planes by the meridian convergence)."""
    local = LocalFrame(lat, lon)
    b = math.radians(bearing_deg)
    plat, plon, ph = local.to_geodetic(BEARING_PROBE_M * math.sin(b), BEARING_PROBE_M * math.cos(b))
    return compass_bearing(frame.to_enu(lat, lon)[:2], frame.to_enu(plat, plon, ph)[:2])
