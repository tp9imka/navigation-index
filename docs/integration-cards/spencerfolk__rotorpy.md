# RotorPy - integration card
<!-- about: repo:spencerfolk/rotorpy -->
One-line: pure-Python multirotor simulator with aerodynamic drag, motor dynamics and wind (constant, sinusoid, Dryden), noisy IMU / motion-capture / range / pinhole-camera sensors and a Gymnasium env; the fastest way to generate IMU + ground-truth datasets and test an estimator under wind without a game engine.

| | |
|---|---|
| Install | `pip install rotorpy` (pyproject `version = "3.0.0"`, release v3.0.0 2026-09-07). Extras: `rotorpy[batched]` (torch, torchdiffeq, roma, opt-einsum), `[learning]` (stable_baselines3, tensorboard), `[filter]` (filterpy==1.4.5, for the wind UKF), `[px4]` (pymavlink), `[all]`. Core deps: pyyaml, cvxopt, matplotlib, numpy>=1.24, scipy, pandas, tqdm, gymnasium, timed_count. `requires-python >=3.8`. |
| Runs on | Any OS with Python (pyproject "OS Independent"); CPU. Batched sim optionally on GPU via torch (`device`). No ROS. |
| Inputs | Vehicle param dict (`rotorpy/vehicles/{crazyflie,crazyfliebrushless,hummingbird,px4_sihsim_quadx}_params.py`), controller (`SE3Control`), trajectory (`HoverTraj`, `ThreeDCircularTraj`, `TwoDLissajous`, `MinSnap`, ...), optional wind (`rotorpy/wind/`), world JSON (`rotorpy/worlds/*.json`). Initial state dict `x` [m], `v` [m/s], `q` [x,y,z,w], `w` [rad/s], `wind`, `rotor_speeds` [rad/s]. World frame is ENU (PX4 bridge converts ENU => NED and ENU => geodetic in `px4_multirotor.py`). |
| Outputs | `Environment.run()` returns a dict: `time`, `state`, `control`, `flat`, `imu_measurements` (`accel` m/s^2, `gyro` rad/s, sensor frame), `imu_gt`, `mocap_measurements`, `state_estimate`, `exit`, `camera_measurements`. `Environment.save_to_csv(savepath=None)` (via `unpack_sim_data`) and `save_camera_data(savepath=None, save_pngs=False)` (`environments.py`). Plots and animations (matplotlib). |
| Key API / entry points | `rotorpy.environments.Environment(vehicle, controller, trajectory, wind_profile=None, imu=None, mocap=None, world=None, estimator=None, camera=None, sim_rate=100, safety_margin=0.25)` and `.run(t_final=10, use_mocap=False, terminate=False, plot=False, ...)`; `rotorpy.vehicles.multirotor.Multirotor(quad_params, initial_state=..., ...)`; `rotorpy.sensors.imu.Imu(accelerometer_params=..., gyroscope_params=..., R_BS=np.eye(3), p_BS=np.zeros(3), sampling_rate=500, gravity_vector=np.array([0,0,-9.81]))` with `.measurement(state, acceleration, with_noise=True)`; `rotorpy.sensors.external_mocap.MotionCapture(sampling_rate, mocap_params=..., ...)`; `rotorpy.sensors.range_sensors.TwoDRangeSensor(world, sampling_rate, ...)`; `rotorpy.sensors.camera.PinholeCamera(intrinsics=None, extrinsics=None, ...)`; `rotorpy.estimators.wind_ekf.WindEKF(quad_params, Q=..., R=..., xhat0=..., P0=..., dt=1/100)` with `.step(ground_truth_state, controller_command, imu_measurement, mocap_measurement)`; Gymnasium id `"Quadrotor-v0"` => `rotorpy.learning.quadrotor_environments:QuadrotorEnv(num_envs, initial_states, control_mode='cmd_vel', reward_fn=...)`; `rotorpy.vehicles.px4_multirotor.PX4Multirotor(quad_params, mavlink_url="tcpin:localhost:4560", lockstep=True, ...)`; `rotorpy.vehicles.ardupilot_multirotor.Ardupilot(...)`. |
| Time to first result | Estimate: 10-20 min from `pip install rotorpy` to plots of a Lissajous flight with IMU and mocap traces (README example). Plugging in your own estimator: an afternoon. PX4 SITL bridge: 1-2 h including a PX4 build. Assumes a desktop Python with matplotlib. |
| License | MIT. |

## Minimal usage
Adapted from the README "minimum working example" (`examples/basic_usage.py`); adds Dryden wind and pulls IMU + truth out for an estimator. Not run.

```python
import numpy as np
from rotorpy.environments import Environment
from rotorpy.vehicles.multirotor import Multirotor
from rotorpy.vehicles.crazyflie_params import quad_params
from rotorpy.controllers.quadrotor_control import SE3Control
from rotorpy.trajectories.lissajous_traj import TwoDLissajous
from rotorpy.wind.dryden_winds import DrydenGust
from rotorpy.sensors.imu import Imu

env = Environment(vehicle=Multirotor(quad_params), controller=SE3Control(quad_params),
                  trajectory=TwoDLissajous(), wind_profile=DrydenGust(dt=1/100, sig_wind=np.array([1, 1, 0.5])),
                  imu=Imu(sampling_rate=100), sim_rate=100)
env.vehicle.initial_state = {'x': np.zeros(3), 'v': np.zeros(3), 'q': np.array([0, 0, 0, 1]),
                             'w': np.zeros(3), 'wind': np.zeros(3),
                             'rotor_speeds': np.array([1788.53] * 4)}
res = env.run(t_final=20, plot=False, animate_bool=False)
t, truth, imu = res['time'], res['state'], res['imu_measurements']
print(t.shape, truth['x'].shape, imu['accel'].shape)
```
`Imu(... sampling_rate=500)` default and `DrydenGust(dt, avg_wind, sig_wind, altitude)` signatures are from `rotorpy/sensors/imu.py` and `rotorpy/wind/dryden_winds.py`. Keep the IMU `sampling_rate` equal to `sim_rate` unless you have checked how `simulate.py` handles a mismatch (not checked here).

## Wiring it into a nav stack
- Estimator test bench: `imu_measurements` + `mocap_measurements` (treat mocap as a GNSS/VIO stand-in with its own noise, and drop it for a "GNSS-denied" window) => your filter ([FilterPy](./rlabbe__filterpy.md), [KF-GINS](./i2nav-whu__kf-gins.md)-style INS, [GTSAM](./borglab__gtsam.md) preintegration) => compare with `state` truth; score with [evo](./michaelgrupp__evo.md) after writing TUM lines. The built-in `estimator=` slot (template `rotorpy/estimators/nullestimator.py`) gets ground truth, controller command, IMU and mocap every step.
- No GNSS sensor model in `rotorpy/sensors/` (imu, mocap, range, camera only); add your own GNSS/baro noise model on top of `state['x']` or use [gnss-ins-sim](./aceinna__gnss-ins-sim.md) for position-level GNSS errors.
- Vision: v3.0 `PinholeCamera` projects world features (points, colours, optional descriptors) to an image, enough to prototype feature-based VO or visual servoing; not photorealistic, so not a substitute for [Gazebo](./gazebosim__gz-sim.md) when testing real image matchers.
- Autopilot in the loop: `PX4Multirotor` sends `HIL_SENSOR` and `HIL_STATE_QUATERNION` to PX4 SITL and reads `HIL_ACTUATOR_CONTROLS` (`px4_multirotor.py`; `examples/basic_usage_px4.py` says start `PX4_SIMULATOR=none PX4_SIM_MODEL=quadx make px4_sitl sihsim_quadx` first). No `HIL_GPS` send was found in that file. ArduPilot SITL bridge in `ardupilot_multirotor.py` and `examples/ardupilot_*`. See [PX4](./px4__px4-autopilot.md), sample [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/).
- Concept page: [simulation](../../catalog/concepts/simulation.md).

## Gotchas
- Built-in estimators (`WindEKF`, `WindUKF`) estimate the wind vector near hover, not the full navigation state; README in `rotorpy/estimators/` says they use small-angle approximations and parasitic drag only.
- `rotorpy/wind/dryden_winds.py` defines `DrydenGustLP` twice (numpy then torch version); the second definition shadows the first at import, so `from rotorpy.wind.dryden_winds import DrydenGustLP` gives the torch one. Use `DrydenGust` for the numpy path.
- Dryden wind needs torch even on the numpy path: `rotorpy/wind/dryden_utils.py` does an unconditional `import torch`, and `dryden_winds.py` builds `torch.tensor` default arguments at import. With plain `pip install rotorpy` the Minimal usage import of `DrydenGust` should fail (read from source, not run); install `rotorpy[batched]` or torch, or use `rotorpy.wind.default_winds` (constant/sinusoid) instead. The Gymnasium `QuadrotorEnv` also uses torch (`device=torch.device('cpu')` default).
- IMU docstring labels gyro output as "rad/s^2"; the code returns body rate (`w_WB`) plus bias/noise, so the unit is rad/s.
- `PX4Multirotor.__init__` blocks on `wait_heartbeat()`; start PX4 SITL first. PX4 interface docs are an open issue (#33).
- Past issues: `PyQt6 needed for Python3.12` (#12, animation backend), `No module named 'rotorpy.utils.flatness'` (#14), gymnasium example failures (#11); all closed.
- v3.0 changed trajectory classes (independent yaw) and the env signature (camera); older tutorials may target v2.x.

## Alternatives
- [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md) - PyBullet physics with collisions and multi-drone RL; Crazyflie-centric.
- [Pegasus Simulator](../../catalog/repos/pegasussimulator__pegasussimulator.md) or [Aerial Gym](../../catalog/repos/ntnu-arl__aerial_gym_simulator.md) - photorealistic or GPU-parallel Isaac-based sims when you need real camera images; much heavier install.
- [Gazebo](./gazebosim__gz-sim.md) with PX4/ArduPilot SITL - full autopilot stack and sensor plugins; use when the deliverable is a flying SITL demo rather than an estimator study.

Sources: `gh api repos/spencerfolk/rotorpy` (MIT, pushed 2026-09-07), releases (v3.0.0 notes), README.md, pyproject.toml, repo tree, rotorpy/environments.py, rotorpy/simulate.py, rotorpy/vehicles/{multirotor.py, px4_multirotor.py, ardupilot_multirotor.py}, rotorpy/sensors/{imu.py, external_mocap.py, range_sensors.py, camera.py}, rotorpy/estimators/{wind_ekf.py, README.md}, rotorpy/wind/dryden_winds.py, rotorpy/controllers/quadrotor_control.py, rotorpy/learning/{__init__.py, quadrotor_environments.py}, examples/basic_usage_px4.py, issue search (#11, #12, #14, #33).
