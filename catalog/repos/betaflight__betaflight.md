# Betaflight

`repo:betaflight/betaflight` - <https://github.com/betaflight/betaflight>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11,748 | C | GPL-3.0 | 2026-11-05 | False | production | low |

Racing/freestyle-oriented flight controller firmware focused on attitude control and low-latency filtering. GPS Rescue was long its only navigation mode; releases since 2025 add altitude hold, position hold and waypoint flight plans (AUTOPILOT mode in 2026.6).

**Why it matters:** Dominant firmware on FPV drones seen in current conflicts; its navigation is still limited (GPS Rescue plus newer altitude/position hold and basic waypoints), which matters for C-UAS and EW-impact analysis.

**Hackathon notes:** Not a navigation platform; use for FPV-class hardware or to study how small drones react to link loss and GNSS jamming.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md)

**Tags:** `fpv`, `racing`, `gps-rescue`, `msp`

**Domains:** air

## Related

- alternative_to: [INAV](../../catalog/repos/inavflight__inav.md)
- integrates_with: [ExpressLRS](../../catalog/repos/expresslrs__expresslrs.md)

## Referenced by

- [ExpressLRS](../../catalog/repos/expresslrs__expresslrs.md) (integrates_with)
- [INAV](../../catalog/repos/inavflight__inav.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
