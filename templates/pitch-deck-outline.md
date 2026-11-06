# Pitch deck outline

9 slides, 3 minutes plus Q&A. Each slide maps to a row in
[playbook "What judges reward"](../docs/hackathon-playbook.md#1-what-judges-reward). The
common thread there: a working, measured, honest prototype on a realistic scenario beats a
clever slide.

| # | Slide | Content | Judges reward (playbook) | Time |
|---|---|---|---|---|
| 1 | Threat | One sentence, one real public incident source, one map or number with its caveat | Skepticism toward unverified claims | 15 s |
| 2 | User and platform | Who, on what vehicle, under what constraints (SWaP, comms, operator) | Rapid field relevance, frontline users | 15 s |
| 3 | What it does | Features mapped to detect / respond / recover (NISTIR 8323, DHS RPNT framework words) | Detect, respond, recover vocabulary | 20 s |
| 4 | Architecture | One diagram: sources => integrity layer => filter => TAK / GCS. Mark what is real vs stub | Multi-sensor fusion; integrity over raw accuracy | 20 s |
| 5 | Live demo / video | Attack, alarm, continued navigation, failure case | Working prototype on a realistic simulated system | 60 s |
| 6 | The number | Baseline vs ours with ground truth and test conditions: ATE, time to detect, false alarms, holdover minutes to N m | Measured accuracy; holdover as value metric | 20 s |
| 7 | Limits | What is not verified, what breaks it, sim-to-real gap | Sim-to-real honesty | 15 s |
| 8 | Deployability and governance | Hardware class and compute, field retuning via config, AI off switch and fallback, dual-use (civil aviation / shipping / timing) | Deployable dual-use; lightweight onboard; governable AI | 10 s |
| 9 | Compliance and next steps | Civil signals, cabled-only signal generation, no targeting; next 3 steps; team | Compliance awareness | 5 s |

## Slide rules

- One number per slide, with its unit, ground truth and how it was measured.
- Every number on a slide is in `runs/results.md` and reproducible with `make eval`.
- Label synthetic and SITL results as such on the slide itself, not only in the talk.
- Put uncertainty on the map screenshot, not just a dot.
- Cite incident sources from the hub (e.g. [EASA SIB 2022-02](../catalog/resources/easa-sib-2022-02-gnss-outages.md),
  [OPSGROUP 2024](../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md)) with their caveat.

## Backup slides (for Q&A only)

- Threat model table (threats x mitigated / detected / not addressed).
- Threshold choice: false-alarm probability per epoch and per window.
- Per-seed / per-run results.
- Hardware bill of materials (cost class) and power draw, if measured; "not measured" otherwise.

## Judge questions to rehearse (from the playbook)

- How is it tested?
- What happens when your second sensor fails too?
- How does a field user retune it?
- How do you turn the AI part off?
- What is the hardware class and power draw?
- What data did you train or tune on, and does it transfer?
