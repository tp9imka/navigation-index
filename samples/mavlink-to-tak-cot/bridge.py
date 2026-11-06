"""MAVLink -> CoT bridge (sketch). Requires: pip install pymavlink pytak.

  python3 bridge.py --mavlink udpin:0.0.0.0:14550 --cot-url udp+wo://239.2.3.1:6969
  python3 bridge.py --mavlink udpin:0.0.0.0:14550 --cot-url tcp://takserver.local:8087
"""
import argparse
import asyncio
from configparser import ConfigParser

import pytak
from pymavlink import mavutil

import cot

MIN_SEND_INTERVAL_S = 1.0  # TAK clients do not need 10-50 Hz autopilot rates


class MavlinkToCot(pytak.QueueWorker):
    def __init__(self, queue, config, args):
        super().__init__(queue, config)
        self.args = args

    async def run(self):
        loop = asyncio.get_running_loop()
        conn = mavutil.mavlink_connection(self.args.mavlink)
        await loop.run_in_executor(None, conn.wait_heartbeat)
        uid = self.args.uid or f"mavlink-sys{conn.target_system}"
        last_sent = 0.0
        while True:
            # recv_match blocks; keep it off the asyncio loop
            msg = await loop.run_in_executor(
                None, lambda: conn.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=5))
            # keep draining the link so we never fall behind; just drop extra fixes
            if msg is None or loop.time() - last_sent < MIN_SEND_INTERVAL_S:
                continue
            last_sent = loop.time()
            await self.put_queue(cot.from_global_position_int(
                msg, uid, callsign=self.args.callsign, geoid_separation_m=self.args.geoid_sep))


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mavlink", default="udpin:0.0.0.0:14550")
    p.add_argument("--cot-url", default="udp+wo://239.2.3.1:6969")
    p.add_argument("--uid")
    p.add_argument("--callsign", default="UAV-1")
    p.add_argument("--geoid-sep", type=float, default=0.0, help="geoid separation N in metres")
    args = p.parse_args()

    config = ConfigParser()
    config["mavcot"] = {"COT_URL": args.cot_url}
    config = config["mavcot"]
    clitool = pytak.CLITool(config)
    await clitool.setup()
    clitool.add_tasks({MavlinkToCot(clitool.tx_queue, config, args)})
    await clitool.run()


if __name__ == "__main__":
    asyncio.run(main())
