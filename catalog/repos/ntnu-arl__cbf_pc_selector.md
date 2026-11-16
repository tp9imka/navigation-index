# cbf_pc_selector

`repo:ntnu-arl/cbf_pc_selector` - <https://github.com/ntnu-arl/cbf_pc_selector>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2 | C++ | BSD-3-Clause | 2026-04-24 | False | research-prototype | low |

ROS 2 node that turns depth images, range images or point clouds from one or more sensors into a small set of obstacle points for the composite CBF, by angular binning with a per-bin percentile filter.

**Why it matters:** Defines the obstacle input the NTNU filter was tuned on; a faithful sim baseline should bin its range fan the same way.

**Build notes:** License BSD-3-Clause per gh api, last push 2026-04-24. README read only. For a Python sim, copy the idea (bins_w x bins_h bins, percentile per bin, min/max range) rather than the node.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `point-cloud`, `downsampling`, `control-barrier-function`, `ros2`, `bsd-3`

**Domains:** air

## Related

- integrates_with: [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md)

_Indexed by lane(s): cbf-baselines_

_GitHub metadata fetched 2026-11-16._
