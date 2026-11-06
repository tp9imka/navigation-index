#!/usr/bin/env python3
"""Golden demo companion: flies an ArduCopter SITL AUTO mission, drags its GPS with
SIM_GPS_GLITCH_X/Y, streams simulated visual-geolocation fixes as VISION_POSITION_ESTIMATE,
runs navapp's chi-square monitor on GNSS vs a VIO dead-reckoning + alt-PNT reference, and on alarm switches
EKF3 to source set 2 (ExternalNav). Every MAVLink message it reads is logged to JSONL.

    python companion.py --connect tcp:127.0.0.1:15766 --mode monitor  --log runs/monitor.raw.jsonl
    python companion.py --connect tcp:127.0.0.1:15766 --mode baseline --log runs/baseline.raw.jsonl

baseline runs the same monitor in shadow mode: it logs verdicts but never acts.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

from pymavlink import mavutil

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "templates" / "project-repo" / "src"))

from navapp.filter import DeadReckoningFilter  # noqa: E402
from navapp.geo import enu_to_geodetic, geodetic_to_enu  # noqa: E402
from navapp.integrity import ChiSquareMonitor  # noqa: E402
from navapp.interfaces import Epoch, Health, Vec2  # noqa: E402

TAKEOFF_ALT_M = 30.0
# Lawnmower survey legs as (north, east) metres from home, flown at WPNAV_SPEED (golden.parm).
# The drag is east, so it is cross-track on the two long legs.
MISSION_NE = [(400.0, 0.0), (400.0, 150.0), (0.0, 150.0)]

SPOOF_ONSET_S = 25.0          # after AUTO starts
SPOOF_RATE_MPS = 1.0
SPOOF_BEARING_DEG = 90.0      # GPS is dragged east => the copter really drifts west
SPOOF_MAX_M = 150.0
SPOOF_UPDATE_S = 0.5
EARTH_R_M = 6371008.8         # SITL glitch offsets are plain lat/lon degrees

VGEO_HZ = 5.0
VGEO_SIGMA_M = 1.5            # simulated visual-geoloc noise (truth + Gaussian)
VGEO_SIGMA_ASSUMED_M = 2.5
VIO_SIGMA_MPS = 0.1
VIO_BIAS_EN_MPS = (0.05, -0.03)
GNSS_SIGMA_ASSUMED_M = 2.0
MONITOR_PERIOD_S = 1.0

EKF_SOURCE_SET_EXTNAV = 2
MAV_CMD_SET_EKF_SOURCE_SET = 42007
GPS_GLOBAL_ORIGIN_ID = 49
END_HOLD_S = 5.0
ARM_RETRY_S = 2.0
ORIGIN_RETRY_S = 2.0
SETUP_TIMEOUT_S = 120.0
RUN_TIMEOUT_S = 400.0
CONNECT_RETRIES = 60

STREAMS_HZ = {
    "GPS_RAW_INT": 5, "GLOBAL_POSITION_INT": 10, "EKF_STATUS_REPORT": 2, "SIMSTATE": 10,
    "SIM_STATE": 10, "RAW_IMU": 10, "LOCAL_POSITION_NED": 5, "MISSION_CURRENT": 1,
    "VFR_HUD": 2,
}
LOGGED = set(STREAMS_HZ) | {"STATUSTEXT", "COMMAND_ACK", "HEARTBEAT", "MISSION_ITEM_REACHED",
                            "GPS_GLOBAL_ORIGIN", "HOME_POSITION", "PARAM_VALUE"}


def offset_deg(north_m: float, east_m: float, lat_deg: float) -> tuple[float, float]:
    dlat = math.degrees(north_m / EARTH_R_M)
    dlon = math.degrees(east_m / (EARTH_R_M * math.cos(math.radians(lat_deg))))
    return dlat, dlon


def spoof_offset_m(t: float) -> float:
    return 0.0 if t < SPOOF_ONSET_S else min(SPOOF_RATE_MPS * (t - SPOOF_ONSET_S), SPOOF_MAX_M)


class Companion:
    def __init__(self, url: str, mode: str, log_path: Path, seed: int):
        self.mode = mode
        self.rng = random.Random(seed)
        self.log = log_path.open("w")
        self.t0 = time.monotonic()
        self.m = mavutil.mavlink_connection(url, source_system=255, source_component=191,
                                            retries=CONNECT_RETRIES)
        self.m.wait_heartbeat()
        self.origin = None          # (lat, lon, alt) of the EKF origin
        self.truth = None           # (lat, lon)
        self.truth_alt = None
        self.truth_vel = None       # (east, north) m/s
        self.truth_yaw = 0.0
        self.gps = None             # (lat, lon) as received, spoofed
        self.armed = False
        self.alt_rel = 0.0
        self.t_auto = None
        self.last_reached = -1
        self.next_vgeo = self.next_spoof = self.next_monitor = 0.0
        self.last_vgeo = None
        self.filter = DeadReckoningFilter()
        self.monitor = ChiSquareMonitor()
        self.acted = False
        self.record({"type": "COMPANION_START", "mode": mode, "seed": seed,
                     "spoof": {"onset_s": SPOOF_ONSET_S, "rate_mps": SPOOF_RATE_MPS,
                               "bearing_deg": SPOOF_BEARING_DEG, "max_m": SPOOF_MAX_M},
                     "vgeo": {"hz": VGEO_HZ, "sigma_m": VGEO_SIGMA_M},
                     "vio": {"sigma_mps": VIO_SIGMA_MPS, "bias_en_mps": VIO_BIAS_EN_MPS},
                     "mission_ne": MISSION_NE, "takeoff_alt_m": TAKEOFF_ALT_M})

    def now(self) -> float:
        return time.monotonic() - self.t0

    def t_mission(self) -> float | None:
        return None if self.t_auto is None else self.now() - self.t_auto

    def record(self, d: dict) -> None:
        d = {"t_host": round(self.now(), 3), "t": self.t_mission(), **d}
        self.log.write(json.dumps(d, default=str) + "\n")

    # --- MAVLink plumbing -------------------------------------------------------------
    def command(self, cmd: int, *p: float) -> None:
        p = list(p) + [0.0] * (7 - len(p))
        self.m.mav.command_long_send(self.m.target_system, self.m.target_component, cmd, 0, *p)

    def request_streams(self) -> None:
        for name, hz in STREAMS_HZ.items():
            msg_id = getattr(mavutil.mavlink, f"MAVLINK_MSG_ID_{name}")
            self.command(mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, 1e6 / hz)

    def pump(self, until, timeout: float, what: str) -> None:
        deadline = self.now() + timeout
        while not until():
            if self.now() > deadline:
                raise TimeoutError(what)
            msg = self.m.recv_match(blocking=True, timeout=0.02)
            if msg is not None:
                self.handle(msg)
            self.service()

    def handle(self, msg) -> None:
        kind = msg.get_type()
        if kind == "BAD_DATA":
            return
        if kind in LOGGED:
            self.record(msg.to_dict() | {"type": kind})
        if kind == "SIMSTATE":
            self.truth = (msg.lat * 1e-7, msg.lng * 1e-7)
            self.truth_yaw = msg.yaw
        elif kind == "SIM_STATE":
            self.truth_alt = msg.alt
            self.truth_vel = (msg.ve, msg.vn)
        elif kind == "GPS_RAW_INT" and msg.fix_type >= 3:
            self.gps = (msg.lat * 1e-7, msg.lon * 1e-7)
        elif kind == "GPS_GLOBAL_ORIGIN" and self.origin is None:
            self.origin = (msg.latitude * 1e-7, msg.longitude * 1e-7, msg.altitude * 1e-3)
        elif kind == "HEARTBEAT" and msg.get_srcComponent() == 1:
            self.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        elif kind == "GLOBAL_POSITION_INT":
            self.alt_rel = msg.relative_alt * 1e-3
        elif kind == "MISSION_ITEM_REACHED":
            self.last_reached = max(self.last_reached, msg.seq)
        elif kind == "STATUSTEXT":
            print(f"  STATUSTEXT: {msg.text}")

    def service(self) -> None:
        now = self.now()
        if self.origin and self.truth and self.truth_alt is not None and now >= self.next_vgeo:
            self.next_vgeo = now + 1.0 / VGEO_HZ
            self.send_vgeo()
        t = self.t_mission()
        if t is None:
            return
        if t >= SPOOF_ONSET_S and now >= self.next_spoof:
            self.next_spoof = now + SPOOF_UPDATE_S
            self.update_spoof(t)
        if now >= self.next_monitor and self.truth_vel and self.last_vgeo:
            self.next_monitor = now + MONITOR_PERIOD_S
            self.monitor_step(t)

    # --- simulated sensors and the attack ---------------------------------------------
    def send_vgeo(self) -> None:
        """Visual geolocation stand-in: truth + Gaussian noise, in the EKF origin's NED frame."""
        lat0, lon0, alt0 = self.origin
        e, n = geodetic_to_enu(*self.truth, lat0, lon0)
        e += self.rng.gauss(0.0, VGEO_SIGMA_M)
        n += self.rng.gauss(0.0, VGEO_SIGMA_M)
        down = -(self.truth_alt - alt0)
        cov = [math.nan] + [0.0] * 20
        self.m.mav.vision_position_estimate_send(int(time.time() * 1e6), n, e, down,
                                                 0.0, 0.0, self.truth_yaw, cov, 0)
        self.last_vgeo = Vec2(e, n)
        lat, lon = enu_to_geodetic(e, n, lat0, lon0)
        self.record({"type": "COMPANION_VGEO", "lat": lat, "lon": lon, "east": e, "north": n})

    def update_spoof(self, t: float) -> None:
        off = spoof_offset_m(t)
        b = math.radians(SPOOF_BEARING_DEG)
        dlat, dlon = offset_deg(off * math.cos(b), off * math.sin(b), self.truth[0])
        self.m.param_set_send("SIM_GPS_GLITCH_X", dlat)
        self.m.param_set_send("SIM_GPS_GLITCH_Y", dlon)
        self.record({"type": "COMPANION_SPOOF", "offset_m": off, "glitch_x_deg": dlat,
                     "glitch_y_deg": dlon})

    def monitor_step(self, t: float) -> None:
        lat0, lon0, _ = self.origin
        ve, vn = self.truth_vel
        vio = Vec2(ve + VIO_BIAS_EN_MPS[0] + self.rng.gauss(0, VIO_SIGMA_MPS),
                   vn + VIO_BIAS_EN_MPS[1] + self.rng.gauss(0, VIO_SIGMA_MPS))
        ep_vgeo = Epoch(t, vio, VIO_SIGMA_MPS, self.last_vgeo, VGEO_SIGMA_ASSUMED_M, "vgeo")
        self.filter.predict(ep_vgeo)
        self.filter.update(ep_vgeo)
        gnss = Vec2(*geodetic_to_enu(*self.gps, lat0, lon0)) if self.gps else None
        ep_gnss = Epoch(t, None, VIO_SIGMA_MPS, gnss, GNSS_SIGMA_ASSUMED_M, "gnss")
        # GNSS is only tested, never fused: the reference (VIO dead reckoning + visual geoloc)
        # stays independent of the signal under test, so a slow drag cannot pull it along.
        verdict = self.monitor.check(ep_gnss, self.filter.innovation(ep_gnss))
        st = self.filter.state(t)
        lat, lon = enu_to_geodetic(st.position.east, st.position.north, lat0, lon0)
        self.record({"type": "COMPANION_MONITOR", "health": verdict.health.value,
                     "alarm": verdict.alarm, "statistic": verdict.statistic,
                     "threshold": verdict.threshold, "reason": verdict.reason,
                     "lat": lat, "lon": lon, "sigma_h": st.sigma_h,
                     "sources": list(st.sources_used)})
        if verdict.alarm and verdict.health == Health.EXCLUDED and not self.acted:
            self.acted = True
            if self.mode == "monitor":
                self.command(MAV_CMD_SET_EKF_SOURCE_SET, EKF_SOURCE_SET_EXTNAV)
                print(f"t={t:.1f}s ALARM ({verdict.reason}) => EKF source set {EKF_SOURCE_SET_EXTNAV}")
                self.record({"type": "COMPANION_ACTION", "action": "set_ekf_source_set",
                             "source_set": EKF_SOURCE_SET_EXTNAV, "reason": verdict.reason})
            else:
                print(f"t={t:.1f}s ALARM ({verdict.reason}) - shadow mode, no action")
                self.record({"type": "COMPANION_ACTION", "action": "none_shadow_mode",
                             "reason": verdict.reason})

    # --- flight -------------------------------------------------------------------------
    def upload_mission(self) -> None:
        lat0, lon0, _ = self.origin
        items = [(mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, lat0, lon0, 0.0),
                 (mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, lat0, lon0, TAKEOFF_ALT_M)]
        for n, e in MISSION_NE:
            lat, lon = enu_to_geodetic(e, n, lat0, lon0)
            items.append((mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, lat, lon, TAKEOFF_ALT_M))
        self.m.mav.mission_count_send(self.m.target_system, self.m.target_component, len(items), 0)
        deadline = self.now() + 30
        while self.now() < deadline:
            msg = self.m.recv_match(type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
                                    blocking=True, timeout=1)
            self.service()
            if msg is None:
                continue
            if msg.get_type() == "MISSION_ACK":
                print(f"mission upload: {mavutil.mavlink.enums['MAV_MISSION_RESULT'][msg.type].name}")
                return
            cmd, lat, lon, alt = items[msg.seq]
            self.m.mav.mission_item_int_send(
                self.m.target_system, self.m.target_component, msg.seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, cmd, 0, 1, 0, 0, 0, 0,
                int(lat * 1e7), int(lon * 1e7), alt, 0)
        raise TimeoutError("mission upload")

    def set_mode(self, name: str) -> None:
        self.m.set_mode(self.m.mode_mapping()[name])

    def run(self) -> None:
        self.request_streams()
        next_req = 0.0

        def have_origin():
            nonlocal next_req
            if self.origin is None and self.now() > next_req:
                next_req = self.now() + ORIGIN_RETRY_S
                self.command(mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE, GPS_GLOBAL_ORIGIN_ID)
            return self.origin is not None

        self.pump(have_origin, SETUP_TIMEOUT_S, "EKF origin")
        print(f"EKF origin {self.origin}")
        self.upload_mission()
        self.set_mode("GUIDED")
        next_arm = 0.0

        def armed():
            nonlocal next_arm
            if not self.armed and self.now() > next_arm:
                next_arm = self.now() + ARM_RETRY_S
                self.set_mode("GUIDED")
                self.command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)
            return self.armed

        self.pump(armed, SETUP_TIMEOUT_S, "arming")
        print("armed")
        self.command(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, TAKEOFF_ALT_M)
        self.pump(lambda: self.alt_rel > 0.9 * TAKEOFF_ALT_M, 60, "takeoff")
        self.set_mode("AUTO")
        self.t_auto = self.now()
        self.record({"type": "COMPANION_AUTO_START"})
        print("AUTO started (t=0)")
        last_seq = len(MISSION_NE) + 1
        self.pump(lambda: self.last_reached >= last_seq, RUN_TIMEOUT_S, "mission")
        t_end = self.now() + END_HOLD_S
        self.pump(lambda: self.now() > t_end, END_HOLD_S + 5, "end hold")
        self.record({"type": "COMPANION_END"})
        print(f"mission complete at t={self.t_mission():.1f}s")
        self.log.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--connect", default="tcp:127.0.0.1:15766")
    ap.add_argument("--mode", choices=["monitor", "baseline"], required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    a.log.parent.mkdir(parents=True, exist_ok=True)
    Companion(a.connect, a.mode, a.log, a.seed).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
