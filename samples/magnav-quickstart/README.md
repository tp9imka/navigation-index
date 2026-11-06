# MagNav quickstart (MagNav.jl)

## Goal

Run airborne magnetic anomaly navigation end to end on real flight data with
`repo:mit-ai-accelerator/magnav.jl`:

1. Download the public SGL 2020 challenge flight (Flt1006) and the Ottawa-area anomaly
   maps (both are Julia artifacts fetched by the package).
2. Fit Tolles-Lawson coefficients on a calibration box and compensate the scalar
   magnetometer for the aircraft's own field.
3. Run the MagNav EKF (INS + scalar magnetometer + anomaly map) on a navigation line and
   compare its position error with INS-only drift and the Cramer-Rao lower bound.

## Status

Ran on 2026-11-06 in the official `julia:1.11` Docker image (Julia 1.11.9, linux/arm64 on
Apple Silicon) with MagNav.jl v1.3.5, CSV v1.3.0, DataFrames v1.8.2. One dependency pin
was needed (FFTA, see Pitfalls). Output below is copied from the run.

## Why MagNav is jam-proof, and where it stops working

**Why it resists jamming and spoofing.** The aircraft measures the Earth's crustal
magnetic anomaly field (a few to hundreds of nT on top of a ~50,000 nT core field) with
a passive scalar magnetometer and matches the measured sequence against a surveyed
anomaly map. There is no RF signal to receive, so RF jammers and GNSS spoofers have
nothing to act on. It emits nothing either. Faking the measurement would mean producing
a magnetic field of tens of nT that varies correctly with position at the aircraft's
location, which is not practical at stand-off range (a dipole field falls off with the
cube of distance). Against GNSS denial it is one of the few options that works over
water and at night, unlike vision.

**Limits.**

- **Map availability and quality.** You can only navigate where a good anomaly map
  exists. Global compilations (EMAG2, WDMAM) are coarse (kilometre-scale, often merged
  from old surveys); high-resolution aeromagnetic surveys exist for some countries and
  are often restricted. Map error goes straight into the measurement residual.
- **Altitude.** Anomalies attenuate and smooth with height above the sources (upward
  continuation). High altitude => a smooth field => weak position observability. The map
  must be upward-continued to flight altitude (`upward_fft` in MagNav.jl); continuing
  downward is unstable.
- **Aircraft noise.** The platform's own field (ferrous structure, induced and eddy
  currents, electrical loads, actuators) is often larger than the anomaly signal.
  Tolles-Lawson needs a calibration box flown with pitch/roll/yaw manoeuvres, and
  degrades for magnetometers inside the cabin (compare Mag 1 on the tail stinger with
  Mag 3-5 inside). This compensation problem is what the MagNav challenge was about.
- **Temporal variation.** Diurnal and space-weather variations (tens of nT, more in
  storms) must be removed with a base station or a model; the core field must come
  from IGRF for the flight date.
- **Magnetically flat regions.** Over sedimentary basins or deep ocean, gradients are
  small and the filter falls back towards INS drift. The CRLB column tells you when.
- **Rate.** Accuracy comes from flying across anomalies, so slow or hovering platforms
  get little information per second.

## Prerequisites

- Julia 1.10+ (ran with 1.11.9), or just Docker with the `julia:1.11` image.
- Disk: the Julia depot ended at 5.8 GB (4.1 GB artifacts, 1.3 GB precompile cache,
  276 MB packages). Data artifacts on disk: `sgl_2020_train` ~563 MB, `ottawa_area_maps`
  ~1.2 GB (Eastern_395.h5 alone is 275 MB), plus `EMAG2` ~0.5 GB that MagNav downloads
  during precompilation. Measured with `du`, not from the package docs.
- Memory: the first attempt was OOM-killed (exit 137) in a Docker VM with 7.7 GB shared
  by other containers. `--heap-size-hint=2500M` and `JULIA_NUM_THREADS=1` fixed it.
- Time on this machine: install + precompile took roughly 10 min across the two
  `Pkg.add` calls (not timed precisely); artifact download not timed separately; the
  script itself 43 s once everything was cached.
- The data is under a USAF Data Sharing Agreement: non-profit research, education, or
  US government purposes only. Read `readmes/DATA_SHARING_AGREEMENT.md` before using it
  in a commercial hackathon entry.

## Run (Docker, as verified)

The script needs `examples/dataframes/*.csv` from a MagNav.jl clone (19 MB).

```bash
git clone --depth 1 https://github.com/MIT-AI-Accelerator/MagNav.jl.git ~/MagNav.jl
docker run -d --name magnav -v magnav-depot:/root/.julia julia:1.11 sleep infinity
docker exec magnav mkdir -p /work /examples /sample
docker cp ~/MagNav.jl/examples/dataframes magnav:/examples/
docker cp samples/magnav-quickstart/magnav_quickstart.jl magnav:/sample/
docker exec magnav sh -c 'cd /work && julia --project=/work -e "using Pkg;
    Pkg.add([\"MagNav\", \"CSV\", \"DataFrames\"]);
    Pkg.add(name=\"FFTA\", version=\"0.2\")"'
docker exec magnav sh -c 'cd /work && JULIA_NUM_THREADS=1 julia --heap-size-hint=2500M \
    --project=/work /sample/magnav_quickstart.jl /examples'
```

These are the steps that ran, consolidated into one listing (the run used the same
container, `Pkg.add` calls and script invocation, issued over several commands). The
first `Pkg.add` prints a precompile failure for GlobalSensitivity; the FFTA pin in
the second `Pkg.add` re-resolves and precompiles cleanly. Bind mounts work too
(`-v "$PWD":/sample`) as long as the path is shared with Docker Desktop; `/tmp` on macOS
is not by default, which is why this uses `docker cp`.

Native Julia: same two `Pkg.add` calls in `julia --project=.`, then
`julia --project=. magnav_quickstart.jl ~/MagNav.jl/examples`. Not run natively here.

The package also publishes a Docker image (`ghcr.io/mit-ai-accelerator/magnav.jl`,
JupyterLab on port 8888) per its README; not tried here.

## What the script does

| Step | Call | Notes |
|---|---|---|
| Load flight | `get_XYZ20(MagNav.sgl_2020_train(:Flt1006))` | `XYZ20` struct with GPS truth, INS, 5 scalar mags, fluxgates |
| Select line | `get_ind(xyz, line, df_nav)` | first `df_nav` row for Flt1006 on `:Eastern_395` (line 1006.08 in the CSV) |
| Calibration box | `get_ind(xyz; tt_lim = [t_start, t_end])` | `df_cal` row 6 = first box of line 1006.04 |
| Tolles-Lawson | `create_TL_coef(flux, xyz.mag_1_uc, TL_ind; λ = 0.025)`, `create_TL_A(flux, ind)` | ridge fit on the box, applied to the line |
| Map | `get_map(MagNav.ottawa_area_maps(:Eastern_395))`, `get_map_val(mapS, traj; return_itp = true)` | anomaly map + interpolant; IGRF and diurnal added back |
| Filter | `create_model(...)`, `run_filt(traj, ins, mag_1_c, itp_mapS, :ekf; P0, Qd, R, core = true)` | returns `(crlb_out, ins_out, filt_out)` |

## Observed output (2026-11-06)

```
[ Info: reading in XYZ20 data: /root/.julia/artifacts/0e129dcdd8b6f8b14581407e3f57ead6c82b24c2/sgl_2020_train/Flt1006_train.h5
[ Info: radar field contains NaNs
  ... (topo, drape, mag_6_uc, ogs_mag, ogs_alt also contain NaNs)
[ Info: CRLB DRMS error = 13 m
[ Info: INS  DRMS error = 137 m
[ Info: FILT DRMS error = 31 m
flight Flt1006, line 1006.08, map Eastern_395, 8391 samples
map - mag std [nT]: uncompensated 4.63, Tolles-Lawson 5.84, SGL-compensated 5.65
t [min]  INS err [m]  MagNav EKF err [m]  CRLB [m]
0.0      0.0          0.0                 0.1
1.0      19.0         18.1                9.1
2.0      38.3         55.4                17.4
3.0      58.3         43.6                14.3
4.0      75.2         34.7                8.9
5.0      93.3         26.1                13.7
6.0      108.8        40.4                19.3
7.0      126.3        45.9                16.8
8.0      143.5        15.2                9.8
9.0      159.0        27.3                12.8
10.0     174.3        17.8                9.7
11.0     187.2        30.0                10.0
12.0     198.5        16.2                8.7
13.0     208.2        16.4                9.5
EKF DRMS over line: 31.2 m; INS final error: 218.8 m
```

Two runs gave identical numbers (`seed!(33)`).

How to read it:

- Over the 14 min line (8391 samples at 10 Hz), INS-only error grows to 219 m. The MagNav
  EKF stays between 15 and 55 m, DRMS 31 m, about 2.4x the CRLB DRMS of 13 m. That
  matches the package's own `run_filt` summary lines (`FILT DRMS error = 31 m`).
- On this line Tolles-Lawson did **not** lower the map residual: 4.63 nT uncompensated
  vs 5.84 nT with the ridge fit from calibration box 1006.04, and 5.65 nT with SGL's
  own compensation (`xyz.mag_1_c`). Mag 1 is on the tail stinger, far from the
  aircraft's own field, so there is little to remove; the std mostly reflects map error
  and the fit's own noise. The in-cabin magnetometers (`mag_3_uc`..`mag_5_uc`) are where
  compensation matters. This contradicts the expectation written in an earlier version
  of this README ("TL std well below uncompensated"); not investigated further.
- The filter still used the Tolles-Lawson signal (`mag_1_c`); swapping in `mag_1_uc`
  is a one-line change worth trying.

## Hackathon extensions

- Swap `mag_1_uc` for `mag_4_uc` or `mag_5_uc` (in-cabin sensors) and watch compensation
  and navigation degrade; that gap is the realistic installation problem.
- Try `run_filt(...; :mpf)` (marginalized particle filter) and compare with `:ekf` on
  the same line.
- Neural compensation: `comp_train` / `comp_test` with the `NNCompParams` models
  (see `examples/pluto_model3.jl`), or the deep-learning notebooks in `repo:naatyu/magnav`.
- Bring your own data: `examples/simple_magnav.jl` loads a CSV/HDF5/MAT trajectory and map
  (`get_XYZ0`, `get_map`) - the documented path for non-SGL flights.
- Python teams: `repo:manasp21/magnav.py` is a port; `repo:afit-eeng-magnav/example-data`
  has extra maps and a challenge flight; `repo:ajisrawi/dronemagnav` is an open drone
  MagNav board design.

## Pitfalls

- Artifact hash mismatch on download: the MagNav.jl README says to rename the folder in
  `~/.julia/artifacts` to the `git-tree-sha1` from `Artifacts.toml`.
- First run is slow (package precompilation plus artifact downloads); do it before the
  hackathon clock starts.
- **FFTA 0.3.x breaks precompilation** (seen 2026-11-06 with a fresh resolve):
  `MethodError: plan_rfft(::Matrix{Float64}, ::Int64) is ambiguous` between FFTA 0.3.2
  and FFTW, raised while precompiling GlobalSensitivity (pulled in through
  KernelDensity => FFTA), so `using MagNav` fails. `Pkg.add(name="FFTA", version="0.2")`
  (resolved to 0.2.1) fixed it.
- Out-of-memory kill (exit 137, just `Killed`) in Docker: give Julia a heap hint
  (`--heap-size-hint=2500M`) or raise the Docker VM memory.
- `ins` from `get_ins(xyz, ind; N_zero_ll = 1)` is re-zeroed to GPS at the first sample
  of the line, so INS error starts at 0. That is a best case for the initial fix.
- `core = true` makes the filter include the core (IGRF) field in its predicted
  measurement, which matches a total-field magnetometer like `mag_1_c`. If you feed an
  anomaly-only signal (core already removed), set `core = false`. Diurnal variation is
  not modelled by the filter and ends up in the FOGM bias state.
- The package's project has concluded and is in maintenance mode (per its README); pin
  the version (`Pkg.add(name = "MagNav", version = "1.3.5")`) for reproducibility.
