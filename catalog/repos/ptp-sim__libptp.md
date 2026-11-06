# LibPTP

`repo:ptp-sim/libptp` - <https://github.com/ptp-sim/libPTP>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 35 | C++ | GPL-3.0 | 2021-07-22 | False | research-prototype | low |

OMNeT++/INET library for simulating IEEE 1588-2008 networks: ordinary, boundary and transparent clocks, E2E and P2P delay, a PI servo with pluggable servos and filters, and power-law clock noise via LibPLN.

**Why it matters:** A packet-level PTP network simulator if a stdlib model is too coarse.

**Hackathon notes:** OMNeT++ setup is heavy and the repo was last pushed in 2021. Prefer sample:timing-network-holdover or clknetsim unless packet-level detail is required.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `ptp`, `omnet++`, `simulation`, `clock-noise`

**Domains:** multi

## Related

- alternative_to: [clknetsim](../../catalog/repos/mlichvar__clknetsim.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
