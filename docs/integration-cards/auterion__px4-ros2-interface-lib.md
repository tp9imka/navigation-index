# PX4 ROS 2 Interface Library - integration card
<!-- about: repo:auterion/px4-ros2-interface-lib -->
One-line: C++ (partial Python) library for writing PX4 flight modes and navigation inputs as ROS 2 nodes; its `GlobalPositionMeasurementInterface` is the shortest path from a map-matching lat/lon to PX4's EKF2, and external modes let you define "what to do when GNSS is gone" without forking firmware.

| | |
|---|---|
| Install | Clone into a ROS 2 workspace with a matching `px4_msgs`: `git clone https://github.com/Auterion/px4-ros2-interface-lib src/px4-ros2-interface-lib` (use branch `release/1.17` for PX4 v1.17, `release/1.16`, `release/1.18`, or `main` with PX4 `main`), `git clone https://github.com/PX4/px4_msgs src/px4_msgs` on the matching branch, `colcon build`. Needs the Micro XRCE-DDS Agent running against PX4. |
| Runs on | ROS 2 (Humble/Jazzy per PX4 docs), Linux companion or the SITL host. |
| Inputs | Your node's data: `px4_ros2::GlobalPositionMeasurement` (`timestamp_sample`, optional `lat_lon` Eigen::Vector2d deg, `horizontal_variance`, `altitude_msl`, `vertical_variance`); `px4_ros2::LocalPositionMeasurement` (`position_xy`, `position_z`, `velocity_xy`, `velocity_z`, `attitude_quaternion`, each with a variance); setpoints for modes (goto, rates, attitude, actuators...). |
| Outputs | Publishes `fmu/in/aux_global_position` (global interface) or `fmu/in/vehicle_visual_odometry` (local interface), registers modes/executors with PX4 so they appear in QGC like internal modes. |
| Key API / entry points | `px4_ros2::GlobalPositionMeasurementInterface(node, id=1, GlobalPositionSource::Vision, topic_namespace_prefix="")` + `update(measurement)` (throws `NavigationInterfaceInvalidArgument`) + `doRegister()`; `px4_ros2::LocalPositionMeasurementInterface(node, PoseFrame::LocalNED, VelocityFrame::LocalNED)`; `px4_ros2::ModeBase`, `ModeExecutorBase`; `px4_ros2::messageCompatibilityCheck(node, {...})`, `setSkipMessageCompatibilityCheck()`; `scripts/check-message-compatibility.py -v <px4_msgs> <PX4-Autopilot>`. Examples: `examples/cpp/navigation/{global_navigation,local_navigation}`, `examples/cpp/modes/{goto,goto_global,rtl_replacement,mission,manual,...}`, `examples/python/modes/goto`. |
| Time to first result | Estimate: 2-3 h to build the workspace and see the global_navigation example accepted by PX4 SITL (`listener estimator_aid_src_aux_global_position` or the EKF status flags). Assumes ROS 2 and PX4 SITL already work. |
| License | BSD-3-Clause. |

## Minimal usage
Shape of `examples/cpp/navigation/global_navigation/include/global_navigation.hpp` (main). Not run.

```cpp
class MapFix : public px4_ros2::GlobalPositionMeasurementInterface {
 public:
  explicit MapFix(rclcpp::Node& node) : GlobalPositionMeasurementInterface(node) {
    _timer = node.create_wall_timer(1s, [this] { push(); });
  }
  void push() {
    px4_ros2::GlobalPositionMeasurement m{};
    m.timestamp_sample = _node.get_clock()->now();
    m.lat_lon = Eigen::Vector2d{lat_deg_, lon_deg_};     // from your map matcher
    m.horizontal_variance = sigma_m_ * sigma_m_;
    try { update(m); } catch (const px4_ros2::NavigationInterfaceInvalidArgument& e) { /* log */ }
  }
  ...
};
// in the node: auto iface = std::make_unique<MapFix>(*this); if (!iface->doRegister()) throw ...;
```
Then enable fusion on the PX4 side: `EKF2_AGP_CTRL` bit 0 on v1.17, or `EKF2_AGP0_ID` = the interface id (default 1) and `EKF2_AGP0_CTRL` bit 0 on `main`.

## Wiring it into a nav stack
- Producers: satellite/ortho map-matching ([wildnav](./tiers__wildnav.md), [AnyLoc](./anyloc__anyloc.md), [LightGlue](./cvg__lightglue.md) pipelines), terrain matching ([TERCOM nav](./mzahana__tercom_nav.md)), magnetic map matching ([MagNav.jl](./mit-ai-accelerator__magnav.jl.md)). Pick the `GlobalPositionSource` that matches (Vision, Terrain, Magnetic, ...).
- Local VIO into `LocalPositionMeasurementInterface` replaces hand-filled `VehicleOdometry` messages from [px4_ros_com](./px4__px4_ros_com.md).
- Behaviour: write an executor that switches to your own mode when GNSS health drops, using the `rtl_replacement` example as the template.
- Firmware side: [PX4](./px4__px4-autopilot.md); transport: [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md); messages: [px4_msgs](../../catalog/repos/px4__px4_msgs.md).
- Catalog: [px4-ros2-interface-lib page](../../catalog/repos/auterion__px4-ros2-interface-lib.md).

## Gotchas
- Message sets must match: the lib checks compatibility at mode registration and refuses mismatches. Either use matching `release/x.y` branches on all three (PX4, px4_msgs, this lib) or run the PX4 message translation node and call `setSkipMessageCompatibilityCheck()` (README, experimental).
- The global publisher appends a message-version suffix to the topic name (`fmu/in/aux_global_position` + `getMessageNameVersion<AuxGlobalPosition>()`), so a hand-rolled publisher on the plain topic name may not match what this lib uses.
- Navigation interfaces live under `navigation/experimental/`; APIs may change between release branches.
- Python bindings are incomplete (README); plan on C++ for navigation inputs.
- Open #93 asks how to use it with Vicon (no answer captured here); closed #57 covers local position updates.

## Alternatives
- [px4_ros_com](./px4__px4_ros_com.md): raw uORB topic publishing with frame helpers, no mode registration.
- [MAVROS](./mavlink__mavros.md): MAVLink path, also works for ArduPilot.

Sources: `README.md`, repo tree, `navigation/experimental/{global,local}_position_measurement_interface.hpp`, `src/navigation/experimental/global_position_measurement_interface.cpp`, `examples/cpp/navigation/{global,local}_navigation`, branches API, issue search (#93, #57).
