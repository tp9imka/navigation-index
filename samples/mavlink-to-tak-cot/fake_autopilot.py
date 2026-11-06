"""Offline MAVLink source: HEARTBEAT at 1 Hz and GLOBAL_POSITION_INT at 10 Hz on a circle. Needs pymavlink.

  python3 fake_autopilot.py --out udpout:127.0.0.1:14550 --seconds 15
"""
import argparse
import math
import time

from pymavlink import mavutil

CENTER_LAT, CENTER_LON = 51.5007, -0.1246
RADIUS_M = 200.0
SPEED_MPS = 15.0
ALT_AMSL_M = 120.0
RATE_HZ = 10
M_PER_DEG_LAT = 111_320.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="udpout:127.0.0.1:14550")
    ap.add_argument("--seconds", type=float, default=15.0)
    args = ap.parse_args()
    conn = mavutil.mavlink_connection(args.out, source_system=1, source_component=1)
    omega = SPEED_MPS / RADIUS_M
    t0 = time.monotonic()
    k = 0
    while (t := time.monotonic() - t0) < args.seconds:
        if k % RATE_HZ == 0:
            conn.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_FIXED_WING,
                                    mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA, 0, 0, 0)
        ang = omega * t
        north, east = RADIUS_M * math.sin(ang), RADIUS_M * (1 - math.cos(ang))
        vn, ve = SPEED_MPS * math.cos(ang), SPEED_MPS * math.sin(ang)
        lat = CENTER_LAT + north / M_PER_DEG_LAT
        lon = CENTER_LON + east / (M_PER_DEG_LAT * math.cos(math.radians(CENTER_LAT)))
        hdg_cdeg = round(math.degrees(math.atan2(ve, vn)) % 360 * 100)
        conn.mav.global_position_int_send(int(t * 1000), round(lat * 1e7), round(lon * 1e7),
                                          round(ALT_AMSL_M * 1000), round(ALT_AMSL_M * 1000),
                                          round(vn * 100), round(ve * 100), 0, hdg_cdeg)
        k += 1
        time.sleep(1 / RATE_HZ)


if __name__ == "__main__":
    main()
