# Fully On-board Low-Power Localization with Multizone Time-of-Flight Sensors on Nano-UAVs

`res:muller-2023-nano-uav-mcl-multizone-tof` - paper - <https://arxiv.org/abs/2212.00710>

**By:** Hanna Muller, Nicky Zimmerman, Tommaso Polonelli, Michele Magno, Jens Behley, Cyrill Stachniss, Luca Benini - **Year:** 2023 - **Level:** intermediate - **Access:** open

DATE 2023 (venue from the AF-MCL reference list); arXiv full text read. Global Monte Carlo localization on a Crazyflie 2.1 with two 8x8-zone VL53L5CX ToF sensors and a GAP9 RISC-V processor, beam end-point (EDT) model on a 0.05 m grid. On recorded real sequences replayed with six seeds in a 31.2 m2 map: 0.15 m accuracy and above 95 % success with enough particles; the initial estimate can start in the wrong maze and converge as the drone moves. Onboard latency 0.2-30 ms depending on particle count.

## Key takeaways

- Map-based global localization from sparse ToF on a nano drone is published and onboard-capable
- Disambiguation is passive: hypotheses resolve as the drone flies its path, not by a chosen move
- Success numbers come from replayed real flight logs, not closed-loop recovery flights

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `monte-carlo-localization`, `nano-uav`, `tof`, `global-localization`, `peer-reviewed`

## Related

- uses: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)

## Referenced by

- [Monte Carlo-Based Indoor UAV Localization in Dynamic Environments Using Only Four Onboard Range Sensors](../../catalog/resources/af-mcl-four-range-uav-2026.md) (cites)

_Indexed by lane(s): relocalization-prior-art_
