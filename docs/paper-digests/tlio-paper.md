# TLIO - paper digest
<!-- about: res:tlio-paper, repo:cathias/tlio -->
**TLIO: Tight Learned Inertial Odometry** - Liu, Caruso, Ilg, Dong, Mourikis, Daniilidis, Kumar, Engel, IEEE RA-L 2020 (DOI 10.1109/LRA.2020.3007421). [paper](https://arxiv.org/abs/2007.01867) | [code](https://github.com/CathIAS/TLIO) | Read: full text via ar5iv HTML render of arXiv 2007.01867 (v3)

## Problem
IMU-only pedestrian dead reckoning. Strapdown integration of a consumer IMU drifts within seconds. VIO fixes drift but costs power, raises privacy issues and fails in low light or occlusion. Goal: IMU-only 3D pose for a head-mounted device.

## Method
- Network: 1D ResNet18 over a 1 s window (N=200 samples at 200 Hz, 6 channels) expressed in a **gravity-aligned, yaw-free** local frame. Yaw is removed so the network cannot inject spurious heading observability.
- Two FC heads: 3D displacement over the window and a diagonal log-sigma; covariance = diag(exp(2u)), so uncertainty axes are locked to the gravity-aligned frame.
- Loss: MSE for 10 epochs, then Gaussian NLL for about 10 more (direct NLL did not converge).
- Augmentation: random yaw rotation, additive accel bias U[-0.2, 0.2] m/s^2, gyro bias U[-0.05, 0.05] rad/s, gravity-direction perturbation up to 5 deg.
- Filter: **stochastic-cloning EKF**. State = current rotation, velocity, position, gyro and accel biases plus m cloned past poses (error-state dim 6m+15). Propagates with raw IMU at IMU rate.
- Update: network displacement between a past clone and the current state, at 20 Hz; with a 1 s window that means at most 21 clones.
- Chi-square outlier gate at 11.345 (99th percentile, 3 DOF). Network covariance scaled by 10 to account for correlation of overlapping windows.

## Data and sensors
- Sensor: Bosch BMI055 IMU on a headset rigidly attached to cameras.
- Own dataset: more than 400 sequences, about 60 hours (walking, stairs, kitchen tasks, pool and more), multiple devices, more than 5 people. Ground truth from an in-house MSCKF-style VIO at 1000 Hz.
- Split 80/10/10 random; test set 37 trajectories of 3-7 minutes.
- Not evaluated on [RoNIN](../dataset-cards/ronin.md) or other public sets in the paper. Baseline is 3D-RoNIN retrained on the same data.

## Headline results (as reported)
- Introduction: 27% lower yaw drift and 33% lower position drift than the best RoNIN velocity-concatenation baseline.
- Sec. VII-B1 / Fig. 8: 27% yaw and 31% position drift reduction vs 3d-ronin-mse. Note the 33% vs 31% mismatch inside the paper (different baseline variant).
- Fig. 3: CDFs over the test set; the paper states TLIO is lower than 3d-ronin for all metrics. **No numeric ATE / RTE table** is given; absolute values not located.
- Fig. 6: over 99% of errors within 3 sigma; outside 3 sigma 0.70% (x, y) and 0.47% (z); 0.30% of samples exceed the 99th-percentile chi-square value. The learned covariance is close to calibrated.
- Fig. 8: learned covariance beats a fixed diag(0.051, 0.051, 0.013) m covariance; fixed variants lose track in one initialization failure.
- Fig. 9: higher update frequency improves ATE and drift; relative yaw error over 1 s grows with frequency.
- Runtime: training about 4 hours on an NVIDIA DGX. Inference and filter runtime not reported.

## Limitations
- Stated by authors: unusual motions (side-stepping, rolling on a chair) break it (Fig. 4). Needs an external initial state; bad init causes yaw drift. IMU used both for propagation and as network input, which can violate EKF independence. Overlapping windows correlate errors (hence the x10 covariance scale). Update undefined when looking straight up or down. Extending to legged robots is open.
- Our read: yaw is unobservable by construction, so heading drift is the dominant long-term error; it needs a magnetometer, map or visual yaw fix for anything beyond minutes.
- Our read: the body is a human head. Domain gap to vehicles, drones or handheld phones is large; retraining is mandatory.

## Code, weights, license
- Repo `CathIAS/TLIO`. GitHub API reports NOASSERTION; the LICENSE file is a BSD license (Facebook copyright, "For TLIO training and inference software"). Last push 2023-08-08, not archived.
- Dataset released: Google Drive zip named `golden-new-format-cc-by-nc-with-imus-v1.5`, i.e. **CC BY-NC**. Attitude filter data not included.
- **No pretrained weights** released; README says users must train (or generate their own dataset and retrain).
- README warning: network-only test mode integrates with ground-truth orientation, so its metrics are a debugging tool, not a benchmark. Use `main_filter.py` for honest numbers.

## Reproduction effort (estimate)
Estimate:
- Hardware: one GPU; paper reports 4 h on a DGX, expect most of a day on a single consumer GPU.
- Data: one Google Drive download (size not checked) plus conda env from `environment.yaml`.
- Time to first filter result: 1-2 days (train, convert to TorchScript, run filter on test sequences).
- Not reproducible: the headset hardware, the internal VIO ground truth, commercial use of the data (NC license).

## What a hackathon team can take from it
- The pattern itself: learned displacement + learned covariance as an EKF measurement between clone states. It works on any IMU-only body (foot, vehicle, drone) once retrained, and is the template later papers (AirIO, EqNIO) extend.
- Gravity-aligned, yaw-free input frame plus random-yaw augmentation: the right inductive bias when heading is unknown.
- Two concrete tuning numbers: chi-square gate 11.345 for 3 DOF updates and x10 covariance inflation for overlapping windows. Both transfer directly to a [filterpy](../integration-cards/rlabbe__filterpy.md) EKF.
- MSE-then-NLL training schedule for any network that must output a usable covariance.
- Pair with a yaw source (magnetometer via [Fusion](../integration-cards/xiotechnologies__fusion.md), or a visual fix) for runs longer than a few minutes.
