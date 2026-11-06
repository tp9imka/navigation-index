#!/usr/bin/env python3
"""Per-flight metrics and the ranked recipe table for the anti-spoof config sweep. Stdlib only;
reuses samples/autopilot-spoof-response/spoof_analyse.py for the shared EKF metrics.

    python3 resil_analyse.py runs/*.raw.jsonl --out data/flights.json --ranking data/ranking.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "autopilot-spoof-response"))

import spoof_analyse as A  # noqa: E402

LUA_SWITCH_TEXT = "RESIL: GPS rejected"
SAFE_EKF_ERR_M = 25.0          # "kept flying safely": EKF error after onset stays under this
SAFE_DEV_M = 25.0              # ... and so does the true cross-track deviation


def switch_events(rows: list[dict]) -> list[dict]:
    """Source switches away from GNSS: companion monitor action or the Lua applet's STATUSTEXT."""
    out = []
    for r in rows:
        if r["type"] == "COMPANION_ACTION" and r.get("action") == "set_ekf_source_set":
            out.append({"t": r.get("t"), "by": "companion", "reason": r.get("reason")})
        elif r["type"] == "STATUSTEXT" and r.get("text", "").startswith(LUA_SWITCH_TEXT):
            out.append({"t": r.get("t"), "by": "lua", "reason": r["text"]})
    return out


def lane_switches(rows: list[dict]) -> int:
    return sum(1 for r in rows if r["type"] == "STATUSTEXT" and r.get("text", "").startswith("EKF3 lane switch"))


def load_flags(log: Path) -> list[dict] | None:
    p = log.with_name(log.name.replace(".raw.jsonl", ".flags.jsonl"))
    if not p.exists():
        return None
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def gnss_status(rows: list[dict], flags: list[dict] | None, onset: float) -> dict:
    """PX4 only: EKF2 control status sampled from the PX4 shell every ~2 s (sim clock).
    gnss_pos_off_s = first sample after onset with GNSS position fusion off; gnss_off_before_onset
    = GNSS position fusion was already off in the 20 s before onset (GNSS lost without an attack)."""
    if not flags:
        return {"gnss_pos_off_s": None, "gnss_off_before_onset": None, "ekf2_flag_samples": 0}
    t_auto = next((r["t_sim"] - r["t"] for r in rows if r.get("t") is not None and r.get("t_sim")), None)
    if t_auto is None:
        return {"gnss_pos_off_s": None, "gnss_off_before_onset": None, "ekf2_flag_samples": len(flags)}
    pts = [(f["t_sim"] - t_auto, f) for f in flags]
    before = [f for t, f in pts if onset - 20.0 <= t < onset]
    off_after = [t for t, f in pts if t >= onset and not f.get("cs_gnss_pos", True)]
    return {"gnss_pos_off_s": round(off_after[0] - onset, 1) if off_after else None,
            "gnss_off_before_onset": any(not f.get("cs_gnss_pos", True) for f in before) if before else None,
            "gnss_hgt_fault_seen": any(f.get("cs_gnss_hgt_fault") for _, f in pts),
            "aux_gpos_seen": any(f.get("cs_aux_gpos") for _, f in pts),
            "ev_vel_seen": any(f.get("cs_ev_vel") for _, f in pts),
            "ekf2_flag_samples": len(flags)}


def summarise(rows: list[dict], flags: list[dict] | None = None) -> dict:
    exp = next(r for r in rows if r["type"] == "EXPERIMENT")
    clean = exp["spoof"] == "none"
    if clean:
        exp["rate_mps"] = 0.0          # spoof_analyse names cases with the rate
    s = A.summarise(rows)
    onset = exp["onset_s"]
    sw = switch_events(rows)
    sw_after = [e for e in sw if e["t"] is not None and e["t"] >= onset]
    first_sw = round(sw_after[0]["t"] - onset, 1) if sw_after else None
    flag = s["first_gps_flag_s"]
    gs = gnss_status(rows, flags, onset)
    # Reject = GNSS stops being used: source switch (Lua / companion) or EKF2 GNSS position fusion
    # off. The glitch flag alone is not a reject: both EKFs keep or resume fusing after it.
    rejects = [x for x in (first_sw, gs["gnss_pos_off_s"]) if x is not None]
    out = {
        "case": f"{exp['autopilot']}-{exp['config']}-{'clean' if clean else 'coherent-%g' % exp['rate_mps']}-s{exp['seed']}",
        "autopilot": exp["autopilot"], "config": exp["config"], "seed": exp["seed"],
        "clean": clean, "rate_mps": None if clean else exp["rate_mps"],
        "params_requested": s["params_requested"], "params_echoed": s["params_echoed"],
        "outcome": s["outcome"], "failsafe_s": s["failsafe_mode_change_s"],
        "max_dev_m": s["max_cross_track_dev_m"], "ekf_err_max_m": s["ekf_err_max_m"],
        "ekf_err_end_m": s["ekf_err_end_m"], "spoof_offset_end_m": s["spoof_offset_end_m"],
        "capture_ratio_end": s["capture_ratio_end"],
        "first_gps_flag_s": flag, "gps_flag_reports": s["gps_flag_reports"],
        "switch_s": first_sw, "switches": len(sw), "switch_by": sw[0]["by"] if sw else None,
        "reject_s": min(rejects) if rejects else None,
        "lane_switches": lane_switches(rows),
        **gs,
        "resets": s["reset_count"],
        "statustext_after_onset": s["statustext_after_onset"],
    }
    out["safe"] = (not clean and out["failsafe_s"] is None and out["outcome"] == "mission_complete"
                   and out["ekf_err_max_m"] <= SAFE_EKF_ERR_M and out["max_dev_m"] <= SAFE_DEV_M)
    out["false_alarm"] = clean and (len(sw) > 0 or flag is not None or out["failsafe_s"] is not None
                                    or out["outcome"] != "mission_complete" or bool(gs["gnss_off_before_onset"])
                                    or gs["gnss_pos_off_s"] is not None)
    return out


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def _max(xs):
    xs = [x for x in xs if x is not None]
    return round(max(xs), 1) if xs else None


def ranking(flights: list[dict]) -> list[dict]:
    """One row per (autopilot, config). Rank: configs with any false alarm on a clean flight go
    last; then spoofed flights flown safely, failsafes, worst max deviation. Incomplete flights
    (companion timed out) are counted, not scored."""
    by, incomplete = {}, {}
    for f in flights:
        key = (f["autopilot"], f["config"])
        if f["outcome"] == "incomplete":
            incomplete[key] = incomplete.get(key, 0) + 1
            by.setdefault(key, [])
            continue
        by.setdefault(key, []).append(f)
    rows = []
    for (ap, cfg), fs in by.items():
        spoofed = [f for f in fs if not f["clean"]]
        clean = [f for f in fs if f["clean"]]
        per_rate = {}
        for r in sorted({f["rate_mps"] for f in spoofed}):
            g = [f for f in spoofed if f["rate_mps"] == r]
            per_rate[f"{r:g}"] = {
                "n": len(g), "safe": sum(f["safe"] for f in g),
                "max_dev_m": [f["max_dev_m"] for f in g], "ekf_err_max_m": [f["ekf_err_max_m"] for f in g],
                "reject_s": [f["reject_s"] for f in g], "switch_s": [f["switch_s"] for f in g],
                "failsafe_s": [f["failsafe_s"] for f in g], "capture_ratio_end": [f["capture_ratio_end"] for f in g],
            }
        rows.append({
            "autopilot": ap, "config": cfg, "spoofed_flights": len(spoofed), "clean_flights": len(clean),
            "incomplete_flights": incomplete.get((ap, cfg), 0),
            "safe": sum(f["safe"] for f in spoofed),
            "false_alarms": sum(f["false_alarm"] for f in clean),
            "failsafes": sum(f["failsafe_s"] is not None for f in fs),
            "worst_dev_m": _max(f["max_dev_m"] for f in spoofed),
            "worst_ekf_err_m": _max(f["ekf_err_max_m"] for f in spoofed),
            "median_reject_s": _med(f["reject_s"] for f in spoofed),
            "rejected": sum(f["reject_s"] is not None for f in spoofed),
            "gnss_off_before_onset": sum(bool(f.get("gnss_off_before_onset")) for f in fs),
            "clean_max_dev_m": _max(f["max_dev_m"] for f in clean),
            "clean_ekf_err_max_m": _max(f["ekf_err_max_m"] for f in clean),
            "params_ok": all(set(f["params_echoed"]) >= set(f["params_requested"]) for f in fs),
            "per_rate": per_rate,
        })
    rows.sort(key=lambda r: (r["autopilot"], r["false_alarms"] > 0, -r["safe"], r["failsafes"], r["worst_dev_m"] or 0))
    for ap in {r["autopilot"] for r in rows}:
        for i, r in enumerate([r for r in rows if r["autopilot"] == ap], 1):
            r["rank"] = i
    return rows


def fmt(r: dict) -> str:
    rates = " ".join(f"{k}:{v['safe']}/{v['n']}" for k, v in r["per_rate"].items())
    return (f"{r['autopilot']:9} #{r['rank']} {r['config']:24} safe {r['safe']}/{r['spoofed_flights']} [{rates}] "
            f"FA {r['false_alarms']}/{r['clean_flights']} FS {r['failsafes']} worst dev {r['worst_dev_m']} "
            f"ekf {r['worst_ekf_err_m']} reject med {r['median_reject_s']} ({r['rejected']}) params_ok {r['params_ok']}")


def _rng(xs, nd=1):
    xs = [x for x in xs if x is not None]
    if not xs:
        return "-"
    lo, hi = min(xs), max(xs)
    return f"{lo:.{nd}f}" if lo == hi else f"{lo:.{nd}f}-{hi:.{nd}f}"


def markdown(rank: list[dict]) -> str:
    """Ranked recipe table: per rate, safe flights / max EKF error range / reject time range."""
    rates = sorted({k for r in rank for k in r["per_rate"]}, key=float)
    head = ("| Rank | Autopilot / config | Safe | " + " | ".join(f"{k} m/s: safe, max EKF err m, GNSS out s" for k in rates)
            + " | Clean: false alarms, max EKF err m | Failsafes |")
    out = [head, "|" + "---|" * (5 + len(rates))]
    for r in rank:
        cells = []
        for k in rates:
            v = r["per_rate"].get(k)
            if not v:
                cells.append("-")
                continue
            rej = [x for x in v["reject_s"] if x is not None]
            cells.append(f"{v['safe']}/{v['n']}, {_rng(v['ekf_err_max_m'])}, "
                         + (f"{_rng(rej)} ({len(rej)}/{v['n']})" if rej else "none"))
        out.append(f"| {r['rank']} | {r['autopilot']} `{r['config']}` | {r['safe']}/{r['spoofed_flights']} | "
                   + " | ".join(cells)
                   + f" | {r['false_alarms']}/{r['clean_flights']}, {r['clean_ekf_err_max_m']} | {r['failsafes']} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("logs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--ranking", type=Path)
    ap.add_argument("--markdown", action="store_true", help="print the ranked recipe table as markdown")
    a = ap.parse_args(argv)
    flights = []
    for p in sorted(a.logs):
        try:
            flights.append(summarise(A.load(p), load_flags(p)))
        except (StopIteration, KeyError, ValueError) as e:
            print(f"{p.name}: incomplete log ({e!r})", file=sys.stderr)
    rank = ranking(flights)
    for r in rank:
        print(fmt(r))
    if a.markdown:
        print(markdown(rank))
    if a.out:
        a.out.write_text(json.dumps(flights, indent=1))
    if a.ranking:
        a.ranking.write_text(json.dumps(rank, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
