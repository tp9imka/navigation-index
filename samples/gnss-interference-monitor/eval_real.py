"""Per-detector evaluation of a scorer on the real Jammertest 2024 VAARA u-blox logs. Stdlib only.

  python3 eval_real.py --data ../real-attack-replay/data/vaara [--brdc DIR] [--scorer PATH]
                       [--split tune|holdout|all] [--out results.json]

Epochs come from ../real-attack-replay/ubx_nmea_epochs.py exactly as replay.py builds them
(L1 C/N0 from GSV, NMEA fix / HDOP / velocity, receiver time minus the reconstructed time axis
as clk_bias_ns, car max speed 70 m/s). With --brdc (a directory holding BRDC_<doy>.rnx.gz IGS
merged broadcast files) the UBX-RXM-SFRBX GPS subframes in the same stream are decoded and
checked against that independent broadcast (ephemeris_check.py) and fed as eph_mismatch_m.
--scorer loads another scorer.py (e.g. the previous git revision) for a before/after run.

Per labelled attack slot and detector: TP when the detector is part of a non-clean verdict
between max(start - 300 s, previous slot end) and the slot end (replay.py's lead rule). False
positives: alerting epochs and alarm raises in the logged quiet slot and in "no logged test"
time (not guaranteed quiet; other Jammertest sites transmitted all day).

Split: thresholds of the new power CUSUM and the Doppler reference were chosen on TUNE_FILES
only; HOLDOUT_FILES hold the logged quiet slot and all spoofing slots but 2.4.13.
"""

from __future__ import annotations

import argparse
import calendar
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPLAY_DIR = HERE.parent / "real-attack-replay"
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(REPLAY_DIR))
import ubx_nmea_epochs as une  # noqa: E402
from ephemeris_check import EphemerisChecker, parse_rinex3_gps_nav  # noqa: E402
from replay import LEAD_S, NS_PER_S, false_alarms, utc, window_metrics  # noqa: E402

CAR_MAX_SPEED_MPS = 70.0
UBX_RXM, UBX_SFRBX = 0x02, 0x13
TUNE_FILES = ("ublox_2024-09-10T073207Z0000", "ublox_2024-09-11T122113", "ublox_2024-09-12T085023")
HOLDOUT_FILES = ("ublox_2024-09-10T115512Z0000", "ublox_2024-09-11T075704", "ublox_2024-09-11T143312",
                 "ublox_2024-09-12T071744")


def load_scorer(path: Path | None):
    if path is None:
        import scorer
        return scorer
    spec = importlib.util.spec_from_file_location("scorer_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(mod)
    return mod


def load_brdc(brdc_dir: Path | None, day: str):
    if brdc_dir is None:
        return None
    y, m, d = (int(x) for x in day.split("-"))
    doy = calendar.timegm((y, m, d, 0, 0, 0)) // 86400 - calendar.timegm((y, 1, 1, 0, 0, 0)) // 86400 + 1
    ref: dict[str, list] = {}
    for k in (doy - 1, doy):  # the previous day's file covers ephemerides issued before midnight
        p = brdc_dir / f"BRDC_{k}.rnx.gz"
        if p.exists():
            for sv, v in parse_rinex3_gps_nav(p).items():
                ref.setdefault(sv, []).extend(v)
    return ref or None


def epochs_with_ephemeris(buf: bytes, spec: dict, checker: EphemerisChecker | None):
    """to_epochs() with the SFRBX frames of the same stream fed to the checker on the way.
    raw_epochs() pulls frames lazily, so when an epoch is yielded the checker has seen the
    subframes up to that epoch (plus at most the next epoch's leading UBX frames)."""
    frames = une.frames
    clock = {"t": None}

    def tapped(b):
        for f in frames(b):
            if checker is not None and f[0] == "ubx" and f[1] == UBX_RXM and f[2] == UBX_SFRBX and clock["t"]:
                checker.feed_sfrbx(f[3], clock["t"])
            yield f

    une.frames = tapped
    try:
        for ep, info in une.to_epochs(buf, spec["day"], spec.get("period_s", 1.0)):
            clock["t"] = ep.t
            if checker is not None:
                ep.eph_mismatch_m = checker.mismatch_m(ep.t)
            yield ep, info
    finally:
        une.frames = frames


def run_file(mod, buf: bytes, spec: dict, brdc_ref):
    sc = mod.InterferenceScorer(max_speed_mps=CAR_MAX_SPEED_MPS)
    checker = EphemerisChecker(brdc_ref) if brdc_ref else None
    rows = []
    for ep, info in epochs_with_ephemeris(buf, spec, checker):
        if info["rx_t"] is not None:
            ep.clk_bias_ns = (info["rx_t"] - ep.t) * NS_PER_S
        a = sc.assess(ep)
        rows.append({"t": ep.t, "verdict": a.verdict, "alarm": a.alarm.active, "fix": ep.has_fix,
                     "detectors": sorted({x.detector for x in a.alerts}), "time_jump_s": info["time_jump_s"]})
    eph = None if checker is None else {"decoded_sets": checker.decoded, "parity_fail": checker.parity_fail}
    return rows, eph


def detector_slots(rows, start, end, lead_from):
    lo = max(lead_from, start - LEAD_S) if lead_from is not None else start - LEAD_S
    c = Counter(d for r in rows if lo < r["t"] <= end and r["verdict"] != "clean" for d in r["detectors"])
    return dict(c.most_common())


def evaluate(mod, data: Path, labels: dict, brdc: Path | None, split: str):
    files = {"tune": TUNE_FILES, "holdout": HOLDOUT_FILES, "all": TUNE_FILES + HOLDOUT_FILES}[split]
    out = []
    for spec in labels["files"]:
        stem = Path(spec["path"]).stem
        if stem not in files:
            continue
        path = data / spec["path"]
        if not path.exists():
            print(f"skip (missing): {path}", file=sys.stderr)
            continue
        rows, eph = run_file(mod, path.read_bytes(), spec, load_brdc(brdc, spec["day"]))
        wins = [(utc(spec["day"], w["start"]), utc(spec["day"], w["end"]), w) for w in spec["windows"]]
        per = []
        for i, (s, e, w) in enumerate(wins):
            prev_end = max((pe for ps, pe, _ in wins[:i] if pe < s), default=None)
            m = window_metrics(rows, s, e, prev_end)
            per.append({"test": w["test"], "kind": w["kind"], "detected": m.get("detected"),
                        "ttd_s": m.get("ttd_s"), "latched_at_start": m.get("alarm_latched_at_start"),
                        "alert_epoch_fraction": m.get("alert_epoch_fraction"),
                        "detectors": detector_slots(rows, s, e, s if w["kind"] == "quiet" else prev_end)})
        t0, t1 = rows[0]["t"], rows[-1]["t"]
        gaps, cur = [], t0
        for s, e, _ in sorted(wins, key=lambda x: x[0]):
            if s - LEAD_S > cur:
                gaps.append((cur, s - LEAD_S))
            cur = max(cur, e + LEAD_S)
        if cur < t1:
            gaps.append((cur, t1))
        quiet = [(s, e) for s, e, w in wins if w["kind"] == "quiet"]
        out.append({"file": stem, "set": "tune" if stem in TUNE_FILES else "holdout", "epochs": len(rows),
                    "ephemeris": eph, "windows": per,
                    "quiet": false_alarms(rows, quiet) if quiet else None,
                    "no_logged_test": false_alarms(rows, gaps)})
    return out


def print_summary(res):
    for f in res:
        print(f"== {f['file']} ({f['set']}) epochs {f['epochs']} eph {f['ephemeris']}")
        for w in f["windows"]:
            print(f"  {w['test']:<8} {w['kind']:<5} det={str(w['detected']):<5} ttd={w['ttd_s']} "
                  f"latched={w['latched_at_start']} alert%={100 * (w['alert_epoch_fraction'] or 0):.0f} {w['detectors']}")
        for k in ("quiet", "no_logged_test"):
            fa = f.get(k)
            if fa:
                print(f"  {k}: {fa['hours']} h raises {fa['alarm_raises']} alarm% {100 * (fa['alarm_epoch_fraction'] or 0):.0f} "
                      f"alert epochs {fa['alert_epochs']} {fa['detector_epochs']}")


def _slot_cell(w):
    if not w.get("detected"):
        return "**no**"
    lat = " L" if w.get("latched_at_start") else ""
    dets = ", ".join(list(w["detectors"])[:3])
    return f"yes {w['ttd_s']}{lat} ({100 * w['alert_epoch_fraction']:.0f}%) {dets}"


def markdown_tables(runs: dict[str, dict]) -> str:
    """runs: label -> eval_real JSON. Per-slot table, then per-detector TP / FP counts."""
    labels = list(runs)
    first = runs[labels[0]]["results"]
    out = ["| Slot | Set | Kind | " + " | ".join(labels) + " |", "|---|---|---|" + "---|" * len(labels)]
    for fi, f in enumerate(first):
        for wi, w in enumerate(f["windows"]):
            cells = [_slot_cell(runs[k]["results"][fi]["windows"][wi]) for k in labels]
            out.append(f"| {w['test']} | {f['set']} | {w['kind']} | " + " | ".join(cells) + " |")
    out.append("")
    dets = sorted({d for r in runs.values() for f in r["results"] for w in f["windows"] for d in w["detectors"]}
                  | {d for r in runs.values() for f in r["results"] for k in ("quiet", "no_logged_test")
                     for d in ((f.get(k) or {}).get("detector_epochs") or {})})
    out.append("| Detector | " + " | ".join(f"{k}: TP tune / holdout, FP epochs" for k in labels) + " |")
    out.append("|---|" + "---|" * len(labels))
    for d in dets:
        cells = []
        for k in labels:
            tp = {"tune": 0, "holdout": 0}
            fp = 0
            for f in runs[k]["results"]:
                for w in f["windows"]:
                    if w["kind"] != "quiet" and d in w["detectors"]:
                        tp[f["set"]] += 1
                    if w["kind"] == "quiet":
                        fp += w["detectors"].get(d, 0)
                fp += ((f.get("no_logged_test") or {}).get("detector_epochs") or {}).get(d, 0)
            cells.append(f"{tp['tune']} / {tp['holdout']}, {fp}")
        out.append(f"| `{d}` | " + " | ".join(cells) + " |")
    n_tune = sum(1 for f in first for w in f["windows"] if w["kind"] != "quiet" and f["set"] == "tune")
    n_hold = sum(1 for f in first for w in f["windows"] if w["kind"] != "quiet" and f["set"] == "holdout")
    out.append("")
    out.append(f"TP = attack slots (tune {n_tune}, holdout {n_hold}) where the detector was part of a non-clean "
               f"verdict; FP epochs = its alerting epochs in the quiet slot and in no-logged-test time.")
    out.append("")
    out.append("| Span | " + " | ".join(labels) + " |")
    out.append("|---|" + "---|" * len(labels))
    for fi, f in enumerate(first):
        for key in ("quiet", "no_logged_test"):
            if not f.get(key):
                continue
            cells = []
            for k in labels:
                fa = runs[k]["results"][fi][key]
                cells.append(f"{fa['alarm_raises']} raises, alarm {100 * (fa['alarm_epoch_fraction'] or 0):.0f}%")
            out.append(f"| {f['file']} {key} ({f[key]['hours']} h, {f['set']}) | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path)
    ap.add_argument("--labels", type=Path, default=REPLAY_DIR / "labels.json")
    ap.add_argument("--brdc", type=Path)
    ap.add_argument("--scorer", type=Path)
    ap.add_argument("--split", choices=("tune", "holdout", "all"), default="all")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--table", nargs="+", metavar="LABEL=JSON",
                    help="print Markdown comparison tables of earlier --out files and exit")
    a = ap.parse_args(argv)
    if a.table:
        print(markdown_tables({k: json.loads(Path(v).read_text()) for k, v in (x.split("=", 1) for x in a.table)}))
        return
    if a.data is None:
        ap.error("--data is required unless --table is given")
    mod = load_scorer(a.scorer)
    res = evaluate(mod, a.data, json.loads(a.labels.read_text()), a.brdc, a.split)
    print_summary(res)
    if a.out:
        a.out.write_text(json.dumps({"scorer": str(a.scorer or "scorer.py"), "brdc": bool(a.brdc),
                                     "split": a.split, "results": res}, indent=1))


if __name__ == "__main__":
    main()
