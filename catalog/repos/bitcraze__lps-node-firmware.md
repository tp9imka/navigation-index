# Loco Positioning node firmware

`repo:bitcraze/lps-node-firmware` - <https://github.com/bitcraze/lps-node-firmware>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 88 | C | LGPL-3.0 | 2026-11-04 | False | production | medium |

Firmware for Bitcraze Loco Positioning UWB anchors and tags (DW1000), supporting two-way ranging and TDoA modes.

**Why it matters:** Off-the-shelf UWB infrastructure for GNSS-denied indoor positioning tests.

**Hackathon notes:** Needs Loco nodes; configure anchors with the Crazyflie client.

**Concepts:** [RF localization and direction finding](../concepts/rf-localization.md), [Indoor and pedestrian navigation](../concepts/indoor-pedestrian.md)

**Tags:** `uwb`, `dw1000`, `anchor`, `tdoa`

**Domains:** air, ground

## Related

- integrates_with: [Crazyflie firmware](../repos/bitcraze__crazyflie-firmware.md)
- evaluated_on: [UTIL UWB TDoA dataset tools](../repos/williamwenda__uwb_tdoa_dataset.md)

## Referenced by

- [Crazyflie firmware](../repos/bitcraze__crazyflie-firmware.md) (integrates_with)
- [uwb-localization (MAV swarm)](../repos/lijx10__uwb-localization.md) (alternative_to)
- [UTIL UWB TDoA dataset tools](../repos/williamwenda__uwb_tdoa_dataset.md) (evaluated_on)
- [Loco Positioning System documentation](../resources/bitcraze-loco-positioning.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
