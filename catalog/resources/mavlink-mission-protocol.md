# MAVLink Mission Protocol

`res:mavlink-mission-protocol` - doc - <https://mavlink.io/en/services/mission.html>

**By:** MAVLink project / Dronecode - **Year:** 2025 - **Level:** intermediate - **Access:** open

The microservice used to upload, download and clear waypoint missions, geofences and rally points between a GCS and an autopilot, with its handshake and retry rules.

## Key takeaways

- Defines MISSION_COUNT / MISSION_ITEM_INT handshake
- Same protocol carries geofence and rally point plans

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Mission planning and routing](../concepts/mission-planning.md)

**Tags:** `mavlink`, `mission`, `waypoints`, `geofence`

## Related

- has_code: [MAVLink](../repos/mavlink__mavlink.md)
- has_code: [MAVSDK](../repos/mavlink__mavsdk.md)
- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- part_of: [MAVLink Developer Guide](../resources/mavlink-developer-guide.md)

_Indexed by lane(s): docs-standards_
