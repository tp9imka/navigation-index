"""Replay the synthetic UBX capture through ubx_monitor and check the episodes are found. Needs pyubx2."""

import contextlib
import io
import os
import random
import tempfile
import unittest

try:
    import gen_synthetic_ubx as gen
    import ubx_monitor
except ImportError:  # pyubx2 not installed; the stdlib scorer tests still run
    gen = ubx_monitor = None


@unittest.skipIf(gen is None, "requires pyubx2 (see requirements.txt)")
class ReplayTest(unittest.TestCase):
    def test_jamming_and_spoofing_episodes_detected(self):
        rng = random.Random(gen.SEED)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.ubx")
            with open(path, "wb") as fh:
                for k in range(gen.DURATION_S):
                    for msg in gen.epoch_messages(k, rng):
                        fh.write(msg.serialize())
            out = io.StringIO()
            with open(path, "rb") as fh, contextlib.redirect_stdout(out):
                ubx_monitor.run(fh)
        lines = out.getvalue().splitlines()
        rows = [l[2:].split() for l in lines if l.startswith("t=")]
        verdict = {round(float(r[0]) - gen.START_ITOW_MS / 1000): r[1] for r in rows}
        self.assertEqual(len(verdict), gen.DURATION_S)
        self.assertTrue(all(verdict[k] == "clean" for k in range(gen.JAM[0])))
        self.assertTrue(all(verdict[k] == "jamming" for k in range(*gen.JAM)))
        self.assertTrue(all(verdict[k] == "spoofing" for k in range(*gen.SPOOF)))
        self.assertTrue(all(verdict[k] == "clean" for k in range(gen.SPOOF[1] + 1, gen.DURATION_S)))


if __name__ == "__main__":
    unittest.main()
