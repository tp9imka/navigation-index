# Low-cost GNSS jammer sensor network

Problem: "build a low-cost sensor network that detects and localizes GNSS jammers and
puts them on a common operating picture". This sample does it with cheap u-blox-class
receivers instead of direction-finding arrays: each node reports what the receiver already
measures (fix, C/N0 drop, AGC, jamming indicator), the aggregator turns that into jammer
power at each node and localizes the emitter, and the result goes to TAK as CoT and to the
demo dashboard as navdash/1 files.

```
u-blox node (pyubx2: NAV-PVT, NAV-SAT, MON-RF)  or  jsn_model.SimNode
   => jsn/1 JSON on jsn/v1/<node>/{meta,obs}   (MQTT, HTTP POST or stdin)
   => jsn_aggregator.py  obs => jammer power J (C/N0 drop, AGC) or a censored bound
                         => (a) weighted centroid  (b) RSS least squares, k=1|2
                            (c) grid likelihood over (x, y, power), Bayesian update
                            (+) DF bearings: ../interference-geolocation-to-tak/triangulate.py, and fused into (c)
   => jsn_outputs.py     CoT point + 95% ellipse (tak_out.py, cot.py) + node markers
                         navdash/1 tracks + zones.geojson for templates/demo-dashboard
```

Defensive scope: receive-only monitoring. Nothing here transmits or generates GNSS signals.
Everything was run on synthetic data. No real receiver, jammer, broker or TAK client was used.

## Run (all run 2026-11-06, Python 3.14.7, stdlib only)

```
python3 -m unittest -v test_jsn          # 16 tests, ~1 s
python3 demo.py                          # static, moving, two-jammer scenarios => out/<scenario>/  (~40 s)
python3 demo.py --scenario static --http # same, through the HTTP aggregator (results identical)
python3 demo.py --scenario static --buildings
python3 demo.py --scenario static --mobile 0     # without vehicle nodes
python3 evaluate.py                      # Monte Carlo sweeps, 40 trials each (~2 min) => out/eval.json
```

Live aggregator:

```
python3 jsn_aggregator.py --origin 69.28,16.03 --area 4000 --port 8765
curl -X POST --data-binary @msgs.txt localhost:8765/v1/msg      # JSONL, JSON array or `topic payload` lines
curl localhost:8765/v1/estimate     # JSON, all methods
curl localhost:8765/v1/cot          # CoT XML, one event per line
curl localhost:8765/v1/zones.geojson
# with a real broker (not tested here): mosquitto_sub -v -t 'jsn/v1/#' | python3 jsn_aggregator.py --origin ... --stdin
```

`python3 demo.py --scenario static --dump-msgs msgs.txt` writes the 2548 messages of the
static run in `mosquitto_sub -v` format; piping that file into `--stdin` was run.

Dashboard: copy `out/static/` under `templates/demo-dashboard/` and open
`?manifest=<dir>/manifest.json` (the page needs a static server). Not opened in a browser
for this sample. The primary `fused` track is the estimate and the `truth` track is the
jammer, so the panel's "error now" is the localization error. Zones: `jamming` (95%
ellipse per fuse step), `denial-model` (model fix-loss radius), `sensor` (static nodes).

## Files

| File | What |
|---|---|
| `jsn_model.py` | physics: path loss, correlated link shadowing, buildings, C/N0 and AGC response, `SimNode` |
| `jsn_protocol.py` | `jsn/1` schema, validation, topic parsing, obs => `Meas` (value or censored bound) |
| `jsn_localize.py` | weighted centroid, `rss_ls` (k sources), `select_sources` (BIC), `GridFilter` |
| `jsn_aggregator.py` | `Aggregator` (windows, evidence bookkeeping, fusion every 5 s), HTTP server, stdin mode |
| `jsn_outputs.py` | CoT and navdash/1 writers |
| `jsn_scenarios.py` | static / moving / two-jammer scenarios, vehicle loops, DF stations |
| `demo.py`, `evaluate.py` | end-to-end run, Monte Carlo sweeps |
| `siblings.py` | puts `../interference-geolocation-to-tak` and `../mavlink-to-tak-cot` on `sys.path`; both are imported unchanged |
| `out/` | outputs of the `demo.py` runs below (CoT, navdash files, `summary.json`, `estimate-last.json`) and `eval.json` |

## Node protocol `jsn/1`

Topics: `jsn/v1/<node>/meta` (retained, on boot and config change) and `jsn/v1/<node>/obs`
(1 Hz, QoS 0). The payload repeats the kind in `k`, so the same JSON works over HTTP or a
pipe. A median `obs` is 170 bytes (measured on the dumped static run), about 1.4 kbit/s per
node at 1 Hz. Whether that fits a given LoRa duty cycle is not checked; send on change or at
lower rate if it does not.

```
jsn/v1/s07/obs {"v":1,"k":"obs","id":"s07","seq":29,"t":28.0,"lat":69.275062,"lon":16.040184,"ps":0.5,"pf":"survey","fix":1,"nsv":8,"cn0":35.0,"dcn0":10.24,"agc":4387,"jam":6,"jst":2}
```

| Field | Type | Meaning | Source on a u-blox receiver |
|---|---|---|---|
| `v`, `k`, `id` | int, str, str | schema version 1, `meta` or `obs`, node id | - |
| `lat`, `lon` | float | node position (WGS84) | NAV-PVT, or survey for static nodes |
| `static` (meta) | bool | surveyed fixed site | config |
| `hw` (meta) | str | receiver model, optional | config |
| `agc_ref`, `agc_db_per_cnt` (meta) | int, float | clear-sky AGC count and the node's calibration (dB per count); omit both if uncalibrated, AGC is then ignored | per-node calibration (see BOM) |
| `seq`, `t` | int, float | sequence, time in s (same clock across nodes) | NAV-PVT iTOW / host clock |
| `ps`, `pf` | float, str | 1-sigma position error m; `survey`, `gnss` or `dr` | DR when the fix is lost |
| `fix`, `nsv` | int | fix valid (0/1), SVs still tracked | NAV-PVT fixType, NAV-SAT |
| `cn0` | float or null | mean C/N0 of tracked SVs, dB-Hz | NAV-SAT cno |
| `dcn0` | float or null | median per-SV drop vs the node's learned clear-sky C/N0, dB | NAV-SAT cno vs baseline |
| `agc` | int | AGC monitor count, 0..8191 | MON-RF agcCnt (MON-HW on M8) |
| `jam` | int | CW jamming indicator 0..255 (not used for localization) | MON-RF jamInd |
| `jst` | int | jamming state 0 unknown, 1 ok, 2 warning, 3 critical | MON-RF jammingState (M8 MON-HW) |

`ubx_monitor.fill()` in `../gnss-interference-monitor/` already reads NAV-PVT, NAV-SAT and
MON-RF with pyubx2; building `obs` from its `Epoch` is a few lines (not written here: there
was no receiver to test against).

## Physics and where the numbers come from

**C/N0 to jammer power.** Effective C/N0 under interference (Kaplan and Hegarty,
"Understanding GPS: Principles and Applications", interference chapter by Ward et al.;
the general spectral-separation form is on ESA Navipedia "Equivalent Carrier to Noise
Ratio in presence of RF interference", citing Ward 1994 and Spilker 1997):

    1/(C/N0)eff = 1/(C/N0) + (J/S) / (Q Rc)

with Rc = 1.023e6 chip/s and Q = 1 (CW), 1.5 (narrowband matched), 2 (wideband noise).
Since S = (C/N0) N0 for each SV, the drop D in dB is identical for every tracked SV and
inverts without knowing any SV's power: **J = Q Rc N0 (10^(D/10) - 1)**. The test
`test_cn0_drop_inverts_and_is_sv_independent` checks both properties. I did not re-read the
Kaplan and Hegarty page; the Q values are as commonly quoted from that chapter.

**AGC.** The AGC holds total in-band power, so its gain reduction is
R = 10 log10(1 + J / (N0 B)). This gives J beyond the point where all SVs are lost. The
counts-to-dB mapping is device specific and polarity is not documented the same way
everywhere; this sample assumes a calibrated `agc_db_per_cnt` with 1.5 dB per-node error.

**Constants (assumptions, in `jsn_model.py`).** N0 = -174 + 2 dB NF = -172 dBm/Hz; front-end
bandwidth 2 MHz; tracking threshold 28 dB-Hz (not a u-blox figure); GPS L1 C/A minimum
received power -128.5 dBm (IS-GPS-200, -158.5 dBW). Resulting thresholds: 1 dB C/N0 drop
or 1 dB AGC reduction at J = -114.8 dBm; a typical 43.5 dB-Hz SV is lost at J = -93.5 dBm;
all SVs (up to 48 dB-Hz) lost at -88.9 dBm.

**Propagation truth.** Log-distance path loss, 36.4 dB at 1 m (free space at L1), exponent
2.7; shadowing is a 4-D Gaussian field over (receiver, jammer) positions with 50 m
correlation length (sum of 96 sinusoids), so moving either end decorrelates it and nothing
is common-mode; optional buildings add 15 dB per crossing. Jammer EIRPs 8-13 dBm in the demo
and 0-20 dBm in the Monte Carlo are scenario choices, not measured devices.

**What the unknown power absorbs.** The localizers fit J_i = P0 - 10 n log10(d_i). P0
soaks up every offset common to all nodes: EIRP, Q (CW vs noise is 3 dB), noise figure and
the antenna's horizon gain (patch antennas have low gain at 0 deg elevation). So identical
node hardware matters more than absolute calibration. Node-to-node differences in those
terms are not absorbed and behave like extra shadowing.

## Estimators

- **(a) Weighted centroid.** Detecting nodes weighted by 10^(dB above threshold / 10n),
  i.e. roughly 1/distance. No uncertainty is reported for it.
- **(b) RSS least squares.** Levenberg-Marquardt on (x, y, P0), multistart from the
  centroid, the strongest nodes and a 4x4 grid; solutions outside the area +10% are
  discarded. Censored nodes enter as one-sided residuals (a "clear" node only costs when
  the model predicts it should have seen the jammer). Covariance from the Jacobian, scaled
  by chi2/dof when that exceeds 1. `select_sources` also fits k=2 (summed linear power,
  pairwise starts from the strongest nodes) and keeps it only if BIC improves by 10 and the
  sources are more than 150 m apart.
- **(c) Grid likelihood.** 41 x 41 cells x 27 power values (EIRP -24..+41 dBm). Value terms
  are Gaussian, censored terms are normal CDFs, every term is floored at 1e-4 so one wrong
  node cannot veto a cell. Position uncertainty of the node (DR drift on vehicles that lost
  GNSS) is added to each term's variance. Evidence bookkeeping, which is the part that keeps
  the posterior honest over time:
  - static nodes are rebuilt every update from their latest 10 s mean, never accumulated
    (their shadowing is a fixed bias, repeating it would count the same evidence again);
  - a vehicle adds a new term only after it moves 100 m (about twice the shadowing
    correlation length) or, for a moving jammer, after the jammer could have moved that far;
  - with a moving jammer the recursive part is blurred by v_max x dt each step and the
    averaging windows shrink to 100 m / v_max.
- **DF comparison.** Bearings in KrakenSDR's shape (`kraken.Bearing`) from 3 stations,
  3 deg noise, 10% outliers, detection floor -120 dBm (assumed). `triangulate.locate` from the
  DF sample gives the DF-only fix; the grid can also take one robust mean bearing per station
  (`grid+df`).

## Results (synthetic, from the runs above)

### Scenarios (`demo.py`, seed 1)

12 static nodes on a jittered grid over 4 x 4 km plus 2 vehicles at 10 m/s on road loops;
shadowing sigma 6 dB; error statistics over fuse steps from 60 s after jammer on.
"truth in 95%" is the fraction of steps where the truth was inside the reported ellipse.

| Scenario | wc median | ls median / p90 | grid median / p90 | df median | grid+df median | coverage ls / grid / grid+df |
|---|---|---|---|---|---|---|
| static jammer, 10 dBm | 324 m | 438 / 2588 m | 599 / 1090 m | 23 m | 57 m | 0.29 / 0.67 / 1.00 |
| static + buildings | 341 m | 441 / 522 m | 576 / 976 m | no fix (one station) | 266 m | 0.29 / 0.57 / 1.00 |
| moving jammer, 13 dBm, ~10 m/s | 407 m | 295 / 1117 m | 338 / 489 m | 94 m | 104 m | 0.88 / 0.80 / 0.93 |
| two jammers, 12 + 12 dBm | 576 m | k=2 chosen 9 of 21 steps: 288 m per source | 889 m (single-source model) | - | - | - |

Other read-outs: detection 5 s after jammer on (first fuse step) in all scenarios; model
EIRP at the last step 9.4 dBm (grid) and 10.6 dBm (ls) for the 10 dBm jammer, 13.2 / 14.4 dBm
for the two 12 dBm jammers. These are one seed each; seeds 2 and 4 of the static scenario
gave grid medians of 794 m and 200 m, so do not read much into one row.

Vehicles help: same seeds, static scenario, grid median without vehicles => with 6 vehicles:
1044 => 371 m (seed 1), 332 => 242 m (seed 2), 565 => 294 m (seed 4). Grid coverage fell to
0.48 / 0.67 / 1.00 with 6 vehicles, so the 100 m new-evidence rule is still somewhat
optimistic when many vehicle points accumulate.

### Monte Carlo (`evaluate.py`, 40 trials per row, one 10 s snapshot of static nodes)

Median / p90 error in m; "(k none)" = trials without an estimate (no detection, or for DF
fewer than 2 stations above the floor). Base: 16 nodes, 4 x 4 km, sigma 6 dB.

Node count (4 x 4 km, sigma 6 dB):

| nodes | /km2 | wc | ls | grid | df (3 stations) | grid+df | 95% cover ls / grid / grid+df |
|---|---|---|---|---|---|---|---|
| 4 | 0.25 | 636 / 978 | 566 / 987 (12 none) | 602 / 1011 | 32 / 66 (13 none) | 55 / 514 (1 none) | 1.00 / 1.00 / 1.00 |
| 8 | 0.50 | 516 / 1018 (1 none) | 450 / 1066 (5 none) | 544 / 903 (1 none) | 29 / 49 (17 none) | 64 / 474 (3 none) | 0.91 / 1.00 / 1.00 |
| 16 | 1.00 | 480 / 652 | 264 / 866 | 313 / 640 | 20 / 72 (13 none) | 40 / 171 (1 none) | 0.78 / 1.00 / 1.00 |
| 32 | 2.00 | 318 / 502 | 200 / 380 | 173 / 375 | 32 / 71 (14 none) | 38 / 148 (5 none) | 0.82 / 0.93 / 0.97 |

Density (16 nodes, area side varied):

| side | /km2 | wc | ls | grid | df | grid+df | cover ls / grid / grid+df |
|---|---|---|---|---|---|---|---|
| 2 km | 4.00 | 239 / 420 | 129 / 355 | 144 / 298 | 10 / 29 (2 none) | 19 / 54 | 0.78 / 0.97 / 1.00 |
| 4 km | 1.00 | 480 / 652 | 264 / 866 | 313 / 640 | 20 / 72 (13 none) | 40 / 171 (1 none) | 0.78 / 1.00 / 1.00 |
| 8 km | 0.25 | 739 / 1300 (1 none) | 662 / 1272 (8 none) | 777 / 1134 (1 none) | 97 / 193 (29 none) | 124 / 614 (19 none) | 0.91 / 1.00 / 1.00 |

Shadowing sigma (16 nodes, 4 x 4 km):

| sigma | wc | ls | grid | df | grid+df | cover ls / grid / grid+df |
|---|---|---|---|---|---|---|
| 2 dB | 342 / 629 | 99 / 206 | 100 / 205 | 27 / 72 (13 none) | 50 / 80 (3 none) | 0.90 / 1.00 / 1.00 |
| 4 dB | 444 / 700 | 211 / 366 (1 none) | 222 / 379 | 24 / 70 (14 none) | 53 / 163 (3 none) | 0.82 / 0.97 / 0.97 |
| 6 dB | 480 / 652 | 264 / 866 | 313 / 640 | 20 / 72 (13 none) | 40 / 171 (1 none) | 0.78 / 1.00 / 1.00 |
| 8 dB | 485 / 737 | 271 / 828 (1 none) | 378 / 810 | 29 / 133 (11 none) | 82 / 184 (1 none) | 0.79 / 1.00 / 1.00 |
| 10 dB | 537 / 874 | 383 / 1228 | 520 / 998 | 28 / 65 (9 none) | 43 / 279 (2 none) | 0.75 / 0.90 / 1.00 |

### What the numbers say

- **Power-only localization is coarse.** With 6 dB shadowing a node's range is uncertain by
  a factor of about 10^(6/27) = 1.7, so errors are a sizeable fraction of node spacing:
  roughly 130-260 m median at 1-4 nodes/km2, and only density or lower shadowing fixes it.
  Good enough to send a team to a block, not to a car.
- **Detection is the strong part.** Every scenario detected on the first fuse step; the
  network tells you "there is a jammer, about this strong, about here" quickly.
- **LS and grid are close on a snapshot; the grid's value is over time and honesty.** LS
  ellipses cover the truth 75-100% of the time (mostly about 80%) at a nominal 95% (linearization ignores
  the banana-shaped likelihood). The grid ellipse is conservative (0.90-1.00), at the cost
  of a posterior mean that a broad posterior pulls toward the centre.
- **DF is about 10x more accurate per fix but needs signal at 2+ stations.** With 3 corner
  stations at -120 dBm it gave no fix in 13 of 40 trials at 4 km and 29 of 40 at 8 km, where
  RSS still produced an estimate. The DF model here has no systematic bearing bias, so it is
  the optimistic case. Fusing both gave 19-124 m medians (mostly 40-65 m) and still
  produced an estimate when DF alone had no fix.
- **Two jammers are only separable when the data show it.** With equal 12 dBm jammers the
  k=2 model won in 9 of 21 steps (288 m per source when it did). A single-source fit lands
  between the two (739 m). A weaker second jammer under 6 dB shadowing will often not pass
  the BIC test at all; that sweep was not run.
- **Mobile nodes are worth more than their count** (vehicle rows above): each 100 m of
  driving adds a fresh link geometry, which is the "synthetic array" idea of Borio et al.
  (ION GNSS+ 2016, "Jammer localization: from crowdsourcing to synthetic detection"; known
  from search summaries, the paper was not read). Vehicles near the jammer lose GNSS; their DR drift (0.5 m/s here)
  enters each term's variance.

## Hardware BOM (capabilities only, no prices)

Per node, what this sample's message needs:

| Item | Requirement | Documented capability |
|---|---|---|
| GNSS receiver | per-SV C/N0, AGC count, CW jamming indicator, jamming state over UBX | u-blox M8: MON-HW carries agcCnt, jamInd, jammingState; broadband interference monitor enabled via CFG-ITFM (u-blox 8 / M8 Receiver Description incl. Protocol Specification, UBX-13003221, [copy](https://cdn.sparkfun.com/assets/0/9/4/3/5/u-blox8-M8_ReceiverDescrProtSpec__UBX-13003221__Public.pdf)). F9 (HPG): MON-RF per RF block ([F9 HPG 1.32 Interface Description, UBX-22008968](https://cdn.sparkfun.com/assets/learn_tutorials/2/7/8/1/u-blox-F9-HPG-1.32_InterfaceDescription_UBX-22008968.pdf)); the ZED-F9T integration manual states MON-RF jamInd indicates CW interference only. M9 / M10: MON-RF per their interface descriptions (not re-checked here). Field ranges as PX4 mirrors them in [SensorGnssRf](https://docs.px4.io/main/en/msg_docs/SensorGnssRf.html): AGC 0..8191, jamming indicator 0..255, state 0-3 unknown/ok/warning/critical |
| Parser | NAV-PVT, NAV-SAT, MON-RF / MON-HW | pyubx2 (`repo:semuconsulting/pyubx2`), as used in `../gnss-interference-monitor/ubx_monitor.py` |
| Antenna | same model on every node (horizon gain is then common-mode) | active L1 patch; exact gain pattern is antenna specific |
| Host + link | publish ~170 B/s JSON | any small Linux board or MCU with Wi-Fi / cellular; MQTT broker of your choice |
| Static nodes | surveyed position (`pf: survey`) | survey once, before jamming |
| Vehicle nodes | DR when the fix drops (`pf: dr`, growing `ps`) | wheel odometry / IMU; this sample models 0.5 m/s drift |
| Calibration | `agc_ref` and dB per count per node | measure AGC against a known injected level in a shielded setup; the counts-to-dB curve is not documented as linear |
| Optional DF | bearings | KrakenSDR via `../interference-geolocation-to-tak` |

The u-blox document set is inconsistent about where jammingState lives (MON-HW on M8,
MON-RF later) and some third-party definitions encode it differently; check the interface
description for your firmware before trusting `jst`.

## Limitations and next steps

- All synthetic. The C/N0 model assumes a white-noise jammer in the receiver bandwidth;
  chirp jammers, CW, and receiver mitigation (u-blox CW suppression) change Q and the
  AGC behaviour. Jammertest data (`res:jammertest-norway`,
  `repo:felixott94/fraunhoferiis_jammertest2025`) is where to calibrate this.
- The path-loss exponent is assumed known (2.7) in both truth and estimator. A mismatch
  biases range; fit n as a 4th parameter when there are many detecting nodes.
- The 100 m evidence rule is a heuristic; grid coverage drops to about 0.5-0.7 with many
  vehicle points. A proper fix is a shadowing-correlation-aware likelihood (Gaussian process
  over links).
- Two-jammer handling is only in LS; the grid is single-source.
- CoT types (`a-u-G` jammer, `a-f-G-E-S` node) and the ellipse angle convention are not
  checked on an ATAK/WinTAK client (same caveat as the DF sample).
- `ubx_monitor` => `jsn/1` publisher not written (no receiver to test with).
