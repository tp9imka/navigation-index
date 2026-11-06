"""Tests for ephemeris_check.py on synthetic GPS LNAV subframes and a synthetic RINEX 3 record.
Stdlib only. Run: python3 -m unittest -v test_ephemeris_check.py"""

import math
import struct
import tempfile
import unittest
from pathlib import Path

from ephemeris_check import (_PARITY, EphemerisChecker, WEEK_S, decode_lnav, parse_rinex3_gps_nav,
                             pick_reference, sat_pos_clk, utc_to_gps, word_parity_ok)

PI = math.pi
EPH = {"week": 2331, "iode": 50, "iodc": 50, "svh": 0, "tgd": -1.1e-8, "toc": 374400.0, "af2": 0.0,
       "af1": -2.0e-12, "af0": 3.1e-4, "crs": 31.5, "deln": 4.5e-9, "m0": 0.52, "cuc": 1.6e-6, "e": 0.0104,
       "cus": 8.3e-6, "sqrta": 5153.62, "toe": 374400.0, "cic": -5.2e-8, "omg0": 1.03, "cis": 1.1e-7,
       "i0": 0.962, "crc": 222.4, "omg": -1.51, "omgd": -8.1e-9, "idot": 1.2e-10}
# field: (subframe, [(pos, len), ...] MSB first, scale, signed)
LAYOUT = {
    "week": (1, [(48, 10)], 1, False), "svh": (1, [(64, 6)], 1, False), "tgd": (1, [(160, 8)], 2 ** -31, True),
    "toc": (1, [(176, 16)], 16, False), "af2": (1, [(192, 8)], 2 ** -55, True),
    "af1": (1, [(200, 16)], 2 ** -43, True), "af0": (1, [(216, 22)], 2 ** -31, True),
    "crs": (2, [(56, 16)], 2 ** -5, True), "deln": (2, [(72, 16)], 2 ** -43 * PI, True),
    "m0": (2, [(88, 8), (96, 24)], 2 ** -31 * PI, True), "cuc": (2, [(120, 16)], 2 ** -29, True),
    "e": (2, [(136, 8), (144, 24)], 2 ** -33, False), "cus": (2, [(168, 16)], 2 ** -29, True),
    "sqrta": (2, [(184, 8), (192, 24)], 2 ** -19, False), "toe": (2, [(216, 16)], 16, False),
    "cic": (3, [(48, 16)], 2 ** -29, True), "omg0": (3, [(64, 8), (72, 24)], 2 ** -31 * PI, True),
    "cis": (3, [(96, 16)], 2 ** -29, True), "i0": (3, [(112, 8), (120, 24)], 2 ** -31 * PI, True),
    "crc": (3, [(144, 16)], 2 ** -5, True), "omg": (3, [(160, 8), (168, 24)], 2 ** -31 * PI, True),
    "omgd": (3, [(192, 24)], 2 ** -43 * PI, True), "idot": (3, [(224, 14)], 2 ** -43 * PI, True),
}


def shifted(eph, **kw):
    out = dict(eph)
    out.update(kw)
    return out


def _put(v, pos, ln, x):
    return v | ((x & ((1 << ln) - 1)) << (240 - pos - ln))


def _parity(d):
    out = 0
    for _, idx in _PARITY:  # D29* = D30* = 0 in these synthetic words
        x = 0
        for i in idx:
            x ^= (d >> (24 - i)) & 1
        out = (out << 1) | x
    return out


def encode_sfrbx(eph, sv=5):
    """Three UBX-RXM-SFRBX payloads (subframes 1-3) carrying eph, in the layout ephemeris_check decodes."""
    bits = {1: 0, 2: 0, 3: 0}
    for name, (sf, parts, scale, _signed) in LAYOUT.items():
        val = eph[name] % 1024 if name == "week" else round(eph[name] / scale)
        n = sum(ln for _, ln in parts)
        val &= (1 << n) - 1
        shift = n
        for pos, ln in parts:
            shift -= ln
            bits[sf] = _put(bits[sf], pos, ln, val >> shift)
    bits[1] = _put(bits[1], 70, 2, eph["iodc"] >> 8)
    bits[1] = _put(bits[1], 168, 8, eph["iodc"])
    bits[2] = _put(bits[2], 48, 8, eph["iode"])
    bits[3] = _put(bits[3], 216, 8, eph["iode"])
    out = []
    for sf in (1, 2, 3):
        v = _put(bits[sf], 0, 8, 0x8B)
        v = _put(v, 24, 24, (1000 << 7) | (sf << 2))
        words = [(v >> (240 - 24 * (k + 1))) & 0xFFFFFF for k in range(10)]
        raw = [(d << 6) | _parity(d) for d in words]
        out.append(bytes([0, sv, 0, 0, 10, 0, 2, 0]) + b"".join(struct.pack("<I", w) for w in raw))
    return out


def rinex_record(sv, eph, epoch="2024 09 12 08 00 00"):
    f = lambda x: f"{x: .12E}".replace("E", "D")  # noqa: E731
    rows = [[eph["iode"], eph["crs"], eph["deln"], eph["m0"]], [eph["cuc"], eph["e"], eph["cus"], eph["sqrta"]],
            [eph["toe"], eph["cic"], eph["omg0"], eph["cis"]], [eph["i0"], eph["crc"], eph["omg"], eph["omgd"]],
            [eph["idot"], 1.0, eph["week"], 0.0], [2.0, eph["svh"], eph["tgd"], eph["iodc"]], [370000.0, 4.0, 0.0, 0.0]]
    head = f"{sv} {epoch}" + "".join(f(x) for x in (eph["af0"], eph["af1"], eph["af2"]))
    return "\n".join([head] + ["    " + "".join(f(x) for x in r) for r in rows]) + "\n"


class Ephemeris(unittest.TestCase):
    def test_decode_round_trip(self):
        chk = EphemerisChecker({})
        done = [chk.feed_sfrbx(p, 1726125465.0) for p in encode_sfrbx(EPH)]
        self.assertEqual(done, [None, None, "G05"])
        dec = chk.current["G05"]
        for k, (_, parts, scale, _) in LAYOUT.items():
            self.assertAlmostEqual(dec[k], EPH[k], delta=scale, msg=k)
        self.assertEqual((dec["iode"], dec["iodc"]), (50, 50))

    def test_parity_rejects_flipped_bit(self):
        p = bytearray(encode_sfrbx(EPH)[1])
        self.assertTrue(word_parity_ok(struct.unpack_from("<I", p, 12)[0]))
        p[13] ^= 0x10
        self.assertFalse(word_parity_ok(struct.unpack_from("<I", p, 12)[0]))
        chk = EphemerisChecker({})
        self.assertIsNone(chk.feed_sfrbx(bytes(p), 1726125465.0))
        self.assertEqual(chk.parity_fail, 1)

    def test_iode_mismatch_across_subframes_not_used(self):
        sf = encode_sfrbx(EPH)
        sf[2] = encode_sfrbx(shifted(EPH, iode=51, iodc=51))[2]
        bits = [[(struct.unpack_from("<I", p, 8 + 4 * k)[0] >> 6) & 0xFFFFFF for k in range(10)] for p in sf]
        self.assertIsNone(decode_lnav(*bits, near_week=2331))

    def test_orbit_radius_and_reference_choice(self):
        t = utc_to_gps(1726125465.0)
        x, y, z, clk = sat_pos_clk(EPH, t)
        self.assertAlmostEqual(math.sqrt(x * x + y * y + z * z) / 1000, 26560, delta=300)
        self.assertAlmostEqual(clk, EPH["af0"], delta=1e-6)
        old = shifted(EPH, iode=49, toe=367200.0, toc=367200.0)
        far = shifted(EPH, iode=10, toe=374400.0 - 2 * WEEK_S)
        self.assertIs(pick_reference([old, EPH, far], EPH, t), EPH)
        self.assertIs(pick_reference([old, far], EPH, t), old)  # nearest toe when no IODE match
        self.assertIsNone(pick_reference([far], EPH, t))  # not measured, never "consistent"

    def test_rinex3_parse(self):
        text = ("     3.04           N: GNSS NAV DATA    M: MIXED            RINEX VERSION / TYPE\n"
                "                                                            END OF HEADER\n"
                + rinex_record("G05", EPH) + "R03 2024 09 12 08 15 00 1.0D-05 0.0D+00 0.0D+00\n" + "    x\n" * 3)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "brdc.rnx")
            p.write_text(text)
            nav = parse_rinex3_gps_nav(p)
        self.assertEqual(list(nav), ["G05"])
        e = nav["G05"][0]
        for k in ("sqrta", "e", "m0", "omg0", "toe", "af0", "iode", "week"):
            self.assertAlmostEqual(e[k], EPH[k], places=9, msg=k)
        self.assertEqual(e["toc"], 374400.0)  # 2024-09-12 08:00:00 GPS = week 2331, 374400 s

    def test_mismatch_metres(self):
        t0 = 1726125465.0
        chk = EphemerisChecker({"G05": [EPH]})
        for p in encode_sfrbx(EPH):
            chk.feed_sfrbx(p, t0)
        self.assertLess(chk.mismatch_m(t0)["G05"], 1.0)
        chk = EphemerisChecker({"G05": [EPH]})
        for p in encode_sfrbx(shifted(EPH, af0=EPH["af0"] + 1e-6)):  # 1 us clock => 300 m
            chk.feed_sfrbx(p, t0)
        self.assertAlmostEqual(chk.mismatch_m(t0)["G05"], 299.8, delta=1.0)
        self.assertEqual(EphemerisChecker({}).mismatch_m(t0), {})


if __name__ == "__main__":
    unittest.main()
