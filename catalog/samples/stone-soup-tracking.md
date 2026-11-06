# Sample: Stone Soup radar tracking of two UAVs with JPDA and OSPA

`sample:stone-soup-tracking` - code and walkthrough in [samples/stone-soup-tracking](../../samples/stone-soup-tracking/)

Simulates two small UAVs observed by a noisy bearing/range radar with clutter and tracks them with Stone Soup's Extended Kalman filter and JPDA data association. Track quality is scored against ground truth with the OSPA metric, the detect-and-track layer of a counter-UAS airspace picture.

**Verification:** unverified sketch: syntax-checked only with python3.14.7 on 2026-11-06; requires stonesoup (numpy, scipy). Class names checked against Stone Soup tutorials 02, 08 and the Metrics example.

**Concepts:** [Tracking and data association](../concepts/target-tracking.md), [Counter-UAS and drone detection](../concepts/counter-uas.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `stone-soup`, `jpda`, `ekf`, `ospa`, `radar`, `c-uas`, `airspace-awareness`

## Related

- uses: [Stone Soup](../repos/dstl__stone-soup.md)

_Indexed by lane(s): samples_
