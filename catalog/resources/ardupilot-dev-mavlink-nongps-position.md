# Non-GPS Position Estimation

`res:ardupilot-dev-mavlink-nongps-position` - doc - <https://ardupilot.org/dev/docs/mavlink-nongps-position-estimation.html>

**By:** ArduPilot Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

Developer page listing the MAVLink messages ArduPilot accepts for external position/velocity estimates and their expected frames.

## Key takeaways

- Lists VISION_POSITION_ESTIMATE, VISION_SPEED_ESTIMATE, ODOMETRY, GPS_INPUT
- Starting point for writing your own nav source

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `mavlink`, `external-nav`

## Related

- explains: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)

_Indexed by lane(s): autopilots_
