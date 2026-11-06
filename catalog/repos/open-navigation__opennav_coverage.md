# opennav_coverage

`repo:open-navigation/opennav_coverage` - <https://github.com/open-navigation/opennav_coverage>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 320 | C++ | Apache-2.0 | 2026-11-04 | False | active-research | medium |

Nav2-compatible complete-coverage task server and navigator built on Fields2Cover, with behavior-tree utilities for field/area coverage and row following.

**Why it matters:** Gives Nav2 robots area-search and survey patterns (boustrophedon sweeps over a polygon) out of the box, useful for search, mapping and route clearance scenarios.

**Hackathon notes:** Fields2Cover is apt-installable on Humble, Jazzy and Kilted (ros-<distro>-fields2cover 2.x); only the main branch (Lyrical) builds it from source. Send a polygon in GPS or map frame and get a coverage route. Best for flat open terrain.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `coverage`, `nav2`, `fields2cover`, `boustrophedon`

**Domains:** ground

## Related

- extends: [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md)
- depends_on: [Fields2Cover](../../catalog/repos/fields2cover__fields2cover.md)

## Referenced by

- [Fields2Cover](../../catalog/repos/fields2cover__fields2cover.md) (integrates_with)
- [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md) (extends)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
