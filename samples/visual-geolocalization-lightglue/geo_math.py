"""Stdlib geometry for map-relative visual localization.

- Affine geotransform (rasterio `Affine` order a, b, c, d, e, f): pixel <-> map coords.
- 3x3 homography point mapping (drone frame pixel -> tile pixel).
- WGS84 UTM forward/inverse (Snyder, USGS PP 1395), for tiles in a projected CRS.
- Haversine distance for error reporting.
"""

import math

WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563
UTM_K0 = 0.9996
UTM_FALSE_EASTING = 500000.0
UTM_FALSE_NORTHING_SOUTH = 10000000.0
MEAN_EARTH_RADIUS_M = 6371008.8


def from_gdal(gt):
    """GDAL GetGeoTransform() tuple (c, a, b, f, d, e) -> rasterio order (a, b, c, d, e, f)."""
    c, a, b, f, d, e = gt
    return (a, b, c, d, e, f)


def pixel_to_world(transform, col, row):
    """Map coords of a pixel position. Use col + 0.5, row + 0.5 for a pixel centre."""
    a, b, c, d, e, f = transform
    return a * col + b * row + c, d * col + e * row + f


def world_to_pixel(transform, x, y):
    a, b, c, d, e, f = transform
    det = a * e - b * d
    if det == 0:
        raise ValueError("singular geotransform")
    dx, dy = x - c, y - f
    return (e * dx - b * dy) / det, (-d * dx + a * dy) / det


def apply_homography(H, x, y):
    """Map (x, y) through a 3x3 homography given as nested lists or a numpy array."""
    u = H[0][0] * x + H[0][1] * y + H[0][2]
    v = H[1][0] * x + H[1][1] * y + H[1][2]
    w = H[2][0] * x + H[2][1] * y + H[2][2]
    if abs(w) < 1e-12:
        raise ValueError("point maps to infinity (degenerate homography)")
    return u / w, v / w


def _ellipsoid():
    e2 = WGS84_F * (2 - WGS84_F)
    return e2, e2 / (1 - e2)


def _meridian_arc(lat):
    e2, _ = _ellipsoid()
    e4, e6 = e2 * e2, e2 * e2 * e2
    return WGS84_A * (
        (1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * lat
        - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * lat)
        + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * lat)
        - (35 * e6 / 3072) * math.sin(6 * lat)
    )


def utm_central_meridian(zone):
    return -183.0 + 6.0 * zone


def latlon_to_utm(lat_deg, lon_deg, zone, south=False):
    e2, ep2 = _ellipsoid()
    lat = math.radians(lat_deg)
    dlon = math.radians(lon_deg - utm_central_meridian(zone))
    n = WGS84_A / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    t = math.tan(lat) ** 2
    c = ep2 * math.cos(lat) ** 2
    a = math.cos(lat) * dlon
    m = _meridian_arc(lat)
    x = UTM_K0 * n * (a + (1 - t + c) * a ** 3 / 6
                      + (5 - 18 * t + t * t + 72 * c - 58 * ep2) * a ** 5 / 120)
    y = UTM_K0 * (m + n * math.tan(lat) * (
        a * a / 2 + (5 - t + 9 * c + 4 * c * c) * a ** 4 / 24
        + (61 - 58 * t + t * t + 600 * c - 330 * ep2) * a ** 6 / 720))
    return x + UTM_FALSE_EASTING, y + (UTM_FALSE_NORTHING_SOUTH if south else 0.0)


def utm_to_latlon(easting, northing, zone, south=False):
    e2, ep2 = _ellipsoid()
    x = easting - UTM_FALSE_EASTING
    y = northing - (UTM_FALSE_NORTHING_SOUTH if south else 0.0)
    m = y / UTM_K0
    mu = m / (WGS84_A * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
            + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
            + (151 * e1 ** 3 / 96) * math.sin(6 * mu)
            + (1097 * e1 ** 4 / 512) * math.sin(8 * mu))
    n1 = WGS84_A / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    t1 = math.tan(phi1) ** 2
    c1 = ep2 * math.cos(phi1) ** 2
    r1 = WGS84_A * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2) ** 1.5
    d = x / (n1 * UTM_K0)
    lat = phi1 - (n1 * math.tan(phi1) / r1) * (
        d * d / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 * c1 - 9 * ep2) * d ** 4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 * t1 - 252 * ep2 - 3 * c1 * c1) * d ** 6 / 720)
    lon = (d - (1 + 2 * t1 + c1) * d ** 3 / 6
           + (5 - 2 * c1 + 28 * t1 - 3 * c1 * c1 + 8 * ep2 + 24 * t1 * t1) * d ** 5 / 120) / math.cos(phi1)
    return math.degrees(lat), utm_central_meridian(zone) + math.degrees(lon)


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * MEAN_EARTH_RADIUS_M * math.asin(math.sqrt(h))


def frame_center_to_world(H, frame_w, frame_h, tile_transform):
    """Drone frame centre -> tile pixel (via H) -> map coords (via geotransform).

    H maps frame keypoint coords to tile keypoint coords, as OpenCV findHomography
    returns it for LightGlue matches. Keypoints use the integer-at-pixel-centre
    convention; a rasterio/GDAL affine puts integers on pixel corners, hence the 0.5.
    """
    tx, ty = apply_homography(H, (frame_w - 1) / 2.0, (frame_h - 1) / 2.0)
    return pixel_to_world(tile_transform, tx + 0.5, ty + 0.5)
