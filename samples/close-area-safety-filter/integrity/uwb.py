"""Second position source for the arena: UWB two-way ranging to 4 anchors in the area corners.

    anchors = make_anchors(world)                  # (4, 3) local ENU, metres
    ranger = UwbRanger(world, rng, nlos=make_nlos(world, seed, index))
    r = ranger.measure(t, x, y, z)                 # (4,) ranges, call at 10 Hz from truth

Model per range i at time t (truth position p, anchor a_i, 3D distance):

    r_i = |p - a_i| + b_i + w + nlos_i(t)

- w ~ N(0, SIGMA_WHITE) white per sample. SIGMA_WHITE = 0.03 m is assumed. Sources: doc 03
  (docs/research/close-area-nav/03-close-area-localization.md, sensor table, UWB row) gives
  static TWR per-axis position jitter ~0.5-2 cm (Bitcraze wiki, "not a specification");
  Fan and Du, arXiv 2205.05939, section II-C: range noise "only a few centimeters".
- b_i ~ U(-CAL_BIAS, CAL_BIAS) per anchor per run: residual bias after antenna-delay
  calibration and anchor survey. CAL_BIAS = 0.10 m is assumed. Doc 03: raw ranges are biased
  short 0.2-0.4 m by antenna delay before calibration, and one static 3D point was ~0.24 m off;
  "bias from anchor survey errors" is listed as the UWB drift source.
- nlos_i(t): the fault option. One seeded anchor gets a positive bias U(NLOS_BIAS) for
  NLOS_DUR_S from t0. NLOS bias is positive (longer path); Fan and Du section II-C, citing
  their refs, give NLOS bias "up to 1.5 m". So NLOS_BIAS = (0.3, 1.5) m. The fault is
  injected, not derived from the arena geometry (obstacles do not block the anchors here).

The monitor's nominal model for one range is SIGMA_MODEL = 0.07 m, a Gaussian overbound of
white + calibration bias (std sqrt(0.03^2 + 0.10^2 / 3) = 0.065 m).

Anchors: corners of the walled area inset ANCHOR_INSET, heights alternating 2.5 / 0.5 m
(doc 03: "poor Z geometry when anchors share a height"). The vehicle height is known (arena
holds z = 1.0 m; a real drone would use its downward rangefinder), so the fix is 2D.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

HZ = 10
SIGMA_WHITE = 0.03      # m, assumed (doc 03; Fan and Du 2022)
CAL_BIAS = 0.10         # m, half-width of the per-anchor residual bias, assumed (doc 03)
SIGMA_MODEL = 0.07      # m, what monitor.py assumes per range (overbound of the two above)
NLOS_BIAS = (0.3, 1.5)  # m, positive NLOS bias range (Fan and Du 2022: up to 1.5 m)
NLOS_DUR_S = 10.0
NLOS_START = (1.0, 10.0)
ANCHOR_INSET = 0.3      # m
ANCHOR_Z = (2.5, 0.5, 2.5, 0.5)


def make_anchors(world) -> np.ndarray:
    i = ANCHOR_INSET
    xy = [(world.xmin + i, world.ymin + i), (world.xmax - i, world.ymin + i),
          (world.xmax - i, world.ymax - i), (world.xmin + i, world.ymax - i)]
    return np.array([(x, y, z) for (x, y), z in zip(xy, ANCHOR_Z)], float)


@dataclass
class NlosFault:
    anchor: int
    bias_m: float
    t0: float
    t1: float

    def active(self, t: float) -> bool:
        return self.t0 <= t < self.t1

    def offset(self, t: float) -> np.ndarray:
        o = np.zeros(4)
        if self.active(t):
            o[self.anchor] = self.bias_m
        return o

    @property
    def log(self) -> dict:
        return {"fault": "uwb_nlos", "anchor": self.anchor, "bias_m": round(self.bias_m, 4),
                "start_t": round(self.t0, 3), "dur_s": round(self.t1 - self.t0, 3)}


def make_nlos(world, seed: int, index: int, t0: float | None = None) -> NlosFault:
    """Seeded per layout. t0 overrides the drawn start (used to align with a VIO fault)."""
    rng = np.random.default_rng([seed, index, 4300])
    anchor = int(rng.integers(0, 4))
    bias = float(rng.uniform(*NLOS_BIAS))
    t_draw = float(rng.uniform(*NLOS_START))
    t0 = t_draw if t0 is None else float(t0)
    return NlosFault(anchor, bias, t0, t0 + NLOS_DUR_S)


class UwbRanger:
    def __init__(self, world, rng, nlos: NlosFault | None = None, anchors: np.ndarray | None = None):
        self.anchors = make_anchors(world) if anchors is None else np.asarray(anchors, float)
        self.rng = rng
        self.cal_bias = rng.uniform(-CAL_BIAS, CAL_BIAS, len(self.anchors))
        self.nlos = nlos

    def measure(self, t: float, x: float, y: float, z: float) -> np.ndarray:
        d = np.linalg.norm(self.anchors - np.array([x, y, z]), axis=1)
        r = d + self.cal_bias + self.rng.normal(0.0, SIGMA_WHITE, len(d))   # always drawn
        if self.nlos is not None:
            r = r + self.nlos.offset(t)
        return r
