# MMCM_GPSDO

`repo:hamsternz/mmcm_gpsdo` - <https://github.com/hamsternz/MMCM_GPSDO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 33 | VHDL | ? | 2022-09-01 | False | research-prototype | low |

All-digital GPSDO in VHDL for a Basys3 FPGA board: steers the clock with MMCM phase shifts from a GPS 1PPS, showing frequency error on LEDs. Author describes the loop as simple and constants as empirical.

**Why it matters:** Minimal FPGA disciplining loop to read or extend with holdover logic.

**Hackathon notes:** Needs a Basys3 (Artix-7) and a GPS with PPS. No licence file per GitHub metadata - read, do not copy.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `gpsdo`, `fpga`, `vhdl`, `1pps`, `xilinx`

**Domains:** multi

## Related

- alternative_to: [STM32 GPSDO](../../catalog/repos/andrewbcn__stm32-gpsdo.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
