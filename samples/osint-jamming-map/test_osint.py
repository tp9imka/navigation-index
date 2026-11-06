"""Offline unit tests: python -m unittest test_osint"""

import unittest

try:
    import numpy as np

    import adsb_hexmap as A
    import s1_rfi as S
    HAVE_DEPS, MISSING = True, ""
except ImportError as e:  # plain python3 without the venv (h3, numpy, rasterio, scipy)
    HAVE_DEPS, MISSING = False, str(e)

needs_venv = unittest.skipUnless(HAVE_DEPS, f"needs the sample venv: {MISSING}")

RFI_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rfi><adsHeader><polarisation>VH</polarisation><startTime>2026-10-01T04:51:03.000000</startTime>
<stopTime>2026-10-01T04:51:28.000000</stopTime></adsHeader>
<rfiMitigationApplied>TimeFrequency</rfiMitigationApplied>
<rfiDetectionFromNoiseReportList count="2">
<rfiDetectionFromNoiseReport><swath>IW1</swath><noiseSensingTime>2026-10-01T04:51:05.0</noiseSensingTime>
<rfiDetected>true</rfiDetected><maxKLDivergence>3.1e+05</maxKLDivergence><maxFisherZ>40.0</maxFisherZ>
<maxRfiPsd>1.0e+02</maxRfiPsd></rfiDetectionFromNoiseReport>
<rfiDetectionFromNoiseReport><swath>IW3</swath><noiseSensingTime>2026-10-01T04:51:10.0</noiseSensingTime>
<rfiDetected>false</rfiDetected><maxKLDivergence>3.0</maxKLDivergence><maxFisherZ>3.0</maxFisherZ>
<maxRfiPsd>0.0</maxRfiPsd></rfiDetectionFromNoiseReport></rfiDetectionFromNoiseReportList>
<rfiBurstReportList count="1"><rfiBurstReport><swath>IW1</swath><azimuthTime>2026-10-01T04:51:03.5</azimuthTime>
<inBandOutBandPowerRatio>5.5</inBandOutBandPowerRatio></rfiBurstReport></rfiBurstReportList></rfi>"""


def ac(hex_, lat, lon, nacp, typ="adsb_icao", **kw):
    return {"hex": hex_, "lat": lat, "lon": lon, "nac_p": nacp, "type": typ, "seen_pos": 1.0, **kw}


@needs_venv
class AdsbTest(unittest.TestCase):
    def test_percent_bad_formula(self):
        self.assertEqual(A.percent_bad(10, 0), 0.0)
        self.assertEqual(A.percent_bad(9, 1), 0.0)  # one bad aircraft is not a signal
        self.assertAlmostEqual(A.percent_bad(8, 2), 10.0)

    def test_levels(self):
        self.assertEqual(A.level(50.0, 2), "no-data")
        self.assertEqual(A.level(11.0, 10), "red")
        self.assertEqual(A.level(5.0, 10), "yellow")
        self.assertEqual(A.level(1.0, 10), "green")

    def test_classify(self):
        self.assertTrue(A.classify(ac("a", 55, 20, 0)))
        self.assertFalse(A.classify(ac("a", 55, 20, 9)))
        self.assertIsNone(A.classify(ac("a", 55, 20, None)))
        self.assertIsNone(A.classify(ac("a", 55, 20, 0, typ="tisb_icao")))
        self.assertIsNone(A.classify(ac("a", 55, 20, 0, seen_pos=60.0)))
        self.assertTrue(A.classify(ac("a", 55, 20, 0, typ="mlat", mlat=["lat", "lon", "nic", "rc"])))
        self.assertTrue(A.classify(ac("a", 55, 20, 10, gpsOkBefore=1.0)))

    def test_aircraft_counted_once_per_hex(self):
        snaps = [{"now": 0.0, "aircraft": [ac("a", 55.0, 20.0, 0), ac("b", 55.0, 20.0, 9)]},
                 {"now": 60.0, "aircraft": [ac("a", 55.0, 20.0, 9), ac("b", 55.0, 20.0, 9)]}]
        hexes, points = A.aggregate(snaps)
        (row,) = A.summarize(hexes)
        self.assertEqual((row["n_aircraft"], row["n_bad"]), (2, 1))
        self.assertEqual(len(points), 4)

    def test_mlat_nic_ignored(self):
        snaps = [{"now": 0.0, "aircraft": [ac("a", 55, 20, 9, typ="mlat", nic=0, mlat=["lat", "lon", "nic"])]}]
        (row,) = A.summarize(A.aggregate(snaps)[0])
        self.assertEqual((row["n_nic_bad"], row["n_mlat_position"]), (0, 1))


@needs_venv
class S1Test(unittest.TestCase):
    def test_parse_rfi_xml(self):
        x = S.parse_rfi_xml(RFI_XML)
        self.assertEqual(x["mitigation"], "TimeFrequency")
        self.assertEqual([r["detected"] for r in x["noise"]], [True, False])
        self.assertEqual(x["bursts"][0]["in_out_ratio"], 5.5)

    def test_zscore_flags_only_the_anomaly(self):
        rng = np.random.default_rng(1)
        lat = np.full((4, 4), 54.005, np.float32)
        lon = np.full((4, 4), 20.005, np.float32)
        grid = (54.0, 20.0, 1, 1)
        stack = [rng.normal(0, 1, (4, 4)).astype(np.float32) for _ in range(10)]
        acc = [S.accumulate(r, lat, lon, grid) for r in stack]
        tot = [sum(a[i] for a in acc) for i in range(3)]
        bright = stack[0].copy()
        bright[0, 0] = 25.0
        z = S.zscores(bright, lat, lon, grid, *[tot[i] - acc[0][i] for i in range(3)])
        self.assertGreater(z[0, 0], S.Z_THRESHOLD)
        self.assertEqual(int((z > S.Z_THRESHOLD).sum()), 1)

    def test_rank_requires_beating_every_other_date(self):
        hx = "851f1d4bfffffff"
        n = S.MIN_HEX_PX
        per = {"d0": {hx: (n, n // 10, 9.0)}, "d1": {hx: (n, 1, 4.0)}, "d2": {hx: (n, 2, 4.0)}, "d3": {hx: (n, 0, 1.0)}}
        self.assertTrue(S.rank_hexes(per, "d0")[0]["candidate"])
        per["d3"] = {hx: (n, n // 5, 9.0)}
        self.assertFalse(S.rank_hexes(per, "d0")[0]["candidate"])


if __name__ == "__main__":
    unittest.main()
