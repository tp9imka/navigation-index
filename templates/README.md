# Hackathon kit templates

Use this when you need a file to copy for the hackathon itself: a repo skeleton, a platform
driver, a demo script, a pitch, a plan or a checklist. For what to build on, read
[competition-playbook.md](../docs/competition-playbook.md) and
[reference-stacks.md](../docs/reference-stacks.md) instead.

## Close-area A=>B (likely Day-1 task)

For "fly a drone from A to B in a close area, maybe with obstacles", open these in order:

1. [flight-repo/](flight-repo/README.md): clone as the team repo. `make test && make sim` runs on a mock.
2. [drone-adapter/drivers/](drone-adapter/drivers/README.md): the driver for PX4, ArduPilot,
   Crazyflie or Tello (velocity setpoints, pose, ranges). Unrun, written from docs.
3. [drone-adapter/frames.md](drone-adapter/frames.md): ENU / NED, FLU / FRD and yaw sign per platform.
4. [demo-script-close-area.md](demo-script-close-area.md): the live demo, two arms side by side.
5. [pitch/close-area-story.md](pitch/close-area-story.md): the pitch, with a kill-test gate at H+24.

Planners and measured baselines to start from (synthetic): [close-area-arena](../samples/close-area-arena/README.md).
Research and the recommended direction: [close-area-nav](../docs/research/close-area-nav/README.md).

For a GNSS / PNT-integrity brief instead:
`cp -r templates/project-repo ~/our-project && cd ~/our-project && make test eval`.

## All templates

| Page | Use it when | You get |
|---|---|---|
| [flight-repo/](flight-repo/README.md) | H+0 of a close-area flight task: clone as the new repo's core, then `make test`, `make sim` | Adapter => NavHealth => Planner => SafetyFilter => send at 20 Hz with keep-alive, degraded speed cap, lost => hover, JSONL log per tick; stdlib, runs on a mock; arena planners plug in unchanged |
| [project-repo/](project-repo/README.md) | A GNSS / PNT-integrity brief. Before the event: fork and run once. H+0: rename, delete what you will not use | Skeleton repo: README with honest results table, AGENTS.md/CLAUDE.md wired to this hub, Makefile (`setup test sim demo eval`), docker-compose skeleton, typed interfaces (PoseSource, NavFilter, IntegrityMonitor, Publisher) with a working stdlib pipeline, metrics script |
| [drone-adapter/](drone-adapter/README.md) | H+0: write the planner before the drone is known; copy into the project repo | `pose()/ranges()/send_setpoint()` dataclasses and Protocol, ENU/NED and FLU/FRD helpers, a stdlib mock vehicle, a 20 Hz example loop |
| [drone-adapter/drivers/](drone-adapter/drivers/README.md) | Day 1, once the platform is known: send velocity setpoints and read pose and ranges on PX4, ArduPilot, Crazyflie or Tello | One `Adapter` class per platform with keep-alive, origin at A and frame conversion; platform table with setpoint path and known traps. Unrun, written from docs |
| [drone-adapter/frames.md](drone-adapter/frames.md) | A setpoint goes the wrong way, or before the first bench test | Frame, unit and yaw conventions per platform, with sources and what is not confirmed |
| [demo-dashboard/](demo-dashboard/README.md) | A GNSS / PNT run needs a judge-facing map replay (lat / lon tracks, PL vs AL, alarms) | Static page, no build step, JSONL schema `navdash/1`, converter from project-repo runs |
| [offline-kit/](offline-kit/README.md) | The week before: venue Wi-Fi will not carry datasets, wheels or Docker images | One cache directory with datasets, pip wheels, Docker tarballs, git bundles and basemap; three rehearsable starter bundles |
| [team-roles-and-48h-plan.md](team-roles-and-48h-plan.md) | Before the event; pinned on the wall at H+0 | Who owns what, time boxes, exit criteria, sleep shifts |
| [threat-model.md](threat-model.md) | H+0 to H+2; frozen by H+14 | Threats, assumptions, what you mitigate and what you do not; source of the "limits" slide |
| [adr.md](adr.md) | Any time a choice costs more than an hour to undo | One architecture decision per file |
| [risk-register.md](risk-register.md) | H+0, re-read at the H+12 go/switch checkpoint | Project risks with trigger and fallback |
| [demo-script.md](demo-script.md) | GNSS / PNT demo. Draft at H+0 (five lines), full by H+30, rehearse x3 | Minute-by-minute live demo with fallback recording plan |
| [demo-script-close-area.md](demo-script-close-area.md) | Close-area demo. Draft at H+0, record the backup by H+30 | Two arms, same seed, same injected VIO fault, side by side; setup, script and fallback |
| [pitch-deck-outline.md](pitch-deck-outline.md) | H+30 to H+40 | 9 slides mapped to what defense judges reward |
| [pitch/](pitch/README.md) | H+22 draft, H+30 to H+40 final, rehearse x3 | 3- and 5-minute skeletons, 15 judge questions with evidence, story bank (10 hooks per brief family tied to measured results), 6-8 slide outline, judges' one-pager |
| [pitch/close-area-story.md](pitch/close-area-story.md) | Close-area pitch. H+0 pick, H+24 kill-test gate, H+36 rehearse | One-line story, 3 backup hooks, 3-minute skeleton, 10 judge questions with where the answer lives |
| [judging-self-assessment.md](judging-self-assessment.md) | H+22 and again at H+40 | Score yourself against the judging criteria before judges do |
| [submission-checklist.md](submission-checklist.md) | H+42 to H+48, before the final push | Licence, export-control check, secrets scan, reproducibility |
| [post-hackathon-retro.md](post-hackathon-retro.md) | Within a week after | What worked, what to keep in the kit |

## The project-repo skeleton

```
src/navapp/interfaces.py   PoseSource => NavFilter => IntegrityMonitor => Publisher (typing.Protocol)
src/navapp/sim.py          synthetic clean / jam / spoof (slow drag-off) scenarios
src/navapp/filter.py       dead reckoning + absolute-fix filter (stand-in for an EKF)
src/navapp/integrity.py    chi-square innovation gate + windowed test, NullMonitor baseline
src/navapp/publishers.py   CoT XML for TAK, MAVLink v1 STATUSTEXT for a GCS, JSONL log, UDP sink
eval/metrics.py            ATE, RPE, time to detect, false alarms, availability, misleading %
```

Swap one stage at a time: recorded log or SITL => new PoseSource; EKF / factor graph => new
NavFilter; RAIM or multi-receiver check => new IntegrityMonitor. The tests check every
implementation against its Protocol.

Synthetic results from `make eval` on the shipped code (seed 7, alert limit 10 m). They show the
pipeline and the metrics work; they say nothing about any real receiver or vehicle:

| Run | ATE RMSE m | ATE max m | Time to detect s | Availability % | Misleading % |
|---|---|---|---|---|---|
| spoof, NullMonitor (fuse everything) | 81.61 | 175.51 | missed | 100.00 | 61.33 |
| spoof, ChiSquareMonitor | 10.25 | 17.17 | 9.00 | 71.27 | 0.00 |
| jam, ChiSquareMonitor | 1.61 | 4.44 | 2.00 | 100.00 | 0.00 |
| clean, ChiSquareMonitor | 1.05 | 2.47 | n/a | 100.00 | 0.00 |

Read the spoof row honestly: the filter absorbs about 7 m of drag-off before the windowed
test fires at 9 s, then dead reckoning on biased odometry drifts past the 10 m alert limit 48 s
after onset (`time_to_exceed_al_s`). Around that point the filter's own 95% radius (8.2 m) is
smaller than the true error (10.1 m): the uncertainty model is optimistic. Misleading % stays 0
only because the alarm is latched. That is the "hybrid-solution corruption" case from the
playbook threat table, and the gap a real project closes with a better velocity source, a
second receiver, or a bias state in the filter.
