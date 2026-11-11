# 05. CBF baselines for the idea C kill test, read faithfully

Loop-05, 2026-11-09. Lane 04 ([04-innovation-prior-art.md](04-innovation-prior-art.md), sections
3 and 5) made the integrity-aware safety filter the headline. Its kill test compares against
PX4-CBF, Belief-CBF and a gatekeeper-style backup filter, all read there as abstracts only.
This doc reads the code and full texts so the later implementation compares against what the
authors built, not against a weaker copy.

Nothing here was run. No result files were produced. Every number is quoted from the cited
source. Pseudo-code is ours, written from the equations and code; it is not tested.

## 0. Findings that change the kill test

1. **PX4-CBF as shipped has no FoV constraint.** The NTNU PX4 fork, branch `cbf` (HEAD
   `e7ef0c61`, 2025-02-12), contains only the analytic single-constraint filter. The
   FoV-constrained qpOASES QP from the paper sits in the earlier commit `338fb51f`; commit
   `db478f07` is titled "[wip] switch to analytical". The paper itself says mapless navigation
   with a sensor FoV under 180 deg cannot be safe for arbitrary motion, and adds the FoV
   constraint for that reason. With our 90 deg range fan, the faithful baseline is the FoV
   variant. The shipped analytic variant is a second arm, labelled as such.
2. **PX4-CBF needs no position, but it does use the velocity estimate.** A VIO position jump
   does not touch it. A VIO velocity bias does. Fault cases in the kill test must say which
   one they inject.
3. **MR-CBF and robust gatekeeper already take a per-step error bound.** MR-CBF has
   `epsilon(y)`, a bound on the state error that may depend on the measurement. Robust
   gatekeeper has `r`, a bound on `||x - x_hat||` at the start of each check. Feeding a
   protection level (PL) into either is a parameter choice inside published theory. Our claim
   narrows to: an integrity monitor produces a bound that stays valid under faults, online.
   The papers took the bound as given (Cosner 2021: a constant 0.4 m measured against motion
   capture). Measured since (synthetic): the monitor's in-loop PL did not stay valid in the
   VIO + UWB two-fault case (breach fraction 1.6e-3 to 8.3e-3 against a 1e-3 risk,
   [what the collisions are](../../../samples/close-area-safety-filter/README.md#what-the-collisions-are)), and a fixed
   0.2 m bound matched its safety ([section 5](#5-baseline--minimal-faithful-implementation-for-the-kill-test)).
4. **Belief-CBF brakes before the margin grows.** The barrier includes the covariance
   prediction `Sigma_dot = A Sigma + Sigma A^T + Q` and a margin `gamma` for the jump at the
   next measurement update. A filter that only inflates clearance by `k * sqrt(lambda_max(P))`
   at update instants is a weaker copy.
5. **Venues are now confirmed (Crossref).** Belief-CBF: IEEE RA-L 8(12):8565-8572, 2023, doi
   10.1109/LRA.2023.3330662 (the hub record says "preprint"). gatekeeper: IEEE T-RO
   40:4358-4375, 2024, doi 10.1109/TRO.2024.3454415, plus IROS 2023 pp. 259-266. PX4-CBF:
   ICUAS 2025 pp. 697-704 (README bibtex).

Source labels used below: **peer-reviewed** / **preprint** / **code** / **docs**, with what was
read: full text, code, README or abstract.

## 1. PX4-CBF (Misyats, Harms, Nissov, Jacquet, Alexis, ICUAS 2025)

### 1.1 Sources read

| Source | Label | Read |
|---|---|---|
| [arXiv 2504.15850](https://arxiv.org/abs/2504.15850) HTML v1, incl. Tables I and II | peer-reviewed (ICUAS 2025) | full text |
| [ntnu-arl/PX4-Autopilot](https://github.com/ntnu-arl/PX4-Autopilot/tree/cbf) branch `cbf`: `CBFSafetyFilter.cpp/.hpp`, `multicopter_safety_filter_params.c`, `PositionControl.cpp`, `MulticopterPositionControl.cpp` | code | code, HEAD `e7ef0c61`, and `CBFSafetyFilter.cpp` at `338fb51f` |
| [ntnu-arl/PX4-CBF](https://github.com/ntnu-arl/PX4-CBF) | docs | README |
| [ntnu-arl/composite_cbf](https://github.com/ntnu-arl/composite_cbf): `CbfSafetyFilter.cpp/.hpp`, `CompositeCbfNode.cpp`, `config/sim.yaml` | code | code |
| [ntnu-arl/cbf_pc_selector](https://github.com/ntnu-arl/cbf_pc_selector) | code | README only |
| Harms, Jacquet, Alexis, ICRA 2025, [arXiv 2502.04101](https://arxiv.org/abs/2502.04101) | peer-reviewed (ICRA 2025 per arXiv comment) | abstract only |

### 1.2 Model, barrier, constraint (paper, as written)

Model (eq. 5): double integrator, acceleration is the input.

```
[p_dot; v_dot] = [0 I; 0 0][p; v] + [0; I] a
```

Per obstacle point `p_i` (eq. 6, 7), relative degree 2, made relative degree 1 with an
exponential CBF with pole `p0 < 0`:

```
nu_i0(x) = ||p_i - p||^2 - eps^2
nu_i1(x) = nu_i0_dot - p0 nu_i0 = -2 v^T (p_i - p) - p0 nu_i0
```

Composite barrier over n points (eq. 8), soft-min with saturation `s = tanh`:

```
h(x) = -(gamma/kappa) ln sum_i exp[ -kappa s(nu_i1 / gamma) ]
```

Lie derivatives (eq. 9-12), with `lambda_i = exp[-kappa s(nu_i1/gamma)] s'(nu_i1/gamma)` and
`Lambda` the sum inside the log:

```
Lf h = (1/Lambda) sum_i lambda_i Lf nu_i1,   Lf nu_i1 = 2 v^T (v + p0 (p_i - p))
Lg h = (1/Lambda) sum_i lambda_i Lg nu_i1,   Lg nu_i1 = -2 (p_i - p)^T
```

Class-K function (eq. 13):

```
alpha(h) = alpha h              if h >= 0
         = h / (1/alpha + |h|)  otherwise
```

FoV constraint (eq. 15, 16), yaw-aligned frame V, inward normals `e_j` of the frustum planes,
`Lf h_fj` assumed 0; only the two horizontal planes are used:

```
h_fj(x) = e_j^T R_VI v,   h_fj_dot ~= e_j^T R_VI a
```

Full QP (eq. 17), FoV as soft constraints:

```
a* = argmin_a (a - a_sp)^T H (a - a_sp) + sum_{i=1,2} rho delta_fi
s.t. Lg h a >= -Lf h - alpha(h)
     Lg h_fi a >= -Lf h_fi - alpha_f h_fi - delta_fi,   delta_fi >= 0
```

Without FoV and with isotropic H, closed form (eq. 18, 19, from Alan et al. 2023):

```
a* = a_sp + max{0, eta} Lg h^T
eta = -(Lf h + Lg h a_sp + alpha(h)) / ||Lg h||^2   if Lg h != 0, else 0
```

Input and output are low-passed (eq. 20): `a_filt_dot = (a - a_filt) / tau`.

How uncertainty and FoV enter: no position estimate is used; obstacles are body-frame points
from the current scan. The velocity estimate enters `nu_i1`, `Lf h`. Unseen obstacles are not
in the barrier at all; the FoV constraint keeps the velocity inside the sensor frustum so the
vehicle moves only where it can see. No covariance, no error bound.

### 1.3 What the code does differently from the paper

| Item | Paper | PX4 fork `cbf` HEAD | PX4 fork `338fb51f` | composite_cbf (ROS 2) |
|---|---|---|---|---|
| FoV constraint | yes, eq. 17 | **absent** | qpOASES QP, 5 variables (3 accel correction + 2 slacks) | absent (README: unconstrained-FoV case) |
| Class-K function | eq. 13 (nonlinear for h < 0) | linear `alpha*h` (`kappaFunction` defined, unused) | eq. 13 via `kappaFunction` | linear `alpha*h` |
| Input to the correction | `a_sp` | raw `a_sp`; low-passed input only logged | raw `a_sp` | low-passed input (`lp_gain_in`) |
| Low-pass form | `tau` (eq. 20) | discrete gain per step | same | discrete gain per step |
| FoV half-angle | from sensor | n/a | hard-coded 40 deg (`_fov_h`, TODO param) | n/a |
| FoV constraint variable | total `a` (eq. 17c) | n/a | applied to the correction only; the `e_j . a_sp` term is missing | n/a |
| Output clamp | not in QP | per-axis clamp after the correction | same | same |

The FoV code at `338fb51f` uses a linear slack cost (`g = CBF_FOV_SLACK` on each slack) and
zero quadratic weight on the slacks, consistent with eq. 17a.

### 1.4 Parameters and defaults

| Parameter | Paper Table II (flight) | Paper Table I range | composite_cbf `sim.yaml` and `CbfConfig` | PX4 fork param default |
|---|---|---|---|---|
| eps (m) | 0.7 | > 0 | 0.7 | `CBF_EPSILON` 0.5 |
| kappa | 70 | [10, 100] | 70 | `CBF_KAPPA` 10 |
| gamma | 40 | [10, 100] | 40 | `CBF_GAMMA` 40 |
| alpha | 2 | [1, 3] | 2 | `CBF_ALPHA` 1 |
| p0 | -2.5 | [-3, -1] | -2.5 | `CBF_POLE0` -2 |
| alpha_f | 6 | [2, 8] | n/a | `CBF_FOV_ALPHA` 1 |
| tau / LP gains | tau 0.5 | tau [0.01, 0.1] | `lp_gain_in` 0.4, `lp_gain_out` 0.6 | `CBF_LP_GAIN_IN` 0.01, `CBF_LP_GAIN_OUT` 0.01 |
| rho (FoV slack) | not given | - | n/a | `CBF_FOV_SLACK` 50 |
| H | not given | - | identity (analytic) | `CBF_QP_GAIN_X/Y/Z` 1 |
| accel clamp (m/s^2) | not given | - | `max_acc_xy` 3, `max_acc_z` 3 | `CBF_CLAMP_XY` 3, `CBF_CLAMP_Z` 3 |
| obstacle timeout | not given | - | `obs_to` 1 s | 1 s (hard-coded) |
| command timeout | not given | - | `cmd_to` 1 s | n/a |
| enabled | - | - | - | `CBF_ENABLED` 0 (off) |

Two inconsistencies we could not resolve. Table II gives tau = 0.5 while Table I gives a range
of [0.01, 0.1]. The PX4 defaults are not the flight values; use Table II, which matches
composite_cbf. Paper tuning procedure (section V-E): tune acceleration tracking first (100-200
ms roll/pitch rise time), set eps, start gamma and kappa large, alpha = 2, p0 = -1, then enable
FoV with alpha_f = 1 and raise it.

### 1.5 Rates

- Filter runs inside the PX4 position controller at 100 Hz (paper VI-A). composite_cbf
  `ctrl_freq` is 100 Hz.
- Obstacles: up to 100 points at 15 Hz in flight; the paper says 10 Hz or more is adequate.
  ToF ranges clamped at 5 m. PX4 code buffer holds up to 200 (`CBF_MAX_OBSTACLES`), sent in
  chunks of 20.
- Downsampling: paper says minimum range per angular bin; the cbf_pc_selector README config
  uses a percentile per bin (example value 20 %), not the strict minimum.
- Compute on the VOXL2 Mini: 50 us with 25 obstacles and 400 us with 200 for the analytic
  case; FoV QP 2 ms average, 2.5 ms spikes.

### 1.6 Infeasible or degenerate cases

- Analytic: one half-space with unbounded input is always feasible. If `||Lg h||^2 <= 1e-5`
  the correction is 0 (pass-through). Actuator limits are not in the QP; the per-axis clamp
  after the correction can undo it, with no flag.
- FoV QP (`338fb51f`): on qpOASES failure (`RET_MAX_NWSR_REACHED`, `nWSR` = 50, or any other
  error) it sets `qp_fail = 1` and keeps the previous output. No fallback action.
- composite_cbf: NaN output => zero acceleration and an error status. Command older than 1 s
  => zero input.
- Both: obstacles older than 1 s are cleared, after which the filter passes the nominal
  command through. A range sensor that stops returning points removes all protection.

### 1.7 Pseudo-code (2.5D point mass, range fan)

```python
EPS, P0, KAPPA, GAMMA, ALPHA = 0.7, -2.5, 70., 40., 2.   # paper Table II
LP_IN, LP_OUT, AMAX, OBS_TO = 0.4, 0.6, 3.0, 1.0         # composite_cbf defaults
def on_scan(ranges, bearings, t):                        # 10-15 Hz
    S.obs = bin_min_points(ranges, bearings, n_bins)     # body-frame 2D points, <= 100
    S.t_obs = t
def cbf_filter(a_sp_w, v_w, yaw, t):                     # 100 Hz
    R = rot2(yaw); a = R.T @ a_sp_w; v = R.T @ v_w       # body frame
    S.a_in = (1 - LP_IN) * S.a_in + LP_IN * a            # PX4 fork: use raw a instead
    if t - S.t_obs > OBS_TO: S.obs = []
    if not S.obs: return R @ S.a_in                      # pass-through, as in the code
    nu1 = [-2 * p @ v - P0 * (p @ p - EPS**2) for p in S.obs]
    w = [exp(-KAPPA * tanh(n / GAMMA)) for n in nu1]; L = sum(w)
    h = -(GAMMA / KAPPA) * log(L)
    lam = [wi * (1 - tanh(n / GAMMA)**2) for wi, n in zip(w, nu1)]
    Lf = sum(l * 2 * v @ (v + P0 * p) for l, p in zip(lam, S.obs)) / L
    Lg = sum(l * (-2 * p) for l, p in zip(lam, S.obs)) / L
    eta = -(Lf + Lg @ S.a_in + ALPHA * h) / (Lg @ Lg) if Lg @ Lg > 1e-5 else 0.
    a_star = clip(S.a_in + max(eta, 0.) * Lg, -AMAX, AMAX)
    S.a_out = (1 - LP_OUT) * S.a_out + LP_OUT * a_star
    return R @ S.a_out
# FoV variant (paper eq. 17): replace the eta line by a QP over (a, d1, d2):
#   min (a-a_in)^T (a-a_in) + RHO*(d1+d2)  s.t.  Lg@a >= -Lf - alpha_eq13(h),
#   e_j@a >= -ALPHA_F*(e_j@v) - d_j, d_j >= 0, e_j = inward normals of the +-45 deg fan.
```

### 1.8 What our sim must provide

- Range returns converted to body-frame points, binned to at most 100, at 10-15 Hz, clamped to
  the sensor range (paper used 5 m).
- An **estimated** body-frame velocity (from our EKF, not truth) and yaw at 100 Hz.
- A nominal **acceleration** setpoint. If the planner outputs velocity, wrap it in a P velocity
  loop the way PX4 does, then filter its output.
- An acceleration tracking lag (first-order, matching the 100-200 ms rise time in the tuning
  procedure) so the low-pass and the barrier see realistic tracking error.

## 2. Belief-CBF (Vahs, Pek, Tumova, IEEE RA-L 2023)

### 2.1 Sources read

| Source | Label | Read |
|---|---|---|
| [arXiv 2309.06499](https://arxiv.org/abs/2309.06499) HTML v1, incl. Table I; venue RA-L 8(12):8565-8572, doi 10.1109/LRA.2023.3330662 (Crossref) | peer-reviewed | full text |
| Official code for the 2023 paper | - | not found (`gh search repos "belief control barrier"`) |
| Follow-up: Han, Vahs, Tumova, CDC 2025, [arXiv 2504.04097](https://arxiv.org/abs/2504.04097); code [KTH-RPL-Planiacs/sample_based_bcbf](https://github.com/KTH-RPL-Planiacs/sample_based_bcbf) (Python, MIT) | peer-reviewed + code | abstract + README |

### 2.2 Barrier and constraint (as written)

Stochastic model (eq. 9, 10): `x_dot = f(x) + g(x) u + w`, `w ~ N(0, Q)`;
`z_k = l(x_k) + v_k`, `v_k ~ N(0, R_k)`, observations in discrete time.

Safe set over beliefs `b = [mu, vec(Sigma)]` (eq. 11, 12), half-space `alpha^T x >= beta`,
risk level delta:

```
h_b(b) = VaR_delta(alpha^T x - beta)
       = alpha^T mu - beta - erfinv(1 - 2 delta) sqrt(2 alpha^T Sigma alpha)
```

Hybrid belief dynamics. Between updates (eq. 13-15, continuous EKF):
`mu_dot = f(mu) + g(mu) u`, `Sigma_dot = A Sigma + Sigma A^T + Q`. At an update (eq. 16):
`mu+ = mu- + K (z - l(mu-))`, `Sigma+ = (I - K H) Sigma-`. The innovation term is treated as
`theta ~ N(0, Lambda)`, `Lambda = K (H Sigma H^T + R) K^T` (eq. 17).

BCBF condition (eq. 19): `dh_b/db (f_b(b) + g_b(b) u) >= -h_b(b)`. For relative degree 2 they
use the second-order exponential CBF of eq. 4: `h_ddot + zeta^T [h, h_dot]^T >= 0`.

Margin for the update jump (Theorem 3): shrink to `h_tilde = h_b - gamma` with

```
gamma >= sqrt(2 alpha^T Lambda alpha) erfinv(1 - 2 eps) - xi(b-)
xi(b-) = erfinv(1 - 2 delta) ( sqrt(2 alpha^T Sigma- alpha)
                             - sqrt(2 alpha^T (I - K H) Sigma- alpha) )
```

so the belief stays in the safe set with probability at least `1 - eps` across an update.

QP (eq. 25): `u* = argmin (u - u_ref)^T (u - u_ref)` s.t. the BCBF condition on `h_tilde`.

Circular obstacle (eq. 27, 28): `Pr[||x - c|| - r >= 0] >= 1 - delta`, linearised at the mean
with `alpha = (mu - c) / ||mu - c||`.

How uncertainty enters: the covariance tightens h directly, its predicted growth enters
`h_dot` and `h_ddot`, and the expected update jump enters as `gamma`. Sensor FoV does not
enter; obstacles are known geometry in the map frame.

Two sign issues as printed. Eq. 6 gives `Pr[alpha^T x >= beta] = 1/2 (1 - erf(...))`, which is
the probability of the opposite event. The 1D example writes `+ erfinv(...)` where eq. 12 has
`-`. Use the standard Gaussian quantile; eq. 12 is the consistent form.

### 2.3 Parameters, rates, infeasibility

- Simulation (unicycle): delta = 0.01; eps = 0.5 (natural bound only) and eps = 0.01;
  sensor 10 Hz; R = diag(0.2^2, 0.2^2, 0.1^2, 0.1^2); LQR reference controller. Table I:
  collisions 1 (eps 0.5) and 0 (eps 0.01) of 100 runs, versus 3 for stochastic CBF and 3 for
  CCNMPC; mean compute 0.0008 s and 0.0017 s per step.
- Hardware: Crazyflie 2.1, double integrator in position and velocity, Q diagonal 0.05^2,
  setpoints at 100 Hz, Euler-discretised EKF, delta = 0.05. Corridor R changes between
  0.08^2, 0.2^2 and 0.15^2 per axis. Experiment II uses optical-flow velocity only, noise
  0.2^2.
- ECBF gains zeta: not given in the text.
- Infeasibility: the paper says it is not an issue because the QP is over controls only. The
  sim has one obstacle; with input bounds or several constraints feasibility is not
  discussed. In our sim add a heavily penalised slack and count its use.

### 2.4 Pseudo-code (2.5D, double integrator, map obstacles)

For `A = [[0, I], [0, 0]]` the covariance dynamics do not depend on u, so the BCBF is the
mean-state ECBF plus covariance terms. `P, C, V` are the position, cross and velocity blocks of
Sigma. The derivative terms below are our derivation with `n` held fixed per step, matching
the paper's linearisation; they are not in the paper.

```python
k = sqrt(2) * erfinv(1 - 2 * DELTA)                 # = Phi^-1(1 - delta)
def predict(dt, u):                                  # every control step
    mu += dt * (A @ mu + B @ u); S += dt * (A @ S + S @ A.T + Q)
def update(z):                                       # at sensor rate, H = [I 0]
    K = S @ H.T @ inv(H @ S @ H.T + Rm); mu += K @ (z - H @ mu); S = (I - K @ H) @ S
def bcbf_filter(u_ref):                              # 100 Hz
    P, C, V = S[:2,:2], S[:2,2:], S[2:,2:]; p, v = mu[:2], mu[2:]
    Kp = S @ H.T @ inv(H @ S @ H.T + Rm); Lam = Kp @ (H @ S @ H.T + Rm) @ Kp.T
    Spost = ((I - Kp @ H) @ S)[:2,:2]; rows = []
    for c, r in nearby_map_obstacles(p):
        d = norm(p - c); n = (p - c) / d
        s = sqrt(n @ P @ n); sd = n @ (C + C.T + Q[:2,:2]) @ n / (2 * s)
        sdd = (n @ V @ n) / s - sd**2 / s           # P_ddot = 2V
        xi = erfinv(1 - 2*DELTA) * (sqrt(2 * n @ P @ n) - sqrt(2 * n @ Spost @ n))
        gam = max(0., sqrt(2 * n @ Lam[:2,:2] @ n) * erfinv(1 - 2*EPS_R) - xi)
        h = d - r - k * s - gam; hd = n @ v - k * sd
        rows.append((n, k * sdd - Z1 * hd - Z0 * h))     # n @ u >= rhs  (eq. 4)
    return qp_min_dist(u_ref, rows)    # closed form if one row; else small QP + slack
```

`Z0, Z1` come from pole placement (both poles at -p gives `Z0 = p^2`, `Z1 = 2p`); the paper does
not give values. Computing `Lam` from the current Sigma, not the prior at the next update time,
is our simplification.

### 2.5 What our sim must provide

The EKF mean and full covariance including cross terms, the process noise Q used by the EKF,
the measurement model H and R, the sensor rate (for the dark zones the covariance must grow
between updates), the obstacle geometry in the map frame (circles or half-spaces), and the
risk levels delta and eps.

## 3. gatekeeper (Agrawal, Chen, Panagou, IEEE T-RO 2024)

### 3.1 Sources read

| Source | Label | Read |
|---|---|---|
| [arXiv 2211.14361](https://arxiv.org/abs/2211.14361) v4 HTML; T-RO 40:4358-4375, doi 10.1109/TRO.2024.3454415; IROS 2023 pp. 259-266 (Crossref) | peer-reviewed | full text, sections III-VI |
| [dev10110/gatekeeper](https://github.com/dev10110/gatekeeper) (MIT): PDFs, a Julia firewatch notebook, videos | code | file tree and README; notebook not read |

### 3.2 Method (as written)

Candidate trajectory (Def. 6, eq. 21): from `x_k`, track the nominal trajectory up to
`t_k + T_S`, then run the backup controller:

```
u(t) = pi_T(p(t), p_nom_k(t))   for t in [t_k, t_k + T_S)
     = pi_B_k(t, p(t))          for t >= t_k + T_S
```

Valid (Def. 7): `p_can(t) in B_k(t)` for all `t in [t_k, t_kB]` and
`p_can(t_kB) in C_k(t_kB)`, with `t_kB = t_k + T_S + T_B`. `B_k` is the perceived safe set,
`C_k` a backup set the backup controller keeps invariant.

Committed trajectory (Def. 8): `T_S* = max {T_S in [0, T_H] : candidate valid}`. If no
candidate is valid, keep the previous committed trajectory. The tracker always follows the
last committed one.

Robustly valid (Def. 9), with `||x(t_k) - x_hat(t_k)|| <= r` and
`R = beta(r, 0) + gamma(w_bar)` from the ISS bound of the tracking observer-controller (eq. 16):

```
x_hat(t_k) = p_can(t_k)                                    (30)
p_can(t) in B_k(t) (-) Ball(R)   for t in [t_k, t_kB]       (31)
p_can(t_kSB) in C_k(t_kB)                                  (32)
C_k(t) subset S(t) (-) Ball(R + r)   for t >= t_k           (33)
```

`(-)` is the Pontryagin difference. Assumption 1: `B_k` is a subset of the true safe set and
does not shrink with new information. Algorithm 1: grid search `T_S = (1 - i/N) T_H`,
`i = 0..N-1`, first valid one wins.

How uncertainty and FoV enter: estimate error through `r`, tracking and disturbance error
through `R`. FoV enters through the perceived safe set: in the quadrotor runs unknown voxels
count as obstacles, so the vehicle never commits to a stop it has not seen.

### 3.3 Parameters and rates (quadrotor implementation, section VI-B/C)

- N = 10 (median compute 3.4 ms in the firewatch case); `T_S <= 2 s`, `T_B = 2.0 s`.
- Validation model: triple integrator. Backup: stopping controller, terminal state zero
  speed and zero input.
- Safe set: 4 x 4 x 2 m ESDF block (nvblox, 7.5 cm voxels), unknown = occupied, convex
  polyhedron from DecompUtil.
- Margins: robot radius 0.15 m, voxel 0.075 m, R = 0.1 m (from measured 5-10 cm tracking
  error), R + r = 0.2 m at the terminal state. Minimum passable gap 0.58 m.
- Rates: planner 5 Hz in sim, every 2 s on hardware; ESDF 5 Hz; gatekeeper 20 Hz on hardware;
  geometric tracking controller 250 Hz. Nominal speed 1 m/s (sim table) and 2 m/s planner
  time allocation.
- When the nominal path is not traversable, gatekeeper publishes a virtual obstacle so the
  planner replans.
- Infeasibility: by construction there is always a committed trajectory that ends in the
  backup set; if nothing validates, the vehicle keeps tracking it and stops.

### 3.4 Pseudo-code

```python
TH, TB, N = 2.0, 2.0, 10
MARGIN = ROBOT_R + VOXEL + R            # 0.15 + 0.075 + 0.1 in the paper
MARGIN_END = ROBOT_R + VOXEL + R + r    # R + r = 0.2 in the paper
committed = simulate(x_hat, None, 0.0, TB)          # T_S = 0: brake from the start
def gatekeeper_step(x_hat, p_nom, grid):            # 20 Hz
    global committed
    sdf = signed_distance(grid, unknown_as_occupied=True)
    for i in range(N):
        TS = (1 - i / N) * TH
        traj = simulate(x_hat, p_nom, TS, TB)       # track p_nom, then brake to v = 0
        ok = all(sdf(q.p) >= MARGIN for q in traj)
        ok = ok and norm(traj[-1].v) < 1e-3 and sdf(traj[-1].p) >= MARGIN_END
        if ok:
            committed = traj; return committed
    return committed                                 # keep last; it already ends stopped
# tracker: follow committed(t) at the control rate (paper 250 Hz)
```

### 3.5 What our sim must provide

A time-parameterised nominal trajectory over 2 s (the planner may ignore dynamics), an
occupancy grid built from the range fan that keeps an unknown state, a forward model of the
closed-loop tracker plus brake, a measured tracking error bound R, and an estimate error
bound r. The `r` slot is where a PL would plug in.

## 4. Measurement-robust CBF (Dean, Taylor, Cosner, Recht, Ames, CoRL 2020)

### 4.1 Sources read

| Source | Label | Read |
|---|---|---|
| Dean et al., CoRL 2020, PMLR 155:654-670, [page](https://proceedings.mlr.press/v155/dean21a.html), arXiv 2010.16001 | peer-reviewed | full text (arXiv LaTeX source `main.tex`), appendices not read |
| Cosner et al., IROS 2021, [arXiv 2104.14030](https://arxiv.org/abs/2104.14030) | peer-reviewed | full text of `mrcbf.tex`, `combine_theory.tex`, `experimental_results.tex` (LaTeX source) |
| [rkcosner/cyberpod_sim_ros](https://github.com/rkcosner/cyberpod_sim_ros) | code | README only; no license file |

### 4.2 Constraint (as written)

Measurement `y = p(x)`, estimate `x_hat = q_hat(y) = x + e(x)`, `e(x) in E(y)`, and
`epsilon(y) >= max ||e||` over `E(y)`. MR-CBF condition (Dean eq. mr-cbf):

```
sup_u  Lf h(x_hat) + Lg h(x_hat) u - (a(y) + b(y) ||u||_2) > -alpha(h(x_hat))
```

Theorem 2 makes it sufficient with Lipschitz constants of `Lf h`, `Lg h` and `alpha o h` on C:

```
a(y) = epsilon(y) (L_Lfh + L_alpha_h),   b(y) = epsilon(y) L_Lgh
```

Controller (MR-OP), a second-order cone program; relaxed form R-MR-OP with slack:

```
k(y, x_hat) = argmin_{u, delta} 1/2 ||u - k_d(x_hat)||^2 + p delta^2
 s.t. Lf h(x_hat) - (L_Lfh + L_alpha_h) eps(y) + Lg h(x_hat) u
      - L_Lgh eps(y) ||u||_2 >= -alpha(h(x_hat)) - delta
```

No closed form; the paper notes Lagrangian closed forms do not apply because the constraint is
non-smooth. Cosner 2021 applies the same terms to every backup-set constraint (MR-BS-OP).

How uncertainty enters: a deterministic worst-case bound on the state error, which tightens
the constant term and penalises large inputs. With `epsilon = 0` it reduces to the CBF-QP.

### 4.3 Parameters, rates, infeasibility

- Dean: Segway sim, ECOS SOCP solver; Lipschitz constants estimated by the largest slope
  between adjacent grid points around the equilibrium; worst-case test with a constant
  pitch offset `epsilon = 0.2`; learned camera estimator at 15 Hz (kernel ridge regression,
  800 images).
- Cosner: Segway hardware, VIO position from a RealSense T265, `epsilon(y) = 0.4` chosen as a
  bound from motion capture; MR-BS-OP at 250 Hz with ECOS, 5 decision variables, 4 linear and
  6 cone constraints, torque saturated at +-20 Nm; backup horizon T = 1 s, Euler step 5 ms.
- Infeasibility: slack variable penalised by p (value not given); the effect on safety is
  argued through projection-to-state safety.

### 4.4 Pseudo-code (map obstacle, same ECBF as PX4-CBF, world frame)

```python
# h = nu1 = 2 (p-c).v - P0 (|p-c|^2 - r^2);  Lf h = 2|v|^2 - 2 P0 (p-c).v;  Lg h = 2 (p-c)
def lipschitz_on_box(fn, x_hat, box):              # Dean: max slope on a local grid
    return max(norm(grad_fd(fn, xg)) for xg in grid_around(x_hat, box))
def mrcbf_filter(u_d, x_hat, eps_y):               # eps_y: constant in the papers
    cons = []
    for c, r in nearby_map_obstacles(x_hat[:2]):
        h, Lf, Lg = barrier_terms(x_hat, c, r)
        L_Lf = lipschitz_on_box(lambda x: barrier_terms(x, c, r)[1], x_hat, BOX)
        L_ah = ALPHA * lipschitz_on_box(lambda x: barrier_terms(x, c, r)[0], x_hat, BOX)
        L_Lg = 2.0                                  # Lg h = 2(p-c) is 2-Lipschitz in p
        cons.append((Lf - (L_Lf + L_ah) * eps_y, Lg, L_Lg * eps_y, ALPHA * h))
    u, d = cp.Variable(2), cp.Variable()
    g = [a0 + Lg @ u - b * cp.norm(u, 2) >= -ah - d for a0, Lg, b, ah in cons]
    cp.Problem(cp.Minimize(0.5 * cp.sum_squares(u - u_d) + PEN * d**2), g).solve()
    return u.value, d.value                         # log d > 0 as an infeasibility event
```

cvxpy with an SOCP solver goes in a sample-local venv (`uv venv`, `uv pip install`).

### 4.5 What our sim must provide

The state estimate, an error bound `epsilon(y)` per step (constant worst case to be faithful
to the papers; a PL is our variant), local Lipschitz constants, an SOCP solver, and the
obstacle geometry in the estimate frame.

## 5. Baseline => minimal faithful implementation for the kill test

| Baseline | Minimal faithful implementation | Inputs from the sim | Effort (our estimate) |
|---|---|---|---|
| PX4-CBF, paper form (FoV) | Section 1.7 plus the eq. 17 QP with two soft FoV constraints at +-45 deg, eq. 13 class-K, Table II parameters, 100 Hz filter, 15 Hz scans of <= 100 binned points | body-frame points, estimated body velocity, yaw, accel setpoint, tracking lag | 2 h if a QP solver is in the venv |
| PX4-CBF, as shipped | Section 1.7 as written (analytic, linear alpha, raw input, clamp after), label "fork `cbf` HEAD" | same | 1 h |
| Belief-CBF | Section 2.4 on the same EKF that the other arms use, covariance predicted every control step, Theorem 3 gamma, risk delta equal to our integrity risk, one constraint per nearby map obstacle | EKF mean and full covariance, Q, H, R, sensor rate, map obstacles | 2-3 h |
| gatekeeper | Section 3.4: N = 10 grid over T_S, 2 s horizon, brake backup, unknown = occupied, R measured from our tracker, keep last committed when none validates | nominal trajectory, occupancy grid with unknown, forward model, R, r | 3 h |
| MR-CBF | Section 4.4 with a constant worst-case `epsilon` measured offline against truth (Cosner practice), slack logged | estimate, epsilon, SOCP solver | 2 h |

Suggested extra arm for the kill test: MR-CBF with a fixed worst-case `epsilon`. If our PL arm
does not beat it on time to goal at equal breach rate, the PL adds nothing over a calibrated
constant bound.

**Measured since (synthetic):** the faithful constant worst case froze the vehicle. With epsilon =
0.99 m (worst per-run error on seed 1) MR-CBF reached B in 0 % of runs, with 13-18 % collisions
from QP slack. A swept 0.2 m bound held collisions at 1.0 % [0.3, 2.9] or less in every case on
seeds 0-2 and matched the PL arm's safety, which ended the headline
([safety-filter Part b](../../../samples/close-area-safety-filter/README.md#part-b-estimation-aware-baselines-ran-2026-11-09-synthetic),
[Part e](../../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).

## 6. Three places a naive implementation would be unfair to the baseline

1. **PX4-CBF without its FoV constraint, or with the wrong obstacle feed.** With a 90 deg fan,
   the analytic filter alone lets the vehicle slide sideways into what it cannot see. The
   authors flag this in section III and add eq. 17 for it. Run the FoV variant as the
   baseline. Feed it what it was tuned on: binned points at 10-15 Hz, filter at 100 Hz on
   the latest velocity, Table II gains rather than the PX4 parameter defaults, and an
   acceleration-tracking lag that the low-pass was tuned against.
2. **Belief-CBF with a weaker estimator or a static margin.** Give its EKF the same
   measurement sources our PL uses (the second source too) and the same standard innovation
   gate a shipped EKF has (PX4 `EKF2_EVP_GATE`; default not checked here). Propagate the
   covariance every control step so the filter brakes in dark zones before the update, add
   the Theorem 3 margin, and set delta to the same risk our PL is sized for. Otherwise the
   comparison measures sensors, gating and risk level, not the margin source.
3. **gatekeeper that panics instead of committing.** When no candidate validates, gatekeeper
   keeps tracking the last committed trajectory, which ends stopped inside known-free space.
   An implementation that hovers in place at once, treats unknown space as free, or uses a
   margin R not measured from our own tracker will look either unsafe or frozen for reasons
   that are not in the method. Count "stuck" separately and add the virtual-obstacle replan
   trigger the authors use.

## 7. Upstream findings (for docs/upstream-findings.md, not filed)

- PX4 fork `CBFSafetyFilter::updateObstacles()`: the trim loop
  `for (size_t i = _obstacles.size(); i >= num_points_total; i--) _obstacles.remove(i);`
  starts one past the last element, and with `num_points_total == 0` the `size_t` condition
  is always true. Read from code, not run.
- FoV QP at `338fb51f`: FoV constraints are written on the correction only, without the
  `e_j . a_sp` term that eq. 17c implies. On QP failure the slack debug fields read an
  uninitialised array.
- composite_cbf node declares `clamp_z` but reads `max_acc_z`, so the YAML value is never
  loaded; the default (3.0) equals the YAML value, so the effect is nil today.
- Paper 2504.15850: tau = 0.5 in Table II versus range [0.01, 0.1] in Table I.
- Belief-CBF paper: sign of eq. 6 and of the 1D example (section 2.2).

## 8. Not verified

Reconciled 2026-11-09 against
[close-area-safety-filter](../../../samples/close-area-safety-filter/README.md). Still open:

- The BCBF derivative terms, the MR-CBF Lipschitz shortcut and the use of `Lam` at the current
  covariance are ours. They now run in `filters.py`, but were not checked against the authors'
  code or results.
- Not built: the PX4-CBF FoV QP (eq. 17) and gatekeeper. The arena fan is 360 deg, so the FoV
  constraint would not bind there; a narrow-fan run was not done.
- PX4 behaviour (100 Hz loop, timeouts) is from code and the paper, not from SITL. The Python
  F2 arm runs at 50 Hz, not 100 Hz.
- Harms 2025 (ICRA) and Han 2025 (CDC) were read as abstracts only. The gatekeeper notebook,
  the BCBF follow-up code and cyberpod_sim_ros were not opened beyond README.
- Dean and Cosner appendices (proofs, SOCP standard form) were not read.
- Table II tau ambiguity and the meaning of the PX4 LP gains in seconds were not resolved.
- Records added for new sources: the CBF-baselines lane files in `data/resources/` and `data/repos/`.

### Verified since

All synthetic (2.5D point-mass arena, VIO-like EKF with injected faults), not SITL or flight.

- "No code was built or run" no longer holds for three arms. Section 1.7 (PX4-CBF as shipped,
  Table II gains), section 2.4 (Belief-CBF with covariance prediction and the Theorem 3 margin)
  and section 4.4 (MR-CBF with a fixed bound) run as F2, F3 and F4 in `filters.py`.
- Finding 2, jump half (a position jump does not touch PX4-CBF): with every obstacle visible, F2
  had 0 % collisions under jump, bias and dropout, 100 layouts per case
  ([part a](../../../samples/close-area-safety-filter/README.md#reading)). The velocity-bias half
  was not isolated: the arena's bias case (0.05 m/s for 10 s) also gave 0 %.
- Finding 4 (Belief-CBF is the strong covariance baseline): F3 removed most fault collisions but
  not jumps, 9 % on seed 0 and 8.0 % [5.0, 12.6] on held-out seeds; a jump is not in the
  covariance ([Part b](../../../samples/close-area-safety-filter/README.md#part-b-estimation-aware-baselines-ran-2026-11-09-synthetic),
  [Part e](../../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).

### Refuted since

- Section 5's faithful MR-CBF form (constant worst-case epsilon) as a usable arm: at 0.99 m it
  froze, 0 % reached (see the note under section 5).
