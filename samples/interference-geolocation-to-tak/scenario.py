"""Synthetic KrakenSDR bearings on a GNSS jammer: 2 fixed sites + 1 moving vehicle.

Output is a list of dicts in the krakensdr_doa "Kraken Pro Local" JSON shape, so the
rest of the pipeline reads synthetic and real data through the same adapter.
"""
import json
import math
import random
import sys
from datetime import datetime, timezone

from geo import LocalFrame, compass_bearing
from kraken import to_kraken_json

JAMMER_LAT, JAMMER_LON = 52.0800, 5.1200
GPS_L1_HZ = 1575.42e6
START = datetime(2026, 11, 6, 10, 0, 0, tzinfo=timezone.utc)
DURATION_S = 300
RATE_HZ = 1.0
FIXED_SIGMA_DEG = 3.0
MOVING_SIGMA_DEG = 5.0       # extra heading error on a vehicle
OUTLIER_P = 0.12
OUTLIER_MIN_DEG, OUTLIER_MAX_DEG = 25.0, 160.0
VEHICLE_SPEED_MPS = 12.0
VEHICLE_TURN_S = 150

FIXED_SITES = [  # id, east m, north m (relative to the jammer), array heading deg
    ("KR-A", -4000.0, -3000.0, 30.0),
    ("KR-B", 5000.0, -2500.0, 300.0),
]
VEHICLE_ID, VEHICLE_START = "KR-C-mobile", (-6000.0, 4000.0)


def vehicle_pose(t):
    """East for VEHICLE_TURN_S, then south-east. Returns (e, n, course_deg)."""
    e0, n0 = VEHICLE_START
    leg1 = min(t, VEHICLE_TURN_S)
    e, n, course = e0 + VEHICLE_SPEED_MPS * leg1, n0, 90.0
    if t > VEHICLE_TURN_S:
        d = VEHICLE_SPEED_MPS * (t - VEHICLE_TURN_S)
        course = 135.0
        e += d * math.sin(math.radians(course))
        n += d * math.cos(math.radians(course))
    return e, n, course


def generate(seed=7, outlier_p=OUTLIER_P):
    rng = random.Random(seed)
    frame = LocalFrame(JAMMER_LAT, JAMMER_LON)
    records, n_out = [], 0
    t0_ms = START.timestamp() * 1000
    for k in range(int(DURATION_S * RATE_HZ)):
        t = k / RATE_HZ
        poses = [(sid, e, n, hdg, FIXED_SIGMA_DEG) for sid, e, n, hdg in FIXED_SITES]
        poses.append((VEHICLE_ID, *vehicle_pose(t), MOVING_SIGMA_DEG))
        for sid, e, n, heading, sigma in poses:
            lat, lon, _ = frame.to_geodetic(e, n)
            true_b = compass_bearing((0.0, 0.0), LocalFrame(lat, lon).to_enu(JAMMER_LAT, JAMMER_LON)[:2])
            meas = true_b + rng.gauss(0.0, sigma)
            if rng.random() < outlier_p:
                meas += rng.choice((-1, 1)) * rng.uniform(OUTLIER_MIN_DEG, OUTLIER_MAX_DEG)
                n_out += 1
            theta = (heading - meas) % 360.0  # invert true = heading + 360 - theta
            records.append(to_kraken_json(
                t0_ms + t * 1000, sid, round(lat, 7), round(lon, 7), heading,
                round(theta, 2), conf=rng.uniform(0.5, 0.95), power_db=rng.uniform(-60, -30),
                freq_hz=GPS_L1_HZ))
    return records, n_out


if __name__ == "__main__":
    recs, n_out = generate()
    out = sys.argv[1] if len(sys.argv) > 1 else "synthetic_bearings.jsonl"
    with open(out, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {len(recs)} bearings ({n_out} injected outliers) to {out}")
