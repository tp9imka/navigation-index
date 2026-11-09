# Demo script: close-area A to B

Live-demo variant of [demo-script.md](demo-script.md) for the close-area task: fly from A to B
through obstacles, with a VIO fault injected. It fits the 3-minute skeleton in
[pitch/close-area-story.md](pitch/close-area-story.md#4-3-minute-skeleton). One driver, one
narrator. The driver never types free text on stage: every step is a command in shell history
or a key press.

State on 2026-11-09: nothing here has been run. `samples/close-area-safety-filter/` does not exist
in the hub yet. Commands in `<angle brackets>` are the team's own; write them on Day 1.

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
| H1 relocalization | Drone flying on VIO, health ok | Tracking lost: strip "lost", drone hovers, hypothesis count shown | One hypothesis wins after `<NUMBER from runs/results.md>` s; drone continues to B |
| H2 fiducial goal | Drone flying on VIO towards B | Tag at B detected: goal snaps from estimate to tag pose, offset shown in m | Lands at B; final error `<NUMBER from runs/results.md>` m vs `<NUMBER from runs/results.md>` m without the tag |
| H3 robust baseline | Random layout seed shown | Obstacle moved by the driver (`<key>`), replan visible | Reaches B; completion counter `<NUMBER from runs/results.md>` of `<NUMBER from runs/results.md>` layouts |

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
