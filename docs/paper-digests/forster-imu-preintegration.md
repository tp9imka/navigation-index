# IMU preintegration (Forster) - paper digest
<!-- about: res:forster-imu-preintegration, repo:borglab/gtsam -->
**On-Manifold Preintegration for Real-Time Visual-Inertial Odometry** - Forster, Carlone, Dellaert, Scaramuzza, IEEE Transactions on Robotics 2016 (DOI 10.1109/TRO.2016.2597321; arXiv 2015). [paper](https://arxiv.org/abs/1512.02363) | [code](https://github.com/borglab/gtsam) | Read: full text via ar5iv HTML render of arXiv 1512.02363 (two passes, whole page)

## Problem
Optimization-based VIO is more accurate than filtering but gets too slow as the trajectory grows, and a 200-800 Hz IMU would add a state per sample. Earlier preintegration (Lupton and Sukkarieh) used Euler angles, which are not frame-invariant and break near gimbal lock.

## Method
- **Preintegration on SO(3)**: all IMU samples between two keyframes are summarized into one relative-motion measurement (delta rotation, delta velocity, delta position) that does not depend on the absolute start state, so it is computed once.
- Analytic residuals and Jacobians are derived on the manifold (exponential map, right Jacobians).
- **Noise propagation**: preintegrated noise treated as zero-mean Gaussian to first order; its covariance is propagated iteratively sample by sample (appendix).
- **Bias correction**: when the bias estimate changes, the preintegrated delta is updated with a first-order Jacobian instead of re-integrating raw samples.
- **Structureless vision factors**: 3D landmarks eliminated linearly (Schur-style), so each landmark becomes one factor over the keyframes that see it.
- Backend: factor graph solved incrementally with iSAM2, keyframe-based; front end SVO. Released in GTSAM 4.0 (`ImuFactor`, `CombinedImuFactor`).

## Data and sensors
- Sensors: monocular camera + IMU. Real rig: VI-Sensor (ADIS16448 IMU at 800 Hz, WVGA camera at 20 Hz).
- Simulation (Sec. VIII-A, Fig. 5): 3 m radius circle with sinusoidal height, 120 m, 50 landmarks per frame, 1 px noise, keyframes at 2.5 Hz, 50 Monte Carlo runs. IMU noise: gyro 0.0007 rad/(s sqrt(Hz)), accel 0.019 m/(s^2 sqrt(Hz)), gyro bias 0.0004, accel bias 0.012.
- Real data: own indoor (Vicon), outdoor loop and multi-floor sequences. No [EuRoC](../dataset-cards/euroc-mav.md) table located in the version we read.

## Headline results (as reported)
- Sec. VIII-B2: 430 m indoor trajectory; over 360 m, average drift 0.3 m for the proposed method vs 0.7 m for OKVIS and MSCKF; much lower yaw drift, similar roll / pitch (gravity observable).
- Fig. 18, outdoor loop about 300 m vs Google Tango: caption says 1.0 m end-to-end error vs 2.2 m for Tango; body text says 1.5 m. The paper contradicts itself here.
- Fig. 19, multi-floor 160 m: about 0.5 m vs about 1.4 m for Tango.
- Fig. 7: iSAM2 accuracy "practically the same as the batch estimate" (simulation).
- Fig. 9: average NEES stays below the 7.0 upper bound of the [5.0, 7.0] acceptance region, i.e. not overconfident.
- Figs. 12-13: Euler-angle preintegration degrades with large dt, high rates (1-3 rad/s) and near 90 deg pitch; the SO(3) version stays accurate.
- Runtime: iSAM2 back end about 10 ms average per update with 10 iterations on an Intel i7 2.4 GHz laptop. Abstract: full smoothing at 100 Hz. Front-end per-frame time printed as "33ms" with an ambiguous footnote marker; we could not resolve it.

## Limitations
- Stated by authors: assumes constant rotation rate between IMU samples (fine at high rate; slower IMUs may need higher-order integration). First-order approximations for rotation noise and bias correction. No marginalization of past states, no loop closure. Real-world consistency checked on one run. Outdoor comparisons use different hardware, so only qualitative.
- Our read: first-order bias correction is only accurate for small bias changes; after a large bias jump (e.g. after a long GNSS outage) re-integrate.
- Our read: the paper's real-data evidence is a handful of own sequences; trust the method because it became the standard (VINS-Mono, ORB-SLAM3, LIO-SAM all use variants), not because of these tables.

## Code, weights, license
- Implemented in GTSAM (`gtsam/navigation`): `PreintegratedImuMeasurements`, `ImuFactor`, `PreintegratedCombinedMeasurements`, `CombinedImuFactor`. Python via `pip install gtsam` (4.3.0 per our integration card).
- GTSAM license: GitHub API says NOASSERTION; LICENSE file says simplified BSD (LICENSE.BSD), with third-party parts under BSD-3 (CCOLAMD), MPL2 (Eigen, Spectra), Apache 2.0 (METIS).
- No weights (not a learned method). GTSAM actively maintained, last push 2026-11-06.

## Reproduction effort (estimate)
Estimate:
- Hardware: any laptop.
- Data: GTSAM bundled example data, or EuRoC for a VIO run.
- Time to first result: 15-30 min to run GTSAM's `ImuFactorExample.py` / `IMUKittiExampleGPS.py`. A full VIO reproduction of the paper (SVO front end + structureless factors) is days and not worth it in a hackathon.
- Not reproducible: the paper's own indoor / outdoor sequences and the Tango comparison.

## What a hackathon team can take from it
- Use `CombinedImuFactor` between keyframes (1-10 Hz) instead of a state per IMU sample; add GNSS, visual-fix or magnetometer factors at keyframes. Starting point: [GTSAM integration card](../integration-cards/borglab__gtsam.md).
- GNSS-outage demo pattern: same graph, drop GNSS factors for N seconds, watch preintegrated IMU carry the trajectory and the marginal covariance grow.
- Noise model numbers from the simulation section are a sane first guess for a mid-grade MEMS IMU; then tune from the datasheet.
- Preintegration is also the clean interface for learned IMU correction (AirIMU style): correct raw samples, then preintegrate.
