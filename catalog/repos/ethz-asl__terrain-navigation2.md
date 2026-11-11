# terrain-navigation2

`repo:ethz-asl/terrain-navigation2` - <https://github.com/ethz-asl/terrain-navigation2>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 59 | C++ | BSD-3-Clause | 2026-10-02 | False | active-research | medium |

ROS 2 port of ETH's safe low-altitude fixed-wing planner for steep terrain: RRT* in Dubins-airplane space over a DEM, with terrain-clearance and circle-of-safety constraints.

**Why it matters:** The closest open match to fixed-wing terrain-following route planning, and it already consumes a DEM, the same input the hub's TRN samples use.

**Build notes:** License BSD-3-Clause (gh api), commercial-friendly. Last push 2026-10-02. Build and run not attempted here; expect a ROS 2 + grid_map + OMPL workspace. The planner core is the asset: swap its cost for TRN information to get a localisability-aware route.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `fixed-wing`, `dubins-airplane`, `rrt-star`, `terrain`, `ros2`, `bsd-3-clause`

**Domains:** air

## Related

- fork_of: [terrain-navigation (ROS 1)](../../catalog/repos/ethz-asl__terrain-navigation.md)
- depends_on: [OMPL - Open Motion Planning Library](../../catalog/repos/ompl__ompl.md)
- depends_on: [grid_map](../../catalog/repos/anybotics__grid_map.md)
- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [01. Flyable maneuvers that separate competing location hypotheses](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md) (mentions)
- [EDuPlane (Extended Dubins Airplane)](../../catalog/repos/dlr-ft__eduplane.md) (alternative_to)
- [terrain-navigation (ROS 1)](../../catalog/repos/ethz-asl__terrain-navigation.md) (alternative_to)
- [Time-optimal Paths for a Dubins airplane](../../catalog/resources/chitsaz-lavalle-dubins-airplane-2007.md) (has_code)
- [Safe Low-Altitude Navigation in Steep Terrain With Fixed-Wing Aerial Vehicles](../../catalog/resources/lim-terrain-navigation-fixed-wing-2024.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
