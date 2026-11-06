# [Project name]: one-pager

<!-- Fill every [bracket]. Delete these comments. One printed page. Every number here must also be
in runs/results.md and reproducible with the command in "Reproduce". Hub numbers (from
docs/evidence-matrix.md) go only in "Context", never in "Results". -->

**Team:** [names, roles] - **Brief:** [problem statement, in its own words] - **Repo:** [URL, public / private] - **Commit:** [hash]

## Problem

[Two sentences: who (user, platform), what goes wrong when GNSS is jammed or spoofed, and why
it matters to that user.]

**Context (not our result):** [one hub number with label and source, e.g. from
[story-bank.md](story-bank.md)] - `[label]`, [N runs], [sample link].

## What it does

| Detect | Respond | Recover |
|---|---|---|
| [test(s) and inputs, e.g. velocity consistency vs VO] | [exclusion / source switch / alarm to TAK] | [re-validation rule when GNSS returns] |

**Architecture:** [sources] => [integrity check] => [filter] => [output: `GPS_INPUT` / CoT / NMEA / GCS].
Real: [list]. Stubbed or simulated: [list].

## Results

| Metric | Ours | Baseline | Runs | Input | Ground truth |
|---|---|---|---|---|---|
| [e.g. max cross-track error, m] | [ ] | [ ] | [N flights / seeds] | [real / SITL / synthetic / mixed: name the data] | [source] |
| [time to detect, s] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [false alarms per hour / per flight] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [availability at AL [x] m, %] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [CPU time per update, ms, on hardware X] | [ ] | - | [ ] | [ ] | - |
| Not measured | [power draw, field accuracy, integrity risk below 1e-4, ...] | | | | |

**Thresholds** were set on [data / runs] and tested on [data / runs].
**SITL and synthetic results show the method works under the stated model; they are not field results.**

## Where it breaks

- [Attack or condition not detected, e.g. drag below X m/s]
- [Condition not tested, e.g. night, water, link loss together with GNSS loss]
- [Sim-to-real gap, e.g. simulated VIO near-perfect]

## Deployability

Hardware class: [e.g. companion computer class, receiver class]. Integration: [message / protocol].
Field retuning: [config file, which parameters]. Learned or LLM components: [none / what, with
log, confidence and off switch => fallback].

## Compliance

Defensive PNT only: no targeting, no terminal guidance, no payload logic. Public civil signals
and public data ([licences]). No over-the-air GNSS transmission: spoofing injected [in software /
into files / cabled]. Export-control checklist reviewed:
[docs/export-control-and-ethics.md](../../docs/export-control-and-ethics.md#7-checklist) (not legal advice).

## Reproduce

```sh
[git clone ... && make setup test eval]   # [runtime, machine]
```

## Next three steps

1. [ ]
2. [ ]
3. [ ]
