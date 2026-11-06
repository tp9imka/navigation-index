# Sample: Stone Soup radar tracking of two UAVs with JPDA and OSPA

`sample:stone-soup-tracking` - code and walkthrough in [samples/stone-soup-tracking](../../samples/stone-soup-tracking/)

Simulates two small UAVs observed by a noisy bearing/range radar with clutter and tracks them with Stone Soup's Extended Kalman filter and JPDA data association. Track quality is scored against ground truth with the OSPA metric, the detect-and-track layer of a counter-UAS airspace picture.

**Verification:** ran radar_jpda_ospa.py with stonesoup 1.9.1, numpy 2.5.4, scipy 1.18.1 on Python 3.12.14 on 2026-11-06: 2 tracks held on 2 truths, OSPA mean 17.0 m / max 53.0 m (c=100 m), identical over 3 runs after fixing set-ordering nondeterminism; output in README. Single seed and scenario, no Monte Carlo; initiators/deleters and live radar input not exercised.

**Concepts:** [Tracking and data association](../../catalog/concepts/target-tracking.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `stone-soup`, `jpda`, `ekf`, `ospa`, `radar`, `c-uas`, `airspace-awareness`

## Related

- uses: [Stone Soup](../../catalog/repos/dstl__stone-soup.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
