"""Gridded DEM with bilinear lookup, plus a seeded synthetic terrain generator."""

import math
import random


class Dem:
    """Heights on a regular grid: x = x0 + col * dx, y = y0 + row * dy (metres).

    dy is negative for north-up rasters (GeoTIFF convention), positive for the
    synthetic grid. Lookups outside the grid return None.
    """

    def __init__(self, heights, x0, y0, dx, dy):
        self.h = heights
        self.rows = len(heights)
        self.cols = len(heights[0])
        self.x0, self.y0, self.dx, self.dy = x0, y0, dx, dy

    def height(self, x, y):
        c = (x - self.x0) / self.dx
        r = (y - self.y0) / self.dy
        c0, r0 = math.floor(c), math.floor(r)
        if c0 < 0 or r0 < 0 or c0 + 1 >= self.cols or r0 + 1 >= self.rows:
            return None
        fc, fr = c - c0, r - r0
        row0, row1 = self.h[r0], self.h[r0 + 1]
        top = row0[c0] * (1 - fc) + row0[c0 + 1] * fc
        bottom = row1[c0] * (1 - fc) + row1[c0 + 1] * fc
        return top * (1 - fr) + bottom * fr


HILL_COUNT = 60
HILL_HEIGHT_M = (40.0, 350.0)
HILL_SIGMA_M = (300.0, 1500.0)
NOISE_OCTAVES = 4
NOISE_BASE_CELL_M = 800.0
NOISE_AMPLITUDE_M = 25.0


def _value_noise(rng, rows, cols, spacing, cell_m):
    """One octave of bilinear value noise on a lattice with cell_m pitch."""
    n = int(rows * spacing / cell_m) + 2
    m = int(cols * spacing / cell_m) + 2
    lattice = [[rng.uniform(-1, 1) for _ in range(m)] for _ in range(n)]
    lat = Dem(lattice, 0.0, 0.0, cell_m, cell_m)
    return [[lat.height(c * spacing, r * spacing) for c in range(cols)] for r in range(rows)]


def synthetic_dem(rows, cols, spacing, seed):
    """Sum of gaussian hills plus multi-octave value noise. Deterministic per seed."""
    rng = random.Random(seed)
    width, depth = cols * spacing, rows * spacing
    hills = [
        (rng.uniform(0, width), rng.uniform(0, depth),
         rng.uniform(*HILL_HEIGHT_M), rng.uniform(*HILL_SIGMA_M))
        for _ in range(HILL_COUNT)
    ]
    heights = [[0.0] * cols for _ in range(rows)]
    for r in range(rows):
        y = r * spacing
        row = heights[r]
        for c in range(cols):
            x = c * spacing
            z = 0.0
            for hx, hy, hh, hs in hills:
                d2 = (x - hx) ** 2 + (y - hy) ** 2
                if d2 < 16 * hs * hs:
                    z += hh * math.exp(-d2 / (2 * hs * hs))
            row[c] = z
    cell, amp = NOISE_BASE_CELL_M, NOISE_AMPLITUDE_M
    for _ in range(NOISE_OCTAVES):
        noise = _value_noise(rng, rows, cols, spacing, cell)
        for r in range(rows):
            for c in range(cols):
                heights[r][c] += amp * noise[r][c]
        cell, amp = cell / 2, amp / 2
    return Dem(heights, 0.0, 0.0, spacing, spacing)
