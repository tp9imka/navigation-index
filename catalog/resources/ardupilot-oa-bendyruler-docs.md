# Object Avoidance with BendyRuler (ArduPilot Copter docs)

`res:ardupilot-oa-bendyruler-docs` - doc - <https://ardupilot.org/copter/docs/common-oa-bendyruler.html>

**By:** ArduPilot Dev Team - **Year:** 2026 - **Level:** intro - **Access:** open

Docs. ArduPilot's onboard local avoidance for Copter and Rover in Auto, Guided and RTL. It probes candidate bearings up to OA_BR_LOOKAHEAD ahead against an object database fed by proximity sensors and fences, keeping OA_MARGIN_MAX clearance. Type 1 is horizontal only, type 2 also searches up and down.

## Key takeaways

- Works in Guided, so a companion can send goals and let BendyRuler dodge
- Object database ages out obstacles after OA_DB_EXPIRE
- Local method: no guarantee in dead ends

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `ardupilot`, `bendyruler`, `proximity`, `docs`

## Related

- explains: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- part_of: [Object Avoidance with Dijkstra's (ArduPilot Copter docs)](../../catalog/resources/ardupilot-oa-dijkstras-docs.md)

## Referenced by

- [Object Avoidance with Dijkstra's (ArduPilot Copter docs)](../../catalog/resources/ardupilot-oa-dijkstras-docs.md) (part_of)

_Indexed by lane(s): close-area-planning_
