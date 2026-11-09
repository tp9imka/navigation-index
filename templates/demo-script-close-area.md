# Demo script: close-area A to B

Live-demo variant of [demo-script.md](demo-script.md) for the close-area task: fly from A to B
through obstacles, with a VIO fault injected. It fits the 3-minute skeleton in
[pitch/close-area-story.md](pitch/close-area-story.md#4-3-minute-skeleton). One driver, one
narrator. The driver never types free text on stage: every step is a command in shell history
or a key press.

State on 2026-11-09: the arena and kill test parts a, b and d ran (synthetic, seed 0,
[close-area-safety-filter](../samples/close-area-safety-filter/README.md)). Ours (F5) had 0 %
collisions but failed the reach bar (61-89 % of PX4-CBF's reach, bar 90 %); a held-out rerun was
still running. If the kill test FAILs, the story pivots to relocalization (H1) and this script
uses the [H1 variant](#h1-relocalization-the-pivot), which has a real seed and command.
A replay of arena runs is in `site/showcase.html`. Commands in `<angle brackets>` are the team's
own; write them on Day 1.

## What the demo shows

Two arms, same layout seed, same injected fault, side by side:

- **Left: baseline.** The planner + a covariance-margin filter (Belief-CBF style). If the kill test
  showed the range-only arm is the stronger baseline, put that on the left instead.
- **Right: ours.** Same planner + our filter (range barrier + margin from the nav monitor + speed
  cap + hover fallback).
- **The event:** a VIO jump or bias starts near a map-only obstacle (thin pole or geofence box)
  that the range sensor does not see. Pick the seed in advance from the kill-test runs. Do not
  hunt for a good seed on stage.

Every frame carries its input label in a corner: `[synthetic]` for the light sim, `[SITL]` for
PX4 / ArduPilot SITL, `[real]` only for a real flight.

If the story switched to an alternative hook ([close-area-story.md section 3](pitch/close-area-story.md#3-alternative-hooks-if-the-kill-test-fails)),
use the variant rows at the end of the script.

## Setup (T-30 min)

- [ ] Demo laptop on mains power, sleep and notifications off, mirrored on the venue projector.
- [ ] Tests green on the demo laptop (`<test command>`). Paste the tail into the team chat.
- [ ] Sim view open: two panes, top-down, A and B marked, the map-only obstacle drawn in a
      different colour from sensed obstacles, range-sensor field of view drawn as a wedge.
- [ ] Status strip visible under each pane: nav health (ok / degraded / lost), current margin in m,
      speed cap in m/s, filter active yes / no.
- [ ] Results table and one plot open in a tab (from `runs/results.md`).
- [ ] Backup video open in a paused player on this laptop AND on laptop 2.
- [ ] Network: assume none. Everything runs from localhost.
- [ ] Real flight only: the organisers' safety rules win. Named safety pilot with the kill switch,
      net or geofence checked, battery checked. A safety-pilot touch counts as an intervention
      (IMAV scores any manual intervention at 0.4, [doc 02 section 3](../docs/research/close-area-nav/02-sims-platforms-competitions.md#3-competition-formats-and-lessons)).
      Say it if it happens.

## Script

Pitch time. The demo block is 1:00-2:00; the other rows say what stays on screen while the
narrator talks.

| Time | On screen | Driver does | Narrator says |
|---|---|---|---|
| 0:00 | Title slide: top-down course, A and B | nothing | One-line story or the chosen hook |
| 0:20 | One slide, one hub number with label | nothing | "Past competitions broke on estimation. Reported covariance is overconfident." Number and label from [close-area-story.md section 6](pitch/close-area-story.md#6-numbers-to-fill-and-where-they-come-from), row C1 or C2 |
| 0:40 | Architecture slide: planner => filter => autopilot; nav monitor => margin | nothing | "Real: `<list>`. Stubbed: `<list>`. The planner runs on `<laptop / companion>`." |
| 1:00 | Both panes, drones at A, health ok, same seed number shown | `<demo command> --seed <N>` | "Same layout, same planner, same fault. Left: covariance margin. Right: ours." |
| 1:20 | Fault starts: status strip turns "degraded" on both; right pane margin ring grows, speed cap drops | nothing (fault scripted at sim time `<T>` s) | "VIO jumps `<size>` m now. Left still trusts its covariance. Right widens the margin to `<NUMBER from the run log>` m and slows to `<NUMBER from the run log>` m/s." |
| 1:40 | Left drone crosses the map-only obstacle (red flash); right drone holds hover, then replans | point at both | "Left hit the pole its sensor never saw. Right held, replanned and is flying on to B." |
| 2:00 | Right drone at B; then the failure case (pre-picked seed) for 10 s | press `<key>` for the failure seed | "Here is where ours breaks: `<failure case>`." Then hand over to slides |
| 2:20 | Results table | scroll | "Over `<NUMBER from samples/close-area-safety-filter/README.md>` layouts: breaches `<NUMBER from samples/close-area-safety-filter/README.md>` vs `<NUMBER from samples/close-area-safety-filter/README.md>`, goal reach `<NUMBER from samples/close-area-safety-filter/README.md>`, `[synthetic]`. Not measured: `<item>`." |
| 2:40 | Path-to-product slide | nothing | "Ships as a runtime-assurance monitor next to the stock autopilot. Next: `<three steps>`." |

If the slot gives the demo less than 60 s, keep the 1:20 and 1:40 rows and drop the failure case
to the results slide.

### Variant rows for the alternative hooks

Replace the 1:00-2:00 rows only.

| Hook | 1:00 | 1:20 | 1:40 |
|---|---|---|---|
| H1 relocalization | Seed 1, jump fault, layout 97, three panes: commit-at-once, hover until one wins, ours. Drones flying on VIO, health ok | Sim t 13.0 s: the scan stops fitting the map at the estimate (estimate 0.21 m off). After the 0.2 s settle wait, commit-at-once snaps to a pose 0.63 m wrong. Ours shows 2 live hypotheses and flies one 1 m move | Sim t 14.7 s: ours accepts 1.7 s after the trigger, 0.07 m from truth, and reaches B at 20.3 s. Hover-until-one-wins stays ambiguous and ends stuck. Commit-at-once is corrected at 17.2 s and reaches B at 21.8 s. Full rows and command [below](#h1-relocalization-the-pivot) |
| H2 fiducial goal | Drone flying on VIO towards B | Tag at B detected: goal snaps from estimate to tag pose, offset shown in m | Lands at B; final error `<NUMBER from runs/results.md>` m vs `<NUMBER from runs/results.md>` m without the tag |
| H3 robust baseline | Random layout seed shown | Obstacle moved by the driver (`<key>`), replan visible | Reaches B; completion counter `<NUMBER from runs/results.md>` of `<NUMBER from runs/results.md>` layouts |

### H1 relocalization (the pivot)

The run is a hub run, `[synthetic]` (simulated layout, vehicle, VIO-like estimator and range fan),
held-out seed 1, from [close-area-relocalize](../samples/close-area-relocalize/README.md#held-out-check-seed-1-run-by-the-loop-driver).
Arms: (b) commit-at-once + innovation test, (c) hover until one wins, (f) ours: hover + the
info-gain disambiguating move. Reproduce it (about 65 s wall on 8 workers, Apple M3 Max; writes
into the gitignored `.venv`, so `results/` is untouched):

```sh
cd samples/close-area-relocalize
uv venv .venv && uv pip install --python .venv -r requirements.txt
.venv/bin/python run_disambiguate.py --layouts 100 --seed 1 --arms single,multi,multi_ig --out .venv/demo-out
.venv/bin/python -c "import json; R=json.load(open('.venv/demo-out/disamb_random_1.json'))['results']['jump']; [print(a, R[a]['runs'][97]['outcome'], [(e['t_trigger'], e['recover_s'], e['result'], e['err_m']) for e in R[a]['runs'][97]['events']]) for a in ('single','multi','multi_ig')]"
```

Expected last command output (checked 2026-11-09): `single reached`, with a 0.6281 m commit at
13.0 s; `multi stuck`, event at 13.0 s still `open`; `multi_ig reached`, event at 13.0 s accepted
after 1.7 s at 0.0748 m. The same table as
[disamb_random_1.md](../samples/close-area-relocalize/results/disamb_random_1.md) prints first.

Replace the 1:00-2:20 rows with these. Sim times are from the run's JSON (`events`, `moves`).

| Time | On screen | Driver does | Narrator says |
|---|---|---|---|
| 1:00 | Three panes, seed 1, layout 97, jump fault. Status strip: nav health, hypothesis count, verdict (none / ambiguous / pending / accept) | Start the replay of the three arms (`<replay command>`; the sample has no viewer, see Not verified) | "Same room, same fault, three ways to recover. Left: snap to the best match. Middle: hover until one hypothesis wins. Right: ours." |
| 1:10 | Sim t 2.7 s: 0.5 m VIO jump, `reset_counter` changes. All three recover in 0.2-0.4 s | nothing | "VIO jumped half a metre. The reset is reported, so all three re-match at once. That is the easy case." |
| 1:25 | Sim t 13.0 s: innovation test fires, estimate 0.21 m off. Left snaps to a pose 0.63 m from truth. Middle and right: strip "ambiguous", 2 live hypotheses | point at the left pane | "Now nothing is reported. The scan just stops fitting the map. Left guessed, and guessed 0.63 m wrong. Middle and right cannot tell two places apart, so they hover." |
| 1:40 | Sim t 14.0 s: right drone flies a 1 m move along +y; t 14.7 s: verdict "accept", error 0.07 m. Middle still hovering | point at the right pane | "Ours makes one short move that tells the two places apart. 1.7 s after the trigger it knows where it is, within 7 cm." |
| 1:55 | Right drone at B (sim t 20.3 s). Middle scored stuck. Left corrected at 17.2 s, at B at 21.8 s | nothing | "Left got there too, because a later match fixed it. In a corridor, that guess was wrong in 8 of 20 runs. Ours: 0 wrong commits." |
| 2:20 | Results table | scroll | "Over 100 random layouts per fault: estimator only 64 % / 36 % reached; ours 99-100 %, 0 collisions, 0 wrong commits, on a held-out seed too. Corridor: 80 %. All `[synthetic]`. Not measured: SITL, flight, map errors." Numbers from [close-area-story.md H1](pitch/close-area-story.md#h1-relocalization-after-vio-loss-the-pivot-if-the-kill-test-fails) |

Failure case for 2:00 (10 s): the symmetric corridor. `.venv/bin/python run_disambiguate.py --corridor --runs 20 --arms single,multi,multi_ig --out .venv/demo-out`
(22 s wall for all five arms in the README). Ours reached 80 % there, with recoveries of about 11 s after a move
([disamb_corridor.md](../samples/close-area-relocalize/results/disamb_corridor.md), `[synthetic]`).
Not rerun for this page; pick the run index from the JSON before H+30.

## Numbers on screen and where they come from

Show only these. Each one is in `runs/results.md` with layouts, seeds and the command.

| Number | When on screen | Source | Label |
|---|---|---|---|
| Fault size (jump m or bias m/s) and onset time | 1:20 | Demo config for the chosen seed | as the run |
| Margin m and speed cap m/s, live | 1:20-2:00 | Run log of the demo seed | as the run |
| Breach rate per arm, jump and bias faults | 2:20 | `<NUMBER from samples/close-area-safety-filter/README.md>` | `[synthetic]` |
| Goal reach and stuck count per arm | 2:20 | `<NUMBER from samples/close-area-safety-filter/README.md>` | `[synthetic]` |
| SITL repeat, if done | 2:20 | `<NUMBER from runs/results.md>` | `[SITL]` |
| Loop time p99 on the board | 0:40 or 2:40 | `<NUMBER from runs/results.md>` | measured on `<board>` |
| One hub context number | 0:20 | [close-area-story.md section 6](pitch/close-area-story.md#6-numbers-to-fill-and-where-they-come-from) C1-C3 | as listed there |
| H1: trigger, accept time, error of the demo run (13.0 s, 1.7 s, 0.07 m) | 1:25-1:40 | Seed 1, jump, layout 97, `disamb_random_1.json` | `[synthetic]` |
| H1: reached % and wrong commits per arm | 2:20 | [close-area-story.md section 6](pitch/close-area-story.md#6-numbers-to-fill-and-where-they-come-from) rows R-H1a to R-H1c | `[synthetic]` |

Rules: a live run is one run, an example, not a statistic. Say "this run" on screen and "over N
layouts" on the table. Never put a hub number in the results table.

## Fallback plan

| Failure | Detect | Switch to | Max time lost |
|---|---|---|---|
| Live run errors or hangs | Drones not moving 10 s after start | Backup video from the 1:00 mark, narrator keeps the same script | 10 s |
| Sim shows a different outcome than rehearsed | Left arm does not breach, or right arm breaches | Say "this seed went differently, here is the recorded one", play the video; show the run on the results table honestly | 10 s |
| Real flight aborted by the safety pilot | Pilot takes over | Say "the safety pilot took over, that counts as an intervention", play the video | 15 s |
| Projector or laptop dies | Black screen | Laptop 2, same video | 30 s |
| Judges ask for it live after the video | - | `<demo command> --seed <N>` at the judging table, offer to move an obstacle | - |

Never debug on stage. Say "switching to the recording made at H+30", switch, continue.

## Recording the backup

H+30 to H+36.

- Record the full script once end to end, screen and narration, no cuts. Show the commit hash and
  the seed number on the first frame.
- Second clip: just 1:20-1:40 (fault, breach on the left, hold on the right), 20 s, for the deck.
- Third clip: the failure case, 10 s.
- Copy all to laptop 2 and a USB stick. Check they play offline.
- Stills for the deck: before the fault, the breach moment, right drone at B.

## Not verified

- No row was rehearsed or timed. Times assume the 3-minute skeleton.
- The sim view, status strip and key bindings do not exist yet; they are the team's to build.
- Whether the chosen seed reproduces the same outcome on the demo laptop: check at T-30 min.
- H1: the seed-1 command above was run once on the authoring laptop and gave the stated layout-97
  events. The relocalize sample has no viewer or replay export, so the three panes and the status
  strip are the team's to build (for example from the run's `events` and `moves`). The "estimate
  0.21 m off" is the logged `pre_err_m`, not something the drone knows. The corridor command was
  not rerun here.
