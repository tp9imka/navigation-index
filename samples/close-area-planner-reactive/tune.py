"""Dev-seed sweeps that set the shipped defaults. Seed 1, 20 layouts, never seed 0 (the report seed).

.venv/bin/python tune.py      # about 1.5 min, writes results/dev_seed1_tuning.md

Each cell is "reached % / collision %".
"""
import os
import time

import arena
import apf
import vfh_plus

HERE = os.path.dirname(os.path.abspath(__file__))
SEED, N = 1, 20


def cell(make, fan, fam):
    _, s, _ = arena.run.evaluate(make, fam, N, SEED, cfg=arena.cfg_for(fan))
    return f"{s['reached_pct']} / {s['collision_pct']}"


def main():
    t0 = time.perf_counter()
    cols = [(f, m) for f in arena.FANS for m in ("random", "u_trap", "narrow_gap")]
    out = [f"`python tune.py` (synthetic arena, seed {SEED}, {N} layouts per cell). Cells: reached % / collision %.\n",
           "## APF escape variants\n",
           "stall_window: also trigger the escape when distance to B fell < 0.3 m over the last 3 s. "
           "wf_weighted: wall direction = weighted mean of close returns instead of the nearest return.\n",
           "| stall_window | wf_weighted | " + " | ".join(f"{f} {m}" for f, m in cols) + " |",
           "|---|---|" + "---|" * len(cols)]
    for sw in (False, True):
        for ww in (False, True):
            r = [cell(lambda: apf.make(stall_window=sw, wf_weighted=ww), f, m) for f, m in cols]
            out.append(f"| {sw} | {ww} | " + " | ".join(r) + " |")
            print(out[-1], flush=True)
    cols2 = [(f, m) for f in arena.FANS for m in ("random", "narrow_gap")]
    out += ["\n## VFH+ safety distance and thresholds\n",
            "tau_low = tau_high / 2.\n",
            "| d_s m | tau_high | " + " | ".join(f"{f} {m}" for f, m in cols2) + " |",
            "|---|---|" + "---|" * len(cols2)]
    for ds in (0.05, 0.1, 0.2):
        for th in (12.0, 24.0, 48.0):
            r = [cell(lambda: vfh_plus.make(d_s=ds, tau_high=th, tau_low=th / 2), f, m) for f, m in cols2]
            out.append(f"| {ds} | {th:g} | " + " | ".join(r) + " |")
            print(out[-1], flush=True)
    out.append(f"\nShipped defaults: APF stall_window False, wf_weighted False; VFH+ d_s 0.1, tau_high 24, tau_low 12. "
               f"Wall {time.perf_counter() - t0:.0f} s.\n")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "dev_seed1_tuning.md"), "w") as fh:
        fh.write("\n".join(out))


if __name__ == "__main__":
    main()
