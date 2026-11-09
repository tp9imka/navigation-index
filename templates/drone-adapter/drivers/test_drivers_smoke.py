"""Smoke test: drivers import without any SDK, satisfy Adapter, and convert frames as frames.md
says. Uses fake connection objects; nothing here talks to a vehicle, a SITL or an SDK.

Run from templates/drone-adapter:  python3 -m unittest drivers.test_drivers_smoke -v
"""
from __future__ import annotations

import math
import types
import unittest

try:
    from ..adapter import Adapter, Setpoint
except ImportError:
    from adapter import Adapter, Setpoint  # type: ignore

from . import (ArduPilotPymavlinkAdapter, CrazyflieCflibAdapter, Px4MavsdkAdapter,
               TelloDjitellopyAdapter)
from . import ardupilot_pymavlink as ap
from . import px4_mavsdk as px4
from . import tello_djitellopy as tl


class Rec:
    """Records every method call: obj.foo(1, 2) => calls == [("foo", (1, 2))]."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        return lambda *a, **k: self.calls.append((name, a))


def msg(kind, **f):
    m = types.SimpleNamespace(**f)
    m.get_type = lambda: kind
    return m


class Drivers(unittest.TestCase):
    def test_all_are_adapters_without_sdk(self):
        for cls in (Px4MavsdkAdapter, ArduPilotPymavlinkAdapter, CrazyflieCflibAdapter,
                    TelloDjitellopyAdapter):
            self.assertIsInstance(cls(), Adapter, cls.__name__)

    def test_px4_heading_and_ned(self):
        psi = px4.heading_step(0.0, 0.5, 0.1, yaw_now=0.0)
        self.assertAlmostEqual(psi, 0.05)                      # +yaw_rate => CCW heading grows
        n, e, d, yaw_deg = px4.ned_velocity_yaw(Setpoint(1.0, 0.0, 0.5), 0.0)
        self.assertEqual((n, e, d), (0.0, 1.0, -0.5))          # east => NED east; up => -down
        self.assertAlmostEqual(yaw_deg, 90.0)                  # ENU yaw 0 (east) = 90 deg NED
        capped = px4.heading_step(0.0, 10.0, 0.2, yaw_now=0.0)
        self.assertAlmostEqual(capped, px4.MAX_HEADING_LEAD)   # target cannot run away

    def test_ardupilot_pose_send_ranges(self):
        conn = Rec()
        conn.mav = Rec()
        conn.target_system, conn.target_component = 1, 1
        d = ArduPilotPymavlinkAdapter(conn=conn)
        d.handle(msg("LOCAL_POSITION_NED", x=2.0, y=1.0, z=-1.5, vx=0.1, vy=0.2, vz=0.0))
        d.handle(msg("ATTITUDE", yaw=0.0))                     # NED yaw 0 = facing north
        d.start()
        d._keepalive.stop()
        p = d.pose()
        self.assertEqual((p.x, p.y, p.z), (0.0, 0.0, 1.5))     # x, y latched at A; z = height
        self.assertAlmostEqual(p.yaw, math.pi / 2)             # north = ENU +90 deg
        conn.mav.calls.clear()
        d._send(Setpoint(1.0, 0.0, 0.0, yaw_rate=0.2), 0.05)
        args = conn.mav.calls[0][1]
        self.assertEqual(args[3:5], (ap.MAV_FRAME_LOCAL_NED, 1479))
        self.assertEqual(args[8:11], (0.0, 1.0, -0.0))         # ENU east => NED (0, 1, 0)
        self.assertAlmostEqual(args[15], -0.2)                 # CCW ENU rate => CW-negative NED
        d.handle(msg("DISTANCE_SENSOR", id=0, orientation=2, current_distance=150,
                     min_distance=10, max_distance=400))
        s = d.ranges()
        self.assertAlmostEqual(s.angles[0], -math.pi / 2)      # YAW_90 = right (ArduPilot rule)
        self.assertAlmostEqual(s.distances[0], 1.5)

    def test_crazyflie_world_setpoint_and_ranges(self):
        cf = types.SimpleNamespace(commander=Rec())
        d = CrazyflieCflibAdapter(scf=types.SimpleNamespace(cf=cf))
        d._on_log(0, {"stateEstimate.x": 1.0, "stateEstimate.y": 2.0, "stateEstimate.z": 0.5,
                      "stateEstimate.yaw": 90.0}, None)
        d._on_log(0, {"stateEstimate.vx": 0.0, "stateEstimate.vy": 0.0,
                      "stateEstimate.vz": 0.0}, None)
        d._on_log(0, {"range.front": 300, "range.back": 8000, "range.left": 1200,
                      "range.right": 65535, "range.up": 8000, "range.zrange": 500}, None)
        p = d.pose()
        self.assertAlmostEqual(p.yaw, math.pi / 2)
        d._send(Setpoint(0.2, 0.0, 0.0, yaw_rate=math.radians(10)), 0.05)
        self.assertEqual(cf.commander.calls[0][0], "send_velocity_world_setpoint")
        self.assertEqual(cf.commander.calls[0][1][:3], (0.2, 0.0, 0.0))
        self.assertAlmostEqual(cf.commander.calls[0][1][3], 10.0)   # rad/s => deg/s
        s = d.ranges()
        self.assertEqual(s.distances[:3], [0.3, 1.2, math.inf])     # front, left, back
        self.assertEqual(s.distances[3], math.inf)                  # >= 8000 mm = no return

    def test_tello_refuses_uncalibrated_and_maps_sticks(self):
        with self.assertRaises(RuntimeError):
            TelloDjitellopyAdapter(tello=Rec()).send_setpoint(Setpoint(0.0, 0.0, 0.0))
        k = 50.0
        self.assertEqual(tl.setpoint_to_rc(Setpoint(1.0, 0.0, 0.0), 0.0, k, k, 1.0), (0, 50, 0, 0))
        self.assertEqual(tl.setpoint_to_rc(Setpoint(0.0, 1.0, 0.0), 0.0, k, k, 1.0), (-50, 0, 0, 0))
        self.assertEqual(tl.setpoint_to_rc(Setpoint(0.0, 0.0, 0.0, math.radians(20)), 0.0, k, k,
                                           1.0), (0, 0, 0, -20))   # CCW => negative (CW) stick
        self.assertEqual(tl.setpoint_to_rc(Setpoint(9.0, 0.0, 0.0), 0.0, k, k, 1.0)[1], 100)


if __name__ == "__main__":
    unittest.main()
