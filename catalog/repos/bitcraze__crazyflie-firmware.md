# Crazyflie firmware

`repo:bitcraze/crazyflie-firmware` - <https://github.com/bitcraze/crazyflie-firmware>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,568 | C | GPL-3.0 | 2026-11-05 | False | production | high |

Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.

**Why it matters:** Mature indoor research platform where UWB/Lighthouse localisation and GPS-free estimation are first-class; widely used in swarm papers.

**Hackathon notes:** If you have Crazyflies, the Python lib gets you scripted flights in an hour. UWB Loco anchors make a good GNSS-denied testbed. Simulation via crazyswarm2 or the official SIL.

**Concepts:** [Autopilots and flight control](../concepts/autopilot.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [RF localization and direction finding](../concepts/rf-localization.md), [Indoor and pedestrian navigation](../concepts/indoor-pedestrian.md), [Swarms and multi-agent navigation](../concepts/multi-agent.md)

**Tags:** `crazyflie`, `uwb`, `lighthouse`, `flow-deck`, `kalman`, `nano-drone`, `tdoa`, `ekf`

**Domains:** air

## Related

- integrates_with: [cflib (Crazyflie Python library)](../repos/bitcraze__crazyflie-lib-python.md)
- integrates_with: [Crazyswarm2](../repos/imrclab__crazyswarm2.md)
- same_org: [ESP-Drone](../repos/espressif__esp-drone.md)
- integrates_with: [Loco Positioning node firmware](../repos/bitcraze__lps-node-firmware.md)

## Referenced by

- [Aerostack2](../repos/aerostack2__aerostack2.md) (integrates_with)
- [cflib (Crazyflie Python library)](../repos/bitcraze__crazyflie-lib-python.md) (integrates_with)
- [Crazyflie simulation](../repos/bitcraze__crazyflie-simulation.md) (same_org)
- [Loco Positioning node firmware](../repos/bitcraze__lps-node-firmware.md) (integrates_with)
- [ESP-Drone](../repos/espressif__esp-drone.md) (fork_of)
- [Swarm relative localization (ETH PBL)](../repos/eth-pbl__swarm-relative-localization.md) (extends)
- [Crazyswarm2](../repos/imrclab__crazyswarm2.md) (depends_on)
- [Crazyswarm2](../repos/imrclab__crazyswarm2.md) (integrates_with)
- [dRehmFlight VTOL](../repos/nickrehm__drehmflight.md) (alternative_to)
- [Loco Positioning System documentation](../resources/bitcraze-loco-positioning.md) (explains)
- [Onboard Ranging-based Relative Localization and Stability for Lightweight Aerial Swarms](../resources/li-onboard-relative-localization-swarms.md) (uses)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
