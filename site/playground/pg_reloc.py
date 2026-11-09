"""Playground glue for VIO-loss recovery (loop-63). Loaded by worker.js DRIVER_PY.

The arms come from samples/close-area-relocalize unchanged: run_disambiguate.build(arm, w, est,
seed, index) returns (pose source, planner) exactly as run_disambiguate.py's run_cell does:
  single    experiment.wrap(.., "single") + HoverGate(A* + ESDF known map): commit to the best match
  multi     experiment.wrap(.., "multi")  + HoverGate: RatioPersistence, hover until accept
  multi_ig  disambiguate.DisambPoseSource("infogain") + DisambGate: multi + after 1 s an info-gain move
  none      no relocalizer: the VIO EKF alone, A* known map, no gate (experiment.py arm "estimator")
This file adds recording only: the hypotheses each scan produced, a per-frame status for the
verdict strip, and run_disambiguate.extra() (events, moves, errors) at the end. It never changes
a decision. Truth enters only the "wrong commit" label, the same err_m > 0.5 m that the sample scores.
No backticks or dollar-brace here: keep it loadable the same way as DRIVER_PY.
"""
from __future__ import annotations

ARMS = ("none", "single", "multi", "multi_ig")
FAULTS = ("jump", "dropout")
# status codes per 10 Hz frame, in this order (playground.js STATUS uses the same list)
STATUS = ("nominal", "lost", "hovering", "moving", "accepted", "wrong")
_ST = {k: i for i, k in enumerate(STATUS)}
MODULES = ("relocalize", "disambiguate", "experiment", "run_disambiguate")
M = {}


def load(reloc_dir, load_sample):
    """Import the sample's modules with the driver's _load_sample recipe (folder on sys.path only
    while importing; the sample's arena.py finds close_area_arena already imported)."""
    M.update(load_sample(reloc_dir, list(MODULES)))
    return M


def params():
    R, D = M["relocalize"], M["disambiguate"]
    return {"S_MIN": R.S_MIN, "RATIO": R.RATIO, "N_SCANS": R.N_SCANS, "K_MAX": R.K_MAX, "SEP_M": R.SEP_M,
            "W0_M": R.W0_M, "HOVER_TIMEOUT_S": D.HOVER_TIMEOUT_S, "MAX_MOVES": D.MAX_MOVES,
            "LIVE_FRAC": round(D.LIVE_FRAC, 4), "WRONG_M": M["experiment"].WRONG_M}


def build(arm, w, est, seed, index):
    """(pose source, planner) for one arm, as run_disambiguate.build. Arm none = (est, A* known map)."""
    if arm == "none":
        X = M["experiment"]
        return X.wrap(est, w, seed, index, "estimator"), X.planner_for("estimator")
    if arm not in ARMS:
        raise ValueError("recovery must be one of " + ", ".join(ARMS))
    return M["run_disambiguate"].build(arm, w, est, seed, index)


class Trace:
    """Records what the relocalizer did at each planner step. Call frame(pose, t) right after
    the pose source was called (adapter.pose()), once per 10 Hz frame."""

    def __init__(self, arm, src):
        self.arm, self.src = arm, src
        self.status, self.hyps = [], []
        self._now = []
        if arm != "none":
            inner = src.matcher.hypotheses

            def recording(*a, **kw):
                h = inner(*a, **kw)
                self._now = h
                return h
            src.matcher.hypotheses = recording

    def _code(self, pose):
        s = self.src
        if self.arm == "none":
            return "lost" if pose.quality == 0 else "nominal"
        if s.state == "reloc":
            if getattr(s, "cmd", None) is not None:
                return "moving"
            v = s.event.last_verdict if s.event is not None else None
            return "hovering" if v in ("ambiguous", "pending") else "lost"
        last = s.events[-1] if s.events else None
        if last is not None and last.result == "accepted":
            return "wrong" if last.err_m is not None and last.err_m > M["experiment"].WRONG_M else "accepted"
        return "nominal"

    def frame(self, pose, t):
        self.status.append(_ST[self._code(pose)])
        if self._now:
            self.hyps.append([round(t, 3), [[round(h.x, 3), round(h.y, 3), round(h.score, 4)] for h in self._now]])
            self._now = []

    def result(self, row, est):
        out = {"arm": self.arm, "status_names": list(STATUS), "status": self.status, "hyps": self.hyps,
               "params": params()}
        if self.arm == "none":
            out.update({"events": [], "summary": {"events": 0, "accepted": 0, "wrong_commits": 0, "open_at_end": 0,
                                                  "moves": 0, "hover_s": None}})
            return out
        x = M["run_disambiguate"].extra(row, est, self.src, est.fault)
        ev = x["events"]
        acc = [e for e in ev if e["result"] == "accepted"]
        moves = [m for e in ev for m in e.get("moves", []) if m.get("move") is not None]
        out.update({"events": ev, "summary": {
            "events": len(ev), "accepted": len(acc), "wrong_commits": x["wrong_commits"],
            "open_at_end": sum(1 for e in ev if e["result"] == "open"), "moves": len(moves),
            "hover_s": x["hover_s"], "move_s": x.get("move_s"),
            "first_recover_s": next((e["recover_s"] for e in ev if e["recover_s"] is not None), None)}})
        return out


def event_key(events):
    """Fields compared browser vs native and driver vs run_disambiguate."""
    return [[e["t_trigger"], e["reason"], e["result"], e["recover_s"], e["err_m"],
             len([m for m in e.get("moves", []) if m.get("move") is not None])] for e in events]
