# Sample: UGV GNSS outage on a real log: wheel odometry + IMU, innovation gate, drag detector

`sample:ugv-gnss-outage-real` - code and walkthrough in [samples/ugv-gnss-outage-real](../../samples/ugv-gnss-outage-real/)

Stdlib-only ground-vehicle loop on a real NCLT Segway session (2013-01-10, 1022 s, 1139 m, 42 MB download): consumer GPS at 1 Hz fused with MEMS strapdown INS (the 8-state EKF of gnss-ins-ekf-outage, imported), wheel speed + MEMS gyro, or wheel speed + KVH fibre-optic gyro. Measures dead-reckoning drift through injected 10/30/60/120 s outages and one real 39.6 s GNSS gap against NCLT SLAM truth, what a chi-square innovation gate does with real multipath, and detection time of an injected coherent drag (synthetic attack on real fixes) for the gate and an odometry-vs-GNSS displacement test, with false alarms on the clean log.

**Verification:** Ran 2026-11-06 with /opt/homebrew/bin/python3 3.14.7, stdlib only (run with -I). fetch_nclt.py downloaded and sha256-verified groundtruth_2013-01-10.csv (20.7 MB) and 2013-01-10_sen.tar.gz (21.7 MB) from the NCLT S3 bucket in ~27 s; ugv_loop.py (all four reports, ~26 s) output saved in results/all-2013-01-10.txt and quoted in the README. Sensor conventions checked against truth (gyro z slope 0.994, KVH rate sign, wheel scale 1.07). 11 unittest tests pass with data, 7 pass + 4 skip without data; mutations (inert gate, zero drag) make the gate and drag tests fail. One session only; truth is NCLT SLAM which fuses the same wheel odometry; the drag is a position offset on recorded fixes, not an RF spoof. robot_localization, DRIFT and KF-GINS were not run.

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `ugv`, `wheel-odometry`, `dead-reckoning`, `fog`, `ekf`, `innovation-gate`, `chi-square`, `multipath`, `gnss-outage`, `spoofing`, `drag`, `real-data`, `nclt`, `stdlib`

## Related

- uses: [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../../catalog/samples/gnss-ins-ekf-outage.md)
- uses: [The University of Michigan North Campus Long-Term Vision and LIDAR Dataset](../../catalog/resources/umich-nclt-dataset.md)
- explains: [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md)
- explains: [DRIFT](../../catalog/repos/umich-curly__drift.md)
- explains: [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
