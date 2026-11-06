import struct
import unittest

import real_link as rl
import timing_network as tn

HAVE_DATA = rl.DATASET.is_dir()
US = tn.US

PPS_INDEXED = """0,null
1,-0.0107
2,0.0103
3,null
"""
PPS_ISO = """2024-07-04T11:50:27.866Z,1,0.00591875
2024-07-04T11:50:28.875Z,2,-0.00012125
"""
PTPD = (
    "# Timestamp, State, Clock ID, One Way Delay, Offset From Master, Slave to Master, Master to Slave, "
    "Observed Drift, Last packet Received, One Way Delay Mean, One Way Delay Std Dev, Offset From Master Mean, "
    "Offset From Master Std Dev, Observed Drift Mean, Observed Drift Std Dev, raw delayMS, raw delay\n"
    "2023-11-23 17:24:15.550122, init, \n"
    "2023-11-23 17:24:17.757543, slv, 8c0f(unknown)/1,  0.000000000,  0.000000000,  0.000000000,  0.000000000, "
    "-16180.0, I, 0, 0, 0, 0, 0, 0,  0,  0\n"
    "2023-11-23 17:43:09.746155, slv, 8c0f(unknown)/1,  0.034706970,  0.000137049,  0.042070336,  0.034679777, "
    "-2203.4, S, 0.035, 253783, -0.00015, 287946, -1660, 535,  0.034679777,  0.042070336"
    "2023-11-23 17:43:11.020843, slv, 8c0f(unknown)/1,  0.034617527,  0.000237049,  0.016306947,  0.034679777, "
    "-2066.4, D, 0.035, 253783, -0.00015, 287946, -1660, 535,  0.034679777,  0.016306947\n"
    "2023-11-23 17:43:13.109205, dsbl, \n"
)


def pcapng_one_delay_req(cap_s=1720093820.379407, origin_s=1720093820.3677533):
    """Section header, raw-IPv4 interface with 1 us resolution, one UDP 319 Delay_Req."""
    shb = struct.pack("<IIIHHq", 0x0A0D0D0A, 28, 0x1A2B3C4D, 1, 0, -1) + struct.pack("<I", 28)
    opt = struct.pack("<HHB3x", 9, 1, 6) + struct.pack("<HH", 0, 0)
    idb_body = struct.pack("<HHI", 101, 0, 0) + opt
    idb = struct.pack("<II", 1, 12 + len(idb_body)) + idb_body + struct.pack("<I", 12 + len(idb_body))
    sec = int(origin_s)
    ptp = bytes([0x01, 0x02]) + b"\x00" * 28 + struct.pack(">H", 205) + b"\x00\x00" + \
        struct.pack(">HII", 0, sec, round((origin_s - sec) * 1e9))
    udp = struct.pack(">HHHH", 319, 319, 8 + len(ptp), 0) + ptp
    ip = bytes([0x45, 0]) + struct.pack(">H", 20 + len(udp)) + b"\x00" * 5 + bytes([17]) + b"\x00\x00" + \
        bytes([10, 45, 0, 190, 10, 45, 0, 1]) + udp
    pad = ip + b"\x00" * (-len(ip) % 4)
    ts = round(cap_s * 1e6)
    epb_body = struct.pack("<IIIII", 0, ts >> 32, ts & 0xFFFFFFFF, len(ip), len(ip)) + pad
    epb = struct.pack("<II", 6, 12 + len(epb_body)) + epb_body + struct.pack("<I", 12 + len(epb_body))
    return shb + idb + epb


class Parsers(unittest.TestCase):
    def test_pps_both_layouts_and_missing(self):
        self.assertEqual(rl.parse_pps(PPS_INDEXED.splitlines()), [(0, None), (1, -0.0107), (2, 0.0103), (3, None)])
        self.assertEqual(rl.parse_pps(PPS_ISO.splitlines()), [(1, 0.00591875), (2, -0.00012125)])

    def test_filled_holds_last_and_backfills(self):
        self.assertEqual(rl.filled(rl.parse_pps(PPS_INDEXED.splitlines())), [-0.0107, -0.0107, 0.0103, 0.0103])

    def test_ptpd_glued_rows_zero_row_and_states(self):
        rows = rl.parse_ptpd(PTPD)
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0]["owd"], 0.034706970)
        self.assertAlmostEqual(rows[1]["ofm"], 0.000237049)
        self.assertAlmostEqual(rows[1]["s2m"], 0.016306947)
        self.assertAlmostEqual(rows[1]["t"] - rows[0]["t"], 1.274688, places=5)

    def test_pcapng_delay_req(self):
        msgs = rl.parse_pcapng_ptp(pcapng_one_delay_req())
        self.assertEqual(len(msgs), 1)
        cap, src, dst, mtype, seq, ots = msgs[0]
        self.assertEqual((src, dst, mtype, seq), ("10.45.0.190", "10.45.0.1", 1, 205))
        self.assertAlmostEqual(cap - ots, 0.0116537, delta=2e-6)

    def test_transit_rejects_unrelated_origin_clock(self):
        msgs = [(100.0 + i, "a", "gm", 1, i, 100.0 + i - 0.012) for i in range(10)]
        msgs += [(100.0 + i, "b", "gm", 1, i, 5.0) for i in range(10)]
        out = rl.delay_req_transit(msgs, tail=1.0)
        self.assertAlmostEqual(out["a"]["median"], 0.012, places=9)
        self.assertIn("unusable", out["b"])


class Replay(unittest.TestCase):
    def test_replay_value_loops_and_averages(self):
        s = [0.0, 1.0, 2.0, 3.0]
        self.assertEqual(tn.replay_value(s, 0, 2.0, 2.0), 2.5)
        self.assertEqual(tn.replay_value(s, 1, 3.0, 2.0), 0.5)
        self.assertEqual(rl.mirrored([1, 2, 3]), [1, 2, 3, 3, 2, 1])

    def test_constant_link_error_becomes_relay_time_error(self):
        runs = rl.replay_regional([2 * US] * 900, tn.Config(), [1], tn.HOUR, calibrate=False)
        self.assertAlmostEqual(runs[0]["relay_te"][tn.HOUR], 2 * US, delta=0.2 * US)

    def test_synthetic_replay_path_matches_sample(self):
        runs = rl.replay_regional(None, tn.Config(), [1], tn.HOUR, calibrate=False)
        self.assertLess(runs[0]["relay_max"], 1 * US)


@unittest.skipIf(not HAVE_DATA, "dataset not fetched (python3 fetch_data.py)")
class RealData(unittest.TestCase):
    def test_pps_files_and_headline(self):
        for label, (rel, _) in rl.PPS_FILES.items():
            pairs = rl.parse_pps((rl.DATASET / rel).read_text().splitlines())
            self.assertEqual(len(pairs), 900, label)
            v = [x for _, x in pairs if x is not None]
            self.assertLess(sum(abs(x) <= 1.5 * US for x in v) / len(v), 0.01, label)

    def test_ptpd_5g_sa_delay(self):
        rows = []
        for log in sorted((rl.DATASET / rl.PTPD_DIRS["5G SA private"]).glob("*.log")):
            rows += rl.settled(rl.parse_ptpd(log.read_text(errors="replace")))
        d = rl.ptpd_summary(rows)
        self.assertGreater(d["rows"], 100)
        self.assertTrue(30e-3 < d["owd"]["median"] < 40e-3)

    def test_upf_capture_delay_req(self):
        msgs = rl.parse_pcapng_ptp((rl.DATASET / rl.UPF_PCAP).read_bytes())
        self.assertEqual(sum(m[3] == 1 for m in msgs), 2 * 927)


if __name__ == "__main__":
    unittest.main()
