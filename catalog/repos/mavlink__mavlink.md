# MAVLink

`repo:mavlink/mavlink` - <https://github.com/mavlink/mavlink>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,475 | Python | NOASSERTION | 2026-11-05 | False | production | high |

Message definitions (XML dialects) and the pymavlink-based generator for the MAVLink micro air vehicle protocol, used by PX4, ArduPilot and most GCS tools.

**Why it matters:** The lingua franca of open-source UAS; any GCS, companion, Remote ID or C-UAS sensor integration ends up speaking it.

**Hackathon notes:** Add a custom dialect XML and regenerate bindings to prototype new messages (e.g. a jamming-detection report).

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [mavlink__mavlink](../../docs/integration-cards/mavlink__mavlink.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `protocol`, `xml`, `dialects`, `generator`

**Domains:** air, ground, maritime, multi

## Related

- depends_on: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- same_org: [MAVLink Developer Guide](../../catalog/repos/mavlink__mavlink-devguide.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [node-mavlink](../../catalog/repos/ardupilot__node-mavlink.md) (depends_on)
- [pymavlink](../../catalog/repos/ardupilot__pymavlink.md) (depends_on)
- [MAVLink Developer Guide](../../catalog/repos/mavlink__mavlink-devguide.md) (same_org)
- [rust-mavlink](../../catalog/repos/mavlink__rust-mavlink.md) (depends_on)
- [MAVLink 2 and Message Signing](../../catalog/resources/mavlink-2-signing.md) (has_code)
- [MAVLink Common Message Set (common.xml)](../../catalog/resources/mavlink-common-messages.md) (has_code)
- [MAVLink Developer Guide](../../catalog/resources/mavlink-developer-guide.md) (has_code)
- [MAVLink Mission Protocol](../../catalog/resources/mavlink-mission-protocol.md) (has_code)
- [Open Drone ID](../../catalog/resources/mavlink-opendroneid-microservice.md) (explains)
- [ArduPilot EKF3 source-set switch under GPS denial](../../catalog/samples/ardupilot-ekf3-source-switch.md) (explains)
- [How PX4 EKF2 and ArduPilot EKF3 handle a spoofed GNSS: source walk-through plus a 45-flight SITL sweep (drag rate 0.1-5 m/s, step offsets, default vs tightened gates, PX4 EKF2_GPS_MODE)](../../catalog/samples/autopilot-spoof-response.md) (uses)
- [Golden demo on PX4 v1.17 SIH: coherent GPS drag via HIL_GPS, integrity monitor (SS + PL, GNSS-vs-VIO velocity), EKF2 switch from GNSS to external vision, comparison with ArduPilot, dashboard replay](../../catalog/samples/golden-demo-px4.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
