#!/usr/bin/env python3
"""Spoof sweep on PX4 v1.17 SIH (EKF2) and ArduCopter 4.6.3 SITL (EKF3): drag rate, step
offset, EKF config. Shadow-mode flights only (no external monitor acts). Parallel lanes;
stdlib only on the host, plus pymavlink for the ArduPilot companion (--python).

    python3 spoof_sweep.py --python ../../.venv/bin/python          # all cases, skips logs that exist
    python3 spoof_sweep.py --only px4 --cases coherent-3            # a subset
    python3 spoof_sweep.py --list                                   # print the case list
Docker names are prefixed ekf2dbg-; ArduPilot lanes use host ports 15820+lane.
"""
from __future__ import annotations

import argparse
import os
import queue
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GOLDEN = ROOT / "samples" / "golden-demo"
RUNS = HERE / "runs"

PX4_IMAGE = os.environ.get("PX4_IMAGE", "nav-sitl-px4:v1.17.0")
CLIENT_IMAGE = os.environ.get("CLIENT_IMAGE", "nav-sitl-client:latest")
AP_IMAGE = os.environ.get("AP_IMAGE", "nav-sitl-ardupilot:copter-4.6.3")
PREFIX = "ekf2dbg"
AP_PORT0 = 15820
HOME = (41.301800, -81.751397, 290)          # golden-demo vgeo table home (NAIP window)
AP_PARMS = ("golden.parm", "inject.parm", "v2.parm")
BOOT_WAIT_S = 8

SPOOFS = [("coherent", r) for r in (0.1, 0.5, 1, 2, 3, 5)] + [("position", 3)] + [("step", s) for s in (20, 100)]
CONFIGS = {
    "px4": {
        "default": {},
        "gates3": {"EKF2_GPS_P_GATE": 3, "EKF2_GPS_V_GATE": 3},
        "drmode": {"EKF2_GPS_MODE": 1},
    },
    "ardupilot": {
        "default": {},
        "gates3": {"EK3_POS_I_GATE": 300, "EK3_VEL_I_GATE": 300},
    },
}


def case_name(ap, cfg, kind, x):
    return f"{ap}-{cfg}-{kind}-{x:g}"


def all_cases():
    for ap, cfgs in CONFIGS.items():
        for cfg in cfgs:
            for kind, x in SPOOFS:
                yield ap, cfg, kind, x


def fly_args(ap, cfg, kind, x, log):
    args = ["--autopilot", ap, "--config", cfg, "--spoof", kind, "--log", log]
    args += ["--step", str(x)] if kind == "step" else ["--rate", str(x)]
    for k, v in CONFIGS[ap][cfg].items():
        args += ["--set", f"{k}={v}"]
    return args


def sh(cmd, **kw):
    return subprocess.run(cmd, check=False, **kw)


def run_px4(lane, case, out):
    sitl, client = f"{PREFIX}-px4-l{lane}-sitl", f"{PREFIX}-px4-l{lane}-client"
    name = case_name(*case)
    sh(["docker", "rm", "-f", client, sitl], capture_output=True)
    try:
        sh(["docker", "run", "-d", "--name", sitl, "-e", f"PX4_HOME_LAT={HOME[0]}", "-e", f"PX4_HOME_LON={HOME[1]}",
            "-e", f"PX4_HOME_ALT={HOME[2]}", PX4_IMAGE], capture_output=True)
        time.sleep(BOOT_WAIT_S)
        # Same boot sequence as golden-demo-px4/run.sh: SIH GPS off, MAVLink HIL_GPS on, restart.
        sh(["docker", "exec", sitl, "sh", "-c", "cd /px4/rootfs && /px4/bin/px4-param set SENS_EN_GPSSIM 0 >/dev/null && "
            "/px4/bin/px4-param set MAV_USEHILGPS 1 >/dev/null && /px4/bin/px4-param save"], capture_output=True)
        sh(["docker", "restart", sitl], capture_output=True)
        sh(["docker", "run", "-d", "--name", client, "--network", f"container:{sitl}", "--entrypoint", "sh",
            CLIENT_IMAGE, "-c", "mkdir -p /nav && exec sleep infinity"], capture_output=True)
        time.sleep(BOOT_WAIT_S)
        tar = subprocess.Popen(["tar", "--no-xattrs", "--no-mac-metadata", "-C", str(ROOT), "--exclude", "runs",
                                "--exclude", "screenshots", "--exclude", "__pycache__", "--exclude", "data/v2*",
                                "-cf", "-", "samples/golden-demo", "samples/golden-demo-px4", "samples/altpnt-integrity",
                                "samples/autopilot-spoof-response", "templates/project-repo/src"],
                               stdout=subprocess.PIPE, env=os.environ | {"COPYFILE_DISABLE": "1"})
        sh(["docker", "cp", "-", f"{client}:/nav"], stdin=tar.stdout, capture_output=True)
        tar.wait()
        with (out / f"{name}.console.txt").open("w") as f:
            rc = sh(["docker", "exec", client, "python", "-u", "/nav/samples/autopilot-spoof-response/spoof_fly.py",
                     *fly_args(*case, f"/nav/{name}.raw.jsonl")], stdout=f, stderr=subprocess.STDOUT).returncode
        sh(["docker", "cp", f"{client}:/nav/{name}.raw.jsonl", str(out / f"{name}.raw.jsonl")], capture_output=True)
        with (out / f"{name}.sitl.log").open("w") as f:
            sh(["docker", "logs", sitl], stdout=f, stderr=subprocess.STDOUT)
        return rc
    finally:
        sh(["docker", "rm", "-f", client, sitl], capture_output=True)


def run_ardupilot(lane, case, out, python):
    sitl, port = f"{PREFIX}-ap-l{lane}", AP_PORT0 + lane
    name = case_name(*case)
    defaults = ",".join(["/ardupilot/Tools/autotest/default_params/copter.parm"] + [f"/{p}" for p in AP_PARMS])
    sh(["docker", "rm", "-f", sitl], capture_output=True)
    try:
        sh(["docker", "create", "--name", sitl, "-p", f"127.0.0.1:{port}:5762", "-e", "SITL_SPEEDUP=1",
            "-e", f"SITL_HOME={HOME[0]},{HOME[1]},{HOME[2]},0", AP_IMAGE, "--defaults", defaults], capture_output=True)
        for p in AP_PARMS:
            sh(["docker", "cp", str(GOLDEN / p), f"{sitl}:/{p}"], capture_output=True)
        sh(["docker", "start", sitl], capture_output=True)
        with (out / f"{name}.console.txt").open("w") as f:
            rc = sh([python, "-u", str(HERE / "spoof_fly.py"), "--connect", f"tcp:127.0.0.1:{port}",
                     *fly_args(*case, str(out / f"{name}.raw.jsonl"))], stdout=f, stderr=subprocess.STDOUT).returncode
        with (out / f"{name}.sitl.log").open("w") as f:
            sh(["docker", "logs", sitl], stdout=f, stderr=subprocess.STDOUT)
        return rc
    finally:
        sh(["docker", "rm", "-f", sitl], capture_output=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--python", default=sys.executable, help="interpreter with pymavlink, for the ArduPilot companion")
    ap.add_argument("--only", choices=["px4", "ardupilot"])
    ap.add_argument("--cases", nargs="*", help="substring filters on case names")
    ap.add_argument("--px4-lanes", type=int, default=3)
    ap.add_argument("--ap-lanes", type=int, default=2)
    ap.add_argument("--force", action="store_true", help="re-fly cases whose log exists")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    cases = [c for c in all_cases() if (a.only in (None, c[0]))
             and (not a.cases or any(s in case_name(*c) for s in a.cases))]
    if a.list:
        print("\n".join(case_name(*c) for c in cases))
        return 0
    RUNS.mkdir(parents=True, exist_ok=True)
    todo = [c for c in cases if a.force or not (RUNS / f"{case_name(*c)}.raw.jsonl").exists()]
    lanes = {"px4": queue.Queue(), "ardupilot": queue.Queue()}
    for i in range(a.px4_lanes):
        lanes["px4"].put(i)
    for i in range(a.ap_lanes):
        lanes["ardupilot"].put(i)
    t0 = time.monotonic()

    def fly(case):
        q = lanes[case[0]]
        lane = q.get()
        try:
            t = time.monotonic()
            rc = run_px4(lane, case, RUNS) if case[0] == "px4" else run_ardupilot(lane, case, RUNS, a.python)
            print(f"{case_name(*case)} lane {lane} rc={rc} {time.monotonic() - t:.0f}s", flush=True)
        finally:
            q.put(lane)

    # One pool per autopilot, so a worker never blocks on the other autopilot's lanes.
    with ThreadPoolExecutor(a.px4_lanes) as ex_px4, ThreadPoolExecutor(a.ap_lanes) as ex_ap:
        futs = [(ex_px4 if c[0] == "px4" else ex_ap).submit(fly, c) for c in todo]
        for f in futs:
            f.result()
    print(f"{len(todo)} flights, wall {time.monotonic() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
