# Pitch kit

Everything you say, show or hand to judges at the end of a PNT-resilience hackathon. Companion
to [pitch-deck-outline.md](../pitch-deck-outline.md) (the 9-slide version mapped to judging
criteria) and [demo-script.md](../demo-script.md) (minute-by-minute live demo). This kit adds
the spoken structure, ready hooks tied to measured numbers, a short deck, judge-question prep
and a one-pager.

| File | What it is for | When |
|---|---|---|
| [pitch-structure.md](pitch-structure.md) | 3-minute and 5-minute skeletons (problem => why it matters operationally => live demo => honest numbers => what's next), funder vocabulary, 15 hard judge questions with answer patterns | Draft H+22, final H+36, rehearse x3 |
| [story-bank.md](story-bank.md) | 10 opening hooks per brief family (6 families), each tied to a measured result in the hub, with its input label and the caveat to say aloud | H+0 to H+2 (pick a family), H+30 (pick 1-2 hooks) |
| [slides-outline.md](slides-outline.md) | 6-8 slide deck, one message per slide, which existing figure or screenshot to use, plus the "demo failed live" fallback | H+30 to H+40 |
| [one-pager-template.md](one-pager-template.md) | Fill-in technical one-pager for judges (results table with input labels) | H+40, print 5 copies if the venue allows |

## On the day

1. **H+0, when the statement drops.** Decode it with
   [problem-statement-decoder.md](../../docs/problem-statement-decoder.md) and pick the matching
   brief family in [story-bank.md](story-bank.md#families). Read that family's 10 hooks. They tell
   you which numbers already exist in the hub and which you will have to measure yourselves.
2. **H+2.** Write the five-line pitch (one line per beat of
   [pitch-structure.md](pitch-structure.md#the-five-beats)) on the wall. If you cannot fill the
   "honest numbers" line with something you will measure, change the project, not the pitch.
3. **H+22.** Fill the 3-minute skeleton with what actually runs. Score it with
   [judging-self-assessment.md](../judging-self-assessment.md).
4. **H+30.** Record the backup video ([demo-script.md](../demo-script.md#recording-the-backup-h30-to-h36))
   and pick the slide figures ([slides-outline.md](slides-outline.md)).
5. **H+36.** Rehearse the judge questions out loud: one person asks, the answerer has 20 s.
6. **H+40.** Fill the [one-pager](one-pager-template.md). Every number on it must also be in
   your repo's `runs/results.md`.

## Rules for numbers (non-negotiable)

- **Your own numbers come first.** A hub number is context ("the autopilot alone does X"); your
  measured number is the result. Never present a hub number as your team's result.
- **Every hub number comes from [evidence-matrix.md](../../docs/evidence-matrix.md)**, quoted
  with its input label and run count, and the sample README linked. The story bank already
  carries both.
- **Input labels**, on the slide itself, not only in the talk:
  - `[real]` = recorded public data (name it: VPAIR, Jammertest, Zenodo 14230741, ...);
  - `[SITL]` = real autopilot firmware, simulated sensors;
  - `[synthetic]` = simulated vehicle and sensors, sometimes over real terrain, maps or traffic;
  - `[mixed]` = some parts real, some simulated (say which: "real flight, simulated TRN sensor").
- **SITL and synthetic are never field results.** Say "in SITL" or "in simulation" in the same
  sentence as the number. The matrix wording: it "shows that a method works under the stated
  model; it is not a field result".
- **One run is an example, not a statistic.** Say "one flight" or "four seeds".
- **Superseded numbers stay out.** altpnt-integrity v1's 41.7 % availability / 0 MI is withdrawn
  by its v2 ([matrix section 3](../../docs/evidence-matrix.md#3-integrity-metrics-protection-level-misleading-information));
  use it only as the "before" of a calibration story (story bank C8).
- **Not measured reads "not measured".** Power draw, unit cost, field accuracy, integrity risk
  below 1e-4: if you did not measure it, the slide says so.

## Scope line for every pitch

Defensive PNT only: keeping position, navigation and timing trustworthy, detecting
interference, giving operators an honest picture. No targeting, no terminal guidance, no
offensive payloads, no over-the-air GNSS transmission (file-based or cabled only). See
[export-control-and-ethics.md](../../docs/export-control-and-ethics.md) (not legal advice) and
the compliance answer in [pitch-structure.md](pitch-structure.md#judge-questions).
