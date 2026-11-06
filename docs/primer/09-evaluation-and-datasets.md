# 9. Evaluation and datasets

After this chapter you can pick a dataset or simulator that matches your scenario, compute
the trajectory metrics judges and reviewers expect, and design a GNSS-outage or
interference test that shows what your system does when it matters.

Prev: [Maritime, underwater and ground](08-maritime-underwater-ground.md) | [Primer index](README.md)

## Metrics

- **ATE / APE (absolute trajectory/pose error)** - align estimate to ground truth, then RMSE
  of position differences. Measures global consistency.
- **RPE (relative pose error)** - error over fixed sub-trajectory lengths. Measures drift
  rate independent of where it started.
- **Alignment matters.** VIO without absolute fixes is only defined up to a rigid transform
  (and scale for monocular); align with SE(3) or Sim(3) and say which you used. Systems that
  claim absolute position (GNSS, map matching) should be scored **without** alignment.
- **Drift under outage** - error as a function of time or distance since GNSS was lost. This
  is the number a resilient-PNT pitch needs.
- **Integrity metrics** - for a detector: detection rate, false-alarm rate, time to alarm.
  For a navigator: how often the true error exceeded the reported uncertainty (consistency).
- **Tracking metrics** for SA and C-UAS: OSPA and SIAP in Stone Soup
  ([Stone Soup docs](../../catalog/resources/stone-soup-docs.md)).

[evo](../../catalog/repos/michaelgrupp__evo.md) computes APE/RPE with alignment flags and
reads most dataset formats directly.

## Datasets by scenario

| Scenario | Datasets in the index |
|----------|------------------------|
| First VIO sanity check | [EuRoC MAV](../../catalog/resources/ethz-euroc-mav-dataset.md) (small, stereo + IMU) |
| Long-term VIO drift | [TUM VI](../../catalog/resources/tum-vi-benchmark.md) |
| Aggressive drone flight | [UZH-FPV](../../catalog/resources/uzh-fpv-drone-racing-dataset.md) |
| Driving, LiDAR/stereo odometry | [KITTI odometry](../../catalog/resources/kitti-odometry-benchmark.md), [KITTI-360](../../catalog/resources/kitti-360-dataset.md) |
| Urban GNSS degradation | [UrbanLoco](../../catalog/resources/polyu-urbanloco-dataset.md), [UrbanNav](../../catalog/repos/ipnl-polyu__urbannavdataset.md), [Complex Urban](../../catalog/resources/kaist-complex-urban-dataset.md) |
| Aerial LiDAR-visual-inertial-GNSS (incl. raw GNSS) | [MARS-LVIG](../../catalog/resources/hku-mars-lvig-dataset.md) |
| Smartphone GNSS | [GSDC 2023](../../catalog/resources/google-gsdc-2023.md), [GSDC 2022](../../catalog/resources/google-gsdc-2022.md) |
| GNSS spoofing (IQ) | [TEXBAT](../../catalog/resources/ut-texbat.md) |
| GNSS interference maps | [GPSJam](../../catalog/resources/gpsjam-org.md), [Flightradar24 map](../../catalog/resources/fr24-gps-jamming-map.md) |
| UAV-to-satellite localization | [UAV-VisLoc](../../catalog/resources/uav-visloc-dataset-2024.md), [University-1652](../../catalog/resources/university-1652-benchmark-2020.md), [SUES-200](../../catalog/resources/sues-200-benchmark-2022.md), [AnyVisLoc](../../catalog/resources/anyvisloc-uav-localization-benchmark-2025.md) |
| Magnetic navigation | [MagNav flight data (Zenodo)](../../catalog/resources/magnav-zenodo-dataset.md) |
| Radar odometry | [Oxford Radar RobotCar](../../catalog/resources/oxford-radar-robotcar-dataset.md), [MulRan](../../catalog/resources/snu-mulran-dataset.md) |
| Long-term place recognition | [Oxford RobotCar](../../catalog/resources/oxford-robotcar-dataset.md), [NCLT](../../catalog/resources/umich-nclt-dataset.md), [HeLiPR](../../catalog/resources/snu-helipr-dataset.md) |
| Underground / degraded | [SubT-MRS](../../catalog/resources/cmu-subt-mrs-dataset.md), [DARPA SubT reference data](../../catalog/resources/darpa-subt-reference-datasets.md), [Hilti SLAM Challenge](../../catalog/resources/hilti-slam-challenge.md) |
| Event cameras | [VECtor](../../catalog/resources/vector-event-slam-benchmark.md), [DSEC](../../catalog/resources/uzh-dsec-dataset.md), [MVSEC](../../catalog/resources/upenn-mvsec-dataset.md) |
| Synthetic, any weather | [TartanAir](../../catalog/resources/cmu-tartanair-dataset.md), [Mid-Air](../../catalog/resources/midair-synthetic-drone-dataset.md) |
| UWB indoor | [UTIL](../../catalog/resources/util-uwb-dataset.md) |
| Drone tracking (C-UAS) | [Anti-UAV](../../catalog/resources/anti-uav-benchmark-paper.md) |

Check each dataset's licence on its catalog page; several are non-commercial (for example
KITTI and Oxford RobotCar per their sites).

## Simulators

| Need | Simulator |
|------|-----------|
| Autopilot in the loop | PX4 / ArduPilot SITL with [Gazebo](../../catalog/resources/gazebo-docs-tutorials.md) ([PX4](../../catalog/resources/px4-simulation-docs.md), [ArduPilot](../../catalog/resources/ardupilot-sitl-docs.md)) |
| Photo-realistic camera | [AirSim](../../catalog/resources/microsoft-airsim-docs.md) (end of active development noted in its docs), [CARLA](../../catalog/repos/carla-simulator__carla.md), [Isaac Sim](../../catalog/repos/isaac-sim__isaacsim.md) |
| IMU/GNSS error models only | [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md) |
| GNSS signal level (to files) | [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md), [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md) |
| Multi-drone RL | [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md) |
| Maritime / underwater | [VRX](../../catalog/repos/osrf__vrx.md), [HoloOcean](../../catalog/resources/byu-holoocean-docs.md) |
| Built-in VIO sim | [OpenVINS](../../catalog/repos/rpng__open_vins.md) |

## Designing a test that shows resilience

A judge-friendly experiment, adaptable to almost any project:

1. **Baseline:** run with healthy GNSS, record error vs ground truth.
2. **Outage:** remove GNSS for a defined window (mask epochs in a dataset, or disable the
   sensor in SITL). Plot error vs time for dead reckoning alone and for your system.
3. **Spoof:** inject a slowly drifting offset into GNSS (in software, on recorded data).
   Report time to detect and the maximum position error reached before rejection.
4. **Recovery:** restore GNSS; show the system re-accepts it without a jump.
5. **Report honestly:** dataset, alignment, number of runs, and where it failed.

For real interference behaviour, read the public
[Jammertest test catalogue](../../catalog/resources/jammertest-norway.md); it describes the
scenarios that Norway transmits under controlled conditions. Use it to script realistic
software scenarios, not to transmit.

## What competitions reward

- DARPA SubT scored accurate localization of reported artifacts, not just coverage; robust
  multi-sensor odometry and operator workflow mattered as much as algorithms
  ([SubT](../../catalog/resources/darpa-subt-challenge.md),
  [CERBERUS lessons](../../catalog/resources/cerberus-subt-final-paper.md)).
- ESA Kelvins scored the sim-to-real gap explicitly
  ([SPEED+](../../catalog/resources/kelvins-pose-estimation-2021.md)).
- The MagNav challenge was scored against a professionally compensated reference
  magnetometer ([challenge site](../../catalog/resources/magnav-challenge-site.md)).
- European and NATO challenges frame GNSS-denied drone navigation as multi-sensor fusion,
  with evaluation campaigns ([EDF 2024 challenge](../../catalog/resources/edf-2024-drone-navigation-challenge.md),
  [NATO DIANA challenges](../../catalog/resources/nato-diana-10-challenges-2025.md)).

## Failure modes of the evaluation itself

- Scoring an absolute-positioning system with Sim(3) alignment hides its real error.
- Tuning on the test sequence.
- Simulated GNSS outages that start at a convenient moment (e.g. straight flight).
- Spoof tests where the "spoofer" jumps instantly; real spoofers drag smoothly
  ([Humphreys 2008](../../catalog/resources/humphreys-2008-assessing-spoofing-threat.md)).
- Reporting one lucky run.

## Learn it

1. [evo](../../catalog/repos/michaelgrupp__evo.md) README and [TUM RGB-D benchmark](../../catalog/resources/tum-rgbd-benchmark.md) (its trajectory format is used widely).
2. [EuRoC](../../catalog/resources/ethz-euroc-mav-dataset.md) and [KITTI odometry](../../catalog/resources/kitti-odometry-benchmark.md) pages - the two most common baselines.
3. [Stone Soup docs](../../catalog/resources/stone-soup-docs.md) - tracking metrics.
4. [Long-term visual localization benchmark](../../catalog/resources/visual-localization-benchmark.md) - evaluation under changing conditions.
5. [Hilti SLAM Challenge](../../catalog/resources/hilti-slam-challenge.md) - hard GNSS-denied sequences with accurate truth.
6. [Jammertest](../../catalog/resources/jammertest-norway.md) - real interference scenarios.
7. [CERBERUS SubT paper](../../catalog/resources/cerberus-subt-final-paper.md) - lessons from a winning field system.

## Build with it

- [evo](../../catalog/repos/michaelgrupp__evo.md) - APE/RPE.
- [pykitti](../../catalog/repos/utiasstars__pykitti.md), [tartanairpy](../../catalog/repos/castacks__tartanairpy.md), [pyboreas](../../catalog/repos/utiasasrl__pyboreas.md) - dataset loaders.
- [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) - GSDC loaders.
- [VPR-methods-evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md) and [AnyVisLoc benchmark code](../../catalog/repos/uav-avl__benchmark.md).
- [Stone Soup](../../catalog/repos/dstl__stone-soup.md) - tracker evaluation.
- [Gazebo Sim](../../catalog/repos/gazebosim__gz-sim.md), [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md), [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md).

Related concepts: [datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md),
[simulation](../../catalog/concepts/simulation.md).
