# Secure Safety Filter: Towards Safe Flight Control under Sensor Attacks

`res:tan-2025-secure-safety-filter` - paper - <https://arxiv.org/abs/2505.06845>

**By:** Xiao Tan, Junior Sundar, Renzo Bruzzone, Pio Ong, Willian T. Lunardi, Martin Andreoni, Paulo Tabuada, Aaron D. Ames - **Year:** 2025 - **Level:** advanced - **Access:** open

Peer-reviewed (IEEE/RSJ IROS 2025, doi 10.1109/IROS60139.2025.11247729). Caltech with TII Abu Dhabi. A secure state reconstructor enumerates sensor subsets over a sliding window, keeps every state consistent with at least p-s sensors under bounded noise, and inflates these plausible states into boxes; a robust CBF filter on velocity setpoints keeps all of them inside the safe set. PX4 SITL (X500, Gazebo) and Holybro X500 hardware with two flight controllers, safe set a square keep-in geofence, attacks injected on one EKF output copy. Code at github.com/tiiuae/px4-secure-state-reconstruction (no license file, checked with gh api 2026-11-09).

## Key takeaways

- Closest prior art to the close-area innovation claim C: multirotor, PX4, geofence margin from a fault-tolerant subset-consistency bound
- Deterministic worst case over bounded noise, no probabilistic protection level or integrity risk budget
- Hardware test duplicated one EKF, so sensor independence was not exercised
- No range-sensor barrier, no VIO; TII is a UAE research lab

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `control-barrier-function`, `safety-filter`, `px4`, `geofence`, `sensor-attack`, `peer-reviewed`

## Related

- cites: [Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions](../../catalog/resources/misyats-px4-cbf-icuas2025.md)

_Indexed by lane(s): pl-margin-prior-art_
