# Sample: AprilTag goal B: detection envelope vs range and view angle, and a tag-relative final approach

`sample:fiducial-goal-apriltag` - code and walkthrough in [samples/fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/)

Renders a tag36h11 AprilTag (0.16 m, also 0.40 m) onto a textured wall with a 640 x 480 pinhole camera (fx = fy = 500 px, no distortion) at known poses, with Gaussian blur and noise, detects it with pupil-apriltags, and reports detection rate, position error and tag-relative heading error (median, p95) per cell over 0.5-8 m and 0-70 deg view angle, with a heatmap PNG and the range where detection fails at each angle. final_approach.py closes the loop: a kinematic camera-equipped point mass starts 3 m off the tag axis at about 5 m, creeps until it sees the tag, then servos on the detected pose to a goal 1 m in front of the tag, rendering and detecting every 10 Hz frame with one frame of latency and velocity disturbance; final true error over 50 seeds. Pose-ambiguity heading flips are counted, not mitigated. All inputs synthetic; rolling shutter, exposure, lens distortion and motion-coupled blur are not modelled. numpy + opencv-python-headless + pupil-apriltags (MIT, with the AprilTag BSD-2-Clause notice).

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / opencv-python-headless 5.0.0.93 / pupil-apriltags 1.0.4.post11 on an Apple M3 Max: sweep.py ran with defaults (twice, identical detection-band summary), with --blur 1.5 --noise 6 and with --tag-size 0.40, each 1600 rendered frames; final_approach.py ran 50 seeds with default and with harsh image noise. Every number in README is from results/. test_smoke.py: 1 passed in the venv (render => detect => pose within 0.02 m / 2 deg at 2 m 40 deg, nothing detected at 8 m, one approach seed within 0.1 m), 1 skipped under plain python3 without numpy. All images and the vehicle are synthetic; no real camera, no real tag print, no SITL, no lens distortion or rolling shutter.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Rendered images and a kinematic point mass; no lens distortion, real camera or SITL. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested.

**Readiness evidence:** [samples/fiducial-goal-apriltag/README.md](../../samples/fiducial-goal-apriltag/README.md), [samples/fiducial-goal-apriltag/sample.json](../../samples/fiducial-goal-apriltag/sample.json), [samples/fiducial-goal-apriltag/results/final_approach.json](../../samples/fiducial-goal-apriltag/results/final_approach.json)

**Concepts:** [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `apriltag`, `fiducial`, `marker`, `landing-pad`, `precision-landing`, `relative-goal`, `visual-servoing`, `pose-ambiguity`, `pinhole-camera`, `synthetic-images`, `python`, `numpy`, `opencv`

## Related

- explains: [AprilTag 3](../../catalog/repos/aprilrobotics__apriltag.md)
- explains: [AprilTag 2: Efficient and robust fiducial detection](../../catalog/resources/wang-olson-2016-apriltag2.md)
- explains: [Precision Landing](../../catalog/resources/px4-precision-landing-docs.md)
- explains: [apriltag_ros (ROS 2)](../../catalog/repos/christianrauch__apriltag_ros.md)

## Referenced by

- [Challenge 2 "Autonomous Frontiers": entry point](../../docs/challenge-2-autonomous-flight.md) (mentions)
- [Cheat sheets: pick one in 30 seconds](../../docs/cheatsheets/README.md) (mentions)
- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area A=>B navigation: synthesis](../../docs/research/close-area-nav/README.md) (mentions)
- [Research rounds: which one applies, and the innovation story per brief](../../docs/research/README.md) (mentions)

_Indexed by lane(s): samples_
