"""Markdown per-test table across replay variants. Stdlib only.

  python3 summary_table.py A=results/results_A.json C=results/results_C.json ...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOP_DETECTORS = 2


def cell(w):
    if not w.get("covered"):
        return "not in log"
    if not w["detected"]:
        return "no"
    dets = ", ".join(list(w["detector_epochs"])[:TOP_DETECTORS])
    latched = " L" if w["alarm_latched_at_start"] else ""
    return f"yes {w['ttd_s']} s{latched} ({100 * w['alert_epoch_fraction']:.0f}%): {dets}"


def fa_cell(fa):
    if not fa or not fa["epochs"]:
        return "-"
    dets = ", ".join(list(fa["detector_epochs"])[:TOP_DETECTORS]) or "none"
    return f"{fa['alarm_raises']} raises / {fa['hours']} h, {100 * fa['alarm_epoch_fraction']:.0f}% alarm: {dets}"


def main(argv):
    variants = [(a.split("=", 1)[0], json.loads(Path(a.split("=", 1)[1]).read_text())) for a in argv]
    names = [n for n, _ in variants]
    print("| test | kind | label | " + " | ".join(names) + " |")
    print("|---|---|---|" + "---|" * len(names))
    files = [r["file"] for r in variants[0][1]["results"]]
    for f in files:
        per_variant = [next((r for r in v["results"] if r["file"] == f), None) for _, v in variants]
        base = next(r for r in per_variant if r)
        for i, w in enumerate(base["windows"]):
            cells = [cell(r["windows"][i]) if r else "n/a" for r in per_variant]
            print(f"| {w['test']} | {w['kind']} | {w['source']} | " + " | ".join(cells) + " |")
    print("\n| file | span | " + " | ".join(f"{n} no-logged-test" for n in names) + " |")
    print("|---|---|" + "---|" * len(names))
    for f in files:
        per_variant = [next((r for r in v["results"] if r["file"] == f), None) for _, v in variants]
        base = next(r for r in per_variant if r)
        cells = [fa_cell(r["no_logged_test"]) if r else "n/a" for r in per_variant]
        print(f"| {Path(f).name} | {base['span_utc'][0]}-{base['span_utc'][1]} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(sys.argv[1:])
