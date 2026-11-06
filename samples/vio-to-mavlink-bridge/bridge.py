#!/usr/bin/env python3
"""Replay an ENU/FLU pose CSV (t,x,y,z,qw,qx,qy,qz) to an autopilot as
VISION_POSITION_ESTIMATE or ODOMETRY.

--dry-run prints the converted message fields as JSON lines and needs only the
stdlib. Without it, pymavlink is required.
"""
import argparse
import csv
import json
import math
import os
import sys
import time

import frames

MAV_FRAME_LOCAL_NED = 1
MAV_FRAME_BODY_FRD = 12
MAV_FRAME_LOCAL_FRD = 20
MAV_ESTIMATOR_TYPE_VIO = 3
MAV_COMP_ID_VISUAL_INERTIAL_ODOMETRY = 197
MAV_TYPE_ONBOARD_CONTROLLER = 18
MAV_AUTOPILOT_INVALID = 8

HEARTBEAT_PERIOD_S = 1.0
LOOP_GAP_S = 0.1
DEFAULT_POS_STD_M = 0.05
DEFAULT_ANG_STD_RAD = math.radians(2.0)


def read_poses(path):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            yield (
                float(row["t"]),
                (float(row["x"]), float(row["y"]), float(row["z"])),
                (float(row["qw"]), float(row["qx"]), float(row["qy"]), float(row["qz"])),
            )


def looped(path):
    """Replays the file forever, shifting timestamps so time keeps increasing."""
    offset = 0.0
    while True:
        last_t = 0.0
        for t, pos, q in read_poses(path):
            last_t = t
            yield t + offset, pos, q
        offset += last_t + LOOP_GAP_S


def build_messages(poses, frame_id, pos_std_m, ang_std_rad):
    """Yields (t, dict) with MAVLink-ready fields for both message types."""
    pose_cov = frames.diag_covariance(pos_std_m ** 2, ang_std_rad ** 2)
    prev = None
    for t, pos_enu, q_enu in poses:
        pos_ned, q_ned = frames.convert_pose(pos_enu, q_enu)
        if prev is None or t <= prev[0]:
            vel_ned = (float("nan"),) * 3
        else:
            dt = t - prev[0]
            vel_ned = tuple((a - b) / dt for a, b in zip(pos_ned, prev[1]))
        vel_body = frames.world_to_body(q_ned, vel_ned) if not math.isnan(vel_ned[0]) else vel_ned
        roll, pitch, yaw = frames.quat_to_euler(q_ned)
        prev = (t, pos_ned)
        yield t, {
            "time_usec": int(t * 1e6),
            "frame_id": frame_id,
            "child_frame_id": MAV_FRAME_BODY_FRD,
            "pos_ned": pos_ned,
            "q_ned_frd": q_ned,
            "rpy": (roll, pitch, yaw),
            "vel_body_frd": vel_body,
            "pose_covariance": pose_cov,
        }


def send(mav, msg_type, m, reset_counter=0):
    x, y, z = m["pos_ned"]
    if msg_type == "vpe":
        roll, pitch, yaw = m["rpy"]
        mav.vision_position_estimate_send(
            m["time_usec"], x, y, z, roll, pitch, yaw, m["pose_covariance"], reset_counter)
    else:
        vx, vy, vz = m["vel_body_frd"]
        nan = float("nan")
        mav.odometry_send(
            m["time_usec"], m["frame_id"], m["child_frame_id"], x, y, z, list(m["q_ned_frd"]),
            vx, vy, vz, nan, nan, nan,
            m["pose_covariance"], frames.unknown_covariance(),
            reset_counter, MAV_ESTIMATOR_TYPE_VIO, 0)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv")
    p.add_argument("--msg", choices=("vpe", "odom"), default="odom")
    p.add_argument("--frame", choices=("frd", "ned"), default="frd",
                   help="ODOMETRY frame_id: frd unless the VIO world frame is north-aligned")
    p.add_argument("--connect", default="udpout:127.0.0.1:14580",
                   help="pymavlink connection string (PX4 SITL onboard port 14580; "
                        "ArduPilot SITL tcp:127.0.0.1:5762)")
    p.add_argument("--sysid", type=int, default=1, help="match the autopilot SYSID_THISMAV / MAV_SYS_ID")
    p.add_argument("--pos-std", type=float, default=DEFAULT_POS_STD_M)
    p.add_argument("--ang-std", type=float, default=DEFAULT_ANG_STD_RAD)
    p.add_argument("--loop", action="store_true", help="replay the CSV forever (not with --dry-run)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    frame_id = MAV_FRAME_LOCAL_FRD if args.frame == "frd" else MAV_FRAME_LOCAL_NED
    poses = looped(args.csv) if args.loop and not args.dry_run else read_poses(args.csv)
    msgs = build_messages(poses, frame_id, args.pos_std, args.ang_std)

    if args.dry_run:
        for t, m in msgs:
            out = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()
                   if k != "pose_covariance"}
            for k in ("pos_ned", "q_ned_frd", "rpy", "vel_body_frd"):
                out[k] = [round(c, 4) for c in m[k]]
            print(json.dumps(out))
        return 0

    # ODOMETRY (id 331) exists only in the MAVLink 2 dialect, which pymavlink loads
    # when MAVLINK20 is set before import.
    os.environ.setdefault("MAVLINK20", "1")
    from pymavlink import mavutil  # imported late so --dry-run works without it

    conn = mavutil.mavlink_connection(
        args.connect, source_system=args.sysid,
        source_component=MAV_COMP_ID_VISUAL_INERTIAL_ODOMETRY)
    start_wall = time.monotonic()
    t0 = None
    last_hb = 0.0
    for t, m in msgs:
        t0 = t if t0 is None else t0
        delay = (t - t0) - (time.monotonic() - start_wall)
        if delay > 0:
            time.sleep(delay)
        now = time.monotonic()
        if now - last_hb >= HEARTBEAT_PERIOD_S:
            conn.mav.heartbeat_send(MAV_TYPE_ONBOARD_CONTROLLER, MAV_AUTOPILOT_INVALID, 0, 0, 0)
            last_hb = now
        # Stamp with the bridge clock; both autopilots correct offboard timestamps.
        m["time_usec"] = int((now - start_wall) * 1e6)
        send(conn.mav, args.msg, m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
