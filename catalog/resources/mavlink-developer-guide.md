# MAVLink Developer Guide

`res:mavlink-developer-guide` - doc - <https://mavlink.io/en/>

**By:** MAVLink project / Dronecode, Dronecode / MAVLink - **Year:** 2025 - **Level:** intro - **Access:** open

Official documentation for the MAVLink micro air vehicle messaging protocol: message definitions, microservices (mission, parameters, camera, FTP), dialects and code generators.

## Key takeaways

- Lightweight binary protocol between autopilots, GCS and companion computers
- Microservices define stateful exchanges like mission upload
- Generators produce bindings for C, Python, Rust and more
- Generated C headers are MIT: safe to link into a closed companion app
- Other language bindings are 'typically MIT'; check each
- The generator (pymavlink tools) is LGPLv3, which does not reach generated output per this page

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Standards and interface specs](../../catalog/concepts/standards.md), [Policy, export control and ethics](../../catalog/concepts/policy-ethics.md)

**Tags:** `mavlink`, `protocol`, `uav`, `dronecode`, `mit`, `lgpl`, `license`

## Related

- has_code: [MAVLink](../../catalog/repos/mavlink__mavlink.md)
- has_code: [MAVSDK](../../catalog/repos/mavlink__mavsdk.md)
- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [ArduPilot License (GPLv3)](../../catalog/resources/ardupilot-gplv3-license-page.md) (cites)
- [MAVLink 2 and Message Signing](../../catalog/resources/mavlink-2-signing.md) (part_of)
- [MAVLink Mission Protocol](../../catalog/resources/mavlink-mission-protocol.md) (part_of)

_Indexed by lane(s): docs-standards, flight-embedded_
