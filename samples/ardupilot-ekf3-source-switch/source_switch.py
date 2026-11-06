#!/usr/bin/env python3
"""ArduCopter SITL: fly on GPS, switch EKF3 to source set 2 (vicon ExternalNav),
cut simulated GPS, keep flying, restore GPS, switch back, RTL.
Logs EKF_STATUS_REPORT to CSV. Requires pymavlink and sim_vehicle.py SITL.
"""
import argparse
import csv
import time

from pymavlink import mavutil

import ekf_flags

EKF_STATUS_REPORT_ID = 193
GLOBAL_POSITION_INT_ID = 33
GPS_RAW_INT_ID = 24
LOCAL_POSITION_NED_ID = 32
REPORT_INTERVAL_US = 200_000
TAKEOFF_ALT_M = 10.0
ALT_REACHED_FRACTION = 0.9
LEG_NORTH_M = 15.0
PHASE_GPS_S = 10.0
PHASE_DENIED_S = 30.0
PHASE_RESTORED_S = 15.0
RC_SOURCE_CHANNEL = 8
RC_PWM_FOR_SET = {1: 1000, 2: 1500, 3: 2000}  # RCx_OPTION=90: low / mid / high
RC_IGNORE = 65535
POSITION_ONLY_MASK = 0b110111111000  # ignore velocity, accel, yaw, yaw rate
TIMEOUT_S = 60.0

SETUP_PARAMS = {
    # From Tools/autotest/arducopter.py GPSViconSwitching and the ArduPilot
    # "GPS / Non-GPS Transitions" wiki page.
    "AHRS_EKF_TYPE": 3,
    "EK3_ENABLE": 1,
    "EK2_ENABLE": 0,
    "VISO_TYPE": 2,
    "SERIAL5_PROTOCOL": 2,
    "EK3_SRC1_POSXY": 3,  # GPS
    "EK3_SRC1_VELXY": 3,  # GPS
    "EK3_SRC1_POSZ": 1,   # Baro
    "EK3_SRC1_VELZ": 3,   # GPS
    "EK3_SRC1_YAW": 1,    # Compass
    "EK3_SRC2_POSXY": 6,  # ExternalNav
    "EK3_SRC2_VELXY": 6,
    "EK3_SRC2_POSZ": 1,
    "EK3_SRC2_VELZ": 6,
    "EK3_SRC2_YAW": 6,
    "EK3_SRC_OPTIONS": 0,  # clear FuseAllVelocities
    "RC8_OPTION": 90,      # EKF source set selector
}


class Vehicle:
    def __init__(self, url):
        self.m = mavutil.mavlink_connection(url)
        self.m.wait_heartbeat()
        self.rc_pwm = None
        self.gps_fix = None
        self.local_ne = None
        print(f"heartbeat from sys {self.m.target_system} comp {self.m.target_component}")

    def command(self, cmd, *params):
        p = list(params) + [0.0] * (7 - len(params))
        self.m.mav.command_long_send(self.m.target_system, self.m.target_component, cmd, 0, *p)
        ack = self.m.recv_match(type="COMMAND_ACK", condition=f"COMMAND_ACK.command=={cmd}",
                                blocking=True, timeout=5)
        result = ack.result if ack else None
        name = mavutil.mavlink.enums["MAV_CMD"][cmd].name if cmd in mavutil.mavlink.enums["MAV_CMD"] else cmd
        result_name = mavutil.mavlink.enums["MAV_RESULT"][result].name if ack else "no ACK"
        print(f"command {name} => {result_name}")
        return result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def get_param(self, name):
        self.m.mav.param_request_read_send(self.m.target_system, self.m.target_component,
                                           name.encode(), -1)
        deadline = time.time() + 3
        while time.time() < deadline:
            msg = self.m.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
            if msg and msg.param_id == name:
                return msg.param_value
        return None

    def set_param(self, name, value):
        self.m.mav.param_set_send(self.m.target_system, self.m.target_component, name.encode(),
                                  float(value), mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
        print(f"param {name} = {value}")

    def set_source_set(self, source_set, via):
        if via == "cmd":
            return self.command(mavutil.mavlink.MAV_CMD_SET_EKF_SOURCE_SET, source_set)
        self.rc_pwm = RC_PWM_FOR_SET[source_set]
        self.refresh_rc()
        return True

    def refresh_rc(self):
        # Overrides expire after RC_OVERRIDE_TIME, so they must be resent continuously.
        if self.rc_pwm is None:
            return
        ch = [RC_IGNORE] * 8
        ch[RC_SOURCE_CHANNEL - 1] = self.rc_pwm
        self.m.mav.rc_channels_override_send(self.m.target_system, self.m.target_component, *ch)


def set_sim_gps(v, enabled):
    """SIM_GPS1_ENABLE on ArduPilot 4.7/master, SIM_GPS_DISABLE on 4.6 and older."""
    if v.get_param("SIM_GPS1_ENABLE") is not None:
        v.set_param("SIM_GPS1_ENABLE", 1 if enabled else 0)
    elif v.get_param("SIM_GPS_DISABLE") is not None:
        v.set_param("SIM_GPS_DISABLE", 0 if enabled else 1)
    else:
        raise RuntimeError("no SIM_GPS1_ENABLE or SIM_GPS_DISABLE parameter: is this SITL?")


def log_phase(v, writer, phase, duration_s):
    end = time.time() + duration_s
    last_print = 0.0
    while time.time() < end:
        v.refresh_rc()
        msg = v.m.recv_match(type=["EKF_STATUS_REPORT", "STATUSTEXT", "GPS_RAW_INT",
                                   "LOCAL_POSITION_NED"], blocking=True, timeout=1)
        if msg is None:
            continue
        if msg.get_type() == "STATUSTEXT":
            print(f"  [{phase}] STATUSTEXT: {msg.text}")
            continue
        if msg.get_type() == "GPS_RAW_INT":
            v.gps_fix = msg.fix_type
            continue
        if msg.get_type() == "LOCAL_POSITION_NED":
            v.local_ne = (msg.x, msg.y)
            continue
        d = msg.to_dict()
        ne = v.local_ne or (float("nan"), float("nan"))
        writer.writerow([f"{time.time():.2f}", phase, d["flags"],
                         "|".join(ekf_flags.decode(d["flags"]))] +
                        [f"{d[f]:.3f}" for f in ekf_flags.VARIANCE_FIELDS] +
                        [v.gps_fix, f"{ne[0]:.2f}", f"{ne[1]:.2f}"])
        if time.time() - last_print >= 1.0:
            print(f"  [{phase}] gps_fix={v.gps_fix} ne=({ne[0]:.1f},{ne[1]:.1f}) "
                  f"{ekf_flags.summarize(d)}")
            last_print = time.time()


def wait_for(v, predicate, what):
    deadline = time.time() + TIMEOUT_S
    while time.time() < deadline:
        msg = v.m.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=1)
        if msg and predicate(msg.flags):
            return
    raise TimeoutError(what)


def fly(v, via, log_path):
    # pymavlink requests no streams, so ask for every message this script reads.
    for msg_id in (EKF_STATUS_REPORT_ID, GLOBAL_POSITION_INT_ID, GPS_RAW_INT_ID,
                   LOCAL_POSITION_NED_ID):
        v.command(mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, REPORT_INTERVAL_US)
    v.set_source_set(1, via)
    wait_for(v, ekf_flags.has_absolute_position, "EKF absolute position before arming")

    v.m.set_mode("GUIDED")
    v.m.arducopter_arm()
    v.m.motors_armed_wait()
    v.command(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, TAKEOFF_ALT_M)
    while True:
        pos = v.m.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=TIMEOUT_S)
        if pos is None:
            raise TimeoutError("no GLOBAL_POSITION_INT during takeoff")
        if pos.relative_alt / 1000.0 >= TAKEOFF_ALT_M * ALT_REACHED_FRACTION:
            break

    with open(log_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "phase", "flags", "flag_names"] + list(ekf_flags.VARIANCE_FIELDS) +
                   ["gps_fix", "north_m", "east_m"])
        log_phase(v, w, "gps", PHASE_GPS_S)

        v.set_source_set(2, via)
        set_sim_gps(v, enabled=False)
        v.m.mav.set_position_target_local_ned_send(
            0, v.m.target_system, v.m.target_component, mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            POSITION_ONLY_MASK, LEG_NORTH_M, 0, -TAKEOFF_ALT_M, 0, 0, 0, 0, 0, 0, 0, 0)
        log_phase(v, w, "extnav-no-gps", PHASE_DENIED_S)

        set_sim_gps(v, enabled=True)
        log_phase(v, w, "gps-back-extnav", PHASE_GPS_S)
        v.set_source_set(1, via)
        log_phase(v, w, "gps-restored", PHASE_RESTORED_S)

    v.m.set_mode("RTL")
    print(f"RTL commanded; EKF log written to {log_path}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--connect", default="tcp:127.0.0.1:5762")
    p.add_argument("--setup", action="store_true", help="write SETUP_PARAMS and reboot, then exit")
    p.add_argument("--switch-via", choices=("cmd", "rc"), default="cmd",
                   help="MAV_CMD_SET_EKF_SOURCE_SET or RC8 aux switch (RC8_OPTION=90)")
    p.add_argument("--log", default="ekf_status_log.csv")
    args = p.parse_args()

    v = Vehicle(args.connect)
    if args.setup:
        for name, value in SETUP_PARAMS.items():
            v.set_param(name, value)
        time.sleep(1)
        v.command(mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 1)
        print("rebooting; rerun without --setup once SITL is back")
        return
    fly(v, args.switch_via, args.log)


if __name__ == "__main__":
    main()
