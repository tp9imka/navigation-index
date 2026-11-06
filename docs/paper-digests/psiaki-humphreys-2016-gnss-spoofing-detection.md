# GNSS Spoofing and Detection - paper digest
<!-- about: res:psiaki-humphreys-2016-gnss-spoofing-detection -->
**GNSS Spoofing and Detection** - Psiaki (Cornell), Humphreys (UT Austin), Proceedings of the IEEE vol. 104 no. 6, pp. 1258-1270, 2016. [paper](https://doi.org/10.1109/JPROC.2016.2526658) | [author preprint](https://radionavlab.ae.utexas.edu/images/stories/files/papers/gnss_spoofing_detection.pdf) | code: none | Read: full text of the author-hosted preprint (11 pages). The IEEE version is paywalled and was not compared, so wording or page layout may differ.

## Problem
In 2016 COTS civil receivers had no spoofing defenses, even though receiver-spoofers and cheap programmable simulators existed. This survey lays out the attack modes and the detection techniques, then builds a cost-ranked attack/defense matrix. The goal is to tell receiver makers which defenses buy the most security per dollar.

## Method
- Common signal model for authentic and spoofed signals (Eqs. 1-3). Each attack is described by how its amplitude, code phase and carrier phase differ from the authentic signal.
- Attack taxonomy (Sec. II):
  - self-consistent spoofers (simulator, receiver-spoofer);
  - meaconing (record and replay);
  - security code estimation and replay (SCER);
  - nulling of the true signal;
  - multi-antenna and motion-matched spoofers;
  - cooperative victims, e.g. a fisherman defeating his own tracker.
- Defense taxonomy (Sec. III):
  - single-antenna signal processing: observable jumps, received power monitoring (RPM) with AGC, correlation-function distortion, continuous re-acquisition search for duplicate signals;
  - encryption: NMA, delayed-key spread-spectrum security codes (SSSC), dual-receiver correlation of the encrypted military code;
  - drift monitoring: clock offset and IMU/position;
  - signal geometry: multi-antenna or moving-antenna direction of arrival (DoA) from carrier phase;
  - multi-pronged combinations.
- Table I is a 13 x 13 matrix. Defenses D1-D13 and attacks A1-A13 are ordered by subjective cost (hardware, expertise, operating complexity). Each cell is a high, intermediate/case-dependent or low detection probability.
- The output is not an experiment. It is engineering judgment from the authors' red-team/blue-team work since 2008.

## Data and sensors
- No new dataset. Figure 2 shows correlation functions from a live-signal yacht spoofing test (their ref [3]).
- Defenses assume combinations of a single antenna with extra correlators, an IMU, an oscillator model, 2+ antennas or a moving antenna, and a network of secure receivers (for the encrypted-code correlation).
- For a signal-level benchmark of the receiver-spoofer attacks discussed here, see [TEXBAT](../dataset-cards/texbat.md). Its ds7/ds8 add carrier-phase alignment and SCER-like replay.

## Headline results (as reported)
- Table I, row D1 (pseudorange RAIM): low detection probability against all 13 attacks. The authors leave it out of the survey as "too weak against modern spoofers" (Sec. III).
- Table I, row D3 (correlation function distortion monitoring): intermediate against A1-A5. The text recommends it as the best single firmware-level choice for low-cost receivers, combined with D7 (NMA + SCER detection) if affordable (Sec. IV).
- Table I, rows D9 (NMA + SCER detection + RPM + drift monitoring) and D10 (multiple receive antennas): together they give high detection probability against all attacks except A11 (meaconing with multiple RX and TX antennas), which is intermediate (Sec. IV text).
- Sec. III-A: under RPM, a sudden total-power jump "especially if the increase were more than 1 or 2 dB" may indicate an attack.
- Sec. III-D: carrier phase measured to about 1/40 cycle gives a direction-of-arrival accuracy of about 3 deg on a 0.1 m baseline.
- Sec. III-A: correlation-distortion and observable-glitch detectors only work during the initial drag-off. Continuous re-acquisition is the single-antenna method that "can work long after drag-off".
- Sec. III: navigation cannot be recovered under nulling, or under an overpowered attack that saturates the front end.
- Sec. I: COTS simulator and record-and-replay platforms put a spoofing capability "under $5k".

## Limitations
- Stated by authors:
  - The cost ranking and the matrix entries are subjective.
  - Post-detection recovery of navigation is largely unsolved and left to future work.
  - D6-D9 and D13 require changes to the signal in space (marked * in Table I).
  - A high-budget attacker (receiver-spoofer with nulling, SCER and multiple platforms) defeats most defenses (Sec. V).
- Our read:
  - Table I gives qualitative grades, not measured Pd/Pfa. Use it to pick candidate detectors, not to quote performance.
  - The paper predates operational Galileo OSNMA. The NMA rows assumed "unpredictable bits" that Galileo now provides, so see [OSNMA](galileo-osnma.md) for real parameters.
  - Preprint text read only; table layout reconstructed from the PDF text layer and checked against the Sec. IV narrative.

## Code, weights, license
No code, data or weights. The preprint is hosted on the UT Radionavigation Lab site, and the published version is IEEE copyright. Prior author papers (two-antenna differential carrier phase, encrypted-signal correlation) are also on radionavlab.ae.utexas.edu.

## Reproduction effort (estimate)
Estimate: as a survey there is nothing to reproduce. Implementing individual defenses from it:
- RPM plus clock-drift monitor on u-blox telemetry (AGC, C/N0, clock bias/drift): hours, using [pyubx2](../integration-cards/semuconsulting__pyubx2.md) logs or the hub's `samples/gnss-interference-monitor`.
- Correlation distortion or duplicate-peak search: needs raw IQ plus a software receiver ([GNSS-SDR](../integration-cards/gnss-sdr__gnss-sdr.md)) and [TEXBAT](../dataset-cards/texbat.md). Allow 2-4 days to a first plot.
- Multi-antenna DoA: needs hardware (2+ phase-coherent receivers). Not realistic in 48 h unless the kit is provided.

## What a hackathon team can take from it
- **Use Table I as a design checklist.** State which attack columns (A1-A13) your detector targets and grade it honestly. Judges familiar with the field will recognise the framework.
- **Make the detector multi-pronged.** The paper's argument (Sec. III-E) is that RPM covers the overpowered case where correlation distortion fails, and drift monitoring forces a slow drag-off so the other detectors get more time.
- **Drift monitoring fits a GNSS-denied nav stack directly.** Gate GNSS updates in your EKF by checking clock-drift rate against oscillator class and position-drift rate against IMU propagation. These are the D4 checks, and they are cheap.
- **Recovery is the open problem.** A team that shows detection followed by a clean switch to INS/VIO has gone beyond what this survey reports as solved. Compare [Humphreys 2008](humphreys-2008-assessing-spoofing-threat.md) for the original threat tiers.
