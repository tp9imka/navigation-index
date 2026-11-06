# LEO Doppler cold start via SDP - paper digest
<!-- about: res:leo-doppler-cold-start-2025 -->
**Initialization-Free LEO Doppler Positioning via Semidefinite Relaxation: A Cold-Start Approach** - Baoshan Song, Weisong Wen, Qi Zhang, Bing Xu, Penggao Yan, Yuan Li, Li-Ta Hsu (Hong Kong PolyU), arXiv 2025 (v1 2025-09-21, v2 2026-10-21 "Revised version"; no venue listed). [paper](https://arxiv.org/abs/2509.17198) | [code](https://github.com/Baoshan-Song/Certifiable-Doppler-positioning) | Read: full text via arXiv HTML (v2).

## Problem
Doppler-only LEO positioning is a nonlinear least-squares problem. Local solvers (Gauss-Newton, Dog-Leg) need a good initial position and diverge from far away. The paper wants a global solution for a static receiver with no prior position at all.

## Method
- Measurement model (Eq. 1): range rate plus receiver clock drift plus Gaussian noise; weighted NLS (Eq. 2).
- Multiply each residual by the range rho_i to remove the fractional line-of-sight term (Eq. 3) => polynomial residuals; weights 1/(sigma_i^2 rho_i^2), updated iteratively.
- Lift to a QCQP with auxiliary variables (e.g. z_i = c rho_i dt_r), state of size 2N+4 (Eqs. 4-5).
- SDP relaxation: replace yy^T by a PSD matrix S and drop rank-1 (Eqs. 8-9); solve with CVX/SeDuMi.
- Rank-1 check (lambda1/lambda2 > 1e5) certifies global optimality; extract the solution from the principal eigenvector.
- Optional refinement: seed GN or DL with the SDP solution ("SDP-GN", "SDP-DL").
- Theory: tightness in the noiseless case; a sufficient (stated as conservative) noise bound for tightness (Proposition 1, Eq. 15).

## Data and sensors
- Simulation: 49 LEO satellites at 800 km on a 1500 x 1500 km grid, 1.626 GHz carrier, 40 Monte Carlo runs per scenario.
- Real: Iridium-NEXT captured with an SDR on the PolyU campus (Table 2): 8 visible satellites, 35 minutes, 436 measurements, TLE + SGP4 ephemerides, static receiver at (22.3045966, 114.180121, 61.384 m).
- No Starlink or Orbcomm data. No dataset card in this hub.

## Headline results (as reported)
- Table 1 (simulation, 3D error km): with init 1/10/100 km, GN/DL/SDP-GN/SDP-DL all 0.00 and SDP alone 0.71. At 580 km init: GN 1839.60, DL 91.65, SDP 0.71, SDP-GN/SDP-DL 0.00. At 1000 km: GN "-", DL 892.23, SDP-GN/SDP-DL 0.00. The 0.71 km SDP residual is attributed to interior-point precision under ECEF scaling.
- Table 3 (real Iridium, 3D error km): init 10/100/500 km: GN 0.13, DL 0.13, SDP 0.14, hybrids 0.13. At 1000 km: GN 2342.50, DL 2069.00, SDP 0.14, hybrids 0.13. At 5000 km: GN "-", DL 8445.10, SDP 0.14, hybrids 0.13.
- Fig. 5: SDP 3D 140 m, horizontal 122 m; hybrids ~130 m 3D.
- Fig. 4: sufficient noise bounds ~2.5e-2 m/s satellite velocity noise and ~5.5e-2 m/s Doppler noise.
- Fig. 3: SDP error grows with noise (Doppler/velocity 0.1-10 m/s, satellite position 10-1000 m) but stays bounded (qualitative).
- Runtime: SDP on 436 observations ~39.69 s; GN/DL refinement < 0.008 s. MATLAB R2024b, CVX + SeDuMi high precision; hardware not stated.

## Limitations
- Stated by authors: static receiver only (dynamic case and joint orbit estimation left for future sum-of-squares work); the noise bound for tightness is conservative.
- Our read: the SDP alone leaves 0.71 km error in simulation; always run the GN/DL refinement after it.
- Our read: Sec. 5.5 says GN diverges or gives no feasible output at 1000 km, while Table 3 lists 2342.50 km. Minor text/table mismatch.
- Our read: one site, one 35 min Iridium session. The 130-140 m result is dominated by TLE error and is not a statement about Starlink.
- Our read: ~40 s per solve and a lifted state of size 2N+4 (N = number of measurements) make it an initializer, not a real-time filter.

## Code, weights, license
- Repo `Baoshan-Song/Certifiable-Doppler-positioning`: MATLAB, needs CVX. Files: `matlab/simulation/simulate_doppler.m`, `matlab/example_simulation.m`, `matlab/example_iridium.m` (real Iridium Doppler example).
- License gotcha: README says GPL v3, but the repo has no LICENSE file and GitHub API reports no license. Treat as GPL v3 per README intent, confirm with the authors before redistributing.
- README cites an older title, "Certifiably Optimal Doppler Positioning using Opportunistic LEO Satellites", for the same arXiv id (v1 title, our read).
- Last push 2025-10-13, 10 stars. No weights (not ML).

## Reproduction effort (estimate)
Estimate:
- MATLAB + CVX (free CVX with SeDuMi works). Clone, run `example_simulation.m` and `example_iridium.m`; under an hour to a first result if MATLAB is available.
- Without MATLAB: port to Python with CVXPY + SCS/MOSEK; a day, and expect different numerical precision than SeDuMi.
- Not reproducible beyond the shipped Iridium session: no other real captures released.

## What a hackathon team can take from it
- A drop-in initializer: SDP from no prior => GN/DL refinement. Solves the "converged only from ~150 km" gap in [psiaki-transit-on-steroids-2021](psiaki-transit-on-steroids-2021.md).
- The rank-ratio test (lambda1/lambda2 > 1e5) is a free integrity flag: when the relaxation is not tight, do not trust the fix.
- Run the SDP once at startup (40 s budget), then hand off to a fast EKF on Doppler (e.g. the STAN pattern in [kassas-starlink-navigation](kassas-starlink-navigation.md)).
- Subsample measurements for the SDP; full data only in the refinement step.
- The shipped Iridium example is real data a team can run immediately without any RF hardware.
