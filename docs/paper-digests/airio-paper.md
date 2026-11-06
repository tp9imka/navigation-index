# AirIO - paper digest
<!-- about: res:airio-paper, repo:air-io/air-io -->
**AirIO: Learning Inertial Odometry with Enhanced IMU Feature Observability** - Qiu, Xu, Chen, Zhao, Geng, Scherer, IEEE RA-L 2025 (accepted per arXiv v2). [paper](https://arxiv.org/abs/2501.15659) | [code](https://github.com/Air-IO/Air-IO) | Read: full text, arXiv HTML v2 (16 Jun 2025)

## Problem
Learned inertial odometry (RoNIN, TLIO style) works for pedestrians but transfers badly to multirotor UAVs, whose motion is agile and not periodic. Existing UAV variants often need extra inputs (thrust, rotor speed). The paper asks why, and how to get IMU-only learned odometry on drones.

## Method
- Core claim: the usual practice of rotating IMU data into a global (gravity-aligned) frame couples attitude nonlinearly with the motion force and hides features the network needs. Keeping IMU data in the **body frame** keeps attitude linearly coupled with gravity and more observable.
- Supported by latent-feature analysis: PCA reaches 95% energy with k=5 (body) vs k=8 (global) on Blackbird, k=15 vs k=40 on Pegasus; t-SNE separates velocity levels better in body frame.
- **Attitude encoding**: orientation mapped to so(3), passed through a CNN encoder, concatenated with the IMU encoder output, then bi-directional GRUs.
- Two MLP heads: body-frame **velocity** and its uncertainty (diag covariance). Loss: Huber (delta 0.005) plus an uncertainty term weighted lambda 1e-4.
- Training uses ground-truth orientation for the attitude input; test uses EKF-estimated orientation.
- **EKF**: state = rotation, global velocity, position, gyro/accel biases. Propagation uses AirIMU (separate learned IMU correction model with its own uncertainty); AirIO velocity is the measurement. Because the net predicts current-frame velocity, no cloned past states are needed (unlike TLIO).
- Repo also ships a CasADi-based EKF for faster Jacobians.

## Data and sensors
- Sensor: IMU only (200 Hz in the runtime test). Orientation input from AirIMU-corrected integration or EKF.
- [Blackbird](../dataset-cards/blackbird.md): 5 SEEN sequences (trajectories shared with training) and 5 UNSEEN (ampersand, sid, oval, sphinx, bentDice). Indoor mocap, aggressive flight.
- [EuRoC MAV](../dataset-cards/euroc-mav.md): 6 training sequences, rest test (appendix). V101 ground truth replaced by an OpenVINS recalibrated version (repo README).
- Pegasus: custom NVIDIA Isaac Sim simulation, 7 trajectories (4 train / 3 test), no external disturbance.

## Headline results (as reported)
- Table I, Blackbird average ATE / RTE: AirIO EKF 0.403 / 0.299 SEEN and 1.309 / 0.834 UNSEEN; TLIO 1.189 / 1.042 SEEN and 3.478 / 3.541 UNSEEN; RoNIN 2.193 / 1.828 SEEN and 13.487 / 8.532 UNSEEN; IMO (uses thrust) 0.929 / 1.004 SEEN and 9.015 / 5.962 UNSEEN; AirIMU-only 7.084 / 1.503 SEEN; dead-reckoning baseline 27.475 / 4.008 SEEN. Units as in the table (not restated in what we read).
- Table I text: vs TLIO on SEEN, 66.1% ATE and 71.3% RTE lower; vs IMO on UNSEEN, 85.5% ATE and 86.0% RTE lower.
- Table II, EuRoC average ATE / RTE: AirIO EKF 3.177 / 1.192; AirIO Net 3.846 / 1.198; RoNIN 6.75 / 2.516; TLIO 6.969 / 3.052. Text: EKF 52.9% better ATE than RoNIN, 54.4% than TLIO.
- Abstract: 66.7% average accuracy gain from the body-frame representation across three datasets, a further 23.8% from attitude encoding.
- Ablation (Table III, Figs. 9-10): removing the rotation-coupled gravity term raises ATE by 90.0% (EuRoC), 107.0% (Pegasus), 360.5% (Blackbird UNSEEN).
- Appendix A-H: on EuRoC, VIO (OpenVINS-class) still beats AirIO by a 64.1% ATE margin; on Blackbird the paper calls AirIO comparable to VIO (VIO suffers motion blur at up to 8 m/s).
- Runtime: 200 Hz IMU, 1000-frame buffer (about 5 s). Jetson AGX Orin 74.23 ms average per update; i9-12900K + RTX 2060 28.92 ms.

## Limitations
- Stated by authors: no closed-loop deployment on a real UAV yet (future work). Several baselines (RoNIN, TLIO, IMO) are fed ground-truth orientation, flagged in table footnotes. IMO uses thrust, so not input-matched. Pegasus is idealized, no disturbances.
- Our read: all real data is indoor mocap (Blackbird, EuRoC). Blackbird SEEN shares trajectory shapes with training, so SEEN numbers flatter the method; UNSEEN is the honest column. No outdoor, wind, long-duration or fixed-wing evidence.
- Our read: the full pipeline depends on a second learned model (AirIMU) trained per dataset; a new airframe means two trainings.
- Our read: 74 ms per update on Orin is fine for a 10-20 Hz filter update, not for running the net at IMU rate.

## Code, weights, license
- Repo `Air-IO/Air-IO`, BSD-3-Clause (GitHub API), last push 2026-09-16, not archived. Built on PyPose.
- Pretrained AirIO models and AirIMU results for EuRoC, Blackbird, Pegasus are GitHub release assets in the same repo; no separate weights license stated, so BSD-3 by default (our read).
- Dataset licenses are separate: EuRoC is non-commercial per its card; Blackbird dataset license not stated in its README.
- Default inference mode uses **ground-truth orientation**; README says to switch `rot_type` to `airimu` or `integration` for a fair run.

## Reproduction effort (estimate)
Estimate:
- Hardware: one consumer GPU for inference and EKF; training on Blackbird fits a single GPU (dataset sizes not checked).
- Data: simplified EuRoC and Blackbird splits are release zips on the repo; no need to pull the 4.9 TB full Blackbird.
- Time to first result: 2-4 hours to run inference + EKF on Blackbird with released models and AirIMU pickles. Retraining on a new platform: 1-2 days including AirIMU.
- Not reproducible from what we read: the IMO and VIO baselines (separate code), real-flight closed-loop use.

## What a hackathon team can take from it
- The body-frame representation trick: if training any learned IO on drone data, feed body-frame IMU plus an explicit attitude encoding, not gravity-rotated IMU. Cheapest single change with the largest reported effect.
- Velocity-as-measurement EKF: a learned body velocity plus covariance is a simple update for any INS EKF (no clone states). Plugs into a [filterpy](../integration-cards/rlabbe__filterpy.md) or [KF-GINS](../integration-cards/i2nav-whu__kf-gins.md) style filter as a GNSS-outage bridge.
- Use the UNSEEN split protocol on Blackbird as the evaluation to quote; score with [evo](../integration-cards/michaelgrupp__evo.md).
- Learned covariance doubles as a gate: inflate or reject velocity updates when predicted sigma is large.
- Before trusting any demo number, check `rot_type` is not ground truth.
