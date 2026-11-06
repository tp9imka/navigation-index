import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from types import SimpleNamespace

import cot

NOW = datetime(2026, 11, 6, 12, 0, 0, tzinfo=timezone.utc)


class BuildEventTest(unittest.TestCase):
    def test_round_trip(self):
        root = ET.fromstring(cot.build_event("uav-1", 51.5, -0.12, 120.0, course=90.0,
                                             speed=15.0, callsign="UAV1", now=NOW))
        self.assertEqual(root.tag, "event")
        self.assertEqual(root.get("type"), "a-f-A-M-F-Q")
        self.assertEqual(root.get("uid"), "uav-1")
        self.assertEqual(root.get("time"), "2026-11-06T12:00:00.000Z")
        self.assertEqual(root.get("start"), root.get("time"))
        self.assertEqual(root.get("stale"), "2026-11-06T12:00:30.000Z")
        pt = root.find("point")
        self.assertAlmostEqual(float(pt.get("lat")), 51.5)
        self.assertAlmostEqual(float(pt.get("lon")), -0.12)
        self.assertAlmostEqual(float(pt.get("hae")), 120.0)
        self.assertEqual(float(pt.get("ce")), cot.UNKNOWN_ERROR_M)
        trk = root.find("detail/track")
        self.assertEqual(float(trk.get("course")), 90.0)
        self.assertEqual(float(trk.get("speed")), 15.0)
        self.assertEqual(root.find("detail/contact").get("callsign"), "UAV1")

    def test_no_track_without_velocity(self):
        root = ET.fromstring(cot.build_event("uav-1", 0, 0, 0, now=NOW))
        self.assertIsNone(root.find("detail/track"))


class GlobalPositionIntTest(unittest.TestCase):
    def msg(self, **kw):
        base = dict(lat=515007000, lon=-1246000, alt=120500, vx=0, vy=1500, hdg=9000)
        base.update(kw)
        return SimpleNamespace(**base)

    def test_scaling(self):
        root = ET.fromstring(cot.from_global_position_int(self.msg(), "uav-2", now=NOW,
                                                          geoid_separation_m=47.0))
        pt = root.find("point")
        self.assertAlmostEqual(float(pt.get("lat")), 51.5007)
        self.assertAlmostEqual(float(pt.get("lon")), -0.1246)
        self.assertAlmostEqual(float(pt.get("hae")), 167.5)
        trk = root.find("detail/track")
        self.assertAlmostEqual(float(trk.get("speed")), 15.0)
        self.assertAlmostEqual(float(trk.get("course")), 90.0)

    def test_course_from_velocity_when_heading_unknown(self):
        m = self.msg(vx=-1000, vy=0, hdg=cot.HDG_UNKNOWN)  # flying south
        trk = ET.fromstring(cot.from_global_position_int(m, "uav-3", now=NOW)).find("detail/track")
        self.assertAlmostEqual(float(trk.get("course")), 180.0)
        self.assertAlmostEqual(float(trk.get("speed")), 10.0)


if __name__ == "__main__":
    unittest.main()
