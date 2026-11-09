# Nav2 AMCL configuration guide

`res:nav2-amcl-configuration-docs` - doc - <https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/others/configuring_amcl/>

**By:** Nav2 contributors - **Year:** 2024 - **Level:** intro - **Access:** open

Parameter reference for the ROS 2 AMCL node (Jazzy docs, read). Likelihood-field laser model by default. Augmented-MCL random-pose injection is controlled by recovery_alpha_slow and recovery_alpha_fast, both default 0.0 (off); the docs suggest 0.001 and 0.1. Nav2 also has a ReinitializeGlobalLocalization behaviour-tree node that spreads particles over the map for a kidnapped robot.

## Key takeaways

- The standard ground-robot relocalizer ships with kidnap recovery switched off
- Global re-initialization is a behaviour-tree action the integrator must wire in
- The obvious passive baseline for any scan-to-map relocalizer on a drone

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md)

**Tags:** `amcl`, `nav2`, `monte-carlo-localization`, `kidnapped-robot`, `docs`

## Related

- part_of: [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md)

_Indexed by lane(s): loop-57_
