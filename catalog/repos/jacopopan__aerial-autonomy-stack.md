# aerial-autonomy-stack

`repo:jacopopan/aerial-autonomy-stack` - <https://github.com/JacopoPan/aerial-autonomy-stack>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | active-research | low |

Dockerized harness to simulate and deploy PX4, ArduPilot and Betaflight drones with ROS 2, YOLO and lidar odometry (KISS-ICP), with a steppable gymnasium interface and Jetson deployment images.

**Why it matters:** A worked example of a sim-to-Jetson product pipeline: same containers for sim and the aircraft, offboard interfaces for both autopilots.

**Build notes:** MIT. Needs an NVIDIA driver and nvidia-container-toolkit; first build about 45 min per README. Not runnable on the Mac. Read it for architecture ideas, do not plan to run it.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `px4`, `ardupilot`, `ros2`, `docker`, `jetson`, `mit`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- integrates_with: [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md)

_Indexed by lane(s): close-area-sims_
