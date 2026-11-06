# BlueOS

`repo:bluerobotics/blueos` - <https://github.com/bluerobotics/BlueOS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 473 | Vue | NOASSERTION | 2026-11-06 | False | production | high |

Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.

**Why it matters:** Strong base for maritime/underwater vehicle builds; extension system makes adding a nav service easy.

**Hackathon notes:** Most useful with a BlueROV2; extensions are Docker images, so a nav add-on can be packaged quickly.

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Underwater navigation](../concepts/underwater-nav.md), [Maritime navigation](../concepts/maritime-nav.md), [Autopilots and flight control](../concepts/autopilot.md)

**Tags:** `companion`, `docker`, `rov`, `usv`, `extensions`, `bluerov2`, `companion-computer`

**Domains:** maritime, underwater, ground, air

## Related

- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- alternative_to: [Rpanion-server](../repos/stephendade__rpanion-server.md)
- depends_on: [MAVLink Camera Manager](../repos/mavlink__mavlink-camera-manager.md)

## Referenced by

- [ArduPilot](../repos/ardupilot__ardupilot.md) (integrates_with)
- [MAVLink Camera Manager](../repos/mavlink__mavlink-camera-manager.md) (integrates_with)
- [Rpanion-server](../repos/stephendade__rpanion-server.md) (alternative_to)
- [ArduSub documentation](../resources/ardusub-docs.md) (explains)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
