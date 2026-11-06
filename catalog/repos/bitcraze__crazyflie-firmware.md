# Crazyflie firmware

`repo:bitcraze/crazyflie-firmware` - <https://github.com/bitcraze/crazyflie-firmware>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,568 | C | GPL-3.0 | 2026-11-05 | False | production | high |

Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.

**Why it matters:** Mature indoor research platform where UWB/Lighthouse localisation and GPS-free estimation are first-class; widely used in swarm papers.

**Hackathon notes:** If you have Crazyflies, the Python lib gets you scripted flights in an hour. UWB Loco anchors make a good GNSS-denied testbed. Simulation via crazyswarm2 or the official SIL.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [bitcraze__crazyflie-firmware](../../docs/integration-cards/bitcraze__crazyflie-firmware.md) (integration-cards)
- [util-uwb-tdoa](../../docs/dataset-cards/util-uwb-tdoa.md) (dataset-cards)

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `crazyflie`, `uwb`, `lighthouse`, `flow-deck`, `kalman`, `nano-drone`, `tdoa`, `ekf`

**Domains:** air

## Related

- integrates_with: [cflib (Crazyflie Python library)](../../catalog/repos/bitcraze__crazyflie-lib-python.md)
- integrates_with: [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md)
- same_org: [ESP-Drone](../../catalog/repos/espressif__esp-drone.md)
- integrates_with: [Loco Positioning node firmware](../../catalog/repos/bitcraze__lps-node-firmware.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md) (integrates_with)
- [cflib (Crazyflie Python library)](../../catalog/repos/bitcraze__crazyflie-lib-python.md) (integrates_with)
- [Crazyflie simulation](../../catalog/repos/bitcraze__crazyflie-simulation.md) (same_org)
- [Loco Positioning node firmware](../../catalog/repos/bitcraze__lps-node-firmware.md) (integrates_with)
- [ESP-Drone](../../catalog/repos/espressif__esp-drone.md) (fork_of)
- [Swarm relative localization (ETH PBL)](../../catalog/repos/eth-pbl__swarm-relative-localization.md) (extends)
- [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md) (depends_on)
- [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md) (integrates_with)
- [dRehmFlight VTOL](../../catalog/repos/nickrehm__drehmflight.md) (alternative_to)
- [Loco Positioning System documentation](../../catalog/resources/bitcraze-loco-positioning.md) (explains)
- [Onboard Ranging-based Relative Localization and Stability for Lightweight Aerial Swarms](../../catalog/resources/li-onboard-relative-localization-swarms.md) (uses)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
