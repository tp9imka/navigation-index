# Risk register

Open at H+0. Re-read at the H+12 go/switch checkpoint and before feature freeze (H+30).
Likelihood and impact: L / M / H. Owner is one name, not "team".

| # | Risk | L | I | Trigger (how we notice) | Mitigation now | Fallback if triggered | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| R1 | Core algorithm does not work on real data | M | H | No honest number by H+12 | Walking skeleton first; synthetic + one recorded dataset | Switch to fallback idea at H+14 | Nav | open |
| R2 | SITL / simulator setup eats the first day | H | H | Not flying in SITL by H+6 | Images built and tested before the event | Replay a recorded log as PoseSource | Platform | open |
| R3 | Venue network too slow for datasets / images | H | M | Download ETA > 30 min | Pre-download; images pinned locally | Synthetic scenarios in the skeleton | Lead | open |
| R4 | Live demo fails on stage | M | H | Any step needs a manual fix in rehearsal | Rehearse x3; scripted `make demo` | Recorded video on two machines | Pitch | open |
| R5 | TAK / GCS integration breaks late | M | M | No CoT on the map by H+6 | Skeleton publishes CoT from H+2 | Show the web map or the JSONL plot | Viz | open |
| R6 | Metric is wrong or overclaimed | M | H | Number changes between runs, no ground truth | Metrics only from `eval/metrics.py`; seeds fixed | Report "not measured" | Pitch | open |
| R7 | Compliance problem (radiating, export, licence) | L | H | Any plan to transmit or private international sharing | [Export control and ethics](../docs/export-control-and-ethics.md); cabled-only | Drop the feature | Lead | open |
| R8 | Key person sick / asleep at the wrong time | M | M | Missed handover | Sleep shifts; README run steps | Second owner per component | Lead | open |
| R9 | Hardware failure (SD card, cable, SDR) | M | M | Device not enumerating | Spares listed in playbook 6.4 | Recorded data path | Platform | open |
| R10 | TODO | | | | | | | |

Closed risks stay in the table with status "closed: reason".
