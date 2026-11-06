# Public RINEX => SPP vs RTK with RTKLIB demo5 and gnss_lib_py

## Goal

Take two days-old public CORS RINEX files, compute positions three ways and score each
against the station's published coordinate:

1. **SPP** (single point, code only) with RTKLIB `rnx2rtkp -p 0` - metre level.
2. **RTK** (kinematic, carrier phase, base 30 km away) with `rnx2rtkp -p 2` - cm to dm level.
3. **SPP in Python** with gnss_lib_py weighted least squares - to own the algorithm and
   change it (FDE, weighting, spoofing checks).

Because a CORS antenna never moves, every metre of error is solution error. That makes
this a baseline harness for any later experiment (degraded geometry, injected faults, a
new spoofing check).

## Repos used and why

| Repo | Role |
|---|---|
| [rtklibexplorer/RTKLIB](https://github.com/rtklibexplorer/RTKLIB) (demo5 / RTKLIB-EX, release v2.5.1) | `rnx2rtkp` post-processing engine, `convbin` for RINEX 2 => 3 |
| [tomojitakasu/RTKLIB](https://github.com/tomojitakasu/RTKLIB) | upstream; the manual's option reference. Note `-p` mode numbers differ (see Pitfalls) |
| [Stanford-NavLab/gnss_lib_py](https://github.com/Stanford-NavLab/gnss_lib_py) (v1.1.0) | `RinexObs`, `add_sv_states_rinex`, `solve_wls` in `glp_spp.py` |
| [geospace-code/georinex](https://github.com/geospace-code/georinex) | RINEX reader under gnss_lib_py; `rinexheader()` gives the header approx position |

## Data (public, no login)

NOAA NGS CORS, 2024-04-09 (day 100), 30 s, RINEX 2.11 Hatanaka-compressed, GPS+GLO+GAL:

| Role | Station | Files |
|---|---|---|
| rover | P730 (Ballard Ridge, CA) | `rinex/2024/100/p730/p7301000.24d.gz`, `coord/coord_20/p730_20.coord.txt` |
| base | P731 (Lil Juniper, CA), 29.9 km from P730 | `rinex/2024/100/p731/p7311000.24d.gz`, `coord/coord_20/p731_20.coord.txt` |
| nav | GPS broadcast | `rinex/2024/100/brdc1000.24n.gz` |

All under `https://geodesy.noaa.gov/corsdata/`. All five URLs answered HTTP 200 on
2026-11-06, and the P730 header was read (RINEX 2.11 MIXED, Septentrio POLARX5, 30 s).
Truth is the ITRF2020 ARP coordinate (epoch 2020.0) on the NGS sheet, moved to the
data epoch with the sheet's velocity (`--epoch 2024.27`, ~8 cm of plate motion).

## Prerequisites

- Python 3.10+ (stdlib) for `compare_pos.py` and its tests.
- Docker, for RTKLIB. `docker/Dockerfile` (debian bookworm-slim) clones rtklibexplorer
  RTKLIB `v2.5.1`, builds `rnx2rtkp` and `convbin` with CMake, and installs `crx2rnx` from
  the `hatanaka` 2.8.0 wheel. `run_in_docker.sh` builds the image on first use (~7 min
  here) and moves files with `docker cp`, so it works even when the sample path is not
  shared with the Docker VM (it was not, for `/private/tmp` on this machine). A native
  build should work with the same CMake lines but was not tried here:
  ```bash
  git clone --depth 1 --branch v2.5.1 https://github.com/rtklibexplorer/RTKLIB.git
  cmake -S RTKLIB -B RTKLIB/build -DCMAKE_BUILD_TYPE=Release
  cmake --build RTKLIB/build --target rnx2rtkp convbin -j     # binaries land in RTKLIB/bin
  ```
- For `glp_spp.py`: `python3 -m pip install -r requirements.txt` (gnss-lib-py 1.1.0,
  georinex 1.16.1) and internet once: glp downloads the day's broadcast nav file into
  `data/glp_ephem/`.

## Run

```bash
cd samples/gnss-rinex-processing
python3 -m unittest -v test_compare_pos.py      # stdlib
./fetch_data.sh                                  # ~3.6 MB into data/ (git-ignored), retries NGS 408s
./run_in_docker.sh                               # rnx2rtkp SPP + RTK, score table, and data/p730_r3.rnx for glp
python3 glp_spp.py data/p730_r3.rnx --truth data/p730_20.coord.txt --epoch 2024.27 \
    --start 2024-04-09T12:00:00 --minutes 120    # ~100 s, mostly RinexObs parsing the 24 h file
```

With RTKLIB and `crx2rnx` already on `PATH`, `./run_rtklib.sh` runs the same two
`rnx2rtkp` commands without Docker:

```bash
rnx2rtkp -k rtk.conf -p 0 -sys G -m 15 -e -ts 2024/04/09 12:00:00 -te 2024/04/09 14:00:00 \
  -o out/spp.pos data/p7301000.24d.gz data/brdc1000.24n.gz
rnx2rtkp -k rtk.conf -p 2 -f 2 -sys G -m 15 -e -r <P731 X Y Z> -ts 2024/04/09 12:00:00 -te 2024/04/09 14:00:00 \
  -o out/rtk.pos data/p7301000.24d.gz data/p7311000.24d.gz data/brdc1000.24n.gz
python3 compare_pos.py --truth data/p730_20.coord.txt --epoch 2024.27 out/spp.pos out/rtk.pos
```

Flags (confirmed with `rnx2rtkp -?` of the v2.5.1 build): `-k` options file, `-p` mode
(0 single, 2 kinematic), `-f` frequencies (2 = L1+L2), `-sys G` GPS only, `-m` elevation
mask in deg, `-e` ECEF x/y/z output, `-r x y z` base ECEF in m (without it RTKLIB averages
the base's single-point solutions, which biases RTK by metres), `-ts`/`-te` start/end as
`y/m/d h:m:s`, `-o` output file. The first OBS file is the rover, the second the base.
`rtk.conf` sets broadcast iono (`pos1-ionoopt=brdc`), Saastamoinen troposphere,
continuous AR. Command-line flags override it. Per-epoch progress goes to `out/*.log`.

Base coordinate printed by `compare_pos.py --print-xyz` from the P731 sheet:

```
-2432862.9296 -4134674.5894 4191141.5339
```

## Observed results (2026-11-06)

RTKLIB demo5 v2.5.1 (`% program : RTKLIB ver.EX 2.5.1` in the `.pos` header), Docker
build, P730 vs its NGS ITRF2020 coordinate propagated to 2024.27, 12:00-14:00 GPST, 30 s,
GPS only:

```
file                   epochs   E rms   N rms   U rms   H 95%  solution types
out/spp.pos               241   0.624   1.244   1.021   2.067  single 100%
out/rtk.pos               241   0.084   0.055   0.071   0.045  fix 97%, float 3%
```

The 8 float epochs are the first 4 minutes of the RTK run (`Q=2` before AR fixes); they
carry most of the RTK RMS, while H 95 % is 4.5 cm.

gnss_lib_py 1.1.0 `glp_spp.py` on the same rover, window and mask (GPS L1 C/A):

```
RINEX header APPROX POSITION XYZ: [-2457630.665, -4118098.427, 4193651.724]
pass 1 (SV states at receive time): 241 epochs  E/N/U rms = 30.69 / 19.58 / 24.67 m  H95 = 43.96 m
pass 2 (SV states at transmit time): 241 epochs  E/N/U rms = 3.22 / 4.26 / 18.96 m  H95 = 10.54 m
pass 3 (+15 deg mask, tropo, Klobuchar): 241 epochs  E/N/U rms = 0.65 / 1.28 / 1.10 m  H95 = 2.02 m
```

Pass 3 agrees with RTKLIB SPP to a few cm per axis. Getting there needed three fixes on
top of the plain glp calls; each one was found from the residuals, not guessed:

1. **Time tag.** glp 1.1.0 `RinexObs` treats RINEX epochs (GPS time) as UTC and adds the
   18 leap seconds. Every SV is then propagated to the wrong second and the solution is
   km off (first attempt: 7.3 / 3.9 / 5.6 km RMS). Subtract the leap seconds.
2. **Ephemeris selection.** `add_sv_states_rinex` picks one ephemeris per SV at the
   *earliest* epoch of its input and uses it for the whole input; per-SV residuals then
   drift linearly to ~25 m over 2 h. Calling it per 15-minute chunk fixes that.
3. **Transmit time and atmosphere.** Without receiver-position rows, SV states are at the
   receive time (pass 1). Feeding the pass-1 fix back gives transmit-time states (pass 2).
   Pass 3 adds the 15 deg mask and glp's `calculate_pseudorange_corr` (tropo + Klobuchar
   with alpha/beta from the nav header). `solve_wls` already applies the Earth-rotation
   correction, so it must not be added again (doing so doubled the east error).

## Test output (observed, python3.14.7, 2026-11-06)

```
test_geodetic_matches_sheet ... ok
test_parses_itrf_block_not_nad83 ... ok
test_scores_synthetic_pos_file ... ok
test_velocity_propagation ... ok
----------------------------------------------------------------------
Ran 4 tests in 0.003s

OK
```

`test_geodetic_matches_sheet` checks that the ECEF => lat/lon/h conversion reproduces the
NGS sheet's own geodetic values for P731 to 1e-7 deg and 1 cm. The `.pos` parser is tested
on a synthetic file in the `-e` layout, not on real RTKLIB output.

## Extend it in a hackathon

1. Fault injection: drop satellites below 30 deg, or add a ramp to one SV's pseudorange in
   the RINEX, and watch SPP vs RTK and RTKLIB's residual output (`-y 2`).
2. Swap the rover for Google Smartphone Decimeter Challenge data via
   `glp.AndroidRawGnss` and compare phone SPP with the CORS numbers.
3. Add RAIM/FDE: gnss_lib_py `solve_fde(navdata, method="residual")` (in `algorithms/fde.py`) does fault detection and exclusion
   ahead of `solve_wls`.
4. PPP: `-p 7` with IGS precise orbits/clocks (SP3/CLK) gives dm-level positions with no base.
5. Run `-p 2` on the base against itself shifted by a known offset to check the pipeline
   end to end.

## Pitfalls

- **Mode numbers differ between forks.** demo5 v2.5.1: `4:static-start, 5:moving-base,
  6:fixed, 7:ppp-kinematic`. Upstream RTKLIB 2.4.x: `4:moving-base, 5:fixed,
  6:ppp-kinematic`. Always check `rnx2rtkp -?` of the binary you built.
- The RINEX header `APPROX POSITION XYZ` is not truth. For P730 it is 1.6 m east of the
  NGS coordinate (computed from the downloaded header and sheet). Use the sheet.
- NGS coordinates are the antenna reference point. Without antenna phase-centre models
  (`-k` with `file-rcvantfile` + ANTEX) RTK results can sit a few cm off in height.
- `-ts`/`-te` take two arguments each (`2024/04/09 12:00:00`); do not quote them as one.
- If `crx2rnx` is missing, `rnx2rtkp` fails on `.d` input with a decompression error, not
  a clear message.
- The `brdc*.24n` file is GPS only. With `-sys G,R,E` you also need a mixed nav file
  (e.g. `BRDC00IGS_R_*_MN.rnx` from an IGS data centre).
- `out/*.pos` with `-e` has 2 time tokens then `x y z Q ns`; adding `-t` keeps 2 tokens,
  but `-a` (ENU) or the default lat/lon layout breaks `compare_pos.py`.

## Files

- `fetch_data.sh` - downloads the 5 public files into `data/` (git-ignored).
- `run_rtklib.sh`, `rtk.conf` - the two `rnx2rtkp` runs and scoring.
- `docker/Dockerfile`, `run_in_docker.sh` - RTKLIB demo5 v2.5.1 + crx2rnx image, and the
  wrapper that runs `run_rtklib.sh` plus the RINEX 2 => 3.04 conversion inside it.
- `requirements.txt` - pinned gnss-lib-py / georinex for `glp_spp.py`.
- `compare_pos.py` - stdlib: NGS sheet parser, plate-motion propagation, ECEF => ENU error stats per solution type.
- `test_compare_pos.py` - unit tests for it.
- `glp_spp.py` - gnss_lib_py WLS SPP, three passes, with the fixes above.
