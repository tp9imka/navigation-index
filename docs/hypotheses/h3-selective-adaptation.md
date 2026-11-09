# H3: adapt a navigation model only when the data identify it

<!-- about: sample:navigation-innovation-lab, repo:sjtu-visys-team/ai-io, res:hattenberger-2022-estimating-wind, res:ni-2026-active-model-discrimination -->

Status: conditional synthetic benefit after observable model change. Not a new
identification principle, not a complete inertial navigation algorithm.

## Failure and hypothesis

During steady flight, wind, accelerometer bias and drag changes can explain similar
residuals. Unrestricted adaptation can fit the wrong parameter. Hypothesis: only update
parameters supported by excitation and a trusted external reference, otherwise freeze
them and preserve uncertainty rather than manufacture confidence.

## Closest work and proposed difference

[AI-IO](https://arxiv.org/abs/2603.00597) already uses rotor measurements and inertial
data for aerodynamic odometry. [Hattenberger et al.](https://journals.sagepub.com/doi/10.1177/17568293211070824)
discuss online drag estimation and the conditions making it observable.
[Ni et al.](https://arxiv.org/abs/2606.19590) actively choose inputs to distinguish
candidate dynamical models with constraints. These are foundations and close prior art.

The potential contribution would be a practical policy selecting parameters and
calibration opportunities under intermittent references. The POC implements only
gated regression for an identifiable parameter pair. It does not select calibration
motions, infer reference health, estimate rotor dynamics, or implement the cited methods.

## POC boundary and identifiability

One-axis synthetic relation: `a = -k * v_ground + c`, where `c = k * wind + bias`.
Vary ground velocity and regress k/c on a 24-sample window. Reject windows with
insufficient velocity variance or implausible k. Clear the window when reference
measurements disappear. Ground truth is used only to generate data and score estimates.

Only k and c are identifiable here. Different wind/bias pairs produce exactly the
same measurements; a unit test verifies that symmetry. No claim of independent wind
and IMU-bias estimation is possible. Availability is supplied, but health of an
available reference is assumed. Constant-velocity motion does not identify k.

The plant is an algebraic quasi-steady drag relation with noise and some deliberately
unmodeled terms; it is not a self-consistent flight dynamics simulation. The final
80-second reference-free tail tests velocity error and its integrated position error.
There is no covariance or calibrated uncertainty bound in this POC.

## Baselines and falsification

Fixed initial parameters; calibrate once using the first 60 samples then freeze;
always-adapting regression; selective adaptation; removal of either excitation or
reference gating. The always-adapting ablation substitutes its own velocity estimate
when reference is absent, explicitly demonstrating circular self-training.

One-time calibration is the strongest ordinary baseline, not the intentionally weak
initial model. Tune the gate on nominal/no-excitation development seeds. Hold out
parameter-change, reference-outage, nonlinear-drag and late-unobserved-change scenarios.

Reject a general superiority claim if initial calibration is competitive. Reject
recovery claims for changes occurring after informative reference evidence disappears.

## Measured result and decision

Across 100 held-out seeds, after a parameter change while a reference and excitation
are available, selective velocity RMSE is 0.2465 m/s versus 2.2660 for initial calibration
and 0.4067 for always-adapting regression. In nominal conditions, initial calibration
is better: 0.3433 m/s versus 0.3579 selective. When the parameter changes after the
reference disappears, both fail: 2.0080 versus 2.1158 m/s respectively.

No-excitation selective adaptation makes zero updates and preserves the inaccurate
prior. This is honest refusal to learn, not successful navigation. Nonlinear drag can
give low velocity error near the tested speed while k is wrong; prediction accuracy
must not be mistaken for recovered physical parameters.

Source: [complete results](../../samples/navigation-innovation-lab/results/report.md).
Decision: pursue only the changing-aircraft/intermittent-reference case, with independent
data and a stronger system-identification baseline. Physics and learned estimators
sharing IMU/rotor telemetry have correlated errors; their agreement is not an independent
integrity certificate. See the completed [differentiator lane](../differentiators-scan.md).
