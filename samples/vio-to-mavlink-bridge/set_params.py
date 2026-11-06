#!/usr/bin/env python3
"""Set autopilot parameters over MAVLink and optionally reboot. Needs pymavlink.

  python3 set_params.py --connect tcp:127.0.0.1:5762 VISO_TYPE=1 EK3_SRC1_POSXY=6 --reboot
"""
import argparse
import time

from pymavlink import mavutil

PARAM_ACK_TIMEOUT_S = 3.0


def set_param(m, name, value):
    m.mav.param_set_send(m.target_system, m.target_component, name.encode(), float(value),
                         mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
    deadline = time.time() + PARAM_ACK_TIMEOUT_S
    while time.time() < deadline:
        msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
        if msg and msg.param_id == name:
            return msg.param_value
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("params", nargs="+", metavar="NAME=VALUE")
    p.add_argument("--connect", default="tcp:127.0.0.1:5762")
    p.add_argument("--reboot", action="store_true")
    args = p.parse_args()

    m = mavutil.mavlink_connection(args.connect)
    m.wait_heartbeat()
    for item in args.params:
        name, value = item.split("=", 1)
        print(f"{name} = {set_param(m, name, value)}")
    if args.reboot:
        m.mav.command_long_send(m.target_system, m.target_component,
                                mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
                                0, 1, 0, 0, 0, 0, 0, 0)
        print("reboot sent")


if __name__ == "__main__":
    main()
