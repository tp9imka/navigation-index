# GNSS interference monitor: receiver telemetry + ADS-B area map

## Goal

Detect GNSS jamming and spoofing from data you already have, at two scales:

1. **One receiver** - score each epoch of u-blox telemetry (C/N0, AGC, CW jamming
   indicator, clock, position, velocity, the receiver's own spoofing/jamming flags, and the
   navigation data it decoded) with transparent heuristics, CUSUM tests against an independent
   or motion-aware reference, power CUSUMs that see staircase changes, and a lost-fix check;
   latch an alarm with explicit clear conditions; say *why* for every alert.
2. **An area** - aggregate the GNSS quality that aircraft broadcast in ADS-B (NACp) into
   cells, the method behind GPSJam, using a readsb receiver feed.

Defensive monitoring only: everything here observes signals; nothing transmits.

The scorer was reworked on 2026-11-06 after [`../real-attack-replay`](../real-attack-replay/README.md)
replayed 13 h of real Jammertest 2024 u-blox logs through it and found four defects (see
[Real-data evaluation](#real-data-evaluation-jammertest-2024)). The previous revision is git
commit `dae8229`; its numbers are kept below as "before".

## Repos used and why

| Repo | Role |
|---|---|
| [semuconsulting/pyubx2](https://github.com/semuconsulting/pyubx2) | parses UBX-NAV-PVT, NAV-SAT, NAV-STATUS, NAV-CLOCK, MON-RF, SEC-SIG and builds the CFG-VALSET that enables them (`ubx_monitor.py`) |
| [wiedehopf/readsb](https://github.com/wiedehopf/readsb) | ADS-B decoder that writes `aircraft.json` with `nac_p`, `nic`, `seen_pos` and the experimental `gpsOkBefore` (`adsb_area_map.py` input) |
| [S7AM1NA/GNSS-Spoofing-Dataset](https://github.com/S7AM1NA/GNSS-Spoofing-Dataset) | Android GNSS Logger raw measurements (per-SV `Cn0DbHz`, clock) under labelled spoofing windows - real data to tune the scorer's C/N0 and clock thresholds |
| [semuconsulting/pygnssutils](https://github.com/semuconsulting/pygnssutils) | `gnssstreamer` CLI (formerly `gnssdump`) to record a `.ubx` capture for replay |

## Files

| File | Status |
|---|---|
| `scorer.py` | stdlib, run-verified. `Epoch` dataclass in, `Assessment` out: `jam_score`, `spoof_score`, `lost_fix`, `verdict`, `reasons`, `alerts` (one `Alert` per firing detector with value, threshold, unit, evidence dict) and `alarm` (latched state: since, families, first-seen time per detector, clear reason) |
| `ephemeris_check.py` | stdlib, run-verified on real logs. Decodes GPS L1 C/A subframes 1-3 from UBX-RXM-SFRBX (parity checked), parses GPS records of a RINEX 3 nav file (IGS BRDC), and returns per-SV orbit/clock disagreement in metres => `Epoch.eph_mismatch_m` |
| `eval_real.py` | stdlib. Per-slot, per-detector evaluation on the VAARA Jammertest 2024 logs (epochs from `../real-attack-replay/ubx_nmea_epochs.py`), tune/holdout split, `--scorer` for a before/after run, `--table` for the Markdown tables below |
| `results/eval_*.json` | derived per-slot numbers of the three evaluation runs quoted below (no raw data) |
| `test_scorer.py` | 30 unit tests on synthetic epochs |
| `test_real_data_defects.py` | 12 regression tests, one group per real-data defect (driving, baseline lock-out, staircase power, spoofer ephemeris) plus guards |
| `test_ephemeris_check.py` | 6 tests: LNAV encode/decode round trip, parity, IODE consistency, orbit radius, reference choice, RINEX 3 parsing, mismatch in metres |
| `adsb_area_map.py` | stdlib, run-verified. readsb `aircraft.json` snapshots => per-cell good/bad aircraft, GPSJam percentage, level |
| `test_adsb_area_map.py` | 6 unit tests |
| `fixtures/aircraft_demo.json` | synthetic readsb snapshot (made-up hex ids and coordinates) |
| `ubx_monitor.py` | pyubx2 adapter (also maps NAV-PVT `fixType` => `fix_ok`, `velN/velE` => velocity, prints the alarm column). Replay of a `.ubx` file run-verified on the synthetic capture; live `--port` mode not verified (no receiver) |
| `gen_synthetic_ubx.py` | pyubx2 generator: 180 s of 1 Hz NAV-PVT/SAT/STATUS/CLOCK + MON-RF + SEC-SIG with a jamming and a spoofing episode (invented values) |
| `fixtures/synthetic.ubx` | its output (60 KB, seed 11) |
| `test_ubx_replay.py` | regenerates the capture, replays it through `ubx_monitor.run`, checks every epoch's verdict and the latched alarm (skipped without pyubx2) |
| `requirements.txt` | pinned `pyubx2==1.4.1` (+ `pyserial` for a live port) |

## Heuristics in `scorer.py`

Instantaneous rules (one epoch, or two consecutive ones):

| Indicator | Fires when | Points to | Weight |
|---|---|---|---|
| `cn0_drop` | >= 75 % of baseline SVs dropped >= 6 dB or were lost | jamming | 0.5 |
| `agc_change` | `agcCnt` moved >= 20 % from baseline (in-band power changed) | jamming (or a high-power spoofer) | 0.3 |
| `jam_ind` | MON-RF `jamInd` >= 100 (0..255 CW indicator) | narrowband jamming | 0.3 |
| `rx_jam_flag` | MON-RF / SEC-SIG `jammingState` >= 2 | jamming | 0.6 |
| `cn0_uniform` | >= 6 SVs with C/N0 spread < 2 dB (one transmitter, one antenna) | spoofing | 0.35 |
| `cn0_rise` | median C/N0 >= 4 dB above baseline | spoofing | 0.3 |
| `clock_jump` | clock bias off its drift prediction by >= 1000 ns (~300 m) | spoofing | 0.35 |
| `position_jump` | implied speed > platform limit (default 100 m/s) | spoofing | 0.35 |
| `vel_jump` | reported velocity changed faster than the platform can accelerate (`MAX_ACCEL_MPS2`, default 10 m/s^2) | spoofing | 0.35 |
| `rx_spoof_flag` | NAV-STATUS `spoofDetState` / SEC-SIG `spoofingState` >= 2 | spoofing | 0.6 |
| `eph_mismatch` | a tracked SV's receiver-decoded ephemeris disagrees with an independent broadcast source by >= 50 m (orbit or clock x c) | spoofing | 0.6 |

Power CUSUMs (memory across epochs; armed after the 10-epoch baseline):

| Indicator | Statistic | Weight |
|---|---|---|
| `cn0_step` | median over baseline SVs of (C/N0 - per-SV baseline), an SV lost since counting as fallen to 20 dB-Hz; one-sided downward CUSUM, `K = 1.5` sigma of that median (learned, floor 1 dB) | jamming 0.5 |
| `agc_step` | relative AGC deviation from its baseline; two-sided CUSUM, `K = 1` sigma (learned, floor 2 %) | jamming 0.3 |

A staircase of steps each under the instantaneous rules keeps adding to the CUSUM, and the
baseline stops following once the CUSUM holds half an alarm's worth of evidence.

Consistency detectors (CUSUM memory):

| Indicator | Residual and reference | Weight |
|---|---|---|
| `pos_drift`, reference `external` | horizontal distance fix => reference track integrated from `ref_vel_e/ref_vel_n` (IMU, odometry, "known static" (0, 0)); the track freezes while the residual is suspect, so a slow drag accumulates | 0.6 |
| `pos_drift`, reference `doppler` | when the receiver reports velocity and nothing external is given: fix displacement over the last 10 s minus the integral of the reported velocity over the same 10 s. Turns, stop-go and braking are consistent by construction; a position jump or pull the velocity does not show is not. Windowed, so a jammed stretch cannot leave a stale reference; a `position_jump` restarts the window | 0.6 |
| `pos_drift`, reference `cv-prior` | only when no velocity at all is reported: constant-velocity track, least-squares slope over the last 30 learning fixes | 0.6 |
| `vel_mismatch` | GNSS Doppler velocity minus the external reference velocity (off without one) | 0.6 |
| `clock_drift` | receiver clock rate (reported `clk_drift_ns_s`, else differenced bias) minus its learned rate, with an oscillator wander allowance growing while frozen | 0.5 |
| `lost_fix` | no fix after a fix was held, or a telemetry gap > 3 s | own family `lost-fix` |

Each consistency residual feeds a one-sided CUSUM, `S = clip(S + z - K, 0, 2H)`, `H = 8`;
`K = 2` sigma for the 2-D magnitudes and `K = 0.5` for the signed clock residual. A detector
hits while `S >= H` and the current `z >= K`. The doppler residuals overlap in time (10 s
windows), so their positive increments are weighted by 1/10; the decay is not.

**What each reference learns from, and when.** Every reference is protected by its own
detector's gates, not by the global alarm (the earlier coupling let one detector's alarm stale
the others' references on a moving platform, and they then held each other latched):

- position / velocity / clock references and noise estimates learn when their residual is
  `< 3` sigma and their CUSUM `< H/2`; a learned noise sigma may grow at most 2x after arming
  (`NOISE_INFLATION_MAX`);
- the C/N0 and AGC baselines learn on every epoch that is not in lost fix and has no spoofing alert (a spoofer's
  power must not become the baseline) and no C/N0 evidence (no jamming-family hit, `cn0_step`
  CUSUM `< H/2`). Spoofing sub-alerts such as a lone `cn0_rise` do **not** stop learning, so a
  recovery after a slow decline is re-learned (this was the lock-out defect). While the C/N0
  evidence holds, upward innovations still learn at the full rate (`BASELINE_ALPHA` 0.1) and
  downward ones at `CN0_FROZEN_ALPHA` 0.005, and every per-SV innovation is clipped to 3 dB: a
  frozen baseline can fall at most ~0.9 dB/min, enough to follow a moving platform's sky,
  far slower than any of the tested attacks.

Weights add up per family, capped at 1.0; >= 0.5 raises the instantaneous verdict
(`jamming`, `spoofing`, `lost-fix`, joined with `+`).

**Latched alarm.** Any non-clean verdict raises `Assessment.alarm`. It records the time,
families and first-seen time per detector, and clears only after 10 consecutive epochs
(`CLEAR_EPOCHS`) with both scores <= 0.2 (`BASELINE_MAX_SCORE`, now only a clear condition), a
fix, and every consistency and power residual < 3 sigma (`CLEAR_SIGMA`); clearing resets the
CUSUMs. `InterferenceScorer.acknowledge(t, relearn=False)` is the operator clear: it re-anchors
the references on the next fix (and with `relearn=True` also restarts the C/N0/AGC baseline).

All thresholds are named constants at the top of `scorer.py` - they are starting points,
not calibrated limits. `CN0_CUSUM_K`, `CN0_SIGMA_FLOOR_DB`, `CN0_FROZEN_ALPHA` and
`DOPPLER_REL_VEL_SIGMA` were chosen on the 3 tuning logs only (below); the rest are unchanged
or physics-motivated.

## Prerequisites

- Python 3.10+ (tested 3.14.7) for `scorer.py`, `ephemeris_check.py`, `eval_real.py`,
  `adsb_area_map.py` and the tests. No packages.
- For `ubx_monitor.py`, `gen_synthetic_ubx.py`, `test_ubx_replay.py`:
  `pip install -r requirements.txt` (pyubx2 1.4.1; pyserial only for a live port). A live
  run needs a u-blox generation 9+ receiver (ZED-F9P, NEO-M9N, MAX-M10S, ...) on USB. SEC-SIG exists
  only on newer firmware; the code works without it.
- For `eval_real.py`: the VAARA logs from `../real-attack-replay/fetch_data.sh`, and for the
  ephemeris check the IGS BRDC files of the previous and same day (`BRDC_<doy>.rnx.gz`; the
  fetch script gets 255 and 256, day 10 also needs 254, see below).
- For the area map on live data: an RTL-SDR dongle + 1090 MHz antenna running readsb, e.g.
  `readsb --device-type rtlsdr --gain auto --write-json /run/readsb --write-json-every 1`.

## Run (verified part)

```bash
cd samples/gnss-interference-monitor
python3 -m unittest discover -v          # stdlib; test_ubx_replay skips without pyubx2
python3 adsb_area_map.py fixtures/aircraft_demo.json
```

Observed 2026-11-06: `/opt/homebrew/bin/python3` 3.14.7, no packages: `Ran 53 tests ... OK
(skipped=1)`; venv with pyubx2 1.4.1 on Python 3.13.15: `Ran 53 tests ... OK`.

The regression tests for the four real-data defects (`test_real_data_defects.py`), on small
synthetic fixtures, and what they do against the previous scorer (`dae8229`, run on a copy):

| Defect (real data) | Test | dae8229 |
|---|---|---|
| 1 constant-velocity `pos_drift` alarms while driving | 15 min stop-go route with 90 deg turns, filtered fixes + reported velocity: no alert | FAIL (alerts from t=24 s) |
| 1 | same route, fix pulled east at 1.5 m/s that the velocity does not show: `pos_drift` within 20 s, nothing before | FAIL |
| 1 | reported velocity steps 25 m/s: `vel_jump` on exactly those 2 epochs | FAIL |
| 1 (guard) | 3 x 1 h static, iid 2 m / 0.3 m/s noise with velocity reported: no alert | pass |
| 2 baseline lock-out after a `cn0_rise` sub-alert | 300 s slow decline to -15 dB, step recovery, then a -12 dB step: `jamming` within 5 s | FAIL (not within 30 s) |
| 2 (guard) | 40 s uniform +48 dB-Hz spoofer with flag, then clean: no jamming verdict afterwards | pass |
| 2 (guard) | 60 s jamming, sky then settles 2 dB lower: the alarm clears within 900 s | pass |
| 3 staircase power | -3 dB every 15 s: `cn0_step` within 30 s; `cn0_drop` silent at the first step | FAIL |
| 3 | AGC -6 % every 15 s: `agc_step`, no `agc_change` in the first step | FAIL |
| 4 spoofer ephemerides | SFRBX subframes with M0 off by 0.01 rad vs the reference: `spoofing` with `eph_mismatch` on G05 | FAIL |
| 4 (guard) | matching ephemeris: no alert | pass |

Mutation check on the new logic (each mutation alone, on a copy, against `test_scorer`,
`test_real_data_defects`, `test_ephemeris_check`; 2026-11-06):

| Mutation | Tests that fail |
|---|---|
| `cn0_step` never fires | 1 |
| `agc_step` never fires | 1 |
| `eph_mismatch` never fires | 1 |
| reported velocity ignored (cv-prior instead of doppler) | 3 |
| `vel_jump` never fires | 1 |
| doppler CUSUM increments unweighted | 1 (the static-noise hour) |
| `CN0_FROZEN_ALPHA = 0` | 1 (stale baseline never clears) |
| C/N0 baseline learns during spoofing alerts | 1 |
| old learning gate: any sub-alert freezes the baseline and no upward learning | 1 (the lock-out test) |
| either half of that alone | **0**: each of the two protections alone prevents the lock-out |
| position/clock references frozen by any latched alarm again | **0 - not covered** (it showed only on real driving data) |
| power residual dropped from the alarm clear rule | **0 - not covered** |

False-alarm soak (synthetic, iid Gaussian: 2 m position, 0.3 m/s velocity, 5 ns clock noise;
20 seeds x 3600 epochs = 20 h per mode; script kept out of the repo):

| Reference mode | dae8229 | now |
|---|---|---|
| cv-prior (no velocity reported) | 0 alert epochs | 0 |
| doppler (velocity reported, no external reference) | 0 (the old scorer ignored velocity here and used the cv-prior) | 0 (177 alert epochs, 3 alarms at an intermediate revision without the 1/10 weighting) |
| external static (0, 0) | 17 alert epochs, 1 alarm | 17, 1 |

Real receiver noise is not iid; treat this as a floor, not a rate.

Drag sensitivity on the same synthetic static receiver (first non-clean epoch after the drag
starts, and how far the fix had moved by then). The drag moves position and reported velocity
together, as a coherent spoofer does:

| Drag | cv-prior (no velocity) | doppler (velocity reported) | external static reference |
|---|---|---|---|
| accel 0.002 m/s^2 | none in 240 s | none in 240 s | 137 s / 19 m |
| accel 0.005 m/s^2 | none in 240 s | none in 240 s | 83 s / 17 m |
| accel 0.01 m/s^2 | none in 240 s | none in 240 s | 56 s / 16 m |
| accel 0.02 m/s^2 | none in 240 s | none in 240 s | 38 s / 14 m |
| accel 0.05 m/s^2 | 63 s / 99 m | none in 240 s | 21 s / 11 m |
| accel 0.5 m/s^2 | 7 s / 12 m | none in 240 s | 4 s / 4 m |
| constant 0.1 m/s | none in 600 s | none in 600 s | none in 600 s |
| constant 0.2 m/s | none in 600 s | none in 600 s | 97 s / 19 m |
| constant 0.5 m/s | none in 600 s | none in 600 s | 13 s / 6 m |
| constant 1.0 m/s (step) | 9 s / 9 m | none in 600 s | 5 s / 5 m |

The cv-prior and external columns are identical before and after. The doppler column is the
price of not alarming on real driving: with no external reference, position and Doppler that
move together look like real motion, whatever the acceleration. Under `dae8229` a receiver that
reported velocity got the cv-prior column, and the same prior alarmed on 86 % of real driving.
A drag is the case for an IMU, odometry or a "parked" flag.

```
    lat     lon  good  bad   %bad  level
   10.0    20.0    40    0    0.0  green
   10.0    21.0    36    4    7.5  yellow
   11.0    20.0     1    0    0.0  no-data
   11.0    21.0    15   15   46.7  red
```

The TIS-B target in the fixture has no `nac_p`, so it is not counted at all (it is not
silently treated as "good"). The single aircraft in cell 11/20 is below `MIN_AIRCRAFT` and
reads `no-data`, not `green`.

## Real-data evaluation (Jammertest 2024)

Data and labels: the 7 VAARA u-blox logs (13 h, 21 labelled slots: 20 attack, 1 quiet) and
`labels.json` of [`../real-attack-replay`](../real-attack-replay/README.md); epochs built by its
`ubx_nmea_epochs.py` exactly as `replay.py` does (NMEA fix, HDOP, RMC velocity, L1 C/N0, receiver
time as `clk_bias_ns`, car max speed 70 m/s). These logs carry no AGC/MON-RF, so `agc_*` and
`jam_ind` stay silent.

**Split.** Tuning (the grid below and every look at per-epoch traces while designing) used
only 3 logs: `2024-09-10 Test_1` (4 drive-by jam slots, 1.6 h no-logged-test driving),
`2024-09-11 Afternoon Test_1` (3 convoy jam slots), `2024-09-12 Test_2` (2.4.13). The holdout
is the other 4: `2024-09-10 Test_2`, `2024-09-11 Morning` (2.6.x spoofing and the only logged
quiet slot 0.0.1), `2024-09-11 Afternoon Test_2` (0.3.1d-f), `2024-09-12 Test_1` (2.4.2, 2.4.3,
2.4.12). Caveat: the four defects themselves were found on the full set before this work
(that is how the task arrived), so the holdout is clean for the parameter values, not for
the choice of mechanisms.

Tuning grid, tuning logs only (all 8 tuning slots detected in every cell; "fixture" = the
synthetic staircase / step-drop / quiet windows of `../real-attack-replay/make_fixture.py`):

| `CN0_CUSUM_K` | floor 0.5 dB, frozen alpha 0.002 / 0.005 / 0.01 | floor 1.0 dB, frozen alpha 0.002 / 0.005 / 0.01 |
|---|---|---|
| 1.0 | 71 / 43 / 37 % alarm in no-logged-test; fixture quiet window alerted at 0.002 and 0.005 | 52 / 32 / 30 % |
| 1.5 | 62 / 40 / 33 % | 30 / **20** / 20 % (chosen: 11 raises in 3.07 h) |
| 2.0 | 49 / 28 / 28 % | 19 / 19 / 20 % |

`DOPPLER_REL_VEL_SIGMA` (reported-velocity error as a fraction of speed): picked as 0.02 at an
intermediate revision on the tuning logs (16 => 11 raises); on the final code 0, 0.01 and 0.02
give the same tuning-set numbers.

Run it:

```bash
cd samples/gnss-interference-monitor
../real-attack-replay/fetch_data.sh                    # VAARA logs + BRDC 255/256 into ../real-attack-replay/data
curl -fsSL -o ../real-attack-replay/data/brdc/BRDC_254.rnx.gz \
  https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2024/254/BRDC00WRD_S_20242540000_01D_MN.rnx.gz
git show dae8229:samples/gnss-interference-monitor/scorer.py > /tmp/scorer_before.py
python3 eval_real.py --data ../real-attack-replay/data/vaara --scorer /tmp/scorer_before.py --out before.json
python3 eval_real.py --data ../real-attack-replay/data/vaara --out after.json            # ~11 s
python3 eval_real.py --data ../real-attack-replay/data/vaara --brdc ../real-attack-replay/data/brdc --out after_eph.json
python3 eval_real.py --table before=before.json after=after.json after+eph=after_eph.json
```

Ran 2026-11-06 (Python 3.14.7, stdlib); output in `results/`. Cells: `yes T` = first non-clean
verdict T s after the logged start (negative: in the 300 s lead-in), `L` = an alarm was already
latched at the start, `%` = share of slot epochs alerting, then the top 3 detectors.

| Slot | Set | Kind | before (`dae8229`) | after | after + ephemeris check |
|---|---|---|---|---|---|
| 1.10.6a | tune | jam | yes -299 L (100%) pos_drift, cn0_drop, lost_fix | yes 159 (12%) cn0_step, cn0_drop, pos_drift | same |
| 1.10.6b | tune | jam | yes -212 L (99%) pos_drift, cn0_drop, position_jump | yes 417 (18%) cn0_step, cn0_drop, position_jump | same |
| 1.10.6c | tune | jam | yes -299 L (100%) pos_drift, cn0_drop, lost_fix | yes 182 (35%) cn0_step, cn0_drop, pos_drift | same |
| 1.10.6d | tune | jam | yes -100 L (95%) pos_drift, cn0_drop, cn0_uniform | yes 521 (9%) cn0_step, cn0_drop, cn0_uniform | same |
| 1.10.3 | holdout | jam | yes 368 (40%) pos_drift, cn0_rise, cn0_drop | yes 365 (20%) cn0_step, cn0_drop, cn0_uniform | same |
| 1.10.4 | holdout | jam | yes -131 L (88%) cn0_drop, pos_drift, cn0_rise | yes -131 (76%) cn0_step, cn0_drop, pos_drift | same |
| 2.6.1a | holdout | spoof | yes -275 L (87%) cn0_drop, pos_drift | yes 1 (52%) cn0_step, cn0_drop | same |
| 2.6.2 | holdout | spoof | yes -220 (99%) cn0_drop, pos_drift | yes -220 (100%) cn0_step, cn0_drop | + eph_mismatch |
| 2.6.3 | holdout | spoof | yes -299 L (100%) cn0_drop, pos_drift | yes 1 (100%) cn0_step, cn0_drop | + eph_mismatch |
| **0.0.1** | holdout | **quiet** | **yes -207 L (98%) pos_drift** | **no** | **no** |
| 2.6.1b | holdout | spoof | yes -299 L (100%) pos_drift, cn0_drop | yes 0 (100%) cn0_drop, cn0_step | + eph_mismatch |
| 0.3.1a | tune | jam | yes -100 L (99%) pos_drift, cn0_drop | yes 1 (100%) cn0_step, cn0_drop | same |
| 0.3.1b | tune | jam | yes -299 L (97%) cn0_drop, pos_drift, cn0_uniform | yes -256 (92%) cn0_step, cn0_drop, pos_drift | same |
| 0.3.1c | tune | jam | yes -299 L (84%) pos_drift, cn0_drop, lost_fix | yes -2 L (54%) cn0_step, cn0_drop, lost_fix | same |
| 0.3.1d | holdout | jam | yes -126 L (93%) pos_drift, cn0_drop | yes -126 (24%) cn0_step, cn0_drop | same |
| 0.3.1e | holdout | jam | yes -191 L (94%) pos_drift, cn0_drop | yes -175 (2%) cn0_step, cn0_drop | same |
| 0.3.1f | holdout | jam | yes -299 L (96%) pos_drift, cn0_drop, lost_fix | yes -1 L (49%) cn0_step, cn0_drop, pos_drift | same |
| 2.4.2 | holdout | spoof | yes 990 (26%) pos_drift, lost_fix, cn0_rise | yes 742 (60%) cn0_step, pos_drift, cn0_drop | yes 742 (61%) cn0_step, pos_drift, eph_mismatch |
| 2.4.3 | holdout | spoof | yes 101 L (81%) pos_drift, cn0_drop | yes 8 (99%) cn0_step, cn0_drop | yes 8 (99%) cn0_step, eph_mismatch, cn0_drop |
| 2.4.12 | holdout | spoof | yes 6 L (99%) cn0_drop | yes -2 L (100%) cn0_step, cn0_drop | + eph_mismatch |
| 2.4.13 | tune | spoof | yes 24 (98%) lost_fix, clock_jump, cn0_uniform | yes 24 (98%) lost_fix, cn0_rise, cn0_drop | yes 24 (98%) lost_fix, eph_mismatch, cn0_rise |

Per detector: TP = attack slots (8 tuning, 12 holdout) where the detector was part of a
non-clean verdict; FP = its alerting epochs in the quiet slot plus all no-logged-test time.

| Detector | before: TP tune / holdout, FP epochs | after | after + ephemeris check |
|---|---|---|---|
| `pos_drift` | 7 / 11, **10220** | 5 / 3, 275 | 5 / 3, 275 |
| `cn0_drop` | 7 / 12, 665 | 8 / 12, 913 | 8 / 12, 913 |
| `cn0_step` (new) | - | 7 / 12, 2190 | 7 / 12, 2474 |
| `cn0_rise` | 0 / 3, 3440 | 2 / 1, 0 | 2 / 1, 0 |
| `cn0_uniform` | 4 / 3, 51 | 4 / 3, 51 | 4 / 3, 51 |
| `eph_mismatch` (new) | - | - (no BRDC given) | 1 / 6, 244 |
| `vel_jump` (new) | - | 4 / 1, 0 | 4 / 1, 0 |
| `position_jump` | 3 / 1, 0 | 4 / 1, 0 | 4 / 1, 0 |
| `clock_jump` | 1 / 1, 0 | 1 / 1, 0 | 1 / 1, 0 |
| `clock_drift` | 0 / 0, 0 | 1 / 0, 0 | 1 / 0, 0 |
| `lost_fix` | 6 / 3, 583 | 6 / 3, 583 | 6 / 3, 583 |

Alarm time where no test was logged (**not guaranteed quiet**: day 10 had drive-by jammers on
the route, day 12 after 09:05 had unlogged plan tests) and in the quiet slot:

| Span (set) | before | after | after + ephemeris check |
|---|---|---|---|
| d10 Test_1, 1.59 h driving (tune) | 2 raises, alarm 86 % | 4 raises, 28 % | 4, 28 % |
| d10 Test_2, 0.08 h (holdout) | 0, 0 % | 0, 0 % | 0, 0 % |
| **d11 morning, quiet slot 0.0.1, 0.2 h (holdout)** | **1 raise, 100 %** | **0, 0 %** | **0, 0 %** |
| d11 morning, 0.93 h (holdout) | 2 raises, 34 % | 1, 7 % | 1, 7 % |
| d11 afternoon 1, 0.45 h (tune) | 1, 7 % | 1, 8 % | 1, 8 % |
| d11 afternoon 2, 0.2 h (holdout) | 0, 0 % | 0, 0 % | 0, 0 % |
| d12 Test_1, 0.25 h static (holdout) | 2 raises, 100 % | 0, 0 % | 2 raises, 36 % (`eph_mismatch`) |
| d12 Test_2, 1.03 h static (tune) | 0 raises, 100 % (latched) | 6, 11 % | 6, 11 % |

What the numbers say:

- **Defect 1 (driving).** `pos_drift` false-alert epochs 10220 => 275; the quiet slot 98 % =>
  0 %; driving alarm time 86 % => 28 % (what is left there is `cn0_step` / `cn0_drop` on short
  C/N0 dips on a day with drive-by jammers, plus 571 epochs without a fix at the end of the
  log). The "before" TP counts for `pos_drift` (7 / 11) were almost all a latched false alarm
  already on at the slot start (`L`), not detections.
- **Defects 2 and 3 (baseline, staircase).** Every attack slot is detected by a C/N0 detector
  without the help of a latched `pos_drift`: 20 / 20 by `cn0_step` or `cn0_drop` (before, with
  `pos_drift` removed, the replay's variant C missed 2.6.1b, 0.3.1e, 2.4.3 and 2.4.12). 2.4.3,
  the staircase, is now caught 8 s after the plan-shifted start by `cn0_step`. `cn0_rise`
  false-alert epochs 3440 => 0 (it fired for an hour on day 12 against the locked baseline).
- **Defect 4 (ephemerides).** On the holdout, the ephemeris check fires in 2.4.2, 2.4.3, 2.4.12,
  2.6.2, 2.6.3, 2.6.1b; on the tuning set in 2.4.13; never on day 10 (jamming only, 70 decoded
  sets) or the day-11 afternoon (40 sets). Parity failures: 0 of all decoded subframes. Real
  ephemerides matched IGS BRDC to 0.0 m (same IODE) or ~2 m (neighbouring IODE); spoofer ones
  (IODE 2 or 3 at round toe values on day 12, IODE 7/59 on day 11) were 276 km to 53 000 km off.
  Its 244 "FP" epochs are on day 12 between and after the logged slots, while the receiver
  still held a spoofer's ephemeris for a tracked SV (the README there notes the 2.4.12 spoofer
  apparently stayed on after its logged end); they are true statements about the receiver's
  navigation data, counted as FP only because no test was logged.
- **What did not change.** 2.6.1a (about 1 min of spoofing) is seen only as a C/N0 drop; no
  spoofed ephemeris was decoded in it. 0.3.1e (L1 switched off) still alerts on 2 % of its
  epochs: the adapter keeps L1 C/N0 only.

### gnss-signal-chain outputs (GNSS-SDR epochs)

`../gnss-signal-chain/score_scenario.py` on its committed `out/*.epochs.jsonl` (+ the IQ power
proxy as `agc_cnt`), old scorer from a copy vs now (2026-11-06; not written back to that sample):

| Scenario | before: first alert / detectors | now: first alert / detectors | now, `--ref-vel 0,0` |
|---|---|---|---|
| clean (107 epochs) | 0 alert epochs | 0 alert epochs | 0 alert epochs |
| overpower, attack t=75 | t=81 (lost_fix; agc_change sub-alert at 75) | t=75 (agc_change + agc_step), cn0_step 78 | t=75, vel_mismatch 79 |
| jamspoof, attack t=75 | t=76 (lost_fix) | t=75 (agc_change + agc_step) | t=75 |
| dragoff, drag from t=60 | t=89 (pos_drift, cv-prior) | t=66 (agc_change + agc_step; agc_step from 64); **no pos_drift** | t=66; vel_mismatch 86, pos_drift 88 |

The drag-off spoofer generates Doppler consistent with its drag, so without a reference the
new scorer does not attribute the position drag (see the drag table); its power step is what
raises the alarm. With `--ref-vel 0,0` the drag is seen at 86-88 s, as before.

## Run (pyubx2, offline replay of a synthetic capture)

```bash
cd samples/gnss-interference-monitor
python3 -m pip install -r requirements.txt
python3 gen_synthetic_ubx.py fixtures/synthetic.ubx     # optional, the fixture is committed
python3 ubx_monitor.py --file fixtures/synthetic.ubx --changes-only
python3 -m unittest test_scorer test_adsb_area_map test_ubx_replay
```

Synthetic timeline (`gen_synthetic_ubx.py`): 0-59 s clean sky (10 GPS/Galileo SVs, C/N0
following elevation), 60-89 s broadband jamming (C/N0 -14..-20 dB until every SV drops
below 20 dB-Hz, AGC -46 %, jamInd 160, receiver `jammingState` 2 from 70 s), 90-119 s
clean, 120-159 s spoofing takeover (uniform 48 dB-Hz on all SVs, +5000 ns clock step,
300 m position step then 20 m/s walk-off, receiver `spoofDetState` 2 from 130 s),
160-179 s clean. Values are invented to exercise every detector, not recorded. NAV-PVT
velocity stays 0, so the scorer uses the doppler reference.

Observed (pyubx2 1.4.1, Python 3.13.15, 2026-11-06, current scorer):

```
t=  216000.0 clean             jam=0.00 spoof=0.00 -
t=  216060.0 jamming           jam=1.00 spoof=0.00 ALARM C/N0 drop >= 6 dB or lost on 10/10 SVs; AGC -46% vs baseline; median C/N0 -15.8 dB vs per-SV baseline, accumulated (CUSUM 14.3); AGC -46% vs baseline, accumulated (CUSUM 16.0); jamInd 160
t=  216090.0 clean             jam=0.00 spoof=0.00 ALARM
t=  216099.0 clean             jam=0.00 spoof=0.00 -
             alarm cleared: 10 epochs with scores <= 0.2, a fix, and consistency and power residuals < 3.0 sigma
t=  216120.0 spoofing          jam=0.00 spoof=1.00 ALARM median C/N0 rise +9.2 dB; C/N0 spread only 0.5 dB over 10 SVs; clock bias jump +5001 ns; implied speed 300 m/s
t=  216161.0 clean             jam=0.00 spoof=0.00 ALARM
t=  216170.0 clean             jam=0.00 spoof=0.00 -
             alarm cleared: 10 epochs with scores <= 0.2, a fix, and consistency and power residuals < 3.0 sigma
epochs per verdict: clean=109, jamming=30, spoofing=41
```

Per-epoch verdicts and the latched spans (60-98 s, 120-169 s) are the same as under `dae8229`.
`pos_drift` (doppler) joins for 30 of the 40 spoofed epochs: at 159 s the fix had moved 199 m
more than the reported velocity says over 10 s. 160 s is still `spoofing` because the spoofer
switching off is itself a -5001 ns clock jump and a 1081 m/s position jump; that is why there
are 41 spoofing epochs for a 40 s episode. Without `--changes-only` every epoch prints.

`test_ubx_replay` asserts every epoch's verdict and the latch / clear epochs. It failed twice
during this rework and caught real problems: the rise-aware baseline first learned the
spoofer's +9 dB, so its departure read as 10 s of jamming (fixed: no C/N0 learning during
spoofing alerts), and the 10 s doppler window kept the 1 km switch-off jump for 10 s (fixed: a
`position_jump` restarts the window).

## Area mapping (GPSJam method)

GPSJam publishes the formula `percent_bad = 100 * (bad - 1) / (good + bad)` per hexagon
per 24 h, with green below 2 %, yellow 2-10 %, red above 10 %. Its FAQ says the signal
is NACp but does not publish the NACp cut-off. `adsb_area_map.py` uses `nac_p < 8` (EPU >= 92.6 m)
as a named constant `NACP_GOOD_MIN`, plus readsb's own `gpsOkBefore` marker. Square
lat/lon cells replace H3 hexagons to stay stdlib.

To build a daily map from one readsb station:

```bash
mkdir -p snaps
while true; do cp /run/readsb/aircraft.json "snaps/$(date +%s).json"; sleep 10; done
# next day:
python3 adsb_area_map.py snaps/*.json --cell-deg 0.5
```

A single station only maps aircraft within its own radio horizon (a few hundred km at
cruise altitude, less in practice). Aggregator feeds cover more.

## Extend it in a hackathon

1. Write a small adapter from Android GNSS Logger `Raw` rows (GNSS-Spoofing-Dataset) to
   `Epoch` (C/N0 per SV from `Cn0DbHz`, clock from `FullBiasNanos`/`BiasNanos`), replay the
   labelled spoofing windows through `scorer.py`, and report detection delay and false alarms.
   AGC/jamInd fields stay `None` there; the scorer skips them.
2. Add elevation-aware C/N0: on a real sky C/N0 rises with elevation (NAV-SAT `elev_NN`).
   A spoofer flattens that slope, which is a stronger check than plain spread.
3. Use two antennas a few metres apart: real signals arrive with different carrier phase
   differences per SV, while a single-source spoofer gives the same for all SVs.
4. Feed the `Assessment` into the EKF in `samples/gnss-ins-ekf-outage` as an external
   "do not trust GNSS" input, and feed the EKF's INS velocity back as `ref_vel_e/ref_vel_n`
   (use the velocity propagated while GNSS updates are gated off, or the reference follows
   the spoofer through the filter).
5. Push per-cell levels to a TAK map with `samples/mavlink-to-tak-cot` style CoT shapes.

## Galileo, multi-constellation and OSNMA

Everything above is constellation-agnostic: SV ids carry a letter (`G`, `E`, `R`, `C`), and
the consistency detectors look at the PVT, not at the signals. What changes with Galileo
OSNMA-authenticated signals:

- **New input, strongest single cue.** OSNMA (TESLA-based navigation message authentication
  on Galileo E1-B I/NAV) lets a receiver verify ephemeris, clock and status data per SV.
  An authentication failure, or authentication dropping while C/N0 stays high, deserves its
  own detector with a weight >= 0.5, and "not yet authenticated" must read as not-measured,
  not clean: the first authentication needs several 30 s subframes
  ([OSNMAlib card](../../docs/integration-cards/algafix__osnma.md), which also suggests the
  "auth drop with high C/N0" cue). Sources: [OSNMA SIS ICD](../../catalog/resources/galileo-osnma-sis-icd.md),
  [receiver guidelines](../../catalog/resources/galileo-osnma-receiver-guidelines.md),
  [Navipedia](../../catalog/resources/navipedia-osnma.md).
- **What OSNMA does not stop.** It authenticates data, not signal timing. A relay /
  meaconing spoofer that delays authentic signals within the receiver's time-sync bound,
  and a drag-off that shifts code phase while forwarding authentic data bits (the
  `gnss-signal-chain` `dragoff` case: the spoofer reuses the real nav data), both pass
  authentication. That is the gap `pos_drift`, `vel_mismatch` and `clock_drift` cover when an
  external velocity reference is given (a coherent drag-off is invisible to the doppler mode),
  so OSNMA complements this scorer rather than replacing it. Jamming and lost fix are also
  outside OSNMA's scope. `eph_mismatch` is the unauthenticated cousin of OSNMA's data check:
  it compares decoded GPS ephemerides with an independent broadcast copy instead of a MAC.
- **Time is part of the security model.** OSNMA assumes the receiver knows GST to within a
  bound (OSNMAlib's `TS` defaults to 30 s, per its card); a spoofer that walks the receiver
  clock past that bound can replay old keys. `clock_drift` plus a holdover oscillator (see
  [timing resilience](../../docs/timing-resilience.md)) is what protects that assumption.
- **Authenticated subset as a second solution.** Solve once with all SVs and once with
  authenticated Galileo SVs only; feed the distance between the two as another residual. In
  this scorer that is a second `PositionConsistency` with the authenticated fix as the
  reference.
- **Multi-constellation consistency.** A spoofer has to fake GPS, Galileo, GLONASS and
  BeiDou coherently. Per-constellation solutions that disagree, or an inter-system clock
  bias that steps, are cheap extra residuals for the same CUSUM machinery.
- **Tooling to try it file-based.** [OSNMA-SDR-SIM](../../docs/integration-cards/haiyang-wong__osnma-sdr-sim.md)
  writes Galileo E1 IQ files with real OSNMA data (file output only; never transmit);
  GNSS-SDR has OSNMA from v0.0.20 (`src/core/libs/osnma_msg_receiver.cc` is present in the
  v0.0.20 tree and absent in v0.0.19 - checked with the GitHub tree API, 2026-11-06), so
  the Ubuntu 24.04 package used in `gnss-signal-chain` (0.0.19) cannot do it. Other
  implementations: [galileo-osnma](../../catalog/repos/daniestevez__galileo-osnma.md) (Rust),
  [fgi-osnma](../../catalog/repos/nlsfi__fgi-osnma.md),
  [osnma_ublox](../../catalog/repos/axelbjork__osnma_ublox.md).

None of the OSNMA path was run in this sample.

## Pitfalls

- Thresholds are not portable. An active antenna, cable loss or a car roof moves AGC and
  C/N0 baselines by several dB. Learn the baseline on each install.
- `cn0_uniform` misfires indoors, under foliage or with few SVs; `CN0_UNIFORM_MIN_SVS`
  guards only the last case.
- Position and clock jumps only work across consecutive epochs; after a receiver reset the
  first epoch has no reference.
- Without an external reference, `pos_drift` only checks that the fix and the receiver's own
  reported velocity agree (doppler mode). That keeps driving quiet, but a spoofer that moves
  position and Doppler together is invisible to it (drag table: "none" in every row). The
  cv-prior applies only when no velocity is reported and alarms on any real manoeuvre. Give
  the scorer an independent velocity whenever the platform has one, even a "parked" flag (0, 0).
- The C/N0 baseline is per SV and frozen only by C/N0 evidence; while frozen it can still fall
  ~0.9 dB/min (`CN0_FROZEN_ALPHA`). A jammer that ramps slower than that, or stays on for tens
  of minutes, is eventually learned as the new sky and the alarm clears.
- `eph_mismatch` needs an independent broadcast source for the same time (IGS BRDC after the
  fact, or a network feed live) and today decodes GPS L1 C/A only; Galileo/GLONASS/BeiDou
  navigation data from a spoofer is not checked. A spoofer that relays the live broadcast
  (meaconing, or gps-sdr-sim fed a current BRDC file) passes it.
- An external reference is only independent if it does not come from a filter that already
  ingested the suspect GNSS fixes.
- `clock_drift` assumes a free-running oscillator. Receivers that steer their clock or apply
  1 ms clock jumps need those epochs excluded (the jump itself is `clock_jump`'s job), and a
  thermal transient can exceed `OSC_WANDER_NS_S2`.
- The latched alarm does not clear while the position stays away from the frozen reference.
  After a confirmed benign event (e.g. the platform was moved while off), call
  `acknowledge()`; nothing else re-anchors it.
- `lost_fix` needs epochs without a fix to arrive (u-blox sends NAV-PVT with `fixType` 0
  every epoch). If the telemetry stops entirely, the scorer sees nothing until the next
  epoch, which then reports the gap.
- The receiver's own `spoofDetState` / `spoofingState` is one input, not ground truth.
  Check how your firmware behaves against your threat (replay, meaconing, coherent
  takeover) before relying on it.
- M8 receivers do not support CFG-VALSET; enable messages with UBX-CFG-MSG or u-center.
- ADS-B NACp also drops for avionics faults and some aircraft never report it. The `-1`
  in the GPSJam formula and `MIN_AIRCRAFT` exist to keep single aircraft from painting a cell red.
