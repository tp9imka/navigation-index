import json
import os
import subprocess
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import odid
import rid_to_cot
import sim
from tracker import Tracker

HARNESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corec", "odid_vectors")


class SimEncoder(unittest.TestCase):
    def test_round_trip(self):
        pack = sim.encode_pack([sim.encode_basic_id("SN-1"),
                                sim.encode_location(51.5007, -0.1246, 120.0, 271.0, 70.0, vspeed=-1.5,
                                                    ts_after_hour=1234.5),
                                sim.encode_system(51.5, -0.12, 30.0, timestamp=12345),
                                sim.encode_operator_id("OP-1"), sim.encode_self_id("hello")])
        s = odid.summarize(odid.decode(pack)[1])
        self.assertEqual(s["ids"], {"serial_number": "SN-1"})
        self.assertEqual((s["lat"], s["lon"], s["alt_geo_m"]), (51.5007, -0.1246, 120.0))
        self.assertEqual((s["course_deg"], s["speed_v_ms"], s["ts_after_hour_s"]), (271.0, -1.5, 1234.5))
        self.assertAlmostEqual(s["speed_h_ms"], 70.0, delta=0.375)  # 0.75 m/s steps above 63.75
        self.assertEqual((s["operator_lat"], s["operator_alt_geo_m"], s["operator_id"]), (51.5, 30.0, "OP-1"))

    @unittest.skipUnless(os.access(HARNESS, os.X_OK), "corec/odid_vectors not built")
    def test_core_c_agrees_on_scenario(self):
        packs = [p.hex() for _, _, p in sim.scenario(duration_s=5)]
        out = subprocess.run([HARNESS, "decode"], input="\n".join(packs) + "\n",
                             capture_output=True, text=True, check=True).stdout.splitlines()
        self.assertEqual(len(out), len(packs))
        for line in out:
            ref = json.loads(line)
            self.assertEqual(ref["ret"], odid.PACKED)
            py = odid.decode(bytes.fromhex(ref["hex"]))[1]
            self.assertEqual(py["Location"]["Latitude"], ref["Location"]["Latitude"])
            self.assertEqual(py["System"]["OperatorLongitude"], ref["System"]["OperatorLongitude"])


class TrackerFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = rid_to_cot.run(sim.scenario(), lambda ev: None)
        cls.flags = {tr.key.split(":", 1)[1]: set(tr.flags) for tr in cls.tracker.tracks.values()}

    def test_expected_flags(self):
        self.assertEqual(self.flags["SIMA-0001"], {"duplicate_id"})
        self.assertEqual(self.flags["SIMC-0003"], {"impossible_speed", "location_jump"})
        self.assertEqual(self.flags["SIMD-0004"], {"operator_far"})
        self.assertEqual(self.flags["SIME-9999"], {"id_change"})
        self.assertEqual(self.flags["SIME-0005"], set())
        self.assertEqual(self.flags["SIMF-0006"], set())

    def test_staleness(self):
        end = sim.T0 + 30
        live, stale = self.tracker.sweep(end)
        self.assertEqual({t.uas_id for t in stale},
                         {"serial_number:SIMF-0006", "serial_number:SIME-0005"})
        live, stale = self.tracker.sweep(end + 120)
        self.assertEqual(live + stale, [])

    def test_mac_track_adopts_id(self):
        tr = Tracker()
        tr.ingest(0.0, "m1", sim.encode_location(1.0, 2.0, 10, 0, 0))
        self.assertIn("mac:m1", tr.tracks)
        tr.ingest(0.5, "m1", sim.encode_basic_id("LATE-ID"))
        self.assertEqual(list(tr.tracks), ["serial_number:LATE-ID"])


class CotOutput(unittest.TestCase):
    def test_uas_and_operator_events(self):
        tracker = Tracker()
        t, mac, pack = sim.scenario(duration_s=1)[0]
        trk = tracker.ingest(t, mac, pack)
        evs = [ET.fromstring(e) for e in rid_to_cot.events_for_track(trk, datetime.now(timezone.utc))]
        self.assertEqual([e.get("type") for e in evs], ["a-u-A-M-H-Q", "a-u-G"])
        uas, op = evs
        self.assertEqual(uas.get("uid"), "rid-SIMA-0001")
        self.assertEqual(float(uas.find("point").get("hae")), 150.0)
        self.assertEqual(float(uas.find("point").get("ce")), 10.0)
        self.assertIsNotNone(uas.find("detail/track"))
        self.assertIn("GBR-OP-DEMO0001", op.find("detail/contact").get("callsign"))


if __name__ == "__main__":
    unittest.main()
