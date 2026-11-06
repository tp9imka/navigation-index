<!-- about: sample:two-source-integrity-vpair, sample:altpnt-integrity, sample:e2e-visual-nav-vpair, res:vpair-dataset-2022, res:geobasis-nrw-dom1-dgm1, res:copernicus-dem-aws, repo:stanford-gps-lab/maast_for_araim_2 -->
# Multi-source FDE: exclude the faulty source and keep navigating (VPAIR, ARAIM-style subsets)

[two-source-integrity-vpair](../two-source-integrity-vpair/README.md) showed that a second absolute
source makes solution-separation integrity available, and that faults are **detected**. It also showed
the limit of the reused altpnt monitor: with two sources the attribution follows the monitor's source
order, and with three sources "exclude the branch with the largest normalised separation" picked the
wrong source and gave 19 HMI epochs at AL 50 under a TRN ambiguity. Its open item was "ARAIM-style
subset exclusion (check each candidate subset's own consistency)". This sample implements that and
measures it on the same flight, against detection-only and against the max-separation rule.

```
nadir VO (real), heading +2 deg      drives every filter (dead reckoning, not a monitored source)
GNSS            simulated: VPAIR pose + 2 m white noise per axis, R 2.5 m, 1 Hz (altpnt v1 values)
visual fixes    real imagery, map stride 8, e2e cache          ../e2e-visual-nav-vpair
TRN lidar5      simulated heightmap over the real NRW 1 m DSM   ../two-source-integrity-vpair trn.py
TRN glo30       same sensor, real Copernicus GLO-30 map         ../two-source-integrity-vpair trn.py
filters         altpnt v2 EKF (heading/scale states), chi-square gate, one filter per subset of sources
FDE             fde.py (stdlib): detection, subset exclusion, ambiguity => unavailable, PL, readmission
```

Data loading, TRN simulation, visual fixes, the misregistration and TRN-ambiguity injections, the EKF
and the max-separation baseline are imported from the two-source and altpnt samples, not re-derived.
Two checks that the reuse is faithful: the GNSS-denied three-source baseline here reproduces
two-source's numbers exactly (nominal 84.7 % available at AL 50; TRN ambiguity **19 HMI** at AL 50).

**Real vs simulated:** flight, poses, VO and visual fixes are real (VPAIR). TRN sensors are simulated
from real terrain at the real poses. GNSS is simulated (VPAIR has no raw GNSS to replay). All faults are
injected.

## The method

Sources `gnss`, `vgeo` (visual), `trn` (LiDAR heightmap TRN), `trn2` (GLO-30 TRN). One EKF per subset
of them (16 filters, including VO-only) runs from GNSS loss to the end, each fusing VO plus its subset,
each with its own chi-square gate. The decision logic (`fde.py`) only chooses which filter is the output,
so detection-only and FDE variants replay the same bank.

With admitted set A and monitored fault hypotheses E (every subset of A with up to `max_faults` sources):

- **Detection:** any `|x_A - x_{A\E}| > T_E`, `T_E = K_fa * sigma(P_{A\E} - P_A)` plus the visual
  registration bias (altpnt v2 constants: P_FA 1e-5 split over hypotheses, sigma floor 0.5 m).
- **Exclusion:** for exclusion sizes 1..`max_faults`, every candidate E whose remaining set A\E passes
  **its own** detection test is consistent. Exactly one consistent candidate at the smallest size =>
  exclude it, and the output switches to filter(A\E), which has never seen the excluded source (no
  rewind). Two or more consistent candidates => `alert:ambiguous`, unavailable. None =>
  `alert:no-consistent-subset`, unavailable. The test is repeated every epoch, so an ambiguity can
  resolve later as the fault grows.
- **PL:** `max(K_ff sigma_A, max_E T_E + K_md(E) sigma_{A\E})` plus bias, K_md from the hypothesis
  prior (altpnt v2's per-source priors: GNSS 1e-2, visual 1.0e-2, TRN 6.3e-4; dual = product).
- **Readmission:** after 30 s hold, A + {s} must pass its full detection test for 45 consecutive
  epochs (altpnt's hold and probation times). Testing only the {s} branch was the first version; it
  readmitted a TRN whose fault had ended while another subset filter (visual + TRN, no GNSS) was still
  off from the fault period, and the next epoch excluded the healthy TRN again (`trn_ambiguity`, 3src, seed 2).
- **Detection-only:** same test, never excludes; unavailable while it trips.

`fde1` monitors single faults only, `fde2` single and dual. With these priors the dual hypotheses
are not negligible: their summed prior is 1.1e-4 (3 sources) and 1.3e-4 (4 sources), above the 1e-5
faulted-mode budget. An ARAIM design would have to monitor at least the GNSS + visual pair, so `fde1`
is the optimistic configuration and `fde2` the one that matches the stated priors.

## Run

```sh
# needs the two-source sample's data/ (fetch_terrain.py) and the VPAIR sample (relative-nav-benchmark/fetch_data.sh aerial)
DATA=../relative-nav-benchmark/data/vpair     # any dir containing vpair_sample/
<venv>/bin/python run_fde.py --data $DATA     # 164 s on M2 Max, 10 seeds x 7 scenarios, results/fde_result.json
python3 -m unittest discover                  # 17 tests; 3 need numpy + the two-source imports
```

Same venv as two-source (numpy, scipy, rasterio). `results/run_output.txt` is the console output of
the run below.

## Scenarios

188 frames after GNSS loss (8.53 km), frame = 1 s, 10 seeds (GNSS noise, TRN sensor noise and
particles; the visual fixes are one deterministic realisation).

| Scenario | Fault (frames) | Source |
|---|---|---|
| `nominal` | none | |
| `gnss_spoof` | drag-off 2 m/s along 120 deg from frame 60 to the end (276 m at the end) | here |
| `visual_misreg` | every visual fix offset along 45 deg, ramp 0 => 40 m over frames 100-139, held to the end | two-source `MISREG persistent` |
| `visual_wrong_place` | matcher locked on a place 60 m away (along 200 deg), frames 100-129 | here |
| `trn_ambiguity` | LiDAR TRN fixes replaced by the secondary peak of their own match surface, frames 60-99 (27-67 m off, mostly ~30 m, with nominal sigma) | two-source `AMBIG_FRAMES` |
| `double_spoof_trn` | `gnss_spoof` + `trn_ambiguity`, both from frame 60 | |
| `double_spoof_visual` | spoof from frame 100 + `visual_misreg` from frame 100 | |

Whether frames 60-99 are flatter than the rest of the track was not measured; the ambiguity is the
two-source injection (a real secondary peak forced onto the output), not an observed flat-terrain failure.

Source sets: `4src` = GNSS + visual + LiDAR TRN + GLO-30 TRN; `3src` = GNSS + visual + LiDAR TRN;
`alt3` = GNSS denied, visual + LiDAR TRN + GLO-30 TRN (two-source's three-source set). For `alt3`
the GNSS-only fault does not exist, so `alt3` rows are shown for the visual and TRN faults only
(`double_*` for `alt3` equals the single fault). `altpnt_maxsep` = altpnt v2 Monitor2, the rule
two-source reused (largest normalised separation, two-source alert and rewind), on the same inputs.

## Results

Outcome per run: **C** all faulty sources excluded and nothing else, **P** some faulty excluded,
nothing wrong, **W** a fault-free source excluded (counted even if a faulty one was too), **U** detected,
never excluded (unavailable instead), **M** never detected. Latency = first detection after onset, in
frames (s). Availability = PL < AL and no alert, averaged over seeds; "post" = from fault onset to the end.
HMI = epochs with error >= AL while available, summed over 10 seeds. MI was 0 in every non-baseline row.

### Exclusion outcomes over all fault runs

| Config | fault runs | C | P | W | U | M | HMI at AL 50 |
|---|---|---|---|---|---|---|---|
| 4src detect-only | 60 | - | - | - | 40 | 20 | 0 |
| 4src fde1 | 60 | 29 | 10 | **1** | 0 | 20 | 0 |
| 4src fde2 | 60 | 48 | 12 | **0** | 0 | 0 | 0 |
| 3src fde1 | 60 | 20 | 19 | 0 | 1 | 20 | 0 |
| 3src altpnt max-separation | 60 | 12 | 1 | **27** | 0 | 20 | 1 |
| alt3 detect-only | 30 | - | - | - | 30 | 0 | 0 |
| alt3 fde1 | 30 | 23 | 0 | **0** | 7 | 0 | 0 |
| alt3 fde2 | 30 | 19 | 0 | 0 | 11 | 0 | 0 |
| alt3 altpnt max-separation | 30 | 1 | 0 | **25** | 0 | 4 | 19 |

The 20 M in the GNSS-present rows are the two visual faults: the all-in-view filter's chi-square gate
rejected the faulty visual fixes (45 and 10 per flight, seed 0) because GNSS held the solution, so the
solution never moved (HPE max 5.9 m, same as nominal). Not detected, and harmless here.

### Per scenario, AL 50 m

| Scenario | Config | outcome | latency | avail all | avail post | avail post AL 100 | HMI 25/50/100 | HPE max | PL median |
|---|---|---|---|---|---|---|---|---|---|
| nominal | 4src fde1 | quiet 10 | - | 100 % | - | - | 0/0/0 | 5.9 m | 23.1 m |
| nominal | 4src fde2 | quiet 10 | - | 90.7 % | - | - | 0/0/0 | 5.9 m | 28.1 m |
| nominal | alt3 fde1 | quiet 10 | - | 84.7 % | - | - | 0/0/0 | 8.9 m | 31.0 m |
| nominal | alt3 fde2 | quiet 10 | - | 5.0 % | - | - | 0/0/0 | 8.9 m | 70.9 m |
| gnss_spoof | 4src detect-only | U10 | 8 (5-8) | 39.9 % | 18.8 % | 20.9 % | 0/0/0 | 278.7 m | 22.6 m |
| gnss_spoof | **4src fde1** | **C10** | 8 (5-8) | 88.0 % | **83.8 %** | 98.2 % | 0/0/0 | **20.6 m** | 27.9 m |
| gnss_spoof | 4src fde2 | C10 | 8 (5-8) | 31.5 % | 8.1 % | 96.3 % | 0/0/0 | 20.6 m | 62.2 m |
| gnss_spoof | 3src altpnt max-sep | C9 W1 | 8 (5-8) | 86.0 % | 81.0 % | 93.3 % | 0/0/0 | 150.5 m | 27.6 m |
| visual_misreg | alt3 detect-only | U10 | 25 | 47.5 % | 18.3 % | 28.0 % | 0/0/0 | 8.9 m | 30.8 m |
| visual_misreg | alt3 fde1 | C6 U4 | 25 | 47.5 % | 18.3 % | 52.0 % | 0/0/0 | 8.9 m | 43.8 m |
| visual_misreg | alt3 altpnt max-sep | **W10** | 25 | 51.2 % | 25.3 % | 61.1 % | 0/0/0 | 173.8 m | 47.4 m |
| visual_misreg | 4src fde2 | C10 | 21 (21-25) | 54.6 % | 24.8 % | 97.8 % | 0/0/0 | 5.9 m | 45.2 m |
| visual_wrong_place | alt3 detect-only | U10 | 18 | 63.2 % | 48.1 % | 68.7 % | 0/0/0 | 8.9 m | 36.1 m |
| visual_wrong_place | alt3 fde1 | C10 | 18 | 43.1 % | **10.0 %** | 81.6 % | 0/0/0 | 8.9 m | 56.9 m |
| visual_wrong_place | alt3 altpnt max-sep | M4 W6 | 21 (19-21) | 53.6 % | 29.8 % | 60.5 % | 0/0/0 | 104.7 m | 64.8 m |
| trn_ambiguity | 4src detect-only | U10 | 24 (8-24) | 80.2 % | 73.2 % | 79.3 % | 0/0/0 | 7.7 m | 23.9 m |
| trn_ambiguity | 4src fde1 | C10 | 24 (8-24) | 86.6 % | 81.9 % | 98.8 % | 0/0/0 | 7.7 m | 30.3 m |
| trn_ambiguity | 3src altpnt max-sep | **W10** | 24 (8-24) | 39.4 % | 18.1 % | 31.9 % | 0/1/10 | 357.3 m | 103.2 m |
| trn_ambiguity | alt3 detect-only | U10 | 12 (8-12) | 63.1 % | 52.4 % | 67.7 % | 0/0/0 | **366.1 m** | 31.2 m |
| trn_ambiguity | **alt3 fde1** | **C7 U3** | 12 (8-12) | 52.0 % | 37.4 % | 82.7 % | **0/0/0** | **40.7 m** | 46.9 m |
| trn_ambiguity | alt3 altpnt max-sep | C1 **W9** | 12 (8-12) | 43.5 % | 25.8 % | 44.5 % | 0/**19**/3 | 252.1 m | 91.9 m |
| double_spoof_trn | 4src detect-only | U10 | 10 (8-11) | 38.4 % | 16.7 % | 20.9 % | 0/0/0 | 278.7 m | 23.5 m |
| double_spoof_trn | 4src fde1 | C3 P6 **W1** | 10 (8-11) | 56.8 % | 41.5 % | 65.2 % | 0/0/0 | 277.2 m | 34.6 m |
| double_spoof_trn | 4src fde2 | C4 P6 | 10.5 (8-11) | 27.6 % | 2.8 % | 42.6 % | 0/0/0 | 75.4 m | 71.2 m |
| double_spoof_trn | 3src altpnt max-sep | C3 P1 W6 | 10 (8-11) | 43.3 % | 23.3 % | 28.9 % | 0/0/10 | 357.3 m | 173.2 m |
| double_spoof_visual | 4src detect-only | U10 | 7 (6-8) | 51.3 % | 7.5 % | 7.5 % | 0/0/0 | 198.8 m | 23.3 m |
| double_spoof_visual | 4src fde1 | C6 P4 | 7 (6-8) | 55.1 % | 14.6 % | 41.3 % | 0/0/0 | 36.5 m | 27.4 m |
| double_spoof_visual | 4src fde2 | C4 P6 | 7 (6-8) | 47.3 % | 10.8 % | 15.3 % | 0/0/0 | 36.5 m | 48.8 m |

All rows for all 11 configurations are in `results/fde_result.json` (`results.<scenario>.<config>`,
with `per_seed` outcomes and exclusion times) and `results/run_output.txt`.

What this shows:

- **Subset exclusion keeps navigating after a spoof.** Detection-only catches the 2 m/s drag in 5-8 s
  (offset 12-18 m) and is then unavailable to the end, coasting on the spoofed all-in-view filter
  (error up to 279 m, flagged). Excluding GNSS switches the output to the GNSS-free filter: error max
  20.6 m, AL 50 availability after onset 18.8 % => 83.8 %, AL 100 20.9 % => 98.2 %, 10/10 correct.
- **No wrong exclusion where the old rule had many.** On the same inputs the max-separation rule
  excluded a fault-free source in 27 of 60 GNSS-present fault runs and 25 of 30 GNSS-denied ones,
  with 19 HMI epochs at AL 50 (GNSS denied), and 1 at AL 50 and 10 at AL 100 (with GNSS), under the
  TRN ambiguity. The
  subset test had 0 wrong exclusions in those cases and 0 HMI and 0 MI in every run at every AL. Where
  it could not find a unique consistent subset it said so: 7 of 30 GNSS-denied fault runs stayed
  unavailable instead of excluding.
- **One wrong exclusion, under a fault it was not built for.** `4src fde1` in `double_spoof_trn`,
  seed 8: two sources faulty, single-fault monitoring. At frame 70 the set {GNSS, LiDAR TRN, GLO-30
  TRN} passed its own test: the GLO-30 TRN's own nominal error in frames 62-70 (16-26 m toward 133-150
  deg, sigma 17-20 m) pointed the same way as the spoof (25 m toward 126 deg), so the healthy visual
  source was the one excluded. The remaining set kept tripping,
  so the system stayed unavailable and that run had no HMI, but error reached 277 m. `fde2`, which
  monitors pairs, had no wrong exclusion in 60 runs, and in the double-fault runs excluded both
  faulty sources in 8 of 20.
- **Exclusion accuracy costs availability when the remaining set is weak.** Without GNSS, excluding
  the visual source leaves LiDAR TRN + GLO-30 TRN, whose "LiDAR TRN faulted" branch is GLO-30 alone, so
  the PL is large until the 30 s hold + 45 s probation readmits the visual source. In
  `visual_wrong_place` that makes FDE less available than detection-only (10.0 % vs 48.1 % post onset),
  because detection-only becomes available again as soon as the transient fault ends. Accuracy goes the
  other way: under TRN ambiguity detection-only coasted to 366 m error (flagged), FDE stayed at 41 m.
- **Monitoring dual faults is expensive.** `fde2` PL needs every pair-excluded subset to be good. With
  GNSS: nominal availability at AL 50 100 % => 90.7 %. Without GNSS: 84.7 % => 5.0 %, since every pair
  leaves one TRN or the visual fixes alone. At AL 100 `fde2` keeps 95-99 % after a single fault with
  GNSS present. With these priors the dual hypotheses should be monitored, so the honest AL 50 number
  for the GNSS-denied three-source system is 5 %, not 85 %.
- **Two faults with three sources is not solvable and is reported as such.** `3src` in
  `double_spoof_trn`: GNSS excluded in 9 of 10, then no further exclusion (two remaining sources that
  disagree cannot be split), and no run excluded the healthy visual source.

## Files

| File | What |
|---|---|
| `fde.py` | Stdlib: hypotheses, solution separation per subset, detection, subset exclusion with the ambiguity rule, PL, readmission, scoring (outcomes, latency, availability, HMI/MI via altpnt's Stanford classifier) |
| `run_fde.py` | Loads the flight through two-source `load()`, builds GNSS/visual/TRN fixes and faults, runs the 16-filter bank (`BankEkf`, altpnt v2 EKF), all configurations and the altpnt baseline, writes `results/fde_result.json` |
| `test_fde.py` | 10 stdlib tests on synthetic least-squares banks (single fault, two-source ambiguity, dual fault with 1 vs 2 monitored, PL cost, readmission, scoring), 4 checks on the committed results, 3 numpy tests |
| `results/fde_result.json` | Aggregates and per-seed outcomes for 7 scenarios x 11 configurations; per-frame rows for seed 0 of five configurations (`examples`) |
| `results/run_output.txt` | Console output of the run |

Tests (2026-11-06): venv CPython 3.12.14 17 pass; plain `/opt/homebrew/bin/python3` 3.14.7 without
packages 14 pass, 3 skip. Mutation check: making the exclusion pick the first consistent candidate
instead of declaring ambiguity fails `test_two_sources_ambiguous_is_unavailable`.

## Limits

- **Simulated GNSS and TRN sensors, injected faults.** GNSS is truth plus white noise with a nominal
  R, no multipath, no clock, no receiver tracking under spoofing. A real drag-off is often preceded by
  jamming and C/N0 or AGC changes that a receiver monitor would see (see `../gnss-interference-monitor`);
  none of that is modelled.
- **One flight, 188 epochs, 10 seeds.** 0 HMI over ~1,900 epochs per configuration says nothing about
  1e-5 or 1e-7. Priors and budgets are altpnt's illustrative values.
- **Dead reckoning is trusted.** VO drives every filter and is not a fault hypothesis; a VO fault is
  common mode. The two TRNs share VO, the simulated heightmap sensor and the terrain; a real terrain
  ambiguity could hit both.
- **Filters are not snapshot ARAIM.** Subset filters gate independently and carry fault history, so a
  filter that was fed a faulty source stays off for a while after the fault ends (the readmission bug
  above). PL after exclusion is the remaining set's own PL; the probability of a wrong exclusion is not
  added to it, which is defensible only because the unique-consistent-subset rule made it rare here.
- **Exclusion is latched for 30 s + 45 s probation.** That is what makes FDE less available than
  detection-only after short transient faults with a weak remaining set. The hold was not tuned.
- **2^N filters.** 16 filters for 4 sources plus the two baselines ran at ~2 s per 188-frame flight in pure Python; 6 sources
  would need 64 or a hypothesis cap by prior, as ARAIM does.
- Not run: GNSS denied plus spoof (no GNSS to spoof), a fault in VO, slower drag rates (0.5 m/s, the
  rate gnss-ins-ekf-outage found the gate misses), a common-mode terrain fault in both TRNs.
