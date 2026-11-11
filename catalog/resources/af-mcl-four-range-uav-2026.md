# Monte Carlo-Based Indoor UAV Localization in Dynamic Environments Using Only Four Onboard Range Sensors

`res:af-mcl-four-range-uav-2026` - paper - <https://arxiv.org/abs/2610.32645>

**By:** Mohammad Reza Ranjbar Divkoti, A. Pedro Aguiar - **Year:** 2026 - **Level:** intermediate - **Access:** open

Preprint (arXiv, Oct 2026), full text read. AF-MCL: 2D Monte Carlo localization in a known occupancy map from four single-point ranges plus measured yaw on a Crazyflie 2.1 with Flow and Multi-ranger decks. Likelihood field from the map EDT, beams inconsistent with the static map rejected at the previous estimate, and augmented-MCL particle injection (slow/fast likelihood averages) for kidnapping. Webots kidnapping test: recovery 2.9 s vs 16.9 s for plain MCL (simulation). Real flights in a 2.10 x 1.63 m arena: 6.4-7.7 cm mean error, filter run on a host PC, not onboard. Author list taken from the arXiv submitter and the HTML byline; not fully confirmed.

## Key takeaways

- Scan-to-map relocalization after kidnapping already runs on a Crazyflie with four ToF beams and a known map
- Same EDT likelihood field as the hub's close-area-relocalize matcher; recovery is passive (particle injection), no hover gate and no disambiguating move
- Kidnap recovery 2.9 s vs 16.9 s for plain MCL is a Webots number, not a flight number

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `monte-carlo-localization`, `kidnapped-robot`, `crazyflie`, `relocalization`, `preprint`

## Related

- uses: [Multi-ranger deck](../../catalog/resources/bitcraze-multi-ranger-deck.md)
- uses: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)
- cites: [Fully On-board Low-Power Localization with Multizone Time-of-Flight Sensors on Nano-UAVs](../../catalog/resources/muller-2023-nano-uav-mcl-multizone-tof.md)

_Indexed by lane(s): relocalization-prior-art_
