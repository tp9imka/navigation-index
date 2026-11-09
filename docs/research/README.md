# Research rounds: which one applies, and the innovation story per brief

Use this when you need the innovation story, want to know which research round fits the brief,
or need the kill test and status for a headline idea.

**close-area-nav is the default frame; innovation-prior-art is the long-range fallback.**
Both rounds are prior-art research. The lane docs themselves ran nothing. The close-area
baseline samples listed below did run, on synthetic inputs only.

## The two rounds

| Page | Use it when | You get |
|---|---|---|
| [close-area-nav/](close-area-nav/README.md) (round 2, 2026-11-09, follow-up docs 05-09 the same day) | The brief says A to B, obstacles, indoor, arena, close area, or a marker / pad at B. This is the likely Day-1 task. | Baseline planner, sims, local localization, Crazyflie sensing limits, how events phrase the task, and the headline (integrity-aware safety filter) with its kill test |
| [innovation-prior-art/](innovation-prior-art/README.md) (round 1, 2026-11-09) | The brief is long range: km-scale legs, GNSS jammed or spoofed, fixed-wing, terrain or visual fixes | Prior art, strongest baseline and a falsifier for three long-range ideas, plus a ten-direction scan |

Round 2 replaced round 1 as the default after the news that the task is likely "move a drone from
A to B in a close area" ([close-area-nav README](close-area-nav/README.md), first paragraph). For
the long-range pitch shape, see also [Challenge 2 section 5](../challenge-2-autonomous-flight.md#5-what-the-pre-day-1-research-added).

## Brief family => headline idea => kill test => status

| Brief family | Headline idea | Kill test | Status |
|---|---|---|---|
| Close-area A=>B (default) | **Integrity-aware safety filter**, narrowed by [07](close-area-nav/07-pl-margin-prior-art.md): range barriers for what the drone sees, a protection-level margin for what it cannot, hover when the monitor cannot tell which source is lying | [04 section 3.4](close-area-nav/04-innovation-prior-art.md#34-falsification-experiment): 200 layouts, injected VIO jump and bias. Pass: breaches <= 1 %, >= 3x lower than Belief-CBF, goal reach >= 90 % of PX4-CBF. Fail: Belief-CBF within 1 pp, or PX4-CBF alone <= 1 %. Arms as read in full in [05](close-area-nav/05-cbf-baselines-faithful.md) | **Verdict after held-out seeds (Part e, synthetic):** FAIL. A hand-tuned fixed bound (MR-CBF 0.2 m) stays at <= 1 % collisions in every case on seeds 0-2; ours (F5, PL margin + hover on ambiguity) collides in 2.5 % [1.1, 5.7] of held-out jump runs and reaches B less often. Headline moves to relocalization after VIO loss; the range filter under any planner and the integrity monitor remain supporting results ([close-area-safety-filter](../../samples/close-area-safety-filter/README.md)). Baseline that ran: [close-area-arena](../../samples/close-area-arena/README.md) (synthetic) |
| Close-area A=>B, support piece | **Replan trigger** (04 idea A): sustained filter intervention or a protection level above half the corridor => replan on an inflated grid with a speed cap | [04 section 1.4](close-area-nav/04-innovation-prior-art.md#14-falsification-experiment-python-no-hardware): pass if collisions <= 1 % per fault case, >= 3x lower than a covariance margin on jump and bias, and median time to goal >= 15 % shorter than fixed worst-case inflation. Fail if the range-only filter alone is <= 1 % everywhere | Not built |
| Long-range multirotor, GNSS lost | **Drag-aided velocity filter** with an identifiability gate ([differentiators-scan 2.1](../differentiators-scan.md#21-propulsion-and-drag-as-a-virtual-velocity-sensor) + [round 1 doc 03](innovation-prior-art/03-identifiability-gated-aero-adaptation.md)) | [03 section 5](innovation-prior-art/03-identifiability-gated-aero-adaptation.md#5-falsification-experiment-48h): in the cells with the drag prior at 0.7x / 1.3x truth and wind >= 3 m/s, the gated filter's median 120 s error <= 0.75x the better of phase-based Schmidt (Laupre 2023) and always-adapt. Fail: within 10 % of phase-based Schmidt | Not built in this checkout. The innovation lab's synthetic H3 model (branch `feat/innovation-pocs`) helped only after an observable change |
| Long-range with visual fixes | **Calibrated trust for visual fixes** ([round 1 doc 04, direction 1](innovation-prior-art/04-wider-innovation-scan.md#21-conformal-acceptance-and-error-radius-for-learned-visual-fixes)) | Pass: false-discovery rate <= 0.10 and 90 % radius coverage >= 0.85 on both test splits, 0 false fused fixes. Fail: day-to-night coverage < 0.80 | Not built |
| Long-range terrain navigation | **Terrain filter that knows it is lost** ([round 1 doc 04, direction 2](innovation-prior-art/04-wider-innovation-scan.md#22-integrity-from-a-multimodal-posterior-with-a-missing-hypothesis-test)) | Pass: 0 HMI epochs over all runs including diverged ones, availability >= 50 % on straight flights. Fail: any HMI, or availability < 20 % | Not built |

All thresholds are proposals from the linked docs. Ideas 01-02 of round 1 (disambiguating
maneuvers, deadline-aware fix scheduling) were judged narrow and are parked.

## What has run for the close-area frame (synthetic only)

From [evidence matrix section 14](../evidence-matrix.md#14-close-area-ab). Every row there is a
2.5D point-mass arena or rendered images, not SITL or flight.

- [close-area-arena](../../samples/close-area-arena/README.md): A* + ESDF reached 100 % on
  known maps (random, u_trap, narrow_gap; 50 layouts each). Under estimator faults, range-only
  planners had 0 % collisions in every case and lost reach instead (freest_beam 86 % => 40 %
  under bias).
- [close-area-planner-reactive](../../samples/close-area-planner-reactive/README.md): with a
  4-beam fan, APF collided in 8-54 % of runs and VFH+ in 72-98 %.
- [fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/README.md): final approach 50/50
  seeds within 0.1 m of the goal.

What this means for the headline: when the range sensor sees every obstacle, range-only
planners stayed collision-free under faults. The filter can only win on obstacles the sensor
cannot see: map-only poles, the geofence, and the Crazyflie's blind wedges. Per
[08](close-area-nav/08-crazyflie-sensing-limits.md), its 4 beams cover 30 % of the circle. Doc 04
section 3.4 already includes map-only poles and a geofence box. Those cases carry the claim; if
they are dropped, the "PX4-CBF alone <= 1 %" fail branch is likely.
