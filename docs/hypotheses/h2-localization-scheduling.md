# H2: request a localization fix before its navigation deadline

<!-- about: sample:navigation-innovation-lab, sample:e2e-visual-nav-vpair, res:catan-2022-robot-scheduling, res:scaramuzza-kaufmann-2023-agile-notes -->

Status: synthetic predictive trigger is competitive, but advantage over a strong
opportunity heuristic is not established. Slowing down is not generally beneficial.

## Failure and hypothesis

An accurate visual fix can arrive after the aircraft needs it. A fixed rate wastes
requests in poor imagery; a covariance threshold may react too late. Hypothesis:
predict uncertainty at delivery time and use upcoming route tolerances and expected
observation opportunities to schedule computation, optionally changing speed.

## Closest work and proposed difference

[Catan](https://experts.illinois.edu/en/publications/on-device-cpu-scheduling-for-robot-systems/)
already schedules robot computation dynamically. [Scaramuzza and Kaufmann's notes](https://realworldrobots.github.io/assets/files/Learning_Agile.pdf)
explain perception-to-action latency and error propagation in flight pipelines.
Active sensing and belief-space planning are established, so the broad idea is not new.

Potential difference: an explicit mission-dependent deadline for the value of an
absolute fix, jointly considering capture opportunity, arrival uncertainty and speed.
The current POC is a heuristic approximation, not a solved optimal scheduling problem.
The research handoff must locate closer sensing/planning co-design baselines.

## POC boundary and algorithm

A 120-m synthetic route has two tight localization-tolerance regions and one poor
imagery region. One-dimensional position-estimate error follows a random walk. Fixes
have noisy captures, delayed arrival, and failed matches. Every policy has at most
10 requests and one outstanding job. Delayed corrections preserve post-capture noise.

The predictive trigger forecasts a `2*sigma/tolerance` proxy at arrival and along an
eight-second horizon, and also requests before a good observation opportunity closes.
It does not know actual future fix success or delay jitter. A speed variant halves
speed when the proxy exceeds one. This is not a calibrated protection level.

Input exposure: current covariance, location along the route, age of last request,
outstanding-job status, budget, nominal latency, route tolerance/opportunity model.
Truth, realized errors, outcome draws and future process noise are evaluator-only.

This is estimator-error replay in a stochastic world, not a flight controller.
Exceeding tolerance is not a collision. Geometry is fixed across seeds. CPU costs
are represented by request count and artificial latency, not measured energy/CPU.

## Baselines and falsification

Tune periodic intervals, covariance thresholds, and a simpler opportunity heuristic
on the same development cases. Compare predictive fixed speed, predictive slowdown,
and an ablation that ignores latency. Baselines share the same maximum budget; report
actual requests as well, since equal caps do not imply equal compute consumption.

Falsification: if opportunity timing alone matches the predictive method, the added
uncertainty machinery has not demonstrated value. If slowdown increases error exposure
or duration without a corresponding benefit, reject the speed rule.

## Measured result and decision

For 100 held-out nominal seeds, predictive fixed speed completes without tolerance
violation in 64% versus 54% for a covariance threshold (paired difference +0.10,
95% bootstrap interval [0.02, 0.19]). But its difference from the simpler opportunity
policy is -0.03 [-0.09, 0.03]. Mean requests: 6.93 predictive versus 10 threshold.
This is promising efficiency evidence only under the synthetic assumptions.

Slowdown completes nominal routes in about 73.62 s versus 48 s, with 55% success;
under unexpected blackout it achieves 20% versus 35% for predictive fixed speed.
The model accumulates error with time: slowing down can make localization worse.

Source: [all scenarios, tuning and comparisons](../../samples/navigation-innovation-lab/results/report.md).
Decision: keep predictive fixed speed and the opportunity baseline; do not pitch the
slowdown rule as an improvement. Test recorded VO/fixes with artificial capture/arrival
separation, then measured onboard runtimes and route variability. A fixed-flight replay
cannot validate speed changes, avoided collisions or real compute savings.

## Cached-flight follow-up (same day)

The [48-case VPAIR replay](../../samples/navigation-innovation-lab/replay-results/report.md)
uses causal single-frame cached matching, a ten-frame calibration window and a
simple delayed-update VO-offset filter. It confirms no consistent predictive win:
for map stride 1, Q=16 and delay 2 frames, threshold / periodic / predictive RMSE is
61.86 / 73.14 / 108.02 m. Read all cases, including those favoring other policies.

These are one flight's derived measurements, not independent test flights. There
are no physical timestamps; artificial delay is measured in frames. Calibration,
map and truth are not independent. The filter omits the sibling's heading/scale
states and changing attitude correction, and can reject useful fixes when its
covariance proxy understates drift. Therefore the replay is an integration/failure
probe, not a clean head-to-head estimator or scheduling benchmark. Before claiming
value, use the validated sibling estimator, actual timing and additional flights.
