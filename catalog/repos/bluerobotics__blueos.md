# BlueOS

`repo:bluerobotics/blueos` - <https://github.com/bluerobotics/BlueOS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 473 | Vue | NOASSERTION | 2026-11-06 | False | production | high |

Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.

**Why it matters:** Strong base for maritime/underwater vehicle builds; extension system makes adding a nav service easy.

**Hackathon notes:** Most useful with a BlueROV2; extensions are Docker images, so a nav add-on can be packaged quickly.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [bluerobotics__blueos](../../docs/integration-cards/bluerobotics__blueos.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Underwater navigation](../../catalog/concepts/underwater-nav.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `companion`, `docker`, `rov`, `usv`, `extensions`, `bluerov2`, `companion-computer`

**Domains:** maritime, underwater, ground, air

## Related

- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- alternative_to: [Rpanion-server](../../catalog/repos/stephendade__rpanion-server.md)
- depends_on: [MAVLink Camera Manager](../../catalog/repos/mavlink__mavlink-camera-manager.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) (integrates_with)
- [MAVLink Camera Manager](../../catalog/repos/mavlink__mavlink-camera-manager.md) (integrates_with)
- [Rpanion-server](../../catalog/repos/stephendade__rpanion-server.md) (alternative_to)
- [ArduSub documentation](../../catalog/resources/ardusub-docs.md) (explains)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
