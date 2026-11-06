# Crazyflie firmware - integration card
<!-- about: repo:bitcraze/crazyflie-firmware -->
Firmware for the Crazyflie 2.x nano quad (and Bolt / 2.1 Brushless / Roadrunner): a small, readable onboard EKF / error-state UKF that fuses IMU with UWB (Loco TWR/TDoA), Lighthouse, optical flow and external mocap pose. The cheapest real indoor GNSS-denied flying testbed, and its estimators can be run on a PC through Python bindings.

| | |
|---|---|
| Install | Latest release tag `2026.08` (2026-08-20). `git clone --recursive https://github.com/bitcraze/crazyflie-firmware.git` (no spaces in the path). Ubuntu: `sudo apt-get install make gcc-arm-none-eabi`; macOS: `brew install gcc-arm-embedded coreutils gnu-sed`; Windows: WSL. Then `make cf2_defconfig` (or `cf21bl_defconfig`, `bolt_defconfig`), `make -j$(nproc)`, flash over radio with `make cload` (needs `cfclient`/cflib and a Crazyradio). Alternatives: pixi, nix, toolbelt (`tb make`) per `docs/building-and-flashing/`. Host tools: `pip install cflib` (PyPI 0.1.34, Python >=3.10), `pip install cfclient` (PyPI 2026.8.1, Python >=3.10). |
| Runs on | Target: the Crazyflie 2.x main MCU (the radio MCU has separate firmware). Build host: Linux, macOS, WSL; toolchain policy is gcc-arm-none-eabi 10.3 or newer. Python bindings (`cffirmware`) build on the host with SWIG. |
| Inputs | Onboard IMU and baro; decks: Flow deck v2 (PMW3901 flow + VL53L1x ToF), Loco deck (DW1000 UWB TWR / TDoA2 / TDoA3), Lighthouse deck (SteamVR base stations), mocap marker decks. External position/pose over radio (cflib `cf.extpos.send_extpos(x, y, z)` / `send_extpose(x, y, z, qx, qy, qz, qw)`). Setpoints via CRTP (commander / high-level commander, trajectories). |
| Outputs | Log variables over the radio (`stateEstimate.x/y/z`, `kalman.*`, etc.) through cflib logging; motor PWM. |
| Key API / entry points | Make targets `cf2_defconfig`, `all`, `cload`, `flash` (OpenOCD), `rtt`, `bindings_python`, `test_python`; `make menuconfig` (kbuild) for estimator/controller selection. Estimator selection at runtime by param `stabilizer.estimator` (enum `StateEstimatorType` in `src/modules/interface/estimator/estimator.h`: 0 auto, 1 complementary, then Kalman, UKF, out-of-tree depending on build config). Code: `src/modules/src/estimator/estimator_kalman.c`, `estimator_ukf.c`, `estimator_complementary.c`; `kalman_core.c` (`kalmanCoreUpdateWithFlow()`), `kalman_supervisor.c`. App layer for your own onboard code (`docs/userguides/app_layer.md`, `examples/`). |
| Time to first result | Estimate: 30-45 min to build and flash with apt toolchain and a Crazyradio; 1-2 h for a Flow-deck hover via cflib scripts. Python bindings build: 15 min if SWIG is present. Assumes hardware in hand. |
| License | `LICENSE.txt` is GPL-3.0 (matches GitHub metadata), but README says "licensed under LGPL-3.0". Treat as GPL-3.0 until clarified. cflib is GPLv3 and cfclient GPLv2+ (PyPI metadata). |

## Minimal usage
Not run. From `docs/building-and-flashing/build.md`.

```sh
git clone --recursive https://github.com/bitcraze/crazyflie-firmware.git && cd crazyflie-firmware
make cf2_defconfig
make -j$(nproc)
make cload          # Crazyradio plugged in, Crazyflie in bootloader mode
```

Estimators on a PC (bindings):

```sh
make cf2_defconfig
make test_python                       # needs swig, numpy, pytest, pyyaml, setuptools
PYTHONPATH=build python3 -c "import cffirmware"
```

Feeding an external position (e.g. from a VIO or mocap) with cflib:

```python
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
cflib.crtp.init_drivers()
with SyncCrazyflie("radio://0/80/2M/E7E7E7E7E7", cf=Crazyflie()) as scf:
    scf.cf.param.set_value("stabilizer.estimator", "2")   # Kalman in default builds
    scf.cf.extpos.send_extpos(x, y, z)
```

`send_extpos`/`send_extpose` signatures checked in `cflib/crazyflie/extpos.py`; the URI and estimator value are typical, not verified for your build.

## Wiring it into a nav stack
- ROS 2: [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md) wraps cflib for multi-drone control and pose input.
- Simulation: [crazyflie-simulation](../../catalog/repos/bitcraze__crazyflie-simulation.md) (Webots/Gazebo) and [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md) (CF2X model).
- UWB anchors: [lps-node-firmware](../../catalog/repos/bitcraze__lps-node-firmware.md) for the Loco anchors; TDoA is the multi-drone, anchor-only-transmit mode.
- Any off-board estimator ([OpenVINS](./rpng__open_vins.md), VPR) can close the loop through `extpos`.

## Gotchas
- Estimator auto-switch: the complementary filter is default; mounting a Flow/Loco/Lighthouse deck switches to the EKF (deck `.requiredEstimator`). The UKF is experimental and must be enabled in kbuild.
- Flow deck needs texture and light: closed issue #617 (Kalman diverges over a dark floor). Issue #1292 (closed): EKF quaternion unstable when yaw exceeds +-90 deg. Open issue #1375: hybrid TDoA broken.
- Kalman supervisor resets the state when values go out of bounds (`kalman_supervisor.c`), which looks like position jumps in logs.
- Licence ambiguity (README LGPL vs LICENSE GPL) matters if you plan closed onboard apps.
- Crazyflie 1.0 is unsupported after tag 2017.06.

## Alternatives
- [PX4](./px4__px4-autopilot.md) / [ArduPilot](./ardupilot__ardupilot.md) - full-size airframes, GNSS, MAVLink tooling; heavier.
- [RotorPy](./spencerfolk__rotorpy.md) or [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md) - no hardware, Python-only estimation experiments.

Sources: `README.md`, `LICENSE.txt`, `docs/building-and-flashing/build.md`, `docs/functional-areas/` listing, `docs/functional-areas/sensor-to-control/state_estimators.md`, `docs/functional-areas/sensor-to-control/configure_estimator_controller.md`, `src/modules/interface/estimator/estimator.h`, `src/modules/src/estimator/` listing, release 2026.08, issues #617 #1292 #1375 (github.com/bitcraze/crazyflie-firmware); `cflib/crazyflie/extpos.py` (github.com/bitcraze/crazyflie-lib-python); PyPI JSON for `cflib`, `cfclient`.
