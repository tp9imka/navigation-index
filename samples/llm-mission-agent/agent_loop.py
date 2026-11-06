#!/usr/bin/env python3
"""Claude tool-use loop over the MAVLink MCP server (and optionally the navigation-index
MCP server), without Claude Code. Needs `pip install anthropic pymavlink` and an API key.

  python3 agent_loop.py --connect tcp:127.0.0.1:5762 \
      --prompt "Survey the fence polygon at 20 m; if GNSS degrades switch to source set 2 and RTL."

Tools of every MCP server are exposed to Claude as "<server>__<tool>". The loop is manual
(not the SDK tool runner) because the tools live behind stdio MCP subprocesses.
NOT RUN by the authors of this sample: no API key was available when it was written.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import anthropic

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_MODEL = "claude-sonnet-5-5"
MAX_TURNS = 40
MAX_TOKENS = 16000
ACTUATING = {"arm_takeoff", "goto", "set_mode", "upload_mission", "set_ekf_source_set"}

SYSTEM = """You operate a simulated ArduCopter (ArduPilot SITL) through MCP tools.
Rules:
- Read mavlink__get_state and mavlink__get_nav_health before any command, and again after
  each command to confirm the effect: a command ACK is not proof the vehicle moved.
- A tool result with rejected=true is a safety decision of the server. Do not retry the same
  command with tweaked numbers to get around it; report it.
- If get_nav_health says gnss_ok=false or verdict degraded/lost during flight, switch to EKF
  source set 2 (vision/ExternalNav) and then RTL, unless the user said otherwise.
- Stay terse. End with a short report: what you did, what the vehicle did, what you could not
  verify."""


class McpProcess:
    def __init__(self, name, cmd):
        self.name = name
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.next_id = 1
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "agent_loop", "version": "0"}})
        self.notify("notifications/initialized")
        self.tools = self.rpc("tools/list")["tools"]

    def notify(self, method):
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.p.stdin.flush()

    def rpc(self, method, params=None):
        msg = {"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params or {}}
        self.next_id += 1
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        reply = json.loads(self.p.stdout.readline())
        if "error" in reply:
            raise RuntimeError(f"{self.name} {method}: {reply['error']}")
        return reply["result"]

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--connect", default="tcp:127.0.0.1:5762")
    ap.add_argument("--fence", default=str(HERE / "fence.example.json"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--with-index", action="store_true", help="also attach tools/mcp_server.py")
    ap.add_argument("--confirm", action="store_true", help="ask on the terminal before actuating tools")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--effort", default="medium", choices=("low", "medium", "high", "xhigh", "max"))
    ap.add_argument("--transcript", default="agent_transcript.jsonl")
    args = ap.parse_args()

    mav_cmd = [sys.executable, str(HERE / "mav_mcp_server.py"), "--connect", args.connect,
               "--fence", args.fence, "--log", "agent_commands.jsonl"]
    if args.dry_run:
        mav_cmd.append("--dry-run")
    servers = {"mavlink": McpProcess("mavlink", mav_cmd)}
    if args.with_index:
        servers["navindex"] = McpProcess("navindex", [sys.executable, str(REPO / "tools" / "mcp_server.py")])

    tools = [{"name": f"{s}__{t['name']}", "description": t["description"],
              "input_schema": t["inputSchema"]} for s, srv in servers.items() for t in srv.tools]
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": args.prompt}]
    log = open(args.transcript, "w")
    log.write(json.dumps({"model": args.model, "prompt": args.prompt, "t": time.time()}) + "\n")

    for _ in range(MAX_TURNS):
        # fallbacks="default": a safety-classifier decline is re-run server-side on another model
        response = client.beta.messages.create(
            model=args.model, max_tokens=MAX_TOKENS, system=SYSTEM, tools=tools,
            messages=messages, output_config={"effort": args.effort},
            betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        log.write(json.dumps({"assistant": [b.model_dump() for b in response.content],
                              "stop_reason": response.stop_reason}, default=str) + "\n")
        log.flush()
        for b in response.content:
            if b.type == "text":
                print(f"\nClaude: {b.text}")
        if response.stop_reason == "refusal":
            print(f"refused: {response.stop_details}")
            break
        if response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continue
        if response.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for b in response.content:
            if b.type != "tool_use":
                continue
            server, _, tool = b.name.partition("__")
            print(f"  -> {b.name} {json.dumps(b.input)[:160]}")
            if args.confirm and tool in ACTUATING and input("     approve? [y/N] ").lower() != "y":
                text, is_error = json.dumps({"rejected": True, "reason": "operator declined"}), True
            else:
                res = servers[server].rpc("tools/call", {"name": tool, "arguments": b.input})
                text, is_error = res["content"][0]["text"], res.get("isError", False)
            print(f"  <- {text[:200]}")
            log.write(json.dumps({"tool": b.name, "input": b.input, "result": text,
                                  "is_error": is_error}) + "\n")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": text,
                            "is_error": is_error})
        messages.append({"role": "user", "content": results})
    else:
        print(f"stopped after {MAX_TURNS} turns")
    log.close()
    for srv in servers.values():
        srv.close()


if __name__ == "__main__":
    main()
