# Object Avoidance with Dijkstra's (ArduPilot Copter docs)

`res:ardupilot-oa-dijkstras-docs` - doc - <https://ardupilot.org/copter/docs/common-oa-dijkstras.html>

**By:** ArduPilot Dev Team - **Year:** 2026 - **Level:** intro - **Access:** open

Docs. Onboard global path planning around polygon fences and stay-out zones in Auto, Guided (with GUID_OPTIONS bit 6) and RTL. It does not use proximity-sensor obstacles; a separate mode combines it with BendyRuler for that.

## Key takeaways

- Known static obstacles can be entered as stay-out polygons and avoided with zero companion code
- No sensed-obstacle avoidance on its own
- Spline waypoints are not supported

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `ardupilot`, `dijkstra`, `fence`, `docs`

## Related

- explains: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- part_of: [Object Avoidance with BendyRuler (ArduPilot Copter docs)](../../catalog/resources/ardupilot-oa-bendyruler-docs.md)

## Referenced by

- [Object Avoidance with BendyRuler (ArduPilot Copter docs)](../../catalog/resources/ardupilot-oa-bendyruler-docs.md) (part_of)

_Indexed by lane(s): close-area-planning_
