"""Heuristic GNSS jamming / spoofing scorer over receiver telemetry epochs. Stdlib only.

Feed one Epoch per navigation epoch (typically 1 Hz). Every field except `t` is
optional, so the scorer works with whatever a receiver exposes. Thresholds are
starting points for a hackathon, not certified detection limits: tune them on
recordings from your own antenna and platform.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

BASELINE_MIN_EPOCHS = 10
BASELINE_ALPHA = 0.1  # EWMA weight for clean epochs
BASELINE_MAX_SCORE = 0.2  # epochs scoring above this never update the baseline

CN0_DROP_DB = 6.0
CN0_DROP_SV_FRACTION = 0.75
CN0_RISE_DB = 4.0
CN0_UNIFORM_SD_DB = 2.0
CN0_UNIFORM_MIN_SVS = 6
AGC_REL_CHANGE = 0.20
JAM_IND_HIGH = 100  # MON-RF jamInd (CW indicator) is 0..255; u-blox gives no fixed cut-off
CLOCK_JUMP_NS = 1000.0  # ~300 m of range
MAX_SPEED_MPS = 100.0  # set per platform: pedestrian ~5, car ~70, UAV ~60, airliner ~300
RX_FLAG_ALERT_STATE = 2  # spoofDetState / jammingState >= 2 means "indicated" / "warning"

ALERT_SCORE = 0.5
EARTH_RADIUS_M = 6371000.0

JAM_WEIGHTS = {"cn0_drop": 0.5, "agc_change": 0.3, "jam_ind": 0.3, "rx_jam_flag": 0.6}
SPOOF_WEIGHTS = {"cn0_uniform": 0.35, "cn0_rise": 0.3, "clock_jump": 0.35,
                 "position_jump": 0.35, "rx_spoof_flag": 0.6}


@dataclass
class Epoch:
    t: float
    cn0: dict[str, float] = field(default_factory=dict)  # sv id -> C/N0 dB-Hz
    agc_cnt: float | None = None
    jam_ind: float | None = None
    clk_bias_ns: float | None = None
    clk_drift_ns_s: float | None = None
    lat: float | None = None
    lon: float | None = None
    spoof_det_state: int | None = None
    jamming_state: int | None = None


@dataclass
class Assessment:
    t: float
    jam_score: float
    spoof_score: float
    reasons: list[str]

    @property
    def verdict(self) -> str:
        jam, spoof = self.jam_score >= ALERT_SCORE, self.spoof_score >= ALERT_SCORE
        if jam and spoof:
            return "jamming+spoofing"
        return "jamming" if jam else "spoofing" if spoof else "clean"


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


class InterferenceScorer:
    def __init__(self, max_speed_mps: float = MAX_SPEED_MPS):
        self.max_speed_mps = max_speed_mps
        self.base_cn0: dict[str, float] = {}
        self.base_agc: float | None = None
        self.clean_epochs = 0
        self.prev: Epoch | None = None

    @property
    def baseline_ready(self) -> bool:
        return self.clean_epochs >= BASELINE_MIN_EPOCHS

    def assess(self, ep: Epoch) -> Assessment:
        hits: set[str] = set()
        reasons: list[str] = []

        if self.baseline_ready:
            self._check_cn0_vs_baseline(ep, hits, reasons)
            if ep.agc_cnt is not None and self.base_agc:
                rel = (ep.agc_cnt - self.base_agc) / self.base_agc
                if abs(rel) >= AGC_REL_CHANGE:
                    hits.add("agc_change")
                    reasons.append(f"AGC {rel:+.0%} vs baseline")
        self._check_cn0_uniform(ep, hits, reasons)
        if ep.jam_ind is not None and ep.jam_ind >= JAM_IND_HIGH:
            hits.add("jam_ind")
            reasons.append(f"jamInd {ep.jam_ind:.0f}")
        if ep.jamming_state is not None and ep.jamming_state >= RX_FLAG_ALERT_STATE:
            hits.add("rx_jam_flag")
            reasons.append(f"receiver jammingState {ep.jamming_state}")
        if ep.spoof_det_state is not None and ep.spoof_det_state >= RX_FLAG_ALERT_STATE:
            hits.add("rx_spoof_flag")
            reasons.append(f"receiver spoofDetState {ep.spoof_det_state}")
        if self.prev is not None:
            self._check_jumps(self.prev, ep, hits, reasons)

        jam = min(1.0, sum(w for k, w in JAM_WEIGHTS.items() if k in hits))
        spoof = min(1.0, sum(w for k, w in SPOOF_WEIGHTS.items() if k in hits))
        result = Assessment(ep.t, jam, spoof, reasons)
        if max(jam, spoof) <= BASELINE_MAX_SCORE:
            self._update_baseline(ep)
        self.prev = ep
        return result

    def _check_cn0_vs_baseline(self, ep, hits, reasons):
        if not self.base_cn0:
            return
        common = [sv for sv in ep.cn0 if sv in self.base_cn0]
        lost = [sv for sv in self.base_cn0 if sv not in ep.cn0]
        deltas = [ep.cn0[sv] - self.base_cn0[sv] for sv in common]
        dropped = sum(1 for d in deltas if d <= -CN0_DROP_DB) + len(lost)
        if dropped / len(self.base_cn0) >= CN0_DROP_SV_FRACTION:
            hits.add("cn0_drop")
            reasons.append(f"C/N0 drop >= {CN0_DROP_DB:.0f} dB or lost on "
                           f"{dropped}/{len(self.base_cn0)} SVs")
        if deltas and statistics.median(deltas) >= CN0_RISE_DB:
            hits.add("cn0_rise")
            reasons.append(f"median C/N0 rise {statistics.median(deltas):+.1f} dB")

    def _check_cn0_uniform(self, ep, hits, reasons):
        values = list(ep.cn0.values())
        if len(values) >= CN0_UNIFORM_MIN_SVS:
            sd = statistics.pstdev(values)
            if sd < CN0_UNIFORM_SD_DB:
                hits.add("cn0_uniform")
                reasons.append(f"C/N0 spread only {sd:.1f} dB over {len(values)} SVs")

    def _check_jumps(self, prev, ep, hits, reasons):
        dt = ep.t - prev.t
        if dt <= 0:
            return
        if prev.clk_bias_ns is not None and ep.clk_bias_ns is not None:
            drift = prev.clk_drift_ns_s or 0.0
            residual = ep.clk_bias_ns - (prev.clk_bias_ns + drift * dt)
            if abs(residual) >= CLOCK_JUMP_NS:
                hits.add("clock_jump")
                reasons.append(f"clock bias jump {residual:+.0f} ns")
        if None not in (prev.lat, prev.lon, ep.lat, ep.lon):
            speed = haversine_m(prev.lat, prev.lon, ep.lat, ep.lon) / dt
            if speed > self.max_speed_mps:
                hits.add("position_jump")
                reasons.append(f"implied speed {speed:.0f} m/s")

    def _update_baseline(self, ep):
        for sv, c in ep.cn0.items():
            old = self.base_cn0.get(sv)
            self.base_cn0[sv] = c if old is None else old + BASELINE_ALPHA * (c - old)
        for sv in [sv for sv in self.base_cn0 if sv not in ep.cn0]:
            del self.base_cn0[sv]  # set or blocked SVs; a whole-sky loss never reaches here
        if ep.agc_cnt is not None:
            old = self.base_agc
            self.base_agc = ep.agc_cnt if old is None else old + BASELINE_ALPHA * (ep.agc_cnt - old)
        self.clean_epochs += 1
