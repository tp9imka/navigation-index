"""Synthetic scenarios: static / moving / two jammers, static + vehicle nodes, optional
buildings, optional KrakenSDR-style DF stations. All numbers are scenario choices."""
import math
import random
from dataclasses import dataclass, field

import siblings  # noqa: F401
import jsn_model as M
from kraken import Bearing  # noqa: E402  (../interference-geolocation-to-tak)

ORIGIN = (69.28, 16.03)          # arbitrary area centre
HALF_M = 2000.0
DF_SIGMA_DEG = 3.0
DF_OUTLIER_P = 0.1
DF_MIN_DBM = -120.0              # assumed DF detection floor at the station
DF_STATIONS = {"KR-A": (-1800.0, -1700.0), "KR-B": (1800.0, -1600.0), "KR-C": (0.0, 1900.0)}
VEHICLE_SPEED_MPS = 10.0
ROAD_LOOPS = [
    [(-1500, -1200), (1500, -1200), (1500, 1300), (-1500, 1300)],
    [(-300, -1800), (-300, 1800), (600, 1800), (600, -1800)],
]


@dataclass
class Scenario:
    name: str
    env: M.Environment
    jammers: list
    nodes: list
    duration_s: float
    jammer_speed_mps: float
    df: dict = field(default_factory=dict)
    note: str = ""


def node_layout(n_static, half, rng, jitter=0.25):
    """Jittered grid of n_static positions over the square [-half, half]^2."""
    k = math.ceil(math.sqrt(n_static))
    cells = [(i, j) for i in range(k) for j in range(k)]
    rng.shuffle(cells)
    step = 2 * half / k
    return [(-half + (i + 0.5 + rng.uniform(-jitter, jitter)) * step,
             -half + (j + 0.5 + rng.uniform(-jitter, jitter)) * step) for i, j in cells[:n_static]]


def make_nodes(n_static, n_mobile, half, rng):
    nodes = [M.SimNode(f"s{i:02d}", M.static_path(p), True, rng)
             for i, p in enumerate(node_layout(n_static, half, rng))]
    for i in range(n_mobile):
        loop = ROAD_LOOPS[i % len(ROAD_LOOPS)]
        nodes.append(M.SimNode(f"v{i:02d}", M.polyline_path(loop, VEHICLE_SPEED_MPS, t_start=-rng.uniform(0, 600)),
                               False, rng))
    return nodes


def build(name, seed=1, n_static=12, n_mobile=2, sigma_db=6.0, buildings=False, df=True):
    rng = random.Random(seed)
    blds = [(250, -500, 330, -380), (520, -260, 640, -180), (300, -150, 380, -60)] if buildings else []
    env = M.Environment(sigma_db=sigma_db, buildings=blds, rng=rng)
    v_assumed = 0.0
    if name == "static":
        jams = [M.Jammer(M.static_path((430.0, -310.0)), 10.0, t_on=20.0)]
        dur = 180.0
    elif name == "moving":
        jams = [M.Jammer(M.linear_path((-1400.0, -700.0), (1300.0, 900.0), 20.0, 280.0), 13.0, t_on=20.0)]
        dur, v_assumed = 280.0, 15.0
    elif name == "two":
        jams = [M.Jammer(M.static_path((-900.0, 600.0)), 12.0, t_on=20.0, name="J1"),
                M.Jammer(M.static_path((800.0, -500.0)), 12.0, t_on=20.0, name="J2")]
        dur = 180.0
        df = False
    else:
        raise ValueError(name)
    nodes = make_nodes(n_static, n_mobile, HALF_M, rng)
    return Scenario(name, env, jams, nodes, dur, v_assumed, DF_STATIONS if df else {},
                    "buildings on" if buildings else "")


def df_bearings(sc, t, frame, rng):
    """KrakenSDR-style bearings (true north) from each DF station to the strongest active jammer."""
    out = []
    for sid, xy in sc.df.items():
        best = None
        for j in sc.jammers:
            if not j.active(t):
                continue
            p = sc.env.received_dbm(xy, j.path(t), j.eirp_dbm)
            if p > DF_MIN_DBM and (best is None or p > best[0]):
                best = (p, j.path(t))
        if best is None:
            continue
        jx, jy = best[1]
        b = math.degrees(math.atan2(jx - xy[0], jy - xy[1]))
        b += rng.uniform(25, 160) * rng.choice((-1, 1)) if rng.random() < DF_OUTLIER_P else rng.gauss(0, DF_SIGMA_DEG)
        lat, lon, _ = frame.to_geodetic(*xy)
        out.append(Bearing(t=t, station_id=sid, lat=lat, lon=lon, bearing_deg=b % 360.0, power_db=best[0]))
    return out
