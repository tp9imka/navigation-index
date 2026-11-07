import importlib.util
import tempfile
import unittest
from pathlib import Path

import recording


class RecordingTests(unittest.TestCase):
    def test_round_trip_and_error_metric(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'poses.jsonl'
            recording.write_jsonl(path, recording.demo_records())
            rows = recording.read_jsonl(path)
            result = recording.metrics(rows)
            self.assertEqual(result['epochs'], 101)
            self.assertEqual(result['duration_s'], 10)
            self.assertAlmostEqual(result['position_rmse_m'], 0.5)
            self.assertEqual(result['frame'], 'local_enu')

    def test_bad_timestamps_frames_and_nonfinite_values_fail(self):
        for change in ({'t_ns': -1}, {'t_ns': True}, {'frame': 'ned'}, {'position_m': [float('nan'), 0, 0]},
                       {'position_m': [1, 2]}, {'truth_m': [float('inf'), 0, 0]}):
            rows = recording.demo_records()
            rows[1].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                recording.metrics(rows)
        rows = recording.demo_records()
        rows[1]['t_ns'] = rows[0]['t_ns']
        with self.assertRaises(ValueError):
            recording.metrics(rows)

    @unittest.skipUnless(importlib.util.find_spec('mcap'), 'optional mcap package not installed')
    def test_mcap_round_trip_preserves_time_and_values(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'poses.mcap'
            rows = recording.demo_records()
            recording.write_mcap(path, rows)
            self.assertEqual(recording.read_mcap(path), rows)


if __name__ == '__main__':
    unittest.main()
