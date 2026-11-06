# Cooperative localization for a GNSS-denied team

<!-- about: repo:eth-pbl/swarm-relative-localization, res:li-onboard-relative-localization-swarms, repo:lijx10/uwb-localization, repo:hkust-aerial-robotics/omni-swarm, repo:decargroup/miluv, res:util-uwb-dataset, res:ion-webinar-gross -->

## Goal

Six vehicles fly together. Only two keep GNSS; the rest have drifting odometry. They range
to each other over UWB and talk over a lossy mesh. This sample answers, in stdlib Python
with runnable numbers:

- how much inter-agent ranging buys over dead reckoning;
- what a centralized joint EKF costs in bandwidth vs a decentralized filter;
- why the naive decentralized filter (treat the neighbour's estimate as independent) breaks,
  and what covariance intersection (CI) costs in accuracy to fix it;
- what robust ranging (gate + Huber + an NLOS-aware side) does against NLOS and outliers;
- what happens to the whole team when one anchor's GNSS is spoofed, with and without
  integrity checks.

Everything is simulated. No real UWB data or flight log was used; see [Limits](#limits).

## Run

```bash
python3 coop_loc.py                                # nominal, seed 1, ~10 s
python3 coop_loc.py --bearing                      # add camera relative bearings
python3 coop_loc.py --scenario spoof               # agent 0 GNSS walked off from t=300 s
python3 coop_loc.py --scenario spoof --bearing
python3 coop_loc.py --seeds 10                     # Monte Carlo (add --scenario spoof / --bearing)
python3 coop_loc.py --scenario spoof --csv out/csv # per-method time series CSV
python3 -m unittest -v test_coop_loc               # 20 tests, 10-40 s
```

Other knobs: `--agents`, `--gnss 0 1 2`, `--loss`, `--comm-range`, `--max-links`,
`--spoof-rate`, `--timeseries` (per-agent table for every method). Python 3.10+, no
third-party packages. Saved outputs of the runs below are in `out/`.

## What it simulates

| Item | Value (all in `sim.Config`) |
|---|---|
| Team | 6 agents, 2-D, 600 s, 1 epoch/s. Formation centre at 5 m/s on a gentle S-curve; agents on a 100 m ring with 40 m per-agent wander, so links come and go |
| Odometry | per-agent constant scale error N(0, 2 %) and heading error N(0, 1.5 deg) + 0.1 m/s white noise. Seed 2 draws a -5.5 deg heading error for agent 2 (300 m DR drift) |
| GNSS | agents 0 and 1 only, 3 m noise (filter assumes 3.5 m) |
| UWB two-way ranging | 0.10 m noise (filter assumes 0.15 m), max 200 m, 15 % dropout, `max_links`=3 ranging slots per agent per epoch (TDMA budget) |
| NLOS | per pair Markov episodes (enter 2 %/s, exit 10 %/s), +1..8 m bias; 3 % gross outliers +5..30 m. Both only lengthen ranges |
| Camera bearing (`--bearing`) | world-frame bearing to the ranged peer, 2 deg noise, within 120 m, 50 % availability, initiator only |
| Mesh | 250 m comm range, 10 % packet loss per hop, BFS multi-hop to the fusion centre (agent 1) |
| Spoof | agent 0 GNSS walks off at 0.5 m/s, 45 deg, from t=300 s (150 m at the end) |

Seed 1 draws: 6816 ranging attempts, 1036 dropouts, 5780 ranges of which 835 NLOS-biased and
171 gross outliers; 15665 of 18000 broadcast receptions; 3310 of 3600 uplinks reached the
fusion centre, mean 1.03 hops.

## Estimators

Per-agent state `[px, py, bx, by]`: position plus a world-frame odometry bias, so a
mis-scaled or mis-aligned odometer is learnt from GNSS or ranges.

| Name | What it does | Messages |
|---|---|---|
| `dead-reckoning` (a) | no cooperation; GNSS agents fuse own GNSS, others integrate odometry | none |
| `central-plain` / `central-robust` (b) | one 24-state EKF at agent 1 with exact cross-covariances; every agent uplinks odometry, GNSS and its ranges multi-hop; the centre floods all estimates back | uplink 4+8+8+5/range B x hops, downlink 6x20 B per reached agent |
| `naive-robust` | decentralized; agent a fuses range to o as if o's broadcast `(x_o, P_o)` were independent of a | 24 B broadcast per agent per epoch |
| `ci-plain` / `ci-robust` (c) | decentralized CI on the joint `[x_a; p_o]` with `P = blkdiag(P_a/w, P_o/(1-w))`, which bounds the true joint covariance for any cross-correlation; `w` minimises the prior-normalised trace of all four states | 24 B |
| `-robust` (d) | chi-square gate (1 dof, 99.9 %) + Huber reweighting (knee 1.5 sigma); ranges longer than predicted (the NLOS side) get a 3-sigma gate and a 1-sigma knee; 8 consecutive rejections inflate that agent's position covariance by 5 m (gate lock-out recovery) | - |

Integrity modes in the spoof scenario (all on robust ranging):

| Mode | Centralized | Decentralized (CI) |
|---|---|---|
| `none` | - | - |
| `gate` | chi-square gate (2 dof, 99.9 %) per GNSS fix | same, on each GNSS agent's own filter |
| `vote` | - | each agent tests ranges to a peer against the peer's broadcast (short side at the gate, long side with 10 m NLOS slack); 3 fails in 5 => flag in its broadcast; 2 distinct peers flagging an agent => team ignores it, it drops its GNSS and widens its covariance |
| `ss` | solution separation: one sub-filter per GNSS agent that excludes that GNSS; a fix that disagrees with its sub-filter in 3 of 5 epochs is excluded and the main filter is replaced by that sub-filter | distributed SS: every agent also runs one filter copy per GNSS agent g that never uses anything derived from g's GNSS and broadcasts it (+20 B per copy). Agent g tests its fix against its own copy (only while that copy's sigma is under 10 m). With two GNSS sources an alarm is detectable but not attributable, so both GNSS are dropped and every agent widens its covariance by 30 m and coasts |

## Results, seed 1 (verbatim from `out/`)

Nominal, range only (`out/nominal.txt`). NEES is the mean of `e^T P^-1 e`; 2.0 means the
reported covariance matches the actual error.

```
method                   RMSE  denied  final     max     NEES  B/s/ag   rej
dead-reckoning           28.5    34.9   37.5    85.6      0.6     0.0     0
central-plain             9.5    11.2    1.1    38.1    127.4   137.8     0
central-robust            1.7     2.0    0.5     9.6      3.7   137.8   950
naive-robust             21.6    26.2   29.2    65.8   6504.6    24.0  4911
ci-plain                  6.6     8.0    1.2    36.2      2.5    24.0     0
ci-robust                 5.1     6.3    0.8    35.8      1.4    24.0   405

Per-agent RMSE (m)
method                     a0*     a1*      a2      a3      a4      a5
dead-reckoning             1.1     1.0    25.5    50.8    35.4    19.5
central-robust             0.8     0.7     2.3     1.6     1.6     2.3
ci-robust                  1.1     1.0     5.9     7.0     7.4     4.3
```

Error over time (m), selected rows:

```
dead-reckoning                                 ci-robust
    t   a2    a3    a4    a5                       t   a2    a3    a4    a5
  120  8.9  18.2  10.8   6.4                     120  1.6   1.9   4.2   1.9
  300 22.4  44.1  29.8  17.1                     300  2.3   1.6   1.2   1.5
  600 43.2  85.6  62.8  32.9                     600  2.4   0.5   0.5   0.6
```

Spoofing, range only (`out/spoof.txt`). Columns from t=300 s; "others" = the five
unspoofed agents.

```
method                     a0 RMSE  others  oth max  oth end  pre RMSE  B/s/ag  detections (t, agent)
dead-reckoning                86.6    41.0     85.6     45.0      14.6     0.0  -
central-robust                82.1    67.6    188.1     92.2       1.8   137.8  -
central-robust+gate            3.5     4.1     10.2      2.6       1.8   137.8  -
central-robust+ss              1.9     2.5      8.9      2.8       1.8   137.8  (334,0)
ci-robust                     86.6   155.9    435.8    257.2       6.1    24.0  -
ci-robust+gate                86.6   155.9    435.8    257.2       6.1    24.0  -
ci-robust+vote                42.9    74.8    237.0     93.2       6.1    24.0  (348,0), (561,5), (567,2), (572,5) ...
ci-robust+ss                  71.5   131.8    378.3    241.1       6.1    55.0  (465,0)
```

Spoofing with camera bearings (`out/spoof_bearing.txt`):

```
method                     a0 RMSE  others  oth max  oth end  pre RMSE  B/s/ag  detections (t, agent)
central-robust                84.9     8.3     20.0      4.4       1.1   138.7  -
central-robust+ss              0.9     1.6      8.2      2.9       1.1   138.7  (323,0)
ci-robust                     86.3    96.7    269.0    115.4       5.9    24.0  -
ci-robust+vote                86.3    85.6    158.7    151.7       5.4    24.0  (314,1), (400,1)
ci-robust+ss                  29.1    27.2     54.3     48.9       5.9    46.2  (333,0)
```

How the spoof propagates (m, range only, `central-robust` with no check vs `+ss`):

```
            no integrity                         solution separation
    t    a0     a1     a2     a3     a4     a5       a0   a1   a2   a3   a4   a5
  300   0.7    0.3    0.5    1.0    0.8    0.9      0.7  0.3  0.5  1.0  0.8  0.9
  360  15.5   11.2    2.2   11.3   18.0   17.0      1.4  0.5  1.1  2.1  2.6  1.5
  480  84.4    1.7   44.3   71.3   95.4  106.6      0.9  0.2  1.2  1.3  2.1  2.2
  600 147.6    3.9   57.7   59.2  173.7  166.7      3.1  0.8  2.5  4.9  3.1  2.8
```

## Results, 10 seeds

Nominal (`out/mc_nominal.txt`, `out/mc_nominal_bearing.txt`): mean [min, max] over seeds.

```
range only                          team RMSE             denied RMSE    NEES  B/s/ag
dead-reckoning            49.1 [  28.5,   71.0]    60.1 [  34.9,   87.0]     0.9     0.0
central-plain             15.0 [   8.6,   25.8]    17.7 [  10.0,   30.8]   311.1   138.1
central-robust             2.0 [   1.5,    2.9]     2.4 [   1.7,    3.4]     4.7   138.1
naive-robust              15.5 [   5.1,   29.3]    18.4 [   5.1,   35.7]  4742.7    24.0
ci-plain                   8.9 [   5.1,   22.6]    10.8 [   6.2,   27.6]     5.2    24.0
ci-robust                  5.5 [   3.9,   10.6]     6.7 [   4.7,   12.9]     2.0    24.0

with bearings
central-robust             1.7 [   1.3,    2.7]     1.9 [   1.5,    3.1]     4.7   139.1
ci-robust                  4.6 [   3.9,    6.2]     5.6 [   4.7,    7.5]     1.8    24.0
```

Spoofing (`out/mc_spoof.txt`, `out/mc_spoof_bearing.txt`):

```
range only                      spoofed a RMSE           others RMSE  det false       latency s  B/s/ag
dead-reckoning              86.4 [ 85.8,  86.9]    70.9 [ 41.0, 102.7]    0     0               -     0.0
central-robust              84.3 [ 82.1,  86.2]    67.7 [ 28.4,  98.5]    0     0               -   138.1
central-robust+gate         21.6 [  3.1,  86.0]    15.9 [  4.1,  61.8]    0     0               -   138.1
central-robust+ss            2.3 [  1.6,   4.7]     2.9 [  1.8,   5.9]    9     1   30 [ 24,  34]   138.1
ci-robust                   86.4 [ 85.9,  86.9]   131.0 [ 90.7, 178.2]    0     0               -    24.0
ci-robust+gate              86.4 [ 85.9,  86.9]   131.8 [ 92.3, 178.2]    0     0               -    24.0
ci-robust+vote              59.5 [ 13.0,  86.9]    79.8 [ 19.8, 134.8]    9     6   81 [ 35, 190]    24.0
ci-robust+ss                76.7 [ 56.9,  88.5]   133.8 [ 40.5, 191.7]    8     0  142 [ 65, 264]    56.6

with bearings
central-robust              84.9 [ 83.6,  86.1]    48.8 [  6.5,  93.6]    0     0               -   139.1
central-robust+gate          4.2 [  1.6,   9.1]     3.5 [  1.9,   6.4]    0     0               -   139.1
central-robust+ss            2.3 [  0.9,   5.0]     2.4 [  1.6,   4.5]   10     0   28 [ 23,  37]   139.1
ci-robust                   86.4 [ 85.9,  86.9]   101.0 [ 62.6, 129.8]    0     0               -    24.0
ci-robust+vote              68.6 [ 25.7,  91.5]    68.4 [ 11.0, 113.7]   10     0   63 [ 14,  84]    24.0
ci-robust+ss                40.5 [ 11.0,  81.9]    32.3 [  8.5,  68.1]   10     0   34 [ 31,  75]    46.7
```

`det` = seeds with a detection at or after spoof start, `false` = detections before it,
latency = median [min, max] seconds from onset to first detection. The `gate` mode does not
log detections (it rejects fixes one at a time). Centralized SS always blamed agent 0; the one
false alarm is seed 6 without bearings at t=49 s, while bias states were still converging -
it happened to exclude agent 0, after which no monitoring was possible. `vote` detections
include honest agents being voted out.

## Findings

1. **Ranging to two anchors bounds everyone.** DR error of the four GNSS-denied agents grows
   to 33-86 m in 600 s (seed 1); with UWB it stays at a few metres. 10-seed denied-agent
   RMSE: 60.1 m DR => 2.4 m centralized => 6.7 m CI.
2. **The bias state matters.** A first version with a position-only random walk locked out:
   one agent's -5.5 deg odometer pulled it outside the gate and every later range was
   rejected (54.7 m team RMSE on seed 2, development run). Estimating odometry bias, the
   NLOS-aware gate side and lock-out recovery together brought seed 2 to 2.9 m.
3. **Plain least squares is not usable with NLOS.** `central-plain` 15.0 m vs
   `central-robust` 2.0 m (10 seeds). The NLOS-aware side (tighter gate on long ranges)
   mattered: with a symmetric gate, development runs of central-robust gave 20.7 m on seed 2
   and 7.3 m on seed 3, vs 2.9 m and 2.1 m now.
4. **Naive decentralized fusion double counts.** NEES in the thousands, RMSE 15.5 m - worse
   than CI and on some seeds close to DR. Two agents ranging each other both reuse the same
   range and each other's already-correlated estimates.
5. **CI is consistent but conservative.** NEES 2.0 vs 4.7 for the centralized EKF (which is
   slightly overconfident: unmodelled NLOS that passes the gate), at roughly 2.5-3x the
   centralized error. It sends 24 B/s per agent instead of 138 B/s, needs no fusion centre
   and no multi-hop routing.
6. **A spoofed anchor is worse than no cooperation.** With no checks the unspoofed agents
   end up farther off than dead reckoning (seed 1: 67.6 m centralized, 155.9 m CI vs 41.0 m
   DR). The team trusts the spoofed agent's confident estimate and fights the honest anchor.
7. **Centralized solution separation contains it.** Detection 24-34 s after onset (12-17 m
   of offset), unspoofed agents at 2.9 m RMSE over 10 seeds vs 67.7 m unprotected; one
   pre-spoof false alarm in 10 range-only runs, none with bearings. A per-fix gate alone is
   seed-dependent (15.9 m, range 4.1-61.8): the odometry-bias state absorbs a slow ramp, so
   the innovation never crosses the gate on some seeds.
8. **Decentralized integrity is the hard part.** Peer votes misfire because the voters are
   themselves contaminated: 6 pre-spoof false votes in 10 range-only runs and honest agents
   voted out. Distributed SS with range only detects late (median 142 s): with one anchor
   left, a range-only CI network cannot hold the formation's rotation, so the reference copy
   is too loose to test against. With camera bearings the copy is tight enough: median
   detection 34 s, unspoofed agents 32.3 m vs 101.0 m unprotected, at +23 B/s per agent. It
   cannot tell which of two anchors lies, so the team coasts without GNSS afterwards and
   drifts. For a decentralized team, a third independent anchor (or a fusion centre for
   the integrity check only) is what makes attribution possible.

## Limits

- 2-D, constant-rate odometry, world-frame bearings (assumes known heading). No clock
  offsets, no TDoA, no antenna delay calibration, no altitude.
- NLOS model is a Markov positive bias, not a measured channel. Real UWB NLOS statistics
  (UTIL, MILUV) were not used.
- Communication is a per-epoch Bernoulli loss model with a TDMA slot cap; no latency,
  out-of-order or asynchronous messages. The UWB ranging exchange itself is not counted
  in the byte figures (same for all cooperative methods).
- The centralized uplink is assumed to deliver odometry reliably (only GNSS and ranges are
  lost with the packet); the decentralized flood of the SS alarm uses one bit in the
  broadcast and is modelled as hop-by-hop.
- After a two-source alarm nothing re-admits the honest anchor; a probation scheme like
  [altpnt-integrity](../altpnt-integrity/README.md) would.
- The spoof is a single slow walk-off on one anchor. Coordinated spoofing of both anchors,
  a meaconing replay, or a spoofed UWB peer are not modelled.
- No indexed repository was run. Their descriptions below come from the index and READMEs.

## Where to go next with real hardware or data

| Resource | Use |
|---|---|
| [MILUV devkit](https://github.com/decargroup/miluv) (`repo:decargroup/miluv`) | multi-UAV dataset with inter-robot UWB, vision and IMU: replace `sim.generate` with its ranges and ground truth |
| [UTIL UWB TDoA dataset](https://utiasdsl.github.io/util-uwb-dataset/) (`res:util-uwb-dataset`) | measured UWB NLOS/obstacle statistics to replace the Markov bias model |
| [ETH PBL swarm relative localization](https://github.com/ETH-PBL/swarm-relative-localization) (`repo:eth-pbl/swarm-relative-localization`) | infrastructure-less UWB relative localization on nano-drones |
| [Onboard ranging-based relative localization](https://arxiv.org/abs/2003.05853) (`res:li-onboard-relative-localization-swarms`) | onboard UWB + EKF relative localization for small quadrotors |
| [UWB Software Library](https://github.com/vladniculescu/uwb-software-library) (`repo:vladniculescu/uwb-software-library`) | DS-TWR and UWB data messaging between Crazyflies: the ranging + broadcast layer this sample assumes |
| [uwb-localization](https://github.com/lijx10/uwb-localization) (`repo:lijx10/uwb-localization`) | UWB + IMU fusion for MAV swarms (ROS) |
| [Omni-swarm](https://github.com/HKUST-Aerial-Robotics/Omni-swarm) (`repo:hkust-aerial-robotics/omni-swarm`) | decentralized visual-inertial-UWB swarm estimation |
| [CoLRIO](https://github.com/PengYu-Team/Co-LRIO) (`repo:pengyu-team/co-lrio`) | centralized lidar-ranging-inertial swarm estimation with UWB inter-robot ranges |
| [Cooperative localization for GNSS-denied subterranean navigation](https://www.ion.org/publications/webinar-gross.cfm) (`res:ion-webinar-gross`) | UAV-UGV team sharing ranging and odometry underground |
| [Saska, RSS 2024 aerial swarms](https://imrclab.github.io/workshop-aerial-swarms-rss2024/presentations/saska_RSS_swarms_2024_compress.pdf) (`res:saska-rss-2024-aerial-swarms`) | onboard relative localization in the field |

Background not in the index (worth adding): Julier and Uhlmann, "A non-divergent
estimation algorithm in the presence of unknown correlations" (ACC 1997) - the CI bound;
Carrillo-Arce, Nerurkar, Gordillo, Roumeliotis, "Decentralized multi-robot cooperative
localization using covariance intersection" (IROS 2013); Luft, Schubert, Roumeliotis,
Burgard, "Recursive decentralized localization for multi-robot systems with asynchronous
pairwise communication" (IJRR 2018).

## Files

| File | What |
|---|---|
| `sim.py` | truth, odometry, GNSS, UWB (dropout, NLOS, outliers), bearings, mesh and multi-hop draws; all randomness lives here |
| `filters.py` | DR, centralized EKF, naive / CI decentralized, robust ranging, lock-out recovery, gate / vote / SS integrity |
| `coop_loc.py` | runner: tables, time series, Monte Carlo, CSV |
| `test_coop_loc.py` | Jacobians vs finite differences, CI bound for random correlations, robust weighting, sim invariants, end-to-end ordering, spoof detection with a no-spoof false-alarm control and a monitor-off negative control |
| `out/` | saved outputs of the runs above, `csv_spoof/` per-method time series |
