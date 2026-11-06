# Cheat sheet: swarm and cooperative navigation

Briefs like "swarm relative localization without GNSS", "team keeps a shared picture",
"coordination under GNSS denial" (EUDIS 2026 common challenge). Decoder rows 10, 11.

## 1. What judges likely want (30 s)

The team keeps one shared estimate when GNSS and some links are gone, and each agent knows how
sure it is. Coordination demos hide weak localization, so judges who know the field will ask
for both: localization error and task outcome, with a defined behaviour on comms loss.

## 2. The demo in 24-48 h

Six vehicles, two with GNSS, UWB ranges between them: centralized EKF vs covariance
intersection, spoofed-anchor detection. Then the same filters on real MILUV inter-drone UWB.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [swarm-coop-localization](../../samples/swarm-coop-localization/) | ran | stdlib | none, ~10 s | `python3 coop_loc.py` |
| [swarm-coop-real-uwb](../../samples/swarm-coop-real-uwb/) | ran | stdlib | 31.4 MB in ~1 min (54.6 MB for all three experiments); stats < 2 s, nominal ~2 min, each fault run ~3 min | `python3 fetch_miluv.py && python3 run_real.py stats && python3 run_real.py fault` |

Task allocation (row 11) has no sample: start from the
[gym-pybullet-drones card](../integration-cards/learnsyslab__gym-pybullet-drones.md) and
[CBBA](../../catalog/repos/inmo-jang__consensus-based-bundle-algorithm.md) on top of the
[project-repo](../../templates/project-repo/) template.

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | How many agents, which radios, sim or hardware? Coordination scored? | ADR-001: team RMSE + task outcome + comms budget |
| Nav | Both samples green | Pick centralized vs CI from bandwidth and robustness |
| Platform | MILUV fetch; gym-pybullet-drones if coordination is scored | Comms-loss model (drop rate, who becomes anchor) |
| Viz (4-5) | Per-agent position + circle on a map | Link graph overlay, dropped agents greyed |
| Pitch (5) | Threat model: GNSS spoof on the anchor, jammed links, biased peer | State the open gap (biased peer) up front |

## 4. Numbers you can cite

- Team RMSE: dead reckoning 49.1 m, centralized robust 2.0 m, covariance intersection 5.5 m;
  bandwidth 138.1 vs 24.0 B/s per agent. **Synthetic** UWB, 10 seeds.
- Real UWB in flight: robust sd 0.09-0.12 m (the sim assumed 0.10 m), max 1.9 m in 32 k ranges.
  **Real** (MILUV, 3 drones, 6 anchors), 3 experiments.
- Biased anchor ranges on one drone: centralized solution separation detected 30/30 at median
  42 s, 0 false alarms in 30 clean runs. **Real** ranges, injected fault.

## 5. Top traps

1. A biased peer is not handled by any shipped monitor: the denied drone was dragged to 2.6 m
   RMSE (DR alone 0.55 m), CI to 11.0 m. A gap, not a result to pitch.
2. The sim's NLOS model is far heavier than real line-of-sight flights (sim 9 % of ranges beyond
   5 m), and MILUV is one indoor arena. Odometry in the real-UWB sample is synthetic, so absolute
   RMSE scales with the assumed odometer; quote ratios.
3. Multi-robot SLAM stacks are heavy for 48 h: keep it 2D range + odometry. Sim comms are a
   Bernoulli loss model, no latency or out-of-order messages.

## 6. Stretch goal

A peer-fault monitor that catches the biased inter-drone ranges the shipped monitors miss
(peer votes flag it in 19/30 at median 87 s today). Or decentralized task allocation that keeps
working when half the links drop, scored together with localization error.

## 7. Links

- Decoder: [rows 10, 11](../problem-statement-decoder.md#the-table); evidence:
  [section 9](../evidence-matrix.md#9-swarm), spoofed anchor in
  [section 1](../evidence-matrix.md#1-gnss-spoof-detection-on-a-vehicle).
- Cards: [GTSAM](../integration-cards/borglab__gtsam.md),
  [gym-pybullet-drones](../integration-cards/learnsyslab__gym-pybullet-drones.md),
  [Crazyflie firmware](../integration-cards/bitcraze__crazyflie-firmware.md),
  [ego-planner-swarm](../integration-cards/zju-fast-lab__ego-planner-swarm.md).
- Datasets: [MILUV](../dataset-cards/miluv.md), [UTIL UWB TDoA](../dataset-cards/util-uwb-tdoa.md).
