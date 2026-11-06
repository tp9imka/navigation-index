# Nav2 (ROS 2 Navigation)

`repo:ros-navigation/navigation2` - <https://github.com/ros-navigation/navigation2>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5,011 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

The standard ROS 2 navigation stack: behavior-tree driven navigator, global planners (NavFn, Smac hybrid-A*/lattice, Theta*), local controllers (DWB, MPPI, Regulated Pure Pursuit), costmaps, recovery behaviors and waypoint following, including GPS waypoints via robot_localization.

**Why it matters:** Default autonomy layer for ground robots in ROS 2; the place to plug a GNSS-denied localization source and still get full point-to-point and waypoint missions.

**Hackathon notes:** apt install ros-<distro>-navigation2 plus nav2_bringup gives a Gazebo TurtleBot demo in under an hour. Swap AMCL for your own localization by publishing map->odom TF. Tuning params YAML is the main time sink.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [ros-navigation__navigation2](../../docs/integration-cards/ros-navigation__navigation2.md) (integration-cards)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `nav2`, `ros2`, `costmap`, `mppi`, `smac-planner`, `behavior-tree`

**Domains:** ground

## Related

- extends: [opennav_coverage](../../catalog/repos/open-navigation__opennav_coverage.md)
- depends_on: [BehaviorTree.CPP](../../catalog/repos/behaviortree__behaviortree.cpp.md)
- integrates_with: [Spatio-Temporal Voxel Layer](../../catalog/repos/stevemacenski__spatio_temporal_voxel_layer.md)
- alternative_to: [OMPL - Open Motion Planning Library](../../catalog/repos/ompl__ompl.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [BehaviorTree.CPP](../../catalog/repos/behaviortree__behaviortree.cpp.md) (integrates_with)
- [Beluga](../../catalog/repos/ekumen-os__beluga.md) (alternative_to)
- [MoveIt 2](../../catalog/repos/moveit__moveit2.md) (integrates_with)
- [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) (integrates_with)
- [opennav_coverage](../../catalog/repos/open-navigation__opennav_coverage.md) (extends)
- [PlanSys2](../../catalog/repos/plansys2__ros2_planning_system.md) (integrates_with)
- [Nav2 tutorials](../../catalog/repos/ros-navigation__navigation2_tutorials.md) (extends)
- [Spatio-Temporal Voxel Layer](../../catalog/repos/stevemacenski__spatio_temporal_voxel_layer.md) (integrates_with)
- [The Marathon 2: A Navigation System](../../catalog/resources/macenski-marathon2-nav2.md) (has_code)
- [From the Desks of ROS Maintainers: A Survey of Modern & Capable Mobile Robotics Algorithms in the Robot Operating System 2](../../catalog/resources/macenski-ros2-algorithms-survey.md) (explains)
- [Nav2 Documentation](../../catalog/resources/nav2-docs.md) (explains)
- [Navigating Using GPS Localization (Nav2 tutorial)](../../catalog/resources/nav2-gps-navigation-tutorial.md) (has_code)
- [Nav2 ROSCon Talks (index)](../../catalog/resources/nav2-roscon-talks.md) (explains)
- [Nav2 ROSCon Talks index](../../catalog/resources/nav2-roscon-talks-index.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
