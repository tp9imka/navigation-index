# Galileo OSNMA authentication as a spoofing defence

<!-- about: repo:algafix/osnma, repo:haiyang-wong/osnma-sdr-sim, repo:gnss-sdr/gnss-sdr -->

What Galileo OSNMA (Open Service Navigation Message Authentication) catches and what it does not,
shown on real recorded Galileo I/NAV pages with an unmodified [OSNMAlib](../../docs/integration-cards/algafix__osnma.md),
plus an adapter that turns authentication status into alerts for the
[gnss-interference-monitor scorer](../gnss-interference-monitor/).

**File-based only. Nothing here generates or transmits RF.** The attacks are edits to recorded
navigation bits in memory. The optional GNSS-SDR part writes a simulated IQ *file* with the
simulator's `usrp=1` (file sink) setting, which `run_sim.sh` asserts before running. See
[export control and ethics](../../docs/export-control-and-ethics.md) before going near hardware.

| File | What |
|---|---|
| `osnma_scenarios.py` | Runs OSNMAlib on the recording, clean and under 10 manipulations; prints a table, writes per-subframe timelines |
| `osnma_adapter.py` | Stdlib. `AuthAwareScorer` subclasses the scorer and adds 6 OSNMA detectors; `OsnmaStatus` from an OSNMAlib status-log entry or a scenario timeline |
| `demo_adapter.py` | Replays the recorded scenario timelines through `AuthAwareScorer` |
| `fixtures/osnma_results_20min.json` | Output of `osnma_scenarios.py --minutes 20` (real OSNMAlib runs, 2026-11-06) |
| `test_osnma_adapter.py` | 15 tests: adapter units, recorded-scenario checks, one OSNMAlib integration test |
| `gnss-sdr/` | Dockerfile (GNSS-SDR 0.0.20 + OSNMA-SDR-SIM), `run_sim.sh`, the PKID 2 public key as PEM, message counts from the runs |

## Run it

```sh
# adapter, demo and fixture tests: stdlib only
python3 -m unittest -v test_osnma_adapter.py
python3 demo_adapter.py

# real OSNMAlib runs (Python 3.10-3.12)
git clone https://github.com/Algafix/OSNMA /path/to/OSNMA      # ran at 25aa61de (2026-10-14)
python3.12 -m venv .venv && .venv/bin/pip install -r /path/to/OSNMA/requirements.txt
.venv/bin/python osnma_scenarios.py --osnmalib /path/to/OSNMA --minutes 20 --out results.json
OSNMALIB_PATH=/path/to/OSNMA .venv/bin/python -m unittest -v test_osnma_adapter.py
```

`osnma_scenarios.py` reads `custom_run/current_config.sbf` from the OSNMAlib checkout: a Septentrio SBF
`GALRawINAV` recording bundled with OSNMAlib, GST WN 1372 TOW 480090-484680, i.e. 2025-12-12
13:21-14:37 UTC (my conversion, 18 leap seconds), 76 min, public key ID 2. The GSC Merkle tree
(`OSNMA_MerkleTree.xml`, issued 2025-12-09) and public key (`OSNMA_PublicKey_2.xml`) are the copies
OSNMAlib ships next to it; that is also how OSNMAlib's own tests get them (each test folder carries
its own `OSNMA_PublicKey*.xml` / `OSNMA_MerkleTree.xml`, `tests/test_corner_cases.py`). For live use,
fetch both from the [GSC OSNMA page](../../catalog/resources/galileo-osnma-service-page.md); a bundled
copy goes stale at the next key or tree renewal.

Each scenario runs in its own process (OSNMAlib keeps config and status logger in module singletons),
with Reed-Solomon recovery off so a forged word cannot be silently replaced by an RS-recovered copy.
20 min of recording, all 11 scenarios: about 8 s wall time on an M-series Mac.

## Results on the real recording (ran 2026-11-06)

`osnma_scenarios.py --minutes 20`. Attacks start at minute 10 unless stated. "ADKD0-auth SVs" counts
satellites whose ephemeris/clock (ADKD0) authentication is fresh (newest authenticated data no older
than 60 s; the nominal lag is 30 s on this recording).

| scenario | first auth [s] | KROOT ok | keys ok / fail | tags ok / fail | ADKD0-auth SVs at min 9.5 / at end | ADKD12-auth SVs at end | pages rejected (time backwards) |
|---|---|---|---|---|---|---|---|
| clean | 90 | 13 | 217 / 0 | 989 / 0 | 9 / 9 | 6 | 0 |
| replay_no_clock | 90 | 13 | 217 / 0 | 989 / 0 | 9 / 9 | 6 | 0 |
| meacon_3s | 90 | 13 | 217 / 0 | 989 / 0 | 9 / 9 | 6 | 0 |
| replay_60s | 360 | 13 | 217 / 0 | 233 / 0 | 0 / 0 | 6 | 0 |
| replay_1h | none | 13 | 217 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |
| forge_nav | 90 | 13 | 217 / 0 | 712 / 277 | 6 / 6 | 5 | 0 |
| forge_nav_late | 90 | 13 | 217 / 0 | 983 / 6 | 9 / 8 | 6 | 0 |
| forge_keys | 90 | 13 | 120 / 97 | 455 / 0 | 9 / 0 | 0 | 0 |
| strip_osnma | 90 | 6 | 120 / 0 | 455 / 0 | 9 / 0 | 0 | 0 |
| time_shift_120s | 90 | 10 | 120 / 73 | 455 / 0 | 9 / 0 | 0 | 590 |
| cold_start_merkle | none | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 |

Full 76 min clean run through the wrapper: 56 KROOT, 962 TESLA keys, 4711 tags authenticated, 0
failures. OSNMAlib's own `custom_run/run.py` on the same file (defaults, RS recovery on) also logged
4711 tags authenticated, 3073 data-authentication events and 0 WARNING/ERROR lines.

What each row is:

- **clean** - warm start (public key given), KROOT from the signal, first ADKD0 authentication 90 s
  after the first page. Authentication works end to end: KROOT signature, TESLA key chain, MACSEQ,
  tags, ADKD0 / ADKD4 / ADKD12 data.
- **replay_no_clock** - identical bits, read as an attack: an 11-month-old recording authenticates
  perfectly on 2026-11-06. OSNMAlib's file mode trusts the signal's own GST (TS fixed at 30 s), so
  without an independent clock a replay is invisible. This is the baseline OSNMA promise breaking
  on time, not on cryptography.
- **meacon_3s / replay_60s / replay_1h** - the wrapper supplies an independent clock = page time +
  delay; OSNMAlib then uses the measured offset as its time uncertainty. 3 s: everything still
  authenticates (OSNMA cannot see a meaconer inside the bound). 60 s: ADKD0/ADKD4 stop, only the
  slow MAC (ADKD12) still verifies, first at 360 s. 1 h: nothing is authenticated, yet nothing
  *fails* either: no error, just silence. Thresholds are OSNMAlib's (`_filter_tag_by_TL`: >30 s
  ADKD12 only, >330 s none); the Receiver Guidelines check |GST_SIS - GST_Rx| against T_L/2 = 15 s
  ([digest](../../docs/paper-digests/galileo-osnma.md)).
- **forge_nav** - one bit of OMEGA_0 (word type 2) flipped on E19, E23, E27 from the first page:
  277 tag failures, those 3 SVs never ADKD0-authenticated, the other 6 unaffected.
- **forge_nav_late** - same flip from minute 10 only, after the genuine word was authenticated.
  OSNMAlib computes an ADKD0 block's authenticated bit stream once, when the block first
  completes (`ADKD0DataBlock.add_word` / `_compute_data_stream` in `osnma/osnma_core/nav_data_manager.py`),
  and later words with the same IOD overwrite `words` but not that stream. So tags keep verifying
  against the genuine copy and the SV stays "authenticated" while the receiver is decoding forged
  words: E23 (no IOD change in the window) stayed authenticated for 10 min with forged OMEGA_0
  (`words_differ_from_authenticated_stream: [23]`). E27 changed IOD at 950 s, its new block was
  built from forged words, and tags failed from 1020 s on. E19 changed IOD at 1160 s, too late to
  show in 20 min. Consequence: **feed the PVT the authenticated copy, or compare decoded words
  against it**; a receiver that authenticates one copy and navigates on another has a 10+ minute
  hole. The adapter has an `osnma_data_mismatch` detector for this.
- **forge_keys** - spoofer without the TESLA chain: from minute 10 every MACK tag and key is random
  and ephemeris is flipped on all SVs. 97 key-chain failures, no tag can be checked (no valid key),
  authenticated set goes to zero. Fully consistent spoofed data does not help an attacker who cannot
  produce keys that hash back to the signed root key.
- **strip_osnma** - plain I/NAV with the 40 OSNMA bits zeroed: no failures at all, authentication
  just stops. Only "authentication was held and is now gone" catches it.
- **time_shift_120s** - pages re-stamped 120 s earlier: 590 pages rejected as time going backwards,
  then 73 key failures once time moves forward again (keys bound to the wrong GST fail the chain).
- **cold_start_merkle** - no public key, only the Merkle tree: no DSM-PKR (DSM IDs 12-15) appears in
  the 76 min recording (only DSM IDs 0 and 11, which are KROOT), so OSNMAlib never gets a key and
  never authenticates. A true cold start needs the public key provisioned out of band or a longer
  wait for a PKR broadcast (PKR rate not measured here).

Not demonstrated: the attack OSNMA's time requirement exists for, i.e. delaying the signal past key
disclosure and re-tagging forged data with already-disclosed keys. It needs a tag generator; the
time rows above show the gate that blocks it (with an independent clock) and the case where that
gate is absent (`replay_no_clock`).

### What OSNMA does and does not cover

| Threat | OSNMA alone | Evidence here |
|---|---|---|
| Forged ephemeris / clock from cold start | caught (tag failures) | forge_nav |
| Spoofer without keys, any data | caught (key-chain failure, auth stops) | forge_keys |
| Forged data after authentication, same IOD | missed by OSNMAlib's status until IOD changes; needs data comparison | forge_nav_late |
| OSNMA stripped | no failure, only absence | strip_osnma |
| GST pulled back | caught (page rejection, key failures) | time_shift_120s |
| Replay, no independent clock | **missed** | replay_no_clock |
| Replay > 15-30 s, independent clock | caught as missing auth / time offset | replay_60s, replay_1h |
| Meaconing / relay within the bound | **missed** | meacon_3s |
| Code-phase drag-off with genuine data | **missed** (data is genuine; OSNMA authenticates data, not ranging) | see [gnss-signal-chain](../gnss-signal-chain/) `dragoff` |
| Jamming | out of scope (no signal => no auth) | - |

The misses are why the adapter combines OSNMA with the scorer's clock-jump, position and clock-drift
consistency detectors instead of replacing them. A 3 s meaconing delay is a ~9e8 m clock-bias step if
switched in abruptly (the scorer's `clock_jump` fires); a slow walk-off is what its CUSUM detectors
are for.

## Adapter: authentication status into the scorer

`AuthAwareScorer` subclasses `InterferenceScorer` (imported from `../gnss-interference-monitor`, not
edited) and injects OSNMA alerts through the scorer's `_update_alarm` hook, so they latch and clear
like every other alert. Feed `update_osnma(OsnmaStatus)` once per 30 s subframe and `assess(Epoch)`
at 1 Hz. All OSNMA alerts are family `spoofing`.

| detector | fires when | weight |
|---|---|---|
| `osnma_tag_fail` | any tag failed this subframe | 0.6 |
| `osnma_key_fail` | any TESLA key failed the chain check | 0.6 |
| `osnma_data_mismatch` | decoded words differ from the authenticated copy | 0.6 |
| `osnma_time_offset` | independent clock vs signal GST > 15 s (T_L/2) | 0.6 |
| `osnma_time_reject` | pages with GST going backwards | 0.5 |
| `osnma_auth_drop` | auth had been held, now < 50 % of tracked Galileo SVs authenticated, while median Galileo C/N0 >= 35 dB-Hz (or C/N0 not reported) | 0.5 |

Honest degradation: before first authentication, without status, or with a status older than 90 s,
`osnma_state` is `not-measured` and no OSNMA detector runs. Missing authentication is never "clean".
A drop with weak Galileo signals is treated as fading, not spoofing (negative-control test).

`demo_adapter.py` on the fixture (synthetic clean static-receiver telemetry, so every alarm comes from
the OSNMA input):

| scenario | first spoofing alarm [s] | detectors | alarm epochs | not-measured epochs | final OSNMA state |
|---|---|---|---|---|---|
| clean | none | - | 0 | 120 | authenticated 9/10 |
| replay_no_clock | none | - | 0 | 120 | authenticated 9/10 |
| meacon_3s | none | - | 0 | 120 | authenticated 9/10 |
| replay_60s | 30 | osnma_time_offset | 1171 | 30 | alert |
| replay_1h | 30 | osnma_time_offset | 1171 | 30 | alert |
| forge_nav | 120 | osnma_tag_fail | 1081 | 120 | alert |
| forge_nav_late | 1050 | osnma_data_mismatch, osnma_tag_fail | 151 | 120 | alert |
| forge_keys | 630 | osnma_auth_drop, osnma_data_mismatch, osnma_key_fail | 571 | 120 | alert |
| strip_osnma | 660 | osnma_auth_drop | 541 | 120 | alert |
| time_shift_120s | 630 | osnma_auth_drop, osnma_key_fail, osnma_time_reject | 451 | 120 | alert |
| cold_start_merkle | none | - | 0 | 1201 | not-measured |

Alarm time = end of the subframe that carried the evidence. Caveat: the scenario output only has run
totals for page rejections and data mismatches, so `from_timeline` attaches them to the last subframe;
in `forge_nav_late` the 1050 s alarm comes from the tag failures, and the mismatch shows only at the
end. A live integration would compute the mismatch per subframe. "9/10" in the clean rows: E18 is
tracked and transmits OSNMA but was never ADKD0-authenticated in the 20 min window (cause not
investigated); E21, E23, E27, E34 carried no OSNMA early on and are authenticated through
cross-authentication tags from other SVs.

Tests (ran 2026-11-06): 15 pass with OSNMAlib on Python 3.12.14 (`OSNMALIB_PATH` set); 14 pass + 1
skipped stdlib-only on Python 3.14.7. Mutation check: disabling the tag-fail, key-fail, auth-drop or
time-offset detector, or the weak-signal guard, each fails 1-2 tests.

## GNSS-SDR with OSNMA on a simulated E1 IQ file

GNSS-SDR gained OSNMA in v0.0.20 (2025-04-01 changelog: "OSNMA is enabled by default if the receiver
configuration defines Galileo E1 OS channels"). v0.0.22 (2026-10-04) hardened it and added
`GNSS-SDR.osnma_mode=replay`. Debian trixie packages 0.0.20 (`apt-cache policy`, checked 2026-11-06;
Ubuntu 26.04 has 0.0.20-2, Ubuntu 24.04 has 0.0.19 without OSNMA).

In the 0.0.20 source (`src/core/libs/osnma_msg_receiver.cc` at tag v0.0.20), the default mode takes
receiver time from the last received GST, i.e. it trusts the signal; `GNSS-SDR.osnma_mode=strict`
uses the system clock and drops tags when |local_t - GST_SIS| exceeds T_L (ADKD12 only up to 10 T_L).

```sh
cd gnss-sdr && docker build -t osnma-gnss-sdr:0.0.20 .     # ~200 s, image 1.74 GB
docker create --name osnma-sim -t -e TERM=xterm -e CROSS_AUTH_MODE=1 osnma-gnss-sdr:0.0.20 \
  bash /scripts/run_sim.sh 600 /out      # MODES="nonstrict" to skip the strict run
docker cp . osnma-sim:/scripts
docker cp /path/to/OSNMA/custom_run/OSNMA_MerkleTree.xml osnma-sim:/scripts/
docker start -a osnma-sim
docker cp osnma-sim:/out/rx_nonstrict . && docker cp osnma-sim:/out/rx_strict .
docker rm osnma-sim        # the IQ file inside is 10.4 MB per second of signal (6.24 GB for 600 s)
```

`docker cp` instead of bind mounts because Docker Desktop on macOS showed `/private/tmp` mounts as
empty directories. Two fixes were needed: OSNMA-SDR-SIM does not compile with GCC 14 without
`-include bitset` (Dockerfile), and GNSS-SDR 0.0.20 segfaults (exit 139, no output) when given the
simulator's short-form public-key XML, so `OSNMA_PublicKey_PKID2.pem` is that key (point
`02219204...5fc99`, PKID 2, same as OSNMAlib's `OSNMA_PublicKey_2.xml`) converted to PEM with `ecdsa`.

Results (ran 2026-11-06, Docker Desktop on Apple silicon, aarch64 container), 600 s scenario
2026-05-13 12:41:01, static location 20, -51, 100 m, E1 only, simulator default `cross_auth_mode=3`:

| step | result |
|---|---|
| simulate 600 s E1 | 235 s wall, 6.24 GB IQ file (2.6 MS/s int16 I/Q), `[TX] Total samples consumed: 0` in the 10 s test run |
| simulator OSNMA | visible PRNs 2, 13, 15, 18, 27, 30, 34; OSNMA on 2, 15, 27, 34; 13, 18, 30 "OSNMA disabled" (mode 3 default) |
| GNSS-SDR non-strict | 679 s wall. 1069 PVT fixes (first at 12:41:48, 43 with 4 SVs, 1026 with 5). OSNMA: 36 subframes from E15, E27, E34 (none from E2), every one "time constraint OK (delta_T=0 s)" because receiver time = signal time; DSM-KROOT (DSM ID 11) stuck at 7 of 8 blocks, so no KROOT, every MACK "Cannot process MACK block. Skipping it.", **no tag or data authenticated in 600 s** |
| GNSS-SDR strict | 298 s wall. Every OSNMA subframe rejected: "time constraint violation", \|local_t - GST_SIS\| = 26,377,2xx-4xx s vs T_L = 30. **0 PVT fixes** |

Readings:

- Strict mode does what a receiver should do with a replayed file: the container clock says
  2026-11-06, the signal says 2026-05-13, so all tags are dropped. Note the reported offset
  (~26.4 Ms, ~305 days) does not match the ~177 days between the two dates; not investigated.
- Strict mode also removes unauthenticated Galileo SVs from the PVT: in `rtklib_pvt_gs.cc` (v0.0.20)
  an E1B/E5b observable is kept only if its PRN and `IOD_nav` are in the authenticated set. With
  nothing authenticated, no fix. That match is on PRN + IOD, not on the data bits, which looks like
  the same same-IOD gap as `forge_nav_late` (by code reading, not tested).
- The GNSS-SDR fix is at 42.349 N, 71.088 W, about 3,000 km from the simulator's configured and
  logged position (20, -51; `sim.log` prints the matching ECEF). Cause not investigated; do not use
  this simulator's output for position-accuracy claims until that is understood.
- With `cross_auth_mode=3` one DSM-KROOT block never arrived with only three OSNMA-carrying SVs
  decoded. Second run with `CROSS_AUTH_MODE=1` (all 7 visible SVs carry OSNMA, 208 s simulation,
  268 s GNSS-SDR, 1025 fixes): all 8 DSM-KROOT blocks arrived at subframe TOW 305100 (about 4 min
  in), "OpenSSL: OSNMA signature authenticated successfully", "DSM-KROOT authentication successful!",
  then 6 x "TESLA key verification :: SUCCESS!". But the glog INFO file shows
  `d_tags_awaiting_verify :: size: 0` every subframe and every nav-data entry `verified=0`: **no tag
  and no navigation data was authenticated**. Cause not found in the time box (candidates: a
  simulator/0.0.20 MACK or MACLT mismatch, or 0.0.20 behaviour fixed in 0.0.22). Next step: same
  file through GNSS-SDR 0.0.22 (source build) or OSNMAlib over GNSS-SDR's UDP nav-message monitor.

So for GNSS-SDR the verified part is: build, simulate, decode and fix, public-key and KROOT signature
verification, TESLA key-chain verification, and the strict-mode time check rejecting a replayed file.
Tag and data authentication in GNSS-SDR is **not** verified. Message counts from all three runs:
`gnss-sdr/results_2026-11-06.txt` (raw logs and the 6.2 GB IQ files were deleted).

## Operational requirements

- **Time.** OSNMA security rests on the receiver knowing GST independently: T_L = 30 s, checked as
  |GST_SIS - GST_Rx| < T_L/2; up to T_L + 300 s only slow MAC (ADKD12); beyond that OSNMA "shall not
  be used". Do not re-sync that clock from the GNSS solution being authenticated (Receiver Guidelines
  1.3 sec. 2.1, 5.3.1, Annex C, via the [digest](../../docs/paper-digests/galileo-osnma.md)). In
  practice: RTC with holdover, NTP/PTP over a trusted link, or a disciplined oscillator (see
  [timing resilience](../../docs/timing-resilience.md)). Both OSNMAlib file mode and GNSS-SDR 0.0.20
  default mode skip this and trust the signal; that is what made `replay_no_clock` pass.
- **Cold / warm / hot start.** Cold: Merkle root only; the public key must arrive in a DSM-PKR, which
  did not appear in this 76 min recording. Warm: public key provisioned (from the GSC), KROOT from
  the signal; first ADKD0 authentication at 90 s here. Hot: saved KROOT (OSNMAlib writes
  `OSNMA_last_KROOT.txt`; not timed here). Key and tree renewals (PKID 1 => 2 on 2025-12-10) mean
  provisioning is ongoing, not one-off.
- **Coverage.** Only part of the constellation transmits OSNMA; others are covered by
  cross-authentication tags. In the recording 5-6 of 10 tracked SVs carried OSNMA data at a time and 9
  were ADKD0-authenticated.
- **Receiver support (vendor / third-party sources, not tested here).**
  u-blox: OSNMA on ZED-F9P announced July 2024
  ([GPS World](https://www.gpsworld.com/u-blox-enhances-jamming-and-spoofing-protection-with-osnma-firmware-update));
  Holybro's page says ZED-F9P firmware 1.51 supports it and keys come from GSC registration
  ([Holybro docs](https://docs.holybro.com/gps-and-rtk-system/f9p-h-rtk-series/galileo-osnma-support)).
  No source found for M10. Septentrio: OSNMA across the mosaic family since 2022
  ([mosaic-T](https://septentrio.com/mosaic-t)); the ROS driver docs say firmware < 4.12.1 lacks it
  ([septentrio_gnss_driver](https://docs.ros.org/en/iron/p/septentrio_gnss_driver)). Software:
  OSNMAlib (u-blox `RXM-SFRBX`, Septentrio `GALRawINAV`, GNSS-SDR, galmon), GNSS-SDR >= 0.0.20,
  [galileo-osnma](../../catalog/repos/daniestevez__galileo-osnma.md) (Rust, no_std).
- **What to report.** Per-SV authentication state with its age, separate from fix validity, and
  "not-measured" as its own state. A dropped authentication with strong signals is an alarm.

## Pitfalls

- OSNMAlib in file mode trusts the recording's time. Any replay demo without an independent clock
  "passes"; that is the finding, not a bug in the demo.
- A same-IOD forgery after authentication is invisible in OSNMAlib's status (forge_nav_late). Use
  the authenticated copy of the data for PVT.
- Thresholds (60 s freshness, 50 % authenticated fraction, 35 dB-Hz) are starting points measured on
  one 76 min static recording.
- `forge_keys` assumes the MACLT 34 layout (6 tags of 40 bits, 128-bit key) that was in force in the
  recording; another MACLT/key size needs `TAG_BITS`, `TAGS_PER_MACK`, `KEY_BITS` changed.
- OSNMAlib is EUPL-1.2 and is used as an external checkout; nothing from it is copied here except
  derived run summaries. OSNMA-SDR-SIM has no licence file (see its card).

Sources: OSNMAlib commit 25aa61de (`osnma/receiver/receiver.py`, `osnma_core/nav_data_manager.py`,
`osnma_core/tag_verification.py`, `osnma_core/tesla_chain.py`, `utils/status_logger.py`,
`tests/test_corner_cases.py`); GNSS-SDR `docs/CHANGELOG.md`, `src/core/libs/osnma_msg_receiver.cc` and
`src/core/receiver/gnss_flowgraph.cc` at v0.0.20; OSNMA-SDR-SIM commit e0b80759 README and
`E1_off_line.conf`; [OSNMA SIS ICD](../../catalog/resources/galileo-osnma-sis-icd.md),
[Receiver Guidelines](../../catalog/resources/galileo-osnma-receiver-guidelines.md).
