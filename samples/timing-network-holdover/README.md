# A network of GNSS-disciplined clocks: holdover from peers, spoof isolation, ensemble time

<!-- about: sample:timing-holdover, repo:nwtime/linuxptp, repo:mlichvar/clknetsim, repo:tum-esi/ptpsec, repo:aewallin/allantools, res:ieee-1588-2019, res:itu-t-g8271, res:rfc7384-time-protocol-security, res:meta-ptp-at-meta-2022 -->

## Goal

[timing-holdover](../timing-holdover/) answers how long ONE node holds time when GNSS goes
away or lies. This sample asks the same for a site network that can also compare clocks over
packet links (PTP-like two-way time transfer):

1. **Regional jamming.** Some nodes lose GNSS. Do they hold time better from peers over the
   network than alone, and for how long do they stay under 1 / 1.5 / 5 / 10 us?
2. **Time-push spoof on one node.** Does a cross-node consistency check catch and isolate it
   before its time reaches GNSS-denied nodes that take time from it? How fast, how many false
   alarms?
3. **All GNSS lost.** Does an ensemble weighted by Allan deviation beat following the best
   single clock?
4. **Path asymmetry**, the blind spot of two-way time transfer: how much does it hurt?

Primer: [docs/timing-resilience.md](../../docs/timing-resilience.md).

## What it simulates

Everything is synthetic. Oscillator parameters come from datasheets via the parent sample;
network delays, asymmetries, PPS noise and the site layout are stated assumptions.

| Item | Value |
|---|---|
| Nodes | base-station (OCXO), radar (Rb), comms-relay (TCXO), c2-post (OCXO), sensor-north (CSAC), sensor-south (TCXO) |
| Oscillators | imported from `../timing-holdover/timing_holdover.py`: white FM at ADEV(1 s), linear aging, 24 h temperature sinusoid at 10 % of spec with a random phase per node. TCXO/OCXO/Rb from Vig table 1, CSAC from the Microchip SA65 datasheet (see parent README). Initial frequency offset one year of aging, as in the parent |
| GNSS discipline | parent's type-2 PLL and time-constant rule (crossover of 20 ns PPS noise and oscillator noise, temperature-ramp cap) |
| Links (8) | 3 fiber (asymmetry 30-60 ns, queueing 0.2-0.4 us mean, 8 ns timestamp noise), 2 microwave into the relay (asym +250 / -150 ns, queueing 1-2 us), 3 tactical radio (asym 200-400 ns, queueing 2-5 us, 50 ns timestamps). All synthetic |
| Two-way exchange | 16 Sync and 16 Delay_Req per second per link (the G.8275.1 telecom-profile rate per [Nokia](https://infocenter.nokia.com/public/7705SAR234R1A/topic/com.nokia.basic-system-guide/itu-t-g-8275-1-g-8275-2.html) and [Cisco](https://cisco.com/c/en/us/td/docs/routers/asr920/b_Chassis_Guide_asr920/gnss.html) docs). Queueing delay is exponential per direction; per step the lucky-packet (minimum-delay) filter, or a plain mean for comparison. offset = (x_a - x_b) - asym/2 + (q_rev - q_fwd)/2 |
| Asymmetry calibration | optional: during the last hour with GNSS on both ends, each link's mean offset is learned as its bias and subtracted later |
| Holdover from peers | GNSS-less node freezes its steering (mean of the last 10 min, as the parent) and tracks the summed path offset to the nearest GNSS-locked trusted node (fewest hops, best grade on ties, BMCA-like) with a type-2 tracker; output = oscillator minus tracked offset |
| Best single clock / ensemble | all GNSS lost: every node tracks the best clock (by the same ADEV model: the Rb), or a paper-clock ensemble: weighted mean of all held-over oscillators with weights 1/sigma_y(24 h)^2, sigma_y^2 = adev1^2/tau + (D tau)^2/2 + (temp swing)^2/2 |
| Consistency check | every 10 s, edge offsets between GNSS-locked trusted nodes minus their 1 h training baseline; weighted least squares node offsets, anchored at the median; node alarm when its residual exceeds 6x its training RMS + 50 ns for 3 consecutive checks |
| Guard | on alarm the node is distrusted: steering frozen at its value 30 min earlier (parent's rule), it takes time from peers, and nobody uses it as a time source |
| Budgets | 1 us; 1.5 us = ITU-T G.8271 accuracy level 4 (LTE-TDD, NR TDD); 5 us = level 3 (LTE-TDD, cells of 3 km or more); 10 us = no standard row, an illustrative coarse budget (3 km of TDOA range at 0.3 m/ns). Levels as summarised by [Calnex's G.8271 page](https://calnexsolutions.atlassian.net/wiki/spaces/GDW/pages/9437354/ITU-T+G.8271+General+One-Page+Summary); level 5 there is 1 us and level 6 below 0.5 us. Check the [ITU text](../../catalog/resources/itu-t-g8271.md) before quoting |

Step: 5 s for (a) and (c), 1 s for (b).

## Repos this sample explains

| Repo | Use it for |
|---|---|
| [linuxptp](https://github.com/nwtime/linuxptp) | the real two-way exchange, servo and BMCA; `delayAsymmetry` in `ptp4l.conf` is where a calibrated link bias goes |
| [clknetsim](https://github.com/mlichvar/clknetsim) | next step up: runs the real chrony / ptp4l daemons against simulated clocks and networks instead of this sample's toy servo |
| [PTPsec](https://github.com/tum-esi/ptpsec) | detecting delay attacks with redundant paths, the attack this sample's asymmetry table is about |
| [allantools](https://github.com/aewallin/allantools) | measure your own oscillators' ADEV before trusting the weights here |

## Prerequisites

Python 3.10+ (run on 3.14.7). No third-party packages. Needs the sibling `../timing-holdover/`.

## Run

```bash
cd samples/timing-network-holdover
python3 timing_network.py                         # all studies, about 50 s
python3 timing_network.py --only b                # spoof study only, about 10 s
python3 timing_network.py --temp-fraction 0       # no temperature term
python3 timing_network.py --trace te.csv --json out.json   # TE vs time per node (one seed) + all numbers
python3 -m unittest -v test_timing_network        # 10 tests, about 3 s
```

## Output (ran on 2026-11-06, Python 3.14.7, default arguments, 51 s)

Link and node lines trimmed.

```
temperature fraction 0.1, PPS noise 20 ns, 16 sync packets/s, min filter

(a) Regional jamming: comms-relay, sensor-north, sensor-south lose GNSS for 24 h after 6 h of discipline
    |TE| median (p95) over runs at 1 h / 4 h / 24 h; then median time staying under each budget
  alone
    comms-relay   TCXO   10.40 us ( 27.12 us)  230.87 us (373.18 us)    4.18 ms (  4.33 ms)
                        <1 us: 18 min  <1.5 us: 22 min  <5 us: 42 min  <10 us: 59 min
    sensor-north  CSAC       7 ns (    31 ns)     115 ns (   225 ns)    1.94 us (  3.80 us)
                        <1 us: 10.4 h (1/10 never exceed)  <1.5 us: 14.0 h (3/10 never exceed)  <5 us: whole 24 h  <10 us: whole 24 h
    sensor-south  TCXO   14.99 us ( 26.81 us)  260.85 us (371.14 us)    3.61 ms (  4.24 ms)
                        <1 us: 13 min  <1.5 us: 16 min  <5 us: 33 min  <10 us: 48 min
  peers, uncalibrated
    comms-relay   TCXO     126 ns (   149 ns)     239 ns (   315 ns)     120 ns (   173 ns)
                        <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
    sensor-north  CSAC     296 ns (   320 ns)     297 ns (   322 ns)     297 ns (   333 ns)
                        <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
    sensor-south  TCXO      51 ns (    99 ns)     154 ns (   230 ns)      28 ns (    74 ns)
                        <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
  peers, calibrated
    comms-relay   TCXO       6 ns (    21 ns)     165 ns (   218 ns)      22 ns (    70 ns)
                        <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
    sensor-north  CSAC      12 ns (    30 ns)      13 ns (    38 ns)      20 ns (    42 ns)
                        <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
    sensor-south  TCXO       7 ns (    26 ns)     165 ns (   187 ns)      35 ns (    64 ns)
                        <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h

(a2) Path asymmetry, extra delay on both microwave links into comms-relay; max |TE| of comms-relay 1-4 h after regional jamming, peer holdover, median of runs
  extra asym  uncalibrated  calibrated  calibrated, then route change
        0 ns        160 ns      181 ns                         181 ns
      500 ns        410 ns      181 ns                         276 ns
     1000 ns        660 ns      181 ns                         526 ns
     2000 ns       1.16 us      181 ns                        1.03 us
     4000 ns       2.16 us      181 ns                        2.03 us

(a3) Packet filter vs queueing asymmetry, uncalibrated, worst jammed node max |TE| 1-4 h after jamming
  min filter, PDV x1     310 ns
  min filter, PDV x4     261 ns
  mean filter, PDV x1    1.74 us
  mean filter, PDV x4    7.82 us

(b) Time-push spoof on one node's GNSS; sensor-north, sensor-south are GNSS-denied and take time from the network
    settle 2 h, consistency-check training 1 h, walk 2 h; dt 1 s
  node          ns/s  detected  det med s  det max s  clean isolation  downstream unguarded  downstream guarded  spoofed node guarded
  comms-relay      1    5/5         190.0      210.0            5/5                 7.20 us              164 ns                483 ns
  comms-relay      5    5/5          90.0       90.0            5/5                36.01 us              191 ns                496 ns
  comms-relay     50    5/5          50.0       50.0            5/5               360.05 us              332 ns                996 ns
  radar            1    5/5         520.0      600.0            5/5                  102 ns               99 ns                 82 ns
  radar            5    5/5         240.0      280.0            5/5                  102 ns              107 ns                 93 ns
  radar           50    5/5         100.0      110.0            5/5                  102 ns               95 ns                164 ns
  no-spoof control: 0 alarms in 20 runs (40 monitored hours)
  detection s = seconds after the walk starts; TE columns = median over runs of max |TE| during the walk

(c) All GNSS lost for 24 h. ADEV weights at tau = 24 h: base-station 0.052, radar 0.594, comms-relay 0.000, c2-post 0.052, sensor-north 0.301, sensor-south 0.000
    best single clock by the same model: radar
  alone     worst node |TE| median (p95): 1 h 18.23 us (27.24 us)  4 h 313.46 us (380.49 us)  12 h 2.50 ms (2.59 ms)  24 h 4.18 ms (4.33 ms)
            worst node time under budget: <1 us: 12 min  <1.5 us: 16 min  <5 us: 31 min  <10 us: 45 min
  best      worst node |TE| median (p95): 1 h 38 ns (49 ns)  4 h 239 ns (397 ns)  12 h 1.26 us (2.03 us)  24 h 2.27 us (2.68 us)
            worst node time under budget: <1 us: 9.8 h  <1.5 us: 13.5 h (2/10 never exceed)  <5 us: whole 24 h  <10 us: whole 24 h
  ensemble  worst node |TE| median (p95): 1 h 38 ns (59 ns)  4 h 202 ns (329 ns)  12 h 1.05 us (1.75 us)  24 h 1.13 us (2.54 us)
            worst node time under budget: <1 us: 10.7 h (1/10 never exceed)  <1.5 us: 22.5 h (5/10 never exceed)  <5 us: whole 24 h  <10 us: whole 24 h
  per node median |TE| at 24 h:
    base-station  OCXO  alone 6.34 us  best 2.24 us  ensemble 1.13 us
    radar         Rb    alone 2.24 us  best 2.24 us  ensemble 1.09 us
    comms-relay   TCXO  alone 4.18 ms  best 2.24 us  ensemble 1.10 us
    c2-post       OCXO  alone 4.42 us  best 2.25 us  ensemble 1.05 us
    sensor-north  CSAC  alone 2.04 us  best 2.24 us  ensemble 1.11 us
    sensor-south  TCXO  alone 3.61 ms  best 2.22 us  ensemble 1.08 us
```

Same (c) with `--temp-fraction 0` (9 s):

```
(c) All GNSS lost for 24 h. ADEV weights at tau = 24 h: base-station 0.002, radar 0.996, comms-relay 0.000, c2-post 0.002, sensor-north 0.000, sensor-south 0.000
    best single clock by the same model: radar
  alone     worst node |TE| median (p95): 1 h 204 ns (381 ns)  4 h 1.87 us (2.61 us)  12 h 15.68 us (17.79 us)  24 h 60.45 us (65.07 us)
            worst node time under budget: <1 us: 2.9 h  <1.5 us: 3.5 h  <5 us: 6.6 h  <10 us: 9.6 h
  best      worst node |TE| median (p95): 1 h 91 ns (126 ns)  4 h 90 ns (144 ns)  12 h 83 ns (151 ns)  24 h 68 ns (108 ns)
            worst node time under budget: <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
  ensemble  worst node |TE| median (p95): 1 h 90 ns (128 ns)  4 h 92 ns (143 ns)  12 h 83 ns (152 ns)  24 h 68 ns (110 ns)
            worst node time under budget: <1 us: whole 24 h  <1.5 us: whole 24 h  <5 us: whole 24 h  <10 us: whole 24 h
  per node median |TE| at 24 h:
    base-station  OCXO  alone 586 ns  best 28 ns  ensemble 26 ns
    radar         Rb    alone 29 ns  best 29 ns  ensemble 27 ns
    comms-relay   TCXO  alone 58.79 us  best 38 ns  ensemble 39 ns
    c2-post       OCXO  alone 584 ns  best 29 ns  ensemble 26 ns
    sensor-north  CSAC  alone 1.13 us  best 13 ns  ensemble 15 ns
    sensor-south  TCXO  alone 60.07 us  best 35 ns  ensemble 38 ns
```

## Reading the output

- **Peers vs alone (a).** A jammed TCXO alone leaves 1.5 us (5G TDD) after 16-22 min and
  reaches milliseconds in a day with the temperature term. Taking time from GNSS-locked peers
  over two hops of microwave and radio keeps all three jammed nodes under 1 us for the whole
  24 h in every run, uncalibrated (checkpoint p95 at most 333 ns). Peer holdover turns the problem from "oscillator grade" into
  "network error budget".
- **What is left is the path.** Uncalibrated, sensor-north sits at a steady 297 ns: half the
  400 ns radio-link asymmetry plus the relay hop. Calibrating the link biases while GNSS was
  still up removes it (12-20 ns). The TCXO nodes keep about 165 ns at 4 h with or without
  calibration: that is the tracker lagging the TCXO's temperature ramp, not the network.
- **Asymmetry is PTP's blind spot (a2).** Two-way time transfer assumes equal delays each way
  ([IEEE 1588](../../catalog/resources/ieee-1588-2019.md)); an unknown asymmetry `A` shifts the
  offset by `A/2` and nothing in the exchange reveals it. The table shows exactly that:
  +4 us of extra one-way delay => about +2 us of time error, uncalibrated or after a route
  change that happens after calibration. Calibration only helps until the path changes, and
  a delay attacker can make that change on purpose; crypto does not stop it
  ([RFC 7384](../../catalog/resources/rfc7384-time-protocol-security.md)). Calibrated links with
  no change are flat at 181 ns (the TCXO lag again).
- **Queueing asymmetry needs a lucky-packet filter (a3).** With 2-5 us of one-sided queueing
  on radio links, averaging all packets biases time by 1.7 us, and 7.8 us at 4x the load. Taking
  the minimum-delay packet out of 80 per step keeps it at 0.26-0.31 us.
- **Spoof on the relay (b).** The relay feeds both GNSS-denied sensors. Unguarded, a 50 ns/s
  push drags them 360 us in 2 h. The consistency check flags the relay after 50 s at 50 ns/s,
  90 s at 5 ns/s and 190-210 s at 1 ns/s, always isolating only the relay (5/5 per rate); the
  sensors re-anchor to c2-post and stay at 164-332 ns. The relay itself peaks at 0.5-1 us
  before isolation.
- **Spoof on the radar (b).** Nobody takes time from the radar while the others have GNSS, so
  nothing propagates (downstream 95-107 ns either way). The Rb's 2000 s loop follows the push
  slowly, which delays detection (100-600 s) but also keeps the radar's own error at
  82-164 ns: a good oscillator buys detection time.
- **False alarms.** 0 in 20 no-spoof runs, 40 monitored hours. That bounds the rate below
  about 0.075 per hour at 95 % (rule of three), nothing tighter.
- **Ensemble vs best clock (c).** With the 10 % temperature term the ADEV model gives the Rb
  0.59 and the CSAC 0.30 of the weight, and the ensemble halves the worst-node 24 h error
  (2.27 => 1.13 us median) because the two clocks' temperature cycles have independent random
  phases. Without temperature the weights collapse onto the Rb (0.996) and ensemble and best
  clock are the same (68 ns at 24 h). Either way network time is the big win over "every node
  alone" (4.18 ms or 60 us worst node).
- **Consistency with the parent.** Alone, no temperature, 24 h: CSAC 1.13 us, OCXO 0.58 us,
  Rb 29 ns, TCXO 59-60 us here vs 1.27 us, 0.61 us, 44 ns, 59.6 us in timing-holdover (20 runs
  there, 10 here).

## Limits and honest notes

- Fully synthetic. No PTP log, hardware, or real network was used; I did not find an open PTP
  offset log with known asymmetry cheap enough to use. Link asymmetries, queueing means,
  timestamp noise, the site layout and the 10 % temperature fraction are assumptions.
- Oscillators are white FM + aging + one temperature sinusoid (parent's model). No flicker
  FM, retrace, or vibration; OCXO long-tau noise is understated (see parent README).
- The ensemble gain in (c) depends on independent temperature phases. Co-located nodes share
  temperature, so their errors correlate and the gain shrinks. Weights assume the deployment's
  temperature fraction is known. No aging-rate estimation before the outage, for any mode.
- Packet delay is exponential and stationary per direction. Real PDV has load steps, route
  changes and heavy tails; real servos use more elaborate packet selection.
- The consistency check needs at least three GNSS-locked nodes with independent links. It
  sees nodes, not satellites: a regional spoofer that pushes all locked nodes together moves the
  median with them and is invisible to it. Combine with the parent's per-node steering monitor,
  an independent source, or OSNMA.
- Detection times are quantised by the 10 s check period and 3 consecutive hits (30 s minimum).
- Results are medians over 10 seeds (a, c), 5 seeds (b) and 3 seeds (a2, a3). Use `--seeds`.
