"""FDE logic on synthetic banks (stdlib), checks on the committed results (stdlib), bank pieces (numpy).

    python3 -m unittest discover
"""
import itertools
import json
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fde  # noqa: E402

RESULT = os.path.join(HERE, "results", "fde_result.json")
PRIORS = {"a": 1e-2, "b": 1e-2, "c": 1e-3, "d": 1e-3}
DR_SIGMA = 60.0       # dead-reckoning prior around the truth (origin)
SIGMA = {"a": 2.0, "b": 4.0, "c": 4.0, "d": 6.0}

try:
    import numpy as np
    import run_fde
    HAVE_NP = True
except ImportError:
    HAVE_NP = False


def snapshot_bank(bias, sources=("a", "b", "c", "d")):
    """Least-squares bank: each subset is the information-weighted mean of the DR prior and its fixes."""
    out = {}
    for n in range(len(sources) + 1):
        for sub in itertools.combinations(sources, n):
            w0 = 1 / DR_SIGMA ** 2
            ws = {s: 1 / SIGMA[s] ** 2 for s in sub}
            tot = w0 + sum(ws.values())
            x = sum(ws[s] * bias.get(s, (0, 0))[0] for s in sub) / tot
            y = sum(ws[s] * bias.get(s, (0, 0))[1] for s in sub) / tot
            out[frozenset(sub)] = (x, y, [[1 / tot, 0.0], [0.0, 1 / tot]])
    return out


def run_static(bias_by_k, sources=("a", "b", "c", "d"), **kw):
    bank = [(k, snapshot_bank(b, sources)) for k, b in enumerate(bias_by_k)]
    truth = {k: (0.0, 0.0) for k in range(len(bias_by_k))}
    return fde.run(bank, truth, sources, PRIORS, **kw)


class TestSubsetFde(unittest.TestCase):
    def test_fault_free_quiet(self):
        rows = run_static([{}] * 5)
        self.assertFalse(any(r["events"] for r in rows))
        self.assertTrue(all(0 < r["hpl"] < 50 for r in rows))

    def test_single_fault_excluded(self):
        rows = run_static([{"b": (40.0, 0.0)}] * 3)
        self.assertIn("exclude:b", rows[0]["events"])
        self.assertEqual(rows[-1]["admitted"], "a+c+d")
        self.assertFalse(rows[-1]["alert"])

    def test_detect_only_never_excludes(self):
        rows = run_static([{"b": (40.0, 0.0)}] * 3, mode="detect")
        self.assertTrue(all(r["alert"] for r in rows))
        self.assertTrue(all(r["admitted"] == "a+b+c+d" for r in rows))

    def test_two_sources_ambiguous_is_unavailable(self):
        rows = run_static([{"b": (40.0, 0.0)}] * 3, sources=("a", "b"))
        self.assertIn("alert:ambiguous", rows[0]["events"])
        self.assertFalse(any(e.startswith("exclude:") for r in rows for e in r["events"]))
        self.assertTrue(all(r["alert"] for r in rows))

    def test_dual_fault(self):
        bias = {"a": (40.0, 0.0), "b": (0.0, -40.0)}
        one = run_static([bias] * 3, max_faults=1)
        self.assertTrue(one[0]["alert"])
        self.assertFalse(any(e.startswith("exclude:") for r in one for e in r["events"]))
        two = run_static([bias] * 3, max_faults=2)
        self.assertIn("exclude:a+b", two[0]["events"])
        self.assertEqual(two[-1]["admitted"], "c+d")

    def test_dual_hypotheses_raise_pl(self):
        one = run_static([{}], max_faults=1)[0]["hpl"]
        two = run_static([{}], max_faults=2)[0]["hpl"]
        self.assertGreater(two, one)

    def test_readmission_after_hold_and_probation(self):
        n_fault = 3
        n = n_fault + fde.HOLD_EPOCHS + fde.PROBATION_EPOCHS + 2
        rows = run_static([{"b": (40.0, 0.0)}] * n_fault + [{}] * (n - n_fault))
        readmit = [r["k"] for r in rows if "readmit:b" in r["events"]]
        self.assertEqual(len(readmit), 1)
        self.assertGreaterEqual(readmit[0], fde.HOLD_EPOCHS)
        self.assertEqual(rows[-1]["admitted"], "a+b+c+d")


class TestEvaluate(unittest.TestCase):
    def rows(self, events_at):
        return [{"k": k, "hpe": 1.0, "hpl": 20.0, "alert": False, "events": events_at.get(k, [])} for k in range(100)]

    def test_wrong_exclusion(self):
        e = fde.evaluate(self.rows({50: ["detect", "exclude:a"]}), {"b": (40, 100)})
        self.assertEqual(e["outcome"], "wrong_exclusion")
        self.assertEqual(e["latency"], 10)

    def test_correct_and_partial(self):
        w = {"a": (40, 100), "b": (40, 100)}
        self.assertEqual(fde.evaluate(self.rows({45: ["detect", "exclude:a+b"]}), w)["outcome"], "correct_exclusion")
        self.assertEqual(fde.evaluate(self.rows({45: ["detect", "exclude:a"]}), w)["outcome"], "partial_exclusion")

    def test_hmi_counted_only_when_available(self):
        rows = [{"k": 0, "hpe": 60.0, "hpl": 30.0, "alert": False, "events": []},
                {"k": 1, "hpe": 60.0, "hpl": 30.0, "alert": True, "events": []}]
        self.assertEqual(fde.evaluate(rows, {})["per_al"]["50"]["HMI"], 1)


@unittest.skipIf(not os.path.exists(RESULT), "results/fde_result.json not present")
class TestCommittedResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULT) as fh:
            cls.r = json.load(fh)["results"]

    def test_subset_fde_never_hmi_nor_mi(self):
        for sc, cfgs in self.r.items():
            for c, agg in cfgs.items():
                if "altpnt" in c:
                    continue
                for al, x in agg["per_al"].items():
                    self.assertEqual((x["HMI"], x["MI"]), (0, 0), (sc, c, al))

    def test_reproduces_two_source_three_source_hmi(self):
        self.assertEqual(self.r["trn_ambiguity"]["alt3_altpnt_maxsep"]["per_al"]["50"]["HMI"], 19)

    def test_spoof_excluded_and_availability_recovers(self):
        f, d = self.r["gnss_spoof"]["4src_fde1"], self.r["gnss_spoof"]["4src_detect"]
        self.assertEqual(f["correct_exclusion_runs"], 10)
        self.assertGreater(f["per_al"]["50"]["avail_post_onset_pct"], d["per_al"]["50"]["avail_post_onset_pct"])

    def test_nominal_quiet(self):
        for c, agg in self.r["nominal"].items():
            self.assertEqual(agg["outcomes"], {"quiet": 10}, c)


@unittest.skipIf(not HAVE_NP, "needs numpy and the two-source sample's imports")
class TestBankPieces(unittest.TestCase):
    def test_subsets_cover_power_set(self):
        s = run_fde.subsets(run_fde.SOURCES4)
        self.assertEqual(len(s), 16)
        self.assertIn(frozenset(), s)

    def test_spoof_drag_grows_linearly(self):
        en = np.zeros((40, 2))
        ctx = {"en": en, "start": 5}
        clean = run_fde.gnss_fixes(ctx, 0)
        bad = run_fde.gnss_fixes(ctx, 0, onset=20)
        self.assertEqual(clean[19], bad[19])
        d = math.hypot(bad[30][0] - clean[30][0], bad[30][1] - clean[30][1])
        self.assertAlmostEqual(d, run_fde.SPOOF["rate_mps"] * 11, places=6)

    def test_wrong_place_window(self):
        vis = {k: (0.0, 0.0) for k in range(90, 140)}
        out = run_fde.wrong_place_fixes(vis)
        a, b = run_fde.WRONG_PLACE["frames"]
        self.assertEqual(float(np.linalg.norm(out[a - 1])), 0.0)
        self.assertAlmostEqual(float(np.linalg.norm(out[a])), run_fde.WRONG_PLACE["offset_m"])
        self.assertEqual(float(np.linalg.norm(out[b])), 0.0)


if __name__ == "__main__":
    unittest.main()
