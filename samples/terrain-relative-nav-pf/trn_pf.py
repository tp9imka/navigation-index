"""Terrain-relative navigation (TERCOM/TRN idea) with a particle filter.

A simulated aircraft flies over a DEM with a drifting INS (velocity bias) and a
noisy radar altimeter. Measured terrain height = baro altitude - radar AGL. The
particle filter keeps hypotheses of (position, INS velocity bias) and weights
them by how well the DEM height under each hypothesis matches the measurement.
"""

import argparse
import math
import random

from terrain import synthetic_dem

DEM_ROWS = DEM_COLS = 300
DEM_SPACING_M = 50.0

DT_S = 1.0
SPEED_MPS = 60.0
BASE_HEADING_DEG = 45.0
WEAVE_DEG = 20.0
WEAVE_PERIOD_S = 90.0
START_XY_M = (1500.0, 1500.0)
FLIGHT_ALT_MSL_M = 1200.0

INS_VEL_BIAS_MPS = (0.8, -0.6)
INS_VEL_NOISE_MPS = 0.05
INS_INITIAL_ERROR_M = (150.0, -100.0)
BARO_NOISE_M = 2.0
RADALT_NOISE_M = 3.0
DEM_ERROR_M = 4.0

INIT_POS_SIGMA_M = 250.0
INIT_BIAS_SIGMA_MPS = 1.0
PROCESS_POS_SIGMA_M = 3.0
PROCESS_BIAS_SIGMA_MPS = 0.02
RESAMPLE_ESS_FRACTION = 0.5
REPORT_EVERY_S = 20


def true_velocity(t):
    heading = math.radians(BASE_HEADING_DEG + WEAVE_DEG * math.sin(2 * math.pi * t / WEAVE_PERIOD_S))
    return SPEED_MPS * math.sin(heading), SPEED_MPS * math.cos(heading)  # (east, north)


def systematic_resample(rng, particles, weights):
    n = len(particles)
    step = 1.0 / n
    u = rng.uniform(0, step)
    out, cum, i = [], weights[0], 0
    for k in range(n):
        target = u + k * step
        while target > cum and i < n - 1:
            i += 1
            cum += weights[i]
        out.append(list(particles[i]))
    return out


def weighted_stats(particles, weights):
    mx = sum(w * p[0] for p, w in zip(particles, weights))
    my = sum(w * p[1] for p, w in zip(particles, weights))
    var = sum(w * ((p[0] - mx) ** 2 + (p[1] - my) ** 2) for p, w in zip(particles, weights))
    return mx, my, math.sqrt(var)


def run(seed, n_particles, duration_s, terrain_scale):
    rng = random.Random(seed)
    dem = synthetic_dem(DEM_ROWS, DEM_COLS, DEM_SPACING_M, seed)
    dem.h = [[z * terrain_scale for z in row] for row in dem.h]
    meas_sigma = math.sqrt(BARO_NOISE_M ** 2 + RADALT_NOISE_M ** 2 + DEM_ERROR_M ** 2)

    tx, ty = START_XY_M
    ix, iy = tx + INS_INITIAL_ERROR_M[0], ty + INS_INITIAL_ERROR_M[1]
    particles = [
        [ix + rng.gauss(0, INIT_POS_SIGMA_M), iy + rng.gauss(0, INIT_POS_SIGMA_M),
         rng.gauss(0, INIT_BIAS_SIGMA_MPS), rng.gauss(0, INIT_BIAS_SIGMA_MPS)]
        for _ in range(n_particles)
    ]
    weights = [1.0 / n_particles] * n_particles
    resamples = 0
    terrain_seen = []

    print(f"seed={seed} particles={n_particles} duration={duration_s}s "
          f"terrain_scale={terrain_scale} meas_sigma={meas_sigma:.1f}m")
    print(f"{'t[s]':>5} {'INS err[m]':>11} {'PF err[m]':>10} {'PF 1-sigma[m]':>14} {'bias est e/n [m/s]':>19}")

    steps = int(duration_s / DT_S)
    for k in range(1, steps + 1):
        t = k * DT_S
        ve, vn = true_velocity(t)
        tx, ty = tx + ve * DT_S, ty + vn * DT_S
        ins_ve = ve + INS_VEL_BIAS_MPS[0] + rng.gauss(0, INS_VEL_NOISE_MPS)
        ins_vn = vn + INS_VEL_BIAS_MPS[1] + rng.gauss(0, INS_VEL_NOISE_MPS)
        ix, iy = ix + ins_ve * DT_S, iy + ins_vn * DT_S

        ground = dem.height(tx, ty)
        if ground is None:
            print(f"t={t:.0f}s: truth left the DEM, stopping")
            break
        terrain_seen.append(ground)
        baro = FLIGHT_ALT_MSL_M + rng.gauss(0, BARO_NOISE_M)
        radalt = FLIGHT_ALT_MSL_M - ground + rng.gauss(0, RADALT_NOISE_M)
        measured_terrain = baro - radalt

        for p in particles:
            p[2] += rng.gauss(0, PROCESS_BIAS_SIGMA_MPS)
            p[3] += rng.gauss(0, PROCESS_BIAS_SIGMA_MPS)
            p[0] += (ins_ve - p[2]) * DT_S + rng.gauss(0, PROCESS_POS_SIGMA_M)
            p[1] += (ins_vn - p[3]) * DT_S + rng.gauss(0, PROCESS_POS_SIGMA_M)

        new_w = []
        for p, w in zip(particles, weights):
            h = dem.height(p[0], p[1])
            if h is None:
                new_w.append(0.0)
            else:
                r = (measured_terrain - h) / meas_sigma
                new_w.append(w * math.exp(-0.5 * r * r))
        total = sum(new_w)
        if total <= 0.0:
            print(f"t={t:.0f}s: all particle weights vanished (filter divergence)")
            break
        weights = [w / total for w in new_w]

        mx, my, spread = weighted_stats(particles, weights)
        if k % int(REPORT_EVERY_S / DT_S) == 0:
            be = sum(w * p[2] for p, w in zip(particles, weights))
            bn = sum(w * p[3] for p, w in zip(particles, weights))
            print(f"{t:5.0f} {math.hypot(ix - tx, iy - ty):11.1f} {math.hypot(mx - tx, my - ty):10.1f} "
                  f"{spread:14.1f} {be:9.2f}/{bn:<9.2f}")

        ess = 1.0 / sum(w * w for w in weights)
        if ess < RESAMPLE_ESS_FRACTION * n_particles:
            particles = systematic_resample(rng, particles, weights)
            weights = [1.0 / n_particles] * n_particles
            resamples += 1

    mean = sum(terrain_seen) / len(terrain_seen)
    roughness = math.sqrt(sum((h - mean) ** 2 for h in terrain_seen) / len(terrain_seen))
    print(f"resamples={resamples} terrain_std_along_track={roughness:.1f}m "
          f"true_bias e/n={INS_VEL_BIAS_MPS[0]:.2f}/{INS_VEL_BIAS_MPS[1]:.2f} m/s")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--particles", type=int, default=2000)
    ap.add_argument("--duration", type=float, default=200.0)
    ap.add_argument("--terrain-scale", type=float, default=1.0,
                    help="multiply DEM heights; small values emulate flat terrain")
    args = ap.parse_args()
    run(args.seed, args.particles, args.duration, args.terrain_scale)


if __name__ == "__main__":
    main()
