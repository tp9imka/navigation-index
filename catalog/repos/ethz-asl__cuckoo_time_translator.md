# cuckoo_time_translator

`repo:ethz-asl/cuckoo_time_translator` - <https://github.com/ethz-asl/cuckoo_time_translator>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 96 | C++ | NOASSERTION | 2022-06-30 | False | archived | medium |

ROS algorithms that translate a sensor's own hardware timestamps into host system time from one-way timing, estimating skew and offset.

**Why it matters:** Multi-sensor fusion (camera, IMU, LiDAR) breaks quietly when timestamps are off; this is the lightweight fix when PTP is not available on the sensor.

**Hackathon notes:** ROS1 catkin package; inactive since 2022, port the algorithm if on ROS 2.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md), [Sensor calibration](../concepts/calibration.md)

**Tags:** `timestamps`, `clock-skew`, `ros`, `sensor-sync`

**Domains:** multi

## Related

- same_org: [Kalibr](../repos/ethz-asl__kalibr.md)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
