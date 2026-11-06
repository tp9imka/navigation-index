# gym-pybullet-drones - integration card
<!-- about: repo:learnsyslab/gym-pybullet-drones -->
One-line: a pip-installable PyBullet quadrotor simulator (Crazyflie models, PID controllers, Gymnasium and PettingZoo envs) for multi-drone control, swarm and planning logic in pure Python, minutes after install.

| | |
|---|---|
| Install | From README: `git clone https://github.com/learnsyslab/gym-pybullet-drones.git && cd gym-pybullet-drones && conda create -n drones python=3.12 && conda activate drones && pip3 install -e .`. Beyond Python 3.10 `pybullet` has no wheel and builds from source: `sudo apt install build-essential` on Ubuntu; on macOS `CFLAGS="-Dfdopen=fdopen" pip install pybullet --no-cache-dir` first. No tagged releases checked; install from `main`. |
| Runs on | README: tested on Intel x64 / Ubuntu 24.04 and Apple Silicon / macOS 26. CPU only. Betaflight SITL example is Ubuntu only. No ROS. |
| Inputs | Per-drone actions as a numpy array `(num_drones, 4)`: motor RPMs for `CtrlAviary`, or other `ActionType`s (`rpm`, `pid`, `vel`, `one_d_rpm`, `one_d_pid`) for RL aviaries. Initial positions `initial_xyzs` (m) and attitudes `initial_rpys` (rad). Physics mode enum `Physics` (`pyb`, `dyn`, `pyb_gnd`, `pyb_drag`, `pyb_dw`, `pyb_gnd_drag_dw`). URDF drone models `cf2x`, `cf2p`, `racer`. |
| Outputs | Per-drone 20-element ground-truth state from `_getDroneStateVector`: position (3), quaternion (4), roll/pitch/yaw (3), velocity (3), angular velocity (3), last clipped action (4). Optional per-drone RGB / depth / segmentation images (`ObservationType` `rgb`, `dep`, `all`). `Logger` saves CSVs and plots. Gymnasium tuple `(obs, reward, terminated, truncated, info)`. |
| Key API / entry points | `gym_pybullet_drones.envs.CtrlAviary(drone_model, num_drones, initial_xyzs, initial_rpys, physics, pyb_freq=240, ctrl_freq=240, gui, record, obstacles, ...)`, `HoverAviary`, `MultiHoverAviary`, `VelocityAviary`, `BetaAviary`. Controllers: `gym_pybullet_drones.control.DSLPIDControl(drone_model).computeControlFromState(control_timestep, state, target_pos, target_rpy)`, `MRACControl`, `CTBRControl`. `gym_pybullet_drones.utils.Logger`, `utils.PettingZooWrapper`. Example scripts: `examples/pid.py`, `pid_velocity.py`, `downwash.py`, `learn.py`, `play.py`, `beta.py`. |
| Time to first result | Estimate: 15-30 min to see `examples/pid.py` fly, mostly the pybullet source build. RL training (`learn.py`) takes longer; duration not stated in the README. |
| License | MIT |

## Minimal usage

Adapted from `gym_pybullet_drones/examples/pid.py`. Not run.

```python
import numpy as np
from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.utils.enums import DroneModel, Physics

env = CtrlAviary(drone_model=DroneModel.CF2X, num_drones=1,
                 initial_xyzs=np.array([[0, 0, 0.1]]), physics=Physics.PYB, gui=False)
ctrl = DSLPIDControl(drone_model=DroneModel.CF2X)
action = np.zeros((1, 4))
for i in range(5 * env.CTRL_FREQ):
    obs, reward, terminated, truncated, info = env.step(action)
    action[0, :], _, _ = ctrl.computeControlFromState(
        control_timestep=env.CTRL_TIMESTEP, state=obs[0],
        target_pos=np.array([1.0, 0.0, 1.0]), target_rpy=np.zeros(3))
print(obs[0][0:3])  # true position, metres
env.close()
```

## Wiring it into a nav stack

- No sensor models: the state is ground truth. To test a navigation filter, derive IMU / GNSS from the truth yourself (differentiate velocity, add bias and noise, drop GNSS during an outage window) and run your estimator in the loop, e.g. the stdlib [GNSS/INS outage sample](../../samples/gnss-ins-ekf-outage/) or [filterpy](./rlabbe__filterpy.md). Then feed the estimate, not the truth, into `computeControlFromState` to see control degrade under GNSS loss. That closed loop is the useful hackathon demo here.
- Positions are in a local Cartesian frame in metres; convert to lat/lon with [pymap3d](./geospace-code__pymap3d.md) (`enu2geodetic`) for map display in [CesiumJS](./cesiumgs__cesium.md) or [MapLibre](./maplibre__maplibre-gl-js.md), or for a TAK feed via the [MAVLink to TAK sample](../../samples/mavlink-to-tak-cot/) pattern.
- Betaflight SITL (`BetaAviary`, `beta.py`) is the only autopilot-in-the-loop path. For PX4/ArduPilot EKFs under GPS denial use [gz-sim](./gazebosim__gz-sim.md) instead.
- Multi-agent: `PettingZooWrapper(MultiHoverAviary(num_drones=3))` gives one agent per drone for MARL libraries.

## Gotchas

- Ground truth only. Sensor noise is an open request (issue #110 "How to simulate the sensor noise?", #259 depth noise, #71 custom distance sensors). Budget time to write your own sensor layer.
- `pybullet` source build on Python > 3.10 is the main install pain; on macOS the `CFLAGS="-Dfdopen=fdopen"` workaround is required per README.
- Attitude in the observation is roll/pitch/yaw plus quaternion; the README TODO notes plans to move to quaternions and body rates, so indexes into the 20-vector may change. Read `_getDroneStateVector` in the version you install.
- `pyb_freq` must be a multiple of `ctrl_freq`; defaults are 240 Hz each.
- The `main` branch is a refactor; the IROS 2021 code lives on `paper` / `master` branches (README note). Older tutorials target those.
- Models are Crazyflie-scale (cf2x / cf2p) plus one racer. Larger airframes need your own URDF and parameters.
- Sim-to-real for Betaflight is an open question (issue #218).

## Alternatives

- [spencerfolk/rotorpy](../../catalog/repos/spencerfolk__rotorpy.md): Python multirotor sim with aerodynamics and an IMU model, closer to what a nav-filter test needs.
- [ntnu-arl/aerial_gym_simulator](../../catalog/repos/ntnu-arl__aerial_gym_simulator.md): GPU-parallel (Isaac Gym) for large-scale RL with depth sensors; needs an NVIDIA GPU.
- [gazebosim/gz-sim](./gazebosim__gz-sim.md) with PX4/ArduPilot SITL when the autopilot's own estimator is part of the experiment.

Sources: `gh api repos/learnsyslab/gym-pybullet-drones/readme`; `gym_pybullet_drones/envs` listing and `BaseAviary.py` (constructor, `_getDroneStateVector`); `utils/enums.py`; `control` listing; `examples/pid.py`; issue search for sensor / noise / gps. Catalog: [record](../../catalog/repos/learnsyslab__gym-pybullet-drones.md).
