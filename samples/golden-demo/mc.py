#!/usr/bin/env python3
"""Headless Monte Carlo for the golden demo: seed x drag rate x spoof type, each case flown
twice (monitor acts / baseline shadow), plus no-spoof runs for false alarms. Each flight gets
its own SITL container; LANES flights run in parallel at SITL --speedup.

    python mc.py --seeds 1 2 3 4 --rates 0.3 1 3 --spoofs position coherent --nospoof-seeds 1 2 3 4
    python mc.py --summarize-only runs/mc

Raw logs and per-flight summaries go to runs/mc/ (git-ignored); the aggregate table to
runs/mc/mc_summary.json, or data/mc_summary.json with --update-reference.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = os.environ.get("IMAGE", "nav-sitl-ardupilot:copter-4.6.3")
DEFAULT_PARMS = ["golden.parm", "inject.parm", "v2.parm"]
SEARCH_ORIGIN = "41.301800,-81.751397,290,0"   # vgeo_real.HOME, the replay table's home


def sitl_up(name: str, port: int, parms: list[str], home: str, speedup: float) -> None:
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    defaults = ",".join(["/ardupilot/Tools/autotest/default_params/copter.parm"] + [f"/{p}" for p in parms])
    subprocess.run(["docker", "create", "--name", name, "-p", f"127.0.0.1:{port}:5762",
                    "-e", f"SITL_SPEEDUP={speedup}", "-e", f"SITL_HOME={home}", IMAGE,
                    "--defaults", defaults], check=True, capture_output=True)
    for p in parms:
        subprocess.run(["docker", "cp", str(HERE / p), f"{name}:/{p}"], check=True, capture_output=True)
    subprocess.run(["docker", "start", name], check=True, capture_output=True)


def sitl_down(name: str, log: Path | None = None) -> None:
    if log:
        with log.open("w") as f:
            subprocess.run(["docker", "logs", name], stdout=f, stderr=subprocess.STDOUT)
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)


def fly(case: dict, out: Path, name: str, port: int, speedup: float, python: str) -> dict:
    raw = out / f"{case['id']}.raw.jsonl"
    sitl_up(name, port, case.get("parms", DEFAULT_PARMS), case.get("home", SEARCH_ORIGIN),
            case.get("speedup", speedup))
    cmd = [python, str(HERE / "companion.py"), "--connect", f"tcp:127.0.0.1:{port}", "--mode", case["mode"],
           "--log", str(raw), "--seed", str(case["seed"]), "--quiet"]
    cmd += case.get("argv") or ["--gps", "inject", "--spoof", case["spoof"], "--rate", str(case["rate"]),
                                "--vgeo", case.get("vgeo", "replay"), "--detector", case.get("detector", "ss+vel"),
                                "--alt", str(case.get("alt", 150)), "--vio-to-ap",
                                "--extnav", case.get("extnav", "reference")]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    wall = time.time() - t0
    sitl_down(name, out / f"{case['id']}.sitl.log")
    (out / f"{case['id']}.stdout.txt").write_text(p.stdout + p.stderr)
    return {"id": case["id"], "ok": p.returncode == 0, "wall_s": round(wall, 1)}


def cases(a) -> list[dict]:
    out = []
    for seed, rate, spoof, mode in itertools.product(a.seeds, a.rates, a.spoofs, ("monitor", "baseline")):
        out.append({"id": f"{spoof}-r{rate:g}-s{seed}-{mode}", "seed": seed, "rate": rate, "spoof": spoof,
                    "mode": mode, "vgeo": a.vgeo})
    for seed in a.nospoof_seeds:
        out.append({"id": f"none-s{seed}-baseline", "seed": seed, "rate": 0.0, "spoof": "none",
                    "mode": "baseline", "vgeo": a.vgeo})
    return out


V1_HOME = "-35.363261,149.165230,584,353"
LANE_CONFIGS = {
    # v1 exactly: host wall-clock timestamps on VISION_POSITION_ESTIMATE, no VIO velocity to the EKF
    "A-v1-hoststamp": (["golden.parm"], ["--stamp", "host"]),
    "B-simstamp": (["golden.parm"], ["--stamp", "sim"]),
    "C-simstamp-vio": (["golden.parm", "v2.parm"], ["--stamp", "sim", "--vio-to-ap"]),
    "D-simstamp-alt150": (["golden.parm"], ["--stamp", "sim", "--alt", "150"]),
    "E-simstamp-gpsinject": (["golden.parm", "inject.parm"], ["--stamp", "sim", "--gps", "inject"]),
    "F-gpsinject-paramsets": (["golden.parm", "inject.parm"], ["--stamp", "sim", "--gps", "inject", "--param-noise"]),
}


def lane_cases(seeds) -> list[dict]:
    """EKF lane-switch experiment: the v1 flight (SITL GPS glitch 1 m/s, sim visual geoloc,
    chi-square), monitor mode, speedup 1, varying only how ExternalNav data is stamped and fed."""
    out = []
    for name, (parms, extra) in LANE_CONFIGS.items():
        for seed in seeds:
            out.append({"id": f"lanes-{name}-s{seed}", "seed": seed, "mode": "monitor", "parms": parms,
                        "home": V1_HOME, "speedup": 1,
                        "argv": ["--gps", "sitl", "--spoof", "position", "--rate", "1", "--vgeo", "sim",
                                 "--detector", "chi2"] + extra})
    return out


def run_all(todo, out, lanes, ports, speedup, python, prefix):
    q = list(todo)
    lock = threading.Lock()
    results = []

    def lane(k):
        while True:
            with lock:
                if not q:
                    return
                c = q.pop(0)
            r = fly(c, out, f"{prefix}{k}", ports[k], speedup, python)
            with lock:
                results.append(r)
                print(f"[{len(results)}/{len(todo)}] {r['id']} ok={r['ok']} wall={r['wall_s']}s", flush=True)

    ts = [threading.Thread(target=lane, args=(k,)) for k in range(lanes)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return results


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 1)


def dist(xs):
    xs = [x for x in xs if x is not None]
    return {"n": len(xs), "min": pct(xs, 0), "median": pct(xs, 0.5), "p90": pct(xs, 0.9), "max": pct(xs, 1)} if xs else {"n": 0}


def summarize(out: Path) -> dict:
    import to_navdash as T
    flights = {}
    for raw in sorted(out.glob("*.raw.jsonl")):
        rows = T.load(raw)
        if not any(r["type"] == "COMPANION_END" for r in rows):
            flights[raw.name[:-10]] = {"complete": False}
            continue
        flights[raw.name[:-10]] = T.analyse(rows) | {"complete": True}
    groups: dict = {}
    for fid, s in flights.items():
        if not s.get("complete"):
            continue
        key = (s["spoof"]["kind"], s["spoof"]["rate_mps"], s["mode"])
        groups.setdefault(key, []).append(s)
    table = []
    for (kind, rate, mode), ss in sorted(groups.items()):
        row = {"spoof": kind, "rate_mps": rate, "mode": mode, "runs": len(ss)}
        for det in ("chi2", "ss", "vel", "ss+vel", "any"):
            ttd = [s["detect"][det]["ttd_s"] for s in ss if s["detect"][det]["ttd_s"] is not None]
            row[f"ttd_{det}_s"] = dist(ttd)
            row[f"missed_{det}"] = sum(1 for s in ss if s["detect"][det]["ttd_s"] is None) if kind != "none" else None
            row[f"false_alarm_{det}"] = sum(1 for s in ss if s["detect"][det]["false_alarm"])
        row["max_path_dev_after_onset_m"] = dist([s["max_path_deviation_after_onset_m"] for s in ss])
        row["max_ekf_error_m"] = dist([s["max_ekf_error_m"] for s in ss])
        row["ekf_gps_glitching_runs"] = sum(1 for s in ss if s["ekf_gps_glitching_reports"] > 0)
        row["hpl_m_before_onset"] = dist([s["ss"]["hpl_median_before_onset_m"] for s in ss])
        row["ss_misleading_epochs"] = sum(s["ss"]["misleading_epochs"] for s in ss)
        row["lane_switches"] = dist([s["ekf_lane_switches"] for s in ss])
        row["outcomes"] = {o: sum(1 for s in ss if s["outcome"] == o) for o in sorted({s["outcome"] for s in ss})}
        row["vgeo_fix_rate"] = round(sum(s["vgeo_fixes"] for s in ss) / max(1, sum(s["vgeo_fixes"] + s["vgeo_failures"] for s in ss)), 2)
        table.append(row)
    return {"flights": flights, "table": table}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4])
    ap.add_argument("--rates", type=float, nargs="+", default=[0.3, 1.0, 3.0])
    ap.add_argument("--spoofs", nargs="+", default=["position", "coherent"])
    ap.add_argument("--nospoof-seeds", type=int, nargs="*", default=[1, 2, 3, 4])
    ap.add_argument("--vgeo", choices=["sim", "replay"], default="replay")
    ap.add_argument("--lanes", type=int, default=4)
    ap.add_argument("--port0", type=int, default=15790)
    ap.add_argument("--speedup", type=float, default=5.0)
    ap.add_argument("--prefix", default="golden2-mc")
    ap.add_argument("--out", type=Path, default=HERE / "runs" / "mc")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--only", nargs="*", help="run only these case ids")
    ap.add_argument("--experiment", choices=["mc", "lanes"], default="mc")
    ap.add_argument("--summarize-only", action="store_true")
    ap.add_argument("--update-reference", action="store_true", help="also write data/mc_summary.json")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    meta = {}
    if not a.summarize_only:
        todo = cases(a) if a.experiment == "mc" else lane_cases(a.seeds)
        todo = [c for c in todo if not a.only or c["id"] in a.only]
        t0 = time.time()
        res = run_all(todo, a.out, a.lanes, [a.port0 + k for k in range(a.lanes)], a.speedup, a.python, a.prefix)
        meta = {"wall_s": round(time.time() - t0, 1), "lanes": a.lanes, "speedup": a.speedup,
                "flights": len(res), "failed": [r["id"] for r in res if not r["ok"]],
                "flight_wall_s": dist([r["wall_s"] for r in res])}
        (a.out / "mc_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    elif (a.out / "mc_meta.json").exists():
        meta = json.loads((a.out / "mc_meta.json").read_text())
    s = summarize(a.out) | {"meta": meta}
    (a.out / "mc_summary.json").write_text(json.dumps(s, indent=1) + "\n")
    if a.update_reference:
        (HERE / "data" / "mc_summary.json").write_text(json.dumps({"meta": meta, "table": s["table"]}, indent=1) + "\n")
    for r in s["table"]:
        print(json.dumps({k: v for k, v in r.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
