#!/usr/bin/env python3
"""Rebuild site/playground/data/advisor.json with data/build_advisor.py, unchanged, plus the loop-73 rows.

build_advisor.py needs a PLANNER_DOCS entry for every planner in matrix_0.json and lists the prior-map
planners in PRIOR_MAP. loop-73 could not edit that file, so this wrapper adds both for the 7 rows added by
`bench.py --add-to matrix_0` (Theta* x4, MPPI x2, Hybrid A*) and then calls build_advisor.main().
Driver: move the entries below into build_advisor.py and delete this file.

    python3 site/playground/results/build_advisor_loop73.py      # stdlib only, < 1 s

The per-planner "matrix" lines and every number in advisor.json are computed by build_advisor.py from
matrix_0.json (synthetic). The text below has no numbers; it points at each sample's README.
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build_advisor", HERE.parent / "data" / "build_advisor.py")
BA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BA)

T = "samples/close-area-planner-thetastar/README.md"
M = "samples/close-area-planner-mppi/README.md"
H = "samples/close-area-planner-hybrid-astar/README.md"
B = BA.B

NEW_DOCS = {
    "thetastar_known": dict(
        what="Theta*: any-angle A* on the same inflated grid and clearance cost as A* + ESDF. A node may link to "
             "any earlier node it can see, so the path is not tied to grid directions. Same follower.",
        needs="An exact prior map and a good pose. Ignores the range sensor.",
        good="Prior map known: shorter, straighter paths than grid A* and usually an earlier arrival at B (sample README).",
        fails="Plans take several times longer than A*. Trusts the pose, as A* known map does.",
        src=[T, B]),
    "lazy_thetastar_known": dict(
        what="Lazy Theta*: Theta* that checks line of sight only when a node is expanded, so fewer checks per plan.",
        needs="An exact prior map and a good pose. Ignores the range sensor.",
        good="Prior map known and a few hundred ms per replan: any-angle paths with cheaper plans than Theta* (sample README).",
        fails="Still slower per plan than grid A*. Trusts the pose.",
        src=[T, B]),
    "thetastar_unknown": dict(
        what="Theta* on the map built from range hits (the unknown-map A* map, on the area geofence).",
        needs="No prior map. A range scan and a good pose.",
        good="Benchmark row only. Not offered in the playground: its replans are slow (sample README).",
        fails="Slow replans when the map changes; with 4 beams it collides more than the unknown-map A* (sample README).",
        src=[T, B]),
    "lazy_thetastar_unknown": dict(
        what="Lazy Theta* on the map built from range hits, on the area geofence.",
        needs="No prior map. A range scan and a good pose.",
        good="Any-angle paths without a prior map, with cheaper replans than plain Theta*.",
        fails="The slowest planner in the playground per run. With 4 beams it collides more than the unknown-map A* (sample README).",
        src=[T, B]),
    "mppi": dict(
        what="MPPI: samples a few hundred velocity sequences over 2 s, scores them against the range-built map "
             "and B, and blends them by cost. No global plan.",
        needs="No prior map. A range scan and a good pose. numpy only, no QP solver.",
        good="Open clutter.",
        fails="A local controller: stays in U traps and maze dead ends.",
        src=[M, B]),
    "mppi_astar": dict(
        what="MPPI that tracks a lookahead point on the unknown-map A* path instead of B.",
        needs="No prior map. A range scan and a good pose.",
        good="Reaches about as often as the unknown-map A* and often sooner, with smooth model-aware setpoints (sample README).",
        fails="With 4 beams it collides more than the unknown-map A* (sample README).",
        src=[M, B]),
    "hybrid_astar": dict(
        what="Hybrid A* over x, y and heading with turn-rate-limited arcs, on the range-built map and the area geofence.",
        needs="No prior map. A range scan and a good pose.",
        good="A vehicle that cannot turn in place at speed.",
        fails="For a multirotor it reached B less often than A* + follower in the sample's runs (sample README).",
        src=[H, B]),
}

missing = [p for p in NEW_DOCS if p in BA.PLANNER_DOCS]
if missing:
    sys.exit(f"build_advisor.py already has {missing}: run it directly and delete this wrapper")
BA.PLANNER_DOCS.update(NEW_DOCS)
BA.PRIOR_MAP.update({"thetastar_known", "lazy_thetastar_known"})      # as bench.py PRIOR_MAP

if __name__ == "__main__":
    BA.main()
