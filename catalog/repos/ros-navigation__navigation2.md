# Nav2 (ROS 2 Navigation)

`repo:ros-navigation/navigation2` - <https://github.com/ros-navigation/navigation2>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5,011 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

The standard ROS 2 navigation stack: behavior-tree driven navigator, global planners (NavFn, Smac hybrid-A*/lattice, Theta*), local controllers (DWB, MPPI, Regulated Pure Pursuit), costmaps, recovery behaviors and waypoint following, including GPS waypoints via robot_localization.

**Why it matters:** Default autonomy layer for ground robots in ROS 2; the place to plug a GNSS-denied localization source and still get full point-to-point and waypoint missions.

**Hackathon notes:** apt install ros-<distro>-navigation2 plus nav2_bringup gives a Gazebo TurtleBot demo in under an hour. Swap AMCL for your own localization by publishing map->odom TF. Tuning params YAML is the main time sink.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../concepts/obstacle-avoidance.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `nav2`, `ros2`, `costmap`, `mppi`, `smac-planner`, `behavior-tree`

**Domains:** ground

## Related

- extends: [opennav_coverage](../repos/open-navigation__opennav_coverage.md)
- depends_on: [BehaviorTree.CPP](../repos/behaviortree__behaviortree.cpp.md)
- integrates_with: [Spatio-Temporal Voxel Layer](../repos/stevemacenski__spatio_temporal_voxel_layer.md)
- alternative_to: [OMPL - Open Motion Planning Library](../repos/ompl__ompl.md)

## Referenced by

- [BehaviorTree.CPP](../repos/behaviortree__behaviortree.cpp.md) (integrates_with)
- [Beluga](../repos/ekumen-os__beluga.md) (alternative_to)
- [MoveIt 2](../repos/moveit__moveit2.md) (integrates_with)
- [Isaac ROS nvblox](../repos/nvidia-isaac-ros__isaac_ros_nvblox.md) (integrates_with)
- [opennav_coverage](../repos/open-navigation__opennav_coverage.md) (extends)
- [PlanSys2](../repos/plansys2__ros2_planning_system.md) (integrates_with)
- [Nav2 tutorials](../repos/ros-navigation__navigation2_tutorials.md) (extends)
- [Spatio-Temporal Voxel Layer](../repos/stevemacenski__spatio_temporal_voxel_layer.md) (integrates_with)
- [The Marathon 2: A Navigation System](../resources/macenski-marathon2-nav2.md) (has_code)
- [From the Desks of ROS Maintainers: A Survey of Modern & Capable Mobile Robotics Algorithms in the Robot Operating System 2](../resources/macenski-ros2-algorithms-survey.md) (explains)
- [Nav2 Documentation](../resources/nav2-docs.md) (explains)
- [Navigating Using GPS Localization (Nav2 tutorial)](../resources/nav2-gps-navigation-tutorial.md) (has_code)
- [Nav2 ROSCon Talks (index)](../resources/nav2-roscon-talks.md) (explains)
- [Nav2 ROSCon Talks index](../resources/nav2-roscon-talks-index.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
