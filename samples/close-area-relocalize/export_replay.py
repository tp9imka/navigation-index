"""Export one relocalization layout as a compact replay for the showcase story section.

.venv/bin/python export_replay.py                 # => ../../site/data/showcase/story/relocalize.json
.venv/bin/python export_replay.py --index 75      # another seed-0 layout (default: picked by the rule below)

One random-family layout, seed 0, VIO "jump" fault (0.5 m step), A* known map, three arms:
  estimator  (a) arena estimator only, no relocalization (experiment.py)
  single     (b) commit to the best match at once + innovation test (experiment.py)
  multi_ig   (f) up to 5 hypotheses, RatioPersistence, info-gain move after 1 s (disambiguate.py)
Per arm, at 10 Hz (every pose-source call): true position, the pose the planner saw, lost / moving
flags, and for (b) and (f) the scored hypotheses of that scan (x, y, score) as ghosts. Loss events
come from the pose source's own event log: trigger, accept, error to truth, wrong commit (> 0.5 m).

The runs are run.run_one with the same builders as run_disambiguate.py; the pose source is wrapped
only to record. Outcome, min clearance, path length, time to goal and wrong commits are compared
against the published rows: (a) results/reloc_random_0.json, (b) and (f) results/disamb_random_0.json.
The file also carries the headline numbers from results/reloc_matrix_matrix.json,
sparse_random_0.json and stalemap_random_2.json, with 95 % Wilson intervals.

Layout rule (default): the first seed-0 jump layout where (b) made a wrong commit and (f) flew a
disambiguating move. Picked to show both mechanisms; not typical. All inputs are synthetic.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import platform
import sys

import numpy as np

from arena import run, world
import experiment as X
import run_disambiguate as RD

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "site", "data", "showcase", "story", "relocalize.json"))
SEED, FAULT, FAMILY = 0, "jump", "random"
ARMS = (("estimator", "(a) estimator only", "reloc_random_0.json"),
        ("single", "(b) single: commit at once", "disamb_random_0.json"),
        ("multi_ig", "(f) multi + info-gain move", "disamb_random_0.json"))
CHECK = ("outcome", "min_clearance_m", "path_length_m", "time_to_goal_s", "wrong_commits")
Z = 1.959964

world_json = importlib.import_module("close_area_arena.world_json")
estimator = importlib.import_module("close_area_arena.estimator")


def r3(v):
    return None if v is None else round(float(v), 3)


def wilson(k, n):
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return [round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1)]


class Recorder:
    """Pose-source wrapper: calls the real source, records what it saw and decided."""

    def __init__(self, src):
        self.src = src
        self.rows = []
        self.hyps = None
        m = getattr(src, "matcher", None)
        if m is not None and not hasattr(src, "last_hyps"):      # (b): record its matches too
            inner = m.hypotheses

            def rec(*a, **kw):
                self.hyps = inner(*a, **kw)
                return self.hyps
            m.hypotheses = rec

    def __call__(self, truth):
        self.hyps = None
        out = self.src(truth)
        s = self.src
        hy = getattr(s, "last_hyps", None) if hasattr(s, "last_hyps") else self.hyps
        lost = getattr(s, "state", "nominal") == "reloc"
        moving = getattr(s, "cmd", None) is not None
        self.rows.append([round(truth.t, 2), r3(truth.x), r3(truth.y), r3(out.x), r3(out.y), int(lost), int(moving),
                          [[r3(h.x), r3(h.y), round(float(h.score), 3)] for h in hy] if hy else None])
        return out


def run_arm(arm: str, index: int):
    w = world.make_world(FAMILY, SEED, index)
    est = estimator.make_pose_source_factory(FAULT, dark=True, sink=[])(w, SEED, index)
    if arm == "estimator":
        src, planner = est, X.planner_for(arm)
    else:
        src, planner = RD.build(arm, w, est, SEED, index)
    rec = Recorder(src)
    row, ts, xy = run.run_one(planner, w, SEED, index, run.DEFAULTS, rec)
    row.update(RD.extra(row, est, src, est.fault) if arm != "estimator" else X.row_extra(row, est, src, est.fault))
    return w, est, row, rec.rows, (float(ts[-1]), float(xy[-1][0]), float(xy[-1][1]))


def published(fname: str, arm: str, index: int) -> dict:
    d = json.load(open(os.path.join(RESULTS, fname)))["results"][FAULT][arm]["runs"]
    return next(r for r in d if r["index"] == index)


def pick_layout() -> int:
    d = json.load(open(os.path.join(RESULTS, "disamb_random_0.json")))["results"][FAULT]
    S = {r["index"]: r for r in d["single"]["runs"]}
    F = {r["index"]: r for r in d["multi_ig"]["runs"]}
    for i in sorted(S):
        if S[i]["wrong_commits"] and any(m.get("move") for e in F[i]["events"] for m in e.get("moves", [])):
            return i
    raise RuntimeError("no layout matches the rule")


def headline() -> dict:
    m = json.load(open(os.path.join(RESULTS, "reloc_matrix_matrix.json")))
    fam = {}
    for f, cells in m["results"].items():
        n = sum(cells[fl]["multi_ig"]["summary"]["n"] for fl in cells)
        k = sum(cells[fl]["multi_ig"]["summary"]["reached"] for fl in cells)
        wc = sum(cells[fl]["multi_ig"]["summary"]["wrong_commits"] for fl in cells)
        coll = [cells[fl]["multi_ig"]["summary"]["collision_pct"] for fl in sorted(cells)]
        fam[f] = {"runs": n, "reached": k, "reached_pct": round(100 * k / n, 1), "ci95": wilson(k, n),
                  "wrong_commits": wc, "collision_pct_dropout_jump": coll,
                  "pass": bool(100 * k / n >= 95 and wc == 0)}
    sp = json.load(open(os.path.join(RESULTS, "sparse_random_0.json")))["results"]["crazyflie"]
    cf = {}
    for fl in ("dropout", "jump"):
        s = sp[fl]["spin_ig"]["summary"]
        k = round(s["reached_pct"] * s["n"] / 100)
        cf[fl] = {"runs": s["n"], "reached": k, "reached_pct": s["reached_pct"], "ci95": wilson(k, s["n"]),
                  "wrong_commits": s["wrong_commits"], "collision_pct": s["collision_pct"]}
    st = json.load(open(os.path.join(RESULTS, "stalemap_random_2.json")))["results"]["c_added"]
    ca = {}
    for fl in ("dropout", "jump"):
        s = st[fl]["multi_ig"]["summary"]
        k = round(s["collision_pct"] * s["n"] / 100)
        ca[fl] = {"runs": s["n"], "collisions": k, "collision_pct": s["collision_pct"], "ci95": wilson(k, s["n"]),
                  "reached_pct": s["reached_pct"], "wrong_commits": s["wrong_commits"]}
    return {
        "input": "synthetic",
        "source": ["samples/close-area-relocalize/results/reloc_matrix_matrix.json",
                   "samples/close-area-relocalize/results/sparse_random_0.json",
                   "samples/close-area-relocalize/results/stalemap_random_2.json"],
        "criterion": "per family: (f) reached >= 95 % and 0 wrong commits (held-out seeds 2-4, both faults pooled)",
        "verdict": "PASS in %d of %d families" % (sum(v["pass"] for v in fam.values()), len(fam)),
        "matrix_seeds": m["seeds"], "families": fam,
        "crazyflie_4beam_spin_ig_seed0": cf,
        "unmapped_obstacles_c_added_seed2": ca,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", type=int, default=None)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    index = a.index if a.index is not None else pick_layout()
    arms, all_ok, w, dark = [], True, None, None
    for arm, label, fname in ARMS:
        w, est, row, rows, end = run_arm(arm, index)
        if end[0] - rows[-1][0] > 1e-6:                   # final truth state (contact or goal)
            rows.append([round(end[0], 2), r3(end[1]), r3(end[2]), rows[-1][3], rows[-1][4], rows[-1][5], rows[-1][6], None])
        pub = published(fname, arm, index)
        check = {k: {"export": row.get(k), "published": pub.get(k)} for k in CHECK}
        ok = all(v["export"] == v["published"] for v in check.values())
        all_ok &= ok
        dark = [z.to_list() for z in est.zones]
        events = []
        for e in row.get("events", []):
            events.append({k: e.get(k) for k in ("t_trigger", "reason", "t_end", "recover_s", "result",
                                                  "accepted_xy", "err_m", "pre_err_m", "last_verdict")}
                          | {"wrong": bool(e["err_m"] is not None and e["err_m"] > X.WRONG_M),
                             "moves": [m["move"] for m in e.get("moves", []) if m.get("move")],
                             "move_t": [m["t"] for m in e.get("moves", []) if m.get("move")]})
        arms.append({"arm": arm, "label": label,
                     "score": {k: row.get(k) for k in ("outcome", "time_to_goal_s", "min_clearance_m",
                                                       "path_length_m", "duration_s", "max_pose_error_m",
                                                       "wrong_commits", "hover_s", "move_s")},
                     "cols": ["t", "truth_x", "truth_y", "seen_x", "seen_y", "lost", "moving", "hyps"],
                     "rows": rows, "events": events, "fault": row["fault_log"],
                     "check": {"file": "samples/close-area-relocalize/results/" + fname, "fields": check, "match": ok}})
        print(f"{arm}: {row['outcome']} wrong {row.get('wrong_commits')} events {len(events)} match {ok}")
    wj = world_json.to_json(w, radius=run.DEFAULTS["vehicle"]["radius"])
    wj["index"] = index
    doc = {
        "schema": "close-area-story-replay/1", "kind": "relocalize", "input": "synthetic",
        "generated_by": "samples/close-area-relocalize/export_replay.py",
        "command": "python export_replay.py " + " ".join(argv if argv is not None else sys.argv[1:]),
        "family": FAMILY, "seed": SEED, "index": index, "fault_case": FAULT, "hz": run.DEFAULTS["plan_hz"],
        "selection": ("first seed-0 jump layout where (b) made a wrong commit and (f) flew a disambiguating "
                      "move; picked to show both mechanisms, not typical") if a.index is None else "chosen by --index",
        "planner": "arena astar_esdf known_map=True, hover while pose quality is 0",
        "wrong_commit_m": X.WRONG_M, "world": wj, "dark_zones": dark,
        "arms": arms, "matches_published": all_ok, "headline": headline(),
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
