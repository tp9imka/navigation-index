"""Truth trajectory and sensors: compass + bottom-track speed log (DVL-like), GNSS with spoof/jam,
marine radar returns from the coastline, structures, aids to navigation and real AIS ships."""
import csv
import gzip
import math
import random
from dataclasses import dataclass
from pathlib import Path

from geo import bearing, closest_on_segment, ray_segment, wrap_pi

FIX = Path(__file__).resolve().parent / "fixtures"

# Route in local metres (frame origin 55.62N 12.70E): open water by Lillgrund wind farm => Drogden
# channel between Amager and Saltholm => past Kastrup => Kongedybet west of Middelgrunden, ending
# off Refshaleoen at the Copenhagen harbour approach.
ROUTE_XY = [(2000.0, -10000.0), (300.0, -7000.0), (300.0, -1000.0), (-800.0, 3000.0),
            (-3100.0, 6400.0), (-3500.0, 8300.0)]
SPEED_MS = 5.0
MAX_TURN_RATE = math.radians(3.0)
LOOKAHEAD_M = 150.0
DT = 1.0


@dataclass
class TruthState:
    t: float
    x: float
    y: float
    psi: float   # heading, rad clockwise from north
    v: float


def truth_trajectory(route=ROUTE_XY, speed=SPEED_MS, dt=DT):
    """Pure-pursuit along the route with a turn-rate limit; ends at the last waypoint."""
    x, y = route[0]
    psi = bearing(route[1][0] - x, route[1][1] - y)
    out, t, leg = [], 0.0, 1
    while True:
        out.append(TruthState(t, x, y, psi, speed))
        ax, ay = route[leg - 1]
        bx, by = route[leg]
        _, cx, cy = closest_on_segment(x, y, ax, ay, bx, by)
        if math.hypot(bx - cx, by - cy) < LOOKAHEAD_M:
            if leg == len(route) - 1:
                if math.hypot(bx - x, by - y) < speed * dt:
                    return out
                tx, ty = bx, by
            else:
                leg += 1
                continue
        else:
            L = math.hypot(bx - ax, by - ay)
            ux, uy = (bx - ax) / L, (by - ay) / L
            tx, ty = cx + ux * LOOKAHEAD_M, cy + uy * LOOKAHEAD_M
        dpsi = wrap_pi(bearing(tx - x, ty - y) - psi)
        psi = (psi + max(-MAX_TURN_RATE * dt, min(MAX_TURN_RATE * dt, dpsi))) % (2 * math.pi)
        x += speed * math.sin(psi) * dt
        y += speed * math.cos(psi) * dt
        t += dt


@dataclass
class DrSensors:
    """Magnetic/AHRS compass and a bottom-tracking speed log. Values are illustrative for a small
    USV with a MEMS AHRS, not taken from a datasheet."""
    compass_bias_deg: float = 1.5
    compass_bias_rw_deg_per_sqrt_s: float = 0.003
    compass_noise_deg: float = 0.5
    speed_scale_err: float = 0.007
    speed_noise_ms: float = 0.05

    def generate(self, truth, rng):
        b = math.radians(self.compass_bias_deg) * rng.choice((-1, 1))
        out = []
        for s in truth:
            b += rng.gauss(0, math.radians(self.compass_bias_rw_deg_per_sqrt_s))
            psi_m = (s.psi + b + rng.gauss(0, math.radians(self.compass_noise_deg))) % (2 * math.pi)
            v_m = s.v * (1 + self.speed_scale_err) + rng.gauss(0, self.speed_noise_ms)
            out.append((psi_m, v_m, b))
        return out


@dataclass
class Attack:
    kind: str = "none"            # none | spoof | jam
    t_start: float = 1e9
    t_end: float = 1e9
    drag_accel: float = 0.003     # m/s^2 until drag_rate is reached
    drag_rate: float = 0.6        # m/s
    drag_dir_deg: float = 270.0   # direction the reported position is pulled (west = towards Amager)

    def offset(self, t):
        if self.kind != "spoof" or not (self.t_start <= t < self.t_end):
            return 0.0, 0.0
        tau = t - self.t_start
        t_ramp = self.drag_rate / self.drag_accel
        d = 0.5 * self.drag_accel * tau * tau if tau < t_ramp else \
            0.5 * self.drag_accel * t_ramp ** 2 + self.drag_rate * (tau - t_ramp)
        a = math.radians(self.drag_dir_deg)
        return d * math.sin(a), d * math.cos(a)

    def denied(self, t):
        return self.kind == "jam" and self.t_start <= t < self.t_end


@dataclass
class Gnss:
    sigma_white: float = 1.5
    sigma_gm: float = 2.0
    tau_gm: float = 120.0

    def generate(self, truth, attack, rng):
        """List of (x, y) or None per truth epoch. Spoofed fixes carry the drag offset."""
        a = math.exp(-DT / self.tau_gm)
        q = self.sigma_gm * math.sqrt(1 - a * a)
        ex = ey = 0.0
        out = []
        for s in truth:
            ex, ey = a * ex + rng.gauss(0, q), a * ey + rng.gauss(0, q)
            if attack.denied(s.t):
                out.append(None)
                continue
            ox, oy = attack.offset(s.t)
            out.append((s.x + ex + ox + rng.gauss(0, self.sigma_white),
                        s.y + ey + oy + rng.gauss(0, self.sigma_white)))
        return out


class AisTraffic:
    """Real DMA AIS positions, linearly interpolated, as radar targets (circles of ~half length)."""
    DEFAULT_LEN_M = 20.0
    MAX_GAP_S = 300

    def __init__(self, frame, path=FIX / "oresund_ais_window.csv.gz"):
        self.tracks = {}
        self.length = {}
        with gzip.open(path, "rt") as f:
            rows = [r for r in csv.DictReader(line for line in f if not line.startswith("#"))]
        for r in rows:
            x, y = frame.to_xy(float(r["lat"]), float(r["lon"]))
            self.tracks.setdefault(r["mmsi"], []).append((int(r["t_rel_s"]), x, y))
            try:
                self.length[r["mmsi"]] = float(r["length_m"])
            except ValueError:
                pass

    def at(self, t):
        out = []
        for mmsi, tr in self.tracks.items():
            if not (tr[0][0] - self.MAX_GAP_S <= t <= tr[-1][0] + self.MAX_GAP_S):
                continue
            prev = tr[0]
            pos = None
            for p in tr:
                if p[0] >= t:
                    if p[0] - prev[0] > self.MAX_GAP_S:
                        pos = None
                    elif p[0] == prev[0]:
                        pos = p[1:]
                    else:
                        w = (t - prev[0]) / (p[0] - prev[0])
                        pos = (prev[1] + w * (p[1] - prev[1]), prev[2] + w * (p[2] - prev[2]))
                    break
                prev = p
            else:
                pos = tr[-1][1:]
            if pos is not None:
                out.append((mmsi, pos[0], pos[1], 0.5 * max(self.length.get(mmsi, self.DEFAULT_LEN_M), 5.0)))
        return out


@dataclass
class Radar:
    """First-return per azimuth from a 2D world, plus sea clutter. No elevation, no multipath,
    no shadowing by terrain height: a low island and a cliff reflect the same way here."""
    n_beams: int = 720
    max_range: float = 6000.0
    sigma_range: float = 7.5
    sigma_bearing_deg: float = 0.4
    pd_near: float = 0.9
    pd_far: float = 0.4
    clutter_mean: float = 12.0
    clutter_range: float = 800.0
    min_range: float = 30.0
    min_incidence_factor: float = 0.25
    self_exclusion_m: float = 40.0

    def scan(self, world, ships, x, y, psi, rng):
        """Returns list of (range m, bearing relative to bow rad, source kind)."""
        n = self.n_beams
        step = 2 * math.pi / n
        best = [math.inf] * n
        kind = [None] * n
        inc = [1.0] * n
        R = self.max_range
        for i in world.near(x, y, R):
            ax, ay, bx, by, k, _ = world.segs[i]
            d2, _, _ = closest_on_segment(x, y, ax, ay, bx, by)
            if d2 > R * R:
                continue
            ba, bb = bearing(ax - x, ay - y), bearing(bx - x, by - y)
            span = wrap_pi(bb - ba)
            lo = ba if span >= 0 else bb
            n_cov = int(abs(span) / step) + 2
            j0 = math.ceil(lo / step) - 1
            sx, sy = bx - ax, by - ay
            sl = math.hypot(sx, sy) or 1.0
            for jj in range(j0, j0 + n_cov + 1):
                j = jj % n
                th = j * step
                ux, uy = math.sin(th), math.cos(th)
                tt = ray_segment(x, y, ux, uy, ax, ay, bx, by)
                if tt is not None and tt < best[j]:
                    best[j] = tt
                    kind[j] = k
                    inc[j] = abs(ux * sy - uy * sx) / sl
        for _, sx_, sy_, rad in ships:
            d = math.hypot(sx_ - x, sy_ - y)
            if d < self.self_exclusion_m or d - rad > R:
                continue
            c = bearing(sx_ - x, sy_ - y)
            half = math.asin(min(1.0, rad / d))
            for jj in range(math.ceil((c - half) / step), math.floor((c + half) / step) + 1):
                j = jj % n
                if d - rad < best[j]:
                    best[j] = d - rad
                    kind[j] = "ship"
                    inc[j] = 1.0
        out = []
        for j in range(n):
            r = best[j]
            if r > R or r < self.min_range:
                continue
            pd = self.pd_near + (self.pd_far - self.pd_near) * r / R
            if kind[j] in ("coast", "structure"):
                pd *= max(self.min_incidence_factor, inc[j])
            if rng.random() > pd:
                continue
            out.append((r + rng.gauss(0, self.sigma_range),
                        wrap_pi(j * step - psi + rng.gauss(0, math.radians(self.sigma_bearing_deg))),
                        kind[j]))
        n_clutter = poisson(self.clutter_mean, rng)
        for _ in range(n_clutter):
            out.append((self.min_range + rng.expovariate(3.0 / self.clutter_range),
                        rng.uniform(-math.pi, math.pi), "clutter"))
        return out


def poisson(lam, rng):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p < L:
            return k
        k += 1


def make_rng(seed, stream):
    return random.Random(f"{seed}:{stream}")
