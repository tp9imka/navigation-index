"""Exact cosine-similarity index over L2-normalised tile descriptors (numpy, or FAISS IndexFlatIP)."""
from dataclasses import dataclass

import numpy as np



@dataclass
class TileIndex:
    """Cosine index over L2-normalised descriptors. meta rows: (east_m, north_m, yaw_deg, tile_m)."""
    desc: np.ndarray
    meta: np.ndarray

    backend: str = "numpy"

    def __post_init__(self):
        self.desc = np.ascontiguousarray(self.desc, np.float32)
        self._faiss = None
        if self.backend == "faiss":
            import faiss  # pip wheels of faiss and torch each ship libomp: do not load both in one process on macOS
            self._faiss = faiss.IndexFlatIP(self.desc.shape[1])
            self._faiss.add(self.desc)

    @property
    def nbytes(self):
        return self.desc.nbytes

    def search(self, q, k):
        q = np.ascontiguousarray(np.atleast_2d(q), np.float32)
        k = min(k, len(self.desc))
        if self._faiss is not None:
            return self._faiss.search(q, k)
        sims = q @ self.desc.T
        part = np.argpartition(-sims, k - 1, 1)[:, :k]
        ps = np.take_along_axis(sims, part, 1)
        order = np.argsort(-ps, 1, kind="stable")
        return np.take_along_axis(ps, order, 1), np.take_along_axis(part, order, 1)

    def search_places(self, q, k, place_radius_m=0.0):
        """Search, then drop hits whose place (east, north) lies within place_radius_m of a better hit.

        With a rotation-augmented DB the same place appears once per yaw; without this a top-10 list
        can be one place at 10 headings. q may be (n_variants, d): the best similarity over variants wins.
        """
        pool = min(len(self.desc), max(k * 16, 64))
        sims, idx = self.search(q, pool)
        sims, idx = sims.ravel(), idx.ravel()
        order = np.argsort(-sims, kind="stable")
        picked, picked_sim, picked_var = [], [], []
        for o in order:
            i = idx[o]
            p = self.meta[i, :2]
            if any(np.hypot(*(p - self.meta[j, :2])) <= place_radius_m for j in picked):
                continue
            picked.append(i)
            picked_sim.append(sims[o])
            picked_var.append(o // pool)
            if len(picked) == k:
                break
        return np.array(picked), np.array(picked_sim), np.array(picked_var)
