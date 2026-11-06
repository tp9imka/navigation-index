"""Stdlib metrics over navapp JSONL runs. Prints a markdown table for the README.

  python3 eval/metrics.py runs/*.jsonl [--alert-limit 10] [--rpe-delta 10] [--json]

Input: first line {"meta": {...}} with optional attack_onset_s; then one record per epoch
with t, east, north, sigma_h, truth_east, truth_north, alarm. Anything a run cannot support
reads "not measured", never a made-up number.

ATE here is translation RMSE in the shared ENU frame with no alignment. For SLAM/VIO
trajectories in their own frame use evo (Umeyama alignment) instead.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

NOT_MEASURED = "not measured"
SIGMA_TO_R95 = math.sqrt(-2.0 * math.log(0.05))
DEFAULT_ALERT_LIMIT_M = 10.0
DEFAULT_RPE_DELTA_S = 10.0


def load(path: Path) -> tuple[dict, list[dict]]:
    meta, recs = {}, []
    with path.open() as fh:
        for line in fh:
            if not line.strip():
                continue
            obj = json.loads(line)
            if "meta" in obj:
                meta = obj["meta"]
            else:
                recs.append(obj)
    recs.sort(key=lambda r: r["t"])
    return meta, recs


def _has_est(r: dict) -> bool:
    return r.get("east") is not None and r.get("north") is not None


def _has_truth(r: dict) -> bool:
    return r.get("truth_east") is not None and r.get("truth_north") is not None


def _err(r: dict) -> float:
    return math.hypot(r["east"] - r["truth_east"], r["north"] - r["truth_north"])


def ate(recs: list[dict]) -> dict:
    errs = [_err(r) for r in recs if _has_est(r) and _has_truth(r)]
    if not errs:
        return {"ate_rmse_m": None, "ate_max_m": None}
    return {"ate_rmse_m": math.sqrt(sum(e * e for e in errs) / len(errs)), "ate_max_m": max(errs)}


def rpe(recs: list[dict], delta_s: float) -> dict:
    pts = [r for r in recs if _has_est(r) and _has_truth(r)]
    sq, j = [], 0
    for i, a in enumerate(pts):
        j = max(j, i + 1)
        while j < len(pts) and pts[j]["t"] - a["t"] < delta_s:
            j += 1
        if j == len(pts):
            break
        b = pts[j]
        de = (b["east"] - a["east"]) - (b["truth_east"] - a["truth_east"])
        dn = (b["north"] - a["north"]) - (b["truth_north"] - a["truth_north"])
        sq.append(de * de + dn * dn)
    return {"rpe_rmse_m": math.sqrt(sum(sq) / len(sq)) if sq else None}


def detection(meta: dict, recs: list[dict]) -> dict:
    onset = meta.get("attack_onset_s")
    before = [r for r in recs if onset is None or r["t"] < onset]
    out = {"false_alarm_epochs": sum(1 for r in before if r.get("alarm")),
           "epochs_without_attack": len(before)}
    if onset is None:
        out["time_to_detect_s"] = "n/a (no attack)"
        return out
    hits = [r["t"] for r in recs if r["t"] >= onset and r.get("alarm")]
    out["time_to_detect_s"] = hits[0] - onset if hits else "missed"
    return out


def availability(recs: list[dict], alert_limit: float) -> dict:
    """Usable = finite estimate whose own 95% radius is within the alert limit."""
    if not recs:
        return {"availability_pct": None, "misleading_pct": None}
    usable = [r for r in recs if _has_est(r) and r.get("sigma_h") is not None
              and SIGMA_TO_R95 * r["sigma_h"] <= alert_limit]
    out = {"availability_pct": 100.0 * len(usable) / len(recs)}
    judged = [r for r in usable if _has_truth(r)]
    # Misleading: the system says usable, truth says outside the alert limit, and no alarm raised.
    out["misleading_pct"] = (100.0 * sum(1 for r in judged if _err(r) > alert_limit and not r.get("alarm"))
                             / len(judged)) if judged else None
    return out


def time_to_exceed(meta: dict, recs: list[dict], alert_limit: float):
    onset = meta.get("attack_onset_s")
    if onset is None:
        return "n/a (no attack)"
    after = [r for r in recs if r["t"] >= onset and _has_est(r) and _has_truth(r)]
    if not after:
        return None
    for r in after:
        if _err(r) > alert_limit:
            return r["t"] - onset
    return f"> {after[-1]['t'] - onset:g} (never)"


def evaluate(path: Path, alert_limit: float, rpe_delta: float) -> dict:
    meta, recs = load(path)
    out = {"run": path.stem, "scenario": meta.get("kind", "?"), "epochs": len(recs)}
    out |= ate(recs) | rpe(recs, rpe_delta) | detection(meta, recs) | availability(recs, alert_limit)
    out["time_to_exceed_al_s"] = time_to_exceed(meta, recs, alert_limit)
    return out


COLUMNS = [
    ("run", "Run"), ("scenario", "Scenario"), ("ate_rmse_m", "ATE RMSE m"), ("ate_max_m", "ATE max m"),
    ("rpe_rmse_m", "RPE RMSE m"), ("time_to_detect_s", "Time to detect s"),
    ("false_alarm_epochs", "False-alarm epochs"), ("availability_pct", "Availability %"),
    ("misleading_pct", "Misleading %"), ("time_to_exceed_al_s", "Time to exceed AL s"),
]


def fmt(v) -> str:
    if v is None:
        return NOT_MEASURED
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def table(rows: list[dict], alert_limit: float, rpe_delta: float) -> str:
    lines = ["| " + " | ".join(h for _, h in COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    lines += ["| " + " | ".join(fmt(r.get(k)) for k, _ in COLUMNS) + " |" for r in rows]
    lines.append(f"\nAlert limit (AL) {alert_limit:g} m, RPE delta {rpe_delta:g} s. ATE is unaligned ENU error.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("runs", nargs="+", type=Path)
    p.add_argument("--alert-limit", type=float, default=DEFAULT_ALERT_LIMIT_M)
    p.add_argument("--rpe-delta", type=float, default=DEFAULT_RPE_DELTA_S)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    rows = [evaluate(r, args.alert_limit, args.rpe_delta) for r in args.runs]
    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        print()
    else:
        print(table(rows, args.alert_limit, args.rpe_delta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
