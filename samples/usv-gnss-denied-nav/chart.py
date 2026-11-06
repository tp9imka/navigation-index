"""Vector chart in local metres: segments, a uniform-grid index, nearest-segment and range queries."""
import gzip
import json
import math
import random
from pathlib import Path

from geo import LocalFrame, closest_on_segment

CELL_M = 500.0       # coarse grid for range queries (radar)
FINE_CELL_M = 50.0   # fine grid for nearest-segment queries (matching)
FIELD_RES_M = 5.0
FIELD_CAP_M = 60.0
POINT_RADIUS_M = {"wind_turbine": 3.0, "buoy": 1.5, "beacon": 1.0, "light": 1.0}
POINT_SIDES = 8
DEFAULT_CHART = Path(__file__).resolve().parent / "fixtures" / "oresund_chart.json.gz"
ORIGIN = (55.62, 12.70)  # local frame origin, between Dragor and Saltholm

COAST, STRUCTURE, POINT = "coast", "structure", "point"


def point_family(kind):
    for k in POINT_RADIUS_M:
        if kind.startswith(k):
            return k
    return "light"


class Chart:
    def __init__(self, segments):
        """segments: list of (ax, ay, bx, by, kind, obj_id)."""
        self.segs = segments
        self.grid, self.fine = {}, {}
        for i, (ax, ay, bx, by, *_rest) in enumerate(segments):
            box = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
            for c in self._cells_for_box(*box, CELL_M):
                self.grid.setdefault(c, []).append(i)
            for c in self._cells_for_box(*box, FINE_CELL_M):
                self.fine.setdefault(c, []).append(i)
        self._field = {}

    @staticmethod
    def _cells_for_box(x0, y0, x1, y1, cell):
        for i in range(math.floor(x0 / cell), math.floor(x1 / cell) + 1):
            for j in range(math.floor(y0 / cell), math.floor(y1 / cell) + 1):
                yield i, j

    def near(self, x, y, radius):
        grid, cell = (self.fine, FINE_CELL_M) if radius <= 2 * FINE_CELL_M else (self.grid, CELL_M)
        out = set()
        for c in self._cells_for_box(x - radius, y - radius, x + radius, y + radius, cell):
            out.update(grid.get(c, ()))
        return out

    def nearest(self, x, y, max_d):
        """(distance, closest x, closest y, segment index) or None within max_d."""
        best = None
        for i in self.near(x, y, max_d):
            ax, ay, bx, by = self.segs[i][:4]
            d2, cx, cy = closest_on_segment(x, y, ax, ay, bx, by)
            if best is None or d2 < best[0]:
                best = (d2, cx, cy, i)
        if best is None or best[0] > max_d * max_d:
            return None
        return math.sqrt(best[0]), best[1], best[2], best[3]

    def field(self, x, y):
        """Distance to the chart, capped, cached on a FIELD_RES_M lattice (a lazy likelihood field)."""
        return self.field_key(round(x / FIELD_RES_M), round(y / FIELD_RES_M))

    def field_key(self, i, j):
        d = self._field.get((i, j))
        if d is None:
            hit = self.nearest(i * FIELD_RES_M, j * FIELD_RES_M, FIELD_CAP_M)
            d = FIELD_CAP_M if hit is None else hit[0]
            self._field[(i, j)] = d
        return d


def polygon_segments(cx, cy, radius, kind, obj_id):
    pts = [(cx + radius * math.cos(2 * math.pi * k / POINT_SIDES),
            cy + radius * math.sin(2 * math.pi * k / POINT_SIDES)) for k in range(POINT_SIDES + 1)]
    return [(a[0], a[1], b[0], b[1], kind, obj_id) for a, b in zip(pts, pts[1:])]


def load_chart_data(path=DEFAULT_CHART):
    with gzip.open(path, "rt") as f:
        return json.load(f)


def build(data, frame, buoy_watch_circle_m=0.0, rng=None):
    """Chart from OSM data. buoy_watch_circle_m > 0 moves each floating aid off its charted
    position (uniform in a disc), which is how the radar 'truth world' differs from the chart."""
    segs = []
    for k, line in enumerate(data["coast"]):
        xy = [frame.to_xy(lat, lon) for lon, lat in line]
        segs += [(a[0], a[1], b[0], b[1], COAST, f"coast{k}") for a, b in zip(xy, xy[1:]) if a != b]
    for k, st in enumerate(data["structures"]):
        xy = [frame.to_xy(lat, lon) for lon, lat in st["line"]]
        segs += [(a[0], a[1], b[0], b[1], STRUCTURE, f"struct{k}") for a, b in zip(xy, xy[1:]) if a != b]
    for k, p in enumerate(data["points"]):
        x, y = frame.to_xy(p["lat"], p["lon"])
        fam = point_family(p["kind"])
        if buoy_watch_circle_m and fam == "buoy":
            r = buoy_watch_circle_m * math.sqrt(rng.random())
            a = rng.uniform(0, 2 * math.pi)
            x, y = x + r * math.cos(a), y + r * math.sin(a)
        segs += polygon_segments(x, y, POINT_RADIUS_M[fam], POINT, f"{fam}{k}")
    return Chart(segs)


def default_frame():
    return LocalFrame(*ORIGIN)


def chart_and_world(seed=0, watch_circle_m=15.0, path=DEFAULT_CHART):
    data = load_chart_data(path)
    frame = default_frame()
    return frame, build(data, frame), build(data, frame, watch_circle_m, random.Random(seed))
