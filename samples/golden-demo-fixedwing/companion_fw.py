#!/usr/bin/env python3
"""Fixed-wing companion: flies an ArduPlane SITL AUTO route (~27.6 km at 300 m), injects GPS as
GPS_INPUT with a coherent drag, runs the golden-demo monitors (solution separation + GNSS-vs-
reference velocity test from samples/golden-demo/ss_fde.py) and on alarm switches EKF3 source set.

Scenarios (--scenario):
  baseline  same monitors in shadow mode, no action (day fix model for the monitor)
  day       VO velocity + visual-geoloc fixes (VPAIR-measured model); alarm => source set 2,
            ExternalNav = this process's GNSS-free reference at 5 Hz
  night     airspeed + compass velocity + thermal-geoloc fixes (Thermal-UAV-measured model);
            alarm => source set 2 as above
  dr        airspeed + compass velocity, no fixes; alarm => source set 3 (no position, no
            velocity source: EKF3 dead reckons on airspeed, sideslip, compass, its wind estimate)

    python companion_fw.py --connect tcp:127.0.0.1:15841 --scenario day --log runs/day.raw.jsonl
Clock: autopilot time_boot_ms (sim time), so SITL --speedup works.
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
sys.path.insert(0, str(HERE.parent / "golden-demo"))
sys.path.insert(0, str(HERE.parents[1] / "templates" / "project-repo" / "src"))

from navapp.filter import DeadReckoningFilter  # noqa: E402
from navapp.geo import enu_to_geodetic, geodetic_to_enu  # noqa: E402
from navapp.interfaces import Epoch, Vec2  # noqa: E402
from ss_fde import SolutionSeparation, VelocityConsistency  # noqa: E402

import fw_core  # noqa: E402

GPS_INPUT_HZ = 10.0
GNSS_WHITE_M = 0.5
GNSS_GM_SIGMA_M = 1.0
GNSS_GM_TAU_S = 30.0
GNSS_VEL_WHITE_MPS = 0.1
GNSS_SIGMA_ASSUMED_M = 2.0
GPS_WEEK = 2350
GPS_WEEK_MS0 = 100_000

# Reference velocity error, applied to truth (VO) or to the AHRS heading (airspeed): constant
# heading error and scale error, plus white noise. +2 deg is the "realistic AHRS heading error"
# case of samples/e2e-visual-nav-vpair; 3 % is the order of its fitted VO scale sigma (3.3 %).
HEADING_ERR_DEG = 2.0
VO_SCALE_ERR = 0.03
VO_WHITE_MPS = 0.2
COMPASS_WHITE_DEG = 0.5
# Velocity-test sigma per reference after calibration; set from no-spoof flights (README,
# "Tuning"), not from a spec.
VEL_TEST_SIGMA = {"vo": 0.35, "air": 0.6}
REF_SIGMA_V = {"vo": 0.3, "air": 0.8}
FIX_SIGMA_ASSUMED_M = 4.0           # overbounds both measured models (p95 5.5 m radial day)
FIX_PERIOD_S = 2.0                  # ~44 m at 22 m/s, VPAIR's frame spacing was 45 m
EXTNAV_HZ = 5.0
MONITOR_PERIOD_S = 1.0
CAL_MAX_ACCEL = 2.0                 # m/s^2: GPS_RAW_INT velocity lags in turns, calibrate on straights

MAV_CMD_SET_EKF_SOURCE_SET = 42007
GPS_GLOBAL_ORIGIN_ID = 49
SOURCE_SET = {"day": 2, "night": 2, "dr": 3}
END_LOITER_S = 120.0
SETUP_TIMEOUT_S = 240.0
RUN_TIMEOUT_S = 3000.0
WALL_TIMEOUT_S = 1800.0

STREAMS_HZ = {"GPS_RAW_INT": 5, "GLOBAL_POSITION_INT": 5, "EKF_STATUS_REPORT": 1, "SIMSTATE": 10,
              "SIM_STATE": 10, "VFR_HUD": 5, "ATTITUDE": 10, "MISSION_CURRENT": 1, "WIND": 1}
LOGGED = {"GPS_RAW_INT", "GLOBAL_POSITION_INT", "EKF_STATUS_REPORT", "SIMSTATE", "VFR_HUD",
          "MISSION_CURRENT", "WIND", "STATUSTEXT", "COMMAND_ACK", "MISSION_ITEM_REACHED",
          "GPS_GLOBAL_ORIGIN", "HEARTBEAT"}
LOG_DECIMATE = {"SIMSTATE": 2}      # truth at 5 Hz in the log is plenty for a 25 km route


class Companion:
    def __init__(self, a):
        self.a = a
        self.scn = a.scenario
        self.acts = self.scn != "baseline"
        self.ref_kind = a.ref if a.ref != "auto" else ("vo" if self.scn in ("day", "baseline") else "air")
        self.fix_name = {"day": "day", "baseline": "day", "night": "night", "dr": None}[self.scn]
        self.rng = random.Random(a.seed)
        models = fw_core.load_fix_models()
        self.fixes = fw_core.FixModel.from_models(models, self.fix_name, random.Random(a.seed + 1000)) \
            if self.fix_name else None
        self.spoof = fw_core.Spoof(a.spoof, a.onset, a.rate, a.bearing)
        self.cal = fw_core.VelocityCalibration(with_bias=self.ref_kind == "air")
        self.vel = VelocityConsistency(VEL_TEST_SIGMA[self.ref_kind])
        self.ref = DeadReckoningFilter()
        self.ss = None
        self.log = a.log.open("w")
        self.t0_wall = time.monotonic()
        self.sim_s = 0.0
        self.counts = {}
        self.m = mavutil.mavlink_connection(a.connect, source_system=255, source_component=191, retries=60)
        self.m.wait_heartbeat()
        self.origin = self.truth = self.truth_vel = self.truth_alt = None
        self.truth_vd = 0.0
        self.truth_sim_s = None
        self.truth_yaw = None
        self.yaw = None
        self.airspeed = None
        self.gnss_ll = self.gps_vel = None
        self.gps_new = False
        self.armed = False
        self.custom_mode = None
        self.alt_rel = 0.0
        self.t_auto = None
        self.last_reached = -1
        self.gm = [0.0, 0.0]
        self.next_fix = self.next_ext = self.next_mon = 0.0
        self.last_spoof_rec = None
        self.prev_v = None
        self.disp = [0.0, 0.0]      # reference displacement since the last monitor epoch
        self.acc_t = None
        self.last_raw = None
        self.ref_t = None
        self.acted = False
        self.first = {}
        self.record({"type": "COMPANION_START", "scenario": self.scn, "seed": a.seed, "ref_kind": self.ref_kind,
                     "fix_model": self.fix_name, "fix_period_s": FIX_PERIOD_S,
                     "spoof": {"kind": a.spoof, "onset_s": a.onset, "rate_mps": a.rate, "bearing_deg": a.bearing},
                     "heading_err_deg": HEADING_ERR_DEG, "vo_scale_err": VO_SCALE_ERR,
                     "vel_test_sigma": VEL_TEST_SIGMA[self.ref_kind], "route_ne": fw_core.ROUTE_NE,
                     "cruise_alt_m": fw_core.CRUISE_ALT_M, "source_set_on_alarm": SOURCE_SET.get(self.scn)})

    # --- plumbing ---------------------------------------------------------------------------
    def now(self):
        return self.sim_s

    def t_mission(self):
        return None if self.t_auto is None else self.now() - self.t_auto

    def record(self, d):
        d = {"t_host": round(time.monotonic() - self.t0_wall, 3), "t_sim": round(self.sim_s, 3),
             "t": None if self.t_auto is None else round(self.now() - self.t_auto, 3), **d}
        self.log.write(json.dumps(d, default=str) + "\n")

    def command(self, cmd, *p):
        p = list(p) + [0.0] * (7 - len(p))
        self.m.mav.command_long_send(self.m.target_system, self.m.target_component, cmd, 0, *p)

    def request_streams(self):
        for name, hz in STREAMS_HZ.items():
            self.command(mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                         getattr(mavutil.mavlink, f"MAVLINK_MSG_ID_{name}"), 1e6 / hz)

    def pump(self, until, timeout, what):
        deadline = self.now() + timeout
        wall = time.monotonic() + WALL_TIMEOUT_S
        while not until():
            if self.now() > deadline or time.monotonic() > wall:
                raise TimeoutError(what)
            msg = self.m.recv_match(blocking=True, timeout=0.01)
            if msg is not None:
                self.handle(msg)
            self.service()

    def handle(self, msg):
        kind = msg.get_type()
        if kind == "BAD_DATA":
            return
        tb = getattr(msg, "time_boot_ms", None)
        if tb is not None and msg.get_srcComponent() == 1:
            self.sim_s = max(self.sim_s, tb * 1e-3)
        if kind in LOGGED:
            n = self.counts[kind] = self.counts.get(kind, 0) + 1
            if n % LOG_DECIMATE.get(kind, 1) == 0:
                self.record(msg.to_dict() | {"type": kind})
        if kind == "SIMSTATE":
            self.truth = (msg.lat * 1e-7, msg.lng * 1e-7)
            self.truth_sim_s = self.sim_s
            self.truth_yaw = msg.yaw
            self.on_tick()
        elif kind == "SIM_STATE":
            self.truth_alt = msg.alt
            self.truth_vel = (msg.ve, msg.vn)
            self.truth_vd = msg.vd
        elif kind == "ATTITUDE":
            self.yaw = msg.yaw
        elif kind == "VFR_HUD":
            self.airspeed = msg.airspeed
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

    def on_tick(self):
        """Every SIMSTATE (10 Hz): the reference, the injected GNSS and the monitor all use the
        same truth instant, so no message latency enters the comparisons."""
        if not self.truth_vel:
            return
        self.integrate_ref()
        self.send_gps_input()
        if self.origin and self.truth_alt is not None and self.now() >= self.next_mon:
            self.next_mon = self.now() + MONITOR_PERIOD_S - 0.05
            self.monitor_step()

    def service(self):
        now = self.now()
        if self.scn != "dr" and self.ref.x is not None and now >= self.next_ext:
            self.next_ext = now + 1.0 / EXTNAV_HZ
            self.send_extnav(now)

    # --- sensors ------------------------------------------------------------------------------
    def truth_en(self):
        return geodetic_to_enu(*self.truth, *self.origin[:2])

    def integrate_ref(self):
        """Integrate the calibrated reference velocity at the SIM_STATE rate (10 Hz): a 1 Hz
        point sample of velocity misses metres per epoch in a fixed-wing turn."""
        v = self.raw_ref_velocity()
        if v is None:
            return
        if self.acc_t is not None:
            dt = self.sim_s - self.acc_t
            vc = self.cal.correct(v)
            self.disp[0] += vc[0] * dt
            self.disp[1] += vc[1] * dt
        self.acc_t = self.sim_s
        self.last_raw = v

    def raw_ref_velocity(self):
        if self.ref_kind == "vo":
            ve, vn = fw_core.rotate_scale(self.truth_vel, HEADING_ERR_DEG, VO_SCALE_ERR)
            return ve + self.rng.gauss(0, VO_WHITE_MPS), vn + self.rng.gauss(0, VO_WHITE_MPS)
        if self.airspeed is None or self.truth_yaw is None:
            return None
        # Airspeed along the companion's own compass heading (truth yaw + bias + noise), not the
        # autopilot's ATTITUDE.yaw: EKF3 yaw leaned with the coherent velocity spoof in a test
        # flight, and the reference followed the spoof (README, "Heading source"). Wind,
        # EAS->TAS and the heading bias are left to the calibration.
        h = self.truth_yaw + math.radians(HEADING_ERR_DEG + self.rng.gauss(0, COMPASS_WHITE_DEG))
        return self.airspeed * math.sin(h), self.airspeed * math.cos(h)

    def send_gps_input(self):
        t = self.t_mission()
        dt = 1.0 / GPS_INPUT_HZ
        phi = math.exp(-dt / GNSS_GM_TAU_S)
        self.gm = [g * phi + self.rng.gauss(0, GNSS_GM_SIGMA_M * math.sqrt(1 - phi * phi)) for g in self.gm]
        oe, on = self.spoof.offset_en(t)
        ne = oe + self.gm[0] + self.rng.gauss(0, GNSS_WHITE_M)
        nn = on + self.gm[1] + self.rng.gauss(0, GNSS_WHITE_M)
        lat0 = self.truth[0]
        dlat = math.degrees(nn / 6371008.8)
        dlon = math.degrees(ne / (6371008.8 * math.cos(math.radians(lat0))))
        sve, svn = self.spoof.vel_en(t)
        ve = self.truth_vel[0] + sve + self.rng.gauss(0, GNSS_VEL_WHITE_MPS)
        vn = self.truth_vel[1] + svn + self.rng.gauss(0, GNSS_VEL_WHITE_MPS)
        lat, lon = self.truth[0] + dlat, self.truth[1] + dlon
        # The monitor reads the receiver output directly (what is injected here), not the
        # autopilot's GPS_RAW_INT echo, which arrives up to one stream period late.
        self.gnss_ll, self.gps_vel, self.gps_new = (lat, lon), (ve, vn), True
        sim_ms = int((self.truth_sim_s or self.now()) * 1000)
        self.m.mav.gps_input_send(sim_ms * 1000, 0, 0, GPS_WEEK_MS0 + sim_ms, GPS_WEEK, 3,
                                  int((self.truth[0] + dlat) * 1e7), int((self.truth[1] + dlon) * 1e7),
                                  (self.truth_alt or 0.0) + self.rng.gauss(0, 1.0), 0.8, 1.2, vn, ve,
                                  self.truth_vd, 0.3, 1.5, 2.5, 14, 0)
        if t is not None and self.spoof.offset_m(t) > 0 and int(t) != self.last_spoof_rec:
            self.last_spoof_rec = int(t)
            self.record({"type": "COMPANION_SPOOF", "offset_m": self.spoof.offset_m(t), "vel_add_en": [sve, svn]})

    def send_extnav(self, now):
        """ExternalNav = the GNSS-free reference, carried forward from the last monitor epoch."""
        dt = max(0.0, now - self.ref_t)
        e = self.ref.x.east + self.disp[0]
        n = self.ref.x.north + self.disp[1]
        sigma = max(math.sqrt(self.ref.P + (REF_SIGMA_V[self.ref_kind] * dt) ** 2), 1.0)
        c = math.sqrt(sigma ** 3 / 3.0)     # GCS_Common: posErr = cbrt(c0^2 + c6^2 + c11^2)
        cov = [math.nan] + [0.0] * 20
        cov[0] = cov[6] = cov[11] = c
        n, e = fw_core.ap_ne_from_ll(*enu_to_geodetic(e, n, *self.origin[:2]), *self.origin[:2])
        self.m.mav.vision_position_estimate_send(int(now * 1e6), n, e, -(self.truth_alt - self.origin[2]),
                                                 0.0, 0.0, self.yaw or 0.0, cov, 0)
        if self.a.extnav_vel and self.last_raw is not None:
            ve, vn = self.cal.correct(self.last_raw)
            self.m.mav.vision_speed_estimate_send(int(now * 1e6), vn, ve, self.truth_vd,
                                                  [math.nan] + [0.0] * 8, 0)

    # --- monitor ------------------------------------------------------------------------------
    def monitor_step(self):
        now = self.now()
        t = self.t_mission()
        raw = self.last_raw
        if raw is None:
            return
        gnss = geodetic_to_enu(*self.gnss_ll, *self.origin[:2])
        v_now = self.cal.correct(raw)
        fix = None
        if self.fixes and now >= self.next_fix:
            self.next_fix = now + FIX_PERIOD_S - 0.05
            fix = self.fixes.attempt(self.truth_en())
            if fix is None:
                self.record({"type": "COMPANION_FIX_FAIL"})
            else:
                lat, lon = enu_to_geodetic(fix[0], fix[1], *self.origin[:2])
                self.record({"type": "COMPANION_FIX", "east": fix[0], "north": fix[1], "lat": lat, "lon": lon})
        sig_v = REF_SIGMA_V[self.ref_kind]
        if self.ref.x is None:
            self.ref.predict(Epoch(now, None, sig_v, Vec2(*gnss), GNSS_SIGMA_ASSUMED_M, "gnss"))
            self.ref_t = now
            self.disp = [0.0, 0.0]
            return
        dt_ep = max(now - self.ref_t, 1e-3)
        v_ref = (self.disp[0] / dt_ep, self.disp[1] / dt_ep)
        self.disp = [0.0, 0.0]
        accel = math.hypot(v_now[0] - self.prev_v[0], v_now[1] - self.prev_v[1]) / dt_ep if self.prev_v else 0.0
        self.prev_v = v_now
        warmup = t is None or t < self.a.monitor_start
        ep = Epoch(now, Vec2(*v_ref), sig_v, Vec2(fix[0], fix[1]) if fix else None, FIX_SIGMA_ASSUMED_M, "vgeo")
        self.ref.predict(ep)
        self.ref.update(ep)
        if warmup:
            # Trusted warm-up (takeoff, climb, two turns): the reference follows GNSS and the
            # velocity calibration learns. From monitor_start on the reference is GNSS-free.
            self.ref.update(Epoch(now, None, sig_v, Vec2(*gnss), GNSS_SIGMA_ASSUMED_M, "gnss"))
        self.ref_t = now
        if warmup and accel < CAL_MAX_ACCEL:
            self.cal.update(raw, self.gps_vel, MONITOR_PERIOD_S)
        # Frozen from monitor start: a calibration that keeps learning from GNSS absorbs a
        # coherent drag into its bias (wind) term within ~20 s (seen in a test flight).
        self.cal.frozen = not warmup
        rec = {"type": "COMPANION_MON", "ref_sigma": math.sqrt(self.ref.P), "cal": [round(x, 4) for x in self.cal.theta],
               "v_ref": v_now, "v_gnss": self.gps_vel, "warmup": warmup}
        rec["ref_lat"], rec["ref_lon"] = enu_to_geodetic(self.ref.x.east, self.ref.x.north, *self.origin[:2])
        if warmup:
            self.gps_new = False
            self.record(rec)
            return
        if self.ss is None:
            # Trusted at monitor start: the SS bank starts on the current GNSS fix.
            r_m = {"gnss": GNSS_SIGMA_ASSUMED_M, "vgeo": FIX_SIGMA_ASSUMED_M}
            mon = ("gnss", "vgeo") if self.fixes else ("gnss",)
            self.ss = SolutionSeparation(gnss[0], gnss[1], GNSS_SIGMA_ASSUMED_M, r_m, monitored=mon)
            self.ss.t = now     # else its first step predicts a full default second ahead of this fix
        ss = self.ss.step(now, v_ref, sig_v,
                          {"gnss": gnss if self.gps_new else None, "vgeo": fix[:2] if fix else None})
        self.gps_new = False
        vel = self.vel.check(self.gps_vel, v_now, accel)
        rec["ss_lat"], rec["ss_lon"] = enu_to_geodetic(ss["e"], ss["n"], *self.origin[:2])
        rec.update({"hpl": ss["hpl"], "excluded": ss["excluded"], "ss_events": ss["events"], "vel": vel})
        self.record(rec)
        fired = {"ss": "gnss" in ss["excluded"], "vel": bool(vel and vel["alarm"])}
        for k, v in fired.items():
            if v and k not in self.first:
                self.first[k] = t
                self.record({"type": "COMPANION_DETECT", "detector": k, "events": ss["events"]})
        if (fired["ss"] or fired["vel"]) and not self.acted:
            self.acted = True
            why = ",".join(k for k, v in fired.items() if v)
            if self.acts:
                self.command(MAV_CMD_SET_EKF_SOURCE_SET, SOURCE_SET[self.scn])
                print(f"t={t:.1f}s ALARM ({why}) => EKF source set {SOURCE_SET[self.scn]}")
                self.record({"type": "COMPANION_ACTION", "action": "set_ekf_source_set",
                             "source_set": SOURCE_SET[self.scn], "reason": why})
            else:
                print(f"t={t:.1f}s ALARM ({why}) - shadow mode, no action")
                self.record({"type": "COMPANION_ACTION", "action": "none_shadow_mode", "reason": why})

    # --- flight ---------------------------------------------------------------------------------
    def upload_mission(self):
        lat0, lon0, _ = self.origin
        L = mavutil.mavlink
        items = [(L.MAV_CMD_NAV_WAYPOINT, lat0, lon0, 0.0, 0.0, 0.0),
                 (L.MAV_CMD_NAV_TAKEOFF, lat0, lon0, fw_core.TAKEOFF_ALT_M, 15.0, 0.0)]
        for k, (n, e) in enumerate(fw_core.ROUTE_NE):
            lat, lon = enu_to_geodetic(e, n, lat0, lon0)
            items.append((L.MAV_CMD_NAV_WAYPOINT, lat, lon, fw_core.CRUISE_ALT_M, 0.0, 0.0))
            if k == 0:
                # One wide orbit while GNSS is trusted: every heading once, so the calibration can
                # separate wind from heading and scale error (accel ~1.2 m/s^2 at 400 m radius).
                items.append((L.MAV_CMD_NAV_LOITER_TURNS, lat, lon, fw_core.CRUISE_ALT_M, 1.0, fw_core.CAL_ORBIT_RADIUS_M))
        lat, lon = enu_to_geodetic(fw_core.ROUTE_NE[-1][1], fw_core.ROUTE_NE[-1][0], lat0, lon0)
        items.append((L.MAV_CMD_NAV_LOITER_UNLIM, lat, lon, fw_core.CRUISE_ALT_M, 0.0, 0.0))
        self.n_items = len(items)
        self.m.mav.mission_count_send(self.m.target_system, self.m.target_component, len(items), 0)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            msg = self.m.recv_match(type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
                                    blocking=True, timeout=0.05)
            self.service()
            if msg is None:
                continue
            if msg.get_type() == "MISSION_ACK":
                print(f"mission upload: {L.enums['MAV_MISSION_RESULT'][msg.type].name}")
                return
            cmd, lat, lon, alt, p1, p3 = items[msg.seq]
            self.m.mav.mission_item_int_send(self.m.target_system, self.m.target_component, msg.seq,
                                             L.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, cmd, 0, 1, p1, 0, p3, 0,
                                             int(lat * 1e7), int(lon * 1e7), alt, 0)
        raise TimeoutError("mission upload")

    def run(self):
        self.request_streams()
        next_req = 0.0

        def have_origin():
            nonlocal next_req
            if self.origin is None and self.now() >= next_req:
                next_req = self.now() + 2.0
                self.command(mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE, GPS_GLOBAL_ORIGIN_ID)
            return self.origin is not None

        self.pump(have_origin, SETUP_TIMEOUT_S, "EKF origin")
        print(f"EKF origin {self.origin}")
        self.upload_mission()
        modes = self.m.mode_mapping()
        next_arm = 0.0

        def armed():
            nonlocal next_arm
            if not self.armed and self.now() >= next_arm:
                next_arm = self.now() + 2.0
                self.m.set_mode(modes["FBWA"])
                self.command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)
            return self.armed

        self.pump(armed, SETUP_TIMEOUT_S, "arming")
        print(f"armed at sim {self.now():.1f}s")
        self.m.set_mode(modes["AUTO"])
        self.t_auto = self.now()
        self.record({"type": "COMPANION_AUTO_START"})
        auto = modes["AUTO"]
        self.pump(lambda: self.custom_mode == auto, 30, "AUTO mode")
        last_wp = self.n_items - 2
        self.pump(lambda: self.last_reached >= last_wp or self.custom_mode != auto or not self.armed,
                  RUN_TIMEOUT_S, "route")
        outcome = "route_complete" if self.last_reached >= last_wp else \
            f"left_auto:{ {v: k for k, v in modes.items()}.get(self.custom_mode, self.custom_mode) }"
        self.record({"type": "COMPANION_ROUTE_END", "outcome": outcome})
        print(f"{outcome} at t={self.t_mission():.1f}s; loitering {END_LOITER_S:.0f} s")
        t_end = self.now() + END_LOITER_S
        self.pump(lambda: self.now() > t_end, END_LOITER_S + 10, "end loiter")
        self.record({"type": "COMPANION_END", "first_detect": self.first, "outcome": outcome})
        print(f"done t={self.t_mission():.1f}s, first detections {self.first}, wall {time.monotonic() - self.t0_wall:.0f}s")
        self.log.close()


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--connect", default="tcp:127.0.0.1:15841")
    ap.add_argument("--scenario", choices=["baseline", "day", "night", "dr"], required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--spoof", choices=["coherent", "position", "none"], default="coherent")
    ap.add_argument("--rate", type=float, default=1.0, help="drag rate, m/s")
    ap.add_argument("--onset", type=float, default=480.0, help="s after AUTO start (the long north leg starts at ~461 s)")
    ap.add_argument("--bearing", type=float, default=90.0, help="direction the GPS is dragged, deg")
    ap.add_argument("--monitor-start", type=float, default=400.0,
                    help="s after AUTO start; before it GNSS is trusted and the calibration learns")
    ap.add_argument("--no-extnav-vel", dest="extnav_vel", action="store_false",
                    help="send ExternalNav position only (no VISION_SPEED_ESTIMATE); needs EK3_SRC2_VELXY 0")
    ap.add_argument("--ref", choices=["auto", "vo", "air"], default="auto",
                    help="velocity reference; auto = vo for baseline/day, air for night/dr")
    ap.add_argument("--quiet", action="store_true")
    return ap.parse_args(argv)


def main(argv=None):
    a = parse(argv)
    a.log.parent.mkdir(parents=True, exist_ok=True)
    Companion(a).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
