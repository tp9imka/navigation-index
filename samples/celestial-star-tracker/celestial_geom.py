"""Stdlib geometry for a celestial position fix from star elevations above a local vertical.

Angles are radians unless a name ends in _deg / _arcmin. Longitude is east-positive, GHA is
west-positive (local hour angle t = GHA + lon), azimuth is from north through east.

Inputs to the fix are, per identified star, its apparent Greenwich hour angle and
declination at the measurement time (from an ephemeris, e.g. skyfield) and its observed
elevation h = asin(star_vector . up_vector), where both vectors are in the camera/IMU
frame. No camera azimuth is needed, only the vertical.
"""
import math

ARCMIN = math.radians(1 / 60)
ARCSEC = math.radians(1 / 3600)
R_EARTH_MEAN = 6371008.8          # IUGG mean radius [m]
NAUTICAL_MILE = 1852.0            # [m], defined as 1 arcmin of latitude on a sphere
OMEGA_EARTH = 7.2921150e-5        # sidereal rotation rate [rad/s]
G0 = 9.80665                      # [m/s^2]


def alt_az(lat, lon, gha, dec):
    """Altitude and azimuth of a body with (GHA, dec) seen from (lat, lon)."""
    t = gha + lon
    sh = math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(t)
    h = math.asin(max(-1.0, min(1.0, sh)))
    az = math.atan2(-math.cos(dec) * math.sin(t),
                    math.sin(dec) * math.cos(lat) - math.cos(dec) * math.cos(t) * math.sin(lat))
    return h, az % (2 * math.pi)


def unit_from_lat_lon(lat, lon):
    return (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))


def lat_lon_from_unit(v):
    x, y, z = v
    return math.atan2(z, math.hypot(x, y)), math.atan2(y, x)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def rotate(v, axis, angle):
    """Rodrigues rotation of v about a unit axis."""
    c, s = math.cos(angle), math.sin(angle)
    k = axis
    kxv = cross(k, v)
    kv = dot(k, v)
    return tuple(v[i] * c + kxv[i] * s + k[i] * kv * (1 - c) for i in range(3))


def tilt(v, angle, direction):
    """Tilt unit vector v by `angle` towards the horizontal azimuth `direction` (ENU frame,
    v near up). Used to model an IMU level error."""
    horiz = (math.sin(direction), math.cos(direction), 0.0)
    axis = norm(cross(v, horiz))
    return rotate(v, axis, angle)


def enu_from_alt_az(h, az):
    return (math.cos(h) * math.sin(az), math.cos(h) * math.cos(az), math.sin(h))


def elevation(star_vec, up_vec):
    return math.asin(max(-1.0, min(1.0, dot(norm(star_vec), norm(up_vec)))))


def refraction_bennett(h_apparent, pressure_hpa=1010.0, temp_c=10.0):
    """Bennett (1982) refraction for an apparent (refracted) altitude, scaled for P and T.
    Returns R in radians; true altitude = apparent - R."""
    hd = math.degrees(h_apparent)
    r_arcmin = 1.0 / math.tan(math.radians(hd + 7.31 / (hd + 4.4)))
    r_arcmin *= (pressure_hpa / 1010.0) * (283.0 / (273.0 + temp_c))
    return max(0.0, r_arcmin) * ARCMIN


def solve_fix(obs, lat0=0.0, lon0=0.0, iters=20, tol=1e-12):
    """Least-squares celestial fix (Marcq St Hilaire intercept method, iterated).

    obs: list of (gha, dec, h_obs) with h_obs already corrected for refraction.
    Returns dict(lat, lon, rms (rad), n, cov ((2x2) unit-weight covariance of lat, lon*cos(lat)
    in rad^2 per rad^2 of elevation noise), az_spread_deg, converged).
    """
    lat, lon = lat0, lon0
    converged = False
    for _ in range(iters):
        ata = [[0.0, 0.0], [0.0, 0.0]]
        atb = [0.0, 0.0]
        for gha, dec, h_obs in obs:
            h, az = alt_az(lat, lon, gha, dec)
            # dh/dlat = cos(az); dh/d(east distance in rad of arc) = sin(az)
            row = (math.cos(az), math.sin(az))
            r = h_obs - h
            for i in range(2):
                atb[i] += row[i] * r
                for j in range(2):
                    ata[i][j] += row[i] * row[j]
        det = ata[0][0] * ata[1][1] - ata[0][1] * ata[1][0]
        if abs(det) < 1e-12:
            return {"lat": lat, "lon": lon, "rms": float("nan"), "n": len(obs), "cov": None,
                    "converged": False, "singular": True}
        inv = [[ata[1][1] / det, -ata[0][1] / det], [-ata[1][0] / det, ata[0][0] / det]]
        d_n = inv[0][0] * atb[0] + inv[0][1] * atb[1]
        d_e = inv[1][0] * atb[0] + inv[1][1] * atb[1]
        lat += d_n
        lon += d_e / max(1e-9, math.cos(lat))
        if math.hypot(d_n, d_e) < tol:
            converged = True
            break
    res = [h_obs - alt_az(lat, lon, gha, dec)[0] for gha, dec, h_obs in obs]
    rms = math.sqrt(sum(r * r for r in res) / len(res))
    azs = [alt_az(lat, lon, g, d)[1] for g, d, _ in obs]
    return {"lat": lat, "lon": (lon + math.pi) % (2 * math.pi) - math.pi, "rms": rms,
            "n": len(obs), "cov": inv, "converged": converged, "singular": False,
            "az_spread_deg": math.degrees(circular_spread(azs))}


def circular_spread(angles):
    """1 - mean resultant length mapped to an angle-like spread (0 = all same azimuth)."""
    c = sum(math.cos(a) for a in angles) / len(angles)
    s = sum(math.sin(a) for a in angles) / len(angles)
    return math.acos(max(-1.0, min(1.0, math.hypot(c, s))))


def zenith_fix(zenith_earth_fixed):
    """Direct fix: the local vertical expressed in an Earth-fixed frame is (lat, lon)."""
    return lat_lon_from_unit(norm(zenith_earth_fixed))


def great_circle_m(lat1, lon1, lat2, lon2, radius=R_EARTH_MEAN):
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * radius * math.asin(math.sqrt(min(1.0, a)))


def position_error_from_level_error(level_err, radius=R_EARTH_MEAN):
    """A vertical tilted by e moves the zenith, and the fix, by e of arc: d = R * e."""
    return radius * level_err


def east_error_from_time_error(dt_s, lat, radius=R_EARTH_MEAN):
    """A clock error dt rotates the sky by OMEGA_EARTH*dt: pure east-west error."""
    return radius * math.cos(lat) * OMEGA_EARTH * dt_s


def level_error_from_accel(a_horizontal):
    """Unmodelled horizontal specific force (accelerometer bias or vehicle acceleration, m/s^2)
    tilts the sensed gravity vector by atan(a/g)."""
    return math.atan2(a_horizontal, G0)
