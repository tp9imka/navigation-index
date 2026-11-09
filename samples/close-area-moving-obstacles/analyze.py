"""Post-hoc facts the README quotes, from results/moving_0.json (no new runs).

python analyze.py [--seed 0]   => results/analysis_<seed>.md

- which layouts each arm got stuck on, per mover speed
- whether the A* + F2 stuck layouts are the ones F2 already gets stuck on with no movers
  (samples/close-area-safety-filter results/kill_a_unsensed_off_0.json, F2, truth pose, layouts < N)
- F2 intervention fraction (median per speed)
- A* collisions: vehicle speed and closing speed at contact (who closed the gap)
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KILL = os.path.join(HERE, "..", "close-area-safety-filter", "results", "kill_a_unsensed_off_0.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    src = os.path.join(HERE, "results", f"moving_{a.seed}.json")
    d = json.load(open(src))
    runs, speeds, arms, n = d["runs"], d["speeds"], list(d["arms"]), d["layouts"]
    sel = lambda arm, sp: [r for r in runs if r["arm"] == arm and r["speed_mps"] == sp]
    out = [f"Source: results/moving_{a.seed}.json (`{d['command']}`, synthetic). Written by `python analyze.py`.", ""]
    out += ["## Stuck layouts", "", "| arm | mover speed m/s | stuck layouts |", "|---|---|---|"]
    for arm in arms:
        for sp in speeds:
            out.append(f"| {arm} | {sp} | {', '.join(str(r['index']) for r in sel(arm, sp) if r['stuck']) or '-'} |")
    if os.path.exists(KILL) and a.seed == 0:
        k = json.load(open(KILL))["runs"]
        ks = sorted(r["index"] for r in k if r["arm"] == "F2" and r["case"] == "truth" and r["stuck"] and r["index"] < n)
        out += ["", f"close-area-safety-filter kill_a_unsensed_off_0.json, F2, truth pose, no movers, layouts 0-{n - 1}: "
                f"stuck on {', '.join(map(str, ks))} ({len(ks)} of {n})."]
        for sp in speeds:
            s = {r["index"] for r in sel("astar_f2", sp) if r["stuck"]}
            out.append(f"- astar_f2 at {sp} m/s: {len(s)} stuck, {len(s & set(ks))} of them also stuck there; "
                       f"new: {sorted(s - set(ks)) or 'none'}")
    if "astar_f2" in arms:
        out += ["", "## F2 intervention fraction (share of 50 Hz steps with eta > 0)", "",
                "| mover speed m/s | median | max |", "|---|---|---|"]
        for sp in speeds:
            v = [r["intervention_frac"] for r in sel("astar_f2", sp)]
            out.append(f"| {sp} | {round(float(np.median(v)), 3)} | {round(float(np.max(v)), 3)} |")
    out += ["", "## Mover collisions: vehicle speed and closing speed at contact", "",
            "| arm | mover speed m/s | mover collisions | vehicle speed median m/s | min | max "
            "| closing speed median m/s | min | max | closing < 0.1 m/s |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm in arms:
        for sp in speeds:
            c = [r for r in sel(arm, sp) if r["hit"] == "mover"]
            if not c:
                continue
            v = [r["speed_at_contact_mps"] for r in c]
            cl = [r["vehicle_closing_mps"] for r in c]
            q = lambda x, f: round(float(f(x)), 3)
            out.append(f"| {arm} | {sp} | {len(c)} | {q(v, np.median)} | {q(v, np.min)} | {q(v, np.max)} "
                       f"| {q(cl, np.median)} | {q(cl, np.min)} | {q(cl, np.max)} | {sum(x < 0.1 for x in cl)} |")
    path = os.path.join(HERE, "results", f"analysis_{a.seed}.md")
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
