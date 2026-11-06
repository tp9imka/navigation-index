# Real attack replay: Jammertest 2024 receiver logs through the interference monitor

## Goal

The [`gnss-interference-monitor`](../gnss-interference-monitor/README.md) scorer (C/N0, AGC,
clock and position rules, CUSUM drift, lost fix, latched alarm) and its numbers came from
synthetic UBX streams and gps-sdr-sim IQ files. This sample replays **real recorded jamming and
spoofing** from Jammertest 2024 (Andoya, Norway) through that scorer, unmodified, and reports per
test: detected or not, time to detect, which detector fired, and alarms in quiet time. It also runs
RTKLIB SPP on the same logs to show what the attacks did to a position solution.

Everything here is file replay of public recordings. Nothing transmits.

## Data survey: what is public, small and receiver-level

| Dataset | Receiver-level logs? | Size | Access / licence | Used |
|---|---|---|---|---|
| [VAARA](https://github.com/UniVaasaDigiEco/VAARA) (Univ. Vaasa, Jammertest 2024) | yes: u-blox `.ubx.xz` (NMEA + RXM-RAWX/SFRBX/MEASX), Android GnssLogger, RINEX `.24o`, NMEA | 1.57 GB in git (card); the 10 u-blox files are 69 MB as `.xz` | plain GitHub, no login; **no licence stated** | yes, 7 u-blox files |
| [NPRA jammertest-plan](https://github.com/NPRA/jammertest-plan) | labels only: test catalog JSON, per-day plans | < 1 MB JSON | MIT | yes, for test descriptions; 2024 plan from git history |
| Fraunhofer IIS Jammertest 2025 | no, raw IQ (HDF5) | 360 GB | CC BY-NC-SA 4.0 | no (IQ, size) |
| S7AM1NA GNSS spoofing | Android raw, yes | full zip not released (2026-11-06); public 23.7 MB sample starts after the last spoof window ([card](../../docs/dataset-cards/gnss-spoofing-s7am1na.md)) | MIT | no (no labelled attack data public) |
| TEXBAT | no, raw IQ | about 430 GB; processed `.mat` 0.8 GB | research use, "refrain from distributing" ([card](../../docs/dataset-cards/texbat.md)) | no |
| FGI Jammer Test 2023 | no, LabSat raw IQ | not checked | CC BY 4.0 (record) | no |
| Safi 2025 timing-spoofing thesis (Vaasa) | analyses Vaasa u-blox ZED-F9P data from Jammertest 2024 (record summary) | thesis page behind a bot check | - | its data source appears to be VAARA; not confirmed |

VAARA is the only one that is receiver-level, labelled with a field log, and downloadable without
login. Its u-blox logs carry **no UBX NAV-\* messages** (no NAV-PVT/SAT/CLOCK, no MON-RF), so the
monitor's pyubx2 adapter (`ubx_monitor.py`) has nothing to read; pyubx2 1.4.1 also raises
`UnicodeDecodeError` on these files when a `$` byte inside a binary payload starts an NMEA parse.
The receiver is a u-blox generation 9 (RXM-MEASX and MON-SPAN present; the Safi thesis record says
ZED-F9P). Day 10 logs are 2 Hz, the rest 1 Hz.

## Files

| File | What |
|---|---|
| `ubx_nmea_epochs.py` | stdlib framer for mixed UBX + NMEA bytes (checksums on both), epoch grouping, Epoch builder: GGA/RMC position, fix, HDOP, RMC velocity, **L1-band C/N0 only** from GSV with NMEA 4.11 signal ids (GPS L1 C/A, GLONASS L1OF, Galileo E1, BeiDou B1I, QZSS L1; L2/L5/E5 entries and SBAS PRNs dropped), and a reconstructed monotonic time axis that survives receiver time jumps |
| `replay.py` | runs `scorer.InterferenceScorer` (imported, not edited) per file and scores every labelled window; variants below |
| `labels.json` | test windows (UTC) per file with source, type and description; optional stationary/ref spans for SPP truth |
| `run_rtklib_spp.sh` | Docker (`rtklib-demo5` image from [`gnss-rinex-processing`](../gnss-rinex-processing/README.md)): `convbin` UBX => RINEX 3.04, `rnx2rtkp -p 0` SPP with solution status; logged nav or an external IGS BRDC file |
| `spp_eval.py` | horizontal error of RTKLIB SPP and of the receiver's own NMEA fix per window, vs a stationary reference |
| `summary_table.py` | Markdown table across variant result files |
| `fetch_data.sh` | downloads the 7 u-blox logs (64 MB `.xz`, 272 MB decompressed) and IGS BRDC for 2024-09-11/12 from the BKG mirror |
| `make_fixture.py`, `fixtures/labels_fixture.json` | synthetic VAARA-shaped stream (same sentence layout, signal ids, binary `$` bytes) with the four effects found on the real data; the `.ubx` is generated, not committed |
| `test_real_attack_replay.py` | 13 tests (stdlib; 1 pyubx2 cross-check skipped without it) |
| `results/` | result JSON of every run quoted below (derived numbers only, no raw data) |

## Labels and how approximate they are

- **source `vaara`**: UTC windows from VAARA `Jammertest_metadata.md` (field log, corrected UTC
  lines). Windows are test slots, not emitter-on intervals: drive-by tests (1.10.x, 0.3.1) have
  the jammer in range for only part of the slot; 2.6.1a "spoofing only lasted for about a minute";
  2.6.2's C/N0 drop starts at 08:57, 3 min before the logged 08:59:59; the 2.4.12 spoofer
  apparently stayed on after the logged end (C/N0 stays ~6 dB low and RTKLIB SPP jumps 100+ m
  from 08:37 to the end of the log).
- **source `plan-shift`** (2.4.2, 2.4.3): VAARA did not log these. The 2024 Thursday plan
  (`Latex/transmissionplan/plan-thursday.tex` at jammertest-plan commit `659ed2ecb0`, CEST) has
  2.4.2 at 10:00-10:25, 2.4.3 at 10:40-10:55 and 2.4.12 at 11:10-11:25; VAARA logged 2.4.12 at
  08:20:10 UTC = 10:20 CEST, 50 min early. Shifting the other two by the same 50 min gives
  07:10-07:35 and 07:50-08:05 UTC, and the data agree: receiver UTC jumps **+900.01 s** at
  07:30:44 and back at 07:32:37 (2.4.2 is "time offset 15 minutes"), and the median L1 C/N0 falls
  from 42 to 30 dB-Hz in steps over 07:50:02-07:50:16 and from 31 to 18 dB-Hz at 08:00:18 (2.4.3
  is "power jump"). The -3 min time offset of 2.4.3 never reached the receiver clock.
- **quiet**: only VAARA's 0.0.1 "no test running" (day 11, 10:11-10:23) is a logged quiet
  window. Time outside every window is reported as "no logged test", not as quiet: Bleik, the
  motorcade and Grunnvatn ran tests in parallel all day (2024 plan), and day 12 after 09:05 has
  unlogged plan tests (the receiver fix wanders up to 2834 m there).
- Test descriptions come from NPRA `testcatalog.json` (current version, which can differ from the
  2024 one) plus the VAARA notes. The day-12 file 10:19-11:05 (`Test_3`) has no logged test and was
  not replayed; day 10's two short `10:14`/`10:26` files overlap the main log and were skipped.

## Replay variants

`replay.py` always uses `max_speed_mps = 70` (car) and feeds receiver UTC minus the reconstructed
time axis as `clk_bias_ns`, so a receiver time jump of more than 5 s reaches `clock_jump`
(slower time drags are absorbed by the reconstruction; see Limits).

| Variant | What changes (scorer.py untouched) | Result file |
|---|---|---|
| A, as shipped | full scorer, constant-velocity prior | `results/A_shipped.json` |
| B | A + `ref_vel = (0, 0)` on the static day-12 files ("known parked") | `results/B_shipped_static_ref.json` |
| C | A without the position/velocity consistency detectors (a `PositionConsistency` stub in `replay.py`) | `results/C_no_pos_drift.json` |
| D | C + **what-if** `scorer.BASELINE_MAX_SCORE = 0.3` set at runtime (see finding 2) | `results/D_no_pos_drift_baseline_0.3.json` |
| F | D + receiver clock from RTKLIB SPP (IGS BRDC) instead of receiver time; only the 3 files with RAWX every epoch | `results/F_D_plus_spp_clock.json` |

## Run

```bash
cd samples/real-attack-replay
python3 -m unittest -v test_real_attack_replay.py          # stdlib, ~0.5 s, no download

./fetch_data.sh                                             # 64 MB download, 272 MB on disk
python3 replay.py --data data/vaara --no-pos-drift --baseline-max-score 0.3 --out out/D.json   # ~14 s
python3 replay.py --data data/vaara --out out/A.json        # as shipped
python3 summary_table.py A=out/A.json D=out/D.json

# RTKLIB SPP (Docker, builds rtklib-demo5 on first use, ~1.5 min here); per file ~2-4 s
./run_rtklib_spp.sh data/vaara/2024-09-12/Test_1/ublox_2024-09-12T071744.ubx out/rtklib G,E,R,C data/brdc/BRDC_256.rnx.gz
python3 spp_eval.py --file 2024-09-12/Test_1/ublox_2024-09-12T071744.ubx \
  --pos out/rtklib/ublox_2024-09-12T071744.brdc.spp.pos --ubx data/vaara/2024-09-12/Test_1/ublox_2024-09-12T071744.ubx
python3 replay.py --data data/vaara --no-pos-drift --baseline-max-score 0.3 --spp-clock out/rtklib   # variant F

# no download: the synthetic VAARA-shaped fixture
python3 make_fixture.py && python3 replay.py --data fixtures --labels fixtures/labels_fixture.json --no-pos-drift
```

## Results

Two scorer revisions. **Before** = `scorer.py` at git `dae8229`, the revision this sample was
built against; its five result files are kept in `results/before_dae8229/`. **Now** = the
reworked scorer (2026-11-06) that fixes findings 1-3 and adds an ephemeris check (finding on
SPP below); `results/*.json` hold the re-run. `replay.py` itself is unchanged; with the new
scorer `--baseline-max-score` only moves the alarm clear threshold, so D equals C apart from
alarm-clear timing. Per-detector TP/FP tables with a tune/holdout split, and the ephemeris
check on these logs, are in the [monitor's real-data evaluation](../gnss-interference-monitor/README.md#real-data-evaluation-jammertest-2024).

Ran 2026-11-06: replay on Python 3.14.7 (stdlib), RTKLIB demo5 v2.5.1 in Docker.

Columns: `yes T s` = first non-clean verdict T seconds after the logged start (negative = before
it; alerts count from max(start - 300 s, previous window end)); `L` = an alarm was already
latched at the logged start, so T says little; `%` = share of window epochs with a non-clean
verdict; then the top 2 detectors by alerting epochs.

| Test (UTC) | Attack | A before | C before (pos_drift off) | A now | B now (static ref, d12) | Receiver NMEA fix |
|---|---|---|---|---|---|---|
| 1.10.6a 08:12-08:28 d10 | drive past 3 parked multi-band jammers (0.4-1 W) | yes -299 L (100%) pos_drift, cn0_drop | yes 226 (1%) lost_fix | yes 159 (12%) cn0_step, cn0_drop | = A | moving, no truth |
| 1.10.6b 08:32-08:48 | same, all 3 on | yes -212 L (99%) | yes 567 L (0%) cn0_rise, position_jump | yes 417 (18%) cn0_step, cn0_drop | = A | " |
| 1.10.6c 09:09-09:24 | same, antennas flat | yes -299 L (100%) | yes 222 L (1%) | yes 182 (35%) cn0_step, cn0_drop | = A | " |
| 1.10.6d 09:26-09:42 | same | yes -100 L (95%) | yes 543 L (1%) | yes 521 (9%) cn0_step, cn0_drop | = A | " |
| 1.10.3 12:05-12:27 d10 | start beside dual-band jammer S2.4, drive away | yes 368 (40%) pos_drift, cn0_rise | yes 368 (9%) cn0_drop | yes 365 (20%) cn0_step, cn0_drop | = A | " |
| 1.10.4 12:30-12:58 | same, H6.5 1-1.6 W | yes -131 L (88%) | yes -129 L (16%) | yes -131 (76%) cn0_step, cn0_drop | = A | " |
| 2.6.1a 08:06-08:16 d11 | spoofer M1.1 in a car, ~1 min on | yes -275 L (87%) | yes 1 (52%) cn0_drop | yes 1 (52%) cn0_step, cn0_drop | = A | 0.8 m median, 1.1 m max (stationary) |
| 2.6.2 08:59-09:22 | spoofer, fixed spoofed position, no initial jamming | yes -220 (99%) cn0_drop, pos_drift | yes -220 (89%) cn0_drop | yes -220 (100%) cn0_step, cn0_drop | = A | 1.1 / 1.3 m (stationary part) |
| 2.6.3 09:51-10:07 | spoofer moving, "sea spoofing" | yes -299 L (100%) | yes 1 (29%) cn0_drop | yes 1 (100%) cn0_step, cn0_drop | = A | 0.5 / 0.7 m (first 3 min) |
| **0.0.1 10:11-10:23** | **quiet** | **yes -207 L (98%) pos_drift** | **no** | **no** | **no** | driving |
| 2.6.1b 10:30-10:51 | spoofer, motorcade stationary | yes -299 L (100%) | **no** | yes 0 (100%) cn0_drop, cn0_step | = A | 1.6 / 3.2 m |
| 0.3.1a 12:46-13:10 d11 | jammer H3.2 in the convoy | yes -100 L (99%) | yes 1 (23%) cn0_drop | yes 1 (100%) cn0_step, cn0_drop | = A | moving |
| 0.3.1b 13:16-13:45 | H6.5 in the convoy | yes -299 L (97%) | yes 244 (10%) | yes -256 (92%) cn0_step, cn0_drop | = A | " |
| 0.3.1c 13:52-14:16 | stationary demo H3.2 | yes -299 L (84%) | yes 257 L (29%) | yes -2 L (54%) cn0_step, cn0_drop | = A | " |
| 0.3.1d 14:50-15:02 | passes H3.2 at varying speed | yes -126 L (93%) | yes -126 (9%) cn0_drop | yes -126 (24%) cn0_step, cn0_drop | = A | " |
| 0.3.1e 15:06-15:22 | H6.5 **with L1 switched off** | yes -191 L (94%) | **no** | yes -175 (2%) cn0_step, cn0_drop | = A | " |
| 0.3.1f 15:28-15:51 | 3 fixed jammers on the route | yes -299 L (96%) | yes -1 L (18%) | yes -1 L (49%) cn0_step, cn0_drop | = A | " |
| 2.4.2* 07:10-07:35 d12 | time offset +15 min, power ramp | yes 990 (26%) pos_drift, lost_fix | yes 1154 (12%) lost_fix, cn0_rise | yes 742 (60%) cn0_step, pos_drift | = A | 1.3 m median, **1288 m max**, no fix in 12% of the logged part |
| 2.4.3* 07:50-08:05 | time offset -3 min, power jump | yes 101 L (81%) pos_drift, cn0_drop | **no** | yes 8 (99%) cn0_step, cn0_drop | = A | 2.1 / 8.7 m |
| 2.4.12 08:20-08:35 | static, pseudorange ramp 9 ns/s | yes 6 L (99%) cn0_drop | **no** | yes -2 L (100%) cn0_step, cn0_drop | = A | 3.7 / 6.8 m |
| 2.4.13 08:50-09:05 | jamming then spoofing, ramp | yes 24 (98%) lost_fix, clock_jump | same | yes 24 (98%) lost_fix, cn0_rise | yes 24 (99%) | fix in 2.5% of the window, 79.5 / 258 m |

\* label from the shifted plan. 2.4.13: the log starts 08:50:23, 15 s after the logged start.
Static reference for day 12 = median receiver fix more than 120 s from every window (spread:
0.4 m median, 1.7 m max on `Test_1`); day 11 stationary spans use the clean minutes just before.
"= A": same cell as A now (B differs from A only on the static day-12 files). C now and D now
equal A now in every attack slot (the new `pos_drift` only fires alongside C/N0 detectors there).

Alarm time outside labelled windows ("no logged test", **not guaranteed quiet**):

| File | Hours | A before | A now (= C, D now) | B now | F now (SPP clock) |
|---|---|---|---|---|---|
| d10 07:32-10:42 (2 Hz, driving) | 1.59 | 2 raises, alarm 86% of the time (pos_drift, lost_fix) | 4 raises, 28% (cn0_step, lost_fix) | = A | n/a |
| d11 morning | 0.93 | 2 raises, 34% (pos_drift) | 1 raise, 7% (cn0_step) | = A | 4 raises, 91% (clock_drift, cn0_rise) |
| d11 afternoon 1 | 0.45 | 1 raise, 7% | 1 raise, 8% (cn0_step, cn0_drop) | = A | n/a |
| d10 test 2, d11 afternoon 2 | 0.28 | 0 | 0 | 0 | n/a |
| d12 07:17-08:45 (static) | 0.25 | 2 raises, 100% (pos_drift) | 0 | 0 | 0 raises, 100% (clock_drift) |
| d12 08:50-10:12 (unlogged plan tests) | 1.03 | 0 raises, 100% (pos_drift, cn0_rise) | 6 raises, 11% (cn0_step, cn0_drop) | 4 raises, 98% (pos_drift, cn0_rise) | 0 raises, 100% (clock_drift) |

B on day-12 `Test_2` stays on through 09:05-10:12 where the receiver fix wanders up to 2834 m
during unlogged plan tests (external static reference; plausibly real, see finding 1). F, the
RTKLIB SPP clock as input, is as noisy as before (finding 6).

### RTKLIB SPP during the attacks

`run_rtklib_spp.sh` + `spp_eval.py`, all four constellations, elevation mask 10 deg, no RAIM.
Left: SPP with the IGS broadcast ephemerides (BKG mirror). The receiver's own NMEA fix on the
right for the same span.

| Test | SPP availability | SPP median error | SPP epochs > 100 m | SPP max | NMEA fix median / max |
|---|---|---|---|---|---|
| 2.4.2 (d12, static) | 45% | 2.3 m | 14% | 1596 km | 1.3 / 1288 m |
| 2.4.3 | 86% | 4.5 m | 39% | 1600 km | 2.1 / 8.7 m |
| 2.4.12 | 97% | 4.6 m | 17% | 1354 km | 3.7 / 6.8 m |
| 2.4.13 | 4% | 818 km | 100% | 4114 km | 79.5 / 258 m (fix 2%) |
| 2.6.1a (d11, stationary) | 100% | 0.9 m | 0% | 14 m | 0.8 / 1.1 m |
| 2.6.2 (stationary part) | 8% | 658 m | 86% | 3115 km | 1.1 / 1.3 m |
| 2.6.3 (first 3 min) | 91% | 10.3 m | 29% | 463 km | 0.5 / 0.7 m |
| 2.6.1b | 6% | 18.4 m | 21% | 4455 km | 1.6 / 3.2 m |

With the navigation data **the receiver itself decoded** (`convbin -n`, the default path), the
day-12 SPP median error is 276 km in every window and 2.6.1a's is 38.6 km: the spoofers'
synthetic ephemerides end up in the RINEX nav file and poison solutions even for real signals.
Use an independent ephemeris source when post-processing data that may contain spoofing. The
monitor's `ephemeris_check.py` now does this on the fly: it decodes the GPS subframes in these logs
(0 parity failures) and flags SVs whose decoded orbit/clock disagrees with IGS BRDC; spoofer
ephemerides (276 km to 53 000 km off) show up in 7 of the 8 spoofing slots and never on the
jamming-only days ([evaluation](../gnss-interference-monitor/README.md#real-data-evaluation-jammertest-2024)).

## Findings

1. **The constant-velocity `pos_drift` is unusable on a driving car without an IMU.** In variant A
   it latches for 86% of the day-10 driving time and 98% of the only logged quiet window (0.0.1),
   and since the alarm only clears when the residual is back inside 3 sigma, almost every window
   reads `L`. The synthetic soak (20 h iid noise, 0 alert epochs) did not predict this: real stop-go
   driving and turns are not constant velocity. On the static day-12 receiver with `ref_vel = (0, 0)`
   (variant B) pos_drift raised no alarm in the 0.25 h outside windows on `Test_1` and did not fire on
   2.4.3 or 2.4.12, where the receiver fix moved at most 8.7 m; on `Test_2` it stays on through
   09:05-10:12, where the fix wanders up to 2834 m during unlogged plan tests (plausibly real).
   **Status (2026-11-06): fixed in the scorer.** Without an external reference `pos_drift` now
   compares the fix with the receiver's own reported velocity over 10 s windows; the quiet
   window reads 0 % and pos_drift false-alert epochs fell from 10220 to 275 over all no-logged-test
   time. Cost: a drag that moves position and Doppler together needs an external reference.
2. **Baseline lock-out (scorer defect, found on real data, reproduced in the fixture).**
   `cn0_rise` has weight 0.3: above `BASELINE_MAX_SCORE` (0.2) but under the 0.5 alert threshold.
   After C/N0 recovers from a slow decline the baseline is still low, `cn0_rise` fires, the verdict
   is clean, and the baseline never learns again. Later real drops are compared with the stale low
   baseline and missed: in C, 2.6.1b (C/N0 42 => ~10 dB-Hz), 2.4.12 (42 => ~15) and 0.3.1e go
   undetected. With the threshold at 0.3 (variant D, runtime override only) they are detected at
   0-21 s. A fix in `scorer.py` could exclude `cn0_rise` from the learning gate or let the baseline
   decay toward the current sky after N clean verdicts; not changed here (another sample owns it).
   **Status: fixed in the scorer.** Spoofing sub-alerts no longer stop baseline learning, a frozen
   baseline still learns upward at full rate and downward at a bounded rate, and the baseline is
   per SV with clipped innovations; 2.6.1b, 2.4.12 and 0.3.1e are detected without the what-if.
3. **Staircase power evades `cn0_drop`.** 2.4.3 lowered the median C/N0 by 2-6 dB per step over
   07:50:02-07:50:16 (42 => 30 dB-Hz); each step is under the 6 dB rule and the EWMA baseline
   (alpha 0.1) follows. The 08:00:18 step (31 => 18 dB-Hz median) hit fewer than 75 % of the SVs by
   6 dB, so it also stayed clean. Missed in every variant except where pos_drift or SPP clock alarms
   were already on. The synthetic jamming episode was a single step, so the unit tests never covered
   this.
   **Status: fixed in the scorer.** `cn0_step`, a CUSUM on the median per-SV C/N0 deviation
   (and `agc_step` on AGC), catches 2.4.3 8 s after the plan-shifted start.
4. **Spoofing showed up as a C/N0 drop, not a rise, and the receiver was rarely captured.** In the
   2.6.x motorcade spoofing tests the u-blox kept its true position (stationary error <= 3.2 m) while
   the field notes say the test car's own navigation was spoofed; every detection was `cn0_drop`,
   i.e. the jamming family. `cn0_uniform` and `cn0_rise`, the synthetic tests' spoofing cues, almost
   never alerted. On day 12, 2.4.2 captured the receiver: UTC +900 s and a 1288 m position excursion.
   The first alert is `lost_fix` at 07:29:14, 11.5 min after the log start, then `clock_jump` at the
   07:30:44 time jump (receiver time path); the power ramp before that raised nothing.
5. **L1-only C/N0 cannot see an L1-off jammer.** 0.3.1e (H6.5 with L1 switched off) is missed in C
   and nearly missed in D (5 epochs). The adapter keeps only L1-band GSV entries; adding L2/L5
   C/N0 as separate keys is the obvious next step.
6. **SPP clock as an input adds alarms, not detections.** Variant F feeds the RTKLIB SPP receiver
   clock: `clock_drift` and `clock_jump` fire in every spoofing window, but also 7 raises in 0.93 h and
   17 raises in 1.03 h of no-logged-test time, and keep 0.0.1 alarmed 48% of the time. On day 12 the
   clean receiver clock rate was ~230-295 ns/s and smooth; SPP outliers and mixed real/spoofed solutions
   make the differenced rate jumpy. A 9 ns/s ramp (2.4.12) was not separable from that noise.
7. **2.4.13 (jamming then spoofing)** is the clearest case: a fix in only 2.5% of the window,
   `lost_fix` at +24 s (log starts 15 s late) and `clock_jump` from the receiver time path.

### Synthetic prediction vs real

As found with the scorer at `dae8229` (rows 3 and 6 are what the rework addressed):

| Synthetic claim (gnss-interference-monitor README) | Real Jammertest 2024 replay |
|---|---|
| Jamming detected at onset by cn0_drop + AGC + jamInd (score 1.0) | No AGC/jamInd in these logs (no MON-RF; MON-SPAN only on day 10, unused). In D, 19 of 20 attack slots raised an alert and cn0_drop (alone it reaches exactly the 0.5 threshold) was among the alerting detectors in 17; onset times are relative to coarse slots |
| Spoofing raises cn0_rise / cn0_uniform / clock_jump / position_jump | Captured only in 2.4.2 and 2.4.13; otherwise spoofing looked like jamming (cn0_drop) |
| CV-prior soak: 0 alert epochs in 20 h | 86% alarm time on a driving car, 98% of the quiet window |
| Drag-off detected 6-9 s after start (GNSS-SDR files) | No drag-off reached the u-blox fix; 2.4.12 ramp moved it < 7 m |
| clock_drift: +20 ns/s detected, soak clean on 5 ns noise | Real SPP clock: alarms in quiet time (finding 6); 9 ns/s ramp not separable |
| Baseline frozen while alarmed protects against slow attackers | Real slow attackers (2.4.3 staircase) defeat it; a sub-alert freezes it for good (finding 2) |

## Tests

```
python3 -m unittest -v test_real_attack_replay.py
```

13 tests on the synthetic VAARA-shaped stream (`make_fixture.py`, built in memory): framing with
binary `$` bytes and a truncated trailing frame, L1/SBAS selection, the time axis across a +900 s
jump and a no-time gap, the replay findings (staircase now caught by `cn0_step` in C and D, step
drop after recovery now caught in C without the baseline what-if; both were missed with the scorer
at `dae8229`; time jump => `clock_jump` only with the receiver-time clock, quiet window clean in
A/B/D), static fix error, and the SPP `.pos`/`$CLK` readers. With the reworked scorer the two
tests that pinned the old defects were rewritten to pin the fixes.
Observed 2026-11-06: `/opt/homebrew/bin/python3` (3.14.7, no packages) `Ran 13 tests OK (skipped=1)`;
venv with pyubx2 1.4.1 (Python 3.13) `Ran 13 tests OK`. Mutation check (each alone, on a copy):
`MAX_STEP_S = 5000` fails 3 tests, dropping the baseline override fails 1, GPS L1 signal id "5"
fails 1, removing the receiver-time clock fails 1.

**Why no real fixture:** VAARA states no licence (no LICENSE file, GitHub reports none), so no bytes
of it are redistributed. The fixture copies only its layout (talkers, NMEA 4.11 signal ids, sentence
order, UBX frames before NMEA) and invented values. `results/*.json` hold derived per-window numbers.

## Limits

- One receiver, one antenna, one week. Thresholds were not tuned; every number is the shipped
  scorer on this data.
- Window labels are test slots or plan-shifted guesses; time to detect is relative to them and can be
  off by minutes (see Labels). Drive-by detection times mostly measure the drive to the jammer.
- Clock from receiver time sees only jumps > 5 s; from SPP it is too noisy here (finding 6). No
  clock from the receiver's own navigation solution exists in these logs (no NAV-CLOCK).
- SPP truth is self-referenced (median of clean fixes), not the NPRA ground-truth survey.
- Not done: Android GnssLogger / RINEX phone logs in VAARA, MON-SPAN spectrum on day 10, OSNMA on the
  logged Galileo SFRBX (`samples/osnma-authentication` adapter), RAIM/FDE in RTKLIB, day 12
  `Test_3` and the afternoon 2.5.x tests (not in the u-blox logs).
