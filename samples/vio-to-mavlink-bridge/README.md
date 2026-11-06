# VIO to MAVLink bridge (ENU/FLU => NED/FRD)

## Goal

Feed an external pose source - a VIO / SLAM estimator, a mocap system, or a CSV log -
into PX4 EKF2 or ArduPilot EKF3 as `VISION_POSITION_ESTIMATE` or `ODOMETRY`, so the
autopilot can hold position with GPS denied. The part everyone gets wrong is the frame
conversion, so that part lives in a small stdlib module with unit tests. The MAVLink
sender is a thin sketch on top.

## Repos used

| Repo | Why |
|---|---|
| `repo:ardupilot/pymavlink` | Encodes and sends the MAVLink messages (`bridge.py` without `--dry-run`). |
| `repo:mavlink/mavlink` | Message definitions: `VISION_POSITION_ESTIMATE` (id 102), `ODOMETRY` (id 331), `MAV_FRAME_*`. |
| `repo:px4/px4-autopilot` | Consumer: EKF2 external vision fusion (`EKF2_EV_CTRL`, `EKF2_HGT_REF`). |
| `repo:ardupilot/ardupilot` | Consumer: EKF3 ExternalNav source (`VISO_TYPE`, `EK3_SRC1_*`). |
| `repo:rpng/open_vins`, `repo:hkust-aerial-robotics/vins-fusion` | Typical VIO producers that publish ENU/FLU poses on ROS topics. |
| `repo:mavlink/mavros`, `repo:thien94/vision_to_mavros` | The ROS-native alternative (MAVROS `vision_pose` plugin does this conversion for you). |

## Files

- `frames.py` - stdlib quaternion math: ENU => NED positions, ENU/FLU => NED/FRD
  orientation, world => body velocity, MAVLink 21-element covariance layout.
- `test_frames.py` - 8 unit tests, including a 200-case randomized check that rotating a
  body vector in ENU then converting equals converting then rotating in NED.
- `bridge.py` - replays a CSV `t,x,y,z,qw,qx,qy,qz` (ENU world, FLU body, quaternion
  w-first). `--dry-run` prints converted fields as JSON lines (stdlib only); otherwise
  sends via pymavlink.
- `example_pose_enu.csv` - 2 s of a 2 m radius circle at 1.5 m altitude, 10 Hz,
  heading tangent to the path, counterclockwise seen from above.

## Prerequisites

- Python 3.10+ (tested on 3.14.7). Unit tests and `--dry-run` need nothing else.
- For sending: `pip install pymavlink` (sketch; tested against no particular version)
  plus a running PX4 or ArduPilot SITL, or a real autopilot.

## Run (stdlib, verified)

```sh
cd samples/vio-to-mavlink-bridge
python3 -m unittest -v test_frames
python3 bridge.py example_pose_enu.csv --dry-run
```

Observed output (python3.14.7, 2026-11-06):

```
Ran 8 tests in 0.002s

OK
```

```
{"time_usec": 0, "frame_id": 20, "child_frame_id": 12, "pos_ned": [0.0, 2.0, -1.5], "q_ned_frd": [1.0, -0.0, -0.0, -0.0], "rpy": [0.0, -0.0, 0.0], "vel_body_frd": [NaN, NaN, NaN]}
{"time_usec": 100000, "frame_id": 20, "child_frame_id": 12, "pos_ned": [0.1, 1.9975, -1.5], "q_ned_frd": [0.9997, -0.0, -0.0, -0.025], "rpy": [0.0, -0.0, -0.05], "vel_body_frd": [1.0, 0.025, 0.0]}
...
{"time_usec": 2000000, "frame_id": 20, "child_frame_id": 12, "pos_ned": [1.6829, 1.0806, -1.5], "q_ned_frd": [0.8776, -0.0, -0.0, -0.4794], "rpy": [0.0, -0.0, -1.0], "vel_body_frd": [0.9998, 0.0247, 0.0]}
```

How to read it: the vehicle starts 2 m east, facing north. In NED that is
`north=0, east=2, down=-1.5`, yaw 0. A counterclockwise ENU circle is a decreasing NED
yaw. Body-frame forward speed is ~1 m/s (radius 2 m x 0.5 rad/s), sideways ~0. The first
row has no previous sample, so velocity is NaN (the JSON line is therefore not strict
JSON).

## Run against SITL (unverified sketch)

The CSV circle is a format demo, not a flyable input: an EKF rejects vision data that
disagrees with what the IMU sees. For a live check, keep the vehicle on the ground and
stream a constant pose, then confirm the EKF fuses it.

```sh
python3 -c "print('t,x,y,z,qw,qx,qy,qz'); [print(f'{i/30:.4f},0,0,0,0.7071068,0,0,0.7071068') for i in range(30)]" > still.csv
```

That pose is "at origin, facing north" in ENU.

PX4 (`make px4_sitl gz_x500`, see `samples/px4-sitl-gps-denial`). In the `pxh>` shell:

```
param set EKF2_EV_CTRL 15
param set EKF2_HGT_REF 3
param set EKF2_GPS_CTRL 0
```

Restart SITL, then:

```sh
python3 bridge.py still.csv --loop --msg odom --frame frd --connect udpout:127.0.0.1:14580
```

In `pxh>`: `listener vehicle_visual_odometry` should show the stream, and
`listener estimator_status_flags` should show `cs_ev_pos: True` once fused.
`EKF2_EV_CTRL` bits are horizontal position, vertical position, velocity, yaw - check
the parameter reference for your PX4 version before relying on 15. Port 14580 is the
PX4 SITL onboard MAVLink port (`ROMFS/px4fmu_common/init.d-posix/px4-rc.mavlink`).

ArduPilot (`sim_vehicle.py -v ArduCopter --console --map`, see
`samples/ardupilot-ekf3-source-switch`). In MAVProxy:

```
param set VISO_TYPE 1
param set EK3_SRC1_POSXY 6
param set EK3_SRC1_VELXY 6
param set EK3_SRC1_POSZ 1
param set EK3_SRC1_VELZ 6
param set EK3_SRC1_YAW 6
reboot
```

```sh
python3 bridge.py still.csv --loop --msg odom --connect tcp:127.0.0.1:5762
```

ArduPilot only accepts `ODOMETRY` with `frame_id=MAV_FRAME_LOCAL_FRD` and
`child_frame_id=MAV_FRAME_BODY_FRD` (`GCS_MAVLINK::handle_odometry` in
`libraries/GCS_MAVLink/GCS_Common.cpp`), which is what `--frame frd` sends. Watch for
the GCS message "EKF3 IMU0 is using external nav data".

## Feeding it from ROS 2 instead of CSV (sketch)

Subscribe to the VIO `nav_msgs/Odometry` topic and call the same converter:

```python
pos_ned, q_ned = frames.convert_pose(
    (p.x, p.y, p.z), (o.w, o.x, o.y, o.z))   # msg.pose.pose.position / .orientation
```

then pass the result to `send()` in `bridge.py`. Check first that the VIO really
publishes ENU/FLU (REP-103). Some estimators publish camera-optical frames
(z forward, x right, y down) and need one more fixed rotation.

## Extending it in a hackathon

- Stream Gazebo ground truth through the bridge with added noise and bias to emulate a
  VIO of known quality, then measure how EKF position error grows with that bias.
- Increment `reset_counter` whenever the VIO relocalizes, so the EKF resets instead of
  fusing a jump.
- Fill `pose_covariance` from the estimator's real covariance instead of the fixed
  `--pos-std` / `--ang-std` defaults.
- Pair with `samples/ardupilot-ekf3-source-switch` to switch from GPS to this source in
  flight.

## Pitfalls

- ROS +pitch is nose down, MAVLink +pitch is nose up. `test_ros_positive_pitch_is_nose_down`
  pins this.
- `MAV_FRAME_LOCAL_NED` claims the VIO world frame is north-aligned. Most VIO world frames
  are gravity-aligned with arbitrary yaw: send `LOCAL_FRD` unless you aligned it.
- `ODOMETRY` velocity is in the child (body) frame, not the world frame. `bridge.py`
  rotates it.
- PX4 docs ask for 30-50 Hz (`docs/en/ros/external_position_estimation.md`). The example
  CSV is 10 Hz because it is only a format demo.
- Set `EKF2_EV_DELAY` (PX4) or `VISO_DELAY_MS` (ArduPilot) to the real pipeline latency;
  the defaults assume a fast source.
- ArduPilot with no GPS has no EKF origin; set one (`SET_GPS_GLOBAL_ORIGIN`, or the
  MAVProxy map "Set Origin") before modes that need a global position.
- Use the autopilot's system id (`--sysid`) so the message is treated as coming from an
  onboard component of that vehicle.
