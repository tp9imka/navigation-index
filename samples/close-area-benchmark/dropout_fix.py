"""Size the dropped-beam bug in astar_esdf.LogOddsMap.update, as a monkeypatch (arena not edited).

The bug (docs/upstream-findings.md section 22): RangeScan reads math.inf both for "no surface within
max_range" and for a dropped beam (sensors.py, sensors_cone.py). LogOddsMap.update traces every inf
beam as free out to max_range, so a dropout marks cells behind a wall as free.

Arms (applied to the class, so every planner that builds its map with LogOddsMap gets it: astar_unknown,
astar_unknown_f2, dstar_lite, thetastar_unknown, lazy_thetastar_unknown, mppi, mppi_astar, hybrid_astar):
  before   LogOddsMap.update as shipped (counters only)
  skip     option A: a beam with no return adds nothing (no free trace). Needs no sensor change.
  reseed   noise floor, not a fix: shipped update, but the sensor gets another noise stream (derived from
           run.py's [seed, index, 7]). Its paired changes vs matrix_0 show how far outcomes move by chance.
  status   option B: a dropped beam adds nothing; a no-target beam is traced free to max_range as before.
           The planner gets the drop mask from a sensor wrapper built here (DropFlagSensor), which replays
           the sensor's own random draws to recover the mask; readings are unchanged (asserted). The real
           sensors.py / sensors_cone.py do not expose it: RangeScan has no status field.
Both fixes are done by removing beams from the scan before calling the shipped update, so the rest of
the shipped code runs unchanged.

The flight loop is bench.run_one (run.run_one's loop, seed 0, same noise streams); only the sensor
factory is wrapped (DropFlagSensor, for counting and for option B) and the update patched.

  .venv/bin/python dropout_fix.py run --arms skip,status --presets ideal,crazyflie --workers 14
  .venv/bin/python dropout_fix.py run --arms before,skip,status --presets crazyflie_bright --workers 14
  .venv/bin/python dropout_fix.py run --arms before --presets ideal,crazyflie --planners astar_unknown,mppi
  .venv/bin/python dropout_fix.py report        # results/dropout_fix_tables.md from the runs file
Runs are merged into results/dropout_fix_runs.json keyed by (arm, planner, family, preset, index).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

import bench as B

AE = B.astar_esdf
LogOddsMap = AE.LogOddsMap
_ORIG_UPDATE = LogOddsMap.update
_ORIG_MAKE_SENSOR = B.presets.make_sensor
RESULTS = B.RESULTS
RUNS_FILE = os.path.join(RESULTS, "dropout_fix_runs.json")
UNKNOWN_MAP = ("astar_unknown", "astar_unknown_f2", "dstar_lite", "thetastar_unknown", "lazy_thetastar_unknown",
               "mppi", "mppi_astar", "hybrid_astar")
ARMS = ("before", "skip", "status", "reseed")
CMP_KEYS = ("outcome", "min_clearance_m", "path_length_m", "time_to_goal_s")

# Control preset with no dropout: the ideal fan with dropout 0 (in memory only, presets.py not edited).
B.presets.SENSOR_PRESETS.setdefault("ideal_nodrop", dict(B.presets.SENSOR_PRESETS["ideal"], dropout=0.0))

STATE = {"arm": "before", "calls": 0, "beams": 0, "inf": 0, "dropped": 0, "map": None}


@dataclasses.dataclass
class RangeScanStatus(B.adapter.RangeScan):
    """RangeScan plus a per-beam drop flag (True = the beam was dropped, reads inf)."""
    dropped: list = None


class DropFlagSensor:
    """Wraps a RangeFan / ConeRangeFan. Same readings, same rng consumption, plus the drop mask.

    The mask is recovered by restoring the rng state after the real scan and replaying the draws the
    sensor makes in order (sensors.py: normal if noise_std > 0, random if dropout > 0; sensors_cone.py:
    normal, random, random). The rng state after the replay must equal the state after the real scan."""

    def __init__(self, inner):
        self.inner = inner
        self.cone = hasattr(inner, "true_ranges")

    def __getattr__(self, k):
        return getattr(self.inner, k)

    def scan(self, world, x, y, yaw, t):
        s, rng = self.inner, self.inner.rng
        st0 = rng.bit_generator.state
        out = s.scan(world, x, y, yaw, t)
        st1 = rng.bit_generator.state
        n = len(s.angles)
        rng.bit_generator.state = st0
        if self.cone:
            rng.normal(0.0, 1.0, size=(n,))
            rng.random((n,))
            drop = rng.random((n,)) < s.dropout
        else:
            if s.noise_std > 0:
                rng.normal(0.0, s.noise_std, size=(n,))
            drop = rng.random((n,)) < s.dropout if s.dropout > 0 else np.zeros(n, bool)
        assert rng.bit_generator.state == st1, "drop-mask replay consumed a different number of draws"
        rng.bit_generator.state = st1
        assert all(not math.isfinite(out.distances[i]) for i in np.flatnonzero(drop))
        return RangeScanStatus(t=out.t, angles=out.angles, distances=out.distances, max_range=out.max_range,
                               dropped=[bool(v) for v in drop])


def make_sensor_flagged(name, rng):
    if STATE["arm"] == "reseed":            # noise floor: shipped update, another sensor noise stream
        rng = np.random.default_rng([int(rng.integers(2 ** 32)), 85])
    return DropFlagSensor(_ORIG_MAKE_SENSOR(name, rng))


def update_patched(self, pose, scan):
    """LogOddsMap.update with the arm's beam selection, then the shipped update on the kept beams."""
    d = np.asarray(scan.distances, float)
    inf = ~np.isfinite(d)
    dropped = getattr(scan, "dropped", None)
    dropped = np.asarray(dropped, bool) if dropped is not None else None
    STATE["calls"] += 1
    STATE["beams"] += len(d)
    STATE["inf"] += int(inf.sum())
    STATE["dropped"] += int(dropped.sum()) if dropped is not None else 0
    STATE["map"] = self
    arm = STATE["arm"]
    if arm in ("before", "reseed"):
        return _ORIG_UPDATE(self, pose, scan)
    if arm == "skip":                       # option A: no return => no information
        keep = ~inf
    elif arm == "status":                   # option B: drop => no information; no target => free to max_range
        keep = ~dropped if dropped is not None else ~inf
    else:
        raise ValueError(arm)
    if keep.all():
        return _ORIG_UPDATE(self, pose, scan)
    idx = np.flatnonzero(keep)
    kept = B.adapter.RangeScan(t=scan.t, angles=[scan.angles[i] for i in idx],
                               distances=[scan.distances[i] for i in idx], max_range=scan.max_range)
    return _ORIG_UPDATE(self, pose, kept)


LogOddsMap.update = update_patched
B.presets.make_sensor = make_sensor_flagged


def false_free(m, w) -> tuple[int, int]:
    """(known-free cells, of them truly occupied or outside the area) in the planner's final map."""
    if m is None:
        return 0, 0
    free = np.argwhere(m.lo < AE.LO_FREE)
    if not len(free):
        return 0, 0
    x = m.x0 + (free[:, 0] + 0.5) * m.res
    y = m.y0 + (free[:, 1] + 0.5) * m.res
    g = w.grid
    ix = np.floor((x - g.x0) / g.res).astype(int)
    iy = np.floor((y - g.y0) / g.res).astype(int)
    inside = (ix >= 0) & (iy >= 0) & (ix < g.occ.shape[0]) & (iy < g.occ.shape[1])
    occ = np.ones(len(free), bool)
    occ[inside] = g.occ[ix[inside], iy[inside]]
    return int(len(free)), int(occ.sum())


def task(args):
    arm, planner, family, preset, index, seed = args
    STATE.update(arm=arm, calls=0, beams=0, inf=0, dropped=0, map=None)
    res = B.run_one(planner, family, preset, index, seed)
    w = B.world_glass.make_any_world(family, seed, index, radius=B.run.DEFAULTS["vehicle"]["radius"])
    nf, nff = false_free(STATE["map"], w)
    res.update({"arm": arm, "map_updates": STATE["calls"], "beams": STATE["beams"], "inf_beams": STATE["inf"],
                "dropped_beams": STATE["dropped"], "free_cells": nf, "false_free_cells": nff})
    return res


def key(r):
    return (r["arm"], r["planner"], r["family"], r["preset"], r["index"])


def load_runs(path=None) -> list:
    """Runs of one file, or (path None) of every results/dropout_fix_runs*.json merged."""
    import glob
    files = [path] if path else sorted(glob.glob(os.path.join(RESULTS, "dropout_fix_runs*.json")))
    out = {}
    for f in files:
        if os.path.exists(f):
            for r in json.load(open(f))["runs"]:
                out[key(r)] = r
    return list(out.values())


def cmd_run(a) -> int:
    global RUNS_FILE
    RUNS_FILE = os.path.join(RESULTS, f"dropout_fix_runs{a.runs_suffix}.json")
    arms = a.arms.split(",")
    planners = [p for p in a.planners.split(",") if p]
    families, presets_ = a.families.split(","), a.presets.split(",")
    tasks = [(arm, p, f, pr, i, a.seed) for arm in arms for p in planners for f in families for pr in presets_
             for i in range(a.layouts)]
    tasks.sort(key=lambda t: (t[2] not in B.LONG_FAMILIES, B.SLOW.get(t[1], 9)))
    old = {key(r): r for r in load_runs(RUNS_FILE)}
    n_all = len(tasks)
    tasks = [t for t in tasks if (t[0], t[1], t[2], t[3], t[4]) not in old]     # resume: skip runs on file
    meta = json.load(open(RUNS_FILE)).get("invocations", []) if os.path.exists(RUNS_FILE) else []
    cmd = "python dropout_fix.py " + " ".join(sys.argv[1:])
    t_all = time.perf_counter()
    rows = []

    def save(final: bool):
        for r in rows:
            old[key(r)] = r
        inv = meta + ([{"command": cmd, "n_runs": len(rows), "n_skipped_on_file": n_all - len(tasks),
                        "wall_s": round(time.perf_counter() - t_all, 1), "workers": a.workers, "env": B.env(),
                        "date": time.strftime("%Y-%m-%d"), "complete": final,
                        "loadavg_at_end": [round(x, 1) for x in os.getloadavg()]}] if rows or final else [])
        os.makedirs(RESULTS, exist_ok=True)
        with open(RUNS_FILE + ".tmp", "w") as fh:
            json.dump({"input": "synthetic", "seed": a.seed, "invocations": inv,
                       "runs": sorted(old.values(), key=lambda r: tuple(str(x) for x in key(r)))}, fh, indent=0)
        os.replace(RUNS_FILE + ".tmp", RUNS_FILE)

    failed = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(task, t) for t in tasks]
        for k, fu in enumerate(as_completed(futs)):
            try:
                rows.append(fu.result())
            except Exception as e:            # e.g. a worker killed by the OS: rerun the command to resume
                failed.append(repr(e))
            if (k + 1) % 50 == 0:
                print(f"{k + 1}/{len(tasks)} runs, {time.perf_counter() - t_all:.0f} s", flush=True)
                save(False)
    save(not failed)
    if failed:
        print(f"{len(failed)} runs failed ({failed[0]}); rerun the same command to resume", flush=True)
        return 1
    print(f"wall {round(time.perf_counter() - t_all, 1)} s for {len(rows)} runs "
          f"({n_all - len(tasks)} already on file); {len(old)} runs in {os.path.relpath(RUNS_FILE, B.HERE)}")
    return 0


# ---------------- report ----------------

def summ(rows):
    n = len(rows)
    return {"n": n, "reached": round(100.0 * sum(r["reached"] for r in rows) / n, 1),
            "collision": round(100.0 * sum(r["collision"] for r in rows) / n, 1)} if n else None


def rank(cells: dict) -> dict:
    """Competition rank (1 = best) by reached % desc, then collision % asc."""
    k = {p: (-s["reached"], s["collision"]) for p, s in cells.items()}
    return {p: 1 + sum(v < k[p] for v in k.values()) for p in k}


def cmd_report(a) -> int:
    runs = load_runs()
    m0 = json.load(open(os.path.join(RESULTS, "matrix_0.json")))
    by = {}
    for r in runs:
        by.setdefault(r["arm"], {})[(r["planner"], r["family"], r["preset"], r["index"])] = r
    base = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in m0["runs"]
            if r["planner"] in UNKNOWN_MAP}
    fams = list(B.FAMILIES)
    presets_ = [p for p in ("ideal", "crazyflie", "crazyflie_bright", "ideal_nodrop")
                if any(k[2] == p for arm in by.values() for k in arm)]
    out = ["Generated by `python dropout_fix.py report` from results/dropout_fix_runs.json and results/matrix_0.json. "
           "Input: synthetic (simulated layouts, vehicle and sensors), seed 0, scored on truth.", ""]

    def before_of(k):
        """'before' run: this job's own unpatched run if present, else matrix_0.json."""
        return by.get("before", {}).get(k) or base.get(k)

    # --- 1. reproduction check: our unpatched runs vs matrix_0 ---
    rep = [(k, r) for k, r in by.get("before", {}).items() if k in base]
    if rep:
        same = sum(all(base[k].get(c) == r.get(c) for c in CMP_KEYS) for k, r in rep)
        out += ["## Reproduction: unpatched runs of this job vs matrix_0.json", "",
                f"Runs identical in {', '.join(CMP_KEYS)}: {same}/{len(rep)}.", ""]
        per = {}
        for k, r in rep:
            c = per.setdefault((k[0], k[2]), [0, 0])
            c[0] += all(base[k].get(x) == r.get(x) for x in CMP_KEYS)
            c[1] += 1
        out += ["| planner | preset | identical |", "|---|---|---|"]
        out += [f"| {p} | {pr} | {c[0]}/{c[1]} |" for (p, pr), c in sorted(per.items())]
        out.append("")

    # --- 2. beam statistics ---
    out += ["## Beams with no return: how many are drops", "",
            "Over every LogOddsMap.update call of the runs (all arms; the sensor stream is the same in every arm "
            "up to the point a run's trajectory diverges).", "",
            "| preset | updates | beams | inf beams % | dropped beams % | dropped share of inf beams % |",
            "|---|---|---|---|---|---|"]
    for pr in presets_:
        sel = [r for r in runs if r["preset"] == pr]
        u, b, i, d = (sum(r[x] for r in sel) for x in ("map_updates", "beams", "inf_beams", "dropped_beams"))
        if b:
            out.append(f"| {pr} | {u} | {b} | {100 * i / b:.1f} | {100 * d / b:.2f} | {100 * d / max(i, 1):.1f} |")
    out.append("")

    # --- 3a. pooled paired changes per arm x preset, with an exact two-sided sign test ---
    def sign_p(a_, b_):
        n_, k_ = a_ + b_, min(a_, b_)
        if n_ == 0:
            return 1.0
        return min(1.0, 2 * sum(math.comb(n_, i) for i in range(k_ + 1)) / 2 ** n_)

    out += ["## Pooled paired changes (all planners re-run in that arm, 8 families, 20 layouts)", "",
            "R+ / R- = runs that newly reach / no longer reach B; C+ / C- = newly collide / no longer collide. "
            "p = exact two-sided sign test on R+ vs R- (and C- vs C+), treating runs as independent (they are not: "
            "the planners share layouts and map code), so read it as a rough guide. `reseed` is the noise floor: "
            "shipped code, other sensor noise stream.", "",
            "| arm | preset | planners | runs | runs changed | reached % before => after | collision % before => after "
            "| R+ | R- | p (reach) | C+ | C- | p (collision) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm in ("reseed", "skip", "status"):
        for pr in presets_:
            ks = [k for k in by.get(arm, {}) if k[2] == pr and before_of(k)]
            if not ks:
                continue
            pairs = [(before_of(k), by[arm][k]) for k in ks]
            rp = sum((not b["reached"]) and x["reached"] for b, x in pairs)
            rm = sum(b["reached"] and not x["reached"] for b, x in pairs)
            cp = sum((not b["collision"]) and x["collision"] for b, x in pairs)
            cm = sum(b["collision"] and not x["collision"] for b, x in pairs)
            chg = sum(any(b.get(c) != x.get(c) for c in CMP_KEYS) for b, x in pairs)
            sb, sa = summ([b for b, _ in pairs]), summ([x for _, x in pairs])
            pl = sorted({k[0] for k in ks}, key=UNKNOWN_MAP.index)
            out.append(f"| {arm} | {pr} | {len(pl)} | {len(pairs)} | {chg} | {sb['reached']:g} => {sa['reached']:g} "
                       f"| {sb['collision']:g} => {sa['collision']:g} | {rp} | {rm} | {sign_p(rp, rm):.3f} "
                       f"| {cp} | {cm} | {sign_p(cp, cm):.3f} |")
    out.append("")

    # --- 3. per planner x family x preset ---
    for arm in ("reseed", "skip", "status"):
        if arm not in by:
            continue
        label = {"skip": "option A (skip every no-return beam)", "status": "option B (skip dropped beams only)",
                 "reseed": "noise floor (shipped code, other sensor noise stream)"}[arm]
        out += [f"## {label}: reached % / collision %, before => after", "",
                "Before = this job's unpatched run where it exists (crazyflie_bright, ideal_nodrop), else "
                "results/matrix_0.json. Paired changes over the same layouts: R+ / R- = runs that newly reach / "
                "no longer reach B, C+ / C- = runs that newly collide / no longer collide.", ""]
        for pr in presets_:
            keys = [k for k in by[arm] if k[2] == pr and before_of(k)]
            if not keys:
                continue
            planners = [p for p in UNKNOWN_MAP if any(k[0] == p for k in keys)]
            out += [f"### Preset `{pr}`", "",
                    "| planner | " + " | ".join(fams) + " | all 8 families | R+ | R- | C+ | C- | runs changed |",
                    "|---" * (len(fams) + 7) + "|"]
            for p in planners:
                cells, allb, alla = [], [], []
                for f in fams:
                    ks = [k for k in keys if k[0] == p and k[1] == f]
                    if not ks:
                        cells.append("-")
                        continue
                    sb, sa = summ([before_of(k) for k in ks]), summ([by[arm][k] for k in ks])
                    allb += [before_of(k) for k in ks]
                    alla += [by[arm][k] for k in ks]
                    ch = "" if (sb["reached"], sb["collision"]) == (sa["reached"], sa["collision"]) else " *"
                    cells.append(f"{sb['reached']:g}/{sb['collision']:g} => {sa['reached']:g}/{sa['collision']:g}{ch}")
                sb, sa = summ(allb), summ(alla)
                pairs = list(zip(allb, alla))
                rp = sum((not b["reached"]) and x["reached"] for b, x in pairs)
                rm = sum(b["reached"] and not x["reached"] for b, x in pairs)
                cp = sum((not b["collision"]) and x["collision"] for b, x in pairs)
                cm = sum(b["collision"] and not x["collision"] for b, x in pairs)
                chg = sum(any(b.get(c) != x.get(c) for c in CMP_KEYS) for b, x in pairs)
                out.append(f"| {p} | " + " | ".join(cells)
                           + f" | {sb['reached']:g}/{sb['collision']:g} => {sa['reached']:g}/{sa['collision']:g} "
                           f"| {rp} | {rm} | {cp} | {cm} | {chg}/{len(pairs)} |")
            out.append("")
            # rank changes among the unknown-map planners
            rk = []
            for f in fams + ["all"]:
                cb, ca = {}, {}
                for p in planners:
                    ks = [k for k in keys if k[0] == p and (f == "all" or k[1] == f)]
                    if ks:
                        cb[p] = summ([before_of(k) for k in ks])
                        ca[p] = summ([by[arm][k] for k in ks])
                if not cb:
                    continue
                rb, ra = rank(cb), rank(ca)
                best_b = sorted(p for p in rb if rb[p] == 1)
                best_a = sorted(p for p in ra if ra[p] == 1)
                moved = [f"{p} {rb[p]}=>{ra[p]}" for p in planners if p in rb and rb[p] != ra[p]]
                if moved or best_b != best_a:
                    rk.append(f"| {f} | {'/'.join(best_b)} | {'/'.join(best_a)} | {', '.join(moved) or '-'} |")
            out += ["Rank among these unknown-map rows (reached desc, then collision asc), only families where it moved:", ""]
            if rk:
                out += ["| family | best before | best after | rank moves |", "|---|---|---|---|"] + rk
            else:
                out.append("No rank change.")
            out.append("")
            # false-free cells (only for this job's runs: matrix_0 has no map counters)
            ff = []
            for p in planners:
                ks = [k for k in keys if k[0] == p]
                bb = [by["before"][k] for k in ks if k in by.get("before", {})]
                aa = [by[arm][k] for k in ks]
                fr = lambda rs: np.median([r["false_free_cells"] / max(r["free_cells"], 1) for r in rs])  # noqa: E731
                if bb:
                    ff.append(f"| {p} | {100 * fr(bb):.2f} | {100 * fr(aa):.2f} |")
                else:
                    ff.append(f"| {p} | - | {100 * fr(aa):.2f} |")
            out += ["Median share of the planner's known-free cells (end of run) that are truly occupied or outside "
                    "the area, % (before = this job's unpatched runs only; '-' = not re-run):", "",
                    "| planner | before | after |", "|---|---|---|"] + ff + [""]

    # --- 4. best planner per family incl. the rows this fix does not touch (matrix presets only) ---
    for arm in ("skip", "status"):
        if arm not in by:
            continue
        out += [f"## Matrix verdict with {arm}: best planner per family, all 21 rows (other rows from matrix_0.json)", ""]
        for pr in ("ideal", "crazyflie"):
            cells_b = {p: dict(v) for p, v in m0["summary"].get(pr, {}).items()}
            if not cells_b:
                continue
            cells_a = {p: dict(v) for p, v in cells_b.items()}
            for p in UNKNOWN_MAP:
                for f in fams:
                    ks = [k for k in by[arm] if k[0] == p and k[1] == f and k[2] == pr]
                    if len(ks) == m0["layouts"]:
                        s = summ([by[arm][k] for k in ks])
                        cells_a[p][f] = {"reached_pct": s["reached"], "collision_pct": s["collision"]}
            planners = list(m0["planners"])
            no_map = [p for p in planners if p not in B.PRIOR_MAP]
            out += [f"### Preset `{pr}`", "", "| family | best before | best after | best without prior map before "
                    "| best without prior map after |", "|---|---|---|---|---|"]
            for f in fams:
                b1, a1 = B.best(cells_b, planners, f), B.best(cells_a, planners, f)
                b2, a2 = B.best(cells_b, no_map, f), B.best(cells_a, no_map, f)
                flag = " *" if (b1, b2) != (a1, a2) else ""
                out.append(f"| {f}{flag} | {b1} | {a1} | {b2} | {a2} |")
            out.append("")
    path = os.path.join(RESULTS, "dropout_fix_tables.md")
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"wrote {os.path.relpath(path, B.HERE)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arms", default="skip,status")
    r.add_argument("--planners", default=",".join(UNKNOWN_MAP))
    r.add_argument("--families", default=",".join(B.FAMILIES))
    r.add_argument("--presets", default="ideal,crazyflie,crazyflie_bright")
    r.add_argument("--layouts", type=int, default=20)
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--runs-suffix", default="", help="write results/dropout_fix_runs<SUFFIX>.json (parallel jobs)")
    r.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    sub.add_parser("report")
    a = ap.parse_args(argv)
    return cmd_run(a) if a.cmd == "run" else cmd_report(a)


if __name__ == "__main__":
    raise SystemExit(main())
