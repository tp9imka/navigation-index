# MagNav.jl - integration card
<!-- about: repo:mit-ai-accelerator/magnav.jl -->
One-line: the reference implementation of airborne magnetic anomaly navigation (Tolles-Lawson / NN aircraft compensation + map-matching EKF) with real SGL flight data and anomaly maps one function call away, so you can show a jam-proof position fix on real flights.

| | |
|---|---|
| Install | Julia REPL: `using Pkg; Pkg.add("MagNav")`. Or clone and `Pkg.activate("."); Pkg.instantiate()`. Docker (Julia + package + notebooks, JupyterLab on 8888): `docker pull ghcr.io/mit-ai-accelerator/magnav.jl && docker run -p 8888:8888 ghcr.io/mit-ai-accelerator/magnav.jl` (Docker Hub `jtaylormit/magnav` is "manually and sporadically updated"). Latest release v1.3.5 (2026-10-05). |
| Runs on | Julia >= 1.10 (`Project.toml` compat; README: tested on LTS and latest stable). CPU; no GPU requirement stated. NN compensation uses Flux 0.16. Linux/macOS/Windows wherever Julia and GDAL_jll build (see Gotchas). |
| Inputs | HDF5 / CSV / MAT flight files with `tt` [s], `lat` `lon` [deg], `alt` [m], `roll` `pitch` `yaw` [deg], scalar mag `mag_1_c` [nT]; INS fields; vector fluxgate for compensation. Maps: `map` [nT] on `xx` (lon, deg) x `yy` (lat, deg) grid at constant HAE `alt` [m] (field list from `examples/simple_magnav.jl`). |
| Outputs | `FILTout` (filtered lat/lon/alt, velocities, attitude, covariances), CRLB, position-error plots (`plot_filt`, `plot_filt_err`), Google Earth export (`src/google_earth.jl`), compensation coefficients / models (`save_comp_params`). |
| Key API / entry points | (confirmed in `src/`) `get_XYZ20(xyz_h5)`, `get_XYZ0(file)`, `get_XYZ(flight::Symbol, df_flight)`; `get_map(map_file)` / `get_map(map_name::Symbol, df_map)`; data artifacts `sgl_2020_train(f)`, `sgl_2021_train(f)`, `ottawa_area_maps(f)`, constants `emag2`, `emm720`, `namad`; `create_TL_coef(flux, B, ...)`, `create_TL_A(...)` (Tolles-Lawson); `comp_train(comp_params, xyz, ind)` (exported compensation entry; the NN trainers `nn_comp_1_train` / `nn_comp_2_train` in `src/compensation.jl` are not exported, call them as `MagNav.nn_comp_1_train`); `create_model(dt, lat1; ...) -> (P0, Qd, R)`; `map_interpolate(mapS)`; `run_filt(traj, ins, meas, itp_mapS, :ekf; ...)` (also `:mpf`); `crlb(traj, itp_mapS; ...)`; `plot_filt(traj, ins, filt_out)`. |
| Time to first result | Estimate: 1-2 h with the Docker image (pull + notebook run); 2-4 h native (Julia install, first-run precompile of a large dependency tree, artifact downloads). `examples/simple_magnav.jl` on bundled small data should report about 7 m navigation error (its docstring says so; not run here). |
| License | Code: GitHub NOASSERTION. `LICENSE.md` says the work was created by the Department of the Air Force under 17 U.S.C. 105 and is public domain, followed by MIT-style permission text. Data: separate and restrictive, see Gotchas. |

## Minimal usage
Adapted from `examples/simple_magnav.jl` (bundled data, no download). Not run.

```julia
using Pkg; Pkg.add("MagNav")
using MagNav, Random
cd(joinpath(pkgdir(MagNav), "examples")); Random.seed!(33)
xyz  = get_XYZ0("simple_magnav_data/xyz.h5")
mapS = get_map("simple_magnav_data/map.h5")
(P0, Qd, R) = create_model(xyz.traj.dt, xyz.traj.lat[1]; init_pos_sigma=3.0, meas_var=3.0^2)
(_, _, filt_out) = run_filt(xyz.traj, xyz.ins, xyz.mag_1_c, map_interpolate(mapS), :ekf;
                            P0=P0, Qd=Qd, R=R, core=false)
plot_filt(xyz.traj, xyz.ins, filt_out; show_plot=false)
```

Real flight (pattern from `examples/pluto_sgl.jl`, which builds `df_flight` / `df_map` in `examples/dataframes_setup.jl`): `xyz = get_XYZ(:Flt1006, df_flight)`, `mapS = get_map(:Eastern_395, df_map)`. Full walk-through with Tolles-Lawson and CRLB: [samples/magnav-quickstart](../../samples/magnav-quickstart) (also unverified).

## Data (AFRL / SGL challenge flights)
- Source: Zenodo DOI 10.5281/zenodo.4271803, "DAF-MIT AIA Open Flight Data for Magnetic Navigation Research", v3 (2023-07). The package fetches the same flights as lazy Julia artifacts (`sgl_2020_train`, `sgl_2021_train`) from Dropbox URLs in `Artifacts.toml`.
- Size (Zenodo API file list, 2026-11-06): 16 HDF5 flights totalling about 1.15 GB uncompressed; 2020 set (Flt1002-1007) about 573 MB, largest file Flt1002 at 153 MB. Artifact tarball sizes are not stated.
- Non-lazy artifacts (`EMM720_World`, `NAMAD_305`, `sgl_fields`, `util_files`) download on first `using MagNav`; `EMAG2`, Ottawa maps and flight sets download on first use. Collected 2020-06-20 to 2020-07-07 near Ottawa by Sander Geophysics Ltd. in a Cessna Grand Caravan (`sgl_2020_train` docstring).
- Licence: Zenodo licence id `other-at`. The Data Sharing Agreement (`readmes/DATA_SHARING_AGREEMENT.md`) grants a "limited personal, non-exclusive, non-transferable ... revocable" licence "solely for the purpose of non-profit research, non-profit education, or for government purposes by or on behalf of the U.S. Government". It runs for one year from approval, the Air Force can revoke access, and you must "expunge any and all copies" when the purpose ends. Citation of FA8750-19-2-1000 required.
- Index pages: [AFRL MagNav challenge 2020](../../catalog/resources/afrl-magnav-challenge-2020.md), [Zenodo dataset](../../catalog/resources/magnav-zenodo-dataset.md), [SGL flight data](../../catalog/resources/magnav-sgs-flight-data.md).

## Wiring it into a nav stack
- It is a batch Julia toolbox, not a ROS node. For a live demo, pre-compute on recorded data, or step the callable `EKF_RT` struct (`src/ekf_&_crlb.jl`; per-step use inferred from its signature, not tested) from a Julia process fed over a socket. `ekf_online` (`src/ekf_online.jl`) is different: an EKF that also estimates Tolles-Lawson coefficients in-filter (`run_filt(traj, ins, meas, itp_mapS, :ekf_online; ...)`). Export the position as CSV and score it with [evo](./michaelgrupp__evo.md) after converting to local ENU.
- Your own hardware: a scalar magnetometer + vector fluxgate + INS log in the CSV/HDF5 field layout above, plus a survey map ([NAMAD/EMAG2](../../catalog/concepts/magnetic-nav.md) at coarse resolution only). Compensation needs a calibration box flight pattern.
- Fuse its fix as an absolute position aid into a GNSS-denied INS (see [gnss-ins-ekf-outage sample](../../samples/gnss-ins-ekf-outage)).

## Gotchas
- **Data licence is the trap**: non-profit research, education or US-government purposes only, one-year term, revocable, delete-after-use. A hackathon by or for a company may not qualify; read the agreement before redistributing data or derived maps in a repo.
- The project "has concluded. Only minimal changes will be made moving forward" (README).
- Artifact hash mismatch on download is a known issue; README says rename the folder in `~/.julia/artifacts` to the `git-tree-sha1` in `Artifacts.toml`. Users fetched other Ottawa maps by hand from the Dropbox URLs there (issue #313).
- Precompile failures on Windows with Julia 1.11.3 in `GDAL_jll` / `ArchGDAL` (issue #271); a DataFrames vs older-BSON segfault was fixed upstream (issue #161). Use the Docker image if Julia setup fights you.
- Ottawa maps are k-NN filled where data is missing; use `map_check` so you do not "navigate" on synthetic map cells (`ottawa_area_maps` docstring).
- Anomaly-map navigation needs map coverage of the flight area; global models (EMAG2, EMM720) are much coarser than survey maps, so accuracy numbers from the SGL flights do not transfer.

## Alternatives
- [magnav.py](../../catalog/repos/manasp21__magnav.py.md) - Python port; prefer it if the team will not touch Julia (check its parity first).
- [MAMMAL](../../catalog/repos/powerbroker2__mammal.md) - Python magnetic-navigation toolkit; alternative stack for map and filter work.
- [AFIT example data](../../catalog/repos/afit-eeng-magnav__example-data.md) - extra data to pair with any of the above.

Sources: README.md, LICENSE.md, Artifacts.toml, Project.toml, src/MagNav.jl, src/{get_XYZ,get_map,ekf_&_crlb,tolles_lawson,compensation,eval_filt,map_functions,model_functions}.jl (function lists), examples/simple_magnav.jl, examples/pluto_sgl.jl, readmes/DATA_SHARING_AGREEMENT.md, Zenodo API record 4271803, issues #161, #271, #313 (read 2026-11-06).
