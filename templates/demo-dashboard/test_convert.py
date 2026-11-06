"""python3 -m unittest test_convert  (from templates/demo-dashboard; needs ../project-repo)"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import convert_navapp as cv

sys.path.insert(0, str(cv.DEFAULT_NAVAPP_SRC))
from navapp.__main__ import main as navapp_main  # noqa: E402


def lines(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines()]


class ConvertTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run = self.tmp / "spoof.jsonl"
        navapp_main(["--scenario", "spoof", "--out", str(self.run)])

    def test_spoof_outputs(self):
        out = self.tmp / "dash"
        m = cv.convert([self.run], out, 10.0, 1e-5, cv.DEFAULT_NAVAPP_SRC, True, cv.ZONE_PAD_M)
        self.assertEqual(m["tracks"], ["truth.jsonl", "fused-spoof.jsonl", "gnss.jsonl", "ins.jsonl"])
        fused = lines(out / "fused-spoof.jsonl")
        self.assertEqual(fused[0]["header"]["schema"], cv.SCHEMA)
        self.assertTrue(fused[0]["header"]["primary"])
        pts = [r for r in fused if "lat" in r]
        self.assertEqual(len(pts), 181)
        self.assertTrue(all(r["pl_m"] > r["r95_m"] for r in pts))
        events = {(r["t"], r["event"]) for r in fused if "event" in r}
        self.assertIn((69.0, "spoof_suspected"), events)
        self.assertIn((69.0, "alarm_raised"), events)
        self.assertNotIn(1.0, {t for t, _ in events}, "init step must not produce a source switch")
        gnss = [r for r in lines(out / "gnss.jsonl") if "lat" in r]
        self.assertEqual(len(gnss), 181)
        zones = json.loads((out / "zones.geojson").read_text())
        self.assertEqual(zones["features"][0]["properties"]["kind"], "spoofing")

    def test_regenerated_truth_must_match(self):
        recs = lines(self.run)
        recs[5]["truth_east"] += 1.0
        self.run.write_text("".join(json.dumps(r) + "\n" for r in recs))
        with self.assertRaises(SystemExit):
            cv.convert([self.run], self.tmp / "bad", 10.0, 1e-5, cv.DEFAULT_NAVAPP_SRC, True, cv.ZONE_PAD_M)


if __name__ == "__main__":
    unittest.main()
