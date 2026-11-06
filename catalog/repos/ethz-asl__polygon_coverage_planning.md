# polygon_coverage_planning

`repo:ethz-asl/polygon_coverage_planning` - <https://github.com/ethz-asl/polygon_coverage_planning>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 670 | C++ | GPL-3.0 | 2023-11-13 | False | research-prototype | medium |

ETH ASL coverage planner for polygons with holes that treats boustrophedon sweep selection as a generalized TSP, aimed at UAV survey.

**Why it matters:** Handles no-fly holes inside a survey area, which simple lawnmower generators do not.

**Hackathon notes:** ROS1 + CGAL; last push 2023. Use as a reference or run offline to produce waypoint lists.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md)

**Tags:** `coverage`, `gtsp`, `uav-survey`, `cgal`

**Domains:** air

## Related

- alternative_to: [Fields2Cover](../../catalog/repos/fields2cover__fields2cover.md)

## Referenced by

- [Fields2Cover](../../catalog/repos/fields2cover__fields2cover.md) (alternative_to)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
