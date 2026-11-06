# Hackathon kit templates

Ready-to-copy files for a 24-48h navigation / PNT / defensive-EW hackathon. Companion to
[hackathon-playbook.md](../docs/hackathon-playbook.md) (ideas, architectures, 48h plan) and
[reference-stacks.md](../docs/reference-stacks.md) (what to build on).

Start: `cp -r templates/project-repo ~/our-project && cd ~/our-project && make test eval`.

| Template | What it is for | When in the 48h |
|---|---|---|
| [project-repo/](project-repo/) | Skeleton repo: README with honest results table, AGENTS.md/CLAUDE.md wired to this hub, Makefile (`setup test sim demo eval`), docker-compose skeleton, typed interfaces (PoseSource, NavFilter, IntegrityMonitor, Publisher) with a working stdlib pipeline, metrics script | Before the event: fork and run once. H+0: rename, delete what you will not use |
| [team-roles-and-48h-plan.md](team-roles-and-48h-plan.md) | Who owns what, time boxes, exit criteria, sleep shifts | Before the event; pinned on the wall at H+0 |
| [threat-model.md](threat-model.md) | Threats, assumptions, what you mitigate and what you do not | H+0 to H+2; frozen by H+14; source of the "limits" slide |
| [adr.md](adr.md) | One architecture decision per file | Any time a choice costs more than an hour to undo |
| [risk-register.md](risk-register.md) | Project risks with trigger and fallback | H+0, re-read at the H+12 go/switch checkpoint |
| [demo-script.md](demo-script.md) | Minute-by-minute live demo with fallback recording plan | Draft at H+0 (five lines), full by H+30, rehearse x3 |
| [pitch-deck-outline.md](pitch-deck-outline.md) | 9 slides mapped to what defense judges reward | H+30 to H+40 |
| [judging-self-assessment.md](judging-self-assessment.md) | Score yourself against the judging criteria before judges do | H+22 and again at H+40 |
| [submission-checklist.md](submission-checklist.md) | Licence, export-control check, secrets scan, reproducibility | H+42 to H+48, before the final push |
| [post-hackathon-retro.md](post-hackathon-retro.md) | What worked, what to keep in the kit | Within a week after |

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
