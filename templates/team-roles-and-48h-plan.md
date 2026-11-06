# Team roles and 48h plan

Derived from [playbook section 5](../docs/hackathon-playbook.md#5-48h-execution-plan-template).
4-5 people. For 24h, halve each block and cut the stretch goal at H+0.

## Roles

| Role | Owns | Hands off | Name | Backup |
|---|---|---|---|---|
| Lead / integrator | Demo path, repo, `main` stays green, go/switch call | Merge order, final README | | |
| Nav / estimation | NavFilter, IntegrityMonitor, metrics | `runs/*.jsonl`, results table | | |
| Platform | PoseSource adapters, SITL, hardware, docker | `make sim` / `make demo` on the demo laptop | | |
| Viz / C2 | Publishers, TAK / web map, operator view | Screen the judges see | | |
| Pitch / evidence | Slides, plots, judge Q&A, tests, submission checklist | Deck, video, self-assessment | | |

Rule: each `src/navapp` stage has one owner. Interface changes need an ADR and the Lead's ok.

## Plan

| Window | Goal | Exit criterion | Done |
|---|---|---|---|
| Pre-event | Fork `templates/project-repo`, `make test eval` green on every laptop; images and datasets local | Each person ran `make demo` once | [ ] |
| H+0 to H+2 | Lock problem against challenge text. One idea, one fallback. Five-line demo script. Threat model draft. Risk register. | Metric named (ATE / time to detect / holdover min / false alarms) | [ ] |
| H+2 to H+6 | Walking skeleton: real input => dumb algorithm => map | Raw position or fake alarm visible in TAK / web map | [ ] |
| H+6 to H+12 | Real core algorithm on real or recorded data; metric automatic | First honest number committed with the script that made it | [ ] |
| H+12 to H+14 | Checkpoint | Go / switch written in an ADR | [ ] |
| H+14 to H+22 | Sleep in shifts. Integrate with SITL or hardware. Find and record a failure case | Full demo runs once without manual fixes | [ ] |
| H+22 to H+30 | Improve metric; integrity/alarm layer; "not verified" list; self-assessment pass 1 | Before/after comparison (baseline vs ours) | [ ] |
| H+30 to H+36 | Feature freeze. Record backup video. Rehearse live run x3 | Video on two machines | [ ] |
| H+36 to H+42 | Pitch built and timed | 3-minute pitch within time | [ ] |
| H+42 to H+48 | Buffer, Q&A prep, submission checklist, clean README | README reproduces the demo on a clean machine | [ ] |

## Sleep shifts (example)

| Window | Awake | Asleep |
|---|---|---|
| H+14 to H+18 | Lead, Nav, Viz | Platform, Pitch |
| H+18 to H+22 | Platform, Pitch, Nav | Lead, Viz |
| H+22 to H+26 | Lead, Viz, Pitch | Nav, Platform |

Nobody sleeps through a checkpoint they own.

## Standups

Every 4h, 5 minutes, standing: done since last, blocked on, next exit criterion. Lead updates the
Done column and the risk register.
