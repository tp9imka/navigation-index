# flexPTP

`repo:epagris/flexptp` - <https://github.com/epagris/flexPTP>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 65 | C | MIT | 2026-10-27 | False | active-research | medium |

PTP (IEEE 1588, also 802.1AS) for Cortex-M4/M7 microcontrollers: master and slave ordinary clock, E2E and P2P, L2 and L4 transports, one- and two-step. MIT licence, with a journal paper.

**Why it matters:** Puts PTP on the MCU next to a sensor, so each sensor node timestamps in a shared timebase.

**Hackathon notes:** Needs an MCU with an Ethernet MAC that supports PTP timestamps (STM32F7/H7 class). Good fit for a sensor-network TDOA demo if the boards are at hand.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `ptp`, `embedded`, `stm32`, `802.1as`, `mcu`

**Domains:** multi

## Related

- integrates_with: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
