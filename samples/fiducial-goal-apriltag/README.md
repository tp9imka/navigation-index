# fiducial-goal-apriltag: how far and how oblique an AprilTag goal still works, and a tag-relative final approach

Goal: when B is "the marker" or "the pad", odometry only has to bring the tag into view; the tag
then gives a metric relative goal for the last metres
([03-close-area-localization.md section 3](../../docs/research/close-area-nav/03-close-area-localization.md)).
This sample measures where that hand-over can happen. It renders a tag36h11 tag onto a textured
wall with a pinhole camera at known poses, detects it with pupil-apriltags, and reports detection
rate and pose error per range and view-angle cell. `final_approach.py` then closes the loop: a
camera-equipped point mass starts 3 m off the tag axis and servos on the detected tag pose.

**Every number here is synthetic**: rendered images, a kinematic vehicle, no real camera, no SITL.

Hub wiring proposals: [INTEGRATION.md](INTEGRATION.md).

## Run

```sh
cd samples/fiducial-goal-apriltag
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt
.venv/bin/python sweep.py                                          # ~50 s, results/sweep.*
.venv/bin/python sweep.py --blur 1.5 --noise 6 --name sweep_harsh  # ~60 s
.venv/bin/python sweep.py --tag-size 0.40 --name sweep_tag040      # ~50 s
.venv/bin/python final_approach.py                                 # ~40 s on 8 processes
.venv/bin/python final_approach.py --blur 1.5 --noise 6 --name final_approach_harsh
.venv/bin/python -m unittest test_smoke -v                         # ~5 s; skips without numpy
```

The detector prints `Error, more than one new minima found.` a few times per sweep (2-4 lines).
It comes from the bundled AprilTag C code during pose estimation; the detections are still
returned and scored. Not investigated further.

## Set-up

| Item | Value |
|---|---|
| Camera | Pinhole, 640 x 480, fx = fy = 500 px, cx = 319.5, cy = 239.5, no distortion => HFOV 65.2 deg, VFOV 51.3 deg. Level camera |
| Tag | tag36h11 id 7, 0.16 m black-border edge (A4 printable), 2-cell white margin, ink 25 DN, paper 220 DN. Bitmap from OpenCV `DICT_APRILTAG_36h11`; pupil-apriltags decodes it as id 7 |
| Scene | Tag on a 12 m wall texture (smooth blotches, 60 random rectangles, pixel noise); rays that miss the wall see flat 150 DN |
| Render | Homography warp at 3x supersampling, area-downsampled; then Gaussian blur (sigma px) and Gaussian noise (sigma DN). Default blur 0.8 px, noise 3 DN; "harsh" blur 1.5 px, noise 6 DN |
| Detector | pupil-apriltags 1.0.4.post11, `quad_decimate 1.0`, `refine_edges 1`, `decode_sharpening 0.25`, 1 thread, pose from `estimate_tag_pose` |
| Sweep | Range 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8 m x view angle 0-70 deg in 10 deg steps (camera rotated about the vertical axis off the tag normal). 20 trials per cell with a random in-plane tag roll and a random pan/tilt so the tag is not always centred. Seed 0 |
| Metrics | Detection = the right id was returned. Position error = norm of `pose_t` minus truth. Yaw error = error in the heading of the tag's outward normal seen from the camera (the tag-relative heading an approach uses). Gross yaw = yaw error > 10 deg. Cell "fails" below 50 % detection; "holds" at 90 % or more |

## Results (ran 2026-11-09, synthetic)

Apple M3 Max, CPython 3.12.10, numpy 2.5.4, opencv-python-headless 5.0.0.93, pupil-apriltags
1.0.4.post11. All inputs synthetic.

### Sweep, 0.16 m tag, blur 0.8 px, noise 3 DN

`python sweep.py`, wall 50.4 s ([results/sweep.md](results/sweep.md), [.json](results/sweep.json),
[heatmap](results/sweep_heatmap.png)):

| view angle deg | ranges with rate >= 0.9 m | far fail: first range beyond with rate < 0.5 m | near fail: closest-side range with rate < 0.5 m |
|---|---|---|---|
| 0 | 0.5-5 | 6.0 | - |
| 10 | 0.5-5 | 6.0 | - |
| 20 | 0.5-4 | 6.0 | - |
| 30 | 0.5-4 | 6.0 | - |
| 40 | 0.5-4 | 5.0 | - |
| 50 | 0.5-4 | 5.0 | - |
| 60 | 0.5-3 | 4.0 | - |
| 70 | 0.5-2 | 3.0 | - |

**Where detection fails:** at 6 m for a frontal view (1/20 detected, 1.67 px per tag cell),
at 5 m from 40 deg, at 4 m from 60 deg and at 3 m at 70 deg (1/20). Nothing is detected at 7 or
8 m at any angle. No wrong-id detections in 1600 frames.

Selected cells, verbatim from [results/sweep.md](results/sweep.md):

| range m | angle deg | rate | pos err med m | pos err p95 m | pos err med % range | yaw err med deg | yaw err p95 deg | gross yaw (>10 deg) | wrong id |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 1.00 | 0.001 | 0.002 | 0.14 | 0.42 | 0.94 | 0/20 | 0 |
| 1 | 30 | 1.00 | 0.001 | 0.002 | 0.14 | 0.07 | 0.17 | 0/20 | 0 |
| 1 | 60 | 1.00 | 0.001 | 0.002 | 0.14 | 0.06 | 0.11 | 0/20 | 0 |
| 2 | 0 | 1.00 | 0.003 | 0.004 | 0.15 | 0.63 | 2.91 | 0/20 | 0 |
| 2 | 30 | 1.00 | 0.003 | 0.004 | 0.15 | 0.12 | 0.25 | 0/20 | 0 |
| 2 | 60 | 1.00 | 0.006 | 0.017 | 0.30 | 0.11 | 0.39 | 0/20 | 0 |
| 3 | 0 | 1.00 | 0.009 | 0.016 | 0.30 | 2.62 | 4.31 | 0/20 | 0 |
| 3 | 30 | 1.00 | 0.006 | 0.015 | 0.22 | 0.16 | 0.61 | 0/20 | 0 |
| 3 | 60 | 1.00 | 0.022 | 0.051 | 0.73 | 0.31 | 0.52 | 0/20 | 0 |
| 4 | 0 | 1.00 | 0.036 | 0.067 | 0.90 | 3.46 | 9.51 | 1/20 | 0 |
| 4 | 30 | 1.00 | 0.023 | 0.041 | 0.57 | 0.29 | 1.06 | 0/20 | 0 |
| 4 | 60 | 0.00 | - | - | - | - | - | 0/0 | 0 |
| 5 | 0 | 1.00 | 0.044 | 0.091 | 0.88 | 2.43 | 8.63 | 0/20 | 0 |
| 5 | 30 | 0.60 | 0.032 | 0.060 | 0.63 | 0.51 | 1.06 | 0/12 | 0 |
| 6 | 0 | 0.05 | 0.111 | 0.111 | 1.86 | 9.39 | 9.39 | 0/1 | 0 |

Reading:
- In every cell with 90 % detection or more, the median position error is under 1 % of range
  except 2 m / 70 deg (1.35 %), and the largest p95 is 0.091 m (5 m, 0 deg).
- Heading is worst near frontal views and best obliquely: at 3 m, p95 yaw error is 4.31 deg at
  0 deg but 0.61 deg at 30 deg. Gross heading errors (pose ambiguity, normal mirrored about the
  line of sight) appear from 3 m: 17 of 968 detections overall, and p95 yaw error reaches
  22.28 deg at 4 m / 20 deg and 39.59 deg at 5 m / 20 deg. Position is unaffected by these flips;
  a goal point set out along the tag normal is.
- Up to 2 m and 50 deg the median position error is a near-constant 0.14-0.16 % of range, in
  the harsh sweep 0.14 % at 0.5 m. That floor may come from the renderer or from the detector's edge
  refinement; the cause was not isolated.

### Harsher images and a bigger tag

`--blur 1.5 --noise 6` (wall 60.3 s, [results/sweep_harsh.md](results/sweep_harsh.md),
[heatmap](results/sweep_harsh_heatmap.png)): detection holds (>= 0.9) only to 2 m at 0-60 deg and
1.5 m at 70 deg; it fails at 4 m frontal, 3 m from 40 deg and 2 m at 70 deg. One wrong-id
detection in 1600 frames.

`--tag-size 0.40` (pad-sized, wall 50.6 s, [results/sweep_tag040.md](results/sweep_tag040.md),
[heatmap](results/sweep_tag040_heatmap.png)): holds 1-8 m at 0-60 deg (p95 position error
0.059 m at 8 m frontal) and 1-6 m at 70 deg; fails at 7 m / 70 deg. It **fails at 0.5 m at every
angle** (rate 0.45 frontal, 0 from 30 deg): with its margin the tag no longer fits the 51 deg
vertical FOV. A pad tag alone cannot guide the last half metre of a landing with this camera;
nest a small tag inside it.

### Final approach, 50 seeds

Vehicle: kinematic point mass, 50 Hz, first-order velocity lag 0.3 s, speed cap 0.8 m/s,
velocity disturbance 0.05 m/s per axis per step, yaw-rate disturbance 2 deg/s. Camera at 10 Hz
renders from the true pose; the controller uses the detection from the previous frame only.
Start 3 m off the tag axis (lateral, side random), 3.5-4.5 m out from the wall, height +-0.2 m,
pointed at the tag +-5 deg. Goal: 1 m in front of the tag centre, facing it. Control:
velocity = 0.8/s x (goal point in the camera frame, from the detected `pose_R`, `pose_t`),
yaw rate keeps the tag centred. Tag not yet seen => creep forward 0.3 m/s along the camera axis;
lost after acquisition => hover. Stop when the estimated goal offset is under 0.05 m for 10
frames; final error is the **true** distance to the goal at that moment. Threshold 0.1 m.

`python final_approach.py`, wall 39.9 s on 8 processes
([results/final_approach.md](results/final_approach.md), [.json](results/final_approach.json),
[top-view plot](results/final_approach.png)):

| seeds | arrived (stop rule) | true final err <= 0.1 m | final err med m | p95 m | max m | final yaw err med deg | p95 deg | time to arrive med s | max s | first detection med s |
|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 50 | 50 (PASS vs all seeds) | 0.0145 | 0.0266 | 0.0307 | 1.08 | 2.4345 | 10.1 | 22.9 | 1.0 |

Start range 4.636-5.406 m, view angle 33.7-40.3 deg. Frames with a detection: 4314 of 5550;
detections with heading error > 10 deg: 83.

`--blur 1.5 --noise 6`, wall 46.3 s ([results/final_approach_harsh.md](results/final_approach_harsh.md)):

| seeds | arrived (stop rule) | true final err <= 0.1 m | final err med m | p95 m | max m | final yaw err med deg | p95 deg | time to arrive med s | max s | first detection med s |
|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 50 | 50 (PASS vs all seeds) | 0.0129 | 0.0225 | 0.0253 | 0.92 | 1.862 | 13.4 | 15.9 | 7.5 |

Reading:
- PASS: 50 of 50 seeds end within 0.1 m in both image settings; the worst is 0.031 m. The final
  error is set mostly by the 0.05 m stop rule, not by the detector, which is at about 1 mm at
  1 m range.
- The hard part is acquisition. The start is at 4.6-5.4 m and 34-40 deg, right at the edge of
  the 0.16 m tag's envelope, so 22 % of frames (1236 of 5550) had no detection. Seeds 21 and 41
  took 21.3 s and 22.9 s because they hovered through repeated drop-outs at that range.
- With harsh images the tag is first seen after a median 7.5 s of creeping (vs 1.0 s), i.e.
  closer. Fewer far-range frames means fewer flipped headings (2 vs 83), so the run is slower
  to start but cleaner once locked.

## Limits (real-camera effects not modelled)

- No lens distortion: real lenses need calibration and rectification (or passing distorted
  corners to a solver that models them); a miscalibrated fx scales range directly.
- No rolling shutter, no motion blur tied to vehicle motion (blur is a fixed isotropic Gaussian),
  no exposure control, auto-gain, saturation, glare on glossy prints, or uneven light.
  Gaussian read noise only; no shot noise, compression artefacts or JPEG.
- The tag is perfectly flat and printed at exactly its nominal size; no partial occlusion, no
  multiple tags, no tag bundle.
- The vehicle is a level kinematic point mass: no attitude tilt while accelerating (which on a
  real quadrotor moves the camera), no wind, no obstacles, no odometry to bridge drop-outs.
  The wall-tag geometry stands in for a down-looking pad camera via a fixed mount rotation;
  the pad case itself was not run.
- No ambiguity handling (tag bundles, temporal filtering, rejecting heading jumps) is
  implemented; the flips are counted, not mitigated.
- Thresholds (0.5 / 0.9 detection, 10 deg gross, 0.05 m stop rule, 0.1 m pass) are this
  sample's choices. 20 trials per cell gives coarse rates (steps of 0.05).
- Timings are on one machine; detection took a median of up to 24 ms per 640 x 480 frame on one
  thread in the default sweep ([results/sweep.json](results/sweep.json), `detect_ms_med`).

## Sources and licenses

- [code] pupil-apriltags 1.0.4.post11, [github.com/pupil-labs/apriltags](https://github.com/pupil-labs/apriltags):
  PyPI metadata says MIT; the wheel's LICENSE file also carries the AprilTag C code's
  BSD-2-Clause notice (University of Michigan). Both permissive. Used as installed.
- [code] AprilTag 3, hub record [aprilrobotics/apriltag](../../catalog/repos/aprilrobotics__apriltag.md)
  (BSD-2-Clause per the hub record). Its build note flags pose ambiguity on small or far tags
  near frontal views; this sample measures it.
- [code] OpenCV 5.0.0 (opencv-python-headless, Apache-2.0): `cv2.aruco` `DICT_APRILTAG_36h11`
  for the tag bitmap, `warpPerspective` for rendering. numpy (BSD-3-Clause).
- [paper] Wang and Olson, AprilTag 2, IROS 2016, hub record
  [wang-olson-2016-apriltag2](../../catalog/resources/wang-olson-2016-apriltag2.md). Not read for
  this sample; no number here comes from it.
- [docs] PX4 precision landing, hub record [px4-precision-landing-docs](../../catalog/resources/px4-precision-landing-docs.md),
  for the LANDING_TARGET hand-off; not exercised here.
