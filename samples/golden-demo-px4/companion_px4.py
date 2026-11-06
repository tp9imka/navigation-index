#!/usr/bin/env python3
"""Golden demo on PX4 v1.17 SIH: the samples/golden-demo v2 companion (spoof model, replayed
real visual geoloc, SS FDE + PL, GNSS-vs-VIO velocity test, all imported unchanged) driving a
PX4 quad instead of ArduCopter.

What differs from ArduPilot, and why:
- Truth: HIL_STATE_QUATERNION (SIH ground truth) instead of SIMSTATE / SIM_STATE.
- GNSS: this process feeds the only GPS as MAVLink HIL_GPS at 10 Hz (MAV_USEHILGPS 1; PX4 only
  takes HIL_GPS whose sysid equals its own). run.sh boots SIH with sensor_gps_sim off
  (SENS_EN_GPSSIM 0), so the MAVLink receiver is sensor_gps instance 0 and GPS_RAW_INT shows it.
  v1.17 has no GPS_INPUT handler.
- Alt-PNT: ODOMETRY (pose in the EKF origin NED frame + VIO velocity) => EKF2 external
  vision. EKF2_EV_CTRL stays 0 until the alarm, so the no-monitor run fuses GNSS only, like
  ArduPilot's source set 1.
- Response: PX4 has no EKF source sets. MAV_CMD_SET_EKF_SOURCE_SET from the shared monitor
  logic is translated into PARAM_SET EKF2_GPS_CTRL 0, then EKF2_EV_CTRL (hpos + vel).
- EKF2 starts external vision only with samples < 200 ms apart (EV_MAX_INTERVAL), so the
  reference goes out at 10 Hz, not the 5 Hz the ArduPilot companion uses.
- Flight: AUTO.TAKEOFF to the survey altitude, then AUTO.MISSION; t = 0 at mission start.

    python companion_px4.py --connect udpin:0.0.0.0:14540 --mode monitor --log runs/px4-monitor.raw.jsonl
"""
from __future__ import annotations

import os

os.environ.setdefault("MAVLINK20", "1")     # ODOMETRY is MAVLink 2 only

import argparse  # noqa: E402
import math  # noqa: E402
import struct  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
GOLDEN = HERE.parent / "golden-demo"
sys.path.insert(0, str(GOLDEN))

import companion as G  # noqa: E402
from pymavlink import mavutil  # noqa: E402

M = mavutil.mavlink
STREAMS_HZ = {
    "GPS_RAW_INT": 5, "GLOBAL_POSITION_INT": 10, "ESTIMATOR_STATUS": 2, "HIL_STATE_QUATERNION": 20,
    "LOCAL_POSITION_NED": 5, "MISSION_CURRENT": 1, "VFR_HUD": 2, "EXTENDED_SYS_STATE": 1,
}
LOGGED = set(STREAMS_HZ) | {"STATUSTEXT", "COMMAND_ACK", "HEARTBEAT", "MISSION_ITEM_REACHED",
                            "GPS_GLOBAL_ORIGIN", "HOME_POSITION", "PARAM_VALUE"}

# PX4 custom_mode: main mode in bits 16-23, sub mode in bits 24-31 (px4_custom_mode.h).
PX4_MAIN_AUTO = 4
PX4_SUB = {"TAKEOFF": 2, "LOITER": 3, "MISSION": 4, "RTL": 5, "LAND": 6}

GPS_CTRL_ON = 7               # EKF2_GPS_CTRL: lon/lat + alt + 3D velocity
EV_CTRL_HPOS_VEL = 5          # EKF2_EV_CTRL: horizontal position + velocity
EV_SEND_HZ = 10.0
PX4_SYSID = 1                 # HIL_GPS is only accepted with the autopilot's own sysid
HIL_GPS_SATS = 14
TAKEOFF_TOLERANCE = 0.9


def int_as_float(v: int) -> float:
    return struct.unpack("<f", struct.pack("<i", v))[0]


def float_as_int(f: float) -> int:
    return struct.unpack("<i", struct.pack("<f", f))[0]


def px4_mode(sub: str) -> int:
    return (PX4_MAIN_AUTO << 16) | (PX4_SUB[sub] << 24)


class PX4Companion(G.Companion):
    def __init__(self, a):
        super().__init__(a)
        self.vio_now = (0.0, 0.0)
        self.next_ev = 0.0
        self.hil_gps_on = False

    # --- MAVLink plumbing -------------------------------------------------------------
    def request_streams(self) -> None:
        for name, hz in STREAMS_HZ.items():
            self.command(M.MAV_CMD_SET_MESSAGE_INTERVAL, getattr(M, f"MAVLINK_MSG_ID_{name}"), 1e6 / hz)

    def param_set(self, name: str, value) -> None:
        """PX4 takes INT32 params bytewise in the float field (MAV_PROTOCOL_CAPABILITY_PARAM_ENCODE_BYTEWISE)."""
        if isinstance(value, int):
            self.m.mav.param_set_send(self.m.target_system, self.m.target_component, name.encode(),
                                      int_as_float(value), M.MAV_PARAM_TYPE_INT32)
        else:
            self.m.mav.param_set_send(self.m.target_system, self.m.target_component, name.encode(),
                                      float(value), M.MAV_PARAM_TYPE_REAL32)

    def command(self, cmd: int, *p: float) -> None:
        if cmd != G.MAV_CMD_SET_EKF_SOURCE_SET:
            return super().command(cmd, *p)
        # Shared monitor logic asks for an ArduPilot source set; PX4 does it with EKF2 params.
        # GNSS out first, so external vision starts as the only horizontal position source.
        params = ({"EKF2_GPS_CTRL": 0, "EKF2_EV_CTRL": EV_CTRL_HPOS_VEL} if p[0] == G.EKF_SOURCE_SET_EXTNAV
                  else {"EKF2_EV_CTRL": 0, "EKF2_GPS_CTRL": GPS_CTRL_ON})
        for k, v in params.items():
            self.param_set(k, v)
        self.record({"type": "COMPANION_PX4_ACTION", "params": params})

    def handle(self, msg) -> None:
        super().handle(msg)
        kind = msg.get_type()
        if kind in LOGGED and kind not in G.LOGGED:
            self.record(msg.to_dict() | {"type": kind})
        if kind == "HIL_STATE_QUATERNION":
            self.truth = (msg.lat * 1e-7, msg.lon * 1e-7)
            self.truth_sim_s = self.sim_s
            self.truth_alt = msg.alt * 1e-3
            self.truth_vel = (msg.vy * 0.01, msg.vx * 0.01)
            self.truth_vd = msg.vz * 0.01
            w, x, y, z = msg.attitude_quaternion
            self.truth_yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

    # --- injected sensors ---------------------------------------------------------------
    def send_gps_input(self) -> None:
        """Same noise + spoof model as golden-demo send_gps_input, sent as HIL_GPS."""
        t = self.t_mission()
        dt = 1.0 / G.GPS_INPUT_HZ
        phi = math.exp(-dt / G.GNSS_GM_TAU_S)
        self.gm = [g * phi + self.rng.gauss(0, G.GNSS_GM_SIGMA_M * math.sqrt(1 - phi * phi)) for g in self.gm]
        oe, on = self.spoof.offset_en(t)
        ne = oe + self.gm[0] + self.rng.gauss(0, G.GNSS_WHITE_M)
        nn = on + self.gm[1] + self.rng.gauss(0, G.GNSS_WHITE_M)
        dlat, dlon = G.offset_deg(nn, ne, self.truth[0])
        sve, svn = self.spoof.vel_en(t)
        ve = self.truth_vel[0] + sve + self.rng.gauss(0, G.GNSS_VEL_WHITE_MPS)
        vn = self.truth_vel[1] + svn + self.rng.gauss(0, G.GNSS_VEL_WHITE_MPS)
        cog = math.degrees(math.atan2(ve, vn)) % 360.0
        self.m.mav.srcSystem = PX4_SYSID
        self.m.mav.hil_gps_send(
            self.stamp_us(self.truth_sim_s or self.now()), 3,
            int((self.truth[0] + dlat) * 1e7), int((self.truth[1] + dlon) * 1e7),
            int((self.truth_alt + self.rng.gauss(0, 1.0)) * 1000), 80, 120,
            int(math.hypot(ve, vn) * 100), int(vn * 100), int(ve * 100), int(self.truth_vd * 100),
            int(cog * 100), HIL_GPS_SATS)
        self.m.mav.srcSystem = 255
        if t is not None and t >= self.a.onset and self.a.spoof != "none":
            self.record({"type": "COMPANION_SPOOF", "offset_m": self.spoof.offset_m(t),
                         "vel_add_en": [sve, svn], "kind": self.a.spoof})

    def extnav_send(self, e, n, sim_s, sigma_m=None) -> None:
        """ODOMETRY: position in the EKF origin's NED frame, VIO velocity in NED."""
        _, _, alt0 = self.origin
        sig = sigma_m if sigma_m is not None else G.VGEO_SIGMA_ASSUMED_M[self.a.vgeo]
        pcov = [math.nan] * 21
        pcov[0] = pcov[6] = sig * sig
        pcov[11] = 4.0
        pcov[15] = pcov[18] = pcov[20] = 0.01
        vcov = [math.nan] * 21
        vcov[0] = vcov[6] = vcov[11] = (G.VIO_SIGMA_MPS * 2) ** 2
        ve, vn = self.vio_now
        cy, sy = math.cos(self.truth_yaw / 2), math.sin(self.truth_yaw / 2)
        self.m.mav.odometry_send(self.stamp_us(sim_s), M.MAV_FRAME_LOCAL_NED, M.MAV_FRAME_LOCAL_NED,
                                 n, e, -(self.truth_alt - alt0), [cy, 0.0, 0.0, sy],
                                 vn, ve, self.truth_vd, math.nan, math.nan, math.nan,
                                 pcov, vcov, 0, M.MAV_ESTIMATOR_TYPE_VIO, 0)

    def send_reference(self, now: float) -> None:
        pass                    # replaced by the 10 Hz schedule in service()

    def service(self) -> None:
        if self.truth_vel:
            self.vio_now = self.vio_en()
        super().service()
        now = self.now()
        if self.reference_ready() and self.t_mission() is not None and now >= self.next_ev:
            self.next_ev = now + 1.0 / EV_SEND_HZ
            G.Companion.send_reference(self, now)

    # --- flight ---------------------------------------------------------------------------
    def upload_mission(self) -> None:
        lat0, lon0, _ = self.origin
        items = []
        for n, e in G.MISSION_NE:
            lat, lon = G.enu_to_geodetic(e, n, lat0, lon0)
            items.append((M.MAV_CMD_NAV_WAYPOINT, lat, lon, self.a.alt))
        self.m.mav.mission_count_send(self.m.target_system, self.m.target_component, len(items), 0)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            msg = self.m.recv_match(type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
                                    blocking=True, timeout=0.05)
            self.service()
            if msg is None:
                continue
            if msg.get_type() == "MISSION_ACK":
                print(f"mission upload: {M.enums['MAV_MISSION_RESULT'][msg.type].name}")
                return
            cmd, lat, lon, alt = items[msg.seq]
            self.m.mav.mission_item_int_send(
                self.m.target_system, self.m.target_component, msg.seq,
                M.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, cmd, 0, 1, 0, 0, 0, math.nan,
                int(lat * 1e7), int(lon * 1e7), alt, 0)
        raise TimeoutError("mission upload")

    def set_auto(self, sub: str) -> None:
        self.command(M.MAV_CMD_DO_SET_MODE, M.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, PX4_MAIN_AUTO, PX4_SUB[sub])

    def setup_params(self) -> None:
        for k, v in {"MIS_TAKEOFF_ALT": self.a.alt, "MPC_XY_CRUISE": self.a.speed,
                     "EKF2_EV_CTRL": 0, "EKF2_GPS_CTRL": GPS_CTRL_ON}.items():
            self.param_set(k, v)

    def run(self) -> None:
        self.request_streams()
        next_req = 0.0

        def have_origin():
            nonlocal next_req
            if self.origin is None and self.now() >= next_req:
                next_req = self.now() + G.ORIGIN_RETRY_S
                self.command(M.MAV_CMD_REQUEST_MESSAGE, G.GPS_GLOBAL_ORIGIN_ID)
            return self.origin is not None

        self.pump(lambda: self.truth is not None, G.SETUP_TIMEOUT_S, "SIH truth")
        self.setup_params()
        self.pump(have_origin, G.SETUP_TIMEOUT_S, "EKF origin")
        print(f"EKF origin {self.origin}")
        self.upload_mission()
        next_arm = 0.0

        def armed():
            nonlocal next_arm
            if not self.armed and self.now() >= next_arm:
                next_arm = self.now() + G.ARM_RETRY_S
                self.command(M.MAV_CMD_COMPONENT_ARM_DISARM, 1)
            return self.armed

        self.pump(armed, G.SETUP_TIMEOUT_S, "arming")
        print(f"armed at sim {self.now():.1f}s")
        self.set_auto("TAKEOFF")
        self.pump(lambda: self.alt_rel > TAKEOFF_TOLERANCE * self.a.alt, 240, "takeoff")
        self.set_auto("MISSION")
        mission = px4_mode("MISSION")
        self.pump(lambda: self.custom_mode == mission, 30, "AUTO.MISSION")
        self.t_auto = self.now()
        self.record({"type": "COMPANION_AUTO_START"})
        print("AUTO.MISSION started (t=0)")
        last_seq = len(G.MISSION_NE) - 1
        self.pump(lambda: self.last_reached >= last_seq or self.custom_mode != mission or not self.armed,
                  G.RUN_TIMEOUT_S, "mission")
        outcome = "mission_complete" if self.last_reached >= last_seq else f"left_mission:custom_mode={self.custom_mode}"
        t_end = self.now() + G.END_HOLD_S
        self.pump(lambda: self.now() > t_end, G.END_HOLD_S + 5, "end hold")
        self.record({"type": "COMPANION_END", "first_detect": self.first, "outcome": outcome})
        print(f"{outcome} at t={self.t_mission():.1f}s, first detections {self.first}, "
              f"wall {time.monotonic() - self.t0_wall:.0f}s")
        self.log.close()


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--connect", default="udpin:0.0.0.0:14540")
    ap.add_argument("--mode", choices=["monitor", "baseline"], required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--spoof", choices=["position", "coherent", "none"], default="coherent")
    ap.add_argument("--rate", type=float, default=1.0, help="drag rate, m/s")
    ap.add_argument("--onset", type=float, default=25.0, help="s after mission start")
    ap.add_argument("--bearing", type=float, default=90.0)
    ap.add_argument("--vgeo", choices=["sim", "replay"], default="replay")
    ap.add_argument("--vgeo-table", type=Path, default=GOLDEN / "data" / "vgeo_table.json")
    ap.add_argument("--detector", choices=["chi2", "ss", "ss+vel"], default="ss+vel")
    ap.add_argument("--alt", type=float, default=150.0, help="survey altitude above home, m")
    ap.add_argument("--speed", type=float, default=10.0, help="MPC_XY_CRUISE, m/s")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    # Fixed v2 settings the shared Companion reads.
    a.gps, a.extnav, a.stamp, a.vio_to_ap, a.param_noise = "inject", "reference", "sim", False, False
    return a


def main(argv=None) -> int:
    a = parse(argv)
    a.log.parent.mkdir(parents=True, exist_ok=True)
    PX4Companion(a).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
