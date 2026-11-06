# GNSS interference monitor: receiver telemetry + ADS-B area map

## Goal

Detect GNSS jamming and spoofing from data you already have, at two scales:

1. **One receiver** - score each epoch of u-blox telemetry (C/N0, AGC, CW jamming
   indicator, clock, position, the receiver's own spoofing/jamming flags) with
   transparent heuristics, and say *why* an epoch looks wrong.
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
| `scorer.py` | stdlib, run-verified. `Epoch` dataclass in, `Assessment` (jam_score, spoof_score, verdict, reasons) out |
| `test_scorer.py` | 8 unit tests on synthetic epochs |
| `adsb_area_map.py` | stdlib, run-verified. readsb `aircraft.json` snapshots => per-cell good/bad aircraft, GPSJam percentage, level |
| `test_adsb_area_map.py` | 6 unit tests |
| `fixtures/aircraft_demo.json` | synthetic readsb snapshot (made-up hex ids and coordinates) |
| `ubx_monitor.py` | pyubx2 adapter. Replay of a `.ubx` file run-verified on the synthetic capture; live `--port` mode not verified (no receiver) |
| `gen_synthetic_ubx.py` | pyubx2 generator: 180 s of 1 Hz NAV-PVT/SAT/STATUS/CLOCK + MON-RF + SEC-SIG with a jamming and a spoofing episode (invented values) |
| `fixtures/synthetic.ubx` | its output (60 KB, seed 11) |
| `test_ubx_replay.py` | regenerates the capture, replays it through `ubx_monitor.run`, checks every epoch's verdict |
| `requirements.txt` | pinned `pyubx2==1.4.1` (+ `pyserial` for a live port) |

## Heuristics in `scorer.py`

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

Weights add up per family, capped at 1.0; >= 0.5 raises the verdict. The C/N0 and AGC
baseline is an EWMA that only learns from epochs scoring <= 0.2, so a long jamming event
does not become the new normal. All thresholds are named constants at the top of
`scorer.py` - they are starting points, not calibrated limits.

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

Observed (python3.14.7, 2026-11-06):

```
test_broadband_jamming ... ok
test_clean_sky_stays_clean ... ok
test_jamming_does_not_pollute_baseline ... ok
test_no_baseline_no_cn0_drop_verdict ... ok
test_receiver_flag_alone_raises_spoofing ... ok
test_sparse_epoch_without_optional_fields ... ok
test_spoofer_uniform_power_clock_and_position_jump ... ok
test_uniform_check_needs_enough_svs ... ok
test_aircraft_counted_once_per_cell_and_bad_wins ... ok
test_aircraft_without_quality_field_is_not_counted_as_good ... ok
test_gps_ok_before_marks_bad ... ok
test_gpsjam_formula_discounts_one_bad_aircraft ... ok
test_red_cell ... ok
test_stale_position_ignored ... ok
----------------------------------------------------------------------
Ran 14 tests in 0.004s

OK
```

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

A negative control was run once: with the `cn0_drop` weight set to 0,
`test_broadband_jamming` fails, so the test does exercise that detector.

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

Observed (pyubx2 1.4.1, Python 3.12.14, 2026-11-06):

```
t=  216000.0 clean             jam=0.00 spoof=0.00
t=  216060.0 jamming           jam=1.00 spoof=0.00 C/N0 drop >= 6 dB or lost on 10/10 SVs; AGC -46% vs baseline; jamInd 160
t=  216090.0 clean             jam=0.00 spoof=0.00
t=  216120.0 spoofing          jam=0.00 spoof=1.00 median C/N0 rise +9.2 dB; C/N0 spread only 0.5 dB over 10 SVs; clock bias jump +5001 ns; implied speed 300 m/s
t=  216161.0 clean             jam=0.00 spoof=0.00
epochs per verdict: clean=109, jamming=30, spoofing=41
```

Without `--changes-only` every epoch prints. Two details from the full run: from 121 s
the spoof score drops to 0.65 (only the C/N0 rise and uniformity checks still fire) until
the receiver flag joins at 130 s; and 160 s is still `spoofing` (0.70) because the
spoofer switching off is itself a -5001 ns clock jump and a 1081 m/s position jump. That
is why there are 41 spoofing epochs for a 40 s episode.

`test_ubx_replay` asserts every epoch's verdict (15 tests in total, all OK). Negative
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
`lat`, `lon` (already scaled to degrees); NAV-SAT `numSvs`, `gnssId_NN`, `svId_NN`,
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
   "do not trust GNSS" input.
5. Push per-cell levels to a TAK map with `samples/mavlink-to-tak-cot` style CoT shapes.

## Pitfalls

- Thresholds are not portable. An active antenna, cable loss or a car roof moves AGC and
  C/N0 baselines by several dB. Learn the baseline on each install.
- `cn0_uniform` misfires indoors, under foliage or with few SVs; `CN0_UNIFORM_MIN_SVS`
  guards only the last case.
- Position and clock jumps only work across consecutive epochs; after a receiver reset the
  first epoch has no reference.
- The receiver's own `spoofDetState` / `spoofingState` is one input, not ground truth.
  Check how your firmware behaves against your threat (replay, meaconing, coherent
  takeover) before relying on it.
- M8 receivers do not support CFG-VALSET; enable messages with UBX-CFG-MSG or u-center.
- ADS-B NACp also drops for avionics faults and some aircraft never report it. The `-1`
  in the GPSJam formula and `MIN_AIRCRAFT` exist to keep single aircraft from painting a cell red.
