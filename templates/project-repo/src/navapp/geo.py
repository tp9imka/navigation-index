"""Local ENU <=> WGS84 geodetic, flat-earth approximation. Fine for a few km; use pyproj beyond."""
from __future__ import annotations

import math

WGS84_A = 6378137.0
WGS84_E2 = 6.69437999014e-3


def _radii(lat_deg: float) -> tuple[float, float]:
    s = math.sin(math.radians(lat_deg))
    w = math.sqrt(1.0 - WGS84_E2 * s * s)
    meridian = WGS84_A * (1.0 - WGS84_E2) / w ** 3
    prime_vertical = WGS84_A / w
    return meridian, prime_vertical


def enu_to_geodetic(east: float, north: float, lat0: float, lon0: float) -> tuple[float, float]:
    rm, rn = _radii(lat0)
    lat = lat0 + math.degrees(north / rm)
    lon = lon0 + math.degrees(east / (rn * math.cos(math.radians(lat0))))
    return lat, lon


def geodetic_to_enu(lat: float, lon: float, lat0: float, lon0: float) -> tuple[float, float]:
    rm, rn = _radii(lat0)
    north = math.radians(lat - lat0) * rm
    east = math.radians(lon - lon0) * rn * math.cos(math.radians(lat0))
    return east, north
