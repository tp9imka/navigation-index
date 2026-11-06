#!/usr/bin/env python3
"""Scripted MCP client: drives mav_mcp_server.py over stdio against ArduCopter SITL and
writes every JSON-RPC request/response to a transcript. No LLM involved: the decisions an
agent would make (switch source on degraded GNSS, then RTL) are hard-coded here, so the
server can be verified end to end without an API key.

A second pymavlink link (--sim-connect) plays the jammer by toggling SIM_GPS_DISABLE.
Run samples/ardupilot-ekf3-source-switch/source_switch.py --setup once first so EKF3
source set 2 is ExternalNav (SITL vicon).
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SURVEY_AREA = [[-35.36290, 149.16480], [-35.36290, 149.16620],
               [-35.36190, 149.16620], [-35.36190, 149.16480]]
OUTSIDE_FENCE = (-35.37000, 149.16520)
GOTO_POINT = (-35.36300, 149.16480)
SURVEY_ALT_M = 20
SURVEY_SPACING_M = 25
CRUISE_S = 25
DEGRADE_POLL_S = 20
EXTNAV_HOLD_S = 15
RTL_TIMEOUT_S = 120
POLL_S = 2.0


class McpClient:
    def __init__(self, cmd, transcript):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.t = open(transcript, "w")
        self.next_id = 1

    def note(self, text):
        print(f"# {text}")
        self.t.write(json.dumps({"note": text, "t": round(time.time(), 1)}) + "\n")
        self.t.flush()

    def send(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = self.next_id
            self.next_id += 1
        self.t.write(json.dumps({"->": msg}) + "\n")
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        if notify:
            return None
        reply = json.loads(self.p.stdout.readline())
        self.t.write(json.dumps({"<-": reply}) + "\n")
        self.t.flush()
        return reply

    def tool(self, name, **args):
        reply = self.send("tools/call", {"name": name, "arguments": args})
        if "error" in reply:
            print(f"{name}: RPC error {reply['error']}")
            return True, reply["error"]
        res = reply["result"]
        body = json.loads(res["content"][0]["text"])
        print(f"{name}({json.dumps(args)[:80]}) => {'ERROR ' if res['isError'] else ''}"
              f"{json.dumps(body)[:200]}")
        return res["isError"], body

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)
        self.t.close()


def sim_gps(url, enabled):
    from pymavlink import mavutil
    m = mavutil.mavlink_connection(url, source_system=251)
    m.wait_heartbeat(timeout=10)
    m.mav.param_set_send(m.target_system, m.target_component, b"SIM_GPS_DISABLE",
                         0.0 if enabled else 1.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
    ack = m.recv_match(type="PARAM_VALUE", condition="PARAM_VALUE.param_id=='SIM_GPS_DISABLE'",
                       blocking=True, timeout=5)
    m.close()
    return None if ack is None else ack.param_value


def flight(c, args):
    c.send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                          "clientInfo": {"name": "run_transcript", "version": "0"}})
    c.send("notifications/initialized", notify=True)
    c.send("tools/list")
    c.tool("get_state")
    c.tool("get_nav_health")

    c.note("safety: target outside fence, then altitude above the band")
    c.tool("goto", lat=OUTSIDE_FENCE[0], lon=OUTSIDE_FENCE[1], rel_alt_m=20)
    c.tool("arm_takeoff", rel_alt_m=120)

    c.note("takeoff and survey")
    err, _ = c.tool("arm_takeoff", rel_alt_m=SURVEY_ALT_M)
    if err:
        return
    c.tool("goto", lat=GOTO_POINT[0], lon=GOTO_POINT[1], rel_alt_m=SURVEY_ALT_M, wait_s=40)
    err, plan = c.tool("plan_survey", polygon=SURVEY_AREA, spacing_m=SURVEY_SPACING_M,
                       rel_alt_m=SURVEY_ALT_M)
    if err:
        return
    c.tool("upload_mission", waypoints=plan["waypoints"], rtl_at_end=True, start=True)
    time.sleep(CRUISE_S)
    c.tool("get_state")
    c.tool("get_nav_health")

    c.note("jammer: SIM_GPS_DISABLE=1 on a separate MAVLink link")
    c.note(f"SIM_GPS_DISABLE now {sim_gps(args.sim_connect, enabled=False)}")
    end = time.time() + DEGRADE_POLL_S
    while time.time() < end:
        _, h = c.tool("get_nav_health")
        if not h.get("gnss_ok", True):
            break
        time.sleep(POLL_S)

    c.note("agent policy: GNSS degraded => vision source set 2 (ExternalNav), then RTL")
    c.tool("set_ekf_source_set", source_set=2)
    end = time.time() + EXTNAV_HOLD_S
    while time.time() < end:
        c.tool("get_nav_health")
        time.sleep(POLL_S * 2)
    c.tool("set_mode", mode="RTL")
    end = time.time() + RTL_TIMEOUT_S
    while time.time() < end:
        _, s = c.tool("get_state")
        if not s.get("armed", True):
            break
        time.sleep(POLL_S * 2)
    c.tool("get_nav_health")

    c.note("restore GPS and source set 1 for the next run")
    c.note(f"SIM_GPS_DISABLE now {sim_gps(args.sim_connect, enabled=True)}")
    time.sleep(5)
    c.tool("set_ekf_source_set", source_set=1)
    c.tool("get_state")


def dry(c, args):
    c.send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                          "clientInfo": {"name": "run_transcript", "version": "0"}})
    c.tool("get_state")
    c.tool("goto", lat=-35.36250, lon=149.16560, rel_alt_m=25)
    c.tool("goto", lat=OUTSIDE_FENCE[0], lon=OUTSIDE_FENCE[1], rel_alt_m=25)
    c.tool("set_mode", mode="AUTO")
    c.tool("set_ekf_source_set", source_set=2)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--connect", default="tcp:127.0.0.1:5762", help="link for the MCP server")
    p.add_argument("--sim-connect", default="tcp:127.0.0.1:5763", help="link for the jammer")
    p.add_argument("--scenario", choices=("flight", "dry"), default="flight")
    p.add_argument("--transcript", default="transcript.jsonl")
    p.add_argument("--log", default="mav_mcp_commands.jsonl")
    args = p.parse_args()
    cmd = [sys.executable, str(HERE / "mav_mcp_server.py"), "--connect", args.connect,
           "--log", args.log]
    if args.scenario == "dry":
        cmd.append("--dry-run")
    c = McpClient(cmd, args.transcript)
    try:
        (flight if args.scenario == "flight" else dry)(c, args)
    finally:
        c.close()


if __name__ == "__main__":
    main()
