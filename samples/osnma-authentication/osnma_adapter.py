"""OSNMA authentication status as an input to samples/gnss-interference-monitor/scorer.py. Stdlib only.

The scorer is imported, not edited. AuthAwareScorer subclasses InterferenceScorer and adds OSNMA
detectors to each Assessment just before the scorer's own alarm latch runs, so OSNMA alerts latch and
clear exactly like the telemetry and consistency alerts.

Input is one OsnmaStatus per Galileo subframe (30 s), built from an OSNMAlib status log entry
(`from_status_entry`) or from the compact timeline that osnma_scenarios.py writes (`from_timeline`).
Status stays in force for the epochs that follow until the next subframe arrives.

Honest degradation: before the first successful authentication, with no status, or with a stale
status, the OSNMA detectors stay silent and `osnma_state` reads "not-measured". Absence of
authentication is only an alert after authentication has been held.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gnss-interference-monitor"))
from scorer import ALERT_SCORE, Alert, Assessment, Epoch, InterferenceScorer  # noqa: E402

SECONDS_PER_WEEK = 604800
SUBFRAME_S = 30
ADKD0_FRESH_S = 60  # nominal lag subframe start => newest authenticated ADKD0 data is 30 s (measured on the OSNMAlib recording)
STATUS_STALE_S = 90  # older status => not measured
TS_BOUND_S = 15.0  # T_L/2 with T_L = 30 s: |GST_SIS - GST_Rx| check in Receiver Guidelines 1.3 sec. 5.3.1
AUTH_FRACTION_MIN = 0.5  # authenticated / tracked Galileo SVs below this counts as an authentication drop
AUTH_DROP_MIN_CN0 = 35.0  # dB-Hz: a drop while Galileo signals are this strong is a spoofing cue, not fading

OSNMA_WEIGHTS = {
    "osnma_tag_fail": 0.6,
    "osnma_key_fail": 0.6,
    "osnma_data_mismatch": 0.6,
    "osnma_time_offset": 0.6,
    "osnma_time_reject": 0.5,
    "osnma_auth_drop": 0.5,
}


@dataclass
class OsnmaStatus:
    t: float  # subframe start on the same time axis as Epoch.t
    tracked_svs: set[int] = field(default_factory=set)  # Galileo SVs with nav data this subframe
    auth_svs: set[int] = field(default_factory=set)  # SVs with fresh ADKD0 authentication
    tags_fail: int = 0
    keys_fail: int = 0
    time_rejects: int = 0  # pages rejected because GST went backwards
    data_mismatch_svs: set[int] = field(default_factory=set)  # decoded words != authenticated copy
    clock_offset_s: float | None = None  # independent clock minus signal GST; None = no independent clock


def gst_seconds(wn_tow) -> int:
    return wn_tow[0] * SECONDS_PER_WEEK + wn_tow[1]


def from_status_entry(entry: dict, t0_gst: int = 0, clock_offset_s: float | None = None) -> OsnmaStatus:
    """One element of OSNMAlib's status_log.json => OsnmaStatus. `t` is GST seconds minus t0_gst."""
    t = gst_seconds(entry["metadata"]["GST_subframe"])
    v = entry.get("verified_OSNMA_material", {})
    adkd0 = entry.get("authenticated_nav_data", {}).get("ADKD0", {})
    return OsnmaStatus(
        t=float(t - t0_gst),
        tracked_svs={int(s) for s in entry.get("nav_data_received", {})},
        auth_svs={int(s) for s, b in adkd0.items() if t - gst_seconds(b["last_gst"]) <= ADKD0_FRESH_S},
        tags_fail=sum(1 for x in v.get("tags", []) if not x["verification"]),
        keys_fail=sum(1 for x in v.get("tesla_key", []) if not x["verification"]),
        clock_offset_s=clock_offset_s,
    )


def from_timeline(result: dict) -> list[OsnmaStatus]:
    """osnma_scenarios.py result => statuses on a time axis starting at 0 at the first subframe.

    Page rejections and data mismatches are run totals in that output, so they are attached to the
    last subframe only; per-subframe values need OSNMAlib's general log.
    """
    tl = result["timeline"]
    if not tl:
        return []
    t0 = gst_seconds(tl[0]["gst_sf"])
    out = [OsnmaStatus(t=float(gst_seconds(x["gst_sf"]) - t0), tracked_svs=set(x["nav_svs"]),
                       auth_svs=set(x["adkd0_fresh"]), tags_fail=x["tags_fail"], keys_fail=x["keys_fail"],
                       clock_offset_s=result.get("independent_clock_offset_s")) for x in tl]
    c = result.get("counts", {})
    out[-1].time_rejects = c.get("time_backwards", 0)
    out[-1].data_mismatch_svs = set(c.get("words_differ_from_authenticated_stream", []))
    return out


class AuthAwareScorer(InterferenceScorer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.osnma: OsnmaStatus | None = None
        self.auth_held = False  # authentication was achieved at least once
        self.osnma_state = "not-measured"

    def update_osnma(self, status: OsnmaStatus) -> None:
        self.osnma = status
        if status.auth_svs:
            self.auth_held = True

    def assess(self, ep: Epoch) -> Assessment:
        res = super().assess(ep)
        res.osnma_state = self.osnma_state
        return res

    # Hook: runs inside InterferenceScorer.assess right before the alarm latch.
    def _update_alarm(self, res: Assessment, ep: Epoch):
        self._apply_osnma(res, ep)
        super()._update_alarm(res, ep)

    def _apply_osnma(self, res: Assessment, ep: Epoch) -> None:
        st = self.osnma
        if st is None or ep.t - st.t > STATUS_STALE_S:
            self.osnma_state = "not-measured"
            return
        hits: list[Alert] = []

        def add(det, value, thr, unit, msg, evidence=None):
            hits.append(Alert(det, "spoofing", float(value), float(thr), unit, msg, evidence or {}))

        if st.tags_fail:
            add("osnma_tag_fail", st.tags_fail, 0, "tags", f"{st.tags_fail} OSNMA tag(s) failed verification")
        if st.keys_fail:
            add("osnma_key_fail", st.keys_fail, 0, "keys", f"{st.keys_fail} TESLA key(s) failed the chain check")
        if st.data_mismatch_svs:
            add("osnma_data_mismatch", len(st.data_mismatch_svs), 0, "SVs",
                f"decoded nav words differ from the authenticated copy on SV {sorted(st.data_mismatch_svs)}",
                {"svs": sorted(st.data_mismatch_svs)})
        if st.time_rejects:
            add("osnma_time_reject", st.time_rejects, 0, "pages", f"{st.time_rejects} page(s) with GST going backwards")
        if st.clock_offset_s is not None and abs(st.clock_offset_s) > TS_BOUND_S:
            add("osnma_time_offset", st.clock_offset_s, TS_BOUND_S, "s",
                f"signal GST is {st.clock_offset_s:+.0f} s off the independent clock (bound {TS_BOUND_S:.0f} s)")
        if self.auth_held and st.tracked_svs:
            frac = len(st.auth_svs & st.tracked_svs) / len(st.tracked_svs)
            gal_cn0 = [v for k, v in (ep.cn0 or {}).items() if k.startswith("E")]
            strong = not gal_cn0 or sorted(gal_cn0)[len(gal_cn0) // 2] >= AUTH_DROP_MIN_CN0
            if frac < AUTH_FRACTION_MIN and strong:
                add("osnma_auth_drop", frac, AUTH_FRACTION_MIN, "frac",
                    f"{len(st.auth_svs & st.tracked_svs)}/{len(st.tracked_svs)} tracked Galileo SVs authenticated"
                    + ("" if gal_cn0 else " (Galileo C/N0 not reported)"),
                    {"tracked": sorted(st.tracked_svs), "authenticated": sorted(st.auth_svs)})

        if not self.auth_held and not hits:
            self.osnma_state = "not-measured"
            return
        n_auth = len(st.auth_svs & st.tracked_svs)
        self.osnma_state = "alert" if hits else f"authenticated {n_auth}/{len(st.tracked_svs)}"
        if not hits:
            return
        res.alerts.extend(hits)
        res.reasons.extend(a.message for a in hits)
        res.spoof_score = min(1.0, res.spoof_score + sum(OSNMA_WEIGHTS[a.detector] for a in hits))


def run_timeline(statuses: list[OsnmaStatus], epoch_fn, duration_s: float | None = None) -> list[Assessment]:
    """Drive the scorer at 1 Hz with epochs from epoch_fn(t) and OSNMA statuses as they fall due."""
    sc = AuthAwareScorer()
    end = duration_s if duration_s is not None else (statuses[-1].t + SUBFRAME_S + 1 if statuses else 0)
    pending = sorted(statuses, key=lambda s: s.t)
    out, i, t = [], 0, 0.0
    while t < end:
        # A subframe's status is known once the subframe has ended.
        while i < len(pending) and pending[i].t + SUBFRAME_S <= t:
            sc.update_osnma(pending[i])
            i += 1
        out.append(sc.assess(epoch_fn(t)))
        t += 1.0
    return out


def first_alarm(results: list[Assessment]) -> Assessment | None:
    return next((r for r in results if r.spoof_score >= ALERT_SCORE), None)
