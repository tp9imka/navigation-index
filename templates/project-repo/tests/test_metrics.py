import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("metrics", Path(__file__).parents[1] / "eval" / "metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


def rec(t, e, n, te=None, tn=None, sigma=1.0, alarm=False):
    return {"t": t, "east": e, "north": n, "truth_east": te, "truth_north": tn, "sigma_h": sigma, "alarm": alarm}


def write(meta, recs):
    fh = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    fh.write(json.dumps({"meta": meta}) + "\n")
    for r in recs:
        fh.write(json.dumps(r) + "\n")
    fh.close()
    return Path(fh.name)


class Metrics(unittest.TestCase):
    def test_ate_by_hand(self):
        recs = [rec(0, 3, 4, 0, 0), rec(1, 0, 0, 0, 0)]
        out = metrics.ate(recs)
        self.assertAlmostEqual(out["ate_rmse_m"], (25 / 2) ** 0.5)
        self.assertEqual(out["ate_max_m"], 5.0)

    def test_rpe_constant_offset_is_zero(self):
        recs = [rec(t, t + 5.0, 2.0, t, 0.0) for t in range(30)]
        self.assertAlmostEqual(metrics.rpe(recs, 10)["rpe_rmse_m"], 0.0)

    def test_detection_and_false_alarms(self):
        recs = [rec(t, 0, 0, alarm=(t in (3, 14, 15))) for t in range(20)]
        out = metrics.detection({"attack_onset_s": 10}, recs)
        self.assertEqual(out["time_to_detect_s"], 4)
        self.assertEqual(out["false_alarm_epochs"], 1)
        self.assertEqual(metrics.detection({"attack_onset_s": 10}, recs[:12])["time_to_detect_s"], "missed")

    def test_availability_and_misleading(self):
        recs = [rec(0, 0, 0, 0, 0, sigma=1.0), rec(1, 50, 0, 0, 0, sigma=1.0),
                rec(2, 0, 0, 0, 0, sigma=100.0), rec(3, 50, 0, 0, 0, sigma=1.0, alarm=True)]
        out = metrics.availability(recs, 10.0)
        self.assertEqual(out["availability_pct"], 75.0)
        self.assertAlmostEqual(out["misleading_pct"], 100 / 3)

    def test_no_truth_reads_not_measured(self):
        path = write({"kind": "field"}, [rec(t, t, 0) for t in range(5)])
        row = metrics.evaluate(path, 10.0, 2.0)
        self.assertIsNone(row["ate_rmse_m"])
        self.assertIn("not measured", metrics.table([row], 10.0, 2.0))
        self.assertEqual(row["availability_pct"], 100.0)


if __name__ == "__main__":
    unittest.main()
