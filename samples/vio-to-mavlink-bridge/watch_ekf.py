#!/usr/bin/env python3
"""Print STATUSTEXT and a once-per-second EKF summary for N seconds. Needs pymavlink.

ArduPilot: EKF_STATUS_REPORT flags. PX4: ESTIMATOR_STATUS flags are not decoded here;
use `listener estimator_status_flags` in the pxh> shell instead.
"""
import argparse
import time

from pymavlink import mavutil

EKF_STATUS_REPORT_ID = 193
LOCAL_POSITION_NED_ID = 32
REPORT_INTERVAL_US = 200_000
POS_HORIZ_REL = 8
POS_HORIZ_ABS = 16
CONST_POS_MODE = 128


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--connect", default="tcp:127.0.0.1:5763")
    p.add_argument("--seconds", type=float, default=30.0)
    args = p.parse_args()

    m = mavutil.mavlink_connection(args.connect)
    m.wait_heartbeat()
    for msg_id in (EKF_STATUS_REPORT_ID, LOCAL_POSITION_NED_ID):
        m.mav.command_long_send(m.target_system, m.target_component,
                                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                                0, msg_id, REPORT_INTERVAL_US, 0, 0, 0, 0, 0)
    end = time.time() + args.seconds
    last, pos = 0.0, None
    while time.time() < end:
        msg = m.recv_match(type=["STATUSTEXT", "EKF_STATUS_REPORT", "LOCAL_POSITION_NED"],
                           blocking=True, timeout=1)
        if msg is None:
            continue
        kind = msg.get_type()
        if kind == "STATUSTEXT":
            print(f"STATUSTEXT: {msg.text}")
        elif kind == "LOCAL_POSITION_NED":
            pos = (msg.x, msg.y, msg.z)
        elif time.time() - last >= 1.0:
            f = msg.flags
            horiz = ("abs" if f & POS_HORIZ_ABS else "rel" if f & POS_HORIZ_REL else "none")
            const = " CONST_POS_MODE" if f & CONST_POS_MODE else ""
            ned = "n/a" if pos is None else "(%.2f, %.2f, %.2f)" % pos
            print(f"ekf flags=0x{f:04x} horiz={horiz}{const} pos_h_var={msg.pos_horiz_variance:.2f} "
                  f"local_ned={ned}")
            last = time.time()


if __name__ == "__main__":
    main()
