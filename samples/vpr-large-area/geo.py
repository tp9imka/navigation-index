"""Stdlib-only geo math for the tile database: grid layout, affine pixel <=> map metres, yaw, recall."""
import math

EARTH_R_M = 6371008.8


def tile_centres(width_m, height_m, tile_m, stride_m):
    """Centres of whole tiles as (east, south) metre offsets from the map's top-left corner, row-major."""
    nx = int(math.floor((width_m - tile_m) / stride_m + 1e-9)) + 1
    ny = int(math.floor((height_m - tile_m) / stride_m + 1e-9)) + 1
    if nx <= 0 or ny <= 0 or tile_m > min(width_m, height_m):
        return []
    return [(tile_m / 2 + i * stride_m, tile_m / 2 + j * stride_m) for j in range(ny) for i in range(nx)]


def grid_worst_case_m(stride_m):
    """Largest distance from any point inside the grid to its nearest centre (square grid)."""
    return stride_m * math.sqrt(2) / 2


def offset_to_world(origin_e, origin_n, east_m, south_m):
    """(east, south) offset from a north-up map's top-left corner => UTM (easting, northing)."""
    return origin_e + east_m, origin_n - south_m


def world_to_px(e, n, origin_e, origin_n, gsd):
    """UTM => (col, row) in a north-up raster whose top-left pixel corner is (origin_e, origin_n)."""
    return (e - origin_e) / gsd, (origin_n - n) / gsd


def px_to_world(col, row, origin_e, origin_n, gsd):
    return origin_e + col * gsd, origin_n - row * gsd


def frame_offset_to_source(du, dv, yaw_deg):
    """Frame pixel offset from centre => source pixel offset, synth_frames.make_frame yaw convention."""
    t = math.radians(yaw_deg)
    return math.cos(t) * du + math.sin(t) * dv, -math.sin(t) * du + math.cos(t) * dv


def angle_diff_deg(a, b):
    """Smallest absolute difference between two angles in degrees, in [0, 180]."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R_M * math.asin(math.sqrt(a))


def recall_at(dists_m, ks=(1, 5, 10), radii=(50, 100, 250)):
    """dists_m: per query, the list of ranked candidates' distances to truth. Returns {'R@k<=r': fraction}."""
    n = len(dists_m)
    out = {}
    for r in radii:
        for k in ks:
            hits = sum(1 for row in dists_m if any(d <= r for d in row[:k]))
            out[f"R@{k}<={r}m"] = hits / n if n else 0.0
    return out
