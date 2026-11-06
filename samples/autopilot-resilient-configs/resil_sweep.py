#!/usr/bin/env python3
"""Anti-spoof config sweep on PX4 v1.17 SIH and ArduCopter 4.6.3 SITL: every config in
configs/ x coherent drag 0.3 / 1 / 3 m/s + a clean flight, x seeds. Parallel Docker lanes,
same boot sequences as samples/autopilot-spoof-response/spoof_sweep.py. Stdlib on the host,
plus pymavlink for the ArduPilot companion (--python).

    python3 resil_sweep.py --python /path/to/venv/bin/python     # all cases, skips logs that exist
    python3 resil_sweep.py --list --cases lua                    # case names (substring filter)
Docker names are prefixed resil-; ArduPilot lanes publish host ports 15830+lane.
"""
from __future__ import annotations

import argparse
import os
import json
import queue
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "autopilot-spoof-response"))

import spoof_sweep as S  # noqa: E402

RUNS = HERE / "runs"
CONFIGS = HERE / "configs"
LUA = HERE / "scripts" / "gnss_extnav_switch.lua"
PREFIX = "resil"
AP_PORT0 = 15830
AP_PORT_MAX = 15839
RATES = (0.3, 1.0, 3.0)
SEEDS = (1, 2, 3)
PX4_BOOT_PARAMS = {"SENS_EN_AGPSIM"}          # reboot_required in PX4 v1.17
PX4_CONFIGS = ("default", "ev-vel", "ev-vel-gpsmode1", "ev-vel-gpsmode1-gates3", "agp-gpsmode1",
               "companion-monitor")
AP_CONFIGS = ("default", "fuse-all-vel", "glitch-clip", "lua-switch", "lua-switch-fuse-all-vel",
              "dual-gps-affinity", "dual-gps-blend")


def config_file(ap: str, cfg: str) -> Path:
    return CONFIGS / ap / (f"{cfg}.params" if ap == "px4" else f"{cfg}.parm")


def read_params(path: Path) -> dict[str, str]:
    import resil_fly
    return resil_fly.read_params(path)


def case_name(ap, cfg, kind, rate, seed):
    return f"{ap}-{cfg}-{kind}-{rate:g}-s{seed}" if kind != "none" else f"{ap}-{cfg}-clean-s{seed}"


def all_cases(seeds=SEEDS):
    for ap, cfgs in (("px4", PX4_CONFIGS), ("ardupilot", AP_CONFIGS)):
        for cfg in cfgs:
            for seed in seeds:
                for r in RATES:
                    yield ap, cfg, "coherent", r, seed
                yield ap, cfg, "none", 0.0, seed


def fly_args(ap, cfg, kind, rate, seed, log, cfg_path):
    args = ["--autopilot", ap, "--config", cfg, "--spoof", kind, "--rate", str(rate), "--seed", str(seed),
            "--log", log, "--params", cfg_path]
    if cfg == "companion-monitor":
        args.append("--monitor")
    if cfg.startswith("dual-gps"):
        args.append("--gps2")
    return args


sh = S.sh
FLAGS_POLL_S = 2.0
PX4_FLAGS = ("cs_gnss_pos", "cs_gnss_vel", "cs_gnss_fault", "cs_gnss_hgt_fault", "cs_ev_pos", "cs_ev_vel",
             "cs_aux_gpos", "cs_inertial_dead_reckoning")


def parse_listener(text: str) -> dict | None:
    """px4-listener estimator_status_flags => {"t_sim": s, flag: bool}; timestamp is hrt = SIH sim time."""
    out = {}
    for line in text.splitlines():
        k, _, v = line.strip().partition(": ")
        if k == "timestamp" and "t_sim" not in out:
            out["t_sim"] = int(v.split()[0]) * 1e-6
        elif k in PX4_FLAGS:
            out[k] = v.strip() == "True"
    return out if "t_sim" in out and len(out) > 1 else None


def poll_px4_flags(sitl: str, path: Path, stop: threading.Event) -> None:
    """EKF2 control status is not on MAVLink; sample it from the PX4 shell during the flight."""
    with path.open("w") as f:
        while not stop.wait(FLAGS_POLL_S):
            r = subprocess.run(["docker", "exec", sitl, "sh", "-c",
                                "cd /px4/rootfs && /px4/bin/px4-listener estimator_status_flags"],
                               capture_output=True, text=True, check=False)
            d = parse_listener(r.stdout)
            if d:
                f.write(json.dumps(d) + "\n")
                f.flush()


def run_px4(lane, case, out):
    sitl, client = f"{PREFIX}-px4-l{lane}-sitl", f"{PREFIX}-px4-l{lane}-client"
    name = case_name(*case)
    boot = {k: v for k, v in read_params(config_file("px4", case[1])).items() if k in PX4_BOOT_PARAMS}
    boot_cmd = " && ".join(f"/px4/bin/px4-param set {k} {v} >/dev/null" for k, v in boot.items())
    sh(["docker", "rm", "-f", client, sitl], capture_output=True)
    try:
        sh(["docker", "run", "-d", "--name", sitl, "-e", f"PX4_HOME_LAT={S.HOME[0]}", "-e", f"PX4_HOME_LON={S.HOME[1]}",
            "-e", f"PX4_HOME_ALT={S.HOME[2]}", S.PX4_IMAGE], capture_output=True)
        time.sleep(S.BOOT_WAIT_S)
        sh(["docker", "exec", sitl, "sh", "-c", "cd /px4/rootfs && /px4/bin/px4-param set SENS_EN_GPSSIM 0 >/dev/null && "
            "/px4/bin/px4-param set MAV_USEHILGPS 1 >/dev/null && " + (boot_cmd + " && " if boot_cmd else "")
            + "/px4/bin/px4-param save"], capture_output=True)
        sh(["docker", "restart", sitl], capture_output=True)
        sh(["docker", "run", "-d", "--name", client, "--network", f"container:{sitl}", "--entrypoint", "sh",
            S.CLIENT_IMAGE, "-c", "mkdir -p /nav && exec sleep infinity"], capture_output=True)
        time.sleep(S.BOOT_WAIT_S)
        tar = subprocess.Popen(["tar", "--no-xattrs", "--no-mac-metadata", "-C", str(ROOT), "--exclude", "runs",
                                "--exclude", "screenshots", "--exclude", "__pycache__", "--exclude", "data/v2*",
                                "-cf", "-", "samples/golden-demo", "samples/golden-demo-px4", "samples/altpnt-integrity",
                                "samples/autopilot-spoof-response", "samples/autopilot-resilient-configs",
                                "templates/project-repo/src"],
                               stdout=subprocess.PIPE, env=os.environ | {"COPYFILE_DISABLE": "1"})
        sh(["docker", "cp", "-", f"{client}:/nav"], stdin=tar.stdout, capture_output=True)
        tar.wait()
        cfg_path = f"/nav/samples/autopilot-resilient-configs/configs/px4/{case[1]}.params"
        stop = threading.Event()
        poller = threading.Thread(target=poll_px4_flags, args=(sitl, out / f"{name}.flags.jsonl", stop), daemon=True)
        poller.start()
        with (out / f"{name}.console.txt").open("w") as f:
            rc = sh(["docker", "exec", client, "python", "-u", "/nav/samples/autopilot-resilient-configs/resil_fly.py",
                     *fly_args(*case, f"/nav/{name}.raw.jsonl", cfg_path)], stdout=f, stderr=subprocess.STDOUT).returncode
        stop.set()
        poller.join()
        sh(["docker", "cp", f"{client}:/nav/{name}.raw.jsonl", str(out / f"{name}.raw.jsonl")], capture_output=True)
        with (out / f"{name}.sitl.log").open("w") as f:
            sh(["docker", "logs", sitl], stdout=f, stderr=subprocess.STDOUT)
        return rc
    finally:
        sh(["docker", "rm", "-f", client, sitl], capture_output=True)


def run_ardupilot(lane, case, out, python):
    sitl, port = f"{PREFIX}-ap-l{lane}", AP_PORT0 + lane
    assert port <= AP_PORT_MAX
    name = case_name(*case)
    cfg = config_file("ardupilot", case[1])
    defaults = ",".join(["/ardupilot/Tools/autotest/default_params/copter.parm"] + [f"/{p}" for p in S.AP_PARMS]
                        + ["/config.parm"])
    sh(["docker", "rm", "-f", sitl], capture_output=True)
    try:
        sh(["docker", "create", "--name", sitl, "-p", f"127.0.0.1:{port}:5762", "-e", "SITL_SPEEDUP=1",
            "-e", f"SITL_HOME={S.HOME[0]},{S.HOME[1]},{S.HOME[2]},0", S.AP_IMAGE, "--defaults", defaults],
           capture_output=True)
        for p in S.AP_PARMS:
            sh(["docker", "cp", str(S.GOLDEN / p), f"{sitl}:/{p}"], capture_output=True)
        sh(["docker", "cp", str(cfg), f"{sitl}:/config.parm"], capture_output=True)
        if "SCR_ENABLE" in read_params(cfg):
            # entrypoint runs in /sitl; ArduPilot SITL loads ./scripts/*.lua
            stage = out / f".stage-{name}" / "sitl" / "scripts"
            stage.mkdir(parents=True, exist_ok=True)
            (stage / LUA.name).write_text(LUA.read_text())
            sh(["docker", "cp", str(stage.parent), f"{sitl}:/sitl"], capture_output=True)
        sh(["docker", "start", sitl], capture_output=True)
        with (out / f"{name}.console.txt").open("w") as f:
            rc = sh([python, "-u", str(HERE / "resil_fly.py"), "--connect", f"tcp:127.0.0.1:{port}",
                     *fly_args(*case, str(out / f"{name}.raw.jsonl"), str(cfg))],
                    stdout=f, stderr=subprocess.STDOUT).returncode
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
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--px4-lanes", type=int, default=3)
    ap.add_argument("--ap-lanes", type=int, default=3)
    ap.add_argument("--force", action="store_true", help="re-fly cases whose log exists")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.ap_lanes > AP_PORT_MAX - AP_PORT0 + 1:
        raise SystemExit(f"at most {AP_PORT_MAX - AP_PORT0 + 1} ArduPilot lanes (ports {AP_PORT0}-{AP_PORT_MAX})")
    cases = [c for c in all_cases(a.seeds) if (a.only in (None, c[0]))
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

    with ThreadPoolExecutor(max(1, a.px4_lanes)) as ex_px4, ThreadPoolExecutor(max(1, a.ap_lanes)) as ex_ap:
        futs = [(ex_px4 if c[0] == "px4" else ex_ap).submit(fly, c) for c in todo]
        for f in futs:
            f.result()
    print(f"{len(todo)} flights, wall {time.monotonic() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
