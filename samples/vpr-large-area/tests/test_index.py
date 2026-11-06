import json
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

try:
    import numpy as np
    import index as vpr
except ImportError:
    vpr = None


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


@unittest.skipIf(vpr is None, "numpy not installed")
class TileIndexTest(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(1)
        self.desc = unit(rng.normal(size=(200, 32)).astype(np.float32))
        self.meta = np.c_[rng.uniform(0, 7000, (200, 2)), np.zeros(200)]

    def test_self_query_ranks_first(self):
        idx = vpr.TileIndex(self.desc, self.meta)
        sims, ids = idx.search(self.desc[:5], 3)
        self.assertEqual(ids[:, 0].tolist(), [0, 1, 2, 3, 4])
        np.testing.assert_allclose(sims[:, 0], 1.0, atol=1e-5)

    def test_numpy_matches_faiss(self):
        # separate process: faiss and torch wheels both bundle libomp and abort when loaded together on macOS
        code = (
            "import sys, json, numpy as np; sys.path.insert(0, sys.argv[1]); import index\n"
            "try:\n import faiss\nexcept ImportError:\n print('null'); raise SystemExit\n"
            "r = np.random.default_rng(1); d = r.normal(size=(200, 32)).astype(np.float32)\n"
            "d /= np.linalg.norm(d, axis=1, keepdims=True); m = np.zeros((200, 3))\n"
            "q = r.normal(size=(4, 32)).astype(np.float32); q /= np.linalg.norm(q, axis=1, keepdims=True)\n"
            "a = index.TileIndex(d, m, backend='faiss').search(q, 5)[1]; b = index.TileIndex(d, m).search(q, 5)[1]\n"
            "print(json.dumps([a.tolist(), b.tolist()]))\n")
        out = subprocess.run([sys.executable, "-c", code, str(HERE)], capture_output=True, text=True, check=True)
        res = json.loads(out.stdout)
        if res is None:
            self.skipTest("faiss not installed")
        self.assertEqual(res[0], res[1])

    def test_places_dedup_across_yaws(self):
        aug = vpr.TileIndex(np.concatenate([self.desc, self.desc * 0.999]),
                            np.concatenate([self.meta, np.c_[self.meta[:, :2], np.full(200, 45.0)]]))
        ids, sims, _ = aug.search_places(self.desc[7], 5)
        places = {tuple(aug.meta[i, :2]) for i in ids}
        self.assertEqual(len(places), 5)
        self.assertEqual(tuple(aug.meta[ids[0], :2]), tuple(self.meta[7, :2]))

    def test_multi_variant_query_reports_variant(self):
        idx = vpr.TileIndex(self.desc, self.meta)
        noise = unit(np.random.default_rng(3).normal(size=(3, 32)).astype(np.float32))
        q = np.stack([noise[0], noise[1], self.desc[42], noise[2]])
        ids, _, var = idx.search_places(q, 1)
        self.assertEqual(ids[0], 42)
        self.assertEqual(var[0], 2)

    def test_place_radius_merges_neighbours(self):
        meta = np.array([[0, 0, 0], [10, 0, 0], [500, 0, 0]], float)
        d = unit(np.array([[1, 0], [0.99, 0.1], [0.9, 0.4]], np.float32))
        idx = vpr.TileIndex(d, meta)
        ids, _, _ = idx.search_places(np.array([1, 0], np.float32), 2, place_radius_m=50)
        self.assertEqual(ids.tolist(), [0, 2])

    def test_nbytes(self):
        self.assertEqual(vpr.TileIndex(self.desc, self.meta).nbytes, 200 * 32 * 4)


if __name__ == "__main__":
    unittest.main()
