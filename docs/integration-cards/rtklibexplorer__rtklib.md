# RTKLIB demo5 / RTKLIB-EX - integration card
<!-- about: repo:rtklibexplorer/rtklib -->
The fastest path from receiver logs or public RINEX to an SPP / RTK / PPK / PPP position file, plus `str2str` and `rtkrcv` for live NTRIP corrections and real-time RTK. Tuned for low-cost receivers (u-blox F9P and friends).

| | |
|---|---|
| Install | Windows: prebuilt binaries on the GitHub releases page (latest tag `v2.5.1`). Linux/macOS CLI: `git clone --depth 1 --branch v2.5.1 https://github.com/rtklibexplorer/RTKLIB.git && cmake -S RTKLIB -B RTKLIB/build -DCMAKE_BUILD_TYPE=Release && cmake --build RTKLIB/build -j` (README: `mkdir build; cd build; cmake ..; make; make test`). Qt5/6 needed only for the GUIs. Old per-app `gcc` makefiles still exist but are marked deprecated. Pre-built Linux packages via openSUSE OBS (`home:ReimannJens/rtklib-qt`), per README. |
| Runs on | Linux, Windows, macOS (CMake). Plain C, no GPU. Runs fine on a Raspberry Pi class board for `rtkrcv`/`str2str` (common community use, not stated in README). |
| Inputs | RINEX 2/3 OBS + NAV (also SP3, CLK, SBAS logs); raw receiver binaries (u-blox UBX, Septentrio SBF, NovAtel, etc.) via `convbin`; RTCM2/3 streams over serial, TCP, NTRIP for live work. Hatanaka `.crx`/`.d` needs `crx2rnx` on PATH. |
| Outputs | `.pos` text solutions (llh, ECEF xyz or ENU baseline; Q flag 1=fix, 2=float, 5=single), NMEA GGA (`-n`), solution status/residual files (`-y`), KML/GPX via `pos2kml`. `str2str` relays/converts streams (e.g. NTRIP => serial to feed a receiver RTCM). |
| Key API / entry points | CLIs in `app/consapp/`: `rnx2rtkp` (post-processing), `rtkrcv` (real-time), `str2str` (stream server/NTRIP), `convbin` (raw => RINEX), `pos2kml`. Library (`src/rtklib.h`): `postpos(gtime_t ts, gtime_t te, double ti, double tu, const prcopt_t*, const solopt_t*, const filopt_t*, char **infile, int n, char *outfile, const char *rov, const char *base)`, `rtkinit(rtk_t*, const prcopt_t*)`, `rtkpos(...)`, `pntpos(const obsd_t*, int n, const nav_t*, ...)`. Example configs in `data/config/`: `f9p_ppk.conf`, `f9p_urban.conf`, `septentrio_urban.conf`, `demo5_m8t_5hz.conf`. |
| Time to first result | Estimate: 20-40 min to build CLIs and run `rnx2rtkp` SPP on public CORS RINEX (assumes cmake + compiler present, `crx2rnx` found). Live F9P + NTRIP RTK: ~1-2 h including receiver config. |
| License | GitHub metadata: NOASSERTION. `license.txt` in repo is BSD 2-clause (T. Takasu). Commercial use permitted under that text. |

## Minimal usage
Adapted from `rnx2rtkp -?` help text and the repo's own [gnss-rinex-processing sample](../../samples/gnss-rinex-processing/README.md):

```bash
# single point (code only), ECEF output
rnx2rtkp -p 0 -sys G -m 15 -e -ts 2024/04/09 12:00:00 -te 2024/04/09 14:00:00 \
  -o spp.pos rover.24d.gz brdc1000.24n.gz
# kinematic RTK against a base with known ECEF coordinate, L1+L2
rnx2rtkp -k data/config/f9p_ppk.conf -p 2 -f 2 -sys G -r X Y Z \
  -o rtk.pos rover.obs base.obs nav.nav
# live: pull NTRIP corrections and push them out a serial port to a receiver
str2str -in ntrip://user:pass@caster:2101/MOUNT -out serial://ttyACM0:115200
```

Order matters for `rnx2rtkp`: first OBS = rover, second OBS = base, then NAV/SP3/CLK.

## Wiring it into a nav stack
- Receiver side: log UBX with [pygnssutils](./semuconsulting__pygnssutils.md) `gnssstreamer` or u-center, convert with `convbin`, post-process with `rnx2rtkp`. Configure the F9P with [pyubx2](./semuconsulting__pyubx2.md).
- Truth for experiments: RTK/PPK `.pos` (Q=1 epochs) is a cheap ground-truth track to score VIO, terrain nav or a GNSS/INS filter during simulated outages ([KF-GINS](./i2nav-whu__kf-gins.md) consumes GNSS position text files of the same shape after a column remap).
- Python side: parse `.pos` with pandas (whitespace separated, `%` header lines). [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) gives you an editable WLS/FDE for the same RINEX.
- Live: `rtkrcv` can output NMEA over TCP, which an autopilot GPS driver or ROS `nmea_navsat_driver` can read. Most F9P setups instead let the receiver do RTK and use `str2str` only as the NTRIP client.
- Integrity / spoofing work: `-y 2` residual output gives per-satellite residuals to feed a RAIM or spoofing check.

## Gotchas
- **Mode numbers differ from upstream RTKLIB 2.4.x.** demo5 v2.5.1: `4:static-start, 5:moving-base, 6:fixed, 7:ppp-kinematic, 8:ppp-static, 9:ppp-fixed`. Upstream: `4:moving-base, 5:fixed, 6:ppp-kinematic`. Always read `rnx2rtkp -?` of the binary you built (confirmed from `app/consapp/rnx2rtkp/rnx2rtkp.c`).
- `crx2rnx` must be on PATH, and on Linux the README says rename `CRX2RNX` to lowercase `crx2rnx`. Without it, Hatanaka files fail silently-ish.
- Without `-r`/`-l` the base position is the average of single solutions: metres of error leak into the "RTK" result.
- RINEX header `APPROX POSITION XYZ` is not truth (the hub sample measured a 1.6 m offset on a CORS station).
- Open issues: #783 malloc error in `addobsdata` for high-rate RINEX 3 base files (2.5.0); #111 `rtkrcv` crashes on musl/uClibc (Alpine containers, some embedded images) - use a glibc base image.
- The README's benchmark percentages (PPC-Dataset 88.0%, UrbanNav Tokyo 75.7% overall) are the maintainer's, measured with the shipped `*_urban.conf` files; not reproduced here.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- **Ran** `rnx2rtkp` v2.5.1 (cmake build in Docker) on NOAA CORS P730 vs base P731, 2 h, 30 s, GPS only, scored against the NGS ITRF2020 coordinate: SPP E/N/U RMS 0.62 / 1.24 / 1.02 m, H95 2.07 m; RTK fix 97 %, H95 4.5 cm (the 8 float epochs are the first 4 min) - [gnss-rinex-processing](../../samples/gnss-rinex-processing/README.md).
- `-r x y z` for the base was used; mode numbers confirmed with `rnx2rtkp -?` of that build (`2` = kinematic). Missing `crx2rnx` shows up as a decompression error on `.d` input, not a clear message. `-ts`/`-te` take two arguments each - [gnss-rinex-processing](../../samples/gnss-rinex-processing/README.md).
- `rnx2rtkp` on GNSS-SDR 0.0.19 RINEX output reproduced GNSS-SDR's own PVT medians to 0.1 m (same RTKLIB core, so a plumbing check) - [gnss-signal-chain](../../samples/gnss-signal-chain/README.md).

## Alternatives
- [tomojitakasu/RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md) - upstream; use only if a tool depends on 2.4.x behaviour. demo5 is the better default for low-cost receivers.
- [rtklibexplorer/rtklib-py](../../catalog/repos/rtklibexplorer__rtklib-py.md) - Python port of the PPK core; prefer when you want to modify the filter in Python.
- [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) - code-only SPP/FDE in Python; no carrier-phase RTK, but readable and hackable.

Sources: https://github.com/rtklibexplorer/RTKLIB readme.txt, license.txt, `src/rtklib.h`, `app/consapp/rnx2rtkp/rnx2rtkp.c` help text, `data/config/` listing, issues #783 #111 (via gh search), releases (v2.5.1), samples/gnss-rinex-processing/README.md in this repo.
