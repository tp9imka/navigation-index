"""Export one kill-test layout as a compact replay for the showcase story section.

.venv/bin/python export_replay.py                 # => ../../site/data/showcase/story/kill_test.json
.venv/bin/python export_replay.py --index 43      # another seed-0 layout (default: picked by the rule below)

One random-family layout, seed 0, unsensed obstacles on, VIO "jump" fault, three arms:
F0 (no filter), F2 (PX4-CBF as shipped) and F5 (ours: PL margin + hover on ambiguity).
Per arm, at 10 Hz: true path, estimated path the planner saw, filter intervened, F5 hover flag.
The run itself is run_kill.run_one, unchanged: the adapter and the filter are wrapped only to
record, so outcome and min clearance are compared against the published per-run rows
(F0: results/kill_a_unsensed_on_0.json, F2 and F5: results/kill_d_unsensed_on_0.json). The file
also carries the headline numbers, recomputed from the result JSONs with 95 % Wilson intervals.

Layout rule (default): the first seed-0 layout where F0 and F2 both hit an unsensed obstacle in the
jump case and one of the two hits is a thin pole (most unsensed hits are glass panels). That layout
is picked to show the failure mode; it is not typical.
All inputs are synthetic. Stdlib + the sample's numpy / scipy.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import platform
import sys

import numpy as np

import arena
import filters
import run_kill
import unsensed

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "site", "data", "showcase", "story", "kill_test.json"))
SEED, CASE = 0, "jump"
ARMS = (("F0", "no filter", "kill_a_unsensed_on_0.json"),
        ("F2", "PX4-CBF as shipped", "kill_d_unsensed_on_0.json"),
        ("F5", "ours: PL margin + hover", "kill_d_unsensed_on_0.json"))
REC_EVERY = 5                    # physics steps (50 Hz) per recorded sample => 10 Hz
CHECK = ("outcome", "min_clearance_m", "path_length_m", "time_to_goal_s", "hit_unsensed")

world_json = importlib.import_module("close_area_arena.world_json")


def _tables():
    spec = importlib.util.spec_from_file_location("kill_e_tables", os.path.join(RESULTS, "kill_e_tables.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def r3(v):
    return None if v is None else round(float(v), 3)


def run_arm(arm: str, index: int):
    """run_kill.run_one, unchanged, with recording wrappers on the adapter and the filter.
    Returns (result row, 10 Hz trace, collision contact or None)."""
    tr = {"t": [], "truth": [], "est": [], "sigma": [], "int": [], "hover": []}
    state = {"k": 0, "ad": None, "truth": None}
    base, make = arena.adapter.SimAdapter, filters.make

    class RecAdapter(base):
        def pose(self):
            state["ad"], state["truth"] = self, self.truth()
            return super().pose()

    def rec_make(name, **kw):
        f = make(name, **kw)
        inner = f.filter

        def filt(*a):
            out = inner(*a)
            k = state["k"]
            state["k"] += 1
            if k % REC_EVERY == 0:
                p, t = a[1], state["truth"]          # a[1]: the estimate given to the filter
                tr["t"].append(round(t.t, 2))
                tr["truth"].append([r3(t.x), r3(t.y)])
                tr["est"].append([r3(p.x), r3(p.y)])
                tr["sigma"].append(r3(p.sigma_xy))
                tr["int"].append(int(bool(out[1])))
                tr["hover"].append(int(bool(getattr(f, "hover_now", False))))
            return out
        f.filter = filt
        return f

    arena.adapter.SimAdapter, filters.make = RecAdapter, rec_make
    try:
        row = run_kill.run_one(arm, CASE, True, index, SEED)
    finally:
        arena.adapter.SimAdapter, filters.make = base, make
    end = state["ad"].truth()                        # final state: contact point or goal
    if end.t - tr["t"][-1] > 1e-6:
        tr["t"].append(round(end.t, 2))
        tr["truth"].append([r3(end.x), r3(end.y)])
        for k in ("est", "sigma", "int", "hover"):
            tr[k].append(tr[k][-1])
    hit = None
    if row["collision"]:
        w0 = arena.world.make_world("random", SEED, index)
        _, placed = unsensed.add_unsensed(w0, SEED, index)
        d, u = min(((unsensed.unsensed_sdf([u], end.x, end.y), u) for u in placed), key=lambda z: z[0])
        uns = bool(d < w0.clearance(end.x, end.y))
        hit = {"t": round(end.t, 2), "xy": [r3(end.x), r3(end.y)], "what": u.kind if uns else "mapped obstacle",
               "unsensed": uns}
    return row, tr, hit


def published(fname: str, arm: str, index: int) -> dict:
    d = json.load(open(os.path.join(RESULTS, fname)))
    for r in d["runs"]:
        if r["arm"] == arm and r["case"] == CASE and r["index"] == index:
            return r
    raise KeyError((fname, arm, index))


def pick_layout() -> int:
    a = {r["index"]: r for r in json.load(open(os.path.join(RESULTS, "kill_a_unsensed_on_0.json")))["runs"]
         if r["arm"] == "F0" and r["case"] == CASE}
    d = {r["index"]: r for r in json.load(open(os.path.join(RESULTS, "kill_d_unsensed_on_0.json")))["runs"]
         if r["arm"] == "F2" and r["case"] == CASE}
    for i in sorted(a):
        if a[i]["hit_unsensed"] and d[i]["hit_unsensed"]:
            if any(run_arm(arm, i)[2]["what"] == "pole" for arm in ("F0", "F2")):
                return i
    raise RuntimeError("no layout matches the rule")


def headline() -> dict:
    """Numbers for the status card, recomputed from the result JSONs (same counting as kill_e_tables.py)."""
    T = _tables()
    cells = {}
    files = {0: "kill_d_unsensed_on_0.json", 1: "kill_e_unsensed_on_1.json", 2: "kill_e_unsensed_on_2.json"}
    for s, f in files.items():
        _, c = T.load(os.path.join(RESULTS, f))
        cells[s] = c

    def pool(arm, case, seeds):
        n = k = rc = 0
        for s in seeds:
            c = cells[s].get((arm, case))
            if c:
                n, k, rc = n + c[0], k + c[1], rc + c[2]
        lo, hi = T.wilson(k, n)
        return {"runs": n, "collisions": k, "collision_pct": round(100 * k / n, 1),
                "ci95": [round(lo, 1), round(hi, 1)], "reached": rc, "reached_pct": round(100 * rc / n, 1)}
    F2j = pool("F2", "jump", (0, 1, 2))
    F5j = pool("F5", "jump", (0, 1, 2))
    return {
        "input": "synthetic",
        "source": ["samples/close-area-safety-filter/results/kill_d_unsensed_on_0.json",
                   "samples/close-area-safety-filter/results/kill_e_unsensed_on_1.json",
                   "samples/close-area-safety-filter/results/kill_e_unsensed_on_2.json"],
        "criterion": "doc 04 section 3.4: collisions <= 1 % in every fault case and reach >= 90 % of F2",
        "verdict": "FAIL",
        "F5_jump_heldout": pool("F5", "jump", (1, 2)),
        "F5_jump_seeds012": F5j,
        "F4_jump_seeds012": pool("F4@eps_m=0.2", "jump", (0, 1, 2)),
        "F2_jump_seeds012": F2j,
        "F5_jump_reach_ratio_vs_F2": round(F5j["reached"] / F2j["reached"], 2),
        "F5_other_cases_seeds012": {c: pool("F5", c, (0, 1, 2)) for c in ("none", "bias", "dropout", "uwb_nlos", "both")},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", type=int, default=None)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    index = a.index if a.index is not None else pick_layout()
    w0 = arena.world.make_world("random", SEED, index)
    _, placed = unsensed.add_unsensed(w0, SEED, index)
    arms, all_ok = [], True
    for arm, label, fname in ARMS:
        row, tr, hit = run_arm(arm, index)
        pub = published(fname, arm, index)
        check = {k: {"export": row.get(k), "published": pub.get(k)} for k in CHECK}
        ok = all(v["export"] == v["published"] for v in check.values())
        all_ok &= ok
        arms.append({"arm": arm, "label": label, "score": {k: row.get(k) for k in
                     ("outcome", "time_to_goal_s", "min_clearance_m", "path_length_m", "duration_s",
                      "max_pose_error_m", "intervention_frac", "ended_in_hover")},
                     "hit": hit, "fault": row["fault_log"], "t": tr["t"], "truth": tr["truth"], "est": tr["est"], "sigma": tr["sigma"],
                     "intervened": tr["int"], "hover": tr["hover"] if arm == "F5" else None,
                     "check": {"file": "samples/close-area-safety-filter/results/" + fname, "fields": check, "match": ok}})
        print(f"{arm}: {row['outcome']} min clr {row['min_clearance_m']} hit {hit} match {ok}")
    wj = world_json.to_json(w0, radius=arena.run.DEFAULTS["vehicle"]["radius"])
    wj["index"] = index
    doc = {
        "schema": "close-area-story-replay/1", "kind": "kill_test", "input": "synthetic",
        "generated_by": "samples/close-area-safety-filter/export_replay.py",
        "command": "python export_replay.py " + " ".join(argv if argv is not None else sys.argv[1:]),
        "family": "random", "seed": SEED, "index": index, "case": CASE, "hz": 50 / REC_EVERY,
        "selection": ("first seed-0 layout where F0 and F2 both hit an unsensed obstacle in the jump case and "
                      "one hit is a pole; picked to show the failure mode, not typical") if a.index is None else "chosen by --index",
        "planner": "arena astar_esdf known_map=True (map includes the unsensed obstacles)",
        "world": wj,
        "unsensed": [{"kind": u.kind, "cx": r3(u.cx), "cy": r3(u.cy), "r": r3(u.r), "hx": r3(u.hx), "hy": r3(u.hy)}
                     for u in placed],
        "goal_tol_m": arena.scorer.GOAL_TOL,
        "arms": arms, "matches_published": all_ok,
        "headline": headline(),
        "env": {"python": platform.python_version(), "numpy": np.__version__, "machine": platform.machine(),
                "system": platform.system()},
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    print(f"wrote {a.out} ({os.path.getsize(a.out)} bytes), matches published rows: {all_ok}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
