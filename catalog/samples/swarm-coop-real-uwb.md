# Sample: Cooperative localization on real UWB: MILUV drones through the swarm-coop filters

`sample:swarm-coop-real-uwb` - code and walkthrough in [samples/swarm-coop-real-uwb](../../samples/swarm-coop-real-uwb/)

Runs the unmodified filters of swarm-coop-localization (dead reckoning, centralized EKF, naive decentralized, covariance intersection; plain vs robust ranging; gate / vote / solution-separation integrity) on real two-way UWB ranges from the MILUV dataset (3 quadcopters, 6 anchors, mocap truth). A stdlib HTTP-range reader pulls only the mocap, uwb_range and height CSVs out of 3-11 GB experiment zips. Two drones get 2-D fixes from multilateration of their own real anchor ranges, the third is denied and uses only real inter-drone ranges (horizontal projection with the height rangefinder) and synthetic odometry. Reports real range error vs the sim's UWB model, per-drone RMSE with real ranges and with the sim's error model on the same geometry, and detection time for a ramp bias on one drone's anchor ranges or on the denied drone's inter-drone ranges, with no-fault controls. Finding: the error core matches the sim (robust sd ~0.10 m) but the real tail stops at 1.9 m where the sim puts 9 % of ranges beyond 5 m, so robust ranging stops mattering; cooperative gain, CI consistency, faulty-anchor propagation and centralized solution separation all reproduce.

**Verification:** Ran 2026-11-06 with /opt/homebrew/bin/python3 3.14.7, stdlib only. fetch_miluv.py fetched the CSVs of default_3_zigzag_0, default_3_random_0 and cirObstacles_3_random_0 by HTTP range (31.4 + 12.6 + 10.6 MB over the wire from 11.1 / 3.2 / 3.2 GB zips). run_real.py stats / nominal / fault / fault --kind peer outputs saved in out/ and quoted in the README (30 runs per table: 3 denied-drone choices x 10 odometry seeds). Truth re-derived from mocap matches the devkit gt_range within 1 cm on 99.91 % of rows. 15 unittest tests pass with data, 7 pass + 8 skip without data; a mutation zeroing the injected fault makes the SS detection test fail. Not verified: real odometry (it is synthetic from mocap), lever-arm or 3-D models, comms, UTIL TDoA data, the MILUV devkit itself (not installed or run).

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `cooperative-localization`, `uwb`, `two-way-ranging`, `nlos`, `real-data`, `miluv`, `multilateration`, `covariance-intersection`, `ekf`, `solution-separation`, `integrity`, `fault-injection`, `http-range`, `stdlib`

## Related

- uses: [Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor](../../catalog/samples/swarm-coop-localization.md)
- uses: [MILUV devkit](../../catalog/repos/decargroup__miluv.md)
- uses: [MILUV: A Multi-UAV Indoor Localization dataset with UWB and Vision](../../catalog/resources/miluv-dataset-2025.md)
- explains: [UTIL: An Ultra-wideband Time-difference-of-arrival Indoor Localization Dataset](../../catalog/resources/util-uwb-dataset.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
