# QGroundControl

`repo:mavlink/qgroundcontrol` - <https://github.com/mavlink/qgroundcontrol>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5,092 | C++ | Apache-2.0 | 2026-11-06 | False | production | high |

Qt/QML cross-platform GCS (desktop, Android, iOS) for PX4 and ArduPilot: setup, mission planning, video and telemetry.

**Why it matters:** Most common open GCS; a base for custom operator UIs, including Remote ID display.

**Hackathon notes:** Use prebuilt binaries for SITL; custom builds take a few hours to set up Qt.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [mavlink__qgroundcontrol](../../docs/integration-cards/mavlink__qgroundcontrol.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Mission planning and routing](../concepts/mission-planning.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `gcs`, `qt`, `qml`, `mission-planning`

**Domains:** air, ground, maritime

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- alternative_to: [Mission Planner](../repos/ardupilot__missionplanner.md)
- alternative_to: [APM Planner 2](../repos/ardupilot__apm_planner.md)

## Referenced by

- [APM Planner 2](../repos/ardupilot__apm_planner.md) (alternative_to)
- [Mission Planner](../repos/ardupilot__missionplanner.md) (alternative_to)
- [MAVLink Camera Manager](../repos/mavlink__mavlink-camera-manager.md) (integrates_with)
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) (integrates_with)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
