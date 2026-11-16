# Fisher Information Field (rpg_information_field)

`repo:uzh-rpg/rpg_information_field` - <https://github.com/uzh-rpg/rpg_information_field>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 212 | C++ | MIT | 2020-10-13 | False | research-prototype | medium |

Implements the Fisher Information Field, a voxel map that stores how well a camera can localise at a given 6-DoF pose against known 3D landmarks. The field is differentiable and fast to query, with RRT* and trajectory-optimisation examples.

**Why it matters:** The clearest open code for a 'localisability map': plan paths that stay where vision-based localisation works, the core idea behind perception-aware planning in GNSS-denied flight.

**Build notes:** License MIT (gh api), with Voxblox-derived code under its own license in third_party. Last push 2020-10-13. ROS 1 build with Unreal-based examples: too heavy for 48h. Re-implement the idea in 2D for aerial nav: a grid where each cell scores expected match quality (texture, terrain roughness) and feed it into the planner cost.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `perception-aware`, `localisability`, `fisher-information`, `voxblox`, `mit`

**Domains:** air

## Related

- same_org: [rpg_mpc (PAMPC)](../../catalog/repos/uzh-rpg__rpg_mpc.md)
- alternative_to: [LA-Planner](../../catalog/repos/robotics-star-lab__la-planner.md)
- alternative_to: [mav_active_3d_planning](../../catalog/repos/ethz-asl__mav_active_3d_planning.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [mav_active_3d_planning](../../catalog/repos/ethz-asl__mav_active_3d_planning.md) (alternative_to)
- [LA-Planner](../../catalog/repos/robotics-star-lab__la-planner.md) (alternative_to)
- [rpg_mpc (PAMPC)](../../catalog/repos/uzh-rpg__rpg_mpc.md) (same_org)
- [Fisher Information Field: an Efficient and Differentiable Map for Perception-aware Planning](../../catalog/resources/zhang-scaramuzza-fisher-information-field-2020.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-16._
