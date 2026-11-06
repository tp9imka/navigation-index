# GPSDO PTP Master

`repo:rjrouquette/gpsdo` - <https://github.com/rjrouquette/gpsdo>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | C++ | Unlicense | 2024-06-10 | False | research-prototype | low |

A GPS-disciplined PTP grandmaster on a TI MSP432E4 MCU: u-blox receiver, software-disciplined crystal, PPS output, and NTP, PTP and SNMP servers on PoE with battery backup.

**Why it matters:** A single-board GNSS time server for a sensor network, the kind of node a distributed-sensing build needs.

**Hackathon notes:** Hardware specific; read for architecture of a small grandmaster.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ptp`, `gpsdo`, `grandmaster`, `ntp`, `microcontroller`

**Domains:** multi

## Related

- integrates_with: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
