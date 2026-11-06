# Cheat sheet: resilient timing

Briefs like "resilient timing for a sensor network", "time server", "critical infrastructure",
"time push", "trustworthy GNSS for the grid / telecom". Decoder rows 6, 19.

## 1. What judges likely want (30 s)

Each node knows when its time source is lying and how long it can hold time without it.
Judges from infrastructure want holdover in microseconds against a stated budget, a time push
caught by cross-checking, and authentication where it exists (Galileo OSNMA), with its limits.

## 2. The demo in 24-48 h

Six GNSS-disciplined sites over PTP-like links: regional jamming, a time push on one node, all
GNSS lost for 24 h. Show the cross-node check isolating the pushed node and the ensemble holding
time. Add the one real time push (Jammertest 2.4.2) and OSNMA authenticate-or-alarm.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [timing-network-holdover](../../samples/timing-network-holdover/) | ran | stdlib | none for the sim (~50 s); real-data mode 60 MB, ~20 s | `python3 timing_network.py`, then `python3 fetch_data.py && python3 real_link.py` |
| [timing-holdover](../../samples/timing-holdover/) | ran | stdlib | none, ~5 s | `python3 timing_holdover.py` |
| [real-attack-replay](../../samples/real-attack-replay/) | ran | stdlib | 64 MB | `./fetch_data.sh && python3 replay.py --data data/vaara --no-pos-drift --baseline-max-score 0.3` (look for `clock_jump` in 2.4.2) |
| [osnma-authentication](../../samples/osnma-authentication/) | ran | stdlib for the first command; OSNMAlib venv (Python 3.10-3.12) for the 11 scenarios | ~8 s | `python3 -m unittest -v test_osnma_adapter.py && python3 demo_adapter.py` |

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Which budget (1.5 us? 1 ms?), which oscillators, receivers with PPS on site? | ADR-001: metric = time to exceed the budget, time to isolate a push |
| Nav | Run both timing samples, read their assumptions | Replace datasheet values with the brief's hardware |
| Platform | Real-data mode, VAARA fetch | If hardware: capture NAV-CLOCK / PPS logs now (none in the hub) |
| Viz (4-5) | TE vs time per node from `--trace te.csv` | Per-node trust state on a map or table |
| Pitch (5) | Read [timing-resilience](../timing-resilience.md) | Layered-defence slide: holdover, cross-check, OSNMA |

## 4. Numbers you can cite

- Jammed TCXO alone exceeds 1.5 us after 16-22 min; held from peers it stays under 1 us for
  24 h; a 50 ns/s push on the relay is isolated in 50 s, 0 false alarms in 40 h. **Synthetic**
  (datasheet oscillators, assumed network), 10 seeds.
- Real PTP over 5G: PPS-truth |TE| median 1.6-2.3 ms (private 5G SA), at most 0.3 % of seconds
  under 1.5 us. **Real** (Zenodo 14230741), 4 PPS records x 900 s.
- Jammertest 2.4.2: receiver UTC jumped +900.01 s, caught by `clock_jump`. **Real** (VAARA),
  1 event.

## 5. Top traps

1. Oscillator models are datasheet parameters (white FM + aging, optional temperature fraction),
   not a unit. No recorded NAV-CLOCK / PPS log and no real PTP / chrony piece in code exist in the
   hub. Receiver time only shows jumps over 5 s; the 9 ns/s ramp (2.4.12) was not separable.
2. OSNMA does not help against jamming. In OSNMAlib file mode a replay without an independent
   clock and 3 s meaconing authenticate normally, and forged same-IOD words stayed
   "authenticated" for 10 min ([upstream findings 1-2](../upstream-findings.md#summary)).
3. Unknown path asymmetry A costs about A/2 (4 us => 2.16 us); real 5G links showed 3.3-14.9 ms
   implied asymmetry, about 10^4 x the synthetic links. A cross-check trained on such links missed
   a 50 ns/s push.

## 6. Stretch goal

Bring a GNSS receiver with PPS, log NAV-CLOCK and PPS against a local reference, and run the
cross-check on your own recording: it closes the hub's biggest timing gap. Cards:
[linuxptp](../integration-cards/nwtime__linuxptp.md), [chrony](../integration-cards/gitlab.com__chrony__chrony.md),
[allantools](../integration-cards/aewallin__allantools.md).

## 7. Links

- Decoder: [rows 6, 19](../problem-statement-decoder.md#the-table); evidence:
  [section 10](../evidence-matrix.md#10-timing-holdover),
  [section 2 (OSNMA)](../evidence-matrix.md#2-receiver-and-signal-level-detection).
- Cards: [OSNMAlib](../integration-cards/algafix__osnma.md),
  [GNSS-SDR](../integration-cards/gnss-sdr__gnss-sdr.md),
  [pyubx2](../integration-cards/semuconsulting__pyubx2.md),
  [satpulse](../integration-cards/jclark__satpulse.md), plus the three above.
- Datasets: [Jammertest](../dataset-cards/jammertest-data.md),
  [OSNMAlib recording](../dataset-cards/osnmalib-recording.md), [TEXBAT](../dataset-cards/texbat.md).
- Guide: [timing-resilience](../timing-resilience.md).
