"""Traffic archive merge rules (stdlib only, no network)."""
import unittest

import traffic

SINCE = "2026-11-16"
REPO_INFO = {"stargazers_count": 3, "forks_count": 1}


def rows(*triples):
    return [{"timestamp": f"{d}T00:00:00Z", "count": c, "uniques": u} for d, c, u in triples]


def build(stored, clones, views=(), uniques=0):
    return traffic.build(stored, {"count": 0, "uniques": uniques, "clones": rows(*clones)},
                         {"count": 0, "uniques": 0, "views": rows(*views)}, [], REPO_INFO, "o/r", "2026-12-01", SINCE)


class TrafficTests(unittest.TestCase):
    def test_days_before_tracking_start_are_dropped(self):
        out = build(None, [("2026-11-09", 966, 257), ("2026-11-16", 4, 2)])
        self.assertEqual([d["date"] for d in out["days"]], ["2026-11-16"])
        self.assertEqual(out["totals"]["clones"], 4)

    def test_day_outside_the_window_keeps_its_stored_value(self):
        first = build(None, [("2026-11-16", 4, 2), ("2026-11-17", 1, 1)])
        later = build(first, [("2026-11-17", 6, 3), ("2026-11-18", 2, 2)])
        self.assertEqual([(d["date"], d["clones"]) for d in later["days"]],
                         [("2026-11-16", 4), ("2026-11-17", 6), ("2026-11-18", 2)])
        self.assertEqual(later["totals"]["clones"], 12)

    def test_clones_and_views_share_one_day_row(self):
        out = build(None, [("2026-11-16", 4, 2)], views=[("2026-11-16", 9, 5)])
        self.assertEqual(out["days"], [{"date": "2026-11-16", "clones": 4, "unique_cloners": 2,
                                        "views": 9, "unique_visitors": 5}])

    def test_window_uniques_not_measured_while_window_predates_tracking(self):
        mixed = build(None, [("2026-11-09", 966, 257), ("2026-11-16", 4, 2)], uniques=259)
        self.assertIsNone(mixed["window_14d"]["unique_cloners"])
        clean = build(None, [("2026-11-16", 4, 2), ("2026-11-17", 1, 1)], uniques=3)
        self.assertEqual(clean["window_14d"]["unique_cloners"], 3)
        self.assertIsNone(clean["window_14d"]["unique_visitors"])


if __name__ == "__main__":
    unittest.main()
