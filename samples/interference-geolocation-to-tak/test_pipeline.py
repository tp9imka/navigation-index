import json
import math
import os
import socket
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer

import kraken
import scenario
import tak_out
from geo import LocalFrame, bearing_in_frame, compass_bearing, wrap_deg
from triangulate import ellipse, locate

TRUTH = (scenario.JAMMER_LAT, scenario.JAMMER_LON)


def _err_m(fix):
    te, tn, _ = fix["frame"].to_enu(*TRUTH)
    return math.hypot(fix["enu"][0] - te, fix["enu"][1] - tn)


class GeoTest(unittest.TestCase):
    def test_enu_round_trip(self):
        f = LocalFrame(52.08, 5.12, 10.0)
        lat, lon, h = f.to_geodetic(*f.to_enu(52.1, 5.2, 50.0))
        self.assertAlmostEqual(lat, 52.1, places=8)
        self.assertAlmostEqual(lon, 5.2, places=8)
        self.assertAlmostEqual(h, 50.0, places=3)

    def test_bearing_and_wrap(self):
        self.assertAlmostEqual(compass_bearing((0, 0), (1, 0)), 90.0)
        self.assertAlmostEqual(compass_bearing((0, 0), (0, -1)), 180.0)
        self.assertAlmostEqual(wrap_deg(350 - 10), -20.0)

    def test_bearing_in_frame_convergence(self):
        f = LocalFrame(52.08, 5.12)
        same = bearing_in_frame(f, 52.08, 5.12, 45.0)
        east = bearing_in_frame(f, 52.08, 5.30, 0.0)
        self.assertAlmostEqual(same, 45.0, places=3)
        self.assertGreater(abs(wrap_deg(east)), 0.1)  # ~12 km east: grid north differs


class KrakenAdapterTest(unittest.TestCase):
    def test_json_convention(self):
        # array heading 30, DSP theta 300 => true = 30 + 360 - 300 = 90 (east)
        d = kraken.to_kraken_json(1_700_000_000_000, "S1", 52.0, 5.0, 30.0, 300.0, 0.8, -40.0, 1575.42e6)
        b = kraken.from_kraken_json(json.loads(json.dumps(d)))
        self.assertAlmostEqual(b.bearing_deg, 90.0)
        self.assertAlmostEqual(b.t, 1_700_000_000.0)
        self.assertEqual(b.station_id, "S1")

    def test_csv_line_matches_json(self):
        # field 2 is 360 - theta, as written for "Kraken App" in kraken_sdr_signal_processor.py
        line = ("1700000000000, 60.0, 0.8, -40.0, 1575420000, UCA, 100, S1, 52.0, 5.0, 30.0, 30.0, "
                "GPS, R, R, R, R, 1.00, 2.00")
        self.assertAlmostEqual(kraken.from_kraken_csv_line(line).bearing_deg, 90.0)

    def test_poll_csv_over_http(self):
        body = (b"1700000000000, 60.0, 0.8, -40.0, 1575420000, UCA, 100, S1, 52.0, 5.0, 30.0, 30.0, "
                b"GPS, R, R, R, R, 1.0 \n")

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            url = f"http://127.0.0.1:{srv.server_port}/DOA_value.html"
            got = list(kraken.poll_csv(url, period_s=0, max_polls=2))
        finally:
            srv.shutdown()
            srv.server_close()
        self.assertEqual(len(got), 2)
        self.assertAlmostEqual(got[0].bearing_deg, 90.0)


class TriangulateTest(unittest.TestCase):
    def test_noiseless_exact(self):
        recs, _ = scenario.generate(seed=1, outlier_p=0.0)
        bs = []
        for r in recs[:30]:
            b = kraken.from_kraken_json(r)
            true_b = compass_bearing((0, 0), LocalFrame(b.lat, b.lon).to_enu(*TRUTH)[:2])
            bs.append(kraken.Bearing(b.t, b.station_id, b.lat, b.lon, true_b))
        self.assertLess(_err_m(locate(bs, 1.0)), 1.0)

    def test_rejects_multipath_outliers(self):
        recs, n_out = scenario.generate(seed=7)
        bs = [kraken.from_kraken_json(r) for r in recs]
        fix = locate(bs, scenario.FIXED_SIGMA_DEG, {scenario.VEHICLE_ID: scenario.MOVING_SIGMA_DEG})
        self.assertGreater(n_out, 50)
        self.assertLessEqual(fix["n_used"], len(bs) - n_out)
        smaj, _, _ = ellipse(fix["cov"])
        self.assertLess(_err_m(fix), smaj)

    def test_ellipse_axes(self):
        smaj, smin, ang = ellipse([[100.0, 0.0], [0.0, 25.0]], chi2=1.0)
        self.assertAlmostEqual(smaj, 10.0)
        self.assertAlmostEqual(smin, 5.0)
        self.assertAlmostEqual(ang, 90.0)  # major axis east-west
        _, _, ang = ellipse([[50.0, 49.0], [49.0, 50.0]], chi2=1.0)
        self.assertAlmostEqual(ang, 45.0)


class TakOutTest(unittest.TestCase):
    def test_events(self):
        evs = tak_out.events_from_fix("j1", 52.08, 5.12, (120.0, 40.0, 45.0), "test")
        pt, el = (ET.fromstring(e) for e in evs)
        self.assertEqual(pt.get("type"), tak_out.EMITTER_COT_TYPE)
        self.assertEqual(pt.get("how"), tak_out.HOW_FUSED)
        self.assertAlmostEqual(float(pt.find("point").get("ce")), 120.0 / math.sqrt(5.991), places=1)
        self.assertEqual(pt.find("detail/remarks").text, "test")
        e = el.find("detail/shape/ellipse")
        self.assertEqual(el.get("type"), "u-d-c-e")
        self.assertEqual((e.get("major"), e.get("minor"), e.get("angle")), ("120.0", "40.0", "45.0"))

    def test_write_and_udp(self):
        evs = tak_out.events_from_fix("j1", 52.08, 5.12, (120.0, 40.0, 45.0), "test")
        with tempfile.TemporaryDirectory() as d:
            paths = tak_out.write_events(evs, d, "j1")
            self.assertTrue(all(os.path.getsize(p) > 0 for p in paths))
        rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rx.bind(("127.0.0.1", 0))
        rx.settimeout(2)
        tak_out.send_udp(evs, "127.0.0.1", rx.getsockname()[1])
        self.assertEqual(rx.recv(65535), evs[0])
        rx.close()


if __name__ == "__main__":
    unittest.main()
