# MAVLink

`repo:mavlink/mavlink` - <https://github.com/mavlink/mavlink>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,475 | Python | NOASSERTION | 2026-11-05 | False | production | high |

Message definitions (XML dialects) and the pymavlink-based generator for the MAVLink micro air vehicle protocol, used by PX4, ArduPilot and most GCS tools.

**Why it matters:** The lingua franca of open-source UAS; any GCS, companion, Remote ID or C-UAS sensor integration ends up speaking it.

**Hackathon notes:** Add a custom dialect XML and regenerate bindings to prototype new messages (e.g. a jamming-detection report).

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `protocol`, `xml`, `dialects`, `generator`

**Domains:** air, ground, maritime, multi

## Related

- depends_on: [pymavlink](../repos/ardupilot__pymavlink.md)
- same_org: [MAVLink Developer Guide](../repos/mavlink__mavlink-devguide.md)

## Referenced by

- [node-mavlink](../repos/ardupilot__node-mavlink.md) (depends_on)
- [pymavlink](../repos/ardupilot__pymavlink.md) (depends_on)
- [MAVLink Developer Guide](../repos/mavlink__mavlink-devguide.md) (same_org)
- [rust-mavlink](../repos/mavlink__rust-mavlink.md) (depends_on)
- [MAVLink 2 and Message Signing](../resources/mavlink-2-signing.md) (has_code)
- [MAVLink Common Message Set (common.xml)](../resources/mavlink-common-messages.md) (has_code)
- [MAVLink Developer Guide](../resources/mavlink-developer-guide.md) (has_code)
- [MAVLink Mission Protocol](../resources/mavlink-mission-protocol.md) (has_code)
- [Open Drone ID (MAVLink microservice)](../resources/mavlink-opendroneid-microservice.md) (explains)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
