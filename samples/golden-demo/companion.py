#!/usr/bin/env python3
"""Golden demo companion: flies an ArduCopter SITL AUTO mission, spoofs its GPS, streams
visual-geolocation fixes as VISION_POSITION_ESTIMATE, runs integrity monitors on GNSS against
a VIO + visual-geoloc reference, and on alarm switches EKF3 to source set 2 (ExternalNav).
Every MAVLink message it reads is logged to JSONL.

v1 (defaults): SITL GPS dragged with SIM_GPS_GLITCH_X/Y, simulated visual geoloc, navapp
chi-square detector.
    python companion.py --connect tcp:127.0.0.1:15766 --mode monitor  --log runs/monitor.raw.jsonl

v2: GPS injected by this process as GPS_INPUT (GPS1_TYPE=14, inject.parm), position-only or
coherent (position + velocity) drag, visual geoloc from real matching (replay table or live),
solution-separation FDE + protection level, VIO velocity also sent to the autopilot.
    python companion.py --mode monitor --gps inject --spoof coherent --rate 1 \
        --vgeo replay --detector ss+vel --alt 150 --vio-to-ap --log runs/x.raw.jsonl

baseline runs the same monitors in shadow mode: it logs verdicts but never acts.
Clock: autopilot time_boot_ms (sim time), so SITL --speedup > 1 works.
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

from ss_fde import SolutionSeparation, VelocityConsistency  # noqa: E402
import vgeo_replay  # noqa: E402

# Lawnmower survey legs as (north, east) metres from home, flown at WPNAV_SPEED (golden.parm).
# The drag is east, so it is cross-track on the two long legs.
MISSION_NE = [(400.0, 0.0), (400.0, 150.0), (0.0, 150.0)]

SPOOF_MAX_M = 150.0
SPOOF_UPDATE_S = 0.5
EARTH_R_M = 6371008.8         # SITL glitch offsets are plain lat/lon degrees

VGEO_SIM_HZ = 5.0
VGEO_REPLAY_HZ = 1.0
VGEO_SIGMA_M = 1.5            # simulated visual-geoloc noise (truth + Gaussian)
# Real matches carry a spatially correlated ~3-5 m east bias (2019 vs 2023 NAIP registration,
# data/vgeo_table.json: median 3.3 m, p90 5.6 m, max 9.9 m). 5 m white gave pre-onset false
# alarms in test flights; 7 m overbounds it at the cost of slower detection.
VGEO_SIGMA_ASSUMED_M = {"sim": 2.5, "replay": 7.0, "live": 7.0}
VIO_SIGMA_MPS = 0.1
VIO_BIAS_EN_MPS = (0.05, -0.03)
VIO_HZ = 5.0
GNSS_SIGMA_ASSUMED_M = 2.0
GNSS_VEL_SIGMA_ASSUMED_MPS = 0.15
MONITOR_PERIOD_S = 1.0
FIX_FRESH_S = 1.5

# Injected GNSS (--gps inject): white + first-order Gauss-Markov per axis, white velocity noise.
GPS_INPUT_HZ = 10.0           # AP_GPS wants an average frame gap < 215 ms; 5 Hz has no margin under load
GNSS_WHITE_M = 0.5
GNSS_GM_SIGMA_M = 1.0
GNSS_GM_TAU_S = 30.0
GNSS_VEL_WHITE_MPS = 0.1
GPS_WEEK = 2350               # arbitrary non-zero GPS week; AP_GPS_MAV needs one for jitter correction
GPS_WEEK_MS0 = 100_000

EKF_SOURCE_SET_EXTNAV = 2
MAV_CMD_SET_EKF_SOURCE_SET = 42007
GPS_GLOBAL_ORIGIN_ID = 49
END_HOLD_S = 5.0
ARM_RETRY_S = 2.0
ORIGIN_RETRY_S = 2.0
SETUP_TIMEOUT_S = 180.0
RUN_TIMEOUT_S = 400.0
WALL_TIMEOUT_S = 900.0
CONNECT_RETRIES = 60

STREAMS_HZ = {
    "GPS_RAW_INT": 5, "GLOBAL_POSITION_INT": 10, "EKF_STATUS_REPORT": 2, "SIMSTATE": 20,
    "SIM_STATE": 20, "RAW_IMU": 10, "LOCAL_POSITION_NED": 5, "MISSION_CURRENT": 1,
    "VFR_HUD": 2, "ATTITUDE": 20,
}
LOGGED = (set(STREAMS_HZ) - {"ATTITUDE"}) | {"STATUSTEXT", "COMMAND_ACK", "HEARTBEAT",
                                             "MISSION_ITEM_REACHED", "GPS_GLOBAL_ORIGIN",
                                             "HOME_POSITION", "PARAM_VALUE"}


def offset_deg(north_m: float, east_m: float, lat_deg: float) -> tuple[float, float]:
    dlat = math.degrees(north_m / EARTH_R_M)
    dlon = math.degrees(east_m / (EARTH_R_M * math.cos(math.radians(lat_deg))))
    return dlat, dlon


class Spoof:
    def __init__(self, kind: str, onset_s: float, rate_mps: float, bearing_deg: float):
        self.kind, self.onset, self.rate = kind, onset_s, rate_mps
        b = math.radians(bearing_deg)
        self.u = (math.sin(b), math.cos(b))       # east, north unit vector

    def offset_m(self, t: float | None) -> float:
        if self.kind == "none" or t is None or t < self.onset:
            return 0.0
        return min(self.rate * (t - self.onset), SPOOF_MAX_M)

    def offset_en(self, t):
        d = self.offset_m(t)
        return d * self.u[0], d * self.u[1]

    def vel_en(self, t):
        """Velocity the spoofer adds: only a coherent drag moves velocity with position."""
        if self.kind != "coherent" or self.offset_m(t) <= 0.0 or self.offset_m(t) >= SPOOF_MAX_M:
            return 0.0, 0.0
        return self.rate * self.u[0], self.rate * self.u[1]


class Companion:
    def __init__(self, a):
        self.a = a
        self.mode = a.mode
        self.rng = random.Random(a.seed)
        self.log = a.log.open("w")
        self.t0_wall = time.monotonic()
        self.sim_s = 0.0
        self.spoof = Spoof(a.spoof, a.onset, a.rate, a.bearing)
        self.m = mavutil.mavlink_connection(a.connect, source_system=255, source_component=191,
                                            retries=CONNECT_RETRIES)
        self.m.wait_heartbeat()
        self.origin = None          # (lat, lon, alt) of the EKF origin
        self.truth = None           # (lat, lon)
        self.truth_sim_s = None
        self.truth_alt = None
        self.truth_vel = None       # (east, north) m/s
        self.truth_vd = 0.0
        self.truth_yaw = 0.0
        self.gps = None             # (lat, lon) as received by the autopilot (GPS_RAW_INT)
        self.gps_vel = None         # (east, north) from GPS_RAW_INT vel/cog
        self.gps_new = False
        self.armed = False
        self.custom_mode = None
        self.alt_rel = 0.0
        self.t_auto = None
        self.last_reached = -1
        self.next_vgeo = self.next_spoof = self.next_monitor = self.next_gps = self.next_vio = self.next_ref = 0.0
        self.last_vgeo = None       # (e, n) last fix sent
        self.vgeo_new = None        # (e, n, sim_s) fix not yet seen by the monitor
        self.gm = [0.0, 0.0]
        self.prev_vio = None
        self.vio_hist: list[tuple[float, float, float]] = []
        self.filter = DeadReckoningFilter()
        self.chi2 = ChiSquareMonitor()
        self.ss = None
        self.vel = VelocityConsistency(math.hypot(GNSS_VEL_SIGMA_ASSUMED_MPS, VIO_SIGMA_MPS))
        self.vgeo_r = VGEO_SIGMA_ASSUMED_M[a.vgeo]
        self.acted = False
        self.first = {}
        self.table = vgeo_replay.load(a.vgeo_table) if a.vgeo == "replay" else None
        self.live = None
        if a.vgeo == "live":
            import vgeo_real  # heavy: torch + LightGlue
            self.live = vgeo_real.LiveVgeo(a.seed)
        self.record({"type": "COMPANION_START", "mode": a.mode, "seed": a.seed,
                     "spoof": {"kind": a.spoof, "onset_s": a.onset, "rate_mps": a.rate,
                               "bearing_deg": a.bearing, "max_m": SPOOF_MAX_M},
                     "gps": a.gps, "detector": a.detector, "extnav": a.extnav, "stamp": a.stamp, "vio_to_ap": a.vio_to_ap,
                     "vgeo": {"mode": a.vgeo, "hz": self.vgeo_hz(), "sigma_m": VGEO_SIGMA_M,
                              "sigma_assumed_m": self.vgeo_r,
                              "table": str(a.vgeo_table) if self.table else None},
                     "vio": {"sigma_mps": VIO_SIGMA_MPS, "bias_en_mps": VIO_BIAS_EN_MPS},
                     "gnss_inject": {"white_m": GNSS_WHITE_M, "gm_sigma_m": GNSS_GM_SIGMA_M,
                                     "gm_tau_s": GNSS_GM_TAU_S, "vel_white_mps": GNSS_VEL_WHITE_MPS},
                     "mission_ne": MISSION_NE, "takeoff_alt_m": a.alt})

    def vgeo_hz(self):
        return {"sim": VGEO_SIM_HZ, "replay": VGEO_REPLAY_HZ, "live": None}[self.a.vgeo]

    def now(self) -> float:
        return self.sim_s

    def t_mission(self) -> float | None:
        return None if self.t_auto is None else self.now() - self.t_auto

    def record(self, d: dict) -> None:
        d = {"t_host": round(time.monotonic() - self.t0_wall, 3), "t_sim": round(self.sim_s, 3),
             "t": self.t_mission(), **d}
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
        wall_deadline = time.monotonic() + WALL_TIMEOUT_S
        while not until():
            if self.now() > deadline or time.monotonic() > wall_deadline:
                raise TimeoutError(what)
            msg = self.m.recv_match(blocking=True, timeout=0.02)
            if msg is not None:
                self.handle(msg)
            self.service()

    def handle(self, msg) -> None:
        kind = msg.get_type()
        if kind == "BAD_DATA":
            return
        tb = getattr(msg, "time_boot_ms", None)
        if tb is not None and msg.get_srcComponent() == 1:
            self.sim_s = max(self.sim_s, tb * 1e-3)
        if kind in LOGGED:
            self.record(msg.to_dict() | {"type": kind})
        if kind == "SIMSTATE":
            self.truth = (msg.lat * 1e-7, msg.lng * 1e-7)
            self.truth_sim_s = self.sim_s
            self.truth_yaw = msg.yaw
        elif kind == "SIM_STATE":
            self.truth_alt = msg.alt
            self.truth_vel = (msg.ve, msg.vn)
            self.truth_vd = msg.vd
        elif kind == "GPS_RAW_INT" and msg.fix_type >= 3:
            self.gps = (msg.lat * 1e-7, msg.lon * 1e-7)
            v, c = msg.vel * 0.01, math.radians(msg.cog * 0.01)
            self.gps_vel = (v * math.sin(c), v * math.cos(c)) if msg.vel != 65535 else None
            self.gps_new = True
        elif kind == "GPS_GLOBAL_ORIGIN" and self.origin is None:
            self.origin = (msg.latitude * 1e-7, msg.longitude * 1e-7, msg.altitude * 1e-3)
        elif kind == "HEARTBEAT" and msg.get_srcComponent() == 1:
            self.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            self.custom_mode = msg.custom_mode
        elif kind == "GLOBAL_POSITION_INT":
            self.alt_rel = msg.relative_alt * 1e-3
        elif kind == "MISSION_ITEM_REACHED":
            self.last_reached = max(self.last_reached, msg.seq)
        elif kind == "STATUSTEXT" and not self.a.quiet:
            print(f"  STATUSTEXT: {msg.text}")

    def service(self) -> None:
        now = self.now()
        if self.a.gps == "inject" and self.truth and self.truth_vel and now >= self.next_gps:
            self.next_gps = now + 1.0 / GPS_INPUT_HZ
            self.send_gps_input()
        if self.origin and self.truth and self.truth_vel and self.truth_alt is not None:
            if self.a.vio_to_ap and now >= self.next_vio:
                self.next_vio = now + 1.0 / VIO_HZ
                self.send_vio()
            self.service_vgeo(now)
            if self.reference_ready() and now >= self.next_ref:
                self.next_ref = now + 1.0 / VGEO_SIM_HZ
                self.send_reference(now)
        t = self.t_mission()
        if t is None:
            return
        if self.a.param_noise and self.a.gps == "inject" and t >= self.a.onset and now >= self.next_spoof:
            self.next_spoof = now + SPOOF_UPDATE_S
            self.m.param_set_send("SIM_GPS_GLITCH_X", 0.0)
            self.m.param_set_send("SIM_GPS_GLITCH_Y", 0.0)
        if self.a.gps == "sitl" and self.a.spoof != "none" and t >= self.a.onset and now >= self.next_spoof:
            self.next_spoof = now + SPOOF_UPDATE_S
            self.update_glitch(t)
        if now >= self.next_monitor and self.truth_vel and self.gps and self.origin:
            self.next_monitor = now + MONITOR_PERIOD_S
            self.monitor_step(t)

    def stamp_us(self, sim_s: float) -> int:
        return int(time.time() * 1e6) if self.a.stamp == "host" else int(sim_s * 1e6)

    # --- simulated sensors and the attack ---------------------------------------------
    def vio_en(self) -> tuple[float, float]:
        ve, vn = self.truth_vel
        return (ve + VIO_BIAS_EN_MPS[0] + self.rng.gauss(0, VIO_SIGMA_MPS),
                vn + VIO_BIAS_EN_MPS[1] + self.rng.gauss(0, VIO_SIGMA_MPS))

    def send_vio(self) -> None:
        ve, vn = self.vio_en()
        self.vio_hist.append((self.now(), ve, vn))
        del self.vio_hist[:-200]
        self.m.mav.vision_speed_estimate_send(self.stamp_us(self.truth_sim_s or self.now()), vn, ve,
                                              self.truth_vd, [math.nan] + [0.0] * 8, 0)

    def send_gps_input(self) -> None:
        """GNSS as the autopilot sees it: truth + noise + spoof, timestamped in sim time."""
        t = self.t_mission()
        dt = 1.0 / GPS_INPUT_HZ
        phi = math.exp(-dt / GNSS_GM_TAU_S)
        self.gm = [g * phi + self.rng.gauss(0, GNSS_GM_SIGMA_M * math.sqrt(1 - phi * phi)) for g in self.gm]
        oe, on = self.spoof.offset_en(t)
        ne = oe + self.gm[0] + self.rng.gauss(0, GNSS_WHITE_M)
        nn = on + self.gm[1] + self.rng.gauss(0, GNSS_WHITE_M)
        dlat, dlon = offset_deg(nn, ne, self.truth[0])
        sve, svn = self.spoof.vel_en(t)
        ve = self.truth_vel[0] + sve + self.rng.gauss(0, GNSS_VEL_WHITE_MPS)
        vn = self.truth_vel[1] + svn + self.rng.gauss(0, GNSS_VEL_WHITE_MPS)
        sim_ms = int((self.truth_sim_s or self.now()) * 1000)
        self.m.mav.gps_input_send(
            self.stamp_us(sim_ms / 1000), 0, 0, GPS_WEEK_MS0 + sim_ms, GPS_WEEK, 3,
            int((self.truth[0] + dlat) * 1e7), int((self.truth[1] + dlon) * 1e7),
            self.truth_alt + self.rng.gauss(0, 1.0), 0.8, 1.2, vn, ve, self.truth_vd,
            0.3, 1.5, 2.5, 14, 0)
        if t is not None and t >= self.a.onset and self.a.spoof != "none":
            self.record({"type": "COMPANION_SPOOF", "offset_m": self.spoof.offset_m(t),
                         "vel_add_en": [sve, svn], "kind": self.a.spoof})

    def update_glitch(self, t: float) -> None:
        off = self.spoof.offset_m(t)
        oe, on = self.spoof.offset_en(t)
        dlat, dlon = offset_deg(on, oe, self.truth[0])
        self.m.param_set_send("SIM_GPS_GLITCH_X", dlat)
        self.m.param_set_send("SIM_GPS_GLITCH_Y", dlon)
        self.record({"type": "COMPANION_SPOOF", "offset_m": off, "glitch_x_deg": dlat,
                     "glitch_y_deg": dlon, "kind": "position"})

    def truth_en(self):
        lat0, lon0, _ = self.origin
        return geodetic_to_enu(*self.truth, lat0, lon0)

    def service_vgeo(self, now: float) -> None:
        mode = self.a.vgeo
        if mode == "live":
            self.service_live(now)
            return
        if now < self.next_vgeo:
            return
        self.next_vgeo = now + 1.0 / self.vgeo_hz()
        e, n = self.truth_en()
        if mode == "sim":
            fix = (e + self.rng.gauss(0.0, VGEO_SIGMA_M), n + self.rng.gauss(0.0, VGEO_SIGMA_M))
            info = {}
        else:
            fix, info = vgeo_replay.lookup(self.table, self.origin, e, n, self.rng)
        if fix is None:
            self.record({"type": "COMPANION_VGEO_FAIL", **info})
            return
        self.send_vgeo(fix, self.truth_sim_s or now, info)

    def service_live(self, now: float) -> None:
        for r in self.live.take():
            if r["lat"] is None:
                self.record({"type": "COMPANION_VGEO_FAIL", "inliers": r["inliers"], "t_capture": r["t_capture"],
                             "latency_s": round(now - r["t_capture"], 2)})
                continue
            lat0, lon0, _ = self.origin
            e, n = geodetic_to_enu(r["lat"], r["lon"], lat0, lon0)
            # The match took seconds: carry the fix forward to now with VIO, then stamp it now.
            de = sum(ve * (1.0 / VIO_HZ) for ts, ve, _ in self.vio_hist if ts > r["t_capture"])
            dn = sum(vn * (1.0 / VIO_HZ) for ts, _, vn in self.vio_hist if ts > r["t_capture"])
            self.send_vgeo((e + de, n + dn), now, {"inliers": r["inliers"], "latency_s": round(now - r["t_capture"], 2),
                                                   "match_s": r["t_s"]})
        if self.truth and (self.filter.x is not None or self.gps):
            lat0, lon0, _ = self.origin
            # Prior: the GNSS-free reference once it exists, else the (pre-attack) GNSS fix.
            prior = (enu_to_geodetic(self.filter.x.east, self.filter.x.north, lat0, lon0)
                     if self.filter.x is not None else self.gps)
            self.live.submit({"lat": self.truth[0], "lon": self.truth[1], "yaw_deg": math.degrees(self.truth_yaw),
                              "agl_m": self.alt_rel, "prior": prior, "t_capture": now})

    def extnav_send(self, e, n, sim_s, sigma_m=None) -> None:
        lat0, lon0, alt0 = self.origin
        cov = [math.nan] + [0.0] * 20
        if sigma_m is not None:
            # GCS_Common: posErr = cbrt(c0^2 + c6^2 + c11^2); pick c so that posErr == sigma_m.
            c = math.sqrt(sigma_m ** 3 / 3.0)
            cov[0] = cov[6] = cov[11] = c
        self.m.mav.vision_position_estimate_send(self.stamp_us(sim_s), n, e, -(self.truth_alt - alt0),
                                                 0.0, 0.0, self.truth_yaw, cov, 0)

    def reference_ready(self) -> bool:
        return self.a.extnav == "reference" and self.filter.x is not None and self.prev_vio is not None

    def send_reference(self, now: float) -> None:
        """ExternalNav = the GNSS-free reference (VIO dead reckoning + visual geoloc), carried
        forward with the latest VIO between 1 Hz monitor epochs, so fix gaps do not starve EKF3."""
        dt = max(0.0, self.t_mission() - self.filter.t)
        e = self.filter.x.east + self.prev_vio[0] * dt
        n = self.filter.x.north + self.prev_vio[1] * dt
        sigma = math.sqrt(self.filter.P + (VIO_SIGMA_MPS * dt) ** 2)
        self.extnav_send(e, n, now, max(sigma, 1.0))

    def send_vgeo(self, fix_en, sim_s: float, info: dict) -> None:
        lat0, lon0, _ = self.origin
        e, n = fix_en
        if not self.reference_ready():
            self.extnav_send(e, n, sim_s, None if self.a.vgeo == "sim" else self.vgeo_r)
        self.last_vgeo = Vec2(e, n)
        self.vgeo_new = (e, n, sim_s)
        lat, lon = enu_to_geodetic(e, n, lat0, lon0)
        self.record({"type": "COMPANION_VGEO", "lat": lat, "lon": lon, "east": e, "north": n, **info})

    # --- monitors -----------------------------------------------------------------------
    def monitor_step(self, t: float) -> None:
        lat0, lon0, _ = self.origin
        vio = Vec2(*self.vio_en())
        gnss = Vec2(*geodetic_to_enu(*self.gps, lat0, lon0))
        new_vgeo = self.vgeo_new if self.vgeo_new and self.now() - self.vgeo_new[2] <= FIX_FRESH_S else None
        self.vgeo_new = None
        if self.ss is None:
            # Start on the current GNSS fix, before any attack: the trusted-at-start assumption.
            self.ss = SolutionSeparation(gnss.east, gnss.north, GNSS_SIGMA_ASSUMED_M,
                                         {"gnss": GNSS_SIGMA_ASSUMED_M, "vgeo": self.vgeo_r})
            self.filter.predict(Epoch(t, None, VIO_SIGMA_MPS, gnss, GNSS_SIGMA_ASSUMED_M, "gnss"))

        # v1 detector: VIO dead reckoning + visual geoloc reference, GNSS tested and never fused.
        vg = Vec2(new_vgeo[0], new_vgeo[1]) if new_vgeo else None
        if self.a.vgeo == "sim":
            vg = self.last_vgeo     # v1 behaviour: latest sim fix every epoch
        ep_vgeo = Epoch(t, vio, VIO_SIGMA_MPS, vg, self.vgeo_r, "vgeo")
        self.filter.predict(ep_vgeo)
        self.filter.update(ep_vgeo)
        ep_gnss = Epoch(t, None, VIO_SIGMA_MPS, gnss, GNSS_SIGMA_ASSUMED_M, "gnss")
        verdict = self.chi2.check(ep_gnss, self.filter.innovation(ep_gnss))
        st = self.filter.state(t)
        lat, lon = enu_to_geodetic(st.position.east, st.position.north, lat0, lon0)
        self.record({"type": "COMPANION_MONITOR", "health": verdict.health.value,
                     "alarm": verdict.alarm, "statistic": verdict.statistic,
                     "threshold": verdict.threshold, "reason": verdict.reason,
                     "lat": lat, "lon": lon, "sigma_h": st.sigma_h,
                     "sources": list(st.sources_used)})

        ss = self.ss.step(t, (vio.east, vio.north), VIO_SIGMA_MPS * 1.5,
                          {"gnss": (gnss.east, gnss.north) if self.gps_new else None,
                           "vgeo": (new_vgeo[0], new_vgeo[1]) if new_vgeo else None})
        self.gps_new = False
        slat, slon = enu_to_geodetic(ss["e"], ss["n"], lat0, lon0)
        self.record({"type": "COMPANION_SS", **ss, "lat": slat, "lon": slon})
        accel = 0.0
        if self.prev_vio is not None:
            accel = math.hypot(vio.east - self.prev_vio[0], vio.north - self.prev_vio[1]) / MONITOR_PERIOD_S
        self.prev_vio = (vio.east, vio.north)
        vel = self.vel.check(self.gps_vel, (vio.east, vio.north), accel)
        if vel:
            self.record({"type": "COMPANION_VEL", **vel})

        fired = {"chi2": verdict.alarm and verdict.health == Health.EXCLUDED,
                 "ss": "gnss" in ss["excluded"],
                 "vel": bool(vel and vel["alarm"])}
        for k, v in fired.items():
            if v and k not in self.first:
                self.first[k] = t
                self.record({"type": "COMPANION_DETECT", "detector": k, "events": ss["events"]})
        act = {"chi2": fired["chi2"], "ss": fired["ss"], "ss+vel": fired["ss"] or fired["vel"]}[self.a.detector]
        if self.acted and self.mode == "monitor" and "readmit:gnss" in ss["events"] and "gnss" not in ss["excluded"]:
            # Probation cleared GNSS (the other source was blamed): go back to source set 1.
            self.acted = False
            self.command(MAV_CMD_SET_EKF_SOURCE_SET, 1)
            print(f"t={t:.1f}s GNSS readmitted by SS probation => EKF source set 1")
            self.record({"type": "COMPANION_ACTION", "action": "revert_source_set", "source_set": 1,
                         "reason": "readmit:gnss"})
            return
        if act and not self.acted:
            self.acted = True
            why = ",".join(k for k, v in fired.items() if v)
            if self.mode == "monitor":
                self.command(MAV_CMD_SET_EKF_SOURCE_SET, EKF_SOURCE_SET_EXTNAV)
                print(f"t={t:.1f}s ALARM ({why}) => EKF source set {EKF_SOURCE_SET_EXTNAV}")
                self.record({"type": "COMPANION_ACTION", "action": "set_ekf_source_set",
                             "source_set": EKF_SOURCE_SET_EXTNAV, "reason": why})
            else:
                print(f"t={t:.1f}s ALARM ({why}) - shadow mode, no action")
                self.record({"type": "COMPANION_ACTION", "action": "none_shadow_mode", "reason": why})

    # --- flight -------------------------------------------------------------------------
    def upload_mission(self) -> None:
        lat0, lon0, _ = self.origin
        alt = self.a.alt
        items = [(mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, lat0, lon0, 0.0),
                 (mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, lat0, lon0, alt)]
        for n, e in MISSION_NE:
            lat, lon = enu_to_geodetic(e, n, lat0, lon0)
            items.append((mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, lat, lon, alt))
        self.m.mav.mission_count_send(self.m.target_system, self.m.target_component, len(items), 0)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            msg = self.m.recv_match(type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
                                    blocking=True, timeout=0.05)
            self.service()
            if msg is None:
                continue
            if msg.get_type() == "MISSION_ACK":
                print(f"mission upload: {mavutil.mavlink.enums['MAV_MISSION_RESULT'][msg.type].name}")
                return
            cmd, lat, lon, alt_i = items[msg.seq]
            self.m.mav.mission_item_int_send(
                self.m.target_system, self.m.target_component, msg.seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, cmd, 0, 1, 0, 0, 0, 0,
                int(lat * 1e7), int(lon * 1e7), alt_i, 0)
        raise TimeoutError("mission upload")

    def set_mode(self, name: str) -> None:
        self.m.set_mode(self.m.mode_mapping()[name])

    def run(self) -> None:
        self.request_streams()
        next_req = 0.0

        def have_origin():
            nonlocal next_req
            if self.origin is None and self.now() >= next_req:
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
            if not self.armed and self.now() >= next_arm:
                next_arm = self.now() + ARM_RETRY_S
                self.set_mode("GUIDED")
                self.command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)
            return self.armed

        self.pump(armed, SETUP_TIMEOUT_S, "arming")
        print(f"armed at sim {self.now():.1f}s")
        self.command(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, self.a.alt)
        self.pump(lambda: self.alt_rel > 0.9 * self.a.alt, 180, "takeoff")
        self.set_mode("AUTO")
        self.t_auto = self.now()
        self.record({"type": "COMPANION_AUTO_START"})
        print("AUTO started (t=0)")
        last_seq = len(MISSION_NE) + 1
        modes = self.m.mode_mapping()
        auto = modes["AUTO"]
        self.pump(lambda: self.custom_mode == auto, 30, "AUTO mode")
        # Ends on the last waypoint, or when the autopilot leaves AUTO by itself (EKF failsafe => LAND).
        self.pump(lambda: self.last_reached >= last_seq or self.custom_mode != auto or not self.armed,
                  RUN_TIMEOUT_S, "mission")
        outcome = "mission_complete" if self.last_reached >= last_seq else \
            f"left_auto:{ {v: k for k, v in modes.items()}.get(self.custom_mode, self.custom_mode) }"
        t_end = self.now() + END_HOLD_S
        self.pump(lambda: self.now() > t_end, END_HOLD_S + 5, "end hold")
        self.record({"type": "COMPANION_END", "first_detect": self.first, "outcome": outcome})
        print(f"{outcome} at t={self.t_mission():.1f}s, first detections {self.first}, "
              f"wall {time.monotonic() - self.t0_wall:.0f}s")
        self.log.close()


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--connect", default="tcp:127.0.0.1:15766")
    ap.add_argument("--mode", choices=["monitor", "baseline"], required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--gps", choices=["sitl", "inject"], default="sitl",
                    help="sitl: SITL GPS + SIM_GPS_GLITCH (v1); inject: GPS_INPUT from here, needs inject.parm")
    ap.add_argument("--spoof", choices=["position", "coherent", "none"], default="position")
    ap.add_argument("--rate", type=float, default=1.0, help="drag rate, m/s")
    ap.add_argument("--onset", type=float, default=25.0, help="s after AUTO start")
    ap.add_argument("--bearing", type=float, default=90.0, help="direction the GPS is dragged, deg")
    ap.add_argument("--vgeo", choices=["sim", "replay", "live"], default="sim")
    ap.add_argument("--vgeo-table", type=Path, default=HERE / "data" / "vgeo_table.json")
    ap.add_argument("--detector", choices=["chi2", "ss", "ss+vel"], default="chi2")
    ap.add_argument("--extnav", choices=["fixes", "reference"], default="fixes",
                    help="what goes to the autopilot as VISION_POSITION_ESTIMATE: raw visual-geoloc fixes (v1) "
                         "or the companion's GNSS-free VIO + visual-geoloc reference at 5 Hz")
    ap.add_argument("--alt", type=float, default=30.0, help="survey altitude above home, m")
    ap.add_argument("--vio-to-ap", action="store_true", help="also send VIO as VISION_SPEED_ESTIMATE")
    ap.add_argument("--stamp", choices=["sim", "host"], default="sim",
                    help="timestamps of injected messages: sim time (default) or host wall clock (v1)")
    ap.add_argument("--param-noise", action="store_true",
                    help="lane-switch experiment: with --gps inject, still send the v1 PARAM_SETs (zero glitch)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.spoof == "coherent" and a.gps != "inject":
        ap.error("--spoof coherent needs --gps inject (SIM_GPS_GLITCH only moves position)")
    return a


def main(argv=None) -> int:
    a = parse(argv)
    a.log.parent.mkdir(parents=True, exist_ok=True)
    Companion(a).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
