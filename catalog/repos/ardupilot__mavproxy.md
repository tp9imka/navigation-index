# MAVProxy

`repo:ardupilot/mavproxy` - <https://github.com/ArduPilot/MAVProxy>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 600 | Python | GPL-3.0 | 2026-11-06 | False | production | high |

Command-line, module-based ground station and MAVLink proxy with map, console and many plugins.

**Why it matters:** Default SITL console for ArduPilot; scriptable modules make it easy to prototype operator-side tools.

**Hackathon notes:** Comes with sim_vehicle.py; write a module to add custom displays or alerts (e.g. GNSS anomaly warnings).

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [ardupilot__mavproxy](../../docs/integration-cards/ardupilot__mavproxy.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md)

**Tags:** `gcs`, `cli`, `modules`, `proxy`

**Domains:** multi

## Related

- depends_on: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- alternative_to: [mavlink-router](../../catalog/repos/mavlink-router__mavlink-router.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) (integrates_with)
- [pymavlink](../../catalog/repos/ardupilot__pymavlink.md) (integrates_with)
- [mavlink-router](../../catalog/repos/mavlink-router__mavlink-router.md) (alternative_to)
- [ArduPilot EKF3 source-set switch under GPS denial](../../catalog/samples/ardupilot-ekf3-source-switch.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
