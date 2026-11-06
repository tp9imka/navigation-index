# x-io Fusion - integration card
<!-- about: repo:xiotechnologies/fusion -->
One-line: a small, dependency-free C AHRS (gyro + accel [+ mag or external heading] => quaternion) with a matching Python package, so the attitude you prototype on a laptop is the attitude your MCU computes.

| | |
|---|---|
| Install | Python: `pip install imufusion==1.3.3` (latest on PyPI as of 2026-11-06). C: copy the `Fusion/` folder into your firmware tree or `add_subdirectory(Fusion)` (it ships a `CMakeLists.txt`). Latest tag `v1.3.3`. |
| Runs on | Anything with a C compiler, including MCUs without an FPU (fast inverse square root is on by default). Python wheels per PyPI; no ROS. |
| Inputs | Gyroscope in deg/s, accelerometer in g, magnetometer in any consistent unit (only direction is used), all as 3-vectors in the sensor frame. Optional external heading in degrees (`UpdateExternalHeading`, e.g. GNSS course). Sample rate in Hz, or measured period per sample via `FusionAhrsSetSamplePeriod`. |
| Outputs | Orientation quaternion (sensor relative to earth), gravity vector (sensor frame), linear acceleration (gravity removed, sensor frame), earth acceleration (earth frame, gravity removed). Earth convention selectable: NWU, ENU or NED. Internal states (accel/mag error in degrees, ignored flags, recovery triggers) and flags (startup, overrange, recovery). |
| Key API / entry points | C: `FusionAhrsInitialise(FusionAhrs*)`, `FusionAhrsSetSettings(FusionAhrs*, const FusionAhrsSettings*)`, `FusionAhrsUpdate(ahrs, gyro, accel, mag)`, `FusionAhrsUpdateNoMagnetometer(ahrs, gyro, accel)`, `FusionAhrsUpdateExternalHeading(ahrs, gyro, accel, heading)`, `FusionAhrsGetQuaternion`, `FusionAhrsGetEarthAcceleration`, `FusionAhrsGetInternalStates`. Gyro bias: `FusionBias*`. Calibration: `FusionModelInertial`, `FusionModelMagnetic`; axis remap: `FusionRemap`. Python: `imufusion.Ahrs`, `imufusion.AhrsSettings(sample_rate=..., convention=..., gain=...)`, `ahrs.update_no_magnetometer(g, a)`, `imufusion.Bias`, `imufusion.quaternion_to_euler(q)`. |
| Time to first result | Estimate: 10-15 min to run `Examples/Python/simple_example.py` on the bundled `sensor_data.csv`, assuming a Python env with numpy and matplotlib. Most extra time goes on getting your own IMU's axes and units right. |
| License | MIT |

## Minimal usage

Adapted from `Examples/Python/simple_example.py` (v1.3.3). Not run.

```python
import numpy as np, imufusion

data = np.genfromtxt("sensor_data.csv", delimiter=",", skip_header=1)  # t, gx gy gz [deg/s], ax ay az [g]
ahrs = imufusion.Ahrs()
ahrs.set_settings(imufusion.AhrsSettings(sample_rate=100, convention=imufusion.CONVENTION_NED))

euler = np.empty((len(data), 3))
for i, row in enumerate(data):
    ahrs.update_no_magnetometer(row[1:4], row[4:7])
    euler[i] = imufusion.quaternion_to_euler(ahrs.get_quaternion())  # roll, pitch, yaw in degrees
print(euler[-1])
```

The advanced example (`Examples/Python/advanced_example.py`) adds `imufusion.Bias` for gyro offset tracking, a magnetometer, per-sample `set_sample_period`, and plots of internal states and flags.

## Wiring it into a nav stack

- Attitude source for a loosely-coupled filter: feed Fusion's quaternion into your own position/velocity EKF (see the stdlib [GNSS/INS outage sample](../../samples/gnss-ins-ekf-outage/) or [filterpy](./rlabbe__filterpy.md)) instead of carrying attitude in the filter. This is a shortcut: it ignores the coupling between attitude and position errors that a full INS such as [KF-GINS](./i2nav-whu__kf-gins.md) models.
- ROS 2: publish `sensor_msgs/Imu` with the quaternion filled in (ENU convention to match REP-103) and let [robot_localization](./cra-ros-pkg__robot_localization.md) fuse it with odometry and GNSS.
- MAVLink: the earth-frame output can drive `ATTITUDE_QUATERNION` for a custom ground display; for feeding an autopilot as an external pose, use a full pose source via the [VIO to MAVLink bridge sample](../../samples/vio-to-mavlink-bridge/), since an AHRS has no position.
- Magnetic and accel error states (`accelerationError`, `magneticError`, ignored flags) are useful as cheap anomaly signals for magnetic disturbance or sustained acceleration.
- Generate test IMU data with [gnss-ins-sim](./aceinna__gnss-ins-sim.md) to check axes and conventions before touching hardware.

## Gotchas

- API changed between 1.2.x and 1.3.x. v1.2.9 Python uses `imufusion.Offset(sample_rate)` and `ahrs.settings = imufusion.Settings(convention, gain, ...)` with positional args; v1.3.x uses `imufusion.Bias`, `imufusion.BiasSettings`, and `ahrs.set_settings(imufusion.AhrsSettings(sample_rate=...))`. Blog posts and older forum answers mostly show the 1.2 API. Pin the version and read the example at the matching tag.
- This is the revised AHRS from chapter 7 of Madgwick's thesis, not the well-known "Madgwick filter". Gains and behaviour are not interchangeable with `madgwickahrs` code.
- Units: gyro must be deg/s, accel in g. Passing rad/s or m/s^2 gives a plausible-looking but wrong attitude.
- Without a magnetometer or external heading, yaw drifts with gyro bias. The most-discussed issues are about yaw (issues #66 "Yaw angle different between devices", #24 "Unstable yaw data") and sustained acceleration (#298, open).
- Startup ramps gain from 10 down over 3 s and disables rejection; ignore the first seconds or call `FusionAhrsSkipStartup` if you initialise from a known attitude.
- Calibration is your job: the library applies misalignment/sensitivity/offset and soft/hard-iron models but does not estimate them.
- Overrange recovery restarts the algorithm when rate exceeds 98% of `gyroscopeRange`; set that to your datasheet value or zero to disable.

## Alternatives

- [mayitzin/ahrs](../../catalog/repos/mayitzin__ahrs.md): pure Python collection of many attitude estimators (Madgwick, Mahony, EKF, ...), better for comparing algorithms, not for firmware.
- [arduino-libraries/madgwickahrs](../../catalog/repos/arduino-libraries__madgwickahrs.md): the classic Madgwick filter for Arduino, simpler but no rejection logic.
- [ccnyroboticslab/imu_tools](../../catalog/repos/ccnyroboticslab__imu_tools.md): ROS nodes (Madgwick, complementary) when you want an attitude topic without writing code.

Sources: `gh api repos/xioTechnologies/Fusion/readme`; `Fusion/FusionAhrs.h` (main); `Examples/Python/simple_example.py`, `advanced_example.py` (main and v1.3.3); `Python/advanced_example.py` at v1.2.9; tags list; PyPI JSON for imufusion; issue search sorted by comments. Catalog: [record](../../catalog/repos/xiotechnologies__fusion.md).
