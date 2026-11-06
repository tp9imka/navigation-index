# GNSS interference monitor: receiver telemetry + ADS-B area map

## Goal

Detect GNSS jamming and spoofing from data you already have, at two scales:

1. **One receiver** - score each epoch of u-blox telemetry (C/N0, AGC, CW jamming
   indicator, clock, position, velocity, the receiver's own spoofing/jamming flags) with
   transparent heuristics, CUSUM consistency tests against an independent reference, and a
   lost-fix check; latch an alarm with explicit clear conditions; say *why* for every alert.
2. **An area** - aggregate the GNSS quality that aircraft broadcast in ADS-B (NACp) into
   cells, the method behind GPSJam, using a readsb receiver feed.

Defensive monitoring only: everything here observes signals; nothing transmits.

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
| `test_scorer.py` | 29 unit tests on synthetic epochs (8 original + 21 for the consistency detectors, lost fix, latching and explanations, incl. negative controls) |
| `adsb_area_map.py` | stdlib, run-verified. readsb `aircraft.json` snapshots => per-cell good/bad aircraft, GPSJam percentage, level |
| `test_adsb_area_map.py` | 6 unit tests |
| `fixtures/aircraft_demo.json` | synthetic readsb snapshot (made-up hex ids and coordinates) |
| `ubx_monitor.py` | pyubx2 adapter (also maps NAV-PVT `fixType` => `fix_ok`, `velN/velE` => velocity, prints the alarm column). Replay of a `.ubx` file run-verified on the synthetic capture; live `--port` mode not verified (no receiver) |
| `gen_synthetic_ubx.py` | pyubx2 generator: 180 s of 1 Hz NAV-PVT/SAT/STATUS/CLOCK + MON-RF + SEC-SIG with a jamming and a spoofing episode (invented values) |
| `fixtures/synthetic.ubx` | its output (60 KB, seed 11; regenerated 2026-11-06, byte-identical) |
| `test_ubx_replay.py` | regenerates the capture, replays it through `ubx_monitor.run`, checks every epoch's verdict and the latched alarm |
| `requirements.txt` | pinned `pyubx2==1.4.1` (+ `pyserial` for a live port) |

## Heuristics in `scorer.py`

Instantaneous rules (one epoch, or two consecutive ones):

| Indicator | Fires when | Points to |
|---|---|---|
| `cn0_drop` | >= 75 % of baseline SVs dropped >= 6 dB or were lost | jamming |
| `agc_change` | `agcCnt` moved >= 20 % from baseline (in-band power changed) | jamming (or a high-power spoofer) |
| `jam_ind` | MON-RF `jamInd` >= 100 (0..255 CW indicator) | narrowband jamming |
| `rx_jam_flag` | MON-RF / SEC-SIG `jammingState` >= 2 | jamming |
| `cn0_uniform` | >= 6 SVs with C/N0 spread < 2 dB (one transmitter, one antenna) | spoofing |
| `cn0_rise` | median C/N0 >= 4 dB above baseline | spoofing |
| `clock_jump` | clock bias off its drift prediction by >= 1000 ns (~300 m) | spoofing |
| `position_jump` | implied speed > platform limit (default 100 m/s) | spoofing |
| `rx_spoof_flag` | NAV-STATUS `spoofDetState` / SEC-SIG `spoofingState` >= 2 | spoofing |

Consistency detectors (memory across epochs; armed after the 10-epoch baseline):

| Indicator | Residual | Reference | Weight |
|---|---|---|---|
| `pos_drift` | horizontal distance fix => reference track, divided by the learned fix noise (per unit HDOP when `hdop` is given) plus the reference's own error growth while frozen | `ref_vel_e/ref_vel_n` from an IMU, odometry or "known static" (0, 0), integrated; without it a constant-velocity prior = least-squares slope over the last 30 clean fixes | 0.6 |
| `vel_mismatch` | GNSS Doppler velocity (`vel_e/vel_n`) minus the reference velocity | external reference only; off without one | 0.6 |
| `clock_drift` | receiver clock rate (reported `clk_drift_ns_s`, else differenced bias) minus its learned rate, with an oscillator wander allowance (`OSC_WANDER_NS_S2`) growing while frozen | the receiver's own clock history | 0.5 |
| `lost_fix` | no fix (`fix_ok=False`, or no lat/lon) after a fix was held, or a telemetry gap > 3 s | - | own family `lost-fix` |

Each consistency residual feeds a one-sided CUSUM, `S = clip(S + z - K, 0, 2H)`, `H = 8`;
`K = 2` sigma for the 2-D magnitudes and `K = 0.5` for the signed clock residual. A detector
hits while `S >= H` and the current `z >= K`. Three rules keep a slow attacker from teaching
the detector that the attack is normal:

- the reference track and the noise estimates learn only when no alarm is latched, `z < 3`
  and `S < H/2`;
- a learned noise sigma may grow at most 2x after the detector is armed
  (`NOISE_INFLATION_MAX`; without that cap a 0.02 m/s^2 drag was never detected in 240 s,
  with it after 38 s - see the drag table below);
- with an external reference the track is pulled toward the fix with a 50 s time constant
  (`EXT_POS_ALPHA = 0.02`), with the constant-velocity prior 10 s.

Weights add up per family, capped at 1.0; >= 0.5 raises the instantaneous verdict
(`jamming`, `spoofing`, `lost-fix`, joined with `+`). The C/N0 and AGC baseline is an EWMA
that only learns from epochs scoring <= 0.2, with a fix, while no alarm is latched.

**Latched alarm.** Any non-clean verdict raises `Assessment.alarm`. It records the time,
families and first-seen time per detector, and clears only after 10 consecutive epochs
(`CLEAR_EPOCHS`) with both scores <= 0.2, a fix, and every consistency residual < 3 sigma
(`CLEAR_SIGMA`); clearing resets the CUSUMs and lets the references learn again.
`InterferenceScorer.acknowledge(t, relearn=False)` is the operator clear: it re-anchors the
references on the next fix (and with `relearn=True` also restarts the C/N0/AGC baseline). A
position residual that never returns inside 3 sigma keeps the alarm on, by design.

All thresholds are named constants at the top of `scorer.py` - they are starting points,
not calibrated limits.

## Prerequisites

- Python 3.10+ (tested 3.14.7) for `scorer.py`, `adsb_area_map.py` and the tests. No packages.
- For `ubx_monitor.py`, `gen_synthetic_ubx.py`, `test_ubx_replay.py`:
  `pip install -r requirements.txt` (pyubx2 1.4.1; pyserial only for a live port). A live
  run needs a u-blox generation 9+ receiver (ZED-F9P, NEO-M9N, MAX-M10S, ...) on USB. SEC-SIG exists
  only on newer firmware; the code works without it.
- For the area map on live data: an RTL-SDR dongle + 1090 MHz antenna running readsb, e.g.
  `readsb --device-type rtlsdr --gain auto --write-json /run/readsb --write-json-every 1`.

## Run (verified part)

```bash
cd samples/gnss-interference-monitor
python3 -m unittest -v test_scorer.py test_adsb_area_map.py
python3 adsb_area_map.py fixtures/aircraft_demo.json
```

Observed (python3.14.7, 2026-11-06): `Ran 35 tests ... OK` (29 scorer + 6 area map).

The new tests, by group:

| Group | Positive cases | Negative controls (must stay clean) |
|---|---|---|
| `pos_drift` | 0.5 m/s^2 drag on a static receiver, CV prior (detected <= 15 s); same with a static external reference (detected earlier than CV); 0.02 m/s^2 drag with an external reference (detected <= 60 s) | 400 s static, both reference modes; 200 s at a constant 15 m/s; a real 0.5 m/s^2 maneuver that the reference also sees |
| `vel_mismatch` | 2 m/s Doppler velocity vs a static reference | no reference => detector off |
| `clock_drift` | +20 ns/s extra clock ramp (6 m/s of pseudorange, far under the 1000 ns jump test, which stays silent); reported `clkD` 50 => 90 ns/s | a slow quadratic oscillator wander over 300 s |
| `lost_fix` | fix lost after a fix; `fix_ok=False` with a stale lat/lon; a 10 s telemetry gap | no fix yet (still acquiring) |
| latch | stays on for 9 clean epochs after a one-epoch alert, clears on the 10th with a reason; stays on through 30 s of lost fix; drift alarm has no silent epoch; baseline frozen while latched; `acknowledge()` | - |
| explanation | every alert carries detector, family, numeric value, message; `reasons` == alert messages | - |

Mutation check (each mutation applied alone to a copy of `scorer.py`, 2026-11-06):

| Mutation | Tests that fail |
|---|---|
| `pos_drift` never fires | 5 |
| `vel_mismatch` never fires | 2 |
| `clock_drift` never fires | 2 |
| `lost-fix` never reported | 3 |
| `CLEAR_EPOCHS = 1` (no latch) | 2 |
| noise may inflate freely (`NOISE_INFLATION_MAX` huge) | 1 (`test_very_slow_drag_external_reference`) |
| learning ignores the CUSUM gate | 1 (`test_clock_time_drag`) |
| references keep learning while the alarm is latched | **0 - not covered by a test** |

False-alarm soak (synthetic, iid Gaussian: 2 m position, 0.3 m/s velocity, 5 ns clock noise;
20 seeds x 3600 epochs = 20 h per mode): constant-velocity prior 0 alert epochs; static
external reference 3 alert epochs, 2 alarms raised. Real receiver noise is not iid; treat
this as a floor, not a rate.

Drag sensitivity on the same synthetic static receiver (first non-clean epoch after the
drag starts, and how far the fix had moved by then; `drag_table` script kept out of the
repo, numbers from 2026-11-06):

| Drag | constant-velocity prior | static external reference |
|---|---|---|
| accel 0.002 m/s^2 | none in 240 s | 137 s / 19 m |
| accel 0.005 m/s^2 | none in 240 s | 83 s / 17 m |
| accel 0.01 m/s^2 | none in 240 s | 56 s / 16 m |
| accel 0.02 m/s^2 | none in 240 s | 38 s / 14 m |
| accel 0.05 m/s^2 | 63 s / 99 m | 21 s / 11 m |
| accel 0.5 m/s^2 | 7 s / 12 m | 4 s / 4 m |
| constant 0.1 m/s | none in 600 s | none in 600 s |
| constant 0.2 m/s | none in 600 s | 97 s / 19 m |
| constant 0.5 m/s | none in 600 s | 13 s / 6 m |
| constant 1.0 m/s (step) | 9 s / 9 m | 5 s / 5 m |

Without the noise-inflation cap the external-reference column reads "none in 240 s" for every
acceleration up to 0.02 m/s^2. A constant-velocity prior cannot see a constant-velocity
drag by definition: it is indistinguishable from real motion. That is the case for an IMU,
odometry or a "parked" flag.

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

An earlier negative control: with the `cn0_drop` weight set to 0,
`test_broadband_jamming` fails, so that test does exercise that detector.

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
160-179 s clean. Values are invented to exercise every detector, not recorded.

Observed (pyubx2 1.4.1, Python 3.12.14, 2026-11-06), before this round's scorer changes:

```
t=  216000.0 clean             jam=0.00 spoof=0.00
t=  216060.0 jamming           jam=1.00 spoof=0.00 C/N0 drop >= 6 dB or lost on 10/10 SVs; AGC -46% vs baseline; jamInd 160
t=  216090.0 clean             jam=0.00 spoof=0.00
t=  216120.0 spoofing          jam=0.00 spoof=1.00 median C/N0 rise +9.2 dB; C/N0 spread only 0.5 dB over 10 SVs; clock bias jump +5001 ns; implied speed 300 m/s
t=  216161.0 clean             jam=0.00 spoof=0.00
epochs per verdict: clean=109, jamming=30, spoofing=41
```

After (same fixture, same versions, 2026-11-06):

```
t=  216000.0 clean             jam=0.00 spoof=0.00 -
t=  216060.0 jamming           jam=1.00 spoof=0.00 ALARM C/N0 drop >= 6 dB or lost on 10/10 SVs; AGC -46% vs baseline; jamInd 160
t=  216090.0 clean             jam=0.00 spoof=0.00 ALARM
t=  216099.0 clean             jam=0.00 spoof=0.00 -
             alarm cleared: 10 epochs with scores <= 0.2, a fix, and consistency residuals < 3.0 sigma
t=  216120.0 spoofing          jam=0.00 spoof=1.00 ALARM median C/N0 rise +9.2 dB; C/N0 spread only 0.5 dB over 10 SVs; clock bias jump +5001 ns; implied speed 300 m/s; position 299 m off constant-velocity track (149.5 sigma, CUSUM 16.0)
t=  216161.0 clean             jam=0.00 spoof=0.00 ALARM
t=  216170.0 clean             jam=0.00 spoof=0.00 -
             alarm cleared: 10 epochs with scores <= 0.2, a fix, and consistency residuals < 3.0 sigma
epochs per verdict: clean=109, jamming=30, spoofing=41
```

Per-epoch verdicts are unchanged (109/30/41); the alarm stays latched for 89 epochs
(60-98 s and 120-169 s) and each clear names its reason. `pos_drift` now joins at 120 s and
stays on through the walk-off: at 159 s the fix is 1079 m off the frozen track (27.6 sigma).
Without `--changes-only` every epoch prints. 160 s is still `spoofing` (0.70) because the
spoofer switching off is itself a -5001 ns clock jump and a 1081 m/s position jump; that is
why there are 41 spoofing epochs for a 40 s episode. The synthetic capture has no lost fix
and no slow drift; those detectors are covered by the unit tests and by the GNSS-SDR runs in
[`../gnss-signal-chain`](../gnss-signal-chain/README.md).

`test_ubx_replay` asserts every epoch's verdict and the latch / clear epochs (36 tests in
total with pyubx2, all OK; 35 + 1 skipped without it on python3.14.7). Earlier negative
control: with the `NAV-SAT` branch of `fill()` disabled, `test_ubx_replay` fails.

Live receiver (not verified, no receiver attached):

```bash
python3 ubx_monitor.py --port /dev/ttyACM0 --baud 38400 --enable   # macOS: /dev/cu.usbmodem*
```

Two things the replay surfaced and the code now handles: the last epoch of a file was
never scored (no following iTOW to flush it), and pyubx2 can only build MON-RF from a raw
payload (it picks the 20- or 24-byte block layout from the payload length), so the
generator packs MON-RF with `struct`.

pyubx2 attribute names used (from `src/pyubx2/ubxtypes_get.py`, v1.4.1): NAV-PVT `fixType`,
`lat`, `lon` (already scaled to degrees), `velN`, `velE` (mm/s); NAV-SAT `numSvs`, `gnssId_NN`, `svId_NN`,
`cno_NN`; NAV-STATUS `spoofDetState`; NAV-CLOCK `clkB` (ns), `clkD` (ns/s); MON-RF
`agcCnt_01`, `jamInd_01`, `jammingState_01` (absent from the 20-byte-block MON-RF-V0
layout); SEC-SIG `jammingState`, `spoofingState` (both V1 and V2 layouts). Repeating-group
fields carry a two-digit suffix, `_01` for the first block.

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
  authentication. That is the gap `pos_drift`, `vel_mismatch` and `clock_drift` cover, so
  OSNMA complements this scorer rather than replacing it. Jamming and lost fix are also
  outside OSNMA's scope.
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
- The constant-velocity prior is the weak mode: it cannot see a constant-velocity drag, and
  while frozen it loses 1 m/s of certainty per second (`CV_VEL_SIGMA_MPS`). Give the scorer
  an independent velocity whenever the platform has one, even a "parked" flag (0, 0).
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
