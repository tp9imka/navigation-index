"""Geofence, altitude and mission checks for the MAVLink MCP server. Stdlib only.

Geometry runs in a local tangent plane (equirectangular around the fence centroid),
which is accurate to well under 1 m for fences a few km across. Not for fences that
span tens of km or cross the antimeridian/poles.
"""
import json
import math

EARTH_RADIUS_M = 6_371_008.8
DEFAULT_MIN_ALT_M = 5.0
DEFAULT_MAX_ALT_M = 60.0
DEFAULT_MARGIN_M = 5.0
DEFAULT_MAX_LEG_M = 1000.0
MAX_WAYPOINTS = 200
MIN_SURVEY_SPACING_M = 5.0
MAX_SURVEY_LINES = 100


class SafetyError(ValueError):
    pass


class Fence:
    """Inclusion polygon (lat/lon degrees, WGS84) plus altitude band relative to home."""

    def __init__(self, polygon, min_alt_m=DEFAULT_MIN_ALT_M, max_alt_m=DEFAULT_MAX_ALT_M,
                 margin_m=DEFAULT_MARGIN_M, max_leg_m=DEFAULT_MAX_LEG_M):
        if len(polygon) < 3:
            raise SafetyError("fence polygon needs at least 3 vertices")
        for lat, lon in polygon:
            check_lat_lon(lat, lon)
        if not 0 <= min_alt_m < max_alt_m:
            raise SafetyError("need 0 <= min_alt_m < max_alt_m")
        self.polygon = [(float(a), float(b)) for a, b in polygon]
        self.min_alt_m = float(min_alt_m)
        self.max_alt_m = float(max_alt_m)
        self.margin_m = float(margin_m)
        self.max_leg_m = float(max_leg_m)
        self.lat0 = sum(p[0] for p in self.polygon) / len(self.polygon)
        self.lon0 = sum(p[1] for p in self.polygon) / len(self.polygon)
        self.xy = [self.to_xy(lat, lon) for lat, lon in self.polygon]

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            cfg = json.load(f)
        return cls(cfg["polygon"], cfg.get("min_alt_m", DEFAULT_MIN_ALT_M),
                   cfg.get("max_alt_m", DEFAULT_MAX_ALT_M), cfg.get("margin_m", DEFAULT_MARGIN_M),
                   cfg.get("max_leg_m", DEFAULT_MAX_LEG_M))

    def describe(self):
        return {"polygon": self.polygon, "min_alt_m": self.min_alt_m,
                "max_alt_m": self.max_alt_m, "margin_m": self.margin_m,
                "max_leg_m": self.max_leg_m}

    def to_xy(self, lat, lon):
        """(east_m, north_m) from the fence centroid."""
        x = math.radians(lon - self.lon0) * EARTH_RADIUS_M * math.cos(math.radians(self.lat0))
        y = math.radians(lat - self.lat0) * EARTH_RADIUS_M
        return x, y

    def to_latlon(self, x, y):
        lat = self.lat0 + math.degrees(y / EARTH_RADIUS_M)
        lon = self.lon0 + math.degrees(x / (EARTH_RADIUS_M * math.cos(math.radians(self.lat0))))
        return lat, lon

    def edges(self):
        n = len(self.xy)
        return [(self.xy[i], self.xy[(i + 1) % n]) for i in range(n)]

    def contains(self, lat, lon):
        """Inside the polygon and at least margin_m from every edge."""
        p = self.to_xy(lat, lon)
        if not point_in_polygon(p, self.xy):
            return False
        return min(point_segment_distance(p, a, b) for a, b in self.edges()) >= self.margin_m

    def check_alt(self, rel_alt_m):
        if not isinstance(rel_alt_m, (int, float)) or math.isnan(rel_alt_m):
            raise SafetyError("altitude must be a number (metres above home)")
        if not self.min_alt_m <= rel_alt_m <= self.max_alt_m:
            raise SafetyError(f"altitude {rel_alt_m} m outside [{self.min_alt_m}, "
                              f"{self.max_alt_m}] m above home")

    def check_point(self, lat, lon, what="target"):
        check_lat_lon(lat, lon)
        if not self.contains(lat, lon):
            raise SafetyError(f"{what} ({lat:.6f}, {lon:.6f}) is outside the geofence "
                              f"(or within {self.margin_m} m of its edge)")

    def check_leg(self, start, end, what="leg"):
        """Straight leg between two (lat, lon) points must stay inside the fence."""
        a, b = self.to_xy(*start), self.to_xy(*end)
        length = math.dist(a, b)
        if length > self.max_leg_m:
            raise SafetyError(f"{what} is {length:.0f} m, longer than max_leg_m {self.max_leg_m:.0f}")
        for e1, e2 in self.edges():
            if segments_intersect(a, b, e1, e2):
                raise SafetyError(f"{what} crosses the geofence boundary")
        return length

    def check_goto(self, lat, lon, rel_alt_m, current=None):
        """current: (lat, lon) of the vehicle, or None when unknown (endpoint check only)."""
        self.check_alt(rel_alt_m)
        self.check_point(lat, lon)
        out = {"target_inside": True, "path_checked": current is not None}
        if current is not None:
            if not point_in_polygon(self.to_xy(*current), self.xy):
                raise SafetyError("vehicle is outside the geofence; only RTL/LAND are allowed")
            out["leg_m"] = round(self.check_leg(current, (lat, lon)), 1)
        return out

    def check_mission(self, waypoints, start=None):
        """waypoints: list of dicts with lat, lon, rel_alt_m. start: (lat, lon) or None."""
        if not waypoints:
            raise SafetyError("mission has no waypoints")
        if len(waypoints) > MAX_WAYPOINTS:
            raise SafetyError(f"mission has {len(waypoints)} waypoints, limit {MAX_WAYPOINTS}")
        total = 0.0
        prev = start
        for i, wp in enumerate(waypoints):
            try:
                lat, lon, alt = float(wp["lat"]), float(wp["lon"]), float(wp["rel_alt_m"])
            except (KeyError, TypeError, ValueError):
                raise SafetyError(f"waypoint {i} needs numeric lat, lon, rel_alt_m")
            self.check_alt(alt)
            self.check_point(lat, lon, what=f"waypoint {i}")
            if prev is not None:
                total += self.check_leg(prev, (lat, lon), what=f"leg into waypoint {i}")
            prev = (lat, lon)
        return {"waypoints": len(waypoints), "path_m": round(total, 1),
                "start_checked": start is not None}


def check_lat_lon(lat, lon):
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (lat, lon)):
        raise SafetyError("lat/lon must be finite numbers in degrees")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise SafetyError(f"lat/lon out of range: {lat}, {lon}")


def point_in_polygon(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


def point_segment_distance(p, a, b):
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    seg2 = dx * dx + dy * dy
    t = 0.0 if seg2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / seg2))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def _orient(a, b, c):
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)


def segments_intersect(p1, p2, q1, q2):
    """Proper or touching intersection of two segments."""
    o1, o2 = _orient(p1, p2, q1), _orient(p1, p2, q2)
    o3, o4 = _orient(q1, q2, p1), _orient(q1, q2, p2)
    if o1 != o2 and o3 != o4:
        return True

    def on_seg(a, b, c):
        return (min(a[0], b[0]) - 1e-9 <= c[0] <= max(a[0], b[0]) + 1e-9 and
                min(a[1], b[1]) - 1e-9 <= c[1] <= max(a[1], b[1]) + 1e-9)
    return ((o1 == 0 and on_seg(p1, p2, q1)) or (o2 == 0 and on_seg(p1, p2, q2)) or
            (o3 == 0 and on_seg(q1, q2, p1)) or (o4 == 0 and on_seg(q1, q2, p2)))


def plan_survey(fence, area, spacing_m, rel_alt_m, heading_deg=0.0, inset_m=None):
    """Boustrophedon (lawnmower) waypoints over `area` (list of (lat, lon)), lines along
    heading_deg (degrees true). Each pass is clipped to the area and shortened by inset_m
    at both ends. The result is checked against the fence by the caller."""
    if spacing_m < MIN_SURVEY_SPACING_M:
        raise SafetyError(f"spacing_m must be >= {MIN_SURVEY_SPACING_M}")
    fence.check_alt(rel_alt_m)
    inset = fence.margin_m if inset_m is None else float(inset_m)
    pts = [fence.to_xy(lat, lon) for lat, lon in area]
    h = math.radians(heading_deg)
    ux, uy = math.sin(h), math.cos(h)      # along-track (east, north)
    vx, vy = math.cos(h), -math.sin(h)     # cross-track
    along = [(x * ux + y * uy, x * vx + y * vy) for x, y in pts]
    vmin, vmax = min(p[1] for p in along), max(p[1] for p in along)
    n_lines = int((vmax - vmin) // spacing_m) + 1
    if n_lines > MAX_SURVEY_LINES:
        raise SafetyError(f"{n_lines} survey lines; raise spacing_m")
    out = []
    flip = False
    for k in range(n_lines):
        v = vmin + spacing_m * (k + 0.5) if n_lines > 1 else (vmin + vmax) / 2
        if v > vmax:
            break
        xs = []
        n = len(along)
        for i in range(n):
            (a1, b1), (a2, b2) = along[i], along[(i + 1) % n]
            if (b1 > v) != (b2 > v):
                xs.append(a1 + (v - b1) * (a2 - a1) / (b2 - b1))
        xs.sort()
        segs = [(xs[i] + inset, xs[i + 1] - inset) for i in range(0, len(xs) - 1, 2)
                if xs[i + 1] - xs[i] > 2 * inset]
        for s0, s1 in (reversed(segs) if flip else segs):
            s0, s1 = _trim_to_fence(fence, s0, s1, v, (ux, uy), (vx, vy))
            if s1 - s0 <= 0:
                continue
            ends = (s1, s0) if flip else (s0, s1)
            for a in ends:
                x, y = a * ux + v * vx, a * uy + v * vy
                lat, lon = fence.to_latlon(x, y)
                out.append({"lat": round(lat, 7), "lon": round(lon, 7), "rel_alt_m": rel_alt_m})
        flip = not flip
    if not out:
        raise SafetyError("survey produced no passes; area too small for spacing/inset")
    return out


TRIM_STEP_M = 1.0


def _trim_to_fence(fence, s0, s1, v, u_axis, v_axis):
    """Pull pass ends inward until they clear the fence margin. The along-track inset alone
    is not enough where a fence edge meets the pass at a shallow angle."""
    def inside(a):
        p = (a * u_axis[0] + v * v_axis[0], a * u_axis[1] + v * v_axis[1])
        clearance = min(point_segment_distance(p, e1, e2) for e1, e2 in fence.edges())
        # half a step of slack so rounding the output to 1e-7 deg cannot push a point out
        return point_in_polygon(p, fence.xy) and clearance >= fence.margin_m + TRIM_STEP_M / 2
    while s0 < s1 and not inside(s0):
        s0 += TRIM_STEP_M
    while s1 > s0 and not inside(s1):
        s1 -= TRIM_STEP_M
    return s0, s1
