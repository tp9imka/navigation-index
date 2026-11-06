# INAV

`repo:inavflight/inav` - <https://github.com/iNavFlight/inav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,290 | C | GPL-3.0 | 2026-11-02 | False | production | medium |

Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.

**Why it matters:** Lowest-cost path to GNSS waypoint navigation on FPV-class airframes; useful to show how small drones behave on GNSS loss and how RTH failsafes work.

**Hackathon notes:** Configure with INAV Configurator; supports MSP and a MAVLink telemetry subset. SITL exists but is less polished than PX4/ArduPilot. Good for physical demos on cheap hardware.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md)

**Tags:** `fpv`, `fixed-wing`, `rth`, `waypoints`, `msp`

**Domains:** air, ground

## Related

- alternative_to: [Betaflight](../../catalog/repos/betaflight__betaflight.md)
- integrates_with: [ExpressLRS](../../catalog/repos/expresslrs__expresslrs.md)

## Referenced by

- [Betaflight](../../catalog/repos/betaflight__betaflight.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
