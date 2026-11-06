"""Stdlib pieces of the fixed-wing demo: route geometry, the measured fix models, the coherent
spoof, and the velocity calibration the companion runs while GNSS is trusted."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent
FIX_MODELS_JSON = HERE / "data" / "fix_models.json"

# Route as (north, east) metres from home, flown at 300 m above home. Two turns before the
# spoof onset give the velocity calibration two headings; then 8 km north, 5 km east, 7.6 km SSE.
ROUTE_NE = [(1500.0, 0.0), (3000.0, 2000.0), (3000.0, 5000.0), (11000.0, 5000.0),
            (11000.0, 10000.0), (4000.0, 13000.0)]
CRUISE_ALT_M = 300.0
TAKEOFF_ALT_M = 60.0
CAL_ORBIT_RADIUS_M = 400.0

SPOOF_MAX_M = 5000.0


# --- geometry ---------------------------------------------------------------------------------
def route_points_en(route_ne=ROUTE_NE):
    """Home plus the route, as (east, north)."""
    return [(0.0, 0.0)] + [(e, n) for n, e in route_ne]


def route_length_m(route_ne=ROUTE_NE) -> float:
    pts = route_points_en(route_ne)
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def cross_track(p_en, pts) -> tuple[float, float, int]:
    """Distance from p to the nearest route segment, along-route distance of the foot point,
    segment index."""
    best = (math.inf, 0.0, 0)
    run = 0.0
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        ax, ay = a
        dx, dy = b[0] - ax, b[1] - ay
        seg = math.hypot(dx, dy)
        u = 0.0 if seg == 0 else max(0.0, min(1.0, ((p_en[0] - ax) * dx + (p_en[1] - ay) * dy) / seg ** 2))
        d = math.hypot(p_en[0] - (ax + u * dx), p_en[1] - (ay + u * dy))
        if d < best[0]:
            best = (d, run + u * seg, i)
        run += seg
    return best


# --- ArduPilot's local frame -----------------------------------------------------------------
# AP_Common/Location.cpp (4.6.3): north = dlat * LATLON_TO_M, east = dlng * LATLON_TO_M *
# cos(mid latitude), a sphere of radius 6378137 m. ExternalNav NED must use this, not a WGS84
# local-radius ENU: at 35 deg S the meridian radius is 0.31 % shorter, i.e. 34 m at 11 km north
# (measured as EKF error on ExternalNav before this conversion was used).
LATLON_TO_M = 0.011131884502145034          # m per 1e-7 deg


def ap_ne_from_ll(lat, lon, lat0, lon0):
    north = (lat - lat0) * 1e7 * LATLON_TO_M
    east = (lon - lon0) * 1e7 * LATLON_TO_M * math.cos(math.radians((lat + lat0) / 2))
    return north, east


# --- coherent spoof -----------------------------------------------------------------------------
class Spoof:
    """Position offset growing at rate_mps toward bearing_deg from onset; a coherent spoof also
    adds the drag rate to the reported velocity."""

    def __init__(self, kind: str, onset_s: float, rate_mps: float, bearing_deg: float, max_m=SPOOF_MAX_M):
        self.kind, self.onset, self.rate, self.max_m = kind, onset_s, rate_mps, max_m
        b = math.radians(bearing_deg)
        self.u = (math.sin(b), math.cos(b))

    def offset_m(self, t) -> float:
        if self.kind == "none" or t is None or t < self.onset:
            return 0.0
        return min(self.rate * (t - self.onset), self.max_m)

    def offset_en(self, t):
        d = self.offset_m(t)
        return d * self.u[0], d * self.u[1]

    def vel_en(self, t):
        d = self.offset_m(t)
        if self.kind != "coherent" or d <= 0.0 or d >= self.max_m:
            return 0.0, 0.0
        return self.rate * self.u[0], self.rate * self.u[1]


# --- measured fix models --------------------------------------------------------------------------
RAYLEIGH_MEDIAN_K = math.sqrt(2 * math.log(2))      # radial median of a 2D Gaussian = 1.1774 sigma


def derive_fix_models(samples=SAMPLES) -> dict:
    """Day: samples/e2e-visual-nav-vpair (VPAIR, 300-400 m AGL aerial, strict gate, map stride 1).
    Night: samples/thermal-geolocalization (Thermal-UAV, ALIKED + gradient preproc, revised gate).
    Only fields that file states are used; see README for what is assumed on top."""
    e2e = json.loads((samples / "e2e-visual-nav-vpair" / "results" / "e2e_result.json").read_text())
    fe = next(r["fix_frontend"] for r in e2e["runs"]
              if r.get("config") == "single_fix" and r.get("match_gate") == "strict"
              and r.get("map_stride") == 1 and r.get("fix_period") == 1 and r.get("yaw_bias_deg") == 0.0)
    path_m = e2e["path_after_calibration_m"]
    day = {"source": "samples/e2e-visual-nav-vpair/results/e2e_result.json (single_fix, strict, stride 1)",
           "attempts": fe["attempts"], "fixes": fe["produced"], "availability": fe["produced"] / fe["attempts"],
           "err_median_m": fe["err_median_m"], "err_p95_m": fe["err_p95_m"], "err_max_m": fe["err_max_m"],
           "false_fixes": fe["false"],
           "sigma_axis_m": round(fe["err_median_m"] / RAYLEIGH_MEDIAN_K, 3),
           "attempt_spacing_m": round(path_m / fe["attempts"], 1)}

    out = samples / "thermal-geolocalization" / "out"
    rows = [json.loads(line) for line in (out / "main_revised.jsonl").read_text().splitlines() if line.strip()]
    summary = (out / "main_revised_summary.md").read_text()
    off_map = {f.strip().lstrip("_") for f in summary.split("Frames outside the map:")[1].split("(")[1].split(")")[0].split(",")}
    rows = [r for r in rows if r["features"] == "aliked" and r["preproc"] == "grad"]
    on_map = [r for r in rows if not any(r["frame"].endswith(f) for f in off_map)]
    acc = sorted(r["err_m"] for r in on_map if r["accepted"])
    night_rows = [r for r in on_map if "night" in r["condition"]]
    night = {"source": "samples/thermal-geolocalization/out/main_revised.jsonl (aliked/grad, all conditions, on-map frames)",
             "attempts": len(on_map), "fixes": len(acc), "availability": len(acc) / len(on_map),
             "night_only_attempts": len(night_rows), "night_only_fixes": sum(r["accepted"] for r in night_rows),
             "false_fixes": sum(1 for e in acc if e > 20.0),
             "err_pool_m": [round(e, 3) for e in acc],
             "err_median_m": round(acc[len(acc) // 2 - 1] / 2 + acc[len(acc) // 2] / 2, 2) if len(acc) % 2 == 0 else acc[len(acc) // 2]}
    return {"day": day, "night": night}


def load_fix_models(path=FIX_MODELS_JSON) -> dict:
    return json.loads(Path(path).read_text())


class FixModel:
    """Bernoulli availability per attempt, error either Rayleigh (sigma per axis) or drawn from
    a measured pool of radial errors; direction uniform. No outliers: both sources report 0
    false fixes after their gates."""

    def __init__(self, availability: float, sigma_axis_m=None, err_pool_m=None, rng=None):
        self.p = availability
        self.sigma = sigma_axis_m
        self.pool = list(err_pool_m or [])
        self.rng = rng or random.Random(0)

    @classmethod
    def from_models(cls, models: dict, name: str, rng):
        m = models[name]
        if name == "day":
            return cls(m["availability"], sigma_axis_m=m["sigma_axis_m"], rng=rng)
        return cls(m["availability"], err_pool_m=m["err_pool_m"], rng=rng)

    def attempt(self, truth_en):
        if self.rng.random() >= self.p:
            return None
        if self.pool:
            r = self.rng.choice(self.pool)
            a = self.rng.uniform(0, 2 * math.pi)
            return truth_en[0] + r * math.sin(a), truth_en[1] + r * math.cos(a)
        return truth_en[0] + self.rng.gauss(0, self.sigma), truth_en[1] + self.rng.gauss(0, self.sigma)


# --- velocity calibration while GNSS is trusted ---------------------------------------------------
class VelocityCalibration:
    """Kalman filter on constant-ish parameters of v_gnss - v_raw = s*v_raw + d*J(v_raw) + b,
    J(v) = (v_n, -v_e): s = scale error, d = heading error (rad), b = earth-frame bias (wind for
    an airspeed reference). VO uses [s, d] only; airspeed uses all four. Random-walk process
    noise rather than exponential forgetting: forgetting winds up the unobservable direction on
    a straight leg (heading error and crosswind are collinear there) and a 10 deg "heading
    error" came out of one SITL probe. Frozen once GNSS is excluded."""

    PRIOR = (0.05, 0.05, 10.0, 10.0)            # scale, heading rad, bias m/s
    Q_PER_S = (1e-4, 2e-4, 0.02, 0.02)          # random-walk sigma per sqrt(s)

    def __init__(self, with_bias: bool, r_mps=0.5):
        self.k = 4 if with_bias else 2
        self.theta = [0.0] * self.k
        self.P = [[(self.PRIOR[i] ** 2 if i == j else 0.0) for j in range(self.k)] for i in range(self.k)]
        self.r = r_mps ** 2
        self.frozen = False
        self.n = 0

    def _rows(self, v):
        ve, vn = v
        rows = [[ve, vn, 1.0, 0.0], [vn, -ve, 0.0, 1.0]]
        return [row[:self.k] for row in rows]

    def correct(self, v_raw):
        rows = self._rows(v_raw)
        return tuple(v_raw[i] + sum(h * t for h, t in zip(rows[i], self.theta)) for i in range(2))

    def update(self, v_raw, v_gnss, dt):
        if self.frozen or v_gnss is None:
            return
        for i in range(self.k):
            self.P[i][i] += self.Q_PER_S[i] ** 2 * dt
        for i, h in enumerate(self._rows(v_raw)):
            y = v_gnss[i] - v_raw[i] - sum(a * b for a, b in zip(h, self.theta))
            ph = [sum(self.P[r][c] * h[c] for c in range(self.k)) for r in range(self.k)]
            s = sum(h[r] * ph[r] for r in range(self.k)) + self.r
            gain = [x / s for x in ph]
            self.theta = [t + g * y for t, g in zip(self.theta, gain)]
            self.P = [[self.P[r][c] - gain[r] * ph[c] for c in range(self.k)] for r in range(self.k)]
        self.n += 1


def rotate_scale(v_en, heading_err_deg: float, scale_err: float):
    """Velocity seen by a sensor whose heading reads heading_err_deg too high (clockwise) and
    whose speed scale is off by scale_err."""
    a = math.radians(heading_err_deg)
    ve, vn = v_en
    k = 1.0 + scale_err
    return k * (ve * math.cos(a) + vn * math.sin(a)), k * (-ve * math.sin(a) + vn * math.cos(a))
