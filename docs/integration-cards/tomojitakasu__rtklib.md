# RTKLIB (upstream, T. Takasu) - integration card
<!-- about: repo:tomojitakasu/rtklib -->
The original RTKLIB: ANSI C library plus CLIs (`rnx2rtkp`, `rtkrcv`, `str2str`, `convbin`, `pos2kml`) for SPP / DGNSS / RTK / PPP from RINEX, receiver binaries and RTCM/NTRIP streams. Frozen upstream; in a hackathon you most likely want it as the Debian/Ubuntu `rtklib` package or as the reference behind the maintained [demo5 / RTKLIB-EX fork](./rtklibexplorer__rtklib.md).

| | |
|---|---|
| Install | Fastest: `sudo apt install rtklib` (Debian bookworm/trixie and Ubuntu 24.04 ship `2.4.3.b34+dfsg`; binary packages `rtklib`, `rtklib-qt`, `librtklib-dev`, `librtklib1`, `rtklib-doc`, per Debian `debian/control` and Launchpad). Source: two branches, no GitHub releases. `master` = 2.4.2 p13 (last commit 2018-01-30); `rtklib_2.4.3` = 2.4.3 b34 (2020-12-29). Build CLIs from source: `git clone -b rtklib_2.4.3 https://github.com/tomojitakasu/RTKLIB.git && cd RTKLIB && make -C lib/iers/gcc && make -C app/consapp` (consapp `makefile` loops over `pos2kml str2str rnx2rtkp convbin rtkrcv`, each `gcc/makefile`). Windows GUI binaries are committed in `bin/`. |
| Runs on | Any POSIX with gcc (pthread, sockets) or Windows. Plain C89, no GPU. GUIs are Embarcadero VCL (Windows) or the Qt port merged in 2.4.3 b15. |
| Inputs | RINEX 2.10-3.02 OBS/NAV, SP3-c, clock RINEX, ANTEX, IONEX, SBAS logs; RTCM 2.3 / 3.x; receiver raw formats (NovAtel, Hemisphere, u-blox, SkyTraq, JAVAD, Furuno, NVS, more in 2.4.3); streams from serial, TCP, NTRIP, files (readme.txt). |
| Outputs | `.pos` solutions (lat/lon/h, ECEF with `-e`, ENU baseline with `-a`), NMEA GGA (`-n`), solution status / residuals (`-y 1|2`), KML/GPX via `pos2kml`, relayed or converted streams via `str2str`, RINEX via `convbin`. |
| Key API / entry points | `rnx2rtkp [-k conf] [-o out] [-p mode 0..7] [-sys G,R,E,J,C,I] [-f 1..3] [-m elmask] [-r x y z | -l lat lon h] [-y level] rover.obs [base.obs] nav...` (help text in `app/consapp/rnx2rtkp/rnx2rtkp.c`; mode 0 single, 1 dgps, 2 kinematic default, 3 static, 4 moving-base, 5 fixed, 6 ppp-kinematic, 7 ppp-static). `rtkrcv` (real-time, console), `str2str -in ... -out ...`, `convbin`. Library (`src/rtklib.h`): `postpos()`, `rtkinit()`, `rtkpos()`, `pntpos()`, `readrnx()`, `input_rtcm3()`, `rtksvrstart()`. Example options: `app/consapp/rnx2rtkp/gcc/opts1.conf`..`opts4.conf`. |
| Time to first result | Estimate: 5 min via apt; 20-30 min from source (needs gcc and gfortran for `lib/iers`). Then minutes to an SPP solution on public RINEX. |
| License | No LICENSE file; `readme.txt` states BSD 2-clause plus a clause on bundled Windows companion binaries (versions up to 2.4.1 were GPLv3). GitHub metadata shows no licence. |

## Minimal usage
Not run. Options from the `rnx2rtkp` help text.

```sh
sudo apt install rtklib
# SPP, GPS+Galileo, ECEF output
rnx2rtkp -p 0 -sys G,E -e -o spp.pos rover.obs brdc.nav
# post-processed kinematic RTK against a base, fix-and-hold, solution status for analysis
rnx2rtkp -p 2 -h -y 1 -o rtk.pos rover.obs base.obs brdc.nav
# NTRIP corrections => serial port of the receiver
str2str -in ntrip://user:pass@caster:2101/MOUNT -out serial://ttyACM0:115200
```

## Wiring it into a nav stack
- Receiver logs: u-blox UBX via `convbin` or parse with [pyubx2](./semuconsulting__pyubx2.md) / [pygnssutils](./semuconsulting__pygnssutils.md) first.
- Live RTK fix into ROS / autopilot: `rtkrcv` NMEA out => `nmea_navsat_driver` => [robot_localization](./cra-ros-pkg__robot_localization.md), or `str2str` feeding RTCM into the receiver and letting the autopilot read the receiver directly.
- Integrity / spoofing research: `-y 2` residuals are the raw material for RAIM-style checks; Python ports in [rtklib-py](../../catalog/repos/rtklibexplorer__rtklib-py.md) are easier to modify.
- Evaluate `.pos` against truth with [evo](./michaelgrupp__evo.md) after converting to TUM format.

## Gotchas
- Frozen: no commits on either branch since 2020 and no releases. Open issue #805 asks to backport Galileo PRN 31-36 (`MAXPRNGAL`) to `master`. Prefer demo5 / RTKLIB-EX for current receivers (F9P, newer signals) and fixes.
- Security: open issues #799 (out-of-bounds write in `decode_type1033` via unbounded RTCM3 descriptor lengths) and #803 (memory-safety report in the NTRIP client). Do not feed untrusted RTCM from the network to an exposed `rtkrcv`/`str2str`.
- `rnx2rtkp` 2.4.3 gcc makefile links `lib/iers/gcc/iers.a` with `-lgfortran`: build `lib/iers/gcc` first, or it fails at link time.
- Open #800: `convbin` reports "Duplicated satellite in one epoch" on u-blox RXM-RAWX.
- `master` vs `rtklib_2.4.3`: the default branch is the older 2.4.2; clone `-b rtklib_2.4.3`.

## Alternatives
- [RTKLIB demo5 / RTKLIB-EX](./rtklibexplorer__rtklib.md) - maintained fork, CMake build, low-cost receiver configs. First choice.
- [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) or [laika](./commaai__laika.md) - Python, easier to hack for research and ML pipelines.
- [GNSS-SDR](./gnss-sdr__gnss-sdr.md) - when you start from IQ samples rather than observables.

Sources: `readme.txt` (master and `rtklib_2.4.3`), branch list and head commits, `app/consapp/makefile`, `app/consapp/rnx2rtkp/rnx2rtkp.c` (help text), `app/consapp/rnx2rtkp/gcc/makefile`, `lib/iers/gcc/makefile`, `app/consapp/str2str/gcc/makefile`, issues #799 #800 #803 #805 (github.com/tomojitakasu/RTKLIB); sources.debian.org API and `debian/control` for `rtklib` 2.4.3.b34+dfsg-1; Launchpad published sources for Ubuntu noble.
