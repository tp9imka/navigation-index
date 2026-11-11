# NanoSLAM: Enabling Fully Onboard SLAM for Tiny Robots

`res:niculescu-2023-nanoslam` - paper - <https://arxiv.org/abs/2309.12008>

**By:** Vlad Niculescu - **Year:** 2023 - **Level:** intermediate - **Access:** open

IEEE Internet of Things Journal (doi 10.1109/JIOT.2023.3339254, per arXiv); abstract read. Lightweight end-to-end SLAM on a 44 g nano drone with a GAP9 RISC-V processor at 87.9 mW; mapping accuracy 4.5 cm and under 250 ms end-to-end, per the authors. Mapping and loop closure, not relocalization after loss. Only the submitter's name was confirmed. Code: github.com/ETH-PBL/NanoSLAM (GPL-3.0, checked with gh api).

## Key takeaways

- Onboard SLAM on a Crazyflie-class drone exists; it builds the map a relocalizer would need in an unknown room
- Says nothing about recovery from tracking loss

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `nano-uav`, `slam`, `tof`, `peer-reviewed`

_Indexed by lane(s): relocalization-prior-art_
