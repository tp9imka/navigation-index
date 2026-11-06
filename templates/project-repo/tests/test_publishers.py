import math
import socket
import struct
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from navapp.geo import enu_to_geodetic, geodetic_to_enu
from navapp.interfaces import Health, NavState, Vec2, Verdict
from navapp.publishers import (SIGMA_TO_R95, STATUSTEXT_CRC_EXTRA, CotPublisher, MavlinkStatusPublisher,
                               UdpSink, statustext_v1, x25_crc)

NOW = datetime(2026, 11, 6, 12, 0, 0, tzinfo=timezone.utc)
STATE = NavState(t=1.0, position=Vec2(100.0, 200.0), sigma_h=2.0, sources_used=("dr", "gnss"))
OK = Verdict(Health.TRUSTED, 1.0, 13.8, False)
BAD = Verdict(Health.EXCLUDED, 99.0, 45.0, True, "windowed NIS over gate")


def crc_extra(name, fields):
    """CRC_EXTRA as pymavlink's generator derives it from the message XML."""
    crc = x25_crc((name + " ").encode())
    for ftype, fname, array_len in fields:
        crc = x25_crc((ftype + " ").encode(), crc)
        crc = x25_crc((fname + " ").encode(), crc)
        if array_len:
            crc = x25_crc(bytes([array_len]), crc)
    return (crc & 0xFF) ^ (crc >> 8)


class Geo(unittest.TestCase):
    def test_roundtrip(self):
        lat, lon = enu_to_geodetic(1234.0, -567.0, 59.0, 10.0)
        e, n = geodetic_to_enu(lat, lon, 59.0, 10.0)
        self.assertAlmostEqual(e, 1234.0, places=6)
        self.assertAlmostEqual(n, -567.0, places=6)

    def test_one_degree_latitude_is_about_111_km(self):
        lat, _ = enu_to_geodetic(0.0, 111_000.0, 0.0, 0.0)
        self.assertAlmostEqual(lat, 1.0, delta=0.01)


class Cot(unittest.TestCase):
    def test_event_fields(self):
        root = ET.fromstring(CotPublisher("uav-1", 59.0, 10.0, clock=lambda: NOW).publish(STATE, BAD))
        self.assertEqual(root.tag, "event")
        self.assertEqual(root.get("time"), "2026-11-06T12:00:00.000Z")
        self.assertEqual(root.get("stale"), "2026-11-06T12:00:30.000Z")
        pt = root.find("point")
        lat, lon = enu_to_geodetic(100.0, 200.0, 59.0, 10.0)
        self.assertAlmostEqual(float(pt.get("lat")), lat, places=6)
        self.assertAlmostEqual(float(pt.get("ce")), SIGMA_TO_R95 * 2.0, places=1)
        self.assertIn("nav=excluded alarm=1", root.find("detail/remarks").text)

    def test_no_estimate_publishes_nothing(self):
        state = NavState(t=0, position=Vec2(math.nan, math.nan), sigma_h=math.inf)
        self.assertIsNone(CotPublisher("u", 0, 0).publish(state, OK))


class Mavlink(unittest.TestCase):
    def test_crc_extra_matches_statustext_definition(self):
        self.assertEqual(crc_extra("STATUSTEXT", [("uint8_t", "severity", 0), ("char", "text", 50)]),
                         STATUSTEXT_CRC_EXTRA)

    def test_frame_layout_and_checksum(self):
        frame = statustext_v1("NAV:EXCLUDED", 2, seq=5)
        self.assertEqual(len(frame), 6 + 51 + 2)
        stx, length, seq, sysid, compid, msgid = struct.unpack("<BBBBBB", frame[:6])
        self.assertEqual((stx, length, seq, msgid), (0xFE, 51, 5, 253))
        self.assertEqual(frame[6], 2)
        self.assertTrue(frame[7:].startswith(b"NAV:EXCLUDED\x00"))
        crc = x25_crc(frame[1:-2] + bytes([STATUSTEXT_CRC_EXTRA]))
        self.assertEqual(struct.unpack("<H", frame[-2:])[0], crc)

    def test_sends_only_on_health_change(self):
        pub = MavlinkStatusPublisher()
        self.assertIsNotNone(pub.publish(STATE, OK))
        self.assertIsNone(pub.publish(STATE, OK))
        self.assertIsNotNone(pub.publish(STATE, BAD))


class Udp(unittest.TestCase):
    def test_sink_delivers_to_localhost(self):
        rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rx.bind(("127.0.0.1", 0))
        rx.settimeout(2.0)
        sink = UdpSink("127.0.0.1", rx.getsockname()[1])
        try:
            data = CotPublisher("u", 59.0, 10.0, sink=sink).publish(STATE, OK)
            self.assertEqual(rx.recv(65535), data)
        finally:
            sink.close()
            rx.close()


if __name__ == "__main__":
    unittest.main()
