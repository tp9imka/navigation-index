"""Run: python3 -m unittest -v test_compare_pos.py"""

import math
import os
import random
import tempfile
import unittest

import compare_pos as cp

# Excerpt of the NGS sheet for CORS P731 (ITRF2020, epoch 2020.0), same layout as the real file.
P731_SHEET = """\
| ITRF2020 POSITION (EPOCH 2020.0)                                            |
| Computed in Apr 2025 using data through gpswk 2237.                         |
|     X =  -2432862.854 m     latitude    =  41 19 57.05111 N                 |
|     Y =  -4134674.615 m     longitude   = 120 28 21.95213 W                 |
|     Z =   4191141.557 m     ellipsoid height = 1391.288   m                 |
| ITRF2020 VELOCITY                                                           |
|     VX =  -0.0177 m/yr      northward =  -0.0066 m/yr                       |
|     VY =   0.0060 m/yr      eastward  =  -0.0183 m/yr                       |
|     VZ =  -0.0054 m/yr      upward    =  -0.0007 m/yr                       |
| NAD_83 (2011) POSITION (EPOCH 2010.0)                                       |
|     X =  -2432861.883 m     latitude    =  41 19 57.03905 N                 |
"""
SHEET_LAT = 41 + 19 / 60 + 57.05111 / 3600
SHEET_LON = -(120 + 28 / 60 + 21.95213 / 3600)
SHEET_H = 1391.288


def write(text):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as fh:
        fh.write(text)
    return path


class ComparePosTests(unittest.TestCase):
    def setUp(self):
        self.sheet = write(P731_SHEET)

    def tearDown(self):
        os.remove(self.sheet)

    def test_parses_itrf_block_not_nad83(self):
        pos, vel, ref = cp.parse_ngs_coord(self.sheet)
        self.assertEqual(pos, [-2432862.854, -4134674.615, 4191141.557])
        self.assertEqual(vel, [-0.0177, 0.0060, -0.0054])
        self.assertEqual(ref, 2020.0)

    def test_geodetic_matches_sheet(self):
        lat, lon, h = cp.ecef_to_geodetic(*cp.parse_ngs_coord(self.sheet)[0])
        self.assertAlmostEqual(math.degrees(lat), SHEET_LAT, places=7)
        self.assertAlmostEqual(math.degrees(lon), SHEET_LON, places=7)
        self.assertAlmostEqual(h, SHEET_H, places=2)

    def test_velocity_propagation(self):
        x = cp.truth_at(self.sheet, 2024.0)
        self.assertAlmostEqual(x[0], -2432862.854 - 0.0177 * 4, places=6)

    def test_scores_synthetic_pos_file(self):
        truth = cp.truth_at(self.sheet, 2024.27)
        lat, lon, _ = cp.ecef_to_geodetic(*truth)
        rng = random.Random(1)
        lines = ["% program   : RNX2RTKP synthetic\n",
                 "%  GPST          x-ecef(m)      y-ecef(m)      z-ecef(m)   Q  ns\n"]
        for k in range(200):
            up = 0.5  # metres straight up
            d = [up * math.cos(lat) * math.cos(lon), up * math.cos(lat) * math.sin(lon), up * math.sin(lat)]
            x = [t + di + rng.gauss(0, 0.001) for t, di in zip(truth, d)]
            lines.append(f"2310 {216000 + 30 * k:.3f} {x[0]:.4f} {x[1]:.4f} {x[2]:.4f} {1 if k % 4 else 2} 9\n")
        pos = write("".join(lines))
        try:
            (e, n, u), h95, q = cp.score(cp.read_pos(pos), truth)
        finally:
            os.remove(pos)
        self.assertLess(max(e, n), 0.005)
        self.assertAlmostEqual(u, 0.5, places=2)
        self.assertEqual(q, {1: 150, 2: 50})


if __name__ == "__main__":
    unittest.main()
