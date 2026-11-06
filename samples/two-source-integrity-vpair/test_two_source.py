"""Unit tests (numpy/scipy, skipped without them) and checks on the committed results (stdlib only).

    python3 -m unittest test_two_source
"""
import json
import math
import os
import sys
import unittest
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RESULT = os.path.join(HERE, "results", "two_source_result.json")

try:
    import numpy as np
    import scipy  # noqa: F401
    HAVE_NP = True
except ImportError:
    HAVE_NP = False

if HAVE_NP:
    import fetch_terrain
    import run_two_source as rts
    import trn


@unittest.skipIf(not HAVE_NP, "needs numpy + scipy")
class TestTrnPieces(unittest.TestCase):
    def test_tercom_peaks_bowl(self):
        offs = np.arange(-50, 51, 10.0)
        de, dn = [a.ravel() for a in np.meshgrid(offs, offs)]
        mad = 1.0 + 0.01 * ((de - 20) ** 2 + (dn + 10) ** 2)
        b, s, sigma = trn.tercom_peaks(de, dn, mad, 10.0, 3, 30.0)
        self.assertEqual((de[b], dn[b]), (20.0, -10.0))
        self.assertGreater(math.hypot(de[s] - de[b], dn[s] - dn[b]), 30.0)
        self.assertTrue(10.0 / math.sqrt(12) <= sigma < 30.0)

    def test_tercom_sigma_grows_when_flat(self):
        offs = np.arange(-50, 51, 10.0)
        de, dn = [a.ravel() for a in np.meshgrid(offs, offs)]
        sharp = trn.tercom_peaks(de, dn, 1.0 + 0.05 * (de ** 2 + dn ** 2), 10.0, 3, 30.0)[2]
        flat = trn.tercom_peaks(de, dn, 1.0 + 0.0005 * (de ** 2 + dn ** 2), 10.0, 3, 30.0)[2]
        self.assertGreater(flat, 2 * sharp)

    def test_tercom_surface_matches_core(self):
        rng = np.random.default_rng(0)
        ref = trn.gaussian_filter(rng.normal(0, 20, (200, 200)), 3)
        te, tn = np.linspace(300, 600, 60), np.linspace(400, 500, 60)
        prof = trn.core.bilinear(ref, te + 25, tn - 15, 5.0)
        de, dn, mad = trn.tercom_surface(ref, 5.0, te, tn, prof, 100.0, 5.0)
        b = int(np.argmin(mad))
        c = trn.core.tercom_fix(ref, 5.0, te, tn, prof, 100.0, 5.0)
        self.assertEqual((de[b], dn[b]), (c[0], c[1]))
        self.assertEqual((de[b], dn[b]), (25.0, -15.0))

    def test_secondary_peak(self):
        m = np.full((41, 41), -10.0)
        m[20, 20], m[20, 30] = 0.0, -1.0
        best, second, gap = trn.secondary_peak([m], [0.0], 100.0, 200.0, 5.0, 30.0)
        self.assertEqual(tuple(best), (200.0, 300.0))
        self.assertEqual(tuple(second), (250.0, 300.0))
        self.assertAlmostEqual(gap, 1.0)

    def test_misreg_ramp_then_hold(self):
        vis = {k: np.zeros(2) for k in range(95, 160)}
        m = {"frames": (100, 150), "offset_m": 40.0, "dir_deg": 90.0, "ramp_frames": 20}
        out = rts.misreg_fixes(vis, m)
        self.assertEqual(float(np.linalg.norm(out[99])), 0.0)
        self.assertAlmostEqual(float(out[109][0]), 20.0)
        self.assertAlmostEqual(float(out[140][0]), 40.0)
        self.assertAlmostEqual(float(out[140][1]), 0.0, places=9)
        self.assertEqual(float(np.linalg.norm(out[150])), 0.0)

    def test_corridor_tiles(self):
        track = np.array([[370500.0, 5610500.0], [370600.0, 5610600.0]])
        self.assertEqual(fetch_terrain.corridor_tiles(track, 0.0), [(370, 5610)])
        self.assertEqual(len(fetch_terrain.corridor_tiles(track, 600.0)), 6)

    def test_third_source_uses_its_own_sigma(self):
        cfg = rts.rf.filter_cfg(5.0)
        x0 = [0.0] * 8
        P0 = rts.v2.mat.eye(8)
        f = rts.EkfThird(x0, P0, cfg)
        z, _, _, r = f._meas("gnss", {"gnss": (1.0, 2.0), "gnss_sigma": 17.0})
        self.assertEqual((z, r), ((1.0, 2.0), 17.0))
        self.assertEqual(f._meas("vgeo", {"vgeo": (0.0, 0.0)})[3], cfg.vgeo_r)


class TestCommittedResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULT) as fh:
            cls.r = json.load(fh)

    def nominal(self, key, cfg, al="50"):
        return self.r["nominal"][key][cfg]["per_al"][al]

    def test_second_source_makes_integrity_available(self):
        both = self.nominal("stride8_lidar5", "both")
        one = self.nominal("stride8_lidar5", "visual_only")
        self.assertGreater(both["avail_pct"], 80.0)
        self.assertLess(one["avail_pct"], 5.0)

    def test_no_hmi_in_fault_free_runs(self):
        for key, cfgs in self.r["nominal"].items():
            for name, x in cfgs.items():
                for al, p in x["per_al"].items():
                    self.assertEqual(p["HMI"], 0, (key, name, al))

    def test_two_source_attribution_follows_monitor_order(self):
        f = self.r["faults"]["lidar5"]
        first = lambda k: {x["first_attribution"][1] for x in f[k]}
        self.assertEqual(first("misreg_persistent_vis_first"), {"magnav"})
        self.assertEqual(first("misreg_persistent_trn_first"), {"vgeo"})
        self.assertTrue(all(x["detected_at"] is not None for x in f["misreg_persistent_vis_first"]))

    def test_three_source_ambiguity_has_hmi(self):
        hmi = sum(x["per_al"]["50"]["HMI"] for x in self.r["faults"]["lidar5"]["trn_ambiguity_three"])
        self.assertGreater(hmi, 0)

    def test_navdash_manifest_files_exist(self):
        nd = os.path.join(HERE, "results", "navdash")
        with open(os.path.join(nd, "manifest.json")) as fh:
            tracks = json.load(fh)["tracks"]
        for t in tracks:
            with open(os.path.join(nd, t)) as fh:
                self.assertEqual(json.loads(fh.readline())["header"]["schema"], "navdash/1")

    def test_svg_parses(self):
        ET.parse(os.path.join(HERE, "results", "pl_vs_frame.svg"))

    def test_sample_json_fields(self):
        with open(os.path.join(HERE, "sample.json")) as fh:
            s = json.load(fh)
        for k in ("id", "title", "summary", "verified", "verified_status", "deps", "first_command", "group", "shows",
                  "input", "runtime", "key_result", "concepts", "related"):
            self.assertIn(k, s)
        self.assertEqual(s["input"], "mixed")


if __name__ == "__main__":
    unittest.main()
