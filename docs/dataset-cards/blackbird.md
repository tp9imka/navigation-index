# Blackbird UAV dataset

<!-- about: repo:mit-aera/blackbird-dataset -->

MIT AERA dataset of aggressive indoor quadrotor flights (Antonini et al., ISER 2018 / IJRR 2020): real IMU, motor speed and mocap data, with camera images rendered afterwards in photorealistic virtual environments (FlightGoggles). Useful when you want many speeds of the same trajectory and perfect pose truth.

| Field | Value |
|---|---|
| Platform | Custom quadrotor in a motion-capture room, up to 7.0 m/s |
| Environment | Real flight indoors; imagery rendered in 5 virtual environments (e.g. "Large_Apartment_Night_Near_Couches" in the README example) |
| Sensors and rates | Stereo and downward virtual cameras 120 Hz (rendered), IMU 100 Hz (real), motor speed sensors ~190 Hz (arXiv abstract) |
| Ground truth | Motion capture at 360 Hz, "millimeter-level accuracy" (arXiv abstract) |
| Size | Full dataset 4.9 TB (README). Per-sequence size not verified: blackbird-dataset.mit.edu did not respond on 2026-11-06 |
| License | Repo (tools) MIT. Dataset-specific license not stated in the README |
| Format | ROS1 bags (IMU, PWM/RPM custom messages, mocap) plus rendered image sequences per environment |
| Index | [Blackbird dataset repo](../../catalog/repos/mit-aera__blackbird-dataset.md) |

## What's in it

- 168 flights, 17 trajectory shapes (Clover, Mouse, Star, Picasso, Thrice, ...), each at several top speeds 0.5-7.0 m/s, yaw-forward and constant-yaw variants; over 10 hours (abstract and README table).
- Calibration flights for dynamics with no camera data (3D/flat figure-8).
- README warns: "some pre-rendered sequences are unavailable for download".

## Download

Host `http://blackbird-dataset.mit.edu/BlackbirdDatasetData/` timed out on 2026-11-06. If it is back, use the repo's helper:

```bash
git clone https://github.com/mit-aera/Blackbird-Dataset
python3 Blackbird-Dataset/fileTreeUtilities/sequenceDownloader.py \
  --flight=clover/yawForward/maxSpeed5p0 \
  --environment=Large_Apartment_Night_Near_Couches \
  --datasetFolder=$HOME/blackbirdDatasetData
# or the README's docker quickstart image winterg/flightgoggles_ros:ijrr
```

## Loading and tooling

- Build the repo's ROS message package to read `blackbird/MotorRPM` and `blackbird/MotorPWM`; `roslaunch blackbird playback_sequence.launch` replays a flight.
- Score with [evo](../../catalog/repos/michaelgrupp__evo.md) after exporting mocap to TUM format.

## Hackathon fit

- Idea 5 (INS holdover budget calculator) and learned-dynamics/inertial odometry: real IMU + motor RPM + mm truth at 360 Hz is rare; "IMU + motor model dead reckoning" demos fit well.
- Idea 10 VIO testing only with caveat: images are synthetic.

## Pitfalls

- Host availability is the main risk; confirm downloads well before the event.
- Rendered imagery: a VIO that works here has not proven anything about real camera noise or rolling shutter.
- Full set is multi-terabyte; choose one trajectory and one environment.
- Custom ROS message types needed even to read IMU/motor bags.

## Sources

- `gh api repos/mit-aera/Blackbird-Dataset/readme` (trajectory table, 4.9 TB, downloader, docker quickstart), LICENSE.md (MIT)
- https://arxiv.org/abs/1810.01987 (rates, mocap 360 Hz, mm accuracy, 10 h / 168 flights)
- HEAD/GET on blackbird-dataset.mit.edu: no response, 2026-11-06
