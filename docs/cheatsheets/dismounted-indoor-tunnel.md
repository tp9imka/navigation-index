# Cheat sheet: dismounted, indoor, tunnel

Briefs like "soldier / first responder navigation indoors or underground", "squad on foot",
"basement, stairwell, multi-storey", "tunnel". Decoder row 9; on wheels or rails, row 14.

## 1. What judges likely want (30 s)

A squad's positions stay on the shared map with no GNSS, and the error circle tells the truth.
Judges want error per distance walked on real IMU data, occasional absolute updates (door, floor,
UWB anchor), and growing uncertainty shown to the operator, not a confident dot.

## 2. The demo in 24-48 h

Foot-mounted ZUPT INS on 36 real pyshoe trials, aided by corridor heading, floor height and
UWB, positions out as CoT with the error circle. Real UWB between team members from MILUV if the
brief says "team".

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [dismounted-foot-ins](../../samples/dismounted-foot-ins/) | ran | stdlib (pyshoe cross-check: separate Python 3.11 venv) | ~120 MB over FTP, about 15 min: start it first; filter table ~3 min, all tables ~12 min | `sh fetch_data.sh && python3 run_hallway.py data/hallway --tables filter --jobs 8` |
| [swarm-coop-real-uwb](../../samples/swarm-coop-real-uwb/) | ran | stdlib | 31.4 MB in ~1 min | `python3 fetch_miluv.py && python3 run_real.py stats` |
| [mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/) | ran | stdlib | none | `python3 -m unittest -v test_cot && python3 cot.py` |

Tunnel on wheels: [relative-nav-benchmark](../../samples/relative-nav-benchmark/)
`PY=$PWD/.venv/bin/python RELNAV_DATA=$PWD/data ./run.sh lidar` (venv, Python 3.12, KITTI 04
1.13 GB) measures odometry drift only; nothing in the hub runs wheel odometry + IMU + a GNSS gate
on recorded data.

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Body-worn IMU or phone? Anchors / floor plan provided? | ADR-001: metric = ARMSE and % of markers inside the 95 % circle |
| Nav | Start `fetch_data.sh` at minute 1 | Filter table; switch to `ins15_py_yrw` for honest covariance |
| Platform | Phone / IMU logging app if hardware exists | Adapter for the provided log format |
| Viz (4-5) | TAK with CoT `ce` growing | Floor plan overlay, per-member circles |
| Pitch (5) | Threat model: no GNSS, no magnetometer trust indoors | Read the sample's limits; licence: pyshoe has no licence file |

## 4. Numbers you can cite

- Stdlib ZUPT EKF: mean ARMSE 2.2-2.35 m (depends on the download), final error 1.30 % of
  214.6 m. **Real** pyshoe hallway set, 36 trials.
- The default filter's 95 % circle covers the truth at 31 % of markers; `ins15_py_yrw` 60 %, same
  accuracy. **Real**, 36 trials.
- Magnetometer heading indoors: position 2-9x worse, max error up to 28.44 m. **Real** raw logs,
  6 trials.

## 5. Top traps

1. The filter is overconfident by default. Say which config you used and show coverage, not just
   ARMSE.
2. Aided result (1.07 m) uses **simulated** UWB (4 anchors, 30 % NLOS), tuned on an 18-trial
   subset with no held-out set. Every trial walks the same L-shaped route.
3. Flaky data hosts (pyshoe FTP ~15 min); pyshoe's own code needs Python 3.11 and numpy < 1.24
   ([upstream finding 14](../upstream-findings.md#14-pyshoe-numpy--124-licence-trial-count)).
   Do not trust the magnetometer indoors.

## 6. Stretch goal

Real UWB between members: [swarm-coop-real-uwb](../../samples/swarm-coop-real-uwb/) took a
denied drone from 0.484 m (DR) to 0.198 m RMSE with real MILUV ranges (synthetic odometry). Port
that update into the foot INS and show a member kept on the map by peers. Or show the 95 % circle
actually covering 95 %.

## 7. Links

- Decoder: [rows 9, 14](../problem-statement-decoder.md#the-table); evidence:
  [section 8](../evidence-matrix.md#8-dismounted), [section 5](../evidence-matrix.md#5-relative-navigation-and-drift-without-gnss).
- Cards: [PyShoe](../integration-cards/utiasstars__pyshoe.md),
  [FilterPy](../integration-cards/rlabbe__filterpy.md), [PyTAK](../integration-cards/snstac__pytak.md),
  [KISS-ICP](../integration-cards/prbonn__kiss-icp.md),
  [robot_localization](../integration-cards/cra-ros-pkg__robot_localization.md),
  [Nav2](../integration-cards/ros-navigation__navigation2.md).
- Datasets: [PyShoe](../dataset-cards/pyshoe.md),
  [Indoor Location 2.0](../dataset-cards/indoor-location-2020.md),
  [Hilti 2022](../dataset-cards/hilti-slam.md), [SubT](../dataset-cards/subt-datasets.md),
  [MILUV](../dataset-cards/miluv.md), [KITTI](../dataset-cards/kitti.md).
