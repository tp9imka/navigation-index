"""Stdlib geometry and small dense linear algebra used by every other module."""
import math

WGS84_A = 6378137.0
WGS84_E2 = 6.69437999014e-3
CHI2_2DOF_999 = 13.816
CHI2_3DOF_999 = 16.266


class LocalFrame:
    """Local east/north metres around (lat0, lon0). x = east, y = north.

    East uses cos(lat) of the point itself, so the map is exactly invertible and the
    distortion over a 30 km area is far below the sensor errors simulated here.
    """

    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        s = math.sin(math.radians(lat0))
        w = math.sqrt(1 - WGS84_E2 * s * s)
        self.m = WGS84_A * (1 - WGS84_E2) / w ** 3   # meridian radius
        self.n = WGS84_A / w                         # prime vertical radius

    def to_xy(self, lat, lon):
        return (math.radians(lon - self.lon0) * self.n * math.cos(math.radians(lat)),
                math.radians(lat - self.lat0) * self.m)

    def to_ll(self, x, y):
        lat = self.lat0 + math.degrees(y / self.m)
        return lat, self.lon0 + math.degrees(x / (self.n * math.cos(math.radians(lat))))


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def bearing(dx, dy):
    """Clockwise from north, radians in [0, 2pi)."""
    return math.atan2(dx, dy) % (2 * math.pi)


def closest_on_segment(px, py, ax, ay, bx, by):
    """Returns (squared distance, closest x, closest y)."""
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    cx, cy = ax + t * vx, ay + t * vy
    return (px - cx) ** 2 + (py - cy) ** 2, cx, cy


def ray_segment(ox, oy, ux, uy, ax, ay, bx, by):
    """Distance along unit ray (ox,oy)+t(ux,uy) to segment AB, or None."""
    ex, ey = bx - ax, by - ay
    den = ux * ey - uy * ex
    if abs(den) < 1e-12:
        return None
    wx, wy = ax - ox, ay - oy
    t = (wx * ey - wy * ex) / den
    s = (wx * uy - wy * ux) / den
    if t >= 0 and 0 <= s <= 1:
        return t
    return None


# --- dense matrices as lists of rows -------------------------------------------------

def zeros(n, m=None):
    return [[0.0] * (n if m is None else m) for _ in range(n)]


def eye(n, d=1.0):
    return [[d if i == j else 0.0 for j in range(n)] for i in range(n)]


def mm(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


def mv(A, v):
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def tr(A):
    return [list(r) for r in zip(*A)]


def madd(A, B, k=1.0):
    return [[a + k * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def inv(A):
    n = len(A)
    M = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-300:
            raise ZeroDivisionError("singular matrix")
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0.0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def sym(A):
    return [[0.5 * (A[i][j] + A[j][i]) for j in range(len(A))] for i in range(len(A))]


def eig2(a, b, d):
    """Eigenvalues (lo, hi) and unit eigenvector of hi for symmetric [[a, b], [b, d]]."""
    m, q = 0.5 * (a + d), math.hypot(0.5 * (a - d), b)
    lo, hi = m - q, m + q
    if abs(b) > 1e-12:
        vx, vy = hi - d, b
    else:
        vx, vy = (1.0, 0.0) if a >= d else (0.0, 1.0)
    n = math.hypot(vx, vy)
    return lo, hi, (vx / n, vy / n)


def quad(v, A):
    return sum(v[i] * A[i][j] * v[j] for i in range(len(v)) for j in range(len(v)))
