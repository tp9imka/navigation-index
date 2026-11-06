"""Bit-exact cross-check of odid.py against opendroneid-core-c.

Fixtures in fixtures/core_c_*.jsonl were produced by corec/odid_vectors (core-c encoder +
decodeOpenDroneID). Each line holds the wire bytes and core-c's decoded fields; every
field must match exactly (floats compared as IEEE values, strings as raw bytes).
If corec/odid_vectors is built, a fresh random batch is also checked live.
"""
import json
import os
import subprocess
import unittest

import odid

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
HARNESS = os.path.join(HERE, "corec", "odid_vectors")
BYTES_FIELDS = {"UASID", "AuthData", "Desc", "OperatorId"}
UASID_WIRE_LEN = odid.ID_SIZE


def py_view(buf: bytes) -> dict:
    ret, uas = odid.decode(buf)
    out = {"ret": ret}
    for key, rec in uas.items():
        out[key] = {k: (v[:UASID_WIRE_LEN].hex() if k == "UASID" else v.hex()) if k in BYTES_FIELDS else v
                    for k, v in rec.items()}
    return out


def compare_lines(tc, lines):
    n = 0
    for line in lines:
        ref = json.loads(line)
        buf = bytes.fromhex(ref.pop("hex"))
        got = py_view(buf)
        tc.assertEqual(got, ref, msg=f"mismatch for {buf.hex()}")
        n += 1
    return n


class CoreCFixtures(unittest.TestCase):
    def _check(self, name, minimum):
        with open(os.path.join(FIX, name)) as f:
            n = compare_lines(self, f)
        self.assertGreaterEqual(n, minimum)

    def test_encoded_by_core_c(self):
        self._check("core_c_gen.jsonl", 400)

    def test_random_raw_messages(self):
        self._check("core_c_fuzz.jsonl", 400)

    def test_public_captures(self):
        self._check("core_c_captures.jsonl", 50)

    @unittest.skipUnless(os.access(HARNESS, os.X_OK), "corec/odid_vectors not built")
    def test_live_harness(self):
        for mode, seed in (("gen", "4242"), ("fuzz", "4243")):
            out = subprocess.run([HARNESS, mode, "300", seed], capture_output=True, text=True, check=True)
            self.assertGreaterEqual(compare_lines(self, out.stdout.splitlines()), 200)


CAPTURES = os.path.join(HERE, "captures")


@unittest.skipUnless(os.path.isdir(CAPTURES), "run ./fetch_captures.sh first")
class PublicCaptures(unittest.TestCase):
    """Counts observed on the opendroneid/wireshark-dissector samples at d12670f."""

    def _decoded(self, name):
        import capture
        return [(r, odid.decode(r["payload"])) for r in capture.extract(os.path.join(CAPTURES, name))]

    def test_wifi_beacon(self):
        recs = self._decoded("odid_wifi_bcn_sample.pcap")
        self.assertEqual(len(recs), 21)
        self.assertTrue(all(t == odid.PACKED and "Location" in u for _, (t, u) in recs))
        s = odid.summarize(recs[0][1][1])
        self.assertEqual((s["lat"], s["lon"], s["operator_id"]), (45.5457468, -122.9681496, "GBR-OP-123ABCD"))

    def test_wifi_nan_and_beacon(self):
        recs = self._decoded("odid_wifi_sample.pcap")
        self.assertEqual(sorted({r["transport"] for r, _ in recs}), ["wifi-beacon", "wifi-nan"])
        self.assertEqual(len(recs), 42)

    def test_bt5_long_range_crc_filter(self):
        recs = self._decoded("odid_bt5_lr_sample.pcapng")
        self.assertEqual(len(recs), 244)
        ids = {odid.summarize(u).get("ids", {}).get("serial_number") for _, (t, u) in recs if t == odid.PACKED}
        self.assertEqual(ids, {"SSEVTFG93700070"})


class Semantics(unittest.TestCase):
    """Hand-built vectors for the scaling rules, independent of the C fixtures."""

    def test_location_scaling(self):
        m = bytearray(odid.MESSAGE_SIZE)
        m[0] = 0x12                      # Location, protocol 2
        m[1] = 0x20 | 0x02 | 0x01        # airborne, EW bit, speed multiplier
        m[2] = 10                        # 10 + 180 = 190 deg
        m[3] = 4                         # 4 * 0.75 + 63.75 = 66.75 m/s
        m[4] = 0xFE                      # -2 * 0.5 = -1 m/s
        m[5:9] = (515007000).to_bytes(4, "little", signed=True)
        m[9:13] = (-1246000).to_bytes(4, "little", signed=True)
        m[15:17] = (2240).to_bytes(2, "little")  # 2240 * 0.5 - 1000 = 120 m
        m[21:23] = (12345).to_bytes(2, "little")
        loc = odid.decode(bytes(m))[1]["Location"]
        self.assertEqual(loc["Direction"], 190.0)
        self.assertEqual(loc["SpeedHorizontal"], 66.75)
        self.assertEqual(loc["SpeedVertical"], -1.0)
        self.assertEqual(loc["Latitude"], 51.5007)
        self.assertEqual(loc["Longitude"], -0.1246)
        self.assertEqual(loc["AltitudeGeo"], 120.0)
        self.assertEqual(loc["TimeStamp"], odid.f32(1234.5))
        self.assertEqual(odid.STATUS[loc["Status"]], "airborne")

    def test_pack_rejects_two_locations(self):
        loc = bytes([0x12]) + bytes(24)
        pack = bytes([0xF2, odid.MESSAGE_SIZE, 2]) + loc + loc
        self.assertEqual(odid.decode(pack)[0], odid.INVALID)

    def test_truncated_pack_rejected(self):
        pack = bytes([0xF2, odid.MESSAGE_SIZE, 3]) + bytes([0x12]) + bytes(24)
        self.assertEqual(odid.decode(pack)[0], odid.INVALID)


if __name__ == "__main__":
    unittest.main()
