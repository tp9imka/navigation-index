# PX4 EKF2 delayed fusion horizon: estimator_interface.cpp, TimestampedRingBuffer and EKF2_DELAY_MAX

`res:px4-ekf2-delayed-horizon-source` - doc - <https://github.com/PX4/PX4-Autopilot/blob/cb61f8c4f1f57573746f8a75999e24225ee6c0fc/src/modules/ekf2/EKF/estimator_interface.cpp>

**By:** PX4 Dev Team - **Year:** 2026 - **Level:** advanced - **Access:** open

Source read at PX4-Autopilot main cb61f8c (2026-10-29). External-vision samples are stamped time_us - EKF2_EV_DELAY - dt/2 and buffered; a sample is popped only when the delayed-horizon time is within 100 ms after its stamp. EKF2_DELAY_MAX defaults to 200 ms with a maximum of 1000 ms, and the observation buffer is 1.5 x EKF2_DELAY_MAX.

## Key takeaways

- A fix older than about 1 s cannot be fused at its capture time in PX4 EKF2
- Pi-class VPR fixes sit near or past that limit; plan a companion-side delayed-state filter
- Measured M2 top-5 match p95 0.82 s is already close

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `px4`, `ekf2`, `delayed-fusion`, `ev-delay`, `latency`

## Related

- part_of: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- cites: [Using PX4's Navigation Filter (EKF2)](../../catalog/resources/px4-ekf2-tuning-guide.md)

_Indexed by lane(s): innovation-pa-scheduling_
