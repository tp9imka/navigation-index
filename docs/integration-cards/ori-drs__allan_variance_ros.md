# allan_variance_ros - integration card
<!-- about: repo:ori-drs/allan_variance_ros -->
ROS 1 tool that reads a multi-hour static IMU rosbag directly (no playback), computes Allan deviation per axis, and writes a Kalibr-style `imu.yaml` (noise density and random walk for accel and gyro). This is how you get honest IMU noise numbers for VIO/LIO/EKF configs.

| | |
|---|---|
| Install | Catkin source build only: put the repo in `~/catkin_ws/src/allan_variance_ros`, then `catkin build allan_variance_ros && source devel/setup.bash` (README). Deps from `package.xml`/`CMakeLists.txt`: rosbag, sensor_msgs, yaml-cpp, optional OpenMP; `analysis.py` needs numpy, scipy, matplotlib, pyyaml. A devcontainer (`.devcontainer/`) is provided for non-20.04 hosts. No ROS 2 build upstream; a ROS 2 fork exists at `Autoliv-Research/allan_variance_ros2` (not reviewed). |
| Runs on | README: "designed for Ubuntu 20.04" (ROS Noetic). CPU only. |
| Inputs | A folder of `.bag` files (only the first `.bag` in sorted order is processed: source comment "For now just do one rosbag"). Topic of `sensor_msgs/Imu` set in a config YAML: `imu_topic`, `imu_rate` (Hz), `measure_rate` (Hz to subsample to), `sequence_time` (s). Examples in `config/` (`realsense_d425i.yaml`, `realsense_t265.yaml`, `alphasense.yaml`, `ouster.yaml`, `anymal_b.yaml`, `anymal_c.yaml`, `sim.yaml`). README: record "at least 3 hours" static on a damped surface. |
| Outputs | `allan_variance.csv` in the bag folder (`AllanVarianceComputor.cpp`). `analysis.py` prints VRW/ARW, bias instability and random walk per axis, saves `acceleration.png` and `gyro.png`, and writes `imu.yaml` (`--output`, default `imu.yaml`) with `accelerometer_noise_density`, `accelerometer_random_walk`, `gyroscope_noise_density`, `gyroscope_random_walk` (gyro converted to rad), `rostopic`, `update_rate`. It writes the worst axis value. |
| Key API / entry points | `rosrun allan_variance_ros cookbag.py --input <bag> --output <bag>` (reorder messages by header stamp, recommended), `rosrun allan_variance_ros allan_variance <bag_folder> <config.yaml>`, `rosrun allan_variance_ros analysis.py --data allan_variance.csv [--config cfg.yaml] [--output imu.yaml] [--skip N]`, `rosrun allan_variance_ros imu_simulator <out.bag> config/simulation/imu_simulator.yaml` (synthetic bag from the Kalibr noise model). Launch `launch/record.launch`. |
| Time to first result | Estimate: 3+ hours of recording plus 15 min of build and processing; 20 min end to end with the simulator bag or the provided 3 h RealSense D435i example bag (Google Drive link in README). |
| License | `LICENSE`: BSD-3-Clause (Copyright 2021 Russell Buchanan, University of Oxford). Note `package.xml` says `<license>Proprietary</license>`, which contradicts the LICENSE file; go by LICENSE but be aware for automated licence scans. Example bags on Google Drive have no stated licence. |

## Minimal usage
Not run. From README:

```sh
cd ~/catkin_ws && catkin build allan_variance_ros && source devel/setup.bash
roscore &
rosbag record -O ~/imu_static/imu.bag /camera/imu        # leave static >= 3 h
rosrun allan_variance_ros cookbag.py --input ~/imu_static/imu.bag --output ~/imu_cooked/imu.bag
rosrun allan_variance_ros allan_variance ~/imu_cooked/ config/realsense_d425i.yaml
rosrun allan_variance_ros analysis.py --data ~/imu_cooked/allan_variance.csv \
  --config config/realsense_d425i.yaml          # press space for the next figure
```

## Wiring it into a nav stack
- `imu.yaml` is directly the Kalibr IMU file: feed it to [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) camera-IMU calibration, then to [OpenVINS](./rpng__open_vins.md), VINS-Fusion or [FAST-LIO](./hku-mars__fast_lio.md) noise parameters.
- For a ROS 2 rig, record a ROS 2 bag and convert to ROS 1 (`rosbags-convert`) or use the ROS 2 fork.
- Pure-Python check of the same data: export the CSV of raw rates and run [allantools](./aewallin__allantools.md) `oadev` to cross-check the fit.
- Use the resulting noise densities as process noise in [robot_localization](./cra-ros-pkg__robot_localization.md) or a hand-written ESKF instead of datasheet guesses.

## Gotchas
- Short recordings break `analysis.py` with `ValueError: array must not contain infs or NaNs` (open issue #43); users report trailing zero/NaN rows in the CSV for recordings under ~1 h; trimming them is a workaround, recording longer is the fix.
- Wrong topic => "No IMU messages to process, is your topic right?" (closed #50).
- Processing a very long bag can freeze or get the process killed for memory (open #59); fit quality complaints (#60, #36).
- Only one bag per folder is used; split recordings must be merged first.
- Values in `imu.yaml` are continuous-time densities per Kalibr convention; some filters want discrete-time sigmas (multiply/divide by sqrt(rate)). Many users then inflate them (Kalibr wiki advice), so don't treat them as final tuning.
- Earth rate is not removed; maintainer says it shows up as a constant bias and so barely affects the Allan parameters (closed #32). The tool reports bias instability and random walk, not absolute bias.

## Alternatives
- [allantools](./aewallin__allantools.md) - general Python ADEV library, no ROS, you do the noise-parameter fit yourself.
- [imu_utils](../../catalog/repos/gaowenliang__imu_utils.md) - older ROS 1 tool with the same goal, needs bag playback.
- [kalibr_allan](../../catalog/repos/rpng__kalibr_allan.md) - MATLAB-based Allan fitting for Kalibr from RPNG.

Sources: `README.md`, `LICENSE`, `package.xml`, `CMakeLists.txt`, `config/realsense_d425i.yaml`, `scripts/analysis.py`, `src/allan_variance.cpp`, `src/AllanVarianceComputor.cpp`, repo tree, fork list, issues #32 #36 #43 #50 #59 #60 (github.com/ori-drs/allan_variance_ros).
