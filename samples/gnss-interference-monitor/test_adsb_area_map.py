"""Run: python3 -m unittest -v test_adsb_area_map.py"""

import unittest

from adsb_area_map import aircraft_cells, percent_bad, summarize


def ac(hex_id, lat, lon, nac_p=9, **extra):
    return {"hex": hex_id, "lat": lat, "lon": lon, "seen_pos": 1.0, "nac_p": nac_p, **extra}


class AreaMapTests(unittest.TestCase):
    def test_gpsjam_formula_discounts_one_bad_aircraft(self):
        self.assertEqual(percent_bad(n_good=9, n_bad=1), 0.0)
        self.assertAlmostEqual(percent_bad(n_good=8, n_bad=2), 10.0)

    def test_aircraft_counted_once_per_cell_and_bad_wins(self):
        snaps = [{"aircraft": [ac("a1", 10.1, 20.1)]},
                 {"aircraft": [ac("a1", 10.2, 20.2, nac_p=2)]}]
        self.assertEqual(aircraft_cells(snaps), {(10.0, 20.0): {"a1": True}})

    def test_gps_ok_before_marks_bad(self):
        cells = aircraft_cells([{"aircraft": [ac("a1", 10.1, 20.1, gpsOkBefore=1.0)]}])
        self.assertTrue(cells[(10.0, 20.0)]["a1"])

    def test_aircraft_without_quality_field_is_not_counted_as_good(self):
        snap = {"aircraft": [{"hex": "~01", "lat": 10.1, "lon": 20.1, "seen_pos": 1.0}]}
        self.assertEqual(aircraft_cells([snap]), {})

    def test_stale_position_ignored(self):
        snap = {"aircraft": [ac("a1", 10.1, 20.1, nac_p=0) | {"seen_pos": 120.0}]}
        self.assertEqual(aircraft_cells([snap]), {})

    def test_red_cell(self):
        acs = [ac(f"g{i}", 10.5, 20.5) for i in range(6)] + \
              [ac(f"b{i}", 10.5, 20.5, nac_p=0) for i in range(4)]
        (row,) = summarize(aircraft_cells([{"aircraft": acs}]))
        self.assertEqual(row[-1], "red")


if __name__ == "__main__":
    unittest.main()
