# AI-IMU Dead-Reckoning - paper digest
<!-- about: res:brossard-ai-imu-dr, repo:mbrossar/ai-imu-dr -->
**AI-IMU Dead-Reckoning** - Brossard, Barrau, Bonnabel, IEEE Transactions on Intelligent Vehicles 2020 (arXiv 2019). [paper](https://arxiv.org/abs/1904.06064) | [code](https://github.com/mbrossar/ai-imu-dr) | Read: full text via ar5iv HTML render of arXiv 1904.06064

## Problem
Dead reckoning for a wheeled car from the IMU alone: 3D position, velocity, orientation and IMU biases in real time, so localization survives GNSS loss or camera / lidar failure. Pure integration drifts with t^2 from bias.

## Method
- **Right-invariant EKF on SE2(3)**, 21-dim error state: orientation, velocity, position, gyro and accel biases, plus car-to-IMU misalignment rotation and lever arm (both near-constant random walks).
- **Pseudo-measurements**: lateral and vertical velocity in the *car* frame are about zero (non-holonomic constraint). Fed as y = 0 with covariance N_n. Car-frame vertical is argued to be more general than world-frame zero vertical velocity.
- **Noise adapter**: a small 1D CNN reads a window of N=15 raw IMU samples (no state) and outputs z_lat, z_up. Covariance N = diag(sigma_lat^2 * 10^(beta*tanh z_lat), sigma_up^2 * 10^(beta*tanh z_up)), beta = 3, sigma_lat = 1 m/s, sigma_up = 3 m/s. 2 conv layers (kernel 5, 32 channels, dilations 1 and 3), ReLU, then FC.
- Only 6210 adapter parameters plus 12 entries of P0 and Q are learned. Q is learned but fixed in time.
- Training: Adam lr 1e-4, batches of nine 1-minute sub-sequences at random starts, Gaussian noise std 1e-4, dropout 0.5, grad clip 1, 400 epochs. Loss is the KITTI relative translation error averaged over 100-800 m segments, backpropagated through the filter; covariances are not supervised directly.
- Evaluation is leave-one-out (e.g. test seq 10 after training on 00-09).

## Data and sensors
- Sensor: OxTS RT3003 IMU at 100 Hz raw (not the 10 Hz synced stream). Paper gives gyro bias stability 36 deg/h and accel bias stability 1 mg. This is a high-grade unit, not a phone MEMS.
- Dataset: [KITTI](../dataset-cards/kitti.md) odometry sequences, seq 03 dropped (no raw data). Ground truth from OxTS GPS/IMU poses.
- Init: ground-truth initial orientation, velocity, position; biases and lever arm at zero.

## Headline results (as reported)
- Table 1, KITTI average over seqs 01, 04, 06, 07, 08, 09, 10: proposed t_rel 1.10% / r_rel 0.23 deg/m; IMU integration 171% / 0.31; ORB-SLAM2 (stereo, no loop closure) 1.17% / 0.27; IMLS (lidar) 0.98% / 0.12.
- Table 1 per sequence, proposed: 01 1.11%, 04 0.35%, 06 0.97%, 07 0.84%, 08 1.48%, 09 0.80%, 10 0.98%.
- Table 2, sequences with data gaps: 00 7.40% / 2.65, 02 2.85% / 0.38, 05 2.76% / 0.86 (vs ORB-SLAM2 1.33, 1.84, 0.75%).
- Fig. 7, seq 01 ablation: full 1.11%; without lever-arm alignment 1.65%; without covariance adaptation 1.94%.
- Fig. 8: adapter inflates lateral-velocity covariance by about 10^2 during a bend (seq 01, t = 90-110 s).
- Seq 08 text: about 5 m final error vs about 20 m cited for visual-inertial methods.
- Runtime / hardware: not reported.

## Limitations
- Stated by authors: seqs 00, 02, 05 degrade due to about 2 s IMU / ground-truth gaps (kept unmodified). KITTI only; cannot submit to the online benchmark (IMU withheld). Lidar / vision baselines are not like-for-like. Q is not adapted online. Learned covariances are tuned for accuracy, not statistical truth. Other vehicles left as future work. A learned block may hinder certification.
- Our read: the 1.10% headline is with a 36 deg/h tactical-ish IMU and ground-truth initialization. A consumer MEMS IMU will be much worse; do not quote 1.10% for a phone or Pixhawk.
- Our read: the README states the shipped parameters were trained on 00, 01, 04-11, so only 02 is a true test sequence for the released weights (the paper's leave-one-out numbers need retraining per fold).
- Our read: the non-holonomic assumption fails on skidding, off-road slip, or reversing on slopes; the adapter only partly absorbs that.

## Code, weights, license
- Repo `mbrossar/ai-imu-dr`, MIT (GitHub API), last push 2025-01-08, not archived. PyTorch, tested under Python 3.5 per README.
- Trained parameters: Dropbox zip linked from the README (`temp.zip`); no separate license stated. Preprocessed KITTI IMU pickles: GitHub attachment zip.
- Data license: KITTI is CC BY-NC-SA 3.0, so pickles derived from it carry that restriction (our read).

## Reproduction effort (estimate)
Estimate:
- Hardware: CPU is enough to run the filter; training is light (6k parameters) but backprop through the filter is slow on CPU.
- Data: two small zips (pickled KITTI IMU + trained params). Dropbox link may rot; regenerate from KITTI raw with `read_data = 1` if so.
- Time to first result: 1-3 hours, mostly fixing an old Python / PyTorch environment.
- Not reproducible directly: leave-one-out numbers (needs 7+ retrains), anything off KITTI without new training data.

## What a hackathon team can take from it
- Non-holonomic pseudo-measurement (zero lateral and vertical velocity in vehicle frame) is the single cheapest drift reducer for any ground vehicle INS. Add it to [KF-GINS](../integration-cards/i2nav-whu__kf-gins.md) or a [filterpy](../integration-cards/rlabbe__filterpy.md) EKF in an afternoon, no learning needed.
- Learned noise adaptation pattern: tiny CNN on raw IMU => measurement covariance scale with bounded range (10^(3 tanh z)). Safe to bolt onto a classical filter because the network can only re-weight, never inject a state.
- Estimate the IMU-to-vehicle misalignment and lever arm in the filter; ablation shows it matters (1.65% vs 1.11%).
- Use the KITTI 100-800 m t_rel / r_rel protocol to report GNSS-outage bridging; score with [evo](../integration-cards/michaelgrupp__evo.md).
