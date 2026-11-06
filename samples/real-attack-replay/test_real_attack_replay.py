"""Tests on the synthetic VAARA-shaped fixture (make_fixture.py). Stdlib only; the pyubx2 cross-check is
skipped without it. Run: python3 -m unittest -v test_real_attack_replay.py"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import make_fixture as fx
import replay
import spp_eval
from ubx_nmea_epochs import frames, raw_epochs, to_epochs

try:
    from pyubx2 import UBXReader
except ImportError:
    UBXReader = None

HERE = Path(__file__).resolve().parent
FIXTURE_LABELS = HERE / "fixtures" / "labels_fixture.json"
BUF = fx.build()


def fixture_spec():
    return json.loads(FIXTURE_LABELS.read_text())["files"][0]


def windows_by_test(argv):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "vaara_shaped.ubx").write_bytes(BUF)
        out = Path(d, "r.json")
        replay.main(["--data", d, "--labels", str(FIXTURE_LABELS), "--out", str(out), "--quiet", *argv])
        res = json.loads(out.read_text())
    return {w["test"]: w for w in res["results"][0]["windows"]}, res["results"][0]


class Framing(unittest.TestCase):
    def test_counts_and_garbage(self):
        kinds = [f[0] for f in frames(BUF)]
        self.assertEqual(kinds.count("ubx"), fx.N_EPOCHS)  # trailing truncated frame is dropped
        nmea = [f[1] for f in frames(BUF) if f[0] == "nmea"]
        self.assertFalse(any("\x97" in s for s in nmea))
        self.assertEqual(sum(s.startswith("GNGGA") for s in nmea), fx.N_EPOCHS)

    @unittest.skipIf(UBXReader is None, "pyubx2 not installed")
    def test_ubx_frames_parse_with_pyubx2(self):
        for kind, cls, mid, payload in (f for f in frames(BUF) if f[0] == "ubx"):
            msg = UBXReader.parse(fx.ubx(cls, mid, payload), validate=1)
            self.assertEqual(msg.identity[:3], "RXM")


class Epochs(unittest.TestCase):
    def test_l1_only_and_no_sbas(self):
        r = next(raw_epochs(BUF))
        self.assertEqual(len(r.cn0), len(fx.SVS))
        self.assertNotIn("G49", r.cn0)
        self.assertEqual(set(k[0] for k in r.cn0), {"G", "E", "R"})
        self.assertAlmostEqual(r.cn0["G02"], 48, delta=4)  # L1 value, not the L2 one (30)

    def test_time_axis(self):
        eps = list(to_epochs(BUF, "2024-09-12"))
        self.assertEqual(len(eps), fx.N_EPOCHS)
        ts = [e.t for e, _ in eps]
        self.assertEqual(ts, [fx.START_UTC + k for k in range(fx.N_EPOCHS)])
        jumps = [(k, i["time_jump_s"]) for k, (_, i) in enumerate(eps) if i["time_jump_s"]]
        a, b = fx.WINDOWS["time_jump"]
        self.assertEqual(jumps, [(a, fx.TIME_JUMP_S), (b + 1, -fx.TIME_JUMP_S)])  # the no-time gap adds none
        self.assertIsNone(eps[fx.WINDOWS["no_time"][0]][1]["rx_t"])
        self.assertFalse(eps[a][0].has_fix)
        self.assertTrue(eps[a + 10][0].has_fix)

    def test_position_and_hdop(self):
        ep, _ = next(to_epochs(BUF, "2024-09-12"))
        self.assertAlmostEqual(ep.lat, fx.LAT, places=4)
        self.assertAlmostEqual(ep.lon, fx.LON, places=4)
        self.assertEqual(ep.hdop, 0.52)


class ReplayFindings(unittest.TestCase):
    """The three effects seen on the real logs, reproduced on the fixture."""

    def test_staircase_evades_cn0_drop(self):
        for argv in (["--no-pos-drift"], ["--no-pos-drift", "--baseline-max-score", "0.3"]):
            w, _ = windows_by_test(argv)
            self.assertFalse(w["staircase"]["detected"], argv)

    def test_baseline_lockout_hides_step_drop(self):
        w, _ = windows_by_test(["--no-pos-drift"])
        self.assertFalse(w["step_drop"]["detected"])
        self.assertGreater(w["staircase"]["epochs"], 0)
        w, _ = windows_by_test(["--no-pos-drift", "--baseline-max-score", "0.3"])
        self.assertTrue(w["step_drop"]["detected"])
        self.assertLessEqual(w["step_drop"]["ttd_s"], 1)
        self.assertIn("cn0_drop", w["step_drop"]["detector_epochs"])

    def test_receiver_time_jump_reaches_clock_jump(self):
        w, _ = windows_by_test(["--no-pos-drift"])
        self.assertIn("clock_jump", w["time_jump"]["detector_epochs"])
        self.assertEqual(w["time_jump"]["max_time_jump_s"], fx.TIME_JUMP_S)
        w, _ = windows_by_test(["--no-pos-drift", "--no-rx-clock"])
        self.assertNotIn("clock_jump", w["time_jump"]["detector_epochs"])
        self.assertIn("lost_fix", w["time_jump"]["detector_epochs"])

    def test_quiet_window_stays_clean(self):
        for argv in ([], ["--static-ref"], ["--no-pos-drift", "--baseline-max-score", "0.3"]):
            w, res = windows_by_test(argv)
            self.assertFalse(w["quiet"]["detected"], argv)
            self.assertEqual(res["quiet"]["alarm_raises"], 0, argv)

    def test_static_position_error_reported(self):
        _, res = windows_by_test(["--static-ref"])
        per = res["static_fix_error"]["per_window"]
        self.assertLess(per["outside-windows"]["p95_m"], 5.0)


class SppEval(unittest.TestCase):
    POS = """% header
2331 371883.000   69.275760000   15.967890000    45.0   5  16 0 0 0 0 0 0 0.00 0.0
2331 371884.000   69.275760000   15.967890000    45.0   5  16 0 0 0 0 0 0 0.00 0.0
"""

    def test_read_pos_gps_to_utc(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "x.pos")
            p.write_text(self.POS)
            pts = spp_eval.read_pos(p)
        self.assertEqual(pts[0][0], 1726125465.0)  # 2024-09-12 07:17:45 UTC
        self.assertEqual(pts[0][3], 16)

    def test_static_window_errors(self):
        spec = fixture_spec()
        t0 = fx.START_UTC
        spp = [(t0 + k, fx.LAT, fx.LON + (0.001 if fx.WINDOWS['step_drop'][0] <= k <= fx.WINDOWS['step_drop'][1] else 0.0)) for k in range(fx.N_EPOCHS)]
        rows = {r["test"]: r for r in spp_eval.evaluate(spec, spp, None)}
        self.assertAlmostEqual(rows["step_drop"]["spp"]["median_m"], 39.4, delta=0.5)  # 0.001 deg lon at 69.3 N
        self.assertEqual(rows["staircase"]["spp"]["max_m"], 0.0)

    def test_read_spp_clock(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "x.stat")
            p.write_text("$POS,2331,371883.000,5,0,0,0,0,0,0\n$CLK,2331,371883.000,5,1,3182417.9,1,2,3,0,0\n"
                         "$CLK,2331,371884.000,5,1,0.000,1,2,3,0,0\n")
            clk = replay.read_spp_clock(p)
        self.assertEqual(clk, {1726125465: 3182417.9})


if __name__ == "__main__":
    unittest.main()
