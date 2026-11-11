# Presenting

Use this when you write what you say, show or hand to reviewers at the end. Close-area A=>B task
(fly from A to B through obstacles): start at [close-area-story.md](close-area-story.md). PNT /
GNSS-resilience brief: start at [story-bank.md](story-bank.md).

Companion to [deck-outline.md](../competition-kit/deck-outline.md) (the 9-slide version mapped to
review criteria), [live-demo-script.md](live-demo-script.md) and
[live-demo-script-close-area.md](live-demo-script-close-area.md) (2-minute live demo of the toolkit: room => Solver => scored flight, H1 appendix for VIO loss). This folder
adds the spoken structure, ready hooks tied to measured numbers, a short deck, reviewer-question
prep and a one-pager. Times below are hours into a 48-hour build; scale them to your schedule.

| Page | Use it when | You get |
|---|---|---|
| [close-area-story.md](close-area-story.md) | Close-area A=>B task. Hour 0 (pick), hour 24 (kill-test gate), hour 36 (rehearse) | One-line story, kill-test gate choosing the story, 3 backup hooks, 3-minute skeleton, 10 reviewer questions with where the answer lives |
| [hard-questions.md](hard-questions.md) | Close-area A=>B task. Hour 36 (rehearse) | Part A: 10 reviewer questions on the measured-toolkit story (the default) plus the one we hope nobody asks. Part B: 15 hard questions on the relocalization story (H1). 20 s answers, each with a number and its input label (or "no number") and a link to the committed file or README section |
| [live-demo-script-close-area.md](live-demo-script-close-area.md) | Close-area A=>B task. Draft at hour 0, record the backup by hour 30 | The 2-minute toolkit demo: setup, script, fallback, H1 appendix |
| [live-demo-script.md](live-demo-script.md) | GNSS / PNT demo. Draft at hour 0 (five lines), full by hour 30, rehearse x3 | Minute-by-minute live demo with fallback recording plan |
| [story-bank.md](story-bank.md) | PNT brief. Hours 0-2 (pick a family), hour 30 (pick 1-2 hooks) | 10 opening hooks per brief family (6 families), each tied to a measured result in the hub, with its input label and the caveat to say aloud |
| [pitch-structure.md](pitch-structure.md) | Any brief. Draft hour 22, final hour 36, rehearse x3 | 3-minute and 5-minute skeletons (problem => why it matters operationally => live demo => honest numbers => what's next), funder vocabulary, 15 hard reviewer questions with answer patterns |
| [slides-outline.md](slides-outline.md) | Hours 30-40 | 6-8 slide deck, one message per slide, which existing figure or screenshot to use, plus the "demo failed live" fallback |
| [one-pager-template.md](one-pager-template.md) | Hour 40, print 5 copies if you can | Fill-in technical one-pager for reviewers (results table with input labels) |

## Order of work

1. **Hour 0, when you get the task statement.** Decode it with
   [problem-statement-decoder.md](../../docs/problem-statement-decoder.md) and pick the matching
   brief family in [story-bank.md](story-bank.md#families). Read that family's 10 hooks. They tell
   you which numbers already exist in the hub and which you will have to measure yourselves.
2. **Hour 2.** Write the five-line pitch (one line per beat of
   [pitch-structure.md](pitch-structure.md#the-five-beats)) on the wall. If you cannot fill the
   "honest numbers" line with something you will measure, change the project, not the pitch.
3. **Hour 22.** Fill the 3-minute skeleton with what actually runs. Score it with
   [self-assessment.md](../competition-kit/self-assessment.md).
4. **Hour 30.** Record the backup video ([live-demo-script.md](live-demo-script.md#recording-the-backup-hours-30-36))
   and pick the slide figures ([slides-outline.md](slides-outline.md)).
5. **Hour 36.** Rehearse the reviewer questions out loud: one person asks, the answerer has 20 s.
6. **Hour 40.** Fill the [one-pager](one-pager-template.md). Every number on it must also be in
   your repo's `runs/results.md`.

## Rules for numbers (non-negotiable)

- **Your own numbers come first.** A hub number is context ("the autopilot alone does X"); your
  measured number is the result. Never present a hub number as your own result.
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
the compliance answer in [pitch-structure.md](pitch-structure.md#reviewer-questions).
