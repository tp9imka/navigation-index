# GNSS-disciplined clock: holdover per oscillator grade, and a slow time-walk spoof

<!-- about: repo:aewallin/allantools, repo:nwtime/linuxptp, repo:gitlab.com/chrony/chrony, repo:andrewbcn/stm32-gpsdo, repo:tum-esi/ptpsec -->

## Goal

Answer three questions a timing-resilience hackathon team gets asked, with numbers that come
from a run rather than a slide:

1. If GNSS goes away, how fast does my clock drift for a TCXO, OCXO, rubidium or chip-scale
   atomic clock?
2. If someone slowly walks GNSS time instead of jamming it, does the disciplined clock follow?
3. What catches the walk: the clock's own steering history, or a second time source?

Primer and holdover math: [docs/timing-resilience.md](../../docs/timing-resilience.md).

## What it simulates

| Item | Value |
|---|---|
| Oscillator model | phase `x` (local minus true time) driven by white FM noise at the grade's ADEV(1 s), linear aging, optional 24 h sinusoidal temperature term |
| Grades | TCXO, OCXO, Rb from J. R. Vig, "Introduction to Quartz Frequency Standards", table 1 (stability at 1 s, aging/year, temperature spec). CSAC from the Microchip SA65 datasheet DS00003478F (9/25): ADEV 3e-10 at 1 s, typical aging <9e-10/month, +/-3e-10 over temperature |
| Initial frequency offset | one year of the grade's aging, random sign (assumption: unadjusted for a year) |
| GNSS 1PPS | 1 Hz, 20 ns 1-sigma white noise (assumption; set with `--sigma-pps`) |
| Discipline loop | type-2 PLL, damping 0.707. Fast-lock time constant 30 s for the first 30 min, then the crossover where GNSS white PM noise meets the oscillator white FM noise, clamped to 30-2000 s and capped so the loop lag on the temperature ramp stays below the PPS noise |
| Holdover | steering frozen at its mean over the last 10 min; 24 h outage stepped at 10 s |
| Spoof | after 2 h settle + 2 h detector training, GNSS time walks off at a constant rate for 2 h (0.5, 2, 10 ns/s by default) |
| Internal monitor | every minute compares the 10-min mean steering with its value 30 min earlier; threshold 6x the RMS seen in training; 3 consecutive hits => alarm |
| Cross-source monitor | second time source (think PTP over a network) with 100 ns noise and an unknown 300 ns constant asymmetry (assumptions); 1-min mean of GNSS minus second source vs the training baseline; threshold 6 sigma + 100 ns margin; 2 consecutive hits => alarm |
| Guard | on alarm, freeze steering at its value 30 min before the alarm (holdover) |

The noise model is white FM plus aging (plus temperature when enabled). Real oscillators also
have flicker and random-walk FM, retrace, warm-up and vibration sensitivity, so the holdover
numbers here are a floor for a given datasheet, not a prediction for a real unit. Measure your
own unit's ADEV with allantools before trusting any of this.

## Repos this sample explains

| Repo | Use it for |
|---|---|
| [aewallin/allantools](https://github.com/aewallin/allantools) | ADEV/MDEV/TDEV from your own logged phase data, plus noise generators that include flicker FM |
| [linuxptp](https://github.com/nwtime/linuxptp) / [chrony](https://gitlab.com/chrony/chrony) | the real servos: `ts2phc`/`phc2sys` and chrony's refclock driver discipline a PHC or system clock from 1PPS |
| [AndrewBCN/STM32-GPSDO](https://github.com/AndrewBCN/STM32-GPSDO) | a real cheap GPSDO firmware whose loop you could swap for the one here |
| [tum-esi/ptpsec](https://github.com/tum-esi/ptpsec) | the network-side counterpart: detecting delay attacks on the PTP second source itself |

## Prerequisites

Python 3.10+ (run on 3.14.7). No third-party packages.

## Run

```bash
cd samples/timing-holdover
python3 timing_holdover.py                       # 20 holdover runs per grade, spoof rates 0.5 2 10 ns/s
python3 timing_holdover.py --temp-fraction 0.3   # harsher temperature swing
python3 timing_holdover.py --sigma-pps 5         # timing-grade receiver with sawtooth correction
python3 timing_holdover.py --json out.json
python3 -m unittest -v test_timing_holdover      # 9 tests
```

## Output (ran on 2026-11-06, Python 3.14.7, default arguments, about 5 s)

```
grades: TCXO adev(1s)=1e-09 aging=5e-07/yr temp=5e-07 [Vig table 1], CSAC adev(1s)=3e-10 aging=1.1e-08/yr temp=3e-10 [Microchip SA65 DS00003478F], OCXO adev(1s)=1e-12 aging=5e-09/yr temp=1e-09 [Vig table 1], Rb adev(1s)=3e-12 aging=2e-10/yr temp=3e-10 [Vig table 1]

Holdover after 6 h of GNSS discipline, 20 runs, no temperature term
grade   loop tc  locked rms  y_err@HO |             1 min |            10 min |               1 h |               4 h |              24 h
TCXO      1200s     30.2 ns   2.5e-11 |  22.7 ns/ 46.8 ns |  23.1 ns/ 66.7 ns | 145.9 ns/328.7 ns |  1.67 us/ 2.43 us | 59.58 us/64.26 us
CSAC      2000s      7.9 ns   6.5e-12 |   4.9 ns/ 14.2 ns |   7.3 ns/ 13.9 ns |  19.2 ns/ 51.5 ns |  89.4 ns/212.8 ns |  1.27 us/ 2.41 us
OCXO      2000s      1.0 ns   4.1e-13 |   0.7 ns/  1.4 ns |   0.8 ns/  1.8 ns |   2.1 ns/  5.7 ns |  19.7 ns/ 32.0 ns | 610.0 ns/680.7 ns
Rb        2000s      0.5 ns   3.9e-13 |   0.3 ns/  0.8 ns |   0.3 ns/  1.2 ns |   1.5 ns/  4.0 ns |   5.2 ns/ 14.7 ns |  43.8 ns/107.5 ns
cells: median / 95th percentile |time error| after the GNSS outage starts
analytic |y_err|*t + D*t^2/2 + adev1*sqrt(t) (+ temp) with the median y_err:
  TCXO   1 min=9.3 ns  10 min=42.6 ns  1 h=254.5 ns  4 h=2.13 us  24 h=61.63 us
  CSAC   1 min=2.7 ns  10 min=11.3 ns  1 h=43.4 ns  4 h=164.4 ns  24 h=1.92 us
  OCXO   1 min=0.0 ns  10 min=0.3 ns  1 h=2.6 ns  4 h=22.5 ns  24 h=627.2 ns
  Rb     1 min=0.0 ns  10 min=0.3 ns  1 h=1.6 ns  4 h=6.6 ns  24 h=58.2 ns

Holdover, temperature term 0.1 of spec over a 24 h cycle
grade   loop tc  locked rms  y_err@HO |             1 min |            10 min |               1 h |               4 h |              24 h
TCXO        74s     14.4 ns   6.8e-10 |  53.6 ns/ 88.4 ns | 838.2 ns/ 1.26 us | 16.73 us/25.79 us | 183.90 us/377.07 us |  3.41 ms/ 4.37 ms
CSAC      2000s      9.8 ns   6.1e-12 |   8.7 ns/ 13.5 ns |   6.1 ns/ 19.5 ns |  17.2 ns/ 48.7 ns | 121.6 ns/355.0 ns |  3.08 us/ 4.40 us
OCXO      1658s     14.6 ns   1.6e-12 |  14.1 ns/ 20.4 ns |  15.1 ns/ 23.0 ns |  45.0 ns/ 75.5 ns | 374.5 ns/753.4 ns |  6.52 us/ 9.42 us
Rb        2000s      6.3 ns   6.1e-13 |   6.0 ns/  8.8 ns |   6.3 ns/  9.5 ns |  15.9 ns/ 26.3 ns | 117.5 ns/225.5 ns |  2.05 us/ 2.72 us
cells: median / 95th percentile |time error| after the GNSS outage starts
analytic |y_err|*t + D*t^2/2 + adev1*sqrt(t) (+ temp) with the median y_err:
  TCXO   1 min=3.05 us  10 min=30.43 us  1 h=182.60 us  4 h=731.53 us  24 h=4.44 ms
  CSAC   1 min=4.5 ns  10 min=29.1 ns  1 h=150.3 ns  4 h=591.8 ns  24 h=4.49 us
  OCXO   1 min=6.1 ns  10 min=61.0 ns  1 h=366.7 ns  4 h=1.48 us  24 h=9.37 us
  Rb     1 min=1.9 ns  10 min=18.4 ns  1 h=110.4 ns  4 h=441.8 ns  24 h=2.67 us

Slow time-walk spoof: settle 2 h, detector training 2 h, walk for 2 h; temp_fraction=0.1
second source: sigma 100 ns, unknown bias 300 ns
grade  walk ns/s  internal alarm s  cross alarm s  TE end, follows  TE end, guarded
TCXO         0.5                 -            660          3.58 us         51.95 us
TCXO           2                 -            240         14.38 us         54.66 us
TCXO          10               360            120         71.98 us         55.39 us
TCXO   no-spoof control: false alarms internal 0/5, cross 0/5
CSAC         0.5               540            660          3.55 us          38.5 ns
CSAC           2               360            240         14.16 us          28.4 ns
CSAC          10               240            120         70.77 us          30.6 ns
CSAC   no-spoof control: false alarms internal 0/5, cross 0/5
OCXO         0.5               360            660          3.58 us          94.8 ns
OCXO           2               240            240         14.37 us          76.4 ns
OCXO          10               180            120         71.91 us          63.4 ns
OCXO   no-spoof control: false alarms internal 0/5, cross 0/5
Rb           0.5               480            660          3.53 us           8.6 ns
Rb             2               300            240         14.15 us          14.3 ns
Rb            10               240            120         70.75 us           4.1 ns
Rb     no-spoof control: false alarms internal 0/5, cross 0/5
alarm times are seconds after the walk starts; '-' = no alarm in the window
```

## Reading the output

- **No temperature term, 24 h holdover**: TCXO about 60 us, CSAC about 1.3 us, OCXO about
  0.6 us, Rb about 44 ns (medians). The analytic line `|y_err|*t + D*t^2/2 + adev1*sqrt(t)`
  tracks the simulated median within a factor of about 2 at every checkpoint where TE has
  grown well past the locked error; the 24 h numbers are dominated by aging (`D*t^2/2`), e.g.
  TCXO aging 5e-7/yr gives 59 us after one day on its own.
- **With a 24 h temperature cycle at 10 % of the spec** the order changes: CSAC (3.1 us) beats
  the OCXO (6.5 us) at 24 h because Vig's OCXO temperature figure (1e-9) is three times the
  SA65's (3e-10), and the TCXO goes to milliseconds. The analytic line here adds a worst-case
  linear temperature term, so it over-predicts.
- **Internal monitor** catches every walk on the OCXO, CSAC and Rb within 3-9 min, but on the
  TCXO it misses 0.5 and 2 ns/s: the TCXO's own temperature wander forces a high threshold.
- **Cross-source monitor** catches every rate on every grade (2-11 min), independent of the
  oscillator, because it compares two external references and ignores the local clock.
- **Detection is not mitigation.** On the TCXO the guard switches to holdover and ends at about
  52-55 us, worse than following the 0.5 and 2 ns/s walk (3.6 and 14 us). With a good holdover
  oscillator the guard keeps the clock within 4-95 ns of truth.
- No false alarms in 5 no-spoof control runs per grade for either monitor. Five runs is a
  smoke test, not a false-alarm rate.

## Limits and honest notes

- Assumptions not taken from a source: 20 ns PPS noise, 100 ns / 300 ns second-source noise
  and asymmetry, the 100 ns cross-source margin, the temperature fraction, the initial offset,
  loop time constant clamps, detector windows and thresholds.
- The asymmetry of the second source is constant here. A real network path changes with
  routing and load, and a spoofer who also controls that path defeats the cross-check; see
  PTPsec and NTS in the primer.
- Only constant-rate walks. A spoofer who walks at a rate that matches the oscillator's natural
  wander, or who steps during a GNSS outage, needs a different test.
- Results are from one seed per spoof row. Use `--seed` to see the spread.
