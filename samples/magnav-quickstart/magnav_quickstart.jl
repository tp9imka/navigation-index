# MagNav quickstart: SGL 2020 challenge flight -> Tolles-Lawson -> EKF vs anomaly map.
#
# Ran with Julia 1.11.9 and MagNav.jl v1.3.5 in the julia:1.11 Docker image (see README).
# Follows MagNav.jl examples/pluto_sgl.jl.
#
# Usage (needs examples/dataframes/*.csv from a MagNav.jl clone):
#   julia --project=. magnav_quickstart.jl /path/to/MagNav.jl/examples

using MagNav
using CSV, DataFrames
using Random: seed!
using Statistics: mean, std

const FLIGHT       = :Flt1006
const MAP_NAME     = :Eastern_395
const TL_CAL_ROW   = 6       # df_cal row: first calibration box of line 1006.04
const RIDGE_LAMBDA = 0.025   # Tolles-Lawson ridge regression parameter
const MEAS_VAR_NT2 = 5.0^2   # magnetometer measurement noise variance [nT^2]
const FOGM_SIGMA   = 3.0     # first-order Gauss-Markov catch-all bias [nT]
const FOGM_TAU_S   = 180.0
const REPORT_EVERY_S = 60.0

examples_dir = isempty(ARGS) ? error("pass the MagNav.jl/examples directory") : abspath(ARGS[1])
seed!(33)

# Only the line/calibration tables are needed from examples/dataframes. Loading the
# flight and map by path (instead of dataframes_setup.jl) avoids pulling the 2021 data.
read_df(name) = DataFrame(CSV.File(joinpath(examples_dir, "dataframes", name)))
df_cal = read_df("df_cal.csv")
df_nav = read_df("df_nav.csv")
df_nav.flight   = Symbol.(df_nav.flight)
df_nav.map_name = Symbol.(df_nav.map_name)

xyz  = get_XYZ20(MagNav.sgl_2020_train(FLIGHT))     # downloads the sgl_2020_train artifact once
mapS = get_map(MagNav.ottawa_area_maps(MAP_NAME))   # downloads the ottawa_area_maps artifact once
lines = df_nav[(df_nav.flight .== FLIGHT) .& (df_nav.map_name .== MAP_NAME), :]
line = lines.line[1]
ind = get_ind(xyz, line, df_nav)
TL_ind = get_ind(xyz; tt_lim = [df_cal.t_start[TL_CAL_ROW], df_cal.t_end[TL_CAL_ROW]])
println("flight $FLIGHT, line $line, map $MAP_NAME, $(sum(ind)) samples")

# Tolles-Lawson: fit platform-field coefficients on the calibration box (pitch/roll/yaw
# manoeuvres), then subtract the predicted platform field on the navigation line.
flux = xyz.flux_d
TL_coef = create_TL_coef(flux, xyz.mag_1_uc, TL_ind; λ = RIDGE_LAMBDA)
A = create_TL_A(flux, ind)
mag_1_uc = xyz.mag_1_uc[ind]
mag_1_c = mag_1_uc - detrend(A * TL_coef; mean_only = true)

traj = get_traj(xyz, ind)
ins = get_ins(xyz, ind; N_zero_ll = 1)
(map_val, itp_mapS) = get_map_val(mapS, traj; return_itp = true)
map_val += (xyz.diurnal + xyz.igrf)[ind]  # map holds anomaly only; add core (IGRF) + diurnal

println("map - mag std [nT]: uncompensated $(round(std(map_val - mag_1_uc), digits=2)), " *
        "Tolles-Lawson $(round(std(map_val - mag_1_c), digits=2)), " *
        "SGL-compensated $(round(std(map_val - xyz.mag_1_c[ind]), digits=2))")

(P0, Qd, R) = create_model(traj.dt, traj.lat[1];
                           init_pos_sigma = 0.1,
                           init_alt_sigma = 1.0,
                           init_vel_sigma = 1.0,
                           meas_var       = MEAS_VAR_NT2,
                           fogm_sigma     = FOGM_SIGMA,
                           fogm_tau       = FOGM_TAU_S)

(crlb_out, ins_out, filt_out) = run_filt(traj, ins, mag_1_c, itp_mapS, :ekf;
                                         P0, Qd, R, core = true)

drms(n, e) = sqrt.(n .^ 2 .+ e .^ 2)
ins_err  = drms(ins_out.n_err, ins_out.e_err)
filt_err = drms(filt_out.n_err, filt_out.e_err)
crlb_std = drms(crlb_out.n_std, crlb_out.e_std)

println(rpad("t [min]", 9), rpad("INS err [m]", 13), rpad("MagNav EKF err [m]", 20), "CRLB [m]")
step = max(1, round(Int, REPORT_EVERY_S / traj.dt))
for i in 1:step:traj.N
    t_min = (traj.tt[i] - traj.tt[1]) / 60
    println(rpad(round(t_min, digits=1), 9), rpad(round(ins_err[i], digits=1), 13),
            rpad(round(filt_err[i], digits=1), 20), round(crlb_std[i], digits=1))
end
println("EKF DRMS over line: $(round(sqrt(mean(filt_err .^ 2)), digits=1)) m; " *
        "INS final error: $(round(ins_err[end], digits=1)) m")
