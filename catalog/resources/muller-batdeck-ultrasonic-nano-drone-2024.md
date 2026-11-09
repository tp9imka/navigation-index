# BatDeck - Ultra Low-power Ultrasonic Ego-velocity Estimation and Obstacle Avoidance on Nano-drones

`res:muller-batdeck-ultrasonic-nano-drone-2024` - paper - <https://arxiv.org/abs/2412.10048>

**By:** Hanna Müller, Victor Kartsch, Michele Magno, Luca Benini - **Year:** 2024 - **Level:** intermediate - **Access:** open

Preprint on arXiv (ETH Zurich and University of Bologna). Adds TDK ultrasonic sensors to a Crazyflie 2.1 for obstacle avoidance and ground velocity, and compares them in real office flights with a forward VL53L1 laser ToF on a Multi-ranger deck and with the Flow deck v2. With the VL53L1 all 10 flights crashed after 4 m on average, mostly on undetected glass doors.

## Key takeaways

- VL53L1 laser ToF misses glass doors and struggles with black objects
- 27 deg VL53L1 cone misses objects that fill little of it, such as a chair edge
- Flow deck velocity degrades over a featureless table; fine over carpet

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `crazyflie`, `vl53l1x`, `multi-ranger`, `ultrasonic`, `glass`, `preprint`

## Related

- evaluates: [Multi-ranger deck](../../catalog/resources/bitcraze-multi-ranger-deck.md)
- evaluates: [Flow deck v2](../../catalog/resources/bitcraze-flow-deck-v2.md)

_Indexed by lane(s): loop-23_
