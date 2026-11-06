"""Write a gps-sdr-sim `-x` user-motion file (10 Hz rows: t, lat, lon, h) for the spoofer.

Starts at an offset from the true receiver position, holds there for --hold-s, then accelerates
at --accel up to (vn, ve). With zero offset and a hold, the spoofer is code- and carrier-aligned
with the authentic signal (same generator, nav file and start time) until it starts to drag off.
Stdlib only.
"""
import argparse
import math

EARTH_RADIUS_M = 6378137.0
RATE_HZ = 10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--h", type=float, default=100.0)
    ap.add_argument("--north-m", type=float, default=2000.0, help="start offset north of truth")
    ap.add_argument("--east-m", type=float, default=2000.0, help="start offset east of truth")
    ap.add_argument("--vn", type=float, default=0.0, help="north velocity m/s")
    ap.add_argument("--ve", type=float, default=20.0, help="east velocity m/s")
    ap.add_argument("--hold-s", type=float, default=0.0, help="stay at the start offset this long")
    ap.add_argument("--accel", type=float, default=0.0, help="m/s^2 after the hold; 0 = jump to (vn, ve)")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    m_per_deg_lat = math.pi * EARTH_RADIUS_M / 180.0
    m_per_deg_lon = m_per_deg_lat * math.cos(math.radians(a.lat))
    with open(a.out, "w") as f:
        for i in range(int(a.duration * RATE_HZ) + 1):
            t = i / RATE_HZ
            n, e = a.north_m, a.east_m
            m = max(0.0, t - a.hold_s)
            for v, axis in ((a.vn, "n"), (a.ve, "e")):
                if a.accel > 0 and v != 0:
                    t_acc = abs(v) / a.accel
                    d = (0.5 * a.accel * m * m if m < t_acc
                         else 0.5 * a.accel * t_acc * t_acc + abs(v) * (m - t_acc))
                    d = math.copysign(d, v)
                else:
                    d = v * m
                if axis == "n":
                    n += d
                else:
                    e += d
            f.write(f"{t:.1f},{a.lat + n / m_per_deg_lat:.9f},"
                    f"{a.lon + e / m_per_deg_lon:.9f},{a.h:.3f}\n")


if __name__ == "__main__":
    main()
