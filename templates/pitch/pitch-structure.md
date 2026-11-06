# Pitch structure

Two skeletons (3 and 5 minutes) for a PNT-resilience pitch, the funder vocabulary to use and
not to stretch, and 15 hard judge questions with answer patterns. Hub numbers below are copied
from [evidence-matrix.md](../../docs/evidence-matrix.md) with their input label; replace them
with your own measured numbers wherever you have one.

Contents: [The five beats](#the-five-beats) - [3-minute skeleton](#3-minute-skeleton) -
[5-minute skeleton](#5-minute-skeleton) - [Worked example](#worked-example-spoof-on-a-small-uas-3-min) -
[Funder vocabulary](#funder-vocabulary-without-overclaiming) - [Judge questions](#judge-questions)

## The five beats

| Beat | Job | One line you must be able to say | Fails when |
|---|---|---|---|
| 1. Problem | Name the threat and the platform in the brief's own words | "When GNSS is [jammed / spoofed] on a [platform], [what goes wrong]." | It is generic ("GPS is vulnerable") |
| 2. Why it matters operationally | Show the consequence for the user, with one hub number as context | "Today, [the autopilot / receiver / operator] [does X]: [number, label]." | The number is yours but from the hub, or has no label |
| 3. Live demo | Attack => alarm => continued navigation => failure case | "Watch the [alarm / uncertainty ring / source switch] at [time]." | It needs network, typing, or luck |
| 4. Honest numbers | Your measured result vs a baseline, with ground truth and run count | "[Ours] vs [baseline], [N runs], [label]. Not measured: [X]." | Only the good number is shown |
| 5. What's next | The next three steps to a field test, and the scope line | "Next: [real data / hardware / longer runs]. Defensive only, no transmission." | It asks for money before it shows a gap |

The order matters. Judges decide in the first 30 s whether you understand the problem; the
honest-numbers beat is what separates you from the vendor brochure they have already read
([landscape](../../docs/landscape/README.md#what-is-commoditized)).

## 3-minute skeleton

| Time | Beat | Say | Show |
|---|---|---|---|
| 0:00-0:20 | Problem | Hook from [story-bank.md](story-bank.md) (one sentence) + the platform and user from the brief | Title slide with the hook's figure |
| 0:20-0:40 | Why it matters | The hook's number with its label: "in SITL, one flight" / "on a real recorded flight" | Problem slide |
| 0:40-1:00 | What we built | One sentence per box: sources => integrity check => filter => output (TAK / GCS / autopilot). Say which boxes are real, which are stubs | Architecture slide |
| 1:00-2:00 | Live demo | Attack starts, alarm fires, source switch or exclusion, uncertainty grows honestly, one failure case | Demo dashboard ([demo-script.md](../demo-script.md)) |
| 2:00-2:35 | Honest numbers | Ours vs baseline, run count, label, ground truth; one "not measured" | Numbers slide |
| 2:35-3:00 | What's next | Three next steps, the scope line, team | Next slide |

Cut order if you are over time: the architecture beat shrinks to one sentence first; the
honest-numbers beat never shrinks below "ours vs baseline, N runs, label".

## 5-minute skeleton

| Time | Beat | Say | Show |
|---|---|---|---|
| 0:00-0:30 | Problem | Hook + brief wording + who uses it | Title |
| 0:30-1:10 | Why it matters | Two hub numbers: what the current system does (story bank) and what that costs the user (distance off, time to failsafe, alarm rate). Labels on both | Problem + consequence slides |
| 1:10-1:40 | What we built | Architecture, what is real vs stub, how it plugs into what the user already runs (MAVLink, CoT, NMEA, UBX) | Architecture |
| 1:40-3:10 | Live demo | Same as 3-min, plus the failure case run on purpose: the attack you do not catch | Dashboard |
| 3:10-4:10 | Honest numbers | Results table: ours vs baseline vs the hub's reference sample, run counts, labels; one row of "not measured"; the threshold you chose and on what data | Numbers + limits slides |
| 4:10-4:40 | Deployability | Hardware class, CPU timing you measured, how a field user retunes it, AI off switch if any | Deployability line |
| 4:40-5:00 | What's next | Next three steps, scope line, ask (data access, test range slot, mentor) | Next |

## Worked example: spoof on a small UAS (3 min)

Shows the shape, using only hub numbers. In your pitch, beats 4 and 5 carry your numbers.

- **0:00 Problem.** "A small drone under a slow GNSS spoof does not crash. It flies
  confidently to the wrong place."
- **0:20 Why it matters.** "In SITL, both open autopilots reset onto a spoofed GNSS offset
  after 7.3 s (PX4) and 10.1 s (ArduPilot), one flight per config
  ([autopilot-spoof-response](../../samples/autopilot-spoof-response/README.md#step-offset-position-jumps-at-onset-velocity-untouched)).
  PX4 reported 0.22 m position uncertainty while it was 106 m off
  ([golden-demo-px4](../../samples/golden-demo-px4/README.md#result-ran-2026-11-06-one-flight-each-seed-7))."
- **0:40 What we built.** "A companion monitor that compares GNSS velocity with a GNSS-free
  reference and, on alarm, switches the autopilot to that reference."
- **1:00 Demo.** Dashboard: drag starts, alarm, source switch, the no-monitor track walking off.
- **2:00 Numbers.** "Hub reference, SITL, one flight per mode: 6.8 m max cross-track with the
  monitor vs 75.0 m without
  ([golden-demo v2](../../samples/golden-demo/README.md#v2-reference-run-ran-2026-11-06-one-run-each-seed-7-speedup-1)).
  Ours: [your number, your runs, your label]. Not measured: real flight, real VIO."
- **2:35 Next.** "Replay on a real recorded flight; second absolute source; one bench test on
  a real receiver with cabled signals. Defensive only, no transmission."

## Funder vocabulary without overclaiming

Funder words come from [programs-and-challenges.md](../../docs/landscape/programs-and-challenges.md)
and the [playbook](../../docs/hackathon-playbook.md#1-what-judges-reward). Use the words; claim
only what the right-hand column allows.

| Funder says | Source | You can honestly claim | Do not claim |
|---|---|---|---|
| Detect, respond, recover | [NISTIR 8323](../../catalog/resources/nist-ir-8323-pnt-profile.md), [DHS RPNT framework](../../catalog/resources/dhs-resilient-pnt-conformance-framework.md) | "Detects [X] in [N runs, label]; responds by [source switch / exclusion]; recovers by [re-validation rule]" | A DHS resilience level, unless you ran their conformance tests |
| Multi-source fusion, AI for spoofing detection | [DASA PNT problem statement](../../catalog/resources/uk-dasa-emp-pnt-problem-statement-2024.md), [EDF 2024](../../catalog/resources/edf-2024-drone-navigation-challenge.md) | "Fuses [list] and refuses a source when [test]"; if a model is involved, what it was trained and tested on | "AI-powered" with no false-alarm rate |
| Plug-in replacement for COTS GNSS | DASA | "Feeds [autopilot] via [`GPS_INPUT` / external vision] in SITL" | "Drop-in for any receiver" |
| Small, cheap, many | DASA, EDF, Brave1 ([patterns](../../docs/landscape/programs-and-challenges.md#patterns-in-the-problem-statements)) | Hardware class from the [playbook shopping list](../../docs/hackathon-playbook.md#64-hardware-shopping-list-cost-class-only) and the CPU time you measured | A unit cost or power draw you did not measure |
| Deployable, testable, dual-use | [NATO DIANA](../../catalog/resources/nato-diana-10-challenges-2025.md) | Civil twin (aviation, shipping, timing) and the test you ran | "Field-proven", "TRL 6" |
| Non-lethal / robust navigation | [Brave NATO UNITE](../../catalog/resources/brave-nato-unite-2026.md) | Navigation, integrity and awareness only | Anything near targeting or terminal guidance |
| Integrity, protection level | [integrity guide](../../docs/integrity-monitoring.md) | "PL from [method] over [N epochs], 0 HMI observed" | "Certified", "1e-7 integrity risk": a few thousand epochs cannot show that |

Words that lose points with practitioners: "spoof-proof", "jam-proof", "works anywhere",
"centimetre accuracy without GPS", "military-grade". The [landscape](../../docs/landscape/README.md#what-to-avoid)
lists what judges already treat as solved or for sale.

## Judge questions

15 questions to rehearse, each with an answer pattern and the hub evidence behind it. Pattern =
the shape of a good answer; fill the brackets with your project. Evidence labels as in the
[README](README.md#rules-for-numbers-non-negotiable). Rehearse with a timer: 20 s per answer, then stop.

### 1. "What happens if both sources fail?"

Pattern: name the state you enter (integrity unavailable, not "still fine"), what the vehicle
does (loiter, RTH on dead reckoning, land), and how fast the uncertainty grows.

Evidence: two sources detect a fault but do not identify it; on the VPAIR flight the blame
followed the monitor order (wrong 10/10 one way, right 10/10 swapped), and a third source that
shares parts with the second excluded the wrong source in 19 of 20 runs, `[mixed]`, 10 seeds per
row ([two-source-integrity-vpair](../../samples/two-source-integrity-vpair/README.md#fault-injection)).
Pure dead reckoning on a fixed-wing: 844 m cross-track after 20.8 km, `[SITL]`, one flight
([golden-demo-fixedwing](../../samples/golden-demo-fixedwing/README.md#what-this-says)). Say
"we declare unavailable and show the growing radius" before anyone asks.

### 2. "Is that SITL or real?"

Pattern: answer with the label first, then the gap. "SITL: real autopilot firmware, simulated
sensors. Not tested: [real IMU noise, wind change, real VIO]." Then point at your one real-data
element if you have one.

Evidence: the hub's real-data anchors to cite as "what the same method does on recorded data":
VPAIR flight (VO only 156 m RMS => 4.8 m with gated fixes, `[real]`, one flight,
[e2e-visual-nav-vpair](../../samples/e2e-visual-nav-vpair/README.md#heading-2-deg-the-realistic-case-ahrs-heading-error)),
Jammertest logs (20 of 20 attack slots alert, `[real]`,
[real-attack-replay](../../samples/real-attack-replay/README.md#results)). Never round a SITL
number into "we showed".

### 3. "How does this scale?"

Pattern: say which axis (more vehicles, larger area, more sensors, longer mission) and give the
one measurement you have on that axis; say the rest is not measured.

Evidence: jammer localization with more cheap nodes, median error 602 / 313 / 173 m for 4 / 16 /
32 nodes (grid Bayes), `[synthetic]`, 40 trials per row
([jammer-sensor-network](../../samples/jammer-sensor-network/README.md#monte-carlo-evaluatepy-40-trials-per-row-one-10-s-snapshot-of-static-nodes)).
Large-area retrieval: search under 1 ms over a 49 km2 database, descriptor 19-39 ms (MPS),
`[synthetic]` queries ([vpr-large-area](../../samples/vpr-large-area/README.md#retrieval-db-2023-250-m-tiles-queries-cut-from-the-same-2023-imagery)).
Swarm bandwidth 138.1 vs 24.0 B/s per agent (centralized vs covariance intersection),
`[synthetic]` ([swarm-coop-localization](../../samples/swarm-coop-localization/README.md#results-10-seeds)).

### 4. "What about export control?"

Pattern: four facts, no legal claims. "Public civil signals only. Published methods and public
data. No over-the-air transmission: spoofing is injected in software or into files. Repo is
[public / private, and if private, who has access]." Add: "We are not lawyers; we followed the
hub's checklist and would ask our export office before any defense integration."

Evidence: [export-control-and-ethics.md](../../docs/export-control-and-ethics.md#7-checklist):
published code is generally outside the EAR, private sharing with foreign nationals can be an
export, OSNMA-style authentication code is worth an encryption check.

### 5. "What does it cost, and what is the SWaP?"

Pattern: hardware class, the CPU time per update you measured, and "power draw not measured"
if it was not. Never invent a unit price.

Evidence: CPU timings that exist in the hub (all on a laptop, not an embedded board): ALIKED +
LightGlue 1.43 s per frame on CPU ([geoloc-license-clean](../../samples/geoloc-license-clean/README.md#measured-results-ran-2026-11-06)),
~0.73 s per frame for the whole VPAIR chain on an M2 with MPS
([e2e-visual-nav-vpair](../../samples/e2e-visual-nav-vpair/README.md#heading-2-deg-the-realistic-case-ahrs-heading-error)),
terrain PF update ~1.1 ms (M2 Max)
([terrain-heightmap-pf](../../samples/terrain-heightmap-pf/README.md#results-ran-2026-11-06-cpython-31315-apple-m2-max-single-python-process)),
star plate solve ~25-30 ms per 1 MP frame
([celestial-star-tracker](../../samples/celestial-star-tracker/README.md#1a-accuracy-against-a-known-wcs)).
Hardware cost classes: [playbook 6.4](../../docs/hackathon-playbook.md#64-hardware-shopping-list-cost-class-only).

### 6. "What is your false-alarm rate?"

Pattern: false alarms over how many hours or flights, on what data, with thresholds set on
which runs. If it is a handful of runs, say "smoke test".

Evidence: chi-square false-alarmed in 4 of 4 no-spoof flights, solution separation and the
velocity test in 0 of 4, `[SITL]` ([golden-demo v2 MC](../../samples/golden-demo/README.md#v2-monte-carlo-ran-2026-11-06-52-flights)).
On real logs the interference scorer raised 1-6 alarms per hour in unlogged time, `[real]`
([real-attack-replay](../../samples/real-attack-replay/README.md#results)). The cost of one
false alarm: a fixed-wing that switched to dead reckoning on a false alarm was 899 m off 688 s
later, `[SITL]`, one flight ([golden-demo-fixedwing](../../samples/golden-demo-fixedwing/README.md#what-this-says)).

### 7. "Why not just use the autopilot's own GNSS checks?"

Pattern: the built-in gate rejects a jump, then times out and accepts it; a slow coherent
drag never trips it. Show the number, then what your monitor adds.

Evidence: every config believed 96-110 % of a coherent drag offset; tighter gates added LAND
failsafes without reducing capture, `[SITL]`, 30 flights one per cell
([autopilot-spoof-response](../../samples/autopilot-spoof-response/README.md#coherent-drag-position--velocity-rate-sweep)).
The best onboard recipe (ArduPilot Lua applet) was safe 6/6 at 1-3 m/s but caught 0/3 at
0.3 m/s, `[SITL]` ([autopilot-resilient-configs](../../samples/autopilot-resilient-configs/README.md#ranked-recipe-table)).

### 8. "Ten vendors already sell visual navigation. What is new?"

Pattern: do not compete on accuracy. Compete on knowing when the fix is wrong, measured on
open data, failure cases included.

Evidence: no vendor publishes a false-alarm or missed-detection rate
([landscape](../../docs/landscape/README.md#where-a-hackathon-team-can-still-add-something)).
On the real VPAIR flight a loose matcher without a filter gate fused 15 false fixes and the
RMS error went to ~12 km; with the chi-square gate 0 false fixes were fused, `[real]`, one
flight ([e2e-visual-nav-vpair](../../samples/e2e-visual-nav-vpair/README.md#heading-2-deg-the-realistic-case-ahrs-heading-error)).

### 9. "Does it work at night, over water, over flat terrain?"

Pattern: name the condition you tested and the one you did not. Have one number for the hard
case.

Evidence: thermal frames vs an RGB map, best config 18 / 111 fixed, night fog 0 / 14, `[real]`
([thermal-geolocalization](../../samples/thermal-geolocalization/README.md#fix-rate-and-error-per-condition-revised-gate-mps-6-main-flights)).
USV under spoofing: 10-25 m max error near the coast vs 71-102 m in open water, `[synthetic]`,
5 seeds ([usv-gnss-denied-nav](../../samples/usv-gnss-denied-nav/README.md#results-5-seeds-real-outputs)).
Terrain PF at 10 km: hilly 12 m median, flat 25 m median with p90 130 m, `[synthetic]` over
real GLO-30 terrain ([terrain-heightmap-pf](../../samples/terrain-heightmap-pf/README.md#1-information-gate-never-worse-than-odometry-on-flat-terrain)).

### 10. "Does your tuning transfer to new data or an old map?"

Pattern: say which data set the thresholds and which data tested them, and give the held-out
number even if it is worse.

Evidence: 4 scorer parameters were chosen on 3 Jammertest logs with a 4-log holdout, and the
holdout is clean for parameter values, not for the choice of mechanisms, `[real]`
([gnss-interference-monitor](../../samples/gnss-interference-monitor/README.md#real-data-evaluation-jammertest-2024)).
Map age: retrieval R@1 within 50 m drops from 0.77 to 0.18-0.29 with a 2-8 year map gap,
`[synthetic]` queries ([vpr-large-area](../../samples/vpr-large-area/README.md#retrieval-by-condition-map-vintage-gap-and-tile-size));
real eBee frames vs NAIP: 1 of 5 fixed, `[real]`, 5 frames
([geoloc-license-clean](../../samples/geoloc-license-clean/README.md#what-the-real-frame-result-says)).

### 11. "How does a field user retune it, and how do we turn the AI off?"

Pattern: thresholds and sources in one config file, a documented default; every learned or LLM
component has a log, a confidence and an off switch that falls back to a classical estimator
or a human.

Evidence: [export-control-and-ethics.md section 5](../../docs/export-control-and-ethics.md#5-responsible-ai-principles)
(traceable, governable, explainable mapped to navigation practice). The hub's MCP vehicle agent
was verified with a scripted client in SITL, no LLM run (`[SITL]`,
[llm-mission-agent](../../samples/llm-mission-agent/README.md#what-was-verified-2026-11-06)):
say the same about yours if it is true.

### 12. "What is your integrity risk? Can this be certified?"

Pattern: give the PL method and the epochs observed; say plainly what that cannot show.

Evidence: 0 HMI over ~1,900 epochs "says nothing about 1e-5 risk"
([two-source-integrity-vpair](../../samples/two-source-integrity-vpair/README.md#results));
12 000 epochs per row cannot validate integrity risk below ~1e-4
([altpnt-integrity v2](../../samples/altpnt-integrity/README.md#3-monte-carlo-python3-altpnt_v2py---runs-20-182-s-resultsv2_mcjson)).
And the calibration lesson: altpnt v1's 0 MI did not survive error models measured on real runs
(MI* 74 % of epochs with the same filter), `[synthetic]` flight with error models fitted on
real runs ([altpnt-integrity](../../samples/altpnt-integrity/README.md#4-what-changed-vs-v1-honestly)).

### 13. "What about a slow spoof that stays under your threshold?"

Pattern: give your slowest detected rate and the first undetected one. That boundary is a
result.

Evidence: only the external companion monitor caught a 0.3 m/s drag (PX4, 44-51 s), `[SITL]`
([autopilot-resilient-configs](../../samples/autopilot-resilient-configs/README.md#ranked-recipe-table)).
A 2D GNSS/INS EKF gate never caught 0.05-0.5 m/s drags, `[synthetic]`, one seed
([gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/README.md#expected-output-observed-python3147-2026-11-06)).
A coherent drag is invisible to a Doppler-only reference by design; it needs an IMU, odometry
or a "parked" reference, `[synthetic]`
([gnss-interference-monitor](../../samples/gnss-interference-monitor/README.md#run-verified-part)).

### 14. "What happens after the attack ends?"

Pattern: re-validation on GNSS return, not only detection on loss; say how long you wait and
what you check.

Evidence: forged OSNMA data after authentication stayed "authenticated" for 10 min (same IOD),
`[mixed]`: real recording, manipulated in memory
([osnma-authentication](../../samples/osnma-authentication/README.md#results-on-the-real-recording-ran-2026-11-06)).
Post-processing with the receiver-decoded nav file gave a 276 km median error in every day-12
window, because spoofer ephemerides were kept, `[real]`
([real-attack-replay](../../samples/real-attack-replay/README.md#rtklib-spp-during-the-attacks)).

### 15. "What if the datalink is jammed at the same time?"

Pattern: say whether you tested it. If not: "not tested; the onboard part runs without the
GCS, and the defined behaviour is [loiter / RTH]". If yes, show it.

Evidence: the hub has no measured GNSS + link loss run; the playbook lists it as a
differentiator ([playbook 1.1](../../docs/hackathon-playbook.md#11-differentiators-judges-have-not-seen)).
Nearest: an ArduPilot GPS cut without a source switch coasted ~6 s, then LAND failsafe, with
~3.6 m dead-reckoning error the EKF had not reported, `[SITL]`, one flight
([ardupilot-ekf3-source-switch](../../samples/ardupilot-ekf3-source-switch/README.md#contrast-run-gps-cut-without-the-source-switch)).
