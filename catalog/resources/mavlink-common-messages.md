# MAVLink Common Message Set (common.xml)

`res:mavlink-common-messages` - doc - <https://mavlink.io/en/messages/common.html>

**By:** MAVLink project / Dronecode - **Year:** 2025 - **Level:** intermediate - **Access:** open

Reference of all messages and commands in the common dialect, including GPS_RAW_INT, GPS_INPUT for injecting external position, ODOMETRY and VISION_POSITION_ESTIMATE for non-GNSS navigation sources.

## Key takeaways

- GPS_INPUT and VISION_POSITION_ESTIMATE are the hooks for feeding alternative PNT into an autopilot
- ODOMETRY carries full pose plus covariance
- Enumerations document EKF and GPS fix status flags

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Autopilots and flight control](../concepts/autopilot.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `mavlink`, `messages`, `gps_input`, `odometry`

## Related

- has_code: [MAVLink](../repos/mavlink__mavlink.md)
- has_code: [MAVSDK](../repos/mavlink__mavsdk.md)
- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [PX4 Autopilot](../repos/px4__px4-autopilot.md)

_Indexed by lane(s): docs-standards_
