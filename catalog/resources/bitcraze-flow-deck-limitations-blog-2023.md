# Go with the Flow: Relative Positioning with the Flow deck

`res:bitcraze-flow-deck-limitations-blog-2023` - blog - <https://www.bitcraze.io/2023/11/go-with-the-flow-relative-positioning-with-the-flow-deck/>

**By:** Bitcraze - **Year:** 2023 - **Level:** intro - **Access:** open

Bitcraze blog post on how the Flow deck v2 estimates position by dead reckoning in the onboard EKF and where it fails. Lists floor, light and motion conditions that make the estimate drift or diverge. Gives no drift-per-metre figure.

## Key takeaways

- Needs a textured, matte, well-lit floor; wood is best
- Fails over plain or black floors, in low light and over its own shadow
- Frequent yaw causes drift; do not fly too high

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `crazyflie`, `optical-flow`, `pmw3901`, `failure-modes`

## Related

- explains: [Flow deck v2](../../catalog/resources/bitcraze-flow-deck-v2.md)
- explains: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)

_Indexed by lane(s): loop-23_
