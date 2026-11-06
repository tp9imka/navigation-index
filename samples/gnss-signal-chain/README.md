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
4. `extract_epochs.py` turns that into 1 Hz epochs (position, Doppler velocity, HDOP, receiver
   clock offset, per-SV C/N0); `score_scenario.py` feeds them into
   [`../gnss-interference-monitor/scorer.py`](../gnss-interference-monitor/scorer.py), including
   a no-fix epoch for every second the receiver produced no PVT.
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
| `extract_epochs.py` | pvt.mat (h5py) + RINEX 3 `S1C` => `epochs.jsonl` (lat/lon/h, ECEF velocity rotated to east/north/up, HDOP, clock offset, C/N0) |
| `score_scenario.py` | stdlib adapter => `InterferenceScorer`; `--ref-vel e,n` independent velocity reference, `--attack-t` for time-to-detect / false-alarm / silent-window metrics; optional rnx2rtkp cross-check line |
| `Makefile` | `make run`, `make score` (re-score `out/` on the host, both reference modes), `make check` |
| `out/` | real outputs of the run below (logs, epochs, power logs, rnx2rtkp `.pos`; `*.score.*` = constant-velocity prior, `*.score-ref.*` = static velocity reference) |

## Run

```bash
cd samples/gnss-signal-chain
./run.sh                    # or: make run
make score                  # re-score existing out/ with host python3 (stdlib only), both reference modes
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

Two full runs on the same day. The first (before this round's scorer work) is summarized
in the before/after table; everything else below is from the second run, which rebuilt the
image from scratch and regenerated all IQ (`out/` holds its files). Whole `./run.sh` 319 s
including the image build; per scenario (`out/timings.txt`) generate+mix 19-35 s, GNSS-SDR
15-74 s. Each mixed file is 600,000,000 bytes (`out/file_sizes.txt`), deleted after use.

| Scenario | 1 Hz PVT epochs (t range) | SVs | horiz. error vs truth | scorer alarm (CV prior / static ref) |
|---|---|---|---|---|
| clean | 107 (43-149 s) | 4 => 8 | median 2.9 m | 0 / 0 alarm epochs |
| overpower | 53 (49-102 s, gap at 81), then no PVT | 7 => 4 | median 4.8 m, stays on truth | raised t=81 (lost fix) / t=79 (velocity), held to the end |
| jamspoof | 27 (49-75 s), then no PVT | 6 | median 3.5 m before the burst | raised t=76 (lost fix), held to the end |
| dragoff | 101 (49-149 s) | 4 => 5 => 8 | 0.4 m at t=80, 99.0 m at t=100, 977.8 m at t=149 | raised t=89 / t=86, held to the end |

rnx2rtkp on GNSS-SDR's RINEX gives the same median errors to 0.1 m (clean 2.9 m, dragoff
91.3 m, final epoch 977.8 m); GNSS-SDR's PVT is itself RTKLIB-based, so this checks the
RINEX/PVT plumbing, not an independent algorithm.

### Before / after

Old = `scorer.py` before this round (git history), new = current. Attack onset for the
metrics: `dragoff` 60 s (spoofer ramp starts; the drag itself starts at 80 s),
`overpower` / `jamspoof` 75 s. "Silent" = longest run of seconds from the onset to the end
of the file with no alert (old: per-epoch verdict; a second with no PVT also counts as
silent because the old adapter fed no epoch). Static ref = `--ref-vel 0,0`.

| Scenario, run | Scorer | First alert | Silent after onset | Silent after first alert | Clean-run false alarms |
|---|---|---|---|---|---|
| dragoff, run 1 | old | t=67 (C/N0 rise + uniform) | 43 s (87-129 s, fix drifted 11 => 580 m) | 43 s | - |
| dragoff, run 1 | new, CV prior | t=67 | 7 s (60-66 s) | 0 (latched; `pos_drift` from t=104) | - |
| dragoff, run 2 | old | t=138 | 78 s (60-137 s, fix drifted to 738 m) | 1 s | - |
| dragoff, run 2 | new, CV prior | t=89 (`pos_drift`, fix 20.5 m off) | 29 s (60-88 s) | 0 | - |
| dragoff, run 2 | new, static ref | t=86 (`vel_mismatch` 3.1 m/s, fix 10.7 m off) | 26 s (60-85 s) | 0 | - |
| overpower, run 2 | old | t=85 (`jamming`, 1 epoch) | 64 s (86-149 s) | 64 s | - |
| overpower, run 2 | new, CV prior / static ref | t=81 (`lost-fix`) / t=79 (`vel_mismatch`) | 6 s / 4 s | 0 | - |
| jamspoof, run 2 | old | none | 75 s (whole attack) | - | - |
| jamspoof, run 2 | new, both modes | t=76 (`lost-fix`) | 1 s | 0 | - |
| clean, runs 1 and 2 | old / new both modes | - | - | - | 0 / 0 / 0 epochs |

Run 2's drag-off sat on 4-5 SVs until t=107 (run 1 had 6), so its C/N0 rise never reached
the uniformity check's 6-SV minimum and the old scorer stayed quiet until t=138. The new
detectors do not depend on that: from the drag start (t=80) they fired after 9 s (CV prior)
and 6 s (static reference), while the fix was 10-21 m off truth. Before t=80 the spoofer is
code/carrier-aligned and only C/N0 and input power move; that 26-29 s stretch is still
silent (see finding 3 below).

### clean (`out/clean.score.txt`)

```
    t nSV meanCN0 sdCN0    herr_m    clk_ns  jam spoof alarm verdict / reasons
   43   4    45.1   1.2      17.5    -144.4 0.00  0.00     - clean
   48   5    43.9   2.2       0.7     -32.7 0.00  0.00     - clean
   72   6    43.1   2.9       3.4      16.4 0.00  0.00     - clean
   78   7    42.8   3.0       0.9     -18.7 0.00  0.00     - clean
  126   8    42.1   3.3       4.8     -40.9 0.00  0.00     - clean
epochs 107 (107 with fix), alert epochs 0, false alerts before attack 0 (latched 0)
```

`out/clean.score-ref.txt` (static reference, velocity check on) is identical: 0 alert epochs.

### dragoff (`out/dragoff.score-ref.txt`, selected epochs)

```
    t nSV meanCN0 sdCN0    herr_m    clk_ns  jam spoof alarm verdict / reasons
   69   5    50.4   1.1       1.7     -32.7 0.30  0.30     - clean / median C/N0 rise +5.0 dB; AGC +130% vs baseline
   80   5    51.2   0.7       3.4     -49.9 0.30  0.30     - clean / median C/N0 rise +5.3 dB; AGC +186% vs baseline
   85   5    49.3   0.5       6.3     -46.3 0.30  0.00     - clean / AGC +161% vs baseline
   86   5    49.0   0.6      10.7     -53.5 0.30  0.60    ON spoofing / AGC +162% vs baseline; GNSS velocity 3.1 m/s off reference (6.9 sigma)
      ALARM raised t=86: spoofing
   88   5    47.8   0.9      16.2     -43.8 0.30  1.00    ON spoofing / AGC +161% vs baseline; position 15 m off reference track (7.2 sigma, CUSUM 10.6); GNSS velocity 3.8 m/s off reference (8.6 sigma)
   92   5    46.6   0.9      35.7     -32.4 0.30  1.00    ON spoofing / AGC +161% vs baseline; position 35 m off reference track (16.2 sigma, CUSUM 16.0); GNSS velocity 6.4 m/s off reference (14.3 sigma)
  149   8    49.3   1.0     977.8     -43.6 0.30  1.00    ON spoofing / AGC +143% vs baseline; C/N0 spread only 1.0 dB over 8 SVs; position 977 m off reference track (261.8 sigma, CUSUM 16.0); GNSS velocity 20.0 m/s off reference (88.9 sigma)
epochs 101 (101 with fix), alert epochs 64, false alerts before attack 0 (latched 0)
attack t=60: first alert t=86.0, first per detector {'agc_change': 66.0, 'cn0_rise': 69.0, 'vel_mismatch': 86.0, 'pos_drift': 88.0, 'cn0_uniform': 108.0}
longest silent run after attack: instantaneous 26 epochs (60.0-85.0), latched alarm 26 epochs; after the first alert 0
```

With the constant-velocity prior (`out/dragoff.score.txt`) the first alert is
`position 19 m off constant-velocity track (4.9 sigma, CUSUM 9.3)` at t=89. GNSS-SDR's
Doppler velocity follows the spoofer early: 1.4 m/s east at t=83, 3.1 m/s at t=86, 20 m/s
from t=120. With a reference that says "not moving" this is the fastest cue. No loss of lock
in the GNSS-SDR log for `dragoff`; the receiver followed the spoofer smoothly to ~1 km
(`out/dragoff.gnss-sdr.events.txt` still lists 5 observable resets and one -79 ms clock
correction; the clean run lists one -60 ms correction, so a single correction is not by
itself an attack sign). Other signatures, in order: C/N0 rise and flattening while aligned
(mean 45.0 => 51.2 dB-Hz), C/N0 dipping back once the drag starts, more SVs (5 => 8, the
spoofer gives low-elevation satellites full power), input power +26 % at t=66 rising to
+227 % on the file-level proxy, and no clock jump (clk_ns within -68 to +76 ns from t=64).

### overpower and jamspoof: denial, not capture

An unaligned spoofer did not capture GNSS-SDR 0.0.19 in this setup (both runs). In
`overpower` the tracking loops stayed on the authentic signals (position within 35 m of
truth) while C/N0 dropped ~5 dB; channels that lost lock re-acquired spoofer PRNs, the
solver saw a mixed authentic/spoofed set, logged 26 `Sent reset to observables` and two
-80 ms clock corrections (`out/overpower.gnss-sdr.events.txt`), and output no PVT after
t=102 s. In `jamspoof` the burst (11,074,088 8-bit samples clipped, `out/jamspoof.mix.log`)
dropped all channels; GNSS-SDR then logged 28 observable resets and clock corrections of
-59/-60 ms and produced no PVT for the remaining 74 s. A separate debug run in the first session with
`Observables.dump=true` showed post-attack pseudoranges offset by ~-23,982 km (~80 ms) from
both the authentic and spoofer-only references, i.e. the receiver time base was corrupted
after the mixed-set solutions, so every solution failed RTKLIB's chi-square test. Treat
this as a GNSS-SDR 0.0.19 behavior in this configuration, not a general result.

What the new scorer reports (`out/overpower.score.txt`):

```
   80   7    37.3   3.1       6.5    -101.4 0.30  0.00     - clean / AGC +173% vs baseline
   81   0     nan   nan       nan         - 0.30  0.00    ON lost-fix / AGC +174% vs baseline; no fix for 1 s (last fix t=80, C/N0 not reported)
      ALARM raised t=81: lost-fix
   83   4    39.2   1.9       2.3      25.0 0.30  0.50    ON spoofing / AGC +174% vs baseline; clock rate +185.1 ns/s vs learned -4.1 ns/s (+9.4 sigma)
   85   4    39.0   1.5       9.0     109.4 0.80  0.50    ON jamming+spoofing / C/N0 drop >= 6 dB or lost on 6/7 SVs; AGC +173% vs baseline; clock rate -188.6 ns/s vs learned -4.1 ns/s (-9.1 sigma)
  103   0     nan   nan       nan         - 0.30  0.00    ON lost-fix / AGC +174% vs baseline; no fix for 1 s (last fix t=102, C/N0 not reported)
  149   0     nan   nan       nan         - 0.30  0.00    ON lost-fix / AGC +155% vs baseline; no fix for 47 s (last fix t=102, C/N0 not reported)
```

`clock_drift` catches the corrupted time base while PVT still exists (t=83-102); it is the
only new detector that fires on the receiver's internal state rather than on the fix.

## Scorer adapter: what maps and what does not

| `Epoch` field | Source here |
|---|---|
| `cn0` | GNSS-SDR RINEX 3 `S1C` per SV; `None` (not reported) on seconds without PVT, because GNSS-SDR writes no RINEX epoch then |
| `lat`, `lon`, `fix_ok` | `pvt.mat` latitude / longitude; `fix_ok=False` for every second after the first fix with no PVT, up to the end of the power log |
| `vel_e`, `vel_n`, `hdop` | `pvt.mat` `vel_x/y/z` (ECEF, rotated to east/north) and `hdop` |
| `ref_vel_e`, `ref_vel_n` | only with `--ref-vel`; `0,0` models a platform that knows it is static (IMU at rest, parked vehicle). The truth is static in every scenario, so this is the best case for the reference |
| `clk_bias_ns` | `pvt.mat` `user_clk_offset` x 1e9; `clk_drift_ns_s` left None (the clock drift GNSS-SDR computes is not in the 0.0.19 dump), so the scorer differences the bias |
| `agc_cnt` | **proxy only**: per-second mean power of the input file from `mix_iq.py`. It is not a receiver AGC (it rises where an AGC count would fall); the scorer only tests the size of the relative change |
| `jam_ind`, `spoof_det_state`, `jamming_state` | no GNSS-SDR equivalent, None |

Findings from the first run and what happened to them:

1. **Missed drag phase** (t=87-129 s `clean` in run 1 while the fix walked 11 => ~580 m):
   addressed by `pos_drift` / `vel_mismatch` and the latched alarm. Run 2: detected 6-9 s
   after the drag began, no silent epoch afterwards.
2. **SPP noise vs `MAX_SPEED_MPS`** (single-epoch SPP on a static receiver implied up to
   14 m/s; `--max-speed 5` made the clean run raise `position_jump`): unchanged, the adapter
   still defaults to 50 m/s. `pos_drift` is the better tool for slow motion.
3. **Power rise counted as jamming only**: unchanged. It is now the main reason the aligned
   phase (t=60-85 in run 2) stays silent: `cn0_rise` 0.3 lands in the spoof family and
   `agc_change` 0.3 in the jam family, so neither reaches 0.5. In `jamspoof` the burst moved
   input power by +29,109 % and still scored only 0.3 (the lost fix raised the alarm one
   second later). A combined "power up and C/N0 up" rule, or `agc_change` in both families,
   is the next fix to try.
4. **Denial invisible when PVT stops**: addressed by `lost_fix` plus the adapter's no-fix
   epochs (jamspoof alarm at t=76, overpower at t=81, both held to the end).

## Caveats

- Thread scheduling makes GNSS-SDR runs not bit-identical: earlier full runs gave 59 vs 54
  `overpower` epochs; this session's two runs gave first fixes at t=43 vs t=49 in `dragoff`,
  6 vs 4-5 SVs in its aligned phase, and first old-scorer alerts at t=67 vs t=138.
- `--ref-vel 0,0` is a perfect reference for a static truth. A real IMU drifts; the scorer
  models that with `REF_VEL_SIGMA_MPS` (0.05 m/s) growing the reference error while frozen.
- Noise is ideal AWGN; no multipath, no front-end filtering or oscillator noise; the receiver
  clock is effectively perfect, so the solved clock bias is SPP noise, within -188..+313 ns across the runs.
- GNSS-SDR C/N0 for the +8 dB spoofer read 49-51 dB-Hz, not the 55 dB-Hz the mixer
  targets; the cause was not investigated.
- GPS L1 C/A only. Not validated against a hardware receiver.
