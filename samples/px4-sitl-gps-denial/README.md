# PX4 SITL GPS denial: inject, measure drift, recover

## Goal

Measure what happens to PX4 EKF2 when GPS disappears mid-mission. A quadcopter in
PX4 SITL (SIH `sihsim_quadx`, headless in Docker; Gazebo `gz_x500` also works per PX4
docs) flies an 80 m square. At the first waypoint the script turns the GPS off (MAVSDK
failure injection, falling back to `SIM_GPS_USED=0`), logs EKF health flags and estimated vs
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
| `repo:gazebosim/gz-sim` | Optional simulator behind `make px4_sitl gz_x500` (not used in the verified run, which uses SIH). |
| `repo:px4/flight_review` | Optional: upload the `.ulg` to inspect `estimator_status_flags` plots. |

PX4 `pyulog` (github.com/PX4/pyulog) reads the `.ulg` in `ulog_drift.py`.

## Files

- `drift.py` - stdlib analyzer. Reads `t,phase,est_lat,est_lon,true_lat,true_lon`
  (extra columns ignored). Missing truth reads "not measured", never a guessed number.
  `--synthetic` builds a dead-reckoning example.
- `test_drift.py` - 4 unit tests.
- `gps_denial_mission.py` - MAVSDK flight script (needs SITL and `mavsdk-grpc`).
- `ulog_drift.py` - converts the PX4 `.ulg` into the same CSV using
  `vehicle_global_position` vs `vehicle_global_position_groundtruth` (needs pyulog).

## Run the stdlib part

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

## Run the SITL flight (ran 2026-11-06)

### 1. Start PX4 SITL (SIH, headless)

```sh
docker build -f samples/sitl-docker/Dockerfile.px4 -t nav-sitl-px4:v1.17.0 samples/sitl-docker
docker build -f samples/sitl-docker/Dockerfile.client -t nav-sitl-client:latest samples/sitl-docker
docker run -d --name px4 nav-sitl-px4:v1.17.0
```

That is PX4 `v1.17.0` with `PX4_SIM_MODEL=sihsim_quadx`: SIH runs the quadrotor physics
inside PX4, so there is no Gazebo and no display. It prints `INFO [init] SIH simulator`
and `Ready for takeoff!` about 10 s after start. Gazebo `gz_x500` (native
`make px4_sitl gz_x500`, or `HEADLESS=1`) is the alternative; not run here.

PX4 SITL only talks MAVLink on localhost (`MAVLink only on localhost (set param
MAV_{i}_BROADCAST = 1 to enable network)`), so the script runs in a client container
that shares the PX4 network namespace:

### 2. Run the mission

```sh
docker run -d --name px4client --network container:px4 --entrypoint sleep nav-sitl-client:latest infinity
docker cp samples/px4-sitl-gps-denial px4client:/sample
docker exec px4client sh -c 'cd /sample && python gps_denial_mission.py --deny-via sim-param --log /tmp/flight_log.csv'
docker exec px4client sh -c 'cd /sample && python drift.py /tmp/flight_log.csv'
```

Or `docker compose up -d px4` and `docker compose run --rm client python
px4-sitl-gps-denial/gps_denial_mission.py --deny-via sim-param` from `samples/sitl-docker`.
Recreate both containers before each flight. A run takes about 2.5 min.

`mavsdk-grpc` 4.0.5 ships `mavsdk_server` inside the wheel; the linux aarch64 build ran
the whole flight here, and the macOS arm64 wheel's binary starts (`--help`) but was not
flown against SITL. The PyPI name `mavsdk` from 4.x on is a different native binding with
a different API; this script needs `mavsdk-grpc` / `import mavsdk_grpc`. To stay on the
old name, `pip install "mavsdk<4"` and change the imports to `mavsdk`.

### How GPS is denied

`MAV_CMD_INJECT_FAILURE` (`drone.failure.inject(SENSOR_GPS, OFF)`) timed out with no ACK on
PX4 v1.17.0 SIH:

```
failure injection not available (TIMEOUT: 'Timeout'; origin: inject(); params: (<FailureUnit.SENSOR_GPS: 4>, <FailureType.OFF: 1>, 0)); using SIM_GPS_USED
```

Reading the v1.17.0 source explains it: commander's `FailureInjector`
(`src/modules/commander/failure_detector/FailureInjector.cpp`) only handles
`FAILURE_UNIT_SYSTEM_MOTOR` and skips everything else without an ACK, and the GPS
failure handling lives in `simulator_mavlink` (the HIL-over-MAVLink simulator path), not
in SIH or `sensor_gps_sim`. PX4 `main` adds a `failure_injection_manager` module that
v1.18.0-rc1 also has; not tried here.

`--deny-via auto` (default) tries failure injection and falls back to
`SIM_GPS_USED=0`; `--deny-via sim-param` goes straight to it. `SIM_GPS_USED` is read by
`sensor_gps_sim`, which reports `fix_type 0` when it is below 4, so EKF2 sees a receiver
with no fix - a sensor-level outage, not an estimator setting.

### Observed

Console (third run, abridged: one row per second, columns `t phase est_lat est_lon
true_lat true_lon global_ok local_ok gps_sats gps_fix`):

```
connected
-- GPS denied via sim-param for 15 s
  44.29 gps-denied 47.398455600 8.545602900 47.398455100 8.545607900 True True 0 NO_GPS
  48.32 gps-denied 47.398465800 8.545733100 47.398462200 8.545746000 True True 0 NO_GPS
  51.33 gps-denied 47.398458000 8.545787900 47.398461400 8.545844900 True True 0 NO_GPS
  52.34 gps-denied 47.398452500 8.545779600 47.398462100 8.545853200 False True 0 NO_GPS
  57.36 gps-denied 47.398409500 8.545683300 47.398469900 8.545872600 False True 0 NO_GPS
-- GPS restored
  59.38 recovery 47.398400400 8.545637100 47.398475200 8.545878400 False True 10 FIX_3D
  60.38 recovery 47.398471500 8.545856800 47.398478800 8.545881600 False True 10 FIX_3D
-- global position OK again, returning to launch
log written to /tmp/flight_log.csv; run: python3 drift.py /tmp/flight_log.csv
```

`drift.py` on the real logs, two runs of the same command (fresh containers each time):

```
run A
pre-denial  samples=200  mean=0.15 m  max=0.90 m
gps-denied  samples=75   mean=3.04 m  max=8.37 m
recovery    samples=482  mean=0.40 m  max=11.80 m
time from GPS loss to >5 m error: 12.7 s

run B
pre-denial  samples=216  mean=0.19 m  max=0.99 m
gps-denied  samples=74   mean=5.68 m  max=17.71 m
recovery    samples=491  mean=0.68 m  max=20.96 m
time from GPS loss to >5 m error: 8.5 s
```

How to read it:

- Truth is real: SIH streams ground truth, so MAVSDK `telemetry.ground_truth()` filled
  `true_lat/true_lon` and `drift.py` measured error instead of printing "not measured".
- `global_ok` went `False` ~8 s into the outage while `local_ok` stayed `True`: EKF2
  keeps a dead-reckoned local estimate after it stops vouching for the global one. The
  truth longitude keeps increasing through the outage, so the vehicle kept moving along
  the east leg. The flight mode was not logged, so whether a position-loss failsafe
  engaged is not recorded.
- The same 15 s outage gave 8.4 m in one run and 17.7 m in the other. The outage starts
  while the vehicle is turning at waypoint 1, and the SIH sensor noise is random, so
  quote a range over several runs, not one number.
- Recovery max is larger than denied max: it is the error in the 1-2 s after GPS comes
  back but before EKF2 resets to it (the `60.38` row shows the jump). It is the outage
  error, measured one sample later.

### Truth from the ULog instead (ulog_drift.py, ran on run B)

```sh
docker exec px4 sh -c 'ls /px4/rootfs/log/*/'          # one .ulg per boot
docker exec px4 cat /px4/rootfs/log/2026-11-06/07_50_25.ulg > px4_sih.ulg
pip install pyulog
python3 ulog_drift.py px4_sih.ulg --deny-from 55.14 --deny-to 69.03 > ulog_drift.csv
python3 drift.py ulog_drift.csv
```

```
pre-denial  samples=6516 mean=0.15 m  max=0.54 m
gps-denied  samples=1737 mean=5.97 m  max=18.30 m
recovery    samples=11515 mean=0.63 m  max=21.24 m
time from GPS loss to >5 m error: 7.8 s
```

That agrees with the MAVSDK log of the same flight (17.71 m) at ~125 Hz instead of 5 Hz.
The denial window came from the `SIM_GPS_USED` changes recorded in the ULog
(`ULog.changed_parameters`, 0 at 55.14 s and 10 at 69.03 s after log start), which is
more reliable than converting the script's own clock. With failure injection the window
would come from the `failure` command time instead. pyulog 1.3.0.

### Same thing by hand from the PX4 shell

SIH on v1.17.0 (ran on a landed vehicle; `px4-<cmd>` is the shell client for each
`pxh>` command):

```sh
docker exec px4 sh -c 'cd /px4/rootfs && /px4/bin/px4-param set SIM_GPS_USED 0'
docker exec px4 sh -c 'cd /px4/rootfs && /px4/bin/px4-listener estimator_status_flags 1'
docker exec px4 sh -c 'cd /px4/rootfs && /px4/bin/px4-param set SIM_GPS_USED 10'
```

Observed 6 s after `SIM_GPS_USED 0`: `cs_inertial_dead_reckoning: True` while
`cs_gnss_pos: True` was still set (the GNSS fusion flag had not timed out yet); 6 s
after restoring, `cs_inertial_dead_reckoning: False`. Watch the dead-reckoning flag, not
only `cs_gnss_pos`.

With a simulator that supports GPS failure injection (per the PX4 failure injection
docs; not run here), in `pxh>`:

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
- On v1.17.0 SIH, GPS failure injection gets no ACK at all (see "How GPS is denied").
  Check the support table in `docs/en/debug/failure_injection.md` and the source for
  your version and simulator before trusting it.
- MAVSDK logs `Received ack for not-existing command: 176! Ignoring...` during the run;
  harmless here (the flight mode changes still happen).
- MAVSDK position telemetry is the EKF estimate, not truth. Without a truth source
  there is no drift number, only the health flags.
- `MissionItem` takes 14 positional arguments in current MAVSDK-Python
  (`examples/mission.py`). Older releases had fewer; match your installed version.
- If the failsafe lands the vehicle before GPS returns, RTL is rejected; the script
  logs that and waits for landing.
- `make px4_sitl gz_x500` failing with `unknown target 'gz_x500'` => `make distclean`
  and retry (from the PX4 Gazebo docs).
