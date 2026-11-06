# Judging self-assessment

Score yourself at H+22 and H+40. Replace these criteria with the event's published rubric
if there is one; keep the evidence column either way. Criteria derived from
[playbook "What judges reward"](../docs/hackathon-playbook.md#1-what-judges-reward).

Score 0-3: 0 = absent, 1 = claimed only, 2 = shown, 3 = shown and measured with evidence a judge can open.

| # | Criterion | Question a judge will ask | Evidence (file, run, video timestamp) | H+22 | H+40 | Fix before pitch |
|---|---|---|---|---|---|---|
| 1 | Working prototype on a realistic system | Is it running on SITL, recorded data or hardware, or only synthetic? | | | | |
| 2 | Measured result with ground truth | What is the number, against what truth, over how many runs? | `runs/results.md` | | | |
| 3 | Baseline comparison | Better than what? | baseline rows in results | | | |
| 4 | Multi-source design | What happens when one source drops out? | | | | |
| 5 | Integrity before fusion | Do you detect before you fuse? False alarm rate? | | | | |
| 6 | Detect / respond / recover mapping | Which feature does what? | slide 3 | | | |
| 7 | Holdover / degradation story | How long until error exceeds N m without GNSS? | `time_to_exceed_al_s` | | | |
| 8 | Operator workflow | Does it show up where operators already look (TAK, GCS)? Uncertainty shown? | | | | |
| 9 | Deployability | Hardware class, compute, latency, power? | | | | |
| 10 | Field reconfigurability | Can a user retune it without code? | config / CLI flags | | | |
| 11 | Governable AI (if any) | Log, confidence, off switch, safe fallback? | | | | |
| 12 | Sim-to-real honesty | What did you not verify? What breaks it? | README "What we did not verify" | | | |
| 13 | Compliance | Signals, transmission, export, licence, scope? | submission checklist | | | |
| 14 | Dual-use | Who else uses this (aviation, maritime, timing)? | slide 8 | | | |
| 15 | Reproducibility | Can a judge rerun it from README on a clean machine? | `make test eval` | | | |

Total H+22: __ / 45. Total H+40: __ / 45.

## Weakest three (H+22)

1. TODO => action, owner, by H+__
2.
3.

## Claims audit (H+40)

Every claim on a slide or in README:

| Claim | Where | Evidence | Verified by running? (yes / from docs / no) |
|---|---|---|---|
| | | | |

Anything "no" gets reworded or removed.
