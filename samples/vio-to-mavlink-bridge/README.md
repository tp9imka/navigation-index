# VIO to MAVLink bridge (ENU/FLU => NED/FRD)

## Goal

Feed an external pose source - a VIO / SLAM estimator, a mocap system, or a CSV log -
into PX4 EKF2 or ArduPilot EKF3 as `VISION_POSITION_ESTIMATE` or `ODOMETRY`, so the
autopilot can hold position with GPS denied. The part everyone gets wrong is the frame
conversion, so that part lives in a small stdlib module with unit tests. The MAVLink
sender is a thin layer on top.

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
  sends via pymavlink. It sets `MAVLINK20=1` before importing pymavlink: `ODOMETRY`
  (id 331) is MAVLink 2 only, and without it pymavlink fails with
  `'MAVLink' object has no attribute 'odometry_send'` (seen on the first SITL run).
- `set_params.py` - set parameters over MAVLink and reboot (pymavlink).
- `watch_ekf.py` - print STATUSTEXT and ArduPilot EKF flags / local position (pymavlink).
- `example_pose_enu.csv` - 2 s of a 2 m radius circle at 1.5 m altitude, 10 Hz,
  heading tangent to the path, counterclockwise seen from above.

## Prerequisites

- Python 3.10+ (tested on 3.14.7). Unit tests and `--dry-run` need nothing else.
- For sending: `pip install pymavlink` (ran with 2.4.50) plus a running PX4 or
  ArduPilot SITL (`samples/sitl-docker`), or a real autopilot.

## Run (stdlib)

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

## Run against SITL (ran 2026-11-06)

The CSV circle is a format demo, not a flyable input: an EKF rejects vision data that
disagrees with what the IMU sees. For a live check, keep the vehicle on the ground and
stream a constant pose, then confirm the EKF fuses it.

```sh
python3 -c "print('t,x,y,z,qw,qx,qy,qz'); [print(f'{i/30:.4f},0,0,0,0.7071068,0,0,0.7071068') for i in range(30)]" > still.csv
```

That pose is "at origin, facing north" in ENU. Both SITLs come from
`samples/sitl-docker`. `set_params.py` and `watch_ekf.py` are small pymavlink helpers in
this folder (no MAVProxy needed).

### ArduPilot (ArduCopter Copter-4.6.3 SITL)

```sh
docker run --rm -d --name ap -p 5760:5760 -p 5762:5762 -p 5763:5763 nav-sitl-ardupilot:copter-4.6.3
python3 set_params.py --connect tcp:127.0.0.1:5762 VISO_TYPE=1 EK3_SRC1_POSXY=6 \
    EK3_SRC1_VELXY=6 EK3_SRC1_POSZ=1 EK3_SRC1_VELZ=6 EK3_SRC1_YAW=6 --reboot
python3 bridge.py still.csv --loop --msg odom --connect tcp:127.0.0.1:5762 &
python3 watch_ekf.py --connect tcp:127.0.0.1:5763 --seconds 30
```

Observed (pymavlink 2.4.50, python3.12):

```
ekf flags=0x00a7 horiz=none CONST_POS_MODE pos_h_var=0.01 local_ned=n/a
STATUSTEXT: EKF3 IMU0 yaw aligned
STATUSTEXT: EKF3 IMU0 is using external nav data
STATUSTEXT: EKF3 IMU0 initial pos NED = 0.0,0.0,-0.0 (m)
STATUSTEXT: EKF3 IMU1 yaw aligned
STATUSTEXT: EKF3 IMU1 is using external nav data
STATUSTEXT: EKF3 IMU1 initial pos NED = 0.0,0.0,-0.0 (m)
ekf flags=0x033f horiz=abs pos_h_var=0.00 local_ned=(0.00, -0.00, 0.01)
ekf flags=0x033f horiz=abs pos_h_var=0.00 local_ned=(-0.00, 0.00, 0.01)
```

Before the bridge starts, the same watcher shows `PreArm: VisOdom: not healthy` and
`CONST_POS_MODE`. ArduPilot only accepts `ODOMETRY` with
`frame_id=MAV_FRAME_LOCAL_FRD` and `child_frame_id=MAV_FRAME_BODY_FRD`
(`GCS_MAVLINK::handle_odometry` in `libraries/GCS_MAVLink/GCS_Common.cpp`), which is what
`--frame frd` sends. The SITL GPS stays on here and sets the EKF origin; with no GPS at
all you must send `SET_GPS_GLOBAL_ORIGIN` first.

### PX4 (v1.17.0, SIH quadrotor)

PX4 SITL only talks MAVLink on localhost, so the bridge runs in a container that shares
the PX4 network namespace (`client` in `samples/sitl-docker/compose.yaml`). Run from the
repo root.

```sh
docker run -d --name px4 nav-sitl-px4:v1.17.0
docker exec px4 sh -c 'cd /px4/rootfs && /px4/bin/px4-param set EKF2_EV_CTRL 15 &&
    /px4/bin/px4-param set EKF2_HGT_REF 3 && /px4/bin/px4-param set EKF2_GPS_CTRL 0'
docker restart px4
docker run -d --name px4client --network container:px4 --entrypoint sleep nav-sitl-client:latest infinity
docker cp samples/vio-to-mavlink-bridge px4client:/vio   # includes still.csv created above
docker exec -d px4client python /vio/bridge.py /vio/still.csv --loop --msg odom --frame frd \
    --connect udpout:127.0.0.1:14580
docker exec px4 sh -c 'cd /px4/rootfs && /px4/bin/px4-listener vehicle_visual_odometry 1 &&
    /px4/bin/px4-listener estimator_status_flags 1'
```

Observed (abridged to the relevant fields):

```
TOPIC: vehicle_visual_odometry
    position: [0.00000, 0.00000, -0.00000]
    q: [1.00000, -0.00000, -0.00000, -0.00000] (Roll: 0.0 deg, Pitch: -0.0 deg, Yaw: 0.0 deg)
    position_variance: [0.00250, 0.00250, 0.00250]
    pose_frame: 2
TOPIC: estimator_status_flags
    cs_tilt_align: True
    cs_ev_pos: True
    cs_ev_yaw: True
    cs_ev_hgt: True
    cs_ev_vel: True
    cs_ev_yaw_fault: False
```

`position_variance` 0.0025 is the default `--pos-std 0.05` squared, and `pose_frame: 2`
is FRD, so the covariance layout and frame id survived the trip. Params persist across
`docker restart` (stored in `/px4/rootfs`), not across `docker rm`. `EKF2_EV_CTRL` bits
are horizontal position, vertical position, velocity, yaw. Port 14580 is the PX4 SITL
onboard MAVLink port (`ROMFS/px4fmu_common/init.d-posix/px4-rc.mavlink`; SITL prints
`mode: Onboard ... on udp port 14580 remote port 14540`).

Not tested: `--msg vpe`, a moving pose, flying on vision, `--frame ned`.

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
