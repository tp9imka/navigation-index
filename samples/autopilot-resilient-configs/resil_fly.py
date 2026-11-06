#!/usr/bin/env python3
"""One flight of a candidate anti-spoof configuration. Wraps samples/autopilot-spoof-response
spoof_fly.py (and through it the golden-demo companions) unchanged and adds:

- --params FILE: a committed config file (NAME VALUE lines) applied as EKF overrides before arming
- --monitor: the golden-demo companion monitor acts (PX4: EKF2_GPS_CTRL 0 + EKF2_EV_CTRL 5)
  instead of logging in shadow mode
- --gps2: a second, unspoofed GNSS receiver as GPS_INPUT gps_id 1 (ArduPilot GPS2_TYPE 14)

    python resil_fly.py --autopilot ardupilot --connect tcp:127.0.0.1:15830 --params configs/ardupilot/lua-switch.parm \
        --config lua-switch --spoof coherent --rate 1 --seed 1 --log runs/x.raw.jsonl
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPOOF_RESPONSE = HERE.parent / "autopilot-spoof-response"
sys.path.insert(0, str(SPOOF_RESPONSE))

import spoof_fly as F  # noqa: E402

F.INT_PARAMS |= {"EKF2_EV_CTRL", "EKF2_AGP_CTRL", "EKF2_AGP_MODE", "SENS_EN_AGPSIM"}
GPS2_ID = 1
GPS2_SEED_OFFSET = 1000


def read_params(path: Path) -> dict[str, str]:
    """NAME VALUE per line, '#' comments; the format of ArduPilot .parm and of configs/px4/*.params."""
    out = {}
    for line in Path(path).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            k, v = line.replace(",", " ").split()[:2]
            out[k] = v
    return out


def with_gps2(base):
    """ArduPilot companion that also feeds an honest second receiver (own noise, never spoofed)."""
    G = sys.modules["companion"]

    class DualGps(base):
        def __init__(self, a):
            super().__init__(a)
            self.rng2 = random.Random(a.seed + GPS2_SEED_OFFSET)
            self.gm2 = [0.0, 0.0]

        def send_gps_input(self) -> None:
            super().send_gps_input()
            dt = 1.0 / G.GPS_INPUT_HZ
            phi = math.exp(-dt / G.GNSS_GM_TAU_S)
            self.gm2 = [g * phi + self.rng2.gauss(0, G.GNSS_GM_SIGMA_M * math.sqrt(1 - phi * phi)) for g in self.gm2]
            ne = self.gm2[0] + self.rng2.gauss(0, G.GNSS_WHITE_M)
            nn = self.gm2[1] + self.rng2.gauss(0, G.GNSS_WHITE_M)
            dlat, dlon = G.offset_deg(nn, ne, self.truth[0])
            ve = self.truth_vel[0] + self.rng2.gauss(0, G.GNSS_VEL_WHITE_MPS)
            vn = self.truth_vel[1] + self.rng2.gauss(0, G.GNSS_VEL_WHITE_MPS)
            sim_ms = int((self.truth_sim_s or self.now()) * 1000)
            self.m.mav.gps_input_send(
                self.stamp_us(sim_ms / 1000), GPS2_ID, 0, G.GPS_WEEK_MS0 + sim_ms, G.GPS_WEEK, 3,
                int((self.truth[0] + dlat) * 1e7), int((self.truth[1] + dlon) * 1e7),
                self.truth_alt + self.rng2.gauss(0, 1.0), 0.8, 1.2, vn, ve, self.truth_vd,
                0.3, 1.5, 2.5, 14, 0)

    return DualGps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=False)
    ap.add_argument("--params", type=Path)
    ap.add_argument("--monitor", action="store_true")
    ap.add_argument("--gps2", action="store_true")
    mine, rest = ap.parse_known_args(argv)
    if mine.params:
        rest += [x for k, v in read_params(mine.params).items() for x in ("--set", f"{k}={v}")]
    a, ca, base = F.build(rest)
    if mine.monitor:
        ca.mode = "monitor"
    if mine.gps2:
        if a.autopilot != "ardupilot":
            raise SystemExit("--gps2 needs --autopilot ardupilot (PX4 v1.17 has no GPS_INPUT handler)")
        base = with_gps2(base)
    a.log.parent.mkdir(parents=True, exist_ok=True)
    c = F.make_companion(a, ca, base)
    c.record({"type": "RESIL", "params_file": mine.params.name if mine.params else None,
              "monitor": mine.monitor, "gps2": mine.gps2})
    c.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
