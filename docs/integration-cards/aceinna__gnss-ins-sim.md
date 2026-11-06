# gnss-ins-sim - integration card
<!-- about: repo:aceinna/gnss-ins-sim -->
One-line: pure-Python generator of reference trajectories plus noisy IMU, GNSS, magnetometer and odometer data from a CSV motion profile, with per-segment GNSS visibility so you can script outages and test your filter against truth.

| | |
|---|---|
| Install | Not on PyPI (pypi.org/pypi/gnss-ins-sim returns 404). `git clone https://github.com/Aceinna/gnss-ins-sim && cd gnss-ins-sim && pip install -e .` (`setup.py`: name `gnss-ins-sim`, version 2.1, requires `numpy>1.10`, `matplotlib`). Or just run demos from the repo root. |
| Runs on | Any OS with Python 3 + numpy/matplotlib. The Aceinna DMU380 INS demo (`demo_aceinna_ins.py`) loads prebuilt Windows `.dll`s (x86/x64) from `demo_algorithms/dmu380_sim_lib`; `demo_algorithms/aceinna_ins.py` raises `OSError('Only support windows.')` on any other OS. The README's `demo_aceinna_vg.py` is not in the repo. |
| Inputs | Motion profile CSV: first row initial lat (deg), lon (deg), alt (m), body velocity (m/s), yaw/pitch/roll (deg); then command rows `type, yaw, pitch, roll, vx, vy, vz, duration, GPS visibility` (5 command types). IMU error model: built-in `'low-accuracy'`, `'mid-accuracy'`, `'high-accuracy'` or a dict (gyro bias deg/h, ARW deg/rt-h, bias instability, correlation s; accel bias m/s^2, VRW m/s/rt-h, ...). Optional vibration model. Or logged data via `demo_gen_data_from_files.py`. |
| Outputs | Named data sets: `ref_pos` (LLA rad,rad,m for `ref_frame=0` NED), `ref_vel`, `ref_att_euler`, `ref_gyro`, `ref_accel`, `gyro`, `accel`, `mag`, `gps`, `gps_visibility`, `time`, `gps_time`; algorithm outputs `pos`, `vel`, `att_euler`, `wb`, `ab`. Saved as CSV under the results dir, plus summary and plots; KML only with `gen_kml=True`. |
| Key API / entry points | `gnss_ins_sim.sim.imu_model.IMU(accuracy=..., axis=6|9, gps=True|False)`; `gnss_ins_sim.sim.ins_sim.Sim([fs, fs_gps, fs_mag], motion_csv, ref_frame=0|1, imu=imu, mode=None, env=None, algorithm=algo)`; `sim.run(n)`; `sim.results(data_dir=None, err_stats_start=0, gen_kml=False, extra_opt='')`; `sim.plot([...], opt={...})`. Algorithm plug-in contract: class with `input` and `output` lists of the names above, `run(set_of_input)`, `get_results()`, `reset()`. |
| Time to first result | Estimate: 10 min for `demo_no_algo.py` (generate data + plots). 1-3 h to wrap your own filter as an algorithm object and get error plots. Assumes Python 3 with numpy/matplotlib already installed. |
| License | MIT. |

## Minimal usage
From `demo_no_algo.py` (run from the repo root so relative paths resolve). Not run.

```python
import os
from gnss_ins_sim.sim import imu_model, ins_sim

imu = imu_model.IMU(accuracy='mid-accuracy', axis=9, gps=True)
sim = ins_sim.Sim([100.0, 10.0, 100.0],                    # fs_imu, fs_gps, fs_mag
                  os.path.abspath('demo_motion_def_files/motion_def-3d.csv'),
                  ref_frame=1, imu=imu, mode=None, env=None, algorithm=None)
sim.run(1)
sim.results('')                                            # writes CSVs + summary
sim.plot(['ref_pos', 'gyro', 'gps_visibility'], opt={'ref_pos': '3d'})
```

Outage scenario: set the last column (GPS visibility) to 0 on the command rows that should be denied; the generated `gps_visibility` series tells your algorithm when GNSS is absent.

## Wiring it into a nav stack
- Feed the CSVs to [KF-GINS](./i2nav-whu__kf-gins.md) (convert rates to increments, rad to deg), to a [GTSAM](./borglab__gtsam.md) ImuFactor graph, or to a [FilterPy](./rlabbe__filterpy.md) EKF wrapped as a gnss-ins-sim algorithm so the tool computes errors against `ref_*` for you.
- Monte Carlo: `sim.run(100)` repeats with fresh noise, useful for NEES/consistency checks.
- Stdlib alternative with outage + spoofing walk-off already built: [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage).
- For receiver-level (RF/IQ) testing rather than PVT-level, use [gps-sdr-sim](./osqzss__gps-sdr-sim.md) file output into [GNSS-SDR](./gnss-sdr__gnss-sdr.md).
- Catalog: [gnss-ins-sim page](../../catalog/repos/aceinna__gnss-ins-sim.md).

## Gotchas
- `demo_ins_loose.py` prints "Still under development. Please try demo_aceinna_ins.py." and its `__main__` does not run the test; its `sim.results(end_point=True)` call also does not match the current `results()` signature. The loosely coupled demo is not a working filter. Write your own algorithm.
- The README's `Sim(...)` example puts the positional `imu` after keyword args (a syntax error as written); use the demo files' call form.
- `ref_frame=1` (virtual inertial frame) adds ECEF initial position to a relative position, which the README itself flags as mixing frames; use `ref_frame=0` (NED/LLA) for GNSS/INS work.
- Positions in `ref_pos` / `pos` are radians for lat/lon, not degrees.
- Closed issues worth reading: #24 (`demo_no_algo.py` NotImplementedError out of the box), #52 (sign of g), #19 (bias drift std), #8 (GPS error model dict modified in place).
- Last push 2024-11; treat it as stable but unmaintained.

## Alternatives
- [pyins](../../catalog/repos/nmayorov__pyins.md): Python INS library with its own simulation and filters, more current.
- [NaveGo](../../catalog/repos/rodralez__navego.md): MATLAB with IMU/GNSS simulation and integration in one place.
- Simulator sensors in [Gazebo gz-sim](./gazebosim__gz-sim.md) or [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md) when the trajectory must come from a closed-loop vehicle.

Sources: `README.md`, `setup.py`, `demo_no_algo.py`, `demo_ins_loose.py`, repo and `demo_algorithms/dmu380_sim_lib` listings, PyPI JSON (404), issue search (sorted by comments).
