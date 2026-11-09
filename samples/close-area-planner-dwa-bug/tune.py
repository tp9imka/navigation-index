"""Dev-seed sweep (seed 1, 20 layouts) that set the defaults in dwa.py and bug.py.

.venv/bin/python tune.py [--layouts 20] [--seed 1] [--only dwa|bug] [--no-write]

Each variant overrides module globals (the named constants at the top of dwa.py / bug.py) for
its cells only. Writes results/dev_seed<seed>_tuning.md. The report seed 0 is not used here.
"""
from __future__ import annotations

import argparse
import contextlib
import os
import sys
import time

import arena
import bug
import dwa

HERE = os.path.dirname(os.path.abspath(__file__))
FAMILIES = ("random", "u_trap", "narrow_gap")

VARIANTS = [
    # (label, module, factory, overrides)
    ("dwa default", dwa, lambda: dwa.make(), {}),
    ("dwa W_CLEAR 0.3", dwa, lambda: dwa.make(W_CLEAR=0.3), {}),
    ("dwa W_CLEAR 1.0", dwa, lambda: dwa.make(W_CLEAR=1.0), {}),
    ("dwa HORIZON_S 1.0", dwa, lambda: dwa.make(HORIZON_S=1.0), {}),
    ("dwa HORIZON_S 2.5", dwa, lambda: dwa.make(HORIZON_S=2.5), {}),
    ("dwa SAFETY_M 0.04", dwa, lambda: dwa.make(SAFETY_M=0.04), {}),
    ("dwa_mem 3 s", dwa, lambda: dwa.make(memory_s=3.0), {}),
    ("dwa_mem 6 s", dwa, lambda: dwa.make(memory_s=6.0), {}),
    ("bug2 default", bug, lambda: bug.make("bug2"), {}),
    ("bug2 D_DES 0.35", bug, lambda: bug.make("bug2"), {"D_DES": 0.35}),
    ("bug2 D_DES 0.6", bug, lambda: bug.make("bug2"), {"D_DES": 0.6}),
    ("bug2 V_WF 0.9", bug, lambda: bug.make("bug2"), {"V_WF": 0.9}),
    ("tangent_bug DROPOUT_HOLD off", bug, lambda: bug.make("tangent_bug"), {"DROPOUT_HOLD": False}),
    ("tangent_bug V_WF 0.9", bug, lambda: bug.make("tangent_bug"), {"V_WF": 0.9}),
    ("tangent_bug default", bug, lambda: bug.make("tangent_bug"), {}),
    ("tangent_bug TB_MARGIN 0.08", bug, lambda: bug.make("tangent_bug"), {"TB_MARGIN": 0.08}),
    ("tangent_bug H_INC_M 0.6", bug, lambda: bug.make("tangent_bug"), {"H_INC_M": 0.6}),
    ("tangent_bug D_DES 0.35", bug, lambda: bug.make("tangent_bug"), {"D_DES": 0.35}),
]


@contextlib.contextmanager
def patched(mod, over):
    old = {k: getattr(mod, k) for k in over}
    for k, v in over.items():
        setattr(mod, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(mod, k, v)


def budget_check(a, cmd) -> int:
    """Is a narrow_gap timeout the 60 s budget or the follower? Same layouts at 180 s."""
    lines = ["| planner | budget s | reached % | collision % | stuck % | timeout % | median time to goal s "
             "| runs ending in Bug2 FAIL (back at hit point) |",
             "|---|---|---|---|---|---|---|---|"]
    t0 = time.perf_counter()
    for v in ("bug2", "tangent_bug"):
        for budget in (60.0, 180.0):
            cfg = arena.cfg_for("default")
            cfg["max_time_s"] = budget
            made = []

            def fac(v=v):
                p = bug.make(v)
                made.append(p)
                return p

            _, s, _ = arena.run.evaluate(fac, "narrow_gap", a.layouts, a.seed, cfg=cfg)
            fails = sum(1 for p in made if p.mode == "fail")
            lines.append(f"| {v} | {budget:.0f} | {s['reached_pct']} | {s['collision_pct']} | {s['stuck_pct']} "
                         f"| {s['timeout_pct']} | {s['median_time_to_goal_s']} | {fails} |")
            print(lines[-1], flush=True)
    md = (f"`{cmd}` (synthetic arena, dev seed {a.seed}, {a.layouts} narrow_gap layouts, default fan), "
          f"wall {time.perf_counter() - t0:.1f} s\n\n" + "\n".join(lines) + "\n")
    if not a.no_write:
        path = os.path.join(HERE, "results", f"dev_seed{a.seed}_budget.md")
        with open(path, "w") as fh:
            fh.write(md)
        print(f"wrote {os.path.relpath(path, HERE)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--only", default=None, help="label prefix filter, e.g. dwa or bug2")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--budget-check", action="store_true",
                    help="only: Bug2 and TangentBug on narrow_gap, default fan, 60 s vs 180 s budget")
    a = ap.parse_args(argv)
    cmd = "python tune.py " + " ".join(argv if argv is not None else sys.argv[1:])
    if a.budget_check:
        return budget_check(a, cmd)
    lines = ["| variant | fan | " + " | ".join(f"{f} reached / coll / stuck / timeout %" for f in FAMILIES) + " |",
             "|---|---|" + "---|" * len(FAMILIES)]
    t_all = time.perf_counter()
    for label, mod, fac, over in VARIANTS:
        if a.only and not label.startswith(a.only):
            continue
        for fan in arena.FANS:
            cells = []
            with patched(mod, over):
                for fam in FAMILIES:
                    _, s, _ = arena.run.evaluate(fac, fam, a.layouts, a.seed, cfg=arena.cfg_for(fan))
                    cells.append(f"{s['reached_pct']} / {s['collision_pct']} / {s['stuck_pct']} / {s['timeout_pct']}")
            lines.append(f"| {label} | {fan} | " + " | ".join(cells) + " |")
            print(lines[-1], flush=True)
    wall = time.perf_counter() - t_all
    md = (f"`{cmd}` (synthetic arena, dev seed {a.seed}, {a.layouts} layouts per cell), wall {wall:.1f} s\n\n"
          + "\n".join(lines) + "\n")
    if not a.no_write:
        os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
        path = os.path.join(HERE, "results", f"dev_seed{a.seed}_tuning.md")
        with open(path, "w") as fh:
            fh.write(md)
        print(f"wrote {os.path.relpath(path, HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
