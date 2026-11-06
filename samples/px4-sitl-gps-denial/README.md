# PX4 SITL GPS denial: inject, measure drift, recover

## Goal

Measure what happens to PX4 EKF2 when GPS disappears mid-mission. A quadcopter in
PX4 SITL (Gazebo `gz_x500`) flies an 80 m square. At the first waypoint the script turns
the GPS off with MAVSDK failure injection, logs EKF health flags and estimated vs
ground-truth position for the outage, turns the GPS back on, and returns home. A stdlib
analyzer turns the log into drift numbers: mean and max horizontal error per phase and
time from GPS loss to 5 m error.

This is the baseline every GPS-denied hackathon project needs: "without our aiding the
vehicle drifts X m in Y s; with it, Z".

## Repos used

| Repo | Why |
|---|---|
| `repo:px4/px4-autopilot` | Firmware, SITL, EKF2, the `failure` module (`docs/en/debug/failure_injection.md`). |
| `repo:mavlink/mavsdk-python` | Python API: mission upload, failure injection, telemetry (published on PyPI as `mavsdk-grpc`). |
| `repo:mavlink/mavsdk` | C++ core; `mavsdk_server` ships inside the Python wheel. |
| `repo:gazebosim/gz-sim` | Simulator behind `make px4_sitl gz_x500`. |
| `repo:px4/flight_review` | Optional: upload the `.ulg` to inspect `estimator_status_flags` plots. |

PX4 `pyulog` (github.com/PX4/pyulog) reads the `.ulg` in `ulog_drift.py`.

## Files

- `drift.py` - stdlib analyzer. Reads `t,phase,est_lat,est_lon,true_lat,true_lon`
  (extra columns ignored). Missing truth reads "not measured", never a guessed number.
  `--synthetic` builds a dead-reckoning example.
- `test_drift.py` - 4 unit tests.
- `gps_denial_mission.py` - MAVSDK flight script (sketch, needs SITL).
- `ulog_drift.py` - converts the PX4 `.ulg` into the same CSV using
  `vehicle_global_position` vs `vehicle_global_position_groundtruth` (sketch, needs pyulog).

## Run the stdlib part (verified)

```sh
cd samples/px4-sitl-gps-denial
python3 -m unittest -v test_drift
python3 drift.py --synthetic
```

Observed output (python3.14.7, 2026-11-06):

```
Ran 4 tests in 0.001s

OK
pre-denial  samples=50   mean=0.00 m  max=0.00 m
gps-denied  samples=100  mean=2.83 m  max=6.89 m
recovery    samples=51   mean=1.41 m  max=6.89 m
time from GPS loss to >5 m error: 16.2 s
```

These numbers come from the synthetic model in `synthetic_csv()` (5 m/s east, 20 s
outage, constant velocity bias plus constant acceleration bias, 2 s recovery time
constant). They are not PX4 results. Recovery max equals the error at the instant GPS
returns, before it decays.

## Run the SITL flight (unverified sketch)

### 1. Start PX4 SITL

Native (Ubuntu, per `docs/en/sim_gazebo_gz/index.md`):

```sh
git clone --recursive https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh        # once, then log out/in
make px4_sitl gz_x500               # HEADLESS=1 make px4_sitl gz_x500 without a GUI
```

Docker (per `docs/en/test_and_ci/docker.md`, image tags follow PX4 releases, e.g.
`px4io/px4-dev:v1.16.0`; check the doc for the image that includes Gazebo for your
version):

```sh
xhost +
docker run -it --privileged --env=LOCAL_USER_ID="$(id -u)" \
  -v ~/src/PX4-Autopilot:/src/PX4-Autopilot/:rw \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e DISPLAY=:0 \
  --network host --name=px4-dev px4io/px4-dev:v1.16.0 bash
# inside the container:
cd /src/PX4-Autopilot && make px4_sitl gz_x500
```

`--network host` matters: the script listens on UDP 14540, where PX4 SITL's offboard
MAVLink instance sends (`ROMFS/px4fmu_common/init.d-posix/px4-rc.mavlink`).

### 2. Run the mission

```sh
pip install mavsdk-grpc
cd samples/px4-sitl-gps-denial
python3 gps_denial_mission.py --denial-s 15 --log flight_log.csv
python3 drift.py flight_log.csv
```

The package was renamed: `mavsdk-grpc` / `import mavsdk_grpc` is the gRPC wrapper this
script uses. The PyPI name `mavsdk` from 4.x on is a different native binding with a
different API. To stay on the old name, `pip install "mavsdk<4"` and change the imports
to `mavsdk`.

Expected (not observed here): the console prints one CSV row per second. In the
`gps-denied` phase `gps_sats` drops to 0 and, after `EKF2_NOAID_TOUT` (a few seconds of
pure inertial dead reckoning), `global_ok` goes `False`. PX4 then enters the position
loss failsafe (for an autonomous multicopter: Return, falling back to Land, then
Descend - `docs/en/config/safety.md`). After `GPS restored` the EKF reacquires and the
script commands RTL.

If `true_lat` stays empty, the simulator is not streaming `HIL_STATE_QUATERNION` and
`drift.py` will say "not measured". Get truth from the flight log instead:

```sh
pip install pyulog
# the log path is printed by PX4 at arming; SITL writes under build/px4_sitl_default/rootfs/log/
python3 ulog_drift.py path/to/log.ulg --deny-from 42 --deny-to 57 > ulog_drift.csv
python3 drift.py ulog_drift.csv
```

`--deny-from` / `--deny-to` are seconds since log start. Read them off the ULog (for
example the `failure` command time in Flight Review's message log) rather than from
`flight_log.csv`, whose clock starts when the script starts.

### Same thing by hand from the PX4 shell

In the `pxh>` console of the running SITL:

```
param set SYS_FAILURE_EN 1
commander takeoff
failure gps off
listener estimator_status_flags     # watch cs_gnss_pos go false
failure gps ok
```

## Extending it in a hackathon

- Make the outage long and the drift numbers your baseline, then add an aiding source
  and rerun: `samples/vio-to-mavlink-bridge` (vision), `make px4_sitl gz_x500_vision`
  (simulated VIO), or optical flow.
- Try `failure gps wrong` (supported on Gazebo per the failure injection table) to test
  spoofing-like behaviour instead of loss.
- Sweep `EKF2_NOAID_TOUT` and `COM_POS_FS_EPH` to see the trade between holding a
  degraded estimate longer and failing safe sooner.
- Feed `flight_log.csv` into a dashboard live: the record task already writes rows at
  5 Hz.

## Pitfalls

- `SYS_FAILURE_EN` must be 1 or `failure` / `MAV_CMD_INJECT_FAILURE` does nothing. The
  script sets it and resets it to 0 at the end.
- PX4 may ACK a failure type the current simulator does not apply. Check the support
  table in `docs/en/debug/failure_injection.md` for your simulator (Gazebo gz,
  SIH, Gazebo Classic differ).
- MAVSDK position telemetry is the EKF estimate, not truth. Without a truth source
  there is no drift number, only the health flags.
- `MissionItem` takes 14 positional arguments in current MAVSDK-Python
  (`examples/mission.py`). Older releases had fewer; match your installed version.
- If the failsafe lands the vehicle before GPS returns, RTL is rejected; the script
  logs that and waits for landing.
- `make px4_sitl gz_x500` failing with `unknown target 'gz_x500'` => `make distclean`
  and retry (from the PX4 Gazebo docs).
