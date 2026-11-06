# MAVLink 2 and Message Signing

`res:mavlink-2-signing` - doc - <https://mavlink.io/en/guide/message_signing.html>

**By:** MAVLink project / Dronecode - **Year:** 2025 - **Level:** intermediate - **Access:** open

Describes MAVLink 2 packet signing: a shared-secret SHA-256 based signature and timestamp appended to frames to authenticate the link and resist replay.

## Key takeaways

- Signing authenticates but does not encrypt traffic
- Key distribution is left to the integrator
- Relevant for hardening drone C2 links against injection

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Electronic warfare resilience](../concepts/ew-resilience.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `mavlink2`, `signing`, `security`, `c2-link`

## Related

- has_code: [MAVLink](../repos/mavlink__mavlink.md)
- has_code: [MAVSDK](../repos/mavlink__mavsdk.md)
- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- part_of: [MAVLink Developer Guide](../resources/mavlink-developer-guide.md)

_Indexed by lane(s): docs-standards_
