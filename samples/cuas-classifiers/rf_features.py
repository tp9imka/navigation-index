"""PSD band-power and burstiness features for DroneRF segments.

A DroneRF segment file is one CSV line of 10,000,000 real-valued samples (counted on the
data). Each segment is cut into windows; features are computed per window and the
segment id is kept so that evaluation can group by segment.
"""
import re
from pathlib import Path

import numpy as np
from scipy.signal import welch
from scipy.stats import kurtosis

N_WINDOWS = 10
NPERSEG = 2048
N_BANDS = 64
ENVELOPE_BLOCK = 1000
EPS = 1e-12

# BUI code prefix => class (DroneRF paper: 00000 background, 100xx Bebop, 101xx AR, 11000 Phantom)
BUI_CLASSES = {"00000": "background", "100": "bebop", "101": "ar_drone", "11000": "phantom"}
SEGMENT_RE = re.compile(r"(?P<bui>\d{5})(?P<band>[LH])_(?P<idx>\d+)\.csv$")


def bui_class(bui):
    for prefix in sorted(BUI_CLASSES, key=len, reverse=True):
        if bui.startswith(prefix):
            return BUI_CLASSES[prefix]
    raise ValueError(f"unknown BUI {bui}")


def read_segment(path):
    return np.fromstring(Path(path).read_text(), sep=",")


def band_powers(x, n_bands=N_BANDS, nperseg=NPERSEG):
    """Welch PSD pooled into n_bands equal-width bands, log10, minus the window's median
    band so absolute receiver gain drops out."""
    _, pxx = welch(x, nperseg=nperseg, detrend="constant")
    bands = pxx[: (len(pxx) // n_bands) * n_bands].reshape(n_bands, -1).mean(axis=1)
    lb = np.log10(bands + EPS)
    return lb - np.median(lb)


def burstiness(x, block=ENVELOPE_BLOCK):
    """Statistics of block power over time: packetised links (video, telemetry) are bursty."""
    n = (len(x) // block) * block
    p = (x[:n].reshape(-1, block) ** 2).mean(axis=1)
    lp = np.log10(p + EPS)
    return {
        "env_p99_over_median_db": 10 * (np.percentile(lp, 99) - np.median(lp)),
        "env_std_db": 10 * lp.std(),
        "env_kurtosis": float(kurtosis(p)),
        "env_active_frac": float((lp > np.median(lp) + 0.5).mean()),
    }


def window_features(x):
    bp = band_powers(x)
    f = {f"band_{i:02d}": v for i, v in enumerate(bp)}
    _, pxx = welch(x, nperseg=NPERSEG)
    f["spectral_flatness"] = float(np.exp(np.mean(np.log(pxx + EPS))) / (pxx.mean() + EPS))
    f.update(burstiness(x))
    return f


def segment_features(x, n_windows=N_WINDOWS):
    w = len(x) // n_windows
    return [window_features(x[i * w:(i + 1) * w]) for i in range(n_windows)]


def iter_segments(root):
    """Yield (path, bui, band, idx, label) for every DroneRF csv under root."""
    for p in sorted(Path(root).rglob("*.csv")):
        m = SEGMENT_RE.search(p.name)
        if m:
            yield p, m["bui"], m["band"], int(m["idx"]), bui_class(m["bui"])
