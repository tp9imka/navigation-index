# Upstream findings

<!-- about: repo:algafix/osnma, repo:opendroneid/opendroneid-core-c, repo:stanford-navlab/gnss_lib_py, repo:px4/px4-autopilot, repo:gnss-sdr/gnss-sdr, repo:haiyang-wong/osnma-sdr-sim, repo:utiasstars/pyshoe, repo:ion-g-ion/mavlinkmcp, repo:semuconsulting/pyubx2, repo:smroid/cedar-solve, repo:univaasadigieco/vaara, repo:rtklibexplorer/rtklib, repo:tomojitakasu/rtklib, repo:krakenrf/heimdall_daq_fw, repo:dstl/stone-soup, repo:michaelgrupp/evo -->

Defects and gaps that the hub's samples found in other people's code and data, with what a
maintainer needs to act on them. Nothing here has been reported. Every entry waits for the hub
owner to decide whether, where and as whom to file it.

Started 2026-11-06 from [review round 2](reports/review-round2.md) fix 16, the
[card vs sample cross-check](reports/card-sample-crosscheck.md) and the sample READMEs. The
hub's own defects (the interference scorer) are tracked in
[real-attack-replay](../samples/real-attack-replay/README.md#findings), not here.

Rules for this page:

- **Status** is `not filed - awaiting owner decision` until the owner files something; then
  `filed #N (date)` or `reported privately (date)`, and later `fixed in vX`.
- **Security-relevant** findings go to the project privately (security policy, GitHub private
  vulnerability reporting, or the maintainer's published contact), never as a public issue
  first. "PVR" below = GitHub private vulnerability reporting, as returned by
  `gh api repos/<owner>/<repo>/private-vulnerability-reporting` on 2026-11-06.
- **Re-check on the latest release before filing.** Versions below are the ones the samples ran
  or read; several projects moved since.
- **No VAARA bytes in reports.** The Jammertest VAARA dataset states no licence; point at the
  public file, do not attach it.
- Search the tracker first. Where a matching upstream issue already exists, the action is a
  comment with our reproduction, not a new issue.

## Summary

| # | Project | Finding | Kind | Channel | Status |
|---|---|---|---|---|---|
| 1 | OSNMAlib | Forged navigation words with an unchanged IOD stay "authenticated" after the genuine block was authenticated (10 min on E23) | **security** | private: maintainer contact in the OSNMAlib README (no SECURITY.md, PVR off) | not filed - awaiting owner decision |
| 2 | OSNMAlib | File mode takes time from the signal's own GST, so a replay without an independent clock authenticates | docs | public issue | not filed - awaiting owner decision |
| 3 | opendroneid-core-c | `decodeOpenDroneID` on a message pack trusts `MsgPackSize` from the frame (over-read on hostile radio input) | possibly security | private first (no SECURITY.md, PVR off): ask the maintainers for a contact | not filed - awaiting owner decision |
| 4 | opendroneid-core-c | `decodeHorizontalAccuracy(ODID_HOR_ACC_4NM)` returns 7808 m; 4 NM is 7408 m | bug | public issue | not filed - awaiting owner decision |
| 5 | opendroneid-core-c | 21-byte copy from a 20-byte UUID / session ID field; no range checks on decoded lat/lon | bug | public issue | not filed - awaiting owner decision |
| 6 | gnss_lib_py | 1.1.0 `RinexObs` treats RINEX GPS-time epochs as UTC (km-level SPP errors) | bug | comment on existing open issue #180 | not filed - awaiting owner decision (already reported upstream as #180) |
| 7 | gnss_lib_py | `add_sv_states_rinex` uses one ephemeris per SV for the whole input (residuals drift to ~25 m over 2 h) | bug or docs | public issue | not filed - awaiting owner decision |
| 8 | PX4-Autopilot | v1.17.0 SIH: `failure gps off` / `MAV_CMD_INJECT_FAILURE` for GPS gets no ACK and does nothing, while the docs table lists it | docs (v1.17) | public issue, after checking `main` | not filed - awaiting owner decision |
| 9 | GNSS-SDR | 0.0.20 segfaults (exit 139, no message) on the short-form OSNMA public-key XML | bug | public issue, after re-testing 0.0.22 | not filed - awaiting owner decision |
| 10 | GNSS-SDR | Strict-mode PVT keeps Galileo SVs by PRN + `IOD_nav`, not data bits: may share finding 1's same-IOD gap | possibly security, untested | private, only after a test | not filed - awaiting owner decision (needs a test first) |
| 11 | OSNMA-SDR-SIM | Does not compile with GCC 14 without `-include bitset`; default `cross_auth_mode=3` never completed DSM-KROOT in 600 s with GNSS-SDR 0.0.20; no licence file | build / bug / licence | public issue | not filed - awaiting owner decision |
| 12 | pyubx2 | 1.4.1 raises `UnicodeDecodeError` on mixed UBX + NMEA logs when a `$` byte inside a UBX payload starts an NMEA parse | bug | public issue with a minimal byte sequence | not filed - awaiting owner decision (no shareable repro yet) |
| 13 | cedar-solve | `pyproject.toml` on master still says version 0.5.1 and pins `numpy<2`, `Pillow<9`, although tag v0.6.0 runs on NumPy 2; PyPI has only 0.5.1 | packaging | public issue | not filed - awaiting owner decision |
| 14 | pyshoe | Breaks on numpy >= 1.24 (`np.int`, `np.float`, `np.maximum_sctype`); no licence file; README says 39 hallway trials, the FTP has 36 | bug / licence / docs | public issue | not filed - awaiting owner decision |
| 15 | MAVLinkMCP | `pyproject.toml` depends on unpinned `mavsdk`; `pip install -e .` can pull 4.x, a different API (inferred, not tested) | packaging | public issue | not filed - awaiting owner decision |
| 16 | VAARA (Univ. Vaasa) | No licence stated for the Jammertest 2024 recordings | licence request | public issue | not filed - awaiting owner decision |
| 17 | RTKLIB demo5 | Upstream RTKLIB has open memory-safety reports (#799 RTCM 1033, #803 NTRIP); demo5's `decode_type1033` clamps lengths, the rest is unchecked | security, check first | private via PVR (enabled on rtklibexplorer/RTKLIB) if affected | not filed - awaiting owner decision (needs a check first) |

Already known upstream, nothing to file: Heimdall DAQ synthetic mode (closed #16), FFTA.jl 0.3.2
ambiguity that broke MagNav.jl precompilation (closed #146, fix #147), RTKLIB upstream #799 / #803
themselves. Not upstream defects: Stone Soup set-order nondeterminism, evo on a straight line
(see [the end of this page](#checked-and-not-filed)).

## 1. OSNMAlib: same-IOD forged words stay authenticated

- **Repo / version:** [Algafix/OSNMA](https://github.com/Algafix/OSNMA) at commit `25aa61de`
  (2026-10-14). Code: `ADKD0DataBlock.add_word` / `_compute_data_stream` in
  `osnma/osnma_core/nav_data_manager.py`.
- **Reproduction:** [osnma-authentication](../samples/osnma-authentication/README.md#results-on-the-real-recording-ran-2026-11-06),
  scenario `forge_nav_late`: `osnma_scenarios.py --osnmalib /path/to/OSNMA --minutes 20` on the
  76 min Galileo recording that ships with OSNMAlib (`custom_run/current_config.sbf`), one bit of
  OMEGA_0 (word type 2) flipped on E19, E23, E27 from minute 10, after the genuine words were
  authenticated. Reed-Solomon recovery off.
- **Evidence:** the authenticated bit stream of an ADKD0 block is computed once, when the block
  first completes; later words with the same IOD overwrite `words` but not that stream. Tags keep
  verifying against the genuine copy. E23 (no IOD change in the window) stayed ADKD0-authenticated
  for 10 min while the receiver decoded forged OMEGA_0 (`words_differ_from_authenticated_stream:
  [23]`). E27 changed IOD at 950 s; its new block was built from forged words and tags failed from
  1020 s.
- **Why it matters:** a receiver that asks OSNMAlib "is E23 authenticated?" and navigates on the
  words it decoded gets "yes" for forged ephemeris. The library's status does not cover the data
  a PVT engine actually uses.
- **Suggested report text:** "After an ADKD0 block for an SV is authenticated, subsequent words
  with the same IOD that differ from the authenticated stream are accepted into `words` without
  invalidating the SV's authenticated state. In our test (commit 25aa61de, bundled
  `current_config.sbf`, one bit of OMEGA_0 flipped on E23 from minute 10, RS recovery off) E23
  stayed authenticated for 10 minutes while the decoded word differed. We'd suggest either
  dropping authentication when a same-IOD word differs from the authenticated stream, or
  exposing the authenticated words so a PVT engine can use them instead of the latest decoded
  ones. Scenario script and per-run summary available on request."
- **Channel:** private. No SECURITY.md and PVR disabled on the repo, so use the contact address
  in OSNMAlib's README. The GSC is not the right first contact: this is a library behaviour, not
  a signal or service issue.
- **Status:** not filed - awaiting owner decision.

## 2. OSNMAlib: file mode trusts the signal's time

- **Repo / version:** as 1. `osnma/receiver/receiver.py` (file input, time from the signal, TS
  fixed at 30 s).
- **Reproduction:** same script, scenario `replay_no_clock`: an 11-month-old recording
  authenticates fully on 2026-11-06 (989 tags, 0 failures in 20 min). With an independent clock
  (`meacon_3s`, `replay_60s`, `replay_1h`) OSNMAlib degrades as the Receiver Guidelines expect.
- **Evidence:** [results table](../samples/osnma-authentication/README.md#results-on-the-real-recording-ran-2026-11-06).
- **Suggested report text:** "In file / post-processing mode OSNMAlib takes receiver time from
  the signal's GST, so a replayed recording authenticates with no warning. That is expected for
  post-processing, but a user wiring OSNMAlib to a live receiver may not realise the time check
  needs an independent clock. Could the README or the status output say when time comes from the
  signal itself?"
- **Channel:** public issue (documentation; this is a known property of OSNMA, not a library bug).
- **Status:** not filed - awaiting owner decision.

## 3. opendroneid-core-c: pack decode trusts `MsgPackSize`

- **Repo / version:** [opendroneid/opendroneid-core-c](https://github.com/opendroneid/opendroneid-core-c)
  master `849c03a` (2026-10-07), `libopendroneid/opendroneid.c`.
- **Reproduction:** [remote-id-to-tak](../samples/remote-id-to-tak/README.md#1-decoder-validated-against-opendroneid-core-c-ran-it)
  builds a harness (`corec/odid_vectors.c`, `corec/build.sh`) against upstream `opendroneid.c`.
  Finding from mirroring the code, not from a crash: `decodeOpenDroneID` on a pack reads
  `MsgPackSize` messages from the buffer without a length argument; only
  `odid_message_process_pack` checks the length.
- **Evidence:** sample README "Things found in core-c" and the
  [core-c card](integration-cards/opendroneid__opendroneid-core-c.md#verified-in-this-hub).
  Not shown: an actual out-of-bounds read under a sanitizer, or which receivers call the bare
  decoder on radio input.
- **Before filing:** build the harness with `-fsanitize=address`, feed a pack whose
  `MsgPackSize` exceeds the bytes received, and check the receiver apps that call
  `decodeOpenDroneID` directly. If the over-read is real and reachable from radio frames, it is a
  memory-safety bug on attacker-controlled input.
- **Suggested report text:** "`decodeOpenDroneID()` on a message pack iterates `MsgPackSize`
  messages from the input buffer; the bare function has no buffer length, so a frame that claims
  more messages than it carries is read past its end. `odid_message_process_pack()` checks the
  length, the bare decoder does not. Reproducer: [ASan output]."
- **Channel:** private first. No SECURITY.md, PVR off: ask the maintainers in a minimal public
  issue for a private contact, without details. Downgrade to a public issue if the check shows it
  is not reachable from radio input.
- **Status:** not filed - awaiting owner decision.

## 4. opendroneid-core-c: 4 NM decodes to 7808 m

- **Repo / version:** as 3, `decodeHorizontalAccuracy`.
- **Reproduction:** remote-id-to-tak's decoder is checked field for field against core-c (500
  encoded vectors, 500 random raw messages, 81 captured payloads) and keeps core-c's 7808 m so
  outputs match (`odid.HORIZ_ACC_M`).
- **Evidence:** `decodeHorizontalAccuracy(ODID_HOR_ACC_4NM)` returns 7808; 4 NM = 4 x 1852 m =
  7408 m, which is also what the enum comment says. Closed #23 (2020) fixed a different
  accuracy-encoding mismatch.
- **Suggested report text:** "`decodeHorizontalAccuracy(ODID_HOR_ACC_4NM)` returns 7808 m. 4 NM
  is 7408 m (4 x 1852), and the enum comment says < 7408 m. Looks like a typo in the lookup."
- **Channel:** public issue (or a one-line PR).
- **Status:** not filed - awaiting owner decision.

## 5. opendroneid-core-c: 21-byte ID copy, no range checks

- **Repo / version:** as 3, `decodeBasicIDMessage`, all decoders.
- **Evidence:** for UUID / session IDs `decodeBasicIDMessage` copies `sizeof(UASID)` = 21 bytes
  from a 20-byte field; the 21st byte is the first reserved byte, so the C string is not
  NUL-terminated when that byte is nonzero. Stays inside the packed struct. Corrupted BT5 frames
  without the sniffer CRC check decoded to lat -89.8, lon -214.6: no range check on decode.
- **Suggested report text:** "(a) `decodeBasicIDMessage` copies 21 bytes into `UASID` for
  UUID/session-ID types although the field is 20 bytes; the string is unterminated when the
  reserved byte is set. (b) Decoders return out-of-range values (lon -214.6 from a corrupted
  frame); a `valid` flag or range check would help receivers that skip CRC."
- **Channel:** public issue.
- **Status:** not filed - awaiting owner decision.

## 6. gnss_lib_py: RINEX GPS time read as UTC

- **Repo / version:** [Stanford-NavLab/gnss_lib_py](https://github.com/Stanford-NavLab/gnss_lib_py)
  1.1.0 (PyPI), `RinexObs`.
- **Reproduction:** [gnss-rinex-processing](../samples/gnss-rinex-processing/README.md), `glp_spp.py`
  on public NOAA CORS P730 RINEX (2024-04-09, 12:00-14:00 GPST).
- **Evidence:** epochs are tagged as UTC and 18 leap seconds are added, so every SV is propagated
  to the wrong second: 7.3 / 3.9 / 5.6 km E/N/U RMS on the first attempt. Subtracting the leap
  seconds, plus findings 7 and transmit-time states, brings the WLS fix to within a few cm of
  RTKLIB SPP per axis.
- **Upstream:** open issue #180 "gps milliseconds conversion seems off" describes the same
  assumption, with no reproduction numbers.
- **Suggested comment on #180:** "Reproduced on 1.1.0 with public CORS data (P730, 2024-04-09):
  treating the RINEX obs epochs as UTC adds 18 s and puts WLS 7.3 / 3.9 / 5.6 km off (E/N/U RMS);
  shifting by the leap seconds fixes it. Script: [link to glp_spp.py]."
- **Channel:** comment on #180.
- **Status:** not filed - awaiting owner decision (already reported upstream as #180).

## 7. gnss_lib_py: one ephemeris per SV per call

- **Repo / version:** as 6, `add_sv_states_rinex`.
- **Evidence:** it picks the ephemeris at the earliest epoch of its input and uses it for the
  whole input; per-SV residuals drift linearly to ~25 m over 2 h. Calling it per 15-minute chunk
  fixes it ([sample README](../samples/gnss-rinex-processing/README.md), "Pass 3" notes).
- **Suggested report text:** "`add_sv_states_rinex` selects one ephemeris per SV at the first
  epoch and applies it to all epochs, so on a 2 h file residuals grow to ~25 m. Is that
  intended? If so, a docstring note would help; otherwise selecting the nearest `toe` per epoch
  would fix it."
- **Channel:** public issue.
- **Status:** not filed - awaiting owner decision.

## 8. PX4 v1.17.0 SIH: GPS failure injection gets no ACK

- **Repo / version:** [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) tag v1.17.0,
  SIH (`sihsim_quadx`), headless Docker image from [sitl-docker](../samples/sitl-docker/README.md).
- **Reproduction:** [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/README.md):
  `failure gps off` in the pxh shell, or MAVSDK `failure.inject(SENSOR_GPS, OFF)`, with
  `SYS_FAILURE_EN=1`.
- **Evidence:** the command timed out with no ACK and GPS stayed on. In v1.17.0 commander's
  `FailureInjector` handles only `FAILURE_UNIT_SYSTEM_MOTOR`; GPS failure handling sits in
  `simulator_mavlink`, not SIH ([PX4 card](integration-cards/px4__px4-autopilot.md#verified-in-this-hub)).
  The docs' failure-injection table suggests GPS works in SIH. `param set SIM_GPS_USED 0` works.
- **Upstream:** `main` / v1.18.0-rc1 add `failure_injection_manager` and there is an open PR
  #28955 "SIH failover tests with injected receiver failures", so `main` may already behave.
- **Suggested report text (docs, only if `main` docs still claim it for v1.17):** "On v1.17.0 SIH,
  `failure gps off` returns no ACK and has no effect (commander only handles motor failures there).
  The failure-injection docs table lists GPS as supported in SIH. Could the table note the
  version, or point to `SIM_GPS_USED 0` for v1.17?"
- **Channel:** public issue (docs). PX4 has a SECURITY.md and PVR; not needed here.
- **Status:** not filed - awaiting owner decision.

## 9. GNSS-SDR 0.0.20: segfault on a short-form public-key XML

- **Repo / version:** [gnss-sdr/gnss-sdr](https://github.com/gnss-sdr/gnss-sdr) v0.0.20
  (source build, aarch64 Docker).
- **Reproduction:** [osnma-authentication](../samples/osnma-authentication/README.md#gnss-sdr-with-osnma-on-a-simulated-e1-iq-file),
  `gnss-sdr/Dockerfile` + `run_sim.sh`, with OSNMA-SDR-SIM's own public-key XML instead of the
  PEM the sample ships.
- **Evidence:** exit 139, no output. The same key converted to PEM works (key and DSM-KROOT
  verified). The XML that fails is the simulator's short form, not the GSC's file.
- **Before filing:** re-test on 0.0.22 (2026-10-04 hardened OSNMA) and save the XML that crashes.
- **Suggested report text:** "GNSS-SDR 0.0.20 exits with SIGSEGV and no log line when
  `GNSS-SDR.osnma_public_key` points at [attached XML]. A malformed key file should give an error,
  not a crash."
- **Channel:** public issue (local configuration file, not remote input).
- **Status:** not filed - awaiting owner decision.

## 10. GNSS-SDR strict mode: PRN + IOD match (untested)

- **Repo / version:** v0.0.20, `rtklib_pvt_gs.cc`.
- **Evidence:** by code reading only: in strict mode an E1B/E5b observable is kept if its PRN and
  `IOD_nav` are in the authenticated set, not if its data bits match the authenticated ones. That
  looks like the same same-IOD gap as finding 1. Not tested (the sample could not get GNSS-SDR to
  authenticate tags at all, see 11).
- **Action before any report:** build a test that forges a same-IOD word after authentication
  and checks whether the PVT uses it. Only report with that result, and privately.
- **Channel:** private if confirmed: GNSS-SDR has no SECURITY.md and PVR is off; use the
  developers' contact on [gnss-sdr.org/team](https://gnss-sdr.org/team/).
- **Status:** not filed - awaiting owner decision (needs a test first).

## 11. OSNMA-SDR-SIM: GCC 14 build, cross-auth default, licence

- **Repo / version:** [haiyang-wong/OSNMA-SDR-SIM](https://github.com/haiyang-wong/OSNMA-SDR-SIM)
  commit `e0b80759`.
- **Evidence** ([sample](../samples/osnma-authentication/README.md#gnss-sdr-with-osnma-on-a-simulated-e1-iq-file),
  [card](integration-cards/haiyang-wong__osnma-sdr-sim.md)):
  - Does not compile with GCC 14 unless `-include bitset` is added (missing `#include <bitset>`).
  - With the default `cross_auth_mode=3` only 4 of 7 visible PRNs carried OSNMA and GNSS-SDR 0.0.20
    never completed DSM-KROOT (7 of 8 blocks in 600 s); `cross_auth_mode=1` delivered all 8 blocks
    about 4 min in.
  - GNSS-SDR's fix was about 3,000 km from the configured position (42.349 N, 71.088 W vs 20 N,
    51 W). Cause not investigated; could be on either side. Do not report until understood.
  - No licence file.
- **Suggested report text:** "(a) Build fails on GCC 14: `std::bitset` used without
  `#include <bitset>` (adding `-include bitset` works). (b) With the default
  `cross_auth_mode=3`, a 600 s E1 file never delivered a complete DSM-KROOT to GNSS-SDR 0.0.20;
  mode 1 did. Is mode 3 expected to need longer, or should the default change? (c) Could you add
  a licence file?"
- **Channel:** public issue (or a PR for a).
- **Status:** not filed - awaiting owner decision.

## 12. pyubx2 1.4.1: `UnicodeDecodeError` on mixed UBX + NMEA

- **Repo / version:** [semuconsulting/pyubx2](https://github.com/semuconsulting/pyubx2) 1.4.1
  (latest on PyPI on 2026-11-06).
- **Reproduction:** [real-attack-replay](../samples/real-attack-replay/README.md#data-survey-what-is-public-small-and-receiver-level)
  reports the error on the real VAARA u-blox logs: a `$` byte inside a binary UBX payload starts
  an NMEA parse. The sample's synthetic fixture (`make_fixture.py`) does **not** reproduce it:
  checked here on 2026-11-06, pyubx2 1.4.1 parsed its 8250 messages with no exception.
- **Before filing:** cut a minimal byte sequence from a VAARA file locally (do not attach VAARA
  bytes; describe the file and offset instead, or synthesise the same bytes), and try
  `UBXReader(..., quitonerror=...)` variants.
- **Upstream:** closed #63 was a `UnicodeDecodeError` on an MGA file, a different input.
- **Channel:** public issue. pyubx2 has a SECURITY.md; this is a robustness bug, not a security
  issue.
- **Status:** not filed - awaiting owner decision (no shareable repro yet).

## 13. cedar-solve: packaging lags the v0.6.0 tag

- **Repo / version:** [smroid/cedar-solve](https://github.com/smroid/cedar-solve) tag v0.6.0;
  `pyproject.toml` on master read 2026-11-06.
- **Evidence:** [celestial-star-tracker](../samples/celestial-star-tracker/README.md#run) installs
  v0.6.0 with `--no-deps` and runs on numpy 2.5.4 and Pillow 13.0.0 (40 / 40 solves). Master's
  `pyproject.toml` still declares version 0.5.1, `numpy >= 1.21.1,<2` and `Pillow >= 8.3.1,<9`
  (Pillow 8 has no wheels past Python 3.10). PyPI has only 0.5.1, which predates the `np.math`
  fix (closed #19).
- **Suggested report text:** "v0.6.0 runs fine on NumPy 2 and current Pillow (we tested numpy
  2.5.4, Pillow 13.0.0 on Python 3.12), but `pyproject.toml` still pins `numpy<2` and `Pillow<9`
  and says 0.5.1, so a normal install fails or downgrades. Could the pins be relaxed and 0.6.0
  published to PyPI?"
- **Channel:** public issue.
- **Status:** not filed - awaiting owner decision.

## 14. pyshoe: numpy >= 1.24, licence, trial count

- **Repo / version:** [utiasSTARS/pyshoe](https://github.com/utiasSTARS/pyshoe) commit `6bbc4df`.
- **Evidence** ([dismounted-foot-ins](../samples/dismounted-foot-ins/README.md#run),
  [card](integration-cards/utiasstars__pyshoe.md)): `INS.baseline` needs Python 3.11 + numpy 1.23.5
  + scipy 1.10.1 because of `np.int`, `np.float`, `np.maximum_sctype` (removed in numpy 1.24 / 2.0);
  no LICENSE file and no licence in GitHub metadata; the README says 39 hallway trials, the UTIAS
  FTP serves 36.
- **Suggested report text:** "(a) The code uses `np.int`, `np.float` and `np.maximum_sctype`,
  which numpy >= 1.24 removed; replacing them with `int`, `float`, `np.float64` makes it run on
  current numpy. (b) The repo has no licence file; could you add one so others can reuse the code?
  (c) The README mentions 39 hallway trials; the FTP has 36."
- **Channel:** public issue.
- **Status:** not filed - awaiting owner decision.

## 15. MAVLinkMCP: unpinned `mavsdk`

- **Repo / version:** [ion-g-ion/MAVLinkMCP](https://github.com/ion-g-ion/MAVLinkMCP), source read
  at the 2026-08-31 commit.
- **Evidence** ([card](integration-cards/ion-g-ion__mavlinkmcp.md)): `pyproject.toml` depends on
  unpinned `mavsdk` and imports `from mavsdk import System` (gRPC API); `uv.lock` pins 3.17.2;
  PyPI `mavsdk` 4.x is the native binding with a different API. Inferred from the files, not run.
- **Before filing:** run `pip install -e .` in a clean venv and confirm the import fails.
- **Suggested report text:** "`pip install -e .` resolves `mavsdk` 4.x, whose API differs from the
  3.x gRPC wrapper the code uses (`uv.lock` pins 3.17.2). Pinning `mavsdk<4` in `pyproject.toml`
  would keep pip installs working."
- **Channel:** public issue.
- **Status:** not filed - awaiting owner decision.

## 16. VAARA: no licence on the Jammertest 2024 recordings

- **Repo:** [UniVaasaDigiEco/VAARA](https://github.com/UniVaasaDigiEco/VAARA).
- **Evidence:** no LICENSE file and no licence in GitHub metadata; real-attack-replay therefore
  ships only a synthetic fixture with the same layout and derived numbers
  ([sample](../samples/real-attack-replay/README.md#tests)). Also worth passing on: their field
  log is 50 min off the 2024 NPRA plan for Thursday (2.4.12 logged at 08:20 UTC = 10:20 CEST, plan
  11:10 CEST), which is how 2.4.2 / 2.4.3 were located.
- **Suggested report text:** "Thanks for publishing the Jammertest 2024 logs. Could you add a
  licence (e.g. CC BY 4.0) so others can redistribute small excerpts as test fixtures? We replay
  the u-blox logs in an open-source interference-monitor evaluation and currently ship only
  synthetic look-alikes."
- **Channel:** public issue.
- **Status:** not filed - awaiting owner decision.

## 17. RTKLIB demo5: check the upstream memory-safety reports

- **Repos:** upstream [tomojitakasu/RTKLIB](https://github.com/tomojitakasu/RTKLIB) (frozen since
  2020) has open reports #799 (out-of-bounds write in `decode_type1033`, unbounded RTCM3
  descriptor lengths into 64-byte fields; same pattern noted in 1007 / 1008) and #803 (NTRIP
  client memory safety). The hub's samples use [rtklibexplorer/RTKLIB](https://github.com/rtklibexplorer/RTKLIB)
  (demo5) in [gnss-rinex-processing](../samples/gnss-rinex-processing/README.md) and
  [real-attack-replay](../samples/real-attack-replay/README.md#rtklib-spp-during-the-attacks).
- **Checked here (code reading, demo5 `src/rtcm3.c`, last change `2628663e1`, 2026-08-28):**
  demo5's `decode_type1033` copies into local 32-byte buffers with `j<31` bounds, so the #799
  write does not apply there. When a length exceeds 31 the bit index is not advanced past the
  rest of the string, so later fields are read from the wrong offset (a parse error, not a
  memory error). Not checked: demo5's 1007 / 1008 decoders and its NTRIP client (#803).
- **Action before any report:** read demo5's `decode_type1007`, `decode_type1008` and
  `stream.c` NTRIP code against #799 / #803. If affected, report privately.
- **Channel:** private via GitHub PVR (enabled on rtklibexplorer/RTKLIB) if affected; the
  1033 offset issue alone is a public issue.
- **Status:** not filed - awaiting owner decision (needs a check first).

## Checked and not filed

- **Heimdall DAQ firmware synthetic mode** ([card](integration-cards/krakenrf__heimdall_daq_fw.md)):
  `daq_synthetic_start.sh` opens a FIFO no start script creates. Closed #16 reports exactly this
  and the maintainer said synthetic start is for development only. From source reading; no
  sample ran Heimdall. Nothing new to add.
- **FFTA.jl 0.3.2** broke `using MagNav` (`plan_rfft` ambiguous with FFTW, seen in
  [magnav-quickstart](../samples/magnav-quickstart/README.md)). Reported upstream as FFTA.jl #146
  (closed, fix #147). The sample pins FFTA 0.2; drop the pin once a fixed FFTA release resolves.
- **Stone Soup 1.9.1 nondeterminism** ([card](integration-cards/dstl__stone-soup.md)): the
  sample kept truths and tracks in Python sets whose order follows random UUIDs. That is a
  usage pitfall, not a Stone Soup defect; at most a docs note.
- **evo Umeyama alignment on a perfectly straight line** fails with a degenerate covariance
  ([relative-nav-benchmark](../samples/relative-nav-benchmark/README.md)). Mathematically
  expected for a degenerate trajectory; not worth filing.
- **PX4 EKF2 at 3 m/s drag** ([golden-demo-px4 sweep](../samples/golden-demo-px4/README.md#sweep-ran-2026-11-06-20-flights)):
  EKF2 flagged `GPS_GLITCH` yet the vehicle still flew the full 150 m offset, which looks like a
  reset onto GNSS after the rejection timeout. Not traced in the v1.17 source, and possibly by
  design. Investigate before calling it a defect.
