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

`magnav_quickstart.jl` is an **unverified sketch**: Julia was not installed where it was
written, so it has never been run. Function names and arguments were checked on
2026-11-06 against MagNav.jl v1.3.5 (`Project.toml`), `examples/pluto_sgl.jl`,
`examples/simple_magnav.jl`, the `export` list in `src/MagNav.jl`, and the signatures of
`get_ind`, `create_TL_coef`, `create_TL_A`, `get_XYZ20`, `get_map`, `run_filt` in `src/`.
No output is shown below because none was observed.

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

- Julia LTS (1.10) or current stable, from https://julialang.org/downloads/ (juliaup).
- Disk and network for the artifacts. `sgl_2020_train` and `ottawa_area_maps` download
  on first use; sizes and URLs are in the package's `Artifacts.toml` (the full dataset is
  also on Zenodo, doi 10.5281/zenodo.4271803).
- The data is under a USAF Data Sharing Agreement: non-profit research, education, or
  US government purposes only. Read `readmes/DATA_SHARING_AGREEMENT.md` before using it
  in a commercial hackathon entry.

## Run

```bash
git clone https://github.com/MIT-AI-Accelerator/MagNav.jl.git /tmp/MagNav.jl   # for examples/dataframes/*.csv
cd samples/magnav-quickstart
julia --project=. -e 'using Pkg; Pkg.add(["MagNav", "CSV", "DataFrames"])'
julia --project=. magnav_quickstart.jl /tmp/MagNav.jl/examples
```

Alternative without a local Julia install: the package's Docker image
(`ghcr.io/mit-ai-accelerator/magnav.jl`, JupyterLab on port 8888) ships Julia, MagNav.jl and
the example notebooks; `examples/pluto_sgl.jl` covers the same flow interactively.

## What the script does

| Step | Call | Notes |
|---|---|---|
| Load flight | `get_XYZ20(MagNav.sgl_2020_train(:Flt1006))` | `XYZ20` struct with GPS truth, INS, 5 scalar mags, fluxgates |
| Select line | `get_ind(xyz, line, df_nav)` | first `df_nav` row for Flt1006 on `:Eastern_395` (line 1006.08 in the CSV) |
| Calibration box | `get_ind(xyz; tt_lim = [t_start, t_end])` | `df_cal` row 6 = first box of line 1006.04 |
| Tolles-Lawson | `create_TL_coef(flux, xyz.mag_1_uc, TL_ind; λ = 0.025)`, `create_TL_A(flux, ind)` | ridge fit on the box, applied to the line |
| Map | `get_map(MagNav.ottawa_area_maps(:Eastern_395))`, `get_map_val(mapS, traj; return_itp = true)` | anomaly map + interpolant; IGRF and diurnal added back |
| Filter | `create_model(...)`, `run_filt(traj, ins, mag_1_c, itp_mapS, :ekf; P0, Qd, R, core = true)` | returns `(crlb_out, ins_out, filt_out)` |

## Expected output shape (not observed)

```
flight Flt1006, line 1006.08, map Eastern_395, <N> samples
map - mag std [nT]: uncompensated <x>, Tolles-Lawson <y>
t [min]  INS err [m]  MagNav EKF err [m]  CRLB [m]
0.0      ...
...
EKF DRMS over line: <z> m; INS final error: <w> m
```

What should hold if it works: the Tolles-Lawson std is well below the uncompensated std;
INS error grows over the line while the EKF error stays bounded and near the CRLB. If
EKF error sits far above the CRLB, raise `MEAS_VAR_NT2` (compensation worse than assumed).
For reference, the package's own `simple_magnav.jl` says its bundled example should show
about 7 m navigation error; that is a different dataset and setup.

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
- `ins` from `get_ins(xyz, ind; N_zero_ll = 1)` is re-zeroed to GPS at the first sample
  of the line, so INS error starts at 0. That is a best case for the initial fix.
- `core = true` makes the filter include the core (IGRF) field in its predicted
  measurement, which matches a total-field magnetometer like `mag_1_c`. If you feed an
  anomaly-only signal (core already removed), set `core = false`. Diurnal variation is
  not modelled by the filter and ends up in the FOGM bias state.
- The package's project has concluded and is in maintenance mode (per its README); pin
  the version (`Pkg.add(name = "MagNav", version = "1.3.5")`) for reproducibility.
