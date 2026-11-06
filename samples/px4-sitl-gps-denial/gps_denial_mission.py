#!/usr/bin/env python3
"""PX4 SITL: fly a square mission, switch the GPS off mid-mission with MAVSDK failure
injection, log EKF2 health and position vs ground truth, restore GPS, return home.

Requires `pip install mavsdk-grpc` and a running `make px4_sitl gz_x500`.
Writes a CSV that drift.py summarizes.
"""
import argparse
import asyncio
import csv
import math
import time

from mavsdk_grpc import System
from mavsdk_grpc.failure import FailureType, FailureUnit
from mavsdk_grpc.mission import MissionItem, MissionPlan

import drift

MISSION_ALT_M = 20.0
MISSION_SPEED_M_S = 5.0
SQUARE_SIDE_M = 80.0
DENY_AT_WAYPOINT = 1
DEFAULT_DENIAL_S = 15.0
RECOVERY_TIMEOUT_S = 60.0
LOG_RATE_HZ = 5.0
GPS_INSTANCE = 0


class FlightLog:
    def __init__(self):
        self.phase = "pre-denial"
        self.est = (None, None)
        self.truth = (None, None)
        self.health = None
        self.gps = None


def square_mission(home_lat, home_lon):
    corners = [(SQUARE_SIDE_M, 0.0), (SQUARE_SIDE_M, SQUARE_SIDE_M), (0.0, SQUARE_SIDE_M), (0.0, 0.0)]
    items = []
    for north, east in corners:
        lat, lon = drift.ne_to_latlon(north, east, home_lat, home_lon)
        nan = float("nan")
        items.append(MissionItem(
            lat, lon, MISSION_ALT_M, MISSION_SPEED_M_S, True, nan, nan,
            MissionItem.CameraAction.NONE, nan, nan, nan, nan, nan,
            MissionItem.VehicleAction.NONE))
    return MissionPlan(items)


async def watch_position(drone, log):
    async for p in drone.telemetry.position():
        log.est = (p.latitude_deg, p.longitude_deg)


async def watch_truth(drone, log):
    # Ground truth arrives only if the simulator streams HIL_STATE_QUATERNION; when it
    # does not, truth stays empty and drift.py reports "not measured".
    async for g in drone.telemetry.ground_truth():
        if not math.isnan(g.latitude_deg):
            log.truth = (g.latitude_deg, g.longitude_deg)


async def watch_health(drone, log):
    async for h in drone.telemetry.health():
        log.health = h


async def watch_gps(drone, log):
    async for g in drone.telemetry.gps_info():
        log.gps = g


async def record(log, path, stop):
    period = 1.0 / LOG_RATE_HZ
    t0 = time.monotonic()
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "phase", "est_lat", "est_lon", "true_lat", "true_lon",
                    "global_ok", "local_ok", "gps_sats", "gps_fix"])
        last_print = 0.0
        while not stop.is_set():
            h, g = log.health, log.gps
            row = [f"{time.monotonic() - t0:.2f}", log.phase,
                   *("" if v is None else f"{v:.9f}" for v in log.est + log.truth),
                   h.is_global_position_ok if h else "", h.is_local_position_ok if h else "",
                   g.num_satellites if g else "", g.fix_type if g else ""]
            w.writerow(row)
            if time.monotonic() - last_print >= 1.0:
                print("  " + " ".join(str(c) for c in row))
                last_print = time.monotonic()
            await asyncio.sleep(period)


async def wait_until(aiter_fn, predicate):
    async for item in aiter_fn():
        if predicate(item):
            return item


async def run(args):
    drone = System()
    await drone.connect(system_address=args.connect)
    await wait_until(drone.core.connection_state, lambda s: s.is_connected)
    print("connected")
    await wait_until(drone.telemetry.health, lambda h: h.is_global_position_ok and h.is_home_position_ok)
    home = await wait_until(drone.telemetry.home, lambda p: not math.isnan(p.latitude_deg))

    await drone.param.set_param_int("SYS_FAILURE_EN", 1)
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(square_mission(home.latitude_deg, home.longitude_deg))
    for setter in (drone.telemetry.set_rate_position, drone.telemetry.set_rate_ground_truth):
        try:
            await setter(LOG_RATE_HZ)
        except Exception as exc:  # a rate request the autopilot rejects is not fatal
            print(f"rate request failed: {exc}")

    log, stop = FlightLog(), asyncio.Event()
    tasks = [asyncio.create_task(c) for c in (
        watch_position(drone, log), watch_truth(drone, log), watch_health(drone, log),
        watch_gps(drone, log), record(log, args.log, stop))]

    await drone.action.arm()
    await drone.mission.start_mission()
    await wait_until(drone.mission.mission_progress, lambda m: m.current >= DENY_AT_WAYPOINT)

    print(f"-- GPS OFF for {args.denial_s:.0f} s")
    log.phase = drift.DENIED_PHASE
    await drone.failure.inject(FailureUnit.SENSOR_GPS, FailureType.OFF, instance=GPS_INSTANCE)
    await asyncio.sleep(args.denial_s)

    print("-- GPS restored")
    log.phase = "recovery"
    await drone.failure.inject(FailureUnit.SENSOR_GPS, FailureType.OK, instance=GPS_INSTANCE)
    try:
        await asyncio.wait_for(
            wait_until(drone.telemetry.health, lambda h: h.is_global_position_ok),
            RECOVERY_TIMEOUT_S)
        print("-- global position OK again, returning to launch")
    except asyncio.TimeoutError:
        print("-- global position did not recover in time; returning to launch anyway")
    try:
        await drone.action.return_to_launch()
    except Exception as exc:  # e.g. a position-loss failsafe already landed the vehicle
        print(f"RTL rejected: {exc}")
    await wait_until(drone.telemetry.in_air, lambda in_air: not in_air)

    stop.set()
    await drone.param.set_param_int("SYS_FAILURE_EN", 0)
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"log written to {args.log}; run: python3 drift.py {args.log}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--connect", default="udpin://0.0.0.0:14540")
    p.add_argument("--denial-s", type=float, default=DEFAULT_DENIAL_S)
    p.add_argument("--log", default="flight_log.csv")
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
