# OSNMA-SDR-SIM - integration card
<!-- about: repo:haiyang-wong/osnma-sdr-sim -->
One-line: generates Galileo E1-B baseband IQ files with real OSNMA authentication data embedded (plus an optional matching E5b file), so you can test an OSNMA-aware receiver chain ([GNSS-SDR](./gnss-sdr__gnss-sdr.md) => [OSNMAlib](./algafix__osnma.md)) offline, including deliberately unauthenticated satellites.

> **Legal boundary.** Radiating GNSS signals over the air without authorization is illegal in practically every jurisdiction and endangers aviation and other users. The tool has a USRP transmit path (`usrp=0`); this card covers file output only. Any hardware test must be cabled into the receiver through attenuation, or run in a certified shielded enclosure under the relevant authorization. Read [docs/export-control-and-ethics.md](../export-control-and-ethics.md#3-gnss-signal-simulation-and-rf-transmission) first.

| | |
|---|---|
| Install | No releases or tags. Build from source (README): `sudo apt-get install -y libuhd-dev uhd-host gnss-sdr g++ libncurses-dev cmake pkg-config libboost-dev libglib2.0-dev build-essential`, then `git clone https://github.com/Haiyang-Wong/OSNMA-SDR-SIM.git && cd OSNMA-SDR-SIM && mkdir build && cd build && cmake ../ && make`. `CMakeLists.txt` also does `find_package(Curses REQUIRED)`, `CURL REQUIRED`, `ZLIB REQUIRED`, Boost `thread system program_options`. UHD headers are needed even for file-only output (`structures.h` includes `<uhd/usrp/multi_usrp.hpp>`). Produces two binaries: `osnma-sdr-sim` (E1 + OSNMA) and `osnma-sdr-sim-e5` (E5b), which E1 forks/execs when `enable_e5=true`. |
| Runs on | Linux (README apt line; `main.cpp` includes `<malloc.h>`, `<sys/wait.h>`, `sys/shm.h`). macOS/Windows not stated. CPU only. USRP only for the transmit path, which is out of scope here. Last push 2026-07-06. |
| Inputs | One INI file passed with `-f`: `location=lat,lon,height` (static only, no trajectory), `start_time=YYYY/MM/DD,hh:mm:ss`, `rinex_file` (Galileo RINEX nav; four dated samples in `rinex_files/`), `osnma_file` (auxiliary OSNMA CSV `TOW,OSNMA40` keyed to the start time; four recorded days in `auxiliary_osnma/`, built from real I/NAV page dumps by `auxiliary_osnma/make_keychain_csv.py`), `output_file`, `usrp`, `bit`, `duration` [s], `enable_e5`, `cross_auth_neighbor_count`, `cross_auth_mode` (1-3), optional `no_osnma_prns=[..]`, `output_file_e5`. Public keys for verification ship in `OSNMA_PublicKey/` (2023-08-16, 2023-10-07, 2026-03-19, 2026-05-13). |
| Outputs | E1 file: interleaved signed 16-bit I/Q, 2.6 MS/s (`SAMP_RATE = 2.6e6` in `src/e1/include/constants.h`; GNSS-SDR conf uses `item_type=ishort`, `sampling_frequency=2600000`). E5b file: same format at 20.46 MS/s (`TX_SAMPLERATE 20460000.0` in `src/e5/include/constants.h`), default name `<output>_e5.bin`. Console logs of tags/cross-authentication. |
| Key API / entry points | CLI only: `./osnma-sdr-sim -f ../config/run_config.ini` (`main()` rejects anything other than exactly `-f <file>`). Config parser `applyRunConfig()` in `src/e1/src/main.cpp`; tag generation (built-in SHA-256/HMAC) in `src/e1/src/genarate-tag.cpp`, `msg-tag.cpp`, `cross_authentication.cpp`. GNSS-SDR configs: `E1_off_line.conf`, `E5_off_line.conf` (file source), `*_on_line.conf`. Helpers: `auxiliary_osnma/make_keychain_csv.py`, `scripts/cross_tags_per_subframe.py`. |
| Time to first result | Estimate: 1-2 h on Ubuntu to install UHD/GNSS-SDR from apt, build, generate a 60-120 s E1-only file with a bundled date, and see GNSS-SDR report OSNMA status. Assumes apt access and a GNSS-SDR build with OSNMA support; OSNMA needs several subframes (30 s each) before the first authentication. |
| License | GitHub metadata: none (no LICENSE file). `CMakeLists.txt` carries an Ettus `SPDX-License-Identifier: GPL-3.0-or-later` header copied from a UHD example; the upstream it was built from ([galileo-sdr-sim](https://github.com/harshadms/galileo-sdr-sim)) also has no licence in metadata. Treat as all-rights-reserved for anything beyond private evaluation. |

## Minimal usage
Not run. E1 only, file sink, short scenario using the bundled 2026-05-13 data:

```ini
# config/e1_only.ini  (usrp=1 means NO transmission, write to file)
location=20,-51,100
start_time=2026/05/13,12:41:01
osnma_file=../auxiliary_osnma/13_MAY_2026_GST_12_11_01_keychain.csv
rinex_file=../rinex_files/2026_05_13.rnx
output_file=../../OSNMA-SIM.bin
usrp=1
bit=0
duration=120
enable_e5=false
cross_auth_neighbor_count=4
cross_auth_mode=3
no_osnma_prns=[]
```
```bash
cd build && ./osnma-sdr-sim -f ../config/e1_only.ini
# then: set SignalSource.filename in ../E1_off_line.conf, point osnma_public_key at
# ../OSNMA_PublicKey/OSNMA_PublicKey_2026_05_13.xml and run
gnss-sdr --config_file=../E1_off_line.conf
```

## Wiring it into a nav stack
- Offline OSNMA test loop: OSNMA-SDR-SIM IQ file => [GNSS-SDR](./gnss-sdr__gnss-sdr.md) (built-in OSNMA, `GNSS-SDR.osnma_enable=true`) for PVT + authentication status, or GNSS-SDR's I/NAV page UDP stream => [OSNMAlib](./algafix__osnma.md) for a per-subframe JSON status log. That status log is the trust signal for an "authenticated position" or spoofing-alarm demo.
- Negative tests: put PRNs into `no_osnma_prns` (cross-authentication modes) to get satellites that are only authenticated via neighbours, or none at all, and check your integrity logic reacts. README states OSNMAlib cross-band (E1 authenticates E5b) needs its dummy-page filter (`if self._filter_page(page): continue`) commented out.
- Relation to [GPS-SDR-SIM](./osqzss__gps-sdr-sim.md): same family of "ephemeris + position + time => IQ file" generators (this one is built on galileo-sdr-sim, whose README credits gps-sdr-sim as its inspiration), but Galileo E1/E5b with OSNMA instead of GPS L1 C/A, config file instead of CLI flags, static position only.
- The OSNMA key/signature content is replayed from real recordings, not freshly signed (inferred from the `TOW,OSNMA40` CSV format and `make_keychain_csv.py`; tags are computed in `genarate-tag.cpp`): the simulator has no access to the GSC private key, so `start_time` must match a recorded `auxiliary_osnma` CSV and the matching public key must be given to the receiver. To use another date, record I/NAV pages (u-blox `RXM-SFRBX` via [pyubx2](./semuconsulting__pyubx2.md), or Septentrio) and convert with `make_keychain_csv.py` (input format: its docstring, not verified here).
- Concept page: [assured PNT](../../catalog/concepts/assured-pnt.md); sample [gnss-signal-chain](../../samples/gnss-signal-chain/).

## Gotchas
- **`usrp` is inverted**: `usrp=1` disables transmission and writes the file; `usrp=0` enables USRP TX (`s.opt.use_usrp = (usrpConfig == 0)` in `main.cpp`). Keep `usrp=1`.
- **Disk size**: derived from the formats, not measured. E1 at 2.6 MS/s x 4 bytes = ~10.4 MB/s; E5b at 20.46 MS/s x 4 bytes = ~82 MB/s. The shipped `run_config.ini` (`duration=600`, `enable_e5=true`) therefore writes roughly 6 GB + 49 GB. Use `enable_e5=false` and short durations first.
- `CMakeLists.txt` sets `CMAKE_BUILD_TYPE Release` and then unconditionally `set(CMAKE_BUILD_TYPE Debug)` with `-g -DDEBUG`, so builds are unoptimised; generation will be slower than an optimised build (not measured).
- `osnma-sdr-sim-e5` must sit next to `osnma-sdr-sim` (lookup in `main.cpp`), so run from `build/`.
- Bundled public key file `OSNMA_PublicKey_2026_03_19.xml.xml` has a double extension.
- Only four recorded dates are bundled; a `start_time` outside a recorded window has no valid OSNMA data. Ephemeris and OSNMA CSV must refer to the same day.
- No issues filed on GitHub (search returned none); 4 stars, single author, research code.

## Alternatives
- [GPS-SDR-SIM](./osqzss__gps-sdr-sim.md) - GPS L1 C/A IQ files with trajectories; no Galileo, no authentication. Archived.
- [multi-sdr-gps-sim](../../catalog/repos/mictronics__multi-sdr-gps-sim.md) - maintained gps-sdr-sim derivative; GPS only.
- No-signal route: replay recorded I/NAV pages straight into [OSNMAlib](./algafix__osnma.md) (bundled SBF/UBX recordings) or [galileo-osnma](../../catalog/repos/daniestevez__galileo-osnma.md) when you only need the authentication logic, not IQ-level realism.

Sources: `gh api repos/Haiyang-Wong/OSNMA-SDR-SIM` (metadata, licence null, pushed 2026-07-06), README.md, CMakeLists.txt, config/run_config.ini, src/e1/src/main.cpp (`main`, `applyRunConfig`, E5 fork/exec), src/e1/src/genarate-tag.cpp, src/e1/include/{constants.h, galileo-sdr.h, structures.h}, src/e1/src/usrp.cpp, src/e5/include/constants.h, E1_off_line.conf, E5_off_line.conf, auxiliary_osnma/make_keychain_csv.py and keychain CSV head, repo tree, commits list, issue search (none), harshadms/galileo-sdr-sim metadata and README (read 2026-11-06).
