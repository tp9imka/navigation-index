# Cистема визуально-инерциальной навигации для дрона на C++

`res:habr-kodoka-mvio-cpp-2026` - blog - <https://habr.com/ru/articles/993694/>

**By:** kodoka (Habr) - **Year:** 2026 - **Level:** intermediate - **Access:** open

English: 'A visual-inertial navigation system for a drone in C++'. Walks through a monocular VIO built with OpenCV and Eigen: per-camera intrinsic calibration, ORB detection with Lucas-Kanade tracking at 30 Hz (SIFT judged too slow on a Raspberry Pi), parallax-based keyframes, essential-matrix initialisation then PnP, IMU preintegration, QR least-squares for scale and gravity with sanity bounds, and a 15-state ESKF. Includes a demo GIF; no quantitative accuracy is reported.

## Key takeaways

- Track with optical flow, detect with ORB: descriptor matching every frame is too slow on small boards
- Accept scale/gravity solutions only inside physical bounds (gravity near 9.81)
- ESKF states: position, velocity, attitude error, accel and gyro biases
- Code: RusaUB/mvio

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `lang:ru`, `habr`, `vio`, `eskf`, `opencv`

## Related

- has_code: [MVIO - monocular visual-inertial odometry in C++](../../catalog/repos/rusaub__mvio.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
