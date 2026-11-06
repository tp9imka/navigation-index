<!-- about: repo:osqzss/gps-sdr-sim, repo:gnss-sdr/gnss-sdr, repo:rtklibexplorer/rtklib -->
# GNSS signal chain: gps-sdr-sim => GNSS-SDR => interference scorer (file-based)

> **FILE-BASED ONLY. NEVER TRANSMIT.** Everything here generates, mixes and processes IQ
> *files* inside Docker. Do not feed these files to an SDR transmitter: radiating GNSS-like
> signals (authentic-looking or spoofed) is illegal in almost every jurisdiction without an
> authorization and a shielded/conducted test setup, and it can endanger aviation and other
> users. Nothing in this sample opens an SDR device.

## Goal

A signal-level testbed for spoofing and jamming detection that needs no hardware:

1. `gps-sdr-sim` synthesizes GPS L1 C/A baseband for a static receiver from a public broadcast
   ephemeris.
2. `mix_iq.py` adds thermal noise and, per scenario, a second gps-sdr-sim stream (the
   spoofer) with a power offset, time offset and on-time, and/or a broadband noise burst.
3. GNSS-SDR processes each 8-bit IQ file (file source) into PVT, RINEX and a PVT dump.
4. `extract_epochs.py` turns that into 1 Hz epochs (position, receiver clock offset, per-SV
   C/N0); `score_scenario.py` feeds them, unchanged, into
   [`../gnss-interference-monitor/scorer.py`](../gnss-interference-monitor/scorer.py).
5. RTKLIB demo5 `rnx2rtkp` re-solves GNSS-SDR's RINEX as a cross-check.

## Repos used

| Repo | Role | Version used |
|---|---|---|
| [osqzss/gps-sdr-sim](https://github.com/osqzss/gps-sdr-sim) | IQ generator; ships `brdc0010.22n` (GPS broadcast nav, 2022-01-01) used as the ephemeris | commit `28ca29a` (2025-01-07), built with `gcc -O3` |
| [gnss-sdr/gnss-sdr](https://github.com/gnss-sdr/gnss-sdr) | software receiver: acquisition, tracking, nav decoding, RTKLIB-based PVT | 0.0.19 from Ubuntu 24.04 `noble/universe` (prebuilt arm64 + amd64) |
| [rtklibexplorer/RTKLIB](https://github.com/rtklibexplorer/RTKLIB) | `rnx2rtkp` SPP on GNSS-SDR's RINEX output | tag `v2.5.1`, cmake build |

Image choice: Ubuntu's `gnss-sdr` package avoids a ~30-60 min source build and is native on
arm64. The maintainer image `carlesfernandez/docker-gnsssdr:latest` is also multi-arch
(`docker manifest inspect` lists amd64, arm, arm64 on 2026-11-06) but was not tried here.

Ephemeris: NASA CDDIS needs a login. This sample uses the nav file shipped in the gps-sdr-sim
repo so the run is offline and reproducible. For another date, BKG's IGS mirror
(`https://igs.bkg.bund.de/root_ftp/IGS/BRDC/<yyyy>/<doy>/`) serves daily merged broadcast nav
without login, but those are RINEX 3 mixed-constellation files; gps-sdr-sim's parser expects a
RINEX 2 GPS nav file (`*.yyn`), so a conversion step (e.g. RTKLIB `convbin`) would be needed.
That path was not tested.

## Files

| File | What |
|---|---|
| `docker/Dockerfile` | Ubuntu 24.04 + gnss-sdr 0.0.19 + gps-sdr-sim + rnx2rtkp + numpy/h5py |
| `run.sh` | host entry point: builds image, runs `pipeline.sh` in a container, copies `out/`, scores |
| `pipeline.sh` | in-container: per scenario, gps-sdr-sim => FIFO => `mix_iq.py` => `.bin` => GNSS-SDR => epochs => rnx2rtkp |
| `gnss-sdr.conf.in` | GNSS-SDR config template (File_Signal_Source, `ibyte`, 2 Msps, 8 GPS L1 C/A channels, Single PVT, PVT dump as .mat) |
| `mix_iq.py` | numpy mixer: noise, spoofer power/ramp/delay, jam burst, per-second input power log |
| `spoof_trajectory.py` | stdlib, writes a gps-sdr-sim `-x` 10 Hz lat/lon/h track (offset, hold, accel) |
| `extract_epochs.py` | pvt.mat (h5py) + RINEX 3 `S1C` => `epochs.jsonl` |
| `score_scenario.py` | stdlib adapter => `InterferenceScorer`; optional rnx2rtkp cross-check line |
| `Makefile` | `make run`, `make score` (re-score `out/` on the host), `make check` |
| `out/` | real outputs of the run below (logs, epochs, scores, power logs, rnx2rtkp `.pos`) |

## Run

```bash
cd samples/gnss-signal-chain
./run.sh                    # or: make run
make score                  # re-score existing out/ with host python3 (stdlib only)
SCENARIOS="clean dragoff" KEEP_IQ=1 ./run.sh   # subset, keep the 8-bit IQ files in the volume
```

Knobs (env): `DUR=150 FS=2000000 LAT LON H CN0_REF=47 ATTACK_T=75 JAM_S=5 JAM_JN_DB=25
SPOOF_GAIN_DB=8 SPOOF_DELAY=10 DRAG_ON=60 DRAG_RAMP=10 DRAG_HOLD=80`.

Large files live in the Docker volume `gnss-signal-chain-work` (the host path is not bind-
mounted; files move with `docker cp`). gps-sdr-sim writes 16-bit IQ to a FIFO, so only the
mixed 8-bit file touches disk: `DUR * FS * 2` bytes = **600,000,000 bytes per scenario** at the
defaults, deleted after GNSS-SDR unless `KEEP_IQ=1`. (A first version that stored the 16-bit
streams, 1,199,200,000 bytes each, filled a shared Docker VM disk.)

## Scenarios

Truth: static receiver at 30.286502 N, 120.032669 E, 100 m (gps-sdr-sim README example),
start 2022-01-01 00:00:00 GPST, 150 s. Noise is set so a 0 dB-gain satellite has C/N0
`CN0_REF` = 47 dB-Hz; authentic satellites keep gps-sdr-sim's path loss / antenna pattern. The
spoofer streams use `-p 128` (all satellites at equal power, a single-transmitter signature)
and are mixed at +8 dB over that reference.

| Scenario | What is in the file |
|---|---|
| `clean` | authentic + noise |
| `overpower` | + unaligned spoofer from t=75 s: track starts 2 km N / 2 km E and moves east at 20 m/s, 5 us late (10 samples) |
| `jamspoof` | as `overpower` + 5 s broadband noise burst at J/N 25 dB (t=75-80 s) to break lock first |
| `dragoff` | + code/carrier-aligned spoofer: same generator at the true position, ramped from -20 to +8 dB over t=60-70 s, holds until t=80 s, then accelerates east at 0.5 m/s^2 to 20 m/s |

The `dragoff` alignment is exact only because both streams come from the same deterministic
generator with the same nav file and start time - a best case for the attacker that a real
spoofer achieves only approximately.

## Results (ran it, 2026-11-06, Apple Silicon, Docker arm64, 4 vCPU)

Timings (`out/timings.txt`): image build ~5 min first time (apt + RTKLIB compile). Per scenario:
generate+mix 18 s (clean) / 31-32 s (two gps-sdr-sim streams), GNSS-SDR 15-61 s (the clean run
is slower because it keeps 8 channels in lock and solving to the end). Whole `run.sh` 223 s.

| Scenario | 1 Hz PVT epochs (t range) | SVs | mean C/N0 | horiz. error vs truth | scorer |
|---|---|---|---|---|---|
| clean | 107 (43-149 s) | 4-7 | 42.2-45.1 dB-Hz | median 3.0 m | 0 alerts |
| overpower | 54 (43-102 s), then no PVT | 5 => 4 | 43.9 => 38.5 after t=75 | median 8.7 m, stays on truth | 1 alert (`jamming` at t=85) |
| jamspoof | 33 (43-75 s), then no PVT | - | - | - | 0 alerts (no epochs after the attack) |
| dragoff | 107 (43-149 s) | 6 => 8 | 45.5 => 51.1 (aligned) => 45.4 (drag) => 49.2 | 0.5 m at t=80, 98.9 m at t=100, 977.8 m at t=149 | 39 alert epochs, first t=67 |

First fix: GNSS-SDR prints `First position fix at 2022-Jan-01 00:00:24.1 UTC` (= 42 s GPST into
the file, after subframes 1-3 are decoded). rnx2rtkp on GNSS-SDR's RINEX gives the same
median errors to 0.1 m (clean 3.0 m, dragoff final epoch 977.8 m); GNSS-SDR's PVT is itself
RTKLIB-based, so this checks the RINEX/PVT plumbing, not an independent algorithm.

### clean (`out/clean.score.txt`)

```
    t nSV meanCN0 sdCN0    herr_m    clk_ns  jam spoof verdict / reasons
   43   4    45.1   1.2      17.6    -144.5 0.00  0.00 clean
   48   5    43.9   2.2       0.7     -33.5 0.00  0.00 clean
   78   6    43.4   2.9       1.9     -21.3 0.00  0.00 clean
   96   7    42.5   3.4       1.4      -9.8 0.00  0.00 clean
epochs 107, alert epochs 0, first alert t=None
```

### dragoff (`out/dragoff.score.txt`, selected epochs)

```
    t nSV meanCN0 sdCN0    herr_m    clk_ns  jam spoof verdict / reasons
   64   6    45.5   1.9       2.4     -34.3 0.00  0.35 clean / C/N0 spread only 1.9 dB over 6 SVs
   67   6    48.0   1.4       0.8     -31.1 0.30  0.65 spoofing / median C/N0 rise +4.0 dB; AGC +49% vs baseline; C/N0 spread only 1.4 dB over 6 SVs
   80   6    51.1   0.8       0.5     -32.9 0.30  0.65 spoofing / median C/N0 rise +7.4 dB; AGC +194% vs baseline; C/N0 spread only 0.8 dB over 6 SVs
   86   6    48.9   0.6       9.9     -27.1 0.30  0.65 spoofing / median C/N0 rise +4.6 dB; ...
   87   6    48.3   0.8      11.3     -31.4 0.30  0.35 clean / AGC +168% vs baseline; C/N0 spread only 0.8 dB over 6 SVs
  100   6    45.4   1.3      98.9     -46.3 0.30  0.35 clean / AGC +168% vs baseline; C/N0 spread only 1.3 dB over 6 SVs
  110   8    46.0   2.1     224.4     -43.4 0.30  0.00 clean / AGC +168% vs baseline
  120   8    47.4   2.2     398.8     -30.1 0.30  0.00 clean / AGC +168% vs baseline
  130   8    48.9   1.6     597.0     -47.9 0.30  0.65 spoofing / median C/N0 rise +4.0 dB; ...
  149   8    49.2   0.9     977.8     -43.6 0.30  0.65 spoofing / median C/N0 rise +5.0 dB; AGC +150% vs baseline; C/N0 spread only 0.9 dB over 8 SVs
epochs 107, alert epochs 39, first alert t=67.0
RTKLIB rnx2rtkp SPP on GNSS-SDR RINEX: 107 common epochs, horizontal error vs truth median 64.1 m (GNSS-SDR PVT 64.1 m), last epoch 977.8 m (GNSS-SDR 977.8 m)
```

No loss of lock in the GNSS-SDR log for `dragoff`: the receiver followed the spoofer smoothly
to ~1 km. Observable signatures, in order:

- **C/N0 rise and flattening** while aligned (mean 45.5 => 51.1 dB-Hz, spread 1.9 => 0.8 dB)
  because the spoofer adds coherently to the authentic signal and has equal power per SV.
- **C/N0 dips back** (51.1 => 45.4 dB-Hz at t=80-100) once the drag starts: the authentic
  signal decorrelates and becomes interference.
- **More SVs** (6 => 8): the spoofer gives low-elevation satellites full power.
- **Input power** (+168 % on the file-level proxy, see below).
- **No clock jump** (clk_ns stays within -10 to -48 ns from t=64 s) and **no position jump**: 20 m/s
  is under the scorer's 50 m/s limit.

### overpower and jamspoof: denial, not capture

An unaligned spoofer did not capture GNSS-SDR 0.0.19 in this setup. In `overpower` the
tracking loops stayed on the authentic signals (position stayed within 34 m of truth) while
their C/N0 dropped ~5 dB from the added power; channels that lost lock re-acquired spoofer
PRNs (e.g. `PRN 28 ... CN0=51.02`), the solver then saw a mixed authentic/spoofed set, logged
25 `Sent reset to observables` and 5 clock corrections of -60/-80 ms (`out/overpower.gnss-sdr.events.txt`),
and output no PVT after t=102 s. In `jamspoof` the burst (55 % of 8-bit samples clipped, power
log `out/jamspoof.power.csv`) dropped all channels; after the burst GNSS-SDR re-acquired spoofer
signals at 49-50 dB-Hz but logged 24 observable resets and one -80 ms correction and produced no
PVT for the remaining 70 s. A separate debug run with `Observables.dump=true` (same
parameters) showed post-attack pseudoranges offset by ~-23,982 km (~80 ms) from both the
authentic and spoofer-only references, i.e. the receiver time base was corrupted after the
mixed-set solutions, so every solution failed RTKLIB's chi-square test. Treat this as a
GNSS-SDR 0.0.19 behavior in this configuration, not a general result for receivers.

## Scorer adapter: what maps and what does not

| `Epoch` field | Source here |
|---|---|
| `cn0` | GNSS-SDR RINEX 3 `S1C` per SV |
| `lat`, `lon` | `pvt.mat` latitude / longitude |
| `clk_bias_ns` | `pvt.mat` `user_clk_offset` x 1e9; `clk_drift_ns_s` left None |
| `agc_cnt` | **proxy only**: per-second mean power of the input file from `mix_iq.py`. It is not a receiver AGC (it rises where an AGC count would fall); the scorer only tests the size of the relative change |
| `jam_ind`, `spoof_det_state`, `jamming_state` | no GNSS-SDR equivalent, None |

Findings about the scorer (not edited; reported here for its owner):

1. **Missed drag phase.** In `dragoff`, t=87-129 s scored `clean` while the position walked from
   11 m to ~580 m off truth: the C/N0 rise dipped under 4 dB as the signals decorrelated, and
   a slow drag never trips the speed test. A drift test against a motion model (or IMU/INS
   cross-check) is the missing indicator.
2. **SPP noise vs `MAX_SPEED_MPS`.** Unsmoothed single-epoch SPP on a static receiver implied up
   to 14 m/s here; with `--max-speed 5` the clean run raised `position_jump` repeatedly, and those
   hits (spoof 0.35 > `BASELINE_MAX_SCORE` 0.2) also stop the baseline from updating. The adapter
   defaults to 50 m/s.
3. **Power rise counted as jamming only.** `agc_change` is in `JAM_WEIGHTS` only, so a +168 %
   power rise from a spoofer adds 0.3 to the jam score and nothing to the spoof score.
4. **Denial is invisible when PVT stops.** In `jamspoof` the scorer gets no epochs after t=75,
   so it raises nothing; an absence-of-epoch / lost-fix indicator would catch it.

## Caveats

- Thread scheduling makes GNSS-SDR runs not bit-identical: two full runs gave 59 vs 54
  `overpower` epochs and first `dragoff` alert at t=68 vs t=67.
- Noise is ideal AWGN; no multipath, no front-end filtering or oscillator noise; the receiver
  clock is effectively perfect, so the solved clock bias is SPP noise, within -188..+313 ns across the runs.
- GNSS-SDR C/N0 for the +8 dB spoofer read 49-51 dB-Hz, not the 55 dB-Hz the mixer
  targets; the cause was not investigated.
- GPS L1 C/A only. Not validated against a hardware receiver.
