# Beluga

`repo:ekumen-os/beluga` - <https://github.com/Ekumen-OS/beluga>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 329 | C++ | Apache-2.0 | 2026-11-06 | False | production | high |

Modern C++17 library of Monte Carlo Localization algorithms with a ROS 2 node that is a drop-in replacement for the Nav2 AMCL package.

**Why it matters:** Map-based particle-filter localization for ground robots operating without GNSS; easier to extend than legacy AMCL.

**Hackathon notes:** Swap beluga_amcl for nav2_amcl in a Nav2 launch file; same parameters. Good base for adding custom sensor models.

**Concepts:** [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `amcl`, `particle-filter`, `mcl`, `nav2`, `c++`

**Domains:** ground

## Related

- alternative_to: [Nav2 (ROS 2 Navigation)](../repos/ros-navigation__navigation2.md)

## Referenced by

- [ROSCon 2024 (Odense) programme and recordings](../resources/roscon-2024.md) (uses)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
